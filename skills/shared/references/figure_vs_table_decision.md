# Figure vs Table Decision Aid

> Decision aid for the question Fujii (2026) places at the end of his framework but is best asked first: **does this result actually require a figure?**
> Version: 1.0.0
> Used by: plotting-libraries, scientific-slides, scientific-schematics, paperbanana, research-posters, scientific-writing
>
> Cross-linked from Q0 of `pre_submission_checklist.md`.

---

## Why this is Q0, not Q-last

Fujii lists "ask whether you really need a figure" as the fifth tactic in his framework, but in practice it dominates everything downstream. A figure that should have been a table fails every other check: it cannot communicate precise values, it under-uses page space, it adds visual cognitive load that obscures rather than reveals. Asking the question early avoids designing the wrong artefact.

---

## When to use a TABLE

Tables are the right format when **precise numerical values are the point**, not the pattern. Specifically:

- **Baseline characteristics** of study participants (age, sex, comorbidities, BMI, etc.) — readers compare exact numbers across columns.
- **Model coefficients with confidence intervals** — readers will quote exact estimates and CIs.
- **Descriptive statistics** (means, medians, IQRs, ranges) — single values per cell, not distributions.
- **Lists of items** that don't have a natural ordering or pattern — gene lists, enrichment results, included studies.
- **Small data** — fewer than ~5 data points that don't form a recognisable shape.
- **Reporting requirements** — many checklists (CONSORT, STROBE, PRISMA) require specific tables.
- **Reference / lookup** — readers will search for a specific value, not scan for trends.

**Rule of thumb:** If a reader will quote, copy, or look up a specific number from this artefact, it should be a table.

---

## When to use a FIGURE

Figures are the right format when **patterns are the point**:

- **Distributions** — is the data bimodal, skewed, heavy-tailed? Histograms, KDEs, ECDFs, box+jitter.
- **Correlations / associations** — does Y vary with X? Scatter plots, regression lines, hexbin.
- **Time trends** — does the response change over time? Line plots, time series with bands.
- **Group comparisons with distribution structure** — do treatment and control differ, and how heterogeneous is each? Box+jitter, violin+jitter, strip plots.
- **Effect estimates with uncertainty** — points + 95% CI for risk ratios, hazard ratios, odds ratios (Fujii 2023).
- **Multi-dimensional comparisons** — heatmaps, PCA / UMAP / t-SNE.
- **Spatial relationships** — maps, anatomical schematics, network diagrams.

**Rule of thumb:** If the reader needs to recognise a shape, ranking, or relationship, it should be a figure.

---

## When to use BOTH

Some results genuinely need both. Use both when readers need:

- **Pattern recognition AND numerical precision.** Fujii's example: the WHO COVID-19 dashboard combines an interactive map (pattern) with a sortable table (precise values).
- **Official statistics or public reporting.** Government and policy contexts frequently combine a chart (for pattern) with a table (for accountability and exact reporting).
- **A figure in the main text + a supplementary table** with full numerical detail. Common pattern in clinical trials: forest plot in the main paper, full table of subgroup HRs and p-values in the supplement.
- **A dashboard.** Layered disclosure: overview chart at the top, drill-down table on click.

---

## Decision tree

```
Does the reader need to KNOW exact values?
├─ Yes → Will they ALSO need to recognise a pattern?
│        ├─ Yes  → BOTH (figure + supplementary table, or dashboard)
│        └─ No   → TABLE
└─ No  → Is there a pattern (distribution, trend, correlation, group difference)?
         ├─ Yes  → FIGURE
         └─ No   → Reconsider: if there's no pattern AND no exact-value need,
                   the result may not be presentable here at all
                   (e.g., a non-finding for a single endpoint goes in the text).
```

---

## Quick examples

| Result | Best format | Why |
|---|---|---|
| Baseline demographics across 3 study arms | Table | Readers compare specific values; no shape to see |
| Survival over 5 years by treatment | Figure (KM curve) | Time trend with separation between groups is the point |
| Cox regression: 12 covariates each with HR + 95% CI + p-value | Both — forest plot in main text, full table in supplement | Pattern of which covariates matter (figure) + precise estimates for citation (table) |
| List of 47 genes from an enrichment analysis | Table | No natural ordering; readers look up specific genes |
| Distribution of one continuous biomarker before vs after treatment, n=200 | Figure (box+jitter or paired-points-with-lines) | Distribution shape and individual response trajectories matter |
| One percentage from one arm of one trial | Text (in the prose) | Single value; neither pattern nor lookup target |
| Confidence intervals for 3 secondary endpoints | Table or figure (forest plot); both work — pick one | Either format works for 3 estimates with CIs |

---

## Anti-patterns

- **Bar chart of three numbers** — a sentence in the text would communicate the same thing with less ink. If the data is small enough to enumerate, it usually doesn't need a figure (Fujii 2026; Tufte 2001 data-to-ink ratio).
- **Table of 200 rows in the main text** — supplementary; main text gets the pattern (a figure or summary table of representative rows).
- **Stacked bar chart of percentages summing to 100%** — a single-row table is usually clearer for ≤5 categories.
- **Pie chart for >3 categories** — table or bar chart (Cleveland-McGill 1984: position-on-aligned-scale beats angle).
- **A figure that communicates only the means, no distribution** — usually a Weissgerber 2015 anti-pattern; either show the distribution (box+jitter) or use a table with exact means and SDs.

---

## Cross-references

| Topic | See |
|---|---|
| Pre-submission gate (Q0 cross-links here) | `pre_submission_checklist.md` |
| Communication-context matrix (figure complexity by viewing context) | `communication_context_matrix.md` |
| Bar-chart / risk-ratio plot anti-patterns | `../plotting-libraries/references/plot_selection_guide.md` |
| Cognitive-foundation citations | `../oligon-brand/SKILL.md` `<design_foundation>` |

---

## References

- Fujii, R. *Nat Hum Behav* (2026). doi:10.1038/s41562-026-02466-9 — §"Ask whether you really need a figure"; figure-vs-table-vs-dashboard.
- Midway, S. R. *Patterns* **1**, 100141 (2020) — "Principles of Effective Data Visualization": when to use tables vs figures.
- Tufte, E. R. *The Visual Display of Quantitative Information* (Graphics Press, 2001).
- Wilke, C. O. *Fundamentals of Data Visualization* (O'Reilly, 2019).
- WHO COVID-19 dashboard: https://covid19.who.int/ — figure + table combination cited by Fujii 2026.
