# Failure Paths — 12 Scenarios + Recovery

Documented failure scenarios that can occur during the deep-research pipeline, with
specific recovery strategies. The orchestrator (SKILL.md) references these by ID (F1-F12).

## Phase 1 Failures (Scoping)

### F1: Research Question Non-Convergence

**Trigger:** User cannot formulate a clear, answerable RQ after 3 attempts.

**Symptoms:**
- RQ keeps shifting with each exchange
- Scope too broad to be actionable ("I want to understand cancer")
- Contradictory scope constraints

**Recovery:**
1. Provide 3 candidate RQs ranked by feasibility and specificity
2. If user rejects all 3 -> suggest switching to **socratic mode** for guided exploration
3. If socratic mode also fails (>10 rounds without convergence) -> suggest starting with
   **quick mode** on a narrow subtopic to build familiarity before scoping the full question

### F2: Insufficient Literature (<5 sources)

**Trigger:** Bibliography agent returns fewer than the minimum source threshold.

**Symptoms:**
- <5 sources after searching >=3 databases
- Search saturation reached immediately (no papers match)
- Only tangentially related papers found

**Recovery:**
1. **Expand keywords:** Add synonyms, broader MeSH terms, related pathways
2. **Broaden databases:** Add Consensus MCP and ToolUniverse fallbacks (EuropePMC, SemanticScholar)
3. **Relax date range:** Extend from 5 years to 10 years
4. **Relax inclusion criteria:** Loosen population/intervention/outcome constraints
5. If still <5 after all expansions -> report to user with recommendation:
   - "Insufficient published evidence. This may be a novel area — consider hypothesis mode."
   - Or: narrow the question to a subtopic with more literature

### F3: Methodology Mismatch

**Trigger:** Advocate identifies at Checkpoint 1 that the chosen methodology cannot
answer the research question.

**Symptoms:**
- Systematic review requested but <10 eligible studies exist
- Hypothesis mode requested but the domain is purely descriptive
- Full mode requested for a simple factual question (should be fact-check)

**Recovery:**
1. Advocate explains the mismatch with specific reasoning
2. Suggest alternative modes:
   - Systematic review with <10 studies -> suggest **lit-review** mode
   - Hypothesis for descriptive domain -> suggest **full** mode with gap analysis focus
   - Full mode for simple question -> suggest **quick** or **fact-check** mode
3. User decides; if they insist on original mode, proceed with limitations noted

## Phase 2 Failures (Investigation)

### F4: Advocate CRITICAL at Checkpoint 1

**Trigger:** Devil's advocate issues a CRITICAL severity finding after scoping.

**Symptoms:**
- RQ is fundamentally unanswerable ("What is the best drug?" without context)
- Methodology is fatally flawed for this question type
- Scope is so broad that meaningful synthesis is impossible

**Recovery:**
1. **STOP** — do not proceed to Phase 2
2. Present the advocate's specific finding and fix recommendation to the user
3. Revise the RQ/methodology per the recommendation
4. Re-run Checkpoint 1 on the revised version
5. Maximum 2 revision loops at Checkpoint 1 — if still CRITICAL, suggest scoping via socratic mode

## Phase 3 Failures (Analysis)

### F5: Ethics BLOCKED

**Trigger:** Ethics agent issues a BLOCKED verdict during Phase 5 review.

**Symptoms:**
- Fabricated reference detected
- No AI disclosure in output
- Dual-use risk High or Critical without safeguards
- Systematic misrepresentation of sources

**Recovery:**
1. **STOP** — do not deliver the output
2. Present the specific blocking condition to the user
3. Remediation path by blocking type:
   - **Fabricated reference:** Remove and replace; re-run verification on replacement
   - **Missing AI disclosure:** Compiler adds mandatory disclosure (this should never happen if compiler is working correctly)
   - **Dual-use risk:** Narrow scope to exclude dangerous content, or add Responsible Use safeguards
   - **Source misrepresentation:** Re-run synthesis with accurate source interpretation
4. After remediation, re-run ethics review before delivery

## Phase 2-4 Failures (Tool/Infrastructure)

### F6: MCP Tool Failure (Primary)

**Trigger:** PubMed MCP, bioRxiv MCP, or Consensus MCP returns an error or times out.

**Symptoms:**
- MCP tool returns error response
- Session timeout or connection failure
- Rate limiting (especially Consensus MCP)

**Recovery — cascade fallback:**

