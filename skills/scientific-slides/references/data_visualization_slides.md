# Data Visualization for Slides

## Overview

Effective data visualization in presentations differs fundamentally from journal figures. While publications prioritize comprehensive detail, presentation slides must emphasize clarity, impact, and immediate comprehension. This guide covers adapting figures for slides, choosing appropriate chart types, and avoiding common visualization mistakes.

## Key Principles for Presentation Figures

### 1. Simplify, Don't Replicate

**The Core Difference**:
- **Journal figures**: Dense, detailed, for careful study
- **Presentation figures**: Clear, simplified, for quick understanding

**Simplification Strategies**:

**Remove Non-Essential Elements**:
- ❌ Minor gridlines
- ❌ Detailed legends (label directly instead)
- ❌ Multiple panels (split into separate slides)
- ❌ Secondary axes (rarely work in presentations)
- ❌ Dense tick marks and minor labels

**Focus on Key Message**:
- Show only the data supporting your current point
- Subset data if full dataset is overwhelming
- Highlight the specific comparison you're discussing
- Remove context that isn't immediately relevant

**Example Transformation**:
```
Journal Figure:
- 6 panels (A-F)
- 4 experimental conditions per panel
- 50+ data points visible
- Complex statistical annotations
- Small font labels

Presentation Version:
- 3 separate slides (1-2 panels each)
- Focus on key comparison per slide
- Large, clear data representation
- One statistical result highlighted
- Large, readable labels
```

### 2. Emphasize Visual Hierarchy

**Guide Attention**:
- Make key result visually dominant
- De-emphasize background or comparison data
- Use size, color, and position strategically

**Techniques**:

**Color Emphasis**:
```
Main Result: Bold, saturated color (e.g., blue)
Comparison: Muted gray or desaturated color
Background: Very light gray or white
```

**Size Emphasis**:
```
Key line/bar: Thicker (3-4pt)
Reference lines: Thinner (1-2pt)
Grid lines: Very thin (0.5pt) or remove
```

**Annotation**:
```
Add text callouts: "34% increase" with arrow
Add shapes: Circle key region
Add color highlights: Background shading for important area
```

### 3. Maximize Readability

**Font Sizes for Presentations**:
- **Axis labels**: 18-24pt minimum
- **Tick labels**: 16-20pt minimum
- **Title**: 24-32pt
- **Legend**: 16-20pt (or label directly on plot)
- **Annotations**: 18-24pt

**The Distance Test**:
- If your figure isn't readable at 2-3 feet from your laptop screen, it won't work in a presentation
- Test by stepping back from screen
- Better to split into multiple simpler figures

**Line and Marker Sizes**:
- **Lines**: 2-4pt thickness (thicker than journal figures)
- **Markers**: 8-12pt size
- **Error bars**: 1.5-2pt thickness
- **Bars**: Adequate width with clear spacing

### 4. Use Progressive Disclosure

**Build Complex Figures Incrementally**:

Instead of showing complete figure at once:
1. **Baseline**: Show axes and basic setup
2. **Data Group 1**: Add first dataset
3. **Data Group 2**: Add comparison dataset
4. **Highlight**: Emphasize key difference
5. **Interpretation**: Add annotation with finding

**Benefits**:
- Controls audience attention
- Prevents information overload
- Guides interpretation
- Emphasizes narrative structure

**Implementation**:
- PowerPoint: Use animation to reveal layers
- Beamer: Use `\pause` or overlays
- Static: Create sequence of slides building the figure

## Chart Types and When to Use Them

### Bar Charts

**Best For**:
- Comparing discrete categories
- Showing counts or frequencies
- Highlighting differences between groups

**Presentation Optimization**:
```
✅ DO:
- Large, clear bars with adequate spacing
- Horizontal bars for long category names
- Direct labeling on bars (not legend)
- Order by value (highest to lowest) unless natural order exists
- Start y-axis at zero for accurate visual comparison

❌ DON'T:
- Too many categories (max 8-10)
- 3D bars (distorts perception)
- Multiple grouped comparisons (split to separate slides)
- Decorative patterns or gradients
```

**Example Enhancement**:
```
Before: 12 categories, small fonts, legend
After: Top 6 categories only, large fonts, direct labels, key bar highlighted
```

### Line Graphs

**Best For**:
- Trends over time
- Continuous data relationships
- Comparing trajectories

