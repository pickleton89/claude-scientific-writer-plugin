# Normalization Methods for Sequencing Data

> Pre-requisite for valid statistical comparisons in RNA-seq and other count-based assays

---

## Why Normalization Is Essential

Raw sequencing counts cannot be directly compared between samples due to systematic technical biases:

### Technical Sources of Variation

| Source | Problem | Solution |
|--------|---------|----------|
| **Sequencing depth** | Sample A: 10M reads vs Sample B: 50M reads | Library size normalization |
| **Gene length** | Long genes capture more reads | Length normalization (RPKM/FPKM/TPM) |
| **RNA composition** | Highly expressed genes dominate | TMM, DESeq2 size factors |
| **GC content** | GC-rich regions have variable coverage | GC-content correction |
| **Batch effects** | Samples processed on different days | Batch correction methods |

### The Composition Bias Problem

```
Scenario: Treatment upregulates one gene 100-fold

Without correction:
- Highly expressed gene takes larger fraction of reads
- Other genes APPEAR downregulated (fewer reads available)
- False positives for downregulation

TMM/DESeq2 solution:
- Estimate scaling factors from genes NOT differentially expressed
- Correct for compositional changes
```

---

## Library Size Normalization Methods

### CPM (Counts Per Million)

**Formula**: `CPM = (raw_count / total_reads) × 10^6`

**Use case**: Quick visualization, not recommended for DE analysis

```python
# Python
import numpy as np

def cpm(counts):
    """Calculate counts per million."""
    lib_sizes = counts.sum(axis=0)
    return counts / lib_sizes * 1e6
```

```r
# R (edgeR)
library(edgeR)
cpm_values <- cpm(counts)
```

**Limitation**: Does not account for gene length or composition bias.

---

### RPKM/FPKM (Reads/Fragments Per Kilobase Million)

**Formula**: `RPKM = (raw_count × 10^9) / (total_reads × gene_length)`

- **RPKM**: Single-end reads
- **FPKM**: Paired-end fragments (count pairs once)

**Use case**: Within-sample comparison of gene expression levels

```python
# Python
def rpkm(counts, gene_lengths, total_reads=None):
    """Calculate RPKM values.

    Parameters
    ----------
    counts : np.ndarray
        Raw count matrix (genes × samples)
    gene_lengths : np.ndarray
        Gene lengths in base pairs
    total_reads : np.ndarray, optional
        Library sizes. Computed from counts if not provided.
    """
    if total_reads is None:
        total_reads = counts.sum(axis=0)

    # Normalize by library size (per million)
    rpm = counts / total_reads * 1e6

    # Normalize by gene length (per kilobase)
    rpkm = rpm / (gene_lengths[:, np.newaxis] / 1000)

    return rpkm
```

```r
# R
rpkm <- function(counts, gene_lengths) {
    lib_sizes <- colSums(counts)
    rpm <- sweep(counts, 2, lib_sizes, "/") * 1e6
    rpkm <- sweep(rpm, 1, gene_lengths / 1000, "/")
    return(rpkm)
}
```

**Limitation**: Not comparable across samples (different total RPKM per sample).

---

### TPM (Transcripts Per Million)

**Formula**:
1. Normalize by gene length: `RPK = count / (gene_length_kb)`
2. Normalize by sum: `TPM = (RPK / sum(RPK)) × 10^6`

**Advantage**: Sum of TPM equals 1 million for every sample (comparable across samples)

```python
# Python
def tpm(counts, gene_lengths):
    """Calculate TPM values.

    TPM sums to 1 million in each sample, enabling cross-sample comparison.
    """
    # Step 1: Normalize by gene length
    rpk = counts / (gene_lengths[:, np.newaxis] / 1000)

    # Step 2: Normalize by sum (per million)
    scaling_factors = rpk.sum(axis=0) / 1e6
    tpm_values = rpk / scaling_factors

    return tpm_values
```

```r
# R
tpm <- function(counts, gene_lengths) {
    rpk <- counts / (gene_lengths / 1000)
    scaling <- colSums(rpk) / 1e6
    tpm <- sweep(rpk, 2, scaling, "/")
    return(tpm)
}
```

**Use case**:
- Visualization and heatmaps
- Cross-sample gene expression comparison
- NOT recommended for differential expression (use raw counts + DESeq2/edgeR)

---

## Advanced Normalization for Differential Expression

### TMM (Trimmed Mean of M-values) — edgeR

