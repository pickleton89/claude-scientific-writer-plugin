# Survival Analysis for Clinical and Biological Research

> Kaplan-Meier curves, log-rank test, Cox regression, and time-to-event analysis

---

## Overview

### When to Use Survival Analysis

Survival analysis is appropriate when studying **time-to-event** data:

| Application | Event | Censoring |
|-------------|-------|-----------|
| **Clinical trials** | Death, disease progression | Lost to follow-up, study ends |
| **Cancer biology** | Recurrence, metastasis | Death from other cause |
| **Cell biology** | Cell death, division | End of experiment |
| **Biomarker studies** | Expression-associated survival | Missing follow-up |

### Key Concepts

**Survival time (T)**: Time from origin (diagnosis, treatment start) to event

**Censoring**: Incomplete observation of survival time
- **Right censoring**: Event not observed by study end (most common)
- **Left censoring**: Event occurred before observation began
- **Interval censoring**: Event occurred within a time interval

**Survival function S(t)**: P(T > t) = Probability of surviving beyond time t

**Hazard function h(t)**: Instantaneous risk of event at time t, given survival to t

---

## Kaplan-Meier Estimation

### Theory

The Kaplan-Meier (KM) estimator is a non-parametric estimate of the survival function:

```
S(t) = ∏ (1 - dᵢ/nᵢ)
       tᵢ≤t

where:
- dᵢ = number of events at time tᵢ
- nᵢ = number at risk just before time tᵢ
```

### Python Implementation

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

def kaplan_meier_analysis(time, event, groups=None):
    """
    Perform Kaplan-Meier survival analysis.

    Parameters
    ----------
    time : array-like
        Survival/follow-up times
    event : array-like
        Event indicator (1 = event occurred, 0 = censored)
    groups : array-like, optional
        Group labels for comparison

    Returns
    -------
    dict
        KM fitters for each group, median survival, confidence intervals
    """
    results = {}

    if groups is None:
        # Single group
        kmf = KaplanMeierFitter()
        kmf.fit(time, event_observed=event)

        results['single'] = {
            'kmf': kmf,
            'median_survival': kmf.median_survival_time_,
            'survival_at_times': kmf.survival_function_
        }
    else:
        # Multiple groups
        unique_groups = np.unique(groups)

        for group in unique_groups:
            mask = groups == group
            kmf = KaplanMeierFitter()
            kmf.fit(time[mask], event_observed=event[mask], label=str(group))

            results[group] = {
                'kmf': kmf,
                'median_survival': kmf.median_survival_time_,
                'n_subjects': mask.sum(),
                'n_events': event[mask].sum()
            }

    return results


def plot_kaplan_meier(km_results, title="Kaplan-Meier Survival Curve",
                      xlabel="Time", ylabel="Survival Probability",
                      ci_show=True, at_risk_counts=True, figsize=(10, 6)):
    """
    Create publication-quality Kaplan-Meier plot.

    Parameters
    ----------
    km_results : dict
        Output from kaplan_meier_analysis()
    ci_show : bool
        Show confidence intervals
    at_risk_counts : bool
        Show number at risk below plot
    """
    fig, ax = plt.subplots(figsize=figsize)

    for group_name, result in km_results.items():
        kmf = result['kmf']
        kmf.plot_survival_function(ax=ax, ci_show=ci_show)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_ylim(0, 1)

    # Add at-risk table
    if at_risk_counts and len(km_results) <= 4:
        from lifelines.plotting import add_at_risk_counts
        add_at_risk_counts(*[r['kmf'] for r in km_results.values()], ax=ax)

    plt.tight_layout()
    return fig


def survival_comparison(time, event, groups, alpha=0.05):
    """
    Compare survival between groups using log-rank test.

    Parameters
    ----------
    time : array-like
        Survival times
    event : array-like
        Event indicators
    groups : array-like
        Group labels

    Returns
    -------
    dict
        Log-rank test results
    """
    unique_groups = np.unique(groups)

    if len(unique_groups) == 2:
        # Two-group comparison
        g1, g2 = unique_groups
        mask1 = groups == g1
        mask2 = groups == g2

        result = logrank_test(
            time[mask1], time[mask2],
            event_observed_A=event[mask1],
            event_observed_B=event[mask2]
        )

        return {
            'test': 'Log-rank test',
            'test_statistic': result.test_statistic,
            'p_value': result.p_value,
            'significant': result.p_value < alpha,
            'groups': (g1, g2)
        }
    else:
        # Multi-group comparison
        from lifelines.statistics import multivariate_logrank_test

        result = multivariate_logrank_test(time, groups, event)

        return {
            'test': 'Multivariate log-rank test',
            'test_statistic': result.test_statistic,
            'p_value': result.p_value,
            'significant': result.p_value < alpha,
            'n_groups': len(unique_groups)
        }


