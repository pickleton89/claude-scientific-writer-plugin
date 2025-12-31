# Power Analysis and Sample Size Estimation

> Study design fundamentals for reliable and reproducible omics research

---

## Overview

### The Power Equation

Statistical power depends on four interrelated quantities:

```
Power = f(effect size, sample size, significance level, variance)
```

Given any three, you can solve for the fourth:

| Calculate | Given | Use Case |
|-----------|-------|----------|
| **Sample size (n)** | Power, α, effect size | Study planning |
| **Power (1-β)** | n, α, effect size | Evaluate existing design |
| **Effect size** | n, power, α | Minimum detectable effect |
| **Significance (α)** | n, power, effect size | Post-hoc adjustment |

### Key Definitions

**Type I error (α)**: False positive rate (reject H₀ when true)
- Convention: α = 0.05

**Type II error (β)**: False negative rate (fail to reject H₀ when false)
- Power = 1 - β

**Power (1-β)**: Probability of detecting a true effect
- Convention: 80% minimum, 90% preferred

**Effect size**: Standardized measure of the magnitude of effect
- Cohen's d, Hedge's g, correlation r, odds ratio

---

## Effect Size Reference

### Cohen's d (Standardized Mean Difference)

```
d = (μ₁ - μ₂) / σ_pooled
```

| d | Interpretation | Example |
|---|----------------|---------|
| 0.2 | Small | Subtle difference |
| 0.5 | Medium | Noticeable difference |
| 0.8 | Large | Obvious difference |
| 1.0+ | Very large | Dramatic difference |

### For Gene Expression

In RNA-seq, effect size often expressed as **log2 fold change**:

| log2 FC | Linear FC | Interpretation |
|---------|-----------|----------------|
| 0.5 | 1.41× | Small |
| 1.0 | 2× | Medium |
| 2.0 | 4× | Large |
| 3.0 | 8× | Very large |

**Converting to Cohen's d** (approximation):

```python
# For RNA-seq, depends on biological coefficient of variation (BCV)
# BCV typically 0.2-0.4 for well-controlled experiments
def log2fc_to_cohens_d(log2fc, bcv=0.4):
    """Approximate Cohen's d from log2 fold change."""
    return log2fc / (bcv * np.sqrt(2))

# Example: log2FC = 1.0, BCV = 0.4
# d ≈ 1.0 / (0.4 × 1.41) ≈ 1.77 (large effect)
```

---

## Two-Group Comparison Power

### Python Implementation

```python
from scipy import stats
import numpy as np
from statsmodels.stats.power import TTestIndPower, TTestPower

def power_two_group(effect_size=None, n=None, alpha=0.05, power=None,
                    ratio=1, alternative='two-sided'):
    """
    Power analysis for two-group comparison (t-test).

    Provide 3 of 4 parameters to calculate the missing one.

    Parameters
    ----------
    effect_size : float
        Cohen's d
    n : int
        Sample size per group (group 1)
    alpha : float
        Significance level
    power : float
        Statistical power (1 - beta)
    ratio : float
        Ratio of group sizes (n2/n1)
    alternative : str
        'two-sided', 'larger', or 'smaller'

    Returns
    -------
    dict
        Calculated parameter and analysis details
    """
    analysis = TTestIndPower()

    # Determine what to calculate
    if n is None:
        n = analysis.solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            ratio=ratio,
            alternative=alternative
        )
        result = {'n_per_group': int(np.ceil(n)),
                  'n_total': int(np.ceil(n * (1 + ratio)))}

    elif power is None:
        power = analysis.solve_power(
            effect_size=effect_size,
            nobs1=n,
            alpha=alpha,
            ratio=ratio,
            alternative=alternative
        )
        result = {'power': power}

    elif effect_size is None:
        effect_size = analysis.solve_power(
            nobs1=n,
            alpha=alpha,
            power=power,
            ratio=ratio,
            alternative=alternative
        )
        result = {'minimum_detectable_effect': effect_size}

    result.update({
        'effect_size': effect_size,
        'n': n,
        'alpha': alpha,
        'power': power,
        'ratio': ratio
    })

    return result


def power_curve(effect_sizes=[0.2, 0.5, 0.8], n_range=range(5, 101, 5),
                alpha=0.05):
    """
    Generate power curves for different effect sizes.
    """
    import matplotlib.pyplot as plt

    analysis = TTestIndPower()
    fig, ax = plt.subplots(figsize=(10, 6))

    for es in effect_sizes:
        powers = [analysis.solve_power(effect_size=es, nobs1=n, alpha=alpha)
                  for n in n_range]
        ax.plot(list(n_range), powers, label=f"d = {es}")

    ax.axhline(y=0.8, color='red', linestyle='--', label='80% power')
    ax.axhline(y=0.9, color='orange', linestyle='--', label='90% power')

    ax.set_xlabel('Sample size per group')
    ax.set_ylabel('Power')
    ax.set_title('Power Curves for Two-Group Comparison')
    ax.legend()
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    return fig


def sample_size_table(effect_sizes=[0.2, 0.5, 0.8, 1.0],
                      power_levels=[0.80, 0.90, 0.95], alpha=0.05):
    """
    Generate sample size table for common scenarios.
    """
    import pandas as pd

    analysis = TTestIndPower()
    results = []

    for es in effect_sizes:
        row = {'Effect Size (d)': es}
        for power in power_levels:
            n = analysis.solve_power(effect_size=es, alpha=alpha, power=power)
            row[f'n (power={power})'] = int(np.ceil(n))
        results.append(row)

    return pd.DataFrame(results)
```

