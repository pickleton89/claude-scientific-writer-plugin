# Oligon Voice & Copy Patterns

Canonical reference for Oligon written communications across every
medium. Source: Oligon Digital Style Guide v2.3, §09 (Voice &
Messaging) and §10 (Copy Patterns). Applies to web, deck, social,
email, spoken scripts, manuscript prose, and any branded document.

---

## 1. Positioning

Oligon develops next-generation RNAi therapeutics. The SeekR™ platform
integrates two RNA aptamers (targeting) flanking two siRNA silencers
(payload) into a single self-delivering drug. The elevator pitch lives
at the intersection of three ideas: **modular**, **precise**,
**programmable**.

Oligon sounds like a clinical-stage biotech run by scientists who
trust their audience — confident without bravado, technical without
jargon theater.

---

## 2. Three Voice Rules

### Rule 1 · Translate, don't dumb down

Introduce every technical term with a plain-language analog in the
same breath. Never strip the term; never leave the term unexplained.
The §5 glossary is the canonical pairing bank.

| Do | Don't |
|----|-------|
| Aptamers — RNA oligos that function like chemical antibodies — selectively bind target proteins. | Our SELEX-selected aptamers exhibit high-affinity binding to cognate surface epitopes. |

### Rule 2 · Numbers over adjectives

Specific figures carry credibility. "Tenfold" beats "significant."
"$14M seed" beats "well-funded." Readers in pharma have heard every
adjective.

| Do | Don't |
|----|-------|
| About a tenfold improvement in cellular internalization. | A revolutionary breakthrough in drug delivery. |

### Rule 3 · Verbs over nouns

Active voice with specific verbs. "Reprograms pathogenic T cells"
beats "offers T-cell reprogramming solutions." Nominalization deadens
scientific claims.

| Do | Don't |
|----|-------|
| SeekR bridges drive selective and potent siRNA uptake. | The SeekR platform delivers targeted therapeutic intervention solutions. |

---

## 3. Messaging Pillars

Four claims every major asset should trace to at least one of. An
asset without a pillar anchor is probably off-mission.

| Pillar             | Claim                                               | Evidence to cite |
|--------------------|-----------------------------------------------------|------------------|
| **Self-delivering** | Systemic injection, no special formulation.         | Platform architecture |
| **Multi-modal**     | Dual aptamers + dual siRNA in one molecule.         | SeekR structure diagram |
| **Multi-targeting** | Bivalent binding enables receptor cross-linking.    | ~10× internalization gain |
| **Any cell type**   | Works in T cells, cancer cells, and beyond.         | Pipeline breadth — six programs |

---

## 4. Copy Patterns

Four repeatable patterns cover most copy work: the eyebrow + headline
pair, three headline formulas, the CTA language bank, and the
technical-to-plain glossary.

### 4.1 Eyebrow + Headline pattern

The most distinctive structural move in the system.

- **Eyebrow** = `H3` (14 pt uppercase, 700, `neutral.900`,
  0.05em letter-spacing)
- **Headline** = `H1` or `H2` depending on hierarchy
- 6–10 pt vertical gap binds them as a unit

**Eyebrow rules.** One to three words. Categorical, not a
sub-headline (`THERAPEUTICS`, `SCIENTIFIC APPROACH`, `PIPELINE
UPDATE` — not "Our approach to therapeutics"). Color at
`neutral.900` on light surfaces, `neutral.50` on dark. Never Brand
Blue — that is reserved for logos and Cycle 1 treatment per §03 and
§06 of the style guide.

### 4.2 Headline formulas

**Formula A · Platform claim.** *[Platform or molecule] [verb]
[outcome] [in or for context].*

> SeekR bridges drive selective and potent siRNA uptake.

**Formula B · Capability statement.** *[Outcome noun] for [audience
or use].*

> Dual binders for precision in delivery.

**Formula C · Eyebrow + Answer.** *[Category eyebrow] / [declarative
answer].*

> THE TECHNOLOGICAL BREAKTHROUGH  
> The bivalent SeekR bridge drives selective and potent siRNA uptake.

**Sentence case everywhere.** "The bivalent SeekR bridge drives
selective…" — not "The Bivalent SeekR Bridge Drives Selective…".
Brand terms preserve their casing: SeekR, RNAi, siRNA, DNA, RNA.

### 4.3 CTA language bank

Use these. Nothing else. Consistency across assets is the point.

| CTA               | When to use |
|-------------------|-------------|
| `Learn more`      | Internal pipeline links, news articles |
| `Explore [topic]` | Platform and pipeline sections |
| `Contact us`      | Partnership, investor, or press inquiries |
| `Read the paper`  | Linking to preprints and publications |
| `Watch the video` | Embedded or linked video content |

**Avoid.** "Click here", "Get started", "Book a demo" (this is not
SaaS), "Unlock", "Discover" (overused industry-wide).

### 4.4 Slide-title headline rule

When writing slide titles, make the title a full-sentence declarative
takeaway, not a topic label. The title should carry the finding in
words so a reader who never hears the presenter can reconstruct the
argument from titles alone. This is the deck-scale instance of Rule 2
(numbers over adjectives) and Rule 3 (verbs over nouns), and maps to
Formula A above.

| Do | Don't |
|----|-------|
| SeekR bridges drive ~10× siRNA uptake in Jurkat T cells. | Jurkat uptake data. |

Exceptions: reference slides, disclosure slides, acknowledgments, and
appendix raw-data slides carry neutral topic labels. Agenda and
section-divider slides carry an eyebrow-only pattern.

---

## 5. Technical-to-Plain Glossary

Use the same pairing twice so readers see it reinforced. When a term
appears in a headline, the pairing belongs in the nearest body
paragraph.

| Technical term          | Plain translation |
|-------------------------|-------------------|
| Aptamer                 | RNA oligo that functions like a chemical antibody |
| siRNA                   | RNA silencer that switches off a specific gene |
| SeekR                   | A single drug molecule carrying targeting binders and silencers |
| Endocytosis             | The process cells use to pull material inside |
| Receptor cross-linking  | Binding two receptors at once to force them into the cell |
| T-cell exhaustion       | When cancer-fighting immune cells lose their ability to function |
| Bivalent                | Binding at two sites at once |
| RNAi                    | The cellular pathway that silences specific genes |

---

## Cross-references

- Color, typography, and figure-level brand rules:
  `references/brand-colors-full.md`
- Medium-specific conventions (social, web, deck, email):
  `references/medium_playbooks.md`
- File-naming convention for all assets:
  `references/medium_playbooks.md` §6

## Plugin integration

Consumed by `scientific-writing`, `scientific-slides`, `research-posters`,
`paper-2-web`, `executive-summary`, and `markdown-to-pdf` — apply these
voice and copy patterns wherever those skills produce written Oligon output.
