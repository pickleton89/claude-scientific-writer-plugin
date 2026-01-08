"""
Tests for the deterministic test selector module.
"""

import pytest

from test_selector import (
    Design,
    Distribution,
    OutcomeType,
    TestRecommendation,
    get_post_hoc_code,
    list_available_tests,
    select_correlation_test,
    select_test,
)


class TestSelectTestContinuous:
    """Tests for continuous outcome test selection."""

    def test_two_groups_normal_independent_equal_variance(self):
        """Student's t-test for normal, equal variance, independent."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
            variance_equal=True,
        )
        assert result.test_name == "Student's t-test"
        assert result.parametric is True
        assert "equal variances" in result.assumptions

    def test_two_groups_normal_independent_unequal_variance(self):
        """Welch's t-test for normal, unequal variance, independent."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
            variance_equal=False,
        )
        assert result.test_name == "Welch's t-test"
        assert result.parametric is True
        assert "Welch" in result.notes or "unequal" in (result.notes or "").lower()

    def test_two_groups_nonnormal_independent(self):
        """Mann-Whitney U for non-normal, independent."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NON_NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
        )
        assert result.test_name == "Mann-Whitney U"
        assert result.parametric is False
        assert "rank-biserial" in result.effect_size_metric

    def test_two_groups_normal_paired(self):
        """Paired t-test for normal, paired."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.PAIRED,
            n_groups=2,
        )
        assert result.test_name == "Paired t-test"
        assert result.parametric is True

    def test_two_groups_nonnormal_paired(self):
        """Wilcoxon signed-rank for non-normal, paired."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NON_NORMAL,
            design=Design.PAIRED,
            n_groups=2,
        )
        assert result.test_name == "Wilcoxon signed-rank"
        assert result.parametric is False

    def test_three_groups_normal_independent_equal_variance(self):
        """One-way ANOVA for 3+ groups, normal, equal variance."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=3,
            variance_equal=True,
        )
        assert result.test_name == "One-way ANOVA"
        assert result.parametric is True
        assert result.post_hoc == "Tukey HSD"

    def test_three_groups_normal_independent_unequal_variance(self):
        """Welch's ANOVA for 3+ groups, normal, unequal variance."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=3,
            variance_equal=False,
        )
        assert result.test_name == "Welch's ANOVA"
        assert result.parametric is True
        assert result.post_hoc == "Games-Howell"

    def test_three_groups_nonnormal_independent(self):
        """Kruskal-Wallis for 3+ groups, non-normal."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NON_NORMAL,
            design=Design.INDEPENDENT,
            n_groups=4,
        )
        assert result.test_name == "Kruskal-Wallis"
        assert result.parametric is False
        assert "Dunn" in result.post_hoc

    def test_three_groups_normal_repeated(self):
        """Repeated measures ANOVA."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.REPEATED_MEASURES,
            n_groups=3,
        )
        assert result.test_name == "Repeated measures ANOVA"
        assert result.parametric is True

    def test_three_groups_nonnormal_repeated(self):
        """Friedman test."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NON_NORMAL,
            design=Design.REPEATED_MEASURES,
            n_groups=3,
        )
        assert result.test_name == "Friedman test"
        assert result.parametric is False

    def test_one_group_normal(self):
        """One-sample t-test."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=1,
        )
        assert result.test_name == "One-sample t-test"
        assert result.parametric is True

    def test_one_group_nonnormal(self):
        """One-sample Wilcoxon."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NON_NORMAL,
            design=Design.INDEPENDENT,
            n_groups=1,
        )
        assert "Wilcoxon" in result.test_name
        assert result.parametric is False


class TestSelectTestCategorical:
    """Tests for categorical outcome test selection."""

    def test_chi_square_sufficient_counts(self):
        """Chi-square test when expected counts >= 5."""
        result = select_test(
            outcome_type=OutcomeType.CATEGORICAL,
            distribution=Distribution.NORMAL,  # Ignored for categorical
            design=Design.INDEPENDENT,
            n_groups=2,
            expected_counts_sufficient=True,
        )
        assert result.test_name == "Chi-square test"
        assert "Cramer" in result.effect_size_metric

    def test_fisher_exact_insufficient_counts(self):
        """Fisher's exact test when expected counts < 5."""
        result = select_test(
            outcome_type=OutcomeType.CATEGORICAL,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
            expected_counts_sufficient=False,
        )
        assert result.test_name == "Fisher's exact test"
        assert "odds ratio" in result.effect_size_metric

    def test_chi_square_multiple_groups(self):
        """Chi-square for independence with 3+ groups."""
        result = select_test(
            outcome_type=OutcomeType.CATEGORICAL,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=4,
        )
        assert "Chi-square" in result.test_name
        assert result.post_hoc is not None

    def test_mcnemar_paired(self):
        """McNemar's test for paired categorical."""
        result = select_test(
            outcome_type=OutcomeType.CATEGORICAL,
            distribution=Distribution.NORMAL,
            design=Design.PAIRED,
            n_groups=2,
        )
        assert result.test_name == "McNemar's test"


