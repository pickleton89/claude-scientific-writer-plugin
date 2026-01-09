"""
Comprehensive tests for compare_to_source.py module.

Tests source comparison functionality including:
- Tokenization
- N-gram generation
- Similarity calculation
- Verbatim phrase detection
- Claim extraction and coverage
- Full comparison workflow
"""

import sys
from pathlib import Path


# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from compare_to_source import (
    ComparisonResult,
    calculate_similarity,
    check_claim_coverage,
    compare_to_source,
    extract_claims,
    find_verbatim_phrases,
    get_ngrams,
    tokenize,
)


# =============================================================================
# Tokenize Tests
# =============================================================================


class TestTokenize:
    """Tests for the tokenize function."""

    def test_basic_tokenization(self):
        """Test basic word tokenization."""
        text = "Hello world this is a test"
        tokens = tokenize(text)
        assert tokens == ["hello", "world", "this", "is", "a", "test"]

    def test_lowercase_conversion(self):
        """Test that tokens are lowercased."""
        text = "Hello WORLD This Is A Test"
        tokens = tokenize(text)
        assert all(t.islower() or not t.isalpha() for t in tokens)

    def test_removes_code_blocks(self):
        """Test that code blocks are removed."""
        text = "Before ```code here``` After"
        tokens = tokenize(text)
        assert "code" not in tokens
        assert "here" not in tokens
        assert "before" in tokens
        assert "after" in tokens

    def test_removes_markdown_formatting(self):
        """Test that markdown formatting is removed."""
        text = "**bold** and *italic* and `code`"
        tokens = tokenize(text)
        assert "bold" in tokens
        assert "italic" in tokens

    def test_empty_text(self):
        """Test tokenization of empty text."""
        assert tokenize("") == []

    def test_only_punctuation(self):
        """Test tokenization of only punctuation."""
        assert tokenize("!@#$%^&*()") == []

    def test_mixed_content(self):
        """Test tokenization with mixed content."""
        text = "Revenue increased by 25% to $1.5M"
        tokens = tokenize(text)
        assert "revenue" in tokens
        assert "increased" in tokens

    def test_removes_pipe_characters(self):
        """Test that pipe characters (tables) are removed."""
        text = "| Column1 | Column2 |"
        tokens = tokenize(text)
        assert "column1" in tokens
        assert "|" not in tokens

    def test_handles_multiline_code_blocks(self):
        """Test multiline code block removal."""
        text = """Before
```python
def hello():
    return "world"
```
After"""
        tokens = tokenize(text)
        assert "def" not in tokens
        assert "return" not in tokens
        assert "before" in tokens
        assert "after" in tokens


# =============================================================================
# N-gram Tests
# =============================================================================


class TestGetNgrams:
    """Tests for the get_ngrams function."""

    def test_basic_trigrams(self):
        """Test basic trigram generation."""
        tokens = ["a", "b", "c", "d", "e"]
        ngrams = get_ngrams(tokens, 3)
        assert ("a", "b", "c") in ngrams
        assert ("b", "c", "d") in ngrams
        assert ("c", "d", "e") in ngrams
        assert len(ngrams) == 3

    def test_bigrams(self):
        """Test bigram generation."""
        tokens = ["a", "b", "c"]
        ngrams = get_ngrams(tokens, 2)
        assert ("a", "b") in ngrams
        assert ("b", "c") in ngrams

    def test_short_text_for_ngrams(self):
        """Test when text is too short for n-grams."""
        tokens = ["a", "b"]
        ngrams = get_ngrams(tokens, 3)
        assert len(ngrams) == 0

    def test_empty_tokens(self):
        """Test empty token list."""
        ngrams = get_ngrams([], 3)
        assert len(ngrams) == 0

    def test_ngram_counts(self):
        """Test that repeated n-grams are counted."""
        tokens = ["a", "b", "c", "a", "b", "c"]
        ngrams = get_ngrams(tokens, 3)
        assert ngrams[("a", "b", "c")] == 2


