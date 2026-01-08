# Scientific Writing Skill: Determinism Audit

> Audit Date: 2026-01-07
> Skill Version: 2.4.0
> Development Stage: First Draft Skill

## Executive Summary

The scientific-writing skill is well-structured with approximately **40% deterministic components** (three Python validation scripts, explicit thresholds, and lookup tables) but has significant opportunities to increase determinism to **~70%**. The primary improvements involve converting prose-based decision guidance into structured decision trees, expanding validation scripts to cover IMRAD structure and field terminology, and creating JSON-based lookup tables for journal requirements and reporting guideline selection.

**Key Findings:**
- Three working Python scripts provide consistent quality metrics (sentence length, readability, citation counts)
- Citation style and reporting guideline selection currently require LLM judgment but are ideal candidates for lookup tables
- IMRAD structure validation is missing but straightforward to implement
- Expected improvement: 40% → 70% deterministic (30% variance reduction)

---

## Current State Analysis

### Deterministic Components (~40%)

| Component | Implementation | Location |
|-----------|---------------|----------|
| Sentence length analysis | Regex-based parsing | `scripts/validate_writing_quality.py` |
| Paragraph length analysis | Word count per paragraph | `scripts/validate_writing_quality.py` |
| Passive voice detection | Regex pattern matching | `scripts/validate_writing_quality.py` |
| Readability scores | Mathematical formulas (FK, Fog, SMOG) | `scripts/readability_score.py` |
| Citation counting | Regex extraction by style | `scripts/count_citations.py` |
| Citation style detection | Pattern matching | `scripts/count_citations.py` |
| Section citation targets | Lookup table by document type | `scripts/count_citations.py` |
| Quality thresholds | Static values in code | All scripts |

### Stochastic Components (~60%)

| Component | Current State | Determinism Opportunity |
|-----------|--------------|------------------------|
| Citation style selection | Prose guidance in tables | HIGH - Lookup table |
| Reporting guideline selection | Prose guidance | HIGH - Decision tree |
| IMRAD structure validation | Not implemented | HIGH - Regex-based |
| Journal-specific requirements | Scattered in prose | HIGH - JSON database |
| Field terminology validation | Reference doc only | MEDIUM - Pattern matching |
| Tense consistency checking | Prose guidelines | MEDIUM - Per-section regex |
| Section proportion calculation | Static tables | MEDIUM - Calculator function |
| Pre-submission checklists | Prose lists | MEDIUM - Template generator |
| Figure/table count validation | Prose rules | LOW - Simple arithmetic |
| Writing style assessment | Prose guidelines | LOW - Inherently subjective |

---

## Input Standardization

### Current State

- Inputs are largely free-form (document type mentioned in prose, journal selection implicit)
- Some structure exists: validation scripts accept file paths with optional section flags
- Document types mentioned: "original_research," "review_article" (in citation targets)
- No explicit input schemas for LLM-facing instructions

### Recommendations

#### 1. JSON Schema for Manuscript Metadata

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ManuscriptMetadata",
  "type": "object",
  "required": ["document_type", "target_venue"],
  "properties": {
    "document_type": {
      "type": "string",
      "enum": ["original_research", "review_article", "case_report", "meta_analysis", "protocol", "methods_paper"]
    },
    "target_venue": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "type": {"type": "string", "enum": ["journal", "ml_conference", "broad_impact"]},
        "field": {"type": "string", "enum": ["biomedical", "chemistry", "physics", "ecology", "neuroscience", "ml", "social_science"]}
      },
      "required": ["name"]
    },
    "study_design": {
      "type": "string",
      "enum": ["rct", "cohort", "case_control", "cross_sectional", "systematic_review", "meta_analysis", "case_report", "qualitative"]
    },
    "word_count_target": {"type": "integer", "minimum": 1000, "maximum": 15000},
    "sections_included": {
      "type": "array",
      "items": {"type": "string", "enum": ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]}
    }
  }
}
```

#### 2. Study Design Enum (Python)

```python
from enum import Enum

class StudyDesign(Enum):
    RCT = "rct"
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    CASE_REPORT = "case_report"
    QUALITATIVE = "qualitative"
    METHODS_PAPER = "methods_paper"
