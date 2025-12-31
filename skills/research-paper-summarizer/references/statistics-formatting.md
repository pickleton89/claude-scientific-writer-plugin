# Statistics Formatting Guide

> Standardized formatting for statistical values in summaries

## Core Formatting Rules

### P-Values

| Format | When to Use | Example |
|--------|-------------|---------|
| `p = X.XXX` | Exact value available | `p = 0.003` |
| `p < 0.001` | Very small p-values | `p < 0.001` |
| `p = 0.05` | Borderline significance | `p = 0.05` |
| `p = 0.XX` | Two decimal places for larger values | `p = 0.34` |

**Never:**
- Replace exact values with thresholds: ❌ `p < 0.05` when you know `p = 0.003`
- Round arbitrarily: ❌ `p = 0.00` instead of `p < 0.001`
- Use "significant" without the value: ❌ "statistically significant"

### Confidence Intervals

```
Standard format: 95% CI: X.X–Y.Y

Examples:
- 95% CI: 1.2–3.4
- 95% CI: 0.45–0.89
- 99% CI: 2.1–5.8 (specify if not 95%)
```

**Typography:**
- Use en-dash (–) not hyphen (-) between values
- Include the CI level (95%, 99%)
- No spaces around the dash

### Sample Sizes

| Context | Format | Example |
|---------|--------|---------|
| Per-group | `n = X/group` | `n = 24/group` |
| Total | `N = XXX total` | `N = 156 total` |
| Unequal groups | `n = X vs Y` | `n = 24 vs 18` |
| Multiple experiments | `n = X–Y` | `n = 8–12 per experiment` |

### Effect Sizes

| Measure | Format | Example |
|---------|--------|---------|
| Cohen's d | `Cohen's d = X.XX` | `Cohen's d = 0.85` |
| Hazard ratio | `HR = X.XX` | `HR = 0.45` |
| Odds ratio | `OR = X.X` | `OR = 2.3` |
| Fold change | `X.X-fold` + direction | `2.3-fold increase` |
| Percent change | `XX%` + direction | `45% reduction` |

### Fold Changes

**Always include direction:**
```
✅ 2.3-fold increase
✅ 0.4-fold decrease (or 60% reduction)
❌ 2.3-fold change (ambiguous)
```

### Concentrations and Doses

```
In vitro:   1 mM, 10 µM, 100 nM
In vivo:    5 mg/kg, 10 mg/kg/day
Time:       24h, 48 hours, 4 weeks
```

## Composite Statistics Formatting

### Complete Finding Format

```markdown
**Finding:** [Description] ([effect size], [p-value], [sample size])

Example:
**DFMO treatment reduced polyamine levels** (78% reduction, p < 0.001, n=6/group)
```

### Results Table Format

```markdown
| Condition | Effect | p-value | n |
|-----------|--------|---------|---|
| Treatment A | 2.3-fold increase | p = 0.003 | 24 |
| Treatment B | 45% reduction | p < 0.001 | 24 |
| Control | baseline | - | 24 |
```

### Statistical Summary Section

```markdown
| Metric | Value |
|--------|-------|
| Sample sizes | n = 8–12/group (in vitro), n = 10/group (in vivo) |
| Effect sizes | 45–95% reduction in target; Cohen's d = 0.8–1.2 |
| P-values | Range: p < 0.001 to p = 0.04; 12/14 comparisons significant |
| Tests used | Two-tailed t-test (pairwise), ANOVA with Tukey's (multiple) |
| Correction | Benjamini-Hochberg FDR < 0.05 |
```

## Special Cases

### Non-Significant Results

Always report with context:
```
❌ "No effect observed"
✅ "No significant effect (p = 0.34, n = 12/group)"
✅ "Effect not significant after multiple testing correction (unadjusted p = 0.04, adjusted p = 0.12)"
```

### Multiple Testing

Note correction method and thresholds:
```
- FDR < 0.05 (Benjamini-Hochberg)
- Bonferroni-corrected p < 0.0025 (20 comparisons)
- q-value < 0.1
```

### Missing Statistics

Flag explicitly:
```
- Effect size not reported
- Sample size not stated for this experiment
- Statistical test not specified
- P-value threshold stated as "p < 0.05" (exact value not provided)
```

## Typography Reference

| Character | Name | Use |
|-----------|------|-----|
| – | En-dash | Ranges: 95% CI: 1.2–3.4 |
| − | Minus | Negative: −0.5 |
| × | Multiplication | Dilution: 10× |
| ± | Plus-minus | Mean ± SD: 45.2 ± 3.1 |
| ≤ | Less than or equal | p ≤ 0.05 |
| ≥ | Greater than or equal | n ≥ 10 |
| µ | Micro | 10 µM |
