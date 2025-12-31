#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Count and verify citations in scientific manuscripts.

Supports multiple citation formats:
- Numbered: [1], [1,2], [1-3], superscript¹²³
- Author-date: (Smith, 2023), (Smith & Jones, 2023), (Smith et al., 2023)
- Narrative: Smith (2023), Smith and Jones (2023)

Usage:
    python count_citations.py <input_file> [--style APA|AMA|Vancouver]
    python count_citations.py <input_file> --by-section

Output: Citation counts per section with pass/fail against targets.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


# Citation targets from SKILL.md
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
}

# Citation patterns by style
CITATION_PATTERNS = {
    "numbered": [
        r"\[(\d+(?:\s*[-–,]\s*\d+)*)\]",  # [1], [1,2], [1-3]
        r"(?<!\w)(\d+)(?:\s*[-–,]\s*(\d+))*(?=\s|[.,;)]|$)",  # Superscript-style numbers
    ],
    "author_date": [
        r"\(([A-Z][a-z]+(?:\s+(?:&|and)\s+[A-Z][a-z]+)?(?:\s+et\s+al\.)?),?\s*(\d{4}[a-z]?)\)",  # (Smith, 2023)
        r"([A-Z][a-z]+(?:\s+(?:&|and)\s+[A-Z][a-z]+)?(?:\s+et\s+al\.)?)\s*\((\d{4}[a-z]?)\)",  # Smith (2023)
    ],
}

# Section header patterns
SECTION_PATTERNS = {
    "abstract": r"(?i)^#+\s*abstract",
    "introduction": r"(?i)^#+\s*introduction|^#+\s*background",
    "methods": r"(?i)^#+\s*method|^#+\s*materials?\s+and\s+method|^#+\s*experimental",
    "results": r"(?i)^#+\s*results?|^#+\s*findings",
    "discussion": r"(?i)^#+\s*discussion|^#+\s*interpretation",
    "conclusion": r"(?i)^#+\s*conclusion|^#+\s*summary",
    "references": r"(?i)^#+\s*references?|^#+\s*bibliography|^#+\s*literature\s+cited",
}


def detect_citation_style(text: str) -> str:
    """Auto-detect the citation style used in the text."""
    numbered_count = len(re.findall(r"\[\d+\]", text))
    author_date_count = len(re.findall(r"\([A-Z][a-z]+.*?\d{4}\)", text))

    if numbered_count > author_date_count:
        return "numbered"
    elif author_date_count > 0:
        return "author_date"
    return "numbered"  # Default


def extract_citations(text: str, style: str = "auto") -> list[dict]:
    """Extract all citations from text with positions."""
    if style == "auto":
        style = detect_citation_style(text)

    citations = []
    patterns = CITATION_PATTERNS.get(style, CITATION_PATTERNS["numbered"])

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            citations.append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "style": style,
            })

    # Deduplicate overlapping citations
    citations.sort(key=lambda x: x["start"])
    deduped = []
    last_end = -1
    for cit in citations:
        if cit["start"] >= last_end:
            deduped.append(cit)
            last_end = cit["end"]

    return deduped


def split_into_sections(text: str) -> dict[str, str]:
    """Split manuscript into sections based on headers."""
    sections = {}
    lines = text.split("\n")
    current_section = "preamble"
    current_content = []

    for line in lines:
        section_found = None
        for section_name, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, line):
                section_found = section_name
                break

        if section_found:
            if current_content:
                sections[current_section] = "\n".join(current_content)
            current_section = section_found
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections[current_section] = "\n".join(current_content)

    return sections


def count_unique_citations(citations: list[dict]) -> int:
    """Count unique citation references."""
    unique = set()
    for cit in citations:
        # Extract reference numbers or author-year
        text = cit["text"]
        if cit["style"] == "numbered":
            # Extract all numbers from [1,2,3] or [1-5] format
            numbers = re.findall(r"\d+", text)
            for num in numbers:
                unique.add(int(num))
            # Handle ranges
            ranges = re.findall(r"(\d+)\s*[-–]\s*(\d+)", text)
            for start, end in ranges:
                for n in range(int(start), int(end) + 1):
                    unique.add(n)
        else:
            # Author-date: use the full citation text as key
            unique.add(text.lower())

    return len(unique)


