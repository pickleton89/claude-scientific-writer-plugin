# Heatmaps for Expression Data

> Comprehensive guide for creating expression heatmaps with hierarchical clustering
> Covers Python (seaborn, matplotlib) and R (ComplexHeatmap, pheatmap) implementations

---

## Overview

Expression heatmaps visualize gene expression across samples, typically showing:
- **Rows**: Genes (features)
- **Columns**: Samples
- **Color**: Expression level (often z-scored)
- **Dendrograms**: Hierarchical clustering relationships

---

## Data Preparation

### When to Z-Score (Scale)

| Scenario | Scale? | Rationale |
|----------|--------|-----------|
| Compare expression patterns | Yes | Normalize different expression levels |
| Compare absolute expression | No | Preserve magnitude information |
| Identify co-expressed genes | Yes | Pattern similarity matters |
| Show expression changes | Yes | Visualize relative changes |

### Python Data Preparation

```python
import numpy as np
import pandas as pd
from scipy import stats

def prepare_expression_matrix(df, log_transform=True, z_score=True):
    """
    Prepare expression matrix for heatmap visualization.

    Parameters
    ----------
    df : pd.DataFrame
        Expression matrix (genes x samples), raw counts or normalized
    log_transform : bool
        Apply log2(x + 1) transformation
    z_score : bool
        Row-wise z-score normalization

    Returns
    -------
    pd.DataFrame
        Prepared expression matrix
    """
    mat = df.copy()

    # Log transform if dealing with counts
    if log_transform:
        mat = np.log2(mat + 1)

    # Row-wise z-score (each gene across samples)
    if z_score:
        mat = mat.apply(stats.zscore, axis=1)

    return mat

# Filter to top variable genes
def filter_top_variable_genes(df, n_genes=500):
    """Select top variable genes by variance."""
    variances = df.var(axis=1)
    top_genes = variances.nlargest(n_genes).index
    return df.loc[top_genes]

# Usage
expr_matrix = pd.read_csv('expression.csv', index_col=0)
expr_filtered = filter_top_variable_genes(expr_matrix, n_genes=200)
expr_scaled = prepare_expression_matrix(expr_filtered, log_transform=True, z_score=True)
```

### R Data Preparation

```r
prepare_expression_matrix <- function(mat, log_transform = TRUE, z_score = TRUE) {
  # Log transform
  if (log_transform) {
    mat <- log2(mat + 1)
  }

  # Row-wise z-score
  if (z_score) {
    mat <- t(scale(t(mat)))
  }

  return(mat)
}

# Filter top variable genes
filter_top_variable_genes <- function(mat, n_genes = 500) {
  gene_vars <- apply(mat, 1, var)
  top_genes <- names(sort(gene_vars, decreasing = TRUE)[1:n_genes])
  return(mat[top_genes, ])
}

# Usage
expr_matrix <- read.csv("expression.csv", row.names = 1)
expr_filtered <- filter_top_variable_genes(expr_matrix, n_genes = 200)
expr_scaled <- prepare_expression_matrix(expr_filtered)
```

---

## Python Implementation

