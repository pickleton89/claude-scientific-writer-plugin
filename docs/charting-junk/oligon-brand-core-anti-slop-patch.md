# Upstream patch — anti-slop Rules 9–12 + two-sided Default-Syndrome (apply in `oligon-brand-core`, NOT here)

> **Why this is a separate patch file, not an in-repo edit.** `skills/oligon-brand/SKILL.md` in this plugin is **vendored/generated** — it is regenerated from the canonical `oligon-brand-core` repo by `scripts/sync_brand_core.sh` and a CI check fails if the vendored copy drifts. So the "Rules 9–12" and the two-sided Default-Syndrome pitfall below must be applied **upstream in `oligon-brand-core`** (which carries the same `## Figure Integrity` and `### Universal design pitfalls` anchors), then pulled back in via `scripts/sync_brand_core.sh <oligon-brand-core checkout>`. Do NOT hand-edit the vendored `skills/oligon-brand/SKILL.md`.

This packages **Edit 1a** (extend the Figure Integrity rules) and **Edit 1b** (two-sided Default-Syndrome pitfall) from `docs/charting-junk/specs/guidance-edits.md`. The plugin-side cross-links into the new doctrine live in the shared registries (`figure_design_principles.md` §12, `pre_submission_checklist.md` "Generative-artifact Integrity") — those are handled separately and do not require this upstream patch to land first.

The substance of Rules 9–12 is the canonical doctrine in `skills/shared/references/ai_figure_slop.md` §3 (categorical tells) and §4 (regression-to-mean catalog). This patch surfaces that doctrine in the brand SKILL body so it appears after the next sync.

---

## Patch 1 (Edit 1a) — Figure Integrity: "Eight Rules" → "Twelve Rules"

### Anchor (upstream `SKILL.md`, inside the `<figure_integrity>` block)

The heading currently reads:

```
## Figure Integrity — Eight Rules
```

and the block currently ends with rule 8 immediately before the closing tag:

```
8. **No dual y-axes without justification.** Prefer small multiples
   or twin-panel layouts first.
</figure_integrity>
```

### Change 1 — retitle the heading

Replace:

```
## Figure Integrity — Eight Rules
```

with:

```
## Figure Integrity — Twelve Rules
```

### Change 2 — insert four new rules before the closing tag

Replace:

```
8. **No dual y-axes without justification.** Prefer small multiples
   or twin-panel layouts first.
</figure_integrity>
```

with the literal text:

```
8. **No dual y-axes without justification.** Prefer small multiples
   or twin-panel layouts first.

These four govern *generative-artifact integrity* — the failure modes a
diffusion model or code-gen LLM introduces that a competent human would
not. Because we author from ground-truth data and source SVG/plot code,
these are **exact deterministic checks against what we already hold**, not
image forensics. A single confirmed violation of Rule 9, 11, or 12 is a
*categorical tell* — it dominates the verdict regardless of how clean the
rest of the figure is.

9. **Lexically-valid labels only.** Every axis label, legend entry, tick
   label, and callout is a real word, term, or number — never a
   letter-shaped but lexically-void glyph-string ("*diƨlocttal*",
   "*testtomcels*"), invented diacritic, or melted/mixed-script character.
   This is the strongest single AI tell (Frontiers/Bik 2024). For our own
   output, scan the source string set, not the pixels.
10. **Non-default styling is intentional, not stripped.** Tool defaults
    (matplotlib `C0`/`C1` tab10, seaborn theme, Excel chart style) are a
    regression-to-mean slop fingerprint — apply a brand cycle or a
    justified palette instead. But this rule is **two-sided**: do *not*
    over-minimize toward a sterile, decoration-free chart either.
    Embellishment that aids recall is not slop (Bateman CHI 2010). Keep
    ink that supports the takeaway; replace defaults, don't strip
    meaning.
11. **Encoding-value fidelity.** Bar heights, slice angles, point
    positions, and marker sizes must match the printed/underlying values.
    Geometry that contradicts the data label is a fabrication tell. We
    hold the data, so verify exactly — `encoded_value == source_value`,
    not OCR.
12. **Closure / conservation holds.** Parts-of-whole sum to the whole
    (pie/stacked slices → 100% or the stated total); subgroup counts
    reconcile to the group total; axis labels are the real categories,
    not raw sequence indices (1, 2, 3…). Check the source data array,
    not the render.
</figure_integrity>
```

---

## Patch 2 (Edit 1b) — Universal design pitfalls: two-sided Default Syndrome

### Anchor (upstream `SKILL.md`, inside the `<design_foundation>` block)

The list currently reads:

```
### Universal design pitfalls

1. **Default Syndrome** — tool defaults without justification
2. **Rainbow colormap for sequential data** — use viridis family
3. **Color-only encoding** — add shape / line style / direct label
4. **Cramming** — one main message per figure
5. **Inconsistent styling** — define the hierarchy before starting
6. **Truncated axes** — start bar charts at zero
7. **3D for 2D data** — distorts perception
```

### Change — replace item 1 with a two-sided entry (numbering 1–7 stays intact)

Replace:

```
1. **Default Syndrome** — tool defaults without justification
```

with:

```
1. **Default Syndrome / regression-to-mean (two-sided)** — tool defaults
   without justification are a slop fingerprint (avoid the canonical
   matplotlib/seaborn/Excel look); but the opposite failure is just as
   real — sterile over-minimization that strips useful labels and
   embellishment is *also* regression-to-the-mean (Bateman CHI 2010: junk
   doesn't impair comprehension and aids recall). Replace defaults with an
   intentional, takeaway-supporting style — not with the leanest possible
   chart.
```

---

## After applying upstream

1. Commit the two patches in `oligon-brand-core`, push.
2. In this plugin, re-vendor: `scripts/sync_brand_core.sh <path-to-oligon-brand-core-checkout>`.
3. The regenerated `skills/oligon-brand/SKILL.md` will then carry "Twelve Rules" and the two-sided Default-Syndrome pitfall; the CI drift check passes because the vendored copy now matches a regeneration against the pinned core SHA.