**Presentation Optimization**:
```
✅ DO:
- Thick lines (2-4pt)
- Distinct colors AND line styles (solid, dashed, dotted)
- Direct line labeling (at end of lines, not legend)
- Highlight key line with color/thickness
- Minimal gridlines or none
- Clear markers at data points

❌ DON'T:
- More than 4-5 lines per plot
- Similar colors (ensure high contrast)
- Small markers or thin lines
- Cluttered with excess gridlines
```

**Time Series Tips**:
- Mark key events or interventions with vertical lines
- Annotate important time points
- Use shaded regions for different phases

### Scatter Plots

**Best For**:
- Relationships between two variables
- Correlations
- Distributions
- Outliers

**Presentation Optimization**:
```
✅ DO:
- Large, distinct markers (8-12pt)
- Color code groups clearly
- Show trendline if discussing correlation
- Annotate key points (outliers, examples)
- Report R² or p-value directly on plot

❌ DON'T:
- Overplot (too many overlapping points)
- Small markers
- Multiple marker types that look similar
- Missing scale information
```

**Overplotting Solutions**:
- Transparency (alpha) for overlapping points
- Hexbin or density plots for very large datasets
- Random jitter for discrete data
- Marginal distributions on axes

### Box Plots / Violin Plots

**Best For**:
- Distribution comparisons
- Showing variability and outliers
- Multiple group comparisons

**Presentation Optimization**:
```
✅ DO:
- Large, clear boxes
- Color code groups
- Add individual data points if n is small (< 30)
- Annotate median or mean values
- Explain components (quartiles, whiskers) first time shown

❌ DON'T:
- Assume audience knows box plot conventions
- Use without brief explanation
- Too many groups (max 6-8)
- Omit axis labels and units
```

**First Use**:
If your audience may be unfamiliar, briefly explain: "Box shows middle 50% of data, line is median, whiskers show range"

### Heatmaps

**Best For**:
- Matrix data
- Gene expression or correlation patterns
- Large datasets with patterns

**Presentation Optimization**:
```
✅ DO:
- Large cells (readable grid)
- Clear, intuitive color scale (diverging or sequential)
- Label rows and columns with large fonts
- Show color scale legend prominently
- Cluster or order meaningfully
- Highlight key region with border

❌ DON'T:
- Too many rows/columns (200×200 matrix unreadable)
- Poor color scales (rainbow, red-green)
- Missing dendrograms if claiming clusters
- Tiny labels
```

**Simplification**:
- Show subset of most interesting rows/columns
- Zoom to relevant region
- Split large heatmap across multiple slides

### Network Diagrams

**Best For**:
- Relationships and connections
- Pathways and networks
- Hierarchical structures

**Presentation Optimization**:
```
✅ DO:
- Large nodes and labels
- Clear edge directionality (arrows)
- Color or size code importance
- Highlight path of interest
- Simplify to essential connections
- Use layout that minimizes crossing edges

❌ DON'T:
- Show entire complex network at once
- Hairball diagrams (too many connections)
- Small labels on nodes
- Unclear what nodes and edges represent
```

**Build Strategy**:
1. Show simplified structure
2. Add key nodes progressively
3. Highlight path or subnetwork of interest
4. Annotate with functional interpretation

### Statistical Plots

**Kaplan-Meier Survival Curves**:
```
✅ Optimize:
- Thick lines (3-4pt)
- Show confidence intervals as shaded regions
- Mark censored observations clearly
- Report hazard ratio and p-value on plot
- Extend axes to show full follow-up
```

**Forest Plots**:
```
✅ Optimize:
- Large markers (diamonds or squares)
- Clear confidence interval bars
- Large font for study names
- Highlight overall estimate
- Show line of no effect prominently
```

**ROC Curves**:
```
✅ Optimize:
- Thick curve line
- Show diagonal reference line (AUC = 0.5)
- Report AUC with confidence interval on plot
- Mark optimal threshold if discussing cutpoint
- Compare ≤ 3 curves per plot
```

## Color in Data Visualizations

### Sequential Color Scales

**When to Use**: Ordered data (low to high)

**Good Palettes**:
- Blues: Light blue → Dark blue
- Greens: Light green → Dark green  
- Grays: Light gray → Black
- Viridis: Yellow → Purple (perceptually uniform)

**Avoid**:
- Rainbow scales (non-uniform perception)
- Red-green scales (color blindness)

### Diverging Color Scales

**When to Use**: Data with meaningful midpoint (e.g., +/− change, correlation from -1 to +1)

**Good Palettes**:
- Blue → White → Red
- Purple → White → Orange
- Blue → Gray → Orange

