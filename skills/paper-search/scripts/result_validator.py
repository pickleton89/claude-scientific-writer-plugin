"""
Result Validation Module for Paper Search.

Provides deterministic feedback on search results to help users
refine their queries without relying on LLM judgment.

Phase 3 Implementation - Determinism Audit
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResultStatus(Enum):
    """Status classification for search results."""

    NONE = "none"  # Zero results
    TOO_FEW = "too_few"  # Less than minimum threshold
    GOOD = "good"  # Within acceptable range
    TOO_MANY = "too_many"  # Hit max limit, may be truncated
    EXHAUSTIVE = "exhaustive"  # Full topic coverage


@dataclass
class SearchFeedback:
    """
    Deterministic feedback on search results.

    Provides actionable suggestions based on result count
    without requiring LLM interpretation.
    """

    result_count: int
    status: ResultStatus
    suggestions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    query_quality_score: float = 0.0
    estimated_total: int | None = None

    def is_acceptable(self) -> bool:
        """Check if results are in acceptable range."""
        return self.status in (ResultStatus.GOOD, ResultStatus.EXHAUSTIVE)

    def needs_refinement(self) -> bool:
        """Check if query should be refined."""
        return self.status in (ResultStatus.NONE, ResultStatus.TOO_FEW)

    def needs_narrowing(self) -> bool:
        """Check if query is too broad."""
        return self.status == ResultStatus.TOO_MANY

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "result_count": self.result_count,
            "status": self.status.value,
            "suggestions": self.suggestions,
            "warnings": self.warnings,
            "query_quality_score": self.query_quality_score,
            "estimated_total": self.estimated_total,
            "is_acceptable": self.is_acceptable(),
        }


@dataclass
class ResultThresholds:
    """Configurable thresholds for result count analysis."""

    min_acceptable: int = 5  # Below this is "too few"
    max_comfortable: int = 100  # Above this starts to feel excessive
    truncation_warning: int = 50  # Warn about possible truncation above this


# Default thresholds
DEFAULT_THRESHOLDS = ResultThresholds()


def analyze_result_count(
    count: int,
    max_requested: int,
    query: str,
    source: str | list[str],
    thresholds: ResultThresholds | None = None,
    estimated_total: int | None = None,
) -> SearchFeedback:
    """
    Provide deterministic feedback on result count.

    Analyzes the search results and provides actionable suggestions
    based on the count relative to expected ranges.

    Args:
        count: Number of results returned
        max_requested: Maximum results requested in the search
        query: The search query used
        source: Database(s) searched
        thresholds: Custom thresholds (uses defaults if not provided)
        estimated_total: If API provided total count estimate

    Returns:
        SearchFeedback with status and suggestions
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    suggestions: list[str] = []
    warnings: list[str] = []

    # Normalize source to list
    sources = [source] if isinstance(source, str) else source

    # Determine status based on count
    if count == 0:
        status = ResultStatus.NONE
        suggestions = _get_zero_result_suggestions(query, sources)
        quality_score = 0.0

    elif count < thresholds.min_acceptable:
        status = ResultStatus.TOO_FEW
        suggestions = _get_few_result_suggestions(count, query, sources)
        quality_score = 0.3

    elif count >= max_requested:
        status = ResultStatus.TOO_MANY
        suggestions = _get_many_result_suggestions(query, sources)
        warnings.append(f"Results may be truncated at {max_requested}")
        if estimated_total and estimated_total > max_requested:
            warnings.append(
                f"Estimated {estimated_total} total matches; only {max_requested} returned"
            )
        quality_score = 0.6

    elif count >= thresholds.max_comfortable:
        # Good count but on the high side
        status = ResultStatus.GOOD
        suggestions = [
            "Results look comprehensive",
            "Consider narrowing if looking for specific papers",
        ]
        quality_score = 0.8

    else:
        status = ResultStatus.GOOD
        quality_score = 1.0

    # Add truncation warning if applicable
    if count >= thresholds.truncation_warning and count < max_requested:
        warnings.append("Large result set - consider if all results are needed")

    return SearchFeedback(
        result_count=count,
        status=status,
        suggestions=suggestions,
        warnings=warnings,
        query_quality_score=quality_score,
        estimated_total=estimated_total,
    )


