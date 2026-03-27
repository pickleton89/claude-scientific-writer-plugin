"""
Consolidated thresholds for the deep-research pipeline.

Constants-only module — no main(), no CLI. All quantitative thresholds that
were previously scattered across bibliography.md, compiler.md, SKILL.md,
biomedical_research.md, convergence_signals.md, synthesis.md, and
score_hypothesis.py are consolidated here.

Other scripts import via:
    sys.path.insert(0, str(Path(__file__).parent))
    from thresholds import MIN_SOURCES, WORD_COUNTS, ...
"""

from typing import Final

# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

ALL_MODES: Final[tuple[str, ...]] = (
    "full",
    "quick",
    "lit-review",
    "systematic-review",
    "hypothesis",
    "fact-check",
    "socratic",
    "review",
)

# ---------------------------------------------------------------------------
# Evidence tiers (ordering: T1 strongest → T4 weakest)
# ---------------------------------------------------------------------------

TIER_ORDER: Final[tuple[str, ...]] = ("T1", "T2", "T3", "T4")

# ---------------------------------------------------------------------------
# Literature search — minimum sources per mode
# (bibliography.md §Quantitative Thresholds + SKILL.md exit criteria)
# Source table covers full/quick/lit-review/systematic-review only;
# hypothesis, fact-check, review, socratic extrapolated from nearest mode.
# ---------------------------------------------------------------------------

MIN_SOURCES: Final[dict[str, int]] = {
    "full": 15,
    "quick": 5,
    "lit-review": 25,
    "systematic-review": 30,  # "all eligible" — use 30 as practical floor
    "hypothesis": 15,
    "fact-check": 3,
    "review": 0,        # no search phase
    "socratic": 0,      # no search phase
}

# ---------------------------------------------------------------------------
# Literature search — minimum databases searched per mode
# ---------------------------------------------------------------------------

MIN_DATABASES: Final[dict[str, int]] = {
    "full": 3,
    "quick": 2,
    "lit-review": 3,
    "systematic-review": 4,
    "hypothesis": 3,
    "fact-check": 2,
    "review": 0,
    "socratic": 0,
}

# ---------------------------------------------------------------------------
# Search saturation thresholds (fraction of new papers in final iteration)
# None = saturation check not applicable
# ---------------------------------------------------------------------------

SEARCH_SATURATION: Final[dict[str, float | None]] = {
    "full": 0.05,
    "quick": None,
    "lit-review": 0.05,
    "systematic-review": 0.02,
    "hypothesis": 0.05,
    "fact-check": None,
    "review": None,
    "socratic": None,
}

# ---------------------------------------------------------------------------
# Minimum fraction of sources from the last 5 years
# ---------------------------------------------------------------------------

RECENT_THRESHOLD: Final[dict[str, float]] = {
    "full": 0.60,
    "quick": 0.50,
    "lit-review": 0.60,
    "systematic-review": 0.60,  # "per protocol" — use 60% as default
    "hypothesis": 0.60,
    "fact-check": 0.50,
    "review": 0.0,
    "socratic": 0.0,
}

# ---------------------------------------------------------------------------
# Minimum fraction of peer-reviewed sources
# ---------------------------------------------------------------------------

PEER_REVIEWED_MIN: Final[dict[str, float]] = {
    "full": 0.60,
    "quick": 0.50,
    "lit-review": 0.70,
    "systematic-review": 0.80,
    "hypothesis": 0.60,
    "fact-check": 0.50,
    "review": 0.0,
    "socratic": 0.0,
}

# ---------------------------------------------------------------------------
# Word counts — target range and hard min/max per mode
# (compiler.md §Word Count Targets)
# ---------------------------------------------------------------------------

WORD_COUNTS: Final[dict[str, dict[str, int]]] = {
    "full":              {"target_min": 3000, "target_max":  8000, "hard_min": 2500, "hard_max": 10000},
    "quick":             {"target_min":  500, "target_max":  1500, "hard_min":  300, "hard_max":  2000},
    "lit-review":        {"target_min": 2000, "target_max":  5000, "hard_min": 1500, "hard_max":  7000},
    "systematic-review": {"target_min": 5000, "target_max": 15000, "hard_min": 4000, "hard_max": 20000},
    "hypothesis":        {"target_min": 2000, "target_max":  4000, "hard_min": 1500, "hard_max":  5000},
    "fact-check":        {"target_min":  300, "target_max":  1000, "hard_min":  200, "hard_max":  1500},
    "review":            {"target_min": 1000, "target_max":  3000, "hard_min":  500, "hard_max":  4000},
    "socratic":          {"target_min":    0, "target_max":     0, "hard_min":    0, "hard_max":     0},  # no compiler output
}

