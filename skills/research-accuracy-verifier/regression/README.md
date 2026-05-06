# Verifier regression set

Pre-fork baseline + post-fork measurement bed for validating the `context: fork` migration of `research-accuracy-verifier`. The migration introduces forked subagent execution (single-fork pattern), a compact JSON return contract, and per-skill model/effort selection. This regression bed measures whether the migration delivers the promised reductions in main-context token usage and consistency in verdict assignment without regressing ground-truth recall.

## Layout

```
regression/
├── README.md
├── manifest.json              # registry of documents + tier + checks_enabled per doc
├── docs/                      # the 5 seeded-error documents under audit
│   ├── 01_grant_fabricated_doi.md
│   ├── 02_lit_review_misattributed_quote.md
│   ├── 03_manuscript_retracted_source.md
│   ├── 04_slides_numerical_inconsistency.md
│   └── 05_memo_cherry_picked.md
├── sources/                   # supporting source material (PDFs, refs) when applicable
├── ground_truth/              # per-doc seeded errors + expected verdicts
│   ├── 01_grant_fabricated_doi.json
│   ├── 02_lit_review_misattributed_quote.json
│   ├── 03_manuscript_retracted_source.json
│   ├── 04_slides_numerical_inconsistency.json
│   └── 05_memo_cherry_picked.json
├── runs/
│   ├── baseline/              # 3× pre-fork run outputs per doc (15 audits)
│   └── post_fork/             # 3× post-fork run outputs per doc (15 audits)
└── score.py                   # measurement harness — see "Metrics" below
```

## Workflow

```bash
# 1. Baseline (BEFORE applying context: fork frontmatter)
git checkout HEAD~1 -- skills/research-accuracy-verifier/SKILL.md   # or whichever ref is pre-fork
for doc in 01 02 03 04 05; do
  for run in 1 2 3; do
    # invoke verifier on docs/${doc}_*.md, capture audit_report.json
    # save under runs/baseline/${doc}/run${run}/audit_report.json
    # save final assistant return-payload under runs/baseline/${doc}/run${run}/return.json
    # save main-context-token measurement under runs/baseline/${doc}/run${run}/tokens.json
  done
done

# 2. Apply context: fork frontmatter (already done in master branch)

# 3. Post-fork
for doc in 01 02 03 04 05; do
  for run in 1 2 3; do
    # invoke verifier the same way; save under runs/post_fork/...
  done
done

# 4. Score
uv run python regression/score.py
```

## Metrics

`score.py` reads `runs/baseline/` and `runs/post_fork/`, compares against `ground_truth/`, and emits a JSON report with:

| Metric | Definition | Sprint 1 target |
|---|---|---|
| `main_context_tokens.post.median` | median of return-payload token counts | ≤ 4000 |
| `main_context_tokens.reduction` | (baseline.median − post.median) / baseline.median | ≥ 0.85 |
| `verdict_consistency_rate.post` | fraction of `(claim_id, verdict)` tuples identical across all 3 reruns of the same doc, averaged across docs | ≥ 0.92 |
| `ground_truth_recall.post` | fraction of seeded errors whose verdict matches ground-truth expectation | ≥ baseline value (non-decreasing) |
| `schema_validation_pass.post` | fraction of stage JSONs passing `validate_finding.py --strict` on first emission | ≥ 0.98 |
| `predicate_audit.post.fail_rate` | fraction of audits where any P1–P5 predicate failed | ≤ baseline value (non-decreasing) |

If post-fork verdict consistency is below 0.92, escalate to per-stage fork (Sprint 4). Otherwise, ship.

## Ground-truth schema (per-doc JSON)

`score.py` accepts two seeded-error shapes; pick whichever fits the test better.

### Simple shape — single acceptable verdict

Use when a seeded error has exactly one canonical detection path.

```jsonc
{
  "doc_id": "<id>",
  "document_type": "grant" | "manuscript" | "lit_review" | "slides" | "report" | "memo" | "other",
  "verification_tier": "1" | "2" | "3" | "custom",
  "domain": "biomedical" | "general" | "mixed",
  "flag_threshold": "conservative" | "standard" | "strict",
  "sources_available": "uploaded_files" | "bibliography_only" | "none",
  "seeded_errors": [
    {
      "error_id": "GT-<n>-<i>",
      "kind": "fabricated_doi" | "misattributed_quote" | "retracted_source"
            | "numerical_inconsistency" | "cherry_picked_support",
      "location": { "section": "...", "paragraph": N, "sentence": N },
      "claim_text": "<verbatim from doc>",
      "cited_source": { "doi": "...", "pmid": "...", "title": "..." },
      "expected_verdict": "<one of CONTRACTS.md verdicts OR style verdict>",
      "expected_severity": "CRITICAL" | "MAJOR" | "MINOR" | "INFORMATIONAL",
      "ground_truth_source": "<URL/explanation that establishes truth>"
    }
  ]
}
```

