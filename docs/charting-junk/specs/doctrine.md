I have everything I need. The "Used by" list in the sibling docs covers the visual skills; the task specifies 7 visual skills. Based on the repo, the visual skills are: svg-figure-maker, plotting-libraries, scientific-schematics, research-posters, venue-templates, paperbanana, generate-image (and scientific-slides for figure-bearing decks). I'll use the 7 figure-generating skills.

Here is the complete file content:

# AI Figure Slop — Regression-to-Mean Tells & Integrity Guardrail (Shared)

> Canonical doctrine for detecting "AI figure slop" in figures this plugin **generates** and (advisory-only) in figures it **audits**. Sibling to `figure_design_principles.md`.
> Version: 1.0.0
> Status: canonical
>
> **Used by:** svg-figure-maker, plotting-libraries, scientific-schematics, research-posters, paperbanana, generate-image, venue-templates. (peer-review and research-accuracy-verifier consume the §5 forward-pointers for inbound audit; they do not own this doctrine.)
>
> **Scope:** *Why* AI-generated figures fail, *which* failures are decisive vs. cosmetic, and *how* this plugin catches them cheaply against the data + source it already holds. This doc is the conceptual spine; the mechanized checks, the vision-QA checklist, and the inbound rubric live in the skills/scripts named in §5.
>
> **What does NOT belong here:** the deterministic linter algorithms (own home: `svg-figure-maker/scripts/preflight_check.py`, `plotting-libraries/scripts/validate_data.py` / `validate_figure.py`); the 15-point submission gate (`pre_submission_checklist.md`); general perception/composition principles (`figure_design_principles.md`); brand palette tokens (`oligon-brand/tokens/brand-tokens.json`); the inbound forensic/OCR/rubric stack (Track D, owned by `peer-review`); per-venue specs (`venue-templates/references/figure_specs.md`).

---

## How to use this document

- Skills' `<cross_references>` blocks point here when a figure must be screened for regression-to-mean tells, **in addition to** the design principles in `figure_design_principles.md`.
- Workflows say "READ §N before proceeding" inline at the stage where a figure is about to be emitted (after rendering, before delivery).
- This doc supplies *doctrine and a tell catalog*; the enforcing code lives in the §5 scripts and consumes the same tell names defined here in §3.
- **Two non-negotiable guardrails** govern everything below — read them before the sections:

### Guardrail 1 — Emit a vector, never a composite "slop score"

Output is always a **vector of flagged sub-scores with severities** (which tell fired, on what evidence, at what confidence), never a single aggregate number. A composite invites a magic threshold; figure integrity has no such threshold. All numeric cutoffs in this doc and its enforcing scripts are **PROVISIONAL and UNCALIBRATED** — the source rubric (`docs/charting-junk/ai-figure-slop-evaluation-2026-06-09.md` §7) is "a constructed instrument synthesizing the above, not a validated scale," with no labeled-corpus calibration and no inter-rater reliability yet established. Treat every band, weight, and tolerance as a starting hypothesis.

### Guardrail 2 — Categorical tells dominate; aesthetic signals are weak and two-sided

**Categorical tells** (lexically-void labels, glyph malformation, encoding-vs-printed-value mismatch, parts-not-summing-to-whole, impossible anatomy) are near-decisive when present and dominate the verdict regardless of any aggregate. **Aesthetic / chartjunk signals** (decoration density, default palette, "generic" layout) are WEAK, heavily DOWN-WEIGHTED, and **TWO-SIDED**: they corroborate at most, never conclude. Per Bateman et al. (CHI 2010), embellishment alone does **not** impair comprehension and **improves** long-term recall — so this plugin must never instruct the model to strip decoration or minimize ink as a slop remedy. **Over-minimization into sterile, default-tool minimalism is itself a regression-to-mean failure** (§4).

---

## §1. Provenance ≠ quality

For the figures this plugin **generates**, the question "is this AI-made?" is not just hard — it is **moot**. Of course it is AI-made; we made it. Provenance carries no quality signal in either direction (source rubric §1: "decorative excess is weak evidence of AI authorship"; integrity bodies in Kwon 2024 stress provenance is "advisory, not dispositive"). What actually matters is whether a figure exhibits **regression-to-mean tells**: the artifacts of a generator collapsing toward its training-distribution default instead of executing bespoke intent.

This reframing has a hard architectural consequence that the rest of the plugin is built on:

