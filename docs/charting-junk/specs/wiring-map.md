I now have everything I need. I have read both reports, the existing shared assets, all seven target skills, and both router files. Let me produce the precise cross-link wiring deliverable.

A few key facts that shape the wiring (so the insertions drop in cleanly):

- The new doc will live at `skills/shared/references/ai_figure_slop.md` (sibling to `figure_design_principles.md` and `pre_submission_checklist.md`). The new gate script will be `skills/svg-figure-maker/scripts/check_ai_figure_slop.py` (Track A/B/C, exact-vs-source) — I reference these by their settled paths.
- `oligon-brand/SKILL.md` is a GENERATED/vendored file ("do not edit here"). So its anti-slop wiring must go into the cross-skill `figure_design_principles.md` and `pre_submission_checklist.md` registries that point at it, not into the vendored SKILL.md body. I flag this explicitly and route the oligon-brand entry there.
- The reports' governing insight: our own output uses EXACT deterministic checks against ground-truth data/source; only Track D (inbound audit) uses the forensic/OCR/rubric stack and stays advisory.

Here is the deliverable.

---

# Anti-slop cross-link wiring — per-skill drop-in spec

**New assets these insertions assume (settled paths):**
- `skills/shared/references/ai_figure_slop.md` — the anti-slop reference (categorical-tell-dominant vector; provisional/uncalibrated thresholds; Track A/B/C exact-vs-source checks; Track D advisory rubric).
- `skills/svg-figure-maker/scripts/check_ai_figure_slop.py` — deterministic gate for SVG output (garbled/lexically-void text, raw-index labels, default-palette fingerprint, parts-not-summing). Emits a **vector of flagged sub-scores with severities**, never a composite.
- `skills/plotting-libraries/scripts/validate_data.py` — already hosts `check_continuous_as_bars` / `check_riskratio_as_bars`; gains `check_encoding_value_fidelity` / `check_parts_sum_to_whole` (exact, against the DataFrame we already hold).

Each entry below is `{skill, file, anchor, insertion_text, workflow_step_edit}`.

---

## 1. oligon-brand

**file:** `skills/oligon-brand/SKILL.md` is a **GENERATED, vendored file** (lines 10–12: `<!-- GENERATED FILE - do not edit here. Vendored from oligon-brand-core ... -->`). **Do NOT edit it directly** — edits are overwritten by `scripts/sync_brand_core.sh`. The two oligon-brand-facing insertions therefore land in the cross-skill registries that *point at* oligon-brand. (If you want the change to survive in the SKILL.md body, it must be made upstream in `oligon-brand-core` and re-synced; that is out of scope for this wiring.)

### 1a. Cross-link — in `figure_design_principles.md` (the shared registry oligon-brand's `<figure_integrity>` already maps onto)

**file:** `skills/shared/references/figure_design_principles.md`
**anchor (quoted existing line, §7 anti-patterns table, last row):**
> `| 14 | Optimizing for data-to-ink ratio mechanically | Tufte's rule mis-applied removes useful labels | Apply Fujii's signal-to-noise reframing: keep ink that supports the *takeaway*, not just ink that "represents data" |`

**insertion_text** (append as new rows 15–16 immediately after row 14, before the `**Sources:**` line):
```
| 15 ⚑ | Lexically-void / garbled label text (`diƨlocttal`, `2xℇpens`), or axis ticks rendered as raw sequence indices (1,2,3…) instead of real categories | Near-categorical AI-generation tell (Frontiers/Bik 2024); a competent human never emits void glyph-strings | Replace with real terms from the source data; for our own output this is caught EXACTLY by `check_ai_figure_slop.py` against the known labels — see `ai_figure_slop.md` |
| 16 ⚑ | Encoding contradicts the printed value (bar height / slice angle / point position ≠ its number), or parts-of-whole that do not sum (pie ≠ 100%, stacked totals don't reconcile) | Covert Class-B tell: rendering looks correct, the encoding contract is broken (Woo; practitioner) | We hold the source data — verify EXACTLY (`validate_data.py::check_encoding_value_fidelity`, `check_parts_sum_to_whole`). Never an image-OCR step for our own figures. See `ai_figure_slop.md` |
```
Also extend the table's `**Sources:**` line:
- **anchor:** `**Sources:** `oligon-brand/SKILL.md` `<anti_patterns>` §1–7; `diagram-design-skill.md` §4 lines 96–113; `pre_submission_checklist.md` §13–14.`
- append: ` Rows 15–16: `ai_figure_slop.md` (categorical-tell-dominant; two-sided/down-weighted aesthetic signals).`

