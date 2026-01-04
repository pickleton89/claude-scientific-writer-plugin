---
name: paper-search
version: 1.0.0
description: "Find academic papers across multiple databases (PubMed, bioRxiv, Semantic Scholar, Google Scholar) using a unified search interface with structured queries, date filtering, and multiple output formats."
when_to_use: "Searching for academic papers across any scale (1-100+ papers), executing database-specific queries, or performing comprehensive multi-database searches for literature reviews"
allowed-tools: [Read, Write, Edit, Bash, WebFetch]
---

# Paper Search

<overview>
Search for academic papers across multiple databases through a single unified interface. This skill provides access to PubMed (biomedical), bioRxiv/medRxiv (preprints), Semantic Scholar (200M+ cross-domain papers), and Google Scholar (broad coverage). Supports Boolean queries, date filtering, publication type filters, citation-based filtering, and outputs in JSON, BibTeX, or human-readable text format with automatic DOI-based deduplication across sources.
</overview>

<prerequisites>
## Prerequisites

**Required:**
- **Python 3.8+**: For running search scripts

**Python Dependencies:**
```bash
pip install requests
```

**Optional (for extended functionality):**
```bash
# For Google Scholar (scraping-based)
pip install scholarly

# For enhanced rate limits
export NCBI_API_KEY="your_key"         # PubMed: 10 req/sec vs 3
export SEMANTIC_SCHOLAR_API_KEY="key"  # S2: recommended for heavy use
```

**API Keys (Optional but Recommended):**

| Service | How to Get | Benefit |
|---------|-----------|---------|
| NCBI (PubMed) | https://www.ncbi.nlm.nih.gov/account/settings/ | 10 req/sec (vs 3) |
| Semantic Scholar | https://www.semanticscholar.org/product/api | Higher rate limits |

</prerequisites>

<scripts>
## Unified Search CLI

The primary interface is `{baseDir}/scripts/search.py`:

```bash
python {baseDir}/scripts/search.py "query" [options]
```

**Basic Usage:**
```bash
# Search PubMed
python {baseDir}/scripts/search.py "CRISPR gene therapy" --source pubmed

# Search multiple databases
python {baseDir}/scripts/search.py "protein folding" --source pubmed,semantic

# Search all databases with deduplication
python {baseDir}/scripts/search.py "CAR-T cell" --source all --output results.json
```

**CLI Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `--source, -s` | Database(s) to search | `pubmed`, `biorxiv,semantic`, `all` |
| `--max, -m` | Max results per source (default: 20) | `--max 50` |
| `--date, -d` | Date range filter | `2024`, `2023:2024`, `2023-01-01:2024-12-31` |
| `--type, -t` | Publication type (PubMed only) | `"Review,Clinical Trial"` |
| `--fields` | Field of study (Semantic Scholar only) | `"Biology,Medicine"` |
| `--min-citations` | Min citations (Semantic Scholar only) | `--min-citations 50` |
| `--open-access` | Open access only (Semantic Scholar only) | `--open-access` |
| `--format, -f` | Output format | `json`, `bibtex`, `text` |
| `--output, -o` | Output file path | `--output results.json` |
| `--no-dedupe` | Disable DOI deduplication | `--no-dedupe` |

**Source Modules:**
Individual database modules are available in `{baseDir}/sources/` for direct use:

| Module | Class | Usage |
|--------|-------|-------|
| `pubmed/search.py` | `PubMedSearcher` | Biomedical literature |
| `biorxiv/search.py` | `BioRxivSearcher` | Biology/medicine preprints |
| `semantic_scholar/search.py` | `SemanticScholarSearcher` | Cross-domain search |
| `google_scholar/search.py` | `GoogleScholarSearcher` | Broad coverage |

</scripts>

<when_to_use>
## Trigger Conditions

**Use this skill when:**
- Searching for papers on a topic (any scale: 1-100+ papers)
- Need structured queries (MeSH terms, Boolean operators, field tags)
- Searching specific databases (PubMed, bioRxiv, Semantic Scholar)
- Finding preprints before peer review
- Cross-database search for comprehensive coverage
- Building a reference list for a manuscript
- Discovering highly-cited papers in a field
- Supporting literature-review skill Stage 2 (Systematic Search)

**Do NOT use this skill when:**
- Formatting existing citations → use `citation-management`
- Validating DOIs or citation accuracy → use `citation-management`
- Conducting full systematic review methodology → use `literature-review`
- Writing the literature review section → use `scientific-writing`
- Converting PDFs to text → use `markitdown`

</when_to_use>

<decision_framework>
## Quick Reference: Database Selection

