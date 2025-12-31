# Component Mapping Reference

Maps markdown elements to PDF components from `oligon_reports.components`.

---

## Detection Patterns

### Tables

| Pattern | Component | Detection Logic |
|---------|-----------|-----------------|
| Status symbols | `StatusTable` | Cell contains: `✓`, `✗`, `✔`, `✘`, `Yes`, `No`, `Pass`, `Fail` |
| Grade values | `GradedTable` | Cell contains: `A`, `B`, `C`, `D`, `F`, `Tier 1-3`, `High/Medium/Low` |
| Regular | Standard table | Standard markdown table without special patterns |

**StatusTable Example:**
```markdown
| Requirement | Status |
|-------------|--------|
| API docs    | ✓      |
| Unit tests  | ✗      |
| Type hints  | ✓      |
```

**GradedTable Example:**
```markdown
| Criterion     | Score |
|---------------|-------|
| Clarity       | A     |
| Completeness  | B     |
| Accuracy      | A     |
```

---

### Findings

| Pattern | Component | Detection Logic |
|---------|-----------|-----------------|
| `#### Finding N:` | `FindingCard` | H4 heading matching `Finding \d+:` |
| `#### Key Finding:` | `FindingCard` | H4 with "Key Finding" prefix |

**FindingCard Example:**
```markdown
#### Finding 1: Performance degradation under load

The system shows 40% slower response times when concurrent users exceed 100.

**Impact:** High
**Recommendation:** Implement connection pooling
```

**Rendered as:**
- Colored card with finding number badge
- Title prominently displayed
- Body text with impact/recommendation formatting

---

### Code & Methods

| Pattern | Component | Detection Logic |
|---------|-----------|-----------------|
| ` ```python ` | `MethodBlock` | Fenced code with `python`, `r`, `bash`, `sql` |
| ` ```pseudocode ` | `MethodBlock` | Fenced code with `pseudocode` or `algorithm` |
| ` ``` ` (other) | Code block | Generic fenced code |

**MethodBlock Example:**
````markdown
```python
def calculate_significance(p_value: float) -> str:
    """Determine statistical significance level."""
    if p_value < 0.001:
        return "***"
    elif p_value < 0.01:
        return "**"
    elif p_value < 0.05:
        return "*"
    return "ns"
```
````

---

### Callouts

| Pattern | Component | Style |
|---------|-----------|-------|
| `> **Note:**` | `CalloutBox` | info (blue) |
| `> **Info:**` | `CalloutBox` | info (blue) |
| `> **Tip:**` | `CalloutBox` | success (green) |
| `> **Warning:**` | `CalloutBox` | warning (amber) |
| `> **Caution:**` | `CalloutBox` | warning (amber) |
| `> **Important:**` | `CalloutBox` | alert (red) |
| `> **Critical:**` | `CalloutBox` | alert (red) |

**CalloutBox Example:**
```markdown
> **Warning:** Sample size is below recommended threshold (n < 30).
> Consider collecting additional data before drawing conclusions.
```

---

### Lists

| Pattern | Component | Detection Logic |
|---------|-----------|-----------------|
| `- [ ]` / `- [x]` | Standard list | Checkbox list items (rendered with ☐/☑) |
| `- item` | Standard list | Unordered list |
| `1. item` | Standard list | Ordered list |

> **Note:** Lists render using ReportLab's built-in paragraph and list styles, not custom components.

**Checklist Example:**
```markdown
- [x] Data collection complete
- [x] Initial analysis done
- [ ] Peer review pending
- [ ] Final report
```

---

### Metadata Header

| Pattern | Component | Detection Logic |
|---------|-----------|-----------------|
| YAML frontmatter | `MetadataHeader` | Document frontmatter fields |

**Rendered Fields:**
- `title` → Document title
- `author` → Author attribution
- `date` → Document date
- `version` → Version number
- `status` → Draft/Review/Final badge

---

## Component Import Reference

```python
from oligon_reports import (
    # Tables (specialized)
    StatusTable,
    GradedTable,

    # Cards
    FindingCard,
    MetricCard,
    MetricCardRow,

    # Text blocks
    MethodBlock,
    CalloutBox,

    # Headers & Layout
    MetadataHeader,
    SectionDivider,
    FigurePlaceholder,
    Timeline,

    # Core
    ReportGenerator,
)
```

> **Note:** Standard tables, lists, and text render using ReportLab primitives via `ReportGenerator`, not custom components.

---

## Mapping Implementation

```python
def map_element_to_component(element, generator: ReportGenerator):
    """Map a parsed element to its PDF component or render directly."""

    if element.type == "table":
        if has_status_symbols(element):
            return StatusTable(element.data)
        elif has_grade_values(element):
            return GradedTable(element.data)
        else:
            # Standard tables render via ReportGenerator
            generator.add_table(element.data)
            return None

    elif element.type == "heading" and is_finding_heading(element):
        return FindingCard(
            number=extract_finding_number(element),
            title=extract_finding_title(element),
            content=element.content
        )

    elif element.type == "code_block":
        if element.language in ("python", "r", "bash", "sql", "pseudocode"):
            return MethodBlock(element.code, language=element.language)
        else:
            # Generic code blocks render via ReportGenerator
            generator.add_code_block(element.code, element.language)
            return None

    elif element.type == "blockquote" and is_callout(element):
        callout_type = detect_callout_type(element)
        return CalloutBox(element.content, style=callout_type)

    elif element.type == "list":
        # All lists render via ReportGenerator (handles checkboxes too)
        generator.add_list(element.items, checked=has_checkboxes(element))
        return None

    # Default: render as paragraph
    generator.add_paragraph(element.content)
    return None
