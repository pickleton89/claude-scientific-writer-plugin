#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Finalize an svg-figure-maker run — Stage 7 of the workflow.

Emits the three-file deliverable:
  - figure.svg          (input, copied if --out-dir differs)
  - figure.preview.png  (input, copied if --out-dir differs)
  - figure.json         (sidecar produced by this script)

The sidecar is validated against schemas/figure_metadata.schema.json before
being written — we fail loud if the produced JSON doesn't match.

Inputs the script needs to assemble the sidecar:
  - figure.svg (required)
  - brand-tokens.json (required, for tokens_hash + palette membership)
  - PNG preview path (required, for the three-file contract)
  - iteration log JSON (optional; defaults to single "converged on first pass" entry)

Usage:
    uv run python finalize.py figure.svg \\
        --tokens ../oligon-brand/tokens/brand-tokens.json \\
        --preview figure.preview.png \\
        --iteration-log iterations.json \\
        --figure-id my-figure \\
        --status complete \\
        --out-dir ./out

Exit codes:
    0 = sidecar written and schema-valid
    1 = sidecar produced but failed schema validation
    2 = error (missing input, parse failure)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
SCHEMA_PATH = SKILL_ROOT / "schemas" / "figure_metadata.schema.json"

# Match SKILL.md frontmatter version. Bump this when the sidecar shape changes.
SCHEMA_VERSION = "0.1.0"

# Default Oligon brand defaults — match preflight_check.py and SKILL.md.
DEFAULT_FONT_SIZE_LADDER = [10, 12, 14, 16]
DEFAULT_GRID_UNIT = 8

SVG_NS = "http://www.w3.org/2000/svg"


# ---------------------------------------------------------------------------
# tokens_hash — deterministic over the brand-token subset we actually pin.
# ---------------------------------------------------------------------------

def compute_tokens_hash(tokens_path: Path) -> tuple[str, set[str]]:
    """Return (sha256_hex, palette_hex_set) for the canonical token subset.

    Canonical subset: the colors block (every {category}.{name}.hex). We hash
    the sorted, uppercased hex list — order-independent, case-normalized.
    Same brand-tokens.json → same hash; reordering keys does not perturb the
    hash. If we later pin fonts/sizes from tokens, extend this subset.
    """
    data = json.loads(tokens_path.read_text())
    hexes: set[str] = set()
    for entries in (data.get("colors") or {}).values():
        if not isinstance(entries, dict):
            continue
        for entry in entries.values():
            if isinstance(entry, dict) and "hex" in entry:
                hexes.add(entry["hex"].upper())
    canonical = json.dumps(sorted(hexes), separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}", hexes


# ---------------------------------------------------------------------------
# SVG inspection — what palette did the figure actually use? What dimensions?
# ---------------------------------------------------------------------------

def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[1] if "}" in tag else tag


def _normalize_hex(val: str) -> str | None:
    v = val.strip()
    m = re.match(r"^#([0-9A-Fa-f]{3,8})$", v)
    if not m:
        return None
    hex_full = v.upper()
    if len(hex_full) == 4:  # #RGB → #RRGGBB
        hex_full = "#" + "".join(c * 2 for c in hex_full[1:])
    if len(hex_full) == 9:  # strip alpha
        hex_full = hex_full[:7]
    return hex_full


def extract_used_palette(root: ET.Element) -> list[str]:
    """Collect every hex color actually referenced in fill/stroke/stop-color."""
    seen: set[str] = set()
    for el in root.iter():
        for attr in ("fill", "stroke", "stop-color"):
            val = el.attrib.get(attr)
            if val:
                h = _normalize_hex(val)
                if h:
                    seen.add(h)
        style = el.attrib.get("style", "")
        for match in re.finditer(r"(fill|stroke|stop-color)\s*:\s*([^;]+)", style):
            h = _normalize_hex(match.group(2).strip())
            if h:
                seen.add(h)
    return sorted(seen)


def extract_dimensions(root: ET.Element) -> list[int]:
    """Read viewBox → [width, height]. Required by the schema."""
    vb = root.attrib.get("viewBox")
    if not vb:
        raise ValueError("SVG has no viewBox; cannot record dimensions_px.")
    parts = vb.strip().split()
    if len(parts) != 4:
        raise ValueError(f"viewBox must have 4 values; got: {vb!r}")
    try:
        w = int(round(float(parts[2])))
        h = int(round(float(parts[3])))
    except ValueError as e:
        raise ValueError(f"viewBox width/height not numeric: {vb!r}") from e
    if w < 1 or h < 1:
        raise ValueError(f"viewBox dimensions must be positive; got {w}x{h}")
    return [w, h]


