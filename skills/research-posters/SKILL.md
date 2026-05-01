---
name: research-posters
version: 1.0.1
extends: visual-design
description: "Design research posters from scratch in LaTeX or PowerPoint with custom layout, brand-compliant styling, and print-ready export. Use when the user wants to create a poster manually. Do NOT use when auto-generating a poster from an existing paper PDF — use paper-2-web (Paper2Poster)."
when_to_use: "Conference posters, academic poster sessions, thesis defense posters, research symposia — designed from scratch, not converted from an existing paper"
allowed-tools: [Read, Write, Edit, Bash, Glob]
---

# Research Posters

> **Design Foundation**: This skill extends [`visual-design`](../visual-design/SKILL.md) for typography, color, composition, and accessibility standards. Cognitive-foundation citations (Cleveland-McGill 1984, Wagemans 2012 Gestalt grouping for direct labelling on posters, Crameri 2020, Fujii 2026 communication context) and cross-skill quality gates also live in [`oligon-brand`](../oligon-brand/SKILL.md) `<design_foundation>` and [`shared/references/`](../shared/references/) (`pre_submission_checklist.md`, `communication_context_matrix.md`, `figure_vs_table_decision.md`).

<overview>
Create publication-quality research posters in either LaTeX (beamerposter, tikzposter, baposter) or PowerPoint format. This skill provides unified workflows for poster design with format-specific implementation paths. Posters are primarily visual media—text-heavy posters fail to communicate effectively.

**Core Requirement**: Every poster MUST include 2-3 AI-generated figures using `scientific-schematics`. Target 40-50% visual content, 300-800 words maximum.
</overview>

<brand_application>
## Brand Application (Default)

**By default, all research posters use Oligon Scientific Brand styling.** This ensures consistent, professional appearance.

### Auto-Applied Settings

When creating posters, apply the following brand defaults:

| Element | Color | Usage |
|---------|-------|-------|
| Primary accent | `#2DB2E8` (Brand Blue) | Section headers, key highlights |
| Secondary accent | `#E8622D` (Orange) | Alerts, call-to-action elements |
| Primary text | `#222222` (Dark Gray) | Body text, titles |
| Secondary text | `#666666` (Medium Gray) | Captions, secondary info |
| Background | `#FFFFFF` (White) | Poster background |

**LaTeX color definitions:**
```latex
\definecolor{brandblue}{HTML}{2DB2E8}
\definecolor{brandorange}{HTML}{E8622D}
\definecolor{darkgray}{HTML}{222222}
\definecolor{mediumgray}{HTML}{666666}
```

**PowerPoint theme colors:**
- Accent 1: `#2DB2E8` (Brand Blue)
- Accent 2: `#E8622D` (Orange)
- Text 1: `#222222` (Dark Gray)
- Background: `#FFFFFF` (White)

### Disabling Brand Styling

To use generic/conference-specific styling instead of Oligon brand:

**Explicit request in prompt:**
- "Use conference template colors"
- "No brand styling" or "Generic color scheme"

**Per-project override:** Add to project `CLAUDE.md`:
```markdown
## Visual Styling
Use generic/default styling for all visual outputs. Do not apply Oligon brand.
```

</brand_application>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Creating research posters for conferences, symposia, or poster sessions
- Designing academic posters for university events or thesis defenses
- Preparing visual summaries of research for public engagement
- Converting scientific papers into poster format
- Building posters with multi-column layouts

Do NOT use this skill when:
- Making slide presentations → use `scientific-slides`
- Writing papers → use `scientific-writing`
- Auto-generating poster from paper → use `paper-2-web` (Paper2Poster)
</when_to_use>

<decision_framework>
## Format Selection

```
Creating a research poster?
│
├─ Complex equations (>5)?
│  └─ YES → LaTeX format
│
├─ Need version control / reproducibility?
│  └─ YES → LaTeX format
│
├─ Timeline < 48 hours?
│  └─ YES → PowerPoint format (faster iteration)
│
├─ Collaborators need to edit?
│  └─ YES → PowerPoint format
│
├─ Template provided by conference?
│  ├─ .tex template → LaTeX format
│  ├─ .pptx template → PowerPoint format
│  └─ No template → Use decision factors above
│
├─ Familiar with LaTeX?
│  ├─ YES → Either format works
│  └─ NO → PowerPoint format (lower barrier)
│
└─ Default: PowerPoint format
```

