#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.20",
# ]
# ///
"""Validate FigureAuditFinding JSON against schema + predicates FD-P1..FD-P7.

FIGURE_INTEGRITY is a PARALLEL ADVISORY family (see references/CONTRACTS.md
§FIGURE_INTEGRITY). It does NOT touch the citation Verdict enum, the
SeverityMatrix, or P1-P9 — this validator is entirely separate from
`validate_finding.py`. The capability is advisory/triage only: a clean audit
is "no positive evidence of AI authorship", never proof; the supported burden
is "obtain source data / provenance", never "conclude misconduct".

Two-stage pattern (inherited from `verifier_kit.validate.SchemaValidator`):
  Stage 1: JSON Schema (Draft-07) against schemas/figure_audit_finding.json
  Stage 2: per-finding predicates FD-P1..FD-P6 (`run_predicates`)

  FD-P1. categorical == (metric_id in {1.1,1.2,2.1,2.2,3.1})
  FD-P2. severity == CRITICAL  ⟹  categorical is true AND score == 2
         (only a categorical ⚑=2 can be CRITICAL — aesthetics never can)
  FD-P3. dimension == D6_stylistic  ⟹  severity in {MINOR, INFORMATIONAL}
         (Bateman down-weight, encoded; two-sided — an over-minimization note
          is valid D6 output)
  FD-P4. recommended_action contains an allowed triage template AND no banned
         dispositive verb (advisory framing, encoded)
  FD-P5. dimension == D4_render_artifact  ⟹  decaying_signal_caveat non-null
         (4.x=0 is never exoneration)
  FD-P6. tier == 1_deterministic  ⟹  source_check non-null
         (deterministic findings must name the linter that produced them)

FD-P7 is an AUDIT-LEVEL post-condition (cross-finding), like P8 for the
citation pipeline — it cannot be enforced per-finding. It lives in
`validate_audit_verdict()` here:
  FD-P7. audit verdict FIGURE_INTEGRITY_FLAG  ⟹  at least one finding with
         score == 2 AND (categorical is true OR tier == 1_deterministic)
         (the flag cannot be raised on soft/aesthetic signals alone)

Usage:
    uv run python validate_figure_finding.py finding.json
    uv run python validate_figure_finding.py findings.json --batch
    uv run python validate_figure_finding.py findings.json --batch \\
        --audit-verdict FIGURE_INTEGRITY_FLAG   # also checks FD-P7
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Make `verifier_kit` importable whether run as a CLI from scripts/ or under
# pytest. The kit lives at skills/shared/verifier_kit/.
_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from verifier_kit.validate import SchemaValidator  # noqa: E402

# The five categorical ⚑ metrics (report-2 §6): label lexical validity, glyph
# integrity, encoding-value fidelity, closure/conservation, anatomical realism.
CATEGORICAL_METRICS = {"1.1", "1.2", "2.1", "2.2", "3.1"}

# FD-P4 — advisory framing. recommended_action must contain one of these
# triage templates and must NOT contain a dispositive verb.
ALLOWED_ACTION_TEMPLATES = (
    "obtain source data",
    "request generating code",
    "request the generating",
    "request provenance",
    "request ai-use disclosure",
    "request disclosure",
    "flag for closer human review",
    "flag for human review",
    "verify against cited source",
    "verify against the source",
    "request the source",
)
_BANNED_DISPOSITIVE_RE = re.compile(
    r"misconduct|fabricat(?:ed|ion)|fraud|guilty|confirmed\s+ai|conclude\s+",
    re.IGNORECASE,
)

FIGURE_VERDICTS = {
    "FIGURE_INTEGRITY_FLAG",
    "FIGURE_REVIEW_RECOMMENDED",
    "FIGURE_NO_POSITIVE_EVIDENCE",
}


class FigureFindingValidator(SchemaValidator):
    """Schema + FD-P1..FD-P6 for a single FigureAuditFinding."""

    def __init__(self, schema_path: str | None = None) -> None:
        base = Path(__file__).parent.parent / "schemas"
        resolved = (
            Path(schema_path) if schema_path else base / "figure_audit_finding.json"
        )
        super().__init__(resolved)
        self.schema_path = resolved

    def run_predicates(
        self,
        record: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        **ctx: Any,
    ) -> None:
        metric = record.get("metric_id")
        categorical = record.get("categorical")
        severity = record.get("severity")
        score = record.get("score")
        dimension = record.get("dimension")
        tier = record.get("tier")
        action = record.get("recommended_action") or ""

        # FD-P1 — categorical flag must match the metric set.
        if metric is not None and categorical is not None:
            expected = metric in CATEGORICAL_METRICS
            if categorical != expected:
                errors.append(
                    f"FD-P1: categorical={categorical} but metric_id {metric!r} "
                    f"{'is' if expected else 'is not'} a categorical tell "
                    f"(expected categorical={expected})."
                )

        # FD-P2 — only a categorical ⚑=2 can be CRITICAL.
        if severity == "CRITICAL" and not (categorical is True and score == 2):
            errors.append(
                "FD-P2: severity CRITICAL requires categorical==true AND score==2 "
                f"(got categorical={categorical}, score={score}). Aesthetic/soft "
                "signals can never be CRITICAL."
            )

        # FD-P3 — D6 (stylistic) is down-weighted (Bateman); never above MINOR.
        if dimension == "D6_stylistic" and severity not in {"MINOR", "INFORMATIONAL"}:
            errors.append(
                f"FD-P3: D6_stylistic findings cap at MINOR/INFORMATIONAL (got "
                f"{severity}). Decoration/default-palette signals are weak and "
                "two-sided — they never drive severity (Bateman CHI 2010)."
            )

        # FD-P4 — advisory framing: allowed template, no dispositive verb.
        low = action.lower()
        if _BANNED_DISPOSITIVE_RE.search(action):
            errors.append(
                f"FD-P4: recommended_action contains a dispositive verb "
                f"({action!r}). The audit triages attention — it never concludes "
                "misconduct/fabrication/fraud. Adjudication stays human."
            )
        if not any(t in low for t in ALLOWED_ACTION_TEMPLATES):
            errors.append(
                f"FD-P4: recommended_action {action!r} is not an allowed triage "
                f"template. Use one of: {', '.join(ALLOWED_ACTION_TEMPLATES)}."
            )

        # FD-P5 — D4 (decaying signal) requires the caveat.
        if dimension == "D4_render_artifact" and not record.get(
            "decaying_signal_caveat"
        ):
            errors.append(
                "FD-P5: D4_render_artifact findings require a non-null "
                "decaying_signal_caveat (4.x=0 is never exoneration; "
                "2026-generation models pass these cleanly)."
            )

        # FD-P6 — Tier-1 deterministic findings must name their source linter.
        if tier == "1_deterministic" and not record.get("source_check"):
            errors.append(
                "FD-P6: tier 1_deterministic requires a non-null source_check "
                "naming the linter fn (no hallucinated deterministic results)."
            )


def validate_audit_verdict(
    verdict: str, findings: list[dict[str, Any]]
) -> tuple[bool, list[str]]:
    """FD-P7 (audit-level): FIGURE_INTEGRITY_FLAG requires a hard finding.

    Returns (ok, errors).
    """
    errors: list[str] = []
    if verdict not in FIGURE_VERDICTS:
        errors.append(
            f"FD-P7: unknown audit verdict {verdict!r} (expected one of "
            f"{sorted(FIGURE_VERDICTS)})."
        )
        return False, errors
    if verdict == "FIGURE_INTEGRITY_FLAG":
        hard = [
            f
            for f in findings
            if f.get("score") == 2
            and (f.get("categorical") is True or f.get("tier") == "1_deterministic")
        ]
        if not hard:
            errors.append(
                "FD-P7: FIGURE_INTEGRITY_FLAG requires ≥1 finding with score==2 "
                "AND (categorical OR tier==1_deterministic). The flag cannot be "
                "raised on soft/aesthetic signals alone."
            )
    return len(errors) == 0, errors


def _validate_one(
    validator: FigureFindingValidator, record: dict[str, Any]
) -> tuple[bool, list[str], list[str]]:
    return validator.validate(record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate FigureAuditFinding JSON (FD-P1..FD-P7)."
    )
    parser.add_argument("path", help="finding JSON, or array of findings with --batch")
    parser.add_argument(
        "--batch", action="store_true", help="input is an array of findings"
    )
    parser.add_argument(
        "--audit-verdict",
        default=None,
        help="If given, also check FD-P7 against the batch (FIGURE_INTEGRITY_FLAG etc.)",
    )
    parser.add_argument("--schema", default=None)
    args = parser.parse_args(argv)

    validator = FigureFindingValidator(args.schema)
    data = json.loads(Path(args.path).read_text())

    records = data if args.batch else [data]
    if not isinstance(records, list):
        print("ERROR: --batch expects a JSON array", file=sys.stderr)
        return 2

    all_ok = True
    for i, rec in enumerate(records):
        ok, errors, warnings = _validate_one(validator, rec)
        tag = f"[{i}] " if args.batch else ""
        if ok:
            print(f"{tag}PASS {rec.get('id', '?')}")
        else:
            all_ok = False
            print(f"{tag}FAIL {rec.get('id', '?')}")
            for e in errors:
                print(f"    - {e}")
        for w in warnings:
            print(f"{tag}    (warn) {w}")

    if args.audit_verdict is not None:
        ok7, errors7 = validate_audit_verdict(args.audit_verdict, records)
        if ok7:
            print(f"FD-P7 PASS for verdict {args.audit_verdict}")
        else:
            all_ok = False
            for e in errors7:
                print(f"FD-P7 FAIL: {e}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
