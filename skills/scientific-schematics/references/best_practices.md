# Best Practices for Scientific Diagrams

## Overview

This guide provides publication standards, accessibility guidelines, and best practices for creating high-quality scientific diagrams that meet journal requirements and communicate effectively to all readers.

## Publication Standards

### 1. File Format Requirements

**Vector Formats (Preferred)**
- **PDF**: Universal acceptance, preserves quality, works with LaTeX
  - Use for: Line drawings, flowcharts, block diagrams, circuit diagrams
  - Advantages: Scalable, small file size, embeds fonts
  - Standard for LaTeX workflows

- **EPS (Encapsulated PostScript)**: Legacy format, still accepted
  - Use for: Older publishing systems
  - Compatible with most journals
  - Can be converted from PDF

- **SVG (Scalable Vector Graphics)**: Web-friendly, increasingly accepted
  - Use for: Online publications, interactive figures
  - Can be edited in vector graphics software
  - Not all journals accept SVG

**Raster Formats (When Necessary)**
- **TIFF**: Professional standard for raster graphics
  - Use for: Microscopy images, photographs combined with diagrams
  - Minimum 300 DPI at final print size
  - Lossless compression (LZW)

- **PNG**: Web-friendly, lossless compression
  - Use for: Online supplementary materials, presentations
  - Minimum 300 DPI for print
  - Supports transparency

**Never Use**
- **JPEG**: Lossy compression creates artifacts in diagrams
- **GIF**: Limited colors, inappropriate for scientific figures
- **BMP**: Uncompressed, unnecessarily large files

### 2. Resolution Requirements

**Vector Graphics**
- Infinite resolution (scalable)
- **Recommended**: Always use vector when possible

**Raster Graphics (when vector not possible)**
- **Publication quality**: 300-600 DPI
- **Line art**: 600-1200 DPI
- **Web/screen**: 150 DPI acceptable
- **Never**: Below 300 DPI for print

**Calculating DPI**
```
DPI = pixels / (inches at final size)

Example:
Image size: 2400 × 1800 pixels
Final print size: 8 × 6 inches
DPI = 2400 / 8 = 300 ✓ (acceptable)
```

### 3. Size and Dimensions

**Journal-Specific Column Widths**
- **Nature**: Single column 89 mm (3.5 in), Double 183 mm (7.2 in)
- **Science**: Single column 55 mm (2.17 in), Double 120 mm (4.72 in)
- **Cell**: Single column 85 mm (3.35 in), Double 178 mm (7 in)
- **PLOS**: Single column 83 mm (3.27 in), Double 173 mm (6.83 in)
- **IEEE**: Single column 3.5 in, Double 7.16 in

**Best Practices**
- Design at final print size (avoid scaling)
- Use journal templates when available
- Allow margins for cropping
- Test appearance at final size before submission

### 4. Typography Standards

**Font Selection**
- **Recommended**: Arial, Helvetica, Calibri (sans-serif)
- **Acceptable**: Times New Roman (serif) for mathematics-heavy
- **Avoid**: Decorative fonts, script fonts, system fonts that may not embed

**Font Sizes (at final print size)**
- **Minimum**: 6-7 pt (journal dependent)
- **Axis labels**: 8-9 pt
- **Figure labels**: 10-12 pt
- **Panel labels (A, B, C)**: 10-14 pt, bold
- **Main text**: Should match manuscript body text

**Text Clarity**
- Use sentence case: "Time (seconds)" not "TIME (SECONDS)"
- Include units in parentheses: "Temperature (°C)"
- Spell out abbreviations in figure caption
- Avoid rotated text when possible (exception: y-axis labels)

### 5. Line Weights and Strokes

**Recommended Line Widths**
- **Diagram outlines**: 0.5-1.0 pt
- **Connection lines/arrows**: 1.0-2.0 pt
- **Emphasis elements**: 2.0-3.0 pt
- **Minimum visible**: 0.25 pt at final size

