"""Complexity analyzer for tiered diagram generation.

Analyzes diagram requests and determines the appropriate generation tier:
- Tier 1 (Mermaid): Simple diagrams, free, instant rendering
- Tier 2 (AI): Complex diagrams, publication quality

Usage:
    >>> from utils.complexity_analyzer import analyze_complexity, GenerationTier
    >>> analysis = analyze_complexity("Simple 5-step process flow")
    >>> print(analysis.recommended_tier)
    GenerationTier.MERMAID
    >>> analysis = analyze_complexity("MAPK signaling pathway with 15 proteins")
    >>> print(analysis.recommended_tier)
    GenerationTier.AI
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .complexity_limits import estimate_nodes_from_prompt, get_limits
from .mermaid_templates import DIAGRAM_TYPE_TO_TEMPLATES


class GenerationTier(Enum):
    """Available generation tiers for diagram creation."""

    MERMAID = "mermaid"
    AI = "ai"
    MERMAID_PLUS_POLISH = "mermaid+ai"


@dataclass
class ComplexityAnalysis:
    """Result of diagram complexity analysis.

    Attributes:
        estimated_nodes: Estimated number of nodes/components
        estimated_edges: Estimated number of connections
        diagram_type: Detected or specified diagram type
        mermaid_compatible: Whether diagram can be rendered with Mermaid
        recommended_tier: Recommended generation tier
        confidence: Confidence score (0.0-1.0) in the recommendation
        reasoning: Human-readable explanation of the decision
    """

    estimated_nodes: int
    estimated_edges: int
    diagram_type: str
    mermaid_compatible: bool
    recommended_tier: GenerationTier
    confidence: float
    reasoning: str


# Quality thresholds by document type
# Higher values require AI generation for quality assurance
QUALITY_THRESHOLDS: dict[str, float] = {
    # Publication-grade (require AI for quality)
    "journal": 8.5,
    "publication": 8.5,
    "manuscript": 8.5,
    # Formal documents (prefer AI but Mermaid acceptable)
    "conference": 8.0,
    "thesis": 8.0,
    "dissertation": 8.0,
    "grant": 8.0,
    # Semi-formal (Mermaid usually sufficient)
    "preprint": 7.5,
    "report": 7.5,
    "technical": 7.5,
    # Informal (Mermaid preferred for speed)
    "poster": 7.0,
    "presentation": 6.5,
    "slides": 6.5,
    "internal": 6.0,
    "draft": 5.0,
    "sketch": 4.0,
    # Default
    "default": 7.5,
}

# Complexity thresholds for Mermaid tier eligibility
MERMAID_MAX_NODES = 10
MERMAID_MAX_EDGES = 15

# Diagram types that Mermaid supports well
MERMAID_SUPPORTED_TYPES: set[str] = set(DIAGRAM_TYPE_TO_TEMPLATES.keys())

# Diagram types that should always use AI generation
# (domain-specific, require specialized rendering)
AI_ONLY_TYPES: set[str] = {
    # Neural network architectures
    "transformer",
    "cnn",
    "rnn",
    "rnn_lstm",
    "lstm",
    "gru",
    "neural_network",
    "autoencoder",
    "gan",
    "vae",
    "diffusion",
    "attention",
    # Biological diagrams
    "pathway",
    "metabolic_pathway",
    "signaling_pathway",
    "regulatory_network",
    "gene_network",
    "protein_interaction",
    "interaction_network",
    # Complex scientific
    "circuit_schematic",
    "circuit",
    "molecular_structure",
    "crystal_structure",
    # Custom positioning required
    "system_architecture",
    "data_flow_diagram",
    "network_topology",
}

# Keywords that suggest AI generation is needed
AI_SUGGESTING_KEYWORDS: list[str] = [
    # Neural network terms
    "transformer",
    "attention",
    "encoder",
    "decoder",
    "cnn",
    "convolutional",
    "rnn",
    "recurrent",
    "lstm",
    "gru",
    "neural",
    "deep learning",
    "machine learning",
    "layer",
    "neuron",
    "activation",
    "embedding",
    # Biology terms
    "pathway",
    "signaling",
    "metabolic",
    "gene",
    "protein",
    "receptor",
    "kinase",
    "phosphorylation",
    "transcription",
    "expression",
    "binding",
    "interaction network",
    # Quality terms
    "publication",
    "journal",
    "figure",
    "manuscript",
    # Complexity indicators
    "complex",
    "detailed",
    "comprehensive",
    "complete",
]

# Keywords that suggest Mermaid is sufficient
MERMAID_SUGGESTING_KEYWORDS: list[str] = [
    "simple",
    "basic",
    "quick",
    "draft",
    "sketch",
    "flowchart",
    "flow chart",
    "process flow",
    "sequence",
    "state machine",
    "state diagram",
    "class diagram",
    "er diagram",
    "entity relationship",
    "timeline",
    "gantt",
    "pie chart",
    "mindmap",
    "mind map",
    "decision tree",
    "consort",
    "prisma",
]


def get_quality_requirement(doc_type: str) -> float:
    """Get minimum quality threshold for a document type.

    Args:
        doc_type: Type of document (e.g., "journal", "presentation", "draft")

    Returns:
        Quality threshold (0-10 scale). Higher values require better quality.

    Example:
        >>> get_quality_requirement("journal")
        8.5
        >>> get_quality_requirement("draft")
        5.0
    """
    return QUALITY_THRESHOLDS.get(doc_type.lower(), QUALITY_THRESHOLDS["default"])


def is_mermaid_compatible(diagram_type: str) -> bool:
    """Check if a diagram type can be rendered with Mermaid.

    Args:
        diagram_type: The type of diagram (e.g., "flowchart", "sequence")

    Returns:
        True if Mermaid has good support for this diagram type

    Example:
        >>> is_mermaid_compatible("flowchart")
        True
        >>> is_mermaid_compatible("neural_network")
        False
    """
    diagram_type_lower = diagram_type.lower()

    # Check if explicitly AI-only
    if diagram_type_lower in AI_ONLY_TYPES:
        return False

    # Check if in Mermaid's supported types
    if diagram_type_lower in MERMAID_SUPPORTED_TYPES:
        return True

    # Check for partial matches with word boundaries
    # e.g., "simple_flowchart" matches "flowchart", but "pipeline" does NOT match "pie"
    for supported in MERMAID_SUPPORTED_TYPES:
        # Check if supported type is a suffix (e.g., "simple_flowchart" ends with "_flowchart")
        if diagram_type_lower.endswith(f"_{supported}"):
            return True
        # Check if supported type is a prefix (e.g., "flowchart_simple" starts with "flowchart_")
        if diagram_type_lower.startswith(f"{supported}_"):
            return True

    return False


def detect_diagram_type(prompt: str) -> str:
    """Detect diagram type from prompt text.

    Uses keyword matching to identify the most likely diagram type
    from the user's description.

    Args:
        prompt: User's diagram description

    Returns:
        Detected diagram type (defaults to "flowchart" if uncertain)

    Example:
        >>> detect_diagram_type("CONSORT flow diagram showing patient enrollment")
        'consort'
        >>> detect_diagram_type("Show the transformer architecture")
        'transformer'
    """
    prompt_lower = prompt.lower()

    # Priority-ordered type detection patterns
    type_patterns: list[tuple[str, list[str]]] = [
        # Study design (high priority - specific terms)
        ("consort", ["consort", "randomized trial", "rct flow"]),
        ("prisma", ["prisma", "systematic review", "literature search"]),
        # Neural networks (high priority - domain specific)
        (
            "transformer",
            ["transformer", "attention mechanism", "self-attention", "bert", "gpt"],
        ),
        ("cnn", ["cnn", "convolutional neural", "convnet"]),
        ("rnn_lstm", ["lstm", "gru", "recurrent neural", "rnn"]),
        ("neural_network", ["neural network", "deep learning", "mlp"]),
        # Biological (high priority - domain specific)
        ("pathway", ["pathway", "signaling", "mapk", "pi3k", "metabolic"]),
        ("regulatory_network", ["regulatory", "transcription factor", "gene network"]),
        (
            "interaction_network",
            ["protein interaction", "ppi", "interaction network"],
        ),
        # Standard diagram types
        ("sequence", ["sequence diagram", "sequencediagram", "message flow"]),
        ("state", ["state machine", "state diagram", "statediagram", "fsm"]),
        ("class", ["class diagram", "classdiagram", "uml class"]),
        ("er", ["er diagram", "entity relationship", "erdiagram", "erd"]),
        ("gantt", ["gantt", "project schedule", "timeline chart"]),
        ("pie", ["pie chart", "pie diagram", "distribution chart"]),
        ("mindmap", ["mindmap", "mind map", "concept map"]),
        ("timeline", ["timeline", "chronology", "history diagram"]),
        ("block", ["block diagram", "block-beta"]),
        ("decision", ["decision tree", "algorithm flowchart", "branching"]),
        # Generic flowchart (lowest priority - catch-all)
        (
            "flowchart",
            [
                "flowchart",
                "flow chart",
                "process flow",
                "workflow",
                "flow diagram",
                "diagram",
            ],
        ),
    ]

    for diagram_type, patterns in type_patterns:
        for pattern in patterns:
            if pattern in prompt_lower:
                return diagram_type

    # Default to flowchart for generic requests
    return "flowchart"


def estimate_edges_from_prompt(prompt: str, estimated_nodes: int) -> int:
    """Estimate number of edges/connections from prompt.

    Uses heuristics based on prompt text and estimated node count.

    Args:
        prompt: User's diagram description
        estimated_nodes: Already-estimated node count

    Returns:
        Estimated edge count

    Example:
        >>> estimate_edges_from_prompt("A → B → C → D", 4)
        3
    """
    prompt_lower = prompt.lower()

    # Count explicit connection indicators
    connection_patterns = [
        r"→|->|-->|—>|⟶",  # Arrow symbols
        r"\bconnects?\s+to\b",  # "connects to"
        r"\blinks?\s+to\b",  # "links to"
        r"\bleads?\s+to\b",  # "leads to"
        r"\bflows?\s+to\b",  # "flows to"
        r"\bthen\b",  # Sequential indicator
    ]

    explicit_count = 0
    for pattern in connection_patterns:
        explicit_count += len(re.findall(pattern, prompt_lower))

    if explicit_count > 0:
        return explicit_count

    # Heuristic: typical diagram has slightly fewer edges than nodes
    # Linear flow: edges = nodes - 1
    # Branching: edges ≈ nodes * 1.2
    # Network: edges ≈ nodes * 1.5

    if "branch" in prompt_lower or "decision" in prompt_lower:
        return int(estimated_nodes * 1.3)
    if "network" in prompt_lower or "mesh" in prompt_lower:
        return int(estimated_nodes * 1.5)

    # Default: assume mostly linear flow
    return max(estimated_nodes - 1, 1)


def _calculate_keyword_score(prompt: str) -> tuple[float, str]:
    """Calculate keyword-based tier preference score.

    Returns a score from -1.0 (strongly prefer Mermaid) to +1.0 (strongly prefer AI),
    along with the key reasoning.

    Args:
        prompt: User's diagram description

    Returns:
        Tuple of (score, reasoning)
    """
    prompt_lower = prompt.lower()

    ai_matches = []
    mermaid_matches = []

    for keyword in AI_SUGGESTING_KEYWORDS:
        if keyword in prompt_lower:
            ai_matches.append(keyword)

    for keyword in MERMAID_SUGGESTING_KEYWORDS:
        if keyword in prompt_lower:
            mermaid_matches.append(keyword)

    ai_count = len(ai_matches)
    mermaid_count = len(mermaid_matches)
    total = ai_count + mermaid_count

    if total == 0:
        return 0.0, "no strong keyword indicators"

    # Score: positive = AI preference, negative = Mermaid preference
    score = (ai_count - mermaid_count) / total

    if ai_count > mermaid_count:
        top_ai = ai_matches[:3]
        return score, f"AI-suggesting keywords: {', '.join(top_ai)}"
    elif mermaid_count > ai_count:
        top_mermaid = mermaid_matches[:3]
        return score, f"Mermaid-suggesting keywords: {', '.join(top_mermaid)}"
    else:
        return score, "mixed keyword indicators"


def analyze_complexity(
    prompt: str,
    doc_type: str = "default",
    force_tier: GenerationTier | None = None,
    diagram_type: str | None = None,
) -> ComplexityAnalysis:
    """Analyze a diagram prompt to determine complexity and recommended tier.

    This is the main entry point for tier selection. It considers:
    - Estimated complexity (node/edge count)
    - Diagram type and Mermaid compatibility
    - Document type quality requirements
    - Keyword indicators in the prompt
    - Explicit tier preferences

    Args:
        prompt: User's diagram description
        doc_type: Document type for quality threshold (e.g., "journal", "draft")
        force_tier: If provided, forces this tier regardless of analysis
        diagram_type: If provided, skips diagram type detection

    Returns:
        ComplexityAnalysis with recommendation and reasoning

    Example:
        >>> analysis = analyze_complexity("Simple 3-step flowchart")
        >>> analysis.recommended_tier
        GenerationTier.MERMAID

        >>> analysis = analyze_complexity(
        ...     "MAPK signaling pathway",
        ...     doc_type="journal"
        ... )
        >>> analysis.recommended_tier
        GenerationTier.AI
    """
    # Detect or use provided diagram type
    detected_type = diagram_type or detect_diagram_type(prompt)

    # Estimate complexity
    estimated_nodes = estimate_nodes_from_prompt(prompt)
    estimated_edges = estimate_edges_from_prompt(prompt, estimated_nodes)

    # Check Mermaid compatibility
    mermaid_ok = is_mermaid_compatible(detected_type)

    # Get quality requirement
    quality_req = get_quality_requirement(doc_type)

    # Calculate keyword score
    keyword_score, keyword_reason = _calculate_keyword_score(prompt)

    # Build reasoning
    reasons: list[str] = []

    # Handle forced tier
    if force_tier is not None:
        return ComplexityAnalysis(
            estimated_nodes=estimated_nodes,
            estimated_edges=estimated_edges,
            diagram_type=detected_type,
            mermaid_compatible=mermaid_ok,
            recommended_tier=force_tier,
            confidence=1.0,
            reasoning=f"Tier forced to {force_tier.value} by user",
        )

    # Decision logic
    recommended_tier = GenerationTier.MERMAID
    confidence = 0.5

    # Factor 1: Mermaid compatibility (strongest factor)
    if not mermaid_ok:
        recommended_tier = GenerationTier.AI
        confidence = 0.95
        reasons.append(f"'{detected_type}' not supported by Mermaid")

    # Factor 2: Complexity thresholds
    elif estimated_nodes > MERMAID_MAX_NODES:
        recommended_tier = GenerationTier.AI
        confidence = max(confidence, 0.8)
        reasons.append(
            f"{estimated_nodes} nodes exceeds Mermaid limit ({MERMAID_MAX_NODES})"
        )
    elif estimated_edges > MERMAID_MAX_EDGES:
        recommended_tier = GenerationTier.AI
        confidence = max(confidence, 0.75)
        reasons.append(
            f"{estimated_edges} edges exceeds Mermaid limit ({MERMAID_MAX_EDGES})"
        )

    # Factor 3: Quality requirements
    elif quality_req >= 8.0:
        # High quality required - prefer AI
        recommended_tier = GenerationTier.AI
        confidence = max(confidence, 0.7)
        reasons.append(
            f"'{doc_type}' requires quality {quality_req}/10 (AI recommended)"
        )

    # Factor 4: Keyword analysis
    elif keyword_score > 0.3:
        # Strong AI keyword indicators
        recommended_tier = GenerationTier.AI
        confidence = max(confidence, 0.6)
        reasons.append(keyword_reason)

    elif keyword_score < -0.3:
        # Strong Mermaid keyword indicators
        recommended_tier = GenerationTier.MERMAID
        confidence = max(confidence, 0.7)
        reasons.append(keyword_reason)

    # Factor 5: Default to Mermaid for simple cases
    else:
        limits = get_limits(detected_type)
        if estimated_nodes <= limits.max_nodes * 0.6:
            recommended_tier = GenerationTier.MERMAID
            confidence = max(confidence, 0.65)
            reasons.append(
                f"Simple {detected_type} ({estimated_nodes} nodes) suitable for Mermaid"
            )
        else:
            # Edge case: moderate complexity
            recommended_tier = GenerationTier.MERMAID
            confidence = 0.55
            reasons.append(
                "Moderate complexity - Mermaid should work, AI available if needed"
            )

    # Special case: Mermaid+AI polish for moderate quality + simple structure
    if (
        recommended_tier == GenerationTier.MERMAID
        and quality_req >= 7.0
        and quality_req < 8.0
        and mermaid_ok
    ):
        # Could benefit from polish
        if "polish" in prompt.lower() or "enhance" in prompt.lower():
            recommended_tier = GenerationTier.MERMAID_PLUS_POLISH
            reasons.append("User requested polish/enhancement")

    reasoning = "; ".join(reasons) if reasons else "Default to Mermaid for simplicity"

    return ComplexityAnalysis(
        estimated_nodes=estimated_nodes,
        estimated_edges=estimated_edges,
        diagram_type=detected_type,
        mermaid_compatible=mermaid_ok,
        recommended_tier=recommended_tier,
        confidence=confidence,
        reasoning=reasoning,
    )


def should_use_mermaid(
    prompt: str,
    doc_type: str = "default",
) -> bool:
    """Quick check if Mermaid tier should be used.

    Convenience function for simple tier decisions.

    Args:
        prompt: User's diagram description
        doc_type: Document type

    Returns:
        True if Mermaid tier is recommended

    Example:
        >>> should_use_mermaid("Simple flowchart: A → B → C")
        True
        >>> should_use_mermaid("Transformer architecture", doc_type="journal")
        False
    """
    analysis = analyze_complexity(prompt, doc_type)
    return analysis.recommended_tier == GenerationTier.MERMAID


def get_tier_summary(tier: GenerationTier) -> dict[str, str | float | bool]:
    """Get summary information about a generation tier.

    Args:
        tier: The generation tier

    Returns:
        Dict with tier characteristics

    Example:
        >>> info = get_tier_summary(GenerationTier.MERMAID)
        >>> info["cost"]
        '$0.00'
    """
    summaries = {
        GenerationTier.MERMAID: {
            "name": "Mermaid (Tier 1)",
            "cost": "$0.00",
            "speed": "~100ms",
            "quality": "Good for drafts/presentations",
            "deterministic": True,
            "description": "Free, instant local rendering. Best for simple diagrams.",
        },
        GenerationTier.AI: {
            "name": "AI Generation (Tier 2)",
            "cost": "$0.02-0.05",
            "speed": "10-30s",
            "quality": "Publication-ready",
            "deterministic": False,
            "description": "AI-powered generation with quality review loop.",
        },
        GenerationTier.MERMAID_PLUS_POLISH: {
            "name": "Mermaid + AI Polish",
            "cost": "$0.01-0.03",
            "speed": "5-15s",
            "quality": "Enhanced presentation",
            "deterministic": False,
            "description": "Mermaid draft with AI enhancement pass.",
        },
    }
    return summaries.get(
        tier,
        {
            "name": "Unknown",
            "cost": "Unknown",
            "speed": "Unknown",
            "quality": "Unknown",
            "deterministic": False,
            "description": "Unknown tier",
        },
    )
