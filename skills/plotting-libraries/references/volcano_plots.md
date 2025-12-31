# Volcano Plots for Differential Expression

> Standard visualization for differential expression analysis
> Covers Python (matplotlib/seaborn) and R (ggplot2/EnhancedVolcano) implementations

---

## Overview

A volcano plot displays:
- **X-axis**: Log2 fold change (effect size)
- **Y-axis**: -log10(p-value) (statistical significance)

Points in the upper corners represent genes that are both statistically significant AND have large effect sizes.

### Standard Thresholds

| Threshold | Typical Value | Meaning |
|-----------|---------------|---------|
| p-value | 0.05 | Statistical significance |
| Adjusted p-value | 0.05 (FDR) | Multiple testing corrected |
| Log2 fold change | 1.0 | 2-fold change |
| Log2 fold change | 0.585 | 1.5-fold change |

---

## Python Implementation

### Basic Volcano with Matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def volcano_plot(df, log2fc_col='log2FoldChange', pvalue_col='padj',
                 gene_col='gene_symbol', fc_threshold=1.0, pval_threshold=0.05,
                 figsize=(10, 8)):
    """
    Create a volcano plot from differential expression results.

    Parameters
    ----------
    df : pd.DataFrame
        DE results with log2FC and p-value columns
    log2fc_col : str
        Column name for log2 fold change
    pvalue_col : str
        Column name for p-value (typically adjusted)
    gene_col : str
        Column name for gene identifiers
    fc_threshold : float
        Absolute log2FC threshold for significance
    pval_threshold : float
        P-value threshold for significance
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Calculate -log10(pvalue)
    df = df.copy()
    df['neg_log10_pval'] = -np.log10(df[pvalue_col].clip(lower=1e-300))

    # Classify points
    df['significance'] = 'Not Significant'
    df.loc[(df[pvalue_col] < pval_threshold) &
           (df[log2fc_col] >= fc_threshold), 'significance'] = 'Up'
    df.loc[(df[pvalue_col] < pval_threshold) &
           (df[log2fc_col] <= -fc_threshold), 'significance'] = 'Down'

    # Color mapping
    colors = {'Not Significant': 'gray', 'Up': 'red', 'Down': 'blue'}

    # Plot each category
    for sig, color in colors.items():
        subset = df[df['significance'] == sig]
        ax.scatter(subset[log2fc_col], subset['neg_log10_pval'],
                   c=color, label=sig, alpha=0.6, s=20, edgecolors='none')

    # Add threshold lines
    ax.axhline(-np.log10(pval_threshold), color='gray',
               linestyle='--', linewidth=0.8)
    ax.axvline(-fc_threshold, color='gray', linestyle='--', linewidth=0.8)
    ax.axvline(fc_threshold, color='gray', linestyle='--', linewidth=0.8)

    # Labels and formatting
    ax.set_xlabel('Log2 Fold Change', fontsize=12)
    ax.set_ylabel('-Log10(Adjusted P-value)', fontsize=12)
    ax.legend(title='Significance', loc='upper right')

    # Count annotations
    n_up = (df['significance'] == 'Up').sum()
    n_down = (df['significance'] == 'Down').sum()
    ax.set_title(f'Volcano Plot (Up: {n_up}, Down: {n_down})', fontsize=14)

    plt.tight_layout()
    return fig, ax

# Usage
# fig, ax = volcano_plot(deseq_results)
# plt.savefig('volcano.pdf', dpi=300, bbox_inches='tight')
```

### Enhanced Volcano with Gene Labels

```python
from adjustText import adjust_text

def volcano_plot_labeled(df, log2fc_col='log2FoldChange', pvalue_col='padj',
                         gene_col='gene_symbol', genes_to_label=None,
                         n_top_genes=10, fc_threshold=1.0, pval_threshold=0.05):
    """
    Volcano plot with gene labels for top significant genes.

    Parameters
    ----------
    genes_to_label : list, optional
        Specific genes to label
    n_top_genes : int
        Number of top genes to label if genes_to_label not provided
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    df = df.copy()
    df['neg_log10_pval'] = -np.log10(df[pvalue_col].clip(lower=1e-300))

    # Classify significance
    df['significance'] = 'NS'
    df.loc[(df[pvalue_col] < pval_threshold) &
           (df[log2fc_col] >= fc_threshold), 'significance'] = 'Up'
    df.loc[(df[pvalue_col] < pval_threshold) &
           (df[log2fc_col] <= -fc_threshold), 'significance'] = 'Down'

    colors = {'NS': '#BBBBBB', 'Up': '#E41A1C', 'Down': '#377EB8'}

    for sig, color in colors.items():
        subset = df[df['significance'] == sig]
        ax.scatter(subset[log2fc_col], subset['neg_log10_pval'],
                   c=color, label=sig, alpha=0.5, s=15)

    # Determine genes to label
    if genes_to_label is None:
        # Top by adjusted p-value
        sig_genes = df[df['significance'].isin(['Up', 'Down'])]
        sig_genes = sig_genes.nsmallest(n_top_genes, pvalue_col)
        genes_to_label = sig_genes[gene_col].tolist()

    # Add labels
    texts = []
    for gene in genes_to_label:
        if gene in df[gene_col].values:
            row = df[df[gene_col] == gene].iloc[0]
            texts.append(ax.text(row[log2fc_col], row['neg_log10_pval'],
                                 gene, fontsize=8, ha='center'))

    # Adjust text positions to avoid overlap
    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='black', lw=0.5))

    # Threshold lines
    ax.axhline(-np.log10(pval_threshold), color='gray', linestyle='--', lw=0.8)
    ax.axvline(-fc_threshold, color='gray', linestyle='--', lw=0.8)
    ax.axvline(fc_threshold, color='gray', linestyle='--', lw=0.8)

    ax.set_xlabel('Log2 Fold Change', fontsize=12, fontweight='bold')
    ax.set_ylabel('-Log10(Adjusted P-value)', fontsize=12, fontweight='bold')
    ax.legend(title='Regulation', frameon=True)

    plt.tight_layout()
    return fig, ax
