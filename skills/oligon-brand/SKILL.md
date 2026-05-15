---
name: oligon-brand
version: 4.1.0
description: "Oligon scientific brand implementation for figures, presentations, and documents. Provides color palettes, typography standards, format-specific adapters for matplotlib, ggplot2, ReportLab, python-docx, python-pptx, and HTML/CSS, and a cognitive-foundation reference block for cross-format design decisions."
allowed-tools: [Read, Glob]
brand-type: organizational
tokens-file: tokens/brand-tokens.json
---

# Oligon Scientific Brand

<overview>
Brand implementation skill providing Oligon-specific colors, typography, and styling for scientific visualizations and documents.

**Core Principle:** Neutrals are default; Brand Colors are for highlights; Contrast colors show opposition.

Most data should be grayscale. Brand Blue (`#2DB2E8`) highlights the most important element (1-2 per panel max).
</overview>

<design_foundation>
## Cognitive Foundation

Brand decisions sit on top of perception and cognitive-science findings that apply regardless of brand. Each citation below carries a one-line application rule for Oligon figures.

### Perception and visual encoding

- **Cleveland & McGill 1984** *J Am Stat Assoc* **79**, 531–554 — channel ranking: position > length > angle > area > saturation > hue. *Apply:* prefer position-encoded charts (scatter, dot plots, box+jitter) over area- or hue-encoded ones (pie charts, heatmaps as primary). Bank trends to 45° when comparing slopes.
- **Treisman & Gelade 1980** *Cognitive Psychol* **12**, 97–136 — feature search is parallel; conjunction search is serial. *Apply:* never rely on hue alone to distinguish series — pair color with marker shape, line style, or direct labels.
- **Wagemans et al. 2012** *Psychol Bull* **138**, 1172–1217 — Gestalt grouping (proximity, similarity, common fate). *Apply:* place labels adjacent to the data they describe; group panels of a multi-panel figure by shared background or close spacing.
- **Cowan 2010** *Curr Dir Psychol Sci* **19**, 51–57 — working memory holds ~4 chunks. *Apply:* keep simultaneous encoded dimensions ≤4 per panel; if you need more, facet into small multiples.
- **Franconeri, Padilla, Shah, Zacks, Hullman 2021** *Psychol Sci Public Interest* **22**, 110–161 — readers see ensembles in parallel but compare items serially. *Apply:* annotate the key comparison directly on the figure rather than asking the reader to compare across panels by eye.

### Color and accessibility

- **Crameri, Shephard, Heron 2020** *Nat Commun* **11**, 5444 — rainbow / jet maps actively distort scientific data; Scientific Colour Maps are perceptually uniform and CVD-safe. *Apply:* never use jet / rainbow / Spectral for sequential data. Defaults: `viridis`, `cividis`, `okabe_ito`, or Crameri's `batlow` / `roma`. Cross-link: https://www.fabiocrameri.ch/colourmaps/

### Practitioner canon and recent reviews