def _get_zero_result_suggestions(query: str, sources: list[str]) -> list[str]:
    """Get suggestions when zero results returned."""
    suggestions = [
        "Remove field constraints (e.g., [Title] tags) to search all fields",
        "Use broader terms or add synonyms with OR operators",
        "Expand date range if filtering by date",
        "Check spelling of technical terms",
    ]

    # Source-specific suggestions
    if "pubmed" in sources:
        suggestions.append("Try removing publication type filters")
        suggestions.append("Check if MeSH terms are spelled correctly")

    if "semantic" in sources or "semantic_scholar" in sources:
        suggestions.append("Semantic Scholar may not index all papers - try PubMed")

    if "biorxiv" in sources:
        suggestions.append("bioRxiv only has preprints - try PubMed for published work")

    # Query-specific suggestions
    if "[" in query and "]" in query:
        suggestions.insert(0, "Field tags detected - try searching without field restrictions")

    if " AND " in query.upper():
        suggestions.insert(0, "Query has AND operators - try removing some constraints")

    return suggestions


def _get_few_result_suggestions(
    count: int, query: str, sources: list[str]
) -> list[str]:
    """Get suggestions when too few results returned."""
    suggestions = [
        f"Only {count} results found - consider broadening the search",
        "Add synonyms using OR: term1 OR term2 OR term3",
        "Remove restrictive filters (publication type, date range)",
    ]

    # Check for overly specific query patterns
    if query.count(" AND ") >= 2:
        suggestions.insert(0, "Query may be too specific - try removing AND clauses")

    if "[Author]" in query or "[AU]" in query:
        suggestions.append("Author-filtered search - consider searching by topic instead")

    # Source-specific
    if len(sources) == 1:
        suggestions.append("Try searching additional databases for more coverage")

    return suggestions


def _get_many_result_suggestions(query: str, sources: list[str]) -> list[str]:
    """Get suggestions when results may be truncated."""
    suggestions = [
        "Results may be truncated - consider narrowing the search",
        "Add more specific terms with AND operators",
        "Narrow date range to recent years",
        "Add publication type filter (e.g., Review, Clinical Trial)",
    ]

    # Source-specific suggestions
    if "pubmed" in sources:
        suggestions.append("Use MeSH terms for more precise filtering")
        suggestions.append("Filter by journal or author for focused results")

    if "semantic" in sources or "semantic_scholar" in sources:
        suggestions.append("Filter by minimum citation count to find influential papers")
        suggestions.append("Use fields_of_study filter for domain-specific results")

    # Query-specific
    if " OR " in query.upper() and " AND " not in query.upper():
        suggestions.insert(0, "Query is broad (OR without AND) - add constraining terms")

    return suggestions


@dataclass
class ResultQualityMetrics:
    """Metrics for assessing result quality beyond count."""

    has_recent_papers: bool = False  # Papers from last 2 years
    has_highly_cited: bool = False  # Papers with significant citations
    has_reviews: bool = False  # Review articles present
    source_diversity: float = 0.0  # Coverage across databases
    year_span: int = 0  # Range of publication years
    avg_citation_count: float = 0.0


