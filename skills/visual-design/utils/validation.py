"""Figure specification validation.

Provides comprehensive validation of figure specifications against
venue requirements and accessibility standards.
"""

from typing import Dict, Any, List, Optional

from .venue_specs import get_venue_specs
from .accessibility import validate_accessibility, check_contrast


def validate_figure_spec(
    spec: Dict[str, Any],
    venue: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate complete figure specification.

    Performs comprehensive validation including:
    - Dimension compliance with venue requirements
    - Resolution/DPI compliance
    - File format compatibility
    - Accessibility requirements
    - Typography requirements

    Args:
        spec: Figure specification dict containing:
            - dimensions: {width_mm, height_mm, column_type}
            - resolution_dpi: Output resolution
            - file_format: Output format (pdf, eps, tiff, etc.)
            - color_palette: Color specifications
            - typography: Font specifications
            - accessibility: Accessibility settings
        venue: Target venue name (optional, uses spec["venue"] if not provided)

    Returns:
        Dict with:
            - valid: Overall validation pass/fail
            - errors: List of critical failures (must fix)
            - warnings: List of recommendations (should consider)
            - venue: Venue name used
            - venue_canonical: Canonical venue key
            - checks_performed: List of validation checks run
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Get venue specs
    venue_name = venue or spec.get("venue", "default")
    venue_req = get_venue_specs(venue_name)

    # Track which checks were performed
    checks_performed = []

    # === Dimension validation ===
    checks_performed.append("dimensions")
    dimensions = spec.get("dimensions", {})
    width = dimensions.get("width_mm", 0)
    height = dimensions.get("height_mm", 0)

    if width > 0:
        if width > venue_req["double_col_mm"]:
            errors.append(
                f"Width {width}mm exceeds {venue_name} maximum "
                f"{venue_req['double_col_mm']}mm (double column)"
            )
        elif width > venue_req["single_col_mm"]:
            warnings.append(
                f"Width {width}mm exceeds single column ({venue_req['single_col_mm']}mm); "
                "requires double column placement"
            )

    if height > 0 and height > venue_req["max_height_mm"]:
        errors.append(
            f"Height {height}mm exceeds {venue_name} maximum {venue_req['max_height_mm']}mm"
        )

    # === Resolution validation ===
    checks_performed.append("resolution")
    dpi = spec.get("resolution_dpi", 0)
    if dpi > 0 and dpi < venue_req["min_dpi"]:
        errors.append(
            f"Resolution {dpi} DPI is below {venue_name} minimum {venue_req['min_dpi']} DPI"
        )

    # === File format validation ===
    checks_performed.append("file_format")
    file_format = spec.get("file_format", "").lower()
    if file_format:
        preferred = venue_req["preferred_format"]
        if file_format not in preferred:
            # Check if it's at least a common format
            common_formats = ["pdf", "eps", "tiff", "png", "svg"]
            if file_format in common_formats:
                warnings.append(
                    f"Format '{file_format}' not in {venue_name} preferred formats: {preferred}"
                )
            else:
                errors.append(
                    f"Format '{file_format}' may not be accepted; "
                    f"use one of: {preferred}"
                )

    # === Typography validation ===
    checks_performed.append("typography")
    typography = spec.get("typography", {})
    min_font = typography.get("min_pt", 0)
    venue_min_font = venue_req.get("min_font_pt", 7)

    if min_font > 0 and min_font < venue_min_font:
        errors.append(
            f"Minimum font size {min_font}pt is below "
            f"{venue_name} requirement of {venue_min_font}pt"
        )
    elif min_font > 0 and min_font < 7:
        errors.append(f"Font size {min_font}pt is below universal 7pt minimum")

    # Check font family recommendation
    font_family = typography.get("family", "")
    if font_family and venue_req.get("font_family"):
        recommended_font = venue_req["font_family"]
        if font_family.lower() not in [
            recommended_font.lower(),
            "arial",
            "helvetica",
        ]:
            warnings.append(
                f"Font '{font_family}' differs from {venue_name} recommended "
                f"'{recommended_font}'"
            )

    # === Panel label validation ===
    checks_performed.append("panel_labels")
    panel_label_case = spec.get("panel_label_case", "")
    venue_panel_case = venue_req.get("panel_label_case", "")

    if panel_label_case and venue_panel_case:
        if panel_label_case.lower() != venue_panel_case.lower():
            warnings.append(
                f"Panel labels are {panel_label_case}case; "
                f"{venue_name} prefers {venue_panel_case}case"
            )

    # === Accessibility validation ===
    checks_performed.append("accessibility")
    accessibility_result = validate_accessibility(spec)
    errors.extend(accessibility_result["errors"])
    warnings.extend(accessibility_result["warnings"])

    # === Color mode validation ===
    checks_performed.append("color_mode")
    color_mode = spec.get("color_mode", "").lower()
    if color_mode == "cmyk":
        warnings.append(
            "CMYK color mode specified; most journals prefer RGB for submission"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "venue": venue_name,
        "venue_canonical": venue_req.get("canonical", venue_name),
        "checks_performed": checks_performed,
    }


def validate_color_palette(
    colors: List[str],
    background: str = "#FFFFFF",
    check_colorblind: bool = True,
) -> Dict[str, Any]:
    """Validate a color palette for accessibility.

    Args:
        colors: List of hex color codes
        background: Background color to check contrast against
        check_colorblind: Whether to check colorblind distinguishability

    Returns:
        Dict with validation results
    """
    errors = []
    warnings = []

    # Check individual color contrast
    low_contrast_colors = []
    for i, color in enumerate(colors):
        result = check_contrast(color, background)
        if result["contrast_ratio"] < 3.0:
            low_contrast_colors.append(
                f"Color {i + 1} ({color}): {result['contrast_ratio']}:1"
            )

    if low_contrast_colors:
        warnings.append(
            f"Low contrast against background: {'; '.join(low_contrast_colors)}"
        )

    # Check color count
    if len(colors) > 10:
        errors.append(
            f"Too many colors ({len(colors)}); maximum 10 for categorical data"
        )
    elif len(colors) > 7:
        warnings.append(
            f"{len(colors)} colors exceeds recommended maximum of 7; "
            "consider grouping or faceting"
        )

    # Check for duplicate colors
    unique_colors = set(c.lower() for c in colors)
    if len(unique_colors) < len(colors):
        warnings.append("Duplicate colors detected in palette")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "color_count": len(colors),
    }


