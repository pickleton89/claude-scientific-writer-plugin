"""Tests for search_contract.py — Search Contract builder, freeze, strike."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from search_contract import (
    NO_SEARCH_MODES,
    OPENALEX_REQUIRED_MODES,
    PAPERCLIP_ELIGIBLE_MODES,
    PAPERCLIP_PROMOTED_MODES,
    PUBTATOR3_ELIGIBLE_MODES,
    REGULATORY_ENTITY_PATTERN,
    SCITE_ELIGIBLE_MODES,
    WEBSEMANTIC_OPTIONAL_MODES,
    WEBSEMANTIC_REQUIRED_MODES,
    _detect_named_entities,
    _detect_regulatory_entities,
    _resolve_tier_table,
    build_contract,
    format_contract_for_user,
)


# ---------------------------------------------------------------------------
# Required databases — Paperclip replaces bioRxiv in heavy/fact-check modes
# for non-preprint-heavy domains.
# ---------------------------------------------------------------------------


def test_full_mode_biomedical_seats_paperclip_in_place_of_biorxiv():
    """Full + biomedical: PubMed + Consensus + Paperclip + OpenAlex + WebSemantic."""
    # RQ has no named entities → PubTator3 stays optional, not in required.
    # OpenAlex + WebSemantic are required across all heavy modes.
    contract = build_contract(
        mode="full",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    names = contract.required_database_names()
    assert names == [
        "PubMed", "Consensus", "Paperclip", "OpenAlex", "WebSemantic",
    ]
    assert contract.min_databases == 5
    assert contract.min_sources == 15
    tiers = [d.tier for d in contract.required_databases]
    assert tiers == [
        "primary", "secondary", "tertiary", "scholarly_graph", "web_discovery",
    ]


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
    """Full + RQ without entities: Scite + PubTator3 optional; Paperclip + WebSemantic required."""
    contract = build_contract(
        mode="full",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    optional_names = {d.name for d in contract.optional_databases}
    assert optional_names == {"Scite", "PubTator3"}
    # Paperclip and WebSemantic are REQUIRED, not optional
    required_names = set(contract.required_database_names())
    assert "Paperclip" in required_names
    assert "WebSemantic" in required_names
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
    # Use full + named entities to get 6 required (3 tier + OpenAlex +
    # WebSemantic + PubTator3) against floor=5. Strike PubTator3 first to drop
    # to the floor; the next strike must raise.
    contract = build_contract(
        mode="full",
        research_question="EGFR resistance",
        domain="biomedical",
    )
    assert len(contract.required_databases) == 6
    contract.strike("PubTator3")
    assert len(contract.required_databases) == 5
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
    assert d["min_databases"] == 5
    assert [r["name"] for r in d["required_databases"]] == [
        "PubMed",
        "Consensus",
        "Paperclip",
        "OpenAlex",
        "WebSemantic",
    ]
    # New strikable + notes fields round-trip.
    websem = next(r for r in d["required_databases"] if r["name"] == "WebSemantic")
    assert websem["strikable"] is True
    assert websem["notes"] == ""
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
    # OpenAlex covers every mode that runs a search phase.
    assert OPENALEX_REQUIRED_MODES == frozenset(
        {"full", "quick", "lit-review", "systematic-review", "hypothesis", "fact-check"}
    )
    # WebSemantic: required in heavy + fact-check, opt-in for systematic-review.
    assert WEBSEMANTIC_REQUIRED_MODES == frozenset(
        {"full", "lit-review", "hypothesis", "fact-check"}
    )
    assert WEBSEMANTIC_OPTIONAL_MODES == frozenset({"systematic-review"})
    # No overlap: a mode is either required or opt-in, never both.
    assert WEBSEMANTIC_REQUIRED_MODES.isdisjoint(WEBSEMANTIC_OPTIONAL_MODES)
    assert NO_SEARCH_MODES == frozenset({"socratic", "review"})


# ---------------------------------------------------------------------------
# OpenAlex required-channel coverage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", sorted(OPENALEX_REQUIRED_MODES))
@pytest.mark.parametrize(
    "domain",
    ["biomedical", "molecular", "pharmacology", "cross-domain", "preprint-heavy"],
)
def test_openalex_required_across_all_modes_and_domains(mode, domain):
    """OpenAlex is a required scholarly_graph channel for every search-running
    mode in every domain — that's the v1.7 contract."""
    contract = build_contract(
        mode=mode,
        research_question="x",
        domain=domain,
        has_named_entities=False,
    )
    names = contract.required_database_names()
    assert "OpenAlex" in names
    openalex = next(d for d in contract.required_databases if d.name == "OpenAlex")
    assert openalex.tier == "scholarly_graph"
    assert openalex.transport == "MCP"
    assert openalex.tool == "mcp__openalex__search_works"