def analyze_result_quality(
    results: list[dict[str, Any]],
    current_year: int = 2026,
) -> ResultQualityMetrics:
    """
    Analyze the quality of search results.

    Provides metrics beyond simple count to help assess
    whether the results are useful.

    Args:
        results: List of result dictionaries with metadata
        current_year: Current year for recency calculation

    Returns:
        ResultQualityMetrics with quality indicators
    """
    if not results:
        return ResultQualityMetrics()

    years: list[int] = []
    citations: list[int] = []
    sources: set[str] = set()
    has_reviews = False
    has_recent = False
    has_highly_cited = False

    for result in results:
        # Extract year
        year = result.get("year") or result.get("publication_year")
        if year:
            try:
                year_int = int(year)
                years.append(year_int)
                if year_int >= current_year - 2:
                    has_recent = True
            except (ValueError, TypeError):
                pass

        # Extract citations
        cite_count = result.get("citation_count") or result.get("citations", 0)
        if cite_count:
            try:
                cite_int = int(cite_count)
                citations.append(cite_int)
                if cite_int >= 100:
                    has_highly_cited = True
            except (ValueError, TypeError):
                pass

        # Check for reviews
        pub_type = result.get("publication_type", "")
        if "review" in str(pub_type).lower():
            has_reviews = True

        # Track sources
        source = result.get("source", "unknown")
        sources.add(source)

    # Calculate metrics
    year_span = max(years) - min(years) if years else 0
    avg_citations = sum(citations) / len(citations) if citations else 0.0
    source_diversity = len(sources) / 3.0  # Normalize by expected source count

    return ResultQualityMetrics(
        has_recent_papers=has_recent,
        has_highly_cited=has_highly_cited,
        has_reviews=has_reviews,
        source_diversity=min(1.0, source_diversity),
        year_span=year_span,
        avg_citation_count=avg_citations,
    )


def get_quality_summary(metrics: ResultQualityMetrics) -> str:
    """Get a human-readable summary of result quality."""
    points: list[str] = []

    if metrics.has_recent_papers:
        points.append("includes recent papers")
    else:
        points.append("no recent papers (last 2 years)")

    if metrics.has_highly_cited:
        points.append("includes highly-cited work")

    if metrics.has_reviews:
        points.append("includes review articles")

    if metrics.year_span > 10:
        points.append(f"spans {metrics.year_span} years of research")

    if metrics.avg_citation_count > 50:
        points.append(f"avg {metrics.avg_citation_count:.0f} citations per paper")

    if metrics.source_diversity >= 0.67:
        points.append("good source diversity")
    elif metrics.source_diversity < 0.34:
        points.append("results from single source")

    return "; ".join(points) if points else "no quality indicators available"


@dataclass
class ValidationReport:
    """Complete validation report for a search."""

    feedback: SearchFeedback
    quality: ResultQualityMetrics
    query_used: str
    sources_searched: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "feedback": self.feedback.to_dict(),
            "quality": {
                "has_recent_papers": self.quality.has_recent_papers,
                "has_highly_cited": self.quality.has_highly_cited,
                "has_reviews": self.quality.has_reviews,
                "source_diversity": self.quality.source_diversity,
                "year_span": self.quality.year_span,
                "avg_citation_count": self.quality.avg_citation_count,
            },
            "query_used": self.query_used,
            "sources_searched": self.sources_searched,
            "quality_summary": get_quality_summary(self.quality),
        }


def validate_search_results(
    results: list[dict[str, Any]],
    query: str,
    sources: str | list[str],
    max_requested: int = 20,
    estimated_total: int | None = None,
) -> ValidationReport:
    """
    Complete validation of search results.

    Combines count analysis and quality metrics into
    a comprehensive report.

    Args:
        results: Search results
        query: Query used
        sources: Sources searched
        max_requested: Max results requested
        estimated_total: Total estimated matches from API

    Returns:
        ValidationReport with all analysis
    """
    source_list = [sources] if isinstance(sources, str) else sources

    feedback = analyze_result_count(
        count=len(results),
        max_requested=max_requested,
        query=query,
        source=source_list,
        estimated_total=estimated_total,
    )

    quality = analyze_result_quality(results)

    return ValidationReport(
        feedback=feedback,
        quality=quality,
        query_used=query,
        sources_searched=source_list,
    )
