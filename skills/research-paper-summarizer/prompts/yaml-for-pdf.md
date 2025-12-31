# YAML Summary for PDF Generation

Generate a structured YAML summary that feeds into the PDF generator script.

## Source Document

**IMPORTANT**: This visual output is generated from the markdown summary file created in Phase 1.

Before generating the YAML:
1. Read the markdown summary file (`{original_filename}_summary.md`)
2. Identify which summarizer type was used (check the section headers)
3. Use the appropriate article-type mapping below
4. Extract and restructure the content into YAML format

---

## Article-Type-Specific Mappings

### General Research Papers
*Source: `general_researcher_summarizer.md`*

| Markdown Section | YAML Field |
|------------------|------------|
| Paper title/authors | `metadata` |
| Key Figures/Tables | `key_figures` |
| Executive Summary | `overview` |
| Results - Structured Breakdown | `key_findings` |
| Experimental Approach | `methods` |
| Critical Analysis - Limitations | `limitations` |
| Bigger Picture Context | `implications` |
| Actionable Takeaways | `relevance_notes` |

### Review Articles
*Source: `review_article_summarizer.md`*

| Markdown Section | YAML Field |
|------------------|------------|
| Paper title/authors | `metadata` |
| Key Figures/Tables (conceptual diagrams) | `key_figures` |
| Executive Summary | `overview` |
| Core Arguments & Evidence Synthesis | `key_findings` (as themes) |
| Scope & Framing | `methods` (as scope) |
| Critical Analysis - Limitations/Biases | `limitations` |
| Future Directions | `implications` |
| Reference Mining | `key_references` (new field) |
| Practical Extraction | `relevance_notes` |

### Computational Biology / Bioinformatics
*Source: `compbio_bioinformatic_summarizer.md`*

| Markdown Section | YAML Field |
|------------------|------------|
| Paper title/authors | `metadata` |
| Key Figures/Tables | `key_figures` |
| Executive Summary | `overview` |
| Results - Structured Breakdown | `key_findings` |
| Computational Approach | `methods` |
| Data Foundation | `data_sources` (new field) |
| Reproducibility Assessment | `reproducibility` (new field) |
| Critical Analysis - Limitations | `limitations` |
| Bigger Picture | `implications` |
| Practical Implementation | `relevance_notes` |

### Cell & Molecular Biology
*Source: `cellmolbio_summarizer.md`*

| Markdown Section | YAML Field |
|------------------|------------|
| Paper title/authors | `metadata` |
| Key Figures/Tables | `key_figures` |
| Executive Summary | `overview` |
| Results - Structured Breakdown | `key_findings` |
| Experimental Design & Methods | `methods` |
| Model Systems | `model_systems` (new field) |
| Mechanistic Depth | `mechanism` (new field) |
| Critical Analysis - Limitations | `limitations` |
| Translational Assessment | `implications` |
| Practical Extraction | `relevance_notes` |

---

## Universal Mapping (All Types)

| Markdown Summary Section | YAML Field |
|--------------------------|------------|
| Paper title/authors (header) | `metadata` |
| Key Figures/Tables | `key_figures` |
| Executive Summary | `overview` |
| Results - Structured Breakdown | `key_findings` |
| Experimental Approach / Methods | `methods` |
| Critical Analysis - Limitations | `limitations` |
| Bigger Picture / Implications | `implications` |
| Actionable Takeaways (if present) | `relevance_notes` |

## Three-Step Workflow

1. **Read markdown summary** - The pre-analyzed summary file
2. **Claude generates YAML** - Transform markdown into YAML format below
3. **User runs Python script** - Generate brand-compliant PDF with automatic figure extraction

## YAML Output Format

### Core Structure (All Article Types)

