"""
Tests for the power calculator module.
"""

import pytest

from power_calculator import (
    PowerResult,
    get_effect_size_conventions,
    power_analysis,
    sample_size_table,
    suggest_effect_size,
)


class TestPowerAnalysisTTest:
    """Tests for t-test power analysis."""

    def test_calculate_sample_size(self):
        """Calculate required sample size."""
        result = power_analysis(
            test_type="t_test",
            effect_size=0.5,
            power=0.8,
            n_per_group=None,
        )
        assert isinstance(result, PowerResult)
        assert result.calculated_param == "n_per_group"
        assert result.n_per_group > 0
        assert result.n_total == result.n_per_group * 2

    def test_calculate_power(self):
        """Calculate power for given sample size."""
        result = power_analysis(
            test_type="t_test",
            effect_size=0.5,
            power=None,
            n_per_group=30,
        )
        assert result.calculated_param == "power"
        assert 0 < result.power < 1

    def test_calculate_effect_size(self):
        """Calculate minimum detectable effect size."""
        result = power_analysis(
            test_type="t_test",
            effect_size=None,
            power=0.8,
            n_per_group=64,
        )
        assert result.calculated_param == "effect_size"
        assert result.effect_size > 0

    def test_medium_effect_sample_size(self):
        """Medium effect (d=0.5) with 80% power should require ~64 per group."""
        result = power_analysis(
            test_type="t_test",
            effect_size=0.5,
            power=0.8,
        )
        # Cohen (1988) recommends n=64 per group for d=0.5, power=0.8
        assert 60 <= result.n_per_group <= 70

    def test_small_effect_needs_more_samples(self):
        """Smaller effect should require larger sample."""
        small = power_analysis(test_type="t_test", effect_size=0.2, power=0.8)
        medium = power_analysis(test_type="t_test", effect_size=0.5, power=0.8)
        assert small.n_per_group > medium.n_per_group

    def test_higher_power_needs_more_samples(self):
        """Higher power should require larger sample."""
        power_80 = power_analysis(test_type="t_test", effect_size=0.5, power=0.8)
        power_90 = power_analysis(test_type="t_test", effect_size=0.5, power=0.9)
        assert power_90.n_per_group > power_80.n_per_group


class TestPowerAnalysisPairedTTest:
    """Tests for paired t-test power analysis."""

    def test_calculate_sample_size(self):
        """Calculate required sample size for paired test."""
        result = power_analysis(
            test_type="paired_t_test",
            effect_size=0.5,
            power=0.8,
        )
        assert result.test_type == "paired_t_test"
        assert result.n_per_group > 0
        # Paired test should need fewer subjects than independent
        independent = power_analysis(test_type="t_test", effect_size=0.5, power=0.8)
        assert result.n_per_group <= independent.n_per_group


class TestPowerAnalysisANOVA:
    """Tests for ANOVA power analysis."""

    def test_calculate_sample_size(self):
        """Calculate required sample size for ANOVA."""
        result = power_analysis(
            test_type="anova",
            effect_size=0.25,  # Cohen's f for medium effect
            power=0.8,
            n_groups=3,
        )
        assert result.test_type == "anova"
        assert result.n_per_group > 0
        assert result.n_total == result.n_per_group * 3

    def test_more_groups_needs_more_samples(self):
        """More groups should generally require more total samples."""
        three_groups = power_analysis(
            test_type="anova", effect_size=0.25, power=0.8, n_groups=3
        )
        four_groups = power_analysis(
            test_type="anova", effect_size=0.25, power=0.8, n_groups=4
        )
        # Total n should be higher with more groups
        assert four_groups.n_total >= three_groups.n_total


class TestPowerAnalysisCorrelation:
    """Tests for correlation power analysis."""

    def test_calculate_sample_size(self):
        """Calculate required sample size for correlation."""
        result = power_analysis(
            test_type="correlation",
            effect_size=0.3,  # Medium correlation
            power=0.8,
        )
        assert result.test_type == "correlation"
        assert result.n_per_group > 0


class TestPowerAnalysisChiSquare:
    """Tests for chi-square power analysis."""

    def test_calculate_sample_size(self):
        """Calculate required sample size for chi-square."""
        result = power_analysis(
            test_type="chi_square",
            effect_size=0.3,  # Cohen's w for medium effect
            power=0.8,
            df=2,
        )
        assert result.test_type == "chi_square"
        assert result.n_per_group > 0

    def test_df_required(self):
        """Should raise error if df not provided."""
        with pytest.raises(ValueError, match="df"):
            power_analysis(
                test_type="chi_square",
                effect_size=0.3,
                power=0.8,
            )


