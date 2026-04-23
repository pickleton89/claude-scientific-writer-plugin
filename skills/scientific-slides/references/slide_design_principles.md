# Slide Design Principles for Scientific Presentations

## Overview

Effective slide design enhances comprehension, maintains audience attention, and ensures your scientific message is communicated clearly. This guide covers visual hierarchy, typography, color theory, layout principles, and accessibility considerations for creating professional scientific presentations.

---

## Expert Principles

> These principles separate competent from excellent execution.

### Five Core Rules

1. **Visual Primacy**: Slides are visual aids, not teleprompters. Every slide needs a dominant visual element (figure, diagram, image)—text supports the visual, never replaces it.

2. **One Idea, One Slide**: Cognitive load is the enemy. Each slide communicates exactly one concept. If you're explaining two things, you need two slides.

3. **Narrative Arc Over Data Dump**: A presentation is a story with hook, conflict, and resolution. Results without context are forgettable; context without story is boring.

4. **Audience-Calibrated Depth**: Expert audiences need different slides than general audiences. Tailor complexity, jargon, and assumed knowledge to who's actually in the room.

5. **You Are the Presentation**: Slides enhance your talk; they don't replace it. If slides could stand alone, send a PDF instead.

### Decision Framework

| Situation | Action |
|-----------|--------|
| Complex concept to explain | Split across 2-3 slides with progressive build, not one dense slide |
| Running over time in practice | Cut content slides, never conclusions—end strong |
| Multiple results to present | Lead with most important finding; save others for backup slides |
| Technical audience | Use field terminology; skip basic definitions |
| Mixed/general audience | Define terms; use analogies; emphasize "so what" |
| Data-heavy figure from paper | Simplify: fewer panels, larger labels, direct annotations |
| Q&A anticipated on specific topic | Prepare dedicated backup slide with detailed data |

### Concrete Patterns

**Hook-First Opening**
- Start with compelling question, surprising fact, or real-world problem—not "Today I'll present..."
- Captures attention in first 60 seconds before audience decides to tune out
- Establishes why they should care

**Visual-Text Hierarchy**
- Large figure occupies 60-70% of slide
- 3-4 word headline above
- 2-3 bullet annotations below
- Eye goes to visual first, text provides interpretation

**Checkpoint Pacing**
- 15-minute talk example: Slide 5 at 4min, Slide 10 at 8min, Conclusions at 12min
- Enables real-time adjustment
- Prevents rushing final section where key messages live

### Anti-Patterns

- **Never** use more than 6 words per bullet—if you need more, you're writing a paragraph
- **Never** present a figure without verbally explaining what the axes mean
- **Never** skip the conclusion to stay on time—cut earlier content instead
- **Never** include slides you can't explain in your own words without reading
- **Never** use red-green color combinations—8% of male audience is colorblind
- **Never** rely on animations for critical information—they may fail on presentation day

### Quality Signals: Good Enough vs. Excellent

| Good Enough | Excellent |
|-------------|-----------|
| Reading-floor fonts (body ≥18pt, axis ≥14pt) | Projection-floor fonts (body ≥24pt, headline ≥32pt, axis ≥18pt) with AAA contrast (7:1) |
| Consistent template | Intentional design system with visual variety in layouts |
| Includes figures | Figures dominate slides; text annotates visuals |
| Practiced once | Practiced 3+ times with timing checkpoints; recorded and reviewed |
| Finishes on time | Finishes 1-2 minutes early with time for strong conclusion |
| Answers questions | Has backup slides ready for anticipated questions |
| Clear structure | Explicit narrative arc with memorable hook and takeaway |
| Citation included | Research context established; 5-10 key papers cited appropriately |

### Quick Quality Check

1. Does every slide have a dominant visual element (figure, diagram, image)?
2. Can each slide be explained in under 60 seconds?
3. Is text limited to 3-4 bullets with 4-6 words each?
4. Have I practiced at least 3 times with a timer?
5. Do I finish 1-2 minutes early in practice runs?
6. Are backup slides ready for the 3-5 most likely questions?

**When In Doubt:** If you can't explain the slide in 60 seconds without reading it, simplify it.

---

## Per-Slide Structure and Assertion-Evidence

### Prefer an assertion headline

Make the slide title a full-sentence declarative **takeaway**, not a topic label.

- ✅ "Compound X shows 12-fold selectivity over the closest off-target at 100 nM"
- ❌ "Selectivity data"

This is the **assertion-evidence** structure (Alley 2013). Garner and Alley (2013) showed in a controlled 110-student study that assertion-evidence slides produced comprehension scores of ~**59% vs 42%** for topic-subtitle slides (p < 0.01), reduced major misconceptions by about tenfold, lowered perceived cognitive load, and increased delayed recall. Doumont (2009) gives the same prescription in a different vocabulary: slide titles should deliver a message, captions should make an assertion rather than name a figure, and headings, visuals, and verbal delivery should be mutually reinforcing.

**When NOT to mandate assertion-evidence:** reference slides, disclosure and conflict-of-interest slides, acknowledgments, methods overviews setting up three subsequent results slides, and discussion slides whose purpose is to pose an open question to an SAB or journal-club audience. For these, a neutral topic label or interrogative title is correct. **On KOL slide kits**, MLR review often rejects assertion headlines that could be read as promotional claims; follow the MLR-approved wording. **In journal clubs**, the defensible default is "Figure 2: knockout phenotype" with a critical takeaway bullet beneath rather than an embedded assertion.

