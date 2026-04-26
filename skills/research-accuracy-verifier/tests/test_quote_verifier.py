"""Tests for verify_exact_quote.py — exact, normalized, partial, fabricated."""

from __future__ import annotations


from verify_exact_quote import QuoteVerifier


class TestQuoteVerifier:
    def setup_method(self) -> None:
        self.v = QuoteVerifier()

    def test_exact_match(self) -> None:
        r = self.v.match("the result was significant", "We found the result was significant.")
        assert r.verdict == "QUOTE_VERIFIED"
        assert r.matched_form == "exact"
        assert r.overlap_ratio == 1.0
        assert r.span is not None

    def test_whitespace_normalized_match(self) -> None:
        # Quote uses single spaces; source has double spaces and a newline
        r = self.v.match(
            "the result was significant after correction",
            "We found  the   result\nwas significant   after correction.",
        )
        assert r.verdict == "QUOTE_VERIFIED"
        assert r.matched_form in {"whitespace_normalized", "unicode_normalized"}

    def test_unicode_smart_quotes_normalized(self) -> None:
        # Source has curly quotes and non-breaking space
        r = self.v.match(
            "it's a 'significant' result",
            "We argue it’s a ‘significant’ result indeed.",
        )
        assert r.verdict == "QUOTE_VERIFIED"
        assert r.matched_form == "unicode_normalized"

    def test_paraphrase_overlap(self) -> None:
        # 5 of 6 words present out of order — over the 0.6 threshold
        r = self.v.match(
            "the result was statistically significant",
            "the statistically significant result was reported in Figure 2.",
        )
        assert r.verdict == "QUOTE_PARAPHRASED"
        assert 0.6 <= r.overlap_ratio <= 1.0

    def test_fabricated_no_overlap(self) -> None:
        r = self.v.match(
            "quantum entanglement explains protein folding",
            "Cells contain mitochondria. The Krebs cycle is well documented.",
        )
        assert r.verdict == "QUOTE_FABRICATED"
        assert r.overlap_ratio < 0.6

    def test_empty_quote_returns_fabricated(self) -> None:
        r = self.v.match("!!!", "Some source text.")
        assert r.verdict == "QUOTE_FABRICATED"

    def test_span_indexes_into_normalized_source(self) -> None:
        source = "Lorem ipsum the result was significant dolor sit amet"
        r = self.v.match("the result was significant", source)
        assert r.span is not None
        start, end = r.span
        assert source[start:end] == "the result was significant"
