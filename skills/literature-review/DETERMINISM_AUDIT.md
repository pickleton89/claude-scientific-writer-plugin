# Literature Review Skill - Determinism Audit

> **Audit Date:** 2026-01-08
> **Skill Version:** 2.2.0
> **Development Stage:** First Draft Skill
> **Current Determinism Score:** ~75%
> **Target Determinism Score:** ~90%

---

## Executive Summary

The literature-review skill is remarkably well-structured with excellent reference documentation, explicit numerical thresholds, decision matrices, and two working Python scripts (verify_citations.py, generate_pdf.py). The remaining variance stems from unvalidated inputs (research questions, criteria), unstandardized intermediate outputs (screening decisions, quality ratings), and subjective processes (theme identification). Implementing input validation schemas and adding 2-3 helper scripts would significantly improve reproducibility.

---

## Determinism Scorecard

| Component | Current | Target | Gap |
|-----------|---------|--------|-----|
| Input validation | 50% | 90% | No schema validation for PICO/PEO/SPIDER |
| Database selection | 60% | 95% | Decision matrix exists but not enforced |
| Search execution | 80% | 90% | Scripts available, syntax validation missing |
| PRISMA documentation | 70% | 95% | Templates exist, no number validation |
| Quality assessment | 60% | 85% | Tool selection clear, rating calculation manual |
| Citation verification | 95% | 98% | Excellent script, edge cases possible |
| PDF generation | 95% | 98% | Deterministic via pandoc |
| **Overall** | **75%** | **90%** | |

---

## Strengths (Deterministic Components)

### 1. Citation Verification Script (95% deterministic)
- `verify_citations.py` extracts DOIs via regex
- CrossRef API provides standardized metadata
- Structured JSON output report
- APA/Nature formatting functions

### 2. PDF Generation Script (95% deterministic)
- `generate_pdf.py` wraps pandoc with consistent options
- Dependency checking included
- BibTeX citation processing
- Reproducible output format

### 3. Explicit Numerical Thresholds
```
Systematic review: ≥3 databases, 30+ papers
Search saturation: <5% new papers in final iteration
Screening time: ≤15s title, ≤2min abstract
Inter-rater agreement: κ ≥0.8
```

### 4. Structured Templates
- PRISMA flow diagram with placeholders
- Data extraction form with 15+ defined fields
- Search documentation template
- Thematic synthesis template

### 5. Decision Matrices
- Database Selection Matrix (domain → databases)
- Quality Assessment Tool Selection (study design → tool)
- Review Type Selection (factors → type)
- Synthesis Approach Selection (data type → approach)

---

## Stochastic Components & Recommendations

### Issue 1: Research Question Validation (P0)

**Current State:** PICO/PEO/SPIDER frameworks described but not validated.

**Impact:** Same topic could be framed differently, affecting search strategy.

**Solution:** Create JSON schemas for structured research questions.

```python
# scripts/research_question.py
from dataclasses import dataclass
from typing import Literal

@dataclass
class PICOQuestion:
    """PICO format for clinical/intervention research questions."""
    population: str
    intervention: str
    comparison: str
    outcome: str

    def to_search_terms(self) -> dict:
        """Generate database-agnostic search term groups."""
        return {
            "population": self.population.split(", "),
            "intervention": self.intervention.split(", "),
            "comparison": self.comparison.split(", "),
            "outcome": self.outcome.split(", ")
        }

    def validate(self) -> list[str]:
        """Return list of validation errors."""
        errors = []
        if len(self.population) < 5:
            errors.append("Population too brief - be specific")
        if not self.outcome:
            errors.append("Outcome required for PICO questions")
        return errors

@dataclass
class PEOQuestion:
    """PEO format for observational/exposure research questions."""
    population: str
    exposure: str
    outcome: str

@dataclass
class SPIDERQuestion:
    """SPIDER format for qualitative research questions."""
    sample: str
    phenomenon: str
    design: Literal["phenomenological", "ethnographic", "grounded theory", "case study", "narrative"]
    evaluation: str
    research_type: Literal["qualitative", "mixed"]
```

### Issue 2: PRISMA Flow Number Validation (P0)

**Current State:** Template has placeholders but no consistency checking.

