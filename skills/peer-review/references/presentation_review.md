# Presentation Review Guide

> Comprehensive criteria for reviewing scientific presentations and slide decks.

---

## Critical: Image-Based Review Workflow

**Always convert presentation PDFs to images before reviewing** - direct PDF reading causes buffer overflow errors and misses visual formatting issues.

**Required Process:**
1. Convert PDF to images using Python:
   ```bash
   python {baseDir}/scripts/pdf_to_images.py presentation.pdf review/slide --dpi 150
   # Creates: review/slide-001.jpg, review/slide-002.jpg, etc.
   ```
2. Read and inspect EACH slide image file sequentially
3. Document issues with specific slide numbers
4. Provide feedback on visual formatting and content

**Print when starting review:**
```
[HH:MM:SS] PEER REVIEW: Presentation detected - converting to images for review
[HH:MM:SS] PDF REVIEW: Using image-based inspection workflow
```

---

## Evaluation Criteria

### Visual Design and Readability

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| Body text size | ≥18pt (ideally 24pt+) | Readable from back of room |
| Text-background contrast | 4.5:1 minimum, 7:1 preferred | WCAG accessibility |
| Color scheme | Professional, colorblind-accessible | Test with color blindness simulator |
| Visual consistency | Uniform across all slides | Fonts, colors, positioning |
| White space | Adequate (not cramped) | Breathing room for content |

### Layout and Formatting Checklist

For EVERY slide image, verify:

- [ ] No text overflow or truncation at slide edges
- [ ] No element overlaps (text over images, overlapping shapes)
- [ ] Titles consistently positioned
- [ ] Content properly aligned
- [ ] Bullets and text not cut off
- [ ] Figures fit within slide boundaries
- [ ] Captions and labels visible and readable

### Content Quality

| Criterion | Target | Flag If |
|-----------|--------|---------|
| Ideas per slide | 1 main idea | Overloaded with concepts |
| Bullet points | 3-6 per slide max | Wall of text |
| Bullet length | 5-7 words each | Full sentences |
| Figure complexity | Simplified, clear | Copy-pasted from papers |
| Data labels | Large, readable | Too small for projection |
| Citations | Present, formatted | Missing or inconsistent |
| Results coverage | 40-50% of slides | Dominated by intro/methods |

### Structure and Flow

**Required elements:**
- [ ] Title slide with authors, affiliation, date
- [ ] Clear narrative arc (intro → methods → results → discussion)
- [ ] Logical progression between slides
- [ ] Conclusions slide summarizing key findings
- [ ] Acknowledgments/funding slide at end

**Content distribution:**
- Slide count ≈ 1 per minute of talk duration
- Introduction cites 3-5 relevant background papers
- Discussion cites 3-5 comparison papers

### Scientific Content

- [ ] Research question clearly stated
- [ ] Methods adequately summarized (appropriate detail level)
- [ ] Results presented logically with clear visualizations
- [ ] Statistical significance indicated appropriately
- [ ] Conclusions supported by data shown
- [ ] Limitations acknowledged where appropriate
- [ ] Future directions or broader impact discussed

---

## Issue Classification

### Critical Issues (Must Fix)

| Issue | Why Critical |
|-------|--------------|
| Text overflow making content unreadable | Audience cannot see information |
| Font sizes <18pt | Illegible from audience distance |
| Element overlaps obscuring data | Key information hidden |
| Insufficient contrast | Text hard to read |
| Figures too complex or illegible | Cannot interpret visualizations |
| No citations | Unsupported scientific claims |
| Slide count drastically mismatched to duration | Talk cannot be delivered |

### Major Issues (Should Fix)

| Issue | Impact |
|-------|--------|
| Inconsistent design across slides | Unprofessional appearance |
| Too much text (walls of text) | Audience reads instead of listens |
| Poorly simplified figures | Axis labels too small, details lost |
| Cramped layout | Cognitive overload |
| Missing key structural elements | Incomplete presentation |
| Poor color choices | Accessibility barriers |
| Minimal results content (<30% of slides) | Insufficient data presentation |

### Minor Issues (Suggestions)

- Could use more visuals/diagrams
- Some slides slightly text-heavy
- Minor alignment inconsistencies
- Could benefit from more white space
- Additional citations would strengthen claims
- Color scheme could be more modern

---

## Review Report Format

### Summary Statement

Include:
- Overall impression of presentation quality
- Appropriateness for target audience and duration
- Key strengths (visual design, content, clarity)
- Key weaknesses (formatting issues, content gaps)
- Recommendation (ready to present, minor revisions, major revisions)

### Layout Issues (By Slide Number)

Format issues as:
```
Slide 3: Text overflow - bullet point 4 extends beyond right margin
Slide 7: Element overlap - figure overlaps with caption text
Slide 12: Font size - axis labels too small to read from distance
Slide 18: Alignment - title not centered
```

### Content and Structure Feedback

Address:
- Adequacy of background context and citations
- Clarity of research question and objectives
- Quality of methods summary
- Effectiveness of results presentation
- Strength of conclusions and implications

### Design and Accessibility

- Overall visual appeal and professionalism
- Color contrast and readability
- Colorblind accessibility
- Consistency across slides

### Timing and Scope

- Whether slide count matches intended duration
- Appropriate level of detail for talk type
- Balance between sections

---

## Example Review Process Log

```
[14:30:00] PEER REVIEW: Starting review of presentation
[14:30:05] PEER REVIEW: Presentation detected - converting to images
[14:30:10] PDF REVIEW: Running pdf_to_images.py on presentation.pdf
[14:30:15] PDF REVIEW: Converted 25 slides to images in review/ directory
[14:30:20] PDF REVIEW: Inspecting slide 1/25 - title slide
[14:30:25] PDF REVIEW: Inspecting slide 2/25 - introduction
...
[14:35:40] PDF REVIEW: Inspecting slide 25/25 - acknowledgments
[14:35:45] PDF REVIEW: Completed image-based review
[14:35:50] PEER REVIEW: Found 8 layout issues, 3 content issues
[14:35:55] PEER REVIEW: Generating structured feedback by slide number
```

---

## Cross-References

- **scientific-slides**: For creating presentations that meet these standards
- **latex-posters**: Similar visual quality criteria for posters
- **visual-design**: Design principles underlying these criteria
