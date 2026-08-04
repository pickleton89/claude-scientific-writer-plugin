# Design Practices Index — stage-anchored reading list

> Curated entry point into shared and skill-local design references. Each workflow stage of svg-figure-maker (see `../SKILL.md` `<workflow>`) cites a section of this index. Claude reads ONE catalog at the start of a session instead of hunting across the repo for the right design rule.
>
> Sections are keyed to the workflow stages: §0 = Stage 0 intent, §1 = Stage 1 brand load, §2 = Stage 2 draft, §3 = Stage 3 preflight, §4 = Stage 4 rasterize, §5 = Stage 5 visual critique.

---

## §0 — Intent and framing (Stage 0)

Use when scoping the figure brief before any drawing.

| Source | What it gives you |
|---|---|
| `shared/references/figure_vs_table_decision.md` | Decision tree: is this actually a figure problem, or should it be a table? |
| `shared/references/communication_context_matrix.md` | Audience × viewing-context grid; calibrates figure complexity to consumption mode (oral talk vs article vs poster vs interactive) |
| `shared/references/figure_design_principles.md` §5.1 (figure-vs-table) and §5.5 (communication context) | One-line summaries of the above |
| `shared/references/figure_design_principles.md` §5.4 (complexity budgets) | Hard ceilings on encoded dimensions, color series, diagram nodes/arrows |

**Stage 0 question to answer:** "What is the one-sentence takeaway message, and what's the consumption context?"

---

## §1 — Brand foundation (Stage 1)

Use when loading brand tokens at the start of a session.

| Source | What it gives you |
|---|---|
| `oligon-brand/SKILL.md` `<design_foundation>` | Cognitive-foundation citations (Cleveland & McGill, Treisman, Wagemans, Cowan, Franconeri, Crameri) — full apply rules |
| `oligon-brand/SKILL.md` `<svg_output>` | Authoritative font-family and font-size-ladder contract for SVG output |
| `oligon-brand/tokens/brand-tokens.json` | The palette, color cycles, typography ladder values to pin |
| `shared/references/figure_design_principles.md` §1 | One-line take-aways from the cognitive foundation (if you don't have time for the full block) |
| `shared/references/figure_design_principles.md` §2 (typography) | Type ladder + font-family + Type 42 embedding rules |
| `shared/references/figure_design_principles.md` §3 (color and palette) | Colorblind defaults, redundant encoding, grayscale test, two-channel fluorescence, no-improvised-hex |

**Stage 1 question to answer:** "What hex values, font-family string, and size ladder are valid for this session?"

---

## §2 — SVG authoring standards (Stage 2)

Use when drafting `figure.svg` v1.

| Source | What it gives you |
|---|---|
| `references/svg_authoring_standards.md` (this skill) | viewBox conventions, units, group naming, accessibility tags (`<title>`/`<desc>`) |
| `references/grid_and_layout.md` (this skill) | 8px / 4px grid discipline; coord-divisibility rule; alignment patterns |
| `shared/references/figure_design_principles.md` §6.1 (grid discipline) | Cross-skill grid rule |
| `shared/references/figure_design_principles.md` §6.2 (multi-panel layout) | Panel labels, shared axes, alignment, inter-panel gaps |
| `shared/references/figure_design_principles.md` §6.3 (legend placement) | Position priority; horizontal vs vertical; padding |
| `shared/references/figure_design_principles.md` §6.4 (whitespace and padding) | 8px-grid padding table |
| `templates/single_panel.svg`, `templates/two_panel_horizontal.svg` (this skill) | Canonical invariants — copy these, edit content, preserve structure |

**Stage 2 question to answer:** "Does the draft preserve viewBox, font-family, group structure, and accessibility tags?"

---

## §3 — Preflight rules (Stage 3)

Use to understand what the preflight script enforces, and to fix what it flags.

| Source | What it gives you |
|---|---|
| `references/anti_patterns.md` (this skill) | Expanded banned-attribute list with examples and fixes |
| `shared/references/figure_design_principles.md` §7 (anti-patterns) | Universal anti-pattern table (17 entries) |
| `shared/references/figure_design_principles.md` §2.1 (type ladder), §2.2 (font family), §3.5 (no improvised hex), §6.1 (grid) | Principles the preflight encodes mechanically |
| `oligon-brand/SKILL.md` `<svg_output>` | The grep checks (`font-family`, `font-size`) the preflight runs |
| `scripts/preflight_check.py --help` (this skill) | Operational reference: invocation, output schema |

**Stage 3 question to answer:** "What does this preflight finding mean, and which principle does it map to?"

---

## §4 — Rasterization (Stage 4)

Use when calling the SVG → PNG converter.

| Source | What it gives you |
|---|---|
| `oligon-brand/SKILL.md` `<svg_output>` "Visual Preview" | Canonical `render_svg_preview.sh` usage, options, font-rendering caveats |
| `oligon-brand/scripts/render_svg_preview.sh` | The script itself — wraps `rsvg-convert` with `--scale` option |

**Stage 4 question to answer:** "Did the PNG render, and at what scale should I render?"

---

## §5 — Visual critique (Stage 5)

Use when inspecting the rasterized PNG for problems no linter can catch.

| Source | What it gives you |
|---|---|
| `references/visual_critique_checklist.md` (this skill — Phase 3 deliverable) | Vision-loop critique rubric |
| `shared/references/pre_submission_checklist.md` | 20-point submission gate (cross-check after Stage 5) |
| `shared/references/figure_design_principles.md` §4 (accessibility) | WCAG contrast minimums; alt-text formula to verify against `<desc>` |
| `shared/references/figure_design_principles.md` §5.2 (direct labeling) | Visual check: are labels placed near their data? |
| `shared/references/figure_design_principles.md` §6.2–6.4 | Visual checks for panel alignment, legend placement, whitespace |
| `shared/references/figure_design_principles.md` §7 (anti-patterns) | Visual catch for things mechanizable rules might miss in edge cases |

**Stage 5 question to answer:** "What's wrong with this rendered figure that the linter can't see?"

---

## How to use this index

- **At session start (Stage 0):** read §0 and §1 in full
- **At each stage:** the SKILL.md workflow names which subsection to consult
- **When in doubt:** the **`shared/references/figure_design_principles.md`** doc is the canonical principles registry; this index is just a navigation aid

The shared doc carries source citations back to the originating skill/file. If you need depth, follow the citation; if you need a quick rule, this index points to it.
