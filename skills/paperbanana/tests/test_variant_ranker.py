"""Tests for variant_ranker: multimodal ranking of variant figures."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from variant_ranker import (
    RankingResult,
    VariantScore,
    _fallback_ranking,
    _parse_ranking_response,
    compute_composite,
    rank_variants,
)


class TestComputeComposite:
    """Test weighted composite score calculation."""

    def test_weights_sum_to_one(self):
        """Weights F=0.35 + R=0.25 + C=0.15 + A=0.25 = 1.0."""
        from variant_ranker import (
            _W_AESTHETICS,
            _W_CONCISENESS,
            _W_FAITHFULNESS,
            _W_READABILITY,
        )

        total = _W_FAITHFULNESS + _W_READABILITY + _W_CONCISENESS + _W_AESTHETICS
        assert abs(total - 1.0) < 1e-10

    def test_perfect_scores(self):
        assert compute_composite(1.0, 1.0, 1.0, 1.0) == 1.0

    def test_zero_scores(self):
        assert compute_composite(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_mixed_scores(self):
        result = compute_composite(0.8, 0.6, 0.4, 0.7)
        expected = 0.8 * 0.35 + 0.6 * 0.25 + 0.4 * 0.15 + 0.7 * 0.25
        assert abs(result - expected) < 1e-10

    def test_faithfulness_has_highest_weight(self):
        """Faithfulness should contribute more than any other single dim."""
        f_only = compute_composite(1.0, 0.0, 0.0, 0.0)
        r_only = compute_composite(0.0, 1.0, 0.0, 0.0)
        c_only = compute_composite(0.0, 0.0, 1.0, 0.0)
        a_only = compute_composite(0.0, 0.0, 0.0, 1.0)
        assert f_only > r_only
        assert f_only > c_only
        assert f_only > a_only


class TestVariantScore:
    """Test VariantScore dataclass."""

    def test_fields(self):
        vs = VariantScore(
            variant_index=0,
            strategy="faithful",
            image_path="/tmp/v0.png",
            faithfulness=0.8,
            conciseness=0.7,
            readability=0.6,
            aesthetics=0.9,
            composite_score=0.77,
            rank=1,
        )
        assert vs.variant_index == 0
        assert vs.strategy == "faithful"
        assert vs.rank == 1


class TestRankingResult:
    """Test RankingResult dataclass."""

    def test_winner_selection(self):
        scores = [
            VariantScore(0, "faithful", "/a.png", 0.5, 0.5, 0.5, 0.5, 0.5, 2),
            VariantScore(1, "enhanced", "/b.png", 0.9, 0.9, 0.9, 0.9, 0.9, 1),
        ]
        rr = RankingResult(scores=scores, winner_index=1, ranking_rationale="Better")
        assert rr.winner_index == 1
        assert len(rr.scores) == 2


class TestParseRankingResponse:
    """Test JSON response parsing."""

    def test_valid_json(self):
        response = json.dumps({
            "variants": [
                {"index": 0, "faithfulness": 0.8, "readability": 0.7, "conciseness": 0.6, "aesthetics": 0.9},
                {"index": 1, "faithfulness": 0.6, "readability": 0.8, "conciseness": 0.7, "aesthetics": 0.5},
            ],
            "rationale": "Variant 0 is more faithful.",
        })
        result = _parse_ranking_response(
            response, ["/a.png", "/b.png"], ["faithful", "enhanced"]
        )
        assert isinstance(result, RankingResult)
        assert len(result.scores) == 2
        # Variant 0 should have higher composite
        assert result.scores[0].rank == 1
        assert result.ranking_rationale == "Variant 0 is more faithful."

    def test_json_with_code_fences(self):
        """Handle markdown code fence wrapping."""
        inner = json.dumps({
            "variants": [
                {"index": 0, "faithfulness": 0.7, "readability": 0.7, "conciseness": 0.7, "aesthetics": 0.7},
            ],
            "rationale": "Only one variant.",
        })
        response = f"```json\n{inner}\n```"
        result = _parse_ranking_response(response, ["/a.png"], ["faithful"])
        assert len(result.scores) == 1


class TestFallbackRanking:
    """Test fallback when API fails."""

    def test_equal_scores(self):
        result = _fallback_ranking(["/a.png", "/b.png"], ["faithful", "enhanced"])
        assert result.winner_index == 0
        assert len(result.scores) == 2
        for s in result.scores:
            assert s.faithfulness == 0.5
            assert s.readability == 0.5
            assert s.conciseness == 0.5
            assert s.aesthetics == 0.5

    def test_fallback_rationale(self):
        result = _fallback_ranking(["/a.png"], ["faithful"])
        assert "Fallback" in result.ranking_rationale


class TestRankVariants:
    """Test rank_variants with mocked API."""

    @patch("variant_ranker._rank_via_gemini", side_effect=RuntimeError("API down"))
    def test_api_failure_returns_fallback(self, mock_gemini):
        """When API call fails, should return fallback scores."""
        result = rank_variants(
            image_paths=["/tmp/a.png", "/tmp/b.png"],
            strategies=["faithful", "enhanced"],
            caption="Test caption",
            source_text="Test text",
            api_key="fake-key",
        )
        assert result.winner_index == 0
        assert "Fallback" in result.ranking_rationale


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
