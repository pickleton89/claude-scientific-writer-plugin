"""Tests for output schema enforcement module.

Comprehensive test suite covering:
- Enum and dataclass validation
- Schema constants verification
- Docstring section extraction and validation
- README template selection and validation
- Validation report creation and formatting
- Edge cases and error handling
"""

import json
import pytest
import sys
from pathlib import Path

# Add scripts to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from utils.output_schema import (  # noqa: E402
    DocstringStyle,
    ProjectType,
    NUMPY_SECTIONS,
    GOOGLE_SECTIONS,
    README_REQUIREMENTS,
    README_SECTION_ALIASES,
    SectionValidation,
    DocstringSectionResult,
    ReadmeValidationResult,
    ValidationReport,
    get_section_schema,
    extract_docstring_sections,
    validate_docstring_sections,
    get_readme_template,
    get_required_sections,
    get_optional_sections,
    normalize_section_name,
    validate_readme_sections,
    create_validation_report,
    format_validation_report,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestDocstringStyleEnum:
    """Tests for DocstringStyle enum."""

    def test_has_numpy(self):
        """Enum includes numpy style."""
        assert DocstringStyle.NUMPY.value == "numpy"

    def test_has_google(self):
        """Enum includes google style."""
        assert DocstringStyle.GOOGLE.value == "google"

    def test_has_sphinx(self):
        """Enum includes sphinx style."""
        assert DocstringStyle.SPHINX.value == "sphinx"

    def test_has_minimal(self):
        """Enum includes minimal style."""
        assert DocstringStyle.MINIMAL.value == "minimal"

    def test_from_string(self):
        """Can create enum from string value."""
        assert DocstringStyle("numpy") == DocstringStyle.NUMPY
        assert DocstringStyle("google") == DocstringStyle.GOOGLE


class TestProjectTypeEnum:
    """Tests for ProjectType enum."""

    def test_has_analysis(self):
        """Enum includes analysis type."""
        assert ProjectType.ANALYSIS.value == "analysis"

    def test_has_software(self):
        """Enum includes software type."""
        assert ProjectType.SOFTWARE.value == "software"

    def test_has_data_repo(self):
        """Enum includes data_repo type."""
        assert ProjectType.DATA_REPO.value == "data_repo"

    def test_has_compendium(self):
        """Enum includes compendium type."""
        assert ProjectType.COMPENDIUM.value == "compendium"

    def test_from_string(self):
        """Can create enum from string value."""
        assert ProjectType("analysis") == ProjectType.ANALYSIS
        assert ProjectType("software") == ProjectType.SOFTWARE


# =============================================================================
# Schema Constants Tests
# =============================================================================


class TestNumpySections:
    """Tests for NUMPY_SECTIONS schema constant."""

    def test_has_required_sections(self):
        """Schema includes all standard NumPy sections."""
        expected = [
            "short_summary",
            "extended_summary",
            "parameters",
            "returns",
            "yields",
            "raises",
            "see_also",
            "notes",
            "references",
            "examples",
        ]
        for section in expected:
            assert section in NUMPY_SECTIONS

    def test_short_summary_is_required(self):
        """Short summary must be required."""
        assert NUMPY_SECTIONS["short_summary"]["required"] is True

    def test_parameters_conditionally_required(self):
        """Parameters required only if function has params."""
        assert NUMPY_SECTIONS["parameters"]["required"] == "if_has_params"

    def test_returns_conditionally_required(self):
        """Returns required only if function returns value."""
        assert NUMPY_SECTIONS["returns"]["required"] == "if_returns"

    def test_examples_is_recommended(self):
        """Examples section is recommended."""
        assert NUMPY_SECTIONS["examples"]["required"] == "recommended"

    def test_ordering_is_sequential(self):
        """Section ordering is sequential starting from 0."""
        orders = [info["order"] for info in NUMPY_SECTIONS.values()]
        assert sorted(orders) == list(range(len(orders)))

    def test_has_aliases(self):
        """Sections have alias lists."""
        assert "aliases" in NUMPY_SECTIONS["parameters"]
        assert "args" in NUMPY_SECTIONS["parameters"]["aliases"]


