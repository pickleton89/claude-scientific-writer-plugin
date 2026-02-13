"""Generate variant communicative intents for multi-variant figure generation.

Each variant uses a different strategy to rewrite the figure caption,
producing diverse visual interpretations of the same source content.
Variant 1 is always FAITHFUL (original caption verbatim); additional
variants use Gemini Flash to generate strategy-specific rewrites.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Add shared utilities to path
_SHARED_DIR = Path(__file__).resolve().parent.parent.parent / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

# Add local utils to path
_UTILS_DIR = Path(__file__).resolve().parent / "utils"
if str(_UTILS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_UTILS_DIR.parent))


class VariantStrategy(Enum):
    """Strategy controlling how a variant caption is generated."""

    FAITHFUL = "faithful"
    ENHANCED = "enhanced"
    ALT_COMPOSITION = "alt_composition"
    STYLE_VARIATION = "style_variation"
    BOLD_CREATIVE = "bold_creative"


VARIANT_PRESETS: dict[int, list[VariantStrategy]] = {
    1: [VariantStrategy.FAITHFUL],
    2: [VariantStrategy.FAITHFUL, VariantStrategy.ENHANCED],
    3: [VariantStrategy.FAITHFUL, VariantStrategy.ENHANCED, VariantStrategy.ALT_COMPOSITION],
    4: [
        VariantStrategy.FAITHFUL,
        VariantStrategy.ENHANCED,
        VariantStrategy.ALT_COMPOSITION,
        VariantStrategy.STYLE_VARIATION,
    ],
    5: [
        VariantStrategy.FAITHFUL,
        VariantStrategy.ENHANCED,
        VariantStrategy.ALT_COMPOSITION,
        VariantStrategy.STYLE_VARIATION,
        VariantStrategy.BOLD_CREATIVE,
    ],
}

_STRATEGY_PROMPTS: dict[VariantStrategy, str] = {
    VariantStrategy.ENHANCED: (
        "Rewrite this figure caption to add more specific visual detail, "
        "scientific precision, and elevated language while maintaining the "
        "same core meaning: {caption}\n\nContext: {context}"
    ),
    VariantStrategy.ALT_COMPOSITION: (
        "Rewrite this figure caption to suggest a fundamentally different "
        "visual layout or composition while conveying the same information: "
        "{caption}\n\nContext: {context}"
    ),
    VariantStrategy.STYLE_VARIATION: (
        "Rewrite this figure caption to emphasize a different visual style "
        "(e.g., more diagrammatic, more infographic-like, more schematic) "
        "while maintaining scientific accuracy: {caption}\n\nContext: {context}"
    ),
    VariantStrategy.BOLD_CREATIVE: (
        "Rewrite this figure caption with a bold, unconventional visual "
        "approach that still maintains scientific rigor: {caption}\n\n"
        "Context: {context}"
    ),
}

_STRATEGY_DESCRIPTIONS: dict[VariantStrategy, str] = {
    VariantStrategy.FAITHFUL: "Original caption, no modification",
    VariantStrategy.ENHANCED: "Enhanced visual detail and scientific precision",
    VariantStrategy.ALT_COMPOSITION: "Alternative visual layout and composition",
    VariantStrategy.STYLE_VARIATION: "Different visual style emphasis",
    VariantStrategy.BOLD_CREATIVE: "Bold, unconventional visual approach",
}


@dataclass
class VariantIntent:
    """A single variant's generation intent."""

    index: int
    strategy: VariantStrategy
    communicative_intent: str
    strategy_description: str


def generate_variant_intents(
    caption: str,
    source_text: str,
    n: int = 3,
    api_key: str | None = None,
) -> list[VariantIntent]:
    """Generate variant communicative intents for multi-variant figure generation.

    Args:
        caption: Original figure caption / communicative intent.
        source_text: Source text context for the figure.
        n: Number of variants to generate (clamped to 1-5).
        api_key: Google API key. If None, loaded from environment.

    Returns:
        List of VariantIntent objects, one per variant.
    """
    n = max(1, min(n, 5))
    strategies = VARIANT_PRESETS[n]

    intents: list[VariantIntent] = []

    for i, strategy in enumerate(strategies):
        if strategy == VariantStrategy.FAITHFUL:
            intents.append(
                VariantIntent(
                    index=i,
                    strategy=strategy,
                    communicative_intent=caption,
                    strategy_description=_STRATEGY_DESCRIPTIONS[strategy],
                )
            )
        else:
            rewritten = _rewrite_caption(caption, source_text, strategy, api_key)
            intents.append(
                VariantIntent(
                    index=i,
                    strategy=strategy,
                    communicative_intent=rewritten,
                    strategy_description=_STRATEGY_DESCRIPTIONS[strategy],
                )
            )

    return intents


def _rewrite_caption(
    caption: str,
    source_text: str,
    strategy: VariantStrategy,
    api_key: str | None,
) -> str:
    """Rewrite a caption using Gemini Flash for the given strategy.

    Args:
        caption: Original caption text.
        source_text: Source context (truncated to 500 chars for prompt).
        strategy: The variant strategy to apply.
        api_key: Google API key. Loaded from environment if None.

    Returns:
        Rewritten caption string.
    """
    if api_key is None:
        from api_utils import load_api_key

        api_key = load_api_key(env_var="GOOGLE_API_KEY", caller_file=__file__)

    from google import genai

    client = genai.Client(api_key=api_key)

    prompt_template = _STRATEGY_PROMPTS[strategy]
    prompt = prompt_template.format(caption=caption, context=source_text[:500])

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()
