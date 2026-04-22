# Design Best-Practices Rollout Plan

A plan for adding **deep, format-specific design best-practices documentation** to every design-related skill in this plugin. Scope: what each skill's `references/design_best_practices.md` should contain, how it ties into the shared design foundation, and the scaffolding that keeps guidance consistent.

---

## Status

> **Phase 1 (hub establishment) complete — see CHANGELOG v1.2.0 (commit `3437765`, 2026-04-22).**
>
> Phase 1 of this plan originally designated `visual-design/` as the hub. Subsequent audit showed most design content was either Oligon-specific or coupled to a single consumer, so the direction was reversed: `visual-design/` was retired, utilities redistributed, and design-philosophy prose moved into `oligon-brand/SKILL.md`'s `<design_foundation>` block (with a generic-fallback paragraph for non-Oligon output). Each of the 6 extending skills received a short inline **Design checklist** (3–5 bullets) so they're self-contained.
>
> **Phase 2 (remaining)** — expand each of those short inline checklists into a full `references/design_best_practices.md` with principles, tool-specific constraints, decision tables, pre-flight acceptance tests, good/bad examples, and further-reading pointers. The scaffolding for Phase 2 is documented below.

### Post-v1.2.0 architecture

| Layer | Home | Responsibility |
|-------|------|----------------|
| Cross-format design philosophy | [`skills/oligon-brand/SKILL.md`](skills/oligon-brand/SKILL.md) `<design_foundation>` | Decision flow (audience → chart → palette → a11y), audience matrix, 7 universal pitfalls, generic-fallback palettes (viridis/Okabe-Ito/ColorBrewer) |
| Accessibility utilities (WCAG, CVD) | [`skills/shared/accessibility/`](skills/shared/accessibility/) | `contrast_ratio`, `validate_accessibility`, colorblind simulation, figure-spec validation, quality scoring, venue specs |
| Chart & palette selection | [`skills/plotting-libraries/scripts/`](skills/plotting-libraries/scripts/) | `chart_selector.recommend_chart_type()`, `palette_selector.select_palette()` |
| Per-venue figure dimensions | [`skills/venue-templates/references/figure_specs.md`](skills/venue-templates/references/figure_specs.md) | Column widths, DPI, preferred formats per journal |
| SVG component library | [`skills/shared/svg-components/`](skills/shared/svg-components/) | 9-component catalog + JSX (DonutChart, StatCallout, etc.) |
| Brand tokens | [`skills/oligon-brand/`](skills/oligon-brand/) | Oligon colors, typography, adapters for matplotlib/ggplot2/reportlab/docx/pptx/HTML |

Format-specific principles (the ones that only matter for one output type) still live per-skill — that's what this plan's Phase 2 builds out.

---

## Guiding principle: single source of truth

Put cross-cutting principles (typography scales, color theory, WCAG contrast, Tufte data-ink, Gestalt) **once** in `oligon-brand/SKILL.md`'s `<design_foundation>` block — or, for code-checkable WCAG/CVD validation, in `skills/shared/accessibility/`. Other skills should *link* to those and only contain **format-specific** guidance — otherwise you'll have 10 copies that drift as you update them.

**Rule of thumb:** if a principle applies equally to a slide, a poster, a figure, and a PDF, it belongs in `oligon-brand/<design_foundation>`. If it only matters for one format (e.g., projector contrast for slides, viewing distance for posters), it belongs in that skill's `references/design_best_practices.md`.

---

## Per-skill plan

### `oligon-brand/<design_foundation>` — the hub (Phase 1 done)

Already landed in v1.2.0. Contains:

- Condensed decision flow (audience → chart type → palette → accessibility → venue constraints)
- Audience matrix (journal reviewers / conference / public / internal)
- 7 universal pitfalls (Default Syndrome, Rainbow Colormap, Color-Only Encoding, Cramming, Inconsistency, Truncated Axes, 3D)
- Generic-fallback paragraph for non-Oligon output (viridis/Okabe-Ito/ColorBrewer, external WCAG tools)
- Absorbed output-format guidance (figures/infographics/reports/presentations/posters)

**Phase 2 opportunity:** consider splitting the dense content out into `oligon-brand/references/design_foundation.md` if the inline SKILL.md block grows past ~150 lines, keeping SKILL.md as the entry point.

### `skills/shared/accessibility/` — the testable layer (Phase 1 done)

Canonical APIs for code-checkable rules (contrast, CVD, validation). Phase 2 docs that reference these should use executable rules (e.g., `check_contrast(fg, bg) >= 4.5`) rather than prose ("sufficient contrast").

---

### `scientific-slides/` (inline checklist landed; deep doc remaining)

**Current (v1.2.0):** Inline Design checklist in SKILL.md — ≥24 pt body, ≥36 pt title, ≥4.5:1 contrast, ≤6 bullets/slide, dark/light per venue, animations narrative-only.

