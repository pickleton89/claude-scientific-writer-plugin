#!/usr/bin/env python3
"""
bioRxiv/medRxiv Search Tool
Search preprint servers using the bioRxiv API.

API Documentation: https://api.biorxiv.org/
"""

import sys
import argparse
import json
import re
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class BioRxivSearcher:
    """Search bioRxiv/medRxiv using their public API."""

    def __init__(self, server: str = "biorxiv"):
        """
        Initialize searcher.

        Args:
            server: Server to search ('biorxiv' or 'medrxiv')
        """
        self.server = server.lower()
        if self.server not in ("biorxiv", "medrxiv"):
            raise ValueError(f"Invalid server: {server}. Use 'biorxiv' or 'medrxiv'")

        self.base_url = "https://api.biorxiv.org"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Claude-Scientific-Writer/1.0 (Academic Research Tool)"
        })

        # Rate limiting: ~30 requests per minute recommended
        self.delay = 2.0

    def search(self, query: str, max_results: int = 50,
               date_start: Optional[str] = None, date_end: Optional[str] = None,
               category: Optional[str] = None) -> List[Dict]:
        """
        Search bioRxiv/medRxiv for preprints.

        The bioRxiv API doesn't support direct text search, so we use the
        content endpoint with date filtering and post-filter by keywords.

        Args:
            query: Search query (keywords to match in title/abstract)
            max_results: Maximum number of results to return
            date_start: Start date (YYYY-MM-DD), defaults to 30 days ago
            date_end: End date (YYYY-MM-DD), defaults to today
            category: Subject category filter (optional)

        Returns:
            List of preprint metadata dictionaries
        """
        # Default date range: last 30 days
        if not date_end:
            date_end = datetime.now().strftime("%Y-%m-%d")
        if not date_start:
            start_dt = datetime.now() - timedelta(days=30)
            date_start = start_dt.strftime("%Y-%m-%d")

        print(f"Searching {self.server}: {query}", file=sys.stderr)
        print(f"Date range: {date_start} to {date_end}", file=sys.stderr)

        # Parse query into keywords for filtering
        keywords = [kw.strip().lower() for kw in query.split() if len(kw.strip()) > 2]

        results = []
        cursor = 0
        page_size = 100  # API max is 100 per page

        while len(results) < max_results:
            # Construct API URL
            # Endpoint: /details/{server}/{start_date}/{end_date}/{cursor}
            url = f"{self.base_url}/details/{self.server}/{date_start}/{date_end}/{cursor}"

            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()

                # Check for valid response
                if "collection" not in data:
                    print(f"No collection in response", file=sys.stderr)
                    break

                papers = data["collection"]

                if not papers:
                    break

                # Filter papers by keywords
                for paper in papers:
                    if len(results) >= max_results:
                        break

                    # Apply category filter
                    if category:
                        paper_category = paper.get("category", "").lower()
                        if category.lower() not in paper_category:
                            continue

                    # Apply keyword filter (match in title or abstract)
                    title = paper.get("title", "").lower()
                    abstract = paper.get("abstract", "").lower()
                    combined_text = f"{title} {abstract}"

                    # Check if any keyword matches
                    if keywords and not any(kw in combined_text for kw in keywords):
                        continue

                    # Extract metadata
                    metadata = self._extract_metadata(paper)
                    results.append(metadata)

                print(f"Processed {cursor + len(papers)} papers, found {len(results)} matches",
                      file=sys.stderr)

                # Move to next page
                cursor += page_size

                # Check if we've reached the end
                total_str = data.get("messages", [{}])[0].get("total", 0)
                total = int(total_str) if total_str else 0
                if cursor >= total:
                    break

                # Rate limiting
                time.sleep(self.delay)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching from {self.server}: {e}", file=sys.stderr)
                break
            except json.JSONDecodeError as e:
                print(f"Error parsing response: {e}", file=sys.stderr)
                break

        print(f"Found {len(results)} matching preprints", file=sys.stderr)
        return results

    def search_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Fetch a specific preprint by DOI.

        Args:
            doi: The DOI of the preprint (e.g., "10.1101/2024.01.01.123456")

        Returns:
            Preprint metadata or None if not found
        """
        # Extract the bioRxiv-specific part of the DOI
        doi_suffix = doi.replace("10.1101/", "")

        url = f"{self.base_url}/details/{self.server}/{doi_suffix}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "collection" in data and data["collection"]:
                return self._extract_metadata(data["collection"][0])

        except Exception as e:
            print(f"Error fetching DOI {doi}: {e}", file=sys.stderr)

        return None

    def get_categories(self) -> List[str]:
        """
        Get list of valid subject categories.

        Returns:
            List of category names
        """
        # bioRxiv subject categories
        biorxiv_categories = [
            "animal behavior and cognition",
            "biochemistry",
            "bioengineering",
            "bioinformatics",
            "biophysics",
            "cancer biology",
            "cell biology",
            "clinical trials",
            "developmental biology",
            "ecology",
            "epidemiology",
            "evolutionary biology",
            "genetics",
            "genomics",
            "immunology",
            "microbiology",
            "molecular biology",
            "neuroscience",
            "paleontology",
            "pathology",
            "pharmacology and toxicology",
            "physiology",
            "plant biology",
            "scientific communication and education",
            "synthetic biology",
            "systems biology",
            "zoology",
        ]

        # medRxiv categories
        medrxiv_categories = [
            "addiction medicine",
            "allergy and immunology",
            "anesthesia",
            "cardiovascular medicine",
            "dentistry and oral medicine",
            "dermatology",
            "emergency medicine",
            "endocrinology",
            "epidemiology",
            "forensic medicine",
            "gastroenterology",
            "genetic and genomic medicine",
            "geriatric medicine",
            "health economics",
            "health informatics",
            "health policy",
            "health systems and quality improvement",
            "hematology",
            "hiv/aids",
            "infectious diseases",
            "intensive care and critical care medicine",
            "medical education",
            "medical ethics",
            "nephrology",
            "neurology",
            "nursing",
            "nutrition",
            "obstetrics and gynecology",
            "occupational and environmental health",
            "oncology",
            "ophthalmology",
            "orthopedics",
            "otolaryngology",
            "pain medicine",
            "palliative medicine",
            "pathology",
            "pediatrics",
            "pharmacology and therapeutics",
            "primary care research",
            "psychiatry and clinical psychology",
            "public and global health",
            "radiology and imaging",
            "rehabilitation medicine and physical therapy",
            "respiratory medicine",
            "rheumatology",
            "sexual and reproductive health",
            "sports medicine",
            "surgery",
            "toxicology",
            "transplantation",
            "urology",
        ]

        return biorxiv_categories if self.server == "biorxiv" else medrxiv_categories

    def _extract_metadata(self, paper: Dict) -> Dict:
        """Extract standardized metadata from API response."""
        # Parse authors (format: "LastName, FirstName; LastName, FirstName; ...")
        authors_str = paper.get("authors", "")
        authors_list = [a.strip() for a in authors_str.split(";") if a.strip()]

        # Convert to standard format
        formatted_authors = " and ".join(authors_list) if authors_list else ""

        # Build DOI
        doi = paper.get("doi", "")
        if doi and not doi.startswith("10.1101/"):
            doi = f"10.1101/{doi}"

        return {
            "doi": doi,
            "title": paper.get("title", ""),
            "authors": formatted_authors,
            "abstract": paper.get("abstract", ""),
            "date": paper.get("date", ""),
            "category": paper.get("category", ""),
            "server": self.server,
            "version": paper.get("version", "1"),
            "published": paper.get("published", "NA"),  # "NA" or journal name if published
            "url": f"https://www.{self.server}.org/content/{doi}" if doi else "",
            "pdf_url": f"https://www.{self.server}.org/content/{doi}.full.pdf" if doi else "",
        }

    def metadata_to_bibtex(self, metadata: Dict) -> str:
        """Convert metadata to BibTeX format."""
        # Generate citation key
        if metadata.get("authors"):
            first_author = metadata["authors"].split(" and ")[0]
            if "," in first_author:
                last_name = first_author.split(",")[0].strip()
            else:
                last_name = first_author.split()[-1] if first_author.split() else "Unknown"
        else:
            last_name = "Unknown"

        # Extract year from date
        date = metadata.get("date", "")
        year = date[:4] if len(date) >= 4 else "XXXX"

        # Get keyword from title
        title = metadata.get("title", "")
        words = re.findall(r'\b[a-zA-Z]{4,}\b', title)
        keyword = words[0].lower() if words else "preprint"

        citation_key = f"{last_name}{year}{keyword}"

        # Build BibTeX entry
        lines = [f"@article{{{citation_key},"]

        if metadata.get("authors"):
            lines.append(f'  author    = {{{metadata["authors"]}}},')

        if metadata.get("title"):
            lines.append(f'  title     = {{{metadata["title"]}}},')

        lines.append(f'  journal   = {{{self.server.capitalize()} (preprint)}},')

        if year != "XXXX":
            lines.append(f'  year      = {{{year}}},')

        if metadata.get("doi"):
            lines.append(f'  doi       = {{{metadata["doi"]}}},')

        if metadata.get("url"):
            lines.append(f'  url       = {{{metadata["url"]}}},')

        if metadata.get("category"):
            lines.append(f'  keywords  = {{{metadata["category"]}}},')

        # Note about preprint status
        note_parts = ["Preprint"]
        if metadata.get("version") and metadata["version"] != "1":
            note_parts.append(f"v{metadata['version']}")
        if metadata.get("published") and metadata["published"] != "NA":
            note_parts.append(f"Published in: {metadata['published']}")
        lines.append(f'  note      = {{{", ".join(note_parts)}}},')

        # Remove trailing comma from last field
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]

        lines.append("}")

        return "\n".join(lines)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Search bioRxiv/medRxiv preprint servers",
        epilog="Example: python search.py 'CRISPR gene therapy' --server biorxiv --limit 50"
    )

    parser.add_argument(
        "query",
        help="Search query (keywords to match in title/abstract)"
    )

    parser.add_argument(
        "--server",
        choices=["biorxiv", "medrxiv"],
        default="biorxiv",
        help="Preprint server to search (default: biorxiv)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of results (default: 50)"
    )

    parser.add_argument(
        "--date-start",
        help="Start date (YYYY-MM-DD), defaults to 30 days ago"
    )

    parser.add_argument(
        "--date-end",
        help="End date (YYYY-MM-DD), defaults to today"
    )

    parser.add_argument(
        "--category",
        help="Filter by subject category"
    )

    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List available subject categories and exit"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)"
    )

    parser.add_argument(
        "--format",
        choices=["json", "bibtex"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Initialize searcher
    searcher = BioRxivSearcher(server=args.server)

    # List categories if requested
    if args.list_categories:
        categories = searcher.get_categories()
        print(f"\n{args.server.capitalize()} Subject Categories:\n")
        for cat in categories:
            print(f"  - {cat}")
        print()
        sys.exit(0)

    # Search
    results = searcher.search(
        args.query,
        max_results=args.limit,
        date_start=args.date_start,
        date_end=args.date_end,
        category=args.category
    )

    if not results:
        print("No results found", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.format == "json":
        output = json.dumps({
            "query": args.query,
            "server": args.server,
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

    print(f"\nRetrieved {len(results)} preprints from {args.server}", file=sys.stderr)


if __name__ == "__main__":
    main()