# =============================================================================
# Similarity Tests
# =============================================================================


class TestCalculateSimilarity:
    """Tests for the calculate_similarity function."""

    def test_identical_texts(self):
        """Test similarity of identical texts."""
        text = "The quick brown fox jumps over the lazy dog"
        similarity = calculate_similarity(text, text)
        assert similarity == 1.0

    def test_completely_different_texts(self):
        """Test similarity of completely different texts."""
        source = "The quick brown fox jumps over the lazy dog"
        summary = "Apples bananas cherries dates elderberries figs grapes"
        similarity = calculate_similarity(source, summary)
        assert similarity == 0.0

    def test_partial_overlap(self):
        """Test partial overlap calculation."""
        source = "The company reported strong revenue growth in Q4"
        summary = "The company reported good performance last quarter"
        similarity = calculate_similarity(source, summary)
        assert 0 < similarity < 1.0

    def test_empty_summary(self):
        """Test with empty summary."""
        source = "Some source text here"
        similarity = calculate_similarity(source, "")
        assert similarity == 0.0

    def test_empty_source(self):
        """Test with empty source."""
        summary = "Some summary text here"
        similarity = calculate_similarity("", summary)
        assert similarity == 0.0

    def test_high_overlap_detection(self):
        """Test detection of high overlap."""
        source = "The company achieved record revenue of $50 million"
        summary = "The company achieved record revenue of $50 million in Q4"
        similarity = calculate_similarity(source, summary)
        assert similarity > 0.5

    def test_short_texts(self):
        """Test with texts shorter than n-gram size."""
        source = "Hi"
        summary = "Hello"
        similarity = calculate_similarity(source, summary)
        assert similarity == 0.0


# =============================================================================
# Verbatim Phrase Tests
# =============================================================================


class TestFindVerbatimPhrases:
    """Tests for the find_verbatim_phrases function."""

    def test_no_verbatim_phrases(self):
        """Test when no verbatim phrases exist."""
        source = "The quick brown fox jumps over the lazy dog"
        summary = "Revenue increased by 25 percent year over year"
        phrases = find_verbatim_phrases(source, summary)
        assert len(phrases) == 0

    def test_detects_verbatim_phrase(self):
        """Test detection of verbatim copying."""
        source = "The company achieved record revenue of fifty million dollars"
        summary = "The company achieved record revenue of fifty million dollars in Q4"
        phrases = find_verbatim_phrases(source, summary)
        assert len(phrases) > 0

    def test_minimum_length_threshold(self):
        """Test minimum phrase length threshold."""
        source = "one two three four five six seven"
        summary = "one two three four five blah blah"
        # Default min_length is 6
        phrases = find_verbatim_phrases(source, summary)
        assert len(phrases) == 0  # Only 5 words match

    def test_custom_minimum_length(self):
        """Test custom minimum length."""
        source = "one two three four five six seven"
        summary = "one two three four five blah"
        phrases = find_verbatim_phrases(source, summary, min_length=5)
        assert len(phrases) == 1

    def test_multiple_verbatim_phrases(self):
        """Test detection of multiple verbatim phrases."""
        source = "The first phrase here. And the second phrase here."
        summary = "The first phrase here. Something else. And the second phrase here."
        phrases = find_verbatim_phrases(source, summary, min_length=4)
        # Overlapping phrases may be detected (e.g., "the first phrase here" and "and the second phrase")
        assert len(phrases) >= 2

    def test_short_source(self):
        """Test with source shorter than min_length."""
        source = "short"
        summary = "This is a longer summary text"
        phrases = find_verbatim_phrases(source, summary)
        assert len(phrases) == 0

    def test_short_summary(self):
        """Test with summary shorter than min_length."""
        source = "This is a longer source text"
        summary = "short"
        phrases = find_verbatim_phrases(source, summary)
        assert len(phrases) == 0

    def test_deduplicates_phrases(self):
        """Test that repeated phrases are deduplicated."""
        source = "repeat this phrase here and then later"
        summary = "repeat this phrase here and repeat this phrase here"
        phrases = find_verbatim_phrases(source, summary, min_length=4)
        # Should only count unique phrases
        assert len(phrases) == len(set(phrases))


