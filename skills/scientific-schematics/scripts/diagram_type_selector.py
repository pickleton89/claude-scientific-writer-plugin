"""Deterministic diagram type selection.

Converts prose-based decision trees into code-based lookup for
consistent diagram type recommendations based on purpose and domain.

Usage:
    >>> from diagram_type_selector import select_diagram_type, infer_type_from_prompt
    >>> select_diagram_type("study_design", "clinical_trial")
    'consort'
    >>> result = infer_type_from_prompt("CONSORT participant flow")
    >>> print(result.diagram_type, result.confidence)
    'consort' 0.9
"""

from __future__ import annotations

from typing import Literal, NamedTuple


# Purpose categories
Purpose = Literal["study_design", "ml_architecture", "biology", "systems", "abstract"]

# Domain subcategories
Domain = Literal[
    # Study design
    "clinical_trial",
    "systematic_review",
    "experimental",
    # ML
    "attention",
    "image",
    "sequence",
    "general",
    # Biology
    "signaling",
    "metabolic",
    "gene",
    "protein",
    # Systems
    "software",
    "data",
    "electronics",
    "hardware",
    # Abstract
    "theory",
    "classification",
    "comparison",
]


# Type mapping: (purpose, domain) -> diagram_type
TYPE_MAP: dict[tuple[Purpose, Domain | None], str] = {
    # Study Design
    ("study_design", "clinical_trial"): "consort",
    ("study_design", "systematic_review"): "prisma",
    ("study_design", "experimental"): "methods_flowchart",
    ("study_design", None): "methods_flowchart",
    # ML Architecture
    ("ml_architecture", "attention"): "transformer",
    ("ml_architecture", "image"): "cnn",
    ("ml_architecture", "sequence"): "rnn_lstm",
    ("ml_architecture", "general"): "neural_network",
    ("ml_architecture", None): "neural_network",
    # Biology
    ("biology", "signaling"): "pathway",
    ("biology", "metabolic"): "metabolic_pathway",
    ("biology", "gene"): "regulatory_network",
    ("biology", "protein"): "interaction_network",
    ("biology", None): "pathway",
    # Systems
    ("systems", "software"): "system_architecture",
    ("systems", "data"): "data_flow_diagram",
    ("systems", "electronics"): "circuit_schematic",
    ("systems", "hardware"): "block_diagram",
    ("systems", None): "block_diagram",
    # Abstract
    ("abstract", "theory"): "conceptual_framework",
    ("abstract", "classification"): "hierarchy_diagram",
    ("abstract", "comparison"): "venn_diagram",
    ("abstract", None): "conceptual_framework",
}


class TypeInference(NamedTuple):
    """Result of inferring diagram type from prompt."""

    diagram_type: str
    confidence: float
    detected_keywords: list[str]


# High-confidence keyword matches (0.9 confidence)
HIGH_CONFIDENCE_KEYWORDS: dict[str, list[str]] = {
    "consort": [
        "consort",
        "participant flow",
        "randomized controlled",
        "rct flow",
        "clinical trial flow",
    ],
    "prisma": [
        "prisma",
        "systematic review",
        "screening records",
        "meta-analysis flow",
        "literature search flow",
    ],
    "transformer": [
        "transformer",
        "self-attention",
        "encoder-decoder",
        "multi-head attention",
        "attention mechanism",
    ],
    "cnn": [
        "cnn",
        "convolutional neural",
        "convnet",
        "conv layer",
        "pooling layer",
    ],
    "rnn_lstm": [
        "rnn",
        "lstm",
        "recurrent neural",
        "gru",
        "sequence model",
    ],
    "pathway": [
        "signaling pathway",
        "mapk",
        "pi3k/akt",
        "phosphorylation cascade",
        "kinase cascade",
    ],
    "metabolic_pathway": [
        "metabolic pathway",
        "metabolism",
        "glycolysis",
        "krebs cycle",
        "tca cycle",
    ],
    "circuit_schematic": [
        "circuit schematic",
        "op-amp",
        "resistor capacitor",
        "transistor circuit",
        "ic pinout",
    ],
}

# Medium-confidence keyword matches (0.6-0.7 confidence)
MEDIUM_CONFIDENCE_KEYWORDS: dict[str, list[str]] = {
    "flowchart": [
        "flowchart",
        "flow chart",
        "process flow",
        "workflow",
        "decision flow",
    ],
    "methods_flowchart": [
        "methods",
        "experimental design",
        "study design",
        "protocol flow",
    ],
    "neural_network": [
        "neural network",
        "deep learning",
        "layers",
        "neurons",
        "activation",
    ],
    "pathway": [
        "pathway",
        "signaling",
        "cascade",
        "signal transduction",
    ],
    "regulatory_network": [
        "gene regulation",
        "transcription",
        "regulatory",
        "gene network",
    ],
    "interaction_network": [
        "protein interaction",
        "ppi",
        "interactome",
        "binding",
    ],
    "system_architecture": [
        "architecture",
        "system diagram",
        "components",
        "microservices",
    ],
    "data_flow_diagram": [
        "data flow",
        "dfd",
        "data pipeline",
        "etl",
    ],
    "block_diagram": [
        "block diagram",
        "blocks",
        "modules",
        "subsystem",
    ],
    "conceptual_framework": [
        "conceptual",
        "theoretical framework",
        "model diagram",
        "concept map",
    ],
    "hierarchy_diagram": [
        "hierarchy",
        "tree structure",
        "taxonomy",
        "classification tree",
    ],
    "venn_diagram": [
        "venn",
        "overlap",
        "intersection",
        "set diagram",
    ],
}