def get_validation_checklist(venue: str) -> List[Dict[str, Any]]:
    """Get a pre-submission validation checklist for a venue.

    Args:
        venue: Target venue name

    Returns:
        List of checklist items with requirements
    """
    venue_specs = get_venue_specs(venue)

    return [
        {
            "category": "Dimensions",
            "items": [
                f"Single column width: <= {venue_specs['single_col_mm']}mm "
                f"({venue_specs['single_col_in']}in)",
                f"Double column width: <= {venue_specs['double_col_mm']}mm "
                f"({venue_specs['double_col_in']}in)",
                f"Maximum height: <= {venue_specs['max_height_mm']}mm",
            ],
        },
        {
            "category": "Resolution & Format",
            "items": [
                f"Minimum resolution: {venue_specs['min_dpi']} DPI",
                f"Preferred formats: {', '.join(venue_specs['preferred_format'])}",
                "Color mode: RGB (convert CMYK if needed)",
            ],
        },
        {
            "category": "Typography",
            "items": [
                f"Minimum font size: {venue_specs.get('min_font_pt', 7)}pt",
                f"Recommended font: {venue_specs.get('font_family', 'Arial')}",
                f"Panel labels: {venue_specs.get('panel_label_case', 'upper')}case "
                f"(e.g., {'a, b, c' if venue_specs.get('panel_label_case') == 'lower' else 'A, B, C'})",
            ],
        },
        {
            "category": "Accessibility",
            "items": [
                "Text/background contrast >= 4.5:1 (WCAG AA)",
                "Colorblind-safe palette used",
                "Redundant encoding (shapes/patterns) for color-critical info",
                "Minimum line weight: 0.5pt (1.0pt recommended)",
            ],
        },
        {
            "category": "Content",
            "items": [
                "Figure is self-contained with caption",
                "All text is legible at print size",
                "No default styling remains",
                "Consistent with other figures in document",
            ],
        },
    ]