**Principle**: Estimate scaling factors from genes that are NOT differentially expressed.

**Algorithm**:
1. Select reference sample (often the one closest to mean library size)
2. Calculate M-values (log fold changes) and A-values (average expression)
3. Trim extreme M and A values (default: 30% M, 5% A)
4. Calculate weighted mean of remaining M-values

```r
# R (edgeR)
library(edgeR)

# Create DGEList object
dge <- DGEList(counts = count_matrix, group = group_factor)

# Calculate TMM normalization factors
dge <- calcNormFactors(dge, method = "TMM")

# View normalization factors (should be close to 1)
dge$samples$norm.factors

# Get normalized counts (for visualization only)
cpm_normalized <- cpm(dge, normalized.lib.sizes = TRUE)

# For DE analysis, use raw counts with normalization factors
```

```python
# Python (using rpy2 or manual implementation)
# Most Python DE tools use DESeq2-style normalization
# For TMM in Python, consider conorm package or manual implementation

import numpy as np

def tmm_normalization(counts, ref_column=None, trim_m=0.3, trim_a=0.05):
    """
    Simplified TMM implementation.

    For production use, prefer edgeR or DESeq2.
    """
    n_samples = counts.shape[1]

    # Select reference (highest total count)
    if ref_column is None:
        ref_column = np.argmax(counts.sum(axis=0))

    ref_counts = counts[:, ref_column]
    norm_factors = np.ones(n_samples)

    for i in range(n_samples):
        if i == ref_column:
            continue

        sample_counts = counts[:, i]

        # Filter zeros
        keep = (ref_counts > 0) & (sample_counts > 0)

        # M-values (log fold changes)
        m_values = np.log2(sample_counts[keep] / ref_counts[keep])

        # A-values (average expression)
        a_values = 0.5 * np.log2(sample_counts[keep] * ref_counts[keep])

        # Trim extremes
        m_lower, m_upper = np.percentile(m_values, [trim_m*100/2, 100-trim_m*100/2])
        a_lower, a_upper = np.percentile(a_values, [trim_a*100/2, 100-trim_a*100/2])

        keep_trim = (m_values >= m_lower) & (m_values <= m_upper) & \
                    (a_values >= a_lower) & (a_values <= a_upper)

        # Weighted mean of M-values
        if keep_trim.sum() > 0:
            norm_factors[i] = 2 ** np.mean(m_values[keep_trim])

    return norm_factors
```

---

### DESeq2 Size Factors (Median of Ratios)

**Principle**: Use geometric mean as pseudo-reference, calculate median ratio.

**Algorithm**:
1. Calculate geometric mean across samples for each gene
2. Divide each sample's counts by the geometric mean
3. Take median of these ratios as the size factor

```r
# R (DESeq2)
library(DESeq2)

# Create DESeqDataSet
dds <- DESeqDataSetFromMatrix(
    countData = count_matrix,
    colData = sample_info,
    design = ~ condition
)

# Estimate size factors
dds <- estimateSizeFactors(dds)

# View size factors
sizeFactors(dds)

# Get normalized counts (for visualization)
counts_normalized <- counts(dds, normalized = TRUE)

# Full DE pipeline
dds <- DESeq(dds)  # Includes size factor estimation
results <- results(dds)
```

```python
# Python (pydeseq2)
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# Create dataset
dds = DeseqDataSet(
    counts=count_df,
    metadata=metadata_df,
    design_factors="condition"
)

# Fit model (includes size factor estimation)
dds.deseq2()

# Access size factors
size_factors = dds.obsm["size_factors"]

# Get normalized counts
normalized_counts = dds.layers["normed_counts"]
```

**Manual implementation**:

```python
import numpy as np
from scipy.stats import gmean

def deseq2_size_factors(counts):
    """
    Calculate DESeq2-style size factors (median of ratios method).

    Parameters
    ----------
    counts : np.ndarray
        Raw count matrix (genes × samples), non-negative integers

    Returns
    -------
    np.ndarray
        Size factors for each sample
    """
    # Filter genes with zeros (geometric mean undefined)
    counts_filtered = counts[np.all(counts > 0, axis=1), :]

    if counts_filtered.shape[0] < 100:
        raise ValueError("Too few genes without zeros for reliable estimation")

    # Geometric mean per gene (pseudo-reference)
    geo_means = gmean(counts_filtered, axis=1)

    # Ratio to pseudo-reference
    ratios = counts_filtered / geo_means[:, np.newaxis]

    # Median of ratios per sample
    size_factors = np.median(ratios, axis=0)

    return size_factors
```

