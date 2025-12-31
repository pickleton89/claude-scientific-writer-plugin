# ggplot2 Reference for Scientific Figures

> Comprehensive guide to R's ggplot2 for publication-quality scientific visualizations
> Based on Grammar of Graphics principles

---

## Quick Start

```r
library(ggplot2)

# Basic pattern
ggplot(data, aes(x = var1, y = var2)) +
  geom_point() +
  theme_minimal() +
  labs(title = "Title", x = "X Label", y = "Y Label")

# Save for publication
ggsave("figure.pdf", width = 7, height = 5, units = "in", dpi = 300)
```

---

## Grammar of Graphics Components

### Core Structure

Every ggplot2 figure is built from layers:

```r
ggplot(data, aes(...)) +    # 1. Data and aesthetic mappings
  geom_*() +                 # 2. Geometric objects
  stat_*() +                 # 3. Statistical transformations
  scale_*() +                # 4. Scale adjustments
  coord_*() +                # 5. Coordinate system
  facet_*() +                # 6. Faceting (small multiples)
  theme_*()                  # 7. Visual styling
```

### Component Reference

| Component | Purpose | Examples |
|-----------|---------|----------|
| `data` | The dataset | `ggplot(df, ...)` |
| `aes()` | Map variables to visual properties | `aes(x = time, y = value, color = group)` |
| `geom_*` | What to draw | `geom_point()`, `geom_line()`, `geom_boxplot()` |
| `stat_*` | Statistical transformations | `stat_smooth()`, `stat_summary()` |
| `scale_*` | Modify axes, colors, sizes | `scale_color_manual()`, `scale_y_log10()` |
| `coord_*` | Coordinate system | `coord_flip()`, `coord_polar()` |
| `facet_*` | Multi-panel layouts | `facet_wrap(~group)`, `facet_grid(row~col)` |
| `theme_*` | Visual appearance | `theme_minimal()`, `theme_classic()` |

---

## Aesthetic Mappings (aes)

### Common Aesthetics

| Aesthetic | Maps to | Typical Use |
|-----------|---------|-------------|
| `x`, `y` | Position | Continuous or categorical variables |
| `color` | Outline/line color | Group differentiation |
| `fill` | Interior color | Bar/box fill |
| `size` | Point/line size | Continuous third variable |
| `shape` | Point shape | Categorical grouping (max ~6 shapes) |
| `alpha` | Transparency | Overlapping points |
| `linetype` | Line pattern | Categorical grouping |
| `group` | Grouping for lines | Connect points within groups |

### Inside vs Outside aes()

```r
# Variable-dependent (INSIDE aes)
geom_point(aes(color = treatment))  # Color varies by treatment

# Fixed value (OUTSIDE aes)
geom_point(color = "red")           # All points red
```

---

## Geoms Reference

### Point and Line Plots

```r
# Scatter plot
geom_point(size = 3, alpha = 0.7)

# Line plot (connects in data order)
geom_line(linewidth = 1)

# Path (connects in x order)
geom_path()

# Smooth line with confidence interval
geom_smooth(method = "lm", se = TRUE)
geom_smooth(method = "loess", span = 0.3)

# Points with connecting lines
geom_point() + geom_line()
```

### Distribution Plots

```r
# Histogram
geom_histogram(bins = 30, fill = "steelblue", color = "white")

# Density
geom_density(fill = "steelblue", alpha = 0.5)

# Combined histogram and density
geom_histogram(aes(y = after_stat(density)), bins = 30) +
geom_density(color = "red", linewidth = 1)

# Boxplot
geom_boxplot(outlier.shape = NA)  # Hide outliers if adding jitter

# Violin plot
geom_violin(trim = FALSE) +
geom_boxplot(width = 0.1)  # Combine with narrow boxplot

# Jittered points
geom_jitter(width = 0.2, height = 0, alpha = 0.5)

# Beeswarm (requires ggbeeswarm)
ggbeeswarm::geom_beeswarm()
```

### Bar and Column Plots

```r
# Count data (stat = "count" is default)
geom_bar()

# Pre-computed values (stat = "identity")
geom_col()  # or geom_bar(stat = "identity")

# Stacked bars
geom_col(position = "stack")

# Dodged (side-by-side) bars
geom_col(position = position_dodge(width = 0.9))

# Error bars
geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0.2)

# Pointrange (mean with error bars)
geom_pointrange(aes(ymin = lower, ymax = upper))
```