Recall match: `score.py` counts the seeded error as caught if any finding (in either `findings[]` or `style_findings[]`) has the matching verdict (and severity, if specified).

### Rich shape — multiple acceptable detection paths

Use when a seeded error can be legitimately caught via more than one path (e.g., a numerical inconsistency surfaceable by Stage 7 main-pipeline OR by `prose_quality_audit`; or a fabricated-DOI catch where UNSUPPORTED is preferred but UNVERIFIED-with-reason or METADATA_MISMATCH would also be valid).

```jsonc
{
  "doc_id": "<id>",
  /* same top-level fields as simple shape */
  "seeded_errors": [
    {
      "error_id": "GT-<n>-<i>",
      "kind": "...",
      "location": { /* ... */ },
      "claim_text": "...",
      "expected_findings_any_of": [
        {
          "stage": 7,                               /* main-pipeline alternative */
          "verdict": "CONTRADICTED",
          "severity": "CRITICAL",
          "severity_rationale": "..."
        },
        {
          "pipeline": "prose_quality_audit",         /* style-pipeline alternative */
          "style_verdict": "STYLE_NUMERICAL_INCONSISTENCY",
          "rule_id": "Q5",
          "severity": "CRITICAL",
          "severity_rationale": "..."
        }
      ],
      "ground_truth_source": "...",
      "notes": { "preferred_verdict": "...", "rationale_for_breadth": "..." }
    }
  ]
}
```

Recall match: a seeded error is considered caught if **any one** entry in `expected_findings_any_of` matches a real finding. An entry with a `verdict` field is matched against `findings[]`; an entry with a `style_verdict` field is matched against `style_findings[]` (with optional `rule_id` filter).

### Optional documentary fields

These are read by humans, not enforced by `score.py`:

- `intake_notes` — describes how the audit was set up (e.g., `sources_available: none` rationale)
- `uncited_claims_note` — flags places where Stage 4 (uncited) may emit non-seeded findings; informational only
- `measurement_notes` — explains what counts as a recall hit and why
- `notes.preferred_verdict`, `notes.rationale_for_breadth` — context on why multiple verdicts are accepted

## Status

| Doc | Seeded error | Status | Notes |
|---|---|---|---|
| 01 grant | fabricated DOI (`10.99999/regression.demo.fake.001`) | authored | Self-contained — DOI prefix `10.99999/` is unallocated, guaranteed 404 from Crossref/PubMed/scite. No real-world refs. |
| 02 lit_review | misattributed quote | deferred | Needs real published quote from Paper A intentionally attributed to Paper B; both must be retrievable for Stage 5 quote regex. Defer until Scite/Crossref MCPs available to verify candidate pairs. |
| 03 manuscript | retracted source | deferred | Needs real retracted paper with Scite editorialNotice as ground truth. Defer until Scite MCP available to verify retraction status. |
| 04 slides | numerical inconsistency × 2 | authored | Self-contained — sample-size (n=120 vs n=132) and p-value (p<0.001 vs p<0.01) inconsistencies internal to the document. No external refs. |
| 05 memo | cherry-picked support (Scite USI < 0.4) | deferred | Needs real paper with Scite USI ratio < 0.4. Defer until Scite MCP available to look up candidate USIs. |

**Sprint 1 measurement bed status:** 2 of 5 docs authored. `score.py` filters by `manifest.documents[].content_status == "authored"` — deferred docs do not contribute to metrics. Sprint 1 ship decision is computed from Docs 01 and 04 alone; Docs 02/03/05 will be added in a follow-on once MCP verification is available, at which point thresholds may need adjustment for the larger N.

`score.py` is exercised by a synthetic smoke test under `/tmp/score_smoketest/` (not committed) and verified to: (a) read `tokens.json` for main-context-token measurement, (b) accept both `findings[]` and `style_findings[]` for ground-truth recall, (c) score the rich `expected_findings_any_of` and the simple `expected_verdict` ground-truth shapes, (d) compute verdict-consistency tuples across runs, (e) emit non-zero exit and a `BLOCKED` ship decision when any threshold fails.
