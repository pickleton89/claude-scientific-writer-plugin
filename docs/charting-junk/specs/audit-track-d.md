Confirmed: the pointer bug is real (`check_continuous_as_bars` / `check_riskratio_as_bars` are NOT in `validate_figure.py`; they live in `validate_data.py`). I now have everything I need to write the concrete spec. Let me compose the deliverable.

---

# Track D — Inbound Third-Party Figure-Audit Capability: Concrete Spec

## 0. Decision & justification: HOME = peer-review (hybrid, rubric-in-peer-review)

**Recommendation: Option A (new figure-integrity reviewer inside `skills/peer-review/`), NOT Option B, and NOT a hybrid that routes findings through the verifier's contract machinery.**

Grounding from the code I read:

- **The verifier's contract system is structurally text/citation-shaped and would have to be torn open.** Per `CONTRACTS.md`, its 10-value Verdict enum is entirely citation/quote/number semantics (`VERIFIED`…`QUOTE_FABRICATED`), and `validate_finding.py` predicates are hard-wired to that world: **P3** requires every evidence entry to carry "a resolvable URL / PMID / DOI"; **P2** requires `len(verification_path) >= 2` for CRITICAL; **P5** computes severity off the 70-cell `Verdict × DocumentType` matrix; **P7/P9** are Scite/metadata-resolution gates. A figure audit produces none of those — its "evidence" is *a pixel region in an image the user handed us*, which has no DOI and cannot satisfy P3. Adding a figure-verdict family means (the project's own rule, from CLAUDE.md) "touching schema+validator+CONTRACTS+predicates+fixtures together" — and worse, it would force figure findings to be either exempted from or contort P2/P3/P5/P7/P9. The precedent the repo *already chose* for a non-citation finding family is instructive: the `STYLE_NONCONFORMING` family (CONTRACTS.md §355) was deliberately built as a **parallel pipeline** (`style_findings[]`) that "does NOT enter the 10-value Verdict enum or the 70-cell Severity matrix." A figure family would be a *second* such bolt-on, and figure audits are even further from citation-shaped than prose is.

- **peer-review already owns figure/presentation review and the right primitives.** Stage 5 ("Figure and Data Presentation") already covers integrity checks, image manipulation, and figure quality thresholds (SKILL.md §386-420). It already has `scripts/figure_checker.py` (PIL-based file-level checks), `references/presentation_review.md` (image-based review workflow via `pdf_to_images.py`), `schemas/`, `validators/`, `calibration/`, and a **compact JSON fork-return contract** (SKILL.md §708-740) that is *the natural carrier* for a "vector of flagged sub-scores." Its severity vocabulary (`Critical/Major/Minor/Optional`, SKILL.md §516) is *advisory-by-construction* — it produces reviewer comments, never dispositions — which is exactly what every integrity body in both reports demands.

- **Advisory framing is native to peer-review, alien to the verifier.** The verifier is contract-*governed*: it produces machine-validated verdicts that gate rendering (`ARTIFACT_ENFORCEMENT="required"` blocks output on predicate failure). That is the opposite of what Track D must be — Report 2 §7 is explicit: "the burden the score supports is 'obtain raw data / provenance / author response,' not 'conclude misconduct'… adjudication stays human." Wiring figure findings through a *blocking* validator fights this requirement; wiring them through peer-review's narrative + compact-JSON return honors it.

**The one verifier mechanism worth borrowing (not routing through):** the **two-stage continue-on-failure validator pattern** (CONTRACTS.md §424-437) and the **schema-then-predicates discipline**. The new capability gets its *own* small schema + validator under `peer-review/schemas/` and `peer-review/validators/`, copying the *intent* of that pattern, not importing the verifier's `SchemaValidator`. This keeps determinism without inheriting citation-shaped predicates.

**Net:** rubric, tiers, schema, validator, and fixtures all live in **peer-review**. The verifier is untouched. A cross-link is added in each direction so the two skills know about each other.

---

## 1. The rubric instrument — one coherent capability