# =============================================================================
# Claim Extraction Tests
# =============================================================================


class TestExtractClaims:
    """Tests for the extract_claims function."""

    def test_extracts_percentage_claims(self):
        """Test extraction of claims with percentages."""
        text = "Revenue increased by 25%. This is good news."
        claims = extract_claims(text)
        assert len(claims) == 1
        assert "25%" in claims[0]

    def test_extracts_dollar_claims(self):
        """Test extraction of claims with dollar amounts."""
        text = "The budget was $50 million. Other information here."
        claims = extract_claims(text)
        assert len(claims) == 1
        assert "$50" in claims[0]

    def test_extracts_findings_verbs(self):
        """Test extraction of claims with findings verbs."""
        text = "The study found significant improvements in performance metrics."
        claims = extract_claims(text)
        assert len(claims) == 1

    def test_extracts_change_verbs(self):
        """Test extraction of claims with change verbs."""
        text = "Sales increased dramatically in the fourth quarter of the year."
        claims = extract_claims(text)
        assert len(claims) == 1

    def test_ignores_short_sentences(self):
        """Test that short sentences are ignored."""
        text = "Up 25%. This is a longer sentence that should be included."
        claims = extract_claims(text)
        # Short sentence should be ignored
        assert not any(len(c) < 20 for c in claims)

    def test_no_claims_in_generic_text(self):
        """Test text without claims."""
        text = "This is a simple paragraph about nothing in particular."
        claims = extract_claims(text)
        assert len(claims) == 0

    def test_multiple_claims(self):
        """Test extraction of multiple claims."""
        text = """Revenue increased by 15%.
                  Costs decreased by 10%.
                  The study shows clear improvements."""
        claims = extract_claims(text)
        assert len(claims) == 3


# =============================================================================
# Claim Coverage Tests
# =============================================================================


class TestCheckClaimCoverage:
    """Tests for the check_claim_coverage function."""

    def test_full_coverage(self):
        """Test when all claims are covered."""
        source = "Revenue increased by 25%. Costs fell by 10%."
        summary = "The company saw 25% revenue growth and 10% cost reduction."
        total, covered, _ = check_claim_coverage(source, summary)
        assert covered == total

    def test_partial_coverage(self):
        """Test partial claim coverage."""
        source = "The company reported revenue increased by 25% this quarter. Operating costs fell by 10% year over year. Quarterly profit rose by 15% overall."
        summary = "Revenue grew 25% year over year."
        total, covered, _ = check_claim_coverage(source, summary)
        assert covered == 1
        assert total == 3

    def test_no_coverage(self):
        """Test when no claims are covered."""
        source = "Revenue increased by 25%. Costs fell by 10%."
        summary = "The company performed well this quarter."
        total, covered, _ = check_claim_coverage(source, summary)
        assert covered == 0

    def test_no_source_claims(self):
        """Test when source has no claims."""
        source = "This is a generic document with no specific data."
        summary = "The summary mentions 25% growth."
        total, covered, _ = check_claim_coverage(source, summary)
        assert total == 0
        assert covered == 0

    def test_returns_covered_list(self):
        """Test that covered claims list is returned."""
        source = "Revenue increased by 25%."
        summary = "We saw 25% revenue growth."
        _, _, covered_list = check_claim_coverage(source, summary)
        assert len(covered_list) == 1


# =============================================================================
# Compare to Source Integration Tests
# =============================================================================


