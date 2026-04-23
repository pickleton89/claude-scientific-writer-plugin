---
name: oligon-brand
version: 5.0.0
description: "Use when applying Oligon brand colors, typography, figure standards, voice rules, or medium-specific layouts (social, deck, email, landing page) to any scientific or communications deliverable. Implements Oligon Digital Style Guide v2.3 with Oklch tonal ramps, same-hue Cycle 1, Peer/Focus cycle split, and format adapters for matplotlib, ggplot2, ReportLab, python-docx, python-pptx, and HTML/CSS."
allowed-tools: Read Glob
brand-type: organizational
tokens-file: tokens/brand-tokens.json
style-guide: references/Oligon_Digital_Style_Guide_v2.3.html
---

# Oligon Scientific Brand

<overview>
Brand implementation skill for Oligon — colors, typography, figure
standards, voice/copy patterns, and medium playbooks for every output
format. Implements **Oligon Digital Style Guide v2.3** (April 2026).

**Core principle:** Neutrals are default; Brand Blue highlights the
one or two elements that matter most; Orange supplies opposition or
focus.

The skill ships three Oklch tonal ramps (Blue / Orange / Neutral ×
10 steps), one Brand Blue anchor (`#2DB2E8`), semantic tokens for
light and dark themes, and six color cycles selected by data
structure (Rule 1) and ramp step (Rule 2).
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
## Trigger Conditions

**Use this skill explicitly when:**
- Accessing brand color hex codes or ramp tokens programmatically
- Loading brand tokens directly (`tokens/brand-tokens.json` or mplstyle)
- Creating branded PDFs, Word documents, PowerPoint presentations
- Writing copy that needs the Oligon voice (technical-plain pairing,
  numbers-over-adjectives, verbs-over-nouns)
- Designing single-image social posts, landing pages, email funnels,
  or decks that follow the v2.3 medium playbooks
- Needing a non-figure asset (file-naming conventions, persistent
  footers, MLR/compliance footers)

**Do NOT use this skill when:**
- Creating standard visual outputs → brand is auto-applied
- Working on a non-Oligon project → request opt-out
- Writing plotting code → use `plotting-libraries` (brand auto-applied)
- Need journal-specific figure dimensions → use `venue-templates`
- Need WCAG / CVD validation utilities → `skills/shared/accessibility/`
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

**Setup (one-time):**
```bash
python {baseDir}/scripts/matplotlib_brand_setup.py
# or
Rscript {baseDir}/scripts/ggplot2_brand_setup.R
```

**Alternative — load mplstyle directly:**
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
| Cycle 1 · Treatment/Control | `brand.blue`, `blue.300`, `blue.100` (CI)              |
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

# Apply brand defaults (Figure Type Scale: title 12pt, axis 10pt, tick 9pt)
set_brand_style(cycle_name)
```

### 3. Create figure

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5, 3.75))
ax.plot(t, tx,   color=BRAND_BLUE, linewidth=2.0, label='Treatment')
ax.plot(t, ctrl, color=BLUE_300,   linewidth=2.0, label='Control')
ax.fill_between(t, lo, hi, color='#DBF3FF', alpha=0.5)  # blue.100 CI
ax.set_xlabel('Time (days)')
ax.set_ylabel('Survival probability')
ax.legend(loc='lower left')
fig.savefig('km.svg')  # vector preferred; 300 dpi PNG for raster
```

### 4. Pre-flight & verify

```python
print(get_brand_compliance_report(fig))
```

Expect PASS on:

- [ ] White background, spines removed, grid off, axes dark
- [ ] No library default colors; no retired v4 hexes (`#E8622D`,
      `#7D250F`, `#0F5D7D`, `#158BBB`)
- [ ] Brand Blue ≤ 2 focal elements per panel
- [ ] Colors drawn from the v2.3 Blue / Orange / Neutral ramps

### 5. Grayscale + CVD check

Convert to grayscale and simulate deuteranopia/protanopia via
`skills/shared/accessibility/`. Every category must remain
distinguishable — if it doesn't, add shape or line-style redundancy.

