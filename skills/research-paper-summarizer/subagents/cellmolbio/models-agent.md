---
name: models-agent
description: Critically evaluates all model systems (cell lines, animal models, patient samples) in cell/molecular biology papers
article_types: [cellmolbio]
execution_order: 2
pdf_sections:
  - methods
  - materials_and_methods
  - supplementary_methods
page_hints:
  start_percent: 15
  end_percent: 35
output_sections:
  - methods
  - methods_1
  - methods_2
depends_on:
  - overview-agent
prompt_file: prompts/subagents/cellmolbio/models.md
---

# Models Agent (Cell & Molecular Biology)

## Purpose

The Models Agent performs rigorous evaluation of all experimental model systems used in cell/molecular biology papers. In cancer research, model system choice is critical - conclusions are only as valid as the models used to generate them.

## Input

- **PDF pages**: Methods/Materials and Methods section
- **Article type**: cellmolbio
- **Prior context**: Overview agent has established the research question

## Output

The agent writes to the summary file, filling in:

1. **Model Systems Overview** (main methods section)
   - Summary of all models used
   - Relevance to human disease

2. **In Vitro & In Vivo Models** (subsection)
   - Comprehensive tables of cell lines and animal models
   - Authentication and validation status
   - Critical assessment of appropriateness

3. **Model Assessment Verdict** (subsection)
   - Overall sufficiency rating
   - Key limitations
   - Suggestions for strengthening

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
- prompt: Read prompts/subagents/cellmolbio/models.md
- Input: Methods section pages from PDF
- Output: Updates summary file sections
```

## Quality Criteria

- EVERY model system documented (cell lines, animals, patient samples)
- Authentication/validation status explicitly noted (including "not stated")
- Relevance to human disease assessed, not just technical rigor
- Limitations are specific and actionable
- Verdict is honest - "adequate" is acceptable when warranted
- Missing controls or models explicitly identified
