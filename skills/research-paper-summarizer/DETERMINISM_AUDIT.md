# Determinism Audit: Research Paper Summarizer

> **Audit Date**: 2026-01-07
> **Skill Version**: 1.1.0
> **Development Stage**: First Draft
> **Auditor**: Claude Opus 4.5

---

## Executive Summary

The research-paper-summarizer skill has excellent architectural foundations—a well-designed subagent pipeline, structured templates with section markers, and comprehensive reference documentation. However, the current implementation relies heavily on LLM interpretation for tasks that could be deterministic: PDF section detection, statistics extraction, output validation, and file marker updates.

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| **Reproducibility** | ~55-60% | 75-80% | Phase 1-2 |
| **Validation Coverage** | Manual | Automated | Phase 1 |
| **Code-Based Processing** | ~20% | ~50% | Phase 2 |

---

## Current Architecture Assessment

### Strengths (Deterministic Foundations)

| Component | Assessment |
|-----------|------------|
| **Page threshold** | Fixed at 12 pages - fully deterministic |
| **Subagent sequence** | Fixed order per article type - deterministic |
| **Section markers** | PENDING/COMPLETE tracking - good structure |
| **Skeleton templates** | Consistent structure with placeholders |
| **Statistics guide** | Comprehensive formatting reference |
| **Article type routing** | Four defined pathways |

### Weaknesses (Stochastic Dependencies)

| Component | Current State | Issue |
|-----------|---------------|-------|
| PDF section detection | LLM-based | Variable boundary identification |
| Statistics extraction | Prose parsing | Inconsistent stat presentation |
| Section marker updates | LLM file editing | Potential marker corruption |
| Output validation | Manual checklist | No automated enforcement |
| Article type selection | Manual only | User error possible |
| Figure reference matching | LLM interpretation | Variable reference format |

---

## Deterministic Opportunities

### High Priority

| Task | Current | Proposed | Impact |
|------|---------|----------|--------|
| Output validation | Manual checklist | `validate_summary.py` | High |
| Statistics extraction | LLM prose parsing | Regex pre-extraction | High |
| YAML validation | None | JSON Schema | High |
| Section markers | LLM editing | Regex replacement | High |

### Medium Priority

| Task | Current | Proposed | Impact |
|------|---------|----------|--------|
| Article type detection | Manual selection | Keyword scoring | Medium |
| Figure ref extraction | LLM parsing | Regex patterns | Medium |
| PDF section detection | LLM scanning | Keyword + heuristics | Medium |
| Statistics formatting | Prose guidelines | Code normalizer | Medium |

---

## Implementation Plan

### Phase 1: Validation Infrastructure (Priority: Critical)

#### 1.1 Create `scripts/validate_summary.py`

Automated quality gate for completed summaries.

