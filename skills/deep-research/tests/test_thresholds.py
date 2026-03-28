"""Tests for thresholds.py — constant consistency validation.

Ensures all modes in ALL_MODES have entries in every mode-keyed dict,
and that constants are well-formed.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from thresholds import (
    ALL_MODES,
    TIER_ORDER,
    MIN_SOURCES,
    MIN_DATABASES,
    SEARCH_SATURATION,
    RECENT_THRESHOLD,
    PEER_REVIEWED_MIN,
    WORD_COUNTS,
    SPOT_CHECK_RATES,
    CURRENCY_THRESHOLDS,
    CONVERGENCE_SIGNALS_REQUIRED,
    CONVERGENCE_SIGNALS_TOTAL,
    CONVERGENCE_STAGNATION_ROUNDS,
    CONVERGENCE_TIME_LIMIT_TURNS,
    SCOPE_STABILITY_ROUNDS,
    STRONG_MIN_SOURCES,
    MODERATE_MIN_SOURCES,
    EMERGING_MAX_AGE_YEARS,
    HYPOTHESIS_STRONG_THRESHOLD,
    HYPOTHESIS_VIABLE_THRESHOLD,
    HYPOTHESIS_MAX_SCORE,
    HYPOTHESIS_CRITERIA_COUNT,
    KAPPA_THRESHOLD,
    MANDATORY_SECTIONS_ALL,
    MANDATORY_SECTIONS_BY_MODE,
    CITATION_PATTERN,
    SECTION_SCHEMAS,
    FILE_SPECS,
)


# =============================================================================
# Mode Completeness: Every mode in ALL_MODES has entries everywhere
# =============================================================================


class TestModeCompleteness:
    def test_min_sources_covers_all_modes(self):
        """MIN_SOURCES has an entry for every mode."""
        for mode in ALL_MODES:
            assert mode in MIN_SOURCES, f"MIN_SOURCES missing {mode}"

    def test_min_databases_covers_all_modes(self):
        """MIN_DATABASES has an entry for every mode."""
        for mode in ALL_MODES:
            assert mode in MIN_DATABASES, f"MIN_DATABASES missing {mode}"

    def test_search_saturation_covers_all_modes(self):
        """SEARCH_SATURATION has an entry for every mode."""
        for mode in ALL_MODES:
            assert mode in SEARCH_SATURATION, f"SEARCH_SATURATION missing {mode}"

    def test_recent_threshold_covers_all_modes(self):
        """RECENT_THRESHOLD has an entry for every mode."""
        for mode in ALL_MODES:
            assert mode in RECENT_THRESHOLD, f"RECENT_THRESHOLD missing {mode}"

    def test_peer_reviewed_min_covers_all_modes(self):
        """PEER_REVIEWED_MIN has an entry for every mode."""
        for mode in ALL_MODES:
            assert mode in PEER_REVIEWED_MIN, f"PEER_REVIEWED_MIN missing {mode}"

    def test_word_counts_covers_all_modes(self):
        """WORD_COUNTS has an entry for every mode."""
        for mode in ALL_MODES:
            assert mode in WORD_COUNTS, f"WORD_COUNTS missing {mode}"

    def test_spot_check_rates_covers_all_modes(self):
        """SPOT_CHECK_RATES has an entry for every mode."""
        for mode in ALL_MODES:
            assert mode in SPOT_CHECK_RATES, f"SPOT_CHECK_RATES missing {mode}"

    def test_mandatory_sections_by_mode_covers_all_modes(self):
        """MANDATORY_SECTIONS_BY_MODE has an entry for every mode."""
        for mode in ALL_MODES:
            assert mode in MANDATORY_SECTIONS_BY_MODE, (
                f"MANDATORY_SECTIONS_BY_MODE missing {mode}"
            )


# =============================================================================
# ALL_MODES Validity
# =============================================================================


class TestAllModes:
    def test_all_modes_is_tuple(self):
        """ALL_MODES is a tuple (immutable)."""
        assert isinstance(ALL_MODES, tuple)

    def test_all_modes_count(self):
        """ALL_MODES has 8 modes."""
        assert len(ALL_MODES) == 8

    def test_expected_modes_present(self):
        """All expected modes are in ALL_MODES."""
        expected = {
            "full", "quick", "lit-review", "systematic-review",
            "hypothesis", "fact-check", "socratic", "review",
        }
        assert set(ALL_MODES) == expected

    def test_no_duplicate_modes(self):
        """No duplicate modes."""
        assert len(ALL_MODES) == len(set(ALL_MODES))


# =============================================================================
# TIER_ORDER Validity
# =============================================================================


class TestTierOrder:
    def test_tier_order_is_tuple(self):
        """TIER_ORDER is a tuple."""
        assert isinstance(TIER_ORDER, tuple)

    def test_tier_order_content(self):
        """TIER_ORDER is T1, T2, T3, T4."""
        assert TIER_ORDER == ("T1", "T2", "T3", "T4")


# =============================================================================
# Word Count Structure
# =============================================================================


class TestWordCountStructure:
    def test_word_count_has_four_keys(self):
        """Each mode's word count has target_min, target_max, hard_min, hard_max."""
        required_keys = {"target_min", "target_max", "hard_min", "hard_max"}
        for mode, wc in WORD_COUNTS.items():
            assert set(wc.keys()) == required_keys, f"Mode {mode} missing keys"

    def test_hard_min_leq_target_min(self):
        """hard_min ≤ target_min for all modes."""
        for mode, wc in WORD_COUNTS.items():
            assert wc["hard_min"] <= wc["target_min"], (
                f"Mode {mode}: hard_min {wc['hard_min']} > target_min {wc['target_min']}"
            )

    def test_target_min_leq_target_max(self):
        """target_min ≤ target_max for all modes."""
        for mode, wc in WORD_COUNTS.items():
            assert wc["target_min"] <= wc["target_max"], (
                f"Mode {mode}: target_min > target_max"
            )

    def test_target_max_leq_hard_max(self):
        """target_max ≤ hard_max for all modes."""
        for mode, wc in WORD_COUNTS.items():
            assert wc["target_max"] <= wc["hard_max"], (
                f"Mode {mode}: target_max > hard_max"
            )

    def test_all_values_non_negative(self):
        """All word count values ≥ 0."""
        for mode, wc in WORD_COUNTS.items():
            for key, val in wc.items():
                assert val >= 0, f"Mode {mode}, {key} is negative: {val}"

    def test_socratic_word_counts_zero(self):
        """Socratic mode has all-zero word counts (no compiler output)."""
        wc = WORD_COUNTS["socratic"]
        assert all(v == 0 for v in wc.values())


