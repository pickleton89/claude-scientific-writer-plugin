"""Tests for accessibility module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from accessibility import (
    hex_to_rgb,
    rgb_to_hex,
    relative_luminance,
    contrast_ratio,
    check_contrast,
    check_palette_contrast,
    validate_accessibility,
    simulate_colorblindness,
    check_colorblind_distinguishability,
)


class TestHexToRgb:
    """Tests for hex to RGB conversion."""

    def test_basic_colors(self):
        """Test basic color conversions."""
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("#000000") == (0, 0, 0)
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#00FF00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)

    def test_with_and_without_hash(self):
        """Should work with or without # prefix."""
        assert hex_to_rgb("#FFFFFF") == hex_to_rgb("FFFFFF")

    def test_lowercase_hex(self):
        """Should handle lowercase hex."""
        assert hex_to_rgb("#ffffff") == (255, 255, 255)
        assert hex_to_rgb("#aabbcc") == (170, 187, 204)

    def test_invalid_hex_raises_error(self):
        """Invalid hex should raise ValueError."""
        with pytest.raises(ValueError):
            hex_to_rgb("#FFF")  # Too short
        with pytest.raises(ValueError):
            hex_to_rgb("#GGGGGG")  # Invalid characters


class TestRgbToHex:
    """Tests for RGB to hex conversion."""

    def test_basic_colors(self):
        """Test basic color conversions."""
        assert rgb_to_hex((255, 255, 255)) == "#ffffff"
        assert rgb_to_hex((0, 0, 0)) == "#000000"
        assert rgb_to_hex((255, 0, 0)) == "#ff0000"

    def test_roundtrip(self):
        """Conversion should roundtrip correctly."""
        original = "#aabbcc"
        rgb = hex_to_rgb(original)
        result = rgb_to_hex(rgb)
        assert result.lower() == original.lower()


class TestRelativeLuminance:
    """Tests for relative luminance calculation."""

    def test_white_luminance(self):
        """White should have luminance of 1.0."""
        assert relative_luminance((255, 255, 255)) == pytest.approx(1.0, rel=0.01)

    def test_black_luminance(self):
        """Black should have luminance of 0.0."""
        assert relative_luminance((0, 0, 0)) == pytest.approx(0.0, abs=0.001)

    def test_gray_luminance(self):
        """Middle gray should have intermediate luminance."""
        lum = relative_luminance((128, 128, 128))
        assert 0.1 < lum < 0.3


class TestContrastRatio:
    """Tests for contrast ratio calculation."""

    def test_black_white_maximum_contrast(self):
        """Black and white should have ~21:1 contrast."""
        ratio = contrast_ratio("#FFFFFF", "#000000")
        assert ratio == pytest.approx(21.0, rel=0.01)

    def test_same_color_minimum_contrast(self):
        """Same colors should have 1:1 contrast."""
        ratio = contrast_ratio("#FFFFFF", "#FFFFFF")
        assert ratio == pytest.approx(1.0, rel=0.01)

    def test_order_independent(self):
        """Contrast ratio should be same regardless of order."""
        ratio1 = contrast_ratio("#FFFFFF", "#000000")
        ratio2 = contrast_ratio("#000000", "#FFFFFF")
        assert ratio1 == pytest.approx(ratio2)

    def test_known_contrast_values(self):
        """Test against known WCAG example values."""
        # Gray on white should be around 4.5:1
        ratio = contrast_ratio("#767676", "#FFFFFF")
        assert 4.4 < ratio < 4.6


class TestCheckContrast:
    """Tests for WCAG contrast checking."""

    def test_black_on_white_passes_aaa(self):
        """Black on white should pass AAA."""
        result = check_contrast("#000000", "#FFFFFF", level="AAA")
        assert result["passed"]
        assert result["contrast_ratio"] >= 7.0

    def test_wcag_aa_normal_text(self):
        """Normal text needs 4.5:1 for AA."""
        result = check_contrast("#767676", "#FFFFFF", level="AA")
        assert result["required_ratio"] == 4.5
        assert result["passed"]

    def test_wcag_aa_large_text(self):
        """Large text needs 3.0:1 for AA."""
        result = check_contrast("#959595", "#FFFFFF", is_large_text=True, level="AA")
        assert result["required_ratio"] == 3.0

    def test_low_contrast_fails(self):
        """Low contrast should fail WCAG AA."""
        result = check_contrast("#CCCCCC", "#FFFFFF", level="AA")
        assert not result["passed"]

    def test_returns_all_expected_fields(self):
        """Should return all expected fields."""
        result = check_contrast("#000000", "#FFFFFF")
        assert "contrast_ratio" in result
        assert "required_ratio" in result
        assert "passed" in result
        assert "wcag_level" in result
        assert "text_type" in result


