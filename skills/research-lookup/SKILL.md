---
name: research-lookup
description: "Search academic papers, current research, and technical documentation with automatic citation generation"
when_to_use: "literature search, find papers, research lookup, recent studies, citation sources, verify claims, academic search, scientific literature, find references"
version: 2.3.0
allowed-tools: [Read, Write, Edit, Bash, WebSearch]
---

# Research Information Lookup

Real-time research lookup using Perplexity's Sonar models through OpenRouter. Intelligently selects between **Sonar Pro Search** (fast lookup) and **Sonar Reasoning Pro** (deep analysis) based on query complexity.

## Prerequisites

- **API Key**: `OPENROUTER_API_KEY` environment variable must be set
- **Account**: OpenRouter account with sufficient credits

**Verify setup before querying:**
```bash
echo $OPENROUTER_API_KEY | head -c 10  # Should show key prefix
```

---

## Core Capabilities

### 1. Academic Research Queries

Search academic literature for recent papers, studies, and reviews:

```
Query Structure: [Topic] + [Specific Aspect] + [Time Frame] + [Type]

Examples:
- "CRISPR gene editing off-target effects 2024 clinical trials"
- "Alzheimer's disease treatment latest clinical trials"
- "Machine learning drug discovery systematic review 2023-2024"
```

**Output includes:**
- Summary of key findings (3-5 most relevant papers)
- Complete citations with authors, titles, journals, years, DOIs
- Key statistics and findings highlighted
- Research gaps or controversies identified

### 2. Technical and Methodological Information

Find protocols, specifications, and methodologies:

```
Examples:
- "Western blot protocol protein detection"
- "RNA sequencing library preparation methods"
- "Statistical power analysis clinical trials"
```

**Output includes:**
- Step-by-step procedures
- Required materials and equipment
- Critical parameters and troubleshooting
- References to standard protocols

### 3. Statistical Data

Look up current statistics and research data:

```
Examples:
- "Prevalence diabetes US population 2024"
- "Global renewable energy adoption statistics"
- "AI adoption healthcare industry survey 2024"
```

**Output includes:**
- Current statistics with dates and sources
- Methodology and confidence intervals
- Year-over-year comparisons
- Citations to original surveys

### 4. Citation Discovery

Locate papers for manuscript citations:

```
Examples:
- "Foundational papers transformer architecture"
- "Seminal works quantum computing"
- "Landmark trials cancer immunotherapy"
```

**Output includes:**
- 5-10 most influential papers
- Complete citation info (authors, title, journal, year, DOI)
- Brief description of each paper's contribution
- Impact metrics when available

---

## Model Selection

The skill automatically selects the optimal model based on query complexity.

| Query Type | Model | Triggers |
|------------|-------|----------|
| Fact lookup, statistics, protocols | Sonar Pro Search | Simple, direct queries |
| Comparative analysis, mechanisms | Sonar Reasoning Pro | Keywords: compare, explain, analyze, mechanism, trade-offs |

**For detailed selection logic and manual override options, see `{baseDir}/references/model_selection.md`.**

### Quick Override

```bash
# Force fast search
python {baseDir}/scripts/research_lookup.py "query" --force-model pro

# Force deep analysis
python {baseDir}/scripts/research_lookup.py "query" --force-model reasoning
```

---

## Validation Workflow

**Critical: Verify citations before including in manuscripts.**

### Step 1: Execute Query

```bash
python {baseDir}/scripts/research_lookup.py "your structured query"
```

### Step 2: Verify Citations

For each citation returned, verify DOI and metadata:

```
Use WebSearch to confirm:
1. DOI resolves correctly (https://doi.org/[DOI])
2. Author names match
3. Publication year is correct
4. Journal name is accurate
```

### Step 3: Cross-Reference

For critical claims, triangulate across 2-3 sources before treating as reliable.

### Step 4: Document Search Strategy

Record query terms and databases searched for reproducibility.

---

## Query Best Practices

### Structured Query Format

```
[Topic] + [Specific Aspect] + [Time Frame] + [Information Type]
```

**Good queries:**
- "CRISPR gene editing + off-target effects + 2024 + clinical trials"
- "Quantum computing + error correction + recent advances + review papers"

