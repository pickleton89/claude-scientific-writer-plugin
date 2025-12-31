---
name: markitdown
version: 2.0.0
description: "Convert files and office documents to Markdown using Microsoft's MarkItDown. Supports PDF, DOCX, PPTX, XLSX, images (OCR), audio (transcription), HTML, and more."
allowed-tools: [Read, Write, Edit, Bash]
license: MIT
source: https://github.com/microsoft/markitdown
---

# MarkItDown - File to Markdown Conversion

<overview>
MarkItDown is a Python tool developed by Microsoft for converting various file formats to Markdown. It produces clean, structured Markdown that is token-efficient and well-understood by LLMs. Supports 15+ file formats including PDF, Office documents, images (with OCR), and audio (with transcription).
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- Converting documents to LLM-friendly Markdown format
- Extracting text from PDFs for processing
- Converting Office documents (DOCX, PPTX, XLSX) to Markdown
- Extracting text from images via OCR
- Transcribing audio files to text
- Batch converting multiple documents
- Preparing documents for literature review or analysis

Do NOT use this skill when:
- Creating Markdown from scratch → use `scientific-writing`
- Converting Markdown to other formats → use `paper-2-web` or document generation tools
- Generating images or visual content → use `generate-image` or `scientific-schematics`
- Need complex PDF manipulation (forms, annotations) → use specialized PDF tools
</when_to_use>

<decision_framework>
## Conversion Path Selection

```
What is the input file type?
│
├─ Office Document?
│  │
│  ├─ DOCX (Word) → Basic MarkItDown (tables, formatting preserved)
│  ├─ PPTX (PowerPoint) → MarkItDown + optional AI image descriptions
│  └─ XLSX (Excel) → Basic MarkItDown (outputs as Markdown tables)
│
├─ PDF?
│  │
│  ├─ Simple text PDF → Basic MarkItDown
│  ├─ Complex layout PDF → Azure Document Intelligence
│  └─ Scanned/image PDF → MarkItDown with OCR (requires tesseract)
│
├─ Image?
│  │
│  ├─ Photo/screenshot → MarkItDown with OCR
│  └─ Need detailed description → MarkItDown with LLM (requires API key)
│
├─ Audio?
│  │
│  └─ WAV/MP3 → MarkItDown with transcription
│
├─ Web content?
│  │
│  ├─ HTML file → Basic MarkItDown
│  └─ YouTube URL → MarkItDown (fetches transcript)
│
└─ Structured data?
   │
   ├─ CSV → Basic MarkItDown (table format)
   ├─ JSON → Basic MarkItDown (structured representation)
   └─ XML → Basic MarkItDown (structured format)
```

## Method Selection Matrix

| Input Type | Method | Requirements | Quality |
|------------|--------|--------------|---------|
| Simple PDF | Basic | None | Good |
| Complex PDF | Azure DocIntel | Azure subscription | Excellent |
| Scanned PDF | OCR | tesseract installed | Good |
| PPTX with images | LLM-enhanced | OpenRouter API key | Excellent |
| PPTX text-only | Basic | None | Good |
| Audio | Transcription | Audio deps installed | Good |
| Image | OCR | tesseract installed | Moderate |
| Image + description | LLM-enhanced | OpenRouter API key | Excellent |

</decision_framework>

<workflow>
## Conversion Workflow

### Stage 1: Input Assessment

**Objective:** Determine file type and optimal conversion method

**Steps:**
1. Identify file extension and type
2. Check file size (large files may need streaming)
3. Assess content complexity (text-only vs. mixed media)
4. Verify required dependencies are available

**Exit Criteria:**
- [ ] File type identified
- [ ] Conversion method selected from decision tree
- [ ] Dependencies verified (tesseract, audio libs, API keys if needed)
- [ ] File accessibility confirmed

---

### Stage 2: Environment Setup

**Objective:** Ensure MarkItDown is properly configured

**Steps:**
1. Verify MarkItDown installation: `pip show markitdown`
2. Install missing format support if needed
3. Configure API keys for LLM-enhanced features (if applicable)
4. Prepare output directory

**Installation Commands:**

