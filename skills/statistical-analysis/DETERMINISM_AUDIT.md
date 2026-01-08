# Statistical Analysis Skill - Determinism Audit

> Audit Date: 2026-01-07
> Skill Version: 1.2.0
> Development Stage: First draft skill

---

## Executive Summary

The statistical-analysis skill is among the most determinism-ready skills due to its foundation in decision trees, lookup tables, and mathematical formulas. The primary opportunity is to formalize these structures into executable code—a Python-based "statistical decision engine" that takes structured inputs and outputs test selections, power calculations, and corrected p-values with zero LLM variance.

**Current determinism estimate:** ~60% (formulas and tables are deterministic, but LLM interprets inputs and traverses decision logic)

**Target determinism after implementation:** ~90% (LLM role reduces to translating natural language to structured input; all core logic becomes code)

**Key transformation:** Move from "LLM reads decision tree and applies it" to "Python code executes decision tree directly."

---

## Scratchpad Analysis

### 1. What the Skill Accomplishes

The statistical-analysis skill provides guidance for scientific data analysis, covering:
- Test selection via decision trees (data type → distribution → pairing → test)
- Code generation patterns for Python (scipy/statsmodels) and R
- Multiple testing correction methods (Bonferroni, BH-FDR, q-values)
- Effect size calculation and interpretation
- Power analysis and sample size estimation
- Result reporting templates for manuscripts

### 2. Key Inputs and Outputs

**Inputs (currently unstructured):**
- Research question type (comparison, association, prediction, distribution)
- Data characteristics (continuous/categorical, normal/non-normal, paired/independent)
- Number of groups being compared
- Sample sizes
- Desired power, alpha, effect size for power calculations
- Raw p-values for multiple testing correction

**Outputs:**
- Recommended statistical test
- Code snippets (Python/R)
- Interpretation guidance
- Manuscript-ready reporting text
- Sample size recommendations
- Corrected p-values

### 3. Components That Are Stochastic But Could Be Deterministic