New reference file: **`skills/peer-review/references/figure_integrity_audit.md`**. It fuses Report 2's v0.1 6-dimension/0-2/⚑ rubric with Report 1's tiered scorer, and **demotes Report 1's image→data recovery to advisory** per the governing insight (we only hold ground-truth for figures *we* generate; inbound figures we don't, so OCR/CV stays triage).

### 1.1 Tier plan — what we build now vs defer

| Tier | What | Build now? | Why |
|---|---|---|---|
| **Tier 1 — deterministic** | Misviz-style axis-metadata + arithmetic-closure rules, run **only when the user supplies machine-readable source** (the generating SVG, the matplotlib/Vega spec, or a values table). Reuses Track B linters. | **BUILD NOW** | Highest precision, explainable, zero model risk. This is the *only* place the inbound track gets ground-truth, and only when the user volunteers it. |
| **Tier 2 — CV/segmentation** | data-ink ratio, gridline density, color entropy, 3D/geometry forensics. | **DEFER** | Report 1: estimators are reasoned extensions (MEDIUM), need a labeled calibration corpus we don't have. These map to the **weak, two-sided** Dimension 6 — building them now risks an over-minimization regression (Bateman). |
| **Tier 3 — instrumented multimodal LLM-judge** | The 6-dimension rubric scored by Claude as vision-judge, with explicit per-tell checklists + written justifications. | **BUILD NOW (as the primary inbound path)** | This *is* peer-review's existing image-inspection workflow (`pdf_to_images.py` → read each image). The rubric instruments it. Report 1 endorses LLM-judge for the perceptual/semantic axes *when instrumented and treated as triage*. |
| **Forensic "AI-generated" classifier** | A binary "was this AI-made" gate. | **DO NOT BUILD / DO NOT GATE** | SciFigDetect: detectors "fail dramatically in zero-shot transfer… fragile under post-processing." Report 2 §3: tells are decaying. We score **artifact-and-integrity, provenance-agnostic**. Dimension 4 stays present but explicitly "tool-flag only, 4.x=0 is never exoneration." |

So: **Tier 1 (deterministic, conditional on source) + Tier 3 (instrumented vision-judge) ship now. Tier 2 deferred. AI-detection classifier never.**

### 1.2 The six dimensions (adapted verbatim-in-spirit from Report 2 §6, weights 3-3-2-1-2-1)

Scored 0/1/2; ⚑ = categorical (a single ⚑=2 dominates the vector regardless of aggregate). N/A allowed + renormalize.

- **D1 Text & symbol integrity ⚑** (×3) — 1.1 lexical validity of labels ⚑, 1.2 glyph integrity ⚑, 1.3 symbol/notation correctness, 1.4 number plausibility. *Frontiers-rat tells. Strongest discriminator.*
- **D2 Quantitative & semantic correctness** (×3) — 2.1 encoding–value fidelity ⚑, 2.2 closure/conservation ⚑, 2.3 axis–data coherence (raw-index labels), 2.4 legend–series correspondence, 2.5 external data verification. *The covert Class-B tell.*
- **D3 Physical/biological/logical plausibility** (×2) — 3.1 anatomical realism ⚑, 3.2 process/pathway logic, 3.3 optical consistency, 3.4 continuity of repeated elements.
- **D4 Render & signal artifacts** (×1) — 4.1 texture naturalness, 4.2 absence-of-manipulation-markers paradox, 4.3 frequency-domain flag. *Decaying, probabilistic. Carries the "4.x=0 ≠ exoneration" caveat on its face.*
- **D5 Provenance & metadata** (×2) — 5.1 disclosure consistency, 5.2 file/vector provenance, 5.3 reuse/panel duplication.
- **D6 Stylistic slop markers** (×1, **WEAK, TWO-SIDED, down-weighted**) — 6.1 gratuitous decoration vs data-ink, 6.2 template/default-distribution look, 6.3 effort-asymmetry. **Carries the Bateman caveat inline: "embellishment alone does not impair (may aid) comprehension; D6 may NEVER trigger an AI/slop verdict on its own; a *too-minimal* figure is also flagged here, not rewarded."**

