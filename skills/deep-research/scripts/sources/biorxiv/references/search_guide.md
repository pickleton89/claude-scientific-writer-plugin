# bioRxiv/medRxiv Search Guide

> Reference documentation for searching preprint servers

---

## Overview

bioRxiv (biology) and medRxiv (medicine) are preprint servers hosting research before peer review. The bioRxiv API provides programmatic access to preprint metadata.

**Key Characteristics:**
- Preprints (not peer-reviewed)
- Often 6-12 months ahead of journal publication
- Version tracking (papers may be updated)
- Open access by default

---

## API Endpoints

Base URL: `https://api.biorxiv.org`

### Content Details Endpoint

Retrieve papers within a date range:

```
GET /details/{server}/{start_date}/{end_date}/{cursor}
```

**Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `server` | `biorxiv` or `medrxiv` | `biorxiv` |
| `start_date` | Start date (YYYY-MM-DD) | `2024-01-01` |
| `end_date` | End date (YYYY-MM-DD) | `2024-06-30` |
| `cursor` | Pagination offset | `0`, `100`, `200` |

**Example:**
```bash
curl "https://api.biorxiv.org/details/biorxiv/2024-01-01/2024-01-31/0"
```

### DOI Lookup Endpoint

Fetch a specific preprint by DOI:

```
GET /details/{server}/{doi_suffix}
```

**Example:**
```bash
curl "https://api.biorxiv.org/details/biorxiv/2024.01.15.575123"
```

### Publisher Articles Endpoint

Find published versions of preprints:

```
GET /publisher/{prefix}/{cursor}
```

Useful for tracking which preprints have been published.

---

## Response Format

```json
{
  "collection": [
    {
      "doi": "10.1101/2024.01.15.575123",
      "title": "Example Preprint Title",
      "authors": "Smith, John; Doe, Jane; Johnson, Bob",
      "author_corresponding": "Smith, John",
      "author_corresponding_institution": "University Name",
      "date": "2024-01-15",
      "version": "1",
      "type": "new results",
      "license": "CC-BY-NC-ND 4.0",
      "category": "genetics",
      "jatsxml": "https://www.biorxiv.org/content/10.1101/2024.01.15.575123.source.xml",
      "abstract": "Abstract text here...",
      "published": "NA"
    }
  ],
  "messages": [
    {
      "status": "ok",
      "count": 100,
      "total": 1523
    }
  ]
}
```

**Field Notes:**
- `published`: "NA" if not yet published, journal name if published
- `version`: Preprint version number (papers can be revised)
- `type`: "new results", "contradictory results", "confirmatory results", or "new methods"

---

## Rate Limits

- **Recommended:** 30 requests per minute
- **Batch size:** 100 papers per request (maximum)
- **Pagination:** Use cursor to iterate through results

---

## Subject Categories

### bioRxiv Categories

| Category | Description |
|----------|-------------|
| `animal behavior and cognition` | Behavioral studies |
| `biochemistry` | Biochemical processes |
| `bioengineering` | Biological engineering |
| `bioinformatics` | Computational biology |
| `biophysics` | Physical biology |
| `cancer biology` | Cancer research |
| `cell biology` | Cellular processes |
| `developmental biology` | Development and differentiation |
| `ecology` | Ecological studies |
| `evolutionary biology` | Evolution |
| `genetics` | Genetic studies |
| `genomics` | Genome-scale studies |
| `immunology` | Immune system |
| `microbiology` | Microorganisms |
| `molecular biology` | Molecular processes |
| `neuroscience` | Neural systems |
| `pathology` | Disease mechanisms |
| `pharmacology and toxicology` | Drug effects |
| `physiology` | Organ/system function |
| `plant biology` | Plant sciences |
| `synthetic biology` | Engineered biology |
| `systems biology` | Systems-level analysis |

### medRxiv Categories

| Category | Description |
|----------|-------------|
| `cardiovascular medicine` | Heart and vascular |
| `epidemiology` | Disease distribution |
| `genetic and genomic medicine` | Clinical genetics |
| `infectious diseases` | Pathogens |
| `neurology` | Neurological disorders |
| `oncology` | Cancer medicine |
| `psychiatry and clinical psychology` | Mental health |
| `public and global health` | Population health |

