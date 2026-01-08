"""Tests for the calculate_targets module."""

import pytest

from calculate_targets import (
    WORD_COUNT_PROPORTIONS,
    calculate_all_targets,
    calculate_citation_targets,
    calculate_display_items,
    calculate_section_words,
    get_document_types,
    get_word_count_proportions,
)


class TestGetterFunctions:
    """Tests for getter functions."""

    def test_get_document_types_returns_list(self):
        """Should return a list of document types."""
        result = get_document_types()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_document_types_includes_common_types(self):
        """Should include common document types."""
        result = get_document_types()
        assert "original_research" in result
        assert "review_article" in result
        assert "case_report" in result

    def test_get_word_count_proportions_returns_dict(self):
        """Should return a dictionary."""
        result = get_word_count_proportions()
        assert isinstance(result, dict)
        assert len(result) > 0


class TestWordCountProportions:
    """Tests for word count proportion data."""

    def test_all_sections_have_min_max(self):
        """All sections should have min and max proportions."""
        for section, props in WORD_COUNT_PROPORTIONS.items():
            assert "min" in props, f"Missing min for {section}"
            assert "max" in props, f"Missing max for {section}"

    def test_min_less_than_max(self):
        """Min should be less than max for all sections."""
        for section, props in WORD_COUNT_PROPORTIONS.items():
            assert props["min"] < props["max"], f"min >= max for {section}"

    def test_proportions_are_valid(self):
        """Proportions should be between 0 and 1."""
        for section, props in WORD_COUNT_PROPORTIONS.items():
            assert 0 < props["min"] < 1, f"Invalid min for {section}"
            assert 0 < props["max"] < 1, f"Invalid max for {section}"

    def test_total_proportions_reasonable(self):
        """Sum of max proportions should allow for overlap (slightly over 1.0 is ok)."""
        total_min = sum(p["min"] for p in WORD_COUNT_PROPORTIONS.values())
        total_max = sum(p["max"] for p in WORD_COUNT_PROPORTIONS.values())
        # Total should be around 1.0, allowing some flexibility
        assert 0.7 < total_min < 1.3
        assert 0.9 < total_max < 1.5


class TestCalculateSectionWords:
    """Tests for calculate_section_words function."""

    def test_returns_dict_with_all_sections(self):
        """Should return targets for all sections."""
        result = calculate_section_words(5000)
        assert isinstance(result, dict)
        for section in WORD_COUNT_PROPORTIONS.keys():
            assert section in result

    def test_each_section_has_required_fields(self):
        """Each section should have min, max, and target."""
        result = calculate_section_words(5000)
        for section, targets in result.items():
            assert "min" in targets
            assert "max" in targets
            assert "target" in targets

    def test_min_less_than_target_less_than_max(self):
        """For each section: min <= target <= max."""
        result = calculate_section_words(5000)
        for section, targets in result.items():
            assert targets["min"] <= targets["target"] <= targets["max"]

    @pytest.mark.parametrize("total_words", [1000, 3000, 5000, 8000, 12000])
    def test_scales_with_total_words(self, total_words):
        """Targets should scale proportionally with total words."""
        result = calculate_section_words(total_words)
        for section, targets in result.items():
            assert targets["min"] > 0
            assert targets["max"] > targets["min"]
            # Check it scales roughly correctly
            expected_min = int(total_words * WORD_COUNT_PROPORTIONS[section]["min"])
            assert targets["min"] == expected_min

    def test_returns_integers(self):
        """All values should be integers."""
        result = calculate_section_words(5000)
        for section, targets in result.items():
            assert isinstance(targets["min"], int)
            assert isinstance(targets["max"], int)
            assert isinstance(targets["target"], int)


class TestCalculateCitationTargets:
    """Tests for calculate_citation_targets function."""

    def test_original_research_targets(self):
        """Should return correct targets for original research."""
        result = calculate_citation_targets("original_research")
        assert "introduction" in result
        assert "methods" in result
        assert "results" in result
        assert "discussion" in result
        assert "total" in result

    def test_review_article_targets(self):
        """Should return correct targets for review articles."""
        result = calculate_citation_targets("review_article")
        assert "total" in result
        assert result["total"]["min"] >= 100  # Reviews need many citations

    def test_unknown_document_type(self):
        """Unknown type should return error."""
        result = calculate_citation_targets("unknown_type")
        assert "error" in result
        assert "valid_types" in result

    def test_case_report_has_lower_targets(self):
        """Case reports should have lower citation targets."""
        result = calculate_citation_targets("case_report")
        assert result["total"]["min"] < 30


