# Writing Process: From Outline to Full Paragraphs

> Detailed guide for the two-stage scientific writing process
> Load this file when drafting manuscript sections
>
> **See also:** Universal voice and revision standards live in `../../shared/references/prose_standards.md`. This file covers the *process* of converting outlines to publishable prose; the universal voice/style rules apply to whatever you draft.

## Critical Rule

**Always write in full paragraphs, never submit bullet points in scientific papers.**

Scientific papers must be written in complete, flowing prose. Use this two-stage approach for effective writing.

---

## Stage 1: Create Section Outlines with Key Points

When starting a new section:

1. Use the `deep-research` skill to gather relevant literature and data
2. Create a structured outline with bullet points marking:
   - Main arguments or findings to present
   - Key studies to cite
   - Data points and statistics to include
   - Logical flow and organization
3. These bullet points serve as scaffolding—they are NOT the final manuscript

### Example Outline (Introduction section)

```
- Background: AI in drug discovery gaining traction
  * Cite recent reviews (Smith 2023, Jones 2024)
  * Traditional methods are slow and expensive
- Gap: Limited application to rare diseases
  * Only 2 prior studies (Lee 2022, Chen 2023)
  * Small datasets remain a challenge
- Our approach: Transfer learning from common diseases
  * Novel architecture combining X and Y
- Study objectives: Validate on 3 rare disease datasets
```

---

## Stage 2: Convert Key Points to Full Paragraphs

Once the outline is complete, expand each bullet point into proper prose:

1. **Transform bullet points into complete sentences** with subjects, verbs, and objects
2. **Add transitions** between sentences and ideas (however, moreover, in contrast, subsequently)
3. **Integrate citations naturally** within sentences, not as lists
4. **Expand with context and explanation** that bullet points omit
5. **Ensure logical flow** from one sentence to the next within each paragraph
6. **Vary sentence structure** to maintain reader engagement

### Example Conversion to Prose

```
Artificial intelligence approaches have gained significant traction in drug discovery
pipelines over the past decade (Smith, 2023; Jones, 2024). While these computational
methods show promise for accelerating the identification of therapeutic candidates,
traditional experimental approaches remain slow and resource-intensive, often requiring
years of laboratory work and substantial financial investment. However, the application
of AI to rare diseases has been limited, with only two prior studies demonstrating
proof-of-concept results (Lee, 2022; Chen, 2023). The primary obstacle has been the
scarcity of training data for conditions affecting small patient populations.

To address this challenge, we developed a transfer learning approach that leverages
knowledge from well-characterized common diseases to predict therapeutic targets for
rare conditions. Our novel neural architecture combines convolutional layers for
molecular feature extraction with attention mechanisms for protein-ligand interaction
modeling. The objective of this study was to validate our approach across three
independent rare disease datasets, assessing both predictive accuracy and biological
interpretability of the results.
```

---

## Key Differences: Outlines vs Final Text

| Outline (Planning Stage) | Final Manuscript |
|--------------------------|------------------|
| Bullet points and fragments | Complete sentences and paragraphs |
| Telegraphic notes | Full explanations with context |
| List of citations | Citations integrated into prose |
| Abbreviated ideas | Developed arguments with transitions |
| For your eyes only | For publication and peer review |

---

## Common Mistakes to Avoid

- **Never** leave bullet points in the final manuscript
- **Never** submit lists where paragraphs should be
- **Don't** use numbered or bulleted lists in Results or Discussion sections (except for specific cases like study hypotheses or inclusion criteria)
- **Don't** write sentence fragments or incomplete thoughts
- **Do** use occasional lists only in Methods (e.g., inclusion/exclusion criteria, materials lists)
- **Do** ensure every section flows as connected prose
- **Do** read paragraphs aloud to check for natural flow

---

## When Lists ARE Acceptable (Limited Cases)

Lists may appear in scientific papers only in specific contexts:

- **Methods**: Inclusion/exclusion criteria, materials and reagents, participant characteristics
- **Supplementary Materials**: Extended protocols, equipment lists, detailed parameters
- **Never in**: Abstract, Introduction, Results, Discussion, Conclusions

---

## Abstract Format Rule

- **NEVER** use labeled sections (Background:, Methods:, Results:, Conclusions:)
- **ALWAYS** write as flowing paragraph(s) with natural transitions
- Exception: Only use structured format if journal explicitly requires it in author guidelines

---

## Integration with Deep Research

The `deep-research` skill is essential for Stage 1 (creating outlines):

1. Search for relevant papers using `deep-research`
2. Extract key findings, methods, and data
3. Organize findings as bullet points in your outline
4. Then convert the outline to full paragraphs in Stage 2

This two-stage process ensures you:

- Gather and organize information systematically
- Create logical structure before writing
- Produce polished, publication-ready prose
- Maintain focus on the narrative flow

---

## The Three-Phase Writing Cycle

The two-stage outline → prose conversion above sits inside a larger three-phase cycle. Treat each phase as a strictly separate cognitive task to avoid creative paralysis.

### Phase 1 — Prewriting (largest time investment)

- Gather information; organize ideas into a sequential roadmap.
- Brainstorm away from the keyboard (commute, exercise, walks).
- Establish the central thesis in one sentence (consider Plan Mode — see `socratic_planning_protocol.md`).
- Choose the venue and confirm format requirements.

Most writing problems are upstream: an unclear thesis or weak structure cannot be fixed at the sentence level. Time spent here saves time downstream.

### Phase 2 — Drafting (silence the inner critic)

- Goal: get ideas down in logical order using complete sentences.
- Do **not** revise while drafting. No polishing, no rearranging, no fact-checking interruptions.
- Apply the two-stage outline → prose conversion documented above in this file.
- Use the writing order in §"Section-Writing Order" below.

### Phase 3 — Revision (more time than drafting)

Apply the **revision hierarchy** (top-down) from `../../shared/references/prose_standards.md` §10.1:

1. Structure — does the logical flow hold?
2. Paragraphs — single idea each? C-C-C intact?
3. Sentences — concise? Voice appropriate? Nominalizations gone?
4. Words — terminology consistent (Banana Rule)? Numbers checked? Hedging calibrated?

Then run the **Five Pre-Submission Tests** (R1–R5) before submission. See `prose_standards.md` §10.3.

Sources: Sainani 4.2, 4.4, 4.5; D2 §VIII; D4 pass 5.

---

## Section-Writing Order

Do not write the manuscript top-to-bottom. Establish the figures and tables first; let the data dictate the story; then build the surrounding prose around the established narrative.

| Order | What to write | Why |
|---|---|---|
| 1 | **Figures and Tables** | These are the primary evidence and constrain everything that follows. Designing them first reveals what the story actually is. |
| 2 | **Results** | Now that the figures are stable, narrate them in the order of the Introduction's objectives (not in the order data were collected). |
| 3 | **Methods** | With the Results fixed, document precisely how each result was produced. Methods written before Results often miss critical steps revealed only during analysis. |
| 4 | **Introduction** | Frame the gap *after* the story is fully clear. Otherwise the Introduction sets up a story the data cannot tell. |
| 5 | **Discussion** | Interpretation, comparison to prior work, limitations, and implications — all easier when the full Results and Introduction are stable. |
| 6 | **Abstract** | Compress the finished story; an abstract drafted earlier almost always misrepresents the final paper. |
| 7 | **Title** | Distill the central finding into 10–15 words after the abstract crystallizes the message. |

Sources: Sainani 5.1; D2 §II; D4 pass 5.

---

## Cross-References

- Universal voice/style/revision standards: `../../shared/references/prose_standards.md`
- Pre-drafting Socratic protocol (Plan Mode): `socratic_planning_protocol.md`
- IMRAD architecture per section: `imrad_structure.md`
- Citation hygiene during drafting: `citation_styles.md`
- Figure-first design: `figures_tables.md`
