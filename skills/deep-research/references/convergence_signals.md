# Biomedical Convergence Signals (B1-B5)

Convergence signals track research readiness during Socratic mode dialogue. Each signal
represents a dimension of maturity in the user's thinking about their biomedical research
question. The mentor agent monitors these signals to determine when the dialogue has
reached productive convergence.

## Signal Definitions

### B1: Target Clarity

**Definition:** The user identifies a specific gene, protein, drug, pathway, or disease
with correct nomenclature and unambiguous scope.

**How to detect:**
- User uses official gene symbols (HGNC) or drug names (INN), not colloquial terms
- User distinguishes between the gene, protein, and pathway levels
- If entity has collision risk (e.g., ACE = enzyme vs. gene vs. inhibitor class), the user
  has resolved the ambiguity explicitly
- User can name the specific molecular entity without hedging ("maybe EGFR or something related")

**Examples:**
- Active: "I want to investigate KRAS G12C resistance mechanisms in NSCLC"
- Not active: "I'm interested in cancer drug resistance"

### B2: Mechanism Specificity

**Definition:** The user describes a causal chain, not just a statistical association or
a general observation.

**How to detect:**
- User articulates a directional relationship: A causes B through mechanism C
- User distinguishes correlation from causation unprompted
- User can specify the biological level of the mechanism (molecular, cellular, tissue, organism)
- If challenged with contradictory data, user can refine the mechanism rather than abandon it

**Examples:**
- Active: "GLP-1 agonists reduce neuroinflammation by downregulating NF-kB signaling
  in microglia, which decreases amyloid-beta phagocytosis impairment"
- Not active: "GLP-1 drugs seem to help with Alzheimer's somehow"

### B3: Falsifiability Defined

**Definition:** The user can name a specific experimental result that would disprove their
hypothesis or invalidate their research question.

**How to detect:**
- User can complete the sentence: "My hypothesis would be wrong if..."
- The falsifying condition is specific and experimentally testable (not vague)
- User has considered what negative results would mean, not just positive results
- The falsifying condition is genuinely threatening to the hypothesis (not a trivial edge case)

**Examples:**
- Active: "If KRAS G12C mutant cells show the same resistance pattern with and without
  SOS1 inhibition, then SOS1-mediated reactivation is not the primary resistance mechanism"
- Not active: "I guess if no papers support it, then maybe it's wrong"

### B4: Scope Stability

**Definition:** The target-disease-mechanism triple has not substantially changed for
3 consecutive dialogue rounds.

**How to detect:**
- Track the core research question across turns
- The fundamental question (not just wording refinements) has been stable for 3 rounds
- User is deepening understanding of the same question, not pivoting to a new one
- Minor refinements (adding specificity) count as stable; changing the target gene does not

**Tracking protocol:**
- Round N: Record the core triple (target, disease, mechanism)
- Round N+1: Compare to N — same core? (refinements OK)
- Round N+2: Compare to N+1 — same core?
- If same for 3 consecutive rounds -> B4 active

### B5: Self-Calibration

**Definition:** The user's predictions about database evidence become more accurate
over the course of the dialogue.

**How to detect (requires SCR protocol active):**
- Compare early commitments to later commitments
- Later predictions better match actual evidence and known literature
- User's hedging becomes more appropriately calibrated (neither overconfident nor excessively cautious)
- User starts voluntarily acknowledging uncertainty in areas they previously assumed certainty

**Examples:**
- Active: Early commitment: "STRING should show strong KRAS-SOS1 interaction"
  (verified: STRING score 0.95 — accurate). Later commitment: "I'd expect moderate
  GTEx expression in lung tissue" (verified: GTEx TPM ~15 in lung — accurate calibration)
- Not active: User consistently overestimates evidence strength or makes claims
  contradicted by database queries

**Note:** B5 is only trackable when SCR is enabled. If SCR is disabled by the user,
B5 is marked as N/A and convergence proceeds with B1-B4 only.

## Convergence Rules

| Condition | Status | Action |
|-----------|--------|--------|
| 3+ signals active | **CONVERGED** | Compile INSIGHTs, produce Research Plan Summary |
| All 5 active | **FULLY CONVERGED** | End immediately with full summary |
| B1-B4 active, B5 N/A | **CONVERGED** | Include calibration advisory in summary |
| B1-B4 active, B5 inactive | **CONVERGED** | Include calibration note: "self-assessment accuracy has room for growth" |
| 10+ rounds, no new INSIGHT | **STAGNATION** | Suggest switching to full mode |
| >40 total turns | **TIME LIMIT** | Force-complete with available INSIGHTs |

## Signal Tracking Format

The mentor tracks signals internally. At dialogue end, report:

```markdown
### Convergence Status
| Signal | Status | Evidence |
|--------|--------|----------|
| B1: Target Clarity | Active/Inactive | [brief note] |
| B2: Mechanism Specificity | Active/Inactive | [brief note] |
| B3: Falsifiability Defined | Active/Inactive | [brief note] |
| B4: Scope Stability | Active/Inactive | [brief note] |
| B5: Self-Calibration | Active/Inactive/N-A | [brief note] |
| **Overall** | CONVERGED / NOT YET / STAGNATION | [X/5 signals] |
```
