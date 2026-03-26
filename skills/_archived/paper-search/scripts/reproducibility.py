"""
Reproducibility Module for Paper Search.

Provides deterministic hashing and logging for search reproducibility.
Enables exact recreation of searches and verification of results.

Phase 3 Implementation - Determinism Audit
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SearchSpecification:
    """
    Complete specification of a search for reproducibility.

    Contains all parameters needed to exactly reproduce a search.
    """

    query: str
    sources: list[str]
    max_results: int = 20
    date_start: str | None = None
    date_end: str | None = None
    publication_types: list[str] = field(default_factory=list)
    fields_of_study: list[str] = field(default_factory=list)
    min_citations: int | None = None
    open_access_only: bool = False
    output_format: str = "json"

    # Additional filters
    author_filter: str | None = None
    journal_filter: str | None = None
    exclude_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchSpecification":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_canonical_string(self) -> str:
        """
        Convert to canonical string for hashing.

        Ensures consistent ordering for deterministic hashing.
        """
        # Sort all lists for consistency
        canonical = {
            "query": self.query,
            "sources": sorted(self.sources),
            "max_results": self.max_results,
            "date_start": self.date_start or "",
            "date_end": self.date_end or "",
            "publication_types": sorted(self.publication_types),
            "fields_of_study": sorted(self.fields_of_study),
            "min_citations": self.min_citations if self.min_citations else 0,
            "open_access_only": self.open_access_only,
            "author_filter": self.author_filter or "",
            "journal_filter": self.journal_filter or "",
            "exclude_terms": sorted(self.exclude_terms),
        }
        return json.dumps(canonical, sort_keys=True, separators=(",", ":"))


@dataclass
class SearchHash:
    """
    Hash representation of a search for reproducibility verification.
    """

    hash_value: str
    algorithm: str = "sha256"
    truncated: bool = True
    truncation_length: int = 12

    @classmethod
    def compute(
        cls,
        spec: SearchSpecification,
        truncate: bool = True,
        length: int = 12,
    ) -> "SearchHash":
        """
        Compute hash from search specification.

        Args:
            spec: Search specification to hash
            truncate: Whether to truncate hash for readability
            length: Truncation length (default 12 chars)

        Returns:
            SearchHash instance
        """
        canonical = spec.to_canonical_string()
        full_hash = hashlib.sha256(canonical.encode()).hexdigest()

        hash_value = full_hash[:length] if truncate else full_hash

        return cls(
            hash_value=hash_value,
            algorithm="sha256",
            truncated=truncate,
            truncation_length=length if truncate else 64,
        )

    def __str__(self) -> str:
        return self.hash_value


def compute_search_hash(
    query: str,
    sources: list[str],
    **params: Any,
) -> str:
    """
    Compute a reproducibility hash for a search.

    This is the primary entry point for generating search hashes.

    Args:
        query: Search query
        sources: List of database sources
        **params: Additional search parameters

    Returns:
        12-character hash string
    """
    spec = SearchSpecification(
        query=query,
        sources=sources,
        max_results=params.get("max_results", params.get("max", 20)),
        date_start=params.get("date_start"),
        date_end=params.get("date_end"),
        publication_types=params.get("publication_types", []),
        fields_of_study=params.get("fields_of_study", []),
        min_citations=params.get("min_citations"),
        open_access_only=params.get("open_access_only", False),
        author_filter=params.get("author_filter"),
        journal_filter=params.get("journal_filter"),
        exclude_terms=params.get("exclude_terms", []),
    )

    return SearchHash.compute(spec).hash_value


@dataclass
class ResultHash:
    """Hash of search results for verification."""

    hash_value: str
    result_count: int
    algorithm: str = "sha256"

    @classmethod
    def compute(cls, results: list[dict[str, Any]]) -> "ResultHash":
        """
        Compute hash of search results.

        Uses DOIs/IDs for consistent hashing regardless of metadata variations.
        """
        # Extract stable identifiers
        identifiers = []
        for result in results:
            # Try various ID fields in order of preference
            id_value = (
                result.get("doi")
                or result.get("pmid")
                or result.get("paperId")
                or result.get("id")
                or result.get("title", "")[:50]  # Fallback to title prefix
            )
            identifiers.append(str(id_value))

        # Sort for consistency
        canonical = json.dumps(sorted(identifiers), separators=(",", ":"))
        full_hash = hashlib.sha256(canonical.encode()).hexdigest()

        return cls(
            hash_value=full_hash[:12],
            result_count=len(results),
        )


@dataclass
class ReproducibilityRecord:
    """
    Complete record for reproducing and verifying a search.
    """

    search_spec: SearchSpecification
    search_hash: str
    result_hash: str
    result_count: int
    timestamp: str
    duration_ms: float | None = None
    api_versions: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "search_spec": self.search_spec.to_dict(),
            "search_hash": self.search_hash,
            "result_hash": self.result_hash,
            "result_count": self.result_count,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "api_versions": self.api_versions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReproducibilityRecord":
        """Create from dictionary."""
        return cls(
            search_spec=SearchSpecification.from_dict(data["search_spec"]),
            search_hash=data["search_hash"],
            result_hash=data["result_hash"],
            result_count=data["result_count"],
            timestamp=data["timestamp"],
            duration_ms=data.get("duration_ms"),
            api_versions=data.get("api_versions", {}),
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


def create_reproducibility_record(
    query: str,
    sources: list[str],
    results: list[dict[str, Any]],
    duration_ms: float | None = None,
    **params: Any,
) -> ReproducibilityRecord:
    """
    Create a complete reproducibility record for a search.

    This is the main entry point for recording reproducible searches.

    Args:
        query: Search query
        sources: List of database sources
        results: Search results
        duration_ms: Search duration in milliseconds
        **params: Additional search parameters

    Returns:
        ReproducibilityRecord instance
    """
    spec = SearchSpecification(
        query=query,
        sources=sources,
        max_results=params.get("max_results", params.get("max", 20)),
        date_start=params.get("date_start"),
        date_end=params.get("date_end"),
        publication_types=params.get("publication_types", []),
        fields_of_study=params.get("fields_of_study", []),
        min_citations=params.get("min_citations"),
        open_access_only=params.get("open_access_only", False),
        output_format=params.get("output_format", "json"),
    )

    search_hash = SearchHash.compute(spec)
    result_hash = ResultHash.compute(results)

    return ReproducibilityRecord(
        search_spec=spec,
        search_hash=search_hash.hash_value,
        result_hash=result_hash.hash_value,
        result_count=len(results),
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=duration_ms,
    )


def verify_reproduction(
    original: ReproducibilityRecord,
    new_results: list[dict[str, Any]],
) -> tuple[bool, list[str]]:
    """
    Verify that a new search reproduces the original.

    Args:
        original: Original reproducibility record
        new_results: Results from reproduction attempt

    Returns:
        Tuple of (matches, list of differences)
    """
    differences: list[str] = []

    # Check result count
    if len(new_results) != original.result_count:
        differences.append(
            f"Result count changed: {original.result_count} -> {len(new_results)}"
        )

    # Check result hash
    new_hash = ResultHash.compute(new_results)
    if new_hash.hash_value != original.result_hash:
        differences.append(
            f"Result hash changed: {original.result_hash} -> {new_hash.hash_value}"
        )

    return len(differences) == 0, differences


class ReproducibilityLog:
    """
    Log of reproducibility records for audit trail.
    """

    def __init__(self, log_path: Path | None = None):
        """
        Initialize log.

        Args:
            log_path: Path to log file. If None, logging is disabled.
        """
        self.log_path = log_path
        self._records: list[ReproducibilityRecord] = []

        if log_path and log_path.exists():
            self._load()

    def _load(self) -> None:
        """Load existing records from file."""
        if not self.log_path or not self.log_path.exists():
            return

        with open(self.log_path) as f:
            content = f.read()
            if not content.strip():
                # Empty file, nothing to load
                return
            data = json.loads(content)
            self._records = [
                ReproducibilityRecord.from_dict(r) for r in data.get("records", [])
            ]

    def _save(self) -> None:
        """Save records to file."""
        if not self.log_path:
            return

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "w") as f:
            json.dump(
                {"records": [r.to_dict() for r in self._records]},
                f,
                indent=2,
            )

    def add(self, record: ReproducibilityRecord) -> None:
        """Add a record to the log."""
        self._records.append(record)
        self._save()

    def find_by_hash(self, search_hash: str) -> list[ReproducibilityRecord]:
        """Find records by search hash."""
        return [r for r in self._records if r.search_hash == search_hash]

    def get_recent(self, limit: int = 10) -> list[ReproducibilityRecord]:
        """Get most recent records."""
        return sorted(self._records, key=lambda r: r.timestamp, reverse=True)[:limit]

    def clear(self) -> None:
        """Clear all records."""
        self._records = []
        self._save()


# Convenience functions for common operations


def hash_query(query: str, sources: list[str]) -> str:
    """Quick hash of just query and sources."""
    canonical = f"{query}|{','.join(sorted(sources))}"
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]


def generate_citation_key(record: ReproducibilityRecord) -> str:
    """
    Generate a citation key for referencing this search.

    Format: search_{hash}_{date}
    """
    date_part = record.timestamp[:10].replace("-", "")
    return f"search_{record.search_hash}_{date_part}"


def format_reproducibility_note(record: ReproducibilityRecord) -> str:
    """
    Format a reproducibility note for including in outputs.

    Provides human-readable record of search parameters.
    """
    lines = [
        "--- Reproducibility Information ---",
        f"Search Hash: {record.search_hash}",
        f"Result Hash: {record.result_hash}",
        f"Timestamp: {record.timestamp}",
        f"Results: {record.result_count}",
        f"Query: {record.search_spec.query}",
        f"Sources: {', '.join(record.search_spec.sources)}",
    ]

    if record.search_spec.date_start or record.search_spec.date_end:
        lines.append(
            f"Date Range: {record.search_spec.date_start or 'any'} to "
            f"{record.search_spec.date_end or 'any'}"
        )

    if record.search_spec.publication_types:
        lines.append(f"Types: {', '.join(record.search_spec.publication_types)}")

    if record.duration_ms:
        lines.append(f"Duration: {record.duration_ms:.0f}ms")

    lines.append("-----------------------------------")

    return "\n".join(lines)
