<cross_references>
## Related Skills

| Skill                           | Relationship |
|---------------------------------|--------------|
| `plotting-libraries`            | Implementation code. Loads oligon-brand first; hosts `chart_selector` + `palette_selector` |
| `skills/shared/accessibility/`  | WCAG + CVD validation; `contrast_ratio`, `validate_accessibility`, colorblind simulation |
| `venue-templates`               | Per-journal figure dimensions, column widths, DPI, format |
| `scientific-slides`             | Presentation layouts; applies oligon-brand colors + projection type scale |
| `research-posters`              | Poster templates; applies oligon-brand colors + print specs |
| `markdown-to-pdf`               | Branded PDF reports; uses reportlab/docx adapters |
| `document-skills:docx`          | Word documents; uses `docx_adapter` |
| `scientific-writing`            | Manuscript prose; applies voice rules from `voice_and_copy.md` |
| `paper-2-web`                   | Web/video/poster from paper; inherits brand tokens |

**Skill Router:** See `SKILL_ROUTER.md` for decision trees.

**Typical workflow:**
1. `oligon-brand` → consult `<design_foundation>`, `<decision_framework>`, load tokens
2. `plotting-libraries` → implement figure code
3. `skills/shared/accessibility/` → validate contrast, CVD, figure-spec

**For brand-skill authors:** This skill is the reference
implementation of the contract in `../BRAND_SKILL_INTERFACE.md`.
Mirror the directory structure and validate with
`../brand-interface/`.
</cross_references>
