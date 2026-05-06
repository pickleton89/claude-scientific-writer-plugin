---
name: target-validation
version: 1.1.0
description: "Quantitative drug target validation (0-100 score) consuming upstream dossiers from entity-resolution, target-intelligence, and drug-intelligence. Produces GO/NO-GO recommendation with scorecard, pathway redundancy analysis, and validation roadmap."
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
context: fork
agent: general-purpose
model: claude-opus-4-7
effort: high
---

# Target Validation

<overview>
Produce a quantitative Target Validation Score (0-100) with priority tier classification and GO/NO-GO recommendation. **Consumes** upstream dossiers — does NOT re-fetch data already gathered by `target-intelligence` or `drug-intelligence`. Only queries for genuinely new dimensions: clinical precedent details (failed programs), pathway redundancy, compensation risk, and gap-fill.

Evidence grading follows `../shared/references/evidence_grading.md` (T1-T4). Scoring weights: T1=full, T2=70-80%, T3=40-60%, T4=10-20%.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- User asks "Is [target] a good drug target for [disease]?"
- Need quantitative GO/NO-GO recommendation for target investment
- Want to score and compare targets for drug discovery prioritization
- Downstream of `target-intelligence` + `drug-intelligence` pipeline
- User needs a validation scorecard for stakeholder decisions

Do NOT use this skill when:
- Need target biology overview only -> use `target-intelligence`
- Need drug compound profiling only -> use `drug-intelligence`
- Need literature-only analysis -> use `deep-research`
- Entity has not been resolved yet -> run `entity-resolution` first
- No upstream dossiers exist -> run intel skills first
</when_to_use>

<prerequisites>
## Required Input

This skill **consumes** upstream dossiers. It does NOT re-query data already gathered.

| Input | Source Skill | Required | What It Provides |
|-------|-------------|----------|------------------|
| Identity table | `entity-resolution` | **Yes** | Ensembl ID, UniProt, ChEMBL, collision filters |
| Target dossier | `target-intelligence` | **Yes** | Structure, function, expression, variants, disease, druggability |
| Drug dossier(s) | `drug-intelligence` | Preferred | Chemistry, ADMET, safety, clinical, regulatory |
| Literature evidence | `deep-research` | Optional | Systematic evidence with T1-T4 grading |
| Disease context | User input | Optional | Focuses scoring on specific indication |
| Modality | User input | Optional | Default: all modalities assessed |

**If upstream dossiers are missing**, prompt the user to run the prerequisite skills first. Do NOT silently re-query — the pipeline ensures data consistency and avoids redundant API calls.
</prerequisites>

<key_principles>
## Key Principles

1. **Consume, don't re-fetch** — Extract scoring data from upstream dossiers. Only query for genuinely new dimensions (pathway redundancy, failed programs, gap-fill).
2. **Every score justified** — Each sub-component score must cite the upstream dossier section or new query that produced it.
3. **Evidence grading** — All evidence labeled T1-T4 per `../shared/references/evidence_grading.md`. Scoring weighted accordingly.
4. **Negative results are data** — Score 0 on a component is valid and must be documented. "No data found" flagged as gap.
5. **Disease-specific when possible** — If disease context provided, tailor scoring (especially Disease Association, Clinical Precedent).
6. **Safety-first flagging** — Critical safety concerns (broad expression, essential gene, known toxicity) flagged prominently in Executive Summary regardless of overall score.
7. **Modality-aware** — Druggability scored per modality when user specifies; otherwise assess all.
8. **Source references** — Every claim cites upstream dossier section or new tool/database query.
</key_principles>

<scoring_framework>
## Scoring Framework (0-100)

| Dimension | Max | Sub-components | Primary Data Source |
|-----------|-----|----------------|---------------------|
| **Disease Association** | 30 | Genetic (10) + Literature (10) + Pathway (10) | Target dossier Sec 8 |
| **Druggability** | 25 | Structural (10) + Chemical (10) + Target Class (5) | Target dossier Sec 9 + Drug dossier Sec 3 |
| **Safety** | 20 | Expression (5) + Genetic Liability (10) + ADRs (5) | Target dossier Sec 10 + Drug dossier Sec 6 |
| **Clinical Precedent** | 15 | FDA status, trials, failed program penalties | Drug dossier Sec 5 + **new queries** |
| **Validation Evidence** | 10 | Functional (5) + Disease Models (5) | Target dossier Sec 7 + **gap-fill** |

