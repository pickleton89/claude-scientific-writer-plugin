# Cross-Database Search Scenarios

Process-oriented recipes answering **"which databases in what order?"** for
common biomedical research questions. Distinct from
`scripts/sources/pubmed/references/common_queries.md`, which provides
*PubMed-only* Boolean templates by domain (cancer, cardio, infectious, etc.).
This cookbook is for the bibliography agent during Phase 2 (Investigation)
when constructing the multi-database execution plan.

Each recipe assumes the frozen Search Contract from Checkpoint 1 already
defines `required_databases`. Recipes describe *how* to phrase queries across
those databases, not which databases to add.

## Recipe selection

| User intent (from RQ scoping) | Recipe |
|------|--------|
| "How do I do [assay]?" / "What's the protocol for…?" | [1. Lab methods & protocols](#1-lab-methods--protocols) |
| "What causes…?" / "What's the mechanism of…?" | [2. Disease mechanism](#2-disease-mechanism) |
| "Does [drug] work for [condition]?" | [3. Drug + condition efficacy](#3-drug--condition-efficacy) |
| "What's new in [field] this year/quarter?" | [4. Latest developments](#4-latest-developments) |
| "What antibody/cell line/primer should I use for X?" | [5. Validated reagents](#5-validated-reagents) |
| "How does [method A] compare to [method B]?" | [6. Method comparison](#6-method-comparison) |

## 1. Lab methods & protocols

**When to use:** RQ asks how to perform an assay, technique, or experimental
procedure. Trigger phrases: "protocol for…", "how to do…", "method for…".

**Database sequence:** PubMed (primary) → Paperclip PMC corpus (secondary) →
external protocol repositories (tertiary, out-of-pipeline).

**Worked example** (Western blot for membrane proteins):

```
PubMed: "Western Blotting"[MeSH] AND ("membrane proteins"[MeSH] OR transmembrane)
        AND (protocol OR method OR technique)
        AND ("2018"[Date - Publication] : "2026"[Date - Publication])
Paperclip: paperclip search "western blot membrane protein protocol" -n 30 -s pmc
```

**Output expectations:** Annotated bibliography weighted toward
*Methods*-typed publications (`Publication Type: Methods` in PubMed metadata)
and protocol-format papers from JoVE / Bio-Protocol / Methods journals.
Out-of-pipeline tertiary references (protocols.io, OpenWetWare) are
mentioned in the synthesis but not included in source counts toward
`MIN_SOURCES`.

## 2. Disease mechanism

**When to use:** RQ asks about pathophysiology, signaling, or molecular
basis of a disease. Trigger phrases: "mechanism of…", "how does X cause Y",
"role of [pathway] in [disease]".

**Database sequence:** PubMed reviews first → PubMed mechanistic primary
papers → Paperclip for emerging mechanism work across bioRxiv/medRxiv/arXiv
preprints → Consensus for cross-paper synthesis.

**Worked example** (amyloid-β in Alzheimer's):

```
Step 1 (overview):
  PubMed: "Alzheimer Disease"[MeSH] AND pathophysiology AND review[Publication Type]
          Filters: 5yr, English
Step 2 (mechanistic primary):
  PubMed: "Alzheimer Disease"[MeSH] AND ("amyloid beta-Peptides"[MeSH] OR tau)
          AND mechanism
Step 3 (preprints):
  Paperclip: search "amyloid beta tau mechanism Alzheimer" -s biorxiv -s medrxiv --since 12m
Step 4 (synthesis):
  Consensus: "What is the current evidence for amyloid-β as the primary driver
              of Alzheimer's pathology?"
```

**Output expectations:** Tiered evidence — review articles set the consensus
landscape, primary mechanistic papers anchor specific claims, preprints flag
emerging counter-evidence. The bibliography agent emits a Search Strategy
Block per `agents/bibliography.md` §Output: Search Strategy Block.

## 3. Drug + condition efficacy

**When to use:** RQ evaluates a specific drug/intervention against a defined
clinical condition. Trigger phrases: "does X work for Y?", "efficacy of…",
"treatment effect…".

**Database sequence:** PubMed (PICO-structured, Publication Type-filtered) →
Scite reception assessment → Consensus for cross-trial synthesis.

**Worked example** (semaglutide for T2D cardiovascular outcomes):

```
PubMed: "Semaglutide"[Substance Name] AND "Diabetes Mellitus, Type 2"[MeSH]
        AND "Cardiovascular Diseases"[MeSH]
        AND (clinical trial[Publication Type] OR meta-analysis[Publication Type])
Scite (post-search, per agents/bibliography.md §Step 4b):
  For each top-20 included paper, query search_literature with dois: [DOI]
  Flag papers with Scite Index < 0.5 as [CONTESTED]
Consensus: "What is the cardiovascular benefit of semaglutide in T2D patients?"
```

**Output expectations:** Annotated bibliography ordered by evidence level
(meta-analyses → RCTs → cohort studies). Each entry carries a Reception
field (Scite Index + supporting/contrasting/mentioning counts) per
`agents/bibliography.md` §Output: Annotated Bibliography. PICO scaffolding
per `references/search_strategy_design.md` §Step 1a is required.

## 4. Latest developments

**When to use:** RQ asks about recent (last 6-12 months) advances in a field.
Trigger phrases: "what's new in…", "latest…", "recent advances", "current
state".

**Database sequence:** Paperclip with `--since` recency filter (primary, for
unindexed preprints across bioRxiv/medRxiv/arXiv) → PubMed with date filter
(secondary, for newly indexed) → Consensus (synthesis).

**Worked example** (CAR-T for solid tumors, last 6 months):

```
Paperclip: search "CAR-T solid tumor" -s biorxiv -s medrxiv --since 6m --sort date
PubMed: "Immunotherapy, Adoptive"[MeSH] AND "Neoplasms"[MeSH]
        AND "solid tumor" AND ("2025/11"[Date - Publication]:"2026/05"[Date - Publication])
Consensus: "What are the most significant advances in CAR-T therapy for solid
            tumors in the last 6 months?"
```

For weekly scans, swap `--since 6m` for `--since 7d`. For DOI-anchored
re-verification of a specific paper in a recent recipe, prefer
`paperclip lookup doi <DOI>` over `paperclip search "<title>" -n 1`.

**Output expectations:** ≥40% of sources from preprint servers (acceptable
deviation from default ≥60% peer-reviewed in `QUANTIFICATION_THRESHOLDS.md`
§1 — document the deviation in the Search Strategy Block since the RQ
itself trades currency against peer review). Verification agent flags every
preprint per its `[PREPRINT]` quality flag.

## 5. Validated reagents

**When to use:** RQ asks which antibody / cell line / primer / vector to use
for a specific application. Trigger phrases: "validated antibody for…", "which
cell line for…", "best primers…".

**Database sequence:** Vendor / community databases (out-of-pipeline) →
PubMed validation papers → Paperclip full-text for usage context.

**Vendor databases (record but do not count toward source minimums):**

| Reagent type | Resource |
|------|------|
| Plasmids | Addgene |
| Cell lines | ATCC, Cellosaurus |
| Antibodies | Antibodypedia, CiteAb |
| Primers | PrimerBank, qPrimerDepot |
| Mouse strains | MGI, JAX |

**Worked example** (validated p53 antibody for Western blot):

```
Antibodypedia: search "p53" — filter by Western blot validation
PubMed: ("p53"[Title/Abstract] OR "TP53"[Title/Abstract])
        AND "Blotting, Western"[MeSH]
        AND (antibody validation OR validated)
Paperclip: paperclip search "anti-p53 antibody western blot validation" -n 20
```

**Output expectations:** Annotated bibliography lists 3-5 validation papers
per recommended reagent, with vendor catalog numbers in the synthesis
(reagents themselves are not citable sources, only the validation papers
are). This recipe often falls below `MIN_SOURCES` for `full` mode and is
better suited to `quick` mode.

## 6. Method comparison

**When to use:** RQ asks how two or more methods, techniques, or
algorithms compare. Trigger phrases: "compare X and Y", "X vs Y",
"which is better…".

**Database sequence:** Consensus (synthesis) → PubMed for each individual
method → Scite for citation context on competing methods.

**Worked example** (lipid nanoparticles vs viral vectors for CRISPR delivery):

```
Consensus: "How do lipid nanoparticles compare to AAV vectors for in vivo
            CRISPR-Cas9 delivery in terms of efficiency and immunogenicity?"
PubMed (Method A): "lipid nanoparticles" AND CRISPR AND "in vivo"
                   AND (efficiency OR delivery)
PubMed (Method B): ("AAV" OR "adeno-associated virus") AND CRISPR AND "in vivo"
                   AND (efficiency OR delivery)
Scite (per top method-comparison paper): retrieve citing-paper snippets to
       surface the field's recent verdict on the comparison
```

**Output expectations:** Synthesis section structured as a comparison
table (efficiency, off-target rate, immunogenicity, manufacturing cost,
clinical readiness) with citations grounded in PubMed; Consensus output
provides the qualitative narrative around the table. The synthesis agent
emits the comparison table per its standard output contract.

## Integration with the pipeline

- **Phase 1 (Scoping):** mentor / advocate agents help the user identify
  which recipe best matches the RQ during Checkpoint 1 framing.
- **Phase 2 (Investigation):** bibliography agent applies the chosen recipe's
  database sequence within the constraints of the frozen Search Contract.
  Recipes do not override `required_databases`; they sequence and phrase
  queries against them.
- **Phase 3 (Synthesis):** synthesis agent uses the recipe's Output
  Expectations to shape the report's structure.

## Quality gates

| Check | Criterion | Failure handling |
|---|---|---|
| Recipe alignment | Selected recipe matches RQ trigger phrasing | Re-scope RQ with mentor agent |
| Database coverage | Recipe sequence respects mode-minimum from `agents/bibliography.md` §Quantitative Thresholds | Add database channel; do not skip recipe step |
| Source-type expectation | Output mix matches recipe Output Expectations (e.g., ≥40% preprints for Recipe 4) | Document deviation in Search Strategy Block |

## Attribution

Cross-database recipe pattern adapted from the external
`scientific-literature-search` skill's §Common Search Scenarios (CC-BY-4.0).
Database sequencing follows the matrices in
`references/biomedical_research.md` §Database-Specific Search Notes and
`agents/bibliography.md` §Step 3.
