# Prose Standards — Universal Voice & Style for Scientific Prose

> Canonical voice, style, and revision standards for any prose artifact produced by skills in this plugin.
> Version: 1.0.0
> Used by: scientific-writing, executive-summary, research-paper-summarizer, peer-review, research-accuracy-verifier, deep-research, code-documentation, reproducible-research, scientific-slides, research-posters, paper-2-web, citation-management, venue-templates, markdown-to-pdf
>
> **Severity scheme.** Every auditable rule carries one of three tags:
> - **CRITICAL** — actively misleads the reader (numerical mismatch, terminology inconsistency, fabricated citation). Block submission.
> - **MAJOR** — significantly impairs clarity (buried predicate, dense nominalization, throat-clearing, missing C-C-C structure). Require revision.
> - **MINOR** — stylistic optimization (a single weak verb, one redundant adjective). Suggest revision.
>
> **Companion file.** Machine-readable thresholds live in `prose_standards_thresholds.yaml` (this directory). The validator (`scientific-writing/scripts/validate_writing_quality.py`) and the verifier's `STYLE_NONCONFORMING` checks read from the YAML; the markdown is the human-readable spec. The two MUST stay in lockstep.
>
> **Out-of-line standards.** Two rule families are documented in skill-local references rather than here, because their full prose guidance (decision tables, examples) is too long to live inline:
> - **Citation Integrity Rules (C1–C5)** — see `scientific-writing/references/citation_styles.md`. Auditable subset (C1, C4) is in `prose_standards_thresholds.yaml` Pass 7.
> - **Figure & Caption Integrity Rules (F1–F5)** — see `scientific-writing/references/figures_tables.md`. Auditable subset (F1, F3, F5) is in `prose_standards_thresholds.yaml` Pass 8.
> Both rule families are universal — every writing skill is expected to honor them.

---

## 1. Foundational Principles

Scientific writing is not a historical record of laboratory activity. It is an act of persuasion — an argument designed to transfer complex information into the brain of a skeptical, time-constrained reader with minimal cognitive friction. When a reader struggles to parse a sentence, they are not merely losing time; they are losing trust. Confusion breeds skepticism, and if the prose is messy, the reader unconsciously assumes the science is equally imprecise.

The defining characteristic of excellent scientific prose is what Pinker (2014) calls **classic style**: the writer acts as a guide, directing the reader's gaze toward a shared reality. This stands in sharp contrast to the defensive, self-conscious register known as *academese*, where authors obscure meaning behind abstractions to signal intellectual seriousness to peers. Classic style assumes the reader is intelligent but lacks your specific context. Every word must earn its place by serving that reader's understanding — not the writer's ego.

### 1.1 The Three Pillars

Three principles anchor all scientific prose:

- **Clarity** — sentences are immediately understandable without ambiguity.
- **Conciseness** — every word that does not add meaning is removed.
- **Accuracy** — the prose is a precise, correct representation of the data and methodology.

These reinforce one another. A concise sentence is almost always clearer than a verbose one, and a clear sentence is far more likely to be accurate because it forces the writer to confront exactly what the data support.

### 1.2 The Rule of Parsimony

Every detail included must be essential to supporting the central conclusion. If a methodological nuance or secondary result does not contribute to the narrative, it belongs in supplementary materials or should be removed (Zhang, 2014). The question for every sentence is: *does this serve the reader's journey from question to answer?*

### 1.3 The Curse of Knowledge

Writers routinely fall victim to what Pinker calls the **curse of knowledge** — the inability to imagine what it is like not to know something you have already mastered. This blind spot drives undefined jargon, abstractions without referents, and throat-clearing that delays the point. The antidote is deliberate perspective-taking: before finalizing any section, ask whether a colleague in an *adjacent subfield* could follow the argument without reaching for a textbook.

> **Weak:** It is important to note that the data gathered from our experiments showed a significant increase in cell death.
>
> **Revised:** Cell death increased significantly.

---

## 2. Voice & Register

Voice and register are precision-engineered tools for establishing accountability and minimizing cognitive load. Modern scientific disclosure requires a default shift from the impersonal passive toward active voice. By identifying the actor, the writer eliminates ambiguity and prioritizes data transfer over prose deciphering.

