# Stage 2 — Citation existence verification

**Purpose:** For every cited reference, attempt at least two independent identifier paths before assigning a verdict that downgrades the citation. A single failed lookup is not sufficient — APIs fail intermittently and bad metadata can hide a real paper.

**Predicate enforced:** P7 (Scite retraction probe — see [`../predicates.md`](../predicates.md)) for biomedical/mixed domains.

## Routing

- DOI / PMID / PMCID resolution via PubMed (biomedical) or Crossref / OpenAlex (general).
- If no identifier provided, search by author + year + title fragment + journal.
- **No identifier exists at all — citation is a bare URL** (e.g., `[12] FDA approval letter, https://www.fda.gov/...`, or a citation to a registry / society / preregistration page): the URL itself IS the canonical record. Resolve it via `mcp__exa__web_fetch_exa` (or directly if already known) and verify the page resolves + matches the claim's framing of it (correct date, correct agency, correct action). Satisfy P7 via the **web-source carve-out** (see below — `verification_path[]` entry with `method == "web_search"` + `result_summary` containing the literal token `no_doi`). The URL MUST be on the citable-web-domain whitelist (`../../shared/references/citable_web_domains.md` — i.e., `skills/shared/references/citable_web_domains.md`); out-of-whitelist URLs fall through to `UNSUPPORTED` with `reason: web_evidence_uncitable_tier`. Capability key: `verification.semantic_web_search`.
- Verify all metadata fields agree: authors (at least first and last), year, journal, volume, pages, DOI.
- For journal-volume-year impossibility (e.g., volume X did not exist in year Y), call `scripts/check_journal_volume.py` (capability key: `verification.citation_existence`).

## Retraction / correction check (P7 — validator-enforced)

After identifier resolution succeeds, call `mcp__scite__search_literature` with `dois=[<resolved DOI>]` (no `term`) and inspect the `editorialNotices` field. A clean DOI resolution does NOT exempt the citation from this check — retracted papers resolve cleanly. **The call MUST be logged in `verification_path[]` regardless of outcome.** Four log shapes are valid:

- **Notices found** → append `{ "method": "scite_context", "tool": "Scite MCP (search_literature)", "result_summary": "editorialNotices: <notice_type> — <reason>" }`. Verdict becomes `METADATA_MISMATCH` per the assignment table below.
- **Empty / no record** (paper not indexed by Scite) → append `{ "method": "scite_context", "tool": "Scite MCP (search_literature)", "result_summary": "editorialNotices: none (Scite returned no record for DOI)" }`. Verdict falls through to the standard assignments.
- **Scite API failure** (timeout / rate-limit / wrapper error) → append `{ "method": "scite_context", "tool": "Scite MCP (search_literature) — failed", "result_summary": "probe failed: <api_timeout|empty_response|not_indexed|other>" }`. Verdict still falls through, but the audit trail records the gap.
- **Web-sourced (no-DOI) evidence carve-out** — when the citation is anchored to a web URL with no DOI resolved (e.g., a Stage-2 finding grounded in an FDA approval letter or EMA assessment report surfaced via `mcp__exa__web_search_exa`), append `{ "method": "web_search", "tool": "mcp__exa__web_search_exa", "result_summary": "web evidence: no_doi available for Scite retraction probe; URL=<resolved-url>, fetched_at=<ISO-8601>" }`. The literal token **`no_doi`** in `result_summary` is what trips the validator's P7 carve-out — a `web_search` entry that omits it is a *dedicated* carve-out violation, not a generic P7 violation, so the LLM is told *why* the check failed. The web URL MUST be on the citable-web-domain whitelist (W1 grounds `VERIFIED` directly, W2/W3a ground with tier-specific `result_summary` tag, W3b is context-only and cannot ground `VERIFIED`). Out-of-whitelist URLs cannot satisfy the carve-out.

Silence — no Scite entry of any shape AND no `web_search`+`no_doi` carve-out entry — is a **P7 violation** and `validate_finding.py` rejects the finding when invoked with `--domain biomedical --stage 2` (or transitively via `checkpoint.py write --stage 2` when `domain` is threaded through). Capability key: `verification.citation_existence` (Scite path) / `verification.semantic_web_search` (web carve-out). Canonical call shapes: `tool-lookup.yaml` `literature.citation_tallies` (Scite) and `verification.semantic_web_search` (Exa).

## OpenAlex backstop

Capability key: `verification.citation_existence` fallback. When PubMed AND Crossref both miss for a citation, call `mcp__openalex__batch_resolve_references` with the DOI (or title-author-year tuple) BEFORE declaring `UNSUPPORTED`. OpenAlex covers cross-disciplinary works (CS, physics, social sciences) where PubMed has no coverage. If OpenAlex resolves the work, proceed with metadata-agreement check using OpenAlex's canonical metadata as the reference. If OpenAlex also misses, finalize `UNSUPPORTED` with the full chain in `verification_path[]`. For free-text fallback (fuzzy title match), use `mcp__openalex__search_works` after `batch_resolve_references` returns empty.

## Venue quality sub-check

Capability key: `verification.venue_quality`. AFTER citation existence resolves a DOI/work, call `mcp__openalex__check_venue_quality` with the venue ID. If quality signals indicate predatory venue, non-indexed venue, or DOAJ-non-membership for an OA-claimed venue, attach as a **sub-reason on a `METADATA_MISMATCH` finding** — do NOT introduce a new verdict subtype. The `result_summary` MUST name the venue concern; the `evidence[]` entry MUST record the OpenAlex venue URL + quality signals. When uncertain whether an unfamiliar venue is "predatory" vs "legitimate-but-niche," call `mcp__openalex__get_top_venues_for_field` to compare against top-N venues for the paper's claimed field. Skip this sub-check silently if OpenAlex venue lookup errors — venue-quality is a sub-check, not a hard gate.

