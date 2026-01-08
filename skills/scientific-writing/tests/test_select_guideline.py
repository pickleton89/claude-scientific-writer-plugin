"""Tests for the select_guideline module."""

import pytest

from select_guideline import (
    GUIDELINE_MAP,
    StudyDesign,
    get_valid_study_designs,
    select_guideline,
)


class TestStudyDesignEnum:
    """Tests for StudyDesign enum."""

    def test_all_study_designs_have_guidelines(self):
        """Every study design enum should have a corresponding guideline mapping."""
        for design in StudyDesign:
            assert design in GUIDELINE_MAP, f"Missing guideline for {design}"

    def test_study_design_values_are_lowercase(self):
        """Study design values should all be lowercase for consistent matching."""
        for design in StudyDesign:
            assert design.value == design.value.lower()


class TestGetValidStudyDesigns:
    """Tests for get_valid_study_designs function."""

    def test_returns_list(self):
        """Should return a list."""
        result = get_valid_study_designs()
        assert isinstance(result, list)

    def test_contains_all_enum_values(self):
        """Should contain all StudyDesign enum values."""
        result = get_valid_study_designs()
        for design in StudyDesign:
            assert design.value in result

    def test_count_matches_enum(self):
        """Should have same count as enum."""
        result = get_valid_study_designs()
        assert len(result) == len(StudyDesign)


class TestSelectGuideline:
    """Tests for select_guideline function."""

    @pytest.mark.parametrize(
        "study_design,expected_guideline",
        [
            ("rct", "CONSORT"),
            ("cohort", "STROBE"),
            ("case_control", "STROBE"),
            ("cross_sectional", "STROBE"),
            ("systematic_review", "PRISMA"),
            ("meta_analysis", "PRISMA"),
            ("case_report", "CARE"),
            ("qualitative", "SRQR"),
            ("diagnostic_accuracy", "STARD"),
            ("prediction_model", "TRIPOD"),
            ("animal_study", "ARRIVE"),
            ("quality_improvement", "SQUIRE"),
            ("economic_evaluation", "CHEERS"),
        ],
    )
    def test_guideline_selection(self, study_design, expected_guideline):
        """Each study design should map to correct reporting guideline."""
        result = select_guideline(study_design)
        assert result["guideline"] == expected_guideline

    def test_case_insensitive(self):
        """Study design matching should be case-insensitive."""
        result_lower = select_guideline("rct")
        result_upper = select_guideline("RCT")
        result_mixed = select_guideline("Rct")

        assert result_lower["guideline"] == result_upper["guideline"]
        assert result_lower["guideline"] == result_mixed["guideline"]

    def test_unknown_study_design(self):
        """Unknown study design should return error with valid options."""
        result = select_guideline("unknown_type")
        assert "error" in result
        assert "valid_options" in result
        assert len(result["valid_options"]) > 0

    def test_result_contains_url(self):
        """Valid results should contain a URL."""
        result = select_guideline("rct")
        assert "url" in result
        assert result["url"].startswith("http")

    def test_result_contains_checklist_items(self):
        """Valid results should contain checklist item count."""
        result = select_guideline("rct")
        assert "checklist_items" in result
        assert isinstance(result["checklist_items"], int)
        assert result["checklist_items"] > 0

    def test_result_contains_equator_search(self):
        """Valid results should contain EQUATOR Network search URL."""
        result = select_guideline("cohort")
        assert "equator_search" in result
        assert "equator-network.org" in result["equator_search"]

    def test_result_contains_extensions(self):
        """Valid results should contain available extensions list."""
        result = select_guideline("rct")
        assert "available_extensions" in result
        assert isinstance(result["available_extensions"], list)

    def test_rct_has_extensions(self):
        """RCT guideline should have extensions available."""
        result = select_guideline("rct")
        assert len(result["available_extensions"]) > 0
        assert "cluster" in result["available_extensions"]


class TestGuidelineMapCompleteness:
    """Tests for GUIDELINE_MAP data completeness."""

    def test_all_guidelines_have_required_fields(self):
        """Each guideline entry should have all required fields."""
        required_fields = ["primary", "url", "items", "extensions"]
        for design, guideline in GUIDELINE_MAP.items():
            for field in required_fields:
                assert field in guideline, f"Missing {field} for {design}"

    def test_all_urls_are_valid_format(self):
        """All URLs should be properly formatted."""
        for design, guideline in GUIDELINE_MAP.items():
            url = guideline["url"]
            assert url.startswith("http"), f"Invalid URL for {design}: {url}"

    def test_all_item_counts_are_positive(self):
        """All checklist item counts should be positive integers."""
        for design, guideline in GUIDELINE_MAP.items():
            items = guideline["items"]
            assert isinstance(items, int), f"Items not int for {design}"
            assert items > 0, f"Items not positive for {design}"

    def test_extensions_are_lists(self):
        """All extensions should be lists."""
        for design, guideline in GUIDELINE_MAP.items():
            extensions = guideline["extensions"]
            assert isinstance(extensions, list), f"Extensions not list for {design}"


class TestDeterminism:
    """Tests verifying deterministic behavior."""

    def test_same_input_same_output(self):
        """Same input should always produce identical output."""
        for _ in range(10):
            result1 = select_guideline("rct")
            result2 = select_guideline("rct")
            assert result1 == result2

    def test_all_designs_produce_consistent_results(self):
        """Running selection multiple times should produce consistent results."""
        for design in get_valid_study_designs():
            results = [select_guideline(design) for _ in range(5)]
            assert all(r == results[0] for r in results)
