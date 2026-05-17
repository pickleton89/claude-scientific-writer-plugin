"""Tests for validate_sidecar.py and thresholds.SIDECAR_SPECS.

Covers all 4 sidecar kinds (sources / grading / synthesis / advocate),
positive validation against minimal fixtures, and negative cases for each
predicate (S*, G*, Y*, A*).
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

# Add scripts directory to path
SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from thresholds import (  # noqa: E402
    ALL_MODES,
    SIDECAR_KINDS,
    SIDECAR_SPECS,
    SIDECAR_ENFORCEMENT,
    required_sidecars,
    sidecar_filename,
)
from validate_sidecar import SidecarValidator, _load_paper_ids  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "sidecars"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


# ───────────────────────────────────────────────────────────────────────
# thresholds: SIDECAR_SPECS / sidecar_filename
# ───────────────────────────────────────────────────────────────────────


class TestSidecarSpecs:
    def test_every_mode_present(self):
        assert set(SIDECAR_SPECS) == set(ALL_MODES)

    def test_kinds_are_known(self):
        for mode, kinds in SIDECAR_SPECS.items():
            for k in kinds:
                assert k in SIDECAR_KINDS, f"{mode}: unknown kind {k}"

    def test_socratic_has_no_sidecars(self):
        assert SIDECAR_SPECS["socratic"] == ()

    def test_quick_has_bibliography_pair(self):
        assert SIDECAR_SPECS["quick"] == ("sources", "grading")

    def test_full_has_all_four(self):
        assert set(SIDECAR_SPECS["full"]) == set(SIDECAR_KINDS)

    def test_enforcement_value_is_known(self):
        assert SIDECAR_ENFORCEMENT in {"advisory", "required"}

    def test_required_sidecars_helper(self):
        assert required_sidecars("quick") == ("sources", "grading")
        assert required_sidecars("socratic") == ()
        assert required_sidecars("nonexistent") == ()


class TestSidecarFilename:
    def test_canonical_form(self):
        assert (
            sidecar_filename("full", "sources", "2026-05-17", "kras-inhibitors")
            == "2026-05-17_kras-inhibitors_full_sources.json"
        )

    def test_quick_grading(self):
        assert (
            sidecar_filename("quick", "grading", "2026-05-17", "topic")
            == "2026-05-17_topic_quick_grading.json"
        )

    def test_socratic_returns_empty(self):
        assert sidecar_filename("socratic", "sources", "2026-05-17", "x") == ""

    def test_unknown_kind_raises(self):
        with pytest.raises(ValueError, match="Unknown sidecar kind"):
            sidecar_filename("full", "bogus", "2026-05-17", "x")

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown mode"):
            sidecar_filename("bogus", "sources", "2026-05-17", "x")

    def test_kind_not_in_mode_raises(self):
        # quick mode does not have synthesis sidecar
        with pytest.raises(ValueError, match="not part of mode"):
            sidecar_filename("quick", "synthesis", "2026-05-17", "x")


# ───────────────────────────────────────────────────────────────────────
# Positive validation — minimal fixtures must validate clean
# ───────────────────────────────────────────────────────────────────────


class TestPositiveValidation:
    def test_sources_minimal_valid(self):
        v = SidecarValidator("sources")
        ok, errors, _warnings = v.validate(_load("sources_minimal.json"))
        assert ok, f"unexpected errors: {errors}"

    def test_grading_minimal_valid_with_source_join(self):
        v = SidecarValidator("grading")
        known = _load_paper_ids(FIXTURES / "sources_minimal.json")
        ok, errors, _warnings = v.validate(_load("grading_minimal.json"), known_paper_ids=known)
        assert ok, f"unexpected errors: {errors}"

    def test_synthesis_minimal_valid_with_source_join(self):
        v = SidecarValidator("synthesis")
        known = _load_paper_ids(FIXTURES / "sources_minimal.json")
        ok, errors, _warnings = v.validate(_load("synthesis_minimal.json"), known_paper_ids=known)
        assert ok, f"unexpected errors: {errors}"

    def test_advocate_minimal_valid(self):
        v = SidecarValidator("advocate")
        ok, errors, _warnings = v.validate(_load("advocate_minimal.json"))
        assert ok, f"unexpected errors: {errors}"


# ───────────────────────────────────────────────────────────────────────
# Negative cases — sources predicates S1-S4
# ───────────────────────────────────────────────────────────────────────


class TestSourcesPredicates:
    def test_S1_duplicate_paper_id(self):
        v = SidecarValidator("sources")
        ok, errors, _w = v.validate(_load("sources_invalid_duplicate_id.json"))
        assert not ok
        assert any("S1" in e and "duplicate" in e for e in errors), errors

    def test_S2_no_identifiers_and_not_grey(self):
        v = SidecarValidator("sources")
        data = _load("sources_minimal.json")
        data["sources"][0]["doi"] = None
        data["sources"][0]["pmid"] = None
        data["sources"][0]["pmcid"] = None
        ok, errors, _w = v.validate(data)
        assert not ok
        assert any(e.startswith("S2:") for e in errors), errors

    def test_S2_grey_lit_with_note_ok(self):
        v = SidecarValidator("sources")
        data = _load("sources_minimal.json")
        data["sources"][0]["doi"] = None
        data["sources"][0]["pmid"] = None
        data["sources"][0]["pmcid"] = None
        data["sources"][0]["source"] = "GreyLit"
        data["sources"][0]["grey_lit_note"] = "FDA briefing document, fetched 2026-05-17."
        ok, errors, _w = v.validate(data)
        assert ok, errors

    def test_S3_warns_on_zero_yield_database(self):
        v = SidecarValidator("sources")
        data = _load("sources_minimal.json")
        data["search_log"].append({
            "database": "ZeroYieldDB",
            "date": "2026-05-17",
            "query": "test",
            "results": 0,
            "after_dedup": 0,
            "trace_id": None,
        })
        ok, _e, warnings = v.validate(data)
        assert ok  # advisory only
        assert any("S3" in w and "ZeroYieldDB" in w for w in warnings), warnings

    def test_S4_rejects_future_timestamp(self):
        v = SidecarValidator("sources")
        data = _load("sources_minimal.json")
        data["metadata"]["frozen_at"] = "2099-01-01T00:00:00Z"
        ok, errors, _w = v.validate(data)
        assert not ok
        assert any(e.startswith("S4:") and "future" in e for e in errors), errors


# ───────────────────────────────────────────────────────────────────────
# Negative cases — grading predicates G1-G3
# ───────────────────────────────────────────────────────────────────────


class TestGradingPredicates:
    def test_G1_unknown_paper_id_flagged(self):
        v = SidecarValidator("grading")
        data = _load("grading_minimal.json")
        data["gradings"][0]["paper_id"] = "10.0000/nonexistent"
        known = _load_paper_ids(FIXTURES / "sources_minimal.json")
        ok, errors, _w = v.validate(data, known_paper_ids=known)
        assert not ok
        assert any(e.startswith("G1:") for e in errors), errors

    def test_G1_skipped_when_no_sources_supplied(self):
        v = SidecarValidator("grading")
        data = _load("grading_minimal.json")
        data["gradings"][0]["paper_id"] = "10.0000/nonexistent"
        ok, errors, _w = v.validate(data)
        # Schema still passes; G1 skipped without known_paper_ids
        assert ok, errors

    def test_G2_predatory_flag_requires_evidence(self):
        v = SidecarValidator("grading")
        data = _load("grading_minimal.json")
        data["gradings"][0]["predatory_flag"] = True
        data["gradings"][0]["predatory_evidence"] = None
        known = _load_paper_ids(FIXTURES / "sources_minimal.json")
        ok, errors, _w = v.validate(data, known_paper_ids=known)
        assert not ok
        assert any(e.startswith("G2:") for e in errors), errors

    def test_G3_advisory_when_verified_without_tier(self):
        v = SidecarValidator("grading")
        data = _load("grading_minimal.json")
        data["gradings"][0]["t_tier"] = None
        known = _load_paper_ids(FIXTURES / "sources_minimal.json")
        ok, _e, warnings = v.validate(data, known_paper_ids=known)
        assert ok
        assert any("G3" in w for w in warnings), warnings


# ───────────────────────────────────────────────────────────────────────
# Negative cases — synthesis predicates Y1-Y3
# ───────────────────────────────────────────────────────────────────────


class TestSynthesisPredicates:
    def test_Y1_unknown_supporting_id_flagged(self):
        v = SidecarValidator("synthesis")
        data = _load("synthesis_minimal.json")
        data["themes"][0]["supporting_paper_ids"].append("10.0000/ghost")
        known = _load_paper_ids(FIXTURES / "sources_minimal.json")
        ok, errors, _w = v.validate(data, known_paper_ids=known)
        assert not ok
        assert any(e.startswith("Y1:") for e in errors), errors

    def test_Y2_contradiction_distinct_ids(self):
        v = SidecarValidator("synthesis")
        data = _load("synthesis_minimal.json")
        # Build a contradiction with two identical paper_ids — schema accepts
        # (minItems=2) but Y2 should reject (not distinct).
        data["contradictions"].append({
            "id": "C-01",
            "claim_a": "ORR is high",
            "claim_b": "ORR is low",
            "paper_ids": ["10.1056/NEJMoa2103695", "10.1056/NEJMoa2103695"],
            "resolution_note": None,
        })
        known = _load_paper_ids(FIXTURES / "sources_minimal.json")
        ok, errors, _w = v.validate(data, known_paper_ids=known)
        assert not ok
        assert any(e.startswith("Y2:") for e in errors), errors

    def test_Y3_hypothesis_mode_requires_hypotheses(self):
        v = SidecarValidator("synthesis")
        data = _load("synthesis_minimal.json")
        data["metadata"]["mode"] = "hypothesis"
        # hypotheses still empty
        known = _load_paper_ids(FIXTURES / "sources_minimal.json")
        ok, errors, _w = v.validate(data, known_paper_ids=known)
        assert not ok
        assert any(e.startswith("Y3:") for e in errors), errors


# ───────────────────────────────────────────────────────────────────────
# Negative cases — advocate predicates A1-A3
# ───────────────────────────────────────────────────────────────────────


class TestAdvocatePredicates:
    def test_A1_duplicate_finding_id(self):
        v = SidecarValidator("advocate")
        data = _load("advocate_minimal.json")
        dup = deepcopy(data["findings"][0])
        data["findings"].append(dup)
        ok, errors, _w = v.validate(data)
        assert not ok
        assert any(e.startswith("A1:") for e in errors), errors

    def test_A2_closed_status_requires_resolution_note(self):
        v = SidecarValidator("advocate")
        data = _load("advocate_minimal.json")
        data["findings"][0]["status"] = "wont_fix"
        data["findings"][0]["resolution_note"] = None
        ok, errors, _w = v.validate(data)
        assert not ok
        assert any(e.startswith("A2:") for e in errors), errors

    def test_A3_advisory_when_open_critical_present(self):
        v = SidecarValidator("advocate")
        data = _load("advocate_minimal.json")
        data["findings"].append({
            "id": "A-999",
            "checkpoint": 3,
            "category": "ethics",
            "description": "Dual-use concern unresolved.",
            "severity": "CRITICAL",
            "status": "open",
            "resolution_note": None,
        })
        ok, _e, warnings = v.validate(data)
        assert ok  # advisory only
        assert any("A3" in w for w in warnings), warnings


# ───────────────────────────────────────────────────────────────────────
# Schema-level checks — make sure jsonschema actually catches malformed data
# ───────────────────────────────────────────────────────────────────────


class TestSchemaLevel:
    def test_sources_missing_required_field(self):
        v = SidecarValidator("sources")
        data = _load("sources_minimal.json")
        del data["sources"][0]["title"]
        ok, errors, _w = v.validate(data)
        assert not ok
        assert any("schema:" in e for e in errors), errors

    def test_grading_bad_verification_status_enum(self):
        v = SidecarValidator("grading")
        data = _load("grading_minimal.json")
        data["gradings"][0]["verification_status"] = "MAYBE"
        ok, errors, _w = v.validate(data)
        assert not ok
        assert any("schema:" in e for e in errors), errors

    def test_synthesis_theme_id_pattern(self):
        v = SidecarValidator("synthesis")
        data = _load("synthesis_minimal.json")
        data["themes"][0]["id"] = "Theme01"  # violates ^T-[0-9]{2}$
        ok, errors, _w = v.validate(data)
        assert not ok
        assert any("schema:" in e for e in errors), errors

    def test_advocate_severity_enum(self):
        v = SidecarValidator("advocate")
        data = _load("advocate_minimal.json")
        data["findings"][0]["severity"] = "SEVERE"
        ok, errors, _w = v.validate(data)
        assert not ok
        assert any("schema:" in e for e in errors), errors

    def test_unknown_kind_raises_at_construction(self):
        with pytest.raises(ValueError, match="Unknown sidecar kind"):
            SidecarValidator("bogus")
