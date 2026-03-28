# Prompt 1

<optimized_prompt>
ROLE
You are an expert immunologist and RNA therapeutics researcher with deep knowledge of CD4+ T helper cell biology, Th17 differentiation programs, and siRNA target selection. You have particular expertise in the molecular distinctions between pathogenic and non-pathogenic Th17 cells, the transcriptional and metabolic programs that drive Th17 pathogenicity, and the translational considerations for selecting therapeutic knockdown targets.
CONTEXT
This research supports a therapeutic program developing aptamer-siRNA conjugates that deliver siRNA payloads specifically to pathogenic Th17 cells. The delivery and cell-targeting problems are solved — assume the conjugate reaches pathogenic Th17 cells with functional siRNA payload. The open question is: which gene(s) should the siRNA target?
The therapeutic goal is one or both of:

Phenotype reversion: Knock down a target that maintains the pathogenic program, causing the cell to revert toward a non-pathogenic, regulatory, or anergic state — effectively reprogramming rather than killing.
Selective elimination: Knock down a target that is essential for pathogenic Th17 survival but dispensable for non-pathogenic Th17 and other T cell subsets — effectively depleting the pathogenic population while preserving protective immunity.

The ideal target would have a wide therapeutic window: high expression and functional importance in pathogenic Th17 cells, with low expression or redundant function in non-pathogenic Th17 cells, Tregs, and other lymphocyte populations. The results of this research will inform target selection for preclinical development, so the analysis must be grounded in published experimental evidence, not speculative pathway reasoning alone.
TASK
Conduct a systematic research investigation to identify, characterize, and prioritize candidate siRNA targets for knockdown in pathogenic Th17 cells. The investigation should proceed through these phases:
Phase 1 — Define the pathogenic Th17 molecular signature
Establish the current consensus on what molecularly distinguishes pathogenic from non-pathogenic Th17 cells. Cover transcription factors, cytokine profiles (including the GM-CSF/IL-10 axis), surface markers, metabolic programs (glycolysis vs. oxidative phosphorylation), and epigenetic features. Ground this in key datasets — particularly single-cell transcriptomic studies (e.g., Gaublomme et al., Kuchroo lab work) and the TGF-β1 vs. TGF-β3 differentiation axis studies. Identify which molecular features are drivers of pathogenicity versus markers of it — this distinction is critical for target selection.
Phase 2 — Identify candidate knockdown targets across functional categories
Systematically identify candidate targets organized by functional class:

Transcription factors: Master regulators and co-factors that maintain the pathogenic program (e.g., RORγt isoform-specific roles, BATF, IRF4, BHLHE40, T-bet co-expression, STAT3 downstream effectors). Distinguish between factors required for all Th17 function vs. those specific to pathogenic commitment.
Signaling molecules: Kinases, phosphatases, and adaptor proteins in pathways preferentially active in pathogenic Th17 (e.g., ROCK2, SGK1, mTORC1 components, specific MAPK pathway nodes).
Metabolic regulators: Enzymes or transporters driving the glycolytic/lipogenic program associated with pathogenicity (e.g., HIF-1α, ACC1, CDK5-SMAD3 axis, specific amino acid transporters).
Cytokine and cytokine receptor components: Targets whose knockdown would disrupt autocrine/paracrine pathogenic maintenance loops without broadly immunosuppressing (e.g., IL-23R signaling components, GM-CSF regulatory elements).
Epigenetic modifiers: Writers, readers, or erasers that maintain the pathogenic chromatin state.
Surface receptors and co-stimulatory molecules: Receptors that sustain pathogenic activation or survival signals.
Cell survival and proliferation factors: Targets whose loss would selectively compromise pathogenic Th17 viability.
Any additional categories that emerge from the literature as relevant.

