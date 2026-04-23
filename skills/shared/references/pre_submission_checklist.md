# Pre-Submission Checklist for Scientific Visuals

> **15-point unified quality gate** for graphical abstracts, posters, schematics, and data plots destined for peer-reviewed publication. Each item states *the check*, *why it matters* (cognitive principle or journal rule), and *how to verify* (tool or command).

Used by `paperbanana`, `research-posters`, `scientific-schematics`, `plotting-libraries`. Skills may extend this checklist with output-specific items but should not replace it. Long-form rationale: [`docs/design-rationale/infographic-graphic-abstract.md`](../../../docs/design-rationale/infographic-graphic-abstract.md).

---

### 1. Confirm the journal's graphical-abstract policy

**Check:** before beginning design, confirm the target journal's GA policy (required, optional, or not used) and size specification against the current Author Guidelines.

**Why:** producing an elaborate graphical abstract for a venue that does not publish them is the most common wasted-effort failure. Cell Press requires them; Nature main, Nature Medicine, Science family, PNAS, eLife, PLOS, JAMA, NEJM, and The Lancet do not.

**How:** check `../../venue-templates/references/figure_specs.md § Graphical-Abstract Specifications`. Re-verify on the journal's current Author Guidelines page.

---

### 2. Verify dimensions, resolution, and file-size cap

**Check:** pixel dimensions match target journal (e.g. 1200 × 1200 px for Cell GA); resolution ≥300 dpi halftone floor (600–1200 dpi for line art at Science/PNAS); file size within cap (Cell ≤20 MB, PLOS ≤10 MB, JAMA ≤1 MB).

**Why:** failing technical check on first submission wastes a review round. Every major publisher enforces these numerically.

**How:** `figure_specs.md § Journal Requirements` for per-venue specs. Verify export dimensions with `identify file.png` (ImageMagick) or `pdfinfo file.pdf`. In matplotlib: `fig.savefig('fig.pdf', dpi=300)` and check final file size.

---

### 3. Confirm fonts are embedded (Type 42 / TrueType), not outlined

**Check:** fonts embedded in the final PDF/EPS unless the journal explicitly requests outlines. Keep an editable source file regardless.

**Why:** publishers need editable text for house-style changes, HTML translation, and accessibility tooling. Outlining breaks all three.

**How:** matplotlib `rcParams['pdf.fonttype'] = 42`; R `ggsave(..., device = cairo_pdf)` or `extrafont::embed_fonts()`; Illustrator "Save As PDF → Preserve Illustrator Editing Capabilities ON, subset fonts at 100 %". Verify with `pdffonts file.pdf` (expect `emb=yes`).

---

### 4. Test figure in grayscale and under CVD simulation

**Check:** figure remains interpretable when desaturated and under deuteranopia/protanopia simulation.

**Why:** ~8 % of males have red-green CVD (Birch 2012); many journals print or copy in grayscale. Redundant encoding (shape, line style, label) rescues both cases.

**How:** Color Oracle (desktop, free), Coblis (web), or Python `colorspacious` with a CVD space spec: `cvd = {"name": "sRGB1+CVD", "cvd_type": "deuteranomaly", "severity": 50}; colorspacious.cspace_convert(rgb, cvd, "sRGB1")`. For grayscale preview, use scikit-image `rgb2gray(img)` or convert via `np.dot(rgb[...,:3], [0.299, 0.587, 0.114])`.

---

### 5. Check that every color encodes information

**Check:** remove color used only for decoration. Every hue in the figure must map to a data or semantic dimension.

**Why:** decorative color competes with informative color for the reader's pre-attentive channel (Treisman & Gelade 1980). A pre-attentive feature used for decoration is wasted.

**How:** mentally strip color from the figure and ask: "Does the reader still know what each color means?" If not, the color encodes nothing — remove it.

---

### 6. Encode the most important claim with position, not color or area

**Check:** the most important quantitative variable is on a position channel (scatter, dot plot, bar position), not color saturation, bubble area, or 3D volume.

**Why:** Cleveland & McGill (1984) ranked elementary perceptual tasks for quantitative judgment. Position on a common scale is the most accurate; shading and color saturation are the least. 3D volume is worse still.

**How:** if the main comparison is encoded by color, switch to a dot plot with position encoding. If by bubble area, ensure `scale_size_area()` is used (area-proportional, not diameter-proportional). Replace 3D pies with horizontal bars sorted by value.

---

### 7. Limit simultaneous encoded channels to ~4 per panel

**Check:** no panel uses more than about four simultaneous encoded dimensions (x, y, color, shape, size, line type, panel row, panel column).

**Why:** working memory holds about four chunks (Cowan 2010). Figures exceeding this force serial re-reading and lose gist.

**How:** count encoded dimensions per panel. If over four, either split into a small-multiple grid or remove lower-priority encodings.

---

### 8. Bar-chart y-axes start at zero; truncation elsewhere is marked

**Check:** bar chart y-axes start at zero. Legitimate truncation on dot plots, effect-size plots, log scales, or trajectories is explicitly marked with a break symbol.

**Why:** bars encode length, which the reader compares to the baseline. Starting at 80 % makes a 2 % effect look enormous (Rougier, Droettboom & Bourne 2014).

