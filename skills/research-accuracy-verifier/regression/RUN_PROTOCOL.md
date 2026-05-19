# Regression run protocol

The contract for executing a single regression run end-to-end. The
orchestrator (Claude Code agent, shell loop, or human) follows these
steps for each `(doc_id, arm, run_idx)` triple in the run plan. After
all runs in the plan complete, the orchestrator invokes `score.py` to
aggregate metrics across runs.

## Per-run steps

### 1. Prepare the run dir

```
uv run --script regression/prepare_run.py \
    --doc-id <doc_id> --arm <baseline|post_fork> --run-idx <N>
```

Reads `manifest.json`, writes `regression/runs/{arm}/{doc_id}/run{N}/intake.json`,
prints the intake path, the run dir, the canonical audit slug
(= `doc_id`), and the doc / ground-truth paths to stdout. See the script's
docstring for the run-dir layout it expects.

### 2. Clear the audit slug from the prior run (sequential reuse)

The verifier writes artifacts to `research/audits/<slug>/`. For sequential
runs of the same `(doc_id, arm)` the slug is reused; clear before each
fresh run so Stage 0 resume-detection does not accidentally pick up
prior-run state:

```
rm -rf research/audits/<audit_slug>/
```

Parallel runs across distinct `(doc_id, arm)` pairs use distinct slugs
naturally — no clearing needed between them, only within a single slot.

### 3. Invoke the verifier

Route to the `research-accuracy-verifier` skill with the prepared intake.
The skill runs in a forked subagent (`context: fork`); it reads:

- the document at `manifest.documents[].doc_path` (resolved relative to
  the verifier skill root), wrapped per SKILL.md §Required input wrappers
- the intake at `regression/runs/{arm}/{doc_id}/run{N}/intake.json`

and writes its artifacts to `research/audits/<audit_slug>/`. The fork
returns a compact JSON summary (~800 tokens) per SKILL.md §Fork-return
contract.

### 4. Capture artifacts into the run dir

After the fork returns, copy the canonical artifact set into the run
dir so `score.py` and the new `artifact_coverage` / `r_predicate_audit`
columns can read them from there:

```
cp research/audits/<audit_slug>/audit_report.json    regression/runs/{arm}/{doc_id}/run{N}/
cp research/audits/<audit_slug>/document_inventory.json \
   research/audits/<audit_slug>/reference_map.json \
   research/audits/<audit_slug>/resolved_sources.json \
   research/audits/<audit_slug>/external_evidence.json \
   regression/runs/{arm}/{doc_id}/run{N}/ 2>/dev/null || true
```

The `|| true` tolerates absent sidecars for baseline runs — Stage 6
fallback may not emit `external_evidence.json` if no ledger-routed
probes ran. `score.py` already handles missing sidecars gracefully
(presence flags + `None` hit rate).

### 5. Persist the fork return + token counts

Write two more files into the run dir. Filenames + shapes must match
what `score.py` reads (see `score.py` lines ~258–263):

- `return.json` — the ~800-token JSON the fork returned to the caller,
  verbatim. `score.py` falls back to approximating tokens from this
  file when `tokens.json` is absent.
- `tokens.json` — a single object `{"main_context_tokens": N}` where
  `N` is the total tokens consumed by the fork (typically
  `input_tokens + output_tokens` from the spawned-agent usage block).
  Optional — omit the file entirely when no real count is available
  rather than writing placeholder zeros or nulls; `score.py` handles
  absent files via the `return.json` approximation fallback.

## Plan execution

For the 12-run smaller bed (docs 06 + 07, 3 baseline + 3 post_fork
each), the orchestrator iterates this Cartesian product:

```
for doc_id in (06_lit_review_cited_paper_numerical,
               07_lit_review_real_paper_numerical):
    for arm in (baseline, post_fork):
        for run_idx in (1, 2, 3):
            run_one(doc_id, arm, run_idx)
```

A serial orchestrator runs 12 invocations sequentially (~2 hr wall
clock). A 4-way parallel orchestrator runs one slot per `(doc_id, arm)`
pair, each slot internally sequential (~30–45 min wall clock,
~$6 in API).

## Smoke-test first

Before committing to all 12 runs, execute a single
`(06_lit_review_cited_paper_numerical, post_fork, 1)` end-to-end and
spot-check:

- `runs/post_fork/06_*/run1/audit_report.json` validates (run
  `uv run --script scripts/validate_audit_report.py` against it).
- All 4 pinned sidecars present.
- `fork_return.json` shape matches SKILL.md §Fork-return contract.
- `tokens.json` populated.
- `extract_artifact_coverage(run_dir)` from `score.py` returns the
  expected `{*_present: true, external_evidence_entries: > 0,
  ledger_hit_rate: float}`.

If any of those fail, fix the harness before spending the remaining
11-run budget.

## Score + analyze

After all 12 runs land:

```
uv run --script regression/score.py
```

Produces aggregate metrics across both arms — the new
`artifact_coverage_rate`, `ledger_hit_rate_{median,max,min}`, and
`r_predicate_pass_rate` columns wired in the post-Phase-4 follow-ups
(commit `1f5c7bb`) plus the pre-existing token-delta, verdict-consistency,
ground-truth-recall, schema-pass, and predicate-fail metrics.

The post-vs-baseline deltas answer the open questions queued for
Sprint 4 measurement: whether the cooperation contract delivers token
savings in practice (vs. only delivering evidence-pinning quality),
and whether the dual-read pattern (Stage 6 reading both `stats.json`
and the cited paper's full text) is empirically defensible.
