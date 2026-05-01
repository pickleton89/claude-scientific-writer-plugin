# Plot Selection Guide — Intent-Driven Chart Choice

> Decision tree for choosing the right plot based on figure intent (Description / Difference / Association) and data structure. Encodes Weissgerber 2015 bar-chart anti-pattern, Fujii 2023 risk-ratio recipe, and direct-labelling guidance from the cognitive-foundation citations.
> Version: 1.1.0
>
> Programmatic counterpart: `../scripts/plotting_params.py::classify_figure_intent`, `recommend_chart`, `recommend_palette`.
>
> **Companion lookup:** Once you know which chart family you want, see `../../shared/references/chart_types_catalog.md` for a flat by-chart-type catalog of 35 chart types with strengths, weaknesses, and data-shape requirements. Use *this* guide when starting from a research question; use the *catalog* when you already know the chart family.

---

## Step 1 — Should this be a figure at all?

Before selecting a plot type, run the figure-vs-table decision:

> See `../../shared/references/figure_vs_table_decision.md`.

If the answer is "table," stop here.

---

## Step 2 — Identify intent (Fujii 2026)

Classify what the figure should communicate:

| Intent | Question the figure answers | Examples |
|---|---|---|
| **Description** | What does the data look like? | Distribution of patient ages, range of expression values, summary of cohort |
| **Difference** | How do groups differ? | Treated vs control, before vs after, knockout vs WT |
| **Association** | How does Y change with X? | Dose-response, correlation, biomarker vs clinical outcome |

Programmatic: `classify_figure_intent("compare gene expression between treated and control")` → `"difference"`.

---

## Step 3 — Match plot type to (intent × data shape)

### Description

| Data shape | Recommended plots | Why |
|---|---|---|
| One continuous variable, n > 30 | Histogram, KDE, ECDF | Distribution shape; KDE smooths bin artefacts; ECDF preserves every point |
| One continuous variable, n < 30 | Strip plot, ECDF | Histograms with few points exaggerate noise |
| Categorical counts | Count bar (acceptable here — data are inherently discrete) | Position-on-aligned-scale wins (Cleveland-McGill 1984); pie chart discouraged for >3 categories |

### Difference (between groups)

| Data shape | Recommended plots | Discouraged | Why |
|---|---|---|---|
| Continuous y, categorical x, unpaired | **Box+jitter** > violin+jitter > strip | Bar chart of means | Bars hide distribution shape (Weissgerber 2015) |
| Continuous y, categorical x, paired | **Paired-points-with-lines** > parallel coordinates | Bar chart | Bars erase pairing structure (Fujii 2026 Fig. 1 §3.i) |
| Risk ratio / odds ratio / hazard ratio with CI | **Pointrange** (point + horizontal CI line) > forest plot for multi-row | **Bar chart** | Bars exaggerate the point estimate at the expense of the CI; wide-CI estimates look deceptively confident as bars (Fujii 2023) |

### Association (between continuous variables)

| Data shape | Recommended plots | Why |
|---|---|---|
| Continuous x, continuous y | Scatter, scatter+regression, hexbin (high density) | Each point is an (x, y) pair; relationship visible directly |
| Continuous x, categorical y | Logistic-regression curve, jittered scatter with logistic fit | Reveals threshold behaviour |

---

## Step 4 — Match colour to scale type

| Scale type | When to use | Recommended palettes |
|---|---|---|
| **Categorical** | Distinguish unrelated groups | `okabe_ito` (≤7 levels), `categorical_8` (Paul Tol, ≤8 levels) |
| **Sequential** | Increasing magnitude (e.g., expression z-score, count density) | `viridis`, `cividis`, Crameri's `batlow` / `roma` |
| **Diverging** | Deviation from a reference point (e.g., log fold change centred at 0) | `heatmap_diverging` (blue-white-red), Crameri `vik` / `bam` |

Programmatic: `recommend_palette("categorical", n_levels=4)` → Okabe-Ito.
**Soft cap:** more than 8 categorical levels exceeds working memory (Cowan 2010); facet or collapse categories.

**Never:** rainbow / jet / Spectral for sequential data — actively distorts perception (Crameri et al. 2020 *Nat Commun*).

---

## Step 5 — Direct labelling, not distant legends

Place labels next to the data they describe. Forced attention shifts between legend and figure increase cognitive load (Fujii 2026 §"Reduce cognitive load"; Wagemans 2012 Gestalt grouping).

### matplotlib

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
line_treated, = ax.plot(x, y_treated, label="Treated")
line_control, = ax.plot(x, y_control, label="Control")

# Direct-label at line endpoints instead of legend
ax.annotate("Treated", xy=(x[-1], y_treated[-1]), xytext=(5, 0),
            textcoords="offset points", color=line_treated.get_color())
