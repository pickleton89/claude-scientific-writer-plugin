# Figure Type Catalog — routing across visual skills

**Status:** Phase 6 deliverable (closes the spicy-stonebraker plan). Scope is **routing + opt-in coupling**, not refactors of the four neighbour skills.

This document answers two questions:

1. **Where does an SVG figure request go?** — the routing table below picks the right skill from the figure type.
2. **Where does `svg-figure-maker` leak into existing skills?** — the leak-investigation section documents each neighbour's current SVG behaviour, the opt-in integration path, and whether any auto-coupling is appropriate (spoiler: no, not in v1).

For the deterministic router behaviour (keywords, regex, negative-keyword fences, canonical tests) see `skills/skill-router/skill_triggers.yaml` and the "Figure & Visual Creation" subtree in `skills/SKILL_ROUTER.md`. This document is the human-readable companion.

---

## Routing table — pick a skill from the figure type

| Figure type | Skill | Why |
|---|---|---|
| Novel custom illustration (no standard type fits) | **`svg-figure-maker`** | Owns hand-authored SVG XML with vision-loop QA |
| Annotated overlay on an existing image / SVG (arrows, callouts, labels) | **`svg-figure-maker`** | Hand-authored layer with brand enforcement |
| Custom panel composition not produced by other skills | **`svg-figure-maker`** | Plugin's low-level SVG primitive |
| Parametric / repeated layout (N panels, identical structure, varying data) | **`svg-figure-maker`** (programmatic path) | `drawsvg` script + byte-identical determinism contract |
| Mermaid flowchart / sequence / ER / swimlane | `scientific-schematics` | Owns Mermaid pipeline; emits SVG via `mermaid_renderer.py` |
| Biological pathway, signal mechanism, network diagram | `scientific-schematics` | Owns structured diagram types |
| Data-driven plot (scatter, bar, box, violin, histogram, heatmap, volcano, forest, ECDF, KDE) | `plotting-libraries` | matplotlib / ggplot2 with brand styling |
| AI text-to-visual graphical abstract | `paperbanana` | AI synthesis from prose |
| Photorealistic / raster generation | `generate-image` | AI raster pipeline |
| Poster (multiple panels, venue spec) | `research-posters` | Compositor that pulls from the skills above |

### Tie-breakers

When two skills could apply:

- **"SVG" named as the medium + diagram-type keyword** → `svg-figure-maker` wins (router priority 5 + negative fences). Example: "draw an SVG of a kinase signalling cascade" → `svg-figure-maker`, not `scientific-schematics`.
- **Diagram-type keyword alone, no "SVG"** → `scientific-schematics` wins. Example: "make a Mermaid flowchart of the workflow" → `scientific-schematics`.
- **"Plot" / "chart" / "histogram" / data-shape vocabulary** → `plotting-libraries` wins (svg-figure-maker's negative-keyword fence blocks the route).
- **"Generate" / "AI" / "graphical abstract"** → `paperbanana`.
- **"Photo" / "photorealistic" / "raster"** → `generate-image`.

---

## Leak investigation — `svg-figure-maker` × four neighbours

Each row asks: *does this skill already emit SVG?* If yes, *how could `svg-figure-maker`'s preflight + vision loop polish that output?* And: *should the coupling be automatic, opt-in, or none?*

### 1. `scientific-schematics`

**Current SVG behaviour:** `scripts/utils/mermaid_renderer.py:72` declares `output_format: Literal["png", "svg", "pdf"]`; at line 394 the `"svg"` branch writes Mermaid-rendered SVG content directly to disk. PNG/PDF go through `cairosvg`. So the skill already produces SVG bytes — the Mermaid pipeline just doesn't currently run them through preflight or a vision loop.

**Leak surface:** every Mermaid SVG is a candidate for brand enforcement (font-family declarations, palette, accessibility tags) and visual critique (label clipping at long node text, arrow overlap on dense graphs). The mechanical wins (preflight) are large; the vision-loop wins are smaller, because Mermaid layout is generated, not hand-placed.

**Decision:** **opt-in, not automatic.** `scientific-schematics` keeps Mermaid as its primary path. A future opt-in step ("polish with svg-figure-maker") can pipe the rendered SVG through `svg-figure-maker/scripts/preflight_check.py` for brand-token enforcement before delivery. Do not auto-couple in v1 — Mermaid users expect Mermaid output, and the preflight's grid check is calibrated for hand-authored SVG, not graph-layout SVG (Mermaid's coords come from `dagre`, not from an 8px grid).

**v1 action:** none. Document the opt-in path here and in `scientific-schematics`' `<cross_references>` if/when wired.

**Eventually owned by:** `scientific-schematics`. `svg-figure-maker` is a consumable post-process, not a takeover.

---

### 2. `plotting-libraries`

**Current SVG behaviour:** `plotting-libraries/SKILL.md` `<svg_export>` already mandates SVG as the preferred output for deep-research reports (lines 60–82). `matplotlib.savefig('figure.svg')` and `ggsave('figure.svg', ...)` are the canonical save commands. Critically, the skill already prescribes a **post-export verification step** using `../oligon-brand/scripts/render_svg_preview.sh` — the same rasterizer `svg-figure-maker` uses in Stage 4. So `plotting-libraries` is already doing a vision-loop in spirit; it just stops at the rasterize-and-Read step without running `preflight_check.py`.