```yaml
metadata:
  title: "[Full paper title - exactly as published]"
  authors: "[First Author et al.]"
  journal: "[Journal Name]"
  year: [YYYY]
  doi: "[DOI]"
  article_type: "[General Research | Review | Computational | Cell & Mol Bio]"
  summarizer_used: "[general | review | compbio | cellmolbio]"
  pmid: "[PMID if available, otherwise omit]"

key_figures:
  - number: "Figure 1"
    title: "[Concise description of what figure shows]"
    importance: "[Why this figure is essential to the paper's argument]"
    key_findings: "[Main quantitative takeaway, e.g., '3.2-fold increase, p<0.001']"
  - number: "Figure 3B"
    title: "[...]"
    importance: "[...]"
    key_findings: "[...]"

overview: |
  [2-3 sentences: What question did they ask? What approach? What main finding?
  This should be a self-contained summary a reader could understand without
  reading anything else.]

key_findings:
  - finding: "[Finding 1 - complete sentence describing the result]"
    statistics: "p = X.XX, n = X, 95% CI: X–X, effect size = X"
    figure_ref: "Figure 2A"
  - finding: "[Finding 2]"
    statistics: "[all relevant statistics]"
    figure_ref: "Table 1"

methods:
  study_design: "[RCT, cohort, case-control, preclinical, in vitro, etc.]"
  model_system: "[Be specific: cell line names, mouse strains, patient cohort details]"
  sample_size: "[n per group, total N, number of replicates]"
  key_techniques: "[Main experimental methods, assays, platforms]"
  statistical_analysis: "[Tests used, multiple comparison corrections, software]"
  key_parameters: "[Doses, timepoints, thresholds, cutoffs used]"

limitations:
  author_stated:
    - "[Limitation 1 as acknowledged by authors]"
    - "[Limitation 2]"
  additional:
    - "[Any obvious methodological concerns not acknowledged]"
    - "[Generalizability issues]"

implications: |
  [What does this mean for the field? What future directions do authors propose?
  What questions remain unanswered?]

relevance_notes: |
  [OPTIONAL: How does this paper relate to the user's specific research interests?
  Key insights for their projects? Comparisons to their approaches?]
```

### Article-Type-Specific Extensions

**Add these fields based on article type:**

#### Review Articles - Additional Fields
```yaml
# Replace methods with scope
scope:
  review_type: "[Systematic | Narrative | Meta-analysis | Scoping]"
  search_strategy: "[Databases searched, date range, keywords]"
  inclusion_criteria: "[What papers were included/excluded]"
  papers_reviewed: "[Number of papers synthesized]"

# Add key references section
key_references:
  - citation: "[Author et al. (Year)]"
    doi: "[DOI]"
    relevance: "[Why this paper is important to read]"
  - citation: "[...]"
    doi: "[...]"
    relevance: "[...]"

# Modify key_findings for thematic organization
key_findings:
  - theme: "[Theme 1 name]"
    finding: "[Consensus or key argument]"
    evidence_strength: "[Strong consensus | Emerging | Controversial]"
  - theme: "[Theme 2 name]"
    finding: "[...]"
    evidence_strength: "[...]"
```

#### Computational Biology - Additional Fields
```yaml
# Add data sources section
data_sources:
  - source: "[GEO/SRA/ENA/etc.]"
    accession: "[Accession number]"
    data_type: "[RNA-seq, WGS, scRNA-seq, etc.]"
    sample_size: "[N samples]"

# Add reproducibility section
reproducibility:
  code_available: true/false
  repository: "[GitHub/Zenodo URL]"
  container: "[Docker/Singularity available?]"
  documentation: "[Excellent | Good | Partial | Poor]"
  dependencies: "[Key packages/versions]"

# Modify methods for computational focus
methods:
  pipeline_overview: "[High-level description of computational approach]"
  key_algorithms: "[Main methods/tools used]"
  validation_strategy: "[How results were validated]"
  performance_metrics: "[AUC, F1, accuracy, etc.]"
  hardware: "[GPU/HPC requirements if noted]"
```