class TestCalculateDisplayItems:
    """Tests for calculate_display_items function."""

    def test_returns_required_fields(self):
        """Should return minimum, recommended, maximum, and rule."""
        result = calculate_display_items(5000)
        assert "minimum" in result
        assert "recommended" in result
        assert "maximum" in result
        assert "rule" in result

    def test_minimum_at_least_two(self):
        """Minimum should be at least 2."""
        for words in [1000, 2000, 5000, 10000]:
            result = calculate_display_items(words)
            assert result["minimum"] >= 2

    def test_recommended_at_least_three(self):
        """Recommended should be at least 3."""
        for words in [1000, 2000, 5000, 10000]:
            result = calculate_display_items(words)
            assert result["recommended"] >= 3

    def test_scales_with_word_count(self):
        """More words should mean more display items."""
        result_small = calculate_display_items(2000)
        result_large = calculate_display_items(10000)
        assert result_large["recommended"] > result_small["recommended"]

    def test_ordering_correct(self):
        """minimum <= recommended <= maximum."""
        for words in [1000, 3000, 5000, 8000, 12000]:
            result = calculate_display_items(words)
            assert result["minimum"] <= result["recommended"] <= result["maximum"]


class TestCalculateAllTargets:
    """Tests for calculate_all_targets function."""

    def test_returns_complete_structure(self):
        """Should return all target categories."""
        result = calculate_all_targets(5000, "original_research")
        assert "total_words" in result
        assert "document_type" in result
        assert "section_word_counts" in result
        assert "citation_targets" in result
        assert "display_items" in result

    def test_preserves_input_values(self):
        """Should preserve input values in result."""
        result = calculate_all_targets(5000, "review_article")
        assert result["total_words"] == 5000
        assert result["document_type"] == "review_article"

    @pytest.mark.parametrize(
        "words,doc_type",
        [
            (3000, "original_research"),
            (5000, "review_article"),
            (2000, "case_report"),
            (6000, "meta_analysis"),
            (4000, "methods_paper"),
        ],
    )
    def test_all_document_types(self, words, doc_type):
        """Should work with all document types."""
        result = calculate_all_targets(words, doc_type)
        assert result["document_type"] == doc_type
        assert "error" not in result["citation_targets"]


class TestDeterminism:
    """Tests verifying deterministic behavior."""

    def test_section_words_deterministic(self):
        """Same input should always produce same output."""
        for _ in range(10):
            result1 = calculate_section_words(5000)
            result2 = calculate_section_words(5000)
            assert result1 == result2

    def test_citation_targets_deterministic(self):
        """Citation targets should be consistent."""
        for doc_type in get_document_types():
            results = [calculate_citation_targets(doc_type) for _ in range(5)]
            assert all(r == results[0] for r in results)

    def test_display_items_deterministic(self):
        """Display item calculations should be consistent."""
        for words in [1000, 3000, 5000, 8000]:
            results = [calculate_display_items(words) for _ in range(5)]
            assert all(r == results[0] for r in results)

    def test_all_targets_deterministic(self):
        """Full calculation should be deterministic."""
        for _ in range(10):
            result1 = calculate_all_targets(5000, "original_research")
            result2 = calculate_all_targets(5000, "original_research")
            assert result1 == result2


class TestEdgeCases:
    """Tests for edge cases."""

    def test_minimum_word_count(self):
        """Should handle minimum word count (1000)."""
        result = calculate_section_words(1000)
        assert all(t["min"] > 0 for t in result.values())

    def test_large_word_count(self):
        """Should handle large word counts."""
        result = calculate_section_words(15000)
        assert all(t["max"] > 0 for t in result.values())

    def test_zero_word_count(self):
        """Should handle zero word count gracefully."""
        result = calculate_section_words(0)
        # All targets will be 0
        assert all(t["min"] == 0 for t in result.values())