### 1.3 The ⚑ categorical override (the second guardrail, encoded)

The instrument states, in bold, on its face:
> CATEGORICAL OVERRIDE: if any ⚑ metric (1.1, 1.2, 2.1, 2.2, 3.1) scores 2, the audit verdict is `FIGURE_INTEGRITY_FLAG` regardless of the weighted aggregate. Aesthetic dimensions (D6) and decaying signals (D4) are corroborating texture only — they can NEVER, alone or summed, produce an integrity flag. The model is NEVER instructed to strip decoration or minimize ink; over-minimization is itself a D6 finding (regression-to-mean failure, Bateman CHI2010).

---

## 2. The figure-audit finding JSON schema

New file: **`skills/peer-review/schemas/figure_audit_finding.json`** (Draft-07). It deliberately mirrors the *shape* of the verifier's `style_finding.json` (own array, own vocabulary, no entry into the 10-value enum) but is owned by peer-review.

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "figure_audit_finding.json",
  "title": "FigureAuditFinding",
  "description": "Advisory inbound figure-integrity finding. NOT a verifier verdict; never dispositive.",
  "required": ["id", "figure_ref", "dimension", "metric_id", "score",
               "categorical", "severity", "tier", "observation",
               "recommended_action", "confidence"],
  "properties": {
    "id":          { "type": "string" },                       // "FA001" sequential
    "figure_ref":  { "type": "object", "required": ["file"],
                     "properties": {
                       "file":  { "type": "string" },          // path/filename of inbound figure
                       "panel": { "type": ["string","null"] }, // "A", "1B", or null (whole figure)
                       "region":{ "type": ["string","null"] }  // free-text locus, e.g. "y-axis tick labels"
                     } },
    "media_class": { "enum": ["A_generated_illustration","B_data_chart",
                              "C_photographic","unknown"] },    // Report 2 §2 three classes
    "dimension":   { "enum": ["D1_text_symbol","D2_quant_semantic","D3_plausibility",
                              "D4_render_artifact","D5_provenance","D6_stylistic"] },
    "metric_id":   { "type": "string" },                       // "1.1","2.2","6.1" ...
    "score":       { "enum": [0, 1, 2] },                      // 0 clean / 1 ambiguous / 2 clear tell
    "categorical": { "type": "boolean" },                      // true iff metric_id in {1.1,1.2,2.1,2.2,3.1}
    "severity":    { "enum": ["CRITICAL","MAJOR","MINOR","INFORMATIONAL"] },
    "tier":        { "enum": ["1_deterministic","3_vision_judge"] },  // no tier 2 yet; no AI-detector
    "source_check":{ "type": ["string","null"] },              // Tier-1 only: linter fn that produced it,
                                                               //  e.g. "validate_data.check_riskratio_as_bars"
    "observation": { "type": "string", "minLength": 1 },       // what a 2nd reviewer would also see
    "evidence_snippet": { "type": ["string","null"] },         // OCR'd string / printed-vs-encoded values
    "recommended_action": { "type": "string", "minLength": 1 },// MUST be triage-shaped (see §4)
    "confidence":  { "enum": ["high","medium","low"] },
    "decaying_signal_caveat": { "type": ["string","null"] }    // required iff dimension == "D4"
  }
}
```

### 2.1 Verdict/severity vocabulary — three audit-level verdicts, NOT mapped into the verifier enum

The **audit-level** roll-up (distinct from per-metric findings) uses a **new, peer-review-local 3-value figure-verdict family**. It does **not** map onto the verifier's 10-value enum and does **not** touch the `Verdict × DocumentType` matrix:

| Audit verdict | Trigger | Meaning |
|---|---|---|
| `FIGURE_INTEGRITY_FLAG` | any ⚑ metric = 2 **OR** any Tier-1 deterministic hard mismatch | "Categorical tell present — obtain source data/provenance." Strongest. |
| `FIGURE_REVIEW_RECOMMENDED` | weighted index in the "converging tells" band, no ⚑=2 | "Multiple soft signals — closer human review warranted." |
| `FIGURE_NO_POSITIVE_EVIDENCE` | clean | "No positive evidence of AI authorship — NOT proof of human authorship (tells decay)." |

**Why a new family, not the existing enum:** the existing 10 verdicts are propositions about *a citation and its resolved record*. A figure audit asserts *a property of an image*. Forcing `CONTRADICTED`/`UNSUPPORTED` onto pixel observations would be a category error and would drag in P2/P3/P5. **Per-metric severity** still uses the shared 4-value `{CRITICAL,MAJOR,MINOR,INFORMATIONAL}` so it slots cleanly into peer-review's existing `concern_counts` and `top_concerns` fork-return — but it is assigned by a **small explicit table in the rubric** (⚑=2 → CRITICAL; non-⚑ score 2 → MAJOR; score 1 → MINOR; D6-only → never above MINOR), **not** computed from the verifier's matrix.

### 2.2 Per-metric → severity table (deterministic, lives in the validator)

```
⚑ metric score 2                      → CRITICAL   (then audit verdict = FIGURE_INTEGRITY_FLAG)
non-⚑ metric score 2 (D1–D3,D5)       → MAJOR
any metric score 1                    → MINOR
D4 any score                          → at most MINOR + decaying_signal_caveat required
D6 any score                          → at most MINOR; INFORMATIONAL if it is an over-minimization note
score 0                               → INFORMATIONAL (emitted only in full matrix, not in findings[])
```

---

## 3. Where Tier-1 deterministic rules reuse the Track B linters

Tier 1 runs **only when the user hands us machine-readable source** (this is the inbound analogue of the governing insight). Concrete reuse, by import:

| Tier-1 rule | Reuses | Maps to metric | Source-input required |
|---|---|---|---|
| Risk/odds/hazard-ratio drawn as bars | `plotting-libraries/scripts/validate_data.py::check_riskratio_as_bars(plot_type, data_label)` | 2.1 encoding-value fidelity (graded, not ⚑) | plot type + axis label (from spec or OCR) |
| Continuous distribution drawn as bars | `plotting-libraries/scripts/validate_data.py::check_continuous_as_bars(data, plot_type)` | 2.1 / D2 | values table + plot type |
| SVG garbled-text / off-palette / banned chrome | `svg-figure-maker/scripts/preflight_check.py::run_checks(...)` (the JSON-finding linter) | 6.1/6.2 chrome (warn-level, two-sided) | the source `.svg` |
| File-level resolution/format/DPI sanity | `peer-review/scripts/figure_checker.py::check_figure_quality(path)` (already in-skill) | 5.2 provenance / D4 render | the image file |
| Axis-truncation / inverted-axis / inconsistent-tick (Misviz linter rules) | **NEW** `peer-review/scripts/figure_axis_lint.py` (the only net-new Tier-1 code) | 2.3 axis-data coherence | axis metadata from spec |
| Parts-not-summing-to-whole / stacked-total reconciliation | **NEW** in `figure_axis_lint.py` (`check_closure(parts, whole)`) | 2.2 closure ⚑ | values table |

The new `figure_axis_lint.py` is a thin PEP-723 stdlib-only adapter that (a) imports the two `validate_data.py` functions, (b) adds the Misviz axis-metadata rules + closure arithmetic that no existing linter covers, and (c) emits findings in the §2 schema shape. Signature sketch:

```python
# skills/peer-review/scripts/figure_axis_lint.py  (PEP-723, stdlib-only + optional sibling import)
def check_axis_truncation(axis_meta: dict) -> list[dict]:
    """Misviz rule: quantitative bar-chart axis whose origin != 0.
       axis_meta = {"type":"quantitative","chart":"bar","min":<float>,"max":<float>,"data_min":<float>}
       Returns [] or one finding (metric 2.3, score 2, categorical=False) with
       severity_hint MAJOR and severity-scaling note (suppressed_range/full_range)."""

