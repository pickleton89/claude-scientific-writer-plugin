# Claude Scientific Writer Plugin

A comprehensive Claude Code plugin with 23+ skills for scientific research writing.

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

### Writing & Documents
| Skill | Description |
|-------|-------------|
| `scientific-writing` | Research papers, methodology, results in LaTeX/BibTeX |
| `literature-review` | Systematic literature reviews and synthesis |
| `hypothesis-generation` | Research hypothesis development |
| `executive-summary` | Executive summaries for research documents |
| `venue-templates` | Journal-specific formatting requirements |

### Presentations & Posters
| Skill | Description |
|-------|-------------|
| `scientific-slides` | Research presentations |
| `research-posters` | Academic posters (LaTeX or PowerPoint format) |

### Research & Analysis
| Skill | Description |
|-------|-------------|
| `research-lookup` | Literature search and database queries |
| `citation-management` | BibTeX citations and bibliography |
| `peer-review` | Manuscript review, critique, and quantitative scoring |
| `statistical-analysis` | Statistical methods and reporting |

### Visuals & Figures
| Skill | Description |
|-------|-------------|
| `scientific-schematics` | Diagrams and scientific illustrations |
| `generate-image` | AI image generation prompts |
| `plotting-libraries` | matplotlib, seaborn, ggplot2 patterns |
| `visual-design` | Publication-quality figure standards |
| `oligon-brand` | Oligon brand visual identity |

### Document Processing
| Skill | Description |
|-------|-------------|
| `markdown-to-pdf` | Template-based PDF generation |
| `markitdown` | Convert documents to markdown |
| `paper-2-web` | Convert papers to web format |
| `document-skills` | Adapter routing to anthropic-agent-skills for DOCX, PDF, PPTX, XLSX |
| `research-paper-summarizer` | Multi-format paper summaries |

### Code & Reproducibility
| Skill | Description |
|-------|-------------|
| `code-documentation` | Scientific code documentation |
| `reproducible-research` | Reproducibility standards |

## Commands

| Command | Description |
|---------|-------------|
| `/scientific-writer-init` | Initialize a scientific writing project |

## Usage

Skills are automatically invoked based on your request. Examples:

```
"Write a methods section for my RNA-seq analysis"
→ Uses: scientific-writing, statistical-analysis

"Create a poster for my conference presentation"
→ Uses: research-posters

"Review this manuscript draft"
→ Uses: peer-review, scientific-writing

"Generate a figure showing gene expression"
→ Uses: plotting-libraries, visual-design
```

## Advanced

For multi-skill workflow planning and skill selection logic, see [SKILL_ROUTER.md](skills/SKILL_ROUTER.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## License

MIT
