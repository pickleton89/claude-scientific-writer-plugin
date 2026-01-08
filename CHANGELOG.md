# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **skills/hypothesis-generation/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~55-60% current determinism, targeting 85% (25-30% variance reduction)
  - Key insight: Well-documented with excellent workflow structure (8 stages), quantified thresholds (≥40 citations, <5% search saturation, quality scores ≥5/10); variance exists because thresholds are stated but never validated—missing validation layer transforms aspirational into enforced requirements
  - 3-phase implementation plan with complete Python code:
    - Phase 1: Critical validation (`validate_input.py`, `validate_hypothesis.py`, `track_citations.py`)
    - Phase 2: Quality automation (`score_hypothesis.py`, `check_distinctiveness.py`)
    - Phase 3: Workflow validation (`validate_stage_exit.py`, `latex_preflight.py`)
  - Ready-to-implement modules with complete code for all 7 validation scripts
  - Structured input schema with domain enum (biomedical, chemistry, physics, ecology, materials, computational, neuroscience, engineering)
  - Hypothesis structure validator enforcing mechanism (trigger/pathway/outcome/causal_chain), evidence (≥3 citations), assumptions (≥2), and predictions (≥2 with falsification criteria)
  - Automated quality scorer calculating testability, falsifiability, parsimony scores deterministically; flags explanatory_power and distinctiveness for LLM review
  - Citation tracker validating ≥40 total, ≥10 main text, ≥60% recent papers thresholds
  - Hypothesis distinctiveness checker using mechanism term overlap (Jaccard similarity <0.4 threshold)
  - Stage exit validators for stages 1, 2, 4, 5, 7 checking all exit criteria before progression
  - LaTeX preflight checker validating required environments, sections, appendices, bibliography, and page break placement
  - Calibration examples: strong hypothesis (9/10) vs weak hypothesis (2/10) with detailed scoring rationale
  - Detection patterns: domain classification keywords, strong/weak prediction markers
  - Deterministic scorecard: Input validation 30%→85%, Hypothesis structure 50%→95%, Citation tracking 20%→95%
  - Priority matrix: validate_input (P0), validate_hypothesis (P0), track_citations (P0), score_hypothesis (P1)
  - Success metrics: overall determinism 55-60%→70%→80%→85% across three phases

- **skills/literature-review/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~75% current determinism, targeting 90% (15% variance reduction)
  - Key insight: Remarkably well-structured with excellent reference documentation, explicit numerical thresholds, decision matrices, and two working Python scripts (verify_citations.py, generate_pdf.py); remaining variance is in unvalidated inputs, unstandardized intermediate outputs, and subjective processes (theme identification)
  - 3-phase implementation plan with complete Python code:
    - Phase 1: Critical validation (`prisma_validator.py`, PICO/PEO/SPIDER JSON schemas, preflight validation)
    - Phase 2: Quality & selection (`quality_scorer.py`, `database_selector.py`, `review_config.py`)
    - Phase 3: Tracking & polish (screening tracker format, search syntax validators, exit criteria checker)
  - Ready-to-implement modules with complete code for all utilities
  - PRISMA flow validator checking arithmetic consistency of identification→screening→included numbers
  - Quality assessment scorer with tool-specific domain definitions (RoB2, NOS, QUADAS2, CASP, AMSTAR2)
  - Algorithmic database selector implementing decision matrix from decision_frameworks.md
  - Research question schemas (PICOQuestion, PEOQuestion, SPIDERQuestion dataclasses) with validation
  - Review configuration preflight validator checking database coverage, date ranges, criteria specificity
  - Deterministic scorecard: Input validation 50%→90%, PRISMA documentation 70%→95%, Quality assessment 60%→85%
  - Detection pattern appendix: research question type detection, study design pattern matching
  - Priority matrix: prisma_validator (P0), PICO schemas (P0), quality_scorer (P1), database_selector (P1)
  - Success metrics: input validation coverage 50%→95%, PRISMA accuracy 70%→98%, overall determinism 75%→93%

