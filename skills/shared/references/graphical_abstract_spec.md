# Graphical Abstract Design Spec — Element, Text, and Thumbnail Budgets

> Design definition for graphical abstracts: how many elements, how much text, and what has to stay legible once the figure is rendered as a table-of-contents thumbnail.
> Version: 1.0.0
> Used by: paperbanana, scientific-schematics, svg-figure-maker, venue-templates
>
> **Design, not format.** Dimensions, DPI, maximum file size, accepted file formats, font-point floors, and which venues use a graphical abstract at all live in `../venue-templates/references/figure_specs.md` §1. This file never restates them.

---

## Scope

A graphical abstract is not a shrunken figure. It is a different deliverable with a different job: it competes for attention in a contents listing against a title and an author list, and it is handled by an editor before it is ever read by a scientist. That job constrains element count, text volume, and label size far more tightly than any journal format sheet does — and the format sheet says nothing about any of it.

Two gates precede everything below:

1. **Confirm the venue uses one.** Most venues do not. Run the pre-design check in `../venue-templates/references/figure_specs.md` §1 before designing anything; a square graphical abstract built for a journal that does not accept one is wasted work.
2. **Confirm the viewing context.** The graphical abstract row of `communication_context_matrix.md` sets the complexity envelope — seconds to interpret, zero interaction, mixed audience of browsing readers and handling editors.

---

## Element budget

`figure_design_principles.md` §5.4 sets complexity ceilings for a figure read at full size, for minutes, by a reader who has already decided to engage. A graphical abstract gets none of those conditions. It therefore inherits §5.4 **tightened by one step: what §5.4 treats as a soft cap is a hard cap here.**

| Element | GA soft cap | GA hard cap | Derivation from §5.4 |
|---|---|---|---|
| Diagram nodes | 5 | 7 | §5.4's soft cap becomes the GA hard cap |
| Arrows / connectors | 6 | 9 | §5.4's soft cap becomes the GA hard cap |
| Simultaneous encoded dimensions | 2 | 3 | §5.4's soft cap becomes the GA hard cap |
| Focal accent elements | 1 | 1 | §5.4 permits a second accent; a graphical abstract makes one claim, so it gets one accent |
| Categorical color series | 3 | 5 | **Departs from the rule above.** §5.4's 7/8 assumes full-size viewing; a thumbnail cannot hold that many hues apart (see Thumbnail legibility) |

Read the caps together, not separately. A graphical abstract sitting at the node hard cap has no room left for the arrow hard cap — seven nodes wired by nine arrows is a mechanism diagram, and it belongs in the paper as a numbered figure with a caption. If the content will not fit, the answer is never to shrink the type; it is to cut the claim down to one, or to accept that this result has no graphical abstract in it.

**Source:** the hard caps for nodes, arrows, and encoded dimensions are §5.4's own soft caps and carry §5.4's sourcing (`oligon-brand/SKILL.md` `<design_foundation>` + `diagram-design-skill.md` §7). Everything else in this table is **PROVISIONAL and UNCALIBRATED** — a working target obtained by tightening §5.4, not a measured threshold. That covers all five GA soft caps (5 nodes, 6 arrows, 2 dimensions, 1 accent, 3 color series) and the two hard caps that do *not* follow the derivation rule: the single focal accent, and the color-series ceiling of 5, which is tightened below §5.4's soft cap of 7 on thumbnail-legibility grounds rather than inherited from it.

---

## Text budget

Two independent measures constrain text in a graphical abstract. They are **two different measures, not one idea**, and a figure can satisfy either while failing the other:

1. **Word count — a graphical abstract carries fewer words than the written abstract it accompanies.** This is a comparative ceiling, not an absolute one: it scales with the venue's abstract limit rather than fixing a number. It is the cheap check, and it is the one that catches a figure whose "design" is a paragraph set in a box.
2. **Content ratio — roughly 70% of the content is carried visually rather than in text.** This asks what the reader learns from the picture with the words covered up. It is the check that catches a figure that passes the word count by using few words that nonetheless do all the work, surrounded by decorative icons that carry no information.

The failure modes are distinct, which is why both checks are run. A graphical abstract of forty words of dense prose beside three generic icons passes the word count and fails the ratio. A wall of unlabelled, self-explanatory panels can invert it.

