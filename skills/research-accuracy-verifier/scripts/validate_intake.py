#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.20",
# ]
# ///
"""Validate intake JSON against schema and business rules.

Two-stage pattern (continue past schema failure so business rules also report):
  1. JSON Schema (Draft-07) validation against schemas/intake.json
  2. Business rules:
     - document_type == "other" requires document_type_other
     - verification_tier == "custom" requires checks_enabled

Usage:
    uv run python validate_intake.py intake.json
    uv run python validate_intake.py intake.json --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

TIER_CHECKS: dict[str, list[str]] = {
    "1": ["citation_existence"],
    "2": ["citation_existence", "claim_alignment"],
    "3": [
        "citation_existence",
        "claim_alignment",
        "uncited_claims",
        "exact_quotes",
        "numerical_sanity",
        "named_entities",
        "internal_consistency",
        "prose_quality_audit",
    ],
}

# prose_quality_audit is restricted to Tier 3 (auto-included) or custom (opt-in).
# Tiers 1 and 2 have no prose-quality coverage.
TIER3_OR_CUSTOM_ONLY_CHECKS: set[str] = {"prose_quality_audit"}


class IntakeValidator:
    """Validate intake objects with schema + business rules (predicates from references/CONTRACTS.md)."""

    def __init__(self, schema_path: str | None = None) -> None:
        if schema_path:
            self.schema_path = Path(schema_path)
        else:
            self.schema_path = (
                Path(__file__).parent.parent / "schemas" / "intake.json"
            )
        with open(self.schema_path) as f:
            self.schema: dict[str, Any] = json.load(f)

    def validate(self, intake: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        # Stage 1: schema (continue past failures)
        for err in Draft7Validator(self.schema).iter_errors(intake):
            errors.append(f"schema: {err.message} at {list(err.absolute_path)}")

        # Stage 2: business rules — run regardless of schema failures
        if intake.get("document_type") == "other" and not intake.get("document_type_other"):
            errors.append(
                "business rule: document_type_other is required when document_type == 'other'"
            )

        tier = intake.get("verification_tier")
        if tier == "custom":
            if not intake.get("checks_enabled"):
                errors.append(
                    "business rule: checks_enabled is required when verification_tier == 'custom'"
                )
        elif tier in TIER_CHECKS:
            user_checks = intake.get("checks_enabled")
            if user_checks and set(user_checks) != set(TIER_CHECKS[tier]):
                warnings.append(
                    f"checks_enabled supplied for tier {tier} differs from canonical "
                    f"mapping; canonical wins (use tier == 'custom' to override)."
                )

        # Tier-3-or-custom-only checks (e.g., prose_quality_audit) cannot be requested
        # at tiers 1 or 2 even via explicit checks_enabled.
        if tier in {"1", "2"}:
            user_checks = set(intake.get("checks_enabled") or [])
            forbidden = user_checks & TIER3_OR_CUSTOM_ONLY_CHECKS
            if forbidden:
                errors.append(
                    f"business rule: {sorted(forbidden)} require verification_tier "
                    f"'3' or 'custom' (got '{tier}')"
                )

        return len(errors) == 0, errors, warnings

    def expand_tier(self, intake: dict[str, Any]) -> dict[str, Any]:
        """Return intake with checks_enabled populated from tier (no-op for custom)."""
        out = dict(intake)
        tier = out.get("verification_tier")
        if tier in TIER_CHECKS:
            out["checks_enabled"] = list(TIER_CHECKS[tier])
        return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate intake JSON")
    parser.add_argument("intake_file", help="Path to intake JSON")
    parser.add_argument("--schema", help="Custom schema path")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    intake_path = Path(args.intake_file)
    if not intake_path.exists():
        print(f"Error: file not found: {args.intake_file}", file=sys.stderr)
        sys.exit(1)
    intake = json.loads(intake_path.read_text())

    validator = IntakeValidator(args.schema)
    ok, errors, warnings = validator.validate(intake)

    if args.json:
        print(json.dumps({"valid": ok, "errors": errors, "warnings": warnings}, indent=2))
    else:
        print(f"Validating: {args.intake_file}")
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
