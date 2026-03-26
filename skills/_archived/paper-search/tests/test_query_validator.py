#!/usr/bin/env python3
"""
Unit tests for query_validator.py

Tests query syntax validation for different database sources.
"""

import sys
from pathlib import Path
import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from query_validator import (
    validate_pubmed_query,
    validate_semantic_query,
    validate_biorxiv_query,
    validate_query,
    validate_for_all_sources,
    check_pubmed_publication_type,
    format_validation_report,
    ValidationResult,
    PUBMED_VALID_FIELDS,
    PUBMED_PUBLICATION_TYPES,
)


class TestValidatePubMedQuery:
    """Tests for PubMed query validation."""

    # Valid queries
    def test_simple_query(self):
        """Test simple valid query."""
        result = validate_pubmed_query("CRISPR gene therapy")
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_with_field_tags(self):
        """Test query with valid field tags."""
        result = validate_pubmed_query("CRISPR[Title] AND gene[Abstract]")
        assert result.is_valid is True

    def test_with_boolean(self):
        """Test query with boolean operators."""
        result = validate_pubmed_query("CRISPR AND therapy AND cancer")
        assert result.is_valid is True

    def test_with_date_range(self):
        """Test query with date range."""
        result = validate_pubmed_query("CRISPR AND 2020:2024[Publication Date]")
        assert result.is_valid is True

    def test_with_publication_type(self):
        """Test query with publication type."""
        result = validate_pubmed_query("cancer AND Review[Publication Type]")
        assert result.is_valid is True

    # Invalid queries - brackets
    def test_unbalanced_brackets(self):
        """Test detection of unbalanced brackets."""
        result = validate_pubmed_query("CRISPR[Title AND therapy")
        assert result.is_valid is False
        assert any("bracket" in e.lower() for e in result.errors)

    def test_unbalanced_parentheses(self):
        """Test detection of unbalanced parentheses."""
        result = validate_pubmed_query("(CRISPR AND therapy")
        assert result.is_valid is False
        assert any("parenthes" in e.lower() for e in result.errors)

    def test_unbalanced_quotes(self):
        """Test detection of unbalanced quotes."""
        result = validate_pubmed_query('"CRISPR gene therapy')
        assert result.is_valid is False
        assert any("quote" in e.lower() for e in result.errors)

    # Invalid queries - boolean
    def test_empty_and_clause(self):
        """Test detection of empty AND clause."""
        result = validate_pubmed_query("CRISPR AND AND therapy")
        assert result.is_valid is False
        assert any("empty" in e.lower() for e in result.errors)

    def test_empty_or_clause(self):
        """Test detection of empty OR clause."""
        result = validate_pubmed_query("CRISPR OR OR therapy")
        assert result.is_valid is False

    def test_starts_with_and(self):
        """Test detection of query starting with AND."""
        result = validate_pubmed_query("AND CRISPR therapy")
        assert result.is_valid is False

    def test_ends_with_or(self):
        """Test detection of query ending with OR."""
        result = validate_pubmed_query("CRISPR therapy OR")
        assert result.is_valid is False

    # Warnings
    def test_lowercase_boolean_warning(self):
        """Test warning for lowercase boolean operators."""
        result = validate_pubmed_query("CRISPR and therapy")
        assert len(result.warnings) > 0
        assert any("lowercase" in w.lower() or "uppercase" in w.lower()
                   for w in result.warnings)

    def test_unknown_field_warning(self):
        """Test warning for unknown field tag."""
        result = validate_pubmed_query("CRISPR[UnknownField]")
        assert len(result.warnings) > 0

    def test_very_short_query_warning(self):
        """Test warning for very short query."""
        result = validate_pubmed_query("cancer")
        assert len(result.warnings) > 0
        assert any("short" in w.lower() for w in result.warnings)

    # Suggestions
    def test_review_suggestion(self):
        """Test suggestion for review searches."""
        result = validate_pubmed_query("cancer review treatment")
        assert len(result.suggestions) > 0
        assert any("Review[Publication Type]" in s for s in result.suggestions)

    def test_date_suggestion(self):
        """Test suggestion for date filtering."""
        result = validate_pubmed_query("cancer 2020")
        assert len(result.suggestions) > 0
        assert any("Publication Date" in s for s in result.suggestions)

    # Date range validation
    def test_invalid_date_range_order(self):
        """Test detection of invalid date range order."""
        result = validate_pubmed_query("cancer AND 2024:2020[Publication Date]")
        assert result.is_valid is False
        assert any("date" in e.lower() and "range" in e.lower() for e in result.errors)

    def test_future_date_warning(self):
        """Test warning for future end date."""
        result = validate_pubmed_query("cancer AND 2020:2050[Publication Date]")
        assert len(result.warnings) > 0
        assert any("future" in w.lower() for w in result.warnings)

    # Empty query
    def test_empty_query(self):
        """Test rejection of empty query."""
        result = validate_pubmed_query("")
        assert result.is_valid is False
        assert any("empty" in e.lower() for e in result.errors)

    def test_whitespace_query(self):
        """Test rejection of whitespace-only query."""
        result = validate_pubmed_query("   ")
        assert result.is_valid is False


