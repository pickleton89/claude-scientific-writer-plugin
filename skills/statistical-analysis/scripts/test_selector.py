"""
Deterministic statistical test selection from data characteristics.

This module encodes the decision trees from SKILL.md as executable Python code,
eliminating LLM interpretation variance from test selection.

Example usage:
    >>> from scripts.test_selector import select_test, OutcomeType, Distribution, Design
    >>> result = select_test(
    ...     outcome_type=OutcomeType.CONTINUOUS,
    ...     distribution=Distribution.NON_NORMAL,
    ...     design=Design.INDEPENDENT,
    ...     n_groups=2
    ... )
    >>> print(result.test_name)
    'Mann-Whitney U'
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OutcomeType(Enum):
    """Type of outcome variable being analyzed."""

    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"
    COUNT = "count"
    TIME_TO_EVENT = "time_to_event"
    PROPORTION = "proportion"


class Distribution(Enum):
    """Distribution characteristics of the data."""

    NORMAL = "normal"
    NON_NORMAL = "non_normal"
    UNKNOWN = "unknown"


class Design(Enum):
    """Study design type."""

    INDEPENDENT = "independent"
    PAIRED = "paired"
    REPEATED_MEASURES = "repeated_measures"


@dataclass
class TestRecommendation:
    """Structured output for test selection."""

    test_name: str
    parametric: bool
    assumptions: list[str]
    python_code: str
    r_code: str
    post_hoc: Optional[str] = None
    effect_size_metric: str = "Cohen's d"
    notes: Optional[str] = None


# =============================================================================
# Code Templates for Statistical Tests
# =============================================================================

TEST_PYTHON_CODE = {
    # Two-group comparisons
    "welch_t_test": """from scipy import stats
t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)""",
    "student_t_test": """from scipy import stats
t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=True)""",
    "mann_whitney_u": """from scipy import stats
u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')""",
    "paired_t_test": """from scipy import stats
t_stat, p_value = stats.ttest_rel(before, after)""",
    "wilcoxon_signed_rank": """from scipy import stats
stat, p_value = stats.wilcoxon(before, after)""",
    # Multi-group comparisons
    "one_way_anova": """from scipy import stats
f_stat, p_value = stats.f_oneway(group1, group2, group3)""",
    "welch_anova": """from scipy import stats
# Welch's ANOVA for unequal variances
from scipy.stats import alexandergovern
stat, p_value = alexandergovern(group1, group2, group3)""",
    "kruskal_wallis": """from scipy import stats
h_stat, p_value = stats.kruskal(group1, group2, group3)""",
    "repeated_measures_anova": """import pingouin as pg
# Requires data in long format with subject, condition, and value columns
aov = pg.rm_anova(data=df, dv='value', within='condition', subject='subject')
print(aov)""",
    "friedman": """from scipy import stats
stat, p_value = stats.friedmanchisquare(condition1, condition2, condition3)""",
    # Categorical tests
    "chi_square": """from scipy import stats
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)""",
    "fisher_exact": """from scipy import stats
odds_ratio, p_value = stats.fisher_exact(contingency_table)""",
    "mcnemar": """from statsmodels.stats.contingency_tables import mcnemar
result = mcnemar(contingency_table, exact=True)
p_value = result.pvalue""",
    # Correlation tests
    "pearson_correlation": """from scipy import stats
r, p_value = stats.pearsonr(x, y)""",
    "spearman_correlation": """from scipy import stats
rho, p_value = stats.spearmanr(x, y)""",
    "kendall_correlation": """from scipy import stats
tau, p_value = stats.kendalltau(x, y)""",
    # Proportion tests
    "z_test_proportions": """from statsmodels.stats.proportion import proportions_ztest
count = np.array([successes1, successes2])
nobs = np.array([n1, n2])
stat, p_value = proportions_ztest(count, nobs)""",
    # Survival analysis
    "log_rank": """from lifelines.statistics import logrank_test
result = logrank_test(durations_A, durations_B, event_observed_A, event_observed_B)
p_value = result.p_value""",
    # Post-hoc tests
    "tukey_hsd": """from scipy import stats
result = stats.tukey_hsd(group1, group2, group3)
print(result)""",
    "dunn_test": """import scikit_posthocs as sp
p_values = sp.posthoc_dunn([group1, group2, group3], p_adjust='bonferroni')""",
    "games_howell": """import pingouin as pg
posthoc = pg.pairwise_gameshowell(data=df, dv='value', between='group')""",
}

