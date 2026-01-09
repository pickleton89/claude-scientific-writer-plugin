#!/usr/bin/env python3
"""
Automated Database Router for Academic Paper Search

Provides deterministic database selection based on domain keywords,
reducing reliance on LLM interpretation of user intent.

Usage:
    from database_router import select_databases, get_routing_explanation

    # Automatic database selection
    databases = select_databases("CRISPR gene therapy")
    # Returns: ["pubmed"]

    # With user hint
    databases = select_databases("neural networks", user_hint="cs")
    # Returns: ["semantic"]

    # Get explanation
    explanation = get_routing_explanation("deep learning drug discovery")
    # Returns: "Cross-domain: biomedical terms (drug), CS/AI terms (deep, learning)"
"""

from dataclasses import dataclass
from typing import List, Set, Dict, Optional, Tuple
import re


# Domain keyword sets for classification
BIOMEDICAL_TERMS: Set[str] = {
    # Clinical/medical
    "disease", "clinical", "patient", "patients", "drug", "drugs", "therapy",
    "treatment", "diagnosis", "symptom", "symptoms", "medical", "medicine",
    "pharmaceutical", "therapeutic", "therapeutics", "pharmacology",
    "dosage", "efficacy", "toxicity", "adverse", "trial", "trials",

    # Molecular biology
    "gene", "genes", "genetic", "genomic", "genomics", "protein", "proteins",
    "cell", "cells", "cellular", "molecular", "dna", "rna", "mrna",
    "mutation", "mutations", "variant", "variants", "allele", "chromosome",
    "transcription", "translation", "expression", "splicing", "epigenetic",

    # Disease/pathology
    "cancer", "tumor", "tumors", "carcinoma", "melanoma", "leukemia",
    "lymphoma", "metastasis", "oncology", "malignant", "benign",
    "inflammation", "inflammatory", "autoimmune", "infection", "infectious",
    "diabetes", "cardiovascular", "neurological", "neurodegenerative",

    # Biochemistry
    "pathway", "pathways", "receptor", "receptors", "enzyme", "enzymes",
    "kinase", "phosphorylation", "signaling", "metabolic", "metabolism",
    "binding", "ligand", "substrate", "inhibitor", "agonist", "antagonist",

    # Techniques
    "immunotherapy", "chemotherapy", "radiotherapy", "surgery", "surgical",
    "biopsy", "histology", "pathology", "cytology", "microscopy",
    "sequencing", "pcr", "elisa", "western", "blot", "assay",

    # Organisms/models
    "human", "mouse", "mice", "rat", "zebrafish", "drosophila", "yeast",
    "mammalian", "vertebrate", "invertebrate", "primate", "rodent",
}

CS_AI_TERMS: Set[str] = {
    # Machine learning core
    "algorithm", "algorithms", "neural", "network", "networks",
    "deep", "learning", "machine", "transformer", "transformers",
    "attention", "embedding", "embeddings", "encoder", "decoder",
    "autoencoder", "gan", "generative", "adversarial", "diffusion",

    # Model types
    "cnn", "rnn", "lstm", "gru", "bert", "gpt", "llm", "llms",
    "classifier", "classification", "regression", "clustering",
    "segmentation", "detection", "recognition", "prediction",

    # Training/optimization
    "training", "inference", "optimization", "gradient", "backpropagation",
    "loss", "accuracy", "precision", "recall", "f1", "auc", "roc",
    "overfitting", "underfitting", "regularization", "dropout",
    "batch", "epoch", "hyperparameter", "learning rate",

    # Data
    "dataset", "datasets", "benchmark", "benchmarks", "annotation",
    "labeled", "unlabeled", "supervised", "unsupervised", "semi-supervised",
    "reinforcement", "self-supervised", "contrastive", "pretraining",

    # Architecture
    "architecture", "architectures", "layer", "layers", "parameter",
    "parameters", "weight", "weights", "activation", "relu", "softmax",
    "convolution", "convolutional", "pooling", "normalization",

    # Applications
    "nlp", "natural language", "computer vision", "image", "text",
    "speech", "audio", "video", "multimodal", "representation",

    # Software/infrastructure
    "pytorch", "tensorflow", "gpu", "cuda", "distributed", "parallel",
    "scalable", "efficient", "computational", "compute",
}

