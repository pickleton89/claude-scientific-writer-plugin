"""
Output validation for generated figures.

Provides deterministic quality checks on saved figures.

Usage:
    from scripts.validate_figure import validate_figure, print_validation

    result = validate_figure("figure.pdf", target_journal="nature")
    print_validation(result)

CLI:
    python validate_figure.py <figure_path> [journal]
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    from .plotting_params import get_journal_spec
except ImportError:
    from plotting_params import get_journal_spec  # noqa: F401


@dataclass
class FigureValidation:
    """Result of figure validation."""

    valid: bool
    checks: dict[str, Optional[bool]] = field(default_factory=dict)
    details: dict[str, str] = field(default_factory=dict)

    def __bool__(self) -> bool:
        """Allow using result directly in if statements."""
        return self.valid


def validate_figure(
    fig_path: str,
    target_journal: Optional[str] = None,
    min_dpi: int = 300,
) -> FigureValidation:
    """
    Validate a saved figure file.

    Checks:
    - File exists and is readable
    - Format is correct (PDF/PNG/SVG/EPS/TIFF)
    - DPI is sufficient (for raster formats)
    - File size is reasonable
    - PDF validity (if pdfinfo available)
    - Font embedding (if pdffonts available)

    Parameters
    ----------
    fig_path : str
        Path to saved figure file
    target_journal : str, optional
        Journal name for dimension checking
    min_dpi : int
        Minimum DPI for raster formats (default: 300)

    Returns
    -------
    FigureValidation
        Result with valid flag, checks dict, and details dict

    Examples
    --------
    >>> result = validate_figure("figure.pdf")
    >>> result.valid
    True
    >>> result.checks["file_exists"]
    True
    """
    path = Path(fig_path)
    checks: dict[str, Optional[bool]] = {}
    details: dict[str, str] = {}

    # Check file exists
    checks["file_exists"] = path.exists()
    if not checks["file_exists"]:
        return FigureValidation(
            valid=False,
            checks=checks,
            details={"error": f"File not found: {fig_path}"},
        )

    # Check file size
    size_bytes = path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    checks["reasonable_size"] = 0.001 < size_mb < 50  # Between 1KB and 50MB
    details["file_size_mb"] = f"{size_mb:.3f}"

    if size_mb < 0.001:
        details["size_warning"] = "File may be empty or corrupted"
    elif size_mb > 50:
        details["size_warning"] = "File is very large; consider reducing DPI or complexity"

    # Check format
    suffix = path.suffix.lower()
    valid_formats = [".pdf", ".png", ".svg", ".eps", ".tiff", ".tif"]
    checks["valid_format"] = suffix in valid_formats
    details["format"] = suffix

    # For PDF, check if it's valid
    if suffix == ".pdf":
        checks.update(_validate_pdf(path, details))

    # For PNG/TIFF, check DPI
    if suffix in [".png", ".tiff", ".tif"]:
        checks.update(_validate_raster(path, min_dpi, details))

    # Check against journal specs if provided
    if target_journal:
        spec = get_journal_spec(target_journal)
        details["target_journal"] = target_journal
        details["required_dpi"] = str(spec.min_dpi)
        details["preferred_format"] = spec.preferred_format

        # Check format matches journal preference
        if suffix.lstrip(".") != spec.preferred_format:
            checks["format_matches_journal"] = False
            details["format_note"] = (
                f"{target_journal} prefers {spec.preferred_format.upper()}"
            )
        else:
            checks["format_matches_journal"] = True

    # Overall validity
    required_checks = ["file_exists", "valid_format", "reasonable_size"]
    valid = all(checks.get(c, True) for c in required_checks)

    return FigureValidation(valid=valid, checks=checks, details=details)


def _validate_pdf(path: Path, details: dict[str, str]) -> dict[str, Optional[bool]]:
    """Validate PDF-specific properties."""
    checks: dict[str, Optional[bool]] = {}

    # Check if pdfinfo is available
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        checks["pdf_valid"] = result.returncode == 0

        if result.returncode == 0:
            # Extract dimensions
            for line in result.stdout.split("\n"):
                if line.startswith("Page size:"):
                    details["dimensions"] = line.split(":")[1].strip()
                elif line.startswith("Pages:"):
                    details["pages"] = line.split(":")[1].strip()
    except FileNotFoundError:
        checks["pdf_valid"] = None
        details["pdf_check"] = "pdfinfo not available (install poppler-utils)"
    except subprocess.TimeoutExpired:
        checks["pdf_valid"] = None
        details["pdf_check"] = "pdfinfo timed out"

    # Check fonts embedded
    try:
        result = subprocess.run(
            ["pdffonts", str(path)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if len(lines) > 2:  # Header + separator + fonts
                font_lines = lines[2:]
                # Check for "no" in emb column (column index ~5)
                all_embedded = True
                for line in font_lines:
                    if line.strip():
                        parts = line.split()
                        # emb column is typically index 3 or 4
                        if len(parts) > 3 and parts[3].lower() == "no":
                            all_embedded = False
                            break
                checks["fonts_embedded"] = all_embedded
                if not all_embedded:
                    details["font_warning"] = "Some fonts not embedded"
            else:
                checks["fonts_embedded"] = True  # No fonts (all paths)
    except FileNotFoundError:
        checks["fonts_embedded"] = None
        details["font_check"] = "pdffonts not available (install poppler-utils)"
    except subprocess.TimeoutExpired:
        checks["fonts_embedded"] = None
        details["font_check"] = "pdffonts timed out"

    return checks


def _validate_raster(
    path: Path, min_dpi: int, details: dict[str, str]
) -> dict[str, Optional[bool]]:
    """Validate raster image properties."""
    checks: dict[str, Optional[bool]] = {}

    try:
        from PIL import Image

        with Image.open(path) as img:
            # Get DPI
            dpi = img.info.get("dpi", (72, 72))
            if isinstance(dpi, tuple):
                actual_dpi = min(dpi[0], dpi[1])
            else:
                actual_dpi = dpi

            checks["dpi_sufficient"] = actual_dpi >= min_dpi
            details["dpi"] = str(int(actual_dpi))
            details["dimensions_px"] = f"{img.width}x{img.height}"

            if actual_dpi < min_dpi:
                details["dpi_warning"] = f"DPI ({actual_dpi}) below minimum ({min_dpi})"

            # Calculate print size at current DPI
            width_in = img.width / actual_dpi
            height_in = img.height / actual_dpi
            details["print_size_inches"] = f"{width_in:.2f}x{height_in:.2f}"

    except ImportError:
        checks["dpi_sufficient"] = None
        details["dpi_check"] = "PIL/Pillow not available (pip install Pillow)"
    except Exception as e:
        checks["dpi_sufficient"] = None
        details["dpi_check"] = f"Error reading image: {e}"

    return checks


def print_validation(result: FigureValidation) -> None:
    """
    Print figure validation result.

    Parameters
    ----------
    result : FigureValidation
        Validation result to print
    """
    status = "PASSED" if result.valid else "FAILED"
    print(f"Figure Validation: {status}")
    print()

    for check, passed in result.checks.items():
        if passed is None:
            icon = "?"
        elif passed:
            icon = "+"
        else:
            icon = "-"
        print(f"  [{icon}] {check}")

    if result.details:
        print()
        print("Details:")
        for key, value in result.details.items():
            print(f"  {key}: {value}")


def validate_figure_for_journal(
    fig_path: str, journal: str
) -> tuple[bool, list[str]]:
    """
    Validate figure meets journal requirements.

    Parameters
    ----------
    fig_path : str
        Path to figure file
    journal : str
        Journal name

    Returns
    -------
    tuple[bool, list[str]]
        (passes_requirements, list_of_issues)
    """
    result = validate_figure(fig_path, target_journal=journal)
    issues = []

    spec = get_journal_spec(journal)

    if not result.checks.get("file_exists", False):
        issues.append("File does not exist")
        return False, issues

    # Check format
    suffix = Path(fig_path).suffix.lower().lstrip(".")
    if suffix != spec.preferred_format:
        issues.append(
            f"Format mismatch: {suffix.upper()} provided, "
            f"{spec.preferred_format.upper()} preferred"
        )

    # Check DPI for raster
    if suffix in ["png", "tiff", "tif"]:
        dpi = result.details.get("dpi", "0")
        try:
            if int(dpi) < spec.min_dpi:
                issues.append(
                    f"DPI too low: {dpi} provided, minimum {spec.min_dpi} required"
                )
        except ValueError:
            issues.append("Could not verify DPI")

    # Check fonts for PDF
    if suffix == "pdf":
        if result.checks.get("fonts_embedded") is False:
            issues.append("Fonts not embedded in PDF")

    passes = len(issues) == 0
    return passes, issues


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validate_figure.py <figure_path> [journal]")
        print()
        print("Supported journals: nature, cell, science, plos, elife")
        print()
        print("Examples:")
        print("  python validate_figure.py figure.pdf")
        print("  python validate_figure.py figure.png nature")
        sys.exit(1)

    fig_path = sys.argv[1]
    journal = sys.argv[2] if len(sys.argv) > 2 else None

    result = validate_figure(fig_path, target_journal=journal)
    print_validation(result)

    if journal:
        print()
        passes, issues = validate_figure_for_journal(fig_path, journal)
        if passes:
            print(f"Figure meets {journal.title()} requirements")
        else:
            print(f"Figure does NOT meet {journal.title()} requirements:")
            for issue in issues:
                print(f"  - {issue}")

    sys.exit(0 if result.valid else 1)
