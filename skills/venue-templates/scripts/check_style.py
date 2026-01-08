#!/usr/bin/env python3
"""
Style Compliance Checker
Validate document style against venue requirements.

Usage:
    python check_style.py --file paper.tex --venue nature
    python check_style.py --file paper.pdf --venue neurips --check-all
    python check_style.py --text "We show that..." --venue nature --check voice
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from venue_database import get_venue, VenueSpec
from venue_resolver import resolve_venue_id


@dataclass
class StyleIssue:
    """A detected style issue."""

    category: str
    severity: Literal["error", "warning", "info"]
    message: str
    location: str = ""
    suggestion: str = ""


class StyleChecker:
    """Check document style compliance against venue requirements."""

    def __init__(self, venue_spec: VenueSpec):
        """Initialize with venue specification."""
        self.spec = venue_spec

    def check_all(self, text: str) -> list[StyleIssue]:
        """Run all style checks."""
        issues: list[StyleIssue] = []
        issues.extend(self.check_voice(text))
        issues.extend(self.check_jargon_level(text))
        issues.extend(self.check_abstract_style(text))
        issues.extend(self.check_contribution_format(text))
        issues.extend(self.check_hedging_language(text))
        issues.extend(self.check_first_person(text))
        return issues

    def check_voice(self, text: str) -> list[StyleIssue]:
        """Check active vs passive voice usage."""
        issues: list[StyleIssue] = []
        style = self.spec.style

        # Count passive constructions
        passive_patterns = [
            r"\b(?:is|are|was|were|been|being)\s+\w+ed\b",
            r"\b(?:is|are|was|were)\s+(?:shown|found|observed|demonstrated|reported|performed|conducted|analyzed|measured)\b",
        ]
        passive_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in passive_patterns)

        # Count active first-person constructions
        active_patterns = [
            r"\bwe\s+(?:show|find|demonstrate|report|present|propose|develop|introduce|describe|analyze|observe)\b",
        ]
        active_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in active_patterns)

        total = passive_count + active_count
        if total == 0:
            return issues

        passive_ratio = passive_count / total

        if style.voice == "active" and passive_ratio > 0.6:
            issues.append(
                StyleIssue(
                    category="voice",
                    severity="warning",
                    message=f"High passive voice usage ({passive_ratio:.0%}) - {self.spec.full_name} prefers active voice",
                    suggestion="Consider rewriting passive constructions with 'we show/find/demonstrate'",
                )
            )
        elif style.voice == "passive" and passive_ratio < 0.4:
            issues.append(
                StyleIssue(
                    category="voice",
                    severity="info",
                    message=f"Low passive voice usage ({passive_ratio:.0%}) - {self.spec.full_name} traditionally uses passive voice",
                    suggestion="Consider using passive constructions for formal tone",
                )
            )

        return issues

    def check_jargon_level(self, text: str) -> list[StyleIssue]:
        """Check jargon usage against venue expectations."""
        issues: list[StyleIssue] = []
        style = self.spec.style

        # Technical jargon indicators
        # Count acronyms (3+ uppercase letters)
        acronyms = re.findall(r"\b[A-Z]{3,}\b", text)
        # Filter out common non-jargon acronyms
        common_acronyms = {"DNA", "RNA", "USA", "COVID", "AIDS", "WHO", "NIH", "NSF", "IEEE", "ACM"}
        jargon_acronyms = [a for a in acronyms if a not in common_acronyms]

        # Count -ization words
        ization_words = re.findall(r"\b\w+(?:ization|isation)\b", text, re.IGNORECASE)

        # Count buzzwords
        buzzwords = re.findall(
            r"\b(?:utilized|leveraged|paradigm|synergy|holistic|robust|scalable|novel)\b",
            text,
            re.IGNORECASE,
        )

        word_count = len(text.split())
        if word_count == 0:
            return issues

        jargon_count = len(jargon_acronyms) + len(ization_words) + len(buzzwords)
        jargon_density = jargon_count / word_count

        if style.jargon_level == "minimal" and jargon_density > 0.015:
            undefined_acronyms = list(set(jargon_acronyms))[:5]  # Top 5
            issues.append(
                StyleIssue(
                    category="jargon",
                    severity="warning",
                    message=f"High jargon density ({jargon_density:.1%}) for {self.spec.full_name}",
                    suggestion=f"Define acronyms on first use; prefer common words. Found: {', '.join(undefined_acronyms)}",
                )
            )

        if buzzwords and style.jargon_level == "minimal":
            issues.append(
                StyleIssue(
                    category="jargon",
                    severity="info",
                    message=f"Buzzwords detected: {', '.join(set(buzzwords))}",
                    suggestion="Consider replacing with simpler alternatives",
                )
            )

        return issues

    def check_abstract_style(self, text: str) -> list[StyleIssue]:
        """Check abstract format and content."""
        issues: list[StyleIssue] = []
        abstract_spec = self.spec.abstract

        # Extract abstract
        abstract_match = re.search(
            r"(?:abstract|ABSTRACT)[:\s]*(.+?)(?=\n\n|\n[A-Z]{2,}|\nIntroduction|\n1\s|\nKeywords)",
            text,
            re.DOTALL | re.IGNORECASE,
        )

        if not abstract_match:
            issues.append(
                StyleIssue(
                    category="abstract",
                    severity="info",
                    message="Could not locate abstract for style analysis",
                )
            )
            return issues

        abstract_text = abstract_match.group(1).strip()
        word_count = len(abstract_text.split())

        # Word count
        if abstract_spec.max_words and word_count > abstract_spec.max_words:
            issues.append(
                StyleIssue(
                    category="abstract",
                    severity="error",
                    message=f"Abstract too long: {word_count} words (max: {abstract_spec.max_words})",
                    suggestion=f"Reduce abstract by {word_count - abstract_spec.max_words} words",
                )
            )

        # Structure check
        if abstract_spec.style == "structured" and abstract_spec.structured_sections:
            sections = abstract_spec.structured_sections
            missing = [
                s
                for s in sections
                if not re.search(rf"\b{s}\b", abstract_text, re.IGNORECASE)
            ]
            if missing:
                issues.append(
                    StyleIssue(
                        category="abstract",
                        severity="error",
                        message=f"Missing structured abstract sections: {', '.join(missing)}",
                        suggestion=f"{self.spec.full_name} requires structured abstract with labeled sections",
                    )
                )

        # Check for required elements in flowing abstracts
        if abstract_spec.style == "flowing" and abstract_spec.required_elements:
            # This is advisory - we can't always detect semantic elements
            pass

        return issues

    def check_contribution_format(self, text: str) -> list[StyleIssue]:
        """Check for proper contribution statement (ML conferences)."""
        issues: list[StyleIssue] = []

        if not self.spec.requirements.contribution_list:
            return issues

        # Look for contribution list patterns
        contrib_patterns = [
            r"contributions?\s*(?:are|include|as follows)[:\s]*\n\s*[-\d\*]",
            r"we\s+(?:make|present)\s+the\s+following\s+contributions?",
            r"our\s+(?:main\s+)?contributions?\s*:",
            r"summary\s+of\s+contributions?",
            r"contributions?\s+are\s+as\s+follows",
        ]

        found = any(re.search(p, text, re.IGNORECASE) for p in contrib_patterns)

        if not found:
            issues.append(
                StyleIssue(
                    category="structure",
                    severity="warning",
                    message="No numbered/bulleted contribution list found",
                    suggestion=f"{self.spec.full_name} papers typically include explicit contribution bullets in the introduction",
                )
            )

        return issues

    def check_hedging_language(self, text: str) -> list[StyleIssue]:
        """Check appropriate hedging for claim strength."""
        issues: list[StyleIssue] = []

        # Strong causal claims
        strong_claims = re.findall(
            r"\b(?:causes?|proves?|confirms?|establishes?)\s+that\b",
            text,
            re.IGNORECASE,
        )

        if self.spec.discipline == "medical" and strong_claims:
            issues.append(
                StyleIssue(
                    category="language",
                    severity="warning",
                    message=f"Found {len(strong_claims)} strong causal claims",
                    suggestion="Medical journals prefer 'is associated with' over 'causes' for observational data",
                )
            )

        # Check for overconfident language in accessible venues
        if self.spec.style.tone == "accessible":
            overconfident = re.findall(
                r"\b(?:clearly|obviously|undoubtedly|certainly|definitely)\b",
                text,
                re.IGNORECASE,
            )
            if len(overconfident) > 3:
                issues.append(
                    StyleIssue(
                        category="language",
                        severity="info",
                        message=f"Overconfident language detected ({len(overconfident)} instances)",
                        suggestion="Consider softer phrasing for broad-audience venues",
                    )
                )

        return issues

    def check_first_person(self, text: str) -> list[StyleIssue]:
        """Check first person usage against venue preferences."""
        issues: list[StyleIssue] = []
        style = self.spec.style

        # Count first person usage
        first_person = len(re.findall(r"\b(?:we|our|us)\b", text, re.IGNORECASE))
        word_count = len(text.split())

        if word_count == 0:
            return issues

        first_person_ratio = first_person / word_count

        if not style.first_person and first_person_ratio > 0.01:
            issues.append(
                StyleIssue(
                    category="voice",
                    severity="warning",
                    message=f"First person usage ({first_person} instances) in venue that prefers impersonal style",
                    suggestion=f"{self.spec.full_name} traditionally avoids first person pronouns",
                )
            )
        elif style.first_person and first_person_ratio < 0.005 and style.voice == "active":
            issues.append(
                StyleIssue(
                    category="voice",
                    severity="info",
                    message="Low first person usage in venue that encourages it",
                    suggestion=f"{self.spec.full_name} encourages 'we' to improve readability",
                )
            )

        return issues


def extract_text(file_path: Path) -> str:
    """Extract text from PDF or read LaTeX/text directly."""
    if file_path.suffix.lower() == ".pdf":
        try:
            result = subprocess.run(
                ["pdftotext", str(file_path), "-"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except (FileNotFoundError, subprocess.CalledProcessError):
            return ""
    else:
        return file_path.read_text()


def print_issues(issues: list[StyleIssue], venue_name: str) -> None:
    """Print style issues to console."""
    if not issues:
        print(f"\nNo style issues found for {venue_name}")
        return

    print(f"\nStyle Check Results for {venue_name}")
    print("=" * 60)

    severity_icons = {
        "error": "[ERROR]",
        "warning": "[WARN]",
        "info": "[INFO]",
    }

    # Group by severity
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    for issue_list in [errors, warnings, infos]:
        for issue in issue_list:
            icon = severity_icons[issue.severity]
            print(f"\n{icon} [{issue.category.upper()}] {issue.message}")
            if issue.suggestion:
                print(f"   Suggestion: {issue.suggestion}")

    print("\n" + "=" * 60)
    print(f"Summary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Check style compliance against venue requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file paper.tex --venue nature --check-all
  %(prog)s --file paper.pdf --venue neurips --check voice,jargon
  %(prog)s --text "We show that X causes Y" --venue lancet

Available checks:
  voice         Check active vs passive voice
  jargon        Check jargon density and buzzwords
  abstract      Check abstract length and structure
  contribution  Check for contribution list (ML venues)
  hedging       Check claim strength and hedging
  first-person  Check first person pronoun usage
        """,
    )

    parser.add_argument("--file", type=str, help="Document to check (PDF or LaTeX)")
    parser.add_argument("--text", type=str, help="Direct text to check")
    parser.add_argument("--venue", type=str, required=True, help="Target venue")
    parser.add_argument(
        "--check",
        type=str,
        default="all",
        help="Checks to perform (comma-separated, or 'all')",
    )
    parser.add_argument("--check-all", action="store_true", help="Run all checks")

    args = parser.parse_args()

    # Get text to analyze
    if args.text:
        text = args.text
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return
        text = extract_text(file_path)
        if not text:
            print(f"Error: Could not extract text from {file_path}")
            return
    else:
        print("Error: Either --file or --text is required")
        return

    # Resolve venue
    venue_id = resolve_venue_id(args.venue)
    if not venue_id:
        venue_id = args.venue.lower().replace(" ", "_")

    venue_spec = get_venue(venue_id)
    if not venue_spec:
        print(f"Unknown venue: {args.venue}")
        return

    # Run checks
    checker = StyleChecker(venue_spec)

    if args.check_all or args.check == "all":
        issues = checker.check_all(text)
    else:
        issues: list[StyleIssue] = []
        checks = [c.strip() for c in args.check.split(",")]

        check_map = {
            "voice": checker.check_voice,
            "jargon": checker.check_jargon_level,
            "abstract": checker.check_abstract_style,
            "contribution": checker.check_contribution_format,
            "hedging": checker.check_hedging_language,
            "first-person": checker.check_first_person,
        }

        for check_name in checks:
            if check_name in check_map:
                issues.extend(check_map[check_name](text))
            else:
                print(f"Unknown check: {check_name}")

    # Print results
    print_issues(issues, venue_spec.full_name)


if __name__ == "__main__":
    main()