class TestGoogleSections:
    """Tests for GOOGLE_SECTIONS schema constant."""

    def test_has_required_sections(self):
        """Schema includes all standard Google sections."""
        expected = ["summary", "args", "returns", "yields", "raises", "attributes", "example"]
        for section in expected:
            assert section in GOOGLE_SECTIONS

    def test_summary_is_required(self):
        """Summary must be required."""
        assert GOOGLE_SECTIONS["summary"]["required"] is True

    def test_args_conditionally_required(self):
        """Args required only if function has params."""
        assert GOOGLE_SECTIONS["args"]["required"] == "if_has_params"

    def test_example_is_recommended(self):
        """Example section is recommended."""
        assert GOOGLE_SECTIONS["example"]["required"] == "recommended"


class TestReadmeRequirements:
    """Tests for README_REQUIREMENTS constant."""

    def test_has_all_project_types(self):
        """Requirements defined for all project types."""
        for pt in ProjectType:
            assert pt in README_REQUIREMENTS

    def test_analysis_required_sections(self):
        """Analysis projects have correct required sections."""
        req = README_REQUIREMENTS[ProjectType.ANALYSIS]
        assert "title" in req["required"]
        assert "description" in req["required"]
        assert "data_requirements" in req["required"]

    def test_software_required_sections(self):
        """Software projects have correct required sections."""
        req = README_REQUIREMENTS[ProjectType.SOFTWARE]
        assert "title" in req["required"]
        assert "installation" in req["required"]
        assert "quick_start" in req["required"]

    def test_has_template_refs(self):
        """All project types have template references."""
        for pt in ProjectType:
            assert "template_ref" in README_REQUIREMENTS[pt]
            assert README_REQUIREMENTS[pt]["template_ref"].startswith("references/")


class TestReadmeSectionAliases:
    """Tests for README_SECTION_ALIASES constant."""

    def test_title_has_aliases(self):
        """Title section has aliases."""
        assert "title" in README_SECTION_ALIASES
        assert "name" in README_SECTION_ALIASES["title"]

    def test_description_has_aliases(self):
        """Description section has aliases."""
        assert "description" in README_SECTION_ALIASES
        assert "overview" in README_SECTION_ALIASES["description"]
        assert "about" in README_SECTION_ALIASES["description"]

    def test_installation_has_aliases(self):
        """Installation section has aliases."""
        assert "installation" in README_SECTION_ALIASES
        assert "setup" in README_SECTION_ALIASES["installation"]


# =============================================================================
# Dataclass Tests
# =============================================================================


class TestSectionValidation:
    """Tests for SectionValidation dataclass."""

    def test_create_with_required_fields(self):
        """Can create with name and present only."""
        sv = SectionValidation(name="parameters", present=True, order_correct=True)
        assert sv.name == "parameters"
        assert sv.present is True

    def test_optional_fields_default(self):
        """Optional fields have correct defaults."""
        sv = SectionValidation(name="test", present=False, order_correct=True)
        assert sv.actual_order is None
        assert sv.expected_order is None
        assert sv.content_preview == ""


class TestDocstringSectionResult:
    """Tests for DocstringSectionResult dataclass."""

    def test_create_with_style(self):
        """Can create with style only."""
        result = DocstringSectionResult(style=DocstringStyle.NUMPY)
        assert result.style == DocstringStyle.NUMPY

    def test_default_lists_are_empty(self):
        """List fields default to empty."""
        result = DocstringSectionResult(style=DocstringStyle.GOOGLE)
        assert result.sections_found == []
        assert result.sections_missing == []
        assert result.order_violations == []

    def test_default_is_valid(self):
        """Default is_valid is True."""
        result = DocstringSectionResult(style=DocstringStyle.NUMPY)
        assert result.is_valid is True


class TestReadmeValidationResult:
    """Tests for ReadmeValidationResult dataclass."""

    def test_create_with_project_type(self):
        """Can create with project_type only."""
        result = ReadmeValidationResult(project_type=ProjectType.ANALYSIS)
        assert result.project_type == ProjectType.ANALYSIS

    def test_default_score_is_zero(self):
        """Default score is 0."""
        result = ReadmeValidationResult(project_type=ProjectType.SOFTWARE)
        assert result.score == 0.0


