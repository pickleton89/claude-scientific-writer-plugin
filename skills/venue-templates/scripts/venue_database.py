#!/usr/bin/env python3
"""
Venue Database Access Layer
Single source of truth for all venue specifications.

Usage:
    from venue_database import get_venue, resolve_venue, list_venues

    # Get venue by ID
    venue = get_venue("nature")

    # Resolve query to venue ID
    venue_id = resolve_venue("Nature paper")  # Returns "nature"

    # List all venues
    venues = list_venues()
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

VENUES_PATH = Path(__file__).parent.parent / "data" / "venues.json"


@dataclass
class FormattingSpec:
    """Formatting specifications for a venue."""

    page_limit: Optional[int]
    word_limit: Optional[int]
    word_limit_scope: Optional[str]
    format: Literal["single-column", "two-column"]
    font_size: int
    font_family: str
    margins_cm: dict[str, float]
    line_spacing: str
    citation_style: Literal["superscript", "numbered", "author-year", "any"]
    reference_format: str


@dataclass
class AbstractSpec:
    """Abstract specifications for a venue."""

    style: Literal["flowing", "structured"]
    max_words: int
    structured_sections: Optional[list[str]]
    required_elements: list[str]


@dataclass
class StyleSpec:
    """Writing style specifications for a venue."""

    tone: Literal["accessible", "technical", "formal"]
    voice: Literal["active", "passive", "mixed"]
    first_person: bool
    jargon_level: Literal["minimal", "moderate", "high"]
    audience: str


@dataclass
class RequirementsSpec:
    """Submission requirements for a venue."""

    anonymization: bool
    graphical_abstract: bool
    data_availability: bool
    contribution_list: bool
    ablation_studies: bool


@dataclass
class VenueSpec:
    """Complete specification for a publication venue."""

    id: str
    full_name: str
    publisher: str
    type: Literal["journal", "conference", "poster", "grant"]
    discipline: str
    impact_tier: Literal["high", "medium", "standard"]
    aliases: list[str]
    formatting: FormattingSpec
    abstract: AbstractSpec
    style: StyleSpec
    requirements: RequirementsSpec
    templates: list[str]
    style_guides: list[str]
    author_guidelines_url: str


class VenueDatabase:
    """Access layer for venue specifications."""

    def __init__(self, path: Path = VENUES_PATH):
        """Initialize database from JSON file."""
        with open(path, encoding="utf-8") as f:
            self._data = json.load(f)
        self._build_alias_index()

    def _build_alias_index(self) -> None:
        """Build reverse index from aliases to venue IDs."""
        self._alias_index: dict[str, str] = {}
        for venue_id, venue in self._data["venues"].items():
            # Add canonical ID
            self._alias_index[venue_id.lower()] = venue_id
            # Add full name
            self._alias_index[venue.get("full_name", "").lower()] = venue_id
            # Add all aliases
            for alias in venue.get("aliases", []):
                self._alias_index[alias.lower()] = venue_id

    def get(self, venue_id: str) -> Optional[VenueSpec]:
        """Get venue spec by ID."""
        if venue_id not in self._data["venues"]:
            return None
        return self._parse_venue(self._data["venues"][venue_id])

    def resolve(self, query: str) -> Optional[str]:
        """Resolve query string to venue ID (exact match only)."""
        normalized = query.lower().strip()
        return self._alias_index.get(normalized)

    def list_all(self) -> list[str]:
        """List all venue IDs."""
        return list(self._data["venues"].keys())

    def list_by_type(self, venue_type: str) -> list[str]:
        """List venues by type (journal, conference, poster, grant)."""
        return [
            vid
            for vid, v in self._data["venues"].items()
            if v["type"] == venue_type
        ]

    def list_by_discipline(self, discipline: str) -> list[str]:
        """List venues by discipline."""
        return [
            vid
            for vid, v in self._data["venues"].items()
            if v.get("discipline") == discipline
        ]

    def get_raw(self, venue_id: str) -> Optional[dict]:
        """Get raw venue dict without parsing to dataclass."""
        return self._data["venues"].get(venue_id)

    def _parse_venue(self, data: dict) -> VenueSpec:
        """Parse venue dict into dataclass."""
        formatting_data = data.get("formatting", {})
        abstract_data = data.get("abstract", {})
        style_data = data.get("style", {})
        requirements_data = data.get("requirements", {})

        return VenueSpec(
            id=data["id"],
            full_name=data["full_name"],
            publisher=data.get("publisher", ""),
            type=data["type"],
            discipline=data.get("discipline", ""),
            impact_tier=data.get("impact_tier", "standard"),
            aliases=data.get("aliases", []),
            formatting=FormattingSpec(
                page_limit=formatting_data.get("page_limit"),
                word_limit=formatting_data.get("word_limit"),
                word_limit_scope=formatting_data.get("word_limit_scope"),
                format=formatting_data.get("format", "single-column"),
                font_size=formatting_data.get("font_size", 12),
                font_family=formatting_data.get("font_family", "Times"),
                margins_cm=formatting_data.get(
                    "margins_cm",
                    {"top": 2.54, "bottom": 2.54, "left": 2.54, "right": 2.54},
                ),
                line_spacing=formatting_data.get("line_spacing", "double"),
                citation_style=formatting_data.get("citation_style", "numbered"),
                reference_format=formatting_data.get("reference_format", ""),
            ),
            abstract=AbstractSpec(
                style=abstract_data.get("style", "flowing"),
                max_words=abstract_data.get("max_words", 300),
                structured_sections=abstract_data.get("structured_sections"),
                required_elements=abstract_data.get("required_elements", []),
            ),
            style=StyleSpec(
                tone=style_data.get("tone", "formal"),
                voice=style_data.get("voice", "active"),
                first_person=style_data.get("first_person", True),
                jargon_level=style_data.get("jargon_level", "moderate"),
                audience=style_data.get("audience", "specialist"),
            ),
            requirements=RequirementsSpec(
                anonymization=requirements_data.get("anonymization", False),
                graphical_abstract=requirements_data.get("graphical_abstract", False),
                data_availability=requirements_data.get("data_availability", False),
                contribution_list=requirements_data.get("contribution_list", False),
                ablation_studies=requirements_data.get("ablation_studies", False),
            ),
            templates=data.get("templates", []),
            style_guides=data.get("style_guides", []),
            author_guidelines_url=data.get("author_guidelines_url", ""),
        )


# Singleton instance
_db: Optional[VenueDatabase] = None


def get_database() -> VenueDatabase:
    """Get singleton database instance."""
    global _db
    if _db is None:
        _db = VenueDatabase()
    return _db


def get_venue(venue_id: str) -> Optional[VenueSpec]:
    """Convenience function to get venue spec by ID."""
    return get_database().get(venue_id)


def resolve_venue(query: str) -> Optional[str]:
    """Convenience function to resolve venue query to ID."""
    return get_database().resolve(query)


def list_venues() -> list[str]:
    """Convenience function to list all venue IDs."""
    return get_database().list_all()


def list_venues_by_type(venue_type: str) -> list[str]:
    """Convenience function to list venues by type."""
    return get_database().list_by_type(venue_type)


if __name__ == "__main__":
    # Demo usage
    import argparse

    parser = argparse.ArgumentParser(description="Query venue database")
    parser.add_argument("--venue", help="Venue ID to look up")
    parser.add_argument("--list", action="store_true", help="List all venues")
    parser.add_argument("--type", help="List venues by type")
    args = parser.parse_args()

    db = get_database()

    if args.list:
        print("Available venues:")
        for vid in db.list_all():
            venue = db.get(vid)
            if venue:
                print(f"  {vid}: {venue.full_name} ({venue.type})")

    elif args.type:
        print(f"Venues of type '{args.type}':")
        for vid in db.list_by_type(args.type):
            venue = db.get(vid)
            if venue:
                print(f"  {vid}: {venue.full_name}")

    elif args.venue:
        venue = db.get(args.venue)
        if venue:
            print(f"Venue: {venue.full_name}")
            print(f"  Type: {venue.type}")
            print(f"  Discipline: {venue.discipline}")
            print(f"  Page limit: {venue.formatting.page_limit or 'None'}")
            print(f"  Word limit: {venue.formatting.word_limit or 'None'}")
            print(f"  Citation style: {venue.formatting.citation_style}")
            print(f"  Abstract max words: {venue.abstract.max_words}")
            print(f"  Anonymization required: {venue.requirements.anonymization}")
        else:
            print(f"Venue '{args.venue}' not found")
    else:
        parser.print_help()