def test_openalex_skipped_for_no_search_modes():
    """Socratic / review modes don't run search → no OpenAlex either."""
    for mode in NO_SEARCH_MODES:
        contract = build_contract(
            mode=mode, research_question="x", domain="biomedical"
        )
        assert "OpenAlex" not in contract.required_database_names()


def test_openalex_capability_key_in_contract():
    """Capability key on the OpenAlex entry must point at literature.search so
    bibliography agent can resolve it via tool-lookup.yaml."""
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    openalex = next(d for d in contract.required_databases if d.name == "OpenAlex")
    assert openalex.capability_key == "literature.search"


def test_format_contract_includes_openalex_behavior_note():
    """The Checkpoint 1 markdown must surface OpenAlex's role to the user."""
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    rendered = format_contract_for_user(contract)
    assert "OpenAlex" in rendered
    assert "scholarly_graph" in rendered
    assert "cross-disciplinary" in rendered.lower()


def test_user_can_strike_openalex_when_above_floor():
    """OpenAlex is strikable at Checkpoint 1 if floor is preserved."""
    contract = build_contract(
        mode="full",
        research_question="EGFR resistance",
        domain="biomedical",
    )
    # full + named entities = 6 required (3 tier + OpenAlex + WebSemantic +
    # PubTator3), floor = 5. Striking OpenAlex drops to 5 (== floor) — still
    # allowed.
    assert "OpenAlex" in contract.required_database_names()
    contract.strike("OpenAlex", reason="user-removed: cost")
    assert "OpenAlex" not in contract.required_database_names()
    struck = [d.name for d in contract.user_struck]
    assert "OpenAlex" in struck


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


# ---------------------------------------------------------------------------
# WebSemantic required-channel coverage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", sorted(WEBSEMANTIC_REQUIRED_MODES))
@pytest.mark.parametrize(
    "domain",
    ["biomedical", "molecular", "pharmacology", "cross-domain", "preprint-heavy"],
)
def test_websemantic_required_across_heavy_modes_and_factcheck(mode, domain):
    """WebSemantic is a required web_discovery channel in every heavy mode +
    fact-check across every domain — that's the v1.8 contract."""
    contract = build_contract(
        mode=mode,
        research_question="x",
        domain=domain,
        has_named_entities=False,
    )
    names = contract.required_database_names()
    assert "WebSemantic" in names, (
        f"WebSemantic missing in required for mode={mode}, domain={domain}"
    )
    entry = next(d for d in contract.required_databases if d.name == "WebSemantic")
    assert entry.tier == "web_discovery"
    assert entry.transport == "MCP"
    assert entry.tool == "mcp__exa__web_search_exa"
    assert entry.capability_key == "discovery.web_grey_literature"


