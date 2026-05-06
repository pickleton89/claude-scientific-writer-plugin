"""
Deterministic effect size interpretation using lookup tables.

This module provides deterministic interpretation of effect sizes based on
established conventions (Cohen, 1988 and field-specific guidelines), with
no LLM variance in the output.

Example usage:
    >>> from scripts.effect_interpreter import interpret_effect_size
    >>> result = interpret_effect_size(0.65, "cohens_d")
    >>> print(result.interpretation)
    "Cohen's d = 0.65 indicates a medium effect (moderate and noticeable difference)."
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class EffectInterpretation:
    """Structured interpretation of effect size."""

    metric: str
    metric_full_name: str
    value: float
    magnitude: str
    interpretation: str
    context: str
    direction: str
    confidence_note: str


# =============================================================================
# Effect Size Threshold Tables
# =============================================================================
# Based on Cohen (1988), Sawilowsky (2009), and field conventions

EFFECT_THRESHOLDS = {
    "cohens_d": {
        "name": "Cohen's d",
        "description": "Standardized mean difference",
        "thresholds": [
            (0.01, "negligible", "no practical difference"),
            (0.20, "very small", "trivial difference, likely not meaningful"),
            (0.50, "small", "subtle but potentially meaningful difference"),
            (0.80, "medium", "moderate and noticeable difference"),
            (1.20, "large", "substantial and obvious difference"),
            (2.00, "very large", "huge difference, easily observable"),
            (float("inf"), "huge", "extremely large effect"),
        ],
        "direction_positive": "Group 1 > Group 2",
        "direction_negative": "Group 1 < Group 2",
    },
    "hedges_g": {
        "name": "Hedges' g",
        "description": "Bias-corrected standardized mean difference",
        "thresholds": [
            (0.01, "negligible", "no practical difference"),
            (0.20, "very small", "trivial difference"),
            (0.50, "small", "subtle difference"),
            (0.80, "medium", "moderate difference"),
            (1.20, "large", "substantial difference"),
            (2.00, "very large", "huge difference"),
            (float("inf"), "huge", "extremely large effect"),
        ],
        "direction_positive": "Group 1 > Group 2",
        "direction_negative": "Group 1 < Group 2",
    },
    "pearsons_r": {
        "name": "Pearson's r",
        "description": "Linear correlation coefficient",
        "thresholds": [
            (0.10, "negligible", "no meaningful relationship"),
            (0.30, "weak", "weak linear relationship"),
            (0.50, "moderate", "moderate linear relationship"),
            (0.70, "strong", "strong linear relationship"),
            (0.90, "very strong", "very strong linear relationship"),
            (float("inf"), "near perfect", "near-perfect linear relationship"),
        ],
        "direction_positive": "positive correlation",
        "direction_negative": "negative correlation",
    },
    "spearmans_rho": {
        "name": "Spearman's rho",
        "description": "Monotonic correlation coefficient",
        "thresholds": [
            (0.10, "negligible", "no meaningful monotonic relationship"),
            (0.30, "weak", "weak monotonic relationship"),
            (0.50, "moderate", "moderate monotonic relationship"),
            (0.70, "strong", "strong monotonic relationship"),
            (0.90, "very strong", "very strong monotonic relationship"),
            (float("inf"), "near perfect", "near-perfect monotonic relationship"),
        ],
        "direction_positive": "positive monotonic",
        "direction_negative": "negative monotonic",
    },
    "eta_squared": {
        "name": "Eta-squared",
        "description": "Proportion of variance explained (ANOVA)",
        "thresholds": [
            (0.01, "negligible", "negligible variance explained"),
            (0.06, "small", "small proportion of variance explained (~6%)"),
            (0.14, "medium", "medium proportion of variance explained (~14%)"),
            (float("inf"), "large", "large proportion of variance explained (>14%)"),
        ],
        "direction_positive": "N/A (always positive)",
        "direction_negative": "N/A",
    },
    "partial_eta_squared": {
        "name": "Partial eta-squared",
        "description": "Proportion of variance explained controlling for other factors",
        "thresholds": [
            (0.01, "negligible", "negligible unique variance explained"),
            (0.06, "small", "small unique variance explained"),
            (0.14, "medium", "medium unique variance explained"),
            (float("inf"), "large", "large unique variance explained"),
        ],
        "direction_positive": "N/A (always positive)",
        "direction_negative": "N/A",
    },
    "omega_squared": {
        "name": "Omega-squared",
        "description": "Less biased estimate of variance explained",
        "thresholds": [
            (0.01, "negligible", "negligible variance explained"),
            (0.06, "small", "small variance explained"),
            (0.14, "medium", "medium variance explained"),
            (float("inf"), "large", "large variance explained"),
        ],
        "direction_positive": "N/A (always positive)",
        "direction_negative": "N/A",
    },
    "r_squared": {
        "name": "R-squared",
        "description": "Coefficient of determination (regression)",
        "thresholds": [
            (0.02, "negligible", "negligible variance explained"),
            (0.13, "small", "small variance explained (~2-13%)"),
            (0.26, "medium", "medium variance explained (~13-26%)"),
            (float("inf"), "large", "large variance explained (>26%)"),
        ],
        "direction_positive": "N/A (always positive)",
        "direction_negative": "N/A",
    },
    "odds_ratio": {
        "name": "Odds ratio",
        "description": "Ratio of odds between groups",
        "thresholds": [
            (1.5, "negligible", "negligible association"),
            (2.5, "small", "small association"),
            (4.0, "medium", "medium association"),
            (10.0, "large", "strong association"),
            (float("inf"), "very large", "very strong association"),
        ],
        "direction_positive": "increased odds",
        "direction_negative": "decreased odds (use 1/OR)",
    },
    "risk_ratio": {
        "name": "Risk ratio",
        "description": "Relative risk between groups",
        "thresholds": [
            (1.25, "negligible", "negligible risk difference"),
            (1.50, "small", "small risk difference"),
            (2.00, "medium", "moderate risk difference"),
            (3.00, "large", "large risk difference"),
            (float("inf"), "very large", "very large risk difference"),
        ],
        "direction_positive": "increased risk",
        "direction_negative": "decreased risk (protective)",
    },
    "hazard_ratio": {
        "name": "Hazard ratio",
        "description": "Relative hazard (survival analysis)",
        "thresholds": [
            (1.25, "negligible", "negligible difference in hazard"),
            (1.50, "small", "small difference in hazard"),
            (2.00, "medium", "moderate difference in hazard"),
            (3.00, "large", "large difference in hazard"),
            (float("inf"), "very large", "very large difference in hazard"),
        ],
        "direction_positive": "increased hazard (worse outcome)",
        "direction_negative": "decreased hazard (better outcome)",
    },
    "cramers_v": {
        "name": "Cramer's V",
        "description": "Association strength for categorical data",
        "thresholds": [
            (0.10, "negligible", "negligible association"),
            (0.20, "small", "weak association"),
            (0.40, "medium", "moderate association"),
            (0.60, "large", "strong association"),
            (float("inf"), "very large", "very strong association"),
        ],
        "direction_positive": "N/A (always positive)",
        "direction_negative": "N/A",
    },
    "phi": {
        "name": "Phi coefficient",
        "description": "Association for 2x2 tables",
        "thresholds": [
            (0.10, "negligible", "negligible association"),
            (0.20, "small", "weak association"),
            (0.40, "medium", "moderate association"),
            (0.60, "large", "strong association"),
            (float("inf"), "very large", "very strong association"),
        ],
        "direction_positive": "positive association",
        "direction_negative": "negative association",
    },
    "log2_fold_change": {
        "name": "Log2 fold change",
        "description": "Relative expression change (gene expression)",
        "thresholds": [
            (0.5, "negligible", "minimal biological change (<1.4-fold)"),
            (1.0, "small", "subtle biological effect (1.4-2-fold)"),
            (2.0, "medium", "moderate biological effect (2-4-fold)"),
            (3.0, "large", "strong biological effect (4-8-fold)"),
            (float("inf"), "very large", "dramatic biological effect (>8-fold)"),
        ],
        "direction_positive": "upregulated",
        "direction_negative": "downregulated",
    },
    "cohens_h": {
        "name": "Cohen's h",
        "description": "Effect size for proportion differences",
        "thresholds": [
            (0.20, "negligible", "negligible proportion difference"),
            (0.50, "small", "small proportion difference"),
            (0.80, "medium", "medium proportion difference"),
            (float("inf"), "large", "large proportion difference"),
        ],
        "direction_positive": "Proportion 1 > Proportion 2",
        "direction_negative": "Proportion 1 < Proportion 2",
    },
    "number_needed_to_treat": {
        "name": "Number needed to treat (NNT)",
        "description": "Patients needed to treat for one benefit",
        "thresholds": [
            (2, "very large", "excellent treatment effect"),
            (5, "large", "strong treatment effect"),
            (10, "medium", "moderate treatment effect"),
            (20, "small", "small treatment effect"),
            (float("inf"), "negligible", "minimal treatment benefit"),
        ],
        "direction_positive": "N/A (lower is better)",
        "direction_negative": "N/A",
    },
    "absolute_risk_reduction": {
        "name": "Absolute risk reduction (ARR)",
        "description": "Risk_control - Risk_treated, expressed as a proportion (0-1)",
        "thresholds": [
            (0.01, "negligible", "<1 percentage-point reduction; rarely clinically meaningful"),
            (0.05, "small", "1-5 percentage-point reduction"),
            (0.10, "medium", "5-10 percentage-point reduction"),
            (0.20, "large", "10-20 percentage-point reduction"),
            (float("inf"), "very large", ">20 percentage-point reduction"),
        ],
        "direction_positive": "treatment reduces risk (benefit)",
        "direction_negative": "treatment increases risk (harm)",
    },
}


# =============================================================================
# Type alias for available metrics
# =============================================================================

EffectMetric = Literal[
    "cohens_d",
    "hedges_g",
    "pearsons_r",
    "spearmans_rho",
    "eta_squared",
    "partial_eta_squared",
    "omega_squared",
    "r_squared",
    "odds_ratio",
    "risk_ratio",
    "hazard_ratio",
    "cramers_v",
    "phi",
    "log2_fold_change",
    "cohens_h",
    "number_needed_to_treat",
    "absolute_risk_reduction",
]


# =============================================================================
# Main Interpretation Function
# =============================================================================


def interpret_effect_size(
    value: float,
    metric: EffectMetric,
) -> EffectInterpretation:
    """
    Deterministic interpretation of effect size.

    Parameters
    ----------
    value : float
        The effect size value
    metric : str
        Type of effect size metric (e.g., "cohens_d", "pearsons_r", "odds_ratio")

    Returns
    -------
    EffectInterpretation
        Complete interpretation with magnitude, context, and direction

    Raises
    ------
    ValueError
        If metric is unknown or value is invalid

    Examples
    --------
    >>> result = interpret_effect_size(0.65, "cohens_d")
    >>> result.magnitude
    'medium'
    >>> result.interpretation
    "Cohen's d = 0.65 indicates a medium effect (moderate and noticeable difference)."

    >>> result = interpret_effect_size(-0.42, "pearsons_r")
    >>> result.direction
    'negative correlation'
    """
    if metric not in EFFECT_THRESHOLDS:
        valid_metrics = ", ".join(sorted(EFFECT_THRESHOLDS.keys()))
        raise ValueError(f"Unknown metric '{metric}'. Valid metrics: {valid_metrics}")

    metric_info = EFFECT_THRESHOLDS[metric]
    thresholds = metric_info["thresholds"]
    metric_name = metric_info["name"]

    # Handle special cases for ratio metrics (OR, RR, HR, NNT)
    is_ratio_metric = metric in (
        "odds_ratio",
        "risk_ratio",
        "hazard_ratio",
        "number_needed_to_treat",
    )

    # Determine the value to compare against thresholds
    if is_ratio_metric:
        # For ratios, compare against 1 (no effect)
        # Convert values < 1 to their reciprocal for threshold comparison
        if metric == "number_needed_to_treat":
            compare_value = abs(value)
        elif value < 1:
            compare_value = 1 / value
        else:
            compare_value = value
    else:
        # For other metrics, use absolute value
        compare_value = abs(value)

    # Find the magnitude category
    magnitude = None
    context = None
    for threshold, mag, ctx in thresholds:
        if compare_value < threshold:
            magnitude = mag
            context = ctx
            break

    if magnitude is None:
        magnitude = thresholds[-1][1]
        context = thresholds[-1][2]

    # Determine direction
    if is_ratio_metric:
        if metric == "number_needed_to_treat":
            direction = "N/A (lower is better)"
        elif value >= 1:
            direction = metric_info["direction_positive"]
        else:
            direction = metric_info["direction_negative"]
    else:
        if value >= 0:
            direction = metric_info["direction_positive"]
        else:
            direction = metric_info["direction_negative"]

    # Generate interpretation text
    interpretation = _format_interpretation(
        metric, metric_name, value, magnitude, context
    )

    # Add confidence note based on magnitude
    confidence_note = _get_confidence_note(magnitude)

    return EffectInterpretation(
        metric=metric,
        metric_full_name=metric_name,
        value=value,
        magnitude=magnitude,
        interpretation=interpretation,
        context=context,
        direction=direction,
        confidence_note=confidence_note,
    )


def _format_interpretation(
    metric: str,
    metric_name: str,
    value: float,
    magnitude: str,
    context: str,
) -> str:
    """Format the interpretation string based on metric type."""

    # Formatting templates for different metric types
    templates = {
        "cohens_d": f"Cohen's d = {value:.2f} indicates a {magnitude} effect ({context}).",
        "hedges_g": f"Hedges' g = {value:.2f} indicates a {magnitude} effect ({context}).",
        "pearsons_r": f"r = {value:.3f} indicates a {magnitude} correlation ({context}).",
        "spearmans_rho": f"rho = {value:.3f} indicates a {magnitude} correlation ({context}).",
        "eta_squared": f"eta^2 = {value:.3f} indicates a {magnitude} effect ({context}).",
        "partial_eta_squared": f"partial eta^2 = {value:.3f} indicates a {magnitude} effect ({context}).",
        "omega_squared": f"omega^2 = {value:.3f} indicates a {magnitude} effect ({context}).",
        "r_squared": f"R^2 = {value:.3f} indicates a {magnitude} effect ({context}).",
        "odds_ratio": f"OR = {value:.2f} indicates a {magnitude} effect ({context}).",
        "risk_ratio": f"RR = {value:.2f} indicates a {magnitude} effect ({context}).",
        "hazard_ratio": f"HR = {value:.2f} indicates a {magnitude} effect ({context}).",
        "cramers_v": f"Cramer's V = {value:.3f} indicates a {magnitude} association ({context}).",
        "phi": f"phi = {value:.3f} indicates a {magnitude} association ({context}).",
        "log2_fold_change": f"log2FC = {value:.2f} indicates a {magnitude} effect ({context}).",
        "cohens_h": f"Cohen's h = {value:.2f} indicates a {magnitude} effect ({context}).",
        "number_needed_to_treat": f"NNT = {value:.1f} indicates a {magnitude} treatment effect ({context}).",
        "absolute_risk_reduction": f"ARR = {value*100:.1f}% indicates a {magnitude} effect ({context}).",
    }

    return templates.get(
        metric, f"{metric_name} = {value} indicates a {magnitude} effect ({context})."
    )


def _get_confidence_note(magnitude: str) -> str:
    """Get a confidence note based on effect size magnitude."""
    notes = {
        "negligible": "Effect may not be clinically or practically meaningful.",
        "very small": "Effect is likely too small to be practically important.",
        "small": "Effect may be meaningful in specific contexts; consider clinical significance.",
        "weak": "Effect is detectable but may not be practically important.",
        "medium": "Effect is clearly noticeable and likely practically meaningful.",
        "moderate": "Effect is clearly noticeable and likely practically meaningful.",
        "large": "Effect is substantial and likely has important real-world implications.",
        "strong": "Effect is substantial and clearly important.",
        "very large": "Effect is very large and has obvious practical significance.",
        "very strong": "Effect is very strong and has obvious practical significance.",
        "near perfect": "Effect is extremely strong; verify data quality.",
        "huge": "Effect is extremely large; verify data quality and methodology.",
    }
    return notes.get(magnitude, "Consider the context when interpreting this effect.")


# =============================================================================
# Utility Functions
# =============================================================================


def get_metric_info(metric: EffectMetric) -> dict:
    """
    Get detailed information about an effect size metric.

    Parameters
    ----------
    metric : str
        The effect size metric name

    Returns
    -------
    dict
        Dictionary with metric name, description, and threshold information
    """
    if metric not in EFFECT_THRESHOLDS:
        valid_metrics = ", ".join(sorted(EFFECT_THRESHOLDS.keys()))
        raise ValueError(f"Unknown metric '{metric}'. Valid metrics: {valid_metrics}")

    info = EFFECT_THRESHOLDS[metric]
    return {
        "name": info["name"],
        "description": info["description"],
        "thresholds": [
            {"upper_bound": t[0], "magnitude": t[1], "context": t[2]}
            for t in info["thresholds"]
        ],
    }


def list_available_metrics() -> list[str]:
    """Return a list of all available effect size metrics."""
    return sorted(EFFECT_THRESHOLDS.keys())


def convert_cohens_d_to_r(d: float) -> float:
    """
    Convert Cohen's d to Pearson's r.

    Parameters
    ----------
    d : float
        Cohen's d value

    Returns
    -------
    float
        Approximate Pearson's r

    Notes
    -----
    Uses the formula: r = d / sqrt(d^2 + 4)
    """
    import math

    return d / math.sqrt(d**2 + 4)


def convert_r_to_cohens_d(r: float) -> float:
    """
    Convert Pearson's r to Cohen's d.

    Parameters
    ----------
    r : float
        Pearson's r value (must be in range [-1, 1])

    Returns
    -------
    float
        Approximate Cohen's d

    Notes
    -----
    Uses the formula: d = 2r / sqrt(1 - r^2)
    """
    import math

    if not (-1 <= r <= 1):
        raise ValueError(f"r must be in range [-1, 1], got {r}")

    # Avoid division by zero at r = +/- 1
    if abs(r) >= 0.9999:
        return float("inf") if r > 0 else float("-inf")

    return 2 * r / math.sqrt(1 - r**2)


def arr_to_nnt(arr: float) -> float:
    """
    Convert absolute risk reduction (ARR) to number needed to treat (NNT).

    Parameters
    ----------
    arr : float
        Absolute risk reduction as a proportion (0-1, e.g., 0.02 for 2%).

    Returns
    -------
    float
        NNT = 1 / ARR. Always reported as a positive integer in clinical
        practice; sign indicates direction (positive ARR = benefit).

    Notes
    -----
    Use to translate relative-risk reductions into clinically interpretable
    numbers. Example: a treatment reducing event rate from 2% to 1% has
    RRR = 50% but ARR = 0.01 and NNT = 100 — treat 100 patients to prevent
    one event. Always pair RRR claims with ARR/NNT.
    """
    if arr == 0:
        raise ValueError("ARR of 0 means no effect; NNT is undefined (infinite)")
    return 1.0 / arr


def risks_to_arr_nnt(risk_control: float, risk_treated: float) -> dict:
    """
    Compute ARR, RRR, RR, and NNT from absolute risks in two arms.

    Parameters
    ----------
    risk_control : float
        Event rate in control arm (proportion 0-1).
    risk_treated : float
        Event rate in treated arm (proportion 0-1).

    Returns
    -------
    dict
        {"arr": float, "rrr": float, "rr": float, "nnt": float}

    Examples
    --------
    >>> risks_to_arr_nnt(0.02, 0.01)
    {'arr': 0.01, 'rrr': 0.5, 'rr': 0.5, 'nnt': 100.0}
    """
    if not (0 <= risk_control <= 1) or not (0 <= risk_treated <= 1):
        raise ValueError("Risks must be proportions in [0, 1]")

    arr = risk_control - risk_treated
    rr = risk_treated / risk_control if risk_control > 0 else float("nan")
    rrr = 1 - rr if risk_control > 0 else float("nan")
    nnt = 1.0 / arr if arr != 0 else float("inf")

    return {"arr": arr, "rrr": rrr, "rr": rr, "nnt": nnt}


def convert_or_to_cohens_d(odds_ratio: float) -> float:
    """
    Convert odds ratio to Cohen's d (approximate).

    Parameters
    ----------
    odds_ratio : float
        Odds ratio value (must be positive)

    Returns
    -------
    float
        Approximate Cohen's d

    Notes
    -----
    Uses the formula: d = ln(OR) * sqrt(3) / pi
    This is an approximation that assumes logistic distribution.
    """
    import math

    if odds_ratio <= 0:
        raise ValueError(f"odds_ratio must be positive, got {odds_ratio}")

    return math.log(odds_ratio) * math.sqrt(3) / math.pi


if __name__ == "__main__":
    # Example usage demonstrating deterministic output
    print("=== Effect Size Interpretation Examples ===\n")

    # Example 1: Cohen's d
    result = interpret_effect_size(0.65, "cohens_d")
    print("Cohen's d = 0.65:")
    print(f"  Magnitude: {result.magnitude}")
    print(f"  {result.interpretation}")
    print(f"  Note: {result.confidence_note}")
    print()

    # Example 2: Negative correlation
    result = interpret_effect_size(-0.42, "pearsons_r")
    print("Pearson's r = -0.42:")
    print(f"  Magnitude: {result.magnitude}")
    print(f"  Direction: {result.direction}")
    print(f"  {result.interpretation}")
    print()

    # Example 3: Odds ratio
    result = interpret_effect_size(3.5, "odds_ratio")
    print("Odds ratio = 3.5:")
    print(f"  Magnitude: {result.magnitude}")
    print(f"  {result.interpretation}")
    print()

    # Example 4: Log2 fold change (gene expression)
    result = interpret_effect_size(-1.5, "log2_fold_change")
    print("log2FC = -1.5:")
    print(f"  Magnitude: {result.magnitude}")
    print(f"  Direction: {result.direction}")
    print(f"  {result.interpretation}")
    print()

    # Conversions
    print("=== Effect Size Conversions ===\n")
    d = 0.5
    r = convert_cohens_d_to_r(d)
    print(f"Cohen's d = {d} -> r = {r:.3f}")

    r = 0.3
    d = convert_r_to_cohens_d(r)
    print(f"Pearson's r = {r} -> d = {d:.3f}")
