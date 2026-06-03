# Oligon Scientific Brand — Figure & Color Reference

**Version 5.0 — aligned with Oligon Digital Style Guide v2.3 (April 2026).**

Canonical reference for figures, charts, diagrams, and slides. Source of
truth: `Oligon_Digital_Style_Guide_v2.3.html`. Machine-readable tokens:
`tokens/brand-tokens.json`. Code adapters: `adapters/`.

Core principle: **Neutrals are default; Brand Blue highlights the one or
two elements that matter most; Orange supplies opposition or focus.**

---

## 0. Logo & Brand Mark

Oligon logo files live in `assets/`. The wordmark uses Brand Blue
`#2DB2E8` on light grounds and white `#FFFFFF` on Blue 700+ or Neutral
800+ grounds.

### Variants

| Variant | Use | Dimensions |
|---------|-----|------------|
| Full wordmark | Headers, presentations, documents | 622 × 263 viewBox |
| Icon only     | Favicons, app icons, small spaces | 500 × 375 viewBox |

### Minimum sizes (from §01 of v2.3)

| Use                     | Minimum width | Clear space         |
|-------------------------|---------------|---------------------|
| Digital header / web    | 120 px        | ½× logo height      |
| Presentation corner     | 100 px / 1.0″ | ½× logo height      |
| Document footer         | 80 px / 0.8″  | ½× logo height      |
| Icon mark standalone    | 24 px         | ¼× icon height      |

### Usage rules

- **Do** use Brand Blue wordmark on white, Neutral 50, or Neutral 100.
- **Do** use White wordmark on Blue 700+ or Neutral 800+.
- **Do not** rotate, skew, or place on low-contrast tinted backgrounds
  (Blue 300–500).
- **Do not** include logos on publication figures — journals prohibit
  branding. Use only on presentations, posters, and internal documents.

SVG sources for all four logo variants (full-blue, full-white,
icon-blue, icon-white) live in the `assets/` directory alongside this
file. Do not embed them inline in this reference.

---

## 1. Color System — Oklch Tonal Ramps

Three perceptually-uniform Oklch ramps span 10 steps each (50 → 900).
Every step has a defined semantic role; adjacent steps are perceptually
equidistant.

### Blue ramp

| Step | Hex      | Role |
|:----:|:---------|------|
| 50   | `#EFFBFF` | Callout background, lightest fill |
| 100  | `#DBF3FF` | Callout background; light fill surface |
| 200  | `#B3E3FC` | Peer lightest arm; Focus receding |
| 300  | `#76CAF3` | Cycle 1 control; Focus receding |
| 400  | `#1FACE3` | Primary data default (Oklch twin of brand.blue) |
| 500  | `#008ECB` | Focus receding; Cycle 4 mid arm; emphasis |
| 600  | `#006EA6` | Cycle 3 negative; CTA hover |
| 700  | `#00507E` | Accent (links, primary buttons); divergent negative |
| 800  | `#003454` | Peer darkest arm; Cycle 4 dark; dark-theme surface |
| 900  | `#001A2E` | Dark-theme page background |

### Orange ramp

| Step | Hex      | Role |
|:----:|:---------|------|
| 50   | `#FFF5F1` | Warning callout background |
| 100  | `#FFE8E0` | Don't-do box background |
| 200  | `#FFCEBD` | Light warning fill |
| 300  | `#F0AA92` | Soft focus fill |
| 400  | `#DD8363` | Focus soft promotion |
| 500  | `#C45E39` | Focus default promotion; Cycle 4 outlier |
| 600  | `#A0421D` | Cycle 3 positive; volcano up-regulated |
| 700  | `#772E11` | Signal/destructive; divergent positive |
| 800  | `#4F1B06` | Deep signal, rare dark accent |
| 900  | `#2B0901` | Deepest warm |

### Neutral ramp

| Step | Hex      | Role |
|:----:|:---------|------|
| 50   | `#F3FAFD` | Surface fill; dark-theme text |
| 100  | `#E9F0F3` | Secondary button fill, subtle surface |
| 200  | `#D6DCDF` | Borders, rules, axis furniture, gridlines |
| 300  | `#B9BFC2` | Volcano non-significant; de-emphasized |
| 400  | `#9A9FA2` | Neutral callout border, annotation mid |
| 500  | `#7C8184` | Caption placeholder, disabled |
| 600  | `#5F6467` | Caption text on light |
| 700  | `#44494B` | Secondary text (`text.muted`); axis furniture dark |
| 800  | `#2A2F31` | High-contrast text on light |
| 900  | `#121719` | Body text on light (default) |