### Rules

| ID | Rule | Severity | Source |
|---|---|---|---|
| **V1** | Default to active voice in Introduction, Results, Discussion. | MAJOR | UCR; Sainani 2.3; Rodrigues 2020 |
| **V2** | Use first-person *I*/*we* for experimental interventions ("We sequenced..."). | MAJOR | UCR; IMRAD Guide |
| **V3** | Reserve passive voice for Methods when the procedure must take precedence over the researcher. | MAJOR | UCR; IMRAD Guide |
| **V4** | Match hedging verbs to evidence type (see §6). Avoid death-by-qualification ("it would seem that"). | MAJOR | Writing Principles |
| **V5** | Prohibit anthropomorphism ("the data wants to show..."). | MAJOR | Writing Principles |

### 2.1 Voice/Tense Reference Table

| Section | Voice | Tense |
|---|---|---|
| Introduction | Active | Present for established facts; past for prior studies |
| Methods | Passive permitted | Past for actions performed; present for general procedures |
| Results | Active | Past for specific findings |
| Discussion | Active | Past for findings; present for interpretations and accepted facts |
| Conclusion | Active | Present for the take-home message |

### 2.2 First Person

Most modern journals (including *Nature*, *Science*, AMA, NEJM) prefer first person when describing the authors' actions or intellectual contributions. It avoids awkward constructions like "It was observed by the authors that..." Use first person to claim responsibility for the intellectual leaps in the paper — the design decisions, interpretive choices, novel arguments.

---

## 3. Sentence Mechanics

Sentences are the fundamental functional units of a scientific argument. Construct them so the reader never backtracks to locate a subject or main verb.

### Rules

| ID | Rule | Severity | Source |
|---|---|---|---|
| **S1** | Eliminate throat-clearing fillers ("It is important to note that," "There is," "It has been shown that"). | MAJOR | Sainani 4.4; Writing Principles |
| **S2** | Bifurcate any sentence exceeding 25 words into distinct functional units. | MAJOR | Writing Principles |
| **S3** | Fix dangling modifiers — introductory phrases must modify the immediate subject. | MAJOR | UCR |
| **S4** | Convert nominalizations back into active verb forms (*analyze* not *perform an analysis*). | MAJOR | UCR; Writing Principles; Sword 2012 |
| **S5** | Apply consistent grammatical form to all lists, comparisons, and series (parallel structure). | MAJOR | Writing Principles; SciWrite Demo 4 |
| **S6** | Buried-predicate alarm: flag any sentence where >12 words separate the subject from the main verb. | MAJOR | Williams & Bizup 2017; AI-Skill audit pass 3 |

### 3.1 The War on Nominalization

Sword (2012) identifies **zombie nouns** — nominalizations that embalm active verbs into heavy, stagnant nouns. Nominalizations require pairing a weak generic verb with a ponderous noun, draining prose of agency.

> **Weak:** We conducted an analysis of the proteins to achieve a reduction in errors.
>
> **Revised:** We analyzed the proteins to reduce errors.

> **Weak:** A determination of the protein concentration was performed.
>
> **Revised:** We determined the protein concentration.

Common substitutions:
- *provides a confirmation of* → *confirms*
- *conduct an assessment of* → *assess*
- *make an adjustment to* → *adjust*
- *perform a measurement of* → *measure*

### 3.2 The Paramedic Method

When a sentence feels bloated but the cause is unclear, apply the **Paramedic Method** (Lanham):

1. Circle the prepositions (*of, in, about, for, onto, into*).
2. Circle the *to be* forms (*is, am, are, was, were*).
3. Ask: "Where is the action?"
4. Change the action into a simple verb.

> **Weak:** The activation of channels is induced by the depletion of stores.
>
> **Revised:** Depleting stores activates channels.

### 3.3 Strong Verbs

Replace generic verbs (*obtained, did, performed*) with specific actions: *calcined, sequenced, titrated, measured, sliced, scooped, phosphorylated, fractionated*.

---

## 4. Paragraph Architecture

Each paragraph must function as a single-themed container. When authors force multiple concepts into one block, they create a wall of words that overwhelms the reader.

### Rules

| ID | Rule | Severity | Source |
|---|---|---|---|
| **P1** | Every paragraph follows the **Context-Content-Conclusion (C-C-C)** framework. | MAJOR | Writing Principles |
| **P2** | Open every paragraph with a topic sentence orienting the reader to the "red thread." | MAJOR | Nature Cancer; Writing Principles |
| **P3** | Each paragraph contains exactly one main idea. | MAJOR | Sainani 3.4 |
| **P4** | Target 3–7 sentences. >10 sentences → split. <2 sentences → expand or merge. | MINOR | Sainani 3.4; Writing Principles |
| **P5** | Front-load the punchline (inverted pyramid): give the take-home early, then supporting evidence. | MAJOR | Sainani 3.4; SciWrite Demo 3 |

### 4.1 The C-C-C Framework

- **Context** (opening sentence) — orient the reader; define the topic; link to the preceding paragraph.
- **Content** (middle sentences) — deliver new evidence, data, or analysis without preamble.
- **Conclusion** (final sentence) — state the take-home or transition.

### 4.2 Internal Coherence

Paragraph flow should rely on the **logical sequence of ideas**, not on transition words used as a crutch. If ideas are arranged chronologically, general-to-specific, or in an "if A, therefore B" form, the reader fills the gaps. Reserve signposts (*however, moreover, consequently, in contrast*) for genuine shifts in direction. Coherence comes primarily from strong topic sentences, parallel structure, and deliberate repetition of key terms.

### 4.3 The Inverted Pyramid

Invert the typical scientific instinct to build through endless details to a buried conclusion. Readers best remember the first and last sentences of each paragraph — give them the punchline early.

---

## 5. Word Choice & Precision

In science, words are tools for precision. Choosing the wrong verb misrepresents the strength of the evidence; inconsistent terminology derails the reader.

### Rules

| ID | Rule | Severity | Source |
|---|---|---|---|
| **W1** | Reserve "significant" for statistical significance (*p* < 0.05). | MAJOR | Writing Principles |
| **W2** | *Affect* is a verb (to influence). *Effect* is a noun (the result). | MINOR | Writing Principles |
| **W3** | *Fewer* for countable items; *less* for continuous quantities. | MINOR | Writing Principles |
| **W4** | **Rule of 3–4**: only abbreviate terms used four or more times; define at first use; avoid in title and abstract. | MAJOR | Writing Principles; Barnett & Doubleday 2020 |
| **W5** | Replace generic verbs ("obtained," "did") with strong, specific actions. | MAJOR | Sainani 4.4; SciWrite Demo 3 |
| **W6** | **The Banana Rule**: once you establish a term for a variable or group, use that exact term throughout. No synonym substitution. | CRITICAL | D2 §IV; Sainani 3.6 |

### 5.1 The Banana Rule (expanded)

If the Methods section introduces an "obese group," the Results section must not refer to a "heavier group." This forces the reader to wonder whether a new variable was introduced. Elegant variation is the enemy of clarity. If you called it a banana in the Introduction, it is still a banana in the Discussion.

This rule is **CRITICAL** because synonym substitution actively misleads — the reader cannot tell whether terminology drift signals a real distinction. The Banana Rule is also the antidote to the "tortured phrases" phenomenon (Cabanac et al. 2021), where automated rewriting tools cycle through synonyms ("counterfeit consciousness" for "artificial intelligence," "enormous information" for "big data").

### 5.2 Lexical Quick-Reference

| Pair | Correct usage |
|---|---|
| Affect vs. Effect | *Affect* (verb): to influence. *Effect* (noun): a result. |
| Fewer vs. Less | *Fewer*: countable items. *Less*: continuous quantities. |
| That vs. Which | *That*: restrictive clause (essential to meaning, no commas). *Which*: nonrestrictive (extra information, set off by commas). |
| Compared with vs. Compared to | *Compared with*: differences between similar items in a study. *Compared to*: metaphorical similarity. |
| Data are | *Data* is plural. "Data are consistent" — not "data is." |
| Significant | Use only for statistical significance (*p* < 0.05). For non-statistical magnitude use *substantial, marked, considerable*. |

### 5.3 Jargon Discipline

Distinguish **precise jargon** (efficient shorthand for experts) from **pretentious jargon** (used to sound sophisticated). The readability decline in scientific literature is driven primarily by general scientific jargon — words used by scientists that substitute for adequate common terms (Plavén-Sigray et al. 2017). Define essential technical terms immediately upon first use.

### 5.4 Grammar & Punctuation

- **Semicolons** — join two independent clauses, or separate complex list items containing internal commas.
- **Colons** — introduce lists, quotes, or amplifications.
- **Dashes** — abruptly insert an essential definition or emphasize a key point.
- **Parentheses** — extra information the reader could comfortably skip.
- **Parallel structure** — strict grammatical parallelism across all items in lists or paired ideas connected by *and*/*but*.
- **Negative → positive** — convert "did not succeed" → "failed"; "is not different from" → "matches."

