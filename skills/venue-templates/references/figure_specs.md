# Figure Specifications — Cross-Cutting Reference

> Cross-cutting figure-format requirements that complement per-venue style files.
> Version: 1.0.0
> Used by: plotting-libraries, paperbanana, scientific-schematics, research-posters, scientific-slides
>
> **Per-venue specifics** (column widths, page dimensions, submission portals) live in `nature_science_style.md`, `cell_press_style.md`, `medical_journal_styles.md`, `journals_formatting.md`, etc.
> **This file** centralises specs that recur across venues: graphical abstracts, font embedding, color spaces, alt text.

---

## 1. Graphical Abstract Specifications

Most venues do **not** use graphical abstracts. Confirm before designing.

| Venue | GA required? | Dimensions | DPI | Max size | Format | Notes |
|---|---|---|---|---|---|---|
| Cell Press (Cell, Cell Reports, Molecular Cell, Cancer Cell, Immunity, etc.) | **Required** | 1200 × 1200 px square | ≥300 | ≤20 MB | TIFF or JPEG, RGB | Font size 8–12 pt (per GA guide); some Cell journals state 12–16 pt — confirm with editor |
| Nature Chemistry, Nature Chemical Biology | **Required** | 90 × 50 mm rectangle | ≥300 | — | EPS or high-res JPG | Rectangular not square |
| Nature (main), Nature Medicine, Nature Cancer, Nature Immunology, Nature Communications | Not used | — | — | — | — | Use plain-language summary instead |
| Science | Not used | — | — | — | — | Editor's summary handled in-house |
| PNAS | Not used | — | — | — | — | Significance Statement (≤120 words) instead |
| eLife | Not used | — | — | — | — | "Plain-language summary" required |
| PLOS journals | Not used | — | — | — | — | Author Summary required for PLOS Genetics / Computational Biology |
| NEJM, JAMA, Lancet | Not used | — | — | — | — | Visual abstracts may be promotional, not editorial |

**Pre-design check:** If the figure is intended as a graphical abstract, verify the journal accepts one and uses a square or rectangular layout. Designing a square graphical abstract for a venue that doesn't use one wastes effort.

---

## 2. Color Space

| Color space | When to use | Venues that require / prefer |
|---|---|---|
| **RGB** | Default for online and most print workflows in 2026; publishers convert in-house | Nature (required), PNAS (required), Science (accepted), Cell (accepted), eLife, PLOS (RGB 8-bit/channel or grayscale only) |
| **CMYK** | Legacy print-only workflows; rarely required now | Some traditional print-only journals; check submission guidelines |
| **Grayscale** | Single-channel data, accessibility prints | Always survives the grayscale test (see oligon-brand grayscale verification) |

**Recommendation:** Submit RGB unless the venue explicitly requires CMYK. The publisher handles conversion to CMYK for print runs.

---

## 3. Font Embedding (Type 42 / TrueType)

Embed fonts so reviewers and typesetters can re-flow text without rasterisation. Outlining text destroys editability and violates publisher submission guidelines for most major venues.

### matplotlib (Python)

```python
import matplotlib.pyplot as plt
plt.rcParams['pdf.fonttype'] = 42  # Type 42 / TrueType
plt.rcParams['ps.fonttype'] = 42
# Then save as usual
plt.savefig('figure.pdf')
```

### ggplot2 (R)

```r
# Option A — cairo_pdf device (recommended)
ggsave("figure.pdf", plot = p, device = cairo_pdf, width = 89, height = 60, units = "mm")

# Option B — extrafont package
library(extrafont)
# ...build plot p...
ggsave("figure.pdf", plot = p, width = 89, height = 60, units = "mm")
embed_fonts("figure.pdf")
```

### Adobe Illustrator

File → Save As → Adobe PDF → Subset fonts when percent of characters used is **100%** (embeds all glyphs without subsetting). Do **not** outline text unless the journal explicitly requests outlines.

### Verification

```bash
pdffonts figure.pdf
```

Look for `type` column showing `Type 1C`, `Type 42`, or `TrueType` — never `Type 3` (rasterised) or missing rows. `emb` column should be `yes` for every row.

---

## 4. Alt Text

Alt text is required by the EU European Accessibility Act (in force June 2025) and US DOJ WCAG 2.1 AA rule (April 2024) for journal websites and supplementary HTML. Most major publishers now either accept or require alt text on figure submission.

### Formula (Fujii 2026; Jambor 2025)

Two sentences. **Describe the take-home finding, not the chart mechanics.**

- ✅ "Treatment with compound X reduced tumour volume by 60% relative to vehicle (left bars), while combination therapy reduced volume by 85% (right bars). The combination effect exceeds additive prediction."
- ❌ "Bar chart showing four bars, two grey and two blue, with error bars and asterisks above each bar."

The first sentence states the finding; the second states the qualifier or comparison. Avoid describing colours, shapes, or chart types unless the visual encoding is itself the point.

### Multi-panel figures

Write **one alt-text per panel**, not one combined description. Each panel's alt text should stand alone if the others are stripped.

---

## 5. Known Conflicts

Where publisher documents disagree, confirm with the editor rather than guessing.

| Conflict | Document A | Document B | Resolution |
|---|---|---|---|
| Cell Press graphical abstract font size | GA guide says 8–12 pt | *Matter* author guidelines say 12–16 pt | Email editor; default to 12 pt for safety |
| Lancet single-column width | Some pages cite 75 mm | Other pages cite 107 mm | Use 75 mm; confirm at proof stage |
| Nature subseries column widths | Main Nature uses 89 / 183 mm | Some subseries (e.g., Nature Methods) cite 88 / 180 mm | Use main Nature spec unless subseries explicitly differs |

---

## Cross-references

| Topic | See |
|---|---|
| Per-venue column widths, DPI floors, page limits | `journals_formatting.md`, `nature_science_style.md`, `cell_press_style.md`, `medical_journal_styles.md`, `bioinformatics_journals.md` |
| Conference posters | `posters_guidelines.md` |
| Iconography licensing (BioRender, NIH BIOART, Servier, etc.) | `../shared/references/iconography-licensing.md` |
| 15-point pre-submission quality gate | `../shared/references/pre_submission_checklist.md` |
| Figure-vs-table decision aid | `../shared/references/figure_vs_table_decision.md` |
| Communication-context matrix (audience × time × interaction) | `../shared/references/communication_context_matrix.md` |
| Font embedding in matplotlib programmatically | `plotting-libraries/scripts/plotting_params.py::JOURNAL_SPECS` |

---

## References

- Fujii, R. *Nat Hum Behav* (2026). doi:10.1038/s41562-026-02466-9 — alt-text formula; "describe the finding, not the mechanics."
- Jambor, H. K. *Nat Cell Biol* **27**, 879–883 (2025) — figure accessibility.
- EU Directive 2019/882 (European Accessibility Act), in force 28 June 2025.
- US DOJ ADA Title II web accessibility rule (28 CFR 35.200), published April 2024 — adopts WCAG 2.1 AA.
