"""
Tests for validate_brand.py

Validates the main brand validation script including structure, tokens,
adapter API, and SKILL.md validation.
"""

import json
import sys
from pathlib import Path

import pytest

# Add validation module to path for imports
validation_dir = Path(__file__).parent.parent / "validation"
sys.path.insert(0, str(validation_dir))

from validate_brand import (
    Severity,
    ValidationIssue,
    ValidationReport,
    validate_structure,
    validate_tokens,
    validate_adapter_api,
    validate_skill_md,
    validate_brand,
    HEX_COLOR_PATTERN,
    REQUIRED_STRUCTURE,
    REQUIRED_FRONTMATTER,
    RECOMMENDED_FRONTMATTER,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_brand_dir(tmp_path):
    """Create a minimal valid brand directory structure."""
    # Create required directories
    (tmp_path / "tokens").mkdir()
    (tmp_path / "adapters").mkdir()

    # Create minimal valid tokens file
    tokens = {
        "meta": {"name": "Test Brand", "version": "1.0.0"},
        "colors": {
            "primary": {"brand_color": {"hex": "#FF0000"}},
            "neutrals": {"gray": {"hex": "#888888"}},
            "structure": {
                "white": {"hex": "#FFFFFF"},
                "black": {"hex": "#000000"}
            }
        },
        "color_cycles": {
            "default": {"colors": ["#FF0000", "#00FF00", "#0000FF"]}
        }
    }
    with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
        json.dump(tokens, f)

    # Create minimal SKILL.md
    skill_md = """---
name: test-brand
version: 1.0.0
description: Test brand for unit tests
---

# Test Brand Skill

<overview>
Test brand for validation testing.
</overview>
"""
    (tmp_path / "SKILL.md").write_text(skill_md)

    # Create minimal adapter
    adapter_code = '''
"""Test adapter."""
BRAND_COLORS = {"primary": "#FF0000"}

def set_brand_style(cycle="default"):
    pass

def get_cycle(name):
    return ["#FF0000"]

def get_color(name):
    return "#FF0000"
'''
    (tmp_path / "adapters" / "matplotlib_adapter.py").write_text(adapter_code)

    return tmp_path


@pytest.fixture
def empty_report():
    """Create an empty validation report."""
    return ValidationReport(brand_name="test", brand_path="/test")


# =============================================================================
# SEVERITY ENUM
# =============================================================================


class TestSeverity:
    """Test Severity enum."""

    def test_all_severities_exist(self):
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"


# =============================================================================
# VALIDATION ISSUE
# =============================================================================


class TestValidationIssue:
    """Test ValidationIssue dataclass."""

    def test_basic_creation(self):
        issue = ValidationIssue(
            severity=Severity.ERROR,
            category="test",
            message="Test error"
        )
        assert issue.severity == Severity.ERROR
        assert issue.category == "test"
        assert issue.message == "Test error"
        assert issue.path is None
        assert issue.suggestion is None

    def test_with_all_fields(self):
        issue = ValidationIssue(
            severity=Severity.WARNING,
            category="tokens",
            message="Missing field",
            path="/path/to/file",
            suggestion="Add the field"
        )
        assert issue.path == "/path/to/file"
        assert issue.suggestion == "Add the field"

    def test_to_dict(self):
        issue = ValidationIssue(
            severity=Severity.ERROR,
            category="test",
            message="Test error",
            path="/test/path",
            suggestion="Fix it"
        )
        d = issue.to_dict()
        assert d["severity"] == "error"
        assert d["category"] == "test"
        assert d["message"] == "Test error"
        assert d["path"] == "/test/path"
        assert d["suggestion"] == "Fix it"


# =============================================================================
# VALIDATION REPORT
# =============================================================================


class TestValidationReport:
    """Test ValidationReport dataclass."""

    def test_basic_creation(self):
        report = ValidationReport(
            brand_name="test-brand",
            brand_path="/path/to/brand"
        )
        assert report.brand_name == "test-brand"
        assert report.valid is True
        assert report.issues == []

    def test_add_error_marks_invalid(self):
        report = ValidationReport(brand_name="test", brand_path="/test")
        report.add_issue(ValidationIssue(
            severity=Severity.ERROR,
            category="test",
            message="Error"
        ))
        assert report.valid is False

    def test_add_warning_keeps_valid(self):
        report = ValidationReport(brand_name="test", brand_path="/test")
        report.add_issue(ValidationIssue(
            severity=Severity.WARNING,
            category="test",
            message="Warning"
        ))
        assert report.valid is True

    def test_add_info_keeps_valid(self):
        report = ValidationReport(brand_name="test", brand_path="/test")
        report.add_issue(ValidationIssue(
            severity=Severity.INFO,
            category="test",
            message="Info"
        ))
        assert report.valid is True

    def test_to_dict(self):
        report = ValidationReport(brand_name="test", brand_path="/test")
        report.add_issue(ValidationIssue(
            severity=Severity.ERROR,
            category="test",
            message="Error"
        ))
        d = report.to_dict()
        assert d["brand_name"] == "test"
        assert d["valid"] is False
        assert d["error_count"] == 1
        assert d["warning_count"] == 0
        assert len(d["issues"]) == 1

    def test_to_json(self):
        report = ValidationReport(brand_name="test", brand_path="/test")
        json_str = report.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["brand_name"] == "test"


# =============================================================================
# HEX COLOR PATTERN
# =============================================================================


class TestHexColorPattern:
    """Test hex color regex pattern."""

    def test_valid_uppercase(self):
        assert HEX_COLOR_PATTERN.match("#FF0000")
        assert HEX_COLOR_PATTERN.match("#AABBCC")

    def test_valid_lowercase(self):
        assert HEX_COLOR_PATTERN.match("#ff0000")
        assert HEX_COLOR_PATTERN.match("#aabbcc")

    def test_valid_mixed(self):
        assert HEX_COLOR_PATTERN.match("#AaBbCc")

    def test_invalid_short(self):
        assert not HEX_COLOR_PATTERN.match("#FFF")

    def test_invalid_long(self):
        assert not HEX_COLOR_PATTERN.match("#FFFFFFFF")

    def test_invalid_no_hash(self):
        assert not HEX_COLOR_PATTERN.match("FF0000")

    def test_invalid_characters(self):
        assert not HEX_COLOR_PATTERN.match("#GGGGGG")


# =============================================================================
# STRUCTURE VALIDATION
# =============================================================================


class TestValidateStructure:
    """Test directory structure validation."""

    def test_valid_structure(self, temp_brand_dir, empty_report):
        validate_structure(temp_brand_dir, empty_report)
        assert empty_report.structure_valid is True
        errors = [i for i in empty_report.issues if i.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_missing_tokens_dir(self, tmp_path, empty_report):
        (tmp_path / "adapters").mkdir()
        (tmp_path / "SKILL.md").touch()
        validate_structure(tmp_path, empty_report)
        assert empty_report.structure_valid is False

    def test_missing_adapters_dir(self, tmp_path, empty_report):
        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "brand-tokens.json").touch()
        (tmp_path / "SKILL.md").touch()
        validate_structure(tmp_path, empty_report)
        assert empty_report.structure_valid is False

    def test_missing_skill_md(self, tmp_path, empty_report):
        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "brand-tokens.json").touch()
        (tmp_path / "adapters").mkdir()
        (tmp_path / "adapters" / "test_adapter.py").touch()
        validate_structure(tmp_path, empty_report)
        assert empty_report.structure_valid is False

    def test_no_adapter_files(self, tmp_path, empty_report):
        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "brand-tokens.json").touch()
        (tmp_path / "adapters").mkdir()  # Empty adapters dir
        (tmp_path / "SKILL.md").touch()
        validate_structure(tmp_path, empty_report)
        assert empty_report.structure_valid is False


