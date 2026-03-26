# Evidence Hierarchy: Level I-VII ↔ T1-T4 Mapping

Reference for mapping traditional study-design evidence levels to the biomedical
claim-strength tiers used across the plugin. Both systems apply simultaneously:
**Level** grades the study design; **Tier** grades a specific claim within that study.

## Full Mapping Table

| Level | Study Design | Tier | Claim Strength | Examples |
|-------|-------------|------|----------------|----------|
| **I** | Systematic review / meta-analysis | **T1** | Mechanistic / Direct | Cochrane reviews, PRISMA-compliant meta-analyses with forest plots |
| **II** | Randomized controlled trial | **T1** | Mechanistic / Direct | Phase III RCTs, crossover trials with washout, cluster-randomized trials |
| **III** | Controlled non-randomized study | **T2** | Functional | Quasi-experimental studies, non-randomized comparisons with concurrent controls |
| **IV** | Case-control / cohort study | **T2** | Functional | Prospective/retrospective cohorts, nested case-control, case-cohort |
| **V** | Descriptive / narrative review | **T3** | Association | Scoping reviews, narrative literature reviews, cross-sectional surveys |
| **VI** | Single descriptive / case study | **T3** | Association | Case reports, case series, single-arm studies, ecological studies |
| **VII** | Expert opinion / editorial | **T4** | Mention / Review | Editorials, consensus statements without systematic methodology, letters |

## Disambiguation Rules

A single study can contain claims at different tiers:

| Scenario | Level | Tier for Primary Claim | Tier for Secondary Claim |
|----------|-------|----------------------|------------------------|
| RCT primary endpoint (significant) | II | T1 | — |
| RCT post-hoc subgroup analysis | II | T3 (exploratory) | — |
| RCT safety signal (adverse event) | II | T2 (functional observation) | — |
| Cohort with genetic association | IV | T2 (primary) | T3 (GWAS sub-analysis) |
| Meta-analysis of observational studies | I (design) | T2 (pooled associations, not causal proof) | — |
| Computational prediction validated in vitro | — | T2 (experimental part) | T4 (computational part) |

**Rule:** Assign the tier to the *claim*, not the study. A Level II study may produce
T1 claims (primary endpoint), T2 claims (secondary endpoints), and T3 claims
(post-hoc analyses) simultaneously.

## Preprint Adjustment

Preprints (bioRxiv, medRxiv) have not undergone peer review:
- Downgrade one tier from what the study design would normally warrant
- Flag with `[PREPRINT]` quality flag
- Example: An RCT preprint → Level II study design, but claims capped at T2 until peer-reviewed

## Special Cases

### Biomedical Laboratory Evidence

Lab evidence doesn't fit the clinical hierarchy cleanly. Use these mappings:

| Evidence Type | Tier | Rationale |
|--------------|------|-----------|
| CRISPR KO + rescue experiment | T1 | Direct causal proof of gene function |
| Crystal structure with mechanism | T1 | Atomic-resolution mechanistic evidence |
| siRNA/shRNA knockdown + phenotype | T2 | Functional but indirect (off-target risk) |
| Biochemical assay (IC50, Kd) | T2 | Quantitative functional measurement |
| Mouse/zebrafish model phenotype | T2 | Cross-species functional evidence |
| GWAS hit (genome-wide significant) | T3 | Statistical association, no mechanism |
| DepMap essentiality score | T3 | High-throughput screen, no mechanism |
| Expression correlation (GTEx) | T3 | Association without causal inference |
| AlphaFold structure prediction | T4 | Computational, no experimental validation |
| ADMET-AI prediction | T4 | Computational, no experimental validation |
| Text-mined interaction | T4 | Automated extraction, unverified |
| Database cross-reference only | T4 | No primary data in cited source |

### Systematic Review Grading (GRADE)

When performing systematic reviews, the GRADE certainty framework operates
alongside the Level/Tier system:

| GRADE Certainty | Typical Tier Assignment |
|----------------|----------------------|
| High (no downgrade) | T1 |
| Moderate (1 downgrade) | T1-T2 (context-dependent) |
| Low (2 downgrades) | T2-T3 |
| Very Low (≥3 downgrades) | T3 |

GRADE downgrade reasons: risk of bias, inconsistency, indirectness, imprecision,
publication bias. GRADE upgrade reasons: large effect, dose-response, confounders
would reduce effect.

## Integration with Verification Agent

The verification agent uses this hierarchy to:
1. Assign an evidence level (I-VII) based on study design
2. Assign a tier (T1-T4) to each specific claim
3. Apply the preprint adjustment if the source is not peer-reviewed
4. Apply quality flags: `[SINGLE-SOURCE]`, `[PREPRINT]`, `[RETRACTED]`, `[CONFLICT]`
5. Report both level and tier in the annotated bibliography

Output format per source:
```
Evidence Level: III | Claim Tier: T2 | Flags: none
```
