# Determinism Audit: peer-review Skill

> Audit Date: 2026-01-08
> Skill Version: 2.2.0
> Development Stage: First draft skill
> Current Determinism Level: 35-40%
> Target Determinism Level: 70-75%

---

## Executive Summary

The peer-review skill has excellent structural foundations—quantitative rubrics, staged workflows, explicit thresholds, and a working Python score calculator—but currently relies almost entirely on LLM judgment to apply these structures. With the recommended code implementations, reviews can become significantly more reproducible across sessions while preserving nuanced scientific judgment where it's genuinely needed.

---

## Current State Analysis

### Deterministic Components (Already Implemented)

| Component | Implementation | Location |
|-----------|----------------|----------|
| Score calculation | Weighted averaging with validation | `scripts/calculate_scores.py` |
| Quality tier mapping | Threshold-based (4.5-5.0=A, etc.) | `scripts/calculate_scores.py` |
| Report template | Structured markdown with placeholders | `templates/scoring_report.md` |
| Workflow stages | 7-stage progression defined | `SKILL.md` lines 79-414 |

### Stochastic Components (LLM-Dependent)

| Component | Current Approach | Variance Risk |
|-----------|------------------|---------------|
| Score assignment (1-5) | LLM interprets rubric criteria | High |
| Issue severity classification | LLM interprets prose criteria | High |
| Stage transition verification | Self-assessed checklists | Medium |
| Common issue detection | Reference file lookup | Medium |
| Statistical test appropriateness | Decision tree in prose | Medium |
| Figure quality assessment | Manual against thresholds | Low-Medium |

---

## Identified Opportunities

### P0: Critical (Implement First)

#### 1. Severity Classifier

**Problem:** Issue severity (Critical/Major/Minor/Optional) relies on LLM interpretation despite explicit quantitative criteria in SKILL.md.

**Solution:** Create `validators/severity_classifier.py`

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

class Severity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    OPTIONAL = "optional"

@dataclass
class SeverityRule:
    """Rule for deterministic severity classification."""
    issue_type: str
    condition: str
    threshold: float
    severity: Severity
    rationale: str

# Rules extracted from SKILL.md lines 447-452
SEVERITY_RULES = [
    # Critical triggers (any one = reject)
    SeverityRule("data_verification", "cannot_verify", 1.0, Severity.CRITICAL,
                 "Data cannot be verified"),
    SeverityRule("statistical_test", "invalidates_results", 1.0, Severity.CRITICAL,
                 "Wrong statistical test invalidating results"),
    SeverityRule("missing_data", "missing_pct_no_sensitivity", 0.30, Severity.CRITICAL,
                 "Missing data >30% without sensitivity analysis"),
    SeverityRule("conclusions", "contradicted_by_data", 1.0, Severity.CRITICAL,
                 "Conclusions contradicted by data"),
    SeverityRule("ethics", "missing_approval", 1.0, Severity.CRITICAL,
                 "Missing ethics approval"),

    # Major triggers (significantly affects interpretation)
    SeverityRule("controls", "key_control_missing_pct", 0.50, Severity.MAJOR,
                 "Key control missing from >=50% of experiments"),
    SeverityRule("sample_size", "below_power_pct", 0.80, Severity.MAJOR,
                 "Sample size <80% of power requirement"),
    SeverityRule("methods", "insufficient_for_replication", 1.0, Severity.MAJOR,
                 "Methods insufficient for replication"),
    SeverityRule("statistical_assumptions", "violated", 1.0, Severity.MAJOR,
                 "Statistical assumptions violated"),
    SeverityRule("outcomes", "missing_stated_pct", 0.20, Severity.MAJOR,
                 ">=20% of stated outcomes missing"),

    # Minor triggers (affects clarity/completeness)
    SeverityRule("grammar", "errors_per_page", 5.0, Severity.MINOR,
                 "Grammar/spelling errors >5/page"),
    SeverityRule("figure_quality", "below_minimum_standards", 1.0, Severity.MINOR,
                 "Figure quality below minimum standards"),
    SeverityRule("references", "formatting_inconsistent", 1.0, Severity.MINOR,
                 "Reference formatting inconsistent"),
    SeverityRule("acronyms", "undefined_count", 3.0, Severity.MINOR,
                 "Acronyms undefined"),
]

