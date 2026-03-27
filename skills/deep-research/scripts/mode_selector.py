#!/usr/bin/env python3
"""
Mode selection for the deep-research pipeline.

Encodes the SKILL.md decision tree (lines 39-66) as priority-ordered keyword
matching. The LLM may override for ambiguous or context-dependent cases, but
this script provides a deterministic default.

Input JSON: {"user_input": "...", "has_provided_text": false}
Output: mode selection with confidence and matched keywords.
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from thresholds import ALL_MODES


@dataclass
class ModeSelection:
    """Result of deterministic mode selection."""

    selected_mode: str
    confidence: str  # "high", "medium", "low"
    matched_keywords: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Priority-ordered keyword patterns (highest priority first)
# Order mirrors the SKILL.md decision tree:
#   systematic-review → hypothesis → fact-check → socratic → quick →
#   lit-review → review (requires text) → full (default)
# ---------------------------------------------------------------------------

MODE_KEYWORDS: dict[str, list[str]] = {
    "systematic-review": [
        r"systematic\s+review",
        r"PRISMA",
        r"meta[\-\s]?analysis",
        r"forest\s+plot",
        r"risk\s+of\s+bias",
        r"PROSPERO",
    ],
    "hypothesis": [
        r"hypothes[ie]s",
        r"testable\s+prediction",
        r"competing\s+explanations?",
        r"generate\s+hypothes",
        r"propose\s+mechanism",
    ],
    "fact-check": [
        r"fact[\-\s]?check",
        r"verify\s+(this\s+)?claim",
        r"is\s+it\s+true\s+that",
        r"check\s+(if|whether)\s+.+\s+true",
        r"debunk",
    ],
    "socratic": [
        r"guide\s+my\s+research",
        r"help\s+me\s+think",
        r"walk\s+me\s+through",
        r"let'?s\s+explore",
        r"brainstorm\s+with\s+me",
    ],
    "quick": [
        r"find\s+papers?\b",
        r"search\s+(pubmed|biorxiv|articles|papers)",
        r"quick\s+(search|look|review|summary)",
        r"any\s+papers?\s+on",
        r"look\s+up\s+(recent\s+)?(papers?|articles?|studies)",
    ],
    "lit-review": [
        r"literature\s+review",
        r"what\s+does\s+the\s+literature\s+say",
        r"review\s+(of\s+)?the\s+(existing\s+)?literature",
        r"survey\s+(of\s+)?the\s+field",
        r"state\s+of\s+the\s+(art|field|science)",
        r"scoping\s+review",
    ],
}

# Indicators for exploratory/vague input that suggests socratic mode
VAGUE_INDICATORS: list[str] = [
    r"^I('m|\s+am)\s+(interested|curious|wondering)",
    r"^what\s+should\s+I\s+(study|research|investigate)",
    r"^where\s+do\s+I\s+(start|begin)",
    r"^I\s+don'?t\s+know\s+(where|how)\s+to",
    r"^can\s+you\s+help\s+me\s+(figure|think|understand)",
    r"^how\s+would\s+I\s+approach",
]


def select_mode(user_input: str, has_provided_text: bool = False) -> ModeSelection:
    """
    Select the pipeline mode from user input.

    Priority-ordered keyword matching. First match wins (highest priority mode).
    "review" mode requires has_provided_text=True plus a "review" keyword.
    Falls back to "full" if nothing matches.

    Args:
        user_input: The user's research request text.
        has_provided_text: Whether the user provided a document/text to review.

    Returns:
        ModeSelection with mode, confidence, matched keywords, and notes.
    """
    text = user_input.strip()
    if not text:
        return ModeSelection(
            selected_mode="full",
            confidence="low",
            notes=["Empty input — defaulting to full mode"],
        )

    # Check priority-ordered modes
    for mode, patterns in MODE_KEYWORDS.items():
        matched = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matched.append(pattern)
        if matched:
            return ModeSelection(
                selected_mode=mode,
                confidence="high",
                matched_keywords=matched,
            )

    # Check "review" mode (requires provided text)
    review_patterns = [
        r"review\s+this",
        r"critique\s+this",
        r"evaluate\s+this",
        r"assess\s+this\s+(manuscript|paper|draft|text)",
        r"give\s+(me\s+)?feedback\s+on",
    ]
    review_matched = []
    for pattern in review_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            review_matched.append(pattern)
    if review_matched:
        if has_provided_text:
            return ModeSelection(
                selected_mode="review",
                confidence="high",
                matched_keywords=review_matched,
            )
        else:
            return ModeSelection(
                selected_mode="review",
                confidence="medium",
                matched_keywords=review_matched,
                notes=["Review keywords detected but no text provided — confirm with user"],
            )

    # Check vague/exploratory indicators → socratic
    vague_matched = []
    for pattern in VAGUE_INDICATORS:
        if re.search(pattern, text, re.IGNORECASE):
            vague_matched.append(pattern)
    if vague_matched:
        return ModeSelection(
            selected_mode="socratic",
            confidence="medium",
            matched_keywords=vague_matched,
            notes=["Exploratory/vague input detected — suggesting socratic mode"],
        )

    # Default → full
    return ModeSelection(
        selected_mode="full",
        confidence="low",
        notes=["No keyword match — defaulting to full mode"],
    )


def select_mode_from_json(data: dict) -> dict:
    """
    JSON-friendly wrapper for select_mode.

    Args:
        data: Dict with "user_input" (str) and optional "has_provided_text" (bool).

    Returns:
        Dict with selection results.
    """
    result = select_mode(
        user_input=data.get("user_input", ""),
        has_provided_text=data.get("has_provided_text", False),
    )
    return {
        "selected_mode": result.selected_mode,
        "confidence": result.confidence,
        "matched_keywords": result.matched_keywords,
        "notes": result.notes,
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: mode_selector.py <input.json | json_string>")
        print('  e.g.: mode_selector.py \'{"user_input": "systematic review of EGFR"}\'')
        sys.exit(1)

    arg = sys.argv[1]

    # Accept inline JSON or a file path
    if arg.startswith("{"):
        data = json.loads(arg)
    else:
        with open(arg) as f:
            data = json.load(f)

    result = select_mode_from_json(data)

    # Validate against ALL_MODES
    assert result["selected_mode"] in ALL_MODES, (
        f"Bug: selected mode '{result['selected_mode']}' not in ALL_MODES"
    )

    print(f"\nMode: {result['selected_mode']}")
    print(f"Confidence: {result['confidence']}")
    if result["matched_keywords"]:
        print(f"Matched: {', '.join(result['matched_keywords'])}")
    for note in result["notes"]:
        print(f"  Note: {note}")

    # Also emit JSON for programmatic consumption
    print(f"\n{json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()