```

#### 3. Structured Venue Database

Create `data/venues.json`:

```json
{
  "nature": {
    "citation_style": "nature_numbered",
    "methods_placement": "supplement",
    "word_limit": 4500,
    "structured_abstract": false,
    "reporting_guidelines": ["appropriate_to_study"]
  },
  "nejm": {
    "citation_style": "vancouver",
    "methods_placement": "main_text",
    "word_limit": 2700,
    "structured_abstract": true,
    "reporting_guidelines": ["consort", "strobe"]
  },
  "neurips": {
    "citation_style": "numbered_brackets",
    "page_limit": 8,
    "requires_code": true,
    "contribution_list": true,
    "reporting_guidelines": []
  },
  "jama": {
    "citation_style": "ama",
    "word_limit": 3500,
    "structured_abstract": true,
    "reporting_guidelines": ["consort", "strobe", "prisma"]
  }
}
```

---

## Output Standardization

### Current State

- Validation scripts output structured JSON with pass/fail status (good)
- Main skill outputs are prose guidance (inherently variable)
- Section templates exist in prose but not as structured outputs

### Recommendations

#### 1. Standardized Validation Report

```python
from dataclasses import dataclass
from typing import Literal
from datetime import datetime

@dataclass
class CheckResult:
    status: Literal["EXCELLENT", "TARGET", "ACCEPTABLE", "FAIL"]
    value: float | str
    threshold: str
    details: str | None = None

@dataclass
class ManuscriptQualityReport:
    overall_status: Literal["PASS", "NEEDS_REVISION", "FAIL"]
    checks: dict[str, CheckResult]
    recommendations: list[str]
    metrics: dict[str, float]
    timestamp: str

    def to_json(self) -> str:
        import json
        return json.dumps(self.__dict__, default=str, indent=2)
```

#### 2. Pre-Submission Checklist Output

```python
@dataclass
class ChecklistItem:
    category: str
    item: str
    status: Literal["checked", "unchecked", "not_applicable"]
    notes: str | None = None

@dataclass
class PreSubmissionChecklist:
    venue_requirements: list[ChecklistItem]
    reporting_guideline_items: list[ChecklistItem]
    formatting_requirements: list[ChecklistItem]
    statistics_requirements: list[ChecklistItem]

    def completion_rate(self) -> float:
        all_items = (self.venue_requirements + self.reporting_guideline_items +
                     self.formatting_requirements + self.statistics_requirements)
        checked = sum(1 for item in all_items if item.status == "checked")
        applicable = sum(1 for item in all_items if item.status != "not_applicable")
        return checked / applicable if applicable > 0 else 0.0
```

---

## Implementation Plan

### Phase 1: Decision Trees → Code (HIGH PRIORITY)

**Goal:** Convert prose-based decisions to deterministic lookups

#### 1.1 Reporting Guideline Selector

Create `scripts/select_guideline.py`:

```python
#!/usr/bin/env python3
"""Select appropriate reporting guideline based on study design."""

from enum import Enum
import json
import sys

class StudyDesign(Enum):
    RCT = "rct"
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    CASE_REPORT = "case_report"
    QUALITATIVE = "qualitative"
    DIAGNOSTIC_ACCURACY = "diagnostic_accuracy"
    PREDICTION_MODEL = "prediction_model"
    ANIMAL_STUDY = "animal_study"
    QI_STUDY = "quality_improvement"
    ECONOMIC_EVALUATION = "economic_evaluation"

