# Claude Scientific Writer Plugin

A comprehensive Claude Code plugin with 25+ skills for scientific research writing.

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
| `latex-posters` | Academic posters in LaTeX |
| `pptx-posters` | PowerPoint poster templates |

### Research & Analysis
| Skill | Description |
|-------|-------------|
| `research-lookup` | Literature search and database queries |
| `citation-management` | BibTeX citations and bibliography |
| `peer-review` | Manuscript review and critique |
| `scholar-evaluation` | Evaluate research quality and impact |
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
| `document-skills` | DOCX, PDF, PPTX, XLSX generation |
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
→ Uses: latex-posters or pptx-posters

"Review this manuscript draft"
→ Uses: peer-review, scientific-writing

"Generate a figure showing gene expression"
→ Uses: plotting-libraries, visual-design
```

## License

MIT
