---
name: markdown-to-pdf
version: 1.0.0
description: "Convert templated markdown to branded PDFs. Create documents from 12 templates (scientific, project-mgmt, technical), generate professional PDFs with Oligon styling."
allowed-tools: [Read, Write, Edit, Bash]
---

# Markdown to PDF - Branded Document Conversion

<overview>
This skill bridges the template infrastructure and PDF component system to provide a complete markdown-to-PDF workflow. It uses `TemplateParser` for document parsing and `oligon_reports` components for branded PDF generation.

**Dependencies:**
- `oligon_reports.templates.TemplateParser` - Template parsing and validation
- `oligon_reports.components` - PDF visual components
- `oligon_reports.ReportGenerator` - PDF orchestration
</overview>

<prerequisites>
## Prerequisites

Before using this skill, verify the oligon_reports package is installed:

```bash
uv sync  # Install all project dependencies
```

**Quick verification:**
```python
from oligon_reports import ReportGenerator
from oligon_reports.templates import TemplateParser
print("Dependencies ready")
```

If imports fail, ensure you're in the project directory with `pyproject.toml`.
</prerequisites>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Listing available document templates
- Creating new documents from templates
- Converting templated markdown to branded PDFs
- Generating professional reports with Oligon styling

Do NOT use this skill when:
- Converting arbitrary files to markdown → use `markitdown`
- Creating LaTeX/academic papers → use `scientific-writing`
- Making PowerPoint presentations → use `scientific-slides` or `pptx-posters`
- Working with existing PDFs (extraction, forms) → use `document-skills/pdf`
</when_to_use>

<decision_framework>
## Command Selection

```
What does the user need?
│
├─ See available templates?
│  └─ YES → /list-templates
│           Returns table of 12 document types with categories
│
├─ Start a new document from template?
│  └─ YES → /new-doc <type>
│           Creates <type>_YYYYMMDD.md in current directory
│
└─ Convert existing markdown to PDF?
   └─ YES → /doc-to-pdf <file>
            │
            ├─ Parses and validates document
            ├─ Shows structure for confirmation
            ├─ Maps elements to PDF components
            └─ Generates branded PDF in output/
```

## Template Categories

| Category | Templates | Use Case |
|----------|-----------|----------|
| scientific | analysis-report, literature-review, data-report | Research outputs |
| project-mgmt | meeting-notes, project-status, phase-plan, task-list | Project tracking |
| technical | technical-spec, method-guide, standards-guide | Documentation |
| meta | agent-definition, readme | System docs |
</decision_framework>

<commands>
## Commands

### /list-templates

**Purpose:** Display all available document templates

**Workflow:**
1. Call `TemplateParser.list_templates()`
2. Format as markdown table
3. Display with type, category, and description

**Output Example:**
```
| Type              | Category        | Description                           |
|-------------------|-----------------|---------------------------------------|
| analysis-report   | scientific      | Structured analysis with findings     |
| literature-review | scientific      | Systematic literature review          |
| data-report       | scientific      | Data analysis and visualization       |
| meeting-notes     | project-mgmt    | Meeting documentation                 |
| project-status    | project-mgmt    | Project status update                 |
| phase-plan        | project-mgmt    | Implementation phase planning         |
| task-list         | project-mgmt    | Task tracking document                |
| technical-spec    | technical       | Technical specification               |
| method-guide      | technical       | Methodology documentation             |
| standards-guide   | technical       | Standards and guidelines              |
| agent-definition  | meta            | AI agent behavior definition          |
| readme            | meta            | Project documentation                 |
```

**Implementation:**
```python
from oligon_reports.templates import TemplateParser

templates = TemplateParser.list_templates()
# Returns: [{"type": "...", "category": "...", "description": "..."}, ...]
```

---

### /new-doc \<type\>

**Purpose:** Create a new document from a template

**Arguments:**
- `type` (required): Document type from template list

**Workflow:**
1. Validate `<type>` exists in template list
2. Get template content: `TemplateParser.get_template(type)`
3. Generate filename: `<type>_YYYYMMDD.md`
4. Write to current directory
5. Report success

**Output Example:**
```
Created: analysis-report_20251228.md
Template type: analysis-report (scientific)

Next: Edit the document, then run /doc-to-pdf analysis-report_20251228.md
```

