"""JSON Schema definitions for visual design inputs and outputs.

Provides structured schemas for validation and documentation.
"""

from typing import Dict, Any


# Input schema for visual design requests
VISUAL_DESIGN_REQUEST_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "VisualDesignRequest",
    "description": "Structured input for visual design skill",
    "type": "object",
    "required": ["venue", "audience", "figure_type"],
    "properties": {
        "venue": {
            "type": "string",
            "description": "Target publication venue",
            "examples": ["nature", "science", "cell", "pnas", "plos", "elife"],
        },
        "audience": {
            "type": "string",
            "enum": [
                "journal",
                "conference_poster",
                "conference_talk",
                "public",
                "internal",
            ],
            "description": "Primary audience for the visual",
        },
        "figure_type": {
            "type": "string",
            "enum": [
                "data_plot",
                "schematic",
                "photograph",
                "multi_panel",
                "infographic",
            ],
            "description": "Type of visual being designed",
        },
        "data_characteristics": {
            "type": "object",
            "description": "Characteristics of the data being visualized",
            "properties": {
                "comparison_type": {
                    "type": "string",
                    "enum": [
                        "comparison",
                        "time_series",
                        "distribution",
                        "relationship",
                        "part_to_whole",
                        "flow_network",
                        "ranking",
                        "geospatial",
                        "uncertainty",
                    ],
                    "description": "Type of data comparison or visualization",
                },
                "n_groups": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "description": "Number of groups or categories",
                },
                "n_time_points": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Number of time points (for time series)",
                },
                "is_diverging": {
                    "type": "boolean",
                    "description": "Data has meaningful center point (e.g., fold change)",
                    "default": False,
                },
            },
        },
        "brand": {
            "type": ["string", "null"],
            "description": "Brand name if organizational standards apply",
        },
        "custom_dimensions": {
            "type": "object",
            "description": "Override default venue dimensions",
            "properties": {
                "width_mm": {"type": "number", "minimum": 10, "maximum": 500},
                "height_mm": {"type": "number", "minimum": 10, "maximum": 500},
            },
        },
        "accessibility_level": {
            "type": "string",
            "enum": ["A", "AA", "AAA"],
            "default": "AA",
            "description": "WCAG accessibility compliance level",
        },
    },
}


# Output schema for figure specifications
FIGURE_SPECIFICATION_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "FigureSpecification",
    "description": "Complete specification for a scientific figure",
    "type": "object",
    "required": ["venue", "dimensions", "resolution_dpi", "color_palette", "typography"],
    "properties": {
        "venue": {
            "type": "string",
            "description": "Target publication venue",
        },
        "dimensions": {
            "type": "object",
            "required": ["width_mm"],
            "properties": {
                "width_mm": {"type": "number"},
                "width_in": {"type": "number"},
                "height_mm": {"type": "number"},
                "height_in": {"type": "number"},
                "column_type": {
                    "type": "string",
                    "enum": ["single", "double", "custom"],
                },
            },
        },
        "resolution_dpi": {
            "type": "integer",
            "minimum": 72,
            "maximum": 1200,
        },
        "file_format": {
            "type": "string",
            "enum": ["pdf", "eps", "tiff", "png", "svg"],
        },
        "color_mode": {
            "type": "string",
            "enum": ["rgb", "cmyk", "grayscale"],
            "default": "rgb",
        },
        "color_palette": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {
                    "type": "string",
                    "enum": ["categorical", "sequential", "diverging", "binary"],
                },
                "colors": {
                    "type": "array",
                    "items": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                },
                "primary": {"type": "string"},
                "secondary": {"type": "string"},
                "accent": {"type": "string"},
                "background": {"type": "string", "default": "#FFFFFF"},
                "text": {"type": "string", "default": "#000000"},
            },
        },
        "typography": {
            "type": "object",
            "properties": {
                "family": {"type": "string"},
                "title_pt": {"type": "number"},
                "axis_label_pt": {"type": "number"},
                "tick_label_pt": {"type": "number"},
                "legend_pt": {"type": "number"},
                "annotation_pt": {"type": "number"},
                "min_pt": {"type": "number", "minimum": 6},
            },
        },
        "accessibility": {
            "type": "object",
            "properties": {
                "colorblind_safe": {"type": "boolean"},
                "min_contrast_ratio": {"type": "number"},
                "redundant_encoding": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["shape", "line_style", "pattern", "size", "label"],
                    },
                },
                "wcag_level": {
                    "type": "string",
                    "enum": ["A", "AA", "AAA"],
                },
            },
        },
        "chart_recommendation": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "alternatives": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "avoid": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "reason": {"type": "string"},
            },
        },
        "panel_label_case": {
            "type": "string",
            "enum": ["upper", "lower"],
        },
        "min_line_weight_pt": {
            "type": "number",
            "minimum": 0.25,
        },
    },
}


# Validation result schema
VALIDATION_RESULT_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ValidationResult",
    "description": "Result of figure specification validation",
    "type": "object",
    "required": ["valid", "errors", "warnings"],
    "properties": {
        "valid": {
            "type": "boolean",
            "description": "Whether the specification passes all critical checks",
        },
        "errors": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Critical issues that must be fixed",
        },
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Recommendations that should be considered",
        },
        "venue": {"type": "string"},
        "venue_canonical": {"type": "string"},
        "checks_performed": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
}


def get_request_schema() -> Dict[str, Any]:
    """Return the visual design request schema."""
    return VISUAL_DESIGN_REQUEST_SCHEMA


def get_specification_schema() -> Dict[str, Any]:
    """Return the figure specification schema."""
    return FIGURE_SPECIFICATION_SCHEMA


def get_validation_schema() -> Dict[str, Any]:
    """Return the validation result schema."""
    return VALIDATION_RESULT_SCHEMA


def validate_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a visual design request against the schema.

    This is a simple validation without jsonschema dependency.
    For full validation, use jsonschema.validate().

    Args:
        request: Request dict to validate

    Returns:
        Dict with valid status and any errors
    """
    errors = []

    # Check required fields
    required = ["venue", "audience", "figure_type"]
    for field in required:
        if field not in request:
            errors.append(f"Missing required field: {field}")

    # Validate audience enum
    valid_audiences = [
        "journal",
        "conference_poster",
        "conference_talk",
        "public",
        "internal",
    ]
    if "audience" in request and request["audience"] not in valid_audiences:
        errors.append(f"Invalid audience: {request['audience']}")

    # Validate figure_type enum
    valid_types = ["data_plot", "schematic", "photograph", "multi_panel", "infographic"]
    if "figure_type" in request and request["figure_type"] not in valid_types:
        errors.append(f"Invalid figure_type: {request['figure_type']}")

    # Validate data_characteristics if present
    if "data_characteristics" in request:
        dc = request["data_characteristics"]
        if "n_groups" in dc:
            if not isinstance(dc["n_groups"], int) or dc["n_groups"] < 1:
                errors.append("n_groups must be a positive integer")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }
