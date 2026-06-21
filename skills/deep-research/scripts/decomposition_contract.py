#!/usr/bin/env python3
"""
Decomposition contract builder for the deep-research pipeline.

Produces a frozen Decomposition Contract at Phase 1 (Scoping), presented at
Checkpoint 1 alongside the Output + Search contracts. It splits the research
question into bounded sub-questions, each carrying the four delegation fields
Anthropic's multi-agent research system found necessary — objective, output
format, source guidance, and an explicit boundary — so the Phase 3 fan-out does
not duplicate work or leave gaps.

The number of sub-questions (fan_out_width) and the per-subagent tool-call budget
come from ``thresholds.COMPLEXITY_SCALING`` keyed on the query complexity
(``complexity_classifier.py``). Width is capped to 1 outside
``thresholds.FANOUT_MODES`` — quick / lit-review / fact-check plan a
decomposition but execute single-context.

Like ``search_contract.py``, the builder emits a SCAFFOLD: each sub-question's
``objective`` / ``boundary`` carry ``[FILL]`` placeholders the orchestrator
replaces with the real semantic decomposition before freezing at Checkpoint 1.

Usage:
    python decomposition_contract.py <input.json>
    JSON: {"mode": "full", "research_question": "...", "complexity": "complex",
           "topic_slug": "..."}   # complexity optional — classified if omitted

Output:
    Markdown rendering for Checkpoint 1, followed by the JSON contract
    (schema: schemas/decomposition.json; predicates D1-D3 in validate_sidecar.py).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from complexity_classifier import classify_complexity
from thresholds import ALL_MODES, FANOUT_MODES, complexity_scaling

SCHEMA_VERSION = "1.0"

# Modes that run neither a search nor a decomposition phase.
NO_DECOMPOSITION_MODES: frozenset[str] = frozenset({"socratic", "review"})


@dataclass
class SubQuestion:
    """One bounded sub-question handed to a researcher."""

    id: str
    objective: str
    output_format: str
    source_guidance: str
    boundary: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "objective": self.objective,
            "output_format": self.output_format,
            "source_guidance": self.source_guidance,
            "boundary": self.boundary,
        }


@dataclass
class DecompositionContract:
    """Frozen Phase-1 decomposition contract."""

    mode: str
    research_question: str
    complexity: str
    topic_slug: str
    fan_out_width: int
    tool_calls_min: int
    tool_calls_max: int
    results_cap_per_channel: int
    fanout_eligible: bool
    sub_questions: list[SubQuestion] = field(default_factory=list)
    frozen: bool = False
    frozen_at: str = ""
    warnings: list[str] = field(default_factory=list)

    def freeze(self) -> None:
        """Lock the contract after user approval at Checkpoint 1."""
        if self.frozen:
            raise RuntimeError("Contract is already frozen")
        self.frozen = True
        self.frozen_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """Convert to the schemas/decomposition.json shape (Draft-07)."""
        return {
            "schema_version": SCHEMA_VERSION,
            "metadata": {
                "frozen_at": self.frozen_at,
                "mode": self.mode,
                "topic_slug": self.topic_slug,
                "complexity": self.complexity,
                "rq": self.research_question or None,
            },
            "scaling": {
                "fan_out_width": self.fan_out_width,
                "tool_calls_min": self.tool_calls_min,
                "tool_calls_max": self.tool_calls_max,
                "results_cap_per_channel": self.results_cap_per_channel,
                "fanout_eligible": self.fanout_eligible,
            },
            "sub_questions": [sq.to_dict() for sq in self.sub_questions],
        }


def _scaffold_sub_questions(
    width: int, research_question: str, fanout_eligible: bool
) -> list[SubQuestion]:
    """Build ``width`` sub-question scaffolds for the orchestrator to fill in."""
    rq = research_question.strip() or "(research question not specified)"

    if width == 1:
        mode_note = (
            "single-context (this mode does not fan out)"
            if not fanout_eligible
            else "single researcher (complexity did not warrant fan-out)"
        )
        return [
            SubQuestion(
                id="SQ1",
                objective=rq,
                output_format=(
                    "Annotated, deduplicated sources with a 2-3 sentence finding "
                    "per included paper and T1-T4 evidence labels."
                ),
                source_guidance=(
                    "Use the frozen Search Contract's required databases; favor "
                    "primary sources over reviews."
                ),
                boundary=f"Cover the full research question — {mode_note}.",
            )
        ]

    subs: list[SubQuestion] = []
    for i in range(1, width + 1):
        subs.append(
            SubQuestion(
                id=f"SQ{i}",
                objective=(
                    f"[FILL] Facet {i} of {width}: a specific, bounded slice of "
                    f"'{rq}' that no sibling sub-question covers."
                ),
                output_format=(
                    "Annotated sources for this facet + a 2-3 sentence synthesized "
                    "finding; T1-T4 labels; flag any contradictions."
                ),
                source_guidance=(
                    "Per the frozen Search Contract; note any facet-specific "
                    "channel (PubTator3 for named entities, WebSemantic for "
                    "regulatory/grey-lit)."
                ),
                boundary=(
                    f"[FILL] State exactly what facet {i} excludes so it does not "
                    "overlap sibling sub-questions."
                ),
            )
        )
    return subs


def build_decomposition_contract(
    mode: str,
    research_question: str = "",
    complexity: str | None = None,
    topic_slug: str = "topic",
    fan_out_width: int | None = None,
) -> DecompositionContract:
    """
    Build a Decomposition Contract for the given mode + RQ.

    Returned UNFROZEN — call :meth:`DecompositionContract.freeze` after the user
    approves at Checkpoint 1 (which stamps ``frozen_at`` so the JSON validates).

    Args:
        mode: One of ``ALL_MODES`` (excluding socratic/review, which do not
            decompose — those raise ValueError).
        research_question: The RQ text (seeds sub-question objectives + drives
            complexity classification when ``complexity`` is omitted).
        complexity: ``simple`` / ``comparative`` / ``complex``. Classified from
            the RQ when ``None``.
        topic_slug: Topic slug for the metadata (matches the report filename).
        fan_out_width: Override the default width from COMPLEXITY_SCALING.
            Clamped to ``[1, fan_out_max]`` and capped to 1 outside FANOUT_MODES.

    Raises:
        ValueError: For unknown modes or modes without a decomposition phase.
    """
    if mode not in ALL_MODES:
        raise ValueError(
            f"Unknown mode '{mode}'. Must be one of: {', '.join(ALL_MODES)}"
        )
    if mode in NO_DECOMPOSITION_MODES:
        raise ValueError(
            f"Mode '{mode}' has no search/decomposition phase — no contract to build."
        )

    notes: list[str] = []
    if complexity is None:
        classification = classify_complexity(research_question, mode)
        complexity = classification.level
        notes.extend(classification.notes)

    scaling = complexity_scaling(complexity)
    fanout_eligible = mode in FANOUT_MODES

    width = fan_out_width if fan_out_width is not None else scaling["fan_out_default"]
    # Clamp to the complexity's upper bound, floor at 1.
    width = max(1, min(width, scaling["fan_out_max"]))
    # Cap to single-context outside fan-out-eligible modes.
    if not fanout_eligible and width > 1:
        notes.append(
            f"Mode '{mode}' is not fan-out-eligible — width capped from {width} to 1 "
            "(plans a decomposition but executes single-context)."
        )
        width = 1

    contract = DecompositionContract(
        mode=mode,
        research_question=research_question,
        complexity=complexity,
        topic_slug=topic_slug,
        fan_out_width=width,
        tool_calls_min=scaling["tool_calls_min"],
        tool_calls_max=scaling["tool_calls_max"],
        results_cap_per_channel=scaling["results_cap"],
        fanout_eligible=fanout_eligible,
        sub_questions=_scaffold_sub_questions(
            width, research_question, fanout_eligible
        ),
        warnings=notes,
    )
    return contract


def format_contract_for_user(contract: DecompositionContract) -> str:
    """Render the contract as readable markdown for Checkpoint 1 review."""
    lines: list[str] = []
    lines.append("# Decomposition Contract")
    lines.append("")
    lines.append(f"**Mode:** {contract.mode}")
    lines.append(f"**Complexity:** {contract.complexity}")
    lines.append(
        f"**Research question:** {contract.research_question or '(not specified)'}"
    )
    lines.append(
        f"**Frozen:** {'yes — ' + contract.frozen_at if contract.frozen else 'no'}"
    )
    lines.append("")
    lines.append(
        f"**Fan-out:** {contract.fan_out_width} sub-question(s) · "
        f"{'PARALLEL subagents (Phase 3)' if contract.fanout_eligible and contract.fan_out_width > 1 else 'single-context'} · "
        f"{contract.tool_calls_min}-{contract.tool_calls_max} tool calls each · "
        f"≤{contract.results_cap_per_channel} results/channel "
        f"(per `thresholds.COMPLEXITY_SCALING['{contract.complexity}']`)."
    )
    lines.append("")
    lines.append(
        "_Each sub-question carries four delegation fields — objective, output "
        "format, source guidance, and an explicit boundary — to prevent "
        "duplicated work and coverage gaps. Replace any `[FILL]` placeholders "
        "with the real decomposition before freezing._"
    )
    lines.append("")

    lines.append("## Sub-questions")
    lines.append("")
    for sq in contract.sub_questions:
        lines.append(f"### {sq.id}")
        lines.append(f"- **Objective:** {sq.objective}")
        lines.append(f"- **Output format:** {sq.output_format}")
        lines.append(f"- **Source guidance:** {sq.source_guidance}")
        lines.append(f"- **Boundary:** {sq.boundary}")
        lines.append("")

    if contract.warnings:
        lines.append("## Notes")
        lines.append("")
        for w in contract.warnings:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """CLI entry point. Reads JSON, prints markdown + JSON contract."""
    if len(sys.argv) < 2:
        print("Usage: decomposition_contract.py <input.json | json_string>")
        print(
            '  JSON: {"mode": "full", "research_question": "...", '
            '"complexity": "complex", "topic_slug": "..."}'
        )
        sys.exit(1)

    arg = sys.argv[1]
    data = json.loads(arg) if arg.startswith("{") else json.load(open(arg))

    contract = build_decomposition_contract(
        mode=data.get("mode", "full"),
        research_question=data.get("research_question", ""),
        complexity=data.get("complexity"),
        topic_slug=data.get("topic_slug", "topic"),
        fan_out_width=data.get("fan_out_width"),
    )

    print(format_contract_for_user(contract))
    print("\n---\n")
    print(json.dumps(contract.to_dict(), indent=2))


if __name__ == "__main__":
    main()