```python
#!/usr/bin/env python3
"""
Summary Validation Script

Validates completed summary files against quality criteria.
Returns pass/fail with detailed check results.

Usage:
    python validate_summary.py summary.md
    python validate_summary.py summary.md --strict
"""

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class ValidationResult(NamedTuple):
    name: str
    passed: bool
    message: str
    severity: str  # 'error', 'warning', 'info'


def validate_summary(file_path: str, strict: bool = False) -> dict:
    """
    Validate a completed summary file.

    Returns:
        {
            'valid': bool,
            'score': float (0-1),
            'checks': list[ValidationResult],
            'errors': int,
            'warnings': int
        }
    """
    content = Path(file_path).read_text(encoding='utf-8')
    checks = []

    # === CRITICAL CHECKS (failures = invalid) ===

    # No pending sections
    pending_count = len(re.findall(r'<!-- SECTION: \w+ PENDING -->', content))
    checks.append(ValidationResult(
        'no_pending_sections',
        pending_count == 0,
        f"Found {pending_count} PENDING sections" if pending_count else "All sections complete",
        'error'
    ))

    # Has executive summary content
    exec_match = re.search(r'## 1\. Executive Summary\s+(.+?)(?=\n## |\n<!-- SECTION)', content, re.DOTALL)
    has_exec = exec_match and len(exec_match.group(1).strip()) > 50
    checks.append(ValidationResult(
        'has_executive_summary',
        has_exec,
        "Executive summary present" if has_exec else "Executive summary missing or too short",
        'error'
    ))

    # Has statistics (at least 3 p-values, CIs, or sample sizes)
    stat_patterns = [
        r'p\s*[<=]\s*0?\.\d+',           # p-values
        r'\d+%\s*CI',                     # confidence intervals
        r'n\s*=\s*\d+',                   # sample sizes
        r'\d+\.?\d*-fold',                # fold changes
        r'HR\s*=\s*[\d.]+',               # hazard ratios
        r'OR\s*=\s*[\d.]+',               # odds ratios
    ]
    stat_count = sum(len(re.findall(p, content, re.I)) for p in stat_patterns)
    checks.append(ValidationResult(
        'has_statistics',
        stat_count >= 3,
        f"Found {stat_count} statistical values" if stat_count >= 3 else f"Only {stat_count} stats found (need 3+)",
        'error'
    ))

    # Has figure references
    fig_refs = re.findall(r'(?:Figure|Fig\.?|Table)\s+\d+[A-Za-z]?', content, re.I)
    checks.append(ValidationResult(
        'has_figure_refs',
        len(fig_refs) >= 2,
        f"Found {len(fig_refs)} figure/table references",
        'error' if len(fig_refs) == 0 else 'warning'
    ))

    # Has limitations section with content
    lim_match = re.search(r'### Limitations\s+(.+?)(?=\n### |\n## |\n<!-- )', content, re.DOTALL)
    has_lims = lim_match and len(lim_match.group(1).strip()) > 20
    checks.append(ValidationResult(
        'has_limitations',
        has_lims,
        "Limitations documented" if has_lims else "Limitations section empty or missing",
        'warning'
    ))

    # === QUALITY CHECKS (warnings only) ===

    # Has sample sizes specified
    sample_sizes = re.findall(r'n\s*=\s*\d+', content)
    checks.append(ValidationResult(
        'has_sample_sizes',
        len(sample_sizes) >= 1,
        f"Found {len(sample_sizes)} sample size specifications",
        'warning'
    ))

    # Has key quote(s)
    quotes = re.findall(r'"[^"]{20,}"', content)
    checks.append(ValidationResult(
        'has_quotes',
        len(quotes) >= 1,
        f"Found {len(quotes)} author quotes",
        'info'
    ))

    # Synthesis section has content
    synth_match = re.search(r'## 10\. One-Paragraph Synthesis\s+(.+?)(?=\n---|\Z)', content, re.DOTALL)
    has_synth = synth_match and len(synth_match.group(1).strip()) > 100
    checks.append(ValidationResult(
        'has_synthesis',
        has_synth,
        "Synthesis paragraph present" if has_synth else "Synthesis section incomplete",
        'warning'
    ))

    # No placeholder text remaining
    placeholders = re.findall(r'\{\{[A-Z_]+\}\}', content)
    checks.append(ValidationResult(
        'no_placeholders',
        len(placeholders) == 0,
        f"Found {len(placeholders)} unfilled placeholders" if placeholders else "No placeholders",
        'error'
    ))

    # Calculate results
    errors = sum(1 for c in checks if not c.passed and c.severity == 'error')
    warnings = sum(1 for c in checks if not c.passed and c.severity == 'warning')

    # In strict mode, warnings count as failures
    if strict:
        valid = errors == 0 and warnings == 0
    else:
        valid = errors == 0

    score = sum(1 for c in checks if c.passed) / len(checks)

    return {
        'valid': valid,
        'score': score,
        'checks': checks,
        'errors': errors,
        'warnings': warnings,
        'file': file_path
    }


def print_results(results: dict):
    """Print validation results in readable format."""
    status = "PASS" if results['valid'] else "FAIL"
    print(f"\n{'=' * 60}")
    print(f"Summary Validation: {status}")
    print(f"File: {results['file']}")
    print(f"Score: {results['score']:.0%} ({sum(1 for c in results['checks'] if c.passed)}/{len(results['checks'])} checks)")
    print(f"{'=' * 60}\n")

    for check in results['checks']:
        icon = "[OK]" if check.passed else "[FAIL]" if check.severity == 'error' else "[WARN]"
        print(f"  {icon} {check.name}: {check.message}")

    print(f"\nErrors: {results['errors']}, Warnings: {results['warnings']}")


def main():
    parser = argparse.ArgumentParser(description='Validate research paper summary')
    parser.add_argument('file', help='Path to summary markdown file')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        return 1

    results = validate_summary(args.file, strict=args.strict)

    if args.json:
        import json
        # Convert NamedTuples to dicts for JSON
        results['checks'] = [c._asdict() for c in results['checks']]
        print(json.dumps(results, indent=2))
    else:
        print_results(results)

    return 0 if results['valid'] else 1


if __name__ == '__main__':
    sys.exit(main())
```

