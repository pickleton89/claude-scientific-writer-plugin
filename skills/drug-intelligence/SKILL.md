---
name: drug-intelligence
version: 1.1.0
description: "Generate comprehensive drug dossiers using resolved IDs from entity-resolution. Covers chemistry, mechanism, ADMET, safety (FAERS), pharmacogenomics, and regulatory status across 6 stages."
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
context: fork
agent: general-purpose
model: claude-sonnet-4-6
effort: medium
---

# Drug Intelligence

<overview>
Generate a structured drug dossier for a compound using canonical IDs from `entity-resolution`. Produces a 10-section report covering identity, chemistry, mechanism & targets, ADMET, clinical development, safety, pharmacogenomics, regulatory status, summary, and data gaps. Uses DailyMed parsed sections as FDA label backbone, enriched with ADMET-AI predictions, FAERS post-marketing data, PharmGKB pharmacogenomics, and FDA Orange Book regulatory data.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- User asks about a drug, medication, or compound ("tell me about imatinib", "drug profile for metformin")
- Need drug safety assessment, ADMET profiling, or regulatory status
- Downstream skill (target-validation) needs a drug dossier as input
- User asks "what do we know about [drug]?"

Do NOT use this skill when:
- Query is about a gene/protein target (not a compound) -> use `target-intelligence`
- Query is literature-only with no database lookups -> use `deep-research`
- Entity has not been resolved yet -> run `entity-resolution` first
- User wants comparative drug-target analysis -> use `target-validation`
</when_to_use>

<prerequisites>
## Required Input

This skill receives a **resolved identity table** from `entity-resolution` containing:

| Field | Required | Example |
|-------|----------|---------|
| Drug Name | Yes | imatinib |
| ChEMBL ID | Yes | CHEMBL941 |
| PubChem CID | Yes | 5291 |
| SMILES | Preferred | CC1=C... |
| DrugBank ID | Preferred | DB00619 |
| Collision Risk | Yes | LOW |

If no identity table is provided, run `entity-resolution` first.
</prerequisites>

<key_principles>
## Key Principles

1. **Report-first approach** — Create report file FIRST, then populate progressively
2. **Citation requirements** — Every piece of information MUST include its source. Use inline `*Source: {Database} via {tool_name}*` after each data block
3. **Evidence grading** — Grade claims by evidence strength:

| Tier | Symbol | Criteria |
|------|--------|----------|
| T1 | ★★★ | FDA label data, pivotal clinical trial results |
| T2 | ★★☆ | Published clinical studies, validated assay data |
| T3 | ★☆☆ | Computational predictions, post-marketing signals |
| T4 | ☆☆☆ | Database annotations, text-mined associations |

4. **Mandatory completeness** — All sections must have data OR explicit "No data" with tool queried
5. **Negative results documented** — "No FAERS data" is data; empty sections are failures
</key_principles>

<workflow>
## Workflow: 6 Stages

### Stage 1: Report Init, ID Intake & Label Retrieval

**Objective:** Create report skeleton, receive resolved IDs, retrieve FDA label.

1. Create file: `{DRUG}_drug_report.md`
2. Initialize all 10 section headers with `[Researching...]` placeholders
3. Receive identity table from `entity-resolution` (or run it if not provided)
4. Populate Section 1 (Identity) from identity table
5. Retrieve DailyMed SPL: use `drug_data.label` capability
   - `DailyMed_search_spls(drug_name)` -> get `setid`
   - Store `setid` for all subsequent DailyMed parsed section calls
   - If no SPL found, note as investigational/non-US and continue

**Report file template:**

