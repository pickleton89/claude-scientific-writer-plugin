# Design Best Practices — Scientific Slides

## When this applies

This doc covers design for **scientific slide decks** built to be presented in a room and/or circulated as documents — conference talks, seminars, thesis defenses, BD and investor decks, SAB decks, KOL kits, journal clubs, grand rounds. Output formats: PowerPoint (.pptx), LaTeX Beamer (.pdf), Nano Banana Pro PDF.

**This doc does NOT cover:**
- Editing existing PPTX files — see `document-skills:pptx`
- Auto-generating presentation videos from papers — see `paper-2-web` (Paper2Video)
- Print-format research posters — see `research-posters`
- Standalone data visualizations (code-rendered figures) — see `plotting-libraries`

**The central tension** is density vs legibility: scientific slides carry multi-panel figures, schematics, and tables because the data is the argument, but those same decks are read asynchronously by people who never see the presenter and must survive that reading. Mainstream TED advice ("one idea per slide, minimal text, let the presenter do the work") strips the evidence and destroys the argument. This doc commits to **density with legibility** — assertion headlines carry the message, visual evidence carries the proof, and the reader can reconstruct both without the presenter.

## Cross-references

| Concern | Authoritative source |
|---------|---------------------|
| Cross-format decision flow (audience → chart → palette → a11y) | [`oligon-brand/SKILL.md`](../../oligon-brand/SKILL.md) `<design_foundation>` block |
| WCAG contrast, CVD simulation, figure-spec validation | [`skills/visual-design/utils/`](../../visual-design/utils/) — `check_contrast()`, `simulate_colorblindness()`, `validate_accessibility()` |
| Chart type + palette selection | [`visual-design/utils/`](../../visual-design/utils/) — `chart_selector.recommend_chart_type()`, `palette_selector.select_palette()` |
| Brand tokens (colors, typography, projection scale) | [`oligon-brand/tokens/brand-tokens.json`](../../oligon-brand/tokens/brand-tokens.json) — especially `typography.projection_scale` |
| python-pptx adapter (Oligon-branded PPTX generation) | [`oligon-brand/adapters/pptx_adapter.py`](../../oligon-brand/adapters/pptx_adapter.py) |
| **Narrative arcs, dual-purpose decks** | [`presentation_structure.md`](presentation_structure.md) |
| **Typography, color, layout, per-slide structure, accessibility** | [`slide_design_principles.md`](slide_design_principles.md) |
| **Chart types, vector workflow, code-to-deck pipelines** | [`data_visualization_slides.md`](data_visualization_slides.md) |
| **PowerPoint M365 discipline (Slide Master, Copilot audit, DLP)** | [`powerpoint_implementation_guide.md`](powerpoint_implementation_guide.md) |
| **Visual validation workflow, metadata/attribution** | [`visual_review_workflow.md`](visual_review_workflow.md) |
| **Delivery technique (pointer, Q&A, recovery)** | [`../assets/timing_guidelines.md`](../assets/timing_guidelines.md) |

## Format-specific principles

Each principle is an imperative rule with a reason and a tool-specific mapping. If you cannot map a principle to a tool, it probably belongs in `oligon-brand/<design_foundation>` instead.

### 1. Assertion-evidence headlines by default

Make the slide title a full-sentence declarative takeaway, not a topic label.

**Why it matters:** Garner & Alley 2013, controlled 110-student study — assertion-evidence slides produced ~59% vs 42% comprehension over topic-subtitle slides (p < 0.01), reduced major misconceptions by ~10×, increased delayed recall.

**How to apply:**
- **python-pptx**: set the slide title text to the full sentence; ensure the title placeholder font size ≥32 pt (projection) or ≥24 pt (reading).
- **Beamer**: use `\frametitle{Full-sentence assertion.}` with a body that supports the claim visually rather than restating it.
- **html2pptx / PptxGenJS**: `slide.addText("Full sentence assertion", { fontSize: 32, bold: true, ... })` as the first element.
- **Exception:** reference slides, disclosure slides, acknowledgments, MLR-approved KOL templates where assertion headlines read as promotional claims — use neutral topic labels instead.