### Seaborn Clustermap (Recommended)

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def expression_heatmap(expr_matrix, sample_metadata=None,
                       gene_metadata=None, figsize=(12, 10),
                       cmap='RdBu_r', center=0, vmin=-2, vmax=2):
    """
    Create clustered expression heatmap with annotations.

    Parameters
    ----------
    expr_matrix : pd.DataFrame
        Expression matrix (genes x samples), z-scored
    sample_metadata : pd.DataFrame, optional
        Sample annotations (samples x annotations)
    gene_metadata : pd.DataFrame, optional
        Gene annotations (genes x annotations)
    """

    # Build color mappings for annotations
    col_colors = None
    row_colors = None

    if sample_metadata is not None:
        col_colors = sample_metadata.apply(
            lambda x: pd.Categorical(x).codes
        ).apply(lambda x: plt.cm.Set2(x / max(x.max(), 1)))

    if gene_metadata is not None:
        row_colors = gene_metadata.apply(
            lambda x: pd.Categorical(x).codes
        ).apply(lambda x: plt.cm.Set1(x / max(x.max(), 1)))

    # Create clustermap
    g = sns.clustermap(
        expr_matrix,
        figsize=figsize,
        cmap=cmap,
        center=center,
        vmin=vmin,
        vmax=vmax,
        col_colors=col_colors,
        row_colors=row_colors,
        xticklabels=True,
        yticklabels=True,
        dendrogram_ratio=(0.1, 0.15),
        cbar_pos=(0.02, 0.8, 0.03, 0.15),
        tree_kws={'linewidths': 0.5}
    )

    # Rotate x-axis labels
    plt.setp(g.ax_heatmap.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Adjust font sizes
    g.ax_heatmap.set_xticklabels(g.ax_heatmap.get_xticklabels(), fontsize=8)
    g.ax_heatmap.set_yticklabels(g.ax_heatmap.get_yticklabels(), fontsize=6)

    return g

# Usage
g = expression_heatmap(expr_scaled, sample_metadata=sample_info)
g.savefig('heatmap.pdf', dpi=300, bbox_inches='tight')
```

### Customizing Clustermap

```python
# Custom color palette
from matplotlib.colors import LinearSegmentedColormap

# Blue-white-red (diverging)
colors = ['#2166AC', '#F7F7F7', '#B2182B']
cmap = LinearSegmentedColormap.from_list('custom_diverging', colors)

# Viridis (sequential, colorblind-friendly)
cmap = 'viridis'

# Control clustering
g = sns.clustermap(
    expr_matrix,
    # Clustering parameters
    method='ward',          # Linkage: 'ward', 'complete', 'average', 'single'
    metric='euclidean',     # Distance: 'euclidean', 'correlation', 'cosine'

    # Control which axes to cluster
    row_cluster=True,
    col_cluster=True,

    # Or use precomputed linkage
    # row_linkage=precomputed_linkage,

    # Standard options
    cmap=cmap,
    center=0,
    figsize=(14, 12)
)

# Disable clustering for ordered data
g = sns.clustermap(expr_matrix, row_cluster=False, col_cluster=False)
```

### Adding Sample Annotations

```python
# Create sample metadata DataFrame
sample_info = pd.DataFrame({
    'Condition': ['Control'] * 5 + ['Treatment'] * 5,
    'Batch': ['A', 'A', 'B', 'B', 'A', 'B', 'B', 'A', 'A', 'B'],
    'Time': [0, 0, 0, 0, 0, 24, 24, 24, 24, 24]
}, index=expr_matrix.columns)

# Define colors for categorical variables
condition_colors = {'Control': '#4DAF4A', 'Treatment': '#E41A1C'}
batch_colors = {'A': '#377EB8', 'B': '#FF7F00'}

# Create color mapping DataFrame
col_colors = pd.DataFrame({
    'Condition': sample_info['Condition'].map(condition_colors),
    'Batch': sample_info['Batch'].map(batch_colors)
})

g = sns.clustermap(expr_matrix, col_colors=col_colors)
```

### Matplotlib Heatmap (No Clustering)

```python
import matplotlib.pyplot as plt
import numpy as np

def simple_heatmap(matrix, row_labels=None, col_labels=None,
                   cmap='RdBu_r', vmin=-2, vmax=2, figsize=(10, 8)):
    """Simple heatmap without clustering using matplotlib."""

    fig, ax = plt.subplots(figsize=figsize)

    im = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Z-score', rotation=270, labelpad=15)

    # Labels
    if col_labels is not None:
        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha='right', fontsize=8)
    if row_labels is not None:
        ax.set_yticks(range(len(row_labels)))
        ax.set_yticklabels(row_labels, fontsize=6)

    plt.tight_layout()
    return fig, ax
```

---

## R Implementation

### ComplexHeatmap (Recommended)

```r
library(ComplexHeatmap)
library(circlize)

