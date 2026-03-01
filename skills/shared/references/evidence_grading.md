# Evidence Grading Tiers (T1-T4)

> Shared reference for evidence classification across research skills.
> Version: 1.0.0
> Used by: literature-review, target-intelligence, drug-intelligence, target-validation

---

## Tier Definitions

| Tier | Label | Strength | Definition |
|------|-------|----------|------------|
| **T1** | Mechanistic / Direct | ★★★ | Direct experimental evidence establishing causal mechanism. Human clinical proof, crystal structures with defined mechanism, CRISPR KO with rescue experiments, FDA-approved drugs with characterized mechanism. |
| **T2** | Functional | ★★☆ | Functional studies with phenotypic outcome. Model organism data (mouse KO, zebrafish morphants), biochemical assays with activity measurements, siRNA/shRNA knockdown with phenotype. |
| **T3** | Association | ★☆☆ | Statistical associations without direct causal proof. GWAS loci, DepMap essentiality scores, high-throughput screen hits, expression correlations, text-mined interactions. |
| **T4** | Mention / Review | ☆☆☆ | Indirect or low-confidence references. Review article mentions, computational predictions (AlphaFold, ADMET-AI), database cross-references without primary data, peripheral citations. |

---

## Inline Labeling Convention

Every factual claim in reports must carry an inline evidence label:

```
"ATP6V1A is essential for lysosomal acidification [T1: PMID:12345678]"
"BRCA2 knockdown reduces homologous recombination efficiency by 85% [T2: PMID:23456789]"
"rs1234567 is associated with increased risk (OR=1.3, p=2e-8) [T3: GWAS Catalog]"
"X has been mentioned in the context of Y [T4: Review, PMID:34567890]"
```

**Format:** `[T{n}: {source}]` where source is PMID, database name, or DOI.

---

## Tier Assignment Rules

### T1 Criteria (all must apply)
- Primary experimental data presented in the cited paper
- Causal mechanism demonstrated (not just correlation)
- Human data or direct biochemical proof
- Reproducible (ideally replicated across labs)

### T2 Criteria
- Functional readout measured (not just binding/association)
- Phenotypic consequence documented
- Model system used (cell line, organoid, animal model)
- Quantitative data reported (IC50, fold-change, p-value)

### T3 Criteria
- Statistical association reported with significance threshold
- Large-scale screen or population study
- Correlation without mechanistic follow-up
- Computational prediction with experimental training data

### T4 Criteria
- No primary experimental data in the cited source
- Review, commentary, or editorial mention
- Pure computational prediction without validation
- Database annotation without linked primary reference

---

## Aggregation for Scoring

When multiple evidence tiers support a single claim, report the **highest tier** with a count:

```
"Target X implicated in Disease Y [T1: 2 studies, T2: 5 studies, T3: 12 associations]"
```

For `target-validation` scoring, evidence weights are:
- T1 evidence: Full points for the relevant scoring component
- T2 evidence: 70-80% of component maximum
- T3 evidence: 40-60% of component maximum
- T4 evidence only: 10-20% of component maximum (flag as gap)

---

## Quality Flags

| Flag | Meaning | Action |
|------|---------|--------|
| `[SINGLE-SOURCE]` | Claim supported by only one study | Note in limitations; seek corroboration |
| `[PREPRINT]` | Evidence from non-peer-reviewed preprint | Downgrade one tier; flag for monitoring |
| `[RETRACTED]` | Source has been retracted | Exclude from evidence base |
| `[CONFLICT]` | Contradictory evidence exists | Present both sides; note in discussion |