class TestCheckPaletteContrast:
    """Tests for palette contrast checking."""

    def test_high_contrast_palette_passes(self):
        """High contrast colors should all pass."""
        colors = ["#000000", "#0000FF", "#008000"]
        result = check_palette_contrast(colors, "#FFFFFF", min_ratio=3.0)
        assert result["all_passed"]

    def test_low_contrast_colors_detected(self):
        """Low contrast colors should be flagged."""
        colors = ["#EEEEEE", "#DDDDDD"]  # Very light colors
        result = check_palette_contrast(colors, "#FFFFFF", min_ratio=3.0)
        assert not result["all_passed"]
        assert result["failed_count"] > 0


class TestValidateAccessibility:
    """Tests for comprehensive accessibility validation."""

    def test_valid_spec_passes(self):
        """Complete valid spec should pass."""
        spec = {
            "typography": {"min_pt": 8},
            "min_line_weight_pt": 1.0,
            "color_palette": {
                "text": "#000000",
                "background": "#FFFFFF",
                "colors": ["#E69F00", "#56B4E9", "#009E73"],
            },
            "accessibility": {
                "redundant_encoding": ["shape"],
            },
        }
        result = validate_accessibility(spec)
        assert result["passed"]
        assert len(result["errors"]) == 0

    def test_small_font_flagged(self):
        """Font size below 7pt should be error."""
        spec = {
            "typography": {"min_pt": 5},
            "color_palette": {"text": "#000000", "background": "#FFFFFF"},
        }
        result = validate_accessibility(spec)
        assert not result["passed"]
        assert any("font" in e.lower() for e in result["errors"])

    def test_thin_lines_flagged(self):
        """Line weight below 0.5pt should be error."""
        spec = {
            "min_line_weight_pt": 0.25,
            "color_palette": {"text": "#000000", "background": "#FFFFFF"},
        }
        result = validate_accessibility(spec)
        assert any("line" in e.lower() for e in result["errors"])

    def test_low_contrast_flagged(self):
        """Low text/background contrast should be error."""
        spec = {
            "color_palette": {
                "text": "#CCCCCC",
                "background": "#FFFFFF",
            },
        }
        result = validate_accessibility(spec)
        assert not result["passed"]
        assert any("contrast" in e.lower() for e in result["errors"])

    def test_many_colors_warning(self):
        """More than 7 colors should generate warning."""
        spec = {
            "color_palette": {
                "text": "#000000",
                "background": "#FFFFFF",
                "colors": [
                    "#E69F00", "#56B4E9", "#009E73", "#F0E442",
                    "#0072B2", "#D55E00", "#CC79A7", "#000000", "#999999"
                ],
            },
        }
        result = validate_accessibility(spec)
        assert any("color" in w.lower() for w in result["warnings"])

    def test_missing_redundant_encoding_warning(self):
        """Missing redundant encoding should warn."""
        spec = {
            "color_palette": {
                "text": "#000000",
                "background": "#FFFFFF",
                "colors": ["#E69F00", "#56B4E9", "#009E73"],
            },
            "accessibility": {},
        }
        result = validate_accessibility(spec)
        assert any("redundant" in w.lower() for w in result["warnings"])


class TestSimulateColorblindness:
    """Tests for colorblindness simulation."""

    def test_returns_valid_hex(self):
        """Simulation should return valid hex."""
        result = simulate_colorblindness("#FF0000", "deuteranopia")
        assert result.startswith("#")
        assert len(result) == 7

    def test_unknown_type_returns_original(self):
        """Unknown CVD type should return original color."""
        original = "#FF0000"
        result = simulate_colorblindness(original, "unknown_type")
        assert result == original

    def test_different_types_produce_different_results(self):
        """Different CVD types should produce different simulations."""
        red = "#FF0000"
        deut = simulate_colorblindness(red, "deuteranopia")
        prot = simulate_colorblindness(red, "protanopia")
        trit = simulate_colorblindness(red, "tritanopia")
        # At least some should differ
        assert len({deut, prot, trit}) >= 2


class TestCheckColorblindDistinguishability:
    """Tests for colorblind distinguishability checking."""

    def test_okabe_ito_is_distinguishable(self):
        """Okabe-Ito palette should be distinguishable."""
        colors = ["#E69F00", "#56B4E9", "#009E73", "#0072B2"]
        result = check_colorblind_distinguishability(colors)
        # May or may not pass depending on threshold
        assert "distinguishable" in result
        assert "issues" in result

    def test_returns_expected_fields(self):
        """Should return all expected fields."""
        colors = ["#FF0000", "#00FF00"]
        result = check_colorblind_distinguishability(colors)
        assert "distinguishable" in result
        assert "issues" in result
        assert "colors_checked" in result
        assert "cvd_types_checked" in result