### Sub-Component Scoring Rules

**Disease Association (0-30):**

| Sub-component | Points | Criteria |
|---------------|--------|----------|
| Genetic (0-10) | 6 | GWAS hits for specific disease (+3/locus, max 6) |
| | +2 | Rare variant evidence (ClinVar pathogenic) |
| | +2 | Somatic mutations in disease / pLI > 0.9 |
| Literature (0-10) | 10/7/5/3/0 | >100 / 50-100 / 10-50 / 1-10 / 0 pubs on target+disease |
| Pathway (0-10) | 10/7/4/1 | OT overall score >0.8 / 0.5-0.8 / 0.2-0.5 / <0.2 |

**Druggability (0-25):**

| Sub-component | Points | Criteria |
|---------------|--------|----------|
| Structural (0-10) | 10 | High-res structure with ligand-bound pocket |
| | 7 | Structure available, pocket predicted |
| | 4 | AlphaFold model only |
| | 1 | No structural data |
| Chemical (0-10) | 10 | Approved drug exists for target |
| | 7 | Clinical compounds (pChEMBL >= 6.0) |
| | 4 | Hit-stage compounds only |
| | 1 | No chemical matter |
| Target Class (0-5) | 5/3/1 | Validated family (kinase, GPCR) / Emerging / Novel |

**Safety (0-20):**

| Sub-component | Points | Criteria |
|---------------|--------|----------|
| Expression (0-5) | 5 | Selective expression (target tissue >> others) |
| | 3 | Moderate selectivity |
| | 1 | Broad/ubiquitous expression |
| Genetic Liability (0-10) | 10 | KO viable, no severe phenotype |
| | 6 | KO viable with manageable phenotype |
| | 3 | KO lethal or severe phenotype |
| | 0 | Essential gene (DepMap highly dependent) |
| ADRs (0-5) | 5 | No known ADRs from target modulation |
| | 3 | Mild/manageable ADRs |
| | 1 | Serious ADRs documented |

**Clinical Precedent (0-15):**

| Scenario | Points | Adjustment |
|----------|--------|------------|
| FDA-approved drug for this target+disease | 15 | — |
| FDA-approved drug for target, different disease | 12 | — |
| Phase III trial active | 10 | — |
| Phase II trial active | 8 | — |
| Phase I trial active | 5 | — |
| Preclinical compounds only | 3 | — |
| No precedent (novel target) | 0 | — |
| Failed Phase III (efficacy) | — | -5 penalty |
| Failed Phase III (safety) | — | -3 penalty (also hits Safety) |

**Validation Evidence (0-10):**

| Sub-component | Points | Criteria |
|---------------|--------|----------|
| Functional (0-5) | 5 | CRISPR/siRNA with rescue + phenotype |
| | 3 | Knockdown with phenotype |
| | 1 | Biochemical assay only |
| Disease Models (0-5) | 5 | In vivo efficacy in disease model |
| | 3 | Cell-based disease model |
| | 1 | Computational prediction only |

### Priority Tiers

| Score | Tier | Label | Recommendation |
|-------|------|-------|----------------|
| 80-100 | T1 | **GO** | Highly validated — proceed with confidence |
| 60-79 | T2 | **CONDITIONAL** | Good target — address identified gaps before commitment |
| 40-59 | T3 | **CAUTION** | Moderate risk — significant validation needed |
| 0-39 | T4 | **NO-GO** | High risk — consider alternatives |

### Modality Assessment Table

When user provides modality preference or when assessing all modalities:

| Modality | Key Factors | Favorable Indicators | Unfavorable Indicators |
|----------|-------------|---------------------|----------------------|
| Small molecule | Binding pocket, selectivity, oral bioavailability | Defined pocket, chemical matter exists | No pocket, disordered regions |
| Antibody | Extracellular domain, epitope accessibility | Surface protein, known epitopes | Intracellular target |
| PROTAC | E3 ligase proximity, linker space | Known binder + accessible lysines | No chemical handle |
| Gene therapy | Genetic basis, delivery route | Monogenic, accessible tissue | Polygenic, CNS target |
| Oligonucleotide | mRNA accessibility, tissue delivery | Liver target, clear splice site | Ubiquitous expression |