#### 1.2 Create `schemas/summary_output.yaml`

JSON Schema for YAML output validation.

```yaml
# summary_output.yaml
# JSON Schema for validating YAML summary output before PDF generation

$schema: "https://json-schema.org/draft/2020-12/schema"
title: "Research Paper Summary"
type: object

required:
  - metadata
  - overview
  - key_findings
  - methods
  - limitations

properties:
  metadata:
    type: object
    required:
      - title
      - authors
      - year
    properties:
      title:
        type: string
        minLength: 10
      authors:
        type: string
        minLength: 3
      journal:
        type: string
      year:
        type: [integer, string]
      doi:
        type: string
        pattern: "^10\\."
      pmid:
        type: string
      article_type:
        type: string
        enum: ["Primary Research", "Review", "Computational", "Cell & Molecular"]

  overview:
    type: string
    minLength: 100
    maxLength: 1000

  key_findings:
    type: array
    minItems: 3
    maxItems: 10
    items:
      type: object
      required:
        - finding
      properties:
        finding:
          type: string
          minLength: 20
        statistics:
          type: string
        figure_ref:
          type: string
          pattern: "^(Figure|Fig|Table)\\s*\\d+"

  key_figures:
    type: array
    items:
      type: object
      required:
        - number
      properties:
        number:
          type: string
          pattern: "^(Figure|Table)\\s*\\d+"
        title:
          type: string
        importance:
          type: string
        key_findings:
          type: string

  methods:
    type: object
    required:
      - study_design
      - sample_size
    properties:
      study_design:
        type: string
      model_system:
        type: string
      sample_size:
        type: string
      key_techniques:
        type: string
      statistical_analysis:
        type: string
      key_parameters:
        type: string

  limitations:
    type: object
    properties:
      author_stated:
        type: array
        items:
          type: string
      additional:
        type: array
        items:
          type: string

  implications:
    type: string

  relevance_notes:
    type: string
```

#### 1.3 Create `scripts/validate_yaml.py`

```python
#!/usr/bin/env python3
"""
Validate YAML summary against schema before PDF generation.

Usage:
    python validate_yaml.py summary.yaml
"""

import argparse
import sys
from pathlib import Path

import yaml

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def validate_yaml(yaml_path: str, schema_path: str = None) -> dict:
    """Validate YAML against schema."""

    # Load YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    errors = []
    warnings = []

    # Basic structure checks (no schema library needed)
    required_keys = ['metadata', 'overview', 'key_findings', 'methods', 'limitations']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    # Metadata checks
    if 'metadata' in data:
        meta = data['metadata']
        if 'title' not in meta:
            errors.append("metadata.title is required")
        if 'authors' not in meta:
            errors.append("metadata.authors is required")
        if 'year' not in meta:
            warnings.append("metadata.year is recommended")

    # Key findings checks
    if 'key_findings' in data:
        findings = data['key_findings']
        if len(findings) < 3:
            warnings.append(f"Only {len(findings)} key findings (recommend 3+)")
        for i, f in enumerate(findings):
            if isinstance(f, dict):
                if 'finding' not in f:
                    errors.append(f"key_findings[{i}].finding is required")
                if 'statistics' not in f:
                    warnings.append(f"key_findings[{i}] missing statistics")

    # Methods checks
    if 'methods' in data:
        methods = data['methods']
        if 'sample_size' not in methods:
            warnings.append("methods.sample_size is recommended")

    # Full schema validation if available
    if HAS_JSONSCHEMA and schema_path and Path(schema_path).exists():
        with open(schema_path, 'r') as f:
            schema = yaml.safe_load(f)
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation: {e.message}")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'data': data
    }


def main():
    parser = argparse.ArgumentParser(description='Validate YAML summary')
    parser.add_argument('yaml_file', help='Path to YAML summary')
    parser.add_argument('--schema', help='Path to JSON schema', default=None)

    args = parser.parse_args()

    results = validate_yaml(args.yaml_file, args.schema)

    if results['valid']:
        print(f"[OK] YAML validation passed")
        if results['warnings']:
            print(f"Warnings: {len(results['warnings'])}")
            for w in results['warnings']:
                print(f"  - {w}")
        return 0
    else:
        print(f"[FAIL] YAML validation failed")
        for e in results['errors']:
            print(f"  [ERROR] {e}")
        for w in results['warnings']:
            print(f"  [WARN] {w}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

---

### Phase 2: Pre-Processing Scripts

#### 2.1 Create `scripts/extract_statistics.py`

Pre-extract statistics from PDF text for structured processing.

```python
#!/usr/bin/env python3
"""
Extract statistics from research paper text.

Returns structured data with all statistical values found,
enabling deterministic processing before LLM interpretation.

Usage:
    python extract_statistics.py paper.txt
    python extract_statistics.py paper.txt --json
"""

