"""Venue database for deterministic poster specifications.

This module provides a lookup table of conference poster specifications,
ensuring consistent dimensions across all generated posters for the same venue.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class PosterSpecs:
    """Poster specification for a venue.

    Attributes:
        width: Width in inches
        height: Height in inches
        orientation: Portrait, landscape, or square
        dpi: Recommended DPI for print quality
        notes: Optional venue-specific notes
    """

    width: float
    height: float
    orientation: Literal["portrait", "landscape", "square"]
    dpi: int = 300
    notes: str | None = None

    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio (width / height)."""
        return self.width / self.height

    def get_pixel_dimensions(self, dpi: int | None = None) -> tuple[int, int]:
        """Get dimensions in pixels at specified or default DPI.

        Args:
            dpi: DPI to use (defaults to spec's recommended DPI)

        Returns:
            Tuple of (width_px, height_px)
        """
        effective_dpi = dpi or self.dpi
        return (
            int(self.width * effective_dpi),
            int(self.height * effective_dpi),
        )


# Comprehensive venue poster specifications
VENUE_POSTER_SPECS: dict[str, PosterSpecs] = {
    # ==========================================================================
    # Machine Learning / AI Conferences
    # ==========================================================================
    "neurips": PosterSpecs(48, 36, "landscape", 300, "NeurIPS standard"),
    "icml": PosterSpecs(48, 36, "landscape", 300, "ICML standard"),
    "iclr": PosterSpecs(48, 36, "landscape", 300, "ICLR standard"),
    "aaai": PosterSpecs(48, 36, "landscape", 300, "AAAI standard"),
    "ijcai": PosterSpecs(48, 36, "landscape", 300, "IJCAI standard"),
    "uai": PosterSpecs(48, 36, "landscape", 300, "UAI standard"),
    "aistats": PosterSpecs(48, 36, "landscape", 300, "AISTATS standard"),

    # ==========================================================================
    # Computer Vision Conferences
    # ==========================================================================
    "cvpr": PosterSpecs(60, 40, "landscape", 300, "CVPR larger format"),
    "iccv": PosterSpecs(60, 40, "landscape", 300, "ICCV larger format"),
    "eccv": PosterSpecs(48, 36, "landscape", 300, "ECCV standard"),
    "wacv": PosterSpecs(48, 36, "landscape", 300, "WACV standard"),
    "bmvc": PosterSpecs(48, 36, "landscape", 300, "BMVC standard"),

    # ==========================================================================
    # Natural Language Processing Conferences
    # ==========================================================================
    "acl": PosterSpecs(48, 36, "landscape", 300, "ACL standard"),
    "emnlp": PosterSpecs(48, 36, "landscape", 300, "EMNLP standard"),
    "naacl": PosterSpecs(48, 36, "landscape", 300, "NAACL standard"),
    "coling": PosterSpecs(48, 36, "landscape", 300, "COLING standard"),
    "eacl": PosterSpecs(48, 36, "landscape", 300, "EACL standard"),

    # ==========================================================================
    # Robotics Conferences
    # ==========================================================================
    "icra": PosterSpecs(48, 36, "landscape", 300, "ICRA standard"),
    "iros": PosterSpecs(48, 36, "landscape", 300, "IROS standard"),
    "rss": PosterSpecs(48, 36, "landscape", 300, "RSS standard"),
    "corl": PosterSpecs(48, 36, "landscape", 300, "CoRL standard"),

    # ==========================================================================
    # Systems / Architecture Conferences
    # ==========================================================================
    "osdi": PosterSpecs(40, 30, "landscape", 300, "OSDI compact"),
    "sosp": PosterSpecs(40, 30, "landscape", 300, "SOSP compact"),
    "nsdi": PosterSpecs(40, 30, "landscape", 300, "NSDI compact"),
    "eurosys": PosterSpecs(48, 36, "landscape", 300, "EuroSys standard"),
    "asplos": PosterSpecs(48, 36, "landscape", 300, "ASPLOS standard"),
    "isca": PosterSpecs(48, 36, "landscape", 300, "ISCA standard"),
    "micro": PosterSpecs(48, 36, "landscape", 300, "MICRO standard"),

    # ==========================================================================
    # Biology / Bioinformatics Conferences
    # ==========================================================================
    "ismb": PosterSpecs(48, 36, "landscape", 300, "ISMB standard"),
    "recomb": PosterSpecs(36, 48, "portrait", 300, "RECOMB portrait preferred"),
    "ashg": PosterSpecs(48, 36, "landscape", 300, "ASHG standard"),
    "cshl": PosterSpecs(48, 36, "landscape", 300, "Cold Spring Harbor standard"),
    "embo": PosterSpecs(48, 36, "landscape", 300, "EMBO standard"),
    "keystone": PosterSpecs(48, 36, "landscape", 300, "Keystone Symposia"),

    # ==========================================================================
    # Neuroscience Conferences
    # ==========================================================================
    "sfn": PosterSpecs(45, 45, "square", 300, "SfN unique square format"),
    "cosyne": PosterSpecs(36, 48, "portrait", 300, "COSYNE portrait"),
    "fens": PosterSpecs(48, 36, "landscape", 300, "FENS standard"),
    "ohbm": PosterSpecs(48, 36, "landscape", 300, "OHBM standard"),

    # ==========================================================================
    # Chemistry / Materials Science Conferences
    # ==========================================================================
    "acs_national": PosterSpecs(48, 36, "landscape", 300, "ACS National Meeting"),
    "acs_spring": PosterSpecs(48, 36, "landscape", 300, "ACS Spring Meeting"),
    "acs_fall": PosterSpecs(48, 36, "landscape", 300, "ACS Fall Meeting"),
    "mrs_spring": PosterSpecs(48, 36, "landscape", 300, "MRS Spring Meeting"),
    "mrs_fall": PosterSpecs(48, 36, "landscape", 300, "MRS Fall Meeting"),

    # ==========================================================================
    # Physics Conferences
    # ==========================================================================
    "aps_march": PosterSpecs(48, 36, "landscape", 300, "APS March Meeting"),
    "aps_april": PosterSpecs(48, 36, "landscape", 300, "APS April Meeting"),
    "aps_damop": PosterSpecs(48, 36, "landscape", 300, "APS DAMOP"),

    # ==========================================================================
    # Medical / Clinical Conferences
    # ==========================================================================
    "asco": PosterSpecs(48, 36, "landscape", 300, "ASCO standard"),
    "aacr": PosterSpecs(48, 36, "landscape", 300, "AACR standard"),
    "ash": PosterSpecs(48, 36, "landscape", 300, "ASH standard"),
    "aha": PosterSpecs(48, 36, "landscape", 300, "AHA standard"),

    # ==========================================================================
    # International Paper Standards (ISO 216)
    # ==========================================================================
    "a0_portrait": PosterSpecs(33.1, 46.8, "portrait", 300, "ISO A0 portrait"),
    "a0_landscape": PosterSpecs(46.8, 33.1, "landscape", 300, "ISO A0 landscape"),
    "a1_portrait": PosterSpecs(23.4, 33.1, "portrait", 300, "ISO A1 portrait"),
    "a1_landscape": PosterSpecs(33.1, 23.4, "landscape", 300, "ISO A1 landscape"),
    "a2_portrait": PosterSpecs(16.5, 23.4, "portrait", 300, "ISO A2 portrait"),
    "a2_landscape": PosterSpecs(23.4, 16.5, "landscape", 300, "ISO A2 landscape"),

    # ==========================================================================
    # US Paper Standards (ANSI/ARCH)
    # ==========================================================================
    "arch_e": PosterSpecs(36, 48, "portrait", 300, "ANSI/ARCH E (36x48)"),
    "arch_e1": PosterSpecs(30, 42, "portrait", 300, "ANSI/ARCH E1 (30x42)"),
    "arch_d": PosterSpecs(24, 36, "portrait", 300, "ANSI/ARCH D (24x36)"),

    # ==========================================================================
    # Default / Fallback
    # ==========================================================================
    "standard": PosterSpecs(48, 36, "landscape", 300, "Standard default"),
}