**Impact:** Arithmetic errors in flow diagrams undermine review credibility.

**Solution:** Create PRISMA validator script.

```python
# scripts/prisma_validator.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class PRISMAFlowData:
    """PRISMA 2020 flow diagram data with validation."""

    # Identification
    databases: dict[str, int]  # database name -> count
    other_sources: dict[str, int]  # source name -> count

    # Pre-screening removal
    duplicates_removed: int
    automation_excluded: int = 0

    # Screening
    records_screened: int
    records_excluded: int

    # Retrieval
    reports_sought: int
    reports_not_retrieved: int

    # Eligibility
    reports_assessed: int
    reports_excluded: int
    exclusion_reasons: dict[str, int]  # reason -> count

    # Included
    studies_included: int
    studies_in_meta: Optional[int] = None

    def validate(self) -> list[str]:
        """Validate PRISMA flow numbers are consistent."""
        errors = []

        # Total identified
        total_db = sum(self.databases.values())
        total_other = sum(self.other_sources.values())
        total_identified = total_db + total_other

        # After deduplication
        after_dedup = total_identified - self.duplicates_removed - self.automation_excluded
        if self.records_screened != after_dedup:
            errors.append(
                f"Records screened ({self.records_screened}) should equal "
                f"total identified ({total_identified}) minus removed ({self.duplicates_removed + self.automation_excluded}) = {after_dedup}"
            )

        # After title/abstract screening
        after_screening = self.records_screened - self.records_excluded
        if self.reports_sought != after_screening:
            errors.append(
                f"Reports sought ({self.reports_sought}) should equal "
                f"screened ({self.records_screened}) minus excluded ({self.records_excluded}) = {after_screening}"
            )

        # After retrieval
        after_retrieval = self.reports_sought - self.reports_not_retrieved
        if self.reports_assessed != after_retrieval:
            errors.append(
                f"Reports assessed ({self.reports_assessed}) should equal "
                f"sought ({self.reports_sought}) minus not retrieved ({self.reports_not_retrieved}) = {after_retrieval}"
            )

        # Exclusion reasons sum
        reasons_sum = sum(self.exclusion_reasons.values())
        if reasons_sum != self.reports_excluded:
            errors.append(
                f"Exclusion reasons sum ({reasons_sum}) should equal "
                f"reports excluded ({self.reports_excluded})"
            )

        # After full-text exclusion
        after_ft = self.reports_assessed - self.reports_excluded
        if self.studies_included != after_ft:
            errors.append(
                f"Studies included ({self.studies_included}) should equal "
                f"assessed ({self.reports_assessed}) minus excluded ({self.reports_excluded}) = {after_ft}"
            )

        return errors

    def generate_diagram(self) -> str:
        """Generate text-based PRISMA flow diagram."""
        # Returns formatted PRISMA diagram with validated numbers
        pass
```

### Issue 3: Quality Assessment Standardization (P1)

**Current State:** Tool selection is clear, but rating calculation is manual.

**Impact:** Inter-rater variability in quality ratings.

**Solution:** Create quality scorer with tool-specific logic.

