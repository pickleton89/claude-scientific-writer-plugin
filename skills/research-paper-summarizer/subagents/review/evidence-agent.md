---
name: evidence-agent
description: Extracts core arguments, evidence synthesis, and frameworks from review article body
article_types: [review]
execution_order: 2
pdf_sections:
  - body
  - main_content
page_hints:
  start_percent: 10
  end_percent: 60
output_sections:
  - methods
  - methods_1
  - methods_2
depends_on:
  - overview-agent
prompt_file: prompts/subagents/review/evidence.md
---

# Evidence Agent (Review Article)

## Purpose

The Evidence Agent extracts how arguments are constructed and evidence is synthesized in review articles. Unlike primary research papers, reviews don't have traditional Methods sections - instead, this agent documents the argumentation structure and quality of evidence synthesis.

## Input

- **PDF pages**: Main body of review (typically 10-60% of document)
- **Article type**: review
- **Prior context**: Overview agent has established scope and thesis

## Output

The agent writes to the summary file, filling in:

1. **Evidence Synthesis Approach** (main methods section)
   - How the review organizes and presents evidence
   - Whether systematic or narrative approach

2. **Argument Structure** (subsection)
   - Major claims with supporting evidence
   - Evidence quality assessment per claim
   - Treatment of contrary findings

3. **Frameworks & Models** (subsection)
   - Conceptual frameworks proposed
   - Classification systems
   - Assessment of framework utility

## Section Markers Updated

```
<!-- SECTION: methods PENDING --> → COMPLETE
<!-- SUBSECTION: methods_1 PENDING --> → COMPLETE
<!-- SUBSECTION: methods_2 PENDING --> → COMPLETE
```

## Dependencies

Runs AFTER:
- overview-agent (order 1)

## Invocation Pattern

```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: Read prompts/subagents/review/evidence.md
- Input: Main body pages from PDF
- Output: Updates summary file sections
```

## Quality Criteria

- Arguments organized by strength of evidence, not presentation order
- Evidence types distinguished (meta-analysis vs. narrative synthesis)
- Contrary evidence explicitly noted when present
- Key frameworks assessed for utility and support
- Verbatim quotes for important synthetic statements
