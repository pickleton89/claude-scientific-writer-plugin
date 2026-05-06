---
name: skill-router
description: Decision trees for selecting the correct skill when multiple options apply. Consult when task scope is ambiguous or spans multiple scientific writing domains.
when_to_use: When a user request could be handled by 2+ skills, when unclear which skill is primary vs. supporting, or when planning multi-skill workflows.
version: 2.3.0
---

# Skill Router

> Decision trees and routing logic for selecting the right skill(s) for scientific writing tasks
> Version: 2.3.0 | Updated: 2026-03-26

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
│  └─ NO → Is it a DIAGRAM or SCHEMATIC with specific layout?
│          │
│          ├─ YES (user specifies type/nodes/layout) → scientific-schematics
│          │         │
│          │         ├─ Workflow/process → Flowchart
│          │         ├─ Biological pathway → Pathway diagram
│          │         ├─ Molecular structure → Structure schematic
│          │         ├─ Experimental setup → Methods diagram
│          │         ├─ Conceptual model → Concept map
│          │         ├─ Mechanism → Mechanism diagram
│          │         │
│          │         └─ NOTE: Tiered generation (see SKILL.md)
│          │            ├─ Tier 1 (Mermaid): Free, instant, <10 nodes
│          │            └─ Tier 2 (AI): Publication quality, complex
│          │
│          └─ NO → Is it TEXT to be visualized?
│                   (graphical abstract, visual summary, methodology overview)
│                   │
│                   ├─ YES → paperbanana
│                   │         │
│                   │         ├─ Graphical abstract from paper text
│                   │         ├─ Visual executive summary
│                   │         ├─ Methodology overview figure
│                   │         ├─ "Explain this visually"
│                   │         └─ Workflow from prose description
│                   │
│                   └─ NO → Is it PHOTOREALISTIC or AI-GENERATED imagery?
│                            │
│                            ├─ YES → generate-image
│                            │         │
│                            │         ├─ Scientific illustration → Claude/DALL-E
│                            │         ├─ Artistic/creative → Image generation models
│                            │         └─ Photo-style → Photorealistic models
│                            │
│                            └─ NO → visual-design (general guidance)
│                                     │
│                                     └─ Provides: color theory, typography,
│                                        layout principles, accessibility
```

### Figure Creation: Quick Selection

| Task | Primary Skill | Supporting Skill |
|------|---------------|------------------|
| Bar chart, scatter plot, histogram | plotting-libraries | visual-design |
| Heatmap, volcano plot, PCA | plotting-libraries | visual-design |
| Flowchart, pathway diagram | scientific-schematics | visual-design |
| Molecular mechanism | scientific-schematics | generate-image |
| Graphical abstract from paper text | paperbanana | visual-design |
| Visual executive summary | paperbanana | executive-summary |
| Methodology overview figure | paperbanana | visual-design |
| "Explain this visually" | paperbanana | visual-design |
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
│  │               │  └─ docx_adapter → document-skills:docx
│  │               │
│  │               ├─ PDF report?
│  │               │  └─ reportlab_adapter → markdown-to-pdf
│  │               │
│  │               └─ Research poster?
│  │                  └─ (manual colors) → research-posters
│  │
│  └─ Other/None?
│     └─ Use visual-design defaults (no brand skill needed)
```

### Brand Application: Quick Selection

