# Literature Review Best Practices & Common Pitfalls

> Guidance for avoiding common mistakes in systematic literature reviews, framed as positive solutions.

---

## 1. Multi-Database Coverage

### Best Practice

Search a minimum of 3 databases for systematic reviews, selecting databases based on domain relevance.

```
Recommended approach:
- Select databases using the Database Selection Matrix
- Include at least one general database (Web of Science, Scopus)
- Include domain-specific databases (PubMed for biomedical, IEEE for engineering)
- Consider preprint servers for recent findings (bioRxiv, arXiv)
- Document all searches for reproducibility
```

### Why This Matters

Single-database searches miss 30-50% of relevant literature. Different databases have varying coverage:
- PubMed: Strong in biomedical, weak in engineering
- Scopus: Broad coverage but gaps in humanities
- Web of Science: Curated quality, limited open access
- Google Scholar: Wide but noisy, not reproducible

### Verification Checklist

- [ ] ≥3 databases searched
- [ ] Domain-specific database included
- [ ] Preprint server checked (if field appropriate)
- [ ] Each database documented with date and query

---

## 2. Thematic Synthesis Over Study-by-Study Summaries

### Best Practice

Organize results by themes and synthesize findings across studies, not as sequential summaries.

```markdown
Effective synthesis structure:

### Theme: [Topic Name]

Multiple studies (n=X) found consistent evidence that [finding]
(Smith 2020; Jones 2021; Brown 2022). Effect sizes ranged from
d=0.3 to d=0.8, with stronger effects in [context]. However,
conflicting results emerged regarding [subtopic], possibly due to
[methodological differences]...
```

### Why This Matters

Study-by-study summaries ("Smith found X, Jones found Y, Brown found Z..."):
- Fail to identify patterns across studies
- Make it difficult for readers to understand consensus
- Don't highlight conflicts or gaps
- Read like annotated bibliographies, not reviews

### Synthesis Approach

| Instead of... | Write... |
|---------------|----------|
| "Smith (2020) found that..." | "Several studies (n=5) demonstrated that..." |
| Listing each study separately | Grouping by finding/theme |
| Reporting all results equally | Highlighting consensus, conflicts, gaps |

---

## 3. Reproducible Search Documentation

### Best Practice

Document verbatim search strategies for each database with all relevant metadata.

```markdown
Required documentation per database:
1. Database name and platform (e.g., "PubMed via NCBI")
2. Date searched (YYYY-MM-DD format)
3. Exact search string (copy-paste from database)
4. Number of results returned
5. Filters applied (date range, language, publication type)
6. Any modifications from master strategy
```

### Why This Matters

Undocumented searches:
- Cannot be replicated by other researchers
- Fail PRISMA reporting requirements
- Undermine review credibility
- Make updates impossible

### Documentation Template

| Database | Platform | Date | Query | Results | Filters |
|----------|----------|------|-------|---------|---------|
| PubMed | NCBI | 2024-01-15 | [full query] | 892 | English, 2019-2024 |
| Scopus | Elsevier | 2024-01-15 | [full query] | 1,203 | Journal articles only |

---

## 4. Standardized Quality Assessment

### Best Practice

Use validated quality assessment tools appropriate to study design, applied systematically to all included studies.

```
Quality assessment process:
1. Select tool based on study design (see Quality Assessment Tool Selection)
2. Pilot on 2-3 studies to calibrate
3. Assess independently with ≥2 reviewers
4. Calculate inter-rater agreement (target κ ≥0.8)
5. Resolve discrepancies through discussion
6. Document all judgments with supporting rationale
7. Create summary table and risk of bias visualization
```

### Tool Selection Guide

| Study Design | Tool |
|-------------|------|
| RCTs | Cochrane RoB 2.0 |
| Observational | Newcastle-Ottawa Scale |
| Diagnostic | QUADAS-2 |
| Qualitative | CASP Checklist |
| Systematic reviews | AMSTAR 2 |

### Why This Matters

Without quality assessment:
- Low-quality studies are weighted equally with rigorous ones
- Bias in individual studies propagates to review conclusions
- Readers cannot judge strength of evidence
- PRISMA and journal requirements are not met

---

## 5. Citation Verification

### Best Practice

Verify 100% of citations before submission using systematic checking procedures.

```
Verification workflow:
1. Extract all DOIs from document
2. Test each DOI resolves correctly
3. Cross-check metadata:
   - Author names match source
   - Publication year correct
   - Journal name correct (full or abbreviated per style)
   - Volume/issue/pages correct
4. Verify in-text citations match reference list
5. Run automated verification script: python {baseDir}/scripts/verify_citations.py
6. Manual review of any flagged issues
```

### Why This Matters

Unverified citations:
- May have incorrect DOIs (broken links)
- May have wrong years or author names
- Create problems during peer review
- Damage author credibility

### Quality Targets

| Metric | Target |
|--------|--------|
| DOIs verified | 100% |
| Metadata accuracy | 100% |
| Broken links | 0 |
| Style consistency | 100% |

---

## 6. Documented Exclusion Reasons

### Best Practice

Track and report specific exclusion reasons at each screening stage with counts.

```
PRISMA-compliant exclusion reporting:

Full-text articles excluded (n = 85):
├─ Wrong population (n = 23)
├─ Wrong study design (n = 31)
├─ Wrong outcome measure (n = 14)
├─ Not English language (n = 8)
├─ Conference abstract only (n = 6)
└─ Duplicate publication (n = 3)
```

### Why This Matters

Missing exclusion reasons:
- Make the review process opaque
- Prevent replication
- Raise questions about bias
- Violate PRISMA requirements

### Tracking Template

| Stage | Excluded | Reason Categories |
|-------|----------|-------------------|
| Title screening | n = X | Not tracked (optional) |
| Abstract screening | n = Y | Track by category |
| Full-text screening | n = Z | Track by specific reason |

---

## 7. Appropriate Date Ranges

### Best Practice

Explicitly specify and justify date ranges based on field characteristics and review objectives.

| Field Type | Recommended Range |
|------------|-------------------|
| Fast-moving (ML, genomics) | 2-5 years |
| Standard biomedical | 5-10 years |
| Historical/foundational | 10+ years or "inception" |
| Guideline updates | Since last guideline |

### Justification Examples

- "We searched from 2015-2024 because [intervention] was FDA-approved in 2014"
- "We searched from inception because we aimed to capture the evolution of [concept]"
- "We limited to 2019-2024 due to rapid methodological advances in [field]"

---

## 8. Inter-Rater Agreement

### Best Practice

Use dual screening and extraction with documented agreement metrics.

| Process | Minimum Requirement |
|---------|---------------------|
| Title/abstract screening | 20% dual-screened |
| Full-text screening | 100% dual-screened |
| Data extraction | 20% dual-extracted |
| Quality assessment | 100% dual-assessed |

### Agreement Thresholds

| Kappa | Interpretation | Action |
|-------|----------------|--------|
| ≥0.81 | Excellent | Proceed |
| 0.61-0.80 | Good | Acceptable, discuss discrepancies |
| 0.41-0.60 | Moderate | Recalibrate, retrain |
| ≤0.40 | Poor | Stop, revise criteria |

---

## Quick Reference: Pre-Submission Checklist

- [ ] ≥3 databases searched with documented strategies
- [ ] PRISMA flow diagram complete with all numbers
- [ ] Exclusion reasons tracked and reported
- [ ] Quality assessment using validated tool
- [ ] Results organized thematically (not study-by-study)
- [ ] 100% of citations verified
- [ ] Inter-rater agreement documented
- [ ] Date range justified
- [ ] Protocol registered (if systematic review)
