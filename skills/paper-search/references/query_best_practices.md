# Query Best Practices

> How to construct effective academic paper searches

This guide covers universal principles for building effective queries across all databases.

---

## Core Principles

### 1. Start Broad, Then Narrow
Begin with broader terms and refine based on results:

```bash
# Too narrow (might miss relevant papers)
python search.py "CRISPR-Cas9 HDR sickle cell HBB gene therapy" --source pubmed

# Better: Start broad
python search.py "CRISPR sickle cell therapy" --source pubmed --max 100

# Then refine based on results
python search.py "CRISPR sickle cell gene therapy" --source pubmed --type "Review"
```

### 2. Use Synonyms and Variants
Different authors use different terminology:

```bash
# Include alternative terms
python search.py "machine learning OR deep learning drug discovery" --source semantic

# Gene names have aliases
python search.py "TP53 OR p53 cancer" --source pubmed
```

### 3. Combine Concepts Strategically
Use AND to require terms, OR to expand options:

```bash
# All terms required
python search.py "CRISPR AND delivery AND therapeutic" --source pubmed

# Any of these terms
python search.py "nanoparticle OR lipid delivery" --source pubmed
```

---

## Query Syntax by Database

### PubMed (Boolean + MeSH)
PubMed supports advanced syntax through NCBI E-utilities:

```bash
# Basic Boolean
python search.py "CRISPR AND therapy" --source pubmed

# Field tags (when passed to PubMed)
python search.py "Smith[Author] CRISPR[Title]" --source pubmed

# Publication types (via --type flag)
python search.py "gene therapy" --source pubmed --type "Review,Clinical Trial"

# Date filtering
python search.py "COVID-19 vaccine" --source pubmed --date 2020:2023
```

**MeSH Tip**: PubMed automatically maps terms to MeSH headings. For precision, use:
- `[MeSH Terms]` for controlled vocabulary
- `[Title/Abstract]` for keyword matching only

### Semantic Scholar
Simple keyword matching with optional filters:

```bash
# Keywords (automatic relevance ranking)
python search.py "transformer attention mechanism" --source semantic

# Year filtering
python search.py "neural network" --source semantic --date 2020:2024

# Field filtering
python search.py "machine learning" --source semantic --fields "Biology,Medicine"

# Citation threshold
python search.py "BERT" --source semantic --min-citations 500
```

### bioRxiv/medRxiv
Keyword matching in titles and abstracts:

```bash
# Keywords automatically searched in title/abstract
python search.py "single cell sequencing" --source biorxiv

# Date range (defaults to last 30 days)
python search.py "RNA seq" --source biorxiv --date 2024-01-01:2024-12-31

# Note: Use --source medrxiv for medical preprints
python search.py "clinical trial COVID" --source medrxiv
```

### Google Scholar
Broad keyword matching:

```bash
# Simple keywords
python search.py "deep learning protein structure" --source scholar

# Year filtering
python search.py "AlphaFold" --source scholar --date 2021:2024
```

---

## Common Patterns

### 1. Finding Reviews
Start with review articles for topic overview:

```bash
# PubMed (using publication type)
python search.py "CRISPR delivery" --source pubmed --type "Review" --max 50

# Semantic Scholar (often titled with "review")
python search.py "CRISPR delivery review" --source semantic
```

### 2. Finding Recent Papers
Get the latest research on a topic:

```bash
# Last 2 years
python search.py "CAR-T cell therapy" --source pubmed --date 2023:2024

# Latest preprints (bioRxiv defaults to last 30 days)
python search.py "CAR-T" --source biorxiv
```

### 3. Finding Highly-Cited Papers
Identify seminal works in a field:

```bash
# Semantic Scholar with citation filter
python search.py "attention is all you need" --source semantic --min-citations 1000

# Google Scholar sorts by relevance (often correlates with citations)
python search.py "deep learning" --source scholar --max 20
```

### 4. Author-Specific Search
Find papers by a specific researcher:

```bash
# PubMed author search
python search.py "Doudna JA[Author] CRISPR" --source pubmed

# Semantic Scholar (in query terms)
python search.py "Doudna CRISPR" --source semantic
```

### 5. Multi-Database Comprehensive Search
For systematic reviews or thorough coverage:

```bash
# Search all sources
python search.py "gene therapy sickle cell" \
  --source pubmed,biorxiv,semantic \
  --date 2020:2024 \
  --max 100 \
  --output comprehensive_search.json
```

---

## Avoiding Common Mistakes

### 1. Over-Specified Queries
**Problem**: Too many required terms misses relevant papers

```bash
# Too specific
python search.py "CRISPR-Cas9 homology-directed repair HBB gene sickle cell anemia therapy clinical"

# Better: Core concepts only
python search.py "CRISPR sickle cell therapy"
```

### 2. Under-Specified Queries
**Problem**: Too broad returns irrelevant results

```bash
# Too broad
python search.py "gene" --source pubmed  # Millions of results

# Better: Add specificity
python search.py "gene therapy CRISPR" --source pubmed
```

### 3. Ignoring Field Differences
**Problem**: Same concept, different terminology across fields

```bash
# Biology term
python search.py "knockout mouse" --source pubmed

# Also search clinical terminology
python search.py "gene inactivation OR gene knockout mouse" --source pubmed
```

### 4. Missing Preprints
**Problem**: Only searching published literature misses recent work

```bash
# Published only
python search.py "new technique" --source pubmed

# Better: Include preprints
python search.py "new technique" --source pubmed,biorxiv
```

---

## Query Templates by Use Case

### Systematic Review Query
```bash
python search.py "(CRISPR OR gene editing) AND (therapy OR treatment) AND (clinical OR patient)" \
  --source pubmed,semantic \
  --date 2018:2024 \
  --max 200 \
  --output systematic_review_results.json
```

### Competitive Landscape
```bash
# Find all papers from competing research groups
python search.py "CAR-T cell therapy" \
  --source pubmed \
  --date 2023:2024 \
  --max 500 \
  --format json \
  --output competitive_landscape.json
```

### Technology Assessment
```bash
# Reviews from PubMed + high-impact papers from Semantic Scholar
# Note: --type only filters PubMed results; --min-citations only filters Semantic Scholar
python search.py "CRISPR base editing" \
  --source pubmed,semantic \
  --type "Review" \
  --min-citations 50 \
  --output tech_assessment.json

# Alternative: Run separate searches for clearer filtering
python search.py "CRISPR base editing" --source pubmed --type "Review" -o pubmed_reviews.json
python search.py "CRISPR base editing" --source semantic --min-citations 50 -o high_impact.json
```

### Grant Background Research
```bash
# Comprehensive recent literature
python search.py "your research topic" \
  --source all \
  --date 2021:2024 \
  --max 100 \
  --format text \
  --output grant_background.txt
```

---

## Output Format Recommendations

| Use Case | Recommended Format | Why |
|----------|-------------------|-----|
| Import to reference manager | `--format bibtex` | Direct import to Zotero, EndNote, etc. |
| Manual review of results | `--format text` | Human-readable list |
| Data analysis/processing | `--format json` | Machine-readable, includes all metadata |
| Sharing with collaborators | `--format text` + `--output file.txt` | Easy to read and share |

---

## See Also

- [Database Selection Guide](./database_selection.md) - Choosing the right database
- [PubMed Search Syntax](../sources/pubmed/references/search_syntax.md) - Detailed MeSH/Boolean syntax
- [Semantic Scholar API Guide](../sources/semantic_scholar/references/api_guide.md) - Advanced S2 features
