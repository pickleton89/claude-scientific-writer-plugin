# deep-research eval harness (Phase 0)

An **LLM-as-judge** regression bed for the `deep-research` skill. It scores a
finished run against a fixed rubric so later changes can be measured instead of
guessed at. This is Phase 0 of the
[multi-agent improvements plan](../../../../.claude/plans/i-am-interested-in-calm-brook.md)
— the prerequisite that gates every behavioral change after it.

Design follows Anthropic's
[multi-agent research post](https://www.anthropic.com/engineering/multi-agent-research-system):
- **One judge, one rubric** (a single judge call aligns with human judgment
  better than several specialized judges).
- **End-state evaluation** — the judge reads the final report **plus its
  evidence-pinned sidecars** (the ground truth), not the search path. Different
  valid paths reach the same goal.
- **Start small** — ~20 representative queries, not hundreds; large quality
  swings show up on a small set.

## Layout

| Path | What |
|---|---|
| `queries/golden_set.yaml` | ~20 fixed RQs across modes + domains (the regression set) |
| `rubric.md` | The 5-dimension rubric + the single judge-prompt template (between sentinel comments) |
| `run_eval.py` | Runner: assembles the prompt, calls the judge, writes scores |
| `fixtures/` | Offline report+sidecar bundles (no live MCP needed) |
| `results/` | Per-query verdict JSON (`{query_id}.json`) |

## The five dimensions

`factual_accuracy` · `citation_accuracy` · `completeness` · `source_quality` ·
`tool_efficiency` — each 0.0–1.0. **pass** = `overall >= 0.70` and no dimension
`< 0.40`. Full anchors are in [`rubric.md`](rubric.md).

## Running it

The judge model is invoked via the Claude Code CLI in headless mode
(`claude -p --output-format json`). The runner is **stdlib-only** (PEP-723, no
deps).

```bash
# Offline: assemble + print the judge prompt (no model call)
uv run python skills/deep-research/evals/run_eval.py --dry-run \
  --mode quick \
  --report   skills/deep-research/evals/fixtures/quick_kras_g12c/2026-06-21_kras-g12c-nsclc_quick_brief.md \
  --sources  skills/deep-research/evals/fixtures/quick_kras_g12c/2026-06-21_kras-g12c-nsclc_quick_sources.json \
  --grading  skills/deep-research/evals/fixtures/quick_kras_g12c/2026-06-21_kras-g12c-nsclc_quick_grading.json

# Offline: score using a canned verdict (used by the test suite)
uv run python skills/deep-research/evals/run_eval.py \
  --mock-judge skills/deep-research/evals/fixtures/quick_kras_g12c/mock_judge_verdict.json \
  --mode quick --query-id fixture-smoke \
  --report skills/deep-research/evals/fixtures/quick_kras_g12c/2026-06-21_kras-g12c-nsclc_quick_brief.md \
  --sources skills/deep-research/evals/fixtures/quick_kras_g12c/2026-06-21_kras-g12c-nsclc_quick_sources.json \
  --grading skills/deep-research/evals/fixtures/quick_kras_g12c/2026-06-21_kras-g12c-nsclc_quick_grading.json \
  --out skills/deep-research/evals/results

# Live: real judge (requires the claude CLI on PATH)
uv run python skills/deep-research/evals/run_eval.py \
  --mode full --query-id q01-full-kras-g12c-resistance \
  --query "<the RQ>" \
  --report <run report.md> --sources <...> --grading <...> \
  --synthesis <...> --advocate <...> --model claude-opus-4-8
```

## How it gates the plan

After each later phase (prompt refinements → decomposition/complexity contracts →
parallel fan-out), regenerate reports for the golden set and re-judge. Compare
per-dimension and overall scores to the Phase 0 baseline. **A phase does not ship
if it regresses the overall score.**

## Tests

`../tests/test_run_eval.py` exercises the two offline paths (`--dry-run`,
`--mock-judge`) against the fixture — run with
`uv run pytest skills/deep-research/tests/test_run_eval.py`.
