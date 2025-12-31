---
name: plotting-libraries
version: 1.4.0
description: "Data visualization for scientific research using Python (matplotlib, seaborn) or R (ggplot2, Bioconductor)"
when_to_use: "Creating plots, charts, figures, visualizations, heatmaps, volcano plots, survival curves, genome tracks, PCA/UMAP, correlation matrices, forest plots, or any scientific figure for publication"
extends: visual-design
quantification-reference: "../QUANTIFICATION_THRESHOLDS.md"
---

> **Quantified Thresholds:** This skill references shared thresholds from [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §2 (Visual Quality), §7.2 (Figure Quality Rubric), and §9 (Figure & Plot Quality).

> **Design Foundation:** This skill extends `visual-design` for design philosophy, typography principles, color theory, and publication specifications. See [visual-design](../visual-design/SKILL.md) for the foundational design layer.

<objective>
Guide effective use of data visualization libraries for creating publication-quality scientific figures. This skill provides decision frameworks for choosing between Python and R libraries, common patterns for bioinformatics visualizations, and links to detailed reference documentation.
</objective>

<quick_start>
**Choose your ecosystem:**

| Preference | Ecosystem | Primary Libraries |
|------------|-----------|-------------------|
| Python-centric workflow | Python | matplotlib, seaborn |
| Statistical graphics, publications | R | ggplot2, Bioconductor |
| Bioinformatics (omics data) | Either | See specialized guides below |

**Quick patterns:**

Python (matplotlib/seaborn):
```python
import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='group', y='value', ax=ax)
plt.savefig('figure.pdf', dpi=300, bbox_inches='tight')
```

R (ggplot2):
```r
library(ggplot2)

ggplot(df, aes(x = group, y = value, fill = group)) +
  geom_boxplot() +
  theme_classic()
ggsave("figure.pdf", width = 7, height = 5)
```
</quick_start>

<prerequisites>
## Required Packages

**Python (core):**
```bash
pip install matplotlib seaborn numpy pandas
```

**Python (statistical annotations):**
```bash
pip install statannotations scipy statsmodels
```

**Python (bioinformatics):**
```bash
pip install adjustText lifelines pyGenomeTracks scanpy
```

**R (core):**
```r
install.packages(c("ggplot2", "ggpubr", "patchwork", "corrplot", "ggsci"))
```

**R (Bioconductor):**
```r
if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install(c("ComplexHeatmap", "EnhancedVolcano", "survminer", "Gviz", "clusterProfiler"))
```
</prerequisites>

<decision_framework>
## Python vs R Decision

| Factor | Python | R |
|--------|--------|---|
| Existing codebase | Already using Python | Already using R |
| Statistical plots | seaborn adequate | ggplot2 preferred |
| Publication quality | Good with effort | Excellent defaults |
| Bioinformatics packages | pyGenomeTracks, scanpy | Bioconductor (ComplexHeatmap, etc.) |
| Learning curve | Lower for programmers | Lower for statisticians |

## Python Library Selection

**Start with seaborn when:**
- Working with pandas DataFrames
- Need statistical estimation (means, confidence intervals, regression)
- Creating distribution plots (histplot, kdeplot, violinplot)
- Want faceted/small-multiple layouts quickly
- Exploring data (pairplot, jointplot)

**Start with matplotlib when:**
- Need pixel-level control over layout
- Creating non-standard plot types
- Building complex multi-panel figures with different plot types
- Animating visualizations
- Embedding in GUI applications

**Use both together when:**
- seaborn creates the base plot, matplotlib fine-tunes it
- Need statistical analysis AND custom annotations
- Creating publication-quality figures

## R Library Selection

**ggplot2 for:**
- Most statistical visualizations
- Publication-quality figures
- Consistent grammar of graphics approach
- Extensive customization via themes

**Bioconductor packages for:**
- ComplexHeatmap: Advanced expression heatmaps
- EnhancedVolcano: Differential expression volcano plots
- survminer: Kaplan-Meier survival curves
- Gviz: Genome track visualization
- clusterProfiler/enrichplot: Enrichment analysis plots

</decision_framework>

<bioinformatics_plots>
## Specialized Bioinformatics Visualizations

| Plot Type | Python | R | Reference |
|-----------|--------|---|-----------|
| Volcano plot | matplotlib + adjustText | EnhancedVolcano, ggplot2 | [{baseDir}/references/volcano_plots.md]({baseDir}/references/volcano_plots.md) |
| Expression heatmap | seaborn clustermap | ComplexHeatmap, pheatmap | [{baseDir}/references/heatmaps.md]({baseDir}/references/heatmaps.md) |
| Survival curves | lifelines | survminer | [{baseDir}/references/survival_curves.md]({baseDir}/references/survival_curves.md) |
| Genome tracks | pyGenomeTracks | Gviz | [{baseDir}/references/genome_tracks.md]({baseDir}/references/genome_tracks.md) |
| PCA/UMAP | matplotlib, scanpy | ggplot2 | See respective guides |

**When to use which:**

| Visualization Need | Recommended Tool |
|-------------------|------------------|
| Differential expression results | EnhancedVolcano (R) or volcano_plots.md patterns (Python) |
| Gene expression clustering | ComplexHeatmap (R) for publication, seaborn clustermap for exploration |
| Clinical survival analysis | survminer (R) for risk tables |
| Multi-omics integration | ComplexHeatmap (R) for multiple linked heatmaps |
| Genome browser views | pyGenomeTracks (Python) or Gviz (R) |

</bioinformatics_plots>

<statistical_visualization>
## Visualizing Statistical Results

Coordinate with **statistical-analysis** skill for test selection.

For complete implementation patterns, see **[{baseDir}/references/statistical_visualization.md]({baseDir}/references/statistical_visualization.md)**.

| Visualization | Python | R |
|--------------|--------|---|
| Group comparisons | seaborn boxplot + stripplot | ggpubr stat_compare_means |
| Q-Q plots | scipy.stats.probplot | ggplot2 stat_qq |
| Regression diagnostics | statsmodels.graphics | ggfortify autoplot |
| Correlation matrices | seaborn heatmap | corrplot |
| Forest plots | matplotlib errorbar | ggplot2 geom_errorbarh |

**Key packages:** `statannotations` (Python), `ggpubr` (R) for significance annotations.
</statistical_visualization>

<common_patterns>
**Combined Python workflow (publications):**
```python
import seaborn as sns
import matplotlib.pyplot as plt

# seaborn for statistical plot
fig, ax = plt.subplots(figsize=(8, 6))
sns.boxplot(data=df, x='group', y='value', ax=ax)

# matplotlib for customization
ax.set_title('Distribution by Group', fontsize=14, fontweight='bold')
ax.set_xlabel('Experimental Group', fontsize=12)
ax.set_ylabel('Measurement (units)', fontsize=12)

# Add custom elements
ax.axhline(y=threshold, color='red', linestyle='--', label='Threshold')
ax.legend()

plt.tight_layout()
plt.savefig('figure.pdf', dpi=300, bbox_inches='tight')
```

**R publication workflow:**
```r
library(ggplot2)
library(ggpubr)

ggplot(df, aes(x = group, y = value, fill = group)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.5) +
  stat_compare_means(method = "anova") +
  labs(x = "Group", y = "Value") +
  theme_classic() +
  theme(legend.position = "none")

ggsave("figure.pdf", width = 7, height = 5)
```

**Export for publications:**
```python
# Vector format (scalable, required by most journals)
plt.savefig('figure.pdf', bbox_inches='tight')
plt.savefig('figure.svg', bbox_inches='tight')

# Raster format (presentations, web)
plt.savefig('figure.png', dpi=300, bbox_inches='tight')
```

```r
# Vector format
ggsave("figure.pdf", width = 180, height = 120, units = "mm")

# Raster format
ggsave("figure.png", width = 7, height = 5, dpi = 300)
```
</common_patterns>

<styling_integration>
## Brand Integration

For scientific figures requiring organizational brand compliance, load brand tokens before plotting.

### Oligon Brand (recommended)

**Python (matplotlib/seaborn):**
```python
# Option 1: Use the adapter (recommended)
import sys
sys.path.insert(0, 'skills/oligon-brand')
from adapters.matplotlib_adapter import set_brand_style, BRAND_COLORS, get_cycle

# Apply brand defaults
set_brand_style('treatment_control')

# Access specific colors
highlight_color = BRAND_COLORS['brand_blue']  # #2DB2E8

# Or use specific cycle
colors = get_cycle('opposing')  # ['#2DB2E8', '#E8622D', '#222222']
```

**Option 2: Load tokens directly:**
```python
import json
from pathlib import Path

tokens_path = Path('skills/oligon-brand/tokens/brand-tokens.json')
with open(tokens_path) as f:
    brand = json.load(f)

# Access colors
brand_blue = brand['colors']['primary']['brand_blue']['hex']  # #2DB2E8
cycle = brand['color_cycles']['treatment_control']['colors']
```

**Option 3: Use mplstyle file:**
```python
import matplotlib.pyplot as plt

# If installed to matplotlib config
plt.style.use('oligon_color_brand')

# Or load directly
plt.style.use('skills/oligon-brand/assets/oligon_color_brand.mplstyle')
```

**R (ggplot2):**
```r
source('skills/oligon-brand/adapters/ggplot2_adapter.R')

# Apply brand theme
ggplot(df, aes(x, y, color = group)) +
  geom_point() +
  scale_color_oligon('treatment_control') +
  theme_oligon()
```

### Generic Brand Integration

For non-Oligon projects or custom brands:

```python
# Define your own brand colors
BRAND_COLORS = {
    'primary': '#YOUR_COLOR',
    'secondary': '#YOUR_COLOR',
    'accent': '#YOUR_COLOR',
}

# Apply to seaborn
import seaborn as sns
sns.set_palette(list(BRAND_COLORS.values()))
```

### Journal Palettes (R)

```r
# ggsci for journal palettes
library(ggsci)
ggplot(...) + scale_color_npg()  # Nature Publishing Group
ggplot(...) + scale_color_lancet()  # Lancet

# Manual colors
scale_fill_manual(values = c("Control" = "#222222", "Treatment" = "#2DB2E8"))
```

See `oligon-brand` skill for complete brand implementation patterns.
</styling_integration>

<reference_guides>
## Detailed Library Documentation

### Python
- **[{baseDir}/references/matplotlib.md]({baseDir}/references/matplotlib.md)**: Complete matplotlib reference—OO API, plot types, subplots, 3D, styling, saving
- **[{baseDir}/references/seaborn.md]({baseDir}/references/seaborn.md)**: Complete seaborn reference—statistical plots, figure-level vs axes-level, palettes, theming

### R
- **[{baseDir}/references/ggplot2.md]({baseDir}/references/ggplot2.md)**: Complete ggplot2 reference—grammar of graphics, geoms, faceting, themes, publication export
- **[{baseDir}/references/bioconductor_viz.md]({baseDir}/references/bioconductor_viz.md)**: Bioconductor packages—ComplexHeatmap, EnhancedVolcano, ggpubr, clusterProfiler

### Bioinformatics-Specific
- **[{baseDir}/references/volcano_plots.md]({baseDir}/references/volcano_plots.md)**: Volcano plots for differential expression (Python + R)
- **[{baseDir}/references/heatmaps.md]({baseDir}/references/heatmaps.md)**: Expression heatmaps with clustering (Python + R)
- **[{baseDir}/references/survival_curves.md]({baseDir}/references/survival_curves.md)**: Kaplan-Meier and survival analysis (Python lifelines + R survminer)
- **[{baseDir}/references/genome_tracks.md]({baseDir}/references/genome_tracks.md)**: Genome visualization (pyGenomeTracks + Gviz)
</reference_guides>

<cross_references>
## Related Skills

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

- **[oligon-brand](../oligon-brand/SKILL.md)**: Brand colors and tokens—load before plotting for Oligon-branded figures. See `<styling_integration>` above for usage patterns.
- **[visual-design](../visual-design/SKILL.md)**: Design principles and publication specifications
- **[statistical-analysis](../statistical-analysis/SKILL.md)**: Statistics underlying visualizations—see `<statistical_visualization>` above for implementation patterns
- **[scientific-writing](../scientific-writing/SKILL.md)**: Figure legends and methods descriptions
- **[reproducible-research](../reproducible-research/SKILL.md)**: Environment management for reproducible figures
- **[code-documentation](../code-documentation/SKILL.md)**: Docstring patterns for plotting functions—see `visualization_documentation` section for templates
</cross_references>

<error_handling>
## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Figure not showing | Missing `plt.show()` or wrong backend | Use `%matplotlib inline` in Jupyter or call `plt.show()` |
| Empty figure saved | Called `plt.savefig()` after `plt.show()` | Save BEFORE showing: `plt.savefig()` then `plt.show()` |
| `SettingWithCopyWarning` | Modifying DataFrame view | Use `df = df.copy()` before modifications |
| Font not found | Missing system font | Use `plt.rcParams['font.family'] = 'sans-serif'` |
| Figure too large for PDF | High DPI raster in vector format | Reduce DPI or use `rasterized=True` for dense scatter plots |
| Truncated labels | Labels extend beyond figure bounds | Use `bbox_inches='tight'` in `savefig()` |
| Colorbar overlap | Default positioning conflicts | Use `fig.colorbar(im, ax=ax, shrink=0.8)` |
| R: `Error in grid.Call.graphics` | Plotting before device open | Run `dev.new()` or use `ggsave()` directly |
| R: Object not found in ggplot | Variable not in `aes()` | Check column names match DataFrame exactly |
| R: Facet labels cut off | Long labels exceed panel width | Use `labeller = label_wrap_gen(width = 15)` |

**Python debugging pattern:**
```python
# Check figure state before saving
print(f"Figure size: {fig.get_size_inches()}")
print(f"Number of axes: {len(fig.axes)}")
fig.savefig('debug.png', dpi=100)  # Quick preview
```

**R debugging pattern:**
```r
# Check plot object
p <- ggplot(...)
print(p)  # Renders to screen
ggsave("debug.png", p, width = 7, height = 5)
```
</error_handling>

<success_criteria>
> **Reference:** See [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §9 (Figure & Plot Quality) for detailed metrics.

**Quality Checklist:**
- [ ] Appropriate library/ecosystem chosen for the task
- [ ] Figure renders correctly with all elements visible
- [ ] Exported at appropriate resolution (≥300 DPI for print, ≥150 for web)
- [ ] Labels, legends, and titles are readable (≥7pt final size)
- [ ] Color palette is accessible (colorblind-safe)
- [ ] Vector format used for publications (PDF, SVG)
- [ ] Figure dimensions match journal requirements
- [ ] Error bars include measure type (SE, SD, 95% CI) and sample size
- [ ] No chart junk (unnecessary gridlines, borders, 3D effects)

**Validation Workflow:**
1. **Preview before saving**: Display figure to verify layout and content
2. **Test output file**: Re-open saved PDF/PNG to confirm no corruption or truncation
3. **Check dimensions**: Verify exported figure matches target dimensions (journal single-column: 89mm, double-column: 183mm)
4. **Colorblind accessibility**: Test with `pip install colorblindcheck` (Python) or `colorBlindness` (R)
5. **Final review**: Zoom to 100% to verify text readability at final print size
</success_criteria>
