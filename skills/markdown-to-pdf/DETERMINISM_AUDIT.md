# Determinism Audit: markdown-to-pdf

> Audit Date: 2025-01-08
> Skill Version: 1.0.0
> Development Stage: First Draft Skill
> Current Determinism Score: 85%
> Target Determinism Score: 95%

---

## Executive Summary

The markdown-to-pdf skill is **already highly deterministic** (~85%) due to its excellent design choice of delegating core logic to Python libraries (`oligon_reports`) with explicit pattern matching. The LLM's role is primarily workflow orchestration and presentation formatting. Key improvements should focus on standardizing output formats, adding preflight validation, and resolving brand color inconsistencies between documentation files.

---

## Audit Dimensions

### Input Standardization

**Current State: Strong**

Inputs are well-defined:
- Template types are explicitly enumerated (12 types, 4 categories)
- Markdown files require YAML frontmatter with specific fields
- Detection patterns use predefined sets (`STATUS_SYMBOLS`, `GRADE_VALUES`)

**Recommendations:**

| Priority | Improvement | Implementation |
|----------|-------------|----------------|
| P1 | Add JSON schema for frontmatter validation | Create `templates/schemas/<type>.json` for each template type |
| P2 | Enforce frontmatter type enum | Validate `type` field against `TemplateParser.list_templates()` |
| P3 | Add file extension validation | Reject non-`.md` files in `/doc-to-pdf` |

**Suggested frontmatter schema:**
```json
{
  "type": "analysis-report",
  "required": ["type", "title", "date"],
  "optional": ["author", "version", "status"],
  "status_enum": ["Draft", "Review", "Final"]
}
```

---

### Output Standardization

**Current State: Moderate**

Outputs are generally predictable but presentation varies:
- Template listing: Fixed format ✓
- Structure tree: LLM-generated format (variable)
- Element summary: LLM-generated counts (variable wording)
- Success/error messages: Variable phrasing

**Recommendations:**

| Priority | Output | Current | Proposed Deterministic Format |
|----------|--------|---------|------------------------------|
| P0 | Element summary | "3 tables (→ StatusTable)" | Use fixed template: `{count} {type} → {component}` |
| P1 | Structure tree | LLM-formatted | Use `TemplateParser.get_structure_tree()` |
| P2 | Success message | Variable | Fixed template with fill-in values |

**Suggested success message template:**
```
✅ PDF generated: {output_path}

Summary:
- {section_count} sections rendered
- {finding_count} FindingCards
- {status_table_count} StatusTables
- {graded_table_count} GradedTables
- {method_block_count} MethodBlocks
- {callout_count} CalloutBoxes
- Brand styling: {brand_name}
```

---

### Deterministic vs Stochastic Components

**Already Deterministic (Excellent):**

| Component | Implementation | Notes |
|-----------|----------------|-------|
| Table classification | `STATUS_SYMBOLS` and `GRADE_VALUES` sets | Explicit membership check |
| Finding detection | Regex: `Finding \d+:\|Key Finding:` | Deterministic pattern match |
| Callout detection | Prefix matching (`> **Note:**`, etc.) | Fixed prefix list |
| Language filtering | `("python", "r", "bash", "sql", "pseudocode")` | Explicit enum |
| Template listing | `TemplateParser.list_templates()` | Fixed data source |
| Filename generation | `{type}_{YYYYMMDD}.md` | Date-based, deterministic |

**Opportunities for Additional Determinism:**

| Current Behavior | Deterministic Alternative | Priority |
|------------------|---------------------------|----------|
| LLM decides element types | Add `TemplateParser.detect_elements()` returning typed list | P0 |
| LLM formats structure tree | Add `TemplateParser.format_structure_tree()` returning fixed string | P1 |
| LLM summarizes validation | Return `ValidationResult` dataclass with typed errors | P1 |
| LLM suggests error recovery | Create `error_recovery_map.json` with error→solution mappings | P2 |

---

### Reproducibility Assessment

**Rating: HIGH (85%)**

**Factors Supporting Reproducibility:**
- Core parsing logic in Python library (not LLM-dependent)
- Explicit pattern matching with predefined sets
- Fixed template catalog
- Deterministic component mapping

**Factors Reducing Reproducibility:**
- Presentation formatting varies by LLM invocation
- Confirmation prompt wording may vary
- Error messages are LLM-generated
- Brand color inconsistency between files

**Critical Issue - Brand Color Mismatch:**
```
SKILL.md says:          component_map.md says:
Accent: #2DB2E8         FindingCard: #1E3A5F
Alert:  #E8622D         CalloutBox alert: #C62828
```
This inconsistency should be resolved with a single source of truth.

---

### Code Integration Opportunities

The skill already excels at code integration. Minor additions recommended:

