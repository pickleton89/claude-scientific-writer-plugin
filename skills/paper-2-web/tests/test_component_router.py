"""Tests for component_router module."""

import pytest
from lib.component_router import (
    UseCase,
    ComponentRecommendation,
    COMPONENT_ROUTING,
    KEYWORD_USE_CASE_MAP,
    route_components,
    infer_use_case,
    infer_use_case_from_text,
    get_all_use_cases,
    get_use_case_description,
    recommend_for_venue,
    format_recommendation,
)


class TestUseCase:
    """Tests for UseCase enum."""

    def test_use_case_values(self):
        """Test that UseCase has expected values."""
        expected = [
            "conference_oral",
            "conference_poster",
            "journal_publication",
            "preprint_promotion",
        ]
        for value in expected:
            assert any(uc.value == value for uc in UseCase)

    def test_use_case_count(self):
        """Test that we have a reasonable number of use cases."""
        assert len(UseCase) >= 10


class TestComponentRecommendation:
    """Tests for ComponentRecommendation dataclass."""

    def test_recommendation_creation(self):
        """Test creating ComponentRecommendation."""
        rec = ComponentRecommendation(
            website=True,
            poster=False,
            video=True,
            video_duration="abstract_5min",
            priority_order=("website", "video"),
            rationale="Test rationale",
        )
        assert rec.website is True
        assert rec.poster is False
        assert rec.video is True
        assert rec.video_duration == "abstract_5min"

    def test_primary_components_property(self):
        """Test primary_components property."""
        rec = ComponentRecommendation(
            website=True,
            poster=True,
            video=False,
            priority_order=("website", "poster"),
            rationale="",
        )
        primary = rec.primary_components
        assert "website" in primary
        assert "poster" in primary
        assert "video" not in primary


class TestComponentRouting:
    """Tests for COMPONENT_ROUTING dictionary."""

    def test_all_use_cases_have_routing(self):
        """Test that all use cases have routing entries."""
        for use_case in UseCase:
            assert use_case in COMPONENT_ROUTING, f"Missing routing for {use_case}"

    def test_routing_has_rationale(self):
        """Test that all routings have rationale."""
        for use_case, rec in COMPONENT_ROUTING.items():
            assert rec.rationale, f"Missing rationale for {use_case}"

    def test_routing_has_priority_order(self):
        """Test that all routings have priority order."""
        for use_case, rec in COMPONENT_ROUTING.items():
            assert rec.priority_order, f"Missing priority for {use_case}"


class TestRouteComponents:
    """Tests for route_components function."""

    def test_conference_oral_routing(self):
        """Test routing for conference oral."""
        rec = route_components(UseCase.CONFERENCE_ORAL)
        assert rec.video is True
        assert rec.poster is False
        assert "video" in rec.priority_order

    def test_conference_poster_routing(self):
        """Test routing for conference poster."""
        rec = route_components(UseCase.CONFERENCE_POSTER)
        assert rec.poster is True
        assert rec.website is False
        assert "poster" in rec.priority_order

    def test_journal_publication_routing(self):
        """Test routing for journal publication."""
        rec = route_components(UseCase.JOURNAL_PUBLICATION)
        assert rec.website is True
        assert rec.poster is False
        assert rec.video is False

    def test_preprint_promotion_routing(self):
        """Test routing for preprint promotion."""
        rec = route_components(UseCase.PREPRINT_PROMOTION)
        assert rec.website is True
        assert rec.video is True

    def test_social_media_routing(self):
        """Test routing for social media."""
        rec = route_components(UseCase.SOCIAL_MEDIA)
        assert rec.video is True
        assert rec.video_duration == "short_2min"

    def test_video_abstract_routing(self):
        """Test routing for video abstract."""
        rec = route_components(UseCase.VIDEO_ABSTRACT)
        assert rec.video is True
        assert rec.video_duration == "abstract_5min"
        assert rec.video_style == "academic"

    def test_thesis_defense_routing(self):
        """Test routing for thesis defense."""
        rec = route_components(UseCase.THESIS_DEFENSE)
        assert rec.website is True
        assert rec.poster is True
        assert rec.video is True


class TestInferUseCase:
    """Tests for infer_use_case function."""

    def test_infer_oral_from_keywords(self):
        """Test inferring oral presentation."""
        result = infer_use_case(["oral", "presentation"])
        assert result == UseCase.CONFERENCE_ORAL

    def test_infer_poster_from_keywords(self):
        """Test inferring poster session."""
        result = infer_use_case(["poster"])
        assert result == UseCase.CONFERENCE_POSTER

    def test_infer_preprint_from_arxiv(self):
        """Test inferring preprint from arxiv."""
        result = infer_use_case(["arxiv"])
        assert result == UseCase.PREPRINT_PROMOTION

    def test_infer_preprint_from_biorxiv(self):
        """Test inferring preprint from biorxiv."""
        result = infer_use_case(["biorxiv"])
        assert result == UseCase.PREPRINT_PROMOTION

    def test_infer_journal_from_publication(self):
        """Test inferring journal publication."""
        result = infer_use_case(["journal", "publication"])
        assert result == UseCase.JOURNAL_PUBLICATION

    def test_infer_social_media(self):
        """Test inferring social media."""
        result = infer_use_case(["twitter"])
        assert result == UseCase.SOCIAL_MEDIA

    def test_infer_returns_none_for_unknown(self):
        """Test that unknown keywords return None."""
        result = infer_use_case(["random", "unknown", "words"])
        assert result is None

    def test_infer_case_insensitive(self):
        """Test case-insensitive inference."""
        result1 = infer_use_case(["ORAL"])
        result2 = infer_use_case(["oral"])
        result3 = infer_use_case(["Oral"])
        assert result1 == result2 == result3 == UseCase.CONFERENCE_ORAL


