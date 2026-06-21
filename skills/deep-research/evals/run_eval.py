# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""LLM-as-judge evaluation runner for the deep-research skill (Phase 0 eval bed).

Judges the END STATE of a deep-research run — the final markdown report plus its
evidence-pinned sidecars — against the 5-dimension rubric in ``rubric.md``. The
judge model is invoked by shelling out to the Claude Code CLI in headless mode
(``claude -p --output-format json``); the runner has NO third-party dependencies
(stdlib only), consistent with this repo's PEP-723 self-bootstrapping scripts.

Offline modes (no model, no network) — used by the test suite:
  --dry-run            assemble + print the judge prompt, then exit 0
  --mock-judge PATH    read a canned verdict JSON instead of calling the model

See ``README.md`` and the plan at
``~/.claude/plans/i-am-interested-in-calm-brook.md`` for context.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_RUBRIC = HERE / "rubric.md"
DEFAULT_OUT = HERE / "results"

TEMPLATE_START = "<!-- JUDGE_PROMPT_TEMPLATE_START -->"
TEMPLATE_END = "<!-- JUDGE_PROMPT_TEMPLATE_END -->"

# Placeholder token -> the sidecar/field it is filled from.
PLACEHOLDERS = (
    "research_question",
    "mode",
    "report",
    "sources_json",
    "grading_json",
    "synthesis_json",
    "advocate_json",
)

MISSING = "(not provided in this mode)"
FENCE_LINES = {"```", "```text", "```markdown", "```json"}


def extract_template(rubric_path: Path) -> str:
    """Pull the judge-prompt template from between the sentinel comments."""
    text = rubric_path.read_text(encoding="utf-8")
    if TEMPLATE_START not in text or TEMPLATE_END not in text:
        raise SystemExit(
            f"rubric file {rubric_path} is missing the "
            f"{TEMPLATE_START} / {TEMPLATE_END} sentinels"
        )
    body = text.split(TEMPLATE_START, 1)[1].split(TEMPLATE_END, 1)[0]
    lines = [ln for ln in body.splitlines() if ln.strip() not in FENCE_LINES]
    return "\n".join(lines).strip()


def read_required(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"--report file not found: {path}")
    return p.read_text(encoding="utf-8")


def read_optional(path: str | None) -> str:
    if not path:
        return MISSING
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"input file not found: {path}")
    return p.read_text(encoding="utf-8")


def build_fields(args: argparse.Namespace) -> dict[str, str]:
    return {
        "research_question": args.query or MISSING,
        "mode": args.mode or MISSING,
        "report": read_required(args.report),
        "sources_json": read_optional(args.sources),
        "grading_json": read_optional(args.grading),
        "synthesis_json": read_optional(args.synthesis),
        "advocate_json": read_optional(args.advocate),
    }


def assemble_prompt(template: str, fields: dict[str, str]) -> str:
    prompt = template
    for key in PLACEHOLDERS:
        prompt = prompt.replace("{{" + key + "}}", fields.get(key, MISSING))
    return prompt


def run_judge(prompt: str, model: str) -> str:
    """Invoke the Claude Code CLI headlessly; return the model's raw text."""
    cmd = ["claude", "-p", "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    try:
        proc = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True, timeout=600
        )
    except FileNotFoundError as exc:
        raise SystemExit(
            "claude CLI not found on PATH. Use --dry-run or --mock-judge for "
            "offline runs, or install the Claude Code CLI for live judging."
        ) from exc
    if proc.returncode != 0:
        raise SystemExit(
            f"claude CLI exited {proc.returncode}: {proc.stderr.strip()[:500]}"
        )
    # --output-format json wraps the model output: {"result": "...", ...}
    try:
        return json.loads(proc.stdout).get("result", proc.stdout)
    except json.JSONDecodeError:
        return proc.stdout


def parse_verdict(raw: str) -> dict:
    """Extract the strict-JSON verdict object from the judge's raw output."""
    raw = raw.strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end <= start:
        raise SystemExit(f"no JSON object found in judge output:\n{raw[:500]}")
    return json.loads(raw[start : end + 1])


def write_results(
    out_dir: str,
    query_id: str | None,
    mode: str | None,
    model: str,
    timestamp: str,
    inputs: dict,
    verdict: dict,
) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    record = {
        "query_id": query_id,
        "mode": mode,
        "model": model,
        "timestamp": timestamp,
        "inputs": inputs,
        "scores": verdict.get("scores"),
        "overall": verdict.get("overall"),
        "pass": verdict.get("pass"),
        "rationale": verdict.get("rationale"),
    }
    slug = query_id or Path(inputs["report"]).stem
    out_path = out / f"{slug}.json"
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return out_path


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="LLM-as-judge eval runner for deep-research (end-state)."
    )
    ap.add_argument(
        "--report", required=True, help="Path to the deep-research markdown report"
    )
    ap.add_argument("--sources", help="Path to sources.json sidecar")
    ap.add_argument("--grading", help="Path to grading.json sidecar")
    ap.add_argument("--synthesis", help="Path to synthesis.json sidecar")
    ap.add_argument("--advocate", help="Path to advocate.json sidecar")
    ap.add_argument(
        "--query",
        "--research-question",
        dest="query",
        help="The research question being evaluated",
    )
    ap.add_argument("--mode", help="deep-research mode (full, quick, ...)")
    ap.add_argument(
        "--query-id",
        dest="query_id",
        help="Stable golden-set id (names the results file)",
    )
    ap.add_argument(
        "--rubric",
        default=str(DEFAULT_RUBRIC),
        help="Path to rubric.md (judge template source)",
    )
    ap.add_argument(
        "--out", default=str(DEFAULT_OUT), help="Directory for the results JSON"
    )
    ap.add_argument(
        "--model", default="", help="Judge model id passed to the claude CLI"
    )
    ap.add_argument(
        "--timestamp", default="", help="ISO-8601 stamp for results (default: now, UTC)"
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Assemble and print the judge prompt, then exit (no model call)",
    )
    ap.add_argument(
        "--mock-judge",
        dest="mock_judge",
        help="Path to a canned verdict JSON (offline; skips the model call)",
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    template = extract_template(Path(args.rubric))
    fields = build_fields(args)
    prompt = assemble_prompt(template, fields)

    if args.dry_run:
        sys.stdout.write(prompt + "\n")
        return 0

    if args.mock_judge:
        verdict = json.loads(Path(args.mock_judge).read_text(encoding="utf-8"))
    else:
        verdict = parse_verdict(run_judge(prompt, args.model))

    timestamp = args.timestamp or datetime.now(timezone.utc).isoformat()
    inputs = {
        "report": args.report,
        "sources": args.sources,
        "grading": args.grading,
        "synthesis": args.synthesis,
        "advocate": args.advocate,
        "rubric": args.rubric,
    }
    out_path = write_results(
        args.out,
        args.query_id,
        args.mode,
        args.model or "(unset)",
        timestamp,
        inputs,
        verdict,
    )
    sys.stdout.write(f"wrote {out_path}\n")
    sys.stdout.write(
        json.dumps({"overall": verdict.get("overall"), "pass": verdict.get("pass")})
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