### R Implementation

```r
library(pwr)

# Two-sample t-test power
power_two_group <- function(d = NULL, n = NULL, sig.level = 0.05,
                            power = NULL, type = "two.sample",
                            alternative = "two.sided") {
  pwr.t.test(
    d = d,
    n = n,
    sig.level = sig.level,
    power = power,
    type = type,
    alternative = alternative
  )
}

# Sample size for given effect and power
sample_size <- function(d, power = 0.8, sig.level = 0.05) {
  result <- pwr.t.test(d = d, power = power, sig.level = sig.level,
                       type = "two.sample")
  ceiling(result$n)
}

# Power curve
power_curve <- function(effect_sizes = c(0.2, 0.5, 0.8),
                        n_range = seq(5, 100, 5),
                        sig.level = 0.05) {
  library(ggplot2)

  results <- data.frame()
  for (d in effect_sizes) {
    for (n in n_range) {
      power <- pwr.t.test(d = d, n = n, sig.level = sig.level)$power
      results <- rbind(results, data.frame(n = n, d = d, power = power))
    }
  }

  results$d <- factor(results$d)

  ggplot(results, aes(x = n, y = power, color = d)) +
    geom_line(size = 1) +
    geom_hline(yintercept = 0.8, linetype = "dashed", color = "red") +
    labs(x = "Sample size per group", y = "Power",
         title = "Power Curves for Two-Group Comparison") +
    theme_minimal()
}
```

---

## RNA-seq Power Analysis

### Key Considerations for RNA-seq

1. **Number of biological replicates** (not technical replicates)
2. **Sequencing depth** (reads per sample)
3. **Biological coefficient of variation (BCV)**
4. **Target effect size (fold change)**
5. **Multiple testing burden**

### RNASeqPower Package

```r
# R - RNASeqPower
library(RNASeqPower)

# Estimate required sample size
rnapower <- function(depth = 10, cv = 0.4, effect = 2,
                     alpha = 0.05, power = 0.8) {
  # depth: mean read count per gene (coverage)
  # cv: coefficient of variation (biological variability)
  # effect: fold change to detect

  rnapower(
    depth = depth,
    cv = cv,
    effect = effect,
    alpha = alpha,
    power = power
  )
}

# Example: How many samples for 2-fold change detection?
# Assuming depth=10, cv=0.4, alpha=0.05, power=0.8
rnapower(depth = 10, cv = 0.4, effect = 2, alpha = 0.05, power = 0.8)
```

### Quick Reference: RNA-seq Sample Sizes

Based on typical parameters (BCV ~0.4, depth ~10M reads, α = 0.05):

| log2 FC | Fold Change | n/group (80% power) | n/group (90% power) |
|---------|-------------|---------------------|---------------------|
| 0.5 | 1.4× | 20-30 | 30-40 |
| 1.0 | 2× | 6-10 | 10-15 |
| 1.5 | 2.8× | 4-6 | 6-8 |
| 2.0 | 4× | 3-4 | 4-5 |

**Note**: These are per gene. For genome-wide studies with FDR correction, increase by ~20-50%.

### Python Approximation for RNA-seq

