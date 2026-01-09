"""
Structure Tree Generator for Markdown-to-PDF

Provides deterministic ASCII tree representation of document structure.
Same input always produces identical tree output - no LLM variation.

Usage:
    from scripts.structure_tree import format_structure_tree, parse_document_tree

    tree = parse_document_tree(markdown_content)
    ascii_tree = format_structure_tree(tree)
    # -> Deterministic ASCII tree string
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal


# ============================================================================
# DOCUMENT STRUCTURE DATACLASSES
# ============================================================================


@dataclass
class Section:
    """
    Represents a document section with heading and content.

    Attributes:
        level: Heading level (1-6)
        title: Section title text
        children: Nested subsections
        element_types: Types of elements in this section
    """

    level: int
    title: str
    children: list[Section] = field(default_factory=list)
    element_types: list[str] = field(default_factory=list)


@dataclass
class DocumentTree:
    """
    Represents parsed document structure.

    Attributes:
        title: Document title (from frontmatter or H1)
        doc_type: Document type from frontmatter
        sections: Top-level sections
    """

    title: str = ""
    doc_type: str = ""
    sections: list[Section] = field(default_factory=list)


# ============================================================================
# TREE PARSING
# ============================================================================


def parse_document_tree(content: str, frontmatter: dict | None = None) -> DocumentTree:
    """
    Parse markdown content into a document tree structure.

    Args:
        content: Markdown content (without frontmatter YAML).
        frontmatter: Optional parsed frontmatter dict.

    Returns:
        DocumentTree with hierarchical section structure.
    """
    tree = DocumentTree()

    # Set metadata from frontmatter
    if frontmatter:
        tree.title = frontmatter.get("title", "")
        tree.doc_type = frontmatter.get("type", "")

    # Parse headings into sections
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(content))

    if not matches:
        return tree

    # If no title from frontmatter, use first H1
    if not tree.title:
        for match in matches:
            if len(match.group(1)) == 1:
                tree.title = match.group(2).strip()
                break

    # Build section hierarchy
    sections_stack: list[tuple[int, Section]] = []  # (level, section)

    for i, match in enumerate(matches):
        level = len(match.group(1))
        title = match.group(2).strip()

        # Get content between this heading and next (for element detection)
        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_content = content[start_pos:end_pos]

        # Detect element types in this section
        element_types = _detect_section_elements(section_content)

        section = Section(level=level, title=title, element_types=element_types)

        # Find parent section
        while sections_stack and sections_stack[-1][0] >= level:
            sections_stack.pop()

        if sections_stack:
            # Add as child of parent
            parent = sections_stack[-1][1]
            parent.children.append(section)
        else:
            # Top-level section
            tree.sections.append(section)

        sections_stack.append((level, section))

    return tree


def _detect_section_elements(content: str) -> list[str]:
    """
    Detect special element types in section content.

    Returns list of element type strings found.
    """
    elements = []

    # Tables
    if re.search(r"^\|.+\|$", content, re.MULTILINE):
        elements.append("table")

    # Findings
    if re.search(r"^#{4}\s+(Finding\s+\d+:|Key\s+Finding:)", content, re.MULTILINE):
        elements.append("finding")

    # Code blocks
    if "```" in content:
        elements.append("code")

    # Callouts
    if re.search(r"^>\s+\*\*(Note|Warning|Important|Tip|Info|Caution|Critical):\*\*", content, re.MULTILINE):
        elements.append("callout")

    # Checklists
    if re.search(r"^[-*]\s+\[[xX ]\]", content, re.MULTILINE):
        elements.append("checklist")

    return elements


# ============================================================================
# TREE FORMATTING
# ============================================================================


TreeStyle = Literal["unicode", "ascii"]


def format_structure_tree(
    tree: DocumentTree,
    style: TreeStyle = "unicode",
    show_elements: bool = True,
) -> str:
    """
    Format document tree as ASCII/Unicode tree representation.

    Args:
        tree: Parsed DocumentTree structure.
        style: "unicode" for box-drawing chars, "ascii" for plain ASCII.
        show_elements: Whether to annotate sections with element types.

    Returns:
        Deterministic tree string - same input always produces same output.
    """
    if style == "unicode":
        branch = "├── "
        last_branch = "└── "
        pipe = "│   "
        space = "    "
    else:
        branch = "+-- "
        last_branch = "`-- "
        pipe = "|   "
        space = "    "

    lines = []

    # Document header
    if tree.title:
        lines.append(f"📄 {tree.title}")
    if tree.doc_type:
        lines.append(f"📋 Type: {tree.doc_type}")
    if lines:
        lines.append("")

    # Build tree
    def format_section(section: Section, prefix: str, is_last: bool) -> None:
        # Choose branch character
        connector = last_branch if is_last else branch

        # Format section line
        section_line = f"{prefix}{connector}{section.title}"

        # Add element annotations if requested
        if show_elements and section.element_types:
            annotations = ", ".join(section.element_types)
            section_line += f" [{annotations}]"

        lines.append(section_line)

        # Recursively format children
        child_prefix = prefix + (space if is_last else pipe)
        for i, child in enumerate(section.children):
            is_last_child = i == len(section.children) - 1
            format_section(child, child_prefix, is_last_child)

    # Format all top-level sections
    for i, section in enumerate(tree.sections):
        is_last = i == len(tree.sections) - 1
        format_section(section, "", is_last)

    return "\n".join(lines)


def format_flat_structure(tree: DocumentTree) -> str:
    """
    Format document tree as flat numbered list.

    Alternative to tree format for simpler output.

    Returns:
        Numbered list of sections.
    """
    lines = []

    if tree.title:
        lines.append(f"📄 Document: {tree.title}")
    if tree.doc_type:
        lines.append(f"📋 Type: {tree.doc_type}")
    if lines:
        lines.append("")
        lines.append("Structure:")

    def format_section(section: Section, number_prefix: str, index: int) -> None:
        current_number = f"{number_prefix}{index}"
        indent = "  " * (current_number.count("."))
        lines.append(f"{indent}{current_number}. {section.title}")

        for i, child in enumerate(section.children, 1):
            format_section(child, f"{current_number}.", i)

    for i, section in enumerate(tree.sections, 1):
        format_section(section, "", i)

    return "\n".join(lines)


# ============================================================================
# SUMMARY FORMATTING
# ============================================================================


def format_element_mapping(tree: DocumentTree) -> str:
    """
    Format element type to component mapping summary.

    Shows what PDF components will be used for detected elements.
    """
    # Collect all elements from all sections
    all_elements: dict[str, int] = {}

    def collect_elements(section: Section) -> None:
        for elem in section.element_types:
            all_elements[elem] = all_elements.get(elem, 0) + 1
        for child in section.children:
            collect_elements(child)

    for section in tree.sections:
        collect_elements(section)

    if not all_elements:
        return "No special elements detected"

    # Map elements to components
    component_map = {
        "table": "StatusTable/GradedTable/BaseTable",
        "finding": "FindingCard",
        "code": "MethodBlock/CodeBlock",
        "callout": "CalloutBox",
        "checklist": "Checklist (rendered)",
    }

    lines = ["Elements Detected:"]
    for elem_type, count in sorted(all_elements.items()):
        component = component_map.get(elem_type, "Standard element")
        lines.append(f"- {count} {elem_type}(s) → {component}")

    return "\n".join(lines)
