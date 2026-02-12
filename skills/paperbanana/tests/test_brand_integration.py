"""Tests for brand_integration: Oligon brand injection for PaperBanana."""

from __future__ import annotations

import sys
from pathlib import Path

# Add utils to path
sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "scripts")
)

from utils.brand_integration import (
    OLIGON_BRAND,
    create_oligon_style_config,
    get_oligon_guidelines,
    get_palette,
)


class TestOligonGuidelines:
    """Test Oligon guidelines text generation."""

    def test_contains_brand_colors(self):
        text = get_oligon_guidelines()
        assert "#2DB2E8" in text
        assert "#E8622D" in text
        assert "#222222" in text
        assert "#666666" in text
        assert "#FFFFFF" in text

    def test_contains_brand_name(self):
        text = get_oligon_guidelines()
        assert "Oligon" in text

    def test_contains_style_guidance(self):
        text = get_oligon_guidelines()
        assert "contrast ratio" in text.lower()
        assert "minimalist" in text.lower()


class TestStyleConfig:
    """Test Oligon style config dictionary."""

    def test_has_brand_section(self):
        config = create_oligon_style_config()
        assert "brand" in config
        assert "name" in config["brand"]

    def test_has_color_palette(self):
        config = create_oligon_style_config()
        assert "color_palette" in config
        palette = config["color_palette"]
        assert palette["primary"] == "#2DB2E8"
        assert palette["contrast"] == "#E8622D"
        assert palette["text"] == "#222222"

    def test_has_style_rules(self):
        config = create_oligon_style_config()
        assert "style_rules" in config
        assert len(config["style_rules"]) > 0

    def test_alternative_palette(self):
        config = create_oligon_style_config("okabe-ito")
        assert config["color_palette"]["primary"] == "#0072B2"


class TestPaletteReuse:
    """Test that palette imports from scientific-schematics work."""

    def test_oligon_brand_available(self):
        assert OLIGON_BRAND.primary == "#2DB2E8"
        assert OLIGON_BRAND.name == "Oligon Scientific"

    def test_get_palette_works(self):
        palette = get_palette("oligon")
        assert palette.primary == "#2DB2E8"

    def test_colorblind_palette_available(self):
        palette = get_palette("okabe-ito")
        assert palette.primary == "#0072B2"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