### Heatmaps and Tiles

```r
# Basic heatmap
geom_tile(aes(fill = value))

# With borders
geom_tile(aes(fill = value), color = "white", linewidth = 0.5)

# Raster (faster for large data)
geom_raster(aes(fill = value))
```

### Text and Annotations

```r
# Text labels
geom_text(aes(label = name), size = 3, vjust = -0.5)

# Labels with background
geom_label(aes(label = name), size = 3)

# Repel overlapping labels (ggrepel package)
ggrepel::geom_text_repel(aes(label = name), max.overlaps = 20)
ggrepel::geom_label_repel(aes(label = name))

# Annotations (not mapped to data)
annotate("text", x = 5, y = 10, label = "Important", size = 5)
annotate("rect", xmin = 2, xmax = 4, ymin = 0, ymax = 10, alpha = 0.2)
annotate("segment", x = 1, xend = 3, y = 5, yend = 8, arrow = arrow())
```

---

## Scales

### Axis Scales

```r
# Log transformation
scale_x_log10()
scale_y_log10()
scale_y_log10(labels = scales::label_log())

# Square root
scale_y_sqrt()

# Reverse axis
scale_y_reverse()

# Custom breaks and labels
scale_x_continuous(
  breaks = c(0, 50, 100),
  labels = c("Low", "Medium", "High"),
  limits = c(0, 100)
)

# Date axis
scale_x_date(date_breaks = "1 month", date_labels = "%b %Y")

# Discrete with custom order
scale_x_discrete(limits = c("Control", "Treatment1", "Treatment2"))
```

### Color Scales

```r
# Continuous color
scale_color_gradient(low = "blue", high = "red")
scale_fill_gradient2(low = "blue", mid = "white", high = "red", midpoint = 0)
scale_fill_viridis_c(option = "plasma")  # Colorblind-friendly

# Discrete color
scale_color_manual(values = c("Control" = "gray", "Treatment" = "red"))
scale_fill_brewer(palette = "Set2")      # ColorBrewer palettes
scale_color_viridis_d()                   # Colorblind-friendly discrete

# Scientific palettes (ggsci package)
ggsci::scale_color_npg()      # Nature Publishing Group
ggsci::scale_color_lancet()   # Lancet
ggsci::scale_color_jco()      # Journal of Clinical Oncology
ggsci::scale_fill_nejm()      # NEJM
```

### Size and Shape Scales

```r
# Size range
scale_size_continuous(range = c(1, 10))
scale_size_area(max_size = 10)  # Area proportional to value

# Custom shapes
scale_shape_manual(values = c(16, 17, 15, 18))  # Filled shapes
```

---

## Faceting

### facet_wrap

```r
# Single variable
facet_wrap(~condition, ncol = 3)
facet_wrap(~condition, nrow = 2)

# Free scales (each panel has own axis limits)
facet_wrap(~condition, scales = "free")
facet_wrap(~condition, scales = "free_y")  # Only y-axis free

# Label formatting
facet_wrap(~condition, labeller = label_both)  # Shows "condition: A"
```

### facet_grid

```r
# Two-variable grid
facet_grid(rows = vars(treatment), cols = vars(timepoint))
facet_grid(treatment ~ timepoint)  # Formula notation

# Free scales
facet_grid(treatment ~ timepoint, scales = "free", space = "free")
```

---

## Themes

### Built-in Themes

```r
theme_gray()      # Default gray background
theme_bw()        # White background with grid
theme_minimal()   # Minimal, no box
theme_classic()   # Classic axis lines, no grid
theme_void()      # Empty (for maps, diagrams)
theme_dark()      # Dark background
```

### Publication-Ready Theme