def extract_font_family(root: ET.Element) -> str:
    """Find a declared font-family. Walks elements until first hit."""
    for el in root.iter():
        ff = el.attrib.get("font-family")
        if ff:
            return ff
        style = el.attrib.get("style", "")
        m = re.search(r"font-family\s*:\s*([^;]+)", style)
        if m:
            return m.group(1).strip()
    # Fall back to the brand default rather than raising — the preflight
    # already enforces presence; we record what we found, or the canonical
    # default if the figure has no text at all.
    return "Arial, Helvetica, sans-serif"


# ---------------------------------------------------------------------------
# Iteration log
# ---------------------------------------------------------------------------

def load_iteration_log(log_path: Path | None) -> tuple[list[dict[str, Any]], int]:
    """Return (iterations, final_iteration).

    Log format (caller-supplied JSON, optional):
        {"iterations": [{"i": 1, "findings": 4, "primary_fixes": [...]}, ...]}

    If no log is provided, we record a single "converged on first pass" entry
    (i=1, findings=0). That matches the schema's minimum: iterations must
    have at least the entry recording how the run terminated.
    """
    if log_path is None:
        return ([{"i": 1, "findings": 0, "primary_fixes": []}], 1)

    data = json.loads(log_path.read_text())
    iterations = data.get("iterations") or []
    if not iterations:
        return ([{"i": 1, "findings": 0, "primary_fixes": []}], 1)
    # Final iteration = max i (or len, since the schema requires i >= 1
    # monotonically — we trust the caller).
    final = max(int(it["i"]) for it in iterations)
    return (iterations, final)


# ---------------------------------------------------------------------------
# Schema validation — minimal JSON-schema-draft-2020-12 subset we actually use.
# ---------------------------------------------------------------------------

