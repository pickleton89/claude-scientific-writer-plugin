#!/usr/bin/env python3
"""Validate an assembled audit_report.json against schema and predicate P8.

Two-stage pattern delegated to `verifier_kit.validate.SchemaValidator`:
  Stage 1: JSON Schema (Draft-07) against schemas/audit_report.json
  Stage 2: Predicate P8 (this module's `run_predicates`)
    P8 (Tier-3 cherry-picking sweep). Intake-domain ∈ {biomedical,mixed} AND
       (tier == "3" OR (tier == "custom" AND "uncited_claims" ∈ checks_enabled))
       ⟹ every (stage="3", verdict="VERIFIED") matrix entry MUST be covered
       by either:
         (a) a findings[] entry whose verification_path[*].result_summary
             contains the tag `cherry_picking:<claim_id>` AND `USI=` AND has
             at least one method=="scite_context" entry; OR
         (b) a header.coverage_caveats[] string of shape
             `cherry_picking:<claim_id>: <reason>`.

P8 is also enforced transitively from `render_report.generate_report()` so an
audit cannot render past a violation even if this CLI is skipped.

Usage:
    uv run python validate_audit_report.py audit_report.json --intake intake.json
    uv run python validate_audit_report.py audit_report.json --intake intake.json --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from verifier_kit.validate import SchemaValidator  # noqa: E402

P8_DOMAINS = {"biomedical", "mixed"}
_USI_RE = re.compile(r"USI\s*=", re.IGNORECASE)


def _p8_active(intake: dict[str, Any]) -> bool:
    """Return True iff P8's trigger conditions are met for this intake."""
    if intake.get("domain") not in P8_DOMAINS:
        return False
    tier = intake.get("verification_tier")
    if tier == "3":
        return True
    if tier == "custom":
        checks = intake.get("checks_enabled") or []
        if "uncited_claims" in checks:
            return True
    return False


def _claim_tag_re(claim_id: str) -> re.Pattern[str]:
    """Match `cherry_picking:<claim_id>` as a word-bounded tag.

    Word boundary on the right prevents `cherry_picking:C1` from matching
    `cherry_picking:C12` (false positive across overlapping ids).
    """
    return re.compile(
        rf"cherry_picking:{re.escape(claim_id)}\b",
        re.IGNORECASE,
    )


def _finding_covers_claim(finding: dict[str, Any], claim_id: str) -> bool:
    """A Stage-4 cherry-picking finding covers claim_id iff some
    verification_path entry has method=='scite_context', its result_summary
    contains `cherry_picking:<claim_id>`, and `USI=` appears in the same
    result_summary."""
    tag = _claim_tag_re(claim_id)
    if finding.get("verdict") != "OVERGENERALIZED":
        return False
    for entry in finding.get("verification_path") or []:
        if not isinstance(entry, dict):
            continue
        method = (entry.get("method") or "").lower()
        if method != "scite_context":
            continue
        summary = entry.get("result_summary") or ""
        if tag.search(summary) and _USI_RE.search(summary):
            return True
    return False


def _caveat_covers_claim(caveats: list[Any], claim_id: str) -> bool:
    """A coverage caveat covers claim_id iff some entry starts with
    `cherry_picking:<claim_id>: ` (prefix-tag, colon, space)."""
    prefix = f"cherry_picking:{claim_id}: "
    prefix_lower = prefix.lower()
    for c in caveats:
        if isinstance(c, str) and c.lower().startswith(prefix_lower):
            return True
    return False


