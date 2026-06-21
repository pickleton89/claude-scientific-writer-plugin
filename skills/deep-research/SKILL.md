---
name: deep-research
version: 1.1.0
description: >
  Multi-mode biomedical research pipeline (7 agents, 8 modes, 6 mandatory user
  checkpoints) for literature reviews, systematic reviews (PRISMA), hypothesis
  generation, fact-checking, evidence synthesis, and Socratic research mentoring.
  Uses PubMed, bioRxiv, Consensus, Paperclip, and ToolUniverse MCP tools for
  evidence gathering and verification. Triggers on "literature review",
  "systematic review", "find papers", "search pubmed", "hypothesis", "research
  question", "deep research", "fact-check", "PRISMA", "meta-analysis", "guide my
  research", "evidence synthesis". Do NOT use to summarize a single paper (use
  research-paper-summarizer), review a manuscript (use peer-review), write a paper
  (use scientific-writing), or build a target/drug dossier or validation scorecard
  (use target-intelligence / drug-intelligence / target-validation).
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

<!-- Pipeline architecture inspired by academic-research-skills by Cheng-I Wu (CC-BY-NC 4.0) -->

# Deep Research

A 6-phase research pipeline with 7 specialized agents, 8 operational modes, and
6 mandatory user checkpoints. Every phase requires user approval before proceeding.

> **Prose Standards:** Synthesis output (literature reviews, hypothesis narratives, fact-check reports) conforms to [`../shared/references/prose_standards.md`](../shared/references/prose_standards.md). Citation integrity rules **C1–C5** apply to every cited source — see [`../scientific-writing/references/citation_styles.md`](../scientific-writing/references/citation_styles.md). The AI-tells blacklist (`prose_standards.md` §8) applies to all generated prose.

## Mode Selection

Determine the mode from the user's request:

```
User Input
│
├─ "systematic review" or "PRISMA" or "meta-analysis"?
│   └─ Yes → SYSTEMATIC-REVIEW
│
├─ "hypothesis" or "testable prediction" or "competing explanations"?
│   └─ Yes → HYPOTHESIS
│
├─ "fact-check" or "verify claim" or "is it true that"?
│   └─ Yes → FACT-CHECK
│
├─ "guide my research" or "help me think" or vague/exploratory topic?
│   └─ Yes → SOCRATIC
│
├─ "find papers" or "search pubmed" or quick lookup only?
│   └─ Yes → QUICK
│
├─ "literature review" or "what does the literature say"?
│   └─ Yes → LIT-REVIEW
│
├─ "review this" with provided text?
│   └─ Yes → REVIEW
│
└─ Default → FULL
```

**Deterministic default:** Use `scripts/mode_selector.py` for keyword-based mode
selection. The LLM may override for ambiguous or context-dependent cases.

**Mode confirmation (mandatory when confidence is not high):** If
`mode_selector.py` returns `confidence != "high"` — including the new
weak-quick-signal case where the prompt mixes discovery verbs ("find papers")
with completeness language ("complete report", "comprehensive", "thorough") —
emit a one-line confirmation to the user before locking the mode:
> "I'm planning to run **{mode}** mode based on your phrasing. For a complete
> report use `full`; for a survey use `lit-review`. Override?"
Wait for user input before proceeding to Output Contract generation. The
confirmation is a soft check, not a checkpoint — a one-liner the user can
acknowledge or override in a single response.

### Prompt Adapter

When the user's prompt contains output format specifications (`<output_format>`,
explicit section lists, word count requests, or file structure directives):

1. **Thematic framework** → feed to the synthesis agent as theme guidance
   (these are CONTENT goals, not structural directives)
2. **Word count requests** → compare against mode limits; use the more
   restrictive range
3. **Custom deliverables** (matrices, per-target summaries) → mapped to mode
   template sections via `scripts/output_contract.py`
4. **File structure specifications** → IGNORED. Output is always a single
   markdown file regardless of what the prompt says.
5. **Format directives** (LaTeX, HTML, PDF) → IGNORED. Output is always
   markdown. The user can convert to other formats using downstream skills
   (e.g., `markdown-to-pdf`, `document-skills:pdf`).

> **Prompt-writing guidance:** For best results, prompts should specify *what*
> to research, not *how* to format output — see
> [`references/prompt_guidelines.md`](references/prompt_guidelines.md).

