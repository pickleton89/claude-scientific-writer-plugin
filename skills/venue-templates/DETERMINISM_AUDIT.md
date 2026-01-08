# Venue-Templates Skill: Determinism Audit

> **Audit Date**: 2026-01-07
> **Skill Version**: 2.2.0
> **Status**: First Draft Skill
> **Auditor**: Claude Opus 4.5

---

## Executive Summary

The venue-templates skill has a strong foundation with existing Python scripts and comprehensive documentation, but suffers from **data fragmentation** (venue specs duplicated across Python dicts and markdown files) and **over-reliance on prose-based style guidance** that requires LLM interpretation. Key opportunities include consolidating all venue data into a single JSON source, creating deterministic style compliance validators, and converting prose style guides into structured, validatable formats.

**Current Determinism Score**: ~40%
**Target Determinism Score**: ~75%
**Expected Variance Reduction**: 50-60%

---

## Current Architecture Analysis

### What's Already Deterministic

| Component | Location | Determinism Level |
|-----------|----------|-------------------|
| Page count validation | `validate_format.py` | High |
| Font detection | `validate_format.py` (pdffonts) | High |
| Template file serving | `assets/` directory | High |
| Venue requirements dict | `validate_format.py:VENUE_REQUIREMENTS` | High |
| Template database | `query_template.py:TEMPLATES` | High |
| Template customization | `customize_template.py` | Medium |

### What's Currently Stochastic

| Component | Current Approach | Issue |
|-----------|-----------------|-------|
| Venue name resolution | LLM interprets user input | "Nature paper" vs "nature" vs "Nature journal" |
| Style guide application | Prose-based guidance | LLM must synthesize actionable advice |
| Venue type classification | Implicit from context | No formal classifier |
| Writing style compliance | Advisory prose only | No code validators |
| Template selection | LLM reasoning | No decision tree |
| Abstract format guidance | Prose descriptions | No structured validation |

### Data Fragmentation Problem

Venue requirements currently exist in **three locations**:

1. **Python scripts**: `VENUE_REQUIREMENTS` dict in `validate_format.py`, `TEMPLATES` dict in `query_template.py`
2. **Reference markdown**: `journals_formatting.md`, `conferences_formatting.md`, etc.
3. **Style guides**: `venue_writing_styles.md`, `nature_science_style.md`, etc.

**Risk**: Data drift between sources leads to inconsistent advice.

---

## Implementation Plan

### Phase 1: Unified Venue Database (High Priority)

**Goal**: Single source of truth for all venue specifications.

#### 1.1 Venue Schema Design

Create `data/venues.json` with comprehensive schema:

```json
{
  "$schema": "./venue_schema.json",
  "venues": {
    "nature": {
      "id": "nature",
      "full_name": "Nature",
      "publisher": "Nature Publishing Group",
      "type": "journal",
      "discipline": "multidisciplinary",
      "impact_tier": "high",
      "aliases": ["nature journal", "nature paper", "nature publishing"],

      "formatting": {
        "page_limit": null,
        "word_limit": 3000,
        "word_limit_scope": "excluding_methods_refs",
        "format": "single-column",
        "font_size": 12,
        "font_family": "Times",
        "margins_cm": {"top": 2.5, "bottom": 2.5, "left": 2.5, "right": 2.5},
        "line_spacing": "double",
        "citation_style": "superscript",
        "reference_format": "nature"
      },

      "abstract": {
        "style": "flowing",
        "max_words": 200,
        "structured_sections": null,
        "required_elements": ["significance", "key_finding", "implications"]
      },

      "style": {
        "tone": "accessible",
        "voice": "active",
        "first_person": true,
        "jargon_level": "minimal",
        "audience": "educated_non_specialist"
      },

      "requirements": {
        "anonymization": false,
        "graphical_abstract": false,
        "data_availability": true,
        "contribution_list": false,
        "ablation_studies": false
      },

      "templates": ["nature_article.tex"],
      "style_guides": ["nature_science_style.md"],
      "author_guidelines_url": "https://www.nature.com/nature/for-authors"
    }
  }
}
```

#### 1.2 JSON Schema for Validation

