---
name: entity-resolution
version: 1.0.0
description: "Resolve gene symbols, protein names, drug names, and disease terms to canonical identifiers with collision detection before any research skill proceeds."
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Entity Resolution

<overview>
Resolve ambiguous biological entity names (genes, proteins, drugs, diseases) to canonical database identifiers before research queries begin. Outputs a verified identity table with all cross-referenced IDs, synonyms, and collision warnings. This is a prerequisite utility invoked by target-intelligence, drug-intelligence, literature-review, and target-validation.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- A downstream research skill needs canonical IDs (Ensembl, UniProt, ChEMBL, EFO) for database queries
- User provides a gene symbol, protein name, drug name, or disease term as free text
- The input entity could be ambiguous (e.g., "ACE" could be a gene or drug class)
- Multiple identifier types are needed for a single entity (e.g., both Ensembl ID and UniProt accession)

Do NOT use this skill when:
- User already provides canonical IDs (e.g., ENSG00000146648, CHEMBL25) — verify format and pass through
- Query is purely literature-based with no database lookups needed → use `paper-search`
- Entity is a pathway, cell type, or other non-resolvable concept — handle inline
</when_to_use>

<decision_framework>
## Decision Matrix

```
Input entity received
│
├─ Is it already a canonical ID? (ENSG*, CHEMBL*, EFO_*, UniProt accession)
│  ├─ Yes → Stage 1: Validate format, skip to Stage 3 (cross-reference + collision check)
│  └─ No → Continue to classification
│
├─ What entity type?
│  │
│  ├─ Gene / Protein
│  │  ├─ Primary: Open Targets search_entities (target)
│  │  ├─ ToolUniverse: MyGene, Ensembl, UniProt
│  │  └─ → Resolve: Ensembl ID, UniProt, HGNC symbol, Entrez ID
│  │
│  ├─ Drug / Compound
│  │  ├─ Primary: Open Targets search_entities (drug)
│  │  ├─ ToolUniverse: ChEMBL, PubChem, DrugBank
│  │  └─ → Resolve: ChEMBL ID, PubChem CID, DrugBank ID
│  │
│  ├─ Disease / Phenotype
│  │  ├─ Primary: Open Targets search_entities (disease)
│  │  └─ → Resolve: EFO ID, MONDO ID, OMIM
│  │
│  └─ Ambiguous (could be multiple types)
│     └─ → Run all type searches, present options, ask user
│
└─ Collision risk? (short symbol, common word)
   ├─ Yes → Stage 4: Collision detection
   └─ No → Stage 5: Output
```

</decision_framework>

<workflow>
## Workflow

### Stage 1: Input Classification

**Objective:** Determine entity type and whether resolution is needed.

**Steps:**
1. Parse the input string. Check if it matches a known canonical ID pattern:
   - Ensembl: `ENSG[0-9]{11}` (gene) or `ENSP[0-9]{11}` (protein)
   - UniProt: `[OPQ][0-9][A-Z0-9]{3}[0-9]` or `[A-NR-Z][0-9][A-Z][A-Z0-9]{2}[0-9]`
   - ChEMBL: `CHEMBL[0-9]+`
   - EFO: `EFO_[0-9]+` or `MONDO_[0-9]+`
2. If canonical ID detected, validate format and skip to Stage 3 (cross-reference + collision check).
3. If free text, classify probable entity type:
   - Gene/protein indicators: all-caps symbol (<=6 chars), "gene", "protein", "receptor", "kinase", "enzyme"
   - Drug indicators: "-ib", "-mab", "-nib", "-statin", "inhibitor", brand name patterns
   - Disease indicators: "-emia", "-itis", "-osis", "syndrome", "disorder", "cancer"
4. If type is ambiguous, flag for multi-type search in Stage 2.

**Exit Criteria:**
- [ ] Entity type classified (gene/protein, drug/compound, disease, or ambiguous)
- [ ] Canonical ID pre-check complete (pass-through or resolution needed)

---

### Stage 2: Primary Resolution

**Objective:** Obtain canonical identifiers using the best available tool.

**Steps:**
1. **For genes/proteins:** Call Open Targets MCP `search_entities` with `query_strings=["{input}"]`. Extract the top hit with `entity: "target"`. Record the Ensembl Gene ID.
2. **For drugs/compounds:** Call Open Targets MCP `search_entities` with `query_strings=["{input}"]`. Extract the top hit with `entity: "drug"`. Record the ChEMBL ID.
3. **For diseases:** Call Open Targets MCP `search_entities` with `query_strings=["{input}"]`. Extract the top hit with `entity: "disease"`. Record the EFO/MONDO ID.
4. **If ToolUniverse available**, enrich with additional IDs:
   - Gene: MyGene (`query` param) → UniProt, Entrez, HGNC, Ensembl
   - Drug: ChEMBL molecule search → synonyms, trade names, formulations
   - Use `tool-lookup.yaml` disambiguation section for tool selection