def analyze_manuscript(text: str, style: str = "auto", document_type: str = "original_research") -> dict:
    """Analyze citations in manuscript by section."""
    sections = split_into_sections(text)
    detected_style = style if style != "auto" else detect_citation_style(text)

    results = {
        "detected_style": detected_style,
        "document_type": document_type,
        "sections": {},
        "total_citations": 0,
        "unique_citations": 0,
    }

    all_citations = []

    for section_name, section_text in sections.items():
        if section_name in ["preamble", "references"]:
            continue

        citations = extract_citations(section_text, detected_style)
        unique_count = count_unique_citations(citations)
        all_citations.extend(citations)

        results["sections"][section_name] = {
            "citation_count": len(citations),
            "unique_citations": unique_count,
            "word_count": len(section_text.split()),
        }

    results["total_citations"] = len(all_citations)
    results["unique_citations"] = count_unique_citations(all_citations)

    return results


def evaluate_citations(analysis: dict) -> dict:
    """Evaluate citation counts against targets."""
    doc_type = analysis["document_type"]
    targets = CITATION_TARGETS.get(doc_type, CITATION_TARGETS["original_research"])

    evaluation = {
        "overall_status": "PASS",
        "checks": {},
        "recommendations": [],
    }

    # Check each section
    for section_name, section_data in analysis["sections"].items():
        if section_name in targets:
            target = targets[section_name]
            count = section_data["unique_citations"]

            if "min" in target and count < target["min"]:
                status = "LOW"
                evaluation["overall_status"] = "NEEDS_ATTENTION"
                evaluation["recommendations"].append(
                    f"{section_name.title()}: Add {target['min'] - count} more citations (current: {count}, minimum: {target['min']})"
                )
            elif "max" in target and count > target["max"]:
                status = "HIGH"
                evaluation["recommendations"].append(
                    f"{section_name.title()}: Consider reducing citations (current: {count}, recommended max: {target['max']})"
                )
            else:
                status = "OK"

            evaluation["checks"][section_name] = {
                "status": status,
                "count": count,
                "target": target,
            }

    # Check total
    total_target = targets.get("total", {})
    total_count = analysis["unique_citations"]

    if "min" in total_target and total_count < total_target["min"]:
        evaluation["overall_status"] = "FAIL"
        evaluation["checks"]["total"] = {
            "status": "FAIL",
            "count": total_count,
            "target": total_target,
        }
        evaluation["recommendations"].insert(
            0,
            f"Total citations ({total_count}) below minimum ({total_target['min']}) for {doc_type.replace('_', ' ')}"
        )
    else:
        evaluation["checks"]["total"] = {
            "status": "OK",
            "count": total_count,
            "target": total_target,
        }

    return evaluation


def main():
    parser = argparse.ArgumentParser(
        description="Count and verify citations in scientific manuscripts."
    )
    parser.add_argument("input_file", help="Path to manuscript file (Markdown or plain text)")
    parser.add_argument(
        "--style", "-s",
        choices=["auto", "numbered", "author_date"],
        default="auto",
        help="Citation style (default: auto-detect)"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["original_research", "review_article"],
        default="original_research",
        help="Document type for target evaluation (default: original_research)"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON only")
    parser.add_argument("--by-section", "-b", action="store_true", help="Show detailed section breakdown")

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8")

    # Analyze and evaluate
    analysis = analyze_manuscript(text, args.style, args.type)
    evaluation = evaluate_citations(analysis)

    report = {
        "analysis": analysis,
        "evaluation": evaluation,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Human-readable output
        print("=" * 60)
        print("CITATION COUNT REPORT")
        print("=" * 60)
        print(f"\nDetected style: {analysis['detected_style']}")
        print(f"Document type: {analysis['document_type'].replace('_', ' ').title()}")
        print(f"\nTotal citations: {analysis['total_citations']}")
        print(f"Unique references: {analysis['unique_citations']}")
        print(f"\nOverall Status: {evaluation['overall_status']}")

        if args.by_section:
            print("\n" + "-" * 40)
            print("SECTION BREAKDOWN")
            print("-" * 40)

            for section, data in analysis["sections"].items():
                check = evaluation["checks"].get(section, {})
                status = check.get("status", "N/A")
                status_icon = {"OK": "+", "LOW": "!", "HIGH": "~", "N/A": " "}[status]
                print(f"[{status_icon}] {section.title()}: {data['unique_citations']} citations ({data['word_count']} words)")

        if evaluation["recommendations"]:
            print("\n" + "-" * 40)
            print("RECOMMENDATIONS")
            print("-" * 40)
            for rec in evaluation["recommendations"]:
                print(f"  - {rec}")

    # Exit with appropriate code
    sys.exit(0 if evaluation["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