Create `data/venue_schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "venues": {
      "type": "object",
      "additionalProperties": {
        "$ref": "#/definitions/venue"
      }
    }
  },
  "definitions": {
    "venue": {
      "type": "object",
      "required": ["id", "full_name", "type", "formatting"],
      "properties": {
        "id": {"type": "string"},
        "full_name": {"type": "string"},
        "publisher": {"type": "string"},
        "type": {"enum": ["journal", "conference", "poster", "grant"]},
        "discipline": {"type": "string"},
        "impact_tier": {"enum": ["high", "medium", "standard"]},
        "aliases": {"type": "array", "items": {"type": "string"}},
        "formatting": {"$ref": "#/definitions/formatting"},
        "abstract": {"$ref": "#/definitions/abstract"},
        "style": {"$ref": "#/definitions/style"},
        "requirements": {"$ref": "#/definitions/requirements"}
      }
    },
    "formatting": {
      "type": "object",
      "properties": {
        "page_limit": {"type": ["integer", "null"]},
        "word_limit": {"type": ["integer", "null"]},
        "format": {"enum": ["single-column", "two-column"]},
        "font_size": {"type": "integer"},
        "citation_style": {"enum": ["superscript", "numbered", "author-year"]}
      }
    }
  }
}
```

#### 1.3 Python Data Access Layer

Create `scripts/venue_database.py`:

```python
#!/usr/bin/env python3
"""
Venue Database Access Layer
Single source of truth for all venue specifications.
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Literal

VENUES_PATH = Path(__file__).parent.parent / "data" / "venues.json"

@dataclass
class FormattingSpec:
    page_limit: Optional[int]
    word_limit: Optional[int]
    format: Literal["single-column", "two-column"]
    font_size: int
    font_family: str
    margins_cm: dict[str, float]
    line_spacing: str
    citation_style: Literal["superscript", "numbered", "author-year"]
    reference_format: str

@dataclass
class AbstractSpec:
    style: Literal["flowing", "structured"]
    max_words: int
    structured_sections: Optional[list[str]]
    required_elements: list[str]

@dataclass
class StyleSpec:
    tone: Literal["accessible", "technical", "formal"]
    voice: Literal["active", "passive", "mixed"]
    first_person: bool
    jargon_level: Literal["minimal", "moderate", "high"]
    audience: str

@dataclass
class RequirementsSpec:
    anonymization: bool
    graphical_abstract: bool
    data_availability: bool
    contribution_list: bool
    ablation_studies: bool

@dataclass
class VenueSpec:
    id: str
    full_name: str
    publisher: str
    type: Literal["journal", "conference", "poster", "grant"]
    discipline: str
    impact_tier: Literal["high", "medium", "standard"]
    aliases: list[str]
    formatting: FormattingSpec
    abstract: AbstractSpec
    style: StyleSpec
    requirements: RequirementsSpec
    templates: list[str]
    style_guides: list[str]
    author_guidelines_url: str

class VenueDatabase:
    """Access layer for venue specifications."""

    def __init__(self, path: Path = VENUES_PATH):
        with open(path) as f:
            self._data = json.load(f)
        self._build_alias_index()

    def _build_alias_index(self):
        """Build reverse index from aliases to venue IDs."""
        self._alias_index = {}
        for venue_id, venue in self._data["venues"].items():
            self._alias_index[venue_id.lower()] = venue_id
            for alias in venue.get("aliases", []):
                self._alias_index[alias.lower()] = venue_id

    def get(self, venue_id: str) -> Optional[VenueSpec]:
        """Get venue spec by ID."""
        if venue_id not in self._data["venues"]:
            return None
        return self._parse_venue(self._data["venues"][venue_id])

    def resolve(self, query: str) -> Optional[str]:
        """Resolve query string to venue ID."""
        normalized = query.lower().strip()
        return self._alias_index.get(normalized)

    def list_all(self) -> list[str]:
        """List all venue IDs."""
        return list(self._data["venues"].keys())

    def list_by_type(self, venue_type: str) -> list[str]:
        """List venues by type."""
        return [
            vid for vid, v in self._data["venues"].items()
            if v["type"] == venue_type
        ]

    def _parse_venue(self, data: dict) -> VenueSpec:
        """Parse venue dict into dataclass."""
        return VenueSpec(
            id=data["id"],
            full_name=data["full_name"],
            publisher=data.get("publisher", ""),
            type=data["type"],
            discipline=data.get("discipline", ""),
            impact_tier=data.get("impact_tier", "standard"),
            aliases=data.get("aliases", []),
            formatting=FormattingSpec(**data["formatting"]),
            abstract=AbstractSpec(**data.get("abstract", {})),
            style=StyleSpec(**data.get("style", {})),
            requirements=RequirementsSpec(**data.get("requirements", {})),
            templates=data.get("templates", []),
            style_guides=data.get("style_guides", []),
            author_guidelines_url=data.get("author_guidelines_url", "")
        )

# Singleton instance
_db: Optional[VenueDatabase] = None

def get_database() -> VenueDatabase:
    """Get singleton database instance."""
    global _db
    if _db is None:
        _db = VenueDatabase()
    return _db

def get_venue(venue_id: str) -> Optional[VenueSpec]:
    """Convenience function to get venue spec."""
    return get_database().get(venue_id)

def resolve_venue(query: str) -> Optional[str]:
    """Convenience function to resolve venue query."""
    return get_database().resolve(query)
```

