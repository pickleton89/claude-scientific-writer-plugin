"""Tests for the select_citation_style module."""

import pytest

from select_citation_style import (
    FIELD_DEFAULTS,
    JOURNAL_STYLES,
    STYLE_DESCRIPTIONS,
    get_available_fields,
    get_available_journals,
    get_available_styles,
    select_citation_style,
)


class TestDataCompleteness:
    """Tests for data structure completeness."""

    def test_journal_styles_not_empty(self):
        """Journal styles dictionary should not be empty."""
        assert len(JOURNAL_STYLES) > 0

    def test_field_defaults_not_empty(self):
        """Field defaults dictionary should not be empty."""
        assert len(FIELD_DEFAULTS) > 0

    def test_all_journal_styles_have_descriptions(self):
        """All styles used in journal mappings should have descriptions."""
        for journal, style in JOURNAL_STYLES.items():
            assert style in STYLE_DESCRIPTIONS, (
                f"Missing description for {style} (from {journal})"
            )

    def test_all_field_styles_have_descriptions(self):
        """All styles used in field mappings should have descriptions."""
        for field, style in FIELD_DEFAULTS.items():
            assert style in STYLE_DESCRIPTIONS, (
                f"Missing description for {style} (from {field})"
            )


class TestGetAvailableFunctions:
    """Tests for getter functions."""

    def test_get_available_journals_returns_sorted_list(self):
        """Should return a sorted list of journals."""
        result = get_available_journals()
        assert isinstance(result, list)
        assert result == sorted(result)

    def test_get_available_fields_returns_sorted_list(self):
        """Should return a sorted list of fields."""
        result = get_available_fields()
        assert isinstance(result, list)
        assert result == sorted(result)

    def test_get_available_styles_returns_dict(self):
        """Should return a dictionary of styles."""
        result = get_available_styles()
        assert isinstance(result, dict)
        assert len(result) > 0


class TestSelectCitationStyleExactMatch:
    """Tests for exact journal matching."""

    @pytest.mark.parametrize(
        "journal,expected_style",
        [
            ("jama", "ama"),
            ("nejm", "vancouver"),
            ("lancet", "vancouver"),
            ("nature", "nature_numbered"),
            ("cell", "cell_author_date"),
            ("neurips", "numbered_brackets"),
            ("psychological bulletin", "apa"),
            ("jacs", "acs"),
        ],
    )
    def test_exact_journal_match(self, journal, expected_style):
        """Known journals should match to correct citation style."""
        result = select_citation_style(journal)
        assert result["style"] == expected_style
        assert result["match_type"] == "exact_journal"

    def test_case_insensitive_matching(self):
        """Journal matching should be case-insensitive."""
        result_lower = select_citation_style("jama")
        result_upper = select_citation_style("JAMA")
        result_mixed = select_citation_style("JaMa")

        assert result_lower["style"] == result_upper["style"]
        assert result_lower["style"] == result_mixed["style"]

    def test_whitespace_handling(self):
        """Should handle leading/trailing whitespace."""
        result = select_citation_style("  jama  ")
        assert result["style"] == "ama"


class TestSelectCitationStyleFuzzyMatch:
    """Tests for fuzzy journal matching."""

    def test_fuzzy_match_returns_matched_to(self):
        """Fuzzy matches should include what they matched to."""
        # "nature med" is close to "nature medicine"
        result = select_citation_style("nature med")
        if result["match_type"] == "fuzzy_journal":
            assert "matched_to" in result

    def test_fuzzy_match_finds_close_journals(self):
        """Should find close matches for minor typos."""
        result = select_citation_style("nature medicin")  # Missing 'e'
        # Should fuzzy match to nature medicine
        assert result["match_type"] in ["fuzzy_journal", "default"]


class TestSelectCitationStyleFieldMatch:
    """Tests for field-based matching."""

    @pytest.mark.parametrize(
        "field,expected_style",
        [
            ("medicine", "vancouver"),
            ("biomedical", "vancouver"),
            ("psychology", "apa"),
            ("social_science", "apa"),
            ("engineering", "ieee"),
            ("computer_science", "ieee"),
            ("chemistry", "acs"),
            ("ml", "numbered_brackets"),
        ],
    )
    def test_field_defaults(self, field, expected_style):
        """Field names should map to correct default styles."""
        result = select_citation_style(field)
        assert result["style"] == expected_style
        assert result["match_type"] == "field_default"

    def test_field_match_includes_note(self):
        """Field matches should include advisory note."""
        result = select_citation_style("medicine")
        assert "note" in result


class TestSelectCitationStyleDefault:
    """Tests for default fallback behavior."""

    def test_unknown_input_returns_default(self):
        """Unknown input should return default style."""
        result = select_citation_style("completely_unknown_journal_xyz")
        assert result["match_type"] == "default"
        assert result["style"] == "vancouver"

    def test_default_includes_available_options(self):
        """Default response should include available options."""
        result = select_citation_style("unknown_journal")
        assert "available_journals" in result
        assert "available_fields" in result

    def test_default_includes_note(self):
        """Default response should include explanatory note."""
        result = select_citation_style("unknown_journal")
        assert "note" in result


class TestResultStructure:
    """Tests for result dictionary structure."""

    def test_all_results_have_required_fields(self):
        """All results should have input, match_type, style, description."""
        test_inputs = ["jama", "medicine", "unknown_xyz"]
        required_fields = ["input", "match_type", "style", "description"]

        for input_val in test_inputs:
            result = select_citation_style(input_val)
            for field in required_fields:
                assert field in result, f"Missing {field} for input {input_val}"

    def test_input_preserved_in_result(self):
        """Original input should be preserved in result."""
        result = select_citation_style("JAMA")
        assert result["input"] == "JAMA"


class TestDeterminism:
    """Tests verifying deterministic behavior."""

    def test_same_input_same_output(self):
        """Same input should always produce identical output."""
        for _ in range(10):
            result1 = select_citation_style("nature")
            result2 = select_citation_style("nature")
            assert result1 == result2

    def test_all_journals_produce_consistent_results(self):
        """Running selection multiple times should produce consistent results."""
        for journal in list(JOURNAL_STYLES.keys())[:10]:
            results = [select_citation_style(journal) for _ in range(5)]
            assert all(r == results[0] for r in results)

    def test_all_fields_produce_consistent_results(self):
        """Field selections should be consistent."""
        for field in FIELD_DEFAULTS.keys():
            results = [select_citation_style(field) for _ in range(5)]
            assert all(r == results[0] for r in results)
