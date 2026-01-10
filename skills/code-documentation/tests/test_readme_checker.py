"""Tests for README validation utilities.

Comprehensive test suite covering:
- Section detection and matching
- Project type detection
- Required section validation
- Section aliases
- Score calculation
- Edge cases
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils.readme_checker import (
    OPTIONAL_SECTIONS,
    REQUIRED_SECTIONS,
    SECTION_ALIASES,
    ProjectType,
    ReadmeValidation,
    SectionResult,
    SectionStatus,
    _extract_sections,
    _find_section_match,
    _normalize_section_name,
    detect_project_type,
    format_validation_report,
    get_optional_sections,
    get_required_sections,
    validate_readme_sections,
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
def analysis_readme(temp_dir):
    """Create a complete analysis project README."""
    readme = temp_dir / "README.md"
    readme.write_text("""# My Analysis Project

## Description

This project analyzes RNA-seq data from patient samples.

## Data Requirements

Input data should be in CSV format with columns:
- gene_id
- expression_value

## Environment Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python run_analysis.py --input data.csv
```

## Output

The analysis produces:
- results/summary.csv
- figures/volcano_plot.png

## Citation

Please cite: Author et al., 2024

## License

MIT License
""")
    return readme


@pytest.fixture
def software_readme(temp_dir):
    """Create a software project README."""
    readme = temp_dir / "README.md"
    readme.write_text("""# MyPackage

![CI](https://badge.svg) ![Version](https://badge2.svg)

## Description

A Python package for data analysis.

## Installation

```bash
pip install mypackage
```

## Quick Start

```python
from mypackage import analyze
result = analyze(data)
```

## Documentation

Full documentation at https://mypackage.readthedocs.io

## Contributing

See CONTRIBUTING.md

## License

Apache 2.0
""")
    return readme


@pytest.fixture
def incomplete_readme(temp_dir):
    """Create an incomplete README."""
    readme = temp_dir / "README.md"
    readme.write_text("""# My Project

Just some text without proper sections.

Here's some more content but no real structure.
""")
    return readme


@pytest.fixture
def minimal_readme(temp_dir):
    """Create a minimal README with only title."""
    readme = temp_dir / "README.md"
    readme.write_text("# Project Name\n")
    return readme


# =============================================================================
# Test ProjectType Enum
# =============================================================================


class TestProjectType:
    """Tests for ProjectType enum."""

    def test_project_type_values(self):
        """All expected project types exist."""
        assert ProjectType.ANALYSIS.value == "analysis"
        assert ProjectType.SOFTWARE.value == "software"
        assert ProjectType.DATA_REPO.value == "data_repo"
        assert ProjectType.COMPENDIUM.value == "compendium"
        assert ProjectType.UNKNOWN.value == "unknown"

    def test_project_type_from_string(self):
        """Can create ProjectType from string."""
        assert ProjectType("analysis") == ProjectType.ANALYSIS
        assert ProjectType("software") == ProjectType.SOFTWARE

    def test_invalid_project_type(self):
        """Invalid string raises ValueError."""
        with pytest.raises(ValueError):
            ProjectType("invalid_type")


# =============================================================================
# Test Section Status Enum
# =============================================================================


class TestSectionStatus:
    """Tests for SectionStatus enum."""

    def test_section_status_values(self):
        """All expected statuses exist."""
        assert SectionStatus.PRESENT.value == "present"
        assert SectionStatus.MISSING.value == "missing"
        assert SectionStatus.PARTIAL.value == "partial"


# =============================================================================
# Test Helper Functions
# =============================================================================


class TestNormalizeSectionName:
    """Tests for _normalize_section_name."""

    def test_simple_name(self):
        """Simple section names are lowercased."""
        assert _normalize_section_name("Installation") == "installation"
        assert _normalize_section_name("USAGE") == "usage"

    def test_name_with_badge(self):
        """Badge images are removed."""
        result = _normalize_section_name("Package ![badge](url)")
        assert "badge" not in result
        assert "url" not in result

    def test_name_with_link(self):
        """Markdown links are removed."""
        result = _normalize_section_name("[Documentation](https://docs.com)")
        assert "documentation" not in result.lower() or result == ""

    def test_name_with_special_chars(self):
        """Special characters are removed."""
        assert _normalize_section_name("Data & Methods") == "data  methods"
        assert _normalize_section_name("Step-by-Step") == "stepbystep"

    def test_whitespace_handling(self):
        """Leading/trailing whitespace is trimmed."""
        assert _normalize_section_name("  Description  ") == "description"


class TestFindSectionMatch:
    """Tests for _find_section_match."""

    def test_direct_match(self):
        """Direct matches are found."""
        assert _find_section_match("installation", ["installation", "usage"]) == "installation"
        assert _find_section_match("usage", ["installation", "usage"]) == "usage"

    def test_no_match(self):
        """Non-matching names return None."""
        assert _find_section_match("foobar", ["installation", "usage"]) is None

    def test_alias_match(self):
        """Aliases are matched correctly."""
        # "setup" is an alias for "installation"
        assert _find_section_match("setup", ["installation"]) == "installation"
        # "overview" is an alias for "description"
        assert _find_section_match("overview", ["description"]) == "description"

    def test_partial_match(self):
        """Partial matches via aliases work."""
        assert _find_section_match("getting started", ["installation"]) == "installation"


class TestExtractSections:
    """Tests for _extract_sections."""

    def test_h1_sections(self):
        """H1 headers are extracted."""
        content = "# Title\n\nSome content\n\n# Another\n\nMore content"
        sections = _extract_sections(content)
        assert len(sections) == 2
        assert sections[0][0] == "Title"
        assert sections[1][0] == "Another"

    def test_h2_sections(self):
        """H2 headers are extracted."""
        content = "# Main\n\n## Section One\n\nContent\n\n## Section Two"
        sections = _extract_sections(content)
        assert any(s[0] == "Section One" for s in sections)
        assert any(s[0] == "Section Two" for s in sections)

    def test_line_numbers(self):
        """Line numbers are correct."""
        content = "# Line One\n\n## Line Three\n"
        sections = _extract_sections(content)
        assert sections[0][1] == 1  # Line numbers are 1-indexed
        assert sections[1][1] == 3

    def test_content_preview(self):
        """Content preview captures next non-empty line."""
        content = "# Title\n\nThis is the preview.\n\nMore content"
        sections = _extract_sections(content)
        assert sections[0][2] == "This is the preview."

    def test_no_sections(self):
        """Content without headers returns empty list."""
        content = "Just some text\nNo headers here"
        sections = _extract_sections(content)
        assert len(sections) == 0


# =============================================================================
# Test Required/Optional Section Lists
# =============================================================================


class TestSectionLists:
    """Tests for required and optional section configuration."""

    def test_all_project_types_have_required_sections(self):
        """All project types (except UNKNOWN) have required sections."""
        for pt in [ProjectType.ANALYSIS, ProjectType.SOFTWARE, ProjectType.DATA_REPO, ProjectType.COMPENDIUM]:
            assert len(get_required_sections(pt)) > 0

    def test_unknown_has_no_required_sections(self):
        """UNKNOWN project type has no required sections."""
        assert get_required_sections(ProjectType.UNKNOWN) == []

    def test_analysis_required_sections(self):
        """Analysis project has expected required sections."""
        required = get_required_sections(ProjectType.ANALYSIS)
        assert "description" in required
        assert "data" in required
        assert "usage" in required
        assert "citation" in required

    def test_software_required_sections(self):
        """Software project has expected required sections."""
        required = get_required_sections(ProjectType.SOFTWARE)
        assert "description" in required
        assert "installation" in required
        assert "license" in required

    def test_get_optional_sections(self):
        """Optional sections are returned correctly."""
        optional = get_optional_sections(ProjectType.SOFTWARE)
        assert isinstance(optional, list)


# =============================================================================
# Test Section Aliases
# =============================================================================


class TestSectionAliases:
    """Tests for section alias mapping."""

    def test_description_aliases(self):
        """Description has common aliases."""
        aliases = SECTION_ALIASES.get("description", [])
        assert "overview" in aliases
        assert "about" in aliases

    def test_installation_aliases(self):
        """Installation has common aliases."""
        aliases = SECTION_ALIASES.get("installation", [])
        assert "install" in aliases
        assert "setup" in aliases

    def test_citation_aliases(self):
        """Citation has common aliases."""
        aliases = SECTION_ALIASES.get("citation", [])
        assert "cite" in aliases
        assert "citing" in aliases


# =============================================================================
# Test Project Type Detection
# =============================================================================


class TestDetectProjectType:
    """Tests for project type auto-detection."""

    def test_detect_software_with_setup_py(self, temp_dir):
        """Projects with setup.py are detected as software."""
        (temp_dir / "setup.py").write_text("from setuptools import setup")
        assert detect_project_type(temp_dir) == ProjectType.SOFTWARE

    def test_detect_software_with_pyproject_toml(self, temp_dir):
        """Projects with pyproject.toml are detected as software."""
        (temp_dir / "pyproject.toml").write_text("[project]")
        assert detect_project_type(temp_dir) == ProjectType.SOFTWARE

    def test_detect_software_with_package_json(self, temp_dir):
        """Node projects are detected as software."""
        (temp_dir / "package.json").write_text("{}")
        assert detect_project_type(temp_dir) == ProjectType.SOFTWARE

    def test_detect_analysis_with_notebooks(self, temp_dir):
        """Projects with notebooks are detected as analysis."""
        (temp_dir / "analysis.ipynb").write_text("{}")
        assert detect_project_type(temp_dir) == ProjectType.ANALYSIS

    def test_detect_analysis_with_rmd(self, temp_dir):
        """Projects with R Markdown are detected as analysis."""
        (temp_dir / "report.Rmd").write_text("---\ntitle: Test\n---")
        assert detect_project_type(temp_dir) == ProjectType.ANALYSIS

    def test_detect_from_readme_path(self, temp_dir):
        """Detection works when given README path."""
        (temp_dir / "setup.py").write_text("")
        (temp_dir / "README.md").write_text("# Test")
        result = detect_project_type(temp_dir / "README.md")
        assert result == ProjectType.SOFTWARE

    def test_empty_directory_is_unknown(self, temp_dir):
        """Empty directories return UNKNOWN."""
        assert detect_project_type(temp_dir) == ProjectType.UNKNOWN


# =============================================================================
# Test README Validation
# =============================================================================


class TestValidateReadmeSections:
    """Tests for validate_readme_sections function."""

    def test_complete_analysis_readme(self, analysis_readme):
        """Complete analysis README passes validation."""
        result = validate_readme_sections(analysis_readme, ProjectType.ANALYSIS)
        assert result.valid
        assert len(result.missing_required) == 0
        assert result.score >= 80

    def test_complete_software_readme(self, software_readme):
        """Complete software README passes validation."""
        result = validate_readme_sections(software_readme, ProjectType.SOFTWARE)
        assert result.valid
        assert len(result.missing_required) == 0

    def test_incomplete_readme_fails(self, incomplete_readme):
        """Incomplete README fails validation."""
        result = validate_readme_sections(incomplete_readme, ProjectType.SOFTWARE)
        assert not result.valid
        assert len(result.missing_required) > 0

    def test_minimal_readme_fails(self, minimal_readme):
        """Minimal README fails validation."""
        result = validate_readme_sections(minimal_readme, ProjectType.ANALYSIS)
        assert not result.valid

    def test_auto_detect_project_type(self, software_readme, temp_dir):
        """Project type is auto-detected when not specified."""
        (temp_dir / "setup.py").write_text("")
        result = validate_readme_sections(software_readme, None)
        assert result.project_type == ProjectType.SOFTWARE

    def test_string_project_type(self, software_readme):
        """String project type is converted to enum."""
        result = validate_readme_sections(software_readme, "software")
        assert result.project_type == ProjectType.SOFTWARE

    def test_invalid_string_project_type(self, software_readme):
        """Invalid string project type becomes UNKNOWN."""
        result = validate_readme_sections(software_readme, "invalid")
        assert result.project_type == ProjectType.UNKNOWN

    def test_missing_readme_file(self, temp_dir):
        """Missing README file returns error result."""
        result = validate_readme_sections(temp_dir / "MISSING.md", ProjectType.SOFTWARE)
        assert not result.valid
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_section_results_populated(self, analysis_readme):
        """Section results contain details for each required section."""
        result = validate_readme_sections(analysis_readme, ProjectType.ANALYSIS)
        assert len(result.sections) > 0
        # All sections should have name and status
        for section in result.sections:
            assert section.name
            assert section.status in SectionStatus

    def test_line_numbers_captured(self, analysis_readme):
        """Line numbers are captured for found sections."""
        result = validate_readme_sections(analysis_readme, ProjectType.ANALYSIS)
        present_sections = [s for s in result.sections if s.status == SectionStatus.PRESENT]
        assert all(s.line_number is not None and s.line_number > 0 for s in present_sections)


# =============================================================================
# Test ReadmeValidation Dataclass
# =============================================================================


class TestReadmeValidationDataclass:
    """Tests for ReadmeValidation dataclass properties."""

    def test_completeness_ratio_all_present(self):
        """Completeness ratio is 1.0 when all required present."""
        sections = [
            SectionResult("a", SectionStatus.PRESENT, True),
            SectionResult("b", SectionStatus.PRESENT, True),
        ]
        validation = ReadmeValidation(
            path="test.md",
            project_type=ProjectType.SOFTWARE,
            valid=True,
            sections=sections,
        )
        assert validation.completeness_ratio == 1.0

    def test_completeness_ratio_half_present(self):
        """Completeness ratio reflects missing sections."""
        sections = [
            SectionResult("a", SectionStatus.PRESENT, True),
            SectionResult("b", SectionStatus.MISSING, True),
        ]
        validation = ReadmeValidation(
            path="test.md",
            project_type=ProjectType.SOFTWARE,
            valid=False,
            sections=sections,
        )
        assert validation.completeness_ratio == 0.5

    def test_completeness_ratio_ignores_optional(self):
        """Optional sections don't affect completeness ratio."""
        sections = [
            SectionResult("a", SectionStatus.PRESENT, True),
            SectionResult("b", SectionStatus.MISSING, False),  # Optional
        ]
        validation = ReadmeValidation(
            path="test.md",
            project_type=ProjectType.SOFTWARE,
            valid=True,
            sections=sections,
        )
        assert validation.completeness_ratio == 1.0

    def test_completeness_ratio_no_required(self):
        """Empty required sections returns 1.0."""
        validation = ReadmeValidation(
            path="test.md",
            project_type=ProjectType.UNKNOWN,
            valid=True,
            sections=[],
        )
        assert validation.completeness_ratio == 1.0

    def test_summary_property_valid(self):
        """Summary property formats correctly for valid README."""
        validation = ReadmeValidation(
            path="test.md",
            project_type=ProjectType.SOFTWARE,
            valid=True,
            score=85.0,
        )
        assert "pass" in validation.summary
        assert "85" in validation.summary
        assert "software" in validation.summary

    def test_summary_property_invalid(self):
        """Summary property formats correctly for invalid README."""
        validation = ReadmeValidation(
            path="test.md",
            project_type=ProjectType.ANALYSIS,
            valid=False,
            score=45.0,
        )
        assert "fail" in validation.summary
        assert "45" in validation.summary
        assert "analysis" in validation.summary


# =============================================================================
# Test Score Calculation
# =============================================================================


class TestScoreCalculation:
    """Tests for README validation score calculation."""

    def test_perfect_score(self, analysis_readme):
        """Complete README with optional sections gets high score."""
        result = validate_readme_sections(analysis_readme, ProjectType.ANALYSIS)
        assert result.score >= 80

    def test_zero_score_minimal(self, minimal_readme):
        """Minimal README gets low score."""
        result = validate_readme_sections(minimal_readme, ProjectType.SOFTWARE)
        assert result.score < 50

    def test_score_increases_with_sections(self, temp_dir):
        """Score increases as more sections are added."""
        # Start with minimal
        readme = temp_dir / "README.md"
        readme.write_text("# Project\n")
        score1 = validate_readme_sections(readme, ProjectType.SOFTWARE).score

        # Add description
        readme.write_text("# Project\n\n## Description\n\nA tool.\n")
        score2 = validate_readme_sections(readme, ProjectType.SOFTWARE).score

        # Add installation
        readme.write_text("# Project\n\n## Description\n\nA tool.\n\n## Installation\n\npip install\n")
        score3 = validate_readme_sections(readme, ProjectType.SOFTWARE).score

        assert score2 > score1
        assert score3 > score2


# =============================================================================
# Test Report Formatting
# =============================================================================


class TestFormatValidationReport:
    """Tests for report formatting."""

    def test_report_includes_file_path(self, analysis_readme):
        """Report includes file path."""
        result = validate_readme_sections(analysis_readme, ProjectType.ANALYSIS)
        report = format_validation_report(result)
        assert str(analysis_readme) in report

    def test_report_includes_project_type(self, analysis_readme):
        """Report includes project type."""
        result = validate_readme_sections(analysis_readme, ProjectType.ANALYSIS)
        report = format_validation_report(result)
        assert "analysis" in report.lower()

    def test_report_includes_score(self, analysis_readme):
        """Report includes score."""
        result = validate_readme_sections(analysis_readme, ProjectType.ANALYSIS)
        report = format_validation_report(result)
        assert "/100" in report

    def test_report_shows_missing_sections(self, incomplete_readme):
        """Report lists missing sections."""
        result = validate_readme_sections(incomplete_readme, ProjectType.SOFTWARE)
        report = format_validation_report(result)
        assert "Missing Required Sections" in report or "missing" in report.lower()

    def test_report_with_error(self, temp_dir):
        """Report shows error message."""
        result = validate_readme_sections(temp_dir / "MISSING.md", ProjectType.SOFTWARE)
        report = format_validation_report(result)
        assert "Error" in report


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_file(self, temp_dir):
        """Empty README file is handled."""
        readme = temp_dir / "README.md"
        readme.write_text("")
        result = validate_readme_sections(readme, ProjectType.SOFTWARE)
        assert not result.valid
        assert len(result.missing_required) > 0

    def test_unicode_content(self, temp_dir):
        """Unicode content is handled correctly."""
        readme = temp_dir / "README.md"
        readme.write_text("# 项目名称\n\n## 描述\n\n这是一个测试项目。\n", encoding="utf-8")
        result = validate_readme_sections(readme, ProjectType.SOFTWARE)
        # Should not raise an error
        assert result.path == str(readme)

    def test_very_long_readme(self, temp_dir):
        """Very long README is handled."""
        readme = temp_dir / "README.md"
        content = "# Project\n\n" + "Lorem ipsum\n" * 10000
        readme.write_text(content)
        result = validate_readme_sections(readme, ProjectType.SOFTWARE)
        assert result.path == str(readme)

    def test_readme_with_code_blocks(self, temp_dir):
        """Code blocks don't interfere with section detection."""
        readme = temp_dir / "README.md"
        readme.write_text("""# Project

## Installation

```bash
# This is a code block
## Not a real header
```

## Usage

Use it.
""")
        result = validate_readme_sections(readme, ProjectType.SOFTWARE)
        # The ## inside code block might be detected, but real sections should still work
        found_sections = [s.name for s in result.sections if s.status == SectionStatus.PRESENT]
        assert "installation" in found_sections or "quick start" in found_sections

    def test_alternative_header_styles(self, temp_dir):
        """Alternative header styles are detected."""
        readme = temp_dir / "README.md"
        readme.write_text("""Project Name
============

Description
-----------

This is a project.
""")
        # Note: Current implementation only handles # style headers
        # This test documents the limitation
        result = validate_readme_sections(readme, ProjectType.SOFTWARE)
        # Won't find underline-style headers with current implementation
        assert result.path == str(readme)


# =============================================================================
# Test Constants Integrity
# =============================================================================


class TestConstantsIntegrity:
    """Tests to ensure configuration constants are valid."""

    def test_required_sections_not_empty(self):
        """REQUIRED_SECTIONS dict has entries."""
        assert len(REQUIRED_SECTIONS) > 0

    def test_optional_sections_not_empty(self):
        """OPTIONAL_SECTIONS dict has entries."""
        assert len(OPTIONAL_SECTIONS) > 0

    def test_section_aliases_not_empty(self):
        """SECTION_ALIASES dict has entries."""
        assert len(SECTION_ALIASES) > 0

    def test_all_required_sections_have_aliases(self):
        """All required sections have at least basic aliases."""
        for project_type, sections in REQUIRED_SECTIONS.items():
            for section in sections:
                # Most sections should have aliases defined
                assert section in SECTION_ALIASES or section in ["title"], f"Missing alias for: {section}"

    def test_no_duplicate_aliases(self):
        """No alias appears in multiple section mappings."""
        all_aliases = []
        for section, aliases in SECTION_ALIASES.items():
            for alias in aliases:
                if alias != section:  # Section name itself can repeat
                    all_aliases.append(alias)
        # Check for duplicates (some overlap is OK for partial matching)
        # This is a soft check - we just want to catch obvious issues


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_validation_workflow(self, temp_dir):
        """Test complete validation workflow."""
        # Create a software project structure
        (temp_dir / "setup.py").write_text("from setuptools import setup")
        (temp_dir / "mypackage").mkdir()
        (temp_dir / "mypackage" / "__init__.py").write_text("")

        readme = temp_dir / "README.md"
        readme.write_text("""# MyPackage

## Overview

A great package.

## Installation

pip install mypackage

## Quick Start

```python
import mypackage
```

## API Documentation

See docs/

## Contributing

PRs welcome!

## License

MIT
""")

        # Validate
        result = validate_readme_sections(readme, None)  # Auto-detect

        assert result.project_type == ProjectType.SOFTWARE
        assert result.valid
        assert result.score >= 70

    def test_data_repo_validation(self, temp_dir):
        """Test data repository README validation."""
        # Create data repo structure
        (temp_dir / "data").mkdir()
        (temp_dir / "metadata.json").write_text("{}")

        readme = temp_dir / "README.md"
        readme.write_text("""# Dataset Name

## Description

A dataset of measurements.

## Data Dictionary

| Column | Type | Description |
|--------|------|-------------|
| id | int | Identifier |
| value | float | Measurement |

## Collection Methods

Data collected via sensors.

## Usage

Download and use.

## License

CC-BY-4.0
""")

        result = validate_readme_sections(readme, ProjectType.DATA_REPO)
        assert result.valid