class TestInferUseCaseFromText:
    """Tests for infer_use_case_from_text function."""

    def test_infer_from_sentence(self):
        """Test inference from sentence."""
        result = infer_use_case_from_text("I need a poster for NeurIPS")
        assert result == UseCase.CONFERENCE_POSTER

    def test_infer_from_description(self):
        """Test inference from description."""
        result = infer_use_case_from_text("Creating materials for my oral presentation")
        assert result == UseCase.CONFERENCE_ORAL

    def test_infer_preprint_from_text(self):
        """Test preprint inference from text."""
        result = infer_use_case_from_text("Promoting my arxiv preprint")
        assert result == UseCase.PREPRINT_PROMOTION


class TestGetAllUseCases:
    """Tests for get_all_use_cases function."""

    def test_returns_all_use_cases(self):
        """Test that all use cases are returned."""
        all_cases = get_all_use_cases()
        assert len(all_cases) == len(UseCase)
        for use_case in UseCase:
            assert use_case in all_cases


class TestGetUseCaseDescription:
    """Tests for get_use_case_description function."""

    def test_returns_description(self):
        """Test that description is returned."""
        desc = get_use_case_description(UseCase.CONFERENCE_ORAL)
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_all_use_cases_have_descriptions(self):
        """Test all use cases have descriptions."""
        for use_case in UseCase:
            desc = get_use_case_description(use_case)
            assert desc, f"Missing description for {use_case}"


class TestRecommendForVenue:
    """Tests for recommend_for_venue function."""

    def test_venue_with_oral_keyword(self):
        """Test venue with 'oral' in name."""
        rec = recommend_for_venue("NeurIPS 2024 Oral")
        assert rec.video is True

    def test_venue_with_workshop_keyword(self):
        """Test venue with 'workshop' in name."""
        rec = recommend_for_venue("ICML Workshop on XYZ")
        assert rec.website is True
        assert rec.video is True

    def test_venue_with_journal_keyword(self):
        """Test venue with journal keyword."""
        rec = recommend_for_venue("Nature Machine Intelligence Journal")
        assert rec.website is True
        assert rec.poster is False

    def test_default_venue_recommendation(self):
        """Test default venue gives poster recommendation."""
        rec = recommend_for_venue("NeurIPS 2024")
        assert rec.poster is True


class TestFormatRecommendation:
    """Tests for format_recommendation function."""

    def test_format_basic(self):
        """Test basic formatting."""
        rec = route_components(UseCase.CONFERENCE_POSTER)
        formatted = format_recommendation(rec)
        assert isinstance(formatted, str)
        assert "Poster" in formatted

    def test_format_includes_rationale(self):
        """Test that rationale is included."""
        rec = route_components(UseCase.PREPRINT_PROMOTION)
        formatted = format_recommendation(rec)
        assert "Rationale" in formatted

    def test_format_includes_priority(self):
        """Test that priority is included."""
        rec = route_components(UseCase.THESIS_DEFENSE)
        formatted = format_recommendation(rec)
        assert "Priority" in formatted or "priority" in formatted


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_route_components_deterministic(self):
        """Test that routing is deterministic."""
        results = [route_components(UseCase.PREPRINT_PROMOTION) for _ in range(5)]
        assert all(r == results[0] for r in results)

    def test_infer_use_case_deterministic(self):
        """Test that inference is deterministic."""
        results = [infer_use_case(["arxiv", "paper"]) for _ in range(5)]
        assert all(r == results[0] for r in results)

    def test_keyword_ordering_doesnt_matter(self):
        """Test that keyword order doesn't affect inference."""
        result1 = infer_use_case(["arxiv", "preprint"])
        result2 = infer_use_case(["preprint", "arxiv"])
        assert result1 == result2


class TestKeywordUseCaseMap:
    """Tests for KEYWORD_USE_CASE_MAP."""

    def test_keywords_map_to_valid_use_cases(self):
        """Test all keywords map to valid use cases."""
        for keyword, use_case in KEYWORD_USE_CASE_MAP.items():
            assert isinstance(use_case, UseCase)

    def test_common_keywords_covered(self):
        """Test common keywords are covered."""
        common = ["poster", "oral", "talk", "journal", "preprint", "arxiv"]
        for keyword in common:
            assert keyword in KEYWORD_USE_CASE_MAP, f"Missing keyword: {keyword}"
