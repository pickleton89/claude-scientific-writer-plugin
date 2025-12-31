---
name: skill-router
description: Decision trees for selecting the correct skill when multiple options apply. Consult when task scope is ambiguous or spans multiple scientific writing domains.
when_to_use: When a user request could be handled by 2+ skills, when unclear which skill is primary vs. supporting, or when planning multi-skill workflows.
version: 1.2.0
---

# Skill Router

> Decision trees and routing logic for selecting the right skill(s) for scientific writing tasks
> Version: 1.2.0 | Updated: 2025-12-30

---

## Overview

Use these decision trees to deterministically route tasks to the appropriate skill(s). Consult this router when:

- Task could be handled by multiple skills
- Unclear which skill is primary vs. supporting
- Planning multi-skill workflows for complex deliverables

---

## Decision Tree: Figure & Visual Creation

```
User wants to create a visual
│
├─ Is it based on DATA (numbers, measurements, statistics)?
│  │
│  ├─ YES → plotting-libraries
│  │         │
│  │         ├─ Python ecosystem?
│  │         │  ├─ Statistical/categorical → seaborn
│  │         │  ├─ Custom/fine control → matplotlib
│  │         │  └─ Interactive → plotly
│  │         │
│  │         ├─ R ecosystem?
│  │         │  ├─ Publication figures → ggplot2
│  │         │  ├─ Genomics/bio data → Bioconductor (ComplexHeatmap, etc.)
│  │         │  └─ Interactive → plotly/shiny
│  │         │
│  │         └─ Then consult → visual-design (for styling guidance)
│  │
│  └─ NO → Is it a DIAGRAM or SCHEMATIC?
│          │
│          ├─ YES → scientific-schematics
│          │         │
│          │         ├─ Workflow/process → Flowchart
│          │         ├─ Biological pathway → Pathway diagram
│          │         ├─ Molecular structure → Structure schematic
│          │         ├─ Experimental setup → Methods diagram
│          │         ├─ Conceptual model → Concept map
│          │         └─ Mechanism → Mechanism diagram
│          │
│          └─ NO → Is it PHOTOREALISTIC or AI-GENERATED imagery?
│                   │
│                   ├─ YES → generate-image
│                   │         │
│                   │         ├─ Scientific illustration → Claude/DALL-E
│                   │         ├─ Artistic/creative → Image generation models
│                   │         └─ Photo-style → Photorealistic models
│                   │
│                   └─ NO → visual-design (general guidance)
│                            │
│                            └─ Provides: color theory, typography,
│                               layout principles, accessibility
```

### Figure Creation: Quick Selection

| Task | Primary Skill | Supporting Skill |
|------|---------------|------------------|
| Bar chart, scatter plot, histogram | plotting-libraries | visual-design |
| Heatmap, volcano plot, PCA | plotting-libraries | visual-design |
| Flowchart, pathway diagram | scientific-schematics | visual-design |
| Molecular mechanism | scientific-schematics | generate-image |
| Conceptual illustration | generate-image | visual-design |
| Infographic elements | visual-design | generate-image |

---

## Decision Tree: Brand Application

```
User needs to apply organizational brand standards
│
├─ Which brand?
│  │
│  ├─ Oligon brand?
│  │  │
│  │  └─ YES → oligon-brand
│  │            │
│  │            ├─ Load brand tokens
│  │            ├─ Select appropriate color cycle
│  │            │
│  │            └─ Which output format? (select adapter)
│  │               │
│  │               ├─ matplotlib/seaborn figure?
│  │               │  └─ matplotlib_adapter → plotting-libraries
│  │               │
│  │               ├─ ggplot2 figure?
│  │               │  └─ ggplot2_adapter → plotting-libraries
│  │               │
│  │               ├─ PowerPoint presentation?
│  │               │  └─ pptx_adapter → scientific-slides
│  │               │
│  │               ├─ Word document?
│  │               │  └─ docx_adapter → document-skills/docx
│  │               │
│  │               ├─ PDF report?
│  │               │  └─ reportlab_adapter → markdown-to-pdf
│  │               │
│  │               └─ LaTeX poster?
│  │                  └─ (manual colors) → latex-posters
│  │
│  └─ Other/None?
│     └─ Use visual-design defaults (no brand skill needed)
```

