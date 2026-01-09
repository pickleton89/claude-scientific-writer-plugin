"""Tests for issue lookup module."""

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validators.issue_lookup import (
    IssueCategory,
    Severity,
    ISSUE_CATALOG,
    lookup_issue,
    search_issues,
    get_issues_by_category,
    get_issues_by_severity,
    get_critical_issues,
    get_all_codes,
    format_issue_report,
)


class TestIssueCategory:
    """Tests for IssueCategory enum."""

    def test_category_values(self):
        """Test that all expected categories exist."""
        assert IssueCategory.STATISTICAL.value == "statistical"
        assert IssueCategory.EXPERIMENTAL.value == "experimental"
        assert IssueCategory.REPRODUCIBILITY.value == "reproducibility"
        assert IssueCategory.INTERPRETATION.value == "interpretation"
        assert IssueCategory.PRESENTATION.value == "presentation"


class TestIssueCatalog:
    """Tests for issue catalog structure."""

    def test_catalog_not_empty(self):
        """Test that catalog is populated."""
        assert len(ISSUE_CATALOG) > 0

    def test_all_issues_have_required_fields(self):
        """Test that all issues have required fields."""
        for code, issue in ISSUE_CATALOG.items():
            assert issue.code == code
            assert issue.name
            assert issue.description
            assert len(issue.detection_hints) > 0
            assert isinstance(issue.category, IssueCategory)
            assert isinstance(issue.default_severity, Severity)
            assert issue.recommendation_template

    def test_statistical_issues_exist(self):
        """Test that statistical issues are cataloged."""
        stat_issues = [i for i in ISSUE_CATALOG.values() if i.category == IssueCategory.STATISTICAL]
        assert len(stat_issues) >= 6

    def test_issue_codes_follow_pattern(self):
        """Test that issue codes follow expected pattern."""
        for code in ISSUE_CATALOG.keys():
            # Should be CATEGORY_NN format
            parts = code.split("_")
            assert len(parts) == 2
            assert parts[1].isdigit()


class TestLookupIssue:
    """Tests for lookup_issue function."""

    def test_lookup_existing_issue(self):
        """Test looking up an existing issue."""
        issue = lookup_issue("STAT_01")
        assert issue is not None
        assert issue.name == "P-value misuse"

    def test_lookup_case_insensitive(self):
        """Test that lookup is case-insensitive."""
        issue1 = lookup_issue("STAT_01")
        issue2 = lookup_issue("stat_01")
        assert issue1 == issue2

    def test_lookup_nonexistent_issue(self):
        """Test looking up a nonexistent issue."""
        issue = lookup_issue("NONEXISTENT_99")
        assert issue is None

    def test_lookup_pseudoreplication(self):
        """Test looking up pseudoreplication issue."""
        issue = lookup_issue("STAT_03")
        assert issue is not None
        assert issue.default_severity == Severity.CRITICAL


class TestSearchIssues:
    """Tests for search_issues function."""

    def test_search_p_value(self):
        """Test searching for p-value issues."""
        results = search_issues("p-value")
        assert len(results) >= 1
        assert any("P-value" in r.name or "p-value" in r.description for r in results)

    def test_search_replication(self):
        """Test searching for replication issues."""
        results = search_issues("replication")
        assert len(results) >= 1

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        results1 = search_issues("statistical")
        results2 = search_issues("STATISTICAL")
        assert len(results1) == len(results2)

    def test_search_no_results(self):
        """Test search with no matches."""
        results = search_issues("zzzznonexistenttermzzzz")
        assert len(results) == 0

    def test_search_in_detection_hints(self):
        """Test that search includes detection hints."""
        # Search for term that appears in detection hints
        results = search_issues("assumption")
        assert len(results) >= 1