### Brand anchor

| Name       | Hex      | Role |
|------------|----------|------|
| Brand Blue | `#2DB2E8` | Logo wordmark; Cycle 1 treatment arm |

Brand Blue is the Oklch twin of Blue 400 `#1FACE3` — the 1-unit drift
is below perceptual threshold. Use Brand Blue for logos and Cycle 1
treatment; use ramp steps everywhere else.

---

## 2. Semantic Tokens

Bind primitives to roles so a single token change propagates everywhere.

### Light theme

| Token        | Source      | Hex       | Role |
|--------------|-------------|-----------|------|
| `page`       | white       | `#FFFFFF` | Document / app background |
| `surface`    | neutral.50  | `#F3FAFD` | Cards, callouts, zebra rows |
| `border`     | neutral.200 | `#D6DCDF` | Rules, input borders |
| `text`       | neutral.900 | `#121719` | Body copy |
| `text.muted` | neutral.700 | `#44494B` | Secondary text, captions |
| `accent`     | blue.700    | `#00507E` | Links, primary button |
| `brand`      | brand.blue  | `#2DB2E8` | Logo, Cycle 1 treatment arm |
| `signal`     | orange.700  | `#772E11` | Warnings, destructive |

### Dark theme

| Token     | Source      | Hex       | Role |
|-----------|-------------|-----------|------|
| `page`    | blue.900    | `#001A2E` | Dark page background |
| `surface` | blue.800    | `#003454` | Elevated cards |
| `text`    | neutral.50  | `#F3FAFD` | Body text on dark |
| `accent`  | blue.300    | `#76CAF3` | Links on dark |
| `brand`   | brand.blue  | `#2DB2E8` | Brand accent on dark (7.28:1) |

---

## 3. Scientific Data Visualization — Two Decision Rules

Every chart color choice is deterministic once you have answered Rule 1
and Rule 2.

### Rule 1 — Choose the Cycle

Pick the cycle that matches your data's categorical structure.

| If your data is…                                         | Use cycle                        | Rationale |
|----------------------------------------------------------|----------------------------------|-----------|
| Two arms, one carries the narrative (treatment vs control) | **Cycle 1 · Treatment/Control**  | Same-hue pair with lightness hierarchy |
| N arms, one carries the narrative answer                 | **Cycle 2 · Focus**              | Three background arms + one promoted focus |
| N arms, all equal weight — no focus                      | **Cycle 2 · Peer**               | Blue ramp at stepped lightness; no promotion |
| Signed / directional effects (up vs down, gain vs loss)  | **Cycle 3 · Opposing**           | Blue + Orange paired across the ramp |
| Continuous signed scalar (heatmap z-scores)              | **Cycle 3 · Divergent**          | Blue 700 → white → Orange 700 |
| 3–4 categories with one conceptual outlier               | **Cycle 4 · Multi-Category**     | Step-spaced Blue + Orange for outlier |

> **The Focus-vs-Peer branch.** Before reaching for Cycle 2, ask: does
> any arm carry the narrative answer? If yes, Focus. If no, Peer.
> Never promote an arm arbitrarily just because the palette has a
> focus slot.

#### Cycle 1 — Treatment / Control

Two-arm studies. Same-hue palette with lightness doing the hierarchy
work — treatment at saturated Brand Blue, control as a lighter tint of
the same hue.

| Order | Color     | Hex       | Role |
|:-----:|-----------|-----------|------|
| 1     | Brand Blue | `#2DB2E8` | Treatment / experimental line |
| 2     | Blue 300  | `#76CAF3` | Control / baseline line |

```python
CYCLE_TREATMENT_CONTROL = ['#2DB2E8', '#76CAF3']
```

> **CI bands are not drawn by default on line plots** — see §8.0. If the
> user explicitly requests bands, they are rendered as a tint of each arm's
> *own* line color at α ≈ 0.18 (matching-hue rule). Do not use `blue.100`
> as a shared CI-band fill — that produces a muddy overlap where treatment
> and control bands fuse.

#### Cycle 2 — Peer

Equal-weight peer comparisons where no arm carries the narrative.
Lightness distinguishes without ranking. Good default for sibling
siRNAs, cell lines, dose levels where ordering is arbitrary.

