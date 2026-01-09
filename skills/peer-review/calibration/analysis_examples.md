# Analysis Scoring Calibration

> Reference examples for consistent analysis/statistical methods scoring (1-5 scale).
> Weight: 15% of overall score.

---

## Score 5 Example (Excellent)

**Excerpt:**
> "Data were tested for normality using Shapiro-Wilk test and homogeneity of variance using Levene's test before parametric analysis. Continuous outcomes were analyzed using mixed-effects ANOVA with treatment as fixed effect and batch as random effect, accounting for the nested structure of technical replicates within biological samples. Post-hoc comparisons used Tukey's HSD with Bonferroni correction for 6 pairwise comparisons (adjusted α = 0.0083). Effect sizes are reported as Cohen's d with 95% bootstrap confidence intervals (10,000 iterations). Missing data (<5% per variable) were handled using multiple imputation (m=20) under MAR assumption, with sensitivity analysis confirming robustness. All analyses were pre-registered (OSF: xxxx) and performed in R 4.3.1 using lme4 and emmeans packages."

**Why Score 5:**
- Assumption testing documented
- Appropriate model for data structure
- Multiple comparison correction justified
- Effect sizes with CIs
- Missing data handling explicit
- Pre-registration mentioned
- Software versions provided

**Key Indicators:**
- ✓ Assumptions verified
- ✓ Model matches design
- ✓ Multiple testing addressed
- ✓ Effect sizes with CIs
- ✓ Missing data strategy
- ✓ Pre-registration

---

## Score 4 Example (Good)

**Excerpt:**
> "Normality was assessed using Shapiro-Wilk test. Groups were compared using one-way ANOVA with Tukey's post-hoc test for multiple comparisons. Effect sizes (Cohen's d) are reported. Statistical significance was set at p < 0.05. Analyses were performed in GraphPad Prism 9."

**Why Score 4:**
- Assumption testing mentioned
- Appropriate test selection
- Post-hoc correction applied
- Effect sizes included
- Software specified
- Missing: CIs, missing data handling

**Key Indicators:**
- ✓ Assumptions checked
- ✓ Multiple testing addressed
- ✓ Effect sizes reported
- ○ No confidence intervals
- ○ Missing data not addressed

---

## Score 3 Example (Adequate)

**Excerpt:**
> "Data were analyzed using ANOVA with post-hoc t-tests. P < 0.05 was considered significant. Statistical analysis was performed using SPSS."

**Why Score 3:**
- General approach stated
- Post-hoc mentioned but not specified
- No multiple testing correction explicit
- No assumption verification
- Software mentioned
- Functional but incomplete

**Key Indicators:**
- ○ Basic approach named
- ○ Post-hoc unclear
- ○ No assumptions mentioned
- ○ No effect sizes
- ○ Software only

---

## Score 2 Example (Needs Work)

**Excerpt:**
> "Statistical analysis was performed. Significant differences were determined."

**Why Score 2:**
- No specific tests named
- No threshold defined
- "Significant" is meaningless here
- Cannot evaluate appropriateness
- Major revision needed

**Key Indicators:**
- ✗ No tests specified
- ✗ No alpha level
- ✗ No software
- ✗ Cannot reproduce

---

## Score 1 Example (Poor)

**Excerpt:**
> "Data were analyzed appropriately."

**Why Score 1:**
- No information provided
- Cannot evaluate anything
- Complete rewrite required

**Key Indicators:**
- ✗ Zero detail
- ✗ Not reproducible
- ✗ Not evaluable

---

## Statistical Method Selection Guide

Use this to verify appropriate test selection:

| Data Structure | Groups | Distribution | Recommended Test |
|---------------|--------|--------------|------------------|
| Continuous | 2, independent | Normal | Independent t-test |
| Continuous | 2, independent | Non-normal | Mann-Whitney U |
| Continuous | 2, paired | Normal | Paired t-test |
| Continuous | 2, paired | Non-normal | Wilcoxon signed-rank |
| Continuous | 3+, independent | Normal | One-way ANOVA |
| Continuous | 3+, independent | Non-normal | Kruskal-Wallis |
| Continuous | 3+, repeated | Normal | Repeated measures ANOVA |
| Continuous | Nested design | Normal | Mixed-effects model |
| Categorical | 2×2 | — | Chi-square / Fisher's exact |
| Time-to-event | — | — | Log-rank / Cox regression |

---

## Common Scoring Pitfalls

1. **Ignoring data structure:** Using independent tests for paired data is a critical error (cap at Score 2).

2. **Missing multiple testing:** Multiple pairwise comparisons without correction caps at Score 3.

3. **Over-crediting software mention:** Naming software without methods detail is Score 2-3.

4. **Ignoring violated assumptions:** Parametric tests with small samples (n<30) and untested normality caps at Score 3.
