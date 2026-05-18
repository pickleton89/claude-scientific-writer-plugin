#!/usr/bin/env python3
"""Validate an assembled audit_report.json against schema, P8, and R1–R6.

Two-stage pattern delegated to `verifier_kit.validate.SchemaValidator`:
  Stage 1: JSON Schema (Draft-07) against schemas/audit_report.json
  Stage 2: Predicates (this module's `run_predicates`)

    P8 (Tier-3 cherry-picking sweep). Intake-domain ∈ {biomedical,mixed} AND
       (tier == "3" OR (tier == "custom" AND "uncited_claims" ∈ checks_enabled))
       ⟹ every (stage="3", verdict="VERIFIED") matrix entry MUST be covered
       by either a Stage-4 OVERGENERALIZED cherry-picking finding OR a
       `cherry_picking:<claim_id>: <reason>` coverage caveat.

    R1 (findings ids resolve in claim_inventory). When `claim_inventory.json`
       is supplied via ctx, every `findings[].id` must appear in items[].id.
    R2 (evidence paper_ids resolve in resolved_sources). When
       `resolved_sources.json` is supplied AND intake.sources_available != "none",
       every non-null `findings[].evidence[].paper_id` must resolve.
    R3 (citation keys resolve in reference_map). When `reference_map.json` is
       supplied, every `findings[].citations[].key` must appear in
       citations[].key.
    R4 (claim_verbatim equality vs document_inventory). When
       `document_inventory.json` + the normalized document text are supplied,
       every `findings[].claim_verbatim` must appear as a substring of the
       text within the paragraph addressed by `findings[].location` (after
       QuoteVerifier whitespace + unicode normalization).
    R6 (matrix claim_ids resolve in claim_inventory). When
       `claim_inventory.json` is supplied, every `verification_matrix[].claim_id`
       must appear in items[].id.

P8 + R1–R6 are also enforced transitively from `render_report.generate_report()`
so an audit cannot render past a violation even if this CLI is skipped.

Enforcement mode (from scripts/thresholds.ARTIFACT_ENFORCEMENT):
  "advisory" — R-predicate failures emit warnings; validation still ok=True.
  "required" — R-predicate failures emit errors; ok=False (Phase 3 default).
P8 always emits errors regardless of enforcement (it's an existing hard gate).

Usage:
    uv run python validate_audit_report.py audit_report.json --intake intake.json
    uv run python validate_audit_report.py audit_report.json --intake intake.json \\
        --claim-inventory ci.json --reference-map rm.json \\
        --resolved-sources rs.json --document-inventory di.json \\
        --document doc.txt --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Literal

_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from verifier_kit.validate import SchemaValidator  # noqa: E402

# Make sibling scripts importable for reusing QuoteVerifier (R4) and
# thresholds (R-predicate enforcement mode).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from thresholds import resolve_enforcement  # noqa: E402
from verify_exact_quote import QuoteVerifier  # noqa: E402

P8_DOMAINS = {"biomedical", "mixed"}
_USI_RE = re.compile(r"USI\s*=", re.IGNORECASE)

# R-predicate identifiers, used to prefix advisory warnings vs errors.
_R_PREDICATES = ("R1", "R2", "R3", "R4", "R5", "R6")

# Mapping of verification_path[].method values to external-evidence
# ledger tool names. A finding whose verification_path[] contains one of
# these methods MUST (per R5) have a matching ledger entry with the same
# (tool, paper_id). Keep in sync with schemas/finding.json verification_path
# method enum and thresholds.ARTIFACT_FRESHNESS_DAYS.
_LEDGER_METHODS: dict[str, str] = {
    "scite_context": "scite",
    "pubtator3_entity_check": "pubtator3",
}

Enforcement = Literal["auto", "advisory", "required"]


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
    """Validate audit_report.json with schema + predicate P8 + R1–R6."""

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

        # P8 — Tier-3 cherry-picking sweep (always hard error when active).
        self._run_p8(record, intake, errors)

        # R1–R6 — cross-artifact join integrity. Failure-mode AND skip-bucket
        # both controlled by enforcement: in required mode a missing artifact
        # is a hard error too (you can't validate against an artifact set the
        # caller didn't supply when the gate is required).
        artifacts = ctx.get("artifacts") or {}
        document_text = ctx.get("document_text")
        enforcement = resolve_enforcement(ctx.get("enforcement") or "auto")
        bucket = errors if enforcement == "required" else warnings
        skip_bucket = bucket  # same destination — keeps "skipped:" prefix detectable
        self._run_r1(record, artifacts, bucket, skip_bucket)
        self._run_r2(record, intake, artifacts, bucket, skip_bucket)
        self._run_r3(record, artifacts, bucket, skip_bucket)
        self._run_r4(record, artifacts, document_text, bucket, skip_bucket)
        self._run_r5(record, artifacts, bucket, skip_bucket)
        self._run_r6(record, artifacts, bucket, skip_bucket)

    def validate(  # type: ignore[override]
        self,
        report: dict[str, Any],
        intake: dict[str, Any],
        *,
        artifacts: dict[str, dict[str, Any]] | None = None,
        document_text: str | None = None,
        enforcement: Enforcement = "auto",
    ) -> tuple[bool, list[str], list[str]]:
        return super().validate(
            report,
            intake=intake,
            artifacts=artifacts or {},
            document_text=document_text,
            enforcement=enforcement,
        )

    # ── P8 ────────────────────────────────────────────────────────────────
    def _run_p8(
        self, record: dict[str, Any], intake: dict[str, Any], errors: list[str]
    ) -> None:
        if not _p8_active(intake):
            return

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

    # ── R1 ────────────────────────────────────────────────────────────────
    def _run_r1(
        self,
        record: dict[str, Any],
        artifacts: dict[str, Any],
        bucket: list[str],
        skip_bucket: list[str],
    ) -> None:
        ci = artifacts.get("claim_inventory")
        if ci is None:
            skip_bucket.append(
                "R1 skipped: claim_inventory.json not provided to validator"
            )
            return
        valid_ids = {
            item.get("id")
            for item in (ci.get("items") or [])
            if isinstance(item, dict) and item.get("id")
        }
        for f in record.get("findings") or []:
            if not isinstance(f, dict):
                continue
            fid = f.get("id")
            if fid and fid not in valid_ids:
                bucket.append(
                    f"R1: findings[id={fid!r}] does not resolve in "
                    f"claim_inventory.json items[]"
                )

    # ── R2 ────────────────────────────────────────────────────────────────
    def _run_r2(
        self,
        record: dict[str, Any],
        intake: dict[str, Any],
        artifacts: dict[str, Any],
        bucket: list[str],
        skip_bucket: list[str],
    ) -> None:
        if intake.get("sources_available") == "none":
            return  # No sources → no paper_id resolution possible.
        rs = artifacts.get("resolved_sources")
        if rs is None:
            skip_bucket.append(
                "R2 skipped: resolved_sources.json not provided to validator"
            )
            return
        valid_paper_ids = {
            src.get("paper_id")
            for src in (rs.get("sources") or [])
            if isinstance(src, dict) and src.get("paper_id")
        }
        for f in record.get("findings") or []:
            if not isinstance(f, dict):
                continue
            fid = f.get("id")
            for j, e in enumerate(f.get("evidence") or []):
                if not isinstance(e, dict):
                    continue
                pid = e.get("paper_id")
                if pid is None:
                    continue  # null permitted (web-sourced no-DOI evidence)
                if pid not in valid_paper_ids:
                    bucket.append(
                        f"R2: findings[id={fid!r}].evidence[{j}].paper_id={pid!r} "
                        f"does not resolve in resolved_sources.json sources[]"
                    )

    # ── R3 ────────────────────────────────────────────────────────────────
    def _run_r3(
        self,
        record: dict[str, Any],
        artifacts: dict[str, Any],
        bucket: list[str],
        skip_bucket: list[str],
    ) -> None:
        rm = artifacts.get("reference_map")
        if rm is None:
            skip_bucket.append(
                "R3 skipped: reference_map.json not provided to validator"
            )
            return
        valid_keys = {
            c.get("key")
            for c in (rm.get("citations") or [])
            if isinstance(c, dict) and c.get("key")
        }
        for f in record.get("findings") or []:
            if not isinstance(f, dict):
                continue
            fid = f.get("id")
            for j, c in enumerate(f.get("citations") or []):
                if not isinstance(c, dict):
                    continue
                k = c.get("key")
                if k and k not in valid_keys:
                    bucket.append(
                        f"R3: findings[id={fid!r}].citations[{j}].key={k!r} "
                        f"does not resolve in reference_map.json citations[]"
                    )

    # ── R4 ────────────────────────────────────────────────────────────────
    def _run_r4(
        self,
        record: dict[str, Any],
        artifacts: dict[str, Any],
        document_text: str | None,
        bucket: list[str],
        skip_bucket: list[str],
    ) -> None:
        di = artifacts.get("document_inventory")
        if di is None or document_text is None:
            skip_bucket.append(
                "R4 skipped: document_inventory.json and/or document text "
                "not provided to validator"
            )
            return

        verifier = QuoteVerifier()
        # Index sections by case-insensitive name for fuzzy name match;
        # paragraphs by section_id for ordinal lookup.
        sections = di.get("sections") or []
        paragraphs = di.get("paragraphs") or []
        section_by_name_lower = {}
        for s in sections:
            if isinstance(s, dict) and s.get("name"):
                section_by_name_lower.setdefault(s["name"].strip().lower(), s)
        paragraphs_by_section: dict[str, list[dict[str, Any]]] = {}
        for p in paragraphs:
            if isinstance(p, dict) and p.get("section_id"):
                paragraphs_by_section.setdefault(p["section_id"], []).append(p)
        # Sort each section's paragraphs by ordinal.
        for plist in paragraphs_by_section.values():
            plist.sort(key=lambda x: x.get("ordinal", 0))

        for f in record.get("findings") or []:
            if not isinstance(f, dict):
                continue
            fid = f.get("id")
            loc = f.get("location") or {}
            section_name = (loc.get("section") or "").strip().lower()
            paragraph_ordinal = loc.get("paragraph")
            claim = f.get("claim_verbatim") or ""
            if not claim:
                continue
            # Find section by exact-or-prefix match on name (handles
            # "Significance, paragraph 3" → "Significance"). Require ≥3-char
            # overlap to prevent one-letter section names from collapsing
            # into false-positive matches (e.g., section "A" matching any
            # location string starting with "a").
            section = section_by_name_lower.get(section_name)
            if section is None:
                for name_lower, s in section_by_name_lower.items():
                    overlap = min(len(name_lower), len(section_name))
                    if overlap < 3:
                        continue
                    if section_name.startswith(name_lower) or name_lower.startswith(
                        section_name
                    ):
                        section = s
                        break
            if section is None:
                bucket.append(
                    f"R4: findings[id={fid!r}].location.section={loc.get('section')!r} "
                    f"does not match any section in document_inventory.json"
                )
                continue
            plist = paragraphs_by_section.get(section.get("id"), [])
            if not (
                isinstance(paragraph_ordinal, int)
                and 1 <= paragraph_ordinal <= len(plist)
            ):
                bucket.append(
                    f"R4: findings[id={fid!r}].location.paragraph="
                    f"{paragraph_ordinal!r} out of range for section "
                    f"{section.get('id')!r} ({len(plist)} paragraphs)"
                )
                continue
            para = plist[paragraph_ordinal - 1]
            cs, ce = para.get("char_start"), para.get("char_end")
            if not (
                isinstance(cs, int)
                and isinstance(ce, int)
                and 0 <= cs <= ce <= len(document_text)
            ):
                bucket.append(
                    f"R4: findings[id={fid!r}] paragraph {para.get('id')!r} "
                    f"has out-of-range char offsets vs supplied document"
                )
                continue
            paragraph_text = document_text[cs:ce]
            mr = verifier.match(claim, paragraph_text)
            if mr.verdict != "QUOTE_VERIFIED":
                bucket.append(
                    f"R4: findings[id={fid!r}].claim_verbatim does not appear "
                    f"in paragraph {para.get('id')!r} (matched_form={mr.matched_form!r}, "
                    f"overlap={mr.overlap_ratio})"
                )

    # ── R5 ────────────────────────────────────────────────────────────────
    def _run_r5(
        self,
        record: dict[str, Any],
        artifacts: dict[str, Any],
        bucket: list[str],
        skip_bucket: list[str],
    ) -> None:
        """For every finding whose verification_path[] mentions a
        ledger-routed method (Scite/PubTator3/...), confirm that
        external_evidence.json has a matching entry with the same
        (tool, paper_id). Failure mode: probe text was hallucinated rather
        than executed.
        """
        ee = artifacts.get("external_evidence")
        if ee is None:
            skip_bucket.append(
                "R5 skipped: external_evidence.json not provided to validator"
            )
            return
        # Index ledger by (tool, paper_id) for O(1) probe-match lookup.
        ledger_keys: set[tuple[str, str | None]] = set()
        for entry in ee.get("entries") or []:
            if not isinstance(entry, dict):
                continue
            tool = entry.get("tool")
            pid = entry.get("paper_id")
            if isinstance(tool, str):
                ledger_keys.add((tool, pid or None))

        for f in record.get("findings") or []:
            if not isinstance(f, dict):
                continue
            fid = f.get("id")
            # Collect paper_ids from this finding's evidence[].
            paper_ids: set[str | None] = set()
            for e in f.get("evidence") or []:
                if isinstance(e, dict):
                    paper_ids.add(e.get("paper_id") or None)
            for step in f.get("verification_path") or []:
                if not isinstance(step, dict):
                    continue
                method = step.get("method")
                tool = _LEDGER_METHODS.get(method) if isinstance(method, str) else None
                if tool is None:
                    continue
                # Match if ANY of the finding's evidence paper_ids has a
                # ledger entry for this tool. If none do, fire R5.
                matched = any((tool, pid) in ledger_keys for pid in paper_ids)
                if not matched:
                    bucket.append(
                        f"R5: findings[id={fid!r}].verification_path step "
                        f"method={method!r} has no matching "
                        f"external_evidence.entries[] entry "
                        f"(tool={tool!r}, paper_id ∈ {sorted(p for p in paper_ids if p) or '<none>'}) — "
                        f"probe text may have been hallucinated rather than executed"
                    )

    # ── R6 ────────────────────────────────────────────────────────────────
    def _run_r6(
        self,
        record: dict[str, Any],
        artifacts: dict[str, Any],
        bucket: list[str],
        skip_bucket: list[str],
    ) -> None:
        ci = artifacts.get("claim_inventory")
        if ci is None:
            skip_bucket.append(
                "R6 skipped: claim_inventory.json not provided to validator"
            )
            return
        valid_ids = {
            item.get("id")
            for item in (ci.get("items") or [])
            if isinstance(item, dict) and item.get("id")
        }
        for j, m in enumerate(record.get("verification_matrix") or []):
            if not isinstance(m, dict):
                continue
            cid = m.get("claim_id")
            if cid and cid not in valid_ids:
                bucket.append(
                    f"R6: verification_matrix[{j}].claim_id={cid!r} does not "
                    f"resolve in claim_inventory.json items[]"
                )


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
    validator._run_p8(report, intake, errors)
    return ("pass" if not errors else "fail"), errors


def run_r_predicates(
    report: dict[str, Any],
    intake: dict[str, Any],
    *,
    artifacts: dict[str, dict[str, Any]] | None = None,
    document_text: str | None = None,
    enforcement: Enforcement = "auto",
) -> tuple[dict[str, str], list[str], list[str]]:
    """Run R1–R6 without schema validation.

    Returns
    -------
    (per_predicate_status, errors, warnings): per_predicate_status maps each
    predicate name to "pass" | "fail" | "n/a". "n/a" means the predicate's
    required artifact (or intake setting) wasn't supplied — in required mode
    that's also surfaced as an error in `errors`.

    Failure-mode and skip-mode bucket-routing both controlled by enforcement
    (defaults to `thresholds.ARTIFACT_ENFORCEMENT`).
    """
    validator = AuditReportValidator()
    errors: list[str] = []
    warnings: list[str] = []
    # Run all R-predicates by invoking the unified run_predicates with intake.
    validator.run_predicates(
        report,
        errors,
        warnings,
        intake=intake,
        artifacts=artifacts or {},
        document_text=document_text,
        enforcement=enforcement,
    )
    r_status = _derive_r_status(errors, warnings)
    # Filter outputs to drop the P8 line (run_p8 owns it).
    r_errors = [e for e in errors if not e.startswith("P8:")]
    return r_status, r_errors, warnings


def _derive_r_status(
    errors: list[str], warnings: list[str]
) -> dict[str, str]:
    """Compute the per-predicate status dict from collected messages.

    Scans BOTH errors and warnings for "{pred} skipped:" and "{pred}:" lines
    — in required mode the skip message lands in errors, in advisory mode it
    lands in warnings. "n/a" wins over "fail" when both prefixes appear (a
    skipped predicate has not actually run).
    """
    combined = [m for m in errors + warnings if not m.startswith("P8:")]
    r_status: dict[str, str] = {}
    for pred in _R_PREDICATES:
        skipped = any(m.startswith(f"{pred} skipped:") for m in combined)
        failed = any(
            m.startswith(f"{pred}:") and not m.startswith(f"{pred} skipped:")
            for m in combined
        )
        if skipped:
            r_status[pred] = "n/a"
        else:
            r_status[pred] = "fail" if failed else "pass"
    return r_status


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate an audit_report.json (schema + P8 + R1–R6)."
    )
    parser.add_argument("report_file", help="Path to audit_report.json")
    parser.add_argument(
        "--intake",
        required=True,
        help="Path to the intake.json from the same audit (carries domain + tier).",
    )
    parser.add_argument("--schema", help="Custom audit_report.json schema path")
    parser.add_argument(
        "--claim-inventory",
        help="Path to claim_inventory.json (enables R1 + R6).",
    )
    parser.add_argument(
        "--reference-map",
        help="Path to reference_map.json (enables R3).",
    )
    parser.add_argument(
        "--resolved-sources",
        help="Path to resolved_sources.json (enables R2 when intake.sources_available != 'none').",
    )
    parser.add_argument(
        "--document-inventory",
        help="Path to document_inventory.json (enables R4 — must pair with --document).",
    )
    parser.add_argument(
        "--document",
        help="Path to the document text (or <document>-wrapped file). Enables R4 paragraph-text substring check.",
    )
    parser.add_argument(
        "--external-evidence",
        dest="external_evidence",
        help="Path to external_evidence.json (enables R5 — ledger probe ↔ verification_path[] consistency).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON result")
    parser.add_argument(
        "--no-enforce-artifacts",
        dest="no_enforce_artifacts",
        action="store_true",
        help=(
            "Force advisory mode regardless of thresholds.ARTIFACT_ENFORCEMENT. "
            "Migration escape hatch for audits started before the required-mode "
            "flip (see references/README_migration.md)."
        ),
    )
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

    artifacts: dict[str, dict[str, Any]] = {}
    for kind, path_arg in [
        ("claim_inventory", args.claim_inventory),
        ("reference_map", args.reference_map),
        ("resolved_sources", args.resolved_sources),
        ("document_inventory", args.document_inventory),
        ("external_evidence", args.external_evidence),
    ]:
        if path_arg:
            p = Path(path_arg)
            if not p.exists():
                print(f"Error: file not found: {p}", file=sys.stderr)
                sys.exit(2)
            artifacts[kind] = json.loads(p.read_text())

    document_text: str | None = None
    if args.document:
        # Normalize using the same rules as parse_document so R4 char-offset
        # lookups align with the document_inventory.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from _text_norm import normalize_text, strip_document_wrapper  # noqa: E402
        raw = Path(args.document).read_text(encoding="utf-8")
        document_text = normalize_text(strip_document_wrapper(raw))

    enforcement: Enforcement = "advisory" if args.no_enforce_artifacts else "auto"
    effective_enforcement = resolve_enforcement(enforcement)

    validator = AuditReportValidator(args.schema)
    ok, errors, warnings = validator.validate(
        report,
        intake,
        artifacts=artifacts,
        document_text=document_text,
        enforcement=enforcement,
    )
    if not _p8_active(intake):
        p8_status = "n/a"
    else:
        p8_status = "pass" if not any(e.startswith("P8:") for e in errors) else "fail"

    r_status = _derive_r_status(errors, warnings)

    if args.json:
        print(
            json.dumps(
                {
                    "valid": ok,
                    "enforcement": effective_enforcement,
                    "p8_status": p8_status,
                    "r_status": r_status,
                    "errors": errors,
                    "warnings": warnings,
                },
                indent=2,
            )
        )
    else:
        tag = "VALID" if ok else "INVALID"
        rs = " ".join(f"{k}:{v}" for k, v in r_status.items())
        print(
            f"{report_path.name}: {tag} (enforcement={effective_enforcement}, "
            f"P8: {p8_status}, {rs})"
        )
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN:  {w}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
