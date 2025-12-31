# Example Workflow: Review Article

This document walks through the complete summarization workflow for a review article using the chunked subagent pipeline.

---

## Scenario

**Input**: A 32-page review article on aptamer therapeutics
**Article Type**: Review Article
**Processing Mode**: Chunked (>12 pages)

---

## Key Differences from General Research

Review articles use a specialized subagent sequence:

| Order | Agent | Focus |
|-------|-------|-------|
| 1 | Overview Agent | Scope, objectives, key conclusions |
| 2 | Evidence Agent | Core arguments, evidence synthesis |
| 3 | Landscape Agent | Field overview, frameworks, trends |
| 4 | Critique Agent | Gaps, biases, methodological concerns |
| 5 | References Agent | Reference quality, seminal works |
| 6 | Synthesis Agent | Final integration |

---

## Phase 0: Initialization

```
User: Please summarize this review article
[Uploads johnson2024_aptamer_therapeutics_review.pdf]

Claude: I've received your paper. Let me analyze it...

This paper has 32 pages. Using Chunked processing mode.

Processing: johnson2024_aptamer_therapeutics_review.pdf (32 pages)
Mode: Chunked subagent pipeline
```

---

## Phase 1a: Article Type Selection

```
Claude: What type of article is this?

1. General research paper
2. Review article / meta-analysis
3. Computational biology / bioinformatics
4. Cell & molecular biology

User: 2
```

---

## Phase 1b: Section Detection (Review-Specific)

For review articles, Claude looks for different section markers:

```json
{
  "abstract": {"start": 1, "end": 1},
  "introduction": {"start": 1, "end": 3},
  "body_sections": [
    {"title": "Aptamer Selection Technologies", "start": 4, "end": 10},
    {"title": "Clinical Applications", "start": 11, "end": 18},
    {"title": "Delivery Challenges", "start": 19, "end": 24},
    {"title": "Future Perspectives", "start": 25, "end": 28}
  ],
  "conclusions": {"start": 28, "end": 29},
  "references": {"start": 30, "end": 32}
}
```

---

## Phase 1c: Skeleton Creation (Review Template)

The skeleton uses review-specific sections:

```markdown
## 7. Reference Mining & Meta-Assessment

<!-- SECTION: article_specific PENDING -->

### Seminal Works Cited

<!-- SUBSECTION: seminal_works PENDING -->

### Citation Patterns

<!-- SUBSECTION: citation_patterns PENDING -->

### Reference Quality Assessment

<!-- SUBSECTION: reference_quality PENDING -->
```

---

## Phase 1d: Subagent Pipeline (Review Sequence)

### Agent 1: Overview Agent

```
[■□□□□□] Step 1/6: Extracting overview...

Reading pages 1-3 (Abstract + Introduction)
Writing to: executive_summary, scope, objectives sections

Note: For reviews, Overview Agent extracts:
- Review scope and boundaries
- Stated objectives
- Key conclusions preview
```

### Agent 2: Evidence Agent

```
[■■□□□□] Step 2/6: Synthesizing evidence...

Reading pages 4-24 (Core content sections)
Writing to: core_arguments, evidence_synthesis sections

Note: Evidence Agent for reviews:
- Identifies main arguments/themes
- Tracks how evidence is synthesized
- Notes meta-analytic elements (if present)
```

### Agent 3: Landscape Agent

```
[■■■□□□] Step 3/6: Mapping field landscape...

Reading pages 4-10, 25-28 (Overview + Future sections)
Writing to: field_landscape, frameworks, trends sections

Note: Landscape Agent identifies:
- Key players and research groups
- Dominant paradigms
- Emerging vs established areas
- Historical progression
```

### Agent 4: Critique Agent

```
[■■■■□□] Step 4/6: Critical analysis...

Reading pages 25-29 (Conclusions + Discussion)
Writing to: gaps, biases, methodological_concerns sections

Note: For reviews, Critique Agent assesses:
- Completeness of literature coverage
- Potential selection bias
- Balance of perspectives
- Methodological rigor of cited studies
```

