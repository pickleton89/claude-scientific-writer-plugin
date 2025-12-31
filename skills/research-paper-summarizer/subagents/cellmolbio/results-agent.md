---
name: results-agent
description: Extracts key findings with cancer hallmarks assessment and statistical rigor evaluation
article_types: [cellmolbio]
execution_order: 4
pdf_sections:
  - results
page_hints:
  start_percent: 30
  end_percent: 65
output_sections:
  - results
  - key_findings
  - key_figures
  - statistics
depends_on:
  - overview-agent
  - models-agent
  - mechanisms-agent
prompt_file: prompts/subagents/cellmolbio/results.md
---

# Results Agent (Cell & Molecular Biology)

## Purpose

The Results Agent extracts and critically assesses all major findings from cell/molecular biology papers. It pays particular attention to biological significance (not just statistical significance) and explicitly maps findings to cancer hallmarks.

## Input

- **PDF pages**: Results section
- **Article type**: cellmolbio
- **Prior context**: Overview established hypothesis; Models and Mechanisms documented approach

## Output

The agent writes to the summary file, filling in:

1. **Results Overview** (main section)
   - Major findings organized by importance
   - Cancer hallmarks addressed

2. **Key Findings** (subsection)
   - Each finding with effect size, statistics, and biological significance
   - Robustness across models
   - Negative/null results

3. **Key Figures** (subsection)
   - 2-4 most important figures with specific data points
   - Persuasiveness and concerns for each

4. **Statistical Summary** (subsection)
   - Rigor assessment table
   - Statistics verdict

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
- models-agent (order 2)
- mechanisms-agent (order 3)

## Invocation Pattern

```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: Read prompts/subagents/cellmolbio/results.md
- Input: Results section pages from PDF
- Output: Updates summary file sections
```

## Quality Criteria

- ALL numerical data preserved (p-values, fold changes, n, CIs)
- Biological significance assessed separately from statistical significance
- Cancer hallmarks explicitly linked to findings
- Negative/null results documented when present
- Figure descriptions include specific data points
- Statistics verdict is justified
