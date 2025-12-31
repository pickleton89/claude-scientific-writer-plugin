# Multiple Testing Correction

> Essential guide for controlling false discoveries in high-dimensional data analysis.
> Critical for RNA-seq, proteomics, GWAS, and any analysis testing thousands of hypotheses.

---

## Why Correction Is Necessary

### The Multiple Testing Problem

When performing a single statistical test at α = 0.05, you accept a 5% chance of a false positive. But when testing thousands of hypotheses simultaneously, false positives accumulate dramatically.

**Example: RNA-seq Analysis**
- Testing 20,000 genes at α = 0.05
- Expected false positives: 20,000 × 0.05 = **1,000 genes**
- Even with no true biological signal, you'd report ~1,000 "significant" genes

### Error Rate Definitions

| Error Rate | Definition | Controls |
|------------|------------|----------|
| **FWER** (Family-Wise Error Rate) | P(at least one false positive) | Very conservative |
| **FDR** (False Discovery Rate) | Expected proportion of false positives among rejections | Standard for genomics |
| **FWER** | P(V ≥ 1) where V = false positives | Bonferroni, Holm |
| **FDR** | E[V/R] where R = total rejections | BH, q-value |

### When to Use Which

| Scenario | Recommended | Rationale |
|----------|-------------|-----------|
| Candidate gene validation | FWER (Bonferroni) | Few tests, each must be reliable |
| Genome-wide discovery | FDR (BH) | Many tests, some false positives acceptable |
| Clinical biomarkers | FWER or stringent FDR | False positives have real consequences |
| Exploratory analysis | FDR | Generating hypotheses for validation |

---

## Bonferroni Correction

### Method

Divide the significance threshold by the number of tests:

```
α_adjusted = α / n

where:
  α = desired family-wise error rate (typically 0.05)
  n = number of tests
```

### Example

Testing 100 genes at FWER = 0.05:
- Bonferroni threshold: 0.05 / 100 = 0.0005
- Only p-values < 0.0005 are significant

### When Bonferroni Is Appropriate

- Small number of pre-specified tests (< 20)
- Each test must be independently reliable
- Confirmatory studies (not exploratory)
- Clinical or regulatory contexts

### Why Bonferroni Is Too Conservative for Omics

1. **Assumes independence**: Tests on correlated genes/proteins are not independent
2. **Loses power**: At 20,000 tests, threshold becomes 2.5 × 10⁻⁶
3. **Misses biology**: Real biological effects with moderate p-values are rejected
4. **Not designed for discovery**: Created for few, independent tests

### Code

**Python:**
```python
from statsmodels.stats.multitest import multipletests

# Raw p-values from your tests
pvalues = [0.001, 0.01, 0.02, 0.04, 0.05, 0.10, 0.50]

# Bonferroni correction
rejected, pvals_corrected, _, _ = multipletests(pvalues, method='bonferroni')

print("Bonferroni-corrected p-values:", pvals_corrected)
print("Significant (α=0.05):", rejected)
```

**R:**
```r
pvalues <- c(0.001, 0.01, 0.02, 0.04, 0.05, 0.10, 0.50)

# Bonferroni correction
p_adjusted <- p.adjust(pvalues, method = "bonferroni")

print(p_adjusted)
# Significant at α = 0.05
significant <- p_adjusted < 0.05
```

---

## Benjamini-Hochberg FDR

### The Standard for Genomics

The Benjamini-Hochberg (BH) procedure controls the **False Discovery Rate** — the expected proportion of false positives among all discoveries.

**Key insight**: If FDR = 0.05 and you call 500 genes significant, you expect ~25 to be false positives. This is often acceptable for discovery.

### Algorithm

1. Rank p-values from smallest to largest: p₁ ≤ p₂ ≤ ... ≤ pₙ
2. Find the largest k where: p_k ≤ (k/n) × α
3. Reject all hypotheses with p-value ≤ p_k

### Adjusted P-Values (FDR q-values)

The BH-adjusted p-value for test i is:
```
p_adj[i] = min(p[i] × n/rank[i], 1)
```

Then enforce monotonicity (adjusted p-values can only increase with rank).

### Visual Intuition

```
P-value vs. BH Threshold

p-value
  |
  |    * * * *           <- p-values above line: not significant
  |   *
  |  *    -------- BH line (slope = α/n)
  | *   /
  |*  /                  <- p-values below line: significant
  |*/
  +-------------------- rank
```

### Assumptions

- **Independence or positive dependence**: Tests can be correlated if the correlation is positive (common in gene expression)
- **BY procedure**: Use Benjamini-Yekutieli for arbitrary dependence (more conservative)

### Code

