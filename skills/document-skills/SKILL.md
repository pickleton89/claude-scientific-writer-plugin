---
name: document-skills
description: "Document format processing container. Routes to format-specific sub-skills for DOCX, PDF, PPTX, and XLSX creation, editing, and analysis."
allowed-tools: [Read, Write, Edit, Bash]
---

# Document Skills

## Overview

This is a **container skill** that organizes format-specific document processing capabilities. Each sub-skill handles a specific Office document format with specialized tools and workflows.

## When to Use This Skill

Route to the appropriate sub-skill based on the document format:

| Format | Sub-Skill | Use Case |
|--------|-----------|----------|
| `.docx` | `document-skills/docx` | Word documents, tracked changes, redlining |
| `.pdf` | `document-skills/pdf` | PDF creation, forms, extraction, manipulation |
| `.pptx` | `document-skills/pptx` | PowerPoint presentations, slide manipulation |
| `.xlsx` | `document-skills/xlsx` | Excel spreadsheets, formulas, data analysis |

## Decision Tree

```
User needs document processing
│
├─ What format?
│  │
│  ├─ Word document (.docx)?
│  │  └─ YES → document-skills/docx
│  │            │
│  │            ├─ Create new document
│  │            ├─ Edit with tracked changes
│  │            ├─ Extract text/content
│  │            └─ Redline workflow
│  │
│  ├─ PDF document (.pdf)?
│  │  └─ YES → document-skills/pdf
│  │            │
│  │            ├─ Create PDF from content
│  │            ├─ Fill PDF forms
│  │            ├─ Extract text/tables
│  │            └─ Merge/split PDFs
│  │
│  ├─ PowerPoint (.pptx)?
│  │  └─ YES → document-skills/pptx
│  │            │
│  │            ├─ Create presentations
│  │            ├─ Edit slide content
│  │            ├─ Modify layouts/themes
│  │            └─ Extract slide content
│  │
│  └─ Excel (.xlsx)?
│     └─ YES → document-skills/xlsx
│              │
│              ├─ Create spreadsheets
│              ├─ Formulas and calculations
│              ├─ Data analysis
│              └─ Chart generation
│
└─ Need Markdown conversion?
   └─ YES → Use markitdown skill instead
```

## Sub-Skill Details

### docx (Word Documents)

**Location:** `document-skills/docx/SKILL.md`

**Key Capabilities:**
- Create/edit DOCX using OOXML or docx-js
- Tracked changes and redlining workflows
- Comments and formatting preservation
- Text extraction and content analysis
- Raw XML access for advanced manipulation

**Scripts:** `docx/scripts/` contains conversion and manipulation tools

### pdf (PDF Documents)

**Location:** `document-skills/pdf/SKILL.md`

**Key Capabilities:**
- PDF creation and generation
- Form filling and field extraction
- Text and table extraction
- PDF merge, split, and manipulation
- Metadata handling

**Scripts:** `pdf/scripts/` contains PDF processing tools

### pptx (PowerPoint Presentations)

**Location:** `document-skills/pptx/SKILL.md`

**Key Capabilities:**
- Presentation creation from content
- Slide layout and theme management
- HTML to PPTX conversion
- OOXML-level slide manipulation
- Speaker notes and animations

**Scripts:** `pptx/scripts/` contains conversion tools

### xlsx (Excel Spreadsheets)

**Location:** `document-skills/xlsx/SKILL.md`

**Key Capabilities:**
- Spreadsheet creation and editing
- Formula support and recalculation
- Data analysis and manipulation
- Chart and visualization support
- Cell formatting and styles

**Scripts:** `xlsx/recalc.py` for formula recalculation

## Cross-References

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

**Related skills:**

- **markitdown**: Convert documents TO Markdown (reverse direction)
- **paper-2-web**: Transform papers to web/poster/video formats
- **scientific-writing**: Create manuscript content to export via document-skills
- **venue-templates**: Journal-specific formatting (use with docx for submissions)

## Usage Pattern

1. **Identify the target format** (docx, pdf, pptx, xlsx)
2. **Load the appropriate sub-skill** (`document-skills/<format>/SKILL.md`)
3. **Follow that skill's workflows** for the specific task
4. **Consult scripts** in the sub-skill folder for automation

## Notes

- Each sub-skill has its own LICENSE.txt with proprietary terms
- OOXML reference materials are provided for advanced manipulation
- Scripts are format-specific and located in each sub-skill directory
