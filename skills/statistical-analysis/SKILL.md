---
name: statistical-analysis
version: 1.2.0
description: "Statistical methods for scientific data analysis. Test selection decision trees, code generation (Python scipy/statsmodels, R), multiple testing correction, and result interpretation."
when_to_use: |
  Use when: selecting statistical tests, generating Python/R code for hypothesis testing,
  interpreting p-values and effect sizes, planning sample sizes, reporting statistics in manuscripts.
  Do NOT use for: machine learning model development, Bayesian inference, time series analysis,
  or causal inference methods (these require specialized resources).
license: MIT
quantification-reference: "../QUANTIFICATION_THRESHOLDS.md"
---

> **Quantified Thresholds:** This skill references shared thresholds from [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §3 (Replication & Sample Size), §10 (Statistical Reporting Completeness), and §4 (Issue Severity Classification for statistical errors).

<objective>
Guide rigorous statistical analysis for scientific research, with emphasis on bioinformatics and high-dimensional data. This skill provides decision frameworks for test selection, code patterns for implementation, and interpretation guidance for manuscripts.
</objective>

<prerequisites>
## Required Packages

**Python:**
```bash
pip install scipy statsmodels numpy pandas
# For power analysis:
pip install statsmodels  # includes power module
```

**R:**
```r
install.packages(c("stats", "car", "effectsize", "pwr"))
# For RNA-seq:
BiocManager::install(c("DESeq2", "edgeR", "limma"))
```

Code patterns in `references/` assume these packages are available. Verify installation before running generated code.
</prerequisites>

<scope>
## In Scope

- Test selection based on data characteristics
- Code generation for Python (scipy, statsmodels) and R
- Multiple testing correction strategies
- Effect size calculation and interpretation
- Power analysis and sample size estimation
- Common statistical pitfalls and how to avoid them
- Normalization methods for sequencing data
- Dimensionality reduction interpretation
- Clustering method selection
- Survival analysis fundamentals

## Out of Scope

- Machine learning model development (see separate resources)
- Bayesian inference (specialized topic requiring dedicated treatment)
- Time series analysis (specialized topic)
- Causal inference methods (specialized topic)
- Deep learning architectures
</scope>

<decision_framework>
## Quick Test Selection

### Comparing Two Groups

| Data Type | Distribution | Paired? | Test |
|-----------|--------------|---------|------|
| Continuous | Normal | No | Independent t-test |
| Continuous | Normal | Yes | Paired t-test |
| Continuous | Non-normal | No | Mann-Whitney U |
| Continuous | Non-normal | Yes | Wilcoxon signed-rank |
| Categorical | — | No | Chi-square / Fisher's exact |
| Proportions | — | No | Z-test for proportions |

### Comparing Multiple Groups

| Data Type | Distribution | Test | Post-hoc |
|-----------|--------------|------|----------|
| Continuous | Normal | One-way ANOVA | Tukey HSD |
| Continuous | Non-normal | Kruskal-Wallis | Dunn's test |
| Continuous | Normal, repeated | Repeated measures ANOVA | — |
| Continuous | Non-normal, repeated | Friedman test | Nemenyi |

### Relationships

| Variables | Test | Output |
|-----------|------|--------|
| Two continuous | Pearson correlation | r, p-value |
| Two continuous (non-normal) | Spearman correlation | ρ, p-value |
| Continuous outcome, predictors | Linear regression | β, R², p-values |
| Binary outcome, predictors | Logistic regression | OR, p-values |
| Time-to-event | Cox proportional hazards | HR, p-values |

### RNA-seq / Differential Expression

| Comparison | Tool | Method |
|------------|------|--------|
| Two conditions | DESeq2 | Negative binomial GLM |
| Two conditions | edgeR | Negative binomial, exact test |
| Multiple conditions | DESeq2/edgeR | Likelihood ratio test |
| Complex designs | limma-voom | Linear models on transformed counts |
| Single-cell | Wilcoxon (Seurat) | Non-parametric per-gene |

</decision_framework>

<usage_patterns>
## When to Apply This Skill

1. **During analysis planning**: "What test should I use for comparing gene expression between treatment groups?"
2. **Code generation**: "Generate Python code for Mann-Whitney U test with effect size"
3. **Results interpretation**: "Is my p-value of 0.03 significant after testing 20,000 genes?"
4. **Manuscript writing**: "How do I report ANOVA results in a methods section?"
5. **Sample size planning**: "How many samples do I need to detect a 2-fold change in RNA-seq?"
6. **Reviewing statistics**: "Is the statistical approach in this paper appropriate?"

## Typical Workflow

```
1. Define research question → Identify comparison type
2. Assess data characteristics → Check normality, sample size
3. Select appropriate test → Use decision framework
4. Apply corrections → Multiple testing if needed
5. Calculate effect sizes → Biological relevance
6. Report results → Methods + Results sections
```

## Workflow Transitions

### Stage 1 → 2: Research Question → Data Assessment
**Exit criteria:**
□ Research question clearly stated as testable hypothesis
□ Comparison type identified (two groups, multiple groups, correlation, regression)
□ Primary outcome variable(s) defined
□ Grouping/predictor variables defined

### Stage 2 → 3: Data Assessment → Test Selection
**Exit criteria:**
□ Normality assessed (Shapiro-Wilk p > 0.05, or visual QQ-plot inspection)
□ Sample size documented (n per group)
□ Data type confirmed (continuous, categorical, ordinal, count)
□ Independence/pairing status determined
□ Outliers identified and handling decision documented

### Stage 3 → 4: Test Selection → Corrections
**Exit criteria:**
□ Test selected from decision framework with documented rationale
□ Test assumptions verified (e.g., homogeneity of variance for ANOVA)
□ Code implementation complete and validated on test data
□ Raw p-values computed for all comparisons

### Stage 4 → 5: Corrections → Effect Sizes
**Exit criteria:**
□ Number of tests documented
□ Correction method selected (BH-FDR for discovery, Bonferroni for confirmation)
□ Adjusted p-values computed
□ Significance threshold stated (e.g., FDR < 0.05)

### Stage 5 → 6: Effect Sizes → Reporting
**Exit criteria:**
□ Effect size metric selected (Cohen's d, fold change, R², OR, HR)
□ Effect sizes computed for all significant comparisons
□ Confidence intervals calculated where applicable
□ Biological relevance assessed (not just statistical significance)

### Stage 6 Complete: Reporting
**Exit criteria:**
□ Methods section includes: software, test name, justification, correction method
□ Results include: test statistic, degrees of freedom, p-value, effect size
□ Figures show data distribution (not just bar + error bars)
□ All comparisons reported (not just significant ones)
</usage_patterns>

<common_pitfalls>
## Statistical Errors to Avoid

### 1. Multiple Testing Without Correction
Testing 20,000 genes at α=0.05 yields ~1,000 false positives by chance alone.
- **Solution**: Apply Benjamini-Hochberg FDR correction; report adjusted p-values

### 2. Pseudoreplication
Treating technical replicates as biological replicates inflates sample size.
- **Solution**: Average technical replicates; use biological replicates for n

### 3. Normality Assumption Violations
Using t-test on count data, percentages, or highly skewed distributions.
- **Solution**: Test normality (Shapiro-Wilk); use non-parametric alternatives

### 4. P-value Misinterpretation
P < 0.05 does NOT mean 95% probability the hypothesis is true.
- **Solution**: Report effect sizes; use confidence intervals; avoid "trending"

### 5. Effect Size Neglect
Statistically significant ≠ biologically meaningful (especially with large n).
- **Solution**: Always report effect sizes (Cohen's d, fold change, R²)

### 6. Batch Effects
Confounding technical variation with biological signal.
- **Solution**: Include batch in model; use ComBat/Harmony for correction

### 7. Overfitting in High-Dimensional Data
More features than samples leads to spurious findings.
- **Solution**: Use regularization; validate on held-out data; report discovery vs validation

### 8. Inappropriate Correlation Interpretation
Correlation ≠ causation; outliers can drive spurious correlations.
- **Solution**: Visualize relationships; use robust methods; consider confounders

### 9. Cherry-Picking Results
Selective reporting of significant results inflates false discovery.
- **Solution**: Pre-register analyses; report all tests performed

### 10. Incorrect Use of Standard Error vs Standard Deviation
SE shows precision of mean estimate; SD shows data spread.
- **Solution**: Use SD for describing variability; SE for comparing means
</common_pitfalls>

<error_handling>
## Common Runtime Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: sample size too small` | n < 3 for normality tests | Skip normality test; use non-parametric method |
| `RuntimeWarning: divide by zero` | Zero variance in a group | Check for constant values; exclude or handle |
| `LinAlgError: singular matrix` | Multicollinearity in regression | Remove correlated predictors; use VIF > 10 threshold |
| All FDR-adjusted p-values = 1.0 | All raw p-values identical or very high | Verify test ran correctly; check data |
| `ConvergenceWarning` in logistic | Perfect separation or small sample | Add regularization; check sample size |
| NaN in effect size calculation | Zero denominator (e.g., pooled SD = 0) | Verify data variability; use alternative metric |

### Handling Missing Data

```python
# Check for missing values before analysis
if df.isnull().any().any():
    print(f"Missing values: {df.isnull().sum().sum()}")
    # Options: df.dropna(), df.fillna(method), or use imputation
```

### Assumption Verification Failures

When assumptions are violated, fall back to robust alternatives:
- Non-normality → Non-parametric tests (Mann-Whitney, Kruskal-Wallis)
- Heteroscedasticity → Welch's t-test, robust standard errors
- Non-independence → Mixed models or GEE
</error_handling>

<reporting_guidelines>
## How to Report Statistical Results

> **Reference:** See [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §10 (Statistical Reporting Completeness) for required elements by test type.

### Methods Section Template
```
Statistical analyses were performed using [Python 3.x with scipy/statsmodels | R 4.x].
[Test name] was used to compare [groups/conditions] because [justification based on
data characteristics]. Multiple testing correction was applied using the
Benjamini-Hochberg procedure with FDR < 0.05. Effect sizes are reported as
[Cohen's d | log2 fold change | Pearson's r]. Sample sizes were determined by
[power analysis | available data], with n = [X] per group providing [Y]% power
to detect [effect size] at α = 0.05.
```

### Results Reporting Format

**t-test**: "Gene expression was significantly higher in treatment vs control
(mean ± SD: 15.2 ± 3.1 vs 8.7 ± 2.4; t(18) = 5.23, p < 0.001, Cohen's d = 2.35)"

**ANOVA**: "Expression differed significantly across conditions (F(2, 27) = 12.4,
p < 0.001, η² = 0.48). Post-hoc Tukey tests revealed..."

**Correlation**: "Expression correlated positively with survival time
(Spearman's ρ = 0.68, p < 0.001, 95% CI [0.42, 0.84])"

**Chi-square**: "Mutation frequency differed by cancer type (χ²(3) = 15.7,
p = 0.001, Cramér's V = 0.31)"
</reporting_guidelines>

<references>
## Reference Documents

Detailed guidance available in `references/` subdirectory:

| Reference | Purpose | Size |
|-----------|---------|------|
| `test_decision_framework.md` | Detailed decision trees with code examples | 17KB |
| `python_scipy_patterns.md` | Complete scipy.stats API patterns | 31KB |
| `r_stats_patterns.md` | R base stats and specialized packages | 16KB |
| `multiple_testing_correction.md` | FDR, Bonferroni, permutation methods | 14KB |
| `normalization_methods.md` | RNA-seq normalization (TMM, DESeq2, limma-voom) | 17KB |
| `dimensionality_reduction.md` | PCA, t-SNE, UMAP theory and implementation | 24KB |
| `clustering_methods.md` | Hierarchical, k-means, graph-based methods | 27KB |
| `survival_analysis.md` | Kaplan-Meier, log-rank, Cox regression | 23KB |
| `power_sample_size.md` | Power analysis for omics studies | 21KB |
</references>

<visualization_guidance>
## Visualizing Statistical Results

Use **plotting-libraries** skill for creating figures. Match visualization to statistical context:

### Data Assessment Plots
| Purpose | Plot Type | When to Use |
|---------|-----------|-------------|
| Normality check | Q-Q plot, histogram | Before parametric tests |
| Variance homogeneity | Box plot by group | Before ANOVA/t-test |
| Outlier detection | Box plot, scatter | During data cleaning |
| Distribution shape | Violin plot, density | Choosing test type |

### Group Comparison Plots
| Test Type | Recommended Plots |
|-----------|-------------------|
| t-test, Mann-Whitney | Box plot + individual points, violin plot |
| ANOVA, Kruskal-Wallis | Grouped box plot, bar + error bars (with data points) |
| Paired tests | Before-after line plot, paired dot plot |
| Post-hoc comparisons | Box plot with significance brackets |

### Regression & Correlation Plots
| Analysis | Recommended Plots |
|----------|-------------------|
| Linear regression | Scatter + fit line, residual plot, Q-Q of residuals |
| Multiple regression | Partial regression plots, coefficient forest plot |
| Correlation matrix | Heatmap with values, corrplot |
| Logistic regression | ROC curve, calibration plot |

### High-Dimensional Data Plots
| Analysis | Recommended Plots |
|----------|-------------------|
| Differential expression | Volcano plot, MA plot |
| Clustering | Heatmap with dendrograms, silhouette plot |
| Dimensionality reduction | PCA/UMAP scatter, scree plot |
| Multiple testing | P-value histogram, adjusted vs raw p-values |

**Anti-patterns to avoid:**
- Bar plots without individual data points (hides distribution)
- Pie charts for comparing quantities
- 3D plots when 2D suffices
- Dynamite plots (bar + error bar only)
</visualization_guidance>

<cross_references>
## Related Skills

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

- **peer-review**: Manuscript evaluation and critical analysis frameworks (evidence evaluation, bias detection, logical fallacies)
- **plotting-libraries**: Visualizing statistical results—see `<visualization_guidance>` above for test-specific plot recommendations
- **scientific-writing**: Reporting statistical methods and results in manuscripts
- **reproducible-research**: Documenting analysis parameters for reproducibility
- **research-lookup**: Finding appropriate statistical methods in literature
</cross_references>
