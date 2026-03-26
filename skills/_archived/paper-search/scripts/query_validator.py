#!/usr/bin/env python3
"""
Query Syntax Validators for Academic Paper Search

Provides pre-flight validation of query syntax before API submission,
catching errors early and providing helpful feedback.

Usage:
    from query_validator import (
        validate_pubmed_query,
        validate_semantic_query,
        validate_query,
        ValidationResult
    )

    # Validate PubMed query
    result = validate_pubmed_query("CRISPR[Title] AND gene therapy")
    if result.is_valid:
        print("Query is valid")
    else:
        for error in result.errors:
            print(f"Error: {error}")
        for warning in result.warnings:
            print(f"Warning: {warning}")
"""

from dataclasses import dataclass, field
from typing import List, Set, Optional, Tuple
import re


@dataclass
class ValidationResult:
    """
    Result of query validation.

    Attributes:
        is_valid: Whether the query passed validation
        errors: List of critical errors that will cause search failure
        warnings: List of potential issues that may affect results
        suggestions: List of improvement suggestions
        normalized_query: Query after normalization (if applicable)
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    normalized_query: Optional[str] = None


# PubMed valid field tags
PUBMED_VALID_FIELDS: Set[str] = {
    # Core fields
    "Author", "AU",
    "Title", "TI",
    "Abstract", "AB",
    "Text Word", "TW",
    "Journal", "TA",
    "Volume", "VI",
    "Issue", "IP",
    "Pagination", "PG",

    # Identifiers
    "PMID", "UID",
    "DOI",
    "ISBN",
    "ISSN",

    # Subject/Classification
    "MeSH Terms", "MH",
    "MeSH Major Topic", "MAJR",
    "MeSH Subheading", "SH",
    "Pharmacological Action", "PA",
    "Substance Name", "NM",
    "Supplementary Concept", "NM",

    # Dates
    "Publication Date", "DP",
    "Date - Create", "CRDT",
    "Date - Completion", "DCOM",
    "Date - Entry", "EDAT",
    "Date - MeSH", "MHDA",
    "Date - Modification", "LR",
    "Date - Publication", "DP",

    # Publication info
    "Publication Type", "PT",
    "Language", "LA",
    "Country",
    "Place of Publication", "PL",

    # Author info
    "Affiliation", "AD",
    "Corporate Author", "CN",
    "First Author Name", "1AU",
    "Full Author Name", "FAU",
    "Investigator", "IR",
    "Investigator Affiliation", "IRAD",
    "Last Author", "LASTAU",

    # Other
    "All Fields", "ALL",
    "Book", "book",
    "Conflict of Interest", "COIS",
    "EC/RN Number", "RN",
    "Editor", "ED",
    "Filter", "FILTER",
    "Grant Number", "GR",
    "Location ID", "LID",
    "NLM Unique ID", "JID",
    "Other Term", "OT",
    "Owner", "OWN",
    "Publisher", "PUBN",
    "Secondary Source ID", "SI",
    "Subset", "SB",
    "Transliterated Title", "TT",
}

# Common PubMed publication types
PUBMED_PUBLICATION_TYPES: Set[str] = {
    "Review",
    "Systematic Review",
    "Meta-Analysis",
    "Clinical Trial",
    "Randomized Controlled Trial",
    "Case Reports",
    "Comparative Study",
    "Controlled Clinical Trial",
    "Editorial",
    "Letter",
    "Comment",
    "Practice Guideline",
    "Guideline",
    "Observational Study",
    "Validation Study",
    "Multicenter Study",
    "Research Support, N.I.H., Extramural",
    "Research Support, N.I.H., Intramural",
    "Research Support, Non-U.S. Gov't",
    "Research Support, U.S. Gov't, Non-P.H.S.",
    "Research Support, U.S. Gov't, P.H.S.",
}


def validate_pubmed_query(query: str) -> ValidationResult:
    """
    Validate PubMed query syntax before submission.

    Checks:
    - Balanced brackets and parentheses
    - Valid field tags
    - Boolean operator syntax
    - Date range format
    - Common mistakes

    Args:
        query: PubMed query string

    Returns:
        ValidationResult with errors, warnings, and suggestions
    """
    errors = []
    warnings = []
    suggestions = []

    if not query or not query.strip():
        return ValidationResult(
            is_valid=False,
            errors=["Query is empty"]
        )

    # Check balanced brackets
    if query.count('[') != query.count(']'):
        errors.append("Unbalanced field tags: mismatched square brackets []")

    # Check balanced parentheses
    if query.count('(') != query.count(')'):
        errors.append("Unbalanced parentheses: mismatched ()")

    # Check balanced quotes
    quote_count = query.count('"')
    if quote_count % 2 != 0:
        errors.append("Unbalanced quotes: odd number of quotation marks")

    # Extract and validate field tags
    field_tags = re.findall(r'\[([^\]]+)\]', query)
    for tag in field_tags:
        # Check if it's a valid field
        if tag not in PUBMED_VALID_FIELDS:
            # Check case-insensitive
            tag_lower = tag.lower()
            valid_lower = {f.lower() for f in PUBMED_VALID_FIELDS}
            if tag_lower not in valid_lower:
                # Check for common typos
                if tag_lower in ("authors", "auth"):
                    suggestions.append(f"Did you mean [Author] instead of [{tag}]?")
                elif tag_lower in ("titles", "ti"):
                    suggestions.append(f"Did you mean [Title] instead of [{tag}]?")
                elif tag_lower in ("abstracts", "abs"):
                    suggestions.append(f"Did you mean [Abstract] instead of [{tag}]?")
                elif tag_lower in ("mesh", "mesh term"):
                    suggestions.append(f"Did you mean [MeSH Terms] instead of [{tag}]?")
                elif tag_lower in ("date", "year", "pub date"):
                    suggestions.append(f"Did you mean [Publication Date] instead of [{tag}]?")
                elif tag_lower in ("type", "pub type"):
                    suggestions.append(f"Did you mean [Publication Type] instead of [{tag}]?")
                else:
                    warnings.append(f"Unknown field tag: [{tag}]")

    # Check for empty boolean clauses
    empty_patterns = [
        (r'AND\s+AND', "Empty clause between AND operators"),
        (r'OR\s+OR', "Empty clause between OR operators"),
        (r'AND\s+OR', "Missing term between AND and OR"),
        (r'OR\s+AND', "Missing term between OR and AND"),
        (r'NOT\s+AND', "Missing term between NOT and AND"),
        (r'NOT\s+OR', "Missing term between NOT and OR"),
        (r'^\s*AND\b', "Query starts with AND operator"),
        (r'^\s*OR\b', "Query starts with OR operator"),
        (r'\bAND\s*$', "Query ends with AND operator"),
        (r'\bOR\s*$', "Query ends with OR operator"),
    ]
    for pattern, message in empty_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            errors.append(message)

    # Check for lowercase boolean operators (common mistake)
    if re.search(r'\b(and|or|not)\b', query):
        warnings.append(
            "Lowercase boolean operators detected. "
            "PubMed requires uppercase AND, OR, NOT"
        )

    # Check date range format
    date_pattern = r'(\d{4}(?:/\d{2}(?:/\d{2})?)?):(\d{4}(?:/\d{2}(?:/\d{2})?)?)\[Publication Date\]'
    date_matches = re.findall(date_pattern, query)
    for start, end in date_matches:
        try:
            start_year = int(start[:4])
            end_year = int(end[:4])
            if start_year > end_year:
                errors.append(f"Invalid date range: start year ({start_year}) > end year ({end_year})")
            if end_year > 2030:
                warnings.append(f"End year ({end_year}) seems too far in the future")
            if start_year < 1800:
                warnings.append(f"Start year ({start_year}) seems too far in the past")
        except ValueError:
            errors.append(f"Invalid date format in range: {start}:{end}")

    # Check for very short queries that might be too broad
    words = re.findall(r'\b\w+\b', query)
    non_operator_words = [w for w in words if w.upper() not in ('AND', 'OR', 'NOT')]
    if len(non_operator_words) == 1:
        warnings.append(
            f"Very short query with single term '{non_operator_words[0]}' "
            "may return too many results"
        )

    # Check for very long queries
    if len(query) > 2000:
        warnings.append(
            f"Query length ({len(query)} chars) is very long. "
            "Consider breaking into multiple searches"
        )

    # Common query improvements
    if "review" in query.lower() and "[Publication Type]" not in query:
        suggestions.append(
            "To specifically find review articles, use: Review[Publication Type]"
        )

    if re.search(r'\b\d{4}\b', query) and "[Publication Date]" not in query:
        suggestions.append(
            "To filter by year, use: YYYY:YYYY[Publication Date]"
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
        normalized_query=query.strip()
    )


def validate_semantic_query(query: str) -> ValidationResult:
    """
    Validate Semantic Scholar query syntax.

    Semantic Scholar has simpler query syntax than PubMed,
    but we still check for common issues.

    Args:
        query: Semantic Scholar query string

    Returns:
        ValidationResult with errors, warnings, and suggestions
    """
    errors = []
    warnings = []
    suggestions = []

    if not query or not query.strip():
        return ValidationResult(
            is_valid=False,
            errors=["Query is empty"]
        )

    # Check balanced quotes
    quote_count = query.count('"')
    if quote_count % 2 != 0:
        errors.append("Unbalanced quotes: odd number of quotation marks")

    # Check balanced parentheses
    if query.count('(') != query.count(')'):
        errors.append("Unbalanced parentheses")

    # Semantic Scholar doesn't use field tags like PubMed
    if re.search(r'\[[^\]]+\]', query):
        warnings.append(
            "Field tags like [Author] are PubMed syntax. "
            "Semantic Scholar uses simpler keyword search"
        )
        suggestions.append(
            "Remove field tags for Semantic Scholar, or use author: prefix"
        )

    # Check for very short queries
    words = re.findall(r'\b\w+\b', query)
    if len(words) == 1 and len(words[0]) < 4:
        warnings.append(
            f"Very short query '{query}' may return too many irrelevant results"
        )

    # Check for special characters that might cause issues
    special_chars = re.findall(r'[&|!~^]', query)
    if special_chars:
        warnings.append(
            f"Special characters {set(special_chars)} may not work as expected"
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
        normalized_query=query.strip()
    )


def validate_biorxiv_query(query: str) -> ValidationResult:
    """
    Validate bioRxiv query syntax.

    bioRxiv uses simple text matching similar to Semantic Scholar.

    Args:
        query: bioRxiv query string

    Returns:
        ValidationResult with errors, warnings, and suggestions
    """
    errors = []
    warnings = []
    suggestions = []

    if not query or not query.strip():
        return ValidationResult(
            is_valid=False,
            errors=["Query is empty"]
        )

    # Check balanced quotes
    quote_count = query.count('"')
    if quote_count % 2 != 0:
        errors.append("Unbalanced quotes")

    # bioRxiv doesn't support complex boolean
    if re.search(r'\bNOT\b', query, re.IGNORECASE):
        warnings.append(
            "bioRxiv may not fully support NOT operator"
        )

    # Check for field tags (not supported)
    if re.search(r'\[[^\]]+\]', query):
        warnings.append(
            "Field tags are PubMed syntax, not supported by bioRxiv"
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
        normalized_query=query.strip()
    )


def validate_query(query: str, source: str) -> ValidationResult:
    """
    Validate query for a specific database source.

    Args:
        query: Search query string
        source: Database source (pubmed, semantic, biorxiv, medrxiv, scholar)

    Returns:
        ValidationResult
    """
    source_lower = source.lower()

    if source_lower == "pubmed":
        return validate_pubmed_query(query)
    elif source_lower == "semantic":
        return validate_semantic_query(query)
    elif source_lower in ("biorxiv", "medrxiv"):
        return validate_biorxiv_query(query)
    elif source_lower == "scholar":
        # Google Scholar has minimal validation needs
        return validate_semantic_query(query)
    else:
        return ValidationResult(
            is_valid=True,
            warnings=[f"No specific validation available for source: {source}"]
        )


def validate_for_all_sources(query: str, sources: List[str]) -> dict:
    """
    Validate query for multiple database sources.

    Args:
        query: Search query string
        sources: List of database sources

    Returns:
        Dictionary mapping source names to ValidationResults
    """
    return {source: validate_query(query, source) for source in sources}


def check_pubmed_publication_type(pub_type: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a publication type is valid for PubMed.

    Args:
        pub_type: Publication type string

    Returns:
        Tuple of (is_valid, suggestion)
    """
    if pub_type in PUBMED_PUBLICATION_TYPES:
        return True, None

    # Check case-insensitive
    pub_type_lower = pub_type.lower()
    for valid_type in PUBMED_PUBLICATION_TYPES:
        if valid_type.lower() == pub_type_lower:
            return True, f"Use '{valid_type}' for correct capitalization"

    # Common typos/variations
    type_mapping = {
        "reviews": "Review",
        "clinical trials": "Clinical Trial",
        "rct": "Randomized Controlled Trial",
        "case report": "Case Reports",
        "meta analysis": "Meta-Analysis",
        "systematic reviews": "Systematic Review",
        "guidelines": "Practice Guideline",
    }

    if pub_type_lower in type_mapping:
        correct = type_mapping[pub_type_lower]
        return False, f"Did you mean '{correct}'?"

    return False, None