---

### Phase 2: Venue Resolution with Fuzzy Matching (High Priority)

**Goal**: Deterministically resolve user queries to canonical venue IDs.

#### 2.1 Fuzzy Resolver Implementation

Create `scripts/venue_resolver.py`:

```python
#!/usr/bin/env python3
"""
Venue Resolver
Fuzzy matching to resolve user queries to canonical venue IDs.

Usage:
    python venue_resolver.py "Nature paper"
    python venue_resolver.py "neurips 2025" --threshold 0.7
"""

import argparse
import re
from dataclasses import dataclass
from typing import Optional
from difflib import SequenceMatcher

from venue_database import get_database, VenueDatabase

@dataclass
class ResolveResult:
    venue_id: Optional[str]
    confidence: float
    matched_alias: str
    alternatives: list[tuple[str, float]]  # (venue_id, score)

class VenueResolver:
    """Fuzzy venue name resolver."""

    def __init__(self, db: Optional[VenueDatabase] = None):
        self.db = db or get_database()
        self._build_search_index()

    def _build_search_index(self):
        """Build searchable index of venue names and aliases."""
        self._index = []  # (search_term, venue_id)

        for venue_id in self.db.list_all():
            venue = self.db.get(venue_id)
            if venue:
                # Add canonical ID
                self._index.append((venue_id.lower(), venue_id))
                # Add full name
                self._index.append((venue.full_name.lower(), venue_id))
                # Add all aliases
                for alias in venue.aliases:
                    self._index.append((alias.lower(), venue_id))

    def _normalize_query(self, query: str) -> str:
        """Normalize query for matching."""
        # Remove year suffixes (NeurIPS 2024 -> NeurIPS)
        query = re.sub(r'\s+20\d{2}$', '', query)
        # Lowercase and strip
        query = query.lower().strip()
        # Remove common words
        query = re.sub(r'\b(paper|article|journal|conference|grant|proposal)\b', '', query)
        # Collapse whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        return query

    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, a, b).ratio()

    def resolve(self, query: str, threshold: float = 0.6) -> ResolveResult:
        """
        Resolve query to venue ID.

        Args:
            query: User's venue query string
            threshold: Minimum confidence for a match (0-1)

        Returns:
            ResolveResult with venue_id, confidence, and alternatives
        """
        normalized = self._normalize_query(query)

        # Exact match first
        for term, venue_id in self._index:
            if term == normalized:
                return ResolveResult(
                    venue_id=venue_id,
                    confidence=1.0,
                    matched_alias=term,
                    alternatives=[]
                )

        # Fuzzy match
        scores = []
        for term, venue_id in self._index:
            score = self._similarity(normalized, term)
            scores.append((venue_id, term, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[2], reverse=True)

        # Deduplicate by venue_id, keeping highest score
        seen = set()
        unique_scores = []
        for venue_id, term, score in scores:
            if venue_id not in seen:
                seen.add(venue_id)
                unique_scores.append((venue_id, term, score))

        if not unique_scores:
            return ResolveResult(
                venue_id=None,
                confidence=0.0,
                matched_alias="",
                alternatives=[]
            )

        best = unique_scores[0]
        alternatives = [(vid, score) for vid, _, score in unique_scores[1:5]]

        if best[2] >= threshold:
            return ResolveResult(
                venue_id=best[0],
                confidence=best[2],
                matched_alias=best[1],
                alternatives=alternatives
            )
        else:
            return ResolveResult(
                venue_id=None,
                confidence=best[2],
                matched_alias=best[1],
                alternatives=[(best[0], best[2])] + alternatives
            )

def resolve_venue(query: str, threshold: float = 0.6) -> ResolveResult:
    """Convenience function for venue resolution."""
    resolver = VenueResolver()
    return resolver.resolve(query, threshold)

def main():
    parser = argparse.ArgumentParser(description="Resolve venue queries")
    parser.add_argument("query", help="Venue query string")
    parser.add_argument("--threshold", type=float, default=0.6,
                       help="Minimum confidence threshold (0-1)")
    args = parser.parse_args()

    result = resolve_venue(args.query, args.threshold)

    if result.venue_id:
        print(f"Resolved: {result.venue_id}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Matched: '{result.matched_alias}'")
    else:
        print(f"No match found (best score: {result.confidence:.2f})")
        if result.alternatives:
            print("\nDid you mean:")
            for vid, score in result.alternatives[:3]:
                print(f"  - {vid} ({score:.2f})")

if __name__ == "__main__":
    main()
```

