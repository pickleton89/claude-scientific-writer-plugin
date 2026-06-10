# AI-Figure-Slop Guardrail — Reconciled Integration Spec

> Master implementation blueprint, synthesized from the 7-agent design workflow
> (`wf_87ac292f-4ff`). Per-track raw specs are in `specs/`. This file resolves the
> cross-agent conflicts and is the source of truth for implementation.
> Status: AWAITING GO — 2 decisions flagged for the user (§D).

## Source

Two reports in this directory:
- `Chart_slop_claude.md` — computable metrics framework (3 axes, 5 dims, Misviz/VisEval/RealChart2Code, tiered scorer).
- `ai-figure-slop-evaluation-2026-06-09.md` — v0.1 6-dimension rubric, 3 media classes, Bateman "useful junk", provenance≠quality.

## Governing insight (drives every track)

This plugin **generates** figures, so we hold ground-truth data + source SVG/plot code. The reports' unreliable step — image→data recovery via OCR/forensic CV (SciFigDetect: fails zero-shot) — is **unnecessary for our own output**. Replace it with cheap **exact** deterministic checks. Only Track D (inbound third-party figures, no source) uses the forensic/OCR/rubric stack, and it stays **advisory/triage, never dispositive**.

## Two guardrails honored everywhere

1. **Vector of flagged sub-scores with severities, never a composite "slop score."** All thresholds documented PROVISIONAL/UNCALIBRATED.
2. **Categorical tells dominate; aesthetic/chartjunk signals are weak, down-weighted, two-sided.** Never instruct the model to strip decoration / minimize ink — over-minimization is itself regression-to-mean (Bateman CHI 2010).

---

## Cross-agent conflicts → resolutions

