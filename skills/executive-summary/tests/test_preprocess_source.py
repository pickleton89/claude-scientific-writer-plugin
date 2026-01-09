#!/usr/bin/env python3
"""
Unit tests for preprocess_source.py

Tests cover:
- Word counting with markdown exclusion
- Incomplete marker detection (TBD, TODO, PLACEHOLDER, etc.)
- Section structure analysis
- Quantification extraction
- Completeness assessment
- Full preprocessing pipeline
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from preprocess_source import (
    count_words,
    detect_incomplete_markers,
    analyze_sections,
    extract_quantification,
    assess_completeness,
    preprocess_source,
)


# =============================================================================
# count_words tests
# =============================================================================


class TestCountWords:
    """Tests for word counting with markdown exclusion."""

    def test_simple_text(self):
        """Count words in plain text."""
        text = "This is a simple sentence."
        assert count_words(text) == 5

    def test_excludes_markdown_bold(self):
        """Bold markers should not affect word count."""
        text = "This has **five** words here"
        assert count_words(text) == 5

    def test_excludes_markdown_italic(self):
        """Italic markers should not affect word count."""
        text = "This has _five_ words here"
        assert count_words(text) == 5

    def test_excludes_code_blocks(self):
        """Code blocks should be excluded from word count."""
        text = "Two words\n```python\nprint('this should not count')\n```"
        assert count_words(text) == 2

    def test_excludes_inline_code(self):
        """Inline code should be excluded from word count."""
        text = "Use the `command` here"
        assert count_words(text) == 3

    def test_excludes_markdown_links(self):
        """Link URLs should be excluded, link text preserved."""
        text = "Click [here](https://example.com) now"
        assert count_words(text) == 3  # Click, here, now

    def test_excludes_headers(self):
        """Header markers should not affect word count."""
        text = "# Title\n## Section\nTwo words"
        assert count_words(text) == 4  # Title, Section, Two, words

    def test_empty_text(self):
        """Empty text should return 0."""
        assert count_words("") == 0
        assert count_words("   \n\t  ") == 0

    def test_mixed_markdown(self):
        """Complex markdown should be handled."""
        text = """# Report

This **important** document has:
- First item
- Second `code` item

> A blockquote here

[Link](url) to resource."""
        # Count: Report, This, important, document, has, First, item, Second,
        #        item, A, blockquote, here, Link, to, resource
        assert count_words(text) == 15


# =============================================================================
# detect_incomplete_markers tests
# =============================================================================


class TestDetectIncompleteMarkers:
    """Tests for finding incomplete content markers."""

    def test_tbd_marker(self):
        """Detect TBD markers."""
        text = "Section 1\nContent here\n\nSection 2\nTBD"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 1
        assert markers[0]["type"] == "TBD marker"
        assert markers[0]["text"] == "TBD"

    def test_tbc_marker(self):
        """Detect TBC markers."""
        text = "Analysis results: TBC"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 1
        assert markers[0]["type"] == "TBD marker"

    def test_todo_marker(self):
        """Detect TODO markers."""
        text = "First line\nTODO: add content\nLast line"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 1
        assert markers[0]["type"] == "TODO marker"
        assert markers[0]["line"] == 2

    def test_fixme_marker(self):
        """Detect FIXME markers."""
        text = "FIXME: broken section"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 1
        assert markers[0]["type"] == "TODO marker"

    def test_placeholder_text(self):
        """Detect PLACEHOLDER text."""
        text = "Add your PLACEHOLDER here"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 1
        assert markers[0]["type"] == "Placeholder text"

    def test_insert_marker(self):
        """Detect INSERT markers."""
        text = "INSERT graph here"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 1
        assert markers[0]["type"] == "Placeholder text"

    def test_fill_in_marker(self):
        """Detect FILL IN markers."""
        text = "Please FILL IN the details"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 1
        assert markers[0]["type"] == "Placeholder text"

    def test_bracketed_ellipsis(self):
        """Detect bracketed ellipsis placeholders."""
        text = "The results showed [...]"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 1
        assert markers[0]["type"] == "Bracketed ellipsis"

    def test_underscore_placeholder(self):
        """Detect blank line placeholders (underscores)."""
        text = "Name: _____ \nDate: _____"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 2
        assert all(m["type"] == "Blank line placeholder" for m in markers)

    def test_case_insensitive(self):
        """Markers should be case-insensitive."""
        text = "tbd here\nTBD there\nTbd everywhere"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 3

    def test_no_markers(self):
        """Complete document should have no markers."""
        text = "This is a complete document with no placeholders."
        markers = detect_incomplete_markers(text)
        assert len(markers) == 0

    def test_line_numbers_accurate(self):
        """Line numbers should be correct."""
        text = "Line 1\nLine 2\nLine 3 with TBD\nLine 4"
        markers = detect_incomplete_markers(text)
        assert markers[0]["line"] == 3

    def test_multiple_markers(self):
        """Multiple different markers in one document."""
        text = "TBD section\nTODO: fix this\nPLACEHOLDER"
        markers = detect_incomplete_markers(text)
        assert len(markers) == 3


# =============================================================================
# analyze_sections tests
# =============================================================================


class TestAnalyzeSections:
    """Tests for document section structure analysis."""

    def test_h1_count(self):
        """Count H1 headers."""
        text = "# Title\n## Section\n# Another Title"
        sections = analyze_sections(text)
        assert sections["h1_count"] == 2

    def test_h2_count(self):
        """Count H2 headers."""
        text = "# Title\n## Section 1\n## Section 2\n### Subsection"
        sections = analyze_sections(text)
        assert sections["h2_count"] == 2

    def test_h3_count(self):
        """Count H3 headers."""
        text = "### Sub 1\n### Sub 2\n### Sub 3"
        sections = analyze_sections(text)
        assert sections["h3_count"] == 3

    def test_total_sections(self):
        """Total sections should sum all header levels."""
        text = "# H1\n## H2\n### H3"
        sections = analyze_sections(text)
        assert sections["total_sections"] == 3

    def test_empty_sections_detected(self):
        """Detect empty sections (header with no content before next header)."""
        text = "## Section 1\n\n## Section 2\nContent here"
        sections = analyze_sections(text)
        assert sections["empty_sections"] == 1

    def test_no_empty_sections(self):
        """Document with content in all sections."""
        text = "## Section 1\nContent 1\n\n## Section 2\nContent 2"
        sections = analyze_sections(text)
        assert sections["empty_sections"] == 0

    def test_no_headers(self):
        """Document with no headers."""
        text = "Just plain text without any headers."
        sections = analyze_sections(text)
        assert sections["total_sections"] == 0

    def test_header_requires_space(self):
        """Headers require space after #."""
        text = "#NoSpace\n# With Space"
        sections = analyze_sections(text)
        assert sections["h1_count"] == 1