```markdown
# Drug Research Report: {DRUG NAME}

**Generated**: {Date} | **Query**: {Original query} | **Status**: In Progress

---

## 1. Compound Identity
### 1.1 Database Identifiers
{Populated from entity-resolution identity table}
### 1.2 Names & Synonyms
[Researching...]

## 2. Chemical Properties
### 2.1 Physicochemical Profile
[Researching...]
### 2.2 Drug-Likeness Assessment
[Researching...]

## 3. Mechanism & Targets
### 3.1 Primary Mechanism of Action
[Researching...]
### 3.2 Primary Target(s)
[Researching...]
### 3.3 Bioactivity Profile
[Researching...]

## 4. ADMET Properties
### 4.1 Absorption
[Researching...]
### 4.2 Distribution
[Researching...]
### 4.3 Metabolism
[Researching...]
### 4.4 Excretion
[Researching...]
### 4.5 Toxicity Predictions
[Researching...]

## 5. Clinical Development
### 5.1 Development Status
[Researching...]
### 5.2 Clinical Trial Landscape
[Researching...]

## 6. Safety Profile
### 6.1 Clinical Adverse Events
[Researching...]
### 6.2 Post-Marketing Safety (FAERS)
[Researching...]
### 6.3 Contraindications
[Researching...]
### 6.4 Drug-Drug Interactions
[Researching...]

## 7. Pharmacogenomics
### 7.1 Relevant Pharmacogenes
[Researching...]
### 7.2 Dosing Guidelines
[Researching...]

## 8. Regulatory & Labeling
### 8.1 Approval Status
[Researching...]
### 8.2 Patents & Exclusivity
[Researching...]
### 8.3 Special Populations
[Researching...]

## 9. Summary & Assessment
[Researching...]

## 10. Data Sources & Gaps
[Researching...]
```

---

### Stage 2: Chemistry & Properties

**Objective:** Full physicochemical profile and drug-likeness.

Use `drug_data.chemistry` capabilities:

| Step | Tool | Data |
|------|------|------|
| 1 | PubChem_get_compound_properties_by_CID | MW, formula, XLogP, TPSA, HBD, HBA, rotatable bonds |
| 2 | ADMETAI_predict_physicochemical_properties | Lipinski, QED, stereocenters; **SMILES as list** |
| 3 | ADMETAI_pred_solu_lipo_hydr | Solubility, lipophilicity; **SMILES as list** |

**Type normalization:** Convert all CIDs to strings before API calls.

**Section 2 output format:**

```markdown
## 2. Chemical Properties

### 2.1 Physicochemical Profile
| Property | Value | Drug-Likeness | Source |
|----------|-------|---------------|--------|
| Molecular Weight | {MW} g/mol | {pass/fail} (< 500) | PubChem |
| LogP | {value} | {pass/fail} (< 5) | ADMET-AI |
| TPSA | {value} A^2 | {pass/fail} (< 140) | PubChem |
| H-Bond Donors | {N} | {pass/fail} (<= 5) | PubChem |
| H-Bond Acceptors | {N} | {pass/fail} (< 10) | PubChem |
| Rotatable Bonds | {N} | {pass/fail} (< 10) | PubChem |

### 2.2 Drug-Likeness Assessment
**Lipinski Rule of Five**: {PASS/FAIL} ({N} violations)
**QED Score**: {value} ({interpretation})
```

---

### Stage 3: Mechanism & Targets

**Objective:** FDA label MOA + experimental targets from bioactivity data.

| Step | Source | Data |
|------|--------|------|
| 1 | DailyMed_parse_clinical_pharmacology | FDA MOA description [T1 evidence] |
| 2 | ChEMBL activities | Derive targets from activities (pChEMBL >= 6.0) |
| 3 | DGIdb | Target genes, interaction types |

**Critical rules:**
- **NEVER use `ChEMBL_get_molecule_targets`** - returns unfiltered, irrelevant targets
- **Derive targets from activities:** Query ChEMBL activities for compound -> filter to pChEMBL >= 6.0 -> get unique `target_chembl_id` values -> look up each target
- Convert all ChEMBL IDs to **strings** before API calls
- ChEMBL bioactivity: use `target_chembl_id__exact` (double underscore)

**Optional literature backbone (PubTator3)** (capability: `literature.entity_annotation`). Complements ChEMBL bioactivity with literature-grounded co-mention evidence. Run when the drug's PubTator3 entity ID was recorded by `entity-resolution`. Recipes:

- `uv run python skills/shared/scripts/pubtator3.py relations --entity @CHEMICAL_<NAME> --summary --top 25` — top genes/diseases co-mentioned with the drug. Genes with `negative_correlate` relation type are strong literature signals for primary targets (e.g. `@CHEMICAL_Vemurafenib → negative_correlate → @GENE_BRAF`); diseases with `treat`/`associate` relations seed the indication-discovery list (Stage 4).
- `uv run python skills/shared/scripts/pubtator3.py search --chemical <NAME> --gene <SYMBOL> --size 5 --summary` — confirm a candidate target by co-mention in primary literature before adding to Section 3.2.