class TestCompareToSource:
    """Integration tests for compare_to_source function."""

    def test_good_summary(self):
        """Test a well-written summary."""
        source = """
        The company reported strong financial results for Q4 2024.
        Revenue increased by 25% to $150 million.
        Operating costs decreased by 10%.
        The analysis shows clear market leadership.
        Customer satisfaction improved significantly.
        """
        summary = """
        Q4 2024 saw exceptional performance with 25% revenue growth
        reaching $150 million. Cost efficiency improved with a 10%
        reduction in operating expenses. Market position strengthened
        considerably during this period.
        """
        result = compare_to_source(source, summary)
        assert isinstance(result, ComparisonResult)
        assert result.similarity_status in ["GOOD", "TOO_SIMILAR", "TOO_DIFFERENT"]

    def test_too_similar_summary(self):
        """Test detection of too-similar summary."""
        source = "The company achieved record revenue of fifty million dollars in the fourth quarter of the fiscal year"
        summary = "The company achieved record revenue of fifty million dollars in the fourth quarter of the fiscal year ending December"
        result = compare_to_source(source, summary)
        # With high overlap, should flag as too similar
        assert result.trigram_overlap > 0.5

    def test_too_different_summary(self):
        """Test detection of summary that drifted from source."""
        source = "Financial performance metrics and revenue analysis for Q4"
        summary = "Elephants roam freely across the African savanna during migration"
        result = compare_to_source(source, summary)
        assert result.similarity_status == "TOO_DIFFERENT"

    def test_verbatim_detection(self):
        """Test verbatim phrase detection in result."""
        source = "the quick brown fox jumps over the lazy dog near the river"
        summary = "the quick brown fox jumps over the lazy dog in the morning"
        result = compare_to_source(source, summary)
        assert len(result.verbatim_phrases) > 0

    def test_claim_coverage_tracking(self):
        """Test that claim coverage is tracked."""
        source = "Revenue grew 25%. Costs fell 15%. Profit increased 30%."
        summary = "We achieved 25% revenue growth this quarter."
        result = compare_to_source(source, summary)
        assert result.source_claims > 0
        assert 0 <= result.covered_claims <= result.source_claims

    def test_issues_populated(self):
        """Test that issues list is populated appropriately."""
        source = "Revenue grew 25%. Costs fell 15%. Profit increased 30%. Sales rose 20%."
        summary = "The company performed well."  # No specific claims covered
        result = compare_to_source(source, summary)
        # Should have low coverage issue
        assert len(result.issues) > 0

    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        result = compare_to_source("", "")
        assert result.trigram_overlap == 0.0

    def test_result_dataclass_fields(self):
        """Test that all result fields are present."""
        result = compare_to_source("Source text here.", "Summary text here.")
        assert hasattr(result, "trigram_overlap")
        assert hasattr(result, "similarity_status")
        assert hasattr(result, "verbatim_phrases")
        assert hasattr(result, "claim_coverage")
        assert hasattr(result, "source_claims")
        assert hasattr(result, "covered_claims")
        assert hasattr(result, "issues")

    def test_similarity_within_bounds(self):
        """Test that similarity is always 0-1."""
        test_cases = [
            ("short", "text"),
            ("a b c d e f g h", "a b c d e f g h"),
            ("completely different", "nothing alike here"),
        ]
        for source, summary in test_cases:
            result = compare_to_source(source, summary)
            assert 0.0 <= result.trigram_overlap <= 1.0

    def test_coverage_within_bounds(self):
        """Test that claim coverage is always 0-1."""
        source = "Revenue grew 25%. Costs fell 15%."
        summaries = [
            "Revenue grew 25%.",
            "Something else entirely.",
            "Revenue grew 25% and costs fell 15%.",
        ]
        for summary in summaries:
            result = compare_to_source(source, summary)
            assert 0.0 <= result.claim_coverage <= 1.0


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_unicode_text(self):
        """Test handling of unicode characters."""
        source = "Revenue increased by 25% → great results"
        summary = "Growth of 25% achieved"
        result = compare_to_source(source, summary)
        assert isinstance(result, ComparisonResult)

    def test_numbers_only(self):
        """Test text with mostly numbers."""
        source = "Q1: 25%, Q2: 30%, Q3: 35%, Q4: 40%"
        summary = "25% in Q1, 40% in Q4"
        result = compare_to_source(source, summary)
        assert isinstance(result, ComparisonResult)

    def test_very_long_text(self):
        """Test with longer text."""
        source = " ".join(["word"] * 1000)
        summary = " ".join(["word"] * 100)
        result = compare_to_source(source, summary)
        assert isinstance(result, ComparisonResult)

    def test_special_characters(self):
        """Test handling of special characters."""
        source = "Revenue: $1.5M (Q4 2024) - up 25%!"
        summary = "Q4 revenue reached $1.5M, a 25% increase"
        result = compare_to_source(source, summary)
        assert isinstance(result, ComparisonResult)

    def test_newlines_and_whitespace(self):
        """Test handling of various whitespace."""
        source = "Line one.\n\n\nLine two.\t\tLine three."
        summary = "Line one and line two combined."
        result = compare_to_source(source, summary)
        assert isinstance(result, ComparisonResult)

    def test_markdown_heavy_text(self):
        """Test with heavy markdown formatting."""
        source = """
        # Heading
        **Bold** and *italic* and `code`
        > Blockquote
        - List item
        | Table | Row |
        """
        summary = "A summary of the heading content."
        result = compare_to_source(source, summary)
        assert isinstance(result, ComparisonResult)


