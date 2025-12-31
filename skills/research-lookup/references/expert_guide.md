# Research Lookup - Expert Guide

> Principles, decision rules, and failure modes that separate competent from excellent execution.
> Generated via expert synthesis prompt.

---

## 1. Core Principles

1. **Query Precision Over Breadth**: A specific, well-structured query outperforms multiple vague attempts. Include topic + aspect + timeframe + information type in every query.

2. **Verify Before Trust**: AI-assisted search provides candidates, not truth. Every critical fact requires primary source verification—abstracts misrepresent findings 15-20% of the time.

3. **Multi-Source Triangulation**: No single database or AI tool captures all relevant literature. Cross-reference findings across 2-3 sources before treating information as reliable.

4. **Complexity-Appropriate Tool Selection**: Match query depth to tool capability. Simple lookups waste reasoning model capacity; complex synthesis underperforms with fast search.

5. **Citation Trail, Not Endpoint**: Treat search results as starting points for citation chaining. Forward and backward citation analysis captures papers with different terminology.

## 2. Decision Framework

| Situation | Action |
|-----------|--------|
| Need quick fact or statistic | Use fast search model; verify number against primary source |
| Comparing mechanisms or trade-offs | Use reasoning model; request explicit comparison structure |
| Query returns no results | Broaden terms, try synonyms, check alternate databases |
| Query returns >50 results | Add specificity: timeframe, study type, or outcome measure |
| Need recent findings (<6 months) | Include preprint servers; note peer-review status in citations |
| Conflicting information across sources | Prioritize peer-reviewed > institutional > news; note discrepancy |
| Critical claim for manuscript | Verify via DOI lookup; read primary source abstract minimum |

## 3. Concrete Patterns

**Structured Query Construction**
- [Vague research need] → [Build: Topic + Specific Aspect + Timeframe + Study Type] → [Precise queries yield relevant results on first attempt, saving iterations]

**Reasoning Keyword Injection**
- [Need deep analysis but query reads as simple] → [Add explicit reasoning words: "compare", "explain mechanism", "analyze trade-offs"] → [Triggers appropriate model selection; ensures analytical depth]

**Citation Verification Loop**
- [Found relevant-seeming paper via AI search] → [Cross-check DOI, author names, publication year via WebSearch or CrossRef] → [Catches hallucinated citations and metadata errors before manuscript inclusion]

## 4. Failure Modes

| Mistake | Why It Fails |
|---------|--------------|
| Treating AI summaries as primary sources | AI may hallucinate citations, misrepresent findings, or conflate studies; citing without verification damages credibility |
| Using single-word queries | Returns noise; lacks specificity to identify truly relevant work |
| Ignoring publication date | Cites superseded findings; misses replication failures or methodology improvements |
| Copying AI-provided citations verbatim | 5-10% contain errors in author names, titles, or DOIs; always verify against CrossRef/DOI |
| Relying on one AI tool | Different tools have different coverage and biases; triangulation catches gaps |
| Forcing reasoning model for simple lookups | Wastes resources and time; fast search handles factual retrieval efficiently |

## 5. Anti-Patterns

- **Never** cite a paper you haven't at least read the abstract and methods of—AI summaries are insufficient
- **Never** use search results to bypass paywall access—this violates academic integrity
- **Never** present AI-synthesized summaries as your own analysis without verification and rewriting
- **Never** trust impact metrics without checking recency—high-citation papers may be outdated
- **Never** skip documenting your search strategy—reproducibility requires query transparency

## 6. Quality Signals

| Good Enough | Excellent |
|-------------|-----------|
| Returns relevant papers | Returns the *most* relevant papers for the specific question |
| Provides citation | Provides verified citation with DOI confirmed via CrossRef |
| Summarizes findings | Identifies consensus, controversies, and gaps across sources |
| Uses one search | Cross-references across 2-3 databases/tools |
| Accepts AI synthesis | Reads primary sources and confirms AI interpretation |
| Includes recent work | Explicitly notes publication dates and acknowledges literature currency |

---

## Final Synthesis

**Do This:**
- Structure queries: [topic] + [aspect] + [timeframe] + [study type]
- Verify every citation DOI before including in manuscripts
- Use reasoning keywords ("compare", "mechanism", "trade-offs") for analytical queries
- Cross-reference findings across multiple sources
- Document your search strategy for reproducibility

**Not That:**
- Vague single-word or phrase queries without structure
- Copying AI citations without DOI verification
- Using reasoning models for simple fact lookups (wastes resources)
- Relying on a single AI tool or database
- Presenting AI summaries as primary source analysis

**When In Doubt:** Verify the claim against the primary source—AI tools are search assistants, not truth oracles.

**Quality Check:**
1. Is my query specific enough to return <50 highly relevant results?
2. Have I verified the DOI and key metadata for every citation I'll use?
3. Did I cross-reference critical findings across at least two sources?
4. Am I using the appropriate model (fast vs reasoning) for query complexity?
5. Have I documented my search strategy for reproducibility?
6. Have I read at least the abstract of every paper I cite?