For each candidate, report: gene name and aliases, functional role in pathogenic Th17 biology, experimental evidence for its contribution to pathogenicity (knockdown, knockout, or pharmacological inhibition data), expression differential between pathogenic and non-pathogenic Th17 cells (with data source), known expression in other immune cell types (therapeutic window assessment), and any existing pharmacological or genetic validation.
Phase 3 — Assess siRNA-specific feasibility for top candidates
For the most promising candidates, evaluate practical siRNA considerations: mRNA expression level and stability in Th17 cells, known isoform complexity that could complicate siRNA design, whether transient knockdown (as opposed to permanent knockout) is likely to be therapeutically meaningful for this target, speed of expected phenotype change after knockdown (some transcription factors act quickly, metabolic targets may have delayed effects), and any published siRNA/shRNA/ASO data for this target in T cells or Th17 specifically.
Phase 4 — Disease context mapping
For each high-priority target, identify which autoimmune and inflammatory diseases have the strongest evidence for pathogenic Th17 involvement and would therefore be the most compelling therapeutic indications. Consider: multiple sclerosis, psoriasis, inflammatory bowel disease, rheumatoid arthritis, ankylosing spondylitis, and any others with strong Th17 pathogenic data. Note any disease-specific differences in the pathogenic Th17 program that might affect target selection.
Phase 5 — Prioritized target ranking
Produce a final ranked list of the top 10–15 candidates, scored across these dimensions:

Pathogenic specificity (high expression/function in pathogenic Th17, low in non-pathogenic and other subsets)
Experimental validation strength (knockout/knockdown phenotype data quality and consistency)
Therapeutic window (risk of immunosuppression or off-target effects from knockdown in other cell types)
siRNA feasibility (expression level, isoform simplicity, transient knockdown sufficiency)
Novelty/IP landscape (is this a well-explored target or a differentiated approach)
Reprogramming vs. elimination potential (which therapeutic strategy does this target best support)

For each ranked target, provide a one-paragraph rationale summarizing why it ranks where it does, including the key evidence and the key uncertainties.
REQUIREMENTS

Format: Structured research report with clear phase headings. Within each phase, write in connected prose paragraphs. Use a summary table only for the final Phase 5 ranking.
Evidence grounding: Every target claim must cite specific studies or datasets. Distinguish between direct experimental evidence (knockdown/knockout in Th17) and indirect pathway inference. Flag claims that rest on inference rather than direct data.
Confidence calibration: For each major claim, indicate confidence level — HIGH (multiple independent studies, genetic validation), MEDIUM (single study or pharmacological data only), LOW (pathway inference or preliminary/preprint data). When evidence is conflicting, present both sides rather than picking a winner.
Recency: Prioritize literature from the last 5 years, but include foundational older studies that established key concepts. Flag any findings that are very recent (preprint or 2025) and may not yet be independently replicated.
Scope: Be comprehensive in Phase 2 (cast a wide net), then be selective and rigorous in Phases 3–5 (narrow to the strongest candidates with clear justification for what was cut).

SUCCESS CRITERIA
A successful output would allow a researcher to:

Understand the current molecular definition of pathogenic Th17 and where consensus exists vs. where it remains contested
Have a comprehensive map of the candidate target landscape organized by functional category
Identify the 3–5 strongest candidates for immediate preclinical investigation, with clear reasoning for why these rise above the field
Understand the key knowledge gaps and experimental questions that would need to be addressed for each top candidate
Make an informed decision about whether to pursue a reprogramming strategy, an elimination strategy, or both — based on which targets support which approach

</optimized_prompt>

---

# Prompt 2
<optimized_prompt>
Deep Research: Aptamer-Targetable Surface Receptors on Pathogenic Th17 Cells for siRNA Delivery
Research Question
Conduct a literature review to identify and comparatively evaluate surface proteins on pathogenic Th17 cells (as distinct from homeostatic/non-pathogenic Th17) that could serve as targets for aptamer-mediated siRNA delivery in autoimmune and inflammatory diseases. The goal is a ranked target shortlist with evidence-graded assessments across six defined evaluation criteria.
PICO Framework

