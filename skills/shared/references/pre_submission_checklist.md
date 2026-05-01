# Pre-Submission Checklist — Scientific Visuals

> 15-point unified quality gate for figures, graphical abstracts, posters, slides, and schematics before submission.
> Version: 1.0.0
> Used by: paperbanana, scientific-schematics, research-posters, plotting-libraries, scientific-slides
>
> **Each item:** check + cognitive principle or journal rule + verification method.

---

## Q0 — Should this be a table instead?

Before working through the rest of the checklist, ask Fujii's question: **does the result actually require a figure?**

- Tables are clearer for: precise numerical values, baseline characteristics, model coefficients with CIs, <5 data points, results readers will quote.
- Figures are clearer for: distributions, correlations, time trends, complex multi-dimensional comparisons.
- Use both (figure + supplementary table; or dashboard) when readers need both pattern recognition and numerical precision.

See `figure_vs_table_decision.md` for the full decision aid. **If the answer is "table," stop here and produce a table.**

> *Why this is Q0:* Fujii (2026) §"Ask whether you really need a figure" — overusing figures can obscure rather than clarify. A figure that should have been a table fails every other check downstream.

---

## Technical Requirements

### 1. Journal policy confirmed

**Check:** Submission guidelines for target venue retrieved and read for figure/GA/poster requirements.
**Why:** Each publisher has venue-specific column widths, DPI floors, GA dimensions, color-space preferences.
**Verify:** Cross-check `venue-templates/references/figure_specs.md` (cross-cutting) and the per-venue file (e.g., `cell_press_style.md`, `nature_science_style.md`).

### 2. Dimensions match column or page width

**Check:** Figure width matches single-column or double-column spec for the target venue.
**Why:** Figures resized at typesetting often lose label legibility.
**Verify:** `JOURNAL_SPECS` in `plotting-libraries/scripts/plotting_params.py` returns width in mm; convert to inches via `mm_to_inches()`.

### 3. Resolution ≥300 DPI for raster

**Check:** Raster outputs (PNG, TIFF, JPEG) are at least 300 DPI; vector outputs (PDF, SVG, EPS) are vector throughout (no embedded rasters at lower DPI).
**Why:** Below 300 DPI, print artefacts appear at journal scale.
**Verify:** `identify -format "%x x %y" figure.png` (ImageMagick) or `pdfimages -list figure.pdf`.

### 4. File size within submission limit

**Check:** Each figure file is under the venue's submission portal limit (commonly ≤20 MB for graphical abstracts, ≤10 MB for main figures).
**Why:** Submission portals reject oversized files.
**Verify:** `ls -lh figure.*`.

---

## Typography

### 5. Type 42 / TrueType font embedding

**Check:** All text is embedded as Type 42 / TrueType, not outlined and not Type 3.
**Why:** Outlined text destroys editability; Type 3 fonts rasterise at low resolutions; both fail typesetting workflows at most major publishers.
**Verify:** `pdffonts figure.pdf` — `type` column shows `Type 42` / `TrueType`, `emb` column shows `yes` for every row. See `venue-templates/references/figure_specs.md` §3 for matplotlib / ggplot2 / Illustrator commands.

### 6. Minimum font size respected

**Check:** Smallest type in the figure (tick labels, annotation) is ≥7 pt at final published size for Nature, ≥6 pt for some venues.
**Why:** Below 6 pt, text becomes illegible at print size and fails accessibility floor.
**Verify:** Open the figure at its final intended print size; if a 7-pt body font is unreadable, the figure text is too small.

---

## Accessibility

### 7. CVD (color-vision-deficiency) safety

**Check:** Figure remains interpretable under deuteranopia, protanopia, and tritanopia simulation.
**Why:** ~8% of male readers have a CVD. Crameri et al. 2020 *Nat Commun* demonstrates rainbow / jet maps actively distort scientific data.
**Verify:** Color Oracle (free desktop simulator), `colorblindcheck` (Python), `colorBlindness::cvdPlot()` (R), or PR Web's CVD simulator. Use `okabe_ito`, `viridis`, or `cividis` palettes by default.

### 8. WCAG 2.1 SC 1.4.3 text contrast ≥4.5:1

**Check:** Text contrast ratio against background ≥4.5:1 (≥3:1 for large text ≥18 pt or 14 pt bold).
**Why:** EU European Accessibility Act (June 2025) and US DOJ ADA Title II rule (April 2024) reference WCAG 2.1 AA.
**Verify:** `colour-contrast-checker` (Python), browser DevTools, or `skills/shared/accessibility/` utilities.

### 9. WCAG 2.1 SC 1.4.11 non-text contrast ≥3:1

**Check:** Lines, shapes, plot elements have ≥3:1 contrast against the background.
**Why:** Same accessibility regulations as above; applies to data marks not just text.
**Verify:** Same tools as #8.

### 10. Two-channel fluorescence uses magenta + green

