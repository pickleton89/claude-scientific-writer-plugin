# Database Selection Guide

> Which academic database should you search?

This guide helps you choose the right database(s) for your research needs.

---

## Quick Decision Matrix

| Research Domain | Primary Database | Secondary | Notes |
|-----------------|-----------------|-----------|-------|
| **Biomedical/Clinical** | PubMed | Semantic Scholar | PubMed has MeSH indexing, clinical trials |
| **Biology (Bench Science)** | PubMed + bioRxiv | Semantic Scholar | bioRxiv for latest preprints |
| **Medical Research** | PubMed + medRxiv | Semantic Scholar | medRxiv for clinical preprints |
| **Neuroscience** | PubMed | bioRxiv, Semantic Scholar | Strong coverage in all three |
| **Computer Science/AI** | Semantic Scholar | Google Scholar | Semantic Scholar specializes here |
| **Physics/Mathematics** | Semantic Scholar | Google Scholar | arXiv papers included |
| **Chemistry** | Semantic Scholar | PubMed | PubMed for biochemistry |
| **Social Sciences** | Semantic Scholar | Google Scholar | Broader coverage |
| **Humanities** | Google Scholar | Semantic Scholar | Best for books, non-STEM |
| **Cross-Domain Search** | Semantic Scholar | Multiple sources | 200M+ papers across fields |

---

## Database Profiles

### PubMed (NCBI)
**Best for**: Biomedical sciences, clinical research, life sciences

**Strengths**:
- MeSH (Medical Subject Headings) controlled vocabulary
- Clinical trial registration linkage
- High-quality biomedical indexing
- Publication type filters (Review, Clinical Trial, Meta-Analysis)
- Free, no API key required (but key recommended for higher rate limits)

**Limitations**:
- Biomedical focus only
- Newer papers may lack MeSH terms initially
- Preprints not indexed

**Typical use case**:
```bash
python search.py "CRISPR sickle cell therapy" \
  --source pubmed \
  --type "Clinical Trial,Review" \
  --date 2020:2024
```

---

### bioRxiv/medRxiv
**Best for**: Preprints, cutting-edge research before peer review

**Strengths**:
- Access to research months before publication
- Biology (bioRxiv) and medical (medRxiv) preprints
- Subject category filtering
- Direct PDF access

**Limitations**:
- Not peer-reviewed
- Limited to preprints only
- Keyword-based filtering (no MeSH)
- May contain preliminary/unvalidated findings

**Typical use case**:
```bash
python search.py "single cell sequencing" \
  --source biorxiv \
  --date 2024: \
  --max 50
```

---

### Semantic Scholar
**Best for**: Cross-domain research, citation analysis, comprehensive coverage

**Strengths**:
- 200+ million papers across all fields
- Citation graph navigation (who cited whom)
- Influential citation scoring
- Open access PDF filtering
- Author lookup and paper graphs
- Strong CS/AI coverage

**Limitations**:
- Metadata quality varies
- Some newer papers may be missing
- Rate limited without API key

**Typical use case**:
```bash
python search.py "transformer protein folding" \
  --source semantic \
  --fields "Biology,Computer Science" \
  --min-citations 50
```

---

### Google Scholar
**Best for**: Comprehensive coverage, citation counts, non-traditional sources

**Strengths**:
- Broadest coverage including books, theses, patents
- Citation count tracking
- Includes non-English sources
- Covers humanities well

**Limitations**:
- Scraping-based (can be rate-limited)
- Requires `scholarly` library
- Quality control is minimal
- No official API

**Typical use case**:
```bash
python search.py "machine learning drug discovery" \
  --source scholar \
  --max 50
```

---

## Multi-Source Search Strategies

### Comprehensive Literature Review
For systematic reviews or comprehensive searches, use multiple sources:

```bash
python search.py "CAR-T cell therapy" \
  --source pubmed,biorxiv,semantic \
  --date 2020:2024 \
  --max 100 \
  --output comprehensive_results.json
```

### Preprint + Published Comparison
To compare preprints with published literature:

```bash
# Published papers
python search.py "CRISPR base editing" --source pubmed --output published.json

# Preprints
python search.py "CRISPR base editing" --source biorxiv --output preprints.json
```

### Citation-Informed Search
Use Semantic Scholar for citation analysis, then PubMed for full metadata:

```bash
# Find highly-cited papers
python search.py "deep learning genomics" \
  --source semantic \
  --min-citations 100 \
  --format text
```

---

## Coverage Overlap Analysis

```
                    PubMed
                   ╱      ╲
                  ╱        ╲
           Biomedical    Clinical
                ╲          ╱
                 ╲        ╱
                 ┌───────┐
                 │ Overlap│ ← Life sciences papers
                 └───────┘    appear in multiple DBs
                  ╱       ╲
                 ╱         ╲
           Semantic      bioRxiv
           Scholar       (preprints)
                │
                │
           Cross-domain
```

### Unique Coverage by Database

| Database | Unique Content |
|----------|---------------|
| PubMed | MeSH-indexed biomedical, MEDLINE journals |
| bioRxiv | Biology preprints (before publication) |
| medRxiv | Medical/clinical preprints |
| Semantic Scholar | CS/AI papers, citation graphs, arXiv papers |
| Google Scholar | Theses, books, patents, grey literature |

---

## Rate Limits and Performance

| Database | Without API Key | With API Key |
|----------|-----------------|--------------|
| PubMed | 3 requests/sec | 10 requests/sec |
| bioRxiv | ~30 requests/min | N/A |
| Semantic Scholar | 100 req/5 min | 1 request/sec |
| Google Scholar | Variable (scraping) | N/A |

**Recommendations**:
1. For PubMed, get an NCBI API key (free): set `NCBI_API_KEY` env var
2. For Semantic Scholar, request an API key: set `SEMANTIC_SCHOLAR_API_KEY` env var
3. For bioRxiv, respect rate limits (~2 second delay is built-in)
4. For Google Scholar, use sparingly and consider proxies for large searches

---

## Decision Flowchart

```
Start
  │
  ▼
Is this biomedical/clinical research?
  │
  ├─ YES → Start with PubMed
  │         └─ Need preprints? → Add bioRxiv/medRxiv
  │
  └─ NO ──▶ Is this CS/AI focused?
              │
              ├─ YES → Start with Semantic Scholar
              │
              └─ NO ──▶ Is this humanities/social science?
                          │
                          ├─ YES → Start with Google Scholar
                          │
                          └─ NO ──▶ Use Semantic Scholar (broadest coverage)

For comprehensive coverage:
  Use multiple sources with deduplication:
  --source pubmed,semantic,biorxiv
```

---

## See Also

- [Query Best Practices](./query_best_practices.md) - Constructing effective queries
- [PubMed Search Syntax](../sources/pubmed/references/search_syntax.md) - MeSH and Boolean operators
- [Semantic Scholar API Guide](../sources/semantic_scholar/references/api_guide.md) - S2 API features
- [bioRxiv Search Guide](../sources/biorxiv/references/search_guide.md) - Preprint search tips
