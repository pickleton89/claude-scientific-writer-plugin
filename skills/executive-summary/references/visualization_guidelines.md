# Visualization Guidelines for Executive Summaries

> Best practices for creating visual summaries and graphical abstracts in executive summaries.

## Purpose of Visual Summaries

A visual summary serves as a **cognitive shortcut** for busy readers. The brain processes visual information faster than text, making well-designed graphics essential for:

- **Screening relevance**: Readers quickly assess if the document matters to them
- **Anchoring key findings**: Visual evidence reinforces textual claims
- **Increasing retention**: Combined text + visual improves memory
- **Cross-cultural communication**: Graphics transcend language barriers

---

## When to Include a Visual Summary

**Always include when:**
- Document will be presented to diverse stakeholders
- Summary will appear in slide decks or board materials
- Distribution as standalone document (email, report excerpt)
- Technical content needs translation for non-specialists

**Consider omitting when:**
- Summary is extremely brief (<1 page)
- Data is primarily qualitative with no numeric findings
- Audience prefers text-heavy formats (legal, regulatory)

---

## Technical Specifications

### File Formats

| Format | Use Case | Advantages |
|--------|----------|------------|
| **PDF** | Print, documents | Vector, universal compatibility |
| **SVG** | Web, presentations | Vector, editable, small file size |
| **EPS** | Professional printing | Vector, CMYK support |

**Never use raster formats** (PNG, JPEG, GIF) for executive summary graphics—they pixelate when scaled.

### Resolution and Dimensions

| Output | Minimum DPI | Recommended |
|--------|-------------|-------------|
| Screen/web | 72 | 150 |
| Print | 300 | 600 |
| Poster/large format | 150 | 300 |

**Aspect ratios:**
- 16:9 for slide integration
- 4:3 for document embedding
- 1:1 for social media/thumbnail use

---

## Color Accessibility

### Avoid Red/Green Combinations

Approximately 8% of men and 0.5% of women have red-green color blindness. Never rely on red/green distinction to convey meaning.

### Recommended Palettes

**Viridis** (perceptually uniform, colorblind-safe):
```
#440154, #414487, #2A788E, #22A884, #7AD151, #FDE725
```

**Blue/Orange** (high contrast, universally distinguishable):
```
Blue: #1F77B4, #AEC7E8
Orange: #FF7F0E, #FFBB78
```

**ColorBrewer qualitative** (categorical data):
```
#377EB8, #984EA3, #FF7F00, #A65628, #F781BF
```
*Note: This modified palette excludes red/green to maintain accessibility.*

### Testing for Accessibility

