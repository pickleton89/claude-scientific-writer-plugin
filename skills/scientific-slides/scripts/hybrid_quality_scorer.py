#!/usr/bin/env python3
"""
Hybrid quality scoring combining deterministic and AI-based evaluation.

Scoring Breakdown:
- 40% Deterministic (measurable criteria)
- 60% AI Review (subjective criteria)

Weighting rationale:
- Deterministic (40%): Objective, reproducible measurements
  - Dimensions/aspect ratio: 10%
  - Contrast/readability: 15%
  - White space/composition: 15%
- AI Review (60%): Subjective quality assessment
  - Visual appeal: 20%
  - Content relevance: 20%
  - Professional polish: 20%

Usage:
    from hybrid_quality_scorer import HybridQualityScorer

    scorer = HybridQualityScorer()
    result = scorer.score(image_path, ai_score=7.5)
    print(f"Total: {result.total_score}, Pass: {result.passed_threshold}")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from validate_slide_image import SlideImageValidator


@dataclass
class HybridScore:
    """Combined quality score with breakdown."""

    total_score: float  # 0-10 final score
    deterministic_score: float  # 0-10 from measurable criteria
    ai_score: float  # 0-10 from AI review
    deterministic_weight: float
    ai_weight: float
    passed_threshold: bool
    details: dict[str, Any] = field(default_factory=dict)


class HybridQualityScorer:
    """
    Combines deterministic image analysis with AI quality review.

    The hybrid approach ensures:
    1. Consistent baseline quality through deterministic checks
    2. Creative quality assessment through AI review
    3. Explainable scoring with clear weight breakdown
    """

    DEFAULT_THRESHOLD = 6.5
    DEFAULT_DETERMINISTIC_WEIGHT = 0.4
    DEFAULT_AI_WEIGHT = 0.6

    def __init__(
        self,
        deterministic_weight: float = DEFAULT_DETERMINISTIC_WEIGHT,
        ai_weight: float = DEFAULT_AI_WEIGHT,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        """
        Initialize hybrid scorer.

        Args:
            deterministic_weight: Weight for deterministic score (0-1)
            ai_weight: Weight for AI score (0-1)
            threshold: Minimum score to pass (0-10)

        Raises:
            ValueError: If weights don't sum to 1.0
        """
        if abs((deterministic_weight + ai_weight) - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {deterministic_weight + ai_weight}")

        self.deterministic_weight = deterministic_weight
        self.ai_weight = ai_weight
        self.threshold = threshold
        self.validator = SlideImageValidator()

    def score(
        self,
        image_path: str,
        ai_score: float,
        ai_feedback: str = "",
        expected_colors: list[str] | None = None,
    ) -> HybridScore:
        """
        Calculate hybrid quality score.

        Args:
            image_path: Path to generated slide image
            ai_score: Score from AI review (0-10)
            ai_feedback: Text feedback from AI review
            expected_colors: Optional brand colors for compliance check

        Returns:
            HybridScore with combined assessment
        """
        # Validate AI score range
        ai_score = max(0.0, min(10.0, ai_score))

        # Get deterministic score
        validation = self.validator.validate(image_path, expected_colors)
        deterministic_score = validation.score

        # Calculate weighted total
        total_score = (deterministic_score * self.deterministic_weight) + (
            ai_score * self.ai_weight
        )
        total_score = round(total_score, 2)

        # Determine if passed
        passed = total_score >= self.threshold

        # Compile details
        details = {
            "deterministic_breakdown": {
                "score": deterministic_score,
                "checks": validation.checks,
                "measurements": validation.details,
                "warnings": validation.warnings,
                "errors": validation.errors,
            },
            "ai_breakdown": {
                "score": ai_score,
                "feedback": ai_feedback,
            },
            "threshold": self.threshold,
            "weights": {
                "deterministic": self.deterministic_weight,
                "ai": self.ai_weight,
            },
        }

        return HybridScore(
            total_score=total_score,
            deterministic_score=deterministic_score,
            ai_score=ai_score,
            deterministic_weight=self.deterministic_weight,
            ai_weight=self.ai_weight,
            passed_threshold=passed,
            details=details,
        )

    def should_regenerate(self, hybrid_score: HybridScore) -> tuple[bool, str]:
        """
        Determine if image should be regenerated based on hybrid score.

        Returns:
            Tuple of (should_regenerate, reason)
        """
        det_breakdown = hybrid_score.details.get("deterministic_breakdown", {})

        # Hard failures (deterministic errors)
        errors = det_breakdown.get("errors", [])
        if errors:
            return True, f"Deterministic validation failed: {errors[0]}"

        # Soft failures (threshold)
        if not hybrid_score.passed_threshold:
            if hybrid_score.deterministic_score < 5.0:
                return True, f"Low deterministic score ({hybrid_score.deterministic_score}/10)"
            elif hybrid_score.ai_score < 5.0:
                return True, f"Low AI score ({hybrid_score.ai_score}/10)"
            else:
                return (
                    True,
                    f"Below threshold ({hybrid_score.total_score} < {self.threshold})",
                )

        return False, "Quality acceptable"

    def get_improvement_suggestions(self, hybrid_score: HybridScore) -> list[str]:
        """
        Generate actionable suggestions based on score breakdown.

        Returns:
            List of improvement suggestions
        """
        suggestions = []
        det_breakdown = hybrid_score.details.get("deterministic_breakdown", {})

        # Check for specific issues
        checks = det_breakdown.get("checks", {})
        measurements = det_breakdown.get("measurements", {})

        if not checks.get("aspect_ratio"):
            suggestions.append("Adjust image to 16:9 aspect ratio")

        if not checks.get("min_dimensions"):
            suggestions.append("Increase resolution to at least 1280x720")

        if not checks.get("adequate_contrast"):
            contrast = measurements.get("contrast_score", 0)
            suggestions.append(f"Increase contrast (current: {contrast:.2f}, target: 0.5+)")

        if not checks.get("adequate_white_space"):
            ws = measurements.get("white_space_percent", 0)
            if ws < 25:
                suggestions.append(f"Add more white space (current: {ws}%, target: 25-70%)")
            else:
                suggestions.append(f"Reduce white space (current: {ws}%, target: 25-70%)")

        # AI feedback suggestions
        ai_feedback = hybrid_score.details.get("ai_breakdown", {}).get("feedback", "")
        if ai_feedback and hybrid_score.ai_score < 7.0:
            suggestions.append(f"AI feedback: {ai_feedback[:200]}")

        return suggestions


def format_score_report(hybrid_score: HybridScore) -> str:
    """Format a human-readable score report."""
    lines = [
        "=" * 50,
        "Hybrid Quality Score Report",
        "=" * 50,
        "",
        f"Total Score: {hybrid_score.total_score}/10",
        f"Status: {'PASSED' if hybrid_score.passed_threshold else 'FAILED'}",
        f"Threshold: {hybrid_score.details.get('threshold', 6.5)}",
        "",
        "Score Breakdown:",
        f"  Deterministic: {hybrid_score.deterministic_score}/10 "
        f"(weight: {hybrid_score.deterministic_weight:.0%})",
        f"  AI Review: {hybrid_score.ai_score}/10 "
        f"(weight: {hybrid_score.ai_weight:.0%})",
        "",
    ]

    det_breakdown = hybrid_score.details.get("deterministic_breakdown", {})

    # Add errors
    errors = det_breakdown.get("errors", [])
    if errors:
        lines.append("Errors:")
        for e in errors:
            lines.append(f"  - {e}")
        lines.append("")

    # Add warnings
    warnings = det_breakdown.get("warnings", [])
    if warnings:
        lines.append("Warnings:")
        for w in warnings:
            lines.append(f"  - {w}")
        lines.append("")

    # Add measurements
    measurements = det_breakdown.get("measurements", {})
    if measurements:
        lines.append("Measurements:")
        for k, v in measurements.items():
            lines.append(f"  {k}: {v}")

    return "\n".join(lines)