> **Do not mark task complete until pre-flight, grayscale, and CVD
> checks all pass.**
</workflow>

<success_criteria>
## Success Criteria

### Pre-flight checklist (from v2.3)

- [ ] White background / brand ground (`blue.900` for dark theme)
- [ ] Axis furniture in `neutral.200`–`300`; text `neutral.900` on
      light, `neutral.50` on dark
- [ ] Top and right spines removed
- [ ] Correct cycle for scientific context (Rule 1) and correct ramp
      step for visual role (Rule 2)
- [ ] Brand Blue limited to 1–2 focal elements per panel
- [ ] No library default colors; no retired v4 hexes
- [ ] Redundant encoding (shapes/styles with color)
- [ ] Tested in grayscale and under CVD simulation
- [ ] Uncertainty rendered and labeled (SEM / SD / 95 % CI, n=?)
- [ ] Font Arial/Helvetica/DejaVu Sans; figure scale 9–12 pt,
      projection scale ≥ 18 pt
- [ ] Resolution ≥ 300 DPI for print; vector preferred for line art
- [ ] Alt text describes the *finding*, not the chart type
- [ ] Logo excluded from publication figures
</success_criteria>

<figure_integrity>
## Figure Integrity — Eight Rules

These govern what a figure is allowed to claim visually. Violating any
of them misrepresents the data, regardless of how well-styled the
figure looks.

1. **Zero baseline on bar charts.** Switch to dot plot if truncation
   is unavoidable.
2. **Log scales labeled as such** (`log10 concentration (nM)`), one
   tick per decade baseline. Never a silent log transform.
3. **Uncertainty is shown** — error bars, CI bands, or individual
   points. Bar definition (SD / SEM / 95 % CI) stated on-figure.
4. **No 3D effects on 2D data.** Flat, 2D, always.
5. **No rainbow / jet colormaps on continuous data.** Use viridis-
   family or the §3 divergent cycle.
6. **No category encoded by hue alone.** Combine with shape, line
   style, or direct label.
7. **Isotype charts replicate 1:1.** Five icons beside one — never a
   single icon scaled 5× larger.
8. **No dual y-axes without justification.** Prefer small multiples
   or twin-panel layouts first.
</figure_integrity>

<design_foundation>
## Design Foundation

Universal design principles that apply across every output format.
Oligon-specific application lives in the other sections of this skill
and in `references/brand-colors-full.md`; this block is the
brand-agnostic decision flow to run *before* picking colors and fonts.

> **Generic-fallback for non-Oligon output.** For unbranded manuscripts,
> cross-organization collaborations, or personal projects, follow the
> same principles but substitute: **viridis/cividis** for sequential
> data, **Okabe-Ito** (8-color) for categorical, **ColorBrewer
> diverging** (RdBu, PuOr) for diverging, and validate contrast with
> the WebAIM Contrast Checker or WCAG 2.1 AA tooling.

### Decision flow

```
Who is the viewer?           → audience matrix (below)
   ↓
What story in one sentence?  → single-message test
   ↓
Which chart type?            → plotting-libraries/scripts/chart_selector
   ↓
Which cycle / palette?       → Rule 1 (oligon-brand) — or palette_selector (generic)
   ↓
Which ramp step?             → Rule 2 (oligon-brand)
   ↓
Accessibility check          → skills/shared/accessibility/
   ↓
Venue constraints            → venue-templates/references/figure_specs.md
```

### Audience matrix

| Audience                         | Output             | Design direction |
|----------------------------------|--------------------|------------------|
| Journal reviewers / academic peers | Data-heavy figures | Precise, restrained, minimal decoration; 300 DPI; venue dimensions |
| Journal reviewers / academic peers | Conceptual figures | Clean, publishable; Helvetica/Arial |
| Conference audience              | Poster             | Scannable in 3 s; ≥ 24 pt body; high contrast |
| Conference audience              | Talk slides        | One idea per slide; projection type scale (§5) |
| General public / media           | Any                | Accessible, engaging; avoid jargon; visual metaphors |
| Internal team                    | Any                | Functional, clear; templates acceptable |

