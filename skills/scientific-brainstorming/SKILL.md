---
name: scientific-brainstorming
version: 1.0.0
description: "Structured ideation methods (SCAMPER, TRIZ, Morphological Analysis, Biomimicry, Six Hats, Provocation, Random Input, Reverse Assumptions, Future Backwards) with a decision tree by challenge type. Use when generating research ideas, exploring interdisciplinary connections, resolving technical contradictions, or challenging assumptions — upstream of deep-research scoping."
allowed-tools: [Read, Write, Edit]
---

# Scientific Brainstorming

<overview>
Structured ideation for research: pick a formal method matched to the creative challenge (stuck, improving existing, contradiction, exploring), run it to completion, then synthesize. Unlike unguided brainstorming, this skill exposes nine method-driven techniques with scientific examples, a decision tree by challenge type, and a TRIZ contradiction-resolution path. It is **upstream** of `deep-research` — once a session produces 2–3 prioritized directions, those become the input to `deep-research` Phase 1 SCOPING.
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- The user is **stuck**: cycling through the same ideas, no new directions emerging.
- The user wants to **improve an existing protocol, assay, or model** and needs systematic operators (SCAMPER) rather than literature search.
- The user has hit a **technical contradiction** ("improving X worsens Y") — potency vs. selectivity, efficacy vs. ADMET, brain-penetration vs. metabolic stability.
- The user wants to **explore a design space systematically** (modality × targeting × release; carrier × payload × trigger) before committing to a research direction.
- The user wants **cross-disciplinary inspiration** (Biomimicry, Random Input) for a problem that has resisted in-domain solutions.
- The user wants to **challenge fundamental assumptions** before committing resources.

Do NOT use this skill when:
- The user wants a **literature review or hypothesis** with cited evidence → use `deep-research` (lit-review or hypothesis mode).
- The user wants **research-question refinement via dialogue** → use `deep-research` socratic mode (5-layer convergence is RQ-driven, not method-driven).
- The user wants **fact-checking or citation verification** → use `research-accuracy-verifier`.
- The user has already prioritized directions and wants experimental design → use `deep-research` hypothesis mode.
</when_to_use>

<decision_framework>
## Decision Tree: Pick a Method by Challenge Type

```
What is the creative challenge?
│
├─ Stuck / no new ideas coming
│   ├─ Need a fresh perspective       → Provocation (Po)
│   └─ Need external stimulus         → Random Input
│
├─ Improving an existing method/system
│   ├─ Incremental improvements       → SCAMPER
│   └─ Hit a technical contradiction  → TRIZ
│
├─ Exploring a design space systematically
│   ├─ Known dimensions, many options → Morphological Analysis
│   └─ Unknown dimensions, need outside inspiration → Biomimicry
│
├─ Need multiple perspectives on a decision
│   └─                                → Six Thinking Hats
│
├─ Questioning fundamental assumptions
│   └─                                → Reverse Assumptions
│
└─ Planning long-term research direction
    └─                                → Future Backwards
```

### Challenge → Primary / Secondary Method

| Challenge | Primary | Secondary | Rationale |
|---|---|---|---|
| No new ideas, feeling stuck | Provocation | Random Input | Break fixation with impossible premises or external stimuli |
| Ideas feel too safe / obvious | Reverse Assumptions | Biomimicry | Challenge defaults; look outside the discipline |
| Too many ideas, need to select | Six Thinking Hats | TRIZ | Multi-perspective evaluation; contradiction resolution |
| Improving an existing protocol | SCAMPER | Morphological Analysis | Systematic operators; design-space mapping |
| Interdisciplinary connections | Biomimicry | Random Input | Nature-inspired patterns; forced cross-domain associations |
| "Improve X but Y worsens" | TRIZ | Six Thinking Hats | Contradiction resolution → multi-angle check |
| Mapping all possible combinations | Morphological Analysis | SCAMPER | Dimension-option matrices |
| Long-term vision / roadmap | Future Backwards | Reverse Assumptions | Solved-future projection |

</decision_framework>

<methods_catalog>
## Methods Catalog (9)

