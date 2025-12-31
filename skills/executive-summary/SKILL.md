---
name: executive-summary
version: 2.0.1
description: "Generates concise, action-oriented executive summaries for decision-makers from reports, proposals, or project plans. Use when creating summaries for stakeholders, board presentations, grant applications, or any document requiring a persuasive standalone overview with optional visual summary."
allowed-tools: Read, Write, Edit, Bash
when_to_use: |
  - Creating a summary for busy decision-makers who won't read the full document
  - Summarizing research reports, proposals, or project plans for stakeholders
  - Writing grant application summaries or board presentation overviews
  - Generating a standalone document that conveys key findings and recommendations
  - Adding a visual summary or graphical abstract to complement text
  - Distilling lengthy technical documents into actionable insights
---

# Executive Summary

## Objective

Generate concise, persuasive executive summaries that enable decision-makers to understand key findings and take action without reading the full document. Apply the Pyramid Principle: lead with conclusions, support with evidence, end with a clear call to action.

**Why this matters:** Decision-makers typically have 2-3 minutes to evaluate a document. A well-structured executive summary captures attention, builds confidence in findings, and drives action—while a poorly structured one gets ignored.

---

## Quick Start

For straightforward summarization tasks, follow this minimal workflow:

1. **Read the source document** using the Read tool
2. **Extract 3-5 key findings** with quantified results
3. **Identify the primary recommendation**—what action should the reader take?
4. **Draft using the five-component template** (see below)
5. **Validate** by running `python3 {baseDir}/scripts/validate_summary.py output.md`

---

## Core Constraints

Apply these constraints to every executive summary:

| Constraint | Requirement | Rationale |
|------------|-------------|-----------|
| **Length** | Maximum 1-2 pages OR ~10% of source document | Busy readers abandon long summaries |
| **Timing** | Write AFTER the full document is complete | Cannot summarize incomplete work |
| **Independence** | Must stand alone—never reference "Section 3.2" | Reader may never see the main document |
| **Audience** | Intelligent non-specialists who need to decide | Avoid jargon; explain technical terms |

---

## The Pyramid Principle

Structure every executive summary with **conclusion first**, then supporting evidence. The reader must grasp the essential message in the first paragraph.

**Why this structure:** Research shows readers form opinions in the first 30 seconds. Front-loading the conclusion ensures your key message lands even if the reader stops early.

### Five-Component Structure

Include all five components in this order:

| # | Component | Purpose | What to Write |
|---|-----------|---------|---------------|
| 1 | **Hook/Problem** | Capture attention | One sentence stating the specific problem with a compelling statistic |
| 2 | **Solution/Objective** | Frame the approach | 1-2 sentences on methodology or proposed solution |
| 3 | **Key Findings** | Provide evidence | Exactly 3-5 quantified insights (never more) |
| 4 | **Value/Impact** | Answer "so what?" | ROI, benefits, or broader significance |
| 5 | **Call to Action** | Drive decision | Specific next step with owner and timeline |

### Template

Use this exact structure for every executive summary:

```markdown
## Executive Summary

[HOOK: One sentence with specific problem/opportunity + key statistic]

[SOLUTION: 1-2 sentences describing methodology or approach]

**Key Findings:**
1. [Finding with number]: [quantified result]
2. [Finding with number]: [quantified result]
3. [Finding with number]: [quantified result]

[VALUE: 2-3 sentences on significance, ROI, or implications]

**Recommendation:** [Specific action] by [owner] by [date/timeline].
```

---

## Complete Examples

For complete examples demonstrating the five-component structure, including:
- Remote Work Productivity Analysis (detailed walkthrough)
- Market Expansion Proposal
- Anti-example showing common mistakes
- Reusable template

See `references/examples.md`.

---

## Writing Rules

Apply these rules to transform technical content into accessible prose:

### 1. One Idea Per Paragraph

**Rule:** Each paragraph addresses exactly one main point.

**Test:** Can you summarize the paragraph in one sentence? If not, split it.

**Why:** Multiple ideas per paragraph force re-reading and slow comprehension.

### 2. Active Voice

**Rule:** Use direct, active constructions. The actor should perform the action.

| Write This (Active) | Not This (Passive) |
|---------------------|-------------------|
| "We measured response times..." | "Response times were measured..." |
| "The analysis shows..." | "It was determined that..." |
| "The committee recommends..." | "A recommendation was made..." |

