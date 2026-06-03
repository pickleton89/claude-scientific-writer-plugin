"""Template rendering for figure specifications.

Generates both human-readable markdown and machine-readable YAML outputs
from figure specification dictionaries.
"""

from typing import Dict, Any, Optional


def render_spec_yaml(spec: Dict[str, Any]) -> str:
    """Render figure specification as YAML for machine parsing.

    Args:
        spec: Figure specification dict

    Returns:
        YAML-formatted string
    """
    lines = ["figure_spec:"]

    # Venue
    lines.append(f"  venue: {spec.get('venue', 'default')}")

    # Dimensions
    dims = spec.get("dimensions", {})
    lines.append("  dimensions:")
    if "width_mm" in dims:
        lines.append(f"    width_mm: {dims['width_mm']}")
    if "width_in" in dims:
        lines.append(f"    width_in: {dims['width_in']}")
    if "height_mm" in dims:
        lines.append(f"    height_mm: {dims['height_mm']}")
    if "column_type" in dims:
        lines.append(f"    column_type: {dims['column_type']}")

    # Resolution and format
    if "resolution_dpi" in spec:
        lines.append(f"  resolution_dpi: {spec['resolution_dpi']}")
    if "file_format" in spec:
        lines.append(f"  file_format: {spec['file_format']}")
    if "color_mode" in spec:
        lines.append(f"  color_mode: {spec['color_mode']}")

    # Color palette
    palette = spec.get("color_palette", {})
    if palette:
        lines.append("  color_palette:")
        if "name" in palette:
            lines.append(f"    name: {palette['name']}")
        if "type" in palette:
            lines.append(f"    type: {palette['type']}")
        if "colors" in palette:
            lines.append("    colors:")
            for color in palette["colors"]:
                lines.append(f'      - "{color}"')
        for key in ["primary", "secondary", "accent", "background", "text"]:
            if key in palette:
                lines.append(f'    {key}: "{palette[key]}"')

    # Typography
    typo = spec.get("typography", {})
    if typo:
        lines.append("  typography:")
        for key in [
            "family",
            "title_pt",
            "axis_label_pt",
            "tick_label_pt",
            "legend_pt",
            "annotation_pt",
            "min_pt",
        ]:
            if key in typo:
                value = typo[key]
                if isinstance(value, str):
                    lines.append(f"    {key}: {value}")
                else:
                    lines.append(f"    {key}: {value}")

    # Accessibility
    access = spec.get("accessibility", {})
    if access:
        lines.append("  accessibility:")
        if "colorblind_safe" in access:
            lines.append(
                f"    colorblind_safe: {str(access['colorblind_safe']).lower()}"
            )
        if "min_contrast_ratio" in access:
            lines.append(f"    min_contrast_ratio: {access['min_contrast_ratio']}")
        if "redundant_encoding" in access:
            lines.append("    redundant_encoding:")
            for enc in access["redundant_encoding"]:
                lines.append(f"      - {enc}")
        if "wcag_level" in access:
            lines.append(f"    wcag_level: {access['wcag_level']}")

    # Chart recommendation
    chart = spec.get("chart_recommendation", {})
    if chart:
        lines.append("  chart_recommendation:")
        if "type" in chart:
            lines.append(f"    type: {chart['type']}")
        if "alternatives" in chart:
            lines.append("    alternatives:")
            for alt in chart["alternatives"]:
                lines.append(f"      - {alt}")
        if "avoid" in chart:
            lines.append("    avoid:")
            for av in chart["avoid"]:
                lines.append(f"      - {av}")

    # Panel labels
    if "panel_label_case" in spec:
        lines.append(f"  panel_label_case: {spec['panel_label_case']}")

    # Line weight
    if "min_line_weight_pt" in spec:
        lines.append(f"  min_line_weight_pt: {spec['min_line_weight_pt']}")

    return "\n".join(lines)