**Add — `references/design_best_practices.md`:**
- Slide grid (12-col), title/body hierarchy, 6×6 or 1-idea-per-slide rule
- **Projection-specific:** min font 24pt body / 32pt title, contrast for dim vs lit rooms, sans-serif default
- Animation discipline (reveal to support narrative, never decoration)
- Speaker notes conventions and presenter view expectations
- Dark vs light theme decision based on venue
- Handout vs presentation duality (same deck, different rendering pass)

**Tailor to tools:** `python-pptx` constraints (placeholder-based layouts, slide master inheritance, no real CSS), Beamer equivalents (frames, `\pause`, themes). Include a decision matrix: venue type → theme → font sizes → figure density.

---

### `research-posters/` (inline checklist landed; deep doc remaining)

**Current (v1.2.0):** Title readable at 10 ft, ≥30% whitespace, ≥300 DPI, bleed/safe margins, QR code resolves.

**Add — `references/design_best_practices.md`:**
- **Viewing-distance rules:** title readable at 10–15 ft, key message at 5 ft, details at 2 ft
- Better Poster format (left-side TL;DR bar) vs traditional 3-column vs billboard
- F-pattern / Z-pattern reading flow, numbered section markers
- Whitespace ≥30%, no walls-of-text, one-sentence section leads
- **Print-specific:** 300 DPI raster, vector for line art, CMYK vs RGB, bleed and safe margins, standard sizes (36×48, 42×72, A0)
- QR codes for paper/data/code links

**Tailor to tools:** LaTeX `beamerposter`/`baposter` (column math, rigid grids) vs PPTX poster (free layout but slide-size config driven). Include a size-preset reference table mapped to each toolchain.

---

### `scientific-schematics/` (inline checklist landed; deep doc remaining)

**Current (v1.2.0):** Reading direction declared, uniform node size unless ranking, arrow convention in legend, edge-crossings minimized, colorblind-safe palette.

**Add — `references/design_best_practices.md`:**
- Reading direction (L→R top→bottom for processes; center-out for systems)
- Node visual weight = importance; uniform sizing unless ranking
- Arrow disambiguation (solid=causal, dashed=hypothesized, double=reversible, open-circle=inhibition)
- Edge-crossing minimization heuristics
- Gestalt grouping with subtle backgrounds > hard boxes
- Diagram-type selection tree (flowchart / sequence / state / pathway / network)

**Tailor to tools:** Mermaid-specific constraints (layout engines `dagre`/`elk`, styling via `classDef`, when Mermaid breaks down → escalate to AI generation). Include a "Mermaid stylesheet" that maps Oligon tokens to `classDef` declarations.

---

### `paperbanana/` (inline checklist landed; deep doc remaining)

**Current (v1.2.0):** One central message, ≤3 panels for graphical abstracts, typography hierarchy, colorblind-safe palette, Oligon brand by default.

**Add — `references/design_best_practices.md`:**
- Graphical abstract conventions: one central message, arrow-driven narrative, 1–3 panels max
- "One figure, one idea" — how to decompose before prompting
- Prose-to-visual translation: which sentence becomes which panel
- Typography hierarchy for figures (title > panel-label > annotation > caption)

**Tailor to tools:** since the pipeline is AI-driven, this is mostly **prompt engineering patterns** — how to describe visual hierarchy, composition, and style constraints in prose so the multi-agent pipeline renders them. Include "anti-prompts" (phrasings that produce bad output) and example-driven prompt templates.

---

### `plotting-libraries/` (inline checklist landed; deep doc remaining)

**Current (v1.2.0):** Colorblind-safe palette (via `palette_selector`), direct labels over legends ≤5 series, bar y-axis starts at zero, log/linear stated, 300 DPI + font embedding.

**Add — `references/design_best_practices.md`:**
- Chart selection decision tree (comparison / composition / distribution / relationship / time) — reference `chart_selector.recommend_chart_type()`
- Data-ink ratio, remove chartjunk, direct labeling over legends where possible
- Binning/smoothing choices and the bias each introduces
- Error representation (SE vs SD vs CI — when each is appropriate)
- Faceting over color encoding past ~5 categories
- Log vs linear axis decision rules

**Tailor to tools:** library-specific idioms — `matplotlib` `rcParams` preset bundled with Oligon tokens, `seaborn` `set_context`/`set_style` pairs, `ggplot2` `theme_oligon()` function. One "publication-ready" recipe per library, plus a caveats section for each.

---

### `generate-image/` (inline checklist landed; deep doc remaining)

**Current (v1.2.0):** One central subject per prompt, aspect ratio explicit, lighting/style specified, typography hierarchy if text present, redirect scientific figures to paperbanana.

