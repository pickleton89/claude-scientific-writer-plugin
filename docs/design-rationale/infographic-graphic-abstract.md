# Designing scientific infographics and graphical abstracts for top-tier biomedical journals

A publishable graphical abstract differs from an amateurish one in three specific, measurable ways: it respects the working-memory ceiling of roughly four chunks, it encodes its most important claim on a perceptually accurate channel, and it meets the exact technical specifications its target journal publishes. Everything else — typography, color, icon choice, file format — is downstream of those three commitments. This report synthesizes the cognitive-science and visualization-research literature with current (April 2026) publisher Author Guidelines to give a senior cancer biologist the evidence base to defend design choices to co-authors and reviewers, and the specifications to export a figure that will clear technical check on the first pass.

The report is organized to follow the five-stage method described in the task brief. It scopes the primary literature across cognition, publisher policy, practitioner textbooks, and recent methodological commentary (Stage 1); every factual claim has been through a second-pass verification against its source, with unverifiable items omitted or flagged (Stage 2); confidence is labeled throughout using a three-tier scheme — "established," "evidence suggests," and "reasonable practitioners disagree" (Stage 3); structural principles are described so they could be rendered as diagrams (Stage 4); and high-value primary reads are pulled out of the reference list and called out by name (Stage 5).

---

## Graphical abstracts are a Cell Press phenomenon, not a universal standard

The first thing to settle is vocabulary, because the distinction drives both the design decisions and the journal specifications. A **graphical abstract** is a single, tightly bounded image — typically square or rectangular — that conveys the one central finding of a paper and is submitted as a required or optional companion to the text abstract. A **scientific infographic** is a broader, usually larger composition that tells a multi-step story for a non-specialist audience — a poster, a review-article centerpiece, a conference-talk overview, a lab-website hero image. The two share cognitive constraints but differ in affordances: a graphical abstract runs at postage-stamp size inside a search result or contents listing and must survive that scale, while an infographic can afford more layers of detail because readers engage with it for longer and often at a larger display.

Among the journals a cancer-biology researcher is likely to target, **graphical abstracts are required at Cell Press journals** (Cell, Cancer Cell, Immunity, Molecular Cell, Cell Reports, and the rest of the portfolio), and are optionally used at Nature Chemistry and Nature Chemical Biology with a very different rectangular geometry. They are **not used** at Nature (main), Nature Medicine, Nature Cancer, Nature Immunology, Nature Communications, the Science family (Science, Science Translational Medicine, Science Immunology), PNAS, eLife, NEJM, JAMA, The Lancet, or PLOS — each of which substitutes either a plain-language summary (eLife "digest," PLOS "Author Summary," PNAS "Significance Statement") or an editor-produced visual abstract (JAMA, NEJM in-house redraw). This is established and is the single most common source of wasted effort: a researcher produces an elaborate graphical abstract for a Nature Medicine submission that the journal will not publish. Where the advice in this report diverges between graphical abstracts and general figures, the text flags it explicitly.

## The cognitive ceiling that every figure has to clear

The binding constraint on any scientific figure is not ink, space, or color — it is the reader's attentional and working-memory budget. This is established. Three specific, quantified results set the budget.

First, **working memory holds about four chunks simultaneously**, not the seven famously reported by Miller (1956). Cowan's 2001 *Behavioral and Brain Sciences* reconsideration pins the capacity at three to five chunks when rehearsal and long-term recoding are blocked, and Cowan's 2010 *Current Directions in Psychological Science* summary treats four as the working estimate. Reasonable practitioners disagree at the margin — mixture-model fits by Van den Berg and colleagues give estimates closer to six, and the debate is not closed — but for figure design, planning around four simultaneous encodings is a safe floor. The practical implication is that a figure requiring the reader to hold more than four distinct encoded dimensions (x, y, color, shape, size, line type, panel row, panel column) will overflow working memory and force serial re-reading.

Second, **comparisons are serial, not parallel**. Franconeri, Padilla, Shah, Zacks and Hullman's 2021 *Psychological Science in the Public Interest* synthesis — the single most important secondary source in this literature and a recommended primary read — documents that while viewers extract ensemble statistics (mean, range, outliers) in a single glance via ensemble perception, they can only perform a handful of direct comparisons per second. Halford and colleagues' 2007 estimate, cited in Franconeri 2021, is that humans can consider interactions among roughly four variables at maximum in a single relational comparison. This is why dense heatmaps where the reader must mentally compare dozens of cells fail: the figure is fine for gist, useless for specifics, and unless the key comparison is pulled out as a direct-encoded annotation, it will not land.

Third, **Cleveland and McGill's 1984 *JASA* ranking of elementary perceptual tasks** is the empirical basis for almost every concrete chart recommendation in the literature. From most to least accurate for quantitative judgment: position along a common scale, position along non-aligned scales, length, angle and slope, area, volume and curvature, and finally shading and color saturation. Heer and Bostock replicated this on Mechanical Turk in 2010 with essentially identical results. Munzner's 2014 *Visualization Analysis and Design* formalizes it further and splits identity channels (spatial region > color hue > motion > shape) from magnitude channels. The practical corollary: encode the most important quantitative variable with position — a scatter, dot plot, or bar position — not with color saturation, bubble area, or 3D volume. 3D pie charts lose on two counts: they replace position with angle, and they distort angle with perspective. This is established and is the single highest-yield principle most figures could apply more aggressively.

Cleveland–McGill, Franconeri 2021, and Cowan 2010 together are the empirical foundation — **read these three directly** before any more design books.

## Pre-attentive features, Gestalt grouping, and the architecture of attention

How a figure directs attention before the reader consciously decides where to look is governed by Treisman's feature integration theory (Treisman and Gelade, *Cognitive Psychology* 1980; Treisman and Gormican, *Psychological Review* 1988). In a feature search — locating a red item among green distractors — reaction time is roughly flat with respect to the number of distractors, about 3 ms per item. In a conjunction search — locating a red *vertical* item among red-horizontal and green-vertical distractors — the slope climbs to about 60 ms per item, consistent with serial self-terminating search. Features demonstrated to be pre-attentive include hue, orientation, size, length, curvature, line terminators, closure, luminance contrast, motion, and stereoscopic depth. Features that are *not* pre-attentive — intersections, parallelism, arbitrary shape combinations, topological connectedness — require serial attention to detect. The practical consequence: to highlight a single key result, use one pre-attentive dimension, not a conjunction. "The red squares" is a conjunction; "the red one" or "the large one" is pre-attentive. A result highlighted by a conjunction of two non-distinctive features will be found only by readers who already know where to look.