| Output | Brand Skill | Implementation Skill |
|--------|-------------|---------------------|
| Publication figure (Python) | oligon-brand | plotting-libraries |
| Publication figure (R) | oligon-brand | plotting-libraries |
| Conference poster | oligon-brand | research-posters |
| Presentation slides | oligon-brand | scientific-slides |
| Word document | oligon-brand | document-skills:docx |
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
│  │         │  └─ YES → deep-research (lit-review or systematic-review mode)
│  │         │
│  │         ├─ Need to generate hypotheses?
│  │         │  └─ YES → deep-research (hypothesis mode)
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
│                   ├─ YES → research-posters
│                   │         │
│                   │         ├─ Complex equations / version control?
│                   │         │  └─ LaTeX format (beamerposter/tikzposter/baposter)
│                   │         │
│                   │         ├─ Quick turnaround / collaboration?
│                   │         │  └─ PowerPoint format
│                   │         │
│                   │         └─ Skill handles format selection
│                   │
│                   └─ NO → Is it a LITERATURE REVIEW?
│                            │
│                            ├─ YES → deep-research (lit-review mode)
│                            │
│                            └─ NO → See "Other Documents" below
```

### Poster Format Selection

The `research-posters` skill handles format selection internally. Use the following criteria:

| Criterion | LaTeX Format | PowerPoint Format |
|-----------|--------------|-------------------|
| Complex equations | ✅ Preferred | ⚠️ Possible but harder |
| Precise typography | ✅ Better control | ⚠️ Limited |
| Quick iteration | ⚠️ Slower | ✅ Faster |
| Non-LaTeX user | ⚠️ Learning curve | ✅ Familiar |
| Template available | Check venue (.tex) | Check venue (.pptx) |
| Collaboration | ⚠️ Requires LaTeX | ✅ Easy sharing |
| Version control | ✅ Git-friendly | ⚠️ Binary format |

**Decision rule:** Use LaTeX if equations OR precise layout OR version control required; otherwise use PowerPoint.

### Other Document Types

| Document Type | Primary Skill | Notes |
|---------------|---------------|-------|
| Literature review paper | deep-research (lit-review) → scientific-writing | Systematic then write |
| Methods paper | scientific-writing + reproducible-research | Emphasize reproducibility |
| Data paper | scientific-writing + code-documentation | Focus on data description |
| Review article | deep-research (lit-review) → scientific-writing | Narrative synthesis |
| Grant proposal | scientific-writing | Adapt for proposal format |
| Executive summary | executive-summary | Pyramid Principle, action-oriented |
| Board/stakeholder summary | executive-summary + visual-design | Include visual summary |
| Thesis chapter | scientific-writing + venue-templates | Institution-specific |

---

## Decision Tree: Research Workflow

```
User needs research/information support
│
├─ Need to GENERATE or EXPLORE ideas (stuck, design space, contradiction)?
│  │
│  └─ YES → scientific-brainstorming
│            │
│            ├─ Stuck / no new ideas?       → Provocation, Random Input
│            ├─ Improving an existing method? → SCAMPER (or TRIZ if contradiction)
│            ├─ Exploring a design space?   → Morphological Analysis, Biomimicry
│            ├─ Multi-perspective decision? → Six Thinking Hats
│            ├─ Question fundamental assumptions? → Reverse Assumptions
│            ├─ Long-term roadmap?          → Future Backwards
│            └─ "Improving X worsens Y"?    → TRIZ (see shared/references/triz_contradictions.md)
│            │
│            → After Stage 3 synthesis, hand off prioritized directions
│              to deep-research Phase 1 SCOPING
│
├─ Need to FIND or REVIEW literature?
│  │
│  └─ YES → deep-research
│            │
│            ├─ Quick search (1-20 papers)?
│            │  └─ quick mode → Brief report (500-1500 words)
│            │
│            ├─ Systematic literature search (50+ papers)?
│            │  └─ lit-review or systematic-review mode
│            │     ├─ T1-T4 evidence grading + full-text verification
│            │     ├─ PRISMA 2020 compliance (systematic-review mode)
│            │     └─ Then → citation-management (for references)
│            │
│            ├─ Fact-check a specific claim?
│            │  └─ fact-check mode → Verification report
│            │
│            ├─ Generate hypotheses?
│            │  └─ hypothesis mode → 3-5 competing hypotheses with quality rubric
│            │
│            ├─ Guided research inquiry?
│            │  └─ socratic mode → 5-layer convergence dialogue
│            │
│            └─ Full research report?
│               └─ full mode → Complete report (3000-8000 words)
│
├─ Need to MANAGE citations?
│  │
│  └─ YES → citation-management
│            │
│            ├─ BibTeX formatting
│            ├─ Style selection (APA, Nature, etc.)
│            └─ Validation and deduplication
│
├─ Need to EVALUATE a paper?
│  │
│  └─ YES → peer-review
│            │
│            ├─ Need detailed revision guidance?
│            │  └─ Full Review mode (default)
│            │
│            ├─ Need quick quality score (8 dimensions)?
│            │  └─ Scoring Only mode
│            │
│            ├─ Need both scoring + detailed review?
│            │  └─ Review + Scoring mode
│            │
│            └─ Need citation reception check for references?
│               └─ Reference Reception Check (Scite MCP)
│                  ├─ Scite Index < 0.5 → flag as contested
│                  └─ editorialNotices → flag retractions/corrections
│
├─ Need to ANALYZE arguments or evidence?
│  │
│  └─ YES → peer-review (use Critical Analysis Framework section)
│            │
│            ├─ Bias identification
│            ├─ Evidence quality hierarchy (GRADE)
│            └─ Logical fallacy detection
│
└─ Need to AUDIT an existing document for factual / citation accuracy?
   │
   └─ YES → research-accuracy-verifier
             │
             ├─ Hallucinated / fabricated citations?
             │  └─ Stage 2: Citation existence (DOI/PMID/journal-volume sanity)
             │
             ├─ Real paper, wrong claim attribution?
             │  └─ Stage 3: Claim-citation alignment (PMC fetch + Scite context)
             │
             ├─ Quotes that may not match source?
             │  └─ Stage 5: Exact-string verification (verify_exact_quote.py)
             │
             ├─ Numbers / named entities to sanity-check?
             │  └─ Stage 6: Numerical heuristics + entity-resolution delegate
             │
             └─ Internal consistency (refs ↔ inline cites, acronym drift)?
                └─ Stage 7: reconcile_references.py + scan_acronyms.py