GUIDELINE_MAP = {
    StudyDesign.RCT: {
        "primary": "CONSORT",
        "url": "http://www.consort-statement.org/",
        "items": 25,
        "extensions": ["cluster", "non-inferiority", "pragmatic", "pilot"]
    },
    StudyDesign.COHORT: {
        "primary": "STROBE",
        "url": "https://www.strobe-statement.org/",
        "items": 22,
        "extensions": ["molecular_epidemiology", "routinely_collected_data"]
    },
    StudyDesign.CASE_CONTROL: {
        "primary": "STROBE",
        "url": "https://www.strobe-statement.org/",
        "items": 22,
        "extensions": []
    },
    StudyDesign.CROSS_SECTIONAL: {
        "primary": "STROBE",
        "url": "https://www.strobe-statement.org/",
        "items": 22,
        "extensions": []
    },
    StudyDesign.SYSTEMATIC_REVIEW: {
        "primary": "PRISMA",
        "url": "http://www.prisma-statement.org/",
        "items": 27,
        "extensions": ["protocols", "network_meta", "scoping", "IPD", "DTA"]
    },
    StudyDesign.META_ANALYSIS: {
        "primary": "PRISMA",
        "url": "http://www.prisma-statement.org/",
        "items": 27,
        "extensions": []
    },
    StudyDesign.CASE_REPORT: {
        "primary": "CARE",
        "url": "https://www.care-statement.org/",
        "items": 13,
        "extensions": []
    },
    StudyDesign.QUALITATIVE: {
        "primary": "SRQR",
        "url": "https://www.equator-network.org/reporting-guidelines/srqr/",
        "items": 21,
        "extensions": ["COREQ"]
    },
    StudyDesign.DIAGNOSTIC_ACCURACY: {
        "primary": "STARD",
        "url": "https://www.equator-network.org/reporting-guidelines/stard/",
        "items": 30,
        "extensions": []
    },
    StudyDesign.PREDICTION_MODEL: {
        "primary": "TRIPOD",
        "url": "https://www.tripod-statement.org/",
        "items": 22,
        "extensions": []
    },
    StudyDesign.ANIMAL_STUDY: {
        "primary": "ARRIVE",
        "url": "https://arriveguidelines.org/",
        "items": 10,
        "extensions": ["ARRIVE_2.0"]
    },
    StudyDesign.QI_STUDY: {
        "primary": "SQUIRE",
        "url": "http://www.squire-statement.org/",
        "items": 18,
        "extensions": []
    },
    StudyDesign.ECONOMIC_EVALUATION: {
        "primary": "CHEERS",
        "url": "https://www.equator-network.org/reporting-guidelines/cheers/",
        "items": 28,
        "extensions": []
    },
}

