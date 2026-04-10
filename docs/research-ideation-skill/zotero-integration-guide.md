# Zotero MCP Integration Guide

Implement automated literature management integration through the Zotero MCP server.

## 1. Available Tools

### 1.1 Browse Tools

| Tool | Function | Use Case |
|------|----------|----------|
| `get_collections` | List all collections | View existing research projects |
| `get_collection_items` | Get items in a collection | Browse papers in a specific collection |
| `search_library` | Search items in library | Find existing papers by keywords |
| `get_items_details` | Batch retrieve item metadata | Get detailed paper information |
| `get_item_fulltext` | Get PDF full text | Read paper content |

### 1.2 Add Tools

| Tool | Function | Use Case |
|------|----------|----------|
| `add_items_by_doi` | Add papers by DOI | Automatically retrieve metadata and OA PDF |
| `add_web_item` | Save webpage as item | Save non-paper resources |
| `create_collection` | Create collection | Organize research projects |
| `import_pdf_to_zotero` | Import PDF | Upload local or online PDF |
| `find_and_attach_pdfs` | Batch attach OA PDFs | Find PDFs for existing items |
| `add_linked_url_attachment` | Attach URL links | Link online resources |

### 1.3 Citation Tools

| Tool | Function | Use Case |
|------|----------|----------|
| `inject_citations` | Inject citations into Word | Generate citation formats |

## 2. Collection Organization Strategy

### 2.1 Naming Convention

```
Research-{topic-keywords}-{YYYY}
```

Examples:
- `Research-TransformerInterpretability-2026`
- `Research-BrainDecoding-2026`
- `Research-RLHF-2026`

### 2.2 Standard Subcollection Structure

```
📁 Research-{topic}-{date}
  ├── 📁 Core Papers
  ├── 📁 Methods
  ├── 📁 Applications
  ├── 📁 Baselines
  └── 📁 To-Read
```

Subcollection purposes:

| Subcollection | Inclusion Criteria | Typical Count |
|---------------|-------------------|---------------|
| Core Papers | Directly related, highly cited key papers | 5-15 papers |
| Methods | Technical method references, methodologies to learn from | 10-20 papers |
| Applications | Application scenario references, domain practices | 5-10 papers |
| Baselines | Experimental benchmarks, work to reproduce | 3-8 papers |
| To-Read | Initial screening, awaiting in-depth reading | Unlimited |

## 3. Automated Workflows

### 3.1 Paper Discovery and Import

```
WebSearch for papers
    ↓
Extract DOI from search results
    ↓
Batch add to Zotero with add_items_by_doi
    ↓
Auto-attach OA PDFs with find_and_attach_pdfs
    ↓
Read full text with get_item_fulltext for analysis
```

### 3.2 DOI Extraction Tips

**Identifying DOI from search result URLs**:
- `https://doi.org/10.xxxx/xxxxx` — Direct DOI link
- `https://dl.acm.org/doi/10.xxxx/xxxxx` — ACM Digital Library
- `https://arxiv.org/abs/xxxx.xxxxx` — arXiv (DOI: `10.48550/arXiv.xxxx.xxxxx`)

**Common DOI formats**:
- Start with `10.`, contain `/` separator
- Example: `10.1038/s41586-023-06747-5` (Nature)
- Example: `10.48550/arXiv.2301.00234` (arXiv)
- Example: `10.1145/3580305.3599256` (ACM/KDD)

**CrossRef query**:
- When no obvious DOI in URL, search paper title on CrossRef to retrieve DOI

### 3.3 Full Text Reading and Notes

```
Retrieve full text with get_item_fulltext
    ↓
Analyze paper content
    ↓
Extract key information
    ↓
Generate structured notes
```

### 3.4 Note Template

Structured notes for each paper should include:

```markdown
## [Paper Title]

**Basic Information**:
- Authors:
- Conference/Journal:
- Year:
- DOI:

**Research Question**:
- What problem does it address?
- Why is it important?

**Core Method**:
- Main technical approach
- Key innovations

**Key Findings**:
- Main experimental results
- Important conclusions

**Limitations**:
- Method limitations
- Experimental limitations

**Relevance to This Research**:
- Lessons to learn
- Differences and improvement opportunities
```

## 4. Frequently Asked Questions

### 4.1 API Rate Limiting

Zotero API has rate limits; for batch additions, it's recommended to:
- Add no more than 10 papers per batch
- Leave appropriate intervals between batches
- If encountering 429 error, retry after waiting

### 4.2 PDF Full Text Indexing Delay

Newly uploaded PDFs require time to index:
- When `get_item_fulltext` returns empty, retry later
- Zotero client needs to run to complete indexing
- Large PDFs take longer to index

### 4.3 DOI Not Recognized

Some papers may not have standard DOI:
- arXiv preprints: Use `10.48550/arXiv.{id}` format
- Workshop papers: Try to obtain DOI from publisher page
- If unable to get DOI: Use `add_web_item` to save webpage link

### 4.4 OA PDF Not Available

Non-open-access papers cannot be retrieved via Unpaywall:
- Check author's homepage for preprint version
- Check arXiv for corresponding version
- For manual upload, use `import_pdf_to_zotero`
