# Scientific Output Design Specification

> **Version:** 1.0.0
> **Created:** 2026-01-20
> **Status:** Active
> **Applies to:** All visual generation skills in claude-scientific-writer-plugin

## Executive Summary

This specification establishes design standards for all visual outputs from the Claude Scientific Writer plugin. It addresses the gap between:
- **AI-generated imagery** that looks "obviously generated" and undermines scientific credibility
- **Plain LaTeX/Beamer output** that is functional but visually bland

**Goal:** Create professional, publication-quality visuals that communicate scientific content clearly without relying on decorative AI imagery.

---

## Core Design Principles

### 1. Content Over Decoration

> **The visual should serve the science, not the other way around.**

| Do | Don't |
|:---|:------|
| Use diagrams that explain concepts | Use AI-generated "conceptual art" |
| Show actual data visualizations | Use abstract network visualizations as filler |
| Create clear workflow diagrams | Add decorative imagery for visual interest |
| Let whitespace work | Fill every space with graphics |

### 2. Geometric Precision Over Generative Ambiguity

AI image generators produce:
- Flowing, organic shapes with no precise meaning
- "Data visualization" aesthetics without actual data
- Abstract representations that viewers must interpret

Instead, prefer:
- Clean geometric shapes (rectangles, circles, arrows)
- Diagrams with specific, labeled components
- Charts derived from real data
- Icons from curated scientific icon libraries

### 3. Scientific Credibility First

| Output Context | Imagery Guideline |
|----------------|-------------------|
| **Journal figures** | Zero decorative imagery; only data plots and essential diagrams |
| **Conference presentations** | Minimal imagery; prefer diagrams over photos/AI art |
| **Posters** | Strategic imagery allowed; must relate directly to content |
| **Internal/educational** | More flexibility; still avoid obvious AI aesthetics |

---

## Visual Hierarchy

### Presentation Slides

```
┌─────────────────────────────────────────────────────────────┐
│  Title (32-44pt, Bold)                                      │
│                                                             │
│  ┌─────────────────────┐    • Key point 1 (18-24pt)        │
│  │                     │    • Key point 2                   │
│  │    DIAGRAM or       │    • Key point 3                   │
│  │    DATA VISUAL      │                                    │
│  │    (60% of width)   │                                    │
│  │                     │                                    │
│  └─────────────────────┘                                    │
│                                                             │
│  Footer: Source / Attribution (10-12pt)                     │
└─────────────────────────────────────────────────────────────┘
```

### Typography Hierarchy

| Element | Font | Size (Slides) | Size (Figures) | Weight |
|---------|------|---------------|----------------|--------|
| Slide title | Arial/Helvetica | 32-44 pt | — | Bold |
| Section header | Arial/Helvetica | 24-28 pt | 12-14 pt | Bold |
| Body text | Arial/Helvetica | 18-24 pt | 10-12 pt | Regular |
| Bullet points | Arial/Helvetica | 18-24 pt | — | Regular |
| Axis labels | Arial/Helvetica | — | 8-10 pt | Regular |
| Captions | Arial/Helvetica | 12-14 pt | 7-9 pt | Regular |
| Footer | Arial/Helvetica | 10-12 pt | 6-8 pt | Regular |

---

## Color System

### Primary Palette (Oligon Brand)

Use the established Oligon brand colors with the core principle: **Neutrals are default; Brand Blue is for highlights.**

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| **Primary data / Control** | Dark Gray | `#222222` | Default for most data, text |
| **Highlight / Treatment** | Brand Blue | `#2DB2E8` | 1-2 elements per panel MAX |
| **Secondary data** | Medium Gray | `#666666` | Supporting data series |
| **Tertiary data** | Muted Gray | `#999999` | Background data, annotations |
| **Opposing / Contrast** | Orange | `#E8622D` | Opposing effects, warnings |
| **Background** | White | `#FFFFFF` | All backgrounds |