**Python:**
```python
from statsmodels.stats.multitest import multipletests
import numpy as np

# Simulated p-values (e.g., from differential expression)
np.random.seed(42)
pvalues = np.concatenate([
    np.random.uniform(0, 0.01, 50),   # 50 "true" effects
    np.random.uniform(0, 1, 950)       # 950 null effects
])

# Benjamini-Hochberg correction
rejected, padj, _, _ = multipletests(pvalues, method='fdr_bh')

print(f"Total tests: {len(pvalues)}")
print(f"Discoveries (FDR < 0.05): {sum(rejected)}")
print(f"Expected false discoveries: {sum(rejected) * 0.05:.1f}")
```

**R:**
```r
# Simulated p-values
set.seed(42)
pvalues <- c(
  runif(50, 0, 0.01),   # 50 "true" effects
  runif(950, 0, 1)       # 950 null effects
)

# Benjamini-Hochberg correction
padj <- p.adjust(pvalues, method = "BH")

# Results
sum(padj < 0.05)  # Number of discoveries
```

**DESeq2 (RNA-seq):**
```r
library(DESeq2)

# DESeq2 automatically applies BH correction
dds <- DESeq(dds)
res <- results(dds)  # padj column is BH-adjusted

# Filter significant genes
sig_genes <- subset(res, padj < 0.05 & abs(log2FoldChange) > 1)
```

**edgeR (RNA-seq):**
```r
library(edgeR)

# After fitting model
et <- exactTest(y, pair = c("Control", "Treatment"))
top_tags <- topTags(et, n = Inf)  # FDR column is BH-adjusted

# Filter significant
sig_genes <- top_tags$table[top_tags$table$FDR < 0.05, ]
```

---

## Q-Value and Local FDR

### Q-Value (Storey's Method)

The q-value is a more powerful alternative to BH that estimates the proportion of true null hypotheses (π₀).

**Intuition**: If 80% of genes are truly null (π₀ = 0.8), we can be less conservative because most tests have no effect.

### Q-Value vs. BH Adjusted P-Value

| Aspect | BH Adjusted P-Value | Q-Value |
|--------|---------------------|---------|
| Assumes π₀ | 1.0 (all null) | Estimated from data |
| Power | Lower | Higher |
| Conservative | More | Less |
| Use case | General | Large-scale genomics |

### Code

**R (qvalue package):**
```r
# Install if needed: BiocManager::install("qvalue")
library(qvalue)

# Calculate q-values
qobj <- qvalue(pvalues)

# Results
summary(qobj)
# pi0: estimated proportion of true nulls

# Q-values
qvalues <- qobj$qvalues

# Significant at FDR 0.05
sig_genes <- which(qvalues < 0.05)

# Plot diagnostics
plot(qobj)
```

**Python (not standard, use BH instead):**
```python
# Q-value estimation is less common in Python
# For most purposes, use BH from statsmodels:
from statsmodels.stats.multitest import multipletests

rejected, padj, _, _ = multipletests(pvalues, method='fdr_bh')
```

### Local FDR (lfdr)

The **local FDR** gives the probability that a specific test is a false positive, rather than controlling the overall rate.

```r
library(qvalue)

qobj <- qvalue(pvalues)
lfdr <- qobj$lfdr  # Local FDR for each test

# Genes with lfdr < 0.05 have <5% chance of being false positives
high_confidence <- which(lfdr < 0.05)
```

---

## Other Correction Methods

### Holm's Step-Down (FWER)

Less conservative than Bonferroni while still controlling FWER.

**Algorithm:**
1. Order p-values: p₁ ≤ p₂ ≤ ... ≤ pₙ
2. Compare p_k to α/(n-k+1)
3. Reject until first non-rejection

```python
# Python
rejected, padj, _, _ = multipletests(pvalues, method='holm')
```

```r
# R
padj <- p.adjust(pvalues, method = "holm")
```

### Hochberg's Step-Up (FWER)

Similar to Holm but slightly more powerful (requires independence).

```python
rejected, padj, _, _ = multipletests(pvalues, method='hochberg')
```

```r
padj <- p.adjust(pvalues, method = "hochberg")
```

### Benjamini-Yekutieli (FDR under arbitrary dependence)

Use when tests have complex correlation structures.

```python
rejected, padj, _, _ = multipletests(pvalues, method='fdr_by')
```

```r
padj <- p.adjust(pvalues, method = "BY")
```

### Comparison Table

| Method | Controls | Power | Assumptions |
|--------|----------|-------|-------------|
| Bonferroni | FWER | Lowest | None |
| Holm | FWER | Low | None |
| Hochberg | FWER | Low-Medium | Independence |
| BH | FDR | Medium-High | Independence or positive dependence |
| BY | FDR | Medium | None (arbitrary dependence) |
| Q-value | FDR | Highest | Independence or positive dependence |

---

## Permutation-Based Approaches

### When to Use Permutation Tests

- Distributional assumptions violated
- Complex test statistics
- Need to account for correlation structure
- Small sample sizes where asymptotic approximations fail

### Permutation FDR

**Concept**: Estimate the null distribution empirically by permuting sample labels.

