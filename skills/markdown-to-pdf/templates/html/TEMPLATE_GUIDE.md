# Oligon Report Template — LLM Authoring Guide

You are formatting a research report into the **Oligon house style**. You have:

1. A markdown research document
2. A set of figures (SVG / PNG)
3. A target variant: **Editorial** (default) or **Banded** (executive / external)

Your job: produce a single HTML file that follows the template structure exactly.

---

## Step-by-step

### 1 · Pick the template file

| Variant | Template file | When to use |
|---|---|---|
| Editorial | `template-editorial.html` | Default. Restrained, journal-feeling. Pre-clinical / technical. |
| Banded    | `template-banded.html`    | More assertive. Blue band cover. Executive / external-facing. |

Copy the template file to a new name (e.g. `OL-RR-2026-014.html`). Keep `report.css`, `oligon-tokens.css`, and the `assets/` folder alongside it.

### 2 · Fill the cover

The cover has these slots (see top of template):

| Slot | Example | Notes |
|---|---|---|
| `{{TITLE_LINE_1}}` | "Choosing the door:" | Plain text. Will sit on first line. |
| `{{TITLE_LINE_2_HIGHLIGHT}}` | "extracellular targets for aptamer–siRNA internalization" | Wrapped in `<em>` → renders Brand Blue. Pick the *clause that carries the meaning*. |
| `{{DECK}}` | One-paragraph summary | What the report assesses, in one sentence. |
| `{{EYEBROW}}` | "Research Report · SeekR Platform" | Small uppercase label above title. |
| `{{PROGRAM_CODE}}` | "SeekR-AT-08" | Program / workstream identifier. |
| `{{REPORT_NUMBER}}` | "OL-RR-2026-014" | Document control number. |
| `{{DATE}}` | "May 2026" | Month + year. |
| `{{CLASSIFICATION}}` | "Internal · Pre-clinical" | Audience. |
| `{{AUTHOR_N}}` / `{{ROLE_N}}` | "J. Chambers, PhD" / "Lead, Discovery Biology" | Three pairs. |

The same `{{PROGRAM_CODE}}`, `{{REPORT_NUMBER}}`, `{{CLASSIFICATION}}` recur in every page header/footer — replace them globally.

### 3 · Map the markdown to pages

The template has eight reference pages, each demonstrating one layout:

| # | Layout | Use it for |
|---|---|---|
| 1 | Cover | Always. |
| 2 | Executive summary | `## Executive Summary` / `## TL;DR` / `## The One-Sentence Essence` sections. |
| 3 | Contents | If the report is ≥6 pages. |
| 4 | Methodology | `## Methodology` / `## How we did this` / `## First Principles`. |
| 5 | Body section | Default for every analytical section. **Duplicate this page as needed.** |
| 6 | Figure spread | Wherever the markdown references a figure, or a finding warrants a chart. |
| 7 | Comparison table | Markdown tables with a "winner" or "best of" structure. |
| 8 | References | Always last. Citations from the markdown. |

**Add or remove pages by duplicating / deleting `<section class="page">` blocks.** Update `.pg` footer text on every page (`02 / 12`, `03 / 12`, …).

### 4 · Component vocabulary

Use these classes verbatim. Do not invent new ones; the brand only sanctions what exists in `report.css`.

#### Section markers and headings
```html
<div class="sec-marker"><span class="num">01</span><span class="label">Section Name</span></div>
<div class="eyebrow">Small uppercase label</div>
<h1 class="display">Headline with <em>highlighted phrase</em>.</h1>
<h2><span class="num">2.1</span>Sub-heading</h2>
<p class="lede">First paragraph of a section, slightly larger.</p>
<p>Body paragraph.</p>
```

#### Callouts (use sparingly — 1–2 per page max)
```html
<div class="callout">…</div>           <!-- Brand Blue · key findings, recs -->
<div class="callout warn">…</div>      <!-- Orange · risks, caveats, opposition -->
<div class="callout neutral">…</div>   <!-- Gray · honest gaps, side-notes -->
```
Each callout has `<div class="label">Label · 01</div>` then `<p>body</p>`.

