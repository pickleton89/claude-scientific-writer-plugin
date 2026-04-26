#!/usr/bin/env python3
"""Stage-5 quote verification: exact-string + whitespace-normalized match.

Pure deterministic check. Returns one of QUOTE_VERIFIED / QUOTE_PARAPHRASED /
QUOTE_FABRICATED based on string match in source text.

Usage:
    uv run python verify_exact_quote.py --quote "the result was significant" --source-file paper.txt
    uv run python verify_exact_quote.py --quote "..." --source-text "..." --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path

# Heuristic threshold for QUOTE_PARAPHRASED vs QUOTE_FABRICATED:
# fraction of words from the quote that appear contiguously in source.
PARAPHRASE_OVERLAP_THRESHOLD = 0.6


@dataclass
class MatchResult:
    verdict: str  # QUOTE_VERIFIED | QUOTE_PARAPHRASED | QUOTE_FABRICATED
    span: tuple[int, int] | None
    matched_form: str  # exact | whitespace_normalized | unicode_normalized | partial | none
    overlap_ratio: float


class QuoteVerifier:
    """Match a quoted passage against source text under progressively looser normalizations."""

    @staticmethod
    def _normalize_whitespace(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    @staticmethod
    def _normalize_unicode(s: str) -> str:
        # Collapse smart quotes / curly apostrophes / non-breaking spaces.
        s = unicodedata.normalize("NFKC", s)
        return (
            s.replace("‘", "'")
            .replace("’", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace(" ", " ")
        )

    def match(self, quote: str, source_text: str) -> MatchResult:
        # Tier 1: exact substring
        idx = source_text.find(quote)
        if idx != -1:
            return MatchResult("QUOTE_VERIFIED", (idx, idx + len(quote)), "exact", 1.0)

        # Tier 2: whitespace-normalized
        q_ws = self._normalize_whitespace(quote)
        s_ws = self._normalize_whitespace(source_text)
        idx = s_ws.find(q_ws)
        if idx != -1:
            return MatchResult(
                "QUOTE_VERIFIED", (idx, idx + len(q_ws)), "whitespace_normalized", 1.0
            )

        # Tier 3: unicode + whitespace normalized
        q_u = self._normalize_whitespace(self._normalize_unicode(quote))
        s_u = self._normalize_whitespace(self._normalize_unicode(source_text))
        idx = s_u.find(q_u)
        if idx != -1:
            return MatchResult(
                "QUOTE_VERIFIED", (idx, idx + len(q_u)), "unicode_normalized", 1.0
            )

        # Tier 4: word-overlap heuristic
        quote_words = re.findall(r"\w+", q_u.lower())
        source_words = re.findall(r"\w+", s_u.lower())
        if not quote_words:
            return MatchResult("QUOTE_FABRICATED", None, "none", 0.0)
        source_set = set(source_words)
        overlap = sum(1 for w in quote_words if w in source_set) / len(quote_words)
        if overlap >= PARAPHRASE_OVERLAP_THRESHOLD:
            return MatchResult("QUOTE_PARAPHRASED", None, "partial", round(overlap, 3))
        return MatchResult("QUOTE_FABRICATED", None, "none", round(overlap, 3))


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a quoted passage against source text")
    parser.add_argument("--quote", required=True, help="Quoted passage to verify")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--source-file", help="Path to source text file")
    g.add_argument("--source-text", help="Source text inline")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.source_file:
        source_text = Path(args.source_file).read_text(encoding="utf-8")
    else:
        source_text = args.source_text

    result = QuoteVerifier().match(args.quote, source_text)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(f"Verdict:        {result.verdict}")
        print(f"Matched form:   {result.matched_form}")
        print(f"Overlap ratio:  {result.overlap_ratio}")
        if result.span:
            print(f"Span:           {result.span}")
    # Exit 0 for VERIFIED, 1 for PARAPHRASED, 2 for FABRICATED
    sys.exit({"QUOTE_VERIFIED": 0, "QUOTE_PARAPHRASED": 1, "QUOTE_FABRICATED": 2}[result.verdict])


if __name__ == "__main__":
    main()
