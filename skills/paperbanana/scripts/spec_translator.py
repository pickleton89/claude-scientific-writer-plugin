"""Deterministic JSON-spec → prose translator for PaperBanana.

Takes a `scientific_figure` spec (validated against
references/scientific_figure.schema.json) and renders it into the two prose
strings that PaperBanana's GenerationInput already consumes:
`source_context` (descriptive: what to depict) and `communicative_intent`
(directive: what the figure should communicate).

`meta.doc_type` is read: a doc type with its own design ceiling (currently
only `graphical_abstract`) appends a budget hint as the last element of
`communicative_intent`. Every other doc type renders exactly as before.

Determinism contract: same spec dict → byte-identical output strings on
every call. Components are sorted by id; relationships render in
declaration order. No timestamps, no random ordering.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "references"
    / "scientific_figure.schema.json"
)


def load_schema() -> dict[str, Any]:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _validate(spec: dict[str, Any]) -> None:
    """Validate a spec against the schema. Raises on failure."""
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError(
            "jsonschema not installed. Install with: uv pip install jsonschema"
        ) from exc
    jsonschema.validate(instance=spec, schema=load_schema())


def _emphasis_phrase(emphasis: str) -> str:
    return {
        "primary": "(primary focus)",
        "secondary": "(supporting role)",
        "background": "(contextual element)",
    }.get(emphasis, "(supporting role)")


def _component_phrase(comp: dict[str, Any]) -> str:
    label = comp["label"]
    role = comp["role"].replace("_", " ")
    emphasis = comp.get("emphasis", "secondary")
    notes = comp.get("notes")
    base = f"{label} — a {role} {_emphasis_phrase(emphasis)}"
    if notes:
        base += f". {notes}"
    return base


def _relationship_phrase(rel: dict[str, Any], id_to_label: dict[str, str]) -> str:
    src = id_to_label.get(rel["from"], rel["from"])
    dst = id_to_label.get(rel["to"], rel["to"])
    rel_type = rel["type"].replace("_", " ")
    label = rel.get("label")
    base = f"{src} {rel_type} {dst}"
    if label:
        base += f" ({label})"
    return base


def _render_source_context(fig: dict[str, Any]) -> str:
    subject = fig["subject"]
    components = sorted(fig["components"], key=lambda c: c["id"])
    relationships = fig.get("relationships", [])
    supporting = fig["narrative"].get("supporting_details", [])

    id_to_label = {c["id"]: c["label"] for c in components}

    parts: list[str] = []
    parts.append(
        f"Subject: {subject['concept']} "
        f"(domain: {subject['domain']}; audience: {subject['audience']})."
    )

    parts.append("Components to depict:")
    for comp in components:
        parts.append(f"  - {_component_phrase(comp)}")

    if relationships:
        parts.append("Relationships:")
        for rel in relationships:
            parts.append(f"  - {_relationship_phrase(rel, id_to_label)}")

    if supporting:
        parts.append("Supporting details:")
        for detail in supporting:
            parts.append(f"  - {detail}")

    return "\n".join(parts)


def _render_style_hint(style: dict[str, Any]) -> str:
    aesthetic = style.get("aesthetic", "diagrammatic")
    density = style.get("density", "moderate")
    density_phrase = {
        "minimal": "minimal visual density with generous whitespace",
        "moderate": "moderate visual density",
        "rich": "rich, information-dense layout",
    }[density]
    return f"Render in a {aesthetic} style with {density_phrase}."


def _render_brand_hint(brand: dict[str, Any]) -> str:
    if not brand.get("use_oligon", True):
        primary = brand.get("primary_color")
        contrast = brand.get("contrast_color")
        if primary or contrast:
            colors: list[str] = []
            if primary:
                colors.append(f"primary {primary}")
            if contrast:
                colors.append(f"contrast {contrast}")
            return f"Use custom palette: {', '.join(colors)}."
        return "No brand palette constraints."
    overrides: list[str] = []
    if brand.get("primary_color"):
        overrides.append(f"override primary to {brand['primary_color']}")
    if brand.get("contrast_color"):
        overrides.append(f"override contrast to {brand['contrast_color']}")
    if overrides:
        return f"Apply Oligon brand styling; {'; '.join(overrides)}."
    return "Apply Oligon brand styling for colors and typography."


def _render_layout_hint(flow: str, controls: dict[str, Any]) -> str:
    flow_phrase = {
        "left_to_right": "horizontal left-to-right flow",
        "top_to_bottom": "vertical top-to-bottom flow",
        "radial": "radial layout with central focus",
        "circular": "circular/cyclical layout",
        "none": "no enforced flow direction",
    }.get(flow, "horizontal left-to-right flow")
    variation = controls.get("allow_layout_variation", "minor")
    variation_phrase = {
        "none": "do not vary the layout",
        "minor": "minor layout variation permitted",
        "moderate": "moderate layout variation permitted",
        "major": "major layout reorganization permitted",
    }[variation]
    locks: list[str] = []
    if controls.get("lock_components", True):
        locks.append("preserve component identity and labels exactly")
    if controls.get("lock_brand", True):
        locks.append("preserve brand colors")
    lock_phrase = "; ".join(locks)
    if lock_phrase:
        return f"Use {flow_phrase}; {variation_phrase}; {lock_phrase}."
    return f"Use {flow_phrase}; {variation_phrase}."


def _render_budget_hint(meta: dict[str, Any]) -> str:
    """Design-budget hint for doc types that carry their own ceiling.

    Only `graphical_abstract` has one today: a graphical abstract is read in
    seconds at table-of-contents thumbnail scale, so it inherits tighter
    element / text / legibility budgets than an in-paper figure
    (`../shared/references/graphical_abstract_spec.md`). Every other doc_type
    returns "" so its rendered intent stays byte-identical to before this
    hint existed.
    """
    if meta.get("doc_type") != "graphical_abstract":
        return ""
    return (
        "Graphical-abstract budgets: one claim only, and a single focal "
        "accent. Target 5 nodes and 6 arrows; 7 nodes and 9 arrows are "
        "absolute ceilings, and they are read together rather than "
        "separately — a figure sitting at both at once is a mechanism "
        "diagram and belongs in the paper as a numbered figure with a "
        "caption. Use fewer words than the written abstract and carry "
        "roughly 70% of the content visually rather than in text (two "
        "separate measures; both provisional/uncalibrated heuristics). "
        "Every label must stay legible when the figure is rendered ~250 px "
        "wide as a table-of-contents thumbnail — the thumbnail, not the "
        "print size, is the binding constraint."
    )


def translate_spec(spec: dict[str, Any], *, validate: bool = True) -> tuple[str, str]:
    """Translate a scientific_figure spec into (source_context, communicative_intent).

    Args:
        spec: The full spec dict (with top-level "scientific_figure" key).
        validate: If True (default), validate against the JSON schema first.

    Returns:
        Tuple of (source_context, communicative_intent) prose strings ready
        to pass to paperbanana's GenerationInput.
    """
    if validate:
        _validate(spec)

    fig = spec["scientific_figure"]

    source_context = _render_source_context(fig)

    style = fig.get("style", {})
    brand = fig.get("brand", {"use_oligon": True})
    controls = fig.get("controls", {})
    meta = fig.get("meta", {})
    flow = fig["narrative"].get("flow_direction", "left_to_right")

    intent_parts = [
        fig["narrative"]["key_message"],
        _render_style_hint(style),
        _render_brand_hint(brand),
        _render_layout_hint(flow, controls),
    ]
    # Appended, never inserted: the first four parts stay byte-identical so
    # only doc_type-gated specs see a changed intent string.
    budget_hint = _render_budget_hint(meta)
    if budget_hint:
        intent_parts.append(budget_hint)
    communicative_intent = " ".join(intent_parts)

    return source_context, communicative_intent