def check_closure(parts: list[float], whole: float | None, *, tol: float = 0.005) -> list[dict]:
    """⚑ metric 2.2: pie/stacked parts must sum to whole (100% or stated total).
       |sum(parts) - (whole or 100)| > tol*scale -> finding score 2, categorical=True."""

def run_tier1(*, svg_path=None, axis_meta=None, values=None, plot_type=None,
              data_label=None, image_path=None) -> dict:
    """Orchestrator. Calls only the checks whose inputs are present.
       Reuses validate_data.check_riskratio_as_bars / check_continuous_as_bars,
       preflight_check.run_checks, figure_checker.check_figure_quality.
       Returns {tier:'1_deterministic', findings:[...], inputs_seen:[...]}.
       If NO machine-readable source supplied -> returns findings=[] with a
       note 'tier1_skipped_no_source' so the audit falls through to Tier-3 only."""
```

**Fix the pointer bug while here (load-bearing — I verified it):** `pre_submission_checklist.md` items #13/#14 and its tooling table point to `plotting-libraries/scripts/validate_figure.py::check_continuous_as_bars` / `::check_riskratio_as_bars`, but `grep` confirms `validate_figure.py` contains only `validate_figure`, `_validate_pdf`, `_validate_raster`, `print_validation`, `validate_figure_for_journal` — the two functions actually live in **`validate_data.py`**. Three edits to apply:

- Line 117: `plotting-libraries/scripts/validate_figure.py::check_continuous_as_bars` → `…/validate_data.py::check_continuous_as_bars`
- Line 149 (table): same fix
- Line 150 (table): `validate_figure.py::check_riskratio_as_bars` → `validate_data.py::check_riskratio_as_bars`

---

## 4. Advisory framing / output contract

The instrument and schema enforce triage-not-disposition mechanically:

1. **Vector, never composite.** The capability returns `figure_audit_findings[]` (one per scored metric ≥1) plus a `dimension_vector` of the six per-dimension sub-scores, plus the single audit verdict from §2.1. It **never** emits a 0–100 "slop score" as the headline; the weighted index is reported only as a *secondary, explicitly-uncalibrated* number with the literal string `"provisional, uncalibrated"` adjacent. (This satisfies guardrail 1 and Report 1's "vector of interpretable sub-scores, not a single verdict.")

2. **Recommended-action lexicon is constrained.** `validators/figure_audit_validator.py` enforces predicate **FA-P4** (below): `recommended_action` must match an allowed triage template (`"obtain source data"`, `"request generating code/spec"`, `"request provenance / AI-use disclosure"`, `"flag for closer human review"`, `"verify against cited source"`) and must **not** contain banned dispositive verbs (`/misconduct|fabricat(ed|ion)|fraud|guilty|confirmed AI/i`). A finding asserting misconduct fails validation.

3. **Two interpretive rules printed on every report** (from Report 2 §7, verbatim intent): "A clean score is NOT proof of human authorship" and "the burden is *obtain raw data / provenance / author response*, not *conclude misconduct* — adjudication stays human."

4. **Hard predicates** (the peer-review-local analogue of P1–P9, enforced by the new validator using the copied two-stage continue-on-failure pattern):
   - **FA-P1.** `categorical == true ⟺ metric_id ∈ {1.1,1.2,2.1,2.2,3.1}`.
   - **FA-P2.** `severity == CRITICAL ⟹ categorical == true AND score == 2` (only a ⚑=2 can be CRITICAL — aesthetics can't).
   - **FA-P3.** `dimension == "D6" ⟹ severity ∈ {MINOR, INFORMATIONAL}` (Bateman down-weight, encoded; two-sided — an over-minimization note is valid D6 output).
   - **FA-P4.** `recommended_action ∈ allowed-template-set AND no banned-dispositive-verb` (advisory framing, encoded).
   - **FA-P5.** `dimension == "D4" ⟹ decaying_signal_caveat is non-null` (4.x=0 ≠ exoneration, encoded).
   - **FA-P6.** `tier == "1_deterministic" ⟹ source_check is non-null` (Tier-1 findings must name the linter that produced them — no hallucinated deterministic results).
   - **FA-P7.** audit verdict `FIGURE_INTEGRITY_FLAG ⟹` at least one finding with `score==2 AND (categorical==true OR tier=="1_deterministic")` (the flag can't be raised on soft signals alone).

5. **Fork-return integration.** Figure-audit findings flow into peer-review's existing compact JSON return (SKILL.md §708) as a new optional block, keeping the ≤800-token discipline and the "no quoted manuscript text" rule:

```jsonc
"figure_audit": {
  "enabled": true,
  "figures_audited": 2,
  "audit_verdict": "FIGURE_REVIEW_RECOMMENDED",   // the §2.1 family
  "dimension_vector": { "D1":0,"D2":1,"D3":0,"D4":0,"D5":1,"D6":1 },
  "weighted_index": { "value": 28, "scale": "0-100", "status": "provisional, uncalibrated" },
  "categorical_flags": [],                          // metric_ids with score 2 that are ⚑
  "tier1_source_provided": true,
  "top_figure_concerns": [
    { "id":"FA003","metric_id":"2.3","severity":"MAJOR",
      "observation":"y-axis ticks render as raw indices 1,2,3 not categories",
      "recommended_action":"request generating code/spec" }
  ]
}
```

---

## 5. Regression fixtures to add

Under **`skills/peer-review/scripts/tests/fixtures/figure_audit/`**, with a `test_figure_audit_validator.py` (pytest, mirrors `test_severity_classifier.py` style) asserting each fixture's expected verdict + which predicate fires. Each fixture = a tiny input (SVG / axis-meta JSON / values JSON / synthetic PNG) + an expected-finding JSON.

1. **`01_frontrat_void_labels`** — SVG/PNG with lexically-void labels ("diƨlocttal", "testtomcels"). Expect: 1.1 ⚑ score 2 → CRITICAL → `FIGURE_INTEGRITY_FLAG`. (The canonical Class-A tell.)
2. **`02_pie_not_summing`** — values `[40,35,30]`, whole 100. Expect: Tier-1 `check_closure` fires, 2.2 ⚑ score 2 → CRITICAL → `FIGURE_INTEGRITY_FLAG`, `source_check` populated (FA-P6).
3. **`03_riskratio_as_bars`** — `plot_type="bar"`, `data_label="Hazard ratio (95% CI)"`. Expect: reuse of `validate_data.check_riskratio_as_bars` → 2.1 score 1/2, MAJOR, `FIGURE_REVIEW_RECOMMENDED`.
4. **`04_raw_index_axis`** — axis-meta with tick labels `1,2,3,4`. Expect: 2.3 score 2 → MAJOR (Class-B covert tell).
5. **`05_truncated_bar_axis`** — bar-chart axis_meta `min=80,max=100,data_min=0`. Expect: `check_axis_truncation` fires, 2.3 with severity-scaling note.
6. **`06_embellished_but_clean` (NEGATIVE / two-sided guard)** — a heavily decorated Holmes-style chart whose numbers are all correct. Expect: D6 score 1 at most, **no ⚑**, audit verdict `FIGURE_NO_POSITIVE_EVIDENCE`. **Asserts FA-P2/FA-P7: decoration alone does NOT raise a flag** (Bateman; guardrail 2).
7. **`07_over_minimized` (NEGATIVE / over-minimization guard)** — a stripped-bare figure missing gridlines/labels. Expect: D6 INFORMATIONAL over-minimization note, **no integrity flag, no reward**. Asserts the spec never instructs ink-minimization.
8. **`08_clean_with_source`** — valid SVG + matching values table, all checks pass. Expect: empty `findings[]`, `FIGURE_NO_POSITIVE_EVIDENCE`, and the "clean ≠ proof of human" caveat string present.
9. **`09_d4_only_smoothness`** — a synthetic over-smooth panel with no other tells. Expect: D4 finding **requires** `decaying_signal_caveat` (FA-P5); audit verdict stays `FIGURE_REVIEW_RECOMMENDED` at most — **proves D4 alone can't flag** (SciFigDetect down-weight).
10. **`10_dispositive_action_rejected`** — a hand-crafted finding whose `recommended_action="conclude misconduct"`. Expect: **validator FAILS on FA-P4** (advisory-framing guard).

---

## 6. Insertion anchors (quote the surrounding line)

- **peer-review SKILL.md, Stage 5.** Insert a new "Inbound Figure-Integrity Audit (Tier-1 + Tier-3)" subsection immediately after the line:
  `**Integrity Checks:**` ... `- Are representative images truly representative?` (SKILL.md §410-414) — extending the existing integrity block rather than duplicating it. Reference `references/figure_integrity_audit.md` and `scripts/figure_axis_lint.py`.

- **peer-review SKILL.md, Resources table.** Add rows after:
  `| `{baseDir}/scripts/calculate_scores.py` | Automated weighted score calculation |` — for `references/figure_integrity_audit.md`, `scripts/figure_axis_lint.py`, `schemas/figure_audit_finding.json`, `validators/figure_audit_validator.py`.

- **peer-review SKILL.md, fork-return JSON.** Add the `"figure_audit": {...}` block after the `"scoring": { ... }` object (SKILL.md §721-730), with a matching paragraph in the "Required fields" note clarifying it is emitted only when figures were audited.

- **presentation_review.md.** Add a "Garbled-text & encoding-mismatch tells (inbound figures)" block after the `### Layout and Formatting Checklist` section (presentation_review.md §39-49) — the image-inspection workflow there is exactly the Tier-3 vehicle.

