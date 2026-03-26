"""
Tests for Result Validation Module.

Phase 3 Implementation - Determinism Audit
"""

import sys
from pathlib import Path

import pytest

# Import from scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from result_validator import (
    ResultQualityMetrics,
    ResultStatus,
    ResultThresholds,
    SearchFeedback,
    ValidationReport,
    analyze_result_count,
    analyze_result_quality,
    get_quality_summary,
    validate_search_results,
)


# ============================================================================
# SearchFeedback Tests
# ============================================================================


class TestSearchFeedback:
    """Tests for SearchFeedback dataclass."""

    def test_search_feedback_creation(self):
        """Test creating SearchFeedback instance."""
        feedback = SearchFeedback(
            result_count=10,
            status=ResultStatus.GOOD,
            suggestions=["Test suggestion"],
            warnings=["Test warning"],
            query_quality_score=0.8,
        )
        assert feedback.result_count == 10
        assert feedback.status == ResultStatus.GOOD
        assert len(feedback.suggestions) == 1
        assert len(feedback.warnings) == 1
        assert feedback.query_quality_score == 0.8

    def test_is_acceptable_good(self):
        """Test is_acceptable returns True for GOOD status."""
        feedback = SearchFeedback(result_count=10, status=ResultStatus.GOOD)
        assert feedback.is_acceptable() is True

    def test_is_acceptable_exhaustive(self):
        """Test is_acceptable returns True for EXHAUSTIVE status."""
        feedback = SearchFeedback(result_count=50, status=ResultStatus.EXHAUSTIVE)
        assert feedback.is_acceptable() is True

    def test_is_acceptable_too_few(self):
        """Test is_acceptable returns False for TOO_FEW status."""
        feedback = SearchFeedback(result_count=2, status=ResultStatus.TOO_FEW)
        assert feedback.is_acceptable() is False

    def test_needs_refinement(self):
        """Test needs_refinement for various statuses."""
        assert SearchFeedback(0, ResultStatus.NONE).needs_refinement() is True
        assert SearchFeedback(2, ResultStatus.TOO_FEW).needs_refinement() is True
        assert SearchFeedback(10, ResultStatus.GOOD).needs_refinement() is False

    def test_needs_narrowing(self):
        """Test needs_narrowing for various statuses."""
        assert SearchFeedback(100, ResultStatus.TOO_MANY).needs_narrowing() is True
        assert SearchFeedback(10, ResultStatus.GOOD).needs_narrowing() is False

    def test_to_dict(self):
        """Test converting feedback to dictionary."""
        feedback = SearchFeedback(
            result_count=10,
            status=ResultStatus.GOOD,
            suggestions=["Test"],
            query_quality_score=0.9,
        )
        d = feedback.to_dict()

        assert d["result_count"] == 10
        assert d["status"] == "good"
        assert d["suggestions"] == ["Test"]
        assert d["is_acceptable"] is True


# ============================================================================
# Result Count Analysis Tests
# ============================================================================


class TestAnalyzeResultCount:
    """Tests for analyze_result_count function."""

    def test_zero_results(self):
        """Test feedback for zero results."""
        feedback = analyze_result_count(
            count=0, max_requested=20, query="test query", source="pubmed"
        )

        assert feedback.status == ResultStatus.NONE
        assert feedback.result_count == 0
        assert len(feedback.suggestions) > 0
        assert feedback.query_quality_score == 0.0

    def test_too_few_results(self):
        """Test feedback for too few results."""
        feedback = analyze_result_count(
            count=3, max_requested=20, query="test query", source="pubmed"
        )

        assert feedback.status == ResultStatus.TOO_FEW
        assert feedback.result_count == 3
        assert len(feedback.suggestions) > 0
        assert feedback.query_quality_score == 0.3

    def test_good_results(self):
        """Test feedback for good result count."""
        feedback = analyze_result_count(
            count=15, max_requested=20, query="test query", source="pubmed"
        )

        assert feedback.status == ResultStatus.GOOD
        assert feedback.result_count == 15
        assert feedback.query_quality_score == 1.0

    def test_too_many_results(self):
        """Test feedback when hitting max limit."""
        feedback = analyze_result_count(
            count=20, max_requested=20, query="test query", source="pubmed"
        )

        assert feedback.status == ResultStatus.TOO_MANY
        assert len(feedback.warnings) > 0
        assert "truncated" in feedback.warnings[0].lower()

    def test_high_comfortable_range(self):
        """Test results in high but comfortable range (count >= max_comfortable)."""
        thresholds = ResultThresholds(max_comfortable=80)
        feedback = analyze_result_count(
            count=90,
            max_requested=100,
            query="test query",
            source="pubmed",
            thresholds=thresholds,
        )

        # Should be good but with suggestions (count >= max_comfortable but < max_requested)
        assert feedback.status == ResultStatus.GOOD
        assert feedback.query_quality_score == 0.8

    def test_with_estimated_total(self):
        """Test including estimated total in feedback."""
        feedback = analyze_result_count(
            count=20,
            max_requested=20,
            query="test query",
            source="pubmed",
            estimated_total=500,
        )

        assert feedback.estimated_total == 500
        assert feedback.status == ResultStatus.TOO_MANY
        # Should warn about truncation with estimate
        assert any("500" in w for w in feedback.warnings)

    def test_multiple_sources(self):
        """Test with multiple sources."""
        feedback = analyze_result_count(
            count=10,
            max_requested=20,
            query="test query",
            source=["pubmed", "semantic"],
        )

        assert feedback.status == ResultStatus.GOOD

    def test_custom_thresholds(self):
        """Test with custom thresholds."""
        thresholds = ResultThresholds(min_acceptable=10, max_comfortable=50)
        feedback = analyze_result_count(
            count=8,
            max_requested=20,
            query="test query",
            source="pubmed",
            thresholds=thresholds,
        )

        # 8 is below min_acceptable of 10
        assert feedback.status == ResultStatus.TOO_FEW


