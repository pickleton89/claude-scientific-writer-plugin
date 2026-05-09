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
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from thresholds import ALL_MODES, MIN_DATABASES, MIN_SOURCES

# ---------------------------------------------------------------------------
# Domain → tier table (mirrors agents/bibliography.md Step 3)
# Keys are canonical domain labels; values map tier → MCP/CLI database name.
#
# NOTE: The tier table below is the *default* (used by quick mode and by
# preprint-heavy across all modes). For heavy modes (full / lit-review /
# systematic-review / hypothesis) and fact-check, ``_resolve_tier_table``
# swaps bioRxiv → Paperclip in non-preprint-heavy domains, since Paperclip's
# corpus already covers PMC + bioRxiv + medRxiv + arXiv as full text. See
# ``_resolve_tier_table`` for the per-mode resolution logic.
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

# Modes where Paperclip's PMC + bioRxiv + medRxiv + arXiv corpus replaces the
# bioRxiv MCP slot in the tier table (heavy modes + fact-check). preprint-heavy
# domain is exempt — direct bioRxiv MCP gives fresher metadata for hot-off-the-
# press preprint scans there.
PAPERCLIP_PROMOTED_MODES: frozenset[str] = frozenset(
    {"full", "lit-review", "systematic-review", "hypothesis", "fact-check"}
)

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
    "PubTator3": {
        "capability_key": "literature.entity_annotation",
        "tool": "pubtator3 search",
        "transport": "CLI",
    },
}

# Mode-eligibility for optional channels (mirrors bibliography.md §Step 4b
# for Scite and §Paperclip channel block).
SCITE_ELIGIBLE_MODES: frozenset[str] = frozenset(
    {"full", "lit-review", "systematic-review", "hypothesis"}
)
# Paperclip is now mode-eligible for heavy modes + fact-check. In domains
# other than preprint-heavy it is *required* (replaces bioRxiv in the tier
# table); in preprint-heavy it remains *optional* alongside primary bioRxiv.
PAPERCLIP_ELIGIBLE_MODES: frozenset[str] = frozenset(
    {"full", "lit-review", "systematic-review", "hypothesis", "fact-check"}
)
# PubTator3 is mode-eligible for heavy modes + fact-check. Promotes from
# optional → required when the RQ contains named biomedical entities (gene,
# disease, chemical, variant) per ``_detect_named_entities``.
PUBTATOR3_ELIGIBLE_MODES: frozenset[str] = frozenset(
    {"full", "lit-review", "systematic-review", "hypothesis", "fact-check"}
)

# Modes that do not run a search phase at all.
NO_SEARCH_MODES: frozenset[str] = frozenset({"socratic", "review"})


# ---------------------------------------------------------------------------
# Heuristics: Paperclip availability + named-entity detection
# ---------------------------------------------------------------------------


def _paperclip_available() -> bool:
    """Return True if the ``paperclip`` CLI binary is on PATH.

    Used to surface a Checkpoint 1 warning when Paperclip is required by the
    contract but the binary is missing. Per project decision, missing binary
    does not hard-fail — the user sees a warning and can either install/login
    or strike Paperclip explicitly. Run-time PATH check via ``shutil.which``;
    no subprocess call (``paperclip --version`` may prompt for OAuth refresh).
    """
    return shutil.which("paperclip") is not None