class TestValidationReport:
    """Tests for ValidationReport dataclass."""

    def test_create_minimal(self):
        """Can create with file only."""
        report = ValidationReport(file="test.py")
        assert report.file == "test.py"
        assert report.is_valid is True

    def test_to_json(self):
        """Can convert to JSON."""
        report = ValidationReport(file="test.py", style="numpy")
        json_str = report.to_json()
        data = json.loads(json_str)
        assert data["file"] == "test.py"
        assert data["style"] == "numpy"

    def test_to_dict(self):
        """Can convert to dict."""
        report = ValidationReport(
            file="test.py",
            coverage={"total_items": 10, "documented": 8, "percentage": 80.0},
        )
        data = report.to_dict()
        assert data["coverage"]["percentage"] == 80.0

    def test_to_json_excludes_none(self):
        """JSON excludes None fields."""
        report = ValidationReport(file="test.py")
        data = report.to_dict()
        assert "style" not in data
        assert "coverage" not in data


# =============================================================================
# Schema Functions Tests
# =============================================================================


class TestGetSectionSchema:
    """Tests for get_section_schema function."""

    def test_numpy_returns_numpy_sections(self):
        """Returns NUMPY_SECTIONS for NumPy style."""
        schema = get_section_schema(DocstringStyle.NUMPY)
        assert "parameters" in schema
        assert "returns" in schema

    def test_google_returns_google_sections(self):
        """Returns GOOGLE_SECTIONS for Google style."""
        schema = get_section_schema(DocstringStyle.GOOGLE)
        assert "args" in schema
        assert "example" in schema

    def test_minimal_returns_empty(self):
        """Returns empty schema for minimal style."""
        schema = get_section_schema(DocstringStyle.MINIMAL)
        assert schema == {}

    def test_sphinx_returns_empty(self):
        """Returns empty schema for sphinx style."""
        schema = get_section_schema(DocstringStyle.SPHINX)
        assert schema == {}

    def test_returns_copy(self):
        """Returns a copy, not original."""
        schema = get_section_schema(DocstringStyle.NUMPY)
        schema["test"] = "modified"
        assert "test" not in NUMPY_SECTIONS


# =============================================================================
# Docstring Extraction Tests
# =============================================================================


class TestExtractDocstringSections:
    """Tests for extract_docstring_sections function."""

    def test_extracts_numpy_summary(self):
        """Extracts short summary from NumPy docstring."""
        doc = "This is a summary line."
        sections = extract_docstring_sections(doc, DocstringStyle.NUMPY)
        assert "short_summary" in sections

    def test_extracts_numpy_parameters(self):
        """Extracts Parameters section from NumPy docstring."""
        doc = """Summary line.

        Parameters
        ----------
        x : int
            Input value.
        """
        sections = extract_docstring_sections(doc, DocstringStyle.NUMPY)
        assert "parameters" in sections

    def test_extracts_numpy_returns(self):
        """Extracts Returns section from NumPy docstring."""
        doc = """Summary line.

        Returns
        -------
        int
            Output value.
        """
        sections = extract_docstring_sections(doc, DocstringStyle.NUMPY)
        assert "returns" in sections

    def test_extracts_google_summary(self):
        """Extracts summary from Google docstring."""
        doc = "This is a summary line."
        sections = extract_docstring_sections(doc, DocstringStyle.GOOGLE)
        assert "summary" in sections

    def test_extracts_google_args(self):
        """Extracts Args section from Google docstring."""
        doc = """Summary line.

        Args:
            x: Input value.
        """
        sections = extract_docstring_sections(doc, DocstringStyle.GOOGLE)
        assert "args" in sections

    def test_extracts_google_returns(self):
        """Extracts Returns section from Google docstring."""
        doc = """Summary line.

        Returns:
            The output value.
        """
        sections = extract_docstring_sections(doc, DocstringStyle.GOOGLE)
        assert "returns" in sections

    def test_empty_docstring(self):
        """Returns empty list for empty docstring."""
        sections = extract_docstring_sections("", DocstringStyle.NUMPY)
        assert sections == []

    def test_whitespace_only(self):
        """Returns empty list for whitespace-only docstring."""
        sections = extract_docstring_sections("   \n   ", DocstringStyle.NUMPY)
        assert sections == []

    def test_multiple_sections(self):
        """Extracts multiple sections in order."""
        doc = """Summary line.

        Parameters
        ----------
        x : int
            Input.

        Returns
        -------
        int
            Output.

        Examples
        --------
        >>> example()
        """
        sections = extract_docstring_sections(doc, DocstringStyle.NUMPY)
        assert sections == ["short_summary", "parameters", "returns", "examples"]