</scoring_framework>

<workflow>
## Workflow

### Stage 1: Report Init & Dossier Intake

**Objective:** Create report file, validate upstream dossiers present, extract scoring-relevant data points.

**Steps:**
1. Create report file: `{target}_{disease}_validation.md` (or `{target}_validation.md` if no disease)
2. Validate required inputs:
   - Identity table from `entity-resolution` — extract Ensembl ID, UniProt, gene symbol, collision risk
   - Target dossier from `target-intelligence` — confirm 12-section report exists
   - Drug dossier(s) from `drug-intelligence` — note if missing (flag as gap)
3. Extract scoring-relevant data points from upstream dossiers into working notes:
   - From target dossier: OT disease scores, structure data, expression profile, variant data, druggability assessment, safety signals
   - From drug dossier: clinical stage, ADMET profile, FAERS safety, mechanism, chemical properties
4. Record disease context and modality preference (if provided)
5. Initialize scorecard with all components at 0

**Exit Criteria:**
- [ ] Report file created with template sections
- [ ] All available upstream dossiers located and validated
- [ ] Scoring data points extracted to working notes
- [ ] Missing dossiers flagged as gaps

---

### Stage 2: Disease Association (0-30) + Druggability (0-25) Scoring

**Objective:** Score the two largest dimensions using upstream data + targeted gap-fill.

**Steps:**

**Disease Association (0-30):**
1. Extract from target dossier Section 8 (Disease Associations):
   - OT overall association score -> Pathway sub-score
   - Genetic evidence (GWAS, ClinVar, somatic) -> Genetic sub-score
   - Literature count for target+disease -> Literature sub-score
2. **Gap-fill** (genuinely new queries — not in upstream):
   - `CTD_get_gene_diseases` (capability: `target_biology.disease_complement`) — complementary disease associations from Comparative Toxicogenomics Database
   - `GO_get_annotations_for_gene` (capability: `interactions.go_annotations`) — Gene Ontology annotations for pathway evidence
3. Score each sub-component per scoring rules above
4. Apply evidence tier weighting: T1=full, T2=70-80%, T3=40-60%, T4=10-20%

**Druggability (0-25):**
1. Extract from target dossier Section 9 (Druggability):
   - OT tractability assessment -> Structural sub-score
   - Pharos TDL, DGIdb categories -> Target Class sub-score
2. Extract from drug dossier Section 3 (Mechanism & Targets):
   - Chemical matter availability -> Chemical sub-score
   - Bioactivity data (pChEMBL values)
3. If modality specified, focus structural assessment on modality-specific factors
4. Score each sub-component

**Exit Criteria:**
- [ ] Disease Association score assigned (X/30) with justification
- [ ] Druggability score assigned (X/25) with justification
- [ ] Gap-fill queries completed (CTD, GO)
- [ ] All sub-component scores documented with evidence tier

---

### Stage 3: Safety (0-20) + Clinical Precedent (0-15) + Validation Evidence (0-10)

**Objective:** Score remaining three dimensions. Clinical precedent requires new queries for failed programs.

**Steps:**

**Safety (0-20):**
1. Extract from target dossier Section 10 (Safety & Selectivity):
   - Expression selectivity (GTEx/HPA data) -> Expression sub-score
   - KO phenotype, essentiality (DepMap, gnomAD pLI) -> Genetic Liability sub-score
2. Extract from drug dossier Section 6 (Safety):
   - FAERS adverse events, known ADRs -> ADRs sub-score
3. **Gap-fill** if DepMap data missing from upstream:
   - `DepMap_get_gene_dependencies` / `DepMap_search_genes` (capability: `genetic_variation.essentiality`)
4. Score each sub-component; flag critical safety concerns for Executive Summary

**Clinical Precedent (0-15):**
1. Extract from drug dossier Section 5 (Clinical Development):
   - Highest clinical stage achieved
   - FDA approval status