TEST_R_CODE = {
    # Two-group comparisons
    "welch_t_test": "t.test(group1, group2)  # Welch's t-test (default)",
    "student_t_test": "t.test(group1, group2, var.equal = TRUE)",
    "mann_whitney_u": "wilcox.test(group1, group2, exact = FALSE)",
    "paired_t_test": "t.test(before, after, paired = TRUE)",
    "wilcoxon_signed_rank": "wilcox.test(before, after, paired = TRUE)",
    # Multi-group comparisons
    "one_way_anova": "summary(aov(value ~ group, data = df))",
    "welch_anova": "oneway.test(value ~ group, data = df, var.equal = FALSE)",
    "kruskal_wallis": "kruskal.test(value ~ group, data = df)",
    "repeated_measures_anova": "library(ez); ezANOVA(data, dv=.(value), wid=.(subject), within=.(condition))",
    "friedman": "friedman.test(y ~ condition | subject, data = df)",
    # Categorical tests
    "chi_square": "chisq.test(contingency_table)",
    "fisher_exact": "fisher.test(contingency_table)",
    "mcnemar": "mcnemar.test(contingency_table)",
    # Correlation tests
    "pearson_correlation": "cor.test(x, y, method = 'pearson')",
    "spearman_correlation": "cor.test(x, y, method = 'spearman')",
    "kendall_correlation": "cor.test(x, y, method = 'kendall')",
    # Proportion tests
    "z_test_proportions": "prop.test(c(successes1, successes2), c(n1, n2))",
    # Survival analysis
    "log_rank": "library(survival); survdiff(Surv(time, event) ~ group, data = df)",
    # Post-hoc tests
    "tukey_hsd": "TukeyHSD(aov_model)",
    "dunn_test": "library(dunn.test); dunn.test(value, group, method = 'bonferroni')",
    "games_howell": "library(rstatix); games_howell_test(df, value ~ group)",
}

POST_HOC_TESTS = {
    "one_way_anova": ("Tukey HSD", "tukey_hsd"),
    "welch_anova": ("Games-Howell", "games_howell"),
    "kruskal_wallis": ("Dunn's test with Bonferroni correction", "dunn_test"),
    "friedman": ("Nemenyi test", None),
    "chi_square": ("Pairwise chi-square with Bonferroni correction", None),
}


# =============================================================================
# Main Test Selection Functions
# =============================================================================


def select_test(
    outcome_type: OutcomeType,
    distribution: Distribution,
    design: Design,
    n_groups: int,
    variance_equal: Optional[bool] = None,
    expected_counts_sufficient: bool = True,
    sample_size_adequate: bool = True,
) -> TestRecommendation:
    """
    Deterministic test selection from data characteristics.

    This function encodes the decision trees from the statistical-analysis
    skill as executable Python code, eliminating LLM interpretation variance.

    Parameters
    ----------
    outcome_type : OutcomeType
        Type of outcome variable (continuous, categorical, ordinal, count, time_to_event)
    distribution : Distribution
        Distribution of the data (normal, non_normal, unknown)
    design : Design
        Study design (independent, paired, repeated_measures)
    n_groups : int
        Number of groups being compared (must be >= 1)
    variance_equal : bool, optional
        Whether variances are equal across groups (for parametric tests)
    expected_counts_sufficient : bool
        For categorical data, whether expected cell counts >= 5
    sample_size_adequate : bool
        Whether sample size is adequate for the test (n >= 30 for CLT)

    Returns
    -------
    TestRecommendation
        Complete recommendation with test name, code, and metadata

    Raises
    ------
    ValueError
        If no test recommendation exists for the given parameters

    Examples
    --------
    >>> result = select_test(
    ...     outcome_type=OutcomeType.CONTINUOUS,
    ...     distribution=Distribution.NORMAL,
    ...     design=Design.INDEPENDENT,
    ...     n_groups=2,
    ...     variance_equal=False
    ... )
    >>> result.test_name
    "Welch's t-test"
    """
    # Validate inputs
    if n_groups < 1:
        raise ValueError(f"n_groups must be >= 1, got {n_groups}")

    # === CONTINUOUS OUTCOME ===
    if outcome_type == OutcomeType.CONTINUOUS:
        return _select_continuous_test(distribution, design, n_groups, variance_equal)

    # === CATEGORICAL OUTCOME ===
    if outcome_type == OutcomeType.CATEGORICAL:
        return _select_categorical_test(design, n_groups, expected_counts_sufficient)

    # === ORDINAL OUTCOME ===
    if outcome_type == OutcomeType.ORDINAL:
        return _select_ordinal_test(design, n_groups)

    # === COUNT OUTCOME ===
    if outcome_type == OutcomeType.COUNT:
        return _select_count_test(design, n_groups)

    # === TIME-TO-EVENT OUTCOME ===
    if outcome_type == OutcomeType.TIME_TO_EVENT:
        return _select_survival_test(n_groups)

    # === PROPORTION OUTCOME ===
    if outcome_type == OutcomeType.PROPORTION:
        return _select_proportion_test(design, n_groups)

    raise ValueError(
        f"No test recommendation for: {outcome_type}, {distribution}, "
        f"{design}, n_groups={n_groups}"
    )


