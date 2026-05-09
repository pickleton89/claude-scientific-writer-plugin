"""Tests for search_contract.py — Search Contract builder, freeze, strike."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from search_contract import (
    NO_SEARCH_MODES,
    PAPERCLIP_ELIGIBLE_MODES,
    PAPERCLIP_PROMOTED_MODES,
    PUBTATOR3_ELIGIBLE_MODES,
    SCITE_ELIGIBLE_MODES,
    _detect_named_entities,
    _resolve_tier_table,
    build_contract,
    format_contract_for_user,
)


# ---------------------------------------------------------------------------
# Required databases — Paperclip replaces bioRxiv in heavy/fact-check modes
# for non-preprint-heavy domains.
# ---------------------------------------------------------------------------


def test_full_mode_biomedical_seats_paperclip_in_place_of_biorxiv():
    """Full + biomedical: PubMed + Consensus + Paperclip (bioRxiv replaced)."""
    # RQ has no named entities → PubTator3 stays optional, not in required.
    contract = build_contract(
        mode="full",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    names = contract.required_database_names()
    assert names == ["PubMed", "Consensus", "Paperclip"]
    assert contract.min_databases == 3
    assert contract.min_sources == 15
    tiers = [d.tier for d in contract.required_databases]
    assert tiers == ["primary", "secondary", "tertiary"]


def test_full_mode_biomedical_with_entities_promotes_pubtator3():
    """Named-entity RQ promotes PubTator3 to required (4th entry)."""
    contract = build_contract(
        mode="full",
        research_question="EGFR resistance in NSCLC",
        domain="biomedical",
    )
    names = contract.required_database_names()
    assert names[:3] == ["PubMed", "Consensus", "Paperclip"]
    assert "PubTator3" in names
    pubtator = next(d for d in contract.required_databases if d.name == "PubTator3")
    assert pubtator.tier == "entity"


def test_cross_domain_promotes_consensus_to_primary():
    """Cross-domain RQs put Consensus first; bioRxiv → Paperclip in heavy mode."""
    contract = build_contract(
        mode="full",
        research_question="ML for protein design",
        domain="cross-domain",
        has_named_entities=False,
    )
    names = contract.required_database_names()
    assert names[0] == "Consensus"
    assert "PubMed" in names
    assert "Paperclip" in names
    assert "bioRxiv" not in names


def test_preprint_heavy_keeps_biorxiv_primary():
    """Preprint-heavy domain exempt from bioRxiv → Paperclip swap."""
    contract = build_contract(
        mode="full",
        research_question="latest CRISPR base-editing methods",
        domain="preprint-heavy",
        has_named_entities=False,
    )
    assert contract.required_databases[0].name == "bioRxiv"
    names = contract.required_database_names()
    assert "bioRxiv" in names
    # Paperclip available as optional alongside primary bioRxiv
    optional_names = [d.name for d in contract.optional_databases]
    assert "Paperclip" in optional_names


def test_quick_mode_keeps_biorxiv_in_required():
    """Quick mode is NOT in PAPERCLIP_PROMOTED_MODES — bioRxiv stays."""
    contract = build_contract(
        mode="quick", research_question="x", domain="biomedical"
    )
    names = contract.required_database_names()
    assert "bioRxiv" in names
    assert "Paperclip" not in names


def test_fact_check_biomedical_seats_paperclip():
    """Fact-check is now in PAPERCLIP_PROMOTED_MODES — Paperclip required."""
    contract = build_contract(
        mode="fact-check",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    names = contract.required_database_names()
    assert "Paperclip" in names
    assert "bioRxiv" not in names


# ---------------------------------------------------------------------------
# Mode-eligibility for optional channels
# ---------------------------------------------------------------------------


def test_quick_mode_skips_scite_paperclip_pubtator3():
    """Quick mode is in none of the eligibility sets."""
    contract = build_contract(
        mode="quick", research_question="x", domain="biomedical"
    )
    optional_names = {d.name for d in contract.optional_databases}
    assert "Scite" not in optional_names
    assert "Paperclip" not in optional_names
    assert "PubTator3" not in optional_names

    skipped_names = {d.name for d in contract.skipped_by_mode}
    assert "Scite" in skipped_names
    assert "Paperclip" in skipped_names
    assert "PubTator3" in skipped_names
    for entry in contract.skipped_by_mode:
        assert "quick" in entry.skipped_reason


def test_full_mode_optional_channels_when_no_entities():
    """Full + RQ without entities: Scite + PubTator3 optional, Paperclip required."""
    contract = build_contract(
        mode="full",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    optional_names = {d.name for d in contract.optional_databases}
    assert optional_names == {"Scite", "PubTator3"}
    # Paperclip is REQUIRED, not optional
    assert "Paperclip" in contract.required_database_names()
    assert contract.skipped_by_mode == []


def test_fact_check_skips_scite_only_when_no_entities():
    """Fact-check: Scite skipped (mode-ineligible); Paperclip required; PubTator3 optional."""
    contract = build_contract(
        mode="fact-check",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    skipped = {d.name for d in contract.skipped_by_mode}
    assert "Scite" in skipped
    assert "Paperclip" not in skipped  # required
    assert "PubTator3" not in skipped  # optional
    optional_names = {d.name for d in contract.optional_databases}
    assert "PubTator3" in optional_names


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
    assert contract.frozen_at
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
# User-strike path
# ---------------------------------------------------------------------------


def test_user_strikes_optional_database():
    """User can strike an optional channel before freezing."""
    contract = build_contract(
        mode="full",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    # Scite is optional in full + biomedical
    assert "Scite" in [d.name for d in contract.optional_databases]
    contract.strike("Scite", reason="not needed for this RQ")
    assert "Scite" not in [d.name for d in contract.optional_databases]
    assert "Scite" in [d.name for d in contract.user_struck]
    assert contract.user_struck[0].skipped_reason == "not needed for this RQ"


def test_user_strikes_paperclip_in_preprint_heavy():
    """Preprint-heavy keeps Paperclip optional — user can strike it."""
    contract = build_contract(
        mode="full",
        research_question="x",
        domain="preprint-heavy",
        has_named_entities=False,
    )
    assert "Paperclip" in [d.name for d in contract.optional_databases]
    contract.strike("Paperclip", reason="binary not installed")
    assert "Paperclip" not in [d.name for d in contract.optional_databases]


def test_strike_below_min_databases_raises():
    """Cannot strike a required database below mode's MIN_DATABASES floor."""
    contract = build_contract(
        mode="full",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    # full has min_databases=3, with 3 required (PubMed/Consensus/Paperclip).
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
        mode="full",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    d = contract.to_dict()
    assert d["mode"] == "full"
    assert d["domain"] == "biomedical"
    assert d["min_databases"] == 3
    assert [r["name"] for r in d["required_databases"]] == [
        "PubMed",
        "Consensus",
        "Paperclip",
    ]
    assert d["frozen"] is False


def test_format_contract_for_user_includes_required_table():
    contract = build_contract(
        mode="full",
        research_question="EGFR",
        domain="biomedical",
    )
    rendered = format_contract_for_user(contract)
    assert "# Search Contract" in rendered
    assert "## Required Databases (gated)" in rendered
    assert "PubMed" in rendered
    assert "Consensus" in rendered
    assert "Paperclip" in rendered


# ---------------------------------------------------------------------------
# Mode-eligibility set sanity
# ---------------------------------------------------------------------------


def test_eligibility_sets_match_documented_semantics():
    """Sets must match what bibliography.md / SKILL.md document."""
    heavy_plus_factcheck = frozenset(
        {"full", "lit-review", "systematic-review", "hypothesis", "fact-check"}
    )
    assert SCITE_ELIGIBLE_MODES == frozenset(
        {"full", "lit-review", "systematic-review", "hypothesis"}
    )
    assert PAPERCLIP_ELIGIBLE_MODES == heavy_plus_factcheck
    assert PUBTATOR3_ELIGIBLE_MODES == heavy_plus_factcheck
    assert PAPERCLIP_PROMOTED_MODES == heavy_plus_factcheck
    assert NO_SEARCH_MODES == frozenset({"socratic", "review"})


# ---------------------------------------------------------------------------
# Tier-table resolution
# ---------------------------------------------------------------------------


def test_resolve_tier_table_swaps_biorxiv_in_heavy_modes():
    """Heavy mode + non-preprint-heavy → bioRxiv → Paperclip."""
    table = _resolve_tier_table("biomedical", "full")
    assert "bioRxiv" not in table.values()
    assert "Paperclip" in table.values()


def test_resolve_tier_table_preserves_biorxiv_in_quick():
    """Quick mode preserves bioRxiv even in biomedical domain."""
    table = _resolve_tier_table("biomedical", "quick")
    assert "bioRxiv" in table.values()
    assert "Paperclip" not in table.values()


def test_resolve_tier_table_preserves_biorxiv_in_preprint_heavy():
    """Preprint-heavy domain always keeps bioRxiv."""
    table = _resolve_tier_table("preprint-heavy", "full")
    assert "bioRxiv" in table.values()
    assert "Paperclip" not in table.values()


# ---------------------------------------------------------------------------
# Named-entity heuristic
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rq",
    [
        "EGFR resistance in NSCLC",
        "BRAF mutations in melanoma",
        "TP53 status across cancer types",
        "Imatinib response in CML",  # drug suffix -nib
        "trastuzumab efficacy",  # drug suffix -mab
        "type 2 diabetes risk factors",
        "alzheimer disease biomarkers",
        "CRISPR-Cas9 fusion variant",  # variant keyword
    ],
)
def test_detect_named_entities_positive_cases(rq):
    assert _detect_named_entities(rq) is True


