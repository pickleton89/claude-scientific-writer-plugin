#!/usr/bin/env python3
"""
Check if arXiv/bioRxiv/medRxiv preprints have been published in peer-reviewed venues.

This script scans a BibTeX file for preprint entries and checks external APIs
to determine if they have since been published. It can optionally update
the BibTeX file with the published version metadata.

Usage:
    python check_preprint_status.py references.bib
    python check_preprint_status.py references.bib --update --output updated.bib
"""

import sys
import os
import argparse
import re
import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)


class PreprintSource(Enum):
    """Supported preprint sources."""
    ARXIV = "arxiv"
    BIORXIV = "biorxiv"
    MEDRXIV = "medrxiv"
    UNKNOWN = "unknown"


@dataclass
class PreprintInfo:
    """Information about a preprint entry."""
    citation_key: str
    source: PreprintSource
    identifier: str  # arXiv ID or DOI
    title: str = ""
    is_published: bool = False
    published_doi: Optional[str] = None
    published_venue: Optional[str] = None
    error: Optional[str] = None


@dataclass
class CheckReport:
    """Report from preprint status checking."""
    filepath: str
    check_date: str
    total_entries: int
    total_preprints: int
    now_published: List[PreprintInfo] = field(default_factory=list)
    still_preprint: List[PreprintInfo] = field(default_factory=list)
    errors: List[PreprintInfo] = field(default_factory=list)
    updated_entries: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "filepath": self.filepath,
            "check_date": self.check_date,
            "total_entries": self.total_entries,
            "total_preprints": self.total_preprints,
            "now_published_count": len(self.now_published),
            "still_preprint_count": len(self.still_preprint),
            "error_count": len(self.errors),
            "now_published": [asdict(p) for p in self.now_published],
            "still_preprint": [asdict(p) for p in self.still_preprint],
            "errors": [asdict(p) for p in self.errors],
            "updated_entries": self.updated_entries,
        }


