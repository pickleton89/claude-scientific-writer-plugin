"""
Statistics extraction utilities for research paper summarization.

Provides regex-based extraction of statistical values from text:
- P-values
- Confidence intervals
- Sample sizes
- Fold changes
- Hazard ratios, odds ratios
- Effect sizes
- Correlations
"""

import re
from typing import Any

from .schemas import StatisticResult, StatisticType


# Deduplication window: statistics within this many characters are considered duplicates
DEDUP_POSITION_WINDOW = 5


# Pattern definitions: (regex_pattern, normalization_template, stat_type)
STAT_PATTERNS: dict[StatisticType, list[tuple[str, str]]] = {
    StatisticType.P_VALUE: [
        (r"[pP]\s*[<=]\s*(0?\.\d+)", "p = {0}"),
        (r"[pP]\s*<\s*(0\.0+1)", "p < {0}"),
        (r"[pP]\s*=\s*(0?\.\d+)", "p = {0}"),
        (r"[pP]\s*[<>]\s*(0?\.\d+)", "p {op} {0}"),
        (r"[pP]-?value\s*[=:]\s*(0?\.\d+)", "p = {0}"),
        (r"significance.{0,20}?([pP]\s*[<=]\s*0?\.\d+)", "{0}"),
    ],
    StatisticType.CONFIDENCE_INTERVAL: [
        (r"(\d+)%\s*CI[:\s]+\[?([\d.]+)\s*[-–]\s*([\d.]+)\]?", "{0}% CI: {1}–{2}"),
        (r"(\d+)%\s*confidence interval[:\s]+([\d.]+)\s*[-–]\s*([\d.]+)", "{0}% CI: {1}–{2}"),
        (r"CI[:\s]+\[?([\d.]+)\s*[-–]\s*([\d.]+)\]?", "95% CI: {0}–{1}"),
        (r"\(([\d.]+)\s*[-–]\s*([\d.]+)\)", "({0}–{1})"),
    ],
    StatisticType.SAMPLE_SIZE: [
        (r"[nN]\s*=\s*(\d+(?:,\d+)?)", "n = {0}"),
        (r"[nN]\s*=\s*(\d+)/group", "n = {0}/group"),
        (r"(\d+(?:,\d+)?)\s+(?:patients|subjects|participants|individuals)", "n = {0}"),
        (r"(\d+(?:,\d+)?)\s+(?:mice|rats|animals|cells|samples)", "n = {0}"),
        (r"sample size[:\s]+(\d+(?:,\d+)?)", "n = {0}"),
        (r"cohort of (\d+(?:,\d+)?)", "n = {0}"),
    ],
    StatisticType.FOLD_CHANGE: [
        (r"(\d+\.?\d*)\s*-?\s*fold\s+(increase|decrease|change|higher|lower)", "{0}-fold {1}"),
        (r"(\d+\.?\d*)\s*[×x]\s*(increase|decrease|change)?", "{0}×"),
        (r"increased\s+(\d+\.?\d*)\s*-?\s*fold", "{0}-fold increase"),
        (r"decreased\s+(\d+\.?\d*)\s*-?\s*fold", "{0}-fold decrease"),
    ],
    StatisticType.HAZARD_RATIO: [
        (r"HR\s*[=:]\s*(\d+\.?\d*)", "HR = {0}"),
        (r"hazard ratio[:\s]+(\d+\.?\d*)", "HR = {0}"),
        (r"HR\s*(\d+\.?\d*)\s*\(", "HR = {0}"),
    ],
    StatisticType.ODDS_RATIO: [
        (r"OR\s*[=:]\s*(\d+\.?\d*)", "OR = {0}"),
        (r"odds ratio[:\s]+(\d+\.?\d*)", "OR = {0}"),
        (r"OR\s*(\d+\.?\d*)\s*\(", "OR = {0}"),
    ],
    StatisticType.PERCENT_CHANGE: [
        (r"(\d+\.?\d*)\s*%\s+(reduction|increase|decrease|improvement|decline)", "{0}% {1}"),
        (r"(\d+\.?\d*)\s*%\s+of\s+(?:patients|subjects|cases)", "{0}%"),
        (r"reduced\s+(?:by\s+)?(\d+\.?\d*)\s*%", "{0}% reduction"),
        (r"increased\s+(?:by\s+)?(\d+\.?\d*)\s*%", "{0}% increase"),
    ],
    StatisticType.EFFECT_SIZE: [
        (r"Cohen'?s?\s*[dD]\s*[=:]\s*(\d+\.?\d*)", "Cohen's d = {0}"),
        (r"effect size[:\s]+(\d+\.?\d*)", "effect size = {0}"),
        (r"[dD]\s*=\s*(\d+\.?\d*)", "d = {0}"),
        (r"η²\s*[=:]\s*(\d+\.?\d*)", "η² = {0}"),
        (r"eta.?squared\s*[=:]\s*(\d+\.?\d*)", "η² = {0}"),
    ],
    StatisticType.CORRELATION: [
        (r"[rR]\s*=\s*(-?\d+\.?\d*)", "r = {0}"),
        (r"correlation[:\s]+(-?\d+\.?\d*)", "r = {0}"),
        (r"Pearson'?s?\s*r\s*[=:]\s*(-?\d+\.?\d*)", "r = {0}"),
        (r"Spearman'?s?\s*r?h?o?\s*[=:]\s*(-?\d+\.?\d*)", "ρ = {0}"),
        (r"ρ\s*[=:]\s*(-?\d+\.?\d*)", "ρ = {0}"),
    ],
    StatisticType.MEAN_SD: [
        (r"(\d+\.?\d*)\s*±\s*(\d+\.?\d*)", "{0} ± {1}"),
        (r"mean\s*[=:]\s*(\d+\.?\d*)\s*(?:±|SD)\s*(\d+\.?\d*)", "{0} ± {1}"),
        (r"(\d+\.?\d*)\s*\(SD\s*(\d+\.?\d*)\)", "{0} (SD {1})"),
    ],
}