- **skills/markdown-to-pdf/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~85% current determinism, targeting 95% (10% variance reduction)
  - Key insight: Skill is highly deterministic due to excellent delegation to Python libraries (`oligon_reports`) with explicit pattern matching; remaining variance is in presentation formatting
  - 3-phase implementation plan with complete Python code:
    - Phase 1: Critical fixes (`preflight_check()` function, brand color consistency, element summary template)
    - Phase 2: Output standardization (`format_structure_tree()`, frontmatter JSON schemas, `ValidationResult` type)
    - Phase 3: Polish (error recovery map, automated tests, documentation deduplication)
  - Already-deterministic components documented: table classification (STATUS_SYMBOLS/GRADE_VALUES sets), finding detection (regex), callout detection (prefix matching), language filtering (explicit enum), template listing, filename generation
  - Critical issue identified: brand color mismatch between SKILL.md and component_map.md requiring single source of truth
  - Ready-to-implement modules: `PreflightResult` dataclass, structure tree generator, error recovery JSON lookup
  - Detection pattern reference appendix with all deterministic patterns used by the skill
  - Priority matrix: preflight_check (P0), brand color fix (P0), structure tree (P1), frontmatter schemas (P1)
  - Success metrics: determinism 85%→90%→93%→95% across three phases

- **skills/oligon-brand/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~85% current determinism, targeting 95% (10% variance reduction)
  - Key insight: Exceptionally well-structured with machine-readable JSON tokens, explicit hex codes, and format-specific adapters; remaining variance is in decision tree interpretation and manual verification
  - 3-phase implementation plan with complete Python code:
    - Phase 1: Quick wins (`select_cycle()` function, `run_preflight()` validator)
    - Phase 2: Core infrastructure (`validate_palette()`, `count_brand_blue()`, workflow docs update)
    - Phase 3: Advanced features (JSON→Markdown generator, adapter test suite, grayscale contrast checker)
  - Ready-to-implement modules with complete code for all utilities
  - Deterministic cycle selector converting text decision tree to callable function with enum inputs
  - Automated preflight validator checking background, spines, grid (returns structured pass/fail dict)
  - Color palette validator extracting colors from figures and comparing against allowed brand set
  - Brand Blue usage counter to enforce 1-2 element limit per panel
  - Pydantic schema for structured brand requests (n_series, context, output_format, target_medium)
  - Testing plan for adapter consistency and regression prevention
  - Priority matrix: select_cycle (P0), run_preflight (P0), validate_palette (P1), brand blue counter (P1)
  - Success metrics: determinism 85%→95%, preflight automation 0%→80%, color validation manual→automated

- **skills/paper-2-web/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~55% current determinism, targeting 85% (30% variance reduction)
  - Key insight: Well-structured orchestration wrapper around Paper2All tool, but relies heavily on LLM interpretation of decision trees and manual quality validation
  - 3-phase implementation plan with complete Python code:
    - Phase 1: Quick wins (`schemas/transformation_request.yaml`, `lib/venue_database.py`, `scripts/validate_links.py`)
    - Phase 2: Core infrastructure (`lib/cost_estimator.py`, `lib/component_router.py`, `scripts/preflight_check.py`)
    - Phase 3: Advanced features (`lib/reproducibility.py`, `lib/quality_scorer.py`)
  - Ready-to-implement modules with complete code for all utilities
  - Structured input schema (YAML) replacing decision tree interpretation
  - Venue database with 20+ conference poster specifications (NeurIPS, ICML, ISMB, etc.)
  - Cost estimator with token-based pricing and paper complexity multipliers
  - Component router with deterministic use-case-to-output mapping
  - Preflight validation script checking inputs, dependencies, API keys, and figure resolution
  - Automated link checker for generated websites using async HTTP validation
  - Reproducibility manifest system with SHA256 hashing and config tracking
  - Quality scorer with deterministic thresholds for website, poster, and video outputs
  - Success metrics: input variance HIGH→LOW, quality check automation 10%→80%, preflight catch rate 0%→90%
  - Priority matrix: input schema (P0), venue database (P0), cost estimator (P1), preflight (P1)

