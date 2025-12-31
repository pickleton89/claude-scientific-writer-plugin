---
name: scientific-writing
version: 2.3.0
description: "Guides scientific manuscript writing using IMRAD structure, citations (APA/AMA/Vancouver), and reporting guidelines (CONSORT/STROBE/PRISMA). Use when writing research papers, journal submissions, abstracts, or scientific documents requiring structured prose with proper citations."
allowed-tools: Read, Write, Edit, Bash
quantification-reference: "../QUANTIFICATION_THRESHOLDS.md"
execution-standards: "../../docs/EXECUTION_STANDARDS.md"
when_to_use: |
  - Writing or revising any section of a scientific manuscript (abstract, introduction, methods, results, discussion)
  - Structuring a research paper using IMRAD or other standard formats
  - Formatting citations and references in specific styles (APA, AMA, Vancouver, Chicago, IEEE)
  - Creating, formatting, or improving figures, tables, and data visualizations
  - Applying study-specific reporting guidelines (CONSORT, STROBE, PRISMA)
  - Drafting abstracts that meet journal requirements
  - Preparing manuscripts for submission to specific journals
  - Improving writing clarity, conciseness, and precision
  - Addressing reviewer comments and revising manuscripts
---

# Scientific Writing

## Overview

**This is the core skill for the deep research and writing tool**—combining AI-driven deep research with well-formatted written outputs. Every document produced is backed by comprehensive literature search and verified citations through the research-lookup skill.

Scientific writing is a process for communicating research with precision and clarity. Write manuscripts using IMRAD structure, citations (APA/AMA/Vancouver), figures/tables, and reporting guidelines (CONSORT/STROBE/PRISMA). Apply this skill for research papers and journal submissions.

**Critical Principle: Always write in full paragraphs with flowing prose. Never submit bullet points in the final manuscript.** Use a two-stage process: first create section outlines with key points using research-lookup, then convert those outlines into complete paragraphs.

## Prerequisites

### Required Skills

| Skill | Purpose | When Needed |
|-------|---------|-------------|
| `research-lookup` | Literature search and citation retrieval | Stage 1 (outline creation), Introduction, Discussion |
| `statistical-analysis` | Test selection and statistical reporting | Methods and Results sections |

### Validation Scripts

This skill includes validation scripts for quality assurance. Run from the skill directory:

```bash
# Validate writing quality (sentence length, passive voice)
python {baseDir}/scripts/validate_writing_quality.py manuscript.md

# Count and verify citations by section
python {baseDir}/scripts/count_citations.py manuscript.md --by-section

# Calculate readability scores
python {baseDir}/scripts/readability_score.py manuscript.md
```

**No external dependencies required** - all scripts use Python standard library only.

---

## Core Philosophy

Scientific writing is not just recording what was done—it is an **argument designed to persuade** the reader of your findings' validity and significance. Three principles should guide every piece of scientific writing:

### Reader-Centricity

Do not write for yourself; write for the reader. Assume readers are intelligent but lack your specific context. The goal is to transfer information with minimal cognitive load. Every sentence should serve the reader's understanding, not demonstrate the author's expertise.

### The Rule of Parsimony

Less is more. Include only what is necessary to support the conclusion. If a detail (like the weather on the day of the experiment) does not impact the result, remove it. Each paragraph, sentence, and word must earn its place in the manuscript.

### Logical Flow as Narrative

Determine the narrative arc before writing. Experiments may be performed out of order, but the report must present them in a linear logic that builds a coherent argument. The reader should never wonder "why am I reading this?"—every section should connect to the central thesis.

---

## Visual Enhancement with Scientific Schematics

**Every scientific paper should include visual elements.** Use the `scientific-schematics` and `generate-image` skills to create figures.

### Minimum Figure Requirements

| Document Type | Minimum | Recommended |
|--------------|---------|-------------|
| Research Papers | 5 | 6-8 |
| Literature Reviews | 4 | 5-7 |
| Posters | 6 | 8-10 |

### Figure Types by Skill

**Use `scientific-schematics` for**:
- Graphical abstracts (required for every paper)
- Study design flowcharts (CONSORT, PRISMA, STROBE)
- Conceptual frameworks and methodology diagrams
- Biological pathways, system architectures

**Use `generate-image` for**:
- Photorealistic illustrations
- Medical/anatomical visualizations
- Cover images and infographics

For detailed figure creation instructions, consult the respective skill documentation.

---

## Core Capabilities

### 1. Manuscript Structure and Organization

> **Reference:** See `../QUANTIFICATION_THRESHOLDS.md` §1 (Literature Coverage) for citation targets.

