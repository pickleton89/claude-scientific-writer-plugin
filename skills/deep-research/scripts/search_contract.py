#!/usr/bin/env python3
"""
Search contract builder for the deep-research pipeline.

Produces a frozen Search Contract at Phase 1 (Scoping) that the Bibliography
agent MUST follow during Phase 2 (Investigation). The contract enumerates the
exact databases that will be queried, distinguishing required channels (gated
by ``thresholds.MIN_DATABASES``) from optional channels (e.g. Scite reception,
Paperclip full-text) that are subject to mode-eligibility rules.

Mirrors the pattern of ``output_contract.py``: deterministic build at
Checkpoint 1, frozen on user approval, consumed by Phase 2 execution and
audited by ``search_audit.py`` before Checkpoint 2.

Usage:
    python search_contract.py <input.json>
    JSON: {"mode": "full", "domain": "biomedical", "research_question": "..."}

Output:
    Markdown rendering of the contract for Checkpoint 1, followed by JSON.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from thresholds import ALL_MODES, MIN_DATABASES, MIN_SOURCES

# ---------------------------------------------------------------------------
# Domain → tier table (mirrors agents/bibliography.md Step 3)
# Keys are canonical domain labels; values map tier → MCP/CLI database name.
# ---------------------------------------------------------------------------

DOMAIN_TIER_TABLE: dict[str, dict[str, str]] = {
    "biomedical": {
        "primary": "PubMed",
        "secondary": "Consensus",
        "tertiary": "bioRxiv",
    },
    "molecular": {
        "primary": "PubMed",
        "secondary": "bioRxiv",
        "tertiary": "Consensus",
    },
    "pharmacology": {
        "primary": "PubMed",
        "secondary": "Consensus",
        "tertiary": "bioRxiv",
    },
    "cross-domain": {
        "primary": "Consensus",
        "secondary": "PubMed",
        "tertiary": "bioRxiv",
    },
    "preprint-heavy": {
        "primary": "bioRxiv",
        "secondary": "PubMed",
        "tertiary": "Consensus",
    },
}

DEFAULT_DOMAIN = "biomedical"

# Capability key + tool metadata per database (resolved against
# skills/shared/tool-lookup.yaml at runtime by the Bibliography agent).
DATABASE_METADATA: dict[str, dict[str, str]] = {
    "PubMed": {
        "capability_key": "literature.search",
        "tool": "search_articles",
        "transport": "MCP",
    },
    "Consensus": {
        "capability_key": "literature.search",
        "tool": "search",
        "transport": "MCP",
    },
    "bioRxiv": {
        "capability_key": "literature.search",
        "tool": "search_preprints",
        "transport": "MCP",
    },
    "Scite": {
        "capability_key": "literature.citation_tallies",
        "tool": "search_literature",
        "transport": "MCP",
    },
    "Paperclip": {
        "capability_key": "literature.corpus_search",
        "tool": "paperclip search",
        "transport": "CLI",
    },
}

# Mode-eligibility for optional channels (mirrors bibliography.md §Step 4b
# for Scite and §Paperclip channel block).
SCITE_ELIGIBLE_MODES: frozenset[str] = frozenset(
    {"full", "lit-review", "systematic-review", "hypothesis"}
)
PAPERCLIP_ELIGIBLE_MODES: frozenset[str] = frozenset(
    {"full", "lit-review", "systematic-review", "hypothesis"}
)

# Modes that do not run a search phase at all.
NO_SEARCH_MODES: frozenset[str] = frozenset({"socratic", "review"})


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class DatabaseEntry:
    """Single database in the contract (required or optional)."""

    name: str
    capability_key: str
    tool: str
    transport: str  # "MCP" or "CLI"
    tier: str  # "primary" / "secondary" / "tertiary" / "reception" / "corpus"
    purpose: str = ""
    starter_query: str = ""
    skipped_reason: str = ""  # populated when the user strikes the channel

    def to_dict(self) -> dict:
        """Convert to JSON-serialisable dict."""
        return {
            "name": self.name,
            "capability_key": self.capability_key,
            "tool": self.tool,
            "transport": self.transport,
            "tier": self.tier,
            "purpose": self.purpose,
            "starter_query": self.starter_query,
            "skipped_reason": self.skipped_reason,
        }


@dataclass
class SearchContract:
    """Frozen search-phase contract produced at Phase 1 (Scoping)."""

    mode: str
    domain: str
    research_question: str
    required_databases: list[DatabaseEntry] = field(default_factory=list)
    optional_databases: list[DatabaseEntry] = field(default_factory=list)
    skipped_by_mode: list[DatabaseEntry] = field(default_factory=list)
    user_struck: list[DatabaseEntry] = field(default_factory=list)
    min_databases: int = 0
    min_sources: int = 0
    frozen: bool = False
    frozen_at: str = ""
    warnings: list[str] = field(default_factory=list)

    def freeze(self) -> None:
        """Lock the contract after user approval at Checkpoint 1."""
        if self.frozen:
            raise RuntimeError("Contract is already frozen")
        self.frozen = True
        self.frozen_at = datetime.now(timezone.utc).isoformat()

    def strike(self, database_name: str, reason: str = "user-removed") -> None:
        """
        Remove a database from the contract before freezing.

        The Bibliography agent's Checkpoint 1 surface lets the user opt out of
        specific channels; this method records that decision. Required channels
        cannot be struck below the ``min_databases`` floor — a ValueError is
        raised in that case so the user is forced to either override the mode
        or restore a channel.
        """
        if self.frozen:
            raise RuntimeError("Cannot modify a frozen contract")

        for collection_name in ("required_databases", "optional_databases"):
            collection = getattr(self, collection_name)
            for entry in list(collection):
                if entry.name == database_name:
                    if (
                        collection_name == "required_databases"
                        and len(self.required_databases) - 1 < self.min_databases
                    ):
                        raise ValueError(
                            f"Cannot strike '{database_name}': would leave "
                            f"{len(self.required_databases) - 1} required databases "
                            f"below the mode minimum of {self.min_databases}"
                        )
                    entry.skipped_reason = reason
                    collection.remove(entry)
                    self.user_struck.append(entry)
                    return
        raise KeyError(f"Database '{database_name}' not found in contract")

    def required_database_names(self) -> list[str]:
        """Return the list of required database names (used by search_audit)."""
        return [d.name for d in self.required_databases]

    def to_dict(self) -> dict:
        """Convert to JSON-serialisable dict."""
        return {
            "mode": self.mode,
            "domain": self.domain,
            "research_question": self.research_question,
            "required_databases": [d.to_dict() for d in self.required_databases],
            "optional_databases": [d.to_dict() for d in self.optional_databases],
            "skipped_by_mode": [d.to_dict() for d in self.skipped_by_mode],
            "user_struck": [d.to_dict() for d in self.user_struck],
            "min_databases": self.min_databases,
            "min_sources": self.min_sources,
            "frozen": self.frozen,
            "frozen_at": self.frozen_at,
            "warnings": list(self.warnings),
        }


# ---------------------------------------------------------------------------
# Contract builder (main entry point)
# ---------------------------------------------------------------------------


def _make_entry(name: str, tier: str, purpose: str, starter_query: str) -> DatabaseEntry:
    """Build a DatabaseEntry from the metadata table."""
    meta = DATABASE_METADATA[name]
    return DatabaseEntry(
        name=name,
        capability_key=meta["capability_key"],
        tool=meta["tool"],
        transport=meta["transport"],
        tier=tier,
        purpose=purpose,
        starter_query=starter_query,
    )


def _starter_query(database: str, research_question: str) -> str:
    """
    Build a starter query for the given database.

    Deliberately minimal — the Bibliography agent refines per Step 1 (Build
    Query) using MeSH terms, synonyms, and Boolean structure. The starter
    here is just a seed the user sees at Checkpoint 1.
    """
    rq = research_question.strip()
    if not rq:
        return ""
    if database == "PubMed":
        # Pre-Boolean stub; agent expands with [tiab]/[mh] tags downstream.
        return rq
    if database == "bioRxiv":
        return rq
    if database == "Consensus":
        return rq
    if database == "Scite":
        # Scite Step 4b is dois-only by default — term left empty here.
        return ""
    if database == "Paperclip":
        return rq
    return rq


def build_contract(
    mode: str,
    research_question: str = "",
    domain: str = DEFAULT_DOMAIN,
) -> SearchContract:
    """
    Build a Search Contract for the given mode + domain + RQ.

    The contract is returned UNFROZEN — call :meth:`SearchContract.freeze`
    after the user approves at Checkpoint 1.

    Args:
        mode: One of ``ALL_MODES``. Modes in ``NO_SEARCH_MODES`` produce an
            empty contract with a warning.
        research_question: User's RQ (used to seed starter queries).
        domain: One of ``DOMAIN_TIER_TABLE`` keys. Defaults to ``biomedical``.

    Returns:
        Unfrozen :class:`SearchContract` ready for Checkpoint 1 presentation.

    Raises:
        ValueError: If ``mode`` or ``domain`` is unknown.
    """
    if mode not in ALL_MODES:
        raise ValueError(
            f"Unknown mode '{mode}'. Must be one of: {', '.join(ALL_MODES)}"
        )

    contract = SearchContract(
        mode=mode,
        domain=domain,
        research_question=research_question,
        min_databases=MIN_DATABASES.get(mode, 0),
        min_sources=MIN_SOURCES.get(mode, 0),
    )

    if mode in NO_SEARCH_MODES:
        contract.warnings.append(
            f"Mode '{mode}' does not run a search phase — contract is empty."
        )
        return contract

    if domain not in DOMAIN_TIER_TABLE:
        raise ValueError(
            f"Unknown domain '{domain}'. Must be one of: "
            f"{', '.join(DOMAIN_TIER_TABLE)}"
        )

    # --- Required databases (per domain tier table) ---------------------------
    tier_map = DOMAIN_TIER_TABLE[domain]
    for tier in ("primary", "secondary", "tertiary"):
        db_name = tier_map[tier]
        contract.required_databases.append(
            _make_entry(
                name=db_name,
                tier=tier,
                purpose="discovery",
                starter_query=_starter_query(db_name, research_question),
            )
        )

    # --- Optional channels (mode-gated) ---------------------------------------
    # Scite reception assessment (Step 4b)
    scite_entry = _make_entry(
        name="Scite",
        tier="reception",
        purpose="post-search citation reception (USI, retraction notices)",
        starter_query=_starter_query("Scite", research_question),
    )
    if mode in SCITE_ELIGIBLE_MODES:
        contract.optional_databases.append(scite_entry)
    else:
        scite_entry.skipped_reason = f"mode '{mode}' not in Scite-eligible modes"
        contract.skipped_by_mode.append(scite_entry)

    # Paperclip full-text corpus
    paperclip_entry = _make_entry(
        name="Paperclip",
        tier="corpus",
        purpose="full-text discovery across PMC + bioRxiv + medRxiv + arXiv",
        starter_query=_starter_query("Paperclip", research_question),
    )
    if mode in PAPERCLIP_ELIGIBLE_MODES:
        contract.optional_databases.append(paperclip_entry)
    else:
        paperclip_entry.skipped_reason = (
            f"mode '{mode}' not in Paperclip-eligible modes"
        )
        contract.skipped_by_mode.append(paperclip_entry)

    # --- Sanity checks --------------------------------------------------------
    if len(contract.required_databases) < contract.min_databases:
        contract.warnings.append(
            f"Required-database count ({len(contract.required_databases)}) is "
            f"below mode minimum ({contract.min_databases}). Domain tier table "
            f"may be incomplete for domain '{domain}'."
        )

    return contract


# ---------------------------------------------------------------------------
# Human-readable rendering
# ---------------------------------------------------------------------------


def format_contract_for_user(contract: SearchContract) -> str:
    """Render the contract as readable markdown for Checkpoint 1 review."""
    lines: list[str] = []

    lines.append("# Search Contract")
    lines.append("")
    lines.append(f"**Mode:** {contract.mode}")
    lines.append(f"**Domain:** {contract.domain}")
    lines.append(
        f"**Research question:** {contract.research_question or '(not specified)'}"
    )
    lines.append(f"**Frozen:** {'yes — ' + contract.frozen_at if contract.frozen else 'no'}")
    lines.append("")
    lines.append(
        f"**Floor:** ≥{contract.min_databases} databases, "
        f"≥{contract.min_sources} sources (per `thresholds.MIN_DATABASES`/`MIN_SOURCES`)."
    )
    lines.append("")

    # --- Required databases ---
    lines.append("## Required Databases (gated)")
    lines.append("")
    if contract.required_databases:
        lines.append("| # | Database | Tier | Tool | Transport | Starter query |")
        lines.append("|---|----------|------|------|-----------|---------------|")
        for idx, db in enumerate(contract.required_databases, 1):
            query_cell = db.starter_query or "_(seeded by agent)_"
            lines.append(
                f"| {idx} | {db.name} | {db.tier} | `{db.tool}` | {db.transport} "
                f"| {query_cell} |"
            )
    else:
        lines.append("_(none — this mode does not run a search phase)_")
    lines.append("")

    # --- Optional databases ---
    if contract.optional_databases:
        lines.append("## Optional Channels (mode-eligible)")
        lines.append("")
        lines.append("| Database | Tier | Purpose | Tool |")
        lines.append("|----------|------|---------|------|")
        for db in contract.optional_databases:
            lines.append(
                f"| {db.name} | {db.tier} | {db.purpose} | `{db.tool}` |"
            )
        lines.append("")

    # --- Skipped by mode ---
    if contract.skipped_by_mode:
        lines.append("## Skipped (mode-ineligible)")
        lines.append("")
        for db in contract.skipped_by_mode:
            lines.append(f"- **{db.name}** — {db.skipped_reason}")
        lines.append("")

    # --- User-struck ---
    if contract.user_struck:
        lines.append("## Struck by user")
        lines.append("")
        for db in contract.user_struck:
            lines.append(f"- **{db.name}** — {db.skipped_reason}")
        lines.append("")

    # --- Warnings ---
    if contract.warnings:
        lines.append("## Warnings")
        lines.append("")
        for warning in contract.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point. Reads JSON, prints markdown + JSON contract."""
    if len(sys.argv) < 2:
        print("Usage: search_contract.py <input.json | json_string>")
        print(
            '  JSON: {"mode": "full", "domain": "biomedical", '
            '"research_question": "..."}'
        )
        sys.exit(1)

    arg = sys.argv[1]
    if arg.startswith("{"):
        data = json.loads(arg)
    else:
        with open(arg) as f:
            data = json.load(f)

    contract = build_contract(
        mode=data.get("mode", "full"),
        research_question=data.get("research_question", ""),
        domain=data.get("domain", DEFAULT_DOMAIN),
    )

    print(format_contract_for_user(contract))
    print("\n---\n")
    print(json.dumps(contract.to_dict(), indent=2))


if __name__ == "__main__":
    main()