---

## 6. Hedging & Certainty

Scientific integrity requires saying exactly what the data support — no more, no less. Authors must navigate between two failure modes: **death-by-qualification** (hedging until the claim evaporates) and **unwarranted causal claims** (overstating correlational evidence).

### Hedging Spectrum

Match the verb to the evidence:

| Evidence type | Verbs |
|---|---|
| **Definitive** (controlled experiments, clear causation) | *demonstrates, establishes, shows, proves* |
| **Strong but indirect** (consistent results, plausible mechanism) | *indicates, reveals, confirms* |
| **Suggestive** (correlations, preliminary data) | *suggests, implies, is consistent with* |
| **Speculative** (interpretation beyond data) | *may, might, could potentially* |

Reserve *demonstrates* and *proves* for definitive, high-confidence data. Use *suggests* and *indicates* for data that point toward a conclusion but allow alternative explanations.

> **Over-hedged:** It could potentially possibly be argued that the policy might have some effect.
>
> **Revised:** The policy may affect outcomes.

### Rules

| ID | Rule | Severity | Source |
|---|---|---|---|
| **H1** | Verb strength must match evidence strength per the spectrum above. | MAJOR | Writing Principles; D2 §IV |
| **H2** | No stacked hedges (*"could potentially possibly"*). One hedge per claim maximum. | MAJOR | D4 pass 1 |
| **H3** | Defensive preemptive hedging is prohibited. Hedge because the evidence requires it, not from anxiety. | MAJOR | D2 §IX |

