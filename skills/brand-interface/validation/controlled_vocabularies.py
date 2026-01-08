"""
Controlled Vocabularies for Brand Skills

Defines enums and valid values for brand token fields to ensure
consistent, deterministic behavior across brand implementations.

Usage:
    from brand_interface.validation.controlled_vocabularies import (
        BrandType,
        ColorRole,
        CycleName,
        validate_role,
    )
"""

from enum import Enum
from typing import Set


# =============================================================================
# BRAND TYPE
# =============================================================================

class BrandType(str, Enum):
    """
    Type of brand skill.

    Used in SKILL.md frontmatter: brand-type: organizational
    """
    ORGANIZATIONAL = "organizational"  # Company/organization brand
    PERSONAL = "personal"              # Individual researcher's style
    INSTITUTIONAL = "institutional"    # University/institute brand
    JOURNAL = "journal"                # Journal-specific styling
    GENERIC = "generic"                # General-purpose/no affiliation


# =============================================================================
# COLOR ROLES
# =============================================================================

class ColorRole(str, Enum):
    """
    Semantic roles for colors in brand tokens.

    Replaces free-text 'role' descriptions with standardized values.
    """
    # Primary roles
    PRIMARY_HIGHLIGHT = "primary-highlight"       # Main emphasis color
    SECONDARY_HIGHLIGHT = "secondary-highlight"   # Secondary emphasis

    # Data representation
    DATA_PRIMARY = "data-primary"                 # Primary data series
    DATA_SECONDARY = "data-secondary"             # Secondary data series
    DATA_TERTIARY = "data-tertiary"               # Tertiary data series
    DATA_CONTROL = "data-control"                 # Control/baseline data
    DATA_TREATMENT = "data-treatment"             # Treatment/experimental data

    # Directional/opposing
    DIRECTION_UP = "direction-up"                 # Upregulated, positive, increase
    DIRECTION_DOWN = "direction-down"             # Downregulated, negative, decrease
    DIRECTION_NEUTRAL = "direction-neutral"       # Unchanged, neutral

    # Significance
    SIGNIFICANT = "significant"                   # Statistically significant
    NOT_SIGNIFICANT = "not-significant"           # Not significant

    # Heatmap extremes
    HEATMAP_POSITIVE = "heatmap-positive"         # Positive extreme
    HEATMAP_NEGATIVE = "heatmap-negative"         # Negative extreme
    HEATMAP_CENTER = "heatmap-center"             # Center/zero value

    # Structure
    BACKGROUND = "background"                     # Figure/panel background
    AXES = "axes"                                 # Axis lines, ticks
    TEXT = "text"                                 # Labels, titles, legends
    GRIDLINES = "gridlines"                       # Grid lines (if used)
    ANNOTATIONS = "annotations"                   # Annotation text/lines

    # Categorical extensions
    CATEGORY_1 = "category-1"
    CATEGORY_2 = "category-2"
    CATEGORY_3 = "category-3"
    CATEGORY_4 = "category-4"


# Mapping from legacy free-text roles to standardized roles
ROLE_ALIASES: dict[str, ColorRole] = {
    # Primary/highlight variations
    "hero highlight": ColorRole.PRIMARY_HIGHLIGHT,
    "primary data of interest": ColorRole.PRIMARY_HIGHLIGHT,
    "treatment groups": ColorRole.DATA_TREATMENT,
    "focal points": ColorRole.PRIMARY_HIGHLIGHT,
    "emphasis": ColorRole.PRIMARY_HIGHLIGHT,

    # Opposition/contrast
    "opposition to brand blue": ColorRole.DIRECTION_UP,
    "up vs down": ColorRole.DIRECTION_UP,
    "mutant vs wildtype": ColorRole.DATA_TREATMENT,

    # Neutrals
    "primary default data": ColorRole.DATA_PRIMARY,
    "control groups": ColorRole.DATA_CONTROL,
    "baselines": ColorRole.DATA_CONTROL,
    "secondary data": ColorRole.DATA_SECONDARY,
    "secondary data lines": ColorRole.DATA_SECONDARY,
    "tertiary data": ColorRole.DATA_TERTIARY,

    # Annotations
    "annotations": ColorRole.ANNOTATIONS,
    "gridlines": ColorRole.GRIDLINES,
    "de-emphasized": ColorRole.ANNOTATIONS,

    # Structure
    "backgrounds only": ColorRole.BACKGROUND,
    "axes": ColorRole.AXES,
    "ticks": ColorRole.AXES,
    "labels": ColorRole.TEXT,
    "titles": ColorRole.TEXT,
    "legend text": ColorRole.TEXT,

    # Heatmap
    "heatmap positive extreme": ColorRole.HEATMAP_POSITIVE,
    "heatmap negative extreme": ColorRole.HEATMAP_NEGATIVE,
}


