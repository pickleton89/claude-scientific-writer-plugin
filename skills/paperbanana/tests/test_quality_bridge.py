"""Tests for quality_bridge: 4-dim → 5-point rubric score mapping."""

from __future__ import annotations

import sys
from pathlib import Path

# Add utils to path
sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "scripts")
)

from utils.quality_bridge import (
    DOC_TYPE_THRESHOLDS,
    PaperBananaScores,
    get_threshold,
    map_to_rubric,
    meets_threshold,
    rubric_total,
    to_review_dict,
)


class TestScaleMapping:
    """Test the 0-1 → 0-2 scaling."""

    def test_perfect_scores(self):
        scores = PaperBananaScores(1.0, 1.0, 1.0, 1.0)
        rubric = map_to_rubric(scores)
        assert rubric_total(rubric) == 10.0

    def test_zero_scores(self):
        scores = PaperBananaScores(0.0, 0.0, 0.0, 0.0)
        rubric = map_to_rubric(scores)
        assert rubric_total(rubric) == 0.0

    def test_mid_scores(self):
        scores = PaperBananaScores(0.5, 0.5, 0.5, 0.5)
        rubric = map_to_rubric(scores)
        assert rubric_total(rubric) == 5.0

    def test_mixed_scores(self):
        scores = PaperBananaScores(0.9, 0.8, 0.7, 0.85)
        rubric = map_to_rubric(scores)
        total = rubric_total(rubric)
        # faithfulness(0.9→1.8) + readability(0.8→1.6) + readability(0.8→1.6)
        # + conciseness(0.7→1.4) + aesthetics(0.85→1.7) = 8.1
        assert 8.0 <= total <= 8.2


class TestMappingDimensions:
    """Test correct dimension mapping."""

    def test_faithfulness_maps_to_accuracy(self):
        scores = PaperBananaScores(1.0, 0.0, 0.0, 0.0)
        rubric = map_to_rubric(scores)
        assert rubric.scientific_accuracy == 2.0
        assert rubric.clarity_readability == 0.0

    def test_readability_maps_to_clarity_and_labels(self):
        scores = PaperBananaScores(0.0, 1.0, 0.0, 0.0)
        rubric = map_to_rubric(scores)
        assert rubric.clarity_readability == 2.0
        assert rubric.label_quality == 2.0

    def test_conciseness_maps_to_layout(self):
        scores = PaperBananaScores(0.0, 0.0, 1.0, 0.0)
        rubric = map_to_rubric(scores)
        assert rubric.layout_composition == 2.0

    def test_aesthetics_maps_to_appearance(self):
        scores = PaperBananaScores(0.0, 0.0, 0.0, 1.0)
        rubric = map_to_rubric(scores)
        assert rubric.professional_appearance == 2.0


class TestThresholds:
    """Test document type threshold lookup."""

    def test_journal_threshold(self):
        config = get_threshold("journal")
        assert config["threshold"] == 8.5

    def test_presentation_threshold(self):
        config = get_threshold("presentation")
        assert config["threshold"] == 6.5

    def test_unknown_falls_to_default(self):
        config = get_threshold("unknown_type")
        assert config["threshold"] == 7.5

    def test_all_doc_types_present(self):
        expected = [
            "journal", "conference", "thesis", "grant",
            "preprint", "report", "poster", "presentation", "default",
        ]
        for dt in expected:
            assert dt in DOC_TYPE_THRESHOLDS


class TestMeetsThreshold:
    """Test threshold comparison."""

    def test_passes_journal(self):
        scores = PaperBananaScores(0.9, 0.85, 0.85, 0.9)
        rubric = map_to_rubric(scores)
        assert meets_threshold(rubric, 8.5)

    def test_fails_journal(self):
        scores = PaperBananaScores(0.7, 0.7, 0.7, 0.7)
        rubric = map_to_rubric(scores)
        assert not meets_threshold(rubric, 8.5)

    def test_passes_presentation(self):
        scores = PaperBananaScores(0.7, 0.7, 0.7, 0.7)
        rubric = map_to_rubric(scores)
        assert meets_threshold(rubric, 6.5)


class TestReviewDict:
    """Test review log dictionary format."""

    def test_has_required_keys(self):
        pb = PaperBananaScores(0.8, 0.75, 0.7, 0.85)
        rubric = map_to_rubric(pb)
        d = to_review_dict(pb, rubric)
        assert "paperbanana_scores" in d
        assert "rubric_scores" in d
        assert "total_score" in d

    def test_paperbanana_scores_preserved(self):
        pb = PaperBananaScores(0.8, 0.75, 0.7, 0.85)
        rubric = map_to_rubric(pb)
        d = to_review_dict(pb, rubric)
        assert d["paperbanana_scores"]["faithfulness"] == 0.8
        assert d["paperbanana_scores"]["readability"] == 0.75

    def test_rubric_scores_correct(self):
        pb = PaperBananaScores(0.8, 0.75, 0.7, 0.85)
        rubric = map_to_rubric(pb)
        d = to_review_dict(pb, rubric)
        assert d["rubric_scores"]["scientific_accuracy"] == 1.6
        assert d["rubric_scores"]["professional_appearance"] == 1.7


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
