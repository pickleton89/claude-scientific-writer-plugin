---
name: scholar-evaluation
version: 2.1.0
description: "Systematic evaluation of scholarly work using the ScholarEval framework with quantitative scoring and structured feedback"
when_to_use: "Evaluating research papers for quality, assessing literature review comprehensiveness, reviewing methodology design, scoring data analysis approaches, providing structured feedback on academic work, benchmarking research quality"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Scholar Evaluation

<overview>
Apply the ScholarEval framework to systematically evaluate scholarly and research work. This skill provides structured evaluation methodology based on peer-reviewed research assessment criteria, enabling comprehensive analysis of academic papers, research proposals, literature reviews, and scholarly writing across 8 quality dimensions with quantitative scoring.
</overview>

<prerequisites>
## Prerequisites

**Required:** None - core evaluation workflow uses only standard tools.

**For automated scoring (optional):**
```bash
# Python 3.7+ with standard library only
python {baseDir}/scripts/calculate_scores.py --interactive
```
</prerequisites>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Evaluating research papers for quality and rigor
- Assessing literature review comprehensiveness
- Reviewing research methodology design
- Scoring data analysis approaches
- Providing structured feedback on academic work
- Benchmarking research quality against standards
- Assessing publication readiness for target venues

Do NOT use this skill when:
- Conducting a full peer review with revision recommendations → use `peer-review`
- Evaluating an individual scholar's career metrics → use bibliometric tools
- Writing or improving the paper itself → use `scientific-writing`
- Assessing statistical methods specifically → use `statistical-analysis`
</when_to_use>

<decision_framework>
## Evaluation Type Selection

| Work Type | Scope | Applicable Dimensions | Est. Time |
|-----------|-------|----------------------|-----------|
| Full research paper | Comprehensive | All 8 dimensions | 45-60 min |
| Research proposal | Targeted | 1-3, 4 (partial), 8 | 30-45 min |
| Literature review | Targeted | 2, 7, 8 | 20-30 min |
| Thesis chapter | Comprehensive | All 8 dimensions | 45-60 min |
| Conference abstract | Quick | 1, 5, 7 | 10-15 min |
| Methods section only | Targeted | 3, 4 | 15-20 min |

## Evaluation Depth Decision

```
What is the evaluation purpose?
│
├─ Publication readiness assessment?
│  └─→ Comprehensive evaluation (all 8 dimensions, full scoring)
│
├─ Quick quality check?
│  └─→ Rapid assessment (dimensions 1, 3, 5, 7 only)
│
├─ Specific aspect review?
│  │
│  ├─ Methodology concerns → Dimensions 3, 4
│  ├─ Writing quality → Dimensions 7, 8
│  ├─ Contribution assessment → Dimensions 1, 2, 5
│  └─ Data/analysis review → Dimensions 4, 5, 6
│
└─ Developmental feedback (student work)?
   └─→ Educational mode (constructive framing, prioritized recommendations)
```

</decision_framework>

<workflow>
## Evaluation Workflow

### Stage 1: Scope Definition

**Objective:** Identify work type and establish evaluation parameters

**Steps:**
1. Identify document type (paper, proposal, review, thesis, abstract)
2. Determine evaluation scope (comprehensive vs. targeted)
3. Select applicable dimensions from the 8-dimension framework
4. Establish context (stage of development, target venue, discipline)

**Exit Criteria:**
- [ ] Work type identified
- [ ] Evaluation scope determined (comprehensive/targeted/quick)
- [ ] Applicable dimensions listed (minimum 3)
- [ ] Context factors documented

---

### Stage 2: Dimension-Based Assessment

**Objective:** Systematically evaluate each applicable dimension

**Steps:**
1. For each applicable dimension:
   - Read relevant sections of the document
   - Assess against dimension-specific criteria (see rubric below)
   - Identify 2-3 specific strengths
   - Identify 2-3 specific weaknesses
   - Assign quantitative score (1-5 scale)
2. Document evidence for each assessment with page/section references

**The 8 Evaluation Dimensions:**

| # | Dimension | Key Criteria |
|---|-----------|--------------|
| 1 | Problem Formulation | Clarity, significance, novelty, feasibility |
| 2 | Literature Review | Comprehensiveness, synthesis, gap identification |
| 3 | Methodology | Appropriateness, rigor, reproducibility, ethics |
| 4 | Data Collection | Quality, sample size, procedures, reliability |
| 5 | Analysis | Method appropriateness, rigor, coherence |
| 6 | Results | Clarity, statistical rigor, visualization |
| 7 | Writing | Organization, clarity, tone, accessibility |
| 8 | Citations | Completeness, quality, accuracy, balance |

**Exit Criteria:**
- [ ] All applicable dimensions assessed
- [ ] Each dimension has 2+ strengths documented
- [ ] Each dimension has 2+ weaknesses documented
- [ ] All scores assigned with evidence

