#!/usr/bin/env python3
"""
Severity Classifier for Peer Review Issues

Provides deterministic severity classification based on quantified criteria
extracted from SKILL.md. Ensures consistent issue categorization across
review sessions.

Usage:
    from validators.severity_classifier import classify_severity, Severity

    severity, rationale = classify_severity("missing_data", 0.35)
    # Returns: (Severity.CRITICAL, "Missing data >30% without sensitivity analysis")

Author: Claude Scientific Writer Plugin
License: MIT
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


class Severity(Enum):
    """Issue severity levels for peer review."""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    OPTIONAL = "optional"


@dataclass(frozen=True)
class SeverityRule:
    """Rule for deterministic severity classification.

    Attributes:
        issue_type: Type of issue (e.g., "missing_data", "sample_size")
        condition: Description of the triggering condition
        threshold: Quantified threshold value that triggers this severity
        severity: Severity level to assign
        rationale: Human-readable explanation for the classification
    """

    issue_type: str
    condition: str
    threshold: float
    severity: Severity
    rationale: str


# Rules extracted from SKILL.md lines 447-452
# Ordered by severity (critical first) then by issue_type
SEVERITY_RULES: List[SeverityRule] = [
    # =========================================================================
    # CRITICAL triggers (any one = reject)
    # These are fundamental issues that invalidate conclusions
    # =========================================================================
    SeverityRule(
        issue_type="data_verification",
        condition="cannot_verify",
        threshold=1.0,
        severity=Severity.CRITICAL,
        rationale="Data cannot be verified",
    ),
    SeverityRule(
        issue_type="statistical_test",
        condition="invalidates_results",
        threshold=1.0,
        severity=Severity.CRITICAL,
        rationale="Wrong statistical test invalidating results",
    ),
    SeverityRule(
        issue_type="missing_data",
        condition="missing_pct_no_sensitivity",
        threshold=0.30,
        severity=Severity.CRITICAL,
        rationale="Missing data >30% without sensitivity analysis",
    ),
    SeverityRule(
        issue_type="conclusions",
        condition="contradicted_by_data",
        threshold=1.0,
        severity=Severity.CRITICAL,
        rationale="Conclusions contradicted by data",
    ),
    SeverityRule(
        issue_type="ethics",
        condition="missing_approval",
        threshold=1.0,
        severity=Severity.CRITICAL,
        rationale="Missing ethics approval",
    ),
    SeverityRule(
        issue_type="pseudoreplication",
        condition="technical_as_biological",
        threshold=1.0,
        severity=Severity.CRITICAL,
        rationale="Technical replicates treated as biological replicates",
    ),
    SeverityRule(
        issue_type="sample_size",
        condition="below_valid_threshold",
        threshold=3.0,  # n < 3 per group
        severity=Severity.CRITICAL,
        rationale="Sample size below minimum for valid statistics (n<3)",
    ),
    # =========================================================================
    # MAJOR triggers (significantly affects interpretation)
    # These require major revision before reconsideration
    # =========================================================================
    SeverityRule(
        issue_type="controls",
        condition="key_control_missing_pct",
        threshold=0.50,
        severity=Severity.MAJOR,
        rationale="Key control missing from >=50% of experiments",
    ),
    SeverityRule(
        issue_type="sample_size",
        condition="below_power_pct",
        threshold=0.80,
        severity=Severity.MAJOR,
        rationale="Sample size <80% of power requirement",
    ),
    SeverityRule(
        issue_type="methods",
        condition="insufficient_for_replication",
        threshold=1.0,
        severity=Severity.MAJOR,
        rationale="Methods insufficient for replication",
    ),
    SeverityRule(
        issue_type="statistical_assumptions",
        condition="violated",
        threshold=1.0,
        severity=Severity.MAJOR,
        rationale="Statistical assumptions violated",
    ),
    SeverityRule(
        issue_type="outcomes",
        condition="missing_stated_pct",
        threshold=0.20,
        severity=Severity.MAJOR,
        rationale=">=20% of stated outcomes missing",
    ),
    SeverityRule(
        issue_type="power_analysis",
        condition="missing",
        threshold=1.0,
        severity=Severity.MAJOR,
        rationale="No power calculation provided",
    ),
    SeverityRule(
        issue_type="blinding",
        condition="missing_required",
        threshold=1.0,
        severity=Severity.MAJOR,
        rationale="Blinding missing when required for study design",
    ),
    SeverityRule(
        issue_type="randomization",
        condition="missing_required",
        threshold=1.0,
        severity=Severity.MAJOR,
        rationale="Randomization missing when required for study design",
    ),
    SeverityRule(
        issue_type="multiple_testing",
        condition="no_correction",
        threshold=5.0,  # >5 tests without correction
        severity=Severity.MAJOR,
        rationale="Multiple testing (>5 tests) without correction",
    ),
    SeverityRule(
        issue_type="effect_sizes",
        condition="missing",
        threshold=1.0,
        severity=Severity.MAJOR,
        rationale="Effect sizes not reported",
    ),
    # =========================================================================
    # MINOR triggers (affects clarity/completeness)
    # These should be addressed before publication
    # =========================================================================
    SeverityRule(
        issue_type="grammar",
        condition="errors_per_page",
        threshold=5.0,
        severity=Severity.MINOR,
        rationale="Grammar/spelling errors >5/page",
    ),
    SeverityRule(
        issue_type="figure_quality",
        condition="below_minimum_standards",
        threshold=1.0,
        severity=Severity.MINOR,
        rationale="Figure quality below minimum standards",
    ),
    SeverityRule(
        issue_type="references",
        condition="formatting_inconsistent",
        threshold=1.0,
        severity=Severity.MINOR,
        rationale="Reference formatting inconsistent",
    ),
    SeverityRule(
        issue_type="acronyms",
        condition="undefined_count",
        threshold=3.0,
        severity=Severity.MINOR,
        rationale="Acronyms undefined (>3)",
    ),
    SeverityRule(
        issue_type="error_bars",
        condition="undefined",
        threshold=1.0,
        severity=Severity.MINOR,
        rationale="Error bars not defined (SD, SEM, CI)",
    ),
    SeverityRule(
        issue_type="scale_bars",
        condition="missing",
        threshold=1.0,
        severity=Severity.MINOR,
        rationale="Scale bars missing from images",
    ),
    SeverityRule(
        issue_type="units",
        condition="missing_or_inconsistent",
        threshold=1.0,
        severity=Severity.MINOR,
        rationale="Units missing or inconsistent in figures/tables",
    ),
    SeverityRule(
        issue_type="methods_detail",
        condition="minor_gap",
        threshold=1.0,
        severity=Severity.MINOR,
        rationale="Minor methods gaps (vendor info, lot numbers)",
    ),
]


def classify_severity(
    issue_type: str,
    metric_value: float,
    condition: Optional[str] = None,
) -> Tuple[Severity, str]:
    """
    Deterministic severity classification based on quantified criteria.

    Searches through SEVERITY_RULES to find matching issue type and threshold.
    Returns the highest severity level that matches the criteria.

    Args:
        issue_type: Type of issue (e.g., "missing_data", "sample_size")
        metric_value: Quantified measure of the issue
        condition: Optional condition specifier to narrow matching rules

    Returns:
        Tuple of (Severity, rationale)

    Examples:
        >>> classify_severity("missing_data", 0.35)
        (Severity.CRITICAL, "Missing data >30% without sensitivity analysis")

        >>> classify_severity("grammar", 3.0)
        (Severity.OPTIONAL, "Does not meet severity threshold criteria")

        >>> classify_severity("sample_size", 2.0, "below_valid_threshold")
        (Severity.CRITICAL, "Sample size below minimum for valid statistics (n<3)")
    """
    matching_rules = []

    for rule in SEVERITY_RULES:
        if rule.issue_type != issue_type:
            continue

        if condition is not None and rule.condition != condition:
            continue

        # Check threshold based on condition type
        # For "below_*" conditions, value should be below threshold
        # For "missing_*" and percentage conditions, value should be >= threshold
        if "below" in rule.condition:
            if metric_value < rule.threshold:
                matching_rules.append(rule)
        else:
            if metric_value >= rule.threshold:
                matching_rules.append(rule)

    if not matching_rules:
        return (Severity.OPTIONAL, "Does not meet severity threshold criteria")

    # Return highest severity (CRITICAL > MAJOR > MINOR > OPTIONAL)
    severity_order = {
        Severity.CRITICAL: 0,
        Severity.MAJOR: 1,
        Severity.MINOR: 2,
        Severity.OPTIONAL: 3,
    }

    matching_rules.sort(key=lambda r: severity_order[r.severity])
    best_match = matching_rules[0]

    return (best_match.severity, best_match.rationale)


def get_recommendation_action(severity: Severity) -> str:
    """Map severity to standard recommendation action.

    Args:
        severity: Severity level

    Returns:
        Recommended action string

    Examples:
        >>> get_recommendation_action(Severity.CRITICAL)
        "Reject - fundamental issue invalidating conclusions"
    """
    actions: Dict[Severity, str] = {
        Severity.CRITICAL: "Reject - fundamental issue invalidating conclusions",
        Severity.MAJOR: "Major revision required before reconsideration",
        Severity.MINOR: "Minor revision - address before publication",
        Severity.OPTIONAL: "Author discretion - suggestion for improvement",
    }
    return actions[severity]


def classify_multiple_issues(
    issues: List[Dict[str, float]],
) -> List[Tuple[str, Severity, str]]:
    """
    Classify multiple issues and return sorted by severity.

    Args:
        issues: List of dicts with 'issue_type' and 'metric_value' keys

    Returns:
        List of (issue_type, Severity, rationale) tuples, sorted by severity

    Example:
        >>> issues = [
        ...     {"issue_type": "missing_data", "metric_value": 0.35},
        ...     {"issue_type": "grammar", "metric_value": 7.0},
        ... ]
        >>> classify_multiple_issues(issues)
        [
            ("missing_data", Severity.CRITICAL, "Missing data >30%..."),
            ("grammar", Severity.MINOR, "Grammar/spelling errors >5/page"),
        ]
    """
    results = []

    for issue in issues:
        issue_type = issue.get("issue_type", "")
        metric_value = issue.get("metric_value", 0.0)
        condition = issue.get("condition")

        severity, rationale = classify_severity(issue_type, metric_value, condition)
        results.append((issue_type, severity, rationale))

    # Sort by severity (CRITICAL first)
    severity_order = {
        Severity.CRITICAL: 0,
        Severity.MAJOR: 1,
        Severity.MINOR: 2,
        Severity.OPTIONAL: 3,
    }
    results.sort(key=lambda x: severity_order[x[1]])

    return results


def get_rules_by_severity(severity: Severity) -> List[SeverityRule]:
    """Get all rules for a specific severity level.

    Args:
        severity: Severity level to filter by

    Returns:
        List of SeverityRule objects matching the severity
    """
    return [rule for rule in SEVERITY_RULES if rule.severity == severity]


def get_rules_by_issue_type(issue_type: str) -> List[SeverityRule]:
    """Get all rules for a specific issue type.

    Args:
        issue_type: Issue type to filter by

    Returns:
        List of SeverityRule objects matching the issue type
    """
    return [rule for rule in SEVERITY_RULES if rule.issue_type == issue_type]
