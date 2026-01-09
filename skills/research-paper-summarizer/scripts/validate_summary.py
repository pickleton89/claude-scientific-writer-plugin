#!/usr/bin/env python3
"""
Summary Validation Script.

Validates completed summary files against quality criteria.
Returns pass/fail with detailed check results.

Usage:
    python validate_summary.py summary.md
    python validate_summary.py summary.md --strict
    python validate_summary.py summary.md --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.schemas import (
    ValidationResult,
    SectionMarker,
    MarkerStatus,
    SummaryValidationReport,
)
from utils.statistics import extract_statistics


def get_section_markers(content: str) -> list[SectionMarker]:
    """Extract all section markers from content."""
    pattern = r"<!-- (SECTION|SUBSECTION): (\w+) (PENDING|COMPLETE|SKIPPED) -->"
    markers = []
    for match in re.finditer(pattern, content):
        marker_type, name, status = match.groups()
        markers.append(
            SectionMarker(
                name=name,
                marker_type=marker_type.lower(),
                status=MarkerStatus(status.lower()),
                position=match.start(),
            )
        )
    return markers


def validate_no_pending_sections(content: str) -> ValidationResult:
    """Check that no sections or subsections are still pending."""
    # Match both SECTION and SUBSECTION markers with PENDING status
    pending_count = len(
        re.findall(r"<!-- (?:SECTION|SUBSECTION): \w+ PENDING -->", content)
    )
    return ValidationResult(
        name="no_pending_sections",
        passed=pending_count == 0,
        message=f"Found {pending_count} PENDING sections/subsections"
        if pending_count
        else "All sections complete",
        severity="error",
    )


def validate_executive_summary(content: str) -> ValidationResult:
    """Check that executive summary has content."""
    exec_match = re.search(
        r"## 1\. Executive Summary\s+(.+?)(?=\n## |\n<!-- SECTION)", content, re.DOTALL
    )
    has_exec = exec_match is not None and len(exec_match.group(1).strip()) > 50
    return ValidationResult(
        name="has_executive_summary",
        passed=has_exec,
        message="Executive summary present"
        if has_exec
        else "Executive summary missing or too short (<50 chars)",
        severity="error",
    )


def validate_statistics_content(content: str, min_stats: int = 3) -> ValidationResult:
    """Check that summary contains sufficient statistics."""
    stats = extract_statistics(content)
    stat_count = len(stats)
    return ValidationResult(
        name="has_statistics",
        passed=stat_count >= min_stats,
        message=f"Found {stat_count} statistical values"
        if stat_count >= min_stats
        else f"Only {stat_count} stats found (need {min_stats}+)",
        severity="error",
    )


def validate_figure_references(content: str, min_refs: int = 2) -> ValidationResult:
    """Check that summary references figures/tables."""
    fig_refs = re.findall(r"(?:Figure|Fig\.?|Table)\s+\d+[A-Za-z]?", content, re.I)
    ref_count = len(fig_refs)
    has_refs = ref_count >= min_refs

    if ref_count == 0:
        severity = "error"
    elif ref_count < min_refs:
        severity = "warning"
    else:
        severity = "info"

    return ValidationResult(
        name="has_figure_refs",
        passed=has_refs,
        message=f"Found {ref_count} figure/table references",
        severity=severity,
    )


def validate_limitations(content: str) -> ValidationResult:
    """Check that limitations section has content."""
    lim_match = re.search(
        r"### Limitations\s+(.+?)(?=\n### |\n## |\n<!-- )", content, re.DOTALL
    )
    has_lims = lim_match is not None and len(lim_match.group(1).strip()) > 20
    return ValidationResult(
        name="has_limitations",
        passed=has_lims,
        message="Limitations documented"
        if has_lims
        else "Limitations section empty or missing",
        severity="warning",
    )


def validate_sample_sizes(content: str) -> ValidationResult:
    """Check that sample sizes are specified."""
    sample_sizes = re.findall(r"[nN]\s*=\s*\d+", content)
    has_sizes = len(sample_sizes) >= 1
    return ValidationResult(
        name="has_sample_sizes",
        passed=has_sizes,
        message=f"Found {len(sample_sizes)} sample size specifications",
        severity="warning",
    )


def validate_quotes(content: str) -> ValidationResult:
    """Check for author quotes."""
    quotes = re.findall(r'"[^"]{20,}"', content)
    has_quotes = len(quotes) >= 1
    return ValidationResult(
        name="has_quotes",
        passed=has_quotes,
        message=f"Found {len(quotes)} author quotes",
        severity="info",
    )


def validate_synthesis(content: str) -> ValidationResult:
    """Check that synthesis section has content."""
    synth_match = re.search(
        r"## 10\. One-Paragraph Synthesis\s+(.+?)(?=\n---|\Z)", content, re.DOTALL
    )
    has_synth = synth_match is not None and len(synth_match.group(1).strip()) > 100
    return ValidationResult(
        name="has_synthesis",
        passed=has_synth,
        message="Synthesis paragraph present"
        if has_synth
        else "Synthesis section incomplete (<100 chars)",
        severity="warning",
    )


def validate_no_placeholders(content: str) -> ValidationResult:
    """Check that no placeholder text remains."""
    placeholders = re.findall(r"\{\{[A-Z_]+\}\}", content)
    no_placeholders = len(placeholders) == 0
    return ValidationResult(
        name="no_placeholders",
        passed=no_placeholders,
        message=f"Found {len(placeholders)} unfilled placeholders"
        if placeholders
        else "No placeholders remaining",
        severity="error",
    )


def validate_word_count(content: str, min_words: int = 500) -> ValidationResult:
    """Check minimum word count."""
    # Remove markdown syntax for word count
    clean_content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    clean_content = re.sub(r"```.*?```", "", clean_content, flags=re.DOTALL)
    clean_content = re.sub(r"#+ ", "", clean_content)
    words = len(clean_content.split())

    has_enough = words >= min_words
    return ValidationResult(
        name="word_count",
        passed=has_enough,
        message=f"Word count: {words}" if has_enough else f"Only {words} words (need {min_words}+)",
        severity="warning" if not has_enough else "info",
    )


def validate_methods_section(content: str) -> ValidationResult:
    """Check that methods section has key components."""
    methods_match = re.search(
        r"## \d+\. (?:Methods|Methodology)\s+(.+?)(?=\n## |\Z)", content, re.DOTALL
    )
    if not methods_match:
        return ValidationResult(
            name="has_methods",
            passed=False,
            message="Methods section not found",
            severity="error",
        )

    methods_content = methods_match.group(1)
    has_content = len(methods_content.strip()) > 100
    return ValidationResult(
        name="has_methods",
        passed=has_content,
        message="Methods section present" if has_content else "Methods section too brief",
        severity="error" if not has_content else "info",
    )


def validate_summary(file_path: str, strict: bool = False) -> SummaryValidationReport:
    """
    Validate a completed summary file.

    Args:
        file_path: Path to the summary markdown file
        strict: If True, warnings count as failures

    Returns:
        SummaryValidationReport with all check results
    """
    content = Path(file_path).read_text(encoding="utf-8")

    report = SummaryValidationReport(summary_path=file_path)

    # Get markers
    report.markers = get_section_markers(content)
    report.pending_count = sum(
        1 for m in report.markers if m.status == MarkerStatus.PENDING
    )
    report.complete_count = sum(
        1 for m in report.markers if m.status == MarkerStatus.COMPLETE
    )

    # Get statistics
    stats = extract_statistics(content)
    report.statistics = stats
    report.stat_count = len(stats)

    # Content metrics
    report.figure_ref_count = len(
        re.findall(r"(?:Figure|Fig\.?|Table)\s+\d+[A-Za-z]?", content, re.I)
    )
    report.quote_count = len(re.findall(r'"[^"]{20,}"', content))
    report.placeholder_count = len(re.findall(r"\{\{[A-Z_]+\}\}", content))

    # Run all checks
    checks = [
        validate_no_pending_sections(content),
        validate_executive_summary(content),
        validate_statistics_content(content),
        validate_figure_references(content),
        validate_limitations(content),
        validate_sample_sizes(content),
        validate_quotes(content),
        validate_synthesis(content),
        validate_no_placeholders(content),
        validate_word_count(content),
        validate_methods_section(content),
    ]

    for check in checks:
        report.add_check(check)

    # Calculate score
    report.calculate_score()

    # In strict mode, warnings count as failures
    if strict:
        warning_fails = sum(
            1 for c in report.checks if not c.passed and c.severity == "warning"
        )
        if warning_fails > 0:
            report.valid = False

    return report


def print_report(report: SummaryValidationReport) -> None:
    """Print validation report in readable format."""
    status = "PASS" if report.valid else "FAIL"
    print(f"\n{'=' * 60}")
    print(f"Summary Validation: {status}")
    print(f"File: {report.summary_path}")
    print(f"Score: {report.score:.0%} ({sum(1 for c in report.checks if c.passed)}/{len(report.checks)} checks)")
    print(f"{'=' * 60}\n")

    # Check results
    print("Checks:")
    for check in report.checks:
        if check.passed:
            icon = "[OK]  "
        elif check.severity == "error":
            icon = "[FAIL]"
        elif check.severity == "warning":
            icon = "[WARN]"
        else:
            icon = "[INFO]"
        print(f"  {icon} {check.name}: {check.message}")

    # Summary statistics
    print("\nContent Metrics:")
    print(f"  Statistics found: {report.stat_count}")
    print(f"  Figure references: {report.figure_ref_count}")
    print(f"  Author quotes: {report.quote_count}")

    # Marker status
    if report.markers:
        print("\nSection Markers:")
        print(f"  Complete: {report.complete_count}")
        print(f"  Pending: {report.pending_count}")

    # Errors and warnings
    errors = sum(1 for c in report.checks if not c.passed and c.severity == "error")
    warnings = sum(1 for c in report.checks if not c.passed and c.severity == "warning")
    print(f"\nErrors: {errors}, Warnings: {warnings}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate research paper summary")
    parser.add_argument("file", help="Path to summary markdown file")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        return 1

    report = validate_summary(args.file, strict=args.strict)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_report(report)

    return 0 if report.valid else 1


if __name__ == "__main__":
    sys.exit(main())