def normalize_statistic(match: re.Match[str], template: str) -> str:
    """
    Normalize a matched statistic to a standard format.

    Args:
        match: The regex match object
        template: The normalization template with {0}, {1}, etc. placeholders

    Returns:
        Normalized string representation
    """
    groups = match.groups()

    # Handle special case for operator in p-value
    if "{op}" in template:
        raw = match.group(0)
        if "<" in raw:
            template = template.replace("{op}", "<")
        elif ">" in raw:
            template = template.replace("{op}", ">")
        else:
            template = template.replace("{op}", "=")

    try:
        # Clean up groups - remove commas from numbers
        cleaned_groups = tuple(g.replace(",", "") if g else g for g in groups)
        return template.format(*cleaned_groups)
    except (IndexError, KeyError):
        # Fall back to raw match if template fails
        return match.group(0)


def extract_statistics(
    text: str,
    context_chars: int = 50,
    deduplicate: bool = True,
) -> list[StatisticResult]:
    """
    Extract all statistics from text.

    Args:
        text: The text to search
        context_chars: Number of characters of context to capture on each side
        deduplicate: Remove duplicate matches at the same position

    Returns:
        List of StatisticResult objects, sorted by position
    """
    stats: list[StatisticResult] = []

    for stat_type, patterns in STAT_PATTERNS.items():
        for pattern, template in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Extract context
                start = max(0, match.start() - context_chars)
                end = min(len(text), match.end() + context_chars)
                context = text[start:end].replace("\n", " ").strip()

                # Normalize the value
                normalized = normalize_statistic(match, template)

                stats.append(
                    StatisticResult(
                        stat_type=stat_type,
                        value=match.group(0),
                        normalized=normalized,
                        context=f"...{context}...",
                        position=match.start(),
                    )
                )

    # Sort by position
    stats.sort(key=lambda s: s.position)

    # Remove duplicates at same position if requested
    if deduplicate:
        seen_positions: set[int] = set()
        unique_stats: list[StatisticResult] = []
        for stat in stats:
            # Group positions within DEDUP_POSITION_WINDOW chars to catch overlapping matches
            position_key = stat.position // DEDUP_POSITION_WINDOW * DEDUP_POSITION_WINDOW
            if position_key not in seen_positions:
                unique_stats.append(stat)
                seen_positions.add(position_key)
        stats = unique_stats

    return stats


def summarize_statistics(stats: list[StatisticResult]) -> dict[str, Any]:
    """
    Generate summary counts by statistic type.

    Args:
        stats: List of extracted statistics

    Returns:
        Dictionary with counts and examples by type
    """
    summary: dict[str, Any] = {
        "total": len(stats),
        "by_type": {},
    }

    for stat in stats:
        type_name = stat.stat_type.value
        if type_name not in summary["by_type"]:
            summary["by_type"][type_name] = {
                "count": 0,
                "examples": [],
            }
        summary["by_type"][type_name]["count"] += 1
        # Keep up to 3 examples
        if len(summary["by_type"][type_name]["examples"]) < 3:
            summary["by_type"][type_name]["examples"].append(stat.normalized)

    return summary


def has_sufficient_statistics(
    text: str,
    min_count: int = 3,
    required_types: list[StatisticType] | None = None,
) -> tuple[bool, int, dict[str, int]]:
    """
    Check if text contains sufficient statistical content.

    Args:
        text: The text to check
        min_count: Minimum number of statistics required
        required_types: Optional list of required statistic types

    Returns:
        Tuple of (passes, count, type_counts)
    """
    stats = extract_statistics(text)
    count = len(stats)

    type_counts = {}
    for stat in stats:
        type_name = stat.stat_type.value
        type_counts[type_name] = type_counts.get(type_name, 0) + 1

    # Check minimum count
    passes = count >= min_count

    # Check required types if specified
    if required_types and passes:
        for req_type in required_types:
            if req_type.value not in type_counts:
                passes = False
                break

    return passes, count, type_counts
