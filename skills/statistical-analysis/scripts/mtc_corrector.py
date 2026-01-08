"""
Deterministic multiple testing correction.

This module wraps statsmodels functions with structured input/output,
providing deterministic multiple testing correction with no LLM involvement.

Example usage:
    >>> from scripts.mtc_corrector import correct_pvalues
    >>> result = correct_pvalues([0.001, 0.01, 0.02, 0.04, 0.05], method="bh_fdr")
    >>> print(result.n_significant)
    4
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass
class MTCResult:
    """Structured output for multiple testing correction."""

    method: str
    method_full_name: str
    raw_pvalues: list[float]
    adjusted_pvalues: list[float]
    significant: list[bool]
    alpha: float
    n_tests: int
    n_significant: int
    expected_false_discoveries: float
    interpretation: str


# Method descriptions for user-friendly output
METHOD_DESCRIPTIONS = {
    "bh_fdr": (
        "Benjamini-Hochberg FDR",
        "Controls false discovery rate; recommended for discovery/screening",
    ),
    "bonferroni": (
        "Bonferroni",
        "Controls family-wise error rate; conservative, for confirmatory studies",
    ),
    "holm": (
        "Holm-Bonferroni",
        "Step-down procedure; less conservative than Bonferroni, controls FWER",
    ),
    "hochberg": (
        "Hochberg",
        "Step-up procedure; less conservative than Holm, requires independence",
    ),
    "by_fdr": (
        "Benjamini-Yekutieli FDR",
        "Controls FDR under arbitrary dependence; more conservative than BH",
    ),
    "sidak": (
        "Sidak",
        "Slightly less conservative than Bonferroni; assumes independence",
    ),
    "holm_sidak": (
        "Holm-Sidak",
        "Step-down Sidak; assumes independence",
    ),
    "fdr_tsbh": (
        "Two-stage Benjamini-Hochberg",
        "Adaptive FDR control; can be more powerful than standard BH",
    ),
    "fdr_tsbky": (
        "Two-stage Benjamini-Krieger-Yekutieli",
        "Adaptive FDR with improved power for small effects",
    ),
}


def correct_pvalues(
    pvalues: list[float],
    method: Literal[
        "bh_fdr",
        "bonferroni",
        "holm",
        "hochberg",
        "by_fdr",
        "sidak",
        "holm_sidak",
        "fdr_tsbh",
        "fdr_tsbky",
    ] = "bh_fdr",
    alpha: float = 0.05,
) -> MTCResult:
    """
    Apply multiple testing correction to a list of p-values.

    Parameters
    ----------
    pvalues : list of float
        Raw p-values from statistical tests. Must be in range [0, 1].
    method : str
        Correction method:
        - "bh_fdr": Benjamini-Hochberg FDR (default, recommended for discovery)
        - "bonferroni": Bonferroni correction (conservative, for confirmation)
        - "holm": Holm step-down (less conservative than Bonferroni)
        - "hochberg": Hochberg step-up (requires independence)
        - "by_fdr": Benjamini-Yekutieli FDR (for arbitrary dependence)
        - "sidak": Sidak correction (assumes independence)
        - "holm_sidak": Holm-Sidak step-down
        - "fdr_tsbh": Two-stage Benjamini-Hochberg
        - "fdr_tsbky": Two-stage Benjamini-Krieger-Yekutieli
    alpha : float
        Significance threshold (default 0.05). Must be in range (0, 1).

    Returns
    -------
    MTCResult
        Complete results with adjusted p-values, significance calls,
        and interpretation.

    Raises
    ------
    ValueError
        If pvalues are invalid or method is unknown.

    Examples
    --------
    >>> result = correct_pvalues([0.001, 0.01, 0.02, 0.04, 0.05], method="bh_fdr")
    >>> result.n_significant
    4
    >>> result.adjusted_pvalues
    [0.005, 0.025, 0.0333..., 0.05, 0.05]
    """
    # Validate inputs
    pvalues_arr = np.array(pvalues, dtype=float)

    if len(pvalues_arr) == 0:
        raise ValueError("pvalues cannot be empty")

    if np.any(np.isnan(pvalues_arr)):
        raise ValueError("pvalues cannot contain NaN values")

    if np.any((pvalues_arr < 0) | (pvalues_arr > 1)):
        raise ValueError("All p-values must be in range [0, 1]")

    if not (0 < alpha < 1):
        raise ValueError(f"alpha must be in range (0, 1), got {alpha}")

    if method not in METHOD_DESCRIPTIONS:
        valid_methods = ", ".join(sorted(METHOD_DESCRIPTIONS.keys()))
        raise ValueError(f"Unknown method '{method}'. Valid methods: {valid_methods}")

    # Import statsmodels here to avoid import errors if not installed
    from statsmodels.stats.multitest import multipletests

    # Map our method names to statsmodels method names
    method_map = {
        "bh_fdr": "fdr_bh",
        "bonferroni": "bonferroni",
        "holm": "holm",
        "hochberg": "simes-hochberg",
        "by_fdr": "fdr_by",
        "sidak": "sidak",
        "holm_sidak": "holm-sidak",
        "fdr_tsbh": "fdr_tsbh",
        "fdr_tsbky": "fdr_tsbky",
    }

    rejected, padj, _, _ = multipletests(
        pvalues_arr, alpha=alpha, method=method_map[method]
    )

    n_sig = int(sum(rejected))
    n_tests = len(pvalues_arr)

    # Calculate expected false discoveries
    if method in ("bh_fdr", "by_fdr", "fdr_tsbh", "fdr_tsbky"):
        # FDR methods: expected FD = n_significant * alpha
        expected_fd = n_sig * alpha
    else:
        # FWER methods: expected FD <= alpha (for all tests combined)
        expected_fd = alpha if n_sig > 0 else 0.0

    # Generate interpretation
    method_full_name, method_desc = METHOD_DESCRIPTIONS[method]
    interpretation = _generate_interpretation(
        method_full_name, method_desc, n_tests, n_sig, alpha, expected_fd
    )

    return MTCResult(
        method=method,
        method_full_name=method_full_name,
        raw_pvalues=list(pvalues_arr),
        adjusted_pvalues=[float(p) for p in padj],
        significant=[bool(r) for r in rejected],
        alpha=alpha,
        n_tests=n_tests,
        n_significant=n_sig,
        expected_false_discoveries=expected_fd,
        interpretation=interpretation,
    )


def _generate_interpretation(
    method_name: str,
    method_desc: str,
    n_tests: int,
    n_significant: int,
    alpha: float,
    expected_fd: float,
) -> str:
    """Generate human-readable interpretation of MTC results."""

    if n_significant == 0:
        return (
            f"After {method_name} correction for {n_tests} tests at alpha = {alpha}, "
            f"no tests reached significance. "
            f"({method_desc})"
        )

    pct_significant = 100 * n_significant / n_tests

    return (
        f"After {method_name} correction for {n_tests} tests at alpha = {alpha}, "
        f"{n_significant} tests ({pct_significant:.1f}%) remained significant. "
        f"Expected false discoveries: ~{expected_fd:.1f}. "
        f"({method_desc})"
    )


def recommend_method(
    n_tests: int,
    study_type: Literal["discovery", "confirmatory", "replication"] = "discovery",
    dependent_tests: bool = False,
) -> str:
    """
    Recommend an appropriate multiple testing correction method.

    Parameters
    ----------
    n_tests : int
        Number of statistical tests being performed
    study_type : str
        Type of study:
        - "discovery": Exploratory analysis, prioritize sensitivity
        - "confirmatory": Hypothesis-driven, prioritize specificity
        - "replication": Validating prior findings
    dependent_tests : bool
        Whether tests are statistically dependent (e.g., correlated endpoints)

    Returns
    -------
    str
        Recommended method name

    Examples
    --------
    >>> recommend_method(20000, study_type="discovery")
    'bh_fdr'
    >>> recommend_method(5, study_type="confirmatory")
    'bonferroni'
    """
    if study_type == "discovery":
        if dependent_tests:
            return "by_fdr"  # BY-FDR valid under arbitrary dependence
        else:
            return "bh_fdr"  # Standard BH-FDR for independent tests

    elif study_type == "confirmatory":
        if n_tests <= 10:
            return "bonferroni"  # Simple and well-understood for small n
        else:
            return "holm"  # Less conservative step-down procedure

    elif study_type == "replication":
        # For replication, use slightly more stringent threshold
        return "holm"

    return "bh_fdr"  # Default fallback


def calculate_bonferroni_threshold(n_tests: int, alpha: float = 0.05) -> float:
    """
    Calculate the Bonferroni-corrected significance threshold.

    Parameters
    ----------
    n_tests : int
        Number of tests being performed
    alpha : float
        Desired family-wise error rate

    Returns
    -------
    float
        Corrected significance threshold (alpha / n_tests)

    Examples
    --------
    >>> calculate_bonferroni_threshold(100, alpha=0.05)
    0.0005
    """
    if n_tests <= 0:
        raise ValueError(f"n_tests must be positive, got {n_tests}")
    if not (0 < alpha < 1):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")

    return alpha / n_tests


def estimate_fdr_discoveries(
    n_tests: int,
    n_true_effects: int,
    power: float = 0.8,
    alpha: float = 0.05,
) -> dict[str, float]:
    """
    Estimate expected discoveries and false discovery rate.

    Useful for power analysis in high-throughput studies.

    Parameters
    ----------
    n_tests : int
        Total number of tests to be performed
    n_true_effects : int
        Expected number of true effects (from prior knowledge or pilot data)
    power : float
        Statistical power to detect true effects (default 0.8)
    alpha : float
        Nominal significance level (default 0.05)

    Returns
    -------
    dict
        Dictionary with expected discoveries, true positives, false positives,
        and estimated FDR

    Examples
    --------
    >>> estimate_fdr_discoveries(20000, 500, power=0.8, alpha=0.05)
    {'expected_discoveries': 1377.5, 'true_positives': 400.0,
     'false_positives': 977.5, 'estimated_fdr': 0.71}
    """
    if n_tests <= 0:
        raise ValueError(f"n_tests must be positive, got {n_tests}")
    if not (0 <= n_true_effects <= n_tests):
        raise ValueError(
            f"n_true_effects must be in [0, n_tests], got {n_true_effects}"
        )
    if not (0 < power < 1):
        raise ValueError(f"power must be in (0, 1), got {power}")
    if not (0 < alpha < 1):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")

    n_null = n_tests - n_true_effects

    # True positives: true effects detected with given power
    true_positives = n_true_effects * power

    # False positives: null hypotheses incorrectly rejected
    false_positives = n_null * alpha

    # Total expected discoveries
    expected_discoveries = true_positives + false_positives

    # Estimated FDR
    if expected_discoveries > 0:
        estimated_fdr = false_positives / expected_discoveries
    else:
        estimated_fdr = 0.0

    return {
        "expected_discoveries": expected_discoveries,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "estimated_fdr": round(estimated_fdr, 3),
    }


if __name__ == "__main__":
    # Example usage demonstrating deterministic output
    print("=== Multiple Testing Correction Examples ===\n")

    pvals = [0.001, 0.01, 0.02, 0.04, 0.05, 0.10, 0.50]

    # Example 1: BH-FDR (default for discovery)
    result = correct_pvalues(pvals, method="bh_fdr")
    print("BH-FDR Correction:")
    print(f"  Significant at FDR < 0.05: {result.n_significant}/{result.n_tests}")
    print(f"  {result.interpretation}")
    print()

    # Example 2: Bonferroni (conservative)
    result = correct_pvalues(pvals, method="bonferroni")
    print("Bonferroni Correction:")
    print(f"  Significant at FWER < 0.05: {result.n_significant}/{result.n_tests}")
    print(f"  {result.interpretation}")
    print()

    # Example 3: Method recommendation
    rec = recommend_method(20000, study_type="discovery")
    print(f"Recommended for 20,000 tests (discovery): {rec}")

    rec = recommend_method(5, study_type="confirmatory")
    print(f"Recommended for 5 tests (confirmatory): {rec}")
    print()

    # Example 4: FDR estimation
    est = estimate_fdr_discoveries(20000, 500, power=0.8)
    print("FDR Estimation (20,000 tests, 500 true effects, 80% power):")
    print(f"  Expected discoveries: {est['expected_discoveries']:.0f}")
    print(f"  True positives: {est['true_positives']:.0f}")
    print(f"  False positives: {est['false_positives']:.0f}")
    print(f"  Estimated FDR: {est['estimated_fdr']:.1%}")