**The rule to carry into every slide:** if a slide has a takeaway, state it in words somewhere the reader cannot miss.

### Two audit heuristics — the 5-second rule and the Squint Test

**The 5-second rule.** A reader landing on the slide should be able to identify the main takeaway within five seconds. If they cannot, the headline has failed its job.

**The Squint Test.** Blur your vision and look at the slide; the headline's position, weight, and visual dominance should clearly mark it as the primary entry point even when the text is unreadable.

Both heuristics are quick to apply during review and catch headlines that are technically assertions but functionally labels.

### Write for the ear on projected slides

On projected slides shown during a live talk, the audience is **listening**, not reading — and reading and listening compete for the same cognitive channel. A slide packed with paragraph-length prose forces a choice: the audience stops listening so they can read, or they stop reading and miss what the slide was put there to convey. Dense journal-abstract phrasing on a projected slide is the most common form of this failure.

**For projection use:** compose slide text the way you would **speak** it — short phrases, active verbs, terminology the room actually uses — and let the presenter's voice carry the connective tissue. An assertion headline that is genuinely a full sentence is tolerable on a projected slide because the reader can absorb one sentence during an initial glance. What fails is the secondary bullet list of three prose sentences beneath the headline.

**For reading decks**, the opposite constraint applies — the reader is reading, not listening, and the caption that carries the presenter's voice earns its place. This is one of the cleanest examples of where projection-deck and reading-deck rules diverge; dual-purpose decks compose toward the reading-deck side (see `presentation_structure.md`).

### The one-minute budget

A typical scientific content slide should take about **one minute** to discuss during a live talk (Naegle et al. 2021). If you cannot, the slide is doing too much and should be split.

**Secondary sanity checks** on a single content slide:
- Not more than **two sentences of assertion** (the headline + optional subtitle)
- Not more than **four distinct visual panels**

Both thresholds are rough proxies for the one-minute test; either one being exceeded is a reason to look hard at whether the slide is doing too much.

**Do not apply Kawasaki's 10/20/30 rule (2005) literally to scientific decks:** 30-point minimum type is too large for figure legends, and 10 slides cannot cover the risk surface a life-science investor or partner underwrites. Use that rule as a reminder to cut fluff, not as a floor.

**Projection vs reading:**
- **Projection deck** — the one-minute test is a strict budget. If you cannot walk through a slide in about a minute, split it.
- **Reading deck** — the one-minute test loosens. A reader can dwell on a dense panel for as long as the evidence rewards; splitting a canonical multi-panel figure for pacing actively hurts comprehension.

### When to split a dense slide and when to keep it

**Split when:**
- Two subplots answer two different questions
- A reader would need to re-caption to follow the argument
- The slide carries more than one takeaway worth stating in words

**Keep together when:**
- Panels are parts of the same comparison that must be seen simultaneously (e.g., a dose-response curve beside a selectivity panel sharing the compound set)
- The figure is the canonical published version and separation would break a reviewer's mental model

Density is not the enemy. Uninterpretable density is.

**Projection deck** tilts toward splitting. **Reading deck** tilts toward keeping together.

### Animation and progressive disclosure — default position is "none"

The default position on animation for scientific content: **none**.

Animations introduce technical risk (fail to advance, desynchronize with the presenter, render oddly across PowerPoint versions and operating systems), they are an accessibility liability for viewers with photosensitive conditions or who rely on screen readers, and decorative animations ("Fly In," "Bounce," "Fade through black") signal amateurism and slow the pacing regardless of intent.

**The one defensible exception:** progressive reveal of a multi-panel figure in the order the argument depends on — controls first, then the treatment condition, then the key comparison — and only when the presenter has rehearsed the reveals as part of the narrative such that each reveal lands on a specific sentence.

**If you must use a reveal:**
- Confine to *Appear* and *Fade* with durations at 0.25–0.5 seconds
- Avoid every emphasis and exit animation on data slides (they break the Tufte data-ink principle)
- Never use an animation whose sole effect is aesthetic

**Progressive disclosure does NOT survive PDF export.** A PDF flattens to the final animated state, which means a reader receiving the asynchronous deck sees all four panels at once. The reliable dual-purpose workaround: **duplicate the slide** — one slide per build state — so the PDF preserves the progressive structure for the reader and the live deck uses Section Zoom to skip the duplicates during presentation.

---

## Core Design Principles

### 1. Simplicity and Clarity

**The Fundamental Rule**: Each slide should communicate ONE main idea.

**Why It Matters**:
- Audiences can only process limited information at once
- Complexity causes cognitive overload
- Simple slides are remembered; busy slides are forgotten

**Application**:
- ✅ One message per slide
- ✅ Minimal text (audiences read OR listen, not both simultaneously)
- ✅ Clear visual focus
- ✅ Generous white space
- ❌ Avoid cramming multiple concepts onto one slide

**Example Comparison**:
```
BAD: Single slide with:
- 3 different graphs
- 8 bullet points
- 2 tables
- Dense caption text

GOOD: Three separate slides:
- Slide 1: First graph with 2-3 key points
- Slide 2: Second graph with interpretation
- Slide 3: Summary table with highlighted finding
```

### 2. Visual Hierarchy

Guide attention to the most important elements through size, color, and position.

**Hierarchy Levels**:
1. **Primary**: Main message or key data (largest, highest contrast)
2. **Secondary**: Supporting information (medium size)
3. **Tertiary**: Details and labels (smaller, lower contrast)