PubTator3 evidence is T4 (text-mined) by default. Promote to T2/T3 only after cross-confirmation by ChEMBL bioactivity (pChEMBL ≥ 6.0) or DailyMed MOA text. Skip silently on network/wrapper error.

**Section 3 output format:**

```markdown
## 3. Mechanism & Targets

### 3.1 Primary Mechanism of Action
{FDA label MOA text}
*Source: DailyMed via DailyMed_parse_clinical_pharmacology [T1]*

### 3.2 Primary Target(s)
| Target | UniProt | Type | Potency | Evidence | Source |
|--------|---------|------|---------|----------|--------|

### 3.3 Bioactivity Profile
**Total ChEMBL Activities**: {N} datapoints across {N} assays
- Potency Range: {range}
- Primary Activity: {type}
```

---

### Stage 4: ADMET & Clinical Development

**Objective:** ADMET predictions + clinical trial landscape.

**ADMET chain** (use `drug_data.admet` + `prediction.admet` capabilities):

| Step | Tool | Data |
|------|------|------|
| 1 | ADMETAI_predict_bioavailability | Oral bioavailability, HIA, Caco-2, PAMPA, P-gp |
| 2 | ADMETAI_predict_BBB_penetrance | BBB penetration probability |
| 3 | ADMETAI_predict_CYP_interactions | CYP inhibitor/substrate predictions |
| 4 | ADMETAI_predict_clearance_distribution | Clearance, half-life, VDss, PPB |
| 5 | ADMETAI_predict_toxicity | AMES, hERG, DILI, ClinTox, LD50 |

**SMILES must be passed as list:** `smiles=["SMILES_STRING"]` (not bare string)

**Fallback chain** (if ADMET-AI fails):
1. DailyMed_parse_clinical_pharmacology -> extract PK parameters from label
2. PubMed search for "{drug} pharmacokinetics"
3. **NEVER leave Section 4 empty** - always populate with predictions OR label data OR literature

**Clinical trials** (use `drug_data.clinical` capabilities):
- `clinicaltrials_search(intervention=drug_name)`
- Compute phase counts from results (Phase 1/2/3/4)
- Count by status (Completed/Recruiting/Active/Terminated)
- List top representative trials, not all trials

---

### Stage 5: Safety, DDIs & Pharmacogenomics

**Objective:** Post-marketing safety, drug interactions, pharmacogenomics.

**FAERS mandatory structure** (use `drug_data.faers` capabilities):

All 5 FAERS tools use param `medicinalproduct` (not `drug_name`):

| Tool | Data |
|------|------|
| FAERS_count_reactions_by_drug_event | Top adverse reactions by MedDRA PT |
| FAERS_count_seriousness_by_drug_event | Serious vs non-serious breakdown |
| FAERS_count_outcomes_by_drug_event | Recovered/fatal/unresolved counts |
| FAERS_count_death_related_by_drug | Fatal outcome count |
| FAERS_count_patient_age_distribution | Reports by age group |

**FAERS reporting requirements (mandatory format):**

```markdown
### 6.2 Post-Marketing Safety (FAERS)

**Total FAERS Reports**: {N} (Date range: {start} - {end})

#### Seriousness Breakdown
| Category | Count | Percentage |
|----------|-------|------------|
| Serious | {N} | {%} |
| Non-Serious | {N} | {%} |

#### Top Adverse Reactions
| Reaction (MedDRA PT) | Count | % of Reports |
|----------------------|-------|--------------|

#### Outcome Distribution
| Outcome | Count | Percentage |
|---------|-------|------------|

#### Data Limitations
FAERS data represents voluntary reports and has important limitations:
- **Reporting bias**: Serious events more likely to be reported
- **Causality not established**: Reports do not prove drug caused the event
- **Incomplete data**: Many reports lack outcome information
- **Denominator unknown**: Cannot calculate incidence rates
```

**Drug interactions** (use `drug_data.label` capabilities):
- DailyMed_parse_drug_interactions -> DDI table, CYP interactions
- DailyMed_parse_contraindications -> contraindicated combinations
- DailyMed_parse_dosing -> dose modification guidance

**Pharmacogenomics** (use `drug_data.pgx` capabilities):

