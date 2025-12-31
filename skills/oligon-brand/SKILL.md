---
name: oligon-brand
version: 4.0.1
description: "Oligon scientific brand implementation for figures, presentations, and documents. Provides color palettes, typography standards, and format-specific adapters for matplotlib, ggplot2, ReportLab, python-docx, python-pptx, and HTML/CSS."
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

<when_to_use>
## Trigger Conditions

**Use this skill when:**
- Creating figures for Oligon-branded publications
- Applying consistent brand colors to matplotlib/seaborn/ggplot2 plots
- Styling presentations or documents with Oligon identity
- Need to access brand color hex codes programmatically
- Creating branded PDFs, Word documents, or PowerPoint presentations

**Do NOT use this skill when:**
- Working on non-Oligon projects → use `visual-design` defaults
- Need general design philosophy → use `visual-design`
- Writing plotting code → use `plotting-libraries` (which references this skill)
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

<scope>
## Scope

**In Scope:**
- Color palette definitions and usage guidance
- Format-specific adapters (matplotlib, ggplot2, ReportLab, etc.)
- Typography standards for figures and documents
- Logo usage guidelines
- Preflight verification checklist

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
| `visual-design` | **Design philosophy** — provides universal principles; oligon-brand provides Oligon-specific implementation |
| `plotting-libraries` | **Code implementation** — use plotting-libraries for matplotlib/ggplot2 code patterns; load oligon-brand first for brand colors |
| `scientific-slides` | **Presentations** — apply oligon-brand colors to slide designs |
| `latex-posters` / `pptx-posters` | **Posters** — apply oligon-brand colors and logo placement |
| `markdown-to-pdf` | **PDF reports** — uses brand colors for styled output |
| `document-skills/docx` | **Word documents** — use docx_adapter for branded styling |

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Typical Workflow:**
1. `oligon-brand` → load tokens and set style
2. `plotting-libraries` → implement figure code
3. `visual-design` → review for design quality
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