# =============================================================================
# TOKENS VALIDATION
# =============================================================================


class TestValidateTokens:
    """Test brand tokens validation."""

    def test_valid_tokens(self, temp_brand_dir, empty_report):
        tokens = validate_tokens(temp_brand_dir, empty_report)
        assert tokens is not None
        assert empty_report.tokens_valid is True

    def test_missing_tokens_file(self, tmp_path, empty_report):
        (tmp_path / "tokens").mkdir()
        tokens = validate_tokens(tmp_path, empty_report)
        assert tokens is None
        assert empty_report.tokens_valid is False

    def test_invalid_json(self, tmp_path, empty_report):
        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "brand-tokens.json").write_text("{invalid json")
        tokens = validate_tokens(tmp_path, empty_report)
        assert tokens is None
        assert empty_report.tokens_valid is False

    def test_missing_meta(self, tmp_path, empty_report):
        (tmp_path / "tokens").mkdir()
        tokens_data = {
            "colors": {"primary": {}},
            "color_cycles": {"default": {"colors": ["#FF0000"]}}
        }
        with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
            json.dump(tokens_data, f)
        validate_tokens(tmp_path, empty_report)
        # Should have error for missing meta
        errors = [i for i in empty_report.issues
                  if i.severity == Severity.ERROR and "meta" in i.message.lower()]
        assert len(errors) > 0

    def test_missing_colors(self, tmp_path, empty_report):
        (tmp_path / "tokens").mkdir()
        tokens_data = {
            "meta": {"name": "test", "version": "1.0"},
            "color_cycles": {"default": {"colors": ["#FF0000"]}}
        }
        with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
            json.dump(tokens_data, f)
        validate_tokens(tmp_path, empty_report)
        errors = [i for i in empty_report.issues
                  if i.severity == Severity.ERROR and "colors" in i.message.lower()]
        assert len(errors) > 0

    def test_invalid_hex_color(self, tmp_path, empty_report):
        (tmp_path / "tokens").mkdir()
        tokens_data = {
            "meta": {"name": "test", "version": "1.0"},
            "colors": {
                "primary": {"bad": {"hex": "invalid"}},
                "neutrals": {},
                "structure": {}
            },
            "color_cycles": {"default": {"colors": ["#FF0000"]}}
        }
        with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
            json.dump(tokens_data, f)
        validate_tokens(tmp_path, empty_report)
        errors = [i for i in empty_report.issues
                  if i.severity == Severity.ERROR and "hex" in i.message.lower()]
        assert len(errors) > 0