def format_validation_report(result: ValidationResult, verbose: bool = False) -> str:
    """
    Format validation result as human-readable report.

    Args:
        result: ValidationResult to format
        verbose: Include all details

    Returns:
        Formatted string
    """
    lines = []

    if result.is_valid:
        lines.append("Query validation: PASSED")
    else:
        lines.append("Query validation: FAILED")

    if result.errors:
        lines.append("\nErrors:")
        for error in result.errors:
            lines.append(f"  - {error}")

    if result.warnings:
        lines.append("\nWarnings:")
        for warning in result.warnings:
            lines.append(f"  - {warning}")

    if verbose and result.suggestions:
        lines.append("\nSuggestions:")
        for suggestion in result.suggestions:
            lines.append(f"  - {suggestion}")

    return "\n".join(lines)


# CLI support
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Query Validator for Paper Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python query_validator.py "CRISPR[Title] AND gene therapy" --source pubmed
    python query_validator.py "machine learning" --source semantic
    python query_validator.py "protein structure" --source all
        """
    )

    parser.add_argument(
        "query",
        help="Query string to validate"
    )

    parser.add_argument(
        "--source", "-s",
        default="pubmed",
        help="Database source (pubmed, semantic, biorxiv, all)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including suggestions"
    )

    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    if args.source.lower() == "all":
        sources = ["pubmed", "semantic", "biorxiv"]
        results = validate_for_all_sources(args.query, sources)

        if args.json:
            import json
            output = {
                source: {
                    "is_valid": r.is_valid,
                    "errors": r.errors,
                    "warnings": r.warnings,
                    "suggestions": r.suggestions
                }
                for source, r in results.items()
            }
            print(json.dumps(output, indent=2))
        else:
            for source, result in results.items():
                print(f"\n=== {source.upper()} ===")
                print(format_validation_report(result, args.verbose))
    else:
        result = validate_query(args.query, args.source)

        if args.json:
            import json
            output = {
                "is_valid": result.is_valid,
                "errors": result.errors,
                "warnings": result.warnings,
                "suggestions": result.suggestions
            }
            print(json.dumps(output, indent=2))
        else:
            print(format_validation_report(result, args.verbose))

        if not result.is_valid:
            sys.exit(1)