---

### Phase 3: Enhanced Validation (High Priority)

**Goal**: Expand `validate_format.py` with additional deterministic checks.

#### 3.1 Extended Validation Checks

Add to `scripts/validate_format.py`:

```python
# Additional validation functions

def check_citation_format(text: str, venue_reqs: dict) -> dict:
    """Validate citation format matches venue requirements."""
    expected = venue_reqs.get("citation_style")
    if not expected:
        return {"status": "skip", "message": "No citation style specified"}

    patterns = {
        "superscript": r"[^0-9]\d{1,3}(?:,\s*\d{1,3})*[^0-9\]]",  # 1,2,3 not in brackets
        "numbered": r"\[\d{1,3}(?:,\s*\d{1,3})*\]",  # [1], [2,3]
        "author-year": r"\([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s*\d{4}[a-z]?\)"  # (Smith, 2023)
    }

    if expected not in patterns:
        return {"status": "skip", "message": f"Unknown citation style: {expected}"}

    pattern = patterns[expected]
    matches = re.findall(pattern, text)

    if len(matches) > 0:
        return {
            "status": "pass",
            "message": f"Found {len(matches)} citations matching {expected} style"
        }
    else:
        return {
            "status": "warn",
            "message": f"No citations found matching {expected} style (expected: {expected})"
        }

def check_abstract_structure(text: str, venue_reqs: dict) -> dict:
    """Check if abstract matches venue structure requirements."""
    abstract_spec = venue_reqs.get("abstract", {})
    style = abstract_spec.get("style")
    max_words = abstract_spec.get("max_words")

    results = []

    # Word count check
    if max_words:
        # Try to extract abstract (look for Abstract: or ABSTRACT section)
        abstract_match = re.search(
            r'(?:abstract|ABSTRACT)[:\s]*(.+?)(?=\n\n|\n[A-Z]{2,}|\nIntroduction|\nKeywords)',
            text, re.DOTALL | re.IGNORECASE
        )
        if abstract_match:
            abstract_text = abstract_match.group(1)
            word_count = len(abstract_text.split())
            if word_count > max_words:
                results.append(f"Abstract too long: {word_count}/{max_words} words")
            else:
                results.append(f"Abstract length OK: {word_count}/{max_words} words")

    # Structure check (for medical journals)
    if style == "structured":
        required_sections = abstract_spec.get("structured_sections",
            ["Background", "Methods", "Results", "Conclusions"])
        missing = []
        for section in required_sections:
            if not re.search(rf'\b{section}\b', text, re.IGNORECASE):
                missing.append(section)
        if missing:
            results.append(f"Missing abstract sections: {', '.join(missing)}")
        else:
            results.append("All required abstract sections present")

    if not results:
        return {"status": "skip", "message": "No abstract requirements to check"}

    has_issues = any("too long" in r or "Missing" in r for r in results)
    return {
        "status": "fail" if has_issues else "pass",
        "message": "\n".join(results)
    }

def check_anonymization(pdf_path: Path, venue_reqs: dict) -> dict:
    """Check if document is properly anonymized for double-blind review."""
    if not venue_reqs.get("requirements", {}).get("anonymization"):
        return {"status": "skip", "message": "Anonymization not required"}

    try:
        # Extract text from PDF
        result = subprocess.run(
            ['pdftotext', str(pdf_path), '-'],
            capture_output=True, text=True, check=True
        )
        text = result.stdout

        # Look for common anonymization violations
        violations = []

        # Author names in acknowledgments
        if re.search(r'acknowledge.*\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text, re.IGNORECASE):
            violations.append("Possible author name in acknowledgments")

        # Self-citations with "our previous work", "we previously"
        if re.search(r'\b(our previous|we previously|our earlier|in \[?\d+\]? we)\b', text, re.IGNORECASE):
            violations.append("Self-referential language detected")

        # GitHub/institution URLs
        if re.search(r'github\.com/[a-zA-Z0-9_-]+', text):
            violations.append("GitHub URL may reveal identity")

        if violations:
            return {
                "status": "warn",
                "message": "Potential anonymization issues:\n" + "\n".join(f"  - {v}" for v in violations)
            }
        else:
            return {"status": "pass", "message": "No obvious anonymization issues detected"}

    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"status": "skip", "message": "Could not extract text for anonymization check"}

def check_contribution_list(text: str, venue_reqs: dict) -> dict:
    """Check for contribution list (required for ML conferences)."""
    if not venue_reqs.get("requirements", {}).get("contribution_list"):
        return {"status": "skip", "message": "Contribution list not required"}

    # Look for numbered/bulleted contribution statements
    patterns = [
        r'(?:our|the)\s+contributions?\s+(?:are|include)[:\s]',
        r'we\s+(?:make|present)\s+the\s+following\s+contributions?',
        r'contributions?[:\s]*\n\s*[\•\-\d]',
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return {
                "status": "pass",
                "message": "Contribution list found in introduction"
            }

    return {
        "status": "warn",
        "message": "No contribution list found (typically required for ML conferences)"
    }
```

