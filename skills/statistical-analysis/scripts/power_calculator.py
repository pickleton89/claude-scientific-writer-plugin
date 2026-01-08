"""
Deterministic power analysis wrapper.

This module provides direct power computations with no LLM involvement,
wrapping statsmodels power functions with structured input/output.

Example usage:
    >>> from scripts.power_calculator import power_analysis
    >>> result = power_analysis(test_type="t_test", effect_size=0.5, power=0.8)
    >>> print(f"Need {result.n_per_group} per group")
    Need 64 per group
"""

from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np


@dataclass
class PowerResult:
    """Structured output for power analysis."""

    test_type: str
    effect_size: float
    alpha: float
    power: float
    n_per_group: int
    n_total: int
    calculated_param: str
    interpretation: str
    recommendations: list[str]


# =============================================================================
# Effect Size Conventions by Test Type
# =============================================================================

EFFECT_SIZE_CONVENTIONS = {
    "t_test": {
        "metric": "Cohen's d",
        "small": 0.2,
        "medium": 0.5,
        "large": 0.8,
    },
    "paired_t_test": {
        "metric": "Cohen's d (paired)",
        "small": 0.2,
        "medium": 0.5,
        "large": 0.8,
    },
    "anova": {
        "metric": "Cohen's f",
        "small": 0.1,
        "medium": 0.25,
        "large": 0.4,
    },
    "correlation": {
        "metric": "Pearson's r",
        "small": 0.1,
        "medium": 0.3,
        "large": 0.5,
    },
    "chi_square": {
        "metric": "Cohen's w",
        "small": 0.1,
        "medium": 0.3,
        "large": 0.5,
    },
    "proportion": {
        "metric": "Cohen's h",
        "small": 0.2,
        "medium": 0.5,
        "large": 0.8,
    },
}


# =============================================================================
# Main Power Analysis Function
# =============================================================================


def power_analysis(
    test_type: Literal[
        "t_test",
        "paired_t_test",
        "one_sample_t",
        "anova",
        "correlation",
        "chi_square",
        "proportion",
    ],
    effect_size: Optional[float] = None,
    alpha: float = 0.05,
    power: Optional[float] = None,
    n_per_group: Optional[int] = None,
    n_groups: int = 2,
    df: Optional[int] = None,
) -> PowerResult:
    """
    Compute power analysis for common statistical tests.

    Provide any 3 of (effect_size, power, n_per_group) to calculate the 4th.

    Parameters
    ----------
    test_type : str
        Type of statistical test:
        - "t_test": Independent samples t-test
        - "paired_t_test": Paired samples t-test
        - "one_sample_t": One-sample t-test
        - "anova": One-way ANOVA
        - "correlation": Correlation test
        - "chi_square": Chi-square test
        - "proportion": Two-proportion z-test
    effect_size : float, optional
        Expected effect size:
        - t-test: Cohen's d
        - ANOVA: Cohen's f
        - Correlation: r
        - Chi-square: Cohen's w
        - Proportion: Cohen's h
    alpha : float
        Significance level (default 0.05)
    power : float, optional
        Desired power (typically 0.8 or 0.9)
    n_per_group : int, optional
        Sample size per group
    n_groups : int
        Number of groups (for ANOVA, default 2)
    df : int, optional
        Degrees of freedom (for chi-square test)

    Returns
    -------
    PowerResult
        Complete results with all parameters and recommendations

    Raises
    ------
    ValueError
        If invalid parameters or unable to calculate

    Examples
    --------
    >>> # What sample size for medium effect t-test?
    >>> result = power_analysis(test_type="t_test", effect_size=0.5, power=0.8)
    >>> print(f"Need {result.n_per_group} per group")
    Need 64 per group

    >>> # What power with n=30 per group?
    >>> result = power_analysis(test_type="t_test", effect_size=0.5, n_per_group=30)
    >>> print(f"Power: {result.power:.1%}")
    Power: 47.8%
    """
    # Validate inputs
    _validate_power_inputs(effect_size, alpha, power, n_per_group)

    # Route to appropriate calculation
    if test_type == "t_test":
        return _power_t_test_ind(effect_size, alpha, power, n_per_group)
    elif test_type == "paired_t_test":
        return _power_t_test_paired(effect_size, alpha, power, n_per_group)
    elif test_type == "one_sample_t":
        return _power_t_test_one_sample(effect_size, alpha, power, n_per_group)
    elif test_type == "anova":
        return _power_anova(effect_size, alpha, power, n_per_group, n_groups)
    elif test_type == "correlation":
        return _power_correlation(effect_size, alpha, power, n_per_group)
    elif test_type == "chi_square":
        if df is None:
            raise ValueError("df (degrees of freedom) required for chi_square test")
        return _power_chi_square(effect_size, alpha, power, n_per_group, df)
    elif test_type == "proportion":
        return _power_proportion(effect_size, alpha, power, n_per_group)
    else:
        raise ValueError(f"Unknown test_type: {test_type}")


