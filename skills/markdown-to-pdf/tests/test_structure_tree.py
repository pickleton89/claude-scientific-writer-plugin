"""
Tests for structure_tree module.

Verifies deterministic ASCII tree generation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from structure_tree import (  # noqa: E402
    parse_document_tree,
    format_structure_tree,
    format_flat_structure,
    format_element_mapping,
    DocumentTree,
    Section,
)


# ============================================================================
# PARSE_DOCUMENT_TREE TESTS
# ============================================================================


class TestParseDocumentTree:
    """Test document tree parsing."""

    def test_empty_content(self):
        """Handles empty content."""
        tree = parse_document_tree("")
        assert tree.title == ""
        assert tree.sections == []

    def test_extracts_title_from_h1(self):
        """Uses first H1 as title if no frontmatter."""
        content = "# My Document\n\n## Section 1"
        tree = parse_document_tree(content)
        assert tree.title == "My Document"

    def test_uses_frontmatter_title(self):
        """Prefers frontmatter title over H1."""
        content = "# Document Heading\n\n## Section"
        frontmatter = {"title": "Frontmatter Title", "type": "readme"}
        tree = parse_document_tree(content, frontmatter)
        assert tree.title == "Frontmatter Title"
        assert tree.doc_type == "readme"

    def test_builds_section_hierarchy(self):
        """Builds correct section hierarchy."""
        content = """
# Title

## Section 1

### Subsection 1.1

### Subsection 1.2

## Section 2

### Subsection 2.1
"""
        tree = parse_document_tree(content)
        # H1 is at top level, H2 sections are children of H1
        assert len(tree.sections) == 1
        assert tree.sections[0].level == 1
        # Two H2 sections as children of H1
        h2_sections = tree.sections[0].children
        assert len(h2_sections) == 2
        # First H2 section has 2 H3 children
        assert len(h2_sections[0].children) == 2

    def test_detects_section_elements(self):
        """Detects elements within sections."""
        content = """
# Report

## Data

| A | B |
|---|---|
| 1 | 2 |

## Findings

#### Finding 1: Result

Description.

## Notes