def select_guideline(study_design: str) -> dict:
    """Select reporting guideline for a given study design."""
    try:
        design = StudyDesign(study_design.lower())
    except ValueError:
        return {
            "error": f"Unknown study design: {study_design}",
            "valid_options": [d.value for d in StudyDesign]
        }

    guideline = GUIDELINE_MAP[design]
    return {
        "study_design": design.value,
        "guideline": guideline["primary"],
        "url": guideline["url"],
        "checklist_items": guideline["items"],
        "available_extensions": guideline["extensions"],
        "equator_search": f"https://www.equator-network.org/?s={guideline['primary']}"
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python select_guideline.py <study_design>")
        print(f"Valid designs: {[d.value for d in StudyDesign]}")
        sys.exit(1)

    result = select_guideline(sys.argv[1])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

#### 1.2 Citation Style Selector

Create `scripts/select_citation_style.py`:

```python
#!/usr/bin/env python3
"""Select citation style based on target journal or field."""

import json
import sys
from difflib import get_close_matches

# Journal -> Citation Style mapping
JOURNAL_STYLES = {
    # Medical journals
    "jama": "ama",
    "jama network": "ama",
    "nejm": "vancouver",
    "new england journal of medicine": "vancouver",
    "lancet": "vancouver",
    "bmj": "vancouver",
    "annals of internal medicine": "ama",

    # Life sciences
    "nature": "nature_numbered",
    "nature medicine": "nature_numbered",
    "nature communications": "nature_numbered",
    "science": "science_numbered",
    "cell": "cell_author_date",
    "cell reports": "cell_author_date",
    "plos one": "vancouver",
    "plos biology": "vancouver",
    "elife": "vancouver",

    # Psychology/Social sciences
    "psychological bulletin": "apa",
    "psychological review": "apa",
    "journal of personality and social psychology": "apa",
    "developmental psychology": "apa",

    # Engineering/CS
    "ieee transactions": "ieee",
    "acm computing surveys": "acm",

    # Chemistry
    "jacs": "acs",
    "journal of the american chemical society": "acs",
    "angewandte chemie": "acs",

    # ML Conferences
    "neurips": "numbered_brackets",
    "icml": "numbered_brackets",
    "iclr": "numbered_brackets",
    "cvpr": "ieee",
    "iccv": "ieee",
    "acl": "acl_author_year",
    "emnlp": "acl_author_year",
}

# Field -> Default style mapping
FIELD_DEFAULTS = {
    "medicine": "vancouver",
    "biomedical": "vancouver",
    "psychology": "apa",
    "social_science": "apa",
    "engineering": "ieee",
    "computer_science": "ieee",
    "chemistry": "acs",
    "physics": "aps",
    "ecology": "cse",
    "ml": "numbered_brackets",
}

STYLE_DESCRIPTIONS = {
    "ama": "Superscript numbers, AMA Manual of Style 11th ed",
    "vancouver": "Numbered brackets [1], ICMJE recommendations",
    "apa": "Author-date (Smith, 2023), APA 7th edition",
    "nature_numbered": "Superscript numbers, abbreviated format",
    "ieee": "Numbered brackets [1], IEEE style",
    "acs": "Superscript or numbered, ACS style",
    "chicago": "Notes-bibliography or author-date",
    "cell_author_date": "Author-date with specific Cell formatting",
    "numbered_brackets": "Generic numbered [1] style for conferences",
    "acl_author_year": "ACL-style author-year citations",
}

def select_citation_style(journal_or_field: str) -> dict:
    """Select citation style for a given journal or field."""
    normalized = journal_or_field.lower().strip()

    # Try exact journal match first
    if normalized in JOURNAL_STYLES:
        style = JOURNAL_STYLES[normalized]
        return {
            "input": journal_or_field,
            "match_type": "exact_journal",
            "style": style,
            "description": STYLE_DESCRIPTIONS.get(style, ""),
        }

    # Try fuzzy journal match
    close_matches = get_close_matches(normalized, JOURNAL_STYLES.keys(), n=1, cutoff=0.6)
    if close_matches:
        matched_journal = close_matches[0]
        style = JOURNAL_STYLES[matched_journal]
        return {
            "input": journal_or_field,
            "match_type": "fuzzy_journal",
            "matched_to": matched_journal,
            "style": style,
            "description": STYLE_DESCRIPTIONS.get(style, ""),
        }

    # Try field match
    if normalized in FIELD_DEFAULTS:
        style = FIELD_DEFAULTS[normalized]
        return {
            "input": journal_or_field,
            "match_type": "field_default",
            "style": style,
            "description": STYLE_DESCRIPTIONS.get(style, ""),
            "note": "Based on field default; check specific journal guidelines"
        }

    # Default fallback
    return {
        "input": journal_or_field,
        "match_type": "default",
        "style": "vancouver",
        "description": STYLE_DESCRIPTIONS["vancouver"],
        "note": "No match found; defaulting to Vancouver (most common in science)",
        "available_journals": list(JOURNAL_STYLES.keys())[:20],
        "available_fields": list(FIELD_DEFAULTS.keys()),
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python select_citation_style.py <journal_name_or_field>")
        sys.exit(1)

    result = select_citation_style(" ".join(sys.argv[1:]))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

### Phase 2: Structure Validation Scripts (HIGH PRIORITY)

#### 2.1 IMRAD Structure Validator

Create `scripts/validate_structure.py`:

```python
#!/usr/bin/env python3
"""Validate IMRAD structure in scientific manuscripts."""

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, asdict

IMRAD_SECTIONS = ["abstract", "introduction", "methods", "results", "discussion"]

SECTION_PATTERNS = {
    "abstract": r"(?i)^#+\s*abstract",
    "introduction": r"(?i)^#+\s*(introduction|background)",
    "methods": r"(?i)^#+\s*(methods?|materials?\s+and\s+methods?|methodology|experimental)",
    "results": r"(?i)^#+\s*(results?|findings)",
    "discussion": r"(?i)^#+\s*discussion",
    "conclusion": r"(?i)^#+\s*(conclusion|conclusions|summary)",
    "references": r"(?i)^#+\s*(references?|bibliography|literature\s+cited)",
    "acknowledgments": r"(?i)^#+\s*(acknowledgments?|acknowledgements?)",
}

# Tense patterns by section (simplified)
TENSE_PATTERNS = {
    "methods": {
        "preferred": r"\b(was|were|used|measured|collected|analyzed|performed)\b",
        "name": "past"
    },
    "results": {
        "preferred": r"\b(was|were|showed|found|observed|demonstrated|indicated)\b",
        "name": "past"
    },
    "discussion": {
        "preferred": r"\b(suggests?|indicates?|demonstrates?|shows?|implies?)\b",
        "name": "present"
    },
}

@dataclass
class StructureValidation:
    found_sections: list[str]
    missing_sections: list[str]
    section_order_correct: bool
    extra_sections: list[str]
    status: str
    recommendations: list[str]

def find_sections(text: str) -> dict[str, int]:
    """Find all sections and their line numbers."""
    sections = {}
    lines = text.split("\n")

    for i, line in enumerate(lines):
        for section_name, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, line):
                if section_name not in sections:  # First occurrence
                    sections[section_name] = i

    return sections