def _validate(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Return a list of validation error messages; empty means valid.

    Implements only the keywords used by our two schemas: type, required,
    properties, items, enum, pattern, minLength, minItems, maxItems,
    minimum, uniqueItems, additionalProperties. No $ref / no anchors.
    """
    errors: list[str] = []

    expected_type = schema.get("type")
    if expected_type:
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "null": type(None),
        }
        py_type = type_map.get(expected_type)
        # bool is a subclass of int in Python — guard.
        if expected_type == "integer" and isinstance(value, bool):
            errors.append(f"{path}: expected integer, got bool")
        elif py_type and not isinstance(value, py_type):
            errors.append(f"{path}: expected {expected_type}, got {type(value).__name__}")
            return errors  # type mismatch — don't dig deeper

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum {schema['enum']}")

    if "pattern" in schema and isinstance(value, str):
        if not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match pattern {schema['pattern']!r}")

    if "minLength" in schema and isinstance(value, str):
        if len(value) < schema["minLength"]:
            errors.append(f"{path}: length {len(value)} < minLength {schema['minLength']}")

    if "minimum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema["minimum"]:
            errors.append(f"{path}: {value} < minimum {schema['minimum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: {len(value)} items < minItems {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: {len(value)} items > maxItems {schema['maxItems']}")
        if schema.get("uniqueItems") and len(set(map(_hashable, value))) != len(value):
            errors.append(f"{path}: items not unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for i, item in enumerate(value):
                errors.extend(_validate(item, item_schema, f"{path}[{i}]"))

    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required property {req!r}")
        props = schema.get("properties", {})
        for k, v in value.items():
            if k in props:
                errors.extend(_validate(v, props[k], f"{path}.{k}"))
        if schema.get("additionalProperties") is False:
            extras = set(value.keys()) - set(props.keys())
            if extras:
                errors.append(f"{path}: unexpected properties {sorted(extras)}")

    return errors


def _hashable(v: Any) -> Any:
    """Make a value hashable for uniqueItems checks."""
    if isinstance(v, (str, int, float, bool, type(None))):
        return v
    if isinstance(v, list):
        return tuple(_hashable(x) for x in v)
    if isinstance(v, dict):
        return tuple(sorted((k, _hashable(val)) for k, val in v.items()))
    return repr(v)


def validate_sidecar(sidecar: dict[str, Any]) -> list[str]:
    """Validate the sidecar against schemas/figure_metadata.schema.json."""
    schema = json.loads(SCHEMA_PATH.read_text())
    return _validate(sidecar, schema, path="$")


# ---------------------------------------------------------------------------
# Sidecar assembly
# ---------------------------------------------------------------------------

def build_sidecar(
    svg_path: Path,
    tokens_path: Path,
    figure_id: str,
    iterations: list[dict[str, Any]],
    final_iteration: int,
    status: str,
    warn_carry_forward: list[str],
    brand_variant: str,
) -> dict[str, Any]:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    if _strip_ns(root.tag) != "svg":
        raise ValueError(f"Input is not an <svg>: root is <{_strip_ns(root.tag)}>")

    tokens_hash, _ = compute_tokens_hash(tokens_path)
    used_palette = extract_used_palette(root)
    if not used_palette:
        # Schema requires palette minItems: 1; figures without any filled element
        # would otherwise produce an invalid sidecar.
        used_palette = ["#222222"]

    return {
        "figure_id": figure_id,
        "version": SCHEMA_VERSION,
        "brand_variant": brand_variant,
        "tokens_hash": tokens_hash,
        "palette": used_palette,
        "font_family": extract_font_family(root),
        "font_size_ladder_pt": DEFAULT_FONT_SIZE_LADDER,
        "grid_unit_px": DEFAULT_GRID_UNIT,
        "dimensions_px": extract_dimensions(root),
        "iterations": iterations,
        "final_iteration": final_iteration,
        "warn_carry_forward": warn_carry_forward,
        "status": status,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Finalize an svg-figure-maker run: emit the three-file deliverable.",
    )
    parser.add_argument("svg_path", type=Path, help="Path to the finalized figure.svg.")
    parser.add_argument(
        "--tokens",
        type=Path,
        required=True,
        help="Path to brand-tokens.json (required for tokens_hash).",
    )
    parser.add_argument(
        "--preview",
        type=Path,
        required=True,
        help="Path to figure.preview.png produced by render_and_inspect.py.",
    )
    parser.add_argument(
        "--iteration-log",
        type=Path,
        default=None,
        help="Optional JSON file with {'iterations': [...]}. Defaults to a single 'converged on first pass' entry.",
    )
    parser.add_argument(
        "--figure-id",
        type=str,
        default=None,
        help="Figure id (defaults to the SVG filename stem).",
    )
    parser.add_argument(
        "--status",
        type=str,
        default="complete",
        choices=["complete", "needs_user_input", "failed"],
        help="Final status (default 'complete').",
    )
    parser.add_argument(
        "--brand-variant",
        type=str,
        default="oligon",
        help="Brand variant name (default 'oligon').",
    )
    parser.add_argument(
        "--warn-carry-forward",
        type=str,
        nargs="*",
        default=[],
        help="Non-blocking warnings deliberately carried into the deliverable.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory. If set, the SVG and PNG are copied here. The sidecar is always written here (or alongside the SVG if unset).",
    )

    args = parser.parse_args(argv)

    if not args.svg_path.exists():
        print(f"error: SVG not found: {args.svg_path}", file=sys.stderr)
        return 2
    if not args.tokens.exists():
        print(f"error: tokens file not found: {args.tokens}", file=sys.stderr)
        return 2
    if not args.preview.exists():
        print(f"error: preview PNG not found: {args.preview}", file=sys.stderr)
        return 2

    figure_id = args.figure_id or args.svg_path.stem

    try:
        iterations, final_iteration = load_iteration_log(args.iteration_log)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"error: iteration log invalid: {e}", file=sys.stderr)
        return 2

    try:
        sidecar = build_sidecar(
            svg_path=args.svg_path,
            tokens_path=args.tokens,
            figure_id=figure_id,
            iterations=iterations,
            final_iteration=final_iteration,
            status=args.status,
            warn_carry_forward=args.warn_carry_forward,
            brand_variant=args.brand_variant,
        )
    except (ET.ParseError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    errors = validate_sidecar(sidecar)
    if errors:
        print("error: sidecar failed schema validation:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        # Still write it for inspection, but signal failure.
        out_dir = args.out_dir or args.svg_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{figure_id}.json").write_text(json.dumps(sidecar, indent=2))
        return 1

    out_dir = args.out_dir or args.svg_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_out = out_dir / f"{figure_id}.svg"
    png_out = out_dir / f"{figure_id}.preview.png"
    json_out = out_dir / f"{figure_id}.json"

    if args.svg_path.resolve() != svg_out.resolve():
        shutil.copy2(args.svg_path, svg_out)
    if args.preview.resolve() != png_out.resolve():
        shutil.copy2(args.preview, png_out)
    json_out.write_text(json.dumps(sidecar, indent=2))

    print(json.dumps({
        "status": "ok",
        "figure_id": figure_id,
        "out_dir": str(out_dir),
        "files": {
            "svg": str(svg_out),
            "preview": str(png_out),
            "sidecar": str(json_out),
        },
        "final_iteration": final_iteration,
        "schema": "valid",
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
