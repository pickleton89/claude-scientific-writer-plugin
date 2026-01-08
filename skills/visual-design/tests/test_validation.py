"""Tests for validation module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validation import (
    validate_figure_spec,
    validate_color_palette,
    get_validation_checklist,
)


class TestValidateFigureSpec:
    """Tests for figure specification validation."""

    def test_valid_nature_spec(self):
        """Valid Nature figure spec should pass."""
        spec = {
            "venue": "nature",
            "dimensions": {
                "width_mm": 89,
                "height_mm": 100,
                "column_type": "single",
            },
            "resolution_dpi": 300,
            "file_format": "pdf",
            "typography": {"min_pt": 7, "family": "Arial"},
            "color_palette": {
                "text": "#000000",
                "background": "#FFFFFF",
            },
            "accessibility": {
                "colorblind_safe": True,
                "min_contrast_ratio": 4.5,
                "redundant_encoding": ["shape"],
            },
        }
        result = validate_figure_spec(spec)
        assert result["valid"]
        assert len(result["errors"]) == 0

    def test_width_exceeds_double_column(self):
        """Width exceeding double column should error."""
        spec = {
            "venue": "nature",
            "dimensions": {"width_mm": 200},  # Nature max is 183mm
        }
        result = validate_figure_spec(spec)
        assert not result["valid"]
        assert any("width" in e.lower() for e in result["errors"])

    def test_width_exceeds_single_warns_about_double(self):
        """Width exceeding single but not double should warn."""
        spec = {
            "venue": "nature",
            "dimensions": {"width_mm": 120, "column_type": "single"},
        }
        result = validate_figure_spec(spec)
        # Should be valid but with warning about double column
        assert any("double" in w.lower() for w in result["warnings"])

    def test_height_exceeds_max(self):
        """Height exceeding max should error."""
        spec = {
            "venue": "nature",
            "dimensions": {"height_mm": 300},  # Nature max is 247mm
        }
        result = validate_figure_spec(spec)
        assert any("height" in e.lower() for e in result["errors"])

    def test_low_dpi_error(self):
        """DPI below minimum should error."""
        spec = {
            "venue": "nature",
            "resolution_dpi": 150,  # Nature requires 300
        }
        result = validate_figure_spec(spec)
        assert any("dpi" in e.lower() or "resolution" in e.lower() for e in result["errors"])

    def test_non_preferred_format_warns(self):
        """Non-preferred format should warn."""
        spec = {
            "venue": "nature",
            "file_format": "png",  # Nature prefers pdf, eps, tiff
        }
        result = validate_figure_spec(spec)
        assert any("format" in w.lower() for w in result["warnings"])

    def test_small_font_error(self):
        """Font below minimum should error."""
        spec = {
            "venue": "nature",
            "typography": {"min_pt": 5},
        }
        result = validate_figure_spec(spec)
        assert any("font" in e.lower() for e in result["errors"])

    def test_wrong_panel_case_warns(self):
        """Wrong panel label case should warn."""
        spec = {
            "venue": "nature",  # Nature uses lowercase
            "panel_label_case": "upper",
        }
        result = validate_figure_spec(spec)
        assert any("panel" in w.lower() for w in result["warnings"])

    def test_cmyk_warns(self):
        """CMYK color mode should warn."""
        spec = {
            "color_mode": "cmyk",
        }
        result = validate_figure_spec(spec)
        assert any("cmyk" in w.lower() for w in result["warnings"])

    def test_venue_from_spec(self):
        """Should use venue from spec if not provided."""
        spec = {"venue": "science"}
        result = validate_figure_spec(spec)
        assert result["venue"] == "science"

    def test_venue_override(self):
        """Provided venue should override spec venue."""
        spec = {"venue": "science"}
        result = validate_figure_spec(spec, venue="nature")
        assert result["venue"] == "nature"

    def test_returns_canonical_venue(self):
        """Should return canonical venue name."""
        spec = {}
        result = validate_figure_spec(spec, venue="Nature Communications")
        assert result["venue_canonical"] == "nature"

    def test_returns_checks_performed(self):
        """Should list all checks performed."""
        spec = {"venue": "nature"}
        result = validate_figure_spec(spec)
        assert "checks_performed" in result
        assert len(result["checks_performed"]) > 0
        assert "dimensions" in result["checks_performed"]
        assert "accessibility" in result["checks_performed"]


class TestValidateColorPalette:
    """Tests for color palette validation."""

    def test_good_palette_valid(self):
        """Good palette should validate."""
        colors = ["#E69F00", "#56B4E9", "#009E73"]
        result = validate_color_palette(colors)
        assert result["valid"]

    def test_too_many_colors_error(self):
        """More than 10 colors should error."""
        colors = [f"#{i:02x}0000" for i in range(12)]
        result = validate_color_palette(colors)
        assert not result["valid"]

    def test_many_colors_warning(self):
        """8-10 colors should warn."""
        colors = ["#000000"] * 9
        result = validate_color_palette(colors)
        assert any("exceed" in w.lower() for w in result["warnings"])

    def test_low_contrast_warning(self):
        """Low contrast colors should warn."""
        colors = ["#EEEEEE", "#DDDDDD"]  # Very light
        result = validate_color_palette(colors, background="#FFFFFF")
        assert any("contrast" in w.lower() for w in result["warnings"])

    def test_duplicate_colors_warning(self):
        """Duplicate colors should warn."""
        colors = ["#FF0000", "#FF0000", "#00FF00"]
        result = validate_color_palette(colors)
        assert any("duplicate" in w.lower() for w in result["warnings"])


class TestGetValidationChecklist:
    """Tests for validation checklist generation."""

    def test_returns_checklist(self):
        """Should return list of checklist items."""
        checklist = get_validation_checklist("nature")
        assert isinstance(checklist, list)
        assert len(checklist) > 0

    def test_checklist_has_categories(self):
        """Checklist should have category headers."""
        checklist = get_validation_checklist("nature")
        categories = [item["category"] for item in checklist]
        assert "Dimensions" in categories
        assert "Accessibility" in categories

    def test_checklist_has_items(self):
        """Each category should have items."""
        checklist = get_validation_checklist("nature")
        for category in checklist:
            assert "items" in category
            assert len(category["items"]) > 0

    def test_checklist_includes_venue_specific_values(self):
        """Checklist should include venue-specific values."""
        checklist = get_validation_checklist("nature")
        # Find dimensions category
        dims = next(c for c in checklist if c["category"] == "Dimensions")
        # Should mention 89mm (Nature single column)
        assert any("89" in item for item in dims["items"])
