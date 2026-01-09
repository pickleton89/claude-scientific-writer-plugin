#!/usr/bin/env python3
"""
Poster Quality Validation - Deterministic Checks

Validates research posters against defined quality thresholds.
Replaces manual checklist items with automated validation.

Usage:
    python validate_poster.py poster.tex poster.pdf
    python validate_poster.py poster.tex poster.pdf --output report.json
    python validate_poster.py poster.tex poster.pdf --spec poster_spec.yaml

Output: Structured JSON report with all validation results.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from utils.dimensions import validate_dimensions, pts_to_inches
from utils.schemas import (
    QualityReport,
    WordCountResult,
    FontCheckResult,
    ImageCheckResult,
    ValidationStatus,
)


# Word count thresholds for research posters
WORD_COUNT_MIN = 300
WORD_COUNT_MAX = 800
WORD_COUNT_IDEAL_MIN = 400
WORD_COUNT_IDEAL_MAX = 600

# Section word budgets (typical)
SECTION_BUDGETS = {
    "introduction": (75, 150),
    "background": (75, 150),
    "methods": (100, 200),
    "results": (150, 250),
    "discussion": (100, 200),
    "conclusions": (50, 100),
    "references": (0, 100),  # References don't count toward main text
}


def count_words_in_tex(tex_path: Path) -> dict[str, int]:
    """
    Extract and count words per section from LaTeX source.

    Handles tikzposter, beamerposter, and baposter block syntax.

    Args:
        tex_path: Path to .tex file

    Returns:
        Dictionary mapping section names to word counts,
        plus 'total' key with overall count
    """
    content = tex_path.read_text(encoding="utf-8")

    sections = {}

    # Pattern for tikzposter/beamerposter blocks: \block{Title}{content}
    block_pattern = r"\\block\s*\{([^}]+)\}\s*\{((?:[^{}]|\{[^{}]*\})*)\}"

    for match in re.finditer(block_pattern, content, re.DOTALL):
        section_name = match.group(1).lower().strip()
        section_content = match.group(2)

        word_count = _count_words_in_latex(section_content)
        sections[section_name] = word_count

    # Also check for baposter headerbox: \headerbox{Title}{...}{content}
    headerbox_pattern = (
        r"\\headerbox\s*\{([^}]+)\}\s*\{[^}]*\}\s*\{((?:[^{}]|\{[^{}]*\})*)\}"
    )

    for match in re.finditer(headerbox_pattern, content, re.DOTALL):
        section_name = match.group(1).lower().strip()
        section_content = match.group(2)

        word_count = _count_words_in_latex(section_content)
        # Add to existing or create new
        sections[section_name] = sections.get(section_name, 0) + word_count

    # Calculate total (excluding references)
    total = sum(
        count
        for name, count in sections.items()
        if "reference" not in name.lower() and "acknowledgment" not in name.lower()
    )
    sections["total"] = total

    return sections


def _count_words_in_latex(text: str) -> int:
    """
    Count words in LaTeX content, stripping commands and environments.

    Args:
        text: LaTeX content string

    Returns:
        Word count
    """
    # Remove LaTeX commands (but keep their text arguments where sensible)
    # Remove \command{arg} but keep arg for text commands
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textit\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)

    # Remove other commands entirely
    text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})*", " ", text)

    # Remove special characters and math
    text = re.sub(r"\$[^$]*\$", " ", text)  # Inline math
    text = re.sub(r"\\[\[\]]", " ", text)  # Display math delimiters
    text = re.sub(r"[{}\\$%&_^~]", " ", text)

    # Remove figure/table environments content (captions counted separately)
    text = re.sub(r"\\begin\{(figure|table)\}.*?\\end\{\1\}", " ", text, flags=re.DOTALL)

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text)

    # Count words
    words = [w for w in text.split() if len(w) > 0 and w[0].isalpha()]
    return len(words)


def validate_word_count(
    word_counts: dict[str, int],
    min_total: int = WORD_COUNT_MIN,
    max_total: int = WORD_COUNT_MAX,
) -> WordCountResult:
    """
    Validate word counts against thresholds.

    Args:
        word_counts: Dictionary from count_words_in_tex
        min_total: Minimum acceptable total words
        max_total: Maximum acceptable total words

    Returns:
        WordCountResult with validation status
    """
    total = word_counts.get("total", 0)

    if min_total <= total <= max_total:
        status = ValidationStatus.PASS
    elif total < min_total * 0.8 or total > max_total * 1.2:
        status = ValidationStatus.FAIL
    else:
        status = ValidationStatus.WARN

    return WordCountResult(
        total=total,
        by_section={k: v for k, v in word_counts.items() if k != "total"},
        target_min=min_total,
        target_max=max_total,
        status=status,
    )


def extract_pdf_dimensions(pdf_path: Path) -> dict | None:
    """
    Extract PDF page dimensions using pdfinfo.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary with width_pts, height_pts, or None if extraction fails
    """
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        for line in result.stdout.split("\n"):
            if "Page size" in line:
                # Parse "Page size:      2384 x 3370 pts"
                match = re.search(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)", line)
                if match:
                    return {
                        "width_pts": float(match.group(1)),
                        "height_pts": float(match.group(2)),
                    }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None


def extract_pdf_fonts(pdf_path: Path) -> list[FontCheckResult]:
    """
    Extract font information from PDF using pdffonts.

    Args:
        pdf_path: Path to PDF file

    Returns:
        List of FontCheckResult objects
    """
    fonts = []

    try:
        result = subprocess.run(
            ["pdffonts", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        lines = result.stdout.strip().split("\n")
        if len(lines) < 3:
            return fonts

        # Skip header lines
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 5:
                fonts.append(
                    FontCheckResult(
                        font_name=parts[0],
                        font_type=parts[1] if len(parts) > 1 else "unknown",
                        embedded=parts[3].lower() == "yes" if len(parts) > 3 else False,
                        subset=parts[4].lower() == "yes" if len(parts) > 4 else False,
                    )
                )

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return fonts


def extract_pdf_images(pdf_path: Path) -> list[ImageCheckResult]:
    """
    Extract image information from PDF using pdfimages.

    Args:
        pdf_path: Path to PDF file

    Returns:
        List of ImageCheckResult objects
    """
    images = []

    try:
        result = subprocess.run(
            ["pdfimages", "-list", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        lines = result.stdout.strip().split("\n")
        if len(lines) < 3:
            return images

        # Skip header lines
        for idx, line in enumerate(lines[2:]):
            parts = line.split()
            if len(parts) >= 7:
                try:
                    images.append(
                        ImageCheckResult(
                            image_index=idx,
                            page=int(parts[0]),
                            width_px=int(parts[3]),
                            height_px=int(parts[4]),
                            color_space=parts[5],
                            format=parts[6] if len(parts) > 6 else "unknown",
                        )
                    )
                except (ValueError, IndexError):
                    continue

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return images


def extract_page_count(pdf_path: Path) -> int | None:
    """
    Extract page count from PDF.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Page count or None if extraction fails
    """
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        for line in result.stdout.split("\n"):
            if line.startswith("Pages:"):
                return int(line.split(":")[1].strip())

    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    return None


def check_latex_structure(tex_path: Path) -> dict:
    """
    Check LaTeX source for required structural elements.

    Args:
        tex_path: Path to .tex file

    Returns:
        Dictionary with structure validation results
    """
    content = tex_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    required_sections = ["introduction", "methods", "results", "conclusions"]
    optional_sections = ["background", "discussion", "references", "acknowledgments"]

    found_sections = []
    for section in required_sections + optional_sections:
        # Check for block/headerbox with section name
        if re.search(rf"\\(block|headerbox)\s*\{{\s*{section}", content_lower):
            found_sections.append(section)

    missing_required = [s for s in required_sections if s not in found_sections]

    # Check for other structural elements
    has_title = bool(re.search(r"\\title\s*\{", content))
    has_author = bool(re.search(r"\\author\s*\{", content))
    has_institute = bool(
        re.search(r"\\(institute|affiliation|organization)\s*\{", content)
    )

    return {
        "sections_present": found_sections,
        "required_sections": required_sections,
        "missing_required": missing_required,
        "has_title": has_title,
        "has_author": has_author,
        "has_affiliation": has_institute,
        "pass": len(missing_required) == 0 and has_title,
    }


def check_latex_compilation(tex_path: Path) -> dict:
    """
    Check LaTeX log file for compilation issues.

    Args:
        tex_path: Path to .tex file (will look for .log with same name)

    Returns:
        Dictionary with compilation check results
    """
    log_path = tex_path.with_suffix(".log")

    if not log_path.exists():
        return {
            "log_found": False,
            "pass": True,  # Can't check, assume OK
        }

    log_content = log_path.read_text(encoding="utf-8", errors="ignore")

    overfull_count = len(re.findall(r"Overfull \\[hv]box", log_content))
    underfull_count = len(re.findall(r"Underfull \\[hv]box", log_content))
    warning_count = len(re.findall(r"Warning:", log_content, re.IGNORECASE))
    error_count = len(re.findall(r"^!", log_content, re.MULTILINE))

    # Extract sample warnings
    warnings = re.findall(r"Warning:.*", log_content, re.IGNORECASE)[:5]

    return {
        "log_found": True,
        "errors": error_count,
        "warnings": warning_count,
        "overfull_boxes": overfull_count,
        "underfull_boxes": underfull_count,
        "sample_warnings": warnings,
        "pass": error_count == 0 and overfull_count <= 10,
    }


def run_validation(
    tex_path: Path | None,
    pdf_path: Path,
    expected_size: str | None = None,
) -> QualityReport:
    """
    Run all validation checks and return structured report.

    Args:
        tex_path: Path to .tex source file (optional)
        pdf_path: Path to compiled .pdf
        expected_size: Expected poster size (e.g., "A0")

    Returns:
        QualityReport with all validation results
    """
    report = QualityReport(
        poster_path=str(pdf_path),
        source_path=str(tex_path) if tex_path else None,
    )

    # PDF-based checks
    if pdf_path.exists():
        # Page count check
        page_count = extract_page_count(pdf_path)
        if page_count is not None:
            if page_count != 1:
                report.add_error(f"Poster should be single page, found {page_count} pages")

        # Dimension check
        dims = extract_pdf_dimensions(pdf_path)
        if dims:
            dim_result = validate_dimensions(
                dims["width_pts"],
                dims["height_pts"],
                expected_size=expected_size,
            )
            report.dimensions = {
                "width_pts": dims["width_pts"],
                "height_pts": dims["height_pts"],
                "width_inches": pts_to_inches(dims["width_pts"]),
                "height_inches": pts_to_inches(dims["height_pts"]),
                "detected_size": dim_result["match"].size_name,
                "orientation": (
                    dim_result["match"].orientation.value
                    if dim_result["match"].orientation
                    else None
                ),
                "pass": dim_result["valid"],
            }
            for issue in dim_result.get("issues", []):
                report.add_warning(issue)
        else:
            report.add_warning("Could not extract PDF dimensions (pdfinfo not available?)")

        # Font check
        fonts = extract_pdf_fonts(pdf_path)
        report.fonts = fonts
        non_embedded = [f for f in fonts if not f.embedded]
        if non_embedded:
            report.add_error(
                f"{len(non_embedded)} fonts not embedded: "
                f"{', '.join(f.font_name for f in non_embedded[:3])}"
            )

        # Image check
        images = extract_pdf_images(pdf_path)
        report.images = images
        if not images:
            report.add_warning("No images found in PDF")

    else:
        report.add_error(f"PDF file not found: {pdf_path}")

    # LaTeX source checks
    if tex_path and tex_path.exists():
        # Word count
        word_counts = count_words_in_tex(tex_path)
        report.word_count = validate_word_count(word_counts)

        if report.word_count.status == ValidationStatus.FAIL:
            report.add_error(
                f"Word count ({report.word_count.total}) outside acceptable range "
                f"({WORD_COUNT_MIN}-{WORD_COUNT_MAX})"
            )
        elif report.word_count.status == ValidationStatus.WARN:
            report.add_warning(
                f"Word count ({report.word_count.total}) outside ideal range "
                f"({WORD_COUNT_IDEAL_MIN}-{WORD_COUNT_IDEAL_MAX})"
            )

        # Structure check
        report.structure = check_latex_structure(tex_path)
        if not report.structure.get("pass"):
            missing = report.structure.get("missing_required", [])
            if missing:
                report.add_warning(f"Missing recommended sections: {', '.join(missing)}")

        # Compilation check
        report.compilation = check_latex_compilation(tex_path)
        if not report.compilation.get("pass"):
            if report.compilation.get("errors", 0) > 0:
                report.add_error(
                    f"LaTeX compilation had {report.compilation['errors']} errors"
                )

    elif tex_path:
        report.add_warning(f"LaTeX source file not found: {tex_path}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Validate research poster quality against defined thresholds."
    )
    parser.add_argument(
        "tex_file",
        type=Path,
        nargs="?",
        help="Path to .tex source file",
    )
    parser.add_argument(
        "pdf_file",
        type=Path,
        help="Path to compiled .pdf file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON report path",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        help="Poster specification YAML (for additional validation)",
    )
    parser.add_argument(
        "--size",
        help="Expected poster size (e.g., 'A0', '36x48')",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output JSON only (no human-readable summary)",
    )

    args = parser.parse_args()

    # Run validation
    report = run_validation(
        tex_path=args.tex_file,
        pdf_path=args.pdf_file,
        expected_size=args.size,
    )

    # Output results
    report_dict = report.to_dict()

    if args.json:
        print(json.dumps(report_dict, indent=2))
    else:
        # Human-readable summary
        print("=" * 60)
        print("POSTER QUALITY VALIDATION REPORT")
        print("=" * 60)
        print(f"\nPoster: {report.poster_path}")
        if report.source_path:
            print(f"Source: {report.source_path}")
        print(f"Timestamp: {report.validation_timestamp}")
        print(f"\nOverall Status: {'PASS' if report.overall_pass else 'FAIL'}")
        print("-" * 40)

        # Word count
        if report.word_count:
            wc = report.word_count
            status_icon = {"pass": "+", "warn": "~", "fail": "X"}[wc.status.value]
            print(f"[{status_icon}] Word Count: {wc.total} (target: {wc.target_min}-{wc.target_max})")

        # Dimensions
        if report.dimensions:
            dims = report.dimensions
            status_icon = "+" if dims.get("pass") else "X"
            size_str = dims.get("detected_size") or "non-standard"
            print(
                f"[{status_icon}] Dimensions: {dims.get('width_inches', 0):.1f}x"
                f"{dims.get('height_inches', 0):.1f}\" ({size_str})"
            )

        # Fonts
        if report.fonts:
            all_embedded = all(f.embedded for f in report.fonts)
            status_icon = "+" if all_embedded else "X"
            print(f"[{status_icon}] Fonts: {len(report.fonts)} fonts, all embedded: {all_embedded}")

        # Images
        if report.images:
            print(f"[+] Images: {len(report.images)} found")

        # Structure
        if report.structure:
            status_icon = "+" if report.structure.get("pass") else "~"
            sections = report.structure.get("sections_present", [])
            print(f"[{status_icon}] Structure: {len(sections)} sections found")

        # Errors and warnings
        if report.errors:
            print("\nErrors:")
            for err in report.errors:
                print(f"  X {err}")

        if report.warnings:
            print("\nWarnings:")
            for warn in report.warnings:
                print(f"  ~ {warn}")

        print("")

    # Save to file if requested
    if args.output:
        args.output.write_text(json.dumps(report_dict, indent=2))
        if not args.json:
            print(f"Report saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if report.overall_pass else 1)


if __name__ == "__main__":
    main()
