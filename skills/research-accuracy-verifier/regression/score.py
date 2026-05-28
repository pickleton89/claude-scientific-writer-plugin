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
import re
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


R_PREDICATE_NAMES = ("R1", "R2", "R3", "R4", "R5", "R6")
ARTIFACT_SIDECARS = (
    "document_inventory.json",
    "reference_map.json",
    "resolved_sources.json",
    "external_evidence.json",
)


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
    artifact_coverage_per_run: list[dict] = field(default_factory=list)
    r_predicate_audit_per_run: list[dict] = field(default_factory=list)


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


def _needle_in_haystack(needle: str, haystack: str) -> bool:
    """Substring match, but with digit-boundary guards for numeric needles.

    Plain `in` would let `"1"` match inside `"187"` or `"187"` inside `"1870"`.
    For needles that begin with a digit (covers `187`, `47.3`, `0.001`), we
    require the match not be flanked by digits or decimal points on either
    side — preventing accidental hits inside larger numbers. Non-numeric
    needles (`"smith2024_pembro_nsclc"`, `"C-01"`) use plain substring.
    """
    if not needle:
        return True
    if not needle[0].isdigit():
        return needle in haystack
    pattern = rf"(?<![\d.]){re.escape(needle)}(?![\d.])"
    return re.search(pattern, haystack) is not None


def _evidence_pin_satisfied(expected: dict | None, evidence: list) -> bool:
    """All expected values must co-occur in a single evidence entry.

    A Stage 6 fallback path (re-extract from full text) can produce the right
    verdict + severity without the cooperation-contract pin (paper_id +
    claim_id from stats.json). Requiring co-occurrence in one entry — rather
    than the union — distinguishes cooperation success from fallback success.
    """
    if not expected:
        return True
    if not isinstance(evidence, list) or not evidence:
        return False
    needles = [str(v) for v in expected.values() if v is not None and v != ""]
    if not needles:
        return True
    for entry in evidence:
        if not isinstance(entry, dict):
            continue
        haystack = " ".join(str(entry.get(k, "")) for k in ("source", "url", "snippet"))
        if all(_needle_in_haystack(n, haystack) for n in needles):
            return True
    return False


def _finding_matches_expectation(
    expectation: dict, findings: list, style_findings: list
) -> bool:
    """One expectation alternative — match against either main or style findings."""
    expected_severity = expectation.get("severity")
    pin = expectation.get("evidence_must_contain")
    if "verdict" in expectation:
        verdict = expectation["verdict"]
        return any(
            f.get("verdict") == verdict
            and _matches_severity(f.get("severity", ""), expected_severity)
            and _evidence_pin_satisfied(pin, f.get("evidence", []))
            for f in findings
        )
    if "style_verdict" in expectation:
        style_verdict = expectation["style_verdict"]
        rule_id = expectation.get("rule_id")
        return any(
            f.get("verdict") == style_verdict
            and (rule_id is None or f.get("rule_id") == rule_id)
            and _matches_severity(f.get("severity", ""), expected_severity)
            and _evidence_pin_satisfied(pin, f.get("evidence", []))
            for f in style_findings
        )
    return False


def seeded_error_forbidden(err: dict, findings: list, style_findings: list) -> bool:
    """True if the run emitted a verdict the ground truth forbids.

    `must_not_emit` lists expectations (same shape as `expected_findings_any_of`
    entries) that represent FAILURE modes — e.g., a wrong-but-valid-DOI fixture
    forbids `VERIFIED`, because a resolving-but-mismatched citation graded
    VERIFIED is exactly the regression P9 guards against. A forbidden match
    overrides recall: the seeded error is NOT counted as caught even if an
    acceptable expectation also matched (a verifier that emits both the right
    and the forbidden verdict for the same claim has produced a broken audit).

    Scope note: matched doc-wide, not per-claim. The regression docs that use
    `must_not_emit` are single-citation by construction, so any forbidden
    verdict in the report pertains to the seeded citation.
    """
    forbidden = err.get("must_not_emit")
    if not forbidden:
        return False
    return any(
        _finding_matches_expectation(expectation, findings, style_findings)
        for expectation in forbidden
    )


def seeded_error_satisfied(err: dict, findings: list, style_findings: list) -> bool:
    """A seeded error counts as caught iff an acceptable expectation matches AND
    no forbidden (`must_not_emit`) verdict was emitted."""
    if seeded_error_forbidden(err, findings, style_findings):
        return False
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
        {"style_verdict": expected, "severity": expected_severity},
        findings,
        style_findings,
    )


def _ledger_hit_rate(ledger: dict | None) -> tuple[int, float | None]:
    """Return (entry_count, hit_rate).

    Cache hits are not persisted directly. Each ledger entry is one fresh
    fetch (a miss). `consumed_by_findings` records every finding that used
    that entry; reuse after the first consumer is a cache hit. So:

        total_calls  = Σ len(consumed_by_findings)
        cache_misses = number of ledger entries that were consumed at all
        cache_hits   = max(0, total_calls − cache_misses)
        hit_rate     = cache_hits / total_calls  (None if total_calls == 0)
    """
    if not isinstance(ledger, dict):
        return 0, None
    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        return 0, None
    entry_count = len(entries)
    consumption_counts = [
        len(e.get("consumed_by_findings", [])) for e in entries if isinstance(e, dict)
    ]
    total_calls = sum(consumption_counts)
    if total_calls == 0:
        return entry_count, None
    cache_misses = sum(1 for c in consumption_counts if c > 0)
    cache_hits = max(0, total_calls - cache_misses)
    return entry_count, cache_hits / total_calls