# =============================================================================
# ADAPTER API VALIDATION
# =============================================================================


class TestValidateAdapterApi:
    """Test Python adapter API validation."""

    def test_valid_adapter(self, temp_brand_dir, empty_report):
        validate_adapter_api(temp_brand_dir, empty_report)
        assert empty_report.adapter_api_valid is True

    def test_missing_brand_colors(self, tmp_path, empty_report):
        (tmp_path / "adapters").mkdir()
        adapter = '''
def set_brand_style(cycle="default"):
    pass
def get_cycle(name):
    return []
def get_color(name):
    return "#000000"
'''
        (tmp_path / "adapters" / "matplotlib_adapter.py").write_text(adapter)
        validate_adapter_api(tmp_path, empty_report)
        assert empty_report.adapter_api_valid is False

    def test_missing_set_brand_style(self, tmp_path, empty_report):
        (tmp_path / "adapters").mkdir()
        adapter = '''
BRAND_COLORS = {}
def get_cycle(name):
    return []
def get_color(name):
    return "#000000"
'''
        (tmp_path / "adapters" / "matplotlib_adapter.py").write_text(adapter)
        validate_adapter_api(tmp_path, empty_report)
        assert empty_report.adapter_api_valid is False

    def test_missing_get_cycle(self, tmp_path, empty_report):
        (tmp_path / "adapters").mkdir()
        adapter = '''
BRAND_COLORS = {}
def set_brand_style(cycle="default"):
    pass
def get_color(name):
    return "#000000"
'''
        (tmp_path / "adapters" / "matplotlib_adapter.py").write_text(adapter)
        validate_adapter_api(tmp_path, empty_report)
        assert empty_report.adapter_api_valid is False

    def test_syntax_error_in_adapter(self, tmp_path, empty_report):
        (tmp_path / "adapters").mkdir()
        adapter = '''
def broken_syntax(
'''
        (tmp_path / "adapters" / "matplotlib_adapter.py").write_text(adapter)
        validate_adapter_api(tmp_path, empty_report)
        assert empty_report.adapter_api_valid is False

    def test_no_matplotlib_adapter_warning(self, tmp_path, empty_report):
        (tmp_path / "adapters").mkdir()
        # Create a different adapter
        (tmp_path / "adapters" / "other_adapter.py").write_text("# other")
        validate_adapter_api(tmp_path, empty_report)
        # Should have info message about no matplotlib adapter
        infos = [i for i in empty_report.issues if i.severity == Severity.INFO]
        assert len(infos) > 0


# =============================================================================
# SKILL.MD VALIDATION
# =============================================================================


