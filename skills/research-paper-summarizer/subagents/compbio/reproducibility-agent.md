---
name: reproducibility-agent
description: Assesses reproducibility potential, code/data availability, and practical applicability
article_types: [compbio]
execution_order: 6
pdf_sections:
  - methods
  - data_availability
  - code_availability
  - discussion
page_hints:
  methods_percent: [10, 40]
  discussion_percent: [70, 90]
output_sections:
  - context
  - field_impact
  - future_directions
  - article_specific
  - reproducibility
  - code_data_availability
depends_on:
  - overview-agent
  - data-agent
  - methods-agent
  - validation-agent
  - critique-agent
prompt_file: prompts/subagents/compbio/reproducibility.md
---

# Reproducibility Agent (Computational Biology)

## Purpose

The Reproducibility Agent assesses whether computational work can be reproduced and evaluates practical applicability. Reproducibility is a cornerstone of computational biology - results that cannot be reproduced have limited value.

## Input

- **PDF pages**: Methods, Data/Code Availability, Discussion
- **Article type**: compbio
- **Prior context**: Full picture from prior agents

## Output

The agent writes to the summary file, filling in:

1. **Bigger Picture** (main context section)
   - Field impact assessment
   - Overall reproducibility verdict

2. **Field Impact** (subsection)
   - Contribution type (method/dataset/insight)
   - Practical applicability
   - Competitive landscape

3. **Future Directions** (subsection)
   - What's needed to use this
   - Barriers to adoption
   - Effort to reproduce estimate

4. **Validation & Reproducibility** (article-specific section)
   - Reproducibility assessment details
   - Code and data availability

## Section Markers Updated

```
<!-- SECTION: context PENDING --> → COMPLETE
<!-- SUBSECTION: field_impact PENDING --> → COMPLETE
<!-- SUBSECTION: future_directions PENDING --> → COMPLETE
<!-- SECTION: article_specific PENDING --> → COMPLETE
<!-- SUBSECTION: reproducibility PENDING --> → COMPLETE
<!-- SUBSECTION: code_data_availability PENDING --> → COMPLETE
```

## Dependencies

Runs AFTER:
- overview-agent (order 1)
- data-agent (order 2)
- methods-agent (order 3)
- validation-agent (order 4)
- critique-agent (order 5)

## Invocation Pattern

```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: Read prompts/subagents/compbio/reproducibility.md
- Input: Methods, availability statements, Discussion from PDF
- Output: Updates summary file sections
```

## Quality Criteria

- Specific URLs/accessions for code and data
- Code completeness assessed (not just "available")
- Environment specification checked (versions, containers)
- Practical barriers identified (time, hardware, expertise)
- Reproducibility verdict justified
- Effort estimate realistic