5. **If ambiguous type**, run searches for all candidate types and rank results by relevance score.

**Exit Criteria:**
- [ ] At least one canonical ID obtained from primary source
- [ ] Entity name confirmed against official nomenclature (HGNC symbol, INN, etc.)

---

### Stage 3: Cross-Reference Validation

**Objective:** Build complete identifier table and verify consistency.

**Steps:**
1. From the primary ID, retrieve cross-references:
   - Gene: Ensembl ID → UniProt (via Open Targets or UniProt ID mapping), NCBI Entrez, HGNC
   - Drug: ChEMBL ID → PubChem CID (via ChEMBL cross-refs), DrugBank ID, CAS number
   - Disease: EFO → MONDO cross-reference, OMIM if genetic
2. Verify consistency: does the UniProt entry match the expected gene symbol? Does the ChEMBL entry name match the input?
3. Collect synonyms and aliases (UniProt alternative names, drug trade names, disease aliases).
4. Record the **versioned Ensembl/Gencode ID** if available (needed for GTEx queries).

**Exit Criteria:**
- [ ] Identity table populated with >=2 cross-referenced IDs
- [ ] No conflicting information between ID sources
- [ ] Synonyms/aliases collected for literature search

---

### Stage 4: Collision Detection

**Objective:** Identify naming collisions that could contaminate downstream searches.

**Steps:**
1. Assess collision risk. High-risk indicators:
   - Gene symbol is <=4 characters (e.g., ACE, CAT, JAK, FAST)
   - Symbol is a common English word or abbreviation
   - Symbol matches entities in different biological contexts
   - Symbol listed in `references/known_collisions.md`
2. If high-risk, run a PubMed title search: `"[SYMBOL]"[Title]` — review first 20 results.
3. Calculate off-topic rate: count results clearly about a different entity.
4. If >20% off-topic, build a **negative filter** string:
   - Identify the collision domain (e.g., bacterial, agricultural, chemical)
   - Construct: `NOT [collision_term_1] NOT [collision_term_2] ...`
5. Record the collision warning and negative filter in output.

**Exit Criteria:**
- [ ] Collision risk assessed (none / low / high)
- [ ] If high: negative filter string constructed
- [ ] Off-topic rate documented

---

### Stage 5: Output Assembly

**Objective:** Produce the structured resolution output for downstream skills.

**Steps:**
1. Assemble the **Entity Identity Table**:

```markdown
## Entity Identity: {Official Name}

| Field | Value |
|-------|-------|
| **Input** | {original user input} |
| **Official Symbol/Name** | {HGNC symbol / INN / disease name} |
| **Ensembl Gene ID** | {ENSG...} |
| **UniProt Accession** | {accession} |
| **NCBI Entrez ID** | {ID} |
| **ChEMBL ID** | {CHEMBL...} |
| **EFO/MONDO ID** | {EFO_... / MONDO_...} |
| **Synonyms** | {comma-separated list} |
| **Collision Risk** | {none / low / HIGH} |
| **Negative Filter** | {NOT term1 NOT term2} |
```

2. Include only rows relevant to the entity type (omit gene fields for drugs, etc.).
3. Pass the identity table and collision metadata to the requesting skill.

**Exit Criteria:**
- [ ] Identity table complete with all available IDs
- [ ] Collision status and filter (if any) documented
- [ ] Output consumable by downstream skill (target-intelligence, drug-intelligence, literature-review, target-validation)

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Cross-referenced IDs per entity | 2 | 4 | 6+ |
| Collision detection for high-risk symbols | Yes/No flag | Negative filter built | Off-topic rate quantified |
| Resolution latency (tool calls) | <=5 | <=3 | 1 (cache hit) |

**Completion Checklist:**
- [ ] Primary canonical ID obtained and verified
- [ ] Cross-references populated (>=2 independent ID sources)
- [ ] Collision risk assessed for all gene/protein entities
- [ ] Negative filter constructed if collision rate >20%
- [ ] Identity table formatted and passed to requesting skill

</success_criteria>

<scope>
## Scope

