# Statistical Test Decision Framework

> Comprehensive decision trees for selecting appropriate statistical tests
> Includes code examples in Python (scipy/statsmodels) and R

---

## Step 1: Identify Your Question Type

### Comparison Questions
"Is there a difference between groups?"
→ Go to [Section 2: Comparison Tests](#section-2-comparison-tests)

### Association Questions
"Is there a relationship between variables?"
→ Go to [Section 3: Association Tests](#section-3-association-tests)

### Prediction Questions
"Can I predict an outcome from predictors?"
→ Go to [Section 4: Regression Models](#section-4-regression-models)

### Distribution Questions
"Does my data follow a specific distribution?"
→ Go to [Section 5: Distribution Tests](#section-5-distribution-tests)

---

## Section 2: Comparison Tests

### 2.1 How Many Groups?

```
                    ┌─────────────────┐
                    │ How many groups?│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         Two groups    Three+ groups   Before/After
              │              │          (same subjects)
              ▼              ▼              │
         Section 2.2    Section 2.3        ▼
                                       Section 2.4
```

---

### 2.2 Two Independent Groups

**Decision Tree:**

```
Is your outcome variable continuous?
├── Yes → Is the data normally distributed in each group?
│         ├── Yes → Are variances equal? (Levene's test)
│         │         ├── Yes → Independent samples t-test
│         │         └── No  → Welch's t-test (default in most software)
│         └── No  → Mann-Whitney U test (Wilcoxon rank-sum)
└── No → Is it categorical?
          ├── Binary → Expected cell counts all ≥ 5?
          │             ├── Yes → Chi-square test
          │             └── No  → Fisher's exact test
          └── Ordinal → Mann-Whitney U test
```

#### Normality Assessment

**Visual Methods:**
1. Histogram with normal curve overlay
2. Q-Q plot (points should follow diagonal)
3. Box plot (check symmetry)

**Statistical Tests:**
- Shapiro-Wilk: Best for n < 50
- Anderson-Darling: n ≥ 50
- Kolmogorov-Smirnov: Large samples

**Rule of Thumb:**
- n > 30: Central Limit Theorem often applies
- Symmetric distribution + no extreme outliers: parametric likely OK

#### Code Examples: Two Independent Groups

**Python (scipy):**

```python
import numpy as np
from scipy import stats

# Sample data
group1 = np.array([23, 25, 28, 30, 27, 26, 24, 29, 31, 28])
group2 = np.array([18, 20, 22, 19, 21, 23, 20, 19, 22, 21])

# Step 1: Check normality
stat1, p_normal1 = stats.shapiro(group1)
stat2, p_normal2 = stats.shapiro(group2)
print(f"Normality p-values: Group1={p_normal1:.4f}, Group2={p_normal2:.4f}")

# Step 2: Check variance equality (if normal)
stat_levene, p_levene = stats.levene(group1, group2)
print(f"Levene's test p-value: {p_levene:.4f}")

# Step 3: Choose and run appropriate test
if p_normal1 > 0.05 and p_normal2 > 0.05:
    # Normal data: use t-test
    # Welch's t-test (default, doesn't assume equal variance)
    t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)
    test_name = "Welch's t-test"
else:
    # Non-normal data: use Mann-Whitney U
    u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
    test_name = "Mann-Whitney U"

print(f"{test_name}: p = {p_value:.4f}")

# Step 4: Calculate effect size (Cohen's d)
pooled_std = np.sqrt(
    ((len(group1)-1)*group1.std(ddof=1)**2 +
     (len(group2)-1)*group2.std(ddof=1)**2) /
    (len(group1) + len(group2) - 2)
)
cohens_d = (group1.mean() - group2.mean()) / pooled_std
print(f"Cohen's d: {cohens_d:.2f}")

# Interpretation of Cohen's d:
# |d| < 0.2: negligible
# 0.2 ≤ |d| < 0.5: small
# 0.5 ≤ |d| < 0.8: medium
# |d| ≥ 0.8: large
```

**R:**

```r
# Sample data
group1 <- c(23, 25, 28, 30, 27, 26, 24, 29, 31, 28)
group2 <- c(18, 20, 22, 19, 21, 23, 20, 19, 22, 21)

# Step 1: Check normality
shapiro.test(group1)
shapiro.test(group2)

# Step 2: Check variance equality
var.test(group1, group2)  # F-test
# or
car::leveneTest(c(group1, group2) ~ factor(rep(1:2, each=10)))

# Step 3: Run appropriate test
# Welch's t-test (default in R, doesn't assume equal variance)
t.test(group1, group2)

# For non-normal data:
wilcox.test(group1, group2, exact = FALSE)

# Step 4: Effect size
library(effectsize)
cohens_d(group1, group2)

# Or manually:
pooled_sd <- sqrt(((length(group1)-1)*sd(group1)^2 +
                   (length(group2)-1)*sd(group2)^2) /
                  (length(group1) + length(group2) - 2))
d <- (mean(group1) - mean(group2)) / pooled_sd
```

---

### 2.3 Three or More Independent Groups

**Decision Tree:**

```
Is your outcome continuous?
├── Yes → Is the data normally distributed in each group?
│         ├── Yes → Are variances homogeneous? (Levene's)
│         │         ├── Yes → One-way ANOVA
│         │         │         └── Post-hoc: Tukey HSD
│         │         └── No  → Welch's ANOVA
│         │                   └── Post-hoc: Games-Howell
│         └── No  → Kruskal-Wallis test
│                   └── Post-hoc: Dunn's test with correction
└── No → Is it categorical?
          └── Chi-square test for independence
              └── Post-hoc: Pairwise chi-square with Bonferroni
```

#### Code Examples: Multiple Groups

**Python:**

```python
import numpy as np
from scipy import stats
import scikit_posthocs as sp  # pip install scikit-posthocs

# Sample data: 3 treatment groups
group_a = np.array([12, 14, 15, 13, 16, 14, 15])
group_b = np.array([18, 20, 19, 21, 22, 20, 19])
group_c = np.array([25, 27, 26, 28, 24, 26, 27])

# Check normality for each group
for i, g in enumerate([group_a, group_b, group_c], 1):
    _, p = stats.shapiro(g)
    print(f"Group {i} normality: p = {p:.4f}")

# Check homogeneity of variances
stat, p_levene = stats.levene(group_a, group_b, group_c)
print(f"Levene's test: p = {p_levene:.4f}")

# If normal and equal variances: One-way ANOVA
f_stat, p_anova = stats.f_oneway(group_a, group_b, group_c)
print(f"ANOVA F({2}, {len(group_a)+len(group_b)+len(group_c)-3}) = {f_stat:.2f}, p = {p_anova:.4f}")

# If non-normal: Kruskal-Wallis
h_stat, p_kruskal = stats.kruskal(group_a, group_b, group_c)
print(f"Kruskal-Wallis H = {h_stat:.2f}, p = {p_kruskal:.4f}")

# Post-hoc tests (if significant)
if p_anova < 0.05 or p_kruskal < 0.05:
    # Combine data for post-hoc
    data = np.concatenate([group_a, group_b, group_c])
    groups = ['A']*len(group_a) + ['B']*len(group_b) + ['C']*len(group_c)

    # Dunn's test (for Kruskal-Wallis)
    posthoc = sp.posthoc_dunn([group_a, group_b, group_c], p_adjust='bonferroni')
    print("\nDunn's post-hoc test:")
    print(posthoc)
```

**R:**

```r
# Sample data
data <- data.frame(
  value = c(12,14,15,13,16,14,15, 18,20,19,21,22,20,19, 25,27,26,28,24,26,27),
  group = factor(rep(c("A", "B", "C"), each = 7))
)

# Check normality by group
by(data$value, data$group, shapiro.test)

# Check homogeneity of variances
car::leveneTest(value ~ group, data = data)

# One-way ANOVA
aov_result <- aov(value ~ group, data = data)
summary(aov_result)

# Effect size (eta-squared)
library(effectsize)
eta_squared(aov_result)

# Post-hoc: Tukey HSD
TukeyHSD(aov_result)

# For non-normal data: Kruskal-Wallis
kruskal.test(value ~ group, data = data)

# Post-hoc: Dunn's test
library(dunn.test)
dunn.test(data$value, data$group, method = "bonferroni")
```

---

### 2.4 Paired/Repeated Measures

**Decision Tree:**

```
Same subjects measured multiple times?
├── Two time points
│   └── Is the difference normally distributed?
│       ├── Yes → Paired t-test
│       └── No  → Wilcoxon signed-rank test
└── Three+ time points
    └── Is the data normally distributed?
        ├── Yes → Repeated measures ANOVA
        │         └── Check sphericity (Mauchly's test)
        │             ├── Satisfied → Use standard RM-ANOVA
        │             └── Violated → Apply Greenhouse-Geisser correction
        └── No  → Friedman test
                  └── Post-hoc: Nemenyi test
```

#### Code Examples: Paired Data

**Python:**

```python
import numpy as np
from scipy import stats

# Paired data: Before and After treatment
before = np.array([120, 125, 130, 118, 140, 135, 128, 122])
after = np.array([118, 120, 125, 115, 132, 128, 125, 118])

# Calculate differences
diff = after - before

# Check normality of differences
stat, p_normal = stats.shapiro(diff)
print(f"Normality of differences: p = {p_normal:.4f}")

if p_normal > 0.05:
    # Paired t-test
    t_stat, p_value = stats.ttest_rel(before, after)
    test_name = "Paired t-test"
else:
    # Wilcoxon signed-rank
    stat, p_value = stats.wilcoxon(before, after)
    test_name = "Wilcoxon signed-rank"

print(f"{test_name}: p = {p_value:.4f}")

# Effect size for paired data (Cohen's d for paired)
cohens_d = diff.mean() / diff.std(ddof=1)
print(f"Cohen's d (paired): {cohens_d:.2f}")
```

**R:**

```r
# Paired data
before <- c(120, 125, 130, 118, 140, 135, 128, 122)
after <- c(118, 120, 125, 115, 132, 128, 125, 118)

# Check normality of differences
diff <- after - before
shapiro.test(diff)

# Paired t-test
t.test(before, after, paired = TRUE)

# Wilcoxon signed-rank (non-parametric)
wilcox.test(before, after, paired = TRUE)

# Effect size
library(effectsize)
cohens_d(before, after, paired = TRUE)

# For 3+ time points: Repeated measures ANOVA
# Using ezANOVA from ez package
library(ez)
# Requires long-format data with subject ID
```

---

## Section 3: Association Tests

### 3.1 Correlation Decision Tree

```
Two continuous variables?
├── Yes → Are both approximately normal?
│         ├── Yes → Pearson correlation (r)
│         └── No  → Spearman correlation (ρ) or Kendall's τ
└── No → Both ordinal?
          └── Spearman or Kendall's τ
```

### 3.2 Correlation Interpretation

| |r| or |ρ| | Interpretation |
|------------|----------------|
| 0.00 - 0.19 | Negligible |
| 0.20 - 0.39 | Weak |
| 0.40 - 0.59 | Moderate |
| 0.60 - 0.79 | Strong |
| 0.80 - 1.00 | Very strong |

**Caveats:**
- Always visualize with scatter plot first
- Check for outliers driving the correlation
- Correlation ≠ causation
- Consider confounding variables

#### Code Examples: Correlation

**Python:**

```python
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Sample data
x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
y = np.array([2.1, 4.2, 5.8, 8.1, 9.5, 12.3, 14.0, 15.8, 18.2, 20.0])

# Visualize first (always!)
plt.scatter(x, y)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Scatter plot before correlation')
plt.show()

# Pearson correlation (parametric)
r, p_pearson = stats.pearsonr(x, y)
print(f"Pearson r = {r:.3f}, p = {p_pearson:.4f}")

# Spearman correlation (non-parametric)
rho, p_spearman = stats.spearmanr(x, y)
print(f"Spearman ρ = {rho:.3f}, p = {p_spearman:.4f}")

# Kendall's tau (robust to ties)
tau, p_kendall = stats.kendalltau(x, y)
print(f"Kendall τ = {tau:.3f}, p = {p_kendall:.4f}")

# 95% confidence interval for Pearson r (Fisher transformation)
n = len(x)
z = np.arctanh(r)  # Fisher z-transformation
se = 1 / np.sqrt(n - 3)
ci_z = (z - 1.96*se, z + 1.96*se)
ci_r = np.tanh(ci_z)  # Back-transform
print(f"95% CI for r: [{ci_r[0]:.3f}, {ci_r[1]:.3f}]")
```

**R:**

```r
# Sample data
x <- c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
y <- c(2.1, 4.2, 5.8, 8.1, 9.5, 12.3, 14.0, 15.8, 18.2, 20.0)

# Visualize
plot(x, y, main = "Scatter plot", pch = 19)

# Pearson correlation
cor.test(x, y, method = "pearson")

# Spearman correlation
cor.test(x, y, method = "spearman")

# Kendall's tau
cor.test(x, y, method = "kendall")

# Correlation matrix for multiple variables
data <- data.frame(x, y, z = rnorm(10))
cor(data, method = "pearson")

# With p-values
library(Hmisc)
rcorr(as.matrix(data), type = "pearson")
```

---

## Section 4: Regression Models

### 4.1 Regression Decision Tree

```
What is your outcome variable type?
├── Continuous → Linear regression
│   └── Multiple predictors? → Multiple linear regression
│       └── Check assumptions: linearity, normality of residuals,
│           homoscedasticity, no multicollinearity
├── Binary (0/1) → Logistic regression
│   └── Output: Odds ratios (OR)
├── Count data → Poisson or Negative Binomial regression
│   └── Overdispersion? → Negative Binomial preferred
└── Time-to-event → Cox proportional hazards
    └── Output: Hazard ratios (HR)
```

#### Code Examples: Linear Regression

**Python:**

```python
import numpy as np
import statsmodels.api as sm
from scipy import stats

# Sample data
X = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6],
              [6, 7], [7, 8], [8, 9], [9, 10], [10, 11]])
y = np.array([2.5, 4.2, 5.8, 8.1, 9.5, 12.3, 14.0, 15.8, 18.2, 20.0])

# Add constant for intercept
X_with_const = sm.add_constant(X)

# Fit model
model = sm.OLS(y, X_with_const)
results = model.fit()

# Full summary
print(results.summary())

# Key outputs
print(f"\nR² = {results.rsquared:.3f}")
print(f"Adjusted R² = {results.rsquared_adj:.3f}")
print(f"\nCoefficients:")
for name, coef, se, p in zip(['Intercept', 'X1', 'X2'],
                              results.params, results.bse, results.pvalues):
    print(f"  {name}: β = {coef:.3f}, SE = {se:.3f}, p = {p:.4f}")

# Check residuals
residuals = results.resid
_, p_normal = stats.shapiro(residuals)
print(f"\nResidual normality (Shapiro-Wilk): p = {p_normal:.4f}")
```

**R:**

```r
# Sample data
data <- data.frame(
  y = c(2.5, 4.2, 5.8, 8.1, 9.5, 12.3, 14.0, 15.8, 18.2, 20.0),
  x1 = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
  x2 = c(2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
)

# Fit model
model <- lm(y ~ x1 + x2, data = data)
summary(model)

# Confidence intervals
confint(model)

# ANOVA table
anova(model)

# Check assumptions
par(mfrow = c(2, 2))
plot(model)

# Residual normality
shapiro.test(residuals(model))

# Multicollinearity (VIF)
library(car)
vif(model)
```

#### Code Examples: Logistic Regression

**Python:**

```python
import numpy as np
import statsmodels.api as sm

# Binary outcome data
X = np.array([[25], [30], [35], [40], [45], [50], [55], [60], [65], [70]])
y = np.array([0, 0, 0, 0, 1, 1, 0, 1, 1, 1])

# Add constant
X_with_const = sm.add_constant(X)

# Fit logistic regression
model = sm.Logit(y, X_with_const)
results = model.fit()

print(results.summary())

# Odds ratios with confidence intervals
odds_ratios = np.exp(results.params)
conf = np.exp(results.conf_int())
print("\nOdds Ratios:")
print(f"  Age: OR = {odds_ratios[1]:.3f}, 95% CI [{conf[1, 0]:.3f}, {conf[1, 1]:.3f}]")
```

**R:**

```r
# Binary outcome
data <- data.frame(
  outcome = c(0, 0, 0, 0, 1, 1, 0, 1, 1, 1),
  age = c(25, 30, 35, 40, 45, 50, 55, 60, 65, 70)
)

# Fit logistic regression
model <- glm(outcome ~ age, data = data, family = binomial)
summary(model)

# Odds ratios
exp(coef(model))

# Confidence intervals for OR
exp(confint(model))

# Pseudo R-squared
library(pscl)
pR2(model)
```

---

## Section 5: Distribution Tests

### 5.1 Normality Tests

| Test | Best For | Code |
|------|----------|------|
| Shapiro-Wilk | n < 50 | `stats.shapiro(x)` / `shapiro.test(x)` |
| Anderson-Darling | n ≥ 50 | `stats.anderson(x)` |
| Kolmogorov-Smirnov | Large n | `stats.kstest(x, 'norm')` |
| D'Agostino-Pearson | n ≥ 20 | `stats.normaltest(x)` |

### 5.2 Homogeneity of Variance Tests

| Test | Code |
|------|------|
| Levene's (robust) | `stats.levene(g1, g2)` / `car::leveneTest()` |
| Bartlett's (sensitive to normality) | `stats.bartlett(g1, g2)` / `bartlett.test()` |

---

## Quick Reference Card

### One-Sentence Guide

| Scenario | Test |
|----------|------|
| Two groups, normal | Welch's t-test |
| Two groups, non-normal | Mann-Whitney U |
| Two groups, paired | Paired t-test / Wilcoxon signed-rank |
| 3+ groups, normal | One-way ANOVA + Tukey |
| 3+ groups, non-normal | Kruskal-Wallis + Dunn |
| Two continuous vars | Pearson / Spearman |
| Binary outcome | Logistic regression |
| Survival | Kaplan-Meier, Cox regression |
| Categorical vs categorical | Chi-square / Fisher's exact |

### Sample Size Guidelines

| Test | Minimum n per group |
|------|---------------------|
| t-test (medium effect d=0.5) | ~30 |
| ANOVA (3 groups) | ~20 |
| Correlation (r=0.3) | ~60 |
| Chi-square | 5+ per cell expected |
| Regression | 10-20 per predictor |

---

*See also: `multiple_testing_correction.md`, `power_sample_size.md`*
