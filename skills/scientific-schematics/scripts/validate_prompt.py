"""Pre-generation prompt validation for scientific schematics.

Validates prompts before expensive API calls to catch issues early
and provide actionable feedback to users.

Usage:
    >>> from validate_prompt import validate_prompt, PromptAnalysis
    >>> result = validate_prompt("CONSORT flowchart with 500 screened, 150 excluded")
    >>> print(result.valid, result.detected_type)
    True 'consort'
"""

from __future__ import annotations

import re
from typing import NamedTuple

from diagram_type_selector import infer_type_from_prompt
from utils.complexity_limits import check_complexity, estimate_nodes_from_prompt


class PromptAnalysis(NamedTuple):
    """Result of prompt validation."""

    valid: bool
    issues: list[str]
    warnings: list[str]
    detected_type: str | None
    type_confidence: float
    component_count: int
    has_layout: bool
    has_quantitative: bool
    detected_keywords: list[str]


# Layout direction keywords
LAYOUT_KEYWORDS = [
    "top-to-bottom",
    "top to bottom",
    "vertical",
    "left-to-right",
    "left to right",
    "horizontal",
    "circular",
    "radial",
    "hierarchical",
    "tree",
]

# Quantitative detail patterns
QUANTITATIVE_PATTERNS = [
    r"n\s*=\s*\d+",  # n = 500
    r"\d+\s*(?:patients?|participants?|subjects?|samples?)",  # 500 patients
    r"\d+\s*(?:layers?|nodes?|steps?|stages?|blocks?)",  # 6 layers
    r"\d+\s*(?:excluded|included|randomized|screened)",  # 150 excluded
    r"\d+%",  # 50%
    r"\d+\s*(?:ms|sec|min|hr)",  # Time durations
]

# Component indicator patterns
COMPONENT_PATTERNS = [
    r"→|->|-->|—>",  # Arrows
    r"\bto\b.*\bfrom\b|\bfrom\b.*\bto\b",  # Flow words
    r"\bconnects?\b|\blinks?\b|\bleads?\b",  # Connection words
    r"\bbox(?:es)?\b|\bnode[s]?\b|\bblock[s]?\b",  # Component words
    r"\blayer[s]?\b|\bstage[s]?\b|\bstep[s]?\b",  # Process words
    r"\bphase[s]?\b|\bcomponent[s]?\b|\bmodule[s]?\b",  # Structure words
    r"\binput\b|\boutput\b",  # I/O
    r"\bstart\b|\bend\b|\bbegin\b|\bfinish\b",  # Endpoints
]


def validate_prompt(prompt: str) -> PromptAnalysis:
    """Validate prompt contains required elements for schematic generation.

    Checks for:
    - Diagram type indicators (CONSORT, transformer, pathway, etc.)
    - Component mentions (arrows, nodes, elements)
    - Layout specification (top-to-bottom, horizontal, etc.)
    - Quantitative details (n=500, 6 layers, etc.)

    Args:
        prompt: User's diagram description

    Returns:
        PromptAnalysis with validation results and detected elements
    """
    issues: list[str] = []
    warnings: list[str] = []
    prompt_lower = prompt.lower()

    # Detect diagram type using the type selector
    type_inference = infer_type_from_prompt(prompt)
    detected_type = type_inference.diagram_type
    type_confidence = type_inference.confidence
    detected_keywords = type_inference.detected_keywords

    # Issue if no diagram type detected with reasonable confidence
    if type_confidence < 0.3:
        issues.append(
            "No recognizable diagram type detected. Include keywords like "
            "'CONSORT', 'transformer', 'pathway', 'flowchart', 'circuit', etc."
        )

    # Check for layout specification
    has_layout = any(kw in prompt_lower for kw in LAYOUT_KEYWORDS)
    if not has_layout:
        warnings.append(
            "No layout direction specified. Consider adding "
            "'top-to-bottom', 'left-to-right', or 'hierarchical'."
        )

    # Estimate component count
    component_count = estimate_nodes_from_prompt(prompt)

    if component_count < 3:
        warnings.append(
            f"Low component count detected (~{component_count}). "
            "Consider adding more specific elements for a meaningful diagram."
        )

    # Check complexity limits
    if detected_type:
        within_limits, complexity_warning = check_complexity(
            detected_type, component_count
        )
        if not within_limits:
            issues.append(complexity_warning or "Complexity exceeds limits")
        elif complexity_warning:
            warnings.append(complexity_warning)

    # Check for quantitative details
    has_quantitative = any(
        re.search(pattern, prompt_lower) for pattern in QUANTITATIVE_PATTERNS
    )
    if not has_quantitative:
        warnings.append(
            "No quantitative details found. Consider adding counts "
            "like 'n=500', '6 layers', or '150 excluded'."
        )

    # Check prompt length
    if len(prompt) < 20:
        issues.append(
            "Prompt too short. Provide more detail about the diagram "
            "structure, components, and relationships."
        )
    elif len(prompt) < 50:
        warnings.append(
            "Prompt is brief. More detail typically produces better results."
        )

    # Check for vague language
    vague_patterns = [
        r"\bsomething\b",
        r"\bwhatever\b",
        r"\betc\.?\b",
        r"\bstuff\b",
        r"\bthings?\b",
    ]
    has_vague = any(re.search(p, prompt_lower) for p in vague_patterns)
    if has_vague:
        warnings.append(
            "Vague language detected. Be specific about components and relationships."
        )

    return PromptAnalysis(
        valid=len(issues) == 0,
        issues=issues,
        warnings=warnings,
        detected_type=detected_type if type_confidence >= 0.3 else None,
        type_confidence=type_confidence,
        component_count=component_count,
        has_layout=has_layout,
        has_quantitative=has_quantitative,
        detected_keywords=detected_keywords,
    )


