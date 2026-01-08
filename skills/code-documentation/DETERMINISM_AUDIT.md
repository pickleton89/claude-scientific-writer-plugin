# Determinism Audit: code-documentation

> Audit Date: 2026-01-08
> Skill Stage: First draft skill
> Current Determinism: ~65%
> Target Determinism: 85%

---

## Executive Summary

The code-documentation skill is well-designed with extensive reference materials and clear templates. The main gaps are: (1) no programmatic validation of generated documentation against the well-defined templates/checklists, and (2) implicit rather than enforced selection logic for styles and templates. With a validation layer and formalized input schemas, this skill can reach 85% determinism.

---

## Current State Analysis

### Strengths
- Excellent reference documentation with concrete examples
- Clear decision tree for style selection (SKILL.md lines 93-101)
- Comprehensive templates for all README types (4 distinct templates)
- Anti-patterns clearly documented (what NOT to do)
- Cross-references to related skills
- Validation checklists provided in `<validation>` section

### Gaps
- Decision tree is narrative, not enforced programmatically
- No structured input format specification
- Validation checklists are advisory, not automated
- Missing quantified quality metrics
- No output schema enforcement

---

## Deterministic Opportunities

| Component | Current State | Proposed Solution | Impact |
|-----------|---------------|-------------------|--------|
| Style selection | LLM interprets decision tree | Code-based selector function | High |
| README template selection | LLM chooses based on context | Lookup table by project type | High |
| Docstring format validation | Post-hoc manual pydocstyle | Automated validation script | High |
| Example validation | Manual doctest suggestion | Automated execution check | Medium |
| Section ordering | Guidelines in reference docs | Schema enforcement | Medium |
| Parameter extraction | LLM reads code | AST parsing pre-processor | Medium |
| Type hint integration | LLM interprets annotations | Automated extraction | Low |

---

## Implementation Plan

### Phase 1: Validation Infrastructure (P0)

**Create `scripts/validate_documentation.py`:**

```python
#!/usr/bin/env python
"""Validate documentation meets skill standards."""

import argparse
import subprocess
import sys
import re
from pathlib import Path

# Required README sections by project type
README_SECTIONS = {
    "analysis": ["overview", "data", "environment", "usage", "results", "citation", "license"],
    "software": ["description", "installation", "quickstart", "documentation", "contributing", "license"],
    "data_repo": ["overview", "files", "data_dictionary", "collection", "usage", "terms"],
    "compendium": ["overview", "structure", "reproduce", "data", "code", "license", "citation"],
}

def validate_python_docstrings(path: str, style: str) -> tuple[int, str]:
    """Run pydocstyle and return exit code and output."""
    convention = "numpy" if style == "numpy" else "google"
    result = subprocess.run(
        ["pydocstyle", f"--convention={convention}", path],
        capture_output=True, text=True
    )
    return result.returncode, result.stdout + result.stderr

def validate_doctests(path: str) -> tuple[int, str]:
    """Run doctests and return exit code and output."""
    result = subprocess.run(
        ["python", "-m", "doctest", "-v", path],
        capture_output=True, text=True
    )
    return result.returncode, result.stdout + result.stderr

def validate_readme_sections(readme_path: str, project_type: str) -> list[str]:
    """Check README has all required sections for project type."""
    if project_type not in README_SECTIONS:
        return [f"Unknown project type: {project_type}"]

    content = Path(readme_path).read_text().lower()
    required = README_SECTIONS[project_type]
    missing = []

    for section in required:
        # Check for section header (## Section or # Section)
        pattern = rf"#{{1,2}}\s*{section}"
        if not re.search(pattern, content, re.IGNORECASE):
            missing.append(section)

    return missing

def main():
    parser = argparse.ArgumentParser(description="Validate documentation")
    parser.add_argument("path", help="File or directory to validate")
    parser.add_argument("--style", choices=["numpy", "google"], default="numpy")
    parser.add_argument("--readme", help="README file to validate")
    parser.add_argument("--project-type", choices=list(README_SECTIONS.keys()))
    args = parser.parse_args()

    exit_code = 0

    # Validate Python docstrings
    if args.path.endswith(".py"):
        code, output = validate_python_docstrings(args.path, args.style)
        if code != 0:
            print(f"Docstring validation failed:\n{output}")
            exit_code = 1
        else:
            print(f"Docstring validation passed ({args.style} style)")

        # Validate doctests
        code, output = validate_doctests(args.path)
        if code != 0:
            print(f"Doctest validation failed:\n{output}")
            exit_code = 1
        else:
            print("Doctest validation passed")

    # Validate README
    if args.readme and args.project_type:
        missing = validate_readme_sections(args.readme, args.project_type)
        if missing:
            print(f"README missing sections: {', '.join(missing)}")
            exit_code = 1
        else:
            print(f"README has all required sections for {args.project_type}")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
```

