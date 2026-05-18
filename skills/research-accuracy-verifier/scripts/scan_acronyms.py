#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Stage-7 acronym scan: detect undefined-on-first-use and expansion drift.

Heuristics:
  - Acronym = whitespace-bounded UPPERCASE token of length 2-7 (incl. digits, e.g. CDK4)
  - Defined when "Expansion (ACRONYM)" appears, where Expansion has the right
    initial-letter pattern (≥50% of acronym letters covered by Expansion word initials).
  - Reports first occurrence of any acronym with no preceding definition
  - Reports any acronym with two distinct expansions in the same document

Usage:
    uv run python scan_acronyms.py --document doc.md
    uv run python scan_acronyms.py --document doc.md --json
    uv run python scan_acronyms.py --document doc.md --ignore CT26 PD-1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

ACRONYM_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,6})\b")
COMMON_WORDS = {
    "I",
    "A",
    "AN",
    "THE",
    "OR",
    "AND",
    "OF",
    "TO",
    "IN",
    "AT",
    "ON",
    "FOR",
    "BY",
    "AS",
    "IS",
    "BE",
    "IT",
    "WE",
    "US",
    "SO",
    "DO",
    "NO",
    "OK",
}


@dataclass
class AcronymIssue:
    acronym: str
    issue: str  # undefined_first_use | expansion_drift
    location_offset: int | None = None
    detail: str = ""


@dataclass
class ScanResult:
    issues: list[AcronymIssue] = field(default_factory=list)
    expansions: dict[str, list[str]] = field(default_factory=dict)


class AcronymScanner:
    """Scan a document for undefined-first-use and expansion-drift acronym issues."""

    def __init__(self, ignore: set[str] | None = None) -> None:
        self.ignore: set[str] = (ignore or set()) | COMMON_WORDS

    def _looks_like_expansion(self, expansion: str, acronym: str) -> bool:
        words = re.findall(r"\b\w+", expansion)
        if not words:
            return False
        initials = "".join(w[0].upper() for w in words if w and w[0].isalpha())
        # Allow ≥50% letter overlap (loose to handle "CRISPR-Cas9" -> "Clustered Regularly...")
        acro_letters = re.sub(r"[^A-Z]", "", acronym)
        if not acro_letters:
            return False
        matched = sum(1 for c in acro_letters if c in initials)
        return matched / len(acro_letters) >= 0.5

    def scan(self, document: str) -> ScanResult:
        result = ScanResult()
        # First pass: collect definitions in BOTH directions:
        #   (a) "Expansion (ACRONYM)"  — typical first definition
        #   (b) "ACRONYM (Expansion)"  — common in scientific prose
        def_pattern_a = re.compile(
            r"((?:\b[A-Za-z][A-Za-z\-]*\b[\s,]*){1,8}?)\s*\(([A-Z][A-Z0-9]{1,6})\)"
        )
        def_pattern_b = re.compile(
            r"\b([A-Z][A-Z0-9]{1,6})\s*\(((?:[A-Za-z][A-Za-z\-]*\s*){1,8})\)"
        )
        defined_at: dict[str, list[tuple[int, str]]] = {}  # acronym -> [(offset, expansion)]

        for m in def_pattern_a.finditer(document):
            expansion_text = m.group(1).strip().rstrip(",").strip()
            acronym = m.group(2)
            if acronym in self.ignore:
                continue
            if self._looks_like_expansion(expansion_text, acronym):
                defined_at.setdefault(acronym, []).append((m.start(), expansion_text))
                result.expansions.setdefault(acronym, [])
                if expansion_text not in result.expansions[acronym]:
                    result.expansions[acronym].append(expansion_text)

        for m in def_pattern_b.finditer(document):
            acronym = m.group(1)
            expansion_text = m.group(2).strip().rstrip(",").strip()
            if acronym in self.ignore:
                continue
            if self._looks_like_expansion(expansion_text, acronym):
                # Definition is at the acronym's position (it's defined here, not earlier)
                defined_at.setdefault(acronym, []).append((m.start(), expansion_text))
                result.expansions.setdefault(acronym, [])
                if expansion_text not in result.expansions[acronym]:
                    result.expansions[acronym].append(expansion_text)

        # Second pass: walk acronyms in order, flag first-use without prior definition
        seen_first: set[str] = set()
        for m in ACRONYM_RE.finditer(document):
            acronym = m.group(1)
            if acronym in self.ignore or acronym in seen_first:
                continue
            seen_first.add(acronym)
            defs = defined_at.get(acronym, [])
            if not defs or all(off > m.start() for off, _ in defs):
                result.issues.append(
                    AcronymIssue(
                        acronym=acronym,
                        issue="undefined_first_use",
                        location_offset=m.start(),
                        detail=document[max(0, m.start() - 30) : m.start() + 30],
                    )
                )

        # Third pass: expansion drift
        for acronym, expansions in result.expansions.items():
            if len(expansions) > 1:
                result.issues.append(
                    AcronymIssue(
                        acronym=acronym,
                        issue="expansion_drift",
                        detail=f"expansions seen: {expansions}",
                    )
                )
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan document for acronym issues")
    parser.add_argument("--document", required=True)
    parser.add_argument("--ignore", nargs="*", default=[], help="Acronyms to ignore")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    document = Path(args.document).read_text(encoding="utf-8")
    scanner = AcronymScanner(ignore=set(args.ignore))
    result = scanner.scan(document)

    if args.json:
        print(
            json.dumps(
                {
                    "issues": [asdict(i) for i in result.issues],
                    "expansions": result.expansions,
                },
                indent=2,
            )
        )
    else:
        print(f"Acronym issues: {len(result.issues)}")
        for issue in result.issues:
            print(f"  - {issue.acronym}: {issue.issue}")
            if issue.detail:
                print(f"    {issue.detail!r}")
    sys.exit(0 if not result.issues else 1)


if __name__ == "__main__":
    main()
