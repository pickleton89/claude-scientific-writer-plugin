"""Orchestrate multi-variant generation, ranking, and refinement.

Generates N figure variants with different communicative intents, ranks
them via multimodal Gemini evaluation, optionally refines the winner,
and produces a JSON review log.
"""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# Add shared utilities to path
_SHARED_DIR = Path(__file__).resolve().parent.parent.parent / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

# Add local utils to path
_UTILS_DIR = Path(__file__).resolve().parent / "utils"
if str(_UTILS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_UTILS_DIR.parent))

from variant_intents import VariantIntent, generate_variant_intents
from variant_ranker import RankingResult, rank_variants

logger = logging.getLogger(__name__)

_MAX_RETRIES = 2
_INITIAL_BACKOFF = 30.0


@dataclass
class VariantConfig:
    """Configuration for multi-variant generation."""

    n_variants: int = 3
    delay_between_runs: float = 30.0
    refine_winner: bool = True
    refinement_iterations: int = 2
    verbose: bool = False


@dataclass
class MultiVariantResult:
    """Result of a multi-variant generation run."""

    variants: list[dict[str, Any]] = field(default_factory=list)
    ranking: RankingResult | None = None
    refined_image_path: str | None = None
    review_log_path: str | None = None


async def run_multi_variant(
    source_text: str,
    caption: str,
    output_dir: str,
    output_stem: str,
    settings_factory: Callable[[int], Any],
    api_key: str,
    config: VariantConfig | None = None,
) -> MultiVariantResult:
    """Run multi-variant figure generation with ranking and optional refinement.

    Args:
        source_text: Source text to visualize.
        caption: Original communicative intent / figure caption.
        output_dir: Directory for output images and logs.
        output_stem: Base filename stem (e.g. "figure1").
        settings_factory: Callable that takes iteration count and returns Settings.
        api_key: Google API key for Gemini.
        config: Variant generation configuration. Uses defaults if None.

    Returns:
        MultiVariantResult with variant info, ranking, and paths.
    """
    from paperbanana import DiagramType, GenerationInput, PaperBananaPipeline

    if config is None:
        config = VariantConfig()

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    result = MultiVariantResult()

    # Generate variant intents
    if config.verbose:
        logger.info("Generating %d variant intents...", config.n_variants)

    intents = generate_variant_intents(
        caption=caption,
        source_text=source_text,
        n=config.n_variants,
        api_key=api_key,
    )

    # Generate each variant
    image_paths: list[str] = []
    strategies: list[str] = []

    for intent in intents:
        variant_path = str(out_path / f"{output_stem}_v{intent.index}.png")

        if config.verbose:
            logger.info(
                "Generating variant %d (%s)...", intent.index, intent.strategy.value
            )

        try:
            gen_result = await _generate_with_retry(
                source_text=source_text,
                intent=intent,
                settings_factory=settings_factory,
                variant_path=variant_path,
            )

            image_paths.append(variant_path)
            strategies.append(intent.strategy.value)

            variant_info: dict[str, Any] = {
                "index": intent.index,
                "strategy": intent.strategy.value,
                "image_path": variant_path,
                "communicative_intent": intent.communicative_intent,
                "scores": _extract_scores(gen_result),
            }
            result.variants.append(variant_info)

        except Exception:
            logger.exception("Variant %d failed; skipping", intent.index)
            continue

        # Delay between runs to avoid rate limits
        if intent.index < len(intents) - 1:
            if config.verbose:
                logger.info("Waiting %.0fs before next variant...", config.delay_between_runs)
            await asyncio.sleep(config.delay_between_runs)

    # Rank variants (need at least 2)
    if len(image_paths) >= 2:
        if config.verbose:
            logger.info("Ranking %d variants...", len(image_paths))
        result.ranking = rank_variants(
            image_paths=image_paths,
            strategies=strategies,
            caption=caption,
            source_text=source_text,
            api_key=api_key,
        )
        winner_index = result.ranking.winner_index
    elif image_paths:
        winner_index = 0
    else:
        logger.error("No variants generated successfully")
        return result

    # Find the winner's image path
    winner_path = None
    for v in result.variants:
        if v["index"] == winner_index:
            winner_path = v["image_path"]
            break
    if winner_path is None:
        winner_path = image_paths[0]

    # Optionally refine the winner
    if config.refine_winner and winner_path:
        if config.verbose:
            logger.info("Refining winner (variant %d)...", winner_index)

        winner_intent = intents[winner_index] if winner_index < len(intents) else intents[0]
        refined_path = str(out_path / f"{output_stem}_refined.png")

        try:
            await _generate_with_retry(
                source_text=source_text,
                intent=winner_intent,
                settings_factory=lambda _it=config.refinement_iterations: settings_factory(_it),
                variant_path=refined_path,
            )
            result.refined_image_path = refined_path
            winner_path = refined_path
        except Exception:
            logger.exception("Refinement failed; using unrefined winner")

    # Copy winner to final output
    final_path = str(out_path / f"{output_stem}_final.png")
    shutil.copy2(winner_path, final_path)

    if config.verbose:
        logger.info("Final output: %s", final_path)

    return result