**Consistency and Magnitude**
- **Width is a style constant within a role** — every element playing the same role (all node outlines, all activation arrows, all compartment boundaries) carries one stroke width. Varying width inside a role for visual interest is decoration, and readers decode it as an unintended claim
- **Hierarchy is expressed across roles, never within one** — emphasis elements heavier than connectors, connectors heavier than outlines; then each of those weights is held fixed
- **Width may carry ordinal magnitude across instances of a single role, and only when the legend declares it** — for example, thicker = larger flux across the arrows of one pathway. Ordinal comparison only ("more than / less than"), never value-reading off the page: Cleveland & McGill rank position and length above area and width, which makes width a weak quantitative channel (see Canonical Arrow Legend)
- **Respect the venue's stroke floor** — never go below the journal minimum (Cell specifies 0.5 pt; see Journal-Specific Guidelines), and avoid hairline rules, which do not print reliably. A legend-declared width ramp must fit entirely above that floor, so a venue with a 0.5 pt floor supports fewer distinguishable width steps than one without

## Accessibility and Colorblindness

### 1. Colorblind-Safe Palettes

**Okabe-Ito Palette (Recommended)**
Most distinguishable by all types of colorblindness:

```latex
% RGB values
Orange:     #E69F00 (230, 159,   0)
Sky Blue:   #56B4E9 ( 86, 180, 233)
Green:      #009E73 (  0, 158, 115)
Yellow:     #F0E442 (240, 228,  66)
Blue:       #0072B2 (  0, 114, 178)
Vermillion: #D55E00 (213,  94,   0)
Purple:     #CC79A7 (204, 121, 167)
Black:      #000000 (  0,   0,   0)
```

**Alternative: ColorBrewer Palettes**
- **Qualitative**: Set2, Paired, Dark2
- **Sequential**: Blues, Greens, Oranges (avoid Reds/Greens together)
- **Diverging**: RdBu (Red-Blue), PuOr (Purple-Orange)

**Colors to Avoid Together**
- Red-Green combinations (8% of males cannot distinguish)
- Blue-Purple combinations
- Yellow-Light green combinations

### 2. Redundant Encoding

Don't rely on color alone. Use multiple visual channels:

**Shape + Color**
```
Circle + Blue   = Condition A
Square + Orange = Condition B
Triangle + Green = Condition C
```

**Line Style + Color**
```
Solid + Blue = Treatment 1
Dashed + Orange = Treatment 2
Dotted + Green = Control
```

**Scope — data plots.** Dashed here is a *categorical series identifier*, not a claim about mechanism: it is the color-vision-deficiency redundant-encoding device that separates Treatment 2 from Treatment 1 without relying on hue. This use is fully legal in data plots and is explicitly exempt from the mechanism-diagram rule that dashed means indirect / hypothetical / context-dependent (see Canonical Arrow Legend). The two uses must never appear in the same figure.

**Pattern Fill + Color**
```
Solid fill + Blue = Group A
Diagonal stripes + Orange = Group B
Cross-hatch + Green = Group C
```

### 3. Grayscale Compatibility

**Test Requirement**: All diagrams must be interpretable in grayscale

**Strategies**
- Use different shades (light, medium, dark)
- Add patterns or textures to filled areas
- Vary line styles (solid, dashed, dotted) to identify series — a legal categorical use of dashed in data plots, distinct from its canonical mechanism-diagram meaning (see Canonical Arrow Legend)
- Use labels directly on elements
- Include text annotations

**Grayscale Test**
```bash
# Convert to grayscale to test
convert diagram.pdf -colorspace gray diagram_gray.pdf
```

### 4. Contrast Requirements

**Minimum Contrast Ratios (WCAG Guidelines)**
- **Normal text**: 4.5:1
- **Large text** (≥18pt): 3:1
- **Graphical elements**: 3:1