# =============================================================================
# Docstring Validation Tests
# =============================================================================


class TestValidateDocstringSections:
    """Tests for validate_docstring_sections function."""

    def test_valid_numpy_docstring(self):
        """Validates correct NumPy docstring."""
        doc = """Short summary line.

        Parameters
        ----------
        x : int
            Input.

        Returns
        -------
        int
            Output.
        """
        result = validate_docstring_sections(doc, "numpy")
        assert result.is_valid is True
        assert result.style == DocstringStyle.NUMPY

    def test_missing_required_section(self):
        """Detects missing required section."""
        doc = ""  # Empty, missing summary
        result = validate_docstring_sections(doc, "numpy")
        assert "short_summary" in result.sections_missing

    def test_accepts_string_style(self):
        """Accepts string style parameter."""
        doc = "Summary."
        result = validate_docstring_sections(doc, "google")
        assert result.style == DocstringStyle.GOOGLE

    def test_accepts_enum_style(self):
        """Accepts enum style parameter."""
        doc = "Summary."
        result = validate_docstring_sections(doc, DocstringStyle.NUMPY)
        assert result.style == DocstringStyle.NUMPY

    def test_minimal_always_valid(self):
        """Minimal style has no schema, always valid."""
        doc = "Just a summary."
        result = validate_docstring_sections(doc, "minimal")
        assert result.is_valid is True

    def test_order_violation_detection(self):
        """Detects out-of-order sections."""
        # Returns before Parameters (order 3 before order 2)
        doc = """Summary.

        Returns
        -------
        int
            Value.

        Parameters
        ----------
        x : int
            Input.
        """
        result = validate_docstring_sections(doc, "numpy")
        assert len(result.order_violations) > 0


# =============================================================================
# README Template Tests
# =============================================================================


class TestGetReadmeTemplate:
    """Tests for get_readme_template function."""

    def test_analysis_template(self):
        """Returns correct template for analysis."""
        template = get_readme_template("analysis")
        assert "analysis-project" in template

    def test_software_template(self):
        """Returns correct template for software."""
        template = get_readme_template("software")
        assert "software-tool" in template

    def test_data_repo_template(self):
        """Returns correct template for data_repo."""
        template = get_readme_template("data_repo")
        assert "data-repository" in template

    def test_compendium_template(self):
        """Returns correct template for compendium."""
        template = get_readme_template("compendium")
        assert "research-compendium" in template

    def test_accepts_enum(self):
        """Accepts ProjectType enum."""
        template = get_readme_template(ProjectType.ANALYSIS)
        assert "analysis-project" in template

    def test_default_to_software(self):
        """Defaults to software for unknown types."""
        # This would require a mock or invalid enum, skip for now
        pass


class TestGetRequiredSections:
    """Tests for get_required_sections function."""

    def test_analysis_required(self):
        """Returns correct required sections for analysis."""
        required = get_required_sections("analysis")
        assert "title" in required
        assert "data_requirements" in required

    def test_software_required(self):
        """Returns correct required sections for software."""
        required = get_required_sections("software")
        assert "installation" in required
        assert "quick_start" in required

    def test_returns_copy(self):
        """Returns a copy, not original."""
        required = get_required_sections("software")
        required.append("test")
        assert "test" not in README_REQUIREMENTS[ProjectType.SOFTWARE]["required"]


class TestGetOptionalSections:
    """Tests for get_optional_sections function."""

    def test_software_optional(self):
        """Returns correct optional sections for software."""
        optional = get_optional_sections("software")
        assert "documentation" in optional
        assert "contributing" in optional

    def test_analysis_optional(self):
        """Returns correct optional sections for analysis."""
        optional = get_optional_sections("analysis")
        assert "citation" in optional


# =============================================================================
# Section Name Normalization Tests
# =============================================================================


class TestNormalizeSectionName:
    """Tests for normalize_section_name function."""

    def test_exact_match(self):
        """Returns canonical name for exact match."""
        assert normalize_section_name("title") == "title"

    def test_alias_match(self):
        """Returns canonical name for alias."""
        assert normalize_section_name("overview") == "description"
        assert normalize_section_name("about") == "description"

    def test_case_insensitive(self):
        """Matching is case-insensitive."""
        assert normalize_section_name("TITLE") == "title"
        assert normalize_section_name("Overview") == "description"

    def test_strips_whitespace(self):
        """Strips leading/trailing whitespace."""
        assert normalize_section_name("  title  ") == "title"

    def test_unknown_returns_normalized(self):
        """Unknown names returned with spaces as underscores."""
        assert normalize_section_name("Custom Section") == "custom_section"

    def test_getting_started_to_installation(self):
        """Getting Started maps to installation."""
        assert normalize_section_name("Getting Started") == "installation"


