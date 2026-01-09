"""Tests for cost_estimator module."""

import pytest
from lib.cost_estimator import (
    ModelPricing,
    MODEL_COSTS,
    MODEL_TIERS,
    COMPONENT_BASE_TOKENS,
    CostBreakdown,
    CostEstimate,
    get_complexity_multiplier,
    get_figure_multiplier,
    estimate_cost,
    compare_models,
    estimate_from_text_length,
    format_cost_summary,
)


class TestModelPricing:
    """Tests for ModelPricing dataclass."""

    def test_model_pricing_creation(self):
        """Test creating ModelPricing instance."""
        pricing = ModelPricing(0.01, 0.03, 128000)
        assert pricing.input_per_1k == 0.01
        assert pricing.output_per_1k == 0.03
        assert pricing.context_window == 128000

    def test_model_pricing_default_context(self):
        """Test default context window."""
        pricing = ModelPricing(0.01, 0.03)
        assert pricing.context_window == 128000


class TestModelCosts:
    """Tests for MODEL_COSTS dictionary."""

    def test_model_costs_has_major_models(self):
        """Test that major models are included."""
        major_models = ["gpt-4o", "gpt-4", "claude-3-opus", "claude-3.5-sonnet"]
        for model in major_models:
            assert model in MODEL_COSTS, f"Missing model: {model}"

    def test_model_costs_positive_values(self):
        """Test that all costs are positive."""
        for model, pricing in MODEL_COSTS.items():
            assert pricing.input_per_1k > 0, f"{model} input cost not positive"
            assert pricing.output_per_1k > 0, f"{model} output cost not positive"

    def test_output_more_expensive_than_input(self):
        """Test that output is more expensive for most models."""
        exceptions = ["llama-3.1-70b", "llama-3.1-8b", "mixtral-8x7b"]  # Some open source have equal
        for model, pricing in MODEL_COSTS.items():
            if model not in exceptions:
                assert pricing.output_per_1k >= pricing.input_per_1k, f"{model} output cheaper than input"


class TestModelTiers:
    """Tests for MODEL_TIERS mapping."""

    def test_model_tiers_has_expected_tiers(self):
        """Test that expected tiers exist."""
        expected = ["draft", "production", "premium", "budget"]
        for tier in expected:
            assert tier in MODEL_TIERS, f"Missing tier: {tier}"

    def test_model_tiers_map_to_valid_models(self):
        """Test that all tiers map to valid models."""
        for tier, model in MODEL_TIERS.items():
            assert model in MODEL_COSTS, f"Tier {tier} maps to unknown model {model}"


class TestComplexityMultiplier:
    """Tests for get_complexity_multiplier function."""

    def test_short_paper_multiplier(self):
        """Test short paper has lower multiplier."""
        mult = get_complexity_multiplier(4)
        assert mult == 0.6

    def test_standard_paper_multiplier(self):
        """Test standard paper has 1.0 multiplier."""
        mult = get_complexity_multiplier(8)
        assert mult == 1.0

    def test_long_paper_multiplier(self):
        """Test longer papers have higher multipliers."""
        mult_12 = get_complexity_multiplier(12)
        mult_20 = get_complexity_multiplier(20)
        mult_50 = get_complexity_multiplier(50)

        assert mult_12 > 1.0
        assert mult_20 > mult_12
        assert mult_50 > mult_20

    def test_multiplier_increases_with_length(self):
        """Test multiplier increases monotonically."""
        lengths = [2, 6, 10, 15, 25, 50]
        multipliers = [get_complexity_multiplier(l) for l in lengths]
        for i in range(1, len(multipliers)):
            assert multipliers[i] >= multipliers[i - 1]


class TestFigureMultiplier:
    """Tests for get_figure_multiplier function."""

    def test_few_figures_multiplier(self):
        """Test few figures has 1.0 multiplier."""
        mult = get_figure_multiplier(3)
        assert mult == 1.0

    def test_many_figures_multiplier(self):
        """Test more figures have higher multipliers."""
        mult_5 = get_figure_multiplier(5)
        mult_10 = get_figure_multiplier(10)
        mult_15 = get_figure_multiplier(15)

        assert mult_5 > 1.0
        assert mult_10 > mult_5
        assert mult_15 > mult_10