def _validate_power_inputs(
    effect_size: Optional[float],
    alpha: float,
    power: Optional[float],
    n_per_group: Optional[int],
) -> None:
    """Validate power analysis inputs."""
    # Count how many parameters are None
    none_count = sum(x is None for x in [effect_size, power, n_per_group])

    if none_count != 1:
        raise ValueError(
            "Exactly one of (effect_size, power, n_per_group) must be None "
            f"to be calculated. Got {none_count} None values."
        )

    if not (0 < alpha < 1):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")

    if effect_size is not None and effect_size <= 0:
        raise ValueError(f"effect_size must be positive, got {effect_size}")

    if power is not None and not (0 < power < 1):
        raise ValueError(f"power must be in (0, 1), got {power}")

    if n_per_group is not None and n_per_group < 2:
        raise ValueError(f"n_per_group must be >= 2, got {n_per_group}")


# =============================================================================
# Test-Specific Power Calculations
# =============================================================================


def _power_t_test_ind(
    effect_size: Optional[float],
    alpha: float,
    power: Optional[float],
    n_per_group: Optional[int],
) -> PowerResult:
    """Power analysis for independent samples t-test."""
    from statsmodels.stats.power import TTestIndPower

    analysis = TTestIndPower()

    if n_per_group is None:
        n = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)
        n_per_group = int(np.ceil(n))
        calculated = "n_per_group"
    elif power is None:
        power = analysis.solve_power(
            effect_size=effect_size, nobs1=n_per_group, alpha=alpha
        )
        calculated = "power"
    else:  # effect_size is None
        effect_size = analysis.solve_power(nobs1=n_per_group, alpha=alpha, power=power)
        calculated = "effect_size"

    interpretation = _generate_interpretation(
        "independent samples t-test",
        effect_size,
        alpha,
        power,
        n_per_group,
        n_per_group * 2,
        calculated,
    )

    recommendations = _generate_recommendations(
        "t_test", effect_size, power, n_per_group
    )

    return PowerResult(
        test_type="t_test",
        effect_size=float(effect_size),
        alpha=alpha,
        power=float(power),
        n_per_group=n_per_group,
        n_total=n_per_group * 2,
        calculated_param=calculated,
        interpretation=interpretation,
        recommendations=recommendations,
    )


def _power_t_test_paired(
    effect_size: Optional[float],
    alpha: float,
    power: Optional[float],
    n_per_group: Optional[int],
) -> PowerResult:
    """Power analysis for paired samples t-test."""
    from statsmodels.stats.power import TTestPower

    analysis = TTestPower()

    if n_per_group is None:
        n = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)
        n_per_group = int(np.ceil(n))
        calculated = "n_per_group"
    elif power is None:
        power = analysis.solve_power(
            effect_size=effect_size, nobs=n_per_group, alpha=alpha
        )
        calculated = "power"
    else:
        effect_size = analysis.solve_power(nobs=n_per_group, alpha=alpha, power=power)
        calculated = "effect_size"

    interpretation = _generate_interpretation(
        "paired samples t-test",
        effect_size,
        alpha,
        power,
        n_per_group,
        n_per_group,
        calculated,
    )

    recommendations = _generate_recommendations(
        "paired_t_test", effect_size, power, n_per_group
    )

    return PowerResult(
        test_type="paired_t_test",
        effect_size=float(effect_size),
        alpha=alpha,
        power=float(power),
        n_per_group=n_per_group,
        n_total=n_per_group,  # Total pairs
        calculated_param=calculated,
        interpretation=interpretation,
        recommendations=recommendations,
    )


