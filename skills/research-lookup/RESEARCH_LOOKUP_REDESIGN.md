# Research Lookup Skill Redesign Analysis

> Analysis Date: 2026-01-04
> Status: Planning Document

## Executive Summary

The current `research-lookup` skill is tightly coupled to Perplexity AI via OpenRouter, which introduces hallucination risk, inconsistent academic coverage, and ongoing API costs. This document evaluates alternative approaches discovered during analysis, including leveraging **existing PubMed infrastructure** already built into the plugin.

**Key Finding**: The `citation-management` skill already contains a production-ready `PubMedSearcher` class that can be immediately integrated into `research-lookup`.

---

## Table of Contents

1. [Current State Assessment](#current-state-assessment)
2. [Available Data Sources](#available-data-sources)
3. [Implementation Options](#implementation-options)
4. [Detailed Comparison Matrix](#detailed-comparison-matrix)
5. [Integration with Literature-Review Skill](#integration-with-literature-review-skill)
6. [Recommended Architecture](#recommended-architecture)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Open Questions](#open-questions)

---

## Current State Assessment

### Architecture

```
research-lookup/
├── SKILL.md                          # Skill definition
├── scripts/
│   ├── research_lookup.py            # Main script (Perplexity-dependent)
│   ├── lookup.py
│   └── examples.py
└── references/
    ├── model_selection.md            # Sonar Pro vs Reasoning selection
    ├── bioinformatics_databases.md   # Database reference (not used programmatically)
    └── expert_guide.md               # Best practices
```

### Current Flow

```
User Query → Perplexity Sonar (via OpenRouter) → AI-Synthesized Response + Citations
```

### Problems with Current Approach

| Issue | Impact | Severity |
|-------|--------|----------|
| **Single source dependency** | No fallback if Perplexity fails or degrades | High |
| **Hallucination risk** | 5-10% of citations may be fabricated (per expert_guide.md) | High |
| **No structured queries** | Cannot use MeSH terms, field tags, Boolean operators | Medium |
| **API costs** | OpenRouter charges per request | Medium |
| **No local library access** | Cannot leverage user's existing Zotero collection | Medium |
| **Inconsistent coverage** | Perplexity's academic indexing varies by field | Medium |

---

## Available Data Sources

### 1. PubMed (via Existing Infrastructure) ✅

**Already implemented** in `citation-management/scripts/search_pubmed.py`

```python
class PubMedSearcher:
    """Search PubMed using NCBI E-utilities API."""

    def search(self, query, max_results=100, date_start=None, date_end=None,
               publication_types=None) -> List[str]:  # Returns PMIDs

    def fetch_metadata(self, pmids: List[str]) -> List[Dict]:
        # Returns: pmid, doi, title, authors, journal, year, volume, issue, pages, abstract

    def metadata_to_bibtex(self, metadata: Dict) -> str:
```

**Coverage**: 35M+ citations in biomedical/life sciences literature

**Query Capabilities**:
- MeSH terms: `"Anemia, Sickle Cell"[MeSH]`
- Field tags: `[Title]`, `[Author]`, `[Abstract]`, `[Publication Date]`
- Boolean operators: `AND`, `OR`, `NOT`
- Date ranges: `2020:2025[Publication Date]`
- Publication type filters: `Review`, `Clinical Trial`, `Meta-Analysis`

### 2. Perplexity Sonar (Current)

**Implementation**: `research-lookup/scripts/research_lookup.py`

**Models**:
- `perplexity/sonar-pro` - Fast lookup
- `perplexity/sonar-reasoning-pro` - Deep analysis

**Strengths**: AI synthesis, cross-domain coverage, natural language queries
**Weaknesses**: Hallucination risk, no structured queries, cost

### 3. Zotero MCP Server (Potential)

**Available implementations**:
- [54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp) - Feature-rich, semantic search
- [kujenga/zotero-mcp](https://github.com/kujenga/zotero-mcp) - Lean and stable
- [kaliaboi/mcp-zotero](https://github.com/kaliaboi/mcp-zotero) - Cloud-focused

**Capabilities**:
- Search local PDF library by content/metadata
- Retrieve annotations and highlights
- Access full-text from owned papers
- Semantic search across collection

**Requirements**: Zotero 7.1+ for `/fulltext` endpoint

### 4. Claude PubMed Connector (Limited Availability)

**Status**: Available in Claude Desktop/Web, **not directly in Claude Code**

**Potential workaround**: Build local MCP server wrapping PubMed E-utilities (essentially what `search_pubmed.py` already does)

### 5. Other Databases

| Database | Access Method | Coverage |
|----------|---------------|----------|
| Semantic Scholar | Direct API (key required) | 200M+ papers, citation graphs |
| arXiv | Direct API | Preprints: physics, CS, math, q-bio |
| bioRxiv/medRxiv | API or gget | Preprints: biology, medicine |
| CrossRef | Direct API | DOI metadata resolution |
| OpenAlex | Direct API (free) | 250M+ works, open bibliometrics |

**Note**: `gget` library does NOT support PubMed literature search—it's for genomic databases (Ensembl, UniProt, PDB, AlphaFold).

---

## Implementation Options

### Option A: PubMed Integration (Recommended First Step)

**Approach**: Import existing `PubMedSearcher` from citation-management

**Effort**: 🟢 Easy (4-8 hours)

| Pros | Cons |
|------|------|
| Code already exists and tested | Limited to biomedical literature |
| Free API (no cost) | Rate limited (3/sec without key, 10/sec with) |
| Structured queries (MeSH, Boolean) | No AI synthesis of results |
| Zero hallucination risk | User must interpret results themselves |
| Direct DOI/PMID for verification | Less convenient for quick answers |

**Implementation**:
```python
# In research_lookup.py
from pathlib import Path
import sys

citation_scripts = Path(__file__).parent.parent.parent / "citation-management" / "scripts"
sys.path.insert(0, str(citation_scripts))
from search_pubmed import PubMedSearcher
```

### Option B: Keep Perplexity + Add Verification Layer

**Approach**: Use Perplexity for synthesis, then verify citations via PubMed/CrossRef

**Effort**: 🟡 Medium (1-2 weeks)

| Pros | Cons |
|------|------|
| Best of both worlds | More complex architecture |
| AI synthesis for quick answers | Still has API costs |
| Automatic verification catches hallucinations | Slower (two API calls) |
| Graceful degradation if one fails | More moving parts to maintain |

**Flow**:
```
Query → Perplexity → Extract DOIs/PMIDs → Verify via PubMed/CrossRef → Flag unverified
```

### Option C: Zotero MCP Integration

**Approach**: Add local library search before external APIs

**Effort**: 🟡 Medium (1-2 weeks)

| Pros | Cons |
|------|------|
| Leverages curated personal library | Requires Zotero 7.1+ |
| No API costs for local searches | MCP server setup required |
| Full-text search of owned PDFs | Only searches what you have |
| Semantic search capabilities | Additional dependency |

**"Library-First" Pattern**:
```
Query → Search Zotero first → If insufficient → Query PubMed/Perplexity
```

### Option D: Multi-Source Router Architecture

**Approach**: Intelligent routing to optimal source based on query type

**Effort**: 🔴 Challenging (3-6 weeks)

| Pros | Cons |
|------|------|
| Optimal source for each query type | Significant architecture work |
| Unified result format | Complex query classification |
| Deduplication across sources | More testing required |
| Extensible for future sources | Higher maintenance burden |

**Routing Logic**:
```
Query Analysis:
├── Biomedical topic? → PubMed
├── Preprint/latest? → bioRxiv/arXiv
├── Have in Zotero? → Local library
├── Need synthesis? → Perplexity
└── Citation chain? → Semantic Scholar
```

### Option E: Build PubMed MCP Server

**Approach**: Wrap existing `search_pubmed.py` as MCP server for broader use

**Effort**: 🟡 Medium (1-2 weeks)

| Pros | Cons |
|------|------|
| Reusable across Claude tools | Requires MCP infrastructure |
| Consistent with Anthropic's direction | Duplicates existing functionality |
| Could share with community | May not add value over direct import |

---

## Detailed Comparison Matrix

| Criterion | PubMed Direct | Perplexity | Zotero MCP | Multi-Source |
|-----------|---------------|------------|------------|--------------|
| **Implementation Effort** | 🟢 Easy | ✅ Exists | 🟡 Medium | 🔴 Hard |
| **API Cost** | Free | $$ | Free | Mixed |
| **Hallucination Risk** | None | 5-10% | None | Varies |
| **Coverage** | Biomedical | Cross-domain | Personal library | Comprehensive |
| **Query Precision** | High (MeSH) | Low (NL) | Medium | High |
| **AI Synthesis** | No | Yes | No | Optional |
| **Citation Accuracy** | 100% | ~90-95% | 100% | ~95-100% |
| **Offline Capability** | No | No | Yes (local) | Partial |
| **Maintenance** | Low | Low | Medium | High |

---

## Integration with Literature-Review Skill

The `literature-review` skill has **overlapping but distinct scope**:

| Aspect | research-lookup | literature-review |
|--------|-----------------|-------------------|
| **Purpose** | Quick lookups, citation discovery | Systematic multi-database reviews |
| **Paper count** | 1-10 papers | 30-100+ papers |
| **Workflow** | Single query → results | PRISMA protocol, screening stages |
| **Output** | Citations + summary | Full review document |

### Shared Infrastructure Opportunities

1. **PubMed query code**: Both can use `search_pubmed.py`
2. **Citation verification**: Share `verify_citations.py`
3. **Database strategies**: Consolidate `database_strategies.md` (fix incorrect gget reference)
4. **Result formatting**: Unified citation output format

### Workflow Integration

```
research-lookup (discovery)
    │
    ├── Quick facts/stats → Return immediately
    │
    └── Comprehensive search needed?
            │
            └── Trigger literature-review skill
```

---

## Recommended Architecture

### Phase 1: Immediate (This Week)

```
research-lookup/
├── SKILL.md                          # Update to support --source flag
├── scripts/
│   ├── research_lookup.py            # Add PubMed source option
│   ├── sources/
│   │   ├── __init__.py
│   │   └── pubmed.py                 # Import from citation-management
│   └── ...
└── references/
    └── pubmed_strategies.md          # NEW: PubMed query best practices
```

**Skill interface**:
```bash
# Current (Perplexity)
python research_lookup.py "CRISPR sickle cell"

# New options
python research_lookup.py "CRISPR sickle cell" --source pubmed
python research_lookup.py "CRISPR sickle cell" --source perplexity  # default
python research_lookup.py "CRISPR sickle cell" --source both        # triangulate
```

### Phase 2: Near-term (2-4 Weeks)

1. Add Zotero MCP integration for "library-first" searches
2. Implement citation verification pipeline
3. Add `--verify` flag to check Perplexity citations against PubMed

### Phase 3: Future (Optional)

1. Multi-source router with intelligent query classification
2. Semantic Scholar integration for citation chain analysis
3. Query-to-MeSH translator using Claude

---

## Implementation Roadmap

### Week 1: PubMed Integration

- [ ] Import `PubMedSearcher` into research-lookup
- [ ] Add `--source pubmed` CLI flag
- [ ] Create `references/pubmed_strategies.md`
- [ ] Update SKILL.md documentation
- [ ] Fix `database_strategies.md` gget error in literature-review

### Week 2-3: Zotero Integration

- [ ] Install and configure [54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp)
- [ ] Add `sources/zotero.py` wrapper
- [ ] Implement "library-first" search pattern
- [ ] Test full-text PDF search

### Week 4: Verification Pipeline

- [ ] Add `--verify` flag for Perplexity results
- [ ] Cross-check DOIs against CrossRef
- [ ] Cross-check PMIDs against PubMed
- [ ] Flag unverifiable citations in output

### Future: Multi-Source Router

- [ ] Query classification logic
- [ ] Result deduplication
- [ ] Unified output format
- [ ] Performance benchmarking

---

## Open Questions

1. **Default source**: Should the default remain Perplexity (AI synthesis) or switch to PubMed (accuracy)?

2. **Zotero requirement**: Should Zotero integration be optional or required for full functionality?

3. **Cost allocation**: For multi-source queries, how to balance API costs vs. result quality?

4. **Claude PubMed connector**: Worth investigating if/when available in Claude Code?

5. **Skill consolidation**: Should research-lookup and citation-management share more infrastructure formally (e.g., monorepo-style imports)?

---

## References

- [54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp) - Zotero MCP Server
- [kujenga/zotero-mcp](https://github.com/kujenga/zotero-mcp) - Alternative Zotero MCP
- [zotero-mcp on PyPI](https://pypi.org/project/zotero-mcp/)
- [MCP Connector - Claude Docs](https://docs.claude.com/en/docs/agents-and-tools/mcp-connector)
- [gget documentation](https://pachterlab.github.io/gget/) - Genomic databases (NOT literature search)
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) - PubMed API documentation

---

## Appendix: Existing Code Locations

| Component | Location |
|-----------|----------|
| PubMed search | `skills/citation-management/scripts/search_pubmed.py` |
| Metadata extraction | `skills/citation-management/scripts/extract_metadata.py` |
| PubMed guide | `skills/citation-management/references/pubmed_search.md` |
| Literature search strategies | `skills/hypothesis-generation/references/literature_search_strategies.md` |
| Database strategies | `skills/literature-review/references/database_strategies.md` |
| Current research-lookup | `skills/research-lookup/scripts/research_lookup.py` |
