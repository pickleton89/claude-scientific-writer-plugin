#!/usr/bin/env python3
"""Select citation style based on target journal or field."""

import json
import sys
from difflib import get_close_matches

# Journal -> Citation Style mapping
JOURNAL_STYLES = {
    # Medical journals
    "jama": "ama",
    "jama network": "ama",
    "nejm": "vancouver",
    "new england journal of medicine": "vancouver",
    "lancet": "vancouver",
    "bmj": "vancouver",
    "annals of internal medicine": "ama",
    # Life sciences
    "nature": "nature_numbered",
    "nature medicine": "nature_numbered",
    "nature communications": "nature_numbered",
    "science": "science_numbered",
    "cell": "cell_author_date",
    "cell reports": "cell_author_date",
    "plos one": "vancouver",
    "plos biology": "vancouver",
    "elife": "vancouver",
    # Psychology/Social sciences
    "psychological bulletin": "apa",
    "psychological review": "apa",
    "journal of personality and social psychology": "apa",
    "developmental psychology": "apa",
    # Engineering/CS
    "ieee transactions": "ieee",
    "acm computing surveys": "acm",
    # Chemistry
    "jacs": "acs",
    "journal of the american chemical society": "acs",
    "angewandte chemie": "acs",
    # ML Conferences
    "neurips": "numbered_brackets",
    "icml": "numbered_brackets",
    "iclr": "numbered_brackets",
    "cvpr": "ieee",
    "iccv": "ieee",
    "acl": "acl_author_year",
    "emnlp": "acl_author_year",
}

# Field -> Default style mapping
FIELD_DEFAULTS = {
    "medicine": "vancouver",
    "biomedical": "vancouver",
    "psychology": "apa",
    "social_science": "apa",
    "engineering": "ieee",
    "computer_science": "ieee",
    "chemistry": "acs",
    "physics": "aps",
    "ecology": "cse",
    "ml": "numbered_brackets",
}

STYLE_DESCRIPTIONS = {
    "ama": "Superscript numbers, AMA Manual of Style 11th ed",
    "vancouver": "Numbered brackets [1], ICMJE recommendations",
    "apa": "Author-date (Smith, 2023), APA 7th edition",
    "nature_numbered": "Superscript numbers, abbreviated format",
    "science_numbered": "Numbered (1), Science journal style",
    "ieee": "Numbered brackets [1], IEEE style",
    "acs": "Superscript or numbered, ACS style",
    "aps": "Numbered, American Physical Society style",
    "chicago": "Notes-bibliography or author-date",
    "cell_author_date": "Author-date with specific Cell formatting",
    "numbered_brackets": "Generic numbered [1] style for conferences",
    "acl_author_year": "ACL-style author-year citations",
    "acm": "Numbered, ACM reference format",
    "cse": "Council of Science Editors, name-year or citation-sequence",
}


def get_available_journals() -> list[str]:
    """Return list of known journal names."""
    return sorted(JOURNAL_STYLES.keys())


def get_available_fields() -> list[str]:
    """Return list of known field names."""
    return sorted(FIELD_DEFAULTS.keys())


def get_available_styles() -> dict[str, str]:
    """Return dictionary of style codes and their descriptions."""
    return STYLE_DESCRIPTIONS.copy()


def select_citation_style(journal_or_field: str) -> dict:
    """Select citation style for a given journal or field.

    Args:
        journal_or_field: Journal name or academic field

    Returns:
        Dictionary containing style information and match details

    Match priority:
        1. Exact journal match
        2. Exact field match
        3. Fuzzy journal match
        4. Default fallback
    """
    normalized = journal_or_field.lower().strip()

    # Try exact journal match first
    if normalized in JOURNAL_STYLES:
        style = JOURNAL_STYLES[normalized]
        return {
            "input": journal_or_field,
            "match_type": "exact_journal",
            "style": style,
            "description": STYLE_DESCRIPTIONS.get(style, ""),
        }

    # Try exact field match (before fuzzy journal to avoid false positives)
    if normalized in FIELD_DEFAULTS:
        style = FIELD_DEFAULTS[normalized]
        return {
            "input": journal_or_field,
            "match_type": "field_default",
            "style": style,
            "description": STYLE_DESCRIPTIONS.get(style, ""),
            "note": "Based on field default; check specific journal guidelines",
        }

    # Try fuzzy journal match
    close_matches = get_close_matches(
        normalized, JOURNAL_STYLES.keys(), n=1, cutoff=0.6
    )
    if close_matches:
        matched_journal = close_matches[0]
        style = JOURNAL_STYLES[matched_journal]
        return {
            "input": journal_or_field,
            "match_type": "fuzzy_journal",
            "matched_to": matched_journal,
            "style": style,
            "description": STYLE_DESCRIPTIONS.get(style, ""),
        }

    # Default fallback
    return {
        "input": journal_or_field,
        "match_type": "default",
        "style": "vancouver",
        "description": STYLE_DESCRIPTIONS["vancouver"],
        "note": "No match found; defaulting to Vancouver (most common in science)",
        "available_journals": get_available_journals(),
        "available_fields": get_available_fields(),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python select_citation_style.py <journal_name_or_field>")
        sys.exit(1)

    result = select_citation_style(" ".join(sys.argv[1:]))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
