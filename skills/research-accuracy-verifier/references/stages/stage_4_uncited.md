# Stage 4 — Uncited claim verification

**Purpose:** For substantive uncited claims (depth permitting), search for support. Also enforces the **P8 cherry-picking sweep** over Stage-3 VERIFIED claims for Tier-3 biomedical/mixed audits.

**Predicate enforced:** P8 (Tier-3 cherry-picking sweep — see [`../predicates.md`](../predicates.md)).

## Routing

- **Biomedical:** PubMed → bioRxiv (preprints) → PubTator3 (entity-grounded literature when claim names genes/diseases/chemicals/variants) → Open Targets (target / disease / drug claims) → Consensus (paper discovery; full-text-indexed) → Scite (citation context) → `mcp__exa__web_search_exa` (grey-lit / regulatory / registry pages on the citable-web-domain whitelist; capability key `verification.semantic_web_search`).
- **General scientific:** Crossref / OpenAlex → `mcp__exa__web_search_exa` (semantic web search; capability key `verification.semantic_web_search`) → `WebSearch` (deeper fallback when Exa returns empty).

## Web-evidence routing rules

These rules apply globally — Stages 2, 3, 4, 5 — wherever web evidence enters the audit. Documented here under Stage 4 for proximity to the routing tiers above.

- Web URLs MUST be on the citable-web-domain whitelist at `skills/shared/references/citable_web_domains.md`. **W1** (regulatory / registries) grounds `VERIFIED` directly; **W2** (societies / repositories) grounds `VERIFIED` with `result_summary` tag `per society/repository source`; **W3a** (`*.edu`) is treated like W2 with tag `per institutional source`; **W3b** (curated journalism — Nature/Science/NEJM/Lancet/BMJ news, `statnews.com`, `endpts.com`) is **context-only** and CANNOT ground `VERIFIED` on its own — it can only support `UNVERIFIED` (`reason: web_evidence_uncitable_tier`) or `OVERGENERALIZED`.
- Out-of-whitelist URLs cannot ground any verdict in the matrix; they may appear in `verification_path[]` as documentary trail but the `verdict` MUST NOT be `VERIFIED`.
- Every web `verification_path[]` entry MUST capture `fetched_at` (ISO-8601) and a resolvable URL in `result_summary` — C4 (cross-reference integrity, CRITICAL — see `../../../scientific-writing/references/citation_styles.md` § *Citation Integrity Rules (TWS C1–C5)*) requires URL resolvability at audit time.
- A web `verification_path[]` entry with `method == "web_search"` MUST include the literal token `no_doi` in `result_summary` when used to satisfy P7 (Stage 2). See the P7 web-source carve-out in [`./stage_2_citation_existence.md`](./stage_2_citation_existence.md).

Capability keys: `verification.citation_existence`, `verification.claim_alignment`, `verification.semantic_web_search`. The LLM invokes the corresponding MCP tools (PubMed, Scite, Exa, etc.) directly per the call patterns documented in `tool-lookup.yaml`, and records each call as a `verification_path[]` entry.

## Verdict assignments

Same as [Stage 3](./stage_3_alignment.md).

## Cherry-picking detection (P8 — validator-enforced)

Tier 3 biomedical/mixed audits, and custom audits with `uncited_claims` enabled. For every already-`VERIFIED` cite-claim pair emitted by Stage 3 in the `verification_matrix[]`, sweep Scite for tally-based contested-consensus detection. Two valid outcomes per Stage-3 VERIFIED claim:

### 1. Cherry-picking finding emitted

Call `mcp__scite__search_literature` with `dois=[<cited DOI>]` (no `term`) to fetch the citation tally — **routed through the external-evidence ledger**. Wrap the call as `external_evidence.lookup_or_fetch(ledger_path, tool="scite", method="scite_context", query_params={"doi": <DOI>}, paper_id=<paper_id>, fetcher, freshness_days=None)`. Within the 7-day Scite TTL, the Stage-2 `editorialNotices` probe entry for this paper_id and the Stage-4 cherry-picking tally entry **share the same ledger row** when their `query_params` canonicalize identically — this is the headline memoization payoff: the Tier-3 sweep adds no incremental Scite API calls beyond what Stage 2 already issued. For this to work, the Stage-2 fetcher MUST emit a structured digest containing both `editorialNotices` AND the citation tally (`supporting` / `contrasting` / `mentioning`) so Stage 4 can extract USI from a cache hit — see [`stage_2_citation_existence.md`](./stage_2_citation_existence.md) §Digest convention. Compute `USI = supporting / (supporting + contrasting)`. If `USI < 0.5` (matches deep-research's `[CONTESTED]` threshold), emit a Stage-4 finding with:

- `verdict == "OVERGENERALIZED"`
- `verification_path[]` containing at least one `method == "scite_context"` entry
- `result_summary` containing **both**:
  - the literal tag `cherry_picking:<claim_id>` — where `<claim_id>` exactly matches the `verification_matrix[].claim_id` of the Stage-3 VERIFIED claim this finding covers
  - the literal pattern `USI=<value>` plus supporting/contrasting counts

The tag is what lets `validate_audit_report.py` pair the Stage-4 finding with its originating Stage-3 claim. The "claim" being overgeneralized is the implicit consensus framing, not the narrow cite-claim pair (which remains `VERIFIED` in the matrix). Tag the `result_summary` "per Scite classification". Recommended action: add a contrasting citation or scope-limit the claim.

### 2. Caveat in lieu of finding

When the Scite tally cannot be computed (DOI not indexed by Scite, API failure, USI ≥ 0.5 so no `OVERGENERALIZED` is warranted), the Stage-3 VERIFIED claim MUST still be accounted for via a `header.coverage_caveats[]` entry of structured shape:

```
cherry_picking:<claim_id>: <reason>
```

The `<claim_id>` MUST exactly match the `verification_matrix[].claim_id`. The `<reason>` is free-form text but should name the actual outcome (`scite_doi_not_indexed`, `api_timeout`, `tally_uncontested_USI=0.83`, `tally_empty`, etc.). The `cherry_picking:` prefix is parsed by `validate_audit_report.py` / `render_report.py`.

### 3. Web-sourced VERIFIED claims carve-out

Stage-3 `VERIFIED` claims grounded in web evidence (no DOI) cannot be swept via Scite tally — there's no DOI to compute USI against. They MUST still be covered via the caveat path: emit a `header.coverage_caveats[]` entry of canonical shape:

```
cherry_picking:<claim_id>: web_source_no_doi_for_scite_tally
```

The reason token `web_source_no_doi_for_scite_tally` signals the carve-out explicitly; `validate_audit_report._caveat_covers_claim` already parses the `cherry_picking:<claim_id>: <reason>` prefix without modification — but the Stage 4 emit logic MUST produce the caveat. Out-of-whitelist web URLs would not have reached `VERIFIED` in Stage 3, so any Stage-3 `VERIFIED` web claim reaching Stage 4 is already a W1/W2/W3a hit.

### P8 violation condition

Silence — a Stage-3 VERIFIED claim with no matching cherry-picking finding **and** no `cherry_picking:<claim_id>:` caveat (Scite-based or web-source carve-out) — is a **P8 violation**. The audit cannot be rendered: `render_report.generate_report()` invokes `validate_audit_report.run_p8(...)` and raises on failure. Capability key: `verification.cherry_picking`.

## On stage completion

Persist via `checkpoint.py write --stage 4`.

**Artifact:** `research/audits/<slug>/04_uncited.json`.
