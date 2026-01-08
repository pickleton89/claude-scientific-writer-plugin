"""
Tests for the validators module.
"""

import pytest

from validators import (
    ValidationResult,
    validate_effect_size_input,
    validate_enum,
    validate_mtc_input,
    validate_numeric_range,
    validate_power_analysis_input,
    validate_test_selection_input,
)


class TestValidateTestSelectionInput:
    """Tests for test selection input validation."""

    def test_valid_continuous_normal(self, test_selection_continuous_normal):
        """Valid continuous normal input should pass."""
        result = validate_test_selection_input(test_selection_continuous_normal)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_valid_categorical(self, test_selection_categorical):
        """Valid categorical input should pass."""
        result = validate_test_selection_input(test_selection_categorical)
        assert result.valid is True

    def test_missing_outcome_type(self):
        """Missing outcome_type should fail."""
        result = validate_test_selection_input({
            "design": "independent",
            "n_groups": 2,
        })
        assert result.valid is False
        assert any("outcome_type" in e for e in result.errors)

    def test_missing_design(self):
        """Missing design should fail."""
        result = validate_test_selection_input({
            "outcome_type": "continuous",
            "distribution": "normal",
            "n_groups": 2,
        })
        assert result.valid is False
        assert any("design" in e for e in result.errors)

    def test_missing_n_groups(self):
        """Missing n_groups should fail."""
        result = validate_test_selection_input({
            "outcome_type": "continuous",
            "distribution": "normal",
            "design": "independent",
        })
        assert result.valid is False
        assert any("n_groups" in e for e in result.errors)

    def test_missing_distribution_for_continuous(self):
        """Missing distribution for continuous should fail."""
        result = validate_test_selection_input({
            "outcome_type": "continuous",
            "design": "independent",
            "n_groups": 2,
        })
        assert result.valid is False
        assert any("distribution" in e for e in result.errors)

    def test_invalid_outcome_type(self):
        """Invalid outcome_type should fail."""
        result = validate_test_selection_input({
            "outcome_type": "invalid",
            "distribution": "normal",
            "design": "independent",
            "n_groups": 2,
        })
        assert result.valid is False
        assert any("outcome_type" in e for e in result.errors)

    def test_invalid_distribution(self):
        """Invalid distribution should fail."""
        result = validate_test_selection_input({
            "outcome_type": "continuous",
            "distribution": "invalid",
            "design": "independent",
            "n_groups": 2,
        })
        assert result.valid is False
        assert any("distribution" in e for e in result.errors)

    def test_invalid_design(self):
        """Invalid design should fail."""
        result = validate_test_selection_input({
            "outcome_type": "continuous",
            "distribution": "normal",
            "design": "invalid",
            "n_groups": 2,
        })
        assert result.valid is False
        assert any("design" in e for e in result.errors)

    def test_invalid_n_groups(self):
        """Invalid n_groups should fail."""
        result = validate_test_selection_input({
            "outcome_type": "continuous",
            "distribution": "normal",
            "design": "independent",
            "n_groups": 0,
        })
        assert result.valid is False
        assert any("n_groups" in e for e in result.errors)

    def test_non_integer_n_groups(self):
        """Non-integer n_groups should fail."""
        result = validate_test_selection_input({
            "outcome_type": "continuous",
            "distribution": "normal",
            "design": "independent",
            "n_groups": "two",
        })
        assert result.valid is False
        assert any("n_groups" in e for e in result.errors)

    def test_case_insensitive(self):
        """Values should be case-insensitive."""
        result = validate_test_selection_input({
            "outcome_type": "CONTINUOUS",
            "distribution": "Normal",
            "design": "INDEPENDENT",
            "n_groups": 2,
        })
        assert result.valid is True
        assert result.normalized_input["outcome_type"] == "continuous"

    def test_normalization(self):
        """Should normalize input values."""
        result = validate_test_selection_input({
            "outcome_type": "  Continuous  ",
            "distribution": "NORMAL",
            "design": "independent",
            "n_groups": "2",
        })
        assert result.valid is True
        assert result.normalized_input["outcome_type"] == "continuous"
        assert result.normalized_input["distribution"] == "normal"
        assert result.normalized_input["n_groups"] == 2

    def test_optional_variance_equal(self):
        """Optional variance_equal should be normalized."""
        result = validate_test_selection_input({
            "outcome_type": "continuous",
            "distribution": "normal",
            "design": "independent",
            "n_groups": 2,
            "variance_equal": "True",
        })
        assert result.valid is True
        assert result.normalized_input["variance_equal"] is True


