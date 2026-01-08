#!/usr/bin/env python3
"""Validate IMRAD structure in scientific manuscripts."""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

IMRAD_SECTIONS = ["abstract", "introduction", "methods", "results", "discussion"]

SECTION_PATTERNS = {
    "abstract": r"(?i)^#+\s*abstract",
    "introduction": r"(?i)^#+\s*(introduction|background)",
    "methods": r"(?i)^#+\s*(methods?|materials?\s+and\s+methods?|methodology|experimental)",
    "results": r"(?i)^#+\s*(results?|findings)",
    "discussion": r"(?i)^#+\s*discussion",
    "conclusion": r"(?i)^#+\s*(conclusion|conclusions|summary)",
    "references": r"(?i)^#+\s*(references?|bibliography|literature\s+cited)",
    "acknowledgments": r"(?i)^#+\s*(acknowledgments?|acknowledgements?)",
}


@dataclass
class StructureValidation:
    found_sections: list[str]
    missing_sections: list[str]
    section_order_correct: bool
    extra_sections: list[str]
    status: str
    recommendations: list[str]


def get_section_patterns() -> dict[str, str]:
    """Return the section pattern mappings."""
    return SECTION_PATTERNS.copy()


def get_imrad_sections() -> list[str]:
    """Return the standard IMRAD section list."""
    return IMRAD_SECTIONS.copy()


def find_sections(text: str) -> dict[str, int]:
    """Find all sections and their line numbers.

    Args:
        text: The manuscript text to analyze

    Returns:
        Dictionary mapping section names to their line numbers
    """
    sections = {}
    lines = text.split("\n")

    for i, line in enumerate(lines):
        for section_name, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, line):
                if section_name not in sections:  # First occurrence
                    sections[section_name] = i

    return sections


def validate_imrad_structure(text: str) -> StructureValidation:
    """Validate IMRAD structure in manuscript.

    Args:
        text: The manuscript text to validate

    Returns:
        StructureValidation dataclass with validation results
    """
    found = find_sections(text)
    found_names = list(found.keys())

    # Check for required sections
    missing = [s for s in IMRAD_SECTIONS if s not in found_names]

    # Check order (only for sections that are present)
    present_imrad = [s for s in IMRAD_SECTIONS if s in found_names]
    found_imrad = [s for s in found_names if s in IMRAD_SECTIONS]
    order_correct = present_imrad == found_imrad

    # Identify extra sections (not in standard IMRAD)
    extra = [s for s in found_names if s not in IMRAD_SECTIONS]

    # Generate recommendations
    recommendations = []
    if missing:
        recommendations.append(f"Add missing sections: {', '.join(missing)}")
    if not order_correct:
        recommendations.append(
            f"Reorder sections to follow IMRAD: {' → '.join(IMRAD_SECTIONS)}"
        )
    if "conclusion" not in found_names and "discussion" in found_names:
        recommendations.append(
            "Consider adding a Conclusion section (or include in Discussion)"
        )

    # Determine status
    if not missing and order_correct:
        status = "PASS"
    elif len(missing) <= 1 and order_correct:
        status = "ACCEPTABLE"
    else:
        status = "FAIL"

    return StructureValidation(
        found_sections=found_names,
        missing_sections=missing,
        section_order_correct=order_correct,
        extra_sections=extra,
        status=status,
        recommendations=recommendations,
    )


def main():
    parser = argparse.ArgumentParser(description="Validate IMRAD structure")
    parser.add_argument("input_file", help="Path to manuscript file")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    text = Path(args.input_file).read_text(encoding="utf-8")
    result = validate_imrad_structure(text)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print("=" * 60)
        print("IMRAD STRUCTURE VALIDATION")
        print("=" * 60)
        print(f"\nStatus: {result.status}")
        print(f"\nFound sections: {', '.join(result.found_sections)}")
        if result.missing_sections:
            print(f"Missing sections: {', '.join(result.missing_sections)}")
        print(
            f"Section order correct: {'Yes' if result.section_order_correct else 'No'}"
        )
        if result.extra_sections:
            print(f"Additional sections: {', '.join(result.extra_sections)}")
        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")

    sys.exit(0 if result.status in ["PASS", "ACCEPTABLE"] else 1)


if __name__ == "__main__":
    main()
