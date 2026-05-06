"""verifier_kit — reusable scaffolding for fact-checking-style skills.

Extracted from `research-accuracy-verifier` (Sprint 3 of the skill-chaining
pilot) so other skills can adopt the same fork-friendly pattern: a two-stage
JSON-Schema + predicate validator and a stage-checkpoint state machine.

Public API:
    SchemaValidator    — base class for two-stage validation. Subclass to add
                         domain predicates; the schema half is generic.
    Checkpoint         — stage-checkpoint state machine parameterized over
                         stage names, audits root, and an optional pre-write
                         findings validator.
    ResumeState        — dataclass returned by Checkpoint.load_resume_state.
    slugify            — filesystem-safe slug helper.
    replay_state       — convenience: load a ResumeState and project it to a
                         target stage for downstream consumers.

Each module remains importable on its own; this package just gives a single
top-level surface for adopters.
"""

from .checkpoint import Checkpoint, ResumeState, slugify
from .replay import replay_state
from .validate import SchemaValidator, ValidationOutcome

__all__ = [
    "Checkpoint",
    "ResumeState",
    "SchemaValidator",
    "ValidationOutcome",
    "replay_state",
    "slugify",
]
