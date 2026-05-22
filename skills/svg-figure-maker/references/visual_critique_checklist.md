# Visual Critique Checklist — Stage 5 of the render→inspect→fix loop

This is the rubric Claude walks when reading the rasterized `figure.preview.png` and
emitting `critique.json`. It targets the visual problems that the deterministic
preflight (`scripts/preflight_check.py`) cannot catch: clipping, overlapping
labels, hierarchy failures, alignment drift across panels, color rendering on
the target medium, line crispness at output resolution.

**Anchor doc:** every item below cites a section of
`skills/shared/references/figure_design_principles.md` — the principle is
authoritative, this checklist is its operational form for the vision loop.

**Output shape:** each finding emitted at Stage 5 MUST validate against
`schemas/critique_finding.schema.json`. The `category` enum values in this
checklist match the schema's `category` enum exactly — copy them verbatim.

**How to use this doc:**

1. After `Read`-ing `figure.preview.png`, walk the seven categories below in
   order. Each category has 2–4 questions; for each question, decide
   `pass | warn | fail`.
2. For every `fail` (and every `warn` you intend to record), emit one finding
   object: `id` = `F` + zero-padded ordinal (`F001`, `F002`, …), `severity`,
   `category`, `principle_ref` (section number, e.g. `§2.1`), `location`
   (group_id + element selector + viewBox coords if possible), `message`,
   `suggested_fix`.
3. After the walk, emit the array of findings as `critique.json`. The
   wrapper format the orchestrator expects:

   ```json
   {
     "iteration": 2,
     "svg_path": "figure.svg",
     "preview_path": "figure.preview.png",
     "findings": [ {...}, {...} ],
     "summary": {"fail": 1, "warn": 2, "info": 0}
   }
   ```

4. If `summary.fail == 0` and `summary.warn == 0`, the loop has converged —
   proceed to Stage 7 (finalize).

---

## Category 1: `text_legibility` → `figure_design_principles.md §2`

Where in the PNG to look: every label, axis tick, legend entry, annotation, title.

| Q | Question | Pass criterion | Anchor |
|---|---|---|---|
| 1.1 | Is every label fully visible (no clipping by panel edges, viewBox, or other elements)? | Every glyph fully inside the panel bounds | §2.1 |
| 1.2 | Are labels readable at the rendered scale (no overlapping characters or stacked labels)? | Adjacent labels separated by ≥ one x-height | §2.1 |
| 1.3 | Does the size ladder feel intentional (titles > subtitles > body > ticks/annotations)? | Larger numbers in the ladder reserved for higher-priority text | §2.1 |
| 1.4 | Does any text show a fallback / wrong font (e.g., serif rendered where Arial expected)? | All text appears sans-serif and consistent | §2.2 |

**Common fixes:** Bump up font size for clipped tiny labels; rotate or stagger crowded tick labels; move overlapping annotations to a callout with a leader line; ensure `font-family` is declared on the element (preflight catches the declaration; only the renderer can show whether the fallback chain worked).

---

## Category 2: `hierarchy` → `figure_design_principles.md §5`

Where in the PNG to look: overall composition; the takeaway-message question.

| Q | Question | Pass criterion | Anchor |
|---|---|---|---|
| 2.1 | Can a reader recognize the one-sentence takeaway message from the figure alone (no caption)? | Title or visual dominance carries the message | §5.1 |
| 2.2 | Is there exactly one focal element drawing the eye first? | One element clearly highest-contrast or largest | §5.2 |
| 2.3 | Are secondary elements visibly subordinate (size, weight, color)? | Visual rank matches conceptual rank | §5.2 |
| 2.4 | Are direct labels used instead of distant legends where possible? | Direct labels on data > legend in margin | §5.2 |

**Common fixes:** Promote the takeaway via title weight; demote noisy supporting elements by reducing stroke or saturating to a neutral palette token; move legend entries inline as direct labels.

---

## Category 3: `alignment` → `figure_design_principles.md §6`

Where in the PNG to look: panel edges, axis baselines, label rows, group boundaries.

| Q | Question | Pass criterion | Anchor |
|---|---|---|---|
| 3.1 | Do panels share consistent baselines / margins / gutters? | Panels visually snap to a common grid | §6.1, §6.2 |
| 3.2 | Are labels in repeated positions (e.g., per-panel titles) at identical y-coordinates? | Same role → same position across panels | §6.2 |
| 3.3 | Does any element appear "drifted" — off by a few pixels relative to neighbors? | Differences are intentional (e.g., shifted to avoid overlap), not random | §6.1 |
| 3.4 | Are panel labels (A, B, C…) at the same offset within each panel? | Identical (x, y) relative to panel origin | §6.2 |

**Common fixes:** Snap drifting coords to the 8px grid (preflight emits a per-coord report under `--strict-grid`); recompute panel origins so margins match; pin panel-label coords to a single shared variable.

---

## Category 4: `color_rendering` → `figure_design_principles.md §3`

Where in the PNG to look: every filled region, every stroke, the figure overall.

