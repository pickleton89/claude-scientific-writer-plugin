"""Tests for quality_scorer module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.quality_scorer import (
    calculate_measurable_score,
    get_subjective_criteria,
    calculate_total_score,
    get_scoring_rubric_text,
)


class TestCalculateMeasurableScore:
    """Tests for measurable score calculation."""

    def test_perfect_score(self):
        """Perfect spec should score 4/4."""
        spec = {
            "resolution_dpi": 300,
            "dimensions": {"width_mm": 89, "column_type": "single"},
            "accessibility": {
                "colorblind_safe": True,
                "min_contrast_ratio": 4.5,
            },
            "typography": {"min_pt": 8},
        }
        venue_specs = {
            "min_dpi": 300,
            "single_col_mm": 89,
            "min_font_pt": 7,
        }
        result = calculate_measurable_score(spec, venue_specs)
        assert result["measurable_score"] == 4
        assert result["measurable_max"] == 4
        assert result["measurable_percentage"] == 100.0

    def test_zero_score(self):
        """Completely non-compliant spec should score 0/4."""
        spec = {
            "resolution_dpi": 72,
            "dimensions": {"width_mm": 200, "column_type": "single"},
            "accessibility": {
                "colorblind_safe": False,
                "min_contrast_ratio": 2.0,
            },
            "typography": {"min_pt": 5},
        }
        venue_specs = {
            "min_dpi": 300,
            "single_col_mm": 89,
            "min_font_pt": 7,
        }
        result = calculate_measurable_score(spec, venue_specs)
        assert result["measurable_score"] == 0

    def test_partial_score(self):
        """Partially compliant spec should get partial score."""
        spec = {
            "resolution_dpi": 300,  # Pass
            "dimensions": {"width_mm": 200},  # Fail (too wide)
            "accessibility": {
                "colorblind_safe": True,
                "min_contrast_ratio": 4.5,
            },  # Pass
            "typography": {"min_pt": 8},  # Pass
        }
        venue_specs = {
            "min_dpi": 300,
            "single_col_mm": 89,
            "min_font_pt": 7,
        }
        result = calculate_measurable_score(spec, venue_specs)
        assert result["measurable_score"] == 3

    def test_returns_details(self):
        """Should return scoring details."""
        spec = {"resolution_dpi": 300}
        venue_specs = {"min_dpi": 300, "single_col_mm": 89}
        result = calculate_measurable_score(spec, venue_specs)
        assert "details" in result
        assert isinstance(result["details"], list)
        assert len(result["details"]) > 0

    def test_returns_criteria_breakdown(self):
        """Should return per-criterion breakdown."""
        spec = {"resolution_dpi": 300}
        venue_specs = {"min_dpi": 300, "single_col_mm": 89}
        result = calculate_measurable_score(spec, venue_specs)
        assert "criteria" in result
        assert "resolution" in result["criteria"]

    def test_missing_values_handled(self):
        """Missing spec values should be handled gracefully."""
        spec = {}
        venue_specs = {"min_dpi": 300, "single_col_mm": 89}
        result = calculate_measurable_score(spec, venue_specs)
        assert result["measurable_score"] == 0


class TestGetSubjectiveCriteria:
    """Tests for subjective criteria definition."""

    def test_returns_list(self):
        """Should return list of criteria."""
        criteria = get_subjective_criteria()
        assert isinstance(criteria, list)
        assert len(criteria) > 0

    def test_criteria_have_required_fields(self):
        """Each criterion should have required fields."""
        criteria = get_subjective_criteria()
        for c in criteria:
            assert "criterion" in c
            assert "question" in c
            assert "max_points" in c
            assert "scoring" in c

    def test_total_subjective_points_is_six(self):
        """Total subjective points should be 6."""
        criteria = get_subjective_criteria()
        total = sum(c["max_points"] for c in criteria)
        assert total == 6

    def test_scoring_rubric_complete(self):
        """Scoring rubric should have entries for all possible scores."""
        criteria = get_subjective_criteria()
        for c in criteria:
            expected_scores = range(c["max_points"] + 1)
            for score in expected_scores:
                assert score in c["scoring"], \
                    f"{c['criterion']} missing score {score}"


class TestCalculateTotalScore:
    """Tests for total score calculation."""

    def test_perfect_score(self):
        """Perfect scores should total 10."""
        measurable_result = {
            "measurable_score": 4,
            "details": [],
        }
        subjective_scores = {
            "intentionality": 2,
            "clarity": 2,
            "consistency": 1,
            "independence": 1,
        }
        result = calculate_total_score(measurable_result, subjective_scores)
        assert result["total_score"] == 10
        assert result["interpretation"] == "Exemplary design"
        assert result["publication_ready"]

    def test_zero_score(self):
        """Zero scores should total 0."""
        measurable_result = {
            "measurable_score": 0,
            "details": [],
        }
        subjective_scores = {
            "intentionality": 0,
            "clarity": 0,
            "consistency": 0,
            "independence": 0,
        }
        result = calculate_total_score(measurable_result, subjective_scores)
        assert result["total_score"] == 0
        assert "major revision" in result["interpretation"].lower()
        assert not result["publication_ready"]

    def test_publication_ready_threshold(self):
        """Score of 7+ should be publication ready."""
        measurable_result = {"measurable_score": 3, "details": []}
        subjective_scores = {
            "intentionality": 1,
            "clarity": 2,
            "consistency": 1,
            "independence": 0,
        }
        result = calculate_total_score(measurable_result, subjective_scores)
        assert result["total_score"] == 7
        assert result["publication_ready"]

    def test_score_interpretation_bands(self):
        """Test all score interpretation bands."""
        for total, expected_interp in [
            (0, "Needs major revision"),
            (4, "Needs major revision"),
            (5, "Acceptable for internal use"),
            (6, "Acceptable for internal use"),
            (7, "Publication ready"),
            (8, "Publication ready"),
            (9, "Exemplary design"),
            (10, "Exemplary design"),
        ]:
            # Create scores that sum to total
            measurable = min(total, 4)
            subjective = total - measurable
            measurable_result = {"measurable_score": measurable, "details": []}

            # Distribute subjective score
            subjective_scores = {
                "intentionality": min(subjective, 2),
                "clarity": min(max(subjective - 2, 0), 2),
                "consistency": min(max(subjective - 4, 0), 1),
                "independence": max(subjective - 5, 0),
            }

            result = calculate_total_score(measurable_result, subjective_scores)
            assert expected_interp in result["interpretation"], \
                f"Score {total} should be '{expected_interp}'"

    def test_clamps_subjective_scores(self):
        """Subjective scores above max should be clamped."""
        measurable_result = {"measurable_score": 4, "details": []}
        subjective_scores = {
            "intentionality": 10,  # Max is 2
            "clarity": 10,  # Max is 2
            "consistency": 10,  # Max is 1
            "independence": 10,  # Max is 1
        }
        result = calculate_total_score(measurable_result, subjective_scores)
        # Should be clamped to 4 + 6 = 10
        assert result["total_score"] == 10

    def test_returns_component_breakdown(self):
        """Should return breakdown of score components."""
        measurable_result = {"measurable_score": 2, "details": ["detail1"]}
        subjective_scores = {"intentionality": 1, "clarity": 1}
        result = calculate_total_score(measurable_result, subjective_scores)

        assert "measurable_component" in result
        assert result["measurable_component"]["score"] == 2
        assert result["measurable_component"]["weight"] == "40%"

        assert "subjective_component" in result
        assert result["subjective_component"]["weight"] == "60%"


class TestGetScoringRubricText:
    """Tests for rubric text generation."""

    def test_returns_string(self):
        """Should return string."""
        text = get_scoring_rubric_text()
        assert isinstance(text, str)
        assert len(text) > 100

    def test_includes_all_criteria(self):
        """Should include all criteria names."""
        text = get_scoring_rubric_text()
        criteria = get_subjective_criteria()
        for c in criteria:
            assert c["criterion"] in text.lower()

    def test_includes_score_interpretations(self):
        """Should include score interpretation guide."""
        text = get_scoring_rubric_text()
        assert "major revision" in text.lower()
        assert "publication ready" in text.lower()
        assert "exemplary" in text.lower()
