# Stage 3 — Claim-citation alignment

**Purpose:** For each claim-citation pair, verify the cited source actually supports the claim attributed to it. This is where most LLM citation errors live: real paper, wrong claim.

## Routing

- **User-provided source:** extract relevant passage; exact-string match for direct quotes (delegate to `scripts/verify_exact_quote.py`); semantic match for paraphrased claims.
- **No source, abstract available via PubMed:** check whether abstract supports, contradicts, or is silent on the claim.
- **Biomedical pre-filter — PubTator3 entity co-mention check** (capability: `literature.entity_annotation`). Run BEFORE attempting full-text retrieval when the claim names structured entities (gene/drug/disease/variant) AND a cited PMID is available. Invoke `uv run python skills/shared/scripts/pubtator3.py annotations --pmids <cited_PMID> --summary`; the output is a per-PMID `entity_counts` tally. Outcomes:
  - **All claim entities present in tally** → proceed to PMC/Paperclip for sentence-level alignment.
  - **One or more claim entities absent from tally** → emit candidate verdict `MISATTRIBUTED` with `reason: entity_not_in_pubtator3_annotations` AND attempt one full-text confirmation via Paperclip before finalizing (PubTator3 NER has known gaps for newer papers; absence ≠ ground truth). If full text also lacks the entity, finalize as `MISATTRIBUTED`. If full text contains it, override to `VERIFIED`/`OVERGENERALIZED` per the alignment outcome and record the PubTator3 false-negative in `evidence[]` for downstream measurement.
  - **PubTator3 unreachable / wrapper error** → skip pre-filter silently and continue with the existing routing chain. No hard failure.
- **Need full text:** attempt PMC fetch; if open access, retrieve and search.
- **PMC fetch failed (paywall / 404), biomedical context:** attempt OA full-text retrieval via Paperclip — `paperclip lookup doi <DOI>` (preferred when DOI is known; saves a search call) or `paperclip search "<title>" -n 1`. If a hit lands in `/papers/<id>/`, read the relevant section files (`/papers/<id>/sections/`) or `paperclip grep "<claim phrase>" /papers/<id>/content.lines` for the alignment check. When the claim asserts multiple things about the same paper, prefer `paperclip scan /papers/<id>/content.lines "<phrase1>" "<phrase2>" ...` over sequential `grep` calls — one round-trip per paper instead of N. Record the citation URL `https://citations.gxl.ai/papers/<doc_id>#L<n1>-L<n2>` in the finding's `evidence[]`. Capability key: `verification.claim_alignment` (Paperclip fallback). Skip if cited paper is outside Paperclip's 8-source corpus (PMC + bioRxiv + medRxiv + arXiv + abstracts + FDA + trials + patents) or `paperclip --version` fails.
- **Figure-content claim (e.g., "Figure 2 shows downregulation of X"), biomedical context:** route to `paperclip ask-image /papers/<id>/figures/<file> "<question>"`. Use `--fn describe` for "what does the figure show" alignment checks and `--fn extract-data` for numerical claims read off the figure. Capability key: `verification.figure_content`. Record the citation URL with the figure path in `evidence[]`. Skip if Paperclip is absent or the cited paper has no `figures/` directory in `/papers/<id>/`.
- **Paperclip miss or unavailable, full text still required:** assign `UNVERIFIED` with `reason: paywalled_full_text`.
- **Citation context (sentiment fallback):** call `mcp__scite__search_literature` with `dois=[<DOI>]` + `term=<key claim phrase>` to retrieve sentiment-classified citing snippets. Use **supporting** snippets as evidence for `VERIFIED`; use **contrasting** snippets as evidence for `CONTRADICTED` or `OVERGENERALIZED`. Capability key: `verification.claim_alignment` (Scite fallback — lower priority than Paperclip OA full text because snippets are 3-sentence and sentiment-biased). The `result_summary` and any sentiment-attributed claim in the report **MUST** be tagged "per Scite classification" — Scite has documented bias toward 'mentioning' classification (see `tool-lookup.yaml` `literature.citation_context` notes).
- **OpenAlex citation-network backstop** (capability key: `verification.claim_alignment` — last fallback, used only when Scite returns empty for a DOI). Call `mcp__openalex__get_citation_network` with the cited Work ID to surface citing/cited works that may anchor the claim. OpenAlex citation context is **unsentenced** (no supporting/contrasting/mentioning classification); it cannot drive `VERIFIED` vs `CONTRADICTED` on its own. Use only as supporting context for `OVERGENERALIZED` (when the citing-paper-density around the claim is sparse) or as evidence chain documentation when full text is unavailable. The `result_summary` MUST be tagged "unsentenced citation context (per OpenAlex)" to distinguish from Scite's classified snippets. If both Scite and OpenAlex return empty AND no full text is available, the verdict is `UNVERIFIED` with `reason: paywalled_full_text` or `tier_does_not_cover` — never `CONTRADICTED` from absence alone.
- **Cited source is a web URL** (no DOI/PMID/PMCID exists — citation is to a regulatory letter, registry page, society proceedings, or preregistration; e.g., `[12] FDA approval letter, https://www.fda.gov/...`): Paperclip and Scite cannot anchor the claim because there's no DOI to feed them. Fetch the page via `mcp__exa__web_fetch_exa` (or `mcp__exa__web_search_exa` first if only a partial URL is given) and align the claim against the page contents — exact-string for direct quotes, semantic for paraphrased claims. The URL MUST be on the citable-web-domain whitelist (`skills/shared/references/citable_web_domains.md`); W1 grounds `VERIFIED` directly, W2/W3a ground with the tier-specific `result_summary` tag, W3b is context-only (verdict `UNVERIFIED` with `reason: web_evidence_uncitable_tier`, never `VERIFIED`). Out-of-whitelist URLs → `UNVERIFIED` with the same reason. Record `fetched_at` (ISO-8601) and the resolved URL in `evidence[]`. Such Stage-3 `VERIFIED` claims are subject to the P8 web-source carve-out in Stage 4. Capability key: `verification.semantic_web_search`.
- **Claim too specific for abstract-only check and full text unavailable:** `UNVERIFIED`, **MUST NOT** flag as `CONTRADICTED`.