**1. Preflight Validator (P0)**
```python
# Add to oligon_reports
def preflight_check(markdown_path: str) -> PreflightResult:
    """Returns structured validation result."""
    return PreflightResult(
        file_exists=True,
        frontmatter_valid=True,
        frontmatter_errors=[],
        required_sections_present=True,
        missing_sections=[],
        element_counts={
            "tables": 3,
            "status_tables": 1,
            "graded_tables": 1,
            "findings": 2,
            "callouts": 1,
            "code_blocks": 3,
            "method_blocks": 2
        }
    )
```

**2. Structure Tree Generator (P1)**
```python
def format_structure_tree(tree: DocumentTree) -> str:
    """Returns deterministic ASCII tree representation."""
    # Fixed format, no LLM variability
```

**3. Error Recovery Lookup (P2)**
```json
{
  "FileNotFoundError": "Verify path exists: ls {path}",
  "KeyError: 'type'": "Add frontmatter: ---\ntype: {suggested_type}\n---",
  "ValidationError": "Check template schema for required fields",
  "ModuleNotFoundError": "Run: uv sync"
}
```

---

### Best Practices Alignment

**Strengths:**
- Clear command structure with decision tree
- Comprehensive error handling documentation
- Anti-patterns section prevents common mistakes
- Cross-references to related skills
- API reference with code examples

**Areas for Improvement:**

| Issue | Current | Best Practice |
|-------|---------|---------------|
| Brand color source | Listed in skill prose | Reference `brand-tokens.json` directly |
| Template schema | Implicit in templates | Explicit JSON schemas |
| Detection patterns | Duplicated in skill + reference | Single source in Python code |
| Success criteria | Manual checklist | Automated validation tests |

---

### Maintainability Assessment

**Rating: HIGH**

**Justification:**
- Clean separation between skill orchestration and library implementation
- Well-organized sections with clear purposes
- Comprehensive error handling table
- API reference with concrete code examples
- Cross-references to related documentation

**Minor Concerns:**
- Some duplication between SKILL.md and component_map.md (detection logic)
- Brand colors listed in multiple places with inconsistent values

---

### Complexity Assessment

**Rating: APPROPRIATE**

The complexity is well-justified:
- 12 templates × 4 categories = reasonable scope
- Component mapping is necessary for rich PDF output
- Detection logic is inherently complex (pattern matching)

**No Unnecessary Complexity Found.**

The skill avoids over-engineering by:
- Delegating parsing to existing library
- Using explicit symbol sets instead of heuristics
- Keeping commands focused (single responsibility)

---

## Implementation Plan

### Phase 1: Critical Fixes (P0)

| Item | Description | Effort |
|------|-------------|--------|
| Preflight validator | Create `preflight_check()` returning `PreflightResult` dataclass | Medium |
| Brand color fix | Resolve inconsistency - single source in `brand-tokens.json` | Low |
| Element summary template | Standardize output format for element counts | Low |

### Phase 2: Output Standardization (P1)

| Item | Description | Effort |
|------|-------------|--------|
| Structure tree generator | Add `format_structure_tree()` for deterministic output | Low |
| Frontmatter schemas | Create JSON schemas for each template type | Medium |
| Validation result type | Return typed `ValidationResult` instead of LLM prose | Medium |

### Phase 3: Polish (P2)

| Item | Description | Effort |
|------|-------------|--------|
| Error recovery map | Create `error_recovery_map.json` for troubleshooting | Low |
| Automated tests | Test suite for success criteria checklist | Medium |
| Documentation dedup | Remove duplicated detection logic | Low |

---

## Determinism Score Projection

| Stage | Score | Key Improvements |
|-------|-------|------------------|
| Current | 85% | Strong library delegation, explicit pattern matching |
| After Phase 1 | 90% | Preflight validation, brand consistency |
| After Phase 2 | 93% | Standardized outputs, typed results |
| After Phase 3 | 95% | Error recovery map, full test coverage |

---

## Appendix: Detection Pattern Reference

The skill uses these deterministic patterns (from `component_map.md`):

```python
STATUS_SYMBOLS = {"✓", "✗", "✔", "✘", "Yes", "No", "Pass", "Fail", "Done", "Pending"}
GRADE_VALUES = {"A", "B", "C", "D", "F", "Tier 1", "Tier 2", "Tier 3", "High", "Medium", "Low"}

# Finding detection regex
FINDING_PATTERN = r"Finding \d+:|Key Finding:"

# Callout prefixes
CALLOUT_PREFIXES = {
    "info": ["> **Note:**", "> **Info:**"],
    "success": ["> **Tip:**"],
    "warning": ["> **Warning:**", "> **Caution:**"],
    "alert": ["> **Important:**", "> **Critical:**"]
}

# Method block languages
METHOD_LANGUAGES = ("python", "r", "bash", "sql", "pseudocode", "algorithm")
```

These patterns are the foundation of the skill's high determinism score.
