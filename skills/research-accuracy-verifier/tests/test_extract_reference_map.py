"""Tests for scripts/extract_reference_map.py."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

import extract_reference_map as erm
import parse_document as pd

SCHEMA = json.loads(
    (Path(__file__).parent.parent / "schemas" / "reference_map.json").read_text()
)


def _build_inventory(text: str) -> dict:
    return pd.build_inventory(text, audit_slug="t")


def _validate(rm: dict) -> None:
    jsonschema.Draft7Validator(SCHEMA).validate(rm)


class TestNumericBrackets:
    def test_single(self) -> None:
        doc = "# A\n\nFoo [1] bar.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        keys = {c["key"] for c in rm["citations"]}
        assert "1" in keys

    def test_comma_list(self) -> None:
        doc = "# A\n\nFoo [1,2,3] bar.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        keys = {c["key"] for c in rm["citations"]}
        assert {"1", "2", "3"} <= keys

    def test_range_expansion(self) -> None:
        doc = "# A\n\nFoo [5-7] bar.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        keys = {c["key"] for c in rm["citations"]}
        assert {"5", "6", "7"} <= keys

    def test_pathological_range_capped(self) -> None:
        doc = "# A\n\nFoo [1-9999] bar.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        # Sanity cap rejects expansion → only literal '1-9999' would be kept; but
        # the function falls back to the original part, which contains '-' so
        # we keep it as-is. Confirm we didn't generate 10000 keys.
        assert len(rm["citations"]) < 50


class TestCiteCommands:
    def test_single_key(self) -> None:
        doc = "# A\n\nSee \\cite{Smith2019}.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        keys = {c["key"] for c in rm["citations"]}
        assert "Smith2019" in keys

    def test_multi_key(self) -> None:
        doc = "# A\n\nSee \\citep{Smith2019, Jones2020}.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        keys = {c["key"] for c in rm["citations"]}
        assert {"Smith2019", "Jones2020"} <= keys


class TestAuthorYear:
    def test_paren_form(self) -> None:
        doc = "# A\n\nA result (Smith, 2019) is here.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        keys = {c["key"] for c in rm["citations"]}
        assert any("Smith" in k and "2019" in k for k in keys)

    def test_et_al(self) -> None:
        doc = "# A\n\nA result (Smith et al., 2019) is here.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        keys = {c["key"] for c in rm["citations"]}
        assert any("Smith et al" in k for k in keys)

    def test_narrative_form(self) -> None:
        doc = "# A\n\nSmith et al. (2019) showed this.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        keys = {c["key"] for c in rm["citations"]}
        assert any("Smith" in k and "2019" in k for k in keys)


class TestOccurrences:
    def test_records_multiple_occurrences(self) -> None:
        doc = "# A\n\nFoo [1] bar.\n\n# B\n\nBaz [1] qux.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        cit = next(c for c in rm["citations"] if c["key"] == "1")
        assert len(cit["occurrences"]) == 2

    def test_occurrence_has_section_paragraph_line(self) -> None:
        doc = "# Intro\n\nFoo [1] bar.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        cit = next(c for c in rm["citations"] if c["key"] == "1")
        assert "section_id" in cit["occurrences"][0]
        assert "paragraph_id" in cit["occurrences"][0]
        assert isinstance(cit["occurrences"][0]["line"], int)


class TestBibliography:
    def test_bibtex_keys_extracted(self, sample_bibliography_bibtex: str) -> None:
        doc = "# A\n\nbody.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(
            doc, inv,
            audit_slug="t",
            sources_available="bibliography_only",
            bibliography_text=sample_bibliography_bibtex,
        )
        keys = {c["key"] for c in rm["citations"]}
        assert {"smith_2019", "anderson_2020"} <= keys

    def test_bibtex_orphans(self, sample_bibliography_bibtex: str) -> None:
        # No inline cites → all bib entries are orphans.
        doc = "# A\n\nbody.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(
            doc, inv,
            audit_slug="t",
            sources_available="bibliography_only",
            bibliography_text=sample_bibliography_bibtex,
        )
        assert set(rm["bibliography_orphans"]) == {"smith_2019", "anderson_2020"}

    def test_numbered_list_format(self) -> None:
        bib = "[1] First entry. Journal.\n[2] Second. Other journal.\n"
        doc = "# A\n\nSee [1] only.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(
            doc, inv,
            audit_slug="t",
            sources_available="bibliography_only",
            bibliography_text=bib,
        )
        keys = {c["key"] for c in rm["citations"]}
        assert {"1", "2"} <= keys
        # [2] has no inline mention → orphan
        assert "2" in rm["bibliography_orphans"]
        assert "1" not in rm["bibliography_orphans"]


class TestSchemaValidates:
    def test_minimal(self) -> None:
        doc = "# A\n\nFoo [1] bar.\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        _validate(rm)

    def test_empty_document(self) -> None:
        doc = ""
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="none")
        _validate(rm)
        assert rm["citations"] == []


class TestUpdatePaperIds:
    def test_backfills_paper_id_only_on_known_keys(self) -> None:
        doc = "# A\n\nSee [1] and [2].\n"
        inv = _build_inventory(doc)
        rm = erm.build_reference_map(doc, inv, audit_slug="t", sources_available="bibliography_only")
        mapping = {"1": {"paper_id": "10.1000/foo", "doi": "10.1000/foo"}}
        erm.update_paper_ids(rm, mapping)
        cit_by_key = {c["key"]: c for c in rm["citations"]}
        assert cit_by_key["1"]["paper_id"] == "10.1000/foo"
        assert cit_by_key["1"]["doi"] == "10.1000/foo"
        # Key '2' untouched
        assert cit_by_key["2"]["paper_id"] is None