# ---------------------------------------------------------------------------
# Spot-check rates for verification agent
# (fraction of sources to verify via full-text snippet)
# Keyed by mode, then by topic type (biomedical vs general).
# systematic-review and fact-check verify all regardless of topic.
# (verification.md §Step 4: biomedical 50%, general 30%, systematic 100%)
# ---------------------------------------------------------------------------

SPOT_CHECK_RATES: Final[dict[str, dict[str, float]]] = {
    "full":              {"biomedical": 0.50, "general": 0.30},
    "quick":             {"biomedical": 0.50, "general": 0.30},
    "lit-review":        {"biomedical": 0.50, "general": 0.30},
    "systematic-review": {"biomedical": 1.00, "general": 1.00},
    "hypothesis":        {"biomedical": 0.50, "general": 0.30},
    "fact-check":        {"biomedical": 1.00, "general": 1.00},
    "review":            {"biomedical": 0.50, "general": 0.30},
    "socratic":          {"biomedical": 0.0,  "general": 0.0},
}

# ---------------------------------------------------------------------------
# Currency thresholds by research field
# (biomedical_research.md §Currency Rules by Field)
# Values are in years.
# ---------------------------------------------------------------------------

CURRENCY_THRESHOLDS: Final[dict[str, dict[str, float | None]]] = {
    "biomedical":          {"recent": 5.0,  "current": 1.0},
    "ml_genomics":         {"recent": 2.0,  "current": 0.5},
    "drug_development":    {"recent": 5.0,  "current": 2.0},
    "clinical_practice":   {"recent": 5.0,  "current": 2.0},
    "structural_biology":  {"recent": 10.0, "current": 3.0},
    "seminal":             {"recent": None, "current": None},  # exempt
}

# ---------------------------------------------------------------------------
# Convergence signals for Socratic mode
# (convergence_signals.md §Convergence Rules)
# ---------------------------------------------------------------------------

CONVERGENCE_SIGNALS_REQUIRED: Final[int] = 3          # min active for CONVERGED
CONVERGENCE_SIGNALS_TOTAL: Final[int] = 5             # B1-B5
CONVERGENCE_STAGNATION_ROUNDS: Final[int] = 10        # no new INSIGHT
CONVERGENCE_TIME_LIMIT_TURNS: Final[int] = 40         # force-complete
SCOPE_STABILITY_ROUNDS: Final[int] = 3                # B4 requires 3 stable rounds

# ---------------------------------------------------------------------------
# Evidence strength thresholds for synthesis agent
# (synthesis.md §Theme-Level Evidence Strength)
# ---------------------------------------------------------------------------

STRONG_MIN_SOURCES: Final[int] = 3
MODERATE_MIN_SOURCES: Final[int] = 2
EMERGING_MAX_AGE_YEARS: Final[float] = 1.0            # ≤1 year for "emerging"

# ---------------------------------------------------------------------------
# Hypothesis quality scoring
# (score_hypothesis.py thresholds)
# ---------------------------------------------------------------------------

HYPOTHESIS_STRONG_THRESHOLD: Final[int] = 8           # total ≥8 out of 10
HYPOTHESIS_VIABLE_THRESHOLD: Final[int] = 5           # total ≥5 out of 10
HYPOTHESIS_MAX_SCORE: Final[int] = 10
HYPOTHESIS_CRITERIA_COUNT: Final[int] = 5             # 5 criteria × 2 pts each

# ---------------------------------------------------------------------------
# Kappa threshold for inter-rater reliability (screening)
# ---------------------------------------------------------------------------

KAPPA_THRESHOLD: Final[float] = 0.80

# ---------------------------------------------------------------------------
# Mandatory output sections (by mode)
# Used by output_validator.py
# ---------------------------------------------------------------------------

MANDATORY_SECTIONS_ALL: Final[tuple[str, ...]] = (
    "AI Disclosure",
    "References",
    "Limitations",
)

MANDATORY_SECTIONS_BY_MODE: Final[dict[str, tuple[str, ...]]] = {
    "full":              ("Executive Summary", "Methods", "Results", "Discussion"),
    "quick":             ("Key Findings", "Evidence Summary"),
    "lit-review":        ("Search Strategy", "Literature Matrix", "Thematic Synthesis", "Gap Analysis"),
    "systematic-review": ("Abstract", "Methods", "Results", "Discussion"),
    "hypothesis":        ("Background", "Hypotheses", "Comparison Matrix"),
    "fact-check":        ("Claim", "Verdict", "Evidence"),
    "review":            ("Summary", "Strengths", "Weaknesses", "Recommendations"),
    "socratic":          (),  # no compiler output
}

# ---------------------------------------------------------------------------
# Citation format regex
# ---------------------------------------------------------------------------

CITATION_PATTERN: Final[str] = r"\[T[1-4]:\s*[^\]]+\]"
