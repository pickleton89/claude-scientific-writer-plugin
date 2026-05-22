---
name: svg-figure-maker
version: 0.1.0
description: "Deterministic, brand-aware SVG figure authoring with vision-iterated QA. Hand-written SVG XML by default; programmatic via drawsvg for parametric figures. The plugin's low-level SVG primitive — owns novel/custom figures and is composable from other visual skills."
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# SVG Figure Maker

<overview>
Build deterministic, brand-compliant SVG figures with a render→inspect→fix iteration loop. Hand-write SVG XML by default — that's where the visual loop pays off most. Switch to programmatic authoring (`drawsvg`) for parametric or repeated layouts. Every figure ships with a `.png` preview and a `.json` sidecar containing the brand variant, palette, iteration log, and a reproducibility hash. This is the plugin's low-level SVG primitive: other visual skills (scientific-schematics, research-posters, plotting-libraries) can compose on top of it.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- The user asks for an **SVG figure or diagram** that doesn't fit a more specific generator (data plot, Mermaid type, AI text-to-image)
- A **novel / custom illustration** is needed: conceptual diagrams, annotated overlays, custom panel compositions, decorative scientific elements
- A figure needs **deterministic styling** that survives re-runs (same brief → same SVG geometry)
- An existing image / SVG needs **brand-compliant annotations** (arrows, callouts, labels) layered on top
- A **parametric figure** (e.g., 6 panels with identical layout, varying content) needs programmatic generation
- Another skill needs to **delegate the SVG-emission step** to a brand-aware authority

Do NOT use this skill when:
- The user wants a **data-driven chart** (scatter, histogram, boxplot, heatmap, volcano) → use `plotting-libraries`
- The user names a **standard structured diagram type** (Mermaid flowchart, biological pathway, signal mechanism, network) → use `scientific-schematics`
- The user wants an **AI-generated graphical abstract** or text-to-visual synthesis → use `paperbanana`
- The user wants a **photorealistic / raster** image → use `generate-image`
- The user wants only the **brand tokens**, not a figure → use `oligon-brand` directly
</when_to_use>

<decision_framework>
## Decision Matrix

| The request involves… | Authoring mode | Skill |
|---|---|---|
| Novel / custom one-off figure (custom illustration, annotated overlay, conceptual diagram, panel composition not covered by other skills) | **Hand-written SVG XML** | This skill |
| Parametric / repeated layout (N panels with identical structure, varying content) | **Programmatic (drawsvg)** | This skill (see `references/programmatic_authoring.md` — Phase 4) |
| Data-driven plot (scatter, bar, box, violin, histogram, heatmap, volcano, forest, ECDF, KDE) | matplotlib / ggplot2 | `plotting-libraries` |
| Standard structured diagram (flowchart, sequence, ER, swimlane, biological pathway, signal mechanism, network) | Mermaid + AI | `scientific-schematics` |
| AI text-to-visual graphical abstract | AI (Gemini) | `paperbanana` |
| Photorealistic / raster generation | AI raster | `generate-image` |

### Within this skill: hand-written vs. programmatic

```
Is the figure a one-off custom illustration?
│
├─ Yes → HAND-WRITTEN SVG XML (default)
│         Use templates/single_panel.svg or templates/two_panel_horizontal.svg as the base
│         Edit with the Edit tool; iterate via the vision loop
│
└─ No → Is it parametric (N panels, same structure, varying data)?
         │
         ├─ Yes → PROGRAMMATIC (drawsvg)
         │         Write a Python script that emits SVG
         │         Iterate by editing the script, not the SVG
         │
         └─ No → Reconsider scope: this may be data viz (→ plotting-libraries)
                 or a standard diagram type (→ scientific-schematics)
```
</decision_framework>

<workflow>
## Workflow — the render→inspect→fix loop

**READ FIRST:** `references/design_practices_index.md` — stage-anchored reading list. At each stage below, the index names the exact references to consult.

**Working directory:** workflow commands below use skill-relative paths (`scripts/...`, `../oligon-brand/...`). Run them from `skills/svg-figure-maker/`, or adjust the paths to match your CWD. Plugin-wide convention.

---

### Stage 0: Intent capture

**Objective:** Lock the figure brief before any drawing.

