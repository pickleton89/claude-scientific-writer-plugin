# SkillsBench Audit — oligon-brand/SKILL.md

**Audit date:** 2026-02-23
**Skill version:** 4.0.1
**Auditor:** Claude Opus 4.6 (SkillsBench framework)

---

## Scratchpad

### 1. Procedural vs. Declarative ("How-To" Check)

Strong procedural content present:
- The `<workflow>` section (lines 131-221) provides a clear 5-stage SOP: Load Tokens → Apply Style → Create Figure → Preflight Check → Verification
- The `<decision_framework>` (lines 97-129) gives a concrete decision tree for color cycle selection based on number of data series
- `<error_handling>` (lines 287-315) gives symptom→solution pairs with code fixes
- `<anti_patterns>` (lines 259-285) give problem→solution pairs

However, there is significant declarative bloat:
- `<default_behavior>` (lines 20-48) is a 6-row table documenting which skills auto-integrate — this is capability documentation, not procedural guidance
- `<when_to_use>` (lines 50-66) is a trigger/routing table — useful for skill discovery but adds cognitive overhead
- `<scope>` (lines 242-257) is purely declarative scope delineation
- `<cross_references>` (lines 332-350) is a 6-row cross-reference table with relationship descriptions
- `<references>` (lines 352-402) duplicates the color quick-reference table, typography table, and logo assets table — these are lookup data, not procedures
- `<adapters>` (lines 317-330) is a lookup table

**Assessment: Partially Satisfied.** The core workflow is procedural and well-structured, but ~40% of the file is declarative/referential content that an agent doesn't need inline.

### 2. Complexity and Length ("Less is More" Check)

The file is 402 lines. Breakdown:
- YAML frontmatter: 8 lines
- `<overview>`: 7 lines (concise — good)
- `<default_behavior>`: 28 lines — explains auto-application across 6 skills + opt-out mechanism
- `<when_to_use>`: 16 lines
- `<prerequisites>`: 24 lines
- `<decision_framework>`: 31 lines (valuable — keep)
- `<workflow>`: 90 lines (the core SOP — keep)
- `<success_criteria>`: 17 lines (the preflight checklist — keep)
- `<scope>`: 15 lines
- `<anti_patterns>`: 26 lines (useful — keep)
- `<error_handling>`: 28 lines (useful — keep)
- `<adapters>`: 13 lines
- `<cross_references>`: 18 lines
- `<references>`: 50 lines

Sections that could be cut or drastically condensed:
- `<default_behavior>` — the agent doesn't need to know which other skills auto-integrate; that routing lives in those skills
- `<scope>` — redundant with `<when_to_use>`
- `<cross_references>` — routing metadata, not procedural
- `<references>` color/typography/logo tables — the agent can read `brand-tokens.json` directly; duplicating lookup data adds ~50 lines of cognitive overhead

**Assessment: Violated.** At 402 lines with ~150 lines of non-procedural content, this trends toward "comprehensive." Could be condensed to ~220-250 lines without losing procedural knowledge.

### 3. Generality ("Task-Class" Check)

The skill applies broadly to an entire class of tasks: "apply Oligon brand to any visual output." The decision framework handles multiple contexts (treatment/control, opposing, multi-category). The workflow generalizes across matplotlib, ggplot2, and document formats.

The `{baseDir}` placeholder is properly parameterized — no hardcoded absolute paths. The color hex codes are organization-specific by design, but the *patterns* (decision tree, preflight checklist, verification workflow) generalize well.

**Assessment: Satisfied.** No hardcoded filenames for single scenarios; patterns are reusable across all brand-application tasks.

### 4. Structure and Examples ("Component" Check)

- **YAML frontmatter:** Present (lines 1-8) with name, version, description, allowed-tools, brand-type, tokens-file. Description is clear and discoverable.
- **Working code examples:** Multiple — Python adapter import, JSON loading, style application, verification pattern.
- **Output format constraints:** The preflight checklist and the verification requirement ("Do not mark task complete until verification passes") act as harness constraints.

Minor issues: Frontmatter `description` is 34 words — functional but not truly "one-line." Stray `</output>` tag on line 403.

**Assessment: Satisfied.**

---

## Evaluation

