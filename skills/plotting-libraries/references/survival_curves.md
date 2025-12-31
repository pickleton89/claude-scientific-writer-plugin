# Survival Curves and Time-to-Event Visualization

> Kaplan-Meier plots, log-rank tests, and Cox regression visualization
> Covers Python (lifelines, matplotlib) and R (survminer, survival) implementations

---

## Overview

Survival analysis visualizes time-to-event data, commonly used for:
- **Clinical studies**: Overall survival, progression-free survival
- **Genomics**: Gene expression stratified survival
- **Reliability**: Time to failure in systems

### Key Concepts

| Term | Definition |
|------|------------|
| Survival function S(t) | Probability of surviving beyond time t |
| Hazard rate h(t) | Instantaneous risk of event at time t |
| Censoring | Incomplete observation (patient lost to follow-up) |
| Median survival | Time when S(t) = 0.5 |

---

## Data Format

### Required Columns

```
| patient_id | time  | event | group     |
|------------|-------|-------|-----------|
| P001       | 24.5  | 1     | Treatment |
| P002       | 36.0  | 0     | Control   |  <- Censored (alive at end)
| P003       | 12.3  | 1     | Treatment |
```

- **time**: Duration of follow-up (months, days, years)
- **event**: 1 = event occurred, 0 = censored
- **group**: Stratification variable (optional)

---

## Python Implementation (lifelines)

### Installation

```bash
pip install lifelines
```

### Basic Kaplan-Meier Curve

```python
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
import pandas as pd

# Load data
df = pd.read_csv('survival_data.csv')

# Fit Kaplan-Meier
kmf = KaplanMeierFitter()
kmf.fit(df['time'], event_observed=df['event'], label='All Patients')

# Plot
fig, ax = plt.subplots(figsize=(10, 7))
kmf.plot_survival_function(ax=ax, ci_show=True)

ax.set_xlabel('Time (months)', fontsize=12)
ax.set_ylabel('Survival Probability', fontsize=12)
ax.set_title('Kaplan-Meier Survival Curve', fontsize=14)
ax.set_ylim(0, 1)

plt.tight_layout()
plt.savefig('km_curve.pdf', dpi=300, bbox_inches='tight')
```

### Stratified Kaplan-Meier (Multiple Groups)

```python
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib.pyplot as plt

def plot_stratified_km(df, time_col, event_col, group_col,
                       colors=None, figsize=(10, 7)):
    """
    Plot stratified Kaplan-Meier curves with log-rank test.

    Parameters
    ----------
    df : pd.DataFrame
        Survival data
    time_col : str
        Column name for time
    event_col : str
        Column name for event indicator
    group_col : str
        Column name for stratification
    """
    fig, ax = plt.subplots(figsize=figsize)

    groups = df[group_col].unique()
    if colors is None:
        colors = plt.cm.tab10.colors[:len(groups)]

    kmf = KaplanMeierFitter()

    for i, group in enumerate(groups):
        mask = df[group_col] == group
        kmf.fit(df.loc[mask, time_col],
                event_observed=df.loc[mask, event_col],
                label=group)
        kmf.plot_survival_function(ax=ax, ci_show=True, color=colors[i])

    # Log-rank test (for 2 groups)
    if len(groups) == 2:
        g1 = df[df[group_col] == groups[0]]
        g2 = df[df[group_col] == groups[1]]
        result = logrank_test(
            g1[time_col], g2[time_col],
            event_observed_A=g1[event_col],
            event_observed_B=g2[event_col]
        )
        p_value = result.p_value
        ax.text(0.7, 0.9, f'Log-rank p = {p_value:.4f}',
                transform=ax.transAxes, fontsize=11,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('Time (months)', fontsize=12)
    ax.set_ylabel('Survival Probability', fontsize=12)
    ax.set_ylim(0, 1)
    ax.legend(loc='lower left', fontsize=10)

    plt.tight_layout()
    return fig, ax

# Usage
fig, ax = plot_stratified_km(df, 'time', 'event', 'treatment_group')
plt.savefig('km_stratified.pdf', dpi=300, bbox_inches='tight')
```

### Adding Risk Table (Number at Risk)

```python
from lifelines import KaplanMeierFitter
from lifelines.plotting import add_at_risk_counts

fig, ax = plt.subplots(figsize=(10, 8))

kmf_treatment = KaplanMeierFitter()
kmf_control = KaplanMeierFitter()

# Fit models
kmf_treatment.fit(df[df['group'] == 'Treatment']['time'],
                  df[df['group'] == 'Treatment']['event'],
                  label='Treatment')
kmf_control.fit(df[df['group'] == 'Control']['time'],
                df[df['group'] == 'Control']['event'],
                label='Control')

# Plot
kmf_treatment.plot(ax=ax, color='blue')
kmf_control.plot(ax=ax, color='red')

# Add risk table
add_at_risk_counts(kmf_treatment, kmf_control, ax=ax)

ax.set_xlabel('Time (months)')
ax.set_ylabel('Survival Probability')
plt.tight_layout()
```

