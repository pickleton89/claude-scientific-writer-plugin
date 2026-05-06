# `verifier_kit` — adoption guide

Reusable scaffolding for fact-checking-style and audit-style skills, extracted from `research-accuracy-verifier` (Sprint 3 of the skill-chaining pilot). The kit gives a new skill three things:

1. **`SchemaValidator`** — a two-stage JSON-Schema-plus-predicates validator base class. The schema half is generic; subclasses override `run_predicates()` to enforce skill-specific rules.
2. **`Checkpoint`** — a stage-checkpoint state machine for resumable pipelines. Parameterized over stage names, audits-root path, and an optional findings validator.
3. **Base schemas** — canonical `$defs` libraries (`finding.base.json`, `intake.base.json`, `audit_report.base.json`) capturing the genuinely-shared shapes (severity, confidence, location, evidence) that audit-style records use.

Worked examples:
- `skills/research-accuracy-verifier/scripts/{validate_finding.py, checkpoint.py}` — the pilot consumer (Sprint 1 → Sprint 3 wrapper refactor)
- `skills/research-paper-summarizer/scripts/validate_stats.py` — the second consumer (Sprint 2 → Sprint 3 subclass refactor)

---

## When to use the kit

Adopt the kit when your skill produces structured, schema-validated records (findings, claims, statistics, checks) and would benefit from:

- **Forked execution.** The kit's two-stage validator + checkpoint pattern composes cleanly with `context: fork` because all heavy state lives on disk, not in main context. A fork can write per-stage artifacts and emit a compact JSON return; the caller follows up with targeted `!\`jq …\`` reads.
- **Resumable pipelines.** Multi-hour audits with many MCP calls regularly exhaust the context window. Stage checkpointing lets a fresh session pick up where the previous one left off without re-running already-completed stages.
- **Determinism.** The two-stage validator keeps schema-shape errors and rule-violation errors in the same error list, so a downstream gate can decide "any error → block" without distinguishing source.

Skip the kit if your skill's output is unstructured prose, conversational reviewer commentary, or purely free-text — there's nothing for the schema half to validate.

---

## Adopting the kit in three steps

### 1. Add `context: fork` frontmatter (and the supporting fields)

In your skill's `SKILL.md`:

```yaml
---
name: my-audit-skill
context: fork
agent: general-purpose          # or a more specialized agent if available
model: claude-sonnet-4-6        # or claude-opus-4-7 for highest-leverage skills
effort: medium                  # or "high" when verdict-truthfulness matters
allowed-tools: [Read, Write, Bash, ...]   # whatever your stages need
---
```

Then append a **`## Fork-return contract`** section to the body that defines the compact JSON object the fork emits. Keep raw evidence, full-text snippets, MCP responses, and intermediate stage findings on disk — the contract is what the caller sees.

See `skills/research-accuracy-verifier/SKILL.md` (§ Fork-return contract) and `skills/research-paper-summarizer/SKILL.md` (§ Fork-return contract) for two worked variants.

### 2. Define your schema and subclass `SchemaValidator`

Author your skill's record schema (e.g., `schemas/finding.json` or `schemas/stats.json`). Reuse fragments from the base schemas where shape is universal:

- `severityEnum` — `CRITICAL | MAJOR | MINOR | INFORMATIONAL`
- `confidenceEnum` — `high | medium | low`
- `locationObject` — `{section, paragraph, line?}`
- `evidenceItem` / `evidenceArray`

You can either copy the `$defs` inline (simplest, no resolver setup) or `$ref` them with a configured `RefResolver` (cleaner, more setup). Sprint 3 ships the bases as a reference library — both consumer skills (`research-accuracy-verifier`, `research-paper-summarizer`) currently keep their schemas self-contained, with the bases serving as the canonical source for future $ref rewiring.

Then subclass:

```python
from verifier_kit.validate import SchemaValidator

class MyValidator(SchemaValidator):
    def __init__(self, schema_path=None):
        super().__init__(schema_path or Path("schemas/finding.json"))

    def run_predicates(self, record, errors, warnings, **ctx):
        # Your skill-specific rule checks. Append to errors / warnings.
        if record.get("severity") == "CRITICAL" and len(record.get("verification_path") or []) < 2:
            errors.append("MyP1: CRITICAL severity requires ≥2 verification paths")
```

The base class:
- Reads the schema once at construction.
- Runs JSON Schema validation; **continues past failures** so predicate checks still report.
- Calls your `run_predicates()` with the record plus arbitrary context (you can pass `document_type`, `flag_threshold`, etc. as kwargs to `validate()`).
- Returns `(ok, errors, warnings)` — or use `validate_outcome()` for the dataclass form.

For a CLI wrapper, see `validate_finding.py` (~40-line argparse harness around the validator).

### 3. Wire stage checkpointing

If your skill has multiple stages and benefits from resumability:

```python
from verifier_kit.checkpoint import Checkpoint

cp = Checkpoint(
    stage_names={1: "extract", 2: "summarize", 3: "validate"},
    audits_root=Path("research/my-audits"),
    findings_validator=MyValidator().validate,   # optional but recommended
)

# Stage write:
cp.write("paper-slug", 2, findings, matrix_delta, document_type="general")

# Resume:
state = cp.load("paper-slug")
print(state.completed_stages)   # [1, 2] for example
print(state.next_stage)         # 3
```

If your Stage 1 produces a different artifact shape than Stages 2+ (the verifier's `claim_inventory.json` is the canonical example), pass `stage_one_alternate_filename="…"` and write Stage 1's payload via the `stage_one_payload=` kwarg.

---

## Sprint 3 → Sprint 4 outlook

The kit is deliberately small (~300 lines across `validate.py` + `checkpoint.py` + `replay.py`) and the wrappers are thin. The Sprint 4+ goals it sets up — without committing to them now — are:

- **Per-stage forks.** A fork that runs only Stage N reads upstream artifacts via `replay_state(cp, slug, upto_stage=N-1)` instead of re-running stages 1..N-1. The current `replay.py` is the smallest version that works; Sprint 4 will add per-finding stage tags so truncation is precise.
- **Schema $ref rewiring.** Existing skill schemas continue to inline their shapes for Sprint 3 (no behavior change). A future patch can rewire severity / confidence / location / evidence references to `finding.base.json#/$defs/...` once a shared `RefResolver` configuration is in place.
- **Wider propagation.** `deep-research/bibliography`, `prose-audit`, and the dossier validators (`entity-resolution`, `target-intelligence`, `drug-intelligence`, `target-validation`) are candidates — each sprint after this should add at most one consumer so behavior is monitored end-to-end.

---

## Frozen during the pilot

Per the original plan:

- **`skills/shared/CONTRACTS.md`** and **`skills/shared/references/prose_standards_thresholds.yaml`** — kit consumers read these but the kit doesn't reshape them.
- **The verifier's verdict / severity / claim_type enums and the `SeverityMatrix`** — verifier-internal; not promoted to the base schemas because they're domain-specific (the summarizer doesn't have verdicts).

If you need to extend the kit itself (new method on `SchemaValidator`, new shape in `audit_report.base.json`, etc.), prefer adding to it over reshaping. The kit's API is small enough that a careful extension is cheap; a reshape risks breaking both consumers.