**Steps:**
1. Confirm purpose (one-sentence takeaway message the figure must communicate)
2. Confirm dimensions (single-column / double-column / poster panel / slide ratio)
3. Confirm brand variant (project default vs. opt-out)
4. Confirm constraints: print-safe? colorblind-safe? grayscale-fallback required? venue-specific column width?
5. READ `design_practices_index.md` §0 → consult `shared/references/figure_vs_table_decision.md` and `communication_context_matrix.md` if the request is ambiguous between figure/table or could benefit from a different communication mode

**Exit Criteria:**
- [ ] One-sentence takeaway message recorded
- [ ] Dimensions in 8px-grid-aligned values recorded
- [ ] Brand variant chosen and pinned

---

### Stage 1: Brand load

**Objective:** Load brand tokens once; pin palette, fonts, font-size ladder, line widths for the rest of the run.

**Steps:**
1. Read `../oligon-brand/tokens/brand-tokens.json` (or the project-declared palette)
2. Extract: allowed hex palette, font-family list, font-size ladder (10/12/14/16pt), default line widths
3. Compute `tokens_hash` (SHA-256 of the canonical token subset) — record for the sidecar
4. READ `design_practices_index.md` §1 → `oligon-brand/SKILL.md` `<design_foundation>` and `<svg_output>` for the canonical font-family + size-ladder contract

**Exit Criteria:**
- [ ] Palette captured as a set of hex values
- [ ] Font-family string captured (must include `Arial, Helvetica, sans-serif` for Oligon)
- [ ] `tokens_hash` recorded

---

### Stage 2: Draft

**Objective:** Produce SVG v1 from a template (hand-written path) or from a `drawsvg` script (programmatic path).

**Steps:**
1. **Hand-written path:** copy the closest `templates/*.svg` into the working directory; rename to `figure.svg`; Edit content while preserving template invariants (viewBox, font-family declarations, group structure, `<title>` and `<desc>` for accessibility)
2. **Programmatic path:** see `references/programmatic_authoring.md` for `drawsvg` patterns (Phase 4)
3. READ `design_practices_index.md` §2 → `references/svg_authoring_standards.md` (viewBox, units, group naming, accessibility) and `references/grid_and_layout.md` (8px grid)
4. Apply the typography ladder from §2.1 of `shared/references/figure_design_principles.md` to every text element

**Exit Criteria:**
- [ ] `figure.svg` exists and parses (well-formed XML)
- [ ] viewBox set and matches Stage 0 dimensions
- [ ] At least one `<title>` and one `<desc>` element present (accessibility)

---

### Stage 3: Preflight (deterministic safety net)

**Objective:** Catch structural / brand / accessibility / grid violations before burning a vision iteration.

**Steps:**
1. Run `uv run python scripts/preflight_check.py figure.svg --tokens ../oligon-brand/tokens/brand-tokens.json -o preflight.json`
2. Read `preflight.json` — the linter returns `pass | warn | fail` per check plus structured findings keyed to `figure_design_principles.md` section numbers
3. If any `fail` finding: Edit `figure.svg` to fix; re-run preflight; loop until pass
4. `warn` findings are non-blocking but should be addressed where possible

**Exit Criteria:**
- [ ] All `fail` findings cleared
- [ ] `preflight.json` `overall: pass`

---

### Stage 4: Rasterize

**Objective:** Produce a PNG preview that Claude can `Read` for visual critique.

**Steps:**
1. Run `../oligon-brand/scripts/render_svg_preview.sh figure.svg`
2. Default output: `figure.preview.png` alongside the SVG
3. For dense labels or small text: re-run with `--scale 3`

**Exit Criteria:**
- [ ] PNG file exists at the expected path
- [ ] PNG file is non-empty

---

### Stage 5: Visual critique (the killer feature)

**Objective:** Visually inspect the rasterized figure against the critique checklist; emit structured findings.