| Arms | Ramp steps | Hex |
|:----:|-----------|-----|
| 4    | blue.800 / 600 / 400 / 200 | `#003454` / `#006EA6` / `#1FACE3` / `#B3E3FC` |
| 3    | blue.700 / 500 / 300       | `#00507E` / `#008ECB` / `#76CAF3` |

```python
CYCLE_PEER_4 = ['#003454', '#006EA6', '#1FACE3', '#B3E3FC']
CYCLE_PEER_3 = ['#00507E', '#008ECB', '#76CAF3']
```

#### Cycle 2 — Focus

N arms with one promoted. Three background arms in receding Blue +
one focus variant.

| Step     | Color     | Role |
|----------|-----------|------|
| Receding 1 | Blue 500 | Background arm (darkest receding) |
| Receding 2 | Blue 300 | Background arm |
| Receding 3 | Blue 200 | Background arm (lightest receding) |

**Focus variants** (pick one for the promoted arm):

| Variant        | Color       | Hex       | Use |
|----------------|-------------|-----------|-----|
| Default        | Orange 500  | `#C45E39` | Saturated hue contrast. Use when focus is categorically different. |
| Soft           | Orange 400  | `#DD8363` | Less saturated; focus present but quieter. |
| Monochromatic  | Blue 800    | `#003454` | Dark lightness alone. Use when focus is "more of the same" rather than different in kind (e.g., highest dose in a dose-response). |

```python
CYCLE_FOCUS_RECEDING = ['#008ECB', '#76CAF3', '#B3E3FC']
FOCUS_VARIANTS = {
    'default':       '#C45E39',  # orange.500
    'soft':          '#DD8363',  # orange.400
    'monochromatic': '#003454',  # blue.800
}
```

#### Cycle 3 — Opposing

Signed or directional data. Avoids red/green colorblind confusion.

| Order | Color      | Hex       | Role |
|:-----:|------------|-----------|------|
| 1     | Blue 600   | `#006EA6` | Direction A (e.g., down-regulated) |
| 2     | Orange 600 | `#A0421D` | Direction B (e.g., up-regulated) |
| 3     | Neutral 300 | `#B9BFC2` | Non-significant / unchanged |

```python
CYCLE_OPPOSING = ['#006EA6', '#A0421D', '#B9BFC2']
```

#### Cycle 3 — Divergent colormap

For heatmaps with data centered at zero (z-scores, log2 fold change).
Matched lightness curves on both ramps keep perceptual distance from
zero symmetric.

| Position | Color      | Hex       | Label |
|:--------:|------------|-----------|-------|
| 0.0      | Blue 700   | `#00507E` | Extreme negative |
| 0.5      | White      | `#FFFFFF` | Zero / neutral |
| 1.0      | Orange 700 | `#772E11` | Extreme positive |

```python
from matplotlib.colors import LinearSegmentedColormap
brand_divergent = LinearSegmentedColormap.from_list(
    'brand_divergent',
    [(0.0, '#00507E'), (0.5, '#FFFFFF'), (1.0, '#772E11')]
)
```

Implementation requirements:

1. Center the colormap at zero — do not let auto-scaling shift the
   neutral point.
2. Use symmetric limits (e.g. `vmin=-5, vmax=5`) even if data spans
   `-3 to +5`.
3. Always include a colorbar with ticks at meaningful intervals.

#### Cycle 4 — Multi-Category

3–4 categories with one conceptually distinct (e.g., vehicle vs
compounds). If all categories are peers, use **Cycle 2 · Peer** instead.

| Order | Color      | Hex       | Role |
|:-----:|------------|-----------|------|
| 1     | Blue 800   | `#003454` | Peer category (dark) |
| 2     | Blue 500   | `#008ECB` | Peer category (mid) |
| 3     | Blue 300   | `#76CAF3` | Peer category (light) |
| 4     | Orange 500 | `#C45E39` | Conceptual outlier |

Marker shapes MANDATORY for accessibility: `['o', 's', '^', 'D']`.
If 5+ categories, redesign using faceting or small multiples.

```python
CYCLE_MULTI_CATEGORY = ['#003454', '#008ECB', '#76CAF3', '#C45E39']
MARKER_SHAPES = ['o', 's', '^', 'D']
```

### Rule 2 — Choose the Ramp Step