```python
import numpy as np
from scipy import stats

def rnaseq_power(n_per_group, fold_change, bcv=0.4, depth=10,
                 alpha=0.05, fdr_genes=1):
    """
    Approximate power for RNA-seq differential expression.

    Parameters
    ----------
    n_per_group : int
        Biological replicates per condition
    fold_change : float
        Fold change to detect (linear scale)
    bcv : float
        Biological coefficient of variation (0.1-0.4 typical)
    depth : float
        Approximate mean counts per gene
    alpha : float
        Significance level
    fdr_genes : int
        Number of genes for FDR adjustment (use 1 for per-gene power)

    Returns
    -------
    float
        Estimated power
    """
    # Effect size in log space
    log_fc = np.log(fold_change)

    # Variance components
    # Total variance ≈ 1/depth + bcv^2
    total_var = 1/depth + bcv**2

    # Standard error of log fold change
    se = np.sqrt(2 * total_var / n_per_group)

    # Effect size (similar to Cohen's d)
    effect_size = log_fc / se

    # Degrees of freedom (approximation)
    df = 2 * (n_per_group - 1)

    # Critical value with multiple testing adjustment
    alpha_adj = alpha / fdr_genes if fdr_genes > 1 else alpha
    t_crit = stats.t.ppf(1 - alpha_adj/2, df)

    # Non-central t distribution for power
    ncp = effect_size  # Non-centrality parameter
    power = 1 - stats.nct.cdf(t_crit, df, ncp) + stats.nct.cdf(-t_crit, df, ncp)

    return power


def rnaseq_sample_size(fold_change, power=0.8, bcv=0.4, depth=10,
                       alpha=0.05, fdr_genes=1):
    """
    Find required sample size for RNA-seq.
    """
    for n in range(2, 101):
        p = rnaseq_power(n, fold_change, bcv, depth, alpha, fdr_genes)
        if p >= power:
            return n
    return ">100"


# Example usage
print("Sample sizes for 80% power to detect 2-fold change:")
print(f"  BCV=0.2: n = {rnaseq_sample_size(2, bcv=0.2)}")
print(f"  BCV=0.4: n = {rnaseq_sample_size(2, bcv=0.4)}")
print(f"  BCV=0.6: n = {rnaseq_sample_size(2, bcv=0.6)}")
```

---

## ANOVA and Multi-Group Comparisons

### Python

```python
from statsmodels.stats.power import FTestAnovaPower

def power_anova(k, n=None, effect_size=None, alpha=0.05, power=None):
    """
    Power analysis for one-way ANOVA.

    Parameters
    ----------
    k : int
        Number of groups
    n : int
        Sample size per group
    effect_size : float
        Cohen's f (small=0.1, medium=0.25, large=0.4)
    alpha : float
        Significance level
    power : float
        Statistical power

    Notes
    -----
    Cohen's f conversion:
    - f = 0.10: small effect
    - f = 0.25: medium effect
    - f = 0.40: large effect

    f = sqrt(eta² / (1 - eta²))
    """
    analysis = FTestAnovaPower()

    if n is None:
        n = analysis.solve_power(
            effect_size=effect_size,
            k_groups=k,
            alpha=alpha,
            power=power
        )
        return int(np.ceil(n))
    elif power is None:
        return analysis.solve_power(
            effect_size=effect_size,
            k_groups=k,
            nobs=n,
            alpha=alpha
        )
    elif effect_size is None:
        return analysis.solve_power(
            k_groups=k,
            nobs=n,
            alpha=alpha,
            power=power
        )


# Example
n = power_anova(k=3, effect_size=0.25, power=0.8)
print(f"Need {n} samples per group for 3-group ANOVA with medium effect")
```

### R

```r
library(pwr)

# One-way ANOVA
power_anova <- function(k, n = NULL, f = NULL, sig.level = 0.05, power = NULL) {
  pwr.anova.test(
    k = k,
    n = n,
    f = f,
    sig.level = sig.level,
    power = power
  )
}

# Example: 3 groups, medium effect (f=0.25), 80% power
result <- pwr.anova.test(k = 3, f = 0.25, power = 0.8)
ceiling(result$n)  # Sample size per group
```

---

## Correlation Power