@pytest.mark.parametrize(
    "rq",
    [
        "",
        "general overview of machine learning approaches",
        "review of statistical methods for clustering",
        "best practices in scientific writing",
        # Regression: 3-char tokens must NOT match inside common English words
        "false negatives in screening procedures",
        "individuals in the cohort were enrolled",
        "clinical trials methodology overview",
        "signals and noise in MEG recordings",
        "details of recruitment strategies",
    ],
)
def test_detect_named_entities_negative_cases(rq):
    assert _detect_named_entities(rq) is False


@pytest.mark.parametrize(
    "rq",
    [
        # Word-boundary biomedical short acronyms must still be detected
        "ALS progression markers",
        "SNP frequency in population genetics",
        "CML treatment response",
        "NSCLC survival outcomes",
        "DVT prophylaxis after surgery",
    ],
)
def test_detect_named_entities_short_acronym_cases(rq):
    """Short biomedical acronyms (als, snp, cml, ...) hit via word-boundary match."""
    assert _detect_named_entities(rq) is True


@pytest.mark.parametrize(
    "rq",
    [
        # Common medical acronyms that should NOT be treated as gene symbols
        "BMI and cardiovascular risk in adults",
        "MRI artifacts in pediatric imaging",
        "PET scan reproducibility study",
        "EEG biomarkers across age groups",
        "ICU staffing models in rural hospitals",
    ],
)
def test_common_medical_acronyms_not_treated_as_gene_symbols(rq):
    """BMI/MRI/PET/etc. are stoplisted so they don't auto-promote PubTator3.

    Note: some of these RQs still trigger via disease keywords (e.g.
    "cardiovascular" → no match here; "cardiovascular risk" doesn't match
    any disease keyword either). Test selects RQs whose only entity-candidate
    is the medical acronym itself.
    """
    assert _detect_named_entities(rq) is False