> **We hold ground truth.** Because we generate the figure, we already possess the source data and the source SVG / plotting code. The source reports' unreliable step — recovering data *back out* of a rendered image via OCR or forensic CV — is **unnecessary for our own output**. SciFigDetect (cited in `docs/charting-junk/Chart_slop_claude.md`) shows those recovery methods fail zero-shot; we do not need them. Replace image→data recovery with **cheap, exact, deterministic checks against the data and source we already own.**

So "slop detection" for our outputs is not forensics. It is verifying the **encoding contract**: does the geometry we drew match the numbers we were given? Are the labels the strings we were handed, or did the renderer invent glyphs? Did the palette come from intent or from `import matplotlib`? These are exact comparisons, not probabilistic image judgments.

Only the **inbound-audit track** (Track D — figures arriving from outside, with no source data) needs the forensic / OCR / rubric stack. There it stays **advisory and triage-only, never dispositive** (§5).

---

## §2. The three orthogonal axes

The source framework (`docs/charting-junk/Chart_slop_claude.md`) decomposes figure quality into three **orthogonal** axes. Two of them are already covered by existing canon — this doc points there rather than re-deriving — and adds the third, which is genuinely new.

| Axis | One-line definition | Where it lives |
|---|---|---|
| **A. Graphical integrity** | Does the figure's visual claim faithfully represent the data (zero baselines, honest scales, shown uncertainty, no 3D distortion)? | **Already canonical** — `oligon-brand/SKILL.md` `<figure_integrity>` "Twelve Rules" + `figure_design_principles.md` §7 anti-patterns. Do not re-derive; point here. |
| **B. Data-ink economy** | Is non-data ink in service of the takeaway, or noise — judged by Fujii's signal-to-noise reframing, **not** mechanical data-ink maximization? | **Already canonical** — `figure_design_principles.md` §7 row 14 + `oligon-brand/SKILL.md` `<design_foundation>` "Universal design pitfalls." **Two-sided** (see §4): more ink can be correct. |
| **C. Generative-artifact credibility** | Are the *generation-specific* artifacts absent — no garbled glyphs, no encoding-value mismatch, no parts-not-summing, no impossible anatomy, no tool-default fingerprint? | **NEW — this doc owns it.** §3 catalogs the tells; §4 catalogs the regression-to-mean defaults. |

The three are orthogonal: a figure can have perfect graphical integrity (Axis A) and lean data-ink (Axis B) yet still scream "generated" because its labels are lexically void (Axis C). Conversely, a busy, embellished figure (low on a naïve Axis-B reading) can be fully credible on Axis C. **Never collapse these axes into one score** (Guardrail 1).

---

## §3. Categorical vs. graded tells

The single most important distinction (source rubric §5): **categorical** tells are near-decisive on a single confirmed instance; **graded** tells each shift probability but none concludes. Because we own the data and source, our catch method is usually an **exact deterministic check**, not a CV/LLM judgment — and that is what makes our confidence high where the source reports could only manage "MEDIUM/LOW practitioner anecdote."

Legend: **Class** A = generated illustration/schematic, B = data chart/plot, C = photographic. **Confidence** = our confidence *given we hold the source*, which is higher than the source reports' confidence in the open-audit case.