def median_survival_table(km_results):
    """Create table of median survival times with CI."""
    rows = []
    for group, result in km_results.items():
        kmf = result['kmf']
        ci = kmf.confidence_interval_survival_function_

        rows.append({
            'Group': group,
            'N': result['n_subjects'],
            'Events': result['n_events'],
            'Median Survival': kmf.median_survival_time_,
            '95% CI Lower': kmf.confidence_interval_median_survival_time_.iloc[0, 0]
                           if hasattr(kmf, 'confidence_interval_median_survival_time_') else np.nan,
            '95% CI Upper': kmf.confidence_interval_median_survival_time_.iloc[0, 1]
                           if hasattr(kmf, 'confidence_interval_median_survival_time_') else np.nan
        })

    return pd.DataFrame(rows)
```

### R Implementation

```r
library(survival)
library(survminer)

# Kaplan-Meier analysis
km_analysis <- function(data, time_col, event_col, group_col = NULL) {
  if (is.null(group_col)) {
    formula <- as.formula(paste("Surv(", time_col, ",", event_col, ") ~ 1"))
  } else {
    formula <- as.formula(paste("Surv(", time_col, ",", event_col, ") ~", group_col))
  }

  fit <- survfit(formula, data = data)

  list(
    fit = fit,
    summary = summary(fit),
    median = surv_median(fit)
  )
}

# Plot Kaplan-Meier curve
plot_km <- function(fit, data = NULL, title = "Kaplan-Meier Curve",
                    risk_table = TRUE, pval = TRUE, conf.int = TRUE) {
  ggsurvplot(
    fit,
    data = data,
    title = title,
    pval = pval,
    conf.int = conf.int,
    risk.table = risk_table,
    risk.table.col = "strata",
    ggtheme = theme_minimal(),
    palette = "jco",
    xlab = "Time",
    ylab = "Survival Probability"
  )
}

# Log-rank test
log_rank_test <- function(data, time_col, event_col, group_col) {
  formula <- as.formula(paste("Surv(", time_col, ",", event_col, ") ~", group_col))
  survdiff(formula, data = data)
}

# Example usage
# df <- data.frame(time = c(...), status = c(...), group = c(...))
# km <- km_analysis(df, "time", "status", "group")
# plot_km(km$fit, df)
# log_rank_test(df, "time", "status", "group")
```

---

## Cox Proportional Hazards Regression

### Theory

The Cox model relates hazard to covariates:

```
h(t|X) = h₀(t) × exp(β₁X₁ + β₂X₂ + ... + βₚXₚ)

where:
- h₀(t) = baseline hazard (unspecified)
- exp(βᵢ) = hazard ratio for one unit increase in Xᵢ
```

**Hazard Ratio (HR) interpretation**:
- HR = 1: No effect
- HR > 1: Increased risk (event happens sooner)
- HR < 1: Decreased risk (protective)

### Proportional Hazards Assumption

The ratio of hazards between groups is constant over time.

**Testing**:
- Schoenfeld residuals vs time
- Log-log plot: parallel curves if PH holds

### Python Implementation

```python
from lifelines import CoxPHFitter
from lifelines.utils import k_fold_cross_validation
import pandas as pd
import numpy as np

def cox_regression(df, duration_col, event_col, covariates=None,
                   strata=None, robust=False):
    """
    Fit Cox proportional hazards model.

    Parameters
    ----------
    df : pd.DataFrame
        Data with survival time, event, and covariates
    duration_col : str
        Column name for time
    event_col : str
        Column name for event indicator
    covariates : list, optional
        Columns to include (default: all except time/event)
    strata : list, optional
        Columns to stratify by (separate baseline hazards)
    robust : bool
        Use robust standard errors

    Returns
    -------
    dict
        Fitted model, summary, hazard ratios
    """
    cph = CoxPHFitter()

    # Prepare data
    if covariates is None:
        cols = [c for c in df.columns if c not in [duration_col, event_col]]
    else:
        cols = covariates

    model_df = df[[duration_col, event_col] + cols].copy()

    # Fit model
    cph.fit(model_df, duration_col=duration_col, event_col=event_col,
            strata=strata, robust=robust)

    # Extract results
    summary = cph.summary
    summary['HR'] = np.exp(summary['coef'])
    summary['HR_lower'] = np.exp(summary['coef'] - 1.96 * summary['se(coef)'])
    summary['HR_upper'] = np.exp(summary['coef'] + 1.96 * summary['se(coef)'])

    return {
        'model': cph,
        'summary': summary,
        'concordance': cph.concordance_index_,
        'log_likelihood': cph.log_likelihood_,
        'AIC': cph.AIC_
    }