---

## 7. Quantitative Language

Mathematical and statistical precision is fundamental to scientific integrity. Vague quantifiers undermine the objectivity of the record.

### Rules

| ID | Rule | Severity | Source |
|---|---|---|---|
| **Q1** | Replace vague quantifiers ("many," "recently," "often") with specific values or timeframes. | MAJOR | Writing Principles |
| **Q2** | Report exact *p*-values unless *p* < 0.001. Include effect sizes and 95% CIs for all primary outcomes. | CRITICAL | IMRAD Guide |
| **Q3** | Match numerical precision to the measurement capability of the instrument. | MAJOR | Writing Principles |
| **Q4** | Report specific hardware configurations (CPU, RAM, cores) when disclosing computational benchmarks. | MAJOR | Medvedev Rule 10 |
| **Q5** | Numbers cited in prose must precisely match Figures, Tables, and the Abstract. | CRITICAL | Writing Principles; D2 §VIII |

### 7.1 Reporting Template

```
Mean systolic blood pressure decreased significantly in the intervention group
compared to controls (t(48) = 3.21, p = 0.002, Cohen's d = 0.87, 95% CI: 0.34–1.40).
```

A *p*-value reported without effect size, confidence interval, or direction of effect is an **orphan statistic** — statistical significance without biological or clinical context is meaningless.

---

## 8. AI-Writing Tells to Avoid

This is the canonical blacklist of "algorithmic slop" patterns. The `humanizer` skill (`~/.claude/skills/humanizer/`) is the executor; this section is the spec. Wherever drafting tools (or human authors) produce these patterns, they must be removed.

### 8.1 Promotional Bloat

Strip generic promotional language and undue emphasis on significance:
- *groundbreaking, vibrant, pivotal, transformative, robust* (when generic)
- *serves as a testament to, stands as a beacon of, plays a pivotal role in*
- *underscores the importance of, highlights the critical nature of*

### 8.2 Superficial Analytical Frames