- **skills/paper-search/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~85% current determinism, targeting 95% (10% variance reduction)
  - Key insight: Skill is exceptionally well-designed with code-based search infrastructure; remaining variance is in query construction and database selection
  - 3-phase implementation plan with complete Python code:
    - Phase 1: Quick wins (`scripts/query_templates.py`, `scripts/database_router.py`)
    - Phase 2: Core improvements (`scripts/query_schema.py`, `scripts/query_validator.py`)
    - Phase 3: Enhancements (`references/gene_aliases.json`, result analysis)
  - Ready-to-implement modules with complete code for all utilities
  - Query template library with 6+ common patterns (review search, author papers, clinical trials)
  - Automated database router with keyword-based domain classification (biomedical vs CS/AI)
  - Structured query schema (StructuredQuery dataclass) for deterministic query construction
  - Gene alias lookup with 18+ common genes (TP53, BRCA1, EGFR, etc.) expandable from HGNC
  - Query syntax validator for PubMed with field tag and boolean clause checking
  - Result count analyzer with deterministic feedback (too_few/good/too_many thresholds)
  - Reproducibility hash generation for search logging
  - Testing plan with unit, integration, and reproducibility tests
  - Priority matrix: query templates (P0), database router (P0), structured schema (P1)
  - Success metrics: query variance HIGH→LOW, routing consistency 70%→95%

- **skills/peer-review/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~35-40% current determinism, targeting 70-75% (30-35% variance reduction)
  - Key insight: Excellent structural foundations (quantitative rubrics, staged workflows, score calculator) but relies on LLM judgment to apply them
  - 4-phase implementation plan with complete Python code:
    - Phase 1: Critical infrastructure (`validators/severity_classifier.py`, extended `calculate_scores.py` validation)
    - Phase 2: Workflow automation (`scripts/workflow_tracker.py` for stage gate enforcement)
    - Phase 3: Calibration & lookup (`calibration/` examples, `validators/issue_lookup.py`)
    - Phase 4: Advanced validators (`scripts/figure_checker.py`, `validators/statistical_tests.py`)
  - Ready-to-implement modules with complete code for all utilities
  - Severity classifier encoding SKILL.md quantitative criteria (Critical/Major/Minor thresholds)
  - Score validation ensuring completeness, bounds checking, and justification requirements
  - Workflow state tracker with stage exit criteria from workflow_transitions.md
  - JSON schemas for manuscript input and review output validation
  - Common issue catalog with 22+ issues mapped to severity levels and recommendation templates
  - Statistical test selection tree converting decision matrix to Python lookup
  - Figure quality checker against quantified thresholds (DPI, font size, contrast ratio)
  - Testing plan with unit, integration, and regression tests
  - Priority matrix: severity_classifier (P0), score validation (P0), workflow tracker (P1)
  - Success metrics: severity consistency 60%→95%, score variance ±0.8→±0.3 points

- **skills/plotting-libraries/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~55-60% current determinism, targeting 80% (20-25% variance reduction)
  - Key insight: Decision matrices (Python vs R, library selection, thresholds) are deterministic in design but need code implementation
  - 4-phase implementation plan with complete Python code:
    - Phase 1: Reproducibility fixes (random seeds in clustering, version pins) - P0 priority
    - Phase 2: Parameter lookup tables (`scripts/plotting_params.py` with thresholds, journal specs, palettes)
    - Phase 3: Input validation (`scripts/validate_data.py` for volcano/heatmap data)
    - Phase 4: Output validation (`scripts/validate_figure.py` for saved figures)
  - Ready-to-implement modules with complete code for all utilities
  - Volcano threshold presets (exploratory, standard, stringent, very_stringent)
  - Journal figure specifications (Nature, Cell, Science, PLOS) with dimension lookup
  - Color palette module with colorblind-safe options (Okabe-Ito, volcano, heatmap diverging)
  - Plot type classifier converting user requests to plot types via keyword matching
  - Ecosystem classifier (Python vs R) based on library/tool mentions
  - Data validation with specific checks for volcano plots and heatmaps
  - Figure validation with PDF/PNG checks (dimensions, DPI, fonts embedded)
  - Testing plan with pytest examples for all validators
  - Priority matrix emphasizing random seeds and version pins as P0 quick wins
  - Success metrics showing path from 55% to 80% deterministic parameter selection