class TestValidateMTCInput:
    """Tests for MTC input validation."""

    def test_valid_input(self, sample_pvalues):
        """Valid input should pass."""
        result = validate_mtc_input({
            "pvalues": sample_pvalues,
            "method": "bh_fdr",
        })
        assert result.valid is True

    def test_missing_pvalues(self):
        """Missing pvalues should fail."""
        result = validate_mtc_input({
            "method": "bh_fdr",
        })
        assert result.valid is False
        assert any("pvalues" in e for e in result.errors)

    def test_empty_pvalues(self):
        """Empty pvalues should fail."""
        result = validate_mtc_input({
            "pvalues": [],
        })
        assert result.valid is False
        assert any("empty" in e.lower() for e in result.errors)

    def test_invalid_pvalue_range(self):
        """P-values outside [0,1] should fail."""
        result = validate_mtc_input({
            "pvalues": [0.05, 1.5],
        })
        assert result.valid is False
        assert any("range" in e.lower() for e in result.errors)

    def test_negative_pvalue(self):
        """Negative p-values should fail."""
        result = validate_mtc_input({
            "pvalues": [-0.1, 0.5],
        })
        assert result.valid is False

    def test_invalid_method(self):
        """Invalid method should fail."""
        result = validate_mtc_input({
            "pvalues": [0.05, 0.10],
            "method": "invalid",
        })
        assert result.valid is False
        assert any("method" in e.lower() for e in result.errors)

    def test_invalid_alpha(self):
        """Invalid alpha should fail."""
        result = validate_mtc_input({
            "pvalues": [0.05],
            "alpha": 1.5,
        })
        assert result.valid is False
        assert any("alpha" in e.lower() for e in result.errors)

    def test_default_method(self):
        """Should default to bh_fdr."""
        result = validate_mtc_input({
            "pvalues": [0.05],
        })
        assert result.valid is True
        assert result.normalized_input["method"] == "bh_fdr"

    def test_default_alpha(self):
        """Should default to 0.05."""
        result = validate_mtc_input({
            "pvalues": [0.05],
        })
        assert result.valid is True
        assert result.normalized_input["alpha"] == 0.05

    def test_warning_identical_pvalues(self):
        """Should warn for identical p-values."""
        result = validate_mtc_input({
            "pvalues": [0.5, 0.5, 0.5],
        })
        assert result.valid is True
        assert any("identical" in w.lower() for w in result.warnings)


class TestValidatePowerAnalysisInput:
    """Tests for power analysis input validation."""

    def test_valid_calculate_n(self):
        """Valid input for calculating n should pass."""
        result = validate_power_analysis_input({
            "test_type": "t_test",
            "effect_size": 0.5,
            "power": 0.8,
        })
        assert result.valid is True

    def test_valid_calculate_power(self):
        """Valid input for calculating power should pass."""
        result = validate_power_analysis_input({
            "test_type": "t_test",
            "effect_size": 0.5,
            "n_per_group": 30,
        })
        assert result.valid is True

    def test_valid_calculate_effect(self):
        """Valid input for calculating effect size should pass."""
        result = validate_power_analysis_input({
            "test_type": "t_test",
            "power": 0.8,
            "n_per_group": 30,
        })
        assert result.valid is True

    def test_missing_test_type(self):
        """Missing test_type should fail."""
        result = validate_power_analysis_input({
            "effect_size": 0.5,
            "power": 0.8,
        })
        assert result.valid is False
        assert any("test_type" in e for e in result.errors)

    def test_invalid_test_type(self):
        """Invalid test_type should fail."""
        result = validate_power_analysis_input({
            "test_type": "invalid",
            "effect_size": 0.5,
            "power": 0.8,
        })
        assert result.valid is False
        assert any("test_type" in e for e in result.errors)

    def test_no_none_values(self):
        """Should fail when no values are None."""
        result = validate_power_analysis_input({
            "test_type": "t_test",
            "effect_size": 0.5,
            "power": 0.8,
            "n_per_group": 30,
        })
        assert result.valid is False
        assert any("Exactly one" in e for e in result.errors)

    def test_all_none_values(self):
        """Should fail when all optional values are None."""
        result = validate_power_analysis_input({
            "test_type": "t_test",
        })
        assert result.valid is False
        assert any("Exactly one" in e for e in result.errors)

    def test_negative_effect_size(self):
        """Negative effect size should fail."""
        result = validate_power_analysis_input({
            "test_type": "t_test",
            "effect_size": -0.5,
            "power": 0.8,
        })
        assert result.valid is False
        assert any("effect_size" in e for e in result.errors)

    def test_invalid_power(self):
        """Power outside (0,1) should fail."""
        result = validate_power_analysis_input({
            "test_type": "t_test",
            "effect_size": 0.5,
            "power": 1.5,
        })
        assert result.valid is False
        assert any("power" in e for e in result.errors)

    def test_small_n_per_group(self):
        """n_per_group < 2 should fail."""
        result = validate_power_analysis_input({
            "test_type": "t_test",
            "effect_size": 0.5,
            "power": None,
            "n_per_group": 1,
        })
        assert result.valid is False
        assert any("n_per_group" in e for e in result.errors)

    def test_chi_square_requires_df(self):
        """chi_square should require df."""
        result = validate_power_analysis_input({
            "test_type": "chi_square",
            "effect_size": 0.3,
            "power": 0.8,
        })
        assert result.valid is False
        assert any("df" in e for e in result.errors)

    def test_anova_requires_n_groups(self):
        """ANOVA should default n_groups to 2 but accept custom."""
        result = validate_power_analysis_input({
            "test_type": "anova",
            "effect_size": 0.25,
            "power": 0.8,
            "n_groups": 3,
        })
        assert result.valid is True
        assert result.normalized_input["n_groups"] == 3

    def test_warning_low_power(self):
        """Should warn for power < 0.8."""
        result = validate_power_analysis_input({
            "test_type": "t_test",
            "effect_size": 0.5,
            "power": 0.6,
        })
        assert result.valid is True
        assert any("below" in w.lower() or "0.8" in w for w in result.warnings)


