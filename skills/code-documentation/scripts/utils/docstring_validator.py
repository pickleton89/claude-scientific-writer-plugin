"""Docstring validation utilities for code documentation skill.

Validates Python docstrings against style conventions (NumPy, Google)
and runs doctests to verify examples execute correctly.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class DocstringStyle(Enum):
    """Supported docstring styles."""

    NUMPY = "numpy"
    GOOGLE = "google"
    SPHINX = "sphinx"
    MINIMAL = "minimal"
    UNKNOWN = "unknown"


class ValidationSeverity(Enum):
    """Severity level of validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Single validation issue found in docstrings."""

    file: str
    line: int
    code: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.code} - {self.message}"


@dataclass
class DoctestResult:
    """Result of running doctests."""

    file: str
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.failed == 0 and len(self.errors) == 0


@dataclass
class DocstringValidation:
    """Complete docstring validation result for a file or module."""

    path: str
    style: DocstringStyle
    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    doctest_result: DoctestResult | None = None
    functions_documented: int = 0
    functions_total: int = 0
    classes_documented: int = 0
    classes_total: int = 0
    error: str | None = None

    @property
    def coverage(self) -> float:
        """Documentation coverage ratio."""
        total = self.functions_total + self.classes_total
        documented = self.functions_documented + self.classes_documented
        if total == 0:
            return 1.0
        return documented / total

    @property
    def pydocstyle_passed(self) -> bool:
        """Whether pydocstyle validation passed."""
        return len([i for i in self.issues if i.severity == ValidationSeverity.ERROR]) == 0

    @property
    def doctests_passed(self) -> bool:
        """Whether doctests passed."""
        return self.doctest_result is None or self.doctest_result.success


# NumPy style section patterns
NUMPY_SECTIONS = [
    "Parameters",
    "Returns",
    "Yields",
    "Raises",
    "Warns",
    "Other Parameters",
    "Attributes",
    "Methods",
    "See Also",
    "Notes",
    "References",
    "Examples",
]

# Google style section patterns
GOOGLE_SECTIONS = [
    "Args",
    "Arguments",
    "Returns",
    "Yields",
    "Raises",
    "Attributes",
    "Example",
    "Examples",
    "Note",
    "Notes",
    "Todo",
]


def detect_docstring_style(content: str) -> DocstringStyle:
    """Detect docstring style from code content.

    Analyzes docstrings in the code to determine which style is used.

    Parameters
    ----------
    content : str
        Python source code content.

    Returns
    -------
    DocstringStyle
        Detected docstring style.
    """
    # NumPy style indicators (underlined sections)
    numpy_patterns = [
        r"Parameters\n\s*-{3,}",
        r"Returns\n\s*-{3,}",
        r"Examples\n\s*-{3,}",
        r"\w+\s*:\s*\w+\n\s+\w",  # param : type pattern
    ]

    # Google style indicators (indented with colon)
    google_patterns = [
        r"Args:\n\s+\w+",
        r"Returns:\n\s+",
        r"Raises:\n\s+\w+Error",
        r"Example:\n\s+>>>",
    ]

    numpy_score = sum(1 for p in numpy_patterns if re.search(p, content))
    google_score = sum(1 for p in google_patterns if re.search(p, content))

    if numpy_score > google_score:
        return DocstringStyle.NUMPY
    elif google_score > numpy_score:
        return DocstringStyle.GOOGLE
    elif numpy_score > 0 or google_score > 0:
        return DocstringStyle.UNKNOWN

    # Check for minimal docstrings (single line)
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring and "\n" not in docstring.strip():
                    return DocstringStyle.MINIMAL
    except SyntaxError:
        pass

    return DocstringStyle.UNKNOWN


def _count_documented_items(content: str) -> tuple[int, int, int, int]:
    """Count documented vs total functions and classes.

    Parameters
    ----------
    content : str
        Python source code.

    Returns
    -------
    tuple[int, int, int, int]
        (functions_documented, functions_total, classes_documented, classes_total)
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return 0, 0, 0, 0

    functions_doc = 0
    functions_total = 0
    classes_doc = 0
    classes_total = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip private functions (single underscore OK, dunder skip)
            if node.name.startswith("__") and node.name.endswith("__"):
                if node.name not in ("__init__", "__new__", "__call__"):
                    continue
            functions_total += 1
            if ast.get_docstring(node):
                functions_doc += 1
        elif isinstance(node, ast.ClassDef):
            classes_total += 1
            if ast.get_docstring(node):
                classes_doc += 1

    return functions_doc, functions_total, classes_doc, classes_total


