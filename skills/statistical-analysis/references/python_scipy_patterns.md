# Python Statistical Analysis Patterns

> Complete reference for scipy.stats and statsmodels usage in scientific computing

---

## Quick Import Reference

```python
# Core statistical libraries
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats import multitest

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
```

---

## Descriptive Statistics

### Basic Summary Statistics

```python
import numpy as np
from scipy import stats

data = np.array([...])

# Central tendency
mean = np.mean(data)
median = np.median(data)
mode = stats.mode(data, keepdims=True)

# Dispersion
std = np.std(data, ddof=1)      # Sample std (ddof=1)
var = np.var(data, ddof=1)      # Sample variance
sem = stats.sem(data)            # Standard error of mean
iqr = stats.iqr(data)            # Interquartile range

# Shape
skewness = stats.skew(data)
kurtosis = stats.kurtosis(data)  # Excess kurtosis (normal = 0)

# Percentiles
percentiles = np.percentile(data, [25, 50, 75])
```

### Confidence Intervals

```python
from scipy import stats
import numpy as np

def confidence_interval(data, confidence=0.95):
    """
    Calculate confidence interval for the mean.

    Parameters
    ----------
    data : array-like
        Sample data
    confidence : float
        Confidence level (default 0.95 for 95% CI)

    Returns
    -------
    tuple
        (mean, ci_low, ci_high)
    """
    n = len(data)
    mean = np.mean(data)
    sem = stats.sem(data)

    # t-distribution for small samples
    h = sem * stats.t.ppf((1 + confidence) / 2, n - 1)

    return mean, mean - h, mean + h

# Usage
mean, ci_low, ci_high = confidence_interval(data, 0.95)
print(f"Mean: {mean:.3f} (95% CI: {ci_low:.3f} - {ci_high:.3f})")
```

### Bootstrap Confidence Intervals

```python
from scipy import stats
import numpy as np

def bootstrap_ci(data, statistic=np.mean, n_bootstrap=10000,
                 confidence=0.95, random_state=None):
    """
    Bootstrap confidence interval for any statistic.

    Parameters
    ----------
    data : array-like
        Sample data
    statistic : callable
        Function to compute statistic (default: np.mean)
    n_bootstrap : int
        Number of bootstrap samples
    confidence : float
        Confidence level

    Returns
    -------
    tuple
        (estimate, ci_low, ci_high)
    """
    rng = np.random.default_rng(random_state)
    n = len(data)

    # Generate bootstrap samples
    bootstrap_stats = np.array([
        statistic(rng.choice(data, size=n, replace=True))
        for _ in range(n_bootstrap)
    ])

    # Percentile method
    alpha = 1 - confidence
    ci_low = np.percentile(bootstrap_stats, alpha/2 * 100)
    ci_high = np.percentile(bootstrap_stats, (1 - alpha/2) * 100)

    return statistic(data), ci_low, ci_high

# Usage
median_est, ci_low, ci_high = bootstrap_ci(data, np.median)
```

---

## Normality Testing

### Visual Assessment

```python
import matplotlib.pyplot as plt
from scipy import stats

def normality_plots(data, title=""):
    """Generate histogram and Q-Q plot for normality assessment."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Histogram with normal overlay
    axes[0].hist(data, bins='auto', density=True, alpha=0.7, edgecolor='black')
    xmin, xmax = axes[0].get_xlim()
    x = np.linspace(xmin, xmax, 100)
    axes[0].plot(x, stats.norm.pdf(x, np.mean(data), np.std(data)), 'r-', lw=2)
    axes[0].set_xlabel('Value')
    axes[0].set_ylabel('Density')
    axes[0].set_title(f'{title} - Histogram')

    # Q-Q plot
    stats.probplot(data, dist="norm", plot=axes[1])
    axes[1].set_title(f'{title} - Q-Q Plot')

    plt.tight_layout()
    return fig
```

### Statistical Tests

