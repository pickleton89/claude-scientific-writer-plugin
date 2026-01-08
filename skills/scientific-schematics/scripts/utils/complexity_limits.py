"""Complexity limits for scientific diagram types.

Defines maximum component counts per diagram type to prevent overcrowded
diagrams that become difficult to read. These limits are based on cognitive
load research and publication best practices.

Usage:
    >>> from utils.complexity_limits import check_complexity
    >>> ok, warning = check_complexity("consort", 12)
    >>> print(ok, warning)
    True None
    >>> ok, warning = check_complexity("consort", 18)
    >>> print(ok, warning)
    False 'Estimated 18 nodes exceeds limit of 15 for consort...'
"""

from __future__ import annotations

import re
from typing import NamedTuple


class ComplexityLimits(NamedTuple):
    """Complexity limits for a diagram type."""

    max_nodes: int
    max_edges: int
    max_levels: int


# Diagram type complexity limits based on cognitive load research
# and publication best practices for scientific figures
COMPLEXITY_LIMITS: dict[str, ComplexityLimits] = {
    # Study design diagrams
    "consort": ComplexityLimits(max_nodes=15, max_edges=20, max_levels=4),
    "prisma": ComplexityLimits(max_nodes=12, max_edges=15, max_levels=4),
    "methods_flowchart": ComplexityLimits(max_nodes=15, max_edges=20, max_levels=5),
    "flowchart": ComplexityLimits(max_nodes=15, max_edges=20, max_levels=5),
    # Neural network architectures
    "transformer": ComplexityLimits(max_nodes=12, max_edges=0, max_levels=3),
    "cnn": ComplexityLimits(max_nodes=12, max_edges=0, max_levels=3),
    "rnn_lstm": ComplexityLimits(max_nodes=10, max_edges=0, max_levels=3),
    "neural_network": ComplexityLimits(max_nodes=12, max_edges=0, max_levels=4),
    # Biological diagrams
    "pathway": ComplexityLimits(max_nodes=10, max_edges=12, max_levels=3),
    "metabolic_pathway": ComplexityLimits(max_nodes=12, max_edges=15, max_levels=3),
    "regulatory_network": ComplexityLimits(max_nodes=10, max_edges=15, max_levels=3),
    "interaction_network": ComplexityLimits(max_nodes=10, max_edges=12, max_levels=2),
    # Systems/engineering diagrams
    "system_architecture": ComplexityLimits(max_nodes=12, max_edges=15, max_levels=3),
    "data_flow_diagram": ComplexityLimits(max_nodes=12, max_edges=15, max_levels=3),
    "block_diagram": ComplexityLimits(max_nodes=10, max_edges=12, max_levels=2),
    "circuit_schematic": ComplexityLimits(max_nodes=15, max_edges=20, max_levels=2),
    "circuit": ComplexityLimits(max_nodes=15, max_edges=20, max_levels=2),
    # Abstract/conceptual diagrams
    "conceptual_framework": ComplexityLimits(max_nodes=8, max_edges=10, max_levels=3),
    "hierarchy_diagram": ComplexityLimits(max_nodes=15, max_edges=14, max_levels=4),
    "venn_diagram": ComplexityLimits(max_nodes=5, max_edges=0, max_levels=1),
}

# Default limits for unknown diagram types
DEFAULT_LIMITS = ComplexityLimits(max_nodes=12, max_edges=15, max_levels=3)


def get_limits(diagram_type: str) -> ComplexityLimits:
    """Get complexity limits for a diagram type.

    Args:
        diagram_type: The type of diagram (e.g., "consort", "transformer")

    Returns:
        ComplexityLimits with max_nodes, max_edges, max_levels
    """
    return COMPLEXITY_LIMITS.get(diagram_type.lower(), DEFAULT_LIMITS)