| Method | When to Use | Key Technique | Scientific Example |
|---|---|---|---|
| **SCAMPER** | Improving / extending an existing method | Apply 7 operators (Substitute, Combine, Adapt, Modify, Put to use, Eliminate, Reverse) | Substitute fluorescence for radioactive labeling; Combine proteomics + metabolomics in one prep |
| **Six Thinking Hats** | Multi-perspective evaluation | White (data), Red (intuition), Black (risks), Yellow (benefits), Green (alternatives), Blue (process) | Evaluate a clinical trial: White = prior data, Black = ethical risks, Green = novel endpoints |
| **Morphological Analysis** | Exploring all combinations in a design space | Define dimensions; list options per dimension; enumerate combinations | Drug delivery: carrier (liposome / nanoparticle / hydrogel) × targeting (passive / active / magnetic) × release (pH / thermal / enzymatic) |
| **TRIZ** | Resolving "improving X worsens Y" | Identify contradiction; apply inventive principles; envision Ideal Final Result | Increasing potency worsens toxicity → Local Quality (tissue-targeted delivery) |
| **Biomimicry** | Cross-domain inspiration | Define function → biologize → discover → abstract → apply | "How does nature filter particles?" → kidney nephron → microfluidic countercurrent filter |
| **Provocation (Po)** | Breaking fixed thinking patterns | State an absurd premise; extract useful principles | "Po: proteins fold instantly" → engineer ultrafast-folding domains, IDP research |
| **Random Input** | Need fresh connections | Pick a random word/image/object; force a connection to the problem | "bridge" + enzyme kinetics → bridging molecules connecting substrate to active site |
| **Reverse Assumptions** | Questioning what is taken for granted | List assumptions; flip each; explore consequences | "Higher purity is always better" → reverse → studying functional impurities |
| **Future Backwards** | Long-term roadmap | Start from a solved future; work back to today's milestones | "Cancer cured 2050" → 2040 milestone → 2030 milestone → today's enabling research |

### SCAMPER Operators (Scientific Applications)

- **Substitute** — replace a component (mouse model → organoid; siRNA → CRISPR knockdown).
- **Combine** — merge approaches (single-sample multi-omics; multiplex biomarker panel).
- **Adapt** — borrow from another field (semiconductor lithography → tissue scaffold patterning).
- **Modify** — change scale, frequency, or intensity (single-molecule resolution; 100× concentration).
- **Put to other use** — repurpose data or compound (failed drug for new indication; existing dataset for a new question).
- **Eliminate** — remove a step or assumption (label-free detection; no purification step; drop linearity assumption).
- **Reverse** — invert order or direction (phenotype → genotype; output → input; effect → cause).

### TRIZ Core Concepts

- **Technical contradiction** — improving one parameter worsens another. State explicitly before searching for resolution.
- **Ideal Final Result (IFR)** — envision the perfect outcome with zero cost, harm, and complexity. Working backwards from the IFR exposes which constraints are real and which are assumed.
- **Inventive principles** (most relevant to pharma/biotech): Segmentation, Extraction, Local Quality, Asymmetry, Nesting, Prior Action, Dynamization, Universality, Periodic Action, Self-Service, Inversion / The Other Way Round, Parameter Changes. **Full pharma examples and resolution recipes:** [`shared/references/triz_contradictions.md`](../shared/references/triz_contradictions.md).

### Biomimicry Design Spiral (5 steps)

1. **Define** — frame the function as a verb. *"How does nature filter?"* not *"How does nature make a filter?"*
2. **Biologize** — translate to biological terms. *"What organisms separate particles from fluid?"*
3. **Discover** — find organisms that solve this. AskNature.org; comparative physiology literature.
4. **Abstract** — extract the principle. Not "copy the kidney" but "countercurrent flow with selective permeability."
5. **Apply** — translate the principle back to the research problem.

</methods_catalog>

<cognitive_categories>
## Cognitive Categories — Use One From Each, In Order

Methods serve three distinct cognitive functions. Effective sessions use methods from multiple categories.

| Category | Function | Methods |
|---|---|---|
| **Divergent** | Expand the idea space; break fixation | SCAMPER, Provocation, Random Input, Future Backwards |
| **Connecting** | Find relationships across ideas; build structure | Morphological Analysis, Biomimicry, Reverse Assumptions |
| **Convergent** | Evaluate, select, resolve | Six Thinking Hats, TRIZ |

