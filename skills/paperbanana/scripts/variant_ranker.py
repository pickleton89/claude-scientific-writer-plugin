"""Rank variant figures using multimodal Gemini evaluation.

Sends all variant images to Gemini Flash in a single multimodal call,
requesting structured scoring on faithfulness, readability, conciseness,
and aesthetics. Computes a weighted composite score and ranks variants.
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

# Add shared utilities to path
_SHARED_DIR = Path(__file__).resolve().parent.parent.parent / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

# Add local utils to path
_UTILS_DIR = Path(__file__).resolve().parent / "utils"
if str(_UTILS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_UTILS_DIR.parent))

logger = logging.getLogger(__name__)

# Composite score weights
_W_FAITHFULNESS = 0.35
_W_READABILITY = 0.25
_W_CONCISENESS = 0.15
_W_AESTHETICS = 0.25


@dataclass
class VariantScore:
    """Evaluation scores for a single variant."""

    variant_index: int
    strategy: str
    image_path: str
    faithfulness: float
    conciseness: float
    readability: float
    aesthetics: float
    composite_score: float
    rank: int


@dataclass
class RankingResult:
    """Result of ranking all variants."""

    scores: list[VariantScore]
    winner_index: int
    ranking_rationale: str


def compute_composite(
    faithfulness: float,
    readability: float,
    conciseness: float,
    aesthetics: float,
) -> float:
    """Compute weighted composite score from four dimensions.

    Weights: F=0.35, R=0.25, C=0.15, A=0.25

    Args:
        faithfulness: Faithfulness score (0-1).
        readability: Readability score (0-1).
        conciseness: Conciseness score (0-1).
        aesthetics: Aesthetics score (0-1).

    Returns:
        Weighted composite score (0-1).
    """
    return (
        faithfulness * _W_FAITHFULNESS
        + readability * _W_READABILITY
        + conciseness * _W_CONCISENESS
        + aesthetics * _W_AESTHETICS
    )


def rank_variants(
    image_paths: list[str],
    strategies: list[str],
    caption: str,
    source_text: str,
    api_key: str,
) -> RankingResult:
    """Rank variant figures using a multimodal Gemini Flash call.

    Args:
        image_paths: Paths to variant images on disk.
        strategies: Strategy name for each variant (same order as images).
        caption: Original figure caption.
        source_text: Source text for faithfulness evaluation.
        api_key: Google API key.

    Returns:
        RankingResult with scored and ranked variants.
    """
    try:
        return _rank_via_gemini(image_paths, strategies, caption, source_text, api_key)
    except Exception:
        logger.exception("Gemini ranking failed; using fallback equal scores")
        return _fallback_ranking(image_paths, strategies)


def _rank_via_gemini(
    image_paths: list[str],
    strategies: list[str],
    caption: str,
    source_text: str,
    api_key: str,
) -> RankingResult:
    """Call Gemini Flash with all images for multimodal scoring."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    # Build multimodal parts: text prompt + each image
    prompt = (
        "You are a scientific figure quality evaluator. "
        f"The intended caption is: \"{caption}\"\n"
        f"Source context (first 500 chars): \"{source_text[:500]}\"\n\n"
        f"I will show you {len(image_paths)} variant figures. "
        "For each variant, score these dimensions from 0.0 to 1.0:\n"
        "- faithfulness: How accurately does the figure represent the source content?\n"
        "- readability: How clear and easy to understand is the figure?\n"
        "- conciseness: How well does the figure avoid clutter and unnecessary elements?\n"
        "- aesthetics: How visually appealing and professional is the figure?\n\n"
        "Respond ONLY with valid JSON in this exact format:\n"
        "{\n"
        '  "variants": [\n'
        '    {"index": 0, "faithfulness": 0.8, "readability": 0.7, '
        '"conciseness": 0.6, "aesthetics": 0.9},\n'
        "    ...\n"
        "  ],\n"
        '  "rationale": "Brief explanation of the ranking."\n'
        "}"
    )

    parts: list = [types.Part.from_text(prompt)]

    for i, img_path in enumerate(image_paths):
        parts.append(types.Part.from_text(f"\n--- Variant {i} (strategy: {strategies[i]}) ---"))
        with open(img_path, "rb") as f:
            image_data = f.read()
        mime = "image/png" if img_path.lower().endswith(".png") else "image/jpeg"
        parts.append(types.Part.from_bytes(data=image_data, mime_type=mime))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=parts,
    )

    return _parse_ranking_response(response.text, image_paths, strategies)


def _parse_ranking_response(
    response_text: str,
    image_paths: list[str],
    strategies: list[str],
) -> RankingResult:
    """Parse the JSON response from Gemini into a RankingResult."""
    # Strip markdown code fences if present
    text = response_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3].strip()

    data = json.loads(text)
    variants_data = data["variants"]
    rationale = data.get("rationale", "")

    scores: list[VariantScore] = []
    for entry in variants_data:
        idx = entry["index"]
        f = float(entry["faithfulness"])
        r = float(entry["readability"])
        c = float(entry["conciseness"])
        a = float(entry["aesthetics"])
        scores.append(
            VariantScore(
                variant_index=idx,
                strategy=strategies[idx] if idx < len(strategies) else "unknown",
                image_path=image_paths[idx] if idx < len(image_paths) else "",
                faithfulness=f,
                conciseness=c,
                readability=r,
                aesthetics=a,
                composite_score=compute_composite(f, r, c, a),
                rank=0,  # assigned below
            )
        )

    # Sort by composite descending, assign ranks
    scores.sort(key=lambda s: s.composite_score, reverse=True)
    for rank, score in enumerate(scores):
        score.rank = rank + 1

    winner_index = scores[0].variant_index if scores else 0

    return RankingResult(
        scores=scores,
        winner_index=winner_index,
        ranking_rationale=rationale,
    )


def _fallback_ranking(
    image_paths: list[str],
    strategies: list[str],
) -> RankingResult:
    """Return equal scores when API ranking fails."""
    scores = [
        VariantScore(
            variant_index=i,
            strategy=strategies[i] if i < len(strategies) else "unknown",
            image_path=image_paths[i] if i < len(image_paths) else "",
            faithfulness=0.5,
            conciseness=0.5,
            readability=0.5,
            aesthetics=0.5,
            composite_score=compute_composite(0.5, 0.5, 0.5, 0.5),
            rank=i + 1,
        )
        for i in range(len(image_paths))
    ]
    return RankingResult(
        scores=scores,
        winner_index=0,
        ranking_rationale="Fallback: API ranking failed; all variants scored equally.",
    )
