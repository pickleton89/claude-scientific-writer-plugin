# Migration guide — required-mode artifact enforcement (Phase 3)

Phase 3 flipped `scripts/thresholds.ARTIFACT_ENFORCEMENT` from `"advisory"` to `"required"`. This document describes what that means for audits started before the flip and how to render / re-validate them.

## What changed

Before the flip (Phases 1+2, advisory mode):

- `validate_audit_report.py` emitted **warnings** when R1–R6 failed or when the cross-artifact artifacts (`document_inventory.json`, `reference_map.json`, `resolved_sources.json`, `external_evidence.json`) weren't supplied. `ok=True` regardless.
- `render_report.py` rendered the audit_report to markdown without checking the artifact set.

After the flip (required mode, the new default):

- `validate_audit_report.py` returns `ok=False` when R1–R6 fails OR when any expected artifact isn't supplied.
- `render_report.py` accepts `--audit-dir <path>` and prepends an evidence-pinned marker as the first line of the rendered output. In required mode, refuses to render if the audit directory is missing any of the 4 canonical artifacts.
- `checkpoint.finalize_audit(slug)` is the pre-ship gate: validates the full artifact set against schemas + predicates before the audit hands off downstream. Raises `ValueError` in required mode when the set is incomplete or invalid.

## In-flight audits started before the flip

If you have an audit in `research/audits/<slug>/` that was started under the advisory regime and contains only the per-stage artifacts `01_claim_inventory.json` through `07_consistency.json` (plus `audit_report.json`, `findings.json`, `matrix.json`, `report.md`), it is missing the Phase 1+2 artifacts. You have three options:

### 1. Render with the escape hatch (recommended for one-off readbacks)

```bash
uv run python scripts/render_report.py \
  research/audits/<slug>/audit_report.json \
  --intake research/audits/<slug>/intake.json \
  --no-enforce-artifacts \
  --out research/audits/<slug>/report.md
```

`--no-enforce-artifacts` forces advisory mode for that single invocation and lets the render proceed without the artifact set. The rendered `report.md` will NOT carry the `<!-- audit_evidence_pinned ... -->` marker (since the artifact set wasn't supplied), so downstream consumers will fall back to whatever their no-marker path is.

> **Trap.** Combining `--no-enforce-artifacts` with `--audit-dir <dir>` lets the render emit the marker even when some files in `<dir>` are missing — the escape hatch suppresses the presence check, but the marker still advertises all 4 canonical filenames. Either supply the audit-dir flag only after all 4 artifacts exist, OR omit `--audit-dir` (no marker, no trap). The `--no-enforce-artifacts`-only form (no `--audit-dir`) is the safe migration default.

Equivalent for validation:

```bash
uv run python scripts/validate_audit_report.py \
  research/audits/<slug>/audit_report.json \
  --intake research/audits/<slug>/intake.json \
  --no-enforce-artifacts
```

### 2. Back-generate the artifact set (one-time bring-it-up-to-spec)

For audits worth keeping in the regression bed or that you want to re-validate under required mode without rerunning the LLM-driven Stage 1–2 prompts, back-generate the artifacts the same way the §Dry-run validation entry of `CONTRACTS.md` describes for audit 06:

1. Run `parse_document.py` on the audited source document → `document_inventory.json`.
2. Either run `extract_reference_map.py` (and inspect its output for parser gaps) OR manually write `reference_map.json` to mirror what the LLM would have patched at Stage 2 (paper_id-backfilled per citation).
3. Synthesize `resolved_sources.json` from any `source_meta.json` files referenced in the audit's `sources_consulted` or from cached Stage-2 records.
4. Initialize `external_evidence.json` with empty `entries[]` (the ledger is append-only; re-running Stages 2–4 will populate it). For audits whose findings carry `scite_context` / `pubtator3_entity_check` methods, you'll need the ledger entries that paired to those probes — those are not recoverable without re-running the API calls.

The four artifacts validate independently with `scripts/validate_artifact.py --kind <kind> --file <path>`. Once all four are in place, the audit becomes Phase-3-compliant and can be rendered + finalized in required mode.

### 3. Re-run Stages 1–2 from scratch

If you can't reconstruct the artifact set offline (e.g. the audit used live Scite/PubTator probes whose ledger entries are now lost), the cleanest path is to re-run Stages 1–2 of the audit. This produces all four artifacts as a side effect and the rest of the audit (Stages 3–7) can resume from `checkpoint.load_resume_state`.

## New audits after the flip

Every new audit MUST produce the full artifact set during Stages 1–2:

- `document_inventory.json` — Stage 1, via `parse_document.py` + LLM overrides.
- `reference_map.json` — Stage 1, via `extract_reference_map.py` + LLM patches; `paper_id` backfilled at Stage 2.
- `resolved_sources.json` — Stage 2, keyed on `paper_id` (DOI-preferred).
- `external_evidence.json` — Stage 2 onwards, append-only via `external_evidence.lookup_or_fetch`.

The audit cannot be finalized (`checkpoint.finalize_audit`) or rendered with the evidence-pinned marker without all four. `render_report --audit-dir <dir>` is the canonical Phase-3 invocation; the marker on the first line of `report.md` tells downstream skills (peer-review, scientific-writing) that the artifacts are present and they may switch to diff-mode against the artifact set.

## CI / regression bed

Existing regression runs against pre-flip audits in `regression/runs/baseline/` must use `--no-enforce-artifacts` until those baselines either gain the back-generated artifact set (per option 2 above) or are rerun under Phase 3. New regression entries (added after the flip) must produce the full artifact set. Plan §11.3 calls for new outcome columns in `regression/manifest.json` (`artifact_coverage`, `r_predicate_audit`); that work is out of scope for the Phase 3 flip and will land in a follow-up PR.

## Pointers

- Phase 3 implementation plan: `~/.claude/plans/let-s-put-together-a-mellow-bumblebee.md` §7 (user-scoped, outside the repo).
- In-repo evidence-pinning history: `EVIDENCE_PINNING_DECISIONS.md` (root).
- Dry-run + perturbation matrix proving the flip is safe: `references/CONTRACTS.md` §Dry-run validation.
- Render-side marker spec: `scripts/render_report.py::_build_marker` + the `<!-- audit_evidence_pinned ... -->` test cases in `tests/test_render_marker.py`.
- Pre-ship gate: `checkpoint.finalize_audit` (library-only; no CLI surface yet).