class PreprintChecker:
    """Check and update preprint citations."""

    # Rate limiting settings
    REQUEST_DELAY = 0.5  # seconds between API requests

    def __init__(self, verbose: bool = False):
        """
        Initialize the preprint checker.

        Args:
            verbose: Whether to print verbose output
        """
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PreprintChecker/1.0 (Citation Management Tool; mailto:research@example.com)'
        })

    def _log(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message, file=sys.stderr)

    def identify_preprint_source(self, entry: Dict) -> Tuple[PreprintSource, str]:
        """
        Identify the preprint source and identifier from a BibTeX entry.

        Args:
            entry: Parsed BibTeX entry dictionary

        Returns:
            Tuple of (source, identifier)
        """
        fields = entry.get('fields', {})

        # Check for arXiv
        eprint = fields.get('eprint', '').strip()
        if eprint:
            # Validate arXiv ID format
            if re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', eprint):
                return PreprintSource.ARXIV, eprint

        # Check archiveprefix
        archive = fields.get('archiveprefix', '').lower()
        if archive == 'arxiv' and eprint:
            return PreprintSource.ARXIV, eprint

        # Check howpublished field
        howpublished = fields.get('howpublished', '').lower()
        if howpublished == 'arxiv':
            # Try to extract arXiv ID from URL or note
            url = fields.get('url', '')
            note = fields.get('note', '')
            for text in [url, note]:
                match = re.search(r'(\d{4}\.\d{4,5})(v\d+)?', text)
                if match:
                    return PreprintSource.ARXIV, match.group(0)

        # Check for bioRxiv/medRxiv
        doi = fields.get('doi', '').strip()
        if howpublished in ['biorxiv', 'medrxiv'] or 'biorxiv' in doi.lower() or 'medrxiv' in doi.lower():
            if doi.startswith('10.1101/'):
                # Determine source: check howpublished first, then DOI content
                if howpublished == 'medrxiv' or 'medrxiv' in doi.lower():
                    source = PreprintSource.MEDRXIV
                else:
                    source = PreprintSource.BIORXIV
                return source, doi

        # Check URL for preprint servers
        url = fields.get('url', '').lower()
        if 'arxiv.org' in url:
            match = re.search(r'(\d{4}\.\d{4,5})(v\d+)?', url)
            if match:
                return PreprintSource.ARXIV, match.group(0)
        elif 'biorxiv.org' in url:
            if doi.startswith('10.1101/'):
                return PreprintSource.BIORXIV, doi
        elif 'medrxiv.org' in url:
            if doi.startswith('10.1101/'):
                return PreprintSource.MEDRXIV, doi

        return PreprintSource.UNKNOWN, ""

    def check_arxiv_published(self, arxiv_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if arXiv preprint has been published.

        Uses the arXiv API to check for DOI field indicating publication.

        Args:
            arxiv_id: arXiv identifier (e.g., '2103.14030')

        Returns:
            Tuple of (is_published, published_doi, venue)
        """
        # Clean the arXiv ID
        arxiv_id = arxiv_id.replace('arXiv:', '').strip()

        try:
            # Query arXiv API
            url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            content = response.text

            # Parse the Atom feed for DOI
            doi_match = re.search(r'<arxiv:doi>([^<]+)</arxiv:doi>', content)
            if doi_match:
                published_doi = doi_match.group(1).strip()
                # Get venue from CrossRef
                venue = self._get_venue_from_doi(published_doi)
                return True, published_doi, venue

            # Also check for journal_ref
            journal_match = re.search(r'<arxiv:journal_ref>([^<]+)</arxiv:journal_ref>', content)
            if journal_match:
                # Has journal reference but maybe no DOI
                # Try to find DOI via CrossRef search
                journal_ref = journal_match.group(1).strip()
                return True, None, journal_ref

            return False, None, None

        except requests.RequestException as e:
            self._log(f"  Error checking arXiv {arxiv_id}: {e}")
            raise

    def check_biorxiv_published(self, doi: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if bioRxiv/medRxiv preprint has been published.

        Uses CrossRef API to find the 'is-preprint-of' relation.

        Args:
            doi: bioRxiv/medRxiv DOI (starts with 10.1101/)

        Returns:
            Tuple of (is_published, published_doi, venue)
        """
        if not doi.startswith('10.1101/'):
            return False, None, None

        try:
            # Query CrossRef for relations
            url = f'https://api.crossref.org/works/{doi}'
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})

                # Check for 'is-preprint-of' relation
                relations = message.get('relation', {})
                is_preprint_of = relations.get('is-preprint-of', [])

                if is_preprint_of:
                    published_doi = is_preprint_of[0].get('id')
                    if published_doi:
                        venue = self._get_venue_from_doi(published_doi)
                        return True, published_doi, venue

            return False, None, None

        except requests.RequestException as e:
            self._log(f"  Error checking bioRxiv {doi}: {e}")
            raise

    def _get_venue_from_doi(self, doi: str) -> Optional[str]:
        """
        Get the journal/venue name from a DOI via CrossRef.

        Args:
            doi: DOI to look up

        Returns:
            Venue name or None
        """
        try:
            url = f'https://api.crossref.org/works/{doi}'
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})

                # Try container-title first (journal name)
                container = message.get('container-title', [])
                if container:
                    return container[0]

                # Fall back to publisher
                return message.get('publisher')

        except requests.RequestException:
            pass

        return None

    def parse_bibtex_file(self, filepath: str) -> List[Dict]:
        """
        Parse BibTeX file and extract entries.

        Args:
            filepath: Path to BibTeX file

        Returns:
            List of entry dictionaries
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f'Error reading file: {e}', file=sys.stderr)
            return []

        entries = []

        # Match BibTeX entries
        pattern = r'@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}'
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)

        for match in matches:
            entry_type = match.group(1).lower()
            citation_key = match.group(2).strip()
            fields_text = match.group(3)

            # Parse fields
            fields = {}
            field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}|(\w+)\s*=\s*"([^"]*)"'
            field_matches = re.finditer(field_pattern, fields_text)

            for field_match in field_matches:
                if field_match.group(1):
                    field_name = field_match.group(1).lower()
                    field_value = field_match.group(2)
                else:
                    field_name = field_match.group(3).lower()
                    field_value = field_match.group(4)

                fields[field_name] = field_value.strip()

            entries.append({
                'type': entry_type,
                'key': citation_key,
                'fields': fields,
                'raw': match.group(0)
            })

        return entries

    def check_file(self, filepath: str) -> CheckReport:
        """
        Check all preprints in a BibTeX file.

        Args:
            filepath: Path to BibTeX file

        Returns:
            CheckReport with results
        """
        self._log(f"Parsing {filepath}...")
        entries = self.parse_bibtex_file(filepath)
        self._log(f"Found {len(entries)} entries")

        report = CheckReport(
            filepath=filepath,
            check_date=datetime.now(timezone.utc).isoformat(),
            total_entries=len(entries),
            total_preprints=0,
        )

        for entry in entries:
            source, identifier = self.identify_preprint_source(entry)

            if source == PreprintSource.UNKNOWN:
                continue

            report.total_preprints += 1
            title = entry['fields'].get('title', '')

            preprint_info = PreprintInfo(
                citation_key=entry['key'],
                source=source,
                identifier=identifier,
                title=title,
            )

            self._log(f"Checking {entry['key']} ({source.value}: {identifier})...")

            try:
                if source == PreprintSource.ARXIV:
                    is_published, pub_doi, venue = self.check_arxiv_published(identifier)
                elif source in (PreprintSource.BIORXIV, PreprintSource.MEDRXIV):
                    is_published, pub_doi, venue = self.check_biorxiv_published(identifier)
                else:
                    is_published, pub_doi, venue = False, None, None

                preprint_info.is_published = is_published
                preprint_info.published_doi = pub_doi
                preprint_info.published_venue = venue

                if is_published:
                    self._log(f"  -> Published: {pub_doi or venue}")
                    report.now_published.append(preprint_info)
                else:
                    self._log("  -> Still preprint")
                    report.still_preprint.append(preprint_info)

                # Rate limiting
                time.sleep(self.REQUEST_DELAY)

            except Exception as e:
                preprint_info.error = str(e)
                report.errors.append(preprint_info)
                self._log(f"  -> Error: {e}")

        return report


def print_report(report: CheckReport) -> None:
    """Print a formatted report to stdout."""
    print("\n" + "=" * 60)
    print("PREPRINT STATUS REPORT")
    print("=" * 60)
    print(f"\nFile: {report.filepath}")
    print(f"Checked: {report.check_date}")
    print(f"\nTotal entries: {report.total_entries}")
    print(f"Preprints found: {report.total_preprints}")
    print(f"Now published: {len(report.now_published)}")
    print(f"Still preprint: {len(report.still_preprint)}")
    print(f"Errors: {len(report.errors)}")

    if report.now_published:
        print("\n" + "-" * 60)
        print("PREPRINTS NOW PUBLISHED:")
        print("-" * 60)
        for p in report.now_published:
            print(f"\n  {p.citation_key}")
            print(f"    Source: {p.source.value}")
            print(f"    Preprint ID: {p.identifier}")
            if p.published_doi:
                print(f"    Published DOI: {p.published_doi}")
            if p.published_venue:
                print(f"    Venue: {p.published_venue}")

    if report.still_preprint:
        print("\n" + "-" * 60)
        print("STILL PREPRINTS:")
        print("-" * 60)
        for p in report.still_preprint:
            print(f"\n  {p.citation_key}")
            print(f"    Source: {p.source.value}")
            print(f"    ID: {p.identifier}")

    if report.errors:
        print("\n" + "-" * 60)
        print("ERRORS:")
        print("-" * 60)
        for p in report.errors:
            print(f"\n  {p.citation_key}")
            print(f"    Error: {p.error}")

    print("\n" + "=" * 60)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Check if preprints have been published',
        epilog='Example: python check_preprint_status.py references.bib --verbose'
    )

    parser.add_argument(
        'file',
        help='BibTeX file to check'
    )

    parser.add_argument(
        '--update',
        action='store_true',
        help='Update entries to published versions (not implemented yet)'
    )

    parser.add_argument(
        '--output',
        help='Output file for updated BibTeX (requires --update)'
    )

    parser.add_argument(
        '--report',
        help='Output file for JSON report'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.output and not args.update:
        parser.error("--output requires --update")

    # Check file
    checker = PreprintChecker(verbose=args.verbose)
    report = checker.check_file(args.file)

    # Print report
    print_report(report)

    # Save JSON report
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, default=str)
        print(f"\nJSON report saved to: {args.report}")

    # Update entries (placeholder for future implementation)
    if args.update:
        print("\nNote: --update functionality not yet implemented.")
        print("Please manually update entries with published DOIs.")

    # Return exit code based on results
    if report.errors:
        sys.exit(2)  # Errors occurred
    elif report.now_published:
        sys.exit(1)  # Updates available
    else:
        sys.exit(0)  # All clean


if __name__ == '__main__':
    main()
