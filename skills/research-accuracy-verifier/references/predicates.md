# Validator-enforced predicates (P1–P5, P7, P8, P9, R1–R6)

Findings that violate these predicates are **rejected** by the validators in `scripts/`, forcing a Stage-8 loop-back. They are not guidelines — the validator code is the source of truth, and this document mirrors it for reading convenience. The canonical definitions live in [`CONTRACTS.md`](./CONTRACTS.md) §Hard predicates.

P1–P5, P7, and P9 are per-finding predicates enforced by [`scripts/validate_finding.py`](../scripts/validate_finding.py). P8 + R1–R6 are cross-stage / cross-artifact post-conditions enforced by [`scripts/validate_audit_report.py`](../scripts/validate_audit_report.py). **P8** is invoked transitively from `render_report.generate_report()` so audits cannot render past a P8 violation. **R1–R6** run at Stage 8 only in Phase 1 — Phase 3 adds the same transitive-from-render enforcement (see [`CONTRACTS.md`](./CONTRACTS.md) §Cross-artifact predicates).

**Enforcement modes.** P1–P9 are hard errors regardless of mode. R1–R6 follow the `ARTIFACT_ENFORCEMENT` constant in [`scripts/thresholds.py`](../scripts/thresholds.py): `"advisory"` (Phase 1 default) → R-failures emit warnings only; `"required"` (Phase 3 target) → R-failures emit errors and block rendering.

## P1 — UNVERIFIED requires reason and bars CRITICAL

`verdict == UNVERIFIED ⟹ reason ∈ Reason AND severity != CRITICAL`

- **Validator:** `validate_finding.py` `_p1_unverified_consistency`
- **Schema:** `schemas/finding.json` (`reason` enum) and `schemas/severity_matrix.values.json` (UNVERIFIED row = all INFORMATIONAL)
- **Failure mode:** finding promotes an UNVERIFIED claim to CRITICAL, or omits the `reason` field
- **Fix:** assign a specific `reason` value (`paywalled_full_text | preprint_not_indexed | api_timeout | source_not_provided | tier_does_not_cover | other`) and downgrade severity to INFORMATIONAL

## P2 — CRITICAL requires ≥2 verification_path entries

`severity == CRITICAL ⟹ len(verification_path) >= 2`

- **Validator:** `validate_finding.py` `_p2_critical_two_paths`
- **Failure mode:** a single failed lookup escalates to CRITICAL without a second independent identifier path
- **Fix:** add a second verification entry (e.g., PubMed search after Crossref lookup; OpenAlex `batch_resolve_references` after both miss) before assigning CRITICAL

## P3 — Every finding needs resolvable evidence

`len(evidence) >= 1 AND every evidence has resolvable URL/PMID/DOI`

- **Validator:** `validate_finding.py` `_p3_evidence_required`
- **Failure mode:** finding asserts a verdict without any pinnable source
- **Fix:** add an `evidence[]` entry with a URL, PMID, or DOI the user can navigate to

## P4 — QUOTE_* verdicts restricted to direct_quote claims

`verdict ∈ {QUOTE_VERIFIED, QUOTE_PARAPHRASED, QUOTE_FABRICATED} ⟺ claim_type == "direct_quote"`

- **Validator:** `validate_finding.py` `_p4_quote_claim_type`
- **Failure mode:** assigning `QUOTE_PARAPHRASED` to a paraphrased mechanistic claim (misuse of quote vocabulary)
- **Fix:** for non-quote claims, use the citation-pipeline verdicts (`OVERGENERALIZED`, `MISATTRIBUTED`, etc.); for `claim_type == "direct_quote"`, only `QUOTE_*` verdicts are allowed

## P5 — Severity is computed from the matrix

`severity == SeverityMatrix[document_type][verdict]`

- **Validator:** `validate_finding.py` `_p5_severity_matches_matrix`
- **Schema:** `schemas/severity_matrix.values.json` (canonical 10×7 table)
- **Failure mode:** LLM assigns a "feels right" severity that diverges from the matrix
- **Fix:** look up the cell in `severity_matrix.values.json`; severity is not an opinion. Apply the `flag_threshold` modifier (`conservative | standard | strict`) AFTER matrix lookup, not as a substitute for it

## P7 — Biomedical Stage-2 findings require Scite probe (or no_doi carve-out)

`domain ∈ {biomedical, mixed} AND stage == 2 AND verdict ∈ {VERIFIED, METADATA_MISMATCH, UNSUPPORTED} ⟹ EITHER verification_path[] contains a Scite probe entry (method == "scite_context" OR an entry with tool matching /scite/i) OR (web-source carve-out) verification_path[] contains an entry with method == "web_search" AND result_summary containing the literal token "no_doi"`

