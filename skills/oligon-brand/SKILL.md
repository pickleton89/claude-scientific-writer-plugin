---
name: oligon-brand
version: 5.0.0
description: Use when applying Oligon brand colors, typography, figure standards, voice rules, or medium layouts to any scientific or communications deliverable — matplotlib/ggplot2 plots, Kaplan-Meier curves, volcano plots, heatmaps, branded PowerPoint decks, Word documents, PDF reports, HTML pages, social posts, or email. Implements Oligon Digital Style Guide v2.3 with Oklch tonal ramps, same-hue Cycle 1, Peer/Focus cycle split, and format adapters for matplotlib, ggplot2, ReportLab, python-docx, python-pptx, and HTML/CSS. Apply whenever a deliverable needs Oligon branding, even if the user doesn't say "brand."
allowed-tools: Read Glob
brand-type: organizational
tokens-file: tokens/brand-tokens.json
style-guide: references/Oligon_Digital_Style_Guide_v2.3.html
---
<!-- GENERATED FILE - do not edit here.
     Vendored from https://github.com/pickleton89/oligon-brand-core@67d9a66
     Edit oligon-brand-core and re-run scripts/sync_brand_core.sh. -->


# Oligon Scientific Brand — Core

<overview>
Self-contained brand implementation for Oligon. Everything needed to
apply the visual system — tokens, adapters, decision rules, preflight —
lives inside this skill folder; nothing points at sibling skills.

**Core principle.** Neutrals are default; Brand Blue highlights the
one or two elements that matter most; Orange supplies opposition or
focus.

**Primitives.** Three Oklch tonal ramps (Blue / Orange / Neutral × 10
steps), one Brand Blue anchor (`#2DB2E8`), semantic tokens for light
and dark themes, and six color cycles selected by data structure
(Rule 1) and ramp step (Rule 2).
</overview>

<default_behavior>
## Default-On Brand Application

Brand styling is applied by default to all visual output skills. Brand
colors are automatically used by `plotting-libraries`,
`scientific-schematics`, `research-posters`, `scientific-slides`,
`research-paper-summarizer`, and `markdown-to-pdf`.

**Opt out per request** by including "Use default colors", "No brand
styling", "Generic color scheme", or "Use matplotlib defaults" in
your prompt. **Opt out per project** by adding to `CLAUDE.md`:

```markdown
## Visual Styling
Use generic/default styling for all visual outputs. Do not apply Oligon brand.
```
</default_behavior>


<when_to_use>
## When to apply this skill

**Apply when:**
- Styling any figure, plot, chart, heatmap, or schematic that will
  carry the Oligon identity
- Building branded PowerPoint, Word, PDF, or HTML deliverables
- Writing copy that needs the Oligon voice (technical-plain pairing,
  numbers-over-adjectives, verbs-over-nouns)
- Designing single-image social posts, landing pages, email funnels,
  or decks against the v2.3 medium playbooks
- Loading brand tokens programmatically from `tokens/brand-tokens.json`

**Do not apply when:**
- Working on an explicitly non-Oligon project (manuscript for an
  external collaborator who has their own identity, personal side
  project). Use the neutral fallback noted under `<design_foundation>`.
