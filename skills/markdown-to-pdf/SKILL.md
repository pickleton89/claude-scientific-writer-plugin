---
name: markdown-to-pdf
version: 2.0.0
description: "Build branded long-form research reports as PDFs from markdown sources. HTML/CSS templates (Editorial / Banded variants) rendered via WeasyPrint. Use for analysis reports, literature reviews, and data reports — not for meeting notes, task lists, or short utility docs."
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Markdown to PDF — Branded Research Reports

<overview>
Produce print-grade Oligon-branded research-report PDFs from markdown. The skill carries hand-crafted HTML/CSS templates (Editorial + Banded variants, 8 reference page layouts) and a deterministic WeasyPrint renderer. The LLM does the markdown→HTML slot-fill against a small component vocabulary; the renderer turns the populated HTML into a US-Letter PDF with edge-to-edge brand layout.

**Pipeline:**
```
markdown → preflight + element detection → fill HTML template → render_pdf.py (WeasyPrint) → output/<doc>.pdf
```

**Brand source of truth:** `../oligon-brand/tokens/brand-tokens.json`. The skill's CSS (`templates/html/oligon-tokens.css`) is a derived implementation; values currently match exactly.
</overview>

> **Prose Standards:** Markdown source content conforms to [`../shared/references/prose_standards.md`](../shared/references/prose_standards.md). This skill does not edit prose. Run `scientific-writing/scripts/validate_writing_quality.py` on the markdown before rendering.

<scope>
## Scope (read this before invoking)

This skill renders **three doc types** through the HTML pipeline:

| Type | Pipeline | Schema |
|---|---|---|
| analysis-report | html-render | `templates/schemas/analysis-report.json` |
| literature-review | html-render | `templates/schemas/literature-review.json` |
| data-report | html-render | `templates/schemas/data-report.json` |

The other 9 schemas (meeting-notes, task-list, project-status, phase-plan, technical-spec, method-guide, standards-guide, agent-definition, readme) are tagged `pipeline: markdown-only`. The skill will **refuse** `/doc-to-pdf` on them with a clear redirect — long-form report layouts don't suit short utility docs.

For executive / external-facing audiences (board updates, grant pitches), use `--variant banded` on any of the three supported types. The `executive-summary` skill remains the source for stakeholder summary content.
</scope>

<prerequisites>
## Prerequisites

WeasyPrint depends on Pango, cairo, and glib (system libraries, not Python).

**macOS:**
```bash
brew install pango cairo glib
```
The renderer auto-sets `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` so Python can find them. No manual env setup required when running via `uv run`.

**Linux (Debian/Ubuntu):**
```bash
sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf2.0-0
```

**Smoke test:**
```bash
uv run skills/markdown-to-pdf/scripts/render_pdf.py --self-test
```
Renders both stock templates with placeholders. Should produce 8-page PDFs (~37–40 KB each) in under 2 seconds. If this fails, fix the system libs before doing anything else.
</prerequisites>

<when_to_use>
## Trigger Conditions

Use this skill when the user wants:
- A branded PDF of an analytical report, literature review, or data report
- An executive/external-facing version of one of the above (`--variant banded`)
- To list the supported doc types (`/list-templates`)
- To start a new report from a template (`/new-doc`)

Do NOT use this skill when:
- Producing PowerPoint / slides → `scientific-slides`
- Writing an academic manuscript for a journal → `scientific-writing`
- Building a research poster → `research-posters`
- Generating a standalone executive summary doc → `executive-summary`
- Working with an existing PDF (extract / fill forms) → `document-skills:pdf`
- Converting an arbitrary file TO markdown → `markitdown`
- Producing a meeting note, task list, or readme → those stay as markdown; this skill explicitly does not render them
</when_to_use>

<commands>
## Commands

### /list-templates

Display the three HTML-render-supported doc types with their categories and required sections. Read each schema's `pipeline` field and surface only `html-render` types.

**Implementation sketch:**
```python
import json, pathlib
schemas_dir = pathlib.Path(__file__).parent / "templates" / "schemas"
for p in sorted(schemas_dir.glob("*.json")):
    if p.name == "_base.json":
        continue
    data = json.loads(p.read_text())
    if data.get("pipeline") == "html-render":
        print(p.stem, data.get("required_sections", []))
```

---

### /new-doc \<type\>

Create a stub markdown file for one of the supported types. Frontmatter is generated from the schema's required fields; section headings come from `required_sections`.

**Workflow:**
1. Reject if `<type>` is not in the html-render set (point to `/list-templates`).
2. Read schema and emit:
   - YAML frontmatter with `type`, `title`, `date` (today), and any required fields from the schema.
   - One H2 heading per `required_sections` entry.