def _select_continuous_test(
    distribution: Distribution,
    design: Design,
    n_groups: int,
    variance_equal: Optional[bool],
) -> TestRecommendation:
    """Select test for continuous outcome."""

    # === Two Groups ===
    if n_groups == 2:
        if design == Design.INDEPENDENT:
            if distribution == Distribution.NORMAL:
                if variance_equal:
                    return TestRecommendation(
                        test_name="Student's t-test",
                        parametric=True,
                        assumptions=[
                            "normal distribution",
                            "equal variances",
                            "independent samples",
                        ],
                        python_code=TEST_PYTHON_CODE["student_t_test"],
                        r_code=TEST_R_CODE["student_t_test"],
                        effect_size_metric="Cohen's d",
                    )
                else:
                    return TestRecommendation(
                        test_name="Welch's t-test",
                        parametric=True,
                        assumptions=[
                            "normal distribution",
                            "independent samples",
                        ],
                        python_code=TEST_PYTHON_CODE["welch_t_test"],
                        r_code=TEST_R_CODE["welch_t_test"],
                        effect_size_metric="Cohen's d",
                        notes="Recommended default for two-group comparison; robust to unequal variances",
                    )
            else:  # non-normal or unknown
                return TestRecommendation(
                    test_name="Mann-Whitney U",
                    parametric=False,
                    assumptions=[
                        "independent samples",
                        "ordinal or continuous outcome",
                    ],
                    python_code=TEST_PYTHON_CODE["mann_whitney_u"],
                    r_code=TEST_R_CODE["mann_whitney_u"],
                    effect_size_metric="rank-biserial correlation",
                )

        elif design == Design.PAIRED:
            if distribution == Distribution.NORMAL:
                return TestRecommendation(
                    test_name="Paired t-test",
                    parametric=True,
                    assumptions=[
                        "normal distribution of differences",
                        "paired samples",
                    ],
                    python_code=TEST_PYTHON_CODE["paired_t_test"],
                    r_code=TEST_R_CODE["paired_t_test"],
                    effect_size_metric="Cohen's d (paired)",
                )
            else:
                return TestRecommendation(
                    test_name="Wilcoxon signed-rank",
                    parametric=False,
                    assumptions=[
                        "symmetric distribution of differences",
                        "paired samples",
                    ],
                    python_code=TEST_PYTHON_CODE["wilcoxon_signed_rank"],
                    r_code=TEST_R_CODE["wilcoxon_signed_rank"],
                    effect_size_metric="matched-pairs rank-biserial correlation",
                )

    # === Three or More Groups ===
    elif n_groups >= 3:
        if design == Design.INDEPENDENT:
            if distribution == Distribution.NORMAL:
                if variance_equal:
                    post_hoc_name, post_hoc_key = POST_HOC_TESTS["one_way_anova"]
                    return TestRecommendation(
                        test_name="One-way ANOVA",
                        parametric=True,
                        assumptions=[
                            "normal distribution",
                            "homogeneity of variance",
                            "independent samples",
                        ],
                        python_code=TEST_PYTHON_CODE["one_way_anova"],
                        r_code=TEST_R_CODE["one_way_anova"],
                        post_hoc=post_hoc_name,
                        effect_size_metric="eta-squared (eta^2)",
                    )
                else:
                    post_hoc_name, post_hoc_key = POST_HOC_TESTS["welch_anova"]
                    return TestRecommendation(
                        test_name="Welch's ANOVA",
                        parametric=True,
                        assumptions=[
                            "normal distribution",
                            "independent samples",
                        ],
                        python_code=TEST_PYTHON_CODE["welch_anova"],
                        r_code=TEST_R_CODE["welch_anova"],
                        post_hoc=post_hoc_name,
                        effect_size_metric="omega-squared (omega^2)",
                        notes="Robust to unequal variances",
                    )
            else:
                post_hoc_name, post_hoc_key = POST_HOC_TESTS["kruskal_wallis"]
                return TestRecommendation(
                    test_name="Kruskal-Wallis",
                    parametric=False,
                    assumptions=[
                        "independent samples",
                        "ordinal or continuous outcome",
                    ],
                    python_code=TEST_PYTHON_CODE["kruskal_wallis"],
                    r_code=TEST_R_CODE["kruskal_wallis"],
                    post_hoc=post_hoc_name,
                    effect_size_metric="epsilon-squared",
                )

        elif design == Design.REPEATED_MEASURES:
            if distribution == Distribution.NORMAL:
                return TestRecommendation(
                    test_name="Repeated measures ANOVA",
                    parametric=True,
                    assumptions=[
                        "normal distribution",
                        "sphericity (test with Mauchly's test)",
                    ],
                    python_code=TEST_PYTHON_CODE["repeated_measures_anova"],
                    r_code=TEST_R_CODE["repeated_measures_anova"],
                    effect_size_metric="partial eta-squared",
                    notes="Apply Greenhouse-Geisser correction if sphericity violated",
                )
            else:
                post_hoc_name, _ = POST_HOC_TESTS["friedman"]
                return TestRecommendation(
                    test_name="Friedman test",
                    parametric=False,
                    assumptions=[
                        "ordinal or continuous outcome",
                        "repeated measures",
                    ],
                    python_code=TEST_PYTHON_CODE["friedman"],
                    r_code=TEST_R_CODE["friedman"],
                    post_hoc=post_hoc_name,
                    effect_size_metric="Kendall's W",
                )

    # === Single Group (one-sample tests) ===
    elif n_groups == 1:
        if distribution == Distribution.NORMAL:
            return TestRecommendation(
                test_name="One-sample t-test",
                parametric=True,
                assumptions=["normal distribution"],
                python_code="""from scipy import stats
t_stat, p_value = stats.ttest_1samp(data, popmean=hypothesized_mean)""",
                r_code="t.test(data, mu = hypothesized_mean)",
                effect_size_metric="Cohen's d",
            )
        else:
            return TestRecommendation(
                test_name="Wilcoxon signed-rank (one-sample)",
                parametric=False,
                assumptions=["symmetric distribution around median"],
                python_code="""from scipy import stats
stat, p_value = stats.wilcoxon(data - hypothesized_median)""",
                r_code="wilcox.test(data, mu = hypothesized_median)",
                effect_size_metric="matched-pairs rank-biserial correlation",
            )

    raise ValueError(
        f"No continuous test for: distribution={distribution}, "
        f"design={design}, n_groups={n_groups}"
    )


