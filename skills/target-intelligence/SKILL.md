---
name: target-intelligence
version: 1.1.0
description: "Generate comprehensive target dossiers for genes/proteins using resolved IDs from entity-resolution. Covers structure, function, expression, variants, disease associations, and druggability across 6 stages."
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
context: fork
agent: general-purpose
model: claude-sonnet-4-6
effort: medium
---

# Target Intelligence

<overview>
Generate a structured target dossier for a gene or protein using canonical IDs from `entity-resolution`. Produces a 12-section report covering identity, structure, function, interactions, expression, variants, disease associations, druggability, and safety. Uses Open Targets MCP as foundation, enriched with ToolUniverse databases.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- User asks about a drug target, protein, or gene ("tell me about EGFR", "BRCA2 target profile")
- Need target validation, druggability assessment, or comprehensive target profiling
- Downstream skill (target-validation) needs a target dossier as input
- User asks "what do we know about [target]?"

Do NOT use this skill when:
- Query is purely about a drug/compound (not a target) -> use `drug-intelligence`
- Query is literature-only with no database lookups -> use `deep-research`
- Entity has not been resolved yet -> run `entity-resolution` first
- User wants comparative target-drug analysis -> use `target-validation`
</when_to_use>

<prerequisites>
## Required Input

This skill receives a **resolved identity table** from `entity-resolution` containing:

| Field | Required | Example |
|-------|----------|---------|
| HGNC Symbol | Yes | BRCA2 |
| Ensembl Gene ID | Yes | ENSG00000139618 |
| UniProt Accession | Yes | P51587 |
| Entrez ID | Preferred | 675 |
| ChEMBL Target ID | Preferred | CHEMBL2073 |
| Collision Risk | Yes | LOW / HIGH |
| Negative Filter | If HIGH | -"ACE inhibitor" -"angiotensin" |

If no identity table is provided, run `entity-resolution` first.
</prerequisites>

<key_principles>
## Key Principles

1. **Report-first approach** — Create report file FIRST, then populate progressively
2. **Citation requirements** — Every piece of information MUST include its source. Use inline `*Source: {Database} via {tool_name}*` after each data block
3. **Evidence grading** — Grade all disease claims T1-T4 (defined in Stage 2)
4. **Mandatory completeness** — All sections must have data OR explicit "No data" with tool queried
5. **Negative results documented** — "No PDB structures" is data; empty sections are failures
</key_principles>

<workflow>
## Workflow: 6 Stages

### Stage 1: Report Init & ID Intake

**Objective:** Create report skeleton, receive resolved IDs.

1. Create file: `{SYMBOL}_target_report.md`
2. Initialize all 12 section headers with `[Researching...]` placeholders
3. Receive identity table from `entity-resolution` (or run it if not provided)
4. Populate Section 2 (Target Identifiers) immediately from identity table
5. Check GPCR status: lookup `target_biology.gpcr_detection` capability
   - Build GPCRdb entry name: `{symbol_lower}_human`
   - If GPCR detected, flag for specialized data in Stages 2-3

**Report file template:**

```markdown
# Target Intelligence Report: {FULL PROTEIN NAME}

**Generated**: {Date} | **Query**: {Original query} | **Status**: In Progress

---

## 1. Executive Summary
[Researching...]

## 2. Target Identifiers
{Populated from entity-resolution identity table}

## 3. Basic Information
[Researching...]

## 4. Structural Biology
[Researching...]

## 5. Function & Pathways
[Researching...]

## 6. Protein-Protein Interactions
[Researching...]

## 7. Expression Profile
[Researching...]

## 8. Variants & Disease Associations
[Researching...]

## 9. Druggability Assessment
[Researching...]

## 10. Safety Profile
[Researching...]

## 11. Summary & Recommendations
[Researching...]

## 12. Data Sources & Gaps
[Researching...]
```

---

### Stage 2: Open Targets Foundation

**Objective:** Populate baseline data across multiple sections before specialized queries.

Query these OT MCP endpoints (use `query_open_targets_graphql`):

| Endpoint | Fills Section | Data |
|----------|---------------|------|
| Target diseases/phenotypes | 8 | Disease associations |
| Target tractability | 9 | Druggability modalities |
| Target safety | 10 | Safety liabilities, adverse effects |
| Target interactions | 6 | PPI network (OT aggregated) |
| Target gene ontology | 5 | GO annotations (MF, BP, CC) |
| Mouse models | 8, 10 | Mouse KO phenotypes |
| Chemical probes | 9 | Available tool compounds |
| Associated drugs | 9 | Known drugs (approved + clinical) |
| Publications | 12 | Literature counts |

