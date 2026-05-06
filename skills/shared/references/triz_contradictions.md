# TRIZ Contradiction Resolution (Pharma & Biotech)

> Shared reference for resolving technical trade-offs in target validation, modality selection, and ideation.
> Version: 1.0.0
> Used by: target-validation (Stage 4 modality, Stage 5 roadmap), scientific-brainstorming (TRIZ method)

---

## 1. Contradiction Framing

A **technical contradiction** has the form:

> *Improving parameter X worsens parameter Y.*

When a barrier or risk in a validation report fits this template, do not accept the trade-off as fixed. State both sides explicitly, then attempt resolution before flagging the modality as Low feasibility or the risk as unmitigable.

**Ideal Final Result (IFR):** before picking a principle, write the single sentence describing the perfect outcome with zero cost, zero harm, and zero complexity. Working backwards from the IFR reveals which constraints are real (physics, regulatory) and which are assumed (current practice). Most pharma trade-offs collapse one constraint when the IFR is articulated.

---

## 2. Pharma-Relevant Contradictions

Common contradictions encountered in target validation and modality selection. Each row links to candidate inventive principles in §3.

| Improving (X) | Worsens (Y) | Candidate principles |
|---|---|---|
| Potency at primary target | Selectivity over paralogs/off-targets | Asymmetry, Local Quality, Extraction |
| Brain (CNS) penetration | Metabolic stability / oral bioavailability | Segmentation (prodrug), Prior Action, Dynamization |
| On-target activity | Off-target liability / tox | Local Quality, Nesting, Periodic Action |
| Oral bioavailability | Aqueous solubility | Segmentation (prodrug), Universality |
| Plasma half-life | Clearance / wash-out flexibility | Periodic Action, Dynamization, Self-Service |
| Broad efficacy (multi-mechanism) | Tissue/cell-type selectivity | Local Quality, Asymmetry, Nesting |
| Selectivity for one paralog | Compensation by redundant family member | Universality (multi-target), Extraction |
| Tumor exposure (delivery) | Healthy-tissue exposure (safety) | Local Quality, Nesting, Prior Action |
| Biologic stability in serum | Tissue penetration / diffusion | Segmentation, Dynamization |
| Strong PD effect | Reversibility / safety margin | Dynamization, Periodic Action |
| Genetic specificity (allele-selective) | Manufacturability / cost | Universality, Self-Service |

If the contradiction in your case is not in this table, write it in the same form and pick from §3 by analogy.

---

## 3. Inventive Principles (Pharma Examples)

A focused subset of TRIZ's 40 principles, selected for relevance to small-molecule, biologic, and modality engineering. Use these as candidate moves, not prescriptions.

| # | Principle | Pharma application |
|---|---|---|
| **1** | **Segmentation** — divide a system into independent parts | Prodrug strategies that separate transport from activation; bispecific antibodies that segment binding from effector function. |
| **2** | **Extraction** — separate an interfering component or property | Engineer out the moiety responsible for hERG / off-target binding while retaining on-target pharmacophore. Enantiomer separation when one isomer drives toxicity. |
| **3** | **Local Quality** — vary conditions locally rather than globally | Tissue-targeted delivery (LNP tropism, antibody-drug conjugates, GalNAc-siRNA) so that exposure rises only where the target sits. |
| **4** | **Asymmetry** — introduce useful asymmetry into a symmetric system | Allosteric inhibitors instead of orthosteric (paralog-selective by exploiting non-conserved pockets); covalent warheads targeting non-conserved cysteines. |
| **5** | **Nesting** — place one system inside another | Encapsulate active payload inside a delivery vehicle (LNP, PEGylated nanoparticle, AAV capsid) so that pharmacology only manifests after the carrier reaches its niche. |
| **6** | **Prior Action** — perform required changes in advance | Pre-functionalize a prodrug for esterase activation; pre-target with a hapten + secondary radioligand; biorthogonal click priming. |
| **7** | **Dynamization** — let the system change to match each stage | Stimulus-responsive release (pH, redox, MMP-cleavable linkers); switchable degraders (PROTAC dosing pulses); inducible expression. |
| **8** | **Universality** — make one element perform multiple functions | Multi-target ligands (kinase polypharmacology) when redundancy is the disease driver; single biologic that combines targeting and effector domains. |
| **9** | **Periodic Action** — replace continuous action with pulsed | Pulsatile dosing to evade resistance, reset receptor occupancy, or restore safety margin (intermittent androgen deprivation, drug holidays for kinase inhibitors). |
| **10** | **Self-Service** — system performs its own auxiliary function | Self-targeting biologics (cell-penetrating + nuclear-localizing peptides built in); auto-induced degradation tags; self-amplifying mRNA. |
| **11** | **Inversion / The Other Way Round** — invert the action, sequence, or goal | Action-flip: replace inhibition with degradation (PROTAC); replace activation with sequestration (decoy receptors). Goal-flip: instead of blocking the disease driver, restore the missing function (gene therapy, enzyme replacement); start from phenotype, work back to target. |
| **12** | **Parameter Changes** — change physical or chemical state | Formulation state shift (oral solid → IV solution; IV → subcutaneous depot); polymorph or salt selection for solubility; co-crystal engineering; lyophilization for stability; isotopic substitution (deuteration) for metabolic robustness. |

The classical TRIZ catalog has 40 principles; the 12 above cover the majority of pharma contradictions. For exhaustive listings, see [TRIZ Journal](https://www.triz-journal.com/).

---

## 4. How to Apply

A 4-step recipe. Use this in `target-validation` Stage 4 (modality barriers) and Stage 5 (roadmap risk mitigation), or as the convergent step inside a `scientific-brainstorming` session that surfaced a trade-off.

1. **State the contradiction explicitly** in `improving X worsens Y` form. If you cannot write it that way, the problem is not a contradiction — it is a missing-data or feasibility problem, and TRIZ does not apply.
2. **Write the Ideal Final Result** in one sentence ("the drug acts only on diseased cells, requires no administration, and has no off-target binding"). Do not constrain to current modalities.
3. **Pick 2–3 candidate principles** from the §2 row that matches your contradiction, or by analogy. Translate each principle into a concrete modality move (e.g., Local Quality → "ADC with tumor-restricted antigen"; Segmentation → "prodrug cleaved by tumor-resident enzyme").
4. **Check feasibility per modality** against existing chemical matter, manufacturability, regulatory precedent. Surface the surviving option as a candidate mitigation in the validation roadmap, not as a guaranteed solution.

If none of the principles produce a feasible move, the contradiction is structural — record it as a hard constraint in the report rather than a soft risk, and revisit the GO/NO-GO tier accordingly.

---

## Quality Flags

| Flag | Meaning | Action |
|------|---------|--------|
| `[CONTRADICTION-RESOLVED]` | A trade-off has a feasible TRIZ resolution path | Surface in roadmap; do not penalize the score for this risk |
| `[CONTRADICTION-STRUCTURAL]` | Trade-off is physical/regulatory and no principle applies | Treat as hard constraint; reflect in tier |
| `[IFR-UNCONSTRAINED]` | Ideal Final Result revealed an assumption is non-binding | Note in discussion; may unlock scope expansion |
