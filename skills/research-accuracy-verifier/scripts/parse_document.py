#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Baseline document parser for the <document> wrapper text.

Stage 1 emits a `document_inventory.json` artifact via this script. The
script produces the deterministic baseline (sections + paragraphs +
char/line offsets + SHA-256). The LLM may append entries to the
`overrides[]` array to correct parser errors without editing the baseline
arrays. Downstream stages read sections/paragraphs through
`resolve_location()` which applies overrides on top of the baseline.

Parser rules:
  - Newlines normalized to LF; trailing whitespace stripped per line.
  - Unicode normalized to NFC.
  - Paragraphs split on runs of ≥1 blank line.
  - Section headings detected in priority order:
      1. Markdown heading:     ^#{1,6} TEXT$
      2. Explicit marker:      ^\\[Section: TEXT\\]$
      3. Plaintext heading:    ALL-CAPS standalone line (≥3 chars,
                               letters/spaces/digits/punct only, no
                               sentence-ending period) — level 1.
  - Pre-heading content gets a synthetic "Preamble" section at level 1.
  - Empty sections (no paragraphs) are omitted.

Usage:
    uv run python parse_document.py --document DOC.txt --slug my-paper \\
        --output document_inventory.json
    uv run python parse_document.py --document DOC.txt --slug my-paper \\
        --document-type manuscript --json   # prints to stdout
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Shared text-normalization utilities. Import-by-path so this script runs
# standalone (CLI usage) regardless of package layout.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _text_norm import normalize_text, strip_document_wrapper  # noqa: E402,F401

PARSER_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0"

_HEADING_MD = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_HEADING_EXPLICIT = re.compile(r"^\[Section:\s*(.+?)\]\s*$")
# Plaintext heading: 3-80 chars, no lowercase letters, contains at least one letter,
# does not end with a period (avoids matching sentences in ALL CAPS).
_HEADING_PLAINTEXT = re.compile(
    r"^(?=.*[A-Z])[A-Z0-9 \-:,&/()]{3,80}$"
)


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Heading detection
# ---------------------------------------------------------------------------


@dataclass
class HeadingHit:
    name: str
    level: int


def detect_heading(line: str) -> HeadingHit | None:
    """Return a HeadingHit when the given line is a section heading, else None.

    Priority: markdown > explicit > plaintext. None on blank or content lines.
    """
    if not line.strip():
        return None
    m = _HEADING_MD.match(line)
    if m:
        return HeadingHit(name=m.group(2).strip(), level=len(m.group(1)))
    m = _HEADING_EXPLICIT.match(line)
    if m:
        return HeadingHit(name=m.group(1).strip(), level=1)
    # Plaintext heading is a stricter fallback to avoid false positives on prose.
    stripped = line.strip()
    if (
        stripped
        and not stripped.endswith(".")
        and _HEADING_PLAINTEXT.match(stripped)
        # extra guard: must contain at least one alpha (skip "123-456")
        and any(c.isalpha() for c in stripped)
    ):
        return HeadingHit(name=stripped, level=1)
    return None


# ---------------------------------------------------------------------------
# Walker
# ---------------------------------------------------------------------------


@dataclass
class _Paragraph:
    id: str
    section_id: str
    ordinal: int
    char_start: int
    char_end: int
    line_start: int
    line_end: int


@dataclass
class _Section:
    id: str
    name: str
    level: int
    char_start: int
    char_end: int
    paragraph_ids: list[str] = field(default_factory=list)