**Implementation:**
```python
from datetime import date
from oligon_reports.templates import TemplateParser

template_content = TemplateParser.get_template("analysis-report")
filename = f"analysis-report_{date.today().strftime('%Y%m%d')}.md"

with open(filename, "w") as f:
    f.write(template_content)
```

**Error Handling:**
- If type not found → Show available types with `/list-templates`
- If file exists → Prompt to overwrite or use incremental name

---

### /doc-to-pdf \<file\> [--figures]

**Purpose:** Convert a templated markdown document to branded PDF

**Arguments:**
- `file` (required): Path to markdown file
- `--figures` (optional): Generate figures using `scientific-schematics`

**Workflow:**

#### Step 1: Parse & Detect

```python
from oligon_reports.templates import TemplateParser

parser = TemplateParser()
tree = parser.parse(content)
doc_type = tree.frontmatter.type  # e.g., "analysis-report"
```

#### Step 2: Show Structure for Confirmation

Present document structure and detected elements for user approval:

```
📄 Document: analysis-report_20251228.md
📋 Type: analysis-report (detected from frontmatter)

Structure:
├── 1. Objective
├── 2. Key Questions
├── 3. Methodology
│   └── 3.1 Data Sources
├── 4. Findings
│   ├── Finding 1: [title]
│   ├── Finding 2: [title]
│   └── Finding 3: [title]
└── 5. Recommendations

Elements Detected:
- 3 tables (→ StatusTable/GradedTable/BaseTable)
- 3 finding cards (→ FindingCard)
- 2 code blocks (→ MethodBlock)
- 1 callout (→ CalloutBox)

⚠️ Validation:
- ✅ All required sections present
- ⚠️ Missing optional: executive_summary

Proceed with PDF generation? [Y/n/edit]
```

#### Step 3: Map Elements to Components

Use the component mapping (see `{baseDir}/references/component_map.md`):

| Markdown Element | Detection | PDF Component |
|------------------|-----------|---------------|
| Tables with ✓/✗ | Status symbols in cells | `StatusTable` |
| Tables with grades | A-F or tier values | `GradedTable` |
| Regular tables | Standard markdown | Standard table |
| `#### Finding N:` | Heading pattern | `FindingCard` |
| Code blocks | Triple backticks | `MethodBlock` |
| `> **Type:**` | Blockquote + bold | `CalloutBox` |
| Checklists | `- [ ]` pattern | Standard list |

#### Step 4: Generate PDF

```python
from oligon_reports import ReportGenerator

generator = ReportGenerator(output_dir="output")
generator.add_title(tree.frontmatter.title)

for section in tree.sections:
    generator.add_section(section.title, section.content)
    for element in section.elements:
        # Map to appropriate component
        component = map_element_to_component(element)
        generator.add_component(component)

pdf_path = generator.build(f"{filename_stem}.pdf")
```

**Output:**
- Creates `output/` directory if needed
- Generates `output/<filename>.pdf`
- Adds `output/` to `.gitignore` if not present

#### Step 5: Optional Figure Enhancement

If `--figures` flag provided:

```
Generating figures for document...
[Invokes scientific-schematics for each figure placeholder]
```

**Success Output:**
```
✅ PDF generated: output/analysis-report_20251228.pdf

Summary:
- 5 sections rendered
- 3 FindingCards
- 2 StatusTables
- 1 MethodBlock
- Brand styling applied (Oligon)
```

**Error Handling:**

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Markdown file doesn't exist | Verify path, check working directory |
| `KeyError: 'type'` | Missing frontmatter type field | Add `type: <template-type>` to YAML header |
| `ValidationError` | Required sections missing | Check template schema for required fields |
| `PermissionError` on output/ | Directory not writable | Check permissions or use different output path |
| `ModuleNotFoundError` | oligon_reports not installed | Run `uv sync` in project directory |

**Recovery workflow:**
```
Error detected?
├─ Missing frontmatter → Add YAML header with type, title, date
├─ Validation errors → Compare against template schema
├─ Import errors → Run `uv sync` and retry
└─ Permission errors → Check output/ directory permissions
```

</commands>

<component_mapping>
## Component Mapping Reference

See `{baseDir}/references/component_map.md` for the complete element-to-component mapping.

### Quick Reference

