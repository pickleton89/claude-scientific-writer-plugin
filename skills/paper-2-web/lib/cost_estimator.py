"""Cost estimation for paper transformation pipeline.

This module provides deterministic cost estimation based on paper complexity,
selected components, and model tier. Estimates are based on empirical token
usage data from typical paper transformations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class ModelPricing:
    """Pricing information for a model.

    Attributes:
        input_per_1k: Cost per 1K input tokens in USD
        output_per_1k: Cost per 1K output tokens in USD
        context_window: Maximum context window size
    """

    input_per_1k: float
    output_per_1k: float
    context_window: int = 128000


# Model pricing lookup (updated January 2025)
# Prices are in USD per 1K tokens
MODEL_COSTS: dict[str, ModelPricing] = {
    # OpenAI Models
    "gpt-4o": ModelPricing(0.0025, 0.01, 128000),
    "gpt-4o-mini": ModelPricing(0.00015, 0.0006, 128000),
    "gpt-4-turbo": ModelPricing(0.01, 0.03, 128000),
    "gpt-4": ModelPricing(0.03, 0.06, 8192),
    "gpt-4-32k": ModelPricing(0.06, 0.12, 32768),
    "gpt-3.5-turbo": ModelPricing(0.0005, 0.0015, 16385),
    "o1-preview": ModelPricing(0.015, 0.06, 128000),
    "o1-mini": ModelPricing(0.003, 0.012, 128000),

    # Anthropic Models
    "claude-3-opus": ModelPricing(0.015, 0.075, 200000),
    "claude-3-sonnet": ModelPricing(0.003, 0.015, 200000),
    "claude-3-haiku": ModelPricing(0.00025, 0.00125, 200000),
    "claude-3.5-sonnet": ModelPricing(0.003, 0.015, 200000),
    "claude-3.5-haiku": ModelPricing(0.001, 0.005, 200000),

    # Google Models
    "gemini-1.5-pro": ModelPricing(0.00125, 0.005, 2000000),
    "gemini-1.5-flash": ModelPricing(0.000075, 0.0003, 1000000),
    "gemini-2.0-flash": ModelPricing(0.0001, 0.0004, 1000000),

    # Open Source / OpenRouter
    "llama-3.1-70b": ModelPricing(0.0008, 0.0008, 131072),
    "llama-3.1-8b": ModelPricing(0.0001, 0.0001, 131072),
    "mixtral-8x7b": ModelPricing(0.0005, 0.0005, 32768),
    "deepseek-v3": ModelPricing(0.00027, 0.0011, 64000),
}


# Model tier mapping for user-friendly selection
MODEL_TIERS: dict[str, str] = {
    "draft": "gpt-4o-mini",           # Fast, cheap, good for iteration
    "production": "gpt-4o",            # Balanced quality and cost
    "premium": "claude-3.5-sonnet",    # Highest quality output
    "budget": "deepseek-v3",           # Cost-effective alternative
}


# Base token estimates per component (empirically derived from typical papers)
# These are estimates for a "standard" 8-page paper
COMPONENT_BASE_TOKENS: dict[str, dict[str, int]] = {
    "website": {
        "input": 12000,   # Paper text + prompts
        "output": 18000,  # HTML, CSS, content
    },
    "poster": {
        "input": 10000,   # Paper text + layout prompts
        "output": 12000,  # SVG/HTML poster content
    },
    "video": {
        "input": 15000,   # Paper text + script prompts
        "output": 25000,  # Script, slides, narration
    },
}


# Iteration multipliers (refinement passes increase token usage)
ITERATION_MULTIPLIERS: dict[int, float] = {
    1: 1.0,    # Single pass
    2: 1.6,    # One refinement
    3: 2.1,    # Two refinements
    4: 2.5,    # Three refinements (diminishing returns)
    5: 2.8,    # Four refinements
}


@dataclass
class CostBreakdown:
    """Breakdown of costs by component.

    Attributes:
        component: Component name
        input_tokens: Estimated input tokens
        output_tokens: Estimated output tokens
        cost_usd: Estimated cost in USD
    """

    component: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


@dataclass
class CostEstimate:
    """Complete cost estimate for a transformation.

    Attributes:
        model: Model used for estimation
        model_tier: User-friendly tier name
        total_input_tokens: Total estimated input tokens
        total_output_tokens: Total estimated output tokens
        estimated_cost_usd: Total estimated cost in USD
        confidence: Confidence level of the estimate
        breakdown: Per-component cost breakdown
        assumptions: List of assumptions made in the estimate
    """

    model: str
    model_tier: str
    total_input_tokens: int
    total_output_tokens: int
    estimated_cost_usd: float
    confidence: Literal["high", "medium", "low"]
    breakdown: list[CostBreakdown] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "model": self.model,
            "model_tier": self.model_tier,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "estimated_cost_usd": round(self.estimated_cost_usd, 4),
            "confidence": self.confidence,
            "breakdown": [
                {
                    "component": b.component,
                    "input_tokens": b.input_tokens,
                    "output_tokens": b.output_tokens,
                    "cost_usd": round(b.cost_usd, 4),
                }
                for b in self.breakdown
            ],
            "assumptions": self.assumptions,
        }


def get_complexity_multiplier(paper_pages: int) -> float:
    """Calculate complexity multiplier based on paper length.

    Longer papers require proportionally more processing, but with
    diminishing returns as length increases.

    Args:
        paper_pages: Estimated number of pages in the paper

    Returns:
        Multiplier for base token estimates
    """
    if paper_pages <= 4:
        return 0.6    # Short paper / workshop
    elif paper_pages <= 8:
        return 1.0    # Standard conference paper
    elif paper_pages <= 12:
        return 1.4    # Extended paper
    elif paper_pages <= 20:
        return 1.8    # Journal article
    elif paper_pages <= 40:
        return 2.5    # Long journal / thesis chapter
    else:
        return 3.5    # Very long document


def get_figure_multiplier(figure_count: int) -> float:
    """Calculate multiplier based on figure count.

    More figures generally require more description and processing.

    Args:
        figure_count: Number of figures in the paper

    Returns:
        Multiplier for output tokens
    """
    if figure_count <= 3:
        return 1.0
    elif figure_count <= 6:
        return 1.2
    elif figure_count <= 10:
        return 1.4
    else:
        return 1.6


def estimate_cost(
    paper_pages: int,
    components: list[str],
    model_tier: str = "production",
    figure_count: int = 5,
    iterations: int = 2,
    custom_model: str | None = None,
) -> CostEstimate:
    """Estimate the cost of a paper transformation.

    Args:
        paper_pages: Estimated number of pages in the source paper
        components: List of components to generate (website, poster, video)
        model_tier: Quality tier (draft, production, premium, budget)
        figure_count: Number of figures in the paper
        iterations: Expected number of refinement iterations
        custom_model: Override model selection with specific model

    Returns:
        CostEstimate with detailed breakdown

    Examples:
        >>> estimate = estimate_cost(10, ["website", "poster"], "production")
        >>> estimate.estimated_cost_usd
        0.35
    """
    # Resolve model
    if custom_model and custom_model in MODEL_COSTS:
        model = custom_model
    else:
        model = MODEL_TIERS.get(model_tier, MODEL_TIERS["production"])

    pricing = MODEL_COSTS[model]

    # Calculate multipliers
    complexity_mult = get_complexity_multiplier(paper_pages)
    figure_mult = get_figure_multiplier(figure_count)
    iteration_mult = ITERATION_MULTIPLIERS.get(iterations, 3.0)

    breakdown: list[CostBreakdown] = []
    total_input = 0
    total_output = 0
    assumptions: list[str] = []

    for component in components:
        if component not in COMPONENT_BASE_TOKENS:
            continue

        base = COMPONENT_BASE_TOKENS[component]

        # Apply multipliers
        input_tokens = int(base["input"] * complexity_mult * iteration_mult)
        output_tokens = int(base["output"] * complexity_mult * figure_mult * iteration_mult)

        # Calculate component cost
        comp_cost = (
            (input_tokens / 1000) * pricing.input_per_1k +
            (output_tokens / 1000) * pricing.output_per_1k
        )

        breakdown.append(CostBreakdown(
            component=component,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=comp_cost,
        ))

        total_input += input_tokens
        total_output += output_tokens

    # Calculate total cost
    total_cost = (
        (total_input / 1000) * pricing.input_per_1k +
        (total_output / 1000) * pricing.output_per_1k
    )

    # Determine confidence based on how close to "standard" the paper is
    if 6 <= paper_pages <= 12 and 3 <= figure_count <= 8 and iterations <= 3:
        confidence: Literal["high", "medium", "low"] = "high"
    elif 4 <= paper_pages <= 20 and figure_count <= 15:
        confidence = "medium"
    else:
        confidence = "low"
        assumptions.append("Paper significantly differs from typical conference paper")

    # Add assumptions
    assumptions.extend([
        f"Based on {paper_pages}-page paper with {figure_count} figures",
        f"Assumes {iterations} refinement iteration(s)",
        f"Using {model} pricing as of January 2025",
    ])

    return CostEstimate(
        model=model,
        model_tier=model_tier,
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        estimated_cost_usd=total_cost,
        confidence=confidence,
        breakdown=breakdown,
        assumptions=assumptions,
    )


def compare_models(
    paper_pages: int,
    components: list[str],
    figure_count: int = 5,
) -> dict[str, CostEstimate]:
    """Compare costs across different model tiers.

    Args:
        paper_pages: Estimated number of pages
        components: List of components to generate
        figure_count: Number of figures

    Returns:
        Dictionary mapping tier names to cost estimates
    """
    return {
        tier: estimate_cost(paper_pages, components, tier, figure_count)
        for tier in MODEL_TIERS.keys()
    }


def estimate_from_text_length(
    char_count: int,
    components: list[str],
    model_tier: str = "production",
) -> CostEstimate:
    """Estimate cost from character count instead of pages.

    Useful when page count is unknown but text is available.

    Args:
        char_count: Number of characters in the paper text
        components: List of components to generate
        model_tier: Quality tier

    Returns:
        CostEstimate with page count derived from text length
    """
    # Approximately 4000 characters per page (with figures, equations)
    estimated_pages = max(1, char_count // 4000)

    # Estimate figure count from text length (heuristic)
    estimated_figures = max(1, char_count // 8000)

    return estimate_cost(
        paper_pages=estimated_pages,
        components=components,
        model_tier=model_tier,
        figure_count=estimated_figures,
    )


def format_cost_summary(estimate: CostEstimate) -> str:
    """Format a human-readable cost summary.

    Args:
        estimate: The cost estimate to format

    Returns:
        Formatted string summary
    """
    lines = [
        f"Cost Estimate ({estimate.model_tier} tier)",
        f"Model: {estimate.model}",
        f"",
        f"Token Usage:",
        f"  Input:  {estimate.total_input_tokens:,}",
        f"  Output: {estimate.total_output_tokens:,}",
        f"",
        f"Breakdown:",
    ]

    for b in estimate.breakdown:
        lines.append(f"  {b.component}: ${b.cost_usd:.3f}")

    lines.extend([
        f"",
        f"Total: ${estimate.estimated_cost_usd:.3f}",
        f"Confidence: {estimate.confidence}",
    ])

    return "\n".join(lines)


__all__ = [
    "ModelPricing",
    "MODEL_COSTS",
    "MODEL_TIERS",
    "COMPONENT_BASE_TOKENS",
    "CostBreakdown",
    "CostEstimate",
    "get_complexity_multiplier",
    "get_figure_multiplier",
    "estimate_cost",
    "compare_models",
    "estimate_from_text_length",
    "format_cost_summary",
]