```r
theme_publication <- function(base_size = 12, base_family = "Arial") {
  theme_classic(base_size = base_size, base_family = base_family) %+replace%
  theme(
    # Text elements
    axis.text = element_text(color = "black", size = base_size * 0.9),
    axis.title = element_text(color = "black", size = base_size, face = "bold"),
    plot.title = element_text(size = base_size * 1.2, face = "bold", hjust = 0),
    plot.subtitle = element_text(size = base_size, hjust = 0),

    # Axis elements
    axis.line = element_line(color = "black", linewidth = 0.5),
    axis.ticks = element_line(color = "black", linewidth = 0.5),

    # Legend
    legend.position = "right",
    legend.background = element_blank(),
    legend.key = element_blank(),
    legend.title = element_text(face = "bold"),

    # Facets
    strip.background = element_blank(),
    strip.text = element_text(face = "bold", size = base_size),

    # Panel
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    panel.background = element_blank(),

    # Plot margins
    plot.margin = margin(10, 10, 10, 10)
  )
}
```

### Common Theme Modifications

```r
theme(
  # Remove legend
  legend.position = "none",

  # Move legend
  legend.position = "bottom",
  legend.position = c(0.8, 0.2),  # Inside plot (0-1 coordinates)

  # Rotate x-axis labels
  axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1),

  # Remove axis titles
  axis.title.x = element_blank(),

  # Bold titles
  axis.title = element_text(face = "bold"),

  # Panel border
  panel.border = element_rect(color = "black", fill = NA, linewidth = 1),

  # Grid lines
  panel.grid.major = element_line(color = "grey90", linewidth = 0.3),

  # Facet spacing
  panel.spacing = unit(1, "lines")
)
```

---

## Common Bioinformatics Plots

### Expression Boxplot with Points

```r
ggplot(expr_data, aes(x = condition, y = expression, fill = condition)) +
  geom_boxplot(outlier.shape = NA, alpha = 0.7) +
  geom_jitter(width = 0.2, alpha = 0.5, size = 1.5) +
  scale_fill_brewer(palette = "Set2") +
  labs(
    x = "Condition",
    y = "Expression (log2 TPM)",
    title = "Gene Expression by Condition"
  ) +
  theme_publication() +
  theme(legend.position = "none")
```

### PCA Plot with Ellipses

```r
ggplot(pca_df, aes(x = PC1, y = PC2, color = condition, shape = batch)) +
  geom_point(size = 3, alpha = 0.8) +
  stat_ellipse(level = 0.95, linetype = "dashed") +
  scale_color_manual(values = c("Control" = "#1f77b4", "Treatment" = "#d62728")) +
  labs(
    x = paste0("PC1 (", round(var_explained[1], 1), "%)"),
    y = paste0("PC2 (", round(var_explained[2], 1), "%)"),
    color = "Condition",
    shape = "Batch"
  ) +
  theme_publication() +
  coord_fixed()  # Equal aspect ratio
```

### Bar Plot with Error Bars

```r
# Summarize data first
summary_df <- df %>%
  group_by(condition) %>%
  summarize(
    mean = mean(value),
    se = sd(value) / sqrt(n()),
    .groups = "drop"
  )

ggplot(summary_df, aes(x = condition, y = mean, fill = condition)) +
  geom_col(width = 0.7, alpha = 0.8) +
  geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0.2) +
  scale_fill_manual(values = c("Control" = "gray50", "Treatment" = "steelblue")) +
  labs(x = "Condition", y = "Mean Value (+/- SE)") +
  theme_publication() +
  theme(legend.position = "none")
```

### Correlation Plot

```r
ggplot(df, aes(x = var1, y = var2)) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "lm", color = "red", se = TRUE) +
  stat_cor(method = "pearson", label.x.npc = "left", label.y.npc = "top") +  # ggpubr
  labs(
    x = "Variable 1",
    y = "Variable 2",
    title = "Correlation Analysis"
  ) +
  theme_publication()
```

### Faceted Time Course

```r
ggplot(timecourse_df, aes(x = time, y = expression, color = gene)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  facet_wrap(~treatment, ncol = 2) +
  scale_color_viridis_d() +
  labs(
    x = "Time (hours)",
    y = "Relative Expression",
    color = "Gene"
  ) +
  theme_publication()
```

---

## Combining Plots

### patchwork Package

