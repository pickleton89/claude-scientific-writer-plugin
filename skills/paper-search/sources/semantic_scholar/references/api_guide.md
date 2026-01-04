# Semantic Scholar API Guide

> Reference documentation for the Semantic Scholar Academic Graph API

---

## Overview

Semantic Scholar provides access to over 200 million academic papers across all fields of research. The API offers paper search, citation graph traversal, and author information.

**Key Features:**
- Full-text search across 200M+ papers
- Citation graph (papers citing/cited by)
- Author profiles and publication lists
- Field of study classification
- Influential citation metrics
- Open access PDF links

---

## Authentication

### Without API Key

- **Rate limit:** 100 requests per 5 minutes
- **Suitable for:** Light usage, testing

### With API Key (Recommended)

- **Rate limit:** 1 request per second (sustained)
- **Get a key:** https://www.semanticscholar.org/product/api#api-key

**Setting up your key:**

```bash
# Environment variable
export SEMANTIC_SCHOLAR_API_KEY="your-api-key-here"

# Or pass directly
python search.py search "query" --api-key "your-key"
```

---

## API Endpoints

Base URL: `https://api.semanticscholar.org/graph/v1`

### Paper Search

```
GET /paper/search
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query (required) |
| `limit` | int | Results per page (max 100) |
| `offset` | int | Pagination offset |
| `fields` | string | Comma-separated field list |
| `year` | string | Year filter (e.g., "2020-2024") |
| `fieldsOfStudy` | string | Field filter (comma-separated) |
| `openAccessPdf` | (empty) | Only return open access papers |

**Example:**
```bash
curl "https://api.semanticscholar.org/graph/v1/paper/search?query=machine+learning&limit=10&fields=title,year,authors"
```

### Get Paper by ID

```
GET /paper/{paper_id}
```

**Paper ID formats:**
- Semantic Scholar ID: `649def34f8be52c8b66281af98ae884c09aef38b`
- DOI: `DOI:10.1038/nature12373`
- arXiv: `ARXIV:2106.15928`
- PubMed: `PMID:19229259`
- Corpus ID: `CorpusId:215416146`

**Example:**
```bash
curl "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1038/nature12373?fields=title,abstract,authors,year"
```

### Paper Citations

```
GET /paper/{paper_id}/citations
```

Returns papers that cite the given paper.

### Paper References

```
GET /paper/{paper_id}/references
```

Returns papers referenced by the given paper.

### Author Search

```
GET /author/search
```

Search for authors by name.

### Get Author

```
GET /author/{author_id}
```

Get author profile including affiliation, h-index, and paper count.

### Author Papers

```
GET /author/{author_id}/papers
```

Get all papers by an author.

---

## Available Fields

### Paper Fields

| Field | Description |
|-------|-------------|
| `paperId` | Semantic Scholar paper ID |
| `title` | Paper title |
| `abstract` | Abstract text |
| `year` | Publication year |
| `venue` | Publication venue |
| `publicationVenue` | Venue details object |
| `citationCount` | Total citations |
| `influentialCitationCount` | Citations in influential papers |
| `authors` | Author list |
| `externalIds` | DOI, PMID, arXiv ID, etc. |
| `url` | Semantic Scholar URL |
| `openAccessPdf` | Open access PDF info |
| `fieldsOfStudy` | Research areas |
| `publicationDate` | Publication date (YYYY-MM-DD) |
| `references` | Referenced papers |
| `citations` | Citing papers |
| `embedding` | Paper embedding vector |

### Author Fields

| Field | Description |
|-------|-------------|
| `authorId` | Author ID |
| `name` | Full name |
| `affiliations` | Institutional affiliations |
| `paperCount` | Number of papers |
| `citationCount` | Total citations |
| `hIndex` | H-index |

---

## Fields of Study

Valid values for the `fieldsOfStudy` filter:

| Field | Description |
|-------|-------------|
| `Computer Science` | CS and related |
| `Medicine` | Medical sciences |
| `Biology` | Life sciences |
| `Chemistry` | Chemical sciences |
| `Physics` | Physical sciences |
| `Mathematics` | Mathematical sciences |
| `Engineering` | Engineering disciplines |
| `Materials Science` | Materials research |
| `Environmental Science` | Environmental studies |
| `Psychology` | Psychological sciences |
| `Economics` | Economic sciences |
| `Sociology` | Social sciences |
| `Political Science` | Political studies |
| `History` | Historical studies |
| `Philosophy` | Philosophical studies |
| `Art` | Arts and humanities |
| `Business` | Business studies |
| `Geography` | Geographic sciences |
| `Linguistics` | Language sciences |
| `Law` | Legal studies |

---

## CLI Commands

### Basic Search

```bash
# Search with keyword
python search.py search "attention mechanism transformers" --limit 30

# Filter by year
python search.py search "CRISPR gene editing" --year-start 2020 --year-end 2024

# Filter by field
python search.py search "neural networks" --fields "Computer Science,Mathematics"

# Open access only
python search.py search "protein structure" --open-access

# Highly cited papers only
python search.py search "deep learning" --min-citations 100
```

### Get Paper Details

```bash
# By Semantic Scholar ID
python search.py paper 649def34f8be52c8b66281af98ae884c09aef38b

# By DOI
python search.py paper "DOI:10.1038/nature12373"

