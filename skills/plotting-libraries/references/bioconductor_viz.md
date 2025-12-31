# Bioconductor Visualization Packages

> Specialized R packages for bioinformatics data visualization
> Covers ComplexHeatmap, EnhancedVolcano, ggpubr, and related tools

---

## Package Overview

| Package | Purpose | Best For |
|---------|---------|----------|
| ComplexHeatmap | Advanced heatmaps | Expression matrices, multi-omics |
| EnhancedVolcano | Volcano plots | Differential expression |
| ggpubr | Publication-ready ggplot2 | Statistical annotations |
| clusterProfiler | Enrichment visualization | GO/KEGG results |
| Gviz | Genome tracks | Genomic regions |
| ggbio | Genome visualization | Circular plots, ideograms |

---

## ComplexHeatmap

### Installation

```r
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("ComplexHeatmap")
```

### Basic Heatmap

```r
library(ComplexHeatmap)
library(circlize)  # For color functions

# Create expression matrix (genes x samples)
mat <- matrix(rnorm(200), nrow = 20, ncol = 10)
rownames(mat) <- paste0("Gene", 1:20)
colnames(mat) <- paste0("Sample", 1:10)

# Basic heatmap
Heatmap(mat)

# With customization
Heatmap(mat,
        name = "Expression",  # Legend title
        col = colorRamp2(c(-2, 0, 2), c("blue", "white", "red")),
        cluster_rows = TRUE,
        cluster_columns = TRUE,
        show_row_names = TRUE,
        show_column_names = TRUE,
        row_names_gp = gpar(fontsize = 8),
        column_names_gp = gpar(fontsize = 10))
```

### Row and Column Annotations

```r
# Sample annotations (columns)
sample_anno <- HeatmapAnnotation(
  Condition = c(rep("Control", 5), rep("Treatment", 5)),
  Batch = c(rep("A", 3), rep("B", 4), rep("A", 3)),
  Age = sample(20:60, 10),
  col = list(
    Condition = c("Control" = "#4DAF4A", "Treatment" = "#E41A1C"),
    Batch = c("A" = "#377EB8", "B" = "#FF7F00"),
    Age = colorRamp2(c(20, 40, 60), c("white", "gray", "black"))
  ),
  annotation_name_side = "left"
)

# Gene annotations (rows)
gene_anno <- rowAnnotation(
  Pathway = c(rep("Metabolism", 10), rep("Signaling", 10)),
  LogFC = rnorm(20),
  col = list(
    Pathway = c("Metabolism" = "#984EA3", "Signaling" = "#FFFF33"),
    LogFC = colorRamp2(c(-2, 0, 2), c("green", "white", "red"))
  )
)

# Combine
Heatmap(mat,
        name = "Expression",
        top_annotation = sample_anno,
        left_annotation = gene_anno)
```

### Row/Column Splitting

```r
# Split by factor
Heatmap(mat,
        name = "Expression",
        row_split = c(rep("Cluster1", 10), rep("Cluster2", 10)),
        column_split = c(rep("Control", 5), rep("Treatment", 5)),
        row_title_rot = 0,
        column_title_rot = 0)

# Split by k-means clustering
Heatmap(mat,
        name = "Expression",
        row_km = 3,      # 3 row clusters
        column_km = 2)   # 2 column clusters
```

### Multiple Heatmaps

```r
# Create additional heatmap
mat2 <- matrix(sample(0:1, 200, replace = TRUE), nrow = 20)
rownames(mat2) <- rownames(mat)

# Horizontal concatenation
ht_list <- Heatmap(mat, name = "Expression") +
           Heatmap(mat2, name = "Mutation",
                   col = c("0" = "white", "1" = "black"),
                   width = unit(2, "cm"))

draw(ht_list)

# Vertical concatenation
ht_list <- Heatmap(mat, name = "Expression") %v%
           Heatmap(t(mat2), name = "Mutation")
```

### Controlling Clustering

```r
# Custom distance and clustering
Heatmap(mat,
        clustering_distance_rows = "pearson",    # or "spearman", "euclidean"
        clustering_method_rows = "ward.D2",      # or "complete", "average"
        clustering_distance_columns = "euclidean",
        clustering_method_columns = "complete")

# Use pre-computed dendrogram
row_dend <- hclust(dist(mat))
Heatmap(mat, cluster_rows = row_dend)

# Disable clustering
Heatmap(mat,
        cluster_rows = FALSE,
        cluster_columns = FALSE)
```

### Adding Significance Marks

```r
# Add significance indicators
pvalue_mat <- matrix(runif(200), nrow = 20, ncol = 10)

# Layer function to add marks
Heatmap(mat,
        cell_fun = function(j, i, x, y, width, height, fill) {
          if(pvalue_mat[i, j] < 0.05) {
            grid.text("*", x, y, gp = gpar(fontsize = 10))
          }
          if(pvalue_mat[i, j] < 0.01) {
            grid.text("**", x, y, gp = gpar(fontsize = 10))
          }
        })
```