# Gene-symbol-shaped tokens: 2–6 uppercase letters optionally followed by digits
# (e.g. BRAF, EGFR, IL8, TP53, NF1). Excludes common English ALL-CAPS noise and
# common biomedical-but-not-gene acronyms via a stop-list. False positives just
# promote PubTator3 unnecessarily, which the user can strike at Checkpoint 1.
_GENE_SYMBOL_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,5}\b")
_GENE_SYMBOL_STOPLIST: frozenset[str] = frozenset(
    {
        # Generic English ALL-CAPS / Roman numerals (≥2 chars; 1-char entries
        # can never match the regex so omitted)
        "AND", "OR", "NOT", "THE", "FOR", "AM", "PM", "II", "III", "IV", "VI",
        "VII", "VIII", "IX", "XL",
        # Bio-data nouns / methods
        "DNA", "RNA", "MRNA", "CDNA", "TRNA", "RRNA", "SIRNA", "MIRNA",
        "PCR", "RTPCR", "QPCR", "ELISA", "FACS", "FISH", "GWAS",
        # Geographies / agencies
        "WHO", "USA", "EU", "UK", "US", "FDA", "EMA", "NIH", "NCI", "CDC",
        "MHRA", "PMDA", "NHS",
        # Tech / software acronyms
        "AI", "ML", "API", "URL", "HTTP", "JSON", "YAML", "CSV", "PDF",
        "HTML", "CSS", "OS", "ID", "IDS", "GMT", "UTC", "PI",
        # Common biomedical-but-not-gene acronyms (imaging, vitals, units of
        # care). Adding these prevents PubTator3 false-promotion on RQs like
        # "BMI and cancer risk" or "PET imaging in dementia". Note: 4+ char
        # gene tokens like MEG3 still match the regex and are NOT stoplisted
        # — only the bare ambiguous 2-3 char acronyms.
        "BMI", "MRI", "CT", "PET", "EEG", "ECG", "EKG", "MEG", "TMS",
        "NIRS", "ICU", "ER", "CV", "IQ", "CSF", "BP", "HR", "RR", "BMD",
        "VO2", "LDL", "HDL", "GFR", "AST", "ALT", "INR", "WBC", "RBC",
        "CRP", "TSH", "FEV1", "EMG", "ENT", "ENG",
    }
)
# Disease/chemical/variant keyword tokens. Length ≥4 ensures substring match
# is safe (no English-word false positives like "false"/"individuals" matching
# a 3-char "als"). Short keywords (e.g. "als" for ALS, "snp" for SNP) are
# handled separately below via word-boundary regex.
_DISEASE_KEYWORDS: frozenset[str] = frozenset(
    {
        "cancer", "tumor", "tumour", "carcinoma", "sarcoma", "leukemia",
        "lymphoma", "melanoma", "glioma", "metastasis", "metastatic",
        "diabetes", "alzheimer", "parkinson", "huntington",
        "obesity", "hypertension", "stroke", "infarction", "ischemia",
        "covid", "covid-19", "sars-cov-2", "influenza", "tuberculosis",
        "asthma", "copd", "fibrosis", "cirrhosis", "hepatitis",
        "arthritis", "psoriasis", "lupus", "crohn", "colitis",
        "schizophrenia", "depression", "autism", "epilepsy",
        "syndrome", "disease", "disorder", "deficiency",
    }
)
_VARIANT_KEYWORDS: frozenset[str] = frozenset(
    {"mutation", "variant", "polymorphism", "indel", "fusion", "deletion"}
)
# Short biomedical tokens (≤3 chars) that need word-boundary matching to
# avoid false positives via substring containment in common English words
# (e.g. "als" must not match "false", "individuals", "trials").
_SHORT_BIO_TOKENS_RE = re.compile(
    r"\b(?:als|snp|cml|aml|all|cll|gbm|nsclc|sclc|hcc|ckd|aki|chd|pad|dvt|"
    r"pe|mi|ms|ra|sle|ibd|uc|cd|ad|pd)\b",
    re.IGNORECASE,
)
# Drug-name suffix patterns common in INN nomenclature (e.g. -mab, -nib, -tinib).
_DRUG_SUFFIX_RE = re.compile(
    r"\b\w+(?:mab|nib|tinib|stat|olol|pril|sartan|prazole|cycline|mycin|"
    r"floxacin|cillin|parin|caine|done|formin|gliflozin|gliptin)\b",
    re.IGNORECASE,
)


def _detect_named_entities(research_question: str) -> bool:
    """Heuristic: does the RQ contain named biomedical entities?

    Returns True if any of the following appears in the RQ:
      - A gene-symbol-shaped ALL-CAPS token (BRAF, EGFR, TP53, ...) not on the
        stop-list
      - A disease/condition keyword (cancer, diabetes, alzheimer, ...)
      - A variant-class keyword (mutation, variant, fusion, ...)
      - A drug name with a recognized INN suffix (-mab, -nib, -tinib, ...)

    False positives just promote PubTator3 to required when it could have been
    optional — strikable at Checkpoint 1, low cost. False negatives leave it
    optional when entity-grounded search would have helped — also strikable
    via the ``has_named_entities=True`` override at ``build_contract``.
    """
    rq = (research_question or "").strip()
    if not rq:
        return False
    lower = rq.lower()
    # Disease / variant keyword hit (substring match — all tokens are ≥4 chars
    # so substring containment is safe).
    for kw in _DISEASE_KEYWORDS:
        if kw in lower:
            return True
    for kw in _VARIANT_KEYWORDS:
        if kw in lower:
            return True
    # Short biomedical acronyms (≤3 chars) — word-boundary match required to
    # avoid matching them inside English words.
    if _SHORT_BIO_TOKENS_RE.search(rq):
        return True
    # Drug INN suffix hit
    if _DRUG_SUFFIX_RE.search(rq):
        return True
    # Gene symbol shape (with stop-list filter)
    for match in _GENE_SYMBOL_RE.finditer(rq):
        token = match.group(0)
        if token not in _GENE_SYMBOL_STOPLIST:
            return True
    return False


