# Literature Review Output Templates

> Ready-to-use templates for PRISMA diagrams, search documentation, and data extraction.

---

## PRISMA Flow Diagram Template

```
┌─────────────────────────────────────────────────────────────────┐
│                        IDENTIFICATION                            │
├─────────────────────────────────────────────────────────────────┤
│  Records identified through            Additional records        │
│  database searching                    from other sources        │
│  (n = {{db_total}})                    (n = {{other}})           │
│                                                                   │
│  ├─ PubMed (n = )                      ├─ Citation search (n = ) │
│  ├─ Scopus (n = )                      ├─ Grey literature (n = ) │
│  ├─ Web of Science (n = )              └─ Expert referral (n = ) │
│  └─ [Other] (n = )                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Records removed before screening                                │
│  ├─ Duplicate records (n = {{duplicates}})                      │
│  └─ Records marked as ineligible by automation (n = )           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SCREENING                                │
├─────────────────────────────────────────────────────────────────┤
│  Records screened ───────────────────► Records excluded          │
│  (n = {{screened}})                    (n = {{title_excl}})      │
│                              │                                   │
│                              ▼                                   │
│  Reports sought for retrieval                                    │
│  (n = {{sought}})                                                │
│                              │                                   │
│                              ▼                                   │
│  Reports not retrieved ──────────────► Reasons:                  │
│  (n = {{not_retrieved}})               ├─ Not available (n = )   │
│                                        └─ Paywall (n = )         │
│                              │                                   │
│                              ▼                                   │
│  Reports assessed for eligibility ───► Reports excluded          │
│  (n = {{ft_assessed}})                 (n = {{ft_excl}})         │
│                                        ├─ Wrong population (n = )│
│                                        ├─ Wrong intervention (n =│
│                                        ├─ Wrong outcome (n = )   │
│                                        ├─ Wrong study design (n =│
│                                        └─ Other (n = )           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          INCLUDED                                │
├─────────────────────────────────────────────────────────────────┤
│  Studies included in review                                      │
│  (n = {{included}})                                              │
│                                                                   │
│  ├─ Reports of included studies (n = {{reports}})               │
│  │                                                               │
│  ├─ Studies in quantitative synthesis / meta-analysis           │
│  │  (n = {{quant}})                                              │
│  │                                                               │
│  └─ Studies in qualitative synthesis                            │
│     (n = {{qual}})                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Search Documentation Template

```markdown
## Search Strategy

**Review title:** {{title}}
**Date of search:** {{YYYY-MM-DD}}
**Reviewer(s):** {{names}}

---

### Database: {{database_name}}

**Platform:** {{platform}} (e.g., Ovid, EBSCOhost, Web)
**Date searched:** {{YYYY-MM-DD}}
**Date coverage:** {{start_year}} to {{end_year}}

**Search query:**
```
{{full_search_string_with_line_numbers}}
```

**Filters applied:**
- Date range: {{start}} to {{end}}
- Language: {{language}}
- Publication type: {{types}}
- Species: {{if applicable}}

**Results:** {{N}} records exported

**Notes:** {{any_issues_or_observations}}

---

### Database: {{database_name_2}}

[Repeat for each database searched]

---

## Search Summary

| Database | Platform | Date | Results |
|----------|----------|------|---------|
| PubMed | NCBI | YYYY-MM-DD | N |
| Scopus | Elsevier | YYYY-MM-DD | N |
| Web of Science | Clarivate | YYYY-MM-DD | N |
| **Total** | | | **N** |
| After deduplication | | | **N** |
```

---

## Data Extraction Form Template

```markdown
## Study: {{First Author}} {{Year}}

### Identification

| Field | Value |
|-------|-------|
| Study ID | {{FirstAuthor_Year}} |
| Full citation | {{APA format citation}} |
| DOI | {{doi}} |
| Country | {{country}} |
| Funding source | {{funding}} |
| Conflicts of interest | {{COI statement}} |

### Study Characteristics

| Field | Value |
|-------|-------|
| Study design | {{RCT/Cohort/Case-control/etc.}} |
| Setting | {{Hospital/Community/etc.}} |
| Study period | {{start}} to {{end}} |
| Follow-up duration | {{duration}} |

### Participants

| Field | Value |
|-------|-------|
| Total sample size | n = {{N}} |
| Intervention group | n = {{n1}} |
| Control group | n = {{n2}} |
| Age (mean ± SD) | {{age}} |
| Sex (% female) | {{percent}} |
| Inclusion criteria | {{criteria}} |
| Exclusion criteria | {{criteria}} |

### Intervention/Exposure

| Field | Value |
|-------|-------|
| Intervention description | {{description}} |
| Dose/intensity | {{dose}} |
| Duration | {{duration}} |
| Comparator | {{comparator description}} |

### Outcomes

