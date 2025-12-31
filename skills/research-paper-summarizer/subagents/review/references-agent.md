---
name: references-agent
description: Mines references for reading recommendations and performs meta-assessment of review quality
article_types: [review]
execution_order: 5
pdf_sections:
  - references
  - acknowledgments
  - disclosures
page_hints:
  start_percent: 85
  end_percent: 100
output_sections:
  - context
  - field_impact
  - future_directions
  - article_specific
  - consensus_controversy
  - evidence_quality
  - reference_mining
depends_on:
  - overview-agent
  - evidence-agent
  - landscape-agent
  - critique-agent
prompt_file: prompts/subagents/review/references.md
---

# References Agent (Review Article)

## Purpose

The References Agent performs reference mining and meta-assessment unique to review articles. It identifies must-read papers, assesses review quality and potential biases, and extracts key terminology.

## Input

- **PDF pages**: References, acknowledgments, disclosures, and conclusions
- **Article type**: review
- **Prior context**: Full picture from prior agents

## Output

The agent writes to the summary file, filling in:

1. **Meta-Assessment** (main context section)
   - Review quality evaluation
   - Potential biases identified
   - Currency of literature

2. **Influence Assessment** (subsection)
   - Likely impact of this review
   - Journal and author standing
   - Shelf life estimate

3. **Reading Recommendations** (subsection)
   - Prioritized list of papers to read
   - Alternative perspectives to seek
   - Methodological resources

4. **Reference Mining Details** (article-specific section)
   - Essential reading table
   - Complementary reviews
   - Key terminology glossary

## Section Markers Updated

```
<!-- SECTION: context PENDING --> → COMPLETE
<!-- SUBSECTION: field_impact PENDING --> → COMPLETE
<!-- SUBSECTION: future_directions PENDING --> → COMPLETE
<!-- SECTION: article_specific PENDING --> → COMPLETE
<!-- SUBSECTION: consensus_controversy PENDING --> → COMPLETE
<!-- SUBSECTION: evidence_quality PENDING --> → COMPLETE
<!-- SUBSECTION: reference_mining PENDING --> → COMPLETE
```

## Dependencies

Runs AFTER:
- overview-agent (order 1)
- evidence-agent (order 2)
- landscape-agent (order 3)
- critique-agent (order 4)

## Invocation Pattern

```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: Read prompts/subagents/review/references.md
- Input: References and disclosure pages from PDF
- Output: Updates summary file sections
```

## Quality Criteria

- Reading list prioritized by importance, not citation order
- Bias assessment is specific and evidence-based
- Conflicts of interest explicitly noted if disclosed
- Currency assessment includes specific date ranges
- Terminology definitions are concise and contextual
- Alternative viewpoints identified even if underrepresented in review
