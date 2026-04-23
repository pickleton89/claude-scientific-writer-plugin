# Publication Specifications for Scientific Figures

> Quick reference for journal-specific requirements, export settings, and pre-submission verification. Specs here were last verified against publisher-hosted pages in April 2026 — re-verify at submission time.

## Journal Requirements

| Journal | Single Column | Double Column | Max Height | Notes |
|---------|---------------|---------------|------------|-------|
| **Nature** | 89 mm (3.5") | 183 mm (7.2") | 247 mm | Lowercase panel labels (a, b, c); 5–7 pt body text floor; RGB recommended |
| **Science** | 55 mm (2.2") | 175 mm (6.9") | 230 mm | Uppercase panel labels (A, B, C); 6 pt minimum; lines ≥0.5 pt |
| **Cell** | 85 mm (3.3") | 178 mm (7.0") | 230 mm | Uppercase panel labels; Avenir/Arial; 8 pt floor |
| **PLOS** | 83 mm | 173 mm | 230 mm | CC-BY license required; 8–12 pt Arial/Times/Symbol only; TIFF or EPS only for main figures |
| **PNAS** | 87 mm | 178 mm | 230 mm | Two-column; RGB required; TIFF/EPS/high-res PDF only; 6 pt min |

**Quick sizing reference:**
```python
# Common figure sizes (width in inches)
JOURNAL_WIDTHS = {
    'nature_single': 3.5,
    'nature_double': 7.2,
    'science_single': 2.2,
    'science_double': 6.9,
    'cell_single': 3.3,
    'cell_double': 7.0,
}
```

## Resolution Standards

| Figure Type | Minimum DPI | Recommended | Format |
|-------------|-------------|-------------|--------|
| **Line art** (graphs, plots) | 600 | 1200 | Vector (PDF, EPS, SVG) |
| **Combination** (plots + images) | 600 | 600 | Vector or TIFF |
| **Photographs** | 300 | 300-600 | TIFF, PNG |
| **Microscopy images** | 300 | 300-600 | TIFF (no compression) |

**Key principles:**
- **Vector formats** (PDF, EPS, SVG) are resolution-independent and preferred for all plots
- **TIFF** preferred for raster images (lossless compression)
- **PNG** acceptable for web/preprint
- **Never use JPEG** for scientific figures (lossy compression creates artifacts)

## File Formats

| Format | Best For | Advantages | Limitations |
|--------|----------|------------|-------------|
| **PDF** | Plots, figures | Vector, fonts embedded, universal | Larger file size |
| **EPS** | Plots, legacy systems | Vector, widely supported | Older format |
| **SVG** | Web, interactive | Vector, editable | Limited print support |
| **TIFF** | Photos, microscopy | Lossless, print standard | Large files |
| **PNG** | Web/preprint | Lossless, web-compatible | No CMYK support |

**Export workflow:**
1. Create figure at target journal dimensions
2. Use vector format (PDF/EPS) for all plots and diagrams
3. Use TIFF (LZW compression) for photographs
4. Verify fonts are embedded
5. Check final file meets size limits

## Multi-Panel Figures

### Panel Labeling Conventions

- **Position**: Top-left corner of each panel
- **Style**: Bold, sans-serif font
- **Size**: 8-12 pt at final print size
- **Case**: Check journal (Nature = lowercase, most others = uppercase)

### Alignment Best Practices