```python
from scipy import stats

def assess_normality(data, alpha=0.05):
    """
    Comprehensive normality assessment.

    Returns dict with test results and interpretation.
    """
    results = {}
    n = len(data)

    # Shapiro-Wilk (best for n < 50)
    if n <= 5000:
        stat, p = stats.shapiro(data)
        results['shapiro_wilk'] = {
            'statistic': stat, 'p_value': p,
            'normal': p > alpha,
            'note': 'Recommended for n < 50'
        }

    # D'Agostino-Pearson (requires n >= 20)
    if n >= 20:
        stat, p = stats.normaltest(data)
        results['dagostino_pearson'] = {
            'statistic': stat, 'p_value': p,
            'normal': p > alpha,
            'note': 'Based on skewness and kurtosis'
        }

    # Anderson-Darling
    result = stats.anderson(data, dist='norm')
    # Compare statistic to critical values at different significance levels
    significance_levels = [15, 10, 5, 2.5, 1]
    for i, (cv, sig) in enumerate(zip(result.critical_values, significance_levels)):
        if result.statistic < cv:
            results['anderson_darling'] = {
                'statistic': result.statistic,
                'critical_value': cv,
                'significance_level': sig,
                'normal': True,
                'note': f'Normal at {sig}% significance'
            }
            break
    else:
        results['anderson_darling'] = {
            'statistic': result.statistic,
            'normal': False,
            'note': 'Not normal at any standard significance level'
        }

    # Kolmogorov-Smirnov (against standard normal)
    data_standardized = (data - np.mean(data)) / np.std(data)
    stat, p = stats.kstest(data_standardized, 'norm')
    results['kolmogorov_smirnov'] = {
        'statistic': stat, 'p_value': p,
        'normal': p > alpha,
        'note': 'Less powerful than Shapiro-Wilk'
    }

    return results

# Usage
results = assess_normality(data)
for test, result in results.items():
    print(f"{test}: p={result.get('p_value', 'N/A'):.4f}, normal={result['normal']}")
```

---

## Two-Sample Comparisons

### Independent Samples

```python
from scipy import stats
import numpy as np

def compare_two_groups(group1, group2, alpha=0.05):
    """
    Comprehensive two-group comparison with automatic test selection.

    Returns dict with test selection rationale and results.
    """
    results = {'n1': len(group1), 'n2': len(group2)}

    # Check normality
    _, p1 = stats.shapiro(group1) if len(group1) <= 5000 else (None, 0.05)
    _, p2 = stats.shapiro(group2) if len(group2) <= 5000 else (None, 0.05)
    normal = (p1 > alpha) and (p2 > alpha)
    results['normality'] = {'group1_p': p1, 'group2_p': p2, 'both_normal': normal}

    if normal:
        # Check homogeneity of variance
        _, p_levene = stats.levene(group1, group2)
        equal_var = p_levene > alpha
        results['variance_test'] = {'levene_p': p_levene, 'equal_variance': equal_var}

        # Parametric test
        if equal_var:
            stat, p = stats.ttest_ind(group1, group2)
            test_name = "Independent t-test"
        else:
            stat, p = stats.ttest_ind(group1, group2, equal_var=False)
            test_name = "Welch's t-test"

        results['test'] = {
            'name': test_name,
            'statistic': stat,
            'p_value': p,
            'significant': p < alpha
        }

        # Effect size: Cohen's d
        pooled_std = np.sqrt(
            ((len(group1)-1)*np.var(group1, ddof=1) +
             (len(group2)-1)*np.var(group2, ddof=1)) /
            (len(group1) + len(group2) - 2)
        )
        cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_std
        results['effect_size'] = {
            'cohens_d': cohens_d,
            'interpretation': interpret_cohens_d(cohens_d)
        }

    else:
        # Non-parametric test
        stat, p = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        results['test'] = {
            'name': "Mann-Whitney U",
            'statistic': stat,
            'p_value': p,
            'significant': p < alpha
        }

        # Effect size: rank-biserial correlation
        n1, n2 = len(group1), len(group2)
        r = 1 - (2*stat) / (n1 * n2)
        results['effect_size'] = {
            'rank_biserial_r': r,
            'interpretation': interpret_rank_biserial(r)
        }

    return results


def interpret_cohens_d(d):
    """Cohen's d effect size interpretation."""
    d = abs(d)
    if d < 0.2:
        return "negligible"
    elif d < 0.5:
        return "small"
    elif d < 0.8:
        return "medium"
    else:
        return "large"


def interpret_rank_biserial(r):
    """Rank-biserial correlation interpretation."""
    r = abs(r)
    if r < 0.1:
        return "negligible"
    elif r < 0.3:
        return "small"
    elif r < 0.5:
        return "medium"
    else:
        return "large"


# Usage
results = compare_two_groups(treatment, control)
print(f"Test: {results['test']['name']}")
print(f"p-value: {results['test']['p_value']:.4f}")
print(f"Effect size: {results['effect_size']}")
```