Population: Pathogenic Th17 cells — the IL-17A⁺/IFN-γ⁺/GM-CSF⁺ subset implicated in autoimmune pathology (MS, RA, psoriasis, IBD), as opposed to homeostatic IL-17A⁺/IL-22⁺ Th17 cells involved in barrier immunity
Intervention: Aptamer-siRNA chimera (AsiC) or aptamer-conjugated siRNA nanoparticle targeting a surface receptor to achieve receptor-mediated endocytosis and cytoplasmic siRNA release in pathogenic Th17 cells
Comparison: Expression of candidate receptors on non-pathogenic Th17, Th1, Th2, Treg, and non-immune tissues (selectivity window)
Outcome: Identification of surface targets that combine pathogenic Th17 selectivity with demonstrated internalization capacity and aptamer-compatible structure

Scoping Guidance
<entity_collision_warning>
Several candidate targets carry HIGH collision risk in literature searches. Apply disambiguation strategies and negative filters for at least these entities:

CD30 (TNFRSF8): Collides with CD30L (TNFSF8/CD153) and with CD30 in classical Hodgkin lymphoma context. Filter: include Th17 OR T helper context; exclude lymphoma-only studies unless they address receptor biology relevant to Th17
CCR6: The receptor itself vs. CCR6⁺ as a lineage marker — studies using CCR6 purely as a sorting marker may not discuss receptor biology. Need studies addressing CCR6 internalization, structure, or targeting
IL-23R: Collides with IL-23 (the cytokine) and IL-12Rβ1 (shared subunit). Filter for receptor-specific studies
CXCR3: Shared with Th1 cells; ensure studies specifically address Th17 co-expression context
</entity_collision_warning>

<seed_candidates>
Begin the bibliography search anchored to these known candidates, but actively search for novel or emerging targets beyond this list:

CCR6 — canonical pathogenic Th17 marker, but expressed on other cell types
IL-23R — critical for pathogenic Th17 differentiation and maintenance
CD161 (KLRB1) — human Th17 marker with restricted expression
CCR4 — expressed on Th17 but shared with Th2 and Treg
CD30 (TNFRSF8) — described on activated pathogenic Th17; known to internalize
CXCR3 — marks ex-Th17/Th17.1 pathogenic subset
OX40 (TNFRSF4) — activation-induced, demonstrated internalization
ICOS — costimulatory receptor on follicular and pathogenic Th17
PD-1 — expressed on exhausted/chronically activated Th17 in disease tissue
Novel candidates — actively search for recently described surface markers on pathogenic Th17 not in this list, particularly from single-cell RNA-seq or CyTOF profiling studies published 2020-present
</seed_candidates>

Evaluation Criteria (Use as Thematic Framework for Synthesis)
Organize the Phase 3 synthesis around these six themes. For each candidate target, evaluate across all six dimensions with T1-T4 evidence labels:

Pathogenic Th17 Selectivity
Differential expression on pathogenic vs. non-pathogenic Th17 cells. Expression on other T cell subsets (Th1, Th2, Treg, CD8⁺). Expression on non-immune tissues — particularly cardiac, hepatic, neural, and pulmonary. The critical question: how wide is the therapeutic window between pathogenic Th17 and the nearest off-target cell population? Quantify with fold-change data where available from scRNA-seq, flow cytometry, or proteomic studies.
Receptor Internalization Capacity
This is a hard requirement — aptamer-siRNA delivery fails without receptor-mediated endocytosis. For each target: does the receptor constitutively internalize, or only upon ligand binding? What is the internalization rate and recycling kinetics? What endosomal pathway does it enter (clathrin-mediated, caveolae, macropinocytosis)? Is there evidence of endosomal escape or cytoplasmic access? Prioritize targets with demonstrated internalization of bound ligands or antibodies.
Safety and Off-Target Risk
Tissue expression atlas data (GTEx, Human Protein Atlas). Known loss-of-function phenotypes — what happens when this receptor is blocked? Existing clinical data on receptor-targeting therapeutics (antibodies, small molecules) and their adverse event profiles. Immunosuppressive consequences of depleting or silencing pathogenic Th17 specifically.
Aptamer Feasibility
Have aptamers been successfully selected (via SELEX) against this target or its extracellular domain? If not, assess structural features that predict SELEX amenability: defined extracellular domain, stable tertiary structure, sufficient molecular complexity for aptamer recognition, and accessibility in the native membrane-bound conformation. Existing aptamer literature for each target, including any cell-SELEX approaches.
Clinical Precedent
Existing therapeutics targeting this receptor (approved or in clinical trials): antibodies, ADCs, BiTEs, CAR-T, small molecules. This establishes target validation in human disease. Ongoing clinical trials involving aptamers or siRNA targeting Th17-related pathways. Prior aptamer-siRNA chimera programs targeting any surface receptor (as technical precedent).
Structural Accessibility
Extracellular domain architecture: size, glycosylation density, conformational flexibility. Availability of crystal/cryo-EM structures for the extracellular domain. Steric considerations: is the target accessible on the cell surface or buried in the immunological synapse? Potential epitope regions accessible to a ~15 kDa aptamer without steric clash from adjacent surface proteins.

