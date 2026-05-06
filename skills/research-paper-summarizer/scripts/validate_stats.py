#!/usr/bin/env python3
"""Validate stats.json against schema and Q5/R5 rule predicates.

Two-stage pattern (continue past schema failure so predicate checks also report),
mirroring skills/research-accuracy-verifier/scripts/validate_finding.py:

  Stage 1: JSON Schema (Draft-07) against schemas/stats.json
  Stage 2: Rule predicates loaded from
           skills/shared/references/prose_standards_thresholds.yaml
    Q5 (numerical_consistency, CRITICAL):
      every stats[] entry has verbatim=true AND non-empty source_location.
    R5 (numerical_consistency_full, CRITICAL):
      no two stats[] entries share a claim_id with conflicting (value, unit) pairs.
    X-count (cross-check, CRITICAL):
      preserved_numerics_count == len(stats).

The script reads Q5/R5 metadata from prose_standards_thresholds.yaml so the
authoritative severity/source list is never duplicated in code; only the
operational test is encoded here.

Usage:
    uv run python validate_stats.py paper_stats.json
    uv run python validate_stats.py paper_stats.json --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover - bootstrap path
    print(
        "Error: PyYAML is required. Install with `uv pip install pyyaml`.",
        file=sys.stderr,
    )
    sys.exit(2)


SHARED_THRESHOLDS_RELPATH = Path("../shared/references/prose_standards_thresholds.yaml")


class StatsValidator:
    """Validate stats.json with schema + rule predicates Q5/R5."""

    def __init__(
        self,
        schema_path: str | None = None,
        thresholds_path: str | None = None,
    ) -> None:
        base = Path(__file__).resolve().parent.parent
        self.schema_path = (
            Path(schema_path) if schema_path else base / "schemas" / "stats.json"
        )
        self.thresholds_path = (
            Path(thresholds_path)
            if thresholds_path
            else (base / SHARED_THRESHOLDS_RELPATH).resolve()
        )
        with open(self.schema_path) as f:
            self.schema: dict[str, Any] = json.load(f)
        with open(self.thresholds_path) as f:
            self.thresholds: dict[str, Any] = yaml.safe_load(f) or {}

    def _rule_meta(self, rule_id: str) -> dict[str, Any]:
        """Locate rule metadata by rule_id across thresholds passes."""
        for section in self.thresholds.values():
            if not isinstance(section, dict):
                continue
            for entry in section.values():
                if isinstance(entry, dict) and entry.get("rule_id") == rule_id:
                    return entry
        return {}

    def validate(
        self, stats_doc: dict[str, Any]
    ) -> tuple[bool, list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        # Stage 1: schema — collect all errors, continue.
        for err in Draft7Validator(self.schema).iter_errors(stats_doc):
            errors.append(f"schema: {err.message} at {list(err.absolute_path)}")

        stats = stats_doc.get("stats") or []
        rule_compliance = stats_doc.get("rule_compliance") or {}
        preserved = stats_doc.get("preserved_numerics_count")
        q5_meta = self._rule_meta("Q5")
        r5_meta = self._rule_meta("R5")
        q5_severity = q5_meta.get("severity", "CRITICAL")
        r5_severity = r5_meta.get("severity", "CRITICAL")

        # X-count cross-check
        if isinstance(preserved, int) and preserved != len(stats):
            errors.append(
                f"X-count: preserved_numerics_count={preserved} disagrees with "
                f"len(stats)={len(stats)}"
            )

        # Q5: every entry verbatim=true AND source_location non-empty
        q5_failures: list[str] = []
        for i, s in enumerate(stats):
            if not isinstance(s, dict):
                continue  # schema already flagged
            cid = s.get("claim_id", f"index {i}")
            if s.get("verbatim") is not True:
                q5_failures.append(
                    f"{cid}: verbatim is not True (Q5 requires verbatim source preservation)"
                )
            loc = s.get("source_location")
            if not (isinstance(loc, str) and loc.strip()):
                q5_failures.append(f"{cid}: source_location is empty (Q5 requires anchor)")
        if q5_failures:
            errors.append(f"Q5 [{q5_severity}]: {len(q5_failures)} violation(s)")
            for f in q5_failures:
                errors.append(f"  Q5 ▸ {f}")

        # R5: no two entries with same claim_id may have conflicting (value, unit)
        seen: dict[str, tuple[Any, Any]] = {}
        r5_failures: list[str] = []
        for s in stats:
            if not isinstance(s, dict):
                continue
            cid = s.get("claim_id")
            if not isinstance(cid, str):
                continue
            pair = (s.get("value"), s.get("unit"))
            if cid in seen and seen[cid] != pair:
                r5_failures.append(
                    f"{cid}: conflicting (value, unit) pairs {seen[cid]} vs {pair}"
                )
            else:
                seen.setdefault(cid, pair)
        if r5_failures:
            errors.append(f"R5 [{r5_severity}]: {len(r5_failures)} violation(s)")
            for f in r5_failures:
                errors.append(f"  R5 ▸ {f}")

        # rule_compliance self-attestation must agree with computed result.
        # 'unknown' is tolerated (partial extractions) but emitted as a warning
        # so callers know the file isn't a clean pass.
        computed_q5 = "pass" if not q5_failures else "fail"
        computed_r5 = "pass" if not r5_failures else "fail"
        attested_q5 = rule_compliance.get("Q5")
        attested_r5 = rule_compliance.get("R5")

        if attested_q5 == "unknown":
            warnings.append("rule_compliance.Q5 is 'unknown' — partial extraction; treat with caution")
        elif attested_q5 not in (computed_q5, None):
            errors.append(
                f"rule_compliance.Q5={attested_q5!r} disagrees with computed {computed_q5!r}"
            )

        if attested_r5 == "unknown":
            warnings.append("rule_compliance.R5 is 'unknown' — partial extraction; treat with caution")
        elif attested_r5 not in (computed_r5, None):
            errors.append(
                f"rule_compliance.R5={attested_r5!r} disagrees with computed {computed_r5!r}"
            )

        return len(errors) == 0, errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate stats.json")
    parser.add_argument("stats_file", help="Path to stats.json")
    parser.add_argument("--schema", help="Custom schema path")
    parser.add_argument(
        "--thresholds",
        help="Custom prose_standards_thresholds.yaml path",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    p = Path(args.stats_file)
    if not p.exists():
        print(f"Error: file not found: {args.stats_file}", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        print(f"Error: not valid JSON: {exc}", file=sys.stderr)
        sys.exit(2)

    validator = StatsValidator(args.schema, args.thresholds)
    ok, errs, warns = validator.validate(data)

    if args.json:
        print(
            json.dumps(
                {
                    "file": str(p),
                    "valid": ok,
                    "errors": errs,
                    "warnings": warns,
                },
                indent=2,
            )
        )
    else:
        tag = "VALID" if ok else "INVALID"
        print(f"{p.name}: {tag}")
        for e in errs:
            print(f"  ERROR: {e}")
        for w in warns:
            print(f"  WARN:  {w}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