**High Contrast Practices**
- Dark text on light background (or vice versa)
- Avoid low-contrast color pairs (yellow on white, light gray on white)
- Use black or dark gray for critical text
- White text on dark backgrounds needs larger font size

### 5. Alternative Text and Descriptions

**Figure Captions Must Include**
- Description of diagram type
- All abbreviations spelled out
- Explanation of symbols and colors
- Sample sizes (n) where relevant
- Statistical annotations explained
- Reference to detailed methods if applicable

**Example Caption**
"Participant flow diagram following CONSORT guidelines. Rectangles represent study stages, with participant numbers (n) shown. Exclusion criteria are listed beside each screening stage. Final analysis included n=350 participants across two groups."

## Design Principles

### 1. Simplicity and Clarity

**Occam's Razor for Diagrams**
- Remove every element that doesn't add information
- Simplify complex relationships
- Break complex diagrams into multiple panels
- Use consistent layouts across related figures

**Visual Hierarchy**
- Most important elements: Largest, darkest, central
- Supporting elements: Smaller, lighter, peripheral
- Annotations: Minimal, clear labels only

### 2. Consistency

**Within a Figure**
- Same shape/color represents same concept
- Consistent arrow styles for same relationships
- Uniform spacing and alignment
- Matching font sizes for similar elements

**Across Figures in a Paper**
- Reuse color schemes
- Maintain consistent node styles
- Use same notation system
- Apply same layout principles

### 3. Professional Appearance

**Alignment**
- Use grids for node placement
- Align nodes horizontally or vertically
- Evenly space elements
- Center labels within shapes

**White Space**
- Don't overcrowd diagrams
- Leave breathing room around elements
- Use white space to group related items
- Margins around entire diagram

**Polish**
- No jagged lines or misaligned elements
- Smooth curves and precise angles
- Clean connection points
- No overlapping text

## Common Pitfalls and Solutions

### Pitfall 1: Overcomplicated Diagrams

**Problem**: Too much information in one diagram
**Solution**: 
- Split into multiple panels (A, B, C)
- Create overview + detailed diagrams
- Move details to supplementary figures
- Use hierarchical presentation

### Pitfall 2: Inconsistent Styling

**Problem**: Different styles for same elements across figures
**Solution**:
- Create and use style templates
- Use the same color palette throughout
- Document your style choices

### Pitfall 3: Poor Label Placement

**Problem**: Labels overlap elements or are hard to read
**Solution**:
- Place labels outside shapes when possible
- Use leader lines for distant labels, terminated in a filled dot at the referent — never an arrowhead. An arrowhead implies movement, so the reader keeps searching for where the line leads instead of treating the label as a stopping point; a dot gives a clean endpoint (see Canonical Arrow Legend)
- Rotate text only when necessary
- Ensure adequate contrast with background

### Pitfall 4: Tiny Text

**Problem**: Text too small to read at final print size
**Solution**:
- Design at final size from the start
- Test print at final size
- Minimum 7-8 pt font
- Simplify labels if space is limited

### Canonical Arrow Legend

**Principle: Every arrow must convey exactly one relationship.** Mixing arrow styles arbitrarily — or using the same style for "leads to," "physically binds," "is required for," and "is hypothesized to influence" — forces readers to guess. Define a legend at the project level and apply it across every panel of every figure in the paper.

A line carries meaning on **four independent channels**: its **path** (solid / dashed / curved), its **terminator** (arrowhead / dot / flat bar), its **stroke width**, and its **profile** (uniform / tapered). Each channel is either declared in the legend or not used at all — an undeclared channel that visibly varies is a defect, not a style choice.

