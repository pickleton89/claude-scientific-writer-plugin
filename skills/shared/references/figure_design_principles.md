# Figure Design Principles (Shared)

> Single source of truth for figure-making principles that apply across multiple visual skills (svg-figure-maker, plotting-libraries, scientific-schematics, research-posters, venue-templates).
> Version: 1.0.0
> Status: canonical
>
> **Skill-specific conventions stay in their own skill directories.** Examples that do NOT belong here: discipline-specific signal conventions (`→` activation / `⊣` inhibition), Oligon-specific palette choices, Mermaid theme variables, matplotlib-only style hacks. Those live with the skill that owns them.
>
> **Every principle below cites its source.** When a source skill's content is the authoritative version, that skill is named and its file:section is given. This doc consolidates *pointers* and shared rules; it does not replace the depth in source skills.

---

## How to use this document

- Skills `<cross_references>` blocks point here for shared principles
- Skills' workflows say "READ §N before proceeding" inline at the relevant stage
- Programmatic enforcement lives in `skills/svg-figure-maker/scripts/preflight_check.py` (rules that can be mechanized)
- For the unified pre-submission gate (15-point checklist), see `pre_submission_checklist.md` in this directory
- For the AI-figure-slop guardrail (categorical tells dominate; aesthetic signals are weak, down-weighted, and two-sided; thresholds provisional/uncalibrated; never minimize ink), see `ai_figure_slop.md` in this directory

---

## §1. Cognitive foundation (cross-link)