```bash
# Full installation
pip install 'markitdown[all]'

# Specific formats
pip install 'markitdown[pdf]'      # PDF support
pip install 'markitdown[docx]'     # Word documents
pip install 'markitdown[pptx]'     # PowerPoint
pip install 'markitdown[xlsx]'     # Excel
pip install 'markitdown[audio-transcription]'  # Audio files
```

**Exit Criteria:**
- [ ] MarkItDown installed with required extras
- [ ] OCR dependencies installed (if needed): `tesseract --version`
- [ ] API keys configured (if using LLM features)
- [ ] Output directory exists and writable

---

### Stage 3: Conversion Execution

**Objective:** Convert document to Markdown

**Steps:**
1. Select appropriate conversion method
2. Execute conversion with proper parameters
3. Handle errors gracefully
4. Save output to specified location

**Basic Conversion:**
```bash
# Command line
markitdown document.pdf -o output.md

# Python API
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)
```

**LLM-Enhanced Conversion (for images in PPTX):**
```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI(
    api_key="your-openrouter-api-key",
    base_url="https://openrouter.ai/api/v1"
)

md = MarkItDown(
    llm_client=client,
    llm_model="anthropic/claude-sonnet-4.5",
    llm_prompt="Describe this image in detail for scientific documentation"
)
result = md.convert("presentation.pptx")
```

**Azure Document Intelligence (for complex PDFs):**
```bash
markitdown document.pdf -o output.md -d -e "<endpoint>"
```

**Exit Criteria:**
- [ ] Conversion completed without errors
- [ ] Output file created
- [ ] Content length is reasonable (not empty, not truncated)
- [ ] Encoding is correct (UTF-8)

---

### Stage 4: Output Validation

**Objective:** Verify conversion quality

**Steps:**
1. Check output file exists and has content
2. Validate Markdown structure (headers, tables preserved)
3. Verify special content (tables, code blocks, links)
4. Clean up excess whitespace if needed

**Validation Checks:**

| Check | Pass Criteria | Action if Fail |
|-------|---------------|----------------|
| File exists | output.md present | Retry conversion |
| Non-empty | >100 characters | Check input file |
| Valid Markdown | Headers render | Manual cleanup |
| Tables intact | Pipe formatting | Use Azure DocIntel |
| No encoding errors | UTF-8 readable | Specify encoding |

**Post-Processing (if needed):**
```python
import re

# Clean up excess whitespace
clean_text = re.sub(r'\n{3,}', '\n\n', result.text_content)
clean_text = clean_text.strip()
```

**Exit Criteria:**
- [ ] Output file non-empty (>100 characters)
- [ ] Markdown structure valid (headers, lists work)
- [ ] Tables preserved (if source had tables)
- [ ] No encoding errors

---

### Stage 5: Integration

**Objective:** Prepare output for downstream use

**Steps:**
1. Add metadata header if needed
2. Organize output in project structure
3. Update any cross-references
4. Document conversion for reproducibility

**Metadata Template:**
```markdown
---
source: {{original_filename}}
converted: {{date}}
method: markitdown {{version}}
---

# {{Title}}

{{converted_content}}
```

**Exit Criteria:**
- [ ] Output in correct project location
- [ ] Metadata added (if required)
- [ ] Ready for downstream processing

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Content extraction | 80% | 95% | 100% |
| Table preservation | Tables present | Formatting intact | Perfect alignment |
| Processing time | <60s/page | <30s/page | <10s/page |
| Error rate | <5% files | <1% files | 0% |

**Completion Checklist:**
- [ ] Output file created successfully
- [ ] Content length matches expected (not truncated)
- [ ] Markdown renders correctly (headers, lists, tables)
- [ ] Special characters preserved (math, symbols)
- [ ] Images referenced (paths or descriptions)
- [ ] No encoding errors in output

</success_criteria>

<scope>
## Scope

**In Scope:**
- PDF to Markdown conversion
- Office document conversion (DOCX, PPTX, XLSX)
- Image OCR to text
- Audio transcription to text
- HTML to Markdown
- Structured data (CSV, JSON, XML) to Markdown
- YouTube transcript extraction
- Batch processing multiple files

**Out of Scope** (use specialized resources):
- Markdown to PDF/DOCX → use document generation tools
- PDF form filling → use PDF-specific libraries
- Image generation → use `generate-image`
- Complex document layout preservation → use specialized tools
- Real-time transcription → use streaming services

