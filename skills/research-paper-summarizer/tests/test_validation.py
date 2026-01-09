"""
Comprehensive test suite for research-paper-summarizer validation utilities.

Tests cover:
- Statistics extraction and normalization
- Article type detection
- Section marker management
- Summary validation
- YAML validation
- Schema serialization/deserialization
"""

import os
import pytest
import tempfile

from utils.schemas import (
    ValidationResult,
    SectionMarker,
    MarkerStatus,
    StatisticResult,
    StatisticType,
    SummaryValidationReport,
    ArticleType,
    ArticleTypeResult,
    YAMLValidationResult,
)
from utils.statistics import (
    extract_statistics,
    summarize_statistics,
    has_sufficient_statistics,
)


# ============================================================================
# Statistics Extraction Tests
# ============================================================================


class TestStatisticsExtraction:
    """Tests for statistics extraction functionality."""

    def test_extract_p_values(self, sample_text_with_statistics: str) -> None:
        """Test extraction of p-values."""
        stats = extract_statistics(sample_text_with_statistics)
        p_values = [s for s in stats if s.stat_type == StatisticType.P_VALUE]
        assert len(p_values) >= 2, "Should find at least 2 p-values"
        # Check that p = 0.003 is found
        assert any("0.003" in s.normalized for s in p_values)

    def test_extract_confidence_intervals(self, sample_text_with_statistics: str) -> None:
        """Test extraction of confidence intervals."""
        stats = extract_statistics(sample_text_with_statistics)
        cis = [s for s in stats if s.stat_type == StatisticType.CONFIDENCE_INTERVAL]
        assert len(cis) >= 1, "Should find at least 1 CI"

    def test_extract_sample_sizes(self, sample_text_with_statistics: str) -> None:
        """Test extraction of sample sizes."""
        stats = extract_statistics(sample_text_with_statistics)
        samples = [s for s in stats if s.stat_type == StatisticType.SAMPLE_SIZE]
        assert len(samples) >= 1, "Should find at least 1 sample size"
        assert any("120" in s.normalized for s in samples)

    def test_extract_fold_changes(self, sample_text_with_statistics: str) -> None:
        """Test extraction of fold changes."""
        stats = extract_statistics(sample_text_with_statistics)
        folds = [s for s in stats if s.stat_type == StatisticType.FOLD_CHANGE]
        assert len(folds) >= 1, "Should find at least 1 fold change"
        assert any("2.3" in s.normalized for s in folds)

    def test_extract_hazard_ratios(self, sample_text_with_statistics: str) -> None:
        """Test extraction of hazard ratios."""
        stats = extract_statistics(sample_text_with_statistics)
        hrs = [s for s in stats if s.stat_type == StatisticType.HAZARD_RATIO]
        assert len(hrs) >= 1, "Should find at least 1 HR"
        assert any("0.67" in s.normalized for s in hrs)

    def test_extract_odds_ratios(self, sample_text_with_statistics: str) -> None:
        """Test extraction of odds ratios."""
        stats = extract_statistics(sample_text_with_statistics)
        ors = [s for s in stats if s.stat_type == StatisticType.ODDS_RATIO]
        assert len(ors) >= 1, "Should find at least 1 OR"
        assert any("2.1" in s.normalized for s in ors)

    def test_extract_effect_sizes(self, sample_text_with_statistics: str) -> None:
        """Test extraction of effect sizes."""
        stats = extract_statistics(sample_text_with_statistics)
        effects = [s for s in stats if s.stat_type == StatisticType.EFFECT_SIZE]
        assert len(effects) >= 1, "Should find at least 1 effect size"
        assert any("0.45" in s.normalized for s in effects)

    def test_extract_correlations(self, sample_text_with_statistics: str) -> None:
        """Test extraction of correlations."""
        stats = extract_statistics(sample_text_with_statistics)
        corrs = [s for s in stats if s.stat_type == StatisticType.CORRELATION]
        assert len(corrs) >= 1, "Should find at least 1 correlation"
        assert any("0.72" in s.normalized for s in corrs)

    def test_extract_percent_changes(self, sample_text_with_statistics: str) -> None:
        """Test extraction of percent changes."""
        stats = extract_statistics(sample_text_with_statistics)
        pcts = [s for s in stats if s.stat_type == StatisticType.PERCENT_CHANGE]
        assert len(pcts) >= 1, "Should find at least 1 percent change"
        assert any("45" in s.normalized for s in pcts)

    def test_extract_mean_sd(self, sample_text_with_statistics: str) -> None:
        """Test extraction of mean ± SD values."""
        stats = extract_statistics(sample_text_with_statistics)
        means = [s for s in stats if s.stat_type == StatisticType.MEAN_SD]
        assert len(means) >= 1, "Should find at least 1 mean±SD"
        assert any("23.5" in s.normalized for s in means)

    def test_deduplication(self) -> None:
        """Test that duplicate statistics at same position are removed."""
        text = "p = 0.05 p = 0.05"  # Same stat repeated
        stats = extract_statistics(text, deduplicate=True)
        # Should find 2 distinct occurrences
        assert len(stats) == 2

    def test_context_extraction(self, sample_text_with_statistics: str) -> None:
        """Test that context is properly extracted."""
        stats = extract_statistics(sample_text_with_statistics, context_chars=30)
        for stat in stats:
            assert stat.context.startswith("...")
            assert stat.context.endswith("...")
            assert len(stat.context) > 10

    def test_position_ordering(self, sample_text_with_statistics: str) -> None:
        """Test that statistics are ordered by position."""
        stats = extract_statistics(sample_text_with_statistics)
        positions = [s.position for s in stats]
        assert positions == sorted(positions), "Stats should be sorted by position"

    def test_empty_text(self) -> None:
        """Test extraction from empty text."""
        stats = extract_statistics("")
        assert stats == []

    def test_no_statistics(self) -> None:
        """Test extraction from text without statistics."""
        text = "This is a sentence without any numerical data or statistics."
        stats = extract_statistics(text)
        assert stats == []