---

### Limma-Voom Transformation

**Principle**: Transform counts to log-CPM with precision weights for linear modeling.

**When to use**:
- Large sample sizes (n > 3 per group)
- When you want to use limma's robust linear modeling
- Complex experimental designs

```r
# R (limma + edgeR)
library(limma)
library(edgeR)

# Create DGEList and normalize
dge <- DGEList(counts = count_matrix)
dge <- calcNormFactors(dge, method = "TMM")

# Filter low-expressed genes (important!)
keep <- filterByExpr(dge, design = design_matrix)
dge <- dge[keep, , keep.lib.sizes = FALSE]

# Voom transformation
v <- voom(dge, design = design_matrix, plot = TRUE)

# v$E contains log2-CPM values
# v$weights contains precision weights

# Fit linear model
fit <- lmFit(v, design_matrix)
fit <- eBayes(fit)
results <- topTable(fit, coef = 2, n = Inf)
```

**Voom output structure**:
- `v$E`: log2-CPM expression values
- `v$weights`: Precision weights (inverse variance)
- `v$targets`: Sample information
- `v$genes`: Gene annotation

---

## Method Selection Guide

### Decision Framework

```
What is your analysis goal?
│
├── Visualization / Exploration
│   ├── Within-sample gene comparison → RPKM/FPKM
│   └── Cross-sample comparison → TPM or normalized CPM
│
├── Differential Expression Analysis
│   ├── Small samples (n ≤ 3 per group)
│   │   └── DESeq2 (better small-sample performance)
│   ├── Large samples (n > 3 per group)
│   │   ├── Simple design → DESeq2 or edgeR
│   │   └── Complex design → limma-voom
│   └── Very large dataset (>100 samples)
│       └── limma-voom (fastest)
│
└── Machine Learning / Integration
    ├── Same platform → TPM or VST (variance stabilizing transformation)
    └── Cross-platform → Quantile normalization + batch correction
```

### Quick Reference Table

| Method | Use For | Avoid For | Tool |
|--------|---------|-----------|------|
| **CPM** | Quick QC plots | DE analysis, comparisons | Any |
| **RPKM/FPKM** | Within-sample comparison | Cross-sample comparison | Any |
| **TPM** | Cross-sample visualization, ML | DE analysis (use raw counts) | Any |
| **TMM** | DE analysis with edgeR | — | edgeR |
| **DESeq2 size factors** | DE analysis with DESeq2 | — | DESeq2 |
| **Voom** | DE with limma, complex designs | Very small samples | limma |
| **VST** | Visualization, clustering, ML | DE analysis | DESeq2 |
| **rlog** | Small samples, visualization | Large datasets (slow) | DESeq2 |

---

## Batch Effect Correction

### When Batch Correction Is Needed

**Symptoms of batch effects**:
- PCA shows samples clustering by batch, not biology
- Known batches (different days, operators, lanes)
- Unexplained systematic variation

**When NOT to correct**:
- Batch is confounded with biological condition (use blocking instead)
- Only one batch (no reference for correction)
- Batch effects are negligible (check PCA first)

### ComBat (SVA Package)

**Use case**: Known batches, moderate effects

```r
# R (sva package)
library(sva)

# Input: log-transformed, normalized expression matrix
# Do NOT use raw counts

# Basic ComBat
combat_corrected <- ComBat(
    dat = log_expr_matrix,      # genes × samples
    batch = batch_vector,        # batch labels
    mod = model_matrix           # biological variables to preserve
)

# ComBat-seq for count data (preferred for RNA-seq)
library(sva)
combat_seq_corrected <- ComBat_seq(
    counts = count_matrix,
    batch = batch_vector,
    group = condition_vector     # biological groups to preserve
)
```

```python
# Python (combat or inmoose)
from combat.pycombat import pycombat
import pandas as pd

# Expression matrix as DataFrame (genes × samples)
corrected = pycombat(expression_df, batch_series)
```

### Harmony (Single-Cell Focus, Also Works for Bulk)

**Use case**: Integration of multiple datasets, large-scale data

```r
# R
library(harmony)

# Typically used on PCA embeddings
# Input: PCA matrix (samples × PCs)
harmony_embeddings <- RunHarmony(
    pca_matrix,
    metadata,
    "batch",
    verbose = FALSE
)
```