| Symbol | Meaning | Encoding | Optional color |
|---|---|---|---|
| → | Activation / direct positive effect | Solid line, solid arrowhead | Green |
| ⊣ | Inhibition / repression | Solid line, flat bar terminator | Red |
| - - → | Indirect, hypothetical, or context-dependent effect | Dashed line, solid arrowhead | Gray |
| ⇌ | Reversible reaction / equilibrium | Two opposing half-arrows | Neutral |
| ⊳ (open arrowhead) | Catalysis / enzyme action on substrate | Solid line, open arrowhead | Neutral |
| → with label | Reaction or process named on the arrow | Add enzyme / kinase / process name above | Match arrow type |
| —● (dot terminator) | Label leader — points at a referent and asserts no motion | Thin solid line, filled dot at the referent end, no arrowhead | Neutral / text color |
| ↺ (curved return path) | Feedback regulation — a downstream node acting back on an upstream one | Curved line routed clear of the forward path; the terminator carries the sign (arrowhead = positive feedback, flat bar = negative feedback) | Green (positive) / red (negative) |
| → (tapered) | Motion, flow, or directional transport, as distinct from a static relation | Stroke narrows or fades along the path; terminator still set by the relationship | Match arrow type |
| → (thick) vs → (thin) | Ordinal magnitude of one relationship (e.g. dominant vs minor flux) — legend-declared only | Identical path, terminator, and profile; only stroke width varies, monotonically | Match arrow type |

**Rules:**

- **Color is redundant encoding only** — never the sole cue; ~8% of male readers cannot distinguish red from green, so the shape distinction (→ vs ⊣) must carry the meaning unaided
- **The terminator is a declared channel, not a drawing default** — the shape where a line ends means something on its own: an arrowhead asserts motion, direction, or transformation; a filled dot asserts a stationary anchor; a flat bar asserts inhibition. Choose each terminator deliberately and hold its meaning fixed across every panel of every figure
- **Never use an arrow as a label leader** — an arrowhead implies movement, so the reader keeps searching for where it leads instead of treating the label as a stopping point. Terminate every leader line in a filled dot: a dot gives a clean endpoint and claims nothing about direction (see Pitfall 3)
- **Dashed is resolved by figure class** — in mechanism and pathway diagrams, dashed means indirect / hypothetical / context-dependent and nothing else; that is the canonical use. In data plots, dashed as a categorical series identifier stays fully legal, because there it is a color-vision-deficiency redundant-encoding device rather than a claim about mechanism (see Redundant Encoding). Any third use — cut plane, weak signal, cross-attention, "secondary flow," grouping border — must be declared in that figure's own legend and must never co-occur with the canonical mechanism use in the same figure
- **Taper or fade a stroke to say "motion," never to say "how much"** — a line that narrows or fades along its path reads as flow or transport rather than a static relation, and a taper widening toward the reader can read as movement toward the viewer (**PROVISIONAL and UNCALIBRATED** — a culturally-contingent depth cue, not a measured effect). Declare the taper in the legend and keep magnitude off this channel
- **Stroke width is a weak ordinal channel** — Cleveland & McGill rank position and length above area and width, so width supports "more than / less than" comparison across instances of a single relationship and never value-reading off the page. Legal only when the legend declares it, and never a substitute for the number in the caption (see Line Weights and Strokes)
- **Labels belong in the figure caption, not on the arrows** — when arrow density is high, arrow labels add clutter and reduce diagram readability. The single sanctioned exception is the "→ with label" row above: a named reaction, enzyme, or process step where the name *is* the relationship. If a panel needs more than a handful of such names, move them to the caption
- **A diagram must be self-explanatory to a reader who has read the caption** — every channel in use is declared either in an on-figure legend or in the caption, and no channel varies for decorative reasons

### Pitfall 5: Ambiguous Arrows

