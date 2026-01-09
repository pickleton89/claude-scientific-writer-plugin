"""Paper-2-Web deterministic utilities library.

This library provides deterministic components for the paper-2-web skill:
- venue_database: Lookup tables for conference poster specifications
- cost_estimator: Token and cost estimation for transformations
- component_router: Use-case based component selection
- quality_scorer: Automated quality metrics
- reproducibility: Manifest generation for reproducible runs
"""

from .venue_database import (
    VENUE_POSTER_SPECS,
    get_poster_specs,
    list_supported_venues,
    get_poster_pixel_dimensions,
)
from .cost_estimator import (
    CostEstimate,
    MODEL_COSTS,
    MODEL_TIERS,
    estimate_cost,
    get_complexity_multiplier,
)
from .component_router import (
    UseCase,
    ComponentRecommendation,
    route_components,
    infer_use_case,
)
from .quality_scorer import (
    QualityScore,
    QualityReport,
    score_website,
    score_poster,
    score_video,
)
from .reproducibility import (
    ReproducibilityConfig,
    ReproducibilityManifest,
    hash_file,
    hash_directory,
    generate_manifest,
    save_manifest,
    verify_reproduction,
)

__all__ = [
    # venue_database
    "VENUE_POSTER_SPECS",
    "get_poster_specs",
    "list_supported_venues",
    "get_poster_pixel_dimensions",
    # cost_estimator
    "CostEstimate",
    "MODEL_COSTS",
    "MODEL_TIERS",
    "estimate_cost",
    "get_complexity_multiplier",
    # component_router
    "UseCase",
    "ComponentRecommendation",
    "route_components",
    "infer_use_case",
    # quality_scorer
    "QualityScore",
    "QualityReport",
    "score_website",
    "score_poster",
    "score_video",
    # reproducibility
    "ReproducibilityConfig",
    "ReproducibilityManifest",
    "hash_file",
    "hash_directory",
    "generate_manifest",
    "save_manifest",
    "verify_reproduction",
]
