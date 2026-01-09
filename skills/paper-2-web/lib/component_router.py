"""Component router for deterministic output selection.

This module provides rule-based routing to determine which output components
(website, poster, video) should be generated based on the use case. This
replaces subjective LLM decision-making with deterministic rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class UseCase(Enum):
    """Supported use cases for paper transformation.

    Each use case maps to a specific combination of output components
    and configuration settings.
    """

    CONFERENCE_ORAL = "conference_oral"
    CONFERENCE_POSTER = "conference_poster"
    CONFERENCE_WORKSHOP = "conference_workshop"
    JOURNAL_PUBLICATION = "journal_publication"
    PREPRINT_PROMOTION = "preprint_promotion"
    LAB_WEBSITE = "lab_website"
    PORTFOLIO = "portfolio"
    SOCIAL_MEDIA = "social_media"
    VIDEO_ABSTRACT = "video_abstract"
    COURSE_MATERIAL = "course_material"
    GRANT_APPLICATION = "grant_application"
    THESIS_DEFENSE = "thesis_defense"


VideoDuration = Literal["short_2min", "abstract_5min", "talk_15min", "extended_30min"]
VideoStyle = Literal["academic", "conference", "public", "tutorial"]
WebsiteStyle = Literal["minimal", "academic", "modern", "interactive"]


@dataclass(frozen=True)
class ComponentRecommendation:
    """Recommended component configuration for a use case.

    Attributes:
        website: Whether to generate a website
        poster: Whether to generate a poster
        video: Whether to generate a video
        video_duration: Target video duration if video is recommended
        video_style: Video style if video is recommended
        website_style: Website style if website is recommended
        priority_order: Order in which to generate components
        rationale: Explanation for the recommendation
        optional_components: Components that could be added but aren't primary
    """

    website: bool
    poster: bool
    video: bool
    video_duration: VideoDuration | None = None
    video_style: VideoStyle | None = None
    website_style: WebsiteStyle | None = None
    priority_order: tuple[str, ...] = ()
    rationale: str = ""
    optional_components: tuple[str, ...] = ()

    @property
    def primary_components(self) -> list[str]:
        """Get list of primary recommended components."""
        components = []
        if self.website:
            components.append("website")
        if self.poster:
            components.append("poster")
        if self.video:
            components.append("video")
        return components


# Deterministic routing table
# Each use case maps to exactly one recommendation
COMPONENT_ROUTING: dict[UseCase, ComponentRecommendation] = {
    UseCase.CONFERENCE_ORAL: ComponentRecommendation(
        website=False,
        poster=False,
        video=True,
        video_duration="talk_15min",
        video_style="conference",
        priority_order=("video",),
        rationale="Oral presentations need a video for practice/backup; slides extracted from video",
        optional_components=("website",),
    ),

    UseCase.CONFERENCE_POSTER: ComponentRecommendation(
        website=False,
        poster=True,
        video=False,
        priority_order=("poster",),
        rationale="Poster session requires print-ready poster; no other outputs needed",
        optional_components=("website", "video"),
    ),

    UseCase.CONFERENCE_WORKSHOP: ComponentRecommendation(
        website=True,
        poster=False,
        video=True,
        video_duration="abstract_5min",
        video_style="academic",
        website_style="minimal",
        priority_order=("website", "video"),
        rationale="Workshop papers benefit from quick reference website and short video",
        optional_components=("poster",),
    ),

    UseCase.JOURNAL_PUBLICATION: ComponentRecommendation(
        website=True,
        poster=False,
        video=False,
        website_style="academic",
        priority_order=("website",),
        rationale="Journal papers need permanent web presence for citations and visibility",
        optional_components=("video",),
    ),

    UseCase.PREPRINT_PROMOTION: ComponentRecommendation(
        website=True,
        poster=False,
        video=True,
        video_duration="abstract_5min",
        video_style="academic",
        website_style="modern",
        priority_order=("website", "video"),
        rationale="Preprints need maximum visibility; website for indexing, video for engagement",
        optional_components=("poster",),
    ),

    UseCase.LAB_WEBSITE: ComponentRecommendation(
        website=True,
        poster=False,
        video=False,
        website_style="minimal",
        priority_order=("website",),
        rationale="Lab portfolio needs only clean website; embed in existing lab site",
        optional_components=(),
    ),

    UseCase.PORTFOLIO: ComponentRecommendation(
        website=True,
        poster=False,
        video=True,
        video_duration="short_2min",
        video_style="public",
        website_style="modern",
        priority_order=("website", "video"),
        rationale="Personal portfolio benefits from polished website and engaging video",
        optional_components=("poster",),
    ),

    UseCase.SOCIAL_MEDIA: ComponentRecommendation(
        website=False,
        poster=False,
        video=True,
        video_duration="short_2min",
        video_style="public",
        priority_order=("video",),
        rationale="Social media needs short, engaging video optimized for attention",
        optional_components=("website",),
    ),

    UseCase.VIDEO_ABSTRACT: ComponentRecommendation(
        website=False,
        poster=False,
        video=True,
        video_duration="abstract_5min",
        video_style="academic",
        priority_order=("video",),
        rationale="Video abstract for journal submission; specific format requirements",
        optional_components=(),
    ),

    UseCase.COURSE_MATERIAL: ComponentRecommendation(
        website=True,
        poster=False,
        video=True,
        video_duration="extended_30min",
        video_style="tutorial",
        website_style="interactive",
        priority_order=("video", "website"),
        rationale="Course materials need detailed tutorial video and interactive website",
        optional_components=("poster",),
    ),

    UseCase.GRANT_APPLICATION: ComponentRecommendation(
        website=True,
        poster=True,
        video=False,
        website_style="minimal",
        priority_order=("poster", "website"),
        rationale="Grant applications often need visual summary poster and quick reference site",
        optional_components=("video",),
    ),

    UseCase.THESIS_DEFENSE: ComponentRecommendation(
        website=True,
        poster=True,
        video=True,
        video_duration="talk_15min",
        video_style="conference",
        website_style="academic",
        priority_order=("video", "poster", "website"),
        rationale="Thesis defense benefits from all formats: presentation, poster, archival site",
        optional_components=(),
    ),
}


# Keyword to use case mapping for inference
KEYWORD_USE_CASE_MAP: dict[str, UseCase] = {
    # Conference-related
    "oral": UseCase.CONFERENCE_ORAL,
    "oral presentation": UseCase.CONFERENCE_ORAL,
    "talk": UseCase.CONFERENCE_ORAL,
    "spotlight": UseCase.CONFERENCE_ORAL,
    "poster": UseCase.CONFERENCE_POSTER,
    "poster session": UseCase.CONFERENCE_POSTER,
    "workshop": UseCase.CONFERENCE_WORKSHOP,
    "workshop paper": UseCase.CONFERENCE_WORKSHOP,

    # Publication types
    "journal": UseCase.JOURNAL_PUBLICATION,
    "publication": UseCase.JOURNAL_PUBLICATION,
    "published": UseCase.JOURNAL_PUBLICATION,
    "paper": UseCase.JOURNAL_PUBLICATION,

    # Preprints
    "preprint": UseCase.PREPRINT_PROMOTION,
    "arxiv": UseCase.PREPRINT_PROMOTION,
    "biorxiv": UseCase.PREPRINT_PROMOTION,
    "medrxiv": UseCase.PREPRINT_PROMOTION,
    "chemrxiv": UseCase.PREPRINT_PROMOTION,

    # Lab/portfolio
    "lab": UseCase.LAB_WEBSITE,
    "lab website": UseCase.LAB_WEBSITE,
    "research group": UseCase.LAB_WEBSITE,
    "portfolio": UseCase.PORTFOLIO,
    "personal": UseCase.PORTFOLIO,
    "cv": UseCase.PORTFOLIO,

    # Social media
    "twitter": UseCase.SOCIAL_MEDIA,
    "linkedin": UseCase.SOCIAL_MEDIA,
    "social": UseCase.SOCIAL_MEDIA,
    "social media": UseCase.SOCIAL_MEDIA,
    "tweetorial": UseCase.SOCIAL_MEDIA,

    # Video abstract
    "video abstract": UseCase.VIDEO_ABSTRACT,
    "graphical abstract": UseCase.VIDEO_ABSTRACT,

    # Educational
    "course": UseCase.COURSE_MATERIAL,
    "teaching": UseCase.COURSE_MATERIAL,
    "lecture": UseCase.COURSE_MATERIAL,
    "tutorial": UseCase.COURSE_MATERIAL,

    # Grant
    "grant": UseCase.GRANT_APPLICATION,
    "proposal": UseCase.GRANT_APPLICATION,
    "funding": UseCase.GRANT_APPLICATION,

    # Thesis
    "thesis": UseCase.THESIS_DEFENSE,
    "defense": UseCase.THESIS_DEFENSE,
    "dissertation": UseCase.THESIS_DEFENSE,
    "phd": UseCase.THESIS_DEFENSE,
}


def route_components(use_case: UseCase) -> ComponentRecommendation:
    """Get component recommendation for a use case.

    Args:
        use_case: The use case enum value

    Returns:
        ComponentRecommendation for the use case

    Examples:
        >>> rec = route_components(UseCase.CONFERENCE_POSTER)
        >>> rec.poster, rec.website, rec.video
        (True, False, False)
    """
    return COMPONENT_ROUTING[use_case]


def infer_use_case(keywords: list[str]) -> UseCase | None:
    """Attempt to infer use case from keywords.

    Searches for matching keywords in the provided list.
    Longer keyword matches take priority.

    Args:
        keywords: List of keywords from user input

    Returns:
        Inferred UseCase or None if no match

    Examples:
        >>> infer_use_case(["poster", "neurips"])
        UseCase.CONFERENCE_POSTER
        >>> infer_use_case(["arxiv", "preprint"])
        UseCase.PREPRINT_PROMOTION
    """
    # Sort keyword map by length (longer matches first)
    sorted_keywords = sorted(KEYWORD_USE_CASE_MAP.keys(), key=len, reverse=True)

    # Normalize input keywords
    normalized = [k.lower().strip() for k in keywords]
    combined = " ".join(normalized)

    # Check for matches
    for keyword in sorted_keywords:
        if keyword in combined or keyword in normalized:
            return KEYWORD_USE_CASE_MAP[keyword]

    return None


def infer_use_case_from_text(text: str) -> UseCase | None:
    """Infer use case from free-form text description.

    Args:
        text: Free-form description of the use case

    Returns:
        Inferred UseCase or None if no match

    Examples:
        >>> infer_use_case_from_text("I need a poster for NeurIPS")
        UseCase.CONFERENCE_POSTER
    """
    words = text.lower().split()
    return infer_use_case(words)


def get_all_use_cases() -> list[UseCase]:
    """Get list of all supported use cases.

    Returns:
        List of UseCase enum values
    """
    return list(UseCase)


def get_use_case_description(use_case: UseCase) -> str:
    """Get human-readable description of a use case.

    Args:
        use_case: The use case enum value

    Returns:
        Description string
    """
    descriptions = {
        UseCase.CONFERENCE_ORAL: "Conference oral/spotlight presentation",
        UseCase.CONFERENCE_POSTER: "Conference poster session",
        UseCase.CONFERENCE_WORKSHOP: "Workshop paper presentation",
        UseCase.JOURNAL_PUBLICATION: "Published journal article",
        UseCase.PREPRINT_PROMOTION: "Preprint promotion (arXiv, bioRxiv, etc.)",
        UseCase.LAB_WEBSITE: "Lab/research group website",
        UseCase.PORTFOLIO: "Personal portfolio/CV",
        UseCase.SOCIAL_MEDIA: "Social media promotion",
        UseCase.VIDEO_ABSTRACT: "Video/graphical abstract for journal",
        UseCase.COURSE_MATERIAL: "Course/teaching material",
        UseCase.GRANT_APPLICATION: "Grant application materials",
        UseCase.THESIS_DEFENSE: "Thesis/dissertation defense",
    }
    return descriptions.get(use_case, use_case.value)


def recommend_for_venue(venue: str) -> ComponentRecommendation:
    """Get recommendation based on venue name.

    Attempts to infer use case from venue and returns appropriate
    recommendation. Falls back to CONFERENCE_POSTER for unknown venues.

    Args:
        venue: Conference or venue name

    Returns:
        ComponentRecommendation for the venue

    Examples:
        >>> rec = recommend_for_venue("NeurIPS 2024")
        >>> rec.poster
        True
    """
    venue_lower = venue.lower()

    # Check for oral-related keywords
    oral_keywords = ["oral", "spotlight", "talk", "presentation"]
    if any(kw in venue_lower for kw in oral_keywords):
        return route_components(UseCase.CONFERENCE_ORAL)

    # Check for workshop keywords
    if "workshop" in venue_lower:
        return route_components(UseCase.CONFERENCE_WORKSHOP)

    # Check for journal keywords
    journal_keywords = ["journal", "transactions", "letters"]
    if any(kw in venue_lower for kw in journal_keywords):
        return route_components(UseCase.JOURNAL_PUBLICATION)

    # Default to poster for conferences
    return route_components(UseCase.CONFERENCE_POSTER)


def format_recommendation(rec: ComponentRecommendation) -> str:
    """Format recommendation as human-readable string.

    Args:
        rec: ComponentRecommendation to format

    Returns:
        Formatted string
    """
    lines = ["Component Recommendation", "=" * 40]

    components = []
    if rec.website:
        style_info = f" ({rec.website_style})" if rec.website_style else ""
        components.append(f"Website{style_info}")
    if rec.poster:
        components.append("Poster")
    if rec.video:
        duration = rec.video_duration or "default"
        style = rec.video_style or "academic"
        components.append(f"Video ({duration}, {style})")

    lines.append("Primary: " + ", ".join(components) if components else "None")

    if rec.optional_components:
        lines.append("Optional: " + ", ".join(rec.optional_components))

    lines.append("")
    lines.append(f"Priority order: {' > '.join(rec.priority_order)}")
    lines.append("")
    lines.append(f"Rationale: {rec.rationale}")

    return "\n".join(lines)


__all__ = [
    "UseCase",
    "VideoDuration",
    "VideoStyle",
    "WebsiteStyle",
    "ComponentRecommendation",
    "COMPONENT_ROUTING",
    "KEYWORD_USE_CASE_MAP",
    "route_components",
    "infer_use_case",
    "infer_use_case_from_text",
    "get_all_use_cases",
    "get_use_case_description",
    "recommend_for_venue",
    "format_recommendation",
]
