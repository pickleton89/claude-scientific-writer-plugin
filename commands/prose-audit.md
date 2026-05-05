---
description: Run a prose-quality (STYLE_NONCONFORMING) audit on a draft using the research-accuracy-verifier. Checks prose against the canonical prose_standards.md / prose_standards_thresholds.yaml — no citation/claim verification.
argument-hint: <file-path> [--severity CRITICAL|MAJOR|MINOR] [--document-type grant|manuscript|lit_review|slides|report|memo]
---

# /prose-audit — STYLE_NONCONFORMING audit

Run the **prose-quality-only** branch of `research-accuracy-verifier` against the file the user passed in `$ARGUMENTS`.

This is the style audit, not the citation audit. It populates `style_findings[]` (separate from the citation `findings[]` array) and never touches the Verdict×DocumentType severity matrix.

## Step 1 — Resolve the target file and flags

1. Parse `$ARGUMENTS`:
   - First positional argument: file path (required).
   - `--severity CRITICAL|MAJOR|MINOR` (optional): filter the printed summary; the JSON report still contains all findings.
   - `--document-type grant|manuscript|lit_review|slides|report|memo` (optional): override the intake `document_type`. Defaults to `manuscript` if not given. Note: severity tags do not depend on document_type for prose findings (per CONTRACTS.md), so this only affects the report header.
2. If no path was given, ask the user for one and stop.
3. Confirm the file exists. If not, report and stop.

## Step 2 — Invoke `research-accuracy-verifier` in custom-tier prose-only mode

Build the intake JSON with these exact values (do **not** ask the standard intake questions — this slash command pins them):

```jsonc
{
  "document_type":     "<from --document-type flag, else 'manuscript'>",
  "sources_available": "none",
  "verification_tier": "custom",
  "checks_enabled":    ["prose_quality_audit"],
  "domain":            "general",
  "flag_threshold":    "standard"
}
```

`domain` is set to `general` because prose-only audits do not perform source lookups; the field is unused but still required by `intake.json`. (For full Tier-3 audits invoked outside this slash command, pick `biomedical`/`general`/`mixed` per the actual content.)

Then run the verifier per `skills/research-accuracy-verifier/SKILL.md`. Because `checks_enabled` contains only `prose_quality_audit`:

- Stages 2 (citation existence), 3 (claim alignment), 4 (cherry-picking), 5 (quotes), 6 (numerical) are **skipped**
- The verifier loads `skills/shared/references/prose_standards_thresholds.yaml` at startup (predicate S-P3 — refuse to run if YAML is missing or schema-invalid)
- Output is `style_findings[]` per the StyleFinding schema in `skills/research-accuracy-verifier/CONTRACTS.md` §STYLE_NONCONFORMING

## Step 3 — Report

Print a markdown summary in this shape:

```
## Prose-quality audit — <filename>

**CRITICAL:** N findings  •  **MAJOR:** N  •  **MINOR:** N

### CRITICAL
- [rule_id] <verdict> @ <section>:<line>
  - Original: "<original_text>"
  - Suggested: "<suggested_revision>"

### MAJOR
…

### MINOR
…

Full report: <path-to-audit_report.json>
```

If `--severity` was given, only show findings at or above that severity in the printed summary; the JSON report still contains everything.

If zero findings: print `✅ No prose-standards violations detected against prose_standards_thresholds.yaml v<version>.`

## Step 4 — Hand-offs

End with a per-verdict nudge tailored to the rules that actually fired (not blanket advice — different CRITICAL rules need different remediation):

- **`STYLE_AI_TELL` or `STYLE_TORTURED_PHRASE` (rules AI1–AI8):** suggest invoking the `humanizer` skill on the affected sections — humanizer is the executor for the AI-tells blacklist (§8 of `prose_standards.md`).
- **`STYLE_BANANA_VIOLATION` (rule W6):** humanizer does **not** address term-of-art consistency. Recommend a manual term-of-art pass (pick one canonical term, replace synonyms throughout, declare any intentional aliases inline).
- **`STYLE_NUMERICAL_INCONSISTENCY` (rules Q5/R5):** humanizer does **not** address numerical drift. Recommend reconciling numbers across Abstract / Results / Tables / Figure legends manually, then re-running `/prose-audit`.
- **MAJOR-only run:** suggest `/prose-audit <file> --severity MAJOR` for a focused re-run after fixes.
- **Always:** remind the user that subjective stylistic critique (not tied to a numbered rule in `prose_standards.md`) is out of scope for this audit and belongs to `peer-review`.

## Notes

- This command is the canonical invocation for the STYLE_NONCONFORMING verdict family. The verifier may also be invoked directly for a full Tier-3 audit that includes prose_quality_audit alongside citation checks; this slash command is the prose-only shortcut.
- Thresholds are governed by `skills/shared/references/prose_standards_thresholds.yaml`. Edit there, not here.
- Severity tags come from the YAML — a CRITICAL is CRITICAL regardless of `document_type` (prose violations are not document-type-conditional).
