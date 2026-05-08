"""
Element Detection Patterns for Markdown-to-PDF

Deterministic pattern matching for document elements. Used in `/doc-to-pdf`
Step 2 (structure confirmation) to surface counts of callout candidates,
table variants, finding cards, and code blocks before the LLM slot-fills the
HTML template.

Output is informational — the LLM, not this module, decides which HTML class
to assign in the filled template.

Usage:
    from scripts.element_detector import detect_element_type, count_elements

    counts = count_elements(markdown_content)
    # -> ElementCounts(tables=3, status_tables=1, callouts=2, findings=4, ...)

All patterns use explicit membership checks — no heuristics, no LLM inference.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

# ============================================================================
# DETECTION PATTERNS (Single Source of Truth)
# ============================================================================

# Status symbols indicating pass/fail compliance
STATUS_SYMBOLS: frozenset[str] = frozenset({
    "✓", "✗", "✔", "✘",  # Unicode checkmarks
    "Yes", "No",
    "Pass", "Fail",
    "Done", "Pending",
})

# Grade values for rating/scoring tables
GRADE_VALUES: frozenset[str] = frozenset({
    "A", "B", "C", "D", "F",  # Letter grades
    "Tier 1", "Tier 2", "Tier 3",  # Tier rankings
    "High", "Medium", "Low",  # Priority levels
})

# Finding heading patterns (regex)
FINDING_PATTERN: re.Pattern[str] = re.compile(r"^#{4}\s+(Finding\s+\d+:|Key\s+Finding:)", re.MULTILINE)

# Callout prefix patterns for blockquote detection
CALLOUT_PREFIXES: dict[str, list[str]] = {
    "info": ["> **Note:**", "> **Info:**"],
    "success": ["> **Tip:**"],
    "warning": ["> **Warning:**", "> **Caution:**"],
    "alert": ["> **Important:**", "> **Critical:**"],
}

# Languages that render as MethodBlock (not generic code)
METHOD_LANGUAGES: frozenset[str] = frozenset({
    "python", "r", "bash", "sql", "pseudocode", "algorithm",
})

# ============================================================================
# ELEMENT COUNTS DATACLASS
# ============================================================================


@dataclass(frozen=True)
class ElementCounts:
    """
    Counts of document elements detected via deterministic patterns.

    Frozen dataclass ensures immutability for reproducibility.
    """

    tables: int = 0
    status_tables: int = 0
    graded_tables: int = 0
    findings: int = 0
    callouts: int = 0
    callouts_by_type: dict[str, int] = field(default_factory=dict)
    code_blocks: int = 0
    method_blocks: int = 0
    checklists: int = 0

    def to_summary(self) -> str:
        """
        Format element counts as deterministic summary string.

        Returns:
            Fixed-format summary string for LLM output consistency.

        Example:
            "3 tables (1 StatusTable, 1 GradedTable, 1 standard)"
        """
        lines = []

        # Tables breakdown
        if self.tables > 0:
            parts = []
            if self.status_tables > 0:
                parts.append(f"{self.status_tables} StatusTable")
            if self.graded_tables > 0:
                parts.append(f"{self.graded_tables} GradedTable")
            standard = self.tables - self.status_tables - self.graded_tables
            if standard > 0:
                parts.append(f"{standard} standard")
            lines.append(f"{self.tables} tables ({', '.join(parts)})")

        # Findings
        if self.findings > 0:
            lines.append(f"{self.findings} FindingCards")

        # Code blocks breakdown
        if self.code_blocks > 0:
            if self.method_blocks > 0:
                other = self.code_blocks - self.method_blocks
                if other > 0:
                    lines.append(f"{self.code_blocks} code blocks ({self.method_blocks} MethodBlock, {other} standard)")
                else:
                    lines.append(f"{self.method_blocks} MethodBlocks")
            else:
                lines.append(f"{self.code_blocks} code blocks")

        # Callouts breakdown
        if self.callouts > 0:
            if self.callouts_by_type:
                parts = [f"{count} {ctype}" for ctype, count in sorted(self.callouts_by_type.items())]
                lines.append(f"{self.callouts} CalloutBoxes ({', '.join(parts)})")
            else:
                lines.append(f"{self.callouts} CalloutBoxes")

        # Checklists
        if self.checklists > 0:
            lines.append(f"{self.checklists} checklists")

        return "\n".join(f"- {line}" for line in lines) if lines else "- No special elements detected"


# ============================================================================
# DETECTION FUNCTIONS
# ============================================================================


ElementType = Literal[
    "status_table", "graded_table", "table",
    "finding",
    "method_block", "code_block",
    "callout_info", "callout_success", "callout_warning", "callout_alert",
    "checklist", "list",
    "paragraph",
]


def has_status_symbols(cells: list[str]) -> bool:
    """
    Check if any cell contains a status symbol.

    Args:
        cells: List of cell content strings from a table.

    Returns:
        True if any cell matches a STATUS_SYMBOL exactly (stripped).
    """
    return any(cell.strip() in STATUS_SYMBOLS for cell in cells)


def has_grade_values(cells: list[str]) -> bool:
    """
    Check if any cell contains a grade value.

    Args:
        cells: List of cell content strings from a table.

    Returns:
        True if any cell matches a GRADE_VALUE exactly (stripped).
    """
    return any(cell.strip() in GRADE_VALUES for cell in cells)


def detect_table_type(rows: list[list[str]]) -> Literal["status_table", "graded_table", "table"]:
    """
    Detect table type based on cell content.

    Priority: status_table > graded_table > table

    Args:
        rows: List of rows, each row is a list of cell strings.

    Returns:
        Table type identifier.
    """
    all_cells = [cell for row in rows for cell in row]

    if has_status_symbols(all_cells):
        return "status_table"
    if has_grade_values(all_cells):
        return "graded_table"
    return "table"


def detect_callout_type(line: str) -> str | None:
    """
    Detect callout type from blockquote line.

    Args:
        line: Line starting with '>'.

    Returns:
        Callout type ("info", "success", "warning", "alert") or None.
    """
    for callout_type, prefixes in CALLOUT_PREFIXES.items():
        for prefix in prefixes:
            if line.startswith(prefix):
                return callout_type
    return None


def is_finding_heading(line: str) -> bool:
    """
    Check if line is a finding heading.

    Args:
        line: Heading line to check.

    Returns:
        True if matches Finding N: or Key Finding: pattern.
    """
    return bool(FINDING_PATTERN.match(line.strip()))


def detect_element_type(element_data: dict) -> ElementType:
    """
    Detect element type from parsed element data.

    Args:
        element_data: Dictionary with 'type' and content fields.

    Returns:
        Specific element type for component mapping.
    """
    elem_type = element_data.get("type", "")

    if elem_type == "table":
        rows = element_data.get("rows", [])
        return detect_table_type(rows)

    if elem_type == "heading":
        text = element_data.get("text", "")
        if is_finding_heading(text):
            return "finding"
        return "paragraph"  # Treat non-finding headings as content

    if elem_type == "code_block":
        language = element_data.get("language", "").lower()
        if language in METHOD_LANGUAGES:
            return "method_block"
        return "code_block"

    if elem_type == "blockquote":
        content = element_data.get("content", "")
        first_line = content.split("\n")[0] if content else ""
        callout_type = detect_callout_type(first_line)
        if callout_type:
            return f"callout_{callout_type}"  # type: ignore[return-value]
        return "paragraph"  # Plain blockquote

    if elem_type == "list":
        items = element_data.get("items", [])
        # Check for checkbox pattern
        for item in items:
            if isinstance(item, str) and (item.startswith("[ ]") or item.startswith("[x]") or item.startswith("[X]")):
                return "checklist"
        return "list"

    return "paragraph"


# ============================================================================
# MARKDOWN PARSING FOR ELEMENT COUNTING
# ============================================================================


def _parse_tables(content: str) -> list[list[list[str]]]:
    """
    Extract tables from markdown content.

    Returns list of tables, each table is list of rows, each row is list of cells.
    """
    tables = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Detect table start (line with | characters)
        if line.startswith("|") and "|" in line[1:]:
            table_rows = []

            while i < len(lines):
                line = lines[i].strip()
                if not line.startswith("|"):
                    break

                # Skip separator rows (|---|---|)
                if re.match(r"^\|[\s\-:|]+\|$", line):
                    i += 1
                    continue

                # Parse cells
                cells = [cell.strip() for cell in line.split("|")[1:-1]]
                if cells:
                    table_rows.append(cells)
                i += 1

            if table_rows:
                tables.append(table_rows)
        else:
            i += 1

    return tables


def _count_findings(content: str) -> int:
    """Count finding headings in content."""
    return len(FINDING_PATTERN.findall(content))


def _count_callouts(content: str) -> dict[str, int]:
    """Count callouts by type."""
    counts: dict[str, int] = {}

    for line in content.split("\n"):
        line = line.strip()
        if line.startswith(">"):
            callout_type = detect_callout_type(line)
            if callout_type:
                counts[callout_type] = counts.get(callout_type, 0) + 1

    return counts


def _count_code_blocks(content: str) -> tuple[int, int]:
    """
    Count code blocks and method blocks.

    Returns:
        Tuple of (total_code_blocks, method_blocks)
    """
    # Match fenced code blocks with optional language
    pattern = re.compile(r"^```(\w*)\s*$", re.MULTILINE)

    total = 0
    method_blocks = 0

    # Find all code block starts
    matches = list(pattern.finditer(content))

    # Each pair of ``` markers is one code block
    for i in range(0, len(matches) - 1, 2):
        total += 1
        language = matches[i].group(1).lower()
        if language in METHOD_LANGUAGES:
            method_blocks += 1

    return total, method_blocks


def _count_checklists(content: str) -> int:
    """Count checklist items."""
    pattern = re.compile(r"^[-*]\s+\[[xX ]\]", re.MULTILINE)
    matches = pattern.findall(content)
    # Count unique checklist blocks (consecutive items)
    return 1 if matches else 0  # Simplified: count as 1 checklist if any items found


def count_elements(content: str) -> ElementCounts:
    """
    Count all document elements using deterministic patterns.

    Args:
        content: Raw markdown content string.

    Returns:
        ElementCounts with counts of all detected elements.
    """
    # Parse tables and classify
    tables = _parse_tables(content)
    status_tables = sum(1 for t in tables if detect_table_type(t) == "status_table")
    graded_tables = sum(1 for t in tables if detect_table_type(t) == "graded_table")

    # Count other elements
    findings = _count_findings(content)
    callouts_by_type = _count_callouts(content)
    code_blocks, method_blocks = _count_code_blocks(content)
    checklists = _count_checklists(content)

    return ElementCounts(
        tables=len(tables),
        status_tables=status_tables,
        graded_tables=graded_tables,
        findings=findings,
        callouts=sum(callouts_by_type.values()),
        callouts_by_type=callouts_by_type,
        code_blocks=code_blocks,
        method_blocks=method_blocks,
        checklists=checklists,
    )
