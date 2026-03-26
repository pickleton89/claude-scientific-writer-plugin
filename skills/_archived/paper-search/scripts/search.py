#!/usr/bin/env python3
"""
Unified Academic Paper Search CLI

Search across multiple academic databases with a single interface.

Supported sources:
    - pubmed: Biomedical literature (PubMed/NCBI)
    - biorxiv: Biology preprints
    - medrxiv: Medical preprints
    - semantic: Semantic Scholar (200M+ papers)
    - scholar: Google Scholar

Usage:
    python search.py "CRISPR gene therapy" --source pubmed --max 50
    python search.py "machine learning" --source semantic,biorxiv --max 20
    python search.py "protein folding" --source all --output results.json
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional, Set, Union

# Add directories to path
scripts_dir = Path(__file__).parent
sources_dir = Path(__file__).parent.parent / "sources"
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(sources_dir))

# Import deterministic utilities
from query_templates import (
    build_query, list_templates, get_template_info,
    format_template_help, TemplateError
)
from database_router import (
    select_databases, get_routing_result, get_routing_explanation
)
from query_schema import (
    StructuredQuery, load_query_from_json, load_query_from_string,
    validate_query_schema
)
from query_validator import (
    validate_query, validate_for_all_sources, format_validation_report
)


def normalize_date(
    date_str: str, for_source: str
) -> Union[tuple, tuple]:  # Returns (str, str) or (int, int) based on source
    """
    Parse a date range string and return start/end dates.

    Handles formats:
        - "2024" -> year only
        - "2023:2024" -> year range
        - "2023-01-01:2024-12-31" -> full date range
        - "2024:" -> from year to present
        - ":2024" -> up to year

    Returns:
        For semantic/scholar: tuple of Optional[int] (year integers)
        For pubmed/biorxiv/medrxiv: tuple of Optional[str] (date strings)
    """
    if not date_str:
        return None, None

    # Parse start and end from range
    if ":" in date_str:
        parts = date_str.split(":", 1)
        start = parts[0].strip() if parts[0].strip() else None
        end = parts[1].strip() if parts[1].strip() else None
    else:
        # Single value = both start and end
        start = date_str.strip()
        end = date_str.strip()

    # For year-only values, extract just the year for sources that need integers
    def extract_year(val: str) -> Optional[int]:
        if not val:
            return None
        # Extract first 4 digits as year
        year_str = val[:4] if len(val) >= 4 else val
        try:
            return int(year_str)
        except ValueError:
            return None

    if for_source in ("semantic", "scholar"):
        # These use integer years
        return extract_year(start), extract_year(end)
    elif for_source == "pubmed":
        # PubMed accepts YYYY or YYYY/MM/DD
        # Convert YYYY-MM-DD to YYYY/MM/DD if needed
        if start:
            start = start.replace("-", "/")
        if end:
            end = end.replace("-", "/")
        return start, end
    elif for_source in ("biorxiv", "medrxiv"):
        # bioRxiv needs YYYY-MM-DD format
        # If only year provided, add month/day
        if start and len(start) == 4:
            start = f"{start}-01-01"
        if end and len(end) == 4:
            end = f"{end}-12-31"
        return start, end

    return start, end


def search_pubmed(query: str, max_results: int, date_start: Optional[str],
                  date_end: Optional[str], pub_types: Optional[List[str]]) -> List[Dict]:
    """Search PubMed and return results.

    Args:
        date_start: Start date in YYYY or YYYY/MM/DD format (pre-normalized)
        date_end: End date in YYYY or YYYY/MM/DD format (pre-normalized)
    """
    try:
        from pubmed.search import PubMedSearcher
    except ImportError as e:
        print(f"Error importing PubMed searcher: {e}", file=sys.stderr)
        return []

    searcher = PubMedSearcher()
    pmids = searcher.search(
        query,
        max_results=max_results,
        date_start=date_start,
        date_end=date_end,
        publication_types=pub_types
    )

    if not pmids:
        return []

    # Fetch full metadata
    results = searcher.fetch_metadata(pmids)

    # Add source field for unified results
    for r in results:
        r["source"] = "pubmed"

    return results


def search_biorxiv(query: str, max_results: int, date_start: Optional[str],
                   date_end: Optional[str], server: str = "biorxiv") -> List[Dict]:
    """Search bioRxiv or medRxiv and return results.

    Args:
        date_start: Start date in YYYY-MM-DD format (pre-normalized)
        date_end: End date in YYYY-MM-DD format (pre-normalized)
    """
    try:
        from biorxiv.search import BioRxivSearcher
    except ImportError as e:
        print(f"Error importing bioRxiv searcher: {e}", file=sys.stderr)
        return []

    searcher = BioRxivSearcher(server=server)
    results = searcher.search(
        query,
        max_results=max_results,
        date_start=date_start,
        date_end=date_end
    )

    # Add source field
    for r in results:
        r["source"] = server

    return results


def search_semantic_scholar(query: str, max_results: int,
                            year_start: Optional[int], year_end: Optional[int],
                            fields: Optional[List[str]] = None,
                            open_access: bool = False,
                            min_citations: Optional[int] = None) -> List[Dict]:
    """Search Semantic Scholar and return results."""
    try:
        from semantic_scholar.search import SemanticScholarSearcher
    except ImportError as e:
        print(f"Error importing Semantic Scholar searcher: {e}", file=sys.stderr)
        return []

    searcher = SemanticScholarSearcher()
    results = searcher.search(
        query,
        max_results=max_results,
        year_start=year_start,
        year_end=year_end,
        fields_of_study=fields,
        open_access_only=open_access,
        min_citations=min_citations
    )

    # Add source field
    for r in results:
        r["source"] = "semantic_scholar"

    return results


def search_google_scholar(query: str, max_results: int,
                          year_start: Optional[int], year_end: Optional[int]) -> List[Dict]:
    """Search Google Scholar and return results."""
    try:
        from google_scholar.search import GoogleScholarSearcher, SCHOLARLY_AVAILABLE
        if not SCHOLARLY_AVAILABLE:
            print("Warning: scholarly library not installed. Skipping Google Scholar.",
                  file=sys.stderr)
            return []
    except ImportError as e:
        print(f"Error importing Google Scholar searcher: {e}", file=sys.stderr)
        return []

    searcher = GoogleScholarSearcher()
    results = searcher.search(
        query,
        max_results=max_results,
        year_start=year_start,
        year_end=year_end
    )

    # Add source field
    for r in results:
        r["source"] = "google_scholar"

    return results


def deduplicate_by_doi(results: List[Dict]) -> List[Dict]:
    """
    Deduplicate results by DOI, keeping the first occurrence.

    Results without DOI are kept.
    """
    seen_dois: Set[str] = set()
    unique_results = []

    for result in results:
        doi = result.get("doi", "")
        if not doi:
            # Keep results without DOI
            unique_results.append(result)
        elif doi.lower() not in seen_dois:
            seen_dois.add(doi.lower())
            unique_results.append(result)

    return unique_results


def results_to_bibtex(results: List[Dict]) -> str:
    """Convert results to BibTeX format."""
    bibtex_entries = []

    # Cache searcher instances to avoid repeated imports/instantiation
    searchers: Dict[str, object] = {}

    def get_searcher(source: str):
        """Get or create a cached searcher instance."""
        if source in searchers:
            return searchers[source]

        try:
            if source == "pubmed":
                from pubmed.search import PubMedSearcher
                searchers[source] = PubMedSearcher()
            elif source in ("biorxiv", "medrxiv"):
                from biorxiv.search import BioRxivSearcher
                searchers[source] = BioRxivSearcher(server=source)
            elif source == "semantic_scholar":
                from semantic_scholar.search import SemanticScholarSearcher
                searchers[source] = SemanticScholarSearcher()
            elif source == "google_scholar":
                from google_scholar.search import GoogleScholarSearcher
                searchers[source] = GoogleScholarSearcher()
        except ImportError as e:
            print(f"Warning: Could not import searcher for {source}: {e}", file=sys.stderr)
            return None

        return searchers.get(source)

    for result in results:
        source = result.get("source", "")

        try:
            searcher = get_searcher(source)
            if searcher and hasattr(searcher, "metadata_to_bibtex"):
                bibtex_entries.append(searcher.metadata_to_bibtex(result))
            else:
                bibtex_entries.append(generic_to_bibtex(result))
        except Exception as e:
            print(f"Error converting to BibTeX: {e}", file=sys.stderr)
            bibtex_entries.append(generic_to_bibtex(result))

    return "\n\n".join(bibtex_entries) + "\n"


def generic_to_bibtex(metadata: Dict) -> str:
    """Generic BibTeX conversion for any result."""
    import re

    # Generate citation key
    authors = metadata.get("authors", "")
    if authors:
        first_author = authors.split(" and ")[0].split(",")[0].strip()
        last_name = first_author.split()[-1] if first_author else "Unknown"
    else:
        last_name = "Unknown"

    year = str(metadata.get("year", "XXXX"))

    # Get keyword from title
    title = metadata.get("title", "")
    words = re.findall(r'\b[a-zA-Z]{4,}\b', title)
    keyword = words[0].lower() if words else "paper"

    citation_key = f"{last_name}{year}{keyword}"

    lines = [f"@article{{{citation_key},"]

    if metadata.get("authors"):
        lines.append(f'  author  = {{{metadata["authors"]}}},')
    if metadata.get("title"):
        lines.append(f'  title   = {{{metadata["title"]}}},')
    if metadata.get("venue") or metadata.get("journal"):
        venue = metadata.get("venue", metadata.get("journal", ""))
        lines.append(f'  journal = {{{venue}}},')
    if metadata.get("year"):
        lines.append(f'  year    = {{{metadata["year"]}}},')
    if metadata.get("doi"):
        lines.append(f'  doi     = {{{metadata["doi"]}}},')

    # Remove trailing comma
    if lines[-1].endswith(","):
        lines[-1] = lines[-1][:-1]

    lines.append("}")
    return "\n".join(lines)


def results_to_text(results: List[Dict]) -> str:
    """Convert results to human-readable text format."""
    lines = []

    for i, result in enumerate(results, 1):
        lines.append(f"[{i}] {result.get('title', 'No title')}")

        authors = result.get("authors", "")
        if authors:
            # Truncate long author lists
            if len(authors) > 100:
                authors = authors[:97] + "..."
            lines.append(f"    Authors: {authors}")

        year = result.get("year", "")
        venue = result.get("venue", result.get("journal", ""))
        if year or venue:
            pub_info = []
            if venue:
                pub_info.append(venue)
            if year:
                pub_info.append(f"({year})")
            lines.append(f"    Published: {' '.join(pub_info)}")

        doi = result.get("doi", "")
        if doi:
            lines.append(f"    DOI: {doi}")

        source = result.get("source", "")
        if source:
            lines.append(f"    Source: {source}")

        lines.append("")  # Blank line between entries

    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Unified academic paper search across multiple databases",
        epilog="""
