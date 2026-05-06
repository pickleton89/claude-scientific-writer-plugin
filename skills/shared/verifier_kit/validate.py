"""Generic two-stage validation framework for audit-style skills.

Pattern (extracted from `skills/research-accuracy-verifier/scripts/validate_finding.py`):

    Stage 1: JSON Schema (Draft-07). Continue past failures so Stage 2 still
             runs — partial errors are more useful than an early abort that
             hides downstream issues.
    Stage 2: Skill-defined predicates. Override `run_predicates()` to add
             whatever invariants the skill requires (e.g., verifier's P1-P5,
             summarizer's Q5/R5).

Subclasses provide the schema path (or live dict) and any auxiliary data
files (severity matrices, threshold YAMLs). The framework guarantees:

  * Errors collected from both stages, returned together.
  * Warnings emitted independently of errors (advisory, never fail-causing).
  * `validate(record, **ctx)` returns `(ok, errors, warnings)` so downstream
    callers can format / persist / abort however they like.

Example minimal subclass:

    class MyValidator(SchemaValidator):
        def run_predicates(self, record, errors, warnings, **ctx):
            if record.get("foo") == "bar" and "baz" not in record:
                errors.append("MyP1: foo=bar requires baz")

The CLI wrapper for any subclass is ~15 lines — see
`skills/research-accuracy-verifier/scripts/validate_finding.py` for a
worked example.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


@dataclass
class ValidationOutcome:
    """Structured return for a single validation pass.

    Equivalent to the `(ok, errors, warnings)` tuple returned by `validate()`
    but useful when callers want to attach extra fields (record id, file
    path, batch index) without re-shaping the tuple.
    """

    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_tuple(cls, tup: tuple[bool, list[str], list[str]]) -> ValidationOutcome:
        ok, errors, warnings = tup
        return cls(ok=ok, errors=list(errors), warnings=list(warnings))


class SchemaValidator:
    """Two-stage validator: schema first (continue past failures), predicates second.

    Subclass and override `run_predicates()` to add skill-specific rule
    checks. The base class handles the schema half generically.

    Parameters
    ----------
    schema:
        Either a `dict` (the schema body) or a `Path | str` pointing to a JSON
        Schema file. Loaded once at construction; not re-read per validation.
    """

    def __init__(self, schema: dict[str, Any] | str | Path) -> None:
        if isinstance(schema, dict):
            self._schema: dict[str, Any] = schema
        else:
            with open(schema) as f:
                self._schema = json.load(f)
        self._validator = Draft7Validator(self._schema)

    @property
    def schema(self) -> dict[str, Any]:
        return self._schema

    def run_predicates(
        self,
        record: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        **ctx: Any,
    ) -> None:
        """Override to add skill-specific predicate checks.

        Append to `errors` for failures (cause the overall validation to
        report invalid) or to `warnings` for advisories (do not fail the
        record). `ctx` carries arbitrary keyword data the subclass needs —
        for example, `document_type` for the verifier's P5 severity check.
        """
        return None

    def validate(
        self, record: dict[str, Any], **ctx: Any
    ) -> tuple[bool, list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        # Stage 1: JSON Schema. Collect every error; do not raise.
        for err in self._validator.iter_errors(record):
            errors.append(f"schema: {err.message} at {list(err.absolute_path)}")

        # Stage 2: skill predicates. Subclass writes into the same buffers.
        self.run_predicates(record, errors, warnings, **ctx)

        return len(errors) == 0, errors, warnings

    def validate_outcome(
        self, record: dict[str, Any], **ctx: Any
    ) -> ValidationOutcome:
        """Same as `validate()` but returns a `ValidationOutcome` dataclass."""
        return ValidationOutcome.from_tuple(self.validate(record, **ctx))