| Step        | Role                         | Where |
|:------------|------------------------------|-------|
| 50 – 200    | Fills, tints, surfaces       | CI bands, box fills, callout backgrounds |
| 300         | Light data strokes           | Cycle 1 control, Cycle 2 Focus receding arms |
| 400         | Primary data                 | Default for lines and markers |
| 500 – 600   | Emphasis / button fills      | CTAs, hover states |
| 700         | Text, borders, links         | Axis titles on light theme; heatmap extremes |
| 800 – 900   | Dark page, deepest contrast  | Dark-theme background; monochromatic Focus promotion |

---

## 4. Figure Integrity — Eight Rules

These rules govern what a figure is allowed to claim visually.
Violating any of them misrepresents the data, regardless of how
well-styled the figure looks.

1. **Zero baseline on bar charts.** Bars encode quantity by length; a
   truncated y-axis inflates differences. If truncation is unavoidable
   (tight effect on a large background), switch to a dot plot or
   Cleveland dot plot rather than a truncated bar.

2. **Log scales labeled as such.** Axis title reads
   `log10 concentration (nM)` or equivalent, with one tick per decade
   as the base case. Never a silent log transform.

3. **Uncertainty is shown.** Caption CI values, at-risk / n-per-arm
   tables, inline error-bar markers, or individual points overlaid on
   summary statistics. Shaded CI bands on line plots are **not** the
   default — see §8.0. The CI definition (SD, SEM, or 95% CI) is stated
   in the caption or legend, never left to the reader to guess.

4. **No 3D effects on 2D data.** 3D bars, 3D pies, and drop shadows
   distort perceived area and introduce perspective error. Flat, 2D,
   always.

5. **No rainbow / jet colormaps on continuous data.** Rainbow has no
   perceptual ordering, introduces false luminance bands, and fails
   both CVD and grayscale. Use viridis-family or the §3 divergent
   cycle for continuous scalars.

6. **No category encoded by hue alone.** Combine color with shape
   (circle / square / triangle), line style, or direct label, so the
   encoding survives grayscale printing, low-quality projection, and
   color vision deficiency.

7. **Isotype charts replicate 1:1.** To show a 5:1 ratio, draw five
   icons beside one icon — never one icon scaled 5× larger. Scaling a
   single icon by height inadvertently scales area and visually
   overstates the difference.

8. **No dual y-axes without justification.** Dual y-axes invite
   spurious visual correlation between series scaled independently.
   Reach for small multiples or a twin-panel layout first.

---

## 5. Typography

Arial / Helvetica for screen; DejaVu Sans as the cross-platform render
target for matplotlib and ReportLab.

### Document type scale

| Role    | Size             | Weight | Color        |
|---------|------------------|:------:|--------------|
| H1      | 28 pt            | 800    | brand.blue   |
| H2      | 19 pt            | 700    | brand.blue   |
| H3      | 14 pt uppercase  | 700    | neutral.900  |
| Body    | 14 pt / 1.55     | 400    | neutral.900  |
| Caption | 11 pt            | 400    | neutral.600  |

### Figure type scale (document scale — print, PDF, web, 60–80 cm reading)

| Role       | Size       | Weight |
|------------|------------|:------:|
| Title      | 12 pt      | 700    |
| Axis label | 10 pt      | 500    |
| Tick label | 9 pt       | 400    |
| Legend     | 8.5–9 pt   | 400    |

### Projection type scale (conference rooms, lecture halls)

Figures embedded in projected slides follow these minimums rather than
the document figure scale — a 9 pt tick label that reads fine on a
laptop disappears from the back row of a conference room.

| Role                     | Size  |
|--------------------------|:-----:|
| Body                     | 18 pt |
| Heading                  | 28 pt |
| Axis labels on embedded figures | 18 pt |

If a data figure's native axis labels fall below 18 pt at projected
scale, re-label them natively in PowerPoint or scale the figure up
before exporting.

---

## 6. Layout

| Parameter         | Value |
|-------------------|-------|
| Aspect ratio      | Match to the data, not the canvas. Trend data banked so the mean slope sits near 45° (Cleveland). Categorical comparisons tolerate squarer ratios (4:3, 3:2). Do **not** stretch/squash to fill slide real estate. |
| Spines            | Left + bottom only (top + right hidden) |
| Gridlines         | Horizontal, neutral.200, 0.5 pt, dashed, off by default |
| Data line width   | 1.8–2.2 pt primary; 1.0–1.6 pt secondary |
| Markers           | 5–6 pt filled circles; white outline on colored fills |
| Resolution        | 300 dpi PNG + SVG/PDF vector |