3. Write to `<type>_YYYYMMDD.md` in the current directory.

---

### /doc-to-pdf \<file\> [--variant editorial|banded]

The full pipeline. Five steps; each must complete before the next.

#### Step 1 — Preflight

```python
from scripts.preflight import preflight_check
result = preflight_check(file)
```
Reject if `result.is_valid is False`. Show errors. Do not proceed.

Also assert: schema for the doc's `type` has `pipeline == "html-render"`. If not, raise `PipelineMismatchError` (see `templates/error_recovery_map.json`).

#### Step 2 — Structure confirmation

```python
from scripts.structure_tree import build_tree
from scripts.element_detector import count_elements
```
Show the user the heading tree, element counts (callout candidates, tables, finding cards, code blocks), and missing-optional-section list. Get explicit confirmation before generating.

#### Step 3 — Pick variant and copy template

- Default: `editorial`. Override via `--variant banded` for executive/external audiences.
- Copy `templates/html/template-{variant}.html` to a working file in the output directory.
- Copy `templates/html/report.css`, `oligon-tokens.css`, and `assets/` alongside it (relative refs in the HTML expect them).

#### Step 4 — Slot-fill the HTML

This is the LLM's core job. Drive it from the inlined component vocabulary below and from `templates/html/TEMPLATE_GUIDE.md` (preserved verbatim — read it before authoring).

**Cover slots (page 1):**
| Slot | Source |
|---|---|
| `{{TITLE_LINE_1}}` / `{{TITLE_LINE_2_HIGHLIGHT}}` | Frontmatter `title` (split at the meaning-carrying clause; wrap second half in `<em>` for Brand Blue) |
| `{{EYEBROW}}` | Brief category label (e.g. "Research Report · SeekR Platform") |
| `{{DECK}}` | One-paragraph summary — what the report assesses |
| `{{PROGRAM_CODE}}`, `{{REPORT_NUMBER}}`, `{{DATE}}`, `{{CLASSIFICATION}}` | Frontmatter / user-provided. Recur in every page header/footer — replace globally. |
| `{{AUTHOR_N}}` / `{{ROLE_N}}` | Up to three pairs |

**Page mapping (duplicate / delete `<section class="page">` blocks as needed):**
| Reference page # | Layout | Use it for |
|---|---|---|
| 1 | Cover | Always |
| 2 | Executive summary | `## Executive Summary` / `## TL;DR` |
| 3 | Contents | Reports ≥ 6 pages |
| 4 | Methodology | `## Methodology` / `## Methods` |
| 5 | Body section | Default analytical section. **Duplicate per top-level finding section.** |
| 6 | Figure spread | Wherever the markdown references a figure |
| 7 | Comparison table | Markdown tables with a winner / "best of" structure |
| 8 | References | Always last |

After populating, update each page's `.pg` footer text (`02 / NN`, `03 / NN`, …) globally.

#### Step 5 — Render

```bash
uv run skills/markdown-to-pdf/scripts/render_pdf.py <filled.html> output/<stem>.pdf
```
The renderer auto-injects `@page { size: letter; margin: 0 }` and sets the macOS dyld path. Output is sharp vector text, ~30–60 KB per 8-page report.

If `output/` is not in `.gitignore`, add it.

---

## Component Vocabulary (use these classes verbatim)

The HTML templates only sanction what's in `templates/html/report.css`. Don't invent classes.

**Section markers / headings:**
```html
<div class="sec-marker"><span class="num">01</span><span class="label">Section Name</span></div>
<h1 class="display">Headline with <em>highlighted phrase</em>.</h1>
<h2><span class="num">2.1</span>Sub-heading</h2>
<p class="lede">First paragraph — slightly larger.</p>
```

**Callouts (1–2 per page max):**
```html
<div class="callout">…</div>          <!-- Brand Blue: key findings, recommendations -->
<div class="callout warn">…</div>     <!-- Orange: risks, caveats, opposition -->
<div class="callout neutral">…</div>  <!-- Gray: honest gaps, side notes -->
```
Each callout: `<div class="label">Label · 01</div>` then `<p>body</p>`.

**Inline pills:** `<span class="pill">…</span>` (`pill warn` for risk, `pill neutral` for tied).

**Stat strip (3 numbers max):**
```html
<div class="summary-grid">
  <div class="stat"><div class="num">12</div><div class="lab">Candidates</div></div>
</div>
```

**Definition list:** `<dl class="kv"><dt>Key</dt><dd>Value</dd></dl>`

**Tables:**
```html
<table class="tbl">
  <thead><tr><th>Criterion</th><th>A</th><th>B</th></tr></thead>
  <tbody><tr><td>…</td><td class="score-good">…</td></tr></tbody>
</table>
```
Score chips: `score-good` (blue), `score-bad` (orange), `score-mid` (gray).

