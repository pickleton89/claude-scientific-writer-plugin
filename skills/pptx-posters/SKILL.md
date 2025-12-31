---
name: pptx-posters
version: 2.2.0
extends: visual-design
description: "Create professional research posters in PowerPoint/PPTX format with structured layouts, brand-compliant styling, and print-ready export. Optimized for quick turnaround and collaborative editing."
when_to_use: "Conference posters with tight deadlines (<48h), collaborative PowerPoint editing, PPTX templates provided, extensive image manipulation needed"
allowed-tools: [Read, Write, Edit, Bash, Glob]
---

# PowerPoint Research Posters

> **Design Foundation**: This skill extends [`visual-design`](../visual-design/SKILL.md) for typography, color, composition, and accessibility standards.

<overview>
Create publication-quality research posters using Microsoft PowerPoint or compatible applications. This skill provides structured workflows for poster design, layout optimization, and print-ready export. Optimized for rapid iteration, collaborative editing, and scenarios where LaTeX is impractical.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Creating posters for conferences with tight deadlines (<48 hours)
- Collaborators require editable PowerPoint format
- Design requires extensive image manipulation or custom graphics
- User explicitly requests PPTX format
- Institution provides PowerPoint templates as standard

Do NOT use this skill when:
- Poster contains complex mathematical equations → use `latex-posters`
- Reproducibility/version control is critical → use `latex-posters`
- Poster requires programmatic generation → use `latex-posters`
- User explicitly requests LaTeX format
</when_to_use>

<decision_framework>
## Format Selection Matrix

```
Need research poster?
│
├─ Complex equations (>5)?
│  │
│  ├─ Yes → latex-posters
│  │
│  └─ No → Continue below
│
├─ Timeline?
│  │
│  ├─ <48 hours → pptx-posters (faster iteration)
│  │
│  └─ >48 hours → Either format works
│
├─ Collaboration requirement?
│  │
│  ├─ Co-authors need to edit → pptx-posters
│  │
│  └─ Single author → Either format works
│
├─ Template provided?
│  │
│  ├─ PPTX template → pptx-posters
│  │
│  ├─ LaTeX template → latex-posters
│  │
│  └─ No template → Use decision factors above
│
└─ Default: pptx-posters (lower barrier to entry)
```

## Size Selection Matrix

| Conference Requirement | PPTX Dimensions | Aspect Ratio |
|-----------------------|-----------------|--------------|
| A0 Portrait (841×1189mm) | 33.11" × 46.81" | 1:1.41 |
| A0 Landscape | 46.81" × 33.11" | 1.41:1 |
| A1 Portrait (594×841mm) | 23.39" × 33.11" | 1:1.41 |
| 36×48" Portrait | 36" × 48" | 3:4 |
| 48×36" Landscape | 48" × 36" | 4:3 |
| 42×56" Portrait | 42" × 56" | 3:4 |
| 48×72" Landscape | 48" × 72" | 2:3 |

## Layout Selection Matrix

| Content Type | Recommended Layout | Columns |
|-------------|-------------------|---------|
| Experimental study | Flow layout | 3-4 |
| Methods-heavy | Step-by-step | 3 |
| Results-heavy | Gallery layout | 3-4 |
| Review/survey | Thematic blocks | 2-3 |
| Case study | Narrative flow | 2 |

</decision_framework>

<prerequisites>
## Prerequisites

**Software Required:**
- Microsoft PowerPoint 2016+ OR LibreOffice Impress 7.0+
- PDF export capability (built into PowerPoint/Impress)

**No Python dependencies required** - this skill uses native PowerPoint functionality.

**Before Starting:**
1. Confirm conference poster requirements (dimensions, format)
2. Collect institutional logos (≥300 DPI, PNG/SVG preferred)
3. Prepare figures at publication quality (≥300 DPI at print size)
</prerequisites>

<workflow>
## Workflow

### Stage 1: Requirements Gathering

**Objective:** Establish poster specifications and constraints

**Steps:**
1. Confirm poster dimensions from conference requirements
2. Identify orientation (portrait/landscape)
3. Determine print deadline and submission format
4. Collect institutional logos (minimum 300 DPI)
5. Confirm color scheme (brand colors or custom)

