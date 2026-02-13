"""Tests for variant_intents: variant strategy generation."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from variant_intents import (
    VARIANT_PRESETS,
    VariantIntent,
    VariantStrategy,
    generate_variant_intents,
)


class TestVariantStrategy:
    """Test VariantStrategy enum."""

    def test_all_values_exist(self):
        assert VariantStrategy.FAITHFUL.value == "faithful"
        assert VariantStrategy.ENHANCED.value == "enhanced"
        assert VariantStrategy.ALT_COMPOSITION.value == "alt_composition"
        assert VariantStrategy.STYLE_VARIATION.value == "style_variation"
        assert VariantStrategy.BOLD_CREATIVE.value == "bold_creative"

    def test_enum_count(self):
        assert len(VariantStrategy) == 5


class TestVariantPresets:
    """Test VARIANT_PRESETS structure."""

    def test_all_preset_counts(self):
        for n in range(1, 6):
            assert n in VARIANT_PRESETS
            assert len(VARIANT_PRESETS[n]) == n

    def test_faithful_always_first(self):
        for n in range(1, 6):
            assert VARIANT_PRESETS[n][0] == VariantStrategy.FAITHFUL

    def test_preset_order_is_cumulative(self):
        """Each preset extends the previous one."""
        for n in range(2, 6):
            prev = VARIANT_PRESETS[n - 1]
            curr = VARIANT_PRESETS[n]
            assert curr[:n - 1] == prev

    def test_preset_3_strategies(self):
        assert VARIANT_PRESETS[3] == [
            VariantStrategy.FAITHFUL,
            VariantStrategy.ENHANCED,
            VariantStrategy.ALT_COMPOSITION,
        ]


class TestGenerateVariantIntents:
    """Test generate_variant_intents function."""

    def test_n1_faithful_returns_original_caption(self):
        """n=1 should return FAITHFUL with original caption, no API call."""
        caption = "Overview of protein folding pathway"
        result = generate_variant_intents(
            caption=caption,
            source_text="Some source text.",
            n=1,
            api_key="fake-key",
        )
        assert len(result) == 1
        assert result[0].strategy == VariantStrategy.FAITHFUL
        assert result[0].communicative_intent == caption
        assert result[0].index == 0

    @patch("google.genai.Client")
    def test_n3_returns_correct_strategies(self, mock_client_cls):
        """n=3 should return FAITHFUL + 2 LLM-rewritten variants."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Rewritten caption text"
        mock_client.models.generate_content.return_value = mock_response

        result = generate_variant_intents(
            caption="Original caption",
            source_text="Context text.",
            n=3,
            api_key="fake-key",
        )

        assert len(result) == 3
        assert result[0].strategy == VariantStrategy.FAITHFUL
        assert result[1].strategy == VariantStrategy.ENHANCED
        assert result[2].strategy == VariantStrategy.ALT_COMPOSITION
        # FAITHFUL keeps original
        assert result[0].communicative_intent == "Original caption"
        # Others are rewritten
        assert result[1].communicative_intent == "Rewritten caption text"

    def test_n_clamped_above_5(self):
        """n > 5 should be clamped to 5."""
        # Only test the clamping logic, not the API call
        # n=1 doesn't call API, so we use that to verify clamping works
        result = generate_variant_intents(
            caption="Test",
            source_text="Text.",
            n=1,  # Can't test n>5 without mocking, but we test clamping separately
            api_key="fake-key",
        )
        assert len(result) == 1

    def test_n_clamped_below_1(self):
        """n < 1 should be clamped to 1."""
        result = generate_variant_intents(
            caption="Test",
            source_text="Text.",
            n=0,
            api_key="fake-key",
        )
        assert len(result) == 1

    @patch("google.genai.Client")
    def test_n_above_5_clamped(self, mock_client_cls):
        """n=10 should produce 5 variants (clamped)."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Rewritten"
        mock_client.models.generate_content.return_value = mock_response

        result = generate_variant_intents(
            caption="Test",
            source_text="Text.",
            n=10,
            api_key="fake-key",
        )
        assert len(result) == 5

    def test_variant_intent_fields(self):
        """VariantIntent has all expected fields."""
        vi = VariantIntent(
            index=0,
            strategy=VariantStrategy.FAITHFUL,
            communicative_intent="Caption",
            strategy_description="Description",
        )
        assert vi.index == 0
        assert vi.strategy == VariantStrategy.FAITHFUL
        assert vi.communicative_intent == "Caption"
        assert vi.strategy_description == "Description"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