**Both numbers are PROVISIONAL and UNCALIBRATED** — practitioner heuristics with no calibrated source. Treat them as starting hypotheses and defer to any venue instruction that contradicts them.

---

## Thumbnail legibility — the binding constraint

A graphical abstract is almost never first seen at the size it was designed for. Its first and most frequent rendering is a table-of-contents entry, a search-results row, an email alert, or a share card, at roughly **200–300 px wide** (**PROVISIONAL and UNCALIBRATED** — an observed rendering range across contents listings, not a published specification; confirm against the venue's own site). The full-size rendering the venue specifies is the *submission* constraint. The thumbnail is the *design* constraint, and it binds first.

**The rule: every label is legible at ~250 px wide, or it does not belong in the graphical abstract.**

- **Down-render before accepting** — export at the venue size, downscale to ~250 px wide, and read it; anything you cannot read gets cut, merged into a neighboring element, or promoted to something larger, and nothing gets fixed by shrinking the type further
- **Point size does not survive scaling** — a font that just clears the venue's minimum at full size (`../venue-templates/references/figure_specs.md` §1) lands near one-fifth of that on a thumbnail, so the venue floor is necessary and nowhere near sufficient
- **Element count is a legibility constraint, not only a clutter one** — every element added takes width from every label, which is why the element budget above sits below `figure_design_principles.md` §5.4 rather than beside it
- **No fine print** — sub-labels, axis ticks, panel letters, units in parentheses, and attribution text are all unreadable at thumbnail scale; move them to the caption or the paper
- **Test the grayscale and the crop** — contents listings crop to fit and some render small; a graphical abstract that depends on a hue distinction its thumbnail cannot resolve has encoded its claim on a channel the reader does not receive

---

## Design rules that bind harder here

Everything in `figure_design_principles.md` applies. Four rules bind harder in a graphical abstract than anywhere else, because a thumbnail gives the reader one scan and no second chance:

- **One claim, stated once** — the key message is the whole content, and a graphical abstract that carries a second claim loses both
- **Reading order is the argument** — "The default scan path is left-to-right, then top-to-bottom" (`figure_design_principles.md` §5.6); at thumbnail scale the reader spends that one scan or leaves
- **A repeated hue is a claim of relatedness** — with the accent budget at one and the color-series budget at three, hue collisions are near-certain, and §3.6 binds: "Never reuse an accent hue across conceptually unrelated elements; a repeated hue is a claim of relatedness, and the reader acts on that claim before reading a single label"
- **No arrowhead terminates on a label** — graphical abstracts are label-dense by construction, which makes this the most-violated rule in the class; per §7 row 17, "Terminate label leaders with a dot / anchor at the target; reserve arrowheads for motion, flow, or transformation"

---

## Cross-references

| Topic | See |
|---|---|
| **Journal dimensions, DPI, file size, format, font floors, which venues accept a GA** | `../venue-templates/references/figure_specs.md` §1 |
| Viewing-context row (seconds, zero interaction, mixed audience) | `communication_context_matrix.md` |
| Complexity budgets this file tightens | `figure_design_principles.md` §5.4 |
| Reading order and comparison axis | `figure_design_principles.md` §5.6 |
| Hue implies grouping | `figure_design_principles.md` §3.6 |
| Arrow / terminator / line-style glyph semantics | `../scientific-schematics/references/best_practices.md` |
| Whether the result needs a figure at all | `figure_vs_table_decision.md` |
| AI-figure-slop guardrail (GA pipelines are diffusion-based) | `ai_figure_slop.md` |
| Pre-submission quality gate | `pre_submission_checklist.md` |
| Generation pipeline for graphical abstracts | `../paperbanana/SKILL.md` |

---

## References

- Fujii, R. *Nat Hum Behav* (2026). doi:10.1038/s41562-026-02466-9 — communication-context decision step; key-message-first framing.
- Cowan, N. *Curr Dir Psychol Sci* **19**, 51–57 (2010) — working-memory limit underlying the encoded-dimension cap inherited from §5.4.
- Wagemans, J. et al. *Psychol Bull* **138**, 1172–1217 (2012) — Gestalt grouping by similarity; basis for the hue and reading-order rules quoted above.
- Heiser, J. & Tversky, B. *Cogn Sci* **30**, 581–592 (2006) — arrows are read as function and motion, not as pointers; basis for the label-leader rule.
