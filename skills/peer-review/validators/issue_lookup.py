#!/usr/bin/env python3
"""
Common Issue Lookup for Peer Review

Provides a structured catalog of common peer review issues with deterministic
severity classification and recommendation templates. Based on
references/common_issues.md.

Usage:
    from validators.issue_lookup import lookup_issue, search_issues, ISSUE_CATALOG

    issue = lookup_issue("STAT_01")
    matching = search_issues("p-value")

Author: Claude Scientific Writer Plugin
License: MIT
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class IssueCategory(Enum):
    """Categories of peer review issues."""

    STATISTICAL = "statistical"
    EXPERIMENTAL = "experimental"
    REPRODUCIBILITY = "reproducibility"
    INTERPRETATION = "interpretation"
    PRESENTATION = "presentation"
    STUDY_DESIGN = "study_design"
    REPORTING = "reporting"


class Severity(Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    OPTIONAL = "optional"


@dataclass(frozen=True)
class CommonIssue:
    """
    Cataloged peer review issue with deterministic classification.

    Attributes:
        code: Unique issue identifier (e.g., "STAT_01")
        category: Issue category for grouping
        name: Short descriptive name
        description: Full description of the issue
        detection_hints: Signs that indicate this issue is present
        default_severity: Typical severity classification
        recommendation_template: Template for recommendations with placeholders
    """

    code: str
    category: IssueCategory
    name: str
    description: str
    detection_hints: tuple  # Using tuple for hashability
    default_severity: Severity
    recommendation_template: str


# ============================================================================
# ISSUE CATALOG
# Based on references/common_issues.md
# ============================================================================

ISSUE_CATALOG: Dict[str, CommonIssue] = {
    # =========================================================================
    # STATISTICAL ISSUES (STAT_01 - STAT_06)
    # =========================================================================
    "STAT_01": CommonIssue(
        code="STAT_01",
        category=IssueCategory.STATISTICAL,
        name="P-value misuse",
        description="P-hacking, multiple testing without correction, or misinterpretation of p-values",
        detection_hints=(
            "Suspiciously high proportion of p-values just below 0.05",
            "Many tests performed but no correction mentioned",
            "No effect sizes or confidence intervals reported",
            "Language suggesting p-values indicate strength of effect",
            "Interpreting non-significance as proof of no effect",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Report effect sizes with confidence intervals. Apply appropriate multiple testing corrections ({correction_type}). Pre-register analyses to avoid p-hacking.",
    ),
    "STAT_02": CommonIssue(
        code="STAT_02",
        category=IssueCategory.STATISTICAL,
        name="Inappropriate statistical test",
        description="Parametric tests with violated assumptions, wrong test for data type, or ignoring data structure",
        detection_hints=(
            "No mention of assumption checking",
            "Small sample sizes with parametric tests",
            "Multiple pairwise t-tests instead of ANOVA",
            "Likert scales analyzed with t-tests",
            "Paired data analyzed with unpaired tests",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Check assumptions explicitly (normality, homoscedasticity). Consider {alternative_test} as alternative. Use {correction_method} for multiple comparisons.",
    ),
    "STAT_03": CommonIssue(
        code="STAT_03",
        category=IssueCategory.STATISTICAL,
        name="Pseudoreplication",
        description="Technical replicates treated as biological replicates, inflating apparent sample size",
        detection_hints=(
            "n defined as number of measurements rather than biological units",
            "Multiple cells from same animal counted as independent",
            "No mention of random effects or clustering",
            "Repeated measures not acknowledged",
        ),
        default_severity=Severity.CRITICAL,
        recommendation_template="Define n as biological replicates (animals, patients, independent samples). Use mixed-effects models for nested data. Average technical replicates before analysis.",
    ),
    "STAT_04": CommonIssue(
        code="STAT_04",
        category=IssueCategory.STATISTICAL,
        name="Sample size and power issues",
        description="No sample size justification, underpowered study, or post-hoc power analysis",
        detection_hints=(
            "Small sample sizes (n<30 per group)",
            "No mention of power analysis in methods",
            "Wide confidence intervals suggesting imprecision",
            "Claims of 'no effect' with large p-values and small n",
            "Post-hoc power calculations",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Conduct a priori power analysis based on expected effect size. Report achieved precision (confidence interval width). Acknowledge if study is underpowered.",
    ),
    "STAT_05": CommonIssue(
        code="STAT_05",
        category=IssueCategory.STATISTICAL,
        name="Missing data problems",
        description="Inappropriate handling of missing data, no sensitivity analysis, or unreported missingness",
        detection_hints=(
            "Different n values across analyses without explanation",
            "No discussion of missing data",
            "Simple mean imputation used",
            "No sensitivity analyses",
            "Complete case analysis without justification",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Report extent and patterns of missingness. Use appropriate methods ({imputation_method}). Perform sensitivity analyses comparing complete vs. imputed data.",
    ),
    "STAT_06": CommonIssue(
        code="STAT_06",
        category=IssueCategory.STATISTICAL,
        name="Circular analysis",
        description="Using same data for selection and inference, double-dipping, or HARKing",
        detection_hints=(
            "ROIs or features selected based on results",
            "Unexpected subgroup analyses",
            "Post-hoc analyses not clearly labeled",
            "No data-independent validation",
            "Introduction perfectly predicts findings",
        ),
        default_severity=Severity.CRITICAL,
        recommendation_template="Use independent datasets for selection and testing. Pre-register analyses and hypotheses. Use cross-validation or hold-out datasets. Clearly distinguish confirmatory vs. exploratory analyses.",
    ),
    # =========================================================================
    # EXPERIMENTAL DESIGN ISSUES (EXP_01 - EXP_04)
    # =========================================================================
    "EXP_01": CommonIssue(
        code="EXP_01",
        category=IssueCategory.EXPERIMENTAL,
        name="Lack of appropriate controls",
        description="Missing negative, positive, vehicle, or batch controls",
        detection_hints=(
            "Methods section lists only experimental groups",
            "No mention of controls in figures",
            "Unclear baseline or reference condition",
            "Cross-batch comparisons without controls",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Include {control_type} controls to assess {purpose}. Use vehicle controls matched to experimental treatment. Include batch controls for cross-batch comparisons.",
    ),
    "EXP_02": CommonIssue(
        code="EXP_02",
        category=IssueCategory.EXPERIMENTAL,
        name="Confounding variables",
        description="Systematic differences between groups besides intervention, uncontrolled confounders",
        detection_hints=(
            "Groups differ in multiple characteristics",
            "Samples processed in different batches by group",
            "No randomization of sample order",
            "No mention of blinding",
            "Baseline characteristics differ between groups",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Randomize experimental units to conditions. Block on known confounders. Use blinding to minimize bias. Perform batch correction if needed.",
    ),
    "EXP_03": CommonIssue(
        code="EXP_03",
        category=IssueCategory.EXPERIMENTAL,
        name="Insufficient replication",
        description="Single experiment without replication, small n without justification",
        detection_hints=(
            "Methods state 'experiment performed once'",
            "n=3 with no justification",
            "'Representative image shown' without quantification",
            "Key claims based on single experiment",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Perform independent biological replicates (typically ≥3). Validate key findings in independent cohorts. Report all replicates, not just representative examples. Show individual data points.",
    ),
    "EXP_04": CommonIssue(
        code="EXP_04",
        category=IssueCategory.EXPERIMENTAL,
        name="Temporal and batch effects",
        description="Uncontrolled batch effects, temporal trends, or operator differences",
        detection_hints=(
            "All treatment samples processed on same day",
            "Controls from different time period",
            "No mention of batch or time effects",
            "Different technicians for groups",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Randomize samples across batches/time. Include batch as covariate in analysis. Perform batch correction (ComBat, limma). Include QC samples across batches.",
    ),
    # =========================================================================
    # REPRODUCIBILITY ISSUES (REP_01 - REP_03)
    # =========================================================================
    "REP_01": CommonIssue(
        code="REP_01",
        category=IssueCategory.REPRODUCIBILITY,
        name="Insufficient methodological detail",
        description="Methods not described in sufficient detail for replication",
        detection_hints=(
            "Vague descriptions ('standard protocols were used')",
            "No information on reagent sources",
            "Generic software mentioned without versions",
            "No antibody validation information",
            "Cell lines not authenticated",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Provide detailed protocols. Include reagent vendors, catalog numbers, lot numbers. Report software versions and all parameters. Include antibody validation. Report cell line authentication.",
    ),
    "REP_02": CommonIssue(
        code="REP_02",
        category=IssueCategory.REPRODUCIBILITY,
        name="Data and code unavailability",
        description="No data availability statement, code not provided, or 'available upon request'",
        detection_hints=(
            "Missing data availability statement",
            "No repository accession numbers",
            "Computational methods with no code",
            "'Data available upon request'",
            "No documentation for custom pipelines",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Deposit raw data in appropriate repositories ({repository}). Share analysis code on {platform}. Provide clear documentation and README files. Include environment/requirements files.",
    ),
    "REP_03": CommonIssue(
        code="REP_03",
        category=IssueCategory.REPRODUCIBILITY,
        name="Lack of method validation",
        description="New methods not validated against gold standard, no specificity/sensitivity testing",
        detection_hints=(
            "Novel assays presented without validation",
            "No comparison to existing methods",
            "No positive/negative controls shown",
            "Claims of specificity without evidence",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Validate new methods against established approaches. Show specificity with knockout/knockdown controls. Demonstrate linearity and dynamic range. Report limits of detection.",
    ),
    # =========================================================================
    # INTERPRETATION ISSUES (INT_01 - INT_03)
    # =========================================================================
    "INT_01": CommonIssue(
        code="INT_01",
        category=IssueCategory.INTERPRETATION,
        name="Overstatement of results",
        description="Causal language for correlational data, mechanistic claims without evidence",
        detection_hints=(
            "'X causes Y' from observational data",
            "Mechanism proposed without direct testing",
            "Mouse data presented as relevant to humans without caveats",
            "Broad claims from narrow samples",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Use appropriate language ('associated with' vs. 'caused by'). Distinguish correlation from causation. Acknowledge limitations of model systems. Propose mechanisms as hypotheses.",
    ),
    "INT_02": CommonIssue(
        code="INT_02",
        category=IssueCategory.INTERPRETATION,
        name="Selective reporting",
        description="Cherry-picking results, unreported negative findings, selective analysis reporting",
        detection_hints=(
            "All reported results are significant",
            "'Representative of 3 experiments' with no quantification",
            "Data exclusions not described in methods",
            "Multiple analysis approaches with only one reported",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Report all planned analyses regardless of outcome. Quantify and show variability across replicates. Pre-specify outlier exclusion criteria. Pre-register analysis plan.",
    ),
    "INT_03": CommonIssue(
        code="INT_03",
        category=IssueCategory.INTERPRETATION,
        name="Ignoring alternative explanations",
        description="Preferred explanation without considering alternatives, minimal limitations",
        detection_hints=(
            "Single interpretation presented as fact",
            "Prior contradictory findings not discussed",
            "No consideration of alternative mechanisms",
            "Limitations section minimal or absent",
        ),
        default_severity=Severity.MINOR,
        recommendation_template="Discuss alternative explanations. Address contradictory findings from literature. Acknowledge and discuss limitations thoroughly. Consider and test alternative hypotheses.",
    ),
    # =========================================================================
    # PRESENTATION ISSUES (PRES_01 - PRES_02)
    # =========================================================================
    "PRES_01": CommonIssue(
        code="PRES_01",
        category=IssueCategory.PRESENTATION,
        name="Inappropriate data visualization",
        description="Bar graphs hiding distributions, undefined error bars, misleading axes",
        detection_hints=(
            "Bar graphs with few data points",
            "Unclear what error bars represent",
            "Y-axis doesn't start at zero for ratio data",
            "Dual y-axes with different scales",
            "Red-green color schemes",
        ),
        default_severity=Severity.MINOR,
        recommendation_template="Show individual data points with scatter/box/violin plots. Define error bars (SD, SEM, 95% CI). Start y-axis at zero or indicate breaks. Use colorblind-friendly palettes.",
    ),
    "PRES_02": CommonIssue(
        code="PRES_02",
        category=IssueCategory.PRESENTATION,
        name="Image manipulation concerns",
        description="Excessive processing, spliced gels, duplicated images",
        detection_hints=(
            "Suspicious patterns or discontinuities",
            "Very high contrast with no background",
            "Similar features in different panels",
            "Straight lines suggesting splicing",
        ),
        default_severity=Severity.CRITICAL,
        recommendation_template="Apply adjustments uniformly across images. Indicate spliced gels with dividing lines. Show full, uncropped images in supplementary. Provide original images if requested.",
    ),
    # =========================================================================
    # STUDY DESIGN ISSUES (DES_01 - DES_02)
    # =========================================================================
    "DES_01": CommonIssue(
        code="DES_01",
        category=IssueCategory.STUDY_DESIGN,
        name="Poorly defined hypotheses and outcomes",
        description="No clear hypothesis, primary outcome not specified, outcomes changed post-hoc",
        detection_hints=(
            "Introduction doesn't state clear testable hypothesis",
            "Multiple outcomes with unclear hierarchy",
            "Outcomes in results don't match methods",
            "Exploratory study presented as confirmatory",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="State clear, testable hypotheses. Designate primary and secondary outcomes a priori. Pre-register studies. Apply corrections for multiple outcomes. Clearly distinguish exploratory from confirmatory.",
    ),
    "DES_02": CommonIssue(
        code="DES_02",
        category=IssueCategory.STUDY_DESIGN,
        name="Baseline imbalance and selection bias",
        description="Groups differ at baseline, selection criteria applied differentially, survivorship bias",
        detection_hints=(
            "Table 1 shows significant baseline differences",
            "Inclusion criteria different between groups",
            "Response rate <50% with no analysis",
            "Analysis only includes completers",
        ),
        default_severity=Severity.MAJOR,
        recommendation_template="Report baseline characteristics. Use randomization to ensure balance. Adjust for baseline differences. Report response rates. Consider propensity score matching. Use intention-to-treat analysis.",
    ),
    # =========================================================================
    # REPORTING ISSUES (RPT_01 - RPT_02)
    # =========================================================================
    "RPT_01": CommonIssue(
        code="RPT_01",
        category=IssueCategory.REPORTING,
        name="Incomplete statistical reporting",
        description="Missing test statistics, degrees of freedom, exact p-values, or effect sizes",
        detection_hints=(
            "Only p-values given with no test statistics",
            "p-values reported as p<0.05 rather than exact",
            "No measures of uncertainty",
            "Effect magnitude unclear",
            "n not reported per group",
        ),
        default_severity=Severity.MINOR,
        recommendation_template="Report complete test statistics (t, F, χ² with df). Report exact p-values (except p<0.001). Include 95% confidence intervals. Report effect sizes. Report n for each group.",
    ),
    "RPT_02": CommonIssue(
        code="RPT_02",
        category=IssueCategory.REPORTING,
        name="Methods-results mismatch",
        description="Analyses in results not described in methods, or vice versa",
        detection_hints=(
            "Analyses in results without methodological description",
            "Methods describe experiments not in results",
            "Numbers don't match between sections",
            "Different software mentioned than used",
        ),
        default_severity=Severity.MINOR,
        recommendation_template="Ensure complete concordance between methods and results. Describe all analyses performed in methods. Remove methodological descriptions of experiments not performed.",
    ),
}


def lookup_issue(code: str) -> Optional[CommonIssue]:
    """
    Retrieve issue details by code.

    Args:
        code: Issue code (e.g., "STAT_01")

    Returns:
        CommonIssue if found, None otherwise

    Examples:
        >>> issue = lookup_issue("STAT_01")
        >>> issue.name
        "P-value misuse"
    """
    return ISSUE_CATALOG.get(code.upper())


def search_issues(keyword: str) -> List[CommonIssue]:
    """
    Search issues by keyword in name, description, or detection hints.

    Args:
        keyword: Search term (case-insensitive)

    Returns:
        List of matching CommonIssue objects

    Examples:
        >>> results = search_issues("p-value")
        >>> len(results) > 0
        True
    """
    keyword = keyword.lower()
    matches = []

    for issue in ISSUE_CATALOG.values():
        searchable = (
            issue.name.lower()
            + " "
            + issue.description.lower()
            + " "
            + " ".join(h.lower() for h in issue.detection_hints)
        )
        if keyword in searchable:
            matches.append(issue)

    return matches


def get_issues_by_category(category: IssueCategory) -> List[CommonIssue]:
    """
    Get all issues in a specific category.

    Args:
        category: IssueCategory enum value

    Returns:
        List of CommonIssue objects in that category

    Examples:
        >>> stats = get_issues_by_category(IssueCategory.STATISTICAL)
        >>> len(stats) == 6
        True
    """
    return [issue for issue in ISSUE_CATALOG.values() if issue.category == category]


def get_issues_by_severity(severity: Severity) -> List[CommonIssue]:
    """
    Get all issues with a specific default severity.

    Args:
        severity: Severity enum value

    Returns:
        List of CommonIssue objects with that severity
    """
    return [
        issue for issue in ISSUE_CATALOG.values() if issue.default_severity == severity
    ]


def get_critical_issues() -> List[CommonIssue]:
    """Get all critical severity issues."""
    return get_issues_by_severity(Severity.CRITICAL)


def get_all_codes() -> List[str]:
    """Get list of all issue codes."""
    return list(ISSUE_CATALOG.keys())


def format_issue_report(issue: CommonIssue, context: Optional[Dict[str, str]] = None) -> str:
    """
    Format an issue as a review comment.

    Args:
        issue: CommonIssue to format
        context: Optional dict with template placeholder values

    Returns:
        Formatted issue report string
    """
    context = context or {}

    lines = [
        f"**[{issue.code}] {issue.name}** ({issue.default_severity.value.upper()})",
        "",
        issue.description,
        "",
        "**Detection indicators:**",
    ]

    for hint in issue.detection_hints:
        lines.append(f"- {hint}")

    lines.append("")
    lines.append("**Recommendation:**")

    # Apply context substitutions to template
    recommendation = issue.recommendation_template
    for key, value in context.items():
        recommendation = recommendation.replace(f"{{{key}}}", value)

    lines.append(recommendation)

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo usage
    print("Issue Lookup Demo")
    print("=" * 40)

    # Look up a specific issue
    issue = lookup_issue("STAT_03")
    if issue:
        print(f"\nLookup STAT_03: {issue.name}")
        print(f"Severity: {issue.default_severity.value}")
        print(f"Category: {issue.category.value}")

    # Search for issues
    results = search_issues("replication")
    print(f"\nSearch 'replication': {len(results)} results")
    for r in results:
        print(f"  - {r.code}: {r.name}")

    # Get by category
    stats = get_issues_by_category(IssueCategory.STATISTICAL)
    print(f"\nStatistical issues: {len(stats)}")

    # Get critical issues
    critical = get_critical_issues()
    print(f"\nCritical issues: {len(critical)}")
    for c in critical:
        print(f"  - {c.code}: {c.name}")