| Step | Tool | Data |
|------|------|------|
| 1 | PharmGKB_search_drugs | PharmGKB drug ID |
| 2 | PharmGKB_get_drug_details | Cross-references, related genes |
| 3 | PharmGKB_get_clinical_annotations | Variant-drug associations, evidence levels |
| 4 | PharmGKB_get_dosing_guidelines | CPIC/DPWG guidelines |

**PharmGKB fallback:** If PharmGKB tools fail:
1. DailyMed_parse_clinical_pharmacology -> PGx from FDA label
2. PubMed search for "{drug} pharmacogenomics"
3. Document: "PharmGKB unavailable; using label + literature"

---

### Stage 6: Regulatory & Completeness Audit

**Objective:** Regulatory status, special populations, completeness check.

**Regulatory** (use `drug_data.regulatory` capabilities):
- FDA_OrangeBook_search_drug -> approval status
- FDA_OrangeBook_get_approval_history -> approval timeline
- FDA_OrangeBook_get_exclusivity -> exclusivity periods
- FDA_OrangeBook_get_patent_info -> patent expiry dates
- FDA_OrangeBook_check_generic_availability -> generic status

**Special populations** (from DailyMed label):
- DailyMed_parse_dosing -> pediatric, geriatric, renal/hepatic impairment
- Note: US-only regulatory data; note limitation for non-US drugs

**Section 8 output format:**

```markdown
## 8. Regulatory & Labeling

### 8.1 Approval Status
| Agency | Status | Date | Indication |
|--------|--------|------|------------|

### 8.2 Patents & Exclusivity
| Patent # | Expiry | Type | Generic Available |
|----------|--------|------|-------------------|

### 8.3 Special Populations
| Population | Recommendation | Source |
|------------|----------------|--------|
| Pediatric | {guidance} | Label |
| Geriatric | {guidance} | Label |
| Renal impairment | {guidance} | Label |
| Hepatic impairment | {guidance} | Label |
| Pregnancy | {category} | Label |
```

**Completeness Audit** (mandatory before finalizing):

| Minimum | Check |
|---------|-------|
| ChEMBL targets derived from activities | Section 3 |
| ADMET populated (predicted OR label) | Section 4 |
| FAERS has mandatory structure | Section 6.2 |
| PharmGKB or label PGx attempted | Section 7 |
| Regulatory data present (or "non-US" noted) | Section 8 |
| All sections have data OR "No data" | All |

If any minimum is not met, document in Section 10.

**Finalize:**
1. Write Section 9 (Summary & Assessment): key strengths, concerns, research gaps
2. Write Section 10 (Data Sources & Gaps) with tool call summary and data quality notes
3. Update report status to "Complete"

</workflow>

<anti_patterns>
## Common Pitfalls

### 1. Using ChEMBL_get_molecule_targets
Returns unfiltered, irrelevant targets.
**Fix:** Derive targets from ChEMBL activities (pChEMBL >= 6.0), then look up each target individually.

### 2. ADMET Section Left Empty
Prediction tools may fail on some SMILES.
**Fix:** Always fall back to DailyMed clinical pharmacology, then PubMed PK literature. NEVER leave Section 4 empty.

### 3. FAERS Without Mandatory Structure
Reporting top reactions without seriousness breakdown, outcome distribution, and limitations.
**Fix:** Always include all 4 FAERS subsections: seriousness, top reactions, outcomes, limitations paragraph.

### 4. SMILES as Bare String to ADMET-AI
Causes silent failure.
**Fix:** Pass SMILES as list: `smiles=["CCO"]` not `smiles="CCO"`.

### 5. Missing DailyMed setid Dependency
Parsed section tools require setid, not drug name.
**Fix:** Always call `DailyMed_search_spls` first to get setid, then pass to parsed section tools.

### 6. Hardcoding Tool Names
**Fix:** Reference `tool-lookup.yaml` capability keys. See `known_param_corrections.md` for parameter quirks.
</anti_patterns>

<scope>
## Scope

**In Scope:**
- Comprehensive drug dossier (10 sections)
- DailyMed parsed sections as FDA label backbone
- ADMET-AI predictions with DailyMed fallback
- FAERS post-marketing safety (mandatory structure)
- PharmGKB pharmacogenomics
- FDA Orange Book regulatory data
- Completeness audit

**Out of Scope** (delegate to other skills):
- Entity disambiguation -> `entity-resolution`
- Literature deep-dive and RWE -> `deep-research`
- Comparative drug analysis and scorecards -> `target-validation`
- Target profiling for identified targets -> `target-intelligence`
</scope>