AI models abuse present-participle phrases tacked onto sentences to simulate analytical depth:
- *...underscoring its significance.*
- *...highlighting the broader implications.*
- *...reflecting a deeper trend.*

Forbid trailing *-ing* clauses that add no new information.

### 8.3 Dramatic Binary Contrasts

Banish performative "Not X, but Y" structures and manufactured dramatic fragmentation:

> **Slop:** Building products is hard. Not because the technology is complex. Because people are complex.
>
> **Revised:** Building products is hard. Technology is manageable. People aren't.

### 8.4 Vague Attribution

Replace anonymous expert appeals with concrete sources:

> **Slop:** Experts argue it plays a crucial role.
>
> **Revised:** The river supports several endemic fish species (2019 survey).

### 8.5 Throat-Clearing

Already covered by S1; restated here for the AI-tells blacklist:
- *It is important to note that*
- *It is worth mentioning that*
- *It has been widely recognized that*

### 8.6 Em-Dash and Rule-of-Three Overuse

AI prose overuses em-dashes for dramatic interjection and rule-of-three constructions ("clear, concise, and compelling"). Use em-dashes for genuine asides only; vary list lengths.

### 8.7 Hyperbolic Language Drift (post-2023)

Lendvai (2025) and others document a measurable increase in hyperbolic adjectives in scientific abstracts since AI-assisted writing became widespread. Audit for: *unprecedented, revolutionary, paradigm-shifting, game-changing, cutting-edge*.

### 8.8 Tortured Phrases (Cabanac et al. 2021)

Algorithmic synonym substitution to evade plagiarism detection produces absurd substitutions:
- *counterfeit consciousness* (artificial intelligence)
- *enormous information* (big data)
- *bosom peril* (breast cancer)

The Banana Rule (W6) is the structural defense. Any term-of-art substitution that produces an unfamiliar phrase is a tortured-phrase signal.

### Rules

| ID | Rule | Severity | Source |
|---|---|---|---|
| **AI1** | No promotional bloat (§8.1 keyword list). | MAJOR | D4 pass 2; humanizer |
| **AI2** | No trailing *-ing* analytical phrases (§8.2). | MAJOR | D4 pass 2; humanizer |
| **AI3** | No dramatic binary contrasts (§8.3). | MAJOR | D4 pass 2 |
| **AI4** | No vague-attribution constructions (§8.4). | MAJOR | humanizer |
| **AI5** | No throat-clearing (§8.5; reinforces S1). | MAJOR | D4 pass 2 |
| **AI6** | No em-dash overuse or mechanical rule-of-three (§8.6). | MINOR | humanizer |
| **AI7** | No hyperbolic adjectives without supporting evidence (§8.7). | MAJOR | Lendvai 2025 |
| **AI8** | No tortured-phrase substitutions (§8.8). | CRITICAL | Cabanac et al. 2021 |

---

## 9. Principles in Tension

Scientific writing is governed by competing conventions. There is no universal right answer for many stylistic choices — only context-dependent resolutions.

### 9.1 Active vs. Passive Voice

**Tension:** Active is concise and clear; passive is traditionally seen as objective.
**Resolution:** Active by default in Introduction/Results/Discussion. Passive in Methods when the action matters more than the actor. Voice is a deliberate rhetorical choice, not a default habit (Rodrigues 2020).

### 9.2 Narrative vs. Scrupulous Precision

**Tension:** Storytelling improves engagement; scrupulous hedging prioritizes nuance at the expense of flow.
**Resolution:** Narrative guides the *structure* of the paper (the ABT framework — see `imrad_structure.md`); precision guides *sentence-level word choice*. These are not mutually exclusive (Bauman 2023).

### 9.3 Conciseness vs. Discoverability

**Tension:** Standard advice demands brevity; Weinberger et al. (2015) show overly simplified abstracts receive *fewer* citations.
**Resolution:** Optimize for two audiences. Write the **main body** with uncompromising conciseness for human readers. Allow the **title and abstract** to remain dense with specific, descriptive, keyword-rich language for academic search algorithms. Brevity in the body; density in the metadata.

### 9.4 Classic Style vs. Defensive Writing

