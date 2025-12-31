---
name: oligon-brand
description: Scientific brand visual identity for figures, charts, presentations, and documents. Apply when creating or styling matplotlib/ggplot2 plots, scientific figures (volcano, Kaplan-Meier, heatmaps, bar charts), PowerPoint presentations, Word documents, grants, manuscripts, or any visualization requiring brand colors. Triggers on requests for figures, plots, charts, graphs, slides, presentations, documents, brand styling, or scientific visualizations.
---

# Oligon Scientific Brand Guidelines

## Core Principle

**Neutrals are default; Brand Colors are for highlights; Contrast colors show opposition.**

Most data should be grayscale. Brand Blue highlights the most important element (1-2 per panel max).

---

## 1. Color Palette (Quick Reference)

### Primary & Accent Colors

| Role | Color | HEX |
|------|-------|-----|
| **Brand Blue** (hero highlight) | Bright Blue | `#2DB2E8` |
| **Contrast** (opposing effects) | Vermilion/Orange | `#E8622D` |

### Neutral Data Colors (Default)

| Role | Color | HEX |
|------|-------|-----|
| Primary data | Very Dark Gray | `#222222` |
| Secondary data | Medium Gray | `#666666` |
| Tertiary data | Muted Gray | `#999999` |
| Annotations only | Light Gray | `#BDBDBD` |

> **Note:** `#BDBDBD` lacks contrast for data points—use only for gridlines, annotations, or non-significant points.

### Supporting Colors (Limited Use)

| Role | Color | HEX |
|------|-------|-----|
| Additional categorical | Medium Blue | `#158BBB` |
| Heatmap negative extreme | Dark Teal | `#0F5D7D` |
| Heatmap positive extreme | Dark Warm | `#7D250F` |

### Structure

| Element | Color | HEX |
|---------|-------|-----|
| Backgrounds | White only | `#FFFFFF` |
| Axes, text, labels | Black | `#000000` |
| Gridlines (if needed) | Light | `#E5E5E5` |

### Logo

| Variant | Color | HEX | Use On | File |
|---------|-------|-----|--------|------|
| Full Logo | Brand Blue | `#2DB2E8` | White/light backgrounds | `assets/Oligon_Logo_BrandBlue.svg` |
| Full Logo | White | `#FFFFFF` | Dark backgrounds | `assets/Oligon_Logo_White.svg` |
| Icon | Brand Blue | `#2DB2E8` | White/light backgrounds | `assets/Oligon_Icon_BrandBlue.svg` |
| Icon | White | `#FFFFFF` | Dark backgrounds | `assets/Oligon_Icon_White.svg` |

> **Do NOT place logos on publication figures** — journals prohibit branding. Use on presentations, posters, and internal documents only.

> **Historical note:** Original logo files used `#00A3DA`. Updated versions use canonical brand blue `#2DB2E8` for palette consistency.

---

## 2. Color Cycle Selection

**Do not use library defaults.** Select based on scientific context:

### Cycle 1: Control vs. Treatment (Most Common)

```python
CYCLE_TREATMENT_CONTROL = ["#222222", "#2DB2E8", "#666666"]
```

| Order | HEX | Use For |
|-------|-----|---------|
| 1 | `#222222` | Control / Baseline |
| 2 | `#2DB2E8` | Treatment / Experimental |
| 3 | `#666666` | Secondary comparison |

### Cycle 2: Neutrals Only (No Highlight)

```python
CYCLE_NEUTRALS_ONLY = ["#222222", "#666666", "#999999"]
```

Use when all groups are equal weight—no single condition deserves emphasis.

### Cycle 3: Opposing Effects (Up vs. Down)

```python
CYCLE_OPPOSING = ["#2DB2E8", "#E8622D", "#222222"]
```

| Order | HEX | Use For |
|-------|-----|---------|
| 1 | `#2DB2E8` | Direction A (e.g., Down-regulated) |
| 2 | `#E8622D` | Direction B (e.g., Up-regulated) |
| 3 | `#222222` | Neutral / Unchanged |

### Cycle 4: Multiple Categories (≤4 groups, use sparingly)

```python
CYCLE_MULTI_CATEGORY = ["#222222", "#2DB2E8", "#666666", "#158BBB"]
```

**Mandatory:** Combine with marker shapes (circle, square, triangle, diamond) for accessibility.

> **5+ categories:** Redesign the figure using faceting or small multiples.

---

## 3. Decision Tree

