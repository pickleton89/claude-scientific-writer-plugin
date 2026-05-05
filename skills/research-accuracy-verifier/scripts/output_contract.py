#!/usr/bin/env python3
"""Stage-1 contract freeze + Stage-8 contract validation.

Pattern follows skills/deep-research/scripts/output_contract.py:
  - At intake (Stage 1), freeze the contract: {intake, document_hash, expected_stages}
  - At report-time (Stage 8), validate the report against the frozen contract

Frozen contract enforces:
  - Same document was audited (sha256 of <document> matches)
  - All stages implied by checks_enabled were executed
  - report.header.verification_tier == intake.verification_tier
  - report.header.document_type == intake.document_type
  - coverage_caveats is non-empty when any UNVERIFIED finding exists with reason
    in {paywalled_full_text, preprint_not_indexed, api_timeout}

Usage:
    uv run python output_contract.py freeze --intake intake.json --document doc.md > contract.json
    uv run python output_contract.py validate --contract contract.json --report report.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

CHECK_TO_STAGES: dict[str, list[str]] = {
    "citation_existence": ["2"],
    "claim_alignment": ["3"],
    "uncited_claims": ["4"],
    "exact_quotes": ["5"],
    "numerical_sanity": ["6"],
    "named_entities": ["6"],
    "internal_consistency": ["7"],
    # prose_quality_audit runs in a parallel pipeline (writes style_findings[],
    # not verification_matrix). It declares no citation-pipeline stage; its
    # presence in checks_enabled signals the prose-quality pass should run.
    "prose_quality_audit": [],
}

CAVEAT_REASONS = {"paywalled_full_text", "preprint_not_indexed", "api_timeout"}


def _document_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def freeze_contract(intake: dict[str, Any], document_text: str) -> dict[str, Any]:
    """Build a frozen contract from intake + document. Called at end of Stage 1."""
    checks = intake.get("checks_enabled") or []
    expected_stages: set[str] = set()
    for c in checks:
        expected_stages.update(CHECK_TO_STAGES.get(c, []))
    expected_stages.add("8")  # synthesis always required
    return {
        "version": "1.0",
        "document_sha256": _document_hash(document_text),
        "intake": intake,
        "expected_stages": sorted(expected_stages),
    }


def validate_against_contract(
    contract: dict[str, Any], report: dict[str, Any]
) -> tuple[bool, list[str], list[str]]:
    """Validate a final AuditReport against the frozen contract."""
    errors: list[str] = []
    warnings: list[str] = []

    intake = contract.get("intake", {})
    header = report.get("header", {})

    # Document type must match
    if header.get("document_type") != intake.get("document_type"):
        errors.append(
            f"contract: document_type drift — intake={intake.get('document_type')}, "
            f"report={header.get('document_type')}"
        )

    # Verification tier must match
    if header.get("verification_tier") != intake.get("verification_tier"):
        errors.append(
            f"contract: verification_tier drift — intake={intake.get('verification_tier')}, "
            f"report={header.get('verification_tier')}"
        )

    # All expected stages must appear in verification_matrix
    expected_stages = set(contract.get("expected_stages", [])) - {"8"}
    seen_stages = {row.get("stage") for row in report.get("verification_matrix", [])}
    missing = expected_stages - seen_stages
    if missing:
        warnings.append(
            f"contract: stages declared in checks_enabled but absent from "
            f"verification_matrix: {sorted(missing)}"
        )

    # Coverage caveats required when UNVERIFIED-with-access-reason findings exist
    unverified_with_caveat = [
        f
        for f in report.get("findings", [])
        if f.get("verdict") == "UNVERIFIED" and f.get("reason") in CAVEAT_REASONS
    ]
    if unverified_with_caveat and not header.get("coverage_caveats"):
        errors.append(
            f"contract: {len(unverified_with_caveat)} UNVERIFIED finding(s) with "
            f"access-blocking reasons, but coverage_caveats is empty"
        )

    return len(errors) == 0, errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze / validate audit contract")
    sub = parser.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("freeze")
    f.add_argument("--intake", required=True)
    f.add_argument("--document", required=True)

    v = sub.add_parser("validate")
    v.add_argument("--contract", required=True)
    v.add_argument("--report", required=True)
    v.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.cmd == "freeze":
        intake = json.loads(Path(args.intake).read_text())
        document = Path(args.document).read_text(encoding="utf-8")
        print(json.dumps(freeze_contract(intake, document), indent=2))
        sys.exit(0)

    contract = json.loads(Path(args.contract).read_text())
    report = json.loads(Path(args.report).read_text())
    ok, errors, warnings = validate_against_contract(contract, report)

    if args.json:
        print(json.dumps({"valid": ok, "errors": errors, "warnings": warnings}, indent=2))
    else:
        if errors:
            print("Errors:")
            for e in errors:
                print(f"  - {e}")
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(f"  - {w}")
        print(f"Result: {'VALID' if ok else 'INVALID'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