### Single-message test

For every figure, answer in one sentence: *"What single insight should
the viewer take away?"* If you can't answer in one sentence, the
figure is doing too many jobs — split into panels or multiple figures.

### Universal design pitfalls

1. **Default Syndrome** — tool defaults without justification
2. **Rainbow colormap for sequential data** — use viridis family
3. **Color-only encoding** — add shape / line style / direct label
4. **Cramming** — one main message per figure
5. **Inconsistent styling** — define the hierarchy before starting
6. **Truncated axes** — start bar charts at zero
7. **3D for 2D data** — distorts perception

### Output-format guidance

- **Figures (matplotlib/seaborn/SVG)** — delegate code to
  `plotting-libraries`; dimensions from
  `venue-templates/references/figure_specs.md`. 300 DPI for print,
  150 DPI for screen. Prefer PDF/EPS/SVG (vector). Embed fonts in PDF.
- **Infographics (SVG)** — one clear message; minimal text;
  `skills/shared/svg-components/` for reusable pieces.
- **Report illustrations (ReportLab)** — use `adapters/reportlab_adapter.py`
  building blocks (`MetricCard`, `CalloutBox`, `SectionHeader`, `DataTable`).
- **Presentations (PPTX/Beamer)** — projection type scale (§5).
- **Posters** — scannable hierarchy (3 s / 10 s / 60 s), view-distance
  font sizing. See `research-posters/`.
</design_foundation>

<scope>
## Scope

**In Scope:**
- Tonal-ramp color tokens + semantic tokens (light + dark themes)
- Format-specific adapters (matplotlib, ggplot2, ReportLab, docx, pptx, HTML)
- Typography standards (document, figure, projection scales)
- Figure integrity rules and pre-flight validation
- Voice, copy patterns, messaging pillars (`references/voice_and_copy.md`)
- Medium playbooks (social, landing page, deck, email) and file-naming
  conventions (`references/medium_playbooks.md`)

**Out of Scope:**
- Plotting code → `plotting-libraries`
- Journal-specific figure dimensions → `venue-templates`
- WCAG / CVD validation utilities → `skills/shared/accessibility/`
- Diagram creation → `scientific-schematics`
- Poster layout from scratch → `research-posters`
- Slide layout from scratch → `scientific-slides`
</scope>

<anti_patterns>
## Common Pitfalls

### 1. Using retired v4 hexes
**Problem:** `#E8622D`, `#7D250F`, `#0F5D7D`, `#158BBB`, `#222222`
legacy colors appear in figures.
**Solution:** v2.3 uses Orange 600 `#A0421D` for opposition, Blue 800
`#003454` for dark teal replacement, Blue 500 `#008ECB` for medium
blue, Neutral 900 `#121719` for dark text. The preflight validator
flags these as violations.

### 2. Using library defaults
**Problem:** Matplotlib/seaborn default colors instead of v2.3 palette.
**Solution:** Call `set_brand_style(cycle_name)` before plotting.

### 3. Overusing Brand Blue
**Problem:** Too many elements highlighted, diluting emphasis.
**Solution:** Limit Brand Blue to 1–2 focal elements per panel. Use
ramp neutrals or Peer blue steps for the rest. `count_brand_blue()`
flags violations.

### 4. Wrong Cycle 2 variant
**Problem:** Using Focus when no arm carries the narrative answer,
or Peer when one arm does.
**Solution:** Ask first — "does any arm carry the narrative?" Yes →
Focus. No → Peer. See Rule 1 in `<decision_framework>`.

### 5. Color-only encoding
**Problem:** Relying solely on color to distinguish groups.
**Solution:** Combine with marker shapes, line styles, or direct
labels. Mandatory for Cycle 4.

### 6. Ignoring grayscale + CVD tests
**Problem:** Figure unreadable when printed black-and-white or viewed
under deuteranopia.
**Solution:** Always run both tests before finalizing. Blue 600 +
Orange 600 ramp-matched lightness survives CVD; pure hue-only does not.

