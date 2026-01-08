#!/usr/bin/env python3
"""
Validate Format Script
Check if document meets venue-specific formatting requirements.

Usage:
    python validate_format.py --file my_paper.pdf --venue "Nature" --check-all
    python validate_format.py --file my_paper.pdf --venue "NeurIPS" --check page-count,margins
    python validate_format.py --file my_paper.pdf --venue "PLOS ONE" --report validation_report.txt
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from venue_database import get_venue, VenueSpec
from venue_resolver import resolve_venue_id


@dataclass
class ValidationResult:
    """Result of a validation check."""

    status: Literal["pass", "fail", "warn", "skip", "info"]
    message: str
    details: Optional[str] = None


def get_pdf_info(pdf_path: Path) -> Optional[dict[str, str]]:
    """Extract information from PDF using pdfinfo."""
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        info: dict[str, str] = {}
        for line in result.stdout.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()

        return info
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError:
        return None


def extract_text(pdf_path: Path) -> Optional[str]:
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def check_page_count(pdf_path: Path, venue: VenueSpec) -> ValidationResult:
    """Check if page count is within limit."""
    pdf_info = get_pdf_info(pdf_path)

    if not pdf_info:
        return ValidationResult(
            status="skip", message="Could not determine page count (pdfinfo not found)"
        )

    try:
        pages = int(pdf_info.get("Pages", 0))
    except (ValueError, TypeError):
        return ValidationResult(
            status="skip", message="Could not parse page count from PDF"
        )

    limit = venue.formatting.page_limit

    if limit is None:
        return ValidationResult(
            status="pass", message=f"No page limit. Document has {pages} pages."
        )

    if pages <= limit:
        return ValidationResult(
            status="pass", message=f"Page count OK: {pages}/{limit} pages"
        )
    else:
        return ValidationResult(
            status="fail",
            message=f"Page count exceeded: {pages}/{limit} pages",
            details=f"Reduce by {pages - limit} page(s)",
        )


def check_margins(pdf_path: Path, venue: VenueSpec) -> ValidationResult:
    """Check if margins meet requirements."""
    req_margins = venue.formatting.margins_cm

    if not req_margins:
        return ValidationResult(status="skip", message="No margin requirements specified")

    # This is a simplified check - accurate margin analysis requires PDF parsing
    margin_str = ", ".join(f"{k}: {v}cm" for k, v in req_margins.items())
    return ValidationResult(
        status="info",
        message=f"Required margins: {margin_str}",
        details="Manual verification recommended",
    )


def check_fonts(pdf_path: Path, venue: VenueSpec) -> ValidationResult:
    """Check fonts in PDF."""
    try:
        result = subprocess.run(
            ["pdffonts", str(pdf_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        fonts_found: list[str] = []
        for line in result.stdout.split("\n")[2:]:  # Skip header
            if line.strip():
                parts = line.split()
                if parts:
                    fonts_found.append(parts[0])

        req_font = venue.formatting.font_family
        req_size = venue.formatting.font_size

        unique_fonts = list(set(fonts_found))
        message = f"Fonts found: {', '.join(unique_fonts)}"
        details = f"Required: {req_font}"
        if req_size:
            details += f" {req_size}pt minimum"

        # Check if required font family is present
        font_match = any(req_font.lower() in f.lower() for f in unique_fonts)
        if font_match:
            return ValidationResult(status="pass", message=message, details=details)
        else:
            return ValidationResult(
                status="warn",
                message=message,
                details=f"Expected {req_font} font family",
            )

    except FileNotFoundError:
        return ValidationResult(status="skip", message="pdffonts not available")
    except subprocess.CalledProcessError:
        return ValidationResult(status="skip", message="Could not extract font information")


def check_citation_format(pdf_path: Path, venue: VenueSpec) -> ValidationResult:
    """Validate citation format matches venue requirements."""
    expected = venue.formatting.citation_style
    if not expected or expected == "any":
        return ValidationResult(status="skip", message="No citation style specified")

    text = extract_text(pdf_path)
    if not text:
        return ValidationResult(status="skip", message="Could not extract text for citation check")

    patterns = {
        "superscript": r"[a-zA-Z]\d{1,3}(?:,\s*\d{1,3})*\s",  # Text followed by numbers
        "numbered": r"\[\d{1,3}(?:[-,]\s*\d{1,3})*\]",  # [1], [2,3], [1-3]
        "author-year": r"\([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s*\d{4}[a-z]?\)",  # (Smith, 2023)
    }

    if expected not in patterns:
        return ValidationResult(status="skip", message=f"Unknown citation style: {expected}")

    pattern = patterns[expected]
    matches = re.findall(pattern, text)

    if len(matches) >= 3:  # Expect at least a few citations
        return ValidationResult(
            status="pass",
            message=f"Found {len(matches)} citations matching {expected} style",
        )
    else:
        return ValidationResult(
            status="warn",
            message=f"Few/no citations found matching {expected} style ({len(matches)} found)",
            details=f"Expected style: {expected}",
        )


def check_abstract_structure(pdf_path: Path, venue: VenueSpec) -> ValidationResult:
    """Check if abstract matches venue structure requirements."""
    abstract_spec = venue.abstract
    style = abstract_spec.style
    max_words = abstract_spec.max_words
    sections = abstract_spec.structured_sections

    text = extract_text(pdf_path)
    if not text:
        return ValidationResult(status="skip", message="Could not extract text for abstract check")

    results: list[str] = []

    # Try to extract abstract
    abstract_match = re.search(
        r"(?:abstract|ABSTRACT)[:\s]*(.+?)(?=\n\n|\n[A-Z]{2,}|\nIntroduction|\n1\s|\nKeywords)",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if not abstract_match:
        return ValidationResult(
            status="info",
            message="Could not locate abstract for analysis",
        )

    abstract_text = abstract_match.group(1).strip()
    word_count = len(abstract_text.split())

    # Word count check
    if max_words:
        if word_count > max_words:
            results.append(f"Abstract too long: {word_count}/{max_words} words")
        else:
            results.append(f"Abstract length OK: {word_count}/{max_words} words")

    # Structure check (for structured abstracts)
    if style == "structured" and sections:
        missing = []
        for section in sections:
            if not re.search(rf"\b{section}\b", abstract_text, re.IGNORECASE):
                missing.append(section)
        if missing:
            results.append(f"Missing abstract sections: {', '.join(missing)}")
        else:
            results.append("All required abstract sections present")

    if not results:
        return ValidationResult(status="skip", message="No abstract requirements to check")

    has_issues = any("too long" in r.lower() or "missing" in r.lower() for r in results)
    return ValidationResult(
        status="fail" if has_issues else "pass",
        message="\n".join(results),
    )


def check_anonymization(pdf_path: Path, venue: VenueSpec) -> ValidationResult:
    """Check if document is properly anonymized for double-blind review."""
    if not venue.requirements.anonymization:
        return ValidationResult(status="skip", message="Anonymization not required")

    text = extract_text(pdf_path)
    if not text:
        return ValidationResult(status="skip", message="Could not extract text for anonymization check")

    violations: list[str] = []

    # Self-citations with "our previous work", "we previously"
    self_ref_patterns = [
        r"\b(our previous|we previously|our earlier|in our)\b",
        r"\bin \[?\d+\]?,? we\b",
    ]
    for pattern in self_ref_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append("Self-referential language detected")
            break

    # GitHub/institution URLs that might reveal identity
    if re.search(r"github\.com/[a-zA-Z0-9_-]+/", text):
        violations.append("GitHub repository URL may reveal identity")

    # Author names in acknowledgments
    if re.search(r"acknowledge.*\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", text, re.IGNORECASE):
        violations.append("Possible author names in acknowledgments")

    # Institution names after "at" or "from"
    # This is a heuristic - may have false positives
    if re.search(
        r"\b(?:at|from)\s+(?:University|Institute|Lab|Laboratory|College)\s+of",
        text,
        re.IGNORECASE,
    ):
        violations.append("Institution affiliation may be present")

    if violations:
        return ValidationResult(
            status="warn",
            message="Potential anonymization issues found",
            details="\n".join(f"  - {v}" for v in violations),
        )
    else:
        return ValidationResult(
            status="pass",
            message="No obvious anonymization issues detected",
        )


def check_contribution_list(pdf_path: Path, venue: VenueSpec) -> ValidationResult:
    """Check for contribution list (required for ML conferences)."""
    if not venue.requirements.contribution_list:
        return ValidationResult(status="skip", message="Contribution list not required")

    text = extract_text(pdf_path)
    if not text:
        return ValidationResult(status="skip", message="Could not extract text")

    # Look for numbered/bulleted contribution statements
    patterns = [
        r"(?:our|the)\s+contributions?\s+(?:are|include)[:\s]",
        r"we\s+(?:make|present)\s+the\s+following\s+contributions?",
        r"contributions?[:\s]*\n\s*[-\d\*]",
        r"summary\s+of\s+contributions?",
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return ValidationResult(
                status="pass",
                message="Contribution list found in document",
            )

    return ValidationResult(
        status="warn",
        message="No contribution list found",
        details=f"{venue.full_name} papers typically include explicit contribution bullets",
    )


def check_graphical_abstract(pdf_path: Path, venue: VenueSpec) -> ValidationResult:
    """Check if graphical abstract is present (required for some journals)."""
    if not venue.requirements.graphical_abstract:
        return ValidationResult(status="skip", message="Graphical abstract not required")

    text = extract_text(pdf_path)
    if not text:
        return ValidationResult(status="skip", message="Could not extract text")

    # Look for graphical abstract indicators
    patterns = [
        r"graphical\s+abstract",
        r"visual\s+abstract",
        r"toc\s+graphic",
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return ValidationResult(
                status="info",
                message="Graphical abstract reference found (verify image quality separately)",
            )

    return ValidationResult(
        status="warn",
        message="No graphical abstract detected",
        details=f"{venue.full_name} requires a graphical abstract",
    )


def validate_document(
    pdf_path: Path,
    venue_query: str,
    checks: list[str],
) -> dict[str, ValidationResult]:
    """Validate document against venue requirements."""

    # Resolve venue
    venue_id = resolve_venue_id(venue_query)
    if not venue_id:
        # Fall back to simple normalization
        venue_id = venue_query.lower().replace(" ", "_")

    venue = get_venue(venue_id)
    if not venue:
        return {
            "error": ValidationResult(
                status="fail",
                message=f"Unknown venue: {venue_query}",
                details="Use --list-venues to see available venues",
            )
        }

    results: dict[str, ValidationResult] = {}

    # Map check names to functions
    check_funcs = {
        "page-count": check_page_count,
        "margins": check_margins,
        "fonts": check_fonts,
        "citations": check_citation_format,
        "abstract": check_abstract_structure,
        "anonymization": check_anonymization,
        "contribution-list": check_contribution_list,
        "graphical-abstract": check_graphical_abstract,
    }

    # Run requested checks
    run_all = "all" in checks
    for name, func in check_funcs.items():
        if run_all or name in checks:
            results[name] = func(pdf_path, venue)

    return results


def print_results(
    pdf_path: Path,
    venue_name: str,
    results: dict[str, ValidationResult],
) -> None:
    """Print validation results to console."""
    print(f"\n{'=' * 60}")
    print(f"VALIDATING: {pdf_path.name}")
    print(f"VENUE: {venue_name}")
    print(f"{'=' * 60}\n")

    status_icons = {
        "pass": "[PASS]",
        "fail": "[FAIL]",
        "warn": "[WARN]",
        "skip": "[SKIP]",
        "info": "[INFO]",
    }

    for check_name, result in results.items():
        icon = status_icons[result.status]
        print(f"{check_name.upper()}: {icon}")
        print(f"  {result.message}")
        if result.details:
            for line in result.details.split("\n"):
                print(f"  {line}")
        print()

    # Summary
    failures = sum(1 for r in results.values() if r.status == "fail")
    warnings = sum(1 for r in results.values() if r.status == "warn")
    passes = sum(1 for r in results.values() if r.status == "pass")

    print(f"{'=' * 60}")
    if failures == 0:
        if warnings > 0:
            print(f"VALIDATION PASSED WITH WARNINGS ({passes} pass, {warnings} warn)")
        else:
            print(f"VALIDATION PASSED ({passes} checks)")
    else:
        print(f"VALIDATION FAILED ({failures} fail, {warnings} warn)")
    print(f"{'=' * 60}\n")


def generate_report(
    pdf_path: Path,
    venue_name: str,
    results: dict[str, ValidationResult],
    report_path: Path,
) -> None:
    """Generate validation report to file."""

    with open(report_path, "w") as f:
        f.write("Validation Report\n")
        f.write(f"{'=' * 60}\n\n")
        f.write(f"File: {pdf_path}\n")
        f.write(f"Venue: {venue_name}\n")
        f.write(f"Date: {datetime.now().isoformat()}\n\n")

        for check_name, result in results.items():
            f.write(f"{check_name.upper()}:\n")
            f.write(f"  Status: {result.status}\n")
            f.write(f"  {result.message}\n")
            if result.details:
                f.write(f"  Details: {result.details}\n")
            f.write("\n")

        failures = sum(1 for r in results.values() if r.status == "fail")
        f.write(f"\nSummary: {'PASSED' if failures == 0 else 'FAILED'}\n")

    print(f"Report saved to: {report_path}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate document formatting for venue requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file my_paper.pdf --venue "Nature" --check-all
  %(prog)s --file my_paper.pdf --venue "NeurIPS" --check page-count,fonts,anonymization
  %(prog)s --file proposal.pdf --venue "NSF" --report validation.txt

Available checks:
  page-count        Check page count against venue limit
  margins           Check margin requirements
  fonts             Check font family and size
  citations         Check citation format style
  abstract          Check abstract length and structure
  anonymization     Check for double-blind violations
  contribution-list Check for explicit contributions (ML venues)
  graphical-abstract Check for graphical abstract (Cell Press)
        """,
    )

    parser.add_argument("--file", type=str, required=True, help="PDF file to validate")
    parser.add_argument("--venue", type=str, required=True, help="Target venue")
    parser.add_argument(
        "--check",
        type=str,
        default="all",
        help="Checks to perform (comma-separated, or 'all')",
    )
    parser.add_argument("--check-all", action="store_true", help="Perform all checks")
    parser.add_argument("--report", type=str, help="Save report to file")
    parser.add_argument(
        "--list-venues", action="store_true", help="List available venues"
    )

    args = parser.parse_args()

    # List venues if requested
    if args.list_venues:
        from venue_database import list_venues, get_venue as get_venue_spec

        print("Available venues:")
        for vid in list_venues():
            v = get_venue_spec(vid)
            if v:
                print(f"  {vid}: {v.full_name} ({v.type})")
        return

    # Check file exists
    pdf_path = Path(args.file)
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        return

    # Parse checks
    if args.check_all:
        checks = ["all"]
    else:
        checks = [c.strip() for c in args.check.split(",")]

    # Validate
    results = validate_document(pdf_path, args.venue, checks)

    # Print results
    print_results(pdf_path, args.venue, results)

    # Generate report if requested
    if args.report and results:
        generate_report(pdf_path, args.venue, results, Path(args.report))


if __name__ == "__main__":
    main()