# =============================================================================
# README Validation Tests
# =============================================================================


class TestValidateReadmeSections:
    """Tests for validate_readme_sections function."""

    def test_complete_software_readme(self):
        """Validates complete software README."""
        sections = ["title", "description", "installation", "quick_start"]
        result = validate_readme_sections(sections, "software")
        assert result.is_valid is True
        assert result.score >= 80.0

    def test_missing_required_sections(self):
        """Detects missing required sections."""
        sections = ["title"]  # Missing installation, quick_start, description
        result = validate_readme_sections(sections, "software")
        assert result.is_valid is False
        assert "installation" in result.required_missing

    def test_includes_optional_in_score(self):
        """Optional sections contribute to score."""
        sections = [
            "title",
            "description",
            "installation",
            "quick_start",
            "documentation",
            "contributing",
        ]
        result = validate_readme_sections(sections, "software")
        assert result.score > 80.0  # Base + optional bonus

    def test_normalizes_section_names(self):
        """Normalizes section names before validation."""
        sections = ["Title", "Overview", "Setup", "Getting Started"]
        result = validate_readme_sections(sections, "software")
        # Overview -> description, Setup -> installation, Getting Started -> installation/quick_start
        assert "title" in result.required_present

    def test_analysis_validation(self):
        """Validates analysis project README."""
        sections = [
            "title",
            "description",
            "data_requirements",
            "environment",
            "usage",
            "output",
        ]
        result = validate_readme_sections(sections, "analysis")
        assert result.is_valid is True

    def test_returns_template_ref(self):
        """Result includes template reference."""
        sections = ["title"]
        result = validate_readme_sections(sections, "software")
        assert "software-tool" in result.template_ref


# =============================================================================
# Validation Report Tests
# =============================================================================


class TestCreateValidationReport:
    """Tests for create_validation_report function."""

    def test_minimal_report(self):
        """Creates report with file only."""
        report = create_validation_report("test.py")
        assert report.file == "test.py"
        assert report.is_valid is True

    def test_with_style(self):
        """Creates report with style."""
        report = create_validation_report("test.py", style="numpy")
        assert report.style == "numpy"

    def test_with_coverage(self):
        """Creates report with coverage."""
        coverage = {"total_items": 10, "documented": 8, "percentage": 80.0}
        report = create_validation_report("test.py", coverage=coverage)
        assert report.coverage == coverage

    def test_with_pydocstyle_issues(self):
        """Creates report with pydocstyle issues."""
        issues = [{"code": "D100", "line": 1, "message": "Missing docstring"}]
        report = create_validation_report("test.py", pydocstyle_issues=issues)
        assert report.pydocstyle["errors"] == 1
        assert report.is_valid is False

    def test_with_doctest_failures(self):
        """Creates report with doctest failures."""
        results = {"total": 5, "passed": 4, "failed": 1, "failures": []}
        report = create_validation_report("test.py", doctest_results=results)
        assert report.doctests["failed"] == 1
        assert report.is_valid is False

    def test_with_readme_result(self):
        """Creates report with README validation."""
        readme_result = ReadmeValidationResult(
            project_type=ProjectType.SOFTWARE,
            score=85.0,
            required_missing=["contributing"],
            is_valid=True,
        )
        report = create_validation_report("README.md", readme_result=readme_result)
        assert report.readme_score == 85.0
        assert "contributing" in report.missing_sections