class TestValidateSemanticQuery:
    """Tests for Semantic Scholar query validation."""

    def test_simple_query(self):
        """Test simple valid query."""
        result = validate_semantic_query("machine learning biology")
        assert result.is_valid is True

    def test_quoted_phrase(self):
        """Test query with quoted phrase."""
        result = validate_semantic_query('"deep learning" protein')
        assert result.is_valid is True

    def test_unbalanced_quotes(self):
        """Test detection of unbalanced quotes."""
        result = validate_semantic_query('"deep learning protein')
        assert result.is_valid is False

    def test_field_tag_warning(self):
        """Test warning for PubMed-style field tags."""
        result = validate_semantic_query("CRISPR[Title]")
        assert len(result.warnings) > 0
        assert any("field" in w.lower() or "pubmed" in w.lower() for w in result.warnings)

    def test_short_query_warning(self):
        """Test warning for very short query."""
        result = validate_semantic_query("ML")
        assert len(result.warnings) > 0

    def test_empty_query(self):
        """Test rejection of empty query."""
        result = validate_semantic_query("")
        assert result.is_valid is False


class TestValidateBioRxivQuery:
    """Tests for bioRxiv query validation."""

    def test_simple_query(self):
        """Test simple valid query."""
        result = validate_biorxiv_query("protein folding AlphaFold")
        assert result.is_valid is True

    def test_unbalanced_quotes(self):
        """Test detection of unbalanced quotes."""
        result = validate_biorxiv_query('"protein folding')
        assert result.is_valid is False

    def test_not_operator_warning(self):
        """Test warning for NOT operator."""
        result = validate_biorxiv_query("CRISPR NOT review")
        assert len(result.warnings) > 0
        assert any("NOT" in w for w in result.warnings)

    def test_field_tag_warning(self):
        """Test warning for field tags."""
        result = validate_biorxiv_query("cancer[Title]")
        assert len(result.warnings) > 0

    def test_empty_query(self):
        """Test rejection of empty query."""
        result = validate_biorxiv_query("")
        assert result.is_valid is False


class TestValidateQuery:
    """Tests for unified validate_query function."""

    def test_pubmed_source(self):
        """Test validation routes to PubMed validator."""
        result = validate_query("CRISPR[Title]", "pubmed")
        assert result.is_valid is True

    def test_semantic_source(self):
        """Test validation routes to Semantic validator."""
        result = validate_query("machine learning", "semantic")
        assert result.is_valid is True

    def test_biorxiv_source(self):
        """Test validation routes to bioRxiv validator."""
        result = validate_query("protein folding", "biorxiv")
        assert result.is_valid is True

    def test_medrxiv_source(self):
        """Test medrxiv uses bioRxiv validator."""
        result = validate_query("clinical trial", "medrxiv")
        assert result.is_valid is True

    def test_scholar_source(self):
        """Test Google Scholar uses Semantic validator."""
        result = validate_query("research topic", "scholar")
        assert result.is_valid is True

    def test_unknown_source(self):
        """Test unknown source returns warning."""
        result = validate_query("test query", "unknown_db")
        assert result.is_valid is True  # Permissive for unknown
        assert len(result.warnings) > 0


class TestValidateForAllSources:
    """Tests for multi-source validation."""

    def test_validate_all_sources(self):
        """Test validation across multiple sources."""
        results = validate_for_all_sources(
            "CRISPR gene therapy",
            ["pubmed", "semantic", "biorxiv"]
        )
        assert len(results) == 3
        assert "pubmed" in results
        assert "semantic" in results
        assert "biorxiv" in results

    def test_source_specific_issues(self):
        """Test that issues are source-specific."""
        # PubMed field tags will cause warning in Semantic
        results = validate_for_all_sources(
            "CRISPR[Title]",
            ["pubmed", "semantic"]
        )
        # Valid for PubMed
        assert results["pubmed"].is_valid is True
        # Warning for Semantic
        assert len(results["semantic"].warnings) > 0


