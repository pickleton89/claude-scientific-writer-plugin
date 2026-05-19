#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Extract inline citations + bibliography keys into a reference_map.json.

Stage 1 emits this artifact alongside `claim_inventory.json` and
`document_inventory.json`. Both `paper_id` and identifier fields
(`doi`/`pmid`/`pmcid`) are left null on every citation; Stage 2 fills them
in after identifier resolution succeeds, via
`checkpoint.update_reference_map_paper_ids()`.

The script supports three citation patterns by default (priority order):
  1. Numeric brackets   — `[1]`, `[1,2]`, `[1-3]`
  2. \\cite-style        — `\\cite{Smith2019}`, `\\citep{Smith2019,Jones2020}`
  3. Author-year         — `(Smith, 2019)`, `(Smith et al., 2019)`,
                           `Smith et al. (2019)`

For each match, an occurrence is recorded against the (section_id,
paragraph_id, line) that contains it, using the supplied
`document_inventory.json` as the structural index. Bibliography parsing
is intentionally minimal in Phase 1 — `--bibliography PATH` loads keys
one-per-line (for .bib files, only the `@type{KEY,` header line is
scanned); richer parsers can land in a future phase.

Usage:
    uv run python extract_reference_map.py \\
        --document DOC.md \\
        --inventory document_inventory.json \\
        --slug my-paper \\
        --sources-available bibliography_only \\
        [--bibliography refs.bib] \\
        --output reference_map.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Shared text-normalization utilities. Import-by-path so this script runs
# standalone (CLI usage) regardless of package layout.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _text_norm import normalize_text as _normalize_text  # noqa: E402
from _text_norm import strip_document_wrapper as _strip_wrapper  # noqa: E402

SCHEMA_VERSION = "1.0"

# Citation pattern regexes. Each captures the citation "key" group.
_NUMERIC_BRACKET = re.compile(r"\[(\d+(?:\s*[,\-]\s*\d+)*)\]")
_CITE_COMMAND = re.compile(r"\\cite[a-zA-Z]*\{([^}]+)\}")
# Author-year: matches "(Smith, 2019)", "(Smith et al., 2019)",
# "(Smith and Jones, 2019)", and the comma-less variants
# "(Smith 2019)" / "(Smith et al. 2019)" / "(Smith and Jones 2019)".
# Year is 4 digits. Conservative on the left side — must be inside
# parentheses. The separator between author and year is `,?\s+` —
# comma is optional but at least one whitespace character is required
# to prevent "Smith2024" from matching.
_AUTHOR_YEAR_PAREN = re.compile(
    r"\(([A-Z][A-Za-z\-']+(?:\s+(?:et\s+al\.?|and\s+[A-Z][A-Za-z\-']+))?),?\s+(\d{4})\)"
)
# Narrative form: "Smith et al. (2019)" — Author capitalized, optional "et al",
# year in parens immediately after.
_AUTHOR_YEAR_NARRATIVE = re.compile(
    r"([A-Z][A-Za-z\-']+(?:\s+(?:et\s+al\.?|and\s+[A-Z][A-Za-z\-']+))?)\s+\((\d{4})\)"
)


# _normalize_text and _strip_wrapper are now imported from _text_norm above.


# ---------------------------------------------------------------------------
# Inline-citation sweep
# ---------------------------------------------------------------------------


def _expand_numeric_range(group: str) -> list[str]:
    """Expand '1,2,4-6' → ['1','2','4','5','6']."""
    keys: list[str] = []
    for part in re.split(r"\s*,\s*", group):
        if "-" in part:
            try:
                a, b = part.split("-", 1)
                start, end = int(a.strip()), int(b.strip())
                if start <= end and end - start < 100:  # sanity cap
                    keys.extend(str(i) for i in range(start, end + 1))
                    continue
            except ValueError:
                pass
        keys.append(part.strip())
    return [k for k in keys if k]


def _split_cite_keys(group: str) -> list[str]:
    """Split '\\cite{A,B,C}' inner group → ['A','B','C']."""
    return [k.strip() for k in group.split(",") if k.strip()]


def _find_paragraph_for_offset(
    inventory: dict[str, Any], offset: int
) -> tuple[str | None, str | None]:
    """Return (section_id, paragraph_id) covering the given char offset.
    Linear scan; paragraphs are usually small in count."""
    for p in inventory.get("paragraphs", []) or []:
        if p["char_start"] <= offset < p["char_end"]:
            return p["section_id"], p["id"]
    return None, None


def _line_of_offset(text: str, offset: int) -> int:
    """1-indexed line number containing the given char offset."""
    return text.count("\n", 0, offset) + 1