def _power_t_test_one_sample(
    effect_size: Optional[float],
    alpha: float,
    power: Optional[float],
    n_per_group: Optional[int],
) -> PowerResult:
    """Power analysis for one-sample t-test."""
    from statsmodels.stats.power import TTestPower

    analysis = TTestPower()

    if n_per_group is None:
        n = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)
        n_per_group = int(np.ceil(n))
        calculated = "n_per_group"
    elif power is None:
        power = analysis.solve_power(
            effect_size=effect_size, nobs=n_per_group, alpha=alpha
        )
        calculated = "power"
    else:
        effect_size = analysis.solve_power(nobs=n_per_group, alpha=alpha, power=power)
        calculated = "effect_size"

    interpretation = _generate_interpretation(
        "one-sample t-test",
        effect_size,
        alpha,
        power,
        n_per_group,
        n_per_group,
        calculated,
    )

    recommendations = _generate_recommendations(
        "t_test", effect_size, power, n_per_group
    )

    return PowerResult(
        test_type="one_sample_t",
        effect_size=float(effect_size),
        alpha=alpha,
        power=float(power),
        n_per_group=n_per_group,
        n_total=n_per_group,
        calculated_param=calculated,
        interpretation=interpretation,
        recommendations=recommendations,
    )


def _power_anova(
    effect_size: Optional[float],
    alpha: float,
    power: Optional[float],
    n_per_group: Optional[int],
    n_groups: int,
) -> PowerResult:
    """Power analysis for one-way ANOVA."""
    from statsmodels.stats.power import FTestAnovaPower

    analysis = FTestAnovaPower()

    if n_per_group is None:
        n = analysis.solve_power(
            effect_size=effect_size, k_groups=n_groups, alpha=alpha, power=power
        )
        n_per_group = int(np.ceil(n))
        calculated = "n_per_group"
    elif power is None:
        power = analysis.solve_power(
            effect_size=effect_size, k_groups=n_groups, nobs=n_per_group, alpha=alpha
        )
        calculated = "power"
    else:
        effect_size = analysis.solve_power(
            k_groups=n_groups, nobs=n_per_group, alpha=alpha, power=power
        )
        calculated = "effect_size"

    interpretation = _generate_interpretation(
        f"one-way ANOVA ({n_groups} groups)",
        effect_size,
        alpha,
        power,
        n_per_group,
        n_per_group * n_groups,
        calculated,
    )

    recommendations = _generate_recommendations(
        "anova", effect_size, power, n_per_group
    )

    return PowerResult(
        test_type="anova",
        effect_size=float(effect_size),
        alpha=alpha,
        power=float(power),
        n_per_group=n_per_group,
        n_total=n_per_group * n_groups,
        calculated_param=calculated,
        interpretation=interpretation,
        recommendations=recommendations,
    )


def _power_correlation(
    effect_size: Optional[float],
    alpha: float,
    power: Optional[float],
    n_per_group: Optional[int],
) -> PowerResult:
    """Power analysis for correlation test."""
    from statsmodels.stats.power import NormalIndPower

    # For correlation, we use the Fisher z transformation
    # The effect size is r, and we convert to z
    analysis = NormalIndPower()

    # Convert r to z for power calculation
    def r_to_z(r):
        return 0.5 * np.log((1 + r) / (1 - r))

    if n_per_group is None:
        # Need to use iterative approach for correlation
        z = r_to_z(effect_size)
        n = analysis.solve_power(effect_size=z, alpha=alpha, power=power)
        n_per_group = int(np.ceil(n)) + 3  # Add 3 for correlation df adjustment
        calculated = "n_per_group"
    elif power is None:
        z = r_to_z(effect_size)
        power = analysis.solve_power(effect_size=z, nobs=n_per_group - 3, alpha=alpha)
        calculated = "power"
    else:
        z = analysis.solve_power(nobs=n_per_group - 3, alpha=alpha, power=power)
        # Convert z back to r
        effect_size = (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)
        calculated = "effect_size"

    interpretation = _generate_interpretation(
        "correlation test",
        effect_size,
        alpha,
        power,
        n_per_group,
        n_per_group,
        calculated,
    )

    recommendations = _generate_recommendations(
        "correlation", effect_size, power, n_per_group
    )

    return PowerResult(
        test_type="correlation",
        effect_size=float(effect_size),
        alpha=alpha,
        power=float(power),
        n_per_group=n_per_group,
        n_total=n_per_group,
        calculated_param=calculated,
        interpretation=interpretation,
        recommendations=recommendations,
    )