---

### Phase 4: Style Compliance Checker (Medium Priority)

**Goal**: Deterministic validation of writing style compliance.

#### 4.1 Style Checker Implementation

Create `scripts/check_style.py`:

```python
#!/usr/bin/env python3
"""
Style Compliance Checker
Validate document style against venue requirements.

Usage:
    python check_style.py --file paper.tex --venue nature
    python check_style.py --file paper.pdf --venue neurips --check-all
"""

import argparse
import re
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Literal

from venue_database import get_venue, VenueSpec

@dataclass
class StyleIssue:
    category: str
    severity: Literal["error", "warning", "info"]
    message: str
    location: str = ""
    suggestion: str = ""

class StyleChecker:
    """Check document style compliance."""

    def __init__(self, venue_spec: VenueSpec):
        self.spec = venue_spec

    def check_all(self, text: str) -> list[StyleIssue]:
        """Run all style checks."""
        issues = []
        issues.extend(self.check_voice(text))
        issues.extend(self.check_jargon_level(text))
        issues.extend(self.check_abstract_style(text))
        issues.extend(self.check_contribution_format(text))
        issues.extend(self.check_hedging_language(text))
        return issues

    def check_voice(self, text: str) -> list[StyleIssue]:
        """Check active vs passive voice usage."""
        issues = []
        style = self.spec.style

        # Count passive constructions
        passive_patterns = [
            r'\b(?:is|are|was|were|been|being)\s+\w+ed\b',
            r'\b(?:is|are|was|were)\s+(?:shown|found|observed|demonstrated|reported)\b'
        ]
        passive_count = sum(len(re.findall(p, text)) for p in passive_patterns)

        # Count active first-person
        active_patterns = [r'\bwe\s+(?:show|find|demonstrate|report|present|propose)\b']
        active_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in active_patterns)

        total = passive_count + active_count
        if total == 0:
            return issues

        passive_ratio = passive_count / total

        if style.voice == "active" and passive_ratio > 0.6:
            issues.append(StyleIssue(
                category="voice",
                severity="warning",
                message=f"High passive voice usage ({passive_ratio:.0%}) - {self.spec.full_name} prefers active voice",
                suggestion="Consider rewriting passive constructions with 'we show/find/demonstrate'"
            ))
        elif style.voice == "passive" and passive_ratio < 0.4:
            issues.append(StyleIssue(
                category="voice",
                severity="info",
                message=f"Low passive voice usage ({passive_ratio:.0%}) - {self.spec.full_name} traditionally uses passive voice",
                suggestion="Consider using passive constructions for formal tone"
            ))

        return issues

    def check_jargon_level(self, text: str) -> list[StyleIssue]:
        """Check jargon usage against venue expectations."""
        issues = []
        style = self.spec.style

        # Technical jargon indicators
        jargon_patterns = [
            r'\b[A-Z]{3,}\b',  # Acronyms
            r'\b\w+(?:ization|isation)\b',  # -ization words
            r'\b(?:utilized|leveraged|paradigm|synergy)\b',  # Buzzwords
        ]

        jargon_count = sum(len(re.findall(p, text)) for p in jargon_patterns)
        word_count = len(text.split())
        jargon_density = jargon_count / word_count if word_count > 0 else 0

        if style.jargon_level == "minimal" and jargon_density > 0.02:
            issues.append(StyleIssue(
                category="jargon",
                severity="warning",
                message=f"High jargon density ({jargon_density:.1%}) for {self.spec.full_name}",
                suggestion="Define acronyms on first use; prefer common words over technical terms"
            ))

        return issues

    def check_abstract_style(self, text: str) -> list[StyleIssue]:
        """Check abstract format and content."""
        issues = []
        abstract_spec = self.spec.abstract

        # Extract abstract
        abstract_match = re.search(
            r'(?:abstract|ABSTRACT)[:\s]*(.+?)(?=\n\n|\n[A-Z]{2,}|\nIntroduction|\n1\s)',
            text, re.DOTALL | re.IGNORECASE
        )

        if not abstract_match:
            issues.append(StyleIssue(
                category="abstract",
                severity="info",
                message="Could not locate abstract for analysis"
            ))
            return issues

        abstract_text = abstract_match.group(1).strip()
        word_count = len(abstract_text.split())

        # Word count
        if abstract_spec.max_words and word_count > abstract_spec.max_words:
            issues.append(StyleIssue(
                category="abstract",
                severity="error",
                message=f"Abstract too long: {word_count} words (max: {abstract_spec.max_words})",
                suggestion=f"Reduce abstract by {word_count - abstract_spec.max_words} words"
            ))

        # Structure check
        if abstract_spec.style == "structured":
            sections = abstract_spec.structured_sections or ["Background", "Methods", "Results", "Conclusions"]
            missing = [s for s in sections if not re.search(rf'\b{s}\b', abstract_text, re.IGNORECASE)]
            if missing:
                issues.append(StyleIssue(
                    category="abstract",
                    severity="error",
                    message=f"Missing structured abstract sections: {', '.join(missing)}",
                    suggestion=f"{self.spec.full_name} requires structured abstract with labeled sections"
                ))

        return issues

    def check_contribution_format(self, text: str) -> list[StyleIssue]:
        """Check for proper contribution statement (ML conferences)."""
        issues = []

        if not self.spec.requirements.contribution_list:
            return issues

        # Look for contribution list patterns
        contrib_patterns = [
            r'contributions?\s*(?:are|include)[:\s]*\n\s*[\•\-\d\*]',
            r'we\s+(?:make|present)\s+the\s+following\s+contributions?',
            r'our\s+(?:main\s+)?contributions?\s*:',
        ]

        found = any(re.search(p, text, re.IGNORECASE) for p in contrib_patterns)

        if not found:
            issues.append(StyleIssue(
                category="structure",
                severity="warning",
                message="No numbered/bulleted contribution list found",
                suggestion=f"{self.spec.full_name} papers typically include explicit contribution bullets in the introduction"
            ))

        return issues

    def check_hedging_language(self, text: str) -> list[StyleIssue]:
        """Check appropriate hedging for claim strength."""
        issues = []

        # Strong causal claims
        strong_claims = re.findall(
            r'\b(?:causes?|proves?|confirms?|establishes?)\s+that\b',
            text, re.IGNORECASE
        )

        if self.spec.type == "journal" and self.spec.discipline == "medical":
            # Medical journals require careful hedging
            if strong_claims:
                issues.append(StyleIssue(
                    category="language",
                    severity="warning",
                    message=f"Found {len(strong_claims)} strong causal claims",
                    suggestion="Medical journals prefer 'is associated with' over 'causes' for observational data"
                ))

        return issues

def extract_text(file_path: Path) -> str:
    """Extract text from PDF or read LaTeX directly."""
    if file_path.suffix.lower() == '.pdf':
        result = subprocess.run(
            ['pdftotext', str(file_path), '-'],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    else:
        return file_path.read_text()

def main():
    parser = argparse.ArgumentParser(description="Check style compliance")
    parser.add_argument("--file", required=True, help="Document to check")
    parser.add_argument("--venue", required=True, help="Target venue")
    parser.add_argument("--check-all", action="store_true", help="Run all checks")
    args = parser.parse_args()

    venue_spec = get_venue(args.venue)
    if not venue_spec:
        print(f"Unknown venue: {args.venue}")
        return

    text = extract_text(Path(args.file))
    checker = StyleChecker(venue_spec)
    issues = checker.check_all(text)

    if not issues:
        print(f"No style issues found for {venue_spec.full_name}")
        return

    print(f"\nStyle Check Results for {venue_spec.full_name}")
    print("=" * 60)

    for issue in issues:
        icon = {"error": "", "warning": "", "info": ""}[issue.severity]
        print(f"\n{icon} [{issue.category.upper()}] {issue.message}")
        if issue.suggestion:
            print(f"   Suggestion: {issue.suggestion}")

if __name__ == "__main__":
    main()
```