### Brand Application: Quick Selection

| Output | Brand Skill | Implementation Skill |
|--------|-------------|---------------------|
| Publication figure (Python) | oligon-brand | plotting-libraries |
| Publication figure (R) | oligon-brand | plotting-libraries |
| Conference poster | oligon-brand | latex-posters / pptx-posters |
| Presentation slides | oligon-brand | scientific-slides |
| Word document | oligon-brand | document-skills/docx |
| PDF report | oligon-brand | markdown-to-pdf |

---

## Decision Tree: Document Creation

```
User wants to create a document
│
├─ Is it a RESEARCH PAPER or MANUSCRIPT?
│  │
│  ├─ YES → scientific-writing
│  │         │
│  │         ├─ Need journal-specific formatting?
│  │         │  └─ YES → venue-templates (for style requirements)
│  │         │
│  │         ├─ Need to review existing literature?
│  │         │  └─ YES → literature-review (systematic approach)
│  │         │
│  │         ├─ Need to generate hypotheses?
│  │         │  └─ YES → hypothesis-generation
│  │         │
│  │         └─ Need statistical analysis guidance?
│  │            └─ YES → statistical-analysis
│  │
│  └─ NO → Is it an EXECUTIVE SUMMARY?
│          │
│          ├─ YES → executive-summary
│          │         │
│          │         ├─ From research paper? → Pyramid Principle structure
│          │         ├─ Need visual summary? → + visual-design, plotting-libraries
│          │         └─ PDF output needed? → + markdown-to-pdf
│          │
│          └─ NO → Is it a PRESENTATION?
│          │
│          ├─ YES → scientific-slides
│          │         │
│          │         ├─ Conference talk → 10-15 slides
│          │         ├─ Seminar → 20-30 slides
│          │         ├─ Thesis defense → 30-45 slides
│          │         └─ Lab meeting → 5-10 slides
│          │
│          └─ NO → Is it a POSTER?
│                   │
│                   ├─ YES → Which format?
│                   │         │
│                   │         ├─ Complex equations/LaTeX needed?
│                   │         │  └─ YES → latex-posters
│                   │         │
│                   │         ├─ Quick turnaround / visual focus?
│                   │         │  └─ YES → pptx-posters
│                   │         │
│                   │         └─ Unsure → See decision criteria below
│                   │
│                   └─ NO → Is it a LITERATURE REVIEW?
│                            │
│                            ├─ YES → literature-review
│                            │
│                            └─ NO → See "Other Documents" below
```

### Poster Format Decision

| Criterion | LaTeX (latex-posters) | PowerPoint (pptx-posters) |
|-----------|----------------------|---------------------------|
| Complex equations | ✅ Preferred | ⚠️ Possible but harder |
| Precise typography | ✅ Better control | ⚠️ Limited |
| Quick iteration | ⚠️ Slower | ✅ Faster |
| Non-LaTeX user | ⚠️ Learning curve | ✅ Familiar |
| Template available | Check venue | Check venue |
| Collaboration | ⚠️ Requires LaTeX | ✅ Easy sharing |

**Decision rule:** Use LaTeX if equations OR precise layout required; otherwise use PowerPoint.

### Other Document Types

| Document Type | Primary Skill | Notes |
|---------------|---------------|-------|
| Literature review paper | literature-review → scientific-writing | Systematic then write |
| Methods paper | scientific-writing + reproducible-research | Emphasize reproducibility |
| Data paper | scientific-writing + code-documentation | Focus on data description |
| Review article | literature-review → scientific-writing | Narrative synthesis |
| Grant proposal | scientific-writing | Adapt for proposal format |
| Executive summary | executive-summary | Pyramid Principle, action-oriented |
| Board/stakeholder summary | executive-summary + visual-design | Include visual summary |
| Thesis chapter | scientific-writing + venue-templates | Institution-specific |

---

## Decision Tree: Research Workflow