def test_proportional_hazards(cox_result):
    """
    Test proportional hazards assumption using Schoenfeld residuals.

    Returns p-values for each covariate. Low p-value suggests violation.
    """
    cph = cox_result['model']
    ph_test = cph.check_assumptions(show_plots=False)
    return ph_test


def plot_hazard_ratios(cox_result, figsize=(8, 6)):
    """
    Forest plot of hazard ratios from Cox model.
    """
    summary = cox_result['summary']

    fig, ax = plt.subplots(figsize=figsize)

    y_pos = range(len(summary))
    ax.hlines(y_pos, summary['HR_lower'], summary['HR_upper'], color='black')
    ax.scatter(summary['HR'], y_pos, color='blue', s=50, zorder=3)
    ax.axvline(x=1, color='red', linestyle='--', label='HR = 1')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(summary.index)
    ax.set_xlabel('Hazard Ratio (95% CI)')
    ax.set_title('Cox Regression - Hazard Ratios')

    # Log scale if range is wide
    if summary['HR'].max() / summary['HR'].min() > 10:
        ax.set_xscale('log')

    plt.tight_layout()
    return fig


def stratified_km_by_risk(cox_result, df, duration_col, event_col,
                          n_groups=2, labels=None):
    """
    Create KM curves stratified by Cox model risk score.

    Common approach: divide by median risk score (low vs high risk).
    """
    cph = cox_result['model']

    # Calculate risk scores
    risk_scores = cph.predict_partial_hazard(df)
    df = df.copy()
    df['risk_score'] = risk_scores

    # Stratify
    if n_groups == 2:
        median_risk = risk_scores.median()
        df['risk_group'] = np.where(risk_scores > median_risk, 'High', 'Low')
    else:
        df['risk_group'] = pd.qcut(risk_scores, n_groups,
                                   labels=labels or range(n_groups))

    # Run KM analysis
    km_results = kaplan_meier_analysis(
        df[duration_col].values,
        df[event_col].values,
        df['risk_group'].values
    )

    # Log-rank test
    lr = survival_comparison(
        df[duration_col].values,
        df[event_col].values,
        df['risk_group'].values
    )

    return km_results, lr, df
```

### R Implementation

```r
library(survival)
library(survminer)

# Cox regression
cox_analysis <- function(data, time_col, event_col, covariates) {
  formula <- as.formula(paste(
    "Surv(", time_col, ",", event_col, ") ~",
    paste(covariates, collapse = " + ")
  ))

  fit <- coxph(formula, data = data)

  list(
    fit = fit,
    summary = summary(fit),
    hr = exp(coef(fit)),
    hr_ci = exp(confint(fit)),
    concordance = fit$concordance[1]
  )
}

# Test proportional hazards
test_ph <- function(cox_fit) {
  cox.zph(cox_fit$fit)
}

# Forest plot
plot_hr <- function(cox_fit) {
  ggforest(cox_fit$fit, data = NULL)
}

# Stratified KM by risk score
risk_stratified_km <- function(cox_fit, data, time_col, event_col,
                               n_groups = 2) {
  # Calculate risk scores
  data$risk_score <- predict(cox_fit$fit, type = "risk")

  # Stratify by median
  data$risk_group <- ifelse(
    data$risk_score > median(data$risk_score),
    "High", "Low"
  )

  # KM analysis
  formula <- as.formula(paste(
    "Surv(", time_col, ",", event_col, ") ~ risk_group"
  ))

  fit <- survfit(formula, data = data)

  # Plot
  ggsurvplot(
    fit,
    data = data,
    pval = TRUE,
    risk.table = TRUE,
    palette = c("blue", "red")
  )
}
```

### Handling PH Violations

When proportional hazards assumption is violated:

```python
# Option 1: Stratify by the violating variable
cph_stratified = CoxPHFitter()
cph_stratified.fit(df, duration_col='time', event_col='event',
                   strata=['violating_variable'])

# Option 2: Include time-varying coefficient
# Add interaction with time
df['covariate_x_time'] = df['covariate'] * df['time']
cph.fit(df, duration_col='time', event_col='event')

# Option 3: Fit separate models for different time periods
# (restricted analysis)
```

---

## Gene Expression Survival Analysis

### Biomarker Cutpoint Selection

```python
from lifelines.statistics import logrank_test
from lifelines import KaplanMeierFitter
import numpy as np

