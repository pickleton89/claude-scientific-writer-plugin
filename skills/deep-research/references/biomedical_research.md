# Biomedical Research Reference

Reference document for deep-research agents operating on biomedical topics. Contains
MCP tool mappings, evidence grading bridge, collision filter protocol, and the
dossier-first principle.

## Biomedical Activation Gate

Activate biomedical-specific protocols when the research topic contains any of:
- Gene symbols (EGFR, BRCA2, TP53, etc.)
- Protein names (kinase, receptor, enzyme, etc.)
- Drug names (imatinib, pembrolizumab, etc.)
- Disease terms (cancer, Alzheimer's, diabetes, etc.)
- Pathway names (MAPK, PI3K/AKT, Wnt, etc.)
- Clinical intervention terms (therapy, treatment, clinical trial, etc.)

When activated:
1. Check for entity-resolution identity table in conversation context
2. Check for upstream target-intelligence or drug-intelligence dossier
3. Apply MCP tool preferences (PubMed primary, ToolUniverse fallback)
4. Use T1-T4 evidence grading alongside Level I-VII hierarchy

## MCP Tool Preference Hierarchy

The 3-tier preference system from `tool-lookup.yaml`:

### Tier 1: Primary MCP Servers (use first)

| Function | MCP Server | Tool | Notes |
|----------|-----------|------|-------|
| Literature search | PubMed MCP | `search_articles` | MeSH vocabulary, clinical trials, high-quality biomedical indexing |
| Article metadata | PubMed MCP | `get_article_metadata` | DOI verification, full metadata |
| Related articles | PubMed MCP | `find_related_articles` | Citation network expansion |
| Full text | PubMed MCP | `get_full_text_article` | PMC open access only |
| Preprint + full-text search | Paperclip CLI | `paperclip search` | Full-text across 8-source corpus: PMC + bioRxiv + medRxiv + arXiv + abstracts + FDA + clinical trials + patents. Replaces the retired bioRxiv MCP. |
| Cross-domain search | Consensus MCP | `search` | AI-synthesized evidence across papers |
| Citation context | Scite MCP | `search_literature` | Smart Citations: supporting/contrasting/mentioning classification |
| Citation tallies | Scite MCP | `search_literature` | Per-paper reception breakdown + Scite Index (USI) + editorial notices |
| Corpus map/reduce | Paperclip CLI | `paperclip map` / `paperclip reduce` | Per-paper LLM reader; recommended at 3–10 papers; `m_xxx` map handles |
| Corpus regex | Paperclip CLI | `paperclip grep` | Sub-second corpus-wide regex; pipes only (no `for`/`while`/`xargs`) |
| Corpus metadata SQL | Paperclip CLI | `paperclip sql` | Read-only SQL over the documents table (200-row cap) — filter by author/journal/year/source pre-search. |
| Figure VLM | Paperclip CLI | `paperclip ask-image` | VLM analysis of paper figures (`--fn describe` / `--fn extract-data`); no PDF download required. |
| Target-disease | Open Targets MCP | `query_open_targets_graphql` | Disease associations, druggability |
| Entity search | Open Targets MCP | `search_entities` | Target/disease/drug lookup |

**Paperclip caveats:** Invoked via Bash, not MCP. Requires `paperclip install` + `paperclip login`
(per machine; vendor SKILL.md auto-installed at `.claude/skills/paperclip/SKILL.md`). The 8-source
corpus does NOT cover full MEDLINE — PubMed MCP remains the primary metadata source. The bioRxiv
index inside Paperclip may trail the direct bioRxiv API by hours; for preprint-heavy domains this
is an accepted trade-off (v1.7.0). Skip Paperclip silently when the binary is absent (CI /
sandboxed environments). Capability keys: `literature.corpus_search`, `literature.corpus_grep`,
`literature.corpus_metadata`, `verification.figure_content`.

### Tier 2: ToolUniverse (fallback, via `grep_tools` → `execute_tool`)

| Capability Key | Tool Name | Use When |
|---------------|-----------|----------|
| `literature.search` | `EuropePMC_search_articles` | PubMed MCP unavailable |
| `literature.citations` | `EuropePMC_get_citations` | Citation network traversal |
| `literature.full_text_snippets` | `EuropePMC_get_fulltext_snippets` | Bounded full-text snippets (needs PMCID) |
| `literature.full_text_snippets` | `SemanticScholar_get_pdf_snippets` | PDF-based snippets (needs pdf_url) |
| `literature.recommendations` | `SemanticScholar_search_recommendations` | Related paper suggestions |
| `interactions.ppi` | STRING tools | Protein-protein interactions |
| `interactions.go_annotations` | GO annotation tools | Gene function annotations |
| `interactions.pathways` | Reactome/KEGG tools | Pathway membership |
| `expression.tissue` | GTEx tools | Tissue-specific expression |
| `genetic_variation.population` | gnomAD tools | Population frequency, constraint (pLI, LOEUF) |
| `enrichment.go_pathway_enrichment` | gProfiler, enrichr | Pathway enrichment analysis |

### Tier 3: Zotero (user's reference library)

| Function | MCP Server | Tool |
|----------|-----------|------|
| Library search | Zotero MCP | `zotero_search_items` |
| Item metadata | Zotero MCP | `zotero_get_item_metadata` |
| Collection browse | Zotero MCP | `zotero_get_collection_items` |

## Evidence Grading Bridge: Level I-VII ↔ T1-T4

See `references/evidence_hierarchy.md` for the full mapping table. Quick reference:

| Study Design Evidence (Level) | Biomedical Claim Evidence (Tier) |
|-------------------------------|----------------------------------|
| I: Systematic review / meta-analysis | T1: Mechanistic/Direct |
| II: Randomized controlled trial | T1: Mechanistic/Direct |
| III: Controlled non-randomized | T2: Functional |
| IV: Case-control / cohort | T2: Functional |
| V: Descriptive review | T3: Association |
| VI: Single descriptive study | T3: Association |
| VII: Expert opinion / editorial | T4: Mention/Review |

Both systems are used: Level I-VII grades the study design quality; T1-T4 grades
the strength of a specific biomedical claim. A Level II study (RCT) may contain
both T1 claims (primary endpoints) and T3 claims (post-hoc correlations).

## Collision-Aware Search Protocol

When entity-resolution reports HIGH collision risk for an entity:

1. Import the negative filter string from the identity table
2. Append to all search queries for that entity
3. Document the filter in the search log

**Example:**
```
Entity: ACE (collision risk: HIGH, 72% off-topic)
Negative filters: NOT poker NOT hardware NOT aviation NOT "ACE inhibitor"
Query: "(ACE gene OR ACE2) AND cardiovascular NOT poker NOT hardware NOT aviation"
```

When collision risk is LOW: use entity name directly, no filters needed.

## Dossier-First Principle

When an upstream dossier exists in the conversation context (from target-intelligence
or drug-intelligence), the synthesis agent MUST:

1. Extract structured data from the dossier FIRST
2. Use dossier data to ground synthesis:
   - GO annotations → functional context
   - PPI data (STRING) → interaction network
   - Expression data (GTEx) → tissue-specific relevance
   - Druggability assessment → therapeutic context
   - Disease associations (Open Targets) → clinical relevance
3. Only query ToolUniverse for data NOT already in the dossier
4. Cross-reference literature claims against dossier data:
   - Literature claims PPI → verify against STRING score in dossier
   - Literature claims expression → verify against GTEx TPM in dossier
   - Flag discrepancies between literature and database records

## Database-Specific Search Notes

### PubMed MCP
- Supports MeSH controlled vocabulary (e.g., `"EGFR"[MeSH]`) and the full
  PubMed field-tag surface — for the complete table (`[MeSH]`, `[tiab]`,
  `[mh]`, `[pt]`, `[dp]`, `[au]`, `[Substance Name]`, `[MeSH Major Topic]`,
  etc.) plus Boolean precedence, phrase searching, wildcards, and proximity
  operators, see `scripts/sources/pubmed/references/search_syntax.md`. For
  domain-specific Boolean templates, see
  `scripts/sources/pubmed/references/common_queries.md`.
- Publication type filters: Review, Clinical Trial, Meta-Analysis
- Use `find_related_articles` for citation network expansion
- Known issue: occasional transient session expiry — retry once

### Paperclip CLI (preprint + full-text channel)
- Replaces the retired bioRxiv MCP (v1.7.0). Use `paperclip search -s biorxiv "<query>"` or
  `paperclip search -s medrxiv "<query>"` for preprint-only restriction; omit `-s` for the
  full 8-source corpus (PMC + bioRxiv + medRxiv + arXiv + abstracts + FDA + trials + patents).
- Preprints are NOT peer-reviewed — always note this in evidence grading.
- `--since 30d` / `--since 7d` for recent-bias scans (replaces "latest developments" recipes).
- `paperclip lookup doi <DOI>` is the canonical re-verification path when an identifier is known.
- Pair with `paperclip map --from <s_id>` (3–10 papers) for synthesis; `paperclip reduce
  --from <m_id> --strategy {summarize|table|themes|consensus|bullet_points|extract}` for
  cross-paper aggregation.
- See `skills/shared/references/paperclip_stateful_workflow.md` for s_id/m_id reuse patterns.

### Consensus MCP
- Best for "what does the literature say about X?" synthesis queries
- Returns structured results with paper URLs — always include these
- Rate limit: batch at most 3 search calls at a time
- Must include sign-up/upgrade message from tool result verbatim at end of response

### Scite MCP
- Single tool: `search_literature` (mcp__scite__search_literature) — behavior changes by parameters
- **Tallies:** Call with `dois: [DOI]`, no `term` — returns citation counts + Scite Index + editorial notices
- **Citation context:** Call with `dois: [DOI]` + `term` — returns citing paper snippets matching the term
- **Full-text search:** Call with `term` only — searches across ~50M indexed full-text articles
- Scite Index (USI) = supporting / (supporting + contrasting); range 0.0-1.0
- `editorialNotices` field flags retractions, corrections, expressions of concern
- 25+ filters: author, journal, topic, affiliation, date range, publication type, citation count ranges
- Accuracy caveat: classification biased toward "mentioning" per independent evaluation
- Requires Premium subscription; MCP launched Feb 2026

### ToolUniverse
- Runs in compact mode: 5 meta-tools (`grep_tools`, `execute_tool`, `find_tools`, `get_tool_info`, `list_tools`)
- Discover tools: `grep_tools` with keyword → get tool name → `execute_tool`
- Known parameter corrections documented in `shared/references/known_param_corrections.md`
- FAERS: parameter is `medicinalproduct` (not drug_name)
- ADMET-AI: SMILES must be list `["SMILES"]` not bare string

## Post-Search Enrichment

After the bibliography is assembled, optionally enrich with reception data:

| Tool | When to Apply | What It Adds |
|------|--------------|--------------|
| Scite tallies (`search_literature` with `dois`, no `term`) | FULL, LIT-REVIEW, SYSTEMATIC-REVIEW, HYPOTHESIS modes | Supporting/contrasting/mentioning counts per paper + Scite Index |
| Scite citation context (`search_literature` with `dois` + `term`) | When a paper has high contrasting count | Snippets from contradicting papers for claim assessment |

Skip for QUICK and FACT-CHECK modes (speed priority).

**Accuracy caveat:** Scite classification accuracy is contested (independent evaluation found bias
toward "mentioning"). Report reception data as "per Scite classification."

**No fallback:** If Scite is unavailable, reception data is simply omitted. No other tool provides
citation sentiment classification. This is acceptable because reception assessment is an enrichment
layer, not a core requirement.

## Currency Rules by Field

| Field | "Recent" threshold | "Current" threshold |
|-------|-------------------|---------------------|
| Biomedical | ≤5 years | ≤1 year |
| ML/Genomics | ≤2 years | ≤6 months |
| Drug development | ≤5 years | ≤2 years |
| Clinical practice | ≤5 years | ≤2 years |
| Structural biology | ≤10 years | ≤3 years |
| Seminal/foundational works | Exempt | Exempt |