<cross_references>
## Related Skills

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

- **entity-resolution** (prerequisite): Provides resolved identity table with ChEMBL, PubChem, SMILES
- **target-intelligence** (related): Profile targets identified in Section 3
- **target-validation** (downstream): Comparative drug-target analysis using this dossier
- **deep-research** (parallel): Deep literature analysis and RWE beyond this skill's scope
- **tool-lookup.yaml**: Capability-to-tool mapping for all database queries
- **known_param_corrections.md**: Parameter quirks that cause silent failures
</cross_references>

## Fork-return contract

This skill runs in a forked subagent context (`context: fork`). The fork executes all 6 stages internally — DailyMed label retrieval, ChEMBL chemistry, mechanism/targets, ADMET-AI, FAERS safety queries, PGx, regulatory checks, and the 10-section dossier write — and returns **only a compact summary** to the calling conversation. Raw API responses, full DailyMed labels, FAERS adverse-event tables, and tool routing transcripts **stay inside the fork**. Pre-fork main-context cost per dossier is estimated at 30k–80k+ tokens (DailyMed full label + ChEMBL bioactivities + FAERS reports + ADMET predictions); the post-fork target is **≤ 1.5k tokens per dossier**.

The fork's final message to the caller is a single JSON object capped at ~600 tokens. Emit it verbatim as the last content of the response, fenced as ```json:

```jsonc
{
  "drug_id": "<INN-name>",
  "report_path": "<{DRUG}_drug_report.md path>",
  "report_dir": "research/drugs/<drug_slug>/",
  "resolved_ids": {
    "inn": "", "chembl_id": "", "pubchem_cid": "", "drugbank_id": "", "rxnorm_cui": "",
    "smiles": "", "inchikey": ""
  },
  "section_status": {
    "compound_identity": "complete", "chemical_properties": "complete",
    "mechanism_and_targets": "complete", "admet": "complete",
    "clinical_development": "complete", "safety_profile": "complete",
    "pharmacogenomics": "complete", "regulatory_and_labeling": "complete",
    "summary_and_assessment": "complete", "data_sources_and_gaps": "complete"
  },
  "regulatory_status": {
    "fda_approval": "approved | investigational | withdrawn | unknown",
    "first_approval_year": null,
    "boxed_warning": false
  },
  "completeness_audit": {
    "data_minimums_met": true,
    "missing_fields": [],
    "faers_signal_count": 0
  },
  "headline": "<≤140 chars: 1-line drug summary; e.g. 'pembrolizumab — anti-PD-1 mAb; FDA-approved 2014; 30+ indications; FAERS top signal: pneumonitis'>",
  "next_actions": [ "<≤2 short suggestions or empty array>" ]
}
```

**Required fields:** `drug_id`, `report_path`, `report_dir`, `resolved_ids` (the upstream entity-resolution identity table — these are the only IDs downstream consumers like target-validation should join on), `section_status` (one of `complete | partial | skipped` per section), `regulatory_status` (parsed from DailyMed + FDA — `boxed_warning` boolean is non-negotiable since it gates safety-critical downstream use), `completeness_audit.data_minimums_met` (boolean from the Stage 6 audit), `headline`. `faers_signal_count` is the number of disproportionality signals exceeding the skill's PRR/ROR thresholds; zero if the FAERS section was skipped.

**Forbidden in fork return:** raw DailyMed label text, full FAERS adverse-event tables, ChEMBL bioactivity lists, ADMET-AI per-endpoint predictions, full mechanism prose, citation/reference lists. All of that lives in the persisted artifacts under `report_dir` and the rendered `{DRUG}_drug_report.md`. The caller follows up with targeted reads — for example, `!\`grep -A 30 "## Section 6: Safety" <report_path>\`` or `!\`jq '.faers_signals' research/drugs/<slug>/audit.json\`` — to surface specific dossier sections on demand at zero token cost in the main context.

**If the dossier cannot complete:** still return the JSON shape with `section_status` reflecting which sections finished, `completeness_audit.data_minimums_met: false` with the missing fields enumerated, and a `next_actions` entry explaining what blocked completion (e.g., `"resume after DailyMed retrieval succeeds"`, `"entity-resolution did not provide ChEMBL ID — required for chemistry section"`). Partial state remains in `report_dir` for follow-up runs.