# ============================================================================
# Source-Specific Suggestions Tests
# ============================================================================


class TestSourceSpecificSuggestions:
    """Tests for source-specific suggestions."""

    def test_pubmed_suggestions_zero(self):
        """Test PubMed-specific suggestions for zero results."""
        feedback = analyze_result_count(
            count=0, max_requested=20, query="test", source="pubmed"
        )

        suggestions_text = " ".join(feedback.suggestions).lower()
        assert "pubmed" in suggestions_text or "mesh" in suggestions_text

    def test_semantic_suggestions(self):
        """Test Semantic Scholar suggestions."""
        feedback = analyze_result_count(
            count=0, max_requested=20, query="test", source="semantic"
        )

        suggestions_text = " ".join(feedback.suggestions).lower()
        assert "semantic" in suggestions_text or "pubmed" in suggestions_text

    def test_biorxiv_suggestions(self):
        """Test bioRxiv-specific suggestions."""
        feedback = analyze_result_count(
            count=0, max_requested=20, query="test", source="biorxiv"
        )

        suggestions_text = " ".join(feedback.suggestions).lower()
        assert "preprint" in suggestions_text or "biorxiv" in suggestions_text

    def test_pubmed_suggestions_too_many(self):
        """Test PubMed suggestions when too many results."""
        feedback = analyze_result_count(
            count=20, max_requested=20, query="cancer", source="pubmed"
        )

        suggestions_text = " ".join(feedback.suggestions).lower()
        assert "mesh" in suggestions_text or "filter" in suggestions_text


# ============================================================================
# Query-Specific Suggestions Tests
# ============================================================================


class TestQuerySpecificSuggestions:
    """Tests for query-specific suggestions."""

    def test_field_tag_suggestion(self):
        """Test suggestions for queries with field tags."""
        feedback = analyze_result_count(
            count=0,
            max_requested=20,
            query="cancer[Title]",
            source="pubmed",
        )

        suggestions_text = " ".join(feedback.suggestions).lower()
        assert "field" in suggestions_text

    def test_and_operator_suggestion(self):
        """Test suggestions for queries with multiple ANDs."""
        feedback = analyze_result_count(
            count=2,
            max_requested=20,
            query="cancer AND mutation AND therapy AND drug",
            source="pubmed",
        )

        suggestions_text = " ".join(feedback.suggestions).lower()
        assert "and" in suggestions_text or "specific" in suggestions_text

    def test_or_without_and_suggestion(self):
        """Test suggestions for broad OR queries."""
        feedback = analyze_result_count(
            count=20,
            max_requested=20,
            query="cancer OR tumor OR neoplasm",
            source="pubmed",
        )

        suggestions_text = " ".join(feedback.suggestions).lower()
        assert "broad" in suggestions_text or "and" in suggestions_text


# ============================================================================
# Result Quality Analysis Tests
# ============================================================================