### Paired Samples

```python
from scipy import stats

def compare_paired(before, after, alpha=0.05):
    """Paired sample comparison with automatic test selection."""
    if len(before) != len(after):
        raise ValueError("Paired samples must have equal length")

    differences = np.array(after) - np.array(before)
    results = {'n_pairs': len(before)}

    # Check normality of differences
    _, p_norm = stats.shapiro(differences) if len(differences) <= 5000 else (None, 0.05)
    normal = p_norm > alpha
    results['normality'] = {'differences_p': p_norm, 'normal': normal}

    if normal:
        # Paired t-test
        stat, p = stats.ttest_rel(before, after)
        results['test'] = {
            'name': "Paired t-test",
            'statistic': stat,
            'p_value': p,
            'significant': p < alpha
        }

        # Effect size: Cohen's d for paired samples
        d = np.mean(differences) / np.std(differences, ddof=1)
        results['effect_size'] = {'cohens_d': d, 'interpretation': interpret_cohens_d(d)}
    else:
        # Wilcoxon signed-rank test
        stat, p = stats.wilcoxon(before, after)
        results['test'] = {
            'name': "Wilcoxon signed-rank",
            'statistic': stat,
            'p_value': p,
            'significant': p < alpha
        }

        # Effect size: matched-pairs rank biserial
        n = len(differences)
        r = 1 - (2*stat) / (n * (n + 1) / 2)
        results['effect_size'] = {'rank_biserial_r': r}

    return results
```

---

## Multiple Group Comparisons

### ANOVA and Kruskal-Wallis

```python
from scipy import stats
import scikit_posthocs as sp  # pip install scikit-posthocs

def compare_multiple_groups(*groups, group_names=None, alpha=0.05):
    """
    Compare multiple groups with automatic test selection.

    Parameters
    ----------
    *groups : array-like
        Variable number of group arrays
    group_names : list, optional
        Names for each group
    alpha : float
        Significance level

    Returns
    -------
    dict
        Test results with post-hoc comparisons if significant
    """
    k = len(groups)
    if group_names is None:
        group_names = [f"Group {i+1}" for i in range(k)]

    results = {
        'n_groups': k,
        'group_sizes': {name: len(g) for name, g in zip(group_names, groups)}
    }

    # Check normality for each group
    normality_ps = []
    for g in groups:
        if len(g) >= 3:
            _, p = stats.shapiro(g) if len(g) <= 5000 else (None, 0.05)
            normality_ps.append(p)
    all_normal = all(p > alpha for p in normality_ps)

    # Check homogeneity of variance
    _, p_levene = stats.levene(*groups)
    equal_var = p_levene > alpha

    results['assumptions'] = {
        'normality_ps': normality_ps,
        'all_normal': all_normal,
        'levene_p': p_levene,
        'equal_variance': equal_var
    }

    if all_normal and equal_var:
        # One-way ANOVA
        stat, p = stats.f_oneway(*groups)
        results['test'] = {
            'name': "One-way ANOVA",
            'statistic': stat,
            'p_value': p,
            'significant': p < alpha
        }

        # Effect size: eta-squared
        # Combine all groups for calculation
        all_data = np.concatenate(groups)
        grand_mean = np.mean(all_data)
        ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
        ss_total = np.sum((all_data - grand_mean)**2)
        eta_squared = ss_between / ss_total
        results['effect_size'] = {
            'eta_squared': eta_squared,
            'interpretation': 'small' if eta_squared < 0.06 else
                            'medium' if eta_squared < 0.14 else 'large'
        }

        # Post-hoc: Tukey HSD
        if p < alpha:
            # Using statsmodels for Tukey HSD
            from statsmodels.stats.multicomp import pairwise_tukeyhsd

            all_data = np.concatenate(groups)
            group_labels = np.concatenate([
                [name] * len(g) for name, g in zip(group_names, groups)
            ])

            tukey = pairwise_tukeyhsd(all_data, group_labels, alpha=alpha)
            results['posthoc'] = {
                'method': 'Tukey HSD',
                'summary': str(tukey)
            }

    else:
        # Kruskal-Wallis
        stat, p = stats.kruskal(*groups)
        results['test'] = {
            'name': "Kruskal-Wallis H",
            'statistic': stat,
            'p_value': p,
            'significant': p < alpha
        }

        # Effect size: epsilon-squared
        n = sum(len(g) for g in groups)
        epsilon_squared = (stat - k + 1) / (n - k)
        results['effect_size'] = {'epsilon_squared': epsilon_squared}

        # Post-hoc: Dunn's test
        if p < alpha:
            # Create DataFrame for scikit-posthocs
            import pandas as pd
            all_data = np.concatenate(groups)
            group_labels = np.concatenate([
                [name] * len(g) for name, g in zip(group_names, groups)
            ])
            df = pd.DataFrame({'value': all_data, 'group': group_labels})

            dunn_results = sp.posthoc_dunn(df, val_col='value', group_col='group',
                                           p_adjust='bonferroni')
            results['posthoc'] = {
                'method': "Dunn's test (Bonferroni corrected)",
                'p_values': dunn_results.to_dict()
            }

    return results

# Usage
results = compare_multiple_groups(group_a, group_b, group_c,
                                  group_names=['Control', 'Low', 'High'])
```