| Research Domain | Primary | Secondary | Notes |
|-----------------|---------|-----------|-------|
| **Biomedical/Clinical** | PubMed | Semantic Scholar | PubMed has MeSH, clinical trials |
| **Biology (Bench)** | PubMed + bioRxiv | Semantic Scholar | bioRxiv for latest preprints |
| **Medical Research** | PubMed + medRxiv | Semantic Scholar | medRxiv for clinical preprints |
| **Neuroscience** | PubMed | bioRxiv, Semantic Scholar | Strong in all three |
| **Computer Science/AI** | Semantic Scholar | Google Scholar | S2 specializes here |
| **Cross-Domain** | Semantic Scholar | Multiple | 200M+ papers |
| **Humanities/Social** | Google Scholar | Semantic Scholar | Best for books, non-STEM |

**Source Selection Matrix:**

| Source | Flag | Best For | Rate Limit |
|--------|------|----------|------------|
| PubMed | `--source pubmed` | Biomedical, clinical, MeSH queries | 3-10 req/sec |
| bioRxiv | `--source biorxiv` | Biology preprints | ~30 req/min |
| medRxiv | `--source medrxiv` | Medical preprints | ~30 req/min |
| Semantic Scholar | `--source semantic` | Cross-domain, citations | 100 req/5min |
| Google Scholar | `--source scholar` | Broad coverage | Variable |
| All | `--source all` | Comprehensive (deduplicated) | Combined |

> **Full decision frameworks:** See [`references/database_selection.md`]({baseDir}/references/database_selection.md) for complete database profiles, overlap analysis, and multi-source strategies.

</decision_framework>

<workflow>
## Workflow

### Stage 1: Define Search Strategy

**Objective:** Determine databases and query structure

**Steps:**
1. Identify research domain (biomedical, CS, cross-domain, etc.)
2. Select primary database based on domain (see Database Selection Matrix)
3. Decide if preprints needed (add bioRxiv/medRxiv)
4. Decide if comprehensive coverage needed (use `--source all`)
5. Construct query with Boolean operators if needed

**Query Construction Tips:**
- Use AND to require terms: `"CRISPR AND therapy"`
- Use OR for synonyms: `"machine learning OR deep learning"`
- Start broad, then narrow based on results

**Exit Criteria:**
- [ ] Database(s) selected
- [ ] Query terms identified
- [ ] Date range determined (if applicable)

---

### Stage 2: Execute Search

**Objective:** Run search and collect results

**Steps:**
1. Run search with appropriate flags:
   ```bash
   python {baseDir}/scripts/search.py "your query" \
     --source pubmed \
     --max 50 \
     --date 2020:2024 \
     --output results.json
   ```

2. Review result count—adjust query if needed:
   - Too few: Broaden terms, add synonyms
   - Too many: Add more specific terms, narrow date range

3. For comprehensive searches, use multiple sources:
   ```bash
   python {baseDir}/scripts/search.py "your query" \
     --source pubmed,biorxiv,semantic \
     --max 100 \
     --output comprehensive.json
   ```

**Exit Criteria:**
- [ ] Search executed successfully
- [ ] Result count is reasonable for needs
- [ ] Results saved to file (if needed)

---

### Stage 3: Export and Use Results

**Objective:** Format results for downstream use

**Output Format Selection:**

| Use Case | Format | Command |
|----------|--------|---------|
| Import to Zotero/EndNote | BibTeX | `--format bibtex -o refs.bib` |
| Data analysis | JSON | `--format json -o data.json` |
| Manual review | Text | `--format text -o papers.txt` |
| Quick scan | Text (stdout) | `--format text` |

**Integration with Other Skills:**

```bash
# For literature-review Stage 2
python {baseDir}/scripts/search.py "query" --source pubmed,biorxiv \
  --max 100 --format json --output search_results.json

# For citation-management (get BibTeX)
python {baseDir}/scripts/search.py "query" --source pubmed \
  --max 20 --format bibtex --output references.bib
```

**Exit Criteria:**
- [ ] Results exported in desired format
- [ ] File accessible for next workflow step

</workflow>

<examples>
## Usage Examples

### Quick PubMed Search
```bash
python {baseDir}/scripts/search.py "CRISPR sickle cell therapy" \
  --source pubmed \
  --max 20
```

### Find Reviews
```bash
python {baseDir}/scripts/search.py "CAR-T cell therapy" \
  --source pubmed \
  --type "Review" \
  --date 2020:2024 \
  --max 50
```

### Latest Preprints
```bash
python {baseDir}/scripts/search.py "single cell RNA sequencing" \
  --source biorxiv \
  --date 2024: \
  --max 30
```

### Highly-Cited Papers
```bash
python {baseDir}/scripts/search.py "transformer attention mechanism" \
  --source semantic \
  --min-citations 500 \
  --max 20
```

### Comprehensive Multi-Database Search
```bash
python {baseDir}/scripts/search.py "gene therapy delivery" \
  --source pubmed,biorxiv,semantic \
  --date 2022:2024 \
  --max 100 \
  --format json \
  --output comprehensive_search.json
```

