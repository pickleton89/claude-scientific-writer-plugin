# Tool Availability Audit

> Version: 1.0.0
> Date: 2026-03-01
> Status: Partial — ToolUniverse MCP installed but requires session restart

---

## MCP Server Status

| MCP Server | Status | Notes |
|------------|--------|-------|
| Open Targets | Active | GraphQL API, search_entities — fully functional |
| PubMed | Active | search_articles, get_article_metadata, full-text, related articles |
| Consensus | Active | Semantic search over 200M+ papers |
| Zotero | Active | Personal library management |
| Readwise Reader | Active | Reading list and highlights |
| **ToolUniverse** | **Configured, pending restart** | Added via `claude mcp add tooluniverse -- uvx --refresh tooluniverse` |

## ToolUniverse Configuration

```json
{
  "tooluniverse": {
    "type": "stdio",
    "command": "uvx",
    "args": ["--refresh", "tooluniverse"],
    "env": {}
  }
}
```

**Location:** Project-scoped in `~/.claude.json` under the `claude-scientific-writer-plugin` project key.

**Compact mode (default):** Exposes 5 meta-tools:
- `list_tools` — List available tools by category
- `grep_tools` — Search tools by keyword
- `get_tool_info` — Get tool details and parameters
- `execute_tool` — Execute a specific tool
- `find_tools` — Find tools by capability description

## Primary Tier Tools (Verified Active)

These tools from `tool-lookup.yaml` are available NOW via existing MCPs:

| Capability Key | Tool | MCP | Status |
|---------------|------|-----|--------|
| `disambiguation.gene_to_ensembl` | `search_entities` | Open Targets | Verified |
| `disambiguation.compound_to_chembl` | `search_entities` | Open Targets | Verified |
| `disambiguation.disease_to_efo` | `search_entities` | Open Targets | Verified |
| `drug_data.safety` | `query_open_targets_graphql` | Open Targets | Verified |
| `literature.search` | `search_articles` | PubMed | Verified |
| `literature.search` | `search` | Consensus | Verified |
| `literature.full_text` | `get_full_text_article` | PubMed | Verified |
| `literature.citations` | `find_related_articles` | PubMed | Verified |

## ToolUniverse Tier Tools (Pending Verification)

These tools need verification after session restart. Listed by priority for entity-resolution and research skills:

### High Priority (entity-resolution dependencies)

| Capability Key | Expected TU Tool | Verify |
|---------------|-----------------|--------|
| `disambiguation.gene_to_ensembl` | `mygene_query` | [ ] Exists, correct params (`query` not `q`) |
| `disambiguation.gene_to_ensembl` | `ensembl_lookup_gene` | [ ] Exists, needs `gene_id` + `species` |
| `disambiguation.compound_to_chembl` | `chembl_molecule_search` | [ ] Exists, search by name |
| `disambiguation.compound_to_chembl` | `pubchem_cid_lookup` | [ ] Exists |
| `disambiguation.protein_to_uniprot` | `uniprot_search` | [ ] Exists |
| `disambiguation.protein_to_uniprot` | `uniprot_id_mapping` | [ ] Exists, ID type conversion |

### Medium Priority (target-intelligence / drug-intelligence)

| Capability Key | Expected TU Tool | Verify |
|---------------|-----------------|--------|
| `target_structure.domains` | `interpro_protein` | [ ] |
| `target_structure.three_d` | `pdb_search` | [ ] |
| `target_structure.three_d` | `alphafold_get_prediction` | [ ] Param is `qualifier` |
| `expression.tissue` | `gtex_get_median_gene_expression` | [ ] Needs `gencode_id` + `operation` |
| `expression.tissue` | `hpa_tissue` | [ ] |
| `interactions.ppi` | `string_interactions` | [ ] `protein_ids` must be array |
| `interactions.pathways` | `reactome_pathways` | [ ] Param is `id` not `uniprot_id` |
| `genetic_variation.population` | `gnomad_variant` | [ ] |
| `genetic_variation.population` | `gnomad_get_gene_constraints` | [ ] Uses gene_symbol |
| `genetic_variation.essentiality` | `depmap_gene_effect` | [ ] Uses gene_symbol |

### Lower Priority (drug-intelligence / target-validation)

| Capability Key | Expected TU Tool | Verify |
|---------------|-----------------|--------|
| `drug_data.bioactivity` | `chembl_bioactivity` | [ ] |
| `drug_data.bioactivity` | `bindingdb_search` | [ ] |
| `drug_data.clinical` | `clinicaltrials_search` | [ ] |
| `drug_data.safety` | `sider_side_effects` | [ ] |
| `drug_data.admet` | `admet_ai_predict` | [ ] |
| `prediction.binding` | `boltz2_predict` | [ ] |
| `literature.search` | `europe_pmc_search` | [ ] |
| `literature.citations` | `openalex_citations` | [ ] |

## API Keys Status

| Key | Status | Impact |
|-----|--------|--------|
| `NCBI_API_KEY` | Not configured | PubMed rate limits (existing MCP handles this) |
| `NVIDIA_API_KEY` | Not configured | Boltz-2 predictions unavailable |
| `BIOGRID_API_KEY` | Not configured | BioGRID interactions unavailable |
| `SEMANTIC_SCHOLAR_API_KEY` | Not configured | Rate limits on S2 tools |

**Recommendation:** Most tools work without API keys. Add `NCBI_API_KEY` if rate limits become an issue. `NVIDIA_API_KEY` only needed for Boltz-2 predictions (Phase 5 concern).

## Next Steps

1. Restart Claude Code session to activate ToolUniverse MCP
2. Run verification script: `grep_tools` for each high-priority tool
3. Execute one test call per tool to verify parameters match `known_param_corrections.md`
4. Update this audit with verified/failed status
5. Flag any tools that don't exist or have different parameters than expected
