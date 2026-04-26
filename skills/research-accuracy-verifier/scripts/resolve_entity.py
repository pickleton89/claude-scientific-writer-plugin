#!/usr/bin/env python3
"""Thin delegation surface for Stage-6 named-entity sanity checks.

The `entity-resolution` skill (skills/entity-resolution/) is the canonical
resolver for gene/protein symbols, drug names, cell lines, and disease terms.
That skill ships only a SKILL.md + references/ — no Python — because resolution
is performed by Claude calling MCP tools (HGNC, UniProt, Cellosaurus, etc.).

This script:
  - Documents the delegation contract for Stage 6
  - Performs offline shape checks (recognised symbol patterns, known-collision
    aliases) so the LLM has a deterministic starting point
  - Returns a structured JSON record matching the entity-resolution skill's
    documented output shape

What this script does NOT do:
  - Call HGNC / UniProt / Cellosaurus / Jackson APIs (delegated to capability
    key `verification.entity_sanity` → entity-resolution skill)
  - Validate biological correctness (e.g., whether BRCA1 truly localises to nucleus)

Usage:
    uv run python resolve_entity.py --entity BRCA2 --type gene
    uv run python resolve_entity.py --entity CT26  --type cell_line --json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field, asdict

# Known short symbols with collision risk (sourced from
# skills/entity-resolution/references/known_collisions.md).
# This is a minimal deterministic seed; the entity-resolution skill maintains
# the authoritative list.
KNOWN_COLLISIONS = {
    "PC": "could mean: Pyruvate Carboxylase | Plasma Cell | Personal Computer",
    "CD4": "could mean: CD4 protein | T-cell receptor",
    "ALL": "could mean: Acute Lymphoblastic Leukaemia | the word 'all'",
    "CAR": "could mean: Chimeric Antigen Receptor | Coxsackievirus and Adenovirus Receptor",
    "MS": "could mean: Multiple Sclerosis | Mass Spectrometry",
}

GENE_SYMBOL_RE = re.compile(r"^[A-Z][A-Z0-9\-]{0,9}$")
DRUG_INN_RE = re.compile(r"^[a-z][a-z0-9\-]{2,}$")
CELL_LINE_RE = re.compile(r"^[A-Za-z0-9\-]{2,15}$")


@dataclass
class EntityCheck:
    entity: str
    entity_type: str
    shape_ok: bool
    collision_risk: str  # "none" | "low" | "HIGH"
    collision_detail: str | None
    delegate_to: str = "verification.entity_sanity (entity-resolution skill)"
    notes: list[str] = field(default_factory=list)


class EntityResolver:
    """Offline shape + known-collision check; full resolution delegated."""

    def check(self, entity: str, entity_type: str) -> EntityCheck:
        notes: list[str] = []
        shape_ok = self._shape_ok(entity, entity_type, notes)

        collision = "none"
        collision_detail = None
        if entity in KNOWN_COLLISIONS:
            collision = "HIGH"
            collision_detail = KNOWN_COLLISIONS[entity]
            notes.append(
                "Known short-symbol collision; entity-resolution skill MUST disambiguate "
                "with negative filters before any downstream claim is verified."
            )
        elif entity_type == "gene" and len(entity) <= 3:
            collision = "low"
            notes.append(
                "Short gene symbol (≤3 chars); recommend running entity-resolution skill "
                "before treating as a gene reference."
            )

        notes.append(
            "Live resolution (HGNC / UniProt / Cellosaurus / Jackson) not performed in v1.2; "
            "delegate to capability `verification.entity_sanity`."
        )
        return EntityCheck(
            entity=entity,
            entity_type=entity_type,
            shape_ok=shape_ok,
            collision_risk=collision,
            collision_detail=collision_detail,
            notes=notes,
        )

    def _shape_ok(self, entity: str, entity_type: str, notes: list[str]) -> bool:
        if entity_type == "gene":
            ok = bool(GENE_SYMBOL_RE.match(entity))
            if not ok:
                notes.append("Does not match HGNC-style gene symbol (e.g., BRCA2, TP53, CDK4).")
            return ok
        if entity_type == "drug":
            ok = bool(DRUG_INN_RE.match(entity)) or bool(DRUG_INN_RE.match(entity.lower()))
            if not ok:
                notes.append("Does not match INN drug name pattern (lowercase, ≥3 chars).")
            return ok
        if entity_type == "cell_line":
            ok = bool(CELL_LINE_RE.match(entity))
            if not ok:
                notes.append("Does not match cell line nomenclature pattern.")
            return ok
        notes.append(f"Unknown entity_type {entity_type!r}; only shape-checking known types.")
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline entity shape + collision check")
    parser.add_argument("--entity", required=True)
    parser.add_argument(
        "--type",
        dest="entity_type",
        required=True,
        choices=["gene", "drug", "cell_line", "disease", "antibody", "mouse_strain"],
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = EntityResolver().check(args.entity, args.entity_type)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(f"Entity:           {result.entity}")
        print(f"Type:             {result.entity_type}")
        print(f"Shape OK:         {result.shape_ok}")
        print(f"Collision risk:   {result.collision_risk}")
        if result.collision_detail:
            print(f"Collision detail: {result.collision_detail}")
        print(f"Delegate to:      {result.delegate_to}")
        for n in result.notes:
            print(f"  - {n}")


if __name__ == "__main__":
    main()
