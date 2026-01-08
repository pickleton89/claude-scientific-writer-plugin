"""Visual Design Skill Utilities.

Deterministic utilities for publication-quality scientific figure design.
These utilities reduce LLM variance by providing code-based lookups and validations.
"""

from .venue_specs import get_venue_specs, normalize_venue_name, VENUE_SPECS, DEFAULT_SPECS
from .chart_selector import recommend_chart_type, CHART_RECOMMENDATIONS
from .palette_selector import select_palette, CATEGORICAL_PALETTES, SEQUENTIAL_PALETTES, DIVERGING_PALETTES
from .accessibility import (
    contrast_ratio,
    check_contrast,
    validate_accessibility,
    hex_to_rgb,
    relative_luminance,
)
from .quality_scorer import (
    calculate_measurable_score,
    calculate_total_score,
    get_subjective_criteria,
)
from .validation import validate_figure_spec
from .template_renderer import render_spec_markdown, render_spec_yaml

__all__ = [
    # Venue specs
    "get_venue_specs",
    "normalize_venue_name",
    "VENUE_SPECS",
    "DEFAULT_SPECS",
    # Chart selection
    "recommend_chart_type",
    "CHART_RECOMMENDATIONS",
    # Palette selection
    "select_palette",
    "CATEGORICAL_PALETTES",
    "SEQUENTIAL_PALETTES",
    "DIVERGING_PALETTES",
    # Accessibility
    "contrast_ratio",
    "check_contrast",
    "validate_accessibility",
    "hex_to_rgb",
    "relative_luminance",
    # Quality scoring
    "calculate_measurable_score",
    "calculate_total_score",
    "get_subjective_criteria",
    # Validation
    "validate_figure_spec",
    # Template rendering
    "render_spec_markdown",
    "render_spec_yaml",
]