---

## Correlation Analysis

```python
from scipy import stats
import numpy as np

def correlation_analysis(x, y, method='auto', alpha=0.05):
    """
    Correlation analysis with automatic method selection.

    Parameters
    ----------
    x, y : array-like
        Variables to correlate
    method : str
        'auto', 'pearson', 'spearman', or 'kendall'
    alpha : float
        Significance level

    Returns
    -------
    dict
        Correlation results with confidence intervals
    """
    x, y = np.array(x), np.array(y)
    n = len(x)

    results = {'n': n}

    if method == 'auto':
        # Check normality of both variables
        _, p_x = stats.shapiro(x) if n <= 5000 else (None, 0.05)
        _, p_y = stats.shapiro(y) if n <= 5000 else (None, 0.05)
        both_normal = (p_x > alpha) and (p_y > alpha)
        method = 'pearson' if both_normal else 'spearman'
        results['method_selection'] = {
            'x_normality_p': p_x,
            'y_normality_p': p_y,
            'selected': method
        }

    if method == 'pearson':
        r, p = stats.pearsonr(x, y)
        results['correlation'] = {
            'method': 'Pearson r',
            'r': r,
            'r_squared': r**2,
            'p_value': p,
            'significant': p < alpha
        }

        # Fisher z-transform for CI
        z = np.arctanh(r)
        se = 1 / np.sqrt(n - 3)
        z_crit = stats.norm.ppf(1 - alpha/2)
        z_low, z_high = z - z_crit * se, z + z_crit * se
        r_low, r_high = np.tanh(z_low), np.tanh(z_high)
        results['confidence_interval'] = {
            'level': 1 - alpha,
            'lower': r_low,
            'upper': r_high
        }

    elif method == 'spearman':
        r, p = stats.spearmanr(x, y)
        results['correlation'] = {
            'method': 'Spearman rho',
            'rho': r,
            'p_value': p,
            'significant': p < alpha
        }

    elif method == 'kendall':
        tau, p = stats.kendalltau(x, y)
        results['correlation'] = {
            'method': 'Kendall tau',
            'tau': tau,
            'p_value': p,
            'significant': p < alpha
        }

    # Interpretation
    r_abs = abs(r if method != 'kendall' else tau)
    if r_abs < 0.1:
        interp = "negligible"
    elif r_abs < 0.3:
        interp = "weak"
    elif r_abs < 0.5:
        interp = "moderate"
    elif r_abs < 0.7:
        interp = "strong"
    else:
        interp = "very strong"

    results['interpretation'] = interp

    return results
```

---

## Regression Analysis

### Linear Regression

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import pandas as pd