**Add — `references/design_best_practices.md`:**
- Composition (rule of thirds, leading lines, subject placement)
- Lighting direction/quality for photorealistic vs illustrative looks
- Aspect ratios for publication contexts (cover art 1:1, figure 3:2, slide 16:9)
- Consistency across a series (anchor prompts, seed reuse when supported)

**Tailor to tools:** Gemini 3 Pro prompt patterns — structural prompt template (subject + action + setting + style + lighting + framing), what Gemini handles well vs poorly. Clearly flag this is **not for figures** — redirect to `paperbanana` / `scientific-schematics`.

---

### `markdown-to-pdf/`

**Add — `references/design_best_practices.md`:**
- Page grid, margin conventions, running headers/footers
- Widow/orphan control, keep-with-next for headings
- Table layout (avoid landscape unless needed, max column count)
- Figure placement rules, caption positioning (above for tables, below for figures)
- Page-break logic for sections
- Font pairing for body / display / mono

**Tailor to tools:** template-engine-specific — which choices live in the template vs which are content-level overrides. Reference the existing 12 templates and note which design decisions each locks in, which are configurable.

---

### `paper-2-web/` (three sub-pipelines)

**Add — split by pipeline in one or three docs:**
- **Paper2Web:** scroll-driven narrative, responsive breakpoints, progressive disclosure, link hygiene, mobile-first figure sizing
- **Paper2Video:** pacing (~1 beat per idea), visual rhythm, caption readability at 480p, B-roll discipline
- **Paper2Poster:** *link out to `research-posters/` design guide — do not duplicate*

**Tailor to tools:** document each pipeline's layout primitives and where design control actually exists (template vs content vs runtime).

---

### `oligon-brand/`

**Current:** SKILL.md already covers brand tokens + `<design_foundation>` + adapters.

**Add — `references/token_application.md`:** token-application specifics not covered in the cross-format foundation:
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

**Tailor:** this is the protocol layer — keep it about *interface*, send visual-decision questions to `oligon-brand/<design_foundation>` or `skills/shared/accessibility/`.

---

## Suggested file structure per skill