def validate_imrad_structure(text: str) -> StructureValidation:
    """Validate IMRAD structure in manuscript."""
    found = find_sections(text)
    found_names = list(found.keys())

    # Check for required sections
    missing = [s for s in IMRAD_SECTIONS if s not in found_names]

    # Check order (only for sections that are present)
    present_imrad = [s for s in IMRAD_SECTIONS if s in found_names]
    found_imrad = [s for s in found_names if s in IMRAD_SECTIONS]
    order_correct = present_imrad == found_imrad

    # Identify extra sections (not in standard IMRAD)
    extra = [s for s in found_names if s not in IMRAD_SECTIONS]

    # Generate recommendations
    recommendations = []
    if missing:
        recommendations.append(f"Add missing sections: {', '.join(missing)}")
    if not order_correct:
        recommendations.append(f"Reorder sections to follow IMRAD: {' → '.join(IMRAD_SECTIONS)}")
    if "conclusion" not in found_names and "discussion" in found_names:
        recommendations.append("Consider adding a Conclusion section (or include in Discussion)")

    # Determine status
    if not missing and order_correct:
        status = "PASS"
    elif len(missing) <= 1 and order_correct:
        status = "ACCEPTABLE"
    else:
        status = "FAIL"

    return StructureValidation(
        found_sections=found_names,
        missing_sections=missing,
        section_order_correct=order_correct,
        extra_sections=extra,
        status=status,
        recommendations=recommendations
    )

def main():
    parser = argparse.ArgumentParser(description="Validate IMRAD structure")
    parser.add_argument("input_file", help="Path to manuscript file")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    text = Path(args.input_file).read_text(encoding="utf-8")
    result = validate_imrad_structure(text)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print("=" * 60)
        print("IMRAD STRUCTURE VALIDATION")
        print("=" * 60)
        print(f"\nStatus: {result.status}")
        print(f"\nFound sections: {', '.join(result.found_sections)}")
        if result.missing_sections:
            print(f"Missing sections: {', '.join(result.missing_sections)}")
        print(f"Section order correct: {'Yes' if result.section_order_correct else 'No'}")
        if result.extra_sections:
            print(f"Additional sections: {', '.join(result.extra_sections)}")
        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")

    sys.exit(0 if result.status in ["PASS", "ACCEPTABLE"] else 1)

if __name__ == "__main__":
    main()
```

### Phase 3: Section Targets Calculator (MEDIUM PRIORITY)

Create `scripts/calculate_targets.py`:

```python
#!/usr/bin/env python3
"""Calculate section-specific word count and citation targets."""

import argparse
import json
import sys

# Word count proportions by document length
WORD_COUNT_PROPORTIONS = {
    "abstract": {"min": 0.03, "max": 0.05},
    "introduction": {"min": 0.12, "max": 0.18},
    "methods": {"min": 0.18, "max": 0.28},
    "results": {"min": 0.20, "max": 0.30},
    "discussion": {"min": 0.20, "max": 0.30},
    "conclusion": {"min": 0.03, "max": 0.05},
}

# Citation targets by document type
CITATION_TARGETS = {
    "original_research": {
        "introduction": {"min": 8, "max": 15},
        "methods": {"min": 3, "max": 8},
        "results": {"min": 0, "max": 3},
        "discussion": {"min": 10, "max": 20},
        "total": {"min": 30},
    },
    "review_article": {
        "introduction": {"min": 15, "max": 30},
        "methods": {"min": 5, "max": 10},
        "discussion": {"min": 30, "max": 60},
        "total": {"min": 100},
    },
    "case_report": {
        "introduction": {"min": 5, "max": 10},
        "case_presentation": {"min": 0, "max": 2},
        "discussion": {"min": 8, "max": 15},
        "total": {"min": 15},
    },
}