**Exit Criteria:**
- [ ] Exact dimensions documented (width × height in inches)
- [ ] All logos collected (≥300 DPI, PNG/SVG preferred)
- [ ] Color palette defined (primary, secondary, accent colors)
- [ ] Deadline confirmed (print date minus 2 days buffer)

---

### Stage 2: Content Preparation

**Objective:** Prepare and organize all poster content

**Steps:**
1. Draft title (≤15 words, impactful)
2. List authors and affiliations
3. Write section content:
   - Introduction: 50-100 words
   - Methods: 75-150 words
   - Results: 100-200 words (figures carry the message)
   - Conclusions: 50-100 words (3-5 bullet points)
4. Prepare figures (minimum 300 DPI at final print size)
5. Compile references (5-10 key citations)

**Content Budget:**

| Section | Word Limit | Visual Elements |
|---------|-----------|-----------------|
| Title | 15 words max | Logo placement |
| Introduction | 100 words | 0-1 figure |
| Methods | 150 words | 1-2 diagrams |
| Results | 200 words | 2-4 figures (primary) |
| Conclusions | 100 words | QR code optional |
| Total | 500-800 words | 3-6 figures |

**Exit Criteria:**
- [ ] Total word count: 500-800 words
- [ ] All figures prepared at ≥300 DPI
- [ ] Figure-to-text ratio: ≥40% figures
- [ ] All content fits within section budgets

---

### Stage 3: Layout Construction

**Objective:** Build poster structure in PowerPoint

**Steps:**
1. Create new presentation with exact dimensions:
   ```
   File → Page Setup → Custom Size → [width] × [height]
   ```
2. Set up grid guides:
   - Margin: 0.5-1.0 inches all sides
   - Column spacing: 0.3-0.5 inches
   - Row guides for header (12-15% height)
3. Create master slide with:
   - Header band with title area
   - Logo placeholders (corners)
   - Footer band for contact info
4. Add content placeholders by section

**Grid Specifications (3-Column A0 Portrait):**

```
┌────────────────────────────────────────────┐
│  LOGO    TITLE / AUTHORS / AFFILIATIONS  LOGO  │ 12%
├────────────┬────────────┬────────────┤
│            │            │            │
│ INTRO      │ RESULTS    │ RESULTS    │
│            │ (cont.)    │ (cont.)    │
│            │            │            │
│            ├────────────┤            │
│ METHODS    │            │ CONCLUSIONS│
│            │ RESULTS    │            │
│            │ (main)     │ REFS       │
│            │            │            │
├────────────┴────────────┴────────────┤
│     CONTACT / QR CODE / ACKNOWLEDGMENTS     │ 5%
└────────────────────────────────────────────┘
```

**Exit Criteria:**
- [ ] Dimensions match requirements exactly
- [ ] Grid guides visible and aligned
- [ ] Header occupies 10-15% of height
- [ ] Margins consistent (≥0.5 inches)
- [ ] Column widths equal (±0.1 inch tolerance)

---

### Stage 4: Content Population

**Objective:** Add content following visual hierarchy

**Steps:**
1. Add title and author block:
   - Title: 72-120pt bold sans-serif
   - Authors: 48-60pt
   - Affiliations: 36-48pt
2. Add section headers: 48-60pt bold
3. Add body text: 28-36pt regular
4. Insert figures with captions
5. Add references in smaller font (18-24pt)
6. Place QR code linking to paper/data (minimum 2×2 inches)

**Typography Specifications:**

| Element | Font Size | Font Weight | Color |
|---------|-----------|-------------|-------|
| Title | 72-120pt | Bold | Primary |
| Authors | 48-60pt | Regular | Dark gray |
| Section headers | 48-60pt | Bold | Primary |
| Body text | 28-36pt | Regular | Black |
| Figure captions | 24-30pt | Regular | Dark gray |
| References | 18-24pt | Regular | Gray |