async def _generate_with_retry(
    source_text: str,
    intent: VariantIntent,
    settings_factory: Callable[[int], Any],
    variant_path: str,
) -> Any:
    """Generate a single variant with exponential backoff on rate limits.

    Args:
        source_text: Source text to visualize.
        intent: The variant intent to generate.
        settings_factory: Callable returning Settings for given iteration count.
        variant_path: Output path for the generated image.

    Returns:
        PaperBanana pipeline result.

    Raises:
        Exception: If all retries are exhausted.
    """
    from paperbanana import DiagramType, GenerationInput, PaperBananaPipeline

    gen_input = GenerationInput(
        source_context=source_text,
        communicative_intent=intent.communicative_intent,
        diagram_type=DiagramType.METHODOLOGY,
    )
    settings = settings_factory(1)
    pipeline = PaperBananaPipeline(settings=settings)

    backoff = _INITIAL_BACKOFF
    last_exc: Exception | None = None

    for attempt in range(_MAX_RETRIES + 1):
        try:
            gen_result = await pipeline.generate(gen_input)

            # Save image
            out = Path(variant_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            if hasattr(gen_result, "image_path") and gen_result.image_path:
                shutil.copy2(gen_result.image_path, out)
            elif hasattr(gen_result, "image_data") and gen_result.image_data:
                out.write_bytes(gen_result.image_data)

            return gen_result

        except Exception as exc:
            last_exc = exc
            exc_str = str(exc).lower()
            is_rate_limit = "429" in exc_str or "resourceexhausted" in exc_str
            if is_rate_limit and attempt < _MAX_RETRIES:
                logger.warning(
                    "Rate limited (attempt %d/%d), backing off %.0fs",
                    attempt + 1,
                    _MAX_RETRIES + 1,
                    backoff,
                )
                await asyncio.sleep(backoff)
                backoff *= 2
            else:
                raise

    raise last_exc  # type: ignore[misc]


def _extract_scores(gen_result: Any) -> dict[str, float] | None:
    """Extract evaluation scores from a PaperBanana result, if available."""
    if not hasattr(gen_result, "evaluation") or not gen_result.evaluation:
        return None
    ev = gen_result.evaluation
    return {
        "faithfulness": getattr(ev, "faithfulness", 0.0),
        "readability": getattr(ev, "readability", 0.0),
        "conciseness": getattr(ev, "conciseness", 0.0),
        "aesthetics": getattr(ev, "aesthetics", 0.0),
    }


def build_variant_review_log(
    result: MultiVariantResult,
    source_text: str,
    caption: str,
    doc_type: str = "default",
    brand_enabled: bool = True,
) -> dict:
    """Build a JSON-serializable review log from a multi-variant result.

    Args:
        result: The completed multi-variant result.
        source_text: Original source text.
        caption: Original caption.
        doc_type: Document type for threshold lookup.
        brand_enabled: Whether brand styling was applied.

    Returns:
        Dictionary suitable for JSON serialization and the review tool.
    """
    log: dict[str, Any] = {
        "source_text_preview": source_text[:200],
        "caption": caption,
        "doc_type": doc_type,
        "brand_enabled": brand_enabled,
        "n_variants": len(result.variants),
        "variants": result.variants,
    }

    if result.ranking:
        log["ranking"] = {
            "winner_index": result.ranking.winner_index,
            "rationale": result.ranking.ranking_rationale,
            "scores": [
                {
                    "variant_index": s.variant_index,
                    "strategy": s.strategy,
                    "faithfulness": s.faithfulness,
                    "readability": s.readability,
                    "conciseness": s.conciseness,
                    "aesthetics": s.aesthetics,
                    "composite_score": round(s.composite_score, 4),
                    "rank": s.rank,
                }
                for s in result.ranking.scores
            ],
        }

    if result.refined_image_path:
        log["refined_image_path"] = result.refined_image_path

    return log
