"""Minimal RFC 6902 JSON Patch implementation for spec iteration.

Supports the three operations needed for scoped spec edits: replace, add,
remove. Hand-rolled to avoid adding a runtime dependency.

Patch format (per RFC 6902):
    [
      {"op": "replace", "path": "/scientific_figure/style/aesthetic", "value": "infographic"},
      {"op": "add", "path": "/scientific_figure/components/-", "value": {...}},
      {"op": "remove", "path": "/scientific_figure/relationships/0"}
    ]

Path uses RFC 6901 JSON Pointer syntax: "/" separates segments, "-" appends
to arrays, "~0" escapes "~", "~1" escapes "/".
"""

from __future__ import annotations

import copy
from typing import Any

_SUPPORTED_OPS = {"replace", "add", "remove"}


class JsonPatchError(ValueError):
    pass


def _unescape(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def _parse_pointer(path: str) -> list[str]:
    if path == "":
        return []
    if not path.startswith("/"):
        raise JsonPatchError(f"Invalid JSON Pointer (must start with '/'): {path!r}")
    return [_unescape(t) for t in path.split("/")[1:]]


def _resolve_parent(doc: Any, tokens: list[str]) -> tuple[Any, str]:
    """Walk to the parent of the target; return (parent, last_token)."""
    if not tokens:
        raise JsonPatchError("Cannot operate on root with empty path")
    parent: Any = doc
    for tok in tokens[:-1]:
        if isinstance(parent, list):
            try:
                idx = int(tok)
            except ValueError as exc:
                raise JsonPatchError(
                    f"Expected integer index into list, got {tok!r}"
                ) from exc
            parent = parent[idx]
        elif isinstance(parent, dict):
            if tok not in parent:
                raise JsonPatchError(f"Path segment not found: {tok!r}")
            parent = parent[tok]
        else:
            raise JsonPatchError(
                f"Cannot traverse non-container at segment {tok!r}"
            )
    return parent, tokens[-1]


def _apply_op(doc: Any, op: dict[str, Any]) -> Any:
    op_name = op.get("op")
    if op_name not in _SUPPORTED_OPS:
        raise JsonPatchError(
            f"Unsupported op {op_name!r}; supported: {sorted(_SUPPORTED_OPS)}"
        )
    path = op.get("path")
    if not isinstance(path, str):
        raise JsonPatchError(f"Op missing string 'path': {op!r}")

    tokens = _parse_pointer(path)
    parent, last = _resolve_parent(doc, tokens)

    if op_name == "replace":
        if "value" not in op:
            raise JsonPatchError(f"replace op requires 'value': {op!r}")
        if isinstance(parent, list):
            parent[int(last)] = op["value"]
        else:
            if last not in parent:
                raise JsonPatchError(f"replace target does not exist: {path}")
            parent[last] = op["value"]
    elif op_name == "add":
        if "value" not in op:
            raise JsonPatchError(f"add op requires 'value': {op!r}")
        if isinstance(parent, list):
            if last == "-":
                parent.append(op["value"])
            else:
                parent.insert(int(last), op["value"])
        else:
            parent[last] = op["value"]
    elif op_name == "remove":
        if isinstance(parent, list):
            del parent[int(last)]
        else:
            if last not in parent:
                raise JsonPatchError(f"remove target does not exist: {path}")
            del parent[last]

    return doc


def apply_patch(spec: dict[str, Any], patch: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply an RFC 6902 patch to a spec, returning a new dict (input untouched).

    Args:
        spec: The original spec dict.
        patch: List of patch operations.

    Returns:
        A new dict with the patch applied. The input spec is not mutated.
    """
    if not isinstance(patch, list):
        raise JsonPatchError(f"Patch must be a list of ops, got {type(patch).__name__}")
    result = copy.deepcopy(spec)
    for op in patch:
        if not isinstance(op, dict):
            raise JsonPatchError(f"Each patch op must be a dict, got {op!r}")
        _apply_op(result, op)
    return result
