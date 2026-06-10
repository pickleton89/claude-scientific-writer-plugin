# Figure-Integrity Audit (FIGURE_INTEGRITY family — inbound, advisory)

> The rubric for auditing a figure the user **hands us** (peer review, accuracy
> verification) — NOT one this plugin generated. For our own output, the exact
> source-side gates apply instead (`svg-figure-maker/scripts/preflight_check.py`,
> `plotting-libraries/scripts/validate_data.py`); see
> `../../shared/references/ai_figure_slop.md`.
> Version: 1.0.0 | Status: canonical (rubric is PROVISIONAL/UNCALIBRATED)
>
> **Parallel advisory family.** Emits `figure_findings[]`, validated by
> `scripts/validate_figure_finding.py` (FD-P1..FD-P7). Does NOT enter the
> 10-value citation Verdict enum or the 70-cell Severity matrix (same posture as
> STYLE_NONCONFORMING). `custom` tier only — `checks_enabled` must include
> `figure_integrity_audit`; no numbered tier auto-includes it.

## Two non-negotiable rules (printed on the instrument)

1. **A clean audit is NO POSITIVE EVIDENCE, never proof of human authorship.**
   Tells are decaying (2026-gen models pass the obvious ones); absence of a tell
   is weak evidence of absence.
2. **The burden it supports is "obtain source data / provenance / author
   response," never "conclude misconduct."** Adjudication stays human — every
   integrity body in the source reports insists on this. Enforced by FD-P4
   (`recommended_action` must be a triage template; dispositive verbs rejected).

## What we build vs. defer

| Tier | What | Status |
|---|---|---|
| **Tier 1 — deterministic** | Misviz axis-metadata rules + arithmetic closure, run **only when the user supplies machine-readable source** (generating SVG, values table, axis metadata). Reuses the Track-B linters via `scripts/figure_axis_lint.py`. | **BUILT** — highest precision, explainable, zero model risk. |
| **Tier 3 — instrumented vision-judge** | The 6-dimension rubric below, scored by Claude as a vision-judge with explicit per-tell checklists + written justifications. This is the verifier's existing image-inspection path. | **BUILT (primary inbound path)** |
| Tier 2 — CV/segmentation | data-ink ratio, gridline density, colour entropy, geometry forensics. | **DEFERRED** — reasoned-extension estimators needing a labelled calibration corpus; map to the weak two-sided D6. |
| "AI-generated" classifier | binary was-this-AI gate. | **NEVER BUILD / NEVER GATE** — SciFigDetect: detectors fail zero-shot. We score artifact-and-integrity, provenance-agnostic. |

## The six dimensions (report-2 §6; weights 3-3-2-1-2-1)

Scored 0 (clean) / 1 (ambiguous) / 2 (clear tell); ⚑ = categorical. N/A allowed + renormalize.

- **D1 Text & symbol integrity ⚑** (×3) — 1.1 lexical validity of labels ⚑, 1.2 glyph integrity ⚑, 1.3 symbol/notation correctness, 1.4 number plausibility. *Frontiers-rat tells; strongest discriminator.*
- **D2 Quantitative & semantic correctness** (×3) — 2.1 encoding–value fidelity ⚑, 2.2 closure/conservation ⚑, 2.3 axis–data coherence (raw-index labels, axis truncation), 2.4 legend–series correspondence, 2.5 external data verification. *The covert Class-B tell.*
- **D3 Physical/biological/logical plausibility** (×2) — 3.1 anatomical realism ⚑, 3.2 process/pathway logic, 3.3 optical consistency, 3.4 continuity of repeated elements.
- **D4 Render & signal artifacts** (×1) — 4.1 texture naturalness, 4.2 absence-of-manipulation-markers paradox, 4.3 frequency-domain flag. *Decaying, probabilistic; carries the "4.x=0 ≠ exoneration" caveat on its face (FD-P5).*
- **D5 Provenance & metadata** (×2) — 5.1 disclosure consistency, 5.2 file/vector provenance, 5.3 reuse/panel duplication.
- **D6 Stylistic slop markers** (×1, **WEAK, TWO-SIDED, down-weighted**) — 6.1 gratuitous decoration vs data-ink, 6.2 template/default-distribution look, 6.3 effort-asymmetry. **Bateman caveat inline: embellishment alone does not impair (may aid) comprehension; D6 may NEVER trigger a flag on its own; a *too-minimal* figure is also flagged here, not rewarded.** Capped at MINOR/INFORMATIONAL by FD-P3.