### Output resolution

| Context               | Resolution             | Formats |
|-----------------------|------------------------|---------|
| Print / publication   | 300 dpi (600 for line art) | PDF, SVG, EPS, TIFF |
| Screen / presentation | 150 dpi                 | PNG, PDF |
| Web / preprint        | 150 dpi                 | PNG, SVG |

Vector formats (PDF, EPS, SVG) are preferred for line-based figures —
they scale without quality loss.

---

## 7. Accessibility

Palette is validated against WCAG 2.1 Level AA. Most pairs below
reach AAA. Blue and Orange ramps share Oklch lightness curves, so
simulated-colorblind rendering preserves the blue-orange axis as a
dark-light differential under deuteranopia and protanopia.

### Light-theme contrast pairs

| Pair                      | Ratio   | Level | Use |
|---------------------------|---------|-------|-----|
| `#121719` on `#FFFFFF`    | 18.07:1 | AAA   | Body text on page |
| `#44494B` on `#FFFFFF`    | 9.13:1  | AAA   | Secondary text on page |
| `#00507E` on `#FFFFFF`    | 8.58:1  | AAA   | Links / CTA text |
| `#FFFFFF` on `#00507E`    | 8.58:1  | AAA   | Button label on Blue 700 |
| `#FFFFFF` on `#772E11`    | 9.62:1  | AAA   | Accent button on Orange 700 |

### Dark-theme contrast pairs

| Pair                      | Ratio   | Level | Use |
|---------------------------|---------|-------|-----|
| `#F3FAFD` on `#001A2E`    | 16.76:1 | AAA   | Body text on dark page |
| `#76CAF3` on `#001A2E`    | 9.70:1  | AAA   | Links / eyebrows on dark |
| `#2DB2E8` on `#001A2E`    | 7.28:1  | AAA   | Brand accent on dark |

### Figure publication checklist

Before publishing a figure:

1. Grayscale version still interpretable.
2. No category encoded by hue alone — shape, line style, or label also
   distinguishes.
3. All text ≥ 9 pt at rendered size, AA contrast verified.
4. Exported as 300 dpi PNG + vector (SVG/PDF).
5. Cycle documented in caption or YAML metadata.
6. Alt text describes the **finding**, not the chart type. Write
   "Bar chart shows a 2-fold increase in cell viability for the
   treatment group" — not "image of a bar chart."

### Testing tools

- [Coblis Colorblind Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)
- [Viz Palette](https://projects.susielu.com/viz-palette)
- matplotlib `colorspacious` package (pip install colorspacious)
- The bundled `matplotlib_adapter.validate_palette()` returns
  per-color lightness deltas so CVD survival can be predicted
  before rendering

---

## 8. Canonical Plot Templates

Per-chart-type recipes for the most common scientific visualizations.
Each entry fixes the cycle, line widths, marker sizes, and annotation
placement so two analysts produce the same figure from the same data.

### 8.0 Universal rule — no CI bands on line plots by default

**Oligon house rule.** Line plots (Kaplan–Meier step curves, tumor-volume
time courses, PK curves, dose-response fits, longitudinal means, and any
other mean-over-time rendering) are **lines-only by default**. No shaded
CI bands on the plot unless the user explicitly asks for them. Uncertainty
is shown in one of three ways:

1. **Caption** — report endpoint ± 95% CI values, e.g., "Day-28 mean (95% CI):
   treatment 312 mm³ (268–356); vehicle 584 mm³ (510–658)."
2. **At-risk / n-per-arm table** beneath the x-axis for KM or repeated-measures
   plots where the sample size changes over time.
3. **Inline error markers** at discrete timepoints — thin vertical SEM or
   95% CI whiskers on the mean points, without extending the band across
   the whole x range.

**Rationale.** CI bands around every line crowd the canvas, draw attention
to the overlap zone rather than the group difference, and train readers to
read uncertainty qualitatively when the caption already states it
quantitatively. Oligon house style keeps the plot surface for the signal
and puts the noise in text. Figure-integrity rule #3 (uncertainty must be
shown) is satisfied by the caption, not by filled bands.

**Honor explicit user CI requests.** If the user explicitly asks for CI
bands on the plot — whether they say "semi-transparent fills," "shaded CI,"
"CI bands," "confidence bands," "95% CI ribbon," or something clearly
equivalent — draw the bands. The user's stated preference wins over the
house default. When drawing bands:

- Use **matching-hue tints** at α=0.18. Each band is a tint of its own
  line color (brand.blue line → brand.blue band; blue.300 line → blue.300
  band). Do NOT fill all bands with a shared `blue.100` — that muddies
  the overlap and misrepresents uncertainty as a shared quantity.
- State in the caption what the bands represent (95% CI, SEM, or SD).
- Use `add_error_band(ax, x, y, yerr, color=line_color)` from
  `matplotlib_adapter`, which handles the matching-hue tint correctly in
  one call.

### 8.1 Kaplan–Meier survival curves

**Context:** Comparing survival between treatment arms.

**Cycle:** Cycle 1 · Treatment/Control.

KM follows the universal rule in §8.0 — step curves by default, no CI bands
on the plot unless the user asks for them. Uncertainty is shown via (a) a
**numbers-at-risk table** below the x-axis and (b) day-endpoint 95% CI
values in the figure caption. This preserves figure-integrity rule #3
without visually crowding the step events, which is what matters clinically.
When the user requests bands, use matching-hue tints at α=0.18 per §8.0;
the at-risk table becomes optional but is still recommended.

| Element              | Color / spec                                    |
|----------------------|-------------------------------------------------|
| Treatment curve      | `brand.blue` `#2DB2E8`, solid, 2.0–2.2 pt, `ax.step(where='post')` |
| Control / vehicle curve | `blue.300` `#76CAF3`, solid, 2.0 pt, `ax.step(where='post')` |
| Additional arm (rare) | Cycle 3 `orange.600` `#A0421D` if opposing effect |
| Confidence bands (default) | **None on plot.** Report endpoint 95% CI in caption |
| Confidence bands (on user request) | Matching-hue tint of the line color at α=0.18 via `add_error_band(ax, x, y, yerr, color=line_color)` |
| Censored tick marks  | `neutral.900` `#121719`, short vertical ticks   |
| Median-survival guide | `neutral.400` dashed, 0.5 pt                   |
| At-risk table        | `neutral.900` text; group labels in arm colors; below x-axis |

- Always use `ax.step(..., where='post')` — KM curves are step functions,
  not smooth interpolations.
- Include the numbers-at-risk table by default. Two rows, one per arm,
  with the arm label in its line color (bold for the hero arm). When CI
  bands are drawn on user request, the table becomes optional.