# =============================================================================
# extract_quantification tests
# =============================================================================


class TestExtractQuantification:
    """Tests for extracting quantified values from text."""

    def test_percentages(self):
        """Extract percentage values."""
        text = "Improved by 45% over baseline."
        quantities = extract_quantification(text)
        assert "45%" in quantities

    def test_dollar_amounts(self):
        """Extract dollar amounts."""
        text = "Cost savings of $50,000 per year."
        quantities = extract_quantification(text)
        assert "$50,000" in quantities

    def test_dollar_with_suffix(self):
        """Extract dollar amounts with K/M/B suffix."""
        text = "Revenue of $5M expected."
        quantities = extract_quantification(text)
        assert "$5M" in quantities

    def test_decimals(self):
        """Extract decimal values."""
        text = "Error rate reduced to 0.05"
        quantities = extract_quantification(text)
        assert "0.05" in quantities

    def test_large_numbers(self):
        """Extract large numbers."""
        text = "Serving 50000 customers daily."
        quantities = extract_quantification(text)
        assert "50000" in quantities

    def test_formatted_numbers(self):
        """Extract comma-formatted numbers."""
        text = "Population of 1,234,567 people."
        quantities = extract_quantification(text)
        assert "1,234,567" in quantities

    def test_multiple_quantities(self):
        """Extract multiple different quantities."""
        text = "Achieved 30% growth with $2M investment, serving 5000 users."
        quantities = extract_quantification(text)
        assert len(quantities) >= 3

    def test_no_duplicates(self):
        """Repeated values should be deduplicated."""
        text = "50% here and 50% there"
        quantities = extract_quantification(text)
        assert quantities.count("50%") == 1

    def test_no_quantities(self):
        """Text without quantities."""
        text = "A qualitative analysis of the situation."
        quantities = extract_quantification(text)
        assert len(quantities) == 0


# =============================================================================
# assess_completeness tests
# =============================================================================