def _power_chi_square(
    effect_size: Optional[float],
    alpha: float,
    power: Optional[float],
    n_per_group: Optional[int],
    df: int,
) -> PowerResult:
    """Power analysis for chi-square test."""
    from statsmodels.stats.power import GofChisquarePower

    analysis = GofChisquarePower()

    if n_per_group is None:
        n = analysis.solve_power(
            effect_size=effect_size, alpha=alpha, power=power, n_bins=df + 1
        )
        n_per_group = int(np.ceil(n))
        calculated = "n_per_group"
    elif power is None:
        power = analysis.solve_power(
            effect_size=effect_size, nobs=n_per_group, alpha=alpha, n_bins=df + 1
        )
        calculated = "power"
    else:
        effect_size = analysis.solve_power(
            nobs=n_per_group, alpha=alpha, power=power, n_bins=df + 1
        )
        calculated = "effect_size"

    interpretation = _generate_interpretation(
        f"chi-square test (df={df})",
        effect_size,
        alpha,
        power,
        n_per_group,
        n_per_group,
        calculated,
    )

    recommendations = _generate_recommendations(
        "chi_square", effect_size, power, n_per_group
    )

    return PowerResult(
        test_type="chi_square",
        effect_size=float(effect_size),
        alpha=alpha,
        power=float(power),
        n_per_group=n_per_group,
        n_total=n_per_group,
        calculated_param=calculated,
        interpretation=interpretation,
        recommendations=recommendations,
    )


def _power_proportion(
    effect_size: Optional[float],
    alpha: float,
    power: Optional[float],
    n_per_group: Optional[int],
) -> PowerResult:
    """Power analysis for two-proportion z-test."""
    from statsmodels.stats.power import NormalIndPower

    analysis = NormalIndPower()

    if n_per_group is None:
        n = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)
        n_per_group = int(np.ceil(n))
        calculated = "n_per_group"
    elif power is None:
        power = analysis.solve_power(
            effect_size=effect_size, nobs=n_per_group, alpha=alpha
        )
        calculated = "power"
    else:
        effect_size = analysis.solve_power(nobs=n_per_group, alpha=alpha, power=power)
        calculated = "effect_size"

    interpretation = _generate_interpretation(
        "two-proportion z-test",
        effect_size,
        alpha,
        power,
        n_per_group,
        n_per_group * 2,
        calculated,
    )

    recommendations = _generate_recommendations(
        "proportion", effect_size, power, n_per_group
    )

    return PowerResult(
        test_type="proportion",
        effect_size=float(effect_size),
        alpha=alpha,
        power=float(power),
        n_per_group=n_per_group,
        n_total=n_per_group * 2,
        calculated_param=calculated,
        interpretation=interpretation,
        recommendations=recommendations,
    )


# =============================================================================
# Helper Functions
# =============================================================================


def _generate_interpretation(
    test_name: str,
    effect_size: float,
    alpha: float,
    power: float,
    n_per_group: int,
    n_total: int,
    calculated: str,
) -> str:
    """Generate human-readable interpretation of power analysis."""

    if calculated == "n_per_group":
        return (
            f"For a {test_name} with effect size = {effect_size:.2f}, "
            f"alpha = {alpha}, and power = {power:.0%}, "
            f"you need {n_per_group} per group ({n_total} total)."
        )
    elif calculated == "power":
        return (
            f"A {test_name} with effect size = {effect_size:.2f}, "
            f"alpha = {alpha}, and n = {n_per_group} per group "
            f"has {power:.1%} power to detect the effect."
        )
    else:  # calculated == "effect_size"
        return (
            f"With n = {n_per_group} per group, alpha = {alpha}, "
            f"and power = {power:.0%}, the {test_name} can detect "
            f"a minimum effect size of {effect_size:.2f}."
        )


def _generate_recommendations(
    test_type: str,
    effect_size: float,
    power: float,
    n_per_group: int,
) -> list[str]:
    """Generate recommendations based on power analysis results."""
    recommendations = []

    conventions = EFFECT_SIZE_CONVENTIONS.get(
        test_type, EFFECT_SIZE_CONVENTIONS["t_test"]
    )

    # Effect size recommendations
    if effect_size < conventions["small"]:
        recommendations.append(
            f"Effect size ({effect_size:.2f}) is smaller than conventional 'small' "
            f"({conventions['small']}). Consider whether this effect is practically meaningful."
        )
    elif effect_size < conventions["medium"]:
        recommendations.append(
            f"Effect size ({effect_size:.2f}) is 'small' by conventional standards. "
            "Ensure sample size is adequate."
        )

    # Power recommendations
    if power < 0.8:
        recommendations.append(
            f"Power ({power:.1%}) is below recommended 80%. Consider increasing sample size."
        )
    elif power < 0.9:
        recommendations.append(
            f"Power ({power:.1%}) is adequate but below 90%. "
            "For confirmatory studies, consider 90% power."
        )

    # Sample size recommendations
    if n_per_group < 10:
        recommendations.append(
            "Very small sample size. Results may be unreliable. "
            "Consider pilot study or pooling data."
        )
    elif n_per_group < 20:
        recommendations.append(
            "Small sample size. Ensure normality assumptions are met or use non-parametric tests."
        )

    if not recommendations:
        recommendations.append(
            "Study appears adequately powered for the target effect size."
        )

    return recommendations