def parse(normalized_text: str) -> tuple[list[_Section], list[_Paragraph]]:
    """Walk normalized text and produce baseline sections + paragraphs.

    The walker is one-pass and emits IDs sequentially. Pre-heading content
    accumulates into a synthetic 'Preamble' section that is only emitted
    if it ends up holding any paragraphs.
    """
    sections: list[_Section] = []
    paragraphs: list[_Paragraph] = []

    section_counter = 0
    paragraph_counter = 0

    def _new_section(name: str, level: int, char_start: int) -> _Section:
        nonlocal section_counter
        section_counter += 1
        return _Section(
            id=f"S{section_counter:03d}",
            name=name,
            level=level,
            char_start=char_start,
            char_end=char_start,  # patched at section close
        )

    def _new_paragraph(
        section: _Section, ordinal: int, char_start: int, line_start: int
    ) -> _Paragraph:
        nonlocal paragraph_counter
        paragraph_counter += 1
        pid = f"P{paragraph_counter:03d}"
        section.paragraph_ids.append(pid)
        return _Paragraph(
            id=pid,
            section_id=section.id,
            ordinal=ordinal,
            char_start=char_start,
            char_end=char_start,
            line_start=line_start,
            line_end=line_start,
        )

    # Defer Preamble creation until pre-heading content actually arrives,
    # so the ID counter doesn't skip a slot when there's no preamble.
    current_section: _Section | None = None
    paragraph_ordinal_in_section = 0
    current_paragraph: _Paragraph | None = None

    cursor = 0  # absolute char offset
    line_no = 1
    lines = normalized_text.split("\n")
    # `split` with a trailing newline yields a final '' which we want to skip.
    if lines and lines[-1] == "":
        lines.pop()

    for raw_line in lines:
        line_len = len(raw_line) + 1  # +1 for the LF we re-add when computing offsets
        line_start_char = cursor
        line_end_char = cursor + len(raw_line)  # exclusive char range of the visible chars
        is_blank = (raw_line.strip() == "")

        heading = detect_heading(raw_line) if not is_blank else None

        if heading is not None:
            # Close current paragraph, if any.
            if current_paragraph is not None:
                paragraphs.append(current_paragraph)
                current_paragraph = None

            # Close current section (if one was open).
            if current_section is not None:
                current_section.char_end = line_start_char
                if current_section.paragraph_ids:
                    sections.append(current_section)
                # else: drop empty section (e.g. consecutive headings)

            # Open new section.
            current_section = _new_section(heading.name, heading.level, line_start_char)
            paragraph_ordinal_in_section = 0
            # Heading line itself is NOT a paragraph.
        elif is_blank:
            # End the current paragraph (if any) on a blank line.
            if current_paragraph is not None:
                paragraphs.append(current_paragraph)
                current_paragraph = None
        else:
            # Content line — extend or open a paragraph.
            if current_section is None:
                # Pre-heading content; materialize a Preamble section now.
                current_section = _new_section("Preamble", 1, char_start=line_start_char)
                paragraph_ordinal_in_section = 0
            if current_paragraph is None:
                paragraph_ordinal_in_section += 1
                current_paragraph = _new_paragraph(
                    current_section,
                    paragraph_ordinal_in_section,
                    char_start=line_start_char,
                    line_start=line_no,
                )
            current_paragraph.char_end = line_end_char
            current_paragraph.line_end = line_no

        cursor += line_len
        line_no += 1

    # Flush final paragraph + section.
    if current_paragraph is not None:
        paragraphs.append(current_paragraph)
    if current_section is not None and current_section.paragraph_ids:
        last_pid = current_section.paragraph_ids[-1]
        last_para = next(p for p in paragraphs if p.id == last_pid)
        current_section.char_end = last_para.char_end
        sections.append(current_section)

    return sections, paragraphs


# ---------------------------------------------------------------------------
# Inventory assembly
# ---------------------------------------------------------------------------


