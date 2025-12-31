# Common Pitfalls

> Anti-patterns to avoid when using the research-paper-summarizer skill

## 1. Skipping Article Type Selection

**Problem:** Using general summarizer for specialized content (compbio, cellmolbio).

**Solution:** Always ask user to confirm article type before processing.

**Why it matters:** Each summarizer is optimized for its domain with specific prompts and section structures.

## 2. Ignoring Page Count Threshold

**Problem:** Using Standard Mode for papers >12 pages, causing context exhaustion.

**Solution:** Let the skill auto-detect; trust the 12-page threshold.

**Why it matters:** Long papers can exceed context limits, leading to truncated or incomplete summaries.

## 3. Summarizing Away Statistics

**Problem:** Replacing "p = 0.003" with "statistically significant."

**Solution:** Preserve ALL numerical data exactly as reported.

**Why it matters:** Researchers need exact values for meta-analysis, replication, and critical evaluation.

**Examples:**
```
❌ Bad:  "showed significant improvement"
✅ Good: "showed significant improvement (p = 0.003, n=24/group)"

❌ Bad:  "moderate effect size"
✅ Good: "moderate effect size (Cohen's d = 0.65, 95% CI: 0.42–0.88)"
```

## 4. Missing Figure References

**Problem:** Summary mentions findings without linking to source figures.

**Solution:** Include figure_ref for every finding with supporting data.

**Why it matters:** Readers need to verify claims against primary evidence.

## 5. Incomplete Chunked Processing

**Problem:** Stopping when one subagent fails.

**Solution:** Use recovery workflow; check for PENDING markers and resume.

**Why it matters:** Partial summaries miss critical information and may be misleading.

## 6. Paraphrasing Technical Terminology

**Problem:** Replacing "CRISPR-Cas9 knockout" with "gene editing technique."

**Solution:** Use exact technical terminology from the paper.

**Why it matters:** Precision matters in scientific communication; paraphrasing can change meaning.

**Examples:**
```
❌ Bad:  "gene editing technique"
✅ Good: "CRISPR-Cas9 knockout"

❌ Bad:  "protein analysis"
✅ Good: "Western blot analysis"

❌ Bad:  "cell death"
✅ Good: "apoptosis" (or "necrosis" if that's what the paper said)
```

## 7. Omitting Negative Results

**Problem:** Only highlighting positive findings.

**Solution:** Include all results, especially null/negative findings with statistical context.

**Why it matters:** Negative results are scientifically important and prevent publication bias.

**Example:**
```
❌ Incomplete: "DFMO reduced tumor growth"
✅ Complete: "DFMO reduced tumor growth in Kelly cells (60% reduction, p<0.001)
              but had no effect in SK-N-AS cells (p=0.34, n=8/group)"
```

## 8. Ignoring Author Hedging

**Problem:** Converting "may suggest" to "demonstrates."

**Solution:** Preserve conditional language exactly as authors stated.

**Why it matters:** Authors use hedging for a reason; removing it overclaims their findings.

**Examples:**
```
❌ Overclaimed: "This demonstrates that X causes Y"
✅ Accurate:    "This suggests that X may contribute to Y"

❌ Overclaimed: "The treatment works"
✅ Accurate:    "The treatment showed promise in this model system"
```

## 9. Generic Critical Analysis

**Problem:** Writing vague criticisms like "more research is needed."

**Solution:** Be specific about what experiments, controls, or analyses are missing.

**Examples:**
```
❌ Vague:    "Sample size was limited"
✅ Specific: "n=12 per group may be underpowered to detect the 15% effect
              size reported; power analysis suggests n=45 needed"

❌ Vague:    "Controls were inadequate"
✅ Specific: "Missing positive control compound (e.g., staurosporine) to
              validate apoptosis assay sensitivity"
```

## 10. Forgetting to Save Output

**Problem:** Generating summary content but not saving to file.

**Solution:** Always save markdown summary to source document directory before offering visual outputs.

**File naming pattern:**
```
Source: smith2024_cancer.pdf
Output: smith2024_cancer_summary.md
```