# =============================================================================
# Utility Functions
# =============================================================================


def get_effect_size_conventions(
    test_type: str,
) -> dict[str, float]:
    """
    Get conventional effect size thresholds for a test type.

    Parameters
    ----------
    test_type : str
        Type of statistical test

    Returns
    -------
    dict
        Dictionary with 'small', 'medium', 'large' thresholds
    """
    if test_type not in EFFECT_SIZE_CONVENTIONS:
        return EFFECT_SIZE_CONVENTIONS["t_test"]
    return EFFECT_SIZE_CONVENTIONS[test_type]


def suggest_effect_size(
    test_type: str,
    prior_studies: Optional[list[float]] = None,
    conservative: bool = True,
) -> float:
    """
    Suggest an effect size for power analysis.

    Parameters
    ----------
    test_type : str
        Type of statistical test
    prior_studies : list of float, optional
        Effect sizes from prior studies
    conservative : bool
        If True, use conservative (smaller) estimate

    Returns
    -------
    float
        Suggested effect size

    Examples
    --------
    >>> suggest_effect_size("t_test", prior_studies=[0.6, 0.8, 0.5])
    0.5
    """
    conventions = get_effect_size_conventions(test_type)

    if prior_studies:
        # Use smallest observed effect if conservative
        if conservative:
            return min(prior_studies)
        else:
            return float(np.median(prior_studies))
    else:
        # Default to medium effect
        return conventions["medium"]


def sample_size_table(
    test_type: str,
    effect_sizes: Optional[list[float]] = None,
    powers: Optional[list[float]] = None,
    alpha: float = 0.05,
) -> list[dict]:
    """
    Generate a sample size table for multiple effect sizes and power levels.

    Parameters
    ----------
    test_type : str
        Type of statistical test
    effect_sizes : list of float, optional
        Effect sizes to include (default: small, medium, large)
    powers : list of float, optional
        Power levels to include (default: 0.8, 0.9)
    alpha : float
        Significance level

    Returns
    -------
    list of dict
        Table entries with effect_size, power, and required n

    Examples
    --------
    >>> table = sample_size_table("t_test")
    >>> for row in table:
    ...     print(f"d={row['effect_size']}, power={row['power']}, n={row['n_per_group']}")
    """
    conventions = get_effect_size_conventions(test_type)

    if effect_sizes is None:
        effect_sizes = [
            conventions["small"],
            conventions["medium"],
            conventions["large"],
        ]
    if powers is None:
        powers = [0.8, 0.9]

    table = []
    for es in effect_sizes:
        for pwr in powers:
            try:
                result = power_analysis(
                    test_type=test_type,
                    effect_size=es,
                    power=pwr,
                    alpha=alpha,
                )
                table.append(
                    {
                        "effect_size": es,
                        "power": pwr,
                        "n_per_group": result.n_per_group,
                        "n_total": result.n_total,
                    }
                )
            except Exception:
                table.append(
                    {
                        "effect_size": es,
                        "power": pwr,
                        "n_per_group": None,
                        "n_total": None,
                    }
                )

    return table


if __name__ == "__main__":
    # Example usage demonstrating deterministic output
    print("=== Power Analysis Examples ===\n")

    # Example 1: What sample size for medium effect t-test?
    result = power_analysis(test_type="t_test", effect_size=0.5, power=0.8)
    print("Two-sample t-test, d=0.5, 80% power:")
    print(f"  {result.interpretation}")
    print(f"  Recommendations: {result.recommendations[0]}")
    print()

    # Example 2: What power with n=30?
    result = power_analysis(test_type="t_test", effect_size=0.5, n_per_group=30)
    print("Two-sample t-test, d=0.5, n=30 per group:")
    print(f"  {result.interpretation}")
    print()

    # Example 3: ANOVA with 3 groups
    result = power_analysis(test_type="anova", effect_size=0.25, power=0.8, n_groups=3)
    print("One-way ANOVA, f=0.25, 3 groups, 80% power:")
    print(f"  {result.interpretation}")
    print()

    # Example 4: Generate sample size table
    print("Sample size table for t-test:")
    table = sample_size_table("t_test")
    print(f"{'Effect':>8} {'Power':>8} {'N/group':>8} {'Total':>8}")
    print("-" * 36)
    for row in table:
        print(
            f"{row['effect_size']:>8.2f} {row['power']:>8.0%} "
            f"{row['n_per_group']:>8} {row['n_total']:>8}"
        )