---

### Phase 5: Style Rules as Structured Data (Medium Priority)

**Goal**: Convert prose style guidance to validatable YAML rules.

#### 5.1 Style Rules Schema

Create `data/style_rules.yaml`:

```yaml
# Style rules that can be programmatically validated
# Complements (not replaces) prose style guides

nature:
  abstract:
    style: flowing
    max_words: 200
    prohibited_patterns:
      - pattern: "state-of-the-art"
        message: "Avoid clichés like 'state-of-the-art'"
      - pattern: "novel"
        message: "Nature discourages overuse of 'novel'"
    required_elements:
      - broad_significance
      - key_finding

  introduction:
    max_paragraphs: 4
    first_paragraph:
      purpose: "Hook with broad significance"
      patterns_expected:
        - "fundamental question"
        - "longstanding challenge"
        - "critical importance"
    last_paragraph:
      purpose: "Preview of findings"
      patterns_expected:
        - "Here we show"
        - "We demonstrate"

  voice:
    active_preferred: true
    first_person: true
    examples:
      good: "We discovered that protein X controls..."
      bad: "It was discovered that protein X controls..."

  figures:
    conceptual_schematics: required
    raw_data_emphasis: low

neurips:
  abstract:
    style: flowing
    numbers_upfront: true
    required_elements:
      - method_name
      - key_metrics
      - benchmark_names

  introduction:
    contribution_list:
      required: true
      format: bulleted
      typical_count: [3, 4]
      patterns:
        - "We propose"
        - "We provide theoretical"
        - "We demonstrate"
        - "We release"

  experiments:
    required_sections:
      - baselines
      - main_results
      - ablation_studies
    tables:
      bold_best: true
      include_std: recommended

medical:
  abstract:
    style: structured
    sections:
      - Background
      - Methods
      - Results
      - Conclusions
    max_words: 300

  language:
    evidence_hedging:
      rct: "reduced", "prevented", "caused"
      observational: "was associated with", "may reduce"
      case_series: "suggests that", "may be"
    patient_centered: true
    examples:
      good: "Patients receiving treatment X..."
      bad: "Treatment X subjects..."

  reporting:
    absolute_numbers: required
    confidence_intervals: required
    nnt_arr: recommended
```

