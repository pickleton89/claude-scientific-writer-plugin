---
name: visual-design
version: 2.3.0
description: "Design philosophy and publication specifications for scientific visuals. Provides guidance on typography, color, layout, accessibility, and journal requirements. Delegates implementation to specialized skills."
allowed-tools: [Read, Glob, Write]
quantification-reference: "../QUANTIFICATION_THRESHOLDS.md"
---

# Visual Design for Scientific Communication

<overview>
Apply intentional design thinking to create publication-quality scientific visuals that avoid generic "default matplotlib" aesthetics. This skill provides the design philosophy layer—establishing visual direction, ensuring accessibility, and meeting publication standards—while delegating code implementation to specialized skills like `plotting-libraries` and `scientific-schematics`.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Planning visual strategy for a manuscript or presentation
- Need guidance on typography, color, or layout decisions
- Checking accessibility requirements (colorblind-safe, contrast)
- Determining publication specifications for a specific journal
- Establishing consistent visual identity across figures
- Reviewing design quality before submission

Do NOT use this skill when:
- Writing matplotlib/seaborn/R code → use `plotting-libraries`
- Generating diagrams → use `scientific-schematics`
- Creating photorealistic images → use `generate-image`
- Building slides or posters → use `scientific-slides`, `latex-posters`, `pptx-posters`
</when_to_use>

<prerequisites>
## Prerequisites

Before using this skill, ensure:
- [ ] Target publication venue identified (journal, conference, or internal)
- [ ] Source data or figures ready for design planning
- [ ] Access to brand guidelines if organizational standards apply (see `../oligon-brand/` for Oligon brand)
- [ ] Knowledge of target audience (reviewers, conference attendees, general public)

**Environment:**
- No special tools required (design philosophy skill)
- Implementation delegated to `plotting-libraries` or `scientific-schematics`
- For journal specifications, verify against target venue guidelines
</prerequisites>

<decision_framework>
## Decision Matrix

### Design Direction Selection

```
Who is your primary audience?
│
├─ Journal Reviewers / Academic Peers
│  │
│  ├─ Data-heavy figures → Precise, restrained, minimal decoration
│  │  • Maximum clarity over visual impact
│  │  • Publication specs: exact dimensions, 300 DPI
│  │  • Conservative color palette
│  │
│  └─ Conceptual figures → Clean, professional, publishable
│     • Focus on clarity of scientific message
│     • Standard typography (Helvetica/Arial)
│
├─ Conference Audience
│  │
│  ├─ Poster presentation → Bold, scannable in 3 seconds
│  │  • Large fonts (≥24pt body, ≥48pt headers)
│  │  • High contrast colors
│  │  • Visual hierarchy guides viewer
│  │
│  └─ Talk slides → Impactful, one idea per slide
│     • Minimal text, maximum visual
│     • Dark backgrounds can work well
│
├─ General Public / Media
│  │
│  └─ Accessible, engaging, memorable
│     • Avoid jargon in labels
│     • Use visual metaphors
│     • Higher visual impact acceptable
│
└─ Internal Team
   │
   └─ Functional, clear, quick to produce
      • Standard templates acceptable
      • Focus on information over aesthetics
```

### Chart Type Selection

| Data Type | ✓ Recommended | ✗ Avoid |
|-----------|---------------|---------|
| Comparison (few categories) | Bar chart, dot plot | Pie chart (hard to compare) |
| Comparison (many categories) | Horizontal bar, heatmap | 3D charts (distorted perception) |
| Time series | Line chart, area chart | Bar chart (implies discrete) |
| Distribution | Histogram, violin, box plot | Bar chart of means only |
| Relationship (2 variables) | Scatter plot | Connected scatter (implies order) |
| Relationship (3 variables) | Scatter + color/size | 3D scatter (depth perception poor) |
| Part-to-whole | Stacked bar, treemap | Pie chart (if >5 segments) |
| Flow/Network | Sankey, network graph | Tables |

### Color Palette Selection

