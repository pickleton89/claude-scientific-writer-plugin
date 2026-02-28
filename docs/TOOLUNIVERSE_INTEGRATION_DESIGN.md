# ToolUniverse Integration Design

> Design document for integrating ToolUniverse capabilities into the
> claude-scientific-writer skill ecosystem.
>
> **Date:** 2026-02-27
> **Status:** Draft / Discussion

---

## Table of Contents

1. [Current System Overview](#1-current-system-overview)
2. [ToolUniverse Background](#2-tooluniverse-background)
3. [Gap Analysis: What ToolUniverse Adds](#3-gap-analysis-what-tooluniverse-adds)
4. [The Four ToolUniverse Skills](#4-the-four-tooluniverse-skills)
5. [Integration Strategy](#5-integration-strategy)
6. [MCP Server as Cross-Cutting Data Layer](#6-mcp-server-as-cross-cutting-data-layer)
7. [Implementation Roadmap](#7-implementation-roadmap)

---

## 1. Current System Overview

### 1.1 Skill Graph Architecture

The claude-scientific-writer plugin organizes capabilities as a **directed graph
of composable skills**. Each skill is a focused node (~200-500 lines) that
follows a standardized template (`SKILL_TEMPLATE.md`) with:

- **YAML frontmatter** — name, version, triggers, allowed tools
- **XML semantic tags** — `<overview>`, `<when_to_use>`, `<decision_framework>`,
  `<workflow>`, `<success_criteria>`, `<scope>`, `<anti_patterns>`, `<templates>`,
  `<cross_references>`, `<references>`
- **Numbered workflow stages** with explicit exit criteria
- **Quality scoring** across 8 dimensions (target: 8.5/10)

Skills connect through **typed wikilink edges**:

| Edge Type | Direction | Meaning |
|-----------|-----------|---------|
| **Extends** | Parent → Child | Inherits principles from a foundational skill |
| **Uses (Input From)** | Source → Consumer | Skill receives data/output from another |
| **Feeds (Output To)** | Producer → Downstream | Skill provides output to another |
| **Related** | Bidirectional | Non-directional relationship |

The `SKILL_ROUTER.md` acts as traversal logic — decision trees that route user
intent to the correct skill(s) and compose multi-skill workflows.

### 1.2 Current Skill Inventory (27 skills)

**Research & Analysis:**
- `paper-search` — Multi-database paper finding (PubMed, bioRxiv, Semantic Scholar, Google Scholar)
- `literature-review` — Systematic reviews with PRISMA compliance
- `research-paper-summarizer` — Deep paper analysis
- `hypothesis-generation` — Testable hypothesis formulation (8-stage workflow)
- `statistical-analysis` — Quantitative methods and power analysis
- `peer-review` — Manuscript evaluation and critical analysis
- `citation-management` — BibTeX formatting and validation

**Writing & Documents:**
- `scientific-writing` — Manuscript composition (central hub node)
- `venue-templates` — Journal-specific formatting
- `executive-summary` — Concise summaries
- `code-documentation` — Docstrings and technical docs

**Visual & Presentation:**
- `plotting-libraries` — matplotlib, seaborn, plotly, ggplot2
- `scientific-schematics` — Pathway diagrams, mechanisms
- `visual-design` — Design principles and publication specs
- `oligon-brand` — Brand tokens and identity
- `paperbanana` — Text-to-visual figure generation
- `generate-image` — AI image generation
- `scientific-slides` — Presentation creation
- `research-posters` — Poster layout and design

**Infrastructure & Export:**
- `reproducible-research` — Environment management
- `markitdown` — Format conversion
- `markdown-to-pdf` — PDF export
- `paper-2-web` — Web conversion
- `document-skills` (docx, pdf, pptx, xlsx) — Office format generation
- `brand-interface` — Interface contract for brand integration
- `shared` — Common utilities

### 1.3 Current Data Sources

The system currently accesses scientific data through:

| Source | Access Method | Coverage |
|--------|-------------|----------|
| PubMed | MCP server + paper-search script | Biomedical literature |
| Open Targets | MCP server (GraphQL) | Target-disease associations, genetics |
| Consensus | MCP server | 200M+ papers, semantic search |
| Zotero | MCP server | Personal library management |
| Readwise Reader | MCP server | Reading list and highlights |
| Semantic Scholar | paper-search script (API) | Cross-domain papers |
| bioRxiv/medRxiv | paper-search script (API) | Preprints |
| Google Scholar | paper-search script (scraping) | Broad coverage |

### 1.4 The Research Workflow Gap

The current skill graph excels at **literature-centric research** (finding papers,
reviewing them, writing about them) and **output production** (figures, documents,
presentations). The router's research decision tree reflects this:

```
User needs research support
├─ Find papers → paper-search / literature-review
├─ Manage citations → citation-management
├─ Evaluate a paper → peer-review
└─ Analyze evidence → peer-review
```

What is **missing** is a structured path for **data-driven biological research**:
target profiling, drug characterization, pathway analysis, computational
validation scoring. These workflows require querying dozens of specialized
databases (ChEMBL, DrugBank, UniProt, STRING, gnomAD, PDB, AlphaFold, GTEx,
DepMap, etc.) that are not currently accessible.

---

## 2. ToolUniverse Background

### 2.1 What It Is

ToolUniverse is an open-source ecosystem from the Zitnik Lab at Harvard Medical
School that wraps any LLM into an "AI scientist" by providing access to 600+
scientific tools.

- **Paper:** Gao et al., "Democratizing AI scientists using ToolUniverse"
  (arXiv:2509.23426v2, October 2025)
- **Website:** https://aiscientist.tools
- **Repository:** https://github.com/mims-harvard/ToolUniverse
- **Package:** `pip install tooluniverse`

### 2.2 Tool Categories

ToolUniverse organizes 600+ tools across these categories:

| Category | Examples |
|----------|---------|
| **ML Models** | Foundation models, Boltz-2 (structure prediction), ADMET-AI |
| **Domain Knowledge** | ChEMBL, DrugBank, PubChem, UniProt, InterPro, gnomAD, ClinVar, KEGG, Reactome, STRING, GTEx, HPA, DepMap, PDB, AlphaFold |
| **Scientific Packages** | Bioinformatic libraries, data analysis toolkits, simulators |
| **Agents** | Research planning, computational biology, literature search, data analysis |
| **Visualization** | Dashboards, plot generators, visual reporting |
| **Workflows** | Orchestration, scheduling, pipelines |
| **Experimentation** | Protocol generators, ELN/LIMS integration |
| **Feedback & Safety** | Privacy guidelines, human-in-the-loop tools |

### 2.3 AI-Tool Interaction Protocol

ToolUniverse defines a standardized protocol (analogous to HTTP) with two
core operations:

1. **Find Tool** — Maps natural-language descriptions to formal tool
   specifications. Supports keyword, LLM, and embedding-based search.
2. **Call Tool** — Executes a tool with specified arguments and returns
   results (text, JSON, embeddings, etc.)

The protocol has three elements:
- **Specification schema** — Common format for describing each tool's function,
  parameters, and outputs
- **Interaction schema** — Uniform request encoding (function calls with tool
  names and arguments)
- **Communication methods** — Local Python execution or remote MCP requests

### 2.4 MCP Server Integration

ToolUniverse provides a **Model Context Protocol (MCP) server** for remote tool
access, compatible with Claude Code, Claude Desktop, and Gemini CLI. This means
the entire 600+ tool catalog can be exposed as MCP tools alongside our existing
Open Targets, PubMed, and Consensus MCPs.

### 2.5 Case Study: Hypercholesterolemia Drug Discovery

The paper demonstrates a complete drug discovery workflow:

1. **Target identification** — Literature mining, target profiling, and tissue
   expression analysis → prioritized HMG-CoA reductase
2. **In silico screening** — DrugBank screening by target/indication → selected
   lovastatin, identified off-target limitations
3. **Compound optimization** — ChEMBL structural analogs → Boltz-2 binding
   prediction → ADMET-AI optimization
4. **Regulatory assessment** — PubChem patent search → confirmed novel candidate

Result: Identified pravastatin (known improvement) and a novel candidate
(CHEMBL2347006/CHEMBL3970138) with higher predicted binding affinity, reduced
BBB penetrance, and improved oral bioavailability.

---

## 3. Gap Analysis: What ToolUniverse Adds

### 3.1 Data Source Expansion

Our current MCPs cover ~5 data sources. ToolUniverse adds access to 500+
scientific tools across databases we cannot currently reach:

| Domain | New Data Sources via ToolUniverse | Currently Available |
|--------|----------------------------------|-------------------|
| **Drug Chemistry** | ChEMBL, DrugBank, PubChem, BindingDB, ChemSpider | None |
| **Target Biology** | UniProt, InterPro, Pfam, AlphaFold, PDB, ProteinsPlus | Open Targets (partial) |
| **Expression** | GTEx, HPA (tissue + single-cell) | None |
| **Genetic Variation** | gnomAD, ClinVar | Open Targets (partial) |
| **Networks & Pathways** | STRING, IntAct, Reactome, KEGG | None |
| **Functional Genomics** | DepMap (essentiality screens) | None |
| **Clinical** | ClinicalTrials.gov, FDA databases, SIDER | None |
| **ML/Prediction** | Boltz-2, ADMET-AI | None |
| **Literature** | Europe PMC, OpenAlex, Semantic Scholar | PubMed, Consensus |

### 3.2 Workflow Capability Expansion

Beyond raw data access, ToolUniverse enables workflow patterns that don't exist
in the current skill graph:

| Capability | Current State | With ToolUniverse |
|-----------|--------------|-------------------|
| Target profiling | Manual literature search | Structured data from UniProt, PDB, GTEx, STRING |
| Drug characterization | Not available | Full compound profiles from ChEMBL, DrugBank, PubChem |
| Druggability assessment | Not available | Tractability scores, structure analysis, chemical matter inventory |
| Computational validation | Not available | Quantitative scoring (0-100) with multi-source evidence |
| ADMET prediction | Not available | ML-based predictions via ADMET-AI |
| Structure prediction | Not available | Boltz-2 binding affinity, AlphaFold structures |
| Safety profiling | Not available | Expression filters, KO phenotypes, ADR databases |

### 3.3 Overlap Assessment

| Our Existing Capability | ToolUniverse Equivalent | Relationship |
|------------------------|------------------------|-------------|
| `paper-search` (5 databases) | Literature search agents (Europe PMC, OpenAlex, Semantic Scholar) | **Complementary** — different databases, some overlap on Semantic Scholar |
| `literature-review` (PRISMA) | Literature deep-research (T1-T4 grading) | **Complementary** — our skill does systematic review methodology; ToolUniverse adds evidence grading and collision-aware search |
| `hypothesis-generation` | Research planning agents | **Complementary** — our skill does hypothesis formulation; ToolUniverse provides data to feed hypotheses |
| Open Targets MCP | Open Targets tools in ToolUniverse | **Redundant** — keep our existing MCP, skip ToolUniverse's OT tools |
| PubMed MCP | PubMed tools in ToolUniverse | **Redundant** — keep our existing MCP |

---

## 4. The Four ToolUniverse Skills

Four ToolUniverse-derived skill documents exist in `docs/` as reference
material. These are **monolithic procedural pipelines** (1,000-1,800 lines each)
that encode specific `tu.tools.X()` API calls. They do not conform to our
skill template and are not directly usable in our graph-based architecture.

However, they contain valuable **workflow logic, tool mappings, and scoring
frameworks** that inform our integration design.

### 4.1 Drug Research (`docs/tooluniverse-drug-research/SKILL.md`)

~1,800 lines. Comprehensive drug profiling using 50+ ToolUniverse tools.

**Capability breakdown:**
- Compound disambiguation (ChemSpider, PubChem, DrugBank, ChEMBL)
- Chemical identity and physicochemical properties
- Pharmacology: molecular targets, mechanism of action
- Clinical development: trials, approvals, indications
- Safety and toxicity: adverse events, pharmacogenomics
- Pharmacokinetics: ADMET, metabolism, drug-drug interactions

**Valuable patterns to extract:**
- Report-first approach (create file with placeholders, then populate)
- Multi-source compound disambiguation workflow
- Safety section structure

### 4.2 Target Research (`docs/tooluniverse-target-research/SKILL.md`)

~1,500 lines. Nine parallel research paths for comprehensive target intelligence.

**Capability breakdown:**
- Target identity and disambiguation (UniProt, Ensembl, MyGene, HGNC)
- Protein structure and domains (PDB, AlphaFold, InterPro)
- Subcellular localization and expression (GTEx, HPA)
- Protein-protein interactions (STRING, IntAct)
- Pathway context (Reactome, KEGG, GO)
- Genetic variants and constraints (gnomAD, ClinVar, DepMap)
- Disease associations (Open Targets, GWAS)
- Drug interactions and chemical matter (ChEMBL, BindingDB)
- Literature and research landscape

**Valuable patterns to extract:**
- Evidence grading tiers (T1-T4: Mechanistic/Functional/Association/Mention)
- Collision-aware literature searching
- Parallel research path architecture
- Completeness auditing

### 4.3 Drug-Target Validation (`docs/tooluniverse-drug-target-validation/SKILL.md`)

~1,207 lines. Ten-phase computational target validation pipeline with
quantitative scoring.

**Capability breakdown (scoring components):**

| Component | Weight | Evidence Sources |
|-----------|--------|-----------------|
| Disease Association | 0-30 | Genetic (0-10), Literature (0-10), Pathway (0-10) |
| Druggability | 0-25 | Structure (0-10), Chemical matter (0-10), Target class (0-5) |
| Safety | 0-20 | Expression (0-5), Genetic liability (0-10), ADRs (0-5) |
| Clinical Precedent | 0-15 | FDA status, trial landscape |
| Validation Evidence | 0-10 | Functional (0-5), Model organisms (0-5) |
| **Total** | **0-100** | **GO/NO-GO recommendation** |

**Priority tiers:** Tier 1 (80-100), Tier 2 (60-79), Tier 3 (40-59), Tier 4 (0-39)

**Valuable patterns to extract:**
- Quantitative scoring framework with weighted components
- GO/NO-GO decision logic
- Parameter corrections table for known API quirks
- Validation roadmap generation

### 4.4 Literature Deep Research (`docs/tooluniverse-literature-deep-research/SKILL.md`)

~1,051 lines. Enhanced literature research with target disambiguation and
evidence grading.

**Capability breakdown:**
- Mode selection: factoid / mini-review / full deep research
- Target disambiguation with collision detection
- High-precision seed queries → citation network expansion
- T1-T4 evidence grading (shared with target-research)
- Three-tier full-text verification (Europe PMC auto-snippet → Semantic Scholar
  manual → fallback download)
- 15-section mandatory report template with completeness checklist

**Valuable patterns to extract:**
- T1-T4 evidence grading system
- Collision-aware search (critical for ambiguous gene symbols)
- Three-tier full-text retrieval strategy
- Mode-based workflow selection (factoid vs. deep research)

### 4.5 Cross-Cutting Patterns

These patterns appear in multiple ToolUniverse skills and should become shared
capabilities in our decomposition:

| Pattern | Appears In | Proposed Home |
|---------|-----------|---------------|
| Entity disambiguation (gene/protein/drug/disease → canonical IDs) | All 4 | `entity-resolution` skill |
| Evidence grading (T1-T4) | target-research, literature-deep-research, drug-target-validation | `evidence-grading` utility or enhancement to `literature-review` |
| Collision-aware search | target-research, literature-deep-research | `entity-resolution` + `literature-review` enhancement |
| Expression context as safety filter | target-research, drug-target-validation | `target-intelligence` skill |
| Report-first approach | All 4 | Already fits our template's `<templates>` tag |
| Completeness checklist | drug-target-validation, literature-deep-research | Standard `<success_criteria>` in each skill |

---

## 5. Integration Strategy

### 5.1 Design Principles

1. **ToolUniverse MCP as shared data layer** — Install once, all skills benefit.
   Analogous to how `oligon-brand` tokens are a shared resource for visual skills.
2. **Decompose, don't import** — Extract workflow logic and scoring frameworks
   from the four reference skills; do not port the monolithic procedures.
3. **Composable graph nodes** — Each new skill follows `SKILL_TEMPLATE.md`,
   connects via wikilink cross-references, and is routable by `SKILL_ROUTER.md`.
4. **Tool indirection via lookup** — Skills reference capabilities (e.g., "get
   protein domains"), not raw tool names. A shared lookup maps capabilities to
   ToolUniverse tools.
5. **Enhance existing skills where possible** — Add new capabilities to
   `literature-review` rather than creating a parallel skill.

### 5.2 Proposed Decomposition

The four monolithic skills decompose into **5 new/enhanced graph nodes** plus
a **shared tool-lookup reference**:

```
┌─────────────────────────── DATA ACCESS LAYER ───────────────────────────┐
│  ToolUniverse MCP │ Open Targets MCP │ PubMed MCP │ Consensus │ Zotero │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
           ┌──────────────┐ ┌──────────┐ ┌──────────────┐
           │   entity-    │ │ evidence │ │   tool-      │
           │  resolution  │ │ grading  │ │  lookup      │
           │  (utility)   │ │ (utility)│ │  (reference) │
           └──────┬───────┘ └────┬─────┘ └──────────────┘
                  │              │
        ┌─────────┼──────────┬───┘
        ▼         ▼          ▼
  ┌───────────┐ ┌──────────┐ ┌─────────────────┐
  │  target-  │ │  drug-   │ │  literature-    │
  │  intel    │ │  intel   │ │  review         │
  │  (NEW)    │ │  (NEW)   │ │  (ENHANCED)     │
  └─────┬─────┘ └────┬─────┘ └────────┬────────┘
        │             │                │
        └──────┬──────┘                │
               ▼                       │
     ┌──────────────────┐              │
     │ target-validation│◄─────────────┘
     │   (integrator)   │
     │   Score: 0-100   │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────┐     ┌───────────────────┐
     │   hypothesis-    │────▶│  scientific-       │
     │   generation     │     │  writing / slides  │
     │   (EXISTING)     │     │  (EXISTING)        │
     └──────────────────┘     └───────────────────┘
```

### 5.3 New Skill Specifications

#### `entity-resolution` (Shared Utility — NEW)

**Purpose:** Resolve gene symbols, protein names, drug names, and disease terms
to canonical identifiers before any research skill proceeds.

**Source material:** Disambiguation phases from all four ToolUniverse skills.

**Scope:**
- Gene/protein → Ensembl ID, UniProt accession, HGNC symbol
- Drug/compound → ChEMBL ID, PubChem CID, DrugBank ID
- Disease → EFO ID, MONDO ID, OMIM
- Collision detection for ambiguous symbols (e.g., "ACE" gene vs. ACE inhibitor)

**Estimated size:** ~150-200 lines

**Cross-references:**
- Feeds → `target-intelligence`, `drug-intelligence`, `literature-review`, `target-validation`
- Uses ← ToolUniverse MCP (disambiguation tools), Open Targets MCP

---

#### `target-intelligence` (Research Node — NEW)

**Purpose:** Comprehensive target profiling — the "know your target" skill.
Assembles a structured target dossier from multiple data sources.

**Source material:** `tooluniverse-target-research` decomposed, excluding
literature (handled by `literature-review`) and validation scoring (handled by
`target-validation`).

**Scope:**
- Protein identity, structure, and domains (UniProt, PDB, AlphaFold, InterPro)
- Expression and localization (GTEx, HPA)
- Protein-protein interactions and complexes (STRING, IntAct)
- Pathway context (Reactome, KEGG, GO)
- Genetic variants and population constraints (gnomAD, ClinVar)
- Disease associations (Open Targets, GWAS)

**Estimated size:** ~350-400 lines

**Cross-references:**
- Uses ← `entity-resolution`
- Feeds → `target-validation`, `hypothesis-generation`, `scientific-writing`
- Related → `drug-intelligence` (shared targets)

---

#### `drug-intelligence` (Research Node — NEW)

**Purpose:** Comprehensive drug/compound profiling — the "know your compound"
skill. Assembles a structured compound dossier.

**Source material:** `tooluniverse-drug-research` decomposed, with clinical
evidence and safety data relevant to the compound.

**Scope:**
- Chemical identity and physicochemical properties (PubChem, ChEMBL, DrugBank)
- Pharmacology: targets, mechanism of action, selectivity
- ADMET properties and metabolism
- Clinical development: trials, approvals, indications
- Safety: adverse events, drug-drug interactions, pharmacogenomics
- Known analogs and SAR

**Estimated size:** ~350-400 lines

**Cross-references:**
- Uses ← `entity-resolution`
- Feeds → `target-validation`, `scientific-writing`
- Related → `target-intelligence` (shared targets)

---

#### `target-validation` (Integrator/Scorer — NEW)

**Purpose:** Quantitative computational target validation. Consumes outputs from
target-intelligence, drug-intelligence, and literature-review to produce a
0-100 validation score with GO/NO-GO recommendation.

**Source material:** `tooluniverse-drug-target-validation` scoring framework.

**Scoring framework:**

| Component | Weight | Sources |
|-----------|--------|---------|
| Disease Association | 0-30 | Genetic evidence (0-10), Literature (0-10), Pathway (0-10) |
| Druggability | 0-25 | Structural tractability (0-10), Chemical matter (0-10), Target class (0-5) |
| Safety | 0-20 | Expression profile (0-5), Genetic liability (0-10), Known ADRs (0-5) |
| Clinical Precedent | 0-15 | FDA approval status, trial landscape |
| Validation Evidence | 0-10 | Functional studies (0-5), Model organisms (0-5) |

**Decision output:**
- Tier 1 (80-100): Strong — proceed to lead optimization
- Tier 2 (60-79): Moderate — address gaps before advancing
- Tier 3 (40-59): Weak — requires significant de-risking
- Tier 4 (0-39): Insufficient — deprioritize or pivot

**Estimated size:** ~300-350 lines

**Cross-references:**
- Uses ← `target-intelligence`, `drug-intelligence`, `literature-review`
- Feeds → `hypothesis-generation`, `scientific-writing`
- Related → `peer-review` (evidence quality standards)

---

#### `literature-review` (ENHANCED — Existing Skill)

**Purpose:** Extend the existing literature-review skill with capabilities
from `tooluniverse-literature-deep-research`.

**Enhancements:**
- **T1-T4 evidence grading** — Classify claims by evidence strength:
  - T1 (Mechanistic): Direct experimental evidence, causal proof
  - T2 (Functional): Functional studies, model organisms
  - T3 (Association): Screen hits, GWAS, correlations
  - T4 (Mention): Reviews, text-mined, peripheral
- **Collision-aware search** — Detect and filter name/symbol ambiguities
  (important for gene symbols that collide with common words)
- **Mode selection** — Factoid (quick answer), mini-review, or full deep research
- **Three-tier full-text verification** — Europe PMC auto-snippet → Semantic
  Scholar manual → fallback download

**Estimated addition:** ~100-150 lines to existing skill

**New cross-references:**
- Uses ← `entity-resolution` (for collision detection)
- Feeds → `target-validation` (evidence-graded findings)

### 5.4 Tool Lookup Reference

A shared reference file (`shared/tool-lookup.yaml`) maps research capabilities
to specific ToolUniverse tools. Skills reference capabilities; the lookup
resolves to tool names. This provides indirection so that tool changes don't
require editing every skill.

```yaml
# shared/tool-lookup.yaml — maps capability to ToolUniverse tools
# Skills reference the capability key; the lookup resolves to tool name(s)

disambiguation:
  gene_to_ensembl:
    tools: [mygene_query, ensembl_lookup]
    fallback: [hgnc_search]
  compound_to_chembl:
    tools: [chembl_molecule_search, pubchem_cid_lookup]
    fallback: [drugbank_search, chemspider_search]
  disease_to_efo:
    tools: [open_targets_disease_search]

target_structure:
  domains:
    tools: [interpro_protein, pfam_search]
  three_d:
    tools: [pdb_search, alphafold_prediction]
  binding_sites:
    tools: [proteins_plus_dogsite]

expression:
  tissue:
    tools: [gtex_expression, hpa_tissue]
  single_cell:
    tools: [hpa_single_cell]

interactions:
  ppi:
    tools: [string_interactions, intact_search]
  pathways:
    tools: [reactome_pathways, kegg_pathway]

genetic_variation:
  population:
    tools: [gnomad_variant, clinvar_search]
  essentiality:
    tools: [depmap_gene_effect]

drug_data:
  bioactivity:
    tools: [chembl_bioactivity, bindingdb_search]
  clinical:
    tools: [clinicaltrials_search, fda_approval]
  safety:
    tools: [sider_side_effects, open_targets_safety]
  admet:
    tools: [admet_ai_predict, drugbank_admet]

literature:
  full_text:
    tools: [europe_pmc_search, semantic_scholar_search]
  citations:
    tools: [openalex_citations, semantic_scholar_citations]

prediction:
  binding:
    tools: [boltz2_predict]
  admet:
    tools: [admet_ai_predict]
```

### 5.5 Wikilink Graph: Complete Edge Map

The new skills integrate into the existing graph. Showing only edges involving
new/enhanced nodes:

```
entity-resolution
  Feeds → target-intelligence
  Feeds → drug-intelligence
  Feeds → literature-review
  Feeds → target-validation

target-intelligence
  Uses ← entity-resolution
  Uses ← tool-lookup (reference)
  Feeds → target-validation
  Feeds → hypothesis-generation
  Feeds → scientific-writing
  Related → drug-intelligence

drug-intelligence
  Uses ← entity-resolution
  Uses ← tool-lookup (reference)
  Feeds → target-validation
  Feeds → scientific-writing
  Related → target-intelligence

target-validation
  Uses ← target-intelligence
  Uses ← drug-intelligence
  Uses ← literature-review
  Feeds → hypothesis-generation
  Feeds → scientific-writing
  Related → peer-review

literature-review (enhanced)
  Uses ← entity-resolution (NEW edge)
  Uses ← paper-search (existing edge)
  Feeds → target-validation (NEW edge)
  Feeds → hypothesis-generation (existing edge)
  Feeds → scientific-writing (existing edge)
```

### 5.6 Updated Router Decision Tree

The research workflow section of `SKILL_ROUTER.md` would expand:

```
User needs research support
│
├─ Need to FIND papers?
│  ├─ Quick search (1-20 papers) → paper-search
│  └─ Systematic review (50+ papers) → literature-review
│
├─ Need to PROFILE a biological target?
│  ├─ Start with → entity-resolution (disambiguation)
│  └─ Then → target-intelligence (structure, expression, pathways, variants)
│
├─ Need to PROFILE a drug or compound?
│  ├─ Start with → entity-resolution (disambiguation)
│  └─ Then → drug-intelligence (chemistry, pharmacology, ADMET, clinical)
│
├─ Need to VALIDATE a drug target?
│  ├─ Start with → entity-resolution
│  ├─ Gather evidence → target-intelligence + drug-intelligence + literature-review
│  └─ Score → target-validation (0-100, GO/NO-GO)
│
├─ Need to GENERATE hypotheses?
│  └─ hypothesis-generation (optionally fed by target-intel or drug-intel)
│
├─ Need to MANAGE citations → citation-management
└─ Need to EVALUATE a paper → peer-review
```

---

## 6. MCP Server as Cross-Cutting Data Layer

### 6.1 Beyond the Four Skills

The ToolUniverse MCP server benefits **existing skills** beyond the four
new/enhanced nodes. Once installed, any skill in the graph can query 600+
scientific tools.

| Existing Skill | How ToolUniverse MCP Helps |
|----------------|--------------------------|
| **hypothesis-generation** | Feed real data into hypothesis formulation. Stage 2 (literature search) can pull from Europe PMC, OpenAlex. Stage 4 (generate hypotheses) can check against protein interaction networks (STRING), pathway databases (Reactome), and expression data (GTEx) for biological plausibility. |
| **literature-review** | Beyond the planned enhancements: access Europe PMC full-text API for open-access verification, OpenAlex for citation network analysis, Semantic Scholar for field-of-study filtering. |
| **scientific-writing** | Methods sections can reference specific database versions and tool parameters. Introduction and Discussion sections can pull current statistics (e.g., "X is expressed in Y tissues per GTEx v8"). |
| **scientific-schematics** | Pathway diagrams can be informed by real Reactome/KEGG pathway data rather than manually curated. Protein domain diagrams can pull from InterPro. |
| **plotting-libraries** | Expression heatmaps from GTEx data. Interaction network visualizations from STRING. Variant frequency plots from gnomAD. |
| **statistical-analysis** | Effect sizes and sample sizes from published datasets. Population frequency data from gnomAD for power calculations. |
| **peer-review** | Verify claims in manuscripts against primary databases. Check whether cited protein interactions exist in STRING. Validate reported expression patterns against GTEx/HPA. |
| **research-paper-summarizer** | Enrich summaries with database context. When summarizing a paper about gene X, pull current knowledge from UniProt, Open Targets, and expression databases to contextualize findings. |

### 6.2 MCP Configuration

The ToolUniverse MCP server would be added alongside existing MCPs in the
Claude Code configuration:

```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "uvx",
      "args": ["tooluniverse-mcp-server"],
      "env": {}
    }
  }
}
```

> **Note:** The exact MCP server package name and configuration will need to
> be verified against the ToolUniverse documentation. The repository at
> `github.com/mims-harvard/ToolUniverse` should have MCP server setup
> instructions.

### 6.3 Redundancy Management

Some ToolUniverse tools overlap with existing MCPs. Strategy:

| Data Source | Keep Existing MCP? | Use ToolUniverse? | Rationale |
|------------|-------------------|-------------------|-----------|
| Open Targets | Yes | Skip OT tools | Our MCP has full GraphQL access, well-integrated |
| PubMed | Yes | Skip PubMed tools | Our MCP has structured search, article metadata, full-text |
| Consensus | Yes | Skip equivalent | Semantic search over 200M+ papers |
| Zotero | Yes | N/A | Personal library, no ToolUniverse equivalent |
| Readwise | Yes | N/A | Reading management, no ToolUniverse equivalent |
| Everything else | N/A | Yes | ChEMBL, DrugBank, UniProt, STRING, GTEx, PDB, AlphaFold, gnomAD, etc. |

Skills should prefer existing MCPs for their covered domains and use
ToolUniverse for everything else. The tool-lookup reference encodes this
preference.

---

## 7. Implementation Roadmap

### Phase 1: Foundation

- [ ] Install and test ToolUniverse MCP server
- [ ] Verify tool availability and response formats
- [ ] Create `shared/tool-lookup.yaml` with initial capability mappings
- [ ] Build `entity-resolution` skill following SKILL_TEMPLATE
- [ ] Test entity resolution for genes, compounds, and diseases

### Phase 2: Research Nodes

- [ ] Build `target-intelligence` skill
- [ ] Build `drug-intelligence` skill
- [ ] Test both skills with 2-3 example targets/compounds
- [ ] Verify wikilink edges work (entity-resolution feeds both)

### Phase 3: Integration Layer

- [ ] Build `target-validation` scoring skill
- [ ] Enhance `literature-review` with T1-T4 grading and collision-aware search
- [ ] Test the full workflow: entity-resolution → target-intel + drug-intel →
  target-validation
- [ ] Validate scoring against the hypercholesterolemia case study from the paper

### Phase 4: Router and Graph Wiring

- [ ] Update `SKILL_ROUTER.md` with new decision tree branches
- [ ] Add cross-reference edges to existing skills that benefit from ToolUniverse
- [ ] Test multi-skill workflows end-to-end
- [ ] Document in changelog

### Phase 5: Broader Ecosystem Benefits

- [ ] Identify which existing skills benefit most from ToolUniverse MCP access
- [ ] Add ToolUniverse-powered enhancements to `hypothesis-generation`,
  `scientific-schematics`, `plotting-libraries`
- [ ] Expand `tool-lookup.yaml` as new tools are discovered

---

## Appendix: Reference Files

| File | Location | Description |
|------|----------|-------------|
| ToolUniverse paper | `docs/2509.23426v2.pdf` | Research paper (arXiv:2509.23426v2) |
| Drug research reference | `docs/tooluniverse-drug-research/SKILL.md` | Monolithic drug profiling workflow (~1,800 lines) |
| Target research reference | `docs/tooluniverse-target-research/SKILL.md` | Monolithic target intelligence workflow (~1,500 lines) |
| Drug-target validation reference | `docs/tooluniverse-drug-target-validation/SKILL.md` | Monolithic validation pipeline (~1,207 lines) |
| Literature deep research reference | `docs/tooluniverse-literature-deep-research/SKILL.md` | Monolithic literature workflow (~1,051 lines) |
| Skill template | `skills/SKILL_TEMPLATE.md` | Standard skill structure |
| Skill router | `skills/SKILL_ROUTER.md` | Decision trees and routing |
| Brand interface | `skills/BRAND_SKILL_INTERFACE.md` | Interface contract example |
