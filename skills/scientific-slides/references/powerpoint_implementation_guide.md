# PowerPoint Implementation Guide for Scientific Presentations

## Overview

This guide covers two things: (1) discipline for building scientific decks in the PowerPoint Microsoft 365 desktop application (Slide Master, placeholders, theme colors, accessibility, Copilot audits, distribution hygiene), and (2) programmatic creation via the `document-skills:pptx` skill (html2pptx / PptxGenJS) when a deck needs to be generated from code.

For cross-cutting design principles (typography floors, color theory, assertion-evidence, narrative arcs, pre-flight QA) read [`design_best_practices.md`](design_best_practices.md) first. For deeper typography/color/layout detail see [`slide_design_principles.md`](slide_design_principles.md).

**CRITICAL**: Avoid dry, text-heavy presentations. Scientific slides should be:
- **Visually engaging**: High-quality images, figures, diagrams on EVERY slide
- **Research-backed**: Citations from `deep-research` for credibility (8-15 papers minimum)
- **Modern design**: Contemporary color palettes, not default themes
- **Minimal text**: 3-4 bullets with 4-6 words each, visuals do the talking
- **Professional polish**: Consistent but varied layouts, generous white space

**Anti-Pattern Warning**: All-bullet-point slides with black text on white background = instant boredom and forgotten science.

---

## PowerPoint Microsoft 365 Desktop Discipline

This section governs work inside the PowerPoint M365 desktop app. Apply these rules before opening any slide file; technical-level drift quietly corrupts both per-slide composition and the deck's macro flow.

### Work at the master, not the slide

Establish theme colors, theme fonts, custom layouts, footer text, and guide positions in `View > Slide Master` before building content. Changes at the master cascade; changes at the slide become overrides that break when the theme is updated. Pick Heading and Body fonts via `Slide Master > Fonts > Customize Fonts` so that placeholder text inherits them; avoid naming specific fonts in text boxes for any content other than code blocks or equation-editor glyphs. When a collaborator pastes in slides from another deck, run `Home > Reset` after re-applying the correct layout to restore placeholder geometry and theme linkage.

Master-level discipline is the primary defense against **slide drift** — the incremental loss of visual consistency that accumulates as collaborators paste content across templates, override fonts from the Home ribbon, and insert free text boxes in place of placeholders. The visible diagnostic is **jittering** — an element that should sit in the same position across slides (a logo, a section header, a footer citation) shifts left-right or up-down as the reader advances. Flip through the deck in Slide Sorter view; anything that jitters is almost certainly not using a placeholder.

Minimum layout set: Title, Section Divider, Content (single column), Two-Content/Comparison, Multi-Panel Figure, Data Table, Equation, References, Disclosures, Backup/Appendix. Build in Slide Master view (`View > Slide Master > Insert Layout`), and populate with `Insert Placeholder` — not text boxes. Two downstream capabilities depend on this: Outline View (`View > Outline View`) only shows placeholder text, and the Accessibility Checker (`Review > Check Accessibility`) flags "missing slide title" if the title lives in a free text box styled to look like a title.

### Build layouts Maximum-to-Minimum

When constructing custom layouts, build the **most complex** layout first and create simpler layouts by duplicating the complex one and **subtracting** placeholders. Do not build simple layouts first and add placeholders to create complex ones.

**Why:** Each placeholder on a layout is assigned an index in creation order. PowerPoint's layout-switching logic tries to match placeholder indices across layouts when a slide is reassigned. Building Maximum-to-Minimum preserves index order automatically because every simpler layout is a strict subset of the complex one. Building Minimum-to-Maximum reverses the order and causes layout switches to silently lose content, reshuffle placeholders, or drop text into unexpected boxes — a failure mode that is hard to diagnose after the fact.

**The rule:** identify the most placeholder-rich layout you will need, build it completely, then duplicate and delete placeholders to make each simpler layout.

### Theme Colors vs Standard Colors

PowerPoint's color picker shows two rows at the top: **Theme Colors** and **Standard Colors**. Theme colors are tied to the Slide Master's theme definition; if the master's color scheme changes (rebrand, partner variant, CVD-safe retool), every element colored from the Theme row updates in one step. Standard colors and manually entered hex values are baked into each object individually and do not respond to theme changes — a rebrand of a deck built with standard colors requires touching every object by hand.