**Exit Criteria:**
- [ ] Title readable from 15+ feet
- [ ] Body text readable from 4-6 feet
- [ ] All figures have captions
- [ ] Font sizes within specified ranges
- [ ] Consistent styling throughout

---

### Stage 5: Visual Refinement

**Objective:** Polish design for maximum impact

**Steps:**
1. Apply consistent color scheme:
   - Maximum 3-4 colors (primary, secondary, accent, neutral)
   - Background: white or very light shade
   - Text: dark (≥4.5:1 contrast ratio)
2. Align all elements to grid
3. Add visual interest:
   - Section dividers or colored bars
   - Icon accents (minimal)
   - Drop shadows (subtle, if any)
4. Verify white space distribution (20-30% of poster area)
5. Add accessibility features:
   - Alt text for figures
   - Color-blind safe palette
   - High contrast text

**Color Contrast Requirements:**

| Element Pair | Minimum Ratio | Target Ratio |
|-------------|---------------|--------------|
| Body text / background | 4.5:1 | 7:1 |
| Title / background | 3:1 | 4.5:1 |
| Data in figures | 3:1 | 4.5:1 |

**Exit Criteria:**
- [ ] Maximum 4 colors used
- [ ] All text meets contrast requirements
- [ ] Elements aligned to grid (use Align tools)
- [ ] White space: 20-30% of total area
- [ ] No orphaned elements (single words on lines)

---

### Stage 6: Quality Validation

**Objective:** Ensure poster meets print and presentation standards

**Steps:**
1. Zoom to 100% and check:
   - Text readability
   - Image quality (no pixelation)
   - Color rendering
2. Print test page at 25% scale (A4/Letter):
   - Title readable from arm's length
   - Sections clearly delineated
   - Figures visible and clear
3. Spell-check entire document
4. Verify all author names and affiliations
5. Check figure numbering and references
6. Test QR codes

**Validation Checklist:**

- [ ] No spelling/grammar errors (run spell-check)
- [ ] All names spelled correctly
- [ ] All figures ≥300 DPI (no pixelation at 100% zoom)
- [ ] Contact information visible
- [ ] QR code tested and functional
- [ ] File size reasonable (<100MB for email, <500MB for print)

**Exit Criteria:**
- [ ] 100% zoom visual inspection passed
- [ ] 25% scale print test completed
- [ ] All checklist items verified
- [ ] No LaTeX compilation needed (ready for print)

---

### Stage 7: Export and Delivery

**Objective:** Generate print-ready files

**Steps:**
1. Save native PPTX file (backup and collaboration)
2. Export PDF for printing:
   ```
   File → Export → PDF
   Options: High quality, embed fonts, PDF/A if required
   ```
3. Verify PDF dimensions match requirements
4. Check PDF file size:
   - <100MB: Email-safe
   - <500MB: Most print services
   - >500MB: May need compression
5. Prepare supplementary formats:
   - PNG for social media (1920px width)
   - JPEG for email preview

**Export Settings:**

| Output | Format | Quality | Use Case |
|--------|--------|---------|----------|
| Print | PDF | High quality, embedded fonts | Professional printing |
| Email | PDF | Compressed | Quick sharing |
| Social | PNG | 150 DPI, 1920px width | Twitter, LinkedIn |
| Archive | PPTX | Native | Future editing |

**Exit Criteria:**
- [ ] PPTX saved as backup
- [ ] PDF dimensions verified (match requirements)
- [ ] PDF fonts embedded
- [ ] File size appropriate for delivery method
- [ ] Print service requirements confirmed

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Total words | 400 | 600 | 500 |
| Figure count | 3 | 5 | 4-6 |
| Figure area | 35% | 45% | 50% |
| White space | 15% | 25% | 20-30% |
| Font size (body) | 24pt | 30pt | 28-36pt |
| Image resolution | 200 DPI | 300 DPI | 300+ DPI |
| Color count | 2 | 3-4 | 3 |
| Contrast ratio | 4.5:1 | 7:1 | 7:1+ |