| Context | Palette Type | Example Use |
|---------|--------------|-------------|
| Continuous data (low→high) | Sequential | Expression levels, intensity |
| Continuous data (diverging) | Diverging | Fold change (up/down regulation) |
| Discrete groups (≤5) | Categorical | Treatment groups |
| Discrete groups (>5) | Extended categorical | Multiple cell types |
| Binary comparison | Two-color | Control vs treatment |
| Highlighting | Neutral + accent | One emphasized element |

**Colorblind-Safe Palettes:**

| Palette | Colors | Best For |
|---------|--------|----------|
| Okabe-Ito | 8 colors | Categorical data, general use |
| Viridis | Continuous | Sequential data |
| Cividis | Continuous | Sequential, colorblind-optimized |
| Blue-Orange | 2 colors | Binary comparisons |
| Magenta-Green | 2 colors | Binary (alternative to red-green) |

</decision_framework>

<workflow>
## Workflow

### Stage 1: Context Analysis

**Objective:** Understand requirements and constraints before designing

**Steps:**
1. Identify target audience (reviewers, conference, public)
2. Determine output format (journal figure, poster, slides)
3. Check venue-specific requirements (dimensions, format, DPI)
4. Identify brand guidelines if applicable
5. Assess accessibility requirements

**Exit Criteria:**
- [ ] Audience identified (academic/conference/public/internal)
- [ ] Output format specified with dimensions
- [ ] Venue requirements documented (if applicable)
- [ ] Accessibility requirements noted (colorblind, contrast)

**Context Questions:**
1. **Story**: What single insight should the viewer take away?
2. **Audience**: What level of expertise? What are their expectations?
3. **Constraints**: Size limits? Color restrictions? File format requirements?
4. **Differentiation**: What will make this memorable?

---

### Stage 2: Visual Strategy

**Objective:** Establish clear design direction before implementation

**Steps:**
1. Select chart type(s) from decision matrix
2. Choose color palette based on data type
3. Define typography hierarchy
4. Plan layout and composition
5. Document visual strategy for consistency

**Exit Criteria:**
- [ ] Chart type(s) selected with rationale
- [ ] Color palette chosen (≤7 colors for categorical)
- [ ] Typography defined (max 2 font families)
- [ ] Layout grid established
- [ ] Visual strategy documented for multi-panel figures

**Typography Hierarchy:**

| Element | Size Range | Style | Purpose |
|---------|------------|-------|---------|
| Figure title | 12-14pt | Bold | Establish context |
| Axis titles | 10-12pt | Regular | Label dimensions |
| Axis labels | 8-10pt | Regular | Show values |
| Annotations | 8-9pt | Regular/Italic | Add context |
| Legend | 8-10pt | Regular | Decode colors/shapes |

---

### Stage 3: Accessibility Check

**Objective:** Ensure visual is accessible to all viewers

**Steps:**
1. Verify colorblind-safe palette used
2. Check contrast ratios (≥4.5:1 for text)
3. Add redundant encoding (shapes + colors)
4. Test at final reproduction size
5. Convert to grayscale to verify contrast

**Exit Criteria:**
- [ ] No red/green only distinctions
- [ ] Contrast ratio ≥4.5:1 for all text
- [ ] Redundant encoding present (not color-only)
- [ ] Readable at final size (≥7pt minimum)
- [ ] Works in grayscale

**Accessibility Checklist (WCAG 2.1 AA Compliance):**

| Check | Minimum | Target | Tool to Verify |
|-------|---------|--------|----------------|
| Colorblind safe | Distinguishable by ≥2 CVD types | All 3 CVD types | Color Oracle, Coblis |
| Text contrast | 4.5:1 | 7:1 | WebAIM Contrast Checker |
| Large text contrast | 3:1 | 4.5:1 | WebAIM Contrast Checker |
| Non-text contrast | 3:1 | 4.5:1 | WebAIM Contrast Checker |
| Redundant coding | 1 alternative | 2 alternatives | Remove color mentally |
| Font size | ≥7pt at final | ≥8pt at final | Measure in layout |
| Line weight | ≥0.5pt at final | ≥1.0pt at final | Measure in layout |
| Color difference (ΔE) | ≥20 CIE2000 | ≥30 CIE2000 | Color difference calculator |