| Tell | Class | Category vs. graded | How WE catch it cheaply (data/SVG we own) | Confidence |
|---|---|---|---|---|
| **Lexically-void / garbled labels** ("*diƨlocttal*", "*testtomcels*") | A, B | **Categorical ⚑** | Exact set-membership: every rendered `<text>` / tick / legend string must be ∈ the source label set we passed in. Any string not in that set, or failing a dictionary/term + Unicode-script check, fires. We never OCR — we compare to the strings we authored. | **High** (exact for our output) |
| **Glyph malformation** (invented diacritics, mixed scripts, melted letters) | A | **Categorical ⚑** | For SVG: assert every char in `<text>` is in an allowed Unicode block; flag private-use / non-Latin / combining-diacritic anomalies. For raster (generate-image/paperbanana): vision-QA checklist item (§5 Track C). | **High** for SVG; **Medium** for raster |
| **Encoding-vs-printed-value mismatch** (bar height ≠ its printed number) | B | **Categorical ⚑** | Exact arithmetic: recompute geometry (bar pixel-height, slice angle, point y) from the source data + axis transform we used, compare to both the drawn geometry and the printed data label. Tolerance is a rounding epsilon, not a judgment. | **High** (we own the transform) |
| **Parts-not-summing-to-100 / stacked totals don't reconcile** | B | **Categorical ⚑** | Exact arithmetic on source data: Σ(parts) vs. whole within rounding epsilon, before rendering. A pie/stacked/100%-bar whose source series doesn't close is rejected at the data gate. | **High** (pure arithmetic) |
| **Impossible anatomy / topology** (extra limbs, arrows to nothing, donut "pathway") | A | **Categorical ⚑** | Not deterministically catchable from source for free-form illustration — routed to vision-QA (§5 Track C) and, for schematics, to graph-validity checks (every arrow has a real source+target node). | **Medium** (vision-assisted) |
| **Raw-index axis labels** (ticks read 1, 2, 3… instead of category names) | B | Graded → categorical if source had names | Exact: if the source data supplied category labels, assert the rendered tick text equals them, not `range(n)`. Firing is deterministic when we know names existed. | **High** when names known |
| **Legend–series mismatch** (legend entry with no drawn series, or vice versa) | B | Graded | Exact: count drawn series vs. legend entries from the source spec; assert 1:1 mapping by key. Orphaned/missing entries fire. | **High** (we own both) |
| **Default-library palette / template fingerprint** (tab10 `#1f77b4`→`#ff7f0e`, default seaborn theme, Excel chrome) | B | **Graded — WEAK, two-sided** | Exact hex scan of SVG/source against the known default sequences in §4; cross-check against the declared brand/project palette. Fires as a **low-severity corroborating** flag only — never alone, never dispositive (Guardrail 2). | **High** detection, **Low** weight |
| **Gratuitous 3D on 2D data** | A, B | Graded (but `<figure_integrity>` Rule 4 bans outright) | SVG/code scan for 3D-projection constructs / `feDropShadow` pseudo-depth; bevel/extrude in chart spec. Already an `<figure_integrity>` Rule-4 violation. | **High** |
| **Axis truncation on bars** (non-zero baseline exaggerating differences) | B | Graded (but `<figure_integrity>` Rule 1 bans outright) | Exact: read y-axis `vmin` from source/render; if a bar geom and `vmin ≠ 0`, fire. Already `<figure_integrity>` Rule 1 + `figure_design_principles.md` §7 row covered. | **High** |
| **Rainbow / jet on continuous data** | B | Graded (but `<figure_integrity>` Rule 5 bans outright) | Exact: detect `jet`/`rainbow`/`Spectral` colormap name in source, or sample the SVG gradient for the jet hue-cycle signature. Already `<figure_integrity>` Rule 5 + `figure_design_principles.md` §3.1 + Crameri 2020. | **High** |

Note the pattern: where the source reports must use forensic CV or LLM-judge (their Tier 2 / Tier 3) and earn only MEDIUM/LOW confidence, **we hold the source and reduce the same tell to an exact comparison at HIGH confidence.** The Tier 2/3 CV/LLM machinery is reserved for Track D inbound audit, where we genuinely lack the source.

---

## §4. The regression-to-mean catalog

This is the user's core concern made concrete. A generator "screams AI" most reliably not through exotic failure but through **lazy convergence to the tool default** — the visual mean of its training distribution. Avoid these specific defaults; prefer **bespoke intent over tool default.**

### Defaults to avoid (the visual mean)

| Default | The tell | The fix (bespoke intent) |
|---|---|---|
| **matplotlib `tab10` cycle** — `C0 = #1f77b4` (muted blue) → `C1 = #ff7f0e` (orange) → `C2 = #2ca02c` (green) → … | The single most recognizable "I ran the default" fingerprint in scientific plotting. Two series colored exactly `#1f77b4` then `#ff7f0e` is a near-signature. | Load the brand mplstyle / `set_brand_style()` (Okabe-Ito or Oligon cycle) before plotting. Covered: `figure_design_principles.md` §7 row 9. |
| **Default seaborn theme** (`darkgrid`, the muted "deep" palette, the seaborn gray panel) | Reads as "notebook output," not "publication figure." | Set an explicit theme + brand palette; remove the gray panel unless intentional. |
| **Default Excel chart styling** (gradient fills, drop-shadowed bars, the Office blue-orange-gray sequence, auto 3D) | "Pasted from a spreadsheet" — pseudo-3D and chrome violate `<figure_integrity>` Rules 4 & 1. | Re-author in matplotlib/ggplot2/SVG with flat 2D geometry and a chosen palette. |
| **Times New Roman / Calibri body defaults** | Calibri = "Office default never changed"; Times = "Word default never changed." Both `figure_design_principles.md` §2.2 *forbidden*. | `font-family="Arial, Helvetica, sans-serif"`; enforced by `preflight_check.py::check_text_font_family`. |
| **Generic "canonical pattern" layouts** (the centered-title + boxed-legend + evenly-spaced-nodes template the model reaches for regardless of content) | Layout that ignores the data's actual structure — every figure looks like the same stock template. | Lay out to the data: direct labels (§5.2 of principles doc), emphasis hierarchy, content-driven spacing. |