```

### Research Task Routing

| Task | Primary Skill | When to Use |
|------|---------------|-------------|
| "I'm stuck — brainstorm new approaches" | scientific-brainstorming | Method-driven ideation (SCAMPER, Provocation, Random Input) |
| "Improve my assay/protocol systematically" | scientific-brainstorming | SCAMPER operators or Morphological Analysis |
| "Resolve the potency vs. selectivity trade-off" | scientific-brainstorming (TRIZ) | Contradiction resolution via inventive principles |
| "Generate ideas for X using cross-domain inspiration" | scientific-brainstorming (Biomimicry) | Nature-inspired or random-input forced associations |
| "Find papers on X" | deep-research (quick) | Quick to medium search, 1-50 papers |
| "Search PubMed for..." | deep-research (quick) | PubMed MCP primary |
| "Find preprints on..." | deep-research (quick) | bioRxiv MCP primary |
| "Comprehensive literature review" | deep-research (lit-review) | Systematic, 50+ papers with thematic synthesis |
| "Systematic review with PRISMA" | deep-research (systematic-review) | PRISMA 2020 compliant review |
| "Generate hypotheses for..." | deep-research (hypothesis) | 3-5 competing hypotheses with experimental designs |
| "Fact-check this claim" | deep-research (fact-check) | Claim verification report |
| "Guide my research on..." | deep-research (socratic) | 5-layer convergence dialogue |
| "Format my references" | citation-management | BibTeX/citation styling |
| "Is this paper reliable?" | peer-review | Full Review or Review + Scoring mode |
| "Score this paper's quality" | peer-review | Scoring Only mode (8-dimension assessment) |
| "Analyze this argument" | peer-review | Logic/evidence analysis (Critical Analysis Framework) |
| "Check citation sentiment for references" | peer-review | Reference Reception Check (Scite MCP) |
| "Has this finding been supported or contradicted?" | deep-research (fact-check) | Claim verification via Scite citation context |
| "How has this work been received?" | deep-research | Evidence reception assessment via Scite tallies |
| "Fact-check this lit review" | research-accuracy-verifier | Audit existing document for hallucinated citations / wrong claims |
| "Verify the citations in this draft" | research-accuracy-verifier | Citation existence + claim-source alignment audit |
| "Audit this grant for accuracy" | research-accuracy-verifier | Tier-3 audit with severity matrix; deterministic Verdict enum |
| "Did the AI make these references up?" | research-accuracy-verifier | Hallucination check on AI-generated content |
| "Check this draft for hallucinated references" | research-accuracy-verifier | Same — strong document-audit signals |

---

## Decision Tree: Biological & Drug Research

```
User needs biological/drug research data
│
├─ About a GENE, PROTEIN, or TARGET?
│  │
│  ├─ IDs already resolved?
│  │  ├─ Yes → target-intelligence (6-stage dossier)
│  │  └─ No → entity-resolution → target-intelligence
│  │
│  └─ Output: 12-section target dossier
│     ├─ Druggability assessed? → Check Section 9
│     ├─ Drugs identified? → entity-resolution → drug-intelligence
│     └─ Need validation scoring? → target-validation (5-stage, 0-100 scorecard)
│
├─ About a DRUG or COMPOUND?
│  │
│  ├─ IDs already resolved?
│  │  ├─ Yes → drug-intelligence (6-stage dossier)
│  │  └─ No → entity-resolution → drug-intelligence
│  │
│  └─ Output: 10-section drug dossier
│     ├─ Targets identified? → entity-resolution → target-intelligence
│     └─ Need comparative analysis? → target-validation
│
├─ About BOTH target AND drug?
│  │
│  └─ entity-resolution (both) → target-intelligence + drug-intelligence
│     └─ target-validation (comparative analysis)
│
└─ About a DISEASE (target landscape)?
   │
   └─ entity-resolution (disease) → Open Targets disease associations
      └─ For each target: target-intelligence