def _resolve_tier_table(domain: str, mode: str) -> dict[str, str]:
    """Return the effective primary/secondary/tertiary tier table.

    For non-preprint-heavy domains in heavy/fact-check modes, swap bioRxiv
    → Paperclip (Paperclip's corpus already covers PMC + bioRxiv + medRxiv
    + arXiv as full text). For preprint-heavy or quick mode, return the
    default tier table unchanged.
    """
    base = DOMAIN_TIER_TABLE[domain]
    if mode not in PAPERCLIP_PROMOTED_MODES:
        return dict(base)
    if domain == "preprint-heavy":
        return dict(base)
    return {tier: ("Paperclip" if name == "bioRxiv" else name) for tier, name in base.items()}


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
    if database == "Scite":
        # Scite Step 4b is dois-only by default — term left empty here.
        return ""
    if database == "PubTator3":
        # PubTator3 entity-grounded queries are auto-tagged from bare symbols;
        # bibliography agent disambiguates first via `pubtator3 autocomplete`.
        return rq
    return rq


def build_contract(
    mode: str,
    research_question: str = "",
    domain: str = DEFAULT_DOMAIN,
    has_named_entities: bool | None = None,
) -> SearchContract:
    """
    Build a Search Contract for the given mode + domain + RQ.

    The contract is returned UNFROZEN — call :meth:`SearchContract.freeze`
    after the user approves at Checkpoint 1.

    Args:
        mode: One of ``ALL_MODES``. Modes in ``NO_SEARCH_MODES`` produce an
            empty contract with a warning.
        research_question: User's RQ (used to seed starter queries and to
            run the named-entity heuristic for PubTator3 promotion).
        domain: One of ``DOMAIN_TIER_TABLE`` keys. Defaults to ``biomedical``.
        has_named_entities: Override the named-entity detection heuristic.
            ``None`` (default) runs ``_detect_named_entities`` on the RQ;
            ``True`` forces PubTator3 promotion to required (when mode-eligible);
            ``False`` keeps PubTator3 optional. Use to override misfires.

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

    # --- Required databases (per resolved tier table) -------------------------
    # ``_resolve_tier_table`` swaps bioRxiv → Paperclip in non-preprint-heavy
    # domains for heavy modes + fact-check.
    tier_map = _resolve_tier_table(domain, mode)
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

    # If Paperclip is in the required tier table, surface a Checkpoint 1
    # warning when the binary is missing. We don't hard-fail — user can
    # acknowledge and proceed, then strike Paperclip if needed.
    paperclip_in_required = any(
        d.name == "Paperclip" for d in contract.required_databases
    )
    if paperclip_in_required and not _paperclip_available():
        contract.warnings.append(
            "Paperclip is required by this contract but the `paperclip` "
            "binary is not on PATH. Run `paperclip install` + "
            "`paperclip login`, or strike Paperclip at Checkpoint 1 to "
            "proceed without full-text corpus search."
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

    # Paperclip — only seat as optional when it is NOT already required (i.e.
    # preprint-heavy in heavy modes, where bioRxiv MCP stays primary but
    # Paperclip is still useful as a full-text complement).
    if not paperclip_in_required:
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

    # PubTator3 — entity-grounded discovery. Promotes from optional → required
    # when (a) mode is eligible AND (b) the RQ contains named biomedical
    # entities (per heuristic or explicit override).
    pubtator3_entry = _make_entry(
        name="PubTator3",
        tier="entity",
        purpose="entity-grounded discovery (gene/disease/chemical/variant co-mentions)",
        starter_query=_starter_query("PubTator3", research_question),
    )
    if mode in PUBTATOR3_ELIGIBLE_MODES:
        if has_named_entities is None:
            entities_present = _detect_named_entities(research_question)
        else:
            entities_present = bool(has_named_entities)
        if entities_present:
            pubtator3_entry.purpose = (
                "entity-grounded discovery (REQUIRED — RQ contains named "
                "biomedical entities; strike if heuristic misfired)"
            )
            contract.required_databases.append(pubtator3_entry)
        else:
            contract.optional_databases.append(pubtator3_entry)
    else:
        pubtator3_entry.skipped_reason = (
            f"mode '{mode}' not in PubTator3-eligible modes"
        )
        contract.skipped_by_mode.append(pubtator3_entry)

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
    lines.append(
        "_Note: in heavy modes + fact-check, Paperclip replaces bioRxiv as "
        "the full-text corpus (PMC + bioRxiv + medRxiv + arXiv). Preprint-"
        "heavy domain keeps bioRxiv MCP primary. PubTator3 is required when "
        "the RQ names biomedical entities (gene/disease/chemical/variant)._"
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
        has_named_entities=data.get("has_named_entities"),
    )

    print(format_contract_for_user(contract))
    print("\n---\n")
    print(json.dumps(contract.to_dict(), indent=2))


if __name__ == "__main__":
    main()