**Rule:** pick colors from the Theme Colors row only for primary content. Reserve Standard Colors and manual hex entries for one-off annotations where the color is genuinely fixed (a specific CPK atom, a published figure's exact shade).

**Audit:** open `Home > Font Color > More Colors > Custom` on any colored element; if the current color is not visibly highlighted in the Theme row, it is not a theme color. For co-branded or licensing contexts where the deck may be rebuilt in the partner's theme, this audit is not optional.

Load the Okabe-Ito categorical palette into the Slide Master's Theme Colors (`Slide Master > Colors > Customize Colors`), mapping the primary brand color to Accent 1 (the default for new shapes and the first chart series).

### Evaluate third-party templates before committing

Downloaded or vendor templates vary enormously. Before adopting one as a project base, test four things:

1. **Real custom layouts exist.** Open Slide Master view; a template with only default Title/Title+Content/Two-Content layouts inherited from PowerPoint's built-in themes is no better than starting blank.
2. **Layout switches survive content.** Insert a test slide on a custom layout, switch it to another custom layout, and verify content survives intact. A template built min-to-max will fail.
3. **Theme Colors customized.** Check `Slide Master > Colors`; uncustomized theme colors mean no visual language has been defined.
4. **Notes + Handout Masters styled.** Open `View > Notes Master` and `View > Handout Master`; a template that only touched the Slide Master leaves notes and handouts exposing default Office styling when printed.

A template that fails any test should be rebuilt or rejected. The cost of rebuilding is lower than the cost of compounding failures across every deck in the project.

### Accessibility as discipline

Run `Review > Check Accessibility` on every deck and address all Errors and most Warnings. Enable "Keep accessibility checker running while I work" so issues surface as they are created.

Alt text is mandatory for every non-decorative image, shape, SmartArt, chart, and embedded object. Add via right-click `View Alt Text` or `Picture Format > Alt Text`. Write one or two descriptive sentences that state the **finding** rather than the chart type — e.g., "Bar chart shows a 2-fold increase in cell viability for the treatment group," not "Image of a bar chart." Mark genuinely decorative elements with the Mark as Decorative checkbox so screen readers skip them.

For reading order, use the **Reading Order Pane** (`Review > Check Accessibility` dropdown > `Reading Order Pane`) — not the Selection Pane. The Reading Order Pane lists objects top-to-bottom in the order a screen reader reads them. The Selection Pane shows z-order for layering and is read bottom-up; using it for reading order is a common source of confusion. Group multi-panel figure elements (Ctrl+G) so the screen reader treats the figure as one unit.

For code-checkable contrast (WCAG 4.5:1 body, 3:1 large text / meaningful non-text) use `skills/visual-design/utils/check_contrast(fg, bg)` rather than PowerPoint's built-in Accessibility Checker warning ("Hard-to-read text contrast"), which is heuristic.

### Embedded vs linked

Link Excel charts while drafting so they update live. Before distribution, either break the links (`File > Info > Edit Links to Files > Break Link`) or re-paste as embedded chart or picture. A linked chart emailed externally displays the last rendered state, throws a broken-link error on open, and the Edit Links dialog reveals the absolute local path of the original. Embedded Excel carries the entire workbook inside the .pptx — inflates file size and can expose hidden sheets, comments, named ranges, or pivot sources. Run `File > Info > Check for Issues > Inspect Document` before distribution. Videos: embed rather than link; compress via `File > Info > Compress Media` before sending.

### Font embedding

Embed fonts for any deck going to another machine: `File > Options > Save > Embed fonts in the file`.

- **"Embed only the characters used"** — smaller file, recipients cannot edit without losing glyphs. Use for final distribution.
- **"Embed all characters"** — larger file, full edit capability. Use for collaborative editing.

TrueType and OpenType embed reliably; PostScript Type 1 does not. Microsoft cloud fonts (Aptos, Bahnschrift) auto-download on M365 devices and remove the need to embed, but require sign-in. If a licensed foundry font flags as non-embeddable, replace the font or convert text to shapes in final artwork.

### Slide dimensions and file hygiene

Default to 16:9 widescreen (13.333" × 7.5") — the PowerPoint default since 2013, matching modern projectors. Use 4:3 (10" × 7.5") only for known legacy display systems. Set dimensions before building; rescaling after introduces artifacts.

**Before distribution:**
- `Picture Format > Compress Pictures` at HD (330 ppi) or Print (220 ppi) quality
- Delete unused masters and layouts from Slide Master
- `Compress Media` for embedded video
- Store in OneDrive or SharePoint for `File > Info > Version History` (AutoRecover is crash recovery, not version control)

### SmartArt, Designer, Copilot — generation anti-patterns

**SmartArt** (`Insert > SmartArt`) is recognizable at a glance and signals template-driven work. Defaults read as dated; auto-sizing collapses text to illegibility when nodes are added. If used as a starting point, immediately right-click and `Convert > Convert to Shapes` to break into editable primitives before styling.

**Designer** (`Design > Designer`) proposes layouts via cloud services and works for title slides and single-visual slides; will not improve data-dense content and tends toward minimalist stock-photo aesthetics wrong for scientific decks. Honest use: inspiration for section dividers and title slides only.

**Microsoft 365 Copilot** can generate entire decks from a prompt or reference document. Use *after* the outline and figures are locked, not before. Audit for these five failure modes whenever Copilot has touched a deck:

1. **Stock imagery instead of data figures** — replace with the actual figure.
2. **Over-bulleted body text** — rewrite as assertion headline + visual evidence.
3. **Loss of scientific specificity** — quantitative claims softened into qualitative summaries that read well but misrepresent the data. Verify every number.
4. **Hallucinated citations** — made-up author names and DOIs. Verify every citation against your reference manager.
5. **Inconsistent color usage** — Copilot ignores the Slide Master theme and introduces its own palette. Reset via `Home > Reset` and re-apply the theme.

**Never ship a Copilot-generated slide without a human read of every claim.** AI-generated images may carry watermark artifacts or C2PA content credentials; disclose if the deck represents the image as a photograph or experimental result. Use AI images for decorative elements and section dividers only — never as data or representations of experimental conditions.

### Collaborative authoring in OneDrive/SharePoint

Real-time co-authoring improves on emailed copies but introduces three failure modes:

1. **Font and color drift from multiple authors** is harder to prevent than to repair. Set the Slide Master early, lock sensitive sections, run a drift audit (`Home > Reset` on each slide) before final distribution.
2. **Silent conflicts** on simultaneous edits to the same placeholder. PowerPoint resolves by keeping the last-saved change, which is occasionally the wrong one. Use `File > Info > Version History` to recover a known-good prior state.
3. **No word-level track changes.** Closest analogs: Comments (`Review > New Comment`) for discussion; `Review > Compare` to diff two versions after the fact. For decks circulating through MLR or legal review: author in a personal drive, circulate a PDF export for comment, log comments into a change register, apply edits, re-export.

### Guides, grids, and alignment

Enable Guides (Alt+F9) and Smart Guides; set master-level guides at safe-area margins (~0.5" from each edge) and at column boundaries for two-content layouts. Use `Shape Format > Align` with Align to Slide for slide-relative alignment and Align Selected Objects for inter-object alignment.

For multi-object alignment, `Align > Distribute Horizontally` / `Distribute Vertically` equalizes spacing between three or more selected objects in one step — the correct tool for four-panel figure layouts and button-style comparison elements.

For cases where a literal grid is needed (aligning six independent text blocks, positioning icons on a lattice), the **table trick**: insert a table sized to the grid (e.g., 12 columns × 8 rows covering the slide area), turn off all borders, use each cell as a positioning anchor. Delete the table when alignment is confirmed, or keep with transparent borders as a persistent scaffold.

### Cameo, live captions, recording

`Insert > Cameo` embeds the presenter's webcam feed as a slide object — useful for hybrid talks and recorded asynchronous decks. Live Captions (`Slide Show > Always Use Subtitles`) provides cloud-based transcription, with optional translation into a second language. Record (`Record > From Beginning`) produces an MP4 with narration, timings, ink, and cameo — increasingly how KOL slide kits are distributed. Some M365 builds report issues running cameo and live captions simultaneously during recording; test the combination before committing.

### Content security, hidden data, DLP

Scientific decks often contain more than what is visible:
- Embedded Excel workbooks carry their full sheet structure — hidden sheets, comments, named ranges, pivot sources.
- Speaker notes travel with the .pptx and are visible to anyone who opens it.
- Revision history metadata, author names, file paths in linked objects, and comments can leak information unintentionally.

**Before distributing:** run `File > Info > Check for Issues > Inspect Document` and remove revealed items that should not travel (comments, ink annotations, document properties, embedded documents, presentation notes if sensitive, off-slide content). For decks going outside the company, **export to PDF** rather than .pptx — PDF flattens embedded objects and strips metadata.

For Data Loss Prevention in corporate environments, Microsoft Purview policies apply to .pptx the same way they apply to Word and Excel; a classified file cannot be emailed externally without policy review. Assume every deck you distribute could be forwarded.

### External image preprocessing

PowerPoint's built-in background removal tool produces fuzzy edges and poor handling of hair/fine detail. For production-quality background removal, use an external tool before insertion:

- **Adobe Express** (background removal)
- **removal.ai**
- **inPixio**
- **removebg** (remove.bg)
- **Erase.bg**

All produce cleaner results than PowerPoint's native tool. Insert the cleaned PNG (or better, transparent-background SVG if the source supports it) into the slide.

### Template variant stripping via POTX

Office theme variants can accidentally apply to template-based decks when users click through `Design > Themes`. To strip variants from a template, save the file as **POTX** and then save back as **PPTX**:

1. `File > Save As` → choose **PowerPoint Template (.potx)`
2. Close and reopen the saved .potx file
3. `File > Save As` → choose **PowerPoint Presentation (.pptx)`

The POTX roundtrip removes the variant metadata. Swinford & Terberg, *Building PowerPoint Templates* (2nd ed.) documents this pattern and is the canonical reference for template maintenance.

---

## Using the PPTX Skill

### Reference

For complete technical documentation on PowerPoint creation, refer to:
- **Main documentation**: `document-skills:pptx`
- **HTML to PowerPoint workflow**: Detailed in `pptx/html2pptx.md`
- **OOXML editing**: For advanced editing in `pptx/ooxml.md`

### Two Approaches to PowerPoint Creation

#### 1. Programmatic Creation (html2pptx)

**Best for**: Creating presentations from scratch with custom designs and data visualizations.

**Workflow**:
1. Read `document-skills:pptx` completely
2. Design slides in HTML with proper dimensions (720pt × 405pt for 16:9)
3. Create JavaScript file using `html2pptx()` function
4. Add charts and tables using PptxGenJS API
5. Generate thumbnails and validate visually
6. Iterate based on visual inspection

**Example Structure**:
```javascript
const pptx = new PptxGenJS();

// Add title slide
const slide1 = pptx.addSlide();
slide1.addText("Your Title", {
  x: 1, y: 2, w: 8, h: 1,
  fontSize: 44, bold: true, align: "center"
});

// Add content slide with figure
const slide2 = pptx.addSlide();
slide2.addText("Results", { x: 0.5, y: 0.5, fontSize: 32 });
slide2.addImage({ path: "figure.png", x: 1, y: 1.5, w: 8, h: 4 });

pptx.writeFile({ fileName: "presentation.pptx" });
```

#### 2. Template-Based Creation

**Best for**: Using existing PowerPoint templates or editing existing presentations.

**Workflow**:
1. Start with template.pptx
2. Use `scripts/rearrange.py` to duplicate/reorder slides
3. Use `scripts/inventory.py` to extract text
4. Generate replacement text JSON
5. Use `scripts/replace.py` to update content
6. Validate with thumbnail grids

**Key Scripts**:
- `rearrange.py`: Duplicate and reorder slides
- `inventory.py`: Extract all text shapes
- `replace.py`: Apply text replacements
- `thumbnail.py`: Visual validation

## Design Principles for Scientific Presentations

### 1. Layout and Structure

**Slide Master Setup**:
- Create consistent master slides
- Define 4-5 layout types (title, content, figure, two-column, closing)
- Set default fonts, colors, and spacing
- Include placeholders for logos and footers

**Standard Layouts**:

**Title Slide**:
```
┌─────────────────────────┐
│                         │
│   Presentation Title    │
│   Your Name             │
│   Institution           │
│   Date / Conference     │
│                         │
└─────────────────────────┘
```

**Content Slide**:
```
┌─────────────────────────┐
│ Slide Title             │
├─────────────────────────┤
│ • Bullet point 1        │
│ • Bullet point 2        │
│ • Bullet point 3        │
│                         │
│ [Optional figure]       │
└─────────────────────────┘
```

**Two-Column Slide**:
```
┌─────────────────────────┐
│ Slide Title             │
├───────────┬─────────────┤
│           │             │
│  Text     │   Figure    │
│  Content  │   or        │
│           │   Data      │
└───────────┴─────────────┘
```

**Full-Figure Slide**:
```
┌─────────────────────────┐
│ Figure Title (small)    │
├─────────────────────────┤
│                         │
│    Large Figure or      │
│    Visualization        │
│                         │
└─────────────────────────┘
```

### 2. Typography

**Font Selection**:
- **Primary**: Sans-serif (Arial, Calibri, Helvetica)
- **Alternative**: Verdana, Tahoma, Trebuchet MS
- **Avoid**: Serif fonts (harder to read on screens), decorative fonts

**Font Sizes**:
- Title slide title: 44-54pt
- Slide titles: 32-40pt
- Body text: 24-28pt (minimum 18pt)
- Captions: 16-20pt
- Footer: 10-12pt

**Text Formatting**:
- **Bold**: For emphasis (use sparingly)
- **Color**: For highlighting (consistent meaning)
- **Size**: For hierarchy
- **Alignment**: Left for body, center for titles

**The 6×6 Rule**:
- Maximum 6 bullet points per slide
- Maximum 6 words per bullet
- Better: 3-4 bullets with 4-8 words each

### 3. Color Schemes

**Selecting Colors**:

Consider your subject matter and audience:
- **Academic/Professional**: Navy blue, gray, white with minimal accent
- **Biomedical**: Blue and green tones (avoid red-green combinations)
- **Technology**: Modern colors (teal, orange, purple)
- **Clinical**: Conservative (blue, gray, subdued greens)

**Example Palettes**:

**Classic Scientific**:
- Background: White (#FFFFFF)
- Title: Navy (#1C3D5A)
- Text: Dark gray (#2D3748)
- Accent: Orange (#E67E22)

**Modern Research**:
- Background: Light gray (#F7FAFC)
- Title: Teal (#0A9396)
- Text: Charcoal (#2C2C2C)
- Accent: Coral (#EE6C4D)

**High Contrast** (for large venues):
- Background: White (#FFFFFF)
- Title: Black (#000000)
- Text: Dark gray (#1A1A1A)
- Accent: Bright blue (#0066CC)

**Accessibility Guidelines**:
- Minimum contrast ratio: 4.5:1 (body text)
- Preferred contrast ratio: 7:1 (AAA standard)
- Avoid red-green combinations (8% of men are color-blind)
- Use patterns or shapes in addition to color for data

### 4. Visual Elements

**Figures and Images**:
- **Resolution**: Minimum 300 DPI for print, 150 DPI for projection
- **Format**: PNG for screenshots, PDF/SVG for vector graphics
- **Size**: Large enough to be readable from back of room
- **Placement**: Center or use two-column layout

**Data Visualizations**:
- **Simplify** from journal figures (fewer panels, larger text)
- **Font sizes**: 18-24pt for axis labels
- **Line widths**: 2-4pt thickness
- **Colors**: High contrast, color-blind safe
- **Labels**: Direct labeling preferred over legends

**Icons and Shapes**:
- Use for visual interest and organization
- Consistent style (all outline or all filled)
- Size appropriately (not too large or small)
- Limit colors (match theme)

### 5. Animations and Transitions

**When to Use**:
- ✅ Progressive disclosure of bullet points
- ✅ Building complex figures incrementally
- ✅ Emphasizing key findings
- ✅ Showing process steps

**When to Avoid**:
- ❌ Decoration or entertainment
- ❌ Every single slide
- ❌ Distracting effects (fly in, bounce, spin)

**Recommended Animations**:
- **Appear**: Clean, professional
- **Fade**: Subtle transition
- **Wipe**: Directional reveal
- **Duration**: Fast (0.2-0.3 seconds)
- **Trigger**: On click (not automatic)

**Slide Transitions**:
- Use consistent transition throughout (or none)
- Recommended: None, Fade, or Push
- Avoid: 3D rotations, complex effects
- Duration: Very fast (0.3-0.5 seconds)

## Creating Presentations with PPTX Skill

### Design-First Workflow

**Step 0: Choose Modern Color Palette Based on Topic**

**CRITICAL**: Select colors that reflect your subject matter, not generic defaults.

**Topic-Based Palette Examples:**
- **Biotechnology/Life Sciences**: Teal (#0A9396), Coral (#EE6C4D), Cream (#F4F1DE)
- **Neuroscience/Brain Research**: Deep Purple (#722880), Magenta (#D72D51), White
- **Machine Learning/AI**: Bold Red (#E74C3C), Orange (#F39C12), Dark Gray (#2C2C2C)
- **Physics/Engineering**: Navy (#1C3D5A), Orange (#E67E22), Light Gray (#F7FAFC)
- **Medicine/Healthcare**: Teal (#5EA8A7), Coral (#FE4447), White (#FFFFFF)
- **Environmental Science**: Sage (#87A96B), Terracotta (#E07A5F), Cream (#F4F1DE)

See full palette options in pptx skill SKILL.md (lines 76-94).

**Step 1: Plan Design System** (With Modern Palette)
```javascript
// Define design constants with MODERN colors (not defaults)
const DESIGN = {
  colors: {
    primary: "0A9396",    // Teal (modern, engaging)
    accent: "EE6C4D",     // Coral (attention-grabbing)
    text: "2C2C2C",       // Charcoal (readable)
    background: "FFFFFF"  // White (clean)
  },
  fonts: {
    title: { size: 40, bold: true, face: "Arial" },
    heading: { size: 28, bold: true, face: "Arial" },
    body: { size: 24, face: "Arial" },
    caption: { size: 16, face: "Arial" }
  },
  layout: {
    margin: 0.5,
    titleY: 0.5,
    contentY: 1.5
  }
};
```

**Step 2: Create Reusable Functions**
```javascript
function addTitleSlide(pptx, title, subtitle, author) {
  const slide = pptx.addSlide();
  slide.background = { color: DESIGN.colors.primary };
  
  slide.addText(title, {
    x: 1, y: 2, w: 8, h: 1,
    fontSize: 44, bold: true, color: "FFFFFF",
    align: "center"
  });
  
  slide.addText(subtitle, {
    x: 1, y: 3.2, w: 8, h: 0.5,
    fontSize: 24, color: "FFFFFF",
    align: "center"
  });
  
  slide.addText(author, {
    x: 1, y: 4, w: 8, h: 0.4,
    fontSize: 18, color: "FFFFFF",
    align: "center"
  });
  
  return slide;
}

function addContentSlide(pptx, title, bullets) {
  const slide = pptx.addSlide();
  
  slide.addText(title, {
    x: DESIGN.layout.margin,
    y: DESIGN.layout.titleY,
    w: 9,
    h: 0.5,
    ...DESIGN.fonts.heading,
    color: DESIGN.colors.primary
  });
  
  slide.addText(bullets, {
    x: DESIGN.layout.margin,
    y: DESIGN.layout.contentY,
    w: 9,
    h: 3,
    ...DESIGN.fonts.body,
    bullet: true
  });
  
  return slide;
}
```

**Step 3: Build Presentation** (Visual-First Approach)
```javascript
const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_16x9";

// Title slide with background image or color block
const titleSlide = pptx.addSlide();
titleSlide.background = { color: DESIGN.colors.primary }; // Bold color background
addTitleSlide(
  pptx,
  "Research Title",
  "Subtitle or Conference Name",
  "Your Name • Institution • Date"
);

// Introduction with image/icon
const introSlide = pptx.addSlide();
introSlide.addImage({
  path: "concept_image.png",  // Visual representation of concept
  x: 5, y: 1.5, w: 4, h: 3
});
introSlide.addText("Background", { x: 0.5, y: 0.5, fontSize: 36, bold: true });
introSlide.addText([
  "Key context point 1 (AuthorA, 2023)",
  "Key context point 2 (AuthorB, 2022)",
  "Research gap identified (AuthorC, 2021)"
], {
  x: 0.5, y: 1.5, w: 4, h: 2,
  fontSize: 24, bullet: true
});

// Results slide - FIGURE DOMINATES
const resultsSlide = pptx.addSlide();
resultsSlide.addText("Main Finding", { x: 0.5, y: 0.5, fontSize: 32, bold: true });
resultsSlide.addImage({
  path: "results_figure.png",  // Large, clear figure
  x: 0.5, y: 1.5, w: 9, h: 4   // Nearly full slide
});
// Minimal text annotation only
resultsSlide.addText("34% improvement (p < 0.001)", {
  x: 7, y: 1, fontSize: 20, color: DESIGN.colors.accent, bold: true
});

// Save
pptx.writeFile({ fileName: "presentation.pptx" });
```

**Key Changes from Dry Presentations:**
- Title slide uses bold background color (not plain white)
- Introduction includes relevant image (not just bullets)
- Results slide is figure-dominated (not text-dominated)
- Citations included in bullets for research context
- Text is minimal and supporting, visuals are primary

### Adding Scientific Content

**Equations** (as images):
```javascript
// Render equation as PNG first (using LaTeX or online tool)
// Then add to slide
slide.addImage({
  path: "equation.png",
  x: 2, y: 3, w: 6, h: 1
});
```

**Tables**:
```javascript
slide.addTable([
  [
    { text: "Method", options: { bold: true } },
    { text: "Accuracy", options: { bold: true } },
    { text: "Time (s)", options: { bold: true } }
  ],
  ["Method A", "0.85", "10"],
  ["Method B", "0.92", "25"],
  ["Method C", "0.88", "15"]
], {
  x: 2, y: 2, w: 6,
  fontSize: 20,
  border: { pt: 1, color: "888888" },
  fill: { color: "F5F5F5" }
});
```

**Charts**:
```javascript
// Bar chart
slide.addChart(pptx.ChartType.bar, [
  {
    name: "Control",
    labels: ["Metric 1", "Metric 2", "Metric 3"],
    values: [45, 67, 82]
  },
  {
    name: "Treatment",
    labels: ["Metric 1", "Metric 2", "Metric 3"],
    values: [52, 78, 91]
  }
], {
  x: 1, y: 1.5, w: 8, h: 4,
  chartColors: [DESIGN.colors.primary, DESIGN.colors.accent],
  showTitle: false,
  showLegend: true,
  fontSize: 18
});
```

## Visual Validation Workflow

### Generate Thumbnails

After creating presentation:

```bash
# Create thumbnail grid for quick review
python scripts/thumbnail.py presentation.pptx review/thumbnails --cols 4

# Or for individual slides
python scripts/thumbnail.py presentation.pptx review/slide
```

### Inspection Checklist

For each slide, check:
- [ ] Text readable (not cut off or too small)
- [ ] No element overlap
- [ ] Consistent colors and fonts
- [ ] Adequate white space
- [ ] Figures clear and properly sized
- [ ] Alignment correct

### Common Issues

**Text Overflow**:
- Reduce font size or text length
- Increase text box size
- Split into multiple slides

**Element Overlap**:
- Use two-column layout
- Reduce element sizes
- Adjust positioning

**Poor Contrast**:
- Choose higher contrast colors
- Use dark text on light background
- Test with contrast checker

## Templates and Examples

### Starting from Template

If you have an existing template:

1. **Extract template structure**:
```bash
python scripts/inventory.py template.pptx inventory.json
```

2. **Create thumbnail grid**:
```bash
python scripts/thumbnail.py template.pptx template_review
```

3. **Analyze layouts** and document which slides to use

4. **Rearrange slides**:
```bash
python scripts/rearrange.py template.pptx working.pptx 0,5,5,12,18,22
```

5. **Replace content**:
```bash
python scripts/replace.py working.pptx replacements.json output.pptx
```

## Best Practices Summary

### Do's (Make Presentations Engaging)

- ✅ Use `deep-research` to find 8-15 papers for citations
- ✅ Add HIGH-QUALITY visuals to EVERY slide (figures, images, diagrams, icons)
- ✅ Choose MODERN color palette reflecting your topic (not defaults)
- ✅ Keep text MINIMAL (3-4 bullets, 4-6 words each)
- ✅ Use LARGE fonts (24-28pt body, 36-44pt titles)
- ✅ Vary slide layouts (full-figure, two-column, visual overlays)
- ✅ Maintain high contrast (7:1 preferred)
- ✅ Generous white space (40-50% of slide)
- ✅ Cite papers in intro and discussion (establish credibility)
- ✅ Test readability from distance
- ✅ Validate visually before presenting

### Don'ts (Avoid Dry Presentations)

- ❌ Don't create text-only slides (add visuals to EVERY slide)
- ❌ Don't use default themes unchanged (customize for your topic)
- ❌ Don't have all bullet-point slides (vary layouts)
- ❌ Don't skip `deep-research` (presentations need citations too)
- ❌ Don't cram too much text on one slide
- ❌ Don't use tiny fonts (<24pt for body)
- ❌ Don't rely solely on color
- ❌ Don't use complex animations
- ❌ Don't mix too many font styles
- ❌ Don't ignore accessibility
- ❌ Don't skip visual validation

## Accessibility Considerations

**Color Contrast**:
- Use WebAIM contrast checker
- Minimum 4.5:1 for normal text
- Preferred 7:1 for optimal readability

**Color Blindness**:
- Test with Coblis simulator
- Use patterns/shapes with colors
- Avoid red-green combinations

**Readability**:
- Sans-serif fonts only
- Minimum 18pt, prefer 24pt+
- Clear visual hierarchy
- Adequate spacing

## Integration with Other Skills

**With Scientific Writing**:
- Convert paper content to slides
- Simplify dense text
- Extract key findings
- Create visual abstracts

**With Data Visualization**:
- Simplify journal figures
- Recreate with larger labels
- Use progressive disclosure
- Emphasize key results

**With Research Lookup**:
- Find relevant papers
- Extract key citations
- Build background context
- Support claims with evidence

## Resources

**PowerPoint Tutorials**:
- Microsoft PowerPoint documentation
- PowerPoint design templates
- Scientific presentation examples

**Design Tools**:
- Color palette generators (Coolors.co)
- Contrast checkers (WebAIM)
- Icon libraries (Noun Project)
- Image editing (PowerPoint built-in, external tools)

**PPTX Skill Documentation**:
- `document-skills:pptx`: Main documentation (from anthropic-agent-skills marketplace)
- HTML to PPTX workflow: See html2pptx.md in marketplace skill
- Advanced OOXML editing: See ooxml.md in marketplace skill

## Quick Reference

### Common Slide Dimensions

- **16:9 aspect ratio**: 10" × 5.625" (720pt × 405pt)
- **4:3 aspect ratio**: 10" × 7.5" (720pt × 540pt)

### Measurement Units

- PowerPoint uses inches
- 72 points = 1 inch
- Position (x, y) from top-left corner
- Size (w, h) for width and height

### Font Size Guidelines

| Element | Minimum | Recommended |
|---------|---------|-------------|
| Title slide | 40pt | 44-54pt |
| Slide title | 28pt | 32-40pt |
| Body text | 18pt | 24-28pt |
| Caption | 14pt | 16-20pt |
| Footer | 10pt | 10-12pt |

### Color Usage

- **Backgrounds**: White or very light colors
- **Text**: Dark (black/dark gray) on light, or white on dark
- **Accents**: One or two accent colors max
- **Data**: Color-blind safe palettes (blue/orange)

## Troubleshooting

**Problem**: Text appears cut off
- **Solution**: Increase text box size or reduce font size

**Problem**: Figures are blurry
- **Solution**: Use higher resolution images (300 DPI)

**Problem**: Colors look different when projected
- **Solution**: Test with projector beforehand, use high contrast

**Problem**: File size too large
- **Solution**: Compress images, reduce image resolution

**Problem**: Animations not working
- **Solution**: Check PowerPoint version compatibility

## Conclusion

Effective PowerPoint presentations for science require:
1. Clear, simple design
2. Readable text (24pt+ body)
3. High-quality figures
4. Consistent formatting
5. Visual validation
6. Accessibility considerations

Use the pptx skill for programmatic creation and the visual review workflow to ensure professional quality before presenting.

