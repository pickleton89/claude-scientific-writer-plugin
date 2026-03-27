#!/usr/bin/env python3
"""
Theme-level evidence strength rating for the deep-research pipeline.

Encodes synthesis.md §Theme-Level Evidence Strength (lines 94-99):
  Strong   — ≥3 sources, (≥1 T1 OR ≥2 T2), consistent direction, no unresolved contradictions
  Moderate — ≥2 sources, ≥1 T2, mostly consistent, minor contradictions explained
  Emerging — 1-2 recent sources (≤1 year), insufficient replication but promising
  Weak     — everything else

Input JSON: {"themes": [{"name": "...", "source_count": N,
             "tier_distribution": {"T1": N, "T2": N, "T3": N, "T4": N},
             "has_contradictions": bool, "contradictions_resolved": bool,
             "all_sources_recent": bool, "consistent_direction": bool}]}
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from thresholds import STRONG_MIN_SOURCES, MODERATE_MIN_SOURCES


@dataclass
class StrengthRating:
    """Evidence strength rating for a single theme."""

    theme_name: str
    rating: str  # "Strong", "Moderate", "Emerging", "Weak"
    rationale: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def rate_theme(theme: dict) -> StrengthRating:
    """
    Rate evidence strength for a single theme.

    Evaluates in priority order: Strong → Moderate → Emerging → Weak.
    First matching rating wins.

    Args:
        theme: Dict with keys: name, source_count, tier_distribution,
               has_contradictions, contradictions_resolved,
               all_sources_recent, consistent_direction.

    Returns:
        StrengthRating with rating and rationale.
    """
    name = theme.get("name", "unnamed")
    source_count = theme.get("source_count", 0)
    tiers = theme.get("tier_distribution", {})
    has_contradictions = theme.get("has_contradictions", False)
    contradictions_resolved = theme.get("contradictions_resolved", False)
    all_recent = theme.get("all_sources_recent", False)
    consistent = theme.get("consistent_direction", True)

    t1_count = tiers.get("T1", 0)
    t2_count = tiers.get("T2", 0)
    t3_count = tiers.get("T3", 0)
    t4_count = tiers.get("T4", 0)

    unresolved_contradictions = has_contradictions and not contradictions_resolved

    # --- Strong ---
    # ≥3 sources, (≥1 T1 OR ≥2 T2), consistent direction, no unresolved contradictions
    has_enough_sources = source_count >= STRONG_MIN_SOURCES
    has_strong_evidence = t1_count >= 1 or t2_count >= 2
    no_unresolved = not unresolved_contradictions

    if has_enough_sources and has_strong_evidence and consistent and no_unresolved:
        rationale = [
            f"{source_count} sources (≥{STRONG_MIN_SOURCES})",
            f"T1={t1_count}, T2={t2_count}",
            "consistent direction",
        ]
        if has_contradictions:
            rationale.append("contradictions resolved")
        return StrengthRating(theme_name=name, rating="Strong", rationale=rationale)

    # --- Moderate ---
    # ≥2 sources, ≥1 T2, mostly consistent, minor contradictions OK if explained
    has_moderate_sources = source_count >= MODERATE_MIN_SOURCES
    has_moderate_evidence = t2_count >= 1 or t1_count >= 1
    contradictions_ok = not has_contradictions or contradictions_resolved

    if has_moderate_sources and has_moderate_evidence and contradictions_ok:
        rationale = [
            f"{source_count} sources (≥{MODERATE_MIN_SOURCES})",
            f"T1={t1_count}, T2={t2_count}",
        ]
        if not consistent:
            rationale.append("mostly consistent (minor inconsistencies)")
        else:
            rationale.append("consistent direction")
        if has_contradictions:
            rationale.append("contradictions explained")

        warnings = []
        if not consistent:
            warnings.append("Direction not fully consistent — verify with additional sources")

        return StrengthRating(
            theme_name=name, rating="Moderate", rationale=rationale, warnings=warnings
        )

    # --- Emerging ---
    # 1-2 recent sources (≤1 year), insufficient replication but promising
    # Contradictory sources are not "promising" — route to Weak instead
    is_small_sample = 1 <= source_count <= 2
    if is_small_sample and all_recent and not unresolved_contradictions:
        rationale = [
            f"{source_count} recent source(s) (≤1 year)",
            "insufficient replication",
            "promising but needs confirmation",
        ]
        return StrengthRating(theme_name=name, rating="Emerging", rationale=rationale)

    # --- Weak ---
    # Everything else: <2 sources, or T3/T4 only, or significant unresolved contradictions
    rationale = []
    if source_count < MODERATE_MIN_SOURCES:
        rationale.append(f"Only {source_count} source(s) (<{MODERATE_MIN_SOURCES})")
    if t1_count == 0 and t2_count == 0:
        rationale.append(f"T3/T4 evidence only (T3={t3_count}, T4={t4_count})")
    if unresolved_contradictions:
        rationale.append("Significant unresolved contradictions")
    if not consistent and source_count >= MODERATE_MIN_SOURCES:
        rationale.append("Inconsistent direction across sources")
    if not rationale:
        rationale.append("Does not meet criteria for Strong, Moderate, or Emerging")

    return StrengthRating(theme_name=name, rating="Weak", rationale=rationale)


def rate_themes(data: dict) -> dict:
    """
    Rate evidence strength for all themes.

    Args:
        data: Dict with "themes" key containing a list of theme dicts.

    Returns:
        Report dict with ratings and summary.
    """
    themes = data.get("themes", [])
    ratings = []

    for theme in themes:
        result = rate_theme(theme)
        ratings.append({
            "theme_name": result.theme_name,
            "rating": result.rating,
            "rationale": result.rationale,
            "warnings": result.warnings,
        })

    # Summary counts
    rating_counts = {"Strong": 0, "Moderate": 0, "Emerging": 0, "Weak": 0}
    for r in ratings:
        rating_counts[r["rating"]] += 1

    return {
        "theme_count": len(themes),
        "ratings": ratings,
        "rating_counts": rating_counts,
        "has_strong": rating_counts["Strong"] > 0,
        "has_weak": rating_counts["Weak"] > 0,
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: evidence_strength.py <themes.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    report = rate_themes(data)

    print("\n" + "=" * 60)
    print("EVIDENCE STRENGTH ASSESSMENT")
    print("=" * 60)

    for r in report["ratings"]:
        icon = {"Strong": "●", "Moderate": "◐", "Emerging": "◑", "Weak": "○"}
        print(f"\n  {icon.get(r['rating'], '?')} {r['theme_name']}: {r['rating']}")
        for reason in r["rationale"]:
            print(f"    - {reason}")
        for warning in r["warnings"]:
            print(f"    ⚠ {warning}")

    print("\n" + "-" * 60)
    print(f"Summary: {report['theme_count']} themes")
    for rating, count in report["rating_counts"].items():
        if count > 0:
            print(f"  {rating}: {count}")

    if report["has_weak"]:
        print("\n⚠ Some themes have Weak evidence — consider additional searches")

    sys.exit(0)


if __name__ == "__main__":
    main()