### Executive Summary

**Grade:** B
**Verdict:** Needs Refinement

The skill has a strong procedural core — the 5-stage workflow, decision tree, anti-patterns, and error handling are excellent. However, ~40% of the file is declarative overhead (routing tables, cross-references, scope blocks, duplicated reference data) that doesn't help an agent execute brand-application tasks. At 402 lines, it crosses from "detailed" into "comprehensive" territory, which empirically degrades agent pass rates.

### Violation Audit

**Procedural Check:** Partially Satisfied — The `<workflow>` (Stages 1-5), `<decision_framework>`, `<anti_patterns>`, and `<error_handling>` sections are strong procedural guidance. However, `<default_behavior>` (lines 20-48), `<scope>` (lines 242-257), and `<cross_references>` (lines 332-350) are purely declarative routing/capability documentation that an executing agent does not need.

**Complexity Check:** Violated — 402 lines with ~150 lines of non-procedural content. The `<references>` section duplicates data already available in `brand-tokens.json`. The `<default_behavior>` integration table, `<scope>` in/out lists, `<cross_references>` relationship table, and `<adapters>` lookup table are all routing content that inflates the skill without adding procedural value. The frontmatter description reads like a feature list, not a task description.

**Generality Check:** Satisfied — Uses `{baseDir}` parameterization throughout; decision tree and workflow generalize across all scientific visualization tasks; no single-scenario hardcoding.

**Structure Check:** Satisfied — YAML frontmatter present with all required fields; multiple working Python code examples; verification requirement acts as harness constraint. Minor: stray `</output>` tag on line 403.

### Recommended Rewrites

**1. Frontmatter description — condense to one actionable line:**
```yaml
description: "Apply Oligon brand colors, typography, and styling to scientific figures and documents."
```

**2. Remove `<default_behavior>` entirely.** Auto-integration routing belongs in the consuming skills or a router, not in this skill. If an agent loads this skill, it's because it *needs* brand tokens — telling it "you might not need me" wastes context.

**3. Merge `<scope>` into `<when_to_use>`.** Delete the `<scope>` block — its content is redundant with the trigger conditions section.

**4. Delete `<cross_references>`.** Skill routing is the router's job. The 3-line "Typical Workflow" at the end is the only useful piece — move it to the end of `<workflow>`.

**5. Condense `<references>` to essential hex codes only:**
```markdown
<references>
## Quick Reference

| Name | HEX | Role |
|------|-----|------|
| Brand Blue | `#2DB2E8` | Hero highlight (1-2 per panel) |
| Contrast Orange | `#E8622D` | Opposing effects |
| Dark Gray | `#222222` | Primary data / control |
| Medium Gray | `#666666` | Secondary data |
| Muted Gray | `#999999` | Tertiary data |
| Medium Blue | `#158BBB` | Additional categorical |

Figures: Arial, 7-10 pt. Full spec: `tokens/brand-tokens.json`
Logo: presentations/posters only, never on journal figures.
</references>
```

**6. Remove stray `</output>` tag on line 403.**

These changes would reduce the skill from ~402 lines to ~250 lines while preserving all procedural knowledge.

### Deployment Note

When an agent needs to create a branded figure, pair this skill with `plotting-libraries` (for code patterns) and optionally `skills/shared/accessibility/` (for WCAG / CVD validation). Design-philosophy guidance now lives inside this skill's `<design_foundation>` block — no separate skill load needed. If venue-specific figure-dimension formatting is required, pair with `venue-templates` (figure_specs.md).


[FILE] SKILL.md
  diagnostics: 3

  [WARN ] description.use_when_phrase at 1:1
    message    : description should contain "Use when" phrasing
    suggestion : Start description with "Use when" to help agents match this skill to user intent.

  [WARN ] frontmatter.allowed_tools_format at 1:1
    message    : allowed-tools must be a string (space-delimited tool list)
    suggestion : Use a space-delimited string, e.g. allowed-tools: Bash(git:*) Read

  [WARN ] frontmatter.unknown_fields at 1:1
    message    : unknown frontmatter fields: version, brand-type, tokens-file
    suggestion : The spec defines: name, description, license, compatibility, metadata, allowed-tools. Remove or rename unrecognized fields.