See `slide_design_principles.md` → "Per-Slide Structure and Assertion-Evidence."

### 2. Two-tier typography — projection vs reading floors

Projection decks require a 24 pt body floor; reading decks tolerate 18 pt; dual-purpose compose to 18 pt body with 32 pt headlines.

**Why it matters:** A projector in a 200-seat room produces effective text smaller than nominal point size due to throw distance, screen size, and ambient lighting; 14 pt axis labels look fine on the authoring laptop and are unreadable from the back row.

**How to apply:**
- **python-pptx / pptx_adapter.py**: `FONT_SIZES["body"]` currently 18 pt (reading-deck-aligned). For a pure-projection deck, override to 24 pt.
- **Beamer**: default 11 pt body is far below floor. Beamer's class accepts only `8|9|10|11|12|14|17|20` pt as options. For projection, use `\documentclass[17pt]{beamer}` (the largest standard size) or load `\usepackage{anyfontsize}` and set `\fontsize{24}{28}\selectfont` on body text. Most decks work in relative sizing (`\Large`, `\huge`) over a 17 pt base.
- **html2pptx / PptxGenJS**: set `fontSize: 24` for body text in the projection variant.
- **Dual-purpose compromise:** body at 18 pt (reading floor), headlines and single-most-important-takeaway line at 32 pt (projection floor).

See `slide_design_principles.md` → "Font Sizes."

### 3. Colorblind-safe palette, committed at the master level

Use the Okabe-Ito 8-color palette (Wong 2011) or a ColorBrewer sequential/diverging palette for ordered data. Never rely on color alone — encode redundantly with shape, pattern, or direct labeling.

**Why it matters:** ~8% of men and 0.5% of women (Northern European ancestry) have red-green color vision deficiency. A deck reviewed by three male partners has roughly a one-in-five chance at least one cannot resolve red-green encodings. WCAG 2.2 SC 1.4.1 treats "conveyed by color alone" as a failure.

**How to apply:**
- **python-pptx / pptx_adapter.py**: palette loaded from `oligon-brand/tokens/brand-tokens.json` v5.0 (Oklch-derived, CVD-safe). For non-Oligon decks, use `skills/visual-design/utils/palette_selector.select_palette(require_colorblind_safe=True)`.
- **PowerPoint Theme Colors**: load palette into `Slide Master > Colors > Customize Colors`, mapping primary to Accent 1. Pick colors from the **Theme Colors row only** for primary content; reserve Standard Colors for one-off annotations.
- **Validation**: `skills/visual-design/utils/simulate_colorblindness(hex, cvd_type)` for CVD simulation; `View > Grayscale` in PowerPoint for the 5-second grayscale test.

See `slide_design_principles.md` → "Color Theory."

### 4. Vector over raster for anything that isn't a photograph

Line art, schematics, icons, chemical structures, and charts live as vector (EMF, WMF, SVG, or native PowerPoint shapes). Raster (PNG, JPEG) only for micrographs, gel blots, photographs.

**Why it matters:** Vectors scale without pixelation, export cleanly to PDF, and respect theme colors if built from native shapes.

**How to apply:**
- **From R/Python**: `ggsave(..., device = "emf")` or `plt.savefig("figure.svg")`. For matplotlib, post-process to `.emf` to preserve editability.
- **Icons**: download EPS/SVG → insert → `Convert to Shape` → ungroup → recolor to theme → regroup. Never drop a raster PNG when a vector source exists.
- **For photos**: 300 ppi at final display size; use `Picture Format > Compress Pictures` at HD (330 ppi) or Print (220 ppi) before distribution.

See `data_visualization_slides.md` → "Vector Over Raster."

### 5. Slide Master discipline — placeholders, not free text boxes

Every deck is built on a Slide Master with named layouts and real placeholders. No free text boxes carrying primary content.

**Why it matters:** Outline View only shows placeholder text. The Accessibility Checker flags "missing slide title" if the title lives in a free text box. Placeholder drift ("jittering" logos, footers, section headers) accumulates as technical debt and fails the reader.