### Cox Proportional Hazards Visualization

```python
from lifelines import CoxPHFitter

# Fit Cox model
cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event')

# Print summary
cph.print_summary()

# Forest plot of hazard ratios
fig, ax = plt.subplots(figsize=(8, 6))
cph.plot(ax=ax)
ax.set_xlabel('Hazard Ratio (95% CI)')
ax.axvline(x=1, linestyle='--', color='gray')
plt.tight_layout()
plt.savefig('forest_plot.pdf', dpi=300, bbox_inches='tight')

# Survival curves for different covariate values
cph.plot_partial_effects_on_outcome(
    covariates='age',
    values=[40, 50, 60, 70],
    plot_baseline=False
)
```

### Gene Expression Stratified Survival

```python
def plot_gene_survival(df, gene_expression, time_col, event_col,
                       split_method='median', figsize=(10, 7)):
    """
    Stratify patients by gene expression and plot survival.

    Parameters
    ----------
    gene_expression : pd.Series
        Expression values for the gene
    split_method : str
        'median' or 'optimal' (maximizes log-rank statistic)
    """
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import logrank_test

    if split_method == 'median':
        threshold = gene_expression.median()
    else:
        # Find optimal cutpoint (simplified)
        threshold = gene_expression.median()  # Placeholder

    high_expr = gene_expression >= threshold
    low_expr = gene_expression < threshold

    fig, ax = plt.subplots(figsize=figsize)

    kmf = KaplanMeierFitter()

    # High expression
    kmf.fit(df.loc[high_expr, time_col],
            df.loc[high_expr, event_col],
            label=f'High (n={high_expr.sum()})')
    kmf.plot(ax=ax, color='red')

    # Low expression
    kmf.fit(df.loc[low_expr, time_col],
            df.loc[low_expr, event_col],
            label=f'Low (n={low_expr.sum()})')
    kmf.plot(ax=ax, color='blue')

    # Log-rank test
    result = logrank_test(
        df.loc[high_expr, time_col],
        df.loc[low_expr, time_col],
        event_observed_A=df.loc[high_expr, event_col],
        event_observed_B=df.loc[low_expr, event_col]
    )

    ax.text(0.7, 0.9, f'Log-rank p = {result.p_value:.4f}',
            transform=ax.transAxes, fontsize=11,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('Time (months)', fontsize=12)
    ax.set_ylabel('Survival Probability', fontsize=12)
    ax.set_title('Survival by Gene Expression', fontsize=14)
    ax.legend(loc='lower left')

    return fig, ax, result.p_value
```

---

## R Implementation (survminer)

### Installation

```r
install.packages("survminer")
install.packages("survival")
```

### Basic Kaplan-Meier Curve

```r
library(survival)
library(survminer)

# Create survival object
surv_obj <- Surv(time = df$time, event = df$event)

# Fit Kaplan-Meier
fit <- survfit(surv_obj ~ 1, data = df)

# Plot with survminer
ggsurvplot(fit,
           data = df,
           risk.table = TRUE,
           pval = FALSE,
           conf.int = TRUE,
           xlab = "Time (months)",
           ylab = "Survival Probability",
           title = "Kaplan-Meier Survival Curve")
```

### Stratified Kaplan-Meier (Recommended)

```r
library(survival)
library(survminer)

# Fit stratified model
fit <- survfit(Surv(time, event) ~ treatment, data = df)

# Publication-ready plot
ggsurvplot(fit,
           data = df,

           # Main plot
           pval = TRUE,                    # Log-rank p-value
           pval.method = TRUE,             # Show test method
           conf.int = TRUE,                # Confidence intervals
           conf.int.style = "ribbon",      # or "step"

           # Risk table
           risk.table = TRUE,
           risk.table.height = 0.25,
           risk.table.y.text = TRUE,
           risk.table.col = "strata",

           # Legend
           legend = "right",
           legend.title = "Group",
           legend.labs = c("Control", "Treatment"),

           # Colors
           palette = c("#377EB8", "#E41A1C"),

           # Lines
           linetype = "strata",            # Different line types
           size = 1,

           # Censor marks
           censor = TRUE,
           censor.shape = "|",
           censor.size = 3,

           # Labels
           xlab = "Time (months)",
           ylab = "Survival Probability",
           title = "Overall Survival by Treatment",

           # Theme
           ggtheme = theme_classic())
```

### Customizing the Plot

```r
# Store plot for modification
p <- ggsurvplot(fit, data = df, pval = TRUE, risk.table = TRUE)

# Access and modify components
p$plot <- p$plot +
  theme(
    legend.position = c(0.8, 0.8),
    legend.background = element_rect(fill = "white", color = "gray"),
    axis.title = element_text(face = "bold")
  ) +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, 0.2))

# Combine plot and table
print(p)

# Save
ggsave("survival_plot.pdf", plot = print(p), width = 8, height = 10)
```