**Algorithm:**
1. Calculate test statistics for real data
2. Permute labels many times (e.g., 1000)
3. Calculate test statistics for each permutation
4. Compare real statistics to permutation distribution

### Code: SAM (Significance Analysis of Microarrays)

**R:**
```r
library(samr)

# Data format: genes × samples
# y: class labels (1 or 2)
samfit <- SAM(x = expression_matrix,
              y = class_labels,
              resp.type = "Two class unpaired",
              nperms = 1000)

# Results with FDR control
siggenes <- samr.compute.siggenes.table(samfit, del = 0.5)
```

### Code: Permutation-Based Gene Set Analysis

**R (fgsea):**
```r
library(fgsea)

# Gene-level statistics (e.g., log2FC or t-statistic)
stats <- setNames(res$log2FoldChange, rownames(res))

# Pathways (list of gene sets)
pathways <- gmtPathways("h.all.v7.5.symbols.gmt")

# GSEA with permutation-based FDR
fgsea_res <- fgsea(pathways = pathways,
                   stats = stats,
                   nperm = 10000)

# Significant pathways
sig_pathways <- fgsea_res[padj < 0.05]
```

### MaxT/MinP Permutation (Westfall-Young)

Controls FWER accounting for correlation.

**R:**
```r
library(multtest)

# mt.maxT for step-down maxT procedure
result <- mt.maxT(X = expression_matrix,
                  classlabel = class_labels,
                  B = 1000)

# Adjusted p-values account for correlation
sig_genes <- which(result$adjp < 0.05)
```

---

## Practical Guidelines

### Decision Framework

```
                     How many tests?
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
         Few (< 20)              Many (> 100)
              │                         │
              ▼                         ▼
    Pre-specified hypotheses?    Discovery or confirmation?
              │                         │
         ┌────┴────┐              ┌─────┴─────┐
         ▼         ▼              ▼           ▼
        Yes        No         Discovery  Confirmation
         │         │              │           │
         ▼         ▼              ▼           ▼
    Bonferroni   Holm         BH/FDR     Bonferroni
                                │
                                ▼
                         Correlated tests?
                                │
                         ┌──────┴──────┐
                         ▼             ▼
                        Yes           No
                         │             │
                         ▼             ▼
                   BY or permutation   BH
```

### Reporting in Manuscripts

**Methods Section Template:**
```
Multiple testing correction was performed using the Benjamini-Hochberg
procedure to control the false discovery rate (FDR) at 0.05. Genes were
considered differentially expressed if the adjusted p-value (FDR) was
< 0.05 and the absolute log2 fold change was > 1.
```

**For permutation-based:**
```
Statistical significance was assessed using permutation testing with
10,000 permutations. FDR was estimated by comparing observed test
statistics to the null distribution generated from label permutations.
```

### Common Mistakes to Avoid

1. **Using uncorrected p-values**: Never report raw p-values for multiple tests
2. **Wrong method for context**: Don't use Bonferroni for 20,000 gene tests
3. **Ignoring correlation**: For highly correlated tests, consider BY or permutation
4. **Threshold shopping**: Don't try multiple FDR thresholds and report the "best" one
5. **Mixing methods**: Be consistent within an analysis
6. **Forgetting to report**: Always state which correction method was used

### FDR Threshold Selection

| FDR Threshold | Interpretation | Use Case |
|---------------|----------------|----------|
| 0.01 | ~1% false discoveries | Stringent, high confidence |
| 0.05 | ~5% false discoveries | Standard for discovery |
| 0.10 | ~10% false discoveries | Exploratory, hypothesis generation |
| 0.25 | ~25% false discoveries | Very exploratory (e.g., GSEA default) |

---

## Quick Reference Card

### Python (statsmodels)

```python
from statsmodels.stats.multitest import multipletests

# Available methods
methods = ['bonferroni', 'holm', 'hochberg', 'fdr_bh', 'fdr_by']

rejected, padj, _, _ = multipletests(pvalues, alpha=0.05, method='fdr_bh')
```

### R Base

```r
# Available methods
methods <- c("bonferroni", "holm", "hochberg", "BH", "BY", "fdr")

padj <- p.adjust(pvalues, method = "BH")
```

### Common Bioinformatics Tools

| Tool | Default Correction | Column Name |
|------|-------------------|-------------|
| DESeq2 | BH | `padj` |
| edgeR | BH | `FDR` |
| limma | BH | `adj.P.Val` |
| Sleuth | BH (via aggregation) | `qval` |
| MAST | BH | `fdr` |

---

## See Also

- **test_decision_framework.md**: Statistical test selection
- **normalization_methods.md**: Pre-processing before testing
- **python_scipy_patterns.md**: Implementation details for Python
- **r_stats_patterns.md**: Implementation details for R

---

*Reference: Benjamini & Hochberg (1995), Storey & Tibshirani (2003)*