**Key Principle**: Midpoint should be visually neutral (white or light gray)

### Categorical Colors

**When to Use**: Distinct groups with no order

**Good Practices**:
- Maximum 5-7 colors for clarity
- High contrast between adjacent categories
- Color-blind safe combinations
- Consistent color mapping across slides

**Example Set**:
```
Blue (#0173B2)
Orange (#DE8F05)
Green (#029E73)
Purple (#CC78BC)
Red (#CA3542)
```

### Highlight Colors

**Strategy**: Use color to direct attention

```
Main Result: Bright, saturated color (e.g., blue)
Comparison: Neutral (gray) or muted color
Background: Very light gray or white
```

**Example Application**:
- Bar chart: Key bar in blue, others in light gray
- Line plot: Main line in bold blue, reference lines in thin gray
- Scatter: Group of interest in color, others faded

## Common Visualization Mistakes

### Mistake 1: Overwhelming Complexity

**Problem**: Showing too much data at once

**Example**:
- Figure with 12 panels
- Each panel has 6 experimental conditions
- Tiny fonts and dense layout
- Audience has 10 seconds to process

**Solution**:
- Split into 3-4 slides
- One comparison per slide
- Focus on key result
- Build understanding progressively

### Mistake 2: Illegible Labels

**Problem**: Text too small to read

**Common Issues**:
- 8-10pt axis labels (need ≥18pt)
- Tiny legend text
- Subscripts and superscripts disappear
- Fine-print p-values