# Low-confidence fallback patterns (0.3-0.4 confidence)
LOW_CONFIDENCE_PATTERNS: dict[str, list[str]] = {
    "flowchart": ["steps", "process", "procedure"],
    "block_diagram": ["diagram", "chart", "visual"],
    "neural_network": ["ml", "ai", "model"],
    "pathway": ["biological", "cellular", "molecular"],
}


def select_diagram_type(purpose: Purpose, domain: Domain | None = None) -> str:
    """Deterministic diagram type selection based on purpose and domain.

    Args:
        purpose: High-level category
            - study_design: Clinical trials, systematic reviews, experiments
            - ml_architecture: Neural networks, transformers, CNNs
            - biology: Signaling pathways, metabolic networks
            - systems: Software architecture, data flow, circuits
            - abstract: Conceptual frameworks, hierarchies, Venn diagrams
        domain: Optional specific domain within the purpose category

    Returns:
        Recommended diagram type string

    Examples:
        >>> select_diagram_type("study_design", "clinical_trial")
        'consort'
        >>> select_diagram_type("ml_architecture", "attention")
        'transformer'
        >>> select_diagram_type("biology")
        'pathway'
    """
    # Try exact match first
    result = TYPE_MAP.get((purpose, domain))
    if result:
        return result

    # Fall back to purpose-only match
    result = TYPE_MAP.get((purpose, None))
    if result:
        return result

    # Ultimate fallback
    return "block_diagram"


def infer_type_from_prompt(prompt: str) -> TypeInference:
    """Infer diagram type from free-form prompt text.

    Args:
        prompt: User's natural language description

    Returns:
        TypeInference with diagram_type, confidence (0-1), and detected keywords
    """
    prompt_lower = prompt.lower()
    detected_keywords: list[str] = []

    # Check high-confidence keywords first
    for dtype, keywords in HIGH_CONFIDENCE_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in prompt_lower]
        if matches:
            detected_keywords.extend(matches)
            return TypeInference(
                diagram_type=dtype,
                confidence=0.9,
                detected_keywords=detected_keywords,
            )

    # Check medium-confidence keywords
    for dtype, keywords in MEDIUM_CONFIDENCE_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in prompt_lower]
        if matches:
            detected_keywords.extend(matches)
            return TypeInference(
                diagram_type=dtype,
                confidence=0.65,
                detected_keywords=detected_keywords,
            )

    # Check low-confidence patterns
    for dtype, patterns in LOW_CONFIDENCE_PATTERNS.items():
        matches = [p for p in patterns if p in prompt_lower]
        if matches:
            detected_keywords.extend(matches)
            return TypeInference(
                diagram_type=dtype,
                confidence=0.35,
                detected_keywords=detected_keywords,
            )

    # No matches - return default with very low confidence
    return TypeInference(
        diagram_type="block_diagram",
        confidence=0.2,
        detected_keywords=[],
    )


def get_diagram_type_info(diagram_type: str) -> dict[str, str | list[str]]:
    """Get detailed information about a diagram type.

    Args:
        diagram_type: The diagram type to look up

    Returns:
        Dictionary with description, purpose, domains, and examples
    """
    info_map: dict[str, dict[str, str | list[str]]] = {
        "consort": {
            "description": "CONSORT participant flow diagram for clinical trials",
            "purpose": "study_design",
            "domains": ["clinical_trial"],
            "examples": [
                "Randomized controlled trial participant flow",
                "Clinical study enrollment and follow-up",
            ],
        },
        "prisma": {
            "description": "PRISMA flow diagram for systematic reviews",
            "purpose": "study_design",
            "domains": ["systematic_review"],
            "examples": [
                "Literature screening and selection process",
                "Meta-analysis study flow",
            ],
        },
        "transformer": {
            "description": "Transformer architecture diagram with attention",
            "purpose": "ml_architecture",
            "domains": ["attention"],
            "examples": [
                "BERT encoder architecture",
                "GPT decoder stack",
            ],
        },
        "cnn": {
            "description": "Convolutional neural network architecture",
            "purpose": "ml_architecture",
            "domains": ["image"],
            "examples": [
                "ResNet architecture",
                "Image classification CNN",
            ],
        },
        "pathway": {
            "description": "Biological signaling pathway",
            "purpose": "biology",
            "domains": ["signaling"],
            "examples": [
                "MAPK signaling cascade",
                "PI3K/AKT pathway",
            ],
        },
        "block_diagram": {
            "description": "Generic block diagram for system components",
            "purpose": "systems",
            "domains": ["hardware", "software"],
            "examples": [
                "System component overview",
                "Module interaction diagram",
            ],
        },
    }

    return info_map.get(
        diagram_type,
        {
            "description": f"Generic {diagram_type} diagram",
            "purpose": "abstract",
            "domains": [],
            "examples": [],
        },
    )


def get_all_purposes() -> list[Purpose]:
    """Get list of all supported purpose categories."""
    return ["study_design", "ml_architecture", "biology", "systems", "abstract"]


def get_domains_for_purpose(purpose: Purpose) -> list[Domain]:
    """Get list of domains for a given purpose."""
    domain_map: dict[Purpose, list[Domain]] = {
        "study_design": ["clinical_trial", "systematic_review", "experimental"],
        "ml_architecture": ["attention", "image", "sequence", "general"],
        "biology": ["signaling", "metabolic", "gene", "protein"],
        "systems": ["software", "data", "electronics", "hardware"],
        "abstract": ["theory", "classification", "comparison"],
    }
    return domain_map.get(purpose, [])


def get_all_diagram_types() -> list[str]:
    """Get list of all unique diagram types."""
    return sorted(set(TYPE_MAP.values()))