def find_optimal_cutpoint(expression, time, event, method='median'):
    """
    Find optimal cutpoint for continuous biomarker.

    Parameters
    ----------
    expression : array-like
        Gene expression values
    time : array-like
        Survival times
    event : array-like
        Event indicators
    method : str
        'median', 'mean', 'tertile', or 'optimal' (maximized log-rank)

    Returns
    -------
    dict
        Cutpoint, groups, and log-rank p-value
    """
    expression = np.array(expression)
    time = np.array(time)
    event = np.array(event)

    if method == 'median':
        cutpoint = np.median(expression)
    elif method == 'mean':
        cutpoint = np.mean(expression)
    elif method == 'tertile':
        # Return two cutpoints for high/medium/low
        cutpoints = np.percentile(expression, [33.3, 66.7])
        groups = np.select(
            [expression < cutpoints[0],
             expression >= cutpoints[1]],
            ['Low', 'High'],
            default='Medium'
        )
        # Multi-group comparison
        from lifelines.statistics import multivariate_logrank_test
        result = multivariate_logrank_test(time, groups, event)
        return {
            'cutpoints': cutpoints,
            'groups': groups,
            'p_value': result.p_value
        }
    elif method == 'optimal':
        # Grid search for cutpoint that maximizes log-rank statistic
        # Note: This overfits! Requires validation!
        percentiles = np.percentile(expression, np.arange(25, 76, 5))
        best_stat = -np.inf
        best_cutpoint = np.median(expression)

        for cut in percentiles:
            high = expression >= cut
            if high.sum() < 5 or (~high).sum() < 5:
                continue

            result = logrank_test(
                time[high], time[~high],
                event[high], event[~high]
            )

            if result.test_statistic > best_stat:
                best_stat = result.test_statistic
                best_cutpoint = cut

        cutpoint = best_cutpoint
        print("WARNING: Optimal cutpoint overfits. Validate in independent cohort!")

    # Create groups
    groups = np.where(expression >= cutpoint, 'High', 'Low')

    # Test
    high = expression >= cutpoint
    result = logrank_test(
        time[high], time[~high],
        event[high], event[~high]
    )

    return {
        'cutpoint': cutpoint,
        'groups': groups,
        'p_value': result.p_value,
        'n_high': high.sum(),
        'n_low': (~high).sum()
    }


def gene_survival_analysis(gene_name, expression_df, clinical_df,
                           time_col='OS', event_col='OS_status',
                           method='median'):
    """
    Complete survival analysis for a single gene.
    """
    # Get expression values
    expr = expression_df.loc[gene_name]

    # Align samples
    common_samples = expression_df.columns.intersection(clinical_df.index)
    expr = expr[common_samples]
    clinical = clinical_df.loc[common_samples]

    # Find cutpoint
    cut_result = find_optimal_cutpoint(
        expr.values,
        clinical[time_col].values,
        clinical[event_col].values,
        method=method
    )

    # KM analysis
    km_results = kaplan_meier_analysis(
        clinical[time_col].values,
        clinical[event_col].values,
        cut_result['groups']
    )

    return {
        'gene': gene_name,
        'cutpoint': cut_result['cutpoint'],
        'p_value': cut_result['p_value'],
        'km_results': km_results
    }


def screen_genes_survival(expression_df, clinical_df, time_col, event_col,
                          n_top=20, method='median'):
    """
    Screen all genes for survival association.

    WARNING: Multiple testing correction needed!
    """
    results = []

    for gene in expression_df.index:
        try:
            result = gene_survival_analysis(
                gene, expression_df, clinical_df,
                time_col, event_col, method
            )
            results.append({
                'gene': gene,
                'p_value': result['p_value'],
                'cutpoint': result['cutpoint']
            })
        except Exception as e:
            continue

    # Create DataFrame and sort
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('p_value')

    # Multiple testing correction
    from statsmodels.stats.multitest import multipletests
    _, results_df['p_adj'], _, _ = multipletests(
        results_df['p_value'], method='fdr_bh'
    )

    return results_df.head(n_top)
```

### R Implementation for Gene Survival

```r
library(survival)
library(survminer)

