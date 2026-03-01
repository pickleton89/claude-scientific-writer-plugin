# Known Entity Naming Collisions

> Catalog of gene symbols and entity names with documented disambiguation issues.
> Version: 1.0.0
> Used by: entity-resolution (Stage 4)

---

## Gene Symbol Collisions

These symbols are known to produce significant off-topic results in literature searches. Apply the listed mitigation strategy before any literature queries.

| Symbol | Target Entity | Collision Domain | Mitigation Strategy |
|--------|--------------|-----------------|---------------------|
| **ACE** | Angiotensin-converting enzyme (human gene) | ACE inhibitor (drug class), Adverse Childhood Experiences (psychology) | Filter: `NOT "ACE inhibitor" NOT "adverse childhood"` |
| **CAT** | Catalase (human enzyme) | Chloramphenicol acetyltransferase (bacterial), computed axial tomography | Filter: `NOT chloramphenicol NOT "CAT scan" NOT bacterial NOT plasmid` |
| **JAK** | Janus kinase family | "Just Another Kinase" (historical annotation), JAK-STAT used loosely | Refine query: use `JAK1`, `JAK2`, or `JAK3` for specific isoforms |
| **TRAG** | T-cell regulatory gene | Bacterial TraG conjugation protein | Filter: `NOT plasmid NOT conjugation NOT bacterial NOT "type IV"` |
| **CAMP** | Cathelicidin antimicrobial peptide | Cyclic AMP (cAMP) signaling | Filter: `NOT "cyclic AMP" NOT "cAMP" NOT "adenosine monophosphate"` |
| **REST** | RE1-silencing transcription factor | REST API (software), rest/sleep | Filter: `NOT "REST API" NOT software NOT web NOT sleep` |
| **ACHE** | Acetylcholinesterase | General "ache" (pain) in medical literature | Refine query: use full name "acetylcholinesterase" or `ACHE[Gene]` field tag |
| **CLOCK** | Circadian locomotor output cycles kaput | General "clock" references in circadian literature | Filter: `NOT "alarm clock" NOT "clock speed"`; use `CLOCK[Gene]` field tag |
| **IMPACT** | Impact RWD domain protein | General word "impact" | Refine query: use `IMPACT[Gene]` field tag in PubMed |
| **NODAL** | Nodal growth differentiation factor | "Nodal" as adjective (nodal metastasis, nodal involvement) | Filter: `NOT "lymph node" NOT "nodal metastasis" NOT "nodal stage"` |
| **FAST** | FOXH1-associated signal transducer | General adjective | Refine query: use `FASTK` or full name; avoid bare "FAST" |
| **WAS** | Wiskott-Aldrich syndrome protein | English word "was" | Refine query: use `WAS[Gene]` field tag or "Wiskott-Aldrich" |

---

## Drug Name Collisions

| Name | Target Entity | Collision Domain | Resolution |
|------|--------------|-----------------|------------|
| **Taxol** | Paclitaxel (brand name) | Generic paclitaxel literature | Use INN "paclitaxel"; Taxol is Bristol-Myers Squibb trademark |
| **Aspirin** | Acetylsalicylic acid | Aspirin-exacerbated respiratory disease (AERD) | Clarify: drug profile vs. AERD context |

---

## High-Risk Patterns

Symbols matching these patterns should **always** trigger collision detection:

1. **<=4 characters** — Nearly all 2-4 letter gene symbols collide with abbreviations (e.g., ACE, CAT, CAMP, FAST)
2. **Common English words** — REST, IMPACT, FAST, WAS, CAN, SET, NOT, BAD
3. **Enzyme abbreviation overlap** — CAT, SOD, GOT, GPT, ALP
4. **Pathway component names** — MAPK, ERK, AKT (less collision but frequently used as pathway shorthand rather than specific gene)

---

## Detection Protocol

When a symbol matches any high-risk pattern:

1. Search PubMed: `"{SYMBOL}"[Title]` — retrieve 20 results
2. Classify each result as on-topic or off-topic
3. If **>20% off-topic**: construct negative filter from collision terms
4. If **>50% off-topic**: consider using the full gene name instead of symbol
5. Record the off-topic rate and filter in the Entity Identity Table