def render_spec_markdown(spec: Dict[str, Any], include_validation: bool = True) -> str:
    """Render figure specification as human-readable markdown.

    Args:
        spec: Figure specification dict
        include_validation: Whether to include validation notes

    Returns:
        Markdown-formatted string
    """
    lines = [
        "# Figure Specification",
        "",
        f"**Target Venue:** {spec.get('venue', 'Not specified')}",
        "",
    ]

    # Dimensions section
    dims = spec.get("dimensions", {})
    lines.extend(
        [
            "## Dimensions",
            "",
            "| Property | Value |",
            "|----------|-------|",
        ]
    )
    if "width_mm" in dims:
        lines.append(
            f"| Width | {dims['width_mm']}mm ({dims.get('width_in', 'N/A')}in) |"
        )
    if "height_mm" in dims:
        lines.append(f"| Height | {dims['height_mm']}mm |")
    if "column_type" in dims:
        lines.append(f"| Column Type | {dims['column_type']} |")
    lines.append("")

    # Output settings
    lines.extend(
        [
            "## Output Settings",
            "",
            "| Setting | Value |",
            "|---------|-------|",
        ]
    )
    if "resolution_dpi" in spec:
        lines.append(f"| Resolution | {spec['resolution_dpi']} DPI |")
    if "file_format" in spec:
        lines.append(f"| Format | {spec['file_format'].upper()} |")
    if "color_mode" in spec:
        lines.append(f"| Color Mode | {spec['color_mode'].upper()} |")
    lines.append("")

    # Color palette
    palette = spec.get("color_palette", {})
    if palette:
        lines.extend(
            [
                "## Color Palette",
                "",
            ]
        )
        if "name" in palette:
            lines.append(
                f"**Palette:** {palette['name']} ({palette.get('type', 'categorical')})"
            )
            lines.append("")

        if "colors" in palette:
            lines.append("**Data Colors:**")
            lines.append("")
            for i, color in enumerate(palette["colors"], 1):
                lines.append(f"- Color {i}: `{color}`")
            lines.append("")

        semantic_colors = []
        for key in ["primary", "secondary", "accent", "background", "text"]:
            if key in palette:
                semantic_colors.append(f"- {key.title()}: `{palette[key]}`")
        if semantic_colors:
            lines.append("**Semantic Colors:**")
            lines.append("")
            lines.extend(semantic_colors)
            lines.append("")

    # Typography
    typo = spec.get("typography", {})
    if typo:
        lines.extend(
            [
                "## Typography",
                "",
                "| Element | Size |",
                "|---------|------|",
            ]
        )
        if "family" in typo:
            lines.append(f"| Font Family | {typo['family']} |")
        for key, label in [
            ("title_pt", "Title"),
            ("axis_label_pt", "Axis Labels"),
            ("tick_label_pt", "Tick Labels"),
            ("legend_pt", "Legend"),
            ("annotation_pt", "Annotations"),
            ("min_pt", "Minimum"),
        ]:
            if key in typo:
                lines.append(f"| {label} | {typo[key]}pt |")
        lines.append("")

    # Accessibility
    access = spec.get("accessibility", {})
    if access:
        lines.extend(
            [
                "## Accessibility",
                "",
            ]
        )
        items = []
        if access.get("colorblind_safe"):
            items.append("- [x] Colorblind-safe palette")
        else:
            items.append("- [ ] Colorblind-safe palette")

        if "min_contrast_ratio" in access:
            ratio = access["min_contrast_ratio"]
            passed = ratio >= 4.5
            mark = "x" if passed else " "
            items.append(
                f"- [{mark}] Contrast ratio: {ratio}:1 (WCAG AA requires 4.5:1)"
            )

        if "wcag_level" in access:
            items.append(f"- WCAG Level: {access['wcag_level']}")

        if "redundant_encoding" in access:
            encodings = ", ".join(access["redundant_encoding"])
            items.append(f"- Redundant encoding: {encodings}")

        lines.extend(items)
        lines.append("")

    # Chart recommendation
    chart = spec.get("chart_recommendation", {})
    if chart:
        lines.extend(
            [
                "## Chart Recommendation",
                "",
            ]
        )
        if "type" in chart:
            lines.append(f"**Recommended:** {chart['type']}")
        if "alternatives" in chart:
            lines.append(f"**Alternatives:** {', '.join(chart['alternatives'])}")
        if "avoid" in chart:
            lines.append(f"**Avoid:** {', '.join(chart['avoid'])}")
        if "reason" in chart:
            lines.append("")
            lines.append(f"*{chart['reason']}*")
        lines.append("")

    # Panel labels
    if "panel_label_case" in spec:
        case = spec["panel_label_case"]
        example = "a, b, c" if case == "lower" else "A, B, C"
        lines.extend(
            [
                "## Panel Labels",
                "",
                f"Use **{case}case** labels ({example})",
                "",
            ]
        )

    return "\n".join(lines)


def render_quick_spec_card(spec: Dict[str, Any]) -> str:
    """Render a compact quick-reference specification card.

    Args:
        spec: Figure specification dict

    Returns:
        Compact markdown string
    """
    dims = spec.get("dimensions", {})
    typo = spec.get("typography", {})
    palette = spec.get("color_palette", {})

    lines = [
        "```",
        f"VENUE: {spec.get('venue', 'default')}",
        f"SIZE:  {dims.get('width_mm', '?')}mm x {dims.get('height_mm', '?')}mm ({dims.get('column_type', 'single')} col)",
        f"DPI:   {spec.get('resolution_dpi', 300)}",
        f"FORMAT: {spec.get('file_format', 'pdf').upper()}",
        f"FONT:  {typo.get('family', 'Arial')} (min {typo.get('min_pt', 7)}pt)",
        f"PALETTE: {palette.get('name', 'default')}",
        f"PANELS: {spec.get('panel_label_case', 'upper')}case",
        "```",
    ]

    return "\n".join(lines)


def render_validation_report(
    validation_result: Dict[str, Any],
    spec: Optional[Dict[str, Any]] = None,
) -> str:
    """Render validation results as a markdown report.

    Args:
        validation_result: Output from validate_figure_spec()
        spec: Optional specification for context

    Returns:
        Markdown-formatted validation report
    """
    lines = [
        "# Validation Report",
        "",
    ]

    # Overall status
    status = "PASSED" if validation_result["valid"] else "FAILED"
    emoji = "✓" if validation_result["valid"] else "✗"
    lines.append(f"**Status:** {emoji} {status}")
    lines.append(f"**Venue:** {validation_result.get('venue', 'N/A')}")
    lines.append("")

    # Errors
    errors = validation_result.get("errors", [])
    if errors:
        lines.extend(
            [
                "## Errors (Must Fix)",
                "",
            ]
        )
        for error in errors:
            lines.append(f"- {error}")
        lines.append("")

    # Warnings
    warnings = validation_result.get("warnings", [])
    if warnings:
        lines.extend(
            [
                "## Warnings (Should Consider)",
                "",
            ]
        )
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")

    # Checks performed
    checks = validation_result.get("checks_performed", [])
    if checks:
        lines.extend(
            [
                "## Checks Performed",
                "",
            ]
        )
        for check in checks:
            lines.append(f"- {check}")
        lines.append("")

    if not errors and not warnings:
        lines.append("All checks passed. Specification is ready for use.")

    return "\n".join(lines)
