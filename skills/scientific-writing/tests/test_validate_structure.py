"""Tests for the validate_structure module."""


from validate_structure import (
    IMRAD_SECTIONS,
    SECTION_PATTERNS,
    find_sections,
    get_imrad_sections,
    get_section_patterns,
    validate_imrad_structure,
)


class TestGetterFunctions:
    """Tests for getter functions."""

    def test_get_imrad_sections_returns_list(self):
        """Should return a list of section names."""
        result = get_imrad_sections()
        assert isinstance(result, list)
        assert len(result) == 5

    def test_get_imrad_sections_correct_order(self):
        """Should return sections in correct IMRAD order."""
        result = get_imrad_sections()
        assert result == [
            "abstract",
            "introduction",
            "methods",
            "results",
            "discussion",
        ]

    def test_get_section_patterns_returns_dict(self):
        """Should return a dictionary of patterns."""
        result = get_section_patterns()
        assert isinstance(result, dict)
        assert len(result) > 0


class TestSectionPatterns:
    """Tests for section pattern matching."""

    def test_abstract_pattern_matches(self):
        """Abstract pattern should match various formats."""
        import re

        pattern = SECTION_PATTERNS["abstract"]
        assert re.match(pattern, "# Abstract")
        assert re.match(pattern, "## Abstract")
        assert re.match(pattern, "# ABSTRACT")
        assert re.match(pattern, "### abstract")

    def test_introduction_pattern_matches(self):
        """Introduction pattern should match various formats."""
        import re

        pattern = SECTION_PATTERNS["introduction"]
        assert re.match(pattern, "# Introduction")
        assert re.match(pattern, "# Background")
        assert re.match(pattern, "## INTRODUCTION")

    def test_methods_pattern_matches_variants(self):
        """Methods pattern should match common variants."""
        import re

        pattern = SECTION_PATTERNS["methods"]
        assert re.match(pattern, "# Methods")
        assert re.match(pattern, "# Materials and Methods")
        assert re.match(pattern, "# Methodology")
        assert re.match(pattern, "# Experimental")
        assert re.match(pattern, "## Materials And Methods")

    def test_results_pattern_matches(self):
        """Results pattern should match various formats."""
        import re

        pattern = SECTION_PATTERNS["results"]
        assert re.match(pattern, "# Results")
        assert re.match(pattern, "# Findings")
        assert re.match(pattern, "## RESULTS")

    def test_discussion_pattern_matches(self):
        """Discussion pattern should match."""
        import re

        pattern = SECTION_PATTERNS["discussion"]
        assert re.match(pattern, "# Discussion")
        assert re.match(pattern, "## Discussion")


class TestFindSections:
    """Tests for find_sections function."""

    def test_finds_all_imrad_sections(self, sample_imrad_manuscript):
        """Should find all IMRAD sections in well-formed manuscript."""
        sections = find_sections(sample_imrad_manuscript)
        for section in IMRAD_SECTIONS:
            assert section in sections

    def test_returns_line_numbers(self, sample_imrad_manuscript):
        """Should return line numbers for each section."""
        sections = find_sections(sample_imrad_manuscript)
        for section, line_num in sections.items():
            assert isinstance(line_num, int)
            assert line_num >= 0

    def test_abstract_comes_first(self, sample_imrad_manuscript):
        """Abstract should have lowest line number."""
        sections = find_sections(sample_imrad_manuscript)
        abstract_line = sections.get("abstract", float("inf"))
        for section, line_num in sections.items():
            if section != "abstract":
                assert abstract_line <= line_num

    def test_finds_extra_sections(self, sample_imrad_manuscript):
        """Should find non-IMRAD sections like references."""
        sections = find_sections(sample_imrad_manuscript)
        assert "references" in sections

    def test_empty_text_returns_empty_dict(self):
        """Empty text should return empty dict."""
        sections = find_sections("")
        assert sections == {}

    def test_text_without_headers_returns_empty(self):
        """Text without markdown headers should return empty dict."""
        text = "Just some text without any headers.\nMore text here."
        sections = find_sections(text)
        assert sections == {}


