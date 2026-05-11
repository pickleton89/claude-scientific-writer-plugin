#!/usr/bin/env python3
"""Validate Finding JSON against schema and predicates P1-P5, P7 from CONTRACTS.md.

Two-stage pattern delegated to `verifier_kit.validate.SchemaValidator`:
  Stage 1: JSON Schema (Draft-07) against schemas/finding.json
  Stage 2: Predicates P1-P5, P7 (this module's `run_predicates`)
    P1. verdict == UNVERIFIED ⟹ reason ∈ enum AND severity != CRITICAL
    P2. severity == CRITICAL ⟹ len(verification_path) >= 2
    P3. len(evidence) >= 1 AND every evidence has resolvable URL/PMID/DOI
    P4. verdict ∈ {QUOTE_*} ⟺ claim_type == "direct_quote"
    P5. severity == SeverityMatrix[document_type][verdict]
    P7. domain ∈ {biomedical,mixed} AND stage == 2 AND
        verdict ∈ {VERIFIED, METADATA_MISMATCH, UNSUPPORTED}
        ⟹ verification_path[] contains either method == "scite_context"
          OR an entry with tool matching /scite/i
        — see CONTRACTS.md §Hard predicates. Skipped when domain or stage
        is None (back-compat for ad-hoc CLI calls without those flags).

P8 (Tier-3 cherry-picking sweep) is a cross-stage post-condition and lives
in `validate_audit_report.py` — it cannot be enforced from a per-finding
validator.

Usage:
    uv run python validate_finding.py finding.json --document-type manuscript
    uv run python validate_finding.py findings.json --batch --document-type grant
    uv run python validate_finding.py finding.json --document-type grant \\
        --domain biomedical --stage 2     # enables P7
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Make `verifier_kit` importable when this script runs either as a CLI
# from the verifier scripts/ dir or under pytest (which preconfigures
# scripts/ on sys.path but not skills/shared/). The kit lives at
# skills/shared/verifier_kit/, so adding skills/shared/ to sys.path makes
# `from verifier_kit.validate import SchemaValidator` resolve.
_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from verifier_kit.validate import SchemaValidator  # noqa: E402

QUOTE_VERDICTS = {"QUOTE_VERIFIED", "QUOTE_PARAPHRASED", "QUOTE_FABRICATED"}
UNVERIFIED_REASONS = {
    "paywalled_full_text",
    "preprint_not_indexed",
    "api_timeout",
    "source_not_provided",
    "tier_does_not_cover",
    "other",
}

# P7: domains for which the Stage-2 Scite retraction probe is mandatory.
P7_DOMAINS = {"biomedical", "mixed"}
# P7: verdicts that require the probe (UNVERIFIED is exempt — the citation
# itself wasn't resolved, so no DOI was available to feed Scite).
P7_VERDICTS = {"VERIFIED", "METADATA_MISMATCH", "UNSUPPORTED"}
_SCITE_TOOL_RE = re.compile(r"scite", re.IGNORECASE)


class FindingValidator(SchemaValidator):
    """Validate findings with schema + predicates P1-P5, P7.

    Subclasses `verifier_kit.validate.SchemaValidator` to inherit the
    continue-past-schema-failure two-stage pattern. P1-P5 and P7 live in
    `run_predicates`. The public `validate(finding, document_type, *,
    domain=None, stage=None)` signature stays back-compatible with the
    pre-Sprint-3 two-arg form: omitting `domain` or `stage` skips P7 only,
    so legacy callers and tests pass unchanged.
    """

    def __init__(
        self,
        schema_path: str | None = None,
        matrix_path: str | None = None,
    ) -> None:
        base = Path(__file__).parent.parent / "schemas"
        resolved_schema = Path(schema_path) if schema_path else base / "finding.json"
        super().__init__(resolved_schema)
        self.schema_path = resolved_schema
        self.matrix_path = (
            Path(matrix_path) if matrix_path else base / "severity_matrix.values.json"
        )
        with open(self.matrix_path) as f:
            self.matrix: dict[str, dict[str, str]] = json.load(f)["matrix"]

    def expected_severity(self, document_type: str, verdict: str) -> str | None:
        return self.matrix.get(document_type, {}).get(verdict)

    def run_predicates(
        self,
        record: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        **ctx: Any,
    ) -> None:
        document_type = ctx.get("document_type")
        if document_type is None:
            errors.append("internal: run_predicates requires document_type")
            return

        verdict = record.get("verdict")
        severity = record.get("severity")
        claim_type = record.get("claim_type")
        verification_path = record.get("verification_path") or []
        evidence = record.get("evidence") or []
        reason = record.get("reason")

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

        # P7: Stage-2 Scite retraction probe (biomedical/mixed only).
        # Skipped when domain or stage is None — callers that don't supply
        # them opt out of P7 (e.g., ad-hoc CLI debugging, legacy tests).
        domain = ctx.get("domain")
        stage = ctx.get("stage")
        if (
            domain in P7_DOMAINS
            and stage == 2
            and verdict in P7_VERDICTS
        ):
            has_scite = False
            for entry in verification_path:
                if not isinstance(entry, dict):
                    continue
                method = (entry.get("method") or "").lower()
                tool = entry.get("tool") or ""
                if method == "scite_context" or _SCITE_TOOL_RE.search(tool):
                    has_scite = True
                    break
            if not has_scite:
                errors.append(
                    f"P7: biomedical/mixed Stage-2 finding with verdict {verdict} "
                    "requires a Scite probe entry in verification_path[] "
                    "(method == 'scite_context' or tool ~ /scite/i). "
                    "Silence is a violation — log the probe outcome (or its "
                    "failure mode) even on API error."
                )

    def validate(  # type: ignore[override]
        self,
        finding: dict[str, Any],
        document_type: str,
        *,
        domain: str | None = None,
        stage: int | None = None,
    ) -> tuple[bool, list[str], list[str]]:
        """Validate a finding.

        `domain` and `stage` gate predicate P7. When either is `None`
        (default), P7 is skipped — preserving back-compat with all
        pre-P7 callers and tests that pass only `(finding, document_type)`.
        """
        return super().validate(
            finding,
            document_type=document_type,
            domain=domain,
            stage=stage,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Finding JSON")
    parser.add_argument("finding_file", help="Path to finding JSON (single or batch)")
    parser.add_argument(
        "--document-type",
        required=True,
        choices=["grant", "manuscript", "lit_review", "slides", "report", "memo", "other"],
    )
    parser.add_argument(
        "--domain",
        choices=["biomedical", "general", "mixed"],
        help="Intake domain. Required to activate P7 (Stage-2 Scite probe).",
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=range(2, 8),
        help="Originating pipeline stage. Required to activate P7.",
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
        ok, errs, warns = validator.validate(
            f, args.document_type, domain=args.domain, stage=args.stage
        )
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
