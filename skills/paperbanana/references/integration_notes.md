# PaperBanana Integration Notes

## Architecture Decisions

### Skill Naming
- Named `paperbanana` (not `academic-figures`) for recognizability and user preference.

### Scope: Text-to-Visual Only
- PaperBanana handles the **text-to-visual** use case: prose → figure.
- Does NOT handle data-to-plot (`plotting-libraries`) or spec-to-diagram (`scientific-schematics`).
- Only uses `DiagramType.METHODOLOGY` — no statistical plot mode.

### API Approach: Python API (not MCP server)
- Uses PaperBanana's Python API directly for full control over configuration, brand injection, and score mapping.
- The PaperBanana MCP server exists but doesn't offer sufficient control for brand integration.

### Brand Integration
- Oligon brand is injected via custom guidelines YAML (`data/guidelines/oligon_style.yaml`) and Stylist prompt (`prompts/diagram/stylist.txt`).
- Reuses `ColorPalette` and `OLIGON_BRAND` from `scientific-schematics/scripts/utils/brand_colors.py`.
- Opt-out via `--no-brand` CLI flag.

### Quality Bridge
- PaperBanana evaluates on 4 dimensions (0.0-1.0): Faithfulness, Readability, Conciseness, Aesthetics.
- Our 5-point rubric has 5 dimensions (0-2 each, total 10): Scientific Accuracy, Clarity & Readability, Label Quality, Layout & Composition, Professional Appearance.
- Readability maps to both Clarity & Readability AND Label Quality (readability implies label quality).
- This enables consistent quality tracking across `scientific-schematics` and `paperbanana`.

### API Key
- Uses `GOOGLE_API_KEY` (not `OPENROUTER_API_KEY`).
- Loaded via shared `api_utils.load_api_key(env_var="GOOGLE_API_KEY")`.
- Free from Google AI Studio: https://aistudio.google.com/apikey

### Dependency
- Installed from PyPI: `pip install paperbanana`
- MIT licensed, maintained by llmsresearch.
- Not vendored — upstream fixes flow through automatically.

## Routing Boundaries

| Input Type | Skill |
|---|---|
| Prose text to visualize | `paperbanana` |
| Data to plot (numbers, CSV) | `plotting-libraries` |
| Diagram specification (nodes, edges, type) | `scientific-schematics` |
| Photorealistic/artistic image | `generate-image` |

## Future Work (v2.0)

- **Delegation to scientific-schematics**: When PaperBanana's Planner determines the figure would be better served by a specific diagram type (flowchart, pathway), delegate to `scientific-schematics` instead of generating with Imagen.
- **Multi-panel figures**: Support for composite figures with mixed text-to-visual and data panels.
- **Template library**: Pre-built templates for common graphical abstract layouts (journal-specific).

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-02-12 | Initial integration |