**Steps:**
1. `Read` the `figure.preview.png` file (Claude reads PNGs directly via the Read tool)
2. Walk `references/visual_critique_checklist.md` (Phase 3 deliverable) — for v0.1 use the inline checklist below:
   - **Text legibility:** every label readable; nothing clipped, overlapping, or truncated
   - **Hierarchy:** the takeaway message is recognizable from the figure alone
   - **Alignment:** elements snap to the 8px grid; panels align cleanly
   - **Color rendering:** brand colors render correctly; no muddy / off-palette tones
   - **Line crispness:** strokes render cleanly at the rasterized resolution
   - **Composition balance:** whitespace is intentional (§6.4 of `figure_design_principles.md`); no crowding
   - **Accessibility:** color isn't the only differentiator; legible in grayscale
3. Emit findings as JSON validating against `schemas/critique_finding.schema.json` — each finding names the issue, its location in the SVG (group id or element selector), and the suggested fix
4. READ `design_practices_index.md` §5 → `shared/references/pre_submission_checklist.md` for the 15-point gate cross-check

**Exit Criteria:**
- [ ] `critique.json` written and schema-valid
- [ ] Number of findings recorded for iteration log

---

### Stage 6: Iterate

**Objective:** Apply critique findings; loop to Stage 3 until convergence.

**Steps:**
1. If `critique.json` has any findings: Edit `figure.svg` (or `figure.py` for programmatic) to address each one
2. Append a row to the iteration log (sidecar `figure.json` `iterations[]`): iteration number, finding count, primary fixes applied
3. Return to Stage 3 (preflight)
4. **Hard cap: 5 iterations.** If not converged, write `figure.json` `status: needs_user_input` and stop for user input

**Exit Criteria:**
- [ ] `critique.json` has zero `fail` findings, OR iteration cap reached
- [ ] Iteration log updated

---

### Stage 7: Finalize

**Objective:** Emit the three-file deliverable.

**Steps:**
1. Run `uv run python scripts/finalize.py figure.svg` (or invoke the same flow inline if the script is not yet present in Phase 2)
2. Verify three files exist: `figure.svg`, `figure.preview.png`, `figure.json`
3. `figure.json` is schema-valid against `schemas/figure_metadata.schema.json` and records: brand variant, palette, grid unit, font-family, font-size ladder, iteration count, iteration log, `tokens_hash`, and any `warn` findings carried forward
4. Report final iteration count and any deferred warnings to the user

**Exit Criteria:**
- [ ] Three files present
- [ ] `figure.json` schema-valid
- [ ] User-facing report names the iteration count

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Preflight pass rate | 100% (no `fail`) | 100% with 0 `warn` | 100% with 0 `warn` and zero off-grid coords |
| Iterations to converge (Stage 6) | ≤ 5 | ≤ 3 | ≤ 2 |
| Banned attributes present | 0 | 0 | 0 |
| Off-palette hex colors | 0 | 0 | 0 |
| Off-grid coordinates (8px grid) | < 10% of total | 0 | 0 |
| Text elements without explicit `font-family` | 0 | 0 | 0 |
| Text elements below 10pt | 0 | 0 | 0 |
| Schema validity of `figure.json` sidecar | valid | valid | valid |

Cross-reference: `QUANTIFICATION_THRESHOLDS.md` §2 (Visual Quality) and §9 (Figure & Plot Quality).

**Completion Checklist:**
- [ ] `figure.svg` exists, well-formed, viewBox set, accessibility tags (`<title>`/`<desc>`) present
- [ ] `figure.preview.png` exists and was visually inspected via `Read`
- [ ] `figure.json` sidecar exists, schema-valid, includes `tokens_hash` and iteration log
- [ ] All preflight `fail` findings cleared
- [ ] Final iteration count ≤ 5
- [ ] Brand verifier passes (font-family + font-size grep checks from `oligon-brand/SKILL.md` `<svg_output>`)

</success_criteria>

<scope>
## Scope

**In Scope:**
- Hand-authored SVG figures (novel illustrations, conceptual diagrams, annotated overlays, custom panel compositions)
- Programmatic SVG via `drawsvg` for parametric / repeated layouts
- Render→inspect→fix iteration loop with deterministic preflight + visual critique
- Brand-token enforcement (palette, fonts, size ladder, line widths)
- Schema-validated metadata sidecar for reproducibility
- SVG primitive interface for other visual skills to compose on