**Problem**: Unclear what arrows represent, where they point, or whether they are meant to point at all
**Solution**:
- Assign one meaning per arrow style *and* per terminator — arrowhead = motion / direction / transformation, filled dot = stationary label anchor, flat bar = inhibition (see Canonical Arrow Legend)
- Never terminate a label leader in an arrowhead; use a filled dot, so the label reads as an endpoint rather than a destination
- Name relationships in the figure caption rather than on the arrows; label an arrow directly only for a named reaction, enzyme, or process step, where the name *is* the relationship
- Include a legend covering every channel in use — path, terminator, stroke width, taper
- Use anchor points for precise connections, so each arrow visibly starts and ends on its intended node

### Pitfall 6: Color Overuse

**Problem**: Too many colors, confusing or inaccessible
**Solution**:
- Limit to 3-5 colors maximum
- Use color purposefully (categories, emphasis)
- Stick to colorblind-safe palette
- Provide redundant encoding

## Quality Control Checklist

### Before Submission

**Technical Requirements**
- [ ] Correct file format (PDF/EPS preferred for diagrams)
- [ ] Sufficient resolution (vector or 300+ DPI)
- [ ] Appropriate size (matches journal column width)
- [ ] Fonts embedded in PDF
- [ ] No compression artifacts

**Accessibility**
- [ ] Colorblind-safe palette used
- [ ] Works in grayscale (tested)
- [ ] Text minimum 7-8 pt at final size
- [ ] High contrast between elements
- [ ] Redundant encoding (not color alone)

**Design Quality**
- [ ] Elements aligned properly
- [ ] Consistent spacing and layout
- [ ] No overlapping text or elements
- [ ] Clear visual hierarchy
- [ ] Professional appearance

**Content**
- [ ] All elements labeled
- [ ] Abbreviations defined
- [ ] Units included where relevant
- [ ] Legend provided if needed
- [ ] Caption comprehensive

**Consistency**
- [ ] Matches other figures in style
- [ ] Same notation as text
- [ ] Consistent with journal guidelines
- [ ] Cross-references work

## Journal-Specific Guidelines

### Nature

**Figure Requirements**
- **Size**: 89 mm (single) or 183 mm (double column)
- **Format**: PDF, EPS, or high-res TIFF
- **Fonts**: Sans-serif preferred
- **File size**: <10 MB per file
- **Resolution**: 300 DPI minimum for raster

**Style Notes**
- Panel labels: lowercase bold (a, b, c)
- Simple, clean design
- Minimal colors
- Clear captions

### Science

**Figure Requirements**
- **Size**: 55 mm (single) or 120 mm (double column)
- **Format**: PDF, EPS, TIFF, or JPEG (high quality)
- **Resolution**: 300 DPI for photos, 600 DPI for line art
- **File size**: <10 MB
- **Fonts**: 6-7 pt minimum

**Style Notes**
- Panel labels: capital bold (A, B, C)
- High contrast
- Readable at small size

### Cell

**Figure Requirements**
- **Size**: 85 mm (single) or 178 mm (double column)
- **Format**: PDF preferred, TIFF, EPS acceptable
- **Resolution**: 300 DPI minimum
- **Fonts**: 8-10 pt for labels
- **Line weight**: 0.5 pt minimum

**Style Notes**
- Clean, professional
- Color or grayscale
- Panel labels capital (A, B, C)

### IEEE

**Figure Requirements**
- **Size**: 3.5 in (single) or 7.16 in (double column)
- **Format**: PDF, EPS (vector preferred)
- **Resolution**: 600 DPI for line art, 300 DPI for halftone
- **Fonts**: 8-10 pt minimum
- **Color**: Grayscale in print, color in digital

**Style Notes**
- Follow IEEE Graphics Manual
- Standard symbols for circuits
- Technical precision
- Clear axis labels

## Software-Specific Export Settings

### AI-Generated Images

AI-generated diagrams are exported as PNG images and can be included in LaTeX documents using:

```latex
\includegraphics[width=\textwidth]{diagram.png}
```

### Python (Matplotlib) Export