PREPRINT_INDICATORS: Set[str] = {
    "recent", "latest", "new", "novel", "cutting-edge", "emerging",
    "preprint", "preprints", "unpublished", "arxiv", "biorxiv", "medrxiv",
    "preliminary", "early", "advance", "breakthrough",
}

PHYSICS_MATH_TERMS: Set[str] = {
    "quantum", "physics", "particle", "cosmology", "astrophysics",
    "mathematics", "mathematical", "theorem", "proof", "topology",
    "geometry", "algebra", "analysis", "statistics", "probability",
    "differential", "integral", "equation", "equations",
}

CHEMISTRY_TERMS: Set[str] = {
    "chemical", "chemistry", "synthesis", "reaction", "catalyst",
    "organic", "inorganic", "polymer", "compound", "molecule",
    "spectroscopy", "crystallography", "nmr", "mass spectrometry",
}


@dataclass(frozen=True)
class RoutingResult:
    """Immutable result of database routing decision."""
    databases: tuple  # Immutable tuple of database names
    confidence: float  # 0.0 to 1.0
    explanation: str
    domain: str  # "biomedical", "cs_ai", "cross_domain", "general"
    biomedical_score: int
    cs_score: int
    preprint_requested: bool


def _tokenize_query(query: str) -> Set[str]:
    """
    Tokenize query into lowercase words for matching.

    Handles multi-word terms by also checking bigrams.
    """
    query_lower = query.lower()

    # Single words
    words = set(re.findall(r'\b[a-z]+\b', query_lower))

    # Also check for multi-word terms
    # This catches "deep learning", "machine learning", etc.
    bigrams = set()
    word_list = re.findall(r'\b[a-z]+\b', query_lower)
    for i in range(len(word_list) - 1):
        bigrams.add(f"{word_list[i]} {word_list[i+1]}")

    return words | bigrams


def _calculate_domain_scores(tokens: Set[str]) -> Tuple[int, int, bool]:
    """
    Calculate domain match scores.

    Returns:
        Tuple of (biomedical_score, cs_score, preprint_requested)
    """
    biomedical_score = len(tokens & BIOMEDICAL_TERMS)
    cs_score = len(tokens & CS_AI_TERMS)
    preprint_requested = bool(tokens & PREPRINT_INDICATORS)

    return biomedical_score, cs_score, preprint_requested


def select_databases(
    query: str,
    user_hint: Optional[str] = None,
    include_preprints: Optional[bool] = None
) -> List[str]:
    """
    Deterministically select databases based on query content.

    Args:
        query: The search query text
        user_hint: Optional domain hint ("biomedical", "cs", "comprehensive")
        include_preprints: Force preprint inclusion (True/False) or auto (None)

    Returns:
        List of database identifiers to search

    Examples:
        >>> select_databases("CRISPR gene therapy")
        ['pubmed']

        >>> select_databases("transformer attention mechanism")
        ['semantic']

        >>> select_databases("deep learning for drug discovery")
        ['semantic', 'pubmed']
    """
    result = get_routing_result(query, user_hint, include_preprints)
    return list(result.databases)


def get_routing_result(
    query: str,
    user_hint: Optional[str] = None,
    include_preprints: Optional[bool] = None
) -> RoutingResult:
    """
    Get detailed routing result with explanation.

    Args:
        query: The search query text
        user_hint: Optional domain hint
        include_preprints: Force preprint inclusion (True/False) or auto (None)

    Returns:
        RoutingResult with databases, confidence, and explanation
    """
    tokens = _tokenize_query(query)
    biomedical_score, cs_score, preprint_requested = _calculate_domain_scores(tokens)

    # Override preprint detection if explicitly specified
    if include_preprints is not None:
        preprint_requested = include_preprints

    # Handle explicit user hints first
    if user_hint:
        return _route_with_hint(
            user_hint, preprint_requested, biomedical_score, cs_score
        )

    # Automatic routing based on keyword scores
    return _route_automatic(
        biomedical_score, cs_score, preprint_requested, tokens
    )


