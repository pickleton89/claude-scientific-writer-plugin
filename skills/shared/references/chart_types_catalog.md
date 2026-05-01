# Chart Types Catalog — Flat Lookup of 35 Chart Types

> Cross-skill flat catalog: 35 chart types with use cases, when-to / when-not-to, strengths, weaknesses, mechanism, and data types. Use as a by-chart-type reference once you know which chart family you want.
> Version: 1.0.0
> Used by: plotting-libraries, scientific-writing, scientific-slides, research-posters
> Source: "Data Visualization Chart Types and Best Practices" (curated reference, 35 entries).

---

## How to use this file (and when not to)

This catalog is a **flat lookup** — alphabetical-by-purpose listing of 35 chart types. Use it when you already know roughly what chart you want and need a quick refresher on its strengths, pitfalls, and required data shape.

For other entry points, prefer the matching decision aid:

| You are starting from… | Use |
|---|---|
| A research question or figure intent (Description / Difference / Association) | `../../plotting-libraries/references/plot_selection_guide.md` (intent-driven decision tree) |
| A result and unsure whether to show it at all | `figure_vs_table_decision.md` (figure vs table vs both vs text) |
| A chosen audience / venue (article, slide, poster, dashboard) | `communication_context_matrix.md` (complexity by viewing context) |
| A drafted figure ready for a final pass | `pre_submission_checklist.md` (15-point quality gate) |

Run the decision aids **first**; come here **second** to look up the chosen chart's properties.

---

## Conflict-resolution policy

Where this catalog conflicts with cited scholarly guidance elsewhere in the plugin, **defer to the cited source**. Specifically:

- **Bar charts of continuous data:** the catalog lists bars as "easy to read." For continuous biological / clinical measurements, bars hide distribution shape and should be replaced with box+jitter or paired-points (Weissgerber et al. *PLoS Biol* 2015). See `../../plotting-libraries/references/plot_selection_guide.md` §"Anti-pattern 1."
- **Bar charts of risk / hazard / odds ratios:** bars exaggerate the point estimate and visually swamp the confidence interval. Use point-with-CI (pointrange) or a forest plot instead (Fujii *J Epidemiol* 2023). See `plot_selection_guide.md` §"Anti-pattern 2."
- **Pie / donut for >3 categories:** the catalog allows up to ~5 slices; cognitive-foundation guidance prefers position-on-aligned-scale (bar chart) above ~3 categories (Cleveland & McGill 1984). See `figure_vs_table_decision.md` §"Anti-patterns."
- **Rainbow / jet / Spectral colour for sequential data:** never use; perceptually distorting (Crameri et al. *Nat Commun* 2020). Use viridis, cividis, or Crameri palettes (`batlow`, `roma`).

When in doubt, the biomedical / scholarly source wins.

---

## Index — grouped by primary purpose

