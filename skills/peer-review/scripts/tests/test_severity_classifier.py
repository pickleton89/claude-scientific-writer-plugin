"""Tests for severity classifier module."""

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validators.severity_classifier import (
    Severity,
    SEVERITY_RULES,
    classify_severity,
    get_recommendation_action,
    classify_multiple_issues,
    get_rules_by_severity,
    get_rules_by_issue_type,
)


class TestSeverityEnum:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test that all expected severity levels exist."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.MAJOR.value == "major"
        assert Severity.MINOR.value == "minor"
        assert Severity.OPTIONAL.value == "optional"

    def test_severity_count(self):
        """Test that we have exactly 4 severity levels."""
        assert len(Severity) == 4


class TestSeverityRules:
    """Tests for severity rules configuration."""

    def test_rules_not_empty(self):
        """Test that rules list is populated."""
        assert len(SEVERITY_RULES) > 0

    def test_rules_have_required_fields(self):
        """Test that all rules have required fields."""
        for rule in SEVERITY_RULES:
            assert rule.issue_type
            assert rule.condition
            assert rule.threshold is not None
            assert isinstance(rule.severity, Severity)
            assert rule.rationale

    def test_critical_rules_exist(self):
        """Test that we have critical rules."""
        critical_rules = [r for r in SEVERITY_RULES if r.severity == Severity.CRITICAL]
        assert len(critical_rules) >= 5

    def test_major_rules_exist(self):
        """Test that we have major rules."""
        major_rules = [r for r in SEVERITY_RULES if r.severity == Severity.MAJOR]
        assert len(major_rules) >= 5

    def test_minor_rules_exist(self):
        """Test that we have minor rules."""
        minor_rules = [r for r in SEVERITY_RULES if r.severity == Severity.MINOR]
        assert len(minor_rules) >= 3


class TestClassifySeverity:
    """Tests for classify_severity function."""

    def test_missing_data_critical(self):
        """Test missing data >30% triggers critical."""
        severity, rationale = classify_severity("missing_data", 0.35)
        assert severity == Severity.CRITICAL
        assert "30%" in rationale

    def test_missing_data_not_critical(self):
        """Test missing data <30% does not trigger critical."""
        severity, rationale = classify_severity("missing_data", 0.25)
        assert severity == Severity.OPTIONAL

    def test_ethics_missing_approval(self):
        """Test missing ethics approval is critical."""
        severity, rationale = classify_severity("ethics", 1.0)
        assert severity == Severity.CRITICAL
        assert "ethics" in rationale.lower()

    def test_sample_size_below_valid(self):
        """Test sample size below valid threshold is critical."""
        severity, rationale = classify_severity(
            "sample_size", 2.0, condition="below_valid_threshold"
        )
        assert severity == Severity.CRITICAL

    def test_sample_size_below_power(self):
        """Test sample size below power requirement is major."""
        severity, rationale = classify_severity(
            "sample_size", 0.70, condition="below_power_pct"
        )
        assert severity == Severity.MAJOR

    def test_grammar_errors_minor(self):
        """Test grammar errors >5/page is minor."""
        severity, rationale = classify_severity("grammar", 7.0)
        assert severity == Severity.MINOR

    def test_grammar_errors_not_minor(self):
        """Test grammar errors <5/page is optional."""
        severity, rationale = classify_severity("grammar", 3.0)
        assert severity == Severity.OPTIONAL

    def test_unknown_issue_type(self):
        """Test unknown issue type returns optional."""
        severity, rationale = classify_severity("unknown_type", 100.0)
        assert severity == Severity.OPTIONAL

    def test_pseudoreplication_critical(self):
        """Test pseudoreplication is critical."""
        severity, rationale = classify_severity("pseudoreplication", 1.0)
        assert severity == Severity.CRITICAL

    def test_controls_missing_major(self):
        """Test controls missing >=50% is major."""
        severity, rationale = classify_severity("controls", 0.60)
        assert severity == Severity.MAJOR


class TestGetRecommendationAction:
    """Tests for recommendation action mapping."""

    def test_critical_action(self):
        """Test critical severity maps to reject."""
        action = get_recommendation_action(Severity.CRITICAL)
        assert "reject" in action.lower()

    def test_major_action(self):
        """Test major severity maps to major revision."""
        action = get_recommendation_action(Severity.MAJOR)
        assert "major revision" in action.lower()

    def test_minor_action(self):
        """Test minor severity maps to minor revision."""
        action = get_recommendation_action(Severity.MINOR)
        assert "minor revision" in action.lower()

    def test_optional_action(self):
        """Test optional severity maps to author discretion."""
        action = get_recommendation_action(Severity.OPTIONAL)
        assert "discretion" in action.lower()


class TestClassifyMultipleIssues:
    """Tests for classify_multiple_issues function."""

    def test_empty_list(self):
        """Test empty list returns empty results."""
        results = classify_multiple_issues([])
        assert results == []

    def test_single_issue(self):
        """Test classification of single issue."""
        issues = [{"issue_type": "missing_data", "metric_value": 0.35}]
        results = classify_multiple_issues(issues)
        assert len(results) == 1
        assert results[0][1] == Severity.CRITICAL

    def test_multiple_issues_sorted(self):
        """Test multiple issues are sorted by severity."""
        issues = [
            {"issue_type": "grammar", "metric_value": 7.0},  # MINOR
            {"issue_type": "missing_data", "metric_value": 0.35},  # CRITICAL
            {"issue_type": "controls", "metric_value": 0.60},  # MAJOR
        ]
        results = classify_multiple_issues(issues)
        assert len(results) == 3
        # Critical should be first
        assert results[0][1] == Severity.CRITICAL
        # Major should be second
        assert results[1][1] == Severity.MAJOR
        # Minor should be third
        assert results[2][1] == Severity.MINOR


class TestGetRulesBy:
    """Tests for rule filtering functions."""

    def test_get_rules_by_severity_critical(self):
        """Test getting critical rules."""
        rules = get_rules_by_severity(Severity.CRITICAL)
        assert all(r.severity == Severity.CRITICAL for r in rules)

    def test_get_rules_by_severity_minor(self):
        """Test getting minor rules."""
        rules = get_rules_by_severity(Severity.MINOR)
        assert all(r.severity == Severity.MINOR for r in rules)

    def test_get_rules_by_issue_type(self):
        """Test getting rules by issue type."""
        rules = get_rules_by_issue_type("sample_size")
        assert all(r.issue_type == "sample_size" for r in rules)
        assert len(rules) >= 2  # At least critical and major rules


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_same_input_same_output(self):
        """Test that same inputs always produce same outputs."""
        for _ in range(10):
            severity1, rationale1 = classify_severity("missing_data", 0.35)
            severity2, rationale2 = classify_severity("missing_data", 0.35)
            assert severity1 == severity2
            assert rationale1 == rationale2

    def test_threshold_boundaries(self):
        """Test behavior at exact threshold boundaries."""
        # At exactly 30% threshold for missing data
        severity_at, _ = classify_severity("missing_data", 0.30)
        severity_below, _ = classify_severity("missing_data", 0.29)

        assert severity_at == Severity.CRITICAL
        assert severity_below == Severity.OPTIONAL
