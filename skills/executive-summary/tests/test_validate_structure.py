#!/usr/bin/env python3
"""
Unit tests for validate_structure.py

Tests cover:
- Executive Summary header detection
- Key Findings section detection
- Recommendation section detection
- Finding count validation (3-5 required)
- Component ordering validation
- Action verb detection in recommendations
- Full structure validation pipeline
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_structure import validate_structure


# =============================================================================
# Valid document fixtures
# =============================================================================


VALID_SUMMARY = """## Executive Summary

Our analysis reveals a critical opportunity to reduce operational costs by 35%
through process automation.

**Key Findings:**

1. **Manual Processing Bottleneck:** Current manual data entry consumes 2,400
   staff hours monthly, representing $180,000 in labor costs.

2. **Error Rate Impact:** Manual processes show 12% error rate, causing $45,000
   in monthly rework costs.

3. **Automation ROI:** Implementing robotic process automation would reduce
   processing time by 85% with payback period of 8 months.

The projected annual savings of $2.1M significantly exceed implementation costs.

**Recommendation:** Approve the $450,000 automation investment by the Operations
Committee in Q2 2024.
"""

MINIMAL_VALID_SUMMARY = """## Executive Summary

Problem statement here.

**Key Findings:**
1. **Finding One:** Result one.
2. **Finding Two:** Result two.
3. **Finding Three:** Result three.

**Recommendation:** Implement the solution immediately.
"""


# =============================================================================
# Header detection tests
# =============================================================================


class TestHeaderDetection:
    """Tests for Executive Summary header detection."""

    def test_standard_header(self):
        """Detect standard ## Executive Summary header."""
        text = "## Executive Summary\n\nContent here."
        result = validate_structure(text)
        assert result.has_header is True

    def test_header_case_insensitive(self):
        """Header detection should be case-insensitive."""
        text = "## executive summary\n\nContent here."
        result = validate_structure(text)
        assert result.has_header is True

    def test_header_with_extra_spaces(self):
        """Header with extra spaces should be detected."""
        text = "##  Executive Summary\n\nContent here."
        result = validate_structure(text)
        assert result.has_header is True

    def test_missing_header(self):
        """Missing header should be flagged."""
        text = "Content without proper header.\n\n**Key Findings:**"
        result = validate_structure(text)
        assert result.has_header is False
        assert "Missing '## Executive Summary' header" in result.issues

    def test_h1_header_not_accepted(self):
        """H1 header should not be accepted (requires ##)."""
        text = "# Executive Summary\n\nContent here."
        result = validate_structure(text)
        assert result.has_header is False

    def test_h3_header_not_accepted(self):
        """H3 header should not be accepted."""
        text = "### Executive Summary\n\nContent here."
        result = validate_structure(text)
        assert result.has_header is False


# =============================================================================
# Key Findings section tests
# =============================================================================


class TestKeyFindingsDetection:
    """Tests for Key Findings section detection."""

    def test_standard_findings_header(self):
        """Detect standard **Key Findings:** header."""
        text = "**Key Findings:**\n1. Finding one."
        result = validate_structure(text)
        assert result.has_findings_section is True

    def test_findings_without_colon(self):
        """Detect **Key Findings** without colon."""
        text = "**Key Findings**\n1. Finding one."
        result = validate_structure(text)
        assert result.has_findings_section is True

    def test_findings_case_insensitive(self):
        """Findings detection should be case-insensitive."""
        text = "**key findings:**\n1. Finding one."
        result = validate_structure(text)
        assert result.has_findings_section is True

    def test_missing_findings(self):
        """Missing findings section should be flagged."""
        text = "## Executive Summary\n\nNo findings here."
        result = validate_structure(text)
        assert result.has_findings_section is False
        assert "Missing '**Key Findings:**' section" in result.issues


# =============================================================================
# Finding count tests
# =============================================================================


