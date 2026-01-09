#!/usr/bin/env python3
"""Automated link validation for generated websites.

This script validates all external and internal links in generated HTML files,
providing a deterministic quality check for website outputs.

Usage:
    python validate_links.py <website_dir> [--timeout 10] [--concurrency 20]

Example:
    python validate_links.py ./output/paper_website --timeout 5
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin, urlparse

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


@dataclass
class LinkCheckResult:
    """Result of checking a single link.

    Attributes:
        url: The URL that was checked
        source_file: HTML file containing the link
        link_type: External (http/https) or internal (relative)
        status: HTTP status code if available
        valid: Whether the link is valid
        error: Error message if any
        redirect_url: Final URL if redirected
    """

    url: str
    source_file: str
    link_type: Literal["external", "internal", "anchor", "mailto", "tel"]
    status: int | None = None
    valid: bool = False
    error: str | None = None
    redirect_url: str | None = None


@dataclass
class LinkValidationReport:
    """Comprehensive report of link validation.

    Attributes:
        website_dir: Directory that was validated
        total_links: Total number of links checked
        valid_count: Number of valid links
        invalid_count: Number of invalid links
        skipped_count: Number of skipped links (mailto, tel, etc.)
        results: All individual link check results
        errors: List of error descriptions
        warnings: List of warning descriptions
    """

    website_dir: str
    total_links: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    skipped_count: int = 0
    results: list[LinkCheckResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Check if validation passed (no invalid links)."""
        return self.invalid_count == 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        checkable = self.total_links - self.skipped_count
        if checkable == 0:
            return 100.0
        return (self.valid_count / checkable) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "website_dir": self.website_dir,
            "total_links": self.total_links,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "skipped_count": self.skipped_count,
            "passed": self.passed,
            "success_rate": round(self.success_rate, 2),
            "errors": self.errors,
            "warnings": self.warnings,
            "invalid_links": [
                {"url": r.url, "source": r.source_file, "error": r.error}
                for r in self.results if not r.valid and r.link_type == "external"
            ],
        }


def classify_link(href: str) -> Literal["external", "internal", "anchor", "mailto", "tel"]:
    """Classify a link by type.

    Args:
        href: The href attribute value

    Returns:
        Link classification
    """
    if not href:
        return "internal"
    if href.startswith(("#",)):
        return "anchor"
    if href.startswith(("mailto:",)):
        return "mailto"
    if href.startswith(("tel:",)):
        return "tel"
    if href.startswith(("http://", "https://")):
        return "external"
    return "internal"


def extract_links_from_html(html_path: Path) -> list[tuple[str, str]]:
    """Extract all links from an HTML file.

    Args:
        html_path: Path to the HTML file

    Returns:
        List of (href, link_text) tuples
    """
    if not BS4_AVAILABLE:
        # Fallback to regex if BeautifulSoup not available
        content = html_path.read_text(encoding="utf-8", errors="ignore")
        href_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
        return [(match.group(1), "") for match in href_pattern.finditer(content)]

    content = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(content, "html.parser")

    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        text = a_tag.get_text(strip=True)
        links.append((href, text))

    # Also check for links in other elements
    for link_tag in soup.find_all("link", href=True):
        links.append((link_tag["href"], "stylesheet"))

    return links


async def check_external_link(
    session: aiohttp.ClientSession,
    url: str,
    source_file: str,
    timeout: int = 10,
) -> LinkCheckResult:
    """Check if an external URL is accessible.

    Args:
        session: aiohttp client session
        url: URL to check
        source_file: Source HTML file path
        timeout: Request timeout in seconds

    Returns:
        LinkCheckResult with validation status
    """
    result = LinkCheckResult(
        url=url,
        source_file=source_file,
        link_type="external",
    )

    try:
        async with session.head(
            url,
            timeout=aiohttp.ClientTimeout(total=timeout),
            allow_redirects=True,
        ) as response:
            result.status = response.status
            result.valid = response.status < 400

            # Track redirect
            if str(response.url) != url:
                result.redirect_url = str(response.url)

            if not result.valid:
                result.error = f"HTTP {response.status}"

    except asyncio.TimeoutError:
        result.error = f"Timeout after {timeout}s"
    except aiohttp.ClientConnectorError as e:
        result.error = f"Connection error: {e}"
    except aiohttp.InvalidURL:
        result.error = "Invalid URL format"
    except Exception as e:
        result.error = f"Error: {type(e).__name__}: {e}"

    return result


def check_internal_link(
    href: str,
    source_file: Path,
    website_dir: Path,
) -> LinkCheckResult:
    """Check if an internal link target exists.

    Args:
        href: Relative href value
        source_file: Source HTML file path
        website_dir: Root directory of the website

    Returns:
        LinkCheckResult with validation status
    """
    result = LinkCheckResult(
        url=href,
        source_file=str(source_file.relative_to(website_dir)),
        link_type="internal",
    )

    # Remove anchor portion
    href_path = href.split("#")[0] if "#" in href else href

    if not href_path:
        # Just an anchor on current page
        result.valid = True
        return result

    # Resolve relative to source file's directory
    if href_path.startswith("/"):
        target = website_dir / href_path.lstrip("/")
    else:
        target = source_file.parent / href_path

    target = target.resolve()

    # Check if file exists
    if target.exists():
        result.valid = True
    elif target.with_suffix(".html").exists():
        result.valid = True
        result.redirect_url = str(target.with_suffix(".html"))
    elif (target / "index.html").exists():
        result.valid = True
        result.redirect_url = str(target / "index.html")
    else:
        result.error = "File not found"

    return result