- Caption must name the CI definition (e.g., "Day-90 95% CI: arm A 0.50–0.78;
  arm B 0.14–0.45"). See the worked example in `oligon-brand-core/assets/`.
- Place p-value and hazard ratio in upper-right or lower-left in 9 pt.
- X-axis: `Time (days)` or appropriate unit; Y-axis: `Survival probability`.

> **The no-CI-band-by-default rule is universal across line plots** (§8.0)
> — it is not specific to KM. It applies equally to tumor-volume time
> courses, PK curves, dose-response fits, and longitudinal means. An
> explicit user request overrides it in every case.

### 8.2 Volcano plots

**Context:** Differential expression (fold change vs significance).

**Cycle:** Cycle 3 · Opposing + non-significant neutral.

| Element                  | Color            | Hex       |
|--------------------------|------------------|-----------|
| Non-significant          | `neutral.300`    | `#B9BFC2` |
| Significant up-regulated | `orange.600`     | `#A0421D` |
| Significant down-regulated | `blue.600`      | `#006EA6` |
| Threshold lines          | `neutral.500`    | `#7C8184` dashed, 0.5 pt |
| Labeled genes            | `neutral.900`    | `#121719` 9 pt, with leader lines if needed |

- Non-significant points: `s=12, alpha=0.6`.
- Significant points: `s=20, alpha=0.85`.
- X-axis: `log₂(Fold Change)`; Y-axis: `-log₁₀(p-value)` or `-log₁₀(FDR)`.
- Use symmetric x-axis limits.

### 8.3 Dose–response curves

**Context:** IC50 / EC50, drug sensitivity.

**Cycle:** Cycle 4 · Multi-Category when comparing compounds + vehicle;
Cycle 1 when comparing a single drug vs vehicle.

| Element           | Color              | Marker / style |
|-------------------|--------------------|----------------|
| Compound A        | `blue.800` `#003454` | Circle, solid 2.0 pt |
| Compound B        | `blue.500` `#008ECB` | Square, solid 2.0 pt |
| Compound C        | `blue.300` `#76CAF3` | Triangle, solid 2.0 pt |
| Vehicle control   | `orange.500` `#C45E39` | Diamond, dotted 1.6 pt |
| 95 % CI bands (default) | **None on plot** per §8.0. Report IC50 ± 95% CI in caption | |
| 95 % CI bands (on user request) | Matching hue, α=0.18, no border | |
| IC50 guide line   | `neutral.400` | Horizontal dashed, 0.5 pt |

- X-axis: `log10 concentration (nM)` (per §4 Rule 2: log scales
  labeled, one tick per decade).
- Y-axis: `% Viability` or `% Response`.
- Annotate IC50 values with vertical droplines or inline text at 9 pt.

### 8.4 Grouped bar charts

**Context:** Comparing discrete measurements across conditions.

**Cycle:** Cycle 1 for highlighted comparison, Cycle 2 · Peer for
equal-weight peers.

| Element            | Spec |
|--------------------|------|
| Bar fill           | Cycle color at full saturation (no outline) |
| Bar edge           | `none` — data-ink economy |
| Error bars         | 0.75 pt, same color as bar or `neutral.900` |
| Zero baseline      | **Always shown.** Per §4 Rule 1, no truncation. |
| Individual points  | Overlay at α=0.6 when n < 20 — uncertainty rule §4.3 |
| Group ordering     | Biological condition (e.g., cell line) on x-axis; treatment as hue |

- Prefer dot plots or Cleveland dot plots for n < 10.
- State error-bar definition (SD / SEM / 95 % CI, n) in caption — §4 Rule 3.

### 8.5 Box / violin plots

**Context:** Distribution comparisons (e.g. immune populations).

**Cycle:** Cycle 2 · Peer when arms are equal weight; Cycle 4 ·
Multi-Category when one arm is categorically different.

| Element           | Spec |
|-------------------|------|
| Box / violin fill | Cycle color at α=0.50 |
| Median line       | `neutral.900` solid, 1.0 pt |
| Whiskers          | `neutral.900` 0.8 pt |
| Outliers          | Same color as fill, marker size 3 pt |
| Jittered points   | Fill color at α=0.50 over the box |

### 8.6 Divergent heatmaps

**Context:** Z-scored expression, log2 fold-change tiles.

**Cycle:** Cycle 3 · Divergent (see §3 for the 3-stop colormap).

| Element             | Spec |
|---------------------|------|
| Colormap            | `blue.700` → white → `orange.700`, linear sRGB |
| Center              | Forced at zero (`vcenter=0`, symmetric `vmin/vmax`) |
| Colorbar            | Always included, ticks at meaningful intervals |
| Row / column labels | `neutral.900` 9 pt |
| Dendrogram lines    | `neutral.700` 0.5 pt |
| Missing values      | `neutral.200` hatched fill |

### 8.7 Flow cytometry histograms

**Context:** Marker expression across conditions.

**Cycle:** Cycle 1 when one condition is the focus; Cycle 3 · Opposing
when comparing populations with opposing shifts.

| Element               | Color                 | Spec |
|-----------------------|-----------------------|------|
| Isotype / FMO control | `neutral.300` `#B9BFC2` | α=0.5 fill, behind |
| Untreated / baseline  | `blue.300` `#76CAF3`  | α=0.5 fill |
| Treatment             | `brand.blue` `#2DB2E8` | α=0.5 fill, on top |
| Secondary (opposing)  | `orange.600` `#A0421D` | α=0.5 fill |
| Gate boundaries       | `neutral.900` `#121719` | Thin solid 0.8 pt |

- Order overlays with controls behind, treatment in front.
- Annotate MFI values inline or in legend at 9 pt.

---

## 9. Code Implementation

### matplotlib / seaborn

```python
import sys
sys.path.insert(0, 'skills/oligon-brand/adapters')

from matplotlib_adapter import (
    set_brand_style, select_cycle,
    BRAND_BLUE, BLUE_300, BLUE_600, BLUE_700,
    ORANGE_500, ORANGE_600, ORANGE_700,
    NEUTRAL_300, NEUTRAL_700, NEUTRAL_900,
    CYCLE_TREATMENT_CONTROL, CYCLE_OPPOSING,
    CYCLE_PEER_4, CYCLE_FOCUS, CYCLE_MULTI_CATEGORY,
    get_divergent_cmap, run_preflight, validate_palette,
)

# Rule 1: pick cycle from data
cycle_name, colors = select_cycle(n_series=2, context='comparison')

# Apply brand defaults
set_brand_style(cycle_name)

fig, ax = plt.subplots(figsize=(5, 3.75))

# Default: lines only, no CI bands (see §8.0).
# Report endpoint ± 95% CI in the caption, not on the plot.
ax.plot(time, treatment, color=BRAND_BLUE, linewidth=2.0, label='Treatment')
ax.plot(time, control,   color=BLUE_300,  linewidth=2.0, label='Control')

# On explicit user request for CI bands — matching-hue tints at α=0.18:
# add_error_band(ax, time, treatment, tx_err,   color=BRAND_BLUE, label='Treatment')
# add_error_band(ax, time, control,   ctrl_err, color=BLUE_300,  label='Control')

# Validate
assert all(run_preflight(fig).values())
```

### ggplot2

```r
source("skills/oligon-brand/adapters/ggplot2_adapter.R")

ggplot(df, aes(time, value, color = arm)) +
  geom_line(linewidth = 0.7) +
  scale_color_brand_treatment() +
  theme_brand()
```

---

## 10. Pre-flight Checklist

Before submitting any figure:

- [ ] White background (`#FFFFFF`) / brand ground (blue.900 for dark theme)
- [ ] Axis furniture in neutral.200–300; text in neutral.900 on light,
      neutral.50 on dark
- [ ] Top and right spines removed
- [ ] Correct cycle for scientific context (Rule 1) and correct ramp
      step for visual role (Rule 2)
- [ ] Brand Blue limited to 1–2 focal elements per panel
- [ ] No library default colors; no retired v4 hexes (`#E8622D`,
      `#7D250F`, `#0F5D7D`, `#158BBB`, `#222222`)
- [ ] Redundant encoding present (shapes/styles with color)
- [ ] Tested in grayscale and under CVD simulation
- [ ] Uncertainty rendered and labeled (SEM/SD/95 % CI, n=?)
- [ ] Font Arial/Helvetica/DejaVu Sans; figure scale 9–12 pt,
      projection scale ≥ 18 pt
- [ ] Resolution ≥ 300 DPI for print; vector preferred for line art
- [ ] Alt text describes the finding, not the chart type

---

## 11. Migration from v4.x → v5.0

If your code still references v4 color names or hexes:

| v4 token / hex              | v5.0 equivalent            |
|-----------------------------|----------------------------|
| `contrast_orange` / `#E8622D` | `orange.600` / `#A0421D` |
| `dark_warm` / `#7D250F`      | `orange.700` / `#772E11` or `orange.800` / `#4F1B06` |
| `dark_teal` / `#0F5D7D`      | `blue.800` / `#003454`   |
| `medium_blue` / `#158BBB`    | `blue.500` / `#008ECB`   |
| `dark_gray` / `#222222`      | `neutral.900` / `#121719` |
| `medium_gray` / `#666666`    | `neutral.700` / `#44494B` |
| `muted_gray` / `#999999`     | `neutral.500` / `#7C8184` |
| `light_gray` / `#BDBDBD`     | `neutral.300` / `#B9BFC2` |
| Cycle 1 `[#222222, #2DB2E8, #666666]` | Cycle 1 `[brand.blue, blue.300, blue.100]` |
| Cycle 3 `[#2DB2E8, #E8622D, #222222]` | Cycle 3 `[blue.600, orange.600, neutral.300]` |
| Cycle 4 `[..., #158BBB]`      | Cycle 4 `[blue.800, blue.500, blue.300, orange.500]` |
| 5-stop divergent              | 3-stop `blue.700 → white → orange.700` |

Adapters in `adapters/*.py` / `*.R` / `*.css` keep deprecated names
as aliases that route to v5.0 ramp equivalents, so existing call
sites continue to work — but prefer the ramp-step names in new code.

---

## Version history

| Version | Date      | Changes |
|---------|-----------|---------|
| 1.0 – 3.0 | —       | Initial releases; neutrals-first philosophy; accessibility standards |
| 4.0     | —         | Scenario-specific color cycles, canonical bio-plot templates (K-M, volcano, dose-response, flow), grayscale testing |
| 4.1     | 2026-04-22 | Visual-design skill retired; design-foundation block moved to SKILL.md |
| **5.0** | **2026-04-22** | **v2.3 Oklch ramps, Peer vs Focus split, 3-stop divergent, document/figure/projection type scales, figure integrity rules, semantic tokens + dark theme** |