### Saving ComplexHeatmap

```r
# PDF (vector)
pdf("heatmap.pdf", width = 10, height = 8)
draw(ht)
dev.off()

# PNG (raster)
png("heatmap.png", width = 10, height = 8, units = "in", res = 300)
draw(ht)
dev.off()

# With specific viewport
pdf("heatmap.pdf", width = 10, height = 8)
draw(ht, heatmap_legend_side = "right", annotation_legend_side = "bottom")
dev.off()
```

---

## EnhancedVolcano

### Installation

```r
BiocManager::install("EnhancedVolcano")
```

### Basic Volcano Plot

```r
library(EnhancedVolcano)

# Requires data frame with gene names, log2FC, and p-values
# Typically from DESeq2, edgeR, or limma results

EnhancedVolcano(res,
    lab = res$gene_symbol,
    x = 'log2FoldChange',
    y = 'pvalue',
    title = 'Treatment vs Control',
    pCutoff = 0.05,
    FCcutoff = 1.0)
```

### Customized Volcano Plot

```r
EnhancedVolcano(res,
    lab = res$gene_symbol,
    x = 'log2FoldChange',
    y = 'padj',  # Use adjusted p-values
    title = 'Differential Expression',
    subtitle = 'Treatment vs Control',
    caption = paste0('Total genes: ', nrow(res)),

    # Thresholds
    pCutoff = 0.05,
    FCcutoff = 1.0,

    # Aesthetics
    pointSize = 2.0,
    labSize = 3.0,
    labCol = 'black',
    labFace = 'bold',

    # Colors
    col = c('grey30', 'forestgreen', 'royalblue', 'red2'),
    colAlpha = 0.5,

    # Legend
    legendPosition = 'right',
    legendLabSize = 12,
    legendIconSize = 4.0,

    # Axis
    xlim = c(-6, 6),
    ylim = c(0, -log10(1e-12)),

    # Gridlines
    gridlines.major = FALSE,
    gridlines.minor = FALSE,

    # Border
    border = 'full',
    borderWidth = 1.0,
    borderColour = 'black')
```

### Highlighting Specific Genes

```r
# Highlight specific genes of interest
genes_of_interest <- c("TP53", "BRCA1", "MYC", "EGFR")

EnhancedVolcano(res,
    lab = res$gene_symbol,
    x = 'log2FoldChange',
    y = 'padj',
    selectLab = genes_of_interest,
    drawConnectors = TRUE,
    widthConnectors = 0.5,
    colConnectors = 'black',
    max.overlaps = Inf)
```

### Custom Cutoff Lines

```r
EnhancedVolcano(res,
    lab = res$gene_symbol,
    x = 'log2FoldChange',
    y = 'padj',
    pCutoff = 0.01,
    FCcutoff = 2.0,

    # Custom cutoff line styles
    cutoffLineType = 'dashed',
    cutoffLineCol = 'black',
    cutoffLineWidth = 0.5,

    # Horizontal line only (p-value)
    hline = c(0.05, 0.01, 0.001),
    hlineCol = c('grey', 'black', 'black'),
    hlineType = c('dashed', 'dashed', 'dotted'),
    hlineWidth = c(0.5, 0.5, 1.0))
```

---

## ggpubr

### Installation

```r
install.packages("ggpubr")
```

### Quick Publication-Ready Plots

```r
library(ggpubr)

# Boxplot with jitter and comparisons
ggboxplot(df, x = "group", y = "value",
          color = "group",
          palette = "jco",
          add = "jitter") +
  stat_compare_means(method = "anova") +
  stat_compare_means(comparisons = list(c("A", "B"), c("B", "C")),
                     method = "t.test",
                     label = "p.signif")

# Violin plot
ggviolin(df, x = "group", y = "value",
         fill = "group",
         palette = "npg",
         add = "boxplot",
         add.params = list(fill = "white"))

# Dotplot (Cleveland dot plot)
ggdotchart(df, x = "name", y = "value",
           color = "group",
           palette = "lancet",
           sorting = "descending",
           add = "segments",
           rotate = TRUE,
           dot.size = 6)
```

### Statistical Comparisons

```r
# Compare means with automatic test selection
ggboxplot(df, x = "group", y = "value") +
  stat_compare_means()  # Kruskal-Wallis by default

# Pairwise comparisons
my_comparisons <- list(c("Control", "Treatment1"), c("Control", "Treatment2"))

ggboxplot(df, x = "group", y = "value") +
  stat_compare_means(comparisons = my_comparisons,
                     method = "wilcox.test",
                     label = "p.format")  # or "p.signif" for stars

# Reference group comparisons
ggboxplot(df, x = "group", y = "value") +
  stat_compare_means(ref.group = "Control",
                     method = "t.test",
                     label = "p.signif")
```

### Correlation Plots

