#!/usr/bin/env python3
"""
Deterministic citation style selector.

Encodes decision tree from references/decision_framework.md as executable logic.
Provides venue type inference and citation style selection for academic writing.
"""

import argparse
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class VenueType(Enum):
    """Target venue categories for citation style selection."""

    BIOMEDICAL_JOURNAL = "biomedical"  # NEJM, JAMA, Lancet, BMJ
    LIFE_SCIENCES = "life_sciences"  # Nature, Science, Cell, PNAS
    SOCIAL_SCIENCES = "social_sciences"  # Psychology, sociology, economics
    HUMANITIES = "humanities"  # History, philosophy, literature
    CS_CONFERENCE = "cs_conference"  # NeurIPS, ICML, ACL
    IEEE_VENUE = "ieee"  # IEEE transactions/conferences
    ACM_VENUE = "acm"  # ACM publications
    THESIS = "thesis"  # PhD/Masters dissertation
    NIH_GRANT = "nih_grant"  # NIH grant proposals
    NSF_GRANT = "nsf_grant"  # NSF grant proposals
    OTHER_GRANT = "other_grant"  # Other funding agencies
    CHEMISTRY = "chemistry"  # ACS journals
    PHYSICS = "physics"  # APS, physics journals
    LEGAL = "legal"  # Law reviews, legal journals
    UNKNOWN = "unknown"  # Could not determine venue type


class CitationStyle(Enum):
    """BibTeX bibliography styles."""

    VANCOUVER = "vancouver"  # Numbered, biomedical
    NATURE = "naturemag"  # Nature/Science style
    APA7 = "apa"  # APA 7th edition
    CHICAGO = "chicago-authordate"  # Chicago author-date
    CHICAGO_NOTES = "chicago-notes"  # Chicago notes-bibliography
    MLA = "mla"  # MLA style
    IEEE = "ieeetr"  # IEEE transactions
    ACM = "acm"  # ACM reference format
    ACS = "achemso"  # American Chemical Society
    AIP = "aip"  # American Institute of Physics
    BLUEBOOK = "bluebook"  # Legal citations


@dataclass
class StyleRecommendation:
    """Citation style recommendation with metadata."""

    style: CitationStyle
    venue_type: VenueType
    confidence: float  # 0.0 to 1.0
    alternatives: List[CitationStyle]
    notes: str


# Deterministic mapping from venue type to citation style
STYLE_MAP: dict[VenueType, CitationStyle] = {
    VenueType.BIOMEDICAL_JOURNAL: CitationStyle.VANCOUVER,
    VenueType.LIFE_SCIENCES: CitationStyle.NATURE,
    VenueType.SOCIAL_SCIENCES: CitationStyle.APA7,
    VenueType.HUMANITIES: CitationStyle.CHICAGO_NOTES,
    VenueType.CS_CONFERENCE: CitationStyle.IEEE,
    VenueType.IEEE_VENUE: CitationStyle.IEEE,
    VenueType.ACM_VENUE: CitationStyle.ACM,
    VenueType.THESIS: CitationStyle.APA7,
    VenueType.NIH_GRANT: CitationStyle.VANCOUVER,
    VenueType.NSF_GRANT: CitationStyle.APA7,
    VenueType.OTHER_GRANT: CitationStyle.APA7,
    VenueType.CHEMISTRY: CitationStyle.ACS,
    VenueType.PHYSICS: CitationStyle.AIP,
    VenueType.LEGAL: CitationStyle.BLUEBOOK,
    VenueType.UNKNOWN: CitationStyle.APA7,
}

# Alternative styles for each venue type
ALTERNATIVE_STYLES: dict[VenueType, List[CitationStyle]] = {
    VenueType.BIOMEDICAL_JOURNAL: [CitationStyle.APA7],
    VenueType.LIFE_SCIENCES: [CitationStyle.VANCOUVER, CitationStyle.APA7],
    VenueType.SOCIAL_SCIENCES: [CitationStyle.CHICAGO],
    VenueType.HUMANITIES: [CitationStyle.MLA, CitationStyle.CHICAGO],
    VenueType.CS_CONFERENCE: [CitationStyle.ACM],
    VenueType.IEEE_VENUE: [],
    VenueType.ACM_VENUE: [],
    VenueType.THESIS: [CitationStyle.CHICAGO],
    VenueType.NIH_GRANT: [CitationStyle.APA7],
    VenueType.NSF_GRANT: [CitationStyle.CHICAGO],
    VenueType.OTHER_GRANT: [CitationStyle.VANCOUVER],
    VenueType.CHEMISTRY: [],
    VenueType.PHYSICS: [CitationStyle.APA7],
    VenueType.LEGAL: [],
    VenueType.UNKNOWN: [CitationStyle.CHICAGO, CitationStyle.MLA],
}