import argparse
import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Statistic:
    type: str           # p_value, ci, sample_size, fold_change, etc.
    value: str          # The extracted value
    context: str        # Surrounding text (50 chars each side)
    position: int       # Character position in document
    normalized: Optional[str] = None  # Standardized format


STAT_PATTERNS = {
    'p_value': [
        (r'p\s*[<=]\s*(0?\.\d+)', 'p = {0}'),
        (r'p\s*<\s*(0\.0+1)', 'p < {0}'),
        (r'P\s*=\s*(0?\.\d+)', 'p = {0}'),
    ],
    'confidence_interval': [
        (r'(\d+)%\s*CI[:\s]+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', '{0}% CI: {1}–{2}'),
        (r'CI[:\s]+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', '95% CI: {0}–{1}'),
    ],
    'sample_size': [
        (r'[nN]\s*=\s*(\d+)', 'n = {0}'),
        (r'[nN]\s*=\s*(\d+)/group', 'n = {0}/group'),
        (r'(\d+)\s+(?:patients|subjects|participants|mice|samples)', 'n = {0}'),
    ],
    'fold_change': [
        (r'(\d+\.?\d*)\s*-?\s*fold\s+(increase|decrease|change)', '{0}-fold {1}'),
        (r'(\d+\.?\d*)\s*×', '{0}×'),
    ],
    'hazard_ratio': [
        (r'HR\s*[=:]\s*(\d+\.?\d*)', 'HR = {0}'),
        (r'hazard ratio[:\s]+(\d+\.?\d*)', 'HR = {0}'),
    ],
    'odds_ratio': [
        (r'OR\s*[=:]\s*(\d+\.?\d*)', 'OR = {0}'),
        (r'odds ratio[:\s]+(\d+\.?\d*)', 'OR = {0}'),
    ],
    'percent_change': [
        (r'(\d+\.?\d*)\s*%\s+(reduction|increase|decrease|improvement)', '{0}% {1}'),
    ],
    'effect_size': [
        (r"Cohen'?s?\s*d\s*[=:]\s*(\d+\.?\d*)", "Cohen's d = {0}"),
        (r'effect size[:\s]+(\d+\.?\d*)', 'effect size = {0}'),
    ],
}


def extract_statistics(text: str) -> list[Statistic]:
    """Extract all statistics from text."""
    stats = []

    for stat_type, patterns in STAT_PATTERNS.items():
        for pattern, norm_template in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Get context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].replace('\n', ' ')

                # Normalize
                groups = match.groups()
                try:
                    normalized = norm_template.format(*groups)
                except:
                    normalized = match.group(0)

                stats.append(Statistic(
                    type=stat_type,
                    value=match.group(0),
                    context=context,
                    position=match.start(),
                    normalized=normalized
                ))

    # Sort by position
    stats.sort(key=lambda s: s.position)

    # Remove duplicates (same position)
    seen_positions = set()
    unique_stats = []
    for s in stats:
        if s.position not in seen_positions:
            unique_stats.append(s)
            seen_positions.add(s.position)

    return unique_stats