def _select_categorical_test(
    design: Design,
    n_groups: int,
    expected_counts_sufficient: bool,
) -> TestRecommendation:
    """Select test for categorical outcome."""

    if design == Design.INDEPENDENT:
        if n_groups == 2:
            if expected_counts_sufficient:
                return TestRecommendation(
                    test_name="Chi-square test",
                    parametric=False,
                    assumptions=[
                        "expected cell counts >= 5",
                        "independent observations",
                    ],
                    python_code=TEST_PYTHON_CODE["chi_square"],
                    r_code=TEST_R_CODE["chi_square"],
                    effect_size_metric="Cramer's V",
                )
            else:
                return TestRecommendation(
                    test_name="Fisher's exact test",
                    parametric=False,
                    assumptions=["independent observations"],
                    python_code=TEST_PYTHON_CODE["fisher_exact"],
                    r_code=TEST_R_CODE["fisher_exact"],
                    effect_size_metric="odds ratio",
                    notes="Use when expected cell counts < 5",
                )
        else:  # 3+ groups
            post_hoc_name, _ = POST_HOC_TESTS["chi_square"]
            return TestRecommendation(
                test_name="Chi-square test for independence",
                parametric=False,
                assumptions=[
                    "expected cell counts >= 5",
                    "independent observations",
                ],
                python_code=TEST_PYTHON_CODE["chi_square"],
                r_code=TEST_R_CODE["chi_square"],
                post_hoc=post_hoc_name,
                effect_size_metric="Cramer's V",
            )

    elif design == Design.PAIRED:
        return TestRecommendation(
            test_name="McNemar's test",
            parametric=False,
            assumptions=["paired binary outcomes", "2x2 contingency table"],
            python_code=TEST_PYTHON_CODE["mcnemar"],
            r_code=TEST_R_CODE["mcnemar"],
            effect_size_metric="odds ratio",
        )

    raise ValueError(f"No categorical test for: design={design}, n_groups={n_groups}")


