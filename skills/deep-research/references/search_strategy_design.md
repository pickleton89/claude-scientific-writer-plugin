# Search Strategy Design

Framework for designing reproducible literature search strategies. Applied by the
bibliography agent during Phase 2 (Investigation) before query execution. Produces
a documented Search Strategy Block that the compiler renders into the report's
`Methods → Search Strategy` and `Methods → Inclusion/Exclusion Criteria` sections.

**Purpose:** a reviewer reading the report alone should be able to replicate the
search.

## Mode Gating

| Mode | Strategy Block | Notes |
|------|----------------|-------|
| `full` | Required | Renders into Methods §Search Strategy + §Inclusion/Exclusion Criteria |
| `lit-review` | Required | Renders as top-level §Search Strategy |
| `systematic-review` | Required | Renders into PRISMA Methods §Search Strategy; criteria feed PRISMA flow |
| `hypothesis` | Required | Documents the evidence base for hypothesis generation |
| `quick` | Skipped | Emit one-line note: "Search strategy not documented in quick mode." |
| `fact-check` | Skipped | Verification report does not require strategy documentation |
| `socratic` | N/A | No bibliography phase |
| `review` | N/A | Reviewer report; no search performed |

## Five-Step Framework

### Step 1: Identify Concepts

Decompose the research question into concept groups:

- **Primary concepts** (2-4 core terms answering the RQ)
- **Synonyms / variants** per primary concept (lexical, abbreviations, brand-vs-generic)
- **MeSH headings** for each concept (PubMed-specific; check via PubMed search syntax)
- **Discipline-specific terminology** (assay names, model systems, clinical phase descriptors)

**Worked example (EGFR resistance in NSCLC):**

| Concept group | Primary | Synonyms / variants | MeSH |
|---|---|---|---|
| Target | EGFR | ErbB1, HER1, epidermal growth factor receptor | "Receptor, Epidermal Growth Factor"[MeSH] |
| Phenotype | resistance | refractory, acquired resistance, drug resistance | "Drug Resistance, Neoplasm"[MeSH] |
| Disease | NSCLC | non-small cell lung cancer, lung adenocarcinoma, LUAD | "Carcinoma, Non-Small-Cell Lung"[MeSH] |

### Step 2: Select Databases

Use the domain-database matrix in `agents/bibliography.md` §Step 3 (Database
Selection). Do not duplicate it here. Minimum coverage:

- `quick`: ≥2 databases
- `full` / `lit-review` / `hypothesis`: ≥3 databases
- `systematic-review`: ≥4 databases

Scite is a post-search reception layer, not a discovery database (see
`bibliography.md` Step 4b).

### Step 3: Construct Boolean Query

Standard biomed structure:

```
(concept1_primary OR concept1_synonym1 OR concept1_synonym2)
  AND (concept2_primary OR concept2_synonym1)
  AND (concept3_primary OR concept3_synonym1)
  [collision filters per entity-resolution, if HIGH risk]
  Filters: [date range], [language], [study design]
```

If entity-resolution flagged HIGH collision risk for any term, append `NOT`
exclusions per `agents/bibliography.md` §Step 2 (Apply Collision Filters).

### Step 4: Define Inclusion / Exclusion Criteria

Criteria are designed *before* execution and documented as part of the Strategy
Block. Adjust template rows to match the topic; the table below is the default
biomed scaffold.

