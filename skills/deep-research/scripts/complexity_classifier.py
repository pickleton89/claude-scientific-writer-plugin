#!/usr/bin/env python3
"""
Query-complexity classification for the deep-research pipeline.

Implements Anthropic's "scale effort to query complexity" lesson: a deterministic
heuristic that labels a research question simple / comparative / complex, which
``decomposition_contract.py`` turns into a sub-question fan-out width and a
per-subagent tool-call budget (``thresholds.COMPLEXITY_SCALING``).

The LLM orchestrator may override for context-dependent cases — this is the
deterministic default, mirroring how ``mode_selector.py`` defaults the mode.

Input JSON: {"research_question": "...", "mode": "full"}
Output: complexity level with confidence, matched signals, and the scaling profile.
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from thresholds import COMPLEXITY_LEVELS, complexity_scaling


@dataclass
class ComplexityClassification:
    """Result of deterministic complexity classification."""

    level: str  # "simple" | "comparative" | "complex"
    confidence: str  # "high" | "medium" | "low"
    matched_signals: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Signal patterns
# ---------------------------------------------------------------------------

# Comparative signals — the RQ pits options against each other.
COMPARATIVE_PATTERNS: list[str] = [
    r"\bvs\.?\b",
    r"\bversus\b",
    r"\bcompare[ds]?\b",
    r"\bcomparison\b",
    r"\bcomparative\b",
    r"\bdifference[s]?\s+between\b",
    r"\brelative\s+to\b",
    r"\bhead[\-\s]to[\-\s]head\b",
    r"\bbetter\s+than\b",
    r"\bmore\s+effective\s+than\b",
]

# Complex signals — breadth/depth that warrants decomposition into sub-questions.
COMPLEX_PATTERNS: list[str] = [
    r"\bmechanism[s]?\b",
    r"\blandscape\b",
    r"\bcomprehensive\b",
    r"\bsystematic\s+review\b",
    r"\bmeta[\-\s]?analysis\b",
    r"\bacross\b",
    r"\bvarious\b",
    r"\bmultiple\b",
    r"\bfactors\b",
    r"\bdrivers\b",
    r"\bstrategies\b",
    r"\bpathways?\b",
    r"\binterplay\b",
    r"\band\s+how\b",
    r"\bwhat\s+are\s+the\s+competing\b",
]

# Simple signals — bounded fact lookups.
SIMPLE_PATTERNS: list[str] = [
    r"\bis\s+it\s+true\b",
    r"\bapproved\s+indication",
    r"\bwhat\s+is\s+the\s+(approved|recommended|standard)\b",
    r"\bwhich\s+\w+\s+are\s+(approved|fda[\-\s]approved)\b",
    r"\bas\s+of\s+\d{4}\b",
    r"\bdoes\s+\w+\s+(reduce|increase|cause|prevent)\b",
]

# Modes whose framing biases complexity (a coarse prior; signals can override).
MODE_COMPLEXITY_PRIOR: dict[str, str] = {
    "systematic-review": "complex",
    "full": "complex",
    "hypothesis": "complex",
    "lit-review": "comparative",
    "fact-check": "simple",
    "quick": "simple",
}


def _matches(patterns: list[str], text: str) -> list[str]:
    return [p for p in patterns if re.search(p, text, re.IGNORECASE)]


def classify_complexity(
    research_question: str, mode: str | None = None
) -> ComplexityClassification:
    """
    Classify a research question's complexity.

    Decision order: explicit comparative signals → complex breadth signals →
    simple lookup signals → mode prior → default ``comparative`` (the safe
    middle). A mode prior only *raises* confidence when it agrees with the
    signal-derived level; on disagreement the signals win but confidence drops.

    Args:
        research_question: The RQ text.
        mode: Optional deep-research mode for a coarse prior.

    Returns:
        ComplexityClassification with level, confidence, matched signals, notes.
    """
    text = (research_question or "").strip()
    prior = MODE_COMPLEXITY_PRIOR.get(mode or "", None)

    if not text:
        return ComplexityClassification(
            level=prior or "comparative",
            confidence="low",
            notes=[
                "Empty research question — using mode prior or 'comparative' default"
            ],
        )

    comparative = _matches(COMPARATIVE_PATTERNS, text)
    complex_hits = _matches(COMPLEX_PATTERNS, text)
    simple_hits = _matches(SIMPLE_PATTERNS, text)

    # Comparative is the most specific signal — a head-to-head framing dominates
    # even when breadth words are also present (the breadth lives *within* the
    # comparison).
    if comparative:
        level, matched = "comparative", comparative
    elif complex_hits:
        level, matched = "complex", complex_hits
    elif simple_hits:
        level, matched = "simple", simple_hits
    elif prior:
        return ComplexityClassification(
            level=prior,
            confidence="low",
            matched_signals=[],
            notes=[
                f"No complexity signal in RQ — falling back to mode prior ('{mode}' → {prior})"
            ],
        )
    else:
        return ComplexityClassification(
            level="comparative",
            confidence="low",
            matched_signals=[],
            notes=[
                "No complexity signal and no mode prior — defaulting to 'comparative'"
            ],
        )

    notes: list[str] = []
    confidence = "high"
    if prior and prior != level:
        confidence = "medium"
        notes.append(
            f"RQ signals indicate '{level}' but mode '{mode}' biases toward "
            f"'{prior}' — signals win; confirm with the user if scope feels off."
        )
    return ComplexityClassification(
        level=level,
        confidence=confidence,
        matched_signals=matched,
        notes=notes,
    )


def classify_from_json(data: dict) -> dict:
    """JSON-friendly wrapper for classify_complexity."""
    result = classify_complexity(
        research_question=data.get("research_question", ""),
        mode=data.get("mode"),
    )
    return {
        "level": result.level,
        "confidence": result.confidence,
        "matched_signals": result.matched_signals,
        "notes": result.notes,
        "scaling": complexity_scaling(result.level),
    }


def main() -> None:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: complexity_classifier.py <input.json | json_string>")
        print(
            "  e.g.: complexity_classifier.py "
            '\'{"research_question": "X vs Y for Z", "mode": "full"}\''
        )
        sys.exit(1)

    arg = sys.argv[1]
    data = json.loads(arg) if arg.startswith("{") else json.load(open(arg))

    result = classify_from_json(data)
    assert result["level"] in COMPLEXITY_LEVELS, (
        f"Bug: level '{result['level']}' not in COMPLEXITY_LEVELS"
    )

    print(f"\nComplexity: {result['level']}")
    print(f"Confidence: {result['confidence']}")
    if result["matched_signals"]:
        print(f"Matched: {', '.join(result['matched_signals'])}")
    for note in result["notes"]:
        print(f"  Note: {note}")
    print(f"\n{json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()
