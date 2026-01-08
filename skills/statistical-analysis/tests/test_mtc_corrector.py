"""
Tests for the multiple testing correction module.
"""

import pytest

from mtc_corrector import (
    MTCResult,
    calculate_bonferroni_threshold,
    correct_pvalues,
    estimate_fdr_discoveries,
    recommend_method,
)


class TestCorrectPvalues:
    """Tests for the main correct_pvalues function."""

    def test_bh_fdr_basic(self, sample_pvalues):
        """Basic BH-FDR correction."""
        result = correct_pvalues(sample_pvalues, method="bh_fdr")
        assert isinstance(result, MTCResult)
        assert result.method == "bh_fdr"
        assert result.n_tests == len(sample_pvalues)
        assert len(result.adjusted_pvalues) == len(sample_pvalues)

    def test_bonferroni_basic(self, sample_pvalues):
        """Basic Bonferroni correction."""
        result = correct_pvalues(sample_pvalues, method="bonferroni")
        assert result.method == "bonferroni"
        # Bonferroni should be more conservative
        assert result.n_significant <= len(sample_pvalues)

    def test_holm_basic(self, sample_pvalues):
        """Basic Holm correction."""
        result = correct_pvalues(sample_pvalues, method="holm")
        assert result.method == "holm"

    def test_hochberg_basic(self, sample_pvalues):
        """Basic Hochberg correction."""
        result = correct_pvalues(sample_pvalues, method="hochberg")
        assert result.method == "hochberg"

    def test_by_fdr_basic(self, sample_pvalues):
        """Basic BY-FDR correction."""
        result = correct_pvalues(sample_pvalues, method="by_fdr")
        assert result.method == "by_fdr"

    def test_all_methods_run(self, sample_pvalues):
        """All methods should run without error."""
        methods = [
            "bh_fdr", "bonferroni", "holm", "hochberg",
            "by_fdr", "sidak", "holm_sidak", "fdr_tsbh", "fdr_tsbky"
        ]
        for method in methods:
            result = correct_pvalues(sample_pvalues, method=method)
            assert result.method == method

    def test_adjusted_pvalues_order(self, sample_pvalues):
        """Adjusted p-values should maintain order with raw."""
        result = correct_pvalues(sample_pvalues, method="bh_fdr")
        # Smaller raw p-values should have smaller adjusted p-values
        for i in range(len(sample_pvalues) - 1):
            if sample_pvalues[i] < sample_pvalues[i + 1]:
                assert result.adjusted_pvalues[i] <= result.adjusted_pvalues[i + 1]

    def test_adjusted_pvalues_bounds(self, sample_pvalues):
        """Adjusted p-values should be in [0, 1]."""
        result = correct_pvalues(sample_pvalues, method="bh_fdr")
        for p in result.adjusted_pvalues:
            assert 0 <= p <= 1

    def test_significant_matches_threshold(self, sample_pvalues):
        """Significance flags should match adjusted p-values < alpha."""
        alpha = 0.05
        result = correct_pvalues(sample_pvalues, method="bh_fdr", alpha=alpha)
        for sig, adj_p in zip(result.significant, result.adjusted_pvalues):
            assert sig == (adj_p < alpha)

    def test_n_significant_count(self, sample_pvalues):
        """n_significant should match sum of significant flags."""
        result = correct_pvalues(sample_pvalues, method="bh_fdr")
        assert result.n_significant == sum(result.significant)

    def test_all_significant_small_pvalues(self, small_pvalues):
        """All small p-values should remain significant after BH-FDR."""
        result = correct_pvalues(small_pvalues, method="bh_fdr")
        assert result.n_significant == len(small_pvalues)

    def test_none_significant_large_pvalues(self, large_pvalues):
        """No large p-values should be significant."""
        result = correct_pvalues(large_pvalues, method="bh_fdr")
        assert result.n_significant == 0

    def test_bonferroni_more_conservative(self, sample_pvalues):
        """Bonferroni should find fewer significant results than BH-FDR."""
        bh_result = correct_pvalues(sample_pvalues, method="bh_fdr")
        bonf_result = correct_pvalues(sample_pvalues, method="bonferroni")
        assert bonf_result.n_significant <= bh_result.n_significant


class TestCorrectPvaluesValidation:
    """Tests for input validation in correct_pvalues."""

    def test_empty_pvalues_raises(self):
        """Should raise error for empty p-values."""
        with pytest.raises(ValueError, match="cannot be empty"):
            correct_pvalues([])

    def test_negative_pvalue_raises(self):
        """Should raise error for negative p-value."""
        with pytest.raises(ValueError, match="range"):
            correct_pvalues([-0.1, 0.5])

    def test_pvalue_greater_than_one_raises(self):
        """Should raise error for p-value > 1."""
        with pytest.raises(ValueError, match="range"):
            correct_pvalues([0.5, 1.5])

    def test_invalid_alpha_raises(self):
        """Should raise error for invalid alpha."""
        with pytest.raises(ValueError, match="alpha"):
            correct_pvalues([0.05], alpha=1.5)

    def test_invalid_method_raises(self):
        """Should raise error for unknown method."""
        with pytest.raises(ValueError, match="Unknown method"):
            correct_pvalues([0.05], method="invalid_method")

    def test_nan_pvalue_raises(self):
        """Should raise error for NaN p-value."""
        import math
        with pytest.raises(ValueError, match="NaN"):
            correct_pvalues([0.05, math.nan])


