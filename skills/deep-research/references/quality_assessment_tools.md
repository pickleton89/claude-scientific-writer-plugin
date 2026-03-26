# Quality Assessment Tools for Literature Reviews

> Reference document for selecting and applying quality assessment tools in systematic reviews.

## Tool Selection by Study Design

| Study Design | Primary Tool | Alternative | Domains Evaluated |
|-------------|--------------|-------------|-------------------|
| Randomized controlled trials | Cochrane RoB 2.0 | Jadad Scale | 5 domains, 7 signaling questions |
| Non-randomized interventions | ROBINS-I | MINORS | 7 bias domains |
| Observational cohort | Newcastle-Ottawa Scale | JBI Cohort | 3 categories, 8 items |
| Case-control studies | Newcastle-Ottawa Scale | JBI Case-Control | 3 categories, 8 items |
| Cross-sectional | JBI Analytical Cross-Sectional | AXIS | 8 items |
| Diagnostic accuracy | QUADAS-2 | QUADAS-C | 4 domains |
| Qualitative studies | CASP Qualitative | JBI Qualitative | 10 items |
| Systematic reviews | AMSTAR 2 | ROBIS | 16 items, 7 critical |
| Animal studies | SYRCLE RoB | CAMARADES | 10 items |
| Prognostic studies | QUIPS | PROBAST | 6 domains |

---

## Cochrane Risk of Bias 2.0 (RoB 2)

**Use for:** Randomized controlled trials

### Domains

| Domain | Signaling Questions | Focus |
|--------|---------------------|-------|
| D1: Randomization | 3 questions | Allocation sequence, concealment, baseline differences |
| D2: Deviations from intervention | 7 questions | Blinding, adherence, appropriate analysis |
| D3: Missing outcome data | 4 questions | Completeness, evidence of impact |
| D4: Outcome measurement | 4 questions | Method appropriateness, blinding of assessors |
| D5: Selection of reported result | 3 questions | Pre-specification, multiple analyses |

### Judgment Categories

| Judgment | Criteria |
|----------|----------|
| Low risk | Low risk in all domains |
| Some concerns | Some concerns in at least one domain, no high risk |
| High risk | High risk in at least one domain, OR some concerns in multiple domains |

### Scoring Template

```markdown
| Domain | Judgment | Support |
|--------|----------|---------|
| Randomization process | Low/Some concerns/High | [rationale] |
| Deviations from interventions | Low/Some concerns/High | [rationale] |
| Missing outcome data | Low/Some concerns/High | [rationale] |
| Measurement of outcome | Low/Some concerns/High | [rationale] |
| Selection of reported result | Low/Some concerns/High | [rationale] |
| **Overall** | Low/Some concerns/High | |
```

---

## ROBINS-I (Non-Randomized Studies of Interventions)

**Use for:** Non-randomized studies comparing interventions

### Domains

| Domain | Focus |
|--------|-------|
| D1: Confounding | Baseline confounding, time-varying confounding |
| D2: Selection of participants | Selection into study, start of follow-up |
| D3: Classification of interventions | Intervention status well-defined |
| D4: Deviations from interventions | Co-interventions, adherence |
| D5: Missing data | Outcome data, covariate data |
| D6: Measurement of outcomes | Differential measurement, assessor blinding |
| D7: Selection of reported result | Multiple analyses, outcomes |

### Judgment Categories

| Judgment | Criteria |
|----------|----------|
| Low | Comparable to well-performed RCT |
| Moderate | Sound for non-randomized study, some confounding |
| Serious | Important problems in one domain |
| Critical | Very problematic in one domain |
| No information | Insufficient data to judge |

---

## Newcastle-Ottawa Scale (NOS)

**Use for:** Observational studies (cohort, case-control)

### Cohort Studies (Max 9 stars)

| Category | Items | Max Stars |
|----------|-------|-----------|
| Selection | Representativeness, selection of non-exposed, ascertainment of exposure, outcome not present at start | 4 |
| Comparability | Comparability of cohorts based on design/analysis | 2 |
| Outcome | Assessment of outcome, follow-up length, adequacy of follow-up | 3 |

### Case-Control Studies (Max 9 stars)

| Category | Items | Max Stars |
|----------|-------|-----------|
| Selection | Case definition, representativeness, control selection, control definition | 4 |
| Comparability | Comparability based on design/analysis | 2 |
| Exposure | Ascertainment, same method for cases/controls, non-response rate | 3 |

