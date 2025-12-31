# Markdown Summary Prompt

Generate a structured markdown summary of the research paper following this exact format.

## Preservation Priorities (Non-Negotiable)

These elements must appear exactly as stated in the paper:

1. **Quantitative results**: All numerical findings, p-values, confidence intervals, effect sizes, sample sizes, fold-changes
2. **Methodology specifics**: Experimental design, model systems, key parameters, datasets, statistical tests, controls
3. **Causal/mechanistic claims**: The logic chain from evidence to conclusion
4. **Novel contributions**: Distinguish what is new versus background
5. **Stated limitations**: Authors' own caveats
6. **Domain terminology**: Use exact technical terms; do not paraphrase

## Condensation Targets

Compress these elements:
- Background/introduction context (unless framing novel approach)
- Rhetorical transitions and redundant explanations
- General methodological boilerplate
- Repeated statements across Results/Discussion

## Output Format

```markdown
### PAPER METADATA
| Field | Value |
|-------|-------|
| **Title** | [Full title] |
| **Authors** | [First author et al.] |
| **Journal / Year** | [Journal name, year] |
| **DOI** | [DOI if available] |
| **Article Type** | [Primary Research / Review / Methods / Meta-analysis / Case Report] |

---

### OVERVIEW
[1-2 sentences maximum: What question? What approach? What main finding?]

---

### KEY FINDINGS

- **Finding 1**: [Description]
  - `p = X.XX` | `n = X` | `95% CI: X–X` | `effect size: X`

- **Finding 2**: [Description]
  - [relevant statistics]

- **Finding 3**: [Description]
  - [relevant statistics]

[Continue for all major findings. Include ALL quantitative results.]

---

### METHODS SUMMARY

| Aspect | Details |
|--------|---------|
| **Study Design** | [RCT, cohort, case-control, in vitro, preclinical, etc.] |
| **Model System** | [Cell lines, animal models, patient cohorts — be specific] |
| **Sample Size** | [n per group, total N] |
| **Key Techniques** | [Assays, sequencing platforms, imaging modalities] |
| **Statistical Analysis** | [Tests used, multiple comparison corrections] |
| **Key Parameters** | [Doses, timepoints, thresholds, cutoffs] |

---

### LIMITATIONS & CAVEATS

**Author-stated limitations:**
- [Limitation 1 — as stated in paper]
- [Limitation 2]

**Additional considerations:**
- [Obvious gaps, generalizability concerns, methodological issues not acknowledged]

---

### IMPLICATIONS & FUTURE DIRECTIONS

[What does this mean for the field? Future work proposed? Open questions?]

---

### VERIFICATION CHECKLIST

- [ ] All numerical results from Results/Figures included
- [ ] Statistical test details preserved (p-values, CIs, effect sizes)
- [ ] Methods allow assessment of study quality
- [ ] Key limitations mentioned
- [ ] Novel claims distinguished from background
- [ ] Domain terminology preserved exactly
```

## Article Type Adjustments

| Type | Priority Adjustments |
|------|---------------------|
| **Primary Research** | Standard format above |
| **Review Article** | Focus on synthesis/framework; organize by themes; note scope and search methodology |
| **Methods Paper** | Prioritize protocol details, validation experiments, performance benchmarks |
| **Meta-analysis** | Include forest plot data, heterogeneity stats (I², Q), inclusion/exclusion criteria |
| **Case Report** | Clinical timeline, intervention details, outcome measures |

## Length Target

Aim for 15–25% of original paper length. For a typical 5000-word paper, target 750–1250 words.

## Figures and Tables

- For key figures: Extract and state the main quantitative finding
- Note "[See Figure X]" for complex data that can't be summarized numerically
- If figure legends contain methods details, include those in Methods Summary