**Key patterns:**
- Use `ensemblId` (camelCase, not `ensemblID`)
- For associated drugs: include `size` parameter (required)
- For publications: use `entityId` (not `ensemblId`)
- Document empty results explicitly: "No data returned from {endpoint}"

**Evidence grading on disease claims:**

| Tier | Symbol | Criteria |
|------|--------|----------|
| T1 | ★★★ | Direct mechanistic evidence, human genetic proof |
| T2 | ★★☆ | Functional studies, model organism validation |
| T3 | ★☆☆ | Association, screen hits, computational prediction |
| T4 | ☆☆☆ | Mention, review, text-mined |

Grade every disease association in Section 8.

---

### Stage 3: Structure, Domains & Function

**Objective:** Comprehensive structural and functional characterization.

**3-step structure search chain** (use `target_structure` capabilities):

| Step | Tool | Purpose |
|------|------|---------|
| 1 | UniProt cross-references | PDB IDs from UniProt entry (most reliable) |
| 2 | Sequence-based PDB search | Catches missing annotations (identity >= 70%) |
| 3 | Domain-based search | InterPro domains -> PDB by domain name |
| Always | AlphaFold prediction | Param is `qualifier`, not `uniprot_accession` |

**Function data** (use `interactions.pathways` capabilities):
- Reactome pathways: param is `id`, not `uniprot_id`
- GO terms from OT (Stage 2) + UniProt function annotation
- Subcellular localization from UniProt

**GPCR branch** (if detected in Stage 1):
- GPCRdb structures (active/inactive states)
- GPCRdb ligands (agonists, antagonists, allosteric modulators)
- GPCRdb mutations (Ballesteros-Weinstein numbering)
- Add dedicated GPCR subsection to Section 4

**Section 4 output format:**

```markdown
## 4. Structural Biology

### 4.1 Experimental Structures (PDB)
| PDB ID | Resolution | Method | Ligand | Coverage | Year |
|--------|------------|--------|--------|----------|------|

**Total PDB Entries**: {N}
**Search Method**: 3-step chain (UniProt xrefs -> sequence -> domain)

### 4.2 AlphaFold Prediction
- Available: Yes/No
- Confidence: {pLDDT range}

### 4.3 Domain Architecture
| Domain | Start-End | Database | Description |
|--------|-----------|----------|-------------|
```

---

### Stage 4: Interactions & Expression

**Objective:** PPI network and tissue expression profile.

**Interactions** (use `interactions.ppi` capabilities):
- STRING: `protein_ids` must be array, `species=9606`
- IntAct: molecular interaction data
- Target: >= 20 PPIs for well-characterized targets

**Expression** (use `expression` capabilities):

GTEx versioned ID fallback chain:
1. Try unversioned Ensembl ID + `operation="median"`
2. If empty, get version from Ensembl lookup -> try `ENSG...{version}`
3. If still empty, fall back to HPA tissue data

HPA extended expression:
- `HPA_get_rna_expression_by_source` requires ALL three params: `gene_name` + `source_type` + `source_name`
- Include top 10 tissues by expression level

**Section 7 output format:**

```markdown
## 7. Expression Profile

### 7.1 Tissue Expression (GTEx)
| Tissue | Median TPM | Rank |
|--------|-----------|------|

### 7.2 Protein Expression (HPA)
| Tissue | Protein Level | RNA nTPM |
|--------|---------------|----------|

### 7.3 Subcellular Localization
- Primary: {location}
- Additional: {locations}
```

---

### Stage 5: Variants, Disease & Safety

**Objective:** Genetic variation, clinical variants, disease associations, and safety.

**Population genetics** (use `genetic_variation.population` capabilities):
- gnomAD gene constraints: uses gene **symbol** (not Ensembl ID)
  - Report: pLI, LOEUF, missense Z, synonymous Z (4 constraint scores minimum)
- ClinVar: separate SNVs from CNVs in reporting

**Disease associations:**
- Open Targets (from Stage 2) provides aggregated evidence
- Grade each association T1-T4 with source type
- **DisGeNET is NOT in ToolUniverse** - use OT + ClinVar instead

**Mouse models** (from Stage 2 OT data):
- KO phenotypes relevant to safety assessment

**Safety** (from Stage 2 OT data):
- Known safety liabilities and adverse effects
- Target-related toxicity concerns
- Essential organ expression flags (from Stage 4)

