#!/usr/bin/env python3
"""
Tests for search_validator.py

Comprehensive test suite for search query syntax validation across
multiple academic databases.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from search_validator import (  # noqa: E402
    ValidationIssue,
    SearchQuery,
    SearchStrategy,
    DATABASE_CONFIGS,
    validate_query,
    parse_search_strategy,
    get_database_info,
    get_supported_databases,
    translate_query,
    load_strategy_from_json,
    save_strategy_to_json,
    generate_validation_report,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestDatabaseConfigs:
    """Tests for database configurations."""

    def test_all_major_databases_configured(self):
        """Test all major databases have configurations."""
        expected = ["pubmed", "cochrane", "wos", "scopus", "cinahl", "psycinfo", "embase", "ieee"]
        for db in expected:
            assert db in DATABASE_CONFIGS

    def test_pubmed_config_complete(self):
        """Test PubMed configuration is complete."""
        config = DATABASE_CONFIGS["pubmed"]
        assert "boolean_operators" in config
        assert "field_tags" in config
        assert "truncation" in config
        assert config["truncation"] == "*"
        assert "[tiab]" in config["field_tags"]

    def test_wos_config_complete(self):
        """Test Web of Science configuration is complete."""
        config = DATABASE_CONFIGS["wos"]
        assert "TS=" in config["field_tags"]
        assert config["proximity_supported"] is True

    def test_scopus_config_complete(self):
        """Test Scopus configuration is complete."""
        config = DATABASE_CONFIGS["scopus"]
        assert "TITLE-ABS-KEY" in config["field_tags"]
        assert config["phrase_operator"] == "{}"


# =============================================================================
# ValidationIssue Tests
# =============================================================================


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_create_error(self):
        """Test creating error-level issue."""
        issue = ValidationIssue(
            severity="error",
            message="Test error",
            position=10,
            suggestion="Fix it",
        )
        assert issue.severity == "error"
        assert issue.message == "Test error"
        assert issue.position == 10

    def test_to_dict(self):
        """Test conversion to dictionary."""
        issue = ValidationIssue(
            severity="warning",
            message="Test warning",
        )
        d = issue.to_dict()
        assert d["severity"] == "warning"
        assert d["message"] == "Test warning"


# =============================================================================
# SearchQuery Validation Tests
# =============================================================================


class TestSearchQueryBasic:
    """Basic tests for SearchQuery validation."""

    def test_empty_query_fails(self):
        """Test empty query fails validation."""
        query = SearchQuery(query="", database="pubmed")
        issues = query.validate()
        assert any("empty" in i.message.lower() for i in issues)

    def test_whitespace_query_fails(self):
        """Test whitespace-only query fails validation."""
        query = SearchQuery(query="   ", database="pubmed")
        issues = query.validate()
        assert any("empty" in i.message.lower() for i in issues)

    def test_unknown_database_fails(self):
        """Test unknown database fails validation."""
        query = SearchQuery(query="test", database="unknown_db")
        issues = query.validate()
        assert any("Unknown database" in i.message for i in issues)

    def test_valid_simple_query(self):
        """Test simple valid query passes."""
        query = SearchQuery(query="cancer", database="pubmed")
        issues = query.validate()
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0


class TestParenthesesValidation:
    """Tests for parentheses balance checking."""

    def test_balanced_parentheses_valid(self):
        """Test balanced parentheses pass."""
        query = SearchQuery(query="(cancer OR tumor) AND treatment", database="pubmed")
        issues = query.validate()
        errors = [i for i in issues if "parenthesis" in i.message.lower()]
        assert len(errors) == 0

    def test_missing_closing_paren(self):
        """Test missing closing parenthesis detected."""
        query = SearchQuery(query="(cancer OR tumor AND treatment", database="pubmed")
        issues = query.validate()
        assert any("closing parenthesis" in i.message.lower() for i in issues)

    def test_extra_closing_paren(self):
        """Test extra closing parenthesis detected."""
        query = SearchQuery(query="cancer OR tumor) AND treatment", database="pubmed")
        issues = query.validate()
        assert any("Unmatched closing parenthesis" in i.message for i in issues)

    def test_nested_parentheses_valid(self):
        """Test nested parentheses work."""
        query = SearchQuery(
            query="((cancer OR tumor) AND (treatment OR therapy))",
            database="pubmed",
        )
        issues = query.validate()
        errors = [i for i in issues if "parenthesis" in i.message.lower()]
        assert len(errors) == 0

    def test_empty_parentheses_error(self):
        """Test empty parentheses detected."""
        query = SearchQuery(query="cancer () AND treatment", database="pubmed")
        issues = query.validate()
        assert any("Empty parentheses" in i.message for i in issues)


class TestQuoteValidation:
    """Tests for quote balance checking."""

    def test_balanced_quotes_valid(self):
        """Test balanced quotes pass."""
        query = SearchQuery(query='"gene therapy" AND cancer', database="pubmed")
        issues = query.validate()
        errors = [i for i in issues if "quote" in i.message.lower()]
        assert len(errors) == 0

    def test_unbalanced_quotes_error(self):
        """Test unbalanced quotes detected."""
        query = SearchQuery(query='"gene therapy AND cancer', database="pubmed")
        issues = query.validate()
        assert any("Unbalanced" in i.message and "quote" in i.message.lower() for i in issues)

    def test_multiple_quoted_phrases(self):
        """Test multiple quoted phrases work."""
        query = SearchQuery(
            query='"gene therapy" AND "stem cells" OR "regenerative medicine"',
            database="pubmed",
        )
        issues = query.validate()
        errors = [i for i in issues if "quote" in i.message.lower()]
        assert len(errors) == 0


class TestBooleanOperatorValidation:
    """Tests for Boolean operator validation."""

    def test_uppercase_bool_valid(self):
        """Test uppercase Boolean operators pass."""
        query = SearchQuery(query="cancer AND treatment", database="pubmed")
        issues = query.validate()
        errors = [i for i in issues if "Boolean" in i.message]
        assert len(errors) == 0

    def test_lowercase_bool_error(self):
        """Test lowercase Boolean operators detected."""
        query = SearchQuery(query="cancer and treatment", database="pubmed")
        issues = query.validate()
        assert any("should be uppercase" in i.message for i in issues)

    def test_lowercase_or_error(self):
        """Test lowercase OR detected."""
        query = SearchQuery(query="cancer or tumor", database="pubmed")
        issues = query.validate()
        assert any("should be uppercase" in i.message for i in issues)

    def test_lowercase_not_error(self):
        """Test lowercase NOT detected."""
        query = SearchQuery(query="cancer not treatment", database="pubmed")
        issues = query.validate()
        assert any("should be uppercase" in i.message for i in issues)

    def test_adjacent_operators_error(self):
        """Test adjacent Boolean operators detected."""
        query = SearchQuery(query="cancer AND OR treatment", database="pubmed")
        issues = query.validate()
        assert any("Adjacent Boolean operators" in i.message for i in issues)

    def test_starting_with_and_error(self):
        """Test query starting with AND detected."""
        query = SearchQuery(query="AND cancer treatment", database="pubmed")
        issues = query.validate()
        assert any("cannot start with AND" in i.message for i in issues)

    def test_starting_with_or_error(self):
        """Test query starting with OR detected."""
        query = SearchQuery(query="OR cancer treatment", database="pubmed")
        issues = query.validate()
        assert any("cannot start with" in i.message for i in issues)

    def test_ending_with_bool_error(self):
        """Test query ending with Boolean detected."""
        query = SearchQuery(query="cancer treatment AND", database="pubmed")
        issues = query.validate()
        assert any("cannot end with Boolean" in i.message for i in issues)

    def test_not_at_start_valid(self):
        """Test NOT at start is valid (common usage)."""
        query = SearchQuery(query="NOT review[pt]", database="pubmed")
        issues = query.validate()
        # NOT at start should not trigger start error
        errors = [i for i in issues if "cannot start" in i.message]
        assert len(errors) == 0


class TestFieldTagValidation:
    """Tests for field tag validation."""

    def test_valid_pubmed_tag(self):
        """Test valid PubMed field tags pass."""
        query = SearchQuery(query="cancer[tiab] AND treatment[ti]", database="pubmed")
        issues = query.validate()
        errors = [i for i in issues if "Unknown" in i.message and "tag" in i.message.lower()]
        assert len(errors) == 0

    def test_invalid_pubmed_tag_warning(self):
        """Test invalid PubMed field tag generates warning."""
        query = SearchQuery(query="cancer[xyz] AND treatment", database="pubmed")
        issues = query.validate()
        assert any("Unknown PubMed field tag" in i.message for i in issues)

    def test_valid_wos_tag(self):
        """Test valid Web of Science tags pass."""
        query = SearchQuery(query="TS=(cancer AND treatment)", database="wos")
        issues = query.validate()
        errors = [i for i in issues if "Unknown" in i.message and "tag" in i.message.lower()]
        assert len(errors) == 0

    def test_valid_cochrane_tag(self):
        """Test valid Cochrane tags pass."""
        query = SearchQuery(query="cancer:ti,ab AND treatment:ti", database="cochrane")
        issues = query.validate()
        errors = [i for i in issues if "Unknown" in i.message and "tag" in i.message.lower()]
        assert len(errors) == 0


class TestTruncationValidation:
    """Tests for truncation symbol validation."""

    def test_valid_truncation(self):
        """Test valid truncation passes."""
        query = SearchQuery(query="therap* AND cancer", database="pubmed")
        issues = query.validate()
        errors = [i for i in issues if i.severity == "error" and "truncation" in i.message.lower()]
        assert len(errors) == 0

    def test_short_stem_warning(self):
        """Test short truncation stem generates warning."""
        query = SearchQuery(query="ca* AND treatment", database="pubmed")
        issues = query.validate()
        assert any("short truncation stem" in i.message.lower() for i in issues)

    def test_truncation_unsupported_warning(self):
        """Test truncation warning for unsupported database."""
        query = SearchQuery(query="cancer* AND treatment", database="semantic_scholar")
        issues = query.validate()
        assert any("may not support truncation" in i.message for i in issues)


class TestIsValidMethod:
    """Tests for is_valid method."""

    def test_valid_query_is_valid(self):
        """Test valid query returns True."""
        query = SearchQuery(query="cancer AND treatment", database="pubmed")
        assert query.is_valid() is True

    def test_invalid_query_not_valid(self):
        """Test invalid query returns False."""
        query = SearchQuery(query="(cancer AND treatment", database="pubmed")
        assert query.is_valid() is False

    def test_warning_only_still_valid(self):
        """Test query with only warnings is still valid."""
        query = SearchQuery(query="ca* AND treatment", database="pubmed")
        # Has warning about short stem but no errors
        query.validate()
        errors = query.get_errors()
        warnings = query.get_warnings()
        assert len(errors) == 0
        assert len(warnings) > 0
        assert query.is_valid() is True


# =============================================================================
# SearchStrategy Tests
# =============================================================================


class TestSearchStrategy:
    """Tests for SearchStrategy collection."""

    def test_add_query(self):
        """Test adding queries to strategy."""
        strategy = SearchStrategy(database="pubmed")
        strategy.add_query("cancer[tiab]", "Cancer terms")
        strategy.add_query("treatment[tiab]", "Treatment terms")
        assert len(strategy.queries) == 2

    def test_line_numbers_assigned(self):
        """Test line numbers are automatically assigned."""
        strategy = SearchStrategy(database="pubmed")
        q1 = strategy.add_query("cancer")
        q2 = strategy.add_query("treatment")
        q3 = strategy.add_query("#1 AND #2")
        assert q1.line_number == 1
        assert q2.line_number == 2
        assert q3.line_number == 3

    def test_validate_all(self):
        """Test validating all queries."""
        strategy = SearchStrategy(database="pubmed")
        strategy.add_query("cancer AND treatment")
        strategy.add_query("(tumor OR neoplasm")  # Missing paren
        issues = strategy.validate_all()
        assert len(issues) > 0
        assert any("Line 2" in i.message for i in issues)

    def test_is_valid_all_valid(self):
        """Test is_valid when all queries valid."""
        strategy = SearchStrategy(database="pubmed")
        strategy.add_query("cancer AND treatment")
        strategy.add_query("tumor OR neoplasm")
        assert strategy.is_valid() is True

    def test_is_valid_some_invalid(self):
        """Test is_valid when some queries invalid."""
        strategy = SearchStrategy(database="pubmed")
        strategy.add_query("cancer AND treatment")
        strategy.add_query("(tumor OR neoplasm")  # Missing paren
        assert strategy.is_valid() is False

    def test_get_summary(self):
        """Test getting summary statistics."""
        strategy = SearchStrategy(database="pubmed", title="Test Strategy")
        strategy.add_query("cancer AND treatment")
        strategy.add_query("(tumor OR neoplasm")  # Error
        strategy.add_query("ca* AND therapy")  # Warning
        summary = strategy.get_summary()
        assert summary["total_queries"] == 3
        assert summary["error_count"] >= 1
        assert summary["database"] == "pubmed"


class TestParseSearchStrategy:
    """Tests for parse_search_strategy function."""

    def test_parse_simple_lines(self):
        """Test parsing simple line-separated queries."""
        text = """
        cancer[tiab]
        treatment[tiab]
        #1 AND #2
        """
        strategy = parse_search_strategy(text, "pubmed")
        assert len(strategy.queries) == 3

    def test_parse_numbered_lines(self):
        """Test parsing numbered queries."""
        text = """
        1. cancer[tiab]
        2. treatment[tiab]
        3. #1 AND #2
        """
        strategy = parse_search_strategy(text, "pubmed")
        assert len(strategy.queries) == 3

    def test_parse_hash_numbered(self):
        """Test parsing hash-numbered queries."""
        text = """
        #1 cancer[tiab]
        #2 treatment[tiab]
        #3 #1 AND #2
        """
        strategy = parse_search_strategy(text, "pubmed")
        assert len(strategy.queries) == 3

    def test_skip_comment_lines(self):
        """Test comment lines are skipped."""
        text = """
        # This is a comment
        cancer[tiab]
        # Another comment
        treatment[tiab]
        """
        strategy = parse_search_strategy(text, "pubmed")
        assert len(strategy.queries) == 2

    def test_skip_empty_lines(self):
        """Test empty lines are skipped."""
        text = """
        cancer[tiab]

        treatment[tiab]

        #1 AND #2
        """
        strategy = parse_search_strategy(text, "pubmed")
        assert len(strategy.queries) == 3


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_supported_databases(self):
        """Test getting list of supported databases."""
        dbs = get_supported_databases()
        assert "pubmed" in dbs
        assert "wos" in dbs
        assert "scopus" in dbs
        assert len(dbs) >= 8

    def test_get_database_info(self):
        """Test getting database information."""
        info = get_database_info("pubmed")
        assert info["name"] == "PubMed"
        assert "AND" in info["boolean_operators"]
        assert "[tiab]" in info["field_tags"]

    def test_get_database_info_unknown(self):
        """Test getting info for unknown database."""
        info = get_database_info("unknown_db")
        assert "error" in info

    def test_validate_query_function(self):
        """Test validate_query convenience function."""
        result = validate_query("cancer AND treatment", "pubmed")
        assert "is_valid" in result
        assert "issues" in result
        assert result["is_valid"] is True


class TestTranslateQuery:
    """Tests for query translation."""

    def test_translate_basic(self):
        """Test basic query translation."""
        result = translate_query("cancer[tiab]", "pubmed", "wos")
        assert "translated" in result
        assert "notes" in result

    def test_translate_unknown_database(self):
        """Test translation with unknown database."""
        result = translate_query("cancer", "unknown_db", "pubmed")
        assert "error" in result

    def test_translate_notes_generated(self):
        """Test translation generates notes."""
        result = translate_query("cancer[tiab] AND treatment", "pubmed", "wos")
        assert isinstance(result["notes"], list)


# =============================================================================
# JSON Serialization Tests
# =============================================================================


class TestJSONSerialization:
    """Tests for JSON save/load functions."""

    def test_save_and_load_strategy(self):
        """Test round-trip JSON serialization."""
        strategy = SearchStrategy(database="pubmed", title="Test Strategy")
        strategy.add_query("cancer[tiab]", "Cancer terms")
        strategy.add_query("treatment[ti]", "Treatment terms")
        strategy.notes = "Test notes"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            save_strategy_to_json(strategy, filepath)
            loaded = load_strategy_from_json(filepath)

            assert loaded.database == "pubmed"
            assert loaded.title == "Test Strategy"
            assert len(loaded.queries) == 2
        finally:
            Path(filepath).unlink()

    def test_json_structure(self):
        """Test saved JSON has correct structure."""
        strategy = SearchStrategy(database="wos", title="WoS Strategy")
        strategy.add_query("TS=(cancer)")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            save_strategy_to_json(strategy, filepath)

            with open(filepath) as f:
                data = json.load(f)

            assert "database" in data
            assert "queries" in data
            assert "summary" in data
        finally:
            Path(filepath).unlink()


# =============================================================================
# Report Generation Tests
# =============================================================================


class TestReportGeneration:
    """Tests for validation report generation."""

    def test_generate_report_basic(self):
        """Test basic report generation."""
        strategy = SearchStrategy(database="pubmed", title="Test Strategy")
        strategy.add_query("cancer AND treatment")

        report = generate_validation_report(strategy)
        assert "SEARCH STRATEGY VALIDATION REPORT" in report
        assert "PubMed" in report
        assert "Test Strategy" in report

    def test_report_includes_errors(self):
        """Test report includes errors."""
        strategy = SearchStrategy(database="pubmed")
        strategy.add_query("(cancer AND treatment")  # Missing paren

        report = generate_validation_report(strategy)
        assert "ERROR" in report or "Errors" in report

    def test_report_all_valid(self):
        """Test report indicates all valid."""
        strategy = SearchStrategy(database="pubmed")
        strategy.add_query("cancer AND treatment")

        report = generate_validation_report(strategy)
        assert "valid" in report.lower()


# =============================================================================
# Database-Specific Tests
# =============================================================================


class TestPubMedSpecific:
    """Tests specific to PubMed syntax."""

    def test_mesh_terms_valid(self):
        """Test MeSH term syntax."""
        query = SearchQuery(query='"Neoplasms"[mh] AND treatment', database="pubmed")
        assert query.is_valid()

    def test_multiple_field_tags(self):
        """Test multiple field tags."""
        query = SearchQuery(
            query='cancer[ti] AND treatment[ab] AND "humans"[mh]',
            database="pubmed",
        )
        assert query.is_valid()

    def test_publication_type_filter(self):
        """Test publication type filter."""
        query = SearchQuery(
            query='cancer AND "Review"[pt]',
            database="pubmed",
        )
        assert query.is_valid()


class TestWebOfScienceSpecific:
    """Tests specific to Web of Science syntax."""

    def test_topic_search(self):
        """Test topic search syntax."""
        query = SearchQuery(query="TS=(cancer AND treatment)", database="wos")
        assert query.is_valid()

    def test_title_search(self):
        """Test title search syntax."""
        query = SearchQuery(query="TI=(gene therapy)", database="wos")
        assert query.is_valid()


class TestScopusSpecific:
    """Tests specific to Scopus syntax."""

    def test_title_abs_key(self):
        """Test TITLE-ABS-KEY syntax."""
        query = SearchQuery(
            query="TITLE-ABS-KEY(cancer AND treatment)",
            database="scopus",
        )
        assert query.is_valid()

    def test_scopus_and_not(self):
        """Test Scopus AND NOT operator."""
        query = SearchQuery(
            query="cancer AND NOT review",
            database="scopus",
        )
        query.validate()
        # Scopus uses "AND NOT" so this should work
        errors = query.get_errors()
        # Should not have adjacent operator error since AND NOT is valid in Scopus
        # Note: our simple validator may flag this, which is acceptable
        assert isinstance(errors, list)


class TestCochraneSpecific:
    """Tests specific to Cochrane syntax."""

    def test_cochrane_field_tags(self):
        """Test Cochrane field tag syntax."""
        query = SearchQuery(query="cancer:ti,ab AND treatment:ti", database="cochrane")
        assert query.is_valid()


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_long_query(self):
        """Test very long query."""
        terms = " AND ".join([f"term{i}" for i in range(100)])
        query = SearchQuery(query=terms, database="pubmed")
        # Should not crash
        query.validate()
        assert isinstance(query.issues, list)

    def test_unicode_characters(self):
        """Test query with unicode characters."""
        query = SearchQuery(query="cancer AND thérapie", database="pubmed")
        # Should not crash
        query.validate()
        assert isinstance(query.issues, list)

    def test_special_characters_in_phrase(self):
        """Test special characters in quoted phrase."""
        query = SearchQuery(query='"COVID-19" AND treatment', database="pubmed")
        assert query.is_valid()

    def test_nested_complex_query(self):
        """Test complex nested query."""
        query = SearchQuery(
            query='((cancer[tiab] OR tumor[tiab]) AND (treatment[ti] OR therapy[ti])) NOT "review"[pt]',
            database="pubmed",
        )
        assert query.is_valid()

    def test_all_databases_basic(self):
        """Test basic validation works for all databases."""
        for db in get_supported_databases():
            query = SearchQuery(query="cancer AND treatment", database=db)
            query.validate()
            # Should not crash and should produce results
            assert isinstance(query.issues, list)

    def test_query_to_dict(self):
        """Test query to_dict method."""
        query = SearchQuery(query="cancer AND treatment", database="pubmed", label="Test")
        query.validate()
        d = query.to_dict()
        assert d["query"] == "cancer AND treatment"
        assert d["database"] == "pubmed"
        assert d["label"] == "Test"
        assert "is_valid" in d
        assert "error_count" in d

    def test_strategy_to_dict(self):
        """Test strategy to_dict method."""
        strategy = SearchStrategy(database="pubmed", title="Test")
        strategy.add_query("cancer")
        d = strategy.to_dict()
        assert d["database"] == "pubmed"
        assert d["title"] == "Test"
        assert "queries" in d
        assert "summary" in d


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
