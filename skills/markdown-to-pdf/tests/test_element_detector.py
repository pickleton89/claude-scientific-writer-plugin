"""
Tests for element_detector module.

Verifies deterministic behavior of element detection patterns.
Same input must always produce same output.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from element_detector import (  # noqa: E402
    STATUS_SYMBOLS,
    GRADE_VALUES,
    CALLOUT_PREFIXES,
    METHOD_LANGUAGES,
    has_status_symbols,
    has_grade_values,
    detect_table_type,
    detect_callout_type,
    is_finding_heading,
    detect_element_type,
    count_elements,
    ElementCounts,
)


# ============================================================================
# PATTERN CONSTANTS TESTS
# ============================================================================


class TestPatternConstants:
    """Test that pattern constants are correctly defined."""

    def test_status_symbols_contains_checkmarks(self):
        """Status symbols include unicode checkmarks."""
        assert "✓" in STATUS_SYMBOLS
        assert "✗" in STATUS_SYMBOLS
        assert "✔" in STATUS_SYMBOLS
        assert "✘" in STATUS_SYMBOLS

    def test_status_symbols_contains_text(self):
        """Status symbols include text variants."""
        assert "Yes" in STATUS_SYMBOLS
        assert "No" in STATUS_SYMBOLS
        assert "Pass" in STATUS_SYMBOLS
        assert "Fail" in STATUS_SYMBOLS
        assert "Done" in STATUS_SYMBOLS
        assert "Pending" in STATUS_SYMBOLS

    def test_grade_values_contains_letters(self):
        """Grade values include letter grades."""
        assert "A" in GRADE_VALUES
        assert "B" in GRADE_VALUES
        assert "C" in GRADE_VALUES
        assert "D" in GRADE_VALUES
        assert "F" in GRADE_VALUES

    def test_grade_values_contains_tiers(self):
        """Grade values include tier rankings."""
        assert "Tier 1" in GRADE_VALUES
        assert "Tier 2" in GRADE_VALUES
        assert "Tier 3" in GRADE_VALUES

    def test_grade_values_contains_priorities(self):
        """Grade values include priority levels."""
        assert "High" in GRADE_VALUES
        assert "Medium" in GRADE_VALUES
        assert "Low" in GRADE_VALUES

    def test_method_languages(self):
        """Method languages include expected code types."""
        assert "python" in METHOD_LANGUAGES
        assert "r" in METHOD_LANGUAGES
        assert "bash" in METHOD_LANGUAGES
        assert "sql" in METHOD_LANGUAGES
        assert "pseudocode" in METHOD_LANGUAGES
        assert "algorithm" in METHOD_LANGUAGES

    def test_callout_prefixes_keys(self):
        """Callout prefixes include all expected types."""
        assert "info" in CALLOUT_PREFIXES
        assert "success" in CALLOUT_PREFIXES
        assert "warning" in CALLOUT_PREFIXES
        assert "alert" in CALLOUT_PREFIXES


# ============================================================================
# HAS_STATUS_SYMBOLS TESTS
# ============================================================================


class TestHasStatusSymbols:
    """Test has_status_symbols function."""

    def test_detects_checkmark(self):
        """Detects checkmark symbols."""
        assert has_status_symbols(["Item", "✓"])
        assert has_status_symbols(["✗", "Item"])

    def test_detects_text_status(self):
        """Detects text status values."""
        assert has_status_symbols(["Feature", "Yes"])
        assert has_status_symbols(["Test", "Pass"])

    def test_ignores_partial_matches(self):
        """Does not match partial strings."""
        assert not has_status_symbols(["Yesterday", "Tomorrow"])
        assert not has_status_symbols(["Passing grade"])

    def test_empty_cells(self):
        """Handles empty cell list."""
        assert not has_status_symbols([])

    def test_strips_whitespace(self):
        """Strips whitespace before matching."""
        assert has_status_symbols(["  ✓  "])
        assert has_status_symbols(["  Yes  "])


# ============================================================================
# HAS_GRADE_VALUES TESTS
# ============================================================================


class TestHasGradeValues:
    """Test has_grade_values function."""

    def test_detects_letter_grades(self):
        """Detects letter grades."""
        assert has_grade_values(["Criterion", "A"])
        assert has_grade_values(["Test", "F"])

    def test_detects_tiers(self):
        """Detects tier rankings."""
        assert has_grade_values(["Component", "Tier 1"])

    def test_detects_priorities(self):
        """Detects priority levels."""
        assert has_grade_values(["Issue", "High"])

    def test_ignores_non_grade_text(self):
        """Does not match non-grade text."""
        assert not has_grade_values(["Apple", "Banana"])
        assert not has_grade_values(["Grade A milk"])

    def test_empty_cells(self):
        """Handles empty cell list."""
        assert not has_grade_values([])


# ============================================================================
# DETECT_TABLE_TYPE TESTS
# ============================================================================


class TestDetectTableType:
    """Test detect_table_type function."""

    def test_status_table_priority(self):
        """Status symbols take priority over grades."""
        rows = [["Item", "✓", "A"]]
        assert detect_table_type(rows) == "status_table"

    def test_graded_table(self):
        """Detects graded tables."""
        rows = [["Criterion", "Score"], ["Clarity", "A"], ["Accuracy", "B"]]
        assert detect_table_type(rows) == "graded_table"

    def test_regular_table(self):
        """Falls back to regular table."""
        rows = [["Name", "Value"], ["foo", "bar"]]
        assert detect_table_type(rows) == "table"

    def test_empty_table(self):
        """Handles empty table."""
        assert detect_table_type([]) == "table"


# ============================================================================
# DETECT_CALLOUT_TYPE TESTS
# ============================================================================


class TestDetectCalloutType:
    """Test detect_callout_type function."""

    def test_info_callouts(self):
        """Detects info callout types."""
        assert detect_callout_type("> **Note:** This is a note") == "info"
        assert detect_callout_type("> **Info:** Information here") == "info"

    def test_success_callouts(self):
        """Detects success callout types."""
        assert detect_callout_type("> **Tip:** Here's a tip") == "success"

    def test_warning_callouts(self):
        """Detects warning callout types."""
        assert detect_callout_type("> **Warning:** Be careful") == "warning"
        assert detect_callout_type("> **Caution:** Take care") == "warning"

    def test_alert_callouts(self):
        """Detects alert callout types."""
        assert detect_callout_type("> **Important:** Critical info") == "alert"
        assert detect_callout_type("> **Critical:** Urgent") == "alert"

    def test_non_callout_blockquote(self):
        """Returns None for non-callout blockquotes."""
        assert detect_callout_type("> Just a regular quote") is None
        assert detect_callout_type("> **Custom:** label") is None


# ============================================================================
# IS_FINDING_HEADING TESTS
# ============================================================================


class TestIsFindingHeading:
    """Test is_finding_heading function."""

    def test_numbered_finding(self):
        """Detects numbered findings."""
        assert is_finding_heading("#### Finding 1: Title")
        assert is_finding_heading("#### Finding 42: Another")

    def test_key_finding(self):
        """Detects key findings."""
        assert is_finding_heading("#### Key Finding: Important")

    def test_non_finding_headings(self):
        """Rejects non-finding headings."""
        assert not is_finding_heading("#### Methodology")
        assert not is_finding_heading("## Finding in wrong level")
        assert not is_finding_heading("#### Found something")


# ============================================================================
# DETECT_ELEMENT_TYPE TESTS
# ============================================================================


class TestDetectElementType:
    """Test detect_element_type function."""

    def test_status_table_detection(self):
        """Detects status tables."""
        elem = {"type": "table", "rows": [["Item", "✓"]]}
        assert detect_element_type(elem) == "status_table"

    def test_graded_table_detection(self):
        """Detects graded tables."""
        elem = {"type": "table", "rows": [["Test", "A"]]}
        assert detect_element_type(elem) == "graded_table"

    def test_finding_detection(self):
        """Detects findings."""
        elem = {"type": "heading", "text": "#### Finding 1: Title"}
        assert detect_element_type(elem) == "finding"

    def test_method_block_detection(self):
        """Detects method blocks."""
        elem = {"type": "code_block", "language": "python", "code": "x = 1"}
        assert detect_element_type(elem) == "method_block"

    def test_regular_code_block(self):
        """Detects regular code blocks."""
        elem = {"type": "code_block", "language": "json", "code": "{}"}
        assert detect_element_type(elem) == "code_block"

    def test_callout_detection(self):
        """Detects callouts."""
        elem = {"type": "blockquote", "content": "> **Warning:** Be careful"}
        assert detect_element_type(elem) == "callout_warning"

    def test_checklist_detection(self):
        """Detects checklists."""
        elem = {"type": "list", "items": ["[ ] Task 1", "[x] Task 2"]}
        assert detect_element_type(elem) == "checklist"


# ============================================================================
# COUNT_ELEMENTS TESTS
# ============================================================================


class TestCountElements:
    """Test count_elements function for determinism."""

    @pytest.fixture
    def sample_markdown(self) -> str:
        """Sample markdown with various elements."""
        return """---