**In Scope:**
- Gene symbols → Ensembl, UniProt, HGNC, Entrez
- Drug/compound names → ChEMBL, PubChem, DrugBank
- Disease names → EFO, MONDO, OMIM
- Collision detection and negative filter construction
- Synonym collection for search expansion

**Out of Scope** (use specialized resources):
- Pathway resolution (e.g., "MAPK signaling") → handle inline in `target-intelligence`
- Cell type resolution → handle inline in requesting skill
- Organism-specific disambiguation beyond human → not supported
- Full literature search → use `literature-review` after resolution

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Skipping Collision Detection for Short Symbols

**Anti-pattern:**
Proceeding directly to literature search with "ACE" without checking if results are about ACE gene, ACE inhibitor drugs, or angiotensin-converting enzyme.

**Solution:**
Always run Stage 4 for symbols <=4 characters or those in the known collisions catalog. Build negative filters before any literature queries.

---

### 2. Using Only One ID Source

**Anti-pattern:**
Getting an Ensembl ID from Open Targets and treating it as verified without cross-referencing against UniProt or HGNC.

**Solution:**
Always cross-reference through at least two independent sources. IDs should be consistent — if UniProt maps to a different Ensembl ID than Open Targets returned, investigate.

---

### 3. Hardcoding Tool Names Instead of Capabilities

**Anti-pattern:**
Writing `call mygene_query(...)` directly in a skill instead of referencing the capability.

**Solution:**
Reference `tool-lookup.yaml` capabilities (e.g., `disambiguation.gene_to_ensembl`). Use the primary tier first, fall back to tooluniverse tier, then fallback tier. This keeps skills functional regardless of which MCPs are installed.

</anti_patterns>

<templates>
## Output Templates

### Template 1: Gene/Protein Identity

```markdown
## Entity Identity: {HGNC_SYMBOL} ({Full Name})

| Field | Value |
|-------|-------|
| **Input** | {original input} |
| **HGNC Symbol** | {symbol} |
| **Full Name** | {approved name} |
| **Ensembl Gene ID** | {ENSG...} |
| **Ensembl Protein ID** | {ENSP...} |
| **UniProt Accession** | {accession} |
| **NCBI Entrez ID** | {ID} |
| **ChEMBL Target ID** | {CHEMBL...} |
| **Synonyms** | {aliases} |
| **Collision Risk** | {none/low/HIGH} |
| **Negative Filter** | {filter string or "N/A"} |
```

### Template 2: Drug/Compound Identity

```markdown
## Entity Identity: {INN} ({Brand Names})

| Field | Value |
|-------|-------|
| **Input** | {original input} |
| **INN (Generic Name)** | {name} |
| **ChEMBL ID** | {CHEMBL...} |
| **PubChem CID** | {CID} |
| **DrugBank ID** | {DB...} |
| **CAS Number** | {CAS} |
| **SMILES** | {canonical SMILES} |
| **Trade Names** | {comma-separated} |
| **Collision Risk** | {none/low/HIGH} |
```

### Template 3: Disease Identity

```markdown
## Entity Identity: {Disease Name}

| Field | Value |
|-------|-------|
| **Input** | {original input} |
| **Preferred Name** | {official name} |
| **EFO ID** | {EFO_...} |
| **MONDO ID** | {MONDO_...} |
| **OMIM** | {OMIM ID if genetic} |
| **Synonyms** | {aliases} |
| **Collision Risk** | {none/low/HIGH} |
| **Negative Filter** | {filter string or "N/A"} |
```

</templates>

<cross_references>
## Cross-References

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

### Feeds (Output To)

| Skill | Relationship |
|-------|-------------|
| `target-intelligence` | Provides verified gene/protein IDs and collision filters for target profiling |
| `drug-intelligence` | Provides verified drug/compound IDs for compound profiling |
| `literature-review` | Provides collision-aware search filters for literature queries |
| `target-validation` | Provides canonical IDs for multi-source evidence integration |

### Uses (Input From)

| Skill | Relationship |
|-------|-------------|
| `tool-lookup` (reference) | Resolves capability keys to specific tool names and parameters |

### Related

| Skill | Relationship |
|-------|-------------|
| `paper-search` | Both handle query construction; entity-resolution provides disambiguation that paper-search can use |

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `references/known_collisions.md` | Catalog of gene symbols with documented naming collisions |
| `../shared/tool-lookup.yaml` | Capability-to-tool mapping with parameter notes |
| `../shared/references/known_param_corrections.md` | ToolUniverse API parameter quirks |

</references>
