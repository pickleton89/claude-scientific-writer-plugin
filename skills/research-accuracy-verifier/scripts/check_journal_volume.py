#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Stage-2 journal-volume-year impossibility checker.

Detects citation hallucinations of the form "Journal X, volume V, year Y" where
the (V, Y) combination is impossible given the journal's start year and
approximate volumes-per-year. Example: "Nature Cancer 5:1123 (2019)" is
impossible because Nature Cancer started in 2020.

Reads an offline known-journals cache (`references/known_journals.json`).
v1.3 will add a live Crossref ISSN start-year lookup fallback for unknown journals.

Usage:
    uv run python check_journal_volume.py --journal "Nature Cancer" --volume 5 --year 2019
    uv run python check_journal_volume.py --journal Cell --volume 180 --year 2020 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class JournalCheckResult:
    journal: str
    claimed_volume: int
    claimed_year: int
    journal_known: bool
    plausible: bool | None  # None when journal unknown
    expected_volume_for_year: int | None
    start_year: int | None
    detail: str


class JournalVolumeChecker:
    """Offline plausibility check for (journal, volume, year) tuples."""

    def __init__(self, cache_path: str | None = None) -> None:
        if cache_path:
            self.cache_path = Path(cache_path)
        else:
            self.cache_path = (
                Path(__file__).parent.parent / "references" / "known_journals.json"
            )
        with open(self.cache_path) as f:
            self.journals: dict[str, dict[str, int | str]] = json.load(f)["journals"]

    def expected_volume_for_year(self, journal: str, year: int) -> int | None:
        """Compute expected volume number at a given year (None if journal unknown)."""
        meta = self.journals.get(journal)
        if meta is None:
            return None
        start_year = int(meta["start_year"])
        vol_per_year = int(meta["vol_per_year"])
        first_volume = int(meta["first_volume"])
        if year < start_year:
            return None  # journal didn't exist yet
        return first_volume + (year - start_year) * vol_per_year

    def check(self, journal: str, volume: int, year: int) -> JournalCheckResult:
        meta = self.journals.get(journal)
        if meta is None:
            return JournalCheckResult(
                journal=journal,
                claimed_volume=volume,
                claimed_year=year,
                journal_known=False,
                plausible=None,
                expected_volume_for_year=None,
                start_year=None,
                detail=(
                    f"Journal '{journal}' not in offline cache. Delegate to "
                    f"capability `verification.citation_existence` for live Crossref ISSN lookup."
                ),
            )

        start_year = int(meta["start_year"])
        if year < start_year:
            return JournalCheckResult(
                journal=journal,
                claimed_volume=volume,
                claimed_year=year,
                journal_known=True,
                plausible=False,
                expected_volume_for_year=None,
                start_year=start_year,
                detail=(
                    f"Year {year} predates journal start year {start_year}. "
                    f"Citation is impossible."
                ),
            )

        expected = self.expected_volume_for_year(journal, year)
        # Allow ±1 volume slop because some journals shift volume boundaries (Jan vs. Dec issue).
        plausible = expected is not None and abs(volume - expected) <= 1
        if plausible:
            detail = f"Volume {volume} is consistent with year {year} (expected ~{expected})."
        else:
            detail = (
                f"Volume {volume} inconsistent with year {year}: "
                f"expected ~{expected} (journal began {start_year}, "
                f"{meta['vol_per_year']} vol/yr from vol {meta['first_volume']})."
            )
        return JournalCheckResult(
            journal=journal,
            claimed_volume=volume,
            claimed_year=year,
            journal_known=True,
            plausible=plausible,
            expected_volume_for_year=expected,
            start_year=start_year,
            detail=detail,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check whether a (journal, volume, year) tuple is plausible"
    )
    parser.add_argument("--journal", required=True)
    parser.add_argument("--volume", required=True, type=int)
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--cache", help="Custom known-journals JSON cache path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checker = JournalVolumeChecker(args.cache)
    result = checker.check(args.journal, args.volume, args.year)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(f"Journal:        {result.journal}")
        print(f"Claimed:        volume {result.claimed_volume} in year {result.claimed_year}")
        print(f"Journal known:  {result.journal_known}")
        print(f"Plausible:      {result.plausible}")
        if result.expected_volume_for_year is not None:
            print(f"Expected vol:   ~{result.expected_volume_for_year}")
        print(f"Detail:         {result.detail}")
    # Exit codes: 0 plausible, 1 implausible, 2 journal unknown (cannot determine)
    if result.plausible is True:
        sys.exit(0)
    if result.plausible is False:
        sys.exit(1)
    sys.exit(2)


if __name__ == "__main__":
    main()