def get_poster_specs(venue: str) -> PosterSpecs:
    """Get poster specifications for a venue.

    Performs case-insensitive lookup with common normalization:
    - Converts to lowercase
    - Replaces spaces and hyphens with underscores

    Args:
        venue: Venue name or identifier

    Returns:
        PosterSpecs for the venue, or standard specs if not found

    Examples:
        >>> specs = get_poster_specs("NeurIPS")
        >>> specs.width, specs.height
        (48, 36)
        >>> specs = get_poster_specs("APS March")
        >>> specs.width, specs.height
        (48, 36)
    """
    venue_key = venue.lower().replace(" ", "_").replace("-", "_")
    return VENUE_POSTER_SPECS.get(venue_key, VENUE_POSTER_SPECS["standard"])


def list_supported_venues() -> list[str]:
    """List all venues with known poster specifications.

    Returns:
        Sorted list of venue names (excluding 'standard')
    """
    return sorted([v for v in VENUE_POSTER_SPECS.keys() if v != "standard"])


def list_venues_by_category() -> dict[str, list[str]]:
    """List venues organized by category.

    Returns:
        Dictionary mapping category names to lists of venue names
    """
    categories: dict[str, list[str]] = {
        "ml_ai": [
            "neurips", "icml", "iclr", "aaai", "ijcai", "uai", "aistats",
        ],
        "computer_vision": [
            "cvpr", "iccv", "eccv", "wacv", "bmvc",
        ],
        "nlp": [
            "acl", "emnlp", "naacl", "coling", "eacl",
        ],
        "robotics": [
            "icra", "iros", "rss", "corl",
        ],
        "systems": [
            "osdi", "sosp", "nsdi", "eurosys", "asplos", "isca", "micro",
        ],
        "biology": [
            "ismb", "recomb", "ashg", "cshl", "embo", "keystone",
        ],
        "neuroscience": [
            "sfn", "cosyne", "fens", "ohbm",
        ],
        "chemistry": [
            "acs_national", "acs_spring", "acs_fall", "mrs_spring", "mrs_fall",
        ],
        "physics": [
            "aps_march", "aps_april", "aps_damop",
        ],
        "medical": [
            "asco", "aacr", "ash", "aha",
        ],
        "paper_standards": [
            "a0_portrait", "a0_landscape", "a1_portrait", "a1_landscape",
            "a2_portrait", "a2_landscape", "arch_e", "arch_e1", "arch_d",
        ],
    }
    return categories


