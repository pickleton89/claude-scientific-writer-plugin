---
name: research-paper-summarizer
version: 1.1.0
description: "Analyze and summarize research papers (PDF, DOI, PubMed, or text) into structured markdown, HTML reports, branded PDFs, or SVG infographics. Extracts statistics, figures, critical analysis, and key findings from scientific publications with full quantitative preservation."
when_to_use: "When user uploads/provides a research paper (PDF, text, abstract, DOI, PubMed ID, or URL) and wants paper analysis, summarization, figure extraction, infographic creation, or visual output generation"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Task]
brand-reference: "../oligon-brand/"
---

# Research Paper Summarizer

<overview>

Create rigorous, quantitative summaries of scientific research papers in multiple output formats while preserving all numerical data, statistical details, and domain terminology.

## Quick Start

### Basic Usage

1. **Provide a PDF**: Upload or specify path to a research paper
2. **Select article type**: General / Review / CompBio / CellMolBio
3. **Get markdown summary**: Saved as `{filename}_summary.md`
4. **Choose visual format**: HTML report, PDF, SVG infographic, or none

### Example Session

```
User: Summarize this paper [uploads smith2024_cancer.pdf]

Claude: This paper has 24 pages. Using Chunked processing mode.
        What type of article is this?
        1. General research paper
        2. Review article
        3. Computational biology
        4. Cell & molecular biology

User: 1

Claude: [Processes paper through 6 specialized agents]
        ✓ Summary complete! Saved to: smith2024_cancer_summary.md

        Which visual format would you like?
        1. Interactive HTML report
        2. PDF summary
        3. SVG infographic
        4. None

User: 1

Claude: ✓ HTML report generated: smith2024_cancer_report.html
```

### What You Get

| Output | Format | Best For |
|--------|--------|----------|
| Markdown summary | `_summary.md` | Reading, editing, version control |
| HTML report | `_report.html` | Presentations, sharing |
| PDF summary | `_summary.pdf` | Printing, archival |
| SVG infographic | `_infographic.svg` | Posters, slides |

### Timing

- **Short papers** (≤12 pages): ~2-3 minutes
- **Long papers** (>12 pages): ~5-8 minutes (chunked processing)
- Visual output generation: ~1-2 minutes per format

</overview>

---

<when_to_use>

## When to Use This Skill

Activate when the user:
- Uploads or pastes a research paper (PDF, text, abstract)
- Provides a DOI, PubMed ID, or paper URL
- Asks to "summarize this paper", "create a summary", or "analyze this research"
- Requests specific outputs: "make an infographic", "create HTML report", "generate PDF summary"

</when_to_use>

---

<decision_framework>

## Processing Modes

This skill automatically selects the best processing approach based on paper length:

| Mode | Paper Length | Approach |
|------|--------------|----------|
| **Standard Mode** | ≤12 pages | Full document analysis using legacy prompts |
| **Chunked Mode** | >12 pages | Section-by-section processing via subagent pipeline |

### Why Two Modes?

- **Standard Mode**: Efficient for shorter papers that fit comfortably in context
- **Chunked Mode**: Handles large papers without context exhaustion by processing sections incrementally and writing to a shared summary file

### Processing Mode Detection

When a PDF is provided:

1. **Read PDF and count pages**
2. **Determine mode**:
   - If pages ≤ 12: Use Standard Mode (legacy prompts)
   - If pages > 12: Use Chunked Mode (subagent pipeline)
3. **Inform user**: "This paper has X pages. Using [Standard/Chunked] processing mode."

## Phase 1: Article Type Selection

**ALWAYS ask the user which type of article they are summarizing:**

| Article Type | Best For | Prompt File |
|--------------|----------|-------------|
| **General Research** | Standard primary research papers | `{baseDir}/prompts/general_researcher_summarizer.md` |
| **Review Article** | Review papers, meta-analyses, systematic reviews | `{baseDir}/prompts/review_article_summarizer.md` |
| **Computational/Bioinformatics** | Genomics, methods, pipelines, algorithms | `{baseDir}/prompts/compbio_bioinformatic_summarizer.md` |
| **Cell & Molecular Biology** | Mechanistic, wet-lab, cancer biology papers | `{baseDir}/prompts/cellmolbio_summarizer.md` |