class TestAssessCompleteness:
    """Tests for document completeness assessment."""

    def test_ready_document(self):
        """Complete document should be READY."""
        text = "A " * 600  # 600 words
        result = assess_completeness(text, [], {"empty_sections": 0})
        assert result["status"] == "READY"
        assert result["score"] >= 80

    def test_incomplete_with_markers(self):
        """Document with markers should be penalized."""
        text = "A " * 600
        markers = [{"type": "TBD", "text": "TBD", "line": 1}]
        result = assess_completeness(text, markers, {"empty_sections": 0})
        assert result["score"] < 100
        assert "1 incomplete marker(s) found" in result["issues"]

    def test_incomplete_with_empty_sections(self):
        """Document with empty sections should be penalized."""
        text = "A " * 600
        result = assess_completeness(text, [], {"empty_sections": 2})
        assert result["score"] < 100
        assert "2 empty section(s)" in result["issues"]

    def test_short_document_warning(self):
        """Very short documents should be flagged."""
        text = "Short " * 50  # 50 words
        result = assess_completeness(text, [], {"empty_sections": 0})
        assert "Document very short (<500 words)" in result["issues"]

    def test_warn_status(self):
        """Score 50-79 should be WARN."""
        text = "A " * 600
        markers = [{"type": "TBD", "text": "TBD", "line": i} for i in range(2)]
        result = assess_completeness(text, markers, {"empty_sections": 0})
        assert result["status"] in ["WARN", "INCOMPLETE"]

    def test_incomplete_status(self):
        """Score below 50 should be INCOMPLETE."""
        text = "A " * 600
        markers = [{"type": "TBD", "text": "TBD", "line": i} for i in range(5)]
        result = assess_completeness(text, markers, {"empty_sections": 0})
        assert result["status"] == "INCOMPLETE"
        assert result["score"] <= 0

    def test_score_never_negative(self):
        """Score should be clamped at 0."""
        text = "A " * 600
        markers = [{"type": "TBD", "text": "TBD", "line": i} for i in range(10)]
        result = assess_completeness(text, markers, {"empty_sections": 5})
        assert result["score"] >= 0


# =============================================================================
# preprocess_source (integration) tests
# =============================================================================


class TestPreprocessSource:
    """Integration tests for full preprocessing pipeline."""

    def test_complete_document(self):
        """Process a complete document."""
        text = """# Analysis Report

## Introduction

This report analyzes performance improvements of 45% achieved through
optimization efforts. The project cost $50,000 and delivered significant
value to 5000 users across the organization.

## Methods

We conducted a comprehensive analysis using standard methodologies.

## Results

Key findings show 30% improvement in efficiency.

## Conclusion

The project was successful in achieving its goals.
"""
        result = preprocess_source(text)

        assert result["word_count"] > 0
        assert result["recommended_summary_length"] > 0
        assert result["max_summary_length"] > result["recommended_summary_length"]
        assert result["completeness"]["status"] in ["READY", "WARN"]
        assert result["quantification_count"] > 0

    def test_incomplete_document(self):
        """Process an incomplete document with markers."""
        text = """# Draft Report

## Section 1

Some content here.

## Section 2

TBD - need to add analysis

## Section 3

TODO: add conclusion
"""
        result = preprocess_source(text)

        assert len(result["incomplete_markers"]) >= 2
        assert result["completeness"]["status"] in ["WARN", "INCOMPLETE"]

    def test_recommended_lengths(self):
        """Recommended and max lengths should be correct ratios."""
        text = "word " * 1000  # 1000 words
        result = preprocess_source(text)

        assert result["recommended_summary_length"] == 100  # 10%
        assert result["max_summary_length"] == 150  # 15%

    def test_sections_tracked(self):
        """Section structure should be tracked."""
        text = """# Title
## Section 1
### Subsection 1.1
## Section 2
"""
        result = preprocess_source(text)

        assert result["sections"]["h1_count"] == 1
        assert result["sections"]["h2_count"] == 2
        assert result["sections"]["h3_count"] == 1

    def test_quantification_extraction(self):
        """Quantification should be extracted and counted."""
        text = "We achieved 50% improvement with $100K investment."
        result = preprocess_source(text)

        assert result["quantification_count"] >= 2
        assert "50%" in result["quantification_found"]


# =============================================================================
# Edge cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_unicode_content(self):
        """Handle unicode content."""
        text = "Revenue increased by 50% in Q4. Caf\u00e9 sales were strong."
        result = preprocess_source(text)
        assert result["word_count"] > 0

    def test_very_long_document(self):
        """Handle very long documents."""
        text = "word " * 50000  # 50,000 words
        result = preprocess_source(text)
        assert result["word_count"] == 50000
        assert result["recommended_summary_length"] == 5000

    def test_only_code_blocks(self):
        """Document with only code blocks."""
        text = "```python\nprint('hello')\n```"
        result = preprocess_source(text)
        assert result["word_count"] == 0

    def test_nested_markdown(self):
        """Handle nested markdown formatting."""
        text = "This is **_bold italic_** text with `code` inside."
        count = count_words(text)
        assert count == 7  # This, is, bold, italic, text, with, inside


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