### 7. Logo on publication figures
**Problem:** Including Oligon logo on journal figures.
**Solution:** Journals prohibit branding. Use logos only on
presentations, posters, and internal documents.

### 8. Slide title as topic label
**Problem:** "Jurkat uptake data" instead of a finding.
**Solution:** Slide titles are declarative takeaways — "SeekR bridges
drive ~10× siRNA uptake in Jurkat T cells." See `voice_and_copy.md`
§4.4.
</anti_patterns>

<error_handling>
## Error Handling

### Font not found
**Symptom:** Matplotlib warns about Arial.
**Solution:**
```python
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
```

### Token file not found
**Symptom:** `FileNotFoundError` loading `brand-tokens.json`.
**Solution:** `matplotlib_adapter` has an embedded fallback and loads
from `tokens/brand-tokens.json` relative to the adapter module. For
direct JSON loading:
```python
from pathlib import Path
tokens_path = Path(__file__).parent / "tokens" / "brand-tokens.json"
assert tokens_path.exists()
```

### Color cycle not applying
**Symptom:** Default matplotlib colors appear despite `set_brand_style()`.
**Solution:** Call `set_brand_style()` **before** creating figures:
```python
set_brand_style('treatment_control')  # Must be first!
fig, ax = plt.subplots()
```

### Legacy v4 alias in downstream code
**Symptom:** `KeyError: 'dark_gray'` in docx/pptx/reportlab adapters.
**Solution:** v4 names (`dark_gray`, `contrast_orange`, etc.) route to
v2.3 equivalents via the `BRAND_HEX` alias block in each adapter.
If the alias is missing, prefer the ramp name (e.g. `neutral_900`).
</error_handling>

<adapters>
## Format Adapters

| Format              | Adapter                          | Entry point |
|---------------------|----------------------------------|-------------|
| matplotlib/seaborn  | `adapters/matplotlib_adapter.py` | `set_brand_style()` |
| ggplot2             | `adapters/ggplot2_adapter.R`     | `theme_brand()` |
| ReportLab (PDF)     | `adapters/reportlab_adapter.py`  | `BRAND_COLORS`, `BRAND_HEX` |
| python-docx         | `adapters/docx_adapter.py`       | `apply_brand_styles()` |
| python-pptx         | `adapters/pptx_adapter.py`       | `get_brand_theme()` |
| HTML / CSS          | `adapters/html_adapter.css`      | `--blue-*`, `--orange-*`, `--neutral-*` |

All adapters ship with the same v5.0 token set (Blue/Orange/Neutral
ramps + brand anchor). The Python adapters keep v4 aliases as
route-through keys so existing call sites continue to work.
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
## Reference Documents

| Document                                  | Purpose |
|-------------------------------------------|---------|
| `tokens/brand-tokens.json`                | Machine-readable brand tokens (primary source of truth) |
| `references/brand-colors-full.md`         | Full figure/color reference — ramps, cycles, typography, accessibility, code templates |
| `references/voice_and_copy.md`            | Voice rules, messaging pillars, headline formulas, CTA bank, glossary |
| `references/medium_playbooks.md`          | Social/web/deck/email playbooks + file-naming convention |
| `references/output_templates.md`          | Output-format templates |
| `assets/oligon_color_brand.mplstyle`      | Matplotlib style file (one-line brand application) |

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

### Logo assets

| Variant                     | File                           | Use on |
|-----------------------------|--------------------------------|--------|
| Full wordmark (Brand Blue)  | `assets/Oligon_Logo_BrandBlue.svg` | Light / Neutral 50 / Neutral 100 |
| Full wordmark (White)       | `assets/Oligon_Logo_White.svg`     | Blue 700+ / Neutral 800+ |
| Icon (Brand Blue)           | `assets/Oligon_Icon_BrandBlue.svg` | Light backgrounds |
| Icon (White)                | `assets/Oligon_Icon_White.svg`     | Dark backgrounds |

> **Do NOT place logos on publication figures** — journals prohibit
> branding. Use on presentations, posters, and internal documents only.
</references>