```python
# Python (harmonypy)
import harmonypy as hm

# Run on PCA embeddings
ho = hm.run_harmony(pca_embeddings, metadata_df, ['batch'])
corrected_embeddings = ho.Z_corr.T
```

### limma removeBatchEffect

**Use case**: Quick batch correction for visualization, not for DE testing

```r
# R (limma)
library(limma)

# For visualization only - corrected values
corrected_expr <- removeBatchEffect(
    log_expr_matrix,
    batch = batch_vector,
    design = model.matrix(~ condition)  # preserve biological signal
)

# For DE analysis - include batch in model instead
design <- model.matrix(~ batch + condition)
fit <- lmFit(expr_matrix, design)
```

### Best Practices for Batch Correction

1. **Always check if needed**: PCA colored by batch before correction
2. **Never correct then test**: Include batch in DE model instead
3. **Preserve biology**: Always include biological covariates in correction
4. **Verify correction**: PCA should show biological clustering after
5. **Document everything**: Report what correction was applied

```r
# Verification workflow
library(ggplot2)

# PCA before correction
pca_before <- prcomp(t(log_expr))
df_before <- data.frame(
    PC1 = pca_before$x[,1],
    PC2 = pca_before$x[,2],
    batch = batch_vector,
    condition = condition_vector
)

p1 <- ggplot(df_before, aes(PC1, PC2, color = batch, shape = condition)) +
    geom_point(size = 3) +
    ggtitle("Before Batch Correction")

# PCA after correction
pca_after <- prcomp(t(corrected_expr))
df_after <- data.frame(
    PC1 = pca_after$x[,1],
    PC2 = pca_after$x[,2],
    batch = batch_vector,
    condition = condition_vector
)

p2 <- ggplot(df_after, aes(PC1, PC2, color = condition, shape = batch)) +
    geom_point(size = 3) +
    ggtitle("After Batch Correction")

gridExtra::grid.arrange(p1, p2, ncol = 2)
```

---

## Reporting in Manuscripts

### Methods Section Template

```markdown
**RNA-seq normalization and batch correction**

Raw read counts were normalized using [TMM normalization (edgeR v3.XX) /
DESeq2 median of ratios method (v1.XX)]. For visualization and clustering,
[TPM / variance-stabilized transformation (VST)] values were used.

[If applicable]: Batch effects arising from [source] were corrected using
[ComBat-seq / Harmony / limma removeBatchEffect], with [biological covariates]
included in the model to preserve biological signal. Principal component
analysis confirmed successful batch correction while maintaining separation
of biological groups (Supplementary Figure X).

For differential expression analysis, raw counts were used with normalization
factors calculated by [method], following best practices that recommend against
using pre-corrected values for statistical testing [cite Love et al. 2014 /
Robinson et al. 2010].
```

### Supplementary Figure Suggestions

1. **Library size distribution**: Box plot of total reads per sample
2. **PCA before/after normalization**: Show effect of normalization
3. **PCA colored by batch**: Verify batch correction (if applied)
4. **MA plot of normalization**: M vs A plot before/after

---

## Common Pitfalls

| Mistake | Problem | Solution |
|---------|---------|----------|
| Using FPKM/TPM for DE | Loses statistical power, ignores uncertainty | Use raw counts + DESeq2/edgeR |
| Batch correction then testing | Inflates significance, loses degrees of freedom | Include batch in statistical model |
| Ignoring composition bias | False DE calls due to highly abundant genes | Use TMM or DESeq2 size factors |
| Same normalization for all purposes | Different goals need different approaches | Visualization: TPM/VST; DE: raw counts |
| Not filtering low counts | Noise dominates, unreliable variance estimates | Filter genes with low counts across samples |

---

## References

1. Robinson MD, Oshlack A (2010). A scaling normalization method for differential expression analysis of RNA-seq data. *Genome Biology* 11:R25. (TMM)

2. Love MI, Huber W, Anders S (2014). Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biology* 15:550.

3. Law CW, Chen Y, Shi W, Smyth GK (2014). voom: precision weights unlock linear model analysis tools for RNA-seq read counts. *Genome Biology* 15:R29.

4. Johnson WE, Li C, Rabinovic A (2007). Adjusting batch effects in microarray expression data using empirical Bayes methods. *Biostatistics* 8:118-127. (ComBat)

5. Korsunsky I, et al. (2019). Fast, sensitive and accurate integration of single-cell data with Harmony. *Nature Methods* 16:1289-1296.