```
User needs research/information support
│
├─ Need to FIND information or papers?
│  │
│  ├─ Quick fact/concept lookup?
│  │  └─ YES → research-lookup (Perplexity API)
│  │            │
│  │            ├─ Simple query → Sonar Pro
│  │            └─ Complex/reasoning → Sonar Reasoning Pro
│  │
│  └─ Systematic literature search?
│     └─ YES → literature-review
│              │
│              ├─ Database selection by domain
│              ├─ PRISMA-style screening
│              └─ Then → citation-management (for references)
│
├─ Need to MANAGE citations?
│  │
│  └─ YES → citation-management
│            │
│            ├─ BibTeX formatting
│            ├─ Style selection (APA, Nature, etc.)
│            └─ Validation and deduplication
│
├─ Need to EVALUATE a paper or researcher?
│  │
│  ├─ Evaluate paper quality?
│  │  └─ YES → peer-review (manuscript review + critical analysis framework)
│  │
│  └─ Evaluate researcher/scholar?
│     └─ YES → scholar-evaluation (8-dimension assessment)
│
└─ Need to ANALYZE arguments or evidence?
   │
   └─ YES → peer-review (use Critical Analysis Framework section)
             │
             ├─ Bias identification
             ├─ Evidence quality hierarchy (GRADE)
             └─ Logical fallacy detection
```

### Research Task Routing

| Task | Primary Skill | When to Use |
|------|---------------|-------------|
| "Find papers on X" | research-lookup | Quick search, <10 papers |
| "Comprehensive literature review" | literature-review | Systematic, 50+ papers |
| "Format my references" | citation-management | BibTeX/citation styling |
| "Is this paper reliable?" | peer-review | Manuscript evaluation |
| "Evaluate this researcher" | scholar-evaluation | Scholar assessment |
| "Analyze this argument" | peer-review | Logic/evidence analysis (Critical Analysis Framework) |

---

## Decision Tree: Paper Summarization

```
User wants to summarize or analyze a research paper
│
├─ Is it a SINGLE paper needing comprehensive summary?
│  │
│  └─ YES → research-paper-summarizer
│            │
│            ├─ What article type?
│            │  ├─ General research → general_researcher_summarizer
│            │  ├─ Review/meta-analysis → review_article_summarizer
│            │  ├─ Computational/bioinformatics → compbio_bioinformatic_summarizer
│            │  └─ Cell & molecular biology → cellmolbio_summarizer
│            │
│            └─ What output format?
│               ├─ Markdown only → _summary.md
│               ├─ Interactive HTML → html-report
│               ├─ PDF summary → yaml-for-pdf → generate_summary_pdf.py
│               └─ SVG infographic → svg-infographic
│
├─ Is it a COLLECTION of papers for systematic review?
│  │
│  └─ YES → literature-review
│            └─ Then optionally → research-paper-summarizer (for each key paper)
│
├─ Is it a quick lookup for citation/abstract only?
│  │
│  └─ YES → research-lookup
│
└─ Is it evaluating paper QUALITY (not summarizing)?
   │
   └─ YES → peer-review
```

### Paper Summarization: Quick Selection

| Task | Primary Skill | Output |
|------|---------------|--------|
| Deep analysis of single paper | research-paper-summarizer | Markdown + optional visual |
| Quick abstract/citation lookup | research-lookup | Text response |
| Systematic review of many papers | literature-review | Review document |
| Evaluate paper methodology | peer-review | Evaluation report |
| Summarize paper for presentation | research-paper-summarizer → scientific-slides | Slides |

---

## Decision Tree: Analysis & Reproducibility

```
User needs analysis or code support
│
├─ Need STATISTICAL analysis guidance?
│  │
│  └─ YES → statistical-analysis
│            │
│            ├─ Test selection → Decision matrices
│            ├─ Multiple testing → Correction methods
│            ├─ Effect sizes → Interpretation thresholds
│            └─ Power analysis → Sample size calculation
│
├─ Need to ensure REPRODUCIBILITY?
│  │
│  └─ YES → reproducible-research
│            │
│            ├─ Environment specification
│            ├─ FAIR principles
│            ├─ Data/code archiving
│            └─ Seed management
│
└─ Need CODE DOCUMENTATION?
   │
   └─ YES → code-documentation
             │
             ├─ README structure
             ├─ Docstring formats (Python/R/Bash)
             ├─ API documentation
             └─ Style selection (NumPy, Google, etc.)
```

### Analysis Support Routing

| Task | Primary Skill | Supporting Skill |
|------|---------------|------------------|
| "Which test should I use?" | statistical-analysis | — |
| "Visualize my statistical results" | statistical-analysis | plotting-libraries |
| "Make my analysis reproducible" | reproducible-research | code-documentation |
| "Document my code" | code-documentation | plotting-libraries (for figure code) |
| "Archive my data" | reproducible-research | — |
| "Report my statistics" | statistical-analysis | scientific-writing |

### Statistical Visualization Routing

```
Need to visualize statistical results?
│
├─ Assessing data before analysis?
│  │
│  ├─ Normality check → Q-Q plot, histogram
│  ├─ Variance by group → Box plot
│  └─ Outlier detection → Box plot, scatter
│  │
│  └─ Use: plotting-libraries (see statistical_visualization section)
│
├─ Showing group comparisons?
│  │
│  ├─ Two groups → Box + strip plot, violin plot
│  ├─ Multiple groups → Grouped box, significance brackets
│  └─ Paired data → Before-after line plot
│  │
│  └─ Use: statistical-analysis (visualization_guidance) → plotting-libraries
│
├─ Showing relationships?
│  │
│  ├─ Correlation → Scatter + fit line, correlation heatmap
│  ├─ Regression diagnostics → Residual plot, Q-Q of residuals
│  └─ Multiple effects → Forest plot, coefficient plot
│  │
│  └─ Use: statistical-analysis → plotting-libraries
│
└─ High-dimensional results?
   │
   ├─ Differential expression → Volcano plot, MA plot
   ├─ Clustering → Heatmap with dendrograms
   └─ Multiple testing → P-value histogram
   │
   └─ Use: plotting-libraries (bioinformatics section)
```

---

## Decision Tree: Documentation & Work Archiving

```
User needs to document their work
│
├─ What type of documentation?
│  │
│  ├─ CODE documentation?
│  │  │
│  │  └─ YES → code-documentation
│  │            │
│  │            ├─ README structure
│  │            ├─ Function docstrings (NumPy, Google, R)
│  │            ├─ API documentation
│  │            ├─ CLI help documentation
│  │            └─ For visualization code → see plotting-libraries
│  │
│  ├─ METHODS section for paper?
│  │  │
│  │  └─ YES → scientific-writing
│  │            │
│  │            ├─ IMRAD Methods structure
│  │            ├─ Statistical reporting
│  │            └─ + reproducible-research (for environment specs)
│  │
│  ├─ REPRODUCIBILITY documentation?
│  │  │
│  │  └─ YES → reproducible-research
│  │            │
│  │            ├─ Environment specifications
│  │            ├─ FAIR principles compliance
│  │            ├─ Data/code archiving
│  │            ├─ Seed management
│  │            └─ + code-documentation (for code comments)
│  │
│  └─ DATA AVAILABILITY statement?
│     │
│     └─ YES → reproducible-research
│              │
│              ├─ Repository selection (Zenodo, Figshare, etc.)
│              ├─ FAIR metadata
│              └─ Accession numbers / DOIs
│
├─ Need to document ANALYSIS workflow?
│  │
│  └─ YES → Which aspect?
│            │
│            ├─ Statistical methods used?
│            │  └─ statistical-analysis → scientific-writing (Methods)
│            │
│            ├─ Visualization code?
│            │  └─ code-documentation + plotting-libraries
│            │
│            └─ Full pipeline?
│               └─ reproducible-research (workflow managers, containers)
│
└─ Need CRITICAL ANALYSIS documentation?
   │
   └─ YES → peer-review (Critical Analysis Framework section)
            │
            ├─ Evidence quality assessment
            ├─ Bias identification
            ├─ Logical reasoning evaluation
            └─ GRADE evidence hierarchy
```

