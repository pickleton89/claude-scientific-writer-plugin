#!/usr/bin/env python3
"""Validate Finding JSON against schema and predicates P1-P5 from CONTRACTS.md.

Two-stage pattern (continue past schema failure so predicate checks also report):
  Stage 1: JSON Schema (Draft-07) against schemas/finding.json
  Stage 2: Predicates P1-P5
    P1. verdict == UNVERIFIED ⟹ reason ∈ enum AND severity != CRITICAL
    P2. severity == CRITICAL ⟹ len(verification_path) >= 2
    P3. len(evidence) >= 1 AND every evidence has resolvable URL/PMID/DOI
    P4. verdict ∈ {QUOTE_*} ⟺ claim_type == "direct_quote"
    P5. severity == SeverityMatrix[document_type][verdict]

Usage:
    uv run python validate_finding.py finding.json --document-type manuscript
    uv run python validate_finding.py findings.json --batch --document-type grant
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

QUOTE_VERDICTS = {"QUOTE_VERIFIED", "QUOTE_PARAPHRASED", "QUOTE_FABRICATED"}
UNVERIFIED_REASONS = {
    "paywalled_full_text",
    "preprint_not_indexed",
    "api_timeout",
    "source_not_provided",
    "tier_does_not_cover",
    "other",
}


class FindingValidator:
    """Validate findings with schema + predicates P1-P5."""

    def __init__(
        self,
        schema_path: str | None = None,
        matrix_path: str | None = None,
    ) -> None:
        base = Path(__file__).parent.parent / "schemas"
        self.schema_path = Path(schema_path) if schema_path else base / "finding.json"
        self.matrix_path = Path(matrix_path) if matrix_path else base / "severity_matrix.values.json"
        with open(self.schema_path) as f:
            self.schema: dict[str, Any] = json.load(f)
        with open(self.matrix_path) as f:
            self.matrix: dict[str, dict[str, str]] = json.load(f)["matrix"]

    def expected_severity(self, document_type: str, verdict: str) -> str | None:
        return self.matrix.get(document_type, {}).get(verdict)

    def validate(
        self, finding: dict[str, Any], document_type: str
    ) -> tuple[bool, list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        # Stage 1: schema — continue past failures
        for err in Draft7Validator(self.schema).iter_errors(finding):
            errors.append(f"schema: {err.message} at {list(err.absolute_path)}")

        # Stage 2: predicates
        verdict = finding.get("verdict")
        severity = finding.get("severity")
        claim_type = finding.get("claim_type")
        verification_path = finding.get("verification_path") or []
        evidence = finding.get("evidence") or []
        reason = finding.get("reason")

        # P1
        if verdict == "UNVERIFIED":
            if reason not in UNVERIFIED_REASONS:
                errors.append("P1: verdict == UNVERIFIED requires reason ∈ enum")
            if severity == "CRITICAL":
                errors.append("P1: verdict == UNVERIFIED MUST NOT be severity CRITICAL")

        # P2
        if severity == "CRITICAL" and len(verification_path) < 2:
            errors.append(
                f"P2: severity == CRITICAL requires ≥2 verification_path entries "
                f"(got {len(verification_path)})"
            )

        # P3
        if not evidence:
            errors.append("P3: at least one evidence entry required")
        else:
            for i, ev in enumerate(evidence):
                if not (ev.get("url") and isinstance(ev["url"], str) and ev["url"].strip()):
                    errors.append(f"P3: evidence[{i}] missing resolvable URL/PMID/DOI")

        # P4
        if verdict in QUOTE_VERDICTS and claim_type != "direct_quote":
            errors.append(
                f"P4: verdict {verdict} requires claim_type == 'direct_quote' (got {claim_type})"
            )
        if claim_type == "direct_quote" and verdict and verdict not in QUOTE_VERDICTS | {"UNVERIFIED"}:
            warnings.append(
                f"P4 advisory: claim_type 'direct_quote' usually pairs with QUOTE_* verdicts (got {verdict})"
            )

        # P5
        if verdict and severity:
            expected = self.expected_severity(document_type, verdict)
            if expected is None:
                errors.append(
                    f"P5: no matrix entry for document_type={document_type}, verdict={verdict}"
                )
            elif expected != severity:
                errors.append(
                    f"P5: severity mismatch — matrix[{document_type}][{verdict}] = {expected}, "
                    f"finding has {severity}"
                )

        return len(errors) == 0, errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Finding JSON")
    parser.add_argument("finding_file", help="Path to finding JSON (single or batch)")
    parser.add_argument(
        "--document-type",
        required=True,
        choices=["grant", "manuscript", "lit_review", "slides", "report", "memo", "other"],
    )
    parser.add_argument("--batch", action="store_true", help="Treat input as array of findings")
    parser.add_argument("--schema", help="Custom schema path")
    parser.add_argument("--matrix", help="Custom matrix values path")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    p = Path(args.finding_file)
    if not p.exists():
        print(f"Error: file not found: {args.finding_file}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(p.read_text())
    findings = data if args.batch else [data]

    validator = FindingValidator(args.schema, args.matrix)
    results: list[dict[str, Any]] = []
    all_ok = True
    for i, f in enumerate(findings):
        ok, errs, warns = validator.validate(f, args.document_type)
        all_ok = all_ok and ok
        results.append(
            {"index": i, "id": f.get("id"), "valid": ok, "errors": errs, "warnings": warns}
        )

    if args.json:
        print(json.dumps({"valid": all_ok, "results": results}, indent=2))
    else:
        for r in results:
            tag = "VALID" if r["valid"] else "INVALID"
            print(f"[{r['index']}] id={r['id']} {tag}")
            for e in r["errors"]:
                print(f"  ERROR: {e}")
            for w in r["warnings"]:
                print(f"  WARN:  {w}")
        print(f"Overall: {'VALID' if all_ok else 'INVALID'}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