The complementary machinery is Gestalt grouping, reviewed authoritatively in Wagemans and colleagues' 2012 *Psychological Bulletin* two-part synthesis. The classical Wertheimer principles — proximity, similarity, continuity, closure, common fate, symmetry — are joined by modern additions: uniform connectedness (Palmer and Rock 1994), common region (Palmer 1992), and synchrony. For a multi-panel figure, proximity groups related sub-panels; common region (a shared background tint or bounding box) defines a panel family; similarity of color or marker across panels binds the same condition; and connectedness — an actual line between two points — is a stronger group than proximity alone. The recurring mistake is placing a legend in the bottom-right of a 3×3 panel grid so that every panel requires a saccade to the legend and back. Direct labels at line endpoints respect proximity; a legend adjacent to the first panel respects it weakly; a corner legend violates it.

A related cognitive reality sets limits on how much the reader will actually notice. Rensink and colleagues' 1997 *Psychological Science* "flicker" paradigm showed that even large changes between two images often require dozens of alternations to detect when a brief blank intervenes. Simons and Chabris's 1999 invisible-gorilla study found that roughly half of observers, counting basketball passes, failed to notice a person in a gorilla suit crossing the scene; Drew, Võ and Wolfe's 2013 replication in radiologists found **83% failed to see a gorilla inserted at 48× the size of the nodules they were scanning for**. Expertise does not rescue the reader. For before/after comparisons in figures, the corollary is that panels must be aligned with shared axes and identical encodings; unexpected effects in an un-highlighted panel can be invisible even to trained readers. Call them out with arrows or annotations.

## Color that survives perception, printing, and disability

Color choice is where the evidence base is strongest and the failure rate in published figures is highest. Three bodies of evidence converge.

First, on **perceptual uniformity**: a colormap that maps equal data differences to equal perceived differences in a uniform color space like CIELAB or CAM02-UCS. The viridis family — viridis, plasma, inferno, magma, and the CVD-optimized cividis — was designed by van der Walt and Smith (SciPy 2015) to have monotonic perceptual lightness, perceptual uniformity, and robustness under common color-vision deficiencies. Cividis, from Nuñez, Anderton and Renslow's 2018 *PLOS ONE* paper, is mathematically optimized to deliver near-identical interpretation to normal and deuteranomalous viewers and should be the default for heatmaps read by mixed audiences. Viridis runs from dark purple (#440154) through teal to yellow (#FDE725) and remains ordered when printed in grayscale.

Second, on **the rainbow critique**: Rogowitz and Treinish's 1996 IBM Research note, republished as "Data Visualization: The End of the Rainbow" in *IEEE Spectrum* in 1998, laid out the case. Jet is non-monotonic in luminance (yellow is the brightest point, so mid-scale values attract attention like extremes); its hue ordering is learned, not perceptual; and it creates artifactual bands at cyan and yellow boundaries that engineers mistake for real data structure. Borkin and colleagues' 2011 *IEEE TVCG* study of coronary-artery visualizations is the strongest clinical evidence: diagnostic accuracy on atherosclerosis rose from 39% to 91% when the team switched from a 3D rainbow to a 2D red-to-black diverging colormap. Evidence suggests the full effect size conflates the 3D-to-2D change with the colormap change, so the headline figure should not be cited as a pure colormap effect, but the direction is unambiguous. Crameri, Shephard and Heron's 2020 *Nature Communications* paper ("The misuse of colour in science communication") is the current authoritative synthesis and hosts the free Scientific Colour Maps — batlow, vik, roma, lajolla, berlin — at fabiocrameri.ch/colourmaps. **Read Crameri 2020 directly**; it is the single most efficient intervention in most labs' figure output.