def _route_with_hint(
    hint: str,
    preprint_requested: bool,
    biomedical_score: int,
    cs_score: int
) -> RoutingResult:
    """Route based on explicit user hint."""
    hint_lower = hint.lower().strip()

    if hint_lower in ("biomedical", "medical", "clinical", "bio", "pubmed"):
        databases = ["pubmed"]
        if preprint_requested:
            databases.append("biorxiv")
        return RoutingResult(
            databases=tuple(databases),
            confidence=1.0,
            explanation=f"User specified biomedical domain",
            domain="biomedical",
            biomedical_score=biomedical_score,
            cs_score=cs_score,
            preprint_requested=preprint_requested,
        )

    elif hint_lower in ("cs", "ai", "ml", "computer science", "semantic"):
        return RoutingResult(
            databases=("semantic",),
            confidence=1.0,
            explanation="User specified CS/AI domain",
            domain="cs_ai",
            biomedical_score=biomedical_score,
            cs_score=cs_score,
            preprint_requested=preprint_requested,
        )

    elif hint_lower in ("comprehensive", "all", "broad"):
        databases = ["pubmed", "semantic"]
        if preprint_requested:
            databases.insert(1, "biorxiv")
        return RoutingResult(
            databases=tuple(databases),
            confidence=1.0,
            explanation="User requested comprehensive search",
            domain="comprehensive",
            biomedical_score=biomedical_score,
            cs_score=cs_score,
            preprint_requested=preprint_requested,
        )

    elif hint_lower in ("preprint", "preprints", "biorxiv"):
        return RoutingResult(
            databases=("biorxiv", "medrxiv"),
            confidence=1.0,
            explanation="User requested preprint search",
            domain="preprint",
            biomedical_score=biomedical_score,
            cs_score=cs_score,
            preprint_requested=True,
        )

    # Unknown hint - fall back to automatic
    return _route_automatic(biomedical_score, cs_score, preprint_requested, set())


def _route_automatic(
    biomedical_score: int,
    cs_score: int,
    preprint_requested: bool,
    tokens: Set[str]
) -> RoutingResult:
    """Automatic routing based on keyword analysis."""

    # Strong biomedical signal, no CS
    if biomedical_score >= 2 and cs_score == 0:
        databases = ["pubmed"]
        if preprint_requested:
            databases.append("biorxiv")
        confidence = min(0.9, 0.5 + biomedical_score * 0.1)
        return RoutingResult(
            databases=tuple(databases),
            confidence=confidence,
            explanation=f"Biomedical domain ({biomedical_score} matching terms)",
            domain="biomedical",
            biomedical_score=biomedical_score,
            cs_score=cs_score,
            preprint_requested=preprint_requested,
        )

    # Strong CS/AI signal, no biomedical
    if cs_score >= 2 and biomedical_score == 0:
        confidence = min(0.9, 0.5 + cs_score * 0.1)
        return RoutingResult(
            databases=("semantic",),
            confidence=confidence,
            explanation=f"CS/AI domain ({cs_score} matching terms)",
            domain="cs_ai",
            biomedical_score=biomedical_score,
            cs_score=cs_score,
            preprint_requested=preprint_requested,
        )

    # Cross-domain (both biomedical and CS terms present)
    if biomedical_score > 0 and cs_score > 0:
        # Order by dominant domain
        if cs_score >= biomedical_score:
            databases = ["semantic", "pubmed"]
        else:
            databases = ["pubmed", "semantic"]

        if preprint_requested:
            databases.append("biorxiv")

        total_score = biomedical_score + cs_score
        confidence = min(0.85, 0.4 + total_score * 0.05)
        return RoutingResult(
            databases=tuple(databases),
            confidence=confidence,
            explanation=f"Cross-domain: biomedical ({biomedical_score}), CS/AI ({cs_score})",
            domain="cross_domain",
            biomedical_score=biomedical_score,
            cs_score=cs_score,
            preprint_requested=preprint_requested,
        )

    # Weak biomedical signal
    if biomedical_score == 1 and cs_score == 0:
        databases = ["pubmed"]
        if preprint_requested:
            databases.append("biorxiv")
        return RoutingResult(
            databases=tuple(databases),
            confidence=0.6,
            explanation=f"Likely biomedical ({biomedical_score} term)",
            domain="biomedical",
            biomedical_score=biomedical_score,
            cs_score=cs_score,
            preprint_requested=preprint_requested,
        )

    # Weak CS signal
    if cs_score == 1 and biomedical_score == 0:
        return RoutingResult(
            databases=("semantic",),
            confidence=0.6,
            explanation=f"Likely CS/AI ({cs_score} term)",
            domain="cs_ai",
            biomedical_score=biomedical_score,
            cs_score=cs_score,
            preprint_requested=preprint_requested,
        )

    # No domain signals - default to Semantic Scholar (broadest coverage)
    return RoutingResult(
        databases=("semantic",),
        confidence=0.4,
        explanation="No domain-specific terms detected, using Semantic Scholar for broad coverage",
        domain="general",
        biomedical_score=biomedical_score,
        cs_score=cs_score,
        preprint_requested=preprint_requested,
    )


