"""Tests for evidence_strength.py — theme-level evidence strength rating."""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evidence_strength import (
    StrengthRating,
    rate_theme,
    rate_themes,
)
from thresholds import STRONG_MIN_SOURCES, MODERATE_MIN_SOURCES


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def strong_theme():
    """A theme that should rate Strong."""
    return {
        "name": "AMPK-mediated autophagy",
        "source_count": 5,
        "tier_distribution": {"T1": 2, "T2": 2, "T3": 1, "T4": 0},
        "has_contradictions": False,
        "contradictions_resolved": False,
        "all_sources_recent": False,
        "consistent_direction": True,
    }


@pytest.fixture
def moderate_theme():
    """A theme that should rate Moderate."""
    return {
        "name": "mTOR pathway regulation",
        "source_count": 3,
        "tier_distribution": {"T1": 0, "T2": 1, "T3": 2, "T4": 0},
        "has_contradictions": False,
        "contradictions_resolved": False,
        "all_sources_recent": False,
        "consistent_direction": True,
    }


@pytest.fixture
def emerging_theme():
    """A theme that should rate Emerging."""
    return {
        "name": "Novel ferroptosis pathway",
        "source_count": 2,
        "tier_distribution": {"T1": 0, "T2": 0, "T3": 2, "T4": 0},
        "has_contradictions": False,
        "contradictions_resolved": False,
        "all_sources_recent": True,
        "consistent_direction": True,
    }


@pytest.fixture
def weak_theme():
    """A theme that should rate Weak."""
    return {
        "name": "Speculative mechanism",
        "source_count": 1,
        "tier_distribution": {"T1": 0, "T2": 0, "T3": 0, "T4": 1},
        "has_contradictions": False,
        "contradictions_resolved": False,
        "all_sources_recent": False,
        "consistent_direction": True,
    }


# =============================================================================
# Strong Rating Tests
# =============================================================================


