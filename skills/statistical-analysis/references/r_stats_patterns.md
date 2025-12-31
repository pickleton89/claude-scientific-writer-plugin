# R Statistical Analysis Patterns

> Complete reference for base R stats and common statistical packages

---

## Quick Package Reference

```r
# Core statistical packages
library(stats)        # Base R (loaded by default)
library(car)          # Companion to Applied Regression
library(lme4)         # Mixed-effects models
library(emmeans)      # Estimated marginal means
library(effectsize)   # Effect size calculations
library(performance)  # Model diagnostics
library(ggplot2)      # Visualization
library(dplyr)        # Data manipulation

# Bioinformatics statistical packages
library(edgeR)        # RNA-seq differential expression
library(DESeq2)       # RNA-seq differential expression
library(limma)        # Linear models for microarray/RNA-seq
```

---

## Descriptive Statistics

### Basic Summary

```r
# Built-in summary
summary(data)

# Custom summary function
describe_numeric <- function(x, na.rm = TRUE) {
  c(
    n = sum(!is.na(x)),
    mean = mean(x, na.rm = na.rm),
    sd = sd(x, na.rm = na.rm),
    se = sd(x, na.rm = na.rm) / sqrt(sum(!is.na(x))),
    median = median(x, na.rm = na.rm),
    min = min(x, na.rm = na.rm),
    max = max(x, na.rm = na.rm),
    q25 = quantile(x, 0.25, na.rm = na.rm),
    q75 = quantile(x, 0.75, na.rm = na.rm),
    iqr = IQR(x, na.rm = na.rm),
    skewness = e1071::skewness(x, na.rm = na.rm),
    kurtosis = e1071::kurtosis(x, na.rm = na.rm)
  )
}

# Group-wise summary with dplyr
library(dplyr)
df %>%
  group_by(group) %>%
  summarise(
    n = n(),
    mean = mean(value, na.rm = TRUE),
    sd = sd(value, na.rm = TRUE),
    se = sd / sqrt(n),
    median = median(value, na.rm = TRUE),
    .groups = "drop"
  )
```

### Confidence Intervals

```r
# CI for mean (t-distribution)
ci_mean <- function(x, conf.level = 0.95) {
  n <- length(x)
  mean_x <- mean(x)
  se <- sd(x) / sqrt(n)
  t_crit <- qt((1 + conf.level) / 2, df = n - 1)

  c(
    mean = mean_x,
    lower = mean_x - t_crit * se,
    upper = mean_x + t_crit * se
  )
}

# Bootstrap CI
library(boot)
boot_ci <- function(x, statistic = mean, R = 10000, conf.level = 0.95) {
  boot_fn <- function(data, indices) statistic(data[indices])
  boot_result <- boot(x, boot_fn, R = R)
  boot.ci(boot_result, conf = conf.level, type = "perc")
}
```

---

## Normality Testing

### Visual Assessment

```r
# Q-Q plot with base R
qqnorm(data)
qqline(data, col = "red")

# Comprehensive normality plots
normality_plots <- function(x, title = "") {
  par(mfrow = c(1, 2))

  # Histogram with normal curve
  hist(x, probability = TRUE, main = paste(title, "- Histogram"),
       xlab = "Value", col = "lightblue", border = "white")
  curve(dnorm(x, mean(x), sd(x)), add = TRUE, col = "red", lwd = 2)

  # Q-Q plot
  qqnorm(x, main = paste(title, "- Q-Q Plot"))
  qqline(x, col = "red", lwd = 2)

  par(mfrow = c(1, 1))
}
```

### Statistical Tests