### Phase 2: Input Standardization (P1)

**Create `scripts/infer_style.py`:**

```python
#!/usr/bin/env python
"""Deterministic docstring style selection."""

import ast
import re
from pathlib import Path
from typing import Literal

DocstringStyle = Literal["numpy", "google", "roxygen2", "minimal"]

def detect_existing_style(code: str) -> DocstringStyle | None:
    """Detect docstring style from existing code."""
    # NumPy style indicators
    if re.search(r"Parameters\n\s*-{3,}", code):
        return "numpy"
    if re.search(r"Returns\n\s*-{3,}", code):
        return "numpy"

    # Google style indicators
    if re.search(r"Args:\n\s+\w+:", code):
        return "google"
    if re.search(r"Returns:\n\s+\w+", code):
        return "google"

    return None

def infer_docstring_style(
    is_package: bool,
    is_r: bool,
    is_scientific: bool,
    is_quick_script: bool,
    existing_style: DocstringStyle | None = None
) -> DocstringStyle:
    """
    Deterministic style selection implementing SKILL.md decision tree.

    Decision tree (SKILL.md lines 93-101):
    1. If existing style in codebase -> match it
    2. If R code -> roxygen2
    3. If not a package and quick script -> minimal
    4. If scientific Python -> numpy
    5. Default -> google
    """
    if existing_style:
        return existing_style
    if is_r:
        return "roxygen2"
    if not is_package and is_quick_script:
        return "minimal"
    if is_scientific:
        return "numpy"
    return "google"

def analyze_project(project_path: str) -> dict:
    """Analyze project to determine documentation style."""
    path = Path(project_path)

    # Detect language
    py_files = list(path.glob("**/*.py"))
    r_files = list(path.glob("**/*.R")) + list(path.glob("**/*.r"))
    is_r = len(r_files) > len(py_files)

    # Detect if package
    is_package = (path / "setup.py").exists() or (path / "pyproject.toml").exists()
    if is_r:
        is_package = (path / "DESCRIPTION").exists()

    # Detect scientific context
    scientific_indicators = ["numpy", "scipy", "pandas", "scikit", "bio", "stats"]
    is_scientific = False
    for py_file in py_files[:5]:  # Sample first 5 files
        content = py_file.read_text()
        if any(ind in content.lower() for ind in scientific_indicators):
            is_scientific = True
            break

    # Detect existing style
    existing_style = None
    for py_file in py_files[:5]:
        content = py_file.read_text()
        detected = detect_existing_style(content)
        if detected:
            existing_style = detected
            break

    # Quick script detection
    is_quick_script = len(py_files) <= 2 and not is_package

    return {
        "is_package": is_package,
        "is_r": is_r,
        "is_scientific": is_scientific,
        "is_quick_script": is_quick_script,
        "existing_style": existing_style,
        "recommended_style": infer_docstring_style(
            is_package, is_r, is_scientific, is_quick_script, existing_style
        ),
    }
```

