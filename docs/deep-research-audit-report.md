# Deep Research Output Determinism Audit Report

**Date:** 2026-03-28
**Audited:** 3 deep-research runs from March 27-28, 2026

## Executive Summary

All three runs failed to use the deep-research skill's deterministic infrastructure. No run invoked `mode_selector.py`, `output_validator.py`, or any deterministic script. Checkpoint enforcement was absent in all runs. The outputs varied from 42K words across 7 markdown files to a 14-page LaTeX PDF, despite using the same underlying skill.

## Session Identification

| Run | Primary JSONL | Project Context (CWD) | Size | Date |
|-----|---------------|----------------------|------|------|
| 1: siRNA Targets | `Documents/0a7e49b9-625d-4cf2-b46a-d5894eef4154.jsonl` | `/Users/jeffkiefer/Documents` | 2.6 MB | Mar 28 07:05 |
| 2: Surface Aptamer | `OneDrive-Reports/51750cea-be91-4800-8a92-4dd7aad50f05.jsonl` | `~/Library/CloudStorage/OneDrive-Personal/Reports` | 1.2 MB | Mar 27 17:34 |
| 3: RORC Off-Target | `OneDrive-Reports/2a28e2ba-320f-493c-b43f-33b13773c7ad.jsonl` | `~/Library/CloudStorage/OneDrive-Personal/Reports` | 2.0 MB | Mar 28 07:03 |

## Summary Comparison

| Metric | Run 1 (siRNA) | Run 2 (Aptamer) | Run 3 (RORC) |
|--------|--------------|-----------------|--------------|
| **Skill Formally Invoked** | YES (`deep-research` + `scientific-writer-init` x3) | YES (`scientific-writer-init`) | **NO** |
| **Mode Selector Invoked** | **NO** | **NO** | **NO** |
| **Output Validator Invoked** | **NO** | **NO** | **NO** |
| **Checkpoints Detected** | ~2/6 | ~1/6 | 0/6 |
| **Files Written (main session)** | 2 | 2 | 5 |
| **Files Written (total incl. agents)** | 7 | 6 | 5+ (LaTeX + PDF) |
| **Output Format** | Markdown + HTML | Markdown | **LaTeX/PDF** |
| **Total Word Count** | ~42,000 | ~14,000 | ~6,500 |
| **Subagents Spawned** | 5 | 5 | 5 |
| **MCP Tools Used** | Consensus (7), scite (5), bioRxiv (1) | scite (8), Consensus (5), Open Targets (2) | 0 (all via agents) |
| **CWD CLAUDE.md Override** | No | Yes (OneDrive Reports) | Yes (OneDrive Reports) |

## Per-Run Findings

### Run 1: siRNA Target Selection

**Session:** `0a7e49b9-625d-4cf2-b46a-d5894eef4154.jsonl` (CWD: `/Users/jeffkiefer/Documents`)

**User prompt:** "Perform a deep research project using the deep research skill in the claude scientific writer plugin."

**What happened:**
- `scientific-writer-init` was invoked 3 times (likely retries or multiple stages)
- `deep-research` skill was formally invoked once
- 5 subagents spawned to conduct parallel research
- Main session wrote 2 files; subagents wrote additional phase files (Phase2A, Phase2B, Phase2C, Phase4, HTML)
- No deterministic scripts invoked at any point
- MCP tools used directly: Consensus (7), scite (5), bioRxiv (1)

**Output structure violations:**
- 7 files produced (skill specifies single-file output via compiler template)
- ~42,000 total words (hard max for `full` mode is 10,000)
- HTML file generated (markdown-only contract)
- Phase-based file organization followed the user prompt's 5-phase structure, not the compiler template

**Root causes confirmed:**
- RC1 (Prompt override): The prompt's 5-phase structure replaced the compiler's template
- RC3 (No file structure): Nothing prevented multi-file output
- RC4 (No checkpoints): Subagents ran to completion without user approval gates
- RC6 (No validation): `output_validator.py` was never called
- RC7 (Format drift): HTML file generated with no governance

### Run 2: Surface Aptamer Targets

**Session:** `51750cea-be91-4800-8a92-4dd7aad50f05.jsonl` (CWD: `~/Library/CloudStorage/OneDrive-Personal/Reports`)

**User prompt:** "I want you to perform a deep research on Th17 aptamer targets using the deep research skill in the claude-scientific-writer-plugin."

**What happened:**
- `scientific-writer-init` invoked once (not `deep-research` specifically)
- 5 subagents spawned for parallel research
- Main session wrote 2 files; agents wrote 4 more (target-grouped assessments)
- MCP tools: scite (8), Consensus (5), Open Targets (2) = 15 calls
- No deterministic scripts invoked

**Output structure violations:**
- 6 files produced (target-centric organization, not matching any compiler template)
- ~14,000 words total (exceeds `full` mode hard max of 10,000)
- Files organized by target group (OX40/GITR/CD161, CCR6/IL23R) rather than report sections
- No AI Disclosure section found in assessment files

