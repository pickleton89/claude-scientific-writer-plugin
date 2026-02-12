"""Quality bridge: maps PaperBanana 4-dimension scores to the 5-point rubric.

PaperBanana evaluates on 4 dimensions (0.0-1.0 each):
  - Faithfulness, Readability, Conciseness, Aesthetics

The existing 5-point rubric (used by scientific-schematics) has 5 dimensions
(0-2 each, total 10 points):
  - Scientific Accuracy, Clarity & Readability, Label Quality,
    Layout & Composition, Professional Appearance

This module maps between the two systems for consistent quality tracking.
"""

from typing import NamedTuple


class PaperBananaScores(NamedTuple):
    """Raw scores from PaperBanana Critic (0.0-1.0 each)."""

    faithfulness: float
    readability: float
    conciseness: float
    aesthetics: float


class RubricScores(NamedTuple):
    """5-point rubric scores (0-2 each, total 0-10)."""

    scientific_accuracy: float
    clarity_readability: float
    label_quality: float
    layout_composition: float
    professional_appearance: float


def map_to_rubric(scores: PaperBananaScores) -> RubricScores:
    """Map PaperBanana 4-dim scores to 5-point rubric.

    Mapping:
        Faithfulness  → Scientific Accuracy (0-2)
        Readability   → Clarity & Readability (0-2)
        Readability   → Label Quality (0-2)  [readability implies label quality]
        Conciseness   → Layout & Composition (0-2)
        Aesthetics    → Professional Appearance (0-2)

    Args:
        scores: PaperBanana 4-dimension scores (0.0-1.0 each)

    Returns:
        RubricScores mapped to 0-2 scale per dimension
    """
    return RubricScores(
        scientific_accuracy=_scale(scores.faithfulness),
        clarity_readability=_scale(scores.readability),
        label_quality=_scale(scores.readability),
        layout_composition=_scale(scores.conciseness),
        professional_appearance=_scale(scores.aesthetics),
    )


def rubric_total(rubric: RubricScores) -> float:
    """Calculate total score from rubric (0-10 scale).

    Args:
        rubric: 5-point rubric scores

    Returns:
        Total score (sum of all dimensions, 0-10)
    """
    return sum(rubric)


def meets_threshold(rubric: RubricScores, threshold: float) -> bool:
    """Check if rubric score meets document type threshold.

    Args:
        rubric: 5-point rubric scores
        threshold: Minimum score for document type (e.g. 8.5 for journal)

    Returns:
        True if total score >= threshold
    """
    return rubric_total(rubric) >= threshold


def to_review_dict(
    pb_scores: PaperBananaScores,
    rubric: RubricScores,
) -> dict:
    """Format scores as a review log dictionary.

    Args:
        pb_scores: Original PaperBanana scores
        rubric: Mapped rubric scores

    Returns:
        Dictionary compatible with scientific-schematics review log format
    """
    return {
        "paperbanana_scores": {
            "faithfulness": round(pb_scores.faithfulness, 3),
            "readability": round(pb_scores.readability, 3),
            "conciseness": round(pb_scores.conciseness, 3),
            "aesthetics": round(pb_scores.aesthetics, 3),
        },
        "rubric_scores": {
            "scientific_accuracy": round(rubric.scientific_accuracy, 2),
            "clarity_readability": round(rubric.clarity_readability, 2),
            "label_quality": round(rubric.label_quality, 2),
            "layout_composition": round(rubric.layout_composition, 2),
            "professional_appearance": round(rubric.professional_appearance, 2),
        },
        "total_score": round(rubric_total(rubric), 2),
    }


# Quality thresholds by document type (from QUANTIFICATION_THRESHOLDS.md §8)
DOC_TYPE_THRESHOLDS: dict[str, dict] = {
    "journal": {"threshold": 8.5, "soft_limit": 3, "hard_limit": 5},
    "conference": {"threshold": 8.0, "soft_limit": 3, "hard_limit": 5},
    "thesis": {"threshold": 8.0, "soft_limit": 3, "hard_limit": 5},
    "grant": {"threshold": 8.0, "soft_limit": 3, "hard_limit": 5},
    "preprint": {"threshold": 7.5, "soft_limit": 2, "hard_limit": 4},
    "report": {"threshold": 7.5, "soft_limit": 2, "hard_limit": 4},
    "poster": {"threshold": 7.0, "soft_limit": 2, "hard_limit": 3},
    "presentation": {"threshold": 6.5, "soft_limit": 2, "hard_limit": 3},
    "default": {"threshold": 7.5, "soft_limit": 3, "hard_limit": 5},
}


def get_threshold(doc_type: str) -> dict:
    """Get quality threshold config for a document type.

    Args:
        doc_type: Document type (journal, poster, presentation, etc.)

    Returns:
        Dict with threshold, soft_limit, hard_limit keys
    """
    return DOC_TYPE_THRESHOLDS.get(doc_type, DOC_TYPE_THRESHOLDS["default"])


def _scale(value: float) -> float:
    """Scale a 0.0-1.0 score to 0-2 range.

    Args:
        value: Score in 0.0-1.0 range

    Returns:
        Score in 0.0-2.0 range
    """
    return round(min(2.0, max(0.0, value * 2.0)), 2)
