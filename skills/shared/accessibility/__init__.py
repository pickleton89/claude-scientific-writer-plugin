"""
Shared figure-quality-control utilities.

Hosts accessibility/WCAG helpers, figure-specification validation, quality
scoring, schema types, and venue-specific publication specs. Moved from
`skills/visual-design/utils/` during the Apr 2026 visual-design deprecation.

Modules
-------
venue_specs
    Journal dimension/DPI/format lookups and venue-name normalization
accessibility
    WCAG contrast ratios, colorblind simulation, luminance
validation
    Figure-specification validation against venue + accessibility requirements
quality_scorer
    Measurable/subjective quality scoring for figures
schema
    Shared dataclass/TypedDict schemas for figure specifications
"""

try:
    from .venue_specs import (
        get_venue_specs,
        normalize_venue_name,
        VENUE_SPECS,
        DEFAULT_SPECS,
    )
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
    from .schema import validate_request
except ImportError:
    from venue_specs import (  # noqa: F401
        get_venue_specs,
        normalize_venue_name,
        VENUE_SPECS,
        DEFAULT_SPECS,
    )
    from accessibility import (  # noqa: F401
        contrast_ratio,
        check_contrast,
        validate_accessibility,
        hex_to_rgb,
        relative_luminance,
    )
    from quality_scorer import (  # noqa: F401
        calculate_measurable_score,
        calculate_total_score,
        get_subjective_criteria,
    )
    from validation import validate_figure_spec  # noqa: F401
    from schema import validate_request  # noqa: F401

__all__ = [
    "get_venue_specs",
    "normalize_venue_name",
    "VENUE_SPECS",
    "DEFAULT_SPECS",
    "contrast_ratio",
    "check_contrast",
    "validate_accessibility",
    "hex_to_rgb",
    "relative_luminance",
    "calculate_measurable_score",
    "calculate_total_score",
    "get_subjective_criteria",
    "validate_figure_spec",
    "validate_request",
]