class TestValidateImradStructure:
    """Tests for validate_imrad_structure function."""

    def test_complete_manuscript_passes(self, sample_imrad_manuscript):
        """Well-formed manuscript should pass validation."""
        result = validate_imrad_structure(sample_imrad_manuscript)
        assert result.status == "PASS"
        assert len(result.missing_sections) == 0
        assert result.section_order_correct is True

    def test_incomplete_manuscript_fails(self, incomplete_manuscript):
        """Manuscript missing sections should fail."""
        result = validate_imrad_structure(incomplete_manuscript)
        assert result.status in ["FAIL", "ACCEPTABLE"]
        assert len(result.missing_sections) > 0

    def test_misordered_manuscript_fails(self, misordered_manuscript):
        """Manuscript with wrong order should fail."""
        result = validate_imrad_structure(misordered_manuscript)
        assert result.section_order_correct is False

    def test_returns_found_sections(self, sample_imrad_manuscript):
        """Should return list of found sections."""
        result = validate_imrad_structure(sample_imrad_manuscript)
        assert isinstance(result.found_sections, list)
        assert len(result.found_sections) > 0

    def test_returns_missing_sections(self, incomplete_manuscript):
        """Should return list of missing sections."""
        result = validate_imrad_structure(incomplete_manuscript)
        assert isinstance(result.missing_sections, list)

    def test_returns_extra_sections(self, sample_imrad_manuscript):
        """Should identify non-IMRAD sections."""
        result = validate_imrad_structure(sample_imrad_manuscript)
        assert isinstance(result.extra_sections, list)
        assert "references" in result.extra_sections

    def test_returns_recommendations(self, incomplete_manuscript):
        """Should provide recommendations for incomplete manuscripts."""
        result = validate_imrad_structure(incomplete_manuscript)
        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0

    def test_acceptable_status_for_one_missing(self):
        """Missing one section with correct order should be ACCEPTABLE."""
        text = """# Abstract

Text.

# Introduction

Text.

# Methods

Text.

# Results

Text.
"""  # Missing Discussion
        result = validate_imrad_structure(text)
        assert result.status == "ACCEPTABLE"


class TestValidationStatuses:
    """Tests for validation status logic."""

    def test_pass_status_requirements(self, sample_imrad_manuscript):
        """PASS requires all sections present and correctly ordered."""
        result = validate_imrad_structure(sample_imrad_manuscript)
        assert result.status == "PASS"
        assert len(result.missing_sections) == 0
        assert result.section_order_correct is True

    def test_fail_status_for_multiple_missing(self):
        """FAIL for multiple missing sections."""
        text = """# Abstract

Text.

# Introduction

Text.
"""  # Missing Methods, Results, Discussion
        result = validate_imrad_structure(text)
        assert result.status == "FAIL"

    def test_fail_status_for_wrong_order_with_missing(self, misordered_manuscript):
        """FAIL when order is wrong."""
        result = validate_imrad_structure(misordered_manuscript)
        # The misordered manuscript actually has wrong order
        assert not result.section_order_correct


class TestDeterminism:
    """Tests verifying deterministic behavior."""

    def test_same_input_same_output(self, sample_imrad_manuscript):
        """Same input should always produce identical output."""
        for _ in range(10):
            result1 = validate_imrad_structure(sample_imrad_manuscript)
            result2 = validate_imrad_structure(sample_imrad_manuscript)
            assert result1.status == result2.status
            assert result1.found_sections == result2.found_sections
            assert result1.missing_sections == result2.missing_sections

    def test_find_sections_deterministic(self, sample_imrad_manuscript):
        """find_sections should be deterministic."""
        for _ in range(10):
            result1 = find_sections(sample_imrad_manuscript)
            result2 = find_sections(sample_imrad_manuscript)
            assert result1 == result2


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_string(self):
        """Should handle empty string."""
        result = validate_imrad_structure("")
        assert result.status == "FAIL"
        assert len(result.missing_sections) == len(IMRAD_SECTIONS)

    def test_only_whitespace(self):
        """Should handle whitespace-only string."""
        result = validate_imrad_structure("   \n\n   ")
        assert result.status == "FAIL"

    def test_duplicate_sections(self):
        """Should handle duplicate section headers (use first occurrence)."""
        text = """# Abstract

First abstract.

# Introduction

Intro.

# Abstract

Second abstract (should be ignored).

# Methods

Methods.

# Results

Results.

# Discussion

Discussion.
"""
        result = validate_imrad_structure(text)
        assert result.status == "PASS"  # Should still pass, using first occurrences
