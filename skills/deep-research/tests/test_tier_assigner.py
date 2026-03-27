"""Tests for tier_assigner.py — evidence tier assignment for claims."""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from tier_assigner import (
    CLAIM_TYPE_TO_TIER,
    LAB_EVIDENCE_TO_TIER,
    DESIGN_PATTERNS,
    LEVEL_TO_TIER,
    GRADE_TO_TIER,
    apply_preprint_adjustment,
    level_from_design,
    assign_tier,
    assign_tiers,
)
from thresholds import TIER_ORDER


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    def test_all_claim_types_map_to_valid_tiers(self):
        """Every claim type maps to T1-T4."""
        for ct, tier in CLAIM_TYPE_TO_TIER.items():
            assert tier in TIER_ORDER, f"Claim type {ct} maps to invalid tier {tier}"

    def test_all_lab_evidence_maps_to_valid_tiers(self):
        """Every lab evidence type maps to T1-T4."""
        for lt, tier in LAB_EVIDENCE_TO_TIER.items():
            assert tier in TIER_ORDER, f"Lab evidence {lt} maps to invalid tier {tier}"

    def test_all_levels_map_to_valid_tiers(self):
        """Every evidence level maps to T1-T4."""
        for level, tier in LEVEL_TO_TIER.items():
            assert tier in TIER_ORDER

    def test_all_grades_map_to_valid_tiers(self):
        """Every GRADE certainty maps to T1-T4."""
        for grade, tier in GRADE_TO_TIER.items():
            assert tier in TIER_ORDER

    def test_claim_type_tier_distribution(self):
        """Verify expected tier distribution for claim types."""
        tiers = list(CLAIM_TYPE_TO_TIER.values())
        assert "T1" in tiers
        assert "T2" in tiers
        assert "T3" in tiers
        assert "T4" in tiers

    def test_design_patterns_count(self):
        """Seven evidence levels have design patterns."""
        assert len(DESIGN_PATTERNS) == 7


# =============================================================================
# Path 1: Claim Type Tests
# =============================================================================


class TestClaimTypePath:
    def test_t1_claim_types(self):
        """T1 claim types assigned correctly."""
        t1_types = [
            "crispr_ko_rescue",
            "crystal_structure_mechanism",
            "cochrane_review",
            "systematic_review",
            "rct_primary_endpoint",
        ]
        for ct in t1_types:
            result = assign_tier({"claim_type": ct})
            assert result.tier == "T1", f"Expected T1 for {ct}, got {result.tier}"
            assert result.method == "claim_type"

    def test_t2_claim_types(self):
        """T2 claim types assigned correctly."""
        t2_types = [
            "sirna_knockdown_phenotype",
            "biochemical_assay",
            "mouse_model_phenotype",
            "rct_secondary_endpoint",
        ]
        for ct in t2_types:
            result = assign_tier({"claim_type": ct})
            assert result.tier == "T2", f"Expected T2 for {ct}, got {result.tier}"

    def test_t3_claim_types(self):
        """T3 claim types assigned correctly."""
        t3_types = ["gwas_hit", "expression_correlation", "case_report", "narrative_review"]
        for ct in t3_types:
            result = assign_tier({"claim_type": ct})
            assert result.tier == "T3", f"Expected T3 for {ct}, got {result.tier}"

    def test_t4_claim_types(self):
        """T4 claim types assigned correctly."""
        t4_types = [
            "alphafold_prediction",
            "text_mined_interaction",
            "expert_opinion",
            "computational_prediction",
        ]
        for ct in t4_types:
            result = assign_tier({"claim_type": ct})
            assert result.tier == "T4", f"Expected T4 for {ct}, got {result.tier}"

    def test_unknown_claim_type_falls_through(self):
        """Unknown claim type doesn't match Path 1."""
        result = assign_tier({"claim_type": "completely_unknown_type"})
        assert result.method != "claim_type"


# =============================================================================
# Path 2: Lab Evidence Tests
# =============================================================================


class TestLabEvidencePath:
    def test_crispr_is_t1(self):
        """CRISPR KO rescue → T1."""
        result = assign_tier({"lab_evidence_type": "crispr_ko_rescue"})
        assert result.tier == "T1"
        assert result.method == "lab_evidence"

    def test_sirna_is_t2(self):
        """siRNA knockdown → T2."""
        result = assign_tier({"lab_evidence_type": "sirna_knockdown"})
        assert result.tier == "T2"

    def test_gwas_is_t3(self):
        """GWAS → T3."""
        result = assign_tier({"lab_evidence_type": "gwas"})
        assert result.tier == "T3"

    def test_alphafold_is_t4(self):
        """AlphaFold prediction → T4."""
        result = assign_tier({"lab_evidence_type": "alphafold"})
        assert result.tier == "T4"

    def test_claim_type_takes_priority_over_lab(self):
        """Path 1 (claim_type) takes priority over Path 2 (lab_evidence)."""
        result = assign_tier({
            "claim_type": "crispr_ko_rescue",  # T1 via Path 1
            "lab_evidence_type": "alphafold",   # T4 via Path 2
        })
        assert result.tier == "T1"
        assert result.method == "claim_type"