Third, on **color-vision deficiency**. Birch's 2012 *J. Opt. Soc. Am. A* survey gives European-male prevalence of red-green CVD at about 8% and European-female prevalence at about 0.4%, with lower rates in African and some Asian populations. Deuteranomaly and deuteranopia (M-cone affected) account for the majority; protanomaly and protanopia (L-cone) for most of the remainder; tritanopia (S-cone, autosomal rather than X-linked) is rare, well under 0.1%. The established design response is to avoid relying on color alone — WCAG 1.4.1 "Use of Color" requires this outside science as well — and to add redundant encoding via shape, line style, pattern, or direct label. For two-channel fluorescence, magenta-plus-green or cyan-plus-magenta have been widespread convention since Wong's 2011 *Nature Methods* "Points of view: Color blindness" piece. The **Okabe–Ito categorical palette** — eight hex codes (#E69F00 orange, #56B4E9 sky blue, #009E73 bluish green, #F0E442 yellow, #0072B2 blue, #D55E00 vermillion, #CC79A7 reddish purple, #000000 black) from Okabe and Ito's 2008 Color Universal Design note — is explicitly recommended by eLife's author guide and has become the default categorical palette in Claus Wilke's *Fundamentals of Data Visualization*. Paul Tol's SRON palettes and ColorBrewer (Harrower and Brewer, *Cartographic Journal* 2003) provide well-documented alternatives for specific needs; ColorBrewer's per-palette filters for colorblind-safe, print-friendly, and photocopy-safe are useful.

The pragmatic palette-by-data-type mapping is as follows. **Categorical data** (cell types, treatment groups) take Okabe-Ito, Paul Tol bright or muted, ColorBrewer Set2 or Dark2, or Tableau 10 — never a rainbow, never red and green alone. **Sequential data** (expression level, cell density) take viridis, cividis, magma, or Crameri's batlow and lajolla. **Diverging data** centered on a meaningful zero (log fold change, z-score) take ColorBrewer RdBu or PuOr or Crameri's vik or berlin — not RdYlGn, which fails deuteranopia. **Kaplan–Meier curves** should use high-contrast categorical palettes distinguishable at small line widths with redundant line-style encoding (solid, dashed, dotted); Paul Tol's three-color high-contrast set (#004488, #DDAA33, #BB5566) is a strong default that also reads in grayscale. **Heatmaps** centered on zero take diverging; unsigned intensity heatmaps take sequential.

Color should also clear WCAG 2.1 non-text contrast. WCAG 2.1 SC 1.4.11, a Level AA criterion, requires a 3:1 contrast ratio for graphical objects — meaning bars, wedges, data lines, and icons that are required to understand content. SC 1.4.3 requires 4.5:1 for normal text and 3:1 for large text (≥18 pt, or ≥14 pt bold). This is established. The usual failure is a pale-yellow data line on white (about 1.3:1 against white) or light-gray error bars that vanish on print.

## Accessibility beyond color: alt text and screen readers

Alt text for scientific figures is becoming a live submission requirement at several publishers, driven by the EU European Accessibility Act (enforced June 2025) and the US DOJ April 2024 rule adopting WCAG 2.1 AA for state and local government sites. Evidence suggests current status across the target journals is this: Springer Nature requests alt text for all figures and provides an AI-assisted "Alternative Text Assistant Tool" from late 2024; eLife and PLOS encourage but do not yet gate on alt text; Cell Press and Elsevier handle accessibility largely in post-production. Guidance on alt-text length varies among the DIAGRAM Center (as brief as possible), Taylor & Francis (40–50 words preferred, up to 100), and Karger (10–100 words). Reasonable practitioners disagree on the exact length, but convergence is clear: describe the **take-home finding**, not the chart mechanics. "Kaplan-Meier curve showing significantly shorter overall survival in TP53-mutant patients (median 14 vs 32 months; p=0.003) over 60 months of follow-up" is useful; "line graph with two curves" is not. For multi-panel figures, one alt text per panel beats one long description for the whole.

## Journal technical specifications, verified against current publisher pages

The table below is the reference the reader will use most often. Every cell was retrieved directly from a publisher-hosted page in April 2026. Items that could not be verified against a current primary source are omitted rather than guessed, in line with the verification protocol for this report. Where a specification appeared in one publisher document but not another, the conflict is flagged. Column-width, resolution, and font-size fields use the canonical units the publisher uses; they are not normalized.

| Publisher | Graphical abstract | GA dims / geometry | Figure max width | Minimum font size | Resolution (line / halftone) | Accepted formats | Color space | Special rules |
|---|---|---|---|---|---|---|---|---|
| **Cell Press** | Required at most titles | 1200 × 1200 px @ 300 dpi | 17.4 cm (full width) | 8 pt per GA guide (internal inconsistency with Matter's 12–16 pt — confirm with handling editor) | ≥300 ppi at final size | PDF (preferred), EPS, JPEG, TIFF; AI/PSD/PPT source accepted | RGB assumed but not explicitly stated in retrieved guide | ≤20 MB per figure; Arial or Avenir; embed fonts; GA reads top→bottom or left→right |
| **Nature portfolio** | Not used (exception: Nature Chemistry and Nature Chem Biol at 90 × 50 mm) | N/A for Nature, Nature Medicine, Nature Cancer, Nature Immunology | 183 mm (double), 89 mm (single), 120–136 mm (1.5) | 5 pt min / 7 pt max body; 8 pt bold lowercase panel labels (a, b, c) | 300–600 dpi for raster; vector for line art | Layered PSD or TIFF; AI, EPS, PDF vector; JPEG, CorelDraw (≤v8), Word, Excel, PPT accepted | **RGB recommended** (wider gamut, preserves fluorescence) | Do not rasterize or outline text; embed TrueType 2 or 42; Helvetica or Arial |
| **Science family** | Not used | N/A | 18.4 cm (2-col), 9 cm (single) | 6 pt minimum (Science Signaling); lines ≥0.5 pt | Line art 1200 dpi; color/grayscale ≥300 dpi (600+ preferred) | PDF (preferred), EPS, AI for vector; TIFF for raster | Color encouraged; RGB accepted | Helvetica preferred; no multi-page figures |
| **eLife** | Not used (uses plain-language digests) | N/A | Min 10 cm (full page 20 cm) at 300 dpi | Minimum pt size not specified in retrieved pages | 300 dpi across all types | TIFF (8-bit), PNG, JPEG | RGB | Preprint required; source data required for all quantitative figures |
| **PNAS** | Not used (Significance Statement replaces) | N/A | 17.8 cm (2-col), 8.7 cm (1-col), 11.4 cm (1.5-col) | 6 pt (~2 mm) min; 12 pt (~6 mm) max | Line art 600–1200 ppi; halftones 300 ppi | **TIFF, EPS, or high-res PDF only** (main figures) | **RGB required** (PNAS converts in-house) | Arial, Helvetica, Times, Symbol only; LZW TIFF compression; submit at final publication size |
| **NEJM** | Not used; in-house illustrators redraw | N/A | Column widths not verifiable in retrieved snippet | Redrawn in-house | Line art 1200 dpi; photos 300 dpi | Editable vector (AI, EPS, SVG) for data figures; PPT/Excel accepted | Not verifiable in retrieved snippet | Max 4 display items per Original Article |
| **JAMA Network** | Not used (Key Points + staff-produced Visual Abstract) | N/A | ≥5 inches for clinical images | Not verifiable in retrieved snippet | ≥350 ppi for clinical images | AI, EMF, EPS, PDF, TIF, JPG, PSD, PPT, XLS, WMF | RGB submission; JAMA converts | ≤1 MB per file at submission; ≤5 display items |
| **The Lancet** | Not used; illustrators redraw | N/A | 154 mm (2-col), 75 mm (1-col) per artwork PDF; 107 mm cited elsewhere (conflict) | 10 pt Times New Roman for headings per snippet | ≥300 dpi at final size | TIFF, JPG for photos; editable Word/PPT for CONSORT diagrams | Not verifiable in retrieved snippet | Photos created at final size or slightly larger |
| **PLOS (all journals)** | Not used (Author Summary) | N/A | 19.05 cm / 7.5 in / 2250 px at 300 dpi; min 6.68 cm / 789 px | **8–12 pt** Arial, Times, or Symbol only | 300–600 dpi (enforced min *and* max) | **TIFF or EPS only** for main figures | **RGB 8 bit/channel or grayscale only** | ≤10 MB per file; LZW TIFF; flattened, no layers, no alpha |

A few cross-cutting observations are worth pulling out. Every publisher surveyed specifies at least 300 dpi for halftones and photographs; that is the de facto universal floor. RGB is now the preferred color space at almost every publisher for initial submission — Nature and PNAS state it explicitly, Science and Cell Press accept it, JAMA and PLOS convert in-house from RGB. Single-column widths cluster between 8.7 and 9 cm and double-column widths between 17.4 and 18.4 cm, so a figure designed at Nature's 89 mm single-column width will scale cleanly to most others. PLOS has the most prescriptive specification and is the easiest to automate against; eLife is the loosest. NEJM, JAMA and The Lancet all redraw figures in-house at the production stage, so their submission-time specifications are functionally looser than their counterparts, but authors should still submit editable vector where data-driven plots are involved.

One unresolved conflict worth flagging to co-authors: Cell Press's graphical-abstract font-size guidance varies between 8–12 pt in the Cell GA guide PDF and 12–16 pt in Matter's figure-guidelines page. Confirm with the handling editor rather than guess. The Lancet's single-column figure width also appears inconsistent across publisher PDFs (75 mm in the artwork-guidelines PDF, 107 mm in the older information-for-authors PDF); design to the narrower figure and expand only on explicit confirmation.

## Composition patterns for mechanism, workflow, comparison, timeline, and space

Five canonical composition patterns cover the vast majority of what a cancer-biology or immunology lab actually produces. Each privileges some kinds of information and systematically obscures others; the designer's choice is less about which pattern is "correct" than about matching the pattern to the claim.

**Mechanism diagrams** — receptor-ligand binding, signaling cascades, the immune synapse — follow a compartmentalized convention: extracellular space at top or left, plasma membrane as a horizontal lipid bilayer, cytoplasm below, nucleus as a bounded oval anchoring transcriptional output. Shape codes proteins by family (receptors as transmembrane rectangles, kinases as ovals, transcription factors as rounded rectangles); color codes family membership; arrows encode activation (→) or inhibition (⊣). The CAR-T canonical decomposition arranges the modular construct vertically (scFv, hinge, transmembrane, costimulatory domain, CD3ζ ITAMs) next to the antigen-presenting tumor cell and the downstream cascade. Checkpoint-inhibitor figures place APC or tumor on one side and T cell on the other, with the PD-1/PD-L1 or CTLA-4/B7 axis defining the central interaction and the antibody drawn as a Y-shape in the interface. Aptamer-target binding typically shows a stem-loop secondary-structure rendering docked onto a protein surface, with an inset at higher magnification on the binding pocket. This pattern privileges causal order and spatial compartmentalization; it obscures kinetics, stoichiometry, and parallel or branching pathways, which will always read as a single linear chain. Useful exemplars in the literature include Majzner and Mackall's 2019 *Nature Medicine* review of CAR-T (the modular-domain diagram), Rafiq, Hackett and Brentjens's 2020 *Nature Reviews Clinical Oncology* CAR-T engineering review, and June and Sadelain's 2018 NEJM "Chimeric antigen receptor therapy" piece.

**Workflow and experimental schema** figures — the mouse-to-readout timeline familiar from every oncology preclinical paper — use a horizontal timeline with icons above the axis at decision points and time labels below. Treatment arms branch vertically from the timeline. Icon language is now dominated by BioRender conventions; this is not a bad thing (standardization aids reading) but it does mean most such figures look interchangeable. This pattern privileges temporal order at the cost of replication structure (n-per-group is often absent), randomization and blinding (invisible), and dropout (uncounted). Weissgerber and colleagues' 2015 *PLOS Biology* and 2019 *Circulation* surveys document the consequences of this invisibility. The single highest-yield improvement is to label n explicitly at each node and to make branches topologically explicit rather than compressing to a linear path.

**Comparison figures** implement Tufte's small multiples: an *m* × *n* grid of panels that share axes, scales, color encoding, and aspect ratio, with only one variable changing across panels. In a typical immunology paper, rows are conditions and columns are readouts (flow markers, cytokines). This pattern privileges direct visual comparison along one axis and preserves gist-level pattern recognition exactly as Franconeri 2021 describes. It obscures higher-order interactions that a 2D grid collapses and can lose small visual differences as panel size shrinks. The most common failure is independent y-axis scales across panels, which destroys the entire value proposition of small multiples; if the axes must differ for biological reasons, state this explicitly and call out the scale change.

**Timeline figures** take time on the x-axis and come in several canonical flavors: tumor-volume growth curves with per-mouse trajectories (thin) and group mean (bold) with SEM shading; Kaplan-Meier step functions with censor ticks, a number-at-risk table, hazard ratio with 95% CI and log-rank p in the plot area; swimmer plots where each patient occupies one horizontal bar with inline symbols for response, progression and censoring; waterfall plots sorted by best percent tumor-size change; spider plots of per-patient trajectories from a shared baseline. Each privileges a different aspect: Kaplan-Meier privileges survival distribution and obscures per-patient duration, swimmer plots privilege per-patient trajectory and obscure the distribution, waterfall privileges best response and obscures the time course. The reporting convention in immuno-oncology pairs Kaplan-Meier with swimmer plots, and waterfall with spider plots, precisely because no single chart answers all the relevant questions. A common pitfall: plotting mean tumor volume obscures bimodal responder/non-responder distributions — Weissgerber's "zone of invisibility."

**Spatial-relationship figures** — tumor microenvironment maps, anatomical maps, tissue compartments — navigate a tradeoff between anatomical realism and schematic clarity. An H&E or multiplexed immunofluorescence image at one level carries evidentiary weight; a schematic overlay at another level carries relational clarity. Jambor and colleagues' 2021 *PLOS Biology* meta-research audit of 580 papers documented that scale information is missing or incomplete in roughly half of image-based figures; insets are often unmarked on the overview; multichannel images are shown as merged only, without per-channel grayscale. The fix is to include scale bars (always), frame inset locations on the overview, present multi-channel fluorescence as merged *and* per-channel grayscale, and choose magenta-plus-green over red-plus-green as a matter of routine.

## Typography that survives at 5–7 points

Scientific figure typography is constrained by the physical size at which the text will be read — usually 5 to 7 points at final print dimensions — and by the journals' font embedding rules. Sans-serif dominates because serifs degrade at small sizes and at the resolutions where journal rasterization happens, because lower stroke contrast supports legibility at distance, and because sans-serif faces align cleanly with data marks and gridlines. Nature's research figure guide explicitly requires sans-serif and names Helvetica or Arial as preferred. Cell Press's current figure guidelines specify Avenir, with Arial as an accepted fallback. PNAS accepts Arial, Helvetica, Times or Symbol. The Journal of Cell Biology accepts Arial, Times New Roman, Courier New or Symbol, and explicitly says **do not convert text to outlines** — a position Nature shares, because their production systems need editable text for house-style changes, HTML translation, and accessibility.

The practical consequence is that the final-export workflow should embed fonts, not outline them, unless the journal asks otherwise. In Adobe Illustrator this is "Save As PDF → Preserve Illustrator Editing Capabilities on, subset fonts at 100%." In matplotlib, set `rcParams['pdf.fonttype'] = 42` so text exports as TrueType rather than Type 3 (the default), which rasterizes. In R/ggplot2, use `cairo_pdf()` or the `ragg` backend and embed fonts with `extrafont::embed_fonts()`. Keep an editable master file; the late-stage revision will always need it. Only convert text to outlines if the journal cannot render an unusual typeface, and communicate that choice to production.

For hierarchy within a figure at Nature-family final size, the working convention is 8 pt bold lowercase for panel labels (Nature explicitly lowercase — a, b, c — while Cell uses uppercase A, B, C), 7 pt regular for axis titles, 6–7 pt for tick labels and legends, and 5–7 pt for annotations, with a hard floor at 5 pt for Nature. Keep a single typeface family across all figures in a paper, and use weight and size — not different fonts — to build hierarchy. At 5 to 7 points, default tracking is often too tight; adding +10 to +25 units of letter-spacing in Illustrator (on its thousandths-of-em scale) helps labels on colored backgrounds, and all-caps headings genuinely need +50 to +100 units because caps lack the natural spacing cues of lowercase. Evidence suggests Inter (designed for screens, SIL Open Font License), Source Sans 3, and IBM Plex Sans are strong open-source alternatives where Helvetica and Avenir are not licensed; for LaTeX workflows, TeX Gyre Heros is metric-compatible with Helvetica and free.

## Iconography libraries and their current licensing terms

Licensing for the common biomedical-illustration libraries changed materially in the 2023-2026 window, and reliance on pre-2024 blog posts will produce wrong information. The terms below were verified directly from each provider in April 2026; a recheck at submission is nonetheless prudent for BioRender, whose terms were revised on 16 January 2026.

**BioRender** operates a tiered model. The free Basic tier allows educational and personal use only — posters, unpublished theses, grant applications — and carries a watermark on export; publication in a peer-reviewed journal is prohibited. Academic Individual subscriptions grant publication rights, but only if the subscriber is listed as first, co-first, co-senior, or last author; Academic Lab and Academic Institutional plans lift that restriction. For open-access journals, selecting the open-access option at export produces a CC BY 4.0 publication license automatically — authors do not need to contact BioRender separately. Publication licenses issued while the plan was active remain valid in perpetuity even after cancellation, but new edits or republication after cancellation revert to Basic terms. The required attribution in the figure caption is of the form "Created in BioRender. Smith, J (2026) https://BioRender.com/xxxxxx." Cell Press, Nature, Elsevier, eLife, PNAS, and APS routinely accept BioRender figures when the publication-license PDF is uploaded as a permission file.

**NIH BIOART Source** (bioart.niaid.nih.gov), launched October 2024 by the NIAID Visual and Medical Arts unit, makes most of its ~2,000 vetted illustrations available in the U.S. public domain — "free for any use, including educational, research, informational, and commercial purposes." A subset of entries carry a Creative Commons license that requires attribution; the metadata on each entry states which. Attribution is requested even for public-domain entries, in the form "NIAID Visual & Medical Arts. [date]. [title]. NIAID NIH BioArt Source. bioart.niaid.nih.gov/bioart/[id]." Files are supplied as EPS, AI, PNG, and SVG.

**SciDraw** (scidraw.io), founded by Federico Claudi and Alex Harston (the name Luke Campagnola that appears in some brief materials does not match SciDraw's own About page), licenses all uploads under CC BY 4.0. Attribution is required by citation; many drawings carry DOIs to simplify referencing. Commercial use, including in for-profit journals, is permitted.

**Smart Servier Medical Art** (smart.servier.com) re-licensed its medical image library as CC BY 4.0 after a relaunch around 2023 (previously CC BY 3.0). Sharing, adaptation, and remixing are permitted in any medium, including commercial, with attribution in the form "Image provided by Servier Medical Art (https://smart.servier.com/), licensed under CC BY 4.0." Site branding and logos are *not* covered by the CC BY 4.0 license.

**Noun Project** (thenounproject.com) offers most individual icons under CC BY 3.0 with mandatory attribution, a subset under CC0, and a royalty-free option via Icon Pro or Creator Pro subscription or a $4.99 single-icon purchase. For journal publication, either the free CC BY 3.0 tier with explicit inline attribution in the figure caption works or a Pro subscription eliminates the attribution requirement; for commercial or industry figures, Pro is the cleaner choice.

Three other libraries are worth flagging briefly. **Reactome** licenses its pathway illustrations, icon library, and branding under CC BY 4.0 (recently changed from an earlier pure-CC-BY-4.0 regime to include CC0 for annotation data). **WikiPathways** releases content under CC0 1.0, so no attribution is legally required. **Somersault 18:24**'s Library of Science and Medical Illustrations uses CC BY-NC-SA 4.0 — usable in academic non-commercial figures, but not safe for for-profit textbooks or industry-sponsored materials.

## A reproducible workflow between statistics code and vector editor

The canonical gold-standard workflow for a cancer-biology graphical abstract or multi-panel figure is stable across labs and reliable: generate quantitative plots in ggplot2 or matplotlib, export each as a PDF with embedded Type-42 fonts via Cairo or `rcParams`, open the panels in Illustrator (or Inkscape with the Scientific-Inkscape extensions), add schematic elements from BioRender or NIH BioArt or Servier, unify typography across all panels, align using artboards, and export the final as PDF and as 300–600 dpi TIFF for submission. The split of responsibility matters: data-plot details (values, axes, error bars) are fixed in the source script and re-exported, never edited in the vector editor — otherwise the figure drifts from the data and reproducibility breaks. Layout, panel labels, arrows, annotations, and schematic icons are composed in the vector editor.

Tool choice inside that workflow depends on cost, collaboration, and output fidelity. Adobe Illustrator remains the industry standard for final publication-quality vector editing and handles round-trip with matplotlib and ggplot2 output reliably; its subscription model (about $22.99/month single-app) is the main friction. Affinity Designer's status changed in late 2025: Canva acquired Serif in March 2024, and in October 2025 the three Affinity apps were unified into a single freemium "Affinity by Canva" v3, with v2 perpetual licenses still honored. Core editing remains subscription-free; only AI features require Canva Pro. Inkscape is free and open source, handles SVG natively, and with the Scientific Inkscape extensions (Burghoff) includes tools specifically for flattening matplotlib and ggplot2 PDF output, scaling plot areas without shrinking text, and homogenizing styles. Its CMYK support remains limited; post-export conversion via Scribus is the workaround. Figma, whose $20B Adobe merger was abandoned in December 2023 after regulatory obstacles and which filed S-1 for IPO in July 2025, remains independent and offers the best real-time collaborative editing but is not designed for print-quality output. Keynote and PowerPoint serve for drafts and talks but produce inconsistent vector output and are poor choices for final journal submission.

File-level hygiene is easy to get wrong. Vector formats — PDF, SVG, EPS, AI — should be used for anything geometric: line plots, bar charts, schematics, text, arrows, cartoons. Raster formats — TIFF, PNG — should be used only for pixel-native content: micrographs, H&E sections, Western blots, FACS density scatter, gels. For extremely dense scatterplots (above about 10⁵ points), rasterize only the point layer via `ggrastr::rasterize()` or matplotlib's `set_rasterized(True)` while keeping axes, text, and lines as vector. Keep a mirrored source-and-output directory structure, store BioRender license PDFs and attribution notes in the same tree, and use zero-padded figure numbers so alphabetic sort matches numeric order. Git-LFS handles large binary assets without bloating the repo; a `.gitattributes` with patterns like `*.ai filter=lfs`, `*.psd filter=lfs`, `*.tif filter=lfs` is a reasonable default. Tag commits at submission and revision milestones. Keep raw microscopy data outside the manuscript repo in institutional archive or Zenodo.

## Failure modes, with the cognitive principle and the fix

The most common figure failures are documented, named, and mapped to specific cognitive or technical principles. Each description below is a compressed before-and-after.

The **overloaded graphical abstract** crowds twenty icons and six bidirectional arrows into a single canvas with no visual hierarchy. This violates Cowan's working-memory ceiling of about four chunks. The fix is to identify three to five "acts," arrange them in an unambiguous reading order, establish one visual hierarchy cue (size or weight) for the main claim, and defer subordinate detail to the figure legend. Jambor and Bornhäuser's 2024 *PLOS Computational Biology* "Ten simple rules for designing graphical abstracts" is the current practical reference.

**Chartjunk** — 3D bar extrusions, textured fills, heavy gridlines, drop shadows — violates Tufte's data-ink ratio. The fix is flat bars with direct labels, faint gridlines only where needed to read values, and no borders. Evidence suggests chartjunk can aid long-term memorability (Bateman and colleagues' 2010 *CHI* paper, and Borkin et al. 2013 *IEEE TVCG*) at the cost of rapid accurate reading; reasonable practitioners disagree on the tradeoff. For peer-reviewed figures, prefer Cleveland-McGill accuracy; for conference talks and review-article centerpieces, modest pictorial elements combined with clear annotations can legitimately improve recall.

**3D pie charts** replace position judgment with angle judgment, then distort the angle with perspective. The fix is a horizontal bar chart or dot plot sorted by value.

**Rainbow or jet heatmaps** create perceptual bands at cyan and yellow boundaries that readers mistake for real data structure, are non-monotonic in luminance, fail under CVD, and collapse in grayscale. The fix is viridis or cividis for sequential data and RdBu, PuOr, vik, or berlin for centered-on-zero data.

**Axis truncation** of a bar chart — y-axis starting at 80% viability so a 2% effect looks enormous — distorts length encoding. The fix is to start bar charts at zero. Truncation is legitimate for dot plots (where position encodes), for difference and effect-size plots centered on zero, for log scales (where zero is undefined), and for trajectory plots where a common baseline is visible and a break is explicitly marked. Rougier, Droettboom and Bourne's 2014 PLOS Comp Biol "Ten simple rules for better figures" illustrates both cases directly.

**Inconsistent typography across panels** — Panel A in Arial 9 pt, Panel B in Helvetica 7 pt bold, axis labels in Times — forces the reader to re-parse per panel, violating Gestalt similarity. The fix is one sans-serif family across the manuscript with a three-level type scale applied consistently.

**Inadequate contrast** — light-gray 60% text on white, pale-yellow data lines, error bars invisible in print — fails WCAG 2.1's 3:1 non-text and 4.5:1 text thresholds. The fix is dark-gray (≥#404040) on white, avoiding yellow as a standalone foreground, and testing figures in grayscale by desaturating before submission.

**Inappropriate scale encoding** — bubble-plot diameter proportional to count, so a 3× count looks 9× bigger because the visual system perceives area — violates Stevens's power-law and Cleveland-McGill. The fix is to encode the value as bubble area (`scale_size_area` in ggplot2), and to plot fold-changes on a log₂ axis with symmetric limits.

**Small-multiple violations** break the central guarantee of small multiples: shared axes, shared scales, shared color. The fix is shared y-axes (or explicitly free ones with a clear note when biologically necessary) and a shared legend outside the grid.

**Legend placement errors** place the legend in a distant corner, forcing saccades back and forth. The fix is direct labeling of lines and bars at their endpoints, or a legend adjacent to (not across from) the panel it describes.

**Red-plus-green-only distinctions** fail for roughly 8% of male readers. The fix is magenta-plus-green or cyan-plus-magenta for two-channel fluorescence, plus per-channel grayscale panels, verified in Color Oracle or Coblis before submission. Nature Methods has recommended this alternative since Wong's 2011 piece.

## A pre-submission checklist

The list below is the exception to the prose-only rule of this report, because the items are genuinely discrete and the reader will run them as a checklist.

1. Confirm the journal's graphical-abstract policy (required, optional, or not used) and size specification against the current Author Guidelines page before beginning design.
2. Verify pixel dimensions, resolution (≥300 dpi halftone floor), and file-size cap against the target journal's specification table at export time.
3. Confirm fonts are embedded (Type 42 / TrueType) rather than outlined, unless the journal explicitly requests outlines; keep an editable source file.
4. Test the figure in grayscale and in deuteranopia simulation (Color Oracle, Coblis, or colorspace simulator) and confirm all information survives both.
5. Check that every color encodes information; remove color used only for decoration.
6. Check that the most important quantitative claim is encoded by position, not by color saturation, area, or volume.
7. Check that no panel carries more than about four simultaneous encoded channels.
8. Check bar-chart y-axes start at zero; legitimate truncation on other plot types is explicitly marked.
9. Check typography: one sans-serif family, three-level hierarchy (panel label, axis title, tick label), ≥5 pt floor for Nature or ≥6 pt for Science and PNAS, ≥8 pt for PLOS.
10. Check contrast: ≥4.5:1 for text, ≥3:1 for graphical objects, against the final background.
11. For multichannel fluorescence, confirm magenta-plus-green (or cyan-plus-magenta) rather than red-plus-green, and include per-channel grayscale panels.
12. Confirm scale bars are present on every image-based panel and inset locations are marked on the overview.
13. Confirm all BioRender, Servier, NIH BioArt, SciDraw, and Noun Project attributions are present in the figure legend or acknowledgments, with the BioRender publication-license PDF ready to upload as a permission file if required.
14. Draft alt text of one to three sentences describing the take-home finding, not the chart type, for each panel.
15. Tag the Git commit at the submission milestone and archive a copy of the final PDF and TIFF alongside the editable source on institutional storage.

## Conclusion

The gap between a publishable graphical abstract and an amateurish one is not a gap of artistic sensibility; it is a gap of applied cognitive science and careful attention to publisher specifications. Most of the common failures — overcrowding, chartjunk, rainbow heatmaps, red-green-only encoding, axis truncation, inconsistent typography, poorly placed legends — map to specific, named cognitive mechanisms (working-memory limits, Cleveland-McGill's channel ranking, Gestalt proximity, opponent-process color vision, WCAG contrast thresholds) and to specific, retrievable journal rules (Cell Press's 1200 × 1200 pixel square at 300 dpi, Nature's 5-pt font floor and RGB preference, PLOS's TIFF/EPS-only rule). None of these require a graphic-design education to apply; they require a willingness to treat the reader's visual system as a measurement instrument with documented limits, and to treat Author Guidelines pages as primary sources to be verified, not summarized from memory.

The three highest-leverage changes most working figures could make are these. First, demote color from its default "decorate every series" role and use it only where it encodes information, with viridis or cividis for sequential data and Okabe-Ito or Paul Tol high-contrast for categorical data. Second, map the most important quantitative claim to position, not to color or area, and let comparisons be visually adjacent on a shared scale. Third, design at final print size and verify typography, contrast, and grayscale legibility before export — not after a reviewer flags it. The evidence base for each of these is strong enough to cite in a response to reviewers; the cognitive-science literature treats them as settled, and the practitioner literature (Tufte, Cairo, Few, Munzner, Ware; Rougier 2014, Weissgerber 2015 and 2019, Crameri 2020, Jambor 2021, Franconeri 2021) converges on the same conclusions from independent angles.

The specifications in the comparison table above, and the licensing status of each asset library, should be re-verified against the publisher's own current page at the time of each submission. The verification protocol of this report is the protocol the reader should apply: draft the claim, find the primary source, and accept the number only when it is on the page.

---

## Recommended primary reads

These are the sources to download and read directly, in priority order for a working cancer biologist:

Franconeri, Padilla, Shah, Zacks and Hullman (2021), "The Science of Visual Data Communication: What Works," *Psychological Science in the Public Interest* 22(3), 110–161 — the single best evidence synthesis. Cleveland and McGill (1984), "Graphical perception: theory, experimentation, and application," *JASA* 79(387), 531–554 — the empirical foundation. Crameri, Shephard and Heron (2020), "The misuse of colour in science communication," *Nature Communications* 11, 5444 — the authoritative color reference, with free Scientific Colour Maps. Jambor and colleagues (2021), "Creating clear and informative image-based figures for scientific publications," *PLOS Biology* 19, e3001161 — the current standard for microscopy and IF figures. Rougier, Droettboom and Bourne (2014), "Ten Simple Rules for Better Figures," *PLOS Computational Biology* 10, e1003833 — the shortest practical reference. Weissgerber and colleagues (2015), "Beyond Bar and Line Graphs," *PLOS Biology* 13, e1002128, and the 2019 follow-up "Reveal, Don't Conceal," *Circulation* 140, 1506–1518 — the biomedical-specific evidence on data presentation. For accessibility, Wong (2011) "Points of view: Color blindness," *Nature Methods* 8, 441, and Katsnelson (2021) "Colour me better," *Nature* 598, 224–225. For graphical abstracts specifically, Jambor and Bornhäuser (2024) "Ten simple rules for designing graphical abstracts," *PLOS Computational Biology* 20, e1011789. As a book, Munzner's *Visualization Analysis and Design* (2014) for the channels-ranking framework; Tufte's *Visual Display of Quantitative Information* for data-ink ratio and small multiples.

## References

Bateman, S., et al. (2010). Useful junk? The effects of visual embellishment on comprehension and memorability of charts. *CHI 2010*.

Birch, J. (2012). Worldwide prevalence of red–green color deficiency. *Journal of the Optical Society of America A*, 29(3), 313–320.

Borkin, M. A., Gajos, K. Z., Peters, A., Mitsouras, D., Melchionna, S., Rybicki, F. J., Feldman, C. L., & Pfister, H. (2011). Evaluation of artery visualizations for heart disease diagnosis. *IEEE Transactions on Visualization and Computer Graphics*, 17(12), 2479–2488.

Borkin, M. A., Vo, A. A., Bylinskii, Z., Isola, P., Sunkavalli, S., Oliva, A., & Pfister, H. (2013). What makes a visualization memorable? *IEEE Transactions on Visualization and Computer Graphics*, 19(12), 2306–2315.

Cairo, A. (2012). *The Functional Art*. New Riders.

Cairo, A. (2016). *The Truthful Art*. New Riders.

Cell Press figure guidelines, graphical-abstract guide, and final file requirements. https://www.cell.com/pb/assets/raw/shared/figureguidelines/GA_guide.pdf and https://www.cell.com/information-for-authors/figure-guidelines (retrieved April 2026).

Cleveland, W. S., & McGill, R. (1984). Graphical perception: theory, experimentation, and application to the development of graphical methods. *Journal of the American Statistical Association*, 79(387), 531–554.

Cowan, N. (2001). The magical number 4 in short-term memory. *Behavioral and Brain Sciences*, 24(1), 87–114.

Cowan, N. (2010). The magical mystery four. *Current Directions in Psychological Science*, 19(1), 51–57.

Crameri, F., Shephard, G. E., & Heron, P. J. (2020). The misuse of colour in science communication. *Nature Communications*, 11, 5444.

Drew, T., Võ, M. L.-H., & Wolfe, J. M. (2013). The invisible gorilla strikes again: Sustained inattentional blindness in expert observers. *Psychological Science*, 24(9), 1848–1853.

eLife author guide. https://elife-rp.msubmit.net/html/elife-rp_author_instructions.html (retrieved April 2026).

Elliott, K. (2016). 39 studies about human perception in 30 minutes. OpenVis Conf / Medium.

Few, S. (2012). *Show Me the Numbers: Designing Tables and Graphs to Enlighten* (2nd ed.). Analytics Press.

Franconeri, S. L., Padilla, L. M., Shah, P., Zacks, J. M., & Hullman, J. (2021). The science of visual data communication: What works. *Psychological Science in the Public Interest*, 22(3), 110–161.

Harrower, M., & Brewer, C. A. (2003). ColorBrewer.org: An online tool for selecting colour schemes for maps. *The Cartographic Journal*, 40(1), 27–37.

Heer, J., & Bostock, M. (2010). Crowdsourcing graphical perception. *Proc. ACM CHI 2010*, 203–212.

Hullman, J., Resnick, P., & Adar, E. (2015). Hypothetical outcome plots outperform error bars and violin plots. *PLOS ONE*, 10(11), e0142444.

JAMA Network instructions for authors and Technical Requirements for Figures. https://jamanetwork.com/journals/jama/pages/instructions-for-authors (retrieved April 2026).

Jambor, H., Bornhäuser, M., et al. (2021). Creating clear and informative image-based figures for scientific publications. *PLOS Biology*, 19(3), e3001161.

Jambor, H., & Bornhäuser, M. (2024). Ten simple rules for designing graphical abstracts. *PLOS Computational Biology*, 20, e1011789.

Kale, A., Nguyen, F., Kay, M., & Hullman, J. (2019). Hypothetical outcome plots help untrained observers judge trends in ambiguous data. *IEEE TVCG*, 25(1), 892–902.

Katsnelson, A. (2021). Colour me better: fixing figures for colour blindness. *Nature*, 598, 224–225.

Klebanoff, M. A. (2021). Use of color in journal figures. *Pediatric Research*, 90, 22.

Lancet information for authors and artwork guidelines. https://www.thelancet.com/pb/assets/raw/Lancet/authors/artwork-guidelines.pdf (retrieved April 2026).

Miller, G. A. (1956). The magical number seven, plus or minus two. *Psychological Review*, 63, 81–97.

Munzner, T. (2014). *Visualization Analysis and Design*. AK Peters/CRC Press.

Nature author guidelines, final submission guide, and research figure guide. https://www.nature.com/nature/for-authors/final-submission and https://research-figure-guide.nature.com/ (retrieved April 2026).

NEJM author center and Technical Guidelines for Figures. https://www.nejm.org/author-center/new-manuscripts (retrieved April 2026).

NIH BIOART Source terms. https://bioart.niaid.nih.gov/terms (retrieved April 2026).

Nuñez, J. R., Anderton, C. R., & Renslow, R. S. (2018). Optimizing colormaps with consideration for color vision deficiency. *PLOS ONE*, 13(7), e0199239.

Okabe, M., & Ito, K. (2008). Color Universal Design. https://jfly.uni-koeln.de/color/.

Paul Tol colour schemes technical note. https://personal.sron.nl/~pault/.

PLOS figure guidelines. https://journals.plos.org/plosone/s/figures (retrieved April 2026).

PNAS Digital Art Guidelines. https://www.pnas.org/author-center/submitting-your-manuscript (retrieved April 2026).

Rensink, R. A., O'Regan, J. K., & Clark, J. J. (1997). To see or not to see: The need for attention to perceive changes in scenes. *Psychological Science*, 8(5), 368–373.

Rogowitz, B. E., & Treinish, L. A. (1998). Data visualization: The end of the rainbow. *IEEE Spectrum*, 35(12), 52–59.

Rougier, N. P., Droettboom, M., & Bourne, P. E. (2014). Ten simple rules for better figures. *PLOS Computational Biology*, 10(9), e1003833.

Science family instructions for preparing manuscripts. https://www.science.org/content/page/instructions-preparing-initial-manuscript (retrieved April 2026).

SciDraw terms. https://scidraw.io/terms (retrieved April 2026).

Simons, D. J., & Chabris, C. F. (1999). Gorillas in our midst. *Perception*, 28(9), 1059–1074.

Smart Servier Medical Art terms of use. https://smart.servier.com/terms-of-use (retrieved April 2026).

Smith, N., & van der Walt, S. (2015). A better default colormap for matplotlib. SciPy 2015; https://bids.github.io/colormap/.

The Noun Project licensing. https://thenounproject.com/legal/ (retrieved April 2026).

Treisman, A., & Gelade, G. (1980). A feature-integration theory of attention. *Cognitive Psychology*, 12(1), 97–136.

Treisman, A., & Gormican, S. (1988). Feature analysis in early vision. *Psychological Review*, 95(1), 15–48.

Tufte, E. R. (1983, 2nd ed. 2001). *The Visual Display of Quantitative Information*. Graphics Press.

Tufte, E. R. (1990). *Envisioning Information*. Graphics Press.

Tufte, E. R. (1997). *Visual Explanations*. Graphics Press.

Tufte, E. R. (2006). *Beautiful Evidence*. Graphics Press.

Wagemans, J., Elder, J. H., Kubovy, M., Palmer, S. E., Peterson, M. A., Singh, M., & von der Heydt, R. (2012). A century of Gestalt psychology in visual perception, I and II. *Psychological Bulletin*, 138(6), 1172–1252.

Ware, C. (2012). *Information Visualization: Perception for Design* (3rd ed.). Morgan Kaufmann.

W3C Web Content Accessibility Guidelines 2.1 and 2.2. https://www.w3.org/WAI/WCAG21/Understanding/.

Weissgerber, T. L., Milic, N. M., Winham, S. J., & Garovic, V. D. (2015). Beyond bar and line graphs. *PLOS Biology*, 13(4), e1002128.

Weissgerber, T. L., et al. (2019). Reveal, don't conceal. *Circulation*, 140, 1506–1518.

Wilke, C. O. (2019). *Fundamentals of Data Visualization*. O'Reilly. https://clauswilke.com/dataviz.

Wong, B. (2011). Points of view: Color blindness. *Nature Methods*, 8, 441.