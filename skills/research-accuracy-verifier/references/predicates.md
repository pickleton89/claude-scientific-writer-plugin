# Validator-enforced predicates P1–P8

Findings that violate these predicates are **rejected** by the validators in `scripts/`, forcing a Stage-8 loop-back. They are not guidelines — the validator code is the source of truth, and this document mirrors it for reading convenience. The canonical definitions live in [`CONTRACTS.md`](./CONTRACTS.md) §Hard predicates.

P1–P5 and P7 are per-finding predicates enforced by [`scripts/validate_finding.py`](../scripts/validate_finding.py). P8 is a cross-stage post-condition enforced by [`scripts/validate_audit_report.py`](../scripts/validate_audit_report.py) and invoked transitively from `render_report.generate_report()` so audits cannot render past a P8 violation.

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

## Operating principles (validator-enforced, not predicates)

These rules are enforced by the validator and/or render pipeline but are not numbered P-predicates:

- **MUST** quote the original document verbatim when reproducing a claim in the report (so the user can locate the passage); paraphrase external sources per copyright norms.
- **MUST** state coverage gaps prominently in `header.coverage_caveats[]` when full-text access blocks a tier-3 check.
- **MUST** suffix every Scite-derived sentiment claim with "per Scite classification" in the finding's `result_summary`. The accompanying coverage caveat noting Scite's documented bias toward 'mentioning' classification is auto-propagated by `scripts/render_report.py` whenever any finding's `verification_path[]` includes `method == "scite_context"` — the per-finding tag is the LLM's responsibility.
- **MUST** treat Consensus's natural-language synthesis output as a routing aid, not primary evidence — when a synthesis points at a finding, cite the underlying paper, not the synthesis text or aggregator URL (e.g., `consensus.app/papers/...`). **Paper search results returned by Consensus (DOIs, titles, abstracts) are first-class scholarly references** and should be cited like any other PubMed/OpenAlex hit; they carry a discovery advantage because Consensus indexes full-text server-side, surfacing papers where the answer lives in methods/results rather than the abstract.
