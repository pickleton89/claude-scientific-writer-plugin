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

# Add sources directory to path
sources_dir = Path(__file__).parent.parent / "sources"
sys.path.insert(0, str(sources_dir))


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
        help="Search query"
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

    args = parser.parse_args()

    # Parse sources
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

    # Collect results from all sources
    all_results = []

    print(f"Searching: {', '.join(sources)}", file=sys.stderr)
    print(f"Query: {args.query}", file=sys.stderr)
    print(f"Max results per source: {args.max}", file=sys.stderr)

    for source in sources:
        print(f"\n--- Searching {source} ---", file=sys.stderr)

        if source == "pubmed":
            results = search_pubmed(
                args.query, args.max,
                pubmed_date_start, pubmed_date_end,
                pub_types
            )
        elif source == "biorxiv":
            results = search_biorxiv(args.query, args.max, biorxiv_date_start, biorxiv_date_end, "biorxiv")
        elif source == "medrxiv":
            results = search_biorxiv(args.query, args.max, biorxiv_date_start, biorxiv_date_end, "medrxiv")
        elif source == "semantic":
            results = search_semantic_scholar(
                args.query, args.max,
                year_start, year_end,
                fields=fields,
                open_access=args.open_access,
                min_citations=args.min_citations
            )
        elif source == "scholar":
            results = search_google_scholar(args.query, args.max, year_start, year_end)
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
            "query": args.query,
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
