---
name: landscape-agent
description: Maps field landscape, knowledge gaps, and future directions from review article
article_types: [review]
execution_order: 3
pdf_sections:
  - introduction
  - discussion
  - future_directions
page_hints:
  introduction_pages: [1, 2, 3, 4]
  discussion_start_percent: 60
  discussion_end_percent: 90
output_sections:
  - results
  - key_findings
  - key_figures
  - statistics
depends_on:
  - overview-agent
  - evidence-agent
prompt_file: prompts/subagents/review/landscape.md
---

# Landscape Agent (Review Article)

## Purpose

The Landscape Agent maps the current state of the field as presented in the review. It identifies key players, historical milestones, knowledge gaps, and future directions - elements that make reviews uniquely valuable.

## Input

- **PDF pages**: Introduction (field background) + Discussion/Conclusions (future directions)
- **Article type**: review
- **Prior context**: Overview established thesis; Evidence documented arguments

## Output

The agent writes to the summary file, filling in:

1. **Field Landscape** (main results section)
   - Current paradigm and consensus
   - Major research groups and seminal papers
   - Competing hypotheses

2. **Key Developments** (subsection)
   - Timeline of field milestones
   - Recent breakthroughs
   - Paradigm shifts

3. **Knowledge Gaps** (subsection)
   - Explicitly identified unknowns
   - Active controversies
   - Questions requiring answers

4. **Field Metrics** (subsection)
   - Clinical translation status
   - Trial landscape summary
   - Regulatory considerations

## Section Markers Updated

```
<!-- SECTION: results PENDING --> → COMPLETE
<!-- SUBSECTION: key_findings PENDING --> → COMPLETE
<!-- SUBSECTION: key_figures PENDING --> → COMPLETE
<!-- SUBSECTION: statistics PENDING --> → COMPLETE
```

## Dependencies

Runs AFTER:
- overview-agent (order 1)
- evidence-agent (order 2)

## Invocation Pattern

```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: Read prompts/subagents/review/landscape.md
- Input: Introduction + Discussion pages from PDF
- Output: Updates summary file sections
```

## Quality Criteria

- Knowledge gaps are often the most valuable content - be thorough
- Distinguish consensus from author opinion
- Timeline includes specific years and attributions
- Key players include institutional affiliations when mentioned
- Future directions are specific, not generic "more research needed"