```r
# Scatter with correlation
ggscatter(df, x = "var1", y = "var2",
          add = "reg.line",
          conf.int = TRUE,
          cor.coef = TRUE,
          cor.method = "pearson")

# With marginal density
ggscatterhist(df, x = "var1", y = "var2",
              color = "group",
              margin.params = list(fill = "group"))
```

### Arranging Multiple Plots

```r
# Arrange plots
p1 <- ggboxplot(df, x = "group", y = "value1")
p2 <- ggboxplot(df, x = "group", y = "value2")
p3 <- ggscatter(df, x = "value1", y = "value2")

ggarrange(p1, p2, p3,
          labels = c("A", "B", "C"),
          ncol = 2, nrow = 2,
          common.legend = TRUE,
          legend = "bottom")
```

---

## clusterProfiler Visualization

### Installation

```r
BiocManager::install("clusterProfiler")
BiocManager::install("enrichplot")
```

### Enrichment Plots

```r
library(clusterProfiler)
library(enrichplot)

# After running enrichGO or enrichKEGG
# ego <- enrichGO(gene = genes, OrgDb = org.Hs.eg.db, ont = "BP")

# Dot plot
dotplot(ego, showCategory = 20)

# Bar plot
barplot(ego, showCategory = 20)

# Enrichment map (network)
emapplot(pairwise_termsim(ego))

# Category-gene network
cnetplot(ego, categorySize = "pvalue")

# Heatmap of enriched terms
heatplot(ego, foldChange = geneList)

# Upset plot
upsetplot(ego)
```

### GSEA Plots

```r
# After running GSEA
# gseaResult <- gseGO(geneList, OrgDb = org.Hs.eg.db, ont = "BP")

# Ridge plot
ridgeplot(gseaResult)

# GSEA enrichment plot for single term
gseaplot2(gseaResult, geneSetID = 1:3, pvalue_table = TRUE)

# Ranked gene list plot
gsearank(gseaResult, geneSetID = 1)
```

---

## ggbio (Genome Visualization)

### Installation

```r
BiocManager::install("ggbio")
```

### Ideogram

```r
library(ggbio)
library(biovizBase)

# Ideogram
autoplot(Homo.sapiens, which = GRanges("chr1", IRanges(1, 1e8)))

# Circular ideogram
p <- ggbio() + circle(Homo.sapiens, geom = "ideo", fill = "gray70")
p + circle(Homo.sapiens, geom = "scale", size = 2)
```

### Track Plots

```r
# Gene model
autoplot(txdb, which = gene_range, names.expr = "gene_id")

# Coverage
autoplot(bam_file, which = region, stat = "coverage")

# Combine tracks
tracks(
  Ideogram = autoplot(seqinfo),
  Coverage = autoplot(bam, stat = "coverage"),
  Genes = autoplot(txdb, which = range)
)
```

---

## Color Palettes for Bioinformatics

### ggsci Palettes

```r
library(ggsci)

# Journal palettes
ggplot(df, aes(x, y, color = group)) +
  geom_point() +
  scale_color_npg()      # Nature Publishing Group
  # scale_color_lancet()  # Lancet
  # scale_color_nejm()    # NEJM
  # scale_color_jco()     # Journal of Clinical Oncology
  # scale_color_aaas()    # Science

# Get palette colors for ComplexHeatmap
npg_colors <- pal_npg()(10)
```

### Color Schemes for Heatmaps

```r
library(circlize)

# Diverging (centered at 0)
col_fun <- colorRamp2(c(-2, 0, 2), c("blue", "white", "red"))

# Sequential
col_fun <- colorRamp2(c(0, 50, 100), c("white", "orange", "red"))

# Viridis (colorblind-friendly)
col_fun <- colorRamp2(seq(0, 1, length = 100), viridis::viridis(100))
```

---

## Publication Export

### Standard Workflow

```r
# 1. Create plot
library(ComplexHeatmap)
ht <- Heatmap(mat, name = "Expression")

# 2. Save to PDF (vector format)
pdf("figure1_heatmap.pdf", width = 8, height = 10)
draw(ht)
dev.off()

# 3. Save to TIFF (raster, some journals require)
tiff("figure1_heatmap.tiff", width = 8, height = 10,
     units = "in", res = 300, compression = "lzw")
draw(ht)
dev.off()
```

### Figure Size Guidelines

| Journal | Column Width | Two-Column | Full Page |
|---------|-------------|------------|-----------|
| Nature | 89 mm | 183 mm | 247 mm (height) |
| Cell | 85 mm | 174 mm | 228 mm |
| Science | 85 mm | 174 mm | 228 mm |

---

## Cross-References

- **[ggplot2.md](ggplot2.md)**: Base R visualization with ggplot2
- **[volcano_plots.md](volcano_plots.md)**: Detailed volcano plot guide
- **[heatmaps.md](heatmaps.md)**: Comprehensive heatmap tutorial
- **[survival_curves.md](survival_curves.md)**: Kaplan-Meier and survival plots
- **[seaborn.md](seaborn.md)**: Python alternative for statistical plots