class TestPowerAnalysisProportion:
    """Tests for proportion power analysis."""

    def test_calculate_sample_size(self):
        """Calculate required sample size for proportion test."""
        result = power_analysis(
            test_type="proportion",
            effect_size=0.5,  # Cohen's h
            power=0.8,
        )
        assert result.test_type == "proportion"
        assert result.n_per_group > 0


class TestValidation:
    """Tests for input validation."""

    def test_all_none_raises(self):
        """Should raise when all optional params are None."""
        with pytest.raises(ValueError, match="Exactly one"):
            power_analysis(
                test_type="t_test",
                effect_size=None,
                power=None,
                n_per_group=None,
            )

    def test_none_missing_raises(self):
        """Should raise when no params are None."""
        with pytest.raises(ValueError, match="Exactly one"):
            power_analysis(
                test_type="t_test",
                effect_size=0.5,
                power=0.8,
                n_per_group=30,
            )

    def test_invalid_alpha_raises(self):
        """Should raise for invalid alpha."""
        with pytest.raises(ValueError, match="alpha"):
            power_analysis(
                test_type="t_test",
                effect_size=0.5,
                power=0.8,
                alpha=1.5,
            )

    def test_negative_effect_size_raises(self):
        """Should raise for negative effect size."""
        with pytest.raises(ValueError, match="effect_size"):
            power_analysis(
                test_type="t_test",
                effect_size=-0.5,
                power=0.8,
            )

    def test_invalid_power_raises(self):
        """Should raise for invalid power."""
        with pytest.raises(ValueError, match="power"):
            power_analysis(
                test_type="t_test",
                effect_size=0.5,
                power=1.5,
            )

    def test_small_n_raises(self):
        """Should raise for n_per_group < 2."""
        with pytest.raises(ValueError, match="n_per_group"):
            power_analysis(
                test_type="t_test",
                effect_size=0.5,
                power=None,
                n_per_group=1,
            )

    def test_invalid_test_type_raises(self):
        """Should raise for unknown test type."""
        with pytest.raises(ValueError):
            power_analysis(
                test_type="invalid_test",  # type: ignore
                effect_size=0.5,
                power=0.8,
            )


class TestInterpretationAndRecommendations:
    """Tests for interpretation and recommendations."""

    def test_interpretation_includes_values(self):
        """Interpretation should include key values."""
        result = power_analysis(
            test_type="t_test",
            effect_size=0.5,
            power=0.8,
        )
        assert "0.5" in result.interpretation  # effect size
        assert "80%" in result.interpretation  # power
        assert str(result.n_per_group) in result.interpretation

    def test_recommendations_low_power(self):
        """Should recommend increasing sample size for low power."""
        result = power_analysis(
            test_type="t_test",
            effect_size=0.5,
            power=None,
            n_per_group=10,
        )
        # Power will be low with n=10, d=0.5
        if result.power < 0.8:
            assert any("increase" in r.lower() or "sample" in r.lower()
                       for r in result.recommendations)

    def test_recommendations_small_sample(self):
        """Should warn about very small samples."""
        result = power_analysis(
            test_type="t_test",
            effect_size=0.5,
            power=None,
            n_per_group=5,
        )
        assert any("small" in r.lower() for r in result.recommendations)


class TestUtilities:
    """Tests for utility functions."""

    def test_get_effect_size_conventions(self):
        """Should return conventions for each test type."""
        conventions = get_effect_size_conventions("t_test")
        assert "small" in conventions
        assert "medium" in conventions
        assert "large" in conventions
        assert conventions["small"] == 0.2
        assert conventions["medium"] == 0.5
        assert conventions["large"] == 0.8

    def test_suggest_effect_size_default(self):
        """Should suggest medium effect when no prior studies."""
        effect = suggest_effect_size("t_test")
        assert effect == 0.5  # Medium effect for t-test

    def test_suggest_effect_size_from_prior(self):
        """Should use prior studies when available."""
        effect = suggest_effect_size(
            "t_test",
            prior_studies=[0.4, 0.6, 0.8],
            conservative=True,
        )
        assert effect == 0.4  # Smallest (most conservative)

    def test_sample_size_table(self):
        """Should generate sample size table."""
        table = sample_size_table("t_test")
        assert isinstance(table, list)
        assert len(table) > 0
        for row in table:
            assert "effect_size" in row
            assert "power" in row
            assert "n_per_group" in row
            assert "n_total" in row


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_same_input_same_output(self):
        """Same input should always produce same output."""
        results = [
            power_analysis(test_type="t_test", effect_size=0.5, power=0.8)
            for _ in range(10)
        ]

        for i in range(1, len(results)):
            assert results[i].n_per_group == results[0].n_per_group
            assert results[i].n_total == results[0].n_total
            assert results[i].power == results[0].power