> **Warning:** Be careful.
"""
        tree = parse_document_tree(content)
        # H1 "Report" is at top level, H2 sections are children
        assert len(tree.sections) == 1
        h2_sections = tree.sections[0].children

        # Find sections and check element types
        data_section = next(s for s in h2_sections if s.title == "Data")
        assert "table" in data_section.element_types

        findings_section = next(s for s in h2_sections if s.title == "Findings")
        # Finding heading becomes a child section, check it exists
        assert len(findings_section.children) == 1
        assert "Finding 1" in findings_section.children[0].title

        notes_section = next(s for s in h2_sections if s.title == "Notes")
        assert "callout" in notes_section.element_types


# ============================================================================
# FORMAT_STRUCTURE_TREE TESTS
# ============================================================================


class TestFormatStructureTree:
    """Test structure tree formatting."""

    @pytest.fixture
    def sample_tree(self) -> DocumentTree:
        """Create sample document tree."""
        tree = DocumentTree(
            title="Test Document",
            doc_type="analysis-report",
            sections=[
                Section(
                    level=2,
                    title="Introduction",
                    element_types=[],
                    children=[],
                ),
                Section(
                    level=2,
                    title="Methodology",
                    element_types=["code"],
                    children=[
                        Section(level=3, title="Data Collection", element_types=["table"]),
                        Section(level=3, title="Analysis", element_types=[]),
                    ],
                ),
                Section(
                    level=2,
                    title="Results",
                    element_types=["finding", "table"],
                    children=[],
                ),
            ],
        )
        return tree

    def test_includes_title(self, sample_tree: DocumentTree):
        """Output includes document title."""
        output = format_structure_tree(sample_tree)
        assert "Test Document" in output

    def test_includes_type(self, sample_tree: DocumentTree):
        """Output includes document type."""
        output = format_structure_tree(sample_tree)
        assert "analysis-report" in output

    def test_unicode_style(self, sample_tree: DocumentTree):
        """Unicode style uses box-drawing characters."""
        output = format_structure_tree(sample_tree, style="unicode")
        assert "├──" in output or "└──" in output

    def test_ascii_style(self, sample_tree: DocumentTree):
        """ASCII style uses plain characters."""
        output = format_structure_tree(sample_tree, style="ascii")
        assert "+--" in output or "`--" in output

    def test_shows_elements(self, sample_tree: DocumentTree):
        """Shows element annotations when enabled."""
        output = format_structure_tree(sample_tree, show_elements=True)
        assert "[code]" in output
        assert "[finding, table]" in output or "[table, finding]" in output

    def test_hides_elements(self, sample_tree: DocumentTree):
        """Hides element annotations when disabled."""
        output = format_structure_tree(sample_tree, show_elements=False)
        assert "[code]" not in output
        assert "[table]" not in output

    def test_deterministic_output(self, sample_tree: DocumentTree):
        """Same tree always produces same output."""
        output1 = format_structure_tree(sample_tree)
        output2 = format_structure_tree(sample_tree)
        output3 = format_structure_tree(sample_tree)
        assert output1 == output2 == output3

    def test_nested_structure(self, sample_tree: DocumentTree):
        """Correctly shows nested sections."""
        output = format_structure_tree(sample_tree)
        # Subsections should be indented under Methodology
        lines = output.split("\n")
        methodology_line = next(line for line in lines if "Methodology" in line)
        data_collection_line = next(line for line in lines if "Data Collection" in line)
        # Data Collection should come after Methodology
        assert lines.index(methodology_line) < lines.index(data_collection_line)


# ============================================================================
# FORMAT_FLAT_STRUCTURE TESTS
# ============================================================================


class TestFormatFlatStructure:
    """Test flat structure formatting."""

    def test_numbered_sections(self):
        """Uses numbered format."""
        tree = DocumentTree(
            title="Doc",
            sections=[
                Section(level=2, title="First"),
                Section(level=2, title="Second"),
            ],
        )
        output = format_flat_structure(tree)
        assert "1. First" in output
        assert "2. Second" in output

    def test_nested_numbering(self):
        """Uses nested numbering for subsections."""
        tree = DocumentTree(
            title="Doc",
            sections=[
                Section(
                    level=2,
                    title="Section",
                    children=[
                        Section(level=3, title="Subsection"),
                    ],
                ),
            ],
        )
        output = format_flat_structure(tree)
        assert "1. Section" in output
        assert "1.1. Subsection" in output


# ============================================================================
# FORMAT_ELEMENT_MAPPING TESTS
# ============================================================================


class TestFormatElementMapping:
    """Test element to component mapping."""

    def test_empty_tree(self):
        """Handles tree with no special elements."""
        tree = DocumentTree(sections=[Section(level=2, title="Plain")])
        output = format_element_mapping(tree)
        assert "No special elements detected" in output

    def test_maps_tables(self):
        """Maps tables to table components."""
        tree = DocumentTree(
            sections=[Section(level=2, title="Data", element_types=["table"])]
        )
        output = format_element_mapping(tree)
        assert "table" in output
        assert "StatusTable" in output or "BaseTable" in output

    def test_maps_findings(self):
        """Maps findings to FindingCard."""
        tree = DocumentTree(
            sections=[Section(level=2, title="Results", element_types=["finding"])]
        )
        output = format_element_mapping(tree)
        assert "finding" in output
        assert "FindingCard" in output

    def test_maps_code(self):
        """Maps code to MethodBlock."""
        tree = DocumentTree(
            sections=[Section(level=2, title="Methods", element_types=["code"])]
        )
        output = format_element_mapping(tree)
        assert "code" in output
        assert "MethodBlock" in output

    def test_aggregates_from_children(self):
        """Aggregates elements from nested sections."""
        tree = DocumentTree(
            sections=[
                Section(
                    level=2,
                    title="Parent",
                    element_types=["table"],
                    children=[
                        Section(level=3, title="Child", element_types=["finding"]),
                    ],
                ),
            ],
        )
        output = format_element_mapping(tree)
        assert "table" in output
        assert "finding" in output


# ============================================================================
# DETERMINISM TESTS
# ============================================================================


class TestDeterminism:
    """Test deterministic behavior across multiple calls."""

    def test_parse_deterministic(self):
        """Parsing same content produces identical trees."""
        content = """
# Title

## Section 1

Content.

## Section 2

More content.
"""
        tree1 = parse_document_tree(content)
        tree2 = parse_document_tree(content)

        assert tree1.title == tree2.title
        assert len(tree1.sections) == len(tree2.sections)
        for s1, s2 in zip(tree1.sections, tree2.sections):
            assert s1.title == s2.title
            assert s1.level == s2.level

    def test_format_deterministic(self):
        """Formatting same tree produces identical output."""
        tree = DocumentTree(
            title="Test",
            doc_type="readme",
            sections=[
                Section(level=2, title="A"),
                Section(level=2, title="B"),
            ],
        )

        outputs = [format_structure_tree(tree) for _ in range(5)]
        assert all(o == outputs[0] for o in outputs)
