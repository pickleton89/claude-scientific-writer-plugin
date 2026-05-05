#!/usr/bin/env python3
"""
Phase 2 search audit for the deep-research pipeline.

Hard gate that compares the executed Search Log against the frozen
:class:`SearchContract`. Wraps the previously-orphaned
:func:`exit_criteria._check_all_databases_searched` so the Bibliography agent
has a runtime check before requesting Checkpoint 2.

Usage:
    python search_audit.py <input.json>
    JSON: {
      "contract": <SearchContract.to_dict() output>,
      "searched_databases": ["PubMed", "Consensus", ...]
    }

Or programmatically::

    from search_audit import audit_search

    result = audit_search(contract_dict, ["PubMed", "Consensus", "bioRxiv"])
    if not result.passed:
        ...

Exit code: 0 on pass, 1 on fail (suitable for shell-level gating).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from exit_criteria import PhaseGateResult, audit_phase_2_search


def audit_search(
    contract: dict,
    searched_databases: list[str],
) -> PhaseGateResult:
    """
    Audit Phase 2 search execution against a frozen Search Contract.

    Args:
        contract: A :class:`SearchContract` serialised via ``to_dict()``.
            Must have the ``frozen: True`` flag set — auditing an unfrozen
            contract is a programming error and raises ``ValueError``.
        searched_databases: Names of databases that were actually called
            during Phase 2 — typically the ``Database`` column of the Search
            Log table.

    Returns:
        :class:`PhaseGateResult`. ``passed=True`` means every required
        database in the contract appears in ``searched_databases``.
    """
    if not contract.get("frozen"):
        raise ValueError(
            "Cannot audit an unfrozen Search Contract. Call SearchContract.freeze() "
            "after user approval at Checkpoint 1 before invoking the audit."
        )

    required = [db["name"] for db in contract.get("required_databases", [])]
    return audit_phase_2_search(
        required_databases=required,
        searched_databases=list(searched_databases),
    )


def format_audit_for_user(result: PhaseGateResult) -> str:
    """Render a PhaseGateResult as readable markdown for the agent's report."""
    lines: list[str] = []
    verdict = "PASSED" if result.passed else "FAILED"
    lines.append(f"# Search Audit — {verdict}")
    lines.append("")
    lines.append(f"**Phase:** {result.phase}")
    lines.append(f"**Required databases:** {', '.join(result.required_databases) or '—'}")
    lines.append(f"**Searched databases:** {', '.join(result.searched_databases) or '—'}")
    if result.missing_databases:
        lines.append(
            f"**Missing:** {', '.join(result.missing_databases)} — "
            "Bibliography agent MUST loop back and call these channels in a "
            "parallel batch before requesting Checkpoint 2."
        )
    lines.append(f"**Message:** {result.message}")
    return "\n".join(lines)


def main() -> None:
    """CLI entry point. Reads JSON, prints markdown report, exits 0/1."""
    if len(sys.argv) < 2:
        print("Usage: search_audit.py <input.json | json_string>")
        print(
            '  JSON: {"contract": {...}, "searched_databases": ["PubMed", ...]}'
        )
        sys.exit(2)

    arg = sys.argv[1]
    if arg.startswith("{"):
        data = json.loads(arg)
    else:
        with open(arg) as f:
            data = json.load(f)

    contract = data.get("contract", {})
    searched = data.get("searched_databases", [])

    result = audit_search(contract, searched)
    print(format_audit_for_user(result))
    print()
    print(json.dumps(result.to_dict(), indent=2))

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
