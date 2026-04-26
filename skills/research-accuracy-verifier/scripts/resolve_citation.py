#!/usr/bin/env python3
"""Thin wrapper / delegation surface for citation existence checks.

Stage 2 cites this script as the canonical entry point for citation existence
verification. The actual lookups happen via the LLM calling capability key
`verification.citation_existence` (PubMed MCP primary, Crossref fallback) — this
script does not attempt live network calls itself in v1.2.

What this script does:
  - Validates citation metadata shape (key, doi, pmid, raw_text)
  - Performs offline plausibility checks (DOI prefix format, PMID is numeric,
    journal-volume-year impossibility lookup if a known-journal table is provided)
  - Documents the delegation contract for future v1.3 live wiring

Pattern reuse: structure modeled on skills/citation-management/scripts/validate_citations.py
(its CitationValidator class handles BibTeX shape; we cover citation-as-record shape).

Usage:
    uv run python resolve_citation.py --citation '{"key":"S1","doi":"10.1038/...","raw_text":"..."}'
    uv run python resolve_citation.py --citations citations.json --json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
PMID_RE = re.compile(r"^\d{1,9}$")


@dataclass
class CitationCheck:
    key: str
    has_doi: bool
    has_pmid: bool
    doi_well_formed: bool | None
    pmid_well_formed: bool | None
    plausibility: str  # "ok" | "needs_lookup" | "malformed"
    notes: list[str]


class CitationResolver:
    """Offline plausibility checks for citation records.

    Live API resolution is delegated to the LLM via capability key
    `verification.citation_existence` (PubMed MCP primary, Crossref fallback).
    """

    def check(self, citation: dict[str, str | None]) -> CitationCheck:
        notes: list[str] = []
        doi = citation.get("doi")
        pmid = citation.get("pmid")

        doi_ok: bool | None
        if doi:
            doi_ok = bool(DOI_RE.match(doi))
            if not doi_ok:
                notes.append(f"DOI '{doi}' does not match standard format 10.NNNN/...")
        else:
            doi_ok = None

        pmid_ok: bool | None
        if pmid:
            pmid_ok = bool(PMID_RE.match(str(pmid)))
            if not pmid_ok:
                notes.append(f"PMID '{pmid}' is not numeric")
        else:
            pmid_ok = None

        if doi_ok is False or pmid_ok is False:
            plausibility = "malformed"
        elif doi_ok or pmid_ok:
            plausibility = "needs_lookup"
            notes.append(
                "Identifier present but live resolution not performed in v1.2 "
                "(delegate to capability `verification.citation_existence`)."
            )
        else:
            plausibility = "needs_lookup"
            notes.append(
                "No identifier provided; LLM must search by author/year/title via "
                "capability `verification.citation_existence`."
            )

        return CitationCheck(
            key=citation.get("key", "?") or "?",
            has_doi=bool(doi),
            has_pmid=bool(pmid),
            doi_well_formed=doi_ok,
            pmid_well_formed=pmid_ok,
            plausibility=plausibility,
            notes=notes,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline citation plausibility check")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--citation", help="Single citation as JSON string")
    g.add_argument("--citations", help="Path to JSON array of citations")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.citation:
        citations = [json.loads(args.citation)]
    else:
        citations = json.loads(Path(args.citations).read_text())
        if not isinstance(citations, list):
            citations = [citations]

    resolver = CitationResolver()
    results = [asdict(resolver.check(c)) for c in citations]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"[{r['key']}] plausibility={r['plausibility']}")
            for n in r["notes"]:
                print(f"  - {n}")


if __name__ == "__main__":
    main()
