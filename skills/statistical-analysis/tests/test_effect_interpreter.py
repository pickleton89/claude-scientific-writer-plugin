"""
Tests for the effect size interpreter module.
"""

import pytest

from effect_interpreter import (
    EffectInterpretation,
    convert_cohens_d_to_r,
    convert_or_to_cohens_d,
    convert_r_to_cohens_d,
    get_metric_info,
    interpret_effect_size,
    list_available_metrics,
)


class TestInterpretCohensD:
    """Tests for Cohen's d interpretation."""

    def test_negligible_effect(self):
        """d < 0.01 should be negligible."""
        result = interpret_effect_size(0.005, "cohens_d")
        assert result.magnitude == "negligible"

    def test_very_small_effect(self):
        """0.01 <= d < 0.20 should be very small."""
        result = interpret_effect_size(0.15, "cohens_d")
        assert result.magnitude == "very small"

    def test_small_effect(self):
        """0.20 <= d < 0.50 should be small."""
        result = interpret_effect_size(0.35, "cohens_d")
        assert result.magnitude == "small"

    def test_medium_effect(self):
        """0.50 <= d < 0.80 should be medium."""
        result = interpret_effect_size(0.65, "cohens_d")
        assert result.magnitude == "medium"

    def test_large_effect(self):
        """0.80 <= d < 1.20 should be large."""
        result = interpret_effect_size(1.0, "cohens_d")
        assert result.magnitude == "large"

    def test_very_large_effect(self):
        """1.20 <= d < 2.00 should be very large."""
        result = interpret_effect_size(1.5, "cohens_d")
        assert result.magnitude == "very large"

    def test_huge_effect(self):
        """d >= 2.00 should be huge."""
        result = interpret_effect_size(2.5, "cohens_d")
        assert result.magnitude == "huge"

    def test_negative_value_absolute(self):
        """Negative values should use absolute value for magnitude."""
        result_pos = interpret_effect_size(0.65, "cohens_d")
        result_neg = interpret_effect_size(-0.65, "cohens_d")
        assert result_pos.magnitude == result_neg.magnitude

    def test_direction_positive(self):
        """Positive d should indicate Group 1 > Group 2."""
        result = interpret_effect_size(0.65, "cohens_d")
        assert "Group 1 > Group 2" in result.direction

    def test_direction_negative(self):
        """Negative d should indicate Group 1 < Group 2."""
        result = interpret_effect_size(-0.65, "cohens_d")
        assert "Group 1 < Group 2" in result.direction


class TestInterpretPearsonsR:
    """Tests for Pearson's r interpretation."""

    def test_negligible_correlation(self):
        """r < 0.10 should be negligible."""
        result = interpret_effect_size(0.05, "pearsons_r")
        assert result.magnitude == "negligible"

    def test_weak_correlation(self):
        """0.10 <= r < 0.30 should be weak."""
        result = interpret_effect_size(0.20, "pearsons_r")
        assert result.magnitude == "weak"

    def test_moderate_correlation(self):
        """0.30 <= r < 0.50 should be moderate."""
        result = interpret_effect_size(0.42, "pearsons_r")
        assert result.magnitude == "moderate"

    def test_strong_correlation(self):
        """0.50 <= r < 0.70 should be strong."""
        result = interpret_effect_size(0.60, "pearsons_r")
        assert result.magnitude == "strong"

    def test_very_strong_correlation(self):
        """r >= 0.70 should be very strong."""
        result = interpret_effect_size(0.85, "pearsons_r")
        assert result.magnitude == "very strong"

    def test_negative_correlation(self):
        """Negative r should indicate negative correlation."""
        result = interpret_effect_size(-0.42, "pearsons_r")
        assert "negative" in result.direction.lower()