def get_routing_explanation(query: str, user_hint: Optional[str] = None) -> str:
    """
    Get human-readable explanation of routing decision.

    Args:
        query: The search query
        user_hint: Optional domain hint

    Returns:
        Explanation string
    """
    result = get_routing_result(query, user_hint)

    parts = [result.explanation]
    parts.append(f"Selected: {', '.join(result.databases)}")
    parts.append(f"Confidence: {result.confidence:.0%}")

    if result.preprint_requested:
        parts.append("(preprints included)")

    return " | ".join(parts)


def get_matched_terms(query: str) -> Dict[str, List[str]]:
    """
    Get the specific terms that matched each domain.

    Useful for debugging and transparency.

    Args:
        query: The search query

    Returns:
        Dictionary with matched terms per domain
    """
    tokens = _tokenize_query(query)

    return {
        "biomedical": sorted(tokens & BIOMEDICAL_TERMS),
        "cs_ai": sorted(tokens & CS_AI_TERMS),
        "preprint_indicators": sorted(tokens & PREPRINT_INDICATORS),
    }


# CLI support
if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description="Database Router for Paper Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python database_router.py "CRISPR gene therapy"
    python database_router.py "transformer attention" --hint cs
    python database_router.py "deep learning drug discovery" --verbose
        """
    )

    parser.add_argument(
        "query",
        help="Search query to analyze"
    )

    parser.add_argument(
        "--hint", "-H",
        help="Domain hint (biomedical, cs, comprehensive, preprint)"
    )

    parser.add_argument(
        "--preprints", "-p",
        action="store_true",
        help="Include preprint servers"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed analysis"
    )

    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Get routing result
    include_preprints = True if args.preprints else None
    result = get_routing_result(args.query, args.hint, include_preprints)

    if args.json:
        output = {
            "query": args.query,
            "databases": list(result.databases),
            "confidence": result.confidence,
            "domain": result.domain,
            "explanation": result.explanation,
            "scores": {
                "biomedical": result.biomedical_score,
                "cs_ai": result.cs_score,
            },
            "preprint_requested": result.preprint_requested,
        }
        if args.verbose:
            output["matched_terms"] = get_matched_terms(args.query)
        print(json.dumps(output, indent=2))
    else:
        print(f"Query: {args.query}")
        print(f"Databases: {', '.join(result.databases)}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Domain: {result.domain}")
        print(f"Explanation: {result.explanation}")

        if args.verbose:
            matched = get_matched_terms(args.query)
            print(f"\nMatched terms:")
            if matched["biomedical"]:
                print(f"  Biomedical: {', '.join(matched['biomedical'])}")
            if matched["cs_ai"]:
                print(f"  CS/AI: {', '.join(matched['cs_ai'])}")
            if matched["preprint_indicators"]:
                print(f"  Preprint indicators: {', '.join(matched['preprint_indicators'])}")