```r
# Shapiro-Wilk (best for n < 50)
shapiro.test(data)

# Kolmogorov-Smirnov (against specified distribution)
ks.test(data, "pnorm", mean(data), sd(data))

# Anderson-Darling (nortest package)
library(nortest)
ad.test(data)

# Comprehensive normality assessment
assess_normality <- function(x, alpha = 0.05) {
  results <- list()

  # Shapiro-Wilk (n <= 5000)
  if (length(x) <= 5000 && length(x) >= 3) {
    sw <- shapiro.test(x)
    results$shapiro_wilk <- list(
      statistic = sw$statistic,
      p_value = sw$p.value,
      normal = sw$p.value > alpha
    )
  }

  # Anderson-Darling
  if (requireNamespace("nortest", quietly = TRUE)) {
    ad <- nortest::ad.test(x)
    results$anderson_darling <- list(
      statistic = ad$statistic,
      p_value = ad$p.value,
      normal = ad$p.value > alpha
    )
  }

  # Decision
  p_values <- sapply(results, function(r) r$p_value)
  results$conclusion <- if (all(p_values > alpha)) {
    "Data appear normally distributed"
  } else {
    "Evidence against normality"
  }

  results
}
```

---

## Two-Sample Comparisons

### Independent Samples

```r
# Student's t-test (equal variances)
t.test(group1, group2, var.equal = TRUE)

# Welch's t-test (unequal variances) - DEFAULT
t.test(group1, group2)

# Formula interface
t.test(value ~ group, data = df)

# Mann-Whitney U / Wilcoxon rank-sum (non-parametric)
wilcox.test(group1, group2)
wilcox.test(value ~ group, data = df)

# Comprehensive comparison function
compare_groups <- function(x, y, alpha = 0.05) {
  # Check normality
  norm_x <- shapiro.test(x)$p.value
  norm_y <- shapiro.test(y)$p.value
  both_normal <- norm_x > alpha && norm_y > alpha

  results <- list(
    n1 = length(x),
    n2 = length(y),
    normality = list(
      group1_p = norm_x,
      group2_p = norm_y,
      both_normal = both_normal
    )
  )

  if (both_normal) {
    # Check variance homogeneity
    var_test <- var.test(x, y)
    equal_var <- var_test$p.value > alpha

    if (equal_var) {
      test <- t.test(x, y, var.equal = TRUE)
      test_name <- "Independent t-test"
    } else {
      test <- t.test(x, y, var.equal = FALSE)
      test_name <- "Welch's t-test"
    }

    results$variance_test <- list(
      F = var_test$statistic,
      p_value = var_test$p.value,
      equal_variance = equal_var
    )

    # Effect size: Cohen's d
    pooled_sd <- sqrt(
      ((length(x) - 1) * var(x) + (length(y) - 1) * var(y)) /
        (length(x) + length(y) - 2)
    )
    d <- (mean(x) - mean(y)) / pooled_sd

    results$effect_size <- list(
      cohens_d = d,
      interpretation = interpret_cohens_d(d)
    )

  } else {
    test <- wilcox.test(x, y)
    test_name <- "Mann-Whitney U"

    # Effect size: rank-biserial correlation
    r <- 1 - (2 * test$statistic) / (length(x) * length(y))
    results$effect_size <- list(
      rank_biserial_r = r
    )
  }

  results$test <- list(
    name = test_name,
    statistic = test$statistic,
    p_value = test$p.value,
    significant = test$p.value < alpha
  )

  results
}

interpret_cohens_d <- function(d) {
  d <- abs(d)
  if (d < 0.2) return("negligible")
  if (d < 0.5) return("small")
  if (d < 0.8) return("medium")
  return("large")
}
```

### Paired Samples

```r
# Paired t-test
t.test(before, after, paired = TRUE)

# Wilcoxon signed-rank (non-parametric)
wilcox.test(before, after, paired = TRUE)

# With data frame
t.test(value ~ time, data = df, paired = TRUE)
```

---

## Multiple Group Comparisons

### ANOVA

