# Skeleton Configuration by Article Type

This file defines how to customize `summary-skeleton.md` for each article type.

---

## General Research

```yaml
METHODS_SECTION_TITLE: "Experimental Approach"
METHODS_SUBSECTION_1_TITLE: "Study Design"
METHODS_SUBSECTION_2_TITLE: "Key Methods & Controls"
ARTICLE_SPECIFIC_SECTION_TITLE: "Implications & Applications"
ARTICLE_SPECIFIC_SUBSECTIONS: |
  ### Clinical/Practical Relevance
  <!-- SUBSECTION: clinical_relevance PENDING -->

  ### Suggested Follow-up Studies
  <!-- SUBSECTION: followup_studies PENDING -->
```

---

## Review Article

```yaml
METHODS_SECTION_TITLE: "Review Scope & Methodology"
METHODS_SUBSECTION_1_TITLE: "Search Strategy & Inclusion Criteria"
METHODS_SUBSECTION_2_TITLE: "Evidence Synthesis Approach"
ARTICLE_SPECIFIC_SECTION_TITLE: "Field Landscape & Evidence Assessment"
ARTICLE_SPECIFIC_SUBSECTIONS: |
  ### Consensus vs Controversy
  <!-- SUBSECTION: consensus_controversy PENDING -->

  ### Evidence Quality Assessment
  <!-- SUBSECTION: evidence_quality PENDING -->

  ### Key Reference Mining
  <!-- SUBSECTION: reference_mining PENDING -->
```

---

## Cell & Molecular Biology

```yaml
METHODS_SECTION_TITLE: "Model Systems & Experimental Design"
METHODS_SUBSECTION_1_TITLE: "Model Systems"
METHODS_SUBSECTION_2_TITLE: "Key Techniques & Assays"
ARTICLE_SPECIFIC_SECTION_TITLE: "Mechanistic Insights & Translational Potential"
ARTICLE_SPECIFIC_SUBSECTIONS: |
  ### Molecular Mechanisms
  <!-- SUBSECTION: molecular_mechanisms PENDING -->

  ### Cancer Hallmarks (if applicable)
  <!-- SUBSECTION: cancer_hallmarks PENDING -->

  ### Translational Assessment
  <!-- SUBSECTION: translational_assessment PENDING -->
```

---

## Computational Biology / Bioinformatics

```yaml
METHODS_SECTION_TITLE: "Data & Computational Approach"
METHODS_SUBSECTION_1_TITLE: "Data Foundation & Sources"
METHODS_SUBSECTION_2_TITLE: "Computational Pipeline & Algorithms"
ARTICLE_SPECIFIC_SECTION_TITLE: "Validation & Reproducibility"
ARTICLE_SPECIFIC_SUBSECTIONS: |
  ### Benchmarking & Validation
  <!-- SUBSECTION: benchmarking PENDING -->

  ### Reproducibility Assessment
  <!-- SUBSECTION: reproducibility PENDING -->

  ### Code & Data Availability
  <!-- SUBSECTION: code_data_availability PENDING -->
```

---

## Usage

When creating a skeleton for a specific paper:

1. Read `summary-skeleton.md`
2. Look up the article type in this configuration
3. Replace all `{{PLACEHOLDER}}` values with the article-type-specific values
4. Fill in metadata (TITLE, TIMESTAMP, FILENAME, PAGE_COUNT, ARTICLE_TYPE)
5. Write the customized skeleton to `{original_filename}_summary.md`