class TestAnalyzeResultQuality:
    """Tests for analyze_result_quality function."""

    def test_empty_results(self):
        """Test quality analysis of empty results."""
        metrics = analyze_result_quality([])
        assert metrics.has_recent_papers is False
        assert metrics.has_highly_cited is False
        assert metrics.year_span == 0

    def test_recent_papers_detection(self):
        """Test detection of recent papers."""
        results = [
            {"year": 2025},
            {"year": 2024},
            {"year": 2020},
        ]
        metrics = analyze_result_quality(results, current_year=2026)
        assert metrics.has_recent_papers is True

    def test_no_recent_papers(self):
        """Test detection when no recent papers."""
        results = [
            {"year": 2015},
            {"year": 2018},
        ]
        metrics = analyze_result_quality(results, current_year=2026)
        assert metrics.has_recent_papers is False

    def test_highly_cited_detection(self):
        """Test detection of highly cited papers."""
        results = [
            {"citation_count": 50},
            {"citation_count": 150},  # Highly cited
            {"citation_count": 10},
        ]
        metrics = analyze_result_quality(results)
        assert metrics.has_highly_cited is True

    def test_no_highly_cited(self):
        """Test when no highly cited papers."""
        results = [
            {"citation_count": 5},
            {"citation_count": 20},
        ]
        metrics = analyze_result_quality(results)
        assert metrics.has_highly_cited is False

    def test_review_detection(self):
        """Test detection of review articles."""
        results = [
            {"publication_type": "Research Article"},
            {"publication_type": "Review"},
        ]
        metrics = analyze_result_quality(results)
        assert metrics.has_reviews is True

    def test_source_diversity(self):
        """Test source diversity calculation."""
        results = [
            {"source": "pubmed"},
            {"source": "pubmed"},
            {"source": "semantic"},
            {"source": "biorxiv"},
        ]
        metrics = analyze_result_quality(results)
        assert metrics.source_diversity == 1.0  # 3/3 = 1.0

    def test_single_source(self):
        """Test low source diversity."""
        results = [
            {"source": "pubmed"},
            {"source": "pubmed"},
        ]
        metrics = analyze_result_quality(results)
        assert metrics.source_diversity < 0.5

    def test_year_span_calculation(self):
        """Test year span calculation."""
        results = [
            {"year": 2010},
            {"year": 2015},
            {"year": 2020},
        ]
        metrics = analyze_result_quality(results)
        assert metrics.year_span == 10  # 2020 - 2010

    def test_average_citations(self):
        """Test average citation calculation."""
        results = [
            {"citation_count": 10},
            {"citation_count": 20},
            {"citation_count": 30},
        ]
        metrics = analyze_result_quality(results)
        assert metrics.avg_citation_count == 20.0

    def test_alternative_field_names(self):
        """Test handling of alternative field names."""
        results = [
            {"publication_year": 2025, "citations": 100},  # Alternative names
        ]
        metrics = analyze_result_quality(results, current_year=2026)
        assert metrics.has_recent_papers is True
        assert metrics.has_highly_cited is True


# ============================================================================
# Quality Summary Tests
# ============================================================================


class TestQualitySummary:
    """Tests for get_quality_summary function."""

    def test_summary_with_recent(self):
        """Test summary includes recent papers indicator."""
        metrics = ResultQualityMetrics(has_recent_papers=True)
        summary = get_quality_summary(metrics)
        assert "recent" in summary.lower()

    def test_summary_without_recent(self):
        """Test summary indicates no recent papers."""
        metrics = ResultQualityMetrics(has_recent_papers=False)
        summary = get_quality_summary(metrics)
        assert "no recent" in summary.lower()

    def test_summary_with_reviews(self):
        """Test summary includes review indicator."""
        metrics = ResultQualityMetrics(has_reviews=True)
        summary = get_quality_summary(metrics)
        assert "review" in summary.lower()

    def test_summary_high_citations(self):
        """Test summary includes high citation indicator."""
        metrics = ResultQualityMetrics(avg_citation_count=75)
        summary = get_quality_summary(metrics)
        assert "75" in summary or "citation" in summary.lower()

    def test_summary_good_diversity(self):
        """Test summary indicates good source diversity."""
        metrics = ResultQualityMetrics(source_diversity=0.8)
        summary = get_quality_summary(metrics)
        assert "diversity" in summary.lower()

    def test_empty_metrics_summary(self):
        """Test summary for empty metrics."""
        metrics = ResultQualityMetrics()
        summary = get_quality_summary(metrics)
        assert len(summary) > 0  # Should return something


# ============================================================================
# Validation Report Tests
# ============================================================================


