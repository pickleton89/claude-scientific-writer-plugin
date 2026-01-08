#!/usr/bin/env python3
"""Calculate section-specific word count and citation targets."""

import argparse
import json

# Word count proportions by document length
WORD_COUNT_PROPORTIONS = {
    "abstract": {"min": 0.03, "max": 0.05},
    "introduction": {"min": 0.12, "max": 0.18},
    "methods": {"min": 0.18, "max": 0.28},
    "results": {"min": 0.20, "max": 0.30},
    "discussion": {"min": 0.20, "max": 0.30},
    "conclusion": {"min": 0.03, "max": 0.05},
}

# Citation targets by document type
CITATION_TARGETS = {
    "original_research": {
        "introduction": {"min": 8, "max": 15},
        "methods": {"min": 3, "max": 8},
        "results": {"min": 0, "max": 3},
        "discussion": {"min": 10, "max": 20},
        "total": {"min": 30},
    },
    "review_article": {
        "introduction": {"min": 15, "max": 30},
        "methods": {"min": 5, "max": 10},
        "discussion": {"min": 30, "max": 60},
        "total": {"min": 100},
    },
    "case_report": {
        "introduction": {"min": 5, "max": 10},
        "case_presentation": {"min": 0, "max": 2},
        "discussion": {"min": 8, "max": 15},
        "total": {"min": 15},
    },
    "meta_analysis": {
        "introduction": {"min": 10, "max": 20},
        "methods": {"min": 8, "max": 15},
        "results": {"min": 5, "max": 15},
        "discussion": {"min": 15, "max": 30},
        "total": {"min": 50},
    },
    "methods_paper": {
        "introduction": {"min": 8, "max": 15},
        "methods": {"min": 10, "max": 20},
        "results": {"min": 3, "max": 10},
        "discussion": {"min": 8, "max": 15},
        "total": {"min": 35},
    },
}


def get_document_types() -> list[str]:
    """Return list of valid document types."""
    return list(CITATION_TARGETS.keys())


def get_word_count_proportions() -> dict:
    """Return word count proportion mappings."""
    return WORD_COUNT_PROPORTIONS.copy()


def calculate_section_words(total_words: int) -> dict:
    """Calculate word count targets for each section.

    Args:
        total_words: Target total word count for the manuscript

    Returns:
        Dictionary mapping section names to min/max/target word counts
    """
    targets = {}
    for section, proportions in WORD_COUNT_PROPORTIONS.items():
        targets[section] = {
            "min": int(total_words * proportions["min"]),
            "max": int(total_words * proportions["max"]),
            "target": int(total_words * (proportions["min"] + proportions["max"]) / 2),
        }
    return targets


def calculate_citation_targets(document_type: str) -> dict:
    """Get citation targets for document type.

    Args:
        document_type: The type of document (e.g., "original_research")

    Returns:
        Dictionary of citation targets or error if type unknown
    """
    if document_type not in CITATION_TARGETS:
        return {
            "error": f"Unknown document type: {document_type}",
            "valid_types": get_document_types(),
        }
    return CITATION_TARGETS[document_type]


def calculate_display_items(total_words: int) -> dict:
    """Calculate recommended number of figures/tables.

    Args:
        total_words: Target total word count

    Returns:
        Dictionary with min/recommended/max display item counts
    """
    # Rule: ~1 display item per 1000 words
    recommended = max(3, total_words // 1000)
    return {
        "minimum": max(2, recommended - 2),
        "recommended": recommended,
        "maximum": recommended + 3,
        "rule": "Approximately 1 figure/table per 1000 words",
    }


def calculate_all_targets(total_words: int, document_type: str) -> dict:
    """Calculate all manuscript targets.

    Args:
        total_words: Target total word count
        document_type: The type of document

    Returns:
        Complete targets dictionary with all calculations
    """
    return {
        "total_words": total_words,
        "document_type": document_type,
        "section_word_counts": calculate_section_words(total_words),
        "citation_targets": calculate_citation_targets(document_type),
        "display_items": calculate_display_items(total_words),
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate manuscript targets")
    parser.add_argument(
        "--words", "-w", type=int, required=True, help="Target total word count"
    )
    parser.add_argument(
        "--type",
        "-t",
        default="original_research",
        choices=get_document_types(),
        help="Document type",
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = calculate_all_targets(args.words, args.type)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=" * 60)
        print(f"MANUSCRIPT TARGETS ({args.words} words, {args.type})")
        print("=" * 60)

        print("\nSection Word Counts:")
        for section, counts in result["section_word_counts"].items():
            print(
                f"  {section.title()}: {counts['min']}-{counts['max']} words "
                f"(target: {counts['target']})"
            )

        print("\nCitation Targets:")
        citation_targets = result["citation_targets"]
        if "error" not in citation_targets:
            for section, targets in citation_targets.items():
                if "min" in targets:
                    max_str = f"-{targets['max']}" if "max" in targets else "+"
                    print(f"  {section.title()}: {targets['min']}{max_str} citations")

        print(
            f"\nFigures/Tables: {result['display_items']['minimum']}-"
            f"{result['display_items']['maximum']} "
            f"(recommended: {result['display_items']['recommended']})"
        )


if __name__ == "__main__":
    main()
