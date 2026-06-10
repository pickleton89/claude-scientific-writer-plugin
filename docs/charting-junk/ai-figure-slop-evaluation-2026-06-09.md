# Visual Features That "Scream" AI: A 2025–2026 Literature Synthesis and Operational Scoring Rubric

*Prepared 9 June 2026. Confidence labels follow your convention: **HIGH** = multiple corroborating sources; **MEDIUM** = single reliable source; **LOW** = inferred, speculative, or practitioner anecdote. Source class is flagged throughout as primary research, review, practitioner commentary, or vendor claim.*

---

## 1. Framing: what "slop" now means, and what it does not

The vocabulary you are asking me to operationalize crystallized in late 2025. Merriam-Webster named **"slop"** its 2025 Word of the Year, defining it as "digital content of low quality that is produced usually in quantity by means of artificial intelligence" (**HIGH**; lexicographic primary source corroborated by NBC, CNN, CBS, Smithsonian). The choice matters for your purpose because it fixes the term's two load-bearing components: *low quality* and *mass production*. Slop is not merely "made by AI" — it is AI output whose volume and indifference to correctness are the defining features.

The most useful scholarly decomposition comes from the software-engineering literature, where Baltes, Cheong, and Treude ("An Endless Stream of AI Slop," arXiv:2603.27249, March 2026, primary qualitative research) adopt **Kommers et al.'s three prototypical properties of AI slop**: *superficial competence* (a veneer of quality belied by a deeper lack of substance), *asymmetry of effort* (creation requires vastly less labor than detection or correction), and *mass producibility* (**MEDIUM**; single primary source, but the framing is convergent with the lexicographic definition). The related coinage **"workslop"** — AI content that looks like work but offloads cognitive cost onto the recipient — comes from Niederhoffer et al. via *Harvard Business Review* (September 2025, practitioner/industry). These three properties are the conceptual spine of any figure rubric: a figure "screams AI" precisely when it presents *superficial competence* — polished rendering — that collapses under inspection into *substantive incorrectness*, at a level of effort asymmetry that a careful human author would not have tolerated.

A critical distinction, and the single most common error in this discourse, is the conflation of **chartjunk** with **AI generation**. They are orthogonal. Tufte's classical framework — the *data-ink ratio* (the proportion of a figure's ink devoted to non-redundant data) and *chartjunk* (decorative non-data ink: moiré vibration, heavy gridlines, 3-D effects, "ducks") — is a normative aesthetic theory from the 1980s (**HIGH**, canonical). It predates generative AI by four decades and describes a stylistic failure mode of *human* designers. Crucially, the empirical literature has substantially qualified Tufte's prescription: Bateman et al.'s "Useful Junk?" (CHI 2010, primary experimental research) found that interpretation *accuracy* for heavily embellished "Nigel Holmes-style" charts was **no worse** than for minimalist charts, and that **long-term recall (2–3 weeks) was significantly better** for the embellished versions (**HIGH**; primary study, replicated in spirit by Li & Moacdieh 2014). The "Goldilocks" practitioner argument (scienceux.org) extends this: some decoration aids comprehension, and minimalism is not automatically ideal (**LOW–MEDIUM**, practitioner synthesis of primary work).

The operational consequence is sharp: **decorative excess is weak evidence of AI authorship.** A cluttered, over-styled chart may be slop, or it may be a perfectly intentional human infographic in the Holmes tradition. The features that genuinely *discriminate* AI generation are not aesthetic richness but **failures of semantic, symbolic, and physical integrity** — the things a competent human, regardless of taste, would not produce. The rubric in Section 6 is built around that discrimination, and deliberately down-weights pure decoration.

---

## 2. Three classes of visual, three different failure signatures

The visual features that signal AI generation differ fundamentally across three media. Treating them as one category is the main reason naïve "AI detectors" misfire. I separate them throughout.

```
                    │ Generation method      │ Dominant AI tell
────────────────────┼────────────────────────┼──────────────────────────────
A. Generated        │ Diffusion / text-to-   │ Garbled text, impossible
   illustrations    │ image (Midjourney,     │ anatomy/topology, fabricated
   & schematics     │ DALL·E, Sora-image)    │ symbols — categorical
────────────────────┼────────────────────────┼──────────────────────────────
B. Data charts      │ LLM code-gen or LLM    │ Encoding-data mismatch:
   & plots          │ "design"; chart-gen    │ numbers ≠ geometry; correct
                    │ agents                 │ look, wrong values — covert
────────────────────┼────────────────────────┼──────────────────────────────
C. Photographic     │ GAN / diffusion of     │ ABSENCE of normal manipulation
   scientific       │ blots, gels,           │ markers; over-smoothness; no
   images           │ microscopy             │ duplicated background — subtle
```