#### Inline pills
```html
<span class="pill">Strong delivery</span>
<span class="pill warn">Risk flag</span>
<span class="pill neutral">Tied</span>
```

#### Stat strip (3 numbers max)
```html
<div class="summary-grid">
  <div class="stat"><div class="num">12</div><div class="lab">Candidates</div></div>
  …
</div>
```

#### Definition list
```html
<dl class="kv">
  <dt>Key</dt><dd>Value</dd>
</dl>
```

#### Tables
```html
<table class="tbl">
  <thead><tr><th>Criterion</th><th>A</th><th>B</th></tr></thead>
  <tbody>
    <tr><td>…</td><td>…</td><td class="score-good">…</td></tr>
  </tbody>
</table>
```
Score chips: `score-good` (blue), `score-bad` (orange), `score-mid` (gray).

#### Figures
```html
<!-- Inline figure with sidebar caption — preferred -->
<div class="fig-wrap">
  <div class="fig"><img src="figures/foo.png" alt=""></div>
  <div class="caption-side">
    <span class="fnum">Figure 6.1</span>
    <span class="ftitle">Figure title</span>
    Caption body.
  </div>
</div>

<!-- Full-bleed figure with caption + source aside -->
<div class="fig-bleed">
  <div class="fig"><img src="figures/bar.png" alt=""></div>
  <div class="fig-cap">
    <div><span class="fnum">Figure 6.2</span> Caption…</div>
    <div style="border-left:1px solid #E5E5E5;padding-left:14px;font-size:8.5pt">
      <strong>Source / n</strong><br>n = 6. Source: …
    </div>
  </div>
</div>
```

#### References
```html
<ol class="refs">
  <li>Author, A. (Year). Title. <i>Journal</i>, 1(1), 1–10.
      <span class="doi">10.xxxx/xxxxx</span></li>
</ol>
```

---

## Voice & style rules

When rewriting markdown into report prose, match the Oligon house voice:

- **Scientific, precise, declarative.** Short sentences, present tense, strong verbs. No hedging.
- **Title Case** for section labels. **Sentence case** in body and headlines.
- **Strip all emoji.** The source markdown may have 🎯 / 💡 / ⚠️ — remove them. Use callout colours to carry the same signal.
- **Strip marketing hype** ("game-changing", "revolutionary"). Replace with measured claims.
- **Brand Blue is earned by importance** — only ~1–2 elements per page. Don't sprinkle.
- **Contrast Orange = opposition only** (risk vs. benefit, treatment vs. control). Never decorative.
- **Hex codes UPPERCASE** (`#2DB2E8`).
- **No new colours.** Only what's in `oligon-tokens.css`.

Voice benchmark: the methods section of a *Nature* paper. Tight, factual, no decoration.

---

## Figures

- Save figures to `figures/` next to the HTML.
- Reference as `<img src="figures/fig-6-1.png" alt="">`.
- Inline SVG is preferred over raster when the source is vector — it stays sharp at print resolution.
- If the markdown describes a figure but does not provide one, leave a placeholder `<div class="fig" style="height:240px;display:flex;align-items:center;justify-content:center;color:#999">Figure placeholder — {{description}}</div>` rather than inventing data.

---

## Generating the PDF

After populating the HTML:

1. Open it in a browser (Chrome / Safari).
2. **File → Print → Save as PDF.**
3. Page size: **US Letter**, margins: **None** (the page already has its own margins).

Pages are pre-sized to 8.5 × 11 in and break correctly.

---

## Checklist

- [ ] Variant chosen (Editorial / Banded)
- [ ] Cover slots filled
- [ ] Markdown content mapped to pages, page by page
- [ ] Footer page numbers updated everywhere (`NN / TOTAL`)
- [ ] Figures placed in `figures/`, referenced from inline `<img>`
- [ ] Emoji stripped, voice aligned to Oligon style
- [ ] Callouts limited to 1–2 per page
- [ ] References numbered, DOIs in `<span class="doi">`
- [ ] HTML opens cleanly in browser
- [ ] PDF exports without weird breaks