def format_validation_report(analysis: PromptAnalysis) -> str:
    """Format validation analysis as human-readable report.

    Args:
        analysis: PromptAnalysis from validate_prompt()

    Returns:
        Formatted string report
    """
    lines = ["Prompt Validation Report", "=" * 40]

    # Status
    status = "VALID" if analysis.valid else "INVALID"
    lines.append(f"Status: {status}")

    # Detected type
    if analysis.detected_type:
        lines.append(
            f"Detected Type: {analysis.detected_type} "
            f"(confidence: {analysis.type_confidence:.0%})"
        )
    else:
        lines.append("Detected Type: None")

    # Metrics
    lines.append(f"Component Count: ~{analysis.component_count}")
    lines.append(f"Has Layout: {'Yes' if analysis.has_layout else 'No'}")
    lines.append(f"Has Quantitative: {'Yes' if analysis.has_quantitative else 'No'}")

    # Keywords
    if analysis.detected_keywords:
        lines.append(f"Keywords: {', '.join(analysis.detected_keywords)}")

    # Issues
    if analysis.issues:
        lines.append("")
        lines.append("ISSUES (must fix):")
        for issue in analysis.issues:
            lines.append(f"  - {issue}")

    # Warnings
    if analysis.warnings:
        lines.append("")
        lines.append("WARNINGS (recommended):")
        for warning in analysis.warnings:
            lines.append(f"  - {warning}")

    return "\n".join(lines)


def suggest_improvements(analysis: PromptAnalysis, original_prompt: str) -> str:
    """Suggest specific improvements to the prompt.

    Args:
        analysis: PromptAnalysis from validate_prompt()
        original_prompt: The original user prompt

    Returns:
        Suggested improved prompt or improvement tips
    """
    suggestions = []

    if not analysis.detected_type:
        suggestions.append(
            "Add a clear diagram type (e.g., 'CONSORT flowchart', "
            "'transformer architecture', 'signaling pathway')"
        )

    if not analysis.has_layout:
        suggestions.append("Specify layout: 'top-to-bottom' or 'left-to-right'")

    if not analysis.has_quantitative:
        suggestions.append("Add numbers: 'n=500', '6 layers', '3 stages'")

    if analysis.component_count < 5:
        suggestions.append(
            "List specific components: 'enrollment box', 'attention layer', etc."
        )

    if not suggestions:
        return "Prompt looks good! No improvements needed."

    return "Suggestions:\n" + "\n".join(f"  - {s}" for s in suggestions)


def validate_and_enhance_prompt(
    prompt: str,
    auto_enhance: bool = False,
) -> tuple[PromptAnalysis, str]:
    """Validate prompt and optionally enhance it.

    Args:
        prompt: User's diagram description
        auto_enhance: If True, add default layout/style if missing

    Returns:
        Tuple of (PromptAnalysis, enhanced_prompt)
    """
    analysis = validate_prompt(prompt)

    if not auto_enhance:
        return analysis, prompt

    enhanced = prompt

    # Add default layout if missing
    if not analysis.has_layout:
        enhanced += "\nLayout: top-to-bottom"

    # Add colorblind-safe note if not present
    if "colorblind" not in prompt.lower() and "color" not in prompt.lower():
        enhanced += "\nUse colorblind-safe colors"

    return analysis, enhanced