class TestStatisticsSummarization:
    """Tests for statistics summarization."""

    def test_summarize_by_type(self, sample_text_with_statistics: str) -> None:
        """Test summarization by statistic type."""
        stats = extract_statistics(sample_text_with_statistics)
        summary = summarize_statistics(stats)
        assert "total" in summary
        assert "by_type" in summary
        assert summary["total"] == len(stats)

    def test_summary_examples(self, sample_text_with_statistics: str) -> None:
        """Test that summary includes examples."""
        stats = extract_statistics(sample_text_with_statistics)
        summary = summarize_statistics(stats)
        for type_name, data in summary["by_type"].items():
            assert "count" in data
            assert "examples" in data
            assert len(data["examples"]) <= 3  # Max 3 examples

    def test_has_sufficient_statistics(self, sample_text_with_statistics: str) -> None:
        """Test sufficiency check for statistics."""
        passes, count, type_counts = has_sufficient_statistics(
            sample_text_with_statistics, min_count=3
        )
        assert passes is True
        assert count >= 3

    def test_insufficient_statistics(self) -> None:
        """Test detection of insufficient statistics."""
        text = "Only one stat: p = 0.05"
        passes, count, type_counts = has_sufficient_statistics(text, min_count=3)
        assert passes is False
        assert count < 3


# ============================================================================
# Article Type Detection Tests
# ============================================================================