**Root causes confirmed:**
- RC1 (Prompt override): PICO framework and evaluation criteria replaced compiler structure
- RC2 (Mode ambiguity): "literature review" keyword likely mapped to `lit-review` but task is comparative evaluation
- RC3 (No file structure): Per-target files with no naming convention
- RC4 (No checkpoints): No approval gates detected
- RC5 (CWD override): OneDrive Reports CLAUDE.md may have influenced output
- RC6 (No validation): Validator never called

### Run 3: RORC Off-Target Risk Assessment

**Session:** `2a28e2ba-320f-493c-b43f-33b13773c7ad.jsonl` (CWD: `~/Library/CloudStorage/OneDrive-Personal/Reports`)

**User prompt:** "I want you to use the deep research skill from the claude-scientific-writer-plugin to conduct deep research."

**What happened:**
- Deep-research skill was **NOT** formally invoked (no Skill tool call)
- 5 subagents spawned for 5 parallel research tracks (matching prompt's track A-E structure)
- 0 MCP calls in main session (all literature search delegated to agents)
- No deterministic scripts invoked
- LaTeX compilation via pdflatex + bibtex (3 pass)
- Output: LaTeX project structure (drafts/, final/, references/)
- Total time: ~30 minutes (06:43-07:12) with no checkpoint pauses

**Output structure violations:**
- **LaTeX/PDF output** (skill mandates markdown)
- Full LaTeX project structure (drafts/, final/, references/, sources/, review/, figures/)
- No markdown report produced at all
- No AI Disclosure section in the standard format
- BibTeX reference format instead of `[T{n}: source]` inline citations

**Root causes confirmed:**
- RC1 (Prompt override): Risk assessment structure from prompt dominated
- RC3 (No file structure): LaTeX project structure generated ad-hoc
- RC4 (No checkpoints): 30-minute run with zero pauses
- RC5 (CWD CLAUDE.md override): **CRITICAL** — OneDrive Reports directory has a CLAUDE.md that specifies "Default Format: LaTeX with BibTeX citations", which completely overrode the skill's markdown contract
- RC6 (No validation): Validator never called
- RC7 (Format drift): LaTeX instead of markdown
- **Additional:** Skill was never formally invoked — the LLM treated the user's request as a general instruction rather than routing through the skill system

## Root Cause Validation Matrix

| Root Cause | Run 1 | Run 2 | Run 3 | Confirmed |
|-----------|-------|-------|-------|-----------|
| RC1: Prompt overrides template | YES — 5-phase prompt structure followed | YES — PICO/evaluation criteria followed | YES — PEO/risk categories followed | **3/3 CONFIRMED** |
| RC2: Mode selection ambiguity | Unknown (no mode_selector invoked) | Unknown | Unknown | **Systemic — never invoked** |
| RC3: No file structure enforcement | 7 files | 6 files | LaTeX project tree | **3/3 CONFIRMED** |
| RC4: Checkpoint non-enforcement | ~2 checkpoints | ~1 checkpoint | 0 checkpoints | **3/3 CONFIRMED** |
| RC5: CWD CLAUDE.md override | N/A (Documents CWD) | Possible | **PRIMARY cause of LaTeX output** | **1/3 CONFIRMED (Run 3)** |
| RC6: No output validation | Validator never called | Validator never called | Validator never called | **3/3 CONFIRMED** |
| RC7: Non-markdown formats | HTML generated | N/A | LaTeX/PDF generated | **2/3 CONFIRMED** |

## Critical Discovery: Skill System Bypass

The most significant finding is that the deterministic infrastructure built during the Phase 1-4 audit (mode_selector.py, tier_assigner.py, evidence_strength.py, output_validator.py, thresholds.py) was **never invoked in any run**. The scripts exist and are tested, but:

1. **No orchestration layer** connects them to the skill execution pipeline
2. **The Skill tool invocation** loads SKILL.md as instructions but doesn't trigger any Python scripts
3. **The agent instructions** reference the scripts (e.g., compiler.md says "use scripts/thresholds.py for word counts") but the LLM treats this as advisory guidance, not mandatory execution steps
4. **The checkpoints** are natural-language instructions with no enforcement mechanism

This means the entire deterministic infrastructure is documentation, not enforcement. The fix must bridge the gap between "the scripts exist" and "the scripts are actually executed."

## Recommendations

1. **Output contract system** (Phase 2 of implementation plan) — freeze structural expectations before content generation
2. **Mandatory script invocation** — compiler.md must contain explicit `Bash: python scripts/output_validator.py` instructions
3. **CWD-aware skill loading** — SKILL.md should explicitly override any CWD-level CLAUDE.md format directives
4. **Single-file mandate** — enforced in both skill instructions and validator
5. **Checkpoint enforcement** — consider Claude Code hooks for phase gating
