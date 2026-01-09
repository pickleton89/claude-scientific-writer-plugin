#!/usr/bin/env python3
"""
Preprocess source document before executive summary generation.

Extracts metrics and validates completeness:
- Word count (for 10% length validation)
- Incomplete markers (TBD, TODO, PLACEHOLDER)
- Section structure analysis
- Existing quantification detection

Usage:
    python preprocess_source.py <source_file>

Output:
    JSON with source metrics for downstream validation
"""

import argparse
import json
import re
import sys
from pathlib import Path


def count_words(text: str) -> int:
    """Count words excluding markdown syntax."""
    text = re.sub(r"```[\s\S]*?```", "", text)  # Remove code blocks
    text = re.sub(r"`[^`]+`", "", text)  # Remove inline code
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # Remove links
    text = re.sub(r"[*_#>|]", "", text)  # Remove formatting
    return len(re.findall(r"\b\w+\b", text))


def detect_incomplete_markers(text: str) -> list[dict]:
    """Find TBD, TODO, PLACEHOLDER markers indicating incomplete content."""
    markers = []
    patterns = [
        (r"\b(TBD|TBC)\b", "TBD marker"),
        (r"\b(TODO|FIXME)\b", "TODO marker"),
        (r"\b(PLACEHOLDER|INSERT|FILL IN)\b", "Placeholder text"),
        (r"\[.*?\.\.\.\]", "Bracketed ellipsis"),
        (r"_{3,}", "Blank line placeholder"),
    ]

    for pattern, marker_type in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            # Find line number
            line_num = text[: match.start()].count("\n") + 1
            markers.append({"type": marker_type, "text": match.group(), "line": line_num})

    return markers


def analyze_sections(text: str) -> dict:
    """Analyze document section structure."""
    h1_count = len(re.findall(r"^#\s+", text, re.MULTILINE))
    h2_count = len(re.findall(r"^##\s+", text, re.MULTILINE))
    h3_count = len(re.findall(r"^###\s+", text, re.MULTILINE))

    # Detect empty sections (header followed by another header or end)
    empty_sections = len(re.findall(r"^##[^\n]+\n\s*\n(?=##|\Z)", text, re.MULTILINE))

    return {
        "h1_count": h1_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "total_sections": h1_count + h2_count + h3_count,
        "empty_sections": empty_sections,
    }


def extract_quantification(text: str) -> list[str]:
    """Extract quantified statements from source."""
    patterns = [
        r"\d+%",  # percentages
        r"\$[\d,]+(?:\.\d{2})?[KMB]?",  # dollar amounts
        r"\d+\.\d+",  # decimals
        r"\b\d{1,3}(?:,\d{3})+\b",  # comma-formatted numbers (e.g., 1,234,567)
        r"\b\d{2,}\b",  # large numbers without commas (10+)
    ]

    quantities = []
    for pattern in patterns:
        quantities.extend(re.findall(pattern, text))

    return list(set(quantities))


def assess_completeness(text: str, markers: list, sections: dict) -> dict:
    """Assess overall document completeness."""
    word_count = count_words(text)

    # Scoring
    issues = []
    score = 100

    if markers:
        score -= 20 * len(markers)
        issues.append(f"{len(markers)} incomplete marker(s) found")

    if sections["empty_sections"] > 0:
        score -= 15 * sections["empty_sections"]
        issues.append(f"{sections['empty_sections']} empty section(s)")

    if word_count < 500:
        score -= 10
        issues.append("Document very short (<500 words)")

    score = max(0, score)

    if score >= 80:
        status = "READY"
    elif score >= 50:
        status = "WARN"
    else:
        status = "INCOMPLETE"

    return {"status": status, "score": score, "issues": issues}


def preprocess_source(text: str) -> dict:
    """Run all preprocessing checks on source document."""
    word_count = count_words(text)
    markers = detect_incomplete_markers(text)
    sections = analyze_sections(text)
    quantities = extract_quantification(text)
    completeness = assess_completeness(text, markers, sections)

    return {
        "word_count": word_count,
        "recommended_summary_length": int(word_count * 0.10),
        "max_summary_length": int(word_count * 0.15),
        "incomplete_markers": markers,
        "sections": sections,
        "quantification_found": quantities,
        "quantification_count": len(quantities),
        "completeness": completeness,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess source document for executive summary"
    )
    parser.add_argument("file", type=Path, help="Source document to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    text = args.file.read_text()
    result = preprocess_source(text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 60)
        print("SOURCE DOCUMENT ANALYSIS")
        print("=" * 60)
        print(f"\nWord count: {result['word_count']}")
        print(f"Recommended summary: <={result['recommended_summary_length']} words (10%)")
        print(f"Maximum summary: <={result['max_summary_length']} words (15%)")
        print(f"\nSections: {result['sections']['total_sections']} total")
        print(f"Quantification found: {result['quantification_count']} metrics")

        print(f"\n--- Completeness: {result['completeness']['status']} ---")
        if result["completeness"]["issues"]:
            for issue in result["completeness"]["issues"]:
                print(f"  * {issue}")

        if result["incomplete_markers"]:
            print("\nIncomplete markers found:")
            for marker in result["incomplete_markers"]:
                print(f"  Line {marker['line']}: {marker['type']} - '{marker['text']}'")

        print()

    # Exit code based on completeness
    if result["completeness"]["status"] == "INCOMPLETE":
        sys.exit(2)
    elif result["completeness"]["status"] == "WARN":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
