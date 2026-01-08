"""Deterministic utilities for scientific schematic generation.

This package provides validation, type selection, and configuration
utilities that reduce output variance through code-based decision making.
"""

from .complexity_limits import (
    COMPLEXITY_LIMITS,
    ComplexityLimits,
    check_complexity,
    estimate_nodes_from_prompt,
)
from .brand_colors import (
    ColorPalette,
    PALETTES,
    get_palette,
    format_color_guidance,
    inject_colors_into_prompt,
)
from .schemas import (
    DocType,
    GenerationResults,
    IterationResult,
    SchematicPrompt,
    ScoreTrend,
    hash_prompt,
    validate_results_dict,
)

__all__ = [
    # Complexity limits
    "COMPLEXITY_LIMITS",
    "ComplexityLimits",
    "check_complexity",
    "estimate_nodes_from_prompt",
    # Brand colors
    "ColorPalette",
    "PALETTES",
    "get_palette",
    "format_color_guidance",
    "inject_colors_into_prompt",
    # Schemas
    "DocType",
    "GenerationResults",
    "IterationResult",
    "SchematicPrompt",
    "ScoreTrend",
    "hash_prompt",
    "validate_results_dict",
]