class TestInterpretEtaSquared:
    """Tests for eta-squared interpretation."""

    def test_negligible_variance(self):
        """eta^2 < 0.01 should be negligible."""
        result = interpret_effect_size(0.005, "eta_squared")
        assert result.magnitude == "negligible"

    def test_small_variance(self):
        """0.01 <= eta^2 < 0.06 should be small."""
        result = interpret_effect_size(0.04, "eta_squared")
        assert result.magnitude == "small"

    def test_medium_variance(self):
        """0.06 <= eta^2 < 0.14 should be medium."""
        result = interpret_effect_size(0.10, "eta_squared")
        assert result.magnitude == "medium"

    def test_large_variance(self):
        """eta^2 >= 0.14 should be large."""
        result = interpret_effect_size(0.20, "eta_squared")
        assert result.magnitude == "large"


class TestInterpretOddsRatio:
    """Tests for odds ratio interpretation."""

    def test_negligible_or(self):
        """OR < 1.5 should be negligible."""
        result = interpret_effect_size(1.2, "odds_ratio")
        assert result.magnitude == "negligible"

    def test_small_or(self):
        """1.5 <= OR < 2.5 should be small."""
        result = interpret_effect_size(2.0, "odds_ratio")
        assert result.magnitude == "small"

    def test_medium_or(self):
        """2.5 <= OR < 4.0 should be medium."""
        result = interpret_effect_size(3.5, "odds_ratio")
        assert result.magnitude == "medium"

    def test_large_or(self):
        """4.0 <= OR < 10.0 should be large."""
        result = interpret_effect_size(6.0, "odds_ratio")
        assert result.magnitude == "large"

    def test_very_large_or(self):
        """OR >= 10.0 should be very large."""
        result = interpret_effect_size(15.0, "odds_ratio")
        assert result.magnitude == "very large"

    def test_protective_or(self):
        """OR < 1 should indicate decreased odds."""
        result = interpret_effect_size(0.5, "odds_ratio")
        assert "decreased" in result.direction.lower()


class TestInterpretLog2FoldChange:
    """Tests for log2 fold change interpretation."""

    def test_negligible_fc(self):
        """|log2FC| < 0.5 should be negligible."""
        result = interpret_effect_size(0.3, "log2_fold_change")
        assert result.magnitude == "negligible"

    def test_small_fc(self):
        """0.5 <= |log2FC| < 1.0 should be small."""
        result = interpret_effect_size(0.7, "log2_fold_change")
        assert result.magnitude == "small"

    def test_medium_fc(self):
        """1.0 <= |log2FC| < 2.0 should be medium."""
        result = interpret_effect_size(1.5, "log2_fold_change")
        assert result.magnitude == "medium"

    def test_large_fc(self):
        """2.0 <= |log2FC| < 3.0 should be large."""
        result = interpret_effect_size(2.5, "log2_fold_change")
        assert result.magnitude == "large"

    def test_upregulated(self):
        """Positive log2FC should indicate upregulation."""
        result = interpret_effect_size(1.5, "log2_fold_change")
        assert "upregulated" in result.direction.lower()

    def test_downregulated(self):
        """Negative log2FC should indicate downregulation."""
        result = interpret_effect_size(-1.5, "log2_fold_change")
        assert "downregulated" in result.direction.lower()


class TestInterpretationOutput:
    """Tests for the output structure."""

    def test_output_structure(self):
        """Output should have all required fields."""
        result = interpret_effect_size(0.65, "cohens_d")
        assert isinstance(result, EffectInterpretation)
        assert result.metric == "cohens_d"
        assert result.metric_full_name == "Cohen's d"
        assert result.value == 0.65
        assert isinstance(result.magnitude, str)
        assert isinstance(result.interpretation, str)
        assert isinstance(result.context, str)
        assert isinstance(result.direction, str)
        assert isinstance(result.confidence_note, str)

    def test_interpretation_contains_value(self):
        """Interpretation should contain the effect size value."""
        result = interpret_effect_size(0.65, "cohens_d")
        assert "0.65" in result.interpretation

    def test_interpretation_contains_magnitude(self):
        """Interpretation should contain the magnitude."""
        result = interpret_effect_size(0.65, "cohens_d")
        assert result.magnitude in result.interpretation