# By arXiv ID
python search.py paper "ARXIV:2106.15928"
```

### Citation Graph

```bash
# Get papers citing a paper
python search.py citations "DOI:10.1038/nature12373" --limit 50

# Get papers referenced by a paper
python search.py references "DOI:10.1038/nature12373" --limit 50
```

### Author Information

```bash
# Get author profile
python search.py author 1234567

# Get author's papers
python search.py author 1234567 --papers --limit 100
```

### Export to BibTeX

```bash
python search.py search "machine learning healthcare" \
  --format bibtex \
  --output references.bib
```

---

## Python API

### Basic Search

```python
from semantic_scholar.search import SemanticScholarSearcher

searcher = SemanticScholarSearcher(api_key="your-key")

results = searcher.search(
    query="transformer attention mechanism",
    max_results=50,
    year_start=2020,
    fields_of_study=["Computer Science"],
    min_citations=10
)

for paper in results:
    print(f"{paper['title']} ({paper['year']}) - {paper['citation_count']} citations")
```

### Citation Graph Traversal

```python
# Get citing papers
citing = searcher.get_citations("DOI:10.1038/nature12373", max_results=50)

# Get referenced papers
refs = searcher.get_references("DOI:10.1038/nature12373", max_results=50)
```

### Author Lookup

```python
# Get author info
author = searcher.get_author("1234567")
print(f"{author['name']} - h-index: {author['hIndex']}")

# Get author's papers
papers = searcher.get_author_papers("1234567", max_results=100)
```

---

## Response Format

### Search Response

```json
{
  "total": 1523,
  "offset": 0,
  "data": [
    {
      "paperId": "649def34f8be52c8b66281af98ae884c09aef38b",
      "title": "Paper Title",
      "abstract": "Abstract text...",
      "year": 2023,
      "citationCount": 150,
      "influentialCitationCount": 25,
      "authors": [
        {"authorId": "1234", "name": "John Smith"},
        {"authorId": "5678", "name": "Jane Doe"}
      ],
      "venue": "Nature",
      "externalIds": {
        "DOI": "10.1038/nature12373",
        "PubMed": "19229259"
      },
      "openAccessPdf": {
        "url": "https://...",
        "status": "GREEN"
      },
      "fieldsOfStudy": ["Biology", "Medicine"]
    }
  ]
}
```

### Standardized Output

The search module returns standardized metadata:

| Field | Description |
|-------|-------------|
| `paper_id` | Semantic Scholar ID |
| `doi` | DOI |
| `pmid` | PubMed ID |
| `arxiv_id` | arXiv ID |
| `title` | Paper title |
| `authors` | Formatted author string |
| `abstract` | Abstract text |
| `year` | Publication year |
| `venue` | Journal/conference name |
| `citation_count` | Total citations |
| `influential_citations` | Influential citations |
| `fields_of_study` | Research areas list |
| `url` | Semantic Scholar URL |
| `pdf_url` | Open access PDF URL |

---

## Rate Limits

| Tier | Limit | Notes |
|------|-------|-------|
| **No Key** | 100 req / 5 min | For testing |
| **API Key** | 1 req / sec | Standard access |
| **Partner** | Higher limits | Contact S2 team |

**Rate limit headers:**
- `X-RateLimit-Limit`: Max requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

---

## Best Practices

### Efficient Searching

1. **Use specific queries** - narrow searches return better results
2. **Apply filters** - year, field, open access reduce noise
3. **Request only needed fields** - reduces response size

### Citation Analysis

1. **Influential citations** - weight by quality, not just count
2. **Citation velocity** - citations per year since publication
3. **Co-citation** - papers frequently cited together

### Handling Errors

```python
try:
    results = searcher.search("query")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # Rate limited - wait and retry
        time.sleep(60)
    elif e.response.status_code == 404:
        # Paper not found
        pass
```

---

## Common Use Cases

### Literature Review

```python
# Find seminal papers in a field
results = searcher.search(
    "deep learning",
    min_citations=1000,
    year_end=2018
)
```

### Track Research Evolution

```python
# Get paper and its citation network
paper = searcher.get_paper("DOI:10.1038/nature12373")
citing = searcher.get_citations(paper["paper_id"], max_results=100)
refs = searcher.get_references(paper["paper_id"], max_results=100)
```

### Find Related Work

```python
# Combine search with field filtering
results = searcher.search(
    "protein structure prediction",
    fields_of_study=["Biology", "Computer Science"],
    year_start=2020,
    open_access_only=True
)
```

### Author Analysis

```python
# Find prolific authors in a field
# (Search papers, extract unique authors, sort by citation count)
```

---

## Limitations

1. **No full-text search** - searches titles, abstracts, not full paper content
2. **Coverage varies by field** - CS/Medicine best covered
3. **Update lag** - new papers may take days to appear
4. **Rate limits** - need API key for serious usage
5. **No bulk download** - must paginate through results

---

## Additional Resources

- **API Documentation:** https://api.semanticscholar.org/api-docs/
- **API Key Request:** https://www.semanticscholar.org/product/api#api-key
- **Semantic Scholar:** https://www.semanticscholar.org
- **Data Releases:** https://api.semanticscholar.org/corpus/
- **Support:** partnerships@semanticscholar.org