| Outcome | Measure | Timepoint | Intervention | Control | Effect (95% CI) |
|---------|---------|-----------|--------------|---------|-----------------|
| Primary: {{outcome}} | {{measure}} | {{time}} | {{value}} | {{value}} | {{effect}} |
| Secondary: {{outcome}} | {{measure}} | {{time}} | {{value}} | {{value}} | {{effect}} |

### Risk of Bias Assessment

| Domain | Judgment | Support |
|--------|----------|---------|
| {{Domain 1}} | Low/Some concerns/High | {{rationale}} |
| {{Domain 2}} | Low/Some concerns/High | {{rationale}} |
| {{Domain 3}} | Low/Some concerns/High | {{rationale}} |
| **Overall** | Low/Some concerns/High | |

### Key Findings

{{Summary of main findings in 2-3 sentences}}

### Limitations

{{Author-reported limitations}}

### Notes

{{Extractor notes, queries for authors, etc.}}

**Extracted by:** {{initials}}
**Date:** {{YYYY-MM-DD}}
**Verified by:** {{initials}}
```

---

## Characteristics of Included Studies Table

```markdown
## Table 1. Characteristics of Included Studies (n = {{N}})

| Study | Country | Design | N | Population | Intervention | Comparator | Outcomes | Follow-up | Quality |
|-------|---------|--------|---|------------|--------------|------------|----------|-----------|---------|
| Smith 2020 | USA | RCT | 150 | Adults with T2DM | Drug A 10mg | Placebo | HbA1c, weight | 12 mo | Low RoB |
| Jones 2021 | UK | Cohort | 500 | Healthcare workers | Shift work | Day work | Burnout | 24 mo | Moderate |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

*RCT = randomized controlled trial; T2DM = type 2 diabetes mellitus; RoB = risk of bias*
```

---

## Summary of Findings Table (GRADE)

```markdown
## Summary of Findings

**Population:** {{population}}
**Intervention:** {{intervention}}
**Comparison:** {{comparator}}
**Setting:** {{setting}}

| Outcome | Studies (n) | Participants (N) | Effect (95% CI) | Certainty | Comments |
|---------|-------------|------------------|-----------------|-----------|----------|
| {{Outcome 1}} | k = 5 | N = 1,200 | RR 0.75 (0.60-0.94) | ⊕⊕⊕⊕ High | |
| {{Outcome 2}} | k = 3 | N = 800 | MD -2.5 (-3.8 to -1.2) | ⊕⊕⊕○ Moderate | Downgraded for imprecision |
| {{Outcome 3}} | k = 4 | N = 950 | OR 1.50 (0.90-2.50) | ⊕⊕○○ Low | Downgraded for RoB and imprecision |

*GRADE certainty ratings: High (⊕⊕⊕⊕), Moderate (⊕⊕⊕○), Low (⊕⊕○○), Very low (⊕○○○)*
*RR = relative risk; MD = mean difference; OR = odds ratio; CI = confidence interval; RoB = risk of bias*
```

---

## Thematic Synthesis Template

```markdown
## Results: Thematic Synthesis

### Theme 1: {{Theme Name}}

{{Synthesis paragraph integrating findings from multiple studies. Do NOT summarize study-by-study.}}

Multiple studies (n = X) found consistent evidence that [finding] (Author1 2020; Author2 2021; Author3 2022). Effect sizes ranged from [range], with the largest effects observed in [context]. However, conflicting results emerged regarding [subtopic], with [n] studies reporting [opposite finding] (Author4 2021; Author5 2022). This discrepancy may be explained by [methodological differences/population differences/etc.].

**Summary Table: Theme 1**

| Finding | Supporting Studies | Effect Direction | Confidence |
|---------|-------------------|------------------|------------|
| {{Finding A}} | Smith 2020, Jones 2021 | Positive | High |
| {{Finding B}} | Brown 2022 | Negative | Low |

---

### Theme 2: {{Theme Name}}

[Continue thematic synthesis...]

---

## Gaps and Future Directions

Based on this review, the following gaps were identified:

1. **Gap 1:** {{description}} — recommended studies: {{type}}
2. **Gap 2:** {{description}} — recommended studies: {{type}}
3. **Gap 3:** {{description}} — recommended studies: {{type}}
```

---

## Citation Style Quick Reference

| Style | In-text | Reference Format |
|-------|---------|------------------|
| APA 7 | (Smith et al., 2023) | Smith, J. D., Johnson, M. L., & Williams, K. (2023). Title. *Journal*, *22*(4), 301-318. https://doi.org/xxx |
| Nature | Superscript^1,2^ | 1. Smith, J. D. et al. Title. *J. Name* **22**, 301-318 (2023). |
| Vancouver | Superscript^1,2^ | 1. Smith JD, Johnson ML. Title. J Name. 2023;22(4):301-18. |
| IEEE | Bracketed [1], [2] | [1] J. D. Smith et al., "Title," *J. Name*, vol. 22, no. 4, pp. 301-318, 2023. |

> For detailed citation formatting, see `citation_styles.md`