### Phase 3: Output Schema Enforcement (P2)

**Docstring section schemas:**

```python
# NumPy style required sections (in order)
NUMPY_SECTIONS = {
    "short_summary": {"required": True, "order": 0},
    "extended_summary": {"required": False, "order": 1},
    "parameters": {"required": "if_has_params", "order": 2},
    "returns": {"required": "if_returns", "order": 3},
    "yields": {"required": "if_generator", "order": 4},
    "raises": {"required": False, "order": 5},
    "see_also": {"required": False, "order": 6},
    "notes": {"required": False, "order": 7},
    "references": {"required": False, "order": 8},
    "examples": {"required": "recommended", "order": 9},
}

# Google style required sections
GOOGLE_SECTIONS = {
    "summary": {"required": True},
    "args": {"required": "if_has_params"},
    "returns": {"required": "if_returns"},
    "raises": {"required": False},
    "example": {"required": "recommended"},
}
```

**README template selector:**

```python
README_TEMPLATES = {
    "analysis": "references/readme_templates.md#analysis-project",
    "software": "references/readme_templates.md#software-tool",
    "data_repo": "references/readme_templates.md#data-repository",
    "compendium": "references/readme_templates.md#research-compendium",
}

def get_readme_template(project_type: str) -> str:
    """Deterministic README template selection."""
    return README_TEMPLATES.get(project_type, README_TEMPLATES["software"])
```

---

## Quality Thresholds

| Metric | Threshold | Validation Method |
|--------|-----------|-------------------|
| Docstring coverage | 100% public API | AST analysis |
| Parameter documentation | 100% of params | Docstring parsing |
| Return documentation | Required if non-None | Signature analysis |
| Example presence | 1+ per function | Docstring parsing |
| Example execution | 0 failures | doctest |
| pydocstyle compliance | 0 errors | pydocstyle |
| README sections | 100% required | Section regex |

---

## Validation Requirements

All generated documentation MUST pass:

1. **Docstring format**: `pydocstyle --convention={style} <file>` (zero errors)
2. **Example execution**: `python -m doctest <file>` (zero failures)
3. **README completeness**: All required sections for project type present

**Run validation:**
```bash
python scripts/validate_documentation.py <path> --style <style>
python scripts/validate_documentation.py --readme README.md --project-type analysis
```

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Style selection consistency | ~70% | 95% | Same input → same style |
| Template adherence | ~60% | 90% | Section completeness |
| Example validity | ~50% | 95% | doctest pass rate |
| Format compliance | ~65% | 95% | pydocstyle pass rate |
| Overall determinism | ~65% | 85% | Composite score |

---

## Implementation Priority

| Priority | Task | Impact | Effort |
|----------|------|--------|--------|
| P0 | Create validation script | High | Low |
| P0 | Add validation requirements to SKILL.md | High | Low |
| P1 | Create style inference script | High | Medium |
| P1 | Define input schema | Medium | Low |
| P2 | Add output schema definitions | Medium | Medium |
| P2 | Implement README section checker | Medium | Low |
| P3 | Add AST-based parameter extraction | Low | Medium |

---

## Remaining Non-Deterministic Components (Acceptable)

These components appropriately remain LLM-driven:

1. **Prose content** - Writing meaningful descriptions requires understanding
2. **Example selection** - Choosing illustrative examples benefits from judgment
3. **Comment placement** - Deciding when complexity warrants explanation
4. **Cross-reference suggestions** - Identifying related functions/skills
5. **Notes content** - Explaining implementation details and caveats

These represent ~15% of the skill's output and genuinely benefit from LLM flexibility.

---

## Files to Create

```
skills/code-documentation/
├── SKILL.md (update <validation> section)
├── DETERMINISM_AUDIT.md (this file)
└── scripts/
    ├── validate_documentation.py
    ├── infer_style.py
    └── check_readme.py
```