### Quality Thresholds

| Rating | Stars | Interpretation |
|--------|-------|----------------|
| High quality | 7-9 | Low risk of bias |
| Moderate quality | 4-6 | Moderate risk of bias |
| Low quality | 0-3 | High risk of bias |

---

## QUADAS-2 (Diagnostic Accuracy)

**Use for:** Diagnostic accuracy studies

### Domains

| Domain | Signaling Questions | Risk of Bias | Applicability |
|--------|---------------------|--------------|---------------|
| Patient selection | 3 questions | Yes | Yes |
| Index test | 3 questions | Yes | Yes |
| Reference standard | 3 questions | Yes | Yes |
| Flow and timing | 4 questions | Yes | No |

### Key Considerations

- Was a consecutive or random sample of patients enrolled?
- Was a case-control design avoided?
- Did all patients receive the same reference standard?
- Were all patients included in the analysis?

---

## CASP Checklists (Critical Appraisal Skills Programme)

**Use for:** Various study types with qualitative focus

### Available Checklists

| Checklist | Items | Key Focus |
|-----------|-------|-----------|
| Qualitative | 10 | Aims, methodology, recruitment, data collection, ethics, analysis, findings |
| RCT | 11 | Randomization, blinding, follow-up, outcomes, applicability |
| Cohort | 12 | Recruitment, exposure, outcome, confounders, follow-up |
| Case-control | 11 | Case definition, controls, exposure measurement, confounders |
| Systematic review | 10 | Question, methods, results, applicability |

### Qualitative Checklist Questions

1. Was there a clear statement of the aims?
2. Is a qualitative methodology appropriate?
3. Was the research design appropriate?
4. Was the recruitment strategy appropriate?
5. Was data collected in a way that addressed the research issue?
6. Has the relationship between researcher and participants been considered?
7. Have ethical issues been taken into consideration?
8. Was the data analysis sufficiently rigorous?
9. Is there a clear statement of findings?
10. How valuable is the research?

---

## AMSTAR 2 (Systematic Reviews)

**Use for:** Appraising systematic reviews

### Critical Domains (7 items)

| Item | Question |
|------|----------|
| 2 | Protocol registered before review? |
| 4 | Comprehensive literature search? |
| 7 | Justification for excluding studies? |
| 9 | Appropriate risk of bias tool? |
| 11 | Appropriate meta-analysis methods? |
| 13 | RoB considered in interpreting results? |
| 15 | Publication bias assessed? |

### Overall Confidence Rating

| Rating | Criteria |
|--------|----------|
| High | No or one non-critical weakness |
| Moderate | More than one non-critical weakness |
| Low | One critical flaw with/without non-critical weaknesses |
| Critically low | More than one critical flaw |

---

## Practical Application

### Step-by-Step Assessment Process

1. **Select tool** based on study design (see table above)
2. **Pilot assessment** on 2-3 studies to calibrate
3. **Independent assessment** by two reviewers
4. **Calculate agreement** (Cohen's kappa ≥0.8 target)
5. **Resolve discrepancies** through discussion or third reviewer
6. **Document judgments** with supporting rationale
7. **Summarize in tables** for transparency

### Inter-Rater Reliability Targets

| Kappa Value | Interpretation |
|-------------|----------------|
| ≥0.81 | Almost perfect agreement |
| 0.61-0.80 | Substantial agreement |
| 0.41-0.60 | Moderate agreement (minimum acceptable) |
| 0.21-0.40 | Fair agreement |
| ≤0.20 | Poor agreement |

### Reporting Quality Assessment

Include in systematic review:
- Tool used and justification
- Training/calibration process
- Number of independent assessors
- Agreement statistics
- Summary table of assessments
- Risk of bias figures (traffic light plot, summary plot)

---

## External Resources

| Tool | URL |
|------|-----|
| Cochrane RoB 2.0 | https://methods.cochrane.org/risk-bias-2 |
| ROBINS-I | https://methods.cochrane.org/robins-i |
| Newcastle-Ottawa | https://www.ohri.ca/programs/clinical_epidemiology/oxford.asp |
| QUADAS-2 | https://www.bristol.ac.uk/population-health-sciences/projects/quadas/ |
| CASP | https://casp-uk.net/casp-tools-checklists/ |
| AMSTAR 2 | https://amstar.ca/ |
| SYRCLE | https://www.radboudumc.nl/en/research/radboud-technology-centers/animal-research-facility/systematic-reviews |