def test_has_named_entities_override_forces_promotion():
    """Even with a non-entity RQ, override=True promotes PubTator3."""
    contract = build_contract(
        mode="full",
        research_question="general writing tips",
        domain="biomedical",
        has_named_entities=True,
    )
    assert "PubTator3" in contract.required_database_names()


def test_has_named_entities_override_forces_demotion():
    """Even with an entity RQ, override=False keeps PubTator3 optional."""
    contract = build_contract(
        mode="full",
        research_question="EGFR resistance in NSCLC",
        domain="biomedical",
        has_named_entities=False,
    )
    assert "PubTator3" not in contract.required_database_names()
    optional_names = {d.name for d in contract.optional_databases}
    assert "PubTator3" in optional_names


# ---------------------------------------------------------------------------
# Paperclip availability warning
# ---------------------------------------------------------------------------


def test_missing_paperclip_emits_warning_when_required(monkeypatch):
    """When Paperclip is required but binary missing, contract carries a warning."""
    import search_contract

    monkeypatch.setattr(search_contract, "_paperclip_available", lambda: False)
    contract = build_contract(
        mode="full",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    assert any("paperclip" in w.lower() for w in contract.warnings)


def test_missing_paperclip_no_warning_when_not_required(monkeypatch):
    """In quick mode (Paperclip not required), no warning even if binary missing."""
    import search_contract

    monkeypatch.setattr(search_contract, "_paperclip_available", lambda: False)
    contract = build_contract(
        mode="quick", research_question="x", domain="biomedical"
    )
    assert not any("paperclip" in w.lower() for w in contract.warnings)