def calculate_section_words(total_words: int) -> dict:
    """Calculate word count targets for each section."""
    targets = {}
    for section, proportions in WORD_COUNT_PROPORTIONS.items():
        targets[section] = {
            "min": int(total_words * proportions["min"]),
            "max": int(total_words * proportions["max"]),
            "target": int(total_words * (proportions["min"] + proportions["max"]) / 2),
        }
    return targets

def calculate_citation_targets(document_type: str) -> dict:
    """Get citation targets for document type."""
    if document_type not in CITATION_TARGETS:
        return {
            "error": f"Unknown document type: {document_type}",
            "valid_types": list(CITATION_TARGETS.keys())
        }
    return CITATION_TARGETS[document_type]

def calculate_display_items(total_words: int) -> dict:
    """Calculate recommended number of figures/tables."""
    # Rule: ~1 display item per 1000 words
    recommended = max(3, total_words // 1000)
    return {
        "minimum": max(2, recommended - 2),
        "recommended": recommended,
        "maximum": recommended + 3,
        "rule": "Approximately 1 figure/table per 1000 words"
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate manuscript targets")
    parser.add_argument("--words", "-w", type=int, required=True, help="Target total word count")
    parser.add_argument("--type", "-t", default="original_research",
                        choices=list(CITATION_TARGETS.keys()),
                        help="Document type")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = {
        "total_words": args.words,
        "document_type": args.type,
        "section_word_counts": calculate_section_words(args.words),
        "citation_targets": calculate_citation_targets(args.type),
        "display_items": calculate_display_items(args.words),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=" * 60)
        print(f"MANUSCRIPT TARGETS ({args.words} words, {args.type})")
        print("=" * 60)

        print("\nSection Word Counts:")
        for section, counts in result["section_word_counts"].items():
            print(f"  {section.title()}: {counts['min']}-{counts['max']} words (target: {counts['target']})")

        print("\nCitation Targets:")
        for section, targets in result["citation_targets"].items():
            if "min" in targets:
                max_str = f"-{targets['max']}" if "max" in targets else "+"
                print(f"  {section.title()}: {targets['min']}{max_str} citations")

        print(f"\nFigures/Tables: {result['display_items']['minimum']}-{result['display_items']['maximum']} "
              f"(recommended: {result['display_items']['recommended']})")

if __name__ == "__main__":
    main()
```

### Phase 4: Data Files (MEDIUM PRIORITY)

#### 4.1 Journal Requirements Database

Create `data/journal_requirements.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "venues": {
    "nature": {
      "citation_style": "nature_numbered",
      "word_limit": 4500,
      "abstract_limit": 150,
      "methods_placement": "supplement",
      "structured_abstract": false,
      "figures_limit": 6,
      "references_limit": 50,
      "reporting_guidelines": "study_appropriate"
    },
    "science": {
      "citation_style": "science_numbered",
      "word_limit": 4500,
      "abstract_limit": 125,
      "methods_placement": "supplement",
      "structured_abstract": false,
      "figures_limit": 4,
      "references_limit": 40
    },
    "nejm": {
      "citation_style": "vancouver",
      "word_limit": 2700,
      "abstract_limit": 250,
      "methods_placement": "main_text",
      "structured_abstract": true,
      "figures_limit": 5,
      "reporting_guidelines": ["consort", "strobe"]
    },
    "jama": {
      "citation_style": "ama",
      "word_limit": 3500,
      "abstract_limit": 350,
      "methods_placement": "main_text",
      "structured_abstract": true,
      "reporting_guidelines": ["consort", "strobe", "prisma"]
    },
    "lancet": {
      "citation_style": "vancouver",
      "word_limit": 3500,
      "abstract_limit": 300,
      "structured_abstract": true,
      "reporting_guidelines": ["consort", "strobe"]
    },
    "plos_one": {
      "citation_style": "vancouver",
      "word_limit": null,
      "abstract_limit": 300,
      "structured_abstract": false,
      "open_access": true,
      "reporting_guidelines": "required_for_study_type"
    },
    "neurips": {
      "citation_style": "numbered_brackets",
      "page_limit": 8,
      "abstract_limit": 200,
      "requires_code": true,
      "contribution_list": true,
      "venue_type": "ml_conference"
    },
    "icml": {
      "citation_style": "numbered_brackets",
      "page_limit": 8,
      "abstract_limit": 200,
      "requires_code": true,
      "venue_type": "ml_conference"
    }
  }
}
```

---

## Success Metrics

### Quantitative Targets

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Deterministic decision coverage | ~40% | ~70% | (Lookup + validation) / total decisions |
| Reporting guideline selection variance | High | Zero | Same study type → same guideline |
| Citation style selection variance | High | Zero | Same journal → same style |
| Structure validation coverage | 0% | 100% | Scripts validate all IMRAD sections |
| Section target calculation variance | Medium | Zero | Same inputs → same outputs |

### Qualitative Improvements

1. **Reproducibility**: Same manuscript metadata → same targets and recommendations
2. **Maintainability**: Lookup tables easier to update than prose
3. **Testability**: All new scripts can be unit tested with pytest
4. **User Experience**: Faster, more consistent guidance

---

## Testing Infrastructure

### pytest Structure

```
skills/scientific-writing/
├── tests/
│   ├── __init__.py
│   ├── test_select_guideline.py
│   ├── test_select_citation_style.py
│   ├── test_validate_structure.py
│   ├── test_calculate_targets.py
│   └── fixtures/
│       ├── sample_manuscript.md
│       └── imrad_variants.md
```

### Example Test Cases

```python
# test_select_guideline.py
import pytest
from scripts.select_guideline import select_guideline

@pytest.mark.parametrize("study_design,expected_guideline", [
    ("rct", "CONSORT"),
    ("cohort", "STROBE"),
    ("case_control", "STROBE"),
    ("systematic_review", "PRISMA"),
    ("case_report", "CARE"),
    ("qualitative", "SRQR"),
])
def test_guideline_selection(study_design, expected_guideline):
    result = select_guideline(study_design)
    assert result["guideline"] == expected_guideline

def test_unknown_study_design():
    result = select_guideline("unknown_type")
    assert "error" in result
    assert "valid_options" in result
```

---

## File Structure After Implementation

```
skills/scientific-writing/
├── SKILL.md                          # Main skill documentation
├── DETERMINISM_AUDIT.md              # This document
├── scripts/
│   ├── validate_writing_quality.py   # Existing (enhanced)
│   ├── readability_score.py          # Existing
│   ├── count_citations.py            # Existing (enhanced)
│   ├── select_guideline.py           # NEW: Study design → guideline
│   ├── select_citation_style.py      # NEW: Journal → citation style
│   ├── validate_structure.py         # NEW: IMRAD validation
│   └── calculate_targets.py          # NEW: Section targets
├── data/
│   └── journal_requirements.json     # NEW: Venue specifications
├── references/
│   ├── imrad_structure.md
│   ├── citation_styles.md
│   ├── figures_tables.md
│   ├── reporting_guidelines.md
│   ├── writing_principles.md
│   ├── field_terminology.md
│   └── writing_process.md
└── tests/
    ├── test_select_guideline.py
    ├── test_select_citation_style.py
    ├── test_validate_structure.py
    └── fixtures/
```

---

## Priority Matrix

| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| Reporting guideline selector | HIGH | LOW | **P0** |
| Citation style selector | HIGH | LOW | **P0** |
| IMRAD structure validator | HIGH | MEDIUM | **P1** |
| Journal requirements database | HIGH | MEDIUM | **P1** |
| Section targets calculator | MEDIUM | LOW | **P2** |
| Field terminology validator | MEDIUM | HIGH | **P3** |
| Tense consistency checker | LOW | MEDIUM | **P3** |

---

## Summary

The scientific-writing skill has a solid foundation with three working Python validation scripts. The primary opportunity is converting prose-based decision guidance (reporting guidelines, citation styles, journal requirements) into deterministic lookup tables and decision trees.

**Recommended immediate actions:**
1. Create `scripts/select_guideline.py` (~100 lines)
2. Create `scripts/select_citation_style.py` (~100 lines)
3. Create `scripts/validate_structure.py` (~80 lines)
4. Create `data/journal_requirements.json` (structured venue data)

**Expected outcome:** 40% → 70% deterministic, with zero variance on guideline selection, citation style selection, and structure validation.