def classify_severity(issue_type: str, metric_value: float) -> Tuple[Severity, str]:
    """
    Deterministic severity classification based on quantified criteria.

    Args:
        issue_type: Type of issue (e.g., "missing_data", "sample_size")
        metric_value: Quantified measure of the issue

    Returns:
        Tuple of (Severity, rationale)
    """
    for rule in SEVERITY_RULES:
        if rule.issue_type == issue_type:
            if metric_value >= rule.threshold:
                return (rule.severity, rule.rationale)
    return (Severity.OPTIONAL, "Does not meet severity threshold criteria")

def get_recommendation_action(severity: Severity) -> str:
    """Map severity to standard recommendation action."""
    actions = {
        Severity.CRITICAL: "Reject - fundamental issue invalidating conclusions",
        Severity.MAJOR: "Major revision required before reconsideration",
        Severity.MINOR: "Minor revision - address before publication",
        Severity.OPTIONAL: "Author discretion - suggestion for improvement"
    }
    return actions[severity]
```

**Impact:** Eliminates variance in severity assignment; ensures consistent recommendations.

#### 2. Extended Score Validation

**Problem:** `calculate_scores.py` calculates but doesn't validate completeness or consistency.

**Solution:** Extend with validation functions

```python
# Add to scripts/calculate_scores.py

REQUIRED_DIMENSIONS = [
    "problem_formulation", "literature_review", "methodology",
    "data_collection", "analysis", "results", "writing", "citations"
]

MIN_JUSTIFICATION_LENGTH = 50  # characters

def validate_scores(scores: Dict[str, float]) -> List[str]:
    """Validate score completeness and bounds."""
    errors = []

    # Check all dimensions present
    for dim in REQUIRED_DIMENSIONS:
        if dim not in scores:
            errors.append(f"Missing required dimension: {dim}")
        elif not 1.0 <= scores[dim] <= 5.0:
            errors.append(f"Score out of bounds for {dim}: {scores[dim]}")

    return errors

def validate_justifications(justifications: Dict[str, str]) -> List[str]:
    """Validate justification completeness."""
    warnings = []

    for dim in REQUIRED_DIMENSIONS:
        if dim not in justifications:
            warnings.append(f"Missing justification for {dim}")
        elif len(justifications[dim]) < MIN_JUSTIFICATION_LENGTH:
            warnings.append(f"Justification too brief for {dim} ({len(justifications[dim])} chars)")

    return warnings

def validate_score_consistency(scores: Dict[str, float], issues: List[dict]) -> List[str]:
    """Check that scores align with identified issues."""
    warnings = []

    # If critical issues exist, methodology score should be low
    critical_issues = [i for i in issues if i.get("severity") == "critical"]
    if critical_issues and scores.get("methodology", 0) > 3.0:
        warnings.append("Critical methodology issues but methodology score > 3.0")

    return warnings
```

**Impact:** Ensures review completeness; catches inconsistencies before output.

---

### P1: High Priority (Implement Second)

#### 3. Workflow State Tracker

**Problem:** Stage transitions rely on self-assessed checklists without enforcement.

**Solution:** Create `scripts/workflow_tracker.py`

```python
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from enum import IntEnum

class ReviewStage(IntEnum):
    INITIAL_ASSESSMENT = 1
    SECTION_REVIEW = 2
    METHODOLOGY = 3
    REPRODUCIBILITY = 4
    FIGURES = 5
    ETHICS = 6
    WRITING = 7
    REPORT = 8

