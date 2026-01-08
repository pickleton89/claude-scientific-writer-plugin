# Visual Design Skill: Determinism Audit & Implementation Plan

> **Audit Date:** 2026-01-07
> **Skill Version:** 2.3.0
> **Development Stage:** First Draft
> **Auditor:** Claude Code Determinism Auditor

---

## Executive Summary

The visual-design skill has unusually strong deterministic foundations for a first-draft skill—it includes decision matrices, quantitative thresholds, lookup tables, and structured templates. The primary opportunity is to convert these human-readable tables into code-executable logic (automated chart selection, publication spec lookup, accessibility validation), reducing LLM reliance from "interpret this table" to "execute this function."

**Key Finding:** ~70% of the skill's decision-making can be converted to deterministic code, leaving LLM reasoning only for creative/contextual tasks like title generation and contextual advice.

**Estimated Variance Reduction:** 50-70% through implementation of code-based lookup and validation utilities.

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Input Analysis](#input-analysis)
3. [Output Analysis](#output-analysis)
4. [Deterministic Opportunities](#deterministic-opportunities)
5. [Reproducibility Assessment](#reproducibility-assessment)
6. [Code Integration Recommendations](#code-integration-recommendations)
7. [Implementation Plan](#implementation-plan)
8. [Success Metrics](#success-metrics)
9. [File Structure](#file-structure)

---

## Current State Analysis

### What the Skill Accomplishes

The visual-design skill is a "design philosophy" layer that provides guidance for creating publication-quality scientific visuals. It:

1. Establishes visual direction (chart types, color palettes, typography)
2. Ensures accessibility compliance (WCAG, colorblind-safe)
3. Provides publication specifications (journal dimensions, DPI, formats)
4. Delegates implementation to specialized skills (`plotting-libraries`, `scientific-schematics`)

### Current Architecture

```
visual-design/
├── SKILL.md                          # Main skill definition (612 lines)
└── references/
    ├── publication_specs.md          # Journal requirements (163 lines)
    ├── output_templates.md           # Specification templates (154 lines)
    └── OUTPUT_FORMATS.md             # Format guidance (65 lines)
```

### Components Classification

| Component | Current State | Determinism Potential |
|-----------|--------------|----------------------|
| Chart type selection | LLM interprets table | **High** - lookup function |
| Publication specs | LLM reads table | **High** - dict lookup |
| Color palette selection | LLM interprets context | **High** - rule-based |
| Typography hierarchy | Fixed values in table | **High** - constants |
| Accessibility thresholds | WCAG values in prose | **High** - validation code |
| Quality scoring | Subjective rubric | **Medium** - split measurable/subjective |
| Design advice | Contextual guidance | **Low** - requires LLM reasoning |
| Independence Test | Judgment-based | **Low** - requires LLM reasoning |

---

## Input Analysis

### Current State

Inputs are implicitly defined through workflow questions and prerequisites, but not formally structured:

- Target audience (free-form text)
- Venue name (string, no validation)
- Data characteristics (unstructured description)
- Accessibility requirements (implicit)

### Issues

1. **No input schema enforcement** - users provide free-form requests
2. **Venue name variance** - "Nature" vs "nature" vs "Nature Medicine"
3. **Data type interpretation** - LLM must infer from descriptions

### Recommendation: Structured Input Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VisualDesignRequest",
  "type": "object",
  "required": ["venue", "audience", "figure_type"],
  "properties": {
    "venue": {
      "type": "string",
      "enum": ["nature", "science", "cell", "pnas", "plos", "elife", "custom"],
      "description": "Target publication venue"
    },
    "audience": {
      "type": "string",
      "enum": ["journal", "conference_poster", "conference_talk", "public", "internal"],
      "description": "Primary audience for the visual"
    },
    "figure_type": {
      "type": "string",
      "enum": ["data_plot", "schematic", "photograph", "multi_panel", "infographic"],
      "description": "Type of visual being designed"
    },
    "data_characteristics": {
      "type": "object",
      "properties": {
        "comparison_type": {
          "type": "string",
          "enum": [
            "comparison_few_categories",
            "comparison_many_categories",
            "time_series",
            "distribution",
            "relationship_2var",
            "relationship_3var",
            "part_to_whole",
            "flow_network"
          ]
        },
        "n_groups": {
          "type": "integer",
          "minimum": 1,
          "maximum": 20
        },
        "is_diverging": {
          "type": "boolean",
          "description": "Data has meaningful center point (e.g., fold change)"
        }
      }
    },
    "brand": {
      "type": "string",
      "nullable": true,
      "description": "Brand name if organizational standards apply"
    },
    "custom_dimensions": {
      "type": "object",
      "properties": {
        "width_mm": { "type": "number" },
        "height_mm": { "type": "number" }
      }
    }
  }
}
```

---

## Output Analysis

### Current State

Outputs are well-defined through templates:

- Visual Specifications Document (structured markdown)
- Pre-Submission Design Checklist
- Quick Specification Card

### Issues

1. **Templates are LLM-generated** - not code-rendered
2. **No machine-readable format** - downstream skills can't parse
3. **Mixed criteria** - measurable and subjective combined

### Recommendation: Dual Output Format

**Machine-Readable (YAML) for skill handoff:**

```yaml
figure_spec:
  venue: nature
  dimensions:
    width_mm: 89
    height_mm: 70
    column_type: single
  resolution_dpi: 300
  file_format: pdf
  color_mode: rgb

  color_palette:
    primary: "#222222"
    secondary: "#2DB2E8"
    accent: "#E8622D"
    background: "#FFFFFF"

  typography:
    family: Arial
    title_pt: 9
    axis_label_pt: 8
    legend_pt: 7
    min_pt: 7

  accessibility:
    colorblind_safe: true
    min_contrast_ratio: 4.5
    redundant_encoding:
      - shape
      - line_style
    wcag_level: AA

  chart_recommendation:
    type: line
    alternatives:
      - area
    avoid:
      - bar

validation:
  passed: true
  warnings: []
  errors: []
```

**Human-Readable (Markdown) for documentation:**

Generated from the same structured data using a template renderer.

---

## Deterministic Opportunities

### Priority 1: Venue Specification Lookup (100% Deterministic)

**Current:** LLM reads publication specs table and extracts values.

**Proposed:** Python dictionary with direct lookup.

```python
# utils/venue_specs.py

VENUE_SPECS = {
    "nature": {
        "single_col_mm": 89,
        "single_col_in": 3.5,
        "double_col_mm": 183,
        "double_col_in": 7.2,
        "max_height_mm": 247,
        "min_dpi": 300,
        "preferred_format": ["pdf", "eps", "tiff"],
        "panel_label_case": "lower",  # a, b, c
        "notes": "Lowercase panel labels"
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
        "notes": "Uppercase panel labels"
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
        "notes": "Uppercase panel labels"
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
        "notes": "Two-column format"
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
        "notes": "CC-BY license required"
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
        "notes": "Wider single column"
    }
}

# Default for unknown venues
DEFAULT_SPECS = {
    "single_col_mm": 89,
    "single_col_in": 3.5,
    "double_col_mm": 178,
    "double_col_in": 7.0,
    "max_height_mm": 230,
    "min_dpi": 300,
    "preferred_format": ["pdf", "eps"],
    "panel_label_case": "upper",
    "notes": "Conservative defaults based on Nature single-column"
}


def normalize_venue_name(venue: str) -> str:
    """Normalize venue name to canonical form."""
    # Handle common variations
    normalized = venue.lower().strip()

    # Map variations to canonical names
    mappings = {
        "nature communications": "nature",
        "nature cancer": "nature",
        "nature medicine": "nature",
        "nat commun": "nature",
        "science advances": "science",
        "cell reports": "cell",
        "plos one": "plos",
        "plos biology": "plos",
    }

    # Check for exact match first
    if normalized in VENUE_SPECS:
        return normalized

    # Check mappings
    if normalized in mappings:
        return mappings[normalized]

    # Extract first word as fallback
    first_word = normalized.split()[0]
    if first_word in VENUE_SPECS:
        return first_word

    return "default"


def get_venue_specs(venue: str) -> dict:
    """Get publication specifications for a venue."""
    canonical = normalize_venue_name(venue)
    if canonical == "default":
        return {**DEFAULT_SPECS, "venue": venue, "canonical": "default"}
    return {**VENUE_SPECS[canonical], "venue": venue, "canonical": canonical}
```

### Priority 2: Chart Type Selector (100% Deterministic)

**Current:** LLM interprets decision matrix table.

**Proposed:** Python function with lookup logic.

```python
# utils/chart_selector.py

CHART_RECOMMENDATIONS = {
    "comparison_few_categories": {
        "recommended": ["bar", "dot_plot"],
        "avoid": ["pie"],
        "reason": "Bar charts enable precise comparison; pie charts make comparisons difficult"
    },
    "comparison_many_categories": {
        "recommended": ["horizontal_bar", "heatmap"],
        "avoid": ["3d_bar", "pie"],
        "reason": "Horizontal bars accommodate labels; heatmaps show patterns in large datasets"
    },
    "time_series": {
        "recommended": ["line", "area"],
        "avoid": ["bar"],
        "reason": "Line charts imply continuity; bar charts imply discrete measurements"
    },
    "distribution": {
        "recommended": ["histogram", "violin", "box_plot"],
        "avoid": ["bar_of_means"],
        "reason": "Distribution plots show spread and shape; bar of means hides variation"
    },
    "relationship_2var": {
        "recommended": ["scatter"],
        "avoid": ["connected_scatter"],
        "reason": "Scatter shows correlation; connected scatter implies ordered sequence"
    },
    "relationship_3var": {
        "recommended": ["scatter_with_color", "scatter_with_size"],
        "avoid": ["3d_scatter"],
        "reason": "Color/size encoding works well; 3D depth perception is poor"
    },
    "part_to_whole": {
        "recommended": ["stacked_bar", "treemap"],
        "avoid": ["pie_many_segments"],
        "reason": "Stacked bars enable comparison; pie charts fail with >5 segments"
    },
    "flow_network": {
        "recommended": ["sankey", "network_graph"],
        "avoid": ["table"],
        "reason": "Flow diagrams show relationships; tables obscure connections"
    }
}


def recommend_chart_type(
    data_type: str,
    n_categories: int = None
) -> dict:
    """
    Recommend chart type based on data characteristics.

    Args:
        data_type: Type of data comparison (from schema enum)
        n_categories: Number of categories if applicable

    Returns:
        Dict with recommended, avoid, and reason keys
    """
    # Normalize input
    normalized = data_type.lower().replace(" ", "_").replace("-", "_")

    # Handle category count thresholds
    if normalized == "comparison" and n_categories:
        if n_categories <= 5:
            normalized = "comparison_few_categories"
        else:
            normalized = "comparison_many_categories"

    if normalized in CHART_RECOMMENDATIONS:
        return {
            "data_type": data_type,
            **CHART_RECOMMENDATIONS[normalized]
        }

    # Default recommendation
    return {
        "data_type": data_type,
        "recommended": ["bar", "scatter"],
        "avoid": ["3d", "pie"],
        "reason": "Safe defaults for unknown data type"
    }
```

### Priority 3: Color Palette Selector (95% Deterministic)

**Current:** LLM interprets palette selection tables.

**Proposed:** Rule-based selection with predefined palettes.

```python
# utils/palette_selector.py

from typing import List, Optional

# Colorblind-safe categorical palettes
CATEGORICAL_PALETTES = {
    "okabe_ito": {
        "colors": ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"],
        "max_categories": 8,
        "colorblind_safe": True,
        "description": "Okabe-Ito palette, optimized for all CVD types"
    },
    "tableau10": {
        "colors": ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"],
        "max_categories": 10,
        "colorblind_safe": True,
        "description": "Tableau 10, widely recognizable"
    }
}

# Sequential palettes (low to high)
SEQUENTIAL_PALETTES = {
    "viridis": {
        "type": "sequential",
        "colorblind_safe": True,
        "description": "Perceptually uniform, colorblind-safe"
    },
    "plasma": {
        "type": "sequential",
        "colorblind_safe": True,
        "description": "Perceptually uniform, high contrast"
    },
    "cividis": {
        "type": "sequential",
        "colorblind_safe": True,
        "description": "Optimized for deuteranomaly and protanomaly"
    }
}

# Diverging palettes (has meaningful center)
DIVERGING_PALETTES = {
    "rdbu": {
        "type": "diverging",
        "colorblind_safe": True,
        "description": "Red-Blue, good for fold change"
    },
    "puor": {
        "type": "diverging",
        "colorblind_safe": True,
        "description": "Purple-Orange, alternative diverging"
    }
}

# Binary comparison palettes
BINARY_PALETTES = {
    "blue_orange": {
        "colors": ["#0072B2", "#E69F00"],
        "colorblind_safe": True,
        "description": "High contrast binary comparison"
    },
    "magenta_green": {
        "colors": ["#CC79A7", "#009E73"],
        "colorblind_safe": True,
        "description": "Alternative to red-green"
    }
}


def select_palette(
    data_type: str,
    n_groups: int = 2,
    is_diverging: bool = False,
    require_colorblind_safe: bool = True
) -> dict:
    """
    Select appropriate color palette based on data characteristics.

    Args:
        data_type: "categorical", "sequential", "diverging", or "binary"
        n_groups: Number of data groups/categories
        is_diverging: Whether data has meaningful center point
        require_colorblind_safe: Filter for colorblind-safe only

    Returns:
        Dict with palette info and hex codes
    """
    # Override data_type if diverging flag set
    if is_diverging and data_type == "sequential":
        data_type = "diverging"

    # Binary comparison
    if n_groups == 2 or data_type == "binary":
        return {
            "palette_name": "blue_orange",
            "palette_type": "binary",
            **BINARY_PALETTES["blue_orange"]
        }

    # Sequential data
    if data_type == "sequential":
        return {
            "palette_name": "viridis",
            "palette_type": "sequential",
            **SEQUENTIAL_PALETTES["viridis"]
        }

    # Diverging data
    if data_type == "diverging":
        return {
            "palette_name": "rdbu",
            "palette_type": "diverging",
            **DIVERGING_PALETTES["rdbu"]
        }

    # Categorical data
    if n_groups <= 8:
        palette = CATEGORICAL_PALETTES["okabe_ito"]
        return {
            "palette_name": "okabe_ito",
            "palette_type": "categorical",
            "colors": palette["colors"][:n_groups],
            "colorblind_safe": palette["colorblind_safe"],
            "description": palette["description"]
        }
    else:
        # Warn about too many categories
        return {
            "palette_name": "tableau10",
            "palette_type": "categorical",
            "colors": CATEGORICAL_PALETTES["tableau10"]["colors"][:min(n_groups, 10)],
            "colorblind_safe": True,
            "warning": f"n_groups={n_groups} exceeds recommended maximum of 7; consider faceting or grouping",
            "description": "Extended palette with warning"
        }
```

### Priority 4: Accessibility Validator (100% Deterministic)

**Current:** LLM checks against WCAG thresholds in prose.

**Proposed:** Code-based validation functions.

```python
# utils/accessibility.py

import math
from typing import List, Tuple, Optional


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance per WCAG 2.1."""
    def channel_luminance(value: int) -> float:
        v = value / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel_luminance(r) + 0.7152 * channel_luminance(g) + 0.0722 * channel_luminance(b)


def contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.

    Args:
        color1: Hex color code (e.g., "#FFFFFF")
        color2: Hex color code (e.g., "#000000")

    Returns:
        Contrast ratio (1.0 to 21.0)
    """
    l1 = relative_luminance(hex_to_rgb(color1))
    l2 = relative_luminance(hex_to_rgb(color2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def check_contrast(
    foreground: str,
    background: str,
    is_large_text: bool = False,
    level: str = "AA"
) -> dict:
    """
    Check if color combination meets WCAG contrast requirements.

    Args:
        foreground: Foreground/text color (hex)
        background: Background color (hex)
        is_large_text: True if text is ≥18pt or ≥14pt bold
        level: "A", "AA", or "AAA"

    Returns:
        Dict with ratio, required, passed, and level
    """
    ratio = contrast_ratio(foreground, background)

    # WCAG thresholds
    thresholds = {
        "AA": {"normal": 4.5, "large": 3.0},
        "AAA": {"normal": 7.0, "large": 4.5},
        "A": {"normal": 3.0, "large": 3.0}
    }

    text_type = "large" if is_large_text else "normal"
    required = thresholds.get(level, thresholds["AA"])[text_type]

    return {
        "contrast_ratio": round(ratio, 2),
        "required_ratio": required,
        "passed": ratio >= required,
        "wcag_level": level,
        "text_type": text_type
    }


def validate_accessibility(specs: dict) -> dict:
    """
    Validate figure specifications against accessibility requirements.

    Args:
        specs: Figure specification dict with color_palette, typography, etc.

    Returns:
        Validation result with passed, errors, warnings
    """
    errors = []
    warnings = []

    # Font size check
    min_font = specs.get("typography", {}).get("min_pt", 0)
    if min_font < 7:
        errors.append(f"Minimum font size {min_font}pt is below 7pt threshold")
    elif min_font < 8:
        warnings.append(f"Font size {min_font}pt is at minimum; 8pt+ recommended")

    # Line weight check
    min_line = specs.get("min_line_weight_pt", 0)
    if min_line < 0.5:
        errors.append(f"Line weight {min_line}pt is below 0.5pt minimum")
    elif min_line < 1.0:
        warnings.append(f"Line weight {min_line}pt is thin; 1.0pt+ recommended")

    # Color contrast check
    palette = specs.get("color_palette", {})
    text_color = palette.get("text", "#000000")
    bg_color = palette.get("background", "#FFFFFF")

    contrast_result = check_contrast(text_color, bg_color)
    if not contrast_result["passed"]:
        errors.append(
            f"Text/background contrast {contrast_result['contrast_ratio']}:1 "
            f"is below WCAG AA minimum of {contrast_result['required_ratio']}:1"
        )

    # Color count check
    n_colors = len([k for k in palette.keys() if k not in ["text", "background"]])
    if n_colors > 7:
        warnings.append(f"Palette has {n_colors} colors; ≤7 recommended for categorical data")

    # Redundant encoding check
    redundant = specs.get("accessibility", {}).get("redundant_encoding", [])
    if not redundant:
        warnings.append("No redundant encoding specified; add shapes or patterns for colorblind accessibility")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks_performed": [
            "font_size",
            "line_weight",
            "contrast_ratio",
            "color_count",
            "redundant_encoding"
        ]
    }
```

### Priority 5: Quality Score Calculator (70% Deterministic)

**Current:** Subjective 10-point rubric with LLM interpretation.

**Proposed:** Split into measurable (code) and subjective (LLM) components.

```python
# utils/quality_scorer.py

from typing import Dict, List, Optional


def calculate_measurable_score(specs: dict, venue_specs: dict) -> dict:
    """
    Calculate quality score for measurable criteria.

    Returns score out of 4 points (40% of total).
    """
    score = 0
    details = []

    # Resolution check (0-1 point)
    dpi = specs.get("resolution_dpi", 0)
    min_dpi = venue_specs.get("min_dpi", 300)
    if dpi >= min_dpi:
        score += 1
        details.append(f"Resolution: {dpi} DPI meets {min_dpi} DPI requirement (1/1)")
    else:
        details.append(f"Resolution: {dpi} DPI below {min_dpi} DPI requirement (0/1)")

    # Dimension compliance (0-1 point)
    width = specs.get("dimensions", {}).get("width_mm", 0)
    max_width = venue_specs.get("single_col_mm", 89)
    if width <= max_width:
        score += 1
        details.append(f"Dimensions: {width}mm fits within {max_width}mm column (1/1)")
    else:
        details.append(f"Dimensions: {width}mm exceeds {max_width}mm column (0/1)")

    # Accessibility compliance (0-1 point)
    accessibility = specs.get("accessibility", {})
    if accessibility.get("colorblind_safe") and accessibility.get("min_contrast_ratio", 0) >= 4.5:
        score += 1
        details.append("Accessibility: Colorblind-safe with sufficient contrast (1/1)")
    else:
        details.append("Accessibility: Missing colorblind-safe or contrast compliance (0/1)")

    # Typography compliance (0-1 point)
    min_font = specs.get("typography", {}).get("min_pt", 0)
    if min_font >= 7:
        score += 1
        details.append(f"Typography: {min_font}pt meets 7pt minimum (1/1)")
    else:
        details.append(f"Typography: {min_font}pt below 7pt minimum (0/1)")

    return {
        "measurable_score": score,
        "measurable_max": 4,
        "measurable_percentage": score / 4 * 100,
        "details": details
    }


def get_subjective_criteria() -> List[dict]:
    """
    Return criteria that require LLM assessment.

    These contribute 6 points (60% of total score).
    """
    return [
        {
            "criterion": "intentionality",
            "question": "Are all visual choices purposeful with no default styling retained?",
            "max_points": 2,
            "scoring": {
                0: "Uses matplotlib/tool defaults",
                1: "Mostly customized with some defaults",
                2: "Every element (colors, fonts, layout) deliberately chosen"
            }
        },
        {
            "criterion": "clarity",
            "question": "How quickly can a viewer understand the main message?",
            "max_points": 2,
            "scoring": {
                0: "Confusing, takes >30s to understand",
                1: "Clear, understood in 10-30s",
                2: "Immediately clear, <10s to understand"
            }
        },
        {
            "criterion": "consistency",
            "question": "Is styling consistent with other figures in the document?",
            "max_points": 1,
            "scoring": {
                0: "Inconsistent styling",
                1: "Fully consistent with document style"
            }
        },
        {
            "criterion": "independence",
            "question": "Can figure + caption be understood without reading main text?",
            "max_points": 1,
            "scoring": {
                0: "Requires main text for interpretation",
                1: "Self-contained with caption"
            }
        }
    ]


def calculate_total_score(measurable_result: dict, subjective_scores: dict) -> dict:
    """
    Combine measurable and subjective scores.

    Args:
        measurable_result: Output from calculate_measurable_score()
        subjective_scores: Dict mapping criterion names to scores (0-max_points)

    Returns:
        Total score out of 10 with interpretation
    """
    measurable = measurable_result["measurable_score"]

    subjective = sum(subjective_scores.values())
    subjective_max = sum(c["max_points"] for c in get_subjective_criteria())

    total = measurable + subjective

    # Score interpretation
    if total <= 4:
        interpretation = "Needs major revision"
    elif total <= 6:
        interpretation = "Acceptable for internal use"
    elif total <= 8:
        interpretation = "Publication ready"
    else:
        interpretation = "Exemplary design"

    return {
        "total_score": total,
        "max_score": 10,
        "measurable_component": {
            "score": measurable,
            "max": 4,
            "weight": "40%"
        },
        "subjective_component": {
            "score": subjective,
            "max": subjective_max,
            "weight": "60%"
        },
        "interpretation": interpretation,
        "publication_ready": total >= 7
    }
```

---

## Reproducibility Assessment

**Current Rating: Medium-High**

### Positive Factors

- Quantitative thresholds are explicit (4.5:1 contrast, 300 DPI, 7pt minimum)
- Decision matrices provide clear mappings
- Templates ensure consistent output structure
- Publication specs are exact (89mm, 183mm, etc.)

### Negative Factors

- Free-form input interpretation creates variance
- Subjective criteria lack operational definitions
- No end-to-end worked examples
- "Independence Test" relies entirely on judgment

### Target: High Reproducibility

After implementation, the same structured input should produce identical specifications for:
- Venue dimensions, DPI, format
- Color palette selection
- Typography hierarchy
- Accessibility validation results
- Measurable quality score components

LLM variance limited to:
- Contextual design advice
- Subjective quality assessment (with structured rubric)
- Creative elements (figure titles, annotations)

---

## Code Integration Recommendations

### Preprocessing (Before LLM)

1. **Input validation**: Validate against JSON Schema
2. **Venue normalization**: Map user input to canonical name
3. **Spec lookup**: Retrieve all publication requirements
4. **Chart recommendation**: Auto-select based on data type
5. **Palette selection**: Choose colors based on characteristics
6. **Brand loading**: Auto-load tokens if brand specified

### Postprocessing (After LLM)

1. **Specification validation**: Verify against venue requirements
2. **Accessibility validation**: Check contrast, font sizes, colors
3. **Completeness check**: Ensure required fields populated
4. **Template rendering**: Generate markdown and YAML outputs
5. **Quality scoring**: Calculate measurable score component

### Validation Guards

```python
def validate_figure_spec(spec: dict, venue: str) -> dict:
    """
    Validate complete figure specification.

    Returns validation result with errors and warnings.
    """
    venue_req = get_venue_specs(venue)
    errors = []
    warnings = []

    # Dimension validation
    width = spec.get("dimensions", {}).get("width_mm", 0)
    if width > venue_req["double_col_mm"]:
        errors.append(f"Width {width}mm exceeds {venue} maximum {venue_req['double_col_mm']}mm")
    elif width > venue_req["single_col_mm"]:
        warnings.append(f"Width {width}mm requires double column")

    # DPI validation
    dpi = spec.get("resolution_dpi", 0)
    if dpi < venue_req["min_dpi"]:
        errors.append(f"DPI {dpi} below {venue} minimum {venue_req['min_dpi']}")

    # Format validation
    format = spec.get("file_format", "").lower()
    if format and format not in venue_req["preferred_format"]:
        warnings.append(f"Format '{format}' not in {venue} preferred formats: {venue_req['preferred_format']}")

    # Run accessibility validation
    accessibility_result = validate_accessibility(spec)
    errors.extend(accessibility_result["errors"])
    warnings.extend(accessibility_result["warnings"])

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "venue": venue,
        "venue_canonical": venue_req.get("canonical", venue)
    }
```

---

## Implementation Plan

### Phase 1: Data Extraction & Schema (Week 1)

**Objective:** Extract deterministic data from prose into structured formats.

**Tasks:**

1.1. Create `utils/` directory structure
```
skills/visual-design/
├── utils/
│   ├── __init__.py
│   ├── venue_specs.py      # Journal specifications lookup
│   ├── chart_selector.py   # Chart type recommendations
│   ├── palette_selector.py # Color palette selection
│   ├── accessibility.py    # Accessibility validation
│   ├── quality_scorer.py   # Quality score calculation
│   └── schema.py           # Input/output schemas
```

1.2. Create `venue_specs.py` with all journal data from `publication_specs.md`

1.3. Create `schema.py` with JSON Schema definitions:
- `VisualDesignRequest` (input)
- `FigureSpecification` (output)

1.4. Update SKILL.md to reference utilities:
```markdown
<utilities>
## Deterministic Utilities

This skill includes Python utilities for deterministic operations:

- `utils/venue_specs.py`: `get_venue_specs(venue)` → publication requirements
- `utils/chart_selector.py`: `recommend_chart_type(data_type, n_categories)` → chart recommendations
- `utils/palette_selector.py`: `select_palette(data_type, n_groups)` → color palette
- `utils/accessibility.py`: `validate_accessibility(specs)` → accessibility validation
- `utils/quality_scorer.py`: `calculate_measurable_score(specs, venue)` → quality metrics

Load utilities when deterministic operations are needed.
</utilities>
```

**Deliverables:**
- [ ] `utils/__init__.py`
- [ ] `utils/venue_specs.py` with complete venue data
- [ ] `utils/schema.py` with JSON Schema definitions
- [ ] Unit tests for venue lookup

---

### Phase 2: Core Utilities (Week 2)

**Objective:** Implement chart selection and palette selection utilities.

**Tasks:**

2.1. Implement `chart_selector.py`:
- `recommend_chart_type(data_type, n_categories)` function
- Complete decision matrix data
- Unit tests

2.2. Implement `palette_selector.py`:
- `select_palette(data_type, n_groups, is_diverging)` function
- All palette definitions (Okabe-Ito, Viridis, etc.)
- Unit tests

2.3. Create `tests/` directory:
```
skills/visual-design/
├── tests/
│   ├── __init__.py
│   ├── test_venue_specs.py
│   ├── test_chart_selector.py
│   └── test_palette_selector.py
```

**Deliverables:**
- [ ] `utils/chart_selector.py` with full decision matrix
- [ ] `utils/palette_selector.py` with all palettes
- [ ] `tests/test_chart_selector.py`
- [ ] `tests/test_palette_selector.py`

---

### Phase 3: Accessibility & Validation (Week 3)

**Objective:** Implement accessibility checking and specification validation.

**Tasks:**

3.1. Implement `accessibility.py`:
- `contrast_ratio(color1, color2)` function
- `check_contrast(fg, bg, is_large_text, level)` function
- `validate_accessibility(specs)` comprehensive validator
- Unit tests with known color pairs

3.2. Create `validation.py`:
- `validate_figure_spec(spec, venue)` function
- Integration with accessibility validation
- Comprehensive error/warning collection

3.3. Add tests:
- Contrast ratio calculations against known values
- Accessibility validation edge cases
- Full specification validation

**Deliverables:**
- [ ] `utils/accessibility.py` with WCAG compliance
- [ ] `utils/validation.py` for spec validation
- [ ] `tests/test_accessibility.py`
- [ ] `tests/test_validation.py`

---

### Phase 4: Quality Scoring & Templates (Week 4)

**Objective:** Implement hybrid quality scoring and template rendering.

**Tasks:**

4.1. Implement `quality_scorer.py`:
- `calculate_measurable_score(specs, venue_specs)` function
- `get_subjective_criteria()` for LLM assessment
- `calculate_total_score(measurable, subjective)` function

4.2. Create `template_renderer.py`:
- `render_spec_markdown(specs)` for human-readable output
- `render_spec_yaml(specs)` for machine-readable output
- Template strings for consistent formatting

4.3. Update SKILL.md workflow to integrate utilities:
- Stage 2 calls `recommend_chart_type()` and `select_palette()`
- Stage 3 calls `validate_accessibility()`
- Stage 5 calls `calculate_measurable_score()`

**Deliverables:**
- [ ] `utils/quality_scorer.py`
- [ ] `utils/template_renderer.py`
- [ ] Updated SKILL.md with utility integration
- [ ] `tests/test_quality_scorer.py`

---

### Phase 5: Reference Consolidation (Week 5)

**Objective:** Clean up reference files and eliminate duplication.

**Tasks:**

5.1. Consolidate reference files:
- Keep `publication_specs.md` as single source for journal requirements
- Rename `OUTPUT_FORMATS.md` → `format_guidance.md`
- Merge overlapping content from `output_templates.md`

5.2. Update cross-references in SKILL.md:
- Remove duplicated publication specs table
- Reference utilities for deterministic operations
- Add version headers to all files

5.3. Add worked examples:
- Example 1: Simple Nature single-column figure
- Example 2: Multi-panel Cell figure
- Example 3: Conference poster adaptation

5.4. Create integration test:
- End-to-end test with sample request
- Verify deterministic outputs match expected

**Deliverables:**
- [ ] Consolidated reference structure
- [ ] Updated SKILL.md with examples
- [ ] `tests/test_integration.py`
- [ ] Documentation of all changes

---

## Success Metrics

### Quantitative Targets

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Deterministic decision coverage | ~30% | 70% | % of decisions made by code vs LLM |
| Output variance (same input) | High | Low | Diff analysis of repeated requests |
| Validation coverage | Manual | 100% | % of specs validated by code |
| Test coverage | 0% | 80% | pytest coverage report |

### Qualitative Targets

1. **Same structured input → identical specifications** for venue, dimensions, palette, accessibility
2. **LLM role limited to**: contextual advice, subjective scoring, creative elements
3. **Skill handoff works**: downstream skills can parse machine-readable output
4. **Maintainability improved**: single source of truth for all data

### Validation Approach

1. **Unit tests**: Each utility function tested independently
2. **Integration tests**: Full workflow from input to output
3. **Regression tests**: Verify outputs don't change unexpectedly
4. **Manual review**: Spot-check LLM outputs for quality

---

## File Structure

### After Implementation

```
skills/visual-design/
├── SKILL.md                          # Main skill (updated with utility refs)
├── DETERMINISM_AUDIT.md              # This document
├── utils/
│   ├── __init__.py                   # Package exports
│   ├── venue_specs.py                # Journal specifications (Priority 1)
│   ├── chart_selector.py             # Chart recommendations (Priority 2)
│   ├── palette_selector.py           # Color selection (Priority 3)
│   ├── accessibility.py              # WCAG validation (Priority 4)
│   ├── quality_scorer.py             # Hybrid scoring (Priority 5)
│   ├── validation.py                 # Spec validation
│   ├── template_renderer.py          # Output generation
│   └── schema.py                     # JSON Schema definitions
├── tests/
│   ├── __init__.py
│   ├── test_venue_specs.py
│   ├── test_chart_selector.py
│   ├── test_palette_selector.py
│   ├── test_accessibility.py
│   ├── test_validation.py
│   ├── test_quality_scorer.py
│   └── test_integration.py
└── references/
    ├── publication_specs.md          # Journal requirements (source of truth)
    ├── output_templates.md           # Specification templates
    └── format_guidance.md            # Format-specific guidance (renamed)
```

---

## Appendix: Quick Reference

### Utility Function Summary

| Function | Input | Output | Determinism |
|----------|-------|--------|-------------|
| `get_venue_specs(venue)` | venue name | specs dict | 100% |
| `recommend_chart_type(data_type, n)` | data characteristics | recommendations | 100% |
| `select_palette(type, n, diverging)` | data characteristics | palette | 100% |
| `contrast_ratio(c1, c2)` | two hex colors | ratio float | 100% |
| `validate_accessibility(specs)` | spec dict | validation result | 100% |
| `calculate_measurable_score(specs)` | spec dict | score (0-4) | 100% |
| `validate_figure_spec(spec, venue)` | spec + venue | validation result | 100% |

### Decision Points Remaining for LLM

1. Interpreting user's free-form request into structured input
2. Providing contextual design advice beyond lookup tables
3. Assessing subjective quality criteria (intentionality, clarity)
4. Generating figure titles and annotations
5. Handling edge cases not covered by decision matrices