```

### Biological Research: Quick Selection

| Task | Primary Skill | Prerequisite | Downstream |
|------|---------------|--------------|------------|
| "Tell me about EGFR" | target-intelligence | entity-resolution | drug-intelligence |
| "Profile imatinib" | drug-intelligence | entity-resolution | target-intelligence |
| "BRCA2 druggability" | target-intelligence | entity-resolution | target-validation |
| "Compare drugs for target" | target-validation | entity-resolution + both intel skills | — |
| "What targets for Alzheimer's?" | target-intelligence (multi) | entity-resolution | — |

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
│  └─ YES → deep-research (lit-review or systematic-review mode)
│            └─ Then optionally → research-paper-summarizer (for each key paper)
│
├─ Is it searching for papers to summarize?
│  │
│  └─ YES → deep-research (quick mode, then research-paper-summarizer for each)
│
└─ Is it evaluating paper QUALITY (not summarizing)?
   │
   └─ YES → peer-review
```

### Paper Summarization: Quick Selection

| Task | Primary Skill | Output |
|------|---------------|--------|
| Deep analysis of single paper | research-paper-summarizer | Markdown + optional visual |
| Find papers on topic | deep-research (quick) | Graded bibliography |
| Systematic review of many papers | deep-research (systematic-review) | PRISMA review document |
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
   └─ YES → paper-2-web (atomic entry point)
             │
             ├─ Interactive website from paper? → paper-2-web:web  (Paper2Web)
             ├─ Narrated presentation video? → paper-2-web:video (Paper2Video)
             ├─ Auto-generated poster from paper? → paper-2-web:poster (Paper2Poster)
             │                                       │
             │                                       └─ NOTE: for poster from scratch → research-posters
             └─ Unsure / all three? → paper-2-web (default)
