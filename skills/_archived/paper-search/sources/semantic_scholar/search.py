#!/usr/bin/env python3
"""
Semantic Scholar Search Tool
Search academic papers using the Semantic Scholar API.

API Documentation: https://api.semanticscholar.org/
"""

import sys
import os
import argparse
import json
import re
import time
import requests
from typing import List, Dict, Optional
from urllib.parse import quote


class SemanticScholarSearcher:
    """Search Semantic Scholar using their public API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize searcher.

        Args:
            api_key: Semantic Scholar API key (optional but recommended for higher rate limits)
        """
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.session = requests.Session()

        # Set headers
        headers = {
            "User-Agent": "Claude-Scientific-Writer/1.0 (Academic Research Tool)"
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        self.session.headers.update(headers)

        # Rate limiting
        # Without key: 100 requests per 5 minutes
        # With key: 1 request per second
        self.delay = 1.0 if self.api_key else 3.0

    def search(self, query: str, max_results: int = 50,
               year_start: Optional[int] = None, year_end: Optional[int] = None,
               fields_of_study: Optional[List[str]] = None,
               open_access_only: bool = False,
               min_citations: Optional[int] = None) -> List[Dict]:
        """
        Search for papers by keyword.

        Args:
            query: Search query
            max_results: Maximum number of results (max 100 per request)
            year_start: Filter by publication year (start)
            year_end: Filter by publication year (end)
            fields_of_study: Filter by fields (e.g., ["Biology", "Medicine"])
            open_access_only: Only return open access papers
            min_citations: Minimum citation count filter

        Returns:
            List of paper metadata dictionaries
        """
        print(f"Searching Semantic Scholar: {query}", file=sys.stderr)

        # Build query parameters
        fields = [
            "paperId",
            "title",
            "abstract",
            "year",
            "citationCount",
            "influentialCitationCount",
            "authors",
            "venue",
            "publicationVenue",
            "externalIds",
            "url",
            "openAccessPdf",
            "fieldsOfStudy",
            "publicationDate",
        ]

        params = {
            "query": query,
            "limit": min(max_results, 100),  # API max is 100
            "fields": ",".join(fields),
        }

        # Add year filter
        if year_start or year_end:
            year_filter = ""
            if year_start and year_end:
                year_filter = f"{year_start}-{year_end}"
            elif year_start:
                year_filter = f"{year_start}-"
            else:
                year_filter = f"-{year_end}"
            params["year"] = year_filter

        # Add fields of study filter
        if fields_of_study:
            params["fieldsOfStudy"] = ",".join(fields_of_study)

        # Add open access filter
        if open_access_only:
            params["openAccessPdf"] = ""

        results = []
        offset = 0

        while len(results) < max_results:
            params["offset"] = offset

            try:
                response = self.session.get(
                    f"{self.base_url}/paper/search",
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                papers = data.get("data", [])

                if not papers:
                    break

                for paper in papers:
                    if len(results) >= max_results:
                        break

                    # Apply citation filter
                    if min_citations:
                        citations = paper.get("citationCount", 0) or 0
                        if citations < min_citations:
                            continue

                    metadata = self._extract_metadata(paper)
                    results.append(metadata)

                print(f"Retrieved {len(results)} papers", file=sys.stderr)

                # Check if more results available
                total = data.get("total", 0)
                offset += len(papers)

                if offset >= total:
                    break

                # Rate limiting
                time.sleep(self.delay)

            except requests.exceptions.RequestException as e:
                print(f"Error searching Semantic Scholar: {e}", file=sys.stderr)
                break
            except json.JSONDecodeError as e:
                print(f"Error parsing response: {e}", file=sys.stderr)
                break

        print(f"Found {len(results)} papers", file=sys.stderr)
        return results

    def get_paper(self, paper_id: str) -> Optional[Dict]:
        """
        Get a specific paper by ID.

        Args:
            paper_id: Semantic Scholar paper ID, DOI, arXiv ID, etc.
                     Examples: "649def34f8be52c8b66281af98ae884c09aef38b"
                              "DOI:10.1038/nature12373"
                              "ARXIV:2106.15928"

        Returns:
            Paper metadata or None if not found
        """
        fields = [
            "paperId",
            "title",
            "abstract",
            "year",
            "citationCount",
            "influentialCitationCount",
            "authors",
            "venue",
            "publicationVenue",
            "externalIds",
            "url",
            "openAccessPdf",
            "fieldsOfStudy",
            "publicationDate",
            "references",
            "citations",
        ]

        try:
            response = self.session.get(
                f"{self.base_url}/paper/{quote(paper_id, safe='')}",
                params={"fields": ",".join(fields)},
                timeout=30
            )
            response.raise_for_status()
            paper = response.json()
            return self._extract_metadata(paper, include_refs=True)

        except Exception as e:
            print(f"Error fetching paper {paper_id}: {e}", file=sys.stderr)
            return None

    def get_author(self, author_id: str) -> Optional[Dict]:
        """
        Get author information.

        Args:
            author_id: Semantic Scholar author ID

        Returns:
            Author metadata or None if not found
        """
        try:
            response = self.session.get(
                f"{self.base_url}/author/{author_id}",
                params={
                    "fields": "authorId,name,affiliations,paperCount,citationCount,hIndex"
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"Error fetching author {author_id}: {e}", file=sys.stderr)
            return None

    def get_author_papers(self, author_id: str, max_results: int = 50) -> List[Dict]:
        """
        Get papers by a specific author.

        Args:
            author_id: Semantic Scholar author ID
            max_results: Maximum number of papers to return

        Returns:
            List of paper metadata
        """
        fields = [
            "paperId",
            "title",
            "year",
            "citationCount",
            "venue",
            "externalIds",
        ]

        try:
            response = self.session.get(
                f"{self.base_url}/author/{author_id}/papers",
                params={
                    "fields": ",".join(fields),
                    "limit": min(max_results, 100)
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return [self._extract_metadata(p) for p in data.get("data", [])]

        except Exception as e:
            print(f"Error fetching author papers: {e}", file=sys.stderr)
            return []

    def get_citations(self, paper_id: str, max_results: int = 50) -> List[Dict]:
        """
        Get papers that cite a given paper.

        Args:
            paper_id: Semantic Scholar paper ID or DOI
            max_results: Maximum number of citing papers

        Returns:
            List of citing paper metadata
        """
        fields = [
            "paperId",
            "title",
            "year",
            "citationCount",
            "authors",
            "venue",
            "externalIds",
        ]

        try:
            response = self.session.get(
                f"{self.base_url}/paper/{quote(paper_id, safe='')}/citations",
                params={
                    "fields": ",".join(fields),
                    "limit": min(max_results, 100)
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return [
                self._extract_metadata(item.get("citingPaper", {}))
                for item in data.get("data", [])
            ]

        except Exception as e:
            print(f"Error fetching citations: {e}", file=sys.stderr)
            return []

    def get_references(self, paper_id: str, max_results: int = 50) -> List[Dict]:
        """
        Get papers referenced by a given paper.

        Args:
            paper_id: Semantic Scholar paper ID or DOI
            max_results: Maximum number of referenced papers

        Returns:
            List of referenced paper metadata
        """
        fields = [
            "paperId",
            "title",
            "year",
            "citationCount",
            "authors",
            "venue",
            "externalIds",
        ]

        try:
            response = self.session.get(
                f"{self.base_url}/paper/{quote(paper_id, safe='')}/references",
                params={
                    "fields": ",".join(fields),
                    "limit": min(max_results, 100)
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return [
                self._extract_metadata(item.get("citedPaper", {}))
                for item in data.get("data", [])
            ]

        except Exception as e:
            print(f"Error fetching references: {e}", file=sys.stderr)
            return []

    def _extract_metadata(self, paper: Dict, include_refs: bool = False) -> Dict:
        """Extract standardized metadata from API response."""
        # Extract external IDs
        external_ids = paper.get("externalIds", {}) or {}
        doi = external_ids.get("DOI", "")
        pmid = external_ids.get("PubMed", "")
        arxiv_id = external_ids.get("ArXiv", "")

        # Extract authors
        authors = paper.get("authors", []) or []
        author_names = [a.get("name", "") for a in authors if a.get("name")]
        formatted_authors = " and ".join(author_names)

        # Extract open access PDF
        open_access = paper.get("openAccessPdf", {}) or {}
        pdf_url = open_access.get("url", "")

        # Extract venue name
        venue = paper.get("venue", "")
        if not venue:
            pub_venue = paper.get("publicationVenue", {}) or {}
            venue = pub_venue.get("name", "")

        metadata = {
            "paper_id": paper.get("paperId", ""),
            "doi": doi,
            "pmid": pmid,
            "arxiv_id": arxiv_id,
            "title": paper.get("title", ""),
            "authors": formatted_authors,
            "abstract": paper.get("abstract", ""),
            "year": paper.get("year", ""),
            "venue": venue,
            "citation_count": paper.get("citationCount", 0),
            "influential_citations": paper.get("influentialCitationCount", 0),
            "fields_of_study": paper.get("fieldsOfStudy", []) or [],
            "url": paper.get("url", ""),
            "pdf_url": pdf_url,
            "publication_date": paper.get("publicationDate", ""),
        }

        # Include reference/citation counts if available
        if include_refs:
            refs = paper.get("references", []) or []
            cites = paper.get("citations", []) or []
            metadata["reference_count"] = len(refs)
            metadata["citing_paper_count"] = len(cites)

        return metadata

    def metadata_to_bibtex(self, metadata: Dict) -> str:
        """Convert metadata to BibTeX format."""
        # Generate citation key
        if metadata.get("authors"):
            first_author = metadata["authors"].split(" and ")[0]
            last_name = first_author.split()[-1] if first_author else "Unknown"
        else:
            last_name = "Unknown"

        year = metadata.get("year", "XXXX")

        # Get keyword from title
        title = metadata.get("title", "")
        words = re.findall(r'\b[a-zA-Z]{4,}\b', title)
        keyword = words[0].lower() if words else "paper"

        citation_key = f"{last_name}{year}{keyword}"

        # Determine entry type
        venue = (metadata.get("venue", "") or "").lower()
        if "conference" in venue or "proceedings" in venue or "workshop" in venue:
            entry_type = "inproceedings"
            venue_field = "booktitle"
        else:
            entry_type = "article"
            venue_field = "journal"

        # Build BibTeX entry
        lines = [f"@{entry_type}{{{citation_key},"]

        if metadata.get("authors"):
            lines.append(f'  author       = {{{metadata["authors"]}}},')

        if metadata.get("title"):
            lines.append(f'  title        = {{{metadata["title"]}}},')

        if metadata.get("venue"):
            lines.append(f'  {venue_field:12} = {{{metadata["venue"]}}},')

        if metadata.get("year"):
            lines.append(f'  year         = {{{metadata["year"]}}},')

        if metadata.get("doi"):
            lines.append(f'  doi          = {{{metadata["doi"]}}},')

        if metadata.get("url"):
            lines.append(f'  url          = {{{metadata["url"]}}},')

        if metadata.get("arxiv_id"):
            lines.append(f'  eprint       = {{{metadata["arxiv_id"]}}},')
            lines.append(f'  archiveprefix = {{arXiv}},')

        if metadata.get("pmid"):
            lines.append(f'  note         = {{PMID: {metadata["pmid"]}}},')

        # Remove trailing comma from last field
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]

        lines.append("}")

        return "\n".join(lines)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Search Semantic Scholar (200M+ academic papers)",
        epilog="Example: python search.py 'transformer attention mechanism' --limit 50"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for papers")
    search_parser.add_argument(
        "query",
        help="Search query"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of results (default: 50)"
    )
    search_parser.add_argument(
        "--year-start",
        type=int,
        help="Filter by start year"
    )
    search_parser.add_argument(
        "--year-end",
        type=int,
        help="Filter by end year"
    )
    search_parser.add_argument(
        "--fields",
        help="Filter by fields of study (comma-separated)"
    )
    search_parser.add_argument(
        "--open-access",
        action="store_true",
        help="Only return open access papers"
    )
    search_parser.add_argument(
        "--min-citations",
        type=int,
        help="Minimum citation count"
    )
    search_parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)"
    )
    search_parser.add_argument(
        "--format",
        choices=["json", "bibtex"],
        default="json",
        help="Output format (default: json)"
    )

    # Paper command
    paper_parser = subparsers.add_parser("paper", help="Get paper details")
    paper_parser.add_argument(
        "paper_id",
        help="Paper ID, DOI (prefix with 'DOI:'), or arXiv ID (prefix with 'ARXIV:')"
    )

    # Citations command
    cite_parser = subparsers.add_parser("citations", help="Get papers citing a paper")
    cite_parser.add_argument("paper_id", help="Paper ID or DOI")
    cite_parser.add_argument("--limit", type=int, default=50, help="Max results")

    # References command
    ref_parser = subparsers.add_parser("references", help="Get papers referenced by a paper")
    ref_parser.add_argument("paper_id", help="Paper ID or DOI")
    ref_parser.add_argument("--limit", type=int, default=50, help="Max results")

    # Author command
    author_parser = subparsers.add_parser("author", help="Get author info and papers")
    author_parser.add_argument("author_id", help="Semantic Scholar author ID")
    author_parser.add_argument("--papers", action="store_true", help="Include author's papers")
    author_parser.add_argument("--limit", type=int, default=50, help="Max papers")

    # API key option for all commands
    parser.add_argument(
        "--api-key",
        help="Semantic Scholar API key (or set SEMANTIC_SCHOLAR_API_KEY env var)"
    )

    args = parser.parse_args()

    # Default to search if no command specified
    if not args.command:
        parser.print_help()
        print("\n\nFor basic search, use: python search.py search 'your query'")
        sys.exit(1)

    # Initialize searcher
    api_key = getattr(args, 'api_key', None)
    searcher = SemanticScholarSearcher(api_key=api_key)

    # Execute command
    if args.command == "search":
        fields = None
        if args.fields:
            fields = [f.strip() for f in args.fields.split(",")]

        results = searcher.search(
            args.query,
            max_results=args.limit,
            year_start=args.year_start,
            year_end=args.year_end,
            fields_of_study=fields,
            open_access_only=args.open_access,
            min_citations=args.min_citations
        )

        if not results:
            print("No results found", file=sys.stderr)
            sys.exit(1)

        # Format output
        if args.format == "json":
            output = json.dumps({
                "query": args.query,
                "count": len(results),
                "results": results
            }, indent=2)
        else:  # bibtex
            bibtex_entries = [searcher.metadata_to_bibtex(r) for r in results]
            output = "\n\n".join(bibtex_entries) + "\n"

        # Write output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Wrote {len(results)} results to {args.output}", file=sys.stderr)
        else:
            print(output)

    elif args.command == "paper":
        result = searcher.get_paper(args.paper_id)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("Paper not found", file=sys.stderr)
            sys.exit(1)

    elif args.command == "citations":
        results = searcher.get_citations(args.paper_id, max_results=args.limit)
        print(json.dumps({"count": len(results), "results": results}, indent=2))

    elif args.command == "references":
        results = searcher.get_references(args.paper_id, max_results=args.limit)
        print(json.dumps({"count": len(results), "results": results}, indent=2))

    elif args.command == "author":
        author = searcher.get_author(args.author_id)
        if author:
            if args.papers:
                papers = searcher.get_author_papers(args.author_id, max_results=args.limit)
                author["papers"] = papers
            print(json.dumps(author, indent=2))
        else:
            print("Author not found", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