- The user explicitly asks for generic styling ("Use matplotlib
  defaults", "No brand styling").
</when_to_use>

<prerequisites>
## Prerequisites

**Python (matplotlib / seaborn):**

```bash
pip install matplotlib numpy pillow
```

**R (ggplot2):**

```r
install.packages(c("ggplot2", "scales"))
```

**One-time setup (optional — installs the mplstyle into matplotlib's
config dir so `plt.style.use('oligon_color_brand')` works from anywhere):**

```bash
python {baseDir}/scripts/matplotlib_brand_setup.py
# or
Rscript {baseDir}/scripts/ggplot2_brand_setup.R
```

**Direct load — works without setup:**

```python
import matplotlib.pyplot as plt
plt.style.use('{baseDir}/assets/oligon_color_brand.mplstyle')
```
</prerequisites>

<decision_framework>
## Rule 1 — Choose the Cycle

Pick the cycle from the data's categorical structure. Before reaching
for Cycle 2, ask: does any arm carry the narrative answer? If yes,
**Focus**. If no, **Peer**. Never promote arbitrarily.

```
n_series = 1  →  single brand.blue stroke
n_series = 2
  ├─ treatment vs control       →  Cycle 1 · Treatment/Control
  └─ opposing effects           →  Cycle 3 · Opposing
n_series = 3
  ├─ all peers (no focus)       →  Cycle 2 · Peer (3-arm)
  ├─ one promoted (has focus)   →  Cycle 2 · Focus
  ├─ signed / directional       →  Cycle 3 · Opposing
  └─ treatment + secondary      →  Cycle 1 · Treatment/Control (extended)
n_series = 4
  ├─ all peers                  →  Cycle 2 · Peer (4-arm)
  └─ one outlier / categorical  →  Cycle 4 · Multi-Category
n_series ≥ 5                    →  REDESIGN (facet / small multiples)
```

### Cycle quick reference

| Cycle                       | Colors (ramp steps)                                    |
|-----------------------------|--------------------------------------------------------|
| Cycle 1 · Treatment/Control | `brand.blue`, `blue.300` (CI bands = matching-hue @ α=0.18) |
| Cycle 2 · Peer (4-arm)      | `blue.800`, `blue.600`, `blue.400`, `blue.200`         |
| Cycle 2 · Peer (3-arm)      | `blue.700`, `blue.500`, `blue.300`                     |
| Cycle 2 · Focus             | `blue.500`, `blue.300`, `blue.200` + `orange.500` focus |
| Cycle 3 · Opposing          | `blue.600`, `orange.600`, `neutral.300`                |
| Cycle 3 · Divergent heatmap | `blue.700` → white → `orange.700`                      |
| Cycle 4 · Multi-Category    | `blue.800`, `blue.500`, `blue.300`, `orange.500`       |

## Rule 2 — Choose the Ramp Step

| Step        | Role                         |
|:------------|------------------------------|
| 50 – 200    | Fills, tints, surfaces       |
| 300         | Light data strokes (Cycle 1 control, Focus receding) |
| 400         | Primary data default         |
| 500 – 600   | Emphasis / button fills      |
| 700         | Text, borders, links, heatmap extremes |
| 800 – 900   | Dark ground, deepest contrast |
</decision_framework>

<workflow>
## Workflow

### 1. Load brand tokens

```python
import sys
sys.path.insert(0, '{baseDir}/adapters')

from matplotlib_adapter import (
    set_brand_style, select_cycle,
    BRAND_BLUE, BLUE_300, BLUE_600, BLUE_700,
    ORANGE_500, ORANGE_600, ORANGE_700,
    NEUTRAL_300, NEUTRAL_700, NEUTRAL_900,
    CYCLE_TREATMENT_CONTROL, CYCLE_OPPOSING,
    CYCLE_PEER_4, CYCLE_FOCUS, CYCLE_MULTI_CATEGORY,
    get_divergent_cmap, get_semantic,
    run_preflight, validate_palette, get_brand_compliance_report,
)
```

### 2. Apply style

```python
# Rule 1: pick the cycle from data
cycle_name, colors = select_cycle(n_series=2, context='comparison')

# Apply brand defaults (title 12pt, axis 10pt, tick 9pt, despined)
set_brand_style(cycle_name)
```

### 3. Create figure

Generic two-arm time-series (dose-response, PK curve, longitudinal mean,
tumor volume, Kaplan–Meier). **Lines-only by default** — no CI bands on
line plots unless the user explicitly asks for them. Uncertainty moves off
the plot and into the caption (endpoint ± 95% CI values), a numbers-at-risk
table beneath the x-axis (for KM), or inline markers showing individual
timepoints.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(5, 3.75))

# Treatment (hero) line — no fill_between
ax.plot(t, tx, color=BRAND_BLUE, linewidth=2.2, label='Treatment', zorder=3)

# Control line — no fill_between
ax.plot(t, ctrl, color=BLUE_300, linewidth=2.0, label='Control', zorder=2)

