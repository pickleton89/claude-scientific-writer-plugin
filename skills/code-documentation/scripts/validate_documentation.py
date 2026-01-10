#!/usr/bin/env python
"""Validate documentation meets code-documentation skill standards.

This script provides deterministic validation of:
- Python docstrings (NumPy or Google style via pydocstyle)
- Docstring examples (via doctest)
- README section completeness (by project type)

Usage:
    # Validate Python docstrings
    python validate_documentation.py module.py --style numpy

    # Validate README sections
    python validate_documentation.py --readme README.md --project-type analysis

    # Validate entire project
    python validate_documentation.py /path/to/project --all
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from utils.docstring_validator import (
    DocstringStyle,
    DocstringValidation,
    format_validation_report as format_docstring_report,
    validate_docstring_format,
)
from utils.readme_checker import (
    ProjectType,
    ReadmeValidation,
    format_validation_report as format_readme_report,
    validate_readme_sections,
)


@dataclass
class ProjectValidation:
    """Complete project documentation validation result."""

    path: str
    readme: ReadmeValidation | None = None
    python_files: list[DocstringValidation] | None = None
    valid: bool = False
    score: float = 0.0

    @property
    def summary(self) -> str:
        """One-line summary of validation result."""
        parts = []
        if self.readme:
            status = "pass" if self.readme.valid else "fail"
            parts.append(f"README: {status}")
        if self.python_files:
            passed = sum(1 for f in self.python_files if f.valid)
            total = len(self.python_files)
            parts.append(f"Python: {passed}/{total}")
        return f"[{self.score:.0f}/100] " + ", ".join(parts)


def validate_python_file(
    path: Path,
    style: DocstringStyle | str,
    run_tests: bool = True,
) -> DocstringValidation:
    """Validate a single Python file's docstrings.

    Parameters
    ----------
    path : Path
        Path to Python file.
    style : DocstringStyle | str
        Docstring style to validate against.
    run_tests : bool
        Whether to run doctests.

    Returns
    -------
    DocstringValidation
        Validation result.
    """
    return validate_docstring_format(path, style=style, run_tests=run_tests)


def validate_project(
    project_path: Path,
    style: DocstringStyle | str | None = None,
    project_type: ProjectType | str | None = None,
    run_tests: bool = True,
) -> ProjectValidation:
    """Validate entire project documentation.

    Parameters
    ----------
    project_path : Path
        Path to project directory.
    style : DocstringStyle | str | None
        Docstring style. Auto-detects if None.
    project_type : ProjectType | str | None
        Project type for README validation. Auto-detects if None.
    run_tests : bool
        Whether to run doctests.

    Returns
    -------
    ProjectValidation
        Complete project validation result.
    """
    project_path = Path(project_path)

    # Validate README
    readme_result = None
    readme_candidates = ["README.md", "README.rst", "README.txt", "README"]
    for candidate in readme_candidates:
        readme_path = project_path / candidate
        if readme_path.exists():
            readme_result = validate_readme_sections(readme_path, project_type)
            break

    # Find and validate Python files
    python_files = list(project_path.glob("**/*.py"))
    # Exclude common non-source directories
    exclude_patterns = ["venv", ".venv", "env", ".env", "__pycache__", "build", "dist"]
    python_files = [
        f
        for f in python_files
        if not any(excl in f.parts for excl in exclude_patterns)
    ]

    python_results = []
    for py_file in python_files[:50]:  # Limit to first 50 files
        result = validate_python_file(py_file, style or DocstringStyle.NUMPY, run_tests)
        python_results.append(result)

    # Calculate overall score
    score = 0.0
    valid = True

    if readme_result:
        score += readme_result.score * 0.3  # README is 30% of score
        if not readme_result.valid:
            valid = False

    if python_results:
        python_score = sum(100 if r.valid else 50 * r.coverage for r in python_results)
        python_score /= len(python_results)
        score += python_score * 0.7  # Python docs are 70% of score
        if not all(r.valid for r in python_results):
            valid = False

    return ProjectValidation(
        path=str(project_path),
        readme=readme_result,
        python_files=python_results,
        valid=valid,
        score=score,
    )


def format_project_report(validation: ProjectValidation) -> str:
    """Format complete project validation report.

    Parameters
    ----------
    validation : ProjectValidation
        Project validation result.

    Returns
    -------
    str
        Formatted report.
    """
    lines = [
        "Project Documentation Validation Report",
        "=" * 60,
        f"Project: {validation.path}",
        f"Overall Valid: {'Yes' if validation.valid else 'No'}",
        f"Overall Score: {validation.score:.1f}/100",
        "",
    ]

    if validation.readme:
        lines.append("-" * 40)
        lines.append(format_readme_report(validation.readme))
        lines.append("")

    if validation.python_files:
        lines.append("-" * 40)
        lines.append(f"Python Files Validated: {len(validation.python_files)}")
        passed = sum(1 for f in validation.python_files if f.valid)
        lines.append(f"Passing: {passed}/{len(validation.python_files)}")
        lines.append("")

        # Show failing files
        failing = [f for f in validation.python_files if not f.valid]
        if failing:
            lines.append("Files with issues:")
            for f in failing[:10]:
                issues = len(f.issues) if f.issues else 0
                doctest_status = ""
                if f.doctest_result and not f.doctest_result.success:
                    doctest_status = f", {f.doctest_result.failed} doctest failures"
                lines.append(f"  - {f.path}: {issues} pydocstyle issues{doctest_status}")

    return "\n".join(lines)


def main() -> int:
    """Main CLI entry point.

    Returns
    -------
    int
        Exit code (0 for success, 1 for validation failure).
    """
    parser = argparse.ArgumentParser(
        description="Validate documentation against code-documentation skill standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Validate Python file docstrings
    %(prog)s module.py --style numpy

    # Validate README sections
    %(prog)s --readme README.md --project-type software

    # Validate entire project
    %(prog)s /path/to/project --all

    # Quick validation (skip doctests)
    %(prog)s module.py --style google --no-tests
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        help="Python file or project directory to validate",
    )
    parser.add_argument(
        "--style",
        choices=["numpy", "google", "sphinx", "minimal"],
        default="numpy",
        help="Docstring style convention (default: numpy)",
    )
    parser.add_argument(
        "--readme",
        metavar="PATH",
        help="README file to validate",
    )
    parser.add_argument(
        "--project-type",
        choices=["analysis", "software", "data_repo", "compendium"],
        help="Project type for README validation (auto-detects if not specified)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate entire project (README + Python files)",
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip doctest execution",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output errors and summary",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.path and not args.readme:
        parser.error("Either path or --readme is required")

    exit_code = 0

    # README-only validation
    if args.readme and not args.path:
        project_type = None
        if args.project_type:
            project_type = ProjectType(args.project_type)
        result = validate_readme_sections(args.readme, project_type)

        if not args.quiet:
            print(format_readme_report(result))
        else:
            print(result.summary if hasattr(result, "summary") else f"Valid: {result.valid}")

        exit_code = 0 if result.valid else 1

    # Python file validation
    elif args.path and not args.all:
        path = Path(args.path)

        if path.is_file() and path.suffix == ".py":
            result = validate_python_file(
                path,
                DocstringStyle(args.style),
                run_tests=not args.no_tests,
            )
            if not args.quiet:
                print(format_docstring_report(result))
            else:
                print(f"Valid: {result.valid}, Coverage: {result.coverage:.0%}")
            exit_code = 0 if result.valid else 1

        elif path.is_dir():
            # Default to full project validation for directories
            args.all = True

    # Full project validation
    if args.all or (args.path and Path(args.path).is_dir()):
        project_type = None
        if args.project_type:
            project_type = ProjectType(args.project_type)

        result = validate_project(
            Path(args.path),
            style=DocstringStyle(args.style) if args.style else None,
            project_type=project_type,
            run_tests=not args.no_tests,
        )

        if not args.quiet:
            print(format_project_report(result))
        else:
            print(result.summary)

        exit_code = 0 if result.valid else 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
