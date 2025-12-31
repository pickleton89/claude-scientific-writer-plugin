# Skill Template

> Standard structure for deterministic skill definitions
> Version: 1.0.0
> Based on: statistical-analysis, reproducible-research, code-documentation patterns

---

## Template Usage

Copy this template when creating or refactoring a skill. Replace all `{{PLACEHOLDER}}` values and remove sections marked `[OPTIONAL]` if not applicable.

---

```markdown
---
name: {{skill-name}}
version: 1.0.0
description: "{{One-line description of what this skill does}}"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# {{Skill Name}}

<overview>
{{2-3 sentences describing the skill's purpose and primary use case. Be specific about what outputs it produces.}}
</overview>

<when_to_use>
## Trigger Conditions

Use this skill when:
- {{Trigger condition 1 - be specific}}
- {{Trigger condition 2}}
- {{Trigger condition 3}}

Do NOT use this skill when:
- {{Anti-trigger 1 - redirect to appropriate skill}}
- {{Anti-trigger 2}}
</when_to_use>

<decision_framework>
## Decision Matrix

{{Choose the appropriate format based on skill complexity}}

### Option A: Simple Table

| Condition | Action |
|-----------|--------|
| {{Condition 1}} | → {{Action 1}} |
| {{Condition 2}} | → {{Action 2}} |
| {{Condition 3}} | → {{Action 3}} |

### Option B: Multi-Factor Matrix

| Factor 1 | Factor 2 | Factor 3 | → Recommendation |
|----------|----------|----------|------------------|
| {{Value}} | {{Value}} | {{Value}} | {{Action}} |
| {{Value}} | {{Value}} | {{Value}} | {{Action}} |

### Option C: ASCII Decision Tree

```
{{Starting question}}
│
├─ Yes → {{Next question or action}}
│         │
│         ├─ Yes → {{Action A}}
│         │
│         └─ No → {{Action B}}
│
└─ No → {{Alternative path}}
         │
         └─ {{Action C}}
```

</decision_framework>

<workflow>
## Workflow

### Stage 1: {{Stage Name}}

**Objective:** {{What this stage accomplishes}}

**Steps:**
1. {{Step 1 with specific action}}
2. {{Step 2 with specific action}}
3. {{Step 3 with specific action}}

**Exit Criteria:**
- [ ] {{Measurable criterion 1}}
- [ ] {{Measurable criterion 2}}
- [ ] {{Measurable criterion 3}}

---

### Stage 2: {{Stage Name}}

**Objective:** {{What this stage accomplishes}}

**Steps:**
1. {{Step 1}}
2. {{Step 2}}

**Exit Criteria:**
- [ ] {{Criterion}}
- [ ] {{Criterion}}

---

### Stage 3: {{Stage Name}}

**Objective:** {{What this stage accomplishes}}

**Steps:**
1. {{Step 1}}
2. {{Step 2}}

**Exit Criteria:**
- [ ] {{Criterion}}
- [ ] {{Criterion}}

</workflow>

<success_criteria>
## Success Criteria

**Quantitative Thresholds:**

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| {{Metric 1}} | {{value}} | {{value}} | {{value}} |
| {{Metric 2}} | {{value}} | {{value}} | {{value}} |
| {{Metric 3}} | {{value}} | {{value}} | {{value}} |

**Completion Checklist:**
- [ ] {{Criterion 1 with measurable threshold}}
- [ ] {{Criterion 2 with measurable threshold}}
- [ ] {{Criterion 3 with measurable threshold}}
- [ ] {{Criterion 4 with measurable threshold}}
- [ ] {{Criterion 5 with measurable threshold}}

</success_criteria>

<scope>
## Scope

**In Scope:**
- {{Capability 1}}
- {{Capability 2}}
- {{Capability 3}}
- {{Capability 4}}

**Out of Scope** (use specialized resources):
- {{Excluded item 1}} → use `{{alternative-skill}}`
- {{Excluded item 2}} → use `{{alternative-skill}}`
- {{Excluded item 3}} → external tool/resource

</scope>

<anti_patterns>
## Common Pitfalls

### 1. {{Pitfall Name}}

**Anti-pattern:**
```
{{Example of what NOT to do}}
```

**Solution:**
```
{{Example of correct approach}}
```

---

### 2. {{Pitfall Name}}

**Anti-pattern:**
{{Description of problematic behavior}}

**Solution:**
{{Correct approach with specific guidance}}

---

### 3. {{Pitfall Name}}

**Anti-pattern:**
{{Description}}

**Solution:**
{{Correction}}

</anti_patterns>

<templates>
## Output Templates

[OPTIONAL - Include if skill produces structured outputs]

### Template 1: {{Template Name}}

```{{format}}
{{Template content with placeholders}}

