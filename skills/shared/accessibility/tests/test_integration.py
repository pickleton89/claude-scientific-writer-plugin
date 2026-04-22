"""Integration tests for figure-QC utilities (formerly skills/visual-design/utils/).

Tests end-to-end workflows combining utilities from shared/accessibility/,
plotting-libraries/scripts/, and oligon-brand/scripts/ (which were colocated
before the 2026-04-22 visual-design deprecation).
"""

import sys
from pathlib import Path

# Utilities live in three skill homes post-migration:
#   shared/accessibility/ : venue_specs, accessibility, quality_scorer, validation, schema
#   plotting-libraries/scripts/ : chart_selector, palette_selector
#   oligon-brand/scripts/ : template_renderer
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE.parent.parent.parent / "plotting-libraries" / "scripts"))
sys.path.insert(0, str(_HERE.parent.parent.parent / "oligon-brand" / "scripts"))

from venue_specs import get_venue_specs
from chart_selector import recommend_chart_type
from palette_selector import select_palette
from accessibility import validate_accessibility, contrast_ratio
from quality_scorer import calculate_measurable_score
from validation import validate_figure_spec
from template_renderer import render_spec_yaml, render_spec_markdown, render_quick_spec_card
from schema import validate_request


class TestEndToEndWorkflow:
    """Tests for complete design workflow."""

    def test_nature_time_series_workflow(self):
        """Test complete workflow for Nature time series figure."""
        # Step 1: Get venue specifications
        venue_specs = get_venue_specs("nature")
        assert venue_specs["single_col_mm"] == 89

        # Step 2: Get chart recommendation
        chart = recommend_chart_type("time_series", n_groups=3)
        assert "line" in chart["recommended"] or "multi_line" in chart["recommended"]

        # Step 3: Select color palette
        palette = select_palette(data_type="categorical", n_groups=3)
        assert len(palette["colors"]) == 3

        # Step 4: Build specification
        spec = {
            "venue": "nature",
            "dimensions": {
                "width_mm": venue_specs["single_col_mm"],
                "height_mm": 70,
                "column_type": "single",
            },
            "resolution_dpi": 300,
            "file_format": "pdf",
            "typography": {
                "family": "Arial",
                "min_pt": 7,
            },
            "color_palette": {
                "text": "#000000",
                "background": "#FFFFFF",
                "colors": palette["colors"],
            },
            "accessibility": {
                "colorblind_safe": True,
                "min_contrast_ratio": 4.5,
                "redundant_encoding": ["line_style"],
            },
            "chart_recommendation": chart,
            "panel_label_case": venue_specs["panel_label_case"],
        }

        # Step 5: Validate specification
        validation = validate_figure_spec(spec)
        assert validation["valid"], f"Validation failed: {validation['errors']}"

        # Step 6: Check accessibility
        accessibility = validate_accessibility(spec)
        assert accessibility["passed"], f"Accessibility failed: {accessibility['errors']}"

        # Step 7: Calculate quality score
        measurable = calculate_measurable_score(spec, venue_specs)
        assert measurable["measurable_score"] == 4  # Perfect measurable score

        # Step 8: Render outputs
        yaml_output = render_spec_yaml(spec)
        assert "venue: nature" in yaml_output

        markdown_output = render_spec_markdown(spec)
        assert "Nature" in markdown_output or "nature" in markdown_output

    def test_science_comparison_workflow(self):
        """Test workflow for Science comparison figure."""
        venue_specs = get_venue_specs("science")
        _chart = recommend_chart_type("comparison", n_categories=4)  # noqa: F841
        palette = select_palette(n_groups=4)

        spec = {
            "venue": "science",
            "dimensions": {
                "width_mm": venue_specs["single_col_mm"],
                "column_type": "single",
            },
            "resolution_dpi": 300,
            "file_format": "pdf",
            "typography": {"min_pt": 7},
            "color_palette": {
                "text": "#000000",
                "background": "#FFFFFF",
                "colors": palette["colors"],
            },
            "accessibility": {
                "colorblind_safe": True,
                "min_contrast_ratio": 4.5,
                "redundant_encoding": ["shape"],
            },
            "panel_label_case": "upper",
        }

        validation = validate_figure_spec(spec)
        assert validation["valid"]
        assert validation["venue_canonical"] == "science"

    def test_diverging_heatmap_workflow(self):
        """Test workflow for diverging data heatmap."""
        _chart = recommend_chart_type("relationship_many_var")  # noqa: F841
        palette = select_palette(data_type="sequential", is_diverging=True)

        # Diverging flag should override to diverging palette
        assert palette["palette_type"] == "diverging"

        spec = {
            "venue": "cell",
            "resolution_dpi": 300,
            "file_format": "pdf",
            "typography": {"min_pt": 7},
            "color_palette": {
                "name": palette["palette_name"],
                "type": "diverging",
                "text": "#000000",
                "background": "#FFFFFF",
            },
            "accessibility": {
                "colorblind_safe": True,
                "min_contrast_ratio": 4.5,
            },
        }

        validation = validate_figure_spec(spec)
        assert validation["valid"]


