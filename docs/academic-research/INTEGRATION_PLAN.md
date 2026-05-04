# Integration Plan: Borrow Two Agents from `academic-research-skills`

**Status:** Drafted 2026-05-04. Not started. Pick up when ready.
**Source repo:** `/Users/jeffkiefer/Documents/projects/academic-research-skills` (v3.6.8, CC BY-NC 4.0)
**Target plugin:** `claude-scientific-writer-plugin`

---

## Goal

Borrow two ideas from A's `academic-paper` skill that fill real gaps in B (claude-scientific-writer-plugin):

1. **Search-strategy design layer** (from `literature_strategist_agent`) — make B's lit-review searches reproducible/auditable
2. **Socratic chapter-planning protocol** (from `socratic_mentor_agent`) — give B an optional "think before you draft" mode

Out of scope (explicitly declined): full APA 7.0 compiler, Material Passport, RoB / meta-analysis machinery, bilingual abstracts, intake interview, revision-coach.

---

## What's been copied to this folder

```
docs/academic-research/
├── INTEGRATION_PLAN.md                          ← this file
├── agents/
│   ├── literature_strategist_agent.md           ← source for borrow #1
│   └── socratic_mentor_agent.md                 ← source for borrow #2
└── references/
    └── plan_mode_protocol.md                    ← supporting doc for #2
```

These are reference copies only — don't edit them. Treat them like documentation. The actual integration files will live inside `skills/`.

---

## Borrow #1 — Search Strategy Design Layer

### What we're taking
Just the **5-step strategy design framework** from `literature_strategist_agent.md` (sections "Search Strategy Design" + "Source Screening Protocol"). NOT the whole agent.

The framework:
1. Identify key concepts (primary, secondary, synonyms, discipline terms)
2. Database selection
3. Boolean search string construction
4. Inclusion/exclusion criteria definition
5. Screening protocol (title/abstract → full-text)

### Where it lives in B
**Target skill:** `skills/deep-research/`
**Form:** New reference doc + light wiring in the bibliography agent