def summarize_statistics(stats: list[Statistic]) -> dict:
    """Generate summary counts by type."""
    summary = {}
    for s in stats:
        if s.type not in summary:
            summary[s.type] = []
        summary[s.type].append(s.normalized or s.value)
    return summary


def main():
    parser = argparse.ArgumentParser(description='Extract statistics from text')
    parser.add_argument('file', help='Text file to analyze')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--summary', action='store_true', help='Show summary only')

    args = parser.parse_args()

    text = Path(args.file).read_text(encoding='utf-8')
    stats = extract_statistics(text)

    if args.json:
        output = {
            'statistics': [asdict(s) for s in stats],
            'summary': summarize_statistics(stats),
            'total_count': len(stats)
        }
        print(json.dumps(output, indent=2))
    elif args.summary:
        summary = summarize_statistics(stats)
        print(f"Found {len(stats)} statistical values:\n")
        for stat_type, values in summary.items():
            print(f"  {stat_type}: {len(values)}")
            for v in values[:3]:
                print(f"    - {v}")
            if len(values) > 3:
                print(f"    ... and {len(values) - 3} more")
    else:
        print(f"Extracted {len(stats)} statistics:\n")
        for s in stats:
            print(f"  [{s.type}] {s.normalized}")
            print(f"    Context: ...{s.context}...")
            print()


if __name__ == '__main__':
    main()
```

#### 2.2 Create `scripts/detect_article_type.py`

Auto-detect article type from abstract/introduction.

```python
#!/usr/bin/env python3
"""
Detect article type from paper abstract/introduction.

Returns suggested article type with confidence score.

Usage:
    python detect_article_type.py abstract.txt
"""

import argparse
import re
from pathlib import Path


# Keywords associated with each article type
TYPE_KEYWORDS = {
    'review': {
        'high': ['systematic review', 'meta-analysis', 'literature review', 'we reviewed',
                 'narrative review', 'scoping review', 'umbrella review'],
        'medium': ['review of', 'overview of', 'synthesis of', 'survey of literature',
                   'examined the literature', 'published studies'],
        'low': ['reviewed', 'summarize', 'consolidate'],
    },
    'compbio': {
        'high': ['bioinformatic', 'computational pipeline', 'RNA-seq', 'genome-wide',
                 'machine learning', 'deep learning', 'algorithm', 'benchmark'],
        'medium': ['dataset', 'database', 'sequencing data', 'transcriptome',
                   'proteome', 'metabolome', 'single-cell', 'multi-omics'],
        'low': ['computational', 'in silico', 'prediction', 'modeling'],
    },
    'cellmolbio': {
        'high': ['mechanism', 'signaling pathway', 'molecular basis', 'in vitro',
                 'cell line', 'western blot', 'immunoprecipitation', 'CRISPR'],
        'medium': ['transfection', 'knockdown', 'overexpression', 'mouse model',
                   'xenograft', 'cell culture', 'protein expression', 'phosphorylation'],
        'low': ['cells', 'molecular', 'protein', 'gene expression'],
    },
    'general': {
        'high': [],  # Default when others don't match
        'medium': ['clinical trial', 'cohort study', 'case-control', 'observational'],
        'low': ['study', 'research', 'investigation', 'analysis'],
    },
}

# Weights for keyword confidence levels
WEIGHTS = {'high': 3, 'medium': 2, 'low': 1}


def detect_article_type(text: str) -> tuple[str, float, dict]:
    """
    Detect article type from text.

    Returns:
        (article_type, confidence, scores_breakdown)
    """
    text_lower = text.lower()
    scores = {}

    for article_type, keyword_groups in TYPE_KEYWORDS.items():
        score = 0
        matches = []

        for level, keywords in keyword_groups.items():
            weight = WEIGHTS[level]
            for keyword in keywords:
                if keyword in text_lower:
                    score += weight
                    matches.append((keyword, level))

        scores[article_type] = {
            'score': score,
            'matches': matches
        }

    # Find best match
    best_type = max(scores, key=lambda t: scores[t]['score'])
    best_score = scores[best_type]['score']

    # Calculate confidence (0-1)
    total_possible = sum(
        len(kws) * WEIGHTS[level]
        for level, kws in TYPE_KEYWORDS[best_type].items()
    )
    confidence = min(best_score / max(total_possible, 1), 1.0)

    # If no strong signal, default to general
    if best_score < 3:
        best_type = 'general'
        confidence = 0.5

    return best_type, confidence, scores