```r
# One-way ANOVA
model <- aov(value ~ group, data = df)
summary(model)

# Check assumptions
# 1. Normality of residuals
shapiro.test(residuals(model))

# 2. Homogeneity of variance
library(car)
leveneTest(value ~ group, data = df)

# If assumptions violated, use Welch's ANOVA
oneway.test(value ~ group, data = df, var.equal = FALSE)

# Effect size: eta-squared
library(effectsize)
eta_squared(model)

# Post-hoc tests
# Tukey HSD (balanced designs, equal variances)
TukeyHSD(model)

# Bonferroni-corrected pairwise t-tests
pairwise.t.test(df$value, df$group, p.adjust.method = "bonferroni")

# Games-Howell (unequal variances)
library(rstatix)
games_howell_test(df, value ~ group)
```

### Two-Way ANOVA

```r
# Two-way ANOVA with interaction
model <- aov(value ~ factor1 * factor2, data = df)
summary(model)

# Main effects only
model <- aov(value ~ factor1 + factor2, data = df)

# Type III sums of squares (unbalanced designs)
library(car)
Anova(model, type = "III")

# Estimated marginal means
library(emmeans)
emm <- emmeans(model, ~ factor1 * factor2)
pairs(emm)  # Pairwise comparisons
```

### Kruskal-Wallis (Non-parametric ANOVA)

```r
# Kruskal-Wallis test
kruskal.test(value ~ group, data = df)

# Post-hoc: Dunn's test
library(dunn.test)
dunn.test(df$value, df$group, method = "bonferroni")

# Alternative: pairwise Wilcoxon
pairwise.wilcox.test(df$value, df$group, p.adjust.method = "BH")
```

---

## Repeated Measures

### Repeated Measures ANOVA

```r
# Within-subjects ANOVA
library(ez)
ezANOVA(
  data = df_long,
  dv = value,
  wid = subject_id,
  within = time_point,
  detailed = TRUE
)

# Mixed design (between + within)
ezANOVA(
  data = df_long,
  dv = value,
  wid = subject_id,
  within = time_point,
  between = group
)

# Check sphericity (Mauchly's test included in ezANOVA output)
# If violated, use Greenhouse-Geisser or Huynh-Feldt correction
```

### Linear Mixed-Effects Models

```r
library(lme4)
library(lmerTest)  # For p-values

# Random intercept
model <- lmer(value ~ condition + (1 | subject_id), data = df)
summary(model)

# Random intercept and slope
model <- lmer(value ~ condition + (condition | subject_id), data = df)

# ANOVA-like table with p-values
anova(model)

# Post-hoc comparisons
library(emmeans)
emmeans(model, pairwise ~ condition)

# Model diagnostics
plot(model)  # Residuals vs fitted
qqnorm(residuals(model))
```

---

## Correlation Analysis

```r
# Pearson correlation
cor.test(x, y, method = "pearson")

# Spearman correlation (rank-based)
cor.test(x, y, method = "spearman")

# Kendall's tau
cor.test(x, y, method = "kendall")

# Correlation matrix
cor(df[, numeric_cols], use = "pairwise.complete.obs")

# Correlation matrix with p-values
library(Hmisc)
rcorr(as.matrix(df[, numeric_cols]))

# Visualization
library(corrplot)
cor_matrix <- cor(df[, numeric_cols], use = "complete.obs")
corrplot(cor_matrix, method = "color", type = "upper",
         addCoef.col = "black", tl.col = "black")

# Comprehensive correlation function
test_correlation <- function(x, y, method = "auto", alpha = 0.05) {
  if (method == "auto") {
    # Check normality
    norm_x <- shapiro.test(x)$p.value > alpha
    norm_y <- shapiro.test(y)$p.value > alpha
    method <- if (norm_x && norm_y) "pearson" else "spearman"
  }

  result <- cor.test(x, y, method = method)

  list(
    method = result$method,
    estimate = result$estimate,
    p_value = result$p.value,
    conf_int = result$conf.int,
    significant = result$p.value < alpha
  )
}
```

---

## Regression Analysis

### Linear Regression

