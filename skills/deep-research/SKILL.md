<!-- Pipeline architecture inspired by academic-research-skills by Cheng-I Wu -->
---
skill_name: deep-research
version: 1.0.0
description: >
  Multi-mode biomedical research pipeline with 7 agents, 8 modes, and 6 mandatory
  checkpoints. Conducts literature reviews, systematic reviews, hypothesis generation,
  fact-checking, and Socratic research mentoring. Uses PubMed, bioRxiv, Consensus,
  and ToolUniverse MCP tools for evidence gathering and verification.
trigger_keywords:
  - literature review
  - systematic review
  - find papers
  - search pubmed
  - hypothesis
  - research question
  - deep research
  - fact-check
  - PRISMA
  - meta-analysis
  - guide my research
  - evidence synthesis
do_not_trigger:
  - summarize this paper (use research-paper-summarizer)
  - review this manuscript (use peer-review)
  - write a paper (use scientific-writing)
  - target dossier (use target-intelligence)
  - drug dossier (use drug-intelligence)
  - validation scorecard (use target-validation)
---

# Deep Research

A 6-phase research pipeline with 7 specialized agents, 8 operational modes, and
6 mandatory user checkpoints. Every phase requires user approval before proceeding.

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

## Agent Team

| Agent | File | Role |
|-------|------|------|
| **Bibliography** | `agents/bibliography.md` | Multi-database search via MCP tools, collision-aware queries, DOI dedup |
| **Verification** | `agents/verification.md` | Source grading (Level I-VII → T1-T4), anti-hallucination, predatory detection |
| **Synthesis** | `agents/synthesis.md` | Thematic synthesis, dossier integration, gap analysis, T1-T4 labeling |
| **Advocate** | `agents/advocate.md` | Devil's advocate at 3 checkpoints: cherry-picking, bias, logic chain |
| **Mentor** | `agents/mentor.md` | Socratic 5-layer dialogue with SCR protocol and convergence detection |
| **Ethics** | `agents/ethics.md` | AI disclosure, attribution integrity, dual-use screening |
| **Compiler** | `agents/compiler.md` | Mode-specific report assembly, citation formatting, limitations |

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

**CHECKPOINT 1 — Advocate Review:**
Load `agents/advocate.md`. The advocate reviews:
- Is the RQ answerable with available evidence?
- Is the methodology appropriate for this question type?
- Is the scope balanced (not too broad, not too narrow)?
- Severity: Critical (blocks) / Major (revise) / Minor (note) / Observation

Present the RQ, methodology, scope, and advocate assessment to the user.
**User must approve before Phase 2.**

### Phase 2: INVESTIGATION

**Objective:** Systematic literature search and source verification.

**Process:**
1. Load `agents/bibliography.md`. Execute multi-database search:
   - PubMed MCP → `search_articles` (primary for biomedical)
   - bioRxiv MCP → `search_preprints` (cutting-edge)
   - Consensus MCP → `search` (cross-domain synthesis)
   - ToolUniverse fallbacks → EuropePMC, SemanticScholar (via `grep_tools`/`execute_tool`)
   - Apply collision-aware negative filters if HIGH collision risk
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

**CHECKPOINT 2 — Source Review:**
Present annotated bibliography with source counts, evidence levels, database coverage,
and search saturation metric to the user.
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
3. Gap analysis: classify as empirical, methodological, theoretical, temporal, or geographic
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
**User confirms delivery.**

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
| `entity-resolution` | **Upstream** — provides collision filters for bibliography agent search |
| `target-intelligence` | **Upstream** — dossier consumed by synthesis agent (dossier-first) |
| `drug-intelligence` | **Upstream** — dossier consumed by synthesis agent (dossier-first) |
| `target-validation` | **Downstream** — consumes T1-T4 evidence grading from synthesis |
| `scientific-writing` | **Downstream** — consumes research reports for manuscript drafting |
| `scientific-schematics` | **Downstream** — generates visual schematics for hypothesis mode |
| `citation-management` | **Downstream** — manages bibliography output |
| `statistical-analysis` | **Downstream** — meta-analysis and power analysis |
| `peer-review` | **Complementary** — deep review of manuscripts (deep-research reviews evidence, peer-review reviews manuscripts) |

## Shared Infrastructure

- `skills/shared/references/evidence_grading.md` — T1-T4 tier definitions
- `skills/shared/tool-lookup.yaml` — MCP capability key resolution
- `skills/shared/QUANTIFICATION_THRESHOLDS.md` — literature coverage thresholds (§1), replication standards (§3)
- `skills/shared/references/known_param_corrections.md` — ToolUniverse API quirks
