# Oligon Report Template — Design Source Archive

This directory holds the original Figma-Make / React design canvas that the production HTML report templates were derived from. Provenance only — not consumed at runtime.

**The canonical, runtime templates live in:**
`skills/markdown-to-pdf/templates/html/`

If you're authoring, rendering, or editing CSS, work from the skill location.

## Contents

- `app.jsx`, `pages.jsx`, `figures.jsx`, `design-canvas.jsx` — React design canvas
- `Oligon Report Template.html` — design-canvas HTML export (its `<link href="report.css">` is intentionally unresolved here; open it from the skill location if you need it rendered)
- `assets/` — Oligon logo SVGs (kept locally so the .jsx files don't have broken image refs; safe to mirror because static)

The CSS files (`report.css`, `oligon-tokens.css`) are deliberately **not** mirrored here — they live only in `skills/markdown-to-pdf/templates/html/` to avoid drift.