Use tools like:
- Coblis Color Blindness Simulator
- Viz Palette (https://projects.susielu.com/viz-palette)
- Chrome DevTools color vision simulation

---

## Chart Selection

### Use Bar Charts For Comparisons

Bar charts are superior to pie charts because:
- Easy to compare lengths (vs. difficult-to-compare angles/areas)
- Can show more categories clearly
- Support negative values
- Allow for error bars and confidence intervals

### Avoid These Chart Types

| Type | Problem | Alternative |
|------|---------|-------------|
| **Pie charts** | Hard to compare slices; imprecise | Horizontal bar chart |
| **3D charts** | Distorts perception; adds chartjunk | 2D equivalent |
| **Donut charts** | Same problems as pie charts | Stacked bar chart |
| **Radar/spider** | Hard to read; misleading areas | Grouped bar chart |
| **Bubble charts** | Area perception is poor | Scatter with size legend |

### Recommended Chart Types

| Data Type | Recommended Chart |
|-----------|-------------------|
| Comparison (categories) | Horizontal bar chart |
| Time series | Line chart |
| Distribution | Histogram, box plot |
| Relationship | Scatter plot |
| Part-to-whole | Stacked bar chart |
| Ranking | Ordered horizontal bar |

---

## Data-Ink Ratio

Maximize the proportion of ink used to display actual data vs. decoration.

### Elements to Remove (Chartjunk)

- Background colors and gradients
- 3D effects and shadows
- Excessive gridlines
- Decorative borders
- Redundant labels
- Legend boxes (integrate labels directly)

### Elements to Keep

- Data points/bars
- Axis labels (minimal)
- Title (brief, informative)
- Direct data labels (when practical)
- Essential reference lines only

### Before/After Example

**Before (low data-ink ratio):**
- Gray background
- Heavy gridlines
- 3D bars with shadows
- Decorative legend box
- Redundant axis title

**After (high data-ink ratio):**
- White background
- No gridlines (or very light)
- Flat 2D bars
- Direct labels on bars
- Integrated title with takeaway message

---

## Caption Best Practices

Every figure must have a **self-contained caption** that allows understanding without reading the main text.

### Caption Structure

1. **Title**: Brief description of what the figure shows
2. **Methods note**: How data was collected/analyzed (1 sentence)
3. **Key finding**: The main takeaway from the figure
4. **Abbreviations**: Define any acronyms used

### Example Caption

> **Figure 1. Quarterly revenue growth exceeded projections by 23%.** Revenue data from Q1-Q4 2024 (n=4 quarters). Bars represent actual revenue; dashed line shows projected targets. All figures in millions USD. Error bars indicate 95% confidence intervals.

### Caption Length

- Minimum: 1 sentence (title + finding)
- Target: 2-3 sentences
- Maximum: 5 sentences (for complex figures)

---

## Typography for Figures

### Font Selection

| Element | Font | Size |
|---------|------|------|
| Title | Sans-serif (Arial, Helvetica) | 12-14pt |
| Axis labels | Sans-serif | 10-12pt |
| Data labels | Sans-serif | 8-10pt |
| Caption | Document body font | Match document |

### Why Sans-Serif?

- Better legibility on screens
- Cleaner at small sizes
- More accessible for readers with dyslexia
- Professional appearance in technical contexts

### Consistency Rules

- Use ONE font family throughout
- Maintain consistent sizing hierarchy
- Match document styling when embedded
- Never use decorative or script fonts

---

## Integration with Executive Summary

### Placement Options

**Option 1: Lead with visual**
```
[VISUAL SUMMARY]
[Hook/Problem paragraph]
[Rest of executive summary]
```

**Option 2: After the hook**
```
[Hook/Problem paragraph]
[VISUAL SUMMARY]
[Solution, Findings, Value, CTA]
```

**Option 3: Findings reinforcement**
```
[Hook, Solution paragraphs]
[VISUAL SUMMARY with key findings]
[Value, CTA paragraphs]
```

### Size Recommendations

| Document Type | Visual Size |
|---------------|-------------|
| 1-page summary | 1/4 to 1/3 of page |
| 2-page summary | 1/3 to 1/2 of first page |
| Slide deck | Full slide or half-slide |

---

## Quality Checklist

Before including any visual in an executive summary:

### Content
- [ ] Figure has ONE clear message (not multiple competing stories)
- [ ] Data is accurate and matches text claims
- [ ] Key finding is stated in title or caption
- [ ] Axes are labeled and units specified

### Format
- [ ] Vector format (PDF, SVG, EPS)
- [ ] Resolution appropriate for output medium
- [ ] Aspect ratio matches intended placement

### Accessibility
- [ ] No red/green color combinations
- [ ] Colors distinguishable in grayscale
- [ ] Sufficient contrast (text vs. background)
- [ ] Font sizes ≥8pt minimum

### Design
- [ ] No 3D effects or shadows
- [ ] Minimal gridlines (or none)
- [ ] No decorative elements (chartjunk)
- [ ] High data-ink ratio

### Caption
- [ ] Self-contained (understandable without main text)
- [ ] Includes key finding
- [ ] Defines abbreviations
- [ ] Appropriate length (2-3 sentences target)