**Leak surface:** matplotlib/ggplot2 SVG output can drift on brand fonts (font-family stripping in headless rendering), can write off-palette colors (custom `cmap` choices), and rarely emits `<title>` / `<desc>` accessibility tags. `svg-figure-maker`'s preflight catches all three deterministically.

**Decision:** **opt-in post-process, leave routing decisions to the user per-call.** A user who wants a data plot routes to `plotting-libraries`; if the saved SVG fails brand grep checks, they can run `svg-figure-maker/scripts/preflight_check.py figure.svg --tokens ../oligon-brand/tokens/brand-tokens.json` manually as a remediation step. Do not auto-couple — wrapping every plot in preflight would slow the common case and the off-grid check would fire constantly on plot coords (which legitimately don't snap to 8px because matplotlib computes them from data).

**v1 action:** none. `plotting-libraries`' existing `<svg_export>` block already wires `render_svg_preview.sh`; no edits needed. Cross-reference the opt-in preflight path here.

**Eventually owned by:** `plotting-libraries`. `svg-figure-maker`'s preflight is the optional remediation tool.

---

### 3. `research-posters`

**Current SVG behaviour:** `research-posters/SKILL.md:19` already declares: *"Every poster MUST include 2-3 AI-generated figures using `scientific-schematics`."* The poster skill is a **compositor** — it pulls figures from other skills (today: `scientific-schematics` for diagrams, `plotting-libraries` for data plots, `paperbanana` for graphical abstracts) and arranges them on a venue-spec poster canvas.

**Leak surface:** posters often need **custom panels that no other skill produces** — decorative scientific elements, conceptual sub-illustrations, custom annotated overlays bridging two data panels, schematic headers. Today those gaps are either filled by hand-editing PDFs/PPTX or by stretching `scientific-schematics` past its diagram-type vocabulary.

**Decision:** **declared dependency, not automatic.** `research-posters` should list `svg-figure-maker` in its `<cross_references>` as the source for "custom poster panels not produced by other skills". The poster builder still drives — it asks `svg-figure-maker` for a panel when no other skill fits, and embeds the resulting `figure.svg` in the poster layout. This is the same pattern as the existing `scientific-schematics` dependency.

**v1 action:** **DONE in Phase 6** — `research-posters/SKILL.md` `<cross_references>` now lists `svg-figure-maker` as the source for custom panels not produced by other skills, with a back-pointer to this catalog for the routing rule.

**Eventually owned by:** `research-posters` (compositor) + `svg-figure-maker` (panel producer). Clean separation.

---

### 4. `paperbanana` / `generate-image`

**Current SVG behaviour:** both produce **raster output** (PNG/JPEG), not SVG. `paperbanana` is an AI text-to-visual pipeline (Gemini); `generate-image` is photorealistic raster generation.

**Leak surface:** none. SVG is not the output format. The vision loop is a meaningful complement (both skills could benefit from rasterized self-inspection), but that's an internal-to-each-skill concern, not a coupling to `svg-figure-maker`.

**Decision:** **no leak; complementary skills.** Routing is already disambiguated by `svg-figure-maker`'s negative-keyword fences (`graphical abstract`, `visual abstract`, `visual summary`, `photorealistic`, `dall-e`, `ai generated`/`ai-generated` all block the svg-figure-maker route — see `skill_triggers.yaml`).

**v1 action:** none.

**Eventually owned by:** each skill independently. No integration warranted.

---

## Summary table — leak decisions at a glance

| Neighbour | Emits SVG? | Coupling to `svg-figure-maker` | v1 action |
|---|---|---|---|
| `scientific-schematics` | Yes (Mermaid → SVG) | **Opt-in post-process** for brand preflight; vision loop not auto-applied | None — document opt-in path |
| `plotting-libraries` | Yes (matplotlib / ggplot2 → SVG) | **Opt-in preflight** as remediation; existing `<svg_export>` already wires the rasterizer | None — cross-reference here |
| `research-posters` | No (compositor) | **Declared dependency** for custom panels not produced by other skills | DONE in Phase 6 — listed in `research-posters/<cross_references>` |
| `paperbanana` | No (raster) | None | None |
| `generate-image` | No (raster) | None | None |

**Net Phase 6 outcome:** zero refactors of neighbour skills, three opt-in / declarative integration paths documented; the lowest-cost coupling (research-posters dependency declaration) landed alongside this catalog. Routing already enforced deterministically by `skill_triggers.yaml` (Phase 5). Any further coupling work (preflight post-process hooks into `scientific-schematics` / `plotting-libraries`) happens in a separate plan if and when the user requests it.

---

## When this catalog needs an update

- A new visual skill is added that produces or consumes SVG → add a row to the routing table and (if applicable) a leak-investigation section
- `scientific-schematics` or `plotting-libraries` ships an opt-in `svg-figure-maker` polish step → mark the "v1 action" as DONE and link the integration commit
- `research-posters` further evolves the declared dependency (e.g., explicit Stage instructions for invoking `svg-figure-maker`) → update the row here
- The router gains a new tie-breaker rule → mirror the rule in the "Tie-breakers" section above