def _select_ordinal_test(design: Design, n_groups: int) -> TestRecommendation:
    """Select test for ordinal outcome."""

    if design == Design.INDEPENDENT:
        if n_groups == 2:
            return TestRecommendation(
                test_name="Mann-Whitney U",
                parametric=False,
                assumptions=["independent samples", "ordinal outcome"],
                python_code=TEST_PYTHON_CODE["mann_whitney_u"],
                r_code=TEST_R_CODE["mann_whitney_u"],
                effect_size_metric="rank-biserial correlation",
            )
        else:
            post_hoc_name, _ = POST_HOC_TESTS["kruskal_wallis"]
            return TestRecommendation(
                test_name="Kruskal-Wallis",
                parametric=False,
                assumptions=["independent samples", "ordinal outcome"],
                python_code=TEST_PYTHON_CODE["kruskal_wallis"],
                r_code=TEST_R_CODE["kruskal_wallis"],
                post_hoc=post_hoc_name,
                effect_size_metric="epsilon-squared",
            )

    elif design == Design.PAIRED:
        if n_groups == 2:
            return TestRecommendation(
                test_name="Wilcoxon signed-rank",
                parametric=False,
                assumptions=["paired ordinal data"],
                python_code=TEST_PYTHON_CODE["wilcoxon_signed_rank"],
                r_code=TEST_R_CODE["wilcoxon_signed_rank"],
                effect_size_metric="matched-pairs rank-biserial correlation",
            )
        else:
            post_hoc_name, _ = POST_HOC_TESTS["friedman"]
            return TestRecommendation(
                test_name="Friedman test",
                parametric=False,
                assumptions=["repeated ordinal measures"],
                python_code=TEST_PYTHON_CODE["friedman"],
                r_code=TEST_R_CODE["friedman"],
                post_hoc=post_hoc_name,
                effect_size_metric="Kendall's W",
            )

    raise ValueError(f"No ordinal test for: design={design}, n_groups={n_groups}")


def _select_count_test(design: Design, n_groups: int) -> TestRecommendation:
    """Select test for count outcome."""

    # Count data typically uses Poisson or negative binomial models
    if design == Design.INDEPENDENT:
        if n_groups == 2:
            return TestRecommendation(
                test_name="Poisson rate test (or Mann-Whitney U)",
                parametric=False,
                assumptions=["independent samples", "count outcome"],
                python_code="""from scipy import stats
# For count data, consider Poisson regression or use non-parametric
u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')""",
                r_code="""# For count data, consider Poisson regression
glm(count ~ group, family = poisson, data = df)
# Or use non-parametric: wilcox.test(count ~ group, data = df)""",
                effect_size_metric="rate ratio",
                notes="Consider negative binomial if overdispersion present",
            )
        else:
            return TestRecommendation(
                test_name="Kruskal-Wallis (or Poisson regression)",
                parametric=False,
                assumptions=["independent samples", "count outcome"],
                python_code=TEST_PYTHON_CODE["kruskal_wallis"],
                r_code=TEST_R_CODE["kruskal_wallis"],
                effect_size_metric="epsilon-squared",
                notes="Consider Poisson/negative binomial regression for more power",
            )

    raise ValueError(f"No count test for: design={design}, n_groups={n_groups}")


def _select_survival_test(n_groups: int) -> TestRecommendation:
    """Select test for time-to-event outcome."""

    if n_groups >= 2:
        return TestRecommendation(
            test_name="Log-rank test (Kaplan-Meier comparison)",
            parametric=False,
            assumptions=[
                "censoring is non-informative",
                "proportional hazards (for Cox regression)",
            ],
            python_code=TEST_PYTHON_CODE["log_rank"],
            r_code=TEST_R_CODE["log_rank"],
            effect_size_metric="hazard ratio",
            notes="Use Cox regression for adjusted analysis with covariates",
        )

    raise ValueError(f"No survival test for n_groups={n_groups}")


