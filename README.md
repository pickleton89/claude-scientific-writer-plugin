# Claude Scientific Writer Plugin

A comprehensive Claude Code plugin with 24 specialized skills for end-to-end scientific research workflows — from literature search and analysis to publication-ready documents, presentations, and figures.

## Features

- **Multi-database paper search**: PubMed, bioRxiv, Semantic Scholar, Google Scholar with unified query interface
- **Intelligent skill routing**: Automatic selection of appropriate skills based on task context
- **Tiered image generation**: Free Mermaid diagrams for simple workflows, AI generation for complex schematics
- **Publication-quality outputs**: Figures, slides, and posters meeting journal submission standards
- **Brand integration**: Consistent visual identity across all generated materials
- **Citation management**: BibTeX generation, validation, and formatting

## Prerequisites

This plugin requires the **anthropic-agent-skills** marketplace plugin for document processing capabilities (DOCX, PDF, PPTX, XLSX).

```bash
/plugin marketplace add anthropics/agent-skills
/plugin install anthropic-agent-skills
```

## Installation

```bash
# Add the marketplace source
/plugin marketplace add pickleton89/claude-scientific-writer-plugin

# Install the plugin
/plugin install claude-scientific-writer
```

Or test locally:
```bash
claude --plugin-dir /path/to/claude-scientific-writer-plugin
```

## Skills Included

### Visual Creation (5 skills)
| Skill | Description |
|-------|-------------|
| `visual-design` | Publication-quality figure standards and design principles |
| `plotting-libraries` | matplotlib, seaborn, ggplot2, Bioconductor patterns |
| `scientific-schematics` | Diagrams and illustrations (Mermaid + AI tiered generation) |
| `generate-image` | AI image generation for scientific illustrations |
| `paperbanana` | Text-to-visual figures (graphical abstracts, visual summaries) |

### Document Creation (8 skills)
| Skill | Description |
|-------|-------------|
| `scientific-writing` | Research papers, methodology, results in LaTeX/BibTeX |
| `executive-summary` | Concise summaries for decision-makers |
| `scientific-slides` | Research presentations |
| `research-posters` | Academic posters (LaTeX or PowerPoint format) |
| `venue-templates` | Journal-specific formatting (Nature, Cell, NeurIPS, etc.) |
| `hypothesis-generation` | Research hypothesis development |
| `markdown-to-pdf` | Template-based PDF generation |
| `document-skills` | Adapter routing to anthropic-agent-skills for DOCX, PDF, PPTX, XLSX |

### Research Workflow (5 skills)
| Skill | Description |
|-------|-------------|
| `paper-search` | Multi-database academic paper search |
| `literature-review` | Systematic literature reviews with PRISMA workflow |
| `citation-management` | BibTeX citations and bibliography |
| `peer-review` | Manuscript review, critique, and quantitative scoring |
| `research-paper-summarizer` | Multi-format paper summaries |

### Analysis & Code (3 skills)
| Skill | Description |
|-------|-------------|
| `statistical-analysis` | Statistical methods, test selection, reporting |
| `reproducible-research` | Reproducibility standards and practices |
| `code-documentation` | Scientific code documentation (docstrings, READMEs) |

### Conversion (2 skills)
| Skill | Description |
|-------|-------------|
| `markitdown` | Convert documents (PDF, DOCX, images) to Markdown |
| `paper-2-web` | Convert papers to web format, videos, and posters |

### Brand (1 skill)
| Skill | Description |
|-------|-------------|
| `oligon-brand` | Oligon brand visual identity and color system |

## Configuration

Some skills require API keys for full functionality:

| Feature | Environment Variable | Required For |
|---------|---------------------|--------------|
| OpenRouter API | `OPENROUTER_API_KEY` | AI image generation, document conversion with vision |
| Google AI | `GOOGLE_API_KEY` | PaperBanana text-to-visual generation (free from AI Studio) |

Set in your shell profile or `.env` file:
```bash
export OPENROUTER_API_KEY="your-key-here"
```

## Commands

| Command | Description |
|---------|-------------|
| `/scientific-writer-init` | Initialize a scientific writing project |

## Usage

Skills are automatically invoked based on your request. Examples:

### Single-skill tasks
```
"Write a methods section for my RNA-seq analysis"
→ Uses: scientific-writing

"Search for papers on CRISPR delivery mechanisms"
→ Uses: paper-search
```

### Multi-skill workflows
```
"Create a poster for my conference presentation on single-cell proteomics"
→ Uses: research-posters + visual-design + oligon-brand

"Review this manuscript draft and check the statistics"
→ Uses: peer-review + statistical-analysis

"Generate a figure showing the experimental workflow"
→ Uses: scientific-schematics (Mermaid tier for simple, AI tier for complex)

"Summarize this paper and create slides for my lab meeting"
→ Uses: research-paper-summarizer + scientific-slides
```

## Architecture

The plugin uses a **skill router** to intelligently select and combine skills based on task requirements. Key architectural decisions:

- **Tiered generation**: Simple diagrams (<10 nodes) use free Mermaid rendering; complex schematics use AI generation
- **Skill composition**: Complex tasks automatically invoke multiple skills with defined handoff patterns
- **Brand integration**: Visual outputs automatically apply organizational brand standards when configured

For multi-skill workflow planning and skill selection logic, see [SKILL_ROUTER.md](skills/SKILL_ROUTER.md).

## Documentation

| Document | Description |
|----------|-------------|
| [SKILL_ROUTER.md](skills/SKILL_ROUTER.md) | Decision trees for skill selection |
| [SCIENTIFIC_OUTPUT_DESIGN_SPEC.md](docs/SCIENTIFIC_OUTPUT_DESIGN_SPEC.md) | Visual design standards |
| [CHANGELOG.md](CHANGELOG.md) | Version history and updates |

## License

MIT
