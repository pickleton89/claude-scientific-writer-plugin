# Design Best-Practices Rollout Plan (ARCHIVED — DIRECTION REVERSED)

> **Archived 2026-04-22.** This plan designated `visual-design` as the cross-format hub for design-philosophy content. Subsequent audit showed most of that content was either Oligon-project-specific or tightly coupled to a single downstream consumer, so the direction was reversed: `visual-design` was retired, design-philosophy prose moved into `oligon-brand/SKILL.md`'s `<design_foundation>` section (with a generic-fallback paragraph for non-Oligon output), and utilities were redistributed to `skills/shared/accessibility/`, `skills/shared/svg-components/`, `plotting-libraries/scripts/`, `venue-templates/references/`, and `oligon-brand/scripts/`. See `CHANGELOG.md` v1.2.0 entry for details. This document is preserved for historical context only — **do not use as a guide**.

---

A plan for adding design best-practices documentation to the design-related skills in this plugin. Scope: what to add per skill, how to tailor it to each skill's output format and toolchain, and the shared scaffolding that keeps everything from drifting.

---

## Guiding principle: single source of truth

Put cross-cutting principles (typography scales, color theory, WCAG contrast, Tufte data-ink, Gestalt) **once** in `skills/visual-design/references/` as reference docs. Other skills should *link* to those and only contain **format-specific** guidance — otherwise you'll have 10 copies that drift as you update them.

**Rule of thumb:** if a principle applies equally to a slide, a poster, a figure, and a PDF, it belongs in `visual-design/`. If it only matters for one format (e.g., projector contrast for slides, viewing distance for posters), it belongs in that skill.

---

## Per-skill plan

### `visual-design/` — the hub

**Add — canonical references that other skills cite:**
- `references/typography.md` — scale, hierarchy, line-length, figure-caption conventions, font pairing
- `references/color.md` — colorblind-safe palettes (viridis, Okabe-Ito, ColorBrewer), semantic color use, contrast ratios, print vs screen
- `references/data_visualization.md` — Tufte/Cairo principles, chart selection tree, error representation, encoding choices
- `references/layout.md` — grid systems, whitespace, visual hierarchy, Gestalt grouping
- `references/accessibility.md` — WCAG AA/AAA thresholds, alt-text patterns, colorblind validation
- `references/journal_conventions.md` — standard figure sizes (column width 3.5", double 7.25"), DPI requirements per publisher, required fonts

**Tailor:** this skill is the delegator — keep each reference authoritative and concise. Implementers link here rather than duplicate.

---

### `scientific-slides/` (you already have source content)

**Add — PowerPoint/Beamer-specific:**
- Slide grid (12-col), title/body hierarchy, 6×6 or 1-idea-per-slide rule
- **Projection-specific:** min font 24pt body / 32pt title, contrast for dim vs lit rooms, sans-serif default
- Animation discipline (reveal to support narrative, never decoration)
- Speaker notes conventions and presenter view expectations
- Dark vs light theme decision based on venue
- Handout vs presentation duality (same deck, different rendering pass)

**Tailor to tools:** `python-pptx` constraints (placeholder-based layouts, slide master inheritance, no real CSS), Beamer equivalents (frames, `\pause`, themes). Include a decision matrix: venue type → theme → font sizes → figure density.

---

### `research-posters/`

**Add — poster-specific:**
- **Viewing-distance rules:** title readable at 10–15 ft, key message at 5 ft, details at 2 ft
- Better Poster format (left-side TL;DR bar) vs traditional 3-column vs billboard
- F-pattern / Z-pattern reading flow, numbered section markers
- Whitespace ≥30%, no walls-of-text, one-sentence section leads
- **Print-specific:** 300 DPI raster, vector for line art, CMYK vs RGB, bleed and safe margins, standard sizes (36×48, 42×72, A0)
- QR codes for paper/data/code links

**Tailor to tools:** LaTeX `beamerposter`/`baposter` (column math, rigid grids) vs PPTX poster (free layout but slide-size config driven). Include a size-preset reference table mapped to each toolchain.

---

### `scientific-schematics/`