def get_poster_pixel_dimensions(
    venue: str,
    dpi: int | None = None,
) -> tuple[int, int]:
    """Get poster dimensions in pixels for a venue.

    Args:
        venue: Venue name or identifier
        dpi: Optional DPI override (uses venue default if not specified)

    Returns:
        Tuple of (width_px, height_px)

    Examples:
        >>> width, height = get_poster_pixel_dimensions("neurips")
        >>> width, height
        (14400, 10800)
    """
    specs = get_poster_specs(venue)
    return specs.get_pixel_dimensions(dpi)


def find_similar_venues(query: str, limit: int = 5) -> list[str]:
    """Find venues with names similar to query.

    Simple substring matching for user assistance.

    Args:
        query: Search query
        limit: Maximum number of results

    Returns:
        List of matching venue names
    """
    query_lower = query.lower()
    matches = []

    for venue in VENUE_POSTER_SPECS.keys():
        if venue == "standard":
            continue
        if query_lower in venue or venue in query_lower:
            matches.append(venue)

    return sorted(matches)[:limit]


__all__ = [
    "PosterSpecs",
    "VENUE_POSTER_SPECS",
    "get_poster_specs",
    "list_supported_venues",
    "list_venues_by_category",
    "get_poster_pixel_dimensions",
    "find_similar_venues",
]
