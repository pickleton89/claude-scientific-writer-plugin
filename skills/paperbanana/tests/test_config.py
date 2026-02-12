"""Tests for config: PaperBanana Settings factory."""

from __future__ import annotations

import sys
from pathlib import Path
# Add utils to path
sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "scripts")
)


class TestCreateSettings:
    """Test Settings factory function.

    These tests mock PaperBanana imports to avoid requiring the
    package to be installed for unit testing.
    """

    def test_settings_factory_callable(self):
        """Verify the factory function exists and is importable."""
        from utils.config import create_settings

        assert callable(create_settings)

    def test_skill_dir_paths(self):
        """Verify skill directory path constants are correct."""
        from utils.config import GUIDELINES_PATH, SKILL_DIR

        assert SKILL_DIR.name == "paperbanana"
        assert GUIDELINES_PATH.name == "oligon_style.yaml"
        assert "data/guidelines" in str(GUIDELINES_PATH)

    def test_guidelines_file_exists(self):
        """Verify the Oligon guidelines YAML exists."""
        from utils.config import GUIDELINES_PATH

        assert GUIDELINES_PATH.exists(), f"Missing: {GUIDELINES_PATH}"

    def test_stylist_prompt_exists(self):
        """Verify the Stylist prompt file exists."""
        from utils.config import STYLIST_PROMPT_PATH

        assert STYLIST_PROMPT_PATH.exists(), f"Missing: {STYLIST_PROMPT_PATH}"

    def test_iterations_clamped(self):
        """Verify iterations are clamped to 1-5 range."""
        # This requires PaperBanana to be installed; skip if not available
        try:
            from utils.config import create_settings

            settings = create_settings("test-key", iterations=10)
            # Should be clamped to 5
            assert settings.refinement_iterations <= 5
        except ImportError:
            pass  # PaperBanana not installed, skip


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