class TestGetIssuesByCategory:
    """Tests for get_issues_by_category function."""

    def test_get_statistical_issues(self):
        """Test getting statistical issues."""
        issues = get_issues_by_category(IssueCategory.STATISTICAL)
        assert len(issues) >= 6
        assert all(i.category == IssueCategory.STATISTICAL for i in issues)

    def test_get_experimental_issues(self):
        """Test getting experimental issues."""
        issues = get_issues_by_category(IssueCategory.EXPERIMENTAL)
        assert len(issues) >= 3
        assert all(i.category == IssueCategory.EXPERIMENTAL for i in issues)

    def test_get_presentation_issues(self):
        """Test getting presentation issues."""
        issues = get_issues_by_category(IssueCategory.PRESENTATION)
        assert len(issues) >= 1


class TestGetIssuesBySeverity:
    """Tests for get_issues_by_severity function."""

    def test_get_critical_issues(self):
        """Test getting critical issues."""
        issues = get_issues_by_severity(Severity.CRITICAL)
        assert len(issues) >= 2
        assert all(i.default_severity == Severity.CRITICAL for i in issues)

    def test_get_major_issues(self):
        """Test getting major issues."""
        issues = get_issues_by_severity(Severity.MAJOR)
        assert len(issues) >= 5
        assert all(i.default_severity == Severity.MAJOR for i in issues)

    def test_critical_helper(self):
        """Test get_critical_issues helper."""
        issues1 = get_critical_issues()
        issues2 = get_issues_by_severity(Severity.CRITICAL)
        assert issues1 == issues2


class TestGetAllCodes:
    """Tests for get_all_codes function."""

    def test_get_all_codes(self):
        """Test getting all issue codes."""
        codes = get_all_codes()
        assert len(codes) == len(ISSUE_CATALOG)
        assert "STAT_01" in codes
        assert "EXP_01" in codes


class TestFormatIssueReport:
    """Tests for format_issue_report function."""

    def test_format_basic_report(self):
        """Test basic report formatting."""
        issue = lookup_issue("STAT_01")
        report = format_issue_report(issue)

        assert "STAT_01" in report
        assert "P-value misuse" in report
        assert "MAJOR" in report
        assert "Detection indicators" in report
        assert "Recommendation" in report

    def test_format_with_context(self):
        """Test report formatting with context substitutions."""
        issue = lookup_issue("STAT_01")
        context = {"correction_type": "Bonferroni"}
        report = format_issue_report(issue, context)

        assert "Bonferroni" in report

    def test_format_critical_issue(self):
        """Test formatting a critical issue."""
        issue = lookup_issue("STAT_03")  # Pseudoreplication
        report = format_issue_report(issue)

        assert "CRITICAL" in report
        assert "biological replicates" in report.lower()


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_lookup_is_deterministic(self):
        """Test that lookups are deterministic."""
        for _ in range(10):
            issue1 = lookup_issue("STAT_01")
            issue2 = lookup_issue("STAT_01")
            assert issue1 == issue2

    def test_search_is_deterministic(self):
        """Test that searches are deterministic."""
        for _ in range(10):
            results1 = search_issues("replication")
            results2 = search_issues("replication")
            assert len(results1) == len(results2)
            assert all(r1.code == r2.code for r1, r2 in zip(results1, results2))

    def test_category_filter_is_deterministic(self):
        """Test that category filtering is deterministic."""
        for _ in range(10):
            issues1 = get_issues_by_category(IssueCategory.STATISTICAL)
            issues2 = get_issues_by_category(IssueCategory.STATISTICAL)
            assert len(issues1) == len(issues2)


class TestIssueCompleteness:
    """Tests to verify catalog completeness."""

    def test_covers_all_categories(self):
        """Test that catalog covers all categories."""
        covered_categories = set(i.category for i in ISSUE_CATALOG.values())
        expected = {
            IssueCategory.STATISTICAL,
            IssueCategory.EXPERIMENTAL,
            IssueCategory.REPRODUCIBILITY,
            IssueCategory.INTERPRETATION,
            IssueCategory.PRESENTATION,
            IssueCategory.STUDY_DESIGN,
            IssueCategory.REPORTING,
        }
        assert covered_categories == expected

    def test_covers_all_severities(self):
        """Test that catalog includes all severity levels."""
        covered_severities = set(i.default_severity for i in ISSUE_CATALOG.values())
        assert Severity.CRITICAL in covered_severities
        assert Severity.MAJOR in covered_severities
        assert Severity.MINOR in covered_severities
