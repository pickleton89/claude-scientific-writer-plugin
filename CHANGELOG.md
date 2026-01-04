# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **skills/paper-search/**: Phase 2 implementation - new source modules
  - **sources/biorxiv/search.py**: bioRxiv/medRxiv API client with preprint search
    - Support for both bioRxiv and medRxiv servers
    - Date range and subject category filtering
    - Keyword matching in title/abstract
    - BibTeX export with preprint metadata
    - CLI with `--server`, `--date-start`, `--date-end`, `--category` options
  - **sources/biorxiv/references/search_guide.md**: Comprehensive bioRxiv API documentation
    - API endpoints and response format
    - Subject category lists for both servers
    - CLI examples and Python usage patterns
  - **sources/semantic_scholar/search.py**: Semantic Scholar API client (200M+ papers)
    - Paper search with year, field, and citation filters
    - Citation graph traversal (get_citations, get_references)
    - Author lookup and paper retrieval by ID/DOI/arXiv
    - Open access PDF filtering
    - Subcommand CLI: search, paper, citations, references, author
  - **sources/semantic_scholar/references/api_guide.md**: Semantic Scholar API documentation
    - Authentication and rate limits
    - Paper ID formats (DOI, arXiv, PMID, S2 ID)
    - Available fields and filters
    - CLI examples and Python usage patterns