**Why:** Active voice is 20-25% shorter and assigns clear accountability.

### 3. Context-Content-Conclusion (C-C-C)

**Rule:** Structure each paragraph with:
1. **Context**: Topic sentence (what this paragraph addresses)
2. **Content**: Evidence, data, or argument
3. **Conclusion**: Take-home message connecting to main thesis

**Why:** This structure guides readers through complex information without confusion.

### 4. Translate Jargon

**Rule:** Replace technical terms with plain language. If a technical term is essential, define it immediately.

| Technical | Plain Language |
|-----------|----------------|
| "p-value < 0.001" | "statistically significant (p<0.001), meaning unlikely due to chance" |
| "RNA-seq analysis" | "gene activity analysis using RNA sequencing" |
| "ROI of 340%" | "return of $3.40 for every $1 invested" |

**Why:** Decision-makers span domains. Undefined jargon creates barriers to understanding and trust.

---

## Visualization Integration

Include a visual summary when the executive summary will be:
- Presented to diverse stakeholders (varying technical backgrounds)
- Used in slide decks or board materials
- Distributed as a standalone document via email

### When to Add Visuals

| Scenario | Include Visual? |
|----------|----------------|
| Board presentation | Yes—graphical abstract |
| Email to executives | Yes—single summary chart |
| Internal team memo | Optional |
| 1-page summary | Only if space allows |

### Technical Requirements

All visuals must meet these standards:

| Requirement | Standard | Rationale |
|-------------|----------|-----------|
| **Format** | Vector only (PDF, SVG) | Scales without pixelation |
| **Colors** | No red/green; use blue/orange or Viridis | 8% of men are red-green colorblind |
| **Chart type** | Bar charts for comparisons | Pie charts distort perception |
| **Effects** | No 3D, shadows, or gradients | "Chartjunk" obscures data |
| **Captions** | Self-contained | Reader may see figure without text |
| **Fonts** | Sans-serif, ≥8pt | Legibility on screens and print |

For detailed visualization guidance, see `references/visualization_guidelines.md`.

---

## Workflow

### Standard Process

Execute these steps in order:

**Step 1: Verify Prerequisites**
```
Read the source document.
Confirm it is complete—do not summarize incomplete drafts.
If incomplete, STOP and notify the user: "The source document appears incomplete.
Please provide the final version before I generate the executive summary."
```

**Step 2: Extract Key Content**
```
Identify the 3-5 most important findings.
Each finding MUST have a quantified result (number, percentage, dollar amount).
If findings lack quantification, note this gap for the user.
```

**Step 3: Determine the Recommendation**
```
Identify what action the reader should take.
The recommendation must specify: WHAT, WHO, and WHEN.
If no clear action emerges, ask the user: "What decision should this summary support?"
```

**Step 4: Draft the Summary**
```
Use the five-component template exactly.
Write in active voice.
Ensure total length is ≤10% of source document.
```

**Step 5: Validate**
```
Run the validation script:
python3 {baseDir}/scripts/validate_summary.py <output_file>

Review the output for:
- PASS: All criteria met
- WARN: Minor issues to consider
- FAIL: Must fix before delivering
```

**Step 6: Revise if Needed**
```
If validation returns FAIL or WARN:
1. Address each issue identified
2. Re-run validation
3. Repeat until all checks pass
```

**Step 7: Deliver**
```
Present the validated executive summary to the user.
Include the validation results as confirmation of quality.
```

### Validation Checklist

Before delivering, confirm all criteria are met:

- [ ] Opens with conclusion/recommendation (Pyramid Principle)
- [ ] Contains all five components in correct order
- [ ] Length is ≤10% of source OR ≤2 pages
- [ ] Stands alone—no references to "Section X" or "see above"
- [ ] Active voice ≥75% of sentences
- [ ] All technical terms defined or translated
- [ ] All findings are quantified (no vague claims)
- [ ] Call to action specifies WHAT + WHO + WHEN

---

## Error Handling

Handle these common scenarios:

### Source Document Issues