**Techniques**:

**Size**:
- Title: Largest (36-54pt)
- Key findings: Large (24-32pt)
- Supporting text: Medium (18-24pt)
- Labels and notes: Smallest but legible (14-18pt)

**Color**:
- High contrast for key elements
- Accent colors for emphasis
- Muted colors for background or secondary info

**Position**:
- Top-left or top-center: Primary content (Western reading pattern)
- Center: Focal point for key visuals
- Bottom or sides: Supporting details

**Weight**:
- Bold for emphasis on key terms
- Regular weight for body text
- Light weight for de-emphasized content

### 3. Consistency

Maintain visual consistency throughout the presentation.

**Elements to Keep Consistent**:
- **Fonts**: Same font family for all slides
- **Colors**: Defined color palette (3-5 colors)
- **Layouts**: Similar slides use same structure
- **Spacing**: Margins and padding uniform
- **Style**: Figure formats, bullet styles, numbering

**Benefits**:
- Professional appearance
- Reduced cognitive load (audiences learn your visual language)
- Focus on content, not adjusting to new formats
- Easy to identify information types

**Template Approach**:
- Create master slide with standard elements
- Design 3-5 layout variants (title, content, figure, section divider)
- Apply consistently throughout

## Typography

### Font Selection

**Recommended Font Types**:

**Sans-Serif Fonts** (Highly Recommended):
- **Arial**: Universal, highly legible
- **Helvetica**: Clean, professional
- **Calibri**: Modern default, works well
- **Gill Sans**: Elegant sans-serif
- **Futura**: Geometric, modern
- **Avenir**: Friendly, professional

**Serif Fonts** (Use Sparingly):
- Generally harder to read on screens
- Acceptable for titles in some contexts
- Avoid for body text in presentations

**Avoid**:
- ❌ Script or handwriting fonts (illegible from distance)
- ❌ Decorative fonts (distracting)
- ❌ Condensed fonts (hard to read)
- ❌ Multiple font families (>2 looks unprofessional)

### Font Sizes

**Minimum sizes depend on the variant — projection deck vs reading deck.** The numbers below replace a single generic scale with the two-tier scale that v3 locks in.

**Projection deck minimums** (auditorium / main-stage projection, 200-seat room):
- **Assertion headline / slide title**: 32 pt
- **Body and caption text**: **24 pt** (hard floor)
- **Axis labels and tick labels**: 18 pt
- **Footnotes and references**: 14 pt
- **Source / citation footer**: 10–12 pt

A projector in a mid-sized conference room produces effective text sizes *smaller* than the nominal point size because of throw distance, screen size, and ambient lighting. 14 pt axis labels on a dense multi-panel figure become unreadable from the back row even when they look fine on the authoring laptop. If the room is specifically small (a 20-person boardroom or a roundtable), the 24 pt body floor can drop to 20 pt — but the default assumes auditorium or main-stage projection.

**Reading deck minimums** (laptop at 60–80 cm):
- **Assertion headline / slide title**: 24 pt
- **Body and caption text**: 18 pt
- **Axis labels and tick labels**: **14 pt** (hard floor)
- **Footnotes**: 12 pt
- **Source / citation footer**: 10 pt

Never go below these floors on a reading deck — 14 pt axis labels are already the lower bound for scannable lookup.

**Dual-purpose deck — the compromise rule:**

The two variants conflict: 24 pt projection body is roughly 33% larger than 18 pt reading body, and a dual-purpose deck cannot honor both exactly. **Compose body text at 18 pt (the reading floor) but enforce the projection floor on headlines, assertion text, and the single most important takeaway line per slide.** This is a deliberate compromise; where the deck is known to serve primarily one use, adopt that variant's floor throughout.

When a figure imported from a journal uses Nature's native 5–8 pt text, it must be scaled up on the slide so that embedded text meets the applicable minimum at the intended viewing distance, or relabeled natively in PowerPoint.

**Presentation-focused headline scale** (title slides, closing slide emphasis):
- **Title slide title**: 44–54 pt
- **Section headers**: 36–44 pt

**The Room Test**:
- Can text be read from the back of the room?
- Rule: Body text should be readable at 6× screen height distance
- When in doubt: go larger

**Size Relationships**:
```
Title: 40pt
━━━━━━━━━━━━━━━━━
Subheading: 28pt
─────────────
Body text: 24pt
Regular content for audience

Caption: 16pt
```

### Text Formatting

**Best Practices**:

**Line Length**:
- Maximum 50-60 characters per line
- Break long sentences into multiple lines
- Use phrases, not full sentences when possible

**Line Spacing**:
- 1.2-1.5× line height for readability
- More spacing for dense content
- Consistent spacing throughout

**Alignment**:
- **Left-aligned**: Best for body text (natural reading)
- **Center-aligned**: Titles, short phrases, key messages
- **Right-aligned**: Rarely used (occasionally for design balance)
- **Justified**: Avoid (creates awkward spacing)

**Emphasis**:
- ✅ **Bold** for key terms (use sparingly)
- ✅ Color for emphasis (consistent meaning)
- ✅ Size increase for importance
- ❌ Avoid italics (hard to read from distance)
- ❌ Avoid underline (confused with hyperlinks)
- ❌ AVOID ALL CAPS FOR BODY TEXT (READS AS SHOUTING)

### Equations, subscripts, and chemical structures

