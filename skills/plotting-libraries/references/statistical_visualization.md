# Statistical Visualization Patterns

> Implementation patterns for visualizing statistical test results
> Coordinate with **statistical-analysis** skill for test selection

---

## Group Comparisons (t-test, ANOVA)

**Python:**
```python
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

fig, ax = plt.subplots(figsize=(8, 6))

# Box plot with individual data points (preferred over bar plots)
sns.boxplot(data=df, x='group', y='value', ax=ax, width=0.5)
sns.stripplot(data=df, x='group', y='value', ax=ax, color='black', alpha=0.5, size=4)

# Add significance annotation
# For automated significance bars, use statannotations package
ax.set_ylabel('Measurement (units)')
ax.set_title('Group Comparison')
```

**R:**
```r
library(ggplot2)
library(ggpubr)

ggplot(df, aes(x = group, y = value, fill = group)) +
  geom_boxplot(outlier.shape = NA, width = 0.5) +
  geom_jitter(width = 0.15, alpha = 0.5) +
  stat_compare_means(method = "t.test") +  # or "anova", "wilcox.test"
  theme_classic() +
  theme(legend.position = "none")
```

---

## Normality Assessment (Q-Q Plots)

**Python:**
```python
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Histogram with normal curve overlay
axes[0].hist(data, bins=30, density=True, alpha=0.7)
x = np.linspace(data.min(), data.max(), 100)
axes[0].plot(x, stats.norm.pdf(x, data.mean(), data.std()), 'r-', lw=2)
axes[0].set_title('Distribution')

# Q-Q plot
stats.probplot(data, dist="norm", plot=axes[1])
axes[1].set_title('Q-Q Plot')
```

**R:**
```r
library(ggplot2)
library(patchwork)

p1 <- ggplot(df, aes(x = value)) +
  geom_histogram(aes(y = after_stat(density)), bins = 30, fill = "steelblue") +
  stat_function(fun = dnorm, args = list(mean = mean(df$value), sd = sd(df$value)),
                color = "red", linewidth = 1)

p2 <- ggplot(df, aes(sample = value)) +
  stat_qq() + stat_qq_line(color = "red")

p1 + p2
```

---

## Regression Diagnostics

**Python:**
```python
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np

# Fit model
model = sm.OLS(y, sm.add_constant(X)).fit()

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Residuals vs Fitted
axes[0, 0].scatter(model.fittedvalues, model.resid, alpha=0.5)
axes[0, 0].axhline(y=0, color='r', linestyle='--')
axes[0, 0].set_xlabel('Fitted values')
axes[0, 0].set_ylabel('Residuals')

# Q-Q plot of residuals
sm.qqplot(model.resid, line='45', ax=axes[0, 1])

# Scale-Location
axes[1, 0].scatter(model.fittedvalues, np.sqrt(np.abs(model.resid)), alpha=0.5)
axes[1, 0].set_xlabel('Fitted values')
axes[1, 0].set_ylabel('√|Residuals|')

# Residuals vs Leverage
sm.graphics.influence_plot(model, ax=axes[1, 1])

plt.tight_layout()
```

**R:**
```r
# Base R diagnostic plots (4 classic plots)
par(mfrow = c(2, 2))
plot(model)

# ggplot2 version with ggfortify
library(ggfortify)
autoplot(model, which = 1:4)
```

---

## Correlation Matrices

**Python:**
```python
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# Compute correlation matrix
corr = df.corr()

# Create mask for upper triangle (avoid redundancy)
mask = np.triu(np.ones_like(corr, dtype=bool))

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, vmin=-1, vmax=1, ax=ax)
ax.set_title('Correlation Matrix')
```

**R:**
```r
library(corrplot)

cor_matrix <- cor(df, use = "pairwise.complete.obs")
corrplot(cor_matrix, method = "color", type = "lower",
         addCoef.col = "black", number.cex = 0.7,
         tl.col = "black", tl.srt = 45)
```

---

## Forest Plots (Effect Sizes)

**Python:**
```python
import matplotlib.pyplot as plt

# Data: estimates, lower CI, upper CI, labels
fig, ax = plt.subplots(figsize=(8, 6))

y_pos = range(len(labels))
ax.errorbar(estimates, y_pos, xerr=[estimates - lower_ci, upper_ci - estimates],
            fmt='o', capsize=5, color='steelblue')
ax.axvline(x=0, color='gray', linestyle='--')  # or x=1 for ratios
ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.set_xlabel('Effect Size (95% CI)')
```

**R:**
```r
library(ggplot2)

ggplot(results, aes(x = estimate, y = reorder(variable, estimate))) +
  geom_point(size = 3) +
  geom_errorbarh(aes(xmin = lower_ci, xmax = upper_ci), height = 0.2) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "gray") +
  labs(x = "Effect Size (95% CI)", y = NULL) +
  theme_minimal()
```

---

## Recommended Packages

| Task | Python | R |
|------|--------|---|
| Significance annotations | `statannotations` | `ggpubr::stat_compare_means` |
| Regression diagnostics | `statsmodels.graphics` | `ggfortify::autoplot` |
| Correlation plots | `seaborn.heatmap` | `corrplot`, `ggcorrplot` |
| Forest plots | `forestplot` | `forestplot`, `ggforestplot` |
| Effect size visualization | Custom matplotlib | `effectsize` + ggplot2 |