**Files to create:**
- `skills/deep-research/references/search_strategy_design.md` — the framework, adapted for biomedical context (PubMed/bioRxiv/Consensus/Scite/Semantic Scholar instead of A's discipline-by-discipline DB table)
- Edit `skills/deep-research/agents/bibliography.md` — add a Step 0 "Strategy Design" before the existing search loop. Output: a documented Search Strategy block that gets included verbatim in the final report.

**What to drop from A's version:**
- The Paper Configuration Record reference (B doesn't have intake_agent)
- The discipline table → replace with biomed-focused database table (B's existing MCP tool list)
- The corpus pre-screening / `literature_corpus[]` references (user declined Material Passport)
- Source count guidelines targeted at IMRaD/conference papers — keep only the lit-review row

### What B gains
- **Reproducibility**: every lit review carries a documented search strategy (concepts → databases → query → criteria) you can paste into a methods section or share with a colleague
- **Auditability**: when a reviewer asks "why these 32 papers?", the answer is in the report
- **Better queries**: forces explicit Boolean construction instead of free-text prompting

### Open decisions
- Does this become a separate `lit-review` mode behavior, or apply across all `deep-research` modes?
- How verbose should the strategy block be in `quick` mode? (Probably collapsed to one paragraph.)
- Should the strategy block live in the report appendix, or up front? (Appendix is more typical.)

### Estimated effort
~2 hours: write the reference doc (1h), edit bibliography agent (30min), test against a real lit-review prompt (30min).

---

## Borrow #2 — Socratic Chapter-Planning Protocol

### What we're taking
The **5-mandatory-questions-per-chapter protocol** from `socratic_mentor_agent.md`. The chapter-specific commitment questions are the highest-leverage piece:

| Section | Commitment question |
|---------|--------------------|
| Introduction | "What do you think will be the hardest part of your Introduction to write well?" |
| Lit Review | "How comprehensive is your current literature coverage, 1–10? What areas are thin?" |
| Methods | "If you were a reviewer, what would be your first criticism of your method?" |
| Results | "Which of your findings is strongest? Which is weakest?" |
| Discussion | "If you could predict the reviewer's main concern about your Discussion, what would it be?" |
| Conclusion | "How clearly does your contribution stand out from existing work, 1–10?" |

Plus the chapter-specific 5-question probes that follow each commitment (different probe sets for each section — see the full agent file).

### Where it lives in B
**Target skill:** `skills/scientific-writing/`
**Form:** New optional mode

**Files to create:**
- `skills/scientific-writing/references/socratic_planning_protocol.md` — adapted version of A's protocol, biomed-flavored, stripped of overhead
- Edit `skills/scientific-writing/SKILL.md` — add a `plan` mode (parallel to existing modes) that activates this protocol before drafting. Trigger keywords: "plan my paper", "think through my draft", "before I write".

**What to drop from A's version:**
- SCR (Stress-test/Commitment/Reflection) full machinery — too heavy. Keep just the chapter commitment question, drop the cross-chapter pattern tracking and reflection extraction. (User can always add it back later if they want.)
- Bilingual prompts (zh-TW lines)
- INSIGHT Collection tagging — B doesn't have a downstream agent that consumes these
- "Plan mode" handoff to structure_architect_agent — B's `scientific-writing` doesn't have that downstream split

**What to keep verbatim:**
- The 6 chapter commitment questions
- The chapter-specific 5-question probe sets (these are the gold)
- "Guide, don't draft" core principle
- "At least 2 rounds of dialogue per chapter" pacing rule

### What B gains
- **Pre-drafting clarity**: forces the user to articulate the argument before writing prose
- **Surfaces unstated assumptions**: especially valuable for Discussion sections where the "so what" often isn't crisp
- **Optional**: doesn't affect existing draft modes; users opt in when they want the slower path

### Open decisions
- Mode name: `plan`? `socratic-plan`? `outline-socratic`? (A uses `plan`.)
- Output format: just the dialogue transcript? Or a structured "Chapter Plan" markdown the user can paste back when drafting?
- Should the lit-review section commitment question be reworded for B's primary use case (literature reviews, not original research)? Probably yes — the current phrasing assumes original work.

### Estimated effort
~3 hours: extract and trim protocol doc (1.5h), wire mode into SKILL.md (30min), test on a real planning conversation (1h).

---

## Pickup Checklist

When you return to this:

- [ ] Read this plan + skim the two source agent files in `agents/`
- [ ] Decide on the open questions (3 per borrow, listed above)
- [ ] **Borrow #1 first** (smaller, more reproducibility-driven)
  - [ ] Create `skills/deep-research/references/search_strategy_design.md`
  - [ ] Edit `skills/deep-research/agents/bibliography.md` Step 0
  - [ ] Test on a real prompt — check the strategy block appears in output
  - [ ] Update `skills/deep-research/SKILL.md` if the mode behavior changes
- [ ] **Borrow #2 second**
  - [ ] Create `skills/scientific-writing/references/socratic_planning_protocol.md`
  - [ ] Add `plan` mode entry to `skills/scientific-writing/SKILL.md`
  - [ ] Test on a real planning conversation
  - [ ] Add trigger keywords for the new mode
- [ ] Run `/fresh-eyes` review on both changes
- [ ] `/ship` (changelog + commit + push)
- [ ] Save milestone to graphiti MCP knowledge graph

---

## Attribution

If either integration ships, add to the relevant SKILL.md or reference doc:

> Inspired by `academic-paper` agents in [academic-research-skills](https://github.com/Imbad0202/academic-research-skills) by Cheng-I Wu (CC BY-NC 4.0).

Note: A is CC BY-NC 4.0. B is MIT. Borrowing *ideas and patterns* is fine (uncopyrightable). If you copy substantial verbatim text from A's reference docs into B, you'll need to either rewrite or deal with the license incompatibility. Easiest path: paraphrase and credit.
