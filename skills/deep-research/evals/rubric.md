# Deep-research eval rubric — LLM-as-judge (Phase 0)

This is the single judge prompt the eval harness uses to score a finished
`deep-research` run. Following Anthropic's
[multi-agent research post](https://www.anthropic.com/engineering/multi-agent-research-system),
we use **one** judge call with **one** rubric (a single judge aligns with human
judgment better than several specialized judges) and we evaluate the **end state**
— the final report plus its evidence-pinned sidecars — **not** the search path
(different valid paths reach the same goal).

`run_eval.py` reads the template between the sentinel comments below, substitutes
the `{{placeholder}}` tokens with the report + sidecar contents, and sends it to
the judge model via the Claude Code CLI (`claude -p --output-format json`).

## Dimensions (each scored 0.0–1.0)

| Dimension | Definition | 0.0 | 0.5 | 1.0 |
|---|---|---|---|---|
| **factual_accuracy** | Do the report's claims match what the sidecars/sources actually support? | Multiple claims contradicted or unsupported | Mostly supported, some overstatement | Every claim traceable to sidecar evidence |
| **citation_accuracy** | Does every cited source exist in the sources sidecar, and does each citation support the claim it's attached to? | Fabricated or misattributed citations | Citations exist but some weakly support claims | All citations resolve and support their claims |
| **completeness** | Are all facets the question requires (mode-appropriate) addressed? | Major aspects missing | Core covered, gaps remain | All expected facets addressed |
| **source_quality** | Does the report rely on primary/high-tier sources over low-quality secondaries (content farms, predatory venues)? | Dominated by weak/secondary sources | Mixed quality | Primary > review > grey-lit ordering respected |
| **tool_efficiency** | Given the search log, were appropriate databases used a reasonable number of times for this mode? | Wrong/too few or wastefully many calls | Adequate | Right tools, right depth for the mode |

## Scoring

- Each dimension: **0.0–1.0** (two decimals).
- **overall**: a single **0.0–1.0** holistic score (not necessarily the mean).
- **pass**: `true` if `overall >= 0.70` **and** no single dimension `< 0.40`; else `false`.

The runner records the judge's `scores`, `overall`, `pass`, and `rationale`
verbatim alongside run metadata in `results/{query_id}.json`.

## Judge prompt template

Placeholders are filled by `run_eval.py`. Keep the placeholder names
(`{{research_question}}`, `{{mode}}`, `{{report}}`, `{{sources_json}}`,
`{{grading_json}}`, `{{synthesis_json}}`, `{{advocate_json}}`) **stable** — the
runner substitutes them by exact string match. Sidecars absent for a mode are
substituted with `(not provided in this mode)`.

<!-- JUDGE_PROMPT_TEMPLATE_START -->
You are an expert research-quality judge evaluating an AI-generated research report produced by the `deep-research` skill. Judge the END STATE (the final report plus its evidence-pinned sidecars), NOT the search path taken — different valid paths can reach the same goal.

RESEARCH QUESTION:
{{research_question}}

MODE: {{mode}}

REPORT (markdown):
{{report}}

SOURCES SIDECAR (ground-truth bibliography + search log, JSON):
{{sources_json}}

GRADING SIDECAR (evidence tiers + verification, JSON):
{{grading_json}}

SYNTHESIS SIDECAR (themes / gaps / hypotheses, JSON):
{{synthesis_json}}

ADVOCATE SIDECAR (adversarial findings, JSON):
{{advocate_json}}

Score each dimension from 0.0 to 1.0 (two decimals):
1. factual_accuracy — do the report's claims match what the sidecars/sources actually support? Penalize unsupported or overstated claims.
2. citation_accuracy — does every cited source exist in the sources sidecar, and does each citation actually support the claim it is attached to? Penalize fabricated or misattributed citations.
3. completeness — are all facets the question requires addressed, given the report's mode and scope? Penalize missing major aspects.
4. source_quality — does the report rely on primary / high-tier sources over low-quality secondary ones (content farms, predatory venues)? Reward a primary > review > grey-lit ordering.
5. tool_efficiency — given the search log, were appropriate databases used a reasonable number of times for this mode (neither too few nor wastefully many)?

Then provide:
- overall — a single 0.0-1.0 score (holistic, not necessarily the mean).
- pass — true if overall >= 0.70 AND no dimension < 0.40, else false.
- rationale — 2-4 sentences citing specific evidence from the report / sidecars.

Respond with STRICT JSON ONLY — no markdown fences, no prose before or after — exactly this shape:
{"scores":{"factual_accuracy":0.0,"citation_accuracy":0.0,"completeness":0.0,"source_quality":0.0,"tool_efficiency":0.0},"overall":0.0,"pass":true,"rationale":"..."}
<!-- JUDGE_PROMPT_TEMPLATE_END -->
