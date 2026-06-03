<default_behavior>
## Default-On Brand Application

Brand styling is applied by default to all visual output skills. Brand
colors are automatically used by `plotting-libraries`,
`scientific-schematics`, `research-posters`, `scientific-slides`,
`research-paper-summarizer`, and `markdown-to-pdf`.

**Opt out per request** by including "Use default colors", "No brand
styling", "Generic color scheme", or "Use matplotlib defaults" in
your prompt. **Opt out per project** by adding to `CLAUDE.md`:

```markdown
## Visual Styling
Use generic/default styling for all visual outputs. Do not apply Oligon brand.
```
</default_behavior>
