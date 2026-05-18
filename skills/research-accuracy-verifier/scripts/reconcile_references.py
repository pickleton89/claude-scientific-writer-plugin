#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Stage-7 reference reconciliation: bibliography ↔ inline citation set diff.

Detects:
  - orphan_refs:        bibliography entries with no inline citation
  - orphan_inline:      inline citations with no bibliography entry
  - author_year_mismatches: inline (Smith, 2019) vs. bibliography (Smith, 2020)

Usage:
    uv run python reconcile_references.py --document doc.md --bibliography refs.bib
    uv run python reconcile_references.py --document doc.md --bib-inline '[12] Smith J ...' --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class ReconcileResult:
    orphan_refs: list[str] = field(default_factory=list)
    orphan_inline: list[str] = field(default_factory=list)
    author_year_mismatches: list[dict[str, str]] = field(default_factory=list)


class ReferenceReconciler:
    """Set-diff inline citations against the bibliography."""

    INLINE_PATTERNS = [
        # (Smith, 2019), (Smith et al., 2019), (Smith and Jones, 2019)
        re.compile(r"\(([A-Z][a-zA-Z\-]+(?:\s+et\s+al\.?|\s+and\s+[A-Z][a-zA-Z\-]+)?),\s*(\d{4})[a-z]?\)"),
        # Smith et al. (2019), Smith (2019)
        re.compile(r"\b([A-Z][a-zA-Z\-]+(?:\s+et\s+al\.?|\s+and\s+[A-Z][a-zA-Z\-]+)?)\s+\((\d{4})[a-z]?\)"),
        # Numeric: [12], [12, 14], [12-15]
        re.compile(r"\[(\d+(?:\s*[-,–]\s*\d+)*)\]"),
    ]

    BIBTEX_KEY_PATTERN = re.compile(r"@\w+\s*\{\s*([^,\s}]+)\s*,", re.IGNORECASE)
    BIBTEX_FIRST_AUTHOR_YEAR = re.compile(
        r"@\w+\s*\{\s*([^,\s}]+).*?author\s*=\s*[{\"]([^}\"]+).*?year\s*=\s*[{\"](\d{4})",
        re.IGNORECASE | re.DOTALL,
    )
    NUMBERED_REF_PATTERN = re.compile(r"^\s*(\d+)\.\s+", re.MULTILINE)

    @staticmethod
    def _surname(author_field: str) -> str:
        """Extract surname from BibTeX author field. Handles 'Last, First' and 'First Last'."""
        first_author = re.split(r"\s+and\s+", author_field, maxsplit=1)[0].strip()
        if "," in first_author:
            return first_author.split(",", 1)[0].strip()
        # 'First Last' — take last word
        parts = first_author.split()
        return parts[-1] if parts else first_author

    def parse_inline(self, document: str) -> tuple[set[str], dict[str, str]]:
        """Return (set of citation tokens, map of token -> raw inline text)."""
        tokens: set[str] = set()
        raw: dict[str, str] = {}
        for pat in self.INLINE_PATTERNS:
            for m in pat.finditer(document):
                if pat is self.INLINE_PATTERNS[2]:
                    # numeric — split ranges and lists
                    for tok in self._expand_numeric(m.group(1)):
                        tokens.add(tok)
                        raw.setdefault(tok, m.group(0))
                else:
                    author, year = m.group(1), m.group(2)
                    tok = f"{author.split()[0].lower()}_{year}"
                    tokens.add(tok)
                    raw.setdefault(tok, m.group(0))
        return tokens, raw

    @staticmethod
    def _expand_numeric(s: str) -> list[str]:
        out: list[str] = []
        for part in re.split(r"\s*,\s*", s):
            if "-" in part or "–" in part:
                lo, hi = re.split(r"\s*[-–]\s*", part)
                out.extend(str(i) for i in range(int(lo), int(hi) + 1))
            else:
                out.append(part.strip())
        return out

    def parse_bibliography(self, bib: str) -> dict[str, dict[str, str | set[str]]]:
        """Return map: canonical_key -> {raw_key, surname, year, alt_tokens}.

        canonical_key is the BibTeX cite key (or numbered reference).
        alt_tokens is the set of inline-citation tokens that should match this entry
        (e.g., 'ghost_2024', 'a._2024' if author was 'Ghost, A.').
        """
        entries: dict[str, dict[str, str | set[str]]] = {}

        # BibTeX
        for m in self.BIBTEX_FIRST_AUTHOR_YEAR.finditer(bib):
            key, author, year = m.group(1), m.group(2).strip(), m.group(3)
            surname = self._surname(author)
            alts = {key, f"{surname.lower()}_{year}"}
            entries[key] = {
                "raw_key": key,
                "surname": surname,
                "year": year,
                "alt_tokens": alts,
            }

        # Numbered references in plain text bibliography
        for m in self.NUMBERED_REF_PATTERN.finditer(bib):
            num = m.group(1)
            if num not in entries:
                entries[num] = {
                    "raw_key": num,
                    "surname": "",
                    "year": "",
                    "alt_tokens": {num},
                }

        return entries

    def reconcile(self, document: str, bibliography: str) -> ReconcileResult:
        inline_tokens, inline_raw = self.parse_inline(document)
        entries = self.parse_bibliography(bibliography)

        result = ReconcileResult()

        # orphan_refs: bib entries with no inline token matching any alt
        all_alts: set[str] = set()
        for e in entries.values():
            alts = e["alt_tokens"]
            assert isinstance(alts, set)
            all_alts |= alts
        for key, e in entries.items():
            alts = e["alt_tokens"]
            assert isinstance(alts, set)
            if not (alts & inline_tokens):
                result.orphan_refs.append(key)
        result.orphan_refs.sort()

        # orphan_inline: inline tokens not matching any bib alt
        result.orphan_inline = sorted(inline_tokens - all_alts)

        # Author/year drift: same surname appears with different years inline vs bib
        bib_by_surname: dict[str, set[str]] = {}
        for e in entries.values():
            sur = e["surname"]
            yr = e["year"]
            assert isinstance(sur, str) and isinstance(yr, str)
            if sur:
                bib_by_surname.setdefault(sur.lower(), set()).add(yr)
        for tok in inline_tokens:
            if "_" not in tok or tok in all_alts:
                continue
            surname, year = tok.rsplit("_", 1)
            other_years = bib_by_surname.get(surname, set())
            if other_years and year not in other_years:
                result.author_year_mismatches.append(
                    {
                        "inline": inline_raw.get(tok, tok),
                        "bib_years_for_same_author": ", ".join(sorted(other_years)),
                    }
                )
        return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconcile bibliography against inline citations"
    )
    parser.add_argument("--document", required=True, help="Path to document under audit")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--bibliography", help="Path to .bib or numbered-refs file")
    g.add_argument("--bib-inline", help="Bibliography text inline")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    document = Path(args.document).read_text(encoding="utf-8")
    bib = (
        Path(args.bibliography).read_text(encoding="utf-8")
        if args.bibliography
        else args.bib_inline
    )

    result = ReferenceReconciler().reconcile(document, bib)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(f"Orphan refs (in bib, no inline cite): {len(result.orphan_refs)}")
        for r in result.orphan_refs:
            print(f"  - {r}")
        print(f"Orphan inline (cited, not in bib):    {len(result.orphan_inline)}")
        for r in result.orphan_inline:
            print(f"  - {r}")
        print(f"Author/year mismatches:               {len(result.author_year_mismatches)}")
        for m in result.author_year_mismatches:
            print(f"  - inline {m['inline']} vs bib years {m['bib_years_for_same_author']}")
    issues = (
        len(result.orphan_refs)
        + len(result.orphan_inline)
        + len(result.author_year_mismatches)
    )
    sys.exit(0 if issues == 0 else 1)


if __name__ == "__main__":
    main()