**Out of Scope** (use specialized resources):
- Data-driven plots (scatter, bar, box, violin, histogram, heatmap, volcano, forest) → use `plotting-libraries`
- Standard structured diagram types (Mermaid flowchart, biological pathway, signal mechanism, network) → use `scientific-schematics`
- AI text-to-visual generation → use `paperbanana`
- Photorealistic / raster image generation → use `generate-image`
- Brand token definitions or adapter authoring → use `oligon-brand`
- Per-venue figure spec compliance (column widths, DPI floors) → cross-reference `venue-templates`

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Skipping the preflight before the vision loop

**Anti-pattern:**
Rasterize and visually critique a figure that fails basic structural checks (missing viewBox, off-palette hex, missing font-family). Burns iterations on problems the linter would catch instantly.

**Solution:**
ALWAYS run `scripts/preflight_check.py` first. It's deterministic, fast, and catches everything mechanical. Reserve the vision loop for things only a viewer can judge: clipping, alignment, hierarchy, composition.

---

### 2. Improvising hex colors

**Anti-pattern:**
```xml
<rect fill="#3498DB"/>  <!-- looks "close enough" to Brand Blue -->
```

**Solution:**
Only use hexes from `tokens/brand-tokens.json` (or the project-declared palette). The preflight checker rejects any off-palette hex. If you need a color that isn't in the palette, the answer is to use a palette color, not to invent one.

---

### 3. Off-grid coordinates ("close enough" placement)

**Anti-pattern:**
```xml
<rect x="42" y="37" width="313" height="98"/>
```
Numbers ending in 1, 2, 3, 5, 6, 7, 9 on the 8px grid signal hand-placed values that drifted off-grid.

**Solution:**
All coordinates, widths, heights, padding, gaps divisible by 8 (figure work) or 4 (dense diagram work). If preflight flags an off-grid coord, snap to the nearest multiple. Saves alignment debugging downstream.

---

### 4. Missing accessibility tags

**Anti-pattern:**
Emitting an SVG with no `<title>` or `<desc>` — screen-readers can't surface anything, and the alt-text formula (§4.2 of `figure_design_principles.md`) has nothing to anchor to.

**Solution:**
Every SVG has at minimum one `<title>` (one-line) and one `<desc>` (the 2-sentence alt-text formula: takeaway message + key supporting evidence). The templates include both as placeholders — fill them, don't delete them.

---

### 5. Letting the iteration loop run unbounded

**Anti-pattern:**
Keep iterating until the figure "feels right" without a cap. Most figures that haven't converged in 5 iterations have a brief-level problem, not a craft problem.

**Solution:**
Hard cap at 5 iterations. If the cap is hit, stop and surface `status: needs_user_input` to the user with the current `critique.json`. Usually the right move is to clarify Stage 0 (intent), not to keep iterating.

---

### 6. Duplicating brand styling content in the figure

**Anti-pattern:**
Hand-writing palette hexes, font-family strings, size values inline as magic numbers throughout the SVG. Drift inevitable across multiple figures.

**Solution:**
Use the templates as the source of truth for invariants (viewBox, font-family declaration, group structure). Edit content, preserve invariants. For programmatic figures, load tokens once from `tokens/brand-tokens.json` and reference them everywhere.

</anti_patterns>

<templates>
## Output Templates

This skill ships with two SVG templates (more deferred to later phases). Each carries the canonical invariants: viewBox in 8px-grid-aligned units, `font-family="Arial, Helvetica, sans-serif"` on every text element, `<title>` and `<desc>` placeholders for accessibility, `<g>` group structure for logical sub-elements.

| Template | Use when |
|---|---|
| `templates/single_panel.svg` | One panel, one focal subject, dimensions ~640×480px |
| `templates/two_panel_horizontal.svg` | Two-panel comparison (e.g., before/after, method A vs. method B), dimensions ~800×400px with A on the left, B on the right |

Deferred to later phases: `two_panel_vertical.svg`, `three_panel_grid.svg`, `annotated_overlay.svg`.

### Sidecar metadata template (`figure.json`)

Schema: `schemas/figure_metadata.schema.json`. Excerpt:

```json
{
  "figure_id": "figure",
  "version": "0.1.0",
  "brand_variant": "oligon",
  "tokens_hash": "sha256:...",
  "palette": ["#222222", "#2DB2E8", "#666666"],
  "font_family": "Arial, Helvetica, sans-serif",
  "font_size_ladder_pt": [10, 12, 14, 16],
  "grid_unit_px": 8,
  "dimensions_px": [800, 600],
  "iterations": [
    {"i": 1, "findings": 4, "primary_fixes": ["axis label clipping", "off-grid coord"]},
    {"i": 2, "findings": 1, "primary_fixes": ["legend overlap"]},
    {"i": 3, "findings": 0, "primary_fixes": []}
  ],
  "final_iteration": 3,
  "warn_carry_forward": [],
  "status": "complete"
}
```

</templates>

<cross_references>
## Cross-References

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

### Uses (Input From)

| Skill | Relationship |
|-------|-------------|
| `oligon-brand` | Brand tokens at Stage 1; `scripts/render_svg_preview.sh` at Stage 4 — **canonical**, do not duplicate |
| `shared/references/figure_design_principles.md` | Authoritative principles (typography, color, accessibility, anti-patterns, grid, layout) — every workflow stage references a section |
| `shared/references/pre_submission_checklist.md` | 15-point operational gate cross-checked at Stage 5 |
| `shared/references/figure_vs_table_decision.md` | Stage 0 sanity check |
| `shared/references/communication_context_matrix.md` | Stage 0 complexity calibration |

### Feeds (Output To)

| Skill | Relationship |
|-------|-------------|
| `markdown-to-pdf` | Embeds SVG figures in PDF reports |
| `scientific-slides` | Embeds SVG figures in PPTX / PDF decks |
| `research-posters` | Composes SVG panels into posters |
| `paper-2-web` | Embeds SVG in HTML papers |
| `research-paper-summarizer` | Embeds SVG in HTML / PDF summaries |

### Related

| Skill | Relationship |
|-------|-------------|
| `scientific-schematics` | Owns structured diagram types (Mermaid flowchart, pathway, mechanism). May delegate the final SVG-emission step to this skill in future. See `references/figure_type_catalog.md` for the routing table |
| `plotting-libraries` | Owns data-driven plots (matplotlib / ggplot2). Outputs SVG that can be post-processed by this skill's preflight for brand enforcement |
| `paperbanana` | AI text-to-visual (raster). Complementary, not overlapping |
| `generate-image` | Raster AI generation. Complementary, not overlapping |
| `visual-design` | Deprecated in plugin v1.2.0 (April); its content was redistributed across `oligon-brand` `<design_foundation>`, `shared/accessibility/`, `plotting-libraries/scripts/`, and `venue-templates/references/`. Phase 1 of this skill's build added `shared/references/figure_design_principles.md` as a curated cross-skill index across those locations |

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `references/design_practices_index.md` | Curated stage-anchored reading list with section-level pointers into the shared design-principles doc, oligon-brand, and pre_submission_checklist |
| `references/svg_authoring_standards.md` | viewBox conventions, units, group naming, accessibility tags |
| `references/grid_and_layout.md` | 8px-grid discipline; coord-divisibility rule; alignment patterns |
| `references/anti_patterns.md` | Banned attributes; "AI slop" markers; expanded checklist with examples |
| `references/visual_critique_checklist.md` | Vision-loop critique rubric — 7 categories with `principle_ref` anchors and the schema-compatible finding shape |
| `references/figure_type_catalog.md` | Routing table for SVG figures across visual skills (Phase 6 deliverable) |
| `references/programmatic_authoring.md` | `drawsvg` patterns for parametric figures (Phase 4 deliverable) |
| `templates/single_panel.svg` | Single-panel SVG template |
| `templates/two_panel_horizontal.svg` | Two-panel horizontal-comparison template |
| `scripts/preflight_check.py` | Deterministic SVG linter → JSON findings |
| `scripts/render_and_inspect.py` | Render-loop orchestration: runs preflight + `render_svg_preview.sh`, emits unified iteration report with `next_step` hint and critique-category seed |
| `scripts/finalize.py` | Stage 7 finalization: emits `figure.svg` + `figure.preview.png` + `figure.json`; sidecar validated against `figure_metadata.schema.json` before write |
| `schemas/figure_metadata.schema.json` | Sidecar `figure.json` shape |
| `schemas/critique_finding.schema.json` | Vision-loop finding shape |

</references>