- **skills/research-paper-summarizer/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~55-60% current determinism, targeting 75-80% (20% variance reduction)
  - Key insight: Excellent architectural foundations (subagent pipeline, templates, section markers) but validation is prose-based
  - 3-phase implementation plan with complete Python code:
    - Phase 1: Validation infrastructure (`scripts/validate_summary.py`, `scripts/validate_yaml.py`, `schemas/summary_output.yaml`)
    - Phase 2: Pre-processing scripts (`scripts/extract_statistics.py`, `scripts/detect_article_type.py`, `scripts/update_markers.py`)
    - Phase 3: Integration with subagent prompts and SKILL.md workflow
  - Ready-to-implement modules with complete code for all utilities
  - Summary validation with 9 quality checks (pending sections, statistics count, figure references, limitations, sample sizes)
  - JSON Schema for YAML output validation before PDF generation
  - Statistics extraction via regex (p-values, CIs, sample sizes, fold changes, hazard/odds ratios)
  - Article type auto-detection via keyword scoring with confidence levels
  - Deterministic section marker management (replaces LLM file editing)
  - Regex pattern reference for statistics and figure references
  - Structured output requirements for subagent prompts (XML tags for statistics_found, figure_references)
  - Success metrics: 0% → 80% validation coverage, <10% failed output rate target
  - Priority matrix: validate_summary.py (P1), extract_statistics.py (P2), YAML schema (P1)

- **skills/research-posters/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~60-70% current determinism, targeting 85% (15-25% variance reduction)
  - Key insight: Skill has strong foundations (templates, review script, quantified criteria) but validation is mostly manual
  - 4-phase implementation plan with complete Python code:
    - Phase 1: Core validation (`scripts/validate_poster.py` for word count, fonts, images, compilation)
    - Phase 2: Accessibility validation (`scripts/validate_accessibility.py` for WCAG contrast, colorblind safety)
    - Phase 3: Enhanced review script (LaTeX log parsing, word count, QR code detection)
    - Phase 4: Examples directory with complete poster samples and expected outputs
  - Ready-to-implement modules with complete code for all utilities
  - Poster specification YAML schema for structured inputs
  - Quality report JSON format for machine-readable validation results
  - Contrast ratio calculation with WCAG 2.1 compliance checking
  - Colorblind simulation (deuteranopia) for palette validation
  - Word count extraction from LaTeX block structures
  - Integration with existing `review_poster.sh` script
  - Testing plan and success metrics (30% → 75% automated validation coverage)
  - Dependencies documented: poppler-utils, texcount, zbar, Python 3.8+

- **skills/scientific-schematics/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~35% current determinism, targeting 60% (25% variance reduction)
  - Key insight: Core image generation is inherently stochastic (AI-based), but significant gains possible through pre-generation validation
  - 3-phase implementation plan with complete Python code:
    - Phase 1: Pre-generation validation (`scripts/validate_prompt.py`, `scripts/utils/complexity_limits.py`)
    - Phase 2: Deterministic selection (`scripts/diagram_type_selector.py`, `scripts/utils/brand_colors.py`)
    - Phase 3: Output validation (`scripts/validate_image.py`, `scripts/utils/schemas.py`)
  - Ready-to-implement modules with complete code for all utilities
  - Prompt validation with keyword detection for diagram types, layout, and component counts
  - Schematic type selector converting prose decision tree to Python lookup function
  - Complexity pre-check against diagram type limits (max nodes, edges, levels)
  - Brand color lookup module with Oligon, Okabe-Ito, and generic palettes
  - Pydantic schemas for GenerationResults and IterationResult
  - Image metadata validation (dimensions, format, file size checks)
  - Testing plan with pytest examples for all validators
  - Priority matrix: prompt validator (P1), type selector (P2), complexity check (P3)
  - Success metrics showing path from 35% to 60% deterministic decision-making

- **skills/scientific-writing/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~40% current determinism, targeting 70% (30% variance reduction)
  - Key insight: Skill has excellent validation scripts but prose-based decision guidance should be code
  - 4-phase implementation plan with complete Python code:
    - Phase 1: Decision trees → code (`scripts/select_guideline.py` for study design → reporting guideline, `scripts/select_citation_style.py` for journal → citation style)
    - Phase 2: Structure validation (`scripts/validate_structure.py` for IMRAD compliance checking)
    - Phase 3: Section targets calculator (`scripts/calculate_targets.py` for word counts and citation targets)
    - Phase 4: Data files (`data/journal_requirements.json` with structured venue specifications)
  - Ready-to-implement modules with complete code for all utilities
  - JSON Schema definitions for manuscript metadata input
  - Structured output dataclasses (StructureValidation, ManuscriptQualityReport, PreSubmissionChecklist)
  - Existing validation scripts analyzed: validate_writing_quality.py, readability_score.py, count_citations.py
  - Testing infrastructure with pytest examples
  - Priority matrix: guideline selector and citation style selector are P0 (high impact, low effort)
  - Success metrics showing path from 40% to 70% deterministic outputs

