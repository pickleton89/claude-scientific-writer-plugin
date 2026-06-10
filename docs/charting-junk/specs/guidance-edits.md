I now have all source material grounded. Here is the structured list of ready-to-apply edits.

---

# EDIT SET — AI-figure-slop guardrail (Tracks A2 + A3)

Three files, six edits. All thresholds documented as provisional/uncalibrated. Categorical tells dominate; aesthetic signals are weak, down-weighted, two-sided. No "strip decoration / minimize ink" instructions.

---

## FILE 1 — `skills/oligon-brand/SKILL.md`

### Edit 1a — extend the `<figure_integrity>` "Eight Rules"

**Anchor** (replace the block's heading line and append after the existing rule 8). The current heading reads:

```
## Figure Integrity — Eight Rules
```

and the block currently ends with:

```
8. **No dual y-axes without justification.** Prefer small multiples
   or twin-panel layouts first.
</figure_integrity>
```

**Change 1 — retitle the heading.** Replace:

```
## Figure Integrity — Eight Rules
```

with:

```
## Figure Integrity — Twelve Rules
```

**Change 2 — insert four new rules.** Replace:

```
8. **No dual y-axes without justification.** Prefer small multiples
   or twin-panel layouts first.
</figure_integrity>
```

with the literal text:

```
8. **No dual y-axes without justification.** Prefer small multiples
   or twin-panel layouts first.

These four govern *generative-artifact integrity* — the failure modes a
diffusion model or code-gen LLM introduces that a competent human would
not. Because we author from ground-truth data and source SVG/plot code,
these are **exact deterministic checks against what we already hold**, not
image forensics. A single confirmed violation of Rule 9, 11, or 12 is a
*categorical tell* — it dominates the verdict regardless of how clean the
rest of the figure is.

9. **Lexically-valid labels only.** Every axis label, legend entry, tick
   label, and callout is a real word, term, or number — never a
   letter-shaped but lexically-void glyph-string ("*diƨlocttal*",
   "*testtomcels*"), invented diacritic, or melted/mixed-script character.
   This is the strongest single AI tell (Frontiers/Bik 2024). For our own
   output, scan the source string set, not the pixels.
10. **Non-default styling is intentional, not stripped.** Tool defaults
    (matplotlib `C0`/`C1` tab10, seaborn theme, Excel chart style) are a
    regression-to-mean slop fingerprint — apply a brand cycle or a
    justified palette instead. But this rule is **two-sided**: do *not*
    over-minimize toward a sterile, decoration-free chart either.
    Embellishment that aids recall is not slop (Bateman CHI 2010). Keep
    ink that supports the takeaway; replace defaults, don't strip
    meaning.
11. **Encoding-value fidelity.** Bar heights, slice angles, point
    positions, and marker sizes must match the printed/underlying values.
    Geometry that contradicts the data label is a fabrication tell. We
    hold the data, so verify exactly — `encoded_value == source_value`,
    not OCR.
12. **Closure / conservation holds.** Parts-of-whole sum to the whole
    (pie/stacked slices → 100% or the stated total); subgroup counts
    reconcile to the group total; axis labels are the real categories,
    not raw sequence indices (1, 2, 3…). Check the source data array,
    not the render.
</figure_integrity>
```

---

### Edit 1b — add ONE two-sided pitfall to `<design_foundation>` "Universal design pitfalls"

**Anchor** — the list currently reads:

```
### Universal design pitfalls

1. **Default Syndrome** — tool defaults without justification
2. **Rainbow colormap for sequential data** — use viridis family
3. **Color-only encoding** — add shape / line style / direct label
4. **Cramming** — one main message per figure
5. **Inconsistent styling** — define the hierarchy before starting
6. **Truncated axes** — start bar charts at zero
7. **3D for 2D data** — distorts perception
```

**Change** — replace item 1 with a two-sided entry (keeps numbering 1–7 intact). Replace:

```
1. **Default Syndrome** — tool defaults without justification
```

with:

```
1. **Default Syndrome / regression-to-mean (two-sided)** — tool defaults
   without justification are a slop fingerprint (avoid the canonical
   matplotlib/seaborn/Excel look); but the opposite failure is just as
   real — sterile over-minimization that strips useful labels and
   embellishment is *also* regression-to-the-mean (Bateman CHI 2010: junk
   doesn't impair comprehension and aids recall). Replace defaults with an
   intentional, takeaway-supporting style — not with the leanest possible
   chart.
```

---

## FILE 2 — `skills/shared/references/figure_design_principles.md`

### Edit 2 — new section `§12. AI figure slop & regression-to-mean`

**Section number:** **§12**. It slots **after §11 (References)** is wrong placement — instead insert it **after §9 (Pre-submission validation)** and **before §10 (Out-of-scope)**, so it sits with the operational/principles material rather than after the reference list. Renumber the trailing two sections: current **§10 Out-of-scope** → **§13**, current **§11 References** → **§14**. (If you prefer not to renumber, the lower-cost alternative is to append it as **§12** after §11; recommended placement below keeps topical order, so renumber.)

**Anchor** — §9 currently ends with:

```
Returns JSON findings keyed to this document's section numbers.

---

## §10. Out-of-scope for this doc
```

**Change** — insert the new section between the `---` and `## §10`. Replace:

```
Returns JSON findings keyed to this document's section numbers.

---

## §10. Out-of-scope for this doc
```

with:

```
Returns JSON findings keyed to this document's section numbers.

---

## §12. AI figure slop & regression-to-mean

> **Canonical reference:** `skills/shared/references/ai_figure_slop.md` —
> the three-track model (A2 author-time exact checks / Track B linter
> functions / Track D inbound advisory triage), the six-dimension v0.1
> rubric, and the categorical-vs-graded severity logic. **Read that file
> before relying on any threshold here; all thresholds are provisional and
> uncalibrated.**

Two load-bearing rules govern everything in that file and must be honored
by any skill that consumes it:

1. **Emit a *vector* of flagged sub-scores with severities — never a single
   composite "slop score."** Provenance ≠ quality: a figure can be
   AI-generated and excellent, or human-made and slop (Kommers 2026).
2. **Categorical tells dominate; aesthetic signals are weak, down-weighted,
   and two-sided.** A lexically-void label or an encoding-vs-value mismatch
   is near-decisive on its own; decoration/data-ink signals never trigger
   a verdict alone and must not be read as "strip the decoration"
   (Bateman 2010).

Because this plugin *generates* figures, we hold the ground-truth data and
source SVG/plot code, so the unreliable image→data recovery step (OCR /
forensic CV — shown to fail zero-shot in SciFigDetect) is **unnecessary for
our own output**. Replace it with cheap *exact* checks against the data and
source. Only inbound third-party figures (Track D) need the forensic/rubric
stack, and there it stays advisory, never dispositive.

**One-line take-aways (mirroring the §1 cognitive-foundation table):**

| Signal | Class | One-line apply rule |
|---|---|---|
| Lexically-void / garbled labels | categorical ⚑ | Real words/terms/numbers only — scan the source string set, not pixels (Frontiers/Bik 2024) |
| Encoding–value mismatch | categorical ⚑ | `encoded == source` for every bar/slice/point — verify against held data, not OCR (Woo 2025) |
| Closure / conservation failure | categorical ⚑ | Parts sum to whole; subgroups reconcile to totals — check the data array |
| Axis labels = raw indices | categorical ⚑ | Tick labels are real categories, never 1,2,3… sequence indices |
| Default-distribution styling | graded, weak | Replace tool defaults (tab10/seaborn/Excel) with an intentional palette — *don't* over-minimize (two-sided) |
| Gratuitous decoration / data-ink | graded, weak, two-sided | Keep ink that supports the takeaway; embellishment aids recall (Bateman 2010) — never an AI verdict alone |

**Track B enforcement.** The exact author-time checks are deterministic
functions in `plotting-libraries/scripts/validate_data.py`
(`check_continuous_as_bars`, `check_riskratio_as_bars`, and the slop
checks added there) plus the SVG-string scan in
`svg-figure-maker/scripts/preflight_check.py`. See
`pre_submission_checklist.md` "Generative-artifact integrity" items for the
operational gate.

---

## §13. Out-of-scope for this doc
```

**Then** — rename the final section. The file currently ends its References heading as:

```
## §11. References
```

Replace with:

```
## §14. References
```

---

## FILE 3 — `skills/shared/references/pre_submission_checklist.md`

### Edit 3a — add a new "Generative-artifact integrity" subsection (5 items)

**Recommendation & justification:** create a **new subsection**, not an extension of "Scientific Rigor." Rationale: items #12–14 under "Scientific Rigor" are all *encoding-choice* guidance (which chart type best represents the data) sourced from perception research. The new items detect a *different failure class* — generative artifacts (garbled glyphs, default fingerprint, geometry≠data, broken closure) that have nothing to do with chart-type choice and whose enforcement is exact data/source comparison, not perceptual judgment. A distinct subsection keeps the severity model legible (these carry categorical-tell weight) and mirrors how `figure_design_principles.md` isolates §12.

**Anchor** — "Scientific Rigor" ends and "Visual Quality" begins:

```
**Verify:** matplotlib `ax.errorbar(x, y, yerr=...)` or ggplot2 `geom_pointrange(aes(ymin=lower, ymax=upper))`.

---

## Visual Quality
```

**Change** — insert the new subsection between them. Replace the snippet above with:

```
**Verify:** matplotlib `ax.errorbar(x, y, yerr=...)` or ggplot2 `geom_pointrange(aes(ymin=lower, ymax=upper))`.

---

## Generative-artifact Integrity

> Detects AI-slop tells (garbled labels, default fingerprint, geometry≠data,
> broken closure). Because we author from ground-truth data and source code,
> these are **exact deterministic checks against what we already hold** — not
> OCR or image forensics. A single confirmed failure of #16, #18, or #19 is a
> *categorical tell* and dominates the verdict. Thresholds here are
> provisional/uncalibrated; see `figure_design_principles.md` §12 and
> `ai_figure_slop.md`.

### 16. No garbled / lexically-void labels

**Check:** Every axis label, legend entry, tick label, and callout is a real word, term, or number — no letter-shaped but meaningless glyph-strings ("*diƨlocttal*"), invented diacritics, or mixed-script characters.
**Why:** Lexically-void figure text is the strongest single AI-generation tell (Frontiers/Bik 2024 retraction). For self-authored figures, scan the source string set, not the rendered pixels.
**Verify:** `svg-figure-maker/scripts/preflight_check.py` (label-string lexical scan over `<text>`/`<tspan>`); for plot code, inspect the label/tick-label arrays directly.

### 17. Non-default palette confirmed

**Check:** Figure does not use the unmodified tool default (matplotlib `C0`/`C1` tab10, seaborn default theme, Excel chart styling); a brand cycle or justified palette is applied. **Two-sided:** confirm styling is *intentional*, not stripped to a sterile, decoration-free minimum.
**Why:** Default-distribution styling is a regression-to-mean slop fingerprint (Kommers 2026); but over-minimization is *also* a failure — embellishment aids recall and does not impair comprehension (Bateman CHI 2010). This is a weak, graded signal, never an AI verdict on its own.
**Verify:** `oligon-brand/SKILL.md` preflight `validate_palette()` / `get_brand_compliance_report()`; for SVG, `preflight_check.py` off-palette-hex check.

### 18. Encoding–value fidelity

**Check:** Bar heights, slice angles, point positions, and marker sizes match the underlying/printed values exactly.
**Why:** Geometry that contradicts the data is a fabrication tell — the covert Class B failure where a chart "looks right but encodes wrong data" (Woo 2025). We hold the source data, so verify `encoded == source` exactly rather than recovering values via OCR.
**Verify:** Compare the plotted array against the source data array in the generating code; for ratio/continuous-encoding pitfalls see `plotting-libraries/scripts/validate_data.py::check_continuous_as_bars` and `::check_riskratio_as_bars`.

### 19. Closure / conservation sums

**Check:** Parts-of-whole reconcile (pie/stacked slices sum to 100% or the stated total); subgroup counts sum to the group total; stacked-bar segments sum to the bar height.
**Why:** Slices that don't sum to 100% and totals that don't reconcile are a deterministic generative-artifact signature (practitioner Class B catalog). Internal-consistency arithmetic is exact and provenance-agnostic.
**Verify:** Sum the source data array(s) and assert closure in the generating code (e.g., `assert abs(sum(parts) - whole) < tol`).

### 20. Axis labels are real categories, not raw indices

**Check:** Categorical tick labels are the actual category names, not raw sequence indices (1, 2, 3…) standing in for unmapped categories.
**Why:** Index-as-label is a code-gen "data-mapping" tell (RealChart2Code 2026) and reads as an unfinished/hallucinated axis. Scale type must also fit the data (no silent log).
**Verify:** Inspect the tick-label array against the category source; `svg-figure-maker/scripts/preflight_check.py` flags numeric-only categorical tick runs.

---

## Visual Quality
```

> Note: this renumbers the existing **#15 Iconography licensing** so it stays last after the inserted #16–20 — recommend bumping it to **#21** for a clean 21-item gate. If preferred, leave #15 in place and number the new items #16–20 *before* it (the anchor above places them before Visual Quality, which already achieves this — #15 remains #15 under Visual Quality). Either is consistent; the anchor as written keeps #15 numerically after the new items, so update the title line "15-point unified quality gate" → "20-point unified quality gate" at the top of the file accordingly (current header line: `> 15-point unified quality gate for figures, graphical abstracts, posters, slides, and schematics before submission.`).

---

### Edit 3b — FIX the broken `validate_figure.py` → `validate_data.py` pointer

Confirmed on disk: `validate_figure.py` contains only `validate_figure`, `_validate_pdf`, `_validate_raster`, `validate_figure_for_journal` (file-level production checks). `check_continuous_as_bars` (line 476) and `check_riskratio_as_bars` (line 548) live in **`validate_data.py`**. Two locations cite the wrong file.

**Fix 1 — checklist item #13.** Current line:

```
**Verify:** See `plotting-libraries/scripts/validate_figure.py::check_continuous_as_bars` and `plotting-libraries/references/plot_selection_guide.md` for code recipes.
```

Replace with:

```
**Verify:** See `plotting-libraries/scripts/validate_data.py::check_continuous_as_bars` and `plotting-libraries/references/plot_selection_guide.md` for code recipes.
```

**Fix 2 — tooling cross-reference table, two rows.** Current lines:

```
| #13 Continuous-as-bars | `plotting-libraries/scripts/validate_figure.py::check_continuous_as_bars` |
| #14 Risk-ratio-as-bars | `plotting-libraries/scripts/validate_figure.py::check_riskratio_as_bars` |
```

Replace with:

```
| #13 Continuous-as-bars | `plotting-libraries/scripts/validate_data.py::check_continuous_as_bars` |
| #14 Risk-ratio-as-bars | `plotting-libraries/scripts/validate_data.py::check_riskratio_as_bars` |
```

(Item #14's own `**Verify:**` line cites matplotlib/ggplot2 calls, not a file path, so it needs no change.)

---

## Summary of edits

| # | File | Anchor | Action |
|---|---|---|---|
| 1a | `oligon-brand/SKILL.md` | `## Figure Integrity — Eight Rules` + rule 8 / `</figure_integrity>` | Retitle → "Twelve Rules"; append Rules 9–12 (lexical labels, two-sided non-default styling, encoding-value fidelity, closure/conservation) |
| 1b | `oligon-brand/SKILL.md` | "Universal design pitfalls" item 1 | Replace item 1 with two-sided Default-Syndrome/regression-to-mean entry |
| 2 | `figure_design_principles.md` | end of §9 / before §10 | Insert new **§12** (cross-link + 6-row take-away table); renumber old §10→§13, §11→§14 |
| 3a | `pre_submission_checklist.md` | end of Scientific Rigor / before Visual Quality | Insert new **"Generative-artifact Integrity"** subsection, items #16–20; bump header count line |
| 3b | `pre_submission_checklist.md` | item #13 `**Verify:**` line + tooling table rows #13/#14 | `validate_figure.py` → `validate_data.py` (3 line replacements) |

**Cross-file dependency:** Edits 2 and 3a both reference a not-yet-created `skills/shared/references/ai_figure_slop.md` (the canonical Track A2/B/D doc) — that file is the companion deliverable; these guidance edits are the cross-links into it. Edits 1a/1b/3b are self-contained and can land independently.