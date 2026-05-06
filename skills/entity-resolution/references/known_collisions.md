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

1. **PubTator3 autocomplete probe (preferred)**: `pubtator3 autocomplete "<SYMBOL>"` (no `--concept` filter) — if the result list contains >1 distinct `biotype`, that's hard evidence of cross-concept ambiguity. With `--concept gene`, check whether the top hit's `name` matches the symbol exactly (case-sensitive) and whether `match` says "Matched on name" (high confidence) vs "Matched on synonyms" (lower confidence).
2. **PubTator3 mention count**: `pubtator3 search --gene <SYMBOL> --size 1 --summary` — the `total` field is an ID-grounded mention count. Near-zero for a well-known gene = wrong canonical resolution.
3. **PubMed title scan (legacy reach check)**: `"{SYMBOL}"[Title]` — retrieve 20 results; classify each as on-topic or off-topic.
4. If **>20% off-topic** in step 3: construct negative filter from collision terms.
5. If **>50% off-topic** in step 3: consider using the full gene name instead of symbol.
6. Record the PubTator3 entity ID, mention count, off-topic rate, and filter in the Entity Identity Table.

### PubTator3 thresholds

| Signal | Action |
|---|---|
| autocomplete returns 0 results for the input symbol | escalate — entity may not be in PubTator3 corpus, fall back to PubMed-only validation |
| autocomplete returns >1 `biotype` without `--concept` filter | flag as cross-concept collision; require user to specify concept |
| autocomplete top hit `match` is "Matched on synonyms" not "Matched on name" | lower confidence — verify with cross-references in Stage 3 |
| `pubtator3 search --gene <X> --size 1 --summary` returns total < 10 for an HGNC-resolved symbol | suspicious — probable wrong gene or PubTator3 indexing gap |