class TestValidationReport:
    """Tests for ValidationReport and validate_search_results."""

    def test_validate_search_results(self):
        """Test complete validation of search results."""
        results = [
            {"year": 2025, "citation_count": 50, "source": "pubmed"},
            {"year": 2020, "citation_count": 100, "source": "semantic"},
        ]

        report = validate_search_results(
            results=results,
            query="test query",
            sources=["pubmed", "semantic"],
            max_requested=20,
        )

        assert report.feedback.result_count == 2
        assert report.query_used == "test query"
        assert len(report.sources_searched) == 2

    def test_validation_report_to_dict(self):
        """Test converting validation report to dictionary."""
        results = [{"year": 2025}]
        report = validate_search_results(
            results=results,
            query="test",
            sources="pubmed",
        )

        d = report.to_dict()
        assert "feedback" in d
        assert "quality" in d
        assert "query_used" in d
        assert "quality_summary" in d

    def test_validation_with_string_source(self):
        """Test validation with single source as string."""
        report = validate_search_results(
            results=[],
            query="test",
            sources="pubmed",  # String, not list
        )

        assert report.sources_searched == ["pubmed"]

    def test_validation_with_estimated_total(self):
        """Test validation with estimated total."""
        results = [{"title": f"Paper {i}"} for i in range(20)]
        report = validate_search_results(
            results=results,
            query="test",
            sources="pubmed",
            max_requested=20,
            estimated_total=500,
        )

        assert report.feedback.estimated_total == 500


# ============================================================================
# Determinism Tests
# ============================================================================


class TestDeterminism:
    """Tests verifying deterministic behavior."""

    def test_analyze_result_count_determinism(self):
        """Test that result analysis is deterministic."""
        params = {
            "count": 10,
            "max_requested": 20,
            "query": "cancer mutation",
            "source": "pubmed",
        }

        feedback1 = analyze_result_count(**params)
        feedback2 = analyze_result_count(**params)
        feedback3 = analyze_result_count(**params)

        assert feedback1.status == feedback2.status == feedback3.status
        assert feedback1.suggestions == feedback2.suggestions == feedback3.suggestions
        assert (
            feedback1.query_quality_score
            == feedback2.query_quality_score
            == feedback3.query_quality_score
        )

    def test_quality_analysis_determinism(self):
        """Test that quality analysis is deterministic."""
        results = [
            {"year": 2025, "citation_count": 100, "source": "pubmed"},
            {"year": 2020, "citation_count": 50, "source": "semantic"},
        ]

        metrics1 = analyze_result_quality(results)
        metrics2 = analyze_result_quality(results)
        metrics3 = analyze_result_quality(results)

        assert metrics1.has_recent_papers == metrics2.has_recent_papers
        assert metrics1.year_span == metrics2.year_span == metrics3.year_span
        assert (
            metrics1.avg_citation_count
            == metrics2.avg_citation_count
            == metrics3.avg_citation_count
        )

    def test_suggestions_determinism(self):
        """Test that suggestions are deterministic."""
        # Zero results case
        feedback1 = analyze_result_count(0, 20, "test", "pubmed")
        feedback2 = analyze_result_count(0, 20, "test", "pubmed")

        assert feedback1.suggestions == feedback2.suggestions

        # Too many results case
        feedback3 = analyze_result_count(20, 20, "test", "pubmed")
        feedback4 = analyze_result_count(20, 20, "test", "pubmed")

        assert feedback3.suggestions == feedback4.suggestions


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_exactly_at_threshold(self):
        """Test result count exactly at thresholds."""
        thresholds = ResultThresholds(min_acceptable=5)

        # Exactly at minimum
        feedback = analyze_result_count(5, 20, "test", "pubmed", thresholds)
        assert feedback.status == ResultStatus.GOOD

        # One below minimum
        feedback = analyze_result_count(4, 20, "test", "pubmed", thresholds)
        assert feedback.status == ResultStatus.TOO_FEW

    def test_invalid_year_in_results(self):
        """Test handling of invalid year values."""
        results = [
            {"year": "invalid"},
            {"year": None},
            {"year": 2020},
        ]
        metrics = analyze_result_quality(results)
        # Should handle gracefully, only count valid year
        assert metrics.year_span == 0  # Only one valid year

    def test_invalid_citations_in_results(self):
        """Test handling of invalid citation values."""
        results = [
            {"citation_count": "many"},
            {"citation_count": None},
            {"citation_count": 100},
        ]
        metrics = analyze_result_quality(results)
        # Should handle gracefully
        assert metrics.avg_citation_count == 100.0

    def test_empty_source_list(self):
        """Test with empty source list."""
        feedback = analyze_result_count(10, 20, "test", [])
        assert feedback.status == ResultStatus.GOOD

    def test_very_large_result_count(self):
        """Test with very large result counts."""
        feedback = analyze_result_count(
            count=10000,
            max_requested=10000,
            query="test",
            source="pubmed",
            estimated_total=1000000,
        )
        assert feedback.status == ResultStatus.TOO_MANY