ax.set_xlabel('Time (days)')
ax.set_ylabel('Response')
ax.legend(loc='lower left', frameon=False)
fig.savefig('plot.svg')  # vector preferred; 300 dpi PNG for raster
```

**Why lines-only by default.** Bands around every line crowd the canvas,
draw the eye toward the overlap zone rather than the group difference, and
train readers to read uncertainty qualitatively when our captions already
state it quantitatively. Oligon house style keeps the plot surface for the
signal and puts the noise in text. This applies across KM step curves,
tumor-volume time courses, dose-response fits, and all other line plots.

**Honor explicit user CI requests.** If the user explicitly asks for CI
bands on the plot (e.g., "semi-transparent fills," "shaded CI," "bands on
the plot," "95% CI ribbon"), honor the request — the user's stated
preference wins over the house default. When drawing bands:

1. Use **matching-hue tints** at α=0.18. Each line's CI band is a tint of
   *its own* line color (brand.blue line → brand.blue band at α=0.18;
   blue.300 line → blue.300 band at α=0.18).
2. Do NOT fill all bands with a shared `blue.100` — that produces a muddy
   overlap where treatment and control bands fuse and it misrepresents
   uncertainty as a shared quantity.
3. Note in the caption that bands are 95% CI (or SEM, SD — whichever you
   used) so the reader isn't left guessing.
4. For KM specifically, the at-risk table is optional once bands are on
   the plot but still recommended for precision-aware audiences.

The `add_error_band(ax, x, y, yerr, color=line_color)` helper in
`matplotlib_adapter` does the matching-hue tint correctly in one call.

```python
# KM default: step lines, no bands, at-risk table below, CI endpoints in caption.
ax.step(days, tx_surv,   color=BRAND_BLUE, linewidth=2.2, where='post',
        label='SeekR-siRNA')
ax.step(days, ctrl_surv, color=BLUE_300,  linewidth=2.0, where='post',
        label='Untreated')

# If the user asked for CI bands, add matching-hue tints:
# add_error_band(ax, days, tx_surv,   yerr=tx_ci,   color=BRAND_BLUE)
# add_error_band(ax, days, ctrl_surv, yerr=ctrl_ci, color=BLUE_300)
```

### 4. Preflight & verify

```python
print(get_brand_compliance_report(fig))
```

Expect PASS on: white background, spines removed, no library default
colors, no retired v4 hexes (`#E8622D`, `#7D250F`, `#0F5D7D`,
`#158BBB`), Brand Blue limited to ≤ 2 focal elements, colors drawn
from v2.3 ramps.

### 5. Grayscale + CVD check

Convert the saved figure to grayscale and simulate deuteranopia /
protanopia. Every category must remain distinguishable. If it doesn't,
add shape or line-style redundancy.

The adapter's `validate_palette()` returns ramp-lightness deltas so
you can predict CVD survival before rendering. For independent
validation, use the Coblis colorblind simulator or the
`colorspacious` Python package.

> **Do not mark task complete until preflight, grayscale, and CVD
> checks all pass.**
</workflow>

<figure_integrity>
## Figure Integrity — Twelve Rules

These govern what a figure is allowed to claim visually. Violating any
of them misrepresents the data, regardless of how well-styled the
figure looks.

1. **Zero baseline on bar charts.** Switch to a dot plot if truncation
   is unavoidable.
2. **Log scales labeled as such** (`log10 concentration (nM)`), one
   tick per decade baseline. Never a silent log transform.
3. **Uncertainty shown** — error bars, CI bands, or individual points.
   State bar definition (SD / SEM / 95 % CI) on-figure.
4. **No 3D effects on 2D data.** Flat, 2D, always.
5. **No rainbow / jet colormaps on continuous data.** Use viridis-
   family or the Cycle 3 divergent ramp.
6. **No category encoded by hue alone.** Combine with shape, line
   style, or direct label.
7. **Isotype charts replicate 1:1.** Five icons beside one — never a
   single icon scaled 5× larger.
8. **No dual y-axes without justification.** Prefer small multiples
   or twin-panel layouts first.

These four govern *generative-artifact integrity* — the failure modes a
diffusion model or code-gen LLM introduces that a competent human would
not. Because we author from ground-truth data and source SVG/plot code,
these are **exact deterministic checks against what we already hold**, not
image forensics. A single confirmed violation of Rule 9, 11, or 12 is a
*categorical tell* — it dominates the verdict regardless of how clean the
rest of the figure is.

9. **Lexically-valid labels only.** Every axis label, legend entry, tick
   label, and callout is a real word, term, or number — never a
   letter-shaped but lexically-void glyph-string ("*diƨlocttal*",
   "*testtomcels*"), invented diacritic, or melted/mixed-script character.
   This is the strongest single AI tell (Frontiers/Bik 2024). For our own
   output, scan the source string set, not the pixels.