---

### Stage 4: Implementation Handoff

**Objective:** Provide clear specifications for implementation skill

**Steps:**
1. Compile visual specifications document
2. Hand off to appropriate skill:
   - Plots/charts → `plotting-libraries`
   - Diagrams → `scientific-schematics`
   - AI images → `generate-image`
3. Review implementation against specifications
4. Iterate if needed

**Exit Criteria:**
- [ ] Specifications document complete
- [ ] Implementation skill identified
- [ ] Design intent communicated
- [ ] Review criteria established

**Specifications Template:**
```markdown
## Figure Specifications

**Dimensions:** {{width}} × {{height}} mm (journal column width)
**Resolution:** 300 DPI
**Color Mode:** RGB (will convert to CMYK for print)

**Color Palette:**
- Primary: {{hex code}}
- Secondary: {{hex code}}
- Accent: {{hex code}}
- Background: {{hex code}}

**Typography:**
- Font: {{font family}}
- Axis labels: {{size}}pt
- Legend: {{size}}pt

**Accessibility:**
- Colorblind-safe palette: Yes
- Redundant encoding: Shapes for groups
```

---

### Stage 5: Quality Review

**Objective:** Verify final visual meets design criteria

**Steps:**
1. Check against original design specifications
2. Verify publication requirements met
3. Run accessibility verification
4. Confirm brand consistency (if applicable)
5. Final approval for submission

**Exit Criteria:**
- [ ] Matches design specifications
- [ ] Meets publication requirements
- [ ] Passes accessibility checks
- [ ] Consistent with other figures in document
- [ ] Ready for submission

</workflow>

<success_criteria>
## Success Criteria

> **Reference:** See `../QUANTIFICATION_THRESHOLDS.md` §2 (Visual Quality) and §7 (Quality Rubrics) for shared thresholds.

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Contrast ratio (text) | 4.5:1 | 7:1 | 10:1 |
| Contrast ratio (large text ≥18pt) | 3:1 | 4.5:1 | 7:1 |
| Non-text contrast | 3:1 | 4.5:1 | 7:1 |
| Minimum font size | 7pt | 8pt | 10pt |
| Color count (categorical) | ≤10 | ≤7 | ≤5 |
| Line weight | 0.5pt | 1.0pt | 1.5pt |
| Resolution (print) | 150 DPI | 300 DPI | 600 DPI |
| Resolution (screen) | 72 DPI | 150 DPI | 300 DPI |

**WCAG 2.1 Accessibility Compliance:**

| Level | Requirements | Use Case |
|-------|--------------|----------|
| Level A | Minimum accessibility | Internal drafts |
| Level AA | Standard accessibility (4.5:1 contrast, focus visible) | Publication, presentations |
| Level AAA | Enhanced accessibility (7:1 contrast, sign language) | Public-facing, web |

**Design Quality Scoring (10-point scale):**

| Criterion | 0 (Fail) | 1 (Acceptable) | 2 (Excellent) |
|-----------|----------|----------------|---------------|
| Intentionality | Default styling | Mostly customized | Every choice purposeful |
| Clarity | >30s to understand | <10s to understand | <5s to understand |
| Consistency | Inconsistent styling | Minor variations | Fully consistent |
| Accessibility | Fails WCAG A | Meets WCAG AA | Meets WCAG AAA |
| Brand alignment | Off-brand | Mostly aligned | Perfect alignment |

**Score Interpretation:**
- **0-4:** Needs major revision
- **5-6:** Acceptable for internal use
- **7-8:** Publication ready
- **9-10:** Exemplary design

**Completion Checklist:**
- [ ] Single clear message communicated
- [ ] Appropriate for target audience
- [ ] No default/generic styling
- [ ] Accessibility requirements met (WCAG AA minimum)
- [ ] Publication specifications followed
- [ ] Consistent with other document figures
- [ ] Brand guidelines applied (if applicable)
- [ ] Design quality score ≥7/10

</success_criteria>

<scope>
## Scope

**In Scope:**
- Design philosophy and visual strategy
- Typography, color, and layout guidance
- Accessibility requirements and verification
- Publication specifications by venue
- Brand integration guidance
- Design quality review