# Keyword patterns for venue type inference
# NOTE: Order matters! More specific patterns must come before general ones.
# E.g., "national science foundation" must be checked before "science" keyword.
VENUE_PATTERNS: List[Tuple[List[str], VenueType, float]] = [
    # NSF grants - MUST be before life_sciences (contains "science")
    (
        ["nsf", "national science foundation", "career award"],
        VenueType.NSF_GRANT,
        0.95,
    ),
    # Social sciences - MUST be before life_sciences (cognitive science contains "science")
    (
        [
            "psychology",
            "psychological",
            "sociology",
            "sociological",
            "social science",
            "behavioral",
            "cognitive",
            "developmental",
            "journal of personality",
            "journal of experimental psychology",
            "american psychologist",
        ],
        VenueType.SOCIAL_SCIENCES,
        0.85,
    ),
    # Biomedical journals (high confidence)
    (
        [
            "nejm",
            "new england journal of medicine",
            "jama",
            "lancet",
            "bmj",
            "british medical journal",
            "annals of internal medicine",
            "circulation",
            "blood",
            "jci",
            "journal of clinical investigation",
        ],
        VenueType.BIOMEDICAL_JOURNAL,
        0.95,
    ),
    # Life sciences (high confidence) - after NSF and social sciences
    (
        [
            "nature",
            "science",
            "cell",
            "pnas",
            "proceedings of the national academy",
            "plos",
            "elife",
            "current biology",
            "molecular cell",
            "nature communications",
            "science advances",
        ],
        VenueType.LIFE_SCIENCES,
        0.95,
    ),
    # IEEE venues
    (
        [
            "ieee",
            "ieee transactions",
            "ieee journal",
            "ieee conference",
        ],
        VenueType.IEEE_VENUE,
        0.98,
    ),
    # ACM venues
    (
        [
            "acm",
            "sigchi",
            "siggraph",
            "sigplan",
            "sigmod",
            "sigir",
            "sigkdd",
            "communications of the acm",
        ],
        VenueType.ACM_VENUE,
        0.98,
    ),
    # CS conferences
    (
        [
            "neurips",
            "nips",
            "icml",
            "iclr",
            "cvpr",
            "iccv",
            "eccv",
            "acl",
            "emnlp",
            "naacl",
            "aaai",
            "ijcai",
            "kdd",
            "www",
            "icse",
            "fse",
            "issta",
        ],
        VenueType.CS_CONFERENCE,
        0.95,
    ),
    # NIH grants
    (
        [
            "nih",
            "ninds",
            "nci",
            "nhlbi",
            "niaid",
            "nigms",
            "nimh",
            "niddk",
            "nia",
            "nichd",
            "r01",
            "r21",
            "r03",
            "k99",
            "f31",
            "f32",
        ],
        VenueType.NIH_GRANT,
        0.95,
    ),
    # Chemistry
    (
        [
            "acs",
            "american chemical society",
            "jacs",
            "journal of the american chemical society",
            "angewandte",
            "chemistry",
            "chemical",
        ],
        VenueType.CHEMISTRY,
        0.85,
    ),
    # Physics
    (
        [
            "physical review",
            "phys rev",
            "aps",
            "american physical society",
            "physics letters",
            "journal of physics",
        ],
        VenueType.PHYSICS,
        0.90,
    ),
    # Humanities
    (
        [
            "history",
            "historical",
            "philosophy",
            "philosophical",
            "literature",
            "literary",
            "humanities",
            "classical",
            "medieval",
            "renaissance",
        ],
        VenueType.HUMANITIES,
        0.85,
    ),
    # Legal
    (
        [
            "law review",
            "legal",
            "law journal",
            "harvard law",
            "yale law",
            "stanford law",
            "columbia law",
        ],
        VenueType.LEGAL,
        0.95,
    ),
    # Thesis/dissertation
    (
        [
            "thesis",
            "dissertation",
            "phd",
            "doctoral",
            "masters",
            "graduate",
        ],
        VenueType.THESIS,
        0.90,
    ),
    # Other grants
    (
        [
            "grant",
            "funding",
            "proposal",
            "foundation",
            "award",
        ],
        VenueType.OTHER_GRANT,
        0.60,
    ),
]