### Export BibTeX for Reference Manager
```bash
python {baseDir}/scripts/search.py "CRISPR therapeutics" \
  --source pubmed \
  --max 30 \
  --format bibtex \
  --output references.bib
```

### Search All Databases (Deduplicated)
```bash
python {baseDir}/scripts/search.py "protein folding AlphaFold" \
  --source all \
  --date 2021:2024 \
  --max 50 \
  --format text
```

</examples>

<success_criteria>
## Success Criteria

**Search Quality Indicators:**

| Metric | Acceptable | Good | Comprehensive |
|--------|------------|------|---------------|
| Sources searched | 1 | 2-3 | 4+ (all) |
| Result relevance | >50% | >70% | >80% |
| Deduplication | None | DOI-based | DOI + title |
| Output format | Stdout | Single file | Multiple formats |

**Completion Checklist:**
- [ ] Search executed without errors
- [ ] Result count appropriate for needs
- [ ] Results exported in usable format
- [ ] Multi-source searches deduplicated
- [ ] Dates and filters applied correctly

</success_criteria>

<scope>
## Scope

**In Scope:**
- Multi-database academic paper search
- Boolean and keyword queries
- Date range filtering
- Publication type filtering (PubMed)
- Citation count filtering (Semantic Scholar)
- Field of study filtering (Semantic Scholar)
- Open access filtering (Semantic Scholar)
- JSON, BibTeX, and text output
- DOI-based deduplication
- Preprint search (bioRxiv, medRxiv)

**Out of Scope** (use other skills):
- Citation validation and metadata verification → `citation-management`
- BibTeX formatting and cleanup → `citation-management`
- Systematic review methodology (PRISMA, screening) → `literature-review`
- Full-text retrieval → manual or institutional access
- Meta-analysis calculations → `statistical-analysis`
- Writing literature review sections → `scientific-writing`

</scope>

<best_practices>
## Best Practices

| Practice | Recommendation |
|----------|----------------|
| Query construction | Start broad, narrow iteratively |
| Synonyms | Include OR alternatives for key terms |
| Database selection | Match to research domain |
| Preprint inclusion | Add bioRxiv for cutting-edge topics |
| Date filtering | Use for recent advances or historical context |
| Result count | 20-50 for quick search, 100+ for comprehensive |
| Output format | BibTeX for reference managers, JSON for analysis |
| Deduplication | Keep enabled for multi-source searches |

**Query Best Practices:**
- Use AND to require concepts: `"CRISPR AND delivery AND nanoparticle"`
- Use OR for synonyms: `"machine learning OR deep learning"`
- Include gene aliases: `"TP53 OR p53"`
- Field tags (PubMed): `"Smith[Author] CRISPR[Title]"`

> **Detailed guidance:** See [`references/query_best_practices.md`]({baseDir}/references/query_best_practices.md) for query templates and common patterns.

</best_practices>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `literature-review` | Uses paper-search for Stage 2 (Systematic Search) |
| `citation-management` | Use for validating and formatting search results |
| `scientific-writing` | Use results to write literature sections |
| `research-paper-summarizer` | Summarize individual papers from search results |
| `venue-templates` | Format for specific journal requirements |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Workflow Integration:**
```
paper-search → citation-management → scientific-writing
     ↓
literature-review (comprehensive reviews)
```

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| [`references/database_selection.md`]({baseDir}/references/database_selection.md) | Database profiles, decision matrix, overlap analysis |
| [`references/query_best_practices.md`]({baseDir}/references/query_best_practices.md) | Query construction, templates, common patterns |
| [`references/bioinformatics_databases.md`]({baseDir}/references/bioinformatics_databases.md) | Specialized bioinformatics database reference |

**Source-Specific Documentation:**

| Database | Documentation |
|----------|---------------|
| PubMed | [`sources/pubmed/references/search_syntax.md`]({baseDir}/sources/pubmed/references/search_syntax.md) |
| bioRxiv | [`sources/biorxiv/references/search_guide.md`]({baseDir}/sources/biorxiv/references/search_guide.md) |
| Semantic Scholar | [`sources/semantic_scholar/references/api_guide.md`]({baseDir}/sources/semantic_scholar/references/api_guide.md) |
| Google Scholar | [`sources/google_scholar/references/google_scholar_search.md`]({baseDir}/sources/google_scholar/references/google_scholar_search.md) |

## External Resources

| Resource | URL |
|----------|-----|
| PubMed | https://pubmed.ncbi.nlm.nih.gov/ |
| PubMed E-utilities | https://www.ncbi.nlm.nih.gov/books/NBK25501/ |
| MeSH Browser | https://meshb.nlm.nih.gov/search |
| bioRxiv | https://www.biorxiv.org/ |
| bioRxiv API | https://api.biorxiv.org/ |
| Semantic Scholar | https://www.semanticscholar.org/ |
| Semantic Scholar API | https://api.semanticscholar.org/ |

</references>