```

> **Note:** Returns `None` when element is rendered directly via `ReportGenerator` rather than as a custom component.

---

## Detection Helper Functions

```python
STATUS_SYMBOLS = {"✓", "✗", "✔", "✘", "Yes", "No", "Pass", "Fail", "Done", "Pending"}
GRADE_VALUES = {"A", "B", "C", "D", "F", "Tier 1", "Tier 2", "Tier 3", "High", "Medium", "Low"}

def has_status_symbols(table_element) -> bool:
    """Check if table contains status symbols."""
    for row in table_element.rows:
        for cell in row:
            if cell.strip() in STATUS_SYMBOLS:
                return True
    return False

def has_grade_values(table_element) -> bool:
    """Check if table contains grade values."""
    for row in table_element.rows:
        for cell in row:
            if cell.strip() in GRADE_VALUES:
                return True
    return False

def is_finding_heading(element) -> bool:
    """Check if heading is a finding heading."""
    import re
    return bool(re.match(r"Finding \d+:|Key Finding:", element.text))

def detect_callout_type(element) -> str:
    """Detect callout type from blockquote content."""
    text = element.content.lower()
    if text.startswith("> **note:") or text.startswith("> **info:"):
        return "info"
    elif text.startswith("> **tip:"):
        return "success"
    elif text.startswith("> **warning:") or text.startswith("> **caution:"):
        return "warning"
    elif text.startswith("> **important:") or text.startswith("> **critical:"):
        return "alert"
    return "info"  # default
```

---

## Brand Colors Applied

Components automatically use Oligon brand colors:

| Component | Primary Color | Usage |
|-----------|---------------|-------|
| FindingCard | `#1E3A5F` (Navy) | Card header |
| StatusTable ✓ | `#2E7D32` (Green) | Pass indicators |
| StatusTable ✗ | `#C62828` (Red) | Fail indicators |
| GradedTable A | `#1B5E20` (Dark Green) | Top grade |
| GradedTable F | `#B71C1C` (Dark Red) | Failing grade |
| CalloutBox info | `#1565C0` (Blue) | Information |
| CalloutBox warning | `#F57C00` (Amber) | Warnings |
| CalloutBox alert | `#C62828` (Red) | Critical |
| MethodBlock | `#37474F` (Blue Grey) | Code background |

See `docs/template-project/brand/BRAND_COLORS_v4.md` for full palette.
