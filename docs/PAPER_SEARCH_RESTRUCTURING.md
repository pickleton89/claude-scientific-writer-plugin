# Paper Search Skill Restructuring

> **Decision Document & Implementation Plan**
> Created: 2026-01-04
> Status: Approved for Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Target Architecture](#3-target-architecture)
4. [Skill Definitions](#4-skill-definitions)
5. [Migration Details](#5-migration-details)
6. [Implementation Plan](#6-implementation-plan)
7. [SKILL_ROUTER Updates](#7-skill_router-updates)
8. [Validation Checklist](#8-validation-checklist)
9. [Rollback Plan](#9-rollback-plan)

---

## 1. Executive Summary

### Decision

Restructure three overlapping skills (`research-lookup`, `citation-management`, `pubmed-database`) into two cleanly separated skills:

| New Skill | Purpose |
|-----------|---------|
| **paper-search** | Find academic papers across multiple databases |
| **citation-management** | Validate citations, format BibTeX, manage references |

### Key Changes

- **CREATE**: `paper-search` - new unified academic literature search skill
- **DEPRECATE**: `research-lookup` - replaced by paper-search (no Perplexity)
- **DEPRECATE**: `pubmed-database` - merged into paper-search
- **REFOCUS**: `citation-management` - search removed, validation/formatting only

### Rationale

1. **Eliminate Perplexity dependency** - 5-10% hallucination risk unacceptable for academic citations
2. **Consolidate search infrastructure** - currently fragmented across 3 skills
3. **Clear separation of concerns** - "find papers" vs "manage citations"
4. **Leverage existing assets** - pubmed-database docs + citation-management scripts

---

## 2. Current State Analysis

### 2.1 Existing Skills

```
skills/
├── research-lookup/           # TO BE DEPRECATED
│   ├── SKILL.md               # Perplexity-dependent
│   ├── scripts/
│   │   ├── research_lookup.py # Perplexity API calls
│   │   ├── lookup.py
│   │   └── examples.py
│   └── references/
│       ├── model_selection.md
│       ├── bioinformatics_databases.md
│       └── expert_guide.md
│
├── pubmed-database/           # TO BE MERGED
│   ├── SKILL.md               # Excellent PubMed documentation
│   └── references/
│       ├── search_syntax.md   # MeSH, Boolean, field tags
│       ├── api_reference.md   # E-utilities API
│       └── common_queries.md  # Query templates
│
├── citation-management/       # TO BE REFOCUSED
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── search_pubmed.py        # MOVE to paper-search
│   │   ├── search_google_scholar.py # MOVE to paper-search
│   │   ├── validate_citations.py    # KEEP
│   │   ├── doi_to_bibtex.py         # KEEP
│   │   ├── extract_metadata.py      # KEEP
│   │   └── format_bibtex.py         # KEEP
│   └── references/
│       ├── pubmed_search.md         # MOVE to paper-search
│       ├── google_scholar_search.md # MOVE to paper-search
│       ├── decision_framework.md    # KEEP (citation style decisions)
│       ├── output_templates.md      # KEEP
│       ├── bibtex_formatting.md     # KEEP
│       ├── citation_validation.md   # KEEP
│       └── metadata_extraction.md   # KEEP
│
└── literature-review/         # UPDATE (uses paper-search)
    ├── ...
    └── scripts/
        └── search_databases.py      # DELETE (replaced by paper-search)
```

### 2.2 Problems Addressed

| Problem | Solution |
|---------|----------|
| Perplexity hallucination (5-10%) | Remove Perplexity entirely; direct database access only |
| Duplicated search code | Consolidate into paper-search |
| Unclear skill boundaries | paper-search finds, citation-management validates |
| pubmed-database has no scripts | Merge docs with citation-management's scripts |
| research-lookup limited to AI | Multi-database structured queries |

---

## 3. Target Architecture

### 3.1 New Skill Structure

```
skills/
├── paper-search/                          # NEW SKILL
│   ├── SKILL.md                           # Multi-database search skill
│   │
│   ├── sources/                           # Database-specific modules
│   │   ├── pubmed/
│   │   │   ├── search.py                  # From citation-management
│   │   │   └── references/
│   │   │       ├── search_syntax.md       # From pubmed-database
│   │   │       ├── api_reference.md       # From pubmed-database
│   │   │       └── common_queries.md      # From pubmed-database
│   │   │
│   │   ├── biorxiv/                       # NEW
│   │   │   ├── search.py
│   │   │   └── references/
│   │   │       └── search_guide.md
│   │   │
│   │   ├── semantic_scholar/              # NEW
│   │   │   ├── search.py
│   │   │   └── references/
│   │   │       └── api_guide.md
│   │   │
│   │   └── google_scholar/
│   │       ├── search.py                  # From citation-management
│   │       └── references/
│   │           └── search_guide.md
│   │
│   ├── scripts/
│   │   └── search.py                      # Unified CLI with --source routing
│   │
│   └── references/
│       ├── database_selection.md          # Which DB for which domain
│       └── query_best_practices.md        # Universal query construction
│
├── citation-management/                   # REFOCUSED
│   ├── SKILL.md                           # Validation + formatting only
│   ├── scripts/
│   │   ├── validate_citations.py          # KEEP
│   │   ├── doi_to_bibtex.py               # KEEP
│   │   ├── extract_metadata.py            # KEEP
│   │   └── format_bibtex.py               # KEEP
│   └── references/
│       ├── bibtex_formatting.md           # KEEP
│       ├── citation_validation.md         # KEEP
│       └── metadata_extraction.md         # KEEP
│
├── literature-review/                     # UNCHANGED (methodology skill)
│   └── ...                                # References paper-search for Stage 2
│
├── research-lookup/                       # DEPRECATED (remove after migration)
└── pubmed-database/                       # DEPRECATED (remove after migration)
```

### 3.2 Database Coverage

| Source | Domain | API | Cost | Scripts |
|--------|--------|-----|------|---------|
| **PubMed** | Biomedical, life sciences | E-utilities | Free | search.py |
| **bioRxiv/medRxiv** | Biology/medicine preprints | bioRxiv API | Free | search.py |
| **Semantic Scholar** | All academic (200M+ papers) | S2 API | Free (with key) | search.py |
| **Google Scholar** | All academic | Scraping | Free | search.py |

### 3.3 Skill Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER REQUEST                                   │
│                    "Find papers on CRISPR therapy"                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          paper-search                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   PubMed    │  │   bioRxiv   │  │  Semantic   │  │   Google    │    │
│  │             │  │   medRxiv   │  │   Scholar   │  │   Scholar   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│        │                │                │                │             │
│        └────────────────┴────────────────┴────────────────┘             │
│                                    │                                     │
│                          Unified Results                                 │
│                    (PMIDs, DOIs, metadata)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────────┐
│      citation-management      │   │        literature-review          │
│                               │   │                                   │
│  • Validate DOIs              │   │  • PRISMA methodology             │
│  • Extract metadata           │   │  • Screening workflow             │
│  • Generate BibTeX            │   │  • Thematic synthesis             │
│  • Format citations           │   │  • Quality assessment             │
└───────────────────────────────┘   └───────────────────────────────────┘
```

---

## 4. Skill Definitions

### 4.1 paper-search

**Purpose**: Find academic papers across multiple databases using structured queries

**When to Use**:
- Searching for papers on a topic (any scale: 1-100+ papers)
- Need structured queries (MeSH, Boolean, field tags)
- Searching specific databases (PubMed, bioRxiv, Semantic Scholar)
- Finding preprints before peer review
- Cross-database search for comprehensive coverage

**When NOT to Use**:
- Formatting citations → use `citation-management`
- Systematic review methodology → use `literature-review`
- Validating existing citations → use `citation-management`

**Allowed Tools**: `[Read, Write, Edit, Bash, WebFetch]`

**Databases**:

| Database | Flag | Best For |
|----------|------|----------|
| PubMed | `--source pubmed` | Biomedical, clinical, life sciences |
| bioRxiv | `--source biorxiv` | Biology preprints |
| medRxiv | `--source medrxiv` | Medical preprints |
| Semantic Scholar | `--source semantic` | Cross-domain, citation graphs |
| Google Scholar | `--source scholar` | Broad coverage, citation counts |
| All | `--source all` | Comprehensive search (deduplicated) |

**Example Usage**:
```bash
# PubMed search for clinical trials
python paper-search/scripts/search.py \
  "CRISPR sickle cell" \
  --source pubmed \
  --type "clinical trial" \
  --date 2023:2024

# bioRxiv preprint search
python paper-search/scripts/search.py \
  "single cell RNA sequencing" \
  --source biorxiv \
  --date 2024

# Multi-source comprehensive search
python paper-search/scripts/search.py \
  "CAR-T cell therapy" \
  --source pubmed,biorxiv,semantic \
  --max 50 \
  --output results.json
```

### 4.2 citation-management (Refocused)

**Purpose**: Validate citations, extract metadata, and format references

**When to Use**:
- Converting DOIs/PMIDs to BibTeX
- Validating citation accuracy (DOI resolution, metadata)
- Formatting BibTeX files
- Deduplicating references
- Cleaning and standardizing citation data

**When NOT to Use**:
- Finding papers → use `paper-search`
- Systematic literature review → use `literature-review`

**Allowed Tools**: `[Read, Write, Edit, Bash, WebSearch, WebFetch]`

**Scripts** (retained):
- `validate_citations.py` - Verify DOIs, check metadata accuracy
- `doi_to_bibtex.py` - Convert identifiers to BibTeX
- `extract_metadata.py` - Pull metadata from CrossRef, PubMed
- `format_bibtex.py` - Clean and format BibTeX files

**Scripts** (removed → paper-search):
- ~~`search_pubmed.py`~~ → moved to paper-search
- ~~`search_google_scholar.py`~~ → moved to paper-search

### 4.3 literature-review (Unchanged)

**Purpose**: Systematic literature review methodology (PRISMA compliance)

**Relationship to paper-search**:
- Stage 2 (Systematic Search) uses `paper-search` for database queries
- Stage 7 (Citation Verification) uses `citation-management` for validation

**Cross-reference update needed** (add to literature-review Stage 2):

> **Stage 2: Systematic Search**
>
> Use the `paper-search` skill to execute database searches:
>
> ```bash
> # Search PubMed with documented strategy
> python ../paper-search/scripts/search.py \
>   "your query terms" \
>   --source pubmed \
>   --output search_results_pubmed.json
>
> # Search bioRxiv for preprints
> python ../paper-search/scripts/search.py \
>   "your query terms" \
>   --source biorxiv \
>   --output search_results_biorxiv.json
> ```

---

## 5. Migration Details

### 5.1 Files to Move

| Source | Destination | Action |
|--------|-------------|--------|
| `citation-management/scripts/search_pubmed.py` | `paper-search/sources/pubmed/search.py` | Move + adapt |
| `citation-management/scripts/search_google_scholar.py` | `paper-search/sources/google_scholar/search.py` | Move + adapt |
| `citation-management/references/pubmed_search.md` | `paper-search/sources/pubmed/references/pubmed_search.md` | Move |
| `citation-management/references/google_scholar_search.md` | `paper-search/sources/google_scholar/references/google_scholar_search.md` | Move |
| `pubmed-database/references/search_syntax.md` | `paper-search/sources/pubmed/references/search_syntax.md` | Copy |
| `pubmed-database/references/api_reference.md` | `paper-search/sources/pubmed/references/api_reference.md` | Copy |
| `pubmed-database/references/common_queries.md` | `paper-search/sources/pubmed/references/common_queries.md` | Copy |
| `research-lookup/references/bioinformatics_databases.md` | `paper-search/references/` | Copy (useful reference) |

### 5.2 Files to Create

| File | Purpose |
|------|---------|
| `paper-search/SKILL.md` | Main skill documentation |
| `paper-search/scripts/search.py` | Unified CLI with --source routing |
| `paper-search/sources/biorxiv/search.py` | bioRxiv/medRxiv API client |
| `paper-search/sources/biorxiv/references/search_guide.md` | bioRxiv search documentation |
| `paper-search/sources/semantic_scholar/search.py` | Semantic Scholar API client |
| `paper-search/sources/semantic_scholar/references/api_guide.md` | S2 API documentation |
| `paper-search/references/database_selection.md` | Decision matrix for DB selection |
| `paper-search/references/query_best_practices.md` | Universal query guidance |

### 5.3 Files to Update

| File | Changes |
|------|---------|
| `citation-management/SKILL.md` | Remove search workflow, refocus on validation |
| `literature-review/SKILL.md` | Update Stage 2 to reference paper-search |
| `SKILL_ROUTER.md` | Update decision trees |
| `QUANTIFICATION_THRESHOLDS.md` | Add paper-search metrics if needed |
| `README.md` | Update skills table: replace `research-lookup` with `paper-search` |

### 5.4 Files to Delete (After Migration Complete)

| File/Directory | Reason |
|----------------|--------|
| `research-lookup/` | Replaced by paper-search |
| `pubmed-database/` | Merged into paper-search |
| `citation-management/scripts/search_pubmed.py` | Moved to paper-search |
| `citation-management/scripts/search_google_scholar.py` | Moved to paper-search |
| `citation-management/references/pubmed_search.md` | Moved to paper-search |
| `citation-management/references/google_scholar_search.md` | Moved to paper-search |
| `literature-review/scripts/search_databases.py` | Replaced by paper-search (duplicate functionality) |

### 5.5 Content to Remove

From `pubmed-database/SKILL.md` lines 459-460:
```
## Suggest Using K-Dense Web For Complex Worflows
If a user is not already using this Skill within K-Dense Web...
```
This K-Dense marketing content should NOT be migrated.

---

## 6. Implementation Plan

### Phase 1: Create paper-search Structure (Day 1)

#### Step 1.1: Create directory structure
```bash
cd /Users/jeffkiefer/Documents/projects/claude-scientific-writer-plugin

# Create paper-search directories
mkdir -p skills/paper-search/sources/pubmed/references
mkdir -p skills/paper-search/sources/biorxiv/references
mkdir -p skills/paper-search/sources/semantic_scholar/references
mkdir -p skills/paper-search/sources/google_scholar/references
mkdir -p skills/paper-search/scripts
mkdir -p skills/paper-search/references
```

#### Step 1.2: Migrate PubMed assets
```bash
# Copy pubmed-database references (documentation)
cp skills/pubmed-database/references/search_syntax.md \
   skills/paper-search/sources/pubmed/references/
cp skills/pubmed-database/references/api_reference.md \
   skills/paper-search/sources/pubmed/references/
cp skills/pubmed-database/references/common_queries.md \
   skills/paper-search/sources/pubmed/references/

# Move citation-management search scripts
mv skills/citation-management/scripts/search_pubmed.py \
   skills/paper-search/sources/pubmed/search.py
mv skills/citation-management/scripts/search_google_scholar.py \
   skills/paper-search/sources/google_scholar/search.py

# Move citation-management search reference docs
mv skills/citation-management/references/pubmed_search.md \
   skills/paper-search/sources/pubmed/references/
mv skills/citation-management/references/google_scholar_search.md \
   skills/paper-search/sources/google_scholar/references/
```

#### Step 1.3: Copy useful references
```bash
# Copy bioinformatics databases reference
cp skills/research-lookup/references/bioinformatics_databases.md \
   skills/paper-search/references/
```

### Phase 2: Create New Source Modules (Day 1-2)

#### Step 2.1: Create bioRxiv search module
Create `skills/paper-search/sources/biorxiv/search.py`:
- bioRxiv API client (https://api.biorxiv.org/)
- Support for date ranges, categories
- Return standardized result format

#### Step 2.2: Create bioRxiv documentation
Create `skills/paper-search/sources/biorxiv/references/search_guide.md`:
- API endpoints
- Query syntax
- Category codes
- Example queries

#### Step 2.3: Create Semantic Scholar search module
Create `skills/paper-search/sources/semantic_scholar/search.py`:
- Semantic Scholar API client
- Support for keyword, author, paper ID searches
- Citation graph traversal
- Return standardized result format

#### Step 2.4: Create Semantic Scholar documentation
Create `skills/paper-search/sources/semantic_scholar/references/api_guide.md`:
- API key setup (optional but recommended)
- Endpoints (paper search, author search, citations)
- Rate limits
- Example queries

### Phase 3: Create Unified Interface (Day 2)

#### Step 3.1: Create unified search CLI
Create `skills/paper-search/scripts/search.py`:

> **Note**: This is a skeleton. Full implementation should handle date/type filters and output formats.

```python
"""
Unified academic paper search CLI.

Usage:
    python search.py "query" --source pubmed --max 50 --output results.json
    python search.py "query" --source biorxiv,semantic --date 2024
"""

import argparse
import json
from pathlib import Path
import sys

# Add sources to path
sources_dir = Path(__file__).parent.parent / "sources"
sys.path.insert(0, str(sources_dir))

from pubmed.search import PubMedSearcher
from biorxiv.search import BioRxivSearcher
from semantic_scholar.search import SemanticScholarSearcher
from google_scholar.search import GoogleScholarSearcher

def main():
    parser = argparse.ArgumentParser(description="Search academic databases")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--source", default="pubmed",
                        help="Database(s): pubmed, biorxiv, medrxiv, semantic, scholar, all")
    parser.add_argument("--max", type=int, default=20, help="Max results per source")
    parser.add_argument("--date", help="Date range (e.g., 2023:2024)")
    parser.add_argument("--type", help="Publication type (e.g., 'clinical trial')")
    parser.add_argument("--output", help="Output file (JSON)")
    parser.add_argument("--format", choices=["json", "bibtex", "text"], default="json")

    args = parser.parse_args()

    sources = [s.strip() for s in args.source.split(",")]
    results = {}

    # TODO: Parse date range into start/end dates
    date_start, date_end = None, None
    if args.date and ":" in args.date:
        date_start, date_end = args.date.split(":")

    for source in sources:
        if source == "pubmed":
            searcher = PubMedSearcher()
            # TODO: Pass date_start, date_end, and args.type to search()
            results["pubmed"] = searcher.search(args.query, max_results=args.max)
        elif source in ("biorxiv", "medrxiv"):
            searcher = BioRxivSearcher(server=source)
            results[source] = searcher.search(args.query, max_results=args.max)
        elif source == "semantic":
            searcher = SemanticScholarSearcher()
            results["semantic_scholar"] = searcher.search(args.query, max_results=args.max)
        elif source == "scholar":
            searcher = GoogleScholarSearcher()
            results["google_scholar"] = searcher.search(args.query, max_results=args.max)
        elif source == "all":
            # TODO: Search all sources and deduplicate by DOI
            for s in ["pubmed", "biorxiv", "semantic", "scholar"]:
                pass  # Implement all-source search with deduplication

    # TODO: Implement --format bibtex and text output modes
    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
    else:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
```

### Phase 4: Create SKILL.md Documentation (Day 2-3)

#### Step 4.1: Create main skill documentation
Create `skills/paper-search/SKILL.md` with:
- Overview and purpose
- When to use / when not to use
- Database coverage table
- Unified CLI interface documentation
- Per-database quick reference
- Cross-references to source-specific docs
- Integration with literature-review
- Best practices

#### Step 4.2: Create database selection guide
Create `skills/paper-search/references/database_selection.md`:
- Decision matrix by domain
- Overlap analysis between databases
- Comprehensive search strategies
- Coverage gaps to be aware of

#### Step 4.3: Create query best practices
Create `skills/paper-search/references/query_best_practices.md`:
- Universal query construction principles
- Boolean operator usage
- Field tag strategies
- Date filtering best practices

### Phase 5: Update Existing Skills (Day 3)

#### Step 5.1: Update citation-management
Edit `skills/citation-management/SKILL.md`:
- Remove Stage 1 (Paper Discovery) workflow
- Remove search script documentation
- Add cross-reference to paper-search for finding papers
- Update "when to use" section
- Update success criteria

#### Step 5.2: Update literature-review
Edit `skills/literature-review/SKILL.md`:
- Update Stage 2 (Systematic Search) to reference paper-search
- Add explicit command examples using paper-search
- Update cross-references table

Delete duplicate search script:
```bash
rm skills/literature-review/scripts/search_databases.py
```

#### Step 5.3: Update SKILL_ROUTER.md
Edit `skills/SKILL_ROUTER.md`:
- Add paper-search to decision trees
- Update "Research Workflow" decision tree
- Remove research-lookup references
- Update quick reference matrix

### Phase 6: Testing and Validation (Day 3-4)

#### Step 6.1: Test each source module

> **Note**: Each source module should maintain standalone CLI capability for testing.
> If the original scripts don't have CLI, add `if __name__ == "__main__":` blocks.

```bash
# Test PubMed (verify CLI works after migration)
python skills/paper-search/sources/pubmed/search.py \
  "CRISPR sickle cell" --max 5

# Test bioRxiv (new module - must implement CLI)
python skills/paper-search/sources/biorxiv/search.py \
  "single cell sequencing" --max 5

# Test Semantic Scholar (new module - must implement CLI)
python skills/paper-search/sources/semantic_scholar/search.py \
  "transformer protein folding" --max 5

# Test Google Scholar (verify CLI works after migration)
python skills/paper-search/sources/google_scholar/search.py \
  "machine learning drug discovery" --max 5
```

**Alternative**: Test modules via Python import if no standalone CLI:
```python
# In Python REPL or test script
from paper_search.sources.pubmed.search import PubMedSearcher
searcher = PubMedSearcher()
results = searcher.search("CRISPR sickle cell", max_results=5)
print(results)
```

#### Step 6.2: Test unified interface
```bash
# Single source
python skills/paper-search/scripts/search.py \
  "CAR-T cell therapy" --source pubmed --max 10

# Multiple sources
python skills/paper-search/scripts/search.py \
  "CRISPR therapeutics" --source pubmed,biorxiv --max 10

# Output to file
python skills/paper-search/scripts/search.py \
  "gene therapy" --source semantic --output test_results.json
```

#### Step 6.3: Validate citation-management still works
```bash
# Validate citations (should still work)
python skills/citation-management/scripts/validate_citations.py test.bib

# DOI to BibTeX (should still work)
python skills/citation-management/scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2
```

### Phase 7: Cleanup and Deprecation (Day 4)

#### Step 7.1: Create deprecation notices
Add to `skills/research-lookup/SKILL.md`:
```markdown
> **DEPRECATED**: This skill has been replaced by `paper-search`.
> See `skills/paper-search/SKILL.md` for the new multi-database search skill.
```

Add to `skills/pubmed-database/SKILL.md`:
```markdown
> **DEPRECATED**: This skill has been merged into `paper-search`.
> See `skills/paper-search/sources/pubmed/` for PubMed-specific documentation.
```

#### Step 7.1.1: High-Impact Skill Updates (COMPLETED in Phase 5)

The following high-impact skills were updated to replace `research-lookup` references with `paper-search` during Phase 5 (early completion):

**Already Updated:**
- ✅ `scientific-writing/SKILL.md` (v2.4.0) - All references updated
- ✅ `scientific-writing/references/writing_process.md` - Updated
- ✅ `scientific-slides/SKILL.md` (v2.3.0) - All references updated
- ✅ `scientific-slides/assets/powerpoint_design_guide.md` - Updated
- ✅ `research-paper-summarizer/SKILL.md` - Cross-reference updated

**Remaining Files (lower priority, update in Phase 7):**
- [ ] `commands/scientific-writer-init.md` - Init command mentions
- [ ] `skills/statistical-analysis/SKILL.md` - Cross-reference only
- [ ] `skills/markitdown/SKILL.md` - Cross-reference only
- [ ] `skills/venue-templates/REVIEW_AND_IMPROVEMENTS.md` - Cross-references
- [ ] `skills/QUANTIFICATION_THRESHOLDS.md` - "Referenced by" list
- [ ] `skills/paper-search/references/bioinformatics_databases.md` - Footer text

#### Step 7.2: Remove deprecated skills (after validation)
```bash
# Only after all tests pass
rm -rf skills/research-lookup
rm -rf skills/pubmed-database
```

### Phase 8: Documentation and Commit (Day 4)

#### Step 8.0: Update README.md
Update the skills table in `README.md`:
```markdown
# Before:
| `research-lookup` | Literature search and database queries |

# After:
| `paper-search` | Multi-database academic paper search (PubMed, bioRxiv, Semantic Scholar) |
```

#### Step 8.1: Update CHANGELOG.md
```markdown
## [Unreleased]

### Added
- `paper-search` skill: unified multi-database academic paper search
  - PubMed support with full MeSH/Boolean query syntax
  - bioRxiv/medRxiv preprint search
  - Semantic Scholar integration (200M+ papers)
  - Google Scholar support
  - Unified CLI with `--source` routing

### Changed
- `citation-management`: refocused on validation and formatting (search moved to paper-search)
- `literature-review`: Stage 2 now references paper-search for database queries
- `SKILL_ROUTER.md`: updated decision trees for new skill structure

### Removed
- `research-lookup`: replaced by paper-search (no more Perplexity dependency)
- `pubmed-database`: merged into paper-search
```

#### Step 8.2: Commit changes
```bash
git add -A
git commit -m "feat: restructure research skills into paper-search

BREAKING CHANGE: research-lookup and pubmed-database deprecated

- Create paper-search skill with multi-database support
  - PubMed (from citation-management + pubmed-database docs)
  - bioRxiv/medRxiv (new)
  - Semantic Scholar (new)
  - Google Scholar (from citation-management)
- Refocus citation-management on validation/formatting only
- Update literature-review to use paper-search for Stage 2
- Update SKILL_ROUTER.md decision trees
- Remove Perplexity dependency entirely (hallucination risk)

🤖 Generated with Claude Code

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## 7. SKILL_ROUTER Updates

### 7.1 Updated Research Workflow Decision Tree

```
User needs research/information support
│
├─ Need to FIND papers?
│  │
│  ├─ Quick search (1-20 papers)?
│  │  └─ YES → paper-search
│  │            │
│  │            ├─ Biomedical topic? → --source pubmed
│  │            ├─ Need preprints? → --source biorxiv
│  │            ├─ Cross-domain? → --source semantic
│  │            └─ Broad coverage? → --source all
│  │
│  └─ Systematic literature search (50+ papers)?
│     └─ YES → literature-review (uses paper-search for Stage 2)
│
├─ Need to MANAGE citations?
│  │
│  └─ YES → citation-management
│            │
│            ├─ Validate DOIs/metadata
│            ├─ Convert to BibTeX
│            └─ Format references
│
└─ Need to EVALUATE a paper?
   │
   └─ YES → peer-review
```

### 7.2 Updated Quick Reference Matrix

| Task | Primary Skill | Notes |
|------|---------------|-------|
| "Find papers on X" | paper-search | Use --source flag for database selection |
| "Search PubMed for..." | paper-search | `--source pubmed` |
| "Find preprints on..." | paper-search | `--source biorxiv` or `--source medrxiv` |
| "Comprehensive literature search" | literature-review | Uses paper-search internally |
| "Format my references" | citation-management | BibTeX/citation styling |
| "Validate these citations" | citation-management | DOI resolution, metadata check |
| "Convert DOI to BibTeX" | citation-management | `doi_to_bibtex.py` |

---

## 8. Validation Checklist

### Pre-Migration
- [ ] Backup current skills directory
- [ ] Document current test queries that work

### Phase 1: Structure
- [ ] Directory structure created
- [ ] PubMed references copied (3 files from pubmed-database)
- [ ] Search scripts moved (2 files from citation-management)
- [ ] Search reference docs moved (2 files from citation-management)
- [ ] K-Dense marketing content NOT copied

### Phase 2: New Modules
- [ ] bioRxiv search.py created and tested
- [ ] bioRxiv search_guide.md created
- [ ] Semantic Scholar search.py created and tested
- [ ] Semantic Scholar api_guide.md created

### Phase 3: Unified Interface
- [ ] search.py CLI created
- [ ] Single source search works
- [ ] Multi-source search works
- [ ] Output formats work (json, bibtex, text)

### Phase 4: Documentation
- [ ] paper-search/SKILL.md complete
- [ ] database_selection.md created
- [ ] query_best_practices.md created

### Phase 5: Updates
- [ ] citation-management updated (search removed)
- [ ] literature-review updated (references paper-search)
- [ ] literature-review/scripts/search_databases.py deleted
- [ ] SKILL_ROUTER.md updated
- [ ] README.md updated (research-lookup → paper-search)

### Phase 6: Testing
- [ ] All source modules return valid results
- [ ] Unified CLI routes correctly
- [ ] citation-management validation still works
- [ ] No broken cross-references

### Phase 7: Cleanup
- [ ] Deprecation notices added
- [ ] research-lookup removed
- [ ] pubmed-database removed

### Phase 8: Documentation
- [ ] CHANGELOG.md updated
- [ ] Git commit created
- [ ] All tests pass

---

## 9. Rollback Plan

If critical issues are discovered:

### Restore Deprecated Skills
```bash
git checkout HEAD~1 -- skills/research-lookup
git checkout HEAD~1 -- skills/pubmed-database
```

### Restore citation-management Search
```bash
git checkout HEAD~1 -- skills/citation-management/scripts/search_pubmed.py
git checkout HEAD~1 -- skills/citation-management/scripts/search_google_scholar.py
git checkout HEAD~1 -- skills/citation-management/SKILL.md
```

### Remove paper-search
```bash
rm -rf skills/paper-search
```

### Restore SKILL_ROUTER
```bash
git checkout HEAD~1 -- skills/SKILL_ROUTER.md
```

---

## Appendix A: API Reference Quick Links

| Database | API Documentation |
|----------|-------------------|
| PubMed E-utilities | https://www.ncbi.nlm.nih.gov/books/NBK25501/ |
| bioRxiv API | https://api.biorxiv.org/ |
| Semantic Scholar | https://api.semanticscholar.org/ |
| Google Scholar | (scraping-based, no official API) |

## Appendix B: Rate Limits

| Database | Without Key | With Key |
|----------|-------------|----------|
| PubMed | 3 req/sec | 10 req/sec |
| bioRxiv | 30 req/min | N/A |
| Semantic Scholar | 100 req/5min | 1 req/sec |
| Google Scholar | N/A (scraping) | N/A |

---

*Document created: 2026-01-04*
*Last updated: 2026-01-04*
