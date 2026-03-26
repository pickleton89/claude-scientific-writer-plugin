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
| Preprint search | bioRxiv MCP | `search_preprints` | Biology + medical preprints |
| Preprint details | bioRxiv MCP | `get_preprint` | DOI-based retrieval |
| Cross-domain search | Consensus MCP | `search` | AI-synthesized evidence across papers |
| Target-disease | Open Targets MCP | `query_open_targets_graphql` | Disease associations, druggability |
| Entity search | Open Targets MCP | `search_entities` | Target/disease/drug lookup |

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
- Supports MeSH terms: `"EGFR"[MeSH]` for controlled vocabulary
- Publication type filters: Review, Clinical Trial, Meta-Analysis
- Use `find_related_articles` for citation network expansion
- Known issue: occasional transient session expiry — retry once

### bioRxiv MCP
- Preprints are NOT peer-reviewed — always note this in evidence grading
- `server` parameter: "biorxiv" for biology, "medrxiv" for clinical
- Use `search_published_preprints` to check if a preprint has been formally published

### Consensus MCP
- Best for "what does the literature say about X?" synthesis queries
- Returns structured results with paper URLs — always include these
- Rate limit: batch at most 3 search calls at a time
- Must include sign-up/upgrade message from tool result verbatim at end of response

### ToolUniverse
- Runs in compact mode: 5 meta-tools (`grep_tools`, `execute_tool`, `find_tools`, `get_tool_info`, `list_tools`)
- Discover tools: `grep_tools` with keyword → get tool name → `execute_tool`
- Known parameter corrections documented in `shared/references/known_param_corrections.md`
- FAERS: parameter is `medicinalproduct` (not drug_name)
- ADMET-AI: SMILES must be list `["SMILES"]` not bare string

## Currency Rules by Field

| Field | "Recent" threshold | "Current" threshold |
|-------|-------------------|---------------------|
| Biomedical | ≤5 years | ≤1 year |
| ML/Genomics | ≤2 years | ≤6 months |
| Drug development | ≤5 years | ≤2 years |
| Clinical practice | ≤5 years | ≤2 years |
| Structural biology | ≤10 years | ≤3 years |
| Seminal/foundational works | Exempt | Exempt |