# Single gene survival analysis
gene_survival <- function(gene, expr_matrix, clinical, time_col, event_col,
                          method = "median") {
  # Get expression
  expr <- expr_matrix[gene, ]
  expr <- expr[rownames(clinical)]

  # Determine cutpoint
  if (method == "median") {
    cutpoint <- median(expr)
  } else if (method == "mean") {
    cutpoint <- mean(expr)
  } else if (method == "surv_cutpoint") {
    # Optimal cutpoint using survminer
    df <- data.frame(
      time = clinical[[time_col]],
      event = clinical[[event_col]],
      expression = as.numeric(expr)
    )
    cut <- surv_cutpoint(df, time = "time", event = "event",
                         variables = "expression")
    cutpoint <- cut$cutpoint$cutpoint
  }

  # Create groups
  group <- ifelse(expr >= cutpoint, "High", "Low")

  # Survival analysis
  df <- data.frame(
    time = clinical[[time_col]],
    event = clinical[[event_col]],
    group = group
  )

  fit <- survfit(Surv(time, event) ~ group, data = df)
  lr <- survdiff(Surv(time, event) ~ group, data = df)
  p_value <- 1 - pchisq(lr$chisq, df = 1)

  list(
    gene = gene,
    cutpoint = cutpoint,
    fit = fit,
    p_value = p_value,
    data = df
  )
}

# Plot gene survival
plot_gene_survival <- function(result) {
  ggsurvplot(
    result$fit,
    data = result$data,
    title = paste(result$gene, "Expression"),
    pval = TRUE,
    risk.table = TRUE,
    palette = c("blue", "red"),
    legend.labs = c("Low", "High")
  )
}
```

---

## Reporting in Manuscripts

### Methods Section

```markdown
**Survival Analysis**

Survival analysis was performed using the Kaplan-Meier method.
Median survival times were estimated with 95% confidence intervals.
Differences between groups were assessed using the log-rank test.

Cox proportional hazards regression was used for multivariable
analysis, adjusting for [covariates]. The proportional hazards
assumption was verified using Schoenfeld residuals (all p > 0.05).
Hazard ratios (HR) are reported with 95% confidence intervals.

For gene expression analysis, patients were dichotomized into
high and low expression groups based on the median expression value.
[If optimal cutpoint: The optimal cutpoint was determined using
X-tile software / maximized log-rank statistic and validated in
an independent cohort.]

Multiple testing correction was applied using the Benjamini-Hochberg
method for [N] genes tested. Statistical significance was defined
as adjusted p < 0.05.
```

### Results Reporting

```markdown
**Survival outcomes**

Median follow-up was [X] months (range: X-X). At the time of analysis,
[N] events (X%) had occurred.

[Gene] expression was significantly associated with overall survival
(HR = X.XX, 95% CI: X.XX-X.XX, p = X.XXX). Patients with high [gene]
expression showed [improved/reduced] survival compared to those with
low expression (median survival: X.X vs Y.Y months, log-rank p = X.XXX).

In multivariable analysis adjusting for [age, stage, etc.], [gene]
remained an independent prognostic factor (HR = X.XX, 95% CI: X.XX-X.XX,
p = X.XXX).
```

### Figure Legends

```markdown
**Figure X. Kaplan-Meier survival analysis of [gene] expression.**

(A) Patients were stratified into high (n=X) and low (n=Y) expression
groups based on [median / optimal cutpoint = X.XX]. Survival curves
show significant difference between groups (log-rank p = X.XXX).
Tick marks indicate censored observations.

(B) Forest plot of hazard ratios from multivariable Cox regression.
Horizontal bars represent 95% confidence intervals. Variables with
HR > 1 indicate increased risk; HR < 1 indicates protective effect.

(C) [Additional survival endpoint, e.g., progression-free survival]
```

---

## Common Pitfalls

| Mistake | Problem | Solution |
|---------|---------|----------|
| **Optimal cutpoint without validation** | Massive overfitting | Use median/tertiles, or validate in independent cohort |
| **Ignoring censoring** | Biased survival estimates | Always use proper survival methods |
| **Not testing PH assumption** | Invalid Cox results | Check Schoenfeld residuals |
| **Multiple testing without correction** | False discoveries | Apply FDR correction |
| **Landmark bias** | Including patients who died before landmark | Define landmark time, analyze from there |
| **Immortal time bias** | Patients assigned based on future events | Use time-varying covariates |

---

## References

1. Kaplan EL, Meier P (1958). Nonparametric estimation from incomplete observations. *JASA* 53:457-481.

2. Cox DR (1972). Regression models and life-tables. *J R Stat Soc B* 34:187-220.

3. Bradburn MJ, et al. (2003). Survival analysis part II: multivariate data analysis. *Br J Cancer* 89:431-436.

4. Therneau TM, Grambsch PM (2000). *Modeling Survival Data: Extending the Cox Model*. Springer.

5. Davidson-Pilon C (2019). *lifelines: survival analysis in Python*. JOSS 4:1317.
