#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.20",
# ]
# ///
"""Validate research-accuracy-verifier pinned artifacts.

Multi-kind validator mirroring `skills/deep-research/scripts/validate_sidecar.py`.
Two-stage continue-on-failure pattern via `verifier_kit.SchemaValidator`:

  Stage 1: JSON Schema (Draft-07) against schemas/<kind>.json
  Stage 2: Per-artifact predicates (D*, M*, S*, V*) below.

Predicates by kind:

  document_inventory.json
    D1. Paragraph ordinals are contiguous within each section starting at 1.
    D2. Char ranges within paragraphs[] are non-overlapping (and within sections[]).
    D3. Every overrides[].path parses and addresses an existing element.
    D4. Every paragraphs[].section_id resolves in sections[]; every
        sections[].paragraph_ids[] entry resolves in paragraphs[] with matching
        section_id.

  reference_map.json
    M1. Every citations[].key is unique.
    M2. When non-null, citations[].doi matches DOI pattern; pmid is digits;
        pmcid matches '^PMC\\d+$'; paper_id is non-empty string.
    M3. Every bibliography_orphans[] entry corresponds to a citations[] entry
        with empty occurrences[] (and a non-empty raw_text).

  resolved_sources.json
    S1. Every sources[].paper_id is unique.
    S2. Every source has at least one of {doi, pmid, pmcid}. (No grey-lit
        carve-out in the verifier — the document under audit produces the
        citations, and a non-identifiable cite-without-paper would have been
        UNSUPPORTED at Stage 2, not added to resolved_sources.)
    S4. metadata.frozen_at not in the future.
    V1. Every resolution_paths[].fetched_at is parseable ISO-8601 and not in
        the future.
    V2. (advisory) At least one resolution_paths[].outcome != 'UNVERIFIED'
        per source. A source with only UNVERIFIED attempts should be a
        finding, not a resolved entry.

  external_evidence.json
    E1. Every entries[].id is unique.
    E2. Every entries[].query_hash is a well-formed lowercase 64-char SHA-256
        hex string.
    E3. (advisory) Every entries[].fetched_at is parseable ISO-8601, not in
        the future, and entries[] is sorted ascending by fetched_at.

Usage:
    uv run python validate_artifact.py --kind document_inventory --file PATH
    uv run python validate_artifact.py --kind reference_map --file PATH --json
    uv run python validate_artifact.py --kind resolved_sources --file PATH
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Make verifier_kit importable.
_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from verifier_kit.validate import SchemaValidator  # noqa: E402

# Local thresholds (for ARTIFACT_KINDS).
sys.path.insert(0, str(Path(__file__).parent))
from thresholds import ARTIFACT_KINDS  # noqa: E402

KIND_TO_SCHEMA = {
    "document_inventory": "document_inventory.json",
    "reference_map": "reference_map.json",
    "resolved_sources": "resolved_sources.json",
    "external_evidence": "external_evidence.json",
}

_DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
_PMID_RE = re.compile(r"^\d{1,9}$")
_PMCID_RE = re.compile(r"^PMC\d+$", re.IGNORECASE)
_OVERRIDE_PATH_RE = re.compile(r"^(sections|paragraphs)\[(\d+)\](?:\.(\w+))?$")
_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def _parse_iso8601(s: str) -> datetime | None:
    try:
        # Python's fromisoformat handles "+00:00" but not "Z" prior to 3.11.
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


class ArtifactValidator(SchemaValidator):
    """Validate any of the verifier's pinned artifacts. Kind selected at construction."""

    def __init__(self, kind: str, schema_path: Path | None = None) -> None:
        if kind not in ARTIFACT_KINDS:
            raise ValueError(
                f"Unknown artifact kind: {kind!r}. Expected one of {ARTIFACT_KINDS}."
            )
        self.kind = kind
        base = Path(__file__).resolve().parent.parent / "schemas"
        resolved = schema_path if schema_path else base / KIND_TO_SCHEMA[kind]
        if not resolved.exists():
            raise FileNotFoundError(
                f"Schema not found for kind={kind!r}: {resolved}"
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
        if self.kind == "document_inventory":
            self._document_inventory_predicates(record, errors, warnings)
        elif self.kind == "reference_map":
            self._reference_map_predicates(record, errors, warnings)
        elif self.kind == "resolved_sources":
            self._resolved_sources_predicates(record, errors, warnings)
        elif self.kind == "external_evidence":
            self._external_evidence_predicates(record, errors, warnings)

    # ── document_inventory ────────────────────────────────────────────────
    def _document_inventory_predicates(
        self, record: dict[str, Any], errors: list[str], warnings: list[str]
    ) -> None:
        sections = record.get("sections") or []
        paragraphs = record.get("paragraphs") or []
        section_index = {s.get("id"): s for s in sections if isinstance(s, dict)}
        paragraph_index = {p.get("id"): p for p in paragraphs if isinstance(p, dict)}

        # D1: ordinals contiguous within each section starting at 1.
        by_section: dict[str, list[int]] = {}
        for p in paragraphs:
            sid = p.get("section_id")
            ord_ = p.get("ordinal")
            if sid is not None and isinstance(ord_, int):
                by_section.setdefault(sid, []).append(ord_)
        for sid, ords in by_section.items():
            sorted_ords = sorted(ords)
            expected = list(range(1, len(sorted_ords) + 1))
            if sorted_ords != expected:
                errors.append(
                    f"D1: section {sid!r} paragraph ordinals {sorted_ords} are not "
                    f"contiguous from 1 (expected {expected})"
                )

        # D2: paragraph char ranges non-overlapping (assuming sorted by char_start).
        sorted_paragraphs = sorted(
            (p for p in paragraphs if isinstance(p.get("char_start"), int)),
            key=lambda x: x["char_start"],
        )
        for i in range(1, len(sorted_paragraphs)):
            prev, curr = sorted_paragraphs[i - 1], sorted_paragraphs[i]
            if curr["char_start"] < prev.get("char_end", -1):
                errors.append(
                    f"D2: paragraph {curr.get('id')!r} char_start={curr['char_start']} "
                    f"overlaps prior {prev.get('id')!r} (char_end={prev.get('char_end')})"
                )

        # D3: every override.path parses + addresses existing element.
        for i, ov in enumerate(record.get("overrides") or []):
            path = ov.get("path", "")
            m = _OVERRIDE_PATH_RE.match(path)
            if not m:
                errors.append(
                    f"D3: overrides[{i}].path={path!r} does not parse "
                    f"(expected 'sections[N]' or 'sections[N].field' / 'paragraphs[N]' / 'paragraphs[N].field')"
                )
                continue
            coll, idx_str, field_name = m.group(1), m.group(2), m.group(3)
            idx = int(idx_str)
            target_list = sections if coll == "sections" else paragraphs
            if not (0 <= idx < len(target_list)):
                errors.append(
                    f"D3: overrides[{i}].path={path!r} index {idx} out of range "
                    f"(have {len(target_list)} {coll})"
                )
                continue
            if field_name and field_name not in target_list[idx]:
                # `after` should add a new field — only warn rather than error.
                warnings.append(
                    f"D3 advisory: overrides[{i}].path={path!r} addresses a field "
                    f"{field_name!r} that is not present in the baseline "
                    f"{coll}[{idx}] — verify this isn't a typo"
                )

        # D4: cross-reference between sections.paragraph_ids and paragraphs.section_id.
        for p in paragraphs:
            sid = p.get("section_id")
            if sid not in section_index:
                errors.append(
                    f"D4: paragraph {p.get('id')!r} section_id={sid!r} not found in sections[]"
                )
        for s in sections:
            sid = s.get("id")
            for pid in s.get("paragraph_ids") or []:
                p = paragraph_index.get(pid)
                if p is None:
                    errors.append(
                        f"D4: section {sid!r} references paragraph_id {pid!r} not in paragraphs[]"
                    )
                elif p.get("section_id") != sid:
                    errors.append(
                        f"D4: section {sid!r} claims paragraph {pid!r} but paragraph.section_id={p.get('section_id')!r}"
                    )

    # ── reference_map ─────────────────────────────────────────────────────
    def _reference_map_predicates(
        self, record: dict[str, Any], errors: list[str], warnings: list[str]
    ) -> None:
        citations = record.get("citations") or []
        orphans = record.get("bibliography_orphans") or []

        # M1: unique keys.
        seen: dict[str, int] = {}
        for i, c in enumerate(citations):
            k = c.get("key")
            if not k:
                continue
            if k in seen:
                errors.append(
                    f"M1: duplicate citation key {k!r} at citations[{i}] "
                    f"(first at citations[{seen[k]}])"
                )
            else:
                seen[k] = i

        # M2: identifier shapes when non-null.
        for i, c in enumerate(citations):
            doi = c.get("doi")
            pmid = c.get("pmid")
            pmcid = c.get("pmcid")
            paper_id = c.get("paper_id")
            if doi is not None and not _DOI_RE.match(doi):
                errors.append(
                    f"M2: citations[{i}].doi={doi!r} does not match DOI pattern (10.NNNN/...)"
                )
            if pmid is not None and not _PMID_RE.match(pmid):
                errors.append(
                    f"M2: citations[{i}].pmid={pmid!r} is not 1-9 digits"
                )
            if pmcid is not None and not _PMCID_RE.match(pmcid):
                errors.append(
                    f"M2: citations[{i}].pmcid={pmcid!r} does not match '^PMC\\d+$'"
                )
            if paper_id is not None and not (isinstance(paper_id, str) and paper_id):
                errors.append(
                    f"M2: citations[{i}].paper_id={paper_id!r} must be a non-empty string when non-null"
                )

        # M3: orphans correspond to citations with empty occurrences AND non-empty raw_text.
        cit_by_key = {c.get("key"): c for c in citations if c.get("key")}
        for k in orphans:
            cit = cit_by_key.get(k)
            if cit is None:
                errors.append(
                    f"M3: bibliography_orphans[] key {k!r} has no matching citations[] entry"
                )
                continue
            if cit.get("occurrences"):
                errors.append(
                    f"M3: orphan key {k!r} has non-empty occurrences[] "
                    f"({len(cit['occurrences'])} entries) — not an orphan"
                )
            if not (cit.get("raw_text") or "").strip():
                warnings.append(
                    f"M3 advisory: orphan key {k!r} has empty raw_text — "
                    f"may indicate a parser miss rather than a true orphan"
                )

        # Symmetric advisory: any citation with raw_text + empty occurrences should
        # ideally appear in orphans[].
        orphan_set = set(orphans)
        for c in citations:
            k = c.get("key")
            if (
                (c.get("raw_text") or "").strip()
                and not c.get("occurrences")
                and k not in orphan_set
            ):
                warnings.append(
                    f"M3 advisory: citation {k!r} has bib raw_text + no occurrences "
                    f"but is not listed in bibliography_orphans[]"
                )

    # ── resolved_sources ──────────────────────────────────────────────────
    def _resolved_sources_predicates(
        self, record: dict[str, Any], errors: list[str], warnings: list[str]
    ) -> None:
        sources = record.get("sources") or []

        # S1: unique paper_id.
        seen: dict[str, int] = {}
        for i, s in enumerate(sources):
            pid = s.get("paper_id")
            if not pid:
                continue
            if pid in seen:
                errors.append(
                    f"S1: duplicate paper_id {pid!r} at sources[{i}] "
                    f"(first at sources[{seen[pid]}])"
                )
            else:
                seen[pid] = i

        # S2: at least one identifier.
        for i, s in enumerate(sources):
            if not (s.get("doi") or s.get("pmid") or s.get("pmcid")):
                errors.append(
                    f"S2: sources[{i}] paper_id={s.get('paper_id')!r} has no doi/pmid/pmcid"
                )

        # S4: metadata.frozen_at not in future.
        meta = record.get("metadata") or {}
        frozen = meta.get("frozen_at")
        if frozen:
            ts = _parse_iso8601(frozen)
            if ts is None:
                errors.append(f"S4: metadata.frozen_at {frozen!r} is not parseable ISO-8601")
            else:
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts > datetime.now(timezone.utc):
                    errors.append(f"S4: metadata.frozen_at {frozen!r} is in the future")

        # V1: every resolution_paths[].fetched_at parseable + not in future.
        # V2: at least one outcome != UNVERIFIED per source.
        now = datetime.now(timezone.utc)
        for i, s in enumerate(sources):
            outcomes: list[str] = []
            for j, rp in enumerate(s.get("resolution_paths") or []):
                fa = rp.get("fetched_at")
                if fa:
                    ts = _parse_iso8601(fa)
                    if ts is None:
                        errors.append(
                            f"V1: sources[{i}].resolution_paths[{j}].fetched_at "
                            f"{fa!r} is not parseable ISO-8601"
                        )
                    else:
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                        if ts > now:
                            errors.append(
                                f"V1: sources[{i}].resolution_paths[{j}].fetched_at "
                                f"{fa!r} is in the future"
                            )
                if isinstance(rp.get("outcome"), str):
                    outcomes.append(rp["outcome"])
            if outcomes and all(o == "UNVERIFIED" for o in outcomes):
                warnings.append(
                    f"V2 advisory: sources[{i}] paper_id={s.get('paper_id')!r} has only "
                    f"UNVERIFIED resolution_paths — should this be a finding, not a "
                    f"resolved source?"
                )

    # ── external_evidence ────────────────────────────────────────────────
    def _external_evidence_predicates(
        self, record: dict[str, Any], errors: list[str], warnings: list[str]
    ) -> None:
        entries = record.get("entries") or []

        # E1: unique entry ids.
        seen: dict[str, int] = {}
        for i, e in enumerate(entries):
            eid = e.get("id")
            if not eid:
                continue
            if eid in seen:
                errors.append(
                    f"E1: duplicate entries[].id {eid!r} at entries[{i}] "
                    f"(first at entries[{seen[eid]}])"
                )
            else:
                seen[eid] = i

        # E2: query_hash well-formed SHA-256 hex.
        for i, e in enumerate(entries):
            qh = e.get("query_hash")
            if qh is None:
                continue
            if not (isinstance(qh, str) and _SHA256_HEX_RE.match(qh)):
                errors.append(
                    f"E2: entries[{i}].query_hash={qh!r} is not a 64-char "
                    f"lowercase SHA-256 hex string"
                )

        # E3: fetched_at parseable + not in future; entries sorted ascending
        # by fetched_at (advisory).
        now = datetime.now(timezone.utc)
        prev_ts: datetime | None = None
        unsorted_flagged = False
        for i, e in enumerate(entries):
            fa = e.get("fetched_at")
            if not fa:
                continue
            ts = _parse_iso8601(fa)
            if ts is None:
                errors.append(
                    f"E3: entries[{i}].fetched_at={fa!r} is not parseable ISO-8601"
                )
                continue
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts > now:
                errors.append(
                    f"E3: entries[{i}].fetched_at={fa!r} is in the future"
                )
            if prev_ts is not None and ts < prev_ts and not unsorted_flagged:
                warnings.append(
                    f"E3 advisory: entries[{i}].fetched_at={fa!r} is earlier "
                    f"than the prior entry — ledger should be append-only and "
                    f"chronological"
                )
                unsorted_flagged = True
            prev_ts = ts


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def validate_artifact(
    kind: str, path: Path | str, schema_path: Path | None = None
) -> tuple[bool, list[str], list[str]]:
    """Validate a single artifact file by kind. Library wrapper around the
    CLI's per-kind validator construction; used by `checkpoint.finalize_audit`
    to gate the audit's full artifact set before render. Raises FileNotFoundError
    if the file is absent so callers can distinguish missing from invalid.
    """
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"artifact not found: {target}")
    record = json.loads(target.read_text(encoding="utf-8"))
    validator = ArtifactValidator(kind, schema_path)
    return validator.validate(record)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a research-accuracy-verifier pinned artifact"
    )
    parser.add_argument(
        "--kind",
        required=True,
        choices=ARTIFACT_KINDS,
        help="Artifact kind to validate against",
    )
    parser.add_argument("--file", required=True, help="Path to artifact JSON")
    parser.add_argument("--schema", help="Override schema path")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    target = Path(args.file)
    if not target.exists():
        print(f"Error: file not found: {target}", file=sys.stderr)
        sys.exit(1)

    try:
        record = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: {target} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        validator = ArtifactValidator(
            args.kind, Path(args.schema) if args.schema else None
        )
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    ok, errors, warnings = validator.validate(record)

    if args.json:
        print(
            json.dumps(
                {
                    "kind": args.kind,
                    "file": str(target),
                    "valid": ok,
                    "errors": errors,
                    "warnings": warnings,
                },
                indent=2,
            )
        )
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
