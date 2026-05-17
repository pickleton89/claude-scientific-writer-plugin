# Stage 5 — Quotation verification

**Purpose:** Direct quotes require exact-string verification. Paraphrase-presented-as-verbatim is a distinct severity from a missing or contradicted quote.

**Predicate enforced:** P4 (`QUOTE_*` verdicts restricted to `claim_type == "direct_quote"` — see [`../predicates.md`](../predicates.md)).

## Procedure

Delegate to `scripts/verify_exact_quote.py` (capability key: `verification.exact_quote`).

- **Source provided** → exact-string + whitespace-normalized search in source via the script.
- **No source, biomedical context** (and `paperclip --version` succeeds) → corpus-wide exact-phrase grep over full text: `paperclip grep -F "<exact passage>" /papers/`. Capability key: `verification.exact_quote` (primary). The CLI returns paper IDs and per-paper match counts with file paths and line numbers (`/papers/<id>/sections/<file>:L<n>`). Sandbox blocks `for`/`while`/`xargs` — use multiple tool calls instead of loops.
- **No source, Paperclip unavailable or non-biomedical** → call `mcp__exa__web_search_exa` with the quoted phrase as a natural-language query (`numResults: 5`); for each promising hit, call `mcp__exa__web_fetch_exa` on the URL to retrieve clean markdown and grep for the exact phrase. `WebSearch` is the deeper fallback when Exa returns empty (regional restriction, rate limit, or query truly off-corpus). Capability key: `verification.semantic_web_search` (Exa primary) / `verification.exact_quote` (web fallback). Web-discovered quote rescues MUST still record the resolved URL + `fetched_at` in the finding's `evidence[]`; the citable-web-domain whitelist applies (W3b context-only — a quote located only on a journal news desk cannot itself become the citation, but it can guide the LLM to the underlying primary source).
- **Rescue path for `QUOTE_FABRICATED`**: when `verify_exact_quote.py` returns `QUOTE_FABRICATED` (quote not found in the *claimed* source), run `paperclip grep -F "<exact passage>" /papers/` before finalizing the finding. If the quote is real but in a different paper, the verdict **stays `QUOTE_FABRICATED`** (the original cite-claim pair is still wrong) — but the finding's `evidence[]` MUST record the discovered true source's citation URL (`https://citations.gxl.ai/papers/<doc_id>#L<n1>-L<n2>`), and the `recommended_action` MUST be "re-attribute the quote to <discovered source>" rather than "remove the quote." This preserves the canonical verdict-origin partition (Stage 5 emits only `QUOTE_*` verdicts) while distinguishing recoverable misattribution from genuinely fabricated text in the remediation guidance.
- Verify attribution (right person, right context).
- Verify date / venue if specified.

## Verdict assignments (canonical, only valid when `claim_type == "direct_quote"`)

| Condition | Verdict |
|---|---|
| Exact match | `QUOTE_VERIFIED` |
| Text differs from source | `QUOTE_PARAPHRASED` |
| No matching text in claimed source | `QUOTE_FABRICATED` (when corpus rescue locates the quote in a different paper, verdict is unchanged but `evidence[]` records the discovered true source and `recommended_action` switches to re-attribution) |

See [`../CONTRACTS.md`](../CONTRACTS.md) for canonical verdict definitions.

## On stage completion

Persist via `checkpoint.py write --stage 5`.

**Artifact:** `research/audits/<slug>/05_quotes.json`.
