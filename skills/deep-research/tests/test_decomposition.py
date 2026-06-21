"""Tests for the Phase-2 decomposition + complexity contracts.

Covers complexity_classifier (level heuristics), decomposition_contract
(fan-out width per complexity, mode capping, freeze, schema roundtrip), and
the validate_sidecar decomposition predicates D1-D3.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from complexity_classifier import classify_complexity  # noqa: E402
from decomposition_contract import build_decomposition_contract  # noqa: E402
from thresholds import COMPLEXITY_SCALING, FANOUT_MODES  # noqa: E402
from validate_sidecar import SidecarValidator  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "sidecars"


def _validate(record: dict):
    return SidecarValidator("decomposition").validate(record)


def _base_record() -> dict:
    return deepcopy(json.loads((FIXTURES / "decomposition_minimal.json").read_text()))


# ── complexity classifier ─────────────────────────────────────────────────


class TestComplexityClassifier:
    def test_comparative_signal(self):
        c = classify_complexity(
            "Efficacy of drug A versus drug B for condition C", "full"
        )
        assert c.level == "comparative"

    def test_complex_signal(self):
        c = classify_complexity(
            "What mechanisms drive resistance across multiple pathways?", "full"
        )
        assert c.level == "complex"

    def test_simple_signal(self):
        c = classify_complexity(
            "What are the approved indications for PCSK9 inhibitors as of 2026?",
            "quick",
        )
        assert c.level == "simple"

    def test_empty_uses_mode_prior(self):
        c = classify_complexity("", "systematic-review")
        assert c.level == "complex"
        assert c.confidence == "low"

    def test_comparative_beats_complex_when_both_present(self):
        c = classify_complexity("Compare the mechanisms of drug A vs drug B", "full")
        assert c.level == "comparative"

    def test_level_always_known(self):
        for rq in ("", "random text with no signals", "X vs Y", "mechanisms of Z"):
            assert classify_complexity(rq, None).level in COMPLEXITY_SCALING


# ── decomposition contract builder ─────────────────────────────────────────


class TestDecompositionContract:
    def test_full_complex_fans_out(self):
        k = build_decomposition_contract(
            "full",
            "What mechanisms drive resistance across multiple pathways and factors?",
            topic_slug="x",
        )
        assert k.complexity == "complex"
        assert k.fanout_eligible is True
        assert k.fan_out_width == COMPLEXITY_SCALING["complex"]["fan_out_default"]
        assert len(k.sub_questions) == k.fan_out_width
        ids = [sq.id for sq in k.sub_questions]
        assert ids == [f"SQ{i}" for i in range(1, k.fan_out_width + 1)]

    def test_quick_capped_to_single_context(self):
        k = build_decomposition_contract(
            "quick",
            "Approved indications for PCSK9 inhibitors as of 2026?",
            topic_slug="x",
        )
        assert k.fanout_eligible is False
        assert k.fan_out_width == 1
        assert len(k.sub_questions) == 1

    def test_comparative_full_within_bounds(self):
        k = build_decomposition_contract(
            "full", "Drug A versus drug B for condition C", topic_slug="x"
        )
        assert k.complexity == "comparative"
        assert 2 <= k.fan_out_width <= COMPLEXITY_SCALING["comparative"]["fan_out_max"]

    def test_width_override_clamped_to_cap(self):
        k = build_decomposition_contract(
            "full", "X vs Y", complexity="comparative", fan_out_width=99, topic_slug="x"
        )
        assert k.fan_out_width == COMPLEXITY_SCALING["comparative"]["fan_out_max"]

    def test_lit_review_not_fanout_eligible(self):
        assert "lit-review" not in FANOUT_MODES
        k = build_decomposition_contract(
            "lit-review", "mechanisms across multiple pathways", topic_slug="x"
        )
        assert k.fanout_eligible is False
        assert k.fan_out_width == 1

    def test_no_search_modes_raise(self):
        for mode in ("socratic", "review"):
            with pytest.raises(ValueError):
                build_decomposition_contract(mode, "anything")

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError):
            build_decomposition_contract("banana", "anything")

    def test_frozen_contract_validates(self):
        k = build_decomposition_contract(
            "full", "What mechanisms drive resistance across pathways?", topic_slug="x"
        )
        k.freeze()
        ok, errors, _ = _validate(k.to_dict())
        assert ok, errors

    def test_double_freeze_raises(self):
        k = build_decomposition_contract(
            "full", "mechanisms across pathways", topic_slug="x"
        )
        k.freeze()
        with pytest.raises(RuntimeError):
            k.freeze()


# ── validator predicates D1-D3 ─────────────────────────────────────────────


class TestDecompositionPredicates:
    def test_fixture_valid(self):
        ok, errors, _ = _validate(_base_record())
        assert ok, errors

    def test_d1_duplicate_id(self):
        record = _base_record()
        record["sub_questions"][1]["id"] = record["sub_questions"][0]["id"]
        ok, errors, _ = _validate(record)
        assert not ok
        assert any(e.startswith("D1") for e in errors)

    def test_d2_width_mismatch(self):
        record = _base_record()
        record["scaling"]["fan_out_width"] = len(record["sub_questions"]) - 1
        ok, errors, _ = _validate(record)
        assert not ok
        assert any(e.startswith("D2") for e in errors)

    def test_d2_exceeds_complexity_cap(self):
        record = _base_record()
        # 4 sub-questions + width 4, but 'simple' caps fan_out at 1.
        record["metadata"]["complexity"] = "simple"
        ok, errors, _ = _validate(record)
        assert not ok
        assert any(e.startswith("D2") and "cap" in e for e in errors)

    def test_d3_empty_delegation_field(self):
        record = _base_record()
        record["sub_questions"][0]["boundary"] = "   "
        ok, errors, _ = _validate(record)
        assert not ok
        assert any(e.startswith("D3") for e in errors)