```

### Seaborn-Based Volcano

```python
import seaborn as sns

def volcano_seaborn(df, log2fc_col='log2FoldChange', pvalue_col='padj',
                    fc_threshold=1.0, pval_threshold=0.05):
    """Volcano plot using seaborn for statistical styling."""

    df = df.copy()
    df['neg_log10_pval'] = -np.log10(df[pvalue_col].clip(lower=1e-300))

    # Classification
    conditions = [
        (df[pvalue_col] < pval_threshold) & (df[log2fc_col] >= fc_threshold),
        (df[pvalue_col] < pval_threshold) & (df[log2fc_col] <= -fc_threshold)
    ]
    choices = ['Upregulated', 'Downregulated']
    df['Regulation'] = np.select(conditions, choices, default='Not Significant')

    # Order categories for legend
    df['Regulation'] = pd.Categorical(
        df['Regulation'],
        categories=['Upregulated', 'Downregulated', 'Not Significant']
    )

    # Plot
    plt.figure(figsize=(10, 8))
    palette = {'Upregulated': '#E41A1C',
               'Downregulated': '#377EB8',
               'Not Significant': '#999999'}

    ax = sns.scatterplot(data=df, x=log2fc_col, y='neg_log10_pval',
                         hue='Regulation', palette=palette,
                         alpha=0.6, s=20, edgecolor='none')

    # Threshold lines
    plt.axhline(-np.log10(pval_threshold), color='gray',
                linestyle='--', linewidth=0.8, zorder=0)
    plt.axvline(-fc_threshold, color='gray',
                linestyle='--', linewidth=0.8, zorder=0)
    plt.axvline(fc_threshold, color='gray',
                linestyle='--', linewidth=0.8, zorder=0)

    plt.xlabel('Log2 Fold Change')
    plt.ylabel('-Log10(Adjusted P-value)')
    plt.legend(title='Regulation', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()

    return plt.gcf(), ax
```

---

## R Implementation

### Basic ggplot2 Volcano

```r
library(ggplot2)
library(dplyr)

volcano_ggplot <- function(df, log2fc_col = "log2FoldChange",
                           pvalue_col = "padj", gene_col = "gene_symbol",
                           fc_threshold = 1.0, pval_threshold = 0.05) {

  # Prepare data
  df <- df %>%
    mutate(
      neg_log10_pval = -log10(get(pvalue_col)),
      significance = case_when(
        get(pvalue_col) < pval_threshold & get(log2fc_col) >= fc_threshold ~ "Up",
        get(pvalue_col) < pval_threshold & get(log2fc_col) <= -fc_threshold ~ "Down",
        TRUE ~ "NS"
      )
    )

  # Count significant genes
  n_up <- sum(df$significance == "Up")
  n_down <- sum(df$significance == "Down")

  # Plot
  ggplot(df, aes_string(x = log2fc_col, y = "neg_log10_pval")) +
    geom_point(aes(color = significance), alpha = 0.6, size = 1.5) +
    scale_color_manual(
      values = c("Up" = "#E41A1C", "Down" = "#377EB8", "NS" = "#999999"),
      labels = c("Up" = paste0("Up (", n_up, ")"),
                 "Down" = paste0("Down (", n_down, ")"),
                 "NS" = "Not Significant")
    ) +
    geom_hline(yintercept = -log10(pval_threshold),
               linetype = "dashed", color = "gray50") +
    geom_vline(xintercept = c(-fc_threshold, fc_threshold),
               linetype = "dashed", color = "gray50") +
    labs(
      x = "Log2 Fold Change",
      y = "-Log10(Adjusted P-value)",
      color = "Regulation"
    ) +
    theme_classic() +
    theme(
      legend.position = "right",
      axis.text = element_text(color = "black"),
      axis.title = element_text(face = "bold")
    )
}

# Usage
# p <- volcano_ggplot(deseq_results)
# ggsave("volcano.pdf", p, width = 8, height = 6)
```

### Volcano with Gene Labels (ggrepel)

```r
library(ggrepel)

volcano_labeled <- function(df, log2fc_col = "log2FoldChange",
                            pvalue_col = "padj", gene_col = "gene_symbol",
                            genes_to_label = NULL, n_top = 10,
                            fc_threshold = 1.0, pval_threshold = 0.05) {

  df <- df %>%
    mutate(
      neg_log10_pval = -log10(get(pvalue_col)),
      significance = case_when(
        get(pvalue_col) < pval_threshold & get(log2fc_col) >= fc_threshold ~ "Up",
        get(pvalue_col) < pval_threshold & get(log2fc_col) <= -fc_threshold ~ "Down",
        TRUE ~ "NS"
      )
    )

  # Determine genes to label
  if (is.null(genes_to_label)) {
    top_genes <- df %>%
      filter(significance %in% c("Up", "Down")) %>%
      arrange(get(pvalue_col)) %>%
      head(n_top) %>%
      pull(gene_col)
    genes_to_label <- top_genes
  }

  df <- df %>%
    mutate(label = ifelse(get(gene_col) %in% genes_to_label, get(gene_col), ""))

  ggplot(df, aes_string(x = log2fc_col, y = "neg_log10_pval")) +
    geom_point(aes(color = significance), alpha = 0.5, size = 1.5) +
    geom_text_repel(
      aes(label = label),
      size = 3,
      max.overlaps = 20,
      box.padding = 0.5,
      point.padding = 0.3,
      segment.color = "gray50",
      segment.size = 0.3
    ) +
    scale_color_manual(
      values = c("Up" = "#E41A1C", "Down" = "#377EB8", "NS" = "#BBBBBB")
    ) +
    geom_hline(yintercept = -log10(pval_threshold),
               linetype = "dashed", color = "gray50") +
    geom_vline(xintercept = c(-fc_threshold, fc_threshold),
               linetype = "dashed", color = "gray50") +
    labs(
      x = "Log2 Fold Change",
      y = "-Log10(Adjusted P-value)",
      color = "Regulation"
    ) +
    theme_classic() +
    theme(legend.position = "right")
}
```

### EnhancedVolcano (Recommended)

```r
library(EnhancedVolcano)

# Basic usage
EnhancedVolcano(res,
    lab = res$gene_symbol,
    x = 'log2FoldChange',
    y = 'padj',
    pCutoff = 0.05,
    FCcutoff = 1.0,
    title = 'Treatment vs Control')

# Publication-ready customization
EnhancedVolcano(res,
    lab = res$gene_symbol,
    x = 'log2FoldChange',
    y = 'padj',

    # Thresholds
    pCutoff = 0.05,
    FCcutoff = 1.0,

    # Title and labels
    title = 'Differential Expression Analysis',
    subtitle = 'Treatment vs Control',
    caption = paste0('Total = ', nrow(res), ' genes'),

    # Point aesthetics
    pointSize = 2.5,
    col = c('grey30', 'forestgreen', 'royalblue', 'red2'),
    colAlpha = 0.5,

    # Label aesthetics
    labSize = 3.5,
    labCol = 'black',
    labFace = 'bold',
    drawConnectors = TRUE,
    widthConnectors = 0.5,
    colConnectors = 'grey50',

    # Axis limits
    xlim = c(-8, 8),
    ylim = c(0, -log10(10e-50)),

    # Legend
    legendPosition = 'right',
    legendLabSize = 12,
    legendIconSize = 4.0,

    # Border
    border = 'full',
    borderWidth = 1.0,
    borderColour = 'black',

    # Gridlines
    gridlines.major = FALSE,
    gridlines.minor = FALSE)
```

### Highlight Specific Genes

```r
# With EnhancedVolcano
genes_of_interest <- c("TP53", "BRCA1", "MYC", "EGFR", "KRAS")

EnhancedVolcano(res,
    lab = res$gene_symbol,
    x = 'log2FoldChange',
    y = 'padj',
    selectLab = genes_of_interest,
    drawConnectors = TRUE,
    boxedLabels = TRUE,
    labSize = 4)

# Custom styling for specific genes
EnhancedVolcano(res,
    lab = res$gene_symbol,
    x = 'log2FoldChange',
    y = 'padj',
    selectLab = genes_of_interest,
    shape = ifelse(res$gene_symbol %in% genes_of_interest, 17, 16),
    pointSize = ifelse(res$gene_symbol %in% genes_of_interest, 4, 2))
```

---

## Best Practices

### Threshold Selection

| Context | p-value | Log2FC | Rationale |
|---------|---------|--------|-----------|
| Exploratory | 0.05 | 0.585 | Broad discovery |
| Standard | 0.05 (FDR) | 1.0 | Balance specificity/sensitivity |
| Stringent | 0.01 (FDR) | 1.5 | High confidence only |
| Very stringent | 0.001 (FDR) | 2.0 | Reduce false positives |

### Always Use Adjusted P-values

```python
# In DESeq2 output, use 'padj' not 'pvalue'
volcano_plot(res, pvalue_col='padj')  # Correct
volcano_plot(res, pvalue_col='pvalue')  # Wrong - inflated significance
```

```r
# Same in R
EnhancedVolcano(res, y = 'padj')  # Correct
EnhancedVolcano(res, y = 'pvalue')  # Wrong
```

### Label Selection Strategies

1. **Top N by p-value**: Most statistically significant
2. **Top N by effect size**: Largest fold changes
3. **Genes of interest**: Prior biological knowledge
4. **Pathway-specific**: Genes in pathways of interest

```python
# Combined strategy
def select_genes_to_label(df, n_pval=5, n_fc=5, custom=[]):
    """Select genes for labeling using multiple criteria."""
    significant = df[df['significance'].isin(['Up', 'Down'])]

    # Top by p-value
    top_pval = significant.nsmallest(n_pval, 'padj')['gene_symbol'].tolist()

    # Top by absolute fold change
    top_fc = significant.nlargest(n_fc, df['log2FoldChange'].abs())['gene_symbol'].tolist()

    # Combine unique
    return list(set(top_pval + top_fc + custom))
```

### Color Accessibility

```python
# Colorblind-friendly palette
colors = {
    'Up': '#D55E00',    # Vermillion (red-blind safe)
    'Down': '#0072B2',  # Blue
    'NS': '#999999'     # Gray
}

# Or use colorblind-safe blue/orange
colors = {
    'Up': '#E69F00',    # Orange
    'Down': '#56B4E9',  # Sky blue
    'NS': '#999999'
}
```

---

## Publication Checklist

- [ ] Used adjusted p-values (FDR), not raw p-values
- [ ] Clearly stated thresholds in figure legend
- [ ] Labeled key genes of interest
- [ ] Used colorblind-friendly palette
- [ ] Included gene counts in legend/title
- [ ] Saved as vector format (PDF/SVG) for print
- [ ] Figure size matches journal requirements
- [ ] Axis labels are clear and include units where applicable

---

## Cross-References

- **[bioconductor_viz.md](bioconductor_viz.md)**: EnhancedVolcano details
- **[heatmaps.md](heatmaps.md)**: Visualize significant genes as heatmap
- **[matplotlib.md](matplotlib.md)**: Python plotting fundamentals
- **[ggplot2.md](ggplot2.md)**: R plotting fundamentals
- **[../statistical-analysis/SKILL.md](../../statistical-analysis/SKILL.md)**: Differential expression statistics