### Class A — Generated illustrations and schematics (the "rat" genre)

This is the most florid and best-documented category, and the source of the canonical cautionary tale. In February 2024, *Frontiers in Cell and Developmental Biology* published Guo et al. with Midjourney-generated figures, including a rat with grossly impossible anatomy and a "JAK-STAT signaling pathway" diagram composed entirely of fabricated glyphs; the paper was retracted within days (**HIGH**; documented by Elisabeth Bik's Science Integrity Digest, *Ars Technica*, *Vice*, and the retraction record). The diagnostic features were unambiguous and remain the prototype tells for this class:

The figures carried **gibberish text** — labels like "*testtomcels*," "*dissilced*," "*diƨlocttal stem ells*," and "*Tramioncatiion of 2xℇpens*" — character strings that are typographically letter-shaped but lexically void, often mixing invented diacritics and non-Latin glyphs. They showed **biological and topological impossibility** (extra or malformed structures, arrows that connect nothing to nothing, a signaling cascade that "explains how to make a donut," in Bik's phrase). And they exhibited **fabricated quantitative ornament** — axis numbers, scale bars, and units that are present as visual furniture but encode nothing.

These are *categorical* tells: a single instance of lexically void label text inside a scientific schematic is, on its own, near-conclusive evidence of uncorrected generative authorship (**HIGH** as a heuristic; the inference is strong because no competent human draftsperson produces void glyph-strings). The important corollary, repeatedly stressed in the integrity literature, is survivorship bias: the rat was caught *because* it was bad. Bik, Christopher, and others warn that more competent AI illustrations have "likely already infiltrated" the literature undetected (**MEDIUM**; expert opinion, not measured prevalence).

### Class B — Data charts and statistical plots

This is the class most relevant to your "chart slop" framing and the one where the tell is most *covert*. The defining 2025–2026 concern, voiced almost entirely in practitioner channels, is that **AI-generated charts can look entirely correct while encoding wrong data** (**MEDIUM** as a phenomenon, **LOW** on quantified frequency; sources are practitioner posts — Jana Diamond, Feb 2026; Allie Miller; Eugene Woo of Vizzly/practitioner commentary). The reported failure modes:

Bar heights, pie-slice angles, or point positions that **do not match the numeric labels** printed on them; pie charts whose slices **do not sum to 100%**; axis tick labels that render as **raw sequence indices** (1, 2, 3 …) instead of the intended categories; legends that reference series **not present** in the plot or vice versa; and decorative default styling (gratuitous 3-D, redundant dual axes, rainbow palettes) inherited from a model's training distribution. The deeper category — and the one that should worry a quantitative reviewer most — is the **plausible-but-false data story**: a chart that is internally consistent and well-styled but visualizes hallucinated or mis-aggregated numbers.

Note the asymmetry with Class A. Here the rendering is competent (often *more* polished than a hand-made figure), so the tell is not in the pixels but in the **encoding contract** between stated numbers and visual geometry. This is why detection requires arithmetic verification, not image forensics. As of mid-2026 there is, to my knowledge, **no peer-reviewed metric standard** specifically for AI-generated *data* charts — the space is practitioner heuristics plus the newly extended commercial tooling described in Section 3 (**MEDIUM**; absence-of-evidence, flagged as a genuine gap).

### Class C — Photographic scientific images (blots, gels, microscopy)

This is the hardest case and the one where your domain expertise is most load-bearing. The integrity literature (Kwon, *Nature* 635:268–269, Nov 2024, journalistic review of expert practice; corroborated by Proofig/ImageTwin technical material) makes a counterintuitive point: AI-generated photographic figures are hard to detect *precisely because they lack the traditional markers of manipulation* (**HIGH** within the integrity community). Classic forensic tells — duplicated backgrounds (the signature of the Tadpole Paper Mill Western blots), copy-move clone stamps, sharp splice discontinuities, repeated noise patches — are *artifacts of editing existing images*. A blot synthesized de novo by a diffusion model has none of them: every pixel is "original," the background is plausibly non-repeating, and the result can be "convincingly real" (Jana Christopher, image-integrity specialist, quoted in Kwon).

The residual tells here are subtle and probabilistic: unnatural **over-smoothness** or texture regularity, **frequency-domain** signatures (diffusion models historically suppressed high-frequency content and left characteristic spectral fingerprints, though 2025–2026 generators have "drastically reduced visible frequency artifacts," per arXiv:2511.00352, primary), and physically implausible **signal-to-noise** uniformity across a panel. Detection at this level is now a machine-forensics problem, not a human-eye problem, which sets up Section 3.

---

## 3. The state of detection tooling, mid-2026

Three things are simultaneously true in 2026, and a good rubric must hold all three.

**First, commercial integrity tooling has moved aggressively into figures.** Proofig AI reports a microscopy AI-generation detector with a claimed **98% success rate and low false-positive rate** (vendor claim, Nov 2024 — **MEDIUM/LOW**, unverified by independent benchmark), and as of **1 June 2026** extended panel-level duplication/plagiarism detection to **graphs, charts, diagrams, and plots**, backed by a 155M-image PubMed Open Access comparison corpus (vendor claim — **MEDIUM**). This is the first major tool to screen *data* figures rather than only life-science imagery, and it operates at the **individual panel level** inside composite figures — relevant because reused-with-relabeled-axes is exactly the Class B reuse pattern. ImageTwin occupies the adjacent niche (cross-checking against published-literature databases). Major publishers (MDPI, plus Aries/LabArchives/Turnitin workflow integrations) have signed on through 2025–2026 (vendor announcements — **MEDIUM**).

**Second, every serious source insists detection tools are advisory, not dispositive.** Christopher and the EASE/Nature line are explicit: tool outputs "will always need to be assessed by an expert who can verify the issues they flag" (**HIGH**; consistent across integrity bodies). The proposed durable countermeasure is provenance, not post-hoc detection — **watermarking raw instrument images** at acquisition (**MEDIUM**; proposed, not yet standard).

**Third, the tells are decaying.** *Forbes* (Feb 2026, practitioner) and multiple forensic papers converge on the thesis that "detection will always lag generation" and that the obvious 2023-era giveaways are "mostly gone" (**MEDIUM**). The Frontiers rat is a 2024 specimen; its equivalents in 2026 are quieter. This is the central reason your rubric should weight **categorical integrity failures** (which remain decisive when present) above **soft stylistic signals** (which are eroding and false-positive-prone), and should treat a *clean* score as "no positive evidence of AI," never as "confirmed human."

---

## 4. What the evidence does and does not support

Synthesizing across the corpus, here is where I would and would not stake claims for a peer audience.

**Well supported (HIGH):** that "slop" is a defined, mainstreamed concept with low-quality-at-scale as its core; that garbled lexically-void text inside a figure is a near-categorical AI tell; that the Frontiers retraction happened and exemplifies Class A; that classical chartjunk is an aesthetic construct distinct from AI authorship, and that embellishment per se does not impair (and may aid) memorability; that AI-synthesized photographic figures evade traditional manipulation forensics; that human expert adjudication remains necessary.

**Moderately supported (MEDIUM):** Kommers' three-property decomposition; the prevalence claim that competent AI figures already pervade the literature undetected; the specific capabilities and accuracy figures of Proofig/ImageTwin (these are vendor self-reports); the "encoding-mismatch" failure catalog for data charts.

**Weakly supported / speculative (LOW):** quantified base rates for any of these tells; the reliability of any single soft signal (over-smoothness, palette, spectral fingerprint) in 2026 against current-generation models; practitioner claims about chart error frequency, which are anecdotal. A genuine gap: **no peer-reviewed, validated metric instrument** exists specifically for scoring AI-tells in *data charts* as of mid-2026. The rubric below is therefore a *constructed* instrument synthesizing the above, not a validated scale — it needs calibration on a labeled corpus before any quantitative threshold is trusted.

---

## 5. Design logic of the rubric

The rubric separates **categorical tells** (a single confirmed instance is near-decisive — primarily Class A symbolic/physical failures) from **graded signals** (each shifts probability but none is conclusive). It scores six dimensions, deliberately ordering them so that the highest-confidence discriminators (text/symbol integrity, quantitative correctness, physical plausibility) carry the most weight, and the erosion-prone, false-positive-prone aesthetic dimension carries the least. Each metric is written to be **observable** — a second reviewer should reach the same score from the same figure — per the spirit of Tufte-style operational definition and your own figure-evaluation practice.

Scoring is 0–2 per metric (0 = clean / no evidence, 1 = ambiguous / mild, 2 = clear tell), except categorical metrics which are flagged ⚑ and, if scored 2, should dominate the verdict regardless of the aggregate. Not every metric applies to every figure; mark non-applicable metrics N/A and renormalize.

---

## 6. The AI-Figure Integrity Rubric (v0.1)

### Dimension 1 — Text & symbol integrity ⚑ *(strongest discriminator; mainly Class A)*

| # | Metric | What to look for | 0 / 1 / 2 anchors | Source basis |
|---|--------|------------------|-------------------|--------------|
| 1.1 ⚑ | **Lexical validity of labels** | Are axis labels, legend entries, callouts real words/terms? | 0 = all valid; 1 = ≥1 misspelling consistent with typo; 2 = lexically void glyph-strings ("*diƨlocttal*") | Frontiers/Bik (HIGH) |
| 1.2 ⚑ | **Glyph/character integrity** | Invented diacritics, melted letters, mixed scripts, non-Unicode shapes | 0 = clean; 1 = isolated odd glyph; 2 = systematic malformed characters | Frontiers/Bik (HIGH) |
| 1.3 | **Symbol/notation correctness** | Are domain symbols (→, ⊣, gene italics, units) used coherently? | 0 = correct; 1 = inconsistent; 2 = decorative/nonsensical notation | Frontiers/Bik (HIGH) |
| 1.4 | **Number plausibility in text** | Do printed numbers/units have sane magnitudes & dimensions? | 0 = plausible; 1 = odd; 2 = impossible units / fabricated precision | Class A synthesis (MEDIUM) |

### Dimension 2 — Quantitative & semantic correctness *(strongest discriminator for Class B)*

| # | Metric | What to look for | 0 / 1 / 2 anchors | Source basis |
|---|--------|------------------|-------------------|--------------|
| 2.1 ⚑ | **Encoding–value fidelity** | Do bar heights / slice angles / point positions match the printed values? | 0 = match; 1 = minor mismatch; 2 = geometry contradicts labels | Practitioner (Woo, Miller) (MEDIUM/LOW) |
| 2.2 ⚑ | **Closure / conservation** | Do parts-of-whole sum to 100%? Do stacked totals reconcile? | 0 = closes; 1 = rounding-level gap; 2 = fails to sum | Practitioner (LOW) |
| 2.3 | **Axis–data coherence** | Tick labels are real categories, not raw indices (1,2,3…); scale type fits data | 0 = coherent; 1 = suboptimal; 2 = index-as-label / wrong scale | Practitioner (LOW) |
| 2.4 | **Legend–series correspondence** | Every legend entry maps to a drawn series and vice versa | 0 = 1:1; 1 = cosmetic mismatch; 2 = orphaned/missing series | Practitioner (LOW) |
| 2.5 | **External data verification** | Do the numbers match a cited/known source when checkable? | 0 = verified; 1 = uncheckable; 2 = contradicts source | Slop "superficial competence" (MEDIUM) |

### Dimension 3 — Physical, biological & logical plausibility *(Class A & C)*

| # | Metric | What to look for | 0 / 1 / 2 anchors | Source basis |
|---|--------|------------------|-------------------|--------------|
| 3.1 ⚑ | **Anatomical/structural realism** | Domain structures have correct count, proportion, topology | 0 = correct; 1 = stylized but valid; 2 = impossible anatomy | Frontiers/Bik (HIGH) |
| 3.2 | **Process/pathway logic** | Arrows, flows, cascades connect meaningful entities in valid order | 0 = valid; 1 = oversimplified; 2 = arrows to/from nothing | Frontiers/Bik (HIGH) |
| 3.3 | **Spatial/optical consistency** | Lighting, shadow, perspective, scale internally consistent | 0 = consistent; 1 = minor; 2 = contradictory physics | Diffusion forensics (MEDIUM) |
| 3.4 | **Continuity of repeated elements** | Repeated motifs (cells, ticks, gridlines) stay self-consistent | 0 = consistent; 1 = drift; 2 = morphing/melting | Diffusion forensics (MEDIUM) |

### Dimension 4 — Render & signal artifacts *(Class C; probabilistic, decaying)*

| # | Metric | What to look for | 0 / 1 / 2 anchors | Source basis |
|---|--------|------------------|-------------------|--------------|
| 4.1 | **Texture/noise naturalness** | Camera/instrument noise random vs. unnaturally smooth or regular | 0 = natural; 1 = suspicious; 2 = synthetic smoothness | Diffusion forensics (MEDIUM) |
| 4.2 | **Absence of expected manipulation markers** | For a *claimed* edited/real photo, are normal artifacts present? (paradoxical tell) | 0 = normal markers; 1 = unusually clean; 2 = implausibly pristine de-novo look | Kwon/Christopher (HIGH within community) |
| 4.3 | **Frequency-domain fingerprint** | Spectral analysis / detector flags (tool-assisted) | 0 = none; 1 = weak; 2 = strong detector flag | arXiv:2511.00352 (MEDIUM) |

*Dimension 4 should be scored with a tool (Proofig/ImageTwin/forensic detector) and an explicit note that 2026-generation models may pass it cleanly. Do not treat 4.x = 0 as exoneration.*

### Dimension 5 — Provenance & metadata

| # | Metric | What to look for | 0 / 1 / 2 anchors | Source basis |
|---|--------|------------------|-------------------|--------------|
| 5.1 | **Disclosure consistency** | Does stated methods/AI-use disclosure match what the figure shows? | 0 = consistent; 1 = silent; 2 = undisclosed generation evident | EASE recommendations (MEDIUM) |
| 5.2 | **File/EXIF & vector provenance** | Native vector vs. flattened raster; generator metadata; resolution sanity | 0 = clean provenance; 1 = stripped; 2 = generator signature/C2PA flag | Tooling practice (MEDIUM) |
| 5.3 | **Reuse / panel duplication** | Panel matches published corpus with altered labels | 0 = none; 1 = similar; 2 = confirmed match | Proofig charts release (MEDIUM) |

### Dimension 6 — Stylistic "slop" markers *(weakest discriminator — down-weight)*

| # | Metric | What to look for | 0 / 1 / 2 anchors | Source basis |
|---|--------|------------------|-------------------|--------------|
| 6.1 | **Gratuitous decoration vs. data-ink** | Non-data ink that obscures rather than aids (3-D, moiré, heavy chrome) | 0 = lean; 1 = busy; 2 = obscuring | Tufte (HIGH) — *but see caveat* |
| 6.2 | **Template/default-distribution look** | Generic model-default palette, font, layout regardless of content | 0 = bespoke; 1 = generic; 2 = unmistakable default | Slop mass-producibility (MEDIUM) |
| 6.3 | **Effort asymmetry signal** | Polish-to-substance imbalance: high gloss, thin meaning | 0 = balanced; 1 = mild; 2 = veneer over emptiness | Kommers/Baltes (MEDIUM) |

**Caveat carried in the instrument:** Dimension 6 is included because it captures the *aesthetic* of slop, but Bateman et al. (HIGH) show embellishment alone does not impair comprehension and can aid recall — so 6.1/6.3 must never trigger an "AI" verdict on their own. They are corroborating texture, not evidence.

---

## 7. Scoring, aggregation, and verdict logic

```
STEP 1  Score each applicable metric 0/1/2; mark others N/A.
STEP 2  CATEGORICAL OVERRIDE — if any ⚑ metric = 2  ─────────►  "Strong AI/slop tell"
        (1.1,1.2,2.1,2.2,3.1)                                    regardless of total.
STEP 3  Else compute weighted index:
            D1 ×3   D2 ×3   D3 ×2   D4 ×1   D5 ×2   D6 ×1
        Normalize to 0–100 over applicable metrics only.
STEP 4  Bands (provisional, UNCALIBRATED):
            0–15   No positive evidence of AI authorship
            16–40  Weak signals — flag for closer human review
            41–70  Multiple converging tells — request source data/provenance
            71–100 Strong slop profile — treat as AI-generated pending rebuttal
```

Two interpretive rules belong on the face of the instrument. **A clean score is not proof of human authorship** — given tell decay (Section 3), absence of evidence is weak evidence of absence. And **the burden the score supports is "obtain raw data / provenance / author response," not "conclude misconduct"** — the rubric triages attention; adjudication stays human, consistent with every integrity body in the corpus.

---

## 8. Recommended next steps to turn v0.1 into a validated instrument

The honest limitation is that this is a synthesized rubric, not a psychometrically validated scale, and the data-chart half of it rests on practitioner anecdote because the peer-reviewed literature has not yet caught up to Class B. To harden it I would: assemble a **labeled corpus** of known-AI and known-human figures across the three classes (the retraction record, PubPeer, and your own field's figures are natural sources); compute **inter-rater reliability** (Cohen's/Fleiss' κ) on the 0/1/2 anchors and tighten any metric below κ ≈ 0.6; calibrate the band thresholds and per-dimension weights against the labels rather than my a priori 3-3-2-1-2-1 scheme; and benchmark Dimension 4 against an external forensic detector to quantify how much it has decayed against 2026-generation models. That validation step is exactly where your experimental-design instincts will matter more than the literature does.

---

## Sources

**Primary research**
- Baltes S., Cheong M., Treude C. "An Endless Stream of AI Slop: The Growing Burden of AI-Assisted Software Development." arXiv:2603.27249 [cs.SE], Mar 2026. https://arxiv.org/abs/2603.27249
- Bateman S. et al. "Useful Junk? The Effects of Visual Embellishment on Comprehension and Memorability of Charts." CHI 2010. https://vis.csail.mit.edu/classes/6.859/readings/pdfs/Bateman-UsefulJunk.pdf
- "Detecting AI-Generated Images via Diffusion Snap-Back." arXiv:2511.00352, 2025. https://arxiv.org/html/2511.00352v1
- Giray L., Sevnarayan K., Maphoto K.B., Wider W. "AI Slop in Academic Publishing: History, Characteristics, Manifestations, Causes, and Mitigation Strategies." *Internet Reference Services Quarterly*, Mar 2026. https://www.researchgate.net/publication/401618720

**Review / journalistic**
- Kwon D. "AI-generated images threaten science — here's how researchers hope to spot them." *Nature* 635(8038):268–269, Nov 2024. https://doi.org/10.1038/d41586-024-03542-8 (summary via EASE: https://ease.org.uk/2025/02/ai-generated-images-threaten-science-heres-how-researchers-hope-to-spot-them/)
- "Resisting AI slop." *Science*, 2026. https://www.science.org/doi/10.1126/science.aee8267

**Integrity reporting / practitioner**
- Bik E. "The rat with the big balls… how Frontiers published a paper with botched AI-generated images." Science Integrity Digest, Feb 2024. https://scienceintegritydigest.com/2024/02/15/the-rat-with-the-big-balls-and-enormous-penis-how-frontiers-published-a-paper-with-botched-ai-generated-images/
- *Ars Technica*, "Scientists aghast at bizarre AI rat…" Feb 2024. https://arstechnica.com/science/2024/02/scientists-aghast-at-bizarre-ai-rat-with-huge-genitals-in-peer-reviewed-article/
- Woo E. "How AI Can Create Misleading and Distorted Graphs (And How to Spot Them)." LinkedIn, 2025. https://www.linkedin.com/pulse/how-ai-can-create-misleading-distorted-graphs-spot-them-eugene-woo-ajtle

**Vendor / tooling**
- Proofig AI, "Image Integrity Moves Beyond the Life Sciences: Proofig AI Now Detects Graphs, Charts, Diagrams, and Plots." 1 Jun 2026. https://www.proofig.com/news/image-integrity-moves-beyond-the-life-sciences-proofig-ai-now-detects-graphs-charts-diagrams-and-plots/
- Proofig AI, "How AI Is Fighting Back Against AI-Generated Image Fraud." Nov 2024. https://www.proofig.com/news/how-ai-is-fighting-back-against-ai-generated-image-fraud-in-scientific-research/
- ImageTwin AI. https://imagetwin.ai/

**Reference / lexicographic**
- Merriam-Webster, "Word of the Year 2025: Slop." https://www.merriam-webster.com/wordplay/word-of-the-year (corroborated: NBC, CNN, CBS, Smithsonian, Dec 2025)
- Tufte E. *The Visual Display of Quantitative Information* (data-ink ratio, chartjunk), canonical. Origins summary: https://data.europa.eu/apps/data-visualisation-guide/chart-junk-and-data-ink-origins