```
How many data series?
│
├─► 1 series → Use #222222 (no highlight needed)
│
├─► 2 series
│   ├─► Treatment vs. Control? → Cycle 1
│   └─► Opposing effects? → Cycle 3
│
├─► 3 series
│   ├─► One highlighted? → Cycle 1
│   ├─► All equal weight? → Cycle 2
│   └─► Two opposing + neutral? → Cycle 3
│
├─► 4 series → Cycle 4 + marker shapes
│
└─► 5+ series → REDESIGN (facet/small multiples)
```

---

## 4. Figure Standards

### Layout ("Despined")

- Keep **left and bottom** spines only—remove top and right
- Axis lines: thin black (0.8 pt)
- Gridlines: off by default; if needed, thin light gray `#E5E5E5`

### Typography (Figures)

| Element | Font | Size |
|---------|------|------|
| Panel labels (A, B, C) | Arial Bold | 9–10 pt |
| Axis labels | Arial | 8 pt |
| Tick labels | Arial | 7–8 pt |
| Legend text | Arial | 7–8 pt |
| Annotations | Arial | 7 pt |

### Error Bars

Always state in legend: "Error bars represent [SEM/SD/95% CI], n = X"

- Discrete data: thin error bars (0.75 pt)
- Continuous data: semi-transparent fill bands (20–30% opacity)

### Resolution

| Context | Resolution | Format |
|---------|------------|--------|
| Print/Publication | 300+ DPI | TIFF, PDF, EPS |
| Screen/Presentation | 150 DPI | PNG, PDF |

---

## 5. Document Standards

### Typography (Word Documents)

| Element | Font | Size | Style |
|---------|------|------|-------|
| Body text | Arial | 11 pt | Regular |
| Heading 1 | Arial | 14 pt | Bold |
| Heading 2 | Arial | 12 pt | Bold |
| Heading 3 | Arial | 11 pt | Bold |
| Figure captions | Arial | 10 pt | Italic |

---

## 6. Presentation Standards

Apply brand colors to slides:

- Background: White (`#FFFFFF`)
- Title text: Black (`#000000`) or Dark Gray (`#222222`)
- Accent elements: Brand Blue (`#2DB2E8`)
- Contrast/highlights: Use sparingly per figure rules
- Logo placement: Header or footer only, not on data panels

---

## 7. Accessibility Requirements

1. **All figures must work in grayscale**—test before finalizing
2. **Never rely on color alone**—use line styles, marker shapes, or labels
3. **Blue-orange pair is colorblind-safe** (`#2DB2E8` + `#E8622D`)
4. Do not use `#2DB2E8` vs `#158BBB` as primary differentiator (too similar)

---

## 8. Pre-Flight Checklist

Before finalizing any figure:

- [ ] White background (`#FFFFFF`)
- [ ] Black text and axes (`#000000`)
- [ ] Top and right spines removed
- [ ] Correct color cycle for context
- [ ] Brand Blue limited to 1–2 elements per panel
- [ ] No library default colors
- [ ] Redundant encoding (shapes/styles with color)
- [ ] Tested in grayscale
- [ ] Error bars labeled in legend
- [ ] Arial font, 7–9 pt range
- [ ] Resolution ≥300 DPI for print
- [ ] Logo excluded from publication figures

---

## 9. Bundled Resources

### Assets

- `assets/oligon_color_brand.mplstyle` — Matplotlib style file (apply with `plt.style.use()`)
- `assets/Oligon_Logo_BrandBlue.svg` — Full wordmark logo for light backgrounds
- `assets/Oligon_Logo_White.svg` — Full wordmark logo for dark backgrounds
- `assets/Oligon_Icon_BrandBlue.svg` — Icon only for light backgrounds
- `assets/Oligon_Icon_White.svg` — Icon only for dark backgrounds

To install the mplstyle permanently, copy to matplotlib's stylelib folder:

```python
import matplotlib
print(matplotlib.get_configdir())  # Copy .mplstyle to stylelib/ subfolder
```

### Scripts

Companion modules with color constants and helper functions:

- `scripts/matplotlib_brand_setup.py` — Color constants, cycles, divergent colormap, panel labels
- `scripts/ggplot2_brand_setup.R` — Complete R/ggplot2 configuration

### References

For detailed guidance on specific plot types (Kaplan-Meier, volcano, heatmaps, etc.):

- `references/brand-colors-full.md` — Complete v4 specification with all templates and embedded logo SVGs