| # | Conflict | Resolution |
|---|---|---|
| C1 | **oligon-brand/SKILL.md is VENDORED** ("do not edit here", synced from `oligon-brand-core`). Guidance agent planned to edit its `<figure_integrity>`/`<design_foundation>` directly. | **Do NOT edit the vendored SKILL.md.** Route oligon-facing anti-slop content into the shared registries it already maps onto (`figure_design_principles.md`, `pre_submission_checklist.md`). The "Rules 9–12" substance lives in the new doctrine `ai_figure_slop.md` §3/§4. **User decision (D1):** optionally also prepare an upstream patch for `oligon-brand-core`. |
| C2 | SVG gate: svg-linter extends existing `preflight_check.py`; wiring-map assumed a new `check_ai_figure_slop.py`. | **Extend `preflight_check.py`** (single deterministic pass, reuses `_finding`/`_collect_color_values`/`run_checks`). Rewrite wiring references from `check_ai_figure_slop.py` → the new checks in `preflight_check.py`. |
| C3 | Doctrine file location + `principle_ref` section numbering (svg-linter proposed a competing skill-local `ai_figure_slop.md` with different §-numbers). | **One canonical file:** `skills/shared/references/ai_figure_slop.md` (doctrine §1–§6). Discard the skill-local copy. preflight `principle_ref` keys → `ai_figure_slop.md§3` (tell catalog) for garbled & raw-index, `ai_figure_slop.md§4` (regression-to-mean) for default-palette. |
| C4 | Plot fn naming: `check_closure` (plot-linter) vs `check_parts_sum_to_whole` (wiring/track-D). | Standardize on **`check_closure`**. Update wiring + Track D references. |
| C5 | Track C doc: svg-figure-maker-local vs shared. | Place at **`skills/shared/references/generative_artifact_tells.md`**; both svg-figure-maker and paperbanana point there. |
| C6 | `pre_submission_checklist.md` edited by 4 agents (pointer fix + new items + tooling rows). | **One merged edit:** the "Generative-artifact Integrity" subsection (items #16–20 from guidance-edits) + plot-linter's tooling rows + single pointer fix (`validate_figure.py`→`validate_data.py`). Retitle "15-point"→"20-point". |
| C7 | Doctrine "Used by" list ≠ wired skill set. | Align "Used by" to the actually-wired skills: plotting-libraries, svg-figure-maker, scientific-schematics, research-posters, paperbanana, scientific-slides, generate-image. Note oligon-brand consumes via shared registries; peer-review/verifier via Track D. |
| C8 | New `"categorical"` severity introduced into `preflight_check.py` (4th severity above `fail`). | Accept — it cleanly encodes Guardrail 2. Wire into `run_checks` (`categorical_count`, `overall` flip) + `anti_patterns.md` severity map. |

---

## Track A — Principles / prevention (guidance layer)

**A1. NEW `skills/shared/references/ai_figure_slop.md`** — canonical doctrine. Content = `specs/doctrine.md` with reconciliations C3/C7 applied. §1 provenance≠quality, §2 three axes (point to existing canon for A/B), §3 categorical-vs-graded tell catalog, §4 regression-to-mean catalog (+ two-sided Bateman caveat), §5 enforcement forward-pointers (Tracks B/C/A3/D), §6 references.

**A2. oligon-brand content → shared registries (C1).**
- `figure_design_principles.md`: add new **§10 "AI figure slop & regression-to-mean"** (cross-link + 6-row takeaway table); renumber §10→§11, §11→§12. Append 2 anti-pattern rows (15–16: lexically-void/raw-index labels; encoding≠value/closure) to the §7 table + a discovery bullet in the header.
- (Upstream-optional, D1) the "Rules 9–12" + two-sided pitfall for `oligon-brand-core`.

**A3. `pre_submission_checklist.md` (C6).** New "Generative-artifact Integrity" subsection, items #16–20 (garbled labels / non-default palette / encoding-value fidelity / closure / real-category labels). Fix the `validate_figure.py`→`validate_data.py` pointer (item #13 + tooling rows #13/#14). Add tooling rows for the new checks. Retitle header to "20-point".

## Track B — Deterministic gate on our own output

**B1. `skills/svg-figure-maker/scripts/preflight_check.py`** (extend; C2/C8). Add `import unicodedata, string`; 3 checks + helpers:
- `check_garbled_text` → severity `categorical` on void tokens, `warn` on soft. (`ai_figure_slop.md§3`)
- `check_default_palette_fingerprint(root, palette)` → `warn`, brand-exempt, ≥3-hit floor. (`ai_figure_slop.md§4`)
- `check_raw_index_labels` → `warn`, numeric-axis-suppressed. (`ai_figure_slop.md§3`)
- Wire 3 `findings.extend(...)` after `check_palette_compliance`; add `categorical_count` + `overall` flip.
- NEW tests: `scripts/tests/test_check_garbled_text.py`, `…default_palette_fingerprint.py`, `…raw_index_labels.py` (cases in `specs/svg-linter.md`).
- Extend `references/anti_patterns.md` severity map (3 rows + `categorical` severity note).

**B2. `skills/plotting-libraries/scripts/validate_data.py`** (extend). Add 3 `ValidationResult` checks:
- `check_encoding_value_fidelity(values, encoding, *, printed_labels, geometry, …)` → `add_error` on mismatch (categorical), `add_warning` soft.
- `check_closure(parts, encoding, *, declared_total, expect_percent, …)` → two-band tolerance (warn rounding / error closure-fail).
- `check_default_palette(palette, …)` → `add_warning` only, brand/CVD palettes verified clean.
- Tests → `scripts/tests/test_plot_selector.py` (3 new classes, cases in `specs/plot-linter.md`).
- Docstring import block + banner comment updates.

**B3. Wiring (C2/C4).** Per-skill workflow steps reference the extended `preflight_check.py` (SVG) and `validate_data.py` (plots). See Track-wiring below.

## Track C — Instrumented vision-QA

**C1. NEW `skills/shared/references/generative_artifact_tells.md`** (C5) — the T1–T6 "Generative-Artifact Tell Pass" (content = `specs/vision-qa.md` §1–§3, shared location).
- `svg-figure-maker/SKILL.md` Stage 5: insert Tell Pass as step 2 (before aesthetic walk) + Exit Criteria line + anti-pattern #7 ("decoration removal is not a slop fix") + references row + schema extension (`generative_tell` enum value + optional `tell` object in `schemas/critique_finding.schema.json`).
- `paperbanana/SKILL.md` anti-pattern #6: insert Tell Pass as step 1 (dominates) + Stage 3 Exit Criteria + review-log `tell_pass` block + references row (points at the shared doc).

## Track D — Inbound figure audit (advisory) — **home = peer-review (D2)**

NEW, all under `skills/peer-review/`:
- `references/figure_integrity_audit.md` — fused rubric (report-2 6-dim/0-2/⚑ + report-1 tiers). Tier 1 (deterministic, conditional on user-supplied source — reuses Track B linters) + Tier 3 (instrumented vision-judge) ship now; Tier 2 deferred; AI-detector classifier never.
- `schemas/figure_audit_finding.json` — Draft-07, mirrors the `STYLE_NONCONFORMING` parallel-pipeline precedent. 3 audit verdicts (`FIGURE_INTEGRITY_FLAG`/`FIGURE_REVIEW_RECOMMENDED`/`FIGURE_NO_POSITIVE_EVIDENCE`), NOT in the verifier's 10-value enum.
- `scripts/figure_axis_lint.py` — PEP-723, imports `validate_data.check_*` + `preflight_check.run_checks` + `figure_checker.check_figure_quality`; adds Misviz axis rules + `check_closure`.
- `validators/figure_audit_validator.py` — predicates FA-P1…FA-P7 (two-stage continue-on-failure pattern).
- `scripts/tests/fixtures/figure_audit/01–10` + `test_figure_audit_validator.py`.
- Edits: peer-review SKILL.md (Stage 5 + Resources + fork-return `figure_audit` block), `references/presentation_review.md` (tells block).
- **Verifier untouched** except ONE cross-link sentence in `CONTRACTS.md` recording the out-of-scope decision (parallel to STYLE_NONCONFORMING).

## Router wiring

- `SKILL_ROUTER.md`: figure-audit leaf under the verifier audit tree + a routing-table row → Track D (advisory).
- `skill-router/skill_triggers.yaml`: add Track-D figure-audit keywords/triggers to `research-accuracy-verifier`; add `negative_keywords` to the 5 figure-creation skills so "audit this figure" doesn't pull a generator. Bump registry version.

## Per-skill cross-link + workflow wiring (Track B/C consumers)

Drop-in anchors in `specs/wiring-map.md` (apply C2/C4 substitutions). Skills: plotting-libraries, svg-figure-maker, scientific-schematics, research-posters, paperbanana, scientific-slides (oligon-brand via registries, C1).

---

## D. Decisions for the user

**D1 — oligon-brand (vendored).** Route anti-slop content into shared registries only (safe, recommended) — and additionally prepare an upstream patch for `oligon-brand-core` (so "Rules 9–12" appear in the brand SKILL body after the next sync)? Or registries-only for now?

**D2 — Track D home.** Confirm **peer-review** (recommended; keeps the verifier's citation-shaped predicates P1–P9 untouched, mirrors the STYLE_NONCONFORMING parallel-pipeline precedent), or route Track D through the research-accuracy-verifier contract system instead?

## Implementation sequencing (post-go)

Shared files have multi-agent contention (pre_submission_checklist, figure_design_principles) → edit sequentially, not via parallel worktrees. NEW files (doctrine, tells doc, Track D files, tests) → safe to fan out. Run `uv run pytest` on the two extended script dirs after B1/B2.