ax.annotate("Control", xy=(x[-1], y_control[-1]), xytext=(5, 0),
            textcoords="offset points", color=line_control.get_color())

# Suppress legend
# (no ax.legend() call)
```

### ggplot2

```r
library(ggplot2)
library(ggrepel)  # repels labels away from data points

ggplot(df, aes(x = time, y = value, colour = group)) +
  geom_line(linewidth = 1) +
  # Direct-label at the end of each line
  geom_text_repel(
    data = df %>% filter(time == max(time)),
    aes(label = group),
    nudge_x = 0.5,
    direction = "y",
    hjust = 0
  ) +
  theme(legend.position = "none")
```

---

## Anti-patterns with code recipes

### Anti-pattern 1: Bar chart of continuous data (Weissgerber 2015)

**Wrong** — bars hide distribution shape:

```python
import seaborn as sns
sns.barplot(data=df, x="group", y="biomarker")  # mean ± SEM only — distribution invisible
```

**Right** — show distribution + summary:

```python
import seaborn as sns
ax = sns.boxplot(data=df, x="group", y="biomarker", showfliers=False, width=0.5)
sns.stripplot(data=df, x="group", y="biomarker", color="black", size=3, jitter=0.15, ax=ax)
```

ggplot2 equivalent:

```r
ggplot(df, aes(x = group, y = biomarker)) +
  geom_boxplot(outlier.shape = NA, width = 0.5) +
  geom_jitter(width = 0.15, size = 1.5, alpha = 0.6)
```

### Anti-pattern 2: Bar chart of risk ratios / odds ratios / hazard ratios (Fujii 2023)

**Wrong** — bars exaggerate point estimate:

```python
import matplotlib.pyplot as plt
plt.bar(["A", "B", "C"], [1.2, 2.5, 0.8])
plt.errorbar(["A", "B", "C"], [1.2, 2.5, 0.8], yerr=[[0.3, 1.0, 0.4], [0.3, 1.0, 0.4]])
```

**Right** — points + CI lines:

```python
import matplotlib.pyplot as plt
import numpy as np

groups = np.array(["A", "B", "C"])
hr = np.array([1.2, 2.5, 0.8])
ci_low = np.array([0.9, 1.5, 0.4])
ci_high = np.array([1.5, 3.5, 1.2])

fig, ax = plt.subplots()
ax.errorbar(hr, groups, xerr=[hr - ci_low, ci_high - hr],
            fmt="o", color="black", capsize=4)
ax.axvline(1.0, color="grey", linestyle="--")  # null reference
ax.set_xlabel("Hazard ratio (95% CI)")
ax.set_xscale("log")
```

ggplot2 forest-plot equivalent:

```r
library(ggplot2)
df <- data.frame(group = c("A", "B", "C"),
                 hr = c(1.2, 2.5, 0.8),
                 lower = c(0.9, 1.5, 0.4),
                 upper = c(1.5, 3.5, 1.2))

ggplot(df, aes(x = hr, y = group, xmin = lower, xmax = upper)) +
  geom_pointrange() +
  geom_vline(xintercept = 1, linetype = "dashed", colour = "grey50") +
  scale_x_log10() +
  labs(x = "Hazard ratio (95% CI)", y = NULL)
```

---

## Cross-references

| Topic | See |
|---|---|
| Figure-vs-table decision | `../../shared/references/figure_vs_table_decision.md` |
| Communication-context matrix | `../../shared/references/communication_context_matrix.md` |
| Pre-submission checklist (with #13 = Weissgerber bar-chart, #14 = Fujii risk-ratio) | `../../shared/references/pre_submission_checklist.md` |
| Cognitive-foundation citations | `../../oligon-brand/SKILL.md` `<design_foundation>` |
| Programmatic recommend / validate | `../scripts/plotting_params.py`, `../scripts/validate_data.py` |
| Volcano plots | `volcano_plots.md` |
| Heatmaps | `heatmaps.md` |
| Survival curves | `survival_curves.md` |

---

## References

- Fujii, R. *Nat Hum Behav* (2026). doi:10.1038/s41562-026-02466-9 — intent-first design, communication context, signal-to-noise.
- Fujii, R. *J Epidemiol* **33**, 487–488 (2023) — risk ratios as points + CI not bars.
- Weissgerber, T. L. et al. *PLoS Biol* **13**, e1002128 (2015) — bar charts of continuous data hide distribution.
- Cleveland, W. S. & McGill, R. *J Am Stat Assoc* **79**, 531–554 (1984) — channel ranking.
- Wagemans, J. et al. *Psychol Bull* **138**, 1172 (2012) — Gestalt grouping (direct-label proximity).
- Crameri, F. et al. *Nat Commun* **11**, 5444 (2020) — CVD-safe palettes.
- Cowan, N. *Curr Dir Psychol Sci* **19**, 51 (2010) — working-memory ~4 chunks.