### Agent 5: References Agent

```
[■■■■■□] Step 5/6: Analyzing references...

Reading pages 30-32 (References) + scanning citations in text
Writing to: seminal_works, citation_patterns, reference_quality sections

Note: References Agent unique to reviews:
- Identifies most-cited foundational papers
- Assesses recency of references
- Notes geographic/institutional diversity
- Flags potential citation bias
```

### Agent 6: Synthesis Agent

```
[■■■■■■] Step 6/6: Generating synthesis...

Reading: summary file only (no PDF)
Writing to: insights, takeaways, synthesis sections
```

---

## Example Output Sections (Review-Specific)

### Reference Mining Section

```markdown
## 7. Reference Mining & Meta-Assessment

### Seminal Works Cited

| Work | Citations in Text | Contribution |
|------|-------------------|--------------|
| Tuerk & Gold 1990 | 12 | Original SELEX methodology |
| Ellington & Szostak 1990 | 11 | Independent aptamer discovery |
| Ng et al. 2006 | 8 | Pegaptanib (Macugen) FDA approval |
| Zhou & Rossi 2017 | 7 | Aptamer-siRNA chimeras |

### Citation Patterns

- **Total references**: 187
- **Recency**: 45% from last 5 years; 78% from last 10 years
- **Self-citation rate**: 8% (within normal range)
- **Geographic distribution**: US (42%), China (23%), Europe (28%), Other (7%)

### Reference Quality Assessment

**Strengths:**
- Comprehensive coverage of clinical trials (23 trials cited)
- Balanced representation of competing approaches
- Includes negative results and failed trials

**Gaps:**
- Limited coverage of non-English literature
- Few citations from industry/patent literature
- Missing recent preprints (2024)
```

### Field Landscape Section

```markdown
## 6. Field Landscape

### Dominant Paradigms

1. **SELEX-based selection** remains gold standard
2. **Chemical modification** for stability (2'-F, 2'-OMe, PS backbone)
3. **Nanoparticle conjugation** emerging for delivery

### Key Research Groups

| Group | Institution | Focus Area |
|-------|-------------|------------|
| Rossi Lab | City of Hope | siRNA delivery |
| Sullenger Lab | Duke | Anticoagulation |
| Tan Lab | U Florida | Cancer diagnostics |

### Emerging vs Established

| Established | Emerging |
|-------------|----------|
| Anti-thrombin aptamers | Cell-SELEX for personalized medicine |
| Diagnostic biosensors | AI-guided aptamer design |
| Pegaptanib (ophthalmology) | Aptamer-drug conjugates (ApDCs) |
```

---

## Visual Output Considerations for Reviews

When generating visual outputs for review articles:

### HTML Report

- **Navigation**: Reflects thematic sections, not methods/results
- **Callouts**: Highlight key debates and controversies
- **Tables**: Emphasize comparison matrices and timelines

### SVG Infographic

- **Timeline component**: Show field evolution
- **Landscape map**: Visual representation of research areas
- **Gap analysis**: Highlight under-explored areas

---

## Complete File Outputs

```
johnson2024_aptamer_therapeutics_review.pdf         (original)
johnson2024_aptamer_therapeutics_review_summary.md  (markdown)
johnson2024_aptamer_therapeutics_review_report.html (HTML report)
```

---

## Common Issues with Review Articles

### Long papers (>40 pages)

```
Claude: This review is 48 pages. Adjusting chunking strategy...
- Sampling representative pages from each major section
- Focus on introduction, conclusions, and key tables
```

### Complex nested structure

```
Claude: Detected 12 major sections with 34 subsections.
Using section headers to guide agent assignments.
```

### Heavy figure/table content

```
Claude: This review contains 8 figures and 12 tables.
Key Figures section will prioritize summary/overview figures.
```