class TestValidateEffectSizeInput:
    """Tests for effect size input validation."""

    def test_valid_input(self):
        """Valid input should pass."""
        result = validate_effect_size_input({
            "value": 0.65,
            "metric": "cohens_d",
        })
        assert result.valid is True

    def test_missing_value(self):
        """Missing value should fail."""
        result = validate_effect_size_input({
            "metric": "cohens_d",
        })
        assert result.valid is False
        assert any("value" in e for e in result.errors)

    def test_missing_metric(self):
        """Missing metric should fail."""
        result = validate_effect_size_input({
            "value": 0.65,
        })
        assert result.valid is False
        assert any("metric" in e for e in result.errors)

    def test_invalid_metric(self):
        """Invalid metric should fail."""
        result = validate_effect_size_input({
            "value": 0.65,
            "metric": "invalid",
        })
        assert result.valid is False
        assert any("metric" in e for e in result.errors)

    def test_correlation_bounds(self):
        """Correlation values outside [-1,1] should fail."""
        result = validate_effect_size_input({
            "value": 1.5,
            "metric": "pearsons_r",
        })
        assert result.valid is False

    def test_eta_squared_bounds(self):
        """eta_squared outside [0,1] should fail."""
        result = validate_effect_size_input({
            "value": -0.1,
            "metric": "eta_squared",
        })
        assert result.valid is False

    def test_odds_ratio_positive(self):
        """Odds ratio must be positive."""
        result = validate_effect_size_input({
            "value": -1.0,
            "metric": "odds_ratio",
        })
        assert result.valid is False

    def test_warning_extreme_value(self):
        """Should warn for extreme effect sizes."""
        result = validate_effect_size_input({
            "value": 15.0,
            "metric": "cohens_d",
        })
        assert result.valid is True
        assert any("large" in w.lower() or "extreme" in w.lower() or "unusual" in w.lower()
                   for w in result.warnings)


class TestUtilityFunctions:
    """Tests for utility validation functions."""

    def test_validate_numeric_range_valid(self):
        """Valid numeric value should pass."""
        value, error = validate_numeric_range(0.5, min_val=0, max_val=1)
        assert value == 0.5
        assert error is None

    def test_validate_numeric_range_below_min(self):
        """Value below min should fail."""
        value, error = validate_numeric_range(-0.1, min_val=0)
        assert value is None
        assert error is not None

    def test_validate_numeric_range_above_max(self):
        """Value above max should fail."""
        value, error = validate_numeric_range(1.5, max_val=1)
        assert value is None
        assert error is not None

    def test_validate_numeric_range_exclusive(self):
        """Exclusive bounds should work correctly."""
        value, error = validate_numeric_range(0, min_val=0, exclusive_min=True)
        assert value is None
        assert error is not None

        value, error = validate_numeric_range(1, max_val=1, exclusive_max=True)
        assert value is None
        assert error is not None

    def test_validate_enum_valid(self):
        """Valid enum value should pass."""
        value, error = validate_enum("normal", {"normal", "non_normal"})
        assert value == "normal"
        assert error is None

    def test_validate_enum_invalid(self):
        """Invalid enum value should fail."""
        value, error = validate_enum("invalid", {"normal", "non_normal"})
        assert value is None
        assert error is not None

    def test_validate_enum_case_insensitive(self):
        """Enum validation should be case-insensitive."""
        value, error = validate_enum("NORMAL", {"normal", "non_normal"})
        assert value == "normal"
        assert error is None