**IMRAD Format**: Guide papers through the standard Introduction, Methods, Results, And Discussion structure used across most scientific disciplines. This includes:
- **Introduction**: Establish research context, identify gaps, state objectives
- **Methods**: Detail study design, populations, procedures, and analysis approaches
- **Results**: Present findings objectively without interpretation
- **Discussion**: Interpret results, acknowledge limitations, propose future directions

**Section Word Count Targets:**

| Section | Short Paper (3000 words) | Standard (5000 words) | Long (8000 words) |
|---------|-------------------------|----------------------|-------------------|
| Abstract | 150-250 | 200-300 | 250-350 |
| Introduction | 400-600 | 600-900 | 900-1200 |
| Methods | 600-900 | 900-1400 | 1400-2000 |
| Results | 600-900 | 1000-1500 | 1500-2400 |
| Discussion | 600-900 | 1000-1500 | 1500-2000 |
| Conclusion | 100-200 | 150-300 | 200-400 |

**Citation Targets by Section:**

| Section | Original Research | Review Article |
|---------|------------------|----------------|
| Introduction | 8-15 citations | 15-30 citations |
| Methods | 3-8 citations | 5-10 citations |
| Results | 0-3 citations | N/A |
| Discussion | 10-20 citations | 30-60 citations |
| **Total** | ≥30 citations | ≥100 citations |

For detailed guidance on IMRAD structure, refer to `references/imrad_structure.md`.

**Alternative Structures**: Support discipline-specific formats including:
- Review articles (narrative, systematic, scoping)
- Case reports and case series
- Meta-analyses and pooled analyses
- Theoretical/modeling papers
- Methods papers and protocols

### 2. Section-Specific Writing Guidance

For detailed IMRAD section guidance, refer to `references/imrad_structure.md`.

**Abstract**: 150-300 words as flowing paragraphs (never labeled sections unless journal requires). Cover: context, methods, key findings with numbers, significance.

**Executive Summary vs. Abstract**: Abstracts are neutral paper summaries for academic indexing. Executive summaries lead with conclusions/recommendations for decision-makers. For executive summaries, use `executive-summary` skill instead.

**Introduction (Funnel Approach)**: Broad context → Specific problem → Knowledge gap → Your study objectives.

**Methods**: Ensure reproducibility—participant descriptions, procedures, statistics, equipment, ethics.

**Results**: Logical flow, integrate figures/tables, statistics with effect sizes, no interpretation.

**Discussion**: Relate to questions, compare literature, acknowledge limitations, implications.

### 3. Citation and Reference Management

Apply citation styles correctly across disciplines. For comprehensive style guides, refer to `references/citation_styles.md`.

**Major Citation Styles:**
- **AMA (American Medical Association)**: Numbered superscript citations, common in medicine
- **Vancouver**: Numbered citations in square brackets, biomedical standard
- **APA (American Psychological Association)**: Author-date in-text citations, common in social sciences
- **Chicago**: Notes-bibliography or author-date, humanities and sciences
- **IEEE**: Numbered square brackets, engineering and computer science

**Best Practices:**
- Cite primary sources when possible
- Include recent literature (last 5-10 years for active fields)
- Balance citation distribution across introduction and discussion
- Verify all citations against original sources
- Use reference management software (Zotero, Mendeley, EndNote)

### 4. Figures and Tables

Create effective data visualizations that enhance comprehension. For detailed best practices, refer to `references/figures_tables.md`.

**Core Principle**: Every figure must have a clear one-sentence message. If it doesn't support a specific conclusion, delete it.

**Quick Reference:**
- **Tables**: Precise numerical data, exact values needed
- **Figures**: Trends, patterns, relationships, visual comparisons
- **Colors**: Never red/green; use Viridis, Magma, or ColorBrewer
- **Format**: Always vector (PDF, SVG) for scalability

### 5. Reporting Guidelines by Study Type

Ensure completeness and transparency by following established reporting standards. For comprehensive guideline details, refer to `references/reporting_guidelines.md`.

**Key Guidelines:**
- **CONSORT**: Randomized controlled trials
- **STROBE**: Observational studies (cohort, case-control, cross-sectional)
- **PRISMA**: Systematic reviews and meta-analyses
- **STARD**: Diagnostic accuracy studies
- **TRIPOD**: Prediction model studies
- **ARRIVE**: Animal research
- **CARE**: Case reports
- **SQUIRE**: Quality improvement studies
- **SPIRIT**: Study protocols for clinical trials
- **CHEERS**: Economic evaluations

Each guideline provides checklists ensuring all critical methodological elements are reported.

### 6. Writing Principles and Style

> **Reference:** See `../QUANTIFICATION_THRESHOLDS.md` §7 (Writing Quality Rubric) for scoring criteria.