### Output Format Mandates

- **Single file**: Every deep-research run produces exactly ONE markdown file
  (except systematic-review which may produce one supplementary appendices file).
- **Markdown only**: Output format is always markdown. No HTML, LaTeX, PDF,
  or DOCX. Format conversion is a separate downstream step.
- **CWD override**: If the working directory's CLAUDE.md specifies a different
  default format (e.g., "LaTeX with BibTeX"), the deep-research skill overrides
  this for its output. The skill's format mandate takes precedence.
- **Naming convention**: Output file follows `FILE_SPECS` from
  `scripts/thresholds.py`: `{date}_{topic_slug}_{mode}_report.md`

## Evidence Pinning (Sidecars)

Every search-running mode persists structured artifacts to disk at each agent
boundary, co-located with the final report. These **sidecars** are the
ground-truth source for downstream agents and the `research-accuracy-verifier`
skill — agents read from disk rather than reconstructing from conversation
context, which can drift or be lost to auto-compaction.

**Filename convention:** `{date}_{topic_slug}_{mode}_{kind}.json` — computed
via `scripts/thresholds.sidecar_filename(mode, kind, date, topic_slug)`.

**Schemas:** `skills/deep-research/schemas/` (Draft-07).
**Validator:** `scripts/validate_sidecar.py --kind {sources|grading|synthesis|advocate}`

| Kind        | Emitted by    | Contains                                                                   |
|-------------|---------------|----------------------------------------------------------------------------|
| `sources`   | Bibliography  | Per-source metadata + per-database search log                              |
| `grading`   | Verification  | Per-source T-tier, evidence level, verification status, predatory flag     |
| `synthesis` | Synthesis     | Themes, gap classifications, contradictions, dossier cross-refs, hypotheses |
| `advocate`  | Advocate      | Cumulative findings across all 3 checkpoint runs                           |

**Mode gating** (`scripts/thresholds.SIDECAR_SPECS`):

| Mode | sources | grading | synthesis | advocate |
|------|:---:|:---:|:---:|:---:|
| full, lit-review, systematic-review, hypothesis, fact-check, review | ✓ | ✓ | ✓ | ✓ |
| quick | ✓ | ✓ | — | — |
| socratic | — | — | — | — |

**Enforcement** (`scripts/thresholds.SIDECAR_ENFORCEMENT`): `"required"` —
missing or invalid sidecars block compiler assembly. Open CRITICAL advocate
findings ALWAYS block regardless of enforcement mode (non-negotiable safety
gate). The `"advisory"` mode (warnings only) remains available for debugging
by editing the constant.

**Marker on the final report:** the compiler prepends an HTML comment to the
first line so the verifier can detect pinned runs and switch to diff-mode:

```markdown
<!-- evidence_pinned: true sidecars: sources.json,grading.json,synthesis.json,advocate.json -->
```

**Compaction recovery:** because every fact a claim depends on lives on disk,
a run that loses context to auto-compaction can be resumed by re-loading the
sidecars and re-invoking the compiler — no re-search required.

