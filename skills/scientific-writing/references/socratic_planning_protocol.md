# Socratic Planning Protocol (Plan Mode)

> Pre-drafting Socratic dialogue for manuscript planning. Optional Stage 0 of
> the manuscript development workflow. Load this file when the user invokes
> Plan Mode.

## Activation

Plan Mode is opt-in. Trigger phrases:
- "plan my paper" / "plan my thesis" / "plan my dissertation"
- "think through my draft" / "think through my manuscript"
- "before I write" / "before I draft"
- "outline my thesis" / "chapter plan" / "argument plan"

When ambiguous between Plan Mode and the `deep-research` skill's `socratic`
mode, use this rule:
- **Plan Mode** → user already has a research question and (often) results,
  needs help articulating *how to write the paper well*.
- **deep-research socratic** → user is still defining the research question
  itself.

## Core Principles

1. **Guide, don't draft.** This protocol elicits the user's thinking. The user
   does the writing later, in a draft-mode capability.
2. **Section-specific questioning.** Each manuscript section gets its own
   commitment question and 5 mandatory probes.
3. **At least 2 rounds of dialogue per section** before extracting a Section
   Summary.
4. **Surface unstated assumptions.** Pre-empt reviewer concerns by forcing the
   user to articulate weaknesses before drafting.
5. **Honor user opt-outs.** If the user asks to skip prediction questions
   ("don't ask me to predict", "skip ahead"), drop the commitment questions
   and go straight to mandatory probes; keep all other Socratic questioning.

## Step 0: Research Readiness Check

Before section-by-section planning, confirm the user has the foundation to
write a paper. Ask three diagnostic questions:

1. What materials do you already have? (literature, data, analysis results)
2. Is the research question fixed? Can you state it in one sentence?
3. How systematic is your literature foundation? (For an original-research
   paper, has the background reading been comprehensive enough to position
   your contribution? For a literature-review paper, this *is* the central
   question — has your search and screening been systematic enough that the
   review itself is reproducible?)

| Response pattern | Action |
|---|---|
| Has RQ + data + literature | Proceed to Step 1 |
| Has RQ + literature, no data (theoretical / lit-review paper) | Confirm paper type, proceed to Step 1 |
| Vague topic, no RQ | Spend extra rounds in Step 1 (Thesis Crystallization) |
| Has nothing concrete | Recommend `deep-research` (socratic mode) first; pause Plan Mode |

## Step 1: Thesis Crystallization

Help the user state the paper's central argument in one sentence.

**Round 1 — Basic:**
- What is your paper arguing? Give it in one sentence.
- If a reader finishes the paper and you've succeeded, what do they now believe
  that they didn't before?

**Round 2 — Stress test:**
- How would someone who disagrees with you respond?
- What is the single biggest difference between your paper and the most
  closely-related existing work?

**Round 3 — Refinement (only if needed):**
- Be precise: are you claiming A causes B, or A is associated with B?
- What is the scope? Are there populations / conditions where this argument
  doesn't hold?

**Output of Step 1:**

```markdown
### Thesis
**Statement:** [one-sentence thesis]
**Type:** [causal / correlational / comparative / exploratory / evaluative]
**Scope of applicability:** [boundary conditions]
```

## Step 2: Section-by-Section Negotiation

For each section: explain the section's purpose → ask the commitment question →
ask the 5 mandatory probes → ask follow-up probes as needed → offer writing-
direction hints → extract a Section Summary → confirm with the user → move on.

### Section commitment questions

A short commitment fires before the mandatory probes. Tag the user's answer as
`[COMMITMENT: section: response]` so it can be re-surfaced later in the
dialogue if reality diverges from the prediction.

