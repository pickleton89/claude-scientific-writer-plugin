---
name: latex-posters
version: 2.1.0
extends: visual-design
description: "Create professional research posters in LaTeX using beamerposter, tikzposter, or baposter. Supports conference presentations, academic posters, and scientific communication with layout design, color schemes, and figure integration."
allowed-tools: [Read, Write, Edit, Bash]
---

# LaTeX Research Posters

> **Design Foundation**: This skill extends [`visual-design`](../visual-design/SKILL.md) for typography, color, composition, and accessibility standards.

<overview>
Create publication-quality research posters using LaTeX packages (beamerposter, tikzposter, baposter). This skill provides decision frameworks for package selection, structured workflows for poster development, and quality validation checklists. Posters are primarily visual media—text-heavy posters fail to communicate effectively.

**Core Requirement**: Every poster MUST include 2-3 AI-generated figures using `scientific-schematics`. Target 40-50% visual content.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Creating research posters for conferences, symposia, or poster sessions
- Designing academic posters for university events or thesis defenses
- Preparing visual summaries of research for public engagement
- Converting scientific papers into poster format
- Building posters with complex multi-column layouts
- Need LaTeX for equations, version control, or reproducibility

Do NOT use this skill when:
- Creating PowerPoint posters → use `pptx-posters`
- Making slide presentations → use `scientific-slides`
- Writing papers → use `scientific-writing`
- Need quick turnaround without LaTeX expertise → use `pptx-posters`
</when_to_use>

<setup>
## Prerequisites

**Required Tools:**
```bash
# Verify LaTeX installation
pdflatex --version   # or lualatex --version
pdfinfo --version    # for PDF quality checks (poppler-utils)
```

**Required LaTeX Packages:**
- `beamerposter` - for Beamer-based posters
- `tikzposter` - for TikZ-based posters
- `baposter` - for multi-column block posters
- `qrcode` - for QR code generation

**Package Installation (TeX Live):**
```bash
tlmgr install beamerposter tikzposter baposter qrcode
```

**Dependency Check:**
Before starting, verify the poster class compiles:
```bash
echo '\documentclass[25pt,a0paper]{tikzposter}\begin{document}\end{document}' | pdflatex
```
</setup>

<decision_framework>
## LaTeX vs PowerPoint Decision

```
Creating a research poster?
│
├─ Need equations, version control, reproducibility?
│   └─ YES → Use this skill (LaTeX posters)
│
├─ Familiar with LaTeX?
│   ├─ YES → Use this skill (LaTeX posters)
│   └─ NO, need quick turnaround → use `pptx-posters`
│
├─ Have institutional LaTeX template?
│   └─ YES → Use this skill with template
│
└─ Conference requires specific format?
    ├─ LaTeX template provided → Use this skill
    └─ No requirement → Choose based on comfort level
```

## LaTeX Package Selection

| Factor | beamerposter | tikzposter | baposter |
|--------|--------------|------------|----------|
| **Best for** | Beamer users, institutional themes | Modern colorful designs, custom graphics | Multi-column, consistent spacing |
| **Learning curve** | Low (if know Beamer) | Medium | Medium |
| **Customization** | Theme-based | TikZ commands | Box-based |
| **Equations** | Excellent | Excellent | Excellent |
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
## Workflow

### Stage 1: Requirements & Planning

**Objective:** Define poster specifications and content outline

**Steps:**
1. Determine poster requirements:
   - Size (A0, 36×48", etc.) from conference guidelines
   - Orientation (portrait/landscape)
   - Submission deadline and format

2. Develop content outline:
   - Identify 1-3 core messages
   - Select 3-6 key figures (40-50% of poster area)
   - Draft bullet points for each section
   - Target 300-800 words total

3. Choose LaTeX package using decision tree above

**Exit Criteria:**
- [ ] Poster size confirmed from conference requirements
- [ ] Orientation decided (portrait/landscape)
- [ ] 1-3 core messages identified
- [ ] Figure list created (3-6 figures)
- [ ] LaTeX package selected (beamerposter/tikzposter/baposter)
- [ ] Word count target set (300-800 words)

---

### Stage 2: Template Setup & Design

**Objective:** Configure template with correct dimensions and branding

**Steps:**
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

3. Set color scheme (match institutional branding if required):
   ```latex
   % Define custom colors
   \definecolor{primarycolor}{RGB}{0,51,102}
   \definecolor{accentcolor}{RGB}{204,153,0}
   ```

4. Configure layout structure:
   - Plan column structure (2, 3, or 4 columns)
   - Allocate: Title 10-15%, Content 70-80%, Footer 5-10%

**Exit Criteria:**
- [ ] Template copied and renamed
- [ ] Page size matches conference requirements
- [ ] Color scheme defined (institutional or professional)
- [ ] Column structure planned
- [ ] Template compiles without errors

---

### Stage 3: Visual Content Creation

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

3. Create subfigures for comparisons if needed

**Exit Criteria:**
- [ ] ≥2 AI-generated schematics created
- [ ] All figures ≥300 DPI
- [ ] Figure labels large enough (18-24pt at poster size)
- [ ] Consistent styling across all figures
- [ ] Figures saved in figures/ directory

---

### Stage 4: Content Integration

**Objective:** Populate poster with text and figures

**Steps:**
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

3. Integrate figures with clear captions:
   ```latex
   \block{Results}{
     \begin{tikzfigure}
       \includegraphics[width=0.9\linewidth]{figures/results.png}
     \end{tikzfigure}
     \small Key finding: [one sentence interpretation]
   }
   ```

4. Add QR codes for supplementary materials:
   ```latex
   \usepackage{qrcode}
   \qrcode[height=2cm]{https://github.com/username/project}
   ```

**Content Density Guidelines:**

| Section | Word Count | Bullets | Visual Element |
|---------|------------|---------|----------------|
| Introduction | 50-100 | 3-5 | Optional diagram |
| Methods | 50-100 | 3-5 | Required flowchart |
| Results | 100-200 | 4-6 | Required figures (2-3) |
| Conclusions | 50-75 | 3-4 | Optional summary graphic |
| References | 5-10 citations | N/A | Optional QR code |

**Exit Criteria:**
- [ ] Title ≤15 words, font ≥72pt
- [ ] Total word count 300-800
- [ ] Each section has bullet points (not paragraphs)
- [ ] Figures integrated with captions
- [ ] QR code added for supplementary materials
- [ ] References included (5-10 key citations)

---

### Stage 5: Compilation & Quality Review

**Objective:** Generate PDF and validate quality

**Steps:**
1. Compile to PDF:
   ```bash
   pdflatex poster.tex
   # Or for better fonts:
   lualatex poster.tex
   ```

2. Verify page dimensions:
   ```bash
   pdfinfo poster.pdf | grep "Page size"
   # A0: 2384 x 3370 points
   # 36x48": 2592 x 3456 points
   ```

3. Check font embedding:
   ```bash
   pdffonts poster.pdf
   # All fonts should show "yes" in "emb" column
   ```

4. Run systematic visual inspection (see checklist below)

5. Perform reduced-scale print test:
   - Print at 25% scale on letter/A4 paper
   - Simulates viewing from 8-10 feet
   - Check title readable from 6 feet, body from 2 feet

**Exit Criteria:**
- [ ] PDF compiles without errors
- [ ] Page size matches requirements exactly
- [ ] All fonts embedded
- [ ] Visual inspection checklist passed
- [ ] Reduced-scale print test completed
- [ ] No overfull/underfull box warnings in critical areas

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
- [ ] White space evenly distributed

Typography:
- [ ] Title visible and large (≥72pt)
- [ ] Section headers readable (48-72pt)
- [ ] Body text readable at 100% zoom (≥24pt)
- [ ] No text cutoff or overflow
- [ ] Consistent font usage

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
- beamerposter, tikzposter, baposter packages
- Portrait and landscape orientations
- Multi-column layouts
- Figure and QR code integration
- PDF output for print and digital display

**Out of Scope** (use specialized resources):
- PowerPoint posters → use `pptx-posters`
- Slide presentations → use `scientific-slides`
- Scientific papers → use `scientific-writing`
- Data visualization code → use `plotting-libraries`
- Technical diagrams → use `scientific-schematics`

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
```latex
% Poster compiles but wrong size
\documentclass{article}  % Wrong! Not a poster class
```

**Solution:**
```latex
% beamerposter - verify size matches conference
\usepackage[size=a0,orientation=portrait]{beamerposter}

% Verify with:
pdfinfo poster.pdf | grep "Page size"
```

---

### 3. Low-Resolution Images

**Anti-pattern:**
- Web images (72 DPI) scaled up
- Pixelated figures at print size
- Small screenshots stretched

**Solution:**
- Generate figures at ≥300 DPI for final print size
- Use vector formats (PDF, SVG) when possible
- Check with: `pdfimages -list poster.pdf`
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

</anti_patterns>

<templates>
## Package Configuration Examples

### beamerposter Full Page Setup

```latex
\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}

% Remove margins
\setbeamersize{text margin left=10mm, text margin right=10mm}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{footline}{}
\setbeamertemplate{headline}{}

% Custom colors
\definecolor{posterblue}{RGB}{0,51,102}
\setbeamercolor{block title}{bg=posterblue,fg=white}
\setbeamercolor{block body}{bg=white,fg=black}
```

### tikzposter Full Page Setup

```latex
\documentclass[
  25pt,
  a0paper,
  portrait,
  margin=10mm,
  innermargin=15mm,
  blockverticalspace=15mm,
  colspace=15mm
]{tikzposter}

\usetheme{Rays}
\usecolorstyle{Denmark}
```

### baposter Full Page Setup

```latex
\documentclass[a0paper,portrait,fontscale=0.285]{baposter}

\begin{poster}{
  grid=false,
  columns=3,
  colspacing=1.5em,
  headerheight=0.12\textheight,
  background=plain,
  bgColorOne=white,
  borderColor=blue!50
}
```

### Common Figure Block

```latex
% tikzposter figure block
\block{Results}{
  \begin{tikzfigure}[Key finding visualization]
    \includegraphics[width=0.9\linewidth]{figures/results.pdf}
  \end{tikzfigure}

  \textbf{Key Findings:}
  \begin{itemize}
    \item Finding 1 with quantitative result
    \item Finding 2 with statistical significance
    \item Finding 3 with comparison to baseline
  \end{itemize}
}
```

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `scientific-schematics` | Generate 2-3 figures BEFORE populating poster |
| `pptx-posters` | Alternative for PowerPoint-based posters |
| `scientific-slides` | Use for presentations (not posters) |
| `plotting-libraries` | Generate data visualizations for results |
| `venue-templates` | Conference-specific formatting requirements |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/references/latex_poster_packages.md` | Detailed package comparison with examples |
| `{baseDir}/references/poster_layout_design.md` | Layout principles, grid systems, visual flow |
| `{baseDir}/references/poster_design_principles.md` | Typography, color theory, accessibility |
| `{baseDir}/references/poster_content_guide.md` | Content organization, writing style |

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