Examples:
    python search.py "CRISPR gene therapy" --source pubmed --max 50
    python search.py "machine learning" --source semantic,biorxiv --max 20
    python search.py "CAR-T cell" --source all --date 2023:2024 --output results.json
    python search.py "protein folding" --source semantic --format bibtex
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "query",
        nargs="?",  # Optional when using --list-templates
        default="",
        help="Search query (required unless using --list-templates)"
    )

    parser.add_argument(
        "--source", "-s",
        default="pubmed",
        help="""Database(s) to search. Options:
            pubmed   - Biomedical literature (NCBI/PubMed)
            biorxiv  - Biology preprints
            medrxiv  - Medical preprints
            semantic - Semantic Scholar (200M+ papers)
            scholar  - Google Scholar
            all      - Search all sources (deduplicated)
            Multiple sources: pubmed,biorxiv,semantic
        """
    )

    parser.add_argument(
        "--max", "-m",
        type=int,
        default=20,
        help="Maximum results per source (default: 20)"
    )

    parser.add_argument(
        "--date", "-d",
        help="Date range filter. Formats: 2024, 2023:2024, 2023-01-01:2024-12-31"
    )

    parser.add_argument(
        "--type", "-t",
        help="Publication type filter (PubMed only). Example: 'Review,Clinical Trial'"
    )

    parser.add_argument(
        "--fields",
        help="Field of study filter (Semantic Scholar only). Example: 'Biology,Medicine'"
    )

    parser.add_argument(
        "--open-access",
        action="store_true",
        help="Only open access papers (Semantic Scholar only)"
    )

    parser.add_argument(
        "--min-citations",
        type=int,
        help="Minimum citation count (Semantic Scholar only)"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["json", "bibtex", "text"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Disable deduplication when searching multiple sources"
    )

    # Deterministic query options
    parser.add_argument(
        "--template", "-T",
        help="Use a query template instead of raw query. Use --list-templates to see options."
    )

    parser.add_argument(
        "--template-params", "-P",
        nargs="*",
        metavar="KEY=VALUE",
        help="Parameters for query template (e.g., topic='CRISPR' author='Doudna')"
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available query templates and exit"
    )

    parser.add_argument(
        "--auto-route",
        action="store_true",
        help="Automatically select databases based on query content"
    )

    parser.add_argument(
        "--domain-hint",
        choices=["biomedical", "cs", "comprehensive", "preprint"],
        help="Hint for automatic database routing"
    )

    # Phase 2: Structured query and validation
    parser.add_argument(
        "--query-file", "-Q",
        help="Load query from JSON schema file (see --show-schema for format)"
    )

    parser.add_argument(
        "--query-json",
        help="Load query from inline JSON string"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate query syntax before searching (recommended)"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate query, do not execute search"
    )

    parser.add_argument(
        "--show-schema",
        action="store_true",
        help="Show JSON schema format and exit"
    )

    args = parser.parse_args()

    # Handle --show-schema
    if args.show_schema:
        print("""Structured Query JSON Schema
============================

Fields:
  concepts          (required) List of search terms
  operator          (optional) "AND" or "OR" (default: "AND")
  synonyms          (optional) Term expansions as {"term": ["syn1", "syn2"]}
  field_constraints (optional) Field filters as {"author": "...", "title": "..."}
  date_range        (optional) Date filter as {"start": "2020", "end": "2024"}
  publication_types (optional) PubMed types: ["Review", "Meta-Analysis", ...]
  fields_of_study   (optional) Semantic Scholar fields: ["Biology", "Medicine", ...]
  min_citations     (optional) Minimum citation count (integer)
  open_access       (optional) Filter for open access only (true/false)
  exclude_terms     (optional) Terms to exclude: ["review", "survey"]

Full Example:
{
    "concepts": ["CRISPR", "gene therapy"],
    "operator": "AND",
    "synonyms": {"CRISPR": ["CRISPR-Cas9", "CRISPR/Cas9"]},
    "field_constraints": {"author": "Doudna JA"},
    "date_range": {"start": "2020", "end": "2024"},
    "publication_types": ["Review"],
    "min_citations": 10,
    "open_access": true,
    "exclude_terms": ["protocol"]
}

Minimal Examples:
  {"concepts": ["CRISPR", "gene therapy"]}
  {"concepts": ["cancer"], "date_range": {"start": "2022"}}
""")
        sys.exit(0)

    # Handle --list-templates
    if args.list_templates:
        print(format_template_help())
        sys.exit(0)

    # Handle structured query from file or JSON string
    structured_query = None
    if args.query_file:
        try:
            structured_query = load_query_from_json(args.query_file)
            print(f"Loaded query from: {args.query_file}", file=sys.stderr)
        except FileNotFoundError:
            print(f"Error: Query file not found: {args.query_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in query file: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: Invalid query schema: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.query_json:
        try:
            structured_query = load_query_from_string(args.query_json)
            print("Loaded query from inline JSON", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON string: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: Invalid query schema: {e}", file=sys.stderr)
            sys.exit(1)

    # Validate query is provided for actual searches
    if not args.query and not args.template and not structured_query:
        parser.error("query is required (or use --template, --query-file, or --query-json)")

    # Handle template-based query construction
    query = args.query or ""
    if args.template:
        # Parse template parameters
        template_params = {}
        if args.template_params:
            for param in args.template_params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    # Strip quotes from value
                    value = value.strip("'\"")
                    template_params[key.strip()] = value
                else:
                    print(f"Invalid parameter format: {param} (expected key=value)",
                          file=sys.stderr)
                    sys.exit(1)

        # If query is provided without 'topic', use it as topic
        if query and "topic" not in template_params:
            template_params["topic"] = query

        try:
            query = build_query(args.template, **template_params)
            print(f"Built query from template '{args.template}': {query}", file=sys.stderr)
        except TemplateError as e:
            print(f"Template error: {e}", file=sys.stderr)
            sys.exit(1)

    # Handle structured query (overrides template if both provided)
    if structured_query:
        # Use PubMed format as the default display query for routing/logging
        # Source-specific query generation happens per-source in the search loop
        query = structured_query.to_pubmed_query()
        print(f"Structured query: {query}", file=sys.stderr)

        # Apply structured query parameters to CLI args if not already set
        if structured_query.publication_types and not args.type:
            args.type = ",".join(structured_query.publication_types)
        if structured_query.fields_of_study and not args.fields:
            args.fields = ",".join(structured_query.fields_of_study)
        if structured_query.min_citations is not None and not args.min_citations:
            args.min_citations = structured_query.min_citations
        if structured_query.open_access and not args.open_access:
            args.open_access = True
        if structured_query.date_range and not args.date:
            start = structured_query.date_range.get("start", "")
            end = structured_query.date_range.get("end", "")
            if start or end:
                args.date = f"{start}:{end}"

    # Handle auto-routing for database selection
    if args.auto_route or args.domain_hint:
        routing_result = get_routing_result(query, args.domain_hint)
        sources = list(routing_result.databases)
        print(f"Auto-routing: {routing_result.explanation}", file=sys.stderr)
        print(f"Confidence: {routing_result.confidence:.0%}", file=sys.stderr)
    else:
        # Parse sources from argument
        sources = [s.strip().lower() for s in args.source.split(",")]

    # Expand "all" to all sources
    if "all" in sources:
        sources = ["pubmed", "biorxiv", "medrxiv", "semantic", "scholar"]

    # Parse date range - normalize once for each format needed
    pubmed_date_start = None
    pubmed_date_end = None
    biorxiv_date_start = None
    biorxiv_date_end = None
    year_start = None
    year_end = None

    if args.date:
        # For sources that need integer years (Semantic Scholar, Google Scholar)
        year_start, year_end = normalize_date(args.date, "semantic")
        # For PubMed (YYYY/MM/DD format)
        pubmed_date_start, pubmed_date_end = normalize_date(args.date, "pubmed")
        # For bioRxiv/medRxiv (YYYY-MM-DD format)
        biorxiv_date_start, biorxiv_date_end = normalize_date(args.date, "biorxiv")

    # Parse publication types
    pub_types = None
    if args.type:
        pub_types = [pt.strip() for pt in args.type.split(",")]

    # Parse fields of study
    fields = None
    if args.fields:
        fields = [f.strip() for f in args.fields.split(",")]

    # Validate query syntax if requested
    if args.validate or args.validate_only:
        print("\n--- Query Validation ---", file=sys.stderr)
        validation_results = validate_for_all_sources(query, sources)

        has_errors = False
        for source, result in validation_results.items():
            print(f"\n{source.upper()}:", file=sys.stderr)
            print(format_validation_report(result, verbose=True), file=sys.stderr)
            if not result.is_valid:
                has_errors = True

        if has_errors:
            print("\nValidation failed. Fix errors before searching.", file=sys.stderr)
            sys.exit(1)

        if args.validate_only:
            print("\nValidation passed. Use without --validate-only to execute search.",
                  file=sys.stderr)
            sys.exit(0)

        print("\nValidation passed. Proceeding with search...\n", file=sys.stderr)

    # Collect results from all sources
    all_results = []

    print(f"Searching: {', '.join(sources)}", file=sys.stderr)
    print(f"Query: {query}", file=sys.stderr)
    print(f"Max results per source: {args.max}", file=sys.stderr)

    for source in sources:
        print(f"\n--- Searching {source} ---", file=sys.stderr)

        # Generate source-specific query if structured query provided
        if structured_query:
            if source == "pubmed":
                source_query = structured_query.to_pubmed_query()
            elif source in ("semantic", "scholar"):
                source_query = structured_query.to_semantic_query()
            elif source in ("biorxiv", "medrxiv"):
                source_query = structured_query.to_biorxiv_query()
            else:
                source_query = query  # Fallback
            if source_query != query:
                print(f"Source-specific query: {source_query}", file=sys.stderr)
        else:
            source_query = query

        if source == "pubmed":
            results = search_pubmed(
                source_query, args.max,
                pubmed_date_start, pubmed_date_end,
                pub_types
            )
        elif source == "biorxiv":
            results = search_biorxiv(source_query, args.max, biorxiv_date_start, biorxiv_date_end, "biorxiv")
        elif source == "medrxiv":
            results = search_biorxiv(source_query, args.max, biorxiv_date_start, biorxiv_date_end, "medrxiv")
        elif source == "semantic":
            results = search_semantic_scholar(
                source_query, args.max,
                year_start, year_end,
                fields=fields,
                open_access=args.open_access,
                min_citations=args.min_citations
            )
        elif source == "scholar":
            results = search_google_scholar(source_query, args.max, year_start, year_end)
        else:
            print(f"Unknown source: {source}", file=sys.stderr)
            continue

        all_results.extend(results)
        print(f"Found {len(results)} results from {source}", file=sys.stderr)

    # Deduplicate if multiple sources
    if len(sources) > 1 and not args.no_dedupe:
        original_count = len(all_results)
        all_results = deduplicate_by_doi(all_results)
        deduped = original_count - len(all_results)
        if deduped > 0:
            print(f"\nDeduplicated {deduped} results by DOI", file=sys.stderr)

    print(f"\nTotal results: {len(all_results)}", file=sys.stderr)

    if not all_results:
        print("No results found", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.format == "json":
        output = json.dumps({
            "query": query,
            "sources": sources,
            "count": len(all_results),
            "results": all_results
        }, indent=2)
    elif args.format == "bibtex":
        output = results_to_bibtex(all_results)
    else:  # text
        output = results_to_text(all_results)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nWrote {len(all_results)} results to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
