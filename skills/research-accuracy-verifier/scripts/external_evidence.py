#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""External-evidence ledger for the research-accuracy-verifier.

Append-only JSON ledger of external tool calls (Scite, PubTator3, OpenAlex,
PubMed, Exa, Crossref). Stages 2-4 route every external call through
`lookup_or_fetch` so retraction / venue / entity probes are memoized within
freshness windows.

Library-only this phase — no CLI. Callers:

    from external_evidence import lookup_or_fetch, record_consumption

    digest, cached = lookup_or_fetch(
        ledger_path=Path("research/audits/X/external_evidence.json"),
        tool="scite",
        method="scite_context",
        query_params={"doi": "10.1038/foo"},
        paper_id="10.1038/foo",
        fetcher=lambda: my_scite_call(...),
        freshness_days=None,  # uses thresholds.ARTIFACT_FRESHNESS_DAYS["scite"]
    )

Single-writer assumption: the verifier runs stages sequentially. If a future
caller parallelizes ledger writes, replace the temp-file-rename with a file
lock or switch to SQLite (see plan §12 risks).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from thresholds import ARTIFACT_FRESHNESS_DAYS  # noqa: E402

SCHEMA_VERSION = "1.0"
_RESPONSE_DIGEST_MAX = 512


def canonicalize_query(query_params: dict[str, Any]) -> str:
    """Canonical JSON of query_params: sorted keys, string values lowercased.

    Used as the SHA-256 pre-image for query_hash. Lowercasing string values
    means `{"doi": "10.1038/X"}` and `{"doi": "10.1038/x"}` collide — DOIs
    and identifier params are case-insensitive in practice, and per-tool
    normalization happens upstream.
    """
    def _normalize(v: Any) -> Any:
        if isinstance(v, str):
            return v.lower()
        if isinstance(v, dict):
            return {k: _normalize(v[k]) for k in sorted(v)}
        if isinstance(v, list):
            return [_normalize(x) for x in v]
        return v

    normalized = _normalize(query_params)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))


def query_hash(query_params: dict[str, Any]) -> str:
    """SHA-256 hex of the canonicalized query_params."""
    return hashlib.sha256(
        canonicalize_query(query_params).encode("utf-8")
    ).hexdigest()


def _parse_iso8601(s: str) -> datetime | None:
    try:
        ts = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    """Write payload as JSON atomically via temp-file + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=False)
            fh.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _load_or_init_ledger(
    ledger_path: Path, audit_slug: str | None
) -> dict[str, Any]:
    if ledger_path.exists():
        return json.loads(ledger_path.read_text(encoding="utf-8"))
    if not audit_slug:
        # Derive from parent directory name (typical layout:
        # research/audits/<slug>/external_evidence.json).
        audit_slug = ledger_path.parent.name or "unknown"
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "audit_slug": audit_slug,
            "opened_at": _now_iso(),
        },
        "entries": [],
    }


def _next_entry_id(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return "E0001"
    # Highest numeric suffix + 1; ignore malformed.
    nums = []
    for e in entries:
        eid = e.get("id", "")
        if isinstance(eid, str) and eid.startswith("E") and eid[1:].isdigit():
            nums.append(int(eid[1:]))
    next_n = (max(nums) + 1) if nums else 1
    return f"E{next_n:04d}"


def _matches(
    entry: dict[str, Any], tool: str, qhash: str, paper_id: str | None
) -> bool:
    """Cache key match. Same tool + same query_hash + same paper_id scope.

    paper_id is part of the key because the same query_params can return
    paper-scoped vs free-text data depending on whether paper_id is set.
    """
    if entry.get("tool") != tool:
        return False
    if entry.get("query_hash") != qhash:
        return False
    if (entry.get("paper_id") or None) != (paper_id or None):
        return False
    return True


def _is_fresh(entry: dict[str, Any], freshness_days: int) -> bool:
    fetched_at = entry.get("fetched_at")
    if not isinstance(fetched_at, str):
        return False
    ts = _parse_iso8601(fetched_at)
    if ts is None:
        return False
    age = datetime.now(timezone.utc) - ts
    return age.total_seconds() <= freshness_days * 86400


def lookup_or_fetch(
    ledger_path: Path,
    tool: str,
    method: str,
    query_params: dict[str, Any],
    paper_id: str | None,
    fetcher: Callable[[], str | dict[str, Any]],
    freshness_days: int | None = None,
    audit_slug: str | None = None,
) -> tuple[str, bool]:
    """Return (response_digest, was_cached).

    Cache key: (tool, query_hash(query_params), paper_id).
    TTL: ``freshness_days`` if provided, else
    ``thresholds.ARTIFACT_FRESHNESS_DAYS[tool]``.

    Cache hit → returns the stored digest, was_cached=True. Ledger untouched.
    Cache miss / stale → calls ``fetcher()``, normalizes its return to a
    string ≤ 512 chars, appends a new entry, atomic-writes, returns the
    fresh digest, was_cached=False.

    fetcher may return either a string (used verbatim, truncated) or a dict
    (JSON-serialized to a single-line string, truncated). Callers should
    pre-summarize when responses are large.

    Raises:
        KeyError: if freshness_days is None and tool is not in
                  ARTIFACT_FRESHNESS_DAYS.
    """
    if freshness_days is None:
        if tool not in ARTIFACT_FRESHNESS_DAYS:
            raise KeyError(
                f"No freshness window configured for tool={tool!r}; pass "
                f"freshness_days explicitly or add to "
                f"thresholds.ARTIFACT_FRESHNESS_DAYS"
            )
        freshness_days = ARTIFACT_FRESHNESS_DAYS[tool]

    qhash = query_hash(query_params)
    ledger = _load_or_init_ledger(Path(ledger_path), audit_slug)
    entries: list[dict[str, Any]] = ledger.setdefault("entries", [])

    for entry in entries:
        if _matches(entry, tool, qhash, paper_id) and _is_fresh(entry, freshness_days):
            digest = entry.get("response_digest", "")
            return digest, True

    raw = fetcher()
    digest = _digest_from_response(raw)
    new_entry = {
        "id": _next_entry_id(entries),
        "tool": tool,
        "method": method,
        "query_hash": qhash,
        "query_params": query_params,
        "paper_id": paper_id,
        "fetched_at": _now_iso(),
        "response_digest": digest,
        "consumed_by_findings": [],
    }
    entries.append(new_entry)
    _atomic_write(Path(ledger_path), ledger)
    return digest, False


def _digest_from_response(raw: str | dict[str, Any]) -> str:
    """Normalize a fetcher return to a ≤512-char string."""
    if isinstance(raw, str):
        s = raw
    else:
        s = json.dumps(raw, sort_keys=True, separators=(",", ":"))
    if len(s) > _RESPONSE_DIGEST_MAX:
        s = s[: _RESPONSE_DIGEST_MAX - 1] + "…"
    return s


def record_consumption(
    ledger_path: Path, entry_id: str, finding_id: str
) -> bool:
    """Append finding_id to entries[entry_id].consumed_by_findings (idempotent).

    Returns True if the ledger was modified, False if the finding was already
    recorded (or the entry was not found).
    """
    path = Path(ledger_path)
    if not path.exists():
        return False
    ledger = json.loads(path.read_text(encoding="utf-8"))
    for entry in ledger.get("entries") or []:
        if entry.get("id") == entry_id:
            consumed = entry.setdefault("consumed_by_findings", [])
            if finding_id in consumed:
                return False
            consumed.append(finding_id)
            _atomic_write(path, ledger)
            return True
    return False