## Verdict assignments

| Condition | Verdict |
|---|---|
| Source clearly supports the claim | `VERIFIED` |
| Source supports a weaker / narrower version | `OVERGENERALIZED` |
| Source explicitly contradicts the claim | `CONTRADICTED` |
| Source does not address the claim | `MISATTRIBUTED` |
| Access blocked | `UNVERIFIED` with `reason` |

See [`../CONTRACTS.md`](../CONTRACTS.md) for canonical verdict definitions.

## Logic-failure subtypes (map to existing verdicts)

These distinguish *how to repair* a flagged claim — no new vocabulary:

- **Correlation presented as causation** — premise cite is correct but claim language asserts causality the source does not support → `OVERGENERALIZED` if a weaker associative version is supported, otherwise `CONTRADICTED`. Recommended action: soften causal language (e.g., "drives" / "causes" → "is associated with").
- **Overgeneralization** — narrow finding extrapolated to a broader population, setting, or time window → `OVERGENERALIZED`.
- **Non-sequitur** — premises true and individually verifiable, but the conclusion does not follow from them → `MISATTRIBUTED` if the cited source is silent on the conclusion, or `UNSUPPORTED` if no source at all connects premises to conclusion.

Cherry-picking — where the cite-claim pair itself is verified but the document selectively suppressed contradicting literature — is **not** a Stage 3 concern (the cited source genuinely supports the claim) and is handled in [Stage 4](./stage_4_uncited.md).

## Route PubTator3 entity-check through the external-evidence ledger

The pre-filter call described above (`pubtator3.py annotations --pmids <PMID>`) MUST be routed through `scripts/external_evidence.lookup_or_fetch(ledger_path, tool="pubtator3", method="pubtator3_entity_check", query_params={"pmid": <PMID>}, paper_id=<paper_id>, fetcher, freshness_days=None)`. The 7-day TTL (`thresholds.ARTIFACT_FRESHNESS_DAYS["pubtator3"]`) reuses the entity tally across findings that cite the same paper.

The `verification_path[]` entry retains its existing shape (`method: "pubtator3_entity_check"`, `tool: "pubtator3"`, `result_summary: <entity_tally_digest>`). R5 (validate_audit_report.py) cross-checks that this step has a matching ledger entry — a missing entry indicates the entity tally was fabricated.

## On stage completion

Persist via `checkpoint.py write --stage 3` (same shape as Stage 2).

**Artifact:** `research/audits/<slug>/03_alignment.json`.
