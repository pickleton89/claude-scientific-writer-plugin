I now have everything I need. I have the exact insertion anchors, the existing schemas, the existing checklist categories, the oligon-brand Eight Rules, and both source reports. Let me compose the deliverable.

I'm not using TaskCreate — this is a single-shot design deliverable, not a multi-step execution task.

Here is the complete Track C deliverable.

---

# Track C — Per-Tell Slop Checklist for the Vision-QA Loops

## Design summary (read first)

Both vision loops already `Read` a rasterized PNG and judge it (svg-figure-maker Stage 5; paperbanana Stages 2c/3 + anti-pattern #6). I bolt a **Generative-Artifact Tell Pass** onto each — a short, ordered, per-item checklist that runs *inside* the existing vision step, before the existing aesthetic critique. It covers only what a linter cannot: garbled vector text, melted glyphs, distorted/impossible geometry, encoding-vs-printed-value mismatch, default-template feel.

Trimming rationale (what I cut from the reports' stacks and why):

- **Dropped Dimension 4 (render/signal artifacts), Dimension 5.2/5.3 (EXIF, panel-dup), and 4.3 (frequency-domain).** These are Class-C photographic / forensic-CV concerns. svg-figure-maker emits vector; paperbanana emits an Imagen raster but we hold the source prose and caption. The governing insight applies: forensic CV is the unreliable step and is unnecessary on our own output. These belong in Track D (inbound audit), not here.
- **Dropped report-1's Tier-2 CV and Tier-3 image→data OCR recovery.** We never recover data from pixels — for svg-figure-maker the data is in the SVG text nodes; for paperbanana the ground truth is the source text.
- **Kept and front-loaded the categorical tells** (lexically-void labels, melted glyphs, encoding≠printed value, parts-not-summing, impossible geometry) because per both reports these *dominate* and remain decisive even as soft tells decay.
- **Kept exactly one down-weighted, two-sided aesthetic item** (default-template feel), explicitly flagged non-categorical and non-dispositive, with the Bateman caveat inline so the model never strips decoration to chase the score.

The two loops share **one rubric** (below) but differ in two items' applicability: svg-figure-maker, being vector, can rarely produce melted glyphs but *can* produce raw-index labels and encoding mismatches if it transcribed data wrong; paperbanana (diffusion raster) is the primary risk surface for garbled text / melted glyphs / impossible anatomy. Per-item N/A handles this.

---

## 1. The shared rubric — "Generative-Artifact Tell Pass" (v0.1, provisional/uncalibrated)

Six items. Items marked **⚑ CATEGORICAL** auto-fail → regenerate when scored 2, regardless of everything else. Items T1–T4 are checked **first and in order** (they dominate); T5–T6 are weak, down-weighted, two-sided corroboration only. Every item requires a one-line written justification quoting what was seen (or "not observed").

| # | Tell (check in this order) | What to look for | 0 / 1 / 2 anchors | Categorical? |
|---|---|---|---|---|
| **T1** | **Lexical validity of rendered text** | Read every axis label, legend entry, callout, title *as it appears in the raster*. Are they real words/terms? | 0 = all lexically valid; 1 = ≥1 misspelling consistent with an ordinary typo (`recieve`); 2 = lexically-void glyph-strings (`diƨlocttal`, `testtomcels`), invented diacritics, or mixed scripts | **⚑ YES** (Frontiers rat; report-2 §6 D1.1) |
| **T2** | **Glyph / character integrity** | Are letterforms intact, or melted, fused, duplicated, half-formed, morphing across a word? | 0 = clean; 1 = one isolated odd glyph; 2 = systematic malformed/melted characters | **⚑ YES** (report-2 D1.2) |
| **T3** | **Encoding ↔ printed-value fidelity** | Where a value is printed *on* a mark (bar with a number, slice with a %, point with a label), does the geometry match the number? Do parts-of-whole sum to the whole? | 0 = geometry matches every printed value AND parts sum; 1 = rounding-level gap (≤2%); 2 = geometry contradicts a printed label, OR slices/stacks don't sum | **⚑ YES** (report-1 Misviz/encoding; report-2 D2.1 + D2.2) |
| **T4** | **Physical / structural / pathway plausibility** | For any depicted structure (anatomy, molecule, apparatus) or flow (arrows, cascade): correct count/topology? Arrows connect real entities in valid order? | 0 = valid (stylization OK); 1 = oversimplified but not wrong; 2 = impossible anatomy/topology, or arrows to/from nothing | **⚑ YES** (Frontiers rat; report-2 D3.1 + D3.2) |
| **T5** | **Axis / label coherence** | Tick labels are real categories, not raw indices (1,2,3…). Legend entries each map to a drawn series and vice-versa. Units present and sane. | 0 = coherent; 1 = suboptimal (e.g., orphaned legend entry, odd unit); 2 = index-as-label or legend references a series not drawn | No (graded) |
| **T6** | **Default-template feel** *(weak, TWO-SIDED, down-weighted)* | Generic model-default palette/font/layout that ignores the brief; OR over-minimized regression-to-mean (decoration stripped to a bland default). | 0 = bespoke to the brief; 1 = mildly generic in either direction; 2 = unmistakable default-distribution look | No (graded — **never dispositive**) |

**Bateman caveat carried on the face of the rubric (do not delete when inserting):**
> T6 is corroborating texture, not evidence. Embellishment alone does **not** impair comprehension and can aid recall (Bateman CHI2010). **Never strip decoration or minimize ink to lower a T6 score** — over-minimization is itself a regression-to-mean slop failure. A clean T1–T4 with a "busy but intentional" T6 is a PASS.

**Applicability defaults (mark N/A and skip, do not score 0):**
- svg-figure-maker: T2 rarely applies (vector text doesn't melt) — score N/A unless a `<path>`-outlined or `textPath` label looks malformed. T3 applies only if the figure prints numeric values.
- paperbanana: all six apply; T1/T2/T4 are the high-yield items for diffusion raster.

---

## 2. Verdict / loop rule (vector of sub-scores, NEVER a composite)

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
1. **Any ⚑ categorical item (T1–T4) = 2 → `verdict: regenerate`.** This dominates the whole figure regardless of all other scores and regardless of the existing aesthetic critique. Do not patch around it; regenerate (svg: re-author the offending text/geometry from the known-correct source values; paperbanana: refine via Critic loop or tighten the caption). One ⚑=2 is near-conclusive evidence of uncorrected generative authorship.
2. **Any categorical item = 1, or any graded item (T5/T6) = 2 → `verdict: accept_with_notes`,** record under `warn`-equivalent and address if cheap, but do not block.
3. **All categorical = 0 and graded ≤ 1 → `verdict: clean_no_positive_evidence`.**
4. This pass shares the existing **5-iteration hard cap.** A ⚑=2 that recurs after 2 regenerations of the same element → stop, surface `status: needs_user_input` (the source data or prompt is the problem, not the render).

**Ordering enforced:** check T1→T2→T3→T4 first; if any hits 2, you may short-circuit to `regenerate` without scoring T5/T6 (record them as `not_assessed`). This keeps the loop cheap.

---

## 3. Mandatory warning text (insert verbatim in both skills)

> **A clean Tell Pass is NO POSITIVE EVIDENCE, not proof.** Generative tells are decaying (2026-generation models pass the obvious ones); absence of a tell is weak evidence of absence. A `clean_no_positive_evidence` verdict means only "no tell observed on this pass" — it never certifies human authorship or data correctness. T3 (encoding fidelity) in particular catches only what is *printed on the figure*; it does not verify the underlying numbers are real — that is the data layer's job (svg: the source values; paperbanana: the source text), not this vision pass. All thresholds here are provisional and uncalibrated.

---

## 4. Exact insertion — svg-figure-maker

### 4a. Insert into `skills/svg-figure-maker/SKILL.md`, Stage 5

**Anchor (quote the surrounding lines you insert near):** in `<workflow>` → `### Stage 5: Visual critique (the killer feature)` → step 2, which currently reads:

```
2. Walk `references/visual_critique_checklist.md` (Phase 3 deliverable) — for v0.1 use the inline checklist below:
   - **Text legibility:** every label readable; nothing clipped, overlapping, or truncated
```

Insert a **new step 2 (Generative-Artifact Tell Pass) ahead of the existing aesthetic walk**, and renumber the current step 2 to step 3. New text to insert immediately after the `**Steps:**` `1. Read the figure.preview.png ...` line and before the existing `2. Walk ...`:

```markdown
2. **Generative-Artifact Tell Pass FIRST** (categorical; dominates the aesthetic walk).
   Before judging craft, run the per-tell checklist in
   `references/generative_artifact_tells.md`. Check T1→T4 (⚑ categorical) **in
   order**; write a one-line justification per item quoting what you saw.
   - T1 Lexical validity · T2 Glyph integrity · T3 Encoding↔printed-value ·
     T4 Physical/pathway plausibility — **any = 2 ⇒ regenerate**, short-circuit,
     skip the aesthetic walk this iteration.
   - T5 Axis/label coherence · T6 Default-template feel (weak, two-sided —
     never strip decoration to lower T6).
   - Emit the `tell_pass` vector into `critique.json` (schema below). A clean
     pass is **no positive evidence**, not proof.
```

Then bump the existing items "2. Walk … / 3. Emit findings … / 4. READ design_practices_index.md §5" to 3/4/5.

**Also update Stage 5 Exit Criteria.** Anchor:

```
**Exit Criteria:**
- [ ] `critique.json` written and schema-valid
- [ ] Number of findings recorded for iteration log
```

Insert a line:

```
- [ ] `tell_pass` vector recorded; no ⚑ categorical tell (T1–T4) scored 2
```

**Add one anti-pattern.** Anchor — the `<anti_patterns>` block currently ends with pitfall #6 ("Duplicating brand styling content in the figure"). Append:

```markdown
### 7. Treating decoration removal as a slop fix

**Anti-pattern:**
Stripping embellishment, flattening to a bare-minimum default, or minimizing
ink to make a figure "look less AI." This chases the wrong signal.

**Solution:**
The decisive AI tells are categorical integrity failures (garbled text, melted
glyphs, encoding≠printed value, impossible geometry — `references/generative_artifact_tells.md`
T1–T4), NOT aesthetic richness. Over-minimization is itself a regression-to-mean
slop failure (Bateman CHI2010). Fix the integrity tell; leave intentional
decoration alone.
```

### 4b. New reference file `skills/svg-figure-maker/references/generative_artifact_tells.md`

Contains §1 rubric table, §2 loop rule, §3 warning text above, verbatim, with these svg-specific notes: T2 default N/A unless `<path>`/`textPath` outlined labels; T3 reconciliation source = the SVG's own `<text>` data values vs. drawn geometry (you authored both, so a mismatch is a transcription bug — fix at source).

### 4c. Register the file. Anchor in `<references>` table:

```
| `references/visual_critique_checklist.md` | Vision-loop critique rubric — 7 categories with `principle_ref` anchors and the schema-compatible finding shape |
```

Insert below it:

```
| `references/generative_artifact_tells.md` | Generative-Artifact Tell Pass (T1–T6) — categorical AI-tell checklist run at the head of Stage 5; vector output, ⚑ auto-fail→regenerate rule |
```

### 4d. Schema extension — `schemas/critique_finding.schema.json`

Two minimal, backward-compatible edits:

1. Add `"generative_tell"` to the `category` enum (currently ends `"accessibility", "other"`):
```json
"text_legibility","hierarchy","alignment","color_rendering",
"line_crispness","composition_balance","accessibility","generative_tell","other"
```
2. Add an optional `tell` discriminator object (not in `required`, so existing findings stay valid):
```json
"tell": {
  "type": "object",
  "properties": {
    "id":          {"type": "string", "enum": ["T1","T2","T3","T4","T5","T6"]},
    "score":       {"type": "integer", "enum": [0,1,2]},
    "categorical": {"type": "boolean"},
    "justification": {"type": "string", "minLength": 1}
  },
  "required": ["id","score","categorical","justification"]
}
```
Because `principle_ref` currently requires a `§n` or `N/A` pattern, generative-tell findings set `principle_ref: "N/A"` (these tells live in the new ref doc, not `figure_design_principles.md`). The wrapper's `summary` object gains an optional `regenerate: <bool>` set true when any ⚑ tell = 2.

### 4e. Cross-link the existing checklist. Anchor in `references/visual_critique_checklist.md`, the section:

```
## What this checklist deliberately does NOT cover

These are caught by `scripts/preflight_check.py` upstream — do not re-check
them visually, do not emit critique findings for them:
```

Insert above it a short pointer:

```markdown
## Run the Generative-Artifact Tell Pass FIRST

Before this aesthetic walk, run `references/generative_artifact_tells.md`
(T1–T6). It catches what BOTH the preflight linter AND this aesthetic checklist
miss: garbled/melted text, encoding≠printed-value, impossible geometry. Any
⚑ categorical tell (T1–T4) at score 2 short-circuits to `regenerate` and you
skip this walk for the current iteration.
```

---

## 5. Exact insertion — paperbanana

paperbanana already has the right home: anti-pattern **#6 "Trusting GenAI Output Without a Communication-Context Review"** (its post-generation review, the only place the model is told to look at the rendered image with a checklist). I extend that review with the Tell Pass as a **new step 0, checked before the existing key-message / context / canon checks**, because it dominates them.

**Anchor — quote the existing lines in `<anti_patterns>` #6:**

```
Per Fujii 2026 §"Choose the right graph and colour", GenAI text-to-figure tools tend to map data 1:1 to a default visualisation without considering message, audience, or interaction context. After every generation, run the post-generation review:

1. **Key message check:** does the figure convey the single takeaway from the caption / Stage 1 input?
```

Insert a new numbered item **before** "1. Key message check" (and renumber 1→2, 2→3, 3→4):

```markdown
1. **Generative-Artifact Tell Pass (CATEGORICAL — run FIRST, dominates the
   checks below).** `Read` the generated PNG and walk the per-tell checklist,
   T1→T4 in order, one written justification each (Imagen raster is the primary
   risk surface for garbled text and melted glyphs):
   - **T1 Lexical validity** — every label/callout a real word? Glyph-strings
     like `diƨlocttal` ⇒ score 2.
   - **T2 Glyph integrity** — melted/fused/morphing letterforms ⇒ score 2.
   - **T3 Encoding↔printed-value** — printed numbers match geometry; parts sum
     to whole ⇒ else score 2.
   - **T4 Physical/pathway plausibility** — impossible anatomy/topology, arrows
     to nothing ⇒ score 2.
   - **T5 Axis/label coherence** (graded) · **T6 default-template feel**
     (weak, two-sided — do NOT strip decoration to lower it; Bateman CHI2010).
   **Any T1–T4 = 2 ⇒ the figure is rejected: refine via the Critic loop or
   tighten the caption and regenerate — do not accept.** Emit the `tell_pass`
   vector into the review log. A clean pass is **no positive evidence**, not
   proof; T3 checks only printed values, not whether the source numbers are real.
```

**Also wire into Stage 3 (Quality Evaluation) Exit Criteria.** Anchor:

```
**Exit Criteria:**
- [ ] Quality score meets document type threshold
- [ ] Review log includes per-dimension scores
- [ ] **Figure complexity matches Stage 1 communication-context tag** (Fujii 2026)
- [ ] No critical issues flagged
```

Insert:

```
- [ ] **Generative-Artifact Tell Pass clean** — no ⚑ categorical tell (T1–T4) scored 2; `tell_pass` vector in review log
```

**Extend the review-log JSON** so the vector is persisted. Anchor — the `### Review Log Structure` block, after the per-iteration `"meets_threshold": false` line, add a sibling key in the iteration object:

```json
"tell_pass": {
  "T1": {"score": 0, "categorical": true,  "justification": "all labels valid: 'RNA-seq', 'alignment', 'DESeq2'"},
  "T2": {"score": 0, "categorical": true,  "justification": "glyphs intact"},
  "T3": {"score": 0, "categorical": true,  "justification": "no printed values on marks; N/A-equivalent, scored 0"},
  "T4": {"score": 0, "categorical": true,  "justification": "workflow arrows connect named real stages"},
  "T5": {"score": 1, "categorical": false, "justification": "legend has one orphaned entry"},
  "T6": {"score": 0, "categorical": false, "justification": "bespoke to brief"},
  "verdict": "accept_with_notes"
}
```

paperbanana needs **no new reference file** — point it at the svg-figure-maker doc to avoid duplication. Add one row to paperbanana's `<references>` table. Anchor:

```
| `../shared/references/pre_submission_checklist.md` | 15-point unified quality gate (Q0 = "should this be a table?") |
```

Insert:

```
| `../svg-figure-maker/references/generative_artifact_tells.md` | Generative-Artifact Tell Pass (T1–T6) — categorical AI-tell checklist; run at the head of the post-generation review |
```

(If a cross-skill home is preferred over an svg-figure-maker-owned doc, the canonical location should instead be `skills/shared/references/generative_artifact_tells.md`, with both skills pointing there — this matches the plugin's "shared references registry" convention and is the cleaner long-term placement.)

---

## 6. Concrete test cases (for the doc's worked examples / future fixtures)

These are the anchors a second reviewer should reproduce; include them in the new ref doc as a calibration table.

| Case | Figure | Expected vector | Expected verdict |
|---|---|---|---|
| **Frontiers rat** (paperbanana) | label reads `diƨlocttal stem ells`; arrows to nothing; impossible anatomy | T1=2, T2=2, T4=2 | `regenerate` (T1 alone suffices) |
| **Bar value mismatch** (svg) | bar labeled "42" but drawn to the 30-gridline | T3=2 | `regenerate` |
| **Pie not summing** (svg/paperbanana) | slices labeled 40/35/30 (=105%) | T3=2 | `regenerate` |
| **Raw-index axis** (svg) | x-ticks render `1,2,3,4` instead of the category names | T3=0, T5=2 | `accept_with_notes` (graded, not categorical) |
| **Busy-but-correct Holmes infographic** (paperbanana) | heavy embellishment, all text valid, geometry matches | T1–T4=0, T6=1 | `clean_no_positive_evidence` — **must NOT regenerate**; do not strip decoration |
| **Over-minimized regression-to-mean** (svg) | decoration removed to a bland matplotlib-default look | T1–T4=0, T6=2 | `accept_with_notes`, do not "fix" by removing more |
| **One typo** (svg) | legend reads `Treatement` | T1=1 | `accept_with_notes` (1, not categorical 2) |
| **Clean bespoke figure** (svg) | valid text, matched geometry, brand palette | all 0, T6=0 | `clean_no_positive_evidence` |

The last two are the false-positive guards: a single ordinary typo (T1=1) and a clean figure must **not** trigger regenerate, and a "busy" figure must never be down-scored on T6 alone.

---

## Files to create / edit (all absolute paths)

- **EDIT** `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/svg-figure-maker/SKILL.md` — Stage 5 step insertion + Exit Criteria + new anti-pattern #7 + `<references>` row (anchors in §4a/4c).
- **CREATE** `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/svg-figure-maker/references/generative_artifact_tells.md` — the §1–§3 content (or place at `skills/shared/references/generative_artifact_tells.md` per the §5 note).
- **EDIT** `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/svg-figure-maker/references/visual_critique_checklist.md` — "Run the Tell Pass FIRST" pointer (anchor in §4e).
- **EDIT** `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/svg-figure-maker/schemas/critique_finding.schema.json` — add `generative_tell` enum value + optional `tell` object (anchor in §4d).
- **EDIT** `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/paperbanana/SKILL.md` — anti-pattern #6 new step 1 + Stage 3 Exit Criteria + review-log JSON `tell_pass` + `<references>` row (anchors in §5).

**Load-bearing exact strings:** the schema `category` enum currently ends `"accessibility",` `"other"` — insert `"generative_tell"` between them; the `principle_ref` regex `^(§[0-9]+(\.[0-9]+)*|N/A)$` already permits `"N/A"`, so generative-tell findings need no regex change.

**One out-of-scope correction noticed (flagged, not in my task):** the prompt's note about `pre_submission_checklist.md` items #13/#14 pointing at `validate_figure.py` when `check_continuous_as_bars`/`check_riskratio_as_bars` live in `validate_data.py` is a real pointer bug but belongs to Track B, not this Track-C vision-loop work — I did not touch it.