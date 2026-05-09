"""Tests for search_audit.py — Phase 2 → Phase 3 hard gate."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from exit_criteria import audit_phase_2_search
from search_audit import audit_search, format_audit_for_user
from search_contract import build_contract


def _frozen_contract(mode: str = "full", domain: str = "biomedical") -> dict:
    """Build + freeze a contract, return its dict form.

    Uses ``has_named_entities=False`` so PubTator3 stays optional, keeping
    the canonical 3-required-databases shape for these audit tests.
    """
    c = build_contract(
        mode=mode,
        research_question="x",
        domain=domain,
        has_named_entities=False,
    )
    c.freeze()
    return c.to_dict()


# ---------------------------------------------------------------------------
# Pass cases
# ---------------------------------------------------------------------------


def test_audit_passes_when_all_required_dbs_called():
    contract = _frozen_contract(mode="full", domain="biomedical")
    result = audit_search(
        contract, ["PubMed", "Consensus", "Paperclip", "OpenAlex"]
    )
    assert result.passed is True
    assert result.missing_databases == []
    assert result.phase == "phase_2_investigation"


def test_audit_passes_when_optional_skipped():
    """Optional channels (Scite, PubTator3) are not part of the gate."""
    contract = _frozen_contract(mode="full", domain="biomedical")
    # Only the 4 required databases are present; no Scite, no PubTator3
    result = audit_search(
        contract, ["PubMed", "Consensus", "Paperclip", "OpenAlex"]
    )
    assert result.passed is True


def test_audit_passes_with_extra_databases_called():
    """Extra databases beyond the required set don't fail the gate."""
    contract = _frozen_contract(mode="full", domain="biomedical")
    result = audit_search(
        contract,
        [
            "PubMed", "Consensus", "Paperclip", "OpenAlex",
            "Scite", "PubTator3", "EuropePMC",
        ],
    )
    assert result.passed is True


# ---------------------------------------------------------------------------
# Fail cases — the regression this whole feature exists to prevent
# ---------------------------------------------------------------------------


def test_audit_fails_when_pubmed_only_in_full_mode():
    """The headline regression: full-mode run that only called PubMed must fail."""
    contract = _frozen_contract(mode="full", domain="biomedical")
    result = audit_search(contract, ["PubMed"])
    assert result.passed is False
    assert set(result.missing_databases) == {"Consensus", "Paperclip", "OpenAlex"}
    assert "Consensus" in result.message
    assert "Paperclip" in result.message
    assert "OpenAlex" in result.message


def test_audit_fails_when_one_db_missing():
    contract = _frozen_contract(mode="full", domain="biomedical")
    result = audit_search(contract, ["PubMed", "Consensus", "Paperclip"])
    assert result.passed is False
    assert result.missing_databases == ["OpenAlex"]


def test_audit_fails_with_empty_searched_list():
    contract = _frozen_contract(mode="full", domain="biomedical")
    result = audit_search(contract, [])
    assert result.passed is False
    assert set(result.missing_databases) == {
        "PubMed", "Consensus", "Paperclip", "OpenAlex",
    }


# ---------------------------------------------------------------------------
# Frozen-contract invariant
# ---------------------------------------------------------------------------


def test_audit_unfrozen_contract_raises():
    """Auditing an unfrozen contract is a programming error."""
    c = build_contract(mode="full", research_question="x", domain="biomedical")
    with pytest.raises(ValueError, match="unfrozen"):
        audit_search(c.to_dict(), ["PubMed"])


# ---------------------------------------------------------------------------
# Quick mode (lower threshold)
# ---------------------------------------------------------------------------


def test_quick_mode_audit_still_requires_all_required_dbs():
    """
    Quick mode has MIN_DATABASES=2, but the contract seats 4 required
    databases (3 tier slots + OpenAlex scholarly_graph). The audit checks
    contract-required, not the abstract minimum — so all four must be hit.
    """
    contract = _frozen_contract(mode="quick", domain="biomedical")
    assert len(contract["required_databases"]) == 4
    result = audit_search(contract, ["PubMed"])
    assert result.passed is False


def test_quick_mode_passes_when_all_four_called():
    contract = _frozen_contract(mode="quick", domain="biomedical")
    result = audit_search(
        contract, ["PubMed", "Consensus", "bioRxiv", "OpenAlex"]
    )
    assert result.passed is True


# ---------------------------------------------------------------------------
# Direct exit_criteria.audit_phase_2_search invariants (the wrapper)
# ---------------------------------------------------------------------------


def test_phase_gate_result_serialises_cleanly():
    result = audit_phase_2_search(["PubMed", "bioRxiv"], ["PubMed"])
    d = result.to_dict()
    assert d["passed"] is False
    assert d["phase"] == "phase_2_investigation"
    assert d["required_databases"] == ["PubMed", "bioRxiv"]
    assert d["searched_databases"] == ["PubMed"]
    assert d["missing_databases"] == ["bioRxiv"]


def test_format_audit_for_user_marks_failure_clearly():
    result = audit_phase_2_search(["PubMed", "bioRxiv"], ["PubMed"])
    rendered = format_audit_for_user(result)
    assert "FAILED" in rendered
    assert "bioRxiv" in rendered
    assert "loop back" in rendered


def test_format_audit_for_user_marks_pass():
    result = audit_phase_2_search(["PubMed"], ["PubMed"])
    rendered = format_audit_for_user(result)
    assert "PASSED" in rendered