class TestValidateSkillMd:
    """Test SKILL.md frontmatter and structure validation."""

    def test_valid_skill_md(self, temp_brand_dir, empty_report):
        validate_skill_md(temp_brand_dir, empty_report)
        assert empty_report.skill_md_valid is True

    def test_missing_skill_md(self, tmp_path, empty_report):
        validate_skill_md(tmp_path, empty_report)
        assert empty_report.skill_md_valid is False

    def test_missing_frontmatter(self, tmp_path, empty_report):
        skill_md = "# Brand Skill\n\nNo frontmatter here."
        (tmp_path / "SKILL.md").write_text(skill_md)
        validate_skill_md(tmp_path, empty_report)
        assert empty_report.skill_md_valid is False

    def test_missing_required_frontmatter(self, tmp_path, empty_report):
        skill_md = """---
version: 1.0.0
---
# Brand
"""
        (tmp_path / "SKILL.md").write_text(skill_md)
        validate_skill_md(tmp_path, empty_report)
        # Missing 'name' and 'description'
        errors = [i for i in empty_report.issues if i.severity == Severity.ERROR]
        assert len(errors) >= 1

    def test_missing_recommended_frontmatter_warning(self, tmp_path, empty_report):
        skill_md = """---
name: test-brand
version: 1.0.0
description: Test brand
---
# Brand
"""
        (tmp_path / "SKILL.md").write_text(skill_md)
        validate_skill_md(tmp_path, empty_report)
        # Should have warnings for missing recommended fields
        warnings = [i for i in empty_report.issues if i.severity == Severity.WARNING]
        assert len(warnings) >= 1  # brand-type, tokens-file, etc.


# =============================================================================
# FULL VALIDATION
# =============================================================================


class TestValidateBrand:
    """Test complete brand validation."""

    def test_valid_brand(self, temp_brand_dir):
        report = validate_brand(temp_brand_dir)
        assert report.valid is True
        assert report.structure_valid is True
        assert report.tokens_valid is True
        assert report.adapter_api_valid is True
        assert report.skill_md_valid is True

    def test_nonexistent_path(self):
        report = validate_brand(Path("/nonexistent/path"))
        assert report.valid is False
        errors = [i for i in report.issues if i.severity == Severity.ERROR]
        assert len(errors) > 0

    def test_brand_name_from_path(self, temp_brand_dir):
        report = validate_brand(temp_brand_dir)
        assert report.brand_name == temp_brand_dir.name

    def test_summary_populated(self, temp_brand_dir):
        report = validate_brand(temp_brand_dir)
        # Summary should contain adapter info
        assert "adapters_found" in report.summary or "matplotlib_adapter" in report.summary


# =============================================================================
# CONSTANTS
# =============================================================================


class TestConstants:
    """Test module constants."""

    def test_required_structure(self):
        assert "SKILL.md" in REQUIRED_STRUCTURE
        assert "tokens" in REQUIRED_STRUCTURE
        assert "adapters" in REQUIRED_STRUCTURE

    def test_required_frontmatter(self):
        assert "name" in REQUIRED_FRONTMATTER
        assert "version" in REQUIRED_FRONTMATTER
        assert "description" in REQUIRED_FRONTMATTER

    def test_recommended_frontmatter(self):
        assert "brand-type" in RECOMMENDED_FRONTMATTER


# =============================================================================
# VOCABULARY VALIDATION
# =============================================================================


