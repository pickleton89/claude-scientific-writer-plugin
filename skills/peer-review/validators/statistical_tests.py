#!/usr/bin/env python3
"""
Statistical Test Validator for Peer Review

Provides deterministic statistical test recommendations based on data
characteristics. Implements a decision tree for test selection and validates
whether the chosen test is appropriate.

Usage:
    from validators.statistical_tests import recommend_test, validate_test_choice

    rec = recommend_test("continuous", "2_groups", "independent", "normal")
    print(rec.test_name)  # "Independent t-test"

Author: Claude Scientific Writer Plugin
License: MIT
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class DataType(Enum):
    """Types of data for statistical analysis."""

    CONTINUOUS = "continuous"
    ORDINAL = "ordinal"
    CATEGORICAL = "categorical"
    COUNT = "count"
    TIME_TO_EVENT = "time_to_event"
    PROPORTION = "proportion"


class GroupStructure(Enum):
    """Number and structure of groups."""

    TWO_GROUPS = "2_groups"
    THREE_PLUS_GROUPS = "3+_groups"
    CORRELATION = "correlation"
    REGRESSION = "regression"


class StudyDesign(Enum):
    """Study design for comparing groups."""

    INDEPENDENT = "independent"
    PAIRED = "paired"
    REPEATED = "repeated"
    NESTED = "nested"
    FACTORIAL = "factorial"


class Distribution(Enum):
    """Distribution assumption."""

    NORMAL = "normal"
    NON_NORMAL = "non_normal"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TestRecommendation:
    """
    Deterministic statistical test recommendation.

    Attributes:
        test_name: Name of the recommended test
        assumptions: List of assumptions that must be met
        alternatives: Alternative tests if assumptions are violated
        when_to_use: Description of when this test is appropriate
        common_mistakes: Frequent errors when using this test
        reporting_requirements: What to report when using this test
    """

    test_name: str
    assumptions: Tuple[str, ...]  # Tuple for hashability
    alternatives: Tuple[str, ...]
    when_to_use: str
    common_mistakes: Tuple[str, ...] = ()
    reporting_requirements: Tuple[str, ...] = ()


# ============================================================================
# TEST SELECTION LOOKUP TABLE
# Keys: (data_type, groups, design, distribution)
# ============================================================================

TEST_SELECTION: Dict[Tuple[str, str, str, str], TestRecommendation] = {
    # =========================================================================
    # CONTINUOUS DATA - TWO GROUPS
    # =========================================================================
    ("continuous", "2_groups", "independent", "normal"): TestRecommendation(
        test_name="Independent t-test",
        assumptions=(
            "Normality of data in each group",
            "Homogeneity of variance (Levene's test)",
            "Independence of observations",
        ),
        alternatives=("Welch's t-test", "Mann-Whitney U"),
        when_to_use="Comparing means of two independent groups with normally distributed data",
        common_mistakes=(
            "Not checking normality assumption",
            "Using paired t-test for independent groups",
            "Ignoring unequal variances",
        ),
        reporting_requirements=(
            "t statistic with degrees of freedom",
            "p-value (exact, not just <0.05)",
            "Effect size (Cohen's d)",
            "95% confidence interval for difference",
            "Sample sizes per group",
        ),
    ),
    ("continuous", "2_groups", "independent", "non_normal"): TestRecommendation(
        test_name="Mann-Whitney U test",
        assumptions=(
            "Independence of observations",
            "Similar distribution shapes between groups",
            "At least ordinal data",
        ),
        alternatives=("Permutation test", "Bootstrap confidence intervals"),
        when_to_use="Comparing two independent groups with non-normal data or ordinal outcomes",
        common_mistakes=(
            "Interpreting as median comparison (compares ranks)",
            "Using with very small samples",
            "Ignoring tied values",
        ),
        reporting_requirements=(
            "U statistic",
            "p-value",
            "Effect size (rank-biserial correlation)",
            "Median and IQR per group",
            "Sample sizes",
        ),
    ),
    ("continuous", "2_groups", "paired", "normal"): TestRecommendation(
        test_name="Paired t-test",
        assumptions=(
            "Normality of differences",
            "Paired/matched observations",
            "Independence between pairs",
        ),
        alternatives=("Wilcoxon signed-rank test",),
        when_to_use="Comparing paired/matched observations (before-after, matched samples) with normal differences",
        common_mistakes=(
            "Using independent t-test for paired data",
            "Not checking normality of differences",
            "Treating repeated measures as paired",
        ),
        reporting_requirements=(
            "t statistic with degrees of freedom",
            "p-value",
            "Effect size (Cohen's d for paired data)",
            "Mean difference with 95% CI",
            "Number of pairs",
        ),
    ),
    ("continuous", "2_groups", "paired", "non_normal"): TestRecommendation(
        test_name="Wilcoxon signed-rank test",
        assumptions=(
            "Paired observations",
            "Symmetric distribution of differences",
            "At least ordinal data",
        ),
        alternatives=("Sign test", "Permutation test"),
        when_to_use="Comparing paired observations with non-normal differences",
        common_mistakes=(
            "Using for independent samples",
            "Ignoring tied differences",
            "Assuming it tests medians (tests symmetry)",
        ),
        reporting_requirements=(
            "W or V statistic",
            "p-value",
            "Effect size (matched-pairs rank-biserial)",
            "Median difference",
            "Number of pairs",
        ),
    ),
    # =========================================================================
    # CONTINUOUS DATA - THREE OR MORE GROUPS
    # =========================================================================
    ("continuous", "3+_groups", "independent", "normal"): TestRecommendation(
        test_name="One-way ANOVA",
        assumptions=(
            "Normality within each group",
            "Homogeneity of variance",
            "Independence of observations",
        ),
        alternatives=("Welch's ANOVA", "Kruskal-Wallis test"),
        when_to_use="Comparing means across 3+ independent groups with normal data",
        common_mistakes=(
            "Multiple t-tests instead of ANOVA",
            "No post-hoc tests after significant F",
            "Reporting only p-value without effect size",
        ),
        reporting_requirements=(
            "F statistic with both df values",
            "p-value",
            "Effect size (eta-squared or omega-squared)",
            "Post-hoc test results with correction",
            "Group means, SDs, and sample sizes",
        ),
    ),
    ("continuous", "3+_groups", "independent", "non_normal"): TestRecommendation(
        test_name="Kruskal-Wallis test",
        assumptions=(
            "Independence of observations",
            "Similar distribution shapes",
            "At least ordinal data",
        ),
        alternatives=("Permutation ANOVA", "Bootstrap methods"),
        when_to_use="Comparing 3+ independent groups with non-normal data",
        common_mistakes=(
            "No post-hoc tests after significant result",
            "Treating as median comparison",
        ),
        reporting_requirements=(
            "H statistic with df",
            "p-value",
            "Effect size (epsilon-squared)",
            "Post-hoc (Dunn's test) with correction",
            "Median and IQR per group",
        ),
    ),
    ("continuous", "3+_groups", "repeated", "normal"): TestRecommendation(
        test_name="Repeated measures ANOVA",
        assumptions=(
            "Normality",
            "Sphericity (test with Mauchly's)",
            "No missing data (or use mixed models)",
        ),
        alternatives=("Friedman test", "Mixed-effects model"),
        when_to_use="Comparing 3+ conditions measured on the same subjects",
        common_mistakes=(
            "Ignoring sphericity violation",
            "Not using Greenhouse-Geisser correction",
            "Excluding subjects with missing data",
        ),
        reporting_requirements=(
            "F statistic with both df values",
            "Sphericity test result (Mauchly's)",
            "Epsilon and correction used if sphericity violated",
            "Effect size (partial eta-squared)",
            "Post-hoc comparisons with correction",
        ),
    ),
    ("continuous", "3+_groups", "repeated", "non_normal"): TestRecommendation(
        test_name="Friedman test",
        assumptions=(
            "Repeated/matched observations",
            "At least ordinal data",
            "Complete cases (or handle missing)",
        ),
        alternatives=("Permutation test", "Mixed-effects model"),
        when_to_use="Comparing 3+ related groups with non-normal data",
        common_mistakes=(
            "Using for independent groups",
            "No post-hoc after significant result",
        ),
        reporting_requirements=(
            "Chi-square statistic with df",
            "p-value",
            "Effect size (Kendall's W)",
            "Post-hoc (Nemenyi or Conover) results",
            "Median per condition",
        ),
    ),
    ("continuous", "3+_groups", "nested", "normal"): TestRecommendation(
        test_name="Mixed-effects model",
        assumptions=(
            "Normality of residuals",
            "Random effects structure correctly specified",
            "Independence at highest level",
        ),
        alternatives=("GEE", "Nested ANOVA"),
        when_to_use="Data with hierarchical/nested structure (e.g., cells within animals within groups)",
        common_mistakes=(
            "Using fixed effects only",
            "Wrong random effects structure",
            "Treating technical replicates as biological",
        ),
        reporting_requirements=(
            "Fixed effects estimates with SE",
            "Random effects variance components",
            "Model comparison (if applicable)",
            "Residual diagnostics",
            "Sample sizes at each level",
        ),
    ),
    # =========================================================================
    # CATEGORICAL DATA
    # =========================================================================
    ("categorical", "2_groups", "independent", "unknown"): TestRecommendation(
        test_name="Chi-square test",
        assumptions=(
            "Expected frequencies ≥ 5 in each cell",
            "Independence of observations",
            "Mutually exclusive categories",
        ),
        alternatives=("Fisher's exact test",),
        when_to_use="Comparing proportions between two independent groups (2×2 table or larger)",
        common_mistakes=(
            "Using with small expected frequencies",
            "Applying to paired data",
            "Not checking expected frequencies",
        ),
        reporting_requirements=(
            "Chi-square statistic with df",
            "p-value",
            "Effect size (Cramér's V or phi)",
            "Observed and expected frequencies",
            "Total N",
        ),
    ),
    ("categorical", "2_groups", "independent", "normal"): TestRecommendation(
        test_name="Fisher's exact test",
        assumptions=(
            "Independence of observations",
            "Fixed marginal totals (for exact test)",
        ),
        alternatives=("Chi-square test", "Barnard's test"),
        when_to_use="Comparing proportions with small samples or when expected frequencies < 5",
        common_mistakes=(
            "Using chi-square with small samples",
            "Misinterpreting odds ratio as relative risk",
        ),
        reporting_requirements=(
            "p-value (exact)",
            "Odds ratio with 95% CI",
            "Cell frequencies",
            "Total N",
        ),
    ),
    ("categorical", "2_groups", "paired", "unknown"): TestRecommendation(
        test_name="McNemar's test",
        assumptions=(
            "Paired/matched observations",
            "Binary outcome",
            "Independence between pairs",
        ),
        alternatives=("Exact McNemar's test",),
        when_to_use="Comparing proportions in paired/matched samples (before-after on same subjects)",
        common_mistakes=(
            "Using chi-square for paired data",
            "Not using exact test for small discordant pairs",
        ),
        reporting_requirements=(
            "Chi-square or exact p-value",
            "Discordant pair counts",
            "Proportions at each time point",
            "Number of pairs",
        ),
    ),
    # =========================================================================
    # TIME-TO-EVENT DATA
    # =========================================================================
    ("time_to_event", "2_groups", "independent", "unknown"): TestRecommendation(
        test_name="Log-rank test",
        assumptions=(
            "Non-informative censoring",
            "Proportional hazards (for interpretation)",
            "Independence of observations",
        ),
        alternatives=("Wilcoxon-Gehan test", "Cox regression"),
        when_to_use="Comparing survival/time-to-event between two groups",
        common_mistakes=(
            "Using when hazards are not proportional",
            "Ignoring censoring in analysis",
            "Not showing Kaplan-Meier curves",
        ),
        reporting_requirements=(
            "Chi-square statistic",
            "p-value",
            "Hazard ratio with 95% CI (from Cox)",
            "Median survival per group",
            "Kaplan-Meier curves",
            "Number at risk table",
        ),
    ),
    ("time_to_event", "3+_groups", "independent", "unknown"): TestRecommendation(
        test_name="Log-rank test (stratified) or Cox regression",
        assumptions=(
            "Non-informative censoring",
            "Proportional hazards",
            "Independence of observations",
        ),
        alternatives=("Stratified log-rank", "Parametric survival models"),
        when_to_use="Comparing survival across 3+ groups or adjusting for covariates",
        common_mistakes=(
            "Not checking proportional hazards assumption",
            "Ignoring time-varying covariates",
        ),
        reporting_requirements=(
            "Hazard ratios with 95% CI",
            "p-values for each comparison",
            "Proportional hazards test result",
            "Kaplan-Meier curves",
            "Events per group",
        ),
    ),
    # =========================================================================
    # CORRELATION AND REGRESSION
    # =========================================================================
    ("continuous", "correlation", "independent", "normal"): TestRecommendation(
        test_name="Pearson correlation",
        assumptions=(
            "Bivariate normality",
            "Linear relationship",
            "Independence of observations",
            "No extreme outliers",
        ),
        alternatives=("Spearman correlation", "Robust correlation"),
        when_to_use="Measuring linear association between two continuous variables",
        common_mistakes=(
            "Assuming causation from correlation",
            "Ignoring outliers",
            "Not checking linearity",
        ),
        reporting_requirements=(
            "r value",
            "p-value",
            "95% CI for r",
            "Scatterplot",
            "Sample size",
        ),
    ),
    ("continuous", "correlation", "independent", "non_normal"): TestRecommendation(
        test_name="Spearman correlation",
        assumptions=(
            "Monotonic relationship",
            "At least ordinal data",
            "Independence of observations",
        ),
        alternatives=("Kendall's tau", "Robust correlation"),
        when_to_use="Measuring monotonic association with non-normal data or ordinal outcomes",
        common_mistakes=(
            "Using for non-monotonic relationships",
            "Interpreting as Pearson equivalent",
        ),
        reporting_requirements=(
            "rho value",
            "p-value",
            "Sample size",
            "Scatterplot",
        ),
    ),
}


def recommend_test(
    data_type: str,
    groups: str,
    design: str,
    distribution: str,
) -> Optional[TestRecommendation]:
    """
    Get deterministic test recommendation based on data characteristics.

    Args:
        data_type: Type of data (continuous, categorical, etc.)
        groups: Group structure (2_groups, 3+_groups, correlation)
        design: Study design (independent, paired, repeated, nested)
        distribution: Distribution assumption (normal, non_normal, unknown)

    Returns:
        TestRecommendation if found, None otherwise

    Examples:
        >>> rec = recommend_test("continuous", "2_groups", "independent", "normal")
        >>> rec.test_name
        "Independent t-test"
    """
    key = (data_type.lower(), groups.lower(), design.lower(), distribution.lower())
    return TEST_SELECTION.get(key)


def get_all_tests_for_design(design: str) -> List[TestRecommendation]:
    """
    Get all test recommendations for a specific study design.

    Args:
        design: Study design (independent, paired, repeated, nested)

    Returns:
        List of TestRecommendation objects for that design
    """
    return [
        test
        for key, test in TEST_SELECTION.items()
        if key[2].lower() == design.lower()
    ]


def get_all_tests_for_data_type(data_type: str) -> List[TestRecommendation]:
    """
    Get all test recommendations for a specific data type.

    Args:
        data_type: Type of data (continuous, categorical, etc.)

    Returns:
        List of TestRecommendation objects for that data type
    """
    return [
        test
        for key, test in TEST_SELECTION.items()
        if key[0].lower() == data_type.lower()
    ]


def validate_test_choice(
    chosen_test: str,
    data_type: str,
    groups: str,
    design: str,
    distribution: str,
) -> Tuple[bool, str, Optional[TestRecommendation]]:
    """
    Validate whether a chosen test is appropriate for the data.

    Args:
        chosen_test: Name of the test being used
        data_type: Type of data
        groups: Group structure
        design: Study design
        distribution: Distribution assumption

    Returns:
        Tuple of (is_appropriate, message, recommended_test)

    Examples:
        >>> valid, msg, rec = validate_test_choice(
        ...     "t-test", "continuous", "2_groups", "independent", "normal"
        ... )
        >>> valid
        True
    """
    recommended = recommend_test(data_type, groups, design, distribution)

    if recommended is None:
        return (False, "No recommendation found for this data structure", None)

    # Normalize test names for comparison
    chosen_lower = chosen_test.lower().replace("-", " ").replace("_", " ")
    recommended_lower = recommended.test_name.lower().replace("-", " ")

    # Check if chosen test matches recommendation
    if chosen_lower in recommended_lower or recommended_lower in chosen_lower:
        return (True, f"Appropriate choice: {recommended.test_name}", recommended)

    # Check if it's a valid alternative
    for alt in recommended.alternatives:
        alt_normalized = alt.lower().replace("-", " ").replace("_", " ")
        if chosen_lower in alt_normalized or alt_normalized in chosen_lower:
            return (
                True,
                f"Acceptable alternative to {recommended.test_name}",
                recommended,
            )

    return (
        False,
        f"Consider using {recommended.test_name} instead of {chosen_test}. "
        f"Reason: {recommended.when_to_use}",
        recommended,
    )


def format_recommendation(rec: TestRecommendation) -> str:
    """
    Format a test recommendation as readable text.

    Args:
        rec: TestRecommendation to format

    Returns:
        Formatted string
    """
    lines = [
        f"Recommended Test: {rec.test_name}",
        "",
        f"When to use: {rec.when_to_use}",
        "",
        "Assumptions:",
    ]
    for assumption in rec.assumptions:
        lines.append(f"  - {assumption}")

    if rec.alternatives:
        lines.append("")
        lines.append("Alternatives if assumptions violated:")
        for alt in rec.alternatives:
            lines.append(f"  - {alt}")

    if rec.reporting_requirements:
        lines.append("")
        lines.append("Reporting requirements:")
        for req in rec.reporting_requirements:
            lines.append(f"  - {req}")

    if rec.common_mistakes:
        lines.append("")
        lines.append("Common mistakes to avoid:")
        for mistake in rec.common_mistakes:
            lines.append(f"  - {mistake}")

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo usage
    print("Statistical Test Validator Demo")
    print("=" * 50)

    # Example: Two independent groups, normal data
    rec = recommend_test("continuous", "2_groups", "independent", "normal")
    if rec:
        print(format_recommendation(rec))

    print("\n" + "=" * 50)

    # Validate a test choice
    valid, msg, rec = validate_test_choice(
        "Mann-Whitney", "continuous", "2_groups", "independent", "normal"
    )
    print("\nValidating 'Mann-Whitney' for normal independent data:")
    print(f"  Valid: {valid}")
    print(f"  Message: {msg}")