| Section | Commitment question (default) |
|---|---|
| Introduction | What part of the Introduction do you expect to be hardest to write well? |
| Literature Review (original-research paper) | Rate the comprehensiveness of your literature coverage 1–10. Where is it thin? |
| Literature Review (lit-review paper — variant) | When you imagine the synthesis you want to deliver, what is the one tension or contradiction in the literature that the review *must* resolve, and how confident are you (1–10) that your sources cover both sides? |
| Methods | If you were the reviewer, what would be your first criticism of your method? |
| Results | Which of your findings is strongest? Which is weakest? |
| Discussion | If you could predict the reviewer's main concern about your Discussion, what would it be? |
| Conclusion | On a 1–10 scale, how clearly does your contribution stand out from existing work? |

The Lit-Review variant fires for review-style papers (literature reviews,
narrative reviews, scoping reviews). Use the original-research version
otherwise. When in doubt, ask the user which paper type they're writing.

### Introduction — 5 mandatory probes

1. By the time the reader finishes the Introduction, what one problem must
   they understand?
2. What gap in current knowledge does your work fill?
3. State the research question in one sentence.
4. Why is *now* the right moment for this work? (recent finding, technological
   shift, policy change, clinical need)
5. What is the reader's reason to keep reading past the Introduction?

**Follow-up probes** when answers are vague:
- Vague gap → Can you point to a specific claim in a specific paper that your
  work answers or challenges?
- Vague timeliness → Is there a recent paper, technology, or event that makes
  this question urgent today rather than five years ago?

**Writing-direction hint (offer once user has answered the 5):**
> A workable Introduction structure: hook (1–2 paragraphs grounded in a recent
> finding or clinical observation) → background (2–3 paragraphs scoping the
> field) → gap (1 paragraph naming the specific unanswered question) → purpose
> and RQ (1 paragraph).

### Literature Review — 5 mandatory probes

1. Which theories, frameworks, or bodies of work will you review?
2. How do these works relate? (complementary / contradictory / evolutionary /
   parallel)
3. What is the largest gap in the existing literature?
4. Where does your work sit on that literature map?
5. Which prior viewpoint do you most disagree with, and why?

**Follow-up probes:**
- Listed works lack a connecting thread → What story are you telling across
  these three topics? What is the through-line?
- Gap is not specific → If you ran a literature search and got zero hits,
  what would your search terms be? Those terms describe your gap.

**Writing-direction hint:**
> A workable structure: theme 1 → theme 2 → theme 3 → critical synthesis. For
> each theme: definition / concept → key findings → controversy or gap → link
> to your work.

### Methods — 5 mandatory probes

1. What method are you using to answer the RQ?
2. Why is this method better than the alternatives a reviewer would suggest?
3. Where does the data come from, and is the sample size adequate?
4. How do you ensure validity and reliability (or trustworthiness, for
   qualitative work)?
5. What is the largest limitation of this method, and how do you mitigate it?

**Follow-up probes:**
- Method-RQ mismatch → Your RQ asks about [X] but [method] is typically used
  for [Y]-type questions. How do you bridge that?
- Vague QA → Concretely, what steps did you take to make sure your results
  aren't an artifact?

**Writing-direction hint:**
> Methods sections answer "why this choice?" at every step: design → sample →
> data collection → analysis → quality assurance → ethics (if relevant) →
> limitations.

### Results — 5 mandatory probes

1. State your single most important finding in one sentence.
2. Was anything unexpected? How do you explain it?
3. Is there data that does *not* support your hypothesis?
4. What is the clearest way to present each result (table / figure / text)?
5. Which results most need in-depth discussion later?

**Follow-up probes:**
- Only supportive findings reported → Were there any patterns in the data that
  surprised you or made you pause? Those are usually the most interesting
  results.
- Presentation unclear → If you could include only one figure or table to
  capture the whole study, which would it be?

**Writing-direction hint:**
> Results report; they do not interpret. Lead with the descriptive overview,
> then walk findings in RQ order, then place tables / figures near the
> reporting prose. Use the prose to direct the reader's eye to the key cells
> or panels.

