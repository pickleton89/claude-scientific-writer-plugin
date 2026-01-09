#!/usr/bin/env python3
"""
Validate executive summary structural compliance.

Checks that the summary follows the exact template structure:
- ## Executive Summary header
- **Key Findings:** section with numbered items
- **Recommendation:** section

More rigorous than keyword-based component detection.

Usage:
    python validate_structure.py <summary_file>
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StructureResult:
    """Result of structural validation."""

    valid: bool
    has_header: bool
    has_findings_section: bool
    has_recommendation: bool
    finding_count: int
    issues: list[str]


def validate_structure(text: str) -> StructureResult:
    """Validate executive summary structure against template."""
    issues = []

    # Check for ## Executive Summary header
    has_header = bool(
        re.search(r"^##\s+Executive Summary", text, re.MULTILINE | re.IGNORECASE)
    )
    if not has_header:
        issues.append("Missing '## Executive Summary' header")

    # Check for **Key Findings:** section
    has_findings = bool(re.search(r"\*\*Key Findings:?\*\*", text, re.IGNORECASE))
    if not has_findings:
        issues.append("Missing '**Key Findings:**' section")

    # Count numbered findings (1. **...**:)
    finding_pattern = r"^\d+\.\s+\*\*[^*]+\*\*:?"
    findings = re.findall(finding_pattern, text, re.MULTILINE)
    finding_count = len(findings)

    if finding_count < 3:
        issues.append(f"Only {finding_count} findings (minimum 3 required)")
    elif finding_count > 5:
        issues.append(f"Too many findings ({finding_count}); maximum is 5")

    # Check for **Recommendation:** section
    has_recommendation = bool(
        re.search(r"\*\*Recommendation:?\*\*", text, re.IGNORECASE)
    )
    if not has_recommendation:
        issues.append("Missing '**Recommendation:**' section")

    # Check component order (Hook before Findings before Recommendation)
    if has_findings and has_recommendation:
        findings_pos = re.search(r"\*\*Key Findings", text, re.IGNORECASE)
        rec_pos = re.search(r"\*\*Recommendation", text, re.IGNORECASE)
        if findings_pos and rec_pos and findings_pos.start() > rec_pos.start():
            issues.append("Findings section should come before Recommendation")

    # Check that Recommendation has specifics
    rec_match = re.search(
        r"\*\*Recommendation:?\*\*:?\s*(.*?)(?=\n\n|\n##|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if rec_match:
        rec_text = rec_match.group(1)
        # Check for action verb
        if not re.search(
            r"\b(approve|implement|proceed|launch|create|develop|hire|invest|authorize|initiate)\b",
            rec_text,
            re.IGNORECASE,
        ):
            issues.append("Recommendation lacks action verb")

    valid = len(issues) == 0

    return StructureResult(
        valid=valid,
        has_header=has_header,
        has_findings_section=has_findings,
        has_recommendation=has_recommendation,
        finding_count=finding_count,
        issues=issues,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Validate executive summary template structure"
    )
    parser.add_argument("file", type=Path, help="Summary file to validate")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    text = args.file.read_text()
    result = validate_structure(text)

    print("\n" + "=" * 60)
    print("STRUCTURE VALIDATION REPORT")
    print("=" * 60)

    checks = [
        ("Executive Summary header", result.has_header),
        ("Key Findings section", result.has_findings_section),
        ("Recommendation section", result.has_recommendation),
        ("Finding count (3-5)", 3 <= result.finding_count <= 5),
    ]

    for name, passed in checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")

    if result.issues:
        print("\nIssues found:")
        for issue in result.issues:
            print(f"  * {issue}")

    print(f"\nOverall: {'VALID' if result.valid else 'INVALID'}")

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