async def validate_website_links(
    website_dir: Path,
    timeout: int = 10,
    concurrency: int = 20,
    check_external: bool = True,
) -> LinkValidationReport:
    """Validate all links in a website directory.

    Args:
        website_dir: Path to the website root directory
        timeout: Timeout for external link checks in seconds
        concurrency: Maximum concurrent external requests
        check_external: Whether to check external links

    Returns:
        LinkValidationReport with all results
    """
    if not AIOHTTP_AVAILABLE and check_external:
        raise ImportError("aiohttp is required for external link checking. Install with: pip install aiohttp")

    report = LinkValidationReport(website_dir=str(website_dir))

    # Find all HTML files
    html_files = list(website_dir.glob("**/*.html"))

    if not html_files:
        report.warnings.append("No HTML files found in directory")
        return report

    # Collect all links
    all_links: list[tuple[str, str, Path]] = []  # (href, link_type, source_file)

    for html_file in html_files:
        links = extract_links_from_html(html_file)
        for href, _ in links:
            link_type = classify_link(href)
            all_links.append((href, link_type, html_file))

    report.total_links = len(all_links)

    # Separate by type
    external_links = [(href, src) for href, lt, src in all_links if lt == "external"]
    internal_links = [(href, src) for href, lt, src in all_links if lt == "internal"]
    anchor_links = [(href, src) for href, lt, src in all_links if lt == "anchor"]
    skipped_links = [(href, src) for href, lt, src in all_links if lt in ("mailto", "tel")]

    report.skipped_count = len(skipped_links)

    # Check internal links (synchronous)
    for href, source_file in internal_links:
        result = check_internal_link(href, source_file, website_dir)
        report.results.append(result)
        if result.valid:
            report.valid_count += 1
        else:
            report.invalid_count += 1
            report.errors.append(f"Broken internal link: {href} in {source_file.name}")

    # Check anchor links (just mark as valid for now - could check if ID exists)
    for href, source_file in anchor_links:
        result = LinkCheckResult(
            url=href,
            source_file=str(source_file.relative_to(website_dir)),
            link_type="anchor",
            valid=True,
        )
        report.results.append(result)
        report.valid_count += 1

    # Check external links (async)
    if check_external and external_links and AIOHTTP_AVAILABLE:
        # Deduplicate URLs but track all source files
        url_sources: dict[str, list[str]] = {}
        for href, source_file in external_links:
            if href not in url_sources:
                url_sources[href] = []
            url_sources[href].append(str(source_file.relative_to(website_dir)))

        connector = aiohttp.TCPConnector(limit=concurrency)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [
                check_external_link(session, url, sources[0], timeout)
                for url, sources in url_sources.items()
            ]
            results = await asyncio.gather(*tasks)

            for result in results:
                report.results.append(result)
                # Count for each occurrence
                occurrences = len(url_sources[result.url])
                if result.valid:
                    report.valid_count += occurrences
                else:
                    report.invalid_count += occurrences
                    report.errors.append(f"Broken external link: {result.url} ({result.error})")

    return report


def print_report(report: LinkValidationReport) -> None:
    """Print a formatted validation report.

    Args:
        report: The validation report to print
    """
    print("\n" + "=" * 60)
    print("LINK VALIDATION REPORT")
    print("=" * 60)
    print(f"Directory: {report.website_dir}")
    print(f"Total links: {report.total_links}")
    print(f"  Valid: {report.valid_count}")
    print(f"  Invalid: {report.invalid_count}")
    print(f"  Skipped: {report.skipped_count}")
    print(f"Success rate: {report.success_rate:.1f}%")

    if report.warnings:
        print(f"\nWarnings ({len(report.warnings)}):")
        for warning in report.warnings:
            print(f"  - {warning}")

    if report.errors:
        print(f"\nErrors ({len(report.errors)}):")
        for error in report.errors[:20]:  # Limit output
            print(f"  - {error}")
        if len(report.errors) > 20:
            print(f"  ... and {len(report.errors) - 20} more")

    print("\n" + "-" * 60)
    status = "PASSED" if report.passed else "FAILED"
    print(f"STATUS: {status}")
    print("=" * 60)


def main() -> int:
    """Main entry point for CLI usage.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Validate links in generated website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "website_dir",
        type=Path,
        help="Path to website directory",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout for external link checks (default: 10s)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=20,
        help="Max concurrent requests (default: 20)",
    )
    parser.add_argument(
        "--no-external",
        action="store_true",
        help="Skip external link checking",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    if not args.website_dir.exists():
        print(f"Error: Directory not found: {args.website_dir}", file=sys.stderr)
        return 1

    if not args.website_dir.is_dir():
        print(f"Error: Not a directory: {args.website_dir}", file=sys.stderr)
        return 1

    report = asyncio.run(
        validate_website_links(
            args.website_dir,
            timeout=args.timeout,
            concurrency=args.concurrency,
            check_external=not args.no_external,
        )
    )

    if args.json:
        import json
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_report(report)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
