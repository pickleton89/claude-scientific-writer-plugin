# PowerPoint Poster Workflows

## Overview

This guide covers PowerPoint-specific workflows, templates, and best practices for creating research posters. PowerPoint offers rapid iteration, easy collaboration, and accessibility for users without LaTeX experience.

## When to Choose PowerPoint

**Ideal Scenarios:**
- Tight deadlines (<48 hours to presentation)
- Collaborators need to edit the poster
- Conference provides PPTX template
- Extensive image manipulation required
- No complex mathematical equations
- User unfamiliar with LaTeX

**Avoid PowerPoint When:**
- Poster contains >5 complex equations
- Version control/reproducibility is critical
- Programmatic poster generation needed
- Conference requires LaTeX submission

## Software Requirements

**Recommended:**
- Microsoft PowerPoint 2016+ (best compatibility)
- LibreOffice Impress 7.0+ (free alternative)

**No additional dependencies required** - uses native PowerPoint functionality.

## Poster Size Setup

### Setting Custom Dimensions

1. **File → Page Setup → Custom Size**
2. Enter exact dimensions in inches
3. Set orientation (Portrait/Landscape)
4. Click OK

**Important:** Always set dimensions at project start. Scaling later causes quality loss.

### Common Poster Sizes

| Conference Requirement | PPTX Dimensions | Aspect Ratio |
|-----------------------|-----------------|--------------|
| A0 Portrait | 33.11" × 46.81" | 1:1.41 |
| A0 Landscape | 46.81" × 33.11" | 1.41:1 |
| A1 Portrait | 23.39" × 33.11" | 1:1.41 |
| 36×48" Portrait | 36" × 48" | 3:4 |
| 48×36" Landscape | 48" × 36" | 4:3 |
| 42×56" Portrait | 42" × 56" | 3:4 |
| 48×72" Landscape | 48" × 72" | 2:3 |

## Layout Templates

### Template 1: 3-Column A0 Portrait

**Dimensions:** 33.11" × 46.81" (841 × 1189 mm)

```
┌─────────────────────────────────────┐
│ [LOGO]     TITLE (72-120pt)  [LOGO] │
│        Authors (48-60pt)            │
│     Affiliations (36-48pt)          │
├───────────┬───────────┬─────────────┤
│           │           │             │
│ INTRO     │ RESULTS-1 │ RESULTS-3   │
│ ~100w     │           │             │
│           │ [FIGURE]  │ [FIGURE]    │
│           │           │             │
├───────────┤           ├─────────────┤
│           │           │             │
│ METHODS   │ RESULTS-2 │ CONCLUSIONS │
│ ~150w     │           │ ~100w       │
│           │ [FIGURE]  │             │
│ [DIAGRAM] │           │ REFERENCES  │
│           │           │ (5-10)      │
├───────────┴───────────┴─────────────┤
│  Contact: email@example.com  [QR]   │
│        Acknowledgments              │
└─────────────────────────────────────┘
```

**Spacing:**
- Margins: 0.75" all sides
- Column gap: 0.5"
- Row gap: 0.4"

**Best For:** Experimental studies, methods-heavy research

---

### Template 2: 48×36" Landscape

**Dimensions:** 48" × 36" (1219 × 914 mm)

```
┌─────────────────────────────────────────────────────┐
│ [LOGO]  TITLE / AUTHORS / AFFILIATIONS       [LOGO] │
├────────────┬────────────┬────────────┬──────────────┤
│            │            │            │              │
│  INTRO     │  METHODS   │  RESULTS   │  CONCLUSIONS │
│            │            │            │              │
│            │ [DIAGRAM]  │ [FIGURES]  │  [QR CODE]   │
│            │            │            │              │
├────────────┴────────────┴────────────┴──────────────┤
│              REFERENCES / CONTACT / ACKNOWLEDGMENTS  │
└─────────────────────────────────────────────────────┘
```

**Spacing:**
- Margins: 0.75" all sides
- Column gap: 0.4"
- Header: 12% of height
- Footer: 8% of height

**Best For:** Results-heavy research, landscape-oriented venues

---

### Template 3: 36×48" Portrait (US Standard)

**Dimensions:** 36" × 48" (914 × 1219 mm)

```
┌───────────────────────────────┐
│ [LOGO]     TITLE       [LOGO] │  10%
│      Authors / Affil          │
├───────────────────────────────┤
│                               │
│     INTRODUCTION              │  15%
│     Background context        │
│                               │
├───────────┬───────────────────┤
│           │                   │
│ METHODS   │     RESULTS       │  50%
│           │                   │
│ [DIAGRAM] │ [MAIN FIGURES]    │
│           │                   │
├───────────┴───────────────────┤
│                               │
│     CONCLUSIONS               │  15%
│     Key takeaways             │
│                               │
├───────────────────────────────┤
│ REFS | CONTACT | [QR]         │  10%
└───────────────────────────────┘
```