- **Validator:** `validate_finding.py` `_p7_scite_probe` (skipped when `domain` or `stage` is None — back-compat for ad-hoc CLI calls)
- **Failure modes:**
  - Silence: neither a Scite probe nor a `web_search`+`no_doi` carve-out entry in `verification_path[]`
  - Dedicated carve-out violation: a `web_search` entry that omits the literal token `no_doi` (so the LLM is told *why* P7 failed, distinct from generic silence)
- **Fix:** for DOI-anchored citations, log the Scite `editorialNotices` probe outcome (notices found / empty / API failure — see [`stages/stage_2_citation_existence.md`](./stages/stage_2_citation_existence.md)). For web-anchored no-DOI citations, log a `web_search` entry whose `result_summary` includes the literal token `no_doi` and a resolvable URL on the citable-web-domain whitelist
- **Related:** `skills/shared/references/citable_web_domains.md` (W1/W2/W3a/W3b tiers)

## P8 — Tier-3 cherry-picking sweep (cross-stage)

For every Stage-3 `VERIFIED` claim in a biomedical/mixed Tier-3 audit (or `custom` audit with `uncited_claims` enabled), there MUST be **either**:

- a Stage-4 cherry-picking finding (verdict `OVERGENERALIZED`, `verification_path[]` contains `method == "scite_context"`, `result_summary` contains both `cherry_picking:<claim_id>` and `USI=<value>`), **OR**
- a `header.coverage_caveats[]` entry of structured shape `cherry_picking:<claim_id>: <reason>`

- **Validator:** `validate_audit_report.py` `run_p8` (also invoked transitively by `render_report.generate_report()` — markdown cannot render past a P8 violation)
- **Failure mode:** silence — a Stage-3 VERIFIED claim with no matching finding AND no `cherry_picking:<claim_id>:` caveat
- **Fix:** complete the Stage-4 Scite tally sweep (USI = supporting / (supporting + contrasting); USI < 0.5 → emit finding) or emit a coverage caveat with the canonical reason token (e.g., `scite_doi_not_indexed`, `api_timeout`, `tally_uncontested_USI=0.83`, or `web_source_no_doi_for_scite_tally` for web-grounded VERIFIED claims). See [`stages/stage_4_uncited.md`](./stages/stage_4_uncited.md)

## P9 — Stage-2 VERIFIED requires an author/title cross-check

`stage == 2 AND verdict == VERIFIED AND verification_path[] contains a scholarly-resolution method (∈ {doi_lookup, pmid_lookup, crossref_search, pubmed_search, pmc_fetch}) ⟹ verification_path[] MUST contain a metadata_agreement entry, AND that entry MUST NOT record author_match=false or title_match=false`

