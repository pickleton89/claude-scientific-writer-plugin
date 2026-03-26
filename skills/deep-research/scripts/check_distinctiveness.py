#!/usr/bin/env python3
"""Check that hypotheses are mechanistically distinct."""

import json
import sys


# Common stopwords to exclude from mechanism term extraction
STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "by",
    "is",
    "are",
    "that",
    "which",
    "for",
    "with",
    "on",
    "at",
    "from",
    "as",
    "be",
    "this",
    "it",
    "its",
    "into",
    "through",
    "via",
}


def normalize_text(text: str) -> list[str]:
    """Normalize text by lowercasing and splitting on common delimiters."""
    return text.lower().replace(",", " ").replace("→", " ").split()


def extract_mechanism_terms(hypothesis: dict) -> set[str]:
    """Extract key terms from hypothesis mechanism."""
    terms = set()

    mechanism = hypothesis.get("mechanism", {})

    # Add causal chain steps
    for step in mechanism.get("causal_chain", []):
        words = normalize_text(step)
        terms.update(words)

    # Add trigger, pathway, outcome
    for field in ["trigger", "pathway", "outcome"]:
        if mechanism.get(field):
            words = normalize_text(mechanism[field])
            terms.update(words)

    # Remove stopwords
    terms -= STOPWORDS

    return terms


def calculate_overlap(terms1: set[str], terms2: set[str]) -> float:
    """Calculate Jaccard similarity between term sets."""
    if not terms1 or not terms2:
        return 0.0
    intersection = len(terms1 & terms2)
    union = len(terms1 | terms2)
    return intersection / union if union > 0 else 0.0


def check_distinctiveness(hypotheses: list[dict], threshold: float = 0.4) -> dict:
    """
    Check pairwise distinctiveness of hypotheses.

    Args:
        hypotheses: List of hypothesis dictionaries
        threshold: Maximum allowed overlap (default 0.4 = 40%)

    Returns:
        Report dictionary with pairwise comparisons and overall status
    """
    report = {
        "hypothesis_count": len(hypotheses),
        "comparisons": [],
        "overall_distinct": True,
        "issues": [],
    }

    # Extract terms for each hypothesis, using index to handle duplicate IDs
    hypothesis_data = []
    for i, h in enumerate(hypotheses):
        h_id = h.get("id", f"H{i+1}")
        terms = extract_mechanism_terms(h)
        hypothesis_data.append((h_id, terms))

    # Pairwise comparisons using indices to avoid duplicate key issues
    for i in range(len(hypothesis_data)):
        for j in range(i + 1, len(hypothesis_data)):
            h1_id, terms1 = hypothesis_data[i]
            h2_id, terms2 = hypothesis_data[j]

            overlap = calculate_overlap(terms1, terms2)
            shared = terms1 & terms2

            comparison = {
                "pair": f"{h1_id} vs {h2_id}",
                "h1_id": h1_id,
                "h2_id": h2_id,
                "overlap_ratio": round(overlap, 3),
                "shared_terms": sorted(list(shared))[:10],  # Limit for readability
                "is_distinct": overlap < threshold,
            }
            report["comparisons"].append(comparison)

            if not comparison["is_distinct"]:
                report["overall_distinct"] = False
                report["issues"].append(
                    f"{h1_id} and {h2_id} share {overlap:.0%} mechanism overlap "
                    f"(threshold: {threshold:.0%}). Shared: {', '.join(sorted(list(shared))[:5])}"
                )

    return report


def check_hypothesis_set(hypothesis_set: dict, threshold: float = 0.4) -> dict:
    """
    Check distinctiveness for a hypothesis set.

    Args:
        hypothesis_set: Dictionary with 'hypotheses' key
        threshold: Maximum allowed overlap (default 0.4 = 40%)

    Returns:
        Report dictionary
    """
    hypotheses = hypothesis_set.get("hypotheses", [])
    return check_distinctiveness(hypotheses, threshold)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: check_distinctiveness.py <hypotheses.json> [threshold]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4

    hypotheses = data.get("hypotheses", [])
    report = check_distinctiveness(hypotheses, threshold)

    status = "✓" if report["overall_distinct"] else "✗"
    print(f"\n{status} Distinctiveness Check (threshold: {threshold:.0%})")
    print(f"  Hypotheses: {report['hypothesis_count']}")
    print(f"  Comparisons: {len(report['comparisons'])}")

    print("\n  Pairwise Analysis:")
    for comp in report["comparisons"]:
        icon = "✓" if comp["is_distinct"] else "✗"
        print(f"    {icon} {comp['pair']}: {comp['overlap_ratio']:.0%} overlap")
        if comp["shared_terms"]:
            print(f"       Shared: {', '.join(comp['shared_terms'][:5])}")

    if report["issues"]:
        print("\n  Issues:")
        for issue in report["issues"]:
            print(f"    ✗ {issue}")

    sys.exit(0 if report["overall_distinct"] else 1)


if __name__ == "__main__":
    main()