# =============================================================================
# Path 3: Study Design Tests
# =============================================================================


class TestStudyDesignPath:
    def test_systematic_review_level_i(self):
        """'systematic review' → Level I → T1."""
        result = assign_tier({"study_design": "systematic review"})
        assert result.tier == "T1"
        assert result.level == "I"
        assert result.method == "study_design"

    def test_rct_level_ii(self):
        """'randomized controlled trial' → Level II → T1."""
        result = assign_tier({"study_design": "randomized controlled trial"})
        assert result.tier == "T1"
        assert result.level == "II"

    def test_quasi_experimental_level_iii(self):
        """'quasi-experimental' → Level III → T2."""
        result = assign_tier({"study_design": "quasi-experimental study"})
        assert result.tier == "T2"
        assert result.level == "III"

    def test_cohort_level_iv(self):
        """'cohort study' → Level IV → T2."""
        result = assign_tier({"study_design": "prospective cohort"})
        assert result.tier == "T2"
        assert result.level == "IV"

    def test_cross_sectional_level_v(self):
        """'cross-sectional' → Level V → T3."""
        result = assign_tier({"study_design": "cross-sectional survey"})
        assert result.tier == "T3"
        assert result.level == "V"

    def test_case_report_level_vi(self):
        """'case report' → Level VI → T3."""
        result = assign_tier({"study_design": "case report of rare adverse event"})
        assert result.tier == "T3"
        assert result.level == "VI"

    def test_expert_opinion_level_vii(self):
        """'expert opinion' → Level VII → T4."""
        result = assign_tier({"study_design": "expert opinion"})
        assert result.tier == "T4"
        assert result.level == "VII"

    def test_meta_analysis_hyphenated(self):
        """'meta-analysis' → Level I → T1."""
        result = assign_tier({"study_design": "meta-analysis"})
        assert result.tier == "T1"

    def test_case_control(self):
        """'case-control' → Level IV → T2."""
        result = assign_tier({"study_design": "case-control study"})
        assert result.tier == "T2"

    def test_unrecognized_design_falls_through(self):
        """Unrecognized study design doesn't match Path 3."""
        result = assign_tier({"study_design": "some novel approach"})
        assert result.method != "study_design"


# =============================================================================
# Path 4: GRADE Certainty Tests
# =============================================================================


class TestGradeCertaintyPath:
    def test_grade_high(self):
        """GRADE high → T1."""
        result = assign_tier({"grade_certainty": "high"})
        assert result.tier == "T1"
        assert result.method == "grade_certainty"

    def test_grade_moderate(self):
        """GRADE moderate → T2 (conservative)."""
        result = assign_tier({"grade_certainty": "moderate"})
        assert result.tier == "T2"

    def test_grade_low(self):
        """GRADE low → T3."""
        result = assign_tier({"grade_certainty": "low"})
        assert result.tier == "T3"

    def test_grade_very_low(self):
        """GRADE very low → T3."""
        result = assign_tier({"grade_certainty": "very low"})
        assert result.tier == "T3"

    def test_grade_very_low_underscore(self):
        """GRADE 'very_low' form also works."""
        result = assign_tier({"grade_certainty": "very_low"})
        assert result.tier == "T3"

    def test_grade_case_insensitive(self):
        """GRADE matching is case-insensitive."""
        result = assign_tier({"grade_certainty": "HIGH"})
        assert result.tier == "T1"

    def test_priority_claim_type_over_grade(self):
        """claim_type takes priority over grade_certainty."""
        result = assign_tier({
            "claim_type": "expert_opinion",  # T4
            "grade_certainty": "high",        # T1
        })
        assert result.tier == "T4"
        assert result.method == "claim_type"


# =============================================================================
# Preprint Adjustment Tests
# =============================================================================


class TestPreprintAdjustment:
    def test_t1_becomes_t2(self):
        """T1 preprint → T2."""
        assert apply_preprint_adjustment("T1") == "T2"

    def test_t2_becomes_t3(self):
        """T2 preprint → T3."""
        assert apply_preprint_adjustment("T2") == "T3"

    def test_t3_becomes_t4(self):
        """T3 preprint → T4."""
        assert apply_preprint_adjustment("T3") == "T4"

    def test_t4_stays_t4(self):
        """T4 preprint stays T4 (floor)."""
        assert apply_preprint_adjustment("T4") == "T4"

    def test_preprint_adjustment_applied(self):
        """Preprint flag correctly adjusts tier in assign_tier."""
        result = assign_tier({
            "claim_type": "crispr_ko_rescue",  # T1
            "source_is_preprint": True,
        })
        assert result.tier == "T2"
        assert result.preprint_adjusted is True
        assert result.original_tier == "T1"

    def test_preprint_note_in_result(self):
        """Preprint adjustment adds explanatory note."""
        result = assign_tier({
            "claim_type": "crispr_ko_rescue",
            "source_is_preprint": True,
        })
        assert any("Preprint" in n for n in result.notes)

    def test_non_preprint_not_adjusted(self):
        """Non-preprint claims are not adjusted."""
        result = assign_tier({
            "claim_type": "crispr_ko_rescue",
            "source_is_preprint": False,
        })
        assert result.tier == "T1"
        assert result.preprint_adjusted is False
        assert result.original_tier is None

    def test_preprint_adjustment_path3_study_design(self):
        """Preprint adjustment works via study_design path (T1 RCT → T2)."""
        result = assign_tier({
            "study_design": "randomized controlled trial",
            "source_is_preprint": True,
        })
        assert result.tier == "T2"
        assert result.original_tier == "T1"
        assert result.method == "study_design"

    def test_preprint_adjustment_path4_grade(self):
        """Preprint adjustment works via grade_certainty path (T1 high → T2)."""
        result = assign_tier({
            "grade_certainty": "high",
            "source_is_preprint": True,
        })
        assert result.tier == "T2"
        assert result.original_tier == "T1"
        assert result.method == "grade_certainty"