**Section 8 output format:**

```markdown
## 8. Variants & Disease Associations

### 8.1 Population Constraint Scores
| Metric | Value | Interpretation |
|--------|-------|----------------|
| pLI | {value} | {tolerant/intolerant to LoF} |
| LOEUF | {value} | {constrained/unconstrained} |
| Missense Z | {value} | {constrained/unconstrained} |
| Synonymous Z | {value} | {baseline} |

### 8.2 Clinical Variants (ClinVar)
#### SNVs
| Variant | Significance | Condition | Review |
|---------|-------------|-----------|--------|

#### CNVs
| Type | Region | Significance |
|------|--------|-------------|

### 8.3 Disease Associations (Open Targets)
| Disease | Score | Evidence Tier | Source Types |
|---------|-------|---------------|-------------|
```

---

### Stage 6: Druggability & Completeness Audit

**Objective:** Assess druggability, compile data, audit completeness.

**Druggability assessment** (use `target_biology.druggability_class` capabilities):
- Pharos TDL classification (Tclin/Tchem/Tbio/Tdark)
- OT tractability modalities (from Stage 2)
- Chemical probes availability (from Stage 2)
- DGIdb druggability categories

**Target essentiality** (use `genetic_variation.essentiality` capabilities):
- DepMap CRISPR data: uses gene **symbol**
- Negative scores = essential (< -0.5 strongly, < -1.0 extremely)

**Bioactivity data** (use `drug_data.bioactivity` capabilities):
- ChEMBL: `target_chembl_id__exact` (double underscore)
- BindingDB: UniProt accession, affinity in **nM**

**Section 9 output format:**

```markdown
## 9. Druggability Assessment

### 9.1 Target Development Level (Pharos)
- **TDL**: {Tclin/Tchem/Tbio/Tdark}
- **Protein Family**: {family}
- **Interpretation**: {druggability statement}

### 9.2 Tractability (Open Targets)
| Modality | Tractable | Top Bucket |
|----------|-----------|-----------|
| Small molecule | Yes/No | {bucket} |
| Antibody | Yes/No | {bucket} |
| Other | Yes/No | {bucket} |

### 9.3 Known Drugs & Clinical Compounds
| Drug | Phase | Indication | Mechanism |
|------|-------|------------|-----------|

### 9.4 Chemical Probes
| Probe | Selectivity | Use | Source |
|-------|-------------|-----|--------|

### 9.5 DepMap Essentiality
- **Mean Effect Score**: {score}
- **Interpretation**: {essential/non-essential}
```

**Completeness Audit** (mandatory before finalizing):

| Minimum | Check |
|---------|-------|
| >= 1 PDB structure OR AlphaFold | Section 4 |
| GO annotations present | Section 5 |
| >= 20 PPIs (well-characterized) | Section 6 |
| Top 10 tissues expression | Section 7 |
| 4 constraint scores | Section 8.1 |
| Disease associations graded | Section 8.3 |
| Druggability assessed | Section 9 |
| All sections have data OR "No data" | All |

If any minimum is not met, document explicitly in Section 12 (Data Sources & Gaps).

**Finalize:**
1. Write Section 1 (Executive Summary): 2-3 sentences + "Bottom Line" on druggability
2. Write Section 11 (Summary & Recommendations)
3. Write Section 12 (Data Sources & Gaps) with tool call summary
4. Update report status to "Complete"

</workflow>

<anti_patterns>
## Common Pitfalls

### 1. Skipping Entity Resolution
Running target queries with unresolved gene symbols leads to wrong target or missed data.
**Fix:** Always receive identity table from `entity-resolution` first.

### 2. Using OT GraphQL symbolSynonyms/nameSynonyms
These fields error on target queries.
**Fix:** Get synonyms from UniProt alternative names or MyGene instead.

### 3. Oversized OT GraphQL Queries
Queries with >4 fields sometimes fail.
**Fix:** Split into smaller queries (2-3 fields each).

### 4. Empty Sections Left Blank
An empty section is a failure; "No data" is data.
**Fix:** Always document negative results with the tool that was queried and what it returned.

### 5. Missing GTEx Versioned ID Fallback
GTEx often requires versioned Ensembl IDs.
**Fix:** Follow the 3-step fallback chain (unversioned -> versioned -> HPA).

### 6. Hardcoding Tool Names
**Fix:** Reference `tool-lookup.yaml` capability keys. See `known_param_corrections.md` for parameter quirks.
</anti_patterns>