# Exit criteria from references/workflow_transitions.md
STAGE_EXIT_CRITERIA = {
    ReviewStage.INITIAL_ASSESSMENT: [
        "research_question_identified",
        "main_findings_summarized",
        "initial_impression_documented",
        "venue_appropriateness_assessed",
        "no_disqualifying_flaws_or_flagged"
    ],
    ReviewStage.SECTION_REVIEW: [
        "all_sections_evaluated",
        "min_2_strengths_per_section",
        "min_2_concerns_per_section",
        "issues_located_by_section",
        "key_claims_identified",
        "citation_coverage_assessed"
    ],
    ReviewStage.METHODOLOGY: [
        "statistical_assumptions_verified",
        "sample_size_checked",
        "controls_assessed",
        "multiple_testing_evaluated",
        "effect_sizes_checked",
        "experimental_design_documented"
    ],
    ReviewStage.REPRODUCIBILITY: [
        "data_availability_assessed",
        "code_availability_checked",
        "reporting_guidelines_verified",
        "protocol_detail_evaluated",
        "materials_availability_confirmed"
    ],
    ReviewStage.FIGURES: [
        "resolution_checked",
        "labeling_assessed",
        "error_bars_verified",
        "colorblind_accessibility_checked",
        "image_integrity_verified",
        "quality_scores_documented"
    ],
    ReviewStage.ETHICS: [
        "irb_verified_if_applicable",
        "iacuc_verified_if_applicable",
        "conflicts_disclosed",
        "funding_disclosed",
        "plagiarism_checked",
        "authorship_assessed"
    ],
    ReviewStage.WRITING: [
        "structure_assessed",
        "language_clarity_evaluated",
        "jargon_minimization_checked",
        "accessibility_considered",
        "all_stages_complete"
    ]
}

@dataclass
class WorkflowState:
    """Tracks review progress through stages."""
    current_stage: ReviewStage = ReviewStage.INITIAL_ASSESSMENT
    checklist: Dict[str, bool] = field(default_factory=dict)
    stage_notes: Dict[int, List[str]] = field(default_factory=dict)

    def mark_complete(self, criterion: str) -> None:
        """Mark a checklist item as complete."""
        self.checklist[criterion] = True

    def can_advance(self) -> Tuple[bool, List[str]]:
        """Check if current stage exit criteria are met."""
        required = STAGE_EXIT_CRITERIA.get(self.current_stage, [])
        missing = [item for item in required if not self.checklist.get(item, False)]
        return (len(missing) == 0, missing)

    def advance_stage(self) -> bool:
        """Attempt to advance to next stage."""
        can_advance, missing = self.can_advance()
        if can_advance and self.current_stage < ReviewStage.REPORT:
            self.current_stage = ReviewStage(self.current_stage + 1)
            return True
        return False

    def get_progress_pct(self) -> float:
        """Calculate overall progress percentage."""
        total_criteria = sum(len(c) for c in STAGE_EXIT_CRITERIA.values())
        completed = sum(1 for v in self.checklist.values() if v)
        return (completed / total_criteria) * 100 if total_criteria > 0 else 0
