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

### Step 1a: PICO decomposition (clinical RQs only)

For RQs that compare an intervention against an alternative in a defined
population for a specific outcome, decompose to PICO before listing concept
groups. PICO catches missing comparator arms that pure concept extraction
misses, and the four axes map directly to MeSH-tagged Boolean clauses.

| Axis | Definition | Worked example (metformin vs placebo for CV outcomes in T2D) |
|---|---|---|
| **P** Population | Who is studied? | Adults with type 2 diabetes — `"Diabetes Mellitus, Type 2"[MeSH]` |
| **I** Intervention | What treatment / exposure? | Metformin — `"Metformin"[MeSH]` |
| **C** Comparison | What is the alternative arm? | Placebo or other oral antidiabetic — `placebo OR "Sulfonylurea Compounds"[MeSH]` |
| **O** Outcome | What result is measured? | Cardiovascular events — `"Cardiovascular Diseases"[MeSH]` |

The PICO-derived Boolean joins all four axes:

```
"Diabetes Mellitus, Type 2"[MeSH] AND "Metformin"[MeSH]
  AND (placebo OR "Sulfonylurea Compounds"[MeSH])
  AND "Cardiovascular Diseases"[MeSH]
  AND (clinical trial[Publication Type] OR meta-analysis[Publication Type])
```

For non-clinical RQs (basic biology, methods, computational), skip Step 1a
and proceed with concept-group decomposition only. PICO's Comparison and
Outcome axes do not apply outside the intervention-evaluation framing.

For domain-specific PICO query templates (cancer, cardiovascular, infectious
disease, neurology, diabetes), see
`scripts/sources/pubmed/references/common_queries.md` §Tips for Constructing
Queries §1 (PICO Framework) and the worked recipes in §Disease-Specific
Queries.

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

For the full PubMed query surface — Boolean precedence, phrase searching,
wildcards, proximity operators, and the complete field-tag table
(`[MeSH]`, `[tiab]`, `[mh]`, `[pt]`, `[dp]`, `[au]`, `[Substance Name]`,
`[MeSH Major Topic]`) — see
`scripts/sources/pubmed/references/search_syntax.md`. For arXiv `cat:` syntax
and biomedical-adjacent subject categories (q-bio.*, cs.*), see
`references/arxiv_categories.md`.

### Step 4: Define Inclusion / Exclusion Criteria

Criteria are designed *before* execution and documented as part of the Strategy
Block. Adjust template rows to match the topic; the table below is the default
biomed scaffold.

| Criterion | Include | Exclude |
|---|---|---|
| Publication type | Peer-reviewed primary research, systematic reviews, meta-analyses, registered preprints; **grey lit from W1/W2 domains** (regulatory, registries, societies — via the WebSemantic channel) carrying `[Grey Lit]` tag + `fetched_at` timestamp | Editorials, letters, news, blog posts and **curated media (W3b)** unless context-only, retracted papers (per Scite editorial notices) |
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

**Grey-literature note.** In heavy modes + fact-check, the WebSemantic
channel (Exa MCP) admits grey lit from the W1/W2 tiers of
`shared/references/citable_web_domains.md` (regulatory pages, society
abstracts, open repositories). W3a (`*.edu` institutional pages) is
treated like W2; W3b (curated journalism — Nature/Science/NEJM news desks)
is context-only and cannot ground a verdict. In `systematic-review` mode,
WebSemantic is **off by default** to keep PRISMA-S compliance clean —
explicit user opt-in at Phase 1 toggles it on with a PRISMA-S §S4
disclosure block. See `agents/bibliography.md` §WebSemantic channel for
the filtering rules and Search Log conventions.

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

## Common Pitfalls

Advisory checks during strategy design. Each pitfall links to the
authoritative reference rather than restating policy.

1. **Over-specific queries.** Packing every concept, modifier, and filter
   into a single Boolean (typically 6+ ANDed clauses) cuts recall — all
   clauses must match simultaneously. *Fix:* split into 2-3 sub-queries on
   the primary concept axes from Step 1, run them independently, and union
   the deduplicated results. Mode-minimum source counts in
   `agents/bibliography.md` §Quantitative Thresholds remain in force on
   the union, not per sub-query.

2. **Single-database reliance.** Querying only PubMed (or only Consensus)
   guarantees coverage gaps — preprints absent from PubMed, biomedical
   results absent from Consensus's general index. *Fix:* the mode minimum
   in `agents/bibliography.md` §Quantitative Thresholds (≥2 for `quick`,
   ≥3 for `full`/`lit-review`/`hypothesis`, ≥4 for `systematic-review`)
   is a hard floor enforced by `scripts/search_audit.py`.

3. **Date-range neglect.** For fast-moving fields, defaulting to "all
   years" buries current evidence under foundational papers; for
   foundational topics, restricting to "last 5 years" excludes the
   defining work. *Fix:* defer to
   `references/biomedical_research.md` §Currency Rules by Field for the
   per-field threshold; document foundational-work exemptions in the
   Strategy Block.

4. **Skipping abstract triage.** Sending all title-screen-passing hits
   to full-text retrieval wastes the Tier-3 full-text budget on hits
   that fail the inclusion criteria at abstract review. *Fix:* enforce
   the 3-tier screening protocol in `agents/bibliography.md` §Screening
   Protocol (title ≤15 s → abstract ≤2 min → full text for High/Medium
   tiers only).

5. **NOT-operator misuse.** `NOT cancer` excludes papers that mention
   cancer in a different context (e.g., "no association with cancer
   risk" — a relevant negative result). *Fix:* prefer adding positive
   terms to narrow results, or use entity-resolution collision filters
   (`agents/bibliography.md` §Step 2) which scope exclusions to the
   specific colliding senses rather than the bare term.

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
