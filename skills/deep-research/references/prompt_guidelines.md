# Prompt Guidelines for Deep Research

Best practices for writing prompts that work with the deep-research skill's
template system. Following these guidelines produces consistent, structured
output across runs.

## The Core Principle

**Specify WHAT to research, not HOW to format the output.**

The deep-research skill has mode-specific templates that enforce consistent
section structure, word counts, citation formatting, and mandatory elements.
When your prompt embeds its own output format specification, the LLM may
follow your format instead of the template — producing inconsistent output.

## The Output Contract

At Phase 1 (Scoping), the skill generates an **output contract** that freezes
the section structure for your run. If your prompt contains format directives
(e.g., `<output_format>` blocks), they are mapped to the contract's canonical
section slots during Phase 1. You review and approve the contract at
Checkpoint 1 before any content is generated. The compiler agent then follows
the contract — not your prompt's format spec — during composition.

See `agents/compiler.md` §Output Contract Authority for enforcement details.

## DO specify

| Element | Purpose | Example |
|---------|---------|---------|
| **Research question** | Drives the entire pipeline | "Identify surface proteins on pathogenic Th17 cells for aptamer targeting" |
| **Mode** | Selects the right template | `Mode: lit-review` or `Mode: full` |
| **PICO/PEO framework** | Structures the scoping phase | Population, Intervention, Comparison, Outcome |
| **Entity collision warnings** | Prevents ambiguous search results | "CD30 collides with Hodgkin lymphoma context — filter for Th17" |
| **Seed candidates/sources** | Anchors the bibliography search | "Begin with CCR6, IL-23R, CD161, OX40 as known candidates" |
| **Inclusion/exclusion criteria** | Bounds the literature search | "Human and mouse; 2015-present; exclude reviews" |
| **Evaluation criteria or themes** | Guides synthesis organization | "Organize around 6 criteria: selectivity, internalization, safety..." |
| **Downstream context** | Informs tone and depth | "This feeds into target-validation scoring" |

## DO NOT specify

| Element | Why not | What happens instead |
|---------|---------|---------------------|
| **Output format blocks** (`<output_format>`) | Overrides the skill's template | The contract system maps your content goals to template slots |
| **Section names** ("include a Risk Assessment Matrix") | Creates non-standard structure | Express as a content goal: "Include a summary matrix comparing all categories" |
| **Word counts per section** ("400-700 words each") | Conflicts with mode limits | Mode templates have built-in word targets |
| **File structure** ("save as separate files per phase") | Causes multi-file output | Always single-file markdown; split by sections, not files |
| **Output format** ("LaTeX", "PDF", "HTML") | Overrides markdown mandate | Use downstream skills for format conversion |
| **Custom phase structures** ("Phase 1, Phase 2...") | Conflicts with pipeline phases | The skill has its own 6-phase pipeline |

## Mode Selection Guide

Always include an explicit `Mode:` line in your prompt:

| If your goal is... | Use mode | Template gives you |
|---------------------|----------|-------------------|
| Comprehensive investigation of a topic | `full` | Executive Summary → Methods → Results (themes) → Discussion → Limitations |
| Quick evidence check | `quick` | Key Findings → Evidence Summary → Evidence Quality |
| Map the literature landscape | `lit-review` | Search Strategy → Literature Matrix → Thematic Synthesis → Gap Analysis |
| PRISMA-compliant systematic review | `systematic-review` | Abstract → Methods → Results → Discussion (PRISMA 2020) |
| Generate competing hypotheses | `hypothesis` | Background → Hypotheses → Comparison Matrix → Priority |
| Verify a specific claim | `fact-check` | Claim → Verdict → Evidence → Nuance |
| Guided research exploration | `socratic` | Interactive Socratic dialogue (no written output) |
| Critique a provided text | `review` | Summary → Strengths → Weaknesses → Recommendations |

## Prompt Template

```
Mode: [full|lit-review|systematic-review|hypothesis|fact-check|socratic|review]

Research Question:
[Clear, specific question]

Framework:
[PICO/PEO/open-ended — define Population, Intervention/Exposure, Comparison, Outcome]

Entity Collision Warnings:
[Entities needing disambiguation — gene names, shared terms, etc.]

Seed Candidates/Sources:
[Known starting points for the bibliography search]

Inclusion Criteria:
[What to include — species, date range, study types]

Exclusion Criteria:
[What to exclude — non-primary sources, unrelated contexts]

Evaluation Criteria / Thematic Framework:
[3-7 themes or criteria to organize the synthesis around]

Content Goals:
[What specific content you want — expressed as goals, not structural directives]
- Include a comparison matrix of all candidates across the evaluation criteria
- Provide 300-500 word evidence synthesis per candidate
- Highlight critical data gaps and suggest resolving experiments

Downstream Context:
[How this output will be used — informs depth and formatting]
```

## Example: Prompt 2 Rewritten

**Before (format-heavy, causes inconsistency):**
```
<output_format>
The final report should include:
- Comparative Target Evaluation Matrix — scored with T-tier labels
- Per-target evidence summaries — 300-500 words each
- Gap analysis — missing data for top candidates
- Recommended shortlist — top 3-5 targets
- Limitations section
Report length: 4000-8000 words.
</output_format>
```

**After (content goals, works with template):**
```
Mode: lit-review

Content Goals:
- The thematic synthesis should include a comparative evaluation matrix
  (candidates x 6 criteria, scored with T-tier labels)
- Each candidate should receive a concise evidence synthesis covering all
  6 evaluation criteria
- The gap analysis should identify missing data for top candidates and
  suggest resolving experiments
- The conclusion should present a ranked shortlist of top 3-5 targets

Downstream Context:
Top-ranked targets will be individually profiled using target-intelligence
dossiers and scored via target-validation.
```

## Example: Prompt 3 Rewritten

**Before:**
```
<output_format>
Structure the final report as a risk assessment, not a flat literature review:
- Risk Assessment Matrix — 6 risk categories x mechanism/probability/severity
- Per-category evidence synthesis — 400-700 words each
- Integrated risk profile — cross-category interactions
- Mitigation strategies — for Medium/High categories
- Critical unknowns — prioritized by information value
Report length: 5000-8000 words.
</output_format>
```

**After:**
```
Mode: full

Evaluation Criteria / Thematic Framework:
Organize the synthesis around 6 risk categories:
1. RORγt Function in Tregs
2. RORγt Function in CD8+ T Cells
3. Isoform Specificity (full-length RORγ collateral)
4. RORC-Independent Innate Immune Activation
5. RISC Pathway Disruption
6. Passenger-Strand Off-Target Silencing

Content Goals:
- Include a risk assessment matrix (categories x probability/severity/mitigability)
- Assess both probability and severity for each risk category
- Synthesize cross-category interactions in the discussion
- Recommend mitigation strategies for Medium/High risk categories
- Prioritize experimental recommendations by information value

Downstream Context:
This informs the safety evaluation of the SEEKR aptamer-siRNA chimera program.
```