def infer_venue_type(venue_name: str) -> Tuple[VenueType, float]:
    """
    Infer venue type from venue name string.

    Args:
        venue_name: Name of journal, conference, or grant program

    Returns:
        Tuple of (VenueType, confidence) where confidence is 0.0-1.0
    """
    if not venue_name:
        return VenueType.UNKNOWN, 0.0

    name_lower = venue_name.lower().strip()

    # Check against all patterns
    for keywords, venue_type, confidence in VENUE_PATTERNS:
        for keyword in keywords:
            if keyword in name_lower:
                return venue_type, confidence

    return VenueType.UNKNOWN, 0.0


def select_citation_style(venue: VenueType) -> CitationStyle:
    """
    Select appropriate citation style for venue.

    Args:
        venue: Target venue type

    Returns:
        Recommended citation style
    """
    return STYLE_MAP.get(venue, CitationStyle.APA7)


def get_style_recommendation(venue_name: str) -> StyleRecommendation:
    """
    Get full style recommendation with alternatives and notes.

    Args:
        venue_name: Name of target venue

    Returns:
        StyleRecommendation with full details
    """
    venue_type, confidence = infer_venue_type(venue_name)
    style = select_citation_style(venue_type)
    alternatives = ALTERNATIVE_STYLES.get(venue_type, [])

    # Generate notes based on venue type
    notes = _generate_notes(venue_type, confidence)

    return StyleRecommendation(
        style=style,
        venue_type=venue_type,
        confidence=confidence,
        alternatives=alternatives,
        notes=notes,
    )


def _generate_notes(venue_type: VenueType, confidence: float) -> str:
    """Generate helpful notes for the style recommendation."""
    notes_map = {
        VenueType.BIOMEDICAL_JOURNAL: (
            "Vancouver/NLM style uses numbered citations. "
            "Check journal's author guidelines for specific requirements."
        ),
        VenueType.LIFE_SCIENCES: (
            "Nature-style citations are common but many journals have specific formats. "
            "Always verify with target journal guidelines."
        ),
        VenueType.SOCIAL_SCIENCES: (
            "APA 7th edition is standard. Ensure DOIs are included when available."
        ),
        VenueType.HUMANITIES: (
            "Chicago notes-bibliography is traditional for humanities. "
            "Some journals prefer author-date format."
        ),
        VenueType.CS_CONFERENCE: (
            "Most CS venues accept IEEE format. "
            "ACM venues require ACM Reference Format."
        ),
        VenueType.IEEE_VENUE: (
            "IEEE style is required. Use ieeetr bibliography style."
        ),
        VenueType.ACM_VENUE: (
            "ACM Reference Format is required. "
            "Include DOIs and access dates for online resources."
        ),
        VenueType.THESIS: (
            "Check your institution's thesis formatting guidelines. "
            "APA and Chicago are commonly accepted."
        ),
        VenueType.NIH_GRANT: (
            "NIH prefers Vancouver/NLM format. "
            "Include PMCIDs for NIH-funded work when available."
        ),
        VenueType.NSF_GRANT: (
            "NSF accepts APA format. Follow specific program guidelines."
        ),
        VenueType.OTHER_GRANT: (
            "Check funder guidelines for citation requirements."
        ),
        VenueType.CHEMISTRY: (
            "ACS style is required for ACS journals. "
            "Use achemso package in LaTeX."
        ),
        VenueType.PHYSICS: (
            "AIP/APS style for physics journals. "
            "RevTeX is commonly used."
        ),
        VenueType.LEGAL: (
            "Bluebook format is standard for U.S. legal citations."
        ),
        VenueType.UNKNOWN: (
            "Could not determine venue type. "
            "APA 7th edition is a safe default for most academic contexts."
        ),
    }

    base_note = notes_map.get(venue_type, "")

    if confidence < 0.7:
        base_note += " (Low confidence - verify with target venue guidelines.)"

    return base_note