class TestPublicationTypeValidation:
    """Tests for publication type validation."""

    def test_valid_publication_type(self):
        """Test valid publication type."""
        is_valid, suggestion = check_pubmed_publication_type("Review")
        assert is_valid is True
        assert suggestion is None

    def test_case_sensitivity(self):
        """Test case sensitivity suggestion."""
        is_valid, suggestion = check_pubmed_publication_type("review")
        assert is_valid is True
        assert suggestion is not None
        assert "Review" in suggestion

    def test_common_typo(self):
        """Test common typo suggestion."""
        is_valid, suggestion = check_pubmed_publication_type("reviews")
        assert is_valid is False
        assert suggestion is not None
        assert "Review" in suggestion

    def test_unknown_type(self):
        """Test unknown publication type."""
        is_valid, suggestion = check_pubmed_publication_type("UnknownType")
        assert is_valid is False
        assert suggestion is None


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_valid_result(self):
        """Test creating valid result."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["minor issue"],
            suggestions=["try this"]
        )
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert len(result.suggestions) == 1

    def test_invalid_result(self):
        """Test creating invalid result."""
        result = ValidationResult(
            is_valid=False,
            errors=["critical error"]
        )
        assert result.is_valid is False
        assert len(result.errors) == 1


class TestFormatValidationReport:
    """Tests for report formatting."""

    def test_format_valid(self):
        """Test formatting valid result."""
        result = ValidationResult(is_valid=True)
        report = format_validation_report(result)
        assert "PASSED" in report

    def test_format_invalid(self):
        """Test formatting invalid result."""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"]
        )
        report = format_validation_report(result)
        assert "FAILED" in report
        assert "Error 1" in report
        assert "Error 2" in report

    def test_format_with_warnings(self):
        """Test formatting with warnings."""
        result = ValidationResult(
            is_valid=True,
            warnings=["Warning 1"]
        )
        report = format_validation_report(result)
        assert "Warning" in report

    def test_format_verbose(self):
        """Test verbose formatting includes suggestions."""
        result = ValidationResult(
            is_valid=True,
            suggestions=["Suggestion 1"]
        )
        report = format_validation_report(result, verbose=True)
        assert "Suggestion" in report

    def test_format_non_verbose(self):
        """Test non-verbose omits suggestions."""
        result = ValidationResult(
            is_valid=True,
            suggestions=["Suggestion 1"]
        )
        report = format_validation_report(result, verbose=False)
        assert "Suggestion" not in report


class TestPubMedFieldTags:
    """Tests for PubMed field tag coverage."""

    def test_common_fields_valid(self):
        """Test that common field tags are recognized."""
        common_fields = ["Author", "Title", "Abstract", "Journal", "MeSH Terms"]
        for field in common_fields:
            assert field in PUBMED_VALID_FIELDS

    def test_date_fields_valid(self):
        """Test that date fields are recognized."""
        date_fields = ["Publication Date", "DP"]
        for field in date_fields:
            assert field in PUBMED_VALID_FIELDS

    def test_abbreviations_valid(self):
        """Test that common abbreviations are recognized."""
        abbrevs = ["AU", "TI", "AB", "TA", "MH"]
        for abbrev in abbrevs:
            assert abbrev in PUBMED_VALID_FIELDS


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_query_same_result(self):
        """Test that same query produces same validation result."""
        query = "CRISPR[Title] AND gene therapy"
        result1 = validate_pubmed_query(query)
        result2 = validate_pubmed_query(query)

        assert result1.is_valid == result2.is_valid
        assert result1.errors == result2.errors
        assert result1.warnings == result2.warnings

    def test_consistent_across_runs(self):
        """Test consistency across multiple invocations."""
        query = "machine learning protein prediction"
        results = [validate_semantic_query(query) for _ in range(10)]

        assert all(r.is_valid == results[0].is_valid for r in results)
        assert all(r.errors == results[0].errors for r in results)


class TestEdgeCases:
    """Tests for edge cases."""

    def test_very_long_query(self):
        """Test handling of very long query."""
        # Create a query over 2000 chars to trigger length warning
        long_query = " AND ".join(["term"] * 500)
        result = validate_pubmed_query(long_query)
        assert result.is_valid is True  # Syntactically valid
        assert len(result.warnings) > 0  # Should warn about length

    def test_special_characters(self):
        """Test query with special characters."""
        result = validate_pubmed_query("BRCA1/2 gene p53 (tumor suppressor)")
        assert result.is_valid is True

    def test_unicode_characters(self):
        """Test query with unicode characters."""
        result = validate_pubmed_query("Müller cell retina")
        assert result.is_valid is True

    def test_nested_parentheses(self):
        """Test query with nested parentheses."""
        result = validate_pubmed_query("((A OR B) AND (C OR D))")
        assert result.is_valid is True

    def test_complex_boolean(self):
        """Test complex boolean expression."""
        result = validate_pubmed_query(
            "(CRISPR OR TALEN) AND (gene therapy OR gene editing) NOT review"
        )
        assert result.is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