10. **Non-default styling is intentional, not stripped.** Tool defaults
    (matplotlib `C0`/`C1` tab10, seaborn theme, Excel chart style) are a
    regression-to-mean slop fingerprint — apply a brand cycle or a
    justified palette instead. But this rule is **two-sided**: do *not*
    over-minimize toward a sterile, decoration-free chart either.
    Embellishment that aids recall is not slop (Bateman CHI 2010). Keep
    ink that supports the takeaway; replace defaults, don't strip
    meaning.
11. **Encoding-value fidelity.** Bar heights, slice angles, point
    positions, and marker sizes must match the printed/underlying values.
    Geometry that contradicts the data label is a fabrication tell. We
    hold the data, so verify exactly — `encoded_value == source_value`,
    not OCR.
12. **Closure / conservation holds.** Parts-of-whole sum to the whole
    (pie/stacked slices → 100% or the stated total); subgroup counts
    reconcile to the group total; axis labels are the real categories,
    not raw sequence indices (1, 2, 3…). Check the source data array,
    not the render.
</figure_integrity>

<design_foundation>
## Design Foundation

Universal design principles that apply across every output format.
Oligon-specific application lives in the other sections of this skill
and in `references/brand-colors-full.md`; this block is the
brand-agnostic decision flow to run *before* picking colors and fonts.

> **Generic-fallback for non-Oligon output.** For unbranded manuscripts,
> cross-organization collaborations, or personal projects, follow the
> same principles but substitute: **viridis / cividis** for sequential
> data, **Okabe-Ito** (8-color) for categorical, **ColorBrewer
> diverging** (RdBu, PuOr) for diverging, and validate contrast with
> the WebAIM Contrast Checker or WCAG 2.1 AA tooling.

### Decision flow

```
Who is the viewer?           → audience matrix (below)
   ↓
What story in one sentence?  → single-message test
   ↓
Which chart type?            → match the data structure, not habit
   ↓
Which cycle / palette?       → Rule 1 (see <decision_framework>)
   ↓
Which ramp step?             → Rule 2 (see <decision_framework>)
   ↓
Accessibility check          → grayscale + CVD (workflow step 5)
   ↓
Venue constraints            → target venue's author guidelines
```

### Audience matrix

| Audience                           | Output             | Design direction |
|------------------------------------|--------------------|------------------|
| Journal reviewers / academic peers | Data-heavy figures | Precise, restrained, minimal decoration; 300 DPI; venue dimensions |
| Journal reviewers / academic peers | Conceptual figures | Clean, publishable; Helvetica / Arial |
| Conference audience                | Poster             | Scannable in 3 s; ≥ 24 pt body; high contrast |
| Conference audience                | Talk slides        | One idea per slide; projection type scale (≥ 18 pt body) |
| General public / media             | Any                | Accessible, engaging; avoid jargon; visual metaphors |
| Internal team                      | Any                | Functional, clear; templates acceptable |

### Single-message test

For every figure, answer in one sentence: *"What single insight should
the viewer take away?"* If you can't answer in one sentence, the
figure is doing too many jobs — split into panels or multiple figures.

### Universal design pitfalls