**Best For:** US conferences, case studies

---

### Template 4: 2-Column Review/Survey

**Dimensions:** A0 Portrait (33.11" × 46.81")

```
┌─────────────────────────────────────┐
│ [LOGO]        TITLE          [LOGO] │
│         Authors / Affiliations      │
├──────────────────┬──────────────────┤
│                  │                  │
│   THEME 1        │   THEME 3        │
│                  │                  │
│   [CONTENT]      │   [CONTENT]      │
│                  │                  │
├──────────────────┼──────────────────┤
│                  │                  │
│   THEME 2        │   THEME 4        │
│                  │                  │
│   [CONTENT]      │   [CONTENT]      │
│                  │                  │
├──────────────────┴──────────────────┤
│   SYNTHESIS / CONCLUSIONS           │
├─────────────────────────────────────┤
│   REFERENCES | CONTACT | [QR]       │
└─────────────────────────────────────┘
```

**Best For:** Literature reviews, survey papers, thematic content

## Typography Specifications

| Element | Font Size | Font Weight | Color |
|---------|-----------|-------------|-------|
| Title | 72-120pt | Bold | Primary |
| Authors | 48-60pt | Regular | Dark gray |
| Section headers | 48-60pt | Bold | Primary |
| Body text | 28-36pt | Regular | Black |
| Figure captions | 24-30pt | Regular | Dark gray |
| References | 18-24pt | Regular | Gray |

**Font Recommendations:**
- Sans-serif fonts: Calibri, Arial, Helvetica, Open Sans
- Maximum 2 font families
- Avoid decorative or script fonts

## Grid and Alignment

### Setting Up Guides

1. **View → Guides** to enable
2. Drag guides from rulers to create grid
3. Use **Snap to Grid** for precise alignment

### Standard Grid Specifications (3-Column A0)

```
Margin guides:     0.5-1.0" from edges
Column guides:     3 equal columns with 0.3-0.5" gaps
Row guides:        Header (12-15%), Content (75-80%), Footer (5-10%)
```

## Color Scheme Guidelines

**Maximum 3-4 Colors:**
- Primary: Headers, key elements
- Secondary: Subheaders, accents
- Neutral: Body text (dark gray/black)
- Background: White or very light tint

**Contrast Requirements:**
- Body text / background: minimum 4.5:1 ratio
- Title / background: minimum 3:1 ratio
- Test at: https://webaim.org/resources/contrastchecker/

## Image Requirements

**Resolution:**
- Minimum 300 DPI at final print size
- For 10" wide figure on A0: 3000+ pixels wide
- Prefer vector graphics (SVG, EMF) when available

**File Formats:**
- PNG: Photos with transparency
- JPEG: Photos without transparency
- SVG/EMF: Diagrams, charts, logos

**Quality Check:**
- Zoom to 100% in PowerPoint
- Any pixelation = insufficient resolution

## Export Settings

### Print-Ready PDF

```
File → Export → PDF
Options:
- High quality
- Embed fonts
- PDF/A if required by print service
```

### Export Checklist

| Output | Format | Quality | Use Case |
|--------|--------|---------|----------|
| Print | PDF | High quality, embedded fonts | Professional printing |
| Email | PDF | Compressed | Quick sharing |
| Social | PNG | 150 DPI, 1920px width | Twitter, LinkedIn |
| Archive | PPTX | Native | Future editing |

### File Size Guidelines

- <100MB: Email-safe
- <500MB: Most print services
- >500MB: May need compression

## Common Pitfalls

### 1. Wrong Dimensions
- **Problem:** Creating at screen dimensions then scaling
- **Solution:** Set exact poster size before adding content

### 2. Low-Resolution Images
- **Problem:** Web images (72-150 DPI) pixelated at print
- **Solution:** All images ≥300 DPI at final size

### 3. Inconsistent Styling
- **Problem:** Multiple fonts, random colors, misaligned elements
- **Solution:** Define style upfront, use Align tools

### 4. Missing Contact Info
- **Problem:** No way for viewers to follow up
- **Solution:** Email + QR code (minimum 2×2 inches)

### 5. Text Overload
- **Problem:** 1500+ words, dense paragraphs
- **Solution:** Maximum 800 words, bullet points, 40-50% figures

## Validation Checklist

**Before Export:**
- [ ] Dimensions match conference requirements
- [ ] All text ≥24pt (body), ≥72pt (title)
- [ ] All images ≥300 DPI (no pixelation at 100% zoom)
- [ ] Color contrast ≥4.5:1
- [ ] Spell-check completed
- [ ] QR codes tested and functional
- [ ] Contact information visible

**Print Test:**
- [ ] Print at 25% scale on letter paper
- [ ] Title readable from arm's length
- [ ] Sections clearly visible
- [ ] No text cutoff or overlap
