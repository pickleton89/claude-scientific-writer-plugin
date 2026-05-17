#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.20",
# ]
# ///
"""Validate deep-research sidecar artifacts (sources / grading / synthesis / advocate).

Two-stage validation per the shared verifier_kit pattern:

  Stage 1: JSON Schema (Draft-07) against schemas/{kind}.json
  Stage 2: Skill-defined predicates (S*, G*, Y*, A*) below.

Predicates by kind:

  sources.json
    S1. Every source.paper_id is unique within sources[].
    S2. Every source has at least one of {doi, pmid} OR source == 'GreyLit' with grey_lit_note.
    S3. search_log[].database appears in sources[].source for at least one entry
        (advisory warning — a database with zero kept sources may indicate over-filtering).
    S4. metadata.frozen_at is a valid ISO-8601 instant (schema enforces format,
        S4 also rejects future timestamps).

  grading.json
    G1. Every grading.paper_id resolves in the referenced sources.json
        (only enforced when sources_path is supplied via CLI / API).
    G2. predatory_flag == true ⟹ predatory_evidence is non-null and non-empty.
    G3. verification_status == 'VERIFIED' ⟹ t_tier is non-null for biomedical
        sources (advisory warning, since some methods/protocol papers legitimately
        lack a T-tier).

  synthesis.json
    Y1. Every theme.supporting_paper_ids[] entry resolves in sources.json
        (when sources_path supplied). Same for gaps[].supporting_paper_ids
        and contradictions[].paper_ids.
    Y2. contradictions[].paper_ids has at least 2 distinct entries (schema enforces
        minItems; Y2 also enforces *distinct*).
    Y3. metadata.mode == 'hypothesis' ⟹ hypotheses[] is non-empty.

  advocate.json
    A1. findings[].id values are unique.
    A2. status != 'open' ⟹ resolution_note is non-null and non-empty.
    A3. (advisory) If any finding has severity == 'CRITICAL' and status == 'open',
        emit a warning that the compiler MUST refuse assembly.
        (Enforcement of refusal lives in output_validator.py, not here.)

Usage:
    uv run python validate_sidecar.py --kind sources --file path/to/sources.json
    uv run python validate_sidecar.py --kind grading --file grading.json --sources sources.json
    uv run python validate_sidecar.py --kind synthesis --file synthesis.json --sources sources.json
    uv run python validate_sidecar.py --kind advocate --file advocate.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Make verifier_kit importable for SchemaValidator reuse.
_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from verifier_kit.validate import SchemaValidator  # noqa: E402

SCHEMA_KINDS = ("sources", "grading", "synthesis", "advocate")


def _load_paper_ids(sources_path: Path) -> set[str]:
    """Load the set of paper_ids from a sources.json. Returns empty set on read failure."""
    try:
        with open(sources_path) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return set()
    return {
        s.get("paper_id")
        for s in (data.get("sources") or [])
        if isinstance(s, dict) and s.get("paper_id")
    }


class SidecarValidator(SchemaValidator):
    """Validate any of the 4 sidecar kinds. Kind selected at construction."""

    def __init__(self, kind: str, schema_path: Path | None = None) -> None:
        if kind not in SCHEMA_KINDS:
            raise ValueError(f"Unknown sidecar kind: {kind!r}. Expected one of {SCHEMA_KINDS}.")
        self.kind = kind
        base = Path(__file__).resolve().parent.parent / "schemas"
        resolved = schema_path if schema_path else base / f"{kind}.json"
        super().__init__(resolved)
        self.schema_path = resolved

    def run_predicates(
        self,
        record: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        **ctx: Any,
    ) -> None:
        if self.kind == "sources":
            self._sources_predicates(record, errors, warnings)
        elif self.kind == "grading":
            self._grading_predicates(record, errors, warnings, ctx.get("known_paper_ids"))
        elif self.kind == "synthesis":
            self._synthesis_predicates(record, errors, warnings, ctx.get("known_paper_ids"))
        elif self.kind == "advocate":
            self._advocate_predicates(record, errors, warnings)

    # ── sources ────────────────────────────────────────────────────────────
    def _sources_predicates(
        self, record: dict[str, Any], errors: list[str], warnings: list[str]
    ) -> None:
        sources = record.get("sources") or []
        search_log = record.get("search_log") or []

        # S1: unique paper_id
        seen: dict[str, int] = {}
        for i, src in enumerate(sources):
            pid = src.get("paper_id")
            if not pid:
                continue
            if pid in seen:
                errors.append(
                    f"S1: duplicate paper_id {pid!r} at sources[{i}] (first seen at sources[{seen[pid]}])"
                )
            else:
                seen[pid] = i

        # S2: identifiers OR grey-lit note
        for i, src in enumerate(sources):
            has_id = bool(src.get("doi") or src.get("pmid") or src.get("pmcid"))
            is_grey = src.get("source") == "GreyLit"
            grey_note = (src.get("grey_lit_note") or "").strip()
            if not has_id and not (is_grey and grey_note):
                errors.append(
                    f"S2: sources[{i}] paper_id={src.get('paper_id')!r} has no doi/pmid/pmcid "
                    "and is not a documented GreyLit entry (source=='GreyLit' AND grey_lit_note set)"
                )

        # S3 (advisory): every database in search_log produced at least one kept source
        log_dbs = {entry.get("database") for entry in search_log if isinstance(entry, dict)}
        source_dbs = {s.get("source") for s in sources if isinstance(s, dict)}
        zero_yield = log_dbs - source_dbs - {None}
        for db in sorted(zero_yield):
            warnings.append(
                f"S3 advisory: database {db!r} appears in search_log but yielded zero kept sources"
            )

        # S4: frozen_at not in the future
        meta = record.get("metadata") or {}
        frozen = meta.get("frozen_at")
        if frozen:
            try:
                ts = datetime.fromisoformat(frozen.replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts > datetime.now(timezone.utc):
                    errors.append(
                        f"S4: metadata.frozen_at {frozen!r} is in the future"
                    )
            except ValueError:
                errors.append(f"S4: metadata.frozen_at {frozen!r} is not a valid ISO-8601 timestamp")

    # ── grading ───────────────────────────────────────────────────────────
    def _grading_predicates(
        self,
        record: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        known_paper_ids: set[str] | None,
    ) -> None:
        gradings = record.get("gradings") or []

        for i, g in enumerate(gradings):
            pid = g.get("paper_id")

            # G1: paper_id resolves in sources.json
            if known_paper_ids is not None and pid and pid not in known_paper_ids:
                errors.append(
                    f"G1: gradings[{i}].paper_id={pid!r} not found in referenced sources.json"
                )

            # G2: predatory_flag ⟹ evidence
            if g.get("predatory_flag") is True:
                ev = (g.get("predatory_evidence") or "").strip()
                if not ev:
                    errors.append(
                        f"G2: gradings[{i}].predatory_flag is true but predatory_evidence is empty"
                    )

            # G3 (advisory): VERIFIED biomedical sources should have a T-tier
            if g.get("verification_status") == "VERIFIED" and g.get("t_tier") is None:
                warnings.append(
                    f"G3 advisory: gradings[{i}] verified but t_tier is null "
                    "(expected for biomedical sources; ignore for methods/protocol papers)"
                )

    # ── synthesis ─────────────────────────────────────────────────────────
    def _synthesis_predicates(
        self,
        record: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        known_paper_ids: set[str] | None,
    ) -> None:
        def _check_ids(path: str, ids: list[str]) -> None:
            if known_paper_ids is None:
                return
            for j, pid in enumerate(ids or []):
                if pid not in known_paper_ids:
                    errors.append(
                        f"Y1: {path}[{j}] paper_id={pid!r} not found in referenced sources.json"
                    )

        for i, theme in enumerate(record.get("themes") or []):
            _check_ids(f"themes[{i}].supporting_paper_ids", theme.get("supporting_paper_ids") or [])

        for i, gap in enumerate(record.get("gaps") or []):
            _check_ids(f"gaps[{i}].supporting_paper_ids", gap.get("supporting_paper_ids") or [])

        for i, c in enumerate(record.get("contradictions") or []):
            ids = c.get("paper_ids") or []
            _check_ids(f"contradictions[{i}].paper_ids", ids)
            # Y2: paper_ids distinct (schema only enforces minItems)
            if len(ids) >= 2 and len(set(ids)) < 2:
                errors.append(
                    f"Y2: contradictions[{i}].paper_ids must have ≥2 *distinct* paper_ids "
                    f"(got {ids!r})"
                )

        # Y3: hypothesis mode requires non-empty hypotheses[]
        meta = record.get("metadata") or {}
        if meta.get("mode") == "hypothesis":
            hyps = record.get("hypotheses") or []
            if not hyps:
                errors.append("Y3: metadata.mode == 'hypothesis' requires hypotheses[] non-empty")

    # ── advocate ──────────────────────────────────────────────────────────
    def _advocate_predicates(
        self, record: dict[str, Any], errors: list[str], warnings: list[str]
    ) -> None:
        findings = record.get("findings") or []

        # A1: unique ids
        seen: dict[str, int] = {}
        for i, f in enumerate(findings):
            fid = f.get("id")
            if not fid:
                continue
            if fid in seen:
                errors.append(
                    f"A1: duplicate finding id {fid!r} at findings[{i}] (first at findings[{seen[fid]}])"
                )
            else:
                seen[fid] = i

        # A2: closed status requires resolution_note
        for i, f in enumerate(findings):
            if f.get("status") in {"addressed", "wont_fix", "deferred"}:
                note = (f.get("resolution_note") or "").strip()
                if not note:
                    errors.append(
                        f"A2: findings[{i}].status={f.get('status')!r} requires non-empty resolution_note"
                    )

        # A3 (advisory): open CRITICALs block the compiler
        open_critical = [
            f for f in findings
            if f.get("severity") == "CRITICAL" and f.get("status") == "open"
        ]
        if open_critical:
            warnings.append(
                f"A3 advisory: {len(open_critical)} open CRITICAL finding(s) present — "
                "compiler MUST refuse assembly until status changes."
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deep-research sidecar JSON")
    parser.add_argument(
        "--kind",
        required=True,
        choices=SCHEMA_KINDS,
        help="Which sidecar schema to validate against",
    )
    parser.add_argument("--file", required=True, help="Path to sidecar JSON")
    parser.add_argument(
        "--sources",
        help="Path to sources.json (required for cross-sidecar paper_id checks in grading/synthesis)",
    )
    parser.add_argument("--schema", help="Override schema path")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    target = Path(args.file)
    if not target.exists():
        print(f"Error: file not found: {target}", file=sys.stderr)
        sys.exit(1)

    try:
        record = json.loads(target.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: {target} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    known_paper_ids: set[str] | None = None
    if args.sources:
        known_paper_ids = _load_paper_ids(Path(args.sources))

    validator = SidecarValidator(args.kind, Path(args.schema) if args.schema else None)
    ok, errors, warnings = validator.validate(record, known_paper_ids=known_paper_ids)

    if args.json:
        print(json.dumps(
            {"kind": args.kind, "file": str(target), "valid": ok, "errors": errors, "warnings": warnings},
            indent=2,
        ))
    else:
        tag = "VALID" if ok else "INVALID"
        print(f"[{args.kind}] {target} {tag}")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN:  {w}")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
