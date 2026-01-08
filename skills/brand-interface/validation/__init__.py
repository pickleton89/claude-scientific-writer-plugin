"""
Brand Interface Validation Package

Provides deterministic validation tools for brand skills.
"""

from .validate_brand import (
    validate_brand,
    ValidationReport,
    ValidationIssue,
    Severity,
)
from .check_accessibility import (
    contrast_ratio,
    passes_wcag_aa,
    passes_wcag_aaa,
    to_grayscale,
    simulate_colorblind,
    check_color_pair,
)
from .controlled_vocabularies import (
    BrandType,
    ColorRole,
    CycleName,
    normalize_role,
    validate_brand_type,
)

__all__ = [
    # Main validation
    "validate_brand",
    "ValidationReport",
    "ValidationIssue",
    "Severity",
    # Accessibility
    "contrast_ratio",
    "passes_wcag_aa",
    "passes_wcag_aaa",
    "to_grayscale",
    "simulate_colorblind",
    "check_color_pair",
    # Vocabularies
    "BrandType",
    "ColorRole",
    "CycleName",
    "normalize_role",
    "validate_brand_type",
]
