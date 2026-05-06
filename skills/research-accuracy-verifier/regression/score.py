#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.0"]
# ///
"""
Regression scorer for the research-accuracy-verifier fork pilot.

Reads:
  manifest.json                       — list of regression documents
  ground_truth/<doc_id>.json          — seeded errors and expected verdicts
  runs/{baseline,post_fork}/<doc_id>/run{1..3}/audit_report.json
  runs/{baseline,post_fork}/<doc_id>/run{1..3}/return.json     (post_fork only; the fork's compact JSON return)
  runs/{baseline,post_fork}/<doc_id>/run{1..3}/tokens.json     (optional: {"main_context_tokens": N})

Writes:
  runs/score.json                     — full numeric report
  Prints a human-readable summary to stdout.

Sprint 1 pass thresholds (from regression/README.md):
  main_context_tokens.post.median        ≤ 4000
  main_context_tokens.reduction          ≥ 0.85
  verdict_consistency_rate.post          ≥ 0.92
  ground_truth_recall.post               ≥ baseline (non-decreasing)
  schema_validation_pass.post            ≥ 0.98
  predicate_audit.post.fail_rate         ≤ baseline (non-decreasing)
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

REGRESSION_ROOT = Path(__file__).parent
MANIFEST = REGRESSION_ROOT / "manifest.json"
GROUND_TRUTH_DIR = REGRESSION_ROOT / "ground_truth"
RUNS_DIR = REGRESSION_ROOT / "runs"
OUT = RUNS_DIR / "score.json"

ARMS = ("baseline", "post_fork")
RUNS_PER_DOC = 3


@dataclass
class DocScore:
    doc_id: str
    arm: str
    main_context_tokens: list[int] = field(default_factory=list)
    verdict_tuples_per_run: list[set[tuple[str, str]]] = field(default_factory=list)
    ground_truth_hits: list[int] = field(default_factory=list)
    ground_truth_total: int = 0
    schema_passes: list[bool] = field(default_factory=list)
    predicate_audit_fails: list[bool] = field(default_factory=list)


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"WARN: malformed JSON at {path}: {exc}", file=sys.stderr)
        return None


def _matches_severity(actual: str, expected: str | None) -> bool:
    """Severity match: exact, or any if expected is None."""
    return expected is None or actual == expected


def _finding_matches_expectation(
    expectation: dict, findings: list, style_findings: list
) -> bool:
    """One expectation alternative — match against either main or style findings."""
    expected_severity = expectation.get("severity")
    if "verdict" in expectation:
        verdict = expectation["verdict"]
        return any(
            f.get("verdict") == verdict
            and _matches_severity(f.get("severity", ""), expected_severity)
            for f in findings
        )
    if "style_verdict" in expectation:
        style_verdict = expectation["style_verdict"]
        rule_id = expectation.get("rule_id")
        return any(
            f.get("verdict") == style_verdict
            and (rule_id is None or f.get("rule_id") == rule_id)
            and _matches_severity(f.get("severity", ""), expected_severity)
            for f in style_findings
        )
    return False


def seeded_error_satisfied(err: dict, findings: list, style_findings: list) -> bool:
    """A seeded error counts as caught if any acceptable expectation matches."""
    alternatives = err.get("expected_findings_any_of")
    if alternatives:
        return any(
            _finding_matches_expectation(alt, findings, style_findings)
            for alt in alternatives
        )
    # legacy / simple shape
    expected = err.get("expected_verdict")
    expected_severity = err.get("expected_severity")
    if expected is None:
        return False
    return _finding_matches_expectation(
        {"verdict": expected, "severity": expected_severity}, findings, style_findings
    ) or _finding_matches_expectation(
        {"style_verdict": expected, "severity": expected_severity}, findings, style_findings
    )


def collect_run(doc_id: str, arm: str, run_idx: int, gt: dict, score: DocScore) -> None:
    run_dir = RUNS_DIR / arm / doc_id / f"run{run_idx}"
    if not run_dir.exists():
        return  # missing runs accounted for downstream

    # main-context tokens
    tokens = load_json(run_dir / "tokens.json")
    if isinstance(tokens, dict) and "main_context_tokens" in tokens:
        score.main_context_tokens.append(int(tokens["main_context_tokens"]))

    # fallback: only approximate from return.json when tokens.json wasn't supplied for this run
    return_payload = load_json(run_dir / "return.json")
    if return_payload is not None and not score.main_context_tokens:
        # rough char→token estimate at 4 chars/token
        approx = len(json.dumps(return_payload)) // 4
        score.main_context_tokens.append(approx)

    audit = load_json(run_dir / "audit_report.json")
    if audit is None:
        return

    findings = audit.get("findings", []) if isinstance(audit, dict) else []
    style_findings = audit.get("style_findings", []) if isinstance(audit, dict) else []

    # verdict tuples for cross-run consistency — combine main + style findings
    tuples = {(f.get("claim_id", f.get("id", "")), f.get("verdict", "")) for f in findings}
    tuples |= {(f.get("id", ""), f.get("verdict", "")) for f in style_findings}
    score.verdict_tuples_per_run.append(tuples)

    # ground-truth recall — supports two ground-truth shapes:
    # 1. simple: {"expected_verdict": "X", "expected_severity": "Y"}
    # 2. rich:   {"expected_findings_any_of": [{"verdict": "X", "severity": "Y"}, {"style_verdict": "S", "severity": "Y"}]}
    seeded = gt.get("seeded_errors", [])
    score.ground_truth_total = len(seeded)
    hits = 0
    for err in seeded:
        if seeded_error_satisfied(err, findings, style_findings):
            hits += 1
    score.ground_truth_hits.append(hits)

    # schema + predicate audit signals — only recorded when the audit_report actually surfaces them.
    # Missing fields are treated as "no signal" (excluded from rate calculation), NOT silent passes,
    # so a regression in audit_meta emission shows up as a smaller N rather than a fake-positive pass.
    audit_meta = audit.get("audit_meta", {}) if isinstance(audit, dict) else {}
    schema_field = audit_meta.get("schema_validation_pass")
    if schema_field is not None:
        score.schema_passes.append(bool(schema_field))
    predicate_results = audit_meta.get("predicate_audit")
    if isinstance(predicate_results, dict) and predicate_results:
        score.predicate_audit_fails.append(any(v != "pass" for v in predicate_results.values()))


def consistency_rate(per_run_tuples: list[set[tuple[str, str]]]) -> float:
    """Fraction of (claim_id, verdict) tuples that appear in ALL runs.

    Returns 1.0 vacuously for a single run (consistency undefined at N=1) and
    0.0 when no runs were collected. The combination of consistency_rate and
    ground_truth_recall protects against the degenerate "0 findings, single
    run" case: consistency would show 1.0 but recall would be 0.
    """
    if len(per_run_tuples) < 2:
        return 1.0 if per_run_tuples else 0.0
    universe = set().union(*per_run_tuples)
    if not universe:
        return 1.0
    intersection = set.intersection(*per_run_tuples)
    return len(intersection) / len(universe)


def aggregate(scores: list[DocScore]) -> dict:
    if not scores:
        return {"empty": True}

    tokens = [t for s in scores for t in s.main_context_tokens]
    consistencies = [consistency_rate(s.verdict_tuples_per_run) for s in scores]
    recalls = []
    for s in scores:
        if s.ground_truth_total > 0 and s.ground_truth_hits:
            recalls.append(statistics.mean(s.ground_truth_hits) / s.ground_truth_total)
    schema_signals = [p for s in scores for p in s.schema_passes]
    predicate_fails = [f for s in scores for f in s.predicate_audit_fails]

    return {
        "doc_count": len(scores),
        "run_count": sum(len(s.verdict_tuples_per_run) for s in scores),
        "main_context_tokens": {
            "median": statistics.median(tokens) if tokens else None,
            "max": max(tokens) if tokens else None,
            "n": len(tokens),
        },
        "verdict_consistency_rate": (
            statistics.mean(consistencies) if consistencies else None
        ),
        "ground_truth_recall": statistics.mean(recalls) if recalls else None,
        "schema_validation_pass_rate": (
            sum(schema_signals) / len(schema_signals) if schema_signals else None
        ),
        "predicate_audit_fail_rate": (
            sum(predicate_fails) / len(predicate_fails) if predicate_fails else None
        ),
    }


def evaluate_thresholds(report: dict) -> tuple[bool, list[str]]:
    failures: list[str] = []
    post = report.get("post_fork", {})
    base = report.get("baseline", {})

    median = post.get("main_context_tokens", {}).get("median")
    if median is None or median > 4000:
        failures.append(f"main_context_tokens.post.median = {median} (target ≤ 4000)")

    base_median = base.get("main_context_tokens", {}).get("median")
    if base_median and median is not None:
        reduction = (base_median - median) / base_median
        if reduction < 0.85:
            failures.append(
                f"main_context_tokens.reduction = {reduction:.2%} (target ≥ 85%)"
            )

    consistency = post.get("verdict_consistency_rate")
    if consistency is None or consistency < 0.92:
        failures.append(
            f"verdict_consistency_rate.post = {consistency} (target ≥ 0.92)"
        )

    base_recall = base.get("ground_truth_recall")
    post_recall = post.get("ground_truth_recall")
    if base_recall is not None and post_recall is not None and post_recall < base_recall:
        failures.append(
            f"ground_truth_recall regressed: baseline={base_recall:.2f} → post={post_recall:.2f}"
        )

    schema_pass = post.get("schema_validation_pass_rate")
    if schema_pass is None or schema_pass < 0.98:
        failures.append(
            f"schema_validation_pass_rate.post = {schema_pass} (target ≥ 0.98)"
        )

    base_fail = base.get("predicate_audit_fail_rate")
    post_fail = post.get("predicate_audit_fail_rate")
    if base_fail is not None and post_fail is not None and post_fail > base_fail:
        failures.append(
            f"predicate_audit_fail_rate regressed: baseline={base_fail:.2f} → post={post_fail:.2f}"
        )

    return (not failures, failures)


def main() -> int:
    manifest = load_json(MANIFEST)
    if not isinstance(manifest, dict) or "documents" not in manifest:
        print(f"ERROR: cannot read manifest at {MANIFEST}", file=sys.stderr)
        return 2

    report: dict = {"docs": defaultdict(dict)}
    arm_scores: dict[str, list[DocScore]] = {arm: [] for arm in ARMS}

    for entry in manifest["documents"]:
        if entry.get("content_status") != "authored":
            # skip deferred / stub documents — they have no content to audit yet
            continue
        doc_id = entry["doc_id"]
        gt_raw = load_json(GROUND_TRUTH_DIR / Path(entry["ground_truth_path"]).name)
        gt: dict = gt_raw if isinstance(gt_raw, dict) else {}
        for arm in ARMS:
            score = DocScore(doc_id=doc_id, arm=arm)
            for run_idx in range(1, RUNS_PER_DOC + 1):
                collect_run(doc_id, arm, run_idx, gt, score)
            arm_scores[arm].append(score)
            report["docs"][doc_id][arm] = {
                "runs_collected": len(score.verdict_tuples_per_run),
                "verdict_consistency_rate": consistency_rate(score.verdict_tuples_per_run),
                "ground_truth_hits": score.ground_truth_hits,
                "ground_truth_total": score.ground_truth_total,
                "main_context_tokens": score.main_context_tokens,
                "schema_pass_runs": sum(score.schema_passes),
                "predicate_fail_runs": sum(score.predicate_audit_fails),
            }

    for arm in ARMS:
        report[arm] = aggregate(arm_scores[arm])

    passed, failures = evaluate_thresholds(report)
    report["ship_decision"] = {"pass": passed, "failures": failures}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=list))

    print(json.dumps({k: report[k] for k in ARMS + ("ship_decision",)}, indent=2, default=list))
    if not passed:
        print("\nSHIP DECISION: BLOCKED — see failures above", file=sys.stderr)
        return 1
    print("\nSHIP DECISION: PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
