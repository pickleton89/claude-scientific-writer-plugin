#!/usr/bin/env python3
"""Preflight validation for paper transformation pipeline.

This script performs comprehensive pre-execution validation to catch
errors before expensive LLM calls. It checks for:
- Input file existence and validity
- Required dependencies
- API key configuration
- Figure resolution (for posters)
- Estimated costs

Usage:
    python preflight_check.py <input_dir> [--components website,poster,video]
    python preflight_check.py ./paper_latex --model-tier production

Example:
    python preflight_check.py ./my_paper --components poster --venue neurips
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# Add lib to path for imports
SCRIPT_DIR = Path(__file__).parent
LIB_DIR = SCRIPT_DIR.parent / "lib"
sys.path.insert(0, str(LIB_DIR.parent))


@dataclass
class CheckResult:
    """Result of a single preflight check.

    Attributes:
        name: Check identifier
        passed: Whether the check passed
        required: Whether passing is required
        message: Description of result
        details: Additional details if any
    """

    name: str
    passed: bool | None  # None means skipped
    required: bool = True
    message: str = ""
    details: str | None = None


@dataclass
class PreflightResult:
    """Complete preflight check result.

    Attributes:
        passed: Whether all required checks passed
        checks: Individual check results
        errors: Critical errors that block execution
        warnings: Non-blocking issues
        cost_estimate: Estimated cost in USD if available
        paper_info: Extracted paper information
    """

    passed: bool = True
    checks: list[CheckResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    cost_estimate: float | None = None
    paper_info: dict = field(default_factory=dict)

    def add_check(self, check: CheckResult) -> None:
        """Add a check result and update overall status."""
        self.checks.append(check)
        if check.required and check.passed is False:
            self.passed = False
            if check.message:
                self.errors.append(check.message)
        elif check.passed is False and check.message:
            self.warnings.append(check.message)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "passed": self.passed,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "required": c.required,
                    "message": c.message,
                }
                for c in self.checks
            ],
            "errors": self.errors,
            "warnings": self.warnings,
            "cost_estimate": self.cost_estimate,
            "paper_info": self.paper_info,
        }


def check_input_exists(input_dir: Path) -> CheckResult:
    """Check that input directory exists and contains valid files."""
    if not input_dir.exists():
        return CheckResult(
            name="input_exists",
            passed=False,
            required=True,
            message=f"Input directory not found: {input_dir}",
        )

    if not input_dir.is_dir():
        return CheckResult(
            name="input_exists",
            passed=False,
            required=True,
            message=f"Input path is not a directory: {input_dir}",
        )

    tex_files = list(input_dir.glob("*.tex"))
    pdf_files = list(input_dir.glob("*.pdf"))

    if not tex_files and not pdf_files:
        return CheckResult(
            name="input_exists",
            passed=False,
            required=True,
            message=f"No .tex or .pdf files found in {input_dir}",
        )

    file_type = "LaTeX" if tex_files else "PDF"
    file_count = len(tex_files) if tex_files else len(pdf_files)

    return CheckResult(
        name="input_exists",
        passed=True,
        message=f"Found {file_count} {file_type} file(s)",
        details=str(tex_files[0] if tex_files else pdf_files[0]),
    )


def check_latex_compiles(input_dir: Path) -> CheckResult:
    """Check that LaTeX files compile successfully."""
    tex_files = list(input_dir.glob("*.tex"))

    if not tex_files:
        return CheckResult(
            name="latex_compiles",
            passed=None,  # Skipped
            required=False,
            message="Skipped: No LaTeX files",
        )

    # Find main tex file (usually main.tex or paper.tex)
    main_tex = None
    for name in ["main.tex", "paper.tex", "manuscript.tex"]:
        candidate = input_dir / name
        if candidate.exists():
            main_tex = candidate
            break

    if main_tex is None:
        main_tex = tex_files[0]

    # Check if pdflatex is available
    if not shutil.which("pdflatex"):
        return CheckResult(
            name="latex_compiles",
            passed=None,
            required=False,
            message="Skipped: pdflatex not installed",
        )

    try:
        proc = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-draftmode",  # Faster, no PDF output
                main_tex.name,
            ],
            capture_output=True,
            timeout=120,
            cwd=input_dir,
        )

        if proc.returncode == 0:
            return CheckResult(
                name="latex_compiles",
                passed=True,
                message="LaTeX compiles successfully",
            )
        else:
            # Extract error message
            stderr = proc.stderr.decode("utf-8", errors="ignore")
            stdout = proc.stdout.decode("utf-8", errors="ignore")
            error_line = ""
            for line in (stderr + stdout).split("\n"):
                if "!" in line or "Error" in line:
                    error_line = line[:100]
                    break

            return CheckResult(
                name="latex_compiles",
                passed=False,
                required=False,  # Not blocking, but a warning
                message=f"LaTeX compilation failed: {error_line}",
            )

    except subprocess.TimeoutExpired:
        return CheckResult(
            name="latex_compiles",
            passed=False,
            required=False,
            message="LaTeX compilation timed out (120s)",
        )
    except Exception as e:
        return CheckResult(
            name="latex_compiles",
            passed=None,
            required=False,
            message=f"Could not check LaTeX: {e}",
        )


def check_dependency(name: str, command: str, required: bool = True) -> CheckResult:
    """Check if a system dependency is available."""
    is_available = shutil.which(command) is not None

    return CheckResult(
        name=f"dep_{name}",
        passed=is_available,
        required=required,
        message=f"{name} {'found' if is_available else 'not found'}",
    )


def check_python_package(package: str, required: bool = True) -> CheckResult:
    """Check if a Python package is installed."""
    try:
        __import__(package)
        return CheckResult(
            name=f"pkg_{package}",
            passed=True,
            required=required,
            message=f"Python package '{package}' available",
        )
    except ImportError:
        return CheckResult(
            name=f"pkg_{package}",
            passed=False,
            required=required,
            message=f"Python package '{package}' not installed",
        )


def check_api_keys() -> CheckResult:
    """Check that required API keys are configured."""
    keys_found = []
    keys_missing = []

    # Check common API key environment variables
    api_keys = {
        "OPENAI_API_KEY": "OpenAI",
        "OPENROUTER_API_KEY": "OpenRouter",
        "ANTHROPIC_API_KEY": "Anthropic",
    }

    for env_var, name in api_keys.items():
        if os.getenv(env_var):
            keys_found.append(name)
        else:
            keys_missing.append(name)

    if keys_found:
        return CheckResult(
            name="api_keys",
            passed=True,
            message=f"API keys configured: {', '.join(keys_found)}",
        )
    else:
        return CheckResult(
            name="api_keys",
            passed=False,
            required=True,
            message="No API keys found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or OPENROUTER_API_KEY",
        )


def check_figure_resolution(
    input_dir: Path,
    min_dpi: int = 300,
    target_width_inches: float = 6.0,
) -> CheckResult:
    """Check figure resolution for poster quality."""
    figures_dir = input_dir / "figures"
    if not figures_dir.exists():
        figures_dir = input_dir / "figs"
    if not figures_dir.exists():
        # Look for figures in input_dir
        figures_dir = input_dir

    image_extensions = {".png", ".jpg", ".jpeg", ".tiff", ".tif"}
    images = [f for f in figures_dir.iterdir() if f.suffix.lower() in image_extensions]

    if not images:
        return CheckResult(
            name="figure_resolution",
            passed=None,
            required=False,
            message="No figure files found",
        )

    try:
        from PIL import Image
    except ImportError:
        return CheckResult(
            name="figure_resolution",
            passed=None,
            required=False,
            message="Skipped: PIL not installed (pip install pillow)",
        )

    low_res_images = []
    min_width_px = int(target_width_inches * min_dpi)

    for img_path in images:
        try:
            with Image.open(img_path) as im:
                if im.width < min_width_px:
                    low_res_images.append(
                        f"{img_path.name} ({im.width}px < {min_width_px}px)"
                    )
        except Exception:
            continue

    if low_res_images:
        return CheckResult(
            name="figure_resolution",
            passed=False,
            required=False,
            message=f"{len(low_res_images)} image(s) may be low resolution for poster",
            details="; ".join(low_res_images[:5]),
        )
    else:
        return CheckResult(
            name="figure_resolution",
            passed=True,
            message=f"All {len(images)} figures have adequate resolution",
        )


def estimate_paper_info(input_dir: Path) -> dict:
    """Extract information about the paper for cost estimation."""
    info = {
        "estimated_pages": 8,
        "figure_count": 5,
        "has_latex": False,
        "has_pdf": False,
        "main_file": None,
    }

    tex_files = list(input_dir.glob("*.tex"))
    pdf_files = list(input_dir.glob("*.pdf"))

    if tex_files:
        info["has_latex"] = True
        # Find main file
        for name in ["main.tex", "paper.tex", "manuscript.tex"]:
            if (input_dir / name).exists():
                info["main_file"] = name
                break
        if info["main_file"] is None:
            info["main_file"] = tex_files[0].name

        # Estimate pages from content
        try:
            content = (input_dir / info["main_file"]).read_text(encoding="utf-8", errors="ignore")
            # Rough estimate: ~4000 chars per page
            info["estimated_pages"] = max(4, len(content) // 4000)

            # Count figures
            import re
            figure_count = len(re.findall(r"\\begin\{figure", content, re.IGNORECASE))
            figure_count += len(re.findall(r"\\includegraphics", content, re.IGNORECASE))
            info["figure_count"] = max(1, figure_count // 2)  # includegraphics often inside figure

        except Exception:
            pass

    elif pdf_files:
        info["has_pdf"] = True
        info["main_file"] = pdf_files[0].name

    # Count actual figure files
    figures_dir = input_dir / "figures"
    if not figures_dir.exists():
        figures_dir = input_dir / "figs"
    if figures_dir.exists():
        image_count = len(list(figures_dir.glob("*.png"))) + len(list(figures_dir.glob("*.jpg")))
        if image_count > 0:
            info["figure_count"] = image_count

    return info


def run_preflight_checks(
    input_dir: Path,
    components: list[str],
    model_tier: str = "production",
    check_dependencies: bool = True,
) -> PreflightResult:
    """Run all preflight checks.

    Args:
        input_dir: Path to input directory
        components: List of components to generate
        model_tier: Model tier for cost estimation
        check_dependencies: Whether to check system dependencies

    Returns:
        PreflightResult with all check results
    """
    result = PreflightResult()

    # Check 1: Input exists
    result.add_check(check_input_exists(input_dir))

    # Check 2: LaTeX compiles (if applicable)
    result.add_check(check_latex_compiles(input_dir))

    # Check 3: System dependencies
    if check_dependencies:
        deps = [
            ("LibreOffice", "libreoffice", "poster" in components),
            ("Poppler", "pdftoppm", True),
            ("FFmpeg", "ffmpeg", "video" in components),
            ("ImageMagick", "convert", "poster" in components),
        ]
        for name, cmd, required in deps:
            result.add_check(check_dependency(name, cmd, required))

    # Check 4: Python packages
    packages = [
        ("aiohttp", False),
        ("beautifulsoup4", False),
        ("PIL", "poster" in components),
        ("yaml", True),
    ]
    for pkg, required in packages:
        pkg_name = pkg if pkg != "PIL" else "pillow"
        import_name = pkg if pkg != "beautifulsoup4" else "bs4"
        import_name = import_name if import_name != "PIL" else "PIL"
        result.add_check(check_python_package(import_name, required))

    # Check 5: API keys
    result.add_check(check_api_keys())

    # Check 6: Figure resolution (for poster)
    if "poster" in components:
        result.add_check(check_figure_resolution(input_dir))

    # Extract paper info
    result.paper_info = estimate_paper_info(input_dir)

    # Estimate cost
    try:
        from lib.cost_estimator import estimate_cost

        estimate = estimate_cost(
            paper_pages=result.paper_info["estimated_pages"],
            components=components,
            model_tier=model_tier,
            figure_count=result.paper_info["figure_count"],
        )
        result.cost_estimate = estimate.estimated_cost_usd

        result.add_check(CheckResult(
            name="cost_estimate",
            passed=True,
            required=False,
            message=f"Estimated cost: ${estimate.estimated_cost_usd:.2f} ({estimate.confidence} confidence)",
        ))
    except Exception as e:
        result.add_check(CheckResult(
            name="cost_estimate",
            passed=None,
            required=False,
            message=f"Could not estimate cost: {e}",
        ))

    return result


def print_report(result: PreflightResult) -> None:
    """Print formatted preflight report."""
    print("\n" + "=" * 60)
    print("PREFLIGHT CHECK REPORT")
    print("=" * 60)

    # Paper info
    if result.paper_info:
        print("\nPaper Information:")
        print(f"  Main file: {result.paper_info.get('main_file', 'Unknown')}")
        print(f"  Estimated pages: {result.paper_info.get('estimated_pages', 'Unknown')}")
        print(f"  Figure count: {result.paper_info.get('figure_count', 'Unknown')}")

    # Check results
    print("\nChecks:")
    for check in result.checks:
        if check.passed is True:
            symbol = "[OK]"
        elif check.passed is False:
            symbol = "[!!]" if check.required else "[--]"
        else:
            symbol = "[--]"

        req = "*" if check.required else " "
        print(f"  {symbol}{req} {check.name}: {check.message}")
        if check.details:
            print(f"       {check.details}")

    # Warnings
    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  - {w}")

    # Errors
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for e in result.errors:
            print(f"  - {e}")

    # Cost
    if result.cost_estimate:
        print(f"\nEstimated cost: ${result.cost_estimate:.2f}")

    # Final status
    print("\n" + "-" * 60)
    status = "READY" if result.passed else "NOT READY"
    print(f"STATUS: {status}")
    print("=" * 60)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Preflight validation for paper transformation",
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Path to paper directory",
    )
    parser.add_argument(
        "--components",
        type=str,
        default="website,poster,video",
        help="Comma-separated list of components",
    )
    parser.add_argument(
        "--model-tier",
        choices=["draft", "production", "premium", "budget"],
        default="production",
        help="Model tier for cost estimation",
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency checks",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    components = [c.strip() for c in args.components.split(",")]

    result = run_preflight_checks(
        args.input_dir,
        components=components,
        model_tier=args.model_tier,
        check_dependencies=not args.skip_deps,
    )

    if args.json:
        import json
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_report(result)

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