- **skills/statistical-analysis/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~60% current determinism, targeting 90% (highest potential among audited skills)
  - Key insight: Skill is built on decision trees, lookup tables, and mathematical formulas—ideal for code-based execution
  - 4-phase implementation plan with complete Python code:
    - Phase 1: Deterministic test selector (`scripts/test_selector.py` encoding full decision tree as if/elif logic)
    - Phase 2: Multiple testing correction wrapper (`scripts/mtc_corrector.py` with structured output)
    - Phase 3: Effect size interpreter (`scripts/effect_interpreter.py` with threshold lookup tables)
    - Phase 4: Power calculator (`scripts/power_calculator.py` wrapping statsmodels)
  - Ready-to-implement modules with complete code for all utilities
  - JSON Schema definitions for three query types: test_selection, power_analysis, mtc_correction
  - Structured output dataclasses (TestRecommendation, MTCResult, EffectInterpretation, PowerResult)
  - Code templates for Python (scipy/statsmodels) and R for all common tests
  - Priority matrix emphasizing that test selection is the highest-impact target
  - Success metrics showing path from LLM-dependent to zero-variance outputs

- **skills/venue-templates/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~40% current determinism, targeting 75% (50-60% variance reduction)
  - Identified key issue: data fragmentation (venue specs duplicated across Python dicts and markdown)
  - 5-phase implementation plan with complete Python code:
    - Phase 1: Unified venue database (`data/venues.json` with JSON Schema, `venue_database.py` access layer)
    - Phase 2: Venue resolution with fuzzy matching (`venue_resolver.py` for deterministic name normalization)
    - Phase 3: Enhanced validation (citation format, abstract structure, anonymization, contribution list checks)
    - Phase 4: Style compliance checker (`check_style.py` for voice, jargon, abstract, hedging validation)
    - Phase 5: Style rules as structured data (`style_rules.yaml` with validatable patterns)
  - Ready-to-implement modules with complete code for all utilities
  - JSON Schema definitions for venue specifications
  - Migration guide for updating existing scripts
  - Testing infrastructure with pytest examples
  - Priority matrix and success metrics

- **skills/visual-design/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary: ~70% of decision-making can become deterministic (50-70% variance reduction)
  - Current state analysis: skill has strong foundations with decision matrices, but implemented as prose tables
  - 5-phase implementation plan with complete Python code:
    - Phase 1: Data extraction & schema (`venue_specs.py`, JSON Schema)
    - Phase 2: Core utilities (`chart_selector.py`, `palette_selector.py`)
    - Phase 3: Accessibility validation (`accessibility.py`, WCAG compliance)
    - Phase 4: Quality scoring (`quality_scorer.py`, hybrid 40% deterministic / 60% LLM)
    - Phase 5: Reference consolidation and worked examples
  - Ready-to-implement modules with complete code for all utilities
  - JSON Schema definitions for structured input/output
  - Testing plan with pytest structure
  - Success metrics and file structure roadmap

- **skills/scientific-slides/DETERMINISM_AUDIT.md**: Comprehensive determinism audit and implementation plan
  - Executive summary with key findings and expected 40-60% variance reduction
  - Current state analysis mapping stochastic vs deterministic components
  - 4-phase implementation plan with complete Python code:
    - Phase 1: Deterministic post-generation validation (PIL-based image analysis)
    - Phase 2: JSON schema for structured slide plan inputs
    - Phase 3: Hybrid quality scoring (40% deterministic, 60% AI)
    - Phase 4: Documentation consolidation
  - Ready-to-implement modules: `validate_slide_image.py`, `validate_slide_plan.py`, `prompt_templates.py`, `hybrid_quality_scorer.py`
  - JSON schema definition for slide plans
  - Testing plan with pytest unit and integration tests
  - Success metrics and timeline summary

### Removed
- **Phase 7: Cleanup and deprecation completed**
  - Removed `skills/research-lookup/` directory (replaced by paper-search)
  - Removed `skills/pubmed-database/` directory (merged into paper-search)
  - All documentation preserved in paper-search skill