def test_websemantic_not_required_in_systematic_review_default():
    """systematic-review excludes WebSemantic by default — opt-in only."""
    contract = build_contract(
        mode="systematic-review",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    required_names = contract.required_database_names()
    optional_names = {d.name for d in contract.optional_databases}
    skipped_names = {d.name for d in contract.skipped_by_mode}
    assert "WebSemantic" not in required_names
    assert "WebSemantic" not in optional_names
    assert "WebSemantic" not in skipped_names


def test_websemantic_not_required_in_quick():
    """quick excludes WebSemantic — not in any of the WebSemantic mode sets."""
    contract = build_contract(
        mode="quick", research_question="x", domain="biomedical"
    )
    assert "WebSemantic" not in contract.required_database_names()
    assert "WebSemantic" not in {d.name for d in contract.optional_databases}


def test_websemantic_absent_in_no_search_modes():
    """socratic + review run no search phase — WebSemantic is absent entirely."""
    for mode in NO_SEARCH_MODES:
        contract = build_contract(
            mode=mode, research_question="x", domain="biomedical"
        )
        assert "WebSemantic" not in contract.required_database_names()
        assert "WebSemantic" not in {d.name for d in contract.optional_databases}


# ---------------------------------------------------------------------------
# Fact-check auto-hardening on regulatory entities
# ---------------------------------------------------------------------------


def test_factcheck_with_regulatory_entity_hardens_websemantic():
    """Fact-check + RQ names a regulator → WebSemantic is non-strikable."""
    contract = build_contract(
        mode="fact-check",
        research_question="Did the FDA approve aducanumab in 2021?",
        domain="biomedical",
        has_named_entities=False,
    )
    entry = next(d for d in contract.required_databases if d.name == "WebSemantic")
    assert entry.strikable is False
    assert "auto-hardened" in entry.notes.lower()


def test_factcheck_without_regulatory_entity_keeps_websemantic_strikable():
    """Fact-check without regulator-shaped RQ → WebSemantic stays strikable."""
    contract = build_contract(
        mode="fact-check",
        research_question="Does aspirin reduce headache duration?",
        domain="biomedical",
        has_named_entities=False,
    )
    entry = next(d for d in contract.required_databases if d.name == "WebSemantic")
    assert entry.strikable is True
    assert entry.notes == ""


def test_full_mode_websemantic_is_strikable_by_default():
    """In non-fact-check heavy modes, WebSemantic is strikable (no auto-harden)."""
    contract = build_contract(
        mode="full",
        research_question="Did FDA approve drug X in 2024?",  # regulator token
        domain="biomedical",
        has_named_entities=False,
    )
    entry = next(d for d in contract.required_databases if d.name == "WebSemantic")
    # Auto-harden only kicks in for fact-check mode.
    assert entry.strikable is True


def test_strike_non_strikable_websemantic_raises():
    """Hardened WebSemantic cannot be struck even when floor is honored."""
    contract = build_contract(
        mode="fact-check",
        research_question="FDA recall of valsartan",
        domain="biomedical",
        has_named_entities=False,
    )
    # min_databases=5; 5 required → striking would also violate floor, but the
    # non-strikable check must fire FIRST (regardless of floor math).
    with pytest.raises(ValueError, match="non-strikable"):
        contract.strike("WebSemantic")


# ---------------------------------------------------------------------------
# Regulatory-entity detection
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rq",
    [
        "Did the FDA approve aducanumab?",
        "EMA assessment of paxlovid",
        "MHRA recall of valsartan",
        "NICE guidance on semaglutide",
        "WHO emergency use authorization for tecovirimat",
        "FDA-issued black box warning on fluoroquinolones",
        "Recall of metformin extended-release products",
        "Withdrawal of rofecoxib from US market",
        "Retraction of the Surgisphere hydroxychloroquine paper",
        "Expression of concern issued on Cell paper",
        "Boxed warning added to JAK inhibitors",
        "EUA revoked for hydroxychloroquine",
    ],
)
def test_detect_regulatory_entities_positive(rq):
    assert _detect_regulatory_entities(rq) is True


@pytest.mark.parametrize(
    "rq",
    [
        "",
        "Does aspirin reduce migraine frequency?",
        "Mechanism of EGFR resistance in lung cancer",
        "Single-cell atlases of the developing brain",
        "Best practices for image quantification in fluorescence microscopy",
        # Regression: ensure `retract\w+` doesn't false-match "retractable" —
        # the tight suffix list `retract(?:ed|ing|ion|ions)?\b` is in place
        # precisely to avoid this. "Retractable" is a non-regulatory term and
        # must NOT auto-harden WebSemantic.
        "Are retractable syringes safer than fixed-needle designs?",
        "Retractable cable assemblies in dental devices",
    ],
)
def test_detect_regulatory_entities_negative(rq):
    assert _detect_regulatory_entities(rq) is False