expression_heatmap <- function(mat, sample_metadata = NULL,
                               gene_metadata = NULL,
                               cluster_rows = TRUE,
                               cluster_cols = TRUE) {

  # Color function (diverging, centered at 0)
  col_fun <- colorRamp2(c(-2, 0, 2), c("#2166AC", "#F7F7F7", "#B2182B"))

  # Sample annotations (columns)
  col_anno <- NULL
  if (!is.null(sample_metadata)) {
    col_anno <- HeatmapAnnotation(
      df = sample_metadata,
      col = list(
        Condition = c("Control" = "#4DAF4A", "Treatment" = "#E41A1C"),
        Batch = c("A" = "#377EB8", "B" = "#FF7F00")
      ),
      annotation_name_side = "left"
    )
  }

  # Gene annotations (rows)
  row_anno <- NULL
  if (!is.null(gene_metadata)) {
    row_anno <- rowAnnotation(
      df = gene_metadata,
      col = list(
        Pathway = c("Metabolism" = "#984EA3", "Signaling" = "#FFFF33")
      )
    )
  }

  # Create heatmap
  ht <- Heatmap(
    mat,
    name = "Z-score",
    col = col_fun,

    # Clustering
    cluster_rows = cluster_rows,
    cluster_columns = cluster_cols,
    clustering_distance_rows = "euclidean",
    clustering_distance_columns = "euclidean",
    clustering_method_rows = "ward.D2",
    clustering_method_columns = "ward.D2",

    # Annotations
    top_annotation = col_anno,
    left_annotation = row_anno,

    # Labels
    show_row_names = nrow(mat) <= 50,  # Only show if reasonable
    show_column_names = TRUE,
    row_names_gp = gpar(fontsize = 6),
    column_names_gp = gpar(fontsize = 8),
    column_names_rot = 45,

    # Appearance
    row_dend_width = unit(1, "cm"),
    column_dend_height = unit(1, "cm"),
    heatmap_legend_param = list(
      title = "Z-score",
      legend_direction = "vertical",
      title_position = "topcenter"
    )
  )

  return(ht)
}

# Usage
ht <- expression_heatmap(expr_scaled, sample_metadata = sample_info)

# Save
pdf("heatmap.pdf", width = 10, height = 12)
draw(ht)
dev.off()
```

### Row and Column Splitting

```r
# Split by gene clusters
Heatmap(mat,
        row_split = gene_clusters,  # Factor vector
        row_title_rot = 0,
        row_gap = unit(2, "mm"))

# Split by sample groups
Heatmap(mat,
        column_split = sample_groups,
        column_title_rot = 0,
        column_gap = unit(2, "mm"))

# K-means clustering
Heatmap(mat,
        row_km = 4,  # 4 gene clusters
        row_km_repeats = 100)  # For stability
```

### Multiple Linked Heatmaps

```r
# Expression + mutation status
ht1 <- Heatmap(expr_mat, name = "Expression",
               col = colorRamp2(c(-2, 0, 2), c("blue", "white", "red")))

ht2 <- Heatmap(mutation_mat, name = "Mutation",
               col = c("0" = "white", "1" = "black"),
               width = unit(1, "cm"))

ht3 <- Heatmap(cnv_mat, name = "CNV",
               col = colorRamp2(c(-2, 0, 2), c("blue", "white", "red")),
               width = unit(2, "cm"))

# Combine horizontally (linked by rows)
ht_list <- ht1 + ht2 + ht3
draw(ht_list)
```

### pheatmap (Simpler Alternative)

```r
library(pheatmap)

# Basic usage
pheatmap(mat,
         scale = "row",  # Z-score by row
         clustering_method = "ward.D2",
         clustering_distance_rows = "euclidean",
         clustering_distance_cols = "euclidean")

# With annotations
annotation_col <- data.frame(
  Condition = c(rep("Control", 5), rep("Treatment", 5)),
  Batch = c("A", "A", "B", "B", "A", "B", "B", "A", "A", "B"),
  row.names = colnames(mat)
)

annotation_colors <- list(
  Condition = c(Control = "#4DAF4A", Treatment = "#E41A1C"),
  Batch = c(A = "#377EB8", B = "#FF7F00")
)

pheatmap(mat,
         scale = "row",
         annotation_col = annotation_col,
         annotation_colors = annotation_colors,
         show_rownames = FALSE,
         fontsize_col = 8,
         cellwidth = 15,
         cellheight = 0.5)

# Save
pheatmap(mat, filename = "heatmap.pdf", width = 10, height = 12)
```

---

## Clustering Considerations

### Distance Metrics

| Metric | Best For | Notes |
|--------|----------|-------|
| `euclidean` | Absolute differences | Sensitive to magnitude |
| `correlation` | Pattern similarity | Ignores magnitude |
| `cosine` | Direction similarity | Common for sparse data |
| `manhattan` | Robust to outliers | L1 norm |

### Linkage Methods

| Method | Behavior | Use When |
|--------|----------|----------|
| `ward.D2` | Compact clusters | Default choice, balanced |
| `complete` | Maximum distance | Want distinct clusters |
| `average` | Mean distance | Balanced approach |
| `single` | Minimum distance | Chain-like structures |

### Practical Recommendations

```python
# For gene expression: correlation distance with ward linkage
g = sns.clustermap(
    expr_matrix,
    metric='correlation',
    method='ward'
)
```

```r
# Same in R
Heatmap(mat,
        clustering_distance_rows = "pearson",  # 1 - correlation
        clustering_method_rows = "ward.D2")