| Criterion | Include | Exclude |
|---|---|---|
| Publication type | Peer-reviewed primary research, systematic reviews, meta-analyses, registered preprints | Editorials, letters, news, blog posts, retracted papers (per Scite editorial notices) |
| Study design | Match the RQ (RCT for efficacy; cohort for prognosis; case-control for risk; mechanistic for biology) | Designs that cannot answer the RQ |
| Date range | Per `references/biomedical_research.md` §Currency Rules by Field; foundational works exempt | Older than threshold unless seminal (substantially above the era's median citations and routinely cited as foundational; "seminal" is a judgment call, not a fixed cutoff) |
| Language | English | Other languages unless key source (translate or note as gap) |
| Population (if clinical) | Match the RQ population (species, age, disease stage) | Off-target populations |
| Intervention / exposure | Match the RQ exposure | Off-target exposures |
| Outcome | Match the RQ outcome | Off-target outcomes |
| Source quality | Indexed journals, recognized preprint servers (bioRxiv, medRxiv) | Predatory journals (per verification agent's predatory list) |

Currency thresholds default to the field-specific values in
`references/biomedical_research.md` §Currency Rules by Field. Source-count
minimums defer to `scripts/thresholds.py` (`MIN_SOURCES`).

### Step 5: Document the Screening Protocol

Bibliography agent's three-tier screening (see `agents/bibliography.md` §Screening
Protocol):

1. **Title screening** (≤15 s/paper) — direct relevance to RQ
2. **Abstract screening** (≤2 min/paper) — inclusion criteria match; relevance tier (High / Medium / Low)
3. **Full-text assessment** for High and Medium tiers; verify key claims

Record per-stage exclusion counts; these feed the PRISMA flow in
`systematic-review` mode and the search-saturation metric in all other modes.

## Strategy Block Output Template

The bibliography agent emits the following block. Values fill in from Steps 1-5.

```markdown
## Search Strategy

**Concepts:**
- Primary: [concept 1], [concept 2], [concept 3]
- Secondary / synonyms: [terms]
- MeSH headings: [MeSH terms used, with [MeSH] tag]

**Boolean structure:**
("concept1" OR "synonym1a" OR "synonym1b")
  AND ("concept2" OR "synonym2a")
  AND ("concept3")
  [NOT "collision_term"]                 # only if entity-resolution flagged HIGH
  Filters: [date range], [language], [study design]

**Databases:** [primary] (primary), [secondary] (secondary), [tertiary] (tertiary)
  Reception assessment: Scite (post-search; skipped in quick / fact-check)

**Inclusion criteria:**
- Publication type: [list]
- Study design: [list]
- Date range: [range]; foundational works unrestricted
- Population: [if applicable]
- Intervention / exposure: [if applicable]
- Outcome: [if applicable]
- Language: English

**Exclusion criteria:**
- [list]
- Predatory journals (per verification agent's predatory list)
- Retracted (per Scite editorial notices)

**Screening protocol:**
1. Title screening (≤15 s/paper): direct relevance to RQ
2. Abstract screening (≤2 min/paper): inclusion criteria match; relevance tier (High / Medium / Low)
3. Full-text assessment for High and Medium tiers
```

## Quality Gates (advisory, not blocking)

| Check | Criterion | Failure handling |
|---|---|---|
| Concept coverage | All RQ concepts represented in Boolean | Add missing concept group |
| Synonym breadth | ≥2 synonyms per concept (or "no common synonyms" noted) | Expand or document the absence |
| Criteria specificity | Every Include row has a paired Exclude row | Fill in missing exclusions |
| Mode-appropriate database count | Meets minimum from Step 2 | Add database or document unavailability |
| Currency justified | Date range cites `biomedical_research.md` threshold or explicit override | Add citation or override rationale |

## Interaction with Other Agents

- **Receives from:** Phase 1 scoping (RQ, prior dossiers if any, entity-resolution
  identity table for collision filters)
- **Produces:** Strategy Block (this template), emitted before the Annotated
  Bibliography in the bibliography agent's output
- **Consumed by:** Compiler agent's mode-specific report templates
  (`agents/compiler.md`):
  - Full mode: rendered into `Methods → Search Strategy` and
    `Methods → Inclusion/Exclusion Criteria`
  - Lit-Review mode: rendered as top-level `## Search Strategy`
  - Systematic-Review mode: feeds PRISMA Methods §Search Strategy and PRISMA flow
  - Hypothesis mode: rendered into `Methods` block above competing hypotheses

## Attribution

Adapted from `literature_strategist_agent` in
[academic-research-skills](https://github.com/Imbad0202/academic-research-skills)
by Cheng-I Wu (CC BY-NC 4.0). Patterns and design DNA are non-copyrightable;
prose has been reformulated for license compatibility (this plugin is
MIT-licensed).
