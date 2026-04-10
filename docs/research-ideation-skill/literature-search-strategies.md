# Literature Search Strategies

Systematic literature search methods to help researchers efficiently find relevant papers.

## 1. Keyword Construction

### 1.1 Core Concept Identification

Extract core concepts from your research interest:

**Example**: Research interest "Transformer Model Interpretability"
- Core Concept 1: Transformer
- Core Concept 2: Interpretability / Explainability

### 1.2 Synonyms and Variants

List synonyms and variants for each core concept:

| Core Concept | Synonyms/Variants |
|---------|------------|
| Transformer | Attention mechanism, Self-attention, BERT, GPT |
| Interpretability | Explainability, Transparency, Understanding |

### 1.3 Boolean Operators

Combine keywords using boolean operators:

```
(Transformer OR "attention mechanism" OR BERT OR GPT)
AND
(interpretability OR explainability OR transparency)
```

### 1.4 Domain-Specific Terminology

Add domain-specific terms:

- **Method terminology**: probing, attention visualization, saliency maps
- **Application domains**: NLP, computer vision, speech recognition
- **Evaluation metrics**: faithfulness, plausibility, human evaluation

## 2. Academic Database Selection

### 2.1 Major Databases

| Database | Characteristics | Use Cases |
|--------|------|---------|
| **arXiv** | Preprints, fast updates | Get latest research advances |
| **Semantic Scholar** | AI-driven, citation analysis | Discover related papers, analyze influence |
| **Google Scholar** | Broad coverage | Comprehensive search, find missed papers |
| **ACL Anthology** | NLP-specialized | Deep search in NLP field |
| **IEEE Xplore** | Engineering and technology | Computer vision, hardware-related |

### 2.2 Search Strategies

**arXiv Search**:
```
cat:cs.LG AND (transformer OR attention) AND (interpretability OR explainability)
```

**Semantic Scholar Search**:
- Use natural language queries
- Leverage "Highly Influential Citations" filtering
- Browse "Related Papers" to discover relevant work

**Google Scholar Search**:
- Use quotation marks for exact match: "transformer interpretability"
- Limit date range: 2020-2024
- Exclude patents: -patent

## 3. Search Techniques

### 3.1 Iterative Search

1. **Initial search** - Use core keywords
2. **Analyze results** - Check keywords in highly cited papers
3. **Optimize query** - Add newly discovered terms
4. **Repeat iteration** - Until finding sufficient relevant papers

### 3.2 Citation Tracking

**Forward Citation**:
- See which new papers cite this paper
- Understand subsequent research developments

**Backward Citation**:
- See which papers this paper cites
- Understand research foundations and background

### 3.3 Author Tracking

- Identify key researchers in the field
- Check their other related work
- Follow their latest research

## 4. Paper Selection Criteria

### 4.1 Initial Screening (Based on Title and Abstract)

**Inclusion Criteria**:
- Directly relevant to research topic
- Published in top-tier conferences/journals (NeurIPS, ICML, ICLR, ACL, AAAI)
- High citation count (relative to publication date)
- Authors from renowned institutions or research groups

**Exclusion Criteria**:
- Unrelated to research topic
- Published in low-quality conferences/journals
- Clearly outdated methods (unless classic papers)

### 4.2 Deep Screening (Based on Full Text)

**Quality Assessment**:
1. **Method innovation** - Does it propose new methods or perspectives
2. **Experimental sufficiency** - Are experiments well-designed with credible results
3. **Writing quality** - Is the paper clear and easy to understand
4. **Reproducibility** - Does it provide code and data

**Relevance Assessment**:
1. **Directly relevant** - Core methods or problems directly related
2. **Indirectly relevant** - Related technologies or application scenarios
3. **Background knowledge** - Provides necessary background and foundations

### 4.3 Literature Management

**Integrated Tools**:
- **Zotero** (Primary tool, integrated via MCP)
  - Automatically add papers via `add_items_by_doi`, get complete metadata
  - Auto-create and organize collections via `create_collection`
  - Auto-attach OA PDFs via `find_and_attach_pdfs`
  - Read PDF full text for analysis via `get_item_fulltext`
  - Search existing papers via `search_library` to avoid duplicate imports
- Mendeley - Social features, PDF annotation (Alternative)
- Papers - Mac-exclusive, elegant interface (Alternative)

**Organization Strategy**:

Organize literature using Zotero collection structure:

```
📁 Research-{topic}-{date}
  ├── 📁 Core Papers
  ├── 📁 Methods
  ├── 📁 Applications
  ├── 📁 Baselines
  └── 📁 To-Read
```

- Core Papers: Directly relevant, highly cited key papers
- Methods: Technical method references, reusable methodologies
- Applications: Application scenario references, field practices
- Baselines: Experimental comparison benchmarks, work to reproduce
- To-Read: Initial screening, pending in-depth reading

## 5. DOI Extraction and Auto-Import

### 5.1 DOI Extraction Methods

Common ways to extract DOI from WebSearch results:

**DOI in URLs**:
- `https://doi.org/10.xxxx/xxxxx` - Direct DOI link
- `https://dl.acm.org/doi/10.xxxx/xxxxx` - ACM Digital Library
- `https://ieeexplore.ieee.org/document/xxxxx` - IEEE (extract from page)
- `https://arxiv.org/abs/xxxx.xxxxx` - arXiv (DOI format: `10.48550/arXiv.xxxx.xxxxx`)

**Common DOI Formats**:
- `10.xxxx/xxxxx` - Standard DOI prefix
- Starts with `10.`, contains `/` delimiter
- Example: `10.1038/s41586-023-06747-5` (Nature)
- Example: `10.48550/arXiv.2301.00234` (arXiv)

### 5.2 Auto-Import Workflow

```
WebSearch paper search
    ↓
Extract DOI from search results
    ↓
Batch add to Zotero via add_items_by_doi
    ↓
Auto-attach OA PDFs via find_and_attach_pdfs
    ↓
Read full text for analysis via get_item_fulltext
```

**Operation Example**:

1. Use WebSearch to search `"transformer interpretability" site:arxiv.org OR site:doi.org`
2. Collect DOI list from results
3. Call `add_items_by_doi` for batch import (recommend no more than 10 papers per batch to avoid API rate limits)
4. Call `find_and_attach_pdfs` to attach PDFs to imported papers
5. Use `get_item_fulltext` to read key paper full text

### 5.3 Handling Papers Without DOI

Some papers may lack standard DOI:
- **arXiv preprints**: Use `10.48550/arXiv.{id}` format
- **Conference proceedings**: Try to obtain DOI from publisher page
- **Unable to obtain DOI**: Use `add_web_item` to save web link, or use `import_pdf_to_zotero` to directly import PDF