def run_pydocstyle(
    path: str | Path,
    style: DocstringStyle | str = DocstringStyle.NUMPY,
    ignore_codes: Sequence[str] | None = None,
) -> list[ValidationIssue]:
    """Run pydocstyle on a Python file.

    Parameters
    ----------
    path : str | Path
        Path to Python file to validate.
    style : DocstringStyle | str, optional
        Docstring style convention. Default is numpy.
    ignore_codes : Sequence[str] | None, optional
        List of pydocstyle codes to ignore (e.g., ["D100", "D104"]).

    Returns
    -------
    list[ValidationIssue]
        List of validation issues found.
    """
    path = Path(path)

    # Convert style enum to convention name
    if isinstance(style, DocstringStyle):
        convention = style.value if style != DocstringStyle.UNKNOWN else "numpy"
    else:
        convention = style

    # Map our style names to pydocstyle conventions
    convention_map = {
        "numpy": "numpy",
        "google": "google",
        "sphinx": "pep257",
        "minimal": "pep257",
    }
    pydocstyle_convention = convention_map.get(convention, "numpy")

    cmd = [sys.executable, "-m", "pydocstyle", f"--convention={pydocstyle_convention}"]

    if ignore_codes:
        cmd.append(f"--ignore={','.join(ignore_codes)}")

    cmd.append(str(path))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        return [
            ValidationIssue(
                file=str(path),
                line=0,
                code="TOOL_ERROR",
                message="pydocstyle module not found. Ensure pydocstyle is installed: pip install pydocstyle",
                severity=ValidationSeverity.ERROR,
            )
        ]
    except subprocess.TimeoutExpired:
        return [
            ValidationIssue(
                file=str(path),
                line=0,
                code="TIMEOUT",
                message="pydocstyle timed out",
                severity=ValidationSeverity.ERROR,
            )
        ]

    # Parse pydocstyle output
    issues = []
    output = result.stdout + result.stderr

    # Pattern: file.py:10 in public function `func_name`:
    #         D103: Missing docstring in public function
    pattern = re.compile(
        r"(.+?):(\d+)\s+(?:in .+?)?\n?\s*(D\d{3}):\s*(.+?)(?=\n\S|\Z)",
        re.MULTILINE,
    )

    for match in pattern.finditer(output):
        file_path, line_num, code, message = match.groups()
        issues.append(
            ValidationIssue(
                file=file_path.strip(),
                line=int(line_num),
                code=code,
                message=message.strip(),
                severity=ValidationSeverity.ERROR,
            )
        )

    return issues


def run_doctests(path: str | Path, verbose: bool = False) -> DoctestResult:
    """Run doctests in a Python file.

    Parameters
    ----------
    path : str | Path
        Path to Python file to test.
    verbose : bool, optional
        Whether to include verbose output. Default is False.

    Returns
    -------
    DoctestResult
        Result of doctest execution.
    """
    path = Path(path)

    cmd = [sys.executable, "-m", "doctest", str(path)]
    if verbose:
        cmd.append("-v")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return DoctestResult(
            file=str(path),
            errors=["Doctest execution timed out (>120s)"],
        )

    # Parse doctest output
    output = result.stdout + result.stderr

    # Extract test counts from verbose output
    passed = 0
    failed = 0
    errors = []

    # Look for summary line: "X items passed all tests"
    passed_match = re.search(r"(\d+)\s+items?\s+passed\s+all\s+tests", output)
    if passed_match:
        passed = int(passed_match.group(1))

    # Look for failure summary
    failed_match = re.search(r"(\d+)\s+items?\s+had\s+failures", output)
    if failed_match:
        failed = int(failed_match.group(1))

    # Alternative: look for "X tests in Y items"
    total_match = re.search(r"(\d+)\s+tests?\s+in\s+(\d+)\s+items?", output)
    if total_match and not passed_match:
        if result.returncode == 0:
            passed = int(total_match.group(1))

    # Capture failure details
    if result.returncode != 0:
        # Extract failed test details
        failure_pattern = re.compile(
            r"Failed example:\n\s+(.+?)\nExpected:\n\s+(.+?)\nGot:\n\s+(.+?)(?=\n\*{3}|\Z)",
            re.DOTALL,
        )
        for match in failure_pattern.finditer(output):
            example, expected, got = match.groups()
            errors.append(f"Failed: {example.strip()}\n  Expected: {expected.strip()}\n  Got: {got.strip()}")

        # If no specific failures found but return code nonzero
        if not errors and "Error" in output:
            errors.append(output.strip()[-500:])  # Last 500 chars

    return DoctestResult(
        file=str(path),
        passed=passed,
        failed=failed,
        errors=errors,
    )