- **skills/paper-search/**: Phase 1 implementation - directory structure and file migrations
  - Created source modules: `pubmed/`, `biorxiv/`, `semantic_scholar/`, `google_scholar/`
  - Migrated PubMed search script and documentation from `citation-management`
  - Migrated Google Scholar search script and documentation from `citation-management`
  - Copied PubMed API references from `pubmed-database` (api_reference.md, search_syntax.md, common_queries.md)
  - Copied bioinformatics_databases.md reference from `research-lookup`

### Changed
- **citation-management**: Removed search functionality (moved to paper-search)
  - Removed `scripts/search_pubmed.py` → now at `paper-search/sources/pubmed/search.py`
  - Removed `scripts/search_google_scholar.py` → now at `paper-search/sources/google_scholar/search.py`
  - Removed `references/pubmed_search.md` and `references/google_scholar_search.md`
  - Retained validation/formatting scripts: doi_to_bibtex.py, validate_citations.py, extract_metadata.py, format_bibtex.py

### Added
- **docs/PAPER_SEARCH_RESTRUCTURING.md**: Comprehensive restructuring plan for research skills
  - Decision to consolidate `research-lookup`, `citation-management`, and `pubmed-database` into two skills
  - New `paper-search` skill: unified multi-database academic literature search (PubMed, bioRxiv, Semantic Scholar, Google Scholar)
  - Refocused `citation-management`: validation and formatting only (search moved to paper-search)
  - Removes Perplexity AI dependency (5-10% hallucination risk)
  - 8-phase implementation plan with validation checklist and rollback procedures
- **skills/pubmed-database/**: PubMed database skill (to be merged into paper-search)
  - Comprehensive E-utilities API documentation
  - MeSH/Boolean search syntax reference
  - Common query patterns for systematic reviews

### Changed
- **literature-review/SKILL.md**: Added "So What?" Test emphasis
  - Stage 6 (Synthesis): Added callout requiring significance explanation for each theme
  - Stage 8 (Document Generation): Discussion must explain why findings matter
- **visual-design/SKILL.md**: Added Independence Test to Success Criteria
  - New checklist item: Figure + caption understandable without main text
  - Actionable test: Print figures with captions, verify key message is clear
- **research-paper-summarizer/SKILL.md**: Added Significance Test to Success Criteria
  - New "So What?" checklist item for markdown summary quality
  - Callout explaining implications, applications, and field impact requirements

### Added
- **research-paper-summarizer/references/reading_strategy.md**: New strategic reading guide for summarization
  - Non-linear reading sequence (Abstract → Conclusions → Results → Introduction → Methods)
  - Relevance filter with "Weather Test" for information selection
  - Section-specific reading goals and time estimates
  - Quick reference card for at-a-glance guidance
  - Integration with summarization workflow
- **QUANTIFICATION_THRESHOLDS.md §11**: New Summarization Quality section (v1.0.0 → v1.1.0)
  - Five Rules of Summarization (Independence, Conciseness, Objectivity, Originality, Jargon)
  - Length thresholds by summary type (executive, paper, abstract)
  - Writing quality metrics for summaries
  - Content completeness requirements by summary type
  - Source fidelity checklist
  - Summarization anti-patterns table
  - AI-assisted summarization method comparison

### Changed
- **research-paper-summarizer/SKILL.md**: Enhanced with summarization best practices
  - Added `<strategic_reading>` section with non-linear reading sequence
  - Added "Rule of Originality (No Copying)" to Core Principles with clarification on terms vs. prose
  - Added "Five Rules of Summarization" validation table to Success Criteria
  - Added filtering criteria (relevance filter, "Weather Test")
  - Updated references to include reading_strategy.md
- **executive-summary/SKILL.md**: Enhanced with summarization best practices
  - Added "5. Paraphrase, Don't Copy (Rule of Originality)" to Writing Rules
  - Added "Step 5: Compare to Source" validation step to workflow
  - Added "Five Rules of Summarization" table to Validation Checklist
  - Added two new checklist items for originality and source comparison
- **research-paper-summarizer/IMPLEMENTATION_PLAN.md**: Added future enhancement roadmap
  - Appendix D: Semantic clustering pipeline for very long documents (v2.0 roadmap)
  - Best Representation Vectors approach with clustering diagram
  - AI-assisted summarization method comparison table
  - Version roadmap (v1.0 → v2.0 → v2.1)

### Added
- **scientific-writing/references/writing_principles.md**: Enhanced with best practices alignment
  - New "Reader-Centricity" section as the Cardinal Rule (cognitive load principle, rule of parsimony, narrative arc)
  - New "Quick Diagnostic: The Four Tests" pre-submission checklist (Elevator Pitch, Independence, "So What?", Formatting)
  - Updated "Final Thoughts" with reader-centricity as principle #1 and Four Tests quick reference
- **docs/SKILLS_CONSOLIDATION_PLAN.md**: Comprehensive implementation plan for skills audit findings
  - Initiative 1: Merge ScholarEval scoring into `peer-review` as optional output mode
  - Initiative 2: Consolidate `latex-posters` + `pptx-posters` into unified `research-posters` skill
  - Initiative 3: Clarify document-skills adapter documentation and references
  - Initiative 4: Default-on Oligon brand application for all visual output skills
  - Includes 5-week implementation timeline, deprecation strategies, and testing checklists

### Added
- **research-posters**: New unified skill consolidating `latex-posters` and `pptx-posters` (Initiative 2, tasks 2.1-2.4)
  - Format selection decision tree (LaTeX vs PowerPoint) based on equations, timeline, collaboration needs
  - Shared workflows: Requirements (Stage 1), Visual Content (Stage 4), Quality Validation (Stage 5)
  - Branched workflows: Stage 3A (LaTeX) and Stage 3B (PowerPoint)
  - LaTeX package sub-selection: beamerposter, tikzposter, baposter
  - Merged reference documents: poster_content_guide.md, poster_design_principles.md, poster_layout_design.md
  - Format-specific references: latex_packages.md (renamed), pptx_workflows.md (new)
  - Copied assets: 3 LaTeX templates, quality checklist, review script

### Changed
- **scientific-writing/references/imrad_structure.md**: Enhanced "So What?" test prominence
  - Added prominent callout box in Discussion section with ⚠️ warning
  - Updated Common Mistakes to emphasize "So What?" as the #1 Discussion failure
- **scientific-writing/references/figures_tables.md**: Added Independence Test terminology
  - Renamed "Self-Explanatory Display Items" section to include "(The Independence Test)"
  - Added actionable test instruction as blockquote
- **Cross-references updated** for poster skills consolidation (Initiative 2, tasks 2.7-2.10):
  - `README.md`: Replaced `latex-posters`/`pptx-posters` with `research-posters`, updated skill count (25→23)
  - `SKILL_ROUTER.md`: Updated all poster routing to `research-posters` (v1.3.0 → v1.4.0)
  - Updated 10+ skill files: visual-design, scientific-schematics, oligon-brand, generate-image, paper-2-web, markdown-to-pdf, scientific-slides, peer-review/references, commands/scientific-writer-init
  - `venue-templates/REVIEW_AND_IMPROVEMENTS.md`: Added deprecation notice for poster consolidation
- **peer-review**: Merged ScholarEval 8-dimension scoring as optional output mode (Initiative 1)
  - Added Output Mode Selection after Stage 1 (Full Review / Scoring Only / Review + Scoring)
  - Added Stage 1.5: Quantitative Scoring with 8-dimension framework and quality tiers (A-F)
  - Migrated `calculate_scores.py` script for automated score calculation
  - Migrated `scholareval_framework.md` and `scholareval_expert_guide.md` reference docs
  - Added `templates/scoring_report.md` for structured scoring output
  - Updated Resources table and cross-references
- **Cross-references updated** for scholar-evaluation deprecation (Initiative 1, task 1.9):
  - `README.md`: Removed scholar-evaluation row, updated peer-review description
  - `scientific-writing/SKILL.md`: Updated Feeds table to reference peer-review scoring mode
  - `QUANTIFICATION_THRESHOLDS.md`: Updated §4 "Referenced by" section
  - `venue-templates/REVIEW_AND_IMPROVEMENTS.md`: Added deprecation notice, updated 3 references
- **SKILL_ROUTER.md**: Updated routing for peer-review scoring modes (v1.2.0 → v1.3.0)
  - Research Workflow decision tree now routes to peer-review with mode selection
  - Updated Research Task Routing table and Quick Reference Matrix
  - Updated Ambiguous Scenarios clarifying questions
  - Skill count reduced from 26 to 25 (scholar-evaluation merged)

### Deprecated
- **scholar-evaluation**: Marked as DEPRECATED, successor is `peer-review` (scoring mode)
  - Will be removed in v2.0.0
  - Migration: Use `peer-review` and select "Scoring Only" or "Review + Scoring" mode
- **latex-posters**: Marked as DEPRECATED, successor is `research-posters` (LaTeX format)
  - Will be removed in v2.0.0
  - Migration: Use `research-posters` and select LaTeX format when prompted
- **pptx-posters**: Marked as DEPRECATED, successor is `research-posters` (PowerPoint format)
  - Will be removed in v2.0.0
  - Migration: Use `research-posters` and select PowerPoint format when prompted

## [1.1.0] - 2025-01-02

### Changed
- **README.md**: Updated documentation to reflect v1.1.0 changes
  - Added Prerequisites section documenting `anthropic-agent-skills` dependency
  - Updated `document-skills` description to reflect adapter pattern
  - Added Changelog section linking to CHANGELOG.md
  - Added Advanced section linking to SKILL_ROUTER.md for workflow planning
- **document-skills**: Refactored from full implementation to thin adapter pattern
  - Removed duplicated docx/, pdf/, pptx/, xlsx/ subdirectories (2.7 MB savings)
  - Now routes to `anthropic-agent-skills` marketplace plugin for core functionality
  - Preserved scientific enhancements (schematics integration) in adapter SKILL.md
- Updated all cross-references to use marketplace notation (`document-skills:pptx` instead of `document-skills/pptx`)
  - SKILL_ROUTER.md (19 references updated)
  - scientific-writing/SKILL.md
  - scientific-slides/SKILL.md
  - venue-templates/SKILL.md
  - markdown-to-pdf/SKILL.md
  - executive-summary/SKILL.md
  - oligon-brand/SKILL.md
  - scientific-slides/assets/powerpoint_design_guide.md

### Removed
- Duplicated OOXML schemas from docx/ and pptx/ directories
- Duplicated Python/JS scripts from all document-skills subdirectories
- LICENSE.txt files from document-skills subdirectories (now in marketplace plugin)

### Dependencies
- Now requires `anthropic-agent-skills` marketplace plugin for document processing

## [1.0.0] - 2025-12-30

### Added
- Initial release with 25+ scientific writing skills
- Skills for research papers, literature reviews, posters, presentations
- Statistical analysis and reproducible research guidance
- Citation management and venue templates
- Oligon brand integration
- Document processing (DOCX, PDF, PPTX, XLSX)
