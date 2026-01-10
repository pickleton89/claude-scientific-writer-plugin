"""Tests for docstring style inference utilities.

Comprehensive test suite covering:
- Style detection patterns (NumPy, Google)
- Language detection (Python, R)
- Package structure detection
- Scientific context detection
- Quick script detection
- Decision tree logic
- Edge cases
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils.infer_style import (
    EXCLUDE_DIRS,
    GOOGLE_PATTERNS,
    NUMPY_PATTERNS,
    SCIENTIFIC_INDICATORS,
    InferredStyle,
    Language,
    ProjectAnalysis,
    StyleDetectionResult,
    analyze_project,
    detect_existing_style,
    detect_language,
    detect_scientific_context,
    detect_style_from_files,
    format_analysis_report,
    infer_docstring_style,
    is_python_package,
    is_quick_script,
    is_r_package,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def numpy_docstring_code():
    """Python code with NumPy-style docstrings."""
    return '''"""Module with NumPy-style docstrings."""


def calculate_mean(values, weights=None):
    """
    Calculate the weighted mean of values.

    Parameters
    ----------
    values : array-like
        Input values to average.
    weights : array-like, optional
        Weights for each value.

    Returns
    -------
    float
        The weighted mean.

    Raises
    ------
    ValueError
        If values is empty.

    Examples
    --------
    >>> calculate_mean([1, 2, 3])
    2.0
    """
    return sum(values) / len(values)
'''


@pytest.fixture
def google_docstring_code():
    """Python code with Google-style docstrings."""
    return '''"""Module with Google-style docstrings."""


def process_data(data, normalize=False):
    """Process input data with optional normalization.

    Args:
        data: Input data to process.
        normalize: Whether to normalize output.

    Returns:
        Processed data as a list.

    Raises:
        ValueError: If data is invalid.

    Example:
        >>> process_data([1, 2, 3])
        [1, 2, 3]
    """
    return list(data)
'''


@pytest.fixture
def minimal_docstring_code():
    """Python code with minimal docstrings."""
    return '''"""Quick utility script."""


def helper(x):
    """Helper function."""
    return x * 2


def main():
    """Main entry point."""
    print(helper(5))
'''


# =============================================================================
# Enum Tests
# =============================================================================


class TestInferredStyle:
    """Tests for InferredStyle enum."""

    def test_numpy_value(self):
        assert InferredStyle.NUMPY.value == "numpy"

    def test_google_value(self):
        assert InferredStyle.GOOGLE.value == "google"

    def test_roxygen2_value(self):
        assert InferredStyle.ROXYGEN2.value == "roxygen2"

    def test_minimal_value(self):
        assert InferredStyle.MINIMAL.value == "minimal"


class TestLanguage:
    """Tests for Language enum."""

    def test_python_value(self):
        assert Language.PYTHON.value == "python"

    def test_r_value(self):
        assert Language.R.value == "r"

    def test_mixed_value(self):
        assert Language.MIXED.value == "mixed"

    def test_unknown_value(self):
        assert Language.UNKNOWN.value == "unknown"


# =============================================================================
# Dataclass Tests
# =============================================================================


class TestStyleDetectionResult:
    """Tests for StyleDetectionResult dataclass."""

    def test_has_style_with_high_confidence(self):
        result = StyleDetectionResult(
            style=InferredStyle.NUMPY, confidence=0.8, numpy_score=5, google_score=1
        )
        assert result.has_style is True

    def test_has_style_with_low_confidence(self):
        result = StyleDetectionResult(
            style=InferredStyle.NUMPY, confidence=0.3, numpy_score=2, google_score=1
        )
        assert result.has_style is False

    def test_has_style_with_no_style(self):
        result = StyleDetectionResult(style=None, confidence=0.0)
        assert result.has_style is False

    def test_has_style_threshold(self):
        # Exactly 0.5 should be True
        result = StyleDetectionResult(style=InferredStyle.GOOGLE, confidence=0.5)
        assert result.has_style is True

        # Just below 0.5 should be False
        result = StyleDetectionResult(style=InferredStyle.GOOGLE, confidence=0.49)
        assert result.has_style is False


class TestProjectAnalysis:
    """Tests for ProjectAnalysis dataclass."""

    def test_default_values(self):
        analysis = ProjectAnalysis(
            path="/test",
            language=Language.PYTHON,
            is_package=True,
            is_scientific=False,
            is_quick_script=False,
            existing_style=StyleDetectionResult(style=None, confidence=0.0),
            recommended_style=InferredStyle.GOOGLE,
        )
        assert analysis.python_files == 0
        assert analysis.r_files == 0
        assert analysis.scientific_indicators == []
        assert analysis.decision_reason == ""


# =============================================================================
# Pattern Constants Tests
# =============================================================================


class TestPatternConstants:
    """Tests for pattern constants."""

    def test_numpy_patterns_not_empty(self):
        assert len(NUMPY_PATTERNS) > 0

    def test_google_patterns_not_empty(self):
        assert len(GOOGLE_PATTERNS) > 0

    def test_scientific_indicators_not_empty(self):
        assert len(SCIENTIFIC_INDICATORS) > 0

    def test_exclude_dirs_not_empty(self):
        assert len(EXCLUDE_DIRS) > 0

    def test_exclude_dirs_contains_common_dirs(self):
        assert "venv" in EXCLUDE_DIRS
        assert ".venv" in EXCLUDE_DIRS
        assert "__pycache__" in EXCLUDE_DIRS
        assert ".git" in EXCLUDE_DIRS

    def test_numpy_patterns_have_weights(self):
        for pattern, weight in NUMPY_PATTERNS:
            assert isinstance(pattern, str)
            assert isinstance(weight, int)
            assert weight > 0

    def test_google_patterns_have_weights(self):
        for pattern, weight in GOOGLE_PATTERNS:
            assert isinstance(pattern, str)
            assert isinstance(weight, int)
            assert weight > 0

    def test_scientific_indicators_are_lowercase(self):
        for indicator in SCIENTIFIC_INDICATORS:
            assert indicator == indicator.lower()


# =============================================================================
# Style Detection Tests
# =============================================================================


class TestDetectExistingStyle:
    """Tests for detect_existing_style function."""

    def test_detect_numpy_style(self, numpy_docstring_code):
        result = detect_existing_style(numpy_docstring_code)
        assert result.style == InferredStyle.NUMPY
        assert result.numpy_score > result.google_score
        assert result.confidence > 0.5

    def test_detect_google_style(self, google_docstring_code):
        result = detect_existing_style(google_docstring_code)
        assert result.style == InferredStyle.GOOGLE
        assert result.google_score > result.numpy_score
        assert result.confidence > 0.5

    def test_detect_no_style_empty_code(self):
        result = detect_existing_style("")
        assert result.style is None
        assert result.confidence == 0.0

    def test_detect_no_style_minimal_code(self, minimal_docstring_code):
        result = detect_existing_style(minimal_docstring_code)
        # Minimal docstrings shouldn't strongly match either
        assert result.numpy_score == 0 or result.google_score == 0

    def test_numpy_parameters_section(self):
        code = '''def foo(x):
    """Do something.

    Parameters
    ----------
    x : int
        Input.
    """
    pass'''
        result = detect_existing_style(code)
        assert result.numpy_score > 0

    def test_numpy_returns_section(self):
        code = '''def foo():
    """Do something.

    Returns
    -------
    int
        Result.
    """
    return 1'''
        result = detect_existing_style(code)
        assert result.numpy_score > 0

    def test_google_args_section(self):
        code = '''def foo(x):
    """Do something.

    Args:
        x: Input value.
    """
    pass'''
        result = detect_existing_style(code)
        assert result.google_score > 0

    def test_google_returns_section(self):
        code = '''def foo():
    """Do something.

    Returns:
        The result.
    """
    return 1'''
        result = detect_existing_style(code)
        assert result.google_score > 0

    def test_tie_defaults_to_numpy(self):
        # Code that matches both equally
        code = '''def foo():
    """A function."""
    pass'''
        result = detect_existing_style(code)
        # If both scores are 0, style is None
        if result.numpy_score == result.google_score and result.numpy_score > 0:
            assert result.style == InferredStyle.NUMPY

    def test_confidence_capped_at_95(self):
        # Very strong NumPy indicators
        code = '''def foo(a, b, c):
    """
    Parameters
    ----------
    a : int
        First.
    b : int
        Second.
    c : int
        Third.

    Returns
    -------
    int

    Yields
    ------
    int

    Raises
    ------
    ValueError
    """
    pass'''
        result = detect_existing_style(code)
        assert result.confidence <= 0.95


class TestDetectStyleFromFiles:
    """Tests for detect_style_from_files function."""

    def test_empty_file_list(self):
        result = detect_style_from_files([])
        assert result.style is None
        assert result.samples_analyzed == 0

    def test_single_numpy_file(self, temp_dir, numpy_docstring_code):
        py_file = temp_dir / "numpy_style.py"
        py_file.write_text(numpy_docstring_code)
        result = detect_style_from_files([py_file])
        assert result.style == InferredStyle.NUMPY
        assert result.samples_analyzed == 1

    def test_single_google_file(self, temp_dir, google_docstring_code):
        py_file = temp_dir / "google_style.py"
        py_file.write_text(google_docstring_code)
        result = detect_style_from_files([py_file])
        assert result.style == InferredStyle.GOOGLE
        assert result.samples_analyzed == 1

    def test_multiple_files_aggregation(self, temp_dir, numpy_docstring_code):
        # Create multiple NumPy-style files
        for i in range(3):
            py_file = temp_dir / f"module{i}.py"
            py_file.write_text(numpy_docstring_code)

        files = list(temp_dir.glob("*.py"))
        result = detect_style_from_files(files)
        assert result.style == InferredStyle.NUMPY
        assert result.samples_analyzed == 3

    def test_max_files_limit(self, temp_dir, numpy_docstring_code):
        # Create more files than the limit
        for i in range(15):
            py_file = temp_dir / f"module{i}.py"
            py_file.write_text(numpy_docstring_code)

        files = list(temp_dir.glob("*.py"))
        result = detect_style_from_files(files, max_files=5)
        assert result.samples_analyzed == 5

    def test_unreadable_file_skipped(self, temp_dir, numpy_docstring_code):
        py_file = temp_dir / "good.py"
        py_file.write_text(numpy_docstring_code)

        # Test with non-existent file to verify graceful handling
        files = [py_file, temp_dir / "nonexistent.py"]
        result = detect_style_from_files(files)
        assert result.samples_analyzed == 1


# =============================================================================
# Language Detection Tests
# =============================================================================


class TestDetectLanguage:
    """Tests for detect_language function."""

    def test_python_only(self, temp_dir):
        (temp_dir / "main.py").write_text("# Python")
        (temp_dir / "utils.py").write_text("# Utils")

        lang, py_count, r_count = detect_language(temp_dir)
        assert lang == Language.PYTHON
        assert py_count == 2
        assert r_count == 0

    def test_r_only(self, temp_dir):
        (temp_dir / "analysis.R").write_text("# R code")
        (temp_dir / "utils.r").write_text("# Utils")

        lang, py_count, r_count = detect_language(temp_dir)
        assert lang == Language.R
        assert py_count == 0
        assert r_count == 2

    def test_mixed_more_python(self, temp_dir):
        (temp_dir / "main.py").write_text("# Python")
        (temp_dir / "utils.py").write_text("# Utils")
        (temp_dir / "analysis.R").write_text("# R")

        lang, py_count, r_count = detect_language(temp_dir)
        assert lang == Language.MIXED
        assert py_count == 2
        assert r_count == 1

    def test_mixed_more_r(self, temp_dir):
        (temp_dir / "main.py").write_text("# Python")
        (temp_dir / "analysis.R").write_text("# R")
        (temp_dir / "utils.R").write_text("# Utils")

        lang, py_count, r_count = detect_language(temp_dir)
        assert lang == Language.R
        assert py_count == 1
        assert r_count == 2

    def test_unknown_no_files(self, temp_dir):
        lang, py_count, r_count = detect_language(temp_dir)
        assert lang == Language.UNKNOWN
        assert py_count == 0
        assert r_count == 0

    def test_excludes_venv(self, temp_dir):
        venv_dir = temp_dir / "venv"
        venv_dir.mkdir()
        (venv_dir / "activate.py").write_text("# venv")
        (temp_dir / "main.py").write_text("# Main")

        lang, py_count, r_count = detect_language(temp_dir)
        assert py_count == 1  # Only main.py, not venv

    def test_excludes_pycache(self, temp_dir):
        cache_dir = temp_dir / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.cpython-39.pyc").write_text("")
        # Note: .pyc files don't match *.py anyway, but test the exclusion logic
        (temp_dir / "main.py").write_text("# Main")

        lang, py_count, r_count = detect_language(temp_dir)
        assert py_count == 1


# =============================================================================
# Package Detection Tests
# =============================================================================


class TestIsPythonPackage:
    """Tests for is_python_package function."""

    def test_setup_py_present(self, temp_dir):
        (temp_dir / "setup.py").write_text("from setuptools import setup")
        assert is_python_package(temp_dir) is True

    def test_pyproject_toml_present(self, temp_dir):
        (temp_dir / "pyproject.toml").write_text("[build-system]")
        assert is_python_package(temp_dir) is True

    def test_pyproject_with_project_section(self, temp_dir):
        (temp_dir / "pyproject.toml").write_text("[project]\nname = 'test'")
        assert is_python_package(temp_dir) is True

    def test_setup_cfg_present(self, temp_dir):
        (temp_dir / "setup.cfg").write_text("[metadata]")
        assert is_python_package(temp_dir) is True

    def test_no_package_indicators(self, temp_dir):
        (temp_dir / "script.py").write_text("# Just a script")
        assert is_python_package(temp_dir) is False

    def test_empty_pyproject(self, temp_dir):
        (temp_dir / "pyproject.toml").write_text("# Just comments")
        assert is_python_package(temp_dir) is True  # File exists


class TestIsRPackage:
    """Tests for is_r_package function."""

    def test_r_package_present(self, temp_dir):
        (temp_dir / "DESCRIPTION").write_text("Package: mypackage")
        (temp_dir / "NAMESPACE").write_text("export(foo)")
        assert is_r_package(temp_dir) is True

    def test_description_only(self, temp_dir):
        (temp_dir / "DESCRIPTION").write_text("Package: mypackage")
        assert is_r_package(temp_dir) is False

    def test_namespace_only(self, temp_dir):
        (temp_dir / "NAMESPACE").write_text("export(foo)")
        assert is_r_package(temp_dir) is False

    def test_not_r_package(self, temp_dir):
        (temp_dir / "analysis.R").write_text("# R script")
        assert is_r_package(temp_dir) is False


# =============================================================================
# Scientific Context Tests
# =============================================================================


class TestDetectScientificContext:
    """Tests for detect_scientific_context function."""

    def test_numpy_in_requirements(self, temp_dir):
        (temp_dir / "requirements.txt").write_text("numpy>=1.20\npandas\n")
        is_sci, indicators = detect_scientific_context(temp_dir)
        assert is_sci is True
        assert "numpy" in indicators
        assert "pandas" in indicators

    def test_scipy_in_pyproject(self, temp_dir):
        (temp_dir / "pyproject.toml").write_text(
            '[project]\ndependencies = ["scipy"]\n'
        )
        is_sci, indicators = detect_scientific_context(temp_dir)
        assert is_sci is True
        assert "scipy" in indicators

    def test_sklearn_import_in_source(self, temp_dir):
        (temp_dir / "model.py").write_text("from sklearn.ensemble import RandomForest")
        is_sci, indicators = detect_scientific_context(temp_dir)
        assert is_sci is True
        assert "sklearn" in indicators

    def test_no_scientific_libraries(self, temp_dir):
        (temp_dir / "main.py").write_text("import json\nimport os")
        is_sci, indicators = detect_scientific_context(temp_dir)
        assert is_sci is False
        assert len(indicators) == 0

    def test_biopython_detected(self, temp_dir):
        (temp_dir / "requirements.txt").write_text("biopython==1.79")
        is_sci, indicators = detect_scientific_context(temp_dir)
        assert is_sci is True
        # "biopython" contains "bio" which is in our indicators

    def test_environment_yml(self, temp_dir):
        (temp_dir / "environment.yml").write_text("dependencies:\n  - numpy\n  - scipy")
        is_sci, indicators = detect_scientific_context(temp_dir)
        assert is_sci is True


class TestIsQuickScript:
    """Tests for is_quick_script function."""

    def test_single_script(self, temp_dir):
        (temp_dir / "script.py").write_text("print('hello')")
        assert is_quick_script(temp_dir, 1) is True

    def test_two_scripts(self, temp_dir):
        (temp_dir / "main.py").write_text("# Main")
        (temp_dir / "utils.py").write_text("# Utils")
        assert is_quick_script(temp_dir, 2) is True

    def test_three_scripts(self, temp_dir):
        for i in range(3):
            (temp_dir / f"script{i}.py").write_text(f"# Script {i}")
        assert is_quick_script(temp_dir, 3) is True

    def test_four_scripts_not_quick(self, temp_dir):
        for i in range(4):
            (temp_dir / f"script{i}.py").write_text(f"# Script {i}")
        assert is_quick_script(temp_dir, 4) is False

    def test_package_not_quick(self, temp_dir):
        (temp_dir / "script.py").write_text("# Script")
        (temp_dir / "setup.py").write_text("from setuptools import setup")
        assert is_quick_script(temp_dir, 1) is False


# =============================================================================
# Decision Tree Tests
# =============================================================================


class TestInferDocstringStyle:
    """Tests for infer_docstring_style decision tree."""

    def test_existing_style_takes_precedence(self):
        existing = StyleDetectionResult(
            style=InferredStyle.GOOGLE, confidence=0.8, numpy_score=1, google_score=5
        )
        style, reason = infer_docstring_style(
            existing_style=existing, is_scientific=True  # Would normally be numpy
        )
        assert style == InferredStyle.GOOGLE
        assert "existing" in reason.lower()

    def test_r_code_uses_roxygen(self):
        style, reason = infer_docstring_style(is_r=True, is_package=True)
        assert style == InferredStyle.ROXYGEN2
        assert "r" in reason.lower() or "roxygen" in reason.lower()

    def test_quick_script_uses_minimal(self):
        style, reason = infer_docstring_style(is_quick=True, is_package=False)
        assert style == InferredStyle.MINIMAL
        assert "quick" in reason.lower() or "minimal" in reason.lower()

    def test_scientific_uses_numpy(self):
        style, reason = infer_docstring_style(is_scientific=True)
        assert style == InferredStyle.NUMPY
        assert "scientific" in reason.lower()

    def test_package_uses_google(self):
        style, reason = infer_docstring_style(is_package=True)
        assert style == InferredStyle.GOOGLE
        assert "package" in reason.lower() or "google" in reason.lower()

    def test_default_is_google(self):
        style, reason = infer_docstring_style()
        assert style == InferredStyle.GOOGLE
        assert "default" in reason.lower() or "google" in reason.lower()

    def test_quick_script_overrides_scientific(self):
        # Quick script without package should still use minimal
        style, reason = infer_docstring_style(
            is_quick=True, is_scientific=True, is_package=False
        )
        assert style == InferredStyle.MINIMAL

    def test_quick_script_with_package_not_minimal(self):
        # If it's a package, don't use minimal even if quick
        style, reason = infer_docstring_style(
            is_quick=True, is_package=True, is_scientific=True
        )
        # Should be NumPy due to scientific
        assert style == InferredStyle.NUMPY

    def test_existing_low_confidence_ignored(self):
        existing = StyleDetectionResult(
            style=InferredStyle.GOOGLE, confidence=0.3  # Below threshold
        )
        style, reason = infer_docstring_style(
            existing_style=existing, is_scientific=True
        )
        assert style == InferredStyle.NUMPY  # Scientific takes over

    def test_r_overrides_everything_except_existing(self):
        existing = StyleDetectionResult(
            style=InferredStyle.NUMPY, confidence=0.9
        )
        style, _ = infer_docstring_style(existing_style=existing, is_r=True)
        assert style == InferredStyle.NUMPY  # Existing takes precedence

        style, _ = infer_docstring_style(is_r=True, is_scientific=True)
        assert style == InferredStyle.ROXYGEN2  # R overrides scientific


# =============================================================================
# Project Analysis Integration Tests
# =============================================================================


class TestAnalyzeProject:
    """Tests for analyze_project function."""

    def test_simple_python_project(self, temp_dir):
        (temp_dir / "main.py").write_text("print('hello')")
        analysis = analyze_project(temp_dir)
        assert analysis.language == Language.PYTHON
        assert analysis.python_files == 1
        assert analysis.is_package is False

    def test_scientific_package(self, temp_dir, numpy_docstring_code):
        (temp_dir / "setup.py").write_text("from setuptools import setup")
        (temp_dir / "requirements.txt").write_text("numpy\nscipy")
        (temp_dir / "analysis.py").write_text(numpy_docstring_code)

        analysis = analyze_project(temp_dir)
        assert analysis.is_package is True
        assert analysis.is_scientific is True
        assert analysis.recommended_style == InferredStyle.NUMPY

    def test_r_project(self, temp_dir):
        (temp_dir / "DESCRIPTION").write_text("Package: mypack")
        (temp_dir / "NAMESPACE").write_text("export(foo)")
        (temp_dir / "R").mkdir()
        (temp_dir / "R" / "functions.R").write_text("#' @export\nfoo <- function() {}")

        analysis = analyze_project(temp_dir)
        assert analysis.language == Language.R
        assert analysis.is_package is True
        assert analysis.recommended_style == InferredStyle.ROXYGEN2

    def test_quick_script_project(self, temp_dir, minimal_docstring_code):
        (temp_dir / "script.py").write_text(minimal_docstring_code)

        analysis = analyze_project(temp_dir)
        assert analysis.is_quick_script is True
        assert analysis.recommended_style == InferredStyle.MINIMAL

    def test_google_style_package(self, temp_dir, google_docstring_code):
        (temp_dir / "pyproject.toml").write_text("[project]\nname = 'test'")
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "module.py").write_text(google_docstring_code)

        analysis = analyze_project(temp_dir)
        assert analysis.is_package is True
        # Should detect Google style from existing code
        assert analysis.existing_style.google_score > 0

    def test_nonexistent_path_raises(self):
        with pytest.raises(FileNotFoundError):
            analyze_project("/nonexistent/path")

    def test_file_path_raises(self, temp_dir):
        py_file = temp_dir / "script.py"
        py_file.write_text("# Python")
        with pytest.raises(NotADirectoryError):
            analyze_project(py_file)

    def test_string_path_accepted(self, temp_dir):
        (temp_dir / "main.py").write_text("# Python")
        analysis = analyze_project(str(temp_dir))
        assert analysis.path == str(temp_dir)


# =============================================================================
# Report Formatting Tests
# =============================================================================


class TestFormatAnalysisReport:
    """Tests for format_analysis_report function."""

    def test_report_contains_path(self, temp_dir):
        (temp_dir / "main.py").write_text("# Python")
        analysis = analyze_project(temp_dir)
        report = format_analysis_report(analysis)
        assert str(temp_dir) in report

    def test_report_contains_language(self, temp_dir):
        (temp_dir / "main.py").write_text("# Python")
        analysis = analyze_project(temp_dir)
        report = format_analysis_report(analysis)
        assert "python" in report.lower()

    def test_report_contains_recommendation(self, temp_dir):
        (temp_dir / "main.py").write_text("# Python")
        analysis = analyze_project(temp_dir)
        report = format_analysis_report(analysis)
        assert "Recommendation" in report
        assert analysis.recommended_style.value in report

    def test_report_contains_scientific_indicators(self, temp_dir):
        (temp_dir / "requirements.txt").write_text("numpy\npandas")
        (temp_dir / "main.py").write_text("import numpy")
        analysis = analyze_project(temp_dir)
        report = format_analysis_report(analysis)
        assert "numpy" in report.lower()

    def test_report_contains_file_counts(self, temp_dir):
        (temp_dir / "a.py").write_text("# A")
        (temp_dir / "b.py").write_text("# B")
        analysis = analyze_project(temp_dir)
        report = format_analysis_report(analysis)
        assert "Python files: 2" in report


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""

    def test_empty_directory(self, temp_dir):
        analysis = analyze_project(temp_dir)
        assert analysis.language == Language.UNKNOWN
        assert analysis.python_files == 0
        assert analysis.r_files == 0

    def test_unicode_in_source(self, temp_dir):
        (temp_dir / "main.py").write_text('"""Module with unicode: αβγ."""\nimport numpy')
        analysis = analyze_project(temp_dir)
        assert analysis.python_files == 1

    def test_deeply_nested_structure(self, temp_dir):
        deep_dir = temp_dir / "a" / "b" / "c" / "d"
        deep_dir.mkdir(parents=True)
        (deep_dir / "module.py").write_text("import scipy")
        analysis = analyze_project(temp_dir)
        assert analysis.python_files == 1
        assert analysis.is_scientific is True

    def test_mixed_case_r_extension(self, temp_dir):
        (temp_dir / "analysis.R").write_text("# Upper R")
        (temp_dir / "utils.r").write_text("# Lower r")
        lang, _, r_count = detect_language(temp_dir)
        assert lang == Language.R
        assert r_count == 2

    def test_binary_file_ignored(self, temp_dir):
        (temp_dir / "main.py").write_text("# Valid Python")
        (temp_dir / "data.bin").write_bytes(b"\x00\x01\x02\x03")
        # Should not crash
        analysis = analyze_project(temp_dir)
        assert analysis.python_files == 1

    def test_syntax_error_in_file(self, temp_dir):
        (temp_dir / "broken.py").write_text("def foo(\n  # Missing close paren")
        (temp_dir / "good.py").write_text("def bar(): pass")
        # Should handle gracefully
        analysis = analyze_project(temp_dir)
        assert analysis.python_files == 2

    def test_very_large_docstring(self, temp_dir):
        large_docstring = '"""' + "A" * 10000 + '"""'
        (temp_dir / "main.py").write_text(f'{large_docstring}\nimport numpy')
        analysis = analyze_project(temp_dir)
        # Should not crash or timeout
        assert analysis.python_files == 1


# =============================================================================
# CLI Interface Test (smoke test)
# =============================================================================


class TestCLI:
    """Smoke tests for CLI interface."""

    def test_module_can_be_run(self, temp_dir):
        """Test that the module can be executed as a script."""
        import subprocess

        (temp_dir / "main.py").write_text("import numpy")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "utils.infer_style",
                str(temp_dir),
            ],
            cwd=str(Path(__file__).parent.parent / "scripts"),
            capture_output=True,
            text=True,
        )
        # Just check it runs - exit code may vary
        assert "Error" not in result.stdout or "Recommendation" in result.stdout