```

---

## Decision Tree: Document Export & Output Formats

```
User has content ready for final document format
│
├─ Need Word document (.docx)?
│  │
│  └─ YES → document-skills:docx
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
│     └─ YES → document-skills:pdf
│              │
│              ├─ Fill PDF forms
│              ├─ Extract text/tables
│              ├─ Merge/split PDFs
│              └─ Metadata handling
│
├─ Need PowerPoint (.pptx)?
│  │
│  ├─ Creating presentation from scratch?
│  │  └─ YES → scientific-slides → document-skills:pptx
│  │            │
│  │            ├─ Plan content with scientific-slides
│  │            └─ Build PPTX with document-skills:pptx
│  │
│  └─ Editing existing presentation?
│     └─ YES → document-skills:pptx
│              │
│              ├─ OOXML manipulation
│              ├─ Template-based creation
│              └─ html2pptx workflow
│
└─ Need Excel (.xlsx)?
   │
   └─ YES → document-skills:xlsx
            │
            ├─ Create spreadsheets with formulas
            ├─ Data analysis and manipulation
            ├─ Chart generation
            └─ Recalculate formulas (recalc.py)
```

### Document Export: Quick Selection

| Content Source | Output Format | Primary Skill | Supporting Skill |
|----------------|---------------|---------------|------------------|
| Manuscript text | Word (.docx) | document-skills:docx | venue-templates |
| Markdown content | Branded PDF | markdown-to-pdf | visual-design |
| Existing PDF | Modified PDF | document-skills:pdf | — |
| Slide plan | PowerPoint | document-skills:pptx | scientific-slides |
| Data/analysis | Excel | document-skills:xlsx | — |

---

## Quick Reference Matrix

### Task → Skill Mapping

| Task Category | Primary Skill | Common Combinations |
|---------------|---------------|---------------------|
| **Writing** | | |
| Write research paper | scientific-writing | + venue-templates, deep-research |
| Write literature review | deep-research (lit-review) | + scientific-writing, citation-management |
| Write executive summary | executive-summary | + visual-design, markdown-to-pdf |
| Generate hypotheses | deep-research (hypothesis) | + statistical-analysis |
| **Presentations** | | |
| Create slides | scientific-slides | + visual-design, plotting-libraries |
| Create research poster | research-posters | + visual-design, scientific-schematics, plotting-libraries |
| **Visuals** | | |
| Data visualization | plotting-libraries | + visual-design |
| Schematic/diagram | scientific-schematics | + visual-design |
| Text-to-visual (graphical abstract, visual summary) | paperbanana | + visual-design |
| AI-generated image | generate-image | + visual-design |
| Design guidance | visual-design | (supporting role) |
| **Brand** | | |
| Apply Oligon brand colors | oligon-brand | + plotting-libraries, document-skills |
| Get brand color hex codes | oligon-brand | — |
| Style matplotlib for brand | oligon-brand | + plotting-libraries |
| **Research** | | |
| Brainstorm / generate research ideas | scientific-brainstorming | → deep-research (scoping) |
| Resolve technical contradiction | scientific-brainstorming (TRIZ) | + target-validation (modality trade-offs) |
| Find papers | deep-research (quick) | + citation-management |
| Systematic review | deep-research (systematic-review) | + citation-management |
| Manage citations | citation-management | — |
| **Paper Analysis** | | |
| Summarize single paper | research-paper-summarizer | + oligon-brand (for visual outputs) |
| Find papers to analyze | deep-research (quick) | + research-paper-summarizer |
| Systematic literature review | deep-research (systematic-review) | + citation-management |
| **Evaluation** | | |
| Review manuscript | peer-review | Full Review mode (includes critical analysis) |
| Score paper quality | peer-review | Scoring Only mode (8-dimension ScholarEval) |
| Comprehensive evaluation | peer-review | Review + Scoring mode |
| Analyze arguments | peer-review | (use Critical Analysis Framework) |
| **Biological Research** | | |
| Target profiling | target-intelligence | entity-resolution → target-intelligence |
| Drug profiling | drug-intelligence | entity-resolution → drug-intelligence |
| Entity disambiguation | entity-resolution | (prerequisite for intel skills) |
| Target-drug validation | target-validation | entity-resolution + both intel skills |
| GO/NO-GO scoring | target-validation | entity-resolution + target-intelligence |
| **Analysis** | | |
| Statistical guidance | statistical-analysis | + reproducible-research |
| Visualize statistical results | statistical-analysis | + plotting-libraries |
| Reproducibility | reproducible-research | + code-documentation |
| Create reproducible analysis | reproducible-research | + code-documentation, statistical-analysis |
| Code documentation | code-documentation | — |
| Document plotting code | code-documentation | + plotting-libraries |
| **Conversion** | | |
| File → Markdown | markitdown | — |
| Paper → Website | paper-2-web:web | — |
| Paper → Video | paper-2-web:video | — |
| Paper → Poster | paper-2-web:poster | + research-posters for scratch design |
| **Document Output** | | |
| Export to Word | document-skills:docx | + venue-templates (for journal styles) |
| Create branded PDF | markdown-to-pdf | + visual-design |
| PDF forms/manipulation | document-skills:pdf | — |
| Create/edit PowerPoint | document-skills:pptx | + scientific-slides |
| Create/edit Excel | document-skills:xlsx | — |

---

## Multi-Skill Workflows

### Workflow 0: Ideation → Research

```
1. scientific-brainstorming   → Pick method via decision tree, run it,
                                 synthesize into 2-3 prioritized directions