---

## Testing Infrastructure

### Test Cases for Validation Scripts

Create `tests/test_venue_resolver.py`:

```python
import pytest
from scripts.venue_resolver import VenueResolver, resolve_venue

class TestVenueResolver:
    def test_exact_match(self):
        result = resolve_venue("nature")
        assert result.venue_id == "nature"
        assert result.confidence == 1.0

    def test_alias_match(self):
        result = resolve_venue("NeurIPS 2024")
        assert result.venue_id == "neurips"
        assert result.confidence >= 0.8

    def test_fuzzy_match(self):
        result = resolve_venue("natur")  # Typo
        assert result.venue_id == "nature"
        assert 0.7 <= result.confidence < 1.0

    def test_no_match(self):
        result = resolve_venue("xyzzy journal")
        assert result.venue_id is None
        assert result.confidence < 0.6

    def test_case_insensitive(self):
        result = resolve_venue("NATURE")
        assert result.venue_id == "nature"

class TestStyleChecker:
    def test_abstract_word_count(self):
        # Test with abstract over limit
        pass

    def test_contribution_list_detection(self):
        # Test ML conference contribution format
        pass

    def test_passive_voice_detection(self):
        # Test voice analysis
        pass
```

---

## Migration Guide

### Updating Existing Scripts

1. **validate_format.py**:
   - Import `get_venue` from `venue_database`
   - Replace `VENUE_REQUIREMENTS` dict with database lookups
   - Add new validation checks