class TestArticleTypeDetection:
    """Tests for article type detection."""

    def test_detect_review_article(self, sample_text_review_article: str) -> None:
        """Test detection of review articles."""
        from detect_article_type import detect_article_type

        result = detect_article_type(sample_text_review_article)
        assert result.detected_type == ArticleType.REVIEW
        assert result.confidence >= 0.5

    def test_detect_compbio_article(self, sample_text_compbio: str) -> None:
        """Test detection of computational biology articles."""
        from detect_article_type import detect_article_type

        result = detect_article_type(sample_text_compbio)
        assert result.detected_type == ArticleType.COMPBIO
        assert result.confidence >= 0.5

    def test_detect_cellmolbio_article(self, sample_text_cellmolbio: str) -> None:
        """Test detection of cell/molecular biology articles."""
        from detect_article_type import detect_article_type

        result = detect_article_type(sample_text_cellmolbio)
        assert result.detected_type == ArticleType.CELLMOLBIO
        assert result.confidence >= 0.5

    def test_detect_general_article(self, sample_text_general: str) -> None:
        """Test detection defaults to general for ambiguous text."""
        from detect_article_type import detect_article_type

        result = detect_article_type(sample_text_general)
        assert result.detected_type == ArticleType.GENERAL

    def test_scores_populated(self, sample_text_review_article: str) -> None:
        """Test that all type scores are populated."""
        from detect_article_type import detect_article_type

        result = detect_article_type(sample_text_review_article)
        assert "review" in result.scores
        assert "compbio" in result.scores
        assert "cellmolbio" in result.scores
        assert "general" in result.scores

    def test_matched_keywords_populated(self, sample_text_review_article: str) -> None:
        """Test that matched keywords are tracked."""
        from detect_article_type import detect_article_type

        result = detect_article_type(sample_text_review_article)
        assert len(result.matched_keywords["review"]) > 0


# ============================================================================
# Section Marker Tests
# ============================================================================


class TestSectionMarkers:
    """Tests for section marker management."""

    def test_get_markers(self, content_with_markers: str) -> None:
        """Test extraction of section markers."""
        from update_markers import get_markers

        markers = get_markers(content_with_markers)
        assert len(markers) == 5

    def test_marker_status_complete(self, content_with_markers: str) -> None:
        """Test detection of COMPLETE markers."""
        from update_markers import get_markers

        markers = get_markers(content_with_markers)
        complete = [m for m in markers if m.status == MarkerStatus.COMPLETE]
        assert len(complete) == 2

    def test_marker_status_pending(self, content_with_markers: str) -> None:
        """Test detection of PENDING markers."""
        from update_markers import get_markers

        markers = get_markers(content_with_markers)
        pending = [m for m in markers if m.status == MarkerStatus.PENDING]
        assert len(pending) == 2

    def test_marker_status_skipped(self, content_with_markers: str) -> None:
        """Test detection of SKIPPED markers."""
        from update_markers import get_markers

        markers = get_markers(content_with_markers)
        skipped = [m for m in markers if m.status == MarkerStatus.SKIPPED]
        assert len(skipped) == 1

    def test_update_marker_complete(self, content_with_markers: str) -> None:
        """Test updating marker to COMPLETE."""
        from update_markers import update_marker

        updated = update_marker(content_with_markers, "methods", "COMPLETE")
        assert "<!-- SECTION: methods COMPLETE -->" in updated
        assert "<!-- SECTION: methods PENDING -->" not in updated

    def test_update_marker_skip(self, content_with_markers: str) -> None:
        """Test updating marker to SKIPPED."""
        from update_markers import update_marker

        updated = update_marker(content_with_markers, "methods", "SKIPPED")
        assert "<!-- SECTION: methods SKIPPED -->" in updated

    def test_update_marker_not_found(self, content_with_markers: str) -> None:
        """Test error when marker not found."""
        from update_markers import update_marker

        with pytest.raises(ValueError, match="not found"):
            update_marker(content_with_markers, "nonexistent", "COMPLETE")

    def test_reset_all_markers(self, content_with_markers: str) -> None:
        """Test resetting all markers."""
        from update_markers import reset_all_markers

        reset = reset_all_markers(content_with_markers, "PENDING")
        assert "COMPLETE" not in reset
        assert "SKIPPED" not in reset


# ============================================================================
# Summary Validation Tests
# ============================================================================