```r
# Simple linear regression
model <- lm(y ~ x, data = df)
summary(model)

# Multiple regression
model <- lm(y ~ x1 + x2 + x3, data = df)

# With interactions
model <- lm(y ~ x1 * x2, data = df)

# Polynomial terms
model <- lm(y ~ x + I(x^2), data = df)

# Model coefficients
coef(model)
confint(model)  # Confidence intervals

# Model diagnostics
par(mfrow = c(2, 2))
plot(model)
par(mfrow = c(1, 1))

# Comprehensive diagnostics
library(performance)
check_model(model)

# Assumption checks
library(car)
# Multicollinearity
vif(model)

# Normality of residuals
shapiro.test(residuals(model))

# Heteroscedasticity
ncvTest(model)

# Influential observations
influencePlot(model)
```

### Logistic Regression

```r
# Binary logistic regression
model <- glm(outcome ~ x1 + x2, data = df, family = binomial)
summary(model)

# Odds ratios with confidence intervals
exp(coef(model))
exp(confint(model))

# Model fit
library(ResourceSelection)
hoslem.test(df$outcome, fitted(model))  # Hosmer-Lemeshow

# Pseudo R-squared
library(pscl)
pR2(model)

# ROC curve and AUC
library(pROC)
roc_obj <- roc(df$outcome, fitted(model))
auc(roc_obj)
plot(roc_obj)

# Predictions
predict(model, type = "response")  # Probabilities
```

### Ordinal Regression

```r
library(MASS)

# Proportional odds model
model <- polr(ordered_outcome ~ x1 + x2, data = df)
summary(model)

# Test proportional odds assumption
library(brant)
brant(model)

# Odds ratios
exp(coef(model))
```

---

## Categorical Data Analysis

### Chi-Square and Fisher's Exact

```r
# Contingency table
table <- table(df$factor1, df$factor2)

# Chi-square test
chisq.test(table)

# Fisher's exact test (for small expected frequencies)
fisher.test(table)

# Expected frequencies
chisq.test(table)$expected

# Effect size: Cramer's V
library(vcd)
assocstats(table)

# Comprehensive contingency analysis
analyze_contingency <- function(table, alpha = 0.05) {
  chi <- chisq.test(table)
  expected <- chi$expected

  # Check if Fisher's exact is needed
  use_fisher <- any(expected < 5)

  if (use_fisher && all(dim(table) == 2)) {
    fisher <- fisher.test(table)
    test_result <- list(
      name = "Fisher's exact",
      p_value = fisher$p.value,
      odds_ratio = fisher$estimate
    )
  } else {
    test_result <- list(
      name = "Chi-square",
      statistic = chi$statistic,
      df = chi$parameter,
      p_value = chi$p.value
    )
  }

  # Cramer's V
  n <- sum(table)
  k <- min(dim(table)) - 1
  cramers_v <- sqrt(chi$statistic / (n * k))

  list(
    table = table,
    expected = expected,
    test = test_result,
    effect_size = cramers_v,
    significant = test_result$p_value < alpha
  )
}
```

### McNemar's Test (Paired Categorical)

```r
# 2x2 table of paired observations
mcnemar.test(table)
```

---

## Multiple Testing Correction

```r
# p.adjust for various methods
p_values <- c(0.01, 0.04, 0.03, 0.08, 0.001)

# Bonferroni (FWER control)
p.adjust(p_values, method = "bonferroni")

# Holm (step-down Bonferroni)
p.adjust(p_values, method = "holm")

# Benjamini-Hochberg (FDR control) - RECOMMENDED for genomics
p.adjust(p_values, method = "BH")

# Benjamini-Yekutieli (FDR, more conservative)
p.adjust(p_values, method = "BY")

# q-values
library(qvalue)
q <- qvalue(p_values)
q$qvalues

# Compare methods
compare_corrections <- function(p_values, alpha = 0.05) {
  methods <- c("bonferroni", "holm", "BH", "BY")
  results <- sapply(methods, function(m) {
    adjusted <- p.adjust(p_values, method = m)
    sum(adjusted < alpha)
  })
  data.frame(
    method = methods,
    n_significant = results
  )
}
```