**How:** in matplotlib, `ax.set_ylim(bottom=0)` for bar charts. Use `brokenaxes` for legitimate breaks. For log scales, axis break isn't required but label the scale explicitly.

---

### 9. Typography: one sans-serif family, three-level hierarchy, venue-appropriate floor

**Check:** single sans-serif family across the manuscript; three-level hierarchy (panel label ≥8 pt bold > axis title ≥7 pt > tick label ≥5–7 pt). Floor: ≥5 pt at Nature; ≥6 pt at Science/PNAS; ≥8 pt at PLOS.

**Why:** serifs degrade at the resolutions where journal rasterization happens; mixing families breaks Gestalt similarity and forces re-parse per panel.

**How:** preferred faces: Arial, Helvetica, Avenir (Cell Press). Open alternatives: Inter, Source Sans 3, IBM Plex Sans. For LaTeX: TeX Gyre Heros (metric-compatible with Helvetica).

---

### 10. Contrast meets WCAG 2.1: ≥4.5:1 text, ≥3:1 graphical objects

**Check:** text contrast ratio ≥4.5:1 against background (3:1 for ≥18 pt or ≥14 pt bold); graphical objects (bars, wedges, data lines, icons) ≥3:1.

**Why:** WCAG 2.1 SC 1.4.3 (text) and SC 1.4.11 (non-text) are enforced by the EU European Accessibility Act (June 2025) and US DOJ WCAG 2.1 AA rule (April 2024). Pale-yellow data lines on white (~1.3:1) fail both.

**How:** WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/) for the WCAG 2.1 ratio, or Python `wcag-contrast-ratio` / `colour` libraries for programmatic computation. APCA (https://www.myndex.com/APCA/) is the newer WCAG 3 draft algorithm with different thresholds — use it for forward compatibility, not for 2.1 compliance. Avoid yellow as standalone foreground.

---

### 11. Two-channel fluorescence: magenta + green (or cyan + magenta) with per-channel grayscale panels

**Check:** multichannel fluorescence uses magenta + green or cyan + magenta, not red + green. Include per-channel grayscale panels in addition to the merged view.

**Why:** red + green confuses ~8 % of male readers. Magenta + green is distinguishable under deuteranopia and protanopia. Nature Methods has recommended this since Wong (2011).

**How:** in ImageJ/Fiji, use "Magenta/Green" or "Cyan/Magenta" LUTs rather than "Red/Green". Export merged + one grayscale per channel.

---

### 12. Scale bars on every image panel; inset locations framed on overview

**Check:** every image-based panel (micrograph, IF, H&E, tissue section) has a scale bar. Inset locations are framed with a rectangle on the overview.

**Why:** Jambor et al. (2021) found scale information missing or incomplete in ~50 % of image-based figures; insets are often unmarked on the overview.

**How:** Fiji "Tools → Scale Bar"; matplotlib `matplotlib-scalebar`. Draw inset rectangle with `Rectangle((x, y), w, h)` on the overview.

---

### 13. All icon and illustration sources attributed; publication licenses ready

**Check:** every BioRender, Servier, NIH BIOART, SciDraw, and Noun Project icon has its attribution in the figure legend or acknowledgments. BioRender publication-license PDF is ready to upload as a permission file.

**Why:** licensing terms changed materially in 2023–2026 and continue to change. Wrong attribution risks manuscript rejection or post-publication retraction.

**How:** see `iconography-licensing.md` for current terms and copy-paste attribution templates. Re-verify at submission.

---

### 14. Alt text drafted: take-home finding, not chart mechanics

**Check:** alt text of 1–3 sentences per panel, describing the scientific finding. For multi-panel figures, one alt text per panel beats one long description.

**Why:** Springer Nature requests alt text (with AI-assisted tool from late 2024); EU European Accessibility Act and US DOJ WCAG 2.1 AA adoption are driving universal requirement. "Line graph with two curves" is not useful; the finding is.

**How:** formula: *"[Chart type, if essential] showing [finding with key numbers and comparison] over [time/condition range]."* Example: *"Kaplan-Meier curve showing significantly shorter overall survival in TP53-mutant patients (median 14 vs 32 months; p = 0.003) over 60 months of follow-up."*

---

### 15. Archive editable source; tag submission commit

**Check:** editable master (AI, PSD, or source PDF with layers) archived alongside the final PDF and TIFF on institutional storage. Git commit tagged at submission milestone.

**Why:** reviewer revisions will request changes to the editable file; rasterized final outputs cannot be recovered. Submission tags make re-creating the exact submitted figure trivial.

**How:** `git tag submission-2026-04-23`; store raw microscopy outside the manuscript repo (institutional archive or Zenodo). Use `.gitattributes` with `*.ai filter=lfs`, `*.psd filter=lfs`, `*.tif filter=lfs` to keep the repo lean.

---

## Related

- `iconography-licensing.md` — detailed terms for BioRender, NIH BIOART, SciDraw, Servier, Noun Project, etc.
- `../accessibility/` — CVD simulation, WCAG contrast, and grayscale testing helpers.
- `../../venue-templates/references/figure_specs.md` — per-journal dimensions, DPI, formats, color-space requirements.
- `../../oligon-brand/SKILL.md` — cross-format design foundation (cognitive principles + brand tokens).
- `../../../docs/design-rationale/infographic-graphic-abstract.md` — long-form cognitive-science and publisher-verified rationale.