def validate_docstring_format(
    path: str | Path,
    style: DocstringStyle | str | None = None,
    run_tests: bool = True,
    ignore_codes: Sequence[str] | None = None,
) -> DocstringValidation:
    """Validate docstrings in a Python file.

    Combines pydocstyle checking, doctest execution, and coverage analysis.

    Parameters
    ----------
    path : str | Path
        Path to Python file.
    style : DocstringStyle | str | None, optional
        Docstring style to validate. Auto-detects if None.
    run_tests : bool, optional
        Whether to run doctests. Default is True.
    ignore_codes : Sequence[str] | None, optional
        pydocstyle codes to ignore.

    Returns
    -------
    DocstringValidation
        Complete validation result.
    """
    path = Path(path)

    # Read file content
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return DocstringValidation(
            path=str(path),
            style=DocstringStyle.UNKNOWN,
            valid=False,
            error=f"File not found: {path}",
        )
    except Exception as e:
        return DocstringValidation(
            path=str(path),
            style=DocstringStyle.UNKNOWN,
            valid=False,
            error=f"Error reading file: {e}",
        )

    # Detect or use provided style
    if style is None:
        detected_style = detect_docstring_style(content)
    elif isinstance(style, str):
        try:
            detected_style = DocstringStyle(style)
        except ValueError:
            detected_style = DocstringStyle.UNKNOWN
    else:
        detected_style = style

    # Count documented items
    func_doc, func_total, class_doc, class_total = _count_documented_items(content)

    # Run pydocstyle
    issues = run_pydocstyle(path, detected_style, ignore_codes)

    # Run doctests if requested
    doctest_result = None
    if run_tests:
        doctest_result = run_doctests(path)

    # Determine overall validity
    has_errors = any(i.severity == ValidationSeverity.ERROR for i in issues)
    doctest_failed = doctest_result is not None and not doctest_result.success
    valid = not has_errors and not doctest_failed

    return DocstringValidation(
        path=str(path),
        style=detected_style,
        valid=valid,
        issues=issues,
        doctest_result=doctest_result,
        functions_documented=func_doc,
        functions_total=func_total,
        classes_documented=class_doc,
        classes_total=class_total,
    )


def format_validation_report(validation: DocstringValidation) -> str:
    """Format validation result as human-readable report.

    Parameters
    ----------
    validation : DocstringValidation
        Validation result to format.

    Returns
    -------
    str
        Formatted report string.
    """
    lines = [
        "Docstring Validation Report",
        "=" * 50,
        f"File: {validation.path}",
        f"Style: {validation.style.value}",
        f"Valid: {'Yes' if validation.valid else 'No'}",
        f"Coverage: {validation.coverage:.0%}",
        f"  Functions: {validation.functions_documented}/{validation.functions_total}",
        f"  Classes: {validation.classes_documented}/{validation.classes_total}",
        "",
    ]

    if validation.error:
        lines.append(f"Error: {validation.error}")
        return "\n".join(lines)

    if validation.issues:
        lines.append(f"pydocstyle Issues ({len(validation.issues)}):")
        for issue in validation.issues[:20]:  # Limit to first 20
            lines.append(f"  {issue}")
        if len(validation.issues) > 20:
            lines.append(f"  ... and {len(validation.issues) - 20} more")
        lines.append("")

    if validation.doctest_result:
        dt = validation.doctest_result
        lines.append("Doctest Results:")
        lines.append(f"  Passed: {dt.passed}")
        lines.append(f"  Failed: {dt.failed}")
        if dt.errors:
            lines.append("  Errors:")
            for err in dt.errors[:5]:
                lines.append(f"    {err[:100]}...")
        lines.append("")

    return "\n".join(lines)