### Changed
- **Phase 8: Paper-search restructuring complete** - All 8 phases implemented, `docs/PAPER_SEARCH_RESTRUCTURING.md` marked complete
- **Phase 7: Final cross-reference updates**
  - Updated `commands/scientific-writer-init.md`: paper-search now featured skill
  - Updated `skills/statistical-analysis/SKILL.md`: cross-reference to paper-search
  - Updated `skills/markitdown/SKILL.md`: cross-reference to paper-search
  - Updated `skills/venue-templates/REVIEW_AND_IMPROVEMENTS.md`: updated integration references
  - Updated `skills/QUANTIFICATION_THRESHOLDS.md`: §6 now references paper-search
  - Updated `skills/paper-search/references/bioinformatics_databases.md`: footer attribution
- **Phase 6: Testing and validation completed**
  - All source modules tested: PubMed (✅), bioRxiv (✅), Semantic Scholar (⚠️ rate-limited without API key), Google Scholar (⚠️ requires `scholarly` library)
  - Unified CLI tested: single source, multi-source, deduplication, output formats (JSON, BibTeX, text)
  - Citation-management scripts validated: doi_to_bibtex.py, validate_citations.py, format_bibtex.py, extract_metadata.py all working
  - Known limitations documented: Semantic Scholar requires API key for heavy usage; Google Scholar requires `pip install scholarly`
- **Phase 5: Existing skill updates for paper-search integration**
  - **citation-management/SKILL.md** (v2.0.0 → v2.1.0): Removed Stage 1 (Paper Discovery), renumbered stages, updated cross-references to use `paper-search`
  - **literature-review/SKILL.md**: Updated Stage 2 with paper-search CLI examples, updated cross-references table
  - **SKILL_ROUTER.md** (v1.4.0 → v1.5.0): Updated all routing tables, decision trees, and added consolidation note about research-lookup deprecation
  - **scientific-writing/SKILL.md** (v2.3.0 → v2.4.0): Updated 6 references from research-lookup to paper-search
  - **scientific-writing/references/writing_process.md**: Updated paper search integration section
  - **scientific-slides/SKILL.md** (v2.2.0 → v2.3.0): Updated workflow Stage 1, anti-patterns, and cross-references
  - **scientific-slides/assets/powerpoint_design_guide.md**: Updated research context best practices
  - **research-paper-summarizer/SKILL.md**: Updated cross-reference to paper-search
  - **README.md**: Updated skills table (research-lookup → paper-search)
  - **docs/PAPER_SEARCH_RESTRUCTURING.md**: Added Step 7.1.1 documenting completed updates and remaining files

### Removed
- **literature-review/scripts/search_databases.py**: Deprecated script removed (functionality now in paper-search)

### Added
- **skills/paper-search/SKILL.md**: Phase 4 implementation - main skill documentation
  - Complete skill definition following project SKILL.md conventions
  - YAML frontmatter (name, version, description, when_to_use, allowed-tools)
  - Prerequisites with Python dependencies and optional API keys
  - Unified CLI documentation with all options and examples
  - Database selection matrix by research domain
  - 3-stage workflow (Define Strategy → Execute Search → Export Results)
  - Usage examples covering common patterns (reviews, preprints, citations, multi-source)
  - Cross-references to source-specific documentation and related skills
  - Integration guidance for literature-review and citation-management workflows
- **skills/paper-search/**: Phase 3 implementation - unified search interface
  - **scripts/search.py**: Unified CLI for multi-database academic paper search
    - Routes to all sources: pubmed, biorxiv, medrxiv, semantic, scholar
    - Multi-source search with `--source pubmed,semantic,biorxiv`
    - Automatic DOI-based deduplication across sources
    - Output formats: JSON, BibTeX, human-readable text
    - Date normalization across database-specific formats
    - Source-specific filters: `--type` (PubMed), `--fields`/`--min-citations` (Semantic Scholar)
  - **references/database_selection.md**: Database selection decision guide
    - Quick decision matrix by research domain
    - Database profiles with strengths/limitations
    - Multi-source search strategies
    - Rate limits and API key recommendations
  - **references/query_best_practices.md**: Query construction guide
    - Core principles (broad-to-narrow, synonyms, Boolean operators)
    - Database-specific syntax examples
    - Common patterns (reviews, recent papers, highly-cited, author search)
    - Query templates for systematic reviews, tech assessments, grants
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