### Discussion — 5 mandatory probes

1. How do your findings dialogue with the existing literature — do they agree,
   extend, or contradict?
2. What are the theoretical or mechanistic implications?
3. What practical, clinical, or policy recommendations follow?
4. List at least 2–3 limitations of your work.
5. What are the most useful next research directions?

**Follow-up probes:**
- Superficial literature dialogue → Do your results agree with [specific
  author]'s findings on this point? If not, why might they differ?
- Single limitation → Reviewers expect at least 2–3 limitations. What would
  the most skeptical reader push on?

**Writing-direction hint:**
> Discussion structure: key findings recap (1 paragraph) → dialogue with
> literature (2–3 paragraphs) → implications (1–2 paragraphs) → limitations
> (1 paragraph) → future directions (1 paragraph). Discussion is "so what?",
> not a re-statement of Results.

### Conclusion — 3 mandatory probes

1. State your core contribution in one sentence.
2. What single sentence do you most want the reader to remember?
3. What is now true (or visible) that wasn't before this paper?

**Writing-direction hint:**
> Conclusion structure: answer the RQ (1 paragraph) → core contribution
> (1 paragraph) → outlook or call to action (1 paragraph). Do not introduce
> new evidence or arguments.

## Step 3: Argument Stress Test

After all section dialogues complete, stress-test the overall argument with
challenger probes:

- Where is the weakest link in the argument chain?
- If your argument were reversed, what would still hold?
- Does the evidence really license a conclusion this strong, or does a softer
  framing fit better?
- Is there a simpler explanation that accounts for the data?

The user's answers feed into the Section Summaries' "Counter-arguments" and
"Argument Strength" fields.

## Question Taxonomy

Each section dialogue should include at least one question from each of four
types:

### 1. Clarifying — make meaning precise
- "When you say X, do you mean A or B?"
- "Can you give a specific example of X?"
- "How would you define X for a reader outside the field?"

### 2. Probing — push on reasoning and evidence
- "What evidence supports that claim?"
- "How do you know X causes Y rather than being correlated with Y?"
- "What kind of evidence would change your mind?"

### 3. Structuring — organize thinking and surface connections
- "How does this connect to what you said about X earlier?"
- "If you had to summarize this section in one sentence, what would it be?"
- "What must the reader understand from this section before the next?"

### 4. Challenging — stress-test before reviewers do
- "A skeptical reviewer would say X — how do you respond?"
- "If a replication of your study returned the opposite result, what would
  that mean for your thesis?"
- "What is the strongest argument against your position?"

### Distribution by section

| Section | Clarifying | Probing | Structuring | Challenging |
|---|---|---|---|---|
| Introduction | High | Medium | Medium | Low |
| Literature Review | Medium | High | High | Medium |
| Methods | Medium | High | Medium | High |
| Results | High | Medium | High | Medium |
| Discussion | Low | High | Medium | High |
| Conclusion | Low | Medium | High | Medium |

## Convergence Signals

Track four signals during each section's dialogue. A section is "converged"
when at least 3 of 4 signals read **Yes**.

| # | Signal | Test |
|---|---|---|
| C1 | **Thesis clarity** | User states the paper's thesis in one sentence without hedging; sharper across rounds. |
| C2 | **Section coherence** | User explains why this section leads to the next in cause-effect or logical-necessity terms. |
| C3 | **Evidence mapping** | User attaches specific data, citations, or findings to each claim — not vague references. |
| C4 | **Limitation honesty** | User volunteers limitations without being prompted. |

Optional fifth signal across the whole conversation (observational only — no
Auto-End rule fires on it):

- **C5 — Self-calibration**: section commitments grow more accurate as the
  dialogue progresses (e.g., late-paper predictions are sharper than
  Introduction predictions). Use C5 as colour for the final wrap-up — point
  out the trend if visible — but do not gate convergence on it.

## Auto-End Rules