2. deep-research (socratic)   → Refine prioritized direction into a precise RQ
                                 (5-layer convergence)
3. deep-research (lit-review  → Evidence gathering + synthesis on the chosen RQ
   or hypothesis)
```

Use when the user is stuck, exploring a design space, or facing a contradiction
*before* a literature review. If the user already has a defined RQ, skip to
`deep-research`.

### Workflow 1: Complete Research Paper

```
1. deep-research (lit-review) → Systematic search & screening
2. citation-management        → Organize references
3. deep-research (hypothesis) → Formulate testable hypotheses
4. statistical-analysis       → Plan analysis approach
5. scientific-writing         → Draft manuscript
6. venue-templates        → Format for target journal
7. plotting-libraries     → Create data figures
8. scientific-schematics  → Create method diagrams
9. visual-design          → Polish all visuals
10. peer-review           → Self-review before submission
11. document-skills:docx  → Export to Word for submission
```

### Workflow 2: Conference Poster

```
1. scientific-writing     → Condense paper to poster content
2. research-posters       → Create poster (LaTeX or PowerPoint format)
3. plotting-libraries     → Create figures
4. scientific-schematics  → Create diagrams
5. visual-design          → Apply design principles
```

### Workflow 3: Literature Review Paper

```
1. deep-research (quick)              → Initial scoping search
2. deep-research (systematic-review)  → Systematic search & PRISMA
3. citation-management                → Organize all references
4. scientific-writing                 → Write review narrative
5. venue-templates                    → Format for target journal
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
   document-skills:pdf    → Advanced PDF manipulation
```

### Workflow 6: Report to Presentation Conversion

```
1. markitdown             → Extract PDF/DOCX to Markdown
2. visual-design          → Load brand specifications
3. scientific-slides      → Plan slide structure
4. document-skills:pptx   → Build PowerPoint file
5. visual-design          → Validate accessibility
```

### Workflow 7: Target Validation Pipeline

```
1. entity-resolution      → Resolve gene/drug/disease identifiers
2. target-intelligence    → Build 12-section target dossier (6 stages)
3. drug-intelligence      → Build 10-section drug dossier (6 stages)
4. target-validation      → Score 0-100 across 5 dimensions, assign T1-T4 tier
5. deep-research (lit-review) → Deep-dive on specific evidence gaps (optional)
6. scientific-writing     → Draft target assessment manuscript (optional)
```

### Workflow 8: Data-Enriched Research Output

```
1. entity-resolution      → Resolve gene/drug/disease identifiers (if not already resolved)
2. target-intelligence     → Build dossier with expression, PPI, pathway data (optional)
   OR drug-intelligence    → Build dossier with pharmacology, ADMET data (optional)