---

### Stage 3: Quantitative Scoring

**Objective:** Calculate aggregate scores and quality ratings

**Steps:**
1. Apply dimension scores using the 5-point rubric
2. Calculate weighted aggregate score (use automated calculator for precision):
   ```bash
   python {baseDir}/scripts/calculate_scores.py --scores scores.json --output report.txt
   ```
   Or run interactively: `python {baseDir}/scripts/calculate_scores.py --interactive`
3. Determine overall quality tier
4. Compare against publication thresholds

**Scoring Rubric:**

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Exemplary quality, publishable in top venues, no significant issues |
| 4 | Good | Strong quality, minor improvements needed, suitable for most venues |
| 3 | Adequate | Acceptable quality, notable areas for improvement, may need revision |
| 2 | Needs Work | Significant revisions required, major issues in this dimension |
| 1 | Poor | Fundamental issues, requires major revision or reconceptualization |

**Dimension Weights (for aggregate score):**

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Problem Formulation | 15% | Foundation of research value |
| Literature Review | 15% | Context and positioning |
| Methodology | 20% | Core scientific rigor |
| Data Collection | 10% | Evidence quality |
| Analysis | 15% | Interpretation validity |
| Results | 10% | Findings significance |
| Writing | 10% | Communication quality |
| Citations | 5% | Scholarly conventions |

**Quality Tiers:**

| Aggregate Score | Tier | Interpretation |
|-----------------|------|----------------|
| 4.5-5.0 | A | Publication-ready for top venues |
| 4.0-4.4 | B | Strong, minor revisions needed |
| 3.5-3.9 | C | Acceptable, moderate revisions |
| 3.0-3.4 | D | Significant revisions required |
| <3.0 | F | Major reconceptualization needed |

**Exit Criteria:**
- [ ] All dimension scores recorded (1-5 scale)
- [ ] Weighted aggregate calculated
- [ ] Quality tier assigned (A-F)
- [ ] Publication readiness assessed

---

### Stage 4: Synthesis and Recommendations

**Objective:** Integrate findings into actionable feedback

**Steps:**
1. Identify 3-5 major strengths across dimensions
2. Identify 3-5 critical weaknesses requiring attention
3. Rank recommendations by impact and feasibility
4. Assess publication readiness for target venue

**Recommendation Priority Matrix:**

| Impact | Effort | Priority |
|--------|--------|----------|
| High | Low | P1 - Address immediately |
| High | High | P2 - Plan for revision |
| Low | Low | P3 - Quick wins |
| Low | High | P4 - Defer or skip |

**Exit Criteria:**
- [ ] 3-5 major strengths identified
- [ ] 3-5 critical weaknesses identified
- [ ] Recommendations prioritized (P1-P4)
- [ ] Publication readiness statement drafted

---

### Stage 5: Report Generation

**Objective:** Produce structured evaluation deliverable

**Steps:**
1. Select output format based on purpose
2. Generate evaluation report using template
3. Include specific evidence and page references
4. Provide constructive, actionable language

**Output Format Options:**

| Format | Use Case | Sections |
|--------|----------|----------|
| Full Report | Comprehensive review | All sections, detailed |
| Executive Summary | Quick overview | Scores, top findings, recommendations |
| Annotated Comments | Line-by-line feedback | Mapped to specific locations |
| Comparative Analysis | Benchmarking | Against standards or other work |

**Exit Criteria:**
- [ ] Format selected appropriate to purpose
- [ ] All required sections completed
- [ ] Evidence cited with specific references
- [ ] Language is constructive and actionable

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Dimensions assessed | 3 | 6 | 8 |
| Strengths per dimension | 1 | 2 | 3+ |
| Weaknesses per dimension | 1 | 2 | 3+ |
| Specific page/section refs | 50% | 80% | 100% |
| Recommendations provided | 3 | 5 | 8+ |

**Completion Checklist:**
- [ ] All applicable dimensions assessed with scores
- [ ] Aggregate score calculated with quality tier
- [ ] 80%+ of assessments include specific evidence
- [ ] Recommendations prioritized by impact/effort
- [ ] Report uses constructive, actionable language
- [ ] Publication readiness explicitly addressed

</success_criteria>

<scope>
## Scope

**In Scope:**
- Evaluation of scholarly work quality
- Quantitative scoring across 8 dimensions
- Structured feedback generation
- Publication readiness assessment
- Comparative benchmarking against standards
- Developmental feedback for students

**Out of Scope** (use specialized resources):
- Full peer review with revision requirements → use `peer-review`
- Career/scholar bibliometric evaluation → external tools (Google Scholar, Scopus)
- Statistical method validation → use `statistical-analysis`
- Writing improvement → use `scientific-writing`
- Domain-specific expertise → consult field experts

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Subjective Scoring