def sweep_citations(
    normalized_text: str, inventory: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Run all citation regexes over the normalized text.

    Returns a dict keyed by citation key with shape:
        { "raw_text": str, "occurrences": [Occurrence, ...] }

    `raw_text` is "" at sweep-time — bib entries fill it in later.
    Occurrences accumulate across all matches of the same key.
    """
    found: dict[str, dict[str, Any]] = {}

    def _record(key: str, offset: int) -> None:
        if not key:
            return
        section_id, paragraph_id = _find_paragraph_for_offset(inventory, offset)
        if paragraph_id is None:
            return  # citation found in a non-paragraph region (e.g., heading)
        line = _line_of_offset(normalized_text, offset)
        entry = found.setdefault(key, {"raw_text": "", "occurrences": []})
        entry["occurrences"].append(
            {"section_id": section_id, "paragraph_id": paragraph_id, "line": line}
        )

    for m in _NUMERIC_BRACKET.finditer(normalized_text):
        for k in _expand_numeric_range(m.group(1)):
            _record(k, m.start())

    for m in _CITE_COMMAND.finditer(normalized_text):
        for k in _split_cite_keys(m.group(1)):
            _record(k, m.start())

    for m in _AUTHOR_YEAR_PAREN.finditer(normalized_text):
        key = f"{m.group(1).strip()} {m.group(2)}"
        _record(key, m.start())

    for m in _AUTHOR_YEAR_NARRATIVE.finditer(normalized_text):
        key = f"{m.group(1).strip()} {m.group(2)}"
        _record(key, m.start())

    return found


# ---------------------------------------------------------------------------
# Bibliography parsing (Phase 1: minimal)
# ---------------------------------------------------------------------------


_BIB_HEADER = re.compile(r"^\s*@\w+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
_NUMBERED_REF = re.compile(r"^\s*\[?(\d+)\]?\.?\s+(.+)$", re.MULTILINE)


def parse_bibliography(text: str) -> dict[str, str]:
    """Return {citation_key: raw_text} for a bibliography text blob.

    Heuristics (in order):
      1. If text looks like BibTeX (any `@TYPE{KEY,` header), parse those.
      2. Else, parse numbered references `[N] Author...` line per entry.

    raw_text for BibTeX is the full entry body (until matching brace);
    for numbered refs, raw_text is the rest of the line after the number.
    """
    keys: dict[str, str] = {}

    # 1. BibTeX-shaped
    bibtex_hits = list(_BIB_HEADER.finditer(text))
    if bibtex_hits:
        for i, m in enumerate(bibtex_hits):
            key = m.group(1)
            # Capture entry text from header end to next entry's start (or EOF).
            body_start = m.end()
            body_end = bibtex_hits[i + 1].start() if i + 1 < len(bibtex_hits) else len(text)
            keys[key] = text[body_start:body_end].strip()
        return keys

    # 2. Numbered list fallback
    for m in _NUMBERED_REF.finditer(text):
        key = m.group(1)
        body = m.group(2).strip()
        if key not in keys:
            keys[key] = body

    return keys


# ---------------------------------------------------------------------------
# Map assembly
# ---------------------------------------------------------------------------


def build_reference_map(
    document_text: str,
    inventory: dict[str, Any],
    *,
    audit_slug: str,
    sources_available: str,
    bibliography_text: str | None = None,
    frozen_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a reference_map.json record."""
    inner = _strip_wrapper(document_text)
    normalized = _normalize_text(inner)

    occurrences_by_key = sweep_citations(normalized, inventory)
    bib_entries = parse_bibliography(bibliography_text) if bibliography_text else {}

    # Citations = union of (occurrence-found keys) and (bib-entry keys).
    all_keys = sorted(set(occurrences_by_key) | set(bib_entries))

    citations = []
    for key in all_keys:
        entry = occurrences_by_key.get(key, {"raw_text": "", "occurrences": []})
        raw_text = bib_entries.get(key, "") or entry["raw_text"]
        citations.append(
            {
                "key": key,
                "paper_id": None,
                "doi": None,
                "pmid": None,
                "pmcid": None,
                "raw_text": raw_text,
                "occurrences": entry["occurrences"],
            }
        )

    # Orphans = bib entries with zero inline occurrences.
    orphans = sorted(k for k in bib_entries if k not in occurrences_by_key)

    ts = (frozen_at or datetime.now(timezone.utc)).isoformat(timespec="seconds")

    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "frozen_at": ts,
            "audit_slug": audit_slug,
            "sources_available": sources_available,
        },
        "citations": citations,
        "bibliography_orphans": orphans,
    }


# ---------------------------------------------------------------------------
# Mutation helper (Stage 2 fills paper_ids back in)
# ---------------------------------------------------------------------------


def update_paper_ids(
    reference_map: dict[str, Any], mapping: dict[str, dict[str, str | None]]
) -> dict[str, Any]:
    """Patch a reference_map record in place with resolved paper_ids /
    identifiers. `mapping` is keyed by citation key with values like
    {"paper_id": "...", "doi": "...", "pmid": "..."}.

    Citations without a mapping entry are left unchanged. Returns the
    mutated reference_map for convenience.
    """
    for cit in reference_map.get("citations", []) or []:
        update = mapping.get(cit.get("key"))
        if not update:
            continue
        for field_name in ("paper_id", "doi", "pmid", "pmcid"):
            if field_name in update:
                cit[field_name] = update[field_name]
    return reference_map


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract reference_map.json from a document + inventory."
    )
    parser.add_argument("--document", required=True, help="Document file path.")
    parser.add_argument(
        "--inventory",
        required=True,
        help="Path to document_inventory.json (from parse_document.py).",
    )
    parser.add_argument("--slug", required=True)
    parser.add_argument(
        "--sources-available",
        required=True,
        choices=["uploaded_files", "bibliography_only", "none"],
    )
    parser.add_argument(
        "--bibliography",
        help="Optional path to a bibliography text or .bib file.",
    )
    parser.add_argument("--output", help="Output path. Default: stdout.")
    args = parser.parse_args()

    for path_arg, label in [(args.document, "document"), (args.inventory, "inventory")]:
        if not Path(path_arg).exists():
            print(f"Error: {label} not found: {path_arg}", file=sys.stderr)
            sys.exit(1)

    raw = Path(args.document).read_text(encoding="utf-8")
    inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    bib_text = (
        Path(args.bibliography).read_text(encoding="utf-8") if args.bibliography else None
    )

    record = build_reference_map(
        raw,
        inventory,
        audit_slug=args.slug,
        sources_available=args.sources_available,
        bibliography_text=bib_text,
    )

    out = json.dumps(record, indent=2)
    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