| Q | Question | Pass criterion | Anchor |
|---|---|---|---|
| 4.1 | Do brand colors render as intended (e.g., Brand Blue actually looks blue, not muddy or shifted)? | Colors match the palette swatches at print size | §3.5 |
| 4.2 | Is the color encoding colorblind-safe (no red/green confusion for categorical channels)? | Categories distinguishable in deuteranopia simulation OR encoded redundantly | §3.1, §3.2 |
| 4.3 | If converted to grayscale, would the figure still communicate? | Hierarchy survives grayscale conversion | §3.3 |
| 4.4 | If a two-channel fluorescence display is present, are channels magenta + green (not red + green)? | No red+green pair for fluorescence | §3.4 |

**Common fixes:** Swap red/green categorical pairs for a colorblind-safe palette token; add a redundant encoding (shape, dash pattern, direct label) so color isn't load-bearing; bump contrast of background-foreground pairs that look washed out at print size.

---

## Category 5: `line_crispness` → `figure_design_principles.md §8`

Where in the PNG to look: every stroke, every axis line, every connector.

| Q | Question | Pass criterion | Anchor |
|---|---|---|---|
| 5.1 | Do lines render cleanly at the rasterized scale (no fuzzy / pixel-soup edges)? | Strokes have crisp 1-px or wider edges | §8.2 |
| 5.2 | Are stroke widths used consistently (e.g., axis lines all the same weight)? | Same role → same stroke width | §6.1 |
| 5.3 | Are very fine lines (< 0.75pt at print size) avoided? | All visible strokes ≥ 0.75pt equivalent | §8.2 |

**Common fixes:** Re-rasterize at `--scale 3` to confirm whether the issue is the SVG or the preview DPI; thicken strokes that vanish at print resolution; collapse redundant strokes (e.g., border + fill of identical color) that compound into fuzz.

---

## Category 6: `composition_balance` → `figure_design_principles.md §5, §6`

Where in the PNG to look: whitespace, density, overall framing.

| Q | Question | Pass criterion | Anchor |
|---|---|---|---|
| 6.1 | Is whitespace intentional (margins, gutters, padding around dense regions)? | No element kissing the viewBox edge; gutters present between panels | §6.4 |
| 6.2 | Is the figure within its complexity budget (no overcrowding)? | Element count appropriate to figure type per §5.4 | §5.4 |
| 6.3 | Does the figure read top-to-bottom or left-to-right in a way that matches the message? | Reading order matches the conceptual flow | §5.5 |
| 6.4 | Is there negative space large enough to host a legend / annotation without colliding with data? | A clear zone exists where text can land | §6.3, §6.4 |

**Common fixes:** Move data away from edges (increase margins); split into two figures if over budget; reorient panels (vertical → horizontal) if reading order is wrong; demote / remove decorative elements that aren't carrying meaning.

---

## Category 7: `accessibility` → `figure_design_principles.md §4`

Where in the PNG to look: contrast, color reliance, redundant cues.

| Q | Question | Pass criterion | Anchor |
|---|---|---|---|
| 7.1 | Do all text/background pairs meet WCAG contrast (≥ 4.5:1 for body text, ≥ 3:1 for large)? | Visual estimate confirms contrast (and `<desc>` declares the figure is colorblind-aware where relevant) | §4.1 |
| 7.2 | Is color paired with at least one other encoding (shape, position, direct label) for every categorical axis? | Color is never the only differentiator | §3.2 |
| 7.3 | If the figure encodes uncertainty / significance, is there a non-color cue (asterisks, error bars, hatching)? | Non-color cue present where applicable | §3.2 |

**Common fixes:** Increase foreground/background contrast (preflight cannot test this — only the visual can confirm); add a shape or pattern channel; add direct asterisks for significance instead of relying on color of bars.

---

## Category 8: `other`

Use this category for findings that don't map cleanly into 1–7. Set
`principle_ref` to the most-relevant section if possible, otherwise `N/A`.
Examples: a rendering artifact specific to `rsvg-convert` that doesn't appear
in other renderers; a brief-level misalignment (the figure doesn't match the
intent from Stage 0).

---

## What this checklist deliberately does NOT cover

These are caught by `scripts/preflight_check.py` upstream — do not re-check
them visually, do not emit critique findings for them:

- Missing `viewBox`, `<title>`, `<desc>` (preflight: `viewbox_present`, `root_title_present`, `root_desc_present`)
- Off-palette hex colors (preflight: `palette_compliance`)
- Off-ladder font sizes, missing `font-family` (preflight: `text_font_size`, `text_font_family`)
- Banned filters (drop-shadow / blur / glow) (preflight: `no_banned_filters`)
- CSS named colors, color functions (preflight: `no_css_named_colors`, `no_color_functions`)
- Off-grid coords (preflight: `grid_alignment` — under `--strict-grid` for per-coord findings)
- Vertical writing-mode, `<script>`, `<foreignObject>` (preflight: `no_vertical_text`, `no_banned_elements`)

If the preflight pass-rate is < 100%, fix preflight findings first and re-run
Stage 3 before burning a vision iteration. The vision loop is the expensive
step; the deterministic linter is the safety net.

---

## Iteration discipline

- One pass through this checklist per iteration (Stage 5).
- Hard cap at 5 iterations (Stage 6). If the loop hasn't converged in 5,
  surface `status: needs_user_input` and stop — the problem is likely at
  Stage 0 (intent), not Stage 5 (craft).
- A finding that re-appears across iterations is a signal that the fix
  didn't take — re-read the SVG diff before re-rendering.