class TestRequestValidation:
    """Tests for input request validation."""

    def test_valid_request(self):
        """Valid request should pass validation."""
        request = {
            "venue": "nature",
            "audience": "journal",
            "figure_type": "data_plot",
            "data_characteristics": {
                "comparison_type": "time_series",
                "n_groups": 3,
            },
        }
        result = validate_request(request)
        assert result["valid"]

    def test_missing_required_fields(self):
        """Missing required fields should fail."""
        request = {"venue": "nature"}  # Missing audience and figure_type
        result = validate_request(request)
        assert not result["valid"]
        assert len(result["errors"]) == 2

    def test_invalid_audience(self):
        """Invalid audience value should fail."""
        request = {
            "venue": "nature",
            "audience": "invalid_audience",
            "figure_type": "data_plot",
        }
        result = validate_request(request)
        assert not result["valid"]

    def test_invalid_figure_type(self):
        """Invalid figure type should fail."""
        request = {
            "venue": "nature",
            "audience": "journal",
            "figure_type": "invalid_type",
        }
        result = validate_request(request)
        assert not result["valid"]


class TestOutputConsistency:
    """Tests for output format consistency."""

    def test_yaml_output_parseable(self):
        """YAML output should be valid YAML structure."""
        spec = {
            "venue": "nature",
            "dimensions": {"width_mm": 89},
            "resolution_dpi": 300,
            "color_palette": {"colors": ["#E69F00", "#56B4E9"]},
            "typography": {"family": "Arial"},
        }
        yaml_output = render_spec_yaml(spec)

        # Check structure
        assert "figure_spec:" in yaml_output
        assert "venue:" in yaml_output
        assert "dimensions:" in yaml_output

    def test_markdown_output_has_sections(self):
        """Markdown output should have expected sections."""
        spec = {
            "venue": "nature",
            "dimensions": {"width_mm": 89},
            "resolution_dpi": 300,
            "color_palette": {"colors": ["#E69F00"]},
            "typography": {"family": "Arial"},
        }
        markdown_output = render_spec_markdown(spec)

        assert "# Figure Specification" in markdown_output
        assert "## Dimensions" in markdown_output

    def test_quick_spec_card_compact(self):
        """Quick spec card should be compact."""
        spec = {
            "venue": "nature",
            "dimensions": {"width_mm": 89, "height_mm": 70, "column_type": "single"},
            "resolution_dpi": 300,
            "file_format": "pdf",
            "typography": {"family": "Arial", "min_pt": 7},
            "color_palette": {"name": "okabe_ito"},
            "panel_label_case": "lower",
        }
        card = render_quick_spec_card(spec)

        # Should be compact (less than 20 lines)
        lines = card.strip().split("\n")
        assert len(lines) < 20

        # Should include key info
        assert "VENUE" in card
        assert "DPI" in card


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self):
        """Same inputs should always produce same outputs."""
        for _ in range(3):
            venue1 = get_venue_specs("nature")
            venue2 = get_venue_specs("nature")
            assert venue1 == venue2

            chart1 = recommend_chart_type("time_series", n_groups=2)
            chart2 = recommend_chart_type("time_series", n_groups=2)
            assert chart1 == chart2

            palette1 = select_palette(n_groups=5)
            palette2 = select_palette(n_groups=5)
            assert palette1 == palette2

    def test_contrast_calculation_deterministic(self):
        """Contrast calculations should be deterministic."""
        for _ in range(3):
            ratio1 = contrast_ratio("#FFFFFF", "#000000")
            ratio2 = contrast_ratio("#FFFFFF", "#000000")
            assert ratio1 == ratio2

    def test_validation_deterministic(self):
        """Validation results should be deterministic."""
        spec = {
            "venue": "nature",
            "dimensions": {"width_mm": 89},
            "resolution_dpi": 300,
            "typography": {"min_pt": 7},
            "color_palette": {"text": "#000000", "background": "#FFFFFF"},
            "accessibility": {"colorblind_safe": True, "min_contrast_ratio": 4.5},
        }

        results = [validate_figure_spec(spec) for _ in range(3)]
        assert all(r == results[0] for r in results)