**Add — diagram-specific:**
- Reading direction (L→R top→bottom for processes; center-out for systems)
- Node visual weight = importance; uniform sizing unless ranking
- Arrow disambiguation (solid=causal, dashed=hypothesized, double=reversible, open-circle=inhibition)
- Edge-crossing minimization heuristics
- Gestalt grouping with subtle backgrounds > hard boxes
- Diagram-type selection tree (flowchart / sequence / state / pathway / network)

**Tailor to tools:** Mermaid-specific constraints (layout engines `dagre`/`elk`, styling via `classDef`, when Mermaid breaks down → escalate to AI generation). Include a "Mermaid stylesheet" that maps Oligon tokens to `classDef` declarations.

---

### `paperbanana/`

**Add — generated-figure specific:**
- Graphical abstract conventions: one central message, arrow-driven narrative, 1–3 panels max
- "One figure, one idea" — how to decompose before prompting
- Prose-to-visual translation: which sentence becomes which panel
- Typography hierarchy for figures (title > panel-label > annotation > caption)

**Tailor to tools:** since the pipeline is AI-driven, this is mostly **prompt engineering patterns** — how to describe visual hierarchy, composition, and style constraints in prose so the multi-agent pipeline renders them. Include "anti-prompts" (phrasings that produce bad output) and example-driven prompt templates.

---

### `plotting-libraries/`

**Add — chart-specific:**
- Chart selection decision tree (comparison / composition / distribution / relationship / time)
- Data-ink ratio, remove chartjunk, direct labeling over legends where possible
- Binning/smoothing choices and the bias each introduces
- Error representation (SE vs SD vs CI — when each is appropriate)
- Faceting over color encoding past ~5 categories
- Log vs linear axis decision rules

**Tailor to tools:** library-specific idioms — `matplotlib` `rcParams` preset bundled with Oligon tokens, `seaborn` `set_context`/`set_style` pairs, `ggplot2` `theme_oligon()` function. One "publication-ready" recipe per library, plus a caveats section for each.

---

### `generate-image/`

**Add — raster-generation specific:**
- Composition (rule of thirds, leading lines, subject placement)
- Lighting direction/quality for photorealistic vs illustrative looks
- Aspect ratios for publication contexts (cover art 1:1, figure 3:2, slide 16:9)
- Consistency across a series (anchor prompts, seed reuse when supported)

**Tailor to tools:** Gemini 3 Pro prompt patterns — structural prompt template (subject + action + setting + style + lighting + framing), what Gemini handles well vs poorly. Clearly flag this is **not for figures** — redirect to `paperbanana` / `scientific-schematics`.

---

### `markdown-to-pdf/`

**Add — print-document specific:**
- Page grid, margin conventions, running headers/footers
- Widow/orphan control, keep-with-next for headings
- Table layout (avoid landscape unless needed, max column count)
- Figure placement rules, caption positioning (above for tables, below for figures)
- Page-break logic for sections
- Font pairing for body / display / mono

**Tailor to tools:** template-engine-specific — which choices live in the template vs which are content-level overrides. Reference the existing 12 templates and note which design decisions each locks in, which are configurable.

---

### `paper-2-web/` (three sub-pipelines)

**Add — split by pipeline:**
- **Paper2Web:** scroll-driven narrative, responsive breakpoints, progressive disclosure, link hygiene, mobile-first figure sizing
- **Paper2Video:** pacing (~1 beat per idea), visual rhythm, caption readability at 480p, B-roll discipline
- **Paper2Poster:** *link out to `research-posters/` design guide — do not duplicate*

**Tailor to tools:** document each pipeline's layout primitives and where design control actually exists (template vs content vs runtime).

---

### `oligon-brand/`

**Add — token-application specific:**
- When to apply brand vs when to step back (journal templates often override)
- Light/dark mode token pairs
- Print-vs-screen color differences (CMYK gamut, ink gain)
- Per-format token mapping table (matplotlib rcParams / ggplot theme / reportlab / python-docx / python-pptx / CSS vars)

