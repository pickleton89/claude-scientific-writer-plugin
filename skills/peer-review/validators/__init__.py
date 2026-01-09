"""
Peer Review Validators Package

Deterministic validation utilities for peer review workflows.
Provides severity classification, issue lookup, and statistical test recommendations.
"""

try:
    from .severity_classifier import (
        Severity,
        SeverityRule,
        SEVERITY_RULES,
        classify_severity,
        get_recommendation_action,
        classify_multiple_issues,
    )
except ImportError:
    pass

try:
    from .issue_lookup import (
        CommonIssue,
        ISSUE_CATALOG,
        lookup_issue,
        search_issues,
        get_issues_by_category,
    )
except ImportError:
    pass

try:
    from .statistical_tests import (
        TestRecommendation,
        TEST_SELECTION,
        recommend_test,
        get_all_tests_for_design,
    )
except ImportError:
    pass

__all__ = [
    # Severity classifier
    "Severity",
    "SeverityRule",
    "SEVERITY_RULES",
    "classify_severity",
    "get_recommendation_action",
    "classify_multiple_issues",
    # Issue lookup
    "CommonIssue",
    "ISSUE_CATALOG",
    "lookup_issue",
    "search_issues",
    "get_issues_by_category",
    # Statistical tests
    "TestRecommendation",
    "TEST_SELECTION",
    "recommend_test",
    "get_all_tests_for_design",
]