**How to apply:**
- **python-pptx**: start from a reference template `.pptx` with the Slide Master already populated; insert content into placeholders by index. See `pptx_adapter.py::create_brand_presentation()`.
- **PowerPoint desktop**: build layouts **Maximum-to-Minimum** (most complex first, then duplicate and subtract placeholders for simpler layouts) to preserve placeholder index order across layout switches.
- **Diagnostic**: flip through Slide Sorter view; anything that jitters is not using a placeholder. Run `Home > Reset` after re-applying the correct layout.
- **Beamer**: the frame structure enforces placeholder discipline by default — use `\frametitle{}`, `\framesubtitle{}`, `columns` environment rather than raw `\put`.

See `powerpoint_implementation_guide.md` → "PowerPoint Microsoft 365 Desktop Discipline."

### 6. Animation default is "none"

Default position on animation: none. The one defensible exception is progressive reveal of a multi-panel figure in the order the argument depends on, only when rehearsed.

**Why it matters:** Animations introduce technical risk (fail to advance, desynchronize, render oddly across PPT versions/OSes), they are an accessibility liability for photosensitive viewers and screen-reader users, and decorative animations signal amateurism. Progressive disclosure does not survive PDF export.

**How to apply:**
- **python-pptx**: python-pptx does not support animations; this is a feature, not a bug.
- **PowerPoint desktop**: when a reveal is used, confine to *Appear* and *Fade* at 0.25–0.5 s. Never use emphasis or exit animations on data slides. For PDF-safe progressive disclosure, duplicate the slide — one slide per build state.
- **Beamer**: use `\pause` or `\onslide<1->` sparingly, only for narrative builds.

See `slide_design_principles.md` → "Animation and progressive disclosure."

### 7. Dual-purpose composition — write for both uses

Most scientific decks are projected AND read asynchronously. Compose on the reading-deck side: assertion headlines do the voiceover work; panel captions are short but self-contained; methods slides include enough context to stand alone.

**Why it matters:** The actual audience includes the VC partner who forwards to three colleagues, the SAB member reading on an airplane, the colleague screenshotting a results slide. A deck that requires the presenter to make sense has failed its actual distribution.

**How to apply:**
- Panel captions 2–3 lines at 14–16 pt below each panel.
- "So what" line in slightly smaller type at the bottom of conclusions slides, stating the implication.
- Methods slides carry a context sentence ("Mouse xenograft, n=8 per arm, dosed QD × 21 days, primary endpoint tumor volume at Day 28").
- Speaker notes (`View > Notes Page`) for presenter-only content; run `File > Info > Inspect Document` before distribution if notes are sensitive.

See `presentation_structure.md` → "Dual-Purpose Decks."

### 8. The Iceberg Principle — appendix does real work

The main arc is the tip above the waterline; the appendix is the mass below. The presenter argues from the tip while every claim is grounded in the mass beneath.

**Why it matters:** A scientific Q&A lives or dies on whether the speaker can produce the supporting data. An appendix with full dose-response curves, individual-patient data, replicate experiments, toxicology, and sequence alignments makes the deck Q&A-survivable. Without it, the speaker is improvising from memory.

**How to apply:**
- Dedicated **Backup** section divider; number appendix slides distinctly (B1–B23 or A-1, A-2) for unambiguous reference.
- **Section Zoom** (`Insert > Zoom > Section Zoom`) for Q&A jumps; keep target sections small and named.
- For inline jumps, hidden hyperlinks on primary slides.

See `presentation_structure.md` → "The Iceberg Principle."

## Tool-specific constraints

What each tool can and cannot enforce for scientific slide design:

| Capability | python-pptx / pptx_adapter | PowerPoint M365 desktop | Beamer (LaTeX) | html2pptx / PptxGenJS | Nano Banana Pro PDF |
|-----------|:--:|:--:|:--:|:--:|:--:|
| Slide Master enforcement | ⚠️ if template provided | ✅ | ✅ (frames are masters) | ⚠️ manual discipline | ❌ (flat PDF) |
| Theme color cascade | ✅ via tokens | ✅ | ✅ `\usetheme` | ⚠️ hex per call | ❌ |
| Font embedding | ✅ on save | ✅ (TrueType/OpenType) | ✅ (LaTeX bundles) | ✅ | ✅ |
| Accessibility tags | ❌ | ✅ Checker | ⚠️ partial | ❌ | ❌ |
| Alt text | ✅ shape.alt_text | ✅ | ⚠️ `\pdftooltip` | ✅ | ❌ |
| Animation / progressive disclosure | ❌ | ✅ | ✅ `\pause` | ⚠️ limited | ❌ |
| Live captions / recording | n/a | ✅ | n/a | n/a | n/a |
| Version history | via OneDrive | via OneDrive/SharePoint | via git | via git | via git |
| Copilot / Designer integration | ❌ | ⚠️ audit required | ❌ | ❌ | ❌ |
| DLP / content security | via `Inspect Document` post-gen | ✅ | n/a | n/a | n/a |
| Equations | ⚠️ as images | ✅ (OMML editor) | ✅ (LaTeX native) | ⚠️ as images | ⚠️ as images |
| Round-trip editability | ✅ | ✅ | ✅ (source .tex) | ✅ | ❌ |

**Key takeaways:**
- **PowerPoint desktop** is the only tool that enforces accessibility natively. Use it for final audit even if the deck was generated programmatically.
- **Beamer** owns accessibility-weak territory; compensate with `\pdftooltip{}{alt text}` for image alt-text (from `pdfcomment` or `accsupp`), load `\usepackage{hyperref}` for document structure, and use the `tagpdf` package on recent LaTeX engines (LuaTeX or pdfTeX) for PDF/UA tagged-PDF output. Full PDF/UA compliance in Beamer remains non-trivial; budget review time accordingly.
- **python-pptx** cannot do animations — a feature for scientific work where animations are generally an anti-pattern.
- **Nano Banana Pro PDF** is a flat-rendered artifact; for anything requiring edit round-trips, use python-pptx or PowerPoint instead.

## Decision tables

### A. Venue → theme → type sizes → density

| Venue | Theme | Body floor | Headline | Density |
|-------|-------|:---:|:---:|---|
| Auditorium / main-stage conference (≥200 seats) | Light, high contrast | 24 pt | 32 pt | Projection-sparse |
| Boardroom / 20-person meeting | Light, corporate | 20 pt | 28 pt | Moderate |
| SAB / in-person advisory | Light, corporate | 20 pt | 28 pt | Moderate + question-forward |
| BD / investor (dual-purpose) | Brand, commercial | 18 pt body / 32 pt headline | 32 pt | Reading-dense |
| Laptop / async reading | Light | 18 pt | 24 pt | Reading-dense |
| KOL / CME | MLR-approved template | 18 pt | per MLR | Per MLR |
| Grand rounds / M&M | Clinical, subdued | 20 pt | 28 pt | Moderate + case-led |

### B. Narrative arc selector

See `presentation_structure.md` → "Narrative Arcs by Audience." Quick version:

| Audience | Arc |
|----------|-----|
| Biotech BD / investor | SCQA (Situation → Complication → Question → Answer) |
| Conference talk / seminar | IMRaD (Introduction → Methods → Results → Discussion) |
| Journal club | PICO seven-step |
| Grand rounds / tumor board / CME | HCDMT (Hook → Context → Discovery → Meaning → Takeaway) |
| M&M conference | Case → Decision points → Outcome → Lessons |
| SAB | Open-question inversion |
| Internal review | Data → Limitations → Next Steps |

### C. Table vs chart

| Task | Use | Why |
|------|-----|-----|
| Precise values matter (TPP, PK parameters) | Table | Chart loses precision |
| Reader will look up specific entries | Table | Scannable structure |
| Data span orders of magnitude | Table or log-scale chart | Linear chart obscures |
| See a pattern | Chart or heatmap | Pattern recognition is a visual task |
| ~50+ cells, pattern-seeking | Heatmap (cell bg color + numeric overlay) | Preserves lookup AND pattern |

### D. Split vs keep dense slide

**Split when:**
- Two subplots answer two different questions
- Reader would need to re-caption to follow the argument
- Slide carries more than one takeaway worth stating in words

**Keep together when:**
- Panels are parts of the same comparison that must be seen simultaneously
- Figure is the canonical published version and separation would break a reviewer's mental model