The five categorical ⚑ metrics are **{1.1, 1.2, 2.1, 2.2, 3.1}** (encoded in `validate_figure_finding.CATEGORICAL_METRICS` and enforced by FD-P1).

## Audit-level verdicts (3 values — NOT the citation enum)

| Audit verdict | Trigger | Meaning |
|---|---|---|
| `FIGURE_INTEGRITY_FLAG` | any ⚑ metric = 2 **OR** any Tier-1 deterministic hard mismatch | "Categorical tell present — obtain source data/provenance." |
| `FIGURE_REVIEW_RECOMMENDED` | converging soft signals, no ⚑=2 | "Multiple soft signals — closer human review." |
| `FIGURE_NO_POSITIVE_EVIDENCE` | clean | "No positive evidence of AI authorship — NOT proof of human authorship." |

The flag cannot be raised on soft/aesthetic signals alone (FD-P7). Per-metric severity uses `{CRITICAL, MAJOR, MINOR, INFORMATIONAL}` assigned by this table — NOT computed from the citation severity matrix:

```
⚑ metric score 2                → CRITICAL   (→ audit verdict FIGURE_INTEGRITY_FLAG)
non-⚑ metric score 2 (D1-D3,D5) → MAJOR
any metric score 1              → MINOR
D4 any score                    → ≤ MINOR + decaying_signal_caveat required (FD-P5)
D6 any score                    → ≤ MINOR; INFORMATIONAL for an over-minimization note (FD-P3)
```

## Hard predicates (FD-P1..FD-P7)

Enforced by `scripts/validate_figure_finding.py`; full statements in `predicates.md`.
FD-P1 categorical⟺metric set · FD-P2 only ⚑=2 can be CRITICAL · FD-P3 D6 ≤ MINOR ·
FD-P4 advisory action template, no dispositive verb · FD-P5 D4 needs caveat ·
FD-P6 Tier-1 names its source linter · FD-P7 (audit-level) flag needs a hard finding.

## Tier-1 reuse map (`scripts/figure_axis_lint.py`)

| Tier-1 rule | Reuses | Metric |
|---|---|---|
| Risk/odds/hazard ratio drawn as bars | `plotting-libraries/scripts/validate_data.py::check_riskratio_as_bars` | 2.1 |
| Continuous distribution as bars | `…validate_data.py::check_continuous_as_bars` | 2.1 |
| Parts-not-summing / stacked total | `…validate_data.py::check_closure` (pie/donut forced to percent-mode) | 2.2 ⚑ |
| Garbled/void SVG labels | `svg-figure-maker/scripts/preflight_check.py::run_checks` (categorical garbled_text) | 1.1 ⚑ |
| Axis truncation (Misviz) | NEW `check_axis_truncation` in this module | 2.3 |

`run_tier1(...)` calls only the checks whose inputs are present; returns
`note="tier1_skipped_no_source"` when no machine-readable source is supplied, so
the audit falls through to Tier-3 only.

## Output contract

`figure_findings[]` (one per scored metric ≥ 1) + a `dimension_vector` of the six
sub-scores + the single audit verdict. **Never a composite 0–100 "slop score"** as
the headline; any weighted index is reported only as a secondary, explicitly
`"provisional, uncalibrated"` number. Vector, not verdict (source report-1).

## Source

`docs/charting-junk/ai-figure-slop-evaluation-2026-06-09.md` (v0.1 rubric) and
`docs/charting-junk/Chart_slop_claude.md` (tiered scorer). The rubric is a
**constructed, uncalibrated instrument** — calibrate on a labelled corpus
(retraction record, PubPeer) before trusting any threshold.