class TestFindingCount:
    """Tests for numbered findings detection."""

    def test_count_numbered_findings(self):
        """Count numbered findings with bold titles."""
        text = """**Key Findings:**
1. **Finding A:** Content
2. **Finding B:** Content
3. **Finding C:** Content
"""
        result = validate_structure(text)
        assert result.finding_count == 3

    def test_minimum_three_required(self):
        """Less than 3 findings should be flagged."""
        text = """**Key Findings:**
1. **Finding A:** Content
2. **Finding B:** Content
"""
        result = validate_structure(text)
        assert result.finding_count == 2
        assert "Only 2 findings (minimum 3 required)" in result.issues

    def test_maximum_five_allowed(self):
        """More than 5 findings should be flagged."""
        text = """**Key Findings:**
1. **Finding A:** Content
2. **Finding B:** Content
3. **Finding C:** Content
4. **Finding D:** Content
5. **Finding E:** Content
6. **Finding F:** Content
"""
        result = validate_structure(text)
        assert result.finding_count == 6
        assert "Too many findings (6); maximum is 5" in result.issues

    def test_exactly_five_findings_valid(self):
        """Exactly 5 findings should be valid."""
        text = """**Key Findings:**
1. **Finding A:** Content
2. **Finding B:** Content
3. **Finding C:** Content
4. **Finding D:** Content
5. **Finding E:** Content
"""
        result = validate_structure(text)
        assert result.finding_count == 5
        assert not any("findings" in issue.lower() for issue in result.issues if "minimum" in issue.lower() or "maximum" in issue.lower())

    def test_exactly_three_findings_valid(self):
        """Exactly 3 findings should be valid."""
        text = """**Key Findings:**
1. **Finding A:** Content
2. **Finding B:** Content
3. **Finding C:** Content
"""
        result = validate_structure(text)
        assert result.finding_count == 3

    def test_finding_without_colon_after_bold(self):
        """Findings without colon after bold should still be detected."""
        text = """**Key Findings:**
1. **Finding A** Content here
2. **Finding B** More content
3. **Finding C** Even more
"""
        result = validate_structure(text)
        assert result.finding_count == 3

    def test_zero_findings(self):
        """Zero findings should be flagged."""
        text = "**Key Findings:**\nNo numbered items here."
        result = validate_structure(text)
        assert result.finding_count == 0
        assert "Only 0 findings (minimum 3 required)" in result.issues


# =============================================================================
# Recommendation section tests
# =============================================================================


class TestRecommendationDetection:
    """Tests for Recommendation section detection."""

    def test_standard_recommendation(self):
        """Detect standard **Recommendation:** header."""
        text = "**Recommendation:** Approve the project."
        result = validate_structure(text)
        assert result.has_recommendation is True

    def test_recommendation_without_colon(self):
        """Detect **Recommendation** without colon."""
        text = "**Recommendation** Approve the project."
        result = validate_structure(text)
        assert result.has_recommendation is True

    def test_recommendation_case_insensitive(self):
        """Recommendation detection should be case-insensitive."""
        text = "**RECOMMENDATION:** Approve the project."
        result = validate_structure(text)
        assert result.has_recommendation is True

    def test_missing_recommendation(self):
        """Missing recommendation should be flagged."""
        text = "## Executive Summary\n\n**Key Findings:**\n1. **A:** B"
        result = validate_structure(text)
        assert result.has_recommendation is False
        assert "Missing '**Recommendation:**' section" in result.issues


# =============================================================================
# Action verb tests
# =============================================================================


class TestActionVerbDetection:
    """Tests for action verb detection in recommendations."""

    def test_approve_verb(self):
        """Detect 'approve' action verb."""
        text = "**Recommendation:** Approve the budget allocation."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_implement_verb(self):
        """Detect 'implement' action verb."""
        text = "**Recommendation:** Implement the new system by Q3."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_proceed_verb(self):
        """Detect 'proceed' action verb."""
        text = "**Recommendation:** Proceed with Phase 2."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_launch_verb(self):
        """Detect 'launch' action verb."""
        text = "**Recommendation:** Launch the pilot program."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_create_verb(self):
        """Detect 'create' action verb."""
        text = "**Recommendation:** Create a task force."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_develop_verb(self):
        """Detect 'develop' action verb."""
        text = "**Recommendation:** Develop a comprehensive plan."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_hire_verb(self):
        """Detect 'hire' action verb."""
        text = "**Recommendation:** Hire two additional analysts."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_invest_verb(self):
        """Detect 'invest' action verb."""
        text = "**Recommendation:** Invest $1M in infrastructure."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_authorize_verb(self):
        """Detect 'authorize' action verb."""
        text = "**Recommendation:** Authorize the expansion project."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_initiate_verb(self):
        """Detect 'initiate' action verb."""
        text = "**Recommendation:** Initiate the review process."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues

    def test_missing_action_verb(self):
        """Missing action verb should be flagged."""
        text = "**Recommendation:** The team should consider options carefully."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" in result.issues

    def test_action_verb_case_insensitive(self):
        """Action verb detection should be case-insensitive."""
        text = "**Recommendation:** APPROVE the proposal."
        result = validate_structure(text)
        assert "Recommendation lacks action verb" not in result.issues