Scientific figures rest on perception and cognitive-science findings that apply regardless of brand. Rather than duplicate the citations here, the canonical reference is **`skills/oligon-brand/SKILL.md` `<design_foundation>` block** — five primary perception sources (Cleveland & McGill 1984, Treisman & Gelade 1980, Wagemans 2012, Cowan 2010, Franconeri et al. 2021) plus practitioner canon (Tufte, Wilke, Heer & Bostock, O'Donoghue, Fujii, Jambor, Midway, Weissgerber, Crameri).

Apply-rules from those sources surface throughout this document and are cited inline where they bear on a specific principle.

**One-line take-aways for consumers who don't have time to read the full block:**

| Source | One-line apply rule |
|---|---|
| Cleveland & McGill 1984 | Prefer position > length > angle > area > hue for data encoding |
| Treisman & Gelade 1980 | Pair hue with shape/style/direct labels — never hue alone |
| Wagemans 2012 (Gestalt) | Place labels adjacent to the data they describe |
| Cowan 2010 | Keep simultaneous encoded dimensions ≤4 per panel |
| Franconeri et al. 2021 | Annotate the key comparison on the figure; don't ask the reader to compare across panels by eye |
| Crameri et al. 2020 | Never use jet / rainbow / Spectral for sequential data |

---

## §2. Typography

### §2.1 Type ladder (canonical)

| Element | Size | Weight |
|---|---|---|
| Annotations | 10pt | normal |
| Tick labels | 10pt | normal |
| Axis labels | 12pt | normal |
| Legend text | 12pt | normal |
| Panel labels (A/B/C) | 14pt | bold |
| Figure titles | 16pt | bold |

**Floor: 10pt.** No figure text smaller than 10pt at final print size. (`pre_submission_checklist.md` §6 allows ≥7pt for some venues; treat 10pt as the design target and 7pt as the absolute emergency floor.)

**Source of truth:** `skills/oligon-brand/SKILL.md` `<svg_output>` "Font Size Ladder" + `tokens/brand-tokens.json` `typography.figures`.

### §2.2 Font family

- Mandatory: `font-family="Arial, Helvetica, sans-serif"` on every `<text>`, `<tspan>`, or styled element in SVG output
- Forbidden: Times New Roman, Calibri, Comic Sans, any system default that isn't on the whitelist
- Acceptable Linux fallbacks: DejaVu Sans, Liberation Sans (`rsvg-convert` may fall back to these — not a brand violation)
- Mono only for technical content (code, ports, URLs, command lines) — never as a blanket "dev-aesthetic" font

**Source:** `skills/oligon-brand/SKILL.md` `<svg_output>` "Font Family" + `tokens/brand-tokens.json` `typography.font_family.forbidden`.

### §2.3 Type 42 / TrueType embedding

All text embedded as Type 42 / TrueType. Not outlined, not Type 3. Outlined text destroys editability; Type 3 fonts rasterize poorly.

**Source:** `pre_submission_checklist.md` §5; verification command: `pdffonts figure.pdf` (column `type` = `Type 42` or `TrueType`, column `emb` = `yes`).

### §2.4 Text orientation

- Horizontal text only — no `writing-mode: vertical-*` or `transform="rotate(90)"` on labels
- Sentence case for axis labels and legends: "Time (seconds)" not "TIME"
- Always include units in axis labels and legend entries

**Source:** `scientific-schematics/references/best_practices.md` lines 82–99; `diagram-design-skill.md` §4 anti-patterns (vertical text).

---

## §3. Color and palette

### §3.1 Colorblind-safe defaults

Categorical: `okabe_ito` (8-color, CVD-safe).
Sequential: `viridis`, `cividis`, `batlow`, `roma` (perceptually uniform).
Diverging: `vik`, `roma` (perceptually uniform centred).

**Forbidden:** `jet`, `rainbow`, `Spectral` for any data encoding. These distort scientific data — see Crameri et al. 2020 *Nat Commun* **11**, 5444.

**Source:** `pre_submission_checklist.md` §7 + Crameri et al. 2020 (cited in `oligon-brand/SKILL.md` `<design_foundation>`).

### §3.2 Redundant encoding

Color must never be the only differentiator. Pair color with marker shape, line style, or direct label. This is a Treisman & Gelade 1980 consequence: feature search is parallel, conjunction search is serial — readers identify "the blue squares" much faster than "the blue ones among shapes."

**Source:** `oligon-brand/SKILL.md` `<anti_patterns>` §3; `pre_submission_checklist.md` §10.

### §3.3 Grayscale test

Every figure must remain interpretable when converted to grayscale. If two series differ only by hue (and not by lightness, shape, or pattern), they collapse together in grayscale.

**Verify:** save grayscale conversion and confirm distinguishability. matplotlib: `PIL.Image.open(...).convert('L').save(...)`.

**Source:** `oligon-brand/SKILL.md` `<anti_patterns>` §4.

### §3.4 Two-channel fluorescence: magenta + green

Use magenta (R+B) + green (G), not red + green. Red+green is unreadable to ~8% of male readers (deuteranopia).

**Source:** `pre_submission_checklist.md` §10.

### §3.5 No improvised hex

All colors come from a brand palette token. The preflight checker (`skills/svg-figure-maker/scripts/preflight_check.py`) rejects any hex value not present in `tokens/brand-tokens.json` (or the project-declared palette).

---

## §4. Accessibility

### §4.1 WCAG contrast minimums

| Element | Minimum contrast ratio |
|---|---|
| Body text vs background (WCAG 2.1 SC 1.4.3) | 4.5 : 1 |
| Large text ≥18pt or ≥14pt bold | 3 : 1 |
| Non-text elements: lines, plot marks, icons, borders (SC 1.4.11) | 3 : 1 |

Required by EU European Accessibility Act (in force 28 June 2025) and US DOJ ADA Title II web accessibility rule (April 2024); both reference WCAG 2.1 AA.

**Verify:** `colour-contrast-checker` (Python), browser DevTools, or `skills/shared/accessibility/` test utilities.

**Source:** `pre_submission_checklist.md` §8, §9.

### §4.2 Alt text formula

Two sentences per panel describing the **finding**, not the chart mechanics.

- ❌ Bad: "Bar chart showing four bars."
- ✅ Good: "Treatment X reduced tumor volume by 60%; combination therapy by 85%."

Required by EU Accessibility Act and US DOJ Title II for journal websites and supplementary HTML. Reframing per Fujii 2026 and Jambor 2025: alt text *is* message communication.

**Source:** `pre_submission_checklist.md` §11; canonical formula at `venue-templates/references/figure_specs.md` §4.

---

## §5. Composition

### §5.1 Figure vs. table decision

Before drawing a figure, ask: should this be a table? Tables win for precise numerical values, baseline characteristics, model coefficients with CIs, <5 data points, and results readers will quote. Figures win for distributions, correlations, time trends, complex multi-dimensional comparisons.

**Source:** `figure_vs_table_decision.md` (full decision aid); Fujii 2026 §"Ask whether you really need a figure."

### §5.2 Direct labeling over distant legends

Label lines, groups, and key points adjacent to the data they describe. Distant legends force readers to shift attention back and forth, increasing cognitive load (Fujii 2026); spatial proximity binds label to data (Wagemans 2012 Gestalt grouping).

For matplotlib: `ax.annotate()` or `loc='best'` inside the plot area. For ggplot2: `geom_text` or `ggrepel::geom_text_repel`.

**Source:** `pre_submission_checklist.md` §12.

### §5.3 Chart-type conflict resolution

When a chart-type recommendation differs across sources, defer to the primary research over template catalogs:

1. **Weissgerber et al. 2015** — bar charts hide continuous distributions; use box/violin/strip+jitter
2. **Fujii 2023** — risk/odds/hazard ratios as `pointrange`, not bars
3. **Cleveland & McGill 1984** — position-encoded charts (scatter, dot plots) beat angle/area encodings
4. **Crameri et al. 2020** — no jet/rainbow for sequential data

**Source:** `chart_types_catalog.md` "Conflict Resolution" section; cross-cited in `plot_selection_guide.md`.

### §5.4 Complexity budgets

Hard ceilings per panel; if exceeded, split into facets / multi-panel rather than crowding:

| Element | Soft cap | Hard cap | Trigger |
|---|---|---|---|
| Simultaneous encoded dimensions | 3 | 4 | Cowan 2010 working-memory limit |
| Categorical color series | 7 | 8 | Okabe-Ito palette size |
| Diagram nodes (svg-figure-maker / scientific-schematics) | 7 | 9 | `diagram-design-skill.md` §7 |
| Diagram arrows | 9 | 12 | `diagram-design-skill.md` §7 |
| Focal accent elements (Brand Blue / coral) | 1 | 2 | `oligon-brand` `<anti_patterns>` §2 |

**Source:** `oligon-brand/SKILL.md` `<design_foundation>` + `diagram-design-skill.md` §7; project memory cites this as a `diagram-design-skill.md` borrow.

### §5.5 Communication context drives complexity

Figure complexity should match the viewing context (oral talk → seconds-to-grasp; article → minutes-to-grasp; interactive → exploration-supported). See `communication_context_matrix.md` for the audience × viewing-context grid.

**Source:** `communication_context_matrix.md`; Fujii 2026.

---

## §6. Layout and grid

### §6.1 Grid discipline

- **8px grid** for figure work (plots, panel composition, posters)
- **4px grid** for dense diagram work (svg-figure-maker hand-authored diagrams, scientific-schematics SVG output)

All coordinates, widths, heights, padding, gaps, and font sizes divisible by the relevant grid unit. Quick check: if a measurement ends in 1, 2, 3, 5, 6, 7, or 9 on a 4px grid, fix it.

**Source:** `diagram-design-skill.md` §7 lines 263–280.

### §6.2 Multi-panel layout

For figures with multiple panels (A, B, C, …):

- **Panel labels** in upper-left of each panel, **14pt bold**, sans-serif, black
- **Label position:** offset 8px from the panel's top-left corner, outside the plot area
- **Shared axes** whenever the data permit it — reduces cognitive load (Cowan 2010) and saves space
- **Alignment:** panel boundaries snap to the 8px grid; horizontally adjacent panels share their y-axis extent; vertically adjacent panels share their x-axis extent
- **Inter-panel gaps:** minimum 16px (two grid units); enlarge to 24px when axes are not shared
- **Don't mix orientations** within one figure — keep panel layouts consistent (all horizontal, all square, etc.) unless content forces otherwise

### §6.3 Legend placement

Direct labeling is preferred (see §5.2). When a legend is unavoidable:

- **Position priority:** top-right *inside* plot area > top-left inside > bottom strip outside > side strip outside. Never place a legend *over* data.
- **Single legend per panel** — if two panels share a series, share a legend at figure level rather than repeating it
- **Horizontal layout** when ≤4 entries; vertical only when entry count forces it
- **No bounding box / drop-shadow** on legends; use 8px internal padding and the page background as the visual frame
- **Order entries** by data prominence (most-emphasized first), not alphabetically

**Source:** §5.2 (direct-labeling preference); `diagram-design-skill.md` line 255 (horizontal bottom strip for diagrams specifically).

### §6.4 Whitespace and padding

| Region | Padding (8px grid) |
|---|---|
| Plot area → axis labels | 8px |
| Axis labels → panel edge | 16px |
| Panel edge → adjacent panel edge | 16–24px (see §6.2) |
| Inside a legend / annotation box | 8px |
| Title → top of plot area | 16px |
| Caption → bottom of figure | 24px |

**Default canvas margins:** 32px on all sides for figures intended for embedding; 16px for figures intended for tight composition. Adjust to the venue's column-width spec — see `venue-templates/references/figure_specs.md`.

**Rule of thumb:** whitespace IS a design element. If you can't decide between two layouts, pick the one with more whitespace.

---

## §7. Anti-patterns (banned)

Universal anti-patterns. Skill-specific anti-patterns (e.g., matplotlib library defaults, Brand-Blue-vs-Medium-Blue confusion) stay in their owning skill.

| # | Anti-pattern | Why it's banned | Fix |
|---|---|---|---|
| 1 | Drop-shadow / glow filters (`filter:`, `feDropShadow`, dark-mode + cyan glow) | Adds visual noise without signal; reads as "AI slop" | Remove all `<filter>` elements; use borders for separation |
| 2 | Color-only encoding (hue without shape/style/label) | Treisman & Gelade 1980 — conjunction search is serial; CVD readers can't distinguish | Add marker shape, line style, or direct label |
| 3 | Bar chart of continuous data (group means with error bars) | Weissgerber 2015 — bars hide the underlying distribution | Use box+jitter, violin+jitter, or strip plot |
| 4 | Bar chart of risk/odds/hazard ratios | Fujii 2023 — bars exaggerate the point estimate vs. the CI | Use `pointrange` (point + horizontal CI) |
| 5 | Rainbow / jet / Spectral colormaps for sequential data | Crameri 2020 — actively distorts scientific data | Use viridis, cividis, batlow, roma |
| 6 | Identical boxes for every diagram node (no hierarchy) | Erases visual hierarchy; reader can't tell what's important | Vary size/weight/color for emphasis |
| 7 | Legend inside the diagram body (not on a strip) | Clutters the data area | Bottom strip or outside the plot area (§6.3) |
| 8 | Vertical writing-mode text on labels or arrows | Unreadable at print scale | Horizontal text only |
| 9 | Library defaults (matplotlib/seaborn categorical colors) | Not brand-compliant; not CVD-safe | Call `set_brand_style()` or load brand mplstyle before plotting |
| 10 | More than two focal accents per panel | Dilutes emphasis | Limit Brand Blue / coral / focal color to 1-2 elements |
| 11 | Logo on publication figures | Most journals prohibit branding on figures (copyright transfer) | Logos only on presentations, posters, internal docs |
| 12 | CSS named colors (`lightblue`, `darkred`, etc.) in SVG | Ambiguous, not in palette tokens, fails preflight | Use hex from `tokens/brand-tokens.json` |
| 13 | Rounded corners larger than 10px on diagram nodes | "rounded-2xl" reads as web-UI, not editorial figure | Max radius 6–10px |
| 14 | Optimizing for data-to-ink ratio mechanically | Tufte's rule mis-applied removes useful labels | Apply Fujii's signal-to-noise reframing: keep ink that supports the *takeaway*, not just ink that "represents data" |
| 15 ⚑ | Lexically-void / garbled label text (`diƨlocttal`, `2xℇpens`), or axis ticks rendered as raw sequence indices (1,2,3…) instead of real categories | Near-categorical AI-generation tell (Frontiers/Bik 2024); a competent human never emits void glyph-strings | Replace with real terms from the source data; for our own output this is caught EXACTLY by `svg-figure-maker/scripts/preflight_check.py` (`check_garbled_text`, `check_raw_index_labels`) against the known labels — see `ai_figure_slop.md` |
| 16 ⚑ | Encoding contradicts the printed value (bar height / slice angle / point position ≠ its number), or parts-of-whole that do not sum (pie ≠ 100%, stacked totals don't reconcile) | Covert Class-B tell: rendering looks correct, the encoding contract is broken (Woo; practitioner) | We hold the source data — verify EXACTLY (`plotting-libraries/scripts/validate_data.py::check_encoding_value_fidelity`, `::check_closure`). Never an image-OCR step for our own figures. See `ai_figure_slop.md` |

**Sources:** `oligon-brand/SKILL.md` `<anti_patterns>` §1–7; `diagram-design-skill.md` §4 lines 96–113; `pre_submission_checklist.md` §13–14. Rows 15–16: `ai_figure_slop.md` (categorical-tell-dominant; two-sided/down-weighted aesthetic signals).

---

## §8. File format and resolution

### §8.1 Preferred order

1. **SVG** — web, editable, vector, preferred for figures Claude generates
2. **PDF** — print, universal, vector, preferred for submission
3. **EPS** — legacy, accept only when journal requires
4. **TIFF / PNG** — raster, fallback only when figure cannot be vector (e.g., microscopy, photos)

### §8.2 Resolution floors

- **Vector outputs (SVG, PDF, EPS):** vector throughout; no embedded rasters below 300 DPI
- **Raster outputs:** ≥300 DPI for prints; 600–1200 DPI for line art; never <300 DPI for print submission
- Below 300 DPI, print artefacts appear at journal scale

**Source:** `pre_submission_checklist.md` §3; `scientific-schematics/references/best_practices.md` lines 50–70.

### §8.3 Journal column widths (single source)

Single-column / double-column targets vary by venue. Authoritative reference: `venue-templates/references/figure_specs.md`. Common values:

| Venue | Single column | Double column |
|---|---|---|
| Nature | 89 mm | 183 mm |
| Science | 55 mm | 120 mm |
| Cell | 85 mm | 178 mm |
| PLOS | 83 mm | 173 mm |

Always cross-check against the venue's current author guidelines.

---

## §9. Pre-submission validation (operational gate)

The full 15-point checklist lives at `pre_submission_checklist.md`. This section names the SVG-specific operational checks every skill that emits SVG must run.

### §9.1 SVG grep checks

```bash
# Must return matches; must NOT include Times, Calibri, or system defaults
grep -oE 'font-family[^;">]+' figure.svg | sort -u

# Confirm sizes are in the 10/12/14/16 band (px or pt; matplotlib emits px, Mermaid pt)
grep -oE 'font-size[^;">]+' figure.svg | sort -u
```

If `font-family` is absent or any size falls below 10 (px or pt), regenerate. See `oligon-brand/SKILL.md` `<svg_output>` for the matplotlib caveat (`svg.fonttype: none` keeps `<text>` elements instead of glyph paths).

### §9.2 Visual preview (mandatory)

Render SVG to PNG via the canonical script:

```bash
skills/oligon-brand/scripts/render_svg_preview.sh figure.svg
# higher resolution for dense labels:
skills/oligon-brand/scripts/render_svg_preview.sh figure.svg --scale 3
```

`Read` the resulting PNG. Verify:

- Every text element is fully visible (not clipped at panel edges)
- Tick labels don't overlap each other or the axis line
- Legend doesn't cover data
- Arrowheads / connector endpoints land where they should
- Panel labels (A, B, C) don't collide with axis titles
- Overall composition matches the figure brief

If any check fails, regenerate. **The grep checks + visual preview are the brand delivery gate.**

**Source:** `oligon-brand/SKILL.md` `<svg_output>` "Visual Preview" + "Post-Generation Sanity Check".

### §9.3 Programmatic enforcement

For rules that can be mechanized (font-family, font-size, banned attrs, off-palette hex, off-grid coords, missing `<title>`/`<desc>`), use:

```bash
uv run python skills/svg-figure-maker/scripts/preflight_check.py figure.svg
```

Returns JSON findings keyed to this document's section numbers.

---

## §10. AI figure slop & regression-to-mean

> **Canonical reference:** `skills/shared/references/ai_figure_slop.md` —
> the three-track model (A2 author-time exact checks / Track B linter
> functions / Track D inbound advisory triage), the six-dimension v0.1
> rubric, and the categorical-vs-graded severity logic. **Read that file
> before relying on any threshold here; all thresholds are provisional and
> uncalibrated.**

Two load-bearing rules govern everything in that file and must be honored
by any skill that consumes it:

1. **Emit a *vector* of flagged sub-scores with severities — never a single
   composite "slop score."** Provenance ≠ quality: a figure can be
   AI-generated and excellent, or human-made and slop (Kommers 2026).
2. **Categorical tells dominate; aesthetic signals are weak, down-weighted,
   and two-sided.** A lexically-void label or an encoding-vs-value mismatch
   is near-decisive on its own; decoration/data-ink signals never trigger
   a verdict alone and must not be read as "strip the decoration"
   (Bateman 2010).

Because this plugin *generates* figures, we hold the ground-truth data and
source SVG/plot code, so the unreliable image→data recovery step (OCR /
forensic CV — shown to fail zero-shot in SciFigDetect) is **unnecessary for
our own output**. Replace it with cheap *exact* checks against the data and
source. Only inbound third-party figures (Track D) need the forensic/rubric
stack, and there it stays advisory, never dispositive.

**One-line take-aways (mirroring the §1 cognitive-foundation table):**

| Signal | Class | One-line apply rule |
|---|---|---|
| Lexically-void / garbled labels | categorical ⚑ | Real words/terms/numbers only — scan the source string set, not pixels (Frontiers/Bik 2024) |
| Encoding–value mismatch | categorical ⚑ | `encoded == source` for every bar/slice/point — verify against held data, not OCR (Woo 2025) |
| Closure / conservation failure | categorical ⚑ | Parts sum to whole; subgroups reconcile to totals — check the data array |
| Axis labels = raw indices | categorical ⚑ | Tick labels are real categories, never 1,2,3… sequence indices |
| Default-distribution styling | graded, weak | Replace tool defaults (tab10/seaborn/Excel) with an intentional palette — *don't* over-minimize (two-sided) |
| Gratuitous decoration / data-ink | graded, weak, two-sided | Keep ink that supports the takeaway; embellishment aids recall (Bateman 2010) — never an AI verdict alone |

**Track B enforcement.** The exact author-time checks are deterministic
functions in `plotting-libraries/scripts/validate_data.py`
(`check_continuous_as_bars`, `check_riskratio_as_bars`,
`check_encoding_value_fidelity`, and `check_closure`) plus the SVG-string
scan in `svg-figure-maker/scripts/preflight_check.py` (`check_garbled_text`,
`check_default_palette_fingerprint`, `check_raw_index_labels`). Run the SVG
gate via `uv run python scripts/preflight_check.py figure.svg`; a
`categorical`-severity finding there is a **hard fail** (treat like `fail`).
See `pre_submission_checklist.md` "Generative-artifact integrity" items for
the operational gate.

---

## §11. Out-of-scope for this doc

Things that look like principles but belong elsewhere:

| Topic | Where it lives |
|---|---|
| Specific brand color hex values | `oligon-brand/tokens/brand-tokens.json` |
| Cognitive-foundation citations (full text + apply rules) | `oligon-brand/SKILL.md` `<design_foundation>` |
| Discipline-specific signal direction (→ ⊣ - - →) | `scientific-schematics/SKILL.md` |
| Biological color conventions (DNA blue, mRNA orange) | `scientific-schematics/SKILL.md` |
| Mermaid theme variables / init blocks | `scientific-schematics/SKILL.md` |
| matplotlib mplstyle / rcParams | `oligon-brand/assets/oligon_color_brand.mplstyle` |
| Skill-internal four-stage workflow recipes | individual skill `<workflow>` blocks |
| The 15-point pre-submission gate | `pre_submission_checklist.md` |
| Per-venue column widths and DPI rules | `venue-templates/references/figure_specs.md` |
| Iconography licensing per library | `iconography-licensing.md` |

---

## §12. References

Primary perception / cognitive science (full citations in `oligon-brand/SKILL.md` `<design_foundation>`):

- Cleveland & McGill 1984 *J Am Stat Assoc*
- Treisman & Gelade 1980 *Cognitive Psychol*
- Wagemans et al. 2012 *Psychol Bull*
- Cowan 2010 *Curr Dir Psychol Sci*
- Franconeri et al. 2021 *Psychol Sci Public Interest*

Scientific-figure guidance:

- Crameri, Shephard, Heron 2020 *Nat Commun* **11**, 5444 — CVD-safe palettes
- Fujii 2026 *Nat Hum Behav* — communication context; signal-to-noise; figure-vs-table
- Fujii 2023 *J Epidemiol* **33**, 487–488 — risk ratios as pointrange
- Weissgerber et al. 2015 *PLoS Biol* **13**, e1002128 — bar charts hide distributions
- Jambor 2025 *Nat Cell Biol* **27**, 879–883 — alt text + figure accessibility
- Midway 2020 *Patterns* **1**, 100141 — table-vs-figure principles
- Tufte 2001 *The Visual Display of Quantitative Information* (2nd ed., Graphics Press)
- Wilke 2019 *Fundamentals of Data Visualization* (O'Reilly)
- Heer & Bostock 2010 *CHI* — crowd-sourced graphical perception

Accessibility law / standards:

- WCAG 2.1 SC 1.4.3, SC 1.4.11 — https://www.w3.org/TR/WCAG21/
- EU Directive 2019/882 (European Accessibility Act), in force 28 June 2025
- US DOJ ADA Title II web accessibility rule (28 CFR 35.200), April 2024