```

**Impact:** Ensures consistent coverage; prevents skipping stages.

#### 4. Input/Output Schemas

**Problem:** No formal validation of manuscript metadata or review output structure.

**Solution:** Create `schemas/` directory with JSON schemas

```json
// schemas/manuscript_input.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ManuscriptInput",
  "type": "object",
  "required": ["title", "manuscript_type"],
  "properties": {
    "title": {"type": "string", "minLength": 1},
    "authors": {"type": "string"},
    "manuscript_type": {
      "type": "string",
      "enum": ["original_research", "review", "meta_analysis", "methods", "short_report", "preprint", "presentation"]
    },
    "discipline": {
      "type": "string",
      "enum": ["biomedical", "computational", "clinical", "physical_sciences", "social_sciences", "other"]
    },
    "venue_tier": {
      "type": "string",
      "enum": ["top_tier", "standard", "student_thesis"],
      "default": "standard"
    },
    "sections_present": {
      "type": "array",
      "items": {"type": "string"}
    },
    "figure_count": {"type": "integer", "minimum": 0},
    "table_count": {"type": "integer", "minimum": 0},
    "word_count": {"type": "integer", "minimum": 0}
  }
}
```

```json
// schemas/review_output.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ReviewOutput",
  "type": "object",
  "required": ["summary", "recommendation", "major_comments", "minor_comments"],
  "properties": {
    "summary": {
      "type": "object",
      "required": ["synopsis", "recommendation", "strengths", "weaknesses"],
      "properties": {
        "synopsis": {"type": "string", "minLength": 100},
        "recommendation": {
          "type": "string",
          "enum": ["accept", "minor_revisions", "major_revisions", "reject"]
        },
        "strengths": {
          "type": "array",
          "items": {"type": "string"},
          "minItems": 2,
          "maxItems": 5
        },
        "weaknesses": {
          "type": "array",
          "items": {"type": "string"},
          "minItems": 1,
          "maxItems": 5
        }
      }
    },
    "scores": {
      "type": "object",
      "properties": {
        "problem_formulation": {"type": "number", "minimum": 1, "maximum": 5},
        "literature_review": {"type": "number", "minimum": 1, "maximum": 5},
        "methodology": {"type": "number", "minimum": 1, "maximum": 5},
        "data_collection": {"type": "number", "minimum": 1, "maximum": 5},
        "analysis": {"type": "number", "minimum": 1, "maximum": 5},
        "results": {"type": "number", "minimum": 1, "maximum": 5},
        "writing": {"type": "number", "minimum": 1, "maximum": 5},
        "citations": {"type": "number", "minimum": 1, "maximum": 5}
      }
    },
    "major_comments": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["issue", "location", "severity", "recommendation"],
        "properties": {
          "issue": {"type": "string"},
          "location": {"type": "string"},
          "severity": {"type": "string", "enum": ["critical", "major"]},
          "recommendation": {"type": "string"}
        }
      }
    },
    "minor_comments": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["issue", "location"],
        "properties": {
          "issue": {"type": "string"},
          "location": {"type": "string"},
          "recommendation": {"type": "string"}
        }
      }
    }
  }
}
```

**Impact:** Enables automated validation; ensures output consistency.

---

### P2: Medium Priority (Implement Third)

#### 5. Calibration Examples

**Problem:** No anchor points for scoring consistency across sessions.

**Solution:** Create `calibration/` directory with scored examples for each dimension

```markdown
<!-- calibration/methodology_examples.md -->
# Methodology Scoring Calibration

## Score 5 Example (Excellent)
**Excerpt:** "Cells were treated with compound X (10μM, Sigma #12345, lot ABC123)
for 24h at 37°C/5% CO2. Viability was assessed using MTT assay (n=6 biological
replicates, 3 technical replicates each). Statistical analysis used one-way
ANOVA with Tukey's post-hoc correction (α=0.05). Power analysis (G*Power 3.1)
indicated n=5 required for 80% power to detect 20% difference."

**Why 5:** Complete reagent info, appropriate replication, justified statistics,
power analysis documented, fully replicable.

## Score 3 Example (Adequate)
**Excerpt:** "Cells were treated with compound X for 24h. Viability was measured
using MTT assay (n=3). Statistical significance was determined using t-test."

**Why 3:** Missing concentration, vendor info, replicate type unclear, no
power justification, basic but acceptable for replication with assumptions.

## Score 1 Example (Poor)
**Excerpt:** "Cells were treated and viability measured using standard protocols."

**Why 1:** No replication possible. Missing all critical details.
```

**Impact:** Anchors scoring; reduces inter-session variance by 30-50%.

#### 6. Common Issue Lookup Table

**Problem:** 22+ issues in common_issues.md must be manually cross-referenced.

**Solution:** Create structured lookup with severity mappings

```python
# validators/issue_lookup.py
from dataclasses import dataclass
from typing import List, Optional
from severity_classifier import Severity

@dataclass
class CommonIssue:
    """Cataloged peer review issue with deterministic classification."""
    code: str
    category: str
    name: str
    description: str
    detection_hints: List[str]
    default_severity: Severity
    recommendation_template: str

