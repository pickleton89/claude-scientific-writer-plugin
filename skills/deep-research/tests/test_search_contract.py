"""Tests for search_contract.py — Search Contract builder, freeze, strike."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from search_contract import (
    SCITE_ELIGIBLE_MODES,
    PAPERCLIP_ELIGIBLE_MODES,
    NO_SEARCH_MODES,
    build_contract,
    format_contract_for_user,
)


# ---------------------------------------------------------------------------
# Required databases — the regression case this whole feature exists for
# ---------------------------------------------------------------------------


def test_full_mode_biomedical_contract_has_three_required_dbs():
    """Full mode + biomedical domain must seat PubMed + Consensus + bioRxiv."""
    contract = build_contract(
        mode="full",
        research_question="EGFR resistance in NSCLC",
        domain="biomedical",
    )
    names = contract.required_database_names()
    assert names == ["PubMed", "Consensus", "bioRxiv"]
    assert contract.min_databases == 3
    assert contract.min_sources == 15
    # Tier metadata is preserved
    tiers = [d.tier for d in contract.required_databases]
    assert tiers == ["primary", "secondary", "tertiary"]


def test_cross_domain_promotes_consensus_to_primary():
    """Cross-domain RQs should put Consensus first (per bibliography.md tier table)."""
    contract = build_contract(
        mode="full",
        research_question="ML for protein design",
        domain="cross-domain",
    )
    names = contract.required_database_names()
    assert names[0] == "Consensus"
    assert "PubMed" in names
    assert "bioRxiv" in names


def test_preprint_heavy_promotes_biorxiv_to_primary():
    """Preprint-heavy domain puts bioRxiv first."""
    contract = build_contract(
        mode="full",
        research_question="latest CRISPR base-editing methods",
        domain="preprint-heavy",
    )
    assert contract.required_databases[0].name == "bioRxiv"


# ---------------------------------------------------------------------------
# Mode-eligibility for optional channels
# ---------------------------------------------------------------------------


def test_quick_mode_skips_scite_and_paperclip():
    """Quick mode is in neither Scite-eligible nor Paperclip-eligible sets."""
    contract = build_contract(
        mode="quick", research_question="x", domain="biomedical"
    )
    optional_names = [d.name for d in contract.optional_databases]
    assert "Scite" not in optional_names
    assert "Paperclip" not in optional_names

    skipped_names = [d.name for d in contract.skipped_by_mode]
    assert "Scite" in skipped_names
    assert "Paperclip" in skipped_names
    # Skip reasons reference the mode explicitly
    for entry in contract.skipped_by_mode:
        assert "quick" in entry.skipped_reason


def test_full_mode_includes_both_optional_channels():
    """Full mode is in both Scite-eligible and Paperclip-eligible sets."""
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    optional_names = [d.name for d in contract.optional_databases]
    assert set(optional_names) == {"Scite", "Paperclip"}
    assert contract.skipped_by_mode == []


def test_fact_check_mode_skips_both_optionals():
    """Fact-check skips both Scite (not in eligible set) and Paperclip."""
    contract = build_contract(
        mode="fact-check", research_question="x", domain="biomedical"
    )
    assert contract.optional_databases == []
    skipped = {d.name for d in contract.skipped_by_mode}
    assert skipped == {"Scite", "Paperclip"}


def test_no_search_modes_produce_empty_contract():
    """Socratic and review modes do not run a search phase."""
    for mode in NO_SEARCH_MODES:
        contract = build_contract(
            mode=mode, research_question="x", domain="biomedical"
        )
        assert contract.required_databases == []
        assert contract.optional_databases == []
        assert any("does not run a search phase" in w for w in contract.warnings)


# ---------------------------------------------------------------------------
# Frozen-contract invariants
# ---------------------------------------------------------------------------


def test_frozen_contract_rejects_strike():
    """After freeze(), strike() raises RuntimeError."""
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    contract.freeze()
    assert contract.frozen is True
    assert contract.frozen_at  # ISO timestamp set
    with pytest.raises(RuntimeError, match="frozen"):
        contract.strike("PubMed")


def test_double_freeze_raises():
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    contract.freeze()
    with pytest.raises(RuntimeError, match="already frozen"):
        contract.freeze()


# ---------------------------------------------------------------------------
# User-strike path (the "user picks" knob)
# ---------------------------------------------------------------------------


def test_user_strikes_optional_database():
    """User can strike an optional channel before freezing."""
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    assert "Paperclip" in [d.name for d in contract.optional_databases]
    contract.strike("Paperclip", reason="binary not installed")
    assert "Paperclip" not in [d.name for d in contract.optional_databases]
    assert "Paperclip" in [d.name for d in contract.user_struck]
    assert contract.user_struck[0].skipped_reason == "binary not installed"


def test_strike_below_min_databases_raises():
    """Cannot strike a required database below mode's MIN_DATABASES floor."""
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    # full has min_databases=3 and exactly 3 required — striking any required raises
    with pytest.raises(ValueError, match="below the mode minimum"):
        contract.strike("PubMed")


def test_strike_unknown_database_raises():
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    with pytest.raises(KeyError):
        contract.strike("NonexistentDB")


# ---------------------------------------------------------------------------
# Validation / errors
# ---------------------------------------------------------------------------


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="Unknown mode"):
        build_contract(mode="not-a-mode", research_question="x")


def test_unknown_domain_raises():
    with pytest.raises(ValueError, match="Unknown domain"):
        build_contract(mode="full", research_question="x", domain="not-a-domain")


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------


def test_to_dict_round_trip_preserves_required_databases():
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    d = contract.to_dict()
    assert d["mode"] == "full"
    assert d["domain"] == "biomedical"
    assert d["min_databases"] == 3
    assert [r["name"] for r in d["required_databases"]] == [
        "PubMed",
        "Consensus",
        "bioRxiv",
    ]
    assert d["frozen"] is False


def test_format_contract_for_user_includes_required_table():
    contract = build_contract(
        mode="full", research_question="EGFR", domain="biomedical"
    )
    rendered = format_contract_for_user(contract)
    assert "# Search Contract" in rendered
    assert "## Required Databases (gated)" in rendered
    assert "PubMed" in rendered
    assert "Consensus" in rendered
    assert "bioRxiv" in rendered


# ---------------------------------------------------------------------------
# Mode-eligibility set sanity (catches accidental drift if someone edits the
# constants in the future)
# ---------------------------------------------------------------------------


def test_eligibility_sets_match_bibliography_md_documentation():
    """Sets must match what bibliography.md / SKILL.md document."""
    expected = frozenset({"full", "lit-review", "systematic-review", "hypothesis"})
    assert SCITE_ELIGIBLE_MODES == expected
    assert PAPERCLIP_ELIGIBLE_MODES == expected
    assert NO_SEARCH_MODES == frozenset({"socratic", "review"})
