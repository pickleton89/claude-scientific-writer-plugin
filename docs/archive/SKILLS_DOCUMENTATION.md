# Claude Scientific Writer - Skills Documentation

**Version:** 1.0.0
**Last Updated:** 2026-01-14
**Total Skills:** 23

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
   - [Skills Directory Structure](#skills-directory-structure)
   - [Routing System](#routing-system)
   - [Shared Infrastructure](#shared-infrastructure)
2. [Skills by Category](#skills-by-category)
   - [Visual Creation (4 skills)](#visual-creation)
   - [Document Creation (8 skills)](#document-creation)
   - [Research Workflow (5 skills)](#research-workflow)
   - [Analysis & Code (3 skills)](#analysis--code)
   - [Conversion (2 skills)](#conversion)
   - [Brand (1 skill)](#brand)
3. [Integration Matrix](#integration-matrix)
4. [Common Workflows](#common-workflows)
5. [Quality Standards](#quality-standards)

---

## Architecture Overview

The Claude Scientific Writer plugin provides a comprehensive suite of 23 specialized skills for scientific writing, research, and publication workflows. Skills are organized by function and connected through a deterministic routing system.

### Skills Directory Structure

```
skills/
├── SKILL_ROUTER.md              # Master routing decision trees
├── QUANTIFICATION_THRESHOLDS.md # Shared quality thresholds (11 sections)
├── BRAND_SKILL_INTERFACE.md     # Brand skill interface contract
├── SKILL_TEMPLATE.md            # Template for creating new skills
├── skill_triggers.yaml          # Keyword registry for routing
│
├── shared/                      # Shared utilities
│   ├── api_utils.py            # API key loading, HTTP utilities
│   └── tests/                  # Shared test infrastructure
│
└── [skill-name]/               # Individual skill directories
    ├── SKILL.md                # Skill documentation
    ├── scripts/                # Executable scripts
    ├── references/             # Detailed reference docs
    └── assets/                 # Templates, styles, configs
```

### Routing System

Skills are selected through a multi-layered routing system:

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| **Decision Trees** | `SKILL_ROUTER.md` | Human-readable routing via ASCII trees |
| **Keyword Registry** | `skill_triggers.yaml` | Deterministic routing via keywords/regex |
| **Confidence Scoring** | `route.py` module | Programmatic selection with thresholds |
| **Negative Keywords** | Per-skill exclusions | Prevent false positive matches |

**Routing Confidence Thresholds:**
- `≥0.7` → Direct routing to skill
- `0.3–0.7` → Requires clarification
- `<0.3` → No clear match; use fallback

### Shared Infrastructure

**QUANTIFICATION_THRESHOLDS.md** provides 11 sections of shared numeric standards:

| Section | Purpose |
|---------|---------|
| §1 Literature Coverage | Search saturation criteria |
| §2 Visual Quality | DPI, contrast, accessibility |
| §3 Replication & Sample Size | Experimental standards |
| §4 Issue Severity | Bug/issue classification |
| §5 Documentation Completeness | Coverage requirements |
| §6 Time-Based Thresholds | Publication recency |
| §7 Quality Scoring Rubrics | 10-point evaluation scales |
| §8 Iteration & Stopping | Refinement loop limits |
| §9 Figure & Plot Quality | Chart validation criteria |
| §10 Statistical Reporting | Required statistical elements |
| §11 Summarization Quality | Summary completeness metrics |

---

## Skills by Category

### Visual Creation

Four skills for generating visual content—from data plots to AI-generated images.

---

#### visual-design

**Foundation skill for visual standards across the plugin.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | Design philosophy, color theory, typography, accessibility |
| **Extended By** | plotting-libraries, scientific-schematics, generate-image, scientific-slides, research-posters |

**What It Does:**
Establishes the design foundation for all visual outputs. Defines color palettes (including colorblind-safe options), typography scales, composition principles, and WCAG 2.1 AA/AAA accessibility requirements.

**Key Capabilities:**
- Color theory and palette selection
- Typography hierarchy (8px–72px scale)
- Layout and composition principles
- WCAG accessibility standards (contrast ≥4.5:1)
- Colorblind-safe color schemes (Viridis, Cividis)

**When to Use:**
- Consulting design principles for any visual output
- Selecting color schemes for figures or presentations
- Ensuring accessibility compliance
- Understanding visual hierarchy

**Integration:**
- **Extended by:** All visual skills inherit these standards
- **Cross-references:** oligon-brand (for organizational styling)

---

#### plotting-libraries

**Data visualization with Python and R.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Extends** | visual-design |
| **Purpose** | Publication-quality data plots and charts |
| **Tools** | matplotlib, seaborn, plotly (Python); ggplot2, Bioconductor (R) |

**What It Does:**
Generates publication-ready data visualizations using standard scientific plotting libraries. Provides decision trees for chart type selection based on data characteristics and research domain.

**Key Capabilities:**
- Chart type selection (scatter, bar, box, heatmap, volcano, survival curves)
- Figure sizing for journal requirements
- Statistical annotations and significance indicators
- Multi-panel figure composition
- Export at publication resolution (300+ DPI)

**Workflow:**
1. **Data Assessment** → Determine variable types and relationships
2. **Chart Selection** → Use decision tree for appropriate visualization
3. **Implementation** → Generate using library-specific patterns
4. **Styling** → Apply visual-design standards
5. **Export** → Save at required resolution/format

**When to Use:**
- Creating charts, plots, or graphs from data
- Statistical result visualization
- Figure panels for papers or presentations

**When NOT to Use:**
- Diagrams/flowcharts → `scientific-schematics`
- Photos/illustrations → `generate-image`

**Reference Documents:**
- `references/matplotlib_patterns.md` - Python matplotlib patterns
- `references/seaborn_patterns.md` - Statistical visualization
- `references/ggplot2_patterns.md` - R grammar of graphics
- `references/scientific_plot_types.md` - Domain-specific plots

---

#### scientific-schematics

**Technical diagrams using tiered generation system.**

| Attribute | Value |
|-----------|-------|
| **Version** | 2.x |
| **Extends** | visual-design |
| **Purpose** | Flowcharts, pathways, circuits, architecture diagrams |
| **Tiers** | Mermaid/TikZ (free) or AI generation (publication-quality) |

**What It Does:**
Creates technical diagrams and scientific schematics with a tiered generation approach. Simple diagrams use free tools (Mermaid, TikZ), while complex publication-quality diagrams use AI image generation.

**Key Capabilities:**
- **Diagram Types:** Flowcharts, process diagrams, biological pathways, circuit diagrams, system architecture, neural network architectures, CONSORT diagrams
- **Tiered Generation:**
  - *Tier 1 (Free):* Mermaid.js, TikZ, draw.io
  - *Tier 2 (AI):* Gemini 3 Pro via OpenRouter for publication-quality output

**Decision Framework:**
```
What type of diagram?
├─ Simple flowchart (≤10 nodes)? → Mermaid (free)
├─ LaTeX-integrated? → TikZ (free)
├─ Complex layout or publication? → AI generation
└─ Biological pathway? → AI generation (recommended)
```

**Workflow:**
1. **Type Classification** → Identify diagram category
2. **Tier Selection** → Choose free vs. AI approach
3. **Generation** → Create using selected tool
4. **Validation** → Review against quality rubric
5. **Iteration** → Refine until quality ≥7/10

**When to Use:**
- Creating flowcharts, process diagrams
- Biological pathways, signaling cascades
- Circuit or electrical diagrams
- System architecture visualizations
- CONSORT or methodology diagrams

**When NOT to Use:**
- Data charts/plots → `plotting-libraries`
- Photos/illustrations → `generate-image`

**Reference Documents:**
- `references/diagram_types.md` - Comprehensive diagram guide
- `references/mermaid_patterns.md` - Mermaid.js syntax
- `references/tikz_patterns.md` - LaTeX TikZ patterns
- `scripts/generate_schematic_ai.py` - AI generation script

---

#### generate-image

**AI-powered image generation for photos, illustrations, and artwork.**

| Attribute | Value |
|-----------|-------|
| **Version** | 2.3.0 |
| **Extends** | visual-design |
| **Purpose** | Photorealistic images, illustrations, concept art |
| **Model** | Gemini 3 Pro via OpenRouter |

**What It Does:**
Generates and edits high-quality images using Google's Gemini 3 Pro model. Produces photos, illustrations, artwork, and visual assets for documents and presentations.

**Key Capabilities:**
- Image generation (photorealistic, artistic, scientific illustration)
- Image editing and modification
- Inpainting and background changes
- Prompt engineering framework
- Quality validation with scoring rubric

**Prompt Formula:**
`[SUBJECT] + [STYLE] + [MEDIUM] + [TECHNICAL] + [QUALITY]`

**Workflow:**
1. **Requirement Analysis** → Define image purpose and specifications
2. **Prompt Engineering** → Craft detailed prompt using formula
3. **Generation** → Execute via `scripts/generate_image.py`
4. **Validation** → Score against 10-point quality rubric
5. **Integration** → Place in project structure

**Iteration Limits:**
| Context | Soft Limit | Hard Limit |
|---------|------------|------------|
| Quick draft | 2 | 3 |
| Presentation | 3 | 4 |
| Publication | 4 | 5 |

**When to Use:**
- Photorealistic images for documents
- Scientific illustrations and concept art
- Visual assets for presentations/posters
- Image editing (background changes, modifications)

**When NOT to Use:**
- Technical diagrams → `scientific-schematics`
- Data visualizations → `plotting-libraries`

**Reference Documents:**
- `references/prompt_templates.md` - Prompt patterns
- `references/model_capabilities.md` - Model comparison
- `scripts/generate_image.py` - Generation script

---

### Document Creation

Eight skills for creating various document types—from research papers to presentations.

---

#### scientific-writing

**Research paper and manuscript creation.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | Research papers, manuscripts, IMRAD structure |
| **Output** | LaTeX, Markdown, Word-ready content |

**What It Does:**
Guides the creation of research papers and scientific manuscripts following the IMRAD structure (Introduction, Methods, Results, And Discussion). Provides templates, section-specific guidance, and integration with venue formatting.

**Key Capabilities:**
- IMRAD structure templates
- Section-by-section writing guidance
- Abstract and title optimization
- Reference integration
- Journal-ready formatting

**Document Structure:**
1. **Title** - Concise, specific, searchable
2. **Abstract** - Structured summary (background, methods, results, conclusions)
3. **Introduction** - Context, gap, hypothesis, approach
4. **Methods** - Reproducible experimental details
5. **Results** - Data presentation without interpretation
6. **Discussion** - Interpretation, limitations, implications
7. **References** - Properly formatted citations

**Workflow:**
1. **Planning** → Outline key findings and narrative
2. **Literature** → Use `paper-search` for citations
3. **Drafting** → Write section-by-section
4. **Figures** → Generate via `plotting-libraries` or `scientific-schematics`
5. **Formatting** → Apply `venue-templates` for target journal
6. **Export** → Via `document-skills:docx` or `markdown-to-pdf`

**When to Use:**
- Writing research papers or manuscripts
- Creating scientific reports
- Drafting thesis chapters

**When NOT to Use:**
- Executive summaries → `executive-summary`
- Slide presentations → `scientific-slides`

**Integration:**
- **Input from:** paper-search, literature-review, statistical-analysis
- **Output to:** venue-templates, document-skills:docx, markdown-to-pdf

---

#### executive-summary

**Stakeholder-focused summaries using the Pyramid Principle.**

| Attribute | Value |
|-----------|-------|
| **Version** | 2.0.1 |
| **Purpose** | Decision-maker summaries, grant applications, board presentations |
| **Method** | Pyramid Principle (conclusion-first) |

**What It Does:**
Generates concise, action-oriented executive summaries that enable decision-makers to understand key findings and take action without reading the full document.

**Five-Component Structure:**
1. **Hook/Problem** - Compelling statistic capturing attention
2. **Solution/Objective** - Methodology or approach (1-2 sentences)
3. **Key Findings** - Exactly 3-5 quantified insights
4. **Value/Impact** - ROI, benefits, significance
5. **Call to Action** - Specific next step with owner and timeline

**Core Constraints:**
| Constraint | Requirement |
|------------|-------------|
| Length | ≤10% of source OR ≤2 pages |
| Timing | Written AFTER full document complete |
| Independence | Must stand alone (no section references) |
| Style | Active voice ≥75% |

**Workflow:**
1. **Prerequisites** → Verify source document is complete
2. **Extract** → Identify 3-5 quantified key findings
3. **Determine** → Define specific recommendation (WHAT + WHO + WHEN)
4. **Draft** → Use five-component template
5. **Compare** → Verify accurate representation of source
6. **Validate** → Run `scripts/validate_summary.py`

**When to Use:**
- Summarizing reports for stakeholders
- Grant application summaries
- Board presentation overviews
- Distilling technical documents for decision-makers

**When NOT to Use:**
- Full paper abstracts → `scientific-writing`
- Detailed research summaries → `research-paper-summarizer`

**Reference Documents:**
- `references/examples.md` - Complete examples
- `references/visualization_guidelines.md` - Visual summary guidelines
- `scripts/validate_summary.py` - Quality validation

---

#### scientific-slides

**Conference presentations and research talks.**

| Attribute | Value |
|-----------|-------|
| **Version** | 2.3.0 |
| **Extends** | visual-design |
| **Purpose** | Conference talks, seminars, thesis defenses, grant pitches |
| **Output** | PDF (Nano Banana Pro), PowerPoint, LaTeX Beamer |

**What It Does:**
Creates effective scientific presentations with a visual-first approach. Supports multiple output formats with AI-powered slide generation capability.

**Talk Type Selection:**
| Type | Duration | Slides | Focus |
|------|----------|--------|-------|
| Conference | 5-20 min | 8-20 | 1-2 key findings |
| Seminar | 45-60 min | 40-60 | Comprehensive coverage |
| Thesis defense | 45-60 min | 45-60 + backup | Demonstrate mastery |
| Grant pitch | 10-20 min | 10-20 | Significance, feasibility |
| Journal club | 20-45 min | 20-35 | Critical analysis |

**Implementation Methods:**
| Method | Best For | Tool |
|--------|----------|------|
| Nano Banana Pro PDF | Stunning visuals, fast creation | `scripts/generate_slide_image.py` |
| PowerPoint | Editable slides, animations | `document-skills:pptx` |
| LaTeX Beamer | Equations, version control | `assets/beamer_template.tex` |

**Workflow:**
1. **Research & Planning** → Use `paper-search` for 8-15 citations
2. **Method Selection** → Choose PDF, PPTX, or Beamer
3. **Generation** → Create slides with selected method
4. **Validation** → Review against quality checklist
5. **Practice** → Minimum 3 runs with timing

**When to Use:**
- Conference presentations
- Academic seminars
- Thesis/dissertation defenses
- Grant pitch presentations

**When NOT to Use:**
- Research posters → `research-posters`
- Papers → `scientific-writing`

**Reference Documents:**
- `references/talk_types_guide.md` - Talk-specific guidance
- `references/slide_design_principles.md` - Visual design
- `references/beamer_guide.md` - LaTeX Beamer documentation

---

#### research-posters

**Conference poster creation in LaTeX or PowerPoint.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.0.0 |
| **Extends** | visual-design |
| **Purpose** | Conference posters, academic poster sessions |
| **Format** | LaTeX (beamerposter, tikzposter, baposter) or PowerPoint |

**What It Does:**
Creates publication-quality research posters with structured layouts. Enforces visual-first design with mandatory AI-generated figures.

**Core Requirements:**
- 2-3 AI-generated figures (via `scientific-schematics`)
- 40-50% visual content
- 300-800 words maximum
- 300+ DPI for all images

**Format Selection:**
| Factor | LaTeX | PowerPoint |
|--------|-------|------------|
| Complex equations (>5) | ✓ | |
| Version control needed | ✓ | |
| Timeline <48 hours | | ✓ |
| Collaborators need to edit | | ✓ |

**Workflow:**
1. **Requirements** → Size, orientation, deadline
2. **Format Selection** → LaTeX or PowerPoint
3. **Implementation** → Build using selected format
4. **Visual Content** → Generate figures via `scientific-schematics`
5. **Validation** → Print test at 25% scale

**When to Use:**
- Conference poster sessions
- Academic symposia
- Thesis defense posters

**When NOT to Use:**
- Slide presentations → `scientific-slides`
- Auto-generation from paper → `paper-2-web`

**Reference Documents:**
- `references/poster_layout_design.md` - Layout principles
- `references/latex_packages.md` - Package comparison
- `assets/beamerposter_template.tex` - LaTeX templates

---

#### venue-templates

**Journal and conference formatting requirements.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | 50+ venue templates, style guides, formatting requirements |
| **Coverage** | Nature/Science, Cell Press, Medical, ML/CS conferences, Grants |

**What It Does:**
Provides comprehensive formatting templates and style guides for major scientific publication venues. Includes specific requirements for figures, citations, word limits, and reviewer expectations.

**Template Categories:**
| Category | Examples |
|----------|----------|
| High-Impact Journals | Nature, Science, Cell |
| Medical Journals | NEJM, Lancet, JAMA |
| Specialty Journals | eLife, PNAS, JBC |
| ML/CS Conferences | NeurIPS, ICML, ACL |
| Grants | NIH, NSF, ERC |

**Key Capabilities:**
- Word count and section limits
- Figure requirements and sizing
- Citation style specifications
- Cover letter templates
- Reviewer expectation guides

**Workflow:**
1. **Venue Selection** → Identify target publication
2. **Template Retrieval** → Access venue-specific guide
3. **Formatting** → Apply requirements to manuscript
4. **Validation** → Check against venue checklist
5. **Export** → Generate submission-ready files

**When to Use:**
- Preparing manuscripts for specific journals
- Understanding reviewer expectations
- Writing cover letters
- Formatting grant proposals

**Integration:**
- **Input from:** scientific-writing, statistical-analysis
- **Output to:** document-skills:docx, markdown-to-pdf

**Reference Documents:**
- `references/venue_writing_styles.md` - Style comparison
- `references/reviewer_expectations.md` - What reviewers look for
- `templates/` - Venue-specific templates

---

#### hypothesis-generation

**Scientific hypothesis formulation with quality metrics.**

| Attribute | Value |
|-----------|-------|
| **Version** | 2.2.0 |
| **Purpose** | Generate testable hypotheses with quantified quality criteria |
| **Output** | LaTeX reports with colored hypothesis boxes |

**What It Does:**
Systematic hypothesis generation process producing 3-5 competing hypotheses with quality scoring, experimental designs, and testable predictions.

**Quality Rubric (10-point scale):**
| Criterion | Weight |
|-----------|--------|
| Testability | 2 pts |
| Falsifiability | 2 pts |
| Parsimony | 2 pts |
| Explanatory Power | 2 pts |
| Distinctiveness | 2 pts |

**Score Thresholds:**
- ≥8/10 → Strong (prioritize for testing)
- 5-7/10 → Viable (include with limitations)
- <5/10 → Weak (deprioritize)

**Workflow:**
1. **Understand Phenomenon** → Define observation/question
2. **Literature Search** → ≥40 papers from ≥3 databases
3. **Synthesize Evidence** → Identify gaps and mechanisms
4. **Generate Hypotheses** → 3-5 competing explanations
5. **Evaluate Quality** → Score against rubric
6. **Design Experiments** → For each viable hypothesis
7. **Formulate Predictions** → Specific, quantitative
8. **Present Output** → LaTeX document with colored boxes

**When to Use:**
- Developing hypotheses from observations
- Designing experiments for scientific questions
- Exploring competing explanations
- Planning mechanistic studies

**Reference Documents:**
- `references/hypothesis_quality_criteria.md` - Evaluation framework
- `references/experimental_design_patterns.md` - Design approaches
- `assets/hypothesis_report_template.tex` - LaTeX template

---

#### markdown-to-pdf

**Branded PDF generation from templated Markdown.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.0.0 |
| **Purpose** | Convert templated markdown to branded PDFs |
| **Templates** | 12 document types (scientific, project-mgmt, technical) |

**What It Does:**
Bridges template infrastructure and PDF component system for markdown-to-PDF conversion with Oligon brand styling.

**Available Templates:**
| Category | Types |
|----------|-------|
| Scientific | analysis-report, literature-review, data-report |
| Project-Mgmt | meeting-notes, project-status, phase-plan, task-list |
| Technical | technical-spec, method-guide, standards-guide |
| Meta | agent-definition, readme |

**Commands:**
- `/list-templates` - Display available templates
- `/new-doc <type>` - Create document from template
- `/doc-to-pdf <file>` - Convert to branded PDF

**Component Mapping:**
| Markdown Pattern | PDF Component |
|------------------|---------------|
| Tables with ✓/✗ | StatusTable |
| Tables with grades | GradedTable |
| `#### Finding N:` | FindingCard |
| Code blocks | MethodBlock |
| `> **Note:**` | CalloutBox |

**When to Use:**
- Creating branded PDFs from templates
- Generating professional reports
- Converting templated documents

**When NOT to Use:**
- Arbitrary file conversion → `markitdown`
- Academic papers → `scientific-writing`
- PowerPoint → `scientific-slides`

---

#### document-skills

**Namespace adapter for marketplace document capabilities.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.1.0 |
| **Purpose** | Routes to anthropic-agent-skills marketplace plugin |
| **Architecture** | Thin adapter (no processing logic) |

**What It Does:**
Provides namespace routing to the anthropic-agent-skills marketplace document capabilities. All processing is handled by the installed marketplace plugin.

**Available Sub-Skills:**
| Namespace | Routes To |
|-----------|-----------|
| `document-skills:docx` | Word document creation/editing |
| `document-skills:pptx` | PowerPoint creation/editing |
| `document-skills:pdf` | PDF manipulation |
| `document-skills:xlsx` | Excel spreadsheet creation |

**Prerequisite:** Requires anthropic-agent-skills marketplace plugin installation.

**Workflow Integration:**
```
scientific-writing → venue-templates → document-skills:docx
scientific-slides → document-skills:pptx
oligon-brand → document-skills:docx (with docx_adapter)
```

---

### Research Workflow

Five skills for literature discovery, management, and evaluation.

---

#### paper-search

**Multi-database academic paper search.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | Quick literature searches (1-50 papers) |
| **Databases** | PubMed, bioRxiv, Semantic Scholar, Google Scholar |

**What It Does:**
Provides unified access to multiple academic databases through a single interface. Performs DOI-based deduplication and exports results in various formats.

**Key Capabilities:**
- Multi-database search (PubMed, bioRxiv, Semantic Scholar, Google Scholar)
- DOI-based deduplication
- Citation export (BibTeX, RIS, plain text)
- Relevance scoring
- Publication metadata extraction

**Database Selection:**
| Database | Best For |
|----------|----------|
| PubMed | Biomedical, clinical |
| bioRxiv | Preprints, cutting-edge |
| Semantic Scholar | AI/ML, citation networks |
| Google Scholar | Broad coverage |

**Workflow:**
1. **Query Formation** → Define search terms and filters
2. **Database Selection** → Choose appropriate sources
3. **Execution** → Run via `scripts/search.py`
4. **Deduplication** → Remove duplicates by DOI
5. **Export** → Save citations for downstream use

**When to Use:**
- Quick literature searches (1-50 papers)
- Finding citations for introductions/discussions
- Identifying relevant papers for a topic

**When NOT to Use:**
- Systematic reviews (50+ papers) → `literature-review`
- Full paper summarization → `research-paper-summarizer`

**Reference Documents:**
- `references/database_guides.md` - Database-specific guidance
- `scripts/search.py` - Unified search CLI

---

#### literature-review

**Systematic literature reviews with PRISMA methodology.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | Comprehensive systematic reviews (50+ papers) |
| **Method** | PRISMA guidelines |

**What It Does:**
Conducts systematic literature reviews following PRISMA methodology. Includes search strategy documentation, screening workflows, and synthesis frameworks.

**Key Capabilities:**
- PRISMA-compliant workflow
- Search strategy documentation
- Inclusion/exclusion criteria
- Quality assessment frameworks
- Narrative and quantitative synthesis

**PRISMA Workflow:**
1. **Identification** → Define search strategy across databases
2. **Screening** → Title/abstract screening
3. **Eligibility** → Full-text assessment
4. **Inclusion** → Final paper selection
5. **Synthesis** → Data extraction and analysis

**Saturation Criteria:**
- <5% new papers in final search iteration
- ≥40 papers minimum (≥70 for comprehensive reviews)
- ≥3 databases searched

**When to Use:**
- Systematic reviews (50+ papers)
- Meta-analyses
- Grant background sections
- Thesis literature chapters

**When NOT to Use:**
- Quick searches (1-50 papers) → `paper-search`

**Uses Internally:** `paper-search` for Stage 2 database searches

**Reference Documents:**
- `references/prisma_checklist.md` - PRISMA requirements
- `references/synthesis_methods.md` - Analysis approaches
- `templates/literature_review_template.md` - Output template

---

#### citation-management

**BibTeX formatting and citation validation.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | Citation formatting, validation, metadata extraction |
| **Output** | BibTeX entries, formatted citations |

**What It Does:**
Manages citations throughout the research workflow. Extracts metadata from DOIs/PMIDs, validates citation completeness, and formats for various styles.

**Key Capabilities:**
- DOI/PMID/arXiv metadata extraction
- BibTeX entry generation
- Citation validation
- Style formatting (APA, MLA, Chicago, etc.)
- Duplicate detection

**Scripts:**
| Script | Purpose |
|--------|---------|
| `doi_to_bibtex.py` | Generate BibTeX from DOI |
| `validate_citations.py` | Check citation completeness |
| `format_bibtex.py` | Format/clean BibTeX files |

**Workflow:**
1. **Collection** → Gather DOIs/PMIDs from research
2. **Extraction** → Convert to BibTeX entries
3. **Validation** → Check for missing fields
4. **Formatting** → Apply target citation style
5. **Export** → Generate .bib file

**When to Use:**
- Managing references for papers
- Validating citation completeness
- Converting between citation formats

**Integration:**
- **Input from:** paper-search, literature-review
- **Output to:** scientific-writing, venue-templates

---

#### peer-review

**Manuscript evaluation with 8-dimension ScholarEval.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | Manuscript evaluation, scoring, constructive feedback |
| **Framework** | ScholarEval 8-dimension rubric |

**What It Does:**
Provides structured manuscript evaluation following reviewer expectations. Includes the ScholarEval 8-dimension scoring framework for objective quality assessment.

**ScholarEval Dimensions:**
1. **Significance** - Importance and impact
2. **Novelty** - Originality of contribution
3. **Clarity** - Writing quality and organization
4. **Methodology** - Experimental rigor
5. **Reproducibility** - Ability to replicate
6. **Limitations** - Acknowledgment of constraints
7. **References** - Citation quality and coverage
8. **Presentation** - Figures, tables, overall presentation

**Review Modes:**
| Mode | Output |
|------|--------|
| Full Review | Detailed feedback + scores |
| Scoring Only | 8-dimension ScholarEval scores |
| Review + Scoring | Combined output |

**Workflow:**
1. **Mode Selection** → Choose review type
2. **Initial Read** → Overall impression
3. **Detailed Evaluation** → Section-by-section analysis
4. **Scoring** → Apply ScholarEval rubric
5. **Synthesis** → Compile feedback and recommendations

**When to Use:**
- Evaluating manuscripts before submission
- Preparing reviewer-style feedback
- Self-assessment of draft quality

**Reference Documents:**
- `references/scholareval_rubric.md` - Scoring criteria
- `references/reviewer_templates.md` - Feedback templates
- `references/common_issues.md` - Typical problems

---

#### research-paper-summarizer

**Multi-format paper summarization with specialized subagents.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | Summarize research papers in multiple formats |
| **Subagents** | 4 specialized summarizers |

**What It Does:**
Summarizes research papers using domain-specialized subagents. Produces summaries in multiple output formats optimized for different use cases.

**Specialized Subagents:**
| Subagent | Domain |
|----------|--------|
| General | Cross-domain papers |
| Review | Review articles, meta-analyses |
| CompBio | Computational biology, bioinformatics |
| CellMolBio | Cell and molecular biology |

**Output Formats:**
| Format | Use Case |
|--------|----------|
| Markdown | Integration with notes |
| HTML | Web display, sharing |
| PDF | Archival, printing |
| SVG | Visual summary cards |

**Workflow:**
1. **Input** → Provide paper (PDF or URL)
2. **Detection** → Auto-detect paper domain
3. **Subagent Selection** → Route to appropriate summarizer
4. **Summarization** → Generate structured summary
5. **Export** → Output in requested format

**When to Use:**
- Summarizing papers for research notes
- Creating visual paper summaries
- Generating annotated bibliographies

**When NOT to Use:**
- Executive summaries for stakeholders → `executive-summary`

**Reference Documents:**
- `references/summary_templates.md` - Output templates
- `references/domain_detection.md` - Auto-detection logic

---

### Analysis & Code

Three skills for statistical analysis, reproducibility, and documentation.

---

#### statistical-analysis

**Test selection and code generation for Python/R.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.2.0 |
| **Purpose** | Statistical test selection, code generation, result interpretation |
| **Languages** | Python (scipy, statsmodels), R |

**What It Does:**
Guides rigorous statistical analysis with decision frameworks for test selection, code patterns for implementation, and interpretation guidance for manuscripts.

**Quick Test Selection:**
| Comparison | Normal | Non-Normal |
|------------|--------|------------|
| Two groups (unpaired) | t-test | Mann-Whitney U |
| Two groups (paired) | Paired t-test | Wilcoxon signed-rank |
| Multiple groups | ANOVA | Kruskal-Wallis |
| Correlation | Pearson | Spearman |

**Key Capabilities:**
- Test selection decision trees
- Python/R code generation
- Multiple testing correction (FDR, Bonferroni)
- Effect size calculation
- Power analysis and sample size estimation
- Reporting templates

**Workflow:**
1. **Research Question** → Define comparison type
2. **Data Assessment** → Check normality, sample size
3. **Test Selection** → Use decision framework
4. **Corrections** → Apply multiple testing correction
5. **Effect Sizes** → Calculate practical significance
6. **Reporting** → Format for manuscript

**When to Use:**
- Selecting appropriate statistical tests
- Generating analysis code
- Interpreting results for manuscripts
- Planning sample sizes

**Reference Documents:**
- `references/test_decision_framework.md` - Decision trees
- `references/python_scipy_patterns.md` - Python patterns
- `references/r_stats_patterns.md` - R patterns
- `references/multiple_testing_correction.md` - Correction methods

---

#### reproducible-research

**FAIR data practices and environment management.**

| Attribute | Value |
|-----------|-------|
| **Version** | 2.2.0 |
| **Purpose** | Reproducibility, FAIR principles, data deposition |
| **Coverage** | Conda, Docker, data repositories, metadata standards |

**What It Does:**
Guides documentation and structuring of reproducible scientific computing projects. Provides templates for environment specification, data deposition, and project organization.

**FAIR Compliance Scoring:**
| Principle | Weight | Minimum Requirements |
|-----------|--------|----------------------|
| Findable | 25% | DOI, ≥5 metadata fields |
| Accessible | 25% | Standard protocol, auth documented |
| Interoperable | 25% | Standard formats, ontologies |
| Reusable | 25% | License, provenance, domain standards |

**Environment Hierarchy:**
| Level | Method | Reproducibility |
|-------|--------|-----------------|
| 1 | requirements.txt | 25-49% |
| 2 | environment.yml (pinned) | 50-74% |
| 3 | Docker/Singularity | 75-89% |
| 4 | Container + CI + DOI | 90-100% |

**Data Repository Selection:**
| Data Type | Primary Repository |
|-----------|-------------------|
| Raw sequencing | SRA (NCBI) |
| Processed expression | GEO |
| Proteomics | PRIDE |
| General/Other | Zenodo |
| Code | GitHub + Zenodo |

**When to Use:**
- Setting up new project structure
- Writing Data Availability statements
- Creating environment specifications
- Preparing code for publication

**Reference Documents:**
- `references/fair_principles.md` - FAIR implementation
- `references/conda_environments.md` - Environment setup
- `references/data_repositories.md` - Repository selection

---

#### code-documentation

**Docstrings, READMEs, and notebook best practices.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | Documentation for scientific code |
| **Coverage** | Docstrings (Python/R), READMEs, notebooks |

**What It Does:**
Generates clear, consistent documentation for scientific code at all levels—from function docstrings to project READMEs.

**Documentation Hierarchy:**
| Level | When | Content |
|-------|------|---------|
| Inline comments | Complex logic | Explains "why" |
| Docstrings | Every public function | Purpose, params, returns, examples |
| README | Every project | Purpose, installation, usage |
| Notebooks | Workflows, tutorials | Narrative with code |
| API docs | Packages | Auto-generated from docstrings |

**Docstring Styles:**
| Context | Style |
|---------|-------|
| Scientific Python | NumPy style |
| General Python | Google style |
| R packages | roxygen2 |

**README Templates:**
| Project Type | Required Sections |
|--------------|-------------------|
| Analysis | Title, Data, Environment, Usage, Output, Citation |
| Software | Title, Description, Install, Quick Start, Docs, License |
| Data Repo | Title, Description, Data Dictionary, Methods, Terms |

**Validation:**
```bash
# Python docstrings
python scripts/validate_documentation.py module.py --style numpy

# README completeness
python scripts/validate_documentation.py --readme README.md
```

**When to Use:**
- Creating project READMEs
- Writing function docstrings
- Documenting notebooks for sharing

**Reference Documents:**
- `references/docstring_patterns.md` - Style examples
- `references/readme_templates.md` - README patterns

---

### Conversion

Two skills for converting between document formats.

---

#### markitdown

**File to Markdown conversion using Microsoft's MarkItDown.**

| Attribute | Value |
|-----------|-------|
| **Version** | 2.0.0 |
| **Purpose** | Convert files to LLM-friendly Markdown |
| **Formats** | PDF, DOCX, PPTX, XLSX, images (OCR), audio, HTML |

**What It Does:**
Converts various file formats to clean, structured Markdown using Microsoft's MarkItDown tool. Produces token-efficient output well-understood by LLMs.

**Supported Formats:**
| Input | Method | Notes |
|-------|--------|-------|
| PDF (text) | Basic | Good extraction |
| PDF (complex) | Azure DocIntel | Excellent for layouts |
| DOCX | Basic | Tables preserved |
| PPTX | Basic/LLM-enhanced | Optional image descriptions |
| XLSX | Basic | Markdown tables |
| Images | OCR | Requires tesseract |
| Audio | Transcription | WAV/MP3 |
| HTML | Basic | Clean conversion |

**Installation:**
```bash
pip install 'markitdown[all]'  # Full installation
```

**Workflow:**
1. **Assessment** → Identify file type and complexity
2. **Setup** → Ensure dependencies installed
3. **Conversion** → Execute via CLI or Python API
4. **Validation** → Check output quality
5. **Integration** → Add metadata, organize

**When to Use:**
- Converting documents for LLM processing
- Extracting text from PDFs
- Batch converting multiple files
- Preparing documents for literature review

**When NOT to Use:**
- Markdown to other formats → `paper-2-web`, `document-skills`
- PDF form filling → specialized tools

---

#### paper-2-web

**Academic paper transformation to web, video, and poster formats.**

| Attribute | Value |
|-----------|-------|
| **Version** | 2.1.0 |
| **Purpose** | Transform papers into promotional materials |
| **Outputs** | Interactive websites, videos, posters |

**What It Does:**
Transforms academic papers (LaTeX or PDF) into promotional formats using the Paper2All pipeline:
- **Paper2Web** - Interactive academic homepages
- **Paper2Video** - Presentation videos with narration
- **Paper2Poster** - Print-ready conference posters

**Output Selection:**
| Need | Format | Time | Cost |
|------|--------|------|------|
| Permanent online presence | Paper2Web | 15-30 min | $0.50-2.00 |
| Poster session | Paper2Poster | 10-20 min | $0.30-1.00 |
| Video abstract | Paper2Video | 20-60 min | $1.00-3.00 |
| Complete package | All three | 45-90 min | $2.00-6.00 |

**Workflow:**
1. **Input Preparation** → Verify LaTeX/PDF source
2. **Environment Setup** → Install Paper2All pipeline
3. **Content Generation** → Run selected components
4. **Quality Validation** → Test outputs
5. **Deployment** → Deploy to target platforms

**When to Use:**
- Creating conference materials
- Promoting published papers
- Generating video abstracts
- Building research homepages

**When NOT to Use:**
- Manual slide creation → `scientific-slides`
- Writing the paper → `scientific-writing`
- File conversion to Markdown → `markitdown`

**Reference Documents:**
- `references/installation.md` - Setup guide
- `references/paper2web.md` - Website generation
- `references/paper2video.md` - Video generation

---

### Brand

One skill for organizational brand application.

---

#### oligon-brand

**Oligon Scientific Brand implementation.**

| Attribute | Value |
|-----------|-------|
| **Version** | 1.x |
| **Purpose** | Organizational brand colors, typography, styling |
| **Adapters** | matplotlib, ggplot2, pptx, docx, reportlab |

**What It Does:**
Applies Oligon Scientific Brand styling to visual outputs. Provides adapter implementations for common output formats.

**Brand Colors:**
| Element | Color | HEX |
|---------|-------|-----|
| Primary accent | Brand Blue | `#2DB2E8` |
| Secondary accent | Orange | `#E8622D` |
| Primary text | Dark Gray | `#222222` |
| Secondary text | Medium Gray | `#666666` |
| Background | White | `#FFFFFF` |

**Available Adapters:**
| Adapter | Format | Usage |
|---------|--------|-------|
| matplotlib_adapter | Python plots | `apply_brand_style(fig)` |
| ggplot2_adapter | R plots | `theme_oligon()` |
| pptx_adapter | PowerPoint | Template application |
| docx_adapter | Word | Document styling |
| reportlab_adapter | PDF | PDF generation |

**Default Behavior:**
All visual outputs use Oligon brand styling by default. To disable:
- Add "No brand styling" to prompt
- Add override to project `CLAUDE.md`

**Reference Documents:**
- `references/brand-colors-full.md` - Complete color guide
- `tokens/brand-tokens.json` - Machine-readable tokens
- Adapter implementations in skill directory

---

## Integration Matrix

Shows how skills connect and feed into each other:

### Input/Output Relationships

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                    RESEARCH PHASE                           │
                    ├─────────────────────────────────────────────────────────────┤
                    │  paper-search ──────► literature-review                     │
                    │       │                      │                              │
                    │       ▼                      ▼                              │
                    │  citation-management ◄──────┴─► hypothesis-generation      │
                    └──────────────────────┬──────────────────────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────────────────────┐
                    │                    WRITING PHASE                            │
                    ├─────────────────────────────────────────────────────────────┤
                    │  scientific-writing                                         │
                    │       │                                                     │
                    │       ├─► statistical-analysis                              │
                    │       │                                                     │
                    │       ├─► plotting-libraries ────► figures                  │
                    │       │                                                     │
                    │       └─► scientific-schematics ─► diagrams                 │
                    └──────────────────────┬──────────────────────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────────────────────┐
                    │                   FORMATTING PHASE                          │
                    ├─────────────────────────────────────────────────────────────┤
                    │  venue-templates ◄─── scientific-writing                    │
                    │       │                                                     │
                    │       ├─► document-skills:docx                              │
                    │       │                                                     │
                    │       └─► markdown-to-pdf                                   │
                    └──────────────────────┬──────────────────────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────────────────────┐
                    │                 DISSEMINATION PHASE                         │
                    ├─────────────────────────────────────────────────────────────┤
                    │  paper-2-web ────────► website, video, poster               │
                    │                                                             │
                    │  scientific-slides ──► conference presentations             │
                    │                                                             │
                    │  research-posters ───► poster sessions                      │
                    │                                                             │
                    │  executive-summary ──► stakeholder communications           │
                    └─────────────────────────────────────────────────────────────┘
```

### Skill Dependencies

| Skill | Depends On | Feeds Into |
|-------|------------|------------|
| literature-review | paper-search | scientific-writing, hypothesis-generation |
| scientific-writing | statistical-analysis, plotting-libraries, scientific-schematics | venue-templates |
| venue-templates | scientific-writing | document-skills, markdown-to-pdf |
| scientific-slides | paper-search, scientific-schematics | document-skills:pptx |
| research-posters | scientific-schematics | - |
| hypothesis-generation | paper-search | scientific-writing |
| paper-2-web | scientific-writing | - |
| plotting-libraries | visual-design | scientific-writing, scientific-slides |
| scientific-schematics | visual-design | scientific-writing, scientific-slides, research-posters |
| generate-image | visual-design | scientific-slides, research-posters |
| markdown-to-pdf | oligon-brand | - |

---

## Common Workflows

### Research Paper Workflow (11 steps)

```
1. paper-search          → Find relevant literature (8-15 papers)
2. literature-review     → Systematic review if needed
3. citation-management   → Organize references
4. hypothesis-generation → Develop research hypotheses
5. statistical-analysis  → Plan/execute analysis
6. plotting-libraries    → Generate data figures
7. scientific-schematics → Create diagrams
8. scientific-writing    → Draft manuscript
9. peer-review           → Self-evaluate quality
10. venue-templates      → Apply journal formatting
11. document-skills:docx → Export for submission
```

### Conference Poster Workflow (5 steps)

```
1. scientific-schematics → Generate 2-3 figures
2. plotting-libraries    → Create data visualizations
3. research-posters      → Build poster layout
4. oligon-brand          → Apply brand styling
5. Export                → PDF for printing
```

### Conference Presentation Workflow (4 steps)

```
1. paper-search          → Gather citations
2. scientific-schematics → Create slide figures
3. scientific-slides     → Build presentation
4. document-skills:pptx  → Export if needed
```

### Paper Promotion Workflow (3 steps)

```
1. markitdown            → Convert paper to Markdown
2. research-paper-summarizer → Generate summary
3. paper-2-web           → Create website/video/poster
```

---

## Quality Standards

### Shared Thresholds (QUANTIFICATION_THRESHOLDS.md)

| Section | Metric | Minimum | Target |
|---------|--------|---------|--------|
| §1 Literature | Search saturation | <5% new | <2% new |
| §1 Literature | Papers retrieved | 40 | 70+ |
| §2 Visual | DPI for print | 150 | 300 |
| §2 Visual | Contrast ratio | 4.5:1 | 7:1 |
| §3 Sample Size | In vitro replicates | 3 bio | 3 bio + 3 tech |
| §7 Quality Score | Acceptable | 5/10 | 7/10 |
| §7 Quality Score | Excellent | 8/10 | 9/10 |
| §8 Iteration | Hard limit | 5 | - |

### Iteration Stopping Rules

Stop refinement when ANY condition is met:
1. Quality score ≥8/10 (excellent)
2. Quality score ≥7/10 AND iterations ≥ soft limit
3. Score improvement <0.5 for 2 consecutive iterations (plateau)
4. Iteration count = hard limit (budget exhausted)
5. API error or rate limit encountered

### Documentation Completeness

| Level | Coverage | Required For |
|-------|----------|--------------|
| Minimal | 50% | Draft/internal |
| Standard | 75% | Publication-ready |
| Comprehensive | 90% | Archival/reproducibility |

---

## Appendix: Skill Quick Reference

| Skill | Purpose | Key Command/Script |
|-------|---------|-------------------|
| visual-design | Design foundation | (extends other skills) |
| plotting-libraries | Data plots | Python/R patterns |
| scientific-schematics | Diagrams | `generate_schematic_ai.py` |
| generate-image | AI images | `generate_image.py` |
| scientific-writing | Research papers | IMRAD templates |
| executive-summary | Stakeholder summaries | `validate_summary.py` |
| scientific-slides | Presentations | `generate_slide_image.py` |
| research-posters | Conference posters | LaTeX/PPTX templates |
| venue-templates | Journal formatting | Template library |
| hypothesis-generation | Hypothesis formulation | LaTeX template |
| markdown-to-pdf | Branded PDFs | `/doc-to-pdf` |
| document-skills | Marketplace adapter | `document-skills:*` |
| paper-search | Literature search | `search.py` |
| literature-review | Systematic reviews | PRISMA workflow |
| citation-management | Reference management | `doi_to_bibtex.py` |
| peer-review | Manuscript evaluation | ScholarEval rubric |
| research-paper-summarizer | Paper summaries | 4 subagents |
| statistical-analysis | Statistics | Test decision trees |
| reproducible-research | FAIR practices | Environment templates |
| code-documentation | Code docs | `validate_documentation.py` |
| markitdown | File conversion | `markitdown` CLI |
| paper-2-web | Paper promotion | Paper2All pipeline |
| oligon-brand | Brand styling | Adapter library |

---

*This documentation is auto-generated from SKILL.md files across the skills directory. For the most current information, consult individual skill documentation.*
