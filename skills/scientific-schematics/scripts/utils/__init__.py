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
from .mermaid_templates import (
    TEMPLATES as MERMAID_TEMPLATES,
    DIAGRAM_TYPE_TO_TEMPLATES,
    TemplateInfo,
    fill_template,
    get_template_for_type,
    get_template,
    list_templates,
    list_diagram_types,
    get_template_metadata,
    get_required_fields,
    validate_template_data,
    build_nodes_string,
    build_connections_string,
    build_flowchart,
    resolve_edge_style,
    EDGE_STYLES,
    EDGE_STYLE_ALIASES,
)
from .mermaid_renderer import (
    MermaidRenderer,
    RenderBackend,
    RenderConfig,
    RenderResult,
    render_mermaid,
    validate_mermaid_syntax,
    get_mermaid_version,
)
from .complexity_analyzer import (
    GenerationTier,
    ComplexityAnalysis,
    analyze_complexity,
    is_mermaid_compatible,
    get_quality_requirement,
    detect_diagram_type,
    should_use_mermaid,
    get_tier_summary,
    QUALITY_THRESHOLDS,
    MERMAID_SUPPORTED_TYPES,
    AI_ONLY_TYPES,
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
    # Mermaid templates
    "MERMAID_TEMPLATES",
    "DIAGRAM_TYPE_TO_TEMPLATES",
    "TemplateInfo",
    "fill_template",
    "get_template_for_type",
    "get_template",
    "list_templates",
    "list_diagram_types",
    "get_template_metadata",
    "get_required_fields",
    "validate_template_data",
    "build_nodes_string",
    "build_connections_string",
    "build_flowchart",
    "resolve_edge_style",
    "EDGE_STYLES",
    "EDGE_STYLE_ALIASES",
    # Mermaid renderer
    "MermaidRenderer",
    "RenderBackend",
    "RenderConfig",
    "RenderResult",
    "render_mermaid",
    "validate_mermaid_syntax",
    "get_mermaid_version",
    # Complexity analyzer
    "GenerationTier",
    "ComplexityAnalysis",
    "analyze_complexity",
    "is_mermaid_compatible",
    "get_quality_requirement",
    "detect_diagram_type",
    "should_use_mermaid",
    "get_tier_summary",
    "QUALITY_THRESHOLDS",
    "MERMAID_SUPPORTED_TYPES",
    "AI_ONLY_TYPES",
]
