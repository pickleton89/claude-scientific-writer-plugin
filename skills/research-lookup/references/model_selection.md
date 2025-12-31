# Model Selection Guide

> Intelligent selection between Sonar Pro Search and Sonar Reasoning Pro based on query complexity.

---

## Model Types

### Sonar Pro Search (`perplexity/sonar-pro-search`)

| Attribute | Value |
|-----------|-------|
| **Use Case** | Straightforward information lookup |
| **Response Time** | 5-15 seconds |
| **Cost** | Lower cost per query |

**Best For:**
- Simple fact-finding queries
- Recent publication searches
- Basic protocol lookups
- Statistical data retrieval
- Citation finding for specific papers

### Sonar Reasoning Pro (`perplexity/sonar-reasoning-pro-online`)

| Attribute | Value |
|-----------|-------|
| **Use Case** | Complex analytical queries requiring deep reasoning |
| **Response Time** | 15-45 seconds |
| **Cost** | Higher cost per query |

**Best For:**
- Comparative analysis ("compare X vs Y")
- Synthesis of multiple studies
- Evaluating trade-offs or controversies
- Explaining mechanisms or relationships
- Critical analysis and interpretation
- Theoretical frameworks
- Multi-faceted relationships

---

## Automatic Complexity Detection

The skill analyzes query text and assigns complexity scores:

### Reasoning Keywords (3 points each)

| Category | Keywords |
|----------|----------|
| Analytical | `compare`, `contrast`, `analyze`, `analysis`, `evaluate`, `critique` |
| Comparative | `versus`, `vs`, `vs.`, `compared to`, `differences between`, `similarities` |
| Synthesis | `meta-analysis`, `systematic review`, `synthesis`, `integrate` |
| Causal | `mechanism`, `why`, `how does`, `how do`, `explain`, `relationship`, `causal relationship`, `underlying mechanism` |
| Theoretical | `theoretical framework`, `implications`, `interpret`, `reasoning` |
| Debate | `controversy`, `conflicting`, `paradox`, `debate`, `reconcile` |
| Trade-offs | `pros and cons`, `advantages and disadvantages`, `trade-off`, `tradeoff`, `trade offs` |
| Complexity | `multifaceted`, `complex interaction`, `critical analysis` |

### Additional Scoring

| Indicator | Points |
|-----------|--------|
| Multiple question marks | 2 points per `?` |
| Clause indicators (`and`, `or`, `but`, `however`, `whereas`, `although`) | 1.5 points each |
| Query length >150 characters | 1 point |

### Threshold

**Score >= 3 points** triggers Sonar Reasoning Pro.

A single strong reasoning keyword (compare, explain, analyze) triggers the reasoning model.

---

## Query Classification Examples

### Sonar Pro Search (straightforward lookup)

```
"Recent advances in CRISPR gene editing 2024"
"Prevalence of diabetes in US population"
"Western blot protocol for protein detection"
"Global AI adoption in healthcare statistics 2024"
```

### Sonar Reasoning Pro (complex analysis)

```
"Compare and contrast mRNA vaccines vs traditional vaccines for cancer treatment"
"Explain the mechanism underlying the relationship between gut microbiome and depression"
"Analyze the controversy surrounding AI in medical diagnosis and evaluate trade-offs"
"Compare the efficacy and safety of mRNA vaccines vs traditional vaccines"
```

---

## Manual Override

Force a specific model when automatic selection doesn't match your needs:

### Python API

```python
# Force Sonar Pro Search for fast lookup
research = ResearchLookup(force_model='pro')

# Force Sonar Reasoning Pro for deep analysis
research = ResearchLookup(force_model='reasoning')

# Automatic selection (default)
research = ResearchLookup()
```

### Command Line

```bash
# Force Sonar Pro Search
python {baseDir}/scripts/research_lookup.py "your query" --force-model pro

# Force Sonar Reasoning Pro
python {baseDir}/scripts/research_lookup.py "your query" --force-model reasoning

# Automatic (default)
python {baseDir}/scripts/research_lookup.py "your query"

# Save output to file
python {baseDir}/scripts/research_lookup.py "your query" -o results.txt

# JSON output
python {baseDir}/scripts/research_lookup.py "your query" --json
```

---

## Cost Optimization

### Automatic Selection Benefits

- Saves costs by using Sonar Pro Search for straightforward queries
- Reserves Sonar Reasoning Pro for queries that truly benefit from deeper analysis
- Optimizes balance between cost and quality

### Override Use Cases

| Scenario | Recommended Model |
|----------|-------------------|
| Budget constrained, speed priority | Force `pro` |
| Critical research requiring maximum depth | Force `reasoning` |
| Methods section queries | `pro` (protocol lookup) |
| Discussion section synthesis | `reasoning` (analysis) |

### Strategy for Literature Reviews

1. Start with Sonar Pro Search for breadth (gather papers)
2. Use Sonar Reasoning Pro for synthesis (analyze and compare)
3. Trust automatic selection for most use cases
4. If Pro Search lacks depth, rephrase query with reasoning keywords