Ask: "What type of article is this?"
1. General research paper
2. Review article / meta-analysis
3. Computational biology / bioinformatics
4. Cell & molecular biology

</decision_framework>

---

<workflow>

## Workflow Overview

This skill follows a multi-phase workflow with mode-dependent processing:

### Prerequisites (PDF Generation)

Before generating PDF output, ensure dependencies are installed:
```bash
pip install weasyprint pyyaml
```

### Phase 0: Initialization (All Papers)
1. Receive PDF from user
2. Read PDF and count pages
3. Determine processing mode (Standard ≤12 pages, Chunked >12 pages)
4. Inform user of mode selection

### Phase 1: Article Type Selection & Summary Generation

**1a. Ask user to select article type** (both modes)

**1b. Generate summary** (mode-dependent):
- **Standard Mode**: Use legacy full-document prompts
- **Chunked Mode**: Use subagent pipeline (see Chunked Mode Workflow below)

**1c. Save markdown file** to same directory as source document

### Phase 2: Visual Output Generation
- Ask user which visual format(s) they want
- Generate visuals using the saved markdown summary as the source

### Generating the Markdown Summary (Standard Mode)

For papers ≤12 pages, use the standard approach:

1. Read the appropriate summarizer prompt file
2. Apply the framework to analyze the paper comprehensively
3. Generate the markdown summary following the prompt's structure
4. **Save the summary** to the same directory as the source document
   - Filename format: `{original_filename}_summary.md`
   - Example: `smith2024_cancer_cells.pdf` → `smith2024_cancer_cells_summary.md`

5. **Validate the summary** before proceeding:
   - Check for any `<!-- SECTION: xxx PENDING -->` markers (should be none)
   - Verify statistics section contains at least 3 numerical values
   - Confirm figure references match actual figures in PDF

---

## Chunked Mode Workflow (Papers >12 Pages)

For longer papers, use the chunked subagent pipeline to avoid context exhaustion.

### Setup Phase

1. **Detect PDF sections** using `{baseDir}/subagents/overview-agent.md` section detection logic
   - Read first 5-10 pages of PDF
   - Identify page ranges for: Abstract, Introduction, Methods, Results, Discussion, References
   - Output JSON mapping of sections to pages

2. **Create skeleton summary file**
   - Read `{baseDir}/templates/summary-skeleton.md`
   - Read `{baseDir}/templates/skeleton-config.md` for article-type-specific placeholders
   - Fill in metadata: TITLE, TIMESTAMP, FILENAME, PAGE_COUNT, ARTICLE_TYPE
   - Apply article-type-specific customizations
   - Write skeleton to `{original_filename}_summary.md`

### Subagent Dispatch Phase

Process the paper section-by-section using specialized subagents:

| Order | Agent | PDF Sections | Output Sections |
|-------|-------|--------------|-----------------|
| 1 | `overview-agent` | Abstract, Introduction | Executive Summary, Background, Hypothesis |
| 2 | `methods-agent` | Methods section | Experimental Approach |
| 3 | `results-agent` | Results section | Key Findings, Figures, Statistics |
| 4 | `critique-agent` | Discussion | Strengths, Limitations, Red Flags |
| 5 | `context-agent` | Introduction + Discussion | Bigger Picture, Implications |
| 6 | `synthesis-agent` | **Summary file only** | Creative Insights, Synthesis |

**Subagent execution pattern:**

For each subagent:
1. Extract relevant PDF pages based on section mapping
2. Read the subagent from `{baseDir}/subagents/` (contains both config and prompt)
3. Substitute placeholders (see `{baseDir}/references/placeholder-guide.md`)
4. Invoke Task tool with the subagent
5. Subagent reads PDF pages + current summary file
6. Subagent writes output to summary file, updating section markers from PENDING → COMPLETE
7. Verify section was written before proceeding to next agent

### Section Markers

The summary file uses HTML comment markers to track progress:

```html
<!-- SECTION: executive_summary PENDING -->   (not yet written)
<!-- SECTION: executive_summary COMPLETE -->  (successfully written)
<!-- SECTION: methods SKIPPED -->             (not applicable for article type)
```

### Article-Type-Specific Subagent Sequences