Inclusion/Exclusion Criteria
<inclusion>
- Studies addressing surface protein expression on human Th17 cells (pathogenic subset preferred, total Th17 acceptable)
- Studies characterizing receptor internalization on any cell type (transferable biology)
- Aptamer selection studies (SELEX) targeting surface receptors, especially on immune cells
- Aptamer-siRNA conjugate or chimera delivery studies
- Single-cell profiling (scRNA-seq, CyTOF, CITE-seq) of Th17 heterogeneity
- Clinical trial data for therapeutics targeting candidate receptors
- Publication date: 2015-present preferred; landmark older studies acceptable
</inclusion>
<exclusion>
- Studies on Th17 in non-mammalian species (mouse acceptable for mechanistic validation only; flag as non-human)
- Studies using "Th17" loosely without confirming IL-17 production or lineage markers
- Aptamer studies targeting intracellular proteins (not relevant to surface targeting)
- Reviews and commentaries (use as leads to primary sources only)
</exclusion>
Output Specification
<output_format>
The final report should include:

Comparative Target Evaluation Matrix — a table with candidate targets as rows and the 6 evaluation criteria as columns, scored qualitatively (Strong / Moderate / Weak / Insufficient Data) with T-tier evidence labels. This matrix is the primary deliverable.
Per-target evidence summaries — for each candidate, a concise synthesis (300-500 words) covering all 6 criteria with inline citations and T-tier labels. Organize targets from most to least promising based on composite assessment.
Gap analysis — what critical data is missing for top-ranked candidates? Where are the biggest uncertainties? What experiments would resolve them?
Recommended shortlist — top 3-5 targets ranked by overall suitability, with explicit rationale for ranking and key risks per target.
Limitations section — species translation concerns (mouse vs. human Th17 biology), disease-context specificity, and gaps in the aptamer feasibility literature.

Report length: 4000-8000 words. Write in flowing prose paragraphs, not bullet-point lists, except for the evaluation matrix which should be tabular.
</output_format>
Downstream Context
This report will feed into downstream workflows: the top-ranked targets may be individually profiled using target-intelligence dossiers, scored via target-validation, and the leading candidate will inform aptamer SELEX design. Format evidence grading (T1-T4 labels) for direct consumption by the target-validation scoring pipeline.
</optimized_prompt>

---

# Prompt 3

<optimized_prompt>
Deep Research: Off-Target Consequences of RORC-Targeting siRNA in Tregs and CD8⁺ T Cells
Research Question
Conduct a deep research investigation into the potential adverse consequences of off-target delivery of RORC-targeting siRNA to regulatory T cells (Tregs) and CD8⁺ T cells. Evaluate three mechanistically distinct risk categories: (1) on-pharmacology risk from RORC/RORγt knockdown in cells where RORγt has functional roles, (2) RORC-independent class-effect siRNA toxicities including innate immune activation and RISC pathway disruption, and (3) passenger-strand (sense-strand) mediated off-target gene silencing. The deliverable is a structured risk assessment that informs the safety evaluation of an aptamer-siRNA chimera (AsiC) therapeutic program targeting pathogenic Th17 cells.
PEO Framework