def _select_proportion_test(design: Design, n_groups: int) -> TestRecommendation:
    """Select test for proportion outcome."""

    if design == Design.INDEPENDENT and n_groups == 2:
        return TestRecommendation(
            test_name="Z-test for two proportions",
            parametric=True,
            assumptions=["independent samples", "large sample approximation"],
            python_code=TEST_PYTHON_CODE["z_test_proportions"],
            r_code=TEST_R_CODE["z_test_proportions"],
            effect_size_metric="odds ratio or risk ratio",
        )

    raise ValueError(f"No proportion test for: design={design}, n_groups={n_groups}")


# =============================================================================
# Correlation Test Selection
# =============================================================================


def select_correlation_test(
    distribution: Distribution = Distribution.NORMAL,
    ordinal: bool = False,
    tied_ranks: bool = False,
) -> TestRecommendation:
    """
    Select appropriate correlation test based on data characteristics.

    Parameters
    ----------
    distribution : Distribution
        Distribution of the variables (normal, non_normal, unknown)
    ordinal : bool
        Whether one or both variables are ordinal
    tied_ranks : bool
        Whether there are many tied ranks (favors Kendall's tau)

    Returns
    -------
    TestRecommendation
        Complete recommendation with test name, code, and metadata
    """

    if ordinal or distribution in (Distribution.NON_NORMAL, Distribution.UNKNOWN):
        if tied_ranks:
            return TestRecommendation(
                test_name="Kendall's tau",
                parametric=False,
                assumptions=[
                    "monotonic relationship",
                    "ordinal or continuous variables",
                ],
                python_code=TEST_PYTHON_CODE["kendall_correlation"],
                r_code=TEST_R_CODE["kendall_correlation"],
                effect_size_metric="Kendall's tau",
                notes="More robust with tied ranks than Spearman",
            )
        else:
            return TestRecommendation(
                test_name="Spearman correlation",
                parametric=False,
                assumptions=[
                    "monotonic relationship",
                    "ordinal or continuous variables",
                ],
                python_code=TEST_PYTHON_CODE["spearman_correlation"],
                r_code=TEST_R_CODE["spearman_correlation"],
                effect_size_metric="Spearman's rho",
            )
    else:
        return TestRecommendation(
            test_name="Pearson correlation",
            parametric=True,
            assumptions=["linear relationship", "bivariate normality"],
            python_code=TEST_PYTHON_CODE["pearson_correlation"],
            r_code=TEST_R_CODE["pearson_correlation"],
            effect_size_metric="Pearson's r",
        )


# =============================================================================
# Utility Functions
# =============================================================================


def get_post_hoc_code(test_name: str, language: str = "python") -> Optional[str]:
    """
    Get the code for the appropriate post-hoc test.

    Parameters
    ----------
    test_name : str
        Name of the omnibus test (e.g., "one_way_anova", "kruskal_wallis")
    language : str
        Programming language ("python" or "r")

    Returns
    -------
    str or None
        Code for the post-hoc test, or None if not applicable
    """
    if test_name not in POST_HOC_TESTS:
        return None

    _, post_hoc_key = POST_HOC_TESTS[test_name]
    if post_hoc_key is None:
        return None

    if language.lower() == "python":
        return TEST_PYTHON_CODE.get(post_hoc_key)
    elif language.lower() == "r":
        return TEST_R_CODE.get(post_hoc_key)

    return None


def list_available_tests() -> list[str]:
    """Return a list of all available statistical tests."""
    return sorted(TEST_PYTHON_CODE.keys())


if __name__ == "__main__":
    # Example usage demonstrating deterministic output
    print("=== Test Selector Examples ===\n")

    # Example 1: Two-group continuous comparison
    result = select_test(
        outcome_type=OutcomeType.CONTINUOUS,
        distribution=Distribution.NON_NORMAL,
        design=Design.INDEPENDENT,
        n_groups=2,
    )
    print("Two groups, non-normal, independent:")
    print(f"  Recommended test: {result.test_name}")
    print(f"  Parametric: {result.parametric}")
    print(f"  Effect size: {result.effect_size_metric}")
    print()

    # Example 2: Multi-group comparison
    result = select_test(
        outcome_type=OutcomeType.CONTINUOUS,
        distribution=Distribution.NORMAL,
        design=Design.INDEPENDENT,
        n_groups=3,
        variance_equal=True,
    )
    print("Three groups, normal, equal variance:")
    print(f"  Recommended test: {result.test_name}")
    print(f"  Post-hoc: {result.post_hoc}")
    print()

    # Example 3: Correlation
    result = select_correlation_test(distribution=Distribution.NON_NORMAL)
    print("Correlation, non-normal:")
    print(f"  Recommended test: {result.test_name}")
