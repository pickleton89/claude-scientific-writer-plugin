#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Token-savings analyzer for the cooperation contract (Sprint 4 item 2).

Classifies each finding's evidence list by source class — stats / txt /
source_meta / other — and approximates main-context token cost using the
4-chars-per-token heuristic already used by score.py. Compares observed
behavior to the design promise of "10–30k tokens eliminated per cited paper"
and reports how often the cooperation path is engaged vs bypassed.

Usage:
  uv run regression/measure_tokens.py <audit_report.json> [--sources DIR]
  uv run regression/measure_tokens.py research/audits/06_lit_review_cited_paper_numerical/audit_report.json

Outputs JSON to stdout. Designed to run on a single audit; aggregation across
the regression bed is left to score.py once Item 3 runs are collected.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHARS_PER_TOKEN = 4
REGRESSION_ROOT = Path(__file__).parent
DEFAULT_SOURCES = REGRESSION_ROOT / "sources"


def classify_evidence_entry(entry: dict) -> str:
    """Return one of: 'stats', 'txt', 'source_meta', 'other'."""
    blob = " ".join(
        str(entry.get(k, "")) for k in ("source", "url", "snippet")
    ).lower()
    if "_stats.json" in blob or "stats.json" in blob:
        return "stats"
    if "_source_meta.json" in blob or "source_meta.json" in blob:
        return "source_meta"
    if ".txt" in blob or ".pdf" in blob:
        return "txt"
    return "other"


def approx_tokens(path: Path) -> int:
    if not path.exists():
        return 0
    return path.stat().st_size // CHARS_PER_TOKEN


def analyze(audit_path: Path, sources_dir: Path) -> dict:
    audit = json.loads(audit_path.read_text())
    findings = audit.get("findings", [])

    per_finding = []
    counts = {"stats_only": 0, "txt_only": 0, "dual": 0, "source_meta_only": 0, "other": 0}
    stage6_counts = {"stats_only": 0, "txt_only": 0, "dual": 0, "other": 0}

    for f in findings:
        evidence = f.get("evidence", [])
        classes = sorted({classify_evidence_entry(e) for e in evidence if isinstance(e, dict)})
        if classes == ["stats"]:
            label = "stats_only"
        elif classes == ["txt"]:
            label = "txt_only"
        elif "stats" in classes and "txt" in classes:
            label = "dual"
        elif classes == ["source_meta"]:
            label = "source_meta_only"
        else:
            label = "other"
        counts[label] = counts.get(label, 0) + 1

        # Stage-6 (numerical) findings: presence of 'stats' or 'txt' as evidence
        # source. Excludes Stage-2 citation-existence findings (source_meta only).
        if "stats" in classes or "txt" in classes:
            if label == "stats_only":
                stage6_counts["stats_only"] += 1
            elif label == "txt_only":
                stage6_counts["txt_only"] += 1
            elif label == "dual":
                stage6_counts["dual"] += 1
            else:
                stage6_counts["other"] += 1

        per_finding.append(
            {
                "id": f.get("id"),
                "verdict": f.get("verdict"),
                "severity": f.get("severity"),
                "evidence_count": len(evidence),
                "classification": label,
            }
        )

    # Per-paper file sizes — naive: any paper subdir under sources/.
    per_paper = []
    if sources_dir.exists():
        for paper_dir in sorted(p for p in sources_dir.iterdir() if p.is_dir()):
            full_text = next(paper_dir.glob("*.txt"), None)
            stats = next(paper_dir.glob("*_stats.json"), None)
            source_meta = next(paper_dir.glob("*_source_meta.json"), None)
            per_paper.append(
                {
                    "paper_id": paper_dir.name,
                    "full_text_tokens": approx_tokens(full_text) if full_text else 0,
                    "stats_tokens": approx_tokens(stats) if stats else 0,
                    "source_meta_tokens": approx_tokens(source_meta) if source_meta else 0,
                    "design_promise_min_tokens_eliminated": 10_000,
                    "design_promise_max_tokens_eliminated": 30_000,
                }
            )

    stage6_total = sum(stage6_counts.values())
    cooperation_engaged = stage6_counts["stats_only"] + stage6_counts["dual"]
    cooperation_bypassed = stage6_counts["txt_only"]

    return {
        "audit_path": str(audit_path),
        "finding_count": len(findings),
        "per_finding": per_finding,
        "counts_all_findings": counts,
        "counts_stage6_only": stage6_counts,
        "cooperation_summary": {
            "stage6_findings": stage6_total,
            "cooperation_engaged": cooperation_engaged,
            "cooperation_bypassed": cooperation_bypassed,
            "engagement_rate": (
                cooperation_engaged / stage6_total if stage6_total else None
            ),
            "stats_only_rate": (
                stage6_counts["stats_only"] / stage6_total if stage6_total else None
            ),
            "dual_read_rate": (
                stage6_counts["dual"] / stage6_total if stage6_total else None
            ),
        },
        "per_paper_token_estimates": per_paper,
        "notes": [
            "engagement_rate = (stats_only + dual) / stage6_findings — fraction "
            "where the verifier acknowledged stats.json at all.",
            "stats_only_rate = pure cooperation success: stats.json sufficed and "
            "full text was not cited as evidence on this finding.",
            "dual_read_rate = stats.json cited AND full text cited — cooperation "
            "engaged for evidence pinning but full text still loaded.",
            "Per-finding evidence classes do NOT directly measure main-context "
            "tokens consumed: if Stage 1 pulls full text once and reuses it "
            "across all Stage-6 findings, the txt-class evidence is free even "
            "when stats.json suffices. Real savings require the orchestrator "
            "to elide the Stage-1 full-text pull when stats.json covers all "
            "numerical claims — currently not enforced by SKILL.md.",
            "design_promise_*_tokens_eliminated calibrated to real papers "
            "(30-80k tokens of full text). Synthetic fixtures with full_text_"
            "tokens < 1000 cannot validate this promise.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit_report", type=Path, help="Path to audit_report.json")
    parser.add_argument(
        "--sources",
        type=Path,
        default=DEFAULT_SOURCES,
        help=f"Directory of per-paper source artifacts (default: {DEFAULT_SOURCES})",
    )
    args = parser.parse_args(argv)

    if not args.audit_report.exists():
        print(f"ERROR: audit_report not found: {args.audit_report}", file=sys.stderr)
        return 2

    report = analyze(args.audit_report, args.sources)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
