# Stage 6 — Numerical and named-entity sanity checks

**Purpose:** Verify numerical claims (p-values, sample sizes, doses, kinetics, dates) and named entities (gene/protein symbols, drug names, cell lines, mouse strains, antibody clones) against canonical sources.

## Cooperation with `research-paper-summarizer`

When the document under audit cites a paper that has already been summarized by `research-paper-summarizer`, the per-paper `{stem}_stats.json` file (schema: [`../../../research-paper-summarizer/schemas/stats.json`](../../../research-paper-summarizer/schemas/stats.json)) is the canonical numerical record for that **cited** paper. The handoff is explicit:

1. **Caller populates `intake.cited_papers[]`** (schema: `../../schemas/intake.json#/properties/cited_papers`) by lifting each upstream summarizer's fork-return `summary_paths.{stats,source_meta}` into a `{paper_id, stats_path, source_meta_path[, doi, pmid, pmcid]}` entry. This is the only formal way the verifier learns where stats files live — there is no path scan or heuristic discovery.
2. **Stage 6 iterates `cited_papers[]`** in the order presented. For each entry: `!\`cat <stats_path>\`` to load it, `!\`uv run python ../research-paper-summarizer/scripts/validate_stats.py <stats_path>\`` to confirm Q5/R5 compliance (skip the entry on non-zero exit and log `header.coverage_caveats[]`), then join the document's numerical claims to the loaded stats by matching `paper_id` and value/unit/context.
3. **Emit `evidence` entries** that pin to `paper_id` + `claim_id` from `stats.json`. Verdict assignment follows the standard enum: matching number → `VERIFIED`; conflicting number → `CONTRADICTED`; missing from stats but plausible → `UNVERIFIED`.

**Fallback:** when `cited_papers[]` is absent from intake, or an entry's `validate_stats.py` fails, Stage 6 falls back to full-text re-extraction from the cited paper (Paperclip / PMC). The cooperation eliminates 10–30k tokens per cited paper and prevents verdict drift from independently re-derived numbers. (This cooperation applies to **cited sources** only — number sanity within the document under audit itself still uses the heuristics below.)

## Numerical claims

Use `scripts/check_journal_volume.py` and number sanity heuristics:

- p-values with implausible precision (≥4 decimal places) or non-standard formatting
- effect sizes outside biologically plausible ranges
- sample sizes inconsistent with described study design or stats
- dates that conflict with cited paper publication years
- **anachronistic temporal claims** — explicit recency phrases ("as of last year", "current data", "recent studies") anchored to a year that no longer qualifies as recent (≥18 months before `date_checked`) → `OVERGENERALIZED` (the claim asserts currency the source does not support). Per matrix, MAJOR for grant / manuscript / lit_review. Recommended action: replace the recency phrase with an explicit cutoff date.
- **anachronistic evidence base** (no specific recency claim, but the latest cited reference year lags `date_checked` by ≥18 months in a fast-moving field) → emit a `header.coverage_caveats[]` entry rather than a `findings[]` entry; this is a coverage gap, not a misstatement. Recommended action: refresh the evidence base or scope-limit the document.

## Named entities

Delegate to `scripts/resolve_entity.py` (which delegates to the `entity-resolution` skill):

- **Gene / protein symbols:** verify official symbol via HGNC / UniProt; flag aliases that may obscure entity confusion
- **Drug names:** verify generic ↔ brand correspondence
- **Cell lines:** cross-check Cellosaurus; flag known misidentified or contaminated lines
- **Mouse strains:** verify against official Jackson Laboratory or Charles River nomenclature
- **Antibody clones:** flag claims requiring validation when no clone or RRID is given

## Verdict assignments

`VERIFIED | METADATA_MISMATCH | CONTRADICTED | MISATTRIBUTED | UNVERIFIED` — no separate vocabulary. See [`../CONTRACTS.md`](../CONTRACTS.md).

## On stage completion

Persist via `checkpoint.py write --stage 6`.

**Artifact:** `research/audits/<slug>/06_sanity.json`.
