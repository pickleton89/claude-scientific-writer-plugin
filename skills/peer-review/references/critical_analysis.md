# Critical Analysis Framework

> Systematic frameworks for evaluating scientific rigor, identifying logical flaws, and assessing evidence quality.

---

## Evidence Quality Assessment (GRADE)

### Study Design Hierarchy

| Rank | Design Type | Starting Quality |
|------|-------------|------------------|
| 1 | Systematic reviews/meta-analyses | Highest (for intervention effects) |
| 2 | Randomized controlled trials | High |
| 3 | Cohort studies | Low-Moderate |
| 4 | Case-control studies | Low |
| 5 | Cross-sectional studies | Low |
| 6 | Case series/reports | Very Low |
| 7 | Expert opinion | Lowest |

### GRADE Adjustment Factors

**Downgrade quality for:**
- Risk of bias (selection, performance, detection, attrition, reporting)
- Inconsistency across studies
- Indirectness (different populations, interventions, outcomes)
- Imprecision (wide confidence intervals, small samples)
- Publication bias

**Upgrade quality for:**
- Large effect sizes (RR >2 or <0.5)
- Dose-response relationships
- Confounders would reduce observed effect

### Convergence of Evidence

| Strength | Characteristics |
|----------|-----------------|
| **Stronger** | Multiple independent replications, different methodologies converge, mechanistic alignment |
| **Weaker** | Single study, contradictory findings, no replication attempts, publication bias evident |

**Reference:** See `{baseDir}/references/evidence_hierarchy.md` for detailed GRADE system.

---

## Logical Fallacy Identification

### Causation Fallacies

| Fallacy | Pattern | Example |
|---------|---------|---------|
| Post hoc | B followed A, so A caused B | "We added the drug, then the cells grew" |
| Correlation = causation | Association interpreted as causality | "Ice cream sales correlate with drowning" |
| Reverse causation | Mistaking cause for effect | "Depression causes poor diet" vs opposite |

### Generalization Fallacies

| Fallacy | Pattern | Example |
|---------|---------|---------|
| Hasty generalization | Broad conclusions from small samples | n=5 study claiming universal effect |
| Cherry-picking | Selecting only supporting evidence | Reporting only significant results |
| Ecological fallacy | Group patterns applied to individuals | Population average doesn't apply to each person |

### Statistical Fallacies

| Fallacy | Pattern | Detection |
|---------|---------|-----------|
| Base rate neglect | Ignoring prior probability | Check if priors considered in interpretation |
| Texas sharpshooter | Finding patterns in random data | Post-hoc hypothesis selection |
| Prosecutor's fallacy | Confusing P(E|H) with P(H|E) | Check direction of conditional probability |

### Science-Specific Fallacies

| Fallacy | Pattern | Response |
|---------|---------|----------|
| Galileo gambit | "They laughed at X, so my fringe idea is correct" | Rejection doesn't validate |
| Argument from ignorance | "Not proven false, so true" | Burden of proof reversed |
| Unfalsifiability | Making untestable claims | Cannot be scientific |

**When identifying fallacies:** Name the specific fallacy, explain why reasoning is flawed, identify what evidence would be needed for valid inference.

**Reference:** See `{baseDir}/references/logical_fallacies.md` for comprehensive catalog.

---

## Claim Evaluation Framework

### 5-Step Systematic Evaluation

1. **Identify the Claim**
   - Type: Causal, associational, or descriptive?
   - Strength: Proven, likely, suggested, possible?

2. **Assess the Evidence**
   - Direct or indirect?
   - Sufficient for claim strength?
   - Alternative explanations ruled out?

3. **Check Logical Connection**
   - Do conclusions follow from data?
   - Are there logical leaps?

4. **Evaluate Proportionality**
   - Is confidence proportional to evidence?
   - Are limitations downplayed?

5. **Check for Overgeneralization**
   - Do claims extend beyond sample?
   - Are caveats included?

### Red Flags in Claims

| Red Flag | Why Problematic |
|----------|-----------------|
| Causal language from correlational studies | Cannot establish causation without experiments |
| "Proves" or absolute certainty | Science deals in evidence, not proof |
| Ignoring contradictory evidence | Selection bias in interpretation |
| Extrapolation beyond data | Unsupported generalization |

---

## Bias Detection

### Cognitive Biases (Researcher)

| Bias | Signs | Check |
|------|-------|-------|
| Confirmation bias | Only supporting findings highlighted | Are null results reported? |
| HARKing | Hypotheses stated post-hoc | Was study pre-registered? |
| Publication bias | Negative results missing | Are file drawer studies cited? |

