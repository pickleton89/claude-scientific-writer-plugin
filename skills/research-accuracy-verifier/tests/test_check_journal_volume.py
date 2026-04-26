"""Tests for check_journal_volume.py — Stage-2 journal-volume-year impossibility check."""

from __future__ import annotations


from check_journal_volume import JournalVolumeChecker


class TestJournalVolumeChecker:
    def setup_method(self) -> None:
        self.c = JournalVolumeChecker()

    def test_canonical_hallucination_nature_cancer_5_in_2019(self) -> None:
        """The worked-example case: Nature Cancer vol 5 in 2019 is impossible (journal began 2020)."""
        r = self.c.check("Nature Cancer", volume=5, year=2019)
        assert r.journal_known is True
        assert r.plausible is False
        assert r.start_year == 2020
        assert "predates" in r.detail.lower() or "impossible" in r.detail.lower()

    def test_plausible_nature_cancer_volume_for_year(self) -> None:
        # Nature Cancer started 2020 vol 1; vol 4 in 2023 is plausible
        r = self.c.check("Nature Cancer", volume=4, year=2023)
        assert r.plausible is True
        assert r.expected_volume_for_year == 4

    def test_volume_year_off_by_one_allowed(self) -> None:
        """Volume slop ±1 to handle Jan vs Dec issue boundaries."""
        r = self.c.check("Nature Cancer", volume=3, year=2023)
        assert r.plausible is True  # expected 4, got 3 — within ±1

    def test_volume_year_off_by_three_rejected(self) -> None:
        r = self.c.check("Nature Cancer", volume=10, year=2023)
        assert r.plausible is False
        assert "inconsistent" in r.detail.lower()

    def test_cell_volume_consistent_with_year(self) -> None:
        # Cell started 1974 vol 1 at ~4 vol/year → vol ~185 in 2020
        r = self.c.check("Cell", volume=185, year=2020)
        assert r.plausible is True

    def test_cell_volume_off_rejects(self) -> None:
        # Cell vol 50 in 2020 is impossibly low
        r = self.c.check("Cell", volume=50, year=2020)
        assert r.plausible is False

    def test_unknown_journal_returns_indeterminate(self) -> None:
        r = self.c.check("Journal of Imaginary Studies", volume=5, year=2020)
        assert r.journal_known is False
        assert r.plausible is None
        assert "verification.citation_existence" in r.detail

    def test_year_predates_start_year(self) -> None:
        # PLOS ONE started 2006; vol 1 in 2000 is impossible
        r = self.c.check("PLOS ONE", volume=1, year=2000)
        assert r.plausible is False
        assert r.start_year == 2006

    def test_first_volume_offset_handled(self) -> None:
        """Bioinformatics started in 1998 at volume 14 (renumbered from CABIOS); vol 14 in 1998 is correct."""
        r = self.c.check("Bioinformatics", volume=14, year=1998)
        assert r.plausible is True

    def test_expected_volume_helper(self) -> None:
        assert self.c.expected_volume_for_year("Nature Cancer", 2020) == 1
        assert self.c.expected_volume_for_year("Nature Cancer", 2025) == 6
        assert self.c.expected_volume_for_year("Cell", 1974) == 1
        assert self.c.expected_volume_for_year("Cell", 2020) == 185  # 1974 + 46*4
        assert self.c.expected_volume_for_year("Unknown Journal", 2020) is None