**Solution**:
- Recreate figures for presentation (don't use journal versions directly)
- Test readability from distance
- Remove or enlarge small text
- Put detailed statistics in notes

### Mistake 3: Chart Junk

**Problem**: Unnecessary decorative elements

**Examples**:
- 3D effects on 2D data
- Excessive gridlines
- Distracting backgrounds
- Decorative borders or shadows
- Animation for decoration only

**Solution**:
- Remove all non-data ink
- Maximize data-ink ratio
- Clean, minimal design
- Let data be the focus

### Mistake 4: Misleading Scales

**Problem**: Visual representation distorts data

**Examples**:
- Bar charts not starting at zero
- Truncated y-axes exaggerating differences
- Inconsistent scales between panels
- Log scales without clear labeling

**Solution**:
- Bar charts: Always start at zero
- Line charts: Can truncate, but make clear
- Label log scales explicitly
- Maintain consistent scales for comparisons

### Mistake 5: Poor Color Choices

**Problem**: Colors reduce clarity or accessibility

**Examples**:
- Red-green for color-blind audience
- Low contrast (yellow on white)
- Too many colors
- Inconsistent color meaning

**Solution**:
- Use color-blind safe palettes
- Test contrast (minimum 4.5:1)
- Limit to 5-7 colors maximum
- Consistent meaning across slides

### Mistake 6: Missing Context

**Problem**: Audience can't interpret visualization

**Missing Elements**:
- Axis labels or units
- Sample sizes (n)
- Error bar meaning (SEM vs SD vs CI)
- Statistical significance indicators
- Scale or reference points

**Solution**:
- Label everything clearly
- Define abbreviations
- Report key statistics on plot
- Provide reference for comparison

### Mistake 7: Inefficient Chart Type

**Problem**: Wrong visualization for data type

**Examples**:
- Pie chart for >5 categories (use bar chart)
- 3D pie chart (especially bad)
- Dual y-axes (confusing)
- Line plot for discrete categories (use bar chart)

**Solution**:
- Match chart type to data type
- Consider what comparison you're showing
- Choose format that makes pattern obvious
- Test if message is immediately clear

## Progressive Disclosure Techniques

### Building a Complex Figure

**Scenario**: Showing multi-panel experimental result

**Approach 1: Sequential Panels**
```
Slide 1: Panel A only (baseline condition)
Slide 2: Panels A+B (add treatment effect)
Slide 3: Panels A+B+C (add time course)
Slide 4: All panels with interpretation overlay
```

**Approach 2: Layered Data**
```
Slide 1: Axes and experimental design schematic
Slide 2: Add control group data
Slide 3: Add treatment group data
Slide 4: Highlight difference, show statistics
```

**Approach 3: Zoom and Context**
```
Slide 1: Full dataset overview
Slide 2: Zoom to interesting region
Slide 3: Highlight specific points in zoomed view
```

### Animation vs. Multiple Slides

**Use Animation** (PowerPoint/Beamer overlays):
- Building bullet points
- Adding layers to same plot
- Highlighting different regions sequentially
- Smooth transitions within a concept

**Use Separate Slides**:
- Different data or experiments
- Major conceptual shifts
- Want to return to previous view
- Need to control timing flexibly

## Figure Preparation Workflow

### Step 1: Start with High-Quality Source

**For Generated Figures**:
- Export at high resolution (300 DPI minimum)
- Vector formats preferred (PDF, SVG)
- Large size (can scale down, not up)
- Clean, professional appearance

**For Published Figures**:
- Request high-resolution versions from authors/publishers
- Recreate if source not available
- Check reuse permissions

### Step 2: Simplify for Presentation

**Edit in Graphics Software**:
- Remove non-essential panels
- Enlarge fonts and labels
- Increase line widths and marker sizes
- Remove or simplify legends
- Add direct labels
- Remove excess gridlines

**Tools**:
- Adobe Illustrator (vector editing)
- Inkscape (free vector editing)
- PowerPoint/Keynote (basic editing)
- Python/R (programmatic recreation)

### Step 3: Optimize for Projection

**Check**:
- ✅ Readable from 10 feet away
- ✅ High contrast between elements
- ✅ Large enough to fill significant slide area
- ✅ Maintains quality when projected
- ✅ Works in various lighting conditions

**Test**:
- View on different screens
- Project if possible before talk
- Print at small scale (simulates distance)
- Check in grayscale (color-blind simulation)

### Step 4: Add Context and Annotations

**Enhancements**:
- Arrows pointing to key features
- Text boxes with key findings ("p < 0.001")
- Circles or rectangles highlighting regions
- Color coding matched to verbal description
- Reference lines or benchmarks

**Verbal Integration**:
- Plan what you'll say about each element
- Use "Notice that..." or "Here you can see..."
- Point to specific features during talk
- Explain axes and scales first time shown

## Recreating Journal Figures for Presentations

### When to Recreate

**Recreate When**:
- Original has small fonts
- Too many panels for one slide
- Multiple comparisons to parse
- Colors not accessible
- Data available to you

**Reuse When**:
- Already simple and clear
- Appropriate font sizes
- Single focused message
- High resolution available
- Remaking not feasible

### Recreation Tools

**Python (matplotlib, seaborn)**:
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set presentation-friendly defaults
plt.rcParams['font.size'] = 18
plt.rcParams['axes.linewidth'] = 2
plt.rcParams['lines.linewidth'] = 3
plt.rcParams['figure.figsize'] = (10, 6)

# Create plot with large, clear elements
# Export as high-res PNG or PDF
```

**R (ggplot2)**:
```r
library(ggplot2)

# Presentation theme
theme_presentation <- theme_minimal() +
  theme(
    text = element_text(size = 18),
    axis.text = element_text(size = 16),
    axis.title = element_text(size = 20),
    legend.text = element_text(size = 16)
  )

# Apply to plots
ggplot(data, aes(x, y)) + geom_point(size=4) + theme_presentation
```

**GraphPad Prism**:
- Increase font sizes in Format Axes
- Thicken lines in Format Graph
- Enlarge symbols
- Export as high-resolution image

**Excel/PowerPoint**:
- Select chart, Format → Text Options → Size (increase to 18-24pt)
- Format → Line → Width (increase to 2-3pt)
- Format → Marker → Size (increase to 10-12pt)

## Advanced Visualization Types for Specific Scientific Tasks

Beyond the standard bar/line/scatter repertoire, several chart types solve specific scientific-communication problems well. Reach for them deliberately when the task matches; they are not decorative alternatives.

### Connected scatterplots for time-delayed correlations

When two variables move together over time with a lag, a **connected scatterplot** — points connected by lines or arrows in temporal order — reveals the temporal structure that a standard correlation plot hides. "L-shapes" and "loops" in the connected path signify delays (e.g., the characteristic lag between job openings and unemployment).

For multi-dimensional temporal trajectories of up to four variables, a **Rosling-style moving-bubble** approach extends this idea: bubbles where size encodes a third variable and color encodes a fourth, with faded trails showing historical paths. Useful for PK/PD trajectories, clonal evolution, and treatment-response time courses.

### Correlation matrices with diagonal histograms

A standard correlation matrix duplicates every comparison (A vs B is the same as B vs A) — half the grid is redundant ink. **Delete the upper or lower triangle** and use the freed diagonal cells to display per-variable histograms (sparklines or small histograms), giving the reader the marginal distribution of each variable at the same glance as the pairwise correlations.

In PowerPoint, this lives as a table with conditional cell shading plus inserted sparkline histograms on the diagonal.

### Cleveland dot plots with direct labeling

For ranked or categorical quantities, a **Cleveland dot plot** — category labels down the y-axis, a single dot per category positioned along the x-axis — is lighter than a bar chart and does not require a zero baseline. When each point is directly labeled with its value, the x-axis itself can be removed.

Implement as a scatter plot with category labels on y and data labels placed immediately adjacent to each dot.

### Isotypes — with correct scaling

Icons can re-humanize data (one icon represents N people, patients, or events) and can carry qualitative detail such as gender balance.

**The common failure mode** is to scale a single icon by height to represent magnitude, which inadvertently scales **area** and visually overstates the difference — the *area-vs-height scaling error*.

**The correct implementation** is 1:1 replication: to show a 5:1 ratio, draw **five icons beside one icon**, not one icon five times larger. Waffle charts and bar-style icon charts both follow this pattern. Keep replication sizes identical.

### Dual-purpose selection

- **Reading deck** — denser types (correlation matrices with diagonals, moving-bubble trajectories) earn their place. A reader can zoom in and dwell.
- **Projection deck** — prefer the sparser types (Cleveland dot plots, simple connected scatterplots). Correlation matrices with four-variable bubble trails do not survive back-row legibility.

---

## Vector Over Raster — Always (except for photos)

Line art, schematics, icons, chemical structures, and charts should live as **vector content**: EMF, WMF, SVG, or native PowerPoint shapes. Vectors scale to any size without pixelation, export cleanly to PDF, and respect theme colors if built from native shapes.

Raster formats (PNG for figures with text and sharp edges; JPEG only for continuous-tone photographs) are appropriate for micrographs, gel blots, photographs, and anything with genuinely continuous pixel data.

**Targets:** 300 ppi for print, 150 ppi for screen at final display size. Use `Picture Format > Compress Pictures` with "Do not compress images in file" off for the working deck and the HD (330 ppi) or Print (220 ppi) preset before distribution.

**SVG gotchas:** whenever an SVG inserts cleanly but renders oddly, pre-flatten filters in Inkscape (Object to Path, flatten filters, Save as Optimized SVG) before bringing it into PowerPoint. A late-2025 bug in some M365 builds grays out `Graphics Format > Convert to Shape` for certain SVGs; a cut-and-paste of the SVG has been reported to restore it.

## Axis, Uncertainty, and Aspect Ratio

- **Bar charts encoding quantity anchor to zero.** Truncated bars mislead (Rougier et al. 2014, Rule 7).
- **Log scales are labeled as such** on the axis title ("log₁₀ concentration (nM)") with one tick per decade.
- **Show uncertainty** — error bars with their definition stated (SD, SEM, 95% CI), confidence bands, or individual data points overlaid on summary statistics.
- **Prefer dot plots or strip plots** over bar charts when n is small enough to plot individuals. SAB decks especially benefit.
- **Black on white with one highlight color** unless there's an explicit reason otherwise. Rougier et al.'s fifth rule is "do not trust the defaults" — that includes a chart coming out blue for no reason.

**Aspect ratio — Cleveland's banking-to-45-degrees:** match the aspect ratio to the underlying variance in the data, not to the available slide real estate. A time course with small signal-to-noise looks flat when squeezed into 16:9 and deceptively steep when stretched vertically; the honest composition **centers the mean trend line near a 45-degree orientation** through the data.

For bar charts and similar categorical figures the aspect-ratio decision matters less, but the broader rule stands: **do not stretch or squash a figure to fit a layout** — the resulting slope change will visually distort the reader's interpretation of rate or trend.

## Iconography and Vector Icon Workflow

Scientific decks use icons sparingly — an overloaded icon set clutters more than it communicates — but targeted icons earn their place for schematic indicators (mechanism of action glyphs, modality icons, pathway elements, regulatory status markers).

**The operational workflow** that keeps icons brand-consistent:

1. Download as EPS or SVG from a vector library
2. Insert into PowerPoint
3. Right-click → `Convert to Shape` (for SVGs) or `Group > Ungroup` (typically twice — once to ungroup the import container, once to break into component shapes)
4. **Recolor** the individual shapes to the deck's theme colors
5. **Regroup**

This converts an off-the-shelf icon into a theme-linked asset that responds to rebranding. **Never drop an icon as a raster PNG when a vector source exists** — the PNG will not recolor, scales poorly, and fails to match any theme change.

### Icon libraries

**Biomedical-specific:**
- **BioRender** — curated biomedical schematics, paid, widely accepted in publications
- **Bioicons** — free open-source library, CC0 or CC BY licensed

**General-purpose:**
- **Flaticon** — large indexed library; mixed free/paid with attribution requirements for free tier
- **SlideRoom** — curated PowerPoint-native icon sets
- **PowerPoint's `Insert > Icons`** — acceptable for generic UI iconography, thin for scientific content

**License every icon** used in commercial/promotional decks. CC BY requires visible attribution; CC0 does not; Flaticon's free tier requires attribution that MLR may flag if missed.

**Consistency rule:** keep the icon set to two or three styles across the deck. Mixing outlined, filled, and flat-color icons in the same deck reads as visual noise.

## Reproducible Code-to-Deck Pipelines

For analyses where the deck must stay in sync with upstream data, three workflows are mature enough for biotech use:

### R — officer + officedown + flextable

`officer` and `officedown` generate .pptx files programmatically from RMarkdown. `flextable` renders publication-quality tables that round-trip into PowerPoint preserving formatting.

### Quarto (Posit 2022–present)

A Quarto document with `.qmd` source and a `pptx` format block renders slides from chunks of R or Python, embedding figures directly with full reproducibility.

**Weakness:** template fidelity. The default Quarto template is generic; matching a corporate or brand template requires supplying a reference .pptx with the Slide Master already populated.

### Python — python-pptx

`python-pptx` provides a lower-level API for composing slides by opening a template and inserting shapes, charts, and text programmatically. Right tool when the deck is primarily data-driven (weekly metrics reviews, automated clinical-trial status updates).

For Oligon-branded slide generation via Claude, see [`skills/oligon-brand/adapters/pptx_adapter.py`](../../oligon-brand/adapters/pptx_adapter.py) which wraps python-pptx with v5.0 brand tokens.

### The defensible pipeline for LLM-drafted decks

1. Generate figures in R or Python with the **Okabe-Ito palette hard-coded** (use `skills/plotting-libraries/scripts/palette_selector.select_palette()`)
2. Save as **EMF or SVG**
3. Assemble in PowerPoint by hand or via `python-pptx` against a branded reference template

This preserves both reproducibility and design integrity.

## Effect-Size Evidence for Design Decisions

Several rules in this guide have direct empirical backing worth citing when challenged:

- **Assertion-evidence headlines** produce ~**59% vs 42%** comprehension over topic-subtitle slides (Garner & Alley 2013, p < 0.01, n=110), reduce major misconceptions by ~**10×**, and increase delayed recall
- **Red-green color vision deficiency** affects ~**8% of men** and **0.5% of women** of Northern European ancestry (Wong 2011)
- **Rainbow colormaps** introduce false banding at luminance transitions (Borland & Taylor 2007)

Beyond these, effect-size data for specific design choices (serif vs sans-serif legibility deltas, direct-labeling comprehension gains over legends, zero-baseline distortion magnitudes) is **sparse** in the peer-reviewed literature — the consensus comes from professional practice and design-industry research rather than controlled studies.

## Summary Checklist

Before including a figure in your presentation:

**Clarity**:
- [ ] One clear message per figure
- [ ] Immediately understandable (< 5 seconds)
- [ ] Appropriate chart type for data
- [ ] Simplified from journal version (if applicable)

**Readability**:
- [ ] Font sizes ≥18pt for labels
- [ ] Thick lines (2-4pt) and large markers (8-12pt)
- [ ] High contrast colors
- [ ] Readable from back of room

**Design**:
- [ ] Minimal chart junk (removed gridlines, simplify)
- [ ] Axes clearly labeled with units
- [ ] Color-blind friendly palette
- [ ] Consistent style with other figures

**Context**:
- [ ] Sample sizes indicated (n)
- [ ] Statistical results shown (p-values, CI)
- [ ] Error bars defined (SE, SD, or CI?)
- [ ] Key finding annotated or highlighted

**Technical Quality**:
- [ ] High resolution (300 DPI minimum)
- [ ] Vector format preferred
- [ ] Properly sized for slide
- [ ] Quality maintained when projected

**Progressive Disclosure** (if complex):
- [ ] Plan for building figure incrementally
- [ ] Each step adds one new element
- [ ] Final version shows complete picture
- [ ] Animation or separate slides prepared