def get_latex_commands(style: CitationStyle) -> dict[str, str]:
    """
    Get LaTeX commands for the citation style.

    Args:
        style: Citation style enum

    Returns:
        Dictionary with bibliographystyle and recommended packages
    """
    packages_map = {
        CitationStyle.VANCOUVER: {
            "bibliographystyle": "\\bibliographystyle{vancouver}",
            "package": "\\usepackage{vancouver}",
            "natbib": True,
        },
        CitationStyle.NATURE: {
            "bibliographystyle": "\\bibliographystyle{naturemag}",
            "package": "\\usepackage{natbib}",
            "natbib": True,
        },
        CitationStyle.APA7: {
            "bibliographystyle": "\\bibliographystyle{apa}",
            "package": "\\usepackage{apacite}",
            "natbib": False,
        },
        CitationStyle.CHICAGO: {
            "bibliographystyle": "\\bibliographystyle{chicago}",
            "package": "\\usepackage{natbib}",
            "natbib": True,
        },
        CitationStyle.CHICAGO_NOTES: {
            "bibliographystyle": "\\bibliographystyle{chicago}",
            "package": "\\usepackage{biblatex-chicago}",
            "natbib": False,
        },
        CitationStyle.MLA: {
            "bibliographystyle": "\\bibliographystyle{mla}",
            "package": "\\usepackage{biblatex-mla}",
            "natbib": False,
        },
        CitationStyle.IEEE: {
            "bibliographystyle": "\\bibliographystyle{ieeetr}",
            "package": "",
            "natbib": False,
        },
        CitationStyle.ACM: {
            "bibliographystyle": "\\bibliographystyle{ACM-Reference-Format}",
            "package": "\\usepackage{acmart}",
            "natbib": False,
        },
        CitationStyle.ACS: {
            "bibliographystyle": "\\bibliographystyle{achemso}",
            "package": "\\usepackage{achemso}",
            "natbib": False,
        },
        CitationStyle.AIP: {
            "bibliographystyle": "\\bibliographystyle{aipnum4-2}",
            "package": "\\usepackage{aip}",
            "natbib": False,
        },
        CitationStyle.BLUEBOOK: {
            "bibliographystyle": "\\bibliographystyle{plain}",
            "package": "% Use manual Bluebook formatting",
            "natbib": False,
        },
    }

    return packages_map.get(
        style,
        {
            "bibliographystyle": f"\\bibliographystyle{{{style.value}}}",
            "package": "",
            "natbib": False,
        },
    )


def format_recommendation(rec: StyleRecommendation) -> str:
    """Format recommendation for display."""
    lines = [
        f"Venue Type: {rec.venue_type.value}",
        f"Confidence: {rec.confidence:.0%}",
        f"Recommended Style: {rec.style.value}",
    ]

    if rec.alternatives:
        alt_names = [s.value for s in rec.alternatives]
        lines.append(f"Alternatives: {', '.join(alt_names)}")

    latex = get_latex_commands(rec.style)
    lines.append(f"LaTeX: {latex['bibliographystyle']}")

    if latex.get("package"):
        lines.append(f"Package: {latex['package']}")

    lines.append(f"\nNotes: {rec.notes}")

    return "\n".join(lines)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Select citation style for academic venue",
        epilog="Example: python select_citation_style.py 'Nature'",
    )
    parser.add_argument("venue", help="Venue name (journal, conference, or grant)")
    parser.add_argument(
        "--format",
        choices=["text", "json", "latex"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()

    rec = get_style_recommendation(args.venue)

    if args.format == "text":
        print(format_recommendation(rec))
    elif args.format == "json":
        import json

        output = {
            "venue_input": args.venue,
            "venue_type": rec.venue_type.value,
            "confidence": rec.confidence,
            "style": rec.style.value,
            "alternatives": [s.value for s in rec.alternatives],
            "latex": get_latex_commands(rec.style),
            "notes": rec.notes,
        }
        print(json.dumps(output, indent=2))
    elif args.format == "latex":
        latex = get_latex_commands(rec.style)
        print(f"% Citation style for: {args.venue}")
        print(f"% Detected venue type: {rec.venue_type.value}")
        if latex.get("package"):
            print(latex["package"])
        print(latex["bibliographystyle"])


if __name__ == "__main__":
    main()