### Documentation Task Routing

| Documentation Need | Primary Skill | Supporting Skill |
|--------------------|---------------|------------------|
| README for code repository | code-documentation | — |
| Function/API docs | code-documentation | — |
| Methods section | scientific-writing | reproducible-research |
| Data availability statement | reproducible-research | — |
| Environment specification | reproducible-research | code-documentation |
| Analysis workflow | reproducible-research | code-documentation, statistical-analysis |
| Critical analysis notes | peer-review | — |
| Visualization code docs | code-documentation | plotting-libraries |

---

## Decision Tree: Conversion & Transformation

```
User needs to convert or transform content
│
├─ Convert FILE to Markdown?
│  │
│  └─ YES → markitdown
│            │
│            ├─ PDF → Markdown (OCR if needed)
│            ├─ DOCX/PPTX/XLSX → Markdown
│            ├─ Images → Markdown (with descriptions)
│            └─ Audio → Markdown (transcription)
│
└─ Convert PAPER to web/media format?
   │
   └─ YES → paper-2-web
             │
             ├─ Interactive website
             ├─ Visual poster summary
             └─ Video abstract
```

---

## Decision Tree: Document Export & Output Formats

```
User has content ready for final document format
│
├─ Need Word document (.docx)?
│  │
│  └─ YES → document-skills/docx
│            │
│            ├─ From scientific-writing content
│            │  └─ Export manuscript to Word format
│            │
│            ├─ With venue-templates formatting
│            │  └─ Apply journal-specific styles
│            │
│            ├─ Need tracked changes/redlining?
│            │  └─ Use OOXML redline workflow
│            │
│            └─ Edit existing DOCX?
│               └─ Raw XML or docx-js manipulation
│
├─ Need PDF output?
│  │
│  ├─ Branded/templated PDF from Markdown?
│  │  └─ YES → markdown-to-pdf
│  │            └─ Uses Oligon templates & brand colors
│  │
│  └─ PDF manipulation (forms, merge, extract)?
│     └─ YES → document-skills/pdf
│              │
│              ├─ Fill PDF forms
│              ├─ Extract text/tables
│              ├─ Merge/split PDFs
│              └─ Metadata handling
│
├─ Need PowerPoint (.pptx)?
│  │
│  ├─ Creating presentation from scratch?
│  │  └─ YES → scientific-slides → document-skills/pptx
│  │            │
│  │            ├─ Plan content with scientific-slides
│  │            └─ Build PPTX with document-skills/pptx
│  │
│  └─ Editing existing presentation?
│     └─ YES → document-skills/pptx
│              │
│              ├─ OOXML manipulation
│              ├─ Template-based creation
│              └─ html2pptx workflow
│
└─ Need Excel (.xlsx)?
   │
   └─ YES → document-skills/xlsx
            │
            ├─ Create spreadsheets with formulas
            ├─ Data analysis and manipulation
            ├─ Chart generation
            └─ Recalculate formulas (recalc.py)
```

### Document Export: Quick Selection

| Content Source | Output Format | Primary Skill | Supporting Skill |
|----------------|---------------|---------------|------------------|
| Manuscript text | Word (.docx) | document-skills/docx | venue-templates |
| Markdown content | Branded PDF | markdown-to-pdf | visual-design |
| Existing PDF | Modified PDF | document-skills/pdf | — |
| Slide plan | PowerPoint | document-skills/pptx | scientific-slides |
| Data/analysis | Excel | document-skills/xlsx | — |

---

## Quick Reference Matrix

### Task → Skill Mapping