# =============================================================================
# Spot Check Rates Structure
# =============================================================================


class TestSpotCheckRates:
    def test_spot_check_has_two_keys(self):
        """Each mode's spot check rates have biomedical and general keys."""
        for mode, rates in SPOT_CHECK_RATES.items():
            assert "biomedical" in rates, f"Mode {mode} missing 'biomedical'"
            assert "general" in rates, f"Mode {mode} missing 'general'"

    def test_spot_check_rates_valid_range(self):
        """All spot check rates are 0.0-1.0."""
        for mode, rates in SPOT_CHECK_RATES.items():
            for topic, rate in rates.items():
                assert 0.0 <= rate <= 1.0, (
                    f"Mode {mode}, {topic} rate {rate} out of range [0, 1]"
                )

    def test_systematic_review_verifies_all(self):
        """Systematic review spot-checks 100% of sources."""
        assert SPOT_CHECK_RATES["systematic-review"]["biomedical"] == 1.0
        assert SPOT_CHECK_RATES["systematic-review"]["general"] == 1.0

    def test_fact_check_verifies_all(self):
        """Fact-check spot-checks 100% of sources."""
        assert SPOT_CHECK_RATES["fact-check"]["biomedical"] == 1.0
        assert SPOT_CHECK_RATES["fact-check"]["general"] == 1.0

    def test_biomedical_geq_general(self):
        """Biomedical spot-check rate ≥ general for all modes."""
        for mode, rates in SPOT_CHECK_RATES.items():
            assert rates["biomedical"] >= rates["general"], (
                f"Mode {mode}: biomedical < general"
            )


# =============================================================================
# Evidence Strength Thresholds
# =============================================================================