# =============================================================================
# Fallback Tests
# =============================================================================


class TestFallback:
    def test_empty_claim_fallback(self):
        """Empty claim dict → T3 fallback."""
        result = assign_tier({})
        assert result.tier == "T3"
        assert result.method == "fallback"

    def test_fallback_has_note(self):
        """Fallback includes explanatory note."""
        result = assign_tier({})
        assert any("insufficient" in n.lower() for n in result.notes)

    def test_all_empty_strings_fallback(self):
        """All fields empty strings → fallback."""
        result = assign_tier({
            "claim_type": "",
            "lab_evidence_type": "",
            "study_design": "",
            "grade_certainty": "",
        })
        assert result.method == "fallback"


# =============================================================================
# Batch Assignment Tests
# =============================================================================


class TestBatchAssignment:
    def test_assign_tiers_basic(self):
        """Batch assignment processes all claims."""
        data = {
            "claims": [
                {"claim_type": "crispr_ko_rescue"},
                {"claim_type": "gwas_hit"},
                {"claim_type": "alphafold_prediction"},
            ]
        }
        report = assign_tiers(data)
        assert report["claim_count"] == 3
        assert len(report["assignments"]) == 3

    def test_tier_counts(self):
        """Tier counts summarized correctly."""
        data = {
            "claims": [
                {"claim_type": "crispr_ko_rescue"},       # T1
                {"claim_type": "systematic_review"},        # T1
                {"claim_type": "biochemical_assay"},        # T2
                {"claim_type": "gwas_hit"},                 # T3
                {"claim_type": "expert_opinion"},           # T4
            ]
        }
        report = assign_tiers(data)
        assert report["tier_counts"]["T1"] == 2
        assert report["tier_counts"]["T2"] == 1
        assert report["tier_counts"]["T3"] == 1
        assert report["tier_counts"]["T4"] == 1

    def test_preprint_count(self):
        """Preprint count tracked in summary."""
        data = {
            "claims": [
                {"claim_type": "crispr_ko_rescue", "source_is_preprint": True},
                {"claim_type": "crispr_ko_rescue", "source_is_preprint": False},
            ]
        }
        report = assign_tiers(data)
        assert report["preprint_count"] == 1

    def test_fallback_count(self):
        """Fallback count tracked in summary."""
        data = {
            "claims": [
                {"claim_type": "crispr_ko_rescue"},
                {},  # fallback
                {},  # fallback
            ]
        }
        report = assign_tiers(data)
        assert report["fallback_count"] == 2

    def test_empty_claims_list(self):
        """Empty claims list handled gracefully."""
        report = assign_tiers({"claims": []})
        assert report["claim_count"] == 0
        assert report["fallback_count"] == 0


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    def test_claim_index_preserved(self):
        """Claim index is preserved in assignment."""
        result = assign_tier({"claim_type": "gwas_hit", "claim_index": 42})
        assert result.claim_index == 42

    def test_deterministic_output(self):
        """Same input always produces same tier."""
        for _ in range(10):
            result = assign_tier({"claim_type": "crispr_ko_rescue"})
            assert result.tier == "T1"

    def test_design_pattern_case_insensitive(self):
        """Study design matching is case-insensitive."""
        result = assign_tier({"study_design": "RANDOMIZED CONTROLLED TRIAL"})
        assert result.tier == "T1"

    def test_level_from_design_returns_none_for_unknown(self):
        """level_from_design returns None for unrecognized designs."""
        assert level_from_design("completely novel study type") is None

    def test_all_four_paths_work(self):
        """Each of the 4 lookup paths can be triggered."""
        p1 = assign_tier({"claim_type": "gwas_hit"})
        p2 = assign_tier({"lab_evidence_type": "sirna_knockdown"})
        p3 = assign_tier({"study_design": "cohort study"})
        p4 = assign_tier({"grade_certainty": "moderate"})

        assert p1.method == "claim_type"
        assert p2.method == "lab_evidence"
        assert p3.method == "study_design"
        assert p4.method == "grade_certainty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
