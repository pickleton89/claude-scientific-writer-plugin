"""Tests for statistical tests validator module."""

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validators.statistical_tests import (
    DataType,
    GroupStructure,
    StudyDesign,
    TEST_SELECTION,
    recommend_test,
    get_all_tests_for_design,
    get_all_tests_for_data_type,
    validate_test_choice,
    format_recommendation,
)


class TestEnums:
    """Tests for enum types."""

    def test_data_type_values(self):
        """Test DataType enum values."""
        assert DataType.CONTINUOUS.value == "continuous"
        assert DataType.CATEGORICAL.value == "categorical"
        assert DataType.TIME_TO_EVENT.value == "time_to_event"

    def test_group_structure_values(self):
        """Test GroupStructure enum values."""
        assert GroupStructure.TWO_GROUPS.value == "2_groups"
        assert GroupStructure.THREE_PLUS_GROUPS.value == "3+_groups"

    def test_study_design_values(self):
        """Test StudyDesign enum values."""
        assert StudyDesign.INDEPENDENT.value == "independent"
        assert StudyDesign.PAIRED.value == "paired"
        assert StudyDesign.REPEATED.value == "repeated"


class TestTestSelection:
    """Tests for test selection lookup table."""

    def test_selection_not_empty(self):
        """Test that selection table is populated."""
        assert len(TEST_SELECTION) > 0

    def test_all_recommendations_have_required_fields(self):
        """Test that all recommendations have required fields."""
        for key, rec in TEST_SELECTION.items():
            assert rec.test_name
            assert len(rec.assumptions) > 0
            assert rec.when_to_use

    def test_two_sample_tests_exist(self):
        """Test that two-sample tests exist."""
        rec = TEST_SELECTION.get(("continuous", "2_groups", "independent", "normal"))
        assert rec is not None
        assert "t-test" in rec.test_name.lower()

    def test_paired_tests_exist(self):
        """Test that paired tests exist."""
        rec = TEST_SELECTION.get(("continuous", "2_groups", "paired", "normal"))
        assert rec is not None
        assert "paired" in rec.test_name.lower()


class TestRecommendTest:
    """Tests for recommend_test function."""

    def test_independent_t_test(self):
        """Test recommendation for independent t-test scenario."""
        rec = recommend_test("continuous", "2_groups", "independent", "normal")
        assert rec is not None
        assert "t-test" in rec.test_name.lower()
        assert "independent" in rec.test_name.lower()

    def test_mann_whitney(self):
        """Test recommendation for Mann-Whitney scenario."""
        rec = recommend_test("continuous", "2_groups", "independent", "non_normal")
        assert rec is not None
        assert "mann-whitney" in rec.test_name.lower()

    def test_paired_t_test(self):
        """Test recommendation for paired t-test scenario."""
        rec = recommend_test("continuous", "2_groups", "paired", "normal")
        assert rec is not None
        assert "paired" in rec.test_name.lower()

    def test_wilcoxon(self):
        """Test recommendation for Wilcoxon scenario."""
        rec = recommend_test("continuous", "2_groups", "paired", "non_normal")
        assert rec is not None
        assert "wilcoxon" in rec.test_name.lower()

    def test_anova(self):
        """Test recommendation for ANOVA scenario."""
        rec = recommend_test("continuous", "3+_groups", "independent", "normal")
        assert rec is not None
        assert "anova" in rec.test_name.lower()

    def test_kruskal_wallis(self):
        """Test recommendation for Kruskal-Wallis scenario."""
        rec = recommend_test("continuous", "3+_groups", "independent", "non_normal")
        assert rec is not None
        assert "kruskal" in rec.test_name.lower()

    def test_chi_square(self):
        """Test recommendation for chi-square scenario."""
        rec = recommend_test("categorical", "2_groups", "independent", "unknown")
        assert rec is not None
        assert "chi-square" in rec.test_name.lower()

    def test_log_rank(self):
        """Test recommendation for survival analysis."""
        rec = recommend_test("time_to_event", "2_groups", "independent", "unknown")
        assert rec is not None
        assert "log-rank" in rec.test_name.lower()

    def test_correlation_normal(self):
        """Test recommendation for correlation (normal)."""
        rec = recommend_test("continuous", "correlation", "independent", "normal")
        assert rec is not None
        assert "pearson" in rec.test_name.lower()

    def test_correlation_non_normal(self):
        """Test recommendation for correlation (non-normal)."""
        rec = recommend_test("continuous", "correlation", "independent", "non_normal")
        assert rec is not None
        assert "spearman" in rec.test_name.lower()

    def test_nonexistent_combination(self):
        """Test that nonexistent combinations return None."""
        rec = recommend_test("unknown", "unknown", "unknown", "unknown")
        assert rec is None

    def test_case_insensitive(self):
        """Test that lookup is case-insensitive."""
        rec1 = recommend_test("continuous", "2_groups", "independent", "normal")
        rec2 = recommend_test("CONTINUOUS", "2_GROUPS", "INDEPENDENT", "NORMAL")
        assert rec1 == rec2


