"""
Pytest fixtures for research-paper-summarizer validation tests.

Provides reusable test data for:
- Sample text with statistics
- Summary markdown files
- YAML summary data
- Section marker content
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


# ============================================================================
# Sample Text Fixtures
# ============================================================================


@pytest.fixture
def sample_text_with_statistics() -> str:
    """Sample research text with various statistics."""
    return """
    The treatment group showed significant improvement compared to control
    (p = 0.003). We enrolled n = 120 patients in a randomized controlled trial.

    Primary outcomes demonstrated a 2.3-fold increase in response rate with
    95% CI: 1.5-3.2. The hazard ratio for survival was HR = 0.67 (p < 0.001).

    Secondary analysis revealed an odds ratio OR = 2.1 for positive response.
    The effect size was moderate (Cohen's d = 0.45). Mean improvement was
    23.5 ± 4.2 points on the validated scale.

    Correlation between biomarker levels and outcome was significant (r = 0.72).
    Patients showed a 45% reduction in symptom severity.
    """


@pytest.fixture
def sample_text_review_article() -> str:
    """Sample abstract from a review article."""
    return """
    This systematic review and meta-analysis examined the published literature
    on treatment efficacy across 45 randomized controlled trials. We performed
    a comprehensive review of databases including PubMed and Cochrane. The
    pooled analysis of 12,500 patients demonstrated significant benefits.
    Our synthesis of the evidence supports current treatment guidelines.
    """


@pytest.fixture
def sample_text_compbio() -> str:
    """Sample abstract from a computational biology paper."""
    return """
    We developed a machine learning pipeline for RNA-seq differential expression
    analysis. Our bioinformatics approach utilized deep learning algorithms to
    process single-cell transcriptome data from 50,000 cells. The computational
    workflow integrated multi-omics datasets including proteome and metabolome
    measurements. Benchmark testing showed 95% accuracy on validation datasets.
    """


@pytest.fixture
def sample_text_cellmolbio() -> str:
    """Sample abstract from a cell/molecular biology paper."""
    return """
    We investigated the molecular mechanism of drug resistance using CRISPR
    knockout in HeLa cell lines. Western blot analysis revealed increased
    phosphorylation of the signaling pathway. In vitro experiments demonstrated
    that protein overexpression led to enhanced cell survival. Immunoprecipitation
    confirmed the protein-protein interaction hypothesis.
    """


@pytest.fixture
def sample_text_general() -> str:
    """Sample abstract from a general research paper."""
    return """
    This prospective cohort study followed 500 patients over 5 years.
    Clinical outcomes were assessed using validated instruments. Statistical
    analysis was performed using standard methods. Results indicate significant
    associations between exposure and outcome variables.
    """


# ============================================================================
# Summary Markdown Fixtures
# ============================================================================


@pytest.fixture
def valid_summary_content() -> str:
    """Valid summary markdown content with all required sections."""
    return """# Research Paper Summary

## 1. Executive Summary

This study investigated the efficacy of a novel treatment approach in patients
with chronic disease. The randomized controlled trial enrolled 240 participants
and demonstrated significant improvements in primary outcomes (p < 0.001) with
a 2.5-fold increase in response rate.

<!-- SECTION: executive_summary COMPLETE -->

## 2. Key Findings

The primary analysis showed:
- Significant improvement in symptom scores (p = 0.003, n = 120/group)
- Response rate of 67% vs 28% in control (Figure 1A)
- Sustained benefit at 12-month follow-up (Table 2)

<!-- SECTION: key_findings COMPLETE -->

## 3. Methods Summary

### Study Design
Randomized, double-blind, placebo-controlled trial with 1:1 allocation.

### Sample Size
n = 240 total (120 per group), powered at 80% for primary endpoint.

<!-- SECTION: methods COMPLETE -->

## 4. Results Analysis

"The magnitude of improvement exceeded our expectations," noted lead author.

Key statistics:
- HR = 0.65 (95% CI: 0.48-0.88)
- NNT = 4 for clinical response
- Effect maintained across subgroups (Figure 2B)

<!-- SECTION: results COMPLETE -->

## 5. Critical Assessment

### Limitations

The study has several limitations including single-center design, relatively
short follow-up period, and exclusion of patients with comorbidities.

### Strengths

Rigorous methodology, pre-registered protocol, intention-to-treat analysis.

<!-- SECTION: assessment COMPLETE -->

## 10. One-Paragraph Synthesis

This well-designed randomized trial provides compelling evidence for the efficacy
of the novel treatment approach in chronic disease management. The significant
improvements in primary outcomes, sustained benefits at follow-up, and favorable
safety profile support consideration of this therapy in clinical practice. While
limitations exist, the robust methodology and consistent findings across subgroups
strengthen confidence in the results.

---
"""


@pytest.fixture
def invalid_summary_content() -> str:
    """Invalid summary markdown with pending sections and missing content."""
    return """# Research Paper Summary

## 1. Executive Summary

Brief overview.

<!-- SECTION: executive_summary PENDING -->

## 2. Key Findings

{{KEY_FINDINGS_PLACEHOLDER}}

<!-- SECTION: key_findings PENDING -->

## 3. Methods Summary

<!-- SECTION: methods PENDING -->

## 10. One-Paragraph Synthesis

Short.

---
"""


# ============================================================================
# YAML Summary Fixtures
# ============================================================================


@pytest.fixture
def valid_yaml_data() -> dict:
    """Valid YAML summary data structure."""
    return {
        "metadata": {
            "title": "Efficacy of Novel Treatment in Chronic Disease: A Randomized Trial",
            "authors": "Smith J, Jones A, Williams B, et al.",
            "journal": "Nature Medicine",
            "year": 2024,
            "doi": "10.1038/nm.12345",
            "article_type": "Primary Research",
        },
        "overview": """This randomized controlled trial investigated the efficacy of a novel
        treatment approach in 240 patients with chronic disease. The study demonstrated
        significant improvements in primary outcomes with sustained benefits at 12-month
        follow-up, suggesting potential for clinical implementation.""",
        "key_findings": [
            {
                "finding": "Primary outcome showed 2.5-fold improvement in response rate",
                "statistics": "p < 0.001, 95% CI: 1.8-3.4",
                "figure_ref": "Figure 1A",
            },
            {
                "finding": "Symptom scores decreased significantly in treatment group",
                "statistics": "p = 0.003, Cohen's d = 0.68",
                "figure_ref": "Figure 2",
            },
            {
                "finding": "Benefits maintained at 12-month follow-up assessment",
                "statistics": "HR = 0.65 (0.48-0.88)",
                "figure_ref": "Table 3",
            },
        ],
        "key_figures": [
            {
                "number": "Figure 1",
                "title": "Primary endpoint analysis",
                "importance": "Shows main efficacy results",
            },
            {
                "number": "Table 2",
                "title": "Baseline characteristics",
                "importance": "Demonstrates group balance",
            },
        ],
        "methods": {
            "study_design": "Randomized, double-blind, placebo-controlled trial",
            "sample_size": "n = 240 (120 per group)",
            "key_techniques": "Validated symptom scales, biomarker analysis",
            "statistical_analysis": "ITT analysis, Cox regression, mixed models",
        },
        "limitations": {
            "author_stated": [
                "Single-center design limits generalizability",
                "12-month follow-up may not capture long-term effects",
            ],
            "additional": [
                "Exclusion of patients with comorbidities",
            ],
        },
        "implications": "Results support consideration of novel treatment in clinical practice",
        "synthesis": """This well-designed randomized trial provides compelling evidence for
        treatment efficacy. The significant improvements, sustained benefits, and favorable
        safety profile support clinical implementation while acknowledging limitations.""",
    }


@pytest.fixture
def invalid_yaml_data() -> dict:
    """Invalid YAML summary data with missing required fields."""
    return {
        "metadata": {
            "title": "Short",  # Too short
            # Missing authors, year
        },
        "overview": "Brief",  # Too short
        "key_findings": [
            {"finding": "One"},  # Too short, only 1 finding
        ],
        # Missing methods, limitations
    }


# ============================================================================
# Section Marker Fixtures
# ============================================================================


@pytest.fixture
def content_with_markers() -> str:
    """Content with various section markers."""
    return """# Document

## Section 1
Content here.
<!-- SECTION: introduction COMPLETE -->

## Section 2
More content.
<!-- SECTION: methods PENDING -->

## Section 3
Final content.
<!-- SUBSECTION: results_primary COMPLETE -->
<!-- SUBSECTION: results_secondary PENDING -->
<!-- SECTION: discussion SKIPPED -->
"""