| Condition | Action |
|---|---|
| 3+ convergence signals = Yes for current section | Section converged; extract Section Summary; move on |
| All sections converged + Stress Test complete | Plan Mode finished; emit Chapter Plan; offer to proceed to drafting |
| > 8 rounds on a single section without convergence | Offer the user three options: (a) skip to next section, (b) accept partial summary and move on, (c) pause and resume later |
| > 30 total rounds without completing all sections | Suggest switching to outline-only mode and saving the partial Chapter Plan |
| User says "stop" / "I'm done" | Save the partial Chapter Plan, note where you stopped |

## Section Summary (per section)

```markdown
### Section Summary: {section name}

**Core purpose:** [one sentence]
**Core argument:** [one sentence]
**Supporting evidence:**
1. [evidence item]
2. [evidence item]
3. [evidence item]
**Counter-arguments to anticipate:** [reviewer's likely pushback]
**Argument strength:** [Strong / Moderate / Weak]
**Estimated word count:** [N]
**User confirmed:** Yes / Needs revision
```

## Final Output: Chapter Plan

> **Terminology note.** The protocol body uses "section" because journal
> manuscripts have sections (Introduction / Methods / Results / etc.). The
> final aggregated artifact is called "Chapter Plan" because (a) it matches
> the user's likely trigger phrase (`chapter plan`, `outline my thesis`) and
> (b) for theses and dissertations the section-level units *are* chapters.
> A Chapter Plan packages the per-section summaries into a single document.

After all sections converge:

```markdown
# Chapter Plan: [Paper Title or Topic]

## Thesis
[Statement, type, scope from Step 1]

## Section Summaries
[All Section Summaries, in manuscript order]

## Stress-Test Results
[Argument-chain weaknesses identified in Step 3 + user's responses]

## Drafting Notes
- Total estimated word count: [N]
- Section pacing recommendations: [if any]
- Sections flagged for extra revision attention: [list]
```

The user pastes this Chapter Plan back when invoking the skill's draft-mode
capabilities (§Workflow Stage 1+ in `SKILL.md`). It feeds outline creation as
high-quality scaffolding, replacing what would otherwise be ad-hoc drafting
prompts.

## Tone

- Warm, but firm enough that users do not skip mandatory probes.
- Specific, not generic — point at the exact thing to think about, not "think
  harder."
- Discipline-aware — adjust terminology to the user's field (clinical vs.
  basic-science vs. computational vs. social-science framing).
- Match the user's language and register; mirror their seriousness level.

## Quality Criteria

- ≥2 rounds of dialogue per section.
- All Section Summaries user-confirmed.
- Final Chapter Plan covers Thesis + 6 Section Summaries + Stress-Test
  Results.
- Writing-direction hints are concrete and actionable, not generic advice.
- Auto-end rules invoked when applicable; the protocol does not silently grind
  on past 8 rounds in one section.

## Cross-References

- **Upstream**: `deep-research` (socratic mode) — for users who don't yet have
  a research question. Plan Mode picks up after the RQ is fixed.
- **Downstream**: this skill's draft-mode capabilities (§Core Capabilities and
  §Workflow for Manuscript Development in `SKILL.md`). The Chapter Plan
  scaffolds Stage 1 outline creation.
- **Related**: `peer-review` — Plan Mode forces the user to anticipate
  reviewer concerns *before* drafting; `peer-review` evaluates the finished
  draft against reviewer standards. Use Plan Mode to prevent issues;
  `peer-review` to catch them.

## Attribution

Adapted from `socratic_mentor_agent` in
[academic-research-skills](https://github.com/Imbad0202/academic-research-skills)
by Cheng-I Wu (CC BY-NC 4.0). Patterns and design DNA are non-copyrightable;
prose has been reformulated for license compatibility (this plugin is
MIT-licensed). The Lit-Review-paper variant of the LR commitment question is
a new addition for biomedical lit-review use cases.