```python
# scripts/quality_scorer.py
from dataclasses import dataclass
from typing import Literal

Rating = Literal["Low", "Some concerns", "High"]
OverallRating = Literal["Low", "Moderate", "High", "Very Low"]

TOOL_DOMAINS = {
    "RoB2": ["randomization", "deviations", "missing_data", "measurement", "selection"],
    "NOS_cohort": ["selection", "comparability", "outcome"],
    "NOS_case_control": ["selection", "comparability", "exposure"],
    "QUADAS2": ["patient_selection", "index_test", "reference_standard", "flow_timing"],
    "CASP": ["aims", "methodology", "design", "recruitment", "data_collection",
             "ethics", "analysis", "findings", "value"],
    "AMSTAR2": ["protocol", "search", "exclusions", "rob_tool", "meta_methods",
                "rob_interpretation", "publication_bias"]
}

@dataclass
class QualityAssessment:
    """Structured quality assessment result."""
    tool: str
    study_id: str
    domain_ratings: dict[str, Rating]
    support: dict[str, str]  # domain -> rationale

    def calculate_overall(self) -> OverallRating:
        """Calculate overall rating from domain ratings."""
        high_count = sum(1 for r in self.domain_ratings.values() if r == "High")
        concerns_count = sum(1 for r in self.domain_ratings.values() if r == "Some concerns")

        if high_count >= 3:
            return "Very Low"
        elif high_count >= 2:
            return "Low"
        elif high_count == 1:
            return "Moderate"
        elif concerns_count >= 3:
            return "Moderate"
        return "High"

    def validate(self) -> list[str]:
        """Validate assessment completeness."""
        errors = []
        expected_domains = TOOL_DOMAINS.get(self.tool, [])

        for domain in expected_domains:
            if domain not in self.domain_ratings:
                errors.append(f"Missing rating for domain: {domain}")
            if domain not in self.support:
                errors.append(f"Missing rationale for domain: {domain}")

        return errors

def select_quality_tool(study_design: str) -> str:
    """Deterministically select quality assessment tool from study design."""
    design_map = {
        "rct": "RoB2",
        "randomized controlled trial": "RoB2",
        "cohort": "NOS_cohort",
        "case-control": "NOS_case_control",
        "cross-sectional": "JBI_cross_sectional",
        "diagnostic": "QUADAS2",
        "qualitative": "CASP",
        "systematic review": "AMSTAR2",
        "meta-analysis": "AMSTAR2"
    }
    return design_map.get(study_design.lower(), "NOS_cohort")
```

### Issue 4: Database Selection Automation (P1)

**Current State:** Decision matrix exists in decision_frameworks.md but not enforced.

**Solution:** Create database selector function.

```python
# scripts/database_selector.py

DATABASE_MATRIX = {
    "biomedical": {
        "clinical": ["PubMed", "Cochrane", "CINAHL", "Embase"],
        "basic_biology": ["PubMed", "bioRxiv", "Web of Science"],
        "genomics": ["PubMed", "bioRxiv", "GEO", "UniProt"]
    },
    "physical_sciences": {
        "physics": ["arXiv", "Web of Science", "ADS"],
        "chemistry": ["PubMed", "SciFinder", "Web of Science"],
        "engineering": ["IEEE Xplore", "Scopus", "Web of Science"]
    },
    "computer_science": {
        "ml_ai": ["arXiv", "Semantic Scholar", "ACM DL", "IEEE"],
        "general": ["ACM DL", "IEEE Xplore", "arXiv", "DBLP"]
    },
    "social_sciences": {
        "psychology": ["PsycINFO", "Scopus", "SSRN"],
        "general": ["SSRN", "Scopus", "Web of Science"]
    },
    "multidisciplinary": {
        "default": ["Semantic Scholar", "Web of Science", "Scopus", "Google Scholar"]
    }
}

REVIEW_MINIMUMS = {
    "systematic": 3,
    "scoping": 2,
    "narrative": 2,
    "rapid": 2
}

def select_databases(
    domain: str,
    subdomain: str = "default",
    review_type: str = "systematic"
) -> dict:
    """
    Select databases based on domain and review type.

    Returns:
        dict with 'required', 'recommended', and 'optional' database lists
    """
    domain_dbs = DATABASE_MATRIX.get(domain, DATABASE_MATRIX["multidisciplinary"])
    subdomain_dbs = domain_dbs.get(subdomain, domain_dbs.get("default", []))

    minimum = REVIEW_MINIMUMS.get(review_type, 3)

    return {
        "required": subdomain_dbs[:minimum],
        "recommended": subdomain_dbs[minimum:minimum+2] if len(subdomain_dbs) > minimum else [],
        "optional": subdomain_dbs[minimum+2:] if len(subdomain_dbs) > minimum+2 else [],
        "minimum_required": minimum,
        "preprint_required": review_type in ["systematic", "scoping"]
    }
```

### Issue 5: Review Configuration Preflight (P1)

**Current State:** No validation before starting review.

**Solution:** Create preflight validator.

