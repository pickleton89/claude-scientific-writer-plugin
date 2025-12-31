# Implementation Plan: Chunked Subagent PDF Summarization

> **Goal**: Refactor the research-paper-summarizer skill to use specialized subagents that process PDFs in chunks, writing incrementally to a summary file to avoid context exhaustion.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Directory Structure](#2-directory-structure)
3. [Subagent Design](#3-subagent-design)
4. [PDF Section Detection](#4-pdf-section-detection)
5. [File Protocol](#5-file-protocol)
6. [Orchestration Logic](#6-orchestration-logic)
7. [Implementation Phases](#7-implementation-phases)
8. [Error Handling](#8-error-handling)
9. [Testing Strategy](#9-testing-strategy)
10. [Migration Path](#10-migration-path)

---

## 1. Architecture Overview

### Current Problem

The existing skill reads entire PDFs into context, then applies comprehensive analysis prompts. For papers >15 pages, this exhausts context before completing the summary.

### Solution: Chunked Processing with File-Based Memory

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR                                   │
│                         (SKILL.md logic)                                │
│                                                                         │
│  1. Receive PDF path                                                    │
│  2. Detect PDF metadata (page count, sections)                          │
│  3. Ask user for article type                                           │
│  4. Create skeleton summary file                                        │
│  5. Dispatch subagents sequentially                                     │
│  6. Validate completed summary                                          │
│  7. Proceed to visual output phase                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SUBAGENT PIPELINE                               │
│                                                                         │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│   │ Overview │───▶│ Methods  │───▶│ Results  │───▶│ Critique │        │
│   │ Agent    │    │ Agent    │    │ Agent    │    │ Agent    │        │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘        │
│        │               │               │               │               │
│        ▼               ▼               ▼               ▼               │
│   [Creates]       [Appends]       [Appends]       [Appends]           │
│                                                                         │
│                    _summary.md (accumulating file)                      │
│                                                                         │
│   ┌──────────┐    ┌──────────┐                                         │
│   │ Context  │───▶│ Synthesis│                                         │
│   │ Agent    │    │ Agent    │                                         │
│   └────┬─────┘    └────┬─────┘                                         │
│        │               │                                                │
│        ▼               ▼                                                │
│   [Appends]       [Completes]  ◀── Reads summary file, NOT PDF         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Each subagent reads only relevant PDF pages** - Reduces context per agent
2. **File is the shared memory** - Subagents write output to disk immediately
3. **Sequential execution** - Each agent depends on prior agents completing
4. **Synthesis agent reads file, not PDF** - Final integration without re-reading source
5. **Article-type routing** - Different pathways for different paper types

---

## 2. Directory Structure

```
research-paper-summarizer/
├── SKILL.md                          # Main orchestrator (refactored)
├── IMPLEMENTATION_PLAN.md            # This document
│
├── prompts/
│   ├── # Existing visual output prompts (unchanged)
│   ├── html-report.md
│   ├── yaml-for-pdf.md
│   ├── svg-infographic.md
│   │
│   ├── # Legacy full-document prompts (kept for fallback)
│   ├── general_researcher_summarizer.md
│   ├── review_article_summarizer.md
│   ├── compbio_bioinformatic_summarizer.md
│   ├── cellmolbio_summarizer.md
│   │
│   └── subagents/                    # NEW: Chunked processing prompts
│       │
│       ├── _shared/                  # Prompts used by all article types
│       │   ├── overview.md           # Exec summary, background, hypothesis
│       │   ├── critique.md           # Critical analysis, limitations
│       │   └── synthesis.md          # Final synthesis (reads file, not PDF)
│       │
│       ├── general/                  # General research paper variants
│       │   ├── methods.md            # Experimental approach
│       │   ├── results.md            # Results breakdown
│       │   └── context.md            # Bigger picture, implications
│       │
│       ├── review/                   # Review article variants
│       │   ├── evidence.md           # Core arguments, evidence synthesis
│       │   ├── landscape.md          # Field landscape, frameworks
│       │   └── references.md         # Reference mining, meta-assessment
│       │
│       ├── cellmolbio/               # Cell & molecular biology variants
│       │   ├── models.md             # Model systems, experimental design
│       │   ├── results.md            # Results + cancer hallmarks
│       │   ├── mechanisms.md         # Mechanistic depth
│       │   └── translational.md      # Translational assessment
│       │
│       └── compbio/                  # Computational biology variants
│           ├── data.md               # Data foundation, sources
│           ├── methods.md            # Computational approach
│           ├── validation.md         # Results + benchmarking
│           └── reproducibility.md    # Reproducibility assessment
│
├── subagents/                        # NEW: Subagent configuration files
│   ├── overview-agent.md             # Shared overview agent
│   ├── critique-agent.md             # Shared critique agent
│   ├── synthesis-agent.md            # Shared synthesis agent
│   │
│   ├── general/
│   │   ├── methods-agent.md
│   │   ├── results-agent.md
│   │   └── context-agent.md
│   │
│   ├── review/
│   │   ├── evidence-agent.md
│   │   ├── landscape-agent.md
│   │   └── references-agent.md
│   │
│   ├── cellmolbio/
│   │   ├── models-agent.md
│   │   ├── results-agent.md
│   │   ├── mechanisms-agent.md
│   │   └── translational-agent.md
│   │
│   └── compbio/
│       ├── data-agent.md
│       ├── methods-agent.md
│       ├── validation-agent.md
│       └── reproducibility-agent.md
│
├── templates/
│   ├── summary-skeleton.md           # NEW: Initial file structure
│   └── report-template.html          # Existing HTML template
│
└── scripts/
    └── generate_summary_pdf.py       # Unchanged

# Note: Brand colors are defined in skills/oligon-brand/ (project-wide brand skill)
```

---

## 3. Subagent Design

### 3.1 Subagent Configuration Format

Each subagent is defined in a `.md` file with YAML frontmatter:

```yaml
---
name: overview-agent
description: Extracts executive summary, background, and hypothesis from paper introduction
article_types: [general, review, cellmolbio, compbio]  # Or "all"
execution_order: 1
pdf_sections:
  - abstract
  - introduction
page_hints:
  start: 1
  end: 3
  fallback_pages: 4
output_sections:
  - executive_summary
  - background_motivation
  - hypothesis
  - key_quotes
depends_on: []  # No dependencies - runs first
---

# Overview Agent Prompt

You are analyzing a scientific paper to extract introductory context.

## Your Task

Read the provided PDF pages (Abstract and Introduction) and generate:

1. **Executive Summary** (2-3 sentences)
2. **Background & Motivation**
3. **Central Hypothesis**
4. **Key Quotes** from the authors

## Input

<pdf_content>
{{PDF_PAGES}}
</pdf_content>

<article_type>
{{ARTICLE_TYPE}}
</article_type>

## Output Format

Write your analysis in markdown, using the exact section headers shown above.
Your output will be appended to the summary file.

[... detailed instructions ...]
```

### 3.2 Shared vs Variant Subagents

**Shared Subagents** (identical across article types):

| Agent | Order | PDF Sections | Output Sections |
|-------|-------|--------------|-----------------|
| `overview-agent` | 1 | Abstract, Introduction | Exec Summary, Background, Hypothesis |
| `critique-agent` | 4 | Discussion (latter half) | Strengths, Limitations, Red Flags |
| `synthesis-agent` | 6 | **None (reads summary file)** | Creative Insights, Final Synthesis |

**Variant Subagents** (differ by article type):

| Article Type | Agent 2 | Agent 3 | Agent 5 |
|--------------|---------|---------|---------|
| General | `methods-agent` | `results-agent` | `context-agent` |
| Review | *(skip)* | `evidence-agent` | `landscape-agent` + `references-agent` |
| CellMolBio | `models-agent` | `results-agent` + `mechanisms-agent` | `translational-agent` |
| CompBio | `data-agent` + `methods-agent` | `validation-agent` | `reproducibility-agent` |

### 3.3 Subagent Input/Output Contract

**Inputs (provided by orchestrator):**
- `{{PDF_PAGES}}` - Extracted text from specific pages
- `{{ARTICLE_TYPE}}` - User-selected type
- `{{RESEARCH_FOCUS}}` - User's research area (optional)
- `{{SUMMARY_FILE_PATH}}` - Path to write output
- `{{PRIOR_SECTIONS}}` - List of sections already completed

**Outputs (written to file):**
- Markdown content with standardized section headers
- Section markers for validation: `<!-- SECTION: executive_summary COMPLETE -->`

---

## 4. PDF Section Detection

### 4.1 The Challenge

Scientific papers don't have consistent page layouts. We need to identify where sections start/end.

### 4.2 Detection Strategy

**Primary: Keyword-Based Section Detection**

```python
SECTION_MARKERS = {
    "abstract": ["abstract", "summary"],
    "introduction": ["introduction", "background"],
    "methods": ["methods", "materials and methods", "experimental procedures",
                "experimental section", "methodology"],
    "results": ["results", "findings"],
    "discussion": ["discussion", "conclusions", "concluding remarks"],
    "references": ["references", "bibliography", "literature cited"]
}
```

**Approach:**
1. Read first 2 pages to find Abstract/Introduction
2. Scan page headers/first lines for section keywords
3. Build section-to-page mapping
4. Use heuristics for unlabeled sections:
   - Methods usually follows Introduction
   - Results usually starts ~40% through paper
   - Discussion usually starts ~70% through paper

**Fallback: Page-Based Estimation**

If section detection fails, use page ratios:

| Section | Page Range (% of total) |
|---------|------------------------|
| Abstract + Intro | Pages 1-3 or first 15% |
| Methods | 15-30% |
| Results | 30-65% |
| Discussion | 65-85% |
| References | 85-100% |

### 4.3 Implementation

Add a utility prompt that runs before subagents:

```markdown
# Section Detection Prompt

Scan this PDF and identify the page numbers where each section begins:

- Abstract: Page __
- Introduction: Page __
- Methods/Materials: Page __
- Results: Page __
- Discussion: Page __
- References: Page __

Output as JSON:
{
  "abstract": {"start": 1, "end": 1},
  "introduction": {"start": 1, "end": 3},
  "methods": {"start": 4, "end": 6},
  ...
}
```

---

## 5. File Protocol

### 5.1 Summary File Format

The summary file uses a standardized structure with section markers:

```markdown
# Paper Summary: {{PAPER_TITLE}}

> Generated: {{TIMESTAMP}}
> Article Type: {{ARTICLE_TYPE}}
> Source: {{PDF_FILENAME}}

---

<!-- SECTION: metadata COMPLETE -->

## 1. Executive Summary

[Content written by overview-agent]

<!-- SECTION: executive_summary COMPLETE -->

## 2. Background & Motivation

[Content written by overview-agent]

<!-- SECTION: background COMPLETE -->

## 3. Experimental Approach

<!-- SECTION: methods PENDING -->

[To be filled by methods-agent]

...
```

### 5.2 Section Markers

Each section uses HTML comments for tracking:

```html
<!-- SECTION: {section_name} {STATUS} -->
```

Status values:
- `PENDING` - Not yet written
- `IN_PROGRESS` - Agent currently working
- `COMPLETE` - Successfully written
- `SKIPPED` - Not applicable for this article type

### 5.3 File Operations

**Orchestrator creates skeleton:**
```
1. Read templates/summary-skeleton.md
2. Fill in metadata (title, date, article type)
3. Mark all sections as PENDING
4. Write to {original_filename}_summary.md
```

**Subagents append content:**
```
1. Read current summary file
2. Find target section marker (PENDING)
3. Replace marker with content + COMPLETE marker
4. Write updated file
```

**Synthesis agent reads file:**
```
1. Read completed summary file (all sections COMPLETE)
2. Generate synthesis based on file content
3. Append final sections
```

### 5.4 Skeleton Template

```markdown
# Paper Summary: {{TITLE}}

> **Generated**: {{TIMESTAMP}}
> **Article Type**: {{ARTICLE_TYPE}}
> **Source**: {{FILENAME}}
> **Processing Mode**: Chunked Subagent Pipeline

---

<!-- METADATA_END -->

## 1. Executive Summary

<!-- SECTION: executive_summary PENDING -->

## 2. Background & Motivation

<!-- SECTION: background PENDING -->

### Knowledge Gap
<!-- SUBSECTION: knowledge_gap PENDING -->

### Central Hypothesis
<!-- SUBSECTION: hypothesis PENDING -->

### Key Quote
<!-- SUBSECTION: background_quote PENDING -->

## 3. {{METHODS_SECTION_TITLE}}

<!-- SECTION: methods PENDING -->

## 4. Results

<!-- SECTION: results PENDING -->

### Key Findings
<!-- SUBSECTION: key_findings PENDING -->

### Key Figures
<!-- SUBSECTION: key_figures PENDING -->

### Statistical Summary
<!-- SUBSECTION: statistics PENDING -->

## 5. Critical Analysis

<!-- SECTION: critical_analysis PENDING -->

### Strengths
<!-- SUBSECTION: strengths PENDING -->

### Limitations
<!-- SUBSECTION: limitations PENDING -->

### Red Flags
<!-- SUBSECTION: red_flags PENDING -->

## 6. Bigger Picture

<!-- SECTION: context PENDING -->

## 7. {{ARTICLE_SPECIFIC_SECTION}}

<!-- SECTION: article_specific PENDING -->

## 8. Creative Insights & Connections

<!-- SECTION: insights PENDING -->

## 9. Actionable Takeaways

<!-- SECTION: takeaways PENDING -->

## 10. One-Paragraph Synthesis

<!-- SECTION: synthesis PENDING -->

---

<!-- SUMMARY_END -->
```

---

## 6. Orchestration Logic

### 6.1 Updated SKILL.md Flow

```
PHASE 0: INITIALIZATION
├── Receive PDF path from user
├── Validate PDF exists and is readable
├── Extract PDF metadata (page count, title if possible)
├── Determine processing mode:
│   ├── IF pages <= 12: Use legacy full-document prompts
│   └── IF pages > 12: Use chunked subagent pipeline
└── Ask user for article type

PHASE 1: SETUP (Chunked Mode Only)
├── Run section detection on PDF
├── Create section-to-page mapping
├── Read templates/summary-skeleton.md
├── Fill in metadata placeholders
├── Customize skeleton for article type
└── Write skeleton to {filename}_summary.md

PHASE 2: SUBAGENT DISPATCH
├── Determine subagent sequence for article type
├── FOR EACH subagent in sequence:
│   ├── Extract relevant PDF pages
│   ├── Read subagent prompt template
│   ├── Fill in placeholders (PDF content, article type, etc.)
│   ├── Invoke Task tool with subagent
│   ├── Verify output was written to file
│   └── Handle errors (retry once, then flag)
└── Validate all sections marked COMPLETE

PHASE 3: VISUAL OUTPUT (Unchanged)
├── Ask user for visual format(s)
├── Read completed summary file
├── Generate visual outputs as before
└── Provide output files to user
```

### 6.2 Subagent Dispatch Sequences

**General Research:**
```
1. overview-agent      → Pages 1-3
2. methods-agent       → Methods section pages
3. results-agent       → Results section pages
4. critique-agent      → Discussion pages
5. context-agent       → Introduction + Discussion (refs)
6. synthesis-agent     → Reads summary file only
```

**Review Article:**
```
1. overview-agent      → Pages 1-3
2. evidence-agent      → Core content pages (varies)
3. landscape-agent     → Field overview sections
4. critique-agent      → Critical evaluation sections
5. references-agent    → Reference analysis
6. synthesis-agent     → Reads summary file only
```

**Cell & Molecular Biology:**
```
1. overview-agent      → Pages 1-3
2. models-agent        → Methods (model systems)
3. mechanisms-agent    → Methods (techniques) + Results (mechanism)
4. results-agent       → Results pages
5. critique-agent      → Discussion pages
6. translational-agent → Discussion (clinical implications)
7. synthesis-agent     → Reads summary file only
```

**Computational Biology:**
```
1. overview-agent      → Pages 1-3
2. data-agent          → Methods (data sources)
3. methods-agent       → Methods (computational approach)
4. validation-agent    → Results + Validation sections
5. critique-agent      → Discussion pages
6. reproducibility-agent → Methods + Discussion (reproducibility)
7. synthesis-agent     → Reads summary file only
```

### 6.3 Task Tool Invocation Pattern

```markdown
For each subagent, the orchestrator invokes:

<Task>
  subagent_type: "general-purpose"
  prompt: |
    You are the {AGENT_NAME} for the research paper summarizer.

    ## Your Role
    {Read from subagents/{type}/{agent}.md}

    ## PDF Content to Analyze
    {Extracted pages from PDF}

    ## Current Summary File
    Path: {summary_file_path}

    ## Instructions
    1. Read the PDF content provided
    2. Read the current summary file
    3. Find the section marked PENDING for your output
    4. Write your analysis
    5. Update the section marker to COMPLETE
    6. Save the file

    ## Output Sections You Are Responsible For
    {List from subagent config}
</Task>
```

---

## 7. Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Deliverables:**
- [ ] Directory structure created
- [ ] `templates/summary-skeleton.md` created
- [ ] Section detection utility prompt
- [ ] File protocol utilities (marker reading/writing)
- [ ] Updated SKILL.md with processing mode detection

**Files to Create:**
```
prompts/subagents/_shared/
templates/summary-skeleton.md
```

**SKILL.md Changes:**
- Add page count detection logic
- Add processing mode branching
- Keep legacy prompts as fallback

---

### Phase 2: General Research Pathway (Week 2)

**Deliverables:**
- [ ] All shared subagent prompts
- [ ] General research variant prompts
- [ ] Subagent config files for general pathway
- [ ] End-to-end test with sample paper

**Files to Create:**
```
prompts/subagents/_shared/overview.md
prompts/subagents/_shared/critique.md
prompts/subagents/_shared/synthesis.md
prompts/subagents/general/methods.md
prompts/subagents/general/results.md
prompts/subagents/general/context.md
subagents/overview-agent.md
subagents/critique-agent.md
subagents/synthesis-agent.md
subagents/general/methods-agent.md
subagents/general/results-agent.md
subagents/general/context-agent.md
```

**Testing:**
- Test with short paper (<12 pages) - should use legacy
- Test with long paper (>15 pages) - should use chunked
- Verify all sections populated
- Compare output quality to legacy approach

---

### Phase 3: Additional Article Types (Week 3)

**Deliverables:**
- [ ] Review article pathway
- [ ] Cell & molecular biology pathway
- [ ] Computational biology pathway

**Files to Create:**
```
prompts/subagents/review/*.md
prompts/subagents/cellmolbio/*.md
prompts/subagents/compbio/*.md
subagents/review/*.md
subagents/cellmolbio/*.md
subagents/compbio/*.md
```

**Testing:**
- Test each pathway with appropriate sample paper
- Verify article-type-specific sections populated

---

### Phase 4: Visual Output Integration (Week 4)

**Deliverables:**
- [ ] Verify visual prompts work with new summary format
- [ ] Update section mappings if needed
- [ ] Add any missing fields for visual templates

**Testing:**
- Generate HTML report from chunked summary
- Generate PDF via YAML from chunked summary
- Generate SVG infographic from chunked summary

---

### Phase 5: Polish & Documentation (Week 5)

**Deliverables:**
- [ ] Error handling improvements
- [ ] Progress feedback to user
- [ ] Updated SKILL.md documentation
- [ ] Usage examples
- [ ] Remove/archive legacy prompts (or keep as fallback)

---

## 8. Error Handling

### 8.1 Failure Scenarios

| Scenario | Detection | Recovery |
|----------|-----------|----------|
| Subagent fails to write | Section still PENDING after Task completes | Retry once, then fall back to legacy mode |
| PDF section detection fails | No sections found | Use page-ratio fallback |
| Partial completion | Some sections COMPLETE, others PENDING | Resume from last PENDING section |
| Malformed output | Section marker invalid | Parse error, retry with clearer instructions |
| Context exceeded in subagent | Task returns truncated | Reduce page range, retry |

### 8.2 Graceful Degradation

```
IF chunked processing fails:
  1. Log failure reason
  2. Notify user: "Falling back to standard processing"
  3. Use legacy full-document prompt
  4. May still hit context limits, but provides best effort
```

### 8.3 Progress Reporting

Provide user visibility into progress:

```
Processing paper: smith2024_cancer_cells.pdf (24 pages)
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

## 9. Testing Strategy

### 9.1 Test Papers

Maintain a set of test papers:

| Paper | Pages | Type | Purpose |
|-------|-------|------|---------|
| `test_short_general.pdf` | 8 | General | Verify legacy mode works |
| `test_long_general.pdf` | 25 | General | Verify chunked mode works |
| `test_review.pdf` | 30 | Review | Verify review pathway |
| `test_cellmolbio.pdf` | 20 | CellMolBio | Verify cancer-specific sections |
| `test_compbio.pdf` | 18 | CompBio | Verify reproducibility sections |

### 9.2 Validation Checks

**Completeness:**
- All section markers show COMPLETE
- No placeholder text remains
- All expected sections present for article type

**Quality:**
- Numerical data preserved (p-values, sample sizes)
- Key quotes extracted
- Limitations identified
- No hallucinated content

**Format:**
- Valid markdown
- Consistent heading levels
- Tables properly formatted

### 9.3 Regression Testing

After each change:
1. Run all test papers through pipeline
2. Compare output to baseline summaries
3. Flag significant differences for review

---

## 10. Migration Path

### 10.1 Backward Compatibility

- Keep legacy prompts in `prompts/*.md`
- Short papers automatically use legacy mode
- User can force legacy mode with flag

### 10.2 Rollout Strategy

1. **Alpha**: Test internally with sample papers
2. **Beta**: Enable for papers >20 pages only
3. **GA**: Enable for all papers >12 pages
4. **Sunset**: Remove legacy mode after 30 days stable

### 10.3 User Communication

Add to SKILL.md user-facing notes:

```markdown
## Processing Modes

This skill automatically selects the best processing approach:

- **Standard Mode** (papers ≤12 pages): Full document analysis
- **Chunked Mode** (papers >12 pages): Section-by-section processing

Chunked mode may take slightly longer but handles large papers
without context limitations.
```

---

## Appendix A: Subagent Prompt Template

```markdown
---
name: {{AGENT_NAME}}
description: {{DESCRIPTION}}
article_types: {{TYPES}}
execution_order: {{ORDER}}
pdf_sections: {{SECTIONS}}
output_sections: {{OUTPUT}}
---

# {{AGENT_NAME}}

You are a specialized analyst focusing on {{FOCUS_AREA}}.

## Context

You are part of a multi-agent pipeline summarizing a scientific paper.
Other agents handle different sections. Your job is ONLY to analyze
{{YOUR_SECTIONS}} and write {{YOUR_OUTPUT}}.

## Input

<pdf_pages>
{{PDF_CONTENT}}
</pdf_pages>

<article_type>{{ARTICLE_TYPE}}</article_type>

<research_focus>{{RESEARCH_FOCUS}}</research_focus>

## Your Task

Analyze the provided content and generate:

{{DETAILED_INSTRUCTIONS}}

## Output Requirements

1. Use the exact section headers specified
2. Preserve ALL numerical data (p-values, n=, fold changes, etc.)
3. Extract verbatim quotes where requested
4. Be critical but fair
5. Note any missing information explicitly

## File Instructions

Write your output to: {{SUMMARY_FILE_PATH}}
Find the section marker: `<!-- SECTION: {{SECTION_NAME}} PENDING -->`
Replace with your content and update marker to COMPLETE.

---

Begin your analysis now.
```

---

## Appendix B: Section Detection Heuristics

```python
# Pseudocode for section detection

def detect_sections(pdf_text_by_page):
    sections = {}

    for page_num, text in enumerate(pdf_text_by_page, 1):
        # Check first 500 chars of each page for section headers
        header_area = text[:500].lower()

        for section, keywords in SECTION_MARKERS.items():
            for keyword in keywords:
                if keyword in header_area:
                    if section not in sections:
                        sections[section] = {"start": page_num}
                    break

    # Fill in end pages
    section_order = ["abstract", "introduction", "methods",
                     "results", "discussion", "references"]

    for i, section in enumerate(section_order):
        if section in sections:
            # End page is start of next section - 1
            next_sections = [s for s in section_order[i+1:] if s in sections]
            if next_sections:
                sections[section]["end"] = sections[next_sections[0]]["start"] - 1
            else:
                sections[section]["end"] = len(pdf_text_by_page)

    return sections
```

---

## Appendix C: Estimated Token Usage

| Component | Est. Tokens | Notes |
|-----------|-------------|-------|
| PDF page (text) | ~800-1200 | Varies by density |
| Subagent prompt | ~500-800 | Plus PDF content |
| Output per section | ~400-1000 | Varies by section |
| Summary file (final) | ~4000-8000 | All sections combined |

**Per-subagent context:**
- Input: ~2000-4000 tokens (prompt + 3-5 PDF pages)
- Output: ~500-1500 tokens
- Total: ~3000-6000 tokens per subagent

**Full pipeline (6 agents):**
- Total tokens used: ~20,000-35,000 (spread across agents)
- vs. Legacy mode: ~25,000-50,000 (single context)

**Net benefit:** Avoids single-context overflow while maintaining quality.

---

## Summary

This implementation transforms the skill from a single-pass full-document approach to a chunked multi-agent pipeline:

1. **Orchestrator** handles routing and file management
2. **Shared subagents** (3) work across all article types
3. **Variant subagents** (3-4 per type) handle type-specific analysis
4. **File protocol** enables incremental writing and validation
5. **Graceful fallback** to legacy mode if chunked processing fails

The architecture is designed to be maintainable, testable, and extensible to new article types or output formats.