And add a one-line pointer to the "How to use this document" header block so consumers discover it:
- **anchor:** `> **One-line take-aways for consumers who don't have time to read the full block:**` — *(no, use the bullet list above it)* — actual anchor:
> `- For the unified pre-submission gate (15-point checklist), see `pre_submission_checklist.md` in this directory`

- **insertion_text** (new bullet immediately after):
```
- For the AI-figure-slop guardrail (categorical tells dominate; aesthetic signals are weak, down-weighted, and two-sided; thresholds provisional/uncalibrated; never minimize ink), see `ai_figure_slop.md` in this directory
```

### 1b. Workflow/QA-step edit — `pre_submission_checklist.md` (oligon-brand's preflight gate routes through this)

oligon-brand's own `<preflight>` and `<workflow>` step 4–5 are in the vendored body; the editable shared gate it shares with every visual skill is `pre_submission_checklist.md`. Add a 16th item + tooling-table rows there (this is **the** post-design/QA edit for oligon-brand, and is consumed by every other skill too):

- **anchor (quoted existing line, end of the Scientific Rigor block):**
> `**Verify:** matplotlib `ax.errorbar(x, y, yerr=...)` or ggplot2 `geom_pointrange(aes(ymin=lower, ymax=upper))`.`

- **insertion_text** (new section appended after item 14, before `## Visual Quality`):
```
---

## Generative-Artifact Integrity (anti-slop)

### 14b. No lexically-void labels, raw-index ticks, or encoding↔value mismatch

**Check:** No garbled/void label glyph-strings; no axis ticks rendered as raw sequence indices (1,2,3…) where real categories exist; bar heights / slice angles / point positions match their printed values; parts-of-whole sum to 100%.
**Why:** These are the near-categorical AI-generation tells (Frontiers/Bik 2024; Class-B encoding-contract breaks). They DOMINATE; aesthetic/chartjunk signals are weak, two-sided, and must NOT trigger an "AI" verdict on their own (Bateman CHI 2010 — embellishment does not impair comprehension; never minimize ink). Thresholds are provisional/uncalibrated; the gate emits a vector of flagged sub-scores, never a single slop score.
**Verify:** For figures we generate, run EXACT checks against the ground-truth data/source we already hold — `svg-figure-maker/scripts/check_ai_figure_slop.py` (SVG text/palette/labels) and `plotting-libraries/scripts/validate_data.py::check_encoding_value_fidelity` / `check_parts_sum_to_whole`. Do NOT use OCR / forensic CV on our own output (image→data recovery is the reports' unreliable step — SciFigDetect fails zero-shot). The forensic/OCR/rubric stack is for the inbound-audit (Track D) path only and stays advisory. Full rationale and the per-track split: `figure_design_principles.md` §7 rows 15–16 and `ai_figure_slop.md`.
```
- **anchor (Tooling cross-references table, last row):**
> `| #14 Risk-ratio-as-bars | `plotting-libraries/scripts/validate_figure.py::check_riskratio_as_bars` |`

