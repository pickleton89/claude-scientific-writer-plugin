"""Deterministic docstring style selection for code documentation.

Analyzes project characteristics and existing code to recommend
the appropriate docstring style following the decision tree in SKILL.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class InferredStyle(Enum):
    """Docstring styles that can be inferred."""

    NUMPY = "numpy"
    GOOGLE = "google"
    ROXYGEN2 = "roxygen2"
    MINIMAL = "minimal"


class Language(Enum):
    """Supported programming languages."""

    PYTHON = "python"
    R = "r"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class StyleDetectionResult:
    """Result of detecting existing docstring style in code."""

    style: InferredStyle | None
    confidence: float
    numpy_score: int = 0
    google_score: int = 0
    samples_analyzed: int = 0

    @property
    def has_style(self) -> bool:
        """Whether a style was confidently detected."""
        return self.style is not None and self.confidence >= 0.5


@dataclass
class ProjectAnalysis:
    """Complete analysis of a project for style recommendation."""

    path: str
    language: Language
    is_package: bool
    is_scientific: bool
    is_quick_script: bool
    existing_style: StyleDetectionResult
    recommended_style: InferredStyle
    python_files: int = 0
    r_files: int = 0
    scientific_indicators: list[str] = field(default_factory=list)
    decision_reason: str = ""


# NumPy style detection patterns (underlined sections)
NUMPY_PATTERNS = [
    (r"Parameters\n\s*-{3,}", 3),  # Strong indicator
    (r"Returns\n\s*-{3,}", 3),
    (r"Examples\n\s*-{3,}", 2),
    (r"Yields\n\s*-{3,}", 2),
    (r"Raises\n\s*-{3,}", 2),
    (r"Attributes\n\s*-{3,}", 2),
    (r"See Also\n\s*-{3,}", 1),
    (r"Notes\n\s*-{3,}", 1),
    (r"\w+\s*:\s*\w+.*\n\s{4,}\w", 1),  # param : type\n    description
]

# Google style detection patterns
GOOGLE_PATTERNS = [
    (r"Args:\n\s{2,}\w+", 3),  # Strong indicator
    (r"Returns:\n\s{2,}", 3),
    (r"Raises:\n\s{2,}\w+Error", 2),
    (r"Example:\n\s{2,}>>>", 2),
    (r"Examples:\n\s{2,}>>>", 2),
    (r"Attributes:\n\s{2,}\w+", 1),
    (r"Note:\n\s{2,}", 1),
]

# Scientific Python indicators
SCIENTIFIC_INDICATORS = [
    "numpy",
    "scipy",
    "pandas",
    "scikit-learn",
    "sklearn",
    "matplotlib",
    "seaborn",
    "statsmodels",
    "biopython",
    "astropy",
    "sympy",
    "networkx",
    "xarray",
    "dask",
]

# Directories to exclude when scanning for source files
EXCLUDE_DIRS = {"venv", ".venv", "env", ".env", "node_modules", "__pycache__", ".git"}


def detect_existing_style(code: str) -> StyleDetectionResult:
    """Detect docstring style from existing Python code.

    Analyzes the code for NumPy-style and Google-style patterns,
    returning the detected style with a confidence score.

    Parameters
    ----------
    code : str
        Python source code to analyze.

    Returns
    -------
    StyleDetectionResult
        Detection result with style, confidence, and scores.

    Examples
    --------
    >>> code = '''
    ... def foo(x):
    ...     \"\"\"Do something.
    ...
    ...     Parameters
    ...     ----------
    ...     x : int
    ...         Input value.
    ...     \"\"\"
    ...     pass
    ... '''
    >>> result = detect_existing_style(code)
    >>> result.style == InferredStyle.NUMPY
    True
    """
    numpy_score = 0
    google_score = 0

    for pattern, weight in NUMPY_PATTERNS:
        if re.search(pattern, code, re.MULTILINE):
            numpy_score += weight

    for pattern, weight in GOOGLE_PATTERNS:
        if re.search(pattern, code, re.MULTILINE):
            google_score += weight

    # Determine style and confidence
    total_score = numpy_score + google_score
    if total_score == 0:
        return StyleDetectionResult(
            style=None,
            confidence=0.0,
            numpy_score=numpy_score,
            google_score=google_score,
            samples_analyzed=1,
        )

    if numpy_score > google_score:
        confidence = numpy_score / (total_score + 1)  # +1 to dampen extreme confidence
        return StyleDetectionResult(
            style=InferredStyle.NUMPY,
            confidence=min(confidence, 0.95),
            numpy_score=numpy_score,
            google_score=google_score,
            samples_analyzed=1,
        )
    elif google_score > numpy_score:
        confidence = google_score / (total_score + 1)
        return StyleDetectionResult(
            style=InferredStyle.GOOGLE,
            confidence=min(confidence, 0.95),
            numpy_score=numpy_score,
            google_score=google_score,
            samples_analyzed=1,
        )
    else:
        # Equal scores - low confidence
        return StyleDetectionResult(
            style=InferredStyle.NUMPY,  # Default to NumPy in tie
            confidence=0.3,
            numpy_score=numpy_score,
            google_score=google_score,
            samples_analyzed=1,
        )


def detect_style_from_files(files: Sequence[Path], max_files: int = 10) -> StyleDetectionResult:
    """Detect existing docstring style from multiple files.

    Parameters
    ----------
    files : Sequence[Path]
        Python files to analyze.
    max_files : int, optional
        Maximum number of files to sample. Default is 10.

    Returns
    -------
    StyleDetectionResult
        Aggregated detection result.
    """
    if not files:
        return StyleDetectionResult(style=None, confidence=0.0, samples_analyzed=0)

    total_numpy = 0
    total_google = 0
    analyzed = 0

    for py_file in files[:max_files]:
        try:
            content = py_file.read_text(encoding="utf-8")
            result = detect_existing_style(content)
            total_numpy += result.numpy_score
            total_google += result.google_score
            analyzed += 1
        except (OSError, UnicodeDecodeError):
            continue

    if analyzed == 0:
        return StyleDetectionResult(style=None, confidence=0.0, samples_analyzed=0)

    total_score = total_numpy + total_google
    if total_score == 0:
        return StyleDetectionResult(
            style=None,
            confidence=0.0,
            numpy_score=total_numpy,
            google_score=total_google,
            samples_analyzed=analyzed,
        )

    if total_numpy > total_google:
        confidence = total_numpy / (total_score + analyzed)
        style = InferredStyle.NUMPY
    elif total_google > total_numpy:
        confidence = total_google / (total_score + analyzed)
        style = InferredStyle.GOOGLE
    else:
        confidence = 0.3
        style = InferredStyle.NUMPY

    return StyleDetectionResult(
        style=style,
        confidence=min(confidence, 0.95),
        numpy_score=total_numpy,
        google_score=total_google,
        samples_analyzed=analyzed,
    )


def detect_language(project_path: Path) -> tuple[Language, int, int]:
    """Detect primary language of a project.

    Parameters
    ----------
    project_path : Path
        Root directory of the project.

    Returns
    -------
    tuple[Language, int, int]
        (language, python_file_count, r_file_count)
    """
    py_files = list(project_path.rglob("*.py"))
    r_files = list(project_path.rglob("*.R")) + list(project_path.rglob("*.r"))

    def is_source_file(p: Path) -> bool:
        return not any(excluded in p.parts for excluded in EXCLUDE_DIRS)

    py_count = len([f for f in py_files if is_source_file(f)])
    r_count = len([f for f in r_files if is_source_file(f)])

    if py_count == 0 and r_count == 0:
        return Language.UNKNOWN, 0, 0
    elif r_count > py_count:
        return Language.R, py_count, r_count
    elif py_count > 0 and r_count > 0:
        return Language.MIXED, py_count, r_count
    else:
        return Language.PYTHON, py_count, r_count


def is_python_package(project_path: Path) -> bool:
    """Determine if project is a Python package.

    Parameters
    ----------
    project_path : Path
        Root directory of the project.

    Returns
    -------
    bool
        True if project appears to be a package.
    """
    # Standard package indicators
    package_files = [
        "setup.py",
        "pyproject.toml",
        "setup.cfg",
    ]

    for pf in package_files:
        if (project_path / pf).exists():
            return True

    return False


def is_r_package(project_path: Path) -> bool:
    """Determine if project is an R package.

    Parameters
    ----------
    project_path : Path
        Root directory of the project.

    Returns
    -------
    bool
        True if project appears to be an R package.
    """
    # R package indicators
    return (project_path / "DESCRIPTION").exists() and (project_path / "NAMESPACE").exists()


def detect_scientific_context(
    project_path: Path, max_files: int = 10
) -> tuple[bool, list[str]]:
    """Detect if project is scientific Python.

    Parameters
    ----------
    project_path : Path
        Root directory of the project.
    max_files : int, optional
        Maximum files to sample. Default is 10.

    Returns
    -------
    tuple[bool, list[str]]
        (is_scientific, list of detected indicators)
    """
    found_indicators: list[str] = []

    # Check requirements files
    req_files = ["requirements.txt", "pyproject.toml", "setup.py", "environment.yml"]
    for req_file in req_files:
        req_path = project_path / req_file
        if req_path.exists():
            try:
                content = req_path.read_text(encoding="utf-8").lower()
                for indicator in SCIENTIFIC_INDICATORS:
                    if indicator in content and indicator not in found_indicators:
                        found_indicators.append(indicator)
            except (OSError, UnicodeDecodeError):
                continue

    # If no indicators in config, check source files
    if not found_indicators:
        py_files = list(project_path.rglob("*.py"))
        source_files = [f for f in py_files if not any(ex in f.parts for ex in EXCLUDE_DIRS)]

        for py_file in source_files[:max_files]:
            try:
                content = py_file.read_text(encoding="utf-8").lower()
                for indicator in SCIENTIFIC_INDICATORS:
                    if f"import {indicator}" in content or f"from {indicator}" in content:
                        if indicator not in found_indicators:
                            found_indicators.append(indicator)
            except (OSError, UnicodeDecodeError):
                continue

    return len(found_indicators) > 0, found_indicators


def is_quick_script(project_path: Path, py_file_count: int) -> bool:
    """Determine if project is a quick/one-off script.

    Parameters
    ----------
    project_path : Path
        Root directory of the project.
    py_file_count : int
        Number of Python files detected.

    Returns
    -------
    bool
        True if project appears to be a quick script.
    """
    # Quick scripts have few files and no package structure
    if py_file_count > 3:
        return False

    # No package indicators
    if is_python_package(project_path):
        return False

    # Check if it's just scripts in root
    py_files = list(project_path.glob("*.py"))
    return len(py_files) >= 1 and py_file_count <= 3


def infer_docstring_style(
    existing_style: StyleDetectionResult | None = None,
    is_r: bool = False,
    is_package: bool = False,
    is_scientific: bool = False,
    is_quick: bool = False,
) -> tuple[InferredStyle, str]:
    """Deterministic style selection implementing SKILL.md decision tree.

    Decision tree (from SKILL.md):
    1. If existing style in codebase -> match it
    2. If R code -> roxygen2
    3. If not a package and quick script -> minimal
    4. If scientific Python -> numpy
    5. Default -> google

    Parameters
    ----------
    existing_style : StyleDetectionResult | None, optional
        Detected existing style in the codebase.
    is_r : bool, optional
        Whether the project is primarily R code.
    is_package : bool, optional
        Whether the project is a package.
    is_scientific : bool, optional
        Whether the project uses scientific Python libraries.
    is_quick : bool, optional
        Whether this is a quick/one-off script.

    Returns
    -------
    tuple[InferredStyle, str]
        (recommended_style, decision_reason)

    Examples
    --------
    >>> style, reason = infer_docstring_style(is_scientific=True, is_package=True)
    >>> style == InferredStyle.NUMPY
    True
    >>> "scientific" in reason.lower()
    True
    """
    # 1. Match existing style if detected
    if existing_style is not None and existing_style.has_style:
        return existing_style.style, "Matches existing codebase style"

    # 2. R code -> roxygen2
    if is_r:
        return InferredStyle.ROXYGEN2, "R code uses roxygen2 documentation"

    # 3. Quick script without package -> minimal
    if is_quick and not is_package:
        return InferredStyle.MINIMAL, "Quick script with minimal documentation needs"

    # 4. Scientific Python -> numpy
    if is_scientific:
        return InferredStyle.NUMPY, "Scientific Python project (numpy/scipy ecosystem standard)"

    # 5. Package -> google (modern default)
    if is_package:
        return InferredStyle.GOOGLE, "Python package using Google style (modern default)"

    # 6. Default fallback
    return InferredStyle.GOOGLE, "Default Google style for general Python"


def analyze_project(project_path: str | Path) -> ProjectAnalysis:
    """Analyze a project to determine recommended documentation style.

    Performs comprehensive analysis including:
    - Language detection (Python vs R)
    - Package structure detection
    - Scientific library usage
    - Existing docstring style detection

    Parameters
    ----------
    project_path : str | Path
        Path to the project root directory.

    Returns
    -------
    ProjectAnalysis
        Complete analysis with recommendation.

    Raises
    ------
    FileNotFoundError
        If project_path does not exist.
    NotADirectoryError
        If project_path is not a directory.

    Examples
    --------
    >>> import tempfile
    >>> from pathlib import Path
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     p = Path(tmpdir)
    ...     _ = (p / "script.py").write_text("import numpy\\ndef foo(): pass")
    ...     result = analyze_project(p)
    ...     result.is_scientific
    True
    """
    path = Path(project_path)

    if not path.exists():
        raise FileNotFoundError(f"Project path does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {path}")

    # Detect language
    language, py_count, r_count = detect_language(path)
    is_r = language == Language.R

    # Detect package status
    if is_r:
        is_package = is_r_package(path)
    else:
        is_package = is_python_package(path)

    # Detect scientific context
    is_scientific, indicators = detect_scientific_context(path)

    # Detect existing style (only for Python)
    existing_style = StyleDetectionResult(style=None, confidence=0.0, samples_analyzed=0)
    if language in (Language.PYTHON, Language.MIXED):
        py_files = list(path.rglob("*.py"))
        source_files = [f for f in py_files if not any(ex in f.parts for ex in EXCLUDE_DIRS)]
        existing_style = detect_style_from_files(source_files)

    # Detect quick script
    is_quick = is_quick_script(path, py_count)

    # Get recommendation
    recommended, reason = infer_docstring_style(
        existing_style=existing_style,
        is_r=is_r,
        is_package=is_package,
        is_scientific=is_scientific,
        is_quick=is_quick,
    )

    return ProjectAnalysis(
        path=str(path),
        language=language,
        is_package=is_package,
        is_scientific=is_scientific,
        is_quick_script=is_quick,
        existing_style=existing_style,
        recommended_style=recommended,
        python_files=py_count,
        r_files=r_count,
        scientific_indicators=indicators,
        decision_reason=reason,
    )


def format_analysis_report(analysis: ProjectAnalysis) -> str:
    """Format project analysis as human-readable report.

    Parameters
    ----------
    analysis : ProjectAnalysis
        Analysis result to format.

    Returns
    -------
    str
        Formatted report string.
    """
    lines = [
        "Project Style Analysis Report",
        "=" * 50,
        f"Path: {analysis.path}",
        f"Language: {analysis.language.value}",
        f"  Python files: {analysis.python_files}",
        f"  R files: {analysis.r_files}",
        "",
        "Project Characteristics:",
        f"  Is package: {'Yes' if analysis.is_package else 'No'}",
        f"  Is scientific: {'Yes' if analysis.is_scientific else 'No'}",
        f"  Is quick script: {'Yes' if analysis.is_quick_script else 'No'}",
    ]

    if analysis.scientific_indicators:
        lines.append(f"  Scientific libraries: {', '.join(analysis.scientific_indicators)}")

    lines.extend([
        "",
        "Existing Style Detection:",
        f"  Style: {analysis.existing_style.style.value if analysis.existing_style.style else 'None detected'}",
        f"  Confidence: {analysis.existing_style.confidence:.0%}",
        f"  NumPy score: {analysis.existing_style.numpy_score}",
        f"  Google score: {analysis.existing_style.google_score}",
        f"  Files analyzed: {analysis.existing_style.samples_analyzed}",
        "",
        "Recommendation:",
        f"  Style: {analysis.recommended_style.value}",
        f"  Reason: {analysis.decision_reason}",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python infer_style.py <project_path>")
        sys.exit(1)

    try:
        analysis = analyze_project(sys.argv[1])
        print(format_analysis_report(analysis))
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        sys.exit(1)