| Task Category | Primary Skill | Common Combinations |
|---------------|---------------|---------------------|
| **Writing** | | |
| Write research paper | scientific-writing | + venue-templates, literature-review |
| Write literature review | literature-review | + scientific-writing, citation-management |
| Write executive summary | executive-summary | + visual-design, markdown-to-pdf |
| Generate hypotheses | hypothesis-generation | + literature-review, statistical-analysis |
| **Presentations** | | |
| Create slides | scientific-slides | + visual-design, plotting-libraries |
| Create LaTeX poster | latex-posters | + visual-design, scientific-schematics |
| Create PowerPoint poster | pptx-posters | + visual-design, plotting-libraries |
| **Visuals** | | |
| Data visualization | plotting-libraries | + visual-design |
| Schematic/diagram | scientific-schematics | + visual-design |
| AI-generated image | generate-image | + visual-design |
| Design guidance | visual-design | (supporting role) |
| **Brand** | | |
| Apply Oligon brand colors | oligon-brand | + plotting-libraries, document-skills |
| Get brand color hex codes | oligon-brand | — |
| Style matplotlib for brand | oligon-brand | + plotting-libraries |
| **Research** | | |
| Quick lookup | research-lookup | — |
| Systematic review | literature-review | + citation-management |
| Manage citations | citation-management | — |
| **Paper Analysis** | | |
| Summarize single paper | research-paper-summarizer | + oligon-brand (for visual outputs) |
| Quick paper lookup | research-lookup | — |
| Systematic literature review | literature-review | + citation-management |
| **Evaluation** | | |
| Review manuscript | peer-review | (includes critical analysis) |
| Evaluate scholar | scholar-evaluation | — |
| Analyze arguments | peer-review | (use Critical Analysis Framework) |
| **Analysis** | | |
| Statistical guidance | statistical-analysis | + reproducible-research |
| Visualize statistical results | statistical-analysis | + plotting-libraries |
| Reproducibility | reproducible-research | + code-documentation |
| Create reproducible analysis | reproducible-research | + code-documentation, statistical-analysis |
| Code documentation | code-documentation | — |
| Document plotting code | code-documentation | + plotting-libraries |
| **Conversion** | | |
| File → Markdown | markitdown | — |
| Paper → Web/Media | paper-2-web | — |
| **Document Output** | | |
| Export to Word | document-skills/docx | + venue-templates (for journal styles) |
| Create branded PDF | markdown-to-pdf | + visual-design |
| PDF forms/manipulation | document-skills/pdf | — |
| Create/edit PowerPoint | document-skills/pptx | + scientific-slides |
| Create/edit Excel | document-skills/xlsx | — |

---

## Multi-Skill Workflows

### Workflow 1: Complete Research Paper

```
1. literature-review      → Systematic search & screening
2. citation-management    → Organize references
3. hypothesis-generation  → Formulate testable hypotheses
4. statistical-analysis   → Plan analysis approach
5. scientific-writing     → Draft manuscript
6. venue-templates        → Format for target journal
7. plotting-libraries     → Create data figures
8. scientific-schematics  → Create method diagrams
9. visual-design          → Polish all visuals
10. peer-review           → Self-review before submission
11. document-skills/docx  → Export to Word for submission
```

### Workflow 2: Conference Poster

```
1. scientific-writing     → Condense paper to poster content
2. pptx-posters OR latex-posters → Create poster structure
3. plotting-libraries     → Create figures
4. scientific-schematics  → Create diagrams
5. visual-design          → Apply design principles
```

### Workflow 3: Literature Review Paper

```
1. research-lookup        → Initial scoping search
2. literature-review      → Systematic search & PRISMA
3. citation-management    → Organize all references
4. scientific-writing     → Write review narrative
5. venue-templates        → Format for target journal
```

### Workflow 4: Reproducible Analysis Pipeline

```
1. statistical-analysis   → Select appropriate methods
2. code-documentation     → Document code thoroughly
3. reproducible-research  → Ensure FAIR compliance
4. plotting-libraries     → Create reproducible figures
```

### Workflow 5: PDF Report from Markdown

```
1. scientific-writing     → Draft content in Markdown
2. visual-design          → Establish design specifications
3. plotting-libraries     → Create data figures
4. markdown-to-pdf        → Apply branded template
   OR
   document-skills/pdf    → Advanced PDF manipulation
```

### Workflow 6: Report to Presentation Conversion

```
1. markitdown             → Extract PDF/DOCX to Markdown
2. visual-design          → Load brand specifications
3. scientific-slides      → Plan slide structure
4. document-skills/pptx   → Build PowerPoint file
5. visual-design          → Validate accessibility
```