**Poor queries:**
- "Tell me about AI" (too broad)
- "Cancer research" (lacks specificity)

### Reasoning Keywords

Add these words to trigger deeper analysis:
- Comparative: `compare`, `contrast`, `versus`, `differences`
- Analytical: `analyze`, `evaluate`, `critique`
- Causal: `mechanism`, `explain`, `why`, `how does`
- Synthesis: `meta-analysis`, `systematic review`, `integrate`

---

## Technical Configuration

### OpenRouter Integration

| Setting | Value |
|---------|-------|
| Models | `perplexity/sonar-pro-search`, `perplexity/sonar-reasoning-pro-online` |
| Search Mode | Academic/scholarly (prioritizes peer-reviewed sources) |
| Search Context | `high` for comprehensive results |
| Context Window | 200K+ tokens |

### Source Prioritization

1. Peer-reviewed academic papers and journals
2. Institutional sources (universities, government agencies)
3. Recent publications (last 2-3 years preferred)
4. High-impact journals and conferences
5. Primary research over secondary sources

### Citation Standards

All responses include:
- Complete bibliographic information
- DOI or stable URLs when available
- Access dates for web sources
- Clear attribution of quotes and data

---

## Error Handling

### Known Limitations

| Limitation | Workaround |
|------------|------------|
| Information cutoff (training data) | Include preprint servers for very recent work |
| Paywall content | May not access full text; use DOI to find access |
| Emerging research | May miss papers not yet indexed |
| Specialized databases | Cannot access proprietary databases |

### Error Recovery

| Error | Action |
|-------|--------|
| No results | Broaden terms, try synonyms, check alternate databases |
| Too many results (>50) | Add specificity: timeframe, study type, outcome measure |
| API rate limit | Wait and retry; consider batch optimization |
| Query ambiguous | Break into simpler components |

### Fallback Strategies

1. Rephrase queries for better clarity
2. Break complex queries into simpler components
3. Use broader time frames if recent data unavailable
4. Cross-reference with multiple query variations

---

## Integration with Scientific Writing

| Writing Phase | How research-lookup Helps |
|---------------|---------------------------|
| Introduction | Literature for background and context |
| Methods | Verify protocols against current standards |
| Results | Compare findings with similar studies |
| Discussion | Support arguments with latest evidence |
| References | Properly formatted citations |

---

## Complementary Tools

| Task | Tool |
|------|------|
| Find academic papers | research-lookup |
| Deep analysis/comparison | research-lookup (Sonar Reasoning Pro) |
| Verify DOI/metadata | WebSearch |
| Check publication year | WebSearch |
| Find journal volume/pages | WebSearch |
| Current events/news | WebSearch |

---

## Academic Integrity

- **Cite original sources**, not the AI tool
- **Verify all citations** against primary sources before use
- **Read abstracts at minimum** for every paper cited
- **Document search strategies** for reproducibility
- **Follow institutional guidelines** for AI tool usage
- **Never use to bypass paywalls** or subscriptions

---

## Reference Documents

| Document | Content |
|----------|---------|
| `{baseDir}/references/model_selection.md` | Detailed model selection logic, complexity scoring, override options |
| `{baseDir}/references/bioinformatics_databases.md` | Bioinformatics-specific databases: NCBI, UniProt, PDB, KEGG, etc. |
| `{baseDir}/references/expert_guide.md` | Expert patterns, failure modes, quality signals |

---

## Cross-References

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

### Feeds (Output To)

| Skill | Relationship |
|-------|-------------|
| `scientific-writing` | Literature for Introduction, Discussion, and citations |
| `literature-review` | Papers for systematic synthesis and analysis |
| `hypothesis-generation` | Evidence to ground research hypotheses |
| `scientific-slides` | Citations and background for presentations |
| `citation-management` | Discovered citations for organization and formatting |
| `research-paper-summarizer` | For comprehensive paper analysis beyond quick lookup |

### Related

| Skill | Relationship |
|-------|-------------|
| `statistical-analysis` | Finding appropriate statistical methods and benchmarks |
| `reproducible-research` | Data deposition standards and repository discovery |