```r
library(patchwork)

# Side by side
p1 + p2

# Stacked
p1 / p2

# Complex layouts
(p1 | p2) / p3

# With labels
(p1 + p2 + p3) + plot_annotation(tag_levels = 'A')

# Adjust relative sizes
p1 + p2 + plot_layout(widths = c(2, 1))

# Collect legends
(p1 + p2) + plot_layout(guides = "collect")
```

### cowplot Package

```r
library(cowplot)

# Combine plots
plot_grid(p1, p2, p3, labels = c("A", "B", "C"), ncol = 3)

# Inset plot
ggdraw() +
  draw_plot(main_plot) +
  draw_plot(inset_plot, x = 0.6, y = 0.6, width = 0.35, height = 0.35)
```

---

## Saving Figures

### ggsave Options

```r
# Vector formats (preferred for publications)
ggsave("figure.pdf", plot = p, width = 7, height = 5, units = "in")
ggsave("figure.svg", plot = p, width = 180, height = 120, units = "mm")
ggsave("figure.eps", plot = p, width = 7, height = 5, device = cairo_ps)

# Raster formats
ggsave("figure.png", plot = p, width = 7, height = 5, dpi = 300)
ggsave("figure.tiff", plot = p, width = 7, height = 5, dpi = 300, compression = "lzw")

# High-resolution for posters
ggsave("figure_poster.png", plot = p, width = 20, height = 15, dpi = 600)
```

### Journal-Specific Sizes

| Journal | Single Column | Double Column | Full Page |
|---------|---------------|---------------|-----------|
| Nature | 89 mm | 183 mm | — |
| Science | 85 mm | 174 mm | 228 mm |
| PNAS | 87 mm | 178 mm | 178 mm |
| Cell | 85 mm | 174 mm | — |

```r
# Example for Nature single-column figure
ggsave("figure.pdf", width = 89, height = 60, units = "mm")
```

---

## Extensions for Scientific Figures

### Essential Packages

```r
# Statistics and annotations
library(ggpubr)      # stat_compare_means(), stat_cor()
library(ggsignif)    # Significance brackets

# Text and labels
library(ggrepel)     # Non-overlapping labels

# Colors
library(ggsci)       # Journal color palettes
library(viridis)     # Colorblind-friendly

# Arrangement
library(patchwork)   # Combine plots
library(cowplot)     # Publication-ready themes

# Specialized
library(ggbeeswarm)  # Beeswarm plots
library(ggridges)    # Ridge plots
library(ggforce)     # Extended geoms (circles, arcs, zooms)
```

### Adding Significance

```r
library(ggpubr)

# Automatic pairwise comparisons
ggplot(df, aes(x = group, y = value)) +
  geom_boxplot() +
  stat_compare_means(comparisons = list(c("A", "B"), c("B", "C")),
                     method = "t.test",
                     label = "p.signif")  # or "p.format" for values

# Global test
ggplot(df, aes(x = group, y = value)) +
  geom_boxplot() +
  stat_compare_means(method = "anova")  # Kruskal for non-parametric
```

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Legend overlaps plot | `theme(legend.position = "bottom")` |
| Labels overlap | Use `ggrepel::geom_text_repel()` |
| X-axis labels overlap | `theme(axis.text.x = element_text(angle = 45, hjust = 1))` |
| Colors too similar | Use `scale_color_viridis_d()` or manual palette |
| Plot too crowded | Increase figure size or use faceting |
| Axis limits cut off data | `coord_cartesian(ylim = c(0, 100))` instead of `scale_y_continuous(limits = ...)` |

### Missing Data Handling

```r
# Remove NA before plotting
ggplot(df %>% filter(!is.na(value)), aes(x = x, y = value))

# Or let ggplot handle it (warns by default)
ggplot(df, aes(x = x, y = value)) +
  geom_point(na.rm = TRUE)  # Suppress warning
```

---

## Cross-References

- **[matplotlib.md](matplotlib.md)**: Python equivalent for matplotlib users
- **[seaborn.md](seaborn.md)**: Python statistical visualization
- **[bioconductor_viz.md](bioconductor_viz.md)**: Specialized bioinformatics R packages
- **[volcano_plots.md](volcano_plots.md)**: Differential expression visualization
- **[heatmaps.md](heatmaps.md)**: Expression heatmaps
- **[../visual-design/SKILL.md](../../visual-design/SKILL.md)**: Design principles for publications
