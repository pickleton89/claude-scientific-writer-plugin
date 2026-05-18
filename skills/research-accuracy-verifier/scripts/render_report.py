#!/usr/bin/env python3
"""Render an AuditReport (validated against schemas/audit_report.json) to markdown.

Pattern model: skills/peer-review/scripts/calculate_scores.py generate_report().

Public API:
    generate_report(
        report: dict,
        *,
        intake: dict | None = None,
        artifact_paths: dict[str, Path | str] | None = None,
        enforcement: Literal["auto","advisory","required"] = "auto",
    ) -> str

When `intake` is supplied, the renderer also enforces predicate P8 (Tier-3
cherry-picking sweep) via `validate_audit_report.run_p8(...)` before
rendering. On P8 failure, the call raises `ValueError` with a structured
message listing the uncovered Stage-3 VERIFIED claim_ids. P8 cannot be
silenced by skipping the CLI step — every render path that supplies an
intake goes through the gate. When `intake is None`, P8 is skipped
(back-compat for legacy callers and tests that render synthetic reports
without an intake context).

When `artifact_paths` is supplied, prepends an evidence-pinned marker as
the first line of the rendered markdown — mirrors deep-research's
`evidence_pinned: true` marker (`skills/deep-research/agents/compiler.md
§Evidence-pinned marker`). Downstream consumers (peer-review,
scientific-writing) can detect the marker to switch into diff-mode against
the artifact set. When effective enforcement (after resolving `"auto"` via
`thresholds.ARTIFACT_ENFORCEMENT`) is `"required"`, also refuses to render
if any path is missing or non-existent — raises `ValueError`.

Usage:
    uv run python render_report.py report.json
    uv run python render_report.py report.json --intake intake.json --out report.md
    uv run python render_report.py report.json --intake intake.json \\
        --audit-dir research/audits/my-slug/ --out report.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from thresholds import resolve_enforcement
from validate_audit_report import Enforcement, run_p8

# Artifact-set the marker enumerates. Order matches plan §7.1 marker spec.
_ARTIFACT_KINDS: tuple[str, ...] = (
    "document_inventory",
    "reference_map",
    "resolved_sources",
    "external_evidence",
)
_ARTIFACT_FILENAMES: dict[str, str] = {kind: f"{kind}.json" for kind in _ARTIFACT_KINDS}
_MARKER_SCHEMA_VERSION = "1.0"

SEVERITY_ORDER = ["CRITICAL", "MAJOR", "MINOR", "INFORMATIONAL"]
P8_PASS_NOTE = (
    "Predicate P8 (Tier-3 cherry-picking sweep) enforced: every Stage-3 "
    "VERIFIED biomedical/mixed claim is covered by either a Stage-4 "
    "cherry-picking finding or a `cherry_picking:<claim_id>: <reason>` "
    "coverage caveat."
)

SCITE_BIAS_CAVEAT = (
    "Scite-derived sentiment classifications are reported per Scite classification "
    "(Scite has documented bias toward 'mentioning' classification; see tool-lookup.yaml "
    "literature.citation_context notes)."
)


def _scite_used(report: dict[str, Any]) -> bool:
    for f in report.get("findings", []):
        for vp in f.get("verification_path", []):
            if vp.get("method") == "scite_context":
                return True
    return False


def _section_header(report: dict[str, Any]) -> str:
    h = report["header"]
    caveats = list(h.get("coverage_caveats", []))
    if _scite_used(report) and SCITE_BIAS_CAVEAT not in caveats:
        caveats.append(SCITE_BIAS_CAVEAT)

    lines = [
        f"# Accuracy Audit — {h['document_title']}",
        "",
        f"- **Document type:** {h['document_type']}",
        f"- **Date checked:** {h['date_checked']}",
        f"- **Verification tier:** {h['verification_tier']}",
        f"- **Sources consulted:** {', '.join(h['sources_consulted']) or '(none recorded)'}",
        f"- **Overall confidence:** {h['overall_confidence']}",
        "",
        f"> {h['confidence_justification']}",
        "",
    ]
    if caveats:
        lines.append("**Coverage caveats:**")
        lines.extend(f"- {c}" for c in caveats)
        lines.append("")
    return "\n".join(lines)


def _section_executive_summary(report: dict[str, Any]) -> str:
    return f"## Executive Summary\n\n{report['executive_summary']}\n"


def _finding_table(f: dict[str, Any]) -> str:
    loc = f["location"]
    loc_str = f"{loc['section']}, paragraph {loc['paragraph']}"
    if loc.get("line"):
        loc_str += f" (line {loc['line']})"

    vp_lines = []
    for i, vp in enumerate(f["verification_path"], 1):
        vp_lines.append(f"({i}) `{vp['method']}` via {vp['tool']}: {vp['result_summary']}")
    vp_str = " ".join(vp_lines)

    ev_lines = [f"{ev['source']} — {ev['url']}" for ev in f["evidence"]]
    ev_str = "; ".join(ev_lines)

    rows = [
        ("Location", loc_str),
        ("Claim (verbatim)", f"\"{f['claim_verbatim']}\""),
        ("Verification path", vp_str),
        ("Evidence", ev_str),
        ("Verdict", f"`{f['verdict']}`"),
        ("Severity", f["severity"]),
        ("Recommended action", f["recommended_action"]),
        ("Confidence", f["confidence"]),
    ]
    if f.get("reason"):
        rows.append(("Reason (UNVERIFIED)", f["reason"]))

    out = ["| Field | Content |", "|---|---|"]
    for k, v in rows:
        # Escape pipes in cell content
        v_safe = str(v).replace("|", "\\|")
        out.append(f"| {k} | {v_safe} |")
    return "\n".join(out)


def _section_findings(report: dict[str, Any]) -> str:
    findings = report.get("findings", [])
    if not findings:
        return "## Findings\n\nNo findings emitted.\n"

    by_sev: dict[str, list[dict[str, Any]]] = {s: [] for s in SEVERITY_ORDER}
    for f in findings:
        by_sev.setdefault(f["severity"], []).append(f)

    parts = ["## Findings\n"]
    for sev in SEVERITY_ORDER:
        items = by_sev.get(sev, [])
        if not items:
            continue
        parts.append(f"### {sev} ({len(items)})\n")
        for f in items:
            parts.append(f"#### {f['id']} — {f['claim_type']}\n")
            parts.append(_finding_table(f))
            parts.append("")
    return "\n".join(parts)


def _section_matrix(report: dict[str, Any]) -> str:
    rows = report.get("verification_matrix", [])
    if not rows:
        return "## Verification Matrix\n\n(empty)\n"
    out = [
        "## Verification Matrix",
        "",
        "| Claim ID | Stage | Verdict | Severity |",
        "|---|---|---|---|",
    ]
    for r in rows:
        out.append(f"| {r['claim_id']} | {r['stage']} | `{r['verdict']}` | {r['severity']} |")
    out.append("")
    return "\n".join(out)


def _section_methodology(report: dict[str, Any]) -> str:
    return f"## Methodology\n\n{report['methodology_note']}\n"


def _build_marker(
    artifact_paths: dict[str, Path | str], audit_dir: Path | str | None
) -> str:
    """Build the `<!-- audit_evidence_pinned: ... -->` first-line marker.

    Format mirrors plan §7.1:
        <!-- audit_evidence_pinned: true artifacts: A,B,C,D
             audit_dir: research/audits/<slug>/ schema_version: 1.0 -->
    Filenames listed in the canonical `_ARTIFACT_KINDS` order.
    """
    filenames = ",".join(_ARTIFACT_FILENAMES[k] for k in _ARTIFACT_KINDS)
    if audit_dir is None:
        # Derive from any supplied artifact path — they should all share a parent.
        sample = next(iter(artifact_paths.values()), None)
        audit_dir = Path(sample).parent if sample else Path(".")
    audit_dir_str = str(audit_dir).rstrip("/") + "/"
    return (
        f"<!-- audit_evidence_pinned: true artifacts: {filenames} "
        f"audit_dir: {audit_dir_str} schema_version: {_MARKER_SCHEMA_VERSION} -->"
    )


def _validate_artifact_paths(
    artifact_paths: dict[str, Path | str], enforcement: str
) -> None:
    """In required mode, refuse to render if any path is missing/nonexistent.

    Only checks file presence — full schema/predicate validation is the
    responsibility of `scripts/validate_artifact.py`, which Stage-8
    finalization (or the upstream test fixture) is expected to have run.
    """
    if enforcement != "required":
        return
    missing: list[str] = []
    for kind in _ARTIFACT_KINDS:
        p = artifact_paths.get(kind)
        if p is None:
            missing.append(f"{kind} (path not provided)")
            continue
        path = Path(p)
        if not path.exists():
            missing.append(f"{kind} ({path} not found)")
    if missing:
        raise ValueError(
            "Cannot render in required-enforcement mode — artifact set "
            "incomplete:\n  - " + "\n  - ".join(missing)
        )


def generate_report(
    report: dict[str, Any],
    *,
    intake: dict[str, Any] | None = None,
    artifact_paths: dict[str, Path | str] | None = None,
    audit_dir: Path | str | None = None,
    enforcement: Enforcement = "auto",
) -> str:
    """Render an AuditReport dict to markdown.

    When `intake` is supplied, enforces predicate P8 before rendering:
    raises `ValueError` if any Stage-3 VERIFIED claim lacks a cherry-picking
    finding or a `cherry_picking:<claim_id>: <reason>` coverage caveat. When
    `intake is None`, P8 is skipped (back-compat).

    When `artifact_paths` is supplied, prepends the evidence-pinned marker
    as the first line. In required-enforcement mode, refuses to render if
    the artifact set is incomplete (any path missing or file nonexistent).
    `audit_dir` is the slug directory; when omitted, derived from the
    parent of the first artifact_paths value.
    """
    p8_status: str | None = None
    if intake is not None:
        p8_status, p8_errors = run_p8(report, intake)
        if p8_status == "fail":
            raise ValueError(
                "P8 (Tier-3 cherry-picking sweep) failed; cannot render audit. "
                "Loop back to Stage 4 and emit the missing cherry-picking "
                "finding(s) or coverage caveat(s):\n  "
                + "\n  ".join(p8_errors)
            )

    if artifact_paths is not None:
        _validate_artifact_paths(artifact_paths, resolve_enforcement(enforcement))

    sections: list[str] = []
    if artifact_paths is not None:
        sections.append(_build_marker(artifact_paths, audit_dir) + "\n")
    sections.extend([
        _section_header(report),
        _section_executive_summary(report),
        _section_findings(report),
        _section_matrix(report),
        _section_methodology(report),
    ])
    if p8_status == "pass":
        sections.append(f"> {P8_PASS_NOTE}\n")
    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render AuditReport JSON to markdown")
    parser.add_argument("report_file", help="Path to audit report JSON")
    parser.add_argument(
        "--intake",
        help=(
            "Path to intake.json. When supplied, enforces P8 "
            "(Tier-3 cherry-picking sweep) before rendering and raises on "
            "failure. Omit to render without P8 enforcement."
        ),
    )
    parser.add_argument(
        "--audit-dir",
        dest="audit_dir",
        help=(
            "Path to the audit directory (e.g. research/audits/<slug>/). "
            "When supplied, auto-resolves the 4 evidence-pinned artifacts "
            "(document_inventory.json, reference_map.json, "
            "resolved_sources.json, external_evidence.json) and prepends the "
            "evidence-pinned marker as the first line of the output."
        ),
    )
    parser.add_argument(
        "--no-enforce-artifacts",
        dest="no_enforce_artifacts",
        action="store_true",
        help=(
            "Force advisory mode regardless of thresholds.ARTIFACT_ENFORCEMENT. "
            "Allows rendering an audit whose artifact set is incomplete "
            "(migration escape hatch — see references/README_migration.md)."
        ),
    )
    parser.add_argument("--out", help="Write to file instead of stdout")
    args = parser.parse_args()

    p = Path(args.report_file)
    if not p.exists():
        print(f"Error: file not found: {args.report_file}", file=sys.stderr)
        sys.exit(1)

    report = json.loads(p.read_text())
    intake: dict[str, Any] | None = None
    if args.intake:
        ip = Path(args.intake)
        if not ip.exists():
            print(f"Error: file not found: {args.intake}", file=sys.stderr)
            sys.exit(1)
        intake = json.loads(ip.read_text())

    artifact_paths: dict[str, Path | str] | None = None
    audit_dir: Path | None = None
    if args.audit_dir:
        audit_dir = Path(args.audit_dir)
        artifact_paths = {
            kind: audit_dir / fname
            for kind, fname in _ARTIFACT_FILENAMES.items()
        }

    enforcement: Enforcement = "advisory" if args.no_enforce_artifacts else "auto"

    try:
        md = generate_report(
            report,
            intake=intake,
            artifact_paths=artifact_paths,
            audit_dir=audit_dir,
            enforcement=enforcement,
        )
    except ValueError as e:
        print(f"Render aborted: {e}", file=sys.stderr)
        sys.exit(1)
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