def main():
    parser = argparse.ArgumentParser(description='Detect article type')
    parser.add_argument('file', help='Text file (abstract/introduction)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed breakdown')

    args = parser.parse_args()

    text = Path(args.file).read_text(encoding='utf-8')
    article_type, confidence, scores = detect_article_type(text)

    # Map to display names
    TYPE_NAMES = {
        'review': 'Review Article',
        'compbio': 'Computational Biology',
        'cellmolbio': 'Cell & Molecular Biology',
        'general': 'General Research',
    }

    print(f"Detected: {TYPE_NAMES[article_type]}")
    print(f"Confidence: {confidence:.0%}")

    if args.verbose:
        print("\nScore breakdown:")
        for t, data in sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True):
            print(f"  {TYPE_NAMES[t]}: {data['score']} points")
            for keyword, level in data['matches'][:5]:
                print(f"    - '{keyword}' ({level})")


if __name__ == '__main__':
    main()
```

#### 2.3 Create `scripts/update_markers.py`

Deterministic section marker management.

```python
#!/usr/bin/env python3
"""
Deterministic section marker management.

Updates section markers in summary files without LLM involvement.

Usage:
    python update_markers.py summary.md --complete executive_summary
    python update_markers.py summary.md --skip methods
    python update_markers.py summary.md --status
"""

import argparse
import re
from pathlib import Path


def get_markers(content: str) -> dict:
    """Get all section markers and their status."""
    pattern = r'<!-- (SECTION|SUBSECTION): (\w+) (PENDING|COMPLETE|SKIPPED) -->'
    markers = {}
    for match in re.finditer(pattern, content):
        marker_type, name, status = match.groups()
        markers[name] = {
            'type': marker_type.lower(),
            'status': status.lower(),
            'position': match.start()
        }
    return markers


def update_marker(content: str, section_name: str, new_status: str) -> str:
    """Update a section marker to new status."""
    pattern = rf'(<!-- (?:SECTION|SUBSECTION): {section_name}) (PENDING|COMPLETE|SKIPPED)( -->)'
    replacement = rf'\1 {new_status.upper()}\3'

    new_content, count = re.subn(pattern, replacement, content)

    if count == 0:
        raise ValueError(f"Section marker not found: {section_name}")

    return new_content


def insert_content(content: str, section_name: str, new_content: str) -> str:
    """Insert content before a section marker."""
    pattern = rf'(<!-- (?:SECTION|SUBSECTION): {section_name}) PENDING( -->)'

    # Escape backslashes in new_content for regex replacement
    escaped_content = new_content.replace('\\', '\\\\')
    replacement = f'{escaped_content}\n\n\\1 COMPLETE\\2'

    return re.sub(pattern, replacement, content)


def print_status(markers: dict):
    """Print marker status summary."""
    print(f"{'Section':<30} {'Type':<12} {'Status':<10}")
    print("-" * 52)

    for name, info in sorted(markers.items(), key=lambda x: x[1]['position']):
        status_icon = {
            'pending': '[  ]',
            'complete': '[OK]',
            'skipped': '[--]'
        }.get(info['status'], '[??]')

        print(f"{name:<30} {info['type']:<12} {status_icon} {info['status']}")

    # Summary
    total = len(markers)
    complete = sum(1 for m in markers.values() if m['status'] == 'complete')
    pending = sum(1 for m in markers.values() if m['status'] == 'pending')

    print(f"\nProgress: {complete}/{total} complete ({pending} pending)")


def main():
    parser = argparse.ArgumentParser(description='Manage section markers')
    parser.add_argument('file', help='Summary markdown file')
    parser.add_argument('--complete', metavar='SECTION', help='Mark section as complete')
    parser.add_argument('--skip', metavar='SECTION', help='Mark section as skipped')
    parser.add_argument('--pending', metavar='SECTION', help='Reset section to pending')
    parser.add_argument('--status', action='store_true', help='Show all marker statuses')
    parser.add_argument('--insert', metavar='CONTENT', help='Insert content before marking complete')

    args = parser.parse_args()

    file_path = Path(args.file)
    content = file_path.read_text(encoding='utf-8')

    if args.status:
        markers = get_markers(content)
        print_status(markers)
        return

    modified = False

    if args.complete:
        if args.insert:
            content = insert_content(content, args.complete, args.insert)
        content = update_marker(content, args.complete, 'COMPLETE')
        modified = True
        print(f"Marked {args.complete} as COMPLETE")

    if args.skip:
        content = update_marker(content, args.skip, 'SKIPPED')
        modified = True
        print(f"Marked {args.skip} as SKIPPED")

    if args.pending:
        content = update_marker(content, args.pending, 'PENDING')
        modified = True
        print(f"Reset {args.pending} to PENDING")

    if modified:
        file_path.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main()