```
<skill>/
  SKILL.md                       # existing — already has a short inline "Design checklist" (v1.2.0)
  references/
    design_best_practices.md     # Phase 2 — format-specific principles with tool mappings
    <format>_checklist.md        # optional — detailed pre-flight checklist per output format
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
- Cross-format foundation: [oligon-brand `<design_foundation>`](../../oligon-brand/SKILL.md)
- Accessibility / WCAG / CVD: [skills/shared/accessibility/](../../shared/accessibility/)
- Per-venue figure dimensions: [venue-templates/references/figure_specs.md](../../venue-templates/references/figure_specs.md)
- Chart & palette selection: [plotting-libraries/scripts/](../../plotting-libraries/scripts/) (`chart_selector`, `palette_selector`)
- Brand tokens: [oligon-brand/tokens/](../../oligon-brand/tokens/)

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

Every design doc should end with a concrete checklist the skill can run before calling a task done. Where possible, write items as code-checkable rules so `skills/shared/accessibility/` or a pre-commit hook can validate automatically. Examples:

**Slides checklist:**
- [ ] All body text ≥24 pt (measured in final deck, not editor zoom)
- [ ] `check_contrast(fg, bg) >= 4.5` for body text (WCAG AA)
- [ ] No slide has >6 bullets or >6 words per bullet
- [ ] All figures legible at projection distance (≥18 pt labels)
- [ ] Speaker notes present for non-self-explanatory slides

**Poster checklist:**
- [ ] Title readable at 10 ft (typically ≥72 pt)
- [ ] Whitespace ≥30% of total poster area
- [ ] All raster images ≥300 DPI at final print size
- [ ] Bleed and safe margins respected per venue print spec
- [ ] QR code resolves correctly (tested with ≥2 scanner apps)

Treat these as acceptance tests, not suggestions.

---

## Cross-reference map

Which skills should link to which parts of the shared foundation. Use this to wire up cross-references cleanly.

Column meanings (the concepts, not literal section names in the hub):
- **typography, color, data_viz, layout** — concerns covered across the `<design_foundation>` subsections (Decision Flow, Audience Matrix, Universal Design Pitfalls, Output-Format Guidance) in `oligon-brand/SKILL.md`. A ✓ means the skill's design doc should link back to the hub when touching that concern.
- **a11y** — `skills/shared/accessibility/` (contrast, CVD, figure-spec validation).
- **journal** — `venue-templates/references/figure_specs.md` (per-venue dimensions, DPI, preferred formats).

If Phase 2 work generates enough typography- or color-specific content to warrant explicit subsections in `<design_foundation>`, promote them there so this map becomes literal rather than conceptual.

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

## Implementation order (Phase 2)

Phase 1 (hub establishment + inline checklists in 6 extenders) is **complete** per v1.2.0.

For Phase 2, land these deep docs in this order — highest payoff first, since format-specific depth compounds with existing tooling:

1. **`scientific-slides/`, `research-posters/`** — highest format-specific payoff; projection and print constraints are concrete.
2. **`plotting-libraries/`, `scientific-schematics/`** — tight coupling to code + deterministic utilities already in place (`chart_selector`, `palette_selector`, Mermaid `classDef`).
3. **`markdown-to-pdf/`** — template-driven; document which decisions are template-locked vs content-overridable.
4. **`paperbanana/`, `generate-image/`** — AI-driven, prompt-engineering-flavored. Treat as a separate pattern.
5. **`paper-2-web/`** — three sub-pipelines; do after poster/figure guidance exists so it can link rather than duplicate.
6. **`oligon-brand/references/token_application.md`** — token-application specifics separate from the already-landed `<design_foundation>`.
7. **`brand-interface/`** — contract docs, written alongside or after the first few deep docs (uses them as examples).

---

## Additional guidance

### Things to avoid while writing these docs

- **Duplication.** If you find yourself writing the same paragraph in two skills, it belongs in `oligon-brand/<design_foundation>` or `skills/shared/accessibility/`. Cut it and link.
- **"Best practices" as platitudes.** "Use good contrast" is useless. "Body text ≥4.5:1 contrast (WCAG AA); use `skills/shared/accessibility/check_contrast(fg, bg)` to validate" is useful.
- **Principles without tool mappings.** Every principle in a format-specific doc should end with "How to apply in <tool>". If you can't, it's really a `<design_foundation>` principle — promote it there and link.
- **Long prose.** These docs are read by both humans and Claude — use decision tables, checklists, and short rules over paragraphs.
- **Aspirational claims.** Document what the tooling can actually enforce today. If `python-pptx` can't do X, say so and give the workaround.
- **Redundant cross-references.** Link to a shared ref the *first* time a concept appears in the doc; don't re-link on every mention.

### Quality gate per skill

Before marking a skill's design doc "done":

1. A reader unfamiliar with the skill can produce an acceptable output using only the doc + SKILL.md.
2. The pre-flight checklist is concrete (every item is pass/fail, not subjective).
3. At least one example of good output and one annotated example of bad output exist.
4. Cross-references to `oligon-brand/<design_foundation>` and/or `skills/shared/accessibility/` are present and resolve.
5. Tool-specific quirks (what the library can and can't enforce) are documented.

### Make it testable

Where possible, write checklist items as code-checkable rules, not human judgments:

- Instead of "use colorblind-safe palettes" → "colors are drawn from `palette_selector.CATEGORICAL_PALETTES` (Okabe-Ito etc.) or Oligon brand tokens"
- Instead of "sufficient contrast" → "`check_contrast(fg, bg) >= 4.5` via `skills/shared/accessibility/`"
- Instead of "appropriate font size" → "body text `>= 24pt` for slides, `>= 10pt` for print"

This lets `skills/shared/accessibility/` or a pre-flight hook validate outputs automatically, matching the contract-enforcement pattern already used for brand tokens in [`BRAND_SKILL_INTERFACE.md`](skills/BRAND_SKILL_INTERFACE.md).

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

Update as each skill's deep design doc lands. The "Inline checklist" column reflects v1.2.0 state (already done for 6 extenders).

| Skill | Inline checklist (v1.2.0) | Deep doc | Pre-flight | Examples | Cross-refs | Notes |
|-------|:---:|:---:|:---:|:---:|:---:|-------|
| oligon-brand (hub) | — | ✓ (`<design_foundation>`) | — | — | n/a | Phase 1 complete |
| skills/shared/accessibility | — | — | — | — | n/a | Utilities only; no SKILL.md |
| scientific-slides | ✓ |  |  |  |  | Phase 2 priority 1 |
| research-posters | ✓ |  |  |  |  | Phase 2 priority 1 |
| plotting-libraries | ✓ |  |  |  |  | Phase 2 priority 2; leverage `chart_selector`/`palette_selector` |
| scientific-schematics | ✓ |  |  |  |  | Phase 2 priority 2; include Mermaid `classDef` recipe |
| markdown-to-pdf |  |  |  |  |  | Phase 2 priority 3 |
| paperbanana | ✓ |  |  |  |  | Phase 2 priority 4; prompt-engineering |
| generate-image | ✓ |  |  |  |  | Phase 2 priority 4; prompt-engineering |
| paper-2-web |  |  |  |  |  | Phase 2 priority 5; three sub-pipelines; link out to posters |
| oligon-brand (token_application.md) | — |  |  |  |  | Phase 2 priority 6; token-application specifics |
| brand-interface |  |  |  |  |  | Phase 2 priority 7; contract-flavored, not visual |