def extract_artifact_coverage(run_dir: Path) -> dict:
    """Derive artifact_coverage column from run-dir sidecar files.

    Plan §11.3 hypothesized `header.evidence_pinning` on audit_report.json,
    but the post-Phase-3 audit_report header carries no such field. The
    sidecar files are the canonical evidence of artifact coverage, so we
    derive presence from the filesystem and ledger stats from
    external_evidence.json directly.
    """
    ledger = load_json(run_dir / "external_evidence.json")
    entries_count, hit_rate = _ledger_hit_rate(
        ledger if isinstance(ledger, dict) else None
    )
    return {
        "document_inventory_present": (run_dir / "document_inventory.json").exists(),
        "reference_map_present": (run_dir / "reference_map.json").exists(),
        "resolved_sources_present": (run_dir / "resolved_sources.json").exists(),
        "external_evidence_entries": entries_count,
        "ledger_hit_rate": hit_rate,
    }


def extract_r_predicate_audit(audit: dict | None) -> dict:
    """Derive r_predicate_audit column from audit_meta sidecar fields.

    Mirrors the existing audit_meta.predicate_audit pattern: regression
    runners attach `audit_meta.r_predicate_status` (or legacy
    `audit_meta.r_predicates`) — a dict mapping R1..R6 → "pass"/"fail"/"n/a".
    Missing keys default to "n/a" so the column shape is stable.
    """
    if not isinstance(audit, dict):
        return {name: "n/a" for name in R_PREDICATE_NAMES}
    audit_meta = audit.get("audit_meta", {}) if isinstance(audit, dict) else {}
    statuses = (
        audit_meta.get("r_predicate_status") or audit_meta.get("r_predicates") or {}
    )
    if not isinstance(statuses, dict):
        statuses = {}
    out: dict[str, str] = {}
    for name in R_PREDICATE_NAMES:
        val = statuses.get(name, "n/a")
        out[name] = val if val in ("pass", "fail", "n/a") else "n/a"
    return out


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

    score.artifact_coverage_per_run.append(extract_artifact_coverage(run_dir))
    score.r_predicate_audit_per_run.append(
        extract_r_predicate_audit(audit if isinstance(audit, dict) else None)
    )

    findings = audit.get("findings", []) if isinstance(audit, dict) else []
    style_findings = audit.get("style_findings", []) if isinstance(audit, dict) else []

    # verdict tuples for cross-run consistency — combine main + style findings
    tuples = {
        (f.get("claim_id", f.get("id", "")), f.get("verdict", "")) for f in findings
    }
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
        score.predicate_audit_fails.append(
            any(v != "pass" for v in predicate_results.values())
        )


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


def _aggregate_artifact_coverage(scores: list[DocScore]) -> dict:
    rows = [row for s in scores for row in s.artifact_coverage_per_run]
    if not rows:
        return {
            "coverage_rate": None,
            "ledger_hit_rate": {"median": None, "max": None, "min": None, "n": 0},
            "n_runs": 0,
        }
    all_present_count = sum(
        1
        for r in rows
        if r["document_inventory_present"]
        and r["reference_map_present"]
        and r["resolved_sources_present"]
        and r["external_evidence_entries"] > 0
    )
    hit_rates = [r["ledger_hit_rate"] for r in rows if r["ledger_hit_rate"] is not None]
    return {
        "coverage_rate": all_present_count / len(rows),
        "ledger_hit_rate": {
            "median": statistics.median(hit_rates) if hit_rates else None,
            "max": max(hit_rates) if hit_rates else None,
            "min": min(hit_rates) if hit_rates else None,
            "n": len(hit_rates),
        },
        "n_runs": len(rows),
    }


def _aggregate_r_predicate_audit(scores: list[DocScore]) -> dict:
    rows = [row for s in scores for row in s.r_predicate_audit_per_run]
    pass_rates: dict[str, float | None] = {}
    for name in R_PREDICATE_NAMES:
        considered = [r.get(name, "n/a") for r in rows if r.get(name, "n/a") != "n/a"]
        if not considered:
            pass_rates[name] = None
        else:
            pass_rates[name] = sum(1 for v in considered if v == "pass") / len(
                considered
            )
    return {"pass_rate": pass_rates, "n_runs": len(rows)}


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

    coverage = _aggregate_artifact_coverage(scores)
    r_audit = _aggregate_r_predicate_audit(scores)

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
        "artifact_coverage_rate": coverage["coverage_rate"],
        "ledger_hit_rate_median": coverage["ledger_hit_rate"]["median"],
        "ledger_hit_rate_max": coverage["ledger_hit_rate"]["max"],
        "ledger_hit_rate_min": coverage["ledger_hit_rate"]["min"],
        "r_predicate_pass_rate": r_audit["pass_rate"],
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
    if (
        base_recall is not None
        and post_recall is not None
        and post_recall < base_recall
    ):
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
                "verdict_consistency_rate": consistency_rate(
                    score.verdict_tuples_per_run
                ),
                "ground_truth_hits": score.ground_truth_hits,
                "ground_truth_total": score.ground_truth_total,
                "main_context_tokens": score.main_context_tokens,
                "schema_pass_runs": sum(score.schema_passes),
                "predicate_fail_runs": sum(score.predicate_audit_fails),
                "artifact_coverage": score.artifact_coverage_per_run,
                "r_predicate_audit": score.r_predicate_audit_per_run,
            }

    for arm in ARMS:
        report[arm] = aggregate(arm_scores[arm])

    passed, failures = evaluate_thresholds(report)
    report["ship_decision"] = {"pass": passed, "failures": failures}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=list))

    print(
        json.dumps(
            {k: report[k] for k in ARMS + ("ship_decision",)}, indent=2, default=list
        )
    )
    if not passed:
        print("\nSHIP DECISION: BLOCKED — see failures above", file=sys.stderr)
        return 1
    print("\nSHIP DECISION: PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