Apply fundamental scientific writing principles. For detailed guidance, refer to `references/writing_principles.md`.

**Four pillars**: Clarity (precise language, defined terms), Conciseness (eliminate redundancy, 15-20 word sentences), Accuracy (exact values, consistent terminology), Objectivity (unbiased, acknowledge limitations).

**Writing Quality Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Sentence length (average) | ≤25 words | 15-20 words | 12-18 words |
| Paragraph length | ≤200 words | 100-150 words | 80-120 words |
| Passive voice usage | ≤40% | ≤25% | ≤15% |
| Acronyms per page | ≤8 | ≤5 | ≤3 |
| Grammar errors per page | ≤3 | ≤1 | 0 |
| Readability (Flesch-Kincaid) | Grade 12-16 | Grade 10-14 | Grade 8-12 |

**Sentence Structure Guidelines:**
- Average sentence length: 15-20 words (≤25 maximum)
- Vary sentence structure (simple, compound, complex)
- Front-load key information in each sentence
- One main idea per sentence

### 7. Writing Process: From Outline to Full Paragraphs

**CRITICAL: Always write in full paragraphs, never submit bullet points in scientific papers.**

Use the two-stage writing process:

**Stage 1: Create Section Outlines**
- Use research-lookup to gather relevant literature
- Create structured outlines with bullet points marking main arguments, key studies, data points
- These bullets are scaffolding, NOT the final manuscript

**Stage 2: Convert to Full Paragraphs**
- Transform bullet points into complete sentences
- Add transitions between ideas (however, moreover, subsequently)
- Integrate citations naturally within sentences
- Ensure logical flow from sentence to sentence

For detailed examples, the outline-to-prose conversion guide, common mistakes, and when lists are acceptable, see `references/writing_process.md`.

### 8. Journal-Specific Formatting

Adapt manuscripts to journal requirements:
- Follow author guidelines for structure, length, and format
- Apply journal-specific citation styles
- Meet figure/table specifications (resolution, file formats, dimensions)
- Include required statements (funding, conflicts of interest, data availability, ethical approval)
- Adhere to word limits for each section
- Format according to template requirements when provided

### 9. Field-Specific Language and Terminology

Adapt language, terminology, and conventions to match the target scientific discipline. Each field has established vocabulary, preferred phrasings, and domain-specific conventions.