- **research-accuracy-verifier SKILL.md / CONTRACTS.md (cross-link only, NO schema change).** Add one sentence under CONTRACTS.md §"What is NOT in Phase-1 contracts" reading: *"Inbound third-party figure-integrity auditing is intentionally OUT of the verifier's contract system — it is owned by `peer-review` (`references/figure_integrity_audit.md`), uses a parallel advisory `figure_audit_finding.json`, and never enters the 10-value Verdict enum or the 70-cell severity matrix (same posture as the STYLE_NONCONFORMING family)."* This records the decision without touching schema/validator/predicates/fixtures.

- **pre_submission_checklist.md.** Apply the three pointer fixes from §3 (lines 117, 149, 150) — independent of Track D but verified during this work.

---

## 7. Files created vs touched (bounded change set)

**New (peer-review only):**
- `skills/peer-review/references/figure_integrity_audit.md` (the fused rubric + tier plan + caveats)
- `skills/peer-review/schemas/figure_audit_finding.json`
- `skills/peer-review/scripts/figure_axis_lint.py` (PEP-723, imports the two `validate_data.py` fns + `preflight_check.run_checks` + `figure_checker.check_figure_quality`; adds Misviz axis rules + closure)
- `skills/peer-review/validators/figure_audit_validator.py` (two-stage continue-on-failure; predicates FA-P1…FA-P7)
- `skills/peer-review/scripts/tests/fixtures/figure_audit/01…10` + `test_figure_audit_validator.py`

**Edited:** `peer-review/SKILL.md` (Stage 5 + Resources + fork-return), `peer-review/references/presentation_review.md` (tells block), `research-accuracy-verifier/references/CONTRACTS.md` (one cross-link sentence), `shared/references/pre_submission_checklist.md` (three pointer fixes).

**Untouched (deliberately):** verifier `schemas/`, `validate_finding.py`, predicates P1–P9, severity matrix, regression fixtures. The verifier never learns about figures beyond the one-line pointer.

Key file paths referenced: `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/peer-review/SKILL.md`, `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/peer-review/scripts/figure_checker.py`, `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/plotting-libraries/scripts/validate_data.py`, `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/svg-figure-maker/scripts/preflight_check.py`, `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/research-accuracy-verifier/references/CONTRACTS.md`, `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/research-accuracy-verifier/scripts/validate_finding.py`, `/Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin/skills/shared/references/pre_submission_checklist.md` (pointer bug confirmed at lines 117/149/150).