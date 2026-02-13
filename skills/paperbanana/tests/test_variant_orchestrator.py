"""Tests for variant_orchestrator: multi-variant generation flow."""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from variant_intents import VariantIntent, VariantStrategy
from variant_orchestrator import (
    MultiVariantResult,
    VariantConfig,
    build_variant_review_log,
)
from variant_ranker import RankingResult, VariantScore


class TestVariantConfig:
    """Test VariantConfig defaults."""

    def test_defaults(self):
        cfg = VariantConfig()
        assert cfg.n_variants == 3
        assert cfg.delay_between_runs == 30.0
        assert cfg.refine_winner is True
        assert cfg.refinement_iterations == 2
        assert cfg.verbose is False

    def test_custom_values(self):
        cfg = VariantConfig(n_variants=5, delay_between_runs=10.0, verbose=True)
        assert cfg.n_variants == 5
        assert cfg.delay_between_runs == 10.0
        assert cfg.verbose is True


class TestMultiVariantResult:
    """Test MultiVariantResult defaults."""

    def test_defaults(self):
        result = MultiVariantResult()
        assert result.variants == []
        assert result.ranking is None
        assert result.refined_image_path is None
        assert result.review_log_path is None


class TestBuildVariantReviewLog:
    """Test review log construction."""

    def _make_result(self) -> MultiVariantResult:
        """Create a sample MultiVariantResult for testing."""
        scores = [
            VariantScore(0, "faithful", "/tmp/v0.png", 0.8, 0.7, 0.6, 0.9, 0.77, 1),
            VariantScore(1, "enhanced", "/tmp/v1.png", 0.6, 0.5, 0.8, 0.5, 0.61, 2),
        ]
        ranking = RankingResult(
            scores=scores,
            winner_index=0,
            ranking_rationale="Variant 0 is more faithful.",
        )
        return MultiVariantResult(
            variants=[
                {
                    "index": 0,
                    "strategy": "faithful",
                    "image_path": "/tmp/v0.png",
                    "communicative_intent": "Original caption",
                    "scores": {"faithfulness": 0.8, "readability": 0.6, "conciseness": 0.7, "aesthetics": 0.9},
                },
                {
                    "index": 1,
                    "strategy": "enhanced",
                    "image_path": "/tmp/v1.png",
                    "communicative_intent": "Enhanced caption",
                    "scores": {"faithfulness": 0.6, "readability": 0.8, "conciseness": 0.5, "aesthetics": 0.5},
                },
            ],
            ranking=ranking,
            refined_image_path="/tmp/refined.png",
        )

    def test_has_required_keys(self):
        result = self._make_result()
        log = build_variant_review_log(
            result, "source text", "caption", "journal", True
        )
        assert "source_text_preview" in log
        assert "caption" in log
        assert "doc_type" in log
        assert "brand_enabled" in log
        assert "n_variants" in log
        assert "variants" in log
        assert "ranking" in log
        assert "refined_image_path" in log

    def test_source_text_truncated(self):
        long_text = "x" * 500
        result = self._make_result()
        log = build_variant_review_log(result, long_text, "caption")
        assert len(log["source_text_preview"]) == 200

    def test_ranking_scores_serializable(self):
        """Ranking scores should be JSON-serializable dicts."""
        import json

        result = self._make_result()
        log = build_variant_review_log(result, "text", "caption")
        # Should not raise
        json.dumps(log)

    def test_ranking_winner_index(self):
        result = self._make_result()
        log = build_variant_review_log(result, "text", "caption")
        assert log["ranking"]["winner_index"] == 0

    def test_no_ranking(self):
        """Log without ranking (e.g., single variant)."""
        result = MultiVariantResult(
            variants=[{"index": 0, "strategy": "faithful", "image_path": "/tmp/v0.png"}],
        )
        log = build_variant_review_log(result, "text", "caption")
        assert "ranking" not in log

    def test_no_refined_image(self):
        """Log without refinement."""
        result = MultiVariantResult(
            variants=[{"index": 0, "strategy": "faithful", "image_path": "/tmp/v0.png"}],
        )
        log = build_variant_review_log(result, "text", "caption")
        assert "refined_image_path" not in log

    def test_doc_type_passed_through(self):
        result = self._make_result()
        log = build_variant_review_log(
            result, "text", "caption", doc_type="poster", brand_enabled=False
        )
        assert log["doc_type"] == "poster"
        assert log["brand_enabled"] is False


class TestRunMultiVariant:
    """Test run_multi_variant orchestration with mocked pipeline."""

    @patch("variant_orchestrator.rank_variants")
    @patch("variant_orchestrator.generate_variant_intents")
    def test_orchestrator_flow(self, mock_intents, mock_rank):
        """Test the full orchestration flow with mocked components."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Mock intents
            mock_intents.return_value = [
                VariantIntent(0, VariantStrategy.FAITHFUL, "Original", "Faithful"),
                VariantIntent(1, VariantStrategy.ENHANCED, "Enhanced", "Enhanced detail"),
            ]

            # Mock ranking
            mock_rank.return_value = RankingResult(
                scores=[
                    VariantScore(0, "faithful", str(tmp_path / "v0.png"), 0.8, 0.7, 0.7, 0.8, 0.76, 1),
                    VariantScore(1, "enhanced", str(tmp_path / "v1.png"), 0.6, 0.6, 0.6, 0.6, 0.6, 2),
                ],
                winner_index=0,
                ranking_rationale="V0 better",
            )

            # Mock PaperBanana pipeline result
            mock_gen_result = MagicMock()
            mock_gen_result.image_path = None
            mock_gen_result.image_data = b"fake-png-data"
            mock_gen_result.evaluation = None

            # Mock the paperbanana imports inside run_multi_variant
            mock_pipeline = MagicMock()
            mock_pipeline.generate = AsyncMock(return_value=mock_gen_result)

            mock_pb_module = MagicMock()
            mock_pb_module.PaperBananaPipeline.return_value = mock_pipeline
            mock_pb_module.DiagramType.METHODOLOGY = "METHODOLOGY"
            mock_pb_module.GenerationInput.return_value = MagicMock()

            with patch.dict("sys.modules", {"paperbanana": mock_pb_module}):
                from variant_orchestrator import run_multi_variant

                config = VariantConfig(
                    n_variants=2,
                    delay_between_runs=0.0,
                    refine_winner=False,
                )

                result = asyncio.run(run_multi_variant(
                    source_text="Test source",
                    caption="Test caption",
                    output_dir=str(tmp_path),
                    output_stem="test",
                    settings_factory=MagicMock(return_value=MagicMock()),
                    api_key="fake-key",
                    config=config,
                ))

                assert len(result.variants) == 2
                assert result.ranking is not None
                assert result.ranking.winner_index == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