def linear_regression(df, formula=None, x_col=None, y_col=None):
    """
    Linear regression with comprehensive diagnostics.

    Use either formula (R-style) or x_col/y_col specification.

    Parameters
    ----------
    df : pd.DataFrame
        Data
    formula : str, optional
        R-style formula (e.g., 'y ~ x1 + x2')
    x_col : str or list, optional
        Predictor column(s)
    y_col : str, optional
        Response column

    Returns
    -------
    dict
        Regression results and diagnostics
    """
    if formula:
        model = smf.ols(formula, data=df).fit()
    else:
        X = df[x_col] if isinstance(x_col, list) else df[[x_col]]
        X = sm.add_constant(X)
        y = df[y_col]
        model = sm.OLS(y, X).fit()

    results = {
        'summary': model.summary(),
        'coefficients': {
            'values': model.params.to_dict(),
            'std_errors': model.bse.to_dict(),
            'p_values': model.pvalues.to_dict(),
            'conf_int': model.conf_int().to_dict()
        },
        'model_fit': {
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'f_statistic': model.fvalue,
            'f_pvalue': model.f_pvalue,
            'aic': model.aic,
            'bic': model.bic
        },
        'residuals': {
            'values': model.resid,
            'fitted': model.fittedvalues
        }
    }

    # Diagnostic tests
    from statsmodels.stats.diagnostic import het_breuschpagan
    from statsmodels.stats.stattools import durbin_watson

    # Heteroscedasticity (Breusch-Pagan)
    bp_stat, bp_p, _, _ = het_breuschpagan(model.resid, model.model.exog)
    results['diagnostics'] = {
        'breusch_pagan': {'statistic': bp_stat, 'p_value': bp_p,
                         'homoscedastic': bp_p > 0.05},
        'durbin_watson': durbin_watson(model.resid)  # ~2 = no autocorrelation
    }

    return results, model