3. OUTPUT SKILL (any of):
   - plotting-libraries    → Biological data visualization (heatmap, network, constraint)
   - scientific-schematics → Data-fed diagrams (pathway, PPI network, domain architecture)
   - peer-review           → Database claim verification for biomedical manuscripts
   - research-paper-summarizer → Entity enrichment callout for biomedical summaries
   - scientific-writing    → Database version tracking in Methods sections
   - statistical-analysis  → Population context for variant/expression analyses
   - deep-research (hypothesis) → Database-grounded hypothesis development
```

**Key principle:** Dossier-first — output skills extract data from upstream dossiers when available, avoiding redundant ToolUniverse queries. Data-enriched requests route to the OUTPUT skill (not to bio research skills), since the output skill controls rendering.

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
    ┌─────────────┐                        ┌──────────────┐    ┌─────────────┐
    │    deep-    │                        │ scientific-  │    │  research-  │
    │  research   │                        │    slides    │    │   posters   │
    │ (8 modes)   │                        └──────┬───────┘    └──────┬──────┘
    └──────┬──────┘                               │                   │
           │                                      │                   │
           ▼                                      │                   │
    ┌─────────────┐                               │                   │
    │  citation-  │                               │                   │
    │ management  │                               │                   │
    └─────────────┘                               ▼                   ▼
                                           ┌─────────────────────────────────┐
                                           │         VISUAL OUTPUT           │
                                           │  plotting-libraries  │ visual-  │
                                           │  scientific-schematics│ design  │
                                           │  generate-image       │         │
                                           │  paperbanana          │         │
                                           └─────────────────────────────────┘
                                                         │
           ┌─────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                     SUPPORTING SKILLS                           │
    │  peer-review      │  statistical-analysis  │  reproducible-     │
    │                                            │  research          │
    │                                            │  code-documentation│
    └─────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                     CONVERSION SKILLS                           │
    │  markitdown (file → markdown)  │  paper-2-web (paper → web)    │
    └─────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────┐
    │                 BIOLOGICAL RESEARCH PIPELINE                    │
    │                                                                 │
    │  entity-resolution ──► target-intelligence ──┐                  │
    │        │                                     ├─► target-        │
    │        └─────────────► drug-intelligence ────┘   validation     │
    │                                                                 │
    │  (upstream: resolve IDs)  (downstream: 0-100 GO/NO-GO score)   │
    └─────────────────────────────────────────────────────────────────┘
```

---

## Ambiguous Scenarios

### "I need to make a figure"

**Clarifying questions:**
1. Is it based on data/numbers? → plotting-libraries
2. Is it a diagram/schematic with specific layout? → scientific-schematics
3. Is it a visual from text (graphical abstract, visual summary)? → paperbanana
4. Is it an illustration/artistic? → generate-image
5. Need design guidance only? → visual-design

### "I need to review something"

**Clarifying questions:**
1. Review a manuscript for peer review? → peer-review (Full Review mode)
2. Quick quality score for a paper? → peer-review (Scoring Only mode)
3. Analyze logical arguments? → peer-review (Critical Analysis Framework)
4. Review literature systematically? → deep-research (lit-review mode)

### "I need to write something"

**Clarifying questions:**
1. Research paper/manuscript? → scientific-writing
2. Literature review? → deep-research (lit-review) + scientific-writing
3. Presentation? → scientific-slides
4. Poster? → research-posters (handles format selection)
5. Hypothesis document? → deep-research (hypothesis mode)

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
| Research/information need | `deep-research` | Quick scoping before deeper work |
| Analysis/statistics | `statistical-analysis` | Covers most quantitative needs |
| Conversion task | `markitdown` | Most common conversion target |
| Biological research | `entity-resolution` | Resolve identifiers first |
| Brand/corporate | `oligon-brand` | Apply brand standards |
| Document output format | `document-skills:docx` | Most common output format |

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