**Figures:**
```html
<!-- Inline (preferred) -->
<div class="fig-wrap">
  <div class="fig"><img src="figures/foo.png" alt=""></div>
  <div class="caption-side">
    <span class="fnum">Figure 6.1</span><span class="ftitle">Title</span>
    Caption body.
  </div>
</div>

<!-- Full-bleed -->
<div class="fig-bleed">
  <div class="fig"><img src="figures/bar.png" alt=""></div>
  <div class="fig-cap">
    <div><span class="fnum">Figure 6.2</span> Caption…</div>
    <div><strong>Source / n</strong><br>n = 6. Source: …</div>
  </div>
</div>
```

**References:**
```html
<ol class="refs">
  <li>Author, A. (Year). Title. <i>Journal</i>, 1(1), 1–10.
      <span class="doi">10.xxxx/xxxxx</span></li>
</ol>
```

---

## Voice rules (when rewriting markdown into report prose)

- Scientific, precise, declarative. Short sentences, present tense, strong verbs. No hedging.
- Title Case for section labels; sentence case in body and headlines.
- Strip emoji. Use callout colors to carry the same signal.
- Strip marketing hype ("game-changing", "revolutionary"). Replace with measured claims.
- Brand Blue is **earned by importance** — only ~1–2 elements per page. Don't sprinkle.
- Contrast Orange = opposition only (risk vs. benefit, treatment vs. control). Never decorative.
- Hex codes UPPERCASE (`#2DB2E8`). No new colors — only what's in `oligon-tokens.css`.

Voice benchmark: the methods section of a *Nature* paper. Tight, factual, no decoration.

</commands>

<error_handling>
## Error Recovery

See `templates/error_recovery_map.json` for the canonical error → recovery table. Key entries:

| Error | Solution |
|---|---|
| `WeasyPrintNativeLibError` | macOS: `brew install pango cairo glib` |
| `PipelineMismatchError` | This doc type isn't supported — see `<scope>` above |
| `KeyError: 'type'` | Add `type: <doc-type>` to YAML frontmatter |
| `ValidationError: Missing sections` | Compare doc against schema's `required_sections` |
| `FileNotFoundError` | Verify path with `ls` |
</error_handling>

<success_criteria>
## Success Criteria

**`/doc-to-pdf` is successful when:**
- [ ] Self-test passes (`render_pdf.py --self-test`)
- [ ] Preflight reports no errors
- [ ] User confirms structure tree before render
- [ ] Output PDF: 8+ pages (or page count matching duplicated body sections), letter size
- [ ] Cover slots all populated (no remaining `{{…}}`)
- [ ] Page footers numbered consistently
- [ ] Brand Blue used sparingly (≤ 2 elements per page)
- [ ] Orange used only for opposition / risk
- [ ] Figures referenced from `figures/`, no broken images
</success_criteria>

<cross_references>
## Related Skills

| Skill | Relationship |
|---|---|
| `oligon-brand` | Canonical brand tokens (`tokens/brand-tokens.json`). The skill's CSS mirrors these — currently in sync. |
| `executive-summary` | Source for stakeholder summary content. Render its output via `--variant banded`. |
| `scientific-writing` | Manuscript-format output (LaTeX/journal). Different deliverable; don't conflate. |
| `scientific-schematics` / `paperbanana` | Generate figures, then drop into `figures/` and reference from the HTML. |
| `markitdown` | Reverse direction (file → markdown). |
| `document-skills:pdf` | Existing-PDF manipulation (forms, extraction). |

</cross_references>

<references>
## Reference Documents

| Path | Purpose |
|---|---|
| `templates/html/TEMPLATE_GUIDE.md` | Original LLM authoring guide — read this before slot-filling |
| `templates/html/template-editorial.html` | Editorial variant (default) |
| `templates/html/template-banded.html` | Banded variant (executive / external) |
| `templates/html/report.css` | Component styling (do not edit without designer review) |
| `templates/html/oligon-tokens.css` | Brand tokens — derived from `oligon-brand/tokens/brand-tokens.json` |
| `templates/html/assets/` | Oligon logos (SVG) |
| `templates/schemas/*.json` | Doc-type schemas; check `pipeline` field |
| `templates/error_recovery_map.json` | Error → recovery actions |
| `scripts/render_pdf.py` | WeasyPrint wrapper (PEP-723; deps installed automatically by `uv run`) |
| `scripts/preflight.py` | Frontmatter / required-section validation |
| `scripts/element_detector.py` | Pattern detection (callouts, tables, findings) |
| `scripts/structure_tree.py` | Heading-tree formatter |

</references>