**General Research:**
```
overview → methods → results → critique → context → synthesis
```

**Review Article:**
```
overview → evidence → landscape → critique → references → synthesis
```

**Cell & Molecular Biology:**
```
overview → models → mechanisms → results → critique → translational → synthesis
```

**Computational Biology:**
```
overview → data → methods → validation → critique → reproducibility → synthesis
```

### Progress Reporting

Keep user informed during chunked processing:

```
Processing: smith2024_cancer_cells.pdf (24 pages)
Mode: Chunked subagent pipeline

[■■■□□□] Step 3/6: Analyzing results...
  ✓ Overview extracted
  ✓ Methods analyzed
  ◉ Results in progress
  ○ Critical analysis pending
  ○ Context pending
  ○ Synthesis pending
```

---

## Phase 2: Visual Output Format Selection

**After markdown summary is saved, ask the user which visual format(s) they want:**

| Format | Best For | Output |
|--------|----------|--------|
| **Interactive HTML** | Presentations, sharing, detailed review | Single-file HTML with navigation |
| **PDF Summary** | Archival, printing, formal documentation | Brand-compliant PDF via YAML intermediate |
| **SVG Infographic** | Visual presentations, posters, slides | Single-page graphical summary |

Ask: "Which visual output format(s) would you like?"
- Interactive HTML report (web presentation)
- PDF summary (printable document)
- SVG infographic (visual poster)
- Multiple formats
- None (markdown summary only)

</workflow>

---

<output_formats>

## Format-Specific Instructions

**IMPORTANT**: All visual formats use the saved markdown summary file as their source. Read the markdown summary first before generating any visual output.

### 1. Interactive HTML Report

Read: `{baseDir}/prompts/html-report.md`

**Source**: The markdown summary file generated in Phase 1

Single-file HTML document with:
- Sticky navigation bar
- Collapsible sections
- Tabbed findings (In Vitro / In Vivo / Clinical)
- P-value badges with significance styling
- Mechanism diagrams (CSS/HTML)
- Verification checklist

### 2. PDF Summary (via YAML)

Read: `{baseDir}/prompts/yaml-for-pdf.md`

**Source**: The markdown summary file generated in Phase 1

Two-step workflow:
1. Generate YAML summary with figure references (extracted from markdown summary)
2. User runs Python script to generate PDF with automatic figure extraction

Script location: `{baseDir}/scripts/generate_summary_pdf.py`

### 3. SVG Infographic

Read: `{baseDir}/prompts/svg-infographic.md`

See also: `{baseDir}/references/svg-component-library.md` for available components

**Source**: The markdown summary file generated in Phase 1

Single-page visual summary using component library:
- DonutChart, StatCallout, HorizontalBarChart
- TimelineNode, HierarchicalTree
- Brand-compliant colors only
- White background, flat design, no gradients

</output_formats>

---

<core_principles>

## Core Principles (All Formats)

### Quantitative Preservation (Non-Negotiable)

NEVER summarize away numerical data. Always preserve:
- **P-values**: p < 0.05, p = 0.003 (with significance context)
- **Sample sizes**: n = 24/group, N = 156 total
- **Effect sizes**: Cohen's d = 0.8, HR = 0.45, OR = 2.3
- **Confidence intervals**: 95% CI: 1.2–3.4
- **Fold changes**: 2.3-fold increase
- **Concentrations/doses**: 1 mM DFMO, 5 mg/kg
- **Timepoints**: 24h, 4 weeks post-treatment

### Scientific Rigor