</scope>

<anti_patterns>
## Common Pitfalls

### 1. Missing Dependencies

**Anti-pattern:**
```bash
markitdown scan.pdf -o output.md
# Error: OCR not available
```

**Solution:**
```bash
# Check and install dependencies first
tesseract --version  # Verify OCR available
pip install 'markitdown[pdf]'  # Install PDF support

# Then convert
markitdown scan.pdf -o output.md
```

---

### 2. Binary Mode Errors

**Anti-pattern:**
```python
with open("file.pdf") as f:  # Text mode - will fail
    result = md.convert_stream(f)
```

**Solution:**
```python
with open("file.pdf", "rb") as f:  # Binary mode required
    result = md.convert_stream(f, file_extension=".pdf")
```

---

### 3. Ignoring Complex PDFs

**Anti-pattern:**
Using basic conversion for multi-column, heavily formatted PDFs (results in jumbled text)

**Solution:**
Detect complex PDFs and use Azure Document Intelligence:
```python
# Signs of complex PDF:
# - Multiple columns
# - Mixed text/tables/figures
# - Scanned content

# Use Azure DocIntel for complex documents
md = MarkItDown(docintel_endpoint="<endpoint>")
result = md.convert("complex_document.pdf")
```

---

### 4. Missing API Keys for LLM Features

**Anti-pattern:**
```python
md = MarkItDown(
    llm_client=client,  # Client not configured
    llm_model="gpt-4"
)
# Silent failure - no image descriptions generated
```

**Solution:**
```python
# Verify API key first
import os
assert os.getenv("OPENROUTER_API_KEY"), "API key required for LLM features"

# Configure client properly
from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

md = MarkItDown(llm_client=client, llm_model="anthropic/claude-sonnet-4.5")
```

---

### 5. No Output Validation

**Anti-pattern:**
```python
result = md.convert("document.pdf")
with open("output.md", "w") as f:
    f.write(result.text_content)
# No validation - may be empty or corrupted
```

**Solution:**
```python
result = md.convert("document.pdf")

# Validate before saving
if not result.text_content or len(result.text_content) < 100:
    raise ValueError(f"Conversion produced insufficient content: {len(result.text_content)} chars")

# Check for common issues
if "�" in result.text_content:
    print("Warning: Encoding issues detected")

with open("output.md", "w", encoding="utf-8") as f:
    f.write(result.text_content)
```

</anti_patterns>

<templates>
## Output Templates

### Template 1: Converted Document with Metadata

```markdown
---
source: {{ORIGINAL_FILENAME}}
format: {{FILE_TYPE}}
converted: {{YYYY-MM-DD}}
tool: markitdown
method: {{basic|ocr|llm-enhanced|azure-docintel}}
---

# {{DOCUMENT_TITLE}}

{{CONVERTED_CONTENT}}

---
*Converted from {{ORIGINAL_FILENAME}} using MarkItDown*
```

### Template 2: Batch Conversion Report

```markdown
# Batch Conversion Report

**Date:** {{YYYY-MM-DD}}
**Total Files:** {{COUNT}}
**Success Rate:** {{PERCENT}}%

## Results

| File | Status | Method | Size | Notes |
|------|--------|--------|------|-------|
| {{filename}} | {{SUCCESS/FAILED}} | {{method}} | {{KB}} | {{notes}} |

## Errors

{{ERROR_DETAILS}}
```

</templates>

<cross_references>
## Related Skills

| Skill | Relationship |
|-------|-------------|
| `literature-review` | Use markitdown to convert PDFs before literature analysis |
| `paper-2-web` | Converts in opposite direction (paper → web formats) |
| `scientific-writing` | Use converted Markdown as source material |
| `research-lookup` | Convert downloaded papers for processing |

**Skill Selection:**
See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

</cross_references>

<references>
## Reference Documents

| Document | Purpose |
|----------|---------|
| `references/api_reference.md` | Complete Python API documentation |
| `references/file_formats.md` | Format-specific conversion details |

## External Resources

- **GitHub**: https://github.com/microsoft/markitdown
- **PyPI**: https://pypi.org/project/markitdown/
- **OpenRouter**: https://openrouter.ai (for LLM-enhanced conversions)

</references>