```python
from statsmodels.stats.power import NormalIndPower

def power_correlation(r=None, n=None, alpha=0.05, power=None,
                      alternative='two-sided'):
    """
    Power analysis for correlation.

    Parameters
    ----------
    r : float
        Expected correlation coefficient
    n : int
        Sample size
    alpha : float
        Significance level
    power : float
        Statistical power

    Notes
    -----
    Effect size conventions for r:
    - small: r = 0.1
    - medium: r = 0.3
    - large: r = 0.5
    """
    # Fisher z transformation for correlation
    from math import atanh

    if r is not None:
        effect_size = atanh(r)
    else:
        effect_size = None

    analysis = NormalIndPower()

    if n is None:
        # Need to solve iteratively for correlation
        from scipy.optimize import brentq

        def power_for_n(n_test):
            z = stats.norm.ppf(1 - alpha/2)
            se = 1 / np.sqrt(n_test - 3)
            ncp = effect_size / se
            power_calc = 1 - stats.norm.cdf(z - ncp) + stats.norm.cdf(-z - ncp)
            return power_calc - power

        n = int(brentq(power_for_n, 4, 10000)) + 1
        return n

    elif power is None:
        z = stats.norm.ppf(1 - alpha/2)
        se = 1 / np.sqrt(n - 3)
        ncp = effect_size / se
        power = 1 - stats.norm.cdf(z - ncp) + stats.norm.cdf(-z - ncp)
        return power

    elif r is None:
        # Minimum detectable correlation
        z = stats.norm.ppf(1 - alpha/2)
        se = 1 / np.sqrt(n - 3)

        from scipy.optimize import brentq

        def power_for_r(r_test):
            eff = atanh(r_test)
            ncp = eff / se
            power_calc = 1 - stats.norm.cdf(z - ncp) + stats.norm.cdf(-z - ncp)
            return power_calc - power

        r = brentq(power_for_r, 0.01, 0.99)
        return r


# Quick reference function
print("Sample sizes for detecting correlations (80% power):")
for r in [0.1, 0.2, 0.3, 0.4, 0.5]:
    n = power_correlation(r=r, power=0.8)
    print(f"  r = {r}: n = {n}")
```

### R

```r
library(pwr)

# Correlation
pwr.r.test(r = 0.3, power = 0.8)  # Find n
pwr.r.test(n = 50, power = 0.8)   # Find minimum r
pwr.r.test(r = 0.3, n = 50)       # Find power
```

---

## Survival Analysis Power

```python
def power_survival(hr, n_events=None, alpha=0.05, power=None,
                   ratio=1, p_event=0.5):
    """
    Power for survival analysis (log-rank test / Cox regression).

    Based on Schoenfeld (1983) formula.

    Parameters
    ----------
    hr : float
        Hazard ratio to detect
    n_events : int
        Number of events
    alpha : float
        Significance level
    power : float
        Statistical power
    ratio : float
        Allocation ratio (n2/n1)
    p_event : float
        Probability of event (for calculating total n from events)

    Returns
    -------
    dict
        Required number of events, total sample size
    """
    from scipy import stats

    # Schoenfeld formula
    z_alpha = stats.norm.ppf(1 - alpha/2)

    if n_events is None:
        z_beta = stats.norm.ppf(power)

        # Events needed
        n_events = ((z_alpha + z_beta)**2 * (1 + ratio)**2) / \
                   ((np.log(hr))**2 * ratio)

        n_events = int(np.ceil(n_events))
        n_total = int(np.ceil(n_events / p_event))

        return {
            'n_events': n_events,
            'n_total': n_total,
            'n_per_group': n_total // (1 + ratio)
        }

    elif power is None:
        # Calculate power from number of events
        ncp = np.abs(np.log(hr)) * np.sqrt(n_events * ratio / (1 + ratio)**2)
        power = 1 - stats.norm.cdf(z_alpha - ncp) + stats.norm.cdf(-z_alpha - ncp)
        return {'power': power}


# Example
result = power_survival(hr=0.7, power=0.8)
print(f"To detect HR=0.7 with 80% power:")
print(f"  Events needed: {result['n_events']}")
print(f"  Total sample (50% event rate): {result['n_total']}")
```

### R

```r
library(powerSurvEpi)

# Log-rank test power
# HR to detect, expected events, etc.
powerCT.default(
  nE = 100,           # Number of events
  pE = 0.5,           # Proportion in treatment
  pC = 0.5,           # Proportion in control
  RR = 0.7,           # Hazard ratio
  alpha = 0.05
)

# Calculate required events
ssizeCT.default(
  power = 0.8,
  pE = 0.5,
  pC = 0.5,
  RR = 0.7,
  alpha = 0.05
)
```

---

## Multiple Testing Adjustment

When testing many hypotheses (e.g., thousands of genes), adjust sample size:

