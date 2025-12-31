# Quantification Thresholds

> Shared numeric standards for scientific writing quality assessment
> Version: 1.0.0
> Last Updated: 2025-12-30

This document provides measurable thresholds referenced by multiple skills. Using shared definitions ensures consistency across the skill library.

**Referencing Convention:** Skills reference sections as `QUANTIFICATION_THRESHOLDS.md §N` (e.g., §1 for Literature Coverage).

---

## Table of Contents

1. [Literature Coverage](#1-literature-coverage)
2. [Visual Quality](#2-visual-quality)
3. [Replication & Sample Size](#3-replication--sample-size)
4. [Issue Severity Classification](#4-issue-severity-classification)
5. [Documentation Completeness](#5-documentation-completeness)
6. [Time-Based Thresholds](#6-time-based-thresholds)
7. [Quality Scoring Rubrics](#7-quality-scoring-rubrics)
8. [Iteration & Stopping Criteria](#8-iteration--stopping-criteria)
9. [Figure & Plot Quality](#9-figure--plot-quality)
10. [Statistical Reporting Completeness](#10-statistical-reporting-completeness)

---

## §1 Literature Coverage

**Referenced by:** `literature-review`, `hypothesis-generation`, `scientific-writing`

### Coverage by Document Type

| Document Type | Min Papers | Min Databases | Time Range | Citation Density |
|---------------|------------|---------------|------------|------------------|
| Original Research | 30 | 2 | 5-10 years | 2-4 per paragraph |
| Review Article | 100 | 4 | 10+ years | 4-6 per paragraph |
| Systematic Review | 50+ | 3 | Per PRISMA | All relevant |
| Meta-Analysis | 10+ studies | 3 | 10+ years | All included |
| Methods Paper | 20 | 2 | 5 years | Key comparisons |
| Commentary/Letter | 10-15 | 1 | 2-3 years | Selective |

### Search Requirements

| Requirement | Minimum | Target | Excellent |
|-------------|---------|--------|-----------|
| Databases searched | 3 | 4-5 | 5+ |
| Total papers retrieved | 40 | 70+ | 100+ |
| Recent papers (≤5 years) | 60% | 75% | 85% |
| Search saturation | <5% new | <2% new | <1% new |

### Comprehensive Search Checklist

A literature search is **comprehensive** when ALL criteria are met:
- [ ] ≥3 databases searched with documented strategy
- [ ] Forward/backward citation search performed
- [ ] Gray literature checked (preprints, theses, conference proceedings)
- [ ] ≤5% new relevant papers found in final search iteration
- [ ] Date range explicitly specified and justified

---

## §2 Visual Quality

**Referenced by:** `visual-design`, `peer-review`, `generate-image`, `plotting-libraries`

### Resolution Standards

| Output Type | Minimum | Target | Excellent |
|-------------|---------|--------|-----------|
| Web/screen | 72 DPI | 150 DPI | 300 DPI |
| Print (draft) | 150 DPI | 300 DPI | 600 DPI |
| Print (publication) | 300 DPI | 600 DPI | 1200 DPI |

### Typography Standards

| Element | Minimum | Target | Excellent |
|---------|---------|--------|-----------|
| Axis labels | 7pt | 8pt | 10pt |
| Tick labels | 6pt | 7pt | 8pt |
| Legend text | 7pt | 8pt | 9pt |
| Figure title | 9pt | 10pt | 12pt |
| Annotations | 6pt | 7pt | 8pt |

### Contrast and Accessibility

| Criterion | Minimum | Target | Excellent |
|-----------|---------|--------|-----------|
| Contrast ratio (text) | 4.5:1 | 7:1 | 10:1 |
| Contrast ratio (graphics) | 3:1 | 4.5:1 | 7:1 |
| Line weight | 0.5pt | 1.0pt | 1.5pt |
| Colorblind-safe | Deuteranopia | +Protanopia | +Tritanopia |

### Color Palette Limits

| Context | Maximum Colors | Recommended |
|---------|----------------|-------------|
| Single figure | 8 | 4-6 |
| Line plot | 6 | 3-4 |
| Bar chart categories | 12 | 6-8 |
| Heatmap continuous | 9 steps | 5-7 steps |

---

## §3 Replication & Sample Size

**Referenced by:** `peer-review`, `hypothesis-generation`, `statistical-analysis`

### Minimum Replication by Experiment Type

| Experiment Type | Biological Reps | Technical Reps | Target Power |
|-----------------|-----------------|----------------|--------------|
| Cell culture (in vitro) | ≥3 | ≥3 | 80% |
| Primary cells | ≥3-5 | ≥2-3 | 80% |
| Mouse studies | ≥6-10 | — | 80% |
| Large animal studies | ≥4-6 | — | 80% |
| Human observational | Per power calc | 1 | 80% |
| Clinical trials | Per power calc | 1 | 80-90% |

### Sample Size Red Flags

| Indicator | Severity | Action |
|-----------|----------|--------|
| n < 3 per group | Critical | Cannot perform valid statistics |
| n = 3-5 per group (no justification) | Major | Request justification or increase |
| No power calculation | Major | Request prospective justification |
| Post-hoc power analysis | Critical | Invalid—flag as major concern |
| Underpowered (<60%) | Major | Results unreliable, effect size inflated |
| Overpowered (>99%) | Minor | Wasteful, consider ethical implications |

### Power Analysis Requirements

| Study Phase | Required Power | Acceptable Alpha |
|-------------|----------------|------------------|
| Pilot/exploratory | 60-70% | 0.10 |
| Confirmatory | 80% | 0.05 |
| Regulatory/clinical | 80-90% | 0.05 or lower |
| Non-inferiority | 80-90% | One-sided 0.025 |

---

## §4 Issue Severity Classification

**Referenced by:** `peer-review`, `scholar-evaluation`

### Severity Criteria

| Severity | Definition | Triggers (any one) | Recommendation |
|----------|------------|-------------------|----------------|
| **Critical** | Invalidates conclusions | Data cannot be verified; wrong statistical test invalidating results; missing data >30% without sensitivity analysis; conclusions contradicted by data; missing ethics approval | Reject |
| **Major** | Significantly affects interpretation | Key control missing from ≥50% of experiments; sample size <80% of power requirement; methods insufficient for replication; statistical assumptions violated; ≥20% of stated outcomes missing | Major revision |
| **Minor** | Affects clarity/completeness | Grammar/spelling errors (>5/page); figure quality below standards; reference formatting inconsistent; acronyms undefined; minor methods gaps | Minor revision |
| **Optional** | Suggestions only | Style preferences; additional analyses that would strengthen; alternative visualizations | Author discretion |

### Issue Count Thresholds

| Issue Type | Acceptable | Needs Revision | Likely Rejection |
|------------|------------|----------------|------------------|
| Critical issues | 0 | 1 | ≥2 |
| Major issues | 0-2 | 3-5 | ≥6 |
| Minor issues | 0-10 | 11-20 | ≥21 |

---

## §5 Documentation Completeness

**Referenced by:** `reproducible-research`, `code-documentation`

### Reproducibility Scoring

| Level | Description | Checklist Score | Environment Spec |
|-------|-------------|-----------------|------------------|
| 0 | Not reproducible | <25% | None |
| 1 | Minimal | 25-49% | requirements.txt with `>=` versions |
| 2 | Standard | 50-74% | environment.yml with pinned versions |
| 3 | Complete | 75-89% | Docker/Singularity container |
| 4 | Exemplary | 90-100% | Container + CI tests + archived DOI |

### Code Documentation Metrics

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Docstring coverage | 60% | 80% | 95% |
| README completeness | Installation only | +Usage | +Examples +API |
| Inline comment density | 5% of lines | 10% | 15% |
| Type hint coverage | 0% | 50% | 90% |

### Data Availability Checklist

- [ ] Raw data deposited in appropriate repository
- [ ] Accession numbers provided
- [ ] Data dictionary/codebook included
- [ ] Processing scripts available
- [ ] Intermediate data available or reproducible

---

## §6 Time-Based Thresholds

**Referenced by:** `literature-review`, `research-lookup`

### Literature Recency Definitions

| Field Type | "Recent" | "Current" | "Foundational" |
|------------|----------|-----------|----------------|
| Fast-moving (ML, genomics) | ≤2 years | ≤6 months | Any age if seminal |
| Standard biomedical | ≤5 years | ≤1 year | ≤15 years |
| Clinical guidelines | ≤3 years | ≤1 year | N/A |
| Historical context | ≤10 years | ≤5 years | Any age |
| Methods/techniques | ≤5 years | ≤2 years | Original description |

### Update Frequency Requirements

| Document Type | Review Cycle | Obsolescence Risk |
|---------------|--------------|-------------------|
| Systematic review | 2 years | High after 3 years |
| Clinical guideline | 3 years | High after 5 years |
| Methods paper | 5 years | Medium after 10 years |
| Review article | 3-5 years | Medium after 7 years |

---

## §7 Quality Scoring Rubrics

**Referenced by:** `scientific-writing`, `scientific-schematics`, `peer-review`, `generate-image`

### §7.1 Writing Quality Rubric

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Sentence length (average) | ≤25 words | 15-20 words | 12-18 words |
| Paragraph length | ≤200 words | 100-150 words | 80-120 words |
| Passive voice usage | ≤40% | ≤25% | ≤15% |
| Acronyms per page | ≤8 | ≤5 | ≤3 |
| Grammar errors per page | ≤3 | ≤1 | 0 |
| Readability (Flesch-Kincaid) | Grade 12-16 | Grade 10-14 | Grade 8-12 |

### §7.2 Figure Quality Rubric

| Criterion | Minimum | Target | Excellent |
|-----------|---------|--------|-----------|
| Resolution | 150 DPI | 300 DPI | 600 DPI |
| Font size (labels) | ≥7pt | ≥8pt | ≥10pt |
| Contrast ratio | 4.5:1 | 7:1 | 10:1 |
| Line weight | ≥0.5pt | ≥1.0pt | ≥1.5pt |
| Error bars present | When applicable | With n stated | With CI type |
| Legend completeness | Variables listed | +Units | +Statistics |

### §7.3 Schematic Quality Rubric (10 points)

| Dimension | Points | 0 (Fail) | 1 (Acceptable) | 2 (Excellent) |
|-----------|--------|----------|----------------|---------------|
| Scientific Accuracy | 0-2 | Factual errors | Minor issues | Scientifically accurate |
| Clarity & Readability | 0-2 | Confusing layout | Understandable | Intuitive flow |
| Label Quality | 0-2 | Missing/unreadable | Present but issues | Clear, consistent |
| Layout & Composition | 0-2 | Overlaps/cramped | Reasonable spacing | Balanced, logical |
| Professional Appearance | 0-2 | Amateur look | Acceptable | Publication-ready |

**Score Interpretation:**
- 0-4: Needs revision (below all thresholds)
- 5-6: Acceptable for presentations/posters
- 7-8: Acceptable for preprints/reports
- 9-10: Publication-ready (journal quality)

---

## §8 Iteration & Stopping Criteria

**Referenced by:** `scientific-schematics`, `generate-image`

### Quality Thresholds by Document Type

| Document Type | Min Score | Soft Limit | Hard Limit |
|---------------|-----------|------------|------------|
| journal | 8.5/10 | 3 iterations | 5 iterations |
| conference | 8.0/10 | 3 | 5 |
| thesis | 8.0/10 | 3 | 5 |
| grant | 8.0/10 | 3 | 5 |
| preprint | 7.5/10 | 2 | 4 |
| report | 7.5/10 | 2 | 4 |
| poster | 7.0/10 | 2 | 3 |
| presentation | 6.5/10 | 2 | 3 |
| default | 7.5/10 | 3 | 5 |

### Iteration Behavior

- **Soft limit:** Target iterations; stop if quality ≥ threshold OR soft limit reached
- **Hard limit:** Absolute maximum; never exceed regardless of quality score
- **Early stop:** If quality ≥ threshold before soft limit, iteration is successful

### Diminishing Returns Indicators

Stop iteration when:
- Quality improvement <0.5 points between iterations
- Same issues flagged ≥2 consecutive iterations
- Score oscillates (improves then regresses)

---

## §9 Figure & Plot Quality

**Referenced by:** `plotting-libraries`, `visual-design`

### Code Quality Standards

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Figure size explicit | Width only | Width + height | +DPI |
| Colors from named palette | Yes | Colorblind-safe | +Perceptually uniform |
| Axis labels present | Yes | +Units | +Symbol definitions |
| Font sizes explicit | Some | All | Hierarchical (title > label > tick) |
| Reproducibility | Hardcoded values | Parameters | Config file/function |

### Statistical Visualization Requirements

| Plot Type | Required Elements | Optional Enhancements |
|-----------|-------------------|----------------------|
| Box plot | Median, quartiles, whiskers | Individual points, outlier labels |
| Bar chart | Error bars (SE or CI), n | Individual data points, significance |
| Scatter plot | Trend line (if appropriate) | Confidence band, R² annotation |
| Violin plot | Median indicator | Quartile lines, individual points |
| Forest plot | Effect size, CI | Heterogeneity stats, weight |

### Plot Type Selection by Data

| Data Characteristics | Recommended Plot | Avoid |
|---------------------|------------------|-------|
| Distribution (1 group) | Histogram, density, violin | Pie chart |
| Distribution (2+ groups) | Box plot, violin, ridgeline | Grouped bar |
| Correlation (2 continuous) | Scatter with trend | Dual y-axis |
| Comparison (categories) | Bar chart with error bars | 3D bar |
| Time series | Line plot | Area chart (unless stacked) |
| Proportions | Stacked bar, waffle | Pie chart (>5 categories) |

### Publication-Ready Checklist

- [ ] Figure dimensions match journal requirements
- [ ] Resolution ≥300 DPI for print
- [ ] Font sizes readable after scaling (≥7pt final)
- [ ] Color palette is colorblind-safe
- [ ] All axes labeled with units
- [ ] Legend complete and positioned appropriately
- [ ] No chart junk (unnecessary gridlines, borders, 3D effects)
- [ ] Data-ink ratio optimized

---

## §10 Statistical Reporting Completeness

**Referenced by:** `statistical-analysis`, `scientific-writing`, `peer-review`

### Test Reporting Requirements

| Element | Required | Recommended | Excellent |
|---------|----------|-------------|-----------|
| Test name | Yes | Yes | Yes |
| Test statistic | Yes | Yes | Yes |
| Degrees of freedom | Yes | Yes | Yes |
| P-value | Yes (exact or <0.001) | 3 significant figures | Confidence interval |
| Effect size | Yes | With interpretation | With CI |
| Sample size | Yes | Per group | With exclusions noted |

### Reporting by Test Type

| Test | Report Format |
|------|---------------|
| t-test | t(df) = X.XX, p = .XXX, d = X.XX |
| ANOVA | F(df1, df2) = X.XX, p = .XXX, η² = X.XX |
| Chi-square | χ²(df) = X.XX, p = .XXX, Cramér's V = X.XX |
| Correlation | r(df) = X.XX, p = .XXX, 95% CI [X.XX, X.XX] |
| Regression | β = X.XX, SE = X.XX, t = X.XX, p = .XXX |
| Mann-Whitney | U = XXX, p = .XXX, r = X.XX |
| Wilcoxon | W = XXX, p = .XXX, r = X.XX |

### Multiple Testing Correction

| Scenario | Method | Threshold Adjustment |
|----------|--------|---------------------|
| ≤3 planned comparisons | None required | α = 0.05 |
| 4-10 comparisons | Bonferroni or Holm | α/n or sequential |
| >10 comparisons | FDR (Benjamini-Hochberg) | q < 0.05 |
| Genome-wide | Bonferroni or permutation | α = 5×10⁻⁸ or empirical |
| Exploratory analysis | Report as exploratory | No correction, note limitation |

### Assumption Verification Checklist

| Test Family | Assumptions to Verify | How to Report |
|-------------|----------------------|---------------|
| Parametric | Normality, homoscedasticity, independence | Test + visual |
| Non-parametric | Independence, ordinal scale | State rationale |
| Linear models | Linearity, normality of residuals, homoscedasticity | Diagnostic plots |
| Generalized linear | Link function appropriate, dispersion | Goodness-of-fit |

### Missing Data Reporting

| Missing Rate | Required Action | Reporting |
|--------------|-----------------|-----------|
| <5% | Complete case acceptable | State n with missingness |
| 5-20% | Sensitivity analysis recommended | Compare complete vs. imputed |
| >20% | Multiple imputation required | Full missing data analysis |
| Non-random | Pattern analysis required | Investigate mechanism (MCAR/MAR/MNAR) |

---

## Changelog

### v1.0.0 (2025-12-30)
- Initial creation consolidating thresholds from across skill library
- §1-§8: Consolidated existing thresholds from skills
- §9: New section for plotting-libraries quality metrics
- §10: New section for statistical-analysis reporting completeness

---

*This document supports deterministic, consistent quality assessment across the scientific writing skill library.*