## Format Comparison

| Criterion | LaTeX | PowerPoint |
|-----------|-------|------------|
| Complex equations | Excellent | Difficult |
| Precise typography | Better control | Limited |
| Quick iteration | Slower | Faster |
| Collaboration | Requires LaTeX | Easy sharing |
| Version control | Git-friendly | Binary format |
| Learning curve | Steeper | Familiar |
| Compilation | Required | None |

## LaTeX Package Selection

When using LaTeX format, choose a package:

| Factor | beamerposter | tikzposter | baposter |
|--------|--------------|------------|----------|
| **Best for** | Beamer users, institutional themes | Modern colorful designs | Multi-column, consistent spacing |
| **Learning curve** | Low (if know Beamer) | Medium | Medium |
| **Customization** | Theme-based | TikZ commands | Box-based |
| **Default look** | Traditional academic | Modern, colorful | Professional blocks |

```
Which LaTeX package?
│
├─ Already know Beamer or have Beamer theme?
│   └─ YES → beamerposter
│       Template: {baseDir}/assets/beamerposter_template.tex
│
├─ Want modern, colorful, highly customizable?
│   └─ YES → tikzposter
│       Template: {baseDir}/assets/tikzposter_template.tex
│
└─ Need structured multi-column with automatic spacing?
    └─ YES → baposter
        Template: {baseDir}/assets/baposter_template.tex
```

## Poster Size Selection