### Selection Biases

| Bias | Signs | Impact |
|------|-------|--------|
| Sampling bias | Non-representative sample | Limited generalizability |
| Attrition bias | Differential dropout | Skewed results |
| Survivorship bias | Only "survivors" visible | Overestimated effects |

### Measurement Biases

| Bias | Signs | Mitigation |
|------|-------|------------|
| Observer bias | Expectations influence observations | Blinding |
| Recall bias | Systematic retrospective inaccuracies | Prospective design |
| Instrument bias | Systematic measurement errors | Calibration, validation |

### Analysis Biases

| Bias | Signs | Red Flag |
|------|-------|----------|
| P-hacking | Multiple analyses until significance | Many tests, few corrections |
| Outcome switching | Replacing non-significant outcomes | Primary outcome different from registered |
| Subgroup fishing | Uncorrected subgroup analyses | Many subgroups, no pre-specification |

**Reference:** See `{baseDir}/references/common_biases.md` for comprehensive bias taxonomy.

---

## Quick Reference Card

### Evidence Strength

```
Strong: Multiple RCTs + meta-analysis + mechanism
Moderate: Single RCT or multiple observational studies
Weak: Single observational or case series
Very Weak: Expert opinion only
```

### Common Logical Errors

```
Causation claims ← Check: Was it randomized?
Generalization ← Check: Sample size and representativeness?
Mechanism claims ← Check: Direct mechanistic evidence?
```

### Bias Checklist

```
□ Was selection randomized?
□ Were observers blinded?
□ Was analysis pre-registered?
□ Are all outcomes reported?
□ Are negative results included?
```

---

## Claim Type → Red Flags Quick Reference

When evaluating claims in a paper, abstract, press release, or news report, this table maps common claim patterns to the appropriate skeptical response and the red flags that signal the claim is overstated or unsupported.

| Claim type | Appropriate response | Red flags requiring skepticism |
|------------|---------------------|-------------------------------|
| "Drug X reduces mortality by 50%" | Ask: relative or absolute? What was baseline event rate? Demand ARR and NNT. | Only relative risk reported; no CI; baseline rates not given; press release without methods access |
| "Observational study shows X causes Y" | Downgrade language to "associated with"; enumerate plausible confounders; check whether DAG-based or propensity-score adjustment was attempted. | Authors use "causes," "leads to," or "drives" without randomization; no sensitivity analysis for unmeasured confounding |
| "Significant p-value (p < 0.05) proves the effect" | Check effect size and 95% CI; assess clinical/practical importance; check the number of comparisons performed. | p ≈ 0.04 with N = 50,000 and tiny effect; many outcomes tested with no multiple-testing correction; primary outcome differs from registered protocol |
| "Single RCT is definitive" | Check for replication; assess risk of bias (RoB 2); check funding and conflicts. | Industry-funded with no independent statistician; open-label design for subjective outcome; per-protocol rather than ITT analysis; outcome switched after unblinding |
| "Preprint shows breakthrough" | Await peer review; check for data/code sharing; look for independent replication. | No data or code; sensational press release; authors with conflicts; method described in too little detail to reproduce |
| "N-of-1 case report demonstrates treatment" | Note absence of control; treat as hypothesis-generating only. | Used to support clinical practice change without cohort or trial evidence |
| "Improved [biomarker / imaging metric]" | Verify the biomarker is a *validated* surrogate for the clinical outcome of interest, not merely correlated with it. | Hard outcome (mortality, hospitalization, function) not measured; surrogate has prior history of translation failure |
| "Worked in mice / cells" | Treat as preclinical signal only. ~85% of preclinical efficacy fails to replicate in humans. | Press coverage frames as a human treatment; species gap not discussed; only one lab; no PK/PD bridging data |
| "Subgroup analysis shows [drug] works in [population]" | Treat as exploratory unless pre-specified with formal interaction test. | Reported separately within subgroup without interaction p; many subgroups tested; main effect was null |
| "Adherent patients had better outcomes" | Suspect healthy adherer bias; check for ITT analysis or comparison across treatment arms. | Per-protocol or as-treated analysis only; no comparison of adherent vs non-adherent within placebo arm |

**Reference for absolute-risk derivation:** `skills/statistical-analysis/scripts/effect_interpreter.py` provides `risks_to_arr_nnt(risk_control, risk_treated)` to compute ARR, RRR, RR, and NNT from arm-level event rates.