```

---

### Phase 3: Integration

#### 3.1 Update Subagent Prompts

Add structured output requirements to subagent prompts:

```markdown
## Output Requirements

Your output MUST include these elements:

<statistics_found>
List all statistics extracted, one per line in normalized format:
- p = 0.003 (DFMO vs control)
- n = 24/group
- 2.3-fold increase
</statistics_found>

<figure_references>
List all figures/tables referenced:
- Figure 1A: [description]
- Table 2: [description]
</figure_references>

Write your prose analysis after these structured sections.
```

#### 3.2 Update SKILL.md Workflow

Add validation steps to the workflow:

```markdown
### Validation Steps

After markdown summary is generated:

1. **Run validation script**:
   ```bash
   python scripts/validate_summary.py {summary_file}
   ```

2. **Check results**:
   - If PASS: Proceed to visual output
   - If FAIL: Review errors and re-run affected subagents

3. **Before PDF generation**:
   ```bash
   python scripts/validate_yaml.py {yaml_file}
   ```
```

---

## Success Metrics

| Metric | Current | Phase 1 Target | Phase 2 Target |
|--------|---------|----------------|----------------|
| **Reproducibility** | ~55% | 70% | 80% |
| **Validation coverage** | 0% | 80% | 95% |
| **Automated checks** | 0 | 9 | 15+ |
| **Code-based processing** | 20% | 35% | 50% |
| **Failed output rate** | Unknown | <10% | <5% |

---

## File Checklist

### Phase 1 (Create)
- [ ] `scripts/validate_summary.py`
- [ ] `scripts/validate_yaml.py`
- [ ] `schemas/summary_output.yaml`

### Phase 2 (Create)
- [ ] `scripts/extract_statistics.py`
- [ ] `scripts/detect_article_type.py`
- [ ] `scripts/update_markers.py`

### Phase 3 (Update)
- [ ] Update subagent prompts with structured output tags
- [ ] Update SKILL.md with validation workflow
- [ ] Add pre-flight checks to orchestration logic

---

## Appendix: Regex Pattern Reference

### Statistics Patterns

| Type | Pattern | Example Match |
|------|---------|---------------|
| P-value | `p\s*[<=]\s*0?\.\d+` | p = 0.003, p < 0.05 |
| CI | `\d+%\s*CI:\s*[\d.]+[–-][\d.]+` | 95% CI: 1.2–3.4 |
| Sample size | `n\s*=\s*\d+` | n = 24 |
| Fold change | `\d+\.?\d*-fold` | 2.3-fold |
| Hazard ratio | `HR\s*=\s*[\d.]+` | HR = 0.45 |
| Odds ratio | `OR\s*=\s*[\d.]+` | OR = 2.3 |

### Figure Reference Patterns

| Type | Pattern | Example Match |
|------|---------|---------------|
| Figure | `Figure\s+\d+[A-Z]?` | Figure 1, Figure 2A |
| Fig abbreviation | `Fig\.?\s+\d+[A-Z]?` | Fig. 3B, Fig 4 |
| Table | `Table\s+\d+` | Table 1 |
| Supplementary | `Supplementary\s+(Figure|Table)\s+\d+` | Supplementary Figure 1 |

### Section Marker Patterns

| Purpose | Pattern |
|---------|---------|
| Find all markers | `<!-- (SECTION\|SUBSECTION): (\w+) (PENDING\|COMPLETE\|SKIPPED) -->` |
| Find pending | `<!-- SECTION: \w+ PENDING -->` |
| Update specific | `<!-- SECTION: {name} PENDING -->` |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-07 | Initial audit completed |