class TestSummaryValidation:
    """Tests for summary markdown validation."""

    def test_valid_summary_passes(self, valid_summary_content: str) -> None:
        """Test that valid summary passes validation."""
        from validate_summary import validate_summary

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(valid_summary_content)
            f.flush()
            temp_path = f.name

        try:
            report = validate_summary(temp_path)
            assert report.valid is True
            assert report.score > 0.8
        finally:
            os.unlink(temp_path)

    def test_invalid_summary_fails(self, invalid_summary_content: str) -> None:
        """Test that invalid summary fails validation."""
        from validate_summary import validate_summary

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(invalid_summary_content)
            f.flush()
            temp_path = f.name

        try:
            report = validate_summary(temp_path)
            assert report.valid is False
            assert report.pending_count > 0
        finally:
            os.unlink(temp_path)

    def test_pending_sections_detected(self, invalid_summary_content: str) -> None:
        """Test detection of pending sections."""
        from validate_summary import validate_summary

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(invalid_summary_content)
            f.flush()
            temp_path = f.name

        try:
            report = validate_summary(temp_path)
            pending_check = next(c for c in report.checks if c.name == "no_pending_sections")
            assert pending_check.passed is False
        finally:
            os.unlink(temp_path)

    def test_placeholder_detection(self, invalid_summary_content: str) -> None:
        """Test detection of unfilled placeholders."""
        from validate_summary import validate_summary

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(invalid_summary_content)
            f.flush()
            temp_path = f.name

        try:
            report = validate_summary(temp_path)
            assert report.placeholder_count > 0
        finally:
            os.unlink(temp_path)

    def test_statistics_counted(self, valid_summary_content: str) -> None:
        """Test that statistics are counted."""
        from validate_summary import validate_summary

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(valid_summary_content)
            f.flush()
            temp_path = f.name

        try:
            report = validate_summary(temp_path)
            assert report.stat_count > 0
        finally:
            os.unlink(temp_path)

    def test_figure_refs_counted(self, valid_summary_content: str) -> None:
        """Test that figure references are counted."""
        from validate_summary import validate_summary

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(valid_summary_content)
            f.flush()
            temp_path = f.name

        try:
            report = validate_summary(temp_path)
            assert report.figure_ref_count > 0
        finally:
            os.unlink(temp_path)


# ============================================================================
# YAML Validation Tests
# ============================================================================


class TestYAMLValidation:
    """Tests for YAML summary validation."""

    def test_valid_yaml_passes(self, valid_yaml_data: dict) -> None:
        """Test that valid YAML passes validation."""
        import yaml as pyyaml
        from validate_yaml import validate_yaml_summary

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            pyyaml.dump(valid_yaml_data, f)
            f.flush()
            temp_path = f.name

        try:
            result = validate_yaml_summary(temp_path)
            assert result.valid is True
            assert len(result.errors) == 0
        finally:
            os.unlink(temp_path)

    def test_invalid_yaml_fails(self, invalid_yaml_data: dict) -> None:
        """Test that invalid YAML fails validation."""
        import yaml as pyyaml
        from validate_yaml import validate_yaml_summary

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            pyyaml.dump(invalid_yaml_data, f)
            f.flush()
            temp_path = f.name

        try:
            result = validate_yaml_summary(temp_path)
            assert result.valid is False
            assert len(result.errors) > 0
        finally:
            os.unlink(temp_path)

    def test_missing_metadata_detected(self) -> None:
        """Test detection of missing metadata."""
        import yaml as pyyaml
        from validate_yaml import validate_yaml_summary

        data = {"overview": "Some content", "key_findings": []}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            pyyaml.dump(data, f)
            f.flush()
            temp_path = f.name

        try:
            result = validate_yaml_summary(temp_path)
            assert any("metadata" in e for e in result.errors)
        finally:
            os.unlink(temp_path)

    def test_short_overview_warning(self, valid_yaml_data: dict) -> None:
        """Test warning for short overview."""
        import yaml as pyyaml
        from validate_yaml import validate_yaml_summary

        valid_yaml_data["overview"] = "Too short"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            pyyaml.dump(valid_yaml_data, f)
            f.flush()
            temp_path = f.name

        try:
            result = validate_yaml_summary(temp_path)
            assert any("overview" in e.lower() for e in result.errors)
        finally:
            os.unlink(temp_path)


# ============================================================================
# Schema Serialization Tests
# ============================================================================