**Completion Checklist:**
- [ ] Dimensions match conference requirements exactly
- [ ] Word count within 500-800 word budget
- [ ] Figures occupy ≥40% of poster area
- [ ] All text meets contrast requirements (≥4.5:1)
- [ ] PDF exports without errors
- [ ] 25% scale print test completed
- [ ] All QR codes functional
- [ ] File deliverable to print service

</success_criteria>

<scope>
## Scope

**In Scope:**
- PowerPoint poster creation and design
- Layout optimization for standard sizes (A0, A1, 36×48", etc.)
- Print-ready PDF export
- Accessibility optimization
- Brand-compliant color schemes
- Quick-turnaround poster production

**Out of Scope** (use specialized resources):
- Complex mathematical typesetting → use `latex-posters`
- Programmatic poster generation → use `latex-posters`
- Version-controlled reproducible posters → use `latex-posters`
- AI-generated figures → use `scientific-schematics`
- Data visualization → use `plotting-libraries`

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Text Overload

**Anti-pattern:**
```
Poster with 1500+ words, dense paragraphs,
minimal figures. Viewers can't process content
in typical 2-3 minute interaction.
```

**Solution:**
```
Maximum 800 words. Use bullet points.
Let figures carry the message. Target
40-50% visual content. Less text = more impact.
```

---

### 2. Wrong Dimensions

**Anti-pattern:**
```
Creating poster at screen dimensions (16:9)
then scaling up. Results in blurry text
and pixelated images at print size.
```

**Solution:**
```
Set exact dimensions from the start:
File → Page Setup → Custom Size → [exact inches]
A0 Portrait: 33.11" × 46.81"
```

---

### 3. Low-Resolution Images

**Anti-pattern:**
```
Using web images or screenshots (72-150 DPI).
Look fine on screen but pixelated when printed
at poster size.
```

**Solution:**
```
All images must be ≥300 DPI at final print size.
For a 10" wide figure on A0: 3000+ pixels wide.
Use vector graphics (SVG, EMF) when possible.
```

---

### 4. Inconsistent Styling

**Anti-pattern:**
```
Multiple fonts (5+), inconsistent colors,
varying text sizes across similar elements,
misaligned boxes. Looks unprofessional.
```

**Solution:**
```
Use 1-2 font families maximum.
Define color palette upfront (3-4 colors).
Create consistent section templates.
Use PowerPoint's Align tools religiously.
```

---

### 5. Missing Contact Information

**Anti-pattern:**
```
No email, no QR code, no way for interested
viewers to follow up after the session.
Missed networking opportunities.
```

**Solution:**
```
Include: Email address (large, readable)
QR code to paper/data (minimum 2×2 inches)
Twitter/LinkedIn handle if appropriate
```

---

### 6. Poor Color Contrast

**Anti-pattern:**
```
Light gray text on white background.
Yellow text on light background.
Fails accessibility standards.
```

**Solution:**
```
Minimum 4.5:1 contrast ratio for body text.
Use WebAIM contrast checker.
Dark text on light backgrounds (or vice versa).
Test with grayscale preview.
```

</anti_patterns>

<templates>
## Output Templates

See `{baseDir}/references/poster_templates.md` for complete layout templates including:
- 3-Column A0 Portrait (experimental studies)
- 48×36" Landscape (results-heavy)
- 36×48" Portrait (US standard)
- 2-Column Review/Survey layout
- Size quick reference table

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `oligon-brand` | Brand colors and tokens—use `pptx_adapter.py` for Oligon-styled posters |
| `latex-posters` | Alternative for complex equations, reproducible posters |
| `scientific-schematics` | Use to generate AI-powered figures for poster |
| `visual-design` | Reference for design principles and color theory |
| `plotting-libraries` | Use to create publication-quality data visualizations |
| `scientific-writing` | Source content from papers for poster adaptation |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/references/poster_design_principles.md` | Typography, color, visual hierarchy |
| `{baseDir}/references/poster_content_guide.md` | Content strategy and word budgets |
| `{baseDir}/references/poster_layout_design.md` | Grid systems and layout patterns |
| `{baseDir}/references/poster_templates.md` | Ready-to-use layout templates |
| `{baseDir}/assets/poster_quality_checklist.md` | Pre-print validation checklist |

</references>
