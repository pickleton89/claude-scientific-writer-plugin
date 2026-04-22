---
name: oligon-brand
version: 4.1.0
description: "Oligon scientific brand implementation for figures, presentations, and documents. Provides color palettes, typography standards, format-specific adapters (matplotlib, ggplot2, ReportLab, python-docx, python-pptx, HTML/CSS), and a `<design_foundation>` block with cross-format decision flow, audience matrix, and universal anti-patterns (with generic-fallback for non-Oligon output)."
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
- Need general design philosophy → see this skill's `<design_foundation>` block below (includes a generic-fallback paragraph for non-Oligon output)
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

<design_foundation>
## Design Foundation

Universal design principles that apply across every output format. Oligon-specific application lives in the other sections of this skill; this block is the brand-agnostic decision flow a designer should run *before* picking colors and fonts.

> **Generic-fallback use.** For non-Oligon output (unbranded manuscripts, cross-organization collaborations, personal projects), follow these same principles but substitute: **viridis/cividis** for sequential data, **Okabe-Ito** (8-color) for categorical data, **ColorBrewer diverging** (RdBu, PuOr) for diverging data, and validate contrast with the WebAIM Contrast Checker or WCAG 2.1 AA tooling. The rest of this section is venue- and brand-agnostic.

### Decision Flow

```
Who is the viewer?           → audience matrix (below)
   ↓
What story in one sentence?  → single-message test
   ↓
Which chart type?            → plotting-libraries/scripts/chart_selector
   ↓
Which palette?               → oligon-brand tokens (default)
                               or plotting-libraries/scripts/palette_selector (generic)
   ↓
Accessibility check          → skills/shared/accessibility/ (contrast, CVD, grayscale)
   ↓
Venue constraints            → venue-templates/references/figure_specs.md
```

Each arrow is a gate: do not proceed until the prior step has a concrete answer.

### Audience Matrix

| Audience | Output | Design direction |
|----------|--------|------------------|
| Journal reviewers / academic peers | Data-heavy figures | Precise, restrained, minimal decoration; conservative palette; exact venue dimensions; 300 DPI |
| Journal reviewers / academic peers | Conceptual figures | Clean, professional, publishable; standard typography (Helvetica/Arial) |
| Conference audience | Poster | Bold, scannable in 3 seconds; ≥24 pt body, ≥48 pt headers; high contrast |
| Conference audience | Talk slides | Impactful, one idea per slide; minimal text, maximum visual; dark backgrounds acceptable |
| General public / media | Any | Accessible, engaging, memorable; avoid jargon; visual metaphors; higher visual impact acceptable |
| Internal team | Any | Functional, clear, quick to produce; standard templates acceptable; information over aesthetics |

### Single-Message Test

For every figure, answer in one sentence: *"What single insight should the viewer take away?"* If you can't answer in one sentence, the figure is doing too many jobs — split into panels or into multiple figures.

### Universal Design Pitfalls

These apply regardless of brand. Oligon-specific pitfalls (e.g., overusing Brand Blue) are in the `<anti_patterns>` block below.

1. **Default Syndrome** — tool defaults (gray backgrounds, thin lines, small fonts, stock colors) without justification. Every choice should answer "why this?"
2. **Rainbow Colormap for Sequential Data** — rainbow/jet is perceptually uneven and not colorblind-safe. Use viridis/plasma/magma (sequential), cividis (CVD-optimized), or RdBu/PuOr (diverging).
3. **Color-Only Encoding** — groups distinguished only by color fail for CVD viewers and grayscale printing. Add redundant encoding: shapes, line styles, direct labels, hatching.
4. **Cramming** — too many panels, data series, or annotations. Limit to one main message per figure; move supporting detail to supplementary panels.
5. **Inconsistent Styling** — different fonts, colors, or sizing across panels in one document. Define a style guide (hex codes, typography hierarchy) before starting.
6. **Truncated Axes** — y-axis starting above zero to exaggerate small differences. Start bar charts at zero; indicate breaks explicitly if unavoidable.
7. **3D for 2D Data** — 3D bar or pie charts distort perception. Use 3D only for genuinely volumetric/spatial data.

### Output-Format Guidance

Absorbed from the former `OUTPUT_FORMATS.md`. For implementation code see the linked skills.

**Figures (matplotlib/seaborn/SVG)** — delegate code to `plotting-libraries`; dimensions from `venue-templates/references/figure_specs.md`. 300 DPI for print, 150 DPI for screen. Prefer PDF/EPS (vector) over TIFF/PNG (raster). Embed fonts in PDF outputs.

**Infographics (SVG)** — one clear message per infographic; visual metaphors that aid (not decorate); prominent data callouts; minimal text. SVG enables infinite scaling, vector-editing, and web embedding. Components in `skills/shared/svg-components/`.

**Report illustrations (ReportLab)** — use the `oligon-brand/adapters/reportlab_adapter.py` building blocks: `MetricCard`, `CalloutBox`, `SectionHeader`, `DataTable`. Consistent margins, brand accents, hierarchical typography, section breaks.

**Presentations (PPTX/Beamer)** — one idea per slide; ≥24 pt body, ≥36 pt titles; high-contrast for projection; simplify journal figures (larger fonts, thicker lines); avoid subtle gradients. Dark vs light per venue.

**Posters** — scannable hierarchy (title in 3 s, key figure in 10 s, details in 60 s); ≤4 colors; generous whitespace; QR code for supplementary resources; view-distance font sizing.
</design_foundation>

<scope>
## Scope

**In Scope:**
- Color palette definitions and usage guidance
- Format-specific adapters (matplotlib, ggplot2, ReportLab, etc.)
- Typography standards for figures and documents
- Logo usage guidelines
- Preflight verification checklist

**Out of Scope:**
- Writing plotting code → use `plotting-libraries`
- Journal-specific requirements and figure-dimension specs → use `venue-templates`
- Accessibility utilities (contrast, CVD simulation, WCAG validation) → `skills/shared/accessibility/`
- Diagram creation → use `scientific-schematics`

Design philosophy that applies across formats lives in the `<design_foundation>` block above — not a separate skill.
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
| `plotting-libraries` | **Code implementation** — use plotting-libraries for matplotlib/ggplot2 code patterns; load oligon-brand first for brand colors. Hosts `chart_selector` and `palette_selector` utilities. |
| `skills/shared/accessibility/` | **WCAG validation** — contrast ratios, colorblind-safe checks, figure-spec validation |
| `venue-templates` | **Figure dimensions & manuscript formatting** — column widths, DPI, preferred formats per journal |
| `scientific-slides` | **Presentations** — apply oligon-brand colors to slide designs |
| `research-posters` | **Posters** — apply oligon-brand colors and logo placement |
| `markdown-to-pdf` | **PDF reports** — uses brand colors for styled output |
| `document-skills:docx` | **Word documents** — use docx_adapter for branded styling |

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Typical Workflow:**
1. `oligon-brand` → consult `<design_foundation>`, then load tokens and set style
2. `plotting-libraries` → implement figure code (with `chart_selector`/`palette_selector` if needed)
3. `skills/shared/accessibility/` → validate contrast, CVD-safety, and figure-spec compliance

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