**Out of Scope** (use specialized resources):
- matplotlib/seaborn/ggplot2 code → use `plotting-libraries`
- Diagram generation → use `scientific-schematics`
- Photorealistic images → use `generate-image`
- Slide creation → use `scientific-slides`
- Poster creation → use `latex-posters`, `pptx-posters`

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Default Syndrome

**Anti-pattern:**
Using tool defaults without customization—gray backgrounds, thin lines, small fonts, default colors.

**Solution:**
Every visual choice should be intentional:
- "Why this color?" → Brand palette / colorblind-safe / emphasizes key data
- "Why this font size?" → Legible at final reproduction size
- "Why this layout?" → Guides viewer to the key insight

---

### 2. Rainbow Colormap for Sequential Data

**Anti-pattern:**
Using rainbow/jet colormap for continuous data—perceptually uneven, not colorblind-safe.

**Solution:**
Use perceptually uniform colormaps:
- Viridis, Plasma, Magma for sequential data
- Cividis for colorblind optimization
- Diverging colormaps (RdBu, PuOr) for data with meaningful center

---

### 3. Color-Only Encoding

**Anti-pattern:**
Distinguishing groups by color alone—fails for colorblind viewers and grayscale printing.

**Solution:**
Add redundant encoding:
- Different shapes for scatter plot groups
- Different line styles (solid, dashed, dotted)
- Direct labels on the plot
- Patterns/hatching for bar charts

---

### 4. Cramming Too Much

**Anti-pattern:**
Putting too many elements, too much data, or too many panels in one figure.

**Solution:**
Follow data-ink ratio principle:
- Remove chartjunk (excessive gridlines, borders, backgrounds)
- Limit to 1 main message per figure
- Break complex figures into multiple panels
- Use supplementary figures for additional data

---

### 5. Inconsistent Styling

**Anti-pattern:**
Different fonts, colors, or sizing across panels or figures in the same document.

**Solution:**
Create style guide before starting:
- Document color palette with hex codes
- Specify typography hierarchy
- Use consistent axis ranges when comparing
- Create template/style file for reuse

---

### 6. Truncated Axes

**Anti-pattern:**
Starting y-axis above zero to exaggerate small differences.

**Solution:**
- Start bar charts at zero
- Clearly indicate axis breaks if necessary
- Use appropriate chart type for the comparison
- Show full range with inset for detail if needed

---

### 7. 3D Charts for 2D Data

**Anti-pattern:**
Using 3D effects (3D bar charts, 3D pie charts) that distort perception.

**Solution:**
- Use 2D representations for 2D data
- 3D only for actual 3D data (volumetric, spatial)
- If 3D needed, use isometric projections with care

</anti_patterns>

<error_handling>
## Error Handling

### Design Fails Journal Review

**Symptoms:** Editor requests figure revisions; reviewer comments on clarity or format

**Resolution:**
1. Review specific feedback against `references/publication_specs.md`
2. Identify if issue is technical (DPI, format, dimensions) vs. design (clarity, accessibility)
3. For technical issues: adjust export settings and re-export
4. For design issues: revisit Stage 2 (Visual Strategy) with new constraints
5. Re-run accessibility checks before resubmission

---

### Color Count Exceeds Palette

**Symptoms:** More data categories than recommended colors (>5 categorical)

**Resolution:**
1. **First choice:** Restructure figure using faceting/small multiples
2. **Second choice:** Group categories hierarchically (e.g., combine similar conditions)
3. **Third choice:** Use shapes/patterns as primary encoding, color as secondary
4. **Last resort:** Extend to Cycle 4 (4 colors) with mandatory shape encoding

**Never:** Use more than 5-7 colors in a single panel—redesign instead.

---

### Accessibility Conflict with Brand

**Symptoms:** Brand colors fail WCAG contrast checks or colorblind simulation