### The two-sided caveat — do NOT over-correct into minimalism

This is half the doctrine, and the half that naïve "slop" remediation gets wrong. **Stripping decoration is itself regression-to-mean.** Bateman et al. (CHI 2010, *primary experimental*, HIGH) found:

- interpretation **accuracy** for heavily embellished ("Nigel Holmes-style") charts was **no worse** than for minimalist charts; and
- **long-term recall (2–3 weeks) was significantly better** for the embellished versions.

So decoration that **aids comprehension or recall is good**, and forcing every figure toward sterile, gridline-free, label-stripped minimalism produces a *different* default mean — the "tasteful AI minimalism" mean — which is equally a tell. The correct frame, repeated from `figure_design_principles.md` §7 row 14 (Fujii signal-to-noise reframing):

> **Keep ink that supports the takeaway; cut ink that obscures it. Bespoke intent over tool default — but decoration that aids comprehension is fine.** Never instruct the model to "minimize ink" or "remove decoration" as a generic slop fix. (Guardrail 2.)

Concretely: a hand-drawn isotype chart, an annotated callout, a textured fill that encodes a category, or a Holmes-style mnemonic illustration are **not** slop. A `tab10`-default scatter with a boxed legend the reader must ping-pong to **is** the mean, even though it has "less ink."

---

## §5. How this is enforced

This doc is doctrine; enforcement is distributed across four tracks, each owned by other agents/scripts. These are **forward-pointers** — the detail lives at the destination.

- **Track B — deterministic gate (the exact checks of §3).** The mechanized, source-aware linters:
  - `skills/svg-figure-maker/scripts/preflight_check.py` — SVG-level (extend with: lexically-void/garbled-label check, default-palette-fingerprint scan, raw-index-label check; it does **not** check these today).
  - `skills/plotting-libraries/scripts/validate_data.py` — input-data checks; **this is where `check_continuous_as_bars` and `check_riskratio_as_bars` actually live** (not `validate_figure.py`). The closure/encoding-fidelity arithmetic of §3 belongs here, on the source data, before render.
  - `skills/plotting-libraries/scripts/validate_figure.py` — file-level production checks (DPI/format/fonts).
  - Output contract: a **vector of findings with severities** (Guardrail 1), keyed to the §3 tell names.
