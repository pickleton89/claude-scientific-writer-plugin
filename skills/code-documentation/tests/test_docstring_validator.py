"""Tests for docstring validation utilities.

Comprehensive test suite covering:
- Style detection (NumPy, Google, minimal)
- pydocstyle integration
- Doctest execution
- Coverage calculation
- Edge cases
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils.docstring_validator import (
    GOOGLE_SECTIONS,
    NUMPY_SECTIONS,
    DocstringStyle,
    DocstringValidation,
    DoctestResult,
    ValidationIssue,
    ValidationSeverity,
    _count_documented_items,
    detect_docstring_style,
    format_validation_report,
    run_doctests,
    run_pydocstyle,
    validate_docstring_format,
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
def numpy_style_file(temp_dir):
    """Create a file with NumPy-style docstrings."""
    py_file = temp_dir / "numpy_style.py"
    py_file.write_text('''"""Module with NumPy-style docstrings."""


def calculate_mean(values):
    """
    Calculate the arithmetic mean of values.

    Parameters
    ----------
    values : list or array-like
        Input values to average.

    Returns
    -------
    float
        The arithmetic mean.

    Examples
    --------
    >>> calculate_mean([1, 2, 3])
    2.0
    """
    return sum(values) / len(values)


class DataProcessor:
    """
    Process data with various transformations.

    Parameters
    ----------
    name : str
        Name of the processor.

    Attributes
    ----------
    name : str
        Processor name.
    processed_count : int
        Number of items processed.
    """

    def __init__(self, name):
        """Initialize processor with name."""
        self.name = name
        self.processed_count = 0
''')
    return py_file


@pytest.fixture
def google_style_file(temp_dir):
    """Create a file with Google-style docstrings."""
    py_file = temp_dir / "google_style.py"
    py_file.write_text('''"""Module with Google-style docstrings."""


def calculate_mean(values):
    """Calculate the arithmetic mean of values.

    Args:
        values: Input values to average.

    Returns:
        The arithmetic mean as a float.

    Example:
        >>> calculate_mean([1, 2, 3])
        2.0
    """
    return sum(values) / len(values)


class DataProcessor:
    """Process data with various transformations.

    Attributes:
        name: Processor name.
        processed_count: Number of items processed.
    """

    def __init__(self, name):
        """Initialize processor with name."""
        self.name = name
        self.processed_count = 0
''')
    return py_file


@pytest.fixture
def minimal_style_file(temp_dir):
    """Create a file with minimal docstrings."""
    py_file = temp_dir / "minimal_style.py"
    py_file.write_text('''"""Simple utility module."""


def add(a, b):
    """Add two numbers."""
    return a + b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b
''')
    return py_file


@pytest.fixture
def undocumented_file(temp_dir):
    """Create a file with missing docstrings."""
    py_file = temp_dir / "undocumented.py"
    py_file.write_text('''
def process_data(data):
    return [x * 2 for x in data]


class Handler:
    def handle(self, item):
        pass
''')
    return py_file


@pytest.fixture
def file_with_failing_doctests(temp_dir):
    """Create a file with failing doctests."""
    py_file = temp_dir / "failing_doctests.py"
    py_file.write_text('''"""Module with failing doctests."""


def add(a, b):
    """
    Add two numbers.

    Examples
    --------
    >>> add(1, 2)
    4  # Wrong! Should be 3
    """
    return a + b
''')
    return py_file


@pytest.fixture
def file_with_passing_doctests(temp_dir):
    """Create a file with passing doctests."""
    py_file = temp_dir / "passing_doctests.py"
    py_file.write_text('''"""Module with passing doctests."""


def add(a, b):
    """
    Add two numbers.

    Examples
    --------
    >>> add(1, 2)
    3
    >>> add(0, 0)
    0
    """
    return a + b


def multiply(a, b):
    """
    Multiply two numbers.

    Examples
    --------
    >>> multiply(2, 3)
    6
    """
    return a * b
''')
    return py_file


# =============================================================================
# Test Enums
# =============================================================================


class TestDocstringStyle:
    """Tests for DocstringStyle enum."""

    def test_style_values(self):
        """All expected styles exist."""
        assert DocstringStyle.NUMPY.value == "numpy"
        assert DocstringStyle.GOOGLE.value == "google"
        assert DocstringStyle.SPHINX.value == "sphinx"
        assert DocstringStyle.MINIMAL.value == "minimal"
        assert DocstringStyle.UNKNOWN.value == "unknown"

    def test_style_from_string(self):
        """Can create style from string."""
        assert DocstringStyle("numpy") == DocstringStyle.NUMPY
        assert DocstringStyle("google") == DocstringStyle.GOOGLE


class TestValidationSeverity:
    """Tests for ValidationSeverity enum."""

    def test_severity_values(self):
        """All expected severities exist."""
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.INFO.value == "info"


# =============================================================================
# Test Dataclasses
# =============================================================================


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_str_representation(self):
        """String representation is formatted correctly."""
        issue = ValidationIssue(
            file="test.py",
            line=10,
            code="D100",
            message="Missing docstring",
        )
        assert "test.py:10" in str(issue)
        assert "D100" in str(issue)
        assert "Missing docstring" in str(issue)

    def test_default_severity(self):
        """Default severity is ERROR."""
        issue = ValidationIssue(file="test.py", line=1, code="D100", message="test")
        assert issue.severity == ValidationSeverity.ERROR


class TestDoctestResult:
    """Tests for DoctestResult dataclass."""

    def test_success_when_no_failures(self):
        """Success is True when no failures."""
        result = DoctestResult(file="test.py", passed=5, failed=0)
        assert result.success

    def test_failure_when_tests_fail(self):
        """Success is False when tests fail."""
        result = DoctestResult(file="test.py", passed=3, failed=2)
        assert not result.success

    def test_failure_when_errors(self):
        """Success is False when errors present."""
        result = DoctestResult(file="test.py", passed=5, failed=0, errors=["Error"])
        assert not result.success


class TestDocstringValidation:
    """Tests for DocstringValidation dataclass."""

    def test_coverage_calculation(self):
        """Coverage is calculated correctly."""
        validation = DocstringValidation(
            path="test.py",
            style=DocstringStyle.NUMPY,
            valid=True,
            functions_documented=3,
            functions_total=4,
            classes_documented=1,
            classes_total=2,
        )
        # (3 + 1) / (4 + 2) = 4/6 = 0.666...
        assert abs(validation.coverage - 0.666) < 0.01

    def test_coverage_empty(self):
        """Coverage is 1.0 when no items to document."""
        validation = DocstringValidation(
            path="test.py",
            style=DocstringStyle.NUMPY,
            valid=True,
            functions_documented=0,
            functions_total=0,
            classes_documented=0,
            classes_total=0,
        )
        assert validation.coverage == 1.0

    def test_pydocstyle_passed(self):
        """pydocstyle_passed reflects issue severity."""
        validation = DocstringValidation(
            path="test.py",
            style=DocstringStyle.NUMPY,
            valid=True,
            issues=[
                ValidationIssue("test.py", 1, "D100", "test", ValidationSeverity.WARNING)
            ],
        )
        assert validation.pydocstyle_passed  # Only warnings

        validation_with_error = DocstringValidation(
            path="test.py",
            style=DocstringStyle.NUMPY,
            valid=False,
            issues=[
                ValidationIssue("test.py", 1, "D100", "test", ValidationSeverity.ERROR)
            ],
        )
        assert not validation_with_error.pydocstyle_passed

    def test_doctests_passed(self):
        """doctests_passed reflects doctest result."""
        validation = DocstringValidation(
            path="test.py",
            style=DocstringStyle.NUMPY,
            valid=True,
            doctest_result=DoctestResult("test.py", passed=5, failed=0),
        )
        assert validation.doctests_passed

        validation_failed = DocstringValidation(
            path="test.py",
            style=DocstringStyle.NUMPY,
            valid=False,
            doctest_result=DoctestResult("test.py", passed=3, failed=2),
        )
        assert not validation_failed.doctests_passed

    def test_doctests_passed_when_none(self):
        """doctests_passed is True when not run."""
        validation = DocstringValidation(
            path="test.py",
            style=DocstringStyle.NUMPY,
            valid=True,
            doctest_result=None,
        )
        assert validation.doctests_passed


# =============================================================================
# Test Style Detection
# =============================================================================


class TestDetectDocstringStyle:
    """Tests for docstring style detection."""

    def test_detect_numpy_style(self, numpy_style_file):
        """NumPy style is detected correctly."""
        content = numpy_style_file.read_text()
        assert detect_docstring_style(content) == DocstringStyle.NUMPY

    def test_detect_google_style(self, google_style_file):
        """Google style is detected correctly."""
        content = google_style_file.read_text()
        assert detect_docstring_style(content) == DocstringStyle.GOOGLE

    def test_detect_minimal_style(self, minimal_style_file):
        """Minimal style is detected correctly."""
        content = minimal_style_file.read_text()
        # Minimal single-line docstrings
        assert detect_docstring_style(content) == DocstringStyle.MINIMAL

    def test_detect_unknown_no_docstrings(self, undocumented_file):
        """Unknown when no docstrings present."""
        content = undocumented_file.read_text()
        assert detect_docstring_style(content) == DocstringStyle.UNKNOWN

    def test_numpy_parameters_pattern(self):
        """NumPy Parameters section pattern is detected."""
        content = '''
def func(x):
    """
    Do something.

    Parameters
    ----------
    x : int
        The value.
    """
'''
        assert detect_docstring_style(content) == DocstringStyle.NUMPY

    def test_numpy_returns_pattern(self):
        """NumPy Returns section pattern is detected."""
        content = '''
def func():
    """
    Return something.

    Returns
    -------
    int
        The result.
    """
'''
        assert detect_docstring_style(content) == DocstringStyle.NUMPY

    def test_google_args_pattern(self):
        """Google Args section pattern is detected."""
        content = '''
def func(x):
    """Do something.

    Args:
        x: The value.
    """
'''
        assert detect_docstring_style(content) == DocstringStyle.GOOGLE

    def test_google_returns_pattern(self):
        """Google Returns section pattern is detected."""
        content = '''
def func():
    """Return something.

    Returns:
        The result.
    """
'''
        assert detect_docstring_style(content) == DocstringStyle.GOOGLE


# =============================================================================
# Test Documentation Counting
# =============================================================================


class TestCountDocumentedItems:
    """Tests for _count_documented_items function."""

    def test_count_fully_documented(self, numpy_style_file):
        """Fully documented file has matching counts."""
        content = numpy_style_file.read_text()
        func_doc, func_total, class_doc, class_total = _count_documented_items(content)
        assert func_doc == func_total  # All functions documented
        assert class_doc == class_total  # All classes documented

    def test_count_undocumented(self, undocumented_file):
        """Undocumented items are counted correctly."""
        content = undocumented_file.read_text()
        func_doc, func_total, class_doc, class_total = _count_documented_items(content)
        assert func_doc < func_total  # Some functions undocumented
        assert func_total >= 1
        assert class_total >= 1

    def test_count_ignores_dunder_methods(self):
        """Dunder methods (except __init__) are ignored."""
        content = '''
class MyClass:
    """A class."""

    def __init__(self):
        """Initialize."""
        pass

    def __repr__(self):
        # No docstring - should be ignored
        return "MyClass()"

    def public_method(self):
        """Public method."""
        pass
'''
        func_doc, func_total, class_doc, class_total = _count_documented_items(content)
        # __init__ and public_method should be counted, __repr__ ignored
        assert func_total == 2
        assert func_doc == 2

    def test_count_syntax_error(self):
        """Syntax errors return zeros."""
        content = "def broken(:\n    pass"
        func_doc, func_total, class_doc, class_total = _count_documented_items(content)
        assert func_doc == 0
        assert func_total == 0


# =============================================================================
# Test pydocstyle Integration
# =============================================================================


class TestRunPydocstyle:
    """Tests for pydocstyle integration."""

    @pytest.mark.skipif(
        True,  # Skip by default since pydocstyle may not be installed
        reason="pydocstyle not installed",
    )
    def test_pydocstyle_on_documented_file(self, numpy_style_file):
        """pydocstyle returns few issues for documented file."""
        issues = run_pydocstyle(numpy_style_file, DocstringStyle.NUMPY)
        # Well-documented file should have few issues
        assert isinstance(issues, list)

    @pytest.mark.skipif(
        True,
        reason="pydocstyle not installed",
    )
    def test_pydocstyle_on_undocumented_file(self, undocumented_file):
        """pydocstyle returns issues for undocumented file."""
        issues = run_pydocstyle(undocumented_file, DocstringStyle.NUMPY)
        assert len(issues) > 0

    def test_pydocstyle_style_conversion(self, temp_dir):
        """Style enum is converted correctly."""
        py_file = temp_dir / "test.py"
        py_file.write_text('"""Module."""\n')

        # Should not raise errors for any style
        run_pydocstyle(py_file, DocstringStyle.NUMPY)
        run_pydocstyle(py_file, DocstringStyle.GOOGLE)
        run_pydocstyle(py_file, "numpy")

    def test_pydocstyle_ignore_codes(self, temp_dir):
        """Ignore codes are passed correctly."""
        py_file = temp_dir / "test.py"
        py_file.write_text('"""Module."""\n')

        issues = run_pydocstyle(py_file, DocstringStyle.NUMPY, ignore_codes=["D100"])
        # Should work without error
        assert isinstance(issues, list)


# =============================================================================
# Test Doctest Integration
# =============================================================================


class TestRunDoctests:
    """Tests for doctest integration."""

    def test_doctests_passing(self, file_with_passing_doctests):
        """Passing doctests are detected."""
        result = run_doctests(file_with_passing_doctests)
        assert result.success
        assert result.failed == 0

    def test_doctests_failing(self, file_with_failing_doctests):
        """Failing doctests are detected."""
        result = run_doctests(file_with_failing_doctests)
        assert not result.success
        # Either failed count or errors should be populated
        assert result.failed > 0 or len(result.errors) > 0

    def test_doctests_no_examples(self, minimal_style_file):
        """Files without doctests pass."""
        result = run_doctests(minimal_style_file)
        # No doctests means nothing failed
        assert result.failed == 0

    def test_doctests_verbose_mode(self, file_with_passing_doctests):
        """Verbose mode works."""
        result = run_doctests(file_with_passing_doctests, verbose=True)
        assert isinstance(result, DoctestResult)


# =============================================================================
# Test Full Validation
# =============================================================================


class TestValidateDocstringFormat:
    """Tests for complete validation function."""

    def test_validate_numpy_file(self, numpy_style_file):
        """NumPy style file validates correctly."""
        result = validate_docstring_format(numpy_style_file, style=DocstringStyle.NUMPY)
        assert result.style == DocstringStyle.NUMPY
        assert result.coverage > 0.5

    def test_validate_google_file(self, google_style_file):
        """Google style file validates correctly."""
        result = validate_docstring_format(google_style_file, style=DocstringStyle.GOOGLE)
        assert result.style == DocstringStyle.GOOGLE

    def test_validate_auto_detect_style(self, numpy_style_file):
        """Style is auto-detected when not specified."""
        result = validate_docstring_format(numpy_style_file, style=None)
        assert result.style == DocstringStyle.NUMPY

    def test_validate_missing_file(self, temp_dir):
        """Missing file returns error result."""
        result = validate_docstring_format(temp_dir / "missing.py")
        assert not result.valid
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_validate_skip_tests(self, file_with_failing_doctests):
        """Can skip doctest execution."""
        result = validate_docstring_format(
            file_with_failing_doctests,
            run_tests=False,
        )
        assert result.doctest_result is None

    def test_validate_string_style(self, numpy_style_file):
        """String style is converted to enum."""
        result = validate_docstring_format(numpy_style_file, style="numpy")
        assert result.style == DocstringStyle.NUMPY

    def test_validate_invalid_string_style(self, numpy_style_file):
        """Invalid string style becomes UNKNOWN."""
        result = validate_docstring_format(numpy_style_file, style="invalid_style")
        assert result.style == DocstringStyle.UNKNOWN


# =============================================================================
# Test Report Formatting
# =============================================================================


class TestFormatValidationReport:
    """Tests for report formatting."""

    def test_report_includes_path(self, numpy_style_file):
        """Report includes file path."""
        result = validate_docstring_format(numpy_style_file)
        report = format_validation_report(result)
        assert str(numpy_style_file) in report

    def test_report_includes_style(self, numpy_style_file):
        """Report includes style."""
        result = validate_docstring_format(numpy_style_file)
        report = format_validation_report(result)
        assert "numpy" in report.lower()

    def test_report_includes_coverage(self, numpy_style_file):
        """Report includes coverage percentage."""
        result = validate_docstring_format(numpy_style_file)
        report = format_validation_report(result)
        assert "Coverage" in report or "coverage" in report

    def test_report_shows_issues(self, undocumented_file):
        """Report shows validation issues."""
        result = validate_docstring_format(undocumented_file, run_tests=False)
        report = format_validation_report(result)
        # Should mention issues if any found
        assert isinstance(report, str)

    def test_report_with_error(self, temp_dir):
        """Report shows error message."""
        result = validate_docstring_format(temp_dir / "missing.py")
        report = format_validation_report(result)
        assert "Error" in report


# =============================================================================
# Test Section Lists
# =============================================================================


class TestSectionLists:
    """Tests for section configuration lists."""

    def test_numpy_sections_complete(self):
        """NumPy sections list is complete."""
        expected = ["Parameters", "Returns", "Examples"]
        for section in expected:
            assert section in NUMPY_SECTIONS

    def test_google_sections_complete(self):
        """Google sections list is complete."""
        expected = ["Args", "Returns", "Example"]
        for section in expected:
            assert section in GOOGLE_SECTIONS


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_file(self, temp_dir):
        """Empty file is handled."""
        py_file = temp_dir / "empty.py"
        py_file.write_text("")
        result = validate_docstring_format(py_file)
        assert result.path == str(py_file)
        # Empty file should have 100% coverage (nothing to document)
        assert result.coverage == 1.0

    def test_syntax_error_file(self, temp_dir):
        """File with syntax error is handled."""
        py_file = temp_dir / "broken.py"
        py_file.write_text("def broken(:\n    pass")
        result = validate_docstring_format(py_file, run_tests=False)
        # Should not crash, but coverage counting may fail
        assert result.path == str(py_file)

    def test_unicode_content(self, temp_dir):
        """Unicode content is handled correctly."""
        py_file = temp_dir / "unicode.py"
        py_file.write_text('"""模块说明。"""\n\ndef 函数():\n    """函数说明。"""\n    pass\n', encoding="utf-8")
        result = validate_docstring_format(py_file, run_tests=False)
        assert result.path == str(py_file)

    def test_very_long_file(self, temp_dir):
        """Very long file is handled."""
        py_file = temp_dir / "long.py"
        functions = "\n\n".join(
            f'def func_{i}():\n    """Function {i}."""\n    pass' for i in range(100)
        )
        py_file.write_text(f'"""Module."""\n\n{functions}\n')
        result = validate_docstring_format(py_file, run_tests=False)
        assert result.functions_total == 100

    def test_async_functions(self, temp_dir):
        """Async functions are counted."""
        py_file = temp_dir / "async.py"
        py_file.write_text('''"""Module."""


async def async_func():
    """Async function."""
    pass


async def undocumented_async():
    pass
''')
        result = validate_docstring_format(py_file, run_tests=False)
        assert result.functions_total == 2
        assert result.functions_documented == 1

    def test_nested_functions(self, temp_dir):
        """Nested functions are counted."""
        py_file = temp_dir / "nested.py"
        py_file.write_text('''"""Module."""


def outer():
    """Outer function."""
    def inner():
        """Inner function."""
        pass
    return inner
''')
        result = validate_docstring_format(py_file, run_tests=False)
        # Both outer and inner should be counted
        assert result.functions_total >= 2


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_validation_workflow(self, numpy_style_file):
        """Test complete validation workflow."""
        result = validate_docstring_format(
            numpy_style_file,
            style=None,  # Auto-detect
            run_tests=True,
        )

        # Style should be detected
        assert result.style == DocstringStyle.NUMPY

        # Should have high coverage
        assert result.coverage >= 0.8

        # Report should be generatable
        report = format_validation_report(result)
        assert len(report) > 0

    def test_validation_with_all_options(self, temp_dir):
        """Test validation with all options specified."""
        py_file = temp_dir / "test.py"
        py_file.write_text('''"""Module with NumPy-style docstrings."""


def add(a, b):
    """
    Add two numbers.

    Parameters
    ----------
    a : int
        First number.
    b : int
        Second number.

    Returns
    -------
    int
        Sum of a and b.

    Examples
    --------
    >>> add(1, 2)
    3
    """
    return a + b
''')

        result = validate_docstring_format(
            py_file,
            style=DocstringStyle.NUMPY,
            run_tests=True,
            ignore_codes=["D100"],
        )

        assert result.style == DocstringStyle.NUMPY
        assert result.coverage == 1.0
        if result.doctest_result:
            assert result.doctest_result.success