**Rule:** A complete session uses at least one method from each category, in the order divergent → connecting → convergent. Generating and judging simultaneously reduces both quantity and quality of ideas.

</cognitive_categories>

<method_combinations>
## Method Combinations

Pair methods across cognitive categories for deeper exploration.

| Combination | Use For |
|---|---|
| SCAMPER + Six Hats | Generate modifications, then evaluate each from six perspectives — protocol refinement |
| Morphological Analysis + TRIZ | Map the design space, then resolve contradictions in promising-but-conflicting cells |
| Biomimicry + Provocation | Find natural solutions, then push beyond biological limits into engineered ones |
| Reverse Assumptions + Future Backwards | Flip current assumptions, then project forward from the reversed world |
| Random Input + Morphological Analysis | Random stimulus reveals a missing dimension for the matrix |
| **Three-method sequence (recommended)** | Divergent (15 min) → Connecting (15 min) → Convergent (15 min). Default for full sessions. |

</method_combinations>

<workflow>
## Workflow

A brainstorming session is a 3-stage loop. Do **not** duplicate `deep-research`'s 6-phase pipeline — when ideas are prioritized, hand them off to `deep-research` Phase 1 SCOPING.

### Stage 1: Pick the Method (5 min)

**Steps:**
1. Restate the creative challenge in one sentence. If it does not fit the decision tree, the request likely needs `deep-research` instead.
2. Map prior context: what has already been tried, what failed, what constraints are real vs. assumed.
3. Pick a primary method using the decision tree. Hold a secondary method ready for switch.

**Exit Criteria:**
- [ ] Challenge classified into one branch of the decision tree
- [ ] Primary method selected with secondary as backup
- [ ] Constraints documented (timeline, budget, equipment, expertise)

---

### Stage 2: Run the Method (15–20 min per method)

**Steps:**
1. Apply the chosen method **completely**. For SCAMPER, run all 7 operators. For Morphological Analysis, define all dimensions before enumerating. For Biomimicry, complete the full 5-step spiral. Do not shortcut.
2. Capture every idea with structured format: `idea statement / connection to problem / potential testability`. Aim for 15–30 raw ideas.
3. If the method plateaus after 15 minutes, switch to the secondary method without guilt. Plateaus are normal; they signal a cognitive frame is exhausted, not that the problem lacks solutions.

**Exit Criteria:**
- [ ] At least 10–15 distinct ideas captured with rationale
- [ ] One method run to completion, or two methods exhausted
- [ ] No premature evaluation during this stage

---

### Stage 3: Synthesize (10 min)

**Steps:**
1. **Cluster** related ideas into 3–6 themes; name each cluster.
2. **Identify bridges** between clusters; deliberately combine elements from different clusters.
3. **Apply convergent filter:** for the top 3–5 directions, run Six Thinking Hats or TRIZ to evaluate. If a contradiction surfaces, use [`shared/references/triz_contradictions.md`](../shared/references/triz_contradictions.md).
4. **Hand off** 2–3 prioritized directions to `deep-research` Phase 1 SCOPING with: core idea, why promising, key assumption to validate, first experiment.

**Exit Criteria:**
- [ ] Ideas clustered with descriptive labels
- [ ] 2–3 prioritized directions documented
- [ ] Each direction has a defined first action (literature search, feasibility check, pilot)

</workflow>

<success_criteria>
## Success Criteria

| Metric | Minimum | Target | Excellent |
|---|---|---|---|
| Distinct ideas generated | 10 | 20 | 30+ |
| Methods used (cognitive categories) | 1 | 2 | 3 (full divergent → connecting → convergent) |
| Prioritized directions handed off | 1 | 2–3 | 3 with first-experiment defined |
| Contradictions surfaced & addressed | 0 | 1 | All identified contradictions matched to a TRIZ principle |

**Completion checklist:**
- [ ] Challenge classified using the decision tree
- [ ] At least one method run to completion
- [ ] Ideas clustered (not left as a flat list)
- [ ] At least 2 prioritized directions with explicit next actions
- [ ] If a trade-off was identified, [`triz_contradictions.md`](../shared/references/triz_contradictions.md) consulted

</success_criteria>

