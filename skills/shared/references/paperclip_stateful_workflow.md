# Paperclip Stateful Workflow

Paperclip's `s_xxxxxxxx` (search) and `m_xxxxxxxx` (map) IDs persist server-side
within a single machine session. Downstream stages can consume them via
`--from <id>` instead of re-querying — this is the "tunnel back into earlier
result sets" pattern described in the gxl.ai agentic-preference write-up.

This guide documents the conventions used across `deep-research`,
`research-accuracy-verifier`, and `research-paper-summarizer` so handles are
re-used rather than re-derived.

## ID lifecycle

| ID prefix | Producer | Consumers | Scope |
|-----------|---------|-----------|-------|
| `s_xxxxxxxx` | `paperclip search` | `paperclip results <id>`, `paperclip map --from <id>` | session-local, single machine |
| `m_xxxxxxxx` | `paperclip map --from <s_id>` | `paperclip results <id>`, `paperclip reduce --from <id>` | session-local, single machine |

IDs are **not** globally reproducible audit identifiers. They are local trace
handles only. For durable per-citation reproducibility, always pair an `s_id` /
`m_id` reference with a citation URL of the form
`https://citations.gxl.ai/papers/<doc_id>#L<n1>-L<n2>` in the finding's
`evidence[]` or the bibliography entry.

## Persisting handles to /.gxl/

The `/.gxl/` virtual filesystem maps to a `.gxl/` directory in the user's
current working directory (host-visible, not a sandbox). Use it to hand off
state between stages without keeping the IDs in chat context.

Recommended file naming (one per topic_slug):

```
/.gxl/<topic_slug>_paperclip_state.json
```

Schema (informal; load and merge per stage):

```json
{
  "topic_slug": "egfr_resistance_nsclc",
  "created_at": "2026-05-22T10:19:00Z",
  "search_handles": [
    {
      "stage": "bibliography",
      "query": "EGFR resistance NSCLC",
      "source_filter": null,
      "limit": 50,
      "s_id": "s_a3f1b210",
      "result_count": 47,
      "created_at": "2026-05-22T10:21:00Z"
    }
  ],
  "map_handles": [
    {
      "stage": "bibliography_synthesis",
      "from_s_id": "s_a3f1b210",
      "question": "What resistance mechanism was reported and what fraction of patients showed it?",
      "m_id": "m_ec2c9cc9",
      "paper_count": 8,
      "created_at": "2026-05-22T10:24:00Z"
    }
  ]
}
```

## Producer pattern (bibliography agent)

When `paperclip search` runs as part of the frozen Search Contract, after the
batched parallel call:

```
paperclip search "EGFR resistance NSCLC" -n 50    # → s_a3f1b210
# Persist:
jq '.search_handles += [{"stage":"bibliography","query":"...","s_id":"s_a3f1b210",...}]' \
  /.gxl/egfr_resistance_nsclc_paperclip_state.json
```

If the search returns ≥5 papers eligible for synthesis, follow with:

```
paperclip map --from s_a3f1b210 "What resistance mechanism was reported?"  # → m_ec2c9cc9
paperclip reduce --from m_ec2c9cc9 --strategy themes
```

The `m_id` is also persisted. Reduce strategies:

| Strategy | Use when |
|----------|----------|
| `summarize` | Need a paragraph-level overview across the map set |
| `table` | Comparing methods/results across papers (compiler emits a comparison table) |
| `themes` | Surfacing common motifs or sub-claims that span multiple papers |
| `consensus` | "Where do papers agree / disagree on X?" — produces a stance breakdown |
| `bullet_points` | Quick scan, lower-cost than `summarize` for long sets |
| `extract` | Pulling specific fields (delivery vector, transfection rate, ...) when each paper's `map` answer is already field-shaped |

## Consumer pattern (verifier Stage 3)

When the verifier's Stage 3 needs to align a claim against a paper that
appeared in the bibliography's earlier `s_id`:

```
# Load the bibliography's state
cat /.gxl/egfr_resistance_nsclc_paperclip_state.json | jq '.search_handles[-1].s_id'
# → "s_a3f1b210"

# Re-inspect the saved set instead of re-querying
paperclip results s_a3f1b210 | grep -i "EGFR"

# If the paper of interest is in the set, skip straight to the paper:
paperclip cat /papers/<id>/sections/discussion
```

This avoids the cost of a fresh `paperclip search` for every Stage 3 alignment
check.

## Inventory commands

`paperclip results --list` lists every `s_id` / `m_id` retained in the current
machine session. Use it when the JSON state file is missing or when debugging
which sessions have been opened:

```
paperclip results --list
# s_a3f1b210  search  "EGFR resistance NSCLC" -n 50         47 results
# m_ec2c9cc9  map     from s_a3f1b210 (8 papers)             8 answers
```

## Failure modes

| Failure | Symptom | Action |
|---------|---------|--------|
| Stale `s_id` after machine restart | `paperclip results s_xxx` returns "not found" | Re-run the original search; update the state file |
| `m_id` from a different `s_id` than the persisted one | `paperclip reduce --from <m_id>` answers don't match expected paper set | Run `paperclip results <m_id>` to inspect the source `s_id`; reconcile |
| `/.gxl/` directory missing | First write creates it; no special handling needed | — |
| State file collision between two topics on the same CWD | Two skills writing the same topic_slug | Include a date prefix: `2026-05-22_egfr_resistance_nsclc_paperclip_state.json` |

## When NOT to use stateful handles

- Cross-session reproducibility (e.g., re-running an audit weeks later): use
  citation URLs (`https://citations.gxl.ai/papers/<doc_id>#L<n>`) instead.
- Sharing results across machines: handles are local-only.
- Long-running pipelines that span Paperclip CLI restarts: persist citation
  URLs and DOIs; re-derive handles on each restart via `paperclip lookup doi`.

## Cross-references

- `skills/deep-research/agents/bibliography.md` — emits `s_id`/`m_id` in Step 4
- `skills/research-accuracy-verifier/SKILL.md` §Connector and tool priority — consumes handles in Stage 3/5
- `.claude/skills/paperclip/SKILL.md` — canonical CLI reference (vendor-managed)
- `skills/shared/tool-lookup.yaml` `literature.corpus_search` / `literature.corpus_grep` / `literature.corpus_metadata` / `verification.figure_content` — capability keys backed by the Paperclip CLI