```python
import matplotlib.pyplot as plt

# Set publication quality
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 8
plt.rcParams['pdf.fonttype'] = 42  # TrueType fonts in PDF

# Save with proper DPI and cropping
fig.savefig('diagram.pdf', dpi=300, bbox_inches='tight', 
            pad_inches=0.1, transparent=False)
fig.savefig('diagram.png', dpi=300, bbox_inches='tight')
```

### Schemdraw Export

```python
import schemdraw

d = schemdraw.Drawing()
# ... build circuit ...

# Export
d.save('circuit.svg')  # Vector
d.save('circuit.pdf')  # Vector
d.save('circuit.png', dpi=300)  # Raster
```

### Inkscape Command Line

```bash
# PDF to high-res PNG
inkscape diagram.pdf --export-png=diagram.png --export-dpi=300

# SVG to PDF
inkscape diagram.svg --export-pdf=diagram.pdf
```

## Version Control Best Practices

**Keep Source Files**
- Save original .tex, .py, or .svg files
- Use descriptive filenames with versions
- Document color palette and style choices
- Include README with regeneration instructions

**Directory Structure**
```
figures/
├── source/          # Editable source files
│   ├── diagram1.tex
│   ├── circuit.py
│   └── pathway.svg
├── generated/       # Auto-generated outputs
│   ├── diagram1.pdf
│   ├── circuit.pdf
│   └── pathway.pdf
└── final/          # Final submission versions
    ├── figure1.pdf
    └── figure2.pdf
```

**Git Tracking**
- Track source files (.tex, .py)
- Consider .gitignore for generated PDFs (large files)
- Use releases/tags for submission versions
- Document generation process in README

## Testing and Validation

### Pre-Submission Tests

**Visual Tests**
1. **Print test**: Print at final size, check readability
2. **Grayscale test**: Convert to grayscale, verify interpretability
3. **Zoom test**: View at 400% and 25% to check scalability
4. **Screen test**: View on different devices (phone, tablet, desktop)

**Technical Tests**
1. **Font embedding**: Check PDF properties
2. **Resolution check**: Verify DPI meets requirements
3. **File size**: Ensure under journal limits
4. **Format compliance**: Verify accepted format

**Accessibility Tests**
1. **Colorblind simulation**: Use tools like Color Oracle
2. **Contrast checker**: WCAG contrast ratio tools
3. **Screen reader**: Test alt text (for web figures)

### Tools for Testing

**Colorblind Simulation**
- Color Oracle (free, cross-platform)
- Coblis (Color Blindness Simulator)
- Photoshop/GIMP colorblind preview modes

**PDF Inspection**
```bash
# Check PDF properties
pdfinfo diagram.pdf

# Check fonts
pdffonts diagram.pdf

# Check image resolution
identify -verbose diagram.pdf
```

**Contrast Checking**
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Colorable: https://colorable.jxnblk.com/

## Summary: Golden Rules

1. **Vector first**: Always use vector formats when possible
2. **Design at final size**: Avoid scaling after creation
3. **Colorblind-safe palette**: Use Okabe-Ito or similar
4. **Test in grayscale**: Diagrams must work without color
5. **Minimum 7-8 pt text**: At final print size
6. **Consistent styling**: Across all figures in paper
7. **Keep it simple**: Remove unnecessary elements
8. **High contrast**: Ensure readability
9. **Align elements**: Professional appearance matters
10. **Comprehensive caption**: Explain everything

## Further Resources

- **Nature Figure Preparation**: https://www.nature.com/nature/for-authors/final-submission
- **Science Figure Guidelines**: https://www.science.org/content/page/instructions-preparing-initial-manuscript
- **WCAG Accessibility Standards**: https://www.w3.org/WAI/WCAG21/quickref/
- **Color Universal Design (CUD)**: https://jfly.uni-koeln.de/color/
- **ColorBrewer**: https://colorbrewer2.org/

Following these best practices ensures your diagrams meet publication standards and effectively communicate to all readers, regardless of colorblindness or viewing conditions.