class TestEvidenceStrengthThresholds:
    def test_strong_gt_moderate(self):
        """STRONG_MIN_SOURCES > MODERATE_MIN_SOURCES."""
        assert STRONG_MIN_SOURCES > MODERATE_MIN_SOURCES

    def test_strong_min_is_three(self):
        """STRONG_MIN_SOURCES is 3."""
        assert STRONG_MIN_SOURCES == 3

    def test_moderate_min_is_two(self):
        """MODERATE_MIN_SOURCES is 2."""
        assert MODERATE_MIN_SOURCES == 2

    def test_emerging_max_age(self):
        """EMERGING_MAX_AGE_YEARS is 1.0."""
        assert EMERGING_MAX_AGE_YEARS == 1.0


# =============================================================================
# Hypothesis Thresholds
# =============================================================================


class TestHypothesisThresholds:
    def test_strong_gt_viable(self):
        """HYPOTHESIS_STRONG_THRESHOLD > HYPOTHESIS_VIABLE_THRESHOLD."""
        assert HYPOTHESIS_STRONG_THRESHOLD > HYPOTHESIS_VIABLE_THRESHOLD

    def test_strong_leq_max(self):
        """HYPOTHESIS_STRONG_THRESHOLD ≤ HYPOTHESIS_MAX_SCORE."""
        assert HYPOTHESIS_STRONG_THRESHOLD <= HYPOTHESIS_MAX_SCORE

    def test_max_score_consistent(self):
        """Max score = criteria count × 2 (since each criterion is 0-2)."""
        assert HYPOTHESIS_MAX_SCORE == HYPOTHESIS_CRITERIA_COUNT * 2


# =============================================================================
# Convergence Thresholds
# =============================================================================


class TestConvergenceThresholds:
    def test_signals_required_leq_total(self):
        """CONVERGENCE_SIGNALS_REQUIRED ≤ CONVERGENCE_SIGNALS_TOTAL."""
        assert CONVERGENCE_SIGNALS_REQUIRED <= CONVERGENCE_SIGNALS_TOTAL

    def test_time_limit_positive(self):
        """CONVERGENCE_TIME_LIMIT_TURNS > 0."""
        assert CONVERGENCE_TIME_LIMIT_TURNS > 0

    def test_stagnation_positive(self):
        """CONVERGENCE_STAGNATION_ROUNDS > 0."""
        assert CONVERGENCE_STAGNATION_ROUNDS > 0

    def test_scope_stability_positive(self):
        """SCOPE_STABILITY_ROUNDS > 0."""
        assert SCOPE_STABILITY_ROUNDS > 0


# =============================================================================
# Other Constants
# =============================================================================


class TestOtherConstants:
    def test_kappa_threshold_in_range(self):
        """KAPPA_THRESHOLD is between 0 and 1."""
        assert 0.0 < KAPPA_THRESHOLD <= 1.0

    def test_kappa_threshold_value(self):
        """KAPPA_THRESHOLD is 0.80."""
        assert KAPPA_THRESHOLD == 0.80

    def test_mandatory_sections_all_is_tuple(self):
        """MANDATORY_SECTIONS_ALL is a tuple."""
        assert isinstance(MANDATORY_SECTIONS_ALL, tuple)

    def test_mandatory_sections_all_content(self):
        """MANDATORY_SECTIONS_ALL contains expected sections."""
        assert "AI Disclosure" in MANDATORY_SECTIONS_ALL
        assert "References" in MANDATORY_SECTIONS_ALL
        assert "Limitations" in MANDATORY_SECTIONS_ALL

    def test_citation_pattern_is_string(self):
        """CITATION_PATTERN is a string."""
        assert isinstance(CITATION_PATTERN, str)

    def test_citation_pattern_matches_format(self):
        """CITATION_PATTERN matches expected [T1: source] format."""
        import re
        assert re.search(CITATION_PATTERN, "[T1: Smith 2024]")
        assert re.search(CITATION_PATTERN, "[T4: Jones et al.]")
        assert not re.search(CITATION_PATTERN, "[T5: Invalid]")
        assert not re.search(CITATION_PATTERN, "No citation here")


# =============================================================================
# Currency Thresholds
# =============================================================================