<scope>
## Scope

**In Scope:**
- Method-driven ideation sessions for research challenges
- TRIZ contradiction resolution in trade-off scenarios
- Cross-domain analogy via Biomimicry and Random Input
- Synthesis into prioritized directions ready for downstream research

**Out of Scope** (use specialized resources):
- Literature search / hypothesis generation with cited evidence → `deep-research` (lit-review, hypothesis modes)
- Research-question convergence via dialogue → `deep-research` (socratic mode)
- Citation/quote/numerical accuracy auditing → `research-accuracy-verifier`
- Experimental design and statistical planning → `deep-research` (hypothesis), `statistical-analysis`
- Manuscript drafting → `scientific-writing`

</scope>

<adaptive_strategies>
## Adaptive Strategies

When the session is not producing results, intervene:

- **Stuck with no ideas** → switch from analytical methods (SCAMPER, Morphological) to provocative ones (Provocation, Random Input). One absurd premise often breaks the logjam.
- **Ideas feel too safe** → use Reverse Assumptions on the most fundamental assumption. Apply TRIZ Ideal Final Result. Ask: "what would a Nobel-winning solution look like?"
- **Energy or engagement dropping** → switch to Random Input (each stimulus creates a fresh starting point) or take a short break and return with Biomimicry.
- **Many disconnected ideas** → pause divergent generation, spend time clustering and bridging. The best idea is often a hybrid of two mediocre ideas from different clusters.
- **One person dominating** → impose Six Thinking Hats (rotates perspectives), or use silent brainstorming (5 min written, then share).

</adaptive_strategies>

<anti_patterns>
## Common Pitfalls

### 1. Evaluating during divergent generation

**Anti-pattern:** Critiquing each idea as it appears ("but that won't work because..."), shutting down exploration.

**Solution:** During Stage 2, the only permitted response is "Yes, and..." or "What if we also...". Reserve evaluation for Stage 3. Explicitly signal the phase transition: *"We are switching from generation to evaluation."*

---

### 2. Skipping the context phase

**Anti-pattern:** Jumping straight into method execution without mapping what has been tried, what failed, and which constraints are real. Result: rediscovering known solutions or violating known constraints.

**Solution:** Spend the first 5 minutes (Stage 1) on context. Briefly summarize the current state of knowledge before generating. If context is thin, run a `deep-research` quick mode first, then return to brainstorming.

---

### 3. No follow-through after the session

**Anti-pattern:** Generating exciting ideas, then never converting them into research actions. The output is intellectual entertainment, not methodology.

**Solution:** Stage 3 is non-optional. Each prioritized direction must have a literature-search query, a feasibility check, and a key assumption to validate. Hand off to `deep-research` Phase 1 SCOPING within one week.

</anti_patterns>

<cross_references>
## Cross-References

**Skill Selection:** See `SKILL_ROUTER.md` (Decision Tree: Research Workflow) for routing when multiple skills may apply.

### Feeds (Output To)

| Skill | Relationship |
|---|---|
| `deep-research` | **Downstream** — prioritized directions feed Phase 1 SCOPING (full, lit-review, or hypothesis modes). For RQ refinement after ideation, use `deep-research` socratic mode. |
| `target-validation` | **Consumes** TRIZ contradiction resolution from `shared/references/triz_contradictions.md` when Stage 4/5 surfaces a structural trade-off. |

### Related

| Skill | Relationship |
|---|---|
| `peer-review` | Six Thinking Hats parallels multi-perspective manuscript critique; both are convergent evaluation frameworks. |
| `research-paper-summarizer` | Useful as input when brainstorming is grounded in a single foundational paper. |

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|---|---|
| [`../shared/references/triz_contradictions.md`](../shared/references/triz_contradictions.md) | Pharma-relevant contradictions table, 12 inventive principles, and 4-step application recipe |

</references>

## Further Reading

- [Lateral Thinking by Edward de Bono](https://en.wikipedia.org/wiki/Lateral_thinking) — Provocation (Po) and Six Thinking Hats
- [TRIZ Journal](https://www.triz-journal.com/) — full 40 inventive principles and contradiction matrix
- [Biomimicry Institute / AskNature](https://biomimicry.org/) — biological-strategies database