#### Cell & Molecular Biology - Additional Fields
```yaml
# Add model systems section
model_systems:
  in_vitro:
    - name: "[Cell line name]"
      type: "[Immortalized | Primary | Patient-derived]"
      validated: true/false
  in_vivo:
    - name: "[Mouse strain or model]"
      type: "[Xenograft | Syngeneic | GEM | PDX]"
      sample_size: "[n per group]"
  patient_samples:
    source: "[Cohort/biobank name]"
    n: "[Number of samples]"
    characteristics: "[Key clinical features]"

# Add mechanism section
mechanism:
  pathway: "[Pathway name]"
  upstream: "[Upstream regulators identified]"
  downstream: "[Downstream effectors]"
  key_interactions: "[Protein-protein interactions, etc.]"
  evidence_type: "[Correlative | Loss-of-function | Gain-of-function | Epistasis]"

# Add hallmarks section (for cancer papers)
hallmarks_addressed:
  - "Sustained proliferative signaling"
  - "Resisting cell death"
  # [List only those addressed]

# Add translation section
translation:
  stage: "[Target validation | Lead compound | Preclinical | Clinical]"
  druggable: true/false
  existing_drugs: "[Any existing drugs for this target?]"
  biomarker_potential: "[Diagnostic/prognostic potential]"
```

## Figure Selection Criteria

**Mark a figure as "key" if it:**
- Contains primary outcome data or the central finding
- Shows the main mechanism, model, or conceptual framework
- Presents dose-response, time-course, or survival data critical to conclusions
- Is referenced multiple times in Results/Discussion
- Contains data needed to evaluate the paper's claims

**Do NOT mark as key:**
- Supplementary figures (unless absolutely essential)
- Schematic diagrams showing only known biology
- Quality control panels (unless QC is the focus)
- Figures duplicating information shown elsewhere
- Graphical abstracts

**Target: 2-5 key figures per paper**

## Statistics Formatting

Format all statistics consistently:
- P-values: `p = 0.003` or `p < 0.001`
- Confidence intervals: `95% CI: 1.2–3.4`
- Effect sizes: `Cohen's d = 0.8`, `HR = 0.45`, `OR = 2.3`
- Sample sizes: `n = 24/group`, `N = 156 total`
- Fold changes: `2.3-fold increase`
- Percentages: `72% (95% CI: 65–79%)`

## Article Type Adjustments

### By Summarizer Type

| Article Type | Key Adjustments |
|--------------|-----------------|
| **General Research** | Standard core structure; include actionable takeaways |
| **Review Article** | Replace `methods` with `scope`; use thematic `key_findings`; add `key_references` |
| **Computational Biology** | Add `data_sources` and `reproducibility`; modify `methods` for pipeline focus |
| **Cell & Mol Bio** | Add `model_systems`, `mechanism`, `hallmarks_addressed`, `translation` |

### Special Cases

| Condition | Additional Adjustments |
|-----------|------------------------|
| **Preprint** | Add `preprint: true` and `preprint_server: "[bioRxiv/medRxiv/etc.]"` to metadata |
| **Meta-analysis** | Use Review format; include forest plot in key_figures; add heterogeneity stats (I², Q) |
| **Clinical Trial** | Add `trial_registration`, `phase`, `primary_endpoints`, `secondary_endpoints`, `adverse_events` |
| **Methods Paper** | Use Comp Bio format; emphasize protocol details, validation, benchmarks |

### Figure Selection by Article Type

**General Research / Cell & Mol Bio:**
- Primary outcome data figures
- Mechanism/pathway diagrams
- Dose-response or time-course data
- Survival curves (if applicable)

**Review Articles:**
- Conceptual models or frameworks
- Summary tables comparing studies
- Timeline of field developments
- Visual abstracts

**Computational Biology:**
- Pipeline/workflow diagrams
- Benchmark comparison charts
- Performance metric visualizations
- Validation plots

## Running the PDF Generator

After generating YAML, instruct user:

```bash
# Save the YAML output as summary.yaml, then run:

# With automatic figure extraction from source paper:
python ~/.claude/skills/research-paper-summarizer/scripts/generate_summary_pdf.py \
    --yaml summary.yaml \
    --source original_paper.pdf \
    --output my_summary.pdf

# With pre-extracted figures directory:
python ~/.claude/skills/research-paper-summarizer/scripts/generate_summary_pdf.py \
    --yaml summary.yaml \
    --figures my_figures/ \
    --output my_summary.pdf

# YAML only (no figures):
python ~/.claude/skills/research-paper-summarizer/scripts/generate_summary_pdf.py \
    --yaml summary.yaml \
    --output my_summary.pdf
```

## Dependencies

User needs these Python packages:
```bash
pip install reportlab pyyaml Pillow pymupdf
```