For anything more complex than CO₂, H₂SO₄, or x_i, use the **modern equation editor** (`Insert > Equation`, or Alt+=). The current editor is OMML-based, scales with theme, and renders as live text.

**PowerPoint for M365 does not expose the LaTeX conversion button that Word has.** The reliable workflow is: author the equation in Word with LaTeX input, render via `Convert > Professional`, then copy into PowerPoint — it pastes as an editable equation.

For simple sub/superscripts, use plain text with Ctrl+= / Ctrl+Shift+=.

PowerPoint has **no native chemical-structure editor.** Draw in ChemDraw or an equivalent, export to EMF (Windows) or SVG (cross-platform), and insert. Simple benzene rings can be built from hexagon shapes, but anything with stereochemistry should come from a dedicated tool.

### Composition balance — symmetrical and asymmetrical

A slide's composition is usually either:

- **Symmetrical** — elements mirror each other around a central vertical axis. Suits title slides, section dividers, and slides whose content genuinely is a paired comparison (left panel vs right panel with shared caption).
- **Asymmetrical** — elements balance by **visual weight** rather than by mirror geometry. Suits content slides where one element (typically a data figure) is the dominant focus and the remaining elements (headline, annotation, caption) sit in the counterweight position.

**Failure modes:**
- **Symmetrical applied by default** — every content slide looks the same and nothing signals where the reader's attention should go.
- **Asymmetrical with underbuilt counterweight** — an 80%-weight figure on the left with a 20%-weight caption on the right leaves the right side visually empty.

**Build each layout in the Slide Master** with explicit placeholder positions, and put the reader's entry point (assertion headline or dominant figure) in the **upper-left**, matching left-to-right reading order. Avoid centered layouts for content slides unless the composition is genuinely symmetric; centering by default is the usual source of "every slide looks alike" drift.

### The 6×6 Rule

**Guideline**: Maximum 6 bullets per slide, maximum 6 words per bullet.

**Rationale**:
- More text = audience reads instead of listens
- Bullet points are prompts, not sentences
- You provide the explanation verbally

**Better Approach**:
- 3-4 bullets optimal
- 4-8 words per bullet
- Use fragments, not complete sentences
- Consider replacing text with visuals

**Example Transformation**:
```
TOO MUCH TEXT:
• Our study examined the relationship between dietary interventions 
  and cardiovascular outcomes in 1,500 participants over 5 years
• We found that participants in the intervention group showed 
  significantly reduced risk compared to controls
• The effect size was larger than previous studies and persisted 
  at long-term follow-up

BETTER:
• 5-year dietary intervention study
• 27% reduced cardiovascular risk
• Largest effect to date
```

## Color Theory

### Color Palettes for Scientific Presentations

**Purpose-Driven Color Selection**:

**Professional/Academic** (Conservative):
- Navy blue (#1C3D5A), gray (#4A5568), white (#FFFFFF)
- Accent: Orange (#E67E22) or green (#27AE60)
- Use: Faculty seminars, grant presentations, institutional talks

**Modern/Engaging** (Energetic):
- Teal (#0A9396), coral (#EE6C4D), cream (#F4F1DE)
- Accent: Burgundy (#780000)
- Use: Conference talks, public engagement, TED-style talks

**High Contrast** (Maximum Legibility):
- Black text (#000000) on white (#FFFFFF)
- Dark blue (#003366) on white
- White on dark gray (#2D3748)
- Use: Large venues, virtual presentations, accessibility priority

**Data Visualization** (Color-blind Safe):
- Blue (#0173B2), orange (#DE8F05), green (#029E73), red (#CC78BC)
- Based on Wong/IBM palettes
- Use: Figures with categorical data, bar charts, line plots

### Color Psychology in Science

**Blue**:
- Associations: Trust, stability, professionalism, intelligence
- Use: Backgrounds, institutional presentations, technology topics
- Caution: Can feel cold; balance with warmer accents

**Green**:
- Associations: Growth, health, nature, sustainability
- Use: Biology, environmental science, health outcomes
- Caution: Avoid red-green combinations (color blindness)

**Red/Orange**:
- Associations: Energy, urgency, warning, importance
- Use: Highlighting critical findings, emphasis, calls to action
- Caution: Don't overuse; loses impact

**Purple**:
- Associations: Innovation, creativity, wisdom
- Use: Neuroscience, novel methods, creative research
- Caution: Can appear less serious in some contexts

**Gray**:
- Associations: Neutrality, professionalism, sophistication
- Use: Backgrounds, de-emphasized content, grounding
- Caution: Can feel dull if overused

### Color Contrast and Accessibility

**WCAG Standards** (Web Content Accessibility Guidelines):
- **Level AA**: 4.5:1 contrast ratio for normal text
- **Level AAA**: 7:1 contrast ratio (preferred for presentations)

**High Contrast Combinations**:
- ✅ Black on white (21:1)
- ✅ Dark blue (#003366) on white (12.6:1)
- ✅ White on dark gray (#2D3748) (11.8:1)
- ✅ Dark text (#333333) on cream (#F4F1DE) (9.7:1)

**Low Contrast Combinations** (Avoid):
- ❌ Light gray on white
- ❌ Yellow on white
- ❌ Pastel colors on white backgrounds
- ❌ Red on black (difficult to read)

**Testing Contrast**:
- Use online tools (e.g., WebAIM Contrast Checker)
- Print slide in grayscale (should remain legible)
- View from distance (simulate audience perspective)

### Color Blindness Considerations

**Prevalence**: ~8% of men, ~0.5% of women have color vision deficiency

**Most Common**: Red-green color blindness (protanopia/deuteranopia)

**Safe Practices**:
- ✅ Use blue/orange instead of red/green
- ✅ Add patterns or shapes in addition to color
- ✅ Use color AND other differentiators (shape, size, position)
- ✅ Test with color blindness simulator

**Color-Blind Safe Palettes**:
```
Primary: Blue (#0173B2)
Contrast: Orange (#DE8F05)  [NOT green]
Additional: Magenta (#CC78BC), Teal (#029E73)
```

**Figure Design**:
- Don't rely solely on red vs. green lines
- Use different line styles (solid, dashed, dotted)
- Use symbols (circle, square, triangle) for scatter plots
- Label directly on plot rather than color legend only

## Layout and Composition

### The Rule of Thirds

Divide slide into 3×3 grid; place key elements at intersections or along lines.

**Application**:
```
+-------+-------+-------+
|   ┃   |   ┃   |   ┃   |
|---●---|---●---|---●---|  ← Key focal points (●)
|   ┃   |   ┃   |   ┃   |
|---●---|---●---|---●---|
|   ┃   |   ┃   |   ┃   |
|---●---|---●---|---●---|
|   ┃   |   ┃   |   ┃   |
+-------+-------+-------+
```

**Benefits**:
- More visually interesting than centered layouts
- Natural eye flow
- Professional appearance
- Guides attention strategically

**Example Usage**:
- Place key figure at right third
- Text summary on left two-thirds
- Title at top third line
- Logo at bottom-right intersection

### White Space

**Definition**: Empty space around and between elements.

**Purpose**:
- Gives content room to "breathe"
- Increases focus on important elements
- Prevents overwhelming the audience
- Projects professionalism and confidence

**Guidelines**:
- Margins: Minimum 5-10% of slide on all sides
- Element spacing: Clear separation between unrelated items
- Text padding: Space around text blocks
- Don't fill every pixel: Empty space is valuable

**Common Mistakes**:
- Cramming too much on one slide
- Extending content to edges
- No space between elements
- Fear of "wasting" space

### Layout Patterns

**Title + Content**:
```
┌─────────────────────────┐
│ Slide Title             │
├─────────────────────────┤
│                         │
│    Content Area         │
│    (text, figure,       │
│     or combination)     │
│                         │
└─────────────────────────┘
```
Use: Standard slide type, most common

**Two Column**:
```
┌─────────────────────────┐
│ Slide Title             │
├───────────┬─────────────┤
│           │             │
│  Text     │   Figure    │
│  Column   │   Column    │
│           │             │
└───────────┴─────────────┘
```
Use: Comparing items, text + figure

**Full-Slide Figure**:
```
┌─────────────────────────┐
│                         │
│                         │
│    Large Figure or      │
│    Image                │
│                         │
│                         │
└─────────────────────────┘
```
Use: Key results, impactful visuals

**Text Overlay**:
```
┌─────────────────────────┐
│   ┌─────────────┐       │
│   │ Text Box    │       │
│   └─────────────┘       │
│     Background Image    │
│                         │
└─────────────────────────┘
```
Use: Title slide, section dividers

**Grid Layout**:
```
┌─────────────────────────┐
│ Title                   │
├─────────┬───────┬───────┤
│ Item 1  │ Item 2│ Item 3│
├─────────┼───────┼───────┤
│ Item 4  │ Item 5│ Item 6│
└─────────┴───────┴───────┘
```
Use: Multiple related items, comparisons

### Alignment

**Principle**: Align elements to create visual order and relationships.

**Types**:

**Edge Alignment**:
- Align left edges of text blocks
- Align right edges of figures
- Align top edges of items in row

**Center Alignment**:
- Center title on slide
- Center key messages
- Center lone figures

**Grid Alignment**:
- Use invisible grid
- Snap elements to grid lines
- Maintains consistency across slides

**Visual Impact**:
- Aligned elements look intentional and professional
- Misaligned elements appear careless
- Small misalignments are very noticeable

## Tables on Slides

### When a table belongs on a slide

A table belongs on the slide when:
- **Precise values matter** (target product profile comparisons, pharmacokinetic parameters, assay readouts across compounds)
- **The reader will look up specific entries**
- **The data span orders of magnitude** in a way that charts obscure

If the audience's task is to **see a pattern**, a chart or heatmap wins. Schwabish (2021) lands on the same partition in his data visualization chapter.

### Table formatting

Scientific tables should be **minimal-rule**:
- Horizontal lines above and below the header row, and above any summary/total row
- No vertical lines unless absolutely necessary
- Align **numeric columns on the decimal**, text columns left, category labels left or centered depending on scan pattern
- Pad cells generously (`Table Design > Cell Margins > Wide`, with 0.04" minimum on left/right) so rows breathe
- **Bold the header row** and flag it as a header in `Table Design > Header Row` so the Accessibility Checker recognizes the structure

**For dense comparisons** (~50 cells or more where the audience's task is pattern-seeking), replace the numeric table with a **heatmap rendering** where cell background encodes magnitude on a sequential palette, keeping numeric values on top. This reads faster for pattern-seeking audiences while preserving the lookup use case.

---

## Background Design

### Background Colors

**Best Practices**:

**Light Backgrounds** (Most Common):
- White or off-white (#FFFFFF, #F8F9FA)
- Very light gray (#F5F5F5)
- Cream/beige (#FAF8F3)

**Advantages**:
- Maximum contrast for dark text
- Works in any lighting
- Professional and clean
- Easier on projectors

**Dark Backgrounds**:
- Dark gray (#2D3748)
- Navy blue (#1A202C)
- Black (#000000)

**Advantages**:
- Modern, sophisticated
- Good for dark venues
- Reduces eye strain in dark rooms
- Makes colors pop

**Disadvantages**:
- Requires light-colored text
- Can be difficult in bright rooms
- Some projectors handle poorly

**Gradient Backgrounds**:
- ✅ Subtle gradients acceptable (light to lighter)
- ❌ Avoid busy or high-contrast gradients
- ❌ Don't distract from content

**Image Backgrounds**:
- Use only for title/section slides
- Ensure sufficient contrast with text
- Add semi-transparent overlay if needed
- Avoid busy or cluttered images

### Borders and Frames

**Minimal Approach** (Recommended):
- No borders on most slides
- Let white space define boundaries
- Clean, modern appearance

**Selective Borders**:
- Around key figures for emphasis
- Separating distinct sections
- Highlighting callout boxes
- Simple, thin lines only

**Avoid**:
- Decorative borders
- Thick, colorful frames
- Clipart-style elements
- 3D effects and shadows

## Visual Elements

### Icons and Graphics

**Purpose**:
- Visual anchors for concepts
- Break up text-heavy slides
- Quick recognition of section types
- Add visual interest

**Best Practices**:
- ✅ Consistent style (all outline or all filled)
- ✅ Simple, recognizable designs
- ✅ Appropriate size (not too large or small)
- ✅ Limited color palette matching theme
- ❌ Avoid clipart or cartoonish graphics (unless appropriate)
- ❌ Don't use for decoration only (should convey meaning)

**Sources**:
- Font Awesome
- Noun Project
- Material Design Icons
- Custom scientific illustrations

### Bullets and Lists

**Bullet Styles**:
- **Simple shapes**: Circle (•), square (■), dash (−)
- **Avoid**: Complex symbols, changing bullet styles within list
- **Hierarchy**: Different bullets for different levels

**List Best Practices**:
- Maximum 4-6 items per list
- Parallel structure (all start with verb, or all nouns, etc.)
- Use fragments, not complete sentences
- Adequate spacing between items (1.5-2× line height)

**Alternative to Bullets**:
- **Numbered lists**: When order matters
- **Icons**: Visual representation of each point
- **Progressive builds**: Reveal one point at a time
- **Separate slides**: One concept per slide

### Shapes and Dividers

**Uses**:
- Background rectangles to highlight content
- Arrows showing relationships or flow
- Circles for emphasis or grouping
- Lines separating sections

**Guidelines**:
- Keep shapes simple (rectangles, circles, lines)
- Use brand colors
- Maintain consistency
- Avoid 3D effects
- Don't overuse

## Animation and Builds

### When to Use Animation

**Appropriate Uses**:
- **Progressive disclosure**: Reveal bullet points one at a time
- **Build complex figures**: Add layers incrementally
- **Show process**: Illustrate sequential steps
- **Emphasize transitions**: Highlight connections
- **Control pacing**: Prevent audience from reading ahead

**Inappropriate Uses**:
- ❌ Decoration or entertainment
- ❌ Every slide transition
- ❌ Multiple animations per slide
- ❌ Distracting effects (spin, bounce, etc.)

### Types of Animations

**Entrance**:
- **Appear**: Instant (good for fast-paced talks)
- **Fade**: Subtle, professional
- **Wipe**: Directional reveal
- Avoid: Fly in, bounce, spiral, etc.

**Exit**:
- Rarely needed
- Use to remove intermediary steps
- Keep simple (fade or disappear)

**Emphasis**:
- Color change for highlighting
- Bold/underline to draw attention
- Grow slightly for importance
- Use very sparingly

**Builds**:
- Reveal bullet points progressively
- Add elements to complex figure
- Show before/after states
- Demonstrate process steps

**Best Practices**:
- Fast transitions (0.2-0.3 seconds)
- Consistent animation type throughout
- Click to advance (not automatic timing)
- Builds should add clarity, not complexity

## Common Design Mistakes

### Failure Modes Overview

| Mistake | Why It Fails |
|---------|--------------|
| Reading slides verbatim | Audience reads faster than you speak; you become redundant and boring |
| Default PowerPoint themes | Signals "thrown together"; undermines perceived effort and credibility |
| 6+ bullet points per slide | Violates cognitive load limits; audience stops processing after third point |
| Skipping practice | First run-through reveals timing and flow problems you can't anticipate |
| Identical slide layouts throughout | Visual monotony; audience disengages after pattern becomes predictable |
| Complex figures copied from paper | Font sizes designed for print (10pt) are unreadable from back of room |
| No backup slides | Leaves you unprepared for predictable questions; appears under-prepared |

### Content Mistakes

**Too Much Text**:
- Problem: Audience reads instead of listening
- Fix: Use key phrases, not paragraphs; move details to notes

**Too Many Concepts per Slide**:
- Problem: Cognitive overload, unclear focus
- Fix: One idea per slide; split complex slides into multiple

**Inconsistent Formatting**:
- Problem: Looks unprofessional, distracting
- Fix: Use templates, maintain style guide

**Poor Contrast**:
- Problem: Illegible from distance
- Fix: Test at actual presentation size, use high-contrast combinations

**Tiny Fonts**:
- Problem: Unreadable for audience
- Fix: ≥24 pt body (projection) / ≥18 pt body (reading); see "Font Sizes" above for full two-tier floors

### Visual Mistakes

**Cluttered Slides**:
- Problem: No clear focal point, overwhelming
- Fix: Embrace white space, remove non-essential elements

**Low-Quality Images**:
- Problem: Pixelated or blurry figures
- Fix: Use high-resolution images (300 DPI minimum)

**Distracting Backgrounds**:
- Problem: Competes with content
- Fix: Simple, solid colors or subtle gradients

**Overuse of Effects**:
- Problem: Looks amateurish, distracting
- Fix: Minimal or no shadows, gradients, 3D effects

**Misaligned Elements**:
- Problem: Appears careless
- Fix: Use alignment tools, grids, and guides

### Color Mistakes

**Insufficient Contrast**:
- Problem: Hard to read
- Fix: Test with contrast checker, use dark on light or light on dark

**Too Many Colors**:
- Problem: Chaotic, unprofessional
- Fix: Limit to 3-5 colors total

**Red-Green Combinations**:
- Problem: Invisible to color-blind audience members
- Fix: Use blue-orange or add patterns/shapes

**Clashing Colors**:
- Problem: Visually jarring
- Fix: Use color palette tools, test combinations

## Accessibility

### Designing for All Audiences

**Visual Impairments**:
- High contrast text (minimum 4.5:1 AA; push toward 7:1 AAA for projection)
- Large fonts — ≥24 pt body for projection, ≥18 pt body for reading (see "Font Sizes")
- Simple, clear fonts (humanist or neo-grotesque sans-serif)
- No reliance on color alone to convey meaning (run the grayscale test)

**Color Blindness**:
- Avoid red-green combinations
- Use patterns, shapes, or labels in addition to color
- Test with color blindness simulator
- Provide alternative visual cues

**Cognitive Considerations**:
- Simple, uncluttered layouts
- One concept per slide
- Clear visual hierarchy
- Consistent navigation and structure

**Presentation Environment**:
- Works in various lighting conditions
- Visible from distance (back of large room)
- Readable on different screens (laptop, projector, phone)
- Printable in grayscale if needed

### Alternative Text and Descriptions

**For Figures**:
- Provide verbal description during talk
- Include detailed caption in notes
- Describe key patterns: "Notice the increasing trend..."

**For Complex Visuals**:
- Break into components
- Use progressive builds
- Provide interpretive context

### Drafting alt text efficiently

Writing alt text for every figure in a long deck is slow work if done cold. The efficient workflow:

1. **Draft with an LLM, then review and edit.** Prompt: hand the LLM the figure or a short description, plus the slide's assertion headline, and ask for one-to-two-sentence alt text that **states the finding** rather than describing the chart type.
2. **Review every draft before committing.** LLMs will plausibly hallucinate specific numbers that are not in the figure, and a wrong number in alt text is worse than no alt text.
3. **For figures already captioned in a manuscript or poster**, the caption is usually better raw material than the LLM draft.
4. **Never leave placeholder alt text** ("Image," "Figure," the filename). The Accessibility Checker flags *missing* alt text but not *generic* alt text — generic alt text passes the check while failing the actual use.

For code-checkable contrast, use `skills/shared/accessibility/check_contrast(fg, bg)` rather than eyeballing. For CVD simulation across deuteranopia/protanopia/tritanopia, use `skills/shared/accessibility/simulate_colorblindness()`.

### Live delivery accessibility

Accessibility is not only a file-level property; live delivery has its own constraints.

**When presenting a data figure live**, verbally describe the central feature as you introduce it — "the blue line rises twofold after treatment between days 7 and 14" — rather than gesturing and expecting visual-only comprehension. This serves audience members with low vision, those attending remotely with poor video quality, and anyone whose attention was elsewhere when the slide changed.

**When live-captioning is on** (PowerPoint's Live Captions, Zoom auto-captions, or a human captioner):
- Pace slightly slower than usual
- Enunciate technical terms
- Spell out acronyms the first time they appear
- Avoid pronouns where possible in the narration of figures ("this data" is ambiguous to a captioner; "the CT scan from week four" is not)

Captioning accuracy degrades sharply on rapid speech and on terminology outside the captioner's training corpus, which includes most biomedical jargon.

### Physical accessibility (in-person posters and setups)

For research posters presented in person, physical accessibility matters as much as visual accessibility of the file. Place the most important content — title, central finding, key figure — in the **upper-middle band of the poster, between roughly three and five and a half feet from the floor**. Text and figures placed above that band may be unreadable by shorter attendees or unreachable by wheelchair users; text placed too low forces everyone to crouch. Provide a **QR code to a PDF version** so attendees can access the content on their own device at their own zoom level; this also serves anyone with low vision who needs screen-reader access.

### Digital and interactive accessibility (web / HTML5 / kiosks)

For decks distributed as interactive web artifacts (embedded on a web page, HTML5 exports, kiosks, slide-sharing platforms with navigation controls), additional rules apply:

- **Keyboard-accessible navigation** — a user must be able to advance, go back, pause, and open every interactive element using only Tab and Enter, without a mouse
- **ARIA labels** on interactive elements so screen readers announce the control's purpose rather than reading the DOM element name
- **Autoplay of audio or video off by default**

These rules are inherited from general web accessibility practice (WCAG 2.2 and WAI-ARIA) and apply whenever the artifact stops being a static PDF and becomes a thing users interact with. For native PowerPoint playback, these concerns do not apply; they become relevant only at the moment the deck is published to the web.

### Regulated-industry archival (21 CFR Part 11)

For decks that enter FDA regulatory submissions, advisory-committee briefing books, or any process where the deck becomes an electronic record of a regulated activity, **21 CFR Part 11** applies.

The requirements are about the system the record lives in, not the PowerPoint file itself: the storage system must provide audit trails of who viewed and modified the record, e-signatures for approvals, secure access controls, and validation that the system behaves as specified.

**Operationally:**
- Store a Part 11-destined deck in a validated document management system (Veeva Vault, Documentum, or equivalent) rather than personal OneDrive
- Export the submission-ready version to **PDF/A** (a long-term-archival PDF variant that is self-contained and reproduces identically across readers)
- Include a **document control footer** with document number, version, effective date, and approver initials
- **Disclose the regulatory basis** for the content (e.g., "Prepared for FDA Type B meeting, October 2026")
- Ensure every data figure traces back to a source study, SAS dataset, or CSR table reference that auditors can follow

For **ICH-GCP sponsor records** (clinical trial documentation), decks used for sponsor-investigator meetings, protocol training, or DSMB review are TMF-eligible records and should be stored with the same rigor as other essential documents. For **IRB submissions**, decks shown to trial participants (consent presentations, site training) are typically appended as supporting materials.

## Design Workflow

### Step 1: Define Visual Identity

Before creating slides:
1. **Color palette**: Choose 3-5 colors
2. **Fonts**: Select 1-2 font families
3. **Style**: Decide on overall aesthetic (minimal, bold, traditional)
4. **Templates**: Create master slides for different types

### Step 2: Create Master Templates

Design 4-6 slide layouts:
1. **Title slide**: Name, title, affiliation
2. **Section divider**: Major transitions
3. **Content slide**: Standard text/bullets
4. **Figure slide**: Large visual focus
5. **Two-column**: Text + figure side-by-side
6. **Closing**: Questions, contact, acknowledgments

### Step 3: Apply Consistently

For each slide:
- Choose appropriate template
- Add content (text or visuals)
- Ensure alignment and spacing
- Check font sizes and contrast
- Verify consistency with other slides

### Step 4: Review and Refine

Review checklist:
- [ ] Every slide has clear focus
- [ ] Text is minimal and readable
- [ ] Visual hierarchy is clear
- [ ] Colors are consistent and accessible
- [ ] Alignment is precise
- [ ] White space is adequate
- [ ] Animations are purposeful
- [ ] Overall flow is smooth

## Tools and Resources

### Design Software

**PowerPoint**:
- Master slides for templates
- Alignment guides and gridlines
- Design Ideas feature for inspiration
- Morph transition for smooth animations

**Keynote** (Mac):
- Beautiful default templates
- Smooth animations
- Magic Move for object transitions

**Google Slides**:
- Collaborative editing
- Cloud-based access
- Simple, clean interface

**LaTeX Beamer**:
- Consistent, professional appearance
- Excellent for equations and code
- Version control friendly
- Reproducible designs

### Design Resources

**Color Tools**:
- Coolors.co: Palette generator
- Adobe Color: Color scheme creator
- WebAIM Contrast Checker: Accessibility testing
- Coblis: Color blindness simulator

**Icon Sources**:
- Font Awesome: General icons
- Noun Project: Specific concepts
- BioIcons: Science-specific graphics
- Flaticon: Large collection

**Inspiration**:
- Scientific presentation examples in your field
- TED talks for delivery style
- Conference websites for design trends
- Design portfolios (Behance, Dribbble)

## Summary Checklist

Before finalizing your slide design:

**Typography**:
- [ ] Body text ≥24 pt (projection) or ≥18 pt (reading); dual-purpose composes to 18 pt body + 32 pt headline
- [ ] Axis / tick labels ≥18 pt (projection) or ≥14 pt (reading)
- [ ] Assertion headline as full-sentence takeaway, not topic label (unless on a reference/disclosure/MLR-regulated slide)
- [ ] Maximum 6 bullets per slide, 6 words per bullet
- [ ] Humanist or neo-grotesque sans-serif throughout body; no more than 2 font families
- [ ] Equations rendered with the equation editor (not pasted as image)

**Color**:
- [ ] High contrast text-background (4.5:1 minimum)
- [ ] Limited color palette (3-5 colors)
- [ ] Color-blind safe combinations
- [ ] Consistent color use throughout

**Layout**:
- [ ] One main idea per slide
- [ ] Generous white space (don't fill every pixel)
- [ ] Elements aligned precisely
- [ ] Consistent layouts for similar content

**Visual Elements**:
- [ ] High-resolution images (300 DPI)
- [ ] Consistent icon/graphic style
- [ ] Minimal decorative elements
- [ ] Clear visual hierarchy

**Accessibility**:
- [ ] Readable from back of room
- [ ] Works in various lighting conditions
- [ ] No reliance on color alone
- [ ] Clear without audio (for recorded talks)

**Professional Polish**:
- [ ] Consistent template throughout
- [ ] No typos or formatting errors
- [ ] Smooth animations (if any)
- [ ] Clean, uncluttered appearance
