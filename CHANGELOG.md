# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
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