**Resolution:**
1. Check if darker/lighter variants of brand colors pass (e.g., Dark Teal #0F5D7D instead of Brand Blue #2DB2E8 for small text)
2. Add redundant encoding (shapes, patterns, direct labels)
3. Use brand colors for large elements only (where 3:1 contrast suffices)
4. Document deviation with justification in figure notes

---

### Venue Requirements Unknown

**Symptoms:** No clear target publication; designing speculatively

**Resolution:**
1. Design for Nature single-column (89mm / 3.5") as conservative default
2. Use 300 DPI, PDF vector format
3. Apply WCAG AA accessibility standards
4. Document assumptions in specifications for later adjustment
5. When venue is determined, verify against `references/publication_specs.md`

---

### Figure Dimensions Exceed Venue Limits

**Symptoms:** Complex figure doesn't fit in journal column width

**Resolution:**
1. Split into multiple panels across pages (Figure 1A-D, Figure 2A-D)
2. Move supplementary data to Extended Data or Supplementary Figures
3. Reduce complexity: fewer subpanels, larger individual panels
4. Consider landscape orientation if journal permits

---

### Inconsistent Styling Across Figures

**Symptoms:** Figures in same manuscript have different fonts, colors, or sizing

**Resolution:**
1. Create a style specification document before starting any figures
2. Document: color palette (hex codes), font family, font sizes, line weights
3. Review all figures together at 100% zoom before submission
4. Use the same implementation skill and code template for all figures

</error_handling>

<templates>
## Output Templates

See `references/output_templates.md` for:
- **Visual Specifications Document** — Template for documenting design decisions
- **Pre-Submission Design Checklist** — Quality verification before submission
- **Quick Specification Card** — Rapid documentation format

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `plotting-libraries` | Use for matplotlib/seaborn/R implementation after design decisions made |
| `scientific-schematics` | Use for diagram generation; visual-design provides principles |
| `generate-image` | Use for photorealistic images; visual-design provides aesthetics guidance |
| `scientific-slides` | Visual-design principles apply to presentation design |
| `latex-posters` / `pptx-posters` | Visual-design principles apply to poster design |
| `oligon-brand` | **Brand implementation** — provides Oligon-specific colors, typography, and logos. For programmatic access, load `oligon-brand/tokens/brand-tokens.json`. For matplotlib, use `oligon-brand/adapters/matplotlib_adapter.py`. |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Brand Integration:**
When Oligon brand standards apply:
1. Load `oligon-brand` tokens first
2. Apply `visual-design` principles
3. Implement with `plotting-libraries` or format-specific skill

**Typical Workflow:**
1. `visual-design` → establish design direction and specifications
2. `oligon-brand` → load brand colors and apply style (if applicable)
3. `plotting-libraries` or `scientific-schematics` → implement visuals
4. `visual-design` → review quality before submission

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `../oligon-brand/references/brand-colors-full.md` | Oligon brand color palette definitions (V4) |
| `../oligon-brand/tokens/brand-tokens.json` | Machine-readable brand tokens for programmatic access |
| `references/OUTPUT_FORMATS.md` | Format-specific guidance for figures, reports, presentations |
| `references/publication_specs.md` | Journal-specific requirements and export settings |
| `references/output_templates.md` | Reusable templates for specifications and checklists |

### Publication Requirements Quick Reference

| Journal | Single Column | Double Column | Max DPI | Format |
|---------|---------------|---------------|---------|--------|
| Nature | 89 mm | 183 mm | 300 | PDF/EPS/TIFF |
| Science | 55 mm | 175 mm | 300 | PDF/EPS |
| Cell | 85 mm | 178 mm | 300 | PDF/EPS/TIFF |
| PNAS | 87 mm | 178 mm | 300 | PDF/EPS/TIFF |
| eLife | 139 mm | 178 mm | 300 | PDF/PNG |

### External Resources

**Accessibility:**
- Okabe-Ito Palette: https://jfly.uni-koeln.de/color/
- Color Oracle: https://colororacle.org/
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Coblis Colorblindness Simulator: https://www.color-blindness.com/coblis-color-blindness-simulator/

**Typography:**
- Google Fonts: https://fonts.google.com/
- Font combinations: https://fontpair.co/

**Data Visualization Theory:**
- Edward Tufte principles
- Grammar of Graphics (Wilkinson)

</references>