| Standard | Dimensions | Common Use |
|----------|------------|------------|
| A0 | 841 × 1189 mm (33.1 × 46.8") | European conferences (most common) |
| A1 | 594 × 841 mm (23.4 × 33.1") | Smaller venues, local events |
| 36 × 48" | 914 × 1219 mm | US conferences (common) |
| 42 × 56" | 1067 × 1422 mm | Large format US |
| 48 × 72" | 1219 × 1829 mm | Extra large |

**Orientation Decision:**
- Portrait (vertical): Traditional, most common, fits standard easels
- Landscape (horizontal): Wide content, timelines, process flows

</decision_framework>

<workflow>
## Unified Workflow

### Stage 1: Requirements & Planning (Both Formats)

**Objective:** Define poster specifications and content outline

**Steps:**
1. Determine poster requirements:
   - Size (A0, 36×48", etc.) from conference guidelines
   - Orientation (portrait/landscape)
   - Submission deadline and format requirements

2. Develop content outline:
   - Identify 1-3 core messages
   - Select 3-6 key figures (40-50% of poster area)
   - Draft bullet points for each section
   - Target 300-800 words total

3. Collect materials:
   - Institutional logos (≥300 DPI, PNG/SVG preferred)
   - Figures at publication quality (≥300 DPI at print size)
   - Color palette (brand colors or custom)

**Exit Criteria:**
- [ ] Poster size confirmed from conference requirements
- [ ] Orientation decided (portrait/landscape)
- [ ] 1-3 core messages identified
- [ ] Figure list created (3-6 figures)
- [ ] Word count target set (300-800 words)
- [ ] All logos collected (≥300 DPI)

---

### Stage 2: Format Selection

**Objective:** Choose implementation format based on requirements

**Ask user:** "Which format would you like for your poster?"

1. **LaTeX** - beamerposter, tikzposter, or baposter
   - Best for: equations, version control, reproducibility
   - → Proceed to Stage 3A

2. **PowerPoint** - PPTX format
   - Best for: quick turnaround, collaboration, ease of use
   - → Proceed to Stage 3B

---

### Stage 3A: LaTeX Implementation

**Objective:** Build poster using LaTeX

**Steps:**

**3A.1 Template Setup:**
1. Copy appropriate template:
   ```bash
   cp {baseDir}/assets/[package]_template.tex poster.tex
   ```

2. Configure page size:
   ```latex
   % beamerposter
   \usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}

   % tikzposter
   \documentclass[25pt,a0paper,portrait]{tikzposter}

   % baposter
   \documentclass[a0paper,portrait,fontscale=0.285]{baposter}
   ```

3. Set color scheme:
   ```latex
   \definecolor{primarycolor}{RGB}{0,51,102}
   \definecolor{accentcolor}{RGB}{204,153,0}
   ```

4. Plan column structure (2, 3, or 4 columns)

**3A.2 Content Integration:**
1. Create poster header:
   - Title: 10-15 words, 72-120pt font
   - Authors and affiliations
   - Logos (high-resolution, consistent sizing)

2. Populate sections with minimal text:
   ```latex
   \block{Introduction}{
     \begin{itemize}
       \item Key point 1 (6-8 words)
       \item Key point 2 (6-8 words)
       \item Key point 3 (6-8 words)
     \end{itemize}
   }
   ```

3. Integrate figures with clear captions
4. Add QR codes for supplementary materials:
   ```latex
   \usepackage{qrcode}
   \qrcode[height=2cm]{https://github.com/username/project}
   ```

**3A.3 Compilation:**
```bash
pdflatex poster.tex
# Or for better fonts:
lualatex poster.tex
```

**Exit Criteria (Stage 3A):**
- [ ] Template configured with correct dimensions
- [ ] Color scheme defined
- [ ] All sections populated
- [ ] Figures integrated with captions
- [ ] PDF compiles without errors

→ Proceed to Stage 4

---

### Stage 3B: PowerPoint Implementation

**Objective:** Build poster using PowerPoint

**Steps:**

**3B.1 Document Setup:**
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

**3B.2 Content Population:**
1. Add title and author block:
   - Title: 72-120pt bold sans-serif
   - Authors: 48-60pt
   - Affiliations: 36-48pt

2. Add section headers: 48-60pt bold

3. Add body text: 28-36pt regular

4. Insert figures with captions

5. Add QR code (minimum 2×2 inches)

**3B.3 Visual Refinement:**
1. Apply consistent color scheme (3-4 colors max)
2. Align all elements to grid (use Align tools)
3. Verify white space (20-30% of poster area)
4. Check accessibility:
   - Text contrast ≥4.5:1
   - Color-blind safe palette

**Exit Criteria (Stage 3B):**
- [ ] Dimensions match requirements exactly
- [ ] Grid guides visible and aligned
- [ ] All sections populated
- [ ] Elements aligned consistently
- [ ] Color scheme applied

→ Proceed to Stage 4

---

### Stage 4: Visual Content Creation (Both Formats)

**Objective:** Generate required figures and schematics

**Steps:**
1. Generate schematics using the `scientific-schematics` skill:
   - Invoke the skill with prompts for each required figure
   - Example prompts:
     - "methodology flowchart showing [process]"
     - "conceptual framework diagram for [topic]"
   - Save outputs to `figures/` directory at ≥300 DPI

2. Ensure all figures are high resolution:
   - Minimum 300 DPI at final print size
   - Vector formats (PDF, SVG) preferred for scalability
   - For 10" wide figure on A0: 3000+ pixels minimum

3. Apply consistent styling across all figures

**Exit Criteria:**
- [ ] ≥2 AI-generated schematics created
- [ ] All figures ≥300 DPI
- [ ] Figure labels large enough (18-24pt at poster size)
- [ ] Consistent styling across all figures
- [ ] Figures saved in appropriate format

---

### Stage 5: Quality Validation (Both Formats)

**Objective:** Ensure poster meets print and presentation standards

**Steps:**

**5.1 Visual Inspection:**
- Zoom to 100% and check:
  - Text readability
  - Image quality (no pixelation)
  - Color rendering

**5.2 Print Test:**
- Print at 25% scale on letter/A4 paper
- Title readable from arm's length (simulates 6 feet)
- Body readable from close (simulates 2 feet)

**5.3 Technical Verification:**

*For LaTeX:*
```bash
# Verify page dimensions
pdfinfo poster.pdf | grep "Page size"

# Check font embedding
pdffonts poster.pdf
```

*For PowerPoint:*
- Export PDF with embedded fonts
- Verify PDF dimensions match requirements

**5.4 Content Checklist:**
- [ ] Title ≤15 words, font ≥72pt
- [ ] Total word count 300-800
- [ ] Each section uses bullet points (not paragraphs)
- [ ] All figures have captions
- [ ] QR code added and tested
- [ ] References included (5-10 key citations)
- [ ] Contact information visible

**Exit Criteria:**
- [ ] Visual inspection passed
- [ ] Print test completed
- [ ] Technical verification passed
- [ ] All content checklist items verified

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Visual content | 30% | 40-50% | 50-60% |
| Word count | 300 | 500-600 | 400-500 |
| Title font | 72pt | 96pt | 120pt |
| Body font | 24pt | 28pt | 32pt |
| Figure resolution | 150 DPI | 300 DPI | 600 DPI |
| AI-generated figures | 1 | 2-3 | 4+ |
| Contrast ratio | 4.5:1 | 7:1 | 10:1 |
| References | 3 | 5-10 | 10-15 |

**Visual Inspection Checklist:**

Layout and Spacing:
- [ ] Content fills page (no large white margins)
- [ ] Consistent spacing between columns
- [ ] Consistent spacing between blocks
- [ ] No overlapping text or figures
- [ ] White space evenly distributed (20-30%)

Typography:
- [ ] Title visible and large (≥72pt)
- [ ] Section headers readable (48-72pt)
- [ ] Body text readable at 100% zoom (≥24pt)
- [ ] No text cutoff or overflow
- [ ] Consistent font usage (2-3 families max)

Visual Elements:
- [ ] All figures display correctly
- [ ] No pixelated or blurry images
- [ ] Figure captions present and readable
- [ ] Colors render as expected
- [ ] Logos display clearly
- [ ] QR codes scannable

Content Completeness:
- [ ] Title and authors complete
- [ ] All sections present (Intro, Methods, Results, Conclusions)
- [ ] References included
- [ ] Contact information visible
- [ ] No placeholder text (Lorem ipsum, TODO)

Accessibility:
- [ ] Text-background contrast ≥4.5:1
- [ ] Color scheme colorblind-safe (no red-green only)
- [ ] Information not conveyed by color alone

</success_criteria>

<scope>
## Scope

**In Scope:**
- Conference research posters (A0, A1, 36×48", etc.)
- Academic event posters
- Thesis defense posters
- LaTeX: beamerposter, tikzposter, baposter packages
- PowerPoint: PPTX format with PDF export
- Portrait and landscape orientations
- Multi-column layouts
- Figure and QR code integration
- PDF output for print and digital display

**Out of Scope** (use specialized resources):
- Slide presentations → use `scientific-slides`
- Scientific papers → use `scientific-writing`
- Data visualization code → use `plotting-libraries`
- Technical diagrams → use `scientific-schematics`
- Auto-generation from paper → use `paper-2-web`

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Text-Heavy Poster

**Anti-pattern:**
- Over 1000 words of text
- Full paragraphs instead of bullets
- Tiny fonts to fit more content
- Less than 30% visual content

**Solution:**
- Target 300-800 words maximum
- Use bullet points (3-5 per section, 6-8 words each)
- Generate 2-3 AI schematics with `scientific-schematics`
- Remove non-essential text ruthlessly

---

### 2. Wrong Page Size

**Anti-pattern:**
- Creating at screen dimensions then scaling
- Results in blurry text and pixelated images

**Solution:**
- Set exact dimensions at project start
- Verify with: `pdfinfo poster.pdf | grep "Page size"` (LaTeX)
- File → Page Setup → Custom Size (PowerPoint)

---

### 3. Low-Resolution Images

**Anti-pattern:**
- Web images (72 DPI) scaled up
- Pixelated figures at print size
- Small screenshots stretched

**Solution:**
- Generate figures at ≥300 DPI for final print size
- Use vector formats (PDF, SVG) when possible
- For A0 width (33.1"): 300 DPI = 9930 pixels minimum

---

### 4. Poor Color Contrast

**Anti-pattern:**
- Light text on light background
- Red-green color schemes
- Low contrast for accessibility

**Solution:**
- Test contrast: https://webaim.org/resources/contrastchecker/
- Target ≥4.5:1 ratio (WCAG AA), prefer 7:1
- Avoid red-green combinations
- Test with color blindness simulator

---

### 5. Skipping Print Test

**Anti-pattern:**
- Only reviewing on screen
- Missing readability issues
- Discovering problems at conference

**Solution:**
- Print at 25% scale on letter/A4 paper
- Title readable from 6 feet (arm's length from mini poster)
- Body readable from 2 feet (close inspection distance)
- Check colors printed accurately

---

### 6. Inconsistent Styling

**Anti-pattern:**
- Multiple font families (5+)
- Inconsistent colors and sizes
- Misaligned elements

**Solution:**
- Use 1-2 font families maximum
- Define color palette upfront (3-4 colors)
- Use alignment tools religiously
- Create consistent section templates

### Figure Legends Far From the Data on a Poster

**Anti-pattern:**
- Placing a colour-coded legend in a corner of a poster figure with viewers expected to shift their eyes back and forth between legend and data marks at 3-foot reading distance.
- Relying on small-font legends that are unreadable at 6-foot scanning distance.

**Solution:**
- **Direct-label** every line, group, and key data element next to the data it describes. The legend, if present, becomes a redundant aid not the primary key.
- Use the figure caption to introduce variables (`Treatment shown in blue, control in grey`), but place the colour-name strings *adjacent to* the visual elements they label, not in a separate legend block.
- For posters specifically: small distant legends are illegible at scanning distance and force readers to abandon the figure (Fujii 2026 §"Reduce cognitive load"; Wagemans 2012 Gestalt grouping).

</anti_patterns>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `scientific-schematics` | Generate 2-3 figures BEFORE populating poster |
| `scientific-slides` | Use for presentations (not posters) |
| `plotting-libraries` | Generate data visualizations for results |
| `venue-templates` | Conference-specific formatting requirements |
| `oligon-brand` | Brand colors and styling for Oligon posters |
| `paper-2-web` | Auto-generate poster from existing paper |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/references/poster_content_guide.md` | Content organization, writing style, word budgets |
| `{baseDir}/references/poster_design_principles.md` | Typography, color theory, accessibility |
| `{baseDir}/references/poster_layout_design.md` | Layout principles, grid systems, visual flow |
| `{baseDir}/references/latex_packages.md` | LaTeX package comparison (beamerposter, tikzposter, baposter) |
| `{baseDir}/references/pptx_workflows.md` | PowerPoint templates and workflows |
| `../shared/references/iconography-licensing.md` | Icon-library licensing (BioRender, NIH BIOART, SciDraw, Servier, Noun Project) — re-verify at submission |
| `../shared/references/pre_submission_checklist.md` | 15-point unified quality gate (also applies to posters) |
| `../shared/references/communication_context_matrix.md` | Audience × time × interaction → poster complexity (Fujii 2026); poster row covers 3-5 minute viewer scenarios |
| `../shared/references/figure_vs_table_decision.md` | Decision aid for figure vs table on a poster (Fujii 2026; Midway 2020) |
| `../shared/references/chart_types_catalog.md` | Flat by-chart-type catalog of 35 chart types — use when planning a poster's data figures (companion to `plot_selection_guide.md`) |
| `../oligon-brand/SKILL.md` `<design_foundation>` | Cognitive-foundation citations (Cleveland-McGill, Wagemans Gestalt grouping for direct labelling on posters, Crameri, Fujii 2026) |

## Templates

| Template | Description |
|----------|-------------|
| `{baseDir}/assets/beamerposter_template.tex` | Beamer-based academic poster |
| `{baseDir}/assets/tikzposter_template.tex` | TikZ-based modern poster |
| `{baseDir}/assets/baposter_template.tex` | Multi-column block poster |
| `{baseDir}/assets/poster_quality_checklist.md` | Quality review checklist |

## Scripts

| Script | Usage |
|--------|-------|
| `{baseDir}/scripts/review_poster.sh` | PDF quality checks (dimensions, fonts, size) |

</references>