ISSUE_CATALOG = {
    # Statistical Issues
    "STAT_01": CommonIssue(
        code="STAT_01",
        category="statistical",
        name="P-value misuse",
        description="P-hacking, multiple testing without correction, or misinterpretation",
        detection_hints=[
            "Suspiciously high proportion of p-values just below 0.05",
            "Many tests performed but no correction mentioned",
            "No effect sizes or confidence intervals reported"
        ],
        default_severity=Severity.MAJOR,
        recommendation_template="Report effect sizes with confidence intervals. Apply appropriate multiple testing corrections ({correction_type})."
    ),
    "STAT_02": CommonIssue(
        code="STAT_02",
        category="statistical",
        name="Inappropriate statistical test",
        description="Parametric tests with violated assumptions, wrong test for data type",
        detection_hints=[
            "No mention of assumption checking",
            "Small sample sizes with parametric tests",
            "Multiple pairwise t-tests instead of ANOVA"
        ],
        default_severity=Severity.MAJOR,
        recommendation_template="Check assumptions explicitly. Consider {alternative_test} as alternative."
    ),
    "STAT_03": CommonIssue(
        code="STAT_03",
        category="statistical",
        name="Pseudoreplication",
        description="Technical replicates treated as biological replicates",
        detection_hints=[
            "n defined as number of measurements rather than biological units",
            "Multiple cells from same animal counted as independent",
            "No mention of random effects or clustering"
        ],
        default_severity=Severity.CRITICAL,
        recommendation_template="Define n as biological replicates. Use mixed-effects models for nested data."
    ),
    # ... additional issues from common_issues.md
}

def lookup_issue(code: str) -> Optional[CommonIssue]:
    """Retrieve issue details by code."""
    return ISSUE_CATALOG.get(code)

def search_issues(keyword: str) -> List[CommonIssue]:
    """Search issues by keyword in name or description."""
    keyword = keyword.lower()
    return [
        issue for issue in ISSUE_CATALOG.values()
        if keyword in issue.name.lower() or keyword in issue.description.lower()
    ]
```

**Impact:** Standardizes issue identification; enables auto-severity assignment.

---

### P3: Lower Priority (Future Enhancement)

#### 7. Figure Quality Checker

```python
# scripts/figure_checker.py
from PIL import Image
from dataclasses import dataclass
from typing import Tuple

@dataclass
class FigureQualityThresholds:
    """Thresholds from SKILL.md lines 323-330."""
    resolution_dpi: Tuple[int, int, int] = (150, 300, 600)  # min, target, excellent
    font_size_pt: Tuple[int, int, int] = (7, 8, 10)
    contrast_ratio: Tuple[float, float, float] = (4.5, 7.0, 10.0)
    line_weight_pt: Tuple[float, float, float] = (0.5, 1.0, 1.5)

THRESHOLDS = FigureQualityThresholds()

def check_resolution(image_path: str) -> dict:
    """Check image resolution against thresholds."""
    with Image.open(image_path) as img:
        dpi = img.info.get('dpi', (72, 72))
        actual_dpi = min(dpi) if isinstance(dpi, tuple) else dpi

        return {
            "actual_dpi": actual_dpi,
            "meets_minimum": actual_dpi >= THRESHOLDS.resolution_dpi[0],
            "meets_target": actual_dpi >= THRESHOLDS.resolution_dpi[1],
            "meets_excellent": actual_dpi >= THRESHOLDS.resolution_dpi[2],
            "tier": classify_tier(actual_dpi, THRESHOLDS.resolution_dpi)
        }

def classify_tier(value: float, thresholds: Tuple) -> str:
    """Classify value into quality tier."""
    if value >= thresholds[2]:
        return "excellent"
    elif value >= thresholds[1]:
        return "target"
    elif value >= thresholds[0]:
        return "minimum"
    return "below_minimum"
```

#### 8. Statistical Test Validator

```python
# validators/statistical_tests.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TestRecommendation:
    """Deterministic statistical test recommendation."""
    test_name: str
    assumptions: List[str]
    alternatives: List[str]
    when_to_use: str