- Distinguish novel findings from confirmatory/background
- Preserve conditional language (authors' hedging)
- Include negative/null results
- Note controls and comparators
- Flag limitations (both author-stated and obvious)
- Use exact technical terminology (no paraphrasing jargon)

### Brand Visual Identity

All visual outputs follow the **Oligon Scientific Brand** (see `oligon-brand` skill).

**Quick Reference:**

| Role | Color | HEX |
|------|-------|-----|
| Primary Highlight | Brand Blue | `#2DB2E8` |
| Contrast/Alert | Orange | `#E8622D` |
| Primary Data | Dark Gray | `#222222` |
| Secondary Data | Medium Gray | `#666666` |
| Tertiary Data | Muted Gray | `#999999` |
| Background | White | `#FFFFFF` |

For complete brand specification, color cycles, and accessibility guidelines, see:
- `skills/oligon-brand/SKILL.md`
- `skills/oligon-brand/references/brand-colors-full.md`

## Quick Reference

### Statistics Formatting
```
p = 0.003          (not "p<0.05" if exact value available)
95% CI: 1.2–3.4    (en-dash, not hyphen)
n = 24/group       (specify per-group)
HR = 0.45          (include measure type)
2.3-fold increase  (include direction)
```

### Color Assignment (Visual Outputs)
```
Treatment/Intervention → Brand Blue (#2DB2E8)
Control/Baseline → Dark Gray (#222222)
Adverse/Opposing effect → Orange (#E8622D)
Secondary comparison → Medium Gray (#666666)
```

</core_principles>

---

<article_types>

## Article Type Details

Each summarizer prompt is optimized for its article type:

| Article Type | Summarizer | Key Focus Areas |
|--------------|------------|-----------------|
| **General Research** | `general_researcher_summarizer.md` | Hypothesis, experimental approach, findings, critical analysis, actionable takeaways |
| **Review Article** | `review_article_summarizer.md` | Scope/framing, field landscape, evidence synthesis, knowledge gaps, reference mining |
| **Comp Bio / Bioinformatics** | `compbio_bioinformatic_summarizer.md` | Data foundation, computational approach, validation strategy, reproducibility assessment |
| **Cell & Molecular Biology** | `cellmolbio_summarizer.md` | Model systems, experimental design, mechanistic depth, cancer biology specifics, translational assessment |

### Special Handling Notes

| Condition | Handling |
|-----------|----------|
| **Preprint** | Add prominent "Not Peer-Reviewed" warning in all outputs |
| **Meta-analysis** | Use Review Article summarizer; include forest plot data, heterogeneity stats (I², Q) |
| **Clinical Trial** | Use General Research summarizer; emphasize CONSORT flow, primary/secondary endpoints, adverse events |
| **Methods Paper** | Use Comp Bio summarizer; prioritize protocol details, validation, benchmarks |

</article_types>

---

<error_handling>

## Troubleshooting & Error Recovery

For detailed troubleshooting, see: `{baseDir}/references/troubleshooting.md`

### Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Summary incomplete | Check for PENDING markers; retry skill |
| Context exceeded | Use chunked mode; reduce page ranges |
| PDF generation fails | Run `pip install weasyprint pyyaml` |
| Wrong article type | Re-run with correct selection |

### Recovery Commands

```
# Resume incomplete chunked summary:
User: Continue summarizing - some sections are still PENDING

# Force standard mode:
User: Use standard mode for this paper instead
```

</error_handling>

---

<anti_patterns>

## Common Pitfalls

For detailed anti-patterns with examples, see: `{baseDir}/references/common-pitfalls.md`

### Quick Reference

| Pitfall | Prevention |
|---------|------------|
| Skipping article type selection | Always ask user to confirm type |
| Ignoring page threshold | Trust 12-page automatic detection |
| Summarizing away statistics | Preserve ALL numerical data exactly |
| Missing figure references | Link every finding to source figure |
| Paraphrasing terminology | Use exact technical terms from paper |
| Omitting negative results | Include all results with statistical context |

</anti_patterns>

---

<success_criteria>

## Success Criteria

### Markdown Summary Quality
- [ ] All statistics preserved with exact values
- [ ] Every finding linked to figure/table reference
- [ ] Limitations section includes both author-stated and additional
- [ ] Technical terminology preserved (no paraphrasing jargon)
- [ ] Conditional language preserved (authors' hedging)
- [ ] Negative/null results included with statistical context
- [ ] Sample sizes specified for all experiments

### Visual Output Quality
- [ ] Brand colors applied correctly (Oligon brand)
- [ ] White background, black text
- [ ] Statistics formatted consistently (p = X.XX, 95% CI: X–X)
- [ ] Figures extracted and matched to references (PDF output)
- [ ] No gradients or 3D effects (flat design)

### Chunked Mode Quality
- [ ] All sections marked COMPLETE (no PENDING markers)
- [ ] Subagent outputs are coherent and non-redundant
- [ ] Synthesis section integrates content from all prior sections
- [ ] Progress was reported to user during processing

### Process Compliance
- [ ] User was asked to confirm article type
- [ ] Processing mode was announced to user
- [ ] Output file was saved to source document directory
- [ ] Visual format options were offered after summary completion

</success_criteria>

---

<cross_references>

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `oligon-brand` | **Brand colors** — all visual outputs (HTML, PDF, SVG) use Oligon brand styling |
| `literature-review` | **Finding papers** — use literature-review to find papers, then summarize key ones |
| `research-lookup` | **Quick lookup** — for simple queries; use research-paper-summarizer for deep analysis |
| `peer-review` | **Evaluation vs summary** — peer-review assesses quality; this skill extracts content |
| `markdown-to-pdf` | **Alternative PDF** — for template-based documents; this skill has specialized figure extraction |
| `scientific-critical-thinking` | **Analysis framework** — provides structure for the critical analysis sections |
| `plotting-libraries` | **Figure creation** — if creating new figures from extracted data |
| `visual-design` | **Design principles** — for infographic composition guidance |
| `markitdown` | **PDF conversion** — convert paper PDFs to markdown before summarizing (optional) |

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Typical Workflow:**
1. Receive paper PDF from user
2. `research-paper-summarizer` → generate markdown summary
3. (Optional) `oligon-brand` colors applied → visual output
4. (Optional) `scientific-critical-thinking` → deeper analysis

</cross_references>

---

<references>

## Supporting Files

All paths use `{baseDir}` which resolves to this skill's installation directory.

### Reference Documentation
- `{baseDir}/references/subagent_architecture.md` - Chunked pipeline architecture deep-dive
- `{baseDir}/references/troubleshooting.md` - Error recovery and common issues
- `{baseDir}/references/common-pitfalls.md` - Anti-patterns with detailed examples
- `{baseDir}/references/placeholder-guide.md` - Template variable substitution guide
- `{baseDir}/references/statistics-formatting.md` - Standardized statistics formatting
- `{baseDir}/references/brand-quick-reference.md` - Quick color codes for visual outputs
- `{baseDir}/references/svg-component-library.md` - SVG components for infographics

### Article Type Summarizers (Standard Mode)
- `{baseDir}/prompts/general_researcher_summarizer.md` - General primary research papers
- `{baseDir}/prompts/review_article_summarizer.md` - Review articles and meta-analyses
- `{baseDir}/prompts/compbio_bioinformatic_summarizer.md` - Computational biology
- `{baseDir}/prompts/cellmolbio_summarizer.md` - Cell and molecular biology papers

### Chunked Mode Templates
- `{baseDir}/templates/summary-skeleton.md` - Base skeleton with section markers
- `{baseDir}/templates/skeleton-config.md` - Article-type placeholder values

### Subagent Configurations (Chunked Mode)
Shared agents (all article types):
- `{baseDir}/subagents/overview-agent.md` - Executive summary, background, hypothesis
- `{baseDir}/subagents/critique-agent.md` - Critical analysis, limitations
- `{baseDir}/subagents/synthesis-agent.md` - Final synthesis (summary file only)

Article-type-specific agents:
- `{baseDir}/subagents/general/` - methods-agent, results-agent, context-agent
- `{baseDir}/subagents/review/` - evidence-agent, landscape-agent, references-agent
- `{baseDir}/subagents/cellmolbio/` - models-agent, mechanisms-agent, translational-agent
- `{baseDir}/subagents/compbio/` - data-agent, methods-agent, validation-agent

### Visual Output Prompts
- `{baseDir}/prompts/html-report.md` - Interactive HTML generation
- `{baseDir}/prompts/yaml-for-pdf.md` - YAML for PDF pipeline
- `{baseDir}/prompts/svg-infographic.md` - Infographic with component library

### Brand Guidelines
- `skills/oligon-brand/SKILL.md` - Complete Oligon brand specification

### Scripts
- `{baseDir}/scripts/generate_summary_pdf.py` - PDF generator (requires weasyprint)

### Examples
- `{baseDir}/examples/example_summary.yaml` - YAML output for PDF generation
- `{baseDir}/examples/example_workflow_general.md` - General research workflow

</references>