1. **Default Syndrome / regression-to-mean (two-sided)** — tool defaults
   without justification are a slop fingerprint (avoid the canonical
   matplotlib/seaborn/Excel look); but the opposite failure is just as
   real — sterile over-minimization that strips useful labels and
   embellishment is *also* regression-to-the-mean (Bateman CHI 2010: junk
   doesn't impair comprehension and aids recall). Replace defaults with an
   intentional, takeaway-supporting style — not with the leanest possible
   chart.
2. **Rainbow colormap for sequential data** — use viridis family
3. **Color-only encoding** — add shape / line style / direct label
4. **Cramming** — one main message per figure
5. **Inconsistent styling** — define the hierarchy before starting
6. **Truncated axes** — start bar charts at zero
7. **3D for 2D data** — distorts perception

### Cognitive foundation

The design rules above are applications of a small set of settled
cognitive-science results. When reviewers push back, these are the
primary references to cite.

- **Cleveland & McGill (1984), *JASA* 79(387)** — ranking of elementary
  perceptual tasks for quantitative judgment. From most to least
  accurate: position on a common scale > length > angle / slope > area
  > volume > shading / color saturation. Justifies encoding the most
  important quantitative claim with position, not color or area.
  Replicated on Mechanical Turk by Heer & Bostock (2010).
- **Cowan (2010), *Current Directions in Psychological Science*
  19(1)** — working memory holds ~4 chunks, not Miller's 7 ± 2.
  Justifies the "≤ 4 simultaneously encoded dimensions per panel"
  constraint and "3–5 acts per graphical abstract" rule.
- **Treisman & Gelade (1980), *Cognitive Psychology* 12(1)** — feature
  integration theory. Feature search (one distinctive dimension) is
  pre-attentive; conjunction search (two non-distinctive features) is
  serial. Justifies **Rule 6 (no hue-alone encoding):** a result
  highlighted by a conjunction of non-distinctive features will only
  be found by readers who already know where to look.
- **Wagemans et al. (2012), *Psychological Bulletin* 138(6)** —
  Gestalt grouping principles (proximity, similarity, continuity,
  closure, common region, connectedness). Justifies direct labeling
  at line endpoints over corner legends, and shared background tints
  for panel families over boxed borders.
- **Franconeri, Padilla, Shah, Zacks & Hullman (2021), *Psychological
  Science in the Public Interest* 22(3)** — evidence synthesis on
  visual data communication. Key finding: comparisons are serial,
  ensemble statistics are parallel. Justifies calling out the key
  comparison as a direct-encoded annotation rather than expecting the
  reader to scan a dense heatmap.
- **Crameri, Shephard & Heron (2020), *Nature Communications* 11** —
  authoritative rainbow-colormap critique and home of the free
  Scientific Colour Maps (batlow, vik, roma, lajolla, berlin) at
  <https://fabiocrameri.ch/colourmaps>. Justifies viridis / cividis for
  sequential, RdBu / PuOr / vik / berlin for diverging.
- **Tufte (2001), *The Visual Display of Quantitative Information* (2nd
  ed., Graphics Press)** — data-to-ink ratio. *Apply:* drop gridlines,
  decorative backgrounds, and redundant ticks unless they carry signal —
  weighed against the takeaway-message reframing (Fujii 2026, below).
- **Wilke (2019), *Fundamentals of Data Visualization* (O'Reilly)** —
  practitioner reference for plot-type selection, color, and proportional
  encoding. *Apply:* default reference for chart-type questions outside
  the primary sources above.
- **O'Donoghue et al. (2018), *Annu Rev Biomed Data Sci* 1** — readers
  look at figures before text. *Apply:* design the figure so its takeaway
  is recognisable from the figure alone, before the caption.
- **Weissgerber et al. (2015), *PLoS Biol* 13, e1002128** — bar charts of
  continuous data hide the distribution. *Apply:* show individual points
  (box+jitter, violin+jitter, or strip), not bars, for continuous
  measurements.
- **Fujii (2023), *J Epidemiol* 33, 487–488** — risk / odds / hazard
  ratios should be drawn as point + 95 % CI (pointrange), never as bars.
  *Apply:* use pointrange for ratio estimates.
- **Fujii (2026), *Nat Hum Behav* doi:10.1038/s41562-026-02466-9** —
  communication-context framework (audience × time × interaction) and the
  modern signal-to-noise reframing of data-to-ink. *Apply:* ask not "does
  this ink represent data?" but "does this ink support the takeaway?" —
  scale figure complexity to the viewing context.
- **Jambor (2025), *Nat Cell Biol* 27, 879–883** — figure accessibility:
  alt text, contrast, and multi-modal redundant encoding. *Apply:* supply
  alt text and never encode category by hue alone (reinforces Rule 6).
- **Midway (2020), *Patterns* 1, 100141** — table-vs-figure principles.
  *Apply:* when exact values matter more than the pattern, use a table.

### Font embedding

Embed fonts; do not outline. Publishers need editable text for
house-style changes, HTML translation, and accessibility tooling.
Concrete commands per toolchain:

- **matplotlib:** `plt.rcParams['pdf.fonttype'] = 42` (TrueType, not
  Type 3) plus `plt.rcParams['ps.fonttype'] = 42`.
- **R:** `cairo_pdf()` device, or
  `extrafont::embed_fonts("out.pdf")` after rendering.
- **Illustrator:** File → Save As → PDF → subset fonts at 100 %.

Verify with `pdffonts file.pdf` — expect `emb=yes` for every face.

### Output-format guidance

- **Figures (matplotlib / seaborn / SVG)** — 300 DPI for print, 150 DPI
  for screen. Prefer PDF / EPS / SVG (vector). Embed fonts in PDF.
- **Infographics (SVG)** — one clear message; minimal text; direct
  labels over legends.
- **Report illustrations (ReportLab)** — route through
  `adapters/reportlab_adapter.py`; use `brand_header`, `brand_logo`,
  `get_brand_styles`, `get_brand_table_style`, `highlight_text`, and
  the `brand_spacer` / `brand_page_break` flowables.
- **Presentations (PPTX / Beamer)** — projection type scale (body
  ≥ 18 pt, heading 28 pt, figure axis labels 18 pt).
- **Posters** — scannable hierarchy (3 s / 10 s / 60 s);
  view-distance font sizing.

### SVG output contract

SVG is the preferred figure format for reports — vector, editable,
embeddable. Two invariants must hold on every emitted figure.

**Font family.** Every `<text>` / `<tspan>` must carry an explicit
font-family (e.g. `font-family="Arial, Helvetica, sans-serif"`).
Renderers that omit it fall back to a system default (often Times on
Linux), which is on the forbidden list. For matplotlib this is guaranteed
by the brand style's `svg.fonttype: none`, which keeps text as real
`<text>` elements rather than outlined glyph paths; if you loaded a
non-brand style first, set `plt.rcParams['svg.fonttype'] = 'none'` before
saving.

**Font sizes follow the v2.3 figure scale** — title 12 pt / axis label
10 pt / tick 9 pt / legend 8.5–9 pt / panel label 9–10 pt — canonical in
`tokens/brand-tokens.json` (`layout.figures`, `typography`). Do not
override downward. (This replaces the old v4 10 pt-floor / 10·12·14·16
ladder.)

**Sanity check** before delivering — must return matches and must NOT
include Times, Calibri, or a system default:

```bash
grep -oE 'font-family[^;">]+' figure.svg | sort -u
```

**Visual preview (required).** The grep confirms text-level compliance
but not layout — overlapping labels, clipped titles, illegible legends.
Render to PNG and inspect:

```bash
scripts/render_svg_preview.sh figure.svg              # writes figure.preview.png
scripts/render_svg_preview.sh figure.svg /tmp/out.png # explicit output path
```
</design_foundation>

<preflight>
## Preflight Checklist

- [ ] White background / brand ground (`blue.900` for dark theme)
- [ ] Axis furniture in `neutral.200`–`300`; text `neutral.900` on
      light, `neutral.50` on dark
- [ ] Top and right spines removed
- [ ] Correct cycle for context (Rule 1) and correct ramp step for
      role (Rule 2)
- [ ] Brand Blue limited to 1–2 focal elements per panel
- [ ] No library default colors; no retired v4 hexes
- [ ] Redundant encoding (shapes / styles with color)
- [ ] Tested in grayscale and under CVD simulation
- [ ] Uncertainty rendered and labeled (SEM / SD / 95 % CI, n=?)
- [ ] Font Arial / Helvetica / DejaVu Sans; figure scale 9–12 pt,
      projection scale ≥ 18 pt
- [ ] Resolution ≥ 300 DPI for print; vector preferred for line art
- [ ] Alt text describes the *finding*, not the chart type
- [ ] Logo excluded from publication figures
</preflight>

<anti_patterns>
## Common Pitfalls

1. **Retired v4 hexes appearing.** `#E8622D`, `#7D250F`, `#0F5D7D`,
   `#158BBB`, `#222222` are legacy. v2.3 uses Orange 600 `#A0421D` for
   opposition, Blue 800 `#003454` for dark teal, Blue 500 `#008ECB`
   for medium blue, Neutral 900 `#121719` for dark text. The preflight
   validator flags these.
2. **Library defaults.** Call `set_brand_style(cycle_name)` before any
   `plt.subplots()` call — order matters.
3. **Overusing Brand Blue.** If more than two elements per panel are
   in `brand.blue`, emphasis is diluted. Use ramp neutrals or Peer
   blue steps for the rest. `count_brand_blue()` flags violations.
4. **Wrong Cycle 2 variant.** Focus when no arm carries the narrative
   is misleading; Peer when one arm carries the narrative buries the
   answer. Ask first — "does any arm carry the narrative?" Yes →
   Focus. No → Peer.
5. **Color-only encoding.** Relying solely on color to distinguish
   groups fails in grayscale and under CVD. Combine with marker
   shapes, line styles, or direct labels. Mandatory for Cycle 4.
6. **Skipping grayscale / CVD tests.** Blue 600 + Orange 600
   ramp-matched for lightness survives CVD; pure hue-only does not.
   Run both tests before finalizing.
7. **Logo on publication figures.** Journals prohibit branding. Use
   logos only on presentations, posters, and internal documents.
8. **Slide title as a topic label.** "Jurkat uptake data" is a topic,
   not a takeaway. Slide titles should be declarative findings —
   "SeekR bridges drive ~10× siRNA uptake in Jurkat T cells." See
   `references/voice_and_copy.md` for the rule and examples.
</anti_patterns>

<error_handling>
## Error Handling

### Font not found
**Symptom:** Matplotlib warns about Arial.
**Fix:**
```python
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
```

### Token file not found
**Symptom:** `FileNotFoundError` loading `brand-tokens.json`.
**Fix:** The matplotlib adapter has an embedded fallback and resolves
`tokens/brand-tokens.json` relative to the adapter module. For direct
JSON loading:
```python
from pathlib import Path
tokens_path = Path(__file__).parent / "tokens" / "brand-tokens.json"
assert tokens_path.exists()
```

### Color cycle not applying
**Symptom:** Default matplotlib colors appear despite `set_brand_style()`.
**Fix:** Call `set_brand_style()` **before** any figure is created:
```python
set_brand_style('treatment_control')   # first
fig, ax = plt.subplots()                # then
```

### Legacy v4 alias in downstream code
**Symptom:** `KeyError: 'dark_gray'` in docx/pptx/reportlab adapters.
**Fix:** v4 names (`dark_gray`, `contrast_orange`, etc.) route to
v2.3 equivalents via the `BRAND_HEX` alias block in each adapter.
If the alias is missing, prefer the ramp name (e.g. `neutral_900`).
</error_handling>

<adapters>
## Format Adapters

Every output format has a bundled adapter that loads the same v2.3
tokens. Route through these rather than hardcoding hex values.

| Format              | Adapter                          | Entry point |
|---------------------|----------------------------------|-------------|
| matplotlib/seaborn  | `adapters/matplotlib_adapter.py` | `set_brand_style()` |
| ggplot2             | `adapters/ggplot2_adapter.R`     | `theme_brand()` |
| ReportLab (PDF)     | `adapters/reportlab_adapter.py`  | `BRAND_COLORS`, `BRAND_HEX` |
| python-docx         | `adapters/docx_adapter.py`       | `apply_brand_styles()` |
| python-pptx         | `adapters/pptx_adapter.py`       | `get_brand_theme()` |
| HTML / CSS          | `adapters/html_adapter.css`      | `--blue-*`, `--orange-*`, `--neutral-*` |

Python adapters keep v4 aliases as route-through keys so existing
call sites continue to work.
</adapters>

<cross_references>
## Related Skills

| Skill                           | Relationship |
|---------------------------------|--------------|
| `plotting-libraries`            | Implementation code. Loads oligon-brand first; hosts `chart_selector` + `palette_selector` |
| `skills/shared/accessibility/`  | WCAG + CVD validation; `contrast_ratio`, `validate_accessibility`, colorblind simulation |
| `venue-templates`               | Per-journal figure dimensions, column widths, DPI, format |
| `scientific-slides`             | Presentation layouts; applies oligon-brand colors + projection type scale |
| `research-posters`              | Poster templates; applies oligon-brand colors + print specs |
| `markdown-to-pdf`               | Branded PDF reports; uses reportlab/docx adapters |
| `document-skills:docx`          | Word documents; uses `docx_adapter` |
| `scientific-writing`            | Manuscript prose; applies voice rules from `voice_and_copy.md` |
| `paper-2-web`                   | Web/video/poster from paper; inherits brand tokens |

**Skill Router:** See `SKILL_ROUTER.md` for decision trees.

**Typical workflow:**
1. `oligon-brand` → consult `<design_foundation>`, `<decision_framework>`, load tokens
2. `plotting-libraries` → implement figure code
3. `skills/shared/accessibility/` → validate contrast, CVD, figure-spec

**For brand-skill authors:** This skill is the reference
implementation of the contract in `../BRAND_SKILL_INTERFACE.md`.
Mirror the directory structure and validate with
`../brand-interface/`.
</cross_references>

<references>
## Bundled Reference Files

| File                                      | Purpose |
|-------------------------------------------|---------|
| `tokens/brand-tokens.json`                | Machine-readable tokens — primary source of truth |
| `references/Oligon_Digital_Style_Guide_v2.3.html` | Human-readable style guide (April 2026) |
| `references/brand-colors-full.md`         | Full figure/color reference — ramps, cycles, typography, code templates |
| `references/voice_and_copy.md`            | Voice rules, messaging pillars, headline formulas, CTA bank, glossary |
| `references/medium_playbooks.md`          | Social / web / deck / email playbooks + file-naming convention |
| `references/output_templates.md`          | Per-format output templates |
| `assets/oligon_color_brand.mplstyle`      | Matplotlib style file (one-line brand application) |
| `assets/Oligon_Logo_*.svg` / `Oligon_Icon_*.svg` | Logo variants (Brand Blue + White) |

### Color quick reference

| Token            | Hex        | Role |
|------------------|------------|------|
| `brand.blue`     | `#2DB2E8`  | Hero highlight, logo, Cycle 1 treatment |
| `blue.300`       | `#76CAF3`  | Cycle 1 control |
| `blue.600`       | `#006EA6`  | Cycle 3 negative direction |
| `blue.700`       | `#00507E`  | Accent (links, buttons); divergent negative |
| `blue.900`       | `#001A2E`  | Dark theme page |
| `orange.500`     | `#C45E39`  | Focus default; Cycle 4 outlier |
| `orange.600`     | `#A0421D`  | Cycle 3 positive direction |
| `orange.700`     | `#772E11`  | Signal / destructive; divergent positive |
| `neutral.200`    | `#D6DCDF`  | Axis furniture, gridlines, borders |
| `neutral.700`    | `#44494B`  | Secondary text (`text.muted`) |
| `neutral.900`    | `#121719`  | Body text on light |

### Typography quick reference

**Document scale:** H1 28 pt/800, H2 19 pt/700, H3 14 pt uppercase/700,
Body 14 pt/400/1.55, Caption 11 pt/400.

**Figure scale (document reading):** Title 12 pt/700, axis label
10 pt/500, tick 9 pt/400, legend 8.5–9 pt/400.

**Projection scale (slides):** Body 18 pt, heading 28 pt, axis labels
on embedded figures 18 pt.

### Logo usage

Full wordmark (Brand Blue) on light / Neutral 50 / Neutral 100
grounds; full wordmark (White) on Blue 700+ / Neutral 800+. Icon
variants for tight spaces. **Never place a logo on a publication
figure** — journals prohibit branding. Logos are for presentations,
posters, and internal documents only.

**Logos live in `assets/logos/`.** The canonical lockup is
`Oligon_Logo_BrandBlue.svg`; the expanded set includes
right-anchored, tracked-under, divider, underline, and stacked-compact
variants in Black / BrandBlue / White. Always use the SVG file — it
embeds as true vector in PDFs and scales cleanly on slides.

**In ReportLab PDFs, use the `brand_logo()` and `brand_header()` helpers
— do not roll your own.** Rolling your own tends to rasterize the SVG at
display DPI (~100) and produces a visibly pixelated logo in print, and
it's easy to underweight the gap between logo and title so they collide.
Both failures showed up in iteration-1 outputs. The helpers handle
vector embedding (via `svglib`) and enforce 24 pt right-padding on the
logo cell:

```python
from reportlab_adapter import brand_header, brand_logo

# Full header (logo + title + brand-blue divider)
story.extend(brand_header(
    title="SeekR-CTLA4 Q1 Readout",
    subtitle="QUARTERLY READOUT",  # optional eyebrow
    logo_width_inches=1.2,
))

# Or just the logo on its own
story.append(brand_logo(width_inches=1.5))
```

Vector embedding needs `pip install svglib reportlab`. If only
`cairosvg` is available, the helper falls back to a 4× high-DPI PNG
(acceptable, not ideal). Never render the logo at `output_width=100` —
that's print-pixelated.
</references>