<scope>
## Scope

**In Scope:**
- Comprehensive target biology dossier (12 sections)
- OT MCP + ToolUniverse enrichment for structure, expression, variants, druggability
- GPCR specialized branch
- Evidence grading (T1-T4) on disease claims
- Completeness audit with data minimums

**Out of Scope** (delegate to other skills):
- Entity disambiguation -> `entity-resolution`
- Literature deep-dive and publication analysis -> `deep-research`
- Target validation scoring and comparative analysis -> `target-validation`
- Drug profiling for compounds found -> `drug-intelligence`
</scope>

<cross_references>
## Related Skills

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

- **entity-resolution** (prerequisite): Provides resolved identity table with canonical IDs
- **drug-intelligence** (downstream): Profile drugs identified in Section 9
- **target-validation** (downstream): Comparative target-drug analysis using this dossier
- **deep-research** (parallel): Deep literature analysis beyond Section 12 publication counts
- **tool-lookup.yaml**: Capability-to-tool mapping for all database queries
- **known_param_corrections.md**: Parameter quirks that cause silent failures
</cross_references>

## Fork-return contract

This skill runs in a forked subagent context (`context: fork`). The fork executes all 6 stages internally — Open Targets Foundation queries, ToolUniverse calls for structure/domains/expression/variants/safety/druggability, evidence grading, and the 12-section dossier write — and returns **only a compact summary** to the calling conversation. Raw API responses, intermediate JSON blobs, GraphQL payloads, and tool routing transcripts **stay inside the fork**. Pre-fork main-context cost per dossier is estimated at 30k–80k+ tokens (multi-stage MCP responses + per-section enrichment); the post-fork target is **≤ 1.5k tokens per dossier**.

The fork's final message to the caller is a single JSON object capped at ~600 tokens. Emit it verbatim as the last content of the response, fenced as ```json:

```jsonc
{
  "target_id": "<HGNC-symbol>",
  "report_path": "<{SYMBOL}_target_report.md path>",
  "report_dir": "research/targets/<symbol_slug>/",
  "resolved_ids": {
    "hgnc_symbol": "", "ensembl_gene_id": "", "uniprot_id": "", "chembl_target_id": ""
  },
  "section_status": {
    "executive_summary": "complete", "target_identifiers": "complete",
    "basic_information": "complete", "structural_biology": "complete",
    "function_and_pathways": "complete", "protein_interactions": "complete",
    "expression_profile": "complete", "variants_and_disease": "complete",
    "druggability": "complete", "safety_profile": "complete",
    "summary_and_recommendations": "complete", "data_sources_and_gaps": "complete"
  },
  "completeness_audit": {
    "data_minimums_met": true,
    "missing_fields": [],
    "evidence_grading_distribution": { "T1": 0, "T2": 0, "T3": 0, "T4": 0 }
  },
  "headline": "<≤140 chars: 1-line target summary; e.g. 'BRCA1 — DNA repair tumor suppressor; 5 approved drugs target BRCA pathway; high tractability'>",
  "next_actions": [ "<≤2 short suggestions or empty array>" ]
}
```

**Required fields:** `target_id`, `report_path`, `report_dir`, `resolved_ids` (the upstream entity-resolution identity table — these are the only IDs downstream consumers like target-validation should join on), `section_status` (one of `complete | partial | skipped` per section), `completeness_audit.data_minimums_met` (boolean from the Stage 6 audit), `headline`. `evidence_grading_distribution` counts disease-association claims by tier (T1 high-confidence → T4 weak); empty if no disease section was generated.

**Forbidden in fork return:** raw Open Targets GraphQL responses, ToolUniverse tool stdout, full PDB structure metadata, expression-atlas tables, variant lists, full reference lists. All of that lives in the persisted artifacts under `report_dir` and the rendered `{SYMBOL}_target_report.md`. The caller follows up with targeted reads — for example, `!\`grep -A 30 "## Section 9: Druggability" <report_path>\`` or `!\`jq '.evidence_grading' research/targets/<slug>/audit.json\`` — to surface specific dossier sections on demand at zero token cost in the main context.

**If the dossier cannot complete:** still return the JSON shape with `section_status` reflecting which sections finished, `completeness_audit.data_minimums_met: false` with the missing fields enumerated, and a `next_actions` entry explaining what blocked completion (e.g., `"resume after Open Targets API responds"`, `"entity-resolution did not provide ChEMBL target ID — required for druggability section"`). Partial state remains in `report_dir` for follow-up runs.
