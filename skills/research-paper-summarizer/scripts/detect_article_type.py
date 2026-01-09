#!/usr/bin/env python3
"""
Detect article type from paper abstract/introduction.

Returns suggested article type with confidence score based on
keyword matching against type-specific vocabulary.

Usage:
    python detect_article_type.py abstract.txt
    python detect_article_type.py abstract.txt --verbose
    python detect_article_type.py abstract.txt --json
"""

import argparse
import json
import sys
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.schemas import ArticleType, ArticleTypeResult


# Keywords associated with each article type
# Organized by confidence level: high (3 pts), medium (2 pts), low (1 pt)
TYPE_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "review": {
        "high": [
            "systematic review",
            "meta-analysis",
            "literature review",
            "we reviewed",
            "narrative review",
            "scoping review",
            "umbrella review",
            "systematic literature",
        ],
        "medium": [
            "review of",
            "overview of",
            "synthesis of",
            "survey of literature",
            "examined the literature",
            "published studies",
            "pooled analysis",
            "comprehensive review",
        ],
        "low": [
            "reviewed",
            "summarize",
            "consolidate",
            "evidence synthesis",
        ],
    },
    "compbio": {
        "high": [
            "bioinformatic",
            "computational pipeline",
            "rna-seq",
            "genome-wide",
            "machine learning",
            "deep learning",
            "neural network",
            "algorithm",
            "benchmark",
            "bioinformatics",
        ],
        "medium": [
            "dataset",
            "database",
            "sequencing data",
            "transcriptome",
            "proteome",
            "metabolome",
            "single-cell",
            "multi-omics",
            "high-throughput",
            "differential expression",
        ],
        "low": [
            "computational",
            "in silico",
            "prediction",
            "modeling",
            "pipeline",
            "workflow",
        ],
    },
    "cellmolbio": {
        "high": [
            "mechanism",
            "signaling pathway",
            "molecular basis",
            "in vitro",
            "cell line",
            "western blot",
            "immunoprecipitation",
            "crispr",
            "knockout",
            "molecular mechanism",
        ],
        "medium": [
            "transfection",
            "knockdown",
            "overexpression",
            "mouse model",
            "xenograft",
            "cell culture",
            "protein expression",
            "phosphorylation",
            "immunofluorescence",
            "co-localization",
        ],
        "low": [
            "cells",
            "molecular",
            "protein",
            "gene expression",
            "pathway",
            "receptor",
        ],
    },
    "general": {
        "high": [],  # Default when others don't match
        "medium": [
            "clinical trial",
            "cohort study",
            "case-control",
            "observational",
            "randomized",
            "prospective",
            "retrospective",
            "cross-sectional",
        ],
        "low": [
            "study",
            "research",
            "investigation",
            "analysis",
            "patients",
            "subjects",
        ],
    },
}

# Weights for keyword confidence levels
WEIGHTS = {"high": 3, "medium": 2, "low": 1}

# Confidence scoring thresholds
# A score of 10+ typically indicates strong keyword matches across multiple categories
CONFIDENCE_SCORE_THRESHOLD = 10
# Minimum score needed to make a type classification (below this defaults to "general")
MIN_CLASSIFICATION_SCORE = 3

# Display names for article types
TYPE_DISPLAY_NAMES = {
    "review": "Review Article",
    "compbio": "Computational Biology",
    "cellmolbio": "Cell & Molecular Biology",
    "general": "General Research",
}


def detect_article_type(text: str) -> ArticleTypeResult:
    """
    Detect article type from text using keyword matching.

    Args:
        text: Text to analyze (typically abstract or introduction)

    Returns:
        ArticleTypeResult with detected type, confidence, and breakdown
    """
    text_lower = text.lower()
    scores: dict[str, int] = {}
    matched_keywords: dict[str, list[str]] = {}

    for article_type, keyword_groups in TYPE_KEYWORDS.items():
        score = 0
        matches: list[str] = []

        for level, keywords in keyword_groups.items():
            weight = WEIGHTS[level]
            for keyword in keywords:
                if keyword in text_lower:
                    score += weight
                    matches.append(f"{keyword} ({level})")

        scores[article_type] = score
        matched_keywords[article_type] = matches

    # Find best match
    best_type = max(scores, key=lambda t: scores[t])
    best_score = scores[best_type]

    # Calculate confidence (0-1) based on score relative to threshold
    confidence = min(best_score / CONFIDENCE_SCORE_THRESHOLD, 1.0)

    # If no strong signal, default to general with lower confidence
    if best_score < MIN_CLASSIFICATION_SCORE:
        best_type = "general"
        confidence = 0.5

    # Map to ArticleType enum
    type_mapping = {
        "general": ArticleType.GENERAL,
        "review": ArticleType.REVIEW,
        "compbio": ArticleType.COMPBIO,
        "cellmolbio": ArticleType.CELLMOLBIO,
    }

    return ArticleTypeResult(
        detected_type=type_mapping[best_type],
        confidence=confidence,
        scores=scores,
        matched_keywords=matched_keywords,
    )


def print_result(result: ArticleTypeResult, file_path: str, verbose: bool = False) -> None:
    """Print detection result in readable format."""
    print(f"\n{'=' * 60}")
    print("Article Type Detection")
    print(f"File: {file_path}")
    print(f"{'=' * 60}\n")

    type_name = TYPE_DISPLAY_NAMES.get(result.detected_type.value, result.detected_type.value)
    print(f"Detected Type: {type_name}")
    print(f"Confidence: {result.confidence:.0%}")

    if verbose:
        print("\nScore Breakdown:")
        sorted_types = sorted(result.scores.items(), key=lambda x: x[1], reverse=True)
        for type_key, score in sorted_types:
            display_name = TYPE_DISPLAY_NAMES.get(type_key, type_key)
            print(f"  {display_name}: {score} points")
            if result.matched_keywords.get(type_key):
                for kw in result.matched_keywords[type_key][:5]:
                    print(f"    - '{kw}'")
                if len(result.matched_keywords[type_key]) > 5:
                    remaining = len(result.matched_keywords[type_key]) - 5
                    print(f"    ... and {remaining} more")

    # Recommendation based on confidence
    print("\nRecommendation:")
    if result.confidence >= 0.8:
        print(f"  High confidence - use '{type_name}' template")
    elif result.confidence >= 0.5:
        print(f"  Moderate confidence - verify '{type_name}' is appropriate")
    else:
        print("  Low confidence - manual classification recommended")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Detect article type from text")
    parser.add_argument("file", help="Text file (abstract/introduction)")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed breakdown"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        return 1

    text = Path(args.file).read_text(encoding="utf-8")
    result = detect_article_type(text)

    if args.json:
        output = result.to_dict()
        output["display_name"] = TYPE_DISPLAY_NAMES.get(
            result.detected_type.value, result.detected_type.value
        )
        print(json.dumps(output, indent=2))
    else:
        print_result(result, args.file, verbose=args.verbose)

    return 0


if __name__ == "__main__":
    sys.exit(main())