| Pattern | Component | Example |
|---------|-----------|---------|
| `✓`, `✗`, `✔`, `✘` in table | StatusTable | Compliance matrix |
| `A`, `B`, `C`, `D`, `F` in table | GradedTable | Rating table |
| `#### Finding [0-9]:` | FindingCard | Key findings |
| Triple backticks | MethodBlock | Code/methods |
| `> **Note:**` | CalloutBox (info) | Information |
| `> **Warning:**` | CalloutBox (warning) | Caution |
| `> **Important:**` | CalloutBox (alert) | Critical |
| `- [ ]` or `- [x]` | Checklist | Tasks |

</component_mapping>

<workflow>
## Complete Workflow Example

### Creating a New Analysis Report

```
> /list-templates

| Type              | Category        | Description                           |
|-------------------|-----------------|---------------------------------------|
| analysis-report   | scientific      | Structured analysis with findings     |
...

> /new-doc analysis-report

Created: analysis-report_20251228.md
Template type: analysis-report (scientific)

[User edits the document with their content]

> /doc-to-pdf analysis-report_20251228.md

📄 Document: analysis-report_20251228.md
📋 Type: analysis-report

Structure:
├── 1. Objective
├── 2. Methodology
├── 3. Findings
└── 4. Recommendations

Elements Detected:
- 2 tables (→ StatusTable)
- 3 finding cards (→ FindingCard)

Proceed with PDF generation? [Y/n/edit]

> Y

✅ PDF generated: output/analysis-report_20251228.pdf
```

</workflow>

<success_criteria>
## Success Criteria

**Command: /list-templates**
- [ ] Shows all 12 template types
- [ ] Grouped by category
- [ ] Descriptions are helpful

**Command: /new-doc**
- [ ] Creates valid markdown file
- [ ] Filename includes date
- [ ] Template content is complete

**Command: /doc-to-pdf**
- [ ] Parses document without errors
- [ ] Shows accurate structure tree
- [ ] Correctly detects element types
- [ ] PDF matches brand styling
- [ ] Output folder is gitignored

</success_criteria>

<anti_patterns>
## Common Pitfalls

### 1. Missing Frontmatter

**Anti-pattern:**
Converting a markdown file without YAML frontmatter

**Solution:**
```markdown
---
type: analysis-report
title: My Analysis
date: 2025-12-28
author: Jane Doe
---

# My Analysis
...
```

---

### 2. Wrong Element Detection

**Anti-pattern:**
Regular table detected as StatusTable

**Solution:**
StatusTable detection requires actual status symbols (✓, ✗, ✔, ✘) in cells, not just checkmark text.

---

### 3. Missing Dependencies

**Anti-pattern:**
```python
from oligon_reports import ReportGenerator
# ModuleNotFoundError
```

**Solution:**
```bash
uv sync  # Ensure oligon_reports is installed
```

---

### 4. Output Directory Issues

**Anti-pattern:**
PDF generation fails because output/ doesn't exist

**Solution:**
The skill automatically creates `output/` and adds it to `.gitignore`.

</anti_patterns>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `oligon-brand` | Brand colors and tokens—`oligon_reports` uses these for PDF styling |
| `markitdown` | Convert documents TO markdown (reverse direction) |
| `document-skills/pdf` | Low-level PDF manipulation (forms, extraction) |
| `scientific-writing` | Create academic manuscripts (different output format) |
| `scientific-schematics` | Generate figures for `--figures` integration |
| `venue-templates` | Journal-specific formatting (use before /doc-to-pdf) |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `{baseDir}/references/component_map.md` | Complete element → component mapping |
| `src/oligon_reports/templates/` | Template schemas and markdown files |
| `src/oligon_reports/components.py` | PDF component implementations |
| `../oligon-brand/references/brand-colors-full.md` | Brand colors and visual identity (V4) |
| `../oligon-brand/tokens/brand-tokens.json` | Machine-readable brand tokens |

## API Reference

```python
from oligon_reports.templates import TemplateParser

# List available templates
templates = TemplateParser.list_templates()
# → [{"type": "...", "category": "...", "description": "..."}, ...]

# Get template content
content = TemplateParser.get_template("analysis-report")
# → Markdown string

# Parse document
parser = TemplateParser()
tree = parser.parse(markdown_content)
# → DocumentTree with frontmatter, sections, elements

# Validate
errors = parser.validate(tree)
# → List of ValidationError
```

</references>