class TestStrongRating:
    def test_classic_strong(self, strong_theme):
        """Classic strong evidence rates Strong."""
        result = rate_theme(strong_theme)
        assert result.rating == "Strong"

    def test_strong_with_t1_only(self):
        """≥3 sources with ≥1 T1 and consistent → Strong."""
        theme = {
            "name": "test",
            "source_count": 3,
            "tier_distribution": {"T1": 1, "T2": 0, "T3": 2, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Strong"

    def test_strong_with_t2_only(self):
        """≥3 sources with ≥2 T2 and consistent → Strong."""
        theme = {
            "name": "test",
            "source_count": 4,
            "tier_distribution": {"T1": 0, "T2": 2, "T3": 2, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Strong"

    def test_strong_with_resolved_contradictions(self):
        """Strong evidence with resolved contradictions still rates Strong."""
        theme = {
            "name": "test",
            "source_count": 4,
            "tier_distribution": {"T1": 2, "T2": 2, "T3": 0, "T4": 0},
            "has_contradictions": True,
            "contradictions_resolved": True,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Strong"

    def test_not_strong_with_unresolved_contradictions(self, strong_theme):
        """Unresolved contradictions prevent Strong rating."""
        strong_theme["has_contradictions"] = True
        strong_theme["contradictions_resolved"] = False
        result = rate_theme(strong_theme)
        assert result.rating != "Strong"

    def test_not_strong_with_inconsistent_direction(self, strong_theme):
        """Inconsistent direction prevents Strong rating."""
        strong_theme["consistent_direction"] = False
        result = rate_theme(strong_theme)
        assert result.rating != "Strong"

    def test_not_strong_with_insufficient_sources(self):
        """<3 sources prevents Strong even with T1 evidence."""
        theme = {
            "name": "test",
            "source_count": 2,
            "tier_distribution": {"T1": 2, "T2": 0, "T3": 0, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating != "Strong"

    def test_not_strong_with_only_one_t2(self):
        """Only 1 T2 (no T1) → not Strong (needs ≥2 T2)."""
        theme = {
            "name": "test",
            "source_count": 3,
            "tier_distribution": {"T1": 0, "T2": 1, "T3": 2, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating != "Strong"


# =============================================================================
# Moderate Rating Tests
# =============================================================================


class TestModerateRating:
    def test_classic_moderate(self, moderate_theme):
        """Classic moderate evidence rates Moderate."""
        result = rate_theme(moderate_theme)
        assert result.rating == "Moderate"

    def test_moderate_with_one_t2(self):
        """≥2 sources with 1 T2, no contradictions → Moderate."""
        theme = {
            "name": "test",
            "source_count": 2,
            "tier_distribution": {"T1": 0, "T2": 1, "T3": 1, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Moderate"

    def test_moderate_with_one_t1(self):
        """≥2 sources with 1 T1 qualifies for Moderate (if not Strong).

        Note: The implementation relaxes the spec from "≥1 T2" to "≥1 T2 or ≥1 T1"
        for Moderate rating. This is intentional — T1 evidence is stronger than T2,
        so it should also satisfy the Moderate tier requirement.
        """
        theme = {
            "name": "test",
            "source_count": 2,
            "tier_distribution": {"T1": 1, "T2": 0, "T3": 1, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Moderate"

    def test_moderate_with_resolved_contradictions(self):
        """Contradictions resolved → still Moderate."""
        theme = {
            "name": "test",
            "source_count": 3,
            "tier_distribution": {"T1": 0, "T2": 1, "T3": 2, "T4": 0},
            "has_contradictions": True,
            "contradictions_resolved": True,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Moderate"

    def test_moderate_inconsistent_direction_warning(self):
        """Moderate with inconsistent direction gets a warning."""
        theme = {
            "name": "test",
            "source_count": 3,
            "tier_distribution": {"T1": 0, "T2": 1, "T3": 2, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": False,
        }
        result = rate_theme(theme)
        assert result.rating == "Moderate"
        assert len(result.warnings) > 0

    def test_not_moderate_with_unresolved_contradictions(self):
        """Unresolved contradictions prevent Moderate."""
        theme = {
            "name": "test",
            "source_count": 3,
            "tier_distribution": {"T1": 0, "T2": 1, "T3": 2, "T4": 0},
            "has_contradictions": True,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating != "Moderate"


# =============================================================================
# Emerging Rating Tests
# =============================================================================


class TestEmergingRating:
    def test_classic_emerging(self, emerging_theme):
        """Classic emerging evidence rates Emerging."""
        result = rate_theme(emerging_theme)
        assert result.rating == "Emerging"

    def test_emerging_one_source(self):
        """1 recent source → Emerging."""
        theme = {
            "name": "test",
            "source_count": 1,
            "tier_distribution": {"T1": 0, "T2": 0, "T3": 1, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": True,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Emerging"

    def test_emerging_two_sources(self):
        """2 recent sources → Emerging."""
        theme = {
            "name": "test",
            "source_count": 2,
            "tier_distribution": {"T1": 0, "T2": 0, "T3": 2, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": True,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Emerging"

    def test_not_emerging_with_three_sources(self):
        """3 T3-only sources → Weak (not Emerging, which requires 1-2 sources)."""
        theme = {
            "name": "test",
            "source_count": 3,
            "tier_distribution": {"T1": 0, "T2": 0, "T3": 3, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": True,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Weak"

    def test_not_emerging_without_recency(self):
        """Not recent → not Emerging."""
        theme = {
            "name": "test",
            "source_count": 2,
            "tier_distribution": {"T1": 0, "T2": 0, "T3": 2, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating != "Emerging"

    def test_not_emerging_with_unresolved_contradictions(self):
        """Unresolved contradictions block Emerging → routes to Weak."""
        theme = {
            "name": "test",
            "source_count": 2,
            "tier_distribution": {"T1": 0, "T2": 0, "T3": 2, "T4": 0},
            "has_contradictions": True,
            "contradictions_resolved": False,
            "all_sources_recent": True,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Weak"


# =============================================================================
# Weak Rating Tests
# =============================================================================


class TestWeakRating:
    def test_classic_weak(self, weak_theme):
        """Classic weak evidence rates Weak."""
        result = rate_theme(weak_theme)
        assert result.rating == "Weak"

    def test_zero_sources(self):
        """0 sources → Weak."""
        theme = {
            "name": "test",
            "source_count": 0,
            "tier_distribution": {"T1": 0, "T2": 0, "T3": 0, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Weak"

    def test_t3_t4_only_weak(self):
        """Multiple T3/T4 sources only → Weak (can't reach Moderate without T2+)."""
        theme = {
            "name": "test",
            "source_count": 5,
            "tier_distribution": {"T1": 0, "T2": 0, "T3": 3, "T4": 2},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Weak"

    def test_weak_includes_rationale(self, weak_theme):
        """Weak rating includes explanatory rationale."""
        result = rate_theme(weak_theme)
        assert len(result.rationale) > 0


# =============================================================================
# Batch Rating Tests
# =============================================================================


class TestBatchRating:
    def test_rate_themes_all_levels(self, strong_theme, moderate_theme, emerging_theme, weak_theme):
        """Batch rating processes all themes and counts correctly."""
        data = {"themes": [strong_theme, moderate_theme, emerging_theme, weak_theme]}
        report = rate_themes(data)
        assert report["theme_count"] == 4
        assert report["rating_counts"]["Strong"] == 1
        assert report["rating_counts"]["Moderate"] == 1
        assert report["rating_counts"]["Emerging"] == 1
        assert report["rating_counts"]["Weak"] == 1

    def test_has_strong_flag(self, strong_theme, weak_theme):
        """has_strong flag set when Strong themes present."""
        report = rate_themes({"themes": [strong_theme, weak_theme]})
        assert report["has_strong"] is True

    def test_has_weak_flag(self, strong_theme, weak_theme):
        """has_weak flag set when Weak themes present."""
        report = rate_themes({"themes": [strong_theme, weak_theme]})
        assert report["has_weak"] is True

    def test_no_strong_flag(self, weak_theme):
        """has_strong is False when no Strong themes."""
        report = rate_themes({"themes": [weak_theme]})
        assert report["has_strong"] is False

    def test_empty_themes(self):
        """Empty themes list handled gracefully."""
        report = rate_themes({"themes": []})
        assert report["theme_count"] == 0
        assert all(v == 0 for v in report["rating_counts"].values())


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    def test_missing_fields_use_defaults(self):
        """Missing fields in theme dict use sensible defaults."""
        result = rate_theme({"name": "minimal"})
        # 0 sources → Weak
        assert result.rating == "Weak"

    def test_empty_tier_distribution(self):
        """Empty tier_distribution handled."""
        theme = {
            "name": "test",
            "source_count": 3,
            "tier_distribution": {},
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Weak"

    def test_deterministic_output(self, strong_theme):
        """Same input always produces same rating."""
        results = [rate_theme(strong_theme) for _ in range(10)]
        assert all(r.rating == "Strong" for r in results)

    def test_exactly_three_sources_strong(self):
        """Exactly 3 sources (= STRONG_MIN_SOURCES) qualifies for Strong."""
        assert STRONG_MIN_SOURCES == 3
        theme = {
            "name": "test",
            "source_count": 3,
            "tier_distribution": {"T1": 1, "T2": 1, "T3": 1, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Strong"

    def test_exactly_two_sources_moderate(self):
        """Exactly 2 sources (= MODERATE_MIN_SOURCES) qualifies for Moderate."""
        assert MODERATE_MIN_SOURCES == 2
        theme = {
            "name": "test",
            "source_count": 2,
            "tier_distribution": {"T1": 0, "T2": 1, "T3": 1, "T4": 0},
            "has_contradictions": False,
            "contradictions_resolved": False,
            "all_sources_recent": False,
            "consistent_direction": True,
        }
        result = rate_theme(theme)
        assert result.rating == "Moderate"

    def test_strength_rating_dataclass(self):
        """StrengthRating dataclass works correctly."""
        sr = StrengthRating(theme_name="test", rating="Strong")
        assert sr.theme_name == "test"
        assert sr.rationale == []
        assert sr.warnings == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