class TestCurrencyThresholds:
    def test_known_fields_present(self):
        """Expected research fields have currency thresholds."""
        expected = ["biomedical", "ml_genomics", "drug_development", "clinical_practice"]
        for f in expected:
            assert f in CURRENCY_THRESHOLDS, f"Missing field: {f}"

    def test_recent_gt_current(self):
        """Recent threshold ≥ current threshold for all non-exempt fields."""
        for f, thresholds in CURRENCY_THRESHOLDS.items():
            if thresholds["recent"] is not None and thresholds["current"] is not None:
                assert thresholds["recent"] >= thresholds["current"], (
                    f"Field {f}: recent < current"
                )

    def test_seminal_exempt(self):
        """Seminal works are exempt (None thresholds)."""
        assert CURRENCY_THRESHOLDS["seminal"]["recent"] is None
        assert CURRENCY_THRESHOLDS["seminal"]["current"] is None


# =============================================================================
# MIN_SOURCES and MIN_DATABASES Consistency
# =============================================================================


class TestSourceDatabaseConsistency:
    def test_review_socratic_zero_sources(self):
        """Review and socratic modes require 0 sources (no search phase)."""
        assert MIN_SOURCES["review"] == 0
        assert MIN_SOURCES["socratic"] == 0

    def test_review_socratic_zero_databases(self):
        """Review and socratic modes require 0 databases."""
        assert MIN_DATABASES["review"] == 0
        assert MIN_DATABASES["socratic"] == 0

    def test_systematic_highest_sources(self):
        """Systematic-review has the most stringent source requirement."""
        max_sources = max(MIN_SOURCES.values())
        assert MIN_SOURCES["systematic-review"] == max_sources

    def test_systematic_highest_databases(self):
        """Systematic-review has the most stringent database requirement."""
        max_dbs = max(MIN_DATABASES.values())
        assert MIN_DATABASES["systematic-review"] == max_dbs

    def test_all_values_non_negative(self):
        """All source/database minimums ≥ 0."""
        for mode in ALL_MODES:
            assert MIN_SOURCES[mode] >= 0
            assert MIN_DATABASES[mode] >= 0


# =============================================================================
# Section Schema Tests
# =============================================================================


class TestSectionSchemas:
    def test_section_schemas_all_modes(self):
        """Every mode in ALL_MODES has a SECTION_SCHEMAS entry."""
        for mode in ALL_MODES:
            assert mode in SECTION_SCHEMAS, f"SECTION_SCHEMAS missing {mode}"

    def test_section_schemas_consistency(self):
        """Every section in MANDATORY_SECTIONS_BY_MODE appears in SECTION_SCHEMAS as required."""
        for mode in ALL_MODES:
            if mode == "socratic":
                continue
            schema_required = {
                s["name"] for s in SECTION_SCHEMAS.get(mode, []) if s.get("required", False)
            }
            mandatory = set(MANDATORY_SECTIONS_BY_MODE.get(mode, ())) | set(MANDATORY_SECTIONS_ALL)
            missing = mandatory - schema_required
            assert not missing, (
                f"Mode '{mode}': mandatory sections {missing} not in SECTION_SCHEMAS as required"
            )

    def test_section_schemas_order_unique(self):
        """No two sections in same mode share order index."""
        for mode in ALL_MODES:
            schema = SECTION_SCHEMAS.get(mode, [])
            orders = [s.get("order", i) for i, s in enumerate(schema)]
            assert len(orders) == len(set(orders)), (
                f"Mode '{mode}' has duplicate order indexes: {orders}"
            )


# =============================================================================
# File Specs Tests
# =============================================================================


class TestFileSpecs:
    def test_file_specs_all_modes(self):
        """Every mode in ALL_MODES has a FILE_SPECS entry."""
        for mode in ALL_MODES:
            assert mode in FILE_SPECS, f"FILE_SPECS missing {mode}"

    def test_file_specs_max_files_positive(self):
        """max_files >= 0 for all modes."""
        for mode in ALL_MODES:
            spec = FILE_SPECS[mode]
            max_files = spec.get("max_files", 0)
            assert max_files >= 0, (
                f"Mode '{mode}' has negative max_files: {max_files}"
            )

    def test_file_specs_socratic_zero_files(self):
        """Socratic mode has max_files=0."""
        assert FILE_SPECS["socratic"]["max_files"] == 0

    def test_file_specs_have_naming(self):
        """Non-socratic modes have a naming pattern."""
        for mode in ALL_MODES:
            if mode == "socratic":
                continue
            spec = FILE_SPECS[mode]
            assert "naming" in spec, f"Mode '{mode}' FILE_SPECS missing 'naming'"
            assert len(spec["naming"]) > 0, f"Mode '{mode}' has empty naming pattern"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
