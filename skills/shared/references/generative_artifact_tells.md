# Generative-Artifact Tell Pass (Shared)

> Canonical, skill-agnostic rubric for the **Generative-Artifact Tell Pass** — the categorical AI-tell checklist run at the head of every vision-QA loop on figures this plugin generates.
> Version: 1.0.0
> Status: canonical
> Used by: svg-figure-maker, paperbanana, scientific-schematics, scientific-slides
>
> **This is the single shared home (C5).** Both svg-figure-maker (Stage 5 visual critique) and paperbanana (post-generation review) point here; do not fork a skill-local copy. Per-skill applicability notes (svg vector vs. paperbanana diffusion raster) are marked inline.
>
> **Cross-link:** the governing doctrine — provenance ≠ quality, the categorical-vs-graded tell catalog, and the regression-to-mean / Bateman caveat — lives in `ai_figure_slop.md` (§3 tell catalog, §4 regression-to-mean) in this same directory. This file is the *operational* rubric that doctrine forward-points to (Track C).

---

## Governing insight (read first)

This plugin **generates** the figures it judges, so we hold the ground-truth data and the source SVG / plot code / prose caption. The reports' unreliable step — recovering data from pixels via OCR or forensic CV — is **unnecessary on our own output** and is explicitly out of scope here (it belongs to Track D, inbound third-party audit, which stays advisory/triage and never dispositive).

The Tell Pass therefore covers **only what a deterministic linter cannot see**: garbled vector/raster text, melted glyphs, distorted/impossible geometry, encoding-vs-printed-value mismatch, and default-template feel. Everything mechanizable (palette fingerprints, raw-index axis detection on the data side, closure on known totals) is handled upstream by the preflight/validate linters; do not re-check those here.

### Two guardrails honored on the face of this rubric

1. **Emit a vector of flagged sub-scores with severities — never a composite "slop score."** All thresholds below are **PROVISIONAL / UNCALIBRATED** (v0.1).
2. **Categorical tells dominate; aesthetic / chartjunk signals are weak, down-weighted, and two-sided.** Never instruct the model to strip decoration or minimize ink — over-minimization is itself regression-to-mean slop (Bateman CHI 2010).

---

## §1. The shared rubric — "Generative-Artifact Tell Pass" (v0.1, PROVISIONAL / UNCALIBRATED)

Six items. Items marked **⚑ CATEGORICAL** auto-fail → regenerate when scored 2, regardless of everything else. Items **T1–T4 are checked first and in order** (they dominate); **T5–T6 are weak, down-weighted, two-sided** corroboration only. Every item requires a one-line written justification quoting what was seen (or "not observed").

| # | Tell (check in this order) | What to look for | 0 / 1 / 2 anchors | Categorical? |
|---|---|---|---|---|
| **T1** | **Lexical validity of rendered text** | Read every axis label, legend entry, callout, title *as it appears in the raster*. Are they real words / terms? | 0 = all lexically valid; 1 = ≥1 misspelling consistent with an ordinary typo (`recieve`); 2 = lexically-void glyph-strings (`diƨlocttal`, `testtomcels`), invented diacritics, or mixed scripts | **⚑ YES** (Frontiers rat; report-2 §6 D1.1) |
| **T2** | **Glyph / character integrity** | Are letterforms intact, or melted, fused, duplicated, half-formed, morphing across a word? | 0 = clean; 1 = one isolated odd glyph; 2 = systematic malformed / melted characters | **⚑ YES** (report-2 D1.2) |
| **T3** | **Encoding ↔ printed-value fidelity** | Where a value is printed *on* a mark (bar with a number, slice with a %, point with a label), does the geometry match the number? Do parts-of-whole sum to the whole? | 0 = geometry matches every printed value AND parts sum; 1 = rounding-level gap (≤2%); 2 = geometry contradicts a printed label, OR slices / stacks don't sum | **⚑ YES** (report-1 Misviz/encoding; report-2 D2.1 + D2.2) |
| **T4** | **Physical / structural / pathway plausibility** | For any depicted structure (anatomy, molecule, apparatus) or flow (arrows, cascade): correct count / topology? Arrows connect real entities in valid order? | 0 = valid (stylization OK); 1 = oversimplified but not wrong; 2 = impossible anatomy / topology, or arrows to / from nothing | **⚑ YES** (Frontiers rat; report-2 D3.1 + D3.2) |
| **T5** | **Axis / label coherence** | Tick labels are real categories, not raw indices (1, 2, 3…). Legend entries each map to a drawn series and vice-versa. Units present and sane. | 0 = coherent; 1 = suboptimal (e.g., orphaned legend entry, odd unit); 2 = index-as-label or legend references a series not drawn | No (graded) |
| **T6** | **Default-template feel** *(weak, TWO-SIDED, down-weighted)* | Generic model-default palette / font / layout that ignores the brief; OR over-minimized regression-to-mean (decoration stripped to a bland default). | 0 = bespoke to the brief; 1 = mildly generic in either direction; 2 = unmistakable default-distribution look | No (graded — **never dispositive**) |