def build_inventory(
    document_text: str,
    *,
    audit_slug: str,
    document_type: str | None = None,
    frozen_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a document_inventory.json record.

    Strips the <document>...</document> wrapper if present, normalizes
    line endings/whitespace/unicode, computes SHA-256, and walks the
    normalized text for sections/paragraphs.
    """
    inner = strip_document_wrapper(document_text)
    normalized = normalize_text(inner)
    digest = sha256_hex(normalized)
    sections, paragraphs = parse(normalized)
    ts = (frozen_at or datetime.now(timezone.utc)).isoformat(timespec="seconds")

    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "frozen_at": ts,
            "source_sha256": digest,
            "audit_slug": audit_slug,
            "document_type": document_type,
            "parser_version": PARSER_VERSION,
        },
        "sections": [
            {
                "id": s.id,
                "name": s.name,
                "level": s.level,
                "char_start": s.char_start,
                "char_end": s.char_end,
                "paragraph_ids": list(s.paragraph_ids),
            }
            for s in sections
        ],
        "paragraphs": [
            {
                "id": p.id,
                "section_id": p.section_id,
                "ordinal": p.ordinal,
                "char_start": p.char_start,
                "char_end": p.char_end,
                "line_start": p.line_start,
                "line_end": p.line_end,
            }
            for p in paragraphs
        ],
        "overrides": [],
    }


# ---------------------------------------------------------------------------
# Override resolution (for downstream consumers)
# ---------------------------------------------------------------------------


_PATH_RE = re.compile(r"^(sections|paragraphs)\[(\d+)\](?:\.(\w+))?$")


def resolve_location(
    inventory: dict[str, Any], *, section_id: str, paragraph_id: str
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Resolve a (section_id, paragraph_id) pair to the override-applied
    section + paragraph records. Returns (section, paragraph) — either may
    be None if the IDs don't resolve.

    Override application is shallow: each override's `path` of the form
    `sections[N].name` (etc.) is parsed and applied to a deep copy of the
    addressed section/paragraph. Unknown paths are silently skipped (D3
    catches them at validate-time).
    """
    # Deep copy minimal slice — only the addressed records get override edits.
    section = next(
        (s for s in inventory.get("sections", []) if s.get("id") == section_id), None
    )
    paragraph = next(
        (p for p in inventory.get("paragraphs", []) if p.get("id") == paragraph_id),
        None,
    )
    section = dict(section) if section else None
    paragraph = dict(paragraph) if paragraph else None

    for ov in inventory.get("overrides", []) or []:
        m = _PATH_RE.match(ov.get("path", ""))
        if not m:
            continue
        coll, idx_str, field_name = m.group(1), m.group(2), m.group(3)
        idx = int(idx_str)
        target_list = inventory.get(coll) or []
        if not (0 <= idx < len(target_list)):
            continue
        target = target_list[idx]
        if coll == "sections" and section and target.get("id") == section.get("id"):
            if field_name:
                section[field_name] = ov.get("after")
            else:
                section = {**section, **(ov.get("after") or {})}
        elif coll == "paragraphs" and paragraph and target.get("id") == paragraph.get("id"):
            if field_name:
                paragraph[field_name] = ov.get("after")
            else:
                paragraph = {**paragraph, **(ov.get("after") or {})}

    return section, paragraph


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse a <document> wrapper file into document_inventory.json"
    )
    parser.add_argument(
        "--document",
        required=True,
        help="Path to a file containing the document text (with or without <document> wrapper).",
    )
    parser.add_argument("--slug", required=True, help="Audit slug.")
    parser.add_argument(
        "--document-type",
        default=None,
        choices=[
            "grant",
            "manuscript",
            "lit_review",
            "slides",
            "report",
            "memo",
            "other",
        ],
    )
    parser.add_argument(
        "--output",
        help="Path to write document_inventory.json. Default: print to stdout.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="When --output is set, also echo the JSON to stdout (otherwise stdout only carries 'wrote PATH').",
    )
    args = parser.parse_args()

    doc_path = Path(args.document)
    if not doc_path.exists():
        print(f"Error: document not found: {doc_path}", file=sys.stderr)
        sys.exit(1)
    raw = doc_path.read_text(encoding="utf-8")

    inventory = build_inventory(
        raw,
        audit_slug=args.slug,
        document_type=args.document_type,
    )

    out = json.dumps(inventory, indent=2)
    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
        if args.json:
            print(out)
    else:
        print(out)


if __name__ == "__main__":
    main()
