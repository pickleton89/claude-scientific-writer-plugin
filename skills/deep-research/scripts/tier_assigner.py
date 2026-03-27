#!/usr/bin/env python3
"""
Evidence tier assignment for the deep-research pipeline.

Encodes evidence_hierarchy.md mapping tables deterministically. Four lookup
paths in priority order:
  1. CLAIM_TYPE_TO_TIER — 20+ specific claim types
  2. LAB_EVIDENCE_TO_TIER — 12 biomedical lab evidence types
  3. DESIGN_TO_LEVEL → LEVEL_TO_TIER — study design keyword matching
  4. GRADE_TO_TIER — GRADE certainty framework

Preprint adjustment caps tier one level lower (T1→T2, T4 stays T4).
Fallback: T3 with note "insufficient information for tier assignment".

Input JSON: {"claims": [{"claim_type": "...", "source_is_preprint": bool,
             "study_design": "...", "grade_certainty": "...",
             "lab_evidence_type": "..."}]}
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from thresholds import TIER_ORDER


@dataclass
class TierAssignment:
    """Result of tier assignment for a single claim."""

    claim_index: int
    tier: str
    level: str | None  # evidence level I-VII if applicable
    method: str  # which lookup path was used
    preprint_adjusted: bool
    original_tier: str | None  # before preprint adjustment
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Path 1: Specific claim types → tier (evidence_hierarchy.md §Special Cases)
# ---------------------------------------------------------------------------

CLAIM_TYPE_TO_TIER: dict[str, str] = {
    # T1 — Mechanistic / Direct
    "crispr_ko_rescue": "T1",
    "crystal_structure_mechanism": "T1",
    "cryo_em_mechanism": "T1",
    "phase_iii_rct_primary": "T1",
    "cochrane_review": "T1",
    "prisma_meta_analysis": "T1",
    "systematic_review": "T1",
    "rct_primary_endpoint": "T1",
    # T2 — Functional
    "sirna_knockdown_phenotype": "T2",
    "shrna_knockdown_phenotype": "T2",
    "biochemical_assay": "T2",
    "ic50_measurement": "T2",
    "kd_measurement": "T2",
    "mouse_model_phenotype": "T2",
    "zebrafish_model_phenotype": "T2",
    "rct_secondary_endpoint": "T2",
    "rct_safety_signal": "T2",
    "meta_analysis_observational": "T2",
    "computational_validated_in_vitro": "T2",
    "cohort_genetic_association": "T2",
    # T3 — Association
    "gwas_hit": "T3",
    "depmap_essentiality": "T3",
    "expression_correlation": "T3",
    "rct_post_hoc_subgroup": "T3",
    "cross_sectional_survey": "T3",
    "case_report": "T3",
    "case_series": "T3",
    "narrative_review": "T3",
    "scoping_review": "T3",
    # T4 — Mention / Review
    "alphafold_prediction": "T4",
    "admet_ai_prediction": "T4",
    "text_mined_interaction": "T4",
    "database_cross_reference": "T4",
    "expert_opinion": "T4",
    "editorial": "T4",
    "consensus_statement": "T4",
    "letter_to_editor": "T4",
    "computational_prediction": "T4",
}

# ---------------------------------------------------------------------------
# Path 2: Lab evidence types → tier (evidence_hierarchy.md §Biomedical Lab)
# ---------------------------------------------------------------------------

LAB_EVIDENCE_TO_TIER: dict[str, str] = {
    "crispr_ko_rescue": "T1",
    "crystal_structure": "T1",
    "cryo_em_structure": "T1",
    "sirna_knockdown": "T2",
    "shrna_knockdown": "T2",
    "biochemical_assay": "T2",
    "animal_model": "T2",
    "cell_line_phenotype": "T2",
    "gwas": "T3",
    "depmap": "T3",
    "expression_correlation": "T3",
    "high_throughput_screen": "T3",
    "alphafold": "T4",
    "admet_prediction": "T4",
    "text_mining": "T4",
    "database_annotation": "T4",
}

# ---------------------------------------------------------------------------
# Path 3: Study design → evidence level → tier
# (evidence_hierarchy.md §Full Mapping Table)
# Keyword patterns follow quality_scorer.py DESIGN_TO_TOOL approach.
# ---------------------------------------------------------------------------

DESIGN_PATTERNS: list[tuple[str, str]] = [
    # (regex pattern, evidence level)
    (r"systematic\s+review|meta[\-\s]?analysis", "I"),
    (r"randomized\s+controlled|rct|crossover\s+trial|cluster[\-\s]?randomized", "II"),
    (r"controlled\s+non[\-\s]?randomized|quasi[\-\s]?experimental", "III"),
    (r"case[\-\s]?control|cohort|prospective|retrospective|nested\s+case", "IV"),
    (r"descriptive|narrative\s+review|cross[\-\s]?sectional|scoping\s+review", "V"),
    (r"case\s+report|case\s+series|single[\-\s]?arm|ecological", "VI"),
    (r"expert\s+opinion|editorial|consensus\s+statement|letter|commentary", "VII"),
]

LEVEL_TO_TIER: dict[str, str] = {
    "I": "T1",
    "II": "T1",
    "III": "T2",
    "IV": "T2",
    "V": "T3",
    "VI": "T3",
    "VII": "T4",
}

# ---------------------------------------------------------------------------
# Path 4: GRADE certainty → tier (evidence_hierarchy.md §GRADE)
# Conservative assignment: "moderate" → T2 (not T1-T2 range)
# ---------------------------------------------------------------------------

GRADE_TO_TIER: dict[str, str] = {
    "high": "T1",
    "moderate": "T2",
    "low": "T3",
    "very low": "T3",
    "very_low": "T3",
}

# ---------------------------------------------------------------------------
# Preprint adjustment: cap tier one level lower
# ---------------------------------------------------------------------------

_TIER_DOWNGRADE: dict[str, str] = {
    "T1": "T2",
    "T2": "T3",
    "T3": "T4",
    "T4": "T4",  # floor
}


def apply_preprint_adjustment(tier: str) -> str:
    """Downgrade tier by one level for preprints (T4 stays T4)."""
    return _TIER_DOWNGRADE.get(tier, tier)


def level_from_design(study_design: str) -> str | None:
    """Match study design text to evidence level I-VII via regex."""
    for pattern, level in DESIGN_PATTERNS:
        if re.search(pattern, study_design, re.IGNORECASE):
            return level
    return None


def assign_tier(claim: dict) -> TierAssignment:
    """
    Assign an evidence tier to a single claim.

    Tries 4 lookup paths in priority order. First match wins.

    Args:
        claim: Dict with optional keys: claim_type, lab_evidence_type,
               study_design, grade_certainty, source_is_preprint.

    Returns:
        TierAssignment with tier, method used, and any notes.
    """
    idx = claim.get("claim_index", 0)
    is_preprint = claim.get("source_is_preprint", False)

    # Path 1: claim_type
    claim_type = claim.get("claim_type", "")
    if claim_type and claim_type in CLAIM_TYPE_TO_TIER:
        tier = CLAIM_TYPE_TO_TIER[claim_type]
        result = TierAssignment(
            claim_index=idx,
            tier=tier,
            level=None,
            method="claim_type",
            preprint_adjusted=False,
            original_tier=None,
        )
        if is_preprint:
            result.original_tier = tier
            result.tier = apply_preprint_adjustment(tier)
            result.preprint_adjusted = True
            result.notes.append(f"Preprint adjustment: {tier} → {result.tier}")
        return result

    # Path 2: lab_evidence_type
    lab_type = claim.get("lab_evidence_type", "")
    if lab_type and lab_type in LAB_EVIDENCE_TO_TIER:
        tier = LAB_EVIDENCE_TO_TIER[lab_type]
        result = TierAssignment(
            claim_index=idx,
            tier=tier,
            level=None,
            method="lab_evidence",
            preprint_adjusted=False,
            original_tier=None,
        )
        if is_preprint:
            result.original_tier = tier
            result.tier = apply_preprint_adjustment(tier)
            result.preprint_adjusted = True
            result.notes.append(f"Preprint adjustment: {tier} → {result.tier}")
        return result

    # Path 3: study_design → level → tier
    study_design = claim.get("study_design", "")
    if study_design:
        level = level_from_design(study_design)
        if level is not None:
            tier = LEVEL_TO_TIER[level]
            result = TierAssignment(
                claim_index=idx,
                tier=tier,
                level=level,
                method="study_design",
                preprint_adjusted=False,
                original_tier=None,
            )
            if is_preprint:
                result.original_tier = tier
                result.tier = apply_preprint_adjustment(tier)
                result.preprint_adjusted = True
                result.notes.append(f"Preprint adjustment: {tier} → {result.tier}")
            return result

    # Path 4: GRADE certainty
    grade = claim.get("grade_certainty", "")
    if grade:
        grade_key = grade.strip().lower().replace(" ", "_")
        # Also check space-separated form
        tier = GRADE_TO_TIER.get(grade_key) or GRADE_TO_TIER.get(
            grade.strip().lower()
        )
        if tier is not None:
            result = TierAssignment(
                claim_index=idx,
                tier=tier,
                level=None,
                method="grade_certainty",
                preprint_adjusted=False,
                original_tier=None,
            )
            if is_preprint:
                result.original_tier = tier
                result.tier = apply_preprint_adjustment(tier)
                result.preprint_adjusted = True
                result.notes.append(f"Preprint adjustment: {tier} → {result.tier}")
            return result

    # Fallback: T3 with note
    return TierAssignment(
        claim_index=idx,
        tier="T3",
        level=None,
        method="fallback",
        preprint_adjusted=False,
        original_tier=None,
        notes=["Insufficient information for tier assignment — defaulting to T3"],
    )


def assign_tiers(data: dict) -> dict:
    """
    Assign tiers to all claims in a JSON structure.

    Args:
        data: Dict with "claims" key containing a list of claim dicts.

    Returns:
        Report dict with assignments and summary.
    """
    claims = data.get("claims", [])
    assignments = []

    for i, claim in enumerate(claims):
        # Pass index without mutating caller's dict
        claim_with_index = {**claim, "claim_index": claim.get("claim_index", i)}
        result = assign_tier(claim_with_index)
        assignments.append({
            "claim_index": result.claim_index,
            "tier": result.tier,
            "level": result.level,
            "method": result.method,
            "preprint_adjusted": result.preprint_adjusted,
            "original_tier": result.original_tier,
            "notes": result.notes,
        })

    # Summary: count by tier
    tier_counts = {t: 0 for t in TIER_ORDER}
    for a in assignments:
        tier_counts[a["tier"]] = tier_counts.get(a["tier"], 0) + 1

    return {
        "claim_count": len(claims),
        "assignments": assignments,
        "tier_counts": tier_counts,
        "preprint_count": sum(1 for a in assignments if a["preprint_adjusted"]),
        "fallback_count": sum(1 for a in assignments if a["method"] == "fallback"),
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: tier_assigner.py <claims.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    report = assign_tiers(data)

    print("\n" + "=" * 60)
    print("EVIDENCE TIER ASSIGNMENT")
    print("=" * 60)

    for a in report["assignments"]:
        preprint_note = " [PREPRINT]" if a["preprint_adjusted"] else ""
        level_note = f" (Level {a['level']})" if a["level"] else ""
        print(f"\n  Claim {a['claim_index']}: {a['tier']}{preprint_note}{level_note}")
        print(f"    Method: {a['method']}")
        if a["original_tier"]:
            print(f"    Original: {a['original_tier']} → {a['tier']}")
        for note in a["notes"]:
            print(f"    Note: {note}")

    print("\n" + "-" * 60)
    print(f"Summary: {report['claim_count']} claims")
    for tier, count in report["tier_counts"].items():
        if count > 0:
            print(f"  {tier}: {count}")
    if report["preprint_count"]:
        print(f"  Preprint-adjusted: {report['preprint_count']}")
    if report["fallback_count"]:
        print(f"  Fallback (T3): {report['fallback_count']}")

    # Exit with warning if many fallbacks
    if report["claim_count"] > 0:
        fallback_ratio = report["fallback_count"] / report["claim_count"]
        if fallback_ratio > 0.5:
            print(f"\n⚠ WARNING: {fallback_ratio:.0%} of claims used fallback tier assignment")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