### Bateman caveat (carried on the face of the rubric — do not delete when inserting)

> T6 is corroborating texture, not evidence. Embellishment alone does **not** impair comprehension and can aid recall (Bateman CHI 2010). **Never strip decoration or minimize ink to lower a T6 score** — over-minimization is itself a regression-to-mean slop failure. A clean T1–T4 with a "busy but intentional" T6 is a **PASS**. (See `ai_figure_slop.md` §4 for the regression-to-mean catalog.)

### Applicability defaults (mark N/A and skip — do not score 0)

- **svg-figure-maker** (vector): **T2** rarely applies (vector text doesn't melt) — score **N/A** unless a `<path>`-outlined or `textPath` label looks malformed. **T3** applies only if the figure prints numeric values; its reconciliation source is the SVG's own `<text>` data values vs. the drawn geometry — you authored both, so a mismatch is a transcription bug, fixed at source.
- **paperbanana** (diffusion raster): **all six apply**; **T1 / T2 / T4** are the high-yield items for diffusion raster (Imagen output is the primary risk surface for garbled text, melted glyphs, and impossible anatomy).
- **scientific-schematics / scientific-slides**: apply T1, T3, T4, T5 to any AI-generated or rendered figure surface; T2 as for the underlying renderer (vector → N/A by default), T6 two-sided as everywhere.

---

## §2. Verdict / loop rule (vector of sub-scores — NEVER a composite)

Emit a **vector**, not a number:

```
tell_pass: {
  T1: {score: 0|1|2|N/A, categorical: true,  justification: "<quote what you saw>"},
  T2: {score: ...,        categorical: true,  justification: "..."},
  T3: {score: ...,        categorical: true,  justification: "..."},
  T4: {score: ...,        categorical: true,  justification: "..."},
  T5: {score: ...,        categorical: false, justification: "..."},
  T6: {score: ...,        categorical: false, justification: "..."},
  verdict: "regenerate" | "accept_with_notes" | "clean_no_positive_evidence"
}
```

**Loop rule:**

1. **Any ⚑ categorical item (T1–T4) = 2 → `verdict: regenerate`.** This dominates the whole figure regardless of all other scores and regardless of the existing aesthetic critique. Do not patch around it; regenerate (svg: re-author the offending text / geometry from the known-correct source values; paperbanana: refine via the Critic loop or tighten the caption). One ⚑ = 2 is near-conclusive evidence of uncorrected generative authorship.
2. **Any categorical item = 1, or any graded item (T5 / T6) = 2 → `verdict: accept_with_notes`,** record under the `warn`-equivalent and address if cheap, but do not block.
3. **All categorical = 0 and graded ≤ 1 → `verdict: clean_no_positive_evidence`.**
4. This pass shares the host loop's existing **5-iteration hard cap.** A ⚑ = 2 that recurs after 2 regenerations of the same element → stop, surface `status: needs_user_input` (the source data or prompt is the problem, not the render).

**Ordering enforced:** check T1 → T2 → T3 → T4 first; if any hits 2, you may short-circuit to `regenerate` without scoring T5 / T6 (record them as `not_assessed`). This keeps the loop cheap.

---

## §3. Mandatory warning text (insert verbatim wherever this rubric is consumed)

> **A clean Tell Pass is NO POSITIVE EVIDENCE, not proof.** Generative tells are decaying (2026-generation models pass the obvious ones); absence of a tell is weak evidence of absence. A `clean_no_positive_evidence` verdict means only "no tell observed on this pass" — it never certifies human authorship or data correctness. **T3** (encoding fidelity) in particular catches only what is *printed on the figure*; it does not verify that the underlying numbers are real — that is the data layer's job (svg: the source values; paperbanana: the source text), not this vision pass. **All thresholds here are provisional and uncalibrated.**

---

## §6. Worked examples — calibration table

These are the anchors a second reviewer should reproduce; they double as the false-positive guards. (Section number aligns with the source spec; §4/§5 are the per-skill insertion mechanics, which live in each skill's SKILL.md, not in this shared doc.)

| Case | Figure | Expected vector | Expected verdict |
|---|---|---|---|
| **Frontiers rat** (paperbanana) | label reads `diƨlocttal stem ells`; arrows to nothing; impossible anatomy | T1 = 2, T2 = 2, T4 = 2 | `regenerate` (T1 alone suffices) |
| **Bar value mismatch** (svg) | bar labeled "42" but drawn to the 30-gridline | T3 = 2 | `regenerate` |
| **Pie not summing** (svg / paperbanana) | slices labeled 40 / 35 / 30 (= 105%) | T3 = 2 | `regenerate` |
| **Raw-index axis** (svg) | x-ticks render `1, 2, 3, 4` instead of the category names | T3 = 0, T5 = 2 | `accept_with_notes` (graded, not categorical) |
| **Busy-but-correct Holmes infographic** (paperbanana) | heavy embellishment, all text valid, geometry matches | T1–T4 = 0, T6 = 1 | `clean_no_positive_evidence` — **must NOT regenerate**; do not strip decoration |
| **Over-minimized regression-to-mean** (svg) | decoration removed to a bland matplotlib-default look | T1–T4 = 0, T6 = 2 | `accept_with_notes`; do not "fix" by removing more |
| **One typo** (svg) | legend reads `Treatement` | T1 = 1 | `accept_with_notes` (1, not categorical 2) |
| **Clean bespoke figure** (svg) | valid text, matched geometry, brand palette | all 0, T6 = 0 | `clean_no_positive_evidence` |

**The last four rows are the false-positive guards:** a single ordinary typo (T1 = 1) and a clean figure must **not** trigger regenerate; a "busy" figure must **never** be down-scored on T6 alone; and an over-minimized figure must **never** be "fixed" by removing more decoration.

---

## References

- `ai_figure_slop.md` (this directory) — governing doctrine: §3 categorical-vs-graded tell catalog, §4 regression-to-mean catalog + two-sided Bateman caveat, §1 provenance ≠ quality.
- `figure_design_principles.md` (this directory) — shared figure-making principles; §10 "AI figure slop & regression-to-mean."
- `pre_submission_checklist.md` (this directory) — unified pre-submission gate; "Generative-artifact Integrity" subsection.
- Bateman, S. et al. (2010). *Useful Junk? The Effects of Visual Embellishment on Comprehension and Memorability of Charts.* CHI 2010. — basis for the two-sided T6 caveat (embellishment is not inherently slop; over-minimization is its own failure mode).
- Tracks B (deterministic linters: `svg-figure-maker/scripts/preflight_check.py`, `plotting-libraries/scripts/validate_data.py`) and D (inbound advisory audit — the `FIGURE_INTEGRITY` parallel family in `research-accuracy-verifier/`) — the mechanizable and forensic complements to this vision-loop pass.