class TestVocabularyValidation:
    """Test vocabulary-based validation for roles, cycles, and free text."""

    def test_nonstandard_role_warning(self, tmp_path, empty_report):
        """Non-standard roles should generate warnings."""
        (tmp_path / "tokens").mkdir()
        tokens_data = {
            "meta": {"name": "test", "version": "1.0"},
            "colors": {
                "primary": {"color1": {"hex": "#FF0000", "role": "completely unknown role"}},
                "neutrals": {},
                "structure": {}
            },
            "color_cycles": {"default": {"colors": ["#FF0000"]}}
        }
        with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
            json.dump(tokens_data, f)
        validate_tokens(tmp_path, empty_report)
        warnings = [i for i in empty_report.issues
                    if i.severity == Severity.WARNING and i.category == "vocabulary"]
        assert len(warnings) >= 1

    def test_normalizable_role_info(self, tmp_path, empty_report):
        """Normalizable roles should generate info messages."""
        (tmp_path / "tokens").mkdir()
        tokens_data = {
            "meta": {"name": "test", "version": "1.0"},
            "colors": {
                "primary": {"color1": {"hex": "#FF0000", "role": "hero highlight"}},
                "neutrals": {},
                "structure": {}
            },
            "color_cycles": {"default": {"colors": ["#FF0000"]}}
        }
        with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
            json.dump(tokens_data, f)
        validate_tokens(tmp_path, empty_report)
        # Should have info suggesting normalization
        infos = [i for i in empty_report.issues
                 if i.severity == Severity.INFO and "normalized" in i.message.lower()]
        assert len(infos) >= 1

    def test_missing_required_cycle_warning(self, tmp_path, empty_report):
        """Missing 'default' cycle should generate warning."""
        (tmp_path / "tokens").mkdir()
        tokens_data = {
            "meta": {"name": "test", "version": "1.0"},
            "colors": {
                "primary": {},
                "neutrals": {},
                "structure": {}
            },
            "color_cycles": {"custom_cycle": {"colors": ["#FF0000"]}}
        }
        with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
            json.dump(tokens_data, f)
        validate_tokens(tmp_path, empty_report)
        warnings = [i for i in empty_report.issues
                    if i.severity == Severity.WARNING and "default" in i.message.lower()]
        assert len(warnings) >= 1

    def test_custom_cycle_name_flagged(self, tmp_path, empty_report):
        """Custom cycle names should be flagged with info."""
        (tmp_path / "tokens").mkdir()
        tokens_data = {
            "meta": {"name": "test", "version": "1.0"},
            "colors": {
                "primary": {},
                "neutrals": {},
                "structure": {}
            },
            "color_cycles": {
                "default": {"colors": ["#FF0000"]},
                "my_very_custom_cycle": {"colors": ["#00FF00"]}
            }
        }
        with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
            json.dump(tokens_data, f)
        validate_tokens(tmp_path, empty_report)
        infos = [i for i in empty_report.issues
                 if i.severity == Severity.INFO and "custom" in i.message.lower()]
        assert len(infos) >= 1

    def test_long_guideline_flagged(self, tmp_path, empty_report):
        """Long philosophy guidelines should be flagged."""
        (tmp_path / "tokens").mkdir()
        long_guideline = "x" * 250  # Longer than 200 chars
        tokens_data = {
            "meta": {"name": "test", "version": "1.0"},
            "colors": {
                "primary": {},
                "neutrals": {},
                "structure": {}
            },
            "color_cycles": {"default": {"colors": ["#FF0000"]}},
            "philosophy": {
                "guidelines": [long_guideline]
            }
        }
        with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
            json.dump(tokens_data, f)
        validate_tokens(tmp_path, empty_report)
        infos = [i for i in empty_report.issues
                 if i.severity == Severity.INFO and "long guideline" in i.message.lower()]
        assert len(infos) >= 1

    def test_vague_checklist_term_flagged(self, tmp_path, empty_report):
        """Vague terms in preflight checklist should be flagged."""
        (tmp_path / "tokens").mkdir()
        tokens_data = {
            "meta": {"name": "test", "version": "1.0"},
            "colors": {
                "primary": {},
                "neutrals": {},
                "structure": {}
            },
            "color_cycles": {"default": {"colors": ["#FF0000"]}},
            "preflight_checklist": [
                "Check colors if needed",  # Contains vague term
                "Verify font size"  # OK
            ]
        }
        with open(tmp_path / "tokens" / "brand-tokens.json", "w") as f:
            json.dump(tokens_data, f)
        validate_tokens(tmp_path, empty_report)
        infos = [i for i in empty_report.issues
                 if i.severity == Severity.INFO and "vague" in i.message.lower()]
        assert len(infos) >= 1


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestValidationIntegration:
    """Integration tests for complete validation workflows."""

    def test_report_json_serializable(self, temp_brand_dir):
        """Ensure report can be serialized to JSON."""
        report = validate_brand(temp_brand_dir)
        json_str = report.to_json()
        parsed = json.loads(json_str)
        assert parsed["brand_name"] == temp_brand_dir.name

    def test_multiple_issues_tracked(self, tmp_path):
        """Multiple validation failures should all be tracked."""
        # Create a brand with multiple issues
        (tmp_path / "SKILL.md").write_text("# No frontmatter")
        # Missing tokens, adapters directories

        report = validate_brand(tmp_path)
        assert report.valid is False
        assert len(report.issues) >= 2  # At least structure and SKILL.md issues

    def test_issue_categories(self, tmp_path):
        """Issues should be properly categorized."""
        (tmp_path / "tokens").mkdir()
        (tmp_path / "adapters").mkdir()
        (tmp_path / "adapters" / "test_adapter.py").touch()
        (tmp_path / "SKILL.md").write_text("no frontmatter")

        report = validate_brand(tmp_path)
        categories = {i.category for i in report.issues}
        # Should have multiple categories
        assert len(categories) >= 1