- Use GridSpec or subplot mosaic for consistent alignment
- Maintain equal margins between panels
- Align related axes where possible
- Use adequate white space (don't cram panels)

**Implementation:**
```python
from string import ascii_uppercase  # or ascii_lowercase for Nature

fig = plt.figure(figsize=(7, 4))
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.4)

for i, ax in enumerate([ax1, ax2, ax3, ax4]):
    ax.text(-0.15, 1.05, ascii_uppercase[i],
            transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top')
```

## Graphical-Abstract Specifications

Graphical abstracts are **required at Cell Press journals** (Cell, Cancer Cell, Immunity, Molecular Cell, Cell Reports, Neuron, and the rest of the portfolio), optionally used at **Nature Chemistry** and **Nature Chemical Biology** with a distinct rectangular geometry, and **not used** at most other major venues — which substitute plain-language summaries instead. Producing an elaborate graphical abstract for a venue that does not publish them is the single most common source of wasted effort.

| Publisher | GA policy | Dimensions / geometry | Special rules |
|---|---|---|---|
| **Cell Press** (Cell, Cancer Cell, Immunity, Molecular Cell, Cell Reports, Neuron, etc.) | **Required** | 1200 × 1200 px @ 300 dpi (square); ≤20 MB | PDF (preferred), EPS, JPEG, TIFF; AI/PSD/PPT source accepted; Avenir or Arial; embed fonts; reads top→bottom or left→right |
| **Nature Chemistry / Nature Chemical Biology** | **Optional** | 90 × 50 mm (rectangular) | Distinct from Cell geometry — do not reuse a square GA |
| **Nature** (main) | Not used | — | No graphical abstract; submit figures only |
| **Nature Medicine, Nature Cancer, Nature Immunology, Nature Communications** | Not used | — | No graphical abstract |
| **Science family** (Science, Science Translational Medicine, Science Immunology) | Not used | — | No graphical abstract |
| **PNAS** | Not used | — | **Significance Statement** replaces it (plain language, ~120 words) |
| **eLife** | Not used | — | Plain-language **"digest"** replaces it |
| **PLOS** | Not used | — | **Author Summary** replaces it |
| **JAMA Network** | Not used | — | **Key Points** (text) + staff-produced visual abstract (redrawn in-house) |
| **NEJM** | Not used | — | In-house illustrators redraw figures for final publication |
| **The Lancet** | Not used | — | In-house illustrators redraw figures |

**Before designing a graphical abstract:** confirm the target journal actually publishes them. Check the current Author Guidelines — policies change.

## Color-Space Preferences

RGB is now the preferred color space at almost every major publisher for initial submission. The days of mandatory CMYK conversion at the author's end are largely over.

| Publisher | Color space at submission | In-house handling |
|---|---|---|
| **Nature portfolio** | RGB recommended (wider gamut, preserves fluorescence) | Production converts if print color management requires |
| **PNAS** | **RGB required** | PNAS converts in-house |
| **Science family** | RGB accepted; color encouraged | — |
| **Cell Press** | RGB assumed (not explicitly stated in retrieved guides) | — |
| **JAMA Network** | RGB submission | JAMA converts |
| **PLOS** | **RGB 8 bit/channel or grayscale only**; no alpha; flattened | Enforced; rejects other modes |
| **eLife** | RGB | — |

**Practical upshot:** design in RGB; only worry about CMYK if the journal's current guide explicitly requires it.

## Font Embedding (Type 42 / TrueType)

Every major publisher that accepts editable figures (PDF, EPS, AI) wants **fonts embedded, not outlined**. Production systems need editable text for house-style changes, HTML translation, and accessibility tooling. Outlined text breaks all three.

Concrete commands by toolchain:

**matplotlib (Python):**
```python
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42  # TrueType (embedded), not Type 3 (rasterized)
matplotlib.rcParams['ps.fonttype'] = 42
```

**ggplot2 (R):**
```r
# Option A: Cairo backend (simplest — fonts embedded automatically)
ggsave("fig1.pdf", device = cairo_pdf, width = 3.5, height = 2.5)

# Option B: default pdf device + extrafont (embeds system fonts post-hoc)
library(extrafont)
ggsave("fig1.pdf", device = "pdf")
embed_fonts("fig1.pdf")  # subsets fonts into the PDF

# Option C: ragg backend (for PNG/TIFF raster with correct font rendering)
library(ragg)
ggsave("fig1.png", device = agg_png, res = 300, width = 3.5, height = 2.5, units = "in")
```

**Adobe Illustrator:**
- `File → Save As → PDF`
- In the dialog: **Preserve Illustrator Editing Capabilities ON**, subset fonts at 100 %
- Do **not** use `Type → Create Outlines` unless the journal explicitly requests outlines for an unusual typeface

**When to outline instead of embed:** only when the journal's Author Guide explicitly requests outlines (rare), or when a license-restricted typeface cannot be embedded legally. Keep an editable master file regardless — late-stage revisions will always need it.

**Default:** embed. Check fonts are embedded with `pdffonts file.pdf` (expect `emb=yes`, `sub=yes` for each face) or in Acrobat under `File → Properties → Fonts`.

## Alt-Text Formula

Alt text is becoming a submission requirement at several publishers (Springer Nature provides an AI-assisted tool from late 2024; PLOS and eLife encourage it; Cell Press handles accessibility in post-production). The EU European Accessibility Act (enforced June 2025) and US DOJ WCAG 2.1 AA adoption (April 2024) are driving universal adoption.

**Formula:** describe the **take-home finding**, not the chart mechanics. One to three sentences. One alt text per panel for multi-panel figures.

**Good:**
> Kaplan-Meier curve showing significantly shorter overall survival in TP53-mutant patients (median 14 vs 32 months; p = 0.003) over 60 months of follow-up.

**Bad:**
> Line graph with two curves.

Length guidance varies among publishers (DIAGRAM Center: as brief as possible; Taylor & Francis: 40–50 words preferred, up to 100; Karger: 10–100 words). Convergence: prioritize the finding over the mechanics. If the chart type is essential to interpretation, lead with the finding and mention the chart type second ("Kaplan-Meier curve showing..." rather than "Line graph showing...").

## Conflict Flags

These are known inconsistencies between publisher documents retrieved in April 2026. **Confirm with the handling editor** rather than guess.

- **Cell Press graphical-abstract font size** — the Cell GA guide PDF states 8–12 pt; the Matter figure-guidelines page states 12–16 pt. Design to the conservative (smaller) end and widen only on explicit confirmation.
- **Lancet single-column figure width** — the artwork-guidelines PDF states 75 mm; older information-for-authors PDFs cite 107 mm. Design to the narrower figure and expand only on confirmation from production.

## Pre-Submission Checklist

Before submitting figures to any journal, verify:

### Technical Requirements
- [ ] Resolution meets journal requirements (≥300 DPI halftone floor; 600–1200 DPI for line art where specified — Science, PNAS)
- [ ] File format is correct (vector for plots; TIFF/EPS where mandated — PLOS, PNAS)
- [ ] Figure size matches journal column width specifications at final publication size
- [ ] File size within journal limits (Cell ≤20 MB; PLOS ≤10 MB; JAMA ≤1 MB per file)
- [ ] Graphical abstract matches target journal geometry (1200 × 1200 px for Cell Press; 90 × 50 mm for Nature Chem / Nature Chem Biol; **skip entirely** for venues that don't publish them)

### Typography
- [ ] All text readable at final size (≥5 pt floor at Nature; ≥6 pt at Science/PNAS; ≥8 pt at PLOS)
- [ ] Fonts consistent across all figures in manuscript
- [ ] Sans-serif fonts used (Arial, Helvetica, Avenir at Cell; Calibri as fallback)
- [ ] **Fonts embedded, not outlined** (Type 42 / TrueType) — verify with `pdffonts` or Acrobat Font panel
- [ ] All axes labeled with units in parentheses

### Color & Accessibility
- [ ] Colors are colorblind-friendly — test with Color Oracle, Coblis, or `colorspacious` simulator (deuteranopia, protanopia, tritanopia)
- [ ] Figure interpretable in grayscale (desaturate before submission)
- [ ] Redundant encoding used (shapes, patterns, line styles, direct labels — not just color)
- [ ] Contrast ≥4.5:1 for text; ≥3:1 for graphical objects (WCAG 2.1 SC 1.4.11, 1.4.3)
- [ ] For 2-channel fluorescence: **magenta + green** (or cyan + magenta), **not** red + green; include per-channel grayscale panels
- [ ] No rainbow / jet colormaps on continuous data — use viridis/cividis (sequential), RdBu/PuOr/vik/berlin (diverging)

### Scientific Rigor
- [ ] Error bars present with type defined in caption (SD, SEM, CI)
- [ ] Sample size (n) stated in figure or caption
- [ ] Statistical significance markers clearly labeled (*, **, ***)
- [ ] Individual data points shown when feasible
- [ ] Scale bars present on every image-based panel; inset locations framed on the overview

### Visual Quality
- [ ] Panel labels present and consistent (A, B, C or a, b, c — match journal convention)
- [ ] No chart junk (unnecessary gridlines, 3D effects, shadows)
- [ ] Legend clear and complete; prefer direct labeling over corner legends
- [ ] No truncated axes on bar charts unless scientifically justified (legitimate for dot plots, effect-size plots, log scales, trajectories with marked breaks)
- [ ] ≤4 simultaneously encoded channels per panel (x, y, color, shape, size, line type, row, column)

### Iconography Licensing
- [ ] Every icon source identified (BioRender, NIH BIOART, SciDraw, Servier, Noun Project, etc.)
- [ ] Publication license PDF downloaded from each paid/tiered source (BioRender in particular)
- [ ] Required attribution lines drafted for figure caption or acknowledgments
- [ ] Re-verified license terms on each submission — see `../../shared/references/iconography-licensing.md`

### Alt Text & Metadata
- [ ] Alt text drafted for each panel: take-home finding in 1–3 sentences, not chart mechanics
- [ ] Figure caption distinguishes what was done from what was found
- [ ] Git commit tagged at submission milestone; final PDF + TIFF archived alongside editable source

## Common Pitfalls

Avoid these publication figure issues. The first 10 are the most frequent; items 11–16 catch failures that land at peer review but not technical check:

1. **Font too small** — Text unreadable when printed at final column width. Design at final size and verify.
2. **JPEG format** — Creates artifacts in graphs; use PDF, PNG, or TIFF. Lossy compression blurs axis text and data lines.
3. **Red-green reliance** — ~8 % of males cannot distinguish; use Okabe-Ito, Paul Tol, or ColorBrewer palettes with redundant shape/line-style encoding.
4. **Low resolution** — Pixelated figures; verify DPI at final print size before export. 300 dpi floor is universal; 600+ for line art at Science/PNAS.
5. **Missing units** — All axes must include units in parentheses.
6. **3D effects / 3D pie charts** — Distorts angle and area judgments (Cleveland-McGill channel ranking). Use 2D bar or dot plots sorted by value.
7. **Chart junk** — Remove unnecessary gridlines, borders, drop shadows, textured fills.
8. **Truncated axes** — Bar charts must start at zero (length encodes). Truncation is legitimate for dot plots, effect-size plots, log scales, or trajectories with marked breaks.
9. **Inconsistent styling** — Different fonts/colors across figures in the same manuscript. One sans-serif family; three-level type scale applied uniformly.
10. **No error bars** — Always show uncertainty; specify type in caption (SD, SEM, 95 % CI, n = ?).
11. **Rainbow / jet heatmaps** — Non-monotonic luminance creates false banding at cyan/yellow boundaries; fails CVD; collapses in grayscale. Use viridis or cividis for sequential data; RdBu, PuOr, vik, or berlin for centered-on-zero diverging.
12. **Legend placement errors** — Corner legends force saccades back and forth across the figure. Prefer direct labeling at line endpoints, or a legend adjacent to (not across from) the panel it describes.
13. **Small-multiple violations** — Independent y-axes, or panels with different color encodings, destroy the value of a small-multiple grid. Share axes, scales, and color unless biologically impossible (and if so, mark the deviation).
14. **Inappropriate scale encoding** — Bubble plots where diameter is proportional to count (visual system perceives area, so 3 × count looks 9 × bigger). Encode count as area (`scale_size_area` in ggplot2); plot fold-changes on log₂ with symmetric limits.
15. **Legend for red-plus-green fluorescence** — Roughly 8 % of male readers cannot separate the two channels. Use magenta + green (or cyan + magenta) and include per-channel grayscale panels. Nature Methods has recommended this since Wong (2011).
16. **Overcrowded graphical abstract** — More than ~4 simultaneous encoded chunks overflows working memory (Cowan 2010). Identify 3–5 "acts" in an unambiguous reading order and defer detail to the figure legend.

## Workflow Summary

**Recommended workflow for publication figures:**

1. **Plan** — Determine target journal, figure type, and key message
2. **Configure** — Apply journal-specific style (dimensions, fonts, colors)
3. **Create** — Build figure with proper labels, colorblind-safe colors, statistics
4. **Verify** — Check size, fonts, colors, accessibility using checklist above
5. **Export** — Save in required formats with correct DPI
6. **Review** — View at actual print size in manuscript context

**Quick configuration:**
```python
# Example: Configure for Nature single-column figure
fig, ax = plt.subplots(figsize=(3.5, 2.5))  # 89mm width
plt.rcParams['font.size'] = 8
plt.rcParams['font.family'] = 'sans-serif'

# After creating figure, export
fig.savefig('figure1.pdf', dpi=300, bbox_inches='tight')
fig.savefig('figure1.png', dpi=300, bbox_inches='tight')
```

---

*See [oligon-brand `<design_foundation>`](../../oligon-brand/SKILL.md) for cross-format design philosophy and [plotting-libraries](../../plotting-libraries/SKILL.md) for implementation code. WCAG / accessibility validation helpers live in [`skills/shared/accessibility/`](../../shared/accessibility/). Icon-library licensing — BioRender, NIH BIOART, SciDraw, Servier, Noun Project — is catalogued in [`skills/shared/references/iconography-licensing.md`](../../shared/references/iconography-licensing.md). The unified 15-point pre-submission gate lives in [`skills/shared/references/pre_submission_checklist.md`](../../shared/references/pre_submission_checklist.md). Long-form cognitive-science and publisher-verified rationale: [`docs/design-rationale/infographic-graphic-abstract.md`](../../../docs/design-rationale/infographic-graphic-abstract.md).*
