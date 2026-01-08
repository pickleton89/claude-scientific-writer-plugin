#!/usr/bin/env python3
"""
Venue Resolver
Fuzzy matching to resolve user queries to canonical venue IDs.

Usage:
    python venue_resolver.py "Nature paper"
    python venue_resolver.py "neurips 2025" --threshold 0.7
    python venue_resolver.py "natur" --show-alternatives

Examples:
    "Nature paper" -> nature (confidence: 1.0)
    "NeurIPS 2024" -> neurips (confidence: 1.0)
    "natur" -> nature (confidence: 0.91, fuzzy match)
    "xyzzy journal" -> None (no match)
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

from venue_database import VenueDatabase, get_database


@dataclass
class ResolveResult:
    """Result of venue resolution."""

    venue_id: Optional[str]
    confidence: float
    matched_alias: str
    alternatives: list[tuple[str, float]]  # (venue_id, score)


class VenueResolver:
    """Fuzzy venue name resolver."""

    def __init__(self, db: Optional[VenueDatabase] = None):
        """Initialize resolver with venue database."""
        self.db = db or get_database()
        self._build_search_index()

    def _build_search_index(self) -> None:
        """Build searchable index of venue names and aliases."""
        self._index: list[tuple[str, str]] = []  # (search_term, venue_id)

        for venue_id in self.db.list_all():
            venue = self.db.get(venue_id)
            if venue:
                # Add canonical ID
                self._index.append((venue_id.lower(), venue_id))
                # Add full name
                self._index.append((venue.full_name.lower(), venue_id))
                # Add all aliases
                for alias in venue.aliases:
                    self._index.append((alias.lower(), venue_id))

    def _normalize_query(self, query: str) -> str:
        """Normalize query for matching."""
        # Remove year suffixes (NeurIPS 2024 -> NeurIPS)
        query = re.sub(r"\s+20\d{2}$", "", query)
        # Lowercase and strip
        query = query.lower().strip()
        # Remove common words
        query = re.sub(
            r"\b(paper|article|journal|conference|grant|proposal|submission)\b",
            "",
            query,
        )
        # Collapse whitespace
        query = re.sub(r"\s+", " ", query).strip()
        return query

    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, a, b).ratio()

    def resolve(self, query: str, threshold: float = 0.6) -> ResolveResult:
        """
        Resolve query to venue ID.

        Args:
            query: User's venue query string
            threshold: Minimum confidence for a match (0-1)

        Returns:
            ResolveResult with venue_id, confidence, and alternatives
        """
        normalized = self._normalize_query(query)

        # Exact match first
        for term, venue_id in self._index:
            if term == normalized:
                return ResolveResult(
                    venue_id=venue_id,
                    confidence=1.0,
                    matched_alias=term,
                    alternatives=[],
                )

        # Substring match (e.g., "nature" in "nature publishing group")
        for term, venue_id in self._index:
            if normalized in term or term in normalized:
                # Score based on length similarity
                score = min(len(normalized), len(term)) / max(
                    len(normalized), len(term)
                )
                if score >= 0.5:  # At least 50% length overlap
                    return ResolveResult(
                        venue_id=venue_id,
                        confidence=min(0.95, score + 0.2),  # Boost for substring
                        matched_alias=term,
                        alternatives=[],
                    )

        # Fuzzy match
        scores: list[tuple[str, str, float]] = []
        for term, venue_id in self._index:
            score = self._similarity(normalized, term)
            scores.append((venue_id, term, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[2], reverse=True)

        # Deduplicate by venue_id, keeping highest score
        seen: set[str] = set()
        unique_scores: list[tuple[str, str, float]] = []
        for venue_id, term, score in scores:
            if venue_id not in seen:
                seen.add(venue_id)
                unique_scores.append((venue_id, term, score))

        if not unique_scores:
            return ResolveResult(
                venue_id=None,
                confidence=0.0,
                matched_alias="",
                alternatives=[],
            )

        best = unique_scores[0]
        alternatives = [(vid, score) for vid, _, score in unique_scores[1:5]]

        if best[2] >= threshold:
            return ResolveResult(
                venue_id=best[0],
                confidence=best[2],
                matched_alias=best[1],
                alternatives=alternatives,
            )
        else:
            return ResolveResult(
                venue_id=None,
                confidence=best[2],
                matched_alias=best[1],
                alternatives=[(best[0], best[2])] + alternatives,
            )


# Module-level resolver instance
_resolver: Optional[VenueResolver] = None


def get_resolver() -> VenueResolver:
    """Get singleton resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = VenueResolver()
    return _resolver


def resolve_venue(query: str, threshold: float = 0.6) -> ResolveResult:
    """Convenience function for venue resolution."""
    return get_resolver().resolve(query, threshold)


def resolve_venue_id(query: str, threshold: float = 0.6) -> Optional[str]:
    """Resolve query and return just the venue ID (or None)."""
    result = resolve_venue(query, threshold)
    return result.venue_id


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Resolve venue queries")
    parser.add_argument("query", help="Venue query string")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="Minimum confidence threshold (0-1)",
    )
    parser.add_argument(
        "--show-alternatives",
        action="store_true",
        help="Always show alternative matches",
    )
    args = parser.parse_args()

    result = resolve_venue(args.query, args.threshold)

    if result.venue_id:
        venue = get_database().get(result.venue_id)
        print(f"Resolved: {result.venue_id}")
        if venue:
            print(f"Full name: {venue.full_name}")
        print(f"Confidence: {result.confidence:.2f}")
        if result.matched_alias != result.venue_id:
            print(f"Matched: '{result.matched_alias}'")

        if args.show_alternatives and result.alternatives:
            print("\nAlternatives:")
            for vid, score in result.alternatives[:3]:
                alt_venue = get_database().get(vid)
                name = alt_venue.full_name if alt_venue else vid
                print(f"  - {name} ({score:.2f})")
    else:
        print(f"No match found (best score: {result.confidence:.2f})")
        if result.alternatives:
            print("\nDid you mean:")
            for vid, score in result.alternatives[:3]:
                alt_venue = get_database().get(vid)
                name = alt_venue.full_name if alt_venue else vid
                print(f"  - {name} ({score:.2f})")


if __name__ == "__main__":
    main()