---

## Skill Relationships Diagram

```
                    ┌─────────────────────────────────────────┐
                    │           DOCUMENT OUTPUT               │
                    │  scientific-writing  │  venue-templates │
                    └──────────┬───────────┴────────┬─────────┘
                               │                    │
           ┌───────────────────┼────────────────────┼───────────────────┐
           │                   │                    │                   │
           ▼                   ▼                    ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
    │ literature- │    │ hypothesis- │    │ scientific-  │    │ latex-/pptx-│
    │   review    │    │ generation  │    │    slides    │    │   posters   │
    └──────┬──────┘    └──────┬──────┘    └──────┬───────┘    └──────┬──────┘
           │                  │                   │                   │
           ▼                  │                   │                   │
    ┌─────────────┐           │                   │                   │
    │  citation-  │◄──────────┘                   │                   │
    │ management  │                               │                   │
    └─────────────┘                               ▼                   ▼
                                           ┌─────────────────────────────────┐
                                           │         VISUAL OUTPUT           │
                                           │  plotting-libraries  │ visual-  │
                                           │  scientific-schematics│ design  │
                                           │  generate-image       │         │
                                           └─────────────────────────────────┘
                                                         │
           ┌─────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                     SUPPORTING SKILLS                           │
    │  research-lookup  │  statistical-analysis  │  reproducible-     │
    │  peer-review      │  scholar-evaluation    │  research          │
    │                                            │  code-documentation│
    └─────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                     CONVERSION SKILLS                           │
    │  markitdown (file → markdown)  │  paper-2-web (paper → web)    │
    └─────────────────────────────────────────────────────────────────┘
```

---

## Ambiguous Scenarios

### "I need to make a figure"

**Clarifying questions:**
1. Is it based on data/numbers? → plotting-libraries
2. Is it a diagram/schematic? → scientific-schematics
3. Is it an illustration/artistic? → generate-image
4. Need design guidance only? → visual-design

### "I need to review something"

**Clarifying questions:**
1. Review a manuscript for peer review? → peer-review
2. Evaluate a researcher's work? → scholar-evaluation
3. Analyze logical arguments? → peer-review (Critical Analysis Framework)
4. Review literature systematically? → literature-review

### "I need to write something"

**Clarifying questions:**
1. Research paper/manuscript? → scientific-writing
2. Literature review? → literature-review + scientific-writing
3. Presentation? → scientific-slides
4. Poster? → latex-posters OR pptx-posters
5. Hypothesis document? → hypothesis-generation

---

## Fallback Routing

When no decision tree clearly matches the user's request:

### Step 1: Clarify Intent
Ask the user to specify:
1. **Output type**: Document, visual, analysis, or research task?
2. **Primary deliverable**: What artifact should result from this work?
3. **Domain**: Does this involve data, diagrams, text, or evaluation?

### Step 2: Default by Category
If clarification isn't possible, use these defaults:

| Task Characteristic | Default Skill | Rationale |
|---------------------|---------------|-----------|
| Text-heavy, unstructured | `scientific-writing` | General manuscript guidance |
| Visual but unclear type | `visual-design` | Design philosophy applies broadly |
| Research/information need | `research-lookup` | Quick scoping before deeper work |
| Analysis/statistics | `statistical-analysis` | Covers most quantitative needs |
| Unknown document format | `venue-templates` | Has format specifications |

### Step 3: Escalate if Needed
If task genuinely doesn't fit existing skills:
1. Acknowledge the gap to the user
2. Identify the closest skill and explain limitations
3. Suggest whether a new skill might be warranted

---

## Cross-References

Each skill's `<cross_references>` section should include:

```markdown
<cross_references>
## Related Skills

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

- [list specific related skills with relationship descriptions]
</cross_references>
```

---

*This router provides deterministic skill selection for the 26-skill scientific writing library (22 top-level + 4 document-skills sub-skills). For threshold values and quality criteria, see `QUANTIFICATION_THRESHOLDS.md`.*