**Tailor to tools:** one "adapter contract" per format — what each adapter can and can't enforce. This complements `brand-interface/` which documents the protocol, not the visual decisions.

---

### `brand-interface/`

**Add — mostly contract docs, not visual principles:**
- How downstream skills request tokens
- Fallback behavior when brand unavailable
- Validation hooks (contrast checks, banned combinations)

**Tailor:** this is the protocol layer — keep it about *interface*, send visual-decision questions to `visual-design/` or `oligon-brand/`.

---

## Suggested file structure per skill

```
<skill>/
  SKILL.md                       # existing — add a "Design guidance" link section
  references/
    design_best_practices.md     # format-specific principles
    <format>_checklist.md        # pre-flight checklist
  examples/
    good_<format>.{ext}          # annotated good example
    bad_<format>_annotated.md    # what went wrong + how to fix
```

---

## Standard template for each `design_best_practices.md`

Use this skeleton so every skill's design doc has the same shape. Readers (including Claude reading the skill) learn the pattern once.

```markdown
# Design Best Practices — <Skill Name>

## When this applies
<one-paragraph scope: the output formats this covers, what it does not cover>

## Cross-references
- Typography: [visual-design/references/typography.md]
- Color: [visual-design/references/color.md]
- Accessibility: [visual-design/references/accessibility.md]
- <other relevant shared refs>

## Format-specific principles
### <Principle 1 — e.g., "Viewing distance">
<the rule, stated as an imperative>
**Why it matters:** <one sentence>
**How to apply in <tool>:** <concrete code or config>

### <Principle 2...>

## Tool-specific constraints
### <Tool A — e.g., "python-pptx">
- What you can control
- What you cannot control
- Workarounds

### <Tool B>

## Decision tables
| Situation | Choice | Rationale |
|-----------|--------|-----------|
| ...       | ...    | ...       |

## Pre-flight checklist
- [ ] ...
- [ ] ...

## Common mistakes
1. **<Mistake>** — <why it happens> — <fix>

## Further reading
- <canonical external source>
```

---

## Pre-flight checklist template

Every design doc should end with a concrete checklist the skill can run before calling a task done. Examples:

**Slides checklist:**
- [ ] All body text ≥24pt
- [ ] Contrast ratio ≥4.5:1 for body text
- [ ] No slide has >6 bullets or >6 words per bullet
- [ ] All figures legible at projection distance (≥18pt labels)
- [ ] Speaker notes present for non-self-explanatory slides

**Poster checklist:**
- [ ] Title readable at 10 ft
- [ ] Whitespace ≥30%
- [ ] All images ≥300 DPI at final print size
- [ ] Bleed and safe margins respected
- [ ] QR code resolves correctly

Treat these as acceptance tests, not suggestions.

---

## Cross-reference map

Which skills should link to which shared refs. Use this to wire up the cross-references cleanly.

| Skill | typography | color | data_viz | layout | a11y | journal |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| scientific-slides | ✓ | ✓ |  | ✓ | ✓ |  |
| research-posters | ✓ | ✓ |  | ✓ | ✓ | ✓ |
| scientific-schematics |  | ✓ |  | ✓ | ✓ |  |
| paperbanana | ✓ | ✓ |  | ✓ | ✓ | ✓ |
| plotting-libraries | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| generate-image |  |  |  | ✓ |  |  |
| markdown-to-pdf | ✓ | ✓ |  | ✓ | ✓ | ✓ |
| paper-2-web | ✓ | ✓ |  | ✓ | ✓ |  |
| oligon-brand | ✓ | ✓ |  |  | ✓ |  |

---

## Implementation order

Land these in this order so downstream skills have something to link to.

1. **`visual-design/references/`** — canonical refs. Do these first so nothing else blocks.
2. **`scientific-slides/`** — you already have source material. Use as the prototype.
3. **`research-posters/`, `plotting-libraries/`, `scientific-schematics/`** — highest format-specificity payoff.
4. **`markdown-to-pdf/`, `oligon-brand/`, `brand-interface/`** — token/adapter layer.
5. **`paperbanana/`, `generate-image/`** — AI-driven, prompt-engineering-flavored. Treat separately.
6. **`paper-2-web/`** — three sub-pipelines; do after poster/figure guidance exists so it can link rather than duplicate.