- **Tufte 2001** *The Visual Display of Quantitative Information* (2nd ed., Graphics Press) — data-to-ink ratio: every drop of ink should represent data. *Apply:* remove gridlines, decorative backgrounds, redundant tick marks unless they carry signal. (See `<anti_patterns>` §4 for the modern signal-to-noise reframing.)
- **Wilke 2019** *Fundamentals of Data Visualization* (O'Reilly) — canonical practitioner reference for plot-type selection, color, and proportional encoding. *Apply:* default reference for chart-type questions outside the cognitive-foundation primary sources above.
- **Heer & Bostock 2010** *CHI* — crowd-sourced graphical perception: position-on-aligned-scale wins for comparison; angle and area lose. *Apply:* corroborates Cleveland-McGill; cite when justifying axis choices in a Methods or response-to-reviewer.
- **O'Donoghue et al. 2018** *Annu Rev Biomed Data Sci* **1**, 275–304 — figures shape interpretation; readers often look at figures before text. *Apply:* design the figure so the takeaway message is recognisable from the figure alone, before reading the caption.

### Recent guidance specific to scientific figures

- **Fujii 2026** *Nat Hum Behav* doi:10.1038/s41562-026-02466-9 — communication-context framework (audience × time × interaction); modern signal-to-noise reframing of data-to-ink; figure-vs-table decision step. *Apply:* see Q0 of `../shared/references/pre_submission_checklist.md` ("should this be a table?") and `../shared/references/communication_context_matrix.md` (matches figure complexity to viewing context).
- **Fujii 2023** *J Epidemiol* **33**, 487–488 — risk ratios / odds ratios / hazard ratios should be drawn as points + 95% CI (`pointrange`), not as bars. *Apply:* see `plotting-libraries/scripts/validate_figure.py::check_riskratio_as_bars`.
- **Weissgerber et al. 2015** *PLoS Biol* **13**, e1002128 — bar charts of continuous data hide distributions; show individual data points with box+jitter, violin+jitter, or strip. *Apply:* see `plotting-libraries/scripts/validate_figure.py::check_continuous_as_bars` and `plotting-libraries/references/plot_selection_guide.md`.
- **Jambor 2025** *Nat Cell Biol* **27**, 879–883 — figure accessibility: alt text, contrast, multi-modal redundant encoding. *Apply:* alt-text formula in `../venue-templates/references/figure_specs.md` §4.
- **Midway 2020** *Patterns* **1**, 100141 — table-vs-figure principles. *Apply:* see `../shared/references/figure_vs_table_decision.md`.

### Font embedding

For figure file format requirements, see `../venue-templates/references/figure_specs.md` §3 (Type 42 / TrueType embedding for matplotlib, ggplot2, Illustrator). Do not duplicate those commands here.

</design_foundation>

<default_behavior>
## Default-On Brand Application

**Brand styling is now applied by default** to all visual output skills. You do not need to explicitly invoke this skill—brand colors are automatically used by:

| Skill | Brand Integration |
|-------|-------------------|
| `plotting-libraries` | Default color cycle uses brand colors |
| `scientific-schematics` | Diagram prompts include brand colors |
| `research-posters` | Poster templates use brand colors |
| `scientific-slides` | Slide generation uses brand formatting |
| `research-paper-summarizer` | HTML/PDF/SVG outputs use brand colors |
| `markdown-to-pdf` | PDF generation uses brand styling |

### Opt-Out Mechanism

To disable brand styling and use generic defaults:

**Per-request:** Include in your prompt:
- "Use default colors" or "No brand styling"
- "Generic color scheme" or "Use matplotlib defaults"

**Per-project:** Add to project `CLAUDE.md`:
```markdown
## Visual Styling
Use generic/default styling for all visual outputs. Do not apply Oligon brand.
```

</default_behavior>

<when_to_use>
## Trigger Conditions

**Use this skill explicitly when:**
- Need to access brand color hex codes programmatically
- Want to load brand tokens directly (JSON or mplstyle)
- Customizing brand application beyond defaults
- Creating branded PDFs, Word documents, or PowerPoint presentations
- Need the complete brand specification or logo assets

**Do NOT use this skill when:**
- Creating standard visual outputs → brand is auto-applied
- Working on non-Oligon projects → request opt-out
- Need general design philosophy → use `visual-design`
- Writing plotting code → use `plotting-libraries` (brand auto-applied)
- Need journal-specific formatting → use `venue-templates`
</when_to_use>

<prerequisites>
## Prerequisites

**For Python (matplotlib/seaborn):**
```bash
pip install matplotlib numpy pillow  # pillow required for verification step
```

**For R (ggplot2):**
```r
install.packages("ggplot2")
```

**Setup (one-time):**
```bash
# Install mplstyle to matplotlib config
python {baseDir}/scripts/matplotlib_brand_setup.py

# Or for R
Rscript {baseDir}/scripts/ggplot2_brand_setup.R
```

**Alternative: Load mplstyle directly:**
```python
import matplotlib.pyplot as plt
plt.style.use('{baseDir}/assets/oligon_color_brand.mplstyle')
```
</prerequisites>

<decision_framework>
## Color Cycle Selection

**Do not use library defaults.** Select cycle based on scientific context:

```
How many data series?
│
├─► 1 series → Use #222222 (no highlight needed)
│
├─► 2 series
│   ├─► Treatment vs. Control? → Cycle 1 (treatment_control)
│   └─► Opposing effects? → Cycle 3 (opposing)
│
├─► 3 series
│   ├─► One highlighted? → Cycle 1 (treatment_control)
│   ├─► All equal weight? → Cycle 2 (neutrals_only)
│   └─► Two opposing + neutral? → Cycle 3 (opposing)
│
├─► 4 series → Cycle 4 (multi_category) + marker shapes
│
└─► 5+ series → REDESIGN (facet/small multiples)
```

### Quick Selection Table

| Context | Cycle Name | Colors |
|---------|------------|--------|
| Control vs Treatment | `treatment_control` | `#222222` → `#2DB2E8` → `#666666` |
| All equal weight | `neutrals_only` | `#222222` → `#666666` → `#999999` |
| Up vs Down regulation | `opposing` | `#2DB2E8` → `#E8622D` → `#222222` |
| 4 categories (+shapes!) | `multi_category` | `#222222` → `#2DB2E8` → `#666666` → `#158BBB` |
</decision_framework>

<workflow>
## Workflow

### Stage 1: Load Brand Tokens

**Python (recommended - using adapter):**
```python
import sys
sys.path.insert(0, '{baseDir}')
from adapters.matplotlib_adapter import (
    set_brand_style,
    BRAND_COLORS,
    get_cycle,
    get_color
)
```

**Python (alternative - direct JSON loading):**
```python
import json
from pathlib import Path

tokens_path = Path("{baseDir}/tokens/brand-tokens.json")
with open(tokens_path) as f:
    brand = json.load(f)

# Access colors
brand_blue = brand['colors']['primary']['brand_blue']['hex']  # #2DB2E8
cycle = brand['color_cycles']['treatment_control']['colors']
```

### Stage 2: Apply Style

```python
# Option A: Set matplotlib defaults with specific cycle
set_brand_style('treatment_control')

# Option B: Apply mplstyle file
import matplotlib.pyplot as plt
plt.style.use('oligon_color_brand')  # If installed via setup script
# OR
plt.style.use('{baseDir}/assets/oligon_color_brand.mplstyle')
```

### Stage 3: Create Figure

```python
import matplotlib.pyplot as plt

# Brand colors are now the default cycle
fig, ax = plt.subplots()
# Your plotting code here...
```

### Stage 4: Preflight Check

Before finalizing, verify:
- [ ] White background
- [ ] Black axes and text
- [ ] Top/right spines removed
- [ ] Brand Blue limited to 1-2 elements
- [ ] Tested in grayscale

### Stage 5: Verification (Required)

**After saving the figure, Claude MUST verify compliance:**

1. **Visual inspection**: Open or display the saved figure
2. **Checklist validation**: Confirm each preflight item passes
3. **Grayscale test**: Convert to grayscale and verify readability
4. **Report findings**: State which checks passed/failed

```python
# Example verification pattern
from PIL import Image

# Load saved figure
img = Image.open('output_figure.png')

# Convert to grayscale for accessibility check
grayscale = img.convert('L')
grayscale.save('output_figure_grayscale.png')

# Claude should visually confirm:
# ✓ Data series distinguishable in grayscale
# ✓ Brand Blue used sparingly (1-2 elements)
# ✓ No library default colors present
```

> **Do not mark task complete until verification passes.** If any check fails, return to the appropriate stage and fix before re-verifying.
</workflow>

<success_criteria>
## Success Criteria

### Visual Compliance Checklist

- [ ] White background (`#FFFFFF`)
- [ ] Black text and axes (`#000000`)
- [ ] Top and right spines removed
- [ ] Correct color cycle for scientific context
- [ ] Brand Blue (`#2DB2E8`) limited to 1-2 elements per panel
- [ ] No library default colors
- [ ] Use redundant encoding (shapes/styles with color)
- [ ] Tested in grayscale
- [ ] Error bars labeled (SEM/SD/95% CI, n=?)
- [ ] Arial font, 7-10 pt range
- [ ] Resolution ≥300 DPI for print
- [ ] Logo excluded from publication figures
</success_criteria>

<svg_output>
## SVG Output Contract

SVG is the preferred figure format for scientific reports — vector, editable, and embeddable. To enforce brand compliance on SVG output, the following invariants MUST hold on every emitted figure.

### Font Family
Every `<text>`, `<tspan>`, or styled element MUST carry an explicit font-family declaration:

```
font-family="Arial, Helvetica, sans-serif"
```

Renderers that omit this (some Mermaid configs, AI-generated SVG) silently fall back to the system default — typically Times New Roman on Linux, which is on the forbidden list in `brand-tokens.json` typography.font_family.forbidden.

### Font Size Ladder (Figures — Source of Truth)

| Element       | Size  | Weight |
|---------------|-------|--------|
| Annotations   | 10pt  | normal |
| Tick labels   | 10pt  | normal |
| Axis labels   | 12pt  | normal |
| Legend text   | 12pt  | normal |
| Panel labels  | 14pt  | bold   |
| Figure titles | 16pt  | bold   |

**10pt is the floor — no figure text smaller than 10pt.** 12pt is the base; titles and panel labels scale up; tick labels and annotations sit at the floor. These values are canonical in `tokens/brand-tokens.json` `typography.figures`. Adapters (matplotlib, ggplot2) ship with rcParams/theme defaults wired to this ladder — do not override downward.

### Post-Generation Sanity Check

After producing an SVG, run two greps before delivering. Both CSS-style (`font-family: ...`) and XML-attribute (`font-family="..."`) forms appear depending on renderer — matplotlib uses CSS, Mermaid uses attributes — so use the broader pattern:

```bash
# Must return matches; must NOT include Times, Calibri, or system defaults
grep -oE 'font-family[^;">]+' figure.svg | sort -u

# Confirm sizes are in the 10/12/14/16 band (px or pt; matplotlib emits px, Mermaid pt)
grep -oE 'font-size[^;">]+' figure.svg | sort -u
```

If `font-family` is absent or the size band shows values below 10 (px or pt), regenerate with the correct adapter or theme variables. For Mermaid SVG specifically, see `../scientific-schematics/SKILL.md` for the `themeVariables` init block.

**For matplotlib SVG specifically:** the brand mplstyle sets `svg.fonttype: none`, which keeps text as `<text>` elements (not glyph paths). Without that setting, matplotlib would emit outlined glyphs and the grep checks would return nothing — looking like a fail but actually a renderer quirk. If you load a non-brand style first, force this rcParam manually: `plt.rcParams['svg.fonttype'] = 'none'`.

### When SVG Isn't an Option
Raster pipelines (paperbanana → Imagen) emit PNG, not SVG. Brand colors still apply via the Stylist agent, but the font-size contract cannot be enforced post-hoc. Prefer scientific-schematics or plotting-libraries when SVG + brand-correct typography is required.

</svg_output>

<scope>
## Scope

**In Scope:**
- Color palette definitions and usage guidance
- Format-specific adapters (matplotlib, ggplot2, ReportLab, etc.)
- Typography standards for figures and documents
- Logo usage guidelines
- Preflight verification checklist
- SVG output contract (font-family + font-size ladder)

**Out of Scope:**
- Design philosophy and principles → use `visual-design`
- Writing plotting code → use `plotting-libraries`
- Journal-specific requirements → use `venue-templates`
- Diagram creation → use `scientific-schematics`
</scope>

<anti_patterns>
## Common Pitfalls

### 1. Using Library Defaults
**Problem:** Matplotlib/seaborn default colors instead of brand palette.
**Solution:** Always call `set_brand_style()` or load mplstyle before plotting.

### 2. Overusing Brand Blue
**Problem:** Too many elements highlighted, diluting emphasis.
**Solution:** Limit Brand Blue to 1-2 focal elements per panel. Use neutrals for everything else.

### 3. Color-Only Encoding
**Problem:** Relying solely on color to distinguish groups.
**Solution:** Combine color with marker shapes, line styles, or direct labels.

### 4. Ignoring Grayscale Test
**Problem:** Figure unreadable when printed in black and white.
**Solution:** Always test in grayscale before finalizing.

### 5. Brand Blue vs Medium Blue Confusion
**Problem:** Using `#2DB2E8` and `#158BBB` as primary differentiators (too similar).
**Solution:** Pair Brand Blue with neutrals or Contrast Orange, not Medium Blue.

### 6. Logo on Publication Figures
**Problem:** Including Oligon logo on journal figures.
**Solution:** Journals prohibit branding. Use logos only on presentations, posters, and internal documents.

### 7. Optimising for Data-to-Ink Ratio Alone (Signal-to-Noise Reframing)

**Problem:** Following Tufte's data-to-ink ratio mechanically — keeping every drop of ink that "represents data" — even when some of that ink does not support the figure's takeaway message.

**Solution:** Apply Fujii's (2026) modern reframing: the question is not "does this ink represent data?" but "does this ink support the takeaway message?" If removing a gridline, label, panel, or colour stop would not change the reader's interpretation, remove it. The principle scales with viewing context (`../shared/references/communication_context_matrix.md`):
- At oral-talk pace, signal-to-noise must be high enough that a reader grasps the message in seconds — strip aggressively.
- At article pace, more elements may be useful provided each carries signal.

**Cross-references:** `../shared/references/pre_submission_checklist.md` (#12 direct labelling); `../oligon-brand/SKILL.md` `<design_foundation>` (Tufte 2001 + Fujii 2026 citations).
</anti_patterns>

<error_handling>
## Error Handling

### Font Not Found
**Symptom:** Matplotlib warning about Arial font.
**Solution:**
```python
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
```

### Token File Not Found
**Symptom:** `FileNotFoundError` when loading brand-tokens.json
**Solution:** The matplotlib_adapter has embedded fallback values. For direct JSON loading, verify path:
```python
from pathlib import Path
tokens_path = Path(__file__).parent / "tokens" / "brand-tokens.json"
assert tokens_path.exists(), f"Tokens not found at {tokens_path}"
```

### Color Cycle Not Applying
**Symptom:** Default matplotlib colors appearing despite `set_brand_style()`.
**Solution:** Call `set_brand_style()` BEFORE creating any figures:
```python
set_brand_style('treatment_control')  # Must be first!
fig, ax = plt.subplots()
```
</error_handling>

<adapters>
## Format Adapters

| Format | Adapter | Usage |
|--------|---------|-------|
| matplotlib/seaborn | `adapters/matplotlib_adapter.py` | `from adapters.matplotlib_adapter import set_brand_style` |
| ggplot2 | `adapters/ggplot2_adapter.R` | `source("adapters/ggplot2_adapter.R")` |
| ReportLab (PDF) | `adapters/reportlab_adapter.py` | `from adapters.reportlab_adapter import get_brand_colors` |
| python-docx | `adapters/docx_adapter.py` | `from adapters.docx_adapter import apply_brand_styles` |
| python-pptx | `adapters/pptx_adapter.py` | `from adapters.pptx_adapter import get_brand_theme` |
| HTML/CSS | `adapters/html_adapter.css` | `<link rel="stylesheet" href="html_adapter.css">` |

See individual adapter files for detailed API documentation.
</adapters>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `visual-design` | **Design philosophy** — provides universal principles; oligon-brand provides Oligon-specific implementation. The new oligon-brand `<design_foundation>` block adds primary-source cognitive-foundation citations (Cleveland-McGill, Wagemans, Crameri, Fujii 2026, etc.) as a complementary layer. |
| `plotting-libraries` | **Code implementation** — use plotting-libraries for matplotlib/ggplot2 code patterns; load oligon-brand first for brand colors |
| `scientific-slides` | **Presentations** — apply oligon-brand colors to slide designs |
| `research-posters` | **Posters** — apply oligon-brand colors and logo placement |
| `venue-templates` | **Journal formatting** — figure_specs.md provides cross-cutting font embedding, color space, and graphical-abstract specs |
| `markdown-to-pdf` | **PDF reports** — uses brand colors for styled output |
| `document-skills:docx` | **Word documents** — use docx_adapter for branded styling |

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Typical Workflow:**
1. `oligon-brand` `<design_foundation>` → consult cognitive-foundation citations for design decisions
2. `oligon-brand` → load tokens and set style
3. `plotting-libraries` → implement figure code
4. `visual-design` → review for design quality
5. Pre-submission gate → run `../shared/references/pre_submission_checklist.md`

**For brand-skill authors:** This skill is the reference implementation of the contract in [`../BRAND_SKILL_INTERFACE.md`](../BRAND_SKILL_INTERFACE.md). To create an alternative brand skill, mirror this directory's structure and validate with the tooling in [`../brand-interface/`](../brand-interface/README.md) (JSON Schema, type stubs, WCAG checker, and 173 tests).
</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `references/brand-colors-full.md` | Complete V4 brand specification with all color codes, typography, and embedded logo SVGs |
| `tokens/brand-tokens.json` | Machine-readable brand tokens for programmatic access |
| `assets/oligon_color_brand.mplstyle` | Matplotlib style file for one-line brand application |

### Color Quick Reference

| Name | Role | HEX |
|------|------|-----|
| Brand Blue | Hero highlight | `#2DB2E8` |
| Contrast Orange | Opposing effects | `#E8622D` |
| Dark Gray | Primary data / control | `#222222` |
| Medium Gray | Secondary data | `#666666` |
| Muted Gray | Tertiary data | `#999999` |
| Light Gray | Annotations only | `#BDBDBD` |
| Medium Blue | Additional categorical | `#158BBB` |

### Typography Quick Reference

**Figures:**
| Element | Font | Size |
|---------|------|------|
| Panel labels (A, B, C) | Arial Bold | 9-10 pt |
| Axis labels | Arial | 8 pt |
| Tick labels | Arial | 7-8 pt |
| Legend text | Arial | 7-8 pt |

**Documents:**
| Element | Font | Size |
|---------|------|------|
| Body text | Arial | 11 pt |
| Heading 1 | Arial Bold | 14 pt |
| Heading 2 | Arial Bold | 12 pt |

### Logo Assets

| Variant | File | Use On |
|---------|------|--------|
| Full Logo (Brand Blue) | `assets/Oligon_Logo_BrandBlue.svg` | Light backgrounds |
| Full Logo (White) | `assets/Oligon_Logo_White.svg` | Dark backgrounds |
| Icon (Brand Blue) | `assets/Oligon_Icon_BrandBlue.svg` | Light backgrounds |
| Icon (White) | `assets/Oligon_Icon_White.svg` | Dark backgrounds |

> **Do NOT place logos on publication figures** — journals prohibit branding. Use on presentations, posters, and internal documents only.

For complete color tables and detailed specifications, see `references/brand-colors-full.md`.
</references>