---

## Search Strategies

### 1. Keyword Search in Recent Papers

The API doesn't support direct text search. Instead:

```python
from biorxiv.search import BioRxivSearcher

searcher = BioRxivSearcher(server="biorxiv")
results = searcher.search(
    query="CRISPR gene therapy",  # Filters by keyword match
    max_results=50,
    date_start="2024-01-01",
    category="genetics"
)
```

### 2. Category-Specific Search

```python
results = searcher.search(
    query="single cell RNA",
    category="genomics",
    date_start="2024-06-01"
)
```

### 3. Fetch by DOI

```python
paper = searcher.search_by_doi("10.1101/2024.01.15.575123")
```

---

## CLI Examples

### Basic Search

```bash
python search.py "CRISPR therapeutics" --server biorxiv --limit 30
```

### Date-Filtered Search

```bash
python search.py "single cell sequencing" \
  --server biorxiv \
  --date-start 2024-01-01 \
  --date-end 2024-06-30 \
  --limit 100
```

### Category-Filtered Search

```bash
python search.py "machine learning" \
  --server biorxiv \
  --category bioinformatics \
  --limit 50
```

### Medical Preprints

```bash
python search.py "COVID-19 variants" \
  --server medrxiv \
  --category "infectious diseases" \
  --limit 50
```

### Export to BibTeX

```bash
python search.py "protein folding" \
  --server biorxiv \
  --format bibtex \
  --output references.bib
```

### List Categories

```bash
python search.py "" --list-categories --server biorxiv
python search.py "" --list-categories --server medrxiv
```

---

## Best Practices

### When to Use bioRxiv/medRxiv

**Good for:**
- Finding the latest research (before publication)
- Tracking preprint-to-publication pipeline
- Accessing research during peer review
- Open access to cutting-edge findings

**Limitations:**
- Not peer-reviewed (quality varies)
- May be revised or retracted
- Some preprints never get published
- Limited historical coverage (bioRxiv: 2013+, medRxiv: 2019+)

### Quality Considerations

1. **Check version number** - v1 may have significant changes in later versions
2. **Check published status** - prefer published version if available
3. **Verify author credentials** - established labs vs. unknown authors
4. **Look for peer review** - note if currently under review

### Combining with Other Sources

For comprehensive searches:

```bash
# Search published literature (PubMed)
python ../pubmed/search.py "CRISPR therapy" --limit 50

# Search preprints (bioRxiv)
python search.py "CRISPR therapy" --server biorxiv --limit 50

# Combine and deduplicate results by DOI
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| `doi` | Digital Object Identifier |
| `title` | Preprint title |
| `authors` | Author list (semicolon-separated) |
| `abstract` | Abstract text |
| `date` | Posting date |
| `category` | Subject category |
| `server` | biorxiv or medrxiv |
| `version` | Version number |
| `published` | Journal name if published, else "NA" |
| `url` | Web URL to preprint |
| `pdf_url` | Direct PDF link |

---

## Troubleshooting

### No Results Found

1. **Expand date range** - default is last 30 days
2. **Simplify keywords** - API filters by keyword presence
3. **Check category spelling** - use `--list-categories` to verify
4. **Try broader terms** - API doesn't support complex boolean

### Rate Limiting

If you get empty responses or errors:
- Add delays between requests (2+ seconds)
- Reduce batch sizes
- Check if API is temporarily unavailable

### Version Tracking

To get all versions of a preprint:
```python
# The API returns only the latest version by default
# Use the DOI lookup to track specific versions
```

---

## Additional Resources

- **bioRxiv Homepage:** https://www.biorxiv.org
- **medRxiv Homepage:** https://www.medrxiv.org
- **API Documentation:** https://api.biorxiv.org
- **bioRxiv on Twitter/X:** @baborxiv
- **Preprint Best Practices:** https://asapbio.org/preprint-info