**Comparison (categories or values):** [Bar Chart](#bar-chart) · [Column Chart](#column-chart) · [Dot Plot](#dot-plot) · [Arrow Plot](#arrow-plot) · [Slope Chart](#slope-chart) · [Bump Chart](#bump-chart)

**Trends over time:** [Line Chart](#line-chart) · [Area Chart](#area-chart) · [Sparklines](#sparklines) · [Connected Scatter Plot](#connected-scatter-plot) · [Cycle Plot](#cycle-plot) · [Stream Graph](#stream-graph) · [Candlestick Chart](#candlestick-chart) · [Gantt Chart](#gantt-chart)

**Distribution:** [Histogram](#histogram) · [Boxplot (Box-and-Whisker)](#boxplot-box-and-whisker) · [Violin Plot](#violin-plot) · [Beeswarm Chart](#beeswarm-chart)

**Relationship / association:** [Scatter Plot](#scatter-plot) · [Bubble Chart](#bubble-chart) · [Heat Map](#heat-map) · [Parallel Coordinates Plot](#parallel-coordinates-plot) · [Radar / Spider Chart](#radar--spider-chart)

**Composition & hierarchy:** [Pie Chart](#pie-chart) · [Donut Chart](#donut-chart) · [Stacked Bar / Column Chart](#stacked-bar--column-chart) · [Tree Map](#tree-map) · [Sunburst Diagram](#sunburst-diagram) · [Mekko Chart](#mekko-chart) · [Waterfall Chart](#waterfall-chart)

**Flow & network:** [Chord Diagram](#chord-diagram) · [Adjacency Matrix](#adjacency-matrix)

**Geospatial:** [Choropleth Map](#choropleth-map) · [Cartogram](#cartogram)

**Reference / lookup:** [Table](#table)

---

## Per-chart entries

Each entry uses a consistent shape:

> **Use** · **When to use** · **When not to use** · **Strengths** · **Weaknesses** · **How it works** · **Data types** · *Cross-refs* (where deeper treatment exists)

---

### Bar Chart

- **Use:** Comparing categories and absolute numbers or distributions.
- **When to use:** Comparing magnitudes across categorical groups; better for long labels or small screens (mobile).
- **When not to use:** When bars are truncated (the axis must start at zero); when continuous trends are more important; **for continuous biological measurements** (defer to Weissgerber 2015 — use box+jitter); **for risk / hazard / odds ratios** (defer to Fujii 2023 — use point + CI).
- **Strengths:** Easy to read; brains judge length accurately; small differences are easy to spot.
- **Weaknesses:** Cluttered with too many categories; diagonal labels slow reading.
- **How it works:** Maps data onto horizontal bars where length represents magnitude on a Cartesian coordinate system.
- **Data types:** Categorical, Quantitative.
- **Cross-refs:** `../../plotting-libraries/references/plot_selection_guide.md` §"Anti-pattern 1" and §"Anti-pattern 2"; `../../scientific-writing/references/figures_tables.md` §"Bar Graphs."

---

### Column Chart

- **Use:** Comparing categories and showing changes over discrete time points.
- **When to use:** Representing data that changes over time (the brain reads left-to-right); comparing absolute numbers or shares.
- **When not to use:** When data has no natural order (implied trend can mislead); on small screens with many bars.
- **Strengths:** Effective for category totals; familiar and intuitive.
- **Weaknesses:** Less effective than bar charts for long labels; vertical labels eat horizontal space.
- **How it works:** Maps data onto vertical columns where height represents magnitude.
- **Data types:** Categorical, Quantitative, Temporal.

---

### Line Chart

- **Use:** Showing trends, patterns, growth, or volatility over time.
- **When to use:** Data with a natural order (time) where upward / downward trends matter; tracking continuous evolution.
- **When not to use:** Categorical data with no natural order; only two data points (use a slope chart).
- **Strengths:** Emphasises slope and direction; less busy than scatter for time series.
- **Weaknesses:** Hides individual points; becomes a "spaghetti chart" with too many overlapping lines.
- **How it works:** Connects data points with lines on a Cartesian coordinate system.
- **Data types:** Temporal, Quantitative, Continuous.
- **Cross-refs:** `../../scientific-writing/references/figures_tables.md` §"Line Graphs"; `../../scientific-slides/references/data_visualization_slides.md` §"Line Graphs" (presentation optimisation).

---

### Scatter Plot

- **Use:** Identifying relationships, correlations, or distributions between two variables.
- **When to use:** Looking for positive / negative correlations or highlighting outliers in large datasets.
- **When not to use:** Showing the trend of a single set of data; when points overlap excessively (overplotting — use hexbin or transparency).
- **Strengths:** Reveals non-linear mathematical relationships; preserves individual x and y values.
- **Weaknesses:** Becomes a "disordered cloud" with no natural order or too many variables.
- **How it works:** Maps individual data points onto x-y coordinates on a Cartesian coordinate system.
- **Data types:** Quantitative, Bi-variate, Categorical (for grouping).
- **Cross-refs:** `../../plotting-libraries/references/plot_selection_guide.md` §"Association"; `../../plotting-libraries/references/volcano_plots.md` for biomedical scatter (differential expression).

---

### Pie Chart

- **Use:** Comparing values against a total (parts-of-a-whole).
- **When to use:** Pieces add up to 100%; very few categories (2–3 ideal, 5 maximum).
- **When not to use:** Comparing categories against each other; time series; segments similar in size; **>3 categories** (defer to bar chart per Cleveland & McGill 1984).
- **Strengths:** Intuitive "whole"; quick visual estimate of simple fractions (½, ¼).
- **Weaknesses:** Brain compares angles / surface areas poorly; 3D effects distort shape.
- **How it works:** Divides a circle into proportional slices where area / angle represents the fraction.
- **Data types:** Categorical, Quantitative (Proportions).
- **Cross-refs:** `figure_vs_table_decision.md` §"Anti-patterns" (pie chart for >3 categories).

---

### Heat Map

- **Use:** Visualising data density, intensity, or large matrices.
- **When to use:** High data density; spotting "hot / cold" patterns without showing every number.
- **When not to use:** Absolute variation must be precisely judged; fine-grained numeric precision required (use a table).
- **Strengths:** Reveals hotspots instantly; space-efficient for large grids or many variables.
- **Weaknesses:** Susceptible to optical illusions (ground subtraction); exact values need tooltips or annotations.
- **How it works:** Maps data values onto a colour gradient / saturation within a grid or matrix.
- **Data types:** Quantitative, Categorical, High-dimensional.
- **Cross-refs:** `../../plotting-libraries/references/heatmaps.md` (Python `clustermap`, R `ComplexHeatmap`, `pheatmap`); `../../plotting-libraries/references/plot_selection_guide.md` §"Step 4 — Match colour to scale type" (use viridis / Crameri, never rainbow).

---

### Stacked Bar / Column Chart

- **Use:** Showing totals of subcategories and their internal breakdown.
- **When to use:** The sum of parts is meaningful; survey results (e.g. Likert scales) over time.
- **When not to use:** Many subcategories; comparing middle segments (the baseline shifts and breaks comparison).
- **Strengths:** Shows proportions of a whole across categories or time points efficiently.
- **Weaknesses:** Subcategories not on a shared baseline are hard to compare.
- **How it works:** Stacks categorical sub-segments vertically or horizontally within a single bar.
- **Data types:** Categorical, Quantitative, Temporal.
- **Cross-refs:** `figure_vs_table_decision.md` §"Anti-patterns" (stacked bar of percentages summing to 100% — usually a single-row table is clearer for ≤5 categories).

---

### Bubble Chart

- **Use:** Visualising relationships between three or more quantitative variables.
- **When to use:** Adding a third dimension (size / area) to a scatter plot to encode volume or quantity.
- **When not to use:** Differences in the third variable are small; exact quantities must be judged precisely.
- **Strengths:** Approachable organic shape; fits a lot of information in a compact field of view.
- **Weaknesses:** Humans compare circle areas poorly; unreadable when over-complicated.
- **How it works:** Maps data to x position, y position, and circle area.
- **Data types:** Quantitative, High-dimensional.

---

### Tree Map

- **Use:** Showing proportions and hierarchical data within nested levels.
- **When to use:** How subcategories fit into an overall total; effective when space is limited.
- **When not to use:** Showing developments over time; comparing categories directly against each other.
- **Strengths:** Powerful for hierarchical visualisation; spots patterns in thousands of items.
- **Weaknesses:** Less easy to read than bar charts; rectangles don't share baselines so comparison is hard.
- **How it works:** Recursively nested rectangles where area is proportional to value.
- **Data types:** Categorical, Quantitative, Hierarchical.

---

### Area Chart

- **Use:** Showing overall trends while emphasising the actual volume or shares of data.
- **When to use:** Change in quantities (e.g. revenue) or internal breakdowns of a total over time.
- **When not to use:** Too many categories; when comparing specific values at specific points is the primary goal.
- **Strengths:** Intuitively shows how categories contribute to a total volume over time.
- **Weaknesses:** Layered overlap is confusing; exact values harder to read than a line chart.
- **How it works:** Fills the space between a line and an axis to represent volume / magnitude.
- **Data types:** Temporal, Quantitative.

---

### Donut Chart

- **Use:** Showing proportions and parts of a whole.
- **When to use:** Modern alternative to the pie chart; categories ≤5.
- **When not to use:** More than a handful of categories; pieces don't add up to 100%.
- **Strengths:** The eye compares arc length instead of surface area (often easier than pie).
- **Weaknesses:** Limited categories; segment comparison still imprecise.
- **How it works:** A pie chart with the centre removed, focusing the viewer on arc lengths.
- **Data types:** Categorical, Quantitative (Proportions).

---

### Boxplot (Box-and-Whisker)

- **Use:** Visualising and summarising data distributions and variability.
- **When to use:** Showing the five-number summary (min, Q1, median, Q3, max) and identifying outliers; group comparisons of continuous biological / clinical measurements (preferred over bars per Weissgerber 2015).
- **When not to use:** Bimodal data — boxplots hide internal distribution shapes (use violin or beeswarm).
- **Strengths:** Highly informative for statistical summaries; clean form for measures of dispersion.
- **Weaknesses:** Hides density / shape; can be opaque to non-technical audiences.
- **How it works:** Box drawn between Q1 and Q3 with a median line; whiskers extend to extremes.
- **Data types:** Quantitative (Distributions), Categorical.
- **Cross-refs:** `../../plotting-libraries/references/plot_selection_guide.md` §"Difference" (box+jitter as the recommended replacement for bars of continuous data); `../../plotting-libraries/references/statistical_visualization.md`.

---

### Connected Scatter Plot

- **Use:** Time series of two variables, or how correlations change over time.
- **When to use:** Identifying cyclic behaviour, phase portraits, or time-delayed correlations.
- **When not to use:** Readers unfamiliar with the format (likely to confuse order and direction).
- **Strengths:** Higher engagement; complex relationships become recognisable shapes.
- **Weaknesses:** Without direction indicators (arrows / colour gradient) it looks like a meaningless scribble; violates standard line-graph conventions.
- **How it works:** Plots two variables on x-y axes and connects points chronologically with lines.
- **Data types:** Temporal, Quantitative, High-dimensional.

---

### Choropleth Map

- **Use:** Showing geographical patterns and values by administrative region.
- **When to use:** Data tied to state / county / province levels (election results, crime rates, prevalence).
- **When not to use:** Data simply reflects underlying population density (unless intended); compare against a cartogram.
- **Strengths:** Standard map type for geographic data; supports categorical or sequential scales.
- **Weaknesses:** Large geographic areas dominate visually regardless of data value; can be mistaken for density maps.
- **How it works:** Shades geographic regions based on a data value or category.
- **Data types:** Geospatial, Categorical, Quantitative.

---

### Waterfall Chart

- **Use:** Showing the breakdown of a value or the path between two values.
- **When to use:** Finance / consulting flows, cumulative effects, incremental changes.
- **When not to use:** No strong source guidance; avoid when ordering of contributions is arbitrary.
- **Strengths:** Explains the specific additions and subtractions leading to a final result.
- **Weaknesses:** Needs careful colour coding (e.g. green / red) to avoid confusion; defer to colour-vision-deficient-safe palettes (e.g. Okabe-Ito blue / orange).
- **How it works:** Floating columns show gains and losses between a starting and ending point.
- **Data types:** Quantitative.

---

### Table

- **Use:** Showing precise values and mixed types of data.
- **When to use:** Individual values are important; fundamentally different metrics (e.g. % alongside absolute counts); reader will quote, copy, or look up specific numbers.
- **When not to use:** The primary goal is a quick trend or relative comparison at a glance.
- **Strengths:** Allows specific, accurate data points; high-dimensional mixed metrics.
- **Weaknesses:** Patterns and trends are hard to see compared to visual charts.
- **How it works:** Organises raw data into a grid of rows and columns.
- **Data types:** Quantitative, Categorical, High-dimensional.
- **Cross-refs:** `figure_vs_table_decision.md` (when to choose table over figure); `../../scientific-writing/references/figures_tables.md` §"Table Design Guidelines."

---

### Histogram

- **Use:** Showing the distribution or shape of a continuous data set.
- **When to use:** Seeing where values are concentrated; identifying variance / spread; n > 30.
- **When not to use:** Bins too wide (loss of resolution) or too narrow (noisy artefacts); n < 30 (use a strip plot or ECDF instead).
- **Strengths:** Powerful for elucidating the underlying frequency distribution.
- **Weaknesses:** Visual similarity to bar charts can confuse beginners; binning choice changes the perceived shape.
- **How it works:** Sorts data into equally sized value ranges (bins) and stacks counts as bars.
- **Data types:** Continuous, Quantitative.
- **Cross-refs:** `../../plotting-libraries/references/plot_selection_guide.md` §"Description."

---

### Sparklines

- **Use:** Showing development over time within restricted spaces.
- **When to use:** Space is limited within a data table to show a trend summary.
- **When not to use:** A consistent y-axis range is critical for comparison across rows (sparklines default to per-row scaling).
- **Strengths:** Shows general trends in very little space without the clutter of axes.
- **Weaknesses:** Y-axis ranges often differ by default, making rows non-comparable.
- **How it works:** Mini line charts without axes or labels.
- **Data types:** Temporal, Quantitative.

---

### Radar / Spider Chart

- **Use:** Plotting multiple variables from a central origin point.
- **When to use:** Profile comparisons where the message is obvious and categories are related.
- **When not to use:** Categories shouldn't be measured against each other (e.g. sales vs. satisfaction); axis ordering is arbitrary.
- **Strengths:** Visually unique; useful for seeing the "shape" of a profile across dimensions.
- **Weaknesses:** Category ordering misleadingly changes the perceived shape and area of the web.
- **How it works:** Maps data onto multiple axes extending from a central origin.
- **Data types:** High-dimensional, Categorical.

---

### Mekko Chart

- **Use:** Ranking along one dimension while showing another.
- **When to use:** Answering multiple questions in one view (e.g. market size and segment focus).
- **When not to use:** General audiences; readers without high data literacy.
- **Strengths:** Captures complex multi-dimensional data (width and height) in one view.
- **Weaknesses:** Hard to interpret quickly due to varying widths and heights.
- **How it works:** A 100% stacked column chart where column widths represent an additional dimension.
- **Data types:** High-dimensional, Categorical.

---

### Adjacency Matrix

- **Use:** Representing network data and interactions.
- **When to use:** Dense networks with many edges (avoids "hairball" clutter of node-link diagrams).
- **When not to use:** Showing path relationships between distant neighbours (node-link is more intuitive for paths).
- **Strengths:** Excellent for showing clusters; readable node labels without clutter.
- **Weaknesses:** Less intuitive than node-link diagrams for understanding network flow.
- **How it works:** Lists all nodes on both axes; fills the intersection cell where an edge exists.
- **Data types:** Relational, Categorical.

---

### Violin Plot

- **Use:** Visualising many distributions with density information.
- **When to use:** A nuanced picture of distributions is needed; especially appropriate for bimodal data.
- **When not to use:** Mainstream / non-technical audiences; very sparse data (the smoothed density misleads).
- **Strengths:** Accurately represents bimodal data and detailed density shapes (where boxplots hide them).
- **Weaknesses:** Smoothing can imply data where none exists; readers may misread the wide / narrow zones.
- **How it works:** A mirrored kernel density estimate rotated by 90 degrees.
- **Data types:** Quantitative (Distributions), Categorical.
- **Cross-refs:** `../../plotting-libraries/references/plot_selection_guide.md` §"Difference" (violin+jitter is the second-choice alternative to box+jitter).

---

### Beeswarm Chart

- **Use:** Visualising distributions of single data points.
- **When to use:** Showing all points in a set (up to a few hundred); highlighting gaps or irregularities; making differences in sample size obvious.
- **When not to use:** Very skewed distributions; very large sample sizes (10,000+ points won't fit).
- **Strengths:** Shows underlying raw data; sample-size differences across groups are immediately visible.
- **Weaknesses:** Doesn't fit on a page when sample sizes are massive.
- **How it works:** Places single data points along one axis, preventing overlap by displacing dots side-by-side.
- **Data types:** Quantitative, Categorical.

---

### Parallel Coordinates Plot

- **Use:** Exploratory visualisation of multi-dimensional data.
- **When to use:** Exploring data with 10+ dimensions; spotting correlations across many records.
- **When not to use:** Explanatory visualisation for general audiences (too complex).
- **Strengths:** Packs 1,000+ records and 10+ dimensions into a single chart.
- **Weaknesses:** Axis ordering is crucial; becomes a mess if axes are not sorted purposefully.
- **How it works:** Vertical axes placed next to each other; each record is connected with a line crossing all axes.
- **Data types:** High-dimensional, Quantitative.

---

### Cartogram

- **Use:** Visualising location data while adjusting region size for a variable (e.g. population).
- **When to use:** Administrative boundaries distort perception due to size vs. data value (e.g. low-population large states swamping a US choropleth).
- **When not to use:** Geographic familiarity is low (distorted shapes become unrecognisable).
- **Strengths:** Overcomes the unequal-container problem of choropleths.
- **Weaknesses:** Scale is distorted; can cause negative reactions due to shape distortion.
- **How it works:** Morphs geographic areas according to a data variable (population density, GDP, etc.).
- **Data types:** Geospatial, Quantitative.

---

### Chord Diagram

- **Use:** Visualising paths, flows, and connections between nodes.
- **When to use:** Mobility (census, travel) or activity between regions.
- **When not to use:** Too much information (arcs become tiny and hard to see).
- **Strengths:** Captures mobility and flow well; arc thickness is informative.
- **Weaknesses:** Visually overwhelming with many connections.
- **How it works:** Wraps axes in a circle and uses arcs to show the relationship and quantity between nodes.
- **Data types:** Quantitative (Flow), Categorical.

---

### Bump Chart

- **Use:** Showing changes in rank over time.
- **When to use:** Relative position is more important than absolute magnitude.
- **When not to use:** Irregular intervals or too many categories.
- **Strengths:** Good summary of position changes over time.
- **Weaknesses:** Shows only rank, not magnitude; messy with many categories.
- **How it works:** Connects ranked positions across regular time intervals with lines.
- **Data types:** Temporal, Ordinal (Rank).

---

### Candlestick Chart

- **Use:** Displaying multiple bits of price information over time.
- **When to use:** Financial analysis of securities, stocks, or currency exchange.
- **When not to use:** Domains outside finance; non-OHLC data shouldn't be forced into the format.
- **Strengths:** Conveys open / high / low / close in a single mark; supports trend and sentiment reading.
- **Weaknesses:** Specialised; assumes audience literacy in financial conventions.
- **How it works:** A "real body" represents the open / close range; "wicks" represent the high / low extremes.
- **Data types:** Temporal, Financial Quantitative.

---

### Gantt Chart

- **Use:** Project management and tracking stages over time.
- **When to use:** Organising events, teams, or people over a horizontal timeline.
- **When not to use:** Outside project / scheduling contexts.
- **Strengths:** Lets viewers see what is happening across multiple teams and time spans simultaneously.
- **Weaknesses:** Visually unorganised if not strictly sorted by time or by team.
- **How it works:** Horizontal bars where the horizontal axis represents time; each bar is a task with start / end.
- **Data types:** Temporal, Categorical.

---

### Sunburst Diagram

- **Use:** Representing hierarchical data.
- **When to use:** Relationships between one group and multiple subgroups in a compact radial space.
- **When not to use:** Many tiny outer wedges (labels become unreadable); compare against a tree map.
- **Strengths:** Packs a large amount of information into a small radial area.
- **Weaknesses:** Small wedges are extremely difficult to identify or label accurately.
- **How it works:** Radial segmented display where outer rings represent sub-levels of inner rings.
- **Data types:** Categorical (Hierarchical).

---

### Cycle Plot

- **Use:** Showing changes over time with seasonality.
- **When to use:** Both seasonal trends and long-term trends matter to the story.
- **When not to use:** Categorical data; data without a seasonal structure.
- **Strengths:** Shows seasonal and long-term trends in a single chart.
- **Weaknesses:** Noisy for first-time viewers; requires data structured into seasonal segments.
- **How it works:** Groups data into seasonal segments and shows trends within those segments over years.
- **Data types:** Temporal (Seasonal), Quantitative.

---

### Slope Chart

- **Use:** Showing changes between two points in time.
- **When to use:** Fluctuations between the first and last date are not relevant; net change is the message.
- **When not to use:** When intermediate trajectory matters (use a line chart instead).
- **Strengths:** Tidies up otherwise messy line charts by focusing on net change.
- **Weaknesses:** Requires a learning curve for general readers; ignores intermediate data.
- **How it works:** A line chart where only the first and last data points are connected.
- **Data types:** Temporal (two points), Categorical.

---

### Arrow Plot

- **Use:** Showing changes between categories in limited space.
- **When to use:** Many categories in a compact space; direction and magnitude of change matter equally.
- **When not to use:** Mainstream audiences less comfortable with non-standard glyphs.
- **Strengths:** Compact; indicates direction and magnitude of change efficiently.
- **Weaknesses:** Less intuitive for mainstream audiences than standard bar or line charts.
- **How it works:** Arrows indicate the direction and magnitude of change between two values.
- **Data types:** Quantitative, Categorical.

---

### Dot Plot

- **Use:** Comparing values within categories.
- **When to use:** Limited space; more than a couple of values per category; an alternative to bars when zero baseline isn't required.
- **When not to use:** When magnitude-from-zero is the message (bars carry that better via length encoding).
- **Strengths:** High space-efficiency; effectively shows individual data points.
- **Weaknesses:** Less immediately intuitive than bars for absolute-magnitude comparison.
- **How it works:** Dots on a single or dual axis represent values.
- **Data types:** Categorical, Quantitative.

---

### Stream Graph

- **Use:** Grabbing attention for developments over time.
- **When to use:** A stronger visual metaphor for flow than a stacked area chart.
- **When not to use:** When exact values matter or when proportions must be compared precisely.
- **Strengths:** High visual impact; grabs attention.
- **Weaknesses:** Hard to read exact values or compare proportions accurately.
- **How it works:** A type of stacked area graph displaced around a central, non-flat axis.
- **Data types:** Temporal, Quantitative.

---

## Cross-references

| Topic | See |
|---|---|
| Intent-driven decision tree (Description / Difference / Association) | `../../plotting-libraries/references/plot_selection_guide.md` |
| Figure vs table vs both vs text | `figure_vs_table_decision.md` |
| Audience × time × interaction → figure complexity | `communication_context_matrix.md` |
| Pre-submission 15-point quality gate | `pre_submission_checklist.md` |
| Cognitive-foundation citations (Cleveland-McGill, Crameri, Wilke, Fujii, Weissgerber) | `../../oligon-brand/SKILL.md` `<design_foundation>` |
| Volcano plots (specialised scatter for differential expression) | `../../plotting-libraries/references/volcano_plots.md` |
| Heatmaps (Python `clustermap`, R `ComplexHeatmap`) | `../../plotting-libraries/references/heatmaps.md` |
| Survival curves (Kaplan-Meier) | `../../plotting-libraries/references/survival_curves.md` |
| Genome tracks | `../../plotting-libraries/references/genome_tracks.md` |
| Per-skill cross-links to this catalog | `../../scientific-writing/references/figures_tables.md` (writing-specific design rules), `../../scientific-slides/references/data_visualization_slides.md` (presentation optimisation), `../../research-posters/SKILL.md` (poster reference table) |

---

## References

- "Data Visualization Chart Types and Best Practices" (curated reference) — source of the 35-chart enumeration captured here.
- Cleveland, W. S. & McGill, R. *J Am Stat Assoc* **79**, 531–554 (1984) — channel ranking; deferral source for pie / donut at >3 categories.
- Crameri, F., Shephard, G. E. & Heron, P. J. *Nat Commun* **11**, 5444 (2020) — perceptually uniform, CVD-safe palettes; never use rainbow / jet for sequential data.
- Fujii, R. *Nat Hum Behav* (2026). doi:10.1038/s41562-026-02466-9 — five-tactic framework for figure design.
- Fujii, R. *J Epidemiol* **33**, 487–488 (2023) — risk ratios as points + CI, not bars.
- Midway, S. R. *Patterns* **1**, 100141 (2020) — "Principles of Effective Data Visualization."
- Tufte, E. R. *The Visual Display of Quantitative Information* (Graphics Press, 2001) — data-ink ratio.
- Weissgerber, T. L. et al. *PLoS Biol* **13**, e1002128 (2015) — bar charts of continuous data hide distribution; use box+jitter.
- Wilke, C. O. *Fundamentals of Data Visualization* (O'Reilly, 2019).
