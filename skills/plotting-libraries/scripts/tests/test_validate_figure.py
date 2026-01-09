"""Tests for figure validation utilities."""

import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validate_figure import (  # noqa: E402
    FigureValidation,
    validate_figure,
    validate_figure_for_journal,
)


class TestFigureValidation:
    """Tests for FigureValidation dataclass."""

    def test_valid_result_is_truthy(self):
        """Valid result should be truthy."""
        result = FigureValidation(valid=True)
        assert result
        assert bool(result) is True

    def test_invalid_result_is_falsy(self):
        """Invalid result should be falsy."""
        result = FigureValidation(valid=False)
        assert not result


class TestValidateFigure:
    """Tests for validate_figure function."""

    def test_nonexistent_file_fails(self):
        """Non-existent file should fail validation."""
        result = validate_figure("/nonexistent/path/figure.pdf")
        assert not result.valid
        assert result.checks["file_exists"] is False
        assert "not found" in result.details.get("error", "").lower()

    def test_valid_format_detection(self):
        """Valid formats should be recognized."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"fake pdf content")
            f.flush()
            result = validate_figure(f.name)
            assert result.checks["valid_format"] is True
            assert result.details["format"] == ".pdf"
            Path(f.name).unlink()

    def test_invalid_format_detection(self):
        """Invalid formats should fail."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"some content")
            f.flush()
            result = validate_figure(f.name)
            assert result.checks["valid_format"] is False
            Path(f.name).unlink()

    def test_file_size_check(self):
        """File size should be checked."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"small pdf")
            f.flush()
            result = validate_figure(f.name)
            assert "file_size_mb" in result.details
            Path(f.name).unlink()

    def test_empty_file_warning(self):
        """Very small file should generate warning."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"x")  # 1 byte
            f.flush()
            result = validate_figure(f.name)
            # File too small
            assert result.checks.get("reasonable_size") is False or "size_warning" in result.details
            Path(f.name).unlink()

    def test_target_journal_adds_details(self):
        """Target journal should add journal-specific details."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"fake pdf content " * 100)  # Make it bigger
            f.flush()
            result = validate_figure(f.name, target_journal="nature")
            assert result.details.get("target_journal") == "nature"
            assert "required_dpi" in result.details
            assert "preferred_format" in result.details
            Path(f.name).unlink()

    def test_format_matches_journal_check(self):
        """Format mismatch with journal should be flagged."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fake png content " * 100)
            f.flush()
            result = validate_figure(f.name, target_journal="nature")
            # Nature prefers PDF, this is PNG
            assert result.checks.get("format_matches_journal") is False
            Path(f.name).unlink()

    @pytest.mark.parametrize(
        "suffix,expected_valid",
        [
            (".pdf", True),
            (".png", True),
            (".svg", True),
            (".eps", True),
            (".tiff", True),
            (".tif", True),
            (".jpg", False),  # Not in valid formats
            (".gif", False),
        ],
    )
    def test_format_validation(self, suffix, expected_valid):
        """Test various format extensions."""
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(b"content " * 100)
            f.flush()
            result = validate_figure(f.name)
            assert result.checks["valid_format"] is expected_valid
            Path(f.name).unlink()


class TestValidateFigureForJournal:
    """Tests for validate_figure_for_journal function."""

    def test_nonexistent_file(self):
        """Non-existent file should fail with issue."""
        passes, issues = validate_figure_for_journal("/fake/path.pdf", "nature")
        assert not passes
        assert any("not exist" in issue.lower() for issue in issues)

    def test_format_mismatch_issue(self):
        """Format mismatch should be listed in issues."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"content " * 100)
            f.flush()
            passes, issues = validate_figure_for_journal(f.name, "nature")
            # Nature prefers PDF
            assert not passes
            assert any("format" in issue.lower() for issue in issues)
            Path(f.name).unlink()

    def test_correct_format_passes(self):
        """Correct format should have no format issues."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"content " * 100)
            f.flush()
            passes, issues = validate_figure_for_journal(f.name, "nature")
            # May have other issues, but no format issue
            format_issues = [i for i in issues if "format" in i.lower()]
            assert len(format_issues) == 0
            Path(f.name).unlink()


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_result_multiple_calls(self):
        """Same file should produce same validation results."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"content " * 100)
            f.flush()

            results = [validate_figure(f.name) for _ in range(5)]
            assert all(r.valid == results[0].valid for r in results)
            assert all(r.checks == results[0].checks for r in results)

            Path(f.name).unlink()

    def test_journal_validation_deterministic(self):
        """Journal validation should be deterministic."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"content " * 100)
            f.flush()

            results = [
                validate_figure_for_journal(f.name, "nature") for _ in range(5)
            ]
            assert all(r[0] == results[0][0] for r in results)
            assert all(r[1] == results[0][1] for r in results)

            Path(f.name).unlink()
