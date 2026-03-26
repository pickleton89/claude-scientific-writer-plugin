# Literature Review Decision Frameworks

> Comprehensive decision matrices for database selection, review types, and quality assessment.

---

## Database Selection Matrix

```
What is the primary research domain?
│
├─ Biomedical / Life Sciences
│  │
│  ├─ Clinical / Medical → PubMed + Cochrane + CINAHL + Embase
│  │
│  ├─ Basic Biology → PubMed + bioRxiv + Web of Science
│  │
│  └─ Genomics/Bioinformatics → PubMed + bioRxiv + GEO + UniProt
│
├─ Physical Sciences / Engineering
│  │
│  ├─ Physics / Math → arXiv + Web of Science + ADS
│  │
│  ├─ Chemistry → PubMed + SciFinder + Web of Science
│  │
│  └─ Engineering → IEEE Xplore + Scopus + Web of Science
│
├─ Computer Science / AI
│  │
│  ├─ ML/AI → arXiv + Semantic Scholar + ACM DL + IEEE
│  │
│  └─ General CS → ACM DL + IEEE Xplore + arXiv + DBLP
│
├─ Social Sciences
│  │
│  └─ Psychology / Sociology → PsycINFO + Scopus + SSRN
│
└─ Multidisciplinary
   │
   └─ Cross-field → Semantic Scholar + Web of Science + Scopus + Google Scholar
```

---

## Minimum Database Requirements

| Review Type | Minimum Databases | Recommended |
|-------------|------------------|-------------|
| Systematic review | 3 | 4-5 |
| Scoping review | 2 | 3-4 |
| Narrative review | 2 | 3 |
| Rapid review | 2 | 2-3 |

---

## Review Type Selection

| Factor | Systematic | Scoping | Narrative | Rapid |
|--------|-----------|---------|-----------|-------|
| Timeline | 6-18 months | 3-6 months | 1-3 months | 2-5 weeks |
| Question type | Focused, specific | Broad, exploratory | Broad overview | Urgent, focused |
| Methodology | Rigorous protocol | Flexible framework | Expert synthesis | Streamlined |
| Quality assessment | Required | Optional | Informal | Limited |
| PRISMA required | Yes | PRISMA-ScR | No | Modified |
| Output papers | ≥30 typical | Variable | Variable | 10-30 typical |

---

## Quality Assessment Tool Selection

| Study Design | Assessment Tool | Domains Evaluated |
|-------------|----------------|-------------------|
| Randomized trials | Cochrane RoB 2.0 | 5 domains, 7 items |
| Non-randomized interventions | ROBINS-I | 7 domains |
| Observational cohort | Newcastle-Ottawa Scale | 3 domains, 8 items |
| Cross-sectional | JBI Checklist | 8 items |
| Diagnostic accuracy | QUADAS-2 | 4 domains |
| Qualitative studies | CASP Checklist | 10 items |
| Systematic reviews | AMSTAR 2 | 16 items, 7 critical |
| Animal studies | SYRCLE RoB | 10 items |

> For detailed tool guidance, see `quality_assessment_tools.md`

---

## Literature Coverage Thresholds

> Reference: [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §1

| Review Type | Min Papers | Min Databases | Time Range | Citation Density |
|-------------|------------|---------------|------------|------------------|
| Original Research | 30 | 2 | 5-10 years | 2-4 per paragraph |
| Review Article | 100 | 4 | 10+ years | 4-6 per paragraph |
| Systematic Review | 50+ | 3 | Per PRISMA | All relevant |
| Meta-Analysis | 10+ studies | 3 | 10+ years | All included |
| Methods Paper | 20 | 2 | 5 years | Key comparisons |
| Commentary/Letter | 10-15 | 1 | 2-3 years | Selective |

### Comprehensive Search Criteria

A literature search is considered **comprehensive** when ALL criteria are met:

- [ ] ≥3 databases searched with documented strategy
- [ ] Forward/backward citation search performed
- [ ] Gray literature checked (preprints, theses, conference proceedings)
- [ ] ≤5% new relevant papers found in final search iteration
- [ ] Date range explicitly specified and justified

---

## Literature Recency Thresholds

> Reference: [`QUANTIFICATION_THRESHOLDS.md`](../QUANTIFICATION_THRESHOLDS.md) §6

| Field Type | "Recent" Means | "Current" Means |
|------------|---------------|-----------------|
| Fast-moving (ML, genomics) | ≤2 years | ≤6 months |
| Standard biomedical | ≤5 years | ≤1 year |
| Clinical guidelines | ≤3 years | ≤1 year |
| Historical context | ≤10 years | ≤5 years |
| Foundational work | Any age if seminal | N/A |

---

## Research Question Frameworks

### PICO (Clinical/Intervention)

| Component | Description | Example |
|-----------|-------------|---------|
| **P**opulation | Who is being studied? | Adults with type 2 diabetes |
| **I**ntervention | What treatment/exposure? | Metformin monotherapy |
| **C**omparison | What is the alternative? | Lifestyle modification only |
| **O**utcome | What is measured? | HbA1c reduction at 6 months |

### PEO (Observational/Exposure)

| Component | Description | Example |
|-----------|-------------|---------|
| **P**opulation | Who is being studied? | Healthcare workers |
| **E**xposure | What exposure/risk factor? | Shift work patterns |
| **O**utcome | What is measured? | Burnout prevalence |

### SPIDER (Qualitative)

| Component | Description | Example |
|-----------|-------------|---------|
| **S**ample | Who is being studied? | Cancer survivors |
| **P**henomenon of Interest | What is being explored? | Treatment decision-making |
| **D**esign | Study design | Phenomenological |
| **E**valuation | How outcomes assessed? | Thematic analysis |
| **R**esearch type | Qualitative/mixed | Qualitative |

---

## Synthesis Approach Selection

| Data Type | Approach | Output |
|-----------|----------|--------|
| Quantitative, similar outcomes | Meta-analysis | Forest plot, pooled effect |
| Quantitative, diverse outcomes | Narrative synthesis | Comparison tables |
| Qualitative | Thematic analysis | Theme framework |
| Mixed | Integrated synthesis | Mixed methods matrix |

### Meta-Analysis Feasibility Checklist

- [ ] ≥3 studies with same outcome
- [ ] Effect sizes can be calculated/extracted
- [ ] Studies are clinically similar
- [ ] Statistical heterogeneity acceptable (I² < 75%)
- [ ] No major risk of bias concerns

---

## Quality Rating Thresholds

| Overall Rating | Criteria |
|---------------|----------|
| High quality (Low RoB) | All domains low or some concerns |
| Moderate quality | One high-risk domain, others low |
| Low quality (High RoB) | ≥2 high-risk domains |
| Very low quality | ≥3 high-risk or critical flaw |

---

## Screening Time Budgets

| Stage | Time per Paper | Action |
|-------|---------------|--------|
| Title screening | ≤15 seconds | Include/Exclude/Maybe |
| Abstract screening | ≤2 minutes | Include/Exclude with reason |
| Full-text screening | 10-20 minutes | Final inclusion decision |