class TestGetAllTestsForDesign:
    """Tests for get_all_tests_for_design function."""

    def test_get_independent_tests(self):
        """Test getting all independent tests."""
        tests = get_all_tests_for_design("independent")
        assert len(tests) >= 5
        # Should include t-test, Mann-Whitney, ANOVA, chi-square, etc.

    def test_get_paired_tests(self):
        """Test getting all paired tests."""
        tests = get_all_tests_for_design("paired")
        assert len(tests) >= 2

    def test_get_repeated_tests(self):
        """Test getting all repeated measures tests."""
        tests = get_all_tests_for_design("repeated")
        assert len(tests) >= 2


class TestGetAllTestsForDataType:
    """Tests for get_all_tests_for_data_type function."""

    def test_get_continuous_tests(self):
        """Test getting all continuous data tests."""
        tests = get_all_tests_for_data_type("continuous")
        assert len(tests) >= 8

    def test_get_categorical_tests(self):
        """Test getting all categorical data tests."""
        tests = get_all_tests_for_data_type("categorical")
        assert len(tests) >= 2


class TestValidateTestChoice:
    """Tests for validate_test_choice function."""

    def test_valid_t_test_choice(self):
        """Test validating correct t-test choice."""
        valid, msg, rec = validate_test_choice(
            "t-test", "continuous", "2_groups", "independent", "normal"
        )
        assert valid
        assert rec is not None

    def test_valid_alternative_choice(self):
        """Test validating valid alternative test choice."""
        # Welch's t-test is listed as an alternative
        valid, msg, rec = validate_test_choice(
            "Welch", "continuous", "2_groups", "independent", "normal"
        )
        assert valid
        assert "alternative" in msg.lower() or "appropriate" in msg.lower()

    def test_invalid_test_choice(self):
        """Test detecting invalid test choice."""
        valid, msg, rec = validate_test_choice(
            "ANOVA", "continuous", "2_groups", "independent", "normal"
        )
        assert not valid
        assert "consider" in msg.lower()

    def test_mann_whitney_for_normal_data(self):
        """Test Mann-Whitney as alternative for normal data."""
        valid, msg, rec = validate_test_choice(
            "Mann-Whitney U", "continuous", "2_groups", "independent", "normal"
        )
        # Mann-Whitney is listed as an alternative to t-test
        assert valid

    def test_invalid_combination(self):
        """Test handling of invalid data combination."""
        valid, msg, rec = validate_test_choice(
            "t-test", "unknown", "unknown", "unknown", "unknown"
        )
        assert not valid
        assert "no recommendation" in msg.lower()


class TestFormatRecommendation:
    """Tests for format_recommendation function."""

    def test_format_basic(self):
        """Test basic formatting."""
        rec = recommend_test("continuous", "2_groups", "independent", "normal")
        formatted = format_recommendation(rec)

        assert "Independent t-test" in formatted
        assert "When to use:" in formatted
        assert "Assumptions:" in formatted

    def test_format_includes_alternatives(self):
        """Test that formatting includes alternatives."""
        rec = recommend_test("continuous", "2_groups", "independent", "normal")
        formatted = format_recommendation(rec)

        assert "Alternatives" in formatted
        assert "Welch" in formatted or "Mann-Whitney" in formatted

    def test_format_includes_reporting(self):
        """Test that formatting includes reporting requirements."""
        rec = recommend_test("continuous", "2_groups", "independent", "normal")
        formatted = format_recommendation(rec)

        assert "Reporting" in formatted

    def test_format_includes_common_mistakes(self):
        """Test that formatting includes common mistakes."""
        rec = recommend_test("continuous", "2_groups", "independent", "normal")
        formatted = format_recommendation(rec)

        assert "mistakes" in formatted.lower() or "avoid" in formatted.lower()


class TestRecommendationCompleteness:
    """Tests for recommendation field completeness."""

    def test_all_have_assumptions(self):
        """Test all recommendations have assumptions."""
        for key, rec in TEST_SELECTION.items():
            assert len(rec.assumptions) >= 2, f"{key} has too few assumptions"

    def test_all_have_alternatives(self):
        """Test all recommendations have alternatives."""
        for key, rec in TEST_SELECTION.items():
            assert len(rec.alternatives) >= 1, f"{key} has no alternatives"

    def test_reporting_requirements_exist(self):
        """Test that key tests have reporting requirements."""
        rec = recommend_test("continuous", "2_groups", "independent", "normal")
        assert len(rec.reporting_requirements) >= 4


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_recommendation_is_deterministic(self):
        """Test that recommendations are deterministic."""
        for _ in range(10):
            rec1 = recommend_test("continuous", "2_groups", "independent", "normal")
            rec2 = recommend_test("continuous", "2_groups", "independent", "normal")
            assert rec1 == rec2

    def test_validation_is_deterministic(self):
        """Test that validation is deterministic."""
        for _ in range(10):
            valid1, msg1, _ = validate_test_choice(
                "t-test", "continuous", "2_groups", "independent", "normal"
            )
            valid2, msg2, _ = validate_test_choice(
                "t-test", "continuous", "2_groups", "independent", "normal"
            )
            assert valid1 == valid2
            assert msg1 == msg2