```

---

## Color Palettes

### Diverging (Centered Data)

```python
# Python - for z-scored data centered at 0
import matplotlib.colors as mcolors

# Blue-white-red
cmap = 'RdBu_r'

# Custom
colors = ['#2166AC', '#67A9CF', '#D1E5F0', '#F7F7F7',
          '#FDDBC7', '#EF8A62', '#B2182B']
cmap = mcolors.LinearSegmentedColormap.from_list('custom', colors)
```

```r
# R - diverging color function
col_fun <- colorRamp2(c(-2, 0, 2), c("#2166AC", "#F7F7F7", "#B2182B"))

# Or with more gradations
col_fun <- colorRamp2(
  c(-2, -1, 0, 1, 2),
  c("#2166AC", "#67A9CF", "#F7F7F7", "#EF8A62", "#B2182B")
)
```

### Sequential (Positive Data)

```python
# For non-centered data (e.g., raw expression)
cmap = 'viridis'  # Colorblind-friendly
cmap = 'YlOrRd'   # Yellow to red
```

```r
col_fun <- colorRamp2(c(0, 5, 10), c("#FFFFCC", "#FD8D3C", "#800026"))
```

---

## Gene Selection Strategies

### Top Differentially Expressed

```python
# From DESeq2 results
def select_top_de_genes(de_results, expr_matrix, n_genes=100,
                        padj_threshold=0.05, lfc_threshold=1.0):
    """Select top DE genes for heatmap."""
    sig_genes = de_results[
        (de_results['padj'] < padj_threshold) &
        (de_results['log2FoldChange'].abs() > lfc_threshold)
    ]
    top_genes = sig_genes.nsmallest(n_genes, 'padj')['gene_id']
    return expr_matrix.loc[expr_matrix.index.isin(top_genes)]
```

### Top Variable Genes

```r
# Select by variance
select_variable_genes <- function(mat, n_genes = 500) {
  vars <- apply(mat, 1, var)
  top_genes <- names(sort(vars, decreasing = TRUE)[1:n_genes])
  return(mat[top_genes, ])
}
```

### Pathway-Specific Genes

```python
# Filter to genes in pathway of interest
pathway_genes = ['GENE1', 'GENE2', 'GENE3', ...]
heatmap_matrix = expr_matrix.loc[expr_matrix.index.isin(pathway_genes)]
```

---

## Publication Checklist

- [ ] Data appropriately transformed (log2 for counts)
- [ ] Z-scored by row if comparing patterns across genes
- [ ] Clustering method and distance metric stated in legend
- [ ] Color scale appropriate for data type (diverging for z-scores)
- [ ] Sample annotations clearly labeled
- [ ] Gene count stated (e.g., "Top 200 variable genes")
- [ ] Figure legend explains all annotation colors
- [ ] Saved as vector format (PDF) for publication
- [ ] Font sizes legible at publication size

---

## Common Issues

| Problem | Solution |
|---------|----------|
| Row labels too crowded | Reduce genes or hide labels (`show_row_names=FALSE`) |
| Columns hard to read | Rotate labels, increase figure width |
| One cluster dominates | Check for outlier samples, consider splitting |
| No clear patterns | Try different clustering, check data scaling |
| Colors too extreme | Adjust `vmin`/`vmax` or use `robust=True` in seaborn |

---

## Cross-References

- **[bioconductor_viz.md](bioconductor_viz.md)**: ComplexHeatmap advanced features
- **[volcano_plots.md](volcano_plots.md)**: Select DE genes for heatmap
- **[seaborn.md](seaborn.md)**: Python clustermap basics
- **[ggplot2.md](ggplot2.md)**: R visualization foundations
- **[../statistical-analysis/SKILL.md](../../statistical-analysis/SKILL.md)**: Clustering methods