Projection decks tilt toward splitting; reading decks tilt toward keeping together.

## Pre-flight checklist

Run before any deck leaves the author's machine. Every item is pass/fail.

### Content integrity

- [ ] Every content slide has an **assertion headline** that answers "so what?" (or a documented exception per §1)
- [ ] Every data figure has **n, dose/concentration, duration, statistical test** on-slide
- [ ] Every borrowed figure has **on-slide attribution** with license info (CC BY / "with permission" / "Data on File")
- [ ] All citations present; references slide or appendix carries full citations
- [ ] Embargoed or unreleased data has appropriate confidentiality marking
- [ ] Effect-size claims do not collapse "statistically significant" into "clinically meaningful"

### Visual integrity — code-checkable

- [ ] Body text ≥**24 pt** (projection variant) or **≥18 pt** (reading variant)
- [ ] `check_contrast(fg, bg) >= 4.5` for body text (WCAG AA) — use `skills/visual-design/utils/check_contrast()`
- [ ] `check_contrast(fg, bg) >= 3.0` for text ≥18 pt regular or 14 pt bold
- [ ] Bar charts encoding quantity **anchor to zero**
- [ ] No rainbow/jet colormaps on continuous data; viridis / cividis / ColorBrewer sequential in use
- [ ] No color-only encoding; **shape, pattern, or direct labeling** present as redundant channel
- [ ] **Grayscale test passed** — `View > Grayscale` in PowerPoint; every data series still distinguishable
- [ ] Colors on primary content drawn from the **Theme Colors row only**; Standard Colors / manual hex confined to one-off annotations
- [ ] Direct labels on line charts where ≤5 series; default legends deleted
- [ ] No 3D effects on 2D data
- [ ] No isotype charts scaled by height rather than area (area-vs-height scaling error)
- [ ] No dual y-axes without explicit justification

### Typographic integrity

- [ ] All body text meets the variant floor (above)
- [ ] Slide titles a consistent **single step above body**; subheadings a consistent single step between
- [ ] Humanist or neo-grotesque sans-serif throughout body; monospace only for code and sequences
- [ ] Math rendered with the **equation editor**, not pasted as image
- [ ] No orphaned single-character widows on wrapped lines; no justified body text

### Structural integrity

- [ ] Every slide assigned to a **master layout**; no free-floating text boxes carrying primary content
- [ ] **Placeholder-drift check passed** — flip through Slide Sorter view; no jittering logos, footers, or section headers
- [ ] **Reading Order Pane verified** on complex multi-object slides
- [ ] No content floats off the slide boundary in projection view
- [ ] Section Zoom or hyperlinks used for backup/appendix navigation

### Accessibility and compliance

- [ ] **Accessibility Checker** shows no errors and only reviewed warnings
- [ ] **Alt text describes the finding**, not the chart type, for every informative image
- [ ] Tables have header rows flagged
- [ ] Embedded video has captions (`Playback > Insert Captions`)
- [ ] For regulated decks: document control footer present; file destined for validated DMS (Veeva Vault, Documentum) in **PDF/A**

### Distribution hygiene

- [ ] Filename follows `project_purpose_date_version.pptx` convention
- [ ] Speaker notes reviewed for content that should not travel
- [ ] `File > Info > Inspect Document` run; leaked metadata removed
- [ ] Embedded fonts enabled in `File > Options > Save` if non-standard fonts in use
- [ ] Export is PDF (or PDF/A) unless recipient explicitly requested .pptx
- [ ] Projection and reading variants (if both exist) exported with matching version numbers

### Copilot / AI-generated content review

- [ ] Every number verified against source
- [ ] Every citation exists and says what the slide claims
- [ ] Every figure inspected for correct axes, units, annotations
- [ ] Copilot-generated text rewritten into the deck's voice and assertion-evidence cadence
- [ ] Theme color consistency restored where Copilot introduced its own palette (`Home > Reset`)

### Narrative QA — the one-minute test