**Check:** Two-channel fluorescence images use magenta (R + B) + green (G), not red + green.
**Why:** Red + green is unreadable to ~8% of male readers (deuteranopia). Magenta + green preserves visibility.
**Verify:** Confirm channel mapping at image-prep stage; standard in most labs since 2010s.

### 11. Alt text drafted

**Check:** Each panel has 2-sentence alt text describing the **finding** (not the chart mechanics).
**Why:** Required by EU Accessibility Act and US DOJ Title II for journal websites and supplementary HTML; Fujii (2026) §"Reduce cognitive load" + Jambor (2025) reframe alt text as message communication.
**Verify:** See alt-text formula in `venue-templates/references/figure_specs.md` §4. Bad: "Bar chart showing four bars." Good: "Treatment X reduced tumour volume by 60%; combination therapy by 85%."

---

## Scientific Rigor

### 12. Direct labelling preferred over distant legend

**Check:** Lines, groups, and key points are labelled adjacent to the data; legends are placed inside the plotting area or replaced by direct labels.
**Why:** Fujii (2026) §"Reduce cognitive load" — distant legends force readers to shift attention back and forth, increasing cognitive load. Wagemans (2012) Gestalt grouping: spatial proximity binds label to data.
**Verify:** Visual inspection. For matplotlib use `ax.annotate()` or place legend `loc='best'` inside the plot area; for ggplot2 use `geom_text` / `ggrepel::geom_text_repel`.

### 13. Bar charts not used for continuous distributions

**Check:** Continuous data (e.g., individual measurements per group) is shown with box+jitter, violin+jitter, or strip plots — **not** as bar charts of group means.
**Why:** Weissgerber et al. 2015 *PLoS Biol* — bar charts hide the underlying distribution; identical-looking bar charts can come from radically different distributions.
**Verify:** See `plotting-libraries/scripts/validate_figure.py::check_continuous_as_bars` and `plotting-libraries/references/plot_selection_guide.md` for code recipes.

### 14. Risk ratios / odds ratios / hazard ratios shown as points + 95% CI, not bars

**Check:** Point estimates with confidence intervals (forest plots; effect sizes) are drawn as points with horizontal CI lines (`pointrange`), not as bars.
**Why:** Fujii 2023 *J Epidemiol* — bars exaggerate the visual weight of the point estimate at the expense of the CI; a wide-CI estimate looks deceptively confident as a bar.
**Verify:** matplotlib `ax.errorbar(x, y, yerr=...)` or ggplot2 `geom_pointrange(aes(ymin=lower, ymax=upper))`.

---

## Visual Quality

### 15. Iconography licensing verified

**Check:** Every composited icon's source library is identified; attribution strings added to caption; license PDFs saved (BioRender) or DOIs cited (SciDraw).
**Why:** Most journals require explicit attribution for CC-BY assets; BioRender requires an active subscription seat at submission time.
**Verify:** See `iconography-licensing.md` per-library checklists.

---

## Putting it together

Run this checklist as a **post-design gate** (after the figure is complete) and as a **pre-submission gate** (immediately before manuscript upload). Some items (e.g., font embedding, alt text) commonly slip between draft and submission.

### Tooling cross-references

| Item | Programmatic check |
|---|---|
| #2 Dimensions | `plotting-libraries/scripts/plotting_params.py::get_figsize_for_journal()` |
| #5 Font embedding | `pdffonts <file.pdf>` |
| #7 CVD simulation | `skills/shared/accessibility/` utilities |
| #8–9 Contrast | `skills/shared/accessibility/` utilities |
| #13 Continuous-as-bars | `plotting-libraries/scripts/validate_figure.py::check_continuous_as_bars` |
| #14 Risk-ratio-as-bars | `plotting-libraries/scripts/validate_figure.py::check_riskratio_as_bars` |

---

## References

- Fujii, R. *Nat Hum Behav* (2026). doi:10.1038/s41562-026-02466-9 — Q0 figure-vs-table; direct labelling; signal-to-noise.
- Fujii, R. *J Epidemiol* **33**, 487–488 (2023) — risk ratios as points + CI not bars.
- Weissgerber, T. L., Milic, N. M., Winham, S. J., Garovic, V. D. *PLoS Biol* **13**, e1002128 (2015) — bar charts hide distributions.
- Jambor, H. K. *Nat Cell Biol* **27**, 879–883 (2025) — figure accessibility, alt-text formula.
- Crameri, F., Shephard, G. E., Heron, P. J. *Nat Commun* **11**, 5444 (2020) — CVD-safe palettes.
- Wagemans, J. et al. *Psychol Bull* **138**, 1172 (2012) — Gestalt grouping.
- WCAG 2.1 SC 1.4.3 (text contrast), SC 1.4.11 (non-text contrast): https://www.w3.org/TR/WCAG21/
- EU Directive 2019/882 (European Accessibility Act), in force 28 June 2025.
- US DOJ ADA Title II web accessibility rule (28 CFR 35.200), April 2024.