Population: Human Tregs (with particular attention to the RORγt⁺ Treg subset enriched in intestinal lamina propria and inflammatory tissues) and CD8⁺ T cells (with attention to Tc17 and other CD8⁺ subsets with documented RORγt expression)
Exposure: Unintended uptake of an aptamer-siRNA chimera designed to deliver RORC-targeting siRNA to pathogenic Th17 cells — resulting in either (a) productive RORC knockdown in the off-target cell, (b) siRNA-mediated innate immune activation independent of RORC targeting, or (c) passenger-strand loading into RISC causing sequence-specific off-target silencing
Outcome: Functional consequences for the off-target cell population and systemic immune homeostasis — including loss of suppressive function in Tregs, impaired cytotoxic or memory function in CD8⁺ T cells, innate immune activation (type I interferon, inflammatory cytokine induction), and passenger-strand-mediated knockdown of unintended gene targets

Scoping Guidance
<entity_collision_warning>
This topic carries HIGH collision risk across multiple entities. Apply strict disambiguation:

RORC / RORγ / RORγt: RORC is the human gene (RORC, Ensembl: ENSG00000143365). RORγ is the full-length isoform (isoform 1, expressed broadly). RORγt (isoform 2, also called RORγ2) is the truncated thymus/lymphocyte-specific isoform that drives Th17 differentiation. Most Th17-relevant literature refers to RORγt, but searches for "RORC" will return both isoforms and unrelated nuclear receptor studies. The siRNA target sequence determines which isoform(s) are knocked down — if the siRNA targets a region shared by both isoforms, full-length RORγ is also silenced, broadening the off-target biology considerably. Flag studies that do not specify isoform.
RORγt⁺ Tregs: This is a well-characterized subset, NOT a hypothetical population. These are Foxp3⁺RORγt⁺ cells enriched in the colonic lamina propria that suppress intestinal inflammation. Studies on "Tregs" that don't subset by RORγt status may miss the most relevant population. Separate evidence for tTregs (thymic), pTregs (peripherally induced), and RORγt⁺ Tregs specifically.
Tc17 cells: CD8⁺ T cells producing IL-17 that express RORγt. Collides with general "CD8⁺ T cell" literature. Filter for studies that specifically measure RORγt expression or IL-17 production in CD8⁺ populations.
siRNA toxicity: Collides with the broader antisense oligonucleotide (ASO) and RNAi toxicity literatures. Focus on siRNA-specific mechanisms (double-stranded RNA sensing, RISC loading competition, passenger-strand effects) rather than ASO chemistry toxicities (hepatotoxicity from phosphorothioate backbone, etc.) unless the mechanism is shared.
Passenger strand vs. guide strand: Some older literature uses "sense strand" and "antisense strand" instead of "passenger" and "guide." Include both terminologies in searches.
</entity_collision_warning>