---

## Additional guidance

### Things to avoid while writing these docs

- **Duplication.** If you find yourself writing the same paragraph in two skills, it belongs in `visual-design/`. Cut it and link.
- **"Best practices" as platitudes.** "Use good contrast" is useless. "Body text ≥4.5:1 contrast (WCAG AA); use `brand-interface.check_contrast(fg, bg)` to validate" is useful.
- **Principles without tool mappings.** Every principle in a format-specific doc should end with "How to apply in <tool>". If you can't, it's really a `visual-design/` principle.
- **Long prose.** These docs are read by both humans and Claude — use decision tables, checklists, and short rules over paragraphs.
- **Aspirational claims.** Document what the tooling can actually enforce today. If `python-pptx` can't do X, say so and give the workaround.
- **Redundant cross-references.** Link to a shared ref the *first* time a concept appears in the doc; don't re-link on every mention.

### Quality gate per skill

Before marking a skill's design doc "done":

1. A reader unfamiliar with the skill can produce an acceptable output using only the doc + SKILL.md.
2. The pre-flight checklist is concrete (every item is pass/fail, not subjective).
3. At least one example of good output and one annotated example of bad output exist.
4. Cross-references to `visual-design/` are present and resolve.
5. Tool-specific quirks (what the library can and can't enforce) are documented.

### Make it testable

Where possible, write checklist items as code-checkable rules, not human judgments:

- Instead of "use colorblind-safe palettes" → "colors are drawn from `oligon-brand.palettes.categorical` or `viridis`"
- Instead of "sufficient contrast" → "`brand-interface.check_contrast(fg, bg) >= 4.5`"
- Instead of "appropriate font size" → "body text `>= 24pt` for slides, `>= 10pt` for print"

This lets `brand-interface` or a pre-flight hook validate outputs automatically, matching the contract-enforcement pattern already used for brand tokens.

### Canonical external references to cite

Use these as "Further reading" pointers so the docs don't need to reinvent foundational material:

- **Data viz:** Tufte, *The Visual Display of Quantitative Information*; Cairo, *The Truthful Art*; Wilke, *Fundamentals of Data Visualization* (free online)
- **Color:** Okabe & Ito palette (2008); ColorBrewer (Brewer & Harrower); WCAG 2.1/2.2 (W3C)
- **Typography:** Bringhurst, *The Elements of Typographic Style*; Butterick, *Practical Typography* (free online)
- **Slides:** Reynolds, *Presentation Zen*; Duarte, *Slide:ology*
- **Posters:** Morrison, *The Better Poster* (OSF + YouTube); Purrington poster design guide
- **Figures in science:** Rougier et al., "Ten Simple Rules for Better Figures" (PLOS Comp Bio, 2014)

### Maintenance plan

- Tie design-doc updates to brand-token releases. When `oligon-brand` bumps a version, sweep design docs for stale token references.
- Add a lightweight CI check (or pre-commit hook) that verifies cross-reference links resolve.
- When a user hits a design problem that wasn't covered, add it to the skill's "Common mistakes" section — treat the docs as living.

---

## Progress tracker

Use this to track rollout. Update as each skill's design doc lands.

| Skill | Design doc | Checklist | Examples | Cross-refs | Notes |
|-------|:---:|:---:|:---:|:---:|-------|
| visual-design (hub) |  |  |  | n/a | Land first |
| scientific-slides |  |  |  |  | Prototype — has source material |
| research-posters |  |  |  |  | |
| plotting-libraries |  |  |  |  | |
| scientific-schematics |  |  |  |  | |
| markdown-to-pdf |  |  |  |  | |
| oligon-brand |  |  |  |  | |
| brand-interface |  |  |  |  | Contract-flavored, not visual |
| paperbanana |  |  |  |  | Prompt-engineering |
| generate-image |  |  |  |  | Prompt-engineering |
| paper-2-web |  |  |  |  | Three sub-pipelines; link out to posters |