See [research-accuracy-verifier/references/CONTRACTS.md](../research-accuracy-verifier/references/CONTRACTS.md#deep-research-handoff-pinned_sidecars) for the cross-skill cooperation contract.

## Agent Team

| Agent | File | Role | Sidecar |
|-------|------|------|---------|
| **Bibliography** | `agents/bibliography.md` | Multi-database search via MCP tools, collision-aware queries, DOI dedup | emits `sources.json` |
| **Verification** | `agents/verification.md` | Source grading (Level I-VII → T1-T4), anti-hallucination, predatory detection | reads `sources.json`; emits `grading.json` |
| **Synthesis** | `agents/synthesis.md` | Thematic synthesis, dossier integration, gap analysis, T1-T4 labeling | reads `sources.json` + `grading.json`; emits `synthesis.json` |
| **Advocate** | `agents/advocate.md` | Devil's advocate at 3 checkpoints: cherry-picking, bias, logic chain | reads `sources.json`; appends to `advocate.json` (cumulative) |
| **Mentor** | `agents/mentor.md` | Socratic 5-layer dialogue with SCR protocol and convergence detection | — (socratic mode has no sidecars) |
| **Ethics** | `agents/ethics.md` | AI disclosure, attribution integrity, dual-use screening | — |
| **Compiler** | `agents/compiler.md` | Mode-specific report assembly, citation formatting, limitations | reads ALL sidecars; refuses assembly on missing/invalid sidecars (when enforcement = `required`) or open CRITICAL advocate findings (always) |

## Agents Active per Mode

| Mode | Bibliography | Verification | Synthesis | Advocate | Mentor | Ethics | Compiler |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **full** | x | x | x | x | | x | x |
| **quick** | x | x | | | | | x |
| **lit-review** | x | x | x | | | | x |
| **systematic-review** | x | x | x | x | | x | x |
| **hypothesis** | x | x | x | x | | x | x |
| **fact-check** | | x | | | | | x |
| **socratic** | | | | x | x | | |
| **review** | | | | x | | x | x |

## 6-Phase Pipeline

Every phase ends with a **mandatory user checkpoint**. The user must approve before
the next phase begins. There are no auto-continue shortcuts.

### Phase 1: SCOPING

**Objective:** Transform the user's topic into a precise, actionable research question.

> **Use extended thinking as a planning scratchpad.** Before emitting the
> contract bundle, reason through (in thinking, not in the output): the RQ's true
> scope, breadth-vs-depth trade-off, which databases actually fit, how much effort
> the question warrants, and where it naturally decomposes into sub-questions.
> Planning in thinking — rather than committing to the first framing — improves
> instruction-following and right-sizes effort for the query.

**Process:**
1. Identify research domain and entity types (gene, drug, disease, general)
2. If biomedical entities detected, check if entity-resolution identity table exists
   - If yes: import collision risk level and negative filters
   - If no: note entity names for disambiguation during search
3. Formulate research question using appropriate framework:
   - Biomedical intervention → PICO (Population, Intervention, Comparison, Outcome)
   - Biomedical observation → PEO (Population, Exposure, Outcome)
   - General research → open-ended with scope boundaries
4. Define inclusion/exclusion criteria
5. Select databases (≥3 required; see `references/biomedical_research.md` for mapping)

### Contract Bundle Generation (Output + Search + Decomposition)

After scope is defined and mode is selected, generate the **contract bundle**
— Output Contract + Search Contract + Decomposition Contract, all presented at
Checkpoint 1, all frozen on approval:

1. Run `scripts/mode_selector.py` with the user's prompt to determine mode
   (if not explicitly specified by the user). Honor the mode-confirmation
   prompt above when confidence is not high.
2. Run `scripts/output_contract.py` to produce the structural contract:
   - Loads the canonical section schema for the selected mode
   - Parses the user's prompt for explicit format specifications
   - Maps user-specified sections to canonical template slots
   - Flags any unmapped items as warnings
3. Run `scripts/search_contract.py` to produce the **Search Contract** (skip
   for `socratic` and `review` — those modes do not search):
   - Inputs: `mode`, `domain` (biomedical / molecular / pharmacology /
     cross-domain / preprint-heavy), `research_question`, optional
     `has_named_entities` override
   - Outputs the required-database list (per `thresholds.MIN_DATABASES` +
     the resolved domain tier table). In heavy modes (`full` /
     `lit-review` / `systematic-review` / `hypothesis`) and `fact-check`,
     **Paperclip replaces bioRxiv as a required full-text channel** for
     all domains except `preprint-heavy`. **PubTator3** is auto-promoted
     to required when the RQ contains named biomedical entities (gene
     symbols, disease/variant keywords, drug INN suffixes). **WebSemantic**
     (Exa-based grey-literature discovery) is required across `full` /
     `lit-review` / `hypothesis` / `fact-check`; `systematic-review` opts
     in separately (see step 3a below). In `fact-check`, WebSemantic
     auto-hardens to non-strikable when the RQ contains regulatory-entity
     tokens (`FDA`, `EMA`, `MHRA`, `recall`, `withdrawal`, `retract`,
     `EUA`, `boxed warning`, etc.) — regulatory pages are first-party
     authoritative for those claims.
   - Optional/reception channels (Scite, Paperclip in preprint-heavy,
     PubTator3 when no entities detected) are also surfaced
   - Mode-skipped channels are surfaced explicitly so the user can see
     *why* a tool is absent
   - When Paperclip is required but the binary is missing, a Checkpoint 1
     warning fires (no hard fail) — user can install/login or strike the
     channel
3a. **WebSemantic opt-in (systematic-review only).** Before locking
    Checkpoint 1 in `systematic-review` mode, emit this one-line prompt:
    > "WebSemantic (Exa grey-lit discovery) is not in the default
    > systematic-review contract. PRISMA-S §S4 permits grey-lit inclusion
    > **only with disclosure**. Opt in? (yes → I'll append WebSemantic to
    > optional_databases and emit a `prisma_s_disclosure_block` in the
    > Search Strategy.) [yes / skip]"
    If the user opts in: append WebSemantic to `optional_databases`,
    flag the contract with `prisma_s_disclosure_required: true`, and the
    bibliography agent must emit a PRISMA-S §S4 disclosure block in
    Phase 2 output. Out-of-whitelist hits stay context-only per
    `shared/references/citable_web_domains.md` W3 rules.
3b. Run `scripts/decomposition_contract.py` to produce the **Decomposition
    Contract** (skip for `socratic` and `review`):
    - Inputs: `mode`, `research_question`, optional `complexity` override,
      optional `topic_slug`. When `complexity` is omitted,
      `scripts/complexity_classifier.py` labels the RQ simple / comparative /
      complex from its wording plus the mode prior.
    - Outputs the sub-question fan-out: `fan_out_width` researchers (from
      `thresholds.COMPLEXITY_SCALING`, capped to 1 outside
      `thresholds.FANOUT_MODES` — only `full` / `systematic-review` /
      `hypothesis` fan out in Phase 3; the rest plan a decomposition but run
      single-context), each with a per-subagent tool-call budget.
    - Emits one sub-question scaffold per researcher with four mandatory
      delegation fields — **objective, output format, source guidance,
      boundary**. **Replace every `[FILL]` placeholder with the real semantic
      decomposition before freezing** — bounded, non-overlapping sub-questions
      prevent the duplicated-work / coverage-gap failure mode.
4. Present ALL THREE contracts to the user as part of Checkpoint 1:
   - Selected mode and confidence level (plus any mode-confirmation note)
   - Output: section structure with user-label mappings, word counts, file spec
   - Search: required databases (gated), optional channels (mode-eligible),
     mode-skipped channels, and the `MIN_DATABASES` / `MIN_SOURCES` floor
   - Decomposition: complexity level, fan-out width, and the sub-question list
     with their objectives + boundaries
   - Any warnings from the contracts
5. The user can strike specific optional channels from the Search Contract
   (e.g., "skip Paperclip") via `SearchContract.strike()`. Required channels
   cannot be struck below `MIN_DATABASES`.
6. The user must approve the bundle before Phase 2 begins. All three contracts
   are FROZEN after approval — no structural changes and no database
   additions/removals in later phases without re-approval. On freeze, write the
   Decomposition Contract to disk as
   `{date}_{topic_slug}_{mode}_decomposition.json` and validate it via
   `scripts/validate_sidecar.py --kind decomposition` (predicates D1-D3). Unlike
   the four evidence-pinning sidecars, the decomposition contract does NOT gate
   compiler assembly — it is a Phase-1 planning artifact consumed by the Phase 2
   investigation (and, in fan-out modes, the per-sub-question researchers).

### RQ Evaluation Scoring

After output contract generation, score the RQ on Significance, Novelty, and
Feasibility (each 1-5) using the rubric in `references/rq_evaluation.md`. The
score is **informational only** — it does not gate progression. Present alongside
the advocate assessment at Checkpoint 1.

**CHECKPOINT 1 — Advocate Review:**
Load `agents/advocate.md`. The advocate reviews:
- Is the RQ answerable with available evidence?
- Is the methodology appropriate for this question type?
- Is the scope balanced (not too broad, not too narrow)?
- Severity: Critical (blocks) / Major (revise) / Minor (note) / Observation

Present the RQ, methodology, scope, RQ evaluation score (from `references/rq_evaluation.md`),
and advocate assessment to the user.
**User must approve before Phase 2.**

### Phase 2: INVESTIGATION

**Objective:** Systematic literature search and source verification.

**Process:**
1. Load `agents/bibliography.md`. Execute multi-database search **per the
   frozen Search Contract**:
   - The Search Contract's `required_databases` list is authoritative — every
     entry MUST be called.
   - **Issue all required-database tool calls in a SINGLE batched message
     using parallel tool calls.** Sequential execution (call PubMed, wait,
     then call Paperclip) is forbidden in this step. Per the user's CLAUDE.md
     preference, batch independent tool calls. The required set typically
     includes PubMed + Consensus + Paperclip (heavy modes + fact-check,
     non-preprint-heavy domains) or PubMed + Consensus + bioRxiv (quick
     mode, preprint-heavy primary). PubTator3 joins the required set when
     the RQ names biomedical entities.
   - Mode-eligible optional channels (Scite reception in Step 4b,
     Paperclip in preprint-heavy domain, PubTator3 when no entities are
     detected) are also called in the same parallel batch unless the user
     struck them at Checkpoint 1.
   - ToolUniverse fallbacks → EuropePMC, SemanticScholar (via
     `grep_tools`/`execute_tool`) only fire when a contract-required MCP
     trips its circuit breaker.
   - Apply collision-aware negative filters if HIGH collision risk.
2. DOI-based deduplication across all sources
3. Screen results against inclusion/exclusion criteria
4. Load `agents/verification.md`. Grade each source:
   - Evidence hierarchy (Level I-VII)
   - Map to T1-T4 for biomedical claims (see `references/evidence_hierarchy.md`)
   - DOI verification: 100% check via PubMed MCP `get_article_metadata`
   - Spot-check: 50% verified via full-text snippet tools
   - Anti-hallucination: every reference verified via MCP, never AI memory
   - Verdicts: VERIFIED or NOT_FOUND only (no gray zone)

**Exit criteria:**
- ≥15 sources (full/systematic), ≥5 (quick), ≥25 (lit-review)
- ≥3 databases searched
- Search saturation: <5% new papers in final iteration
- ≥60% papers from last 5 years (unless historical review)
- All sources graded with evidence level

**Hard gate (Phase 2 → Phase 3):** Run `scripts/search_audit.py` against the
frozen Search Contract before requesting Checkpoint 2. The audit calls
`exit_criteria.audit_phase_2_search()` to compare contracted required
databases against the actual Search Log. If `passed: false`, the Bibliography
agent MUST loop back, issue parallel tool calls for the missing channels,
and re-run the audit. Phase 3 is BLOCKED until the audit passes. Do NOT
request Checkpoint 2 with a failing audit.

**CHECKPOINT 2 — Source Review:**
Present annotated bibliography with source counts, evidence levels, database
coverage, search saturation metric, and the **Search Audit verdict**
(passed / missing-databases list) to the user.
**User must approve sources before Phase 3.**

### Phase 3: ANALYSIS

**Objective:** Synthesize findings into themes, identify gaps, resolve contradictions.

**Process:**
1. Load `agents/synthesis.md`. Perform thematic synthesis:
   - Organize by 3-7 major themes (NOT study-by-study)
   - T1-T4 inline evidence labeling: `[T{n}: source]`
   - Literature matrix: sources × themes cross-tabulation
   - Theme-level strength: "Theme: X — Strong (8 T1, 3 T2)" or "Weak (2 T3, 1 T4)"
   - Identify consensus, conflicts, and gaps per theme
   - "So What?" test: every theme must explain significance
2. If upstream dossier exists (target-intelligence or drug-intelligence):
   - Extract structured data from dossier FIRST (dossier-first principle)
   - Use dossier data to ground synthesis (GO annotations, PPI, expression, druggability)
   - Only query ToolUniverse for data NOT in the dossier
3. Gap analysis: classify and score gaps per `agents/synthesis.md` Step 5 (7 types, priority scoring)
4. Contradiction resolution: when sources disagree, compare evidence quality and explain

**Mode-specific behavior in Phase 3:**
- **hypothesis mode:** Instead of thematic synthesis, generate 3-5 competing hypotheses:
  - Each mechanistically distinct with different causal chains
  - Ground in database evidence (STRING, GTEx, GO if biomedical)
  - Score each on 10-point quality rubric (testability, falsifiability, parsimony, explanatory power, distinctiveness)
  - Design experimental tests per hypothesis (primary outcome, ≥2 controls, sample size rationale, ≥3 confound mitigations)
  - Formulate ≥2 testable predictions per hypothesis
  - Reference: `references/hypothesis_quality_criteria.md`, `references/experimental_design_patterns.md`
- **systematic-review mode:** Apply RoB 2 (RCTs) or ROBINS-I (non-randomized) per study.
  If ≥2 studies with comparable PICOS: calculate effect sizes, heterogeneity (I-squared),
  produce forest plot data. Apply GRADE certainty assessment per outcome.

**CHECKPOINT 3 — Advocate Review:**
Load `agents/advocate.md`. The advocate reviews:
- Cherry-picking: are contradictory findings suppressed?
- Confirmation bias: does synthesis favor a predetermined conclusion?
- Logic chain: are causal claims supported by the evidence level?
- Alternative explanations: are plausible alternatives considered?

Present synthesis/hypotheses, gap analysis, and advocate assessment to the user.
**User must approve findings before Phase 4.**

### Phase 4: COMPOSITION

**Objective:** Assemble the final deliverable based on mode.

**Contract enforcement:** The compiler agent MUST load the output contract
approved at Checkpoint 1 and assemble the output STRICTLY following the
contract's section schema. See `agents/compiler.md` §Output Contract Authority.

**Process:**
1. Load `agents/compiler.md`. Assemble output:
   - **full:** Complete research report (3000-8000 words) with all sections
   - **quick:** Brief report (500-1500 words) with key findings
   - **lit-review:** Annotated bibliography + thematic synthesis
   - **systematic-review:** PRISMA 2020 report with flow diagram, RoB tables, forest plot data, GRADE tables
   - **hypothesis:** Structured hypothesis document with quality scores, experimental designs, predictions
   - **fact-check:** Claim verification report with verdicts
   - **review:** Assessment of provided text with strengths/weaknesses
2. All outputs in markdown format
3. Mandatory elements in every output:
   - AI disclosure statement
   - Methods section with database versions and search dates
   - All claims cited with `[T{n}: source]` labels
   - Limitations section
4. If hypothesis mode: include mandatory visual schematic via `scientific-schematics` cross-reference

**CHECKPOINT 4 — Draft Review:**
Present the complete draft to the user.
**User must approve draft before Phase 5.**

### Phase 5: REVIEW

**Objective:** Adversarial review and ethics check.

**Process:**
1. Load `agents/advocate.md`. Final vulnerability scan (CHECKPOINT 5):
   - Stress test: What if the strongest source is removed?
   - Stress test: What if the RQ is flipped (opposite conclusion)?
   - Stress test: "So what?" — does this matter to the field?
   - Produce strongest counter-argument (200-300 words)
   - Severity classification of all issues found
2. Load `agents/ethics.md`. Ethics review:
   - AI disclosure present and accurate?
   - Attribution integrity: all references verified, none fabricated?
   - Dual-use screening: biosecurity concerns?
   - Verdict: CLEARED / CONDITIONAL / BLOCKED

**Blocking conditions:**
- Advocate CRITICAL finding → must be resolved before delivery
- Ethics BLOCKED → must be remediated (fabricated refs removed, AI disclosure added, etc.)

Present advocate report and ethics verdict to the user.
**User must acknowledge before Phase 6.**

### Phase 6: REVISION

**Objective:** Address any issues from Phase 5, deliver final output.

**Process:**
1. If Phase 5 found issues: load `agents/compiler.md`, revise to address feedback
2. Maximum 2 revision loops — if issues remain after 2 rounds, document in
   "Acknowledged Limitations" section rather than looping indefinitely
3. Present final revised output

**CHECKPOINT 6 — Final Approval:**
Present final output to the user with:
- Summary of changes from Phase 5 feedback
- Any acknowledged limitations
- Suggested next steps (downstream skills: scientific-writing, plotting-libraries, etc.)
- **Figure handoff guidance** (see "Figure Handoff" section below) if the report mentions figures or the user is likely to request them

**User confirms delivery.**

## Figure Handoff

After a deep-research report is delivered, users frequently request figures. To prevent ad-hoc figure generation that bypasses brand standards, route every figure request through the matrix below. Every path MUST invoke `oligon-brand` (default-on) and conform to the SVG output contract in `../oligon-brand/SKILL.md` `<svg_output>` (font-family Arial/Helvetica, 10pt floor, 12pt base, 14pt panel labels, 16pt titles).

| Figure type                                              | Skill to invoke         | Output format          |
|----------------------------------------------------------|-------------------------|------------------------|
| Schematic, flowchart, pathway, mechanism, architecture   | `scientific-schematics` | SVG (Mermaid or AI)    |
| Data plot, chart, heatmap, survival/forest/volcano       | `plotting-libraries`    | SVG (matplotlib/ggplot)|
| Prose → graphical abstract / visual summary              | `paperbanana`           | PNG (raster; brand colors only, font ladder not enforceable)|
| Mixed / unclear                                          | Ask user which figure type before routing | — |

**Routing rule:** If the figure has named nodes and explicit relationships, use `scientific-schematics`. If it has quantitative data, use `plotting-libraries`. If only unstructured prose, use `paperbanana` — but prefer the other two whenever SVG + font compliance matters.

**Post-generation verification (two-step gate):** For SVG outputs, run BOTH:

1. Text-level grep check:
```bash
grep -oE 'font-family[^;">]+' figure.svg | sort -u
grep -oE 'font-size[^;">]+' figure.svg | sort -u
```
No Times/Calibri/system defaults; no sizes below 10 (px or pt).

2. Visual preview (catches layout failures grep can't see):
```bash
skills/oligon-brand/scripts/render_svg_preview.sh figure.svg
```
Read the resulting PNG and confirm no clipping, overlap, or composition issues before delivering.

## Failure Paths

See `references/failure_paths.md` for 12 documented failure scenarios with recovery
strategies. Key patterns:
- **F1:** RQ non-convergence → provide 3 candidate RQs or suggest lit-review mode
- **F2:** Insufficient literature (<5 sources) → expand keywords, broaden databases, relax date range
- **F4:** Advocate CRITICAL → STOP, present specific corrections, re-review before continuing
- **F5:** Ethics BLOCKED → STOP, present remediation path
- **F6:** MCP tool failure → fall back to ToolUniverse alternatives (see `references/biomedical_research.md`)

## Modes Not Using Full Pipeline

Some modes skip phases:

| Mode | Phases Used | Notes |
|------|------------|-------|
| **fact-check** | 2→4 (verification + compilation) | Verify claims against sources, format verdict report |
| **socratic** | 1 only (scoping via mentor) | Multi-turn dialogue; see `agents/mentor.md` for 5-layer convergence |
| **quick** | 1→2→4→6 | Skip analysis and review for speed |
| **review** | 5→6 only | Review provided text, no search |

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `scientific-brainstorming` | **Upstream** — feeds prioritized ideation directions into Phase 1 SCOPING (use when user is stuck, exploring a design space, or facing a contradiction before literature review) |
| `entity-resolution` | **Upstream** — provides collision filters for bibliography agent search |
| `target-intelligence` | **Upstream** — dossier consumed by synthesis agent (dossier-first) |
| `drug-intelligence` | **Upstream** — dossier consumed by synthesis agent (dossier-first) |
| `target-validation` | **Downstream** — consumes T1-T4 evidence grading from synthesis |
| `scientific-writing` | **Downstream** — consumes research reports for manuscript drafting |
| `scientific-schematics` | **Downstream** — schematics/diagrams (Mermaid + AI), SVG; see Figure Handoff above |
| `plotting-libraries` | **Downstream** — data plots/charts (matplotlib/ggplot), SVG; see Figure Handoff above |
| `paperbanana` | **Downstream** — prose-to-figure graphical abstracts, PNG only |
| `oligon-brand` | **Cross-cutting** — invoked by all figure paths; owns SVG output contract |
| `citation-management` | **Downstream** — manages bibliography output |
| `statistical-analysis` | **Downstream** — meta-analysis and power analysis |
| `peer-review` | **Complementary** — deep review of manuscripts (deep-research reviews evidence, peer-review reviews manuscripts) |

## Shared Infrastructure

- `skills/shared/references/evidence_grading.md` — T1-T4 tier definitions
- `skills/shared/tool-lookup.yaml` — MCP capability key resolution
- `skills/QUANTIFICATION_THRESHOLDS.md` — literature coverage thresholds (§1), replication standards (§3)
- `skills/shared/references/known_param_corrections.md` — ToolUniverse API quirks