| Scenario | Detection | Response |
|----------|-----------|----------|
| **Document incomplete** | Missing sections, "TBD" markers, blank areas | STOP. Notify user: "Source document appears incomplete. Please provide final version." |
| **Document too short** | Source < 500 words | WARN user: "Source is brief. Executive summary may be as long as the original. Consider whether a summary is needed." |
| **No quantified findings** | Findings lack numbers | Extract what exists. WARN user: "Findings lack quantification. Summary will be less compelling. Can you provide metrics?" |

### Content Challenges

| Scenario | Detection | Response |
|----------|-----------|----------|
| **Fewer than 3 findings** | Cannot identify 3+ distinct insights | Include what exists. Note: "Only [N] key findings identified. Consider whether source contains sufficient content." |
| **No clear recommendation** | Cannot determine action | Ask user: "What decision should this summary support? I need a clear action to recommend." |
| **Multiple competing recommendations** | Source suggests conflicting actions | Present options to user: "Source contains multiple potential recommendations. Which should I prioritize?" |

### Output Constraints

| Scenario | Detection | Response |
|----------|-----------|----------|
| **User requests longer summary** | Request exceeds 10% guideline | WARN: "Extended summaries reduce effectiveness. Recommend staying under [X] words. Proceed with longer version?" |
| **User requests bullet-only format** | No prose requested | Deliver bullets but WARN: "Bullet-only format may reduce persuasive impact. Consider adding narrative framing." |

---

## Quality Thresholds

### Writing Metrics

| Metric | Fail | Minimum | Target | Excellent |
|--------|------|---------|--------|-----------|
| Sentence length (avg) | >30 words | ≤25 words | 15-20 words | 12-18 words |
| Passive voice | >50% | ≤40% | ≤25% | ≤15% |
| Undefined jargon | >5 terms | ≤5 terms | All defined | 0 jargon |
| Call to action | Missing | Present | Specific | Specific + Owner + Timeline |
| Quantified findings | 0-1 | 2 | 3-4 | 5 with comparisons |

### Validation Script

Run quality checks using:

```bash
python3 {baseDir}/scripts/validate_summary.py <markdown_file>
```

The script checks:
- Word count and length ratio
- Passive voice percentage
- Component presence (all 5 required)
- Quantification in findings
- Call-to-action specificity

---

## Common Pitfalls

Avoid these errors that reduce executive summary effectiveness:

| Pitfall | Why It Fails | Fix |
|---------|--------------|-----|
| **Burying the lead** | Reader may stop before reaching conclusion | Move recommendation to first paragraph |
| **Data dump** | Overwhelms reader; obscures key points | Limit to 3-5 findings; move details to appendix |
| **Vague language** | "Improvements were made" lacks credibility | Quantify: "Efficiency improved 34%" |
| **Passive hedging** | "It could be considered..." sounds uncertain | Be direct: "We recommend..." |
| **Referencing main doc** | "As shown in Section 3.2..." | Restate the point—summary must stand alone |
| **Missing action** | Reader finishes without knowing next step | Always end with specific call to action |
| **Wall of text** | No visual breaks reduce readability | Use headers, bullets, bold for key terms |

---

## Cross-References

### Uses (Input From)

| Skill | Relationship |
|-------|-------------|
| `scientific-writing` | Source manuscripts and reports to summarize |
| `literature-review` | Synthesized background for context |
| `statistical-analysis` | Key statistical findings to highlight |

### Feeds (Output To)

| Skill | Relationship |
|-------|-------------|
| `visual-design` | Graphical abstract and visual summary creation |
| `plotting-libraries` | Data visualizations for findings |
| `markdown-to-pdf` | Branded PDF output with Oligon styling |
| `scientific-slides` | Presentation-ready summary slides |
| `document-skills/docx` | Word format for stakeholder distribution |

### Related

| Skill | Relationship |
|-------|-------------|
| `scientific-schematics` | Study design diagrams for visual summaries |
| `generate-image` | Infographics and conceptual illustrations |

---

## References

**Validation Scripts:**
- `scripts/validate_summary.py` - Automated quality checks

**Reference Documents:**
- `references/visualization_guidelines.md` - Visual summary best practices

**Related Skills:**
- `../visual-design/SKILL.md` - Design philosophy for scientific visuals
- `../plotting-libraries/SKILL.md` - Python plotting implementations
- `../scientific-writing/SKILL.md` - Abstract vs. executive summary distinction
