# Design Best-Practices Rollout Plan

A plan for adding **deep, format-specific design best-practices documentation** to every design-related skill in this plugin. Scope: what each skill's `references/design_best_practices.md` should contain, how it ties into the shared design foundation, and the scaffolding that keeps guidance consistent.

---

## Status

> **Phase 1 (hub establishment) complete — see CHANGELOG v1.2.0 (commit `3437765`, 2026-04-22).**
>
> Phase 1 of this plan originally designated `visual-design/` as the hub. Subsequent audit showed most design content was either Oligon-specific or coupled to a single consumer, so the direction was reversed: `visual-design/` was retired, utilities redistributed, and design-philosophy prose moved into `oligon-brand/SKILL.md`'s `<design_foundation>` block (with a generic-fallback paragraph for non-Oligon output). Each of the 6 extending skills received a short inline **Design checklist** (3–5 bullets) so they're self-contained.
>
> **Phase 2 underway — `scientific-slides/` v2.5.0 landed 2026-04-22 (commit `5c8c61c`).** First priority-1 deep doc shipped: [`skills/scientific-slides/references/design_best_practices.md`](skills/scientific-slides/references/design_best_practices.md). Validates the template (see [§Standard template](#standard-template-for-each-design_best_practicesmd)) and the "distribute + capstone" synthesis pattern when a skill already has substantial design reference material. Surfaced a set of upstream gaps now tracked in [§Phase 2 backlog](#phase-2-backlog). Remaining priority-1 target: `research-posters/`.
>
> **Cross-cutting absorption landed 2026-04-23 (commit `5463f4d`).** A long-form, primary-source-verified (April 2026) synthesis covering cognitive science for figures, journal GA specs, and iconography licensing was absorbed horizontally into three consolidation points rather than per-skill deep docs: `venue-templates/references/figure_specs.md` (GA specs, font embedding, alt text, conflict flags), two new shared refs (`skills/shared/references/iconography-licensing.md`, `pre_submission_checklist.md`), and a new "Cognitive foundation" subsection of `oligon-brand/<design_foundation>` (Cleveland-McGill, Cowan, Treisman, Wagemans, Franconeri, Crameri). The 4 visual skills (`paperbanana`, `research-posters`, `scientific-schematics`, `plotting-libraries`) were wired to the new shared refs; source doc preserved at [`docs/design-rationale/infographic-graphic-abstract.md`](docs/design-rationale/infographic-graphic-abstract.md). This is a **third pattern** alongside per-skill deep doc and distribute + capstone: a horizontal slice when content is genuinely cross-cutting and primary-source-verified. See [§Phase 2 backlog](#phase-2-backlog) for what was promoted to the hub and what gaps remain.
>
> **Phase 2 (remaining)** — expand each of the remaining short inline checklists into a full `references/design_best_practices.md` with principles, tool-specific constraints, decision tables, pre-flight acceptance tests, good/bad examples, and further-reading pointers. The 2026-04-23 absorption narrows scope for `research-posters`, `paperbanana`, `scientific-schematics`, and `plotting-libraries` deep docs — each can now link to shared refs rather than re-stating icon licensing, pre-submission gates, or cognitive foundations. Scaffolding below.

### Post-v1.2.0 architecture

| Layer | Home | Responsibility |
|-------|------|----------------|
| Cross-format design philosophy | [`skills/oligon-brand/SKILL.md`](skills/oligon-brand/SKILL.md) `<design_foundation>` | Decision flow (audience → chart → palette → a11y), audience matrix, 7 universal pitfalls, generic-fallback palettes (viridis/Okabe-Ito/ColorBrewer), **Cognitive foundation** (Cleveland-McGill 1984, Cowan 2010, Treisman & Gelade 1980, Wagemans et al. 2012, Franconeri et al. 2021, Crameri et al. 2020) — added 2026-04-23 |
| Accessibility utilities (WCAG, CVD) | [`skills/shared/accessibility/`](skills/shared/accessibility/) | `contrast_ratio`, `validate_accessibility`, colorblind simulation, figure-spec validation, quality scoring, venue specs |
| Chart & palette selection | [`skills/plotting-libraries/scripts/`](skills/plotting-libraries/scripts/) | `chart_selector.recommend_chart_type()`, `palette_selector.select_palette()` |
| Per-venue figure + GA specs | [`skills/venue-templates/references/figure_specs.md`](skills/venue-templates/references/figure_specs.md) | Column widths, DPI, preferred formats per journal; **graphical-abstract specs** (Cell 1200×1200@300dpi, Nature Chem 90×50mm, "not used" for most other venues with the alternative they substitute); **color-space preferences**; **font embedding (Type 42)** with per-toolchain commands; **alt-text formula**; Cell GA + Lancet conflict flags — expanded 2026-04-23 |
| Icon/illustration library licensing | [`skills/shared/references/iconography-licensing.md`](skills/shared/references/iconography-licensing.md) | BioRender (tiered + Academic Individual author-position rule), NIH BIOART, SciDraw, Servier Medical Art, Noun Project, Reactome, WikiPathways, Somersault. Attribution templates, re-verify banner — added 2026-04-23 |
| Unified pre-submission quality gate | [`skills/shared/references/pre_submission_checklist.md`](skills/shared/references/pre_submission_checklist.md) | 15-point checklist spanning GA policy → dimensions → font embedding → CVD → color-as-information → position-over-area → ≤4 channels → zero baseline → typography → WCAG contrast → magenta+green fluorescence → scale bars → icon licensing → alt text → archive. Each item states check/why/how — added 2026-04-23 |
| Long-form design rationale | [`docs/design-rationale/infographic-graphic-abstract.md`](docs/design-rationale/infographic-graphic-abstract.md) | Primary-source-verified (April 2026) cognitive-science + publisher-spec synthesis. Canonical "cite-back" for reviewer pushback — moved to docs/ 2026-04-23 |
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

### `scientific-slides/` — **Phase 2 landed (v2.5.0, 2026-04-22)** ✓

**Capstone:** [`skills/scientific-slides/references/design_best_practices.md`](skills/scientific-slides/references/design_best_practices.md) — ~320-line executive summary following the standard template. Eight format-specific principles each mapped to python-pptx / Beamer / html2pptx; tool-capability matrix; four decision tables (venue → typography/density, narrative arc selector, table vs chart, split vs keep); code-checkable pre-flight keyed to `skills/shared/accessibility/` functions; ten common mistakes; canonical further reading (Alley, Doumont, Garner & Alley, Naegle, Rougier, Wong, Reynolds, Tufte, Minto, Morrison).

**Updated inline checklist** (SKILL.md v2.5.0): assertion-evidence default, two-tier typography (24 pt projection / 18 pt reading / 32 pt dual-purpose headline), WCAG 4.5:1 contrast with `check_contrast()` pointer, grayscale test, one-minute test, animation default-none.

**Synthesis strategy used.** The skill already had ~4,900 lines of reference material across 7 existing files. Rather than create a parallel `design_best_practices.md` that duplicated 60% of `slide_design_principles.md`, the Phase 2 pass was executed in two parts:
1. **Capstone** as a high-density executive doc that summarizes and cross-references; each section links to the detailed file rather than duplicating it.
2. **Distribution**: content from three new source docs (a 509-line v3 scientific-slide-decks combined guide, a 664-line PowerPoint design guide, a 1762-line NotebookLM Q&A transcript) was routed into matching existing refs, then the source docs were deleted so there is one source of truth per topic. Reference listing in SKILL.md restructured into six groups (design entry point, structure, design details, implementation by tool, validation/delivery, legacy) for scannability.

**File reorganization.** `assets/powerpoint_design_guide.md` → `references/powerpoint_implementation_guide.md` (prose+code belongs in refs, not assets). Two untracked source files deleted after content distribution.

**Validator bugfix (in-scope surfacing).** Fresh-eyes review caught that `SlidePlanValidator.validate()` short-circuited after JSONSchema errors, masking three business-rule test expectations. Fixed by continuing past schema errors (business rules already use defensive `.get()`). Test suite now 47/47 passing (was 44/47).

**Examples still pending.** The standard template asks for `examples/good_<format>.{ext}` + `examples/bad_<format>_annotated.md`. Deferred to a follow-on; not blocking.

**Template-validation note for future priority-1 skills.** The capstone template worked well. The "distribute + capstone" pattern is the right default when a skill already has substantial design reference material; use it (rather than writing a single standalone deep doc) for `research-posters/` and `plotting-libraries/`, which both already have rich per-format content.

---

### `research-posters/` (inline checklist landed; shared refs wired 2026-04-23; deep doc remaining)

**Current (v1.2.0):** Title readable at 10 ft, ≥30% whitespace, ≥300 DPI, bleed/safe margins, QR code resolves.

**Shared refs now wired (2026-04-23):** `SKILL.md <references>` table links to `iconography-licensing.md` (handles BioRender/Servier/Noun Project licensing — common on posters), `pre_submission_checklist.md` (supplements poster-specific checklist with CVD/contrast/alt-text/font-embedding items), and `oligon-brand/<design_foundation>` (cognitive foundation). The eventual deep doc should link to these rather than re-state them.

**Add — `references/design_best_practices.md`:**
- **Viewing-distance rules:** title readable at 10–15 ft, key message at 5 ft, details at 2 ft
- Better Poster format (left-side TL;DR bar) vs traditional 3-column vs billboard
- F-pattern / Z-pattern reading flow, numbered section markers
- Whitespace ≥30%, no walls-of-text, one-sentence section leads
- **Print-specific:** 300 DPI raster, vector for line art, CMYK vs RGB, bleed and safe margins, standard sizes (36×48, 42×72, A0)
- QR codes for paper/data/code links

**Tailor to tools:** LaTeX `beamerposter`/`baposter` (column math, rigid grids) vs PPTX poster (free layout but slide-size config driven). Include a size-preset reference table mapped to each toolchain.

---

### `scientific-schematics/` (inline checklist landed; shared refs wired 2026-04-23; deep doc remaining)

**Current (v1.2.0):** Reading direction declared, uniform node size unless ranking, arrow convention in legend, edge-crossings minimized, colorblind-safe palette.

**Shared refs now wired (2026-04-23):** `SKILL.md <references>` table links to `iconography-licensing.md`, `pre_submission_checklist.md`, `figure_specs.md`, and `oligon-brand/<design_foundation>`. Gestalt grouping + pre-attentive features (both relevant to node/edge design) now have primary-lit citations in the hub.

**Add — `references/design_best_practices.md`:**
- Reading direction (L→R top→bottom for processes; center-out for systems)
- Node visual weight = importance; uniform sizing unless ranking
- Arrow disambiguation (solid=causal, dashed=hypothesized, double=reversible, open-circle=inhibition)
- Edge-crossing minimization heuristics
- Gestalt grouping with subtle backgrounds > hard boxes
- Diagram-type selection tree (flowchart / sequence / state / pathway / network)

**Tailor to tools:** Mermaid-specific constraints (layout engines `dagre`/`elk`, styling via `classDef`, when Mermaid breaks down → escalate to AI generation). Include a "Mermaid stylesheet" that maps Oligon tokens to `classDef` declarations.

---

### `paperbanana/` (inline checklist landed; shared refs wired 2026-04-23; deep doc remaining)

**Current (v1.2.0):** One central message, ≤3 panels for graphical abstracts, typography hierarchy, colorblind-safe palette, Oligon brand by default.

**Shared refs now wired (2026-04-23):** `SKILL.md <references>` table links to `iconography-licensing.md`, `pre_submission_checklist.md`, `figure_specs.md § Graphical-Abstract Specifications` (Cell 1200×1200px@300dpi — directly relevant since paperbanana generates GAs), and `oligon-brand/<design_foundation>`. The eventual deep doc focuses on prompt-engineering patterns; the technical specs and cognitive foundations are already centralized.

**Add — `references/design_best_practices.md`:**
- Graphical abstract conventions: one central message, arrow-driven narrative, 1–3 panels max
- "One figure, one idea" — how to decompose before prompting
- Prose-to-visual translation: which sentence becomes which panel
- Typography hierarchy for figures (title > panel-label > annotation > caption)

**Tailor to tools:** since the pipeline is AI-driven, this is mostly **prompt engineering patterns** — how to describe visual hierarchy, composition, and style constraints in prose so the multi-agent pipeline renders them. Include "anti-prompts" (phrasings that produce bad output) and example-driven prompt templates.

---

### `plotting-libraries/` (inline checklist landed; shared refs wired 2026-04-23; deep doc remaining)

**Current (v1.2.0):** Colorblind-safe palette (via `palette_selector`), direct labels over legends ≤5 series, bar y-axis starts at zero, log/linear stated, 300 DPI + font embedding.

**Shared refs now wired (2026-04-23):** `SKILL.md <reference_guides>` gained a "Shared References (Cross-Skill)" section linking to `iconography-licensing.md`, `pre_submission_checklist.md`, `figure_specs.md` (now with font-embedding commands for matplotlib/ggplot2/ragg — directly executable), and `oligon-brand/<design_foundation>` (Cleveland-McGill justifies the palette_selector's position-over-color bias).

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
- **typography, color, data_viz, layout** — concerns covered across the `<design_foundation>` subsections (Decision Flow, Audience Matrix, Universal Design Pitfalls, Output-Format Guidance, **Cognitive foundation** added 2026-04-23) in `oligon-brand/SKILL.md`. A ✓ means the skill's design doc should link back to the hub when touching that concern.
- **a11y** — `skills/shared/accessibility/` (contrast, CVD, figure-spec validation). **Note:** as of 2026-04-23, the unified 15-point `skills/shared/references/pre_submission_checklist.md` is the single entry point that each visual-skill's deep doc should link for accessibility/contrast/alt-text/grayscale/CVD gating.
- **journal** — `venue-templates/references/figure_specs.md` (per-venue dimensions, DPI, preferred formats; as of 2026-04-23 also **graphical-abstract specs**, **color-space preferences**, **Type 42 font-embedding commands**, **alt-text formula**).
- **icons** (implicit column, not shown in the table) — `skills/shared/references/iconography-licensing.md`. Every skill that composites icons (BioRender, Servier, NIH BIOART, SciDraw, Noun Project) should link here rather than re-stating licensing terms. Wired into `paperbanana`, `research-posters`, `scientific-schematics`, `plotting-libraries` on 2026-04-23.

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

1. **`scientific-slides/`** ✓ landed v2.5.0 (2026-04-22, commit `5c8c61c`); **`research-posters/`** — next up. Highest format-specific payoff; projection and print constraints are concrete.
2. **`plotting-libraries/`, `scientific-schematics/`** — tight coupling to code + deterministic utilities already in place (`chart_selector`, `palette_selector`, Mermaid `classDef`).
3. **`markdown-to-pdf/`** — template-driven; document which decisions are template-locked vs content-overridable.
4. **`paperbanana/`, `generate-image/`** — AI-driven, prompt-engineering-flavored. Treat as a separate pattern.
5. **`paper-2-web/`** — three sub-pipelines; do after poster/figure guidance exists so it can link rather than duplicate.
6. **`oligon-brand/references/token_application.md`** — token-application specifics separate from the already-landed `<design_foundation>`.
7. **`brand-interface/`** — contract docs, written alongside or after the first few deep docs (uses them as examples).

---

## Phase 2 backlog

*Upstream follow-ups surfaced during implementation.*

Issues that the Phase 2 per-skill passes discover in the shared foundation. These are not themselves Phase 2 deep docs; they are candidates for promotion to the hub layer or for targeted upgrades to shared utilities. Log them here so they surface when subsequent Phase 2 skills hit the same gap.

### Surfaced by `scientific-slides/` (v2.5.0)

**Candidates for promotion to `oligon-brand/<design_foundation>`** — cross-format principles currently sitting inside a single skill's deep doc:

- **Color theory foundations** — hue / saturation / brightness as three independent dimensions; monochromatic / analogous / complementary / triadic palette schemes. Currently in `slide_design_principles.md` (absorbed from v3 §D). Applies equally to figures, posters, and presentations.
- **Grayscale-encoding test** — toggle `View > Grayscale` (or `Image > Grayscale` in Inkscape/Illustrator) and verify every data series remains distinguishable. Five-second sanity check for color-alone encoding failures. Currently in `slide_design_principles.md`; applies to any figure or chart.
- **Single-message test** — "if you cannot state what the slide/figure is about in one sentence, it is doing too much." Currently in `slide_design_principles.md`; applies to any figure/poster/slide.
- **Assertion-evidence framework** — title as declarative takeaway, body as supporting evidence (Alley 2013). Currently framed as a slide principle but applies to figure titles, poster sections, and graphical-abstract captions.
- **5-second rule + Squint test** — headline legibility audits that apply to any visual artifact with a primary entry point.

**Shared-infrastructure gaps:**

| Gap | Location | Impact |
|-----|----------|--------|
| No dark-background projection palette variant | `oligon-brand/tokens/brand-tokens.json` v5.0 | `scientific-slides/` design doc has to specify generic fallback; dark-room venues currently unsupported by brand tokens |
| No alternative slide dimensions (4:3, vertical) | `oligon-brand/adapters/pptx_adapter.py` — hardcodes 13.333" × 7.5" | Legacy venues and mobile-first decks require manual override |
| No "projection" or "dark-background" palette preset | `plotting-libraries/scripts/palette_selector.py` | Slide-specific figures built through the palette selector get reading-deck colors |
| Zero slide/presentation venue coverage in figure specs | `venue-templates/references/figure_specs.md` | Covers only journal figs; slide venues (conference stage, boardroom, projector vs laptop) need parallel `slide_specs.md` eventually |

**How to act on these:** when two or more priority-1 Phase 2 skills need the same principle, promote it to `<design_foundation>` rather than duplicating. Shared-infra gaps should be filed as standalone upgrade tickets; they block the Phase 2 doc less than they block the underlying rendering.

### Surfaced by 2026-04-23 cross-cutting absorption (`infographic-graphic-abstract.md`)

A long-form primary-source-verified synthesis was absorbed horizontally rather than per-skill. Key movements:

**Promoted to `oligon-brand/<design_foundation>` as a new "Cognitive foundation" subsection:**
- Cleveland & McGill 1984 *JASA* channel ranking (position > length > angle > area > color saturation)
- Cowan 2010 *Curr Dir Psych Sci* — ~4-chunk working-memory limit (justifies ≤4 encoded dimensions per panel, 3–5 acts per GA)
- Treisman & Gelade 1980 *Cog Psych* — feature-integration theory (justifies Rule 6 no-hue-alone)
- Wagemans et al. 2012 *Psych Bulletin* — Gestalt grouping (justifies direct labeling over corner legends)
- Franconeri et al. 2021 *PSPI* — serial comparisons vs parallel ensemble perception
- Crameri et al. 2020 *Nat Comm* — rainbow critique + Scientific Colour Maps

Listed as citations with one-line applications. Linked back from `brand-colors-full.md § 4 Figure Integrity` for reviewer-pushback cite-backs.

**Promoted to shared references (new files):**
- `skills/shared/references/iconography-licensing.md` — BioRender tiered model, NIH BIOART, SciDraw, Servier, Noun Project, Reactome, WikiPathways, Somersault. Attribution templates + re-verify banner.
- `skills/shared/references/pre_submission_checklist.md` — 15-point unified gate (check/why/how per item).

**Expanded in `venue-templates/references/figure_specs.md`:**
- § Graphical-Abstract Specifications (per-publisher policy + dimensions)
- § Color-Space Preferences (RGB at Nature/PNAS/Science/Cell/JAMA/PLOS/eLife)
- § Font Embedding with Type 42 / `cairo_pdf()` / `ragg` / Illustrator commands
- § Alt-Text Formula
- § Conflict Flags (Cell GA 8–12 vs 12–16 pt; Lancet 75 vs 107 mm)

**Not closed (still in prior backlog):**
- Dark-background projection palette variant in brand tokens.
- Alt slide dimensions in `pptx_adapter.py`.
- "projection" / "dark-background" palette preset in `palette_selector`.
- Slide/presentation venue coverage in `figure_specs.md` (this pass expanded the journal-figure side only; conference-stage/boardroom/projector specs remain uncovered).

**New pattern validated.** The "horizontal slice" is a third absorption pattern alongside per-skill deep doc (e.g. `scientific-slides`) and distribute + capstone (also `scientific-slides`). Use a horizontal slice when:
1. The source material is genuinely cross-cutting (relevant to ≥3 priority-1 or priority-2 skills).
2. The content is primary-source-verified (citations, publisher guides) rather than practitioner heuristics.
3. The content is reference-shaped (tables, formulae, lookup) rather than workflow-shaped.

When any of those three conditions fail, prefer the per-skill deep doc or the distribute + capstone patterns.

**Implication for remaining Phase 2 deep docs.** `research-posters`, `paperbanana`, `scientific-schematics`, and `plotting-libraries` each now link to the shared refs; their deep docs shrink correspondingly. The remaining scope for each is their format-specific content (poster viewing-distance math, Mermaid classDef recipes, paperbanana prompt-engineering patterns, per-library publication-ready recipes) rather than cross-cutting color/typography/licensing/cognitive principles.

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
| oligon-brand (hub) | — | ✓ (`<design_foundation>` + **Cognitive foundation** 2026-04-23) | — | — | n/a | Phase 1 complete + cross-cutting augment 2026-04-23 |
| skills/shared/accessibility | — | — | — | — | n/a | Utilities only; no SKILL.md |
| skills/shared/references (new) | — | ✓ (iconography-licensing, pre_submission_checklist) | — | — | n/a | Cross-cutting shared references — landed 2026-04-23 (commit `5463f4d`) |
| venue-templates/figure_specs | — | ✓ expanded | ✓ 15-point | — | ✓ | GA specs, color-space, font embedding, alt text, conflict flags — expanded 2026-04-23 |
| scientific-slides | ✓ | ✓ | ✓ |  | ✓ | **Landed v2.5.0** (commit `5c8c61c`, 2026-04-22) — Phase 2 priority 1 complete. Examples (`examples/good_*`, `examples/bad_*_annotated.md`) still pending; upstream findings filed under [§Phase 2 backlog](#phase-2-backlog) |
| research-posters | ✓ |  |  |  | ✓ | Phase 2 priority 1; shared refs wired 2026-04-23 |
| plotting-libraries | ✓ |  |  |  | ✓ | Phase 2 priority 2; leverage `chart_selector`/`palette_selector`; shared refs wired 2026-04-23 |
| scientific-schematics | ✓ |  |  |  | ✓ | Phase 2 priority 2; include Mermaid `classDef` recipe; shared refs wired 2026-04-23 |
| markdown-to-pdf |  |  |  |  |  | Phase 2 priority 3 |
| paperbanana | ✓ |  |  |  | ✓ | Phase 2 priority 4; prompt-engineering; shared refs wired 2026-04-23 (GA specs particularly relevant) |
| generate-image | ✓ |  |  |  |  | Phase 2 priority 4; prompt-engineering |
| paper-2-web |  |  |  |  |  | Phase 2 priority 5; three sub-pipelines; link out to posters |
| oligon-brand (token_application.md) | — |  |  |  |  | Phase 2 priority 6; token-application specifics |
| brand-interface |  |  |  |  |  | Phase 2 priority 7; contract-flavored, not visual |
