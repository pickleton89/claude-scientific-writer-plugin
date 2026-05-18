"""Tests for scripts/validate_artifact.py — per-kind happy + perturbation paths."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from validate_artifact import ArtifactValidator

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "audit_minimal"


def _load(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text())


# ---------------------------------------------------------------------------
# document_inventory
# ---------------------------------------------------------------------------


class TestDocumentInventoryHappyPath:
    def test_valid_fixture(self) -> None:
        v = ArtifactValidator("document_inventory")
        ok, errs, warns = v.validate(_load("document_inventory.json"))
        assert ok, f"errors: {errs}"
        assert errs == []


class TestDocumentInventoryD1:
    """D1: paragraph ordinals contiguous within section starting at 1."""

    def test_non_contiguous_ordinal_fails(self) -> None:
        d = _load("document_inventory.json")
        # Change one paragraph's ordinal to create a gap
        if d["paragraphs"]:
            d["paragraphs"][0]["ordinal"] = 5  # gap from 1
        v = ArtifactValidator("document_inventory")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("D1:" in e for e in errs)


class TestDocumentInventoryD3:
    """D3: override.path resolves to an existing element."""

    def test_out_of_range_index_fails(self) -> None:
        d = _load("document_inventory.json")
        d["overrides"].append(
            {
                "kind": "section_name",
                "path": "sections[99].name",
                "after": "X",
                "reason": "test",
            }
        )
        v = ArtifactValidator("document_inventory")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("D3:" in e for e in errs)

    def test_unparseable_path_fails(self) -> None:
        d = _load("document_inventory.json")
        d["overrides"].append(
            {"kind": "section_name", "path": "garbage", "after": "X", "reason": "test"}
        )
        v = ArtifactValidator("document_inventory")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("D3:" in e and "does not parse" in e for e in errs)

    def test_valid_override_passes(self) -> None:
        d = _load("document_inventory.json")
        d["overrides"].append(
            {
                "kind": "section_name",
                "path": "sections[0].name",
                "before": d["sections"][0]["name"],
                "after": "Renamed Section",
                "reason": "test rename",
            }
        )
        v = ArtifactValidator("document_inventory")
        ok, errs, _ = v.validate(d)
        assert ok, f"errors: {errs}"


class TestDocumentInventoryD4:
    """D4: cross-reference between section.paragraph_ids and paragraph.section_id."""

    def test_orphan_paragraph_id_fails(self) -> None:
        d = _load("document_inventory.json")
        d["sections"][0]["paragraph_ids"].append("P999")
        v = ArtifactValidator("document_inventory")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("D4:" in e for e in errs)

    def test_orphan_section_id_fails(self) -> None:
        d = _load("document_inventory.json")
        d["paragraphs"][0]["section_id"] = "S999"
        v = ArtifactValidator("document_inventory")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("D4:" in e for e in errs)


# ---------------------------------------------------------------------------
# reference_map
# ---------------------------------------------------------------------------


class TestReferenceMapHappyPath:
    def test_valid_fixture(self) -> None:
        v = ArtifactValidator("reference_map")
        ok, errs, _ = v.validate(_load("reference_map.json"))
        assert ok, f"errors: {errs}"


class TestReferenceMapM1:
    def test_duplicate_keys_fail(self) -> None:
        d = _load("reference_map.json")
        if d["citations"]:
            d["citations"].append(copy.deepcopy(d["citations"][0]))
        v = ArtifactValidator("reference_map")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("M1:" in e for e in errs)


class TestReferenceMapM2:
    def test_malformed_doi_fails(self) -> None:
        d = _load("reference_map.json")
        d["citations"][0]["doi"] = "not-a-doi"
        v = ArtifactValidator("reference_map")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("M2:" in e and "DOI pattern" in e for e in errs)

    def test_malformed_pmid_fails(self) -> None:
        d = _load("reference_map.json")
        d["citations"][0]["pmid"] = "abc"
        v = ArtifactValidator("reference_map")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("M2:" in e and "pmid" in e for e in errs)

    def test_well_formed_pmcid(self) -> None:
        d = _load("reference_map.json")
        d["citations"][0]["pmcid"] = "PMC123456"
        v = ArtifactValidator("reference_map")
        ok, errs, _ = v.validate(d)
        assert ok, f"errors: {errs}"


class TestReferenceMapM3:
    def test_orphan_must_have_empty_occurrences(self) -> None:
        d = _load("reference_map.json")
        # Make orphan claim a non-orphan: put it in bibliography_orphans and add occurrences
        if not d["bibliography_orphans"]:
            d["bibliography_orphans"].append(d["citations"][0]["key"])
        # The first citation has occurrences, so listing it as orphan should fail
        v = ArtifactValidator("reference_map")
        ok, errs, _ = v.validate(d)
        # If the first citation in the fixture has occurrences, this will fail M3.
        if d["citations"][0]["occurrences"]:
            assert not ok
            assert any("M3:" in e for e in errs)


# ---------------------------------------------------------------------------
# resolved_sources
# ---------------------------------------------------------------------------


class TestResolvedSourcesHappyPath:
    def test_valid_fixture(self) -> None:
        v = ArtifactValidator("resolved_sources")
        ok, errs, _ = v.validate(_load("resolved_sources.json"))
        assert ok, f"errors: {errs}"


class TestResolvedSourcesS1:
    def test_duplicate_paper_id_fails(self) -> None:
        d = _load("resolved_sources.json")
        d["sources"].append(copy.deepcopy(d["sources"][0]))
        v = ArtifactValidator("resolved_sources")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("S1:" in e for e in errs)


class TestResolvedSourcesS2:
    def test_missing_all_ids_fails(self) -> None:
        d = _load("resolved_sources.json")
        for f in ("doi", "pmid", "pmcid"):
            d["sources"][0][f] = None
        v = ArtifactValidator("resolved_sources")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("S2:" in e for e in errs)


class TestResolvedSourcesS4:
    def test_future_frozen_at_fails(self) -> None:
        d = _load("resolved_sources.json")
        d["metadata"]["frozen_at"] = "2999-01-01T00:00:00+00:00"
        v = ArtifactValidator("resolved_sources")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("S4:" in e for e in errs)


class TestResolvedSourcesV1:
    def test_future_fetched_at_fails(self) -> None:
        d = _load("resolved_sources.json")
        d["sources"][0]["resolution_paths"][0]["fetched_at"] = "2999-01-01T00:00:00+00:00"
        v = ArtifactValidator("resolved_sources")
        ok, errs, _ = v.validate(d)
        assert not ok
        assert any("V1:" in e for e in errs)


class TestResolvedSourcesV2:
    def test_all_unverified_warns_advisory(self) -> None:
        d = _load("resolved_sources.json")
        d["sources"][0]["resolution_paths"] = [
            {
                "tool": "PubMed MCP",
                "outcome": "UNVERIFIED",
                "fetched_at": "2026-05-18T16:00:00+00:00",
            }
        ]
        v = ArtifactValidator("resolved_sources")
        ok, errs, warns = v.validate(d)
        # Advisory — should still pass but emit a warning.
        assert ok
        assert any("V2 advisory" in w for w in warns)


# ---------------------------------------------------------------------------
# Constructor edge cases
# ---------------------------------------------------------------------------


class TestConstructor:
    def test_unknown_kind_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown artifact kind"):
            ArtifactValidator("bogus")