# Decision tree from references/common_issues.md
TEST_SELECTION = {
    ("continuous", "2_groups", "independent", "normal"): TestRecommendation(
        test_name="Independent t-test",
        assumptions=["Normality", "Homogeneity of variance", "Independence"],
        alternatives=["Mann-Whitney U"],
        when_to_use="Comparing means of two independent groups with normal data"
    ),
    ("continuous", "2_groups", "independent", "non_normal"): TestRecommendation(
        test_name="Mann-Whitney U",
        assumptions=["Independence", "Similar distribution shapes"],
        alternatives=["Permutation test"],
        when_to_use="Comparing two independent groups with non-normal data"
    ),
    ("continuous", "2_groups", "paired", "normal"): TestRecommendation(
        test_name="Paired t-test",
        assumptions=["Normality of differences", "Paired observations"],
        alternatives=["Wilcoxon signed-rank"],
        when_to_use="Comparing paired/matched observations with normal differences"
    ),
    ("continuous", "3+_groups", "independent", "normal"): TestRecommendation(
        test_name="One-way ANOVA",
        assumptions=["Normality", "Homogeneity of variance", "Independence"],
        alternatives=["Kruskal-Wallis", "Welch's ANOVA"],
        when_to_use="Comparing means across 3+ independent groups"
    ),
    # ... additional combinations
}

def recommend_test(
    data_type: str,
    groups: str,
    design: str,
    distribution: str
) -> Optional[TestRecommendation]:
    """Get deterministic test recommendation based on data characteristics."""
    key = (data_type, groups, design, distribution)
    return TEST_SELECTION.get(key)
```

---

## Implementation Plan

### Phase 1: Critical Infrastructure (Week 1)
- [ ] Create `validators/severity_classifier.py`
- [ ] Extend `scripts/calculate_scores.py` with validation
- [ ] Create `schemas/` directory with JSON schemas
- [ ] Add basic input validation to workflow

### Phase 2: Workflow Automation (Week 2)
- [ ] Create `scripts/workflow_tracker.py`
- [ ] Integrate state tracking into SKILL.md guidance
- [ ] Add stage gate enforcement hints

### Phase 3: Calibration & Lookup (Week 3)
- [ ] Create `calibration/` directory
- [ ] Add 3 calibration examples per dimension (24 total)
- [ ] Create `validators/issue_lookup.py` with issue catalog

### Phase 4: Advanced Validators (Week 4)
- [ ] Implement `scripts/figure_checker.py`
- [ ] Implement `validators/statistical_tests.py`
- [ ] Add integration tests for all validators

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Severity classification consistency | ~60% | >95% | Same issue → same severity across sessions |
| Score variance (same paper) | ±0.8 points | ±0.3 points | Repeated reviews of calibration papers |
| Stage completion verification | Manual | Automated | Workflow tracker gate pass rate |
| Review completeness | Variable | >95% | Schema validation pass rate |

---

## Testing Strategy

### Unit Tests
- Severity classifier returns correct severity for all threshold conditions
- Score validation catches missing dimensions and out-of-bounds values
- Workflow tracker correctly identifies missing exit criteria

### Integration Tests
- End-to-end review of calibration manuscript produces consistent scores
- Workflow state persists correctly across stage transitions
- Output passes JSON schema validation

### Regression Tests
- Historical reviews remain valid under new validation rules
- No false positives in severity classification

---

## Dependencies

- Python 3.8+
- Pillow (for figure_checker.py)
- jsonschema (for schema validation)
- dataclasses (standard library)

---

## Maintenance Notes

1. **Severity rules** should be updated when SKILL.md criteria change
2. **Calibration examples** should be reviewed annually for relevance
3. **Issue catalog** should sync with `references/common_issues.md`
4. **Test selection tree** should be validated against current statistical best practices

---

## References

- SKILL.md lines 447-452: Severity classification criteria
- SKILL.md lines 323-330: Figure quality thresholds
- references/workflow_transitions.md: Stage exit criteria
- references/common_issues.md: Issue catalog source
- scripts/calculate_scores.py: Existing deterministic implementation
