"""
Utility modules for research-posters validation.

Provides deterministic validation utilities for research poster quality checks:
- brand_colors: Color palette, contrast ratios, colorblind simulation
- dimensions: Poster size constants and lookups
- schemas: Dataclasses for structured validation I/O
"""

from .brand_colors import (
    OLIGON_COLORS,
    calculate_contrast_ratio,
    hex_to_rgb,
    rgb_to_hex,
    simulate_deuteranopia,
    simulate_protanopia,
    check_wcag_compliance,
)
from .dimensions import (
    POSTER_SIZES,
    PosterSize,
    get_poster_size,
    validate_dimensions,
    pts_to_inches,
    inches_to_pts,
)
from .schemas import (
    ValidationResult,
    WordCountResult,
    ContrastCheckResult,
    ImageCheckResult,
    FontCheckResult,
    QualityReport,
    PosterSpec,
)

__all__ = [
    # brand_colors
    "OLIGON_COLORS",
    "calculate_contrast_ratio",
    "hex_to_rgb",
    "rgb_to_hex",
    "simulate_deuteranopia",
    "simulate_protanopia",
    "check_wcag_compliance",
    # dimensions
    "POSTER_SIZES",
    "PosterSize",
    "get_poster_size",
    "validate_dimensions",
    "pts_to_inches",
    "inches_to_pts",
    # schemas
    "ValidationResult",
    "WordCountResult",
    "ContrastCheckResult",
    "ImageCheckResult",
    "FontCheckResult",
    "QualityReport",
    "PosterSpec",
]
