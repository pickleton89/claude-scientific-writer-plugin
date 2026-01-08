"""Quality scoring for scientific figures.

Provides hybrid scoring that separates measurable criteria (deterministic)
from subjective criteria (requires LLM assessment).
"""

from typing import Dict, Any, List


def calculate_measurable_score(
    specs: Dict[str, Any], venue_specs: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate quality score for measurable criteria.

    Scores 4 objective criteria worth 1 point each (40% of total):
    1. Resolution compliance
    2. Dimension compliance
    3. Accessibility compliance
    4. Typography compliance

    Args:
        specs: Figure specifications dict
        venue_specs: Venue requirements from get_venue_specs()

    Returns:
        Dict with:
            - measurable_score: Score out of 4
            - measurable_max: Maximum possible (4)
            - measurable_percentage: Score as percentage
            - details: List of scoring explanations
            - criteria: Individual criterion results
    """
    score = 0
    details = []
    criteria = {}

    # 1. Resolution check (0-1 point)
    dpi = specs.get("resolution_dpi", 0)
    min_dpi = venue_specs.get("min_dpi", 300)
    if dpi >= min_dpi:
        score += 1
        criteria["resolution"] = {"score": 1, "max": 1, "passed": True}
        details.append(f"Resolution: {dpi} DPI meets {min_dpi} DPI requirement (1/1)")
    else:
        criteria["resolution"] = {"score": 0, "max": 1, "passed": False}
        details.append(f"Resolution: {dpi} DPI below {min_dpi} DPI requirement (0/1)")

    # 2. Dimension compliance (0-1 point)
    dimensions = specs.get("dimensions", {})
    width = dimensions.get("width_mm", 0)
    column_type = dimensions.get("column_type", "single")

    if column_type == "double":
        max_width = venue_specs.get("double_col_mm", 178)
    else:
        max_width = venue_specs.get("single_col_mm", 89)

    if width > 0 and width <= max_width:
        score += 1
        criteria["dimensions"] = {"score": 1, "max": 1, "passed": True}
        details.append(f"Dimensions: {width}mm fits within {max_width}mm column (1/1)")
    elif width == 0:
        criteria["dimensions"] = {"score": 0, "max": 1, "passed": False}
        details.append("Dimensions: Not specified (0/1)")
    else:
        criteria["dimensions"] = {"score": 0, "max": 1, "passed": False}
        details.append(f"Dimensions: {width}mm exceeds {max_width}mm column (0/1)")

    # 3. Accessibility compliance (0-1 point)
    accessibility = specs.get("accessibility", {})
    colorblind_safe = accessibility.get("colorblind_safe", False)
    min_contrast = accessibility.get("min_contrast_ratio", 0)

    if colorblind_safe and min_contrast >= 4.5:
        score += 1
        criteria["accessibility"] = {"score": 1, "max": 1, "passed": True}
        details.append("Accessibility: Colorblind-safe with sufficient contrast (1/1)")
    else:
        criteria["accessibility"] = {"score": 0, "max": 1, "passed": False}
        reasons = []
        if not colorblind_safe:
            reasons.append("not colorblind-safe")
        if min_contrast < 4.5:
            reasons.append(f"contrast {min_contrast}:1 < 4.5:1")
        details.append(f"Accessibility: {', '.join(reasons)} (0/1)")

    # 4. Typography compliance (0-1 point)
    typography = specs.get("typography", {})
    min_font = typography.get("min_pt", 0)
    venue_min_font = venue_specs.get("min_font_pt", 7)

    if min_font >= venue_min_font:
        score += 1
        criteria["typography"] = {"score": 1, "max": 1, "passed": True}
        details.append(
            f"Typography: {min_font}pt meets {venue_min_font}pt minimum (1/1)"
        )
    else:
        criteria["typography"] = {"score": 0, "max": 1, "passed": False}
        details.append(
            f"Typography: {min_font}pt below {venue_min_font}pt minimum (0/1)"
        )

    return {
        "measurable_score": score,
        "measurable_max": 4,
        "measurable_percentage": round(score / 4 * 100, 1),
        "details": details,
        "criteria": criteria,
    }


def get_subjective_criteria() -> List[Dict[str, Any]]:
    """Return criteria that require LLM assessment.

    These contribute 6 points (60% of total score).
    Each criterion includes a question and scoring rubric.

    Returns:
        List of criterion dicts with:
            - criterion: Short identifier
            - question: Assessment question
            - max_points: Maximum points for this criterion
            - scoring: Dict mapping scores to descriptions
    """
    return [
        {
            "criterion": "intentionality",
            "question": "Are all visual choices purposeful with no default styling retained?",
            "max_points": 2,
            "scoring": {
                0: "Uses matplotlib/tool defaults without customization",
                1: "Mostly customized with some defaults remaining",
                2: "Every element (colors, fonts, layout) deliberately chosen",
            },
        },
        {
            "criterion": "clarity",
            "question": "How quickly can a viewer understand the main message?",
            "max_points": 2,
            "scoring": {
                0: "Confusing, takes >30s to understand main point",
                1: "Clear, understood in 10-30s with some effort",
                2: "Immediately clear, <10s to understand key message",
            },
        },
        {
            "criterion": "consistency",
            "question": "Is styling consistent with other figures in the document?",
            "max_points": 1,
            "scoring": {
                0: "Inconsistent styling (fonts, colors, or layout differs)",
                1: "Fully consistent with document style guide",
            },
        },
        {
            "criterion": "independence",
            "question": "Can figure + caption be understood without reading main text?",
            "max_points": 1,
            "scoring": {
                0: "Requires main text for interpretation",
                1: "Self-contained with descriptive caption",
            },
        },
    ]


def calculate_total_score(
    measurable_result: Dict[str, Any], subjective_scores: Dict[str, int]
) -> Dict[str, Any]:
    """Combine measurable and subjective scores.

    Total score is out of 10 points:
    - Measurable: 4 points (40%)
    - Subjective: 6 points (60%)

    Args:
        measurable_result: Output from calculate_measurable_score()
        subjective_scores: Dict mapping criterion names to scores (0-max_points)
            Expected keys: "intentionality", "clarity", "consistency", "independence"

    Returns:
        Dict with:
            - total_score: Combined score out of 10
            - max_score: Maximum possible (10)
            - measurable_component: Breakdown of measurable scoring
            - subjective_component: Breakdown of subjective scoring
            - interpretation: Quality rating description
            - publication_ready: Boolean for >= 7/10
    """
    measurable = measurable_result["measurable_score"]

    # Validate and sum subjective scores
    criteria = get_subjective_criteria()
    criteria_lookup = {c["criterion"]: c["max_points"] for c in criteria}

    subjective = 0
    subjective_details = []
    for criterion_name, score in subjective_scores.items():
        max_pts = criteria_lookup.get(criterion_name, 0)
        clamped = max(0, min(score, max_pts))
        subjective += clamped
        subjective_details.append(
            {"criterion": criterion_name, "score": clamped, "max": max_pts}
        )

    subjective_max = sum(c["max_points"] for c in criteria)
    total = measurable + subjective

    # Score interpretation
    if total <= 4:
        interpretation = "Needs major revision"
        recommendation = "Address all failed measurable criteria and improve clarity"
    elif total <= 6:
        interpretation = "Acceptable for internal use"
        recommendation = "Consider improvements before external publication"
    elif total <= 8:
        interpretation = "Publication ready"
        recommendation = "Minor refinements may enhance impact"
    else:
        interpretation = "Exemplary design"
        recommendation = "Ready for high-impact publication"

    return {
        "total_score": total,
        "max_score": 10,
        "measurable_component": {
            "score": measurable,
            "max": 4,
            "weight": "40%",
            "details": measurable_result["details"],
        },
        "subjective_component": {
            "score": subjective,
            "max": subjective_max,
            "weight": "60%",
            "details": subjective_details,
        },
        "interpretation": interpretation,
        "recommendation": recommendation,
        "publication_ready": total >= 7,
    }


def get_scoring_rubric_text() -> str:
    """Return formatted text of the complete scoring rubric.

    Useful for including in LLM prompts or documentation.
    """
    lines = [
        "# Figure Quality Scoring Rubric (10 points total)",
        "",
        "## Measurable Criteria (4 points, 40%)",
        "Scored automatically based on specifications:",
        "",
        "1. **Resolution** (1 pt): DPI meets venue minimum",
        "2. **Dimensions** (1 pt): Width fits column specification",
        "3. **Accessibility** (1 pt): Colorblind-safe + contrast >= 4.5:1",
        "4. **Typography** (1 pt): Font size meets venue minimum",
        "",
        "## Subjective Criteria (6 points, 60%)",
        "Requires human/LLM assessment:",
        "",
    ]

    for c in get_subjective_criteria():
        lines.append(f"### {c['criterion'].title()} ({c['max_points']} pts)")
        lines.append(f"*{c['question']}*")
        lines.append("")
        for score, desc in sorted(c["scoring"].items()):
            lines.append(f"- **{score}**: {desc}")
        lines.append("")

    lines.extend(
        [
            "## Score Interpretation",
            "- **0-4**: Needs major revision",
            "- **5-6**: Acceptable for internal use",
            "- **7-8**: Publication ready",
            "- **9-10**: Exemplary design",
        ]
    )

    return "\n".join(lines)
