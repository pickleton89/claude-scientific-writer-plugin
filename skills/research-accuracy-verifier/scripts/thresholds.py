"""Consolidated thresholds for the research-accuracy-verifier pipeline.

Constants-only module — no main(), no CLI. Mirrors the pattern of
`skills/deep-research/scripts/thresholds.py`: every quantitative constant /
artifact spec / enforcement flag that downstream scripts depend on lives
here.

Other scripts import via:

    sys.path.insert(0, str(Path(__file__).parent))
    from thresholds import ARTIFACT_KINDS, ARTIFACT_SPECS_BY_TIER, ...

This module is Phase-1 minimal — only the new evidence-pinning constants
land here. The existing P1–P8 logic stays in `validate_finding.py` /
`validate_audit_report.py` for now; a future consolidation may pull
predicate constants here too.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Artifact kinds (evidence pinning)
# ---------------------------------------------------------------------------
# Each artifact pins one piece of cross-stage state to disk so downstream
# stages and the assembled report read ground truth instead of
# reconstructing from conversation context. See SKILL.md §Pinned artifacts.
#
# Filename convention: `<kind>.json` inside `research/audits/<slug>/`.
# (Verifier slug dirs are already unique per audit, so no date prefix is
# needed — unlike deep-research which co-locates sidecars with the report.)

ARTIFACT_KINDS: Final[tuple[str, ...]] = (
    "document_inventory",
    "reference_map",
    "resolved_sources",
    "external_evidence",
)

# Per-tier required-artifact specs.
#
# Tier 1 (citation existence only) needs document_inventory + reference_map
# (Stage 1 prerequisites) + resolved_sources (Stage 2 output).
# Tier 2 adds external_evidence (Stage 2+ ledger for memoizing Scite/etc).
# Tier 3 same as Tier 2 (full audit; ledger still required).
# Custom is conditional — uses CUSTOM_ARTIFACT_DEPENDENCIES below to compute
# required set from `intake.checks_enabled`.

ARTIFACT_SPECS_BY_TIER: Final[dict[str, tuple[str, ...]]] = {
    "1":      ("document_inventory", "reference_map", "resolved_sources"),
    "2":      ("document_inventory", "reference_map", "resolved_sources", "external_evidence"),
    "3":      ("document_inventory", "reference_map", "resolved_sources", "external_evidence"),
    "custom": ("document_inventory",),  # always required; rest computed
}

# For tier == "custom", these are the artifact requirements per enabled check.
# Computed by `required_artifacts()` below.
CUSTOM_ARTIFACT_DEPENDENCIES: Final[dict[str, tuple[str, ...]]] = {
    "citation_existence":   ("reference_map", "resolved_sources"),
    "claim_alignment":      ("reference_map", "resolved_sources", "external_evidence"),
    "uncited_claims":       ("external_evidence",),
    "exact_quotes":         (),  # uses paperclip / web; no new artifacts in Phase 1
    "numerical_sanity":     (),  # cited_papers[] handoff already covers
    "named_entities":       (),
    "internal_consistency": ("reference_map",),
    "prose_quality_audit":  (),
}

# Feature flag — verifier enforcement of artifact presence/validity.
#
# "advisory" — missing or invalid artifacts emit warnings only; render
#              proceeds; R-predicates surface as warnings.
# "required" — missing or invalid artifacts block report rendering;
#              R-predicate failures become hard errors.
#
# Phase 1 ships as advisory. Phase 3 flips to "required" after an
# end-to-end dry-run validates the perturbation matrix.
ARTIFACT_ENFORCEMENT: Final[str] = "advisory"

# Per-tool freshness windows for the external-evidence ledger (Phase 2).
# A cached probe entry is reused when (now - fetched_at) ≤ freshness_days.
# Retraction status changes fastest (Scite/PubTator3), venue quality slowest.
ARTIFACT_FRESHNESS_DAYS: Final[dict[str, int]] = {
    "scite":     7,
    "openalex": 30,
    "pubtator3": 7,
    "pubmed":    7,
    "crossref": 30,
    "exa":       7,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def artifact_filename(kind: str) -> str:
    """Return the canonical filename for an artifact kind.

    Filenames are flat (no date prefix) because the audit slug directory
    is already unique. Mirrors deep-research's `sidecar_filename()` shape
    without the date/topic_slug prefixing.

    Raises:
        ValueError: if kind is not in ARTIFACT_KINDS.
    """
    if kind not in ARTIFACT_KINDS:
        raise ValueError(
            f"Unknown artifact kind: {kind!r}. Expected one of {ARTIFACT_KINDS}."
        )
    return f"{kind}.json"


def required_artifacts(
    tier: str,
    checks_enabled: list[str] | tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    """Return the tuple of artifact kinds required for a given tier + checks.

    For tier ∈ {"1","2","3"}, returns the pre-computed spec from
    `ARTIFACT_SPECS_BY_TIER`.

    For tier == "custom", composes the requirement set from
    `ARTIFACT_SPECS_BY_TIER["custom"]` (always-required base) plus the
    union of `CUSTOM_ARTIFACT_DEPENDENCIES` entries for every check in
    `checks_enabled`. Returns artifacts in `ARTIFACT_KINDS` order.

    Raises:
        ValueError: if tier is not recognized.
    """
    if tier not in ARTIFACT_SPECS_BY_TIER:
        raise ValueError(
            f"Unknown tier: {tier!r}. Expected one of "
            f"{tuple(ARTIFACT_SPECS_BY_TIER)}."
        )
    if tier != "custom":
        return ARTIFACT_SPECS_BY_TIER[tier]

    # Custom tier: union of base + per-check dependencies.
    base = set(ARTIFACT_SPECS_BY_TIER["custom"])
    for check in checks_enabled or []:
        base.update(CUSTOM_ARTIFACT_DEPENDENCIES.get(check, ()))
    # Preserve canonical ARTIFACT_KINDS order in the returned tuple.
    return tuple(k for k in ARTIFACT_KINDS if k in base)


# ---------------------------------------------------------------------------
# Self-consistency check (runs at import time)
# ---------------------------------------------------------------------------


def _validate_consistency() -> None:
    """Verify the constants are internally consistent. Raises ValueError on
    drift between ARTIFACT_KINDS, ARTIFACT_SPECS_BY_TIER, and
    CUSTOM_ARTIFACT_DEPENDENCIES."""
    for tier, kinds in ARTIFACT_SPECS_BY_TIER.items():
        unknown = set(kinds) - set(ARTIFACT_KINDS)
        if unknown:
            raise ValueError(
                f"ARTIFACT_SPECS_BY_TIER[{tier!r}] references unknown "
                f"artifact kinds: {sorted(unknown)}"
            )
    for check, kinds in CUSTOM_ARTIFACT_DEPENDENCIES.items():
        unknown = set(kinds) - set(ARTIFACT_KINDS)
        if unknown:
            raise ValueError(
                f"CUSTOM_ARTIFACT_DEPENDENCIES[{check!r}] references "
                f"unknown artifact kinds: {sorted(unknown)}"
            )
    if ARTIFACT_ENFORCEMENT not in {"advisory", "required"}:
        raise ValueError(
            f"ARTIFACT_ENFORCEMENT must be 'advisory' or 'required', "
            f"got {ARTIFACT_ENFORCEMENT!r}"
        )


_validate_consistency()