```python
# scripts/review_config.py
import json
from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional

@dataclass
class ReviewConfig:
    """Validated review configuration."""
    title: str
    review_type: str  # systematic, scoping, narrative, rapid
    research_question: dict  # PICO, PEO, or SPIDER format
    domain: str
    subdomain: Optional[str]
    date_range: tuple[date, date]
    inclusion_criteria: list[dict]  # [{criterion, rationale}]
    exclusion_criteria: list[dict]
    databases: list[str]

    def validate(self) -> list[str]:
        """Validate configuration completeness and consistency."""
        errors = []

        # Review type validation
        valid_types = ["systematic", "scoping", "narrative", "rapid"]
        if self.review_type not in valid_types:
            errors.append(f"Invalid review type: {self.review_type}")

        # Database minimum check
        minimums = {"systematic": 3, "scoping": 2, "narrative": 2, "rapid": 2}
        required = minimums.get(self.review_type, 2)
        if len(self.databases) < required:
            errors.append(f"{self.review_type} review requires ≥{required} databases")

        # Date range validation
        if self.date_range[1] < self.date_range[0]:
            errors.append("End date must be after start date")

        # Criteria validation
        if not self.inclusion_criteria:
            errors.append("At least one inclusion criterion required")
        if not self.exclusion_criteria:
            errors.append("At least one exclusion criterion required")

        return errors

    def to_json(self, path: str):
        """Save validated config to JSON."""
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)

def preflight_check(config: ReviewConfig) -> dict:
    """Run all preflight validations."""
    return {
        "config_valid": len(config.validate()) == 0,
        "config_errors": config.validate(),
        "database_coverage": check_database_coverage(config),
        "date_range_appropriate": check_date_range(config),
        "criteria_specificity": check_criteria_specificity(config)
    }
```

---

## Implementation Roadmap

### Phase 1: Critical Validation (P0)
**Target: +10% determinism**

| Task | Effort | Impact |
|------|--------|--------|
| Create `prisma_validator.py` | 2h | Catches arithmetic errors |
| Add PICO/PEO/SPIDER schemas | 2h | Standardizes input |
| Add preflight validation | 1h | Catches config issues |

### Phase 2: Quality & Selection (P1)
**Target: +5% determinism**

| Task | Effort | Impact |
|------|--------|--------|
| Create `quality_scorer.py` | 3h | Standardizes assessment |
| Create `database_selector.py` | 1h | Enforces decision matrix |
| Add `review_config.py` | 2h | Validates all inputs |

### Phase 3: Tracking & Polish (P2)
**Target: +3% determinism**

| Task | Effort | Impact |
|------|--------|--------|
| Create screening tracker format | 2h | Audit trail |
| Add search syntax validators | 3h | Per-database validation |
| Add exit criteria checker | 1h | Stage completion validation |

---

## Success Metrics

| Metric | Current | After P0 | After P1 | After P2 |
|--------|---------|----------|----------|----------|
| Input validation coverage | 50% | 80% | 90% | 95% |
| PRISMA accuracy | 70% | 95% | 95% | 98% |
| Quality assessment consistency | 60% | 75% | 90% | 90% |
| Overall determinism | 75% | 85% | 90% | 93% |

---

## Files to Create/Modify

### New Files
- `scripts/prisma_validator.py` - PRISMA flow validation
- `scripts/quality_scorer.py` - Quality assessment standardization
- `scripts/database_selector.py` - Algorithmic database selection
- `scripts/review_config.py` - Configuration validation
- `scripts/research_question.py` - PICO/PEO/SPIDER schemas

### Existing Files to Enhance
- `scripts/verify_citations.py` - Add batch processing, edge case handling
- `scripts/generate_pdf.py` - Add template selection by review type

---

## Appendix: Detection Patterns

### Research Question Pattern Detection
```python
def detect_question_type(text: str) -> str:
    """Detect PICO/PEO/SPIDER from question text."""
    text_lower = text.lower()

    if "intervention" in text_lower or "treatment" in text_lower:
        return "PICO"
    elif "exposure" in text_lower or "risk factor" in text_lower:
        return "PEO"
    elif "qualitative" in text_lower or "experience" in text_lower:
        return "SPIDER"

    return "PICO"  # Default
```

### Study Design Pattern Detection
```python
DESIGN_PATTERNS = {
    r"random(ized|ised)": "rct",
    r"cohort": "cohort",
    r"case.?control": "case-control",
    r"cross.?sectional": "cross-sectional",
    r"systematic review": "systematic review",
    r"meta.?analysis": "meta-analysis",
    r"qualitative": "qualitative"
}
```