- **Track C — instrumented vision-QA checklist.** For raster outputs where we lack vector source (generate-image, paperbanana) and for impossible-anatomy / glyph-malformation tells that need an eye: the render→`Read`-PNG→checklist loop in `oligon-brand/SKILL.md` `<svg_output>` "Visual Preview" and `figure_design_principles.md` §9.2, extended with the §3 categorical-tell items. Vision is **assistive**, not a slop-score generator.
- **Track A3 — pre-submission gate slop items.** `skills/shared/references/pre_submission_checklist.md` carries the slop sub-checks as gate items. (Maintenance note: its items #13/#14 and tooling table currently point to `validate_figure.py::check_continuous_as_bars` / `check_riskratio_as_bars`, but those functions live in **`validate_data.py`** — fix that pointer when wiring this in.)
- **Track D — inbound-audit rubric (advisory/triage only).** For figures arriving from *outside* the plugin (peer review, accuracy verification) where we do **not** hold source data, the forensic / OCR / CV / LLM-judge / rubric stack from `docs/charting-junk/ai-figure-slop-evaluation-2026-06-09.md` (v0.1 6-dimension rubric, categorical ⚑ override) applies — owned by `skills/peer-review/` (`references/presentation_review.md`) and surfaced to `research-accuracy-verifier`. It is **advisory and triage-only, never dispositive**: a clean score is "no positive evidence," never "confirmed human," and the burden it supports is "obtain source data / provenance," never "conclude misconduct" (source rubric §7).

---

## §6. References

**Foundational visualization / perception** (full citations in `oligon-brand/SKILL.md` `<design_foundation>` and `figure_design_principles.md` §11):

- Tufte E. 2001 *The Visual Display of Quantitative Information* (2nd ed., Graphics Press) — data-ink ratio, chartjunk; **note the empirical qualification below.**
- Cleveland & McGill 1984 *J Am Stat Assoc* **79**(387) — elementary perceptual-task ranking (position > length > angle > area > hue); underpins encoding choices.
- Crameri, Shephard & Heron 2020 *Nat Commun* **11**, 5444 — perceptually uniform / CVD-safe colormaps; the authority behind "no jet/rainbow on continuous data."

**The two-sided / "useful junk" evidence** (Guardrail 2):

- Bateman S. et al. 2010 "Useful Junk? The Effects of Visual Embellishment on Comprehension and Memorability of Charts." *CHI 2010* — embellishment did not impair accuracy and improved 2–3-week recall. Primary experimental, HIGH. The reason this plugin never strips decoration as a slop fix.
- Li & Moacdieh 2014 — replication-in-spirit of the embellishment-vs-clutter trade-off (MEDIUM).

**AI-slop concept & integrity literature:**

- Merriam-Webster 2025 *Word of the Year: "Slop"* — "low-quality content produced in quantity by AI"; fixes the two load-bearing components (low quality + mass production).
- Kommers et al. (via Baltes, Cheong, Treude, "An Endless Stream of AI Slop," arXiv:2603.27249, Mar 2026) — three properties: *superficial competence*, *asymmetry of effort*, *mass producibility*. MEDIUM.
- Niederhoffer et al. 2025 (*Harvard Business Review*) — "workslop" (looks like work, offloads cognitive cost to the recipient). Practitioner.
- Giray L. et al. 2026 "AI Slop in Academic Publishing." *Internet Reference Services Quarterly*. Review.
- Bik E. 2024 "The rat with the big balls…" Science Integrity Digest; *Ars Technica*, Feb 2024 — the **Frontiers rat** retraction: lexically-void labels ("*testtomcels*", "*diƨlocttal stem ells*") + impossible anatomy as the prototype **categorical** Class-A tells. HIGH as heuristic.
- Kwon D. 2024 "AI-generated images threaten science." *Nature* **635**:268–269 — synthesized photographic figures evade *traditional* manipulation forensics (no duplicated background); detection is advisory, provenance is the durable countermeasure. HIGH within integrity community.

**Computable-metric frameworks** (Track D / inbound, owned by `peer-review`; see `docs/charting-junk/Chart_slop_claude.md`):

- **Misviz** — misleading-visualization linter keyed to axis metadata.
- **VisEval** — validity / legality / readability scoring (0.843 SRCC with human judgment).
- **RealChart2Code** — Syntax / Layout / Data-Mapping / Instruction-Neglect error taxonomy; 8-criterion voting rubric.
- **Draco** — visualization-design constraints as logic (Cleveland-McGill encoded as soft constraints).
- **SciFigDetect** — evidence that zero-shot image→data recovery / forensic CV **fails**; the basis for §1's "we own the source, skip the forensics" principle.
- Tiered scorer (Tier 1 deterministic rules / Tier 2 CV / Tier 3 LLM-judge) — Tiers 2–3 reserved for Track D where source data is absent.

**Detection-decay & forensics context:**

- "Detecting AI-Generated Images via Diffusion Snap-Back," arXiv:2511.00352, 2025 — 2026-generation models "drastically reduced visible frequency artifacts"; why soft/forensic signals are decaying and must not be dispositive.
- Proofig AI (1 Jun 2026) — panel-level duplication detection extended to graphs/charts/diagrams (vendor claim, MEDIUM); the first tool screening *data* figures, relevant to Track D reuse checks.

**Provisional-instrument provenance:**

- `docs/charting-junk/ai-figure-slop-evaluation-2026-06-09.md` — the v0.1 6-dimension / 0-1-2-anchor rubric with categorical ⚑ override; **explicitly a constructed, uncalibrated instrument** (no labeled corpus, no inter-rater reliability) — the source of every "PROVISIONAL / UNCALIBRATED" caveat in this doc.