{{SECTION_TITLE}}:
{{content}}

{{ANOTHER_SECTION}}:
- {{item 1}}
- {{item 2}}
```

### Template 2: {{Template Name}}

```{{format}}
{{Template content}}
```

</templates>

<cross_references>
## Cross-References

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

### Extends
[OPTIONAL - Use if this skill inherits from a foundational skill]

- `{{parent-skill}}` - inherits {{specific principles or patterns}}

### Uses (Input From)
[List skills that provide input to this skill]

| Skill | Relationship |
|-------|-------------|
| `{{skill-name}}` | {{What this skill receives from it}} |
| `{{skill-name}}` | {{Relationship}} |

### Feeds (Output To)
[List skills that receive output from this skill]

| Skill | Relationship |
|-------|-------------|
| `{{skill-name}}` | {{What this skill provides to it}} |
| `{{skill-name}}` | {{Relationship}} |

### Related
[List skills with non-directional relationships]

| Skill | Relationship |
|-------|-------------|
| `{{skill-name}}` | {{How they relate - e.g., "Alternative for X", "Shared framework"}} |
| `{{skill-name}}` | {{Relationship}} |

</cross_references>

<references>
## Reference Documents

[OPTIONAL - List supplementary reference files in `references/` subdirectory]

| Document | Purpose |
|----------|---------|
| `references/{{filename}}.md` | {{What it contains}} |
| `references/{{filename}}.md` | {{What it contains}} |

</references>
```

---

## Checklist for Skill Authors

### Structure & Content Checklist

Before finalizing a skill, verify:

- [ ] **XML Tags**: All major sections wrapped in semantic tags
- [ ] **Decision Framework**: Clear condition → action mappings
- [ ] **Numbered Workflow**: Stages with explicit exit criteria
- [ ] **Quantitative Thresholds**: No undefined qualitative terms
- [ ] **Scope Boundaries**: Clear in/out of scope lists
- [ ] **Anti-patterns**: At least 3 common pitfalls with solutions
- [ ] **Cross-references**: Links to related skills
- [ ] **Templates**: Output formats defined (if applicable)

### Skill Integration Checklist

When creating a new skill, verify ecosystem integration:

- [ ] **Extends visual-design?** Any visual/presentation skill should extend `visual-design`
- [ ] **Input skills identified**: What skills provide data or context to this skill?
- [ ] **Output skills identified**: What skills consume output from this skill?
- [ ] **Bidirectional cross-references**: Related skills updated to reference this skill
- [ ] **Added to SKILL_ROUTER.md**: Decision tree updated for skill selection
- [ ] **QUANTIFICATION_THRESHOLDS.md**: Quality metrics added if skill produces measurable outputs

---

## Quality Scoring Dimensions

Skills are evaluated on 8 dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Structure | 15% | XML semantic tags, consistent formatting |
| Decision Framework | 20% | Clear routing logic, decision matrices |
| Workflow | 15% | Numbered stages with transitions |
| Quantification | 15% | Measurable thresholds, no vague terms |
| Scope | 10% | Clear boundaries, appropriate redirects |
| Anti-patterns | 10% | Common pitfalls documented |
| Templates | 10% | Structured output formats |
| Cross-references | 5% | Integration with skill ecosystem |

**Target Score:** 8.5/10 or higher
