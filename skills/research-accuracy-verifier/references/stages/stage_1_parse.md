# Stage 1 — Document parsing and claim extraction

**Purpose:** Build a `ClaimInventory` validated against [`schemas/claim_inventory.json`](../../schemas/claim_inventory.json).

For each item record `id`, `location {section, paragraph, line}`, `claim_text` (verbatim), `claim_type`, and `citations[]`.

**Claim type categories:**

- **citation_bearing** — any sentence with an inline citation, footnote, or reference marker
- **direct_quote** — text inside quotation marks attributed to a person or source
- **numerical** — percentages, p-values, sample sizes, effect sizes, doses, kinetic parameters (Kd, IC50, EC50), sequence lengths, gene / protein counts, dates
- **named_entity** — gene / protein symbols, drug names (generic and brand), cell lines, antibody clones, mouse strains, instrument models, software versions
- **mechanistic** — causal or mechanistic statements ("X activates Y", "mutation in A causes B")
- **attribution** — "Smith et al. showed…", "the Anderson lab demonstrated…"
- **uncited** — empirical statements with no citation

**Bipartite map:** build a claim ↔ citation map — each claim links to zero, one, or many citations; each citation links to all claims it nominally supports.

**On stage completion:** call `checkpoint.py write --slug <slug> --stage 1 --claim-inventory <path> --document-type <type>` to persist the inventory.

**Artifact:** `research/audits/<slug>/claim_inventory.json`.

## Emit pinned artifacts (Phase 1+)

In addition to `claim_inventory.json`, Stage 1 emits two pinned-artifact siblings that downstream stages (and the R-predicate cross-artifact gate) read from disk rather than reconstructing from conversation context.

### `document_inventory.json` — hybrid parser baseline + LLM overrides

1. Invoke `scripts/parse_document.py --document DOC --slug <slug> --document-type <type> --output document_inventory.json`. The script produces the deterministic baseline: sections, paragraphs, char/line offsets, and a SHA-256 of the normalized document content.
2. Read the baseline `document_inventory.json` alongside the original `<document>` text. If the parser missed a section boundary, paragraph break, or section name, append an entry to `overrides[]`. Do NOT edit `sections[]` or `paragraphs[]` directly — overrides preserve diff auditability.
3. Override shape: `{kind, path, before, after, reason}` where `kind ∈ {section_name, section_boundary, paragraph_boundary}` and `path` is a JSON-pointer-like address (e.g., `sections[2].name`). Every override MUST resolve at validate-time (predicate D3).
4. Validate via `scripts/validate_artifact.py --kind document_inventory --file PATH`.

Downstream stages address paragraphs via `parse_document.resolve_location(inventory, section_id, paragraph_id)` which transparently applies overrides on top of the baseline.

### `reference_map.json` — citation occurrences + bibliography keys

1. Invoke `scripts/extract_reference_map.py --document DOC --inventory document_inventory.json --slug <slug> --sources-available <intake.sources_available> [--bibliography PATH] --output reference_map.json`. The script sweeps numeric brackets, `\cite{}` commands, and author-year forms; records each occurrence with `(section_id, paragraph_id, line)`.
2. Every `citations[].paper_id` is `null` at Stage 1 — Stage 2 (citation existence) backfills these via `extract_reference_map.update_paper_ids()` after identifier resolution.
3. `bibliography_orphans[]` is populated by the script: bib entries with zero inline occurrences. Used by Stage 7 internal consistency.
4. Validate via `scripts/validate_artifact.py --kind reference_map --file PATH`.

Both artifacts are validator-required (advisory mode in Phase 1; required in Phase 3) — see [`../predicates.md`](../predicates.md) §R1, R3, R4, R6 and [`../../scripts/thresholds.py`](../../scripts/thresholds.py) `ARTIFACT_SPECS_BY_TIER`.
