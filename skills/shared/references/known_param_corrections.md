# Known Parameter Corrections

> Consolidated ToolUniverse API quirks that cause silent failures.
> Version: 1.1.0
> Source: Verified across all four reference skills.
>
> **Naming convention:** Tool names here match `tool-lookup.yaml` keys.
> ToolUniverse canonical names (if different) are noted in parentheses.

---

## Critical Parameter Corrections

| Tool | Common Mistake | Correct Usage | Notes |
|------|---------------|---------------|-------|
| `ensembl_lookup_gene` | `id` param only | `gene_id` + `species="homo_sapiens"` | species is **required**; response wrapped in `{status, data, url, content_type}` — access via `result['data']` |
| `ensembl_get_xrefs` | `gene_id` | `id` | Parameter renamed from expected convention |
| `mygene_query` (TU: `MyGene_query_genes`) | `q` | `query` | Different from standard convention |
| `pubchem_get_cid` (TU: `PubChem_get_CID_by_compound_name`) | `compound_name` | `name` | Param is just `name`, not `compound_name` |
| `gtex_get_median_gene_expression` (TU: `GTEx_get_median_gene_expression`) | `gencode_id` only | `gencode_id` + `operation="median"` | If versioned ID fails (e.g., ENSG00000114573.18), try unversioned |
| `alphafold_get_prediction` | `uniprot_accession` | `qualifier` | Parameter name differs from intuitive choice |
| `reactome_pathways` (TU: `Reactome_map_uniprot_to_pathways`) | `uniprot_id` | `id` | Unintuitive parameter name |

---

## Open Targets Parameter Patterns

| Pattern | Wrong | Correct | Affected Tools |
|---------|-------|---------|----------------|
| Ensembl ID param | `ensemblID` (uppercase) | `ensemblId` (camelCase) | All OT target queries |
| Publications endpoint | `ensemblId` | `entityId` | `OpenTargets_get_publications_*` |
| Associated drugs | `ensemblId` alone | `ensemblId` + `size` (required) | `OpenTargets_get_associated_drugs_*` |

---

## Response Format Quirks

| Tool | Expected Format | Actual Format | Handling |
|------|----------------|---------------|----------|
| `PubMed_search_articles` | `{articles: [...]}` | Plain list of dicts | Iterate directly, no wrapper |
| `UniProt_get_function_by_accession` | Dict | List of strings | Iterate directly, not a dict |
| `ensembl_lookup_gene` | Direct response | Nested `{status, data, ...}` | Access `result['data']` |

---

## Multi-Parameter Requirements

These tools require **all** listed parameters (none are optional):

| Tool | Required Parameters |
|------|-------------------|
| `hpa_get_rna_expression_by_source` (TU: `HPA_get_rna_expression_by_source`) | `gene_name` + `source_type` + `source_name` |
| `drugbank_get_safety` (TU: `drugbank_get_safety_*`) | `query` + `case_sensitive` + `exact_match` + `limit` |
| `string_interactions` (TU: `STRING_get_protein_interactions`) | `protein_ids` (array, even for single) + `species=9606` |

---

## ID Format Requirements

| Tool | Expected ID Format | Example |
|------|-------------------|---------|
| `gnomad_get_gene_constraints` | Gene **symbol** (not Ensembl ID) | `BRCA1` not `ENSG00000012048` |
| `depmap_gene_effect` (TU: `DepMap_get_gene_dependencies`) | Gene **symbol** (not Ensembl ID) | `EGFR` not `ENSG00000146648` |
| `chembl_bioactivity` (TU: `ChEMBL_get_target_activities`) | `target_chembl_id__exact` (double underscore) | `CHEMBL203` |
| `bindingdb_search` (TU: `BindingDB_get_ligands_by_uniprot`) | UniProt accession | `P12821`; affinity in **nM** (not uM) |
| `gtex_get_median_gene_expression` (TU: `GTEx_get_median_gene_expression`) | Gencode ID (versioned preferred) | `ENSG00000114573.18` |

---

## Phase 2 Parameter Corrections

| Tool | Common Mistake | Correct Usage | Notes |
|------|---------------|---------------|-------|
| `FAERS_count_*` (all 5 tools) | `drug_name` or `drug` | `medicinalproduct` | All FAERS tools use `medicinalproduct` param |
| `ADMETAI_predict_*` (all tools) | `smiles="CCO"` (bare string) | `smiles=["CCO"]` (list) | SMILES must be passed as a **list**, even for single compound |
| `DailyMed_parse_*` (parsed section tools) | `drug_name` | `setid` | Requires `setid` from `DailyMed_search_spls` first |
| `PharmGKB_get_clinical_annotations` | `drug_name` | `annotation_id` or gene-based query | May need annotation ID; check tool info |
| `FDA_OrangeBook_search_drug` | `drug` | `brand_name` or `generic_name` | Use exact trade name or generic name |

---

## Fallback Strategies

When a primary tool fails, try these alternatives:

| Capability | Primary | Fallback 1 | Fallback 2 |
|-----------|---------|-----------|-----------|
| Gene expression | GTEx (versioned ID) | GTEx (unversioned ID) | HPA tissue data |
| Protein structure | PDB search | AlphaFold prediction | InterPro domains |
| Citation network | PubMed `get_cited_by` | Europe PMC citations | Semantic Scholar |
| Drug safety | DrugBank safety | SIDER side effects | Open Targets safety |
| Gene-disease assoc. | Open Targets MCP | Open Targets TU tools | GWAS Catalog |
| ADMET predictions | ADMET-AI tools | DailyMed clinical_pharmacology | PubMed PK literature |
| Pharmacogenomics | PharmGKB tools | DailyMed PGx section | PubMed PGx literature |
| Post-marketing safety | FAERS 5-tool chain | DailyMed adverse_reactions | Open Targets safety |
| Regulatory status | FDA OrangeBook | DailyMed SPL | ClinicalTrials.gov |