**Anti-pattern:**
```
"The methodology seems okay, I'll give it a 3."
```

**Solution:**
```
"Methodology score: 3
- Strengths: Clear experimental design (p.5), reproducible protocol (p.7)
- Weaknesses: Sample size justification missing (p.6), no power analysis
- Evidence: Methods section pp.5-8"
```

---

### 2. Vague Recommendations

**Anti-pattern:**
```
"The literature review needs improvement."
```

**Solution:**
```
"P1 Recommendation: Expand literature review to include:
- Recent work by Smith et al. (2023) on [topic]
- Meta-analyses from the past 3 years
- Specific gap: No coverage of [subfield] (pp.3-4)"
```

---

### 3. Unbalanced Feedback

**Anti-pattern:**
Listing only weaknesses without acknowledging strengths

**Solution:**
For each dimension, document both strengths AND weaknesses. Even weak sections have salvageable elements. Example: "While the analysis lacks statistical rigor (weakness), the visual presentation of results is clear and effective (strength)."

---

### 4. Context-Blind Evaluation

**Anti-pattern:**
Applying top-tier journal standards to a student's first draft

**Solution:**
Calibrate expectations to:
- Stage of development (early draft vs. final submission)
- Purpose (class assignment vs. publication)
- Venue (student journal vs. Nature)
- Experience level (novice vs. senior researcher)

---

### 5. Missing Evidence

**Anti-pattern:**
```
"The writing quality is poor."
```

**Solution:**
```
"Writing quality (Score: 2)
- Issue 1: Passive voice overuse (examples on pp.3, 7, 12)
- Issue 2: Paragraph transitions missing (pp.5-6)
- Issue 3: Technical terms undefined (see 'bifurcation' p.4)"
```

</anti_patterns>

<templates>
## Output Templates

### Template 1: Executive Summary

```markdown
# Scholar Evaluation: {{PAPER_TITLE}}

**Evaluation Date:** {{DATE}}
**Evaluator:** Claude (ScholarEval Framework)
**Scope:** {{COMPREHENSIVE/TARGETED}}

## Overall Assessment

| Metric | Value |
|--------|-------|
| Aggregate Score | {{X.X}}/5.0 |
| Quality Tier | {{A-F}} |
| Publication Readiness | {{READY/REVISE/NOT READY}} |

## Dimension Scores

| Dimension | Score | Key Finding |
|-----------|-------|-------------|
| Problem Formulation | {{1-5}} | {{One-line summary}} |
| Literature Review | {{1-5}} | {{One-line summary}} |
| Methodology | {{1-5}} | {{One-line summary}} |
| Data Collection | {{1-5}} | {{One-line summary}} |
| Analysis | {{1-5}} | {{One-line summary}} |
| Results | {{1-5}} | {{One-line summary}} |
| Writing | {{1-5}} | {{One-line summary}} |
| Citations | {{1-5}} | {{One-line summary}} |

## Top 3 Strengths
1. {{Strength with evidence}}
2. {{Strength with evidence}}
3. {{Strength with evidence}}

## Priority Recommendations
1. **P1:** {{Recommendation}} (Impact: High, Effort: {{Low/High}})
2. **P2:** {{Recommendation}} (Impact: High, Effort: {{Low/High}})
3. **P3:** {{Recommendation}} (Impact: {{Low/High}}, Effort: Low)
```

### Template 2: Detailed Dimension Report

```markdown
## Dimension {{#}}: {{DIMENSION_NAME}}

**Score:** {{1-5}}/5 ({{RATING}})

### Strengths
1. {{Specific strength with page reference}}
2. {{Specific strength with page reference}}

### Weaknesses
1. {{Specific weakness with page reference}}
2. {{Specific weakness with page reference}}

### Recommendations
- {{Actionable recommendation}}
- {{Actionable recommendation}}

### Evidence
- {{Quote or specific reference from document}}
```

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `peer-review` | Use for full peer review with revision requirements; includes critical analysis frameworks (evidence evaluation, bias detection, logical fallacies) |
| `scientific-writing` | Use to improve writing after identifying weaknesses via scholar-evaluation |
| `statistical-analysis` | Use for detailed statistical method review when dimension 5 scores low |
| `literature-review` | Use when dimension 2 (Literature Review) requires expansion |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/references/evaluation_framework.md` | Detailed criteria and rubrics for each dimension |
| `{baseDir}/references/expert_guide.md` | Expert synthesis on evaluation principles and failure modes |
| `{baseDir}/scripts/calculate_scores.py` | Automated score calculation with weighted averaging |

## Citation

This skill is based on the ScholarEval framework:

**Moussa, H. N., et al. (2025).** _ScholarEval: Research Idea Evaluation Grounded in Literature_. arXiv:2510.16234. [https://arxiv.org/abs/2510.16234](https://arxiv.org/abs/2510.16234)

</references>