def check_complexity(
    diagram_type: str,
    estimated_nodes: int,
    estimated_edges: int | None = None,
    estimated_levels: int | None = None,
) -> tuple[bool, str | None]:
    """Check if estimated complexity is within limits.

    Args:
        diagram_type: The type of diagram
        estimated_nodes: Estimated number of nodes/components
        estimated_edges: Optional estimated number of connections
        estimated_levels: Optional estimated number of hierarchy levels

    Returns:
        Tuple of (within_limits, warning_message)
        - within_limits: True if complexity is acceptable
        - warning_message: Warning text if approaching or exceeding limits, None otherwise
    """
    limits = get_limits(diagram_type)
    warnings = []

    # Check node count
    if estimated_nodes > limits.max_nodes:
        return (
            False,
            f"Estimated {estimated_nodes} nodes exceeds limit of {limits.max_nodes} "
            f"for {diagram_type}. Consider splitting into multiple figures.",
        )

    if estimated_nodes > limits.max_nodes * 0.8:
        warnings.append(
            f"Approaching node limit ({estimated_nodes}/{limits.max_nodes})"
        )

    # Check edge count if provided
    if estimated_edges is not None and limits.max_edges > 0:
        if estimated_edges > limits.max_edges:
            return (
                False,
                f"Estimated {estimated_edges} edges exceeds limit of {limits.max_edges} "
                f"for {diagram_type}. Simplify connections or split into multiple figures.",
            )
        if estimated_edges > limits.max_edges * 0.8:
            warnings.append(
                f"Approaching edge limit ({estimated_edges}/{limits.max_edges})"
            )

    # Check level count if provided
    if estimated_levels is not None:
        if estimated_levels > limits.max_levels:
            return (
                False,
                f"Estimated {estimated_levels} levels exceeds limit of {limits.max_levels} "
                f"for {diagram_type}. Flatten hierarchy or split into multiple figures.",
            )
        if estimated_levels > limits.max_levels - 1:
            warnings.append(
                f"Approaching level limit ({estimated_levels}/{limits.max_levels})"
            )

    # Return combined warning if any
    if warnings:
        return True, f"Complexity warning: {'; '.join(warnings)}. Consider simplifying."

    return True, None


def estimate_nodes_from_prompt(prompt: str) -> int:
    """Estimate number of nodes/components from prompt text.

    Uses heuristics to count component indicators in the prompt.
    This is a rough estimate for early validation.

    Args:
        prompt: User's diagram description

    Returns:
        Estimated node count (minimum 3)
    """
    prompt_lower = prompt.lower()

    # Count explicit numeric mentions
    numeric_patterns = [
        r"(\d+)\s*(?:boxes?|nodes?|components?|steps?|stages?|layers?|blocks?)",
        r"(\d+)\s*(?:items?|elements?|parts?|sections?)",
    ]

    explicit_count = 0
    for pattern in numeric_patterns:
        matches = re.findall(pattern, prompt_lower)
        for match in matches:
            explicit_count += int(match)

    if explicit_count > 0:
        return explicit_count

    # Count component indicators
    component_indicators = [
        r"→|->|-->|—>",  # Arrows
        r"\bto\b|\bfrom\b",  # Flow words
        r"\bconnects?\b|\blinks?\b",  # Connection words
        r"\bbox\b|\bnode\b|\bblock\b",  # Component words
        r"\blayer\b|\bstage\b|\bstep\b",  # Process words
        r"\bphase\b|\bcomponent\b|\bmodule\b",  # Structure words
    ]

    indicator_count = 0
    for pattern in component_indicators:
        indicator_count += len(re.findall(pattern, prompt_lower))

    # Estimate: each indicator roughly corresponds to 0.5 nodes
    # with a minimum of 3 and maximum of 20
    estimated = max(3, min(20, indicator_count // 2 + 3))

    return estimated


def get_all_diagram_types() -> list[str]:
    """Get list of all supported diagram types.

    Returns:
        Sorted list of diagram type names
    """
    return sorted(COMPLEXITY_LIMITS.keys())
