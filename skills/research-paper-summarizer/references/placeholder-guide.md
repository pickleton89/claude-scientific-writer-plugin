# Template Placeholder Guide

> How to substitute placeholders in prompt templates

## Overview

Prompt templates and subagent files use `{{PLACEHOLDER}}` syntax for dynamic content. When invoking prompts or subagents, substitute these placeholders with actual values.

## Standard Placeholders

### Paper Content

| Placeholder | Description | Source |
|-------------|-------------|--------|
| `{{PAPER}}` | Full text of paper being analyzed | Read from PDF |
| `{{PDF_PAGES}}` | Extracted text from specific PDF page range | Read specified pages |
| `{{RESEARCH_AREA}}` | User's stated research area/focus | Ask user if not provided |

### Metadata

| Placeholder | Description | Source |
|-------------|-------------|--------|
| `{{TITLE}}` | Paper title | Extract from first page of PDF |
| `{{FILENAME}}` | Source PDF filename (without extension) | From file path |
| `{{PAGE_COUNT}}` | Total number of pages in PDF | Count from PDF |
| `{{TIMESTAMP}}` | Current date/time | System time |
| `{{ARTICLE_TYPE}}` | Selected article type | User selection: general/review/compbio/cellmolbio |

### File Paths

| Placeholder | Description | Source |
|-------------|-------------|--------|
| `{{SUMMARY_FILE_PATH}}` | Absolute path to the summary file being written | Constructed from source directory + filename |
| `{baseDir}` | Skill installation directory | Resolved by Claude Code |

## Usage Examples

### In Subagent Prompts

When invoking a subagent, the prompt template contains:
```markdown
<pdf_pages>
{{PDF_PAGES}}
</pdf_pages>

<article_type>{{ARTICLE_TYPE}}</article_type>

<summary_file>{{SUMMARY_FILE_PATH}}</summary_file>
```

Before invocation, substitute:
```markdown
<pdf_pages>
[Extracted text from pages 1-3 of the PDF]
</pdf_pages>

<article_type>general</article_type>

<summary_file>/path/to/smith2024_cancer_summary.md</summary_file>
```

### In Summary Skeleton

The skeleton template contains:
```markdown
# Paper Summary: {{TITLE}}

> **Generated**: {{TIMESTAMP}}
> **Article Type**: {{ARTICLE_TYPE}}
> **Source**: {{FILENAME}}
> **Pages**: {{PAGE_COUNT}}
```

After substitution:
```markdown
# Paper Summary: Polyamine Depletion in Neuroblastoma

> **Generated**: 2024-01-15 14:32:00
> **Article Type**: General Research
> **Source**: smith2024_cancer
> **Pages**: 18
```

## Substitution Rules

1. **Always substitute before use** - Never pass templates with unresolved placeholders
2. **Preserve formatting** - Maintain the surrounding context when substituting
3. **Handle missing values gracefully** - If a value is unavailable, use appropriate defaults:
   - `{{RESEARCH_AREA}}` → "Not specified" if user didn't provide
   - `{{TIMESTAMP}}` → Current system time
4. **Use exact values** - Don't paraphrase or modify the extracted content

## Context-Specific Placeholders

### Article Type-Specific

The `skeleton-config.md` template includes placeholders that change based on article type:

| Placeholder | General | Review | CompBio |
|-------------|---------|--------|---------|
| `{{METHODS_SECTION_TITLE}}` | Experimental Approach | Scope & Methods | Data & Methods |
| `{{METHODS_SUBSECTION_1_TITLE}}` | Study Design | Literature Search | Data Sources |
| `{{ARTICLE_SPECIFIC_SECTION_TITLE}}` | Implications | Knowledge Gaps | Reproducibility |

### Processing Mode Placeholders

| Placeholder | Standard Mode | Chunked Mode |
|-------------|---------------|--------------|
| Processing indicator | (not used) | `Processing Mode: Chunked Subagent Pipeline` |
| Progress markers | (not used) | `<!-- SECTION: xxx PENDING -->` |
