# Phase 1 Completion Report — ToolUniverse Integration

> **Date:** 2026-03-01
> **Status:** Complete
> **Phase:** 1 of 5 (Foundation)

---

## Summary

Phase 1 established the foundation for ToolUniverse integration: MCP server installed, capability mapping created, entity-resolution skill written and tested against 4 real-world cases spanning all entity types. The primary tier (Open Targets + PubMed) handles entity resolution well for most cases; ToolUniverse will add chemical structure data and fill cross-reference gaps.

---

## 1. MCP Installation

| Item | Status |
|------|--------|
| ToolUniverse MCP server | Configured via `claude mcp add tooluniverse -- uvx --refresh tooluniverse` |
| Package | `tooluniverse` v1.0.22 (PyPI), launched via `uvx` |
| Scope | Project-local (claude-scientific-writer-plugin) |
| Compact mode | Default — 5 meta-tools (`list_tools`, `grep_tools`, `get_tool_info`, `execute_tool`, `find_tools`) |
| API keys | None configured (most tools work without keys) |
| Session activation | Requires Claude Code restart (configured but not yet live) |

**Action needed:** Restart session to activate, then verify meta-tools respond.

---

## 2. Tool Availability Audit

Full audit at: `skills/shared/references/tool_availability_audit.md`

**Primary tier (verified active):**
- Open Targets: `search_entities`, `query_open_targets_graphql` — fully functional
- PubMed: `search_articles`, `get_article_metadata`, `get_full_text_article`, `find_related_articles` — fully functional
- Consensus: `search` — fully functional

**ToolUniverse tier (pending verification after restart):**
- 6 high-priority tools (entity resolution): `mygene_query`, `ensembl_lookup_gene`, `chembl_molecule_search`, `pubchem_cid_lookup`, `uniprot_search`, `uniprot_id_mapping`
- 10 medium-priority tools (target/drug intelligence)
- 10 lower-priority tools (drug data, predictions, literature)

**Shared references created:**
- `skills/shared/tool-lookup.yaml` — 215-line capability-to-tool mapping with 3-tier preference (primary → tooluniverse → fallback)
- `skills/shared/references/known_param_corrections.md` — documented API quirks for 10+ tools
- `skills/shared/references/evidence_grading.md` — T1-T4 evidence grading framework
- `skills/shared/references/tool_availability_audit.md` — tool verification checklist

---

## 3. Entity Resolution Test Results

### Test Matrix

| Test Case | Entity Type | Primary ID | Cross-Refs | Collision Risk | Off-Topic Rate | Verdict |
|-----------|-------------|-----------|------------|---------------|----------------|---------|
| **BRCA2** | Gene/protein | ENSG00000139618 | 4 (Ensembl, UniProt P51587, HGNC 1101, ENSP) | LOW | 0% | PASS (with caveats) |
| **imatinib** | Drug/compound | CHEMBL941 | 2 (ChEMBL, DrugBank DB00619) | LOW | ~0% | PASS |
| **ACE** | Ambiguous (gene) | ENSG00000159640 | 6+ (Ensembl, UniProt P12821, HGNC 2707, ChEMBL 1808, Reactome, InterPro) | **HIGH** | **72%** | PASS |
| **Alzheimer's** | Disease | MONDO_0004975 | **14** (MeSH, UMLS, Orphanet, ICD-10, NCIT, DOID, HPO, SNOMED, MedGen, ICD-11, BIRNLEX) | LOW | 0% | PASS |

### Quality Metrics

| Metric | Target | BRCA2 | imatinib | ACE | Alzheimer's |
|--------|--------|-------|----------|-----|-------------|
| Cross-ref IDs (min 2, target 4, excellent 6+) | 4 | 4 | 2 | 6+ | **14** |
| Collision detection | Flag | LOW | LOW | **HIGH** | LOW |
| Negative filter (if >20% off-topic) | Built | N/A | N/A | **Built** | N/A |
| Resolution tool calls (target <=5) | <=5 | ~11 | 4 | ~8 | 5 |

### Key Findings