```python
def power_with_fdr(base_power=0.8, n_tests=20000, fdr_level=0.05,
                   expected_true=0.05):
    """
    Adjust power calculation for multiple testing.

    Parameters
    ----------
    base_power : float
        Per-test power
    n_tests : int
        Number of tests
    fdr_level : float
        Desired FDR level
    expected_true : float
        Expected proportion of true positives

    Returns
    -------
    dict
        Adjusted power and expected discoveries
    """
    # Number of true positives
    n_true = int(n_tests * expected_true)
    n_null = n_tests - n_true

    # Expected true positives (discoveries)
    true_positives = n_true * base_power

    # Expected false positives at FDR level
    # FDR = FP / (FP + TP)
    # Solving: FP = TP × FDR / (1 - FDR)
    expected_fp = true_positives * fdr_level / (1 - fdr_level)

    # Adjusted "effective power" considering FDR
    effective_power = true_positives / n_true if n_true > 0 else 0

    return {
        'n_tests': n_tests,
        'n_true_effects': n_true,
        'expected_true_discoveries': true_positives,
        'expected_false_discoveries': expected_fp,
        'effective_power': effective_power
    }


def sample_size_fdr_adjustment(base_n, n_tests=20000, fdr_level=0.05):
    """
    Rule of thumb: increase sample size by ~20-50% for FDR-controlled studies.
    """
    # Adjust alpha for multiple testing
    adjusted_alpha = fdr_level / np.sqrt(n_tests) * 10  # Approximate

    # Recalculate n with stricter alpha
    # This is approximate; formal methods exist
    adjustment_factor = 1.2 if n_tests < 10000 else 1.5

    return int(np.ceil(base_n * adjustment_factor))
```

---

## Reporting in Manuscripts

### Methods Section

```markdown
**Sample Size Justification**

Sample size was determined a priori using power analysis. To detect
a [effect size description] with 80% power at α = 0.05 (two-sided),
[N] samples per group are required. This calculation assumed
[key assumptions, e.g., standard deviation from pilot data, expected
variance from literature].

[For RNA-seq]:
Sample size for RNA-seq was estimated using the RNASeqPower package
(Bioconductor). Assuming a biological coefficient of variation of 0.4,
sequencing depth of 10 million reads per sample, and FDR < 0.05,
[N] biological replicates per condition provide >80% power to detect
genes with ≥2-fold differential expression.

[For survival analysis]:
Based on the Schoenfeld formula, [N] events are required to detect
a hazard ratio of [X] with 80% power at α = 0.05 (two-sided log-rank
test). Assuming [X]% event rate over [Y] months, this requires
enrollment of [Z] patients.
```

### Power Analysis Table

Include in supplementary materials:

| Parameter | Value | Source/Justification |
|-----------|-------|---------------------|
| Effect size (d) | 0.8 | Large effect based on pilot |
| α (two-sided) | 0.05 | Conventional |
| Power (1-β) | 0.80 | Standard |
| n per group | 26 | Calculated |
| Total n | 52 | — |
| Software | G*Power 3.1 | — |

---

## Quick Reference Tables

### Two-Group t-test (α = 0.05, 80% power)

| Cohen's d | n per group | Total n |
|-----------|-------------|---------|
| 0.2 (small) | 394 | 788 |
| 0.3 | 176 | 352 |
| 0.5 (medium) | 64 | 128 |
| 0.8 (large) | 26 | 52 |
| 1.0 | 17 | 34 |
| 1.2 | 12 | 24 |

### Correlation (α = 0.05, 80% power)

| r | n |
|---|---|
| 0.1 (small) | 783 |
| 0.2 | 194 |
| 0.3 (medium) | 85 |
| 0.4 | 47 |
| 0.5 (large) | 29 |

### One-Way ANOVA (α = 0.05, 80% power)

| k groups | f = 0.1 (small) | f = 0.25 (medium) | f = 0.4 (large) |
|----------|-----------------|-------------------|-----------------|
| 3 | 322 | 52 | 21 |
| 4 | 274 | 45 | 18 |
| 5 | 240 | 39 | 16 |

---

## Software References

| Tool | Language | Use Case |
|------|----------|----------|
| `pwr` | R | General power analysis |
| `RNASeqPower` | R | RNA-seq studies |
| `powerSurvEpi` | R | Survival analysis |
| `statsmodels.stats.power` | Python | General power analysis |
| **G*Power** | GUI | Interactive, most test types |
| **PASS** | Commercial | Comprehensive, validated |

---

## References

1. Cohen J (1988). *Statistical Power Analysis for the Behavioral Sciences*. 2nd ed. Lawrence Erlbaum.

2. Schoenfeld D (1983). Sample-size formula for the proportional-hazards regression model. *Biometrics* 39:499-503.

3. Hart SN, et al. (2013). Calculating sample size estimates for RNA sequencing data. *J Comput Biol* 20:970-978.

4. Faul F, et al. (2007). G*Power 3: A flexible statistical power analysis program. *Behav Res Methods* 39:175-191.
