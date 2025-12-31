---
name: validation-agent
description: Extracts results and critically assesses validation strategy and overfitting risk
article_types: [compbio]
execution_order: 4
pdf_sections:
  - results
page_hints:
  start_percent: 35
  end_percent: 70
output_sections:
  - results
  - key_findings
  - key_figures
  - statistics
  - benchmarking
depends_on:
  - overview-agent
  - data-agent
  - methods-agent
prompt_file: prompts/subagents/compbio/validation.md
---

# Validation Agent (Computational Biology)

## Purpose

The Validation Agent extracts key results and critically evaluates the validation strategy. In computational biology, validation rigor is crucial - overfitting and circular analyses are common pitfalls.

## Input

- **PDF pages**: Results section
- **Article type**: compbio
- **Prior context**: Overview established question; Data and Methods documented approach

## Output

The agent writes to the summary file, filling in:

1. **Results Overview** (main section)
   - Key findings with performance metrics
   - Validation strategy assessment

2. **Key Findings** (subsection)
   - Each finding with metrics, baselines, interpretation
   - Internal vs. external validation performance

3. **Key Figures** (subsection)
   - Most important figures with specific values
   - Assessment of persuasiveness

4. **Statistical Summary** (subsection)
   - Performance metrics table
   - Overfitting risk assessment

5. **Benchmarking & Validation** (article-specific subsection)
   - Comparison against existing methods
   - Validation strategy assessment

## Section Markers Updated

```
<!-- SECTION: results PENDING --> → COMPLETE
<!-- SUBSECTION: key_findings PENDING --> → COMPLETE
<!-- SUBSECTION: key_figures PENDING --> → COMPLETE
<!-- SUBSECTION: statistics PENDING --> → COMPLETE
<!-- SUBSECTION: benchmarking PENDING --> → COMPLETE
```

## Dependencies

Runs AFTER:
- overview-agent (order 1)
- data-agent (order 2)
- methods-agent (order 3)

## Invocation Pattern

```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: Read prompts/subagents/compbio/validation.md
- Input: Results section pages from PDF
- Output: Updates summary file sections
```

## Quality Criteria

- ALL performance metrics captured with CIs
- Internal vs. external validation compared
- Baselines and random performance included
- Overfitting risk explicitly assessed
- Negative/null results documented
- Performance drop in external validation flagged
