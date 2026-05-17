# Stage 7 — Internal consistency

**Purpose:** Cross-check the document against itself. Stage 7 work is largely deterministic and is delegated to scripts.

## Delegated checks

- `scripts/reconcile_references.py` — bibliography ↔ inline citation set diff (orphan refs, missing inline)
- `scripts/scan_acronyms.py` — acronym defined-before-first-use, expansion drift

## LLM adjudication scope

The LLM still adjudicates:

- The same fact stated with different numbers in different sections → `CONTRADICTED`
- Discussion claims not supported by results presented → `UNSUPPORTED` or `OVERGENERALIZED`
- Definitions that drift across sections → `METADATA_MISMATCH`
- Author / year mismatches between inline citations and bibliography → `METADATA_MISMATCH`

## Verdict assignments

`CONTRADICTED | UNSUPPORTED | OVERGENERALIZED | METADATA_MISMATCH` — no separate vocabulary. See [`../CONTRACTS.md`](../CONTRACTS.md).

## On stage completion

Persist via `checkpoint.py write --stage 7`.

**Artifact:** `research/audits/<slug>/07_consistency.json`.