2. **New queries** (genuinely new — failed program analysis not in upstream):
   - `search_clinical_trials` (capability: `drug_data.clinical`) — search for terminated/failed trials on this target
   - Parameter: `query_term` (NOT `query` — see `known_param_corrections.md`)
   - Look for: terminated trials, failed Phase III, safety-related withdrawals
3. Apply failed program penalties: -5 for efficacy failure, -3 for safety failure
4. Score clinical precedent

**Validation Evidence (0-10):**
1. Extract from target dossier Section 7 (Interactions & Pathways):
   - Functional studies (CRISPR, siRNA) -> Functional sub-score
   - Disease model data -> Disease Models sub-score
2. Extract from literature evidence (if `deep-research` was run):
   - T1/T2 evidence counts for functional validation
3. Score validation evidence

**Exit Criteria:**
- [ ] Safety score assigned (X/20) with justification
- [ ] Clinical Precedent score assigned (X/15) with justification
- [ ] Failed program search completed
- [ ] Validation Evidence score assigned (X/10) with justification
- [ ] Critical safety flags identified (if any)

---

### Stage 4: Pathway Redundancy & Modality Assessment

**Objective:** Assess compensation risk and modality-specific feasibility (genuinely new analysis not in upstream).

**Steps:**

**Pathway Redundancy (compensation risk):**
1. Extract pathway context from target dossier Section 7:
   - Reactome pathways, KEGG pathways
   - PPI network (STRING interactions)
2. Assess compensation risk:
   - **Low risk**: Target is sole pathway member or rate-limiting step
   - **Medium risk**: Paralogs exist but divergent function
   - **High risk**: Multiple redundant family members with overlapping function
3. Document paralog analysis: list family members, % sequence identity, overlapping substrates/interactions
4. If HIGH compensation risk, note in Executive Summary as key risk factor

**Modality Assessment:**
1. If user specified modality: score feasibility using Modality Assessment Table
2. If no modality specified: assess top 2-3 feasible modalities
3. For each modality, document:
   - Feasibility (High/Medium/Low)
   - Key enablers (existing structures, chemical matter, accessibility)
   - Key barriers (intracellular, no pocket, delivery challenges)
4. Recommend optimal modality with rationale

**Exit Criteria:**
- [ ] Compensation risk assessed (Low/Medium/High) with justification
- [ ] Paralog analysis documented
- [ ] Modality feasibility assessed
- [ ] Optimal modality recommended

---

### Stage 5: Synthesis — Scorecard, Roadmap & Audit

**Objective:** Compute composite score, assign tier, generate validation roadmap, run completeness audit.

**Steps:**
1. **Compute composite score:**
   - Sum all 5 dimension scores
   - Assign priority tier (T1-T4)
   - Determine GO/NO-GO recommendation
2. **Generate scorecard table** (12-component breakdown)
3. **Write Executive Summary:**
   - Composite score and tier
   - GO/NO-GO with 1-sentence rationale
   - Top 3 strengths
   - Top 3 risks/gaps
   - Critical safety flags (if any)
4. **Validation Roadmap** — prioritized next steps:
   - Experiments to close evidence gaps
   - Tool compounds to acquire/synthesize
   - Biomarkers to develop
   - Risk mitigation strategies
5. **Completeness Audit:**
   - List all 12 scoring components with data source status
   - Flag components scored from T3/T4 evidence only
   - Calculate data completeness percentage
   - List upstream dossier sections consumed

**Exit Criteria:**
- [ ] Composite score computed
- [ ] Priority tier assigned
- [ ] Executive Summary written
- [ ] Validation Roadmap with actionable next steps
- [ ] Completeness audit shows ≥80% components with T1/T2 evidence

</workflow>

<report_template>
## Report Template (9 Sections)