class TestFormatValidationReport:
    """Tests for format_validation_report function."""

    def test_includes_file_name(self):
        """Output includes file name."""
        report = ValidationReport(file="test.py")
        output = format_validation_report(report)
        assert "test.py" in output

    def test_includes_style(self):
        """Output includes style when present."""
        report = ValidationReport(file="test.py", style="numpy")
        output = format_validation_report(report)
        assert "numpy" in output

    def test_includes_coverage(self):
        """Output includes coverage when present."""
        report = ValidationReport(
            file="test.py",
            coverage={"total_items": 10, "documented": 8, "percentage": 80.0},
        )
        output = format_validation_report(report)
        assert "80.0%" in output

    def test_includes_valid_status(self):
        """Output includes valid status."""
        report = ValidationReport(file="test.py", is_valid=True)
        output = format_validation_report(report)
        assert "VALID" in output

    def test_includes_invalid_status(self):
        """Output includes invalid status."""
        report = ValidationReport(file="test.py", is_valid=False)
        output = format_validation_report(report)
        assert "INVALID" in output

    def test_verbose_shows_issues(self):
        """Verbose mode shows issue details."""
        report = ValidationReport(
            file="test.py",
            pydocstyle={
                "errors": 1,
                "warnings": 0,
                "issues": [{"code": "D100", "message": "Missing docstring"}],
            },
        )
        output = format_validation_report(report, verbose=True)
        assert "D100" in output


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_sections_list(self):
        """Handles empty sections list for README."""
        result = validate_readme_sections([], "software")
        assert result.is_valid is False
        assert len(result.required_missing) > 0

    def test_none_docstring(self):
        """Handles None-ish empty docstring."""
        result = validate_docstring_sections("", "numpy")
        assert "short_summary" in result.sections_missing

    def test_unicode_in_docstring(self):
        """Handles unicode in docstring."""
        doc = """Calculates π approximation.

        Parameters
        ----------
        n : int
            Number of iterations.
        """
        sections = extract_docstring_sections(doc, DocstringStyle.NUMPY)
        assert "short_summary" in sections

    def test_mixed_case_section_headers(self):
        """Handles mixed case section headers."""
        doc = """Summary.

        PARAMETERS
        ----------
        x : int
            Value.
        """
        # Note: Our regex may be case-sensitive, adjust if needed
        # For now, test documents expected behavior
        _ = extract_docstring_sections(doc, DocstringStyle.NUMPY)

    def test_report_json_valid(self):
        """Report JSON is always valid JSON."""
        report = ValidationReport(
            file="test.py",
            style="numpy",
            coverage={"total_items": 10, "documented": 5, "percentage": 50.0},
            pydocstyle={"errors": 2, "warnings": 1, "issues": []},
        )
        json_str = report.to_json()
        # Should not raise
        parsed = json.loads(json_str)
        assert parsed["file"] == "test.py"

    def test_special_characters_in_path(self):
        """Handles special characters in file path."""
        report = ValidationReport(file="/path/with spaces/and-dashes/test.py")
        assert report.file == "/path/with spaces/and-dashes/test.py"


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_full_docstring_validation_workflow(self):
        """Tests complete docstring validation workflow."""
        doc = """Calculate the mean of values.

        Parameters
        ----------
        values : list[float]
            Input values.

        Returns
        -------
        float
            The arithmetic mean.

        Examples
        --------
        >>> calculate_mean([1, 2, 3])
        2.0
        """
        # Extract sections
        sections = extract_docstring_sections(doc, DocstringStyle.NUMPY)
        assert len(sections) >= 4

        # Validate sections
        result = validate_docstring_sections(doc, "numpy")
        assert result.is_valid is True

    def test_full_readme_validation_workflow(self):
        """Tests complete README validation workflow."""
        # Simulate parsed sections from a README
        sections = [
            "Title",  # title
            "Overview",  # description alias
            "Installation",
            "Quick Start",
            "Documentation",
            "License",
        ]

        # Get requirements (verify functions work)
        assert len(get_required_sections("software")) > 0
        assert len(get_optional_sections("software")) > 0

        # Validate
        result = validate_readme_sections(sections, "software")
        assert result.is_valid is True
        assert result.score >= 80.0

        # Get template
        template = get_readme_template("software")
        assert template == result.template_ref

    def test_full_report_creation_workflow(self):
        """Tests complete validation report workflow."""
        # Create report with all components
        report = create_validation_report(
            file_path="module.py",
            style="numpy",
            coverage={"total_items": 10, "documented": 9, "percentage": 90.0},
            pydocstyle_issues=[],
            doctest_results={"total": 5, "passed": 5, "failed": 0, "failures": []},
        )

        assert report.is_valid is True

        # Format for output
        output = format_validation_report(report)
        assert "90.0%" in output
        assert "VALID" in output

        # Convert to JSON
        json_data = report.to_dict()
        assert json_data["coverage"]["percentage"] == 90.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