| Failed Tool | Fallback 1 | Fallback 2 | Last Resort |
|------------|-----------|-----------|------------|
| PubMed MCP `search_articles` | ToolUniverse `EuropePMC_search_articles` | ToolUniverse `SemanticScholar_search_papers` | Document gap |
| PubMed MCP `get_article_metadata` | ToolUniverse `EuropePMC_search_articles` (with DOI) | ToolUniverse `Crossref_get_work_by_doi` | Mark NOT_FOUND |
| PubMed MCP `get_full_text_article` | ToolUniverse `EuropePMC_get_fulltext_snippets` | ToolUniverse `SemanticScholar_get_pdf_snippets` | Abstract-only verification |
| bioRxiv MCP `search_preprints` | ToolUniverse `EuropePMC_search_articles` (source:PPR) | Document gap | — |
| Consensus MCP `search` | ToolUniverse `SemanticScholar_search_papers` | PubMed MCP `search_articles` | Document gap |

**Protocol:**
1. Retry the primary tool once (transient errors are common)
2. If second failure: use Fallback 1
3. If Fallback 1 fails: use Fallback 2
4. If all fail: document the gap explicitly in Methods section

### F7: ToolUniverse Session Expiry

**Trigger:** ToolUniverse `execute_tool` returns a session or authentication error.

**Symptoms:**
- "Session expired" or similar error from execute_tool
- Tool discovery works (grep_tools) but execution fails

**Recovery:**
1. Retry execute_tool once (sessions sometimes auto-renew)
2. If second failure: fall back to MCP tools for the same data type:
   - Literature search -> PubMed MCP
   - Interaction data -> Open Targets MCP `query_open_targets_graphql`
   - Expression data -> skip, note gap
3. Document the ToolUniverse outage in Methods section

### F8: >5 Consecutive MCP Failures

**Trigger:** Five or more consecutive MCP tool calls fail across any tools.

**Symptoms:**
- Systemic infrastructure issue
- Multiple different tools all failing

**Recovery:**
1. **Pause investigation** — do not continue burning retries
2. Report to user: "Multiple MCP tools are currently unavailable. Available data: [list what was gathered]."
3. Offer options:
   - Proceed with available data (reduced evidence base, noted in limitations)
   - Pause and retry later
   - Switch to a mode that requires fewer sources (quick, fact-check)

## Phase 3-5 Failures (Content Quality)

### F9: Contradictory Evidence Deadlock

**Trigger:** Synthesis agent finds sources that fundamentally contradict each other
with comparable evidence quality, making synthesis impossible.

**Symptoms:**
- Two T1 sources reach opposite conclusions
- Evidence split ~50/50 with no clear quality differential
- Methodological differences don't explain the contradiction

**Recovery:**
1. Do NOT force consensus — state the contradiction explicitly
2. Structure as: "Active controversy: [Position A] vs [Position B]"
3. Compare evidence quality, sample sizes, populations, methodology
4. Present both positions to the user at Checkpoint 3 with advocate assessment
5. In the final output, maintain the contradiction as an open question in the Discussion

### F10: Search Saturation Not Reached

**Trigger:** After maximum search iterations, <5% new papers threshold not met.

**Symptoms:**
- Each search iteration continues finding substantial new papers
- Topic is too broad or too active for bounded review

**Recovery:**
1. Check if scope is too broad — if yes, recommend narrowing at Checkpoint 2
2. If scope is appropriate but literature is vast:
   - Set a hard cap at 50 sources for full mode, 100 for systematic-review
   - Document that saturation was not reached in Methods
   - Note as a limitation: "Rapid literature growth in this area means this review is a snapshot, not comprehensive"
3. Prioritize highest-tier sources if capping

### F11: Hypothesis Mode — All Hypotheses Score Low

**Trigger:** All generated hypotheses score below 5/10 on the quality rubric.

**Symptoms:**
- No hypotheses meet testability threshold
- All hypotheses are variants of the same mechanism (low distinctiveness)
- Insufficient evidence base to ground any mechanistic hypothesis

**Recovery:**
1. Re-examine the evidence base — is this a domain where hypothesis generation
   is premature? (insufficient foundational knowledge)
2. If yes: recommend switching to **lit-review** mode to map the landscape first
3. If evidence exists but hypotheses are weak:
   - Broaden the mechanistic space (consider different biological levels)
   - Consult upstream dossier for alternative pathways (STRING, GO annotations)
   - Generate "negative hypotheses" — what mechanisms can we rule out?
4. Present low scores to user at Checkpoint 3 with honest assessment

### F12: Revision Loop Exhaustion

**Trigger:** Maximum 2 revision loops completed in Phase 6, but issues remain.

**Symptoms:**
- Advocate or ethics issues not fully resolvable with available evidence
- User feedback requires changes that conflict with available sources
- Circular revisions (fix A breaks B, fix B breaks A)

**Recovery:**
1. **Do NOT loop further** — 2 revisions is the hard limit
2. Move all unresolved issues to "Acknowledged Limitations" section
3. Present final output to user with explicit list:
   - "Resolved in revision: [list]"
   - "Acknowledged but unresolved: [list with reasons]"
4. Suggest follow-up actions:
   - "Use `peer-review` for deeper evaluation of [unresolved issue]"
   - "Additional evidence from [database/experiment] would help resolve [issue]"