class TestAllMetrics:
    """Tests across all supported metrics."""

    def test_all_metrics_work(self):
        """All metrics should produce valid output."""
        metrics = list_available_metrics()
        test_values = {
            "cohens_d": 0.5,
            "hedges_g": 0.5,
            "pearsons_r": 0.3,
            "spearmans_rho": 0.3,
            "eta_squared": 0.1,
            "partial_eta_squared": 0.1,
            "omega_squared": 0.1,
            "r_squared": 0.2,
            "odds_ratio": 2.0,
            "risk_ratio": 1.5,
            "hazard_ratio": 1.5,
            "cramers_v": 0.3,
            "phi": 0.3,
            "log2_fold_change": 1.0,
            "cohens_h": 0.5,
            "number_needed_to_treat": 10,
            "absolute_risk_reduction": 0.05,
        }

        for metric in metrics:
            value = test_values.get(metric, 0.5)
            result = interpret_effect_size(value, metric)
            assert isinstance(result, EffectInterpretation)
            assert result.metric == metric


class TestValidation:
    """Tests for input validation."""

    def test_invalid_metric_raises(self):
        """Should raise for unknown metric."""
        with pytest.raises(ValueError, match="Unknown metric"):
            interpret_effect_size(0.5, "invalid_metric")  # type: ignore


class TestConversions:
    """Tests for effect size conversions."""

    def test_cohens_d_to_r(self):
        """Convert Cohen's d to r."""
        r = convert_cohens_d_to_r(0.5)
        assert 0 < r < 1
        assert r == pytest.approx(0.243, rel=0.01)

    def test_cohens_d_to_r_zero(self):
        """d=0 should convert to r=0."""
        r = convert_cohens_d_to_r(0)
        assert r == 0

    def test_r_to_cohens_d(self):
        """Convert r to Cohen's d."""
        d = convert_r_to_cohens_d(0.3)
        assert d > 0
        assert d == pytest.approx(0.63, rel=0.01)

    def test_r_to_cohens_d_zero(self):
        """r=0 should convert to d=0."""
        d = convert_r_to_cohens_d(0)
        assert d == 0

    def test_r_to_cohens_d_bounds(self):
        """Should raise for r outside [-1, 1]."""
        with pytest.raises(ValueError):
            convert_r_to_cohens_d(1.5)

    def test_or_to_cohens_d(self):
        """Convert odds ratio to Cohen's d."""
        d = convert_or_to_cohens_d(2.0)
        assert d > 0

    def test_or_to_cohens_d_one(self):
        """OR=1 should convert to d=0."""
        d = convert_or_to_cohens_d(1.0)
        assert d == pytest.approx(0, abs=0.01)

    def test_or_to_cohens_d_invalid(self):
        """Should raise for OR <= 0."""
        with pytest.raises(ValueError):
            convert_or_to_cohens_d(-1)


class TestUtilities:
    """Tests for utility functions."""

    def test_list_available_metrics(self):
        """Should return list of available metrics."""
        metrics = list_available_metrics()
        assert isinstance(metrics, list)
        assert len(metrics) > 0
        assert "cohens_d" in metrics
        assert "pearsons_r" in metrics

    def test_get_metric_info(self):
        """Should return metric info."""
        info = get_metric_info("cohens_d")
        assert "name" in info
        assert "description" in info
        assert "thresholds" in info
        assert info["name"] == "Cohen's d"

    def test_get_metric_info_invalid(self):
        """Should raise for unknown metric."""
        with pytest.raises(ValueError):
            get_metric_info("invalid_metric")  # type: ignore


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_same_input_same_output(self):
        """Same input should always produce same output."""
        results = [
            interpret_effect_size(0.65, "cohens_d")
            for _ in range(10)
        ]

        for i in range(1, len(results)):
            assert results[i].magnitude == results[0].magnitude
            assert results[i].interpretation == results[0].interpretation
            assert results[i].context == results[0].context
            assert results[i].direction == results[0].direction