Risk Categories (Use as Thematic Framework for Synthesis)
Organize Phase 3 synthesis around these six themes. Each theme represents a distinct risk mechanism. For each, assess both the probability that the risk materializes and the severity of the consequence if it does.
Category 1: RORγt Function in Tregs — What Gets Lost
What transcriptional programs depend on RORγt in Tregs? Focus on the RORγt⁺Foxp3⁺ subset: what happens to these cells when RORγt is deleted or knocked down? Evidence from conditional knockout studies (Rorc^fl/fl × Foxp3-Cre), pharmacological RORγt inhibition, and in vitro knockdown experiments. Key outcomes to assess: suppressive capacity (in vitro suppression assays, in vivo colitis models), expression of anti-inflammatory mediators (IL-10, CTLA-4, ICOS), stability of Foxp3 expression, and gut immune homeostasis. Does RORγt loss in Tregs phenocopy any aspect of intestinal inflammation or autoimmunity? Quantify the fraction of total Tregs that are RORγt⁺ in relevant tissue compartments (gut, inflamed joints, CNS) to estimate the scope of impact.
Category 2: RORγt Function in CD8⁺ T Cells — What Gets Disrupted
What role does RORγt play in CD8⁺ T cell subsets? Characterize Tc17 cells: prevalence, tissue distribution, functional significance, and dependence on RORγt. Does RORγt expression in CD8⁺ cells extend beyond the Tc17 subset — for example, does it play a role in CD8⁺ memory formation, tissue-resident memory (Trm) differentiation, or anti-tumor immunity? Evidence from Rorc knockout or knockdown in CD8⁺ contexts. Assess whether RORγt loss in CD8⁺ T cells would impair cytotoxicity, survival, or recall responses.
Category 3: Isoform Specificity — Full-Length RORγ Collateral Damage
If the siRNA target sequence falls in a region shared between RORγt (isoform 2) and full-length RORγ (isoform 1), both isoforms are silenced. Full-length RORγ is expressed in non-immune tissues including liver, skeletal muscle, kidney, and adipose. What are the consequences of RORγ knockdown in these tissues? Evidence from Rorc germline knockouts, RORγ inverse agonist clinical trials (which typically target both isoforms), and tissue expression atlas data. This risk category is relevant only if the siRNA design does not achieve isoform selectivity — flag whether isoform-selective siRNA design is feasible for RORC.
Category 4: RORC-Independent Innate Immune Activation
siRNA class effects independent of the target gene. Double-stranded RNA sensing by pattern recognition receptors: TLR3 (endosomal dsRNA), TLR7/8 (single-stranded RNA in endosomes — relevant to passenger strand and degradation intermediates), RIG-I and MDA5 (cytoplasmic dsRNA with 5'-triphosphate or blunt ends). Protein kinase R (PKR) activation by dsRNA. Consequences: type I interferon induction, inflammatory cytokine production (TNF-α, IL-6, IL-12), upregulation of MHC and costimulatory molecules. Do chemical modifications (2'-O-methyl, 2'-fluoro, phosphorothioate linkages) used in therapeutic siRNA adequately suppress innate sensing in T cells specifically? Most suppression data comes from hepatocytes or cell lines — is there T cell-specific data? Assess whether the aptamer component of the AsiC adds to or mitigates innate sensing.
Category 5: RISC Pathway Disruption and Endogenous miRNA Competition
Exogenous siRNA competes with endogenous miRNAs for loading into Argonaute proteins (AGO1-4, primarily AGO2 for siRNA). At high intracellular concentrations, therapeutic siRNA can saturate the RISC loading complex, displacing endogenous miRNAs from AGO2 and causing global miRNA derepression. What is the evidence for RISC saturation toxicity in immune cells? What intracellular siRNA concentrations trigger saturation — and are the concentrations expected from off-target AsiC uptake likely to reach this threshold? Are there miRNAs in Tregs or CD8⁺ T cells whose displacement would have particularly severe functional consequences (e.g., miR-155, miR-146a, miR-17-92 cluster)?
Category 6: Passenger-Strand Off-Target Gene Silencing
The sense (passenger) strand of the siRNA duplex can be loaded into RISC and direct sequence-specific silencing of unintended mRNA targets. This risk depends on: (a) efficiency of passenger-strand exclusion during RISC loading (asymmetry of the duplex thermodynamic profile), (b) seed-region complementarity (nucleotides 2-8 of the passenger strand) with 3'-UTRs of off-target genes, and (c) functional significance of any off-target knockdown. What bioinformatic and experimental approaches exist for predicting and validating passenger-strand off-targets? What is the current evidence base for passenger-strand toxicity in clinical siRNA programs? Can passenger-strand activity be mitigated through chemical modification (e.g., abasic substitutions at position 1, 2'-O-methyl modification of seed region)?
Inclusion/Exclusion Criteria
<inclusion>
- Studies on RORγt function in Tregs (conditional knockouts, pharmacological inhibition, siRNA/shRNA knockdown)
- Studies on RORγt expression and function in CD8⁺ T cells, including Tc17 biology
- RORγt⁺Foxp3⁺ Treg characterization studies (frequency, tissue distribution, function)
- siRNA innate immune sensing studies (TLR, RIG-I, PKR pathway activation by siRNA)
- RISC saturation and miRNA competition studies
- Passenger-strand off-target identification and mitigation
- Chemical modification strategies to reduce siRNA toxicity (2'-O-methyl, 2'-F, LNA)
- Clinical RORγt inhibitor trial data (safety signal extrapolation to knockdown context)
- Aptamer-siRNA chimera safety/toxicity data from any target
- Publication date: 2015-present preferred; seminal mechanistic studies from earlier acceptable
- Human and mouse studies (flag species for each finding)
</inclusion>
<exclusion>
- Studies on RORγt in Th17 cells only (unless directly comparing Th17 vs. Treg or CD8⁺ RORγt biology)
- ASO-specific toxicology not shared with siRNA (e.g., phosphorothioate hepatotoxicity, RNase H-dependent mechanisms)
- Aptamer toxicity studies focused on the aptamer component alone (not siRNA payload effects)
- Computational-only passenger-strand prediction studies with no experimental validation (include as T4 evidence if no better data exists)
</exclusion>
Search Strategy Guidance
<search_priorities>
The literature for these six risk categories lives in largely separate bodies of work. Structure the bibliography search in parallel tracks:
Track A — RORγt in non-Th17 cells: Search for RORγt conditional knockout studies in Tregs and CD8⁺ T cells. Key search terms: "RORγt Treg," "Foxp3 RORγt," "RORγt⁺ regulatory T cell," "Tc17 RORγt," "RORC CD8." Cross-reference with Consensus MCP for pre-synthesized findings on RORγt in regulatory T cells.
Track B — RORγ isoform biology and clinical inhibitors: Search for RORγ inverse agonist clinical trials (safety data). Key terms: "RORγt inhibitor clinical trial," "RORγ inverse agonist safety." Check ClinicalTrials.gov entries via ToolUniverse for adverse event profiles.
Track C — siRNA class toxicities: Search for innate immune activation and RISC saturation. Key terms: "siRNA TLR7 activation," "siRNA innate immunity," "RISC saturation miRNA competition," "siRNA off-target seed region." This literature is largely target-agnostic and comes from the RNAi therapeutics field (Alnylam, Arrowhead, Silence Therapeutics programs).
Track D — Passenger-strand effects: Key terms: "siRNA passenger strand off-target," "sense strand RISC loading," "siRNA seed-mediated off-target," "passenger strand mitigation chemical modification."
Track E — T cell-specific siRNA delivery data: Any studies delivering siRNA to T cells (any method) that report functional or toxicity outcomes. Key terms: "siRNA T cell delivery," "aptamer siRNA T cell," "RNAi T lymphocyte."
Search ≥3 databases per track. PubMed as primary, bioRxiv for preprints, Consensus for cross-domain synthesis.
</search_priorities>
Output Specification
<output_format>
Structure the final report as a risk assessment, not a flat literature review:

Risk Assessment Matrix — tabular summary with six risk categories as rows and columns for: mechanism, probability of occurrence (High/Medium/Low with rationale), severity if realized (High/Medium/Low with rationale), quality of evidence (T1-T4 composite), mitigability (existing chemical or design solutions), and key uncertainties.
Per-category evidence synthesis — for each of the six risk categories, a 400-700 word synthesis covering the mechanistic basis, available evidence (with T-tier labels), species translation concerns, and dose-dependency considerations. Write in connected prose paragraphs.
Integrated risk profile — a synthesis section that considers how the six risk categories interact. For example: does innate immune activation in Tregs compound the effect of RORγt knockdown? Does RISC saturation in CD8⁺ T cells interact with any RORγt-dependent gene programs?
Mitigation strategies — for each risk category rated Medium or High, what siRNA design, chemical modification, or delivery optimization strategies could reduce the risk? Cite precedent from clinical siRNA programs.
Critical unknowns and recommended experiments — what data gaps, if filled, would most reduce uncertainty in the overall risk assessment? Prioritize by information value.
Limitations section — species translation issues (mouse Rorc biology vs. human RORC), extrapolation from pharmacological RORγt inhibition to genetic knockdown, and gaps in T cell-specific siRNA toxicity data.

Report length: 5000-8000 words.
</output_format>