def normalize_role(role_text: str) -> ColorRole | None:
    """
    Normalize free-text role description to standardized ColorRole.

    Parameters
    ----------
    role_text : str
        Free-text role description from tokens file

    Returns
    -------
    ColorRole or None
        Standardized role enum, or None if no match
    """
    # Try exact match first
    try:
        return ColorRole(role_text.lower().replace(" ", "-"))
    except ValueError:
        pass

    # Try alias lookup
    normalized = role_text.lower().strip()
    for alias, role in ROLE_ALIASES.items():
        if alias in normalized:
            return role

    return None


# =============================================================================
# COLOR CYCLE NAMES
# =============================================================================

class CycleName(str, Enum):
    """
    Standard names for color cycles.

    Cycle names should be semantic, describing the use case.
    """
    DEFAULT = "default"
    TREATMENT_CONTROL = "treatment_control"
    NEUTRALS_ONLY = "neutrals_only"
    OPPOSING = "opposing"
    MULTI_CATEGORY = "multi_category"
    VOLCANO = "volcano"
    HEATMAP = "heatmap"
    CATEGORICAL = "categorical"
    SEQUENTIAL = "sequential"
    DIVERGING = "diverging"


# Minimum required cycles for a brand
REQUIRED_CYCLES: Set[str] = {"default"}

# Recommended cycles for scientific visualization
RECOMMENDED_CYCLES: Set[str] = {
    "treatment_control",
    "neutrals_only",
    "opposing",
}


# =============================================================================
# FONT WEIGHTS
# =============================================================================

class FontWeight(str, Enum):
    """Valid font weight values."""
    NORMAL = "normal"
    BOLD = "bold"
    LIGHT = "light"
    MEDIUM = "medium"
    SEMIBOLD = "semibold"


# =============================================================================
# FONT STYLES
# =============================================================================

class FontStyle(str, Enum):
    """Valid font style values."""
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


# =============================================================================
# SPINE POSITIONS
# =============================================================================

class SpinePosition(str, Enum):
    """Valid spine position values."""
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


# =============================================================================
# OUTPUT FORMATS
# =============================================================================

class OutputFormat(str, Enum):
    """Valid output format values."""
    PNG = "PNG"
    PDF = "PDF"
    SVG = "SVG"
    TIFF = "TIFF"
    EPS = "EPS"
    JPEG = "JPEG"
    JPG = "JPG"


# =============================================================================
# MARKER SHAPES
# =============================================================================

class MarkerShape(str, Enum):
    """
    Standard marker shapes for matplotlib.

    When using multiple categories, combine colors with shapes
    for accessibility.
    """
    CIRCLE = "o"
    SQUARE = "s"
    TRIANGLE_UP = "^"
    TRIANGLE_DOWN = "v"
    DIAMOND = "D"
    PENTAGON = "p"
    HEXAGON = "h"
    PLUS = "+"
    X = "x"
    STAR = "*"


# Default shape sequence for multi-category plots
DEFAULT_MARKER_SEQUENCE = [
    MarkerShape.CIRCLE,
    MarkerShape.SQUARE,
    MarkerShape.TRIANGLE_UP,
    MarkerShape.DIAMOND,
]


# =============================================================================
# LINE STYLES
# =============================================================================

class LineStyle(str, Enum):
    """
    Standard line styles for matplotlib.

    Combine with colors for accessibility.
    """
    SOLID = "-"
    DASHED = "--"
    DOTTED = ":"
    DASHDOT = "-."


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def validate_enum_value(value: str, enum_class: type[Enum]) -> bool:
    """Check if value is valid for the given enum."""
    try:
        enum_class(value)
        return True
    except ValueError:
        return False


def get_valid_values(enum_class: type[Enum]) -> list[str]:
    """Get list of valid values for an enum."""
    return [e.value for e in enum_class]


def validate_brand_type(value: str) -> bool:
    """Validate brand-type frontmatter value."""
    return validate_enum_value(value, BrandType)


def validate_font_weight(value: str) -> bool:
    """Validate font weight value."""
    return validate_enum_value(value, FontWeight)


def validate_cycle_name(name: str) -> tuple[bool, str | None]:
    """
    Validate color cycle name.

    Returns tuple of (is_valid, suggestion).
    """
    # Check if it's a standard name
    if validate_enum_value(name, CycleName):
        return True, None

    # Check for common variations
    normalized = name.lower().replace("-", "_").replace(" ", "_")
    if validate_enum_value(normalized, CycleName):
        return True, f"Consider using '{normalized}' for consistency"

    # Custom names are allowed but flagged
    return True, f"'{name}' is a custom cycle name (not in standard vocabulary)"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BrandType",
    "ColorRole",
    "CycleName",
    "FontWeight",
    "FontStyle",
    "SpinePosition",
    "OutputFormat",
    "MarkerShape",
    "LineStyle",
    "normalize_role",
    "validate_brand_type",
    "validate_cycle_name",
    "validate_enum_value",
    "get_valid_values",
    "ROLE_ALIASES",
    "REQUIRED_CYCLES",
    "RECOMMENDED_CYCLES",
    "DEFAULT_MARKER_SEQUENCE",
]