### Adding Median Survival Lines

```r
ggsurvplot(fit,
           data = df,
           pval = TRUE,
           risk.table = TRUE,

           # Median survival
           surv.median.line = "hv",        # "h" = horizontal, "v" = vertical

           # Specific survival times
           break.time.by = 12,             # Time axis breaks

           # Annotations
           tables.height = 0.2,
           tables.theme = theme_cleantable())
```

### Gene Expression Survival (Optimal Cutpoint)

```r
library(survival)
library(survminer)
library(maxstat)  # For optimal cutpoint

# Find optimal cutpoint
optimal_cut <- surv_cutpoint(
  df,
  time = "time",
  event = "event",
  variables = "gene_expression"
)

# Categorize by cutpoint
df_cat <- surv_categorize(optimal_cut)

# Fit and plot
fit <- survfit(Surv(time, event) ~ gene_expression, data = df_cat)

ggsurvplot(fit,
           data = df_cat,
           pval = TRUE,
           pval.method = TRUE,
           risk.table = TRUE,
           palette = c("#0072B2", "#D55E00"),
           legend.labs = c("Low Expression", "High Expression"),
           xlab = "Time (months)",
           title = paste0("Survival by ", gene_name, " Expression"))
```

### Cox Proportional Hazards Forest Plot

```r
library(survival)
library(survminer)

# Fit Cox model
cox_fit <- coxph(Surv(time, event) ~ age + sex + stage + treatment, data = df)

# Summary
summary(cox_fit)

# Forest plot
ggforest(cox_fit,
         data = df,
         main = "Hazard Ratios",
         fontsize = 0.9,
         cpositions = c(0.02, 0.22, 0.4),
         refLabel = "Reference",
         noDigits = 2)
```

### Multiple Plots Arrangement

```r
library(survminer)
library(patchwork)

# Create multiple KM plots
fit_os <- survfit(Surv(os_time, os_event) ~ treatment, data = df)
fit_pfs <- survfit(Surv(pfs_time, pfs_event) ~ treatment, data = df)

p1 <- ggsurvplot(fit_os, data = df, title = "Overall Survival",
                 pval = TRUE, risk.table = FALSE)
p2 <- ggsurvplot(fit_pfs, data = df, title = "Progression-Free Survival",
                 pval = TRUE, risk.table = FALSE)

# Combine (note: survminer plots need special handling)
arrange_ggsurvplots(list(p1, p2), ncol = 2, nrow = 1)
```

---

## Statistical Considerations

### Log-Rank Test Assumptions

- Proportional hazards (curves shouldn't cross)
- Non-informative censoring
- Independent observations

### When Curves Cross

```r
# Use restricted mean survival time (RMST) instead
library(survRM2)
rmst2(df$time, df$event, df$group, tau = 60)  # Compare at 60 months

# Or use weighted log-rank tests
survdiff(Surv(time, event) ~ group, data = df, rho = 1)  # Peto-Peto
```

### Multiple Comparisons

```r
# Pairwise log-rank tests with correction
pairwise_survdiff(Surv(time, event) ~ stage, data = df,
                  p.adjust.method = "BH")  # Benjamini-Hochberg
```

---

## Reporting Guidelines

### Methods Section Template

```
Survival analysis was performed using the Kaplan-Meier method.
Differences between groups were assessed using the log-rank test.
Hazard ratios and 95% confidence intervals were estimated using
Cox proportional hazards regression. The proportional hazards
assumption was tested using Schoenfeld residuals. P-values < 0.05
were considered statistically significant. Analyses were performed
using R version X.X.X with the survival and survminer packages.
```

### Figure Legend Template

```
Figure X. Kaplan-Meier survival curves by [grouping variable].
(A) [Endpoint] for patients stratified by [variable]. Shaded areas
represent 95% confidence intervals. Tick marks indicate censored
observations. P-value from log-rank test. Numbers below the plot
show patients at risk at each time point.
```

---

## Publication Checklist

- [ ] Clearly stated time unit (days, months, years)
- [ ] Defined event (death, recurrence, etc.)
- [ ] Censoring explained in methods
- [ ] Log-rank p-value displayed on plot
- [ ] Confidence intervals shown
- [ ] Number at risk table included
- [ ] Median survival reported if reached
- [ ] Statistical test stated in legend
- [ ] Curves distinguishable (color + line type)
- [ ] Proportional hazards assumption checked (for Cox)

---

## Cross-References

- **[ggplot2.md](ggplot2.md)**: R plotting fundamentals
- **[matplotlib.md](matplotlib.md)**: Python plotting fundamentals
- **[../statistical-analysis/SKILL.md](../../statistical-analysis/SKILL.md)**: Survival analysis statistics
- **[../statistical-analysis/references/survival_analysis.md](../../statistical-analysis/references/survival_analysis.md)**: Statistical methods