**Already highly deterministic:**
- Decision trees for test selection are essentially lookup tables
- Effect size thresholds (Cohen's d < 0.2 = negligible, etc.)
- Sample size formulas are pure math
- Multiple testing correction algorithms are deterministic
- Code templates are fixed text
- Reporting templates are fixed text

**Currently stochastic (LLM-mediated):**
- Parsing user's free-text description to extract: data type, distribution, pairing, n groups
- Selecting which decision tree branch to follow based on natural language
- Adapting code templates with user-specific variable names
- Generating contextualized explanations

**COULD BE DETERMINISTIC with structured input:**
- Test selection: If user provides `{data_type: "continuous", normal: false, paired: true, groups: 2}`, output is 100% deterministic (Wilcoxon signed-rank)
- Power calculations: Given (effect_size, alpha, power, n), compute missing value—pure math
- Multiple testing correction: Given list of p-values and method, compute adjusted p-values—pure algorithm
- Effect size interpretation: Given d=0.6, output "medium effect"—lookup table

### 4. Red Flags for Reproducibility/Maintainability

**Reproducibility:**
- The skill itself is highly reproducible IF the LLM correctly interprets user input
- Main variability source: natural language interpretation of data characteristics
- The code patterns reference specific package versions—good for reproducibility

**Maintainability:**
- Skill is well-organized with clear sections
- References are modular (separate files for each topic)
- Workflow stages have explicit exit criteria—excellent
- Cross-references to other skills are explicit

**Missing:**
- No JSON schema for structured inputs
- No validation scripts to check if user's stated characteristics match their data
- No automated test selection algorithm—relies on LLM traversing decision tree

---

## Input Analysis

### Current State

Inputs are entirely free-form natural language. Users describe their data ("I have gene expression from 3 treatment groups") and the LLM must extract: data type, distribution assumption, design type, number of groups, sample sizes.

### Issues

- Same user scenario can be described many ways, leading to interpretation variance
- No validation that user's stated characteristics match their actual data
- Missing input → LLM guesses or asks, introducing inconsistency

### Recommendations

#### 1. Define JSON Input Schemas

```json
// Test selection query
{
  "query_type": "test_selection",
  "outcome_type": "continuous|categorical|ordinal|count|time_to_event",
  "distribution": "normal|non_normal|unknown",
  "design": "independent|paired|repeated_measures",
  "n_groups": 2,
  "variance_equal": true|false|null
}

// Power analysis query
{
  "query_type": "power_analysis",
  "test_type": "t_test|anova|correlation|survival",
  "effect_size": 0.5,
  "alpha": 0.05,
  "power": null,
  "n_per_group": 30
}

// Multiple testing correction query
{
  "query_type": "mtc_correction",
  "p_values": [0.001, 0.02, 0.04, 0.08],
  "method": "bh_fdr|bonferroni|holm"
}
```

#### 2. Add Input Validation Checklist

Before proceeding, confirm with the user:
- [ ] Data type: {continuous, categorical, ordinal, count}
- [ ] Distribution: {normal, non-normal, unknown}
- [ ] Design: {independent, paired, repeated}
- [ ] Number of groups: {2, 3+}

---

## Output Analysis

### Current State

Outputs are generally well-structured:
- Test recommendations reference specific test names
- Code snippets are templated
- Reporting templates exist with slot markers

### Issues

- Code outputs may vary in style/completeness across invocations
- Interpretation text is generated rather than templated
- No structured output format (just prose)

### Recommendations

#### 1. Standardize Output Format Per Query Type

```yaml
# Test selection output
test_name: "Mann-Whitney U"
parametric: false
assumptions: ["independent samples", "ordinal or continuous outcome"]
python_function: "scipy.stats.mannwhitneyu"
r_function: "wilcox.test"
post_hoc: null
```

#### 2. Template-Based Interpretation

```python
EFFECT_SIZE_TEMPLATES = {
    "cohens_d": {
        "negligible": "The effect size (d = {d:.2f}) is negligible, suggesting no practical difference.",
        "small": "The effect size (d = {d:.2f}) is small, indicating a subtle difference.",
        "medium": "The effect size (d = {d:.2f}) is medium, representing a moderate difference.",
        "large": "The effect size (d = {d:.2f}) is large, indicating a substantial difference."
    }
}
```

#### 3. Reporting Section as Fill-in-the-Blank

```markdown
Statistical analyses were performed using {software}.
{test_name} was used to compare {groups} because {justification}.
Results: {statistic}({df}) = {value}, p = {p_value}, {effect_metric} = {effect_value}.
```

---

## Deterministic Opportunities

| Component | Current | Proposed | Effort |
|-----------|---------|----------|--------|
| Test selection | LLM traverses decision tree | Python function with if/elif logic | Low |
| Power calculation | LLM generates code | Direct computation with scipy/statsmodels | Low |
| Multiple testing correction | LLM explains & generates code | Direct computation returning adjusted p-values | Low |
| Effect size interpretation | LLM generates prose | Lookup table with threshold ranges | Low |
| Sample size tables | LLM reads tables | Pre-computed lookup or formula execution | Low |
| Code generation | LLM adapts templates | String templating with parameter substitution | Medium |
| Reporting text | LLM generates | Template slot-filling | Medium |

### Phase 1: Deterministic Test Selector (`scripts/test_selector.py`)

```python
"""
Deterministic statistical test selection from data characteristics.
Encodes the decision trees from SKILL.md as executable Python code.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class OutcomeType(Enum):
    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"
    COUNT = "count"
    TIME_TO_EVENT = "time_to_event"

class Distribution(Enum):
    NORMAL = "normal"
    NON_NORMAL = "non_normal"
    UNKNOWN = "unknown"

class Design(Enum):
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

# Code templates for each test
TEST_PYTHON_CODE = {
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

    "one_way_anova": """from scipy import stats
f_stat, p_value = stats.f_oneway(group1, group2, group3)""",

    "kruskal_wallis": """from scipy import stats
h_stat, p_value = stats.kruskal(group1, group2, group3)""",

    "chi_square": """from scipy import stats
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)""",

    "fisher_exact": """from scipy import stats
odds_ratio, p_value = stats.fisher_exact(contingency_table)""",

    "pearson_correlation": """from scipy import stats
r, p_value = stats.pearsonr(x, y)""",

    "spearman_correlation": """from scipy import stats
rho, p_value = stats.spearmanr(x, y)""",
}

TEST_R_CODE = {
    "welch_t_test": "t.test(group1, group2)  # Welch's t-test (default)",
    "student_t_test": "t.test(group1, group2, var.equal = TRUE)",
    "mann_whitney_u": "wilcox.test(group1, group2, exact = FALSE)",
    "paired_t_test": "t.test(before, after, paired = TRUE)",
    "wilcoxon_signed_rank": "wilcox.test(before, after, paired = TRUE)",
    "one_way_anova": "summary(aov(value ~ group, data = df))",
    "kruskal_wallis": "kruskal.test(value ~ group, data = df)",
    "chi_square": "chisq.test(contingency_table)",
    "fisher_exact": "fisher.test(contingency_table)",
    "pearson_correlation": "cor.test(x, y, method = 'pearson')",
    "spearman_correlation": "cor.test(x, y, method = 'spearman')",
}

POST_HOC_TESTS = {
    "one_way_anova": "tukey_hsd",
    "kruskal_wallis": "dunn_test",
    "chi_square": "pairwise_chi_square_bonferroni",
}


def select_test(
    outcome_type: OutcomeType,
    distribution: Distribution,
    design: Design,
    n_groups: int,
    variance_equal: Optional[bool] = None,
    expected_counts_sufficient: bool = True
) -> TestRecommendation:
    """
    Deterministic test selection from data characteristics.

    This function encodes the decision trees from the statistical-analysis
    skill as executable Python code, eliminating LLM interpretation variance.

    Parameters
    ----------
    outcome_type : OutcomeType
        Type of outcome variable
    distribution : Distribution
        Distribution of the data (for continuous outcomes)
    design : Design
        Study design (independent, paired, repeated measures)
    n_groups : int
        Number of groups being compared
    variance_equal : bool, optional
        Whether variances are equal across groups (for parametric tests)
    expected_counts_sufficient : bool
        For categorical data, whether expected cell counts >= 5

    Returns
    -------
    TestRecommendation
        Complete recommendation with test name, code, and metadata
    """

    # === CONTINUOUS OUTCOME ===
    if outcome_type == OutcomeType.CONTINUOUS:

        # Two groups
        if n_groups == 2:
            if design == Design.INDEPENDENT:
                if distribution == Distribution.NORMAL:
                    if variance_equal:
                        test = "student_t_test"
                    else:
                        test = "welch_t_test"
                    return TestRecommendation(
                        test_name="Welch's t-test" if test == "welch_t_test" else "Student's t-test",
                        parametric=True,
                        assumptions=["normal distribution", "independent samples"],
                        python_code=TEST_PYTHON_CODE[test],
                        r_code=TEST_R_CODE[test],
                        effect_size_metric="Cohen's d"
                    )
                else:  # non-normal
                    return TestRecommendation(
                        test_name="Mann-Whitney U",
                        parametric=False,
                        assumptions=["independent samples", "ordinal or continuous outcome"],
                        python_code=TEST_PYTHON_CODE["mann_whitney_u"],
                        r_code=TEST_R_CODE["mann_whitney_u"],
                        effect_size_metric="rank-biserial correlation"
                    )

            elif design == Design.PAIRED:
                if distribution == Distribution.NORMAL:
                    return TestRecommendation(
                        test_name="Paired t-test",
                        parametric=True,
                        assumptions=["normal distribution of differences", "paired samples"],
                        python_code=TEST_PYTHON_CODE["paired_t_test"],
                        r_code=TEST_R_CODE["paired_t_test"],
                        effect_size_metric="Cohen's d (paired)"
                    )
                else:
                    return TestRecommendation(
                        test_name="Wilcoxon signed-rank",
                        parametric=False,
                        assumptions=["symmetric distribution of differences", "paired samples"],
                        python_code=TEST_PYTHON_CODE["wilcoxon_signed_rank"],
                        r_code=TEST_R_CODE["wilcoxon_signed_rank"],
                        effect_size_metric="matched-pairs rank-biserial"
                    )

        # Three or more groups
        elif n_groups >= 3:
            if design == Design.INDEPENDENT:
                if distribution == Distribution.NORMAL:
                    return TestRecommendation(
                        test_name="One-way ANOVA",
                        parametric=True,
                        assumptions=["normal distribution", "homogeneity of variance", "independent samples"],
                        python_code=TEST_PYTHON_CODE["one_way_anova"],
                        r_code=TEST_R_CODE["one_way_anova"],
                        post_hoc="Tukey HSD" if variance_equal else "Games-Howell",
                        effect_size_metric="eta-squared"
                    )
                else:
                    return TestRecommendation(
                        test_name="Kruskal-Wallis",
                        parametric=False,
                        assumptions=["independent samples", "ordinal or continuous outcome"],
                        python_code=TEST_PYTHON_CODE["kruskal_wallis"],
                        r_code=TEST_R_CODE["kruskal_wallis"],
                        post_hoc="Dunn's test with Bonferroni correction",
                        effect_size_metric="epsilon-squared"
                    )

            elif design == Design.REPEATED_MEASURES:
                if distribution == Distribution.NORMAL:
                    return TestRecommendation(
                        test_name="Repeated measures ANOVA",
                        parametric=True,
                        assumptions=["normal distribution", "sphericity"],
                        python_code="# Use statsmodels AnovaRM or pingouin",
                        r_code="library(ez); ezANOVA(data, dv, wid, within)",
                        effect_size_metric="partial eta-squared"
                    )
                else:
                    return TestRecommendation(
                        test_name="Friedman test",
                        parametric=False,
                        assumptions=["ordinal or continuous outcome", "repeated measures"],
                        python_code="from scipy import stats; stat, p = stats.friedmanchisquare(*groups)",
                        r_code="friedman.test(y ~ condition | subject, data = df)",
                        post_hoc="Nemenyi test",
                        effect_size_metric="Kendall's W"
                    )

    # === CATEGORICAL OUTCOME ===
    elif outcome_type == OutcomeType.CATEGORICAL:
        if n_groups == 2:
            if expected_counts_sufficient:
                return TestRecommendation(
                    test_name="Chi-square test",
                    parametric=False,
                    assumptions=["expected cell counts >= 5", "independent observations"],
                    python_code=TEST_PYTHON_CODE["chi_square"],
                    r_code=TEST_R_CODE["chi_square"],
                    effect_size_metric="Cramer's V"
                )
            else:
                return TestRecommendation(
                    test_name="Fisher's exact test",
                    parametric=False,
                    assumptions=["independent observations"],
                    python_code=TEST_PYTHON_CODE["fisher_exact"],
                    r_code=TEST_R_CODE["fisher_exact"],
                    effect_size_metric="odds ratio"
                )
        else:
            return TestRecommendation(
                test_name="Chi-square test for independence",
                parametric=False,
                assumptions=["expected cell counts >= 5", "independent observations"],
                python_code=TEST_PYTHON_CODE["chi_square"],
                r_code=TEST_R_CODE["chi_square"],
                post_hoc="Pairwise chi-square with Bonferroni correction",
                effect_size_metric="Cramer's V"
            )

    # === ORDINAL OUTCOME ===
    elif outcome_type == OutcomeType.ORDINAL:
        if n_groups == 2:
            return TestRecommendation(
                test_name="Mann-Whitney U",
                parametric=False,
                assumptions=["independent samples", "ordinal outcome"],
                python_code=TEST_PYTHON_CODE["mann_whitney_u"],
                r_code=TEST_R_CODE["mann_whitney_u"],
                effect_size_metric="rank-biserial correlation"
            )
        else:
            return TestRecommendation(
                test_name="Kruskal-Wallis",
                parametric=False,
                assumptions=["independent samples", "ordinal outcome"],
                python_code=TEST_PYTHON_CODE["kruskal_wallis"],
                r_code=TEST_R_CODE["kruskal_wallis"],
                post_hoc="Dunn's test",
                effect_size_metric="epsilon-squared"
            )

    # === TIME-TO-EVENT OUTCOME ===
    elif outcome_type == OutcomeType.TIME_TO_EVENT:
        return TestRecommendation(
            test_name="Log-rank test (Kaplan-Meier comparison)",
            parametric=False,
            assumptions=["censoring is non-informative", "proportional hazards (for Cox)"],
            python_code="from lifelines.statistics import logrank_test; result = logrank_test(T1, T2, E1, E2)",
            r_code="library(survival); survdiff(Surv(time, event) ~ group, data = df)",
            effect_size_metric="hazard ratio"
        )

    raise ValueError(f"No test recommendation for: {outcome_type}, {distribution}, {design}, n={n_groups}")


# === CORRELATION TEST SELECTION ===
def select_correlation_test(
    distribution: Distribution,
    ordinal: bool = False
) -> TestRecommendation:
    """Select appropriate correlation test."""

    if ordinal or distribution == Distribution.NON_NORMAL:
        return TestRecommendation(
            test_name="Spearman correlation",
            parametric=False,
            assumptions=["monotonic relationship", "ordinal or continuous variables"],
            python_code=TEST_PYTHON_CODE["spearman_correlation"],
            r_code=TEST_R_CODE["spearman_correlation"],
            effect_size_metric="Spearman's rho"
        )
    else:
        return TestRecommendation(
            test_name="Pearson correlation",
            parametric=True,
            assumptions=["linear relationship", "bivariate normality"],
            python_code=TEST_PYTHON_CODE["pearson_correlation"],
            r_code=TEST_R_CODE["pearson_correlation"],
            effect_size_metric="Pearson's r"
        )


if __name__ == "__main__":
    # Example usage demonstrating deterministic output
    result = select_test(
        outcome_type=OutcomeType.CONTINUOUS,
        distribution=Distribution.NON_NORMAL,
        design=Design.INDEPENDENT,
        n_groups=2
    )

    print(f"Recommended test: {result.test_name}")
    print(f"Parametric: {result.parametric}")
    print(f"Assumptions: {result.assumptions}")
    print(f"Python code:\n{result.python_code}")
```

### Phase 2: Multiple Testing Correction (`scripts/mtc_corrector.py`)

```python
"""
Deterministic multiple testing correction.
Wraps statsmodels functions with structured input/output.
"""

from typing import List, Literal, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class MTCResult:
    """Structured output for multiple testing correction."""
    method: str
    raw_pvalues: List[float]
    adjusted_pvalues: List[float]
    significant: List[bool]
    alpha: float
    n_significant: int
    expected_false_discoveries: float


def correct_pvalues(
    pvalues: List[float],
    method: Literal["bh_fdr", "bonferroni", "holm", "hochberg", "by_fdr"] = "bh_fdr",
    alpha: float = 0.05
) -> MTCResult:
    """
    Apply multiple testing correction to a list of p-values.

    Parameters
    ----------
    pvalues : list of float
        Raw p-values from statistical tests
    method : str
        Correction method:
        - "bh_fdr": Benjamini-Hochberg FDR (default, recommended for discovery)
        - "bonferroni": Bonferroni correction (conservative, for confirmation)
        - "holm": Holm step-down (less conservative than Bonferroni)
        - "hochberg": Hochberg step-up (requires independence)
        - "by_fdr": Benjamini-Yekutieli FDR (for arbitrary dependence)
    alpha : float
        Significance threshold (default 0.05)

    Returns
    -------
    MTCResult
        Complete results with adjusted p-values and significance calls
    """
    from statsmodels.stats.multitest import multipletests

    method_map = {
        "bh_fdr": "fdr_bh",
        "bonferroni": "bonferroni",
        "holm": "holm",
        "hochberg": "hochberg",
        "by_fdr": "fdr_by"
    }

    rejected, padj, _, _ = multipletests(
        pvalues,
        alpha=alpha,
        method=method_map[method]
    )

    n_sig = sum(rejected)

    # Expected false discoveries for FDR methods
    if method in ["bh_fdr", "by_fdr"]:
        expected_fd = n_sig * alpha
    else:
        expected_fd = alpha  # FWER methods control at alpha

    return MTCResult(
        method=method,
        raw_pvalues=list(pvalues),
        adjusted_pvalues=list(padj),
        significant=list(rejected),
        alpha=alpha,
        n_significant=n_sig,
        expected_false_discoveries=expected_fd
    )


if __name__ == "__main__":
    # Example usage
    pvals = [0.001, 0.01, 0.02, 0.04, 0.05, 0.10, 0.50]
    result = correct_pvalues(pvals, method="bh_fdr")

    print(f"Method: {result.method}")
    print(f"Significant at FDR < 0.05: {result.n_significant}")
    print(f"Expected false discoveries: {result.expected_false_discoveries:.1f}")
    for raw, adj, sig in zip(result.raw_pvalues, result.adjusted_pvalues, result.significant):
        marker = "*" if sig else ""
        print(f"  {raw:.4f} -> {adj:.4f} {marker}")
```

### Phase 3: Effect Size Interpreter (`scripts/effect_interpreter.py`)

```python
"""
Deterministic effect size interpretation using lookup tables.
"""

from typing import Literal, Tuple
from dataclasses import dataclass


@dataclass
class EffectInterpretation:
    """Structured interpretation of effect size."""
    metric: str
    value: float
    magnitude: str
    interpretation: str
    context: str


# Threshold tables (from Cohen, 1988 and field conventions)
EFFECT_THRESHOLDS = {
    "cohens_d": [
        (0.2, "negligible", "no practical difference"),
        (0.5, "small", "subtle but potentially meaningful difference"),
        (0.8, "medium", "moderate and noticeable difference"),
        (float("inf"), "large", "substantial and obvious difference")
    ],
    "pearsons_r": [
        (0.1, "negligible", "no meaningful relationship"),
        (0.3, "weak", "weak relationship"),
        (0.5, "moderate", "moderate relationship"),
        (0.7, "strong", "strong relationship"),
        (float("inf"), "very_strong", "very strong relationship")
    ],
    "eta_squared": [
        (0.01, "negligible", "negligible variance explained"),
        (0.06, "small", "small amount of variance explained"),
        (0.14, "medium", "medium amount of variance explained"),
        (float("inf"), "large", "large amount of variance explained")
    ],
    "odds_ratio": [
        (1.5, "negligible", "negligible association"),
        (2.5, "small", "small association"),
        (4.0, "medium", "medium association"),
        (float("inf"), "large", "strong association")
    ],
    "log2_fold_change": [
        (0.5, "negligible", "minimal change"),
        (1.0, "small", "subtle biological effect"),
        (2.0, "medium", "moderate biological effect"),
        (float("inf"), "large", "strong biological effect")
    ]
}


def interpret_effect_size(
    value: float,
    metric: Literal["cohens_d", "pearsons_r", "eta_squared", "odds_ratio", "log2_fold_change"]
) -> EffectInterpretation:
    """
    Deterministic interpretation of effect size.

    Parameters
    ----------
    value : float
        The effect size value
    metric : str
        Type of effect size metric

    Returns
    -------
    EffectInterpretation
        Complete interpretation with magnitude and context
    """

    abs_value = abs(value)
    thresholds = EFFECT_THRESHOLDS[metric]

    for threshold, magnitude, context in thresholds:
        if abs_value < threshold:
            break

    # Generate interpretation text
    templates = {
        "cohens_d": f"Cohen's d = {value:.2f} indicates a {magnitude} effect ({context}).",
        "pearsons_r": f"r = {value:.3f} indicates a {magnitude} correlation ({context}).",
        "eta_squared": f"η² = {value:.3f} indicates a {magnitude} effect ({context}).",
        "odds_ratio": f"OR = {value:.2f} indicates a {magnitude} effect ({context}).",
        "log2_fold_change": f"log₂FC = {value:.2f} indicates a {magnitude} effect ({context})."
    }

    return EffectInterpretation(
        metric=metric,
        value=value,
        magnitude=magnitude,
        interpretation=templates[metric],
        context=context
    )


if __name__ == "__main__":
    # Example usage
    result = interpret_effect_size(0.65, "cohens_d")
    print(result.interpretation)

    result = interpret_effect_size(0.42, "pearsons_r")
    print(result.interpretation)
```

### Phase 4: Power Calculator (`scripts/power_calculator.py`)

```python
"""
Deterministic power analysis wrapper.
Direct computation with no LLM involvement.
"""

from typing import Optional, Literal
from dataclasses import dataclass
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


def power_analysis(
    test_type: Literal["t_test", "anova", "correlation", "chi_square"],
    effect_size: Optional[float] = None,
    alpha: float = 0.05,
    power: Optional[float] = None,
    n_per_group: Optional[int] = None,
    n_groups: int = 2
) -> PowerResult:
    """
    Compute power analysis for common statistical tests.

    Provide any 3 of (effect_size, power, n_per_group) to calculate the 4th.

    Parameters
    ----------
    test_type : str
        Type of statistical test
    effect_size : float, optional
        Expected effect size (Cohen's d for t-test, f for ANOVA, r for correlation)
    alpha : float
        Significance level (default 0.05)
    power : float, optional
        Desired power (typically 0.8 or 0.9)
    n_per_group : int, optional
        Sample size per group
    n_groups : int
        Number of groups (for ANOVA)

    Returns
    -------
    PowerResult
        Complete results with all parameters
    """
    from statsmodels.stats.power import (
        TTestIndPower, FTestAnovaPower, NormalIndPower
    )

    if test_type == "t_test":
        analysis = TTestIndPower()

        if n_per_group is None:
            n = analysis.solve_power(
                effect_size=effect_size, alpha=alpha, power=power
            )
            n_per_group = int(np.ceil(n))
            calculated = "n_per_group"
        elif power is None:
            power = analysis.solve_power(
                effect_size=effect_size, nobs1=n_per_group, alpha=alpha
            )
            calculated = "power"
        elif effect_size is None:
            effect_size = analysis.solve_power(
                nobs1=n_per_group, alpha=alpha, power=power
            )
            calculated = "effect_size"

        return PowerResult(
            test_type=test_type,
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            n_per_group=n_per_group,
            n_total=n_per_group * 2,
            calculated_param=calculated
        )

    elif test_type == "anova":
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

        return PowerResult(
            test_type=test_type,
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            n_per_group=n_per_group,
            n_total=n_per_group * n_groups,
            calculated_param=calculated
        )

    # Add correlation and chi-square implementations similarly

    raise ValueError(f"Unsupported test type: {test_type}")


if __name__ == "__main__":
    # Example: What sample size for medium effect t-test?
    result = power_analysis(
        test_type="t_test",
        effect_size=0.5,
        power=0.8
    )
    print(f"Need {result.n_per_group} per group ({result.n_total} total)")
```

---

## Reproducibility Assessment

**Rating: Medium-High**

### Factors Supporting Reproducibility

- Decision frameworks are explicit and well-documented
- Mathematical formulas are deterministic
- Code templates are fixed
- Effect size thresholds are explicit numbers
- Multiple testing algorithms are deterministic

### Factors Limiting Reproducibility

- LLM interpretation of user's data description
- Variable phrasing of explanations
- Code adaptation to user-specific contexts

### Recommendations

1. Force structured input collection before proceeding with analysis
2. Implement deterministic test selector (eliminates LLM judgment)
3. Use templated outputs with parameter slots
4. Add checksums/validation for computed values

---

## Code Integration Recommendations

### 1. Preprocessing (before LLM)

- Input schema validation
- Extract structured parameters from conversation history
- Validate numeric inputs (n > 0, 0 < alpha < 1, etc.)

### 2. Core Computations (bypass LLM entirely)

```python
# scripts/statistical_engine.py

def run_power_analysis(test_type, **params):
    """Wrapper around statsmodels power functions."""
    # Pure computation, no LLM

def correct_pvalues(pvalues, method="bh_fdr"):
    """Apply multiple testing correction."""
    from statsmodels.stats.multitest import multipletests
    return multipletests(pvalues, method=method)

def interpret_effect_size(metric, value):
    """Deterministic interpretation from lookup table."""
    # Pure lookup, no LLM
```

### 3. Postprocessing (validation)

- Verify generated code is syntactically valid
- Check computed values against sanity bounds
- Validate that output format matches expected schema

### 4. Recommended File Structure

```
skills/statistical-analysis/
├── SKILL.md
├── DETERMINISM_AUDIT.md
├── scripts/
│   ├── test_selector.py       # Deterministic test selection
│   ├── power_calculator.py    # Power analysis computations
│   ├── mtc_corrector.py       # Multiple testing correction
│   ├── effect_interpreter.py  # Effect size interpretation
│   └── validators.py          # Input validation
├── schemas/
│   ├── test_selection.json    # Input schema
│   ├── power_analysis.json
│   └── mtc_correction.json
└── references/
    └── [existing files]
```

---

## Best Practices Evaluation

### Strengths

- Excellent use of decision trees with clear branching logic
- Workflow stages with explicit exit criteria (progressive disclosure)
- Common pitfalls section prevents errors
- Cross-references to related skills
- Code examples in both Python and R
- Clear scope definition (in/out of scope)

### Areas for Improvement

- No structured input requirements (relies on LLM extraction)
- Workflow exit criteria are not machine-checkable
- No validation of user-provided numerical inputs
- Code templates aren't parameterized for automated substitution

---

## Maintainability Score

**Rating: High**

### Justification

- Clear modular structure (main SKILL.md + reference files)
- Well-documented decision frameworks
- Explicit version numbering
- References to external quantification thresholds
- Logical organization by topic

### Improvements

- Add version tracking for reference files
- Include test cases for the decision logic
- Document which external packages are required

---

## Complexity Assessment

### Current Complexity: Appropriate

The skill handles genuinely complex subject matter (statistical test selection involves many conditional branches). The decision trees accurately capture this complexity rather than artificially simplifying it.

### Potential Simplification

- The 9 reference files could be consolidated if they share significant overlap
- Some code examples are redundant between SKILL.md and reference files

### Missing Beneficial Structure

- Input schemas (would reduce ambiguity)
- Output schemas (would ensure consistency)
- Executable decision logic (would eliminate interpretation variance)

---

## Prioritized Recommendations

### 1. Create Deterministic Test Selector Script (HIGH IMPACT, LOW EFFORT)

**Location:** `scripts/test_selector.py`

- Encode the decision trees as Python code
- Input: structured data characteristics
- Output: test name + code template + interpretation
- Eliminates LLM judgment from core task

### 2. Define JSON Input Schemas (HIGH IMPACT, LOW EFFORT)

**Location:** `schemas/`

- Three schemas: test_selection, power_analysis, mtc_correction
- Forces user to provide structured input
- Enables validation before processing

### 3. Implement Direct Computation Wrappers (HIGH IMPACT, LOW EFFORT)

**Location:** `scripts/power_calculator.py`, `scripts/mtc_corrector.py`

- Power calculations via statsmodels
- Multiple testing correction via statsmodels
- These are already deterministic algorithms—just expose them

### 4. Template-Based Code Generation (MEDIUM IMPACT, MEDIUM EFFORT)

- Parameterize code examples with placeholders
- Use Jinja2 or simple string formatting
- Ensures consistent code style across invocations

### 5. Add Validation Module (MEDIUM IMPACT, LOW EFFORT)

**Location:** `scripts/validators.py`

- Validate that n > 0, 0 < alpha < 1, 0 < power < 1
- Check that p-values are in [0, 1]
- Verify effect sizes are reasonable

---

## Stage-Specific Guidance

### Development Stage: First Draft Skill

For a first-draft skill, the structure is excellent. The decision frameworks are comprehensive and the reference documentation is thorough.

### Immediate (before moving to production)

1. Create `scripts/test_selector.py` with deterministic logic
2. Add basic input validation (numeric bounds, enum values)
3. Define at least one input schema (test_selection)

### Short-term Refinement

1. Test the decision logic against edge cases
2. Add example queries with expected outputs
3. Create the power calculation wrapper

### Before Production

1. Full input/output schema coverage
2. Validation scripts
3. Template-based code generation
4. Integration tests

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Determinism | ~60% | ~90% |
| Test selection variance | LLM-dependent | Zero (code-based) |
| Power calculation variance | LLM-dependent | Zero (direct computation) |
| MTC variance | LLM-dependent | Zero (direct computation) |
| Effect interpretation variance | LLM-dependent | Zero (lookup table) |

---

## Summary

The statistical-analysis skill is well-positioned to become highly deterministic because it's fundamentally built on decision trees and mathematical formulas. The main investment is encoding these structures as executable code rather than prose for the LLM to interpret.

**Top priority:** Create `scripts/test_selector.py` that takes structured input and returns the exact test, code, and interpretation—eliminating LLM variance from the core analytical task.
