#!/usr/bin/env python3
"""
Pre-flight check for LaTeX hypothesis reports.

Validates document structure before compilation to catch common issues.
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# Required components
REQUIRED_ENVIRONMENTS = [
    "summarybox",
    "hypothesisbox",  # Any of hypothesisbox1-5
    "predictionbox",
    "comparisonbox",
]

REQUIRED_SECTIONS = [
    (r"\\section\*?\{.*Executive Summary.*\}", "Executive Summary"),
    (r"\\section\*?\{.*Competing Hypotheses.*\}", "Competing Hypotheses"),
    (r"\\section\*?\{.*Testable Predictions.*\}", "Testable Predictions"),
    (r"\\section\*?\{.*Critical Comparisons.*\}", "Critical Comparisons"),
]

REQUIRED_APPENDICES = ["Appendix A", "Appendix B", "Appendix C"]


@dataclass
class PreflightReport:
    """LaTeX preflight check report."""

    environments: dict[str, int] = field(default_factory=dict)
    sections: dict[str, bool] = field(default_factory=dict)
    appendices: dict[str, bool] = field(default_factory=dict)
    citations: dict[str, int | bool] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    overall_valid: bool = True


def count_hypothesis_boxes(content: str) -> int:
    """Count total hypothesis boxes (numbered variants 1-5)."""
    count = 0
    for i in range(1, 6):
        pattern = rf"\\begin\{{hypothesisbox{i}\}}"
        count += len(re.findall(pattern, content))
    # Also check for generic hypothesisbox
    count += len(re.findall(r"\\begin\{hypothesisbox\}", content))
    return count


def check_environment(content: str, env_name: str) -> int:
    """Count occurrences of a LaTeX environment."""
    pattern = rf"\\begin\{{{env_name}\}}"
    return len(re.findall(pattern, content))


def check_section(content: str, pattern: str) -> bool:
    """Check if a section matching the pattern exists."""
    return bool(re.search(pattern, content, re.IGNORECASE))


def check_balanced_environments(content: str, env_name: str) -> tuple[bool, str]:
    """Check that begin/end are balanced for an environment."""
    begin_pattern = rf"\\begin\{{{env_name}"
    end_pattern = rf"\\end\{{{env_name}"

    begin_count = len(re.findall(begin_pattern, content))
    end_count = len(re.findall(end_pattern, content))

    if begin_count != end_count:
        return False, f"Unbalanced {env_name}: {begin_count} begins, {end_count} ends"
    return True, f"{env_name} balanced"


def check_citations(content: str) -> tuple[int, bool]:
    """
    Count citations and check for bibliography.

    Returns:
        (citation_count, has_bibliography)
    """
    # Count \cite{}, \citep{}, \citet{} patterns
    cite_patterns = [
        r"\\cite\{[^}]+\}",
        r"\\citep\{[^}]+\}",
        r"\\citet\{[^}]+\}",
        r"\\citeauthor\{[^}]+\}",
    ]
    total = 0
    for pattern in cite_patterns:
        total += len(re.findall(pattern, content))

    # Check for bibliography
    has_bib = bool(
        re.search(r"\\bibliography\{", content)
        or re.search(r"\\begin\{thebibliography\}", content)
        or re.search(r"\\addbibresource\{", content)
        or re.search(r"\\printbibliography", content)
    )

    return total, has_bib


def check_page_breaks_before_boxes(content: str) -> int:
    """
    Check for page breaks before hypothesis boxes.

    Returns count of boxes without preceding newpage.
    """
    # Find hypothesis box positions
    hyp_box_pattern = r"\\begin\{hypothesisbox[1-5]?\}"
    newpage_pattern = r"\\newpage|\\clearpage|\\cleardoublepage"

    hyp_positions = [m.start() for m in re.finditer(hyp_box_pattern, content)]
    newpage_positions = [m.start() for m in re.finditer(newpage_pattern, content)]

    missing = 0
    for pos in hyp_positions:
        # Check if there's a page break within 300 chars before the box
        nearby = [np for np in newpage_positions if pos - 300 < np < pos]
        if not nearby:
            missing += 1

    return missing


def check_figure_references(content: str) -> list[str]:
    """Check for unreferenced figures or missing figure references."""
    warnings = []

    # Find figure labels
    label_pattern = r"\\label\{(fig:[^}]+)\}"
    labels = set(re.findall(label_pattern, content))

    # Find figure references
    ref_pattern = r"\\ref\{(fig:[^}]+)\}"
    refs = set(re.findall(ref_pattern, content))

    # Check for unreferenced figures
    unreferenced = labels - refs
    if unreferenced:
        warnings.append(f"Unreferenced figures: {', '.join(unreferenced)}")

    # Check for missing figure references
    missing = refs - labels
    if missing:
        warnings.append(f"Missing figure labels: {', '.join(missing)}")

    return warnings


def check_table_references(content: str) -> list[str]:
    """Check for unreferenced tables or missing table references."""
    warnings = []

    # Find table labels
    label_pattern = r"\\label\{(tab:[^}]+)\}"
    labels = set(re.findall(label_pattern, content))

    # Find table references
    ref_pattern = r"\\ref\{(tab:[^}]+)\}"
    refs = set(re.findall(ref_pattern, content))

    # Check for unreferenced tables
    unreferenced = labels - refs
    if unreferenced:
        warnings.append(f"Unreferenced tables: {', '.join(unreferenced)}")

    # Check for missing table references
    missing = refs - labels
    if missing:
        warnings.append(f"Missing table labels: {', '.join(missing)}")

    return warnings


def check_latex_structure(content: str) -> PreflightReport:
    """
    Check LaTeX document structure.

    Args:
        content: LaTeX document content as string

    Returns:
        PreflightReport with validation results
    """
    report = PreflightReport()

    # Check for required environments
    for env in REQUIRED_ENVIRONMENTS:
        if env == "hypothesisbox":
            count = count_hypothesis_boxes(content)
            report.environments[env] = count
            if count == 0:
                report.errors.append("No hypothesis boxes found")
                report.overall_valid = False
            elif count < 3:
                report.errors.append(
                    f"Only {count} hypothesis boxes (need >=3)"
                )
                report.overall_valid = False
            elif count > 5:
                report.warnings.append(f"{count} hypothesis boxes (expected 3-5)")
        else:
            count = check_environment(content, env)
            report.environments[env] = count
            if count == 0:
                report.errors.append(f"Missing {env} environment")
                report.overall_valid = False

    # Check for balanced environments
    for env in ["hypothesisbox", "predictionbox", "comparisonbox", "summarybox"]:
        balanced, msg = check_balanced_environments(content, env)
        if not balanced:
            report.errors.append(msg)
            report.overall_valid = False

    # Also check numbered hypothesis boxes
    for i in range(1, 6):
        balanced, msg = check_balanced_environments(content, f"hypothesisbox{i}")
        if not balanced:
            report.errors.append(msg)
            report.overall_valid = False

    # Check for required sections
    for pattern, name in REQUIRED_SECTIONS:
        found = check_section(content, pattern)
        report.sections[name] = found
        if not found:
            report.errors.append(f"Missing section: {name}")
            report.overall_valid = False

    # Check for appendices (warnings only, not errors)
    for appendix in REQUIRED_APPENDICES:
        found = appendix in content
        report.appendices[appendix] = found
        if not found:
            report.warnings.append(f"Missing {appendix}")

    # Check citations
    cite_count, has_bib = check_citations(content)
    report.citations["count"] = cite_count
    report.citations["has_bibliography"] = has_bib

    if cite_count < 10:
        report.warnings.append(
            f"Only {cite_count} citations (recommend >=40 total)"
        )
    if not has_bib:
        report.errors.append("No bibliography found")
        report.overall_valid = False

    # Check page breaks before hypothesis boxes
    missing_breaks = check_page_breaks_before_boxes(content)
    if missing_breaks > 0:
        report.warnings.append(
            f"{missing_breaks} hypothesis boxes without preceding page break (overflow risk)"
        )

    # Check figure and table references
    report.warnings.extend(check_figure_references(content))
    report.warnings.extend(check_table_references(content))

    # Check for common LaTeX issues
    if "\\begin{document}" not in content:
        report.errors.append("Missing \\begin{document}")
        report.overall_valid = False
    if "\\end{document}" not in content:
        report.errors.append("Missing \\end{document}")
        report.overall_valid = False

    # Check for documentclass
    if not re.search(r"\\documentclass", content):
        report.errors.append("Missing \\documentclass")
        report.overall_valid = False

    return report


def check_latex_file(filepath: Path) -> PreflightReport:
    """
    Check a LaTeX file.

    Args:
        filepath: Path to the LaTeX file

    Returns:
        PreflightReport with validation results

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    content = filepath.read_text(encoding="utf-8")
    return check_latex_structure(content)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: latex_preflight.py <document.tex>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    report = check_latex_file(filepath)

    status = "PASS" if report.overall_valid else "FAIL"
    icon = "✓" if report.overall_valid else "✗"
    print(f"\n{icon} {status}: LaTeX Preflight Check")
    print(f"  File: {filepath.name}")

    print("\n  Environments:")
    for env, count in report.environments.items():
        env_icon = "✓" if count > 0 else "✗"
        print(f"    {env_icon} {env}: {count}")

    print("\n  Sections:")
    for section, found in report.sections.items():
        sec_icon = "✓" if found else "✗"
        print(f"    {sec_icon} {section}")

    print("\n  Appendices:")
    for appendix, found in report.appendices.items():
        app_icon = "✓" if found else "⚠"
        print(f"    {app_icon} {appendix}")

    print(f"\n  Citations: {report.citations.get('count', 0)}")
    bib_icon = "✓" if report.citations.get("has_bibliography") else "✗"
    print(f"  Bibliography: {bib_icon}")

    if report.warnings:
        print("\n  Warnings:")
        for w in report.warnings:
            print(f"    ⚠ {w}")

    if report.errors:
        print("\n  Errors:")
        for e in report.errors:
            print(f"    ✗ {e}")

    sys.exit(0 if report.overall_valid else 1)


if __name__ == "__main__":
    main()