## Verdict assignments

| Condition | Verdict |
|---|---|
| Record exists, all metadata matches | `VERIFIED` |
| Record exists, ≥1 field disagrees | `METADATA_MISMATCH` |
| Record exists, `editorialNotices` non-empty (retraction / correction / expression of concern) | `METADATA_MISMATCH` (`result_summary` MUST name notice type + reason) |
| Record exists, OpenAlex `check_venue_quality` flags predatory / non-indexed venue | `METADATA_MISMATCH` with `result_summary` sub-reason `venue_quality_concern` |
| No record found via any identifier path (PubMed → Crossref → OpenAlex `batch_resolve_references`) | `UNSUPPORTED` |
| Access blocked (paywall, timeout) | `UNVERIFIED` with `reason` |

See [`../CONTRACTS.md`](../CONTRACTS.md) for canonical verdict definitions.

## Hallucination signatures (each becomes evidence for `UNSUPPORTED` after multi-path failure)

- Plausible author names with no matching paper
- Real authors paired with titles they never wrote
- DOIs that don't resolve, or resolve to a different paper
- Journal names that don't exist or are off-by-one ("Nature Cellular Biology" vs. "Nature Cell Biology")
- Year / volume mismatches (volume X did not exist in year Y)
- Page ranges inconsistent with journal volume
- Impossible dates (citation predates the cited finding)

## Worked example — CRITICAL finding

| Field | Content |
|---|---|
| **Location** | Significance, paragraph 3, line 42 |
| **Claim (verbatim)** | "Anti-PD-1 monotherapy in the CT26 syngeneic colon model achieves complete response rates of 47% (Chen et al., 2019, *Nature Cancer* 5:1123–1135)." |
| **Verification path** | (1) `doi_lookup` via Crossref — no DOI provided; (2) `pubmed_search` by author + year + title fragment + journal — 0 hits; (3) `journal_volume_check` (Crossref ISSN 2662-1347) — *Nature Cancer* volume 1 first published Jan 2020, so volume 5 in 2019 is impossible; (4) `pubmed_search` for any Chen et al. paper on CT26 + PD-1 in 2018–2020 — no candidate matches the claimed title or response rate. |
| **Evidence** | *Nature Cancer* journal start year per Crossref ISSN 2662-1347: January 2020. No PubMed / Crossref record matches author/year/title/journal/volume combination. |
| **Verdict** | `UNSUPPORTED` |
| **Severity** | CRITICAL (matrix: UNSUPPORTED × manuscript = CRITICAL) |
| **Recommended action** | Replace with a verified source. Selby et al. 2013 (PMID:23300641) reports CT26 anti-PD-1 response data; or Mosely et al. 2017 (PMID:29097623) for syngeneic-model checkpoint response benchmarks. The 47% number itself is unsupported and **MUST** be re-verified against whichever source is substituted. |
| **Confidence** | high |

## On stage completion

Call `checkpoint.py write --slug <slug> --stage 2 --findings <path> --matrix <path> --document-type <type>`. Findings are validated against `schemas/finding.json` before write; on validation failure, fix the offending finding and retry.

**Artifact:** `research/audits/<slug>/02_existence.json`.

## Emit `resolved_sources.json` + backfill `reference_map.json` paper_ids

In addition to the per-stage findings artifact, Stage 2 emits the **canonical resolved-metadata sidecar** (`resolved_sources.json`) AND backfills resolved identifiers into the Stage-1 `reference_map.json`:

1. For every successfully resolved citation, append a `sources[]` entry to `resolved_sources.json` with shape `{paper_id, doi, pmid, pmcid, title, authors, year, venue, resolution_paths[], editorial_notices, venue_quality}`. The `paper_id` is DOI-preferred (PMID fallback, slug last resort) and is **byte-compatible with `deep-research/schemas/sources.json#paper_id`** so cross-skill diff-mode (`intake.pinned_sidecars`) can read either artifact interchangeably.
2. Every resolution attempt (PubMed → Crossref → OpenAlex) is logged in `resolution_paths[]` with `tool`, `outcome ∈ {VERIFIED, METADATA_MISMATCH, UNSUPPORTED, UNVERIFIED}`, and `fetched_at`. At least one entry is required (`minItems: 1`).
3. P7 Scite probes populate `editorial_notices` — when the probe ran and found nothing, encode as `{type: "NONE", fetched_at: ...}` (NOT `null`) so the audit trail records the probe attempt distinctly from "never probed".
4. OpenAlex `check_venue_quality` populates `venue_quality` with the same NONE-sentinel convention.
5. Backfill identifiers into `reference_map.json` via `extract_reference_map.update_paper_ids(reference_map, {citation_key: {paper_id, doi, pmid, pmcid}})` so downstream stages can join `findings[].citations[].key` ↔ `findings[].evidence[].paper_id` ↔ `resolved_sources.sources[].paper_id`.
6. Validate the emitted artifact via `scripts/validate_artifact.py --kind resolved_sources --file PATH`. Predicates S1 (unique paper_id), S2 (at least one identifier), S4 (frozen_at not in future), V1 (fetched_at parseable + not in future), V2 (at least one non-UNVERIFIED outcome) gate the write.

These artifacts power the cross-artifact predicates R2 (evidence paper_id resolution) and R3 (citation key resolution) in `validate_audit_report.py` — see [`../predicates.md`](../predicates.md).