class TestSchemasSerialization:
    """Tests for schema serialization and deserialization."""

    def test_validation_result_roundtrip(self) -> None:
        """Test ValidationResult serialization roundtrip."""
        original = ValidationResult(
            name="test_check",
            passed=True,
            message="Test passed",
            severity="info",
        )
        data = original.to_dict()
        restored = ValidationResult.from_dict(data)

        assert restored.name == original.name
        assert restored.passed == original.passed
        assert restored.message == original.message
        assert restored.severity == original.severity

    def test_section_marker_roundtrip(self) -> None:
        """Test SectionMarker serialization roundtrip."""
        original = SectionMarker(
            name="introduction",
            marker_type="section",
            status=MarkerStatus.COMPLETE,
            position=100,
        )
        data = original.to_dict()
        restored = SectionMarker.from_dict(data)

        assert restored.name == original.name
        assert restored.status == original.status

    def test_statistic_result_roundtrip(self) -> None:
        """Test StatisticResult serialization roundtrip."""
        original = StatisticResult(
            stat_type=StatisticType.P_VALUE,
            value="p = 0.003",
            normalized="p = 0.003",
            context="...significance (p = 0.003) was...",
            position=50,
        )
        data = original.to_dict()
        restored = StatisticResult.from_dict(data)

        assert restored.stat_type == original.stat_type
        assert restored.normalized == original.normalized

    def test_article_type_result_roundtrip(self) -> None:
        """Test ArticleTypeResult serialization roundtrip."""
        original = ArticleTypeResult(
            detected_type=ArticleType.REVIEW,
            confidence=0.85,
            scores={"review": 15, "compbio": 3, "cellmolbio": 2, "general": 5},
            matched_keywords={"review": ["systematic review", "meta-analysis"]},
        )
        data = original.to_dict()
        restored = ArticleTypeResult.from_dict(data)

        assert restored.detected_type == original.detected_type
        assert restored.confidence == original.confidence

    def test_yaml_validation_result_roundtrip(self) -> None:
        """Test YAMLValidationResult serialization roundtrip."""
        original = YAMLValidationResult(
            valid=True,
            errors=[],
            warnings=["Minor issue"],
            data={"test": "data"},
        )
        data = original.to_dict()
        restored = YAMLValidationResult.from_dict(data)

        assert restored.valid == original.valid
        assert restored.warnings == original.warnings

    def test_summary_validation_report_roundtrip(self) -> None:
        """Test SummaryValidationReport full roundtrip."""
        original = SummaryValidationReport(summary_path="/path/to/summary.md")
        original.add_check(
            ValidationResult("test", True, "Passed", "info")
        )
        original.markers = [
            SectionMarker("intro", "section", MarkerStatus.COMPLETE, 0)
        ]
        original.statistics = [
            StatisticResult(
                StatisticType.P_VALUE, "p=0.05", "p = 0.05", "...", 10
            )
        ]
        original.stat_count = 1
        original.figure_ref_count = 3
        original.calculate_score()

        data = original.to_dict()
        restored = SummaryValidationReport.from_dict(data)

        assert restored.summary_path == original.summary_path
        assert restored.score == original.score
        assert len(restored.checks) == len(original.checks)
        assert len(restored.markers) == len(original.markers)
        assert len(restored.statistics) == len(original.statistics)


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_extract_stats_unicode(self) -> None:
        """Test extraction with unicode characters."""
        text = "Cohen's d = 0.45, η² = 0.12, ρ = 0.78"
        stats = extract_statistics(text)
        assert len(stats) >= 2

    def test_extract_stats_newlines(self) -> None:
        """Test extraction across newlines."""
        text = "p = 0.003\nn = 120\nHR = 0.67"
        stats = extract_statistics(text)
        assert len(stats) >= 3

    def test_large_numbers(self) -> None:
        """Test extraction of large sample sizes."""
        text = "n = 12,500 patients enrolled"
        stats = extract_statistics(text)
        sample_stats = [s for s in stats if s.stat_type == StatisticType.SAMPLE_SIZE]
        assert len(sample_stats) >= 1

    def test_marker_types_distinguished(self, content_with_markers: str) -> None:
        """Test that SECTION and SUBSECTION types are distinguished."""
        from update_markers import get_markers

        markers = get_markers(content_with_markers)
        sections = [m for m in markers if m.marker_type == "section"]
        subsections = [m for m in markers if m.marker_type == "subsection"]
        assert len(sections) == 3
        assert len(subsections) == 2