- **insertion_text** (replace the two existing rows that mis-point at `validate_figure.py` AND add the new row — **fixes the #13/#14 pointer bug noted in the brief**):
```
| #13 Continuous-as-bars | `plotting-libraries/scripts/validate_data.py::check_continuous_as_bars` |
| #14 Risk-ratio-as-bars | `plotting-libraries/scripts/validate_data.py::check_riskratio_as_bars` |
| #14b Encoding↔value, parts-sum (anti-slop) | `plotting-libraries/scripts/validate_data.py::check_encoding_value_fidelity`, `check_parts_sum_to_whole` |
| #14b Garbled/void labels, raw-index ticks, default-palette (SVG, anti-slop) | `svg-figure-maker/scripts/check_ai_figure_slop.py` |
```
(The first two rows replace the current `validate_figure.py` rows at lines 149–150 — both currently point to the wrong file.)

---

## 2. plotting-libraries

**file:** `skills/plotting-libraries/SKILL.md`

### 2a. Cross-link

- **anchor (quoted existing line, `<reference_guides>` → "Cross-Skill Design References"):**
> `- **[../shared/references/pre_submission_checklist.md](../shared/references/pre_submission_checklist.md)**: 15-point unified quality gate (Q0 = "should this be a table?")`

- **insertion_text** (new bullet immediately after):
```
- **[../shared/references/ai_figure_slop.md](../shared/references/ai_figure_slop.md)**: AI-figure-slop guardrail. Because we hold the source DataFrame, encoding↔value fidelity and parts-sum closure are checked EXACTLY against the data (`scripts/validate_data.py::check_encoding_value_fidelity`, `check_parts_sum_to_whole`) — not via image OCR. Categorical tells (raw-index tick labels, geometry-contradicts-label) dominate; chartjunk/default-palette signals are weak, two-sided, and down-weighted (do NOT strip decoration to "minimize ink" — Bateman). Thresholds provisional/uncalibrated.
```
Mirror it in `<cross_references>`:
- **anchor:** `- **[shared/references/figure_design_principles.md](../shared/references/figure_design_principles.md)**: Shared figure-making principles consumed by all visual skills — typography ladder, colorblind palettes, accessibility minimums, anti-patterns, grid discipline. Consult §2 (typography), §3 (color), §5.3 (chart conflict resolution), §7 (anti-patterns) when choosing plot types and palettes.`
- **insertion_text** (append `§7` reference and a new sentence — minimal: add a bullet after it):
```
- **[shared/references/ai_figure_slop.md](../shared/references/ai_figure_slop.md)**: Anti-slop gate. Run `scripts/validate_data.py` (now hosts `check_continuous_as_bars`, `check_riskratio_as_bars`, `check_encoding_value_fidelity`, `check_parts_sum_to_whole`) as the data-side post-design check.
```

### 2b. Workflow/QA-step edit — `<success_criteria>` "Validation Workflow"

- **anchor (quoted existing line):**
> `5. **Final review**: Zoom to 100% to verify text readability at final print size`

- **workflow_step_edit** (append step 6):
```
6. **Anti-slop data check (post-design):** Run `uv run python scripts/validate_data.py <data.csv-or-df>` to confirm — against the SOURCE data we already hold — that bar heights / point positions / slice angles match their printed values (`check_encoding_value_fidelity`), parts-of-whole sum (`check_parts_sum_to_whole`), tick labels are real categories not raw indices, and continuous-as-bars / riskratio-as-bars are not used. These exact checks replace the unreliable image→data recovery step for our own output. The script emits a vector of flagged sub-scores with severities — never a single slop score. Aesthetic/chartjunk flags are advisory and two-sided: do not remove labels or decoration to chase a data-ink target (Bateman). See `../shared/references/ai_figure_slop.md`.
```
Also append a checkbox to the `**Quality Checklist:**` block:
- **anchor:** `- [ ] No chart junk (unnecessary gridlines, borders, 3D effects)`
- **insertion_text** (new checkbox after it):
```
- [ ] Anti-slop: encoding matches printed values; parts-of-whole sum; tick labels are real categories (not 1,2,3… indices) — verified against source data via `scripts/validate_data.py`
```

---

## 3. svg-figure-maker

**file:** `skills/svg-figure-maker/SKILL.md`

### 3a. Cross-link

- **anchor (quoted existing line, `<cross_references>` → "Uses (Input From)" table):**
> `| `shared/references/pre_submission_checklist.md` | 15-point operational gate cross-checked at Stage 5 |`

- **insertion_text** (new table row immediately after):
```
| `shared/references/ai_figure_slop.md` | Anti-slop guardrail. `scripts/check_ai_figure_slop.py` (Stage 3 preflight) checks our own SVG EXACTLY — garbled/lexically-void text, axis ticks as raw indices, default-palette fingerprint, parts-not-summing — against the labels/palette we authored, never via OCR. Categorical tells dominate; chartjunk signals are weak and two-sided |
```

### 3b. Workflow/QA-step edit — Stage 3 (Preflight) and the references table

The natural home is **Stage 3: Preflight (deterministic safety net)** — `check_ai_figure_slop.py` is a sibling to `preflight_check.py` and runs in the same deterministic pass before the vision loop.

- **anchor (quoted existing line, Stage 3 Steps):**
> `1. Run `uv run python scripts/preflight_check.py figure.svg --tokens ../oligon-brand/tokens/brand-tokens.json -o preflight.json``

- **workflow_step_edit** (insert as new step 1b, immediately after that line, renumbering nothing — it slots between steps 1 and 2):
```
1b. Run the anti-slop gate: `uv run python scripts/check_ai_figure_slop.py figure.svg --tokens ../oligon-brand/tokens/brand-tokens.json -o slop.json`. It deterministically flags the categorical AI-generation tells in our OWN output — lexically-void / garbled `<text>` content, axis ticks emitted as raw sequence indices (1,2,3…) instead of real categories, default-library palette fingerprint, and parts-of-whole that don't sum — checking against the labels and palette we authored (no OCR, no forensic CV; those are Track D / inbound-audit only). It emits a VECTOR of flagged sub-scores with severities, never a composite slop score. Any `categorical`-severity finding is a hard `fail` (treat like a preflight `fail` below). Aesthetic/chartjunk findings are advisory and two-sided — do NOT strip decoration or minimize ink to clear them (Bateman). Thresholds are provisional/uncalibrated.
```
- **anchor (Stage 3 Exit Criteria):**
> `- [ ] All `fail` findings cleared`

- **insertion_text** (new checkbox after it):
```
- [ ] `slop.json` has zero `categorical`-severity findings (aesthetic findings may remain — they are advisory, not blocking)
```
Add the script to the `<references>` "Reference Documents" table:
- **anchor:** `| `scripts/preflight_check.py` | Deterministic SVG linter → JSON findings |`
- **insertion_text** (new row after):
```
| `scripts/check_ai_figure_slop.py` | Deterministic anti-slop gate → JSON vector of flagged sub-scores (categorical tells dominant; thresholds provisional). Exact checks against authored labels/palette — no OCR |
```
And add it to the anti-patterns: pitfall §1 ("Skipping the preflight before the vision loop") should mention it:
- **anchor:** `ALWAYS run `scripts/preflight_check.py` first. It's deterministic, fast, and catches everything mechanical. Reserve the vision loop for things only a viewer can judge: clipping, alignment, hierarchy, composition.`
- **insertion_text** (append to that paragraph):
```
 Run `scripts/check_ai_figure_slop.py` in the same pass — it catches the categorical AI-slop tells (void/garbled text, raw-index ticks, default palette) that the brand linter doesn't.
```

---

## 4. scientific-schematics

**file:** `skills/scientific-schematics/SKILL.md`

### 4a. Cross-link

- **anchor (quoted existing line, `<cross_references>` Related Skills table):**
> `| `shared/references/figure_design_principles.md` | Shared visual-design principles — typography ladder (§2), colorblind palettes (§3), accessibility (§4), grid discipline (§6.1), complexity budgets (§5.4), diagram anti-patterns (§7). Consult before authoring schematics |`

- **insertion_text** (new table row immediately after):
```
| `shared/references/ai_figure_slop.md` | Anti-slop guardrail — most relevant to the Tier-2 AI (Nano Banana Pro) path, which produces the Class-A tells (lexically-void labels like `diƨlocttal`, arrows connecting nothing, impossible anatomy/topology). Categorical tells dominate; verify label lexical-validity and pathway logic before delivery |
```
Also add to `<references>` "Reference Documents" table:
- **anchor:** `| `../shared/references/pre_submission_checklist.md` | 15-point unified quality gate (Q0 = "should this be a table?") |`
- **insertion_text** (new row after):
```
| `../shared/references/ai_figure_slop.md` | AI-figure-slop guardrail (categorical tells dominate; aesthetic signals weak/two-sided; provisional thresholds). Apply at Stage 5 quality verification, especially for Tier-2 AI output |
```

### 4b. Workflow/QA-step edit — Stage 5 (Quality Verification)

Tier-2 AI output is raster (PNG/PDF) and can carry true diffusion-style Class-A tells, so this is the one target where a human-eye / advisory-rubric check (not an exact source check) is appropriate — but it stays advisory and categorical-tell-led. For the SVG (Mermaid Tier-1) path, the deterministic SVG gate applies.

- **anchor (quoted existing line, Stage 5 Steps):**
> `5. Validate file format and resolution`

- **workflow_step_edit** (append step 6):
```
6. **Anti-slop check (post-generation).** For Tier-1 Mermaid SVG: run `../svg-figure-maker/scripts/check_ai_figure_slop.py figure.svg` to flag garbled `<text>`, raw-index node labels, and default palette — exact, against the labels we authored. For Tier-2 AI (Nano Banana Pro) raster output: visually confirm the Class-A categorical tells are ABSENT — every label is a real word/term (no `diƨlocttal`-style glyph-strings), every arrow connects meaningful entities (no arrows to/from nothing), anatomy/topology is valid, and printed numbers/units are plausible. These categorical tells dominate the verdict; the default-palette / decoration signal is weak, two-sided, and must not by itself fail a diagram (Bateman). Emit findings as a vector with severities, never a single slop score. See `../shared/references/ai_figure_slop.md`.
```
- **anchor (Stage 5 Exit Criteria):**
> `- [ ] File format appropriate (PNG for web, PDF for print)`

- **insertion_text** (new checkbox after it):
```
- [ ] Anti-slop: no lexically-void labels, no arrows to/from nothing, no impossible anatomy/topology (`ai_figure_slop.md`); SVG output additionally cleared by `check_ai_figure_slop.py`
```

---

## 5. paperbanana

**file:** `skills/paperbanana/SKILL.md`

This is a pure AI-generation (Imagen) raster pipeline — its post-design check is advisory/categorical (no source SVG to diff), and it already has a Stage-3 "Trusting GenAI Output" discipline to extend.

### 5a. Cross-link

- **anchor (quoted existing line, `<references>` Reference Documents table):**
> `| `../shared/references/pre_submission_checklist.md` | 15-point unified quality gate (Q0 = "should this be a table?") |`

- **insertion_text** (new row immediately after):
```
| `../shared/references/ai_figure_slop.md` | AI-figure-slop guardrail. PaperBanana is a diffusion/Imagen pipeline — the highest-risk source of Class-A categorical tells (garbled labels, impossible anatomy, fabricated symbols). Apply at Stage 3 quality evaluation; categorical tells dominate, aesthetic signals are weak/two-sided |
```
Also mirror in `<cross_references>` Related Skills:
- **anchor:** `| `oligon-brand` | Consult `<design_foundation>` for cognitive-foundation citations (Cleveland, Crameri, Fujii 2026) — complementary to visual-design |`
- **insertion_text** (new row after):
```
| `shared/references/ai_figure_slop.md` | Anti-slop guardrail — read before accepting any generation as final; the diffusion path is exactly where lexically-void labels and impossible geometry appear |
```

### 5b. Workflow/QA-step edit — Stage 3 (Quality Evaluation) + anti-pattern §6

Extend the existing Stage-3 "Communication-context fit check" with a categorical anti-slop check.

- **anchor (quoted existing line, Stage 3 Steps):**
> `2. **Communication-context fit check (Fujii 2026):** confirm the figure's complexity matches the Stage 1 context tag (audience / setting / time). E.g., an `oral / brief / lay` figure with 4 panels and 12 colours fails this check; a single-message annotated figure passes. Cross-reference `../shared/references/communication_context_matrix.md`.`

- **workflow_step_edit** (insert as new step 2b immediately after):
```
2b. **Anti-slop categorical check (Class A).** PaperBanana renders via diffusion (Imagen), so inspect the output for the near-categorical AI-generation tells that diffusion produces: lexically-void / garbled label text (letter-shaped but not real words — e.g. `diƨlocttal`, `2xℇpens`), invented glyphs / mixed scripts, impossible anatomy or topology, and arrows connecting nothing to nothing. A single confirmed instance is near-conclusive (Frontiers/Bik 2024) and should fail the figure regardless of the 4-dim score. This is image-only (no source data to diff), so it is a structured human-eye check against the `ai_figure_slop.md` rubric, scored as a vector of flagged sub-scores with severities — NOT a single slop number. The default-palette / decoration signal is weak, two-sided, and never a standalone fail (Bateman). Thresholds provisional/uncalibrated.
```
- **anchor (Stage 3 Exit Criteria):**
> `- [ ] No critical issues flagged`

- **insertion_text** (new checkbox before/after it):
```
- [ ] Anti-slop: zero lexically-void/garbled labels, zero impossible anatomy/topology, zero arrows-to-nothing (`../shared/references/ai_figure_slop.md`)
```
And tie it into the existing anti-pattern §6:
- **anchor:** `3. **Figure-design canon check:** does the output respect Cleveland-McGill 1984 channel ranking, Crameri 2020 colour, Wagemans 2012 direct-labelling, and (if continuous data is involved) Weissgerber 2015? See `../oligon-brand/SKILL.md` `<design_foundation>`.`
- **insertion_text** (new numbered item 4 after it):
```
4. **Anti-slop categorical check:** scan every label for lexical validity and every connector/structure for physical plausibility — the diffusion-specific Class-A tells (`../shared/references/ai_figure_slop.md`). These dominate; do not let a clean aesthetic pass override a single garbled label.
```

---

## 6. research-posters

**file:** `skills/research-posters/SKILL.md`

Posters compose figures produced by `scientific-schematics`, `plotting-libraries`, and `svg-figure-maker` (each of which now runs its own gate). The poster-level edit is a composition-level reminder, placed in Stage 5 (Quality Validation).

### 6a. Cross-link

- **anchor (quoted existing line, `<cross_references>` Related Skills table):**
> `| `shared/references/figure_design_principles.md` | Shared figure-making principles — typography (§2), multi-panel layout (§6.2), legend placement (§6.3), whitespace and padding (§6.4), anti-patterns (§7). Essential for poster panel composition |`

- **insertion_text** (new table row immediately after):
```
| `shared/references/ai_figure_slop.md` | Anti-slop guardrail. Every composited figure must have passed its own skill's anti-slop gate before placement; at poster scale also confirm no figure carries garbled labels or encoding↔value mismatch. Categorical tells dominate; do not down-style figures to look "leaner" (Bateman) |
```
Also add to `<references>` Reference Documents:
- **anchor:** `| `../shared/references/pre_submission_checklist.md` | 15-point unified quality gate (also applies to posters) |`
- **insertion_text** (new row after):
```
| `../shared/references/ai_figure_slop.md` | AI-figure-slop guardrail for composited figures (categorical tells dominate; aesthetic signals weak/two-sided; provisional thresholds) |
```

### 6b. Workflow/QA-step edit — Stage 5 (Quality Validation), §5.4 Content Checklist

- **anchor (quoted existing line, §5.4 Content Checklist):**
> `- [ ] All figures have captions`

- **insertion_text** (new checkbox immediately after):
```
- [ ] Each composited figure passed its source skill's anti-slop gate (`scientific-schematics` Stage 5 / `plotting-libraries` `validate_data.py` / `svg-figure-maker` `check_ai_figure_slop.py`); no figure shows garbled labels, raw-index ticks, or geometry that contradicts its printed values (`../shared/references/ai_figure_slop.md`)
```
And the **Visual Inspection Checklist → Visual Elements** block:
- **anchor:** `- [ ] Colors render as expected`
- **insertion_text** (new checkbox after):
```
- [ ] No anti-slop tells in any figure (lexically-void labels, encoding≠value, parts not summing) — categorical tells, dominate the review (`../shared/references/ai_figure_slop.md`)
```

---

## 7. scientific-slides

**file:** `skills/scientific-slides/SKILL.md`

Slides use the Nano Banana Pro raster path (Class-A risk) plus embedded data figures from other skills. Stage 4 (Visual Validation) is the QA home.

### 7a. Cross-link

- **anchor (quoted existing line, `<references>` Reference Documents table):**
> `| `../shared/references/pre_submission_checklist.md` | 15-point quality gate; applies to slides exported as PDF for permanent record |`

- **insertion_text** (new row immediately after):
```
| `../shared/references/ai_figure_slop.md` | AI-figure-slop guardrail. The Nano Banana Pro slide-image path is a diffusion source of Class-A tells (garbled text, fabricated symbols); embedded data figures inherit their source skill's gate. Apply at Stage 4 visual validation; categorical tells dominate, aesthetic signals weak/two-sided |
```
Also mirror in `<cross_references>` Related Skills:
- **anchor:** `| `venue-templates` | Consult for conference-specific styles |`
- **insertion_text** (new row after):
```
| `shared/references/ai_figure_slop.md` | Anti-slop guardrail — scan generated slide images for garbled label text and fabricated symbols before assembling the PDF |
```

### 7b. Workflow/QA-step edit — Stage 4 (Visual Validation) checklist table

- **anchor (quoted existing line, the validation checklist table row):**
> `| White space | 40-50% of slide empty |`

- **workflow_step_edit** (append new table row immediately after):
```
| Anti-slop (categorical) | No garbled / lexically-void label text on generated slide images, no fabricated symbols, no impossible geometry; embedded data figures have passed their source-skill gate. Dominates: a single garbled label fails the slide regardless of polish (`../shared/references/ai_figure_slop.md`). Aesthetic/default-palette signals are advisory and two-sided — do NOT minimize visuals to clear them (Bateman) |
```
- **anchor (Stage 4 Exit Criteria):**
> `- [ ] Visual content on every slide`

- **insertion_text** (new checkbox after):
```
- [ ] Anti-slop: no garbled labels / fabricated symbols on any generated slide image (`../shared/references/ai_figure_slop.md`)
```
And add to the top-level `**Completion Checklist:**`:
- **anchor:** `- [ ] Visual content on every slide` *(this exact line appears in the Stage-4 exit criteria; in the success-criteria completion checklist the nearest anchor is)* → use:
> `- [ ] High contrast (≥4.5:1) throughout`
- **insertion_text** (new checkbox after it):
```
- [ ] No AI-slop tells on generated slide images (garbled labels, fabricated symbols) — categorical tells, checked at Stage 4
```

---

## Router wiring — YES, both files need a note (Track D capability)

The seven skills above cover the **generative** tracks (A/B/C, our own output, exact checks). The brief also asks whether "is my figure AI slop / audit this figure" should route to the **Track D** inbound-audit capability. Today nothing in either router file catches "audit this figure" / "is this AI slop" — the closest skill, `research-accuracy-verifier`, is **TEXT/citations only** and its triggers (`audit`, `fact-check`, `hallucinated`) would mis-fire on a figure-audit request without a figure-scoped carve-out. Track D is advisory/triage and never dispositive, so it belongs as a **routed capability**, not a verdict gate. Two minimal edits:

### Router note A — `skills/SKILL_ROUTER.md`

Track D logically extends the **research-accuracy-verifier** audit tree (the existing "AUDIT an existing document" branch), since it is the plugin's audit/verify authority. Add a figure-audit leaf.

- **file:** `skills/SKILL_ROUTER.md`
- **anchor (quoted existing line, the verifier audit tree):**
> `             └─ Internal consistency (refs ↔ inline cites, acronym drift)?
                └─ Stage 7: reconcile_references.py + scan_acronyms.py`

- **insertion_text** (new branch appended inside that tree, before the closing ```` ``` ````):
```
             │
             └─ Auditing a FIGURE/CHART for AI-generation tells ("is this AI slop?", "audit this figure")?
                └─ Track D (inbound figure audit) — ADVISORY/TRIAGE ONLY, never dispositive.
                   Uses the forensic/OCR/rubric stack from `shared/references/ai_figure_slop.md`
                   (categorical tells dominate: lexically-void labels, encoding≠value,
                   parts-not-summing, impossible anatomy). For figures WE generated, prefer the
                   exact source-side gates instead (svg-figure-maker `check_ai_figure_slop.py`,
                   plotting-libraries `validate_data.py`). Emit a vector of flagged sub-scores —
                   never a single slop verdict; adjudication stays human.
```
And add a Research-Task-Routing table row:
- **anchor:** `| "Check this draft for hallucinated references" | research-accuracy-verifier | Same — strong document-audit signals |`
- **insertion_text** (new row after):
```
| "Is this figure AI slop?" / "Audit this figure/chart" | research-accuracy-verifier (Track D, advisory) | Forensic/rubric triage per `ai_figure_slop.md`; vector of sub-scores, human-adjudicated. For our own output use the source-side exact gates instead |
```

### Router note B — `skills/skill-router/skill_triggers.yaml`

Add figure-audit phrasings to `research-accuracy-verifier` so "is my figure AI slop / audit this figure" deterministically routes there (Track D), and add `negative_keywords` to the figure-*creation* skills so those same phrases don't pull a generator. Bump the registry version (`# Version: 1.7.0` → `1.8.0`).

- **anchor (quoted existing line, `research-accuracy-verifier` keywords, the prose-audit block tail):**
> `      - run prose-quality audit`

- **insertion_text** (new keywords appended to that list):
```
      # Track D — inbound AI-figure-slop audit (advisory/triage)
      - is this figure ai slop
      - is this chart ai slop
      - audit this figure
      - audit this chart
      - ai-generated figure
      - ai generated chart
      - figure integrity check
      - chart slop
      - is this figure real
```
- **anchor (`research-accuracy-verifier` triggers, prose-audit tail):**
> `      - "(?:check|audit).*against.*prose\\s*standards"`

- **insertion_text** (new triggers appended):
```
      # Track D — inbound AI-figure-slop audit
      - "(?:is|audit).*(?:this|the|my).*(?:figure|chart|plot|diagram).*(?:ai|slop|generated|real|fake)"
      - "(?:figure|chart)\\s+integrity\\s+(?:check|audit)"
      - "chart\\s+slop"
      - "(?:ai|machine)[-\\s]?generated.*(?:figure|chart|plot|diagram)"
```
- **anchor (`research-accuracy-verifier` negative_keywords, near the bottom):**
> `      - single claim`
- **insertion_text** (append — exclude *creation* phrasings so the verifier doesn't grab figure-making requests):
```
      - create figure          # figure creation → plotting-libraries / scientific-schematics / svg-figure-maker, not audit
      - make a chart
      - design a figure
      - generate a figure
```
Add a matching negative_keyword to each **figure-creation** trigger block so "audit this figure / is this AI slop" doesn't mis-route to a generator. For `plotting-libraries`, `scientific-schematics`, `svg-figure-maker`, `paperbanana`, `generate-image`:
- **anchor (example, `plotting-libraries` negative_keywords last line):**
> `      - figure from method`
- **insertion_text** (append, repeat the analogous append at the end of each of the five blocks' `negative_keywords`):
```
      - audit this figure
      - is this figure ai slop
      - chart slop
      - figure integrity check
```

---

### Notes for the implementer
- **oligon-brand is vendored** (`SKILL.md` lines 10–12 say "do not edit here"): its anti-slop wiring is implemented in `figure_design_principles.md` (§1a) and `pre_submission_checklist.md` (§1b), which oligon-brand already maps onto. To make it appear in the SKILL.md body, change `oligon-brand-core` upstream and re-run `scripts/sync_brand_core.sh` — out of scope for this wiring task.
- The §1b tooling-table edit **also fixes the brief's noted bug**: `pre_submission_checklist.md` rows #13/#14 currently point at `validate_figure.py`, but `check_continuous_as_bars`/`check_riskratio_as_bars` live in `validate_data.py`. The replacement rows correct this and add the two new anti-slop checks beside them.
- Every insertion honors both guardrails: **(1)** all gates emit a *vector of flagged sub-scores with severities* (stated in each insertion), thresholds labeled *provisional/uncalibrated*; **(2)** *categorical* tells dominate and aesthetic/chartjunk signals are weak, two-sided, down-weighted, with an explicit "do not minimize ink / do not strip decoration (Bateman)" warning in each workflow edit.
- Track D (forensic/OCR/rubric) appears **only** in the router notes and the `ai_figure_slop.md` reference itself — never as a step inside a generator's own QA workflow, where exact source-side checks replace it.