**What works well:**
1. **Disease resolution is excellent** — Open Targets `dbXRefs` provides 14+ cross-references in a single GraphQL query. Disease is the strongest entity type for primary-tier-only resolution.
2. **Collision detection works** — ACE correctly identified as HIGH risk with 72% off-topic rate. Negative filters built for both gene and drug-class interpretations. Disambiguation prompt designed.
3. **Drug resolution captures mechanisms** — imatinib resolved with all 4 mechanisms of action and linked targets from a single Open Targets query.
4. **The 5-stage workflow is sound** — all 4 test cases followed the stages naturally without workflow gaps.

**Issues found:**
1. **Open Targets GraphQL synonym fields fail** — `symbolSynonyms` and `nameSynonyms` consistently error on target queries. Workaround: synonyms available for diseases but not genes/proteins via GraphQL. ToolUniverse (MyGene, UniProt) will fill this gap.
2. **GraphQL query complexity limits** — queries with >4 fields sometimes fail, requiring split queries. BRCA2 needed ~11 calls instead of the target <=5.
3. **No Entrez Gene ID without ToolUniverse** — NCBI Gene IDs cannot be obtained from Open Targets alone. Critical for GTEx queries (need Gencode versioned IDs).
4. **Drug chemical data missing** — PubChem CID, CAS, SMILES, InChI all unavailable without ToolUniverse. Imatinib test scored "minimum" (2 IDs) instead of "excellent" (6+).
5. **PubMed session transience** — one transient MCP session expiry observed (resolved on retry).

---

## 4. Corrections Needed

### SKILL.md Adjustments

| Item | Current | Recommended Change |
|------|---------|-------------------|
| Stage 2 Step 1 | Suggests single `search_entities` call | Note: Open Targets returns multiple entity types; always filter by expected type |
| Stage 3 Step 1 | "From the primary ID, retrieve cross-references" | Add: Split GraphQL queries into <=4 fields to avoid complexity errors |
| Stage 3 Step 3 | "Collect synonyms and aliases" | Add: `symbolSynonyms`/`nameSynonyms` may fail on OT GraphQL; use ToolUniverse MyGene/UniProt as enrichment source |
| Stage 4 Step 2 | "run a PubMed title search" | Clarify: use `"[SYMBOL]"[Title]` exact match, review top 20 *by relevance* |

### tool-lookup.yaml Adjustments

| Item | Change |
|------|--------|
| `disambiguation.gene_to_ensembl` primary | Add note: "OT GraphQL synonym fields may error; use MyGene for synonym collection" |
| New capability key | Add `disambiguation.gene_synonyms` pointing to MyGene and UniProt for synonym retrieval |

---

## 5. Phase 2 Readiness

### Prerequisites Met
- [x] ToolUniverse MCP configured (activate on next session restart)
- [x] `tool-lookup.yaml` created with full capability mapping
- [x] `entity-resolution` SKILL.md written and tested
- [x] Known parameter corrections documented
- [x] Evidence grading framework documented
- [x] Test infrastructure (`scratch/entity-resolution-tests/`) established

### Recommended Before Phase 2
1. **Restart session** to activate ToolUniverse MCP
2. **Run tool verification** — confirm high-priority ToolUniverse tools exist and respond correctly
3. **Apply SKILL.md corrections** from Section 4 above
4. **Re-run BRCA2 and imatinib tests** with ToolUniverse active to verify enrichment

### Phase 2 Scope (Research Nodes)
- Build `target-intelligence` SKILL.md (~350-400 lines)
- Build `drug-intelligence` SKILL.md (~350-400 lines)
- Test both with 2-3 example targets/compounds using ToolUniverse
- Verify wikilink edges (entity-resolution → target-intel, entity-resolution → drug-intel)

---

## Appendix: Test Output Files

| File | Lines | Entity |
|------|-------|--------|
| `scratch/entity-resolution-tests/brca2_test.md` | 197 | Gene/protein |
| `scratch/entity-resolution-tests/imatinib_test.md` | 195 | Drug/compound |
| `scratch/entity-resolution-tests/ace_test.md` | 278 | Ambiguous (gene + drug class) |
| `scratch/entity-resolution-tests/alzheimers_test.md` | 209 | Disease |