# =============================================================================
# Component ordering tests
# =============================================================================


class TestComponentOrdering:
    """Tests for component ordering validation."""

    def test_correct_order(self):
        """Findings before Recommendation should be valid."""
        text = """## Executive Summary
**Key Findings:**
1. **A:** B
2. **C:** D
3. **E:** F
**Recommendation:** Approve the project.
"""
        result = validate_structure(text)
        assert "Findings section should come before Recommendation" not in result.issues

    def test_incorrect_order(self):
        """Recommendation before Findings should be flagged."""
        text = """## Executive Summary
**Recommendation:** Approve the project.
**Key Findings:**
1. **A:** B
2. **C:** D
3. **E:** F
"""
        result = validate_structure(text)
        assert "Findings section should come before Recommendation" in result.issues


# =============================================================================
# Full validation tests
# =============================================================================


class TestFullValidation:
    """Integration tests for full structure validation."""

    def test_valid_summary(self):
        """Valid summary should pass all checks."""
        result = validate_structure(VALID_SUMMARY)
        assert result.valid is True
        assert result.has_header is True
        assert result.has_findings_section is True
        assert result.has_recommendation is True
        assert 3 <= result.finding_count <= 5
        assert len(result.issues) == 0

    def test_minimal_valid_summary(self):
        """Minimal valid summary should pass."""
        result = validate_structure(MINIMAL_VALID_SUMMARY)
        assert result.valid is True
        assert len(result.issues) == 0

    def test_multiple_issues(self):
        """Document with multiple issues should report all of them."""
        text = """# Wrong Header Level

Some content without findings section.

**Recommendation:** Consider the options.
"""
        result = validate_structure(text)
        assert result.valid is False
        assert len(result.issues) >= 3  # Missing header, findings, finding count, action verb

    def test_result_dataclass_fields(self):
        """StructureResult should have all expected fields."""
        result = validate_structure(VALID_SUMMARY)
        assert hasattr(result, "valid")
        assert hasattr(result, "has_header")
        assert hasattr(result, "has_findings_section")
        assert hasattr(result, "has_recommendation")
        assert hasattr(result, "finding_count")
        assert hasattr(result, "issues")


# =============================================================================
# Edge cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_document(self):
        """Empty document should fail gracefully."""
        result = validate_structure("")
        assert result.valid is False
        assert result.has_header is False
        assert result.has_findings_section is False
        assert result.has_recommendation is False

    def test_only_header(self):
        """Document with only header should fail."""
        result = validate_structure("## Executive Summary")
        assert result.valid is False
        assert result.has_header is True

    def test_unicode_content(self):
        """Handle unicode content."""
        text = """## Executive Summary

Analysis of caf\u00e9 operations shows significant improvement.

**Key Findings:**
1. **Revenue Growth:** Increased 25%
2. **Customer Satisfaction:** Up 30%
3. **Cost Reduction:** Down 15%

**Recommendation:** Approve expansion to new locations.
"""
        result = validate_structure(text)
        assert result.valid is True

    def test_multiline_recommendation(self):
        """Recommendation spanning multiple lines should be handled."""
        text = """## Executive Summary

**Key Findings:**
1. **A:** B
2. **C:** D
3. **E:** F

**Recommendation:** Approve the comprehensive modernization initiative,
including infrastructure upgrades and staff training, to be completed
by the Technology Committee in Q3 2024.
"""
        result = validate_structure(text)
        assert result.has_recommendation is True
        assert "Recommendation lacks action verb" not in result.issues

    def test_findings_with_sublists(self):
        """Findings with sublists should count correctly."""
        text = """**Key Findings:**
1. **Finding A:** Main point
   - Sub point 1
   - Sub point 2
2. **Finding B:** Another point
3. **Finding C:** Final point
"""
        result = validate_structure(text)
        assert result.finding_count == 3

    def test_recommendation_at_end_of_file(self):
        """Recommendation at very end of file (no trailing newline)."""
        text = "## Executive Summary\n\n**Key Findings:**\n1. **A:** B\n2. **C:** D\n3. **E:** F\n\n**Recommendation:** Implement immediately."
        result = validate_structure(text)
        assert result.has_recommendation is True
        assert "Recommendation lacks action verb" not in result.issues


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