class TestSelectTestOrdinal:
    """Tests for ordinal outcome test selection."""

    def test_ordinal_two_groups(self):
        """Mann-Whitney U for ordinal, 2 groups."""
        result = select_test(
            outcome_type=OutcomeType.ORDINAL,
            distribution=Distribution.NON_NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
        )
        assert result.test_name == "Mann-Whitney U"

    def test_ordinal_multiple_groups(self):
        """Kruskal-Wallis for ordinal, 3+ groups."""
        result = select_test(
            outcome_type=OutcomeType.ORDINAL,
            distribution=Distribution.NON_NORMAL,
            design=Design.INDEPENDENT,
            n_groups=3,
        )
        assert result.test_name == "Kruskal-Wallis"

    def test_ordinal_paired_two_groups(self):
        """Wilcoxon for paired ordinal."""
        result = select_test(
            outcome_type=OutcomeType.ORDINAL,
            distribution=Distribution.NON_NORMAL,
            design=Design.PAIRED,
            n_groups=2,
        )
        assert "Wilcoxon" in result.test_name

    def test_ordinal_paired_multiple_groups(self):
        """Friedman for paired ordinal, 3+ groups."""
        result = select_test(
            outcome_type=OutcomeType.ORDINAL,
            distribution=Distribution.NON_NORMAL,
            design=Design.PAIRED,
            n_groups=3,
        )
        assert result.test_name == "Friedman test"


class TestSelectTestSurvival:
    """Tests for time-to-event outcome test selection."""

    def test_survival_two_groups(self):
        """Log-rank test for survival."""
        result = select_test(
            outcome_type=OutcomeType.TIME_TO_EVENT,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
        )
        assert "Log-rank" in result.test_name or "Kaplan" in result.test_name
        assert "hazard ratio" in result.effect_size_metric


class TestSelectTestProportion:
    """Tests for proportion outcome test selection."""

    def test_proportion_two_groups(self):
        """Z-test for two proportions."""
        result = select_test(
            outcome_type=OutcomeType.PROPORTION,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
        )
        assert "proportion" in result.test_name.lower() or "Z-test" in result.test_name


class TestSelectCorrelationTest:
    """Tests for correlation test selection."""

    def test_pearson_normal(self):
        """Pearson for normal data."""
        result = select_correlation_test(
            distribution=Distribution.NORMAL,
            ordinal=False,
        )
        assert result.test_name == "Pearson correlation"
        assert result.parametric is True

    def test_spearman_nonnormal(self):
        """Spearman for non-normal data."""
        result = select_correlation_test(
            distribution=Distribution.NON_NORMAL,
            ordinal=False,
        )
        assert result.test_name == "Spearman correlation"
        assert result.parametric is False

    def test_spearman_ordinal(self):
        """Spearman for ordinal data."""
        result = select_correlation_test(
            distribution=Distribution.NORMAL,
            ordinal=True,
        )
        assert result.test_name == "Spearman correlation"

    def test_kendall_tied_ranks(self):
        """Kendall's tau for tied ranks."""
        result = select_correlation_test(
            distribution=Distribution.NON_NORMAL,
            ordinal=False,
            tied_ranks=True,
        )
        assert result.test_name == "Kendall's tau"


class TestTestRecommendationOutput:
    """Tests for TestRecommendation output structure."""

    def test_recommendation_has_python_code(self):
        """All recommendations should have Python code."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
        )
        assert result.python_code is not None
        assert len(result.python_code) > 0
        assert "import" in result.python_code or "from" in result.python_code

    def test_recommendation_has_r_code(self):
        """All recommendations should have R code."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
        )
        assert result.r_code is not None
        assert len(result.r_code) > 0

    def test_recommendation_has_effect_size(self):
        """All recommendations should have effect size metric."""
        result = select_test(
            outcome_type=OutcomeType.CONTINUOUS,
            distribution=Distribution.NORMAL,
            design=Design.INDEPENDENT,
            n_groups=2,
        )
        assert result.effect_size_metric is not None
        assert len(result.effect_size_metric) > 0


class TestValidation:
    """Tests for input validation."""

    def test_invalid_n_groups(self):
        """Should raise error for n_groups < 1."""
        with pytest.raises(ValueError, match="n_groups must be >= 1"):
            select_test(
                outcome_type=OutcomeType.CONTINUOUS,
                distribution=Distribution.NORMAL,
                design=Design.INDEPENDENT,
                n_groups=0,
            )


class TestUtilities:
    """Tests for utility functions."""

    def test_list_available_tests(self):
        """Should return list of available tests."""
        tests = list_available_tests()
        assert isinstance(tests, list)
        assert len(tests) > 0
        assert "welch_t_test" in tests

    def test_get_post_hoc_code_python(self):
        """Should return post-hoc code for Python."""
        code = get_post_hoc_code("one_way_anova", "python")
        assert code is not None
        assert "tukey" in code.lower() or "Tukey" in code

    def test_get_post_hoc_code_r(self):
        """Should return post-hoc code for R."""
        code = get_post_hoc_code("one_way_anova", "r")
        assert code is not None

    def test_get_post_hoc_code_unknown(self):
        """Should return None for unknown test."""
        code = get_post_hoc_code("unknown_test", "python")
        assert code is None


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_same_input_same_output(self):
        """Same input should always produce same output."""
        inputs = {
            "outcome_type": OutcomeType.CONTINUOUS,
            "distribution": Distribution.NORMAL,
            "design": Design.INDEPENDENT,
            "n_groups": 2,
            "variance_equal": False,
        }

        results = [select_test(**inputs) for _ in range(10)]

        # All results should be identical
        for i in range(1, len(results)):
            assert results[i].test_name == results[0].test_name
            assert results[i].parametric == results[0].parametric
            assert results[i].assumptions == results[0].assumptions
            assert results[i].python_code == results[0].python_code
            assert results[i].r_code == results[0].r_code