def plot_regression_diagnostics(model):
    """Generate diagnostic plots for linear regression."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    # 1. Residuals vs Fitted
    axes[0, 0].scatter(model.fittedvalues, model.resid, alpha=0.5)
    axes[0, 0].axhline(y=0, color='r', linestyle='--')
    axes[0, 0].set_xlabel('Fitted values')
    axes[0, 0].set_ylabel('Residuals')
    axes[0, 0].set_title('Residuals vs Fitted')

    # 2. Q-Q plot
    from scipy import stats
    stats.probplot(model.resid, dist="norm", plot=axes[0, 1])
    axes[0, 1].set_title('Normal Q-Q')

    # 3. Scale-Location
    standardized_resid = model.resid / np.std(model.resid)
    axes[1, 0].scatter(model.fittedvalues, np.sqrt(np.abs(standardized_resid)), alpha=0.5)
    axes[1, 0].set_xlabel('Fitted values')
    axes[1, 0].set_ylabel('sqrt(|Standardized Residuals|)')
    axes[1, 0].set_title('Scale-Location')

    # 4. Residuals vs Leverage
    from statsmodels.stats.outliers_influence import OLSInfluence
    influence = OLSInfluence(model)
    leverage = influence.hat_matrix_diag
    axes[1, 1].scatter(leverage, standardized_resid, alpha=0.5)
    axes[1, 1].set_xlabel('Leverage')
    axes[1, 1].set_ylabel('Standardized Residuals')
    axes[1, 1].set_title('Residuals vs Leverage')

    plt.tight_layout()
    return fig
```

### Logistic Regression

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import pandas as pd

def logistic_regression(df, formula=None, x_cols=None, y_col=None):
    """
    Logistic regression for binary outcomes.

    Parameters
    ----------
    df : pd.DataFrame
        Data with binary outcome (0/1)
    formula : str, optional
        R-style formula (e.g., 'outcome ~ x1 + x2')
    x_cols : list, optional
        Predictor columns
    y_col : str, optional
        Binary outcome column

    Returns
    -------
    dict
        Results including odds ratios
    """
    if formula:
        model = smf.logit(formula, data=df).fit()
    else:
        X = df[x_cols]
        X = sm.add_constant(X)
        y = df[y_col]
        model = sm.Logit(y, X).fit()

    # Calculate odds ratios
    odds_ratios = np.exp(model.params)
    or_ci = np.exp(model.conf_int())

    results = {
        'summary': model.summary(),
        'coefficients': {
            'log_odds': model.params.to_dict(),
            'odds_ratios': odds_ratios.to_dict(),
            'or_ci_lower': or_ci[0].to_dict(),
            'or_ci_upper': or_ci[1].to_dict(),
            'p_values': model.pvalues.to_dict()
        },
        'model_fit': {
            'pseudo_r_squared': model.prsquared,
            'log_likelihood': model.llf,
            'aic': model.aic,
            'bic': model.bic
        }
    }

    return results, model


def classification_metrics(y_true, y_pred_proba, threshold=0.5):
    """Calculate classification metrics from predicted probabilities."""
    from sklearn.metrics import (
        confusion_matrix, accuracy_score, precision_score,
        recall_score, f1_score, roc_auc_score, roc_curve
    )

    y_pred = (y_pred_proba >= threshold).astype(int)

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    return {
        'confusion_matrix': cm,
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),  # Sensitivity
        'specificity': tn / (tn + fp),
        'f1_score': f1_score(y_true, y_pred),
        'auc_roc': roc_auc_score(y_true, y_pred_proba),
        'roc_curve': roc_curve(y_true, y_pred_proba)
    }
```

---

## Categorical Data Analysis

### Chi-Square and Fisher's Exact

```python
from scipy import stats
import numpy as np
import pandas as pd

def analyze_contingency(table, alpha=0.05):
    """
    Analyze contingency table with appropriate test selection.

    Parameters
    ----------
    table : array-like or pd.DataFrame
        Contingency table (2D array of counts)
    alpha : float
        Significance level

    Returns
    -------
    dict
        Test results and effect sizes
    """
    table = np.array(table)
    results = {'table': table, 'shape': table.shape}

    # Expected frequencies
    chi2, p, dof, expected = stats.chi2_contingency(table)

    # Check if Fisher's exact is needed (any expected < 5)
    use_fisher = np.any(expected < 5)

    results['expected'] = expected
    results['min_expected'] = expected.min()

    if use_fisher and table.shape == (2, 2):
        # Fisher's exact test (only for 2x2)
        odds_ratio, p = stats.fisher_exact(table)
        results['test'] = {
            'name': "Fisher's exact",
            'odds_ratio': odds_ratio,
            'p_value': p,
            'significant': p < alpha,
            'note': 'Used because expected frequencies < 5'
        }
    else:
        results['test'] = {
            'name': "Chi-square",
            'statistic': chi2,
            'dof': dof,
            'p_value': p,
            'significant': p < alpha
        }

        if use_fisher and table.shape != (2, 2):
            results['test']['warning'] = (
                "Expected frequencies < 5 detected. "
                "Consider collapsing categories or using simulation."
            )

    # Effect sizes
    n = table.sum()
    k = min(table.shape) - 1

    # Cramer's V
    cramers_v = np.sqrt(chi2 / (n * k))
    results['effect_size'] = {
        'cramers_v': cramers_v,
        'interpretation': 'small' if cramers_v < 0.1 else
                         'medium' if cramers_v < 0.3 else 'large'
    }

    # For 2x2: Odds ratio and relative risk
    if table.shape == (2, 2):
        a, b, c, d = table.ravel()

        # Odds ratio
        odds_ratio = (a * d) / (b * c) if (b * c) != 0 else np.inf
        or_se = np.sqrt(1/a + 1/b + 1/c + 1/d) if min(a,b,c,d) > 0 else np.nan
        or_ci = (
            odds_ratio * np.exp(-1.96 * or_se),
            odds_ratio * np.exp(1.96 * or_se)
        )

        # Relative risk
        rr = (a / (a + b)) / (c / (c + d)) if (c + d) > 0 else np.inf

        results['effect_size'].update({
            'odds_ratio': odds_ratio,
            'or_95ci': or_ci,
            'relative_risk': rr
        })

    return results

# Usage
table = [[30, 10], [15, 25]]  # 2x2 contingency table
results = analyze_contingency(table)
```

---

## Multiple Testing Correction

```python
from statsmodels.stats import multitest
import numpy as np

def correct_pvalues(pvalues, method='fdr_bh', alpha=0.05):
    """
    Apply multiple testing correction.

    Parameters
    ----------
    pvalues : array-like
        Raw p-values
    method : str
        Correction method:
        - 'bonferroni': Bonferroni (FWER)
        - 'sidak': Sidak (FWER)
        - 'holm': Holm-Bonferroni (FWER)
        - 'fdr_bh': Benjamini-Hochberg (FDR) - DEFAULT
        - 'fdr_by': Benjamini-Yekutieli (FDR, conservative)
    alpha : float
        Significance level

    Returns
    -------
    dict
        Corrected p-values and significant calls
    """
    pvalues = np.array(pvalues)

    # Apply correction
    reject, pvals_corrected, _, _ = multitest.multipletests(
        pvalues, alpha=alpha, method=method
    )

    return {
        'method': method,
        'alpha': alpha,
        'n_tests': len(pvalues),
        'pvalues_raw': pvalues,
        'pvalues_corrected': pvals_corrected,
        'reject': reject,
        'n_significant': reject.sum(),
        'proportion_significant': reject.mean()
    }


def compare_corrections(pvalues, alpha=0.05):
    """Compare different multiple testing correction methods."""
    methods = ['bonferroni', 'holm', 'fdr_bh', 'fdr_by']
    results = {}

    for method in methods:
        correction = correct_pvalues(pvalues, method=method, alpha=alpha)
        results[method] = {
            'n_significant': correction['n_significant'],
            'proportion': correction['proportion_significant']
        }

    return results
```

---

## Complete Analysis Template

```python
"""
Template for complete statistical analysis workflow.
"""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def full_analysis_report(df, group_col, value_col, alpha=0.05):
    """
    Generate complete statistical analysis report.

    Parameters
    ----------
    df : pd.DataFrame
        Data
    group_col : str
        Column with group labels
    value_col : str
        Column with numeric values
    alpha : float
        Significance level

    Returns
    -------
    dict
        Complete analysis results
    """
    groups = df.groupby(group_col)[value_col].apply(list).to_dict()
    group_names = list(groups.keys())
    group_data = list(groups.values())

    report = {
        'sample_info': {
            'total_n': len(df),
            'n_groups': len(groups),
            'group_sizes': {k: len(v) for k, v in groups.items()}
        }
    }

    # Descriptive statistics
    report['descriptives'] = df.groupby(group_col)[value_col].agg([
        'count', 'mean', 'std', 'median',
        lambda x: x.quantile(0.25),
        lambda x: x.quantile(0.75)
    ]).rename(columns={'<lambda_0>': 'Q1', '<lambda_1>': 'Q3'}).to_dict('index')

    # Normality tests
    report['normality'] = {}
    for name, data in groups.items():
        stat, p = stats.shapiro(data) if len(data) <= 5000 else (None, None)
        report['normality'][name] = {
            'shapiro_stat': stat,
            'p_value': p,
            'normal': p > alpha if p else None
        }

    # Main comparison
    all_normal = all(r['normal'] for r in report['normality'].values() if r['normal'] is not None)

    if len(groups) == 2:
        g1, g2 = group_data
        if all_normal:
            stat, p = stats.ttest_ind(g1, g2)
            test_name = "Independent t-test"
        else:
            stat, p = stats.mannwhitneyu(g1, g2, alternative='two-sided')
            test_name = "Mann-Whitney U"
    else:
        if all_normal:
            stat, p = stats.f_oneway(*group_data)
            test_name = "One-way ANOVA"
        else:
            stat, p = stats.kruskal(*group_data)
            test_name = "Kruskal-Wallis H"

    report['main_test'] = {
        'name': test_name,
        'statistic': stat,
        'p_value': p,
        'significant': p < alpha,
        'alpha': alpha
    }

    return report


# Usage example
if __name__ == "__main__":
    # Example data
    np.random.seed(42)
    df = pd.DataFrame({
        'group': ['Control'] * 30 + ['Treatment'] * 30,
        'value': np.concatenate([
            np.random.normal(10, 2, 30),
            np.random.normal(12, 2, 30)
        ])
    })

    report = full_analysis_report(df, 'group', 'value')

    print("=== Statistical Analysis Report ===")
    print(f"\nSample sizes: {report['sample_info']['group_sizes']}")
    print(f"\nMain test: {report['main_test']['name']}")
    print(f"p-value: {report['main_test']['p_value']:.4f}")
    print(f"Significant: {report['main_test']['significant']}")
```

---

## Reporting Templates

### Methods Section

```python
def generate_methods_text(results):
    """Generate methods section text from analysis results."""
    test = results['main_test']

    text = f"""
Statistical analysis was performed using Python {np.version.version}
with scipy {stats.version} and statsmodels.

{test['name']} was used to compare groups
{['after confirming normality assumptions (Shapiro-Wilk test, p > 0.05)'
  if 't-test' in test['name'] or 'ANOVA' in test['name']
  else 'due to violation of normality assumptions'][0]}.

Significance was set at α = {test['alpha']}.
"""
    return text.strip()


def generate_results_text(results):
    """Generate results section text from analysis results."""
    test = results['main_test']

    # Format p-value
    if test['p_value'] < 0.001:
        p_text = "p < 0.001"
    else:
        p_text = f"p = {test['p_value']:.3f}"

    text = f"""
The {test['name']} revealed
{'a significant' if test['significant'] else 'no significant'}
difference between groups ({test['name'].split()[0]} = {test['statistic']:.2f}, {p_text}).
"""
    return text.strip()
```