class TestEstimateCost:
    """Tests for estimate_cost function."""

    def test_estimate_cost_basic(self):
        """Test basic cost estimation."""
        estimate = estimate_cost(8, ["website"])
        assert isinstance(estimate, CostEstimate)
        assert estimate.estimated_cost_usd > 0
        assert estimate.total_input_tokens > 0
        assert estimate.total_output_tokens > 0

    def test_estimate_cost_multiple_components(self):
        """Test cost with multiple components."""
        single = estimate_cost(8, ["website"])
        multiple = estimate_cost(8, ["website", "poster", "video"])
        assert multiple.estimated_cost_usd > single.estimated_cost_usd

    def test_estimate_cost_breakdown(self):
        """Test that breakdown matches total."""
        estimate = estimate_cost(8, ["website", "poster"])
        breakdown_total = sum(b.cost_usd for b in estimate.breakdown)
        assert abs(breakdown_total - estimate.estimated_cost_usd) < 0.01

    def test_estimate_cost_model_tiers(self):
        """Test different model tiers have different costs."""
        draft = estimate_cost(8, ["website"], "draft")
        prod = estimate_cost(8, ["website"], "production")
        premium = estimate_cost(8, ["website"], "premium")

        # Draft should be cheapest
        assert draft.estimated_cost_usd < prod.estimated_cost_usd

    def test_estimate_cost_custom_model(self):
        """Test custom model override."""
        estimate = estimate_cost(8, ["website"], custom_model="gpt-4")
        assert estimate.model == "gpt-4"

    def test_estimate_cost_longer_paper_more_expensive(self):
        """Test longer papers cost more."""
        short = estimate_cost(4, ["website"])
        medium = estimate_cost(10, ["website"])
        long = estimate_cost(30, ["website"])

        assert short.estimated_cost_usd < medium.estimated_cost_usd
        assert medium.estimated_cost_usd < long.estimated_cost_usd

    def test_estimate_cost_more_figures_more_expensive(self):
        """Test more figures cost more."""
        few = estimate_cost(8, ["website"], figure_count=3)
        many = estimate_cost(8, ["website"], figure_count=12)
        assert few.estimated_cost_usd < many.estimated_cost_usd

    def test_estimate_cost_more_iterations_more_expensive(self):
        """Test more iterations cost more."""
        single = estimate_cost(8, ["website"], iterations=1)
        multiple = estimate_cost(8, ["website"], iterations=3)
        assert single.estimated_cost_usd < multiple.estimated_cost_usd

    def test_estimate_cost_confidence_levels(self):
        """Test confidence levels are set appropriately."""
        standard = estimate_cost(8, ["website"], figure_count=5, iterations=2)
        assert standard.confidence in ["high", "medium", "low"]

        unusual = estimate_cost(100, ["website"], figure_count=50)
        assert unusual.confidence == "low"

    def test_estimate_cost_assumptions_included(self):
        """Test that assumptions are documented."""
        estimate = estimate_cost(8, ["website"])
        assert len(estimate.assumptions) > 0

    def test_estimate_cost_to_dict(self):
        """Test CostEstimate serialization."""
        estimate = estimate_cost(8, ["website"])
        d = estimate.to_dict()
        assert "model" in d
        assert "estimated_cost_usd" in d
        assert "breakdown" in d


class TestCompareModels:
    """Tests for compare_models function."""

    def test_compare_models_returns_all_tiers(self):
        """Test that all tiers are compared."""
        comparison = compare_models(8, ["website"])
        for tier in MODEL_TIERS.keys():
            assert tier in comparison

    def test_compare_models_consistent_inputs(self):
        """Test that comparison uses same inputs."""
        comparison = compare_models(8, ["website"])
        for tier, estimate in comparison.items():
            assert "website" in [b.component for b in estimate.breakdown]


class TestEstimateFromTextLength:
    """Tests for estimate_from_text_length function."""

    def test_estimate_from_text_short(self):
        """Test estimate from short text."""
        estimate = estimate_from_text_length(4000, ["website"])
        assert estimate.total_input_tokens > 0

    def test_estimate_from_text_long(self):
        """Test estimate from long text."""
        short = estimate_from_text_length(4000, ["website"])
        long = estimate_from_text_length(40000, ["website"])
        assert long.estimated_cost_usd > short.estimated_cost_usd


class TestFormatCostSummary:
    """Tests for format_cost_summary function."""

    def test_format_cost_summary_basic(self):
        """Test basic formatting."""
        estimate = estimate_cost(8, ["website"])
        summary = format_cost_summary(estimate)
        assert isinstance(summary, str)
        assert "Cost Estimate" in summary
        assert "$" in summary

    def test_format_cost_summary_includes_breakdown(self):
        """Test that breakdown is included."""
        estimate = estimate_cost(8, ["website", "poster"])
        summary = format_cost_summary(estimate)
        assert "website" in summary
        assert "poster" in summary


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self):
        """Test that same input always gives same output."""
        results = [estimate_cost(8, ["website"]) for _ in range(5)]
        costs = [r.estimated_cost_usd for r in results]
        assert all(c == costs[0] for c in costs)

    def test_deterministic_across_parameters(self):
        """Test determinism with various parameters."""
        params = [
            (8, ["website"], "production"),
            (10, ["poster", "video"], "draft"),
            (20, ["website", "poster", "video"], "premium"),
        ]

        for pages, components, tier in params:
            results = [estimate_cost(pages, components, tier) for _ in range(3)]
            costs = [r.estimated_cost_usd for r in results]
            assert all(c == costs[0] for c in costs)