- **Validator:** `validate_finding.py` `_p9_metadata_agreement` (inlined in `run_predicates`; skipped when `stage` is None — back-compat for ad-hoc CLI calls)
- **Why it exists:** a "do all DOIs resolve?" check structurally cannot catch a **wrong-but-valid DOI** — an identifier that resolves cleanly to a *real but different* paper. Resolution proves a record EXISTS; it does not prove the record IS the cited paper. The highest-value Stage-2 catch (a DOI resolving to a different author's paper) is only reachable by cross-checking the resolved record's authors + title against the citation. P9 makes that cross-check load-bearing: `VERIFIED` is unreachable without it.
- **Failure modes:**
  - **Silence:** a scholarly identifier resolved and the verdict is `VERIFIED`, but no `metadata_agreement` entry documents the author/title comparison.
  - **Contradiction:** a `metadata_agreement` entry records `author_match=false` (or `title_match=false`) yet the verdict is still `VERIFIED` — a recorded mismatch means the DOI points at a different paper, so the verdict MUST be `METADATA_MISMATCH`.
- **Fix:** after identifier resolution, compare the resolved record's authors (at least first + last) and title against the citation, and log a `verification_path[]` entry with `method == "metadata_agreement"` whose `result_summary` carries the tokens `author_match=<true|false>; title_match=<true|false>` (year/venue optional). If either is false, assign `METADATA_MISMATCH`, not `VERIFIED`.
- **Domain-independent:** unlike P7, P9 fires for `general` domain too — wrong-but-valid DOIs occur in general-science writing (Crossref / OpenAlex resolution) as readily as in biomedical.
- **Web-source exemption:** purely web-sourced findings (no scholarly-resolution method in `verification_path[]`) are exempt — there is no resolved scholarly record to compare authors/title against. Their integrity is governed by the P7 web-source carve-out (page-matches-claim framing) instead.
- **Related:** [`stages/stage_2_citation_existence.md`](./stages/stage_2_citation_existence.md) (metadata-agreement step + token convention), CONTRACTS.md §Hard predicates.

## R1 — Finding.id resolves in claim_inventory.json

When `claim_inventory.json` is supplied to the validator, every `findings[].id` MUST appear in `claim_inventory.items[].id`.

- **Validator:** `validate_audit_report.py` `_run_r1`
- **Failure mode:** a finding references a claim ID that was never registered at Stage 1 (drift between claim extraction and finding emission).
- **Fix:** ensure every finding's `id` matches a `ClaimInventoryItem.id` from Stage 1's `claim_inventory.json`. If a new claim was discovered mid-pipeline, add it to the inventory.
- **Skipped when:** `claim_inventory.json` is not supplied to the validator (advisory WARN, not failure).

## R2 — Finding.evidence[].paper_id resolves in resolved_sources.json

When `resolved_sources.json` is supplied AND `intake.sources_available != "none"`, every non-null `findings[].evidence[].paper_id` MUST resolve in `resolved_sources.sources[].paper_id`.

- **Validator:** `validate_audit_report.py` `_run_r2`
- **Failure mode:** finding cites a `paper_id` that was never registered at Stage 2 (drift between citation existence resolution and finding emission, or hallucinated DOI).
- **Fix:** verify the cited source ran through Stage 2, ensure its `paper_id` made it into `resolved_sources.json`, and that the finding uses the same key. `paper_id: null` is permitted for web-sourced (no-DOI) evidence.
- **Skipped when:** `resolved_sources.json` is not supplied, or `intake.sources_available == "none"`.

## R3 — Finding.citations[].key resolves in reference_map.json

When `reference_map.json` is supplied, every `findings[].citations[].key` MUST appear in `reference_map.citations[].key`.

- **Validator:** `validate_audit_report.py` `_run_r3`
- **Failure mode:** finding cites a citation key that was never extracted at Stage 1 (e.g., the LLM hallucinated a citation that isn't in the document).
- **Fix:** confirm the citation key was extracted by `scripts/extract_reference_map.py`. If the key appears in the document but wasn't extracted, add it manually or refine the citation regex.
- **Skipped when:** `reference_map.json` is not supplied.

## R4 — Finding.claim_verbatim matches document at location

When `document_inventory.json` AND the normalized document text are supplied, every `findings[].claim_verbatim` MUST appear as a substring of the paragraph addressed by `findings[].location` (after QuoteVerifier whitespace + unicode normalization).

- **Validator:** `validate_audit_report.py` `_run_r4` (delegates to `scripts/verify_exact_quote.py` `QuoteVerifier`)
- **Failure mode:** the finding's verbatim claim text doesn't appear in the indicated paragraph — indicates the LLM paraphrased the claim, picked the wrong paragraph, or hallucinated the location.
- **Fix:** copy the claim text verbatim from the source paragraph, or correct the `location.section / paragraph` to point at the right paragraph.
- **Skipped when:** either `document_inventory.json` or the normalized document text is not supplied.

## R6 — verification_matrix[].claim_id resolves in claim_inventory.json

When `claim_inventory.json` is supplied, every `verification_matrix[].claim_id` MUST appear in `claim_inventory.items[].id`.

- **Validator:** `validate_audit_report.py` `_run_r6`
- **Failure mode:** the matrix references a claim ID that was never registered (drift between Stage 1 and Stage 8 matrix assembly).
- **Fix:** same as R1 — ensure matrix claim IDs are drawn from the inventory.
- **Skipped when:** `claim_inventory.json` is not supplied.

## R5 — verification_path probes have matching external-evidence ledger entries

When `external_evidence.json` is supplied, every `findings[].verification_path[]` step whose `method` is one of the **ledger-routed methods** (`scite_context`, `pubtator3_entity_check`) MUST have a matching `external_evidence.entries[]` row with the same `(tool, paper_id)` — where `tool` is derived from `method` per the `_LEDGER_METHODS` registry in `validate_audit_report.py` (`scite_context → scite`, `pubtator3_entity_check → pubtator3`) and `paper_id` is drawn from the finding's `evidence[].paper_id` set.

- **Validator:** `validate_audit_report.py` `_run_r5`
- **Failure mode:** P7 / Stage 4 narrative says "Scite probe ran" but the ledger has no Scite entry for that paper_id. Indicates the probe text was hallucinated rather than executed.
- **Fix:** route the probe through `external_evidence.lookup_or_fetch` so the call is logged (and memoized) on the ledger; re-emit the finding.
- **Skipped when:** `external_evidence.json` is not supplied.
- **Future tool methods:** when adding a new ledger-routed method to `schemas/finding.json` `verification_path.method` enum, also extend `_LEDGER_METHODS` and `thresholds.ARTIFACT_FRESHNESS_DAYS`.

## Ledger predicates (E1–E3 — artifact-local)

Run by `scripts/validate_artifact.py --kind external_evidence`. Not transitive at Stage 8 (`audit_report.json` doesn't embed the ledger).

- **E1 — unique `entries[].id`.** Sequential IDs are assigned by `external_evidence.lookup_or_fetch`; duplicates indicate manual editing or a races-around-the-rename bug.
- **E2 — `query_hash` is well-formed 64-char lowercase SHA-256 hex.** Stage 1 schema also enforces the pattern; the predicate guards against malformed entries that bypass schema.
- **E3 — (advisory)** `fetched_at` is parseable ISO-8601 and not in the future; `entries[]` is sorted ascending by `fetched_at`. Append-only writes via `lookup_or_fetch` produce sorted ledgers by construction — out-of-order entries flag a manual edit or clock skew.

## Operating principles (validator-enforced, not predicates)

These rules are enforced by the validator and/or render pipeline but are not numbered P-predicates:

- **MUST** quote the original document verbatim when reproducing a claim in the report (so the user can locate the passage); paraphrase external sources per copyright norms.
- **MUST** state coverage gaps prominently in `header.coverage_caveats[]` when full-text access blocks a tier-3 check.
- **MUST** suffix every Scite-derived sentiment claim with "per Scite classification" in the finding's `result_summary`. The accompanying coverage caveat noting Scite's documented bias toward 'mentioning' classification is auto-propagated by `scripts/render_report.py` whenever any finding's `verification_path[]` includes `method == "scite_context"` — the per-finding tag is the LLM's responsibility.
- **MUST** treat Consensus's natural-language synthesis output as a routing aid, not primary evidence — when a synthesis points at a finding, cite the underlying paper, not the synthesis text or aggregator URL (e.g., `consensus.app/papers/...`). **Paper search results returned by Consensus (DOIs, titles, abstracts) are first-class scholarly references** and should be cited like any other PubMed/OpenAlex hit; they carry a discovery advantage because Consensus indexes full-text server-side, surfacing papers where the answer lives in methods/results rather than the abstract.

## Figure-audit predicates (FD-P1–FD-P7 — FIGURE_INTEGRITY parallel family)

Enforced by [`scripts/validate_figure_finding.py`](../scripts/validate_figure_finding.py): FD-P1–FD-P6 are per-finding (`run_predicates`); FD-P7 is the audit-level post-condition (`validate_audit_verdict`). This is the **inbound figure-audit** family — advisory/triage only, parallel to the citation pipeline (see [`CONTRACTS.md`](./CONTRACTS.md) §FIGURE_INTEGRITY and `references/figure_integrity_audit.md`). It never touches P1–P9, the 10-value Verdict enum, or the severity matrix.

- **FD-P1 — categorical flag matches the metric.** `categorical == true ⟺ metric_id ∈ {1.1,1.2,2.1,2.2,3.1}` (the five categorical ⚑ tells: label lexical validity, glyph integrity, encoding–value fidelity, closure, anatomical realism).
- **FD-P2 — only a categorical ⚑=2 can be CRITICAL.** `severity == CRITICAL ⟹ categorical == true AND score == 2`. Aesthetic/soft signals can never be CRITICAL.
- **FD-P3 — D6 is down-weighted (two-sided).** `dimension == D6_stylistic ⟹ severity ∈ {MINOR, INFORMATIONAL}`. Decoration/default-palette signals never drive severity (Bateman CHI 2010); an over-minimization note is valid D6 output.
- **FD-P4 — advisory framing.** `recommended_action` MUST contain an allowed triage template (e.g. "obtain source data", "request provenance", "flag for closer human review", "verify against cited source") AND MUST NOT contain a dispositive verb (`/misconduct|fabricat(ed|ion)|fraud|guilty|confirmed ai|conclude/i`). The audit triages attention; it never concludes misconduct.
- **FD-P5 — decaying signals carry their caveat.** `dimension == D4_render_artifact ⟹ decaying_signal_caveat is non-null` (4.x=0 is never exoneration; 2026-generation models pass these cleanly).
- **FD-P6 — deterministic findings name their linter.** `tier == 1_deterministic ⟹ source_check is non-null` (no hallucinated deterministic results).
- **FD-P7 — the flag needs a hard finding (audit-level).** audit verdict `FIGURE_INTEGRITY_FLAG ⟹` at least one finding with `score == 2 AND (categorical == true OR tier == 1_deterministic)`. The flag cannot be raised on soft/aesthetic signals alone.