class AuditReportValidator(SchemaValidator):
    """Validate audit_report.json with schema + predicate P8."""

    def __init__(self, schema_path: str | None = None) -> None:
        base = Path(__file__).parent.parent / "schemas"
        resolved = Path(schema_path) if schema_path else base / "audit_report.json"
        super().__init__(resolved)
        self.schema_path = resolved

    def run_predicates(
        self,
        record: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        **ctx: Any,
    ) -> None:
        intake = ctx.get("intake")
        if intake is None:
            errors.append("internal: run_predicates requires intake")
            return

        if not _p8_active(intake):
            return  # P8 trigger conditions not met; skip silently.

        matrix = record.get("verification_matrix") or []
        findings = record.get("findings") or []
        caveats = (record.get("header") or {}).get("coverage_caveats") or []

        stage3_verified_ids: list[str] = []
        for m in matrix:
            if not isinstance(m, dict):
                continue
            if str(m.get("stage")) == "3" and m.get("verdict") == "VERIFIED":
                cid = m.get("claim_id")
                if isinstance(cid, str) and cid:
                    stage3_verified_ids.append(cid)

        for claim_id in stage3_verified_ids:
            covered_by_finding = any(
                _finding_covers_claim(f, claim_id)
                for f in findings
                if isinstance(f, dict)
            )
            if covered_by_finding:
                continue
            if _caveat_covers_claim(caveats, claim_id):
                continue
            errors.append(
                f"P8: Stage-3 VERIFIED claim_id={claim_id!r} has no matching "
                "Stage-4 cherry-picking finding (OVERGENERALIZED with "
                f"method=='scite_context', result_summary containing "
                f"'cherry_picking:{claim_id}' and 'USI=') and no "
                f"'cherry_picking:{claim_id}: <reason>' entry in "
                "header.coverage_caveats[]."
            )

    def validate(  # type: ignore[override]
        self,
        report: dict[str, Any],
        intake: dict[str, Any],
    ) -> tuple[bool, list[str], list[str]]:
        return super().validate(report, intake=intake)


def run_p8(
    report: dict[str, Any], intake: dict[str, Any]
) -> tuple[str, list[str]]:
    """Run only the P8 predicate against an already-loaded report + intake.

    Skips the schema-validation half of the two-stage pipeline so callers
    (like `render_report.generate_report()`) that already trust the report's
    shape can run the cross-stage post-condition cheaply.

    Returns
    -------
    (status, errors): status ∈ {"pass", "fail", "n/a"}. "n/a" indicates the
    P8 trigger conditions were not met for this intake (general-domain
    audit, Tier-1/2, or custom tier without uncited_claims).
    """
    if not _p8_active(intake):
        return "n/a", []
    validator = AuditReportValidator()
    errors: list[str] = []
    warnings: list[str] = []
    validator.run_predicates(report, errors, warnings, intake=intake)
    return ("pass" if not errors else "fail"), errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate an audit_report.json (schema + P8)."
    )
    parser.add_argument("report_file", help="Path to audit_report.json")
    parser.add_argument(
        "--intake",
        required=True,
        help="Path to the intake.json from the same audit (carries domain + tier).",
    )
    parser.add_argument("--schema", help="Custom audit_report.json schema path")
    parser.add_argument("--json", action="store_true", help="Emit JSON result")
    args = parser.parse_args()

    report_path = Path(args.report_file)
    intake_path = Path(args.intake)
    if not report_path.exists():
        print(f"Error: file not found: {report_path}", file=sys.stderr)
        sys.exit(2)
    if not intake_path.exists():
        print(f"Error: file not found: {intake_path}", file=sys.stderr)
        sys.exit(2)

    report = json.loads(report_path.read_text())
    intake = json.loads(intake_path.read_text())

    # validator.validate() runs schema + P8 (via run_predicates). We compute
    # p8_status separately only for the display badge: when the trigger
    # conditions aren't met (general domain, Tier-1/2, etc.) we want to
    # surface "n/a" rather than the binary VALID/INVALID. _p8_active() is
    # a single dict lookup, so this is cheaper than re-running run_p8.
    validator = AuditReportValidator(args.schema)
    ok, errors, warnings = validator.validate(report, intake)
    if not _p8_active(intake):
        p8_status = "n/a"
    else:
        p8_status = "pass" if not any(e.startswith("P8:") for e in errors) else "fail"

    if args.json:
        print(
            json.dumps(
                {
                    "valid": ok,
                    "p8_status": p8_status,
                    "errors": errors,
                    "warnings": warnings,
                },
                indent=2,
            )
        )
    else:
        tag = "VALID" if ok else "INVALID"
        print(f"{report_path.name}: {tag} (P8: {p8_status})")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN:  {w}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
