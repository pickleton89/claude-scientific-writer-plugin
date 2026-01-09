"""Tests for calculate_scores module validation functions."""

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculate_scores import (
    REQUIRED_DIMENSIONS,
    validate_scores,
    validate_justifications,
    validate_score_consistency,
    validate_complete_review,
    calculate_weighted_average,
    get_quality_level,
    DEFAULT_WEIGHTS,
)


class TestValidateScores:
    """Tests for validate_scores function."""

    def test_complete_valid_scores(self):
        """Test that complete valid scores pass validation."""
        scores = {
            "problem_formulation": 4.0,
            "literature_review": 4.0,
            "methodology": 3.5,
            "data_collection": 4.0,
            "analysis": 3.5,
            "results": 4.0,
            "writing": 4.5,
            "citations": 4.0,
        }
        result = validate_scores(scores)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_dimension(self):
        """Test that missing dimensions are detected."""
        scores = {
            "problem_formulation": 4.0,
            "literature_review": 4.0,
            # Missing other dimensions
        }
        result = validate_scores(scores)
        assert not result.is_valid
        assert len(result.errors) == 6  # Missing 6 dimensions

    def test_score_out_of_bounds_high(self):
        """Test that scores above 5 are detected."""
        scores = {dim: 4.0 for dim in REQUIRED_DIMENSIONS}
        scores["methodology"] = 6.0  # Invalid
        result = validate_scores(scores)
        assert not result.is_valid
        assert any("out of bounds" in e for e in result.errors)

    def test_score_out_of_bounds_low(self):
        """Test that scores below 1 are detected."""
        scores = {dim: 4.0 for dim in REQUIRED_DIMENSIONS}
        scores["methodology"] = 0.5  # Invalid
        result = validate_scores(scores)
        assert not result.is_valid
        assert any("out of bounds" in e for e in result.errors)

    def test_normalized_dimension_names(self):
        """Test that hyphenated dimension names are normalized."""
        scores = {
            "problem-formulation": 4.0,  # Hyphenated
            "literature_review": 4.0,
            "methodology": 3.5,
            "data_collection": 4.0,
            "analysis": 3.5,
            "results": 4.0,
            "writing": 4.5,
            "citations": 4.0,
        }
        result = validate_scores(scores)
        assert result.is_valid


class TestValidateJustifications:
    """Tests for validate_justifications function."""

    def test_complete_justifications(self):
        """Test that complete justifications pass validation."""
        justifications = {
            dim: "A" * 60  # Long enough justification
            for dim in REQUIRED_DIMENSIONS
        }
        result = validate_justifications(justifications)
        assert result.is_valid  # Justifications are warnings, not errors
        assert len(result.warnings) == 0

    def test_missing_justifications(self):
        """Test that missing justifications generate warnings."""
        justifications = {
            "methodology": "Excellent methods with clear protocols and validation."
        }
        result = validate_justifications(justifications)
        assert result.is_valid  # Still valid - just warnings
        assert len(result.warnings) >= 7  # Missing 7 dimensions

    def test_brief_justifications(self):
        """Test that brief justifications generate warnings."""
        justifications = {
            dim: "Short"  # Too brief
            for dim in REQUIRED_DIMENSIONS
        }
        result = validate_justifications(justifications)
        assert result.is_valid
        assert all("too brief" in w.lower() for w in result.warnings)


