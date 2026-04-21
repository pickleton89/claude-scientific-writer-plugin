# brand-interface — Support Tooling (Not a Skill)

This directory is **not a callable skill**. It has no `SKILL.md` by design. It holds the executable implementation of the brand-skill contract defined in [`../BRAND_SKILL_INTERFACE.md`](../BRAND_SKILL_INTERFACE.md).

## What lives here

| Path | Purpose |
|---|---|
| `schemas/brand-tokens.schema.json` | JSON Schema (2020-12) for validating any brand's `brand-tokens.json` |
| `type_stubs/adapter_interface.pyi` | Python type stubs for `BrandAdapterProtocol` (required methods: `set_brand_style`, `get_cycle`, `get_color`) |
| `validation/validate_brand.py` | End-to-end validator for a brand skill |
| `validation/check_accessibility.py` | WCAG contrast checker for brand palettes |
| `validation/controlled_vocabularies.py` | Enum definitions enforced across brand skills |
| `tests/` | 173 tests covering schema validation, accessibility, and controlled vocabularies |
| `DETERMINISM_AUDIT.md` | Audit record: this tooling gives the contract a ~95% determinism score |

## Relationship to the rest of the repo

- [`../BRAND_SKILL_INTERFACE.md`](../BRAND_SKILL_INTERFACE.md) — prose specification of the contract this directory enforces.
- [`../oligon-brand/`](../oligon-brand/) — the reference implementation that satisfies the contract. Any new brand skill should mirror its structure (`tokens/brand-tokens.json` + `adapters/*` + SKILL.md).

## Running validation

```bash
# Validate a brand skill end-to-end
uv run python skills/brand-interface/validation/validate_brand.py skills/your-brand

# Check color-pair accessibility (WCAG AA/AAA)
uv run python skills/brand-interface/validation/check_accessibility.py skills/your-brand/tokens/brand-tokens.json

# JSON-Schema validation
uv run python -c "import json, jsonschema; \
  schema = json.load(open('skills/brand-interface/schemas/brand-tokens.schema.json')); \
  tokens = json.load(open('skills/your-brand/tokens/brand-tokens.json')); \
  jsonschema.validate(tokens, schema); print('Valid!')"

# Full test suite
uv run pytest skills/brand-interface/tests/
```

## Why the name is not `oligon-brand`-shaped

`oligon-brand/` implements the contract. `brand-interface/` *is* the contract's tooling. If you are authoring a new brand skill (e.g., `acme-brand/`), read `BRAND_SKILL_INTERFACE.md` first, then use the scripts here to validate your work. Do not try to invoke this directory as a skill — the skill router does not list it, and it has no `SKILL.md`.
