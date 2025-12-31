---
name: mechanisms-agent
description: Assesses mechanistic depth, causality evidence, and pathway delineation in cell/molecular biology papers
article_types: [cellmolbio]
execution_order: 3
pdf_sections:
  - methods
  - results
page_hints:
  start_percent: 15
  end_percent: 65
output_sections:
  - article_specific
  - molecular_mechanisms
  - cancer_hallmarks
depends_on:
  - overview-agent
  - models-agent
prompt_file: prompts/subagents/cellmolbio/mechanisms.md
---

# Mechanisms Agent (Cell & Molecular Biology)

## Purpose

The Mechanisms Agent assesses the depth and rigor of mechanistic evidence in cell/molecular biology papers. It distinguishes correlation from causation and evaluates whether the molecular pathway is adequately defined.

## Input

- **PDF pages**: Methods (for genetic/pharmacological approaches) + Results (for mechanistic findings)
- **Article type**: cellmolbio
- **Prior context**: Overview established the hypothesis; Models documented the systems used

## Output

The agent writes to the summary file, filling in:

1. **Mechanistic Analysis** (article-specific section)
   - Genetic manipulation approaches with validation
   - Pharmacological approaches with controls
   - Pathway delineation assessment

2. **Causality Assessment** (subsection)
   - Evidence strength checklist
   - Causality verdict (Correlative → Definitive)

3. **Mechanistic Gaps** (subsection)
   - Where pathway is incomplete
   - Suggested experiments to fill gaps

## Section Markers Updated

```
<!-- SECTION: article_specific PENDING --> → COMPLETE
<!-- SUBSECTION: molecular_mechanisms PENDING --> → COMPLETE
<!-- SUBSECTION: cancer_hallmarks PENDING --> → COMPLETE
```

## Dependencies

Runs AFTER:
- overview-agent (order 1)
- models-agent (order 2)

## Invocation Pattern

```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: Read prompts/subagents/cellmolbio/mechanisms.md
- Input: Methods + Results pages from PDF
- Output: Updates summary file sections
```

## Quality Criteria

- Clear distinction between correlation and causation
- Rescue experiments assessed as gold standard
- Missing controls explicitly identified
- Pathway gaps are specific (not "more work needed")
- Causality verdict is justified with evidence
- Off-target effects addressed for genetic approaches