**Tension:** Classic style prizes transparency; peer review often forces preemptive qualification.
**Resolution:** Draft in classic style — direct, confident, clear. Add hedging strategically during revision, only where the data warrant uncertainty. Never hedge preemptively from anxiety.

### 9.5 Sterile Consistency vs. Controlled Messiness

**Tension:** Mechanical style enforcement flattens prose into a different kind of robotic voice.
**Resolution:** Vary sentence rhythm — alternate short, punchy sentences with longer, reflective ones. Use first-person *I*/*we* to signal a real person thinking. The standards in this document constrain *errors*; they do not prescribe sentence-by-sentence uniformity.

### 9.6 Register by Venue

Calibrate register to the audience:

| Aspect | Nature / Science | Medical (JAMA / NEJM) | ML Conferences (NeurIPS) | NIH Grant (R01) |
|---|---|---|---|---|
| **Audience** | Broad scientists | Clinicians | Researchers / engineers | Review panel (mixed expertise) |
| **Tone** | Engaging, significance-driven | Conservative, formal | Direct, contribution-focused | Persuasive, feasibility-driven |
| **Key feature** | Compelling story | Clinical outcomes | Numbered contributions | Significance + rigor |
| **Methods** | Often in supplement | Comprehensive in main text | Concise / pseudocode | Exhaustive with alternatives |
| **Abstract style** | Flowing paragraph | Structured (labeled sections) | Flowing paragraph | Specific Aims page replaces abstract |
| **Word limits** | Severe (~3,000 words) | Moderate (~3,500) | Strict page limits (8–9 pp.) | 12 pages (Research Strategy) |

For venue-specific format requirements (citation style, line spacing, figure specs), consult `venue-templates/` or `scientific-writing/data/journal_requirements.json`.

---

## 10. Revision

Great writing is not generated; it is rewritten. Professional writers spend the majority of their time in revision. Treat drafting and editing as strictly separate cognitive tasks — silence the inner critic on the first draft, then polish ruthlessly.

### 10.1 The Revision Hierarchy

Revise top-down. Sentence-level editing is wasted effort if the section belongs somewhere else.

1. **Structure.** Does the logical flow hold? Are sections in the right order? Is the "red thread" visible from Introduction to Discussion?
2. **Paragraphs.** Does each contain exactly one main idea? Is C-C-C intact? Are transitions smooth?
3. **Sentences.** Are they concise? Is voice appropriate for the section? Are nominalizations eliminated?
4. **Words.** Is terminology consistent (Banana Rule)? Are numbers checked? Is hedging calibrated?

### 10.2 The Read-Aloud Diagnostic

Reading the manuscript aloud is one of the most effective revision tools. The ear catches repetitive cadences, buried leads, and clumsy syntax that the eye glosses over. If you stumble while reading, the reader will stumble too.

### 10.3 The Five Pre-Submission Tests (R1–R5)

Run these before submission. Failing any one is a CRITICAL block.

| ID | Test | Pass criterion | Severity |
|---|---|---|---|
| **R1** | **Elevator Pitch** | Main finding identifiable from Title + Abstract alone. | CRITICAL |
| **R2** | **Replication** | Methods detailed enough for exact replication by an expert peer. | CRITICAL |
| **R3** | **Independence** | Every figure and table understandable without the main text. | CRITICAL |
| **R4** | **"So What?"** | Discussion explicitly answers strategic significance and future directions. | CRITICAL |
| **R5** | **Numerical Consistency** | Numbers in Abstract = Results = Tables = Figure legends. Single discrepancy = severe credibility hit. | CRITICAL |

### 10.4 Review Modes

When invoking this standard from a drafting or auditing skill, select one mode:

- **Full** — run all checks across the entire document.
- **Section** — restrict to one structural component (Introduction, Methods, etc.).
- **Targeted** — run a single check (e.g., "fix passive voice").
- **Interactive** — paragraph-by-paragraph, requiring approval before each change. Use for sensitive late-stage revision.

---

## 11. Anti-Patterns Appendix

These are recurring failure modes. Each is a violation of one or more rules above; this appendix gives them names so reviewers and authors can talk about them.

| Pattern | Description | Violates |
|---|---|---|
| **Buried Lead** | The most important finding appears in the third paragraph of the Discussion instead of the first sentence. | P5 |
| **Method-Heavy Introduction** | The Introduction drifts into methodological detail before establishing why the reader should care. The gap must come before the approach. | (see `imrad_structure.md` Introduction template) |
| **Restating Discussion** | The Discussion recapitulates the Results in slightly different words, never reaching the "So What?" layer. If a Discussion paragraph could move to Results without seeming out of place, it has failed. | R4; (see `imrad_structure.md`) |
| **Synonym Carousel** | The writer uses three different terms for the same variable across three sections. | W6 (Banana Rule) |
| **Orphan Statistic** | A *p*-value reported without effect size, CI, or direction of effect. | Q2 |
| **Empty Callout** | "Figure 3 shows the results" tells the reader nothing. Instead: "Figure 3 shows that phosphorylation peaked at 30 minutes and declined to baseline by 2 hours." | (see `figures_tables.md`) |
| **Tortured Phrase** | Algorithmic synonym substitution producing unfamiliar substitutes for terms of art. | AI8 |
| **Death by Qualification** | Stacked hedges that evaporate the claim. | H2 |
| **Throat-Clearing** | Empty introductory phrases that delay the point. | S1, AI5 |

---

## 12. Auditable Thresholds (B5 Subset)

This section enumerates the testable rules. The canonical machine-readable form is `prose_standards_thresholds.yaml` in this directory; the validator and verifier MUST read from the YAML, not parse this markdown. The two are kept in lockstep — if you change one, change both.

Audit passes (executed in order by `validate_writing_quality.py` and the verifier's `STYLE_NONCONFORMING` checks):

### Pass 1 — Clutter Extraction
- S1 throat-clearing keyword list (regex match) → MAJOR
- AI5 throat-clearing reinforced → MAJOR
- Negative-construction conversions → MINOR

### Pass 2 — Voice & Verb Vitality
- V1 active-voice default outside Methods → MAJOR (passive ratio threshold: ≤25%)
- S4/W5 nominalization patterns ("conduct an *X* of," "perform *X*") → MAJOR
- W5 weak-verb keyword list (*obtained, did, performed*) → MINOR

### Pass 3 — Sentence Architecture
- S2 sentence length ≤25 words (count, not characters) → MAJOR
- S6 buried-predicate alarm: subject-to-main-verb gap >12 words → MAJOR
- S3 dangling-modifier patterns → MAJOR
- S5 parallel-structure violations in lists → MAJOR

### Pass 4 — Paragraph Structure
- P3 single-idea check (heuristic; flag paragraphs >10 sentences) → MAJOR
- P4 length: target 3–7 sentences; <2 → MINOR; >10 → MAJOR
- P5 punchline-late check (heuristic: first sentence vs. last sentence importance scoring) → MINOR

### Pass 5 — Keyword Consistency (Banana Rule)
- W6 extract terminology from Methods; flag any synonym substitution in later sections → CRITICAL
- AI8 tortured-phrase detection (substituted terms-of-art) → CRITICAL

### Pass 6 — Quantitative Integrity
- Q2 *p*-value reporting (exact unless <0.001; effect size + CI present) → CRITICAL
- Q5 numerical consistency across abstract/main text/tables/legends → CRITICAL
- Orphan statistic detection (statistic with no effect size or CI) → MAJOR

### Pass 7 — Citation & Reference Integrity
- C1 no citations in Abstract → MAJOR
- C4 cross-reference integrity (text ↔ reference list) → CRITICAL

### Pass 8 — Figure & Table Integrity
- F3 chronological mention order in text → MAJOR
- F5 sample sizes (n) in every figure legend → MAJOR
- F1 standalone caption (defines abbreviations, statistics, error bars) → MAJOR

### Pass 9 — AI-Tells Blacklist
- AI1–AI8 keyword/regex list (see §8) → MAJOR (most), CRITICAL (AI8)
- Hyperbolic-adjective audit (§8.7) → MAJOR

### Pass 10 — Pre-Submission Diagnostic
- R1 Elevator Pitch (heuristic) → CRITICAL
- R3 Independence Test (caption + figure self-contained) → CRITICAL
- R5 Numerical Consistency (full reconciliation) → CRITICAL

**Output format requirement.** Every audit finding must report: original text, suggested revision, the rule ID violated, and the severity tag. No silent rewrites.

---

## 13. References

### Empirical readability and impact studies

- Plavén-Sigray, P., Matheson, G.J., Schiffler, B.C., & Thompson, W.H. (2017). The readability of scientific texts is decreasing over time. *eLife*, 6, e27725.
- Barnett, A. & Doubleday, Z. (2020). The growth of acronyms in the scientific literature. *eLife*, 9, e60080.
- Barnett, A., Doubleday, Z., et al. (2021). Better writing in scientific publications builds reader confidence and understanding. *Frontiers in Psychology*, 12, 714321.
- Weinberger, C.J., et al. (2015). The impact of linguistic complexity on science communication. *PLoS ONE*, 10(7), e0135463.
- Hillier, A., et al. (2016). Predicting conference talk evaluations from writing style. *NAACL-HLT*.
- Graf-Vlachy, L. (2021). Is the readability of abstracts decreasing in management research? *Review of Managerial Science*, 16, 1063–1084.
- Ryba, K., et al. (2025). The evolution of scientific writing: 20 million abstracts over 70 years. *Scientometrics*.
- Song, M., et al. (2023). Understanding writing styles of scientific papers in the IS-LS domain. *Journal of Informetrics*, 17(1), 101375.
- Lendvai, G.F. (2025). ChatGPT in academic writing: scientometric analysis. *SAGE*.

### Style guides and theoretical works

- Pinker, S. (2014). *The Sense of Style: The Thinking Person's Guide to Writing in the 21st Century*. Viking.
- Pinker, S. (2014). Why academics stink at writing. *Chronicle of Higher Education*.
- Sword, H. (2012). *Stylish Academic Writing*. Harvard University Press.
- Sword, H. (2017). *Air & Light & Time & Space: How Successful Academics Write*. Harvard University Press.
- Williams, J. & Bizup, J. (2017). *Style: Lessons in Clarity and Grace* (12th ed.). Pearson.
- Schimel, J. (2012). *Writing Science: How to Write Papers That Get Cited and Proposals That Get Funded*. Oxford University Press.
- Olson, R. (2015). *Houston, We Have a Narrative: Why Science Needs Story*. University of Chicago Press.
- Bauman, J.R. (2023). Maximize your research impact with storytelling. *Nature Reviews Cancer*, 23, 799.
- Bloomfield, E.F. (2024). *Science V. Story: Narrative Strategies for Science Communicators*. University of California Press.

### Voice and mechanics

- Rodrigues, V. (2020). Reconsidering the use of the passive voice in scientific writing.
- Amdur, R.J., Kirwan, J., & Morris, C.G. (2010). Use of the passive voice in medical journal articles. *AMWA Journal*, 25(3).
- Kurihara, Y., et al. (2024). Strategies on reducing wordiness to enhance readability in academic writing. *PMC*.
- Sand-Jensen, K. (2007). How to write consistently boring scientific literature. *Oikos*, 116, 723–727.

### Narrative and storytelling

- Dahlstrom, M.F. (2014). Using narratives and storytelling to communicate science with nonexpert audiences. *PNAS*, 111(S4), 13614–13620.
- McCall, B., et al. (2021). Storytelling as a research tool. *International Journal of Public Health*, 66, 1604262.

### Algorithmic prose pathologies

- Cabanac, G., Labbé, C., & Magazinov, A. (2021). Tortured phrases: A dubious writing style emerging in science. *arXiv:2107.06751*.
- Buriak, J.M., et al. (2023). Best practices for using AI when writing scientific manuscripts. *ACS Nano*.
- Al Hosni, J. (2025). Preserving authorial voice in academic texts in the age of generative AI. *Arab World English Journal*, 16(3), 244–258.

### Foundational practitioner sources cited as anchor authorities

- Sainani, K. *Writing in the Sciences* (Stanford SciWrite course modules 1.2–5.4).
- *Nature Cancer* Editorial (2023). Balancing informativeness with accessibility.
- Medvedev, P. (2020). Ten rules for algorithmic bioinformatics. *PLoS Computational Biology*.
- Romano, J. & Moore, J. (2020). Guidelines for scientific software papers.
- Zhang, X. (2014). Reader-centric scientific writing.