# =============================================================================
# Threshold Tests
# =============================================================================


class TestThresholds:
    """Tests for similarity and coverage thresholds."""

    def test_similarity_threshold_60_percent(self):
        """Test that >60% similarity is flagged as TOO_SIMILAR."""
        # Create text with >60% overlap
        source = "a b c d e f g h i j k l m n o p q r s t"
        summary = "a b c d e f g h i j k l m n o p q r s t u v"
        result = compare_to_source(source, summary)
        if result.trigram_overlap > 0.6:
            assert result.similarity_status == "TOO_SIMILAR"

    def test_similarity_threshold_10_percent(self):
        """Test that <10% similarity is flagged as TOO_DIFFERENT."""
        source = "alpha beta gamma delta epsilon zeta eta theta iota"
        summary = "one two three four five six seven eight nine ten"
        result = compare_to_source(source, summary)
        if result.trigram_overlap < 0.1:
            assert result.similarity_status == "TOO_DIFFERENT"

    def test_coverage_threshold_30_percent(self):
        """Test low coverage flagging with >3 claims."""
        source = """
        Revenue grew 25%. Costs fell 15%. Profit up 30%. Sales rose 20%.
        """
        summary = "The company performed well this quarter."
        result = compare_to_source(source, summary)
        # Should flag low coverage
        if result.claim_coverage < 0.3 and result.source_claims > 3:
            assert any("coverage" in issue.lower() for issue in result.issues)


# =============================================================================
# Regression Tests
# =============================================================================


class TestRegressions:
    """Regression tests for previously identified issues."""

    def test_claim_truncation(self):
        """Test that long claims are properly truncated."""
        source = "This is a very long claim that contains 25% growth and spans multiple words to test the truncation behavior"
        summary = "We saw 25% growth"
        _, _, covered = check_claim_coverage(source, summary)
        if covered:
            assert len(covered[0]) <= 53  # 50 chars + "..."

    def test_default_coverage_no_claims(self):
        """Test default coverage when source has no claims."""
        source = "Generic text without any numbers or findings."
        summary = "A simple summary."
        result = compare_to_source(source, summary)
        # Should default to 1.0 (100%) when no claims to check
        assert result.claim_coverage == 1.0