```markdown
# Target Validation Report: {TARGET} — {DISEASE}

## 1. Executive Summary

**Target:** {gene_symbol} ({full_name})
**Disease Context:** {disease} (or "General assessment" if none)
**Modality:** {modality} (or "All assessed")

### Validation Score: {XX}/100 — Tier {N}: {LABEL}

**Recommendation:** {GO / CONDITIONAL / CAUTION / NO-GO}
{1-sentence rationale}

**Key Strengths:**
1. {strength_1} [T{n}]
2. {strength_2} [T{n}]
3. {strength_3} [T{n}]

**Key Risks:**
1. {risk_1}
2. {risk_2}
3. {risk_3}

{If critical safety flags: **SAFETY FLAG:** {description}}

---

## 2. Validation Scorecard

| Dimension | Sub-component | Score | Max | Evidence Tier | Source |
|-----------|---------------|-------|-----|---------------|--------|
| Disease Association | Genetic | X | 10 | T{n} | Target dossier Sec 8 |
| Disease Association | Literature | X | 10 | T{n} | Target dossier Sec 8 |
| Disease Association | Pathway | X | 10 | T{n} | Target dossier Sec 8 + CTD |
| Druggability | Structural | X | 10 | T{n} | Target dossier Sec 9 |
| Druggability | Chemical | X | 10 | T{n} | Drug dossier Sec 3 |
| Druggability | Target Class | X | 5 | T{n} | Target dossier Sec 9 |
| Safety | Expression | X | 5 | T{n} | Target dossier Sec 10 |
| Safety | Genetic Liability | X | 10 | T{n} | Target dossier Sec 10 |
| Safety | ADRs | X | 5 | T{n} | Drug dossier Sec 6 |
| Clinical Precedent | — | X | 15 | T{n} | Drug dossier Sec 5 + trials |
| Validation Evidence | Functional | X | 5 | T{n} | Target dossier Sec 7 |
| Validation Evidence | Disease Models | X | 5 | T{n} | Target dossier Sec 7 |
| **TOTAL** | | **XX** | **100** | | |

---

## 3. Disease Association Evidence

{Scoring justification for all 3 sub-components}
{References to target dossier Section 8}
{Gap-fill results from CTD, GO annotations}

---

## 4. Druggability & Chemical Matter

{Merged assessment: structural tractability + chemical matter + target class}
{References to target dossier Section 9 + drug dossier Section 3}
{Modality-specific feasibility if assessed}

---

## 5. Clinical Precedent

{FDA status, trial landscape}
{Failed program analysis with penalties applied}
{Clinical trial search results}

---

## 6. Safety Profile

{Expression selectivity assessment}
{Genetic liability (KO phenotype, essentiality)}
{ADR summary from FAERS/known safety signals}
{References to target dossier Section 10 + drug dossier Section 6}

---

## 7. Pathway Redundancy & Validation Evidence

**Compensation Risk:** {Low/Medium/High}
{Paralog analysis, pathway redundancy assessment}

**Validation Evidence:**
{Functional studies summary}
{Disease model evidence}

---

## 8. Validation Roadmap

### Priority Experiments
1. {experiment_1} — addresses {gap}
2. {experiment_2} — validates {finding}

### Tool Compounds
- {compound recommendation with rationale}

### Biomarkers
- {biomarker_1} for {purpose}

### Risk Mitigation
- {strategy_1} for {risk}

---

## 9. Completeness & Data Sources

### Audit Checklist

| Component | Data Available | Evidence Tier | Source |
|-----------|---------------|---------------|--------|
| Disease Association - Genetic | Yes/No | T{n} | {source} |
| Disease Association - Literature | Yes/No | T{n} | {source} |
| Disease Association - Pathway | Yes/No | T{n} | {source} |
| Druggability - Structural | Yes/No | T{n} | {source} |
| Druggability - Chemical | Yes/No | T{n} | {source} |
| Druggability - Target Class | Yes/No | T{n} | {source} |
| Safety - Expression | Yes/No | T{n} | {source} |
| Safety - Genetic Liability | Yes/No | T{n} | {source} |
| Safety - ADRs | Yes/No | T{n} | {source} |
| Clinical Precedent | Yes/No | T{n} | {source} |
| Validation - Functional | Yes/No | T{n} | {source} |
| Validation - Disease Models | Yes/No | T{n} | {source} |

**Data Completeness:** {X}/12 components with data ({Y}%)
**T1/T2 Coverage:** {Z}/12 components with T1 or T2 evidence ({W}%)

### Upstream Dossiers Consumed
- entity-resolution: {date}
- target-intelligence: {date}, {N} sections
- drug-intelligence: {date}, {N} sections (or "Not available")
- deep-research: {date} (or "Not available")
```

