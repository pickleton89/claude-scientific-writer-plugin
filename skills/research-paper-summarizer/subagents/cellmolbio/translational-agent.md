---
name: translational-agent
description: Assesses therapeutic implications, clinical feasibility, and translational potential
article_types: [cellmolbio]
execution_order: 6
pdf_sections:
  - discussion
  - conclusions
page_hints:
  start_percent: 65
  end_percent: 90
output_sections:
  - context
  - field_impact
  - future_directions
  - translational_assessment
depends_on:
  - overview-agent
  - models-agent
  - mechanisms-agent
  - results-agent
  - critique-agent
prompt_file: prompts/subagents/cellmolbio/translational.md
---

# Translational Agent (Cell & Molecular Biology)

## Purpose

The Translational Agent assesses the clinical relevance and drug development potential of cell/molecular biology findings. It provides a realistic assessment of the path from bench to bedside.

## Input

- **PDF pages**: Discussion and Conclusions sections
- **Article type**: cellmolbio
- **Prior context**: Full picture from prior agents

## Output

The agent writes to the summary file, filling in:

1. **Translational Assessment** (main context section)
   - Target validation level
   - Druggability assessment
   - Biomarker potential

2. **Field Impact** (subsection)
   - Competitive landscape
   - Advantages/disadvantages vs. alternatives

3. **Future Directions** (subsection)
   - Development stage assessment
   - Critical gaps for translation
   - Realistic timeline

## Section Markers Updated

```
<!-- SECTION: context PENDING --> → COMPLETE
<!-- SUBSECTION: field_impact PENDING --> → COMPLETE
<!-- SUBSECTION: future_directions PENDING --> → COMPLETE
<!-- SUBSECTION: translational_assessment PENDING --> → COMPLETE
```

## Dependencies

Runs AFTER:
- overview-agent (order 1)
- models-agent (order 2)
- mechanisms-agent (order 3)
- results-agent (order 4)
- critique-agent (order 5)

## Invocation Pattern

```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: Read prompts/subagents/cellmolbio/translational.md
- Input: Discussion pages from PDF
- Output: Updates summary file sections
```

## Quality Criteria

- Realistic about translation - most findings don't become drugs
- Specific barriers identified, not vague "more work needed"
- Drug concentrations assessed for clinical achievability
- Business case considered - would pharma pursue this?
- Existing drugs/trials for target mentioned if applicable
- Timeline estimates are honest