- [ ] Hand the closed deck to a colleague with 60 s per slide + pen
- [ ] For each slide, can they write the key finding and why it matters?
- [ ] If not, assertion headlines and visual hierarchy have failed somewhere — revisit `slide_design_principles.md` "Per-Slide Structure" and `data_visualization_slides.md` "Chart types and when to use them."

## Common mistakes

1. **Default-theme syndrome** — shipping a deck with PowerPoint's built-in Office theme. *Fix:* customize Slide Master theme colors and fonts before building content; load Okabe-Ito or Oligon palette into Theme Colors row.
2. **Copilot hallucinated citations** — Copilot invents author names and DOIs that read plausibly. *Fix:* verify every citation Copilot introduces against your reference manager. Never ship a Copilot-generated slide without a human read of every claim.
3. **Theme-color drift on rebrand** — deck built with Standard Colors or manual hex values requires touching every object to retheme. *Fix:* pick from Theme Colors row only for primary content.
4. **Placeholder jittering** — logos, footers, section headers shift position as the reader advances. *Fix:* flip through Slide Sorter view; anything that jitters is a free text box — replace with a master-level placeholder.
5. **Color-only encoding** — red-green comparisons with no shape, pattern, or label redundancy. *Fix:* run the 5-second grayscale test (`View > Grayscale` in PowerPoint); any data series that collapses into indistinguishable gray needs a non-color redundant channel.
6. **Font embed missing** — deck travels to another machine and fonts fall back to Calibri/Arial, breaking layouts. *Fix:* `File > Options > Save > Embed fonts in the file`. Use "Embed only the characters used" for final distribution.
7. **Dual-purpose over-pack** — composing every slide at reading-deck density on a projection-primary talk, making every slide unreadable from the back row. *Fix:* confirm venue; if projection-primary, compose to projection-deck floors (24 pt body, projection-sparse density).
8. **Assertion headlines on regulated templates** — KOL slide kits with MLR-approved claim structures reject AE headlines that read as promotional. *Fix:* document the exception; carry a non-AE variant alongside AE for non-regulated distribution.
9. **Projection-deck body @ 18 pt** — v2 of this guide allowed 18 pt projection body; v3 raises the floor to 24 pt for pure auditorium projection. *Fix:* audit any pure-projection deck using the 18 pt reading-variant floor; bump body to 24 pt.
10. **Animation survives only in Slide Show mode** — progressive disclosure is invisible in the PDF export that actually gets forwarded. *Fix:* duplicate the slide (one per build state) so the PDF preserves the progressive structure.

## Further reading

- **Alley, M. (2013).** *The Craft of Scientific Presentations*. 2nd ed. Springer. — Assertion-evidence framework.
- **Doumont, J.-L. (2009).** *Trees, Maps, and Theorems: Effective Communication for Rational Minds*. Principiae. — Three-laws framing; slide titles should deliver a message.
- **Garner, J. K. & Alley, M. P. (2013).** How the design of presentation slides affects audience comprehension: A case for the assertion-evidence approach. *IJEE* 29(6): 1564–1579. — The 59% vs 42% comprehension data.
- **Naegle, K. M. et al. (2021).** Ten simple rules for effective presentation slides. *PLOS Comp Bio* 17(12): e1009554. — One-minute test.
- **Rougier, N. P., Droettboom, M. & Bourne, P. E. (2014).** Ten simple rules for better figures. *PLOS Comp Bio* 10(9): e1003833. — "Do not trust the defaults." Banking-to-45.
- **Wong, B. (2011).** Color blindness. *Nature Methods* 8(6): 441. — Okabe-Ito 8-color palette.
- **Reynolds, G. (2011).** *Presentation Zen*. 2nd ed. New Riders. — Image-heavy keynote style (correct for general-audience talks; wrong for scientific decks).
- **Tufte, E. R. (2001, 2006).** *The Visual Display of Quantitative Information*; *The Cognitive Style of PowerPoint*. Graphics Press. — Proportional ink, data-to-ink ratio; critique of bullet-list defaults.
- **Minto, B. (1987).** *The Pyramid Principle*. Pitman. — SCQA narrative structure.
- **Morrison, M. (2019).** #betterposter. OSF / YouTube. — Billboard-poster insight; works in deck form as the assertion-headline anchor.
