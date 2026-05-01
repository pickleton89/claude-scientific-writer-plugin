# Communication-Context Matrix — Audience × Time × Interaction → Figure Complexity

> Cross-skill decision aid mapping the viewing context of a figure to the appropriate level of complexity, detail, and annotation.
> Version: 1.0.0
> Used by: plotting-libraries, scientific-slides, scientific-schematics, paperbanana, research-posters, scientific-writing
> Source: Fujii, R. *Nat Hum Behav* (2026) §"Consider time and interaction" — doi:10.1038/s41562-026-02466-9.

---

## Why this matters

The same dataset can be visualised in many ways; the right visualisation depends strongly on **how the figure will be encountered**. A figure designed for a colleague at a lab meeting differs from one designed for a 2-minute oral talk, which differs from one designed for an asynchronous research-article reader. The variables that drive that difference are:

1. **Time available to interpret** — seconds (oral talk slide), minutes (poster glance), unbounded (article).
2. **Interaction level with the presenter / authors** — high (lab meeting Q&A), low (asynchronous article), bidirectional with UI (online interactive).
3. **Audience expertise** — colleague specialist, conference specialist, lay public.

Match figure complexity to the context. Over-detailed figures fail in oral talks; under-detailed figures waste page space in articles.

---

## The matrix

| Context | Time | Interaction | Audience | Recommended figure complexity | Recommended techniques |
|---|---|---|---|---|---|
| **Lab meeting / journal club** | +++ (minutes per figure, with Q&A) | +++ (real-time discussion) | Colleagues with shared background | High — methodological detail, raw data overlay OK | Show distributions (box+jitter); include n; raw data points visible; minor methodology in caption; legend OK |
| **Poster session** | +++ (3–5 minute viewer engagement; multiple viewing distances) | ++ (verbal explanation possible) | Mixed: specialists in adjacent fields, occasional lay attendees | Medium — three-tier layered: title visible at 6 ft, headers + key figure at 3 ft, detail at 1 ft | Title + 1 hero figure for scan; section headers + 2–3 figures for browse; full detail for engaged viewers; **direct-label, never legend**; QR code for supplementary |
| **Oral / public talk** | + (seconds per slide) | + to ++ (limited Q&A) | Specialists or lay public depending on venue | **Low — single message per figure** | One takeaway annotated directly on the figure; statistical-significance markers integrated; key value text-callouts (e.g., "−2.5 kg"); strip non-essential elements; build-up animation for complex figures (PowerPoint or Beamer `\pause`) |
| **Research article (PDF / journal page)** | +++ (asynchronous; reader can re-read) | 0 (no real-time interaction) | Specialists in the field | High — multi-panel composition; comprehensive | Multi-panel (A, B, C, D) with shared axes / consistent panel size; detailed legend; methodology in caption; supplementary data linked separately; alt text per panel for HTML version |
| **Online / interactive (dashboard, web supplement)** | +++ (asynchronous; user-paced) | ++ (UI: zoom, filter, hover, switch views) | Mixed: specialists, journalists, lay public | Variable — **progressive disclosure** | Overview-first then detail-on-demand (Shneiderman); hover tooltips for exact values; default view simple, advanced controls behind a toggle; tables alongside figures for precise lookup (e.g., WHO COVID-19 dashboard pattern) |

Legend: + = limited, ++ = moderate, +++ = abundant, 0 = none.

---

## Decision workflow

1. **Identify the context** from the row above.
2. **Identify the key message** — one sentence the reader should take away (Fujii 2026 §"Identify the key message"; this is upstream of complexity choice).
3. **Match complexity to context.** A 6-panel figure dense with annotations works for an article and fails for a 1-minute oral slide.
4. **Apply the matching techniques** in the rightmost column.
5. **Run the pre-submission checklist** (`pre_submission_checklist.md`) before declaring done.

---

## Worked examples

### Example A — Same dataset, three contexts

A clinical-trial dataset showing 30% reduction in primary endpoint with treatment X vs placebo:

- **Lab meeting:** Box+jitter of all individual patient outcomes; methodology arm and randomisation visible; CIs shown.
- **Oral talk:** A single forest-plot point with "30% reduction (95% CI 22–37%)" annotated directly next to the point; nothing else.
- **Article:** Multi-panel — A: Kaplan-Meier survival curves with CI bands; B: forest plot of subgroup analyses; C: time-to-event by stratification factor. Detailed caption.
- **Online interactive:** Default view = main forest plot; click any subgroup → drill into KM curve for that subgroup; table of n, events, HR, CI on hover.

The dataset is identical. The figures are not.

### Example B — When NOT to use a figure

A baseline-characteristics summary (age, sex, comorbidities across study arms): no pattern to reveal, just numbers to compare. **Use a table** (Fujii §"Ask whether you really need a figure"; see `figure_vs_table_decision.md`). The "lab meeting" cell of this matrix is not "show everything as a figure" — it is "you can show more detail than in an oral talk if a figure is the right format."

---

## Cross-references

| Topic | See |
|---|---|
| Figure-vs-table decision (upstream of this matrix) | `figure_vs_table_decision.md` |
| Pre-submission quality gate | `pre_submission_checklist.md` |
| Cognitive-foundation citations (Cleveland, Crameri, Fujii, Wilke) | `../oligon-brand/SKILL.md` `<design_foundation>` |
| Bar-chart / risk-ratio anti-patterns | `../plotting-libraries/references/plot_selection_guide.md` |
| Time-allocation matrix (slide-section percentages, complementary) | `../scientific-slides/SKILL.md` §"Time Allocation Matrix" |

---

## References

- Fujii, R. *Nat Hum Behav* (2026). doi:10.1038/s41562-026-02466-9 — five-tactic framework, communication-context decision step.
- Shneiderman, B. (1996) "The Eyes Have It: A Task by Data Type Taxonomy for Information Visualizations" — overview-first, zoom-and-filter, details-on-demand pattern for interactive figures.
- Heer, J. & Bostock, M. (2010) *CHI* — graphical perception (cited for direct-labelling preference at oral-talk pace).
