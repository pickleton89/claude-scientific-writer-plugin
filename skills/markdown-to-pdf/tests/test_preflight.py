"""
Tests for preflight validation module.

Verifies deterministic behavior of document validation.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from preflight import (  # noqa: E402
    preflight_check,
    PreflightResult,
    list_templates,
    TEMPLATE_SCHEMAS,
    _extract_frontmatter,
    _extract_sections,
)


# ============================================================================
# TEMPLATE SCHEMAS TESTS
# ============================================================================


class TestTemplateSchemas:
    """Test template schema definitions."""

    def test_has_12_templates(self):
        """Schema includes all 12 template types."""
        assert len(TEMPLATE_SCHEMAS) == 12

    def test_template_categories(self):
        """Templates have correct categories."""
        categories = {schema["category"] for schema in TEMPLATE_SCHEMAS.values()}
        assert categories == {"scientific", "project-mgmt", "technical", "meta"}

    def test_scientific_templates(self):
        """Scientific templates are defined."""
        assert "analysis-report" in TEMPLATE_SCHEMAS
        assert "literature-review" in TEMPLATE_SCHEMAS
        assert "data-report" in TEMPLATE_SCHEMAS

    def test_project_mgmt_templates(self):
        """Project management templates are defined."""
        assert "meeting-notes" in TEMPLATE_SCHEMAS
        assert "project-status" in TEMPLATE_SCHEMAS
        assert "phase-plan" in TEMPLATE_SCHEMAS
        assert "task-list" in TEMPLATE_SCHEMAS

    def test_technical_templates(self):
        """Technical templates are defined."""
        assert "technical-spec" in TEMPLATE_SCHEMAS
        assert "method-guide" in TEMPLATE_SCHEMAS
        assert "standards-guide" in TEMPLATE_SCHEMAS

    def test_meta_templates(self):
        """Meta templates are defined."""
        assert "agent-definition" in TEMPLATE_SCHEMAS
        assert "readme" in TEMPLATE_SCHEMAS

    def test_all_have_required_fields(self):
        """All templates have required and optional sections."""
        for template_type, schema in TEMPLATE_SCHEMAS.items():
            assert "required" in schema, f"{template_type} missing required fields"
            assert "required_sections" in schema, f"{template_type} missing required_sections"


# ============================================================================
# LIST_TEMPLATES TESTS
# ============================================================================


class TestListTemplates:
    """Test list_templates function."""

    def test_returns_12_templates(self):
        """Returns all 12 templates."""
        templates = list_templates()
        assert len(templates) == 12

    def test_template_structure(self):
        """Each template has required keys."""
        templates = list_templates()
        for t in templates:
            assert "type" in t
            assert "category" in t
            assert "description" in t

    def test_deterministic_order(self):
        """Same order every time (sorted by type)."""
        templates1 = list_templates()
        templates2 = list_templates()
        assert templates1 == templates2
        # Verify sorted
        types = [t["type"] for t in templates1]
        assert types == sorted(types)


# ============================================================================
# EXTRACT_FRONTMATTER TESTS
# ============================================================================


class TestExtractFrontmatter:
    """Test frontmatter extraction."""

    def test_extracts_valid_frontmatter(self):
        """Extracts valid YAML frontmatter."""
        content = """---
type: analysis-report
title: Test
---

# Content
"""
        fm, body = _extract_frontmatter(content)
        assert fm is not None
        assert fm["type"] == "analysis-report"
        assert fm["title"] == "Test"
        assert "# Content" in body

    def test_no_frontmatter(self):
        """Returns None for content without frontmatter."""
        content = "# Just Content\nNo frontmatter here."
        fm, body = _extract_frontmatter(content)
        assert fm is None

    def test_invalid_yaml(self):
        """Returns None for invalid YAML."""
        content = """---
type: [unclosed
---
"""
        fm, body = _extract_frontmatter(content)
        assert fm is None

    def test_non_dict_yaml(self):
        """Returns None for non-dict YAML."""
        content = """---
- item1
- item2
---
"""
        fm, body = _extract_frontmatter(content)
        assert fm is None


# ============================================================================
# EXTRACT_SECTIONS TESTS
# ============================================================================


class TestExtractSections:
    """Test section heading extraction."""

    def test_extracts_h1_h2(self):
        """Extracts H1 and H2 headings."""
        content = """
# Title
## Section 1
### Subsection
## Section 2
"""
        sections = _extract_sections(content)
        assert "Title" in sections
        assert "Section 1" in sections
        assert "Section 2" in sections
        # H3 not included
        assert "Subsection" not in sections

    def test_empty_content(self):
        """Handles empty content."""
        sections = _extract_sections("")
        assert sections == []


# ============================================================================
# PREFLIGHT_CHECK TESTS
# ============================================================================


class TestPreflightCheck:
    """Test preflight_check function."""

    def test_file_not_found(self):
        """Reports file not found."""
        result = preflight_check("/nonexistent/file.md")
        assert not result.file_exists
        assert not result.is_valid

    def test_invalid_extension(self):
        """Rejects non-md files."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"content")
            path = f.name
        try:
            result = preflight_check(path)
            assert not result.file_extension_valid
            assert not result.is_valid
        finally:
            Path(path).unlink()

    def test_missing_frontmatter(self):
        """Reports missing frontmatter."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write("# Just a heading\nNo frontmatter.")
            path = f.name
        try:
            result = preflight_check(path)
            assert not result.frontmatter_present
            assert not result.is_valid
        finally:
            Path(path).unlink()

    def test_missing_type_field(self):
        """Reports missing type field."""
        content = """---
title: Test
date: 2025-01-09
---

# Test
"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write(content)
            path = f.name
        try:
            result = preflight_check(path)
            assert not result.frontmatter_valid
            assert any("type" in e for e in result.frontmatter_errors)
        finally:
            Path(path).unlink()

    def test_unknown_type(self):
        """Reports unknown document type."""
        content = """---
type: unknown-type
title: Test
date: 2025-01-09
---

# Test
"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write(content)
            path = f.name
        try:
            result = preflight_check(path)
            assert not result.frontmatter_valid
            assert any("Unknown type" in e for e in result.frontmatter_errors)
        finally:
            Path(path).unlink()

    def test_valid_document(self):
        """Validates correct document."""
        content = """---
type: analysis-report
title: Test Analysis
date: 2025-01-09
---

# Test Analysis

## Objective

Test objective.

## Methodology

Test methods.

## Findings

Test findings.
"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write(content)
            path = f.name
        try:
            result = preflight_check(path)
            assert result.is_valid
            assert result.detected_type == "analysis-report"
            assert result.detected_category == "scientific"
        finally:
            Path(path).unlink()

    def test_missing_required_sections(self):
        """Reports missing required sections."""
        content = """---
type: analysis-report
title: Test
date: 2025-01-09
---

# Test

## Introduction

Just intro, missing Objective, Methodology, Findings.
"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write(content)
            path = f.name
        try:
            result = preflight_check(path)
            assert not result.required_sections_present
            assert len(result.missing_sections) > 0
        finally:
            Path(path).unlink()

    def test_counts_elements(self):
        """Includes element counts in result."""
        content = """---
type: task-list
title: Tasks
date: 2025-01-09
---

# Tasks

## Tasks

- [ ] Task 1
- [x] Task 2

| Item | Status |
|------|--------|
| A    | ✓      |
"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write(content)
            path = f.name
        try:
            result = preflight_check(path)
            assert result.element_counts is not None
            assert result.element_counts.tables > 0
            assert result.element_counts.checklists > 0
        finally:
            Path(path).unlink()


# ============================================================================
# PREFLIGHT_RESULT TESTS
# ============================================================================


class TestPreflightResult:
    """Test PreflightResult dataclass."""

    def test_is_valid_checks_all_conditions(self):
        """is_valid checks file, extension, frontmatter, sections."""
        result = PreflightResult()
        assert result.is_valid  # All defaults are True

        result.file_exists = False
        assert not result.is_valid

        result.file_exists = True
        result.frontmatter_valid = False
        assert not result.is_valid

    def test_format_report_deterministic(self):
        """format_report produces consistent output."""
        result = PreflightResult(
            file_path="test.md",
            detected_type="analysis-report",
            detected_category="scientific",
        )
        report1 = result.format_report()
        report2 = result.format_report()
        assert report1 == report2
        assert "PASS" in report1
        assert "analysis-report" in report1

    def test_format_errors(self):
        """format_errors lists all errors."""
        result = PreflightResult(
            file_exists=False,
            file_path="/missing/file.md",
            frontmatter_errors=["Missing type"],
        )
        errors = result.format_errors()
        assert "FileNotFoundError" in errors
