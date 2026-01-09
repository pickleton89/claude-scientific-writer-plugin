# Methodology Scoring Calibration

> Reference examples for consistent methodology scoring (1-5 scale).
> Weight: 20% of overall score.

---

## Score 5 Example (Excellent)

**Excerpt:**
> "Cells were treated with compound X (10μM, Sigma #12345, lot ABC123) for 24h at 37°C/5% CO2. Viability was assessed using MTT assay (n=6 biological replicates from independent passages, 3 technical replicates each, across 3 independent experiments). Statistical analysis used one-way ANOVA with Tukey's post-hoc correction (α=0.05, Bonferroni-adjusted for multiple comparisons). Power analysis (G*Power 3.1) indicated n=5 required for 80% power to detect 20% difference (effect size d=0.8). All experiments were performed by blinded observers; treatment allocation was randomized using computer-generated sequences."

**Why Score 5:**
- Complete reagent information (source, lot number)
- Appropriate replication (n=6 biological, n=3 technical)
- Justified statistical approach with correction
- Power analysis documented with parameters
- Blinding and randomization described
- Fully replicable by another lab

**Key Indicators:**
- ✓ Reagent/material sources with identifiers
- ✓ Biological AND technical replicates specified
- ✓ Statistical methods justified
- ✓ Power analysis with parameters
- ✓ Blinding/randomization documented

---

## Score 4 Example (Good)

**Excerpt:**
> "HEK293T cells were treated with 10μM compound X (Sigma) for 24 hours. Cell viability was measured by MTT assay in six biological replicates. Data were analyzed using one-way ANOVA with Tukey correction. Experiments were performed in triplicate on three separate occasions."

**Why Score 4:**
- Reagent source provided (missing lot)
- Good replication structure
- Appropriate statistical approach
- Missing power analysis
- No explicit blinding mentioned
- Replicable with some assumptions

**Key Indicators:**
- ✓ Basic reagent sourcing
- ✓ Clear replication (n=6 biological)
- ✓ Statistical approach named
- ○ No power analysis
- ○ Blinding not mentioned

---

## Score 3 Example (Adequate)

**Excerpt:**
> "Cells were treated with compound X for 24h. Viability was measured using MTT assay (n=3). Statistical significance was determined using t-test (p<0.05)."

**Why Score 3:**
- Missing concentration, vendor info
- Minimum replication (n=3)
- Replicate type unclear (biological vs technical?)
- No power justification
- Basic but acceptable for replication with assumptions
- Statistical test may not be optimal

**Key Indicators:**
- ○ No reagent sourcing
- ○ Minimal replication (n=3)
- ○ Replicate type not specified
- ○ Simple statistical approach
- ○ Multiple comparisons not addressed

---

## Score 2 Example (Needs Work)

**Excerpt:**
> "Cells were treated and viability was assessed by MTT. The experiment was repeated twice and results were analyzed statistically."

**Why Score 2:**
- No treatment details
- No sample sizes given
- "Repeated twice" is ambiguous
- Statistical approach not specified
- Cannot replicate without major assumptions
- Fundamental gaps in reporting

**Key Indicators:**
- ✗ No experimental parameters
- ✗ Sample size unclear
- ✗ Statistical method unspecified
- ✗ Replication inadequate

---

## Score 1 Example (Poor)

**Excerpt:**
> "Cells were treated and viability measured using standard protocols. Results showed significant effects."

**Why Score 1:**
- No replication possible
- Missing all critical details
- "Standard protocols" is undefined
- "Significant" without statistics
- Complete revision needed

**Key Indicators:**
- ✗ No methods detail
- ✗ No replication information
- ✗ No statistical support
- ✗ Cannot evaluate validity

---

## Scoring Decision Tree

```
Is full replication possible from text alone?
├── Yes → Does it include power analysis?
│   ├── Yes → Does it describe blinding/randomization?
│   │   ├── Yes → Score 5
│   │   └── No → Score 4
│   └── No → Score 4 (if good replication) or 3
├── Partially → Score 3
├── With major assumptions → Score 2
└── No → Score 1
```

---

## Common Scoring Pitfalls

1. **Over-scoring brief but correct methods:** A short but technically correct description that lacks replicability details should not exceed Score 3.

2. **Under-scoring non-standard approaches:** Novel methods with thorough documentation can score 5 even if unconventional.

3. **Ignoring sample size:** n<3 per group caps score at 2 regardless of other details.

4. **Conflating technical and biological replicates:** Only biological replicates count for sample size; technical replicates are quality control.