def test_regulatory_pattern_is_case_insensitive():
    """Pattern should be IGNORECASE so 'fda' / 'FDA' / 'Fda' all match."""
    for token in ("fda", "FDA", "Fda", "Recall", "RECALL"):
        assert REGULATORY_ENTITY_PATTERN.search(token) is not None


# ---------------------------------------------------------------------------
# Strike floor with WebSemantic in heavy modes
# ---------------------------------------------------------------------------


def test_strike_websemantic_in_full_mode_above_floor():
    """In full + no entities: 5 required, floor=5 → striking WebSemantic must
    raise (would drop to 4 < 5). Demonstrates the +1 floor bump from
    WebSemantic actually constrains strikes."""
    contract = build_contract(
        mode="full",
        research_question="x",
        domain="biomedical",
        has_named_entities=False,
    )
    assert len(contract.required_databases) == 5
    assert contract.min_databases == 5
    with pytest.raises(ValueError, match="below the mode minimum"):
        contract.strike("WebSemantic")


def test_format_contract_mentions_websemantic_note():
    """The Checkpoint 1 markdown surfaces WebSemantic's role to the user."""
    contract = build_contract(
        mode="full", research_question="x", domain="biomedical"
    )
    rendered = format_contract_for_user(contract)
    assert "WebSemantic" in rendered
    assert "web_discovery" in rendered
    assert "grey-lit" in rendered.lower() or "grey lit" in rendered.lower()


def test_factcheck_regulatory_plus_named_entities_hardens_and_promotes():
    """Interaction: fact-check RQ that names BOTH a regulator AND a drug INN
    suffix (`FDA approval of trastuzumab`) must (a) auto-harden WebSemantic
    AND (b) auto-promote PubTator3 to required. The two heuristics are
    independent and must compose."""
    contract = build_contract(
        mode="fact-check",
        research_question="FDA approval of trastuzumab for HER2+ breast cancer",
        domain="biomedical",
        # Don't override — let the named-entity heuristic fire on "trastuzumab"
        # (drug INN suffix -mab) and "breast cancer" (disease keyword).
    )
    names = contract.required_database_names()
    assert "WebSemantic" in names
    assert "PubTator3" in names  # promoted by named-entity heuristic
    websem = next(d for d in contract.required_databases if d.name == "WebSemantic")
    assert websem.strikable is False  # hardened by regulatory regex
    pubtator = next(d for d in contract.required_databases if d.name == "PubTator3")
    # PubTator3 is strikable by default — only WebSemantic gets hardened in
    # fact-check + regulator RQs.
    assert pubtator.strikable is True


def test_frozen_contract_rejects_strike_before_strikable_check():
    """Strike ordering: frozen × non-strikable → frozen wins (the contract
    is immutable, period, regardless of the per-entry strikable flag)."""
    contract = build_contract(
        mode="fact-check",
        research_question="FDA recall of valsartan",
        domain="biomedical",
        has_named_entities=False,
    )
    # WebSemantic is non-strikable here; freeze the contract first.
    contract.freeze()
    # Both error conditions exist; frozen check must run first.
    with pytest.raises(RuntimeError, match="frozen"):
        contract.strike("WebSemantic")


def test_to_dict_round_trip_preserves_hardened_websemantic_state():
    """The `strikable=False` + `notes` fields must round-trip in `to_dict()`
    so audit/replay tooling sees the same hardening decision later."""
    contract = build_contract(
        mode="fact-check",
        research_question="FDA recall of valsartan",
        domain="biomedical",
        has_named_entities=False,
    )
    d = contract.to_dict()
    ws = next(r for r in d["required_databases"] if r["name"] == "WebSemantic")
    assert ws["strikable"] is False
    assert "auto-hardened" in ws["notes"].lower()
    assert "regulatory-entity" in ws["notes"].lower()
