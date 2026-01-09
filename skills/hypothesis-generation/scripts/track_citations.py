#!/usr/bin/env python3
"""Track and validate citation requirements."""

import json
import re
import sys

# Thresholds from SKILL.md
TOTAL_CITATIONS_MIN = 40
TOTAL_CITATIONS_TARGET = 50
MAIN_TEXT_CITATIONS_MIN = 10
MAIN_TEXT_CITATIONS_TARGET = 15
RECENT_PAPERS_MIN_PERCENT = 60  # Papers from last 5 years


def extract_citations_from_hypothesis_set(hypothesis_set: dict) -> dict:
    """
    Extract all citations from structured hypothesis data.

    Returns:
        Dictionary with citation lists by source
    """
    citations = {"main_text": set(), "appendix": set(), "all": set()}

    for h in hypothesis_set.get("hypotheses", []):
        # Main text citations (from evidence in hypothesis boxes)
        for e in h.get("supporting_evidence", []):
            cit = e.get("citation", "").strip()
            if cit:
                citations["main_text"].add(cit)
                citations["all"].add(cit)

        # Conflicting evidence also counts as main text
        for e in h.get("conflicting_evidence", []):
            cit = e.get("citation", "").strip()
            if cit:
                citations["main_text"].add(cit)
                citations["all"].add(cit)

        # Additional appendix citations
        for e in h.get("appendix_evidence", []):
            cit = e.get("citation", "").strip()
            if cit:
                citations["appendix"].add(cit)
                citations["all"].add(cit)

    return {k: list(v) for k, v in citations.items()}


def extract_year(citation: str) -> int | None:
    """Extract publication year from citation string."""
    # Match patterns like (2023), 2023, et al. 2023
    patterns = [
        r"\((\d{4})\)",  # (2023)
        r"(\d{4})[,\.\)]",  # 2023, or 2023. or 2023)
        r"et al\.?\s*(\d{4})",  # et al. 2023
    ]
    for pattern in patterns:
        match = re.search(pattern, citation)
        if match:
            year = int(match.group(1))
            if 1900 < year < 2100:
                return year
    return None


def analyze_citations(citations: dict, current_year: int = 2026) -> dict:
    """
    Analyze citation list against requirements.

    Returns:
        Analysis report dictionary
    """
    all_cits = citations.get("all", [])
    main_cits = citations.get("main_text", [])

    # Extract years
    years = [extract_year(c) for c in all_cits]
    years = [y for y in years if y is not None]

    recent_cutoff = current_year - 5
    recent_count = sum(1 for y in years if y >= recent_cutoff)
    recent_percent = (recent_count / len(years) * 100) if years else 0

    report = {
        "counts": {
            "total": len(all_cits),
            "main_text": len(main_cits),
            "appendix_only": len(citations.get("appendix", [])),
        },
        "thresholds": {
            "total_meets_min": len(all_cits) >= TOTAL_CITATIONS_MIN,
            "total_meets_target": len(all_cits) >= TOTAL_CITATIONS_TARGET,
            "main_text_meets_min": len(main_cits) >= MAIN_TEXT_CITATIONS_MIN,
            "main_text_meets_target": len(main_cits) >= MAIN_TEXT_CITATIONS_TARGET,
            "recent_meets_min": recent_percent >= RECENT_PAPERS_MIN_PERCENT,
        },
        "recency": {
            "papers_with_year": len(years),
            "recent_count": recent_count,
            "recent_percent": round(recent_percent, 1),
        },
        "gaps": {
            "total_needed": max(0, TOTAL_CITATIONS_MIN - len(all_cits)),
            "main_text_needed": max(0, MAIN_TEXT_CITATIONS_MIN - len(main_cits)),
        },
        "overall_valid": True,
    }

    # Overall validity
    report["overall_valid"] = (
        report["thresholds"]["total_meets_min"]
        and report["thresholds"]["main_text_meets_min"]
    )

    return report


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: track_citations.py <hypotheses.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        hypothesis_set = json.load(f)

    citations = extract_citations_from_hypothesis_set(hypothesis_set)
    report = analyze_citations(citations)

    valid = report["overall_valid"]
    print(f"\n{'✓' if valid else '✗'} Citation Analysis")

    print("\n  Counts:")
    print(
        f"    Total: {report['counts']['total']} "
        f"(min: {TOTAL_CITATIONS_MIN}, target: {TOTAL_CITATIONS_TARGET})"
    )
    print(
        f"    Main text: {report['counts']['main_text']} "
        f"(min: {MAIN_TEXT_CITATIONS_MIN}, target: {MAIN_TEXT_CITATIONS_TARGET})"
    )
    print(f"    Appendix: {report['counts']['appendix_only']}")

    print("\n  Recency (last 5 years):")
    print(
        f"    {report['recency']['recent_count']}/{report['recency']['papers_with_year']} "
        f"papers ({report['recency']['recent_percent']}%)"
    )
    threshold_met = report["thresholds"]["recent_meets_min"]
    print(
        f"    Threshold: ≥{RECENT_PAPERS_MIN_PERCENT}% {'✓' if threshold_met else '✗'}"
    )

    if report["gaps"]["total_needed"] > 0 or report["gaps"]["main_text_needed"] > 0:
        print("\n  Gaps:")
        if report["gaps"]["total_needed"] > 0:
            print(
                f"    ✗ Need {report['gaps']['total_needed']} more citations for minimum"
            )
        if report["gaps"]["main_text_needed"] > 0:
            print(
                f"    ✗ Need {report['gaps']['main_text_needed']} more main text citations"
            )

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