*This router provides deterministic skill selection for the 29-skill scientific writing library (21 top-level + 4 document-skills sub-skills + 4 biological research skills). All 29 skills are registered in `skill_triggers.yaml` v1.5.0 with 169 canonical test cases. `deep-research` consolidates paper-search, literature-review, and hypothesis-generation into a single 8-mode skill. 7 existing skills consume ToolUniverse data feeds via `tool-lookup.yaml` v1.4.0. Scite MCP provides citation sentiment analysis for peer-review (Reference Reception Check) and deep-research (evidence reception assessment). For threshold values and quality criteria, see `QUANTIFICATION_THRESHOLDS.md`.*

---

## Validation Tooling

The skill router includes programmatic validation tools for deterministic routing:

### Directory Structure

```
skills/skill-router/
├── __init__.py           # Package exports
├── route.py              # Deterministic routing module
├── skill_triggers.yaml   # Keyword registry for all 29 skills (v1.5.0)
└── tests/
    ├── __init__.py
    ├── canonical_routes.yaml  # 169 canonical test cases (v1.5.0)
    └── test_routing.py        # Validation script
```

### Usage

```bash
# Run all routing tests
uv run python skills/skill-router/tests/test_routing.py

# Interactive routing mode
uv run python skills/skill-router/route.py --interactive

# Route a single request
uv run python skills/skill-router/route.py "Create a bar chart of my results"

# List all skills
uv run python skills/skill-router/route.py --list-skills
```

### Programmatic API

```python
from skills.skill_router import route_request, RoutingDecision

result = route_request("Create a bar chart of my results")
print(result.primary_skill)      # "plotting-libraries"
print(result.confidence)         # 0.75
print(result.requires_clarification)  # False

# Output formats
print(result.to_xml())           # Structured XML output
print(result.to_dict())          # Dictionary for JSON
```

### Confidence Thresholds

| Threshold | Meaning |
|-----------|---------|
| >= 0.7 | High confidence - route directly |
| 0.5 - 0.7 | Medium confidence - route with clarification flag |
| < 0.5 | Low confidence - requires disambiguation |

See `skill-router/DETERMINISM_AUDIT.md` for implementation details.

### Scoring Algorithm

| Keyword Matches | Base Score |
|-----------------|------------|
| 0               | 0.0        |
| 1               | 0.35       |
| 2               | 0.55       |
| 3               | 0.65       |
| 4+              | 0.65 + 0.05 per additional (capped at 0.80) |

Trigger boost: +0.2 per regex match (configurable via `trigger_boost` in YAML)
Max trigger boost: 0.4 (configurable via `max_trigger_boost` in YAML)
Total score: capped at 1.0

### Tie-Breaking Order

When multiple skills score identically, the router uses a 4-level tiebreaker:

1. **Total score** (higher wins)
2. **Keyword match count** (more matches = more specific to that skill)
3. **Trigger match count** (more regex matches = stronger signal)
4. **Explicit priority** (`priority` field in `skill_triggers.yaml`, default 0)

If all four are equal, YAML insertion order is the final tiebreaker (stable sort).

---

> **Consolidation Notes:**
> - `paper-search`, `literature-review`, and `hypothesis-generation` have been consolidated into `deep-research` (8-mode skill with 7 agents, 6 checkpoints). Use `deep-research` with the appropriate mode: quick, lit-review, systematic-review, hypothesis, fact-check, socratic, review, or full. *(Archived to `skills/_archived/`)*
> - `research-lookup` has been replaced by `deep-research`. *(Originally replaced by paper-search)*
> - `scholar-evaluation` has been merged into `peer-review` as an optional scoring mode. Use `peer-review` with "Scoring Only" or "Review + Scoring" mode for 8-dimension quantitative assessment. *(Archived to `docs/archive/scholar-evaluation/`)*
> - `latex-posters` and `pptx-posters` have been consolidated into `research-posters`. The unified skill handles format selection (LaTeX or PowerPoint) internally. *(Archived to `docs/archive/`)*