type: analysis-report
title: Test Report
date: 2025-01-09
---

# Test Report

## Methodology

| Item | Status |
|------|--------|
| Test A | ✓ |
| Test B | ✗ |

## Findings

#### Finding 1: Important Result

This is the first finding.

#### Finding 2: Another Result

This is another finding.

## Code

```python
def hello():
    print("Hello")
```

```json
{"key": "value"}
```

## Notes

> **Warning:** This is a warning callout.

- [x] Task completed
- [ ] Task pending
"""

    def test_counts_tables(self, sample_markdown: str):
        """Counts tables correctly."""
        counts = count_elements(sample_markdown)
        assert counts.tables == 1
        assert counts.status_tables == 1

    def test_counts_findings(self, sample_markdown: str):
        """Counts findings correctly."""
        counts = count_elements(sample_markdown)
        assert counts.findings == 2

    def test_counts_code_blocks(self, sample_markdown: str):
        """Counts code blocks correctly."""
        counts = count_elements(sample_markdown)
        assert counts.code_blocks == 2
        assert counts.method_blocks == 1

    def test_counts_callouts(self, sample_markdown: str):
        """Counts callouts correctly."""
        counts = count_elements(sample_markdown)
        assert counts.callouts == 1
        assert counts.callouts_by_type.get("warning") == 1

    def test_counts_checklists(self, sample_markdown: str):
        """Counts checklists correctly."""
        counts = count_elements(sample_markdown)
        assert counts.checklists == 1

    def test_determinism(self, sample_markdown: str):
        """Same input always produces same output."""
        counts1 = count_elements(sample_markdown)
        counts2 = count_elements(sample_markdown)
        counts3 = count_elements(sample_markdown)

        assert counts1 == counts2 == counts3


# ============================================================================
# ELEMENT_COUNTS TO_SUMMARY TESTS
# ============================================================================


class TestElementCountsSummary:
    """Test ElementCounts.to_summary formatting."""

    def test_empty_counts_summary(self):
        """Empty counts produce standard message."""
        counts = ElementCounts()
        summary = counts.to_summary()
        assert "No special elements detected" in summary

    def test_tables_summary(self):
        """Tables are formatted with breakdown."""
        counts = ElementCounts(tables=3, status_tables=1, graded_tables=1)
        summary = counts.to_summary()
        assert "3 tables" in summary
        assert "1 StatusTable" in summary
        assert "1 GradedTable" in summary
        assert "1 standard" in summary

    def test_findings_summary(self):
        """Findings use FindingCards label."""
        counts = ElementCounts(findings=2)
        summary = counts.to_summary()
        assert "2 FindingCards" in summary

    def test_method_blocks_summary(self):
        """Method blocks are labeled correctly."""
        counts = ElementCounts(code_blocks=3, method_blocks=2)
        summary = counts.to_summary()
        assert "3 code blocks" in summary
        assert "2 MethodBlock" in summary

    def test_deterministic_format(self):
        """Same counts always produce same summary."""
        counts = ElementCounts(tables=2, findings=1, callouts=1)
        summary1 = counts.to_summary()
        summary2 = counts.to_summary()
        assert summary1 == summary2