---

## Power Analysis

```r
library(pwr)

# Two-sample t-test power
# Find required n for given power
pwr.t.test(
  d = 0.5,        # Effect size (Cohen's d)
  sig.level = 0.05,
  power = 0.80,
  type = "two.sample"
)

# Find power for given n
pwr.t.test(
  n = 30,
  d = 0.5,
  sig.level = 0.05,
  type = "two.sample"
)

# ANOVA power
pwr.anova.test(
  k = 3,          # Number of groups
  n = 30,         # Sample size per group
  f = 0.25,       # Effect size
  sig.level = 0.05
)

# Chi-square power
pwr.chisq.test(
  w = 0.3,        # Effect size
  df = 2,
  N = 100,
  sig.level = 0.05
)

# Correlation power
pwr.r.test(
  r = 0.3,
  sig.level = 0.05,
  power = 0.80
)
```

---

## RNA-seq Specific Patterns

### edgeR Workflow

```r
library(edgeR)

# Create DGEList
dge <- DGEList(counts = count_matrix, group = group_factor)

# Filter low-expressed genes
keep <- filterByExpr(dge, group = group_factor)
dge <- dge[keep, , keep.lib.sizes = FALSE]

# TMM normalization
dge <- calcNormFactors(dge, method = "TMM")

# Estimate dispersion
design <- model.matrix(~ group_factor)
dge <- estimateDisp(dge, design)

# Fit model
fit <- glmQLFit(dge, design)

# Test for differential expression
qlf <- glmQLFTest(fit, coef = 2)

# Get results
results <- topTags(qlf, n = Inf)$table
```

### DESeq2 Workflow

```r
library(DESeq2)

# Create DESeqDataSet
dds <- DESeqDataSetFromMatrix(
  countData = count_matrix,
  colData = sample_info,
  design = ~ condition
)

# Filter low counts
keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep, ]

# Run DESeq2
dds <- DESeq(dds)

# Get results
res <- results(dds, contrast = c("condition", "treatment", "control"))

# Shrinkage for visualization
res_shrunk <- lfcShrink(dds, coef = 2, type = "apeglm")

# Summary
summary(res, alpha = 0.05)

# Significant genes
sig_genes <- subset(res, padj < 0.05 & abs(log2FoldChange) > 1)
```

### limma-voom Workflow

```r
library(limma)
library(edgeR)

# Create DGEList and normalize
dge <- DGEList(counts = count_matrix)
dge <- calcNormFactors(dge, method = "TMM")

# Filter
keep <- filterByExpr(dge, design = design_matrix)
dge <- dge[keep, , keep.lib.sizes = FALSE]

# Voom transformation
v <- voom(dge, design_matrix, plot = TRUE)

# Fit linear model
fit <- lmFit(v, design_matrix)
fit <- eBayes(fit)

# Results
results <- topTable(fit, coef = 2, n = Inf)
```

---

## Reporting Templates

### Methods Section (R)

```r
generate_methods <- function(test_result) {
  test_name <- test_result$test$name

  sprintf(
    "Statistical analysis was performed using R version %s. %s was used to compare groups. Significance was set at α = 0.05.",
    R.version.string,
    test_name
  )
}
```

### Results Reporting

```r
format_p_value <- function(p) {
  if (p < 0.001) {
    "p < 0.001"
  } else if (p < 0.01) {
    sprintf("p = %.3f", p)
  } else {
    sprintf("p = %.2f", p)
  }
}

format_result <- function(test_result) {
  test <- test_result$test
  sprintf(
    "%s revealed %s difference (%s = %.2f, %s).",
    test$name,
    if (test$significant) "a significant" else "no significant",
    if (grepl("t-test", test$name)) "t" else if (grepl("Mann", test$name)) "U" else "statistic",
    test$statistic,
    format_p_value(test$p_value)
  )
}
```

---

## Session Information

Always report for reproducibility:

```r
sessionInfo()

# Or more detailed
devtools::session_info()
```
