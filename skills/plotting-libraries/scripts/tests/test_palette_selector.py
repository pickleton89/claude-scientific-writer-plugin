"""Tests for palette_selector module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from palette_selector import (
    select_palette,
    get_palette_colors,
    list_palettes,
    CATEGORICAL_PALETTES,
    SEQUENTIAL_PALETTES,
    DIVERGING_PALETTES,
    BINARY_PALETTES,
)


class TestSelectPalette:
    """Tests for palette selection."""

    def test_binary_for_two_groups(self):
        """Two groups should get binary palette."""
        result = select_palette(n_groups=2)
        assert result["palette_type"] == "binary"
        assert len(result["colors"]) == 2

    def test_categorical_for_few_groups(self):
        """Few groups should get categorical palette."""
        result = select_palette(data_type="categorical", n_groups=5)
        assert result["palette_type"] == "categorical"
        assert len(result["colors"]) == 5

    def test_sequential_for_continuous_data(self):
        """Sequential data should get sequential palette."""
        result = select_palette(data_type="sequential")
        assert result["palette_type"] == "sequential"
        assert "matplotlib_name" in result

    def test_diverging_for_centered_data(self):
        """Diverging data should get diverging palette."""
        result = select_palette(data_type="diverging")
        assert result["palette_type"] == "diverging"

    def test_diverging_flag_overrides_sequential(self):
        """is_diverging=True should override sequential to diverging."""
        result = select_palette(data_type="sequential", is_diverging=True)
        assert result["palette_type"] == "diverging"

    def test_specific_palette_override(self):
        """Specifying palette name should override auto-selection."""
        result = select_palette(palette_name="tableau10")
        assert result["palette_name"] == "tableau10"

    def test_warning_for_many_categories(self):
        """Many categories should produce warning."""
        result = select_palette(n_groups=12)
        assert "warning" in result

    def test_all_returned_palettes_colorblind_safe(self):
        """Default palettes should be colorblind-safe."""
        for n in [2, 5, 8]:
            result = select_palette(n_groups=n)
            assert result.get("colorblind_safe", True)

    def test_categorical_colors_truncated_to_n_groups(self):
        """Categorical palettes should return exactly n_groups colors."""
        for n in [3, 5, 7]:
            result = select_palette(data_type="categorical", n_groups=n)
            if "colors" in result:
                assert len(result["colors"]) == n


class TestGetPaletteColors:
    """Tests for palette color retrieval."""

    def test_okabe_ito_returns_8_colors(self):
        """Okabe-Ito should have 8 colors."""
        colors = get_palette_colors("okabe_ito")
        assert len(colors) == 8

    def test_truncate_to_n_colors(self):
        """Should truncate to requested number of colors."""
        colors = get_palette_colors("okabe_ito", n_colors=3)
        assert len(colors) == 3

    def test_binary_palettes_return_two_colors(self):
        """Binary palettes should return 2 colors."""
        colors = get_palette_colors("blue_orange")
        assert len(colors) == 2

    def test_colors_are_valid_hex(self):
        """All colors should be valid hex codes."""
        colors = get_palette_colors("okabe_ito")
        for color in colors:
            assert color.startswith("#")
            assert len(color) == 7

    def test_unknown_palette_raises_error(self):
        """Unknown palette should raise ValueError."""
        with pytest.raises(ValueError):
            get_palette_colors("nonexistent_palette")

    def test_sequential_palette_raises_error(self):
        """Sequential palettes don't have discrete colors."""
        with pytest.raises(ValueError):
            get_palette_colors("viridis")


class TestListPalettes:
    """Tests for palette listing."""

    def test_list_all_palettes(self):
        """Should list all available palettes."""
        palettes = list_palettes()
        assert len(palettes) > 0
        assert "okabe_ito" in palettes
        assert "viridis" in palettes

    def test_filter_by_type(self):
        """Should filter by palette type."""
        categorical = list_palettes("categorical")
        sequential = list_palettes("sequential")

        assert "okabe_ito" in categorical
        assert "viridis" in sequential
        assert "okabe_ito" not in sequential
        assert "viridis" not in categorical

    def test_binary_filter(self):
        """Should list binary palettes."""
        binary = list_palettes("binary")
        assert "blue_orange" in binary


class TestPaletteDataIntegrity:
    """Tests for palette data integrity."""

    def test_categorical_palettes_have_required_fields(self):
        """Categorical palettes should have required fields."""
        for name, palette in CATEGORICAL_PALETTES.items():
            assert "colors" in palette, f"{name} missing colors"
            assert "max_categories" in palette, f"{name} missing max_categories"
            assert "colorblind_safe" in palette, f"{name} missing colorblind_safe"

    def test_categorical_colors_are_valid_hex(self):
        """All categorical colors should be valid hex."""
        for name, palette in CATEGORICAL_PALETTES.items():
            for color in palette["colors"]:
                assert color.startswith("#"), f"{name} has invalid color: {color}"
                assert len(color) == 7, f"{name} has invalid color length: {color}"

    def test_categorical_max_matches_color_count(self):
        """Max categories should match actual color count."""
        for name, palette in CATEGORICAL_PALETTES.items():
            assert palette["max_categories"] <= len(palette["colors"]), \
                f"{name} max_categories exceeds color count"

    def test_sequential_palettes_have_matplotlib_name(self):
        """Sequential palettes should have matplotlib names."""
        for name, palette in SEQUENTIAL_PALETTES.items():
            assert "matplotlib_name" in palette, f"{name} missing matplotlib_name"

    def test_diverging_palettes_have_matplotlib_name(self):
        """Diverging palettes should have matplotlib names."""
        for name, palette in DIVERGING_PALETTES.items():
            assert "matplotlib_name" in palette, f"{name} missing matplotlib_name"

    def test_binary_palettes_have_exactly_two_colors(self):
        """Binary palettes should have exactly 2 colors."""
        for name, palette in BINARY_PALETTES.items():
            assert len(palette["colors"]) == 2, \
                f"{name} should have exactly 2 colors"

    def test_all_palettes_marked_colorblind_safe(self):
        """All provided palettes should be colorblind-safe."""
        for palettes in [CATEGORICAL_PALETTES, BINARY_PALETTES]:
            for name, palette in palettes.items():
                assert palette.get("colorblind_safe", False), \
                    f"{name} should be colorblind-safe"