### Color Usage Rules

1. **Most data should be grayscale** — Brand Blue highlights only the most important element
2. **Never use more than 5 colors** in a single panel — redesign with faceting if needed
3. **Always include redundant encoding** — shapes, patterns, or labels alongside color
4. **Test in grayscale** before finalizing

### Forbidden Colors/Patterns

| Avoid | Why | Instead Use |
|-------|-----|-------------|
| Red-green combinations | Colorblind inaccessible | Blue-orange or Okabe-Ito |
| Rainbow/jet colormaps | Perceptually uneven | Viridis, Cividis |
| Gradients as backgrounds | Distracting, unprofessional | Solid white |
| Drop shadows | Looks dated, adds noise | Clean flat design |
| 3D effects | Distorts perception | 2D representations |

---

## Diagram Standards

### Workflow Diagrams

Use simple geometric shapes with clear flow:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│              │     │              │     │              │
│   Stage 1    │────▶│   Stage 2    │────▶│   Stage 3    │
│              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

**Implementation:**
- Rounded rectangles (8-12px radius) for process steps
- Straight arrows with consistent weight (2-3pt)
- Equal spacing between elements
- Max 5-7 elements per row before wrapping

### Comparison Layouts

For side-by-side comparisons:

```
┌─────────────────────────────────────────────┐
│                  TITLE                       │
├──────────────────────┬──────────────────────┤
│     Category A       │     Category B        │
├──────────────────────┼──────────────────────┤
│  • Point 1           │  • Point 1            │
│  • Point 2           │  • Point 2            │
│  • Point 3           │  • Point 3            │
└──────────────────────┴──────────────────────┘
```

### Icon Usage

**Approved sources:**
1. Scientific icons from `skills/scientific-icons/` (900+ domain icons)
2. Simple geometric shapes drawn programmatically
3. Standard unicode symbols where appropriate

**Icon requirements:**
- Consistent line weight across all icons (2pt recommended)
- Single color (Brand Blue or Dark Gray)
- Appropriate size relative to text (1.5-2x line height)
- Never use clipart-style or photorealistic icons

---

## Output Format Specifications

### Presentations (PPTX/PDF)

| Attribute | Specification |
|-----------|---------------|
| Aspect ratio | 16:9 (widescreen) |
| Resolution | 1920 x 1080 px minimum |
| Font embedding | Required |
| Image resolution | 150 DPI minimum |
| Background | White (`#FFFFFF`) |

### Publication Figures

| Attribute | Specification |
|-----------|---------------|
| Format | PDF (vector) or TIFF (raster) |
| Resolution | 300 DPI minimum, 600+ for line art |
| Color mode | RGB (convert to CMYK at submission) |
| Single column | 89mm / 3.5" (Nature standard) |
| Double column | 183mm / 7.2" |

### Posters

| Attribute | Specification |
|-----------|---------------|
| Common sizes | A0 (841 x 1189 mm), 48" x 36" |
| Resolution | 150-300 DPI |
| Minimum font | 24pt body, 48pt headers |
| Viewing distance | Design for 3-5 feet |

---

## What NOT to Generate

### Banned Visual Elements

| Element | Problem | Alternative |
|---------|---------|-------------|
| AI-generated "network" visualizations | Obvious AI aesthetic, no meaning | Actual network diagrams with labeled nodes |
| Flowing abstract "data streams" | Decorative, not informative | Real data flow diagrams |
| Generic cell/molecule imagery | Stock photo quality | Actual structural data or simple icons |
| Photorealistic backgrounds | Distracting, unprofessional | White or subtle solid colors |
| "Futuristic" UI overlays | Dated sci-fi aesthetic | Clean, minimal layouts |
| Lens flares, glows, sparkles | Unprofessional | Nothing — remove entirely |

### When AI Imagery Might Be Acceptable

Limited contexts where AI generation could work:

1. **Graphical abstracts** — where artistic interpretation is expected
2. **Public engagement materials** — social media, press releases
3. **Educational illustrations** — where clarity matters more than accuracy
4. **Explicitly artistic outputs** — when the user requests creative interpretation

Even in these cases:
- Verify output doesn't have telltale AI artifacts
- Ensure scientific accuracy isn't compromised
- Get explicit user approval before including

---

## Implementation Guidelines

### For `scientific-slides` Skill

```yaml
default_behavior:
  background: white
  imagery: geometric_diagrams_only
  ai_generation: disabled_by_default

workflow:
  1. Parse content structure
  2. Generate layout with text placeholders
  3. Create geometric diagrams for workflows/comparisons
  4. Add data visualizations from plotting-libraries
  5. Apply Oligon brand colors
  6. Render to target format
```

### For `scientific-schematics` Skill

```yaml
preferred_methods:
  - mermaid_diagrams      # For flowcharts, sequences
  - tikz_diagrams         # For precise technical drawings
  - matplotlib_patches    # For geometric layouts
  - python_pptx_shapes    # For slide graphics

avoid:
  - ai_image_generation   # Unless explicitly requested
  - stock_imagery
  - decorative_elements
```

### For `plotting-libraries` Skill

```yaml
defaults:
  style: oligon_brand
  background: white
  spines: [bottom, left]  # Remove top, right
  grid: minimal_or_none

data_presentation:
  show_individual_points: true
  error_bars: required
  statistics: labeled_in_caption
```

---

## Quality Checklist

Before any visual output is finalized:

### Technical Quality
- [ ] Resolution meets target specification
- [ ] Fonts are embedded (for PDF/PPTX)
- [ ] Colors match brand specification
- [ ] All text readable at final size (≥7pt)

### Design Quality
- [ ] Single clear message per visual
- [ ] No decorative-only elements
- [ ] Consistent styling throughout
- [ ] Adequate whitespace

### Scientific Quality
- [ ] Data accurately represented
- [ ] Axes labeled with units
- [ ] Error bars present (where applicable)
- [ ] Source/attribution included

### Accessibility
- [ ] Passes grayscale test
- [ ] Colorblind-safe palette used
- [ ] Redundant encoding present
- [ ] Contrast ratio ≥4.5:1 for text

---

## Examples

### Good: Workflow Diagram (Slide 3 from SCP presentation)

The "Scope of Recommendations" slide demonstrates proper design:
- Clean 4-box horizontal flow
- Consistent rounded rectangles
- Single-weight line icons
- Brand blue color
- Clear arrow progression
- Minimal text in boxes

### Bad: Title Slide with AI Network

The title slide demonstrates problems:
- AI-generated flowing network image
- No specific meaning conveyed
- "Obviously generated" aesthetic
- Competes with text for attention

### Improved: Title Slide Approach

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                                                             │
│      'Initial Recommendations for                           │
│       Single-Cell Proteomics'                              │
│                                                             │
│      Gatto et al., Nature Methods 2023                     │
│                                                             │
│      ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                    │
│      │ ● ● │  │ ▼   │  │ ◆◆◆ │  │ ═══ │                    │
│      │ ●●● │→ │ ▼▼  │→ │ ◆◆  │→ │ ─── │                    │
│      │cells│  │prep │  │ MS  │  │data │                    │
│      └─────┘  └─────┘  └─────┘  └─────┘                    │
│                                                             │
│      Journal Club Presentation                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Simple icons representing the workflow stages, not AI-generated imagery.

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-20 | Initial specification based on design analysis |

---

## Related Documents

- `skills/oligon-brand/SKILL.md` — Brand colors, typography, logos
- `skills/visual-design/SKILL.md` — Design philosophy and principles
- `skills/visual-design/references/publication_specs.md` — Journal requirements
- `skills/plotting-libraries/SKILL.md` — Data visualization implementation
- `skills/scientific-schematics/SKILL.md` — Diagram generation
