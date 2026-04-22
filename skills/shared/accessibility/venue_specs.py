"""Journal and venue publication specifications.

Provides deterministic lookup of publication requirements for major scientific journals.
Eliminates LLM variance by encoding exact dimensions, DPI, and format requirements.
"""

from typing import Dict, Any


VENUE_SPECS: Dict[str, Dict[str, Any]] = {
    "nature": {
        "single_col_mm": 89,
        "single_col_in": 3.5,
        "double_col_mm": 183,
        "double_col_in": 7.2,
        "max_height_mm": 247,
        "min_dpi": 300,
        "preferred_format": ["pdf", "eps", "tiff"],
        "panel_label_case": "lower",  # a, b, c
        "font_family": "Arial",
        "min_font_pt": 7,
        "notes": "Lowercase panel labels",
    },
    "science": {
        "single_col_mm": 55,
        "single_col_in": 2.2,
        "double_col_mm": 175,
        "double_col_in": 6.9,
        "max_height_mm": 230,
        "min_dpi": 300,
        "preferred_format": ["pdf", "eps"],
        "panel_label_case": "upper",  # A, B, C
        "font_family": "Helvetica",
        "min_font_pt": 7,
        "notes": "Uppercase panel labels",
    },
    "cell": {
        "single_col_mm": 85,
        "single_col_in": 3.3,
        "double_col_mm": 178,
        "double_col_in": 7.0,
        "max_height_mm": 230,
        "min_dpi": 300,
        "preferred_format": ["pdf", "eps", "tiff"],
        "panel_label_case": "upper",
        "font_family": "Arial",
        "min_font_pt": 7,
        "notes": "Uppercase panel labels",
    },
    "pnas": {
        "single_col_mm": 87,
        "single_col_in": 3.4,
        "double_col_mm": 178,
        "double_col_in": 7.0,
        "max_height_mm": 230,
        "min_dpi": 300,
        "preferred_format": ["pdf", "eps", "tiff"],
        "panel_label_case": "upper",
        "font_family": "Arial",
        "min_font_pt": 6,
        "notes": "Two-column format",
    },
    "plos": {
        "single_col_mm": 83,
        "single_col_in": 3.3,
        "double_col_mm": 173,
        "double_col_in": 6.8,
        "max_height_mm": 230,
        "min_dpi": 300,
        "preferred_format": ["tiff", "eps", "pdf"],
        "panel_label_case": "upper",
        "font_family": "Arial",
        "min_font_pt": 8,
        "notes": "CC-BY license required",
    },
    "elife": {
        "single_col_mm": 139,
        "single_col_in": 5.5,
        "double_col_mm": 178,
        "double_col_in": 7.0,
        "max_height_mm": 230,
        "min_dpi": 300,
        "preferred_format": ["pdf", "png"],
        "panel_label_case": "upper",
        "font_family": "Arial",
        "min_font_pt": 7,
        "notes": "Wider single column",
    },
    "jbc": {
        "single_col_mm": 85,
        "single_col_in": 3.3,
        "double_col_mm": 178,
        "double_col_in": 7.0,
        "max_height_mm": 230,
        "min_dpi": 300,
        "preferred_format": ["tiff", "eps", "pdf"],
        "panel_label_case": "upper",
        "font_family": "Arial",
        "min_font_pt": 8,
        "notes": "Journal of Biological Chemistry",
    },
    "embo": {
        "single_col_mm": 86,
        "single_col_in": 3.4,
        "double_col_mm": 178,
        "double_col_in": 7.0,
        "max_height_mm": 230,
        "min_dpi": 300,
        "preferred_format": ["pdf", "eps", "tiff"],
        "panel_label_case": "upper",
        "font_family": "Arial",
        "min_font_pt": 7,
        "notes": "EMBO Journal",
    },
}

# Default specifications for unknown venues
DEFAULT_SPECS: Dict[str, Any] = {
    "single_col_mm": 89,
    "single_col_in": 3.5,
    "double_col_mm": 178,
    "double_col_in": 7.0,
    "max_height_mm": 230,
    "min_dpi": 300,
    "preferred_format": ["pdf", "eps"],
    "panel_label_case": "upper",
    "font_family": "Arial",
    "min_font_pt": 7,
    "notes": "Conservative defaults based on Nature single-column",
}

# Mapping of venue name variations to canonical names
VENUE_ALIASES: Dict[str, str] = {
    # Nature family
    "nature communications": "nature",
    "nature cancer": "nature",
    "nature medicine": "nature",
    "nature methods": "nature",
    "nature genetics": "nature",
    "nature biotechnology": "nature",
    "nature structural & molecular biology": "nature",
    "nature cell biology": "nature",
    "nat commun": "nature",
    "nat med": "nature",
    "nat methods": "nature",
    # Science family
    "science advances": "science",
    "science signaling": "science",
    "science translational medicine": "science",
    "sci adv": "science",
    # Cell family
    "cell reports": "cell",
    "cell systems": "cell",
    "molecular cell": "cell",
    "developmental cell": "cell",
    # PLOS family
    "plos one": "plos",
    "plos biology": "plos",
    "plos genetics": "plos",
    "plos computational biology": "plos",
    "plos medicine": "plos",
    # EMBO family
    "embo journal": "embo",
    "embo reports": "embo",
    "embo molecular medicine": "embo",
}


def normalize_venue_name(venue: str) -> str:
    """Normalize venue name to canonical form.

    Args:
        venue: User-provided venue name (any case/format)

    Returns:
        Canonical venue name key, or "default" if not recognized
    """
    # Normalize: lowercase, strip whitespace
    normalized = venue.lower().strip()

    # Check for exact match first
    if normalized in VENUE_SPECS:
        return normalized

    # Check aliases
    if normalized in VENUE_ALIASES:
        return VENUE_ALIASES[normalized]

    # Extract first word as fallback (handles "Nature Methods" -> "nature")
    first_word = normalized.split()[0] if normalized else ""
    if first_word in VENUE_SPECS:
        return first_word

    return "default"


def get_venue_specs(venue: str) -> Dict[str, Any]:
    """Get publication specifications for a venue.

    Args:
        venue: Venue name (case-insensitive, handles common variations)

    Returns:
        Dict with publication specifications including:
        - single_col_mm/in: Single column width
        - double_col_mm/in: Double column width
        - max_height_mm: Maximum figure height
        - min_dpi: Minimum resolution
        - preferred_format: List of accepted formats
        - panel_label_case: "upper" or "lower"
        - font_family: Recommended font
        - min_font_pt: Minimum font size
        - notes: Additional requirements
        - venue: Original venue name provided
        - canonical: Canonical venue key used
    """
    canonical = normalize_venue_name(venue)

    if canonical == "default":
        return {**DEFAULT_SPECS, "venue": venue, "canonical": "default"}

    return {**VENUE_SPECS[canonical], "venue": venue, "canonical": canonical}


def list_supported_venues() -> list[str]:
    """Return list of all supported venue names."""
    return list(VENUE_SPECS.keys())


def get_column_width(venue: str, column_type: str = "single") -> dict:
    """Get column width for a venue in both mm and inches.

    Args:
        venue: Venue name
        column_type: "single" or "double"

    Returns:
        Dict with width_mm and width_in
    """
    specs = get_venue_specs(venue)

    if column_type == "double":
        return {
            "width_mm": specs["double_col_mm"],
            "width_in": specs["double_col_in"],
            "column_type": "double",
        }

    return {
        "width_mm": specs["single_col_mm"],
        "width_in": specs["single_col_in"],
        "column_type": "single",
    }