2. **query_template.py**:
   - Import from `venue_database`
   - Replace `TEMPLATES` dict with database queries
   - Add fuzzy search capability

3. **customize_template.py**:
   - No major changes needed
   - Consider using Jinja2 for template rendering

### Generating Markdown from Database

Create `scripts/generate_docs.py` to generate reference markdown from `venues.json`:

```python
#!/usr/bin/env python3
"""Generate reference documentation from venue database."""

from venue_database import get_database

def generate_quick_reference():
    db = get_database()
    lines = ["# Quick Reference Table\n"]
    lines.append("| Venue | Max Length | Format | Citations | Template |")
    lines.append("|-------|-----------|--------|-----------|----------|")

    for venue_id in sorted(db.list_all()):
        v = db.get(venue_id)
        length = v.formatting.word_limit or v.formatting.page_limit or "Variable"
        lines.append(
            f"| **{v.full_name}** | {length} | {v.formatting.format} | "
            f"{v.formatting.citation_style} | `{v.templates[0] if v.templates else 'N/A'}` |"
        )

    return "\n".join(lines)
```

---

## Implementation Priority Matrix

| Phase | Component | Impact | Effort | Dependencies |
|-------|-----------|--------|--------|--------------|
| 1 | `venues.json` schema | High | Medium | None |
| 1 | `venue_database.py` | High | Low | venues.json |
| 2 | `venue_resolver.py` | High | Low | venue_database |
| 3 | Extended validation | High | Medium | venue_database |
| 4 | `check_style.py` | Medium | Medium | venue_database |
| 5 | `style_rules.yaml` | Medium | High | check_style.py |
| - | Test suite | Medium | Low | All scripts |
| - | Doc generation | Low | Low | venue_database |

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Venue resolution accuracy | ~70% (LLM) | 95%+ | Test suite with 100+ queries |
| Style check coverage | 0 checks | 8+ checks | Count of implemented validators |
| Data consistency | 3 sources | 1 source | venues.json as single source |
| Validation coverage | 3 checks | 10+ checks | validate_format.py checks |
| Test coverage | 0% | 80%+ | pytest coverage report |

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-07 | Initial determinism audit | Claude Opus 4.5 |

---

*This document should be updated as implementation progresses.*