</report_template>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `entity-resolution` | **Prerequisite** — provides resolved IDs and collision filters |
| `target-intelligence` | **Required upstream** — provides target dossier (12 sections) |
| `drug-intelligence` | **Preferred upstream** — provides drug dossier (10 sections) |
| `deep-research` | **Optional upstream** — provides systematic evidence with T1-T4 grading |
| `scientific-writing` | **Downstream** — write up validation findings for publication |
| `executive-summary` | **Downstream** — condense scorecard for stakeholder communication |

**Shared References:**
- `../shared/references/evidence_grading.md` — T1-T4 tier definitions and scoring weights
- `../shared/tool-lookup.yaml` — capability-to-tool mapping for gap-fill queries

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.
</cross_references>

## Fork-return contract

This skill runs in a forked subagent context (`context: fork`). The fork executes all 5 stages internally — dossier intake (target-intelligence + drug-intelligence + entity-resolution), disease-association extraction, druggability scoring, safety synthesis, pathway-redundancy analysis, and the validation-roadmap write — and returns **only a compact summary** to the calling conversation. The full upstream dossier text, intermediate scoring tables, pathway-redundancy intermediate calculations, and gap-fill query transcripts **stay inside the fork**. Pre-fork main-context cost per validation has been observed at 40k–100k+ tokens (full target dossier + drug dossier + entity table + gap-fill MCP responses); the post-fork target is **≤ 1.5k tokens per validation**.

The fork's final message to the caller is a single JSON object capped at ~800 tokens. Emit it verbatim as the last content of the response, fenced as ```json:

```jsonc
{
  "validation_id": "<target>_<disease_slug-or-empty>",
  "validation_dir": "research/validations/<slug>/",
  "scorecard_path": "<{target}_{disease}_validation.md path>",
  "target_id": "",
  "disease": "",
  "upstream_dossiers": {
    "target_intelligence_path": "",
    "drug_intelligence_paths": [],
    "entity_resolution_path": ""
  },
  "score": {
    "total_0_to_100": 0,
    "dimensions": {
      "disease_association": 0, "druggability": 0, "safety": 0,
      "clinical_precedent": 0, "pathway_redundancy": 0
    }
  },
  "recommendation": "GO | CONDITIONAL_GO | NO_GO | INSUFFICIENT_DATA",
  "evidence_grading_distribution": { "T1": 0, "T2": 0, "T3": 0, "T4": 0 },
  "validation_roadmap_steps": 0,
  "headline": "<≤140 chars: 1-line verdict; e.g. 'BRCA1 / breast cancer — GO (score 78); strong clinical precedent; primary risk: pathway redundancy with PARP'>",
  "next_actions": [ "<≤2 short suggestions or empty array>" ]
}
```

**Required fields:** `validation_id`, `validation_dir`, `scorecard_path`, `target_id`, `upstream_dossiers` (paths the caller passed in for trace), `score.total_0_to_100`, `score.dimensions` (the 5 weighted dimensions producing the total — must sum per the skill's documented weights), `recommendation` (one of the 4 enum values), `headline`. `disease` is empty string for target-only validations (no indication specified). `validation_roadmap_steps` is the count of items in the persisted roadmap; the roadmap content itself stays in the scorecard markdown.

**Forbidden in fork return:** full target/drug dossier section quotes, intermediate scoring tables, pathway-redundancy adjacency matrices, gap-fill MCP query transcripts, disease-association T1-T4 evidence excerpts, validation-roadmap step prose. All of that lives in the persisted artifacts under `validation_dir` and the rendered `{target}_{disease}_validation.md`. The caller follows up with targeted reads — for example, `!\`grep -A 30 "## Validation Roadmap" <scorecard_path>\`` or `!\`jq '.score.dimensions' research/validations/<slug>/audit.json\`` — to surface specific scorecard sections on demand at zero token cost in the main context.

**If validation cannot complete:** still return the JSON shape with whatever dimension scores were computed (others as `null`), `recommendation: "INSUFFICIENT_DATA"`, and a `next_actions` entry explaining what blocked completion (e.g., `"resume after target-intelligence dossier completes Section 9: Druggability"`, `"drug-intelligence dossier missing FAERS section — required for safety dimension"`). Partial state remains in `validation_dir` for follow-up runs.