**Key principles**:
- Match audience expertise level (specialized vs. broad-impact journals)
- Define technical terms strategically (at first use, appropriate for audience)
- Maintain terminology consistency throughout the manuscript
- Avoid field-mixing errors (don't import terms incorrectly from adjacent fields)

For detailed discipline-specific guides covering Biomedical, Molecular Biology, Chemistry, Ecology, Physics, Neuroscience, and Social Sciences, see `references/field_terminology.md`.

### 10. Common Pitfalls to Avoid

**Top rejection reasons**: Poor statistics, over-interpretation, irreproducible methods, inadequate samples, poor writing, weak literature review, unclear figures, missing reporting guidelines.

**Writing issues**: Tense mixing (past for methods/results, present for facts), undefined jargon, disrupted flow, missing transitions.

### 11. Error Handling

Common failure scenarios and how to resolve them:

| Scenario | Symptoms | Resolution |
|----------|----------|------------|
| **Literature search returns no results** | Empty citation list, unable to support claims | Broaden search terms, try synonyms, check alternative databases (PubMed, Scopus, Google Scholar). If topic is truly novel, state this explicitly and cite foundational work. |
| **Conflicting reporting guidelines** | Study crosses categories (e.g., observational + interventional) | Use primary guideline for main study type, incorporate relevant items from secondary guidelines, document in Methods which guidelines were followed. |
| **Word count exceeds journal limit** | Section totals exceed target | Run `validate_writing_quality.py` to identify verbose passages. Prioritize cutting: redundant citations, over-explained methods, tangential discussion points. Move details to supplementary materials. |
| **Citation count below minimum** | `count_citations.py` reports LOW status | Return to research-lookup for additional sources. Focus on: recent review articles, seminal papers, methodological references. Verify you haven't missed citing relevant work. |
| **Readability score too high (>16)** | `readability_score.py` reports TOO_COMPLEX | Break compound sentences, replace jargon with simpler terms where precision allows, add transitional phrases. Target: 1 idea per sentence. |
| **Mixed tense throughout manuscript** | Reviewer feedback on inconsistent tense | Methods/Results: past tense ("We measured..."). Introduction/Discussion: present for established facts ("Cancer is..."), past for specific studies ("Smith found..."). |
| **Figures rejected by journal** | Resolution/format/size errors | Check journal guidelines for DPI (typically 300+), format (TIFF/EPS preferred), dimensions. Use vector formats (PDF/SVG) when possible. |
| **Missing ethics statement** | Desk rejection | Add required statements: IRB approval number, informed consent process, data availability, conflict of interest declarations. Check ICMJE requirements. |

**Validation workflow after each section:**
1. Run `python {baseDir}/scripts/validate_writing_quality.py section.md`
2. Run `python {baseDir}/scripts/count_citations.py section.md`
3. Address any FAIL or LOW status before proceeding

## Workflow for Manuscript Development

**Stage 1: Planning** — Identify journal, determine reporting guideline, outline IMRAD structure, plan figures/tables.

**Stage 2: Drafting** — Start with figures/tables, then write sections using two-stage process (outline → prose). Order: Methods → Results → Discussion → Introduction → Abstract → Title.

**Stage 3: Revision** — Check flow, consistency, figure clarity, guideline adherence, citations, word counts, proofread.

**Stage 4: Final Preparation** — Format for journal, prepare supplementary materials, write cover letter, complete checklists.

### Version Management

**Never overwrite previous versions.** Always increment version numbers when editing manuscripts:

| Version | File Name | Purpose |
|---------|-----------|---------|
| Initial | `v1_draft.tex` | First complete draft |
| Revision 1 | `v2_draft.tex` | After first round of edits |
| Revision 2 | `v3_draft.tex` | After second round of edits |

Document changes in `revision_notes.md` with date and summary of modifications.

> **Full workflow standards:** See `docs/EXECUTION_STANDARDS.md` for file organization, progress logging, and PDF review procedures.

### Pre-Submission Diagnostic Tests

Run three tests before submission:
1. **Elevator Pitch**: Can someone grasp the main finding from Title + Abstract alone?
2. **Independence**: Do figures/captions tell the complete story without main text?
3. **So What?**: Does Discussion explicitly state why findings matter?

**Quick checks**: Acronyms defined, citations consistent, figures legible (fonts ≥8pt).

---

## Cross-References

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

### Uses (Input From)

| Skill | Relationship |
|-------|-------------|
| `research-lookup` | Literature search and citation finding |
| `hypothesis-generation` | Research hypotheses that drive narrative |
| `literature-review` | Synthesized background for Introduction and Discussion |
| `statistical-analysis` | Test selection, statistical reporting in Methods, interpreting results |
| `plotting-libraries` | Data visualizations for Results section |
| `scientific-schematics` | Methodology diagrams, CONSORT/PRISMA flowcharts |
| `generate-image` | Photorealistic figures and cover images |

### Feeds (Output To)

| Skill | Relationship |
|-------|-------------|
| `citation-management` | Organize and format manuscript references |
| `peer-review` | Structured feedback and revision guidance |
| `scholar-evaluation` | Publication readiness assessment (8 dimensions) |
| `executive-summary` | Action-oriented summaries for decision-makers |
| `venue-templates` | Journal-specific formatting and requirements |
| `markdown-to-pdf` | Branded PDF output with Oligon styling |
| `paper-2-web` | Web-optimized HTML version |
| `document-skills/docx` | Word format for journal submission |
| `document-skills/pdf` | PDF for preprints or supplementary materials |

### Related

| Skill | Relationship |
|-------|-------------|
| `reproducible-research` | Data Availability statements, environment documentation, FAIR compliance |
| `code-documentation` | Documenting analysis code referenced in Methods sections |

### Workflow Guidance

**Drafting**: Use this skill for general principles (IMRAD, citations, clarity). For quantitative Methods sections, reference `statistical-analysis` for proper test selection and reporting. For Data Availability statements, use `reproducible-research` guidance.

**Figures**: Coordinate with `plotting-libraries` for data plots, `scientific-schematics` for diagrams, and `generate-image` for photorealistic visuals.

**Output**: After drafting, use `venue-templates` for journal-specific formatting, then export via `document-skills/docx` for Word submissions or `markdown-to-pdf` for branded PDF output.

## References

**Reference Documents** (load as needed):
- `references/imrad_structure.md` - Detailed IMRAD section guidance
- `references/citation_styles.md` - APA, AMA, Vancouver, Chicago, IEEE formats
- `references/figures_tables.md` - Data visualization best practices
- `references/reporting_guidelines.md` - CONSORT, STROBE, PRISMA checklists
- `references/writing_principles.md` - Clarity, conciseness, style
- `references/field_terminology.md` - Discipline-specific language guides
- `references/writing_process.md` - Outline-to-prose conversion examples

**Validation Scripts** (run for quality assurance):
- `scripts/validate_writing_quality.py` - Sentence/paragraph length, passive voice
- `scripts/count_citations.py` - Citation counts by section
- `scripts/readability_score.py` - Flesch-Kincaid, Gunning Fog, SMOG indices