class TestValidateScoreConsistency:
    """Tests for validate_score_consistency function."""

    def test_consistent_scores_and_issues(self):
        """Test that consistent scores and issues pass."""
        scores = {
            "methodology": 2.0,  # Low score
            "data_collection": 2.5,
            "writing": 4.0,
        }
        issues = [
            {"severity": "critical", "category": "methodology"},
        ]
        result = validate_score_consistency(scores, issues)
        assert result.is_valid
        assert len(result.warnings) == 0

    def test_inconsistent_methodology_score(self):
        """Test that high methodology score with critical issues triggers warning."""
        scores = {
            "methodology": 4.5,  # High score despite critical issues
            "data_collection": 4.0,
            "writing": 4.0,
        }
        issues = [
            {"severity": "critical", "category": "methodology"},
        ]
        result = validate_score_consistency(scores, issues)
        assert not result.is_valid
        assert any("methodology" in w.lower() for w in result.warnings)

    def test_many_writing_issues(self):
        """Test that many writing issues with high score triggers warning."""
        scores = {
            "methodology": 4.0,
            "data_collection": 4.0,
            "writing": 4.5,  # High score despite many issues
        }
        issues = [
            {"severity": "minor", "category": "writing"},
            {"severity": "minor", "category": "grammar"},
            {"severity": "minor", "category": "clarity"},
            {"severity": "minor", "category": "writing"},
            {"severity": "minor", "category": "writing"},
            {"severity": "minor", "category": "writing"},
        ]
        result = validate_score_consistency(scores, issues)
        assert any("writing" in w.lower() for w in result.warnings)

    def test_multiple_critical_issues(self):
        """Test that multiple critical issues with high average triggers warning."""
        scores = {dim: 4.5 for dim in REQUIRED_DIMENSIONS}
        issues = [
            {"severity": "critical", "category": "methodology"},
            {"severity": "critical", "category": "data"},
        ]
        result = validate_score_consistency(scores, issues)
        assert any("critical" in w.lower() for w in result.warnings)


class TestValidateCompleteReview:
    """Tests for validate_complete_review function."""

    def test_complete_valid_review(self):
        """Test that complete valid review passes."""
        scores = {dim: 4.0 for dim in REQUIRED_DIMENSIONS}
        justifications = {dim: "A" * 60 for dim in REQUIRED_DIMENSIONS}
        issues = []

        result = validate_complete_review(scores, justifications, issues)
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_review_with_missing_scores(self):
        """Test that review with missing scores fails."""
        scores = {"methodology": 4.0}  # Incomplete
        result = validate_complete_review(scores)
        assert not result.is_valid
        assert len(result.errors) > 0


class TestScoreCalculation:
    """Tests for score calculation functions."""

    def test_weighted_average_all_same(self):
        """Test weighted average with all same scores."""
        scores = {dim: 4.0 for dim in REQUIRED_DIMENSIONS}
        avg = calculate_weighted_average(scores, DEFAULT_WEIGHTS)
        assert abs(avg - 4.0) < 0.01

    def test_weighted_average_methodology_weight(self):
        """Test that methodology has higher weight."""
        # All 3.0 except methodology is 5.0
        scores = {dim: 3.0 for dim in REQUIRED_DIMENSIONS}
        baseline = calculate_weighted_average(scores, DEFAULT_WEIGHTS)

        scores["methodology"] = 5.0
        with_high_methodology = calculate_weighted_average(scores, DEFAULT_WEIGHTS)

        # Reset and try citations instead (lowest weight)
        scores = {dim: 3.0 for dim in REQUIRED_DIMENSIONS}
        scores["citations"] = 5.0
        with_high_citations = calculate_weighted_average(scores, DEFAULT_WEIGHTS)

        # Methodology should have larger impact than citations
        methodology_impact = with_high_methodology - baseline
        citations_impact = with_high_citations - baseline
        assert methodology_impact > citations_impact

    def test_quality_levels(self):
        """Test quality level classification."""
        level, desc = get_quality_level(4.7)
        assert "exceptional" in level.lower()

        level, desc = get_quality_level(4.2)
        assert "strong" in level.lower()

        level, desc = get_quality_level(3.7)
        assert "good" in level.lower()

        level, desc = get_quality_level(2.5)
        assert "weak" in level.lower()


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_validation_is_deterministic(self):
        """Test that validation produces consistent results."""
        scores = {dim: 4.0 for dim in REQUIRED_DIMENSIONS}
        scores["methodology"] = 6.0  # Invalid

        for _ in range(10):
            result = validate_scores(scores)
            assert not result.is_valid
            assert len(result.errors) == 1