class TestInterpretation:
    """Tests for interpretation generation."""

    def test_interpretation_includes_method(self, sample_pvalues):
        """Interpretation should mention the method."""
        result = correct_pvalues(sample_pvalues, method="bh_fdr")
        assert "Benjamini-Hochberg" in result.interpretation

    def test_interpretation_includes_count(self, sample_pvalues):
        """Interpretation should mention significant count."""
        result = correct_pvalues(sample_pvalues, method="bh_fdr")
        assert str(result.n_significant) in result.interpretation

    def test_interpretation_none_significant(self, large_pvalues):
        """Interpretation for no significant results."""
        result = correct_pvalues(large_pvalues, method="bh_fdr")
        assert "no tests" in result.interpretation.lower() or "0" in result.interpretation


class TestRecommendMethod:
    """Tests for the recommend_method function."""

    def test_discovery_recommends_bh_fdr(self):
        """Discovery studies should recommend BH-FDR."""
        method = recommend_method(20000, study_type="discovery")
        assert method == "bh_fdr"

    def test_discovery_dependent_recommends_by_fdr(self):
        """Dependent tests in discovery should recommend BY-FDR."""
        method = recommend_method(100, study_type="discovery", dependent_tests=True)
        assert method == "by_fdr"

    def test_confirmatory_small_n_recommends_bonferroni(self):
        """Confirmatory with small n should recommend Bonferroni."""
        method = recommend_method(5, study_type="confirmatory")
        assert method == "bonferroni"

    def test_confirmatory_large_n_recommends_holm(self):
        """Confirmatory with large n should recommend Holm."""
        method = recommend_method(50, study_type="confirmatory")
        assert method == "holm"

    def test_replication_recommends_holm(self):
        """Replication should recommend Holm."""
        method = recommend_method(20, study_type="replication")
        assert method == "holm"


class TestCalculateBonferroniThreshold:
    """Tests for Bonferroni threshold calculation."""

    def test_basic_calculation(self):
        """Basic Bonferroni threshold calculation."""
        threshold = calculate_bonferroni_threshold(100, alpha=0.05)
        assert threshold == pytest.approx(0.0005)

    def test_single_test(self):
        """Single test should return alpha."""
        threshold = calculate_bonferroni_threshold(1, alpha=0.05)
        assert threshold == pytest.approx(0.05)

    def test_large_n(self):
        """Large number of tests."""
        threshold = calculate_bonferroni_threshold(20000, alpha=0.05)
        assert threshold == pytest.approx(0.05 / 20000)

    def test_invalid_n_raises(self):
        """Should raise for n <= 0."""
        with pytest.raises(ValueError):
            calculate_bonferroni_threshold(0)

    def test_invalid_alpha_raises(self):
        """Should raise for invalid alpha."""
        with pytest.raises(ValueError):
            calculate_bonferroni_threshold(10, alpha=1.5)


class TestEstimateFDRDiscoveries:
    """Tests for FDR discovery estimation."""

    def test_basic_estimation(self):
        """Basic FDR estimation."""
        est = estimate_fdr_discoveries(20000, 500, power=0.8, alpha=0.05)
        assert "expected_discoveries" in est
        assert "true_positives" in est
        assert "false_positives" in est
        assert "estimated_fdr" in est

    def test_true_positives_calculation(self):
        """True positives = n_true * power."""
        est = estimate_fdr_discoveries(1000, 100, power=0.8, alpha=0.05)
        assert est["true_positives"] == pytest.approx(80)

    def test_false_positives_calculation(self):
        """False positives = n_null * alpha."""
        est = estimate_fdr_discoveries(1000, 100, power=0.8, alpha=0.05)
        expected_fp = 900 * 0.05  # 900 nulls * 0.05
        assert est["false_positives"] == pytest.approx(expected_fp)

    def test_fdr_calculation(self):
        """FDR = FP / (TP + FP)."""
        est = estimate_fdr_discoveries(1000, 100, power=0.8, alpha=0.05)
        expected_fdr = est["false_positives"] / est["expected_discoveries"]
        assert est["estimated_fdr"] == pytest.approx(expected_fdr, rel=0.01)

    def test_invalid_n_tests_raises(self):
        """Should raise for n_tests <= 0."""
        with pytest.raises(ValueError):
            estimate_fdr_discoveries(0, 10)

    def test_invalid_n_true_raises(self):
        """Should raise for n_true > n_tests."""
        with pytest.raises(ValueError):
            estimate_fdr_discoveries(100, 200)


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_same_input_same_output(self, sample_pvalues):
        """Same input should always produce same output."""
        results = [
            correct_pvalues(sample_pvalues, method="bh_fdr")
            for _ in range(10)
        ]

        for i in range(1, len(results)):
            assert results[i].adjusted_pvalues == results[0].adjusted_pvalues
            assert results[i].significant == results[0].significant
            assert results[i].n_significant == results[0].n_significant
