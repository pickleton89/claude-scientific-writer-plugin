---
name: paperclip
description: Search and read full-text biomedical papers from PubMed Central, bioRxiv, medRxiv, and arXiv, FDA/regulatory documents, and clinical trials using the paperclip CLI.
---

# Paperclip

A virtual filesystem of full-text biomedical papers from PubMed Central, bioRxiv, medRxiv, and arXiv, plus FDA/regulatory documents and clinical trials.

Treat it like a mounted drive. Papers live at `/papers/<id>/` Ã¢ÂÂ use standard bash patterns to navigate, read, search, and extract.
## Virtual Filesystem Layout

```
/papers/          3.4M+ papers (PMC, bioRxiv, medRxiv, arXiv)
/fda/             217K+ FDA regulatory documents (US FDA, Japan PMDA, EU EPAR)
/trials/          110K+ clinical trial protocols and regulatory reviews
```

All document types follow the same layout: `meta.json`, `content.lines`, `sections/`, `figures/`.
IDs: `fda_` (FDA docs), `tri_` (trial docs), `PMC` (papers), `bio_`/`med_`/`arx_` (preprints).

## Paper Layout

`/papers/<id>/`: `meta.json` (metadata), `content.lines` (full text, line-numbered), `sections/` (named files), `figures/`, `supplements/`.

IDs: `PMC` (PubMed Central), `bio_` (bioRxiv), `med_` (medRxiv), `arx_` (arXiv).
`/.gxl/` is writable scratch. `/papers/` is read-only.

## Workflow

Default to `map` for multi-paper questions Ã¢ÂÂ it reads each paper via a lightweight model. After map, synthesize directly; don't re-read papers individually.

1. **Find**: `search "topic"` Ã¢ÂÂ present results
2. **One paper**: `head`/`grep`/`scan` on `/papers/<id>/`
3. **Many papers**: `search -n 10` Ã¢ÂÂ `map --from ID "q"` Ã¢ÂÂ synthesize
4. **Stats**: `sql "SELECT ..."`

## CRITICAL: Source Selection for Search

**You MUST add `-s fda` or `-s trials` to search when the question involves regulatory or clinical trial content. Without it, search only returns biomedical papers.**

| User asks about... | You MUST search with |
|---|---|
| FDA, drug approval, NDA, BLA, drug label, regulatory review | `search "query" -s fda` |
| Clinical trials, NCT, study protocol, Phase 1/2/3 | `search "query" -s trials` |
| PMDA, EMA, EPAR, Japan/EU regulatory | `search "query" -s trials -T pmda` or `-T epar` |
| Biomedical research papers | `search "query"` (no flag â default) |

**Example:** "Find FDA submissions about AI mammography" â `search "AI mammography cancer detection 510k" -s fda -n 10`

If the question spans both domains, run **both** searches:
```
search "drug name" -s fda -n 10      # FDA regulatory docs
search "drug name" -s trials -n 10   # clinical trial protocols
```

## Path Routing by Document Type

**Paths MUST match the document type. Using the wrong root path will fail.**

| Document type | Root path | Example |
|--------------|-----------|---------|
| Papers (PMC, bioRxiv, medRxiv, arXiv) | `/papers/` | `/papers/bio_dca47d15/content.lines` |
| FDA regulatory documents | `/fda/` | `/fda/fda_585eacf455e8/content.lines` |
| Clinical trials | `/trials/` | `/trials/tri_1159d009c7c5/content.lines` |

**NEVER use `/papers/` for FDA, trials, or patent documents.** An `fda_` ID goes under `/fda/`, a `tri_` ID goes under `/trials/`.

## Examples

```
search "CRISPR base editing delivery"
head -40 /papers/bio_dca47d15/content.lines
cat /papers/bio_dca47d15/meta.json
grep -i "off-target" /papers/bio_dca47d15/content.lines
scan /papers/bio_dca47d15/content.lines "CRISPR" "off-target"

# FDA documents use /fda/ NOT /papers/
search "pembrolizumab" -s fda
cat /fda/fda_585eacf455e8/meta.json
grep "efficacy" /fda/fda_585eacf455e8/content.lines

# Trials use /trials/ NOT /papers/
cat /trials/tri_1159d009c7c5/meta.json
```

Use `head -N`, section files, or `grep`/`scan` over `cat` on full `content.lines`.
Pipes: `bash 'search "protein design" | grep -i "diffusion"'`.

## Sources

Default search covers PMC, bioRxiv, medRxiv, arXiv.
- `-s abstracts` for broader abstract-only corpus (no full text).
- `-s fda` for regulatory documents (defaults to US FDA). Narrow with `-s fda/jp` (PMDA), `-s fda/eu` (EMA).
- `-s trials` for all clinical trial registries. Narrow with `-s trials/us`, `-s trials/cn`, `-s trials/jp`, `-s trials/eu`.

**Scoped search with virtual directories** (equivalent to `-s` flags):
```
```

**Source selection rule:** When the user specifies a domain or literature type (e.g. "trials", "regulatory", "FDA", "clinical"), always use the corresponding `-s` flag or virtual directory path rather than running an unscoped search across all sources. Run parallel targeted searches when multiple specific sources are needed. Only omit `-s` for genuinely exploratory queries with no domain signal.

Use specific query terms to avoid false positives (e.g. `"GLP-1 receptor agonist"` not `"GLP-1"` which matches "Good Laboratory Practice" in regulatory docs).

## Citations

Cite **[1]**, **[2]** inline. End with:

```
--------
REFERENCES
[1] Authors. "Title." *Journal* vol, pages (year). doi:XX
    https://citations.gxl.ai/papers/<doc_id>#L<n>
```

Never expose doc_id in prose. Cite every factual claim.

# Commands

Run `<cmd> --help` for full usage on any command.

## Search & Discovery

| Command | Description |
|---------|-------------|
| `paperclip search QUERY` | Semantic + keyword search. Key opts: `-n`, `-s SOURCE`, `-e`, `--since`, `--sort`, `--author`, `--journal`, `--year` |
| `paperclip grep PATTERN PATH` | Regex search across corpus or within a paper |
| `paperclip lookup FIELD VALUE` | Find by metadata: doi, author, title, pmc, pmid, journal |
| `paperclip sql "SELECT ..."` | SQL on `documents` table (200-row limit) |

## Reading & Analysis

| Command | Description |
|---------|-------------|
| `paperclip cat`, `head`, `tail`, `ls` | Read files, list directories |
| `paperclip scan FILE "p1" "p2"` | Multi-pattern search in a file |
| `paperclip ask-image PATH "q"` | Analyze figure with vision. `--fn describe` / `--fn extract-data` |
| `paperclip map --from ID "q"` | LLM reader across search results Ã¢ÂÂ answers per paper |
| `paperclip reduce --from ID "q"` | Synthesize map results. Strategies: summarize, table, themes |
| `paperclip results [ID]` | View saved search/map results. `--list` to see all |

## Text Processing

`sed`, `awk`, `sort`, `cut`, `tr`, `jq` Ã¢ÂÂ standard tools, pipes via `bash '...'`.

## Paper Repositories

Git-like collections for curated literature. Use repos whenever a task involves sustained analysis across multiple papers (reviews, meta-analyses, comparisons, evidence synthesis).

| Command | Description |
|---------|-------------|
| `paperclip init`, `repo`, `checkout` | Create, list, switch repos |
| `paperclip add`, `remove` | Add/remove papers |
| `paperclip commit`, `log`, `diff` | Version history |
| `paperclip branch`, `merge` | Branching |
| `paperclip annotate`, `cite`, `export` | Notes, citations, export (bib/csv/md) |
| `paperclip import` | Import from .bib/.ris or paper refs |
| `paperclip library` | Personal paper library |

### Repo-scoped search and map

When checked out to a repo, `search` and `map` automatically scope to the repo's papers:

```
checkout my-review
search "CRISPR delivery"    # searches only within the repo's papers
map "What methods were used?" # maps over all repo papers (no --from needed)
```

To search the full corpus while a repo is active, use `--corpus`:

```
search --corpus "CRISPR delivery"   # full corpus search (ignores repo scope)
map --corpus "What methods?"        # requires --from (normal behavior)
```

### Annotate and commit discipline

Repos track analysis history. Follow these rules:

- **Annotate relevance when adding papers.** When adding a paper via `add` or after search auto-adds it, annotate *why* it's relevant to the user's query. Use `add PMC123 --note "RCT on saline rinse for colds, reports illness duration"` or `annotate PMC123 "Relevant: only RCT directly testing hypertonic saline for common cold (not COVID)"`. This makes the curation rationale visible Ã¢ÂÂ a reader of the repo should understand why each paper was included without re-reading it.
- **Annotate papers with findings.** After `map` or manual reading extracts key data (effect sizes, methods, conclusions), write those back with `annotate`. This makes findings persistent and visible in `repo` output.
- **Commit at milestones.** Commit after each meaningful step: initial curation, after adding annotations from a map pass, after removing irrelevant papers, after a round of analysis. Use descriptive messages.
- **Use `reduce` after `map`.** Don't manually synthesize map results when `reduce --from m_xxx --strategy table` can produce a structured summary. Use `reduce` first, then refine in your response.

Failure mode to avoid: running `map`, synthesizing the answer in prose, and never writing annotations or committing Ã¢ÂÂ this leaves no durable record in the repo.

## Regulatory & Clinical Trials

Browse and search regulatory documents and clinical trials using virtual directory paths:

```
ls /fda                              # List regional sub-directories
ls /fda/us                           # List US FDA documents (top 20 + total count)
ls /clinicaltrials                   # List regional sub-directories
ls /trials/                          # List trial documents
cat /fda/fda_XXXX/meta.json           # Read FDA document metadata
cat /trials/tri_XXXX/meta.json
head -40 /trials/tri_XXXX/content.lines
grep "efficacy" /fda/fda_XXXX/content.lines
search "pembrolizumab" -s fda       # Search FDA docs
search "breast cancer" -s trials  # Search trial protocols
```

| Source | Content | IDs |
|--------|---------|-----|
| `-s fda` | US FDA reviews, Japan PMDA, EU EPAR (217K docs) | `fda_XXXXXXXXXXXX` |
| `-s trials` | ClinicalTrials.gov protocols, PMDA, EPAR reviews (110K docs) | `tri_XXXXXXXXXXXX` |
| `-T pmda` | Japan PMDA only | `tri_*` |
| `-T epar` | EU EPAR only | `tri_*` |

Search across sources with `-s` flags:

| Command | Description |
|---------|-------------|
| `paperclip search -s fda Q` | Search FDA regulatory documents |
| `paperclip search -s fda/jp Q` | Search Japan PMDA reviews |
| `paperclip search -s trials Q` | Search all clinical trials |
| `paperclip search -s trials/us Q` | Search ClinicalTrials.gov only |

## Configuration

`config`, `login`/`logout`, `install`/`setup`, `update`/`uninstall` Ã¢ÂÂ settings, auth, IDE skills.

## Map Query Tips

- Be specific about what to extract. Bad: "Summarize this paper." Good: "What delivery vector was used, what cell type was targeted, and what transfection efficiency was reported?"
- When extracting data, enumerate every field you want in the query.
- Specify which section to focus on when relevant (e.g., "From the Methods section, extract...").
- Keep search results to **3Ã¢ÂÂ10 papers** for fast execution (`-n 5` or `-n 10`).
- After map, respond directly Ã¢ÂÂ don't follow up by reading individual papers with `cat`/`grep`.

## Recommended Workflows

### Finding papers or trials
```
search "your topic"
```
Present the results. Done. Do not read into individual papers unless asked.

### Answering a question about one paper
```
lookup doi 10.1101/...
cat /papers/<id>/meta.json
grep -i "keyword" /papers/<id>/content.lines
```

### Answering a question across multiple papers
```
search "topic" -n 10
map --from s_xxx "Specific question with enumerated fields to extract"
```
Synthesize the map results into your answer. Do not read individual papers after map.

### Extracting structured data from papers
```
search "topic" -n 5
map --from s_xxx "From the Methods section: what model architecture was used, what dataset size, what training time, and what benchmark score was reported?"
reduce --from m_xxx --strategy table "Compare model architectures and performance"
```

### Repo-based literature analysis (reviews, meta-analyses)

When the user asks to analyze, review, or compare across papers, use a repo to track the work:

```
# 1. Create repo and find papers (corpus-wide searches)
init my-review "Description of the analysis"
checkout my-review
search --corpus "topic A" -n 10
search --corpus "topic B" -n 10

# 2. Annotate relevance Ã¢ÂÂ explain why each paper belongs
annotate PMC123 "Relevant: only RCT directly testing saline rinse for common cold"
annotate bio_456 "Relevant: systematic review pooling URTI duration outcomes"
annotate PMC789 "Marginal: COVID-focused, but reports nasal saline arm"
commit -m "Initial curation with relevance notes"

# 3. Extract data (repo-scoped Ã¢ÂÂ maps all repo papers)
map "Extract: study design, sample size, intervention, primary outcome, effect size with CI and p-value"
reduce --from m_xxx --strategy table "Compare study designs and effect sizes"

# 4. Annotate papers with extracted findings
annotate PMC123 "RCT, N=100, MD -1.9 days (95% CI -3.3 to -0.4, p=0.01)" -L L20
annotate bio_456 "Systematic review, pooled MD -1.5 days (p<0.001)"
commit -m "Add effect size annotations from map extraction"

# 5. Refine Ã¢ÂÂ remove off-topic papers, add newly found ones
remove PMC999
search --corpus "narrower query" -n 5
commit -m "Refine collection: remove off-topic, add newly found"
```

Key rules:
- **Initial searches use `--corpus`** (repo is empty, nothing to scope to yet).
- **After curation, `map` and `search` auto-scope** to the repo's papers when checked out.
- **Always `reduce` after `map`** before synthesizing in prose Ã¢ÂÂ `reduce --strategy table` is especially useful for structured comparisons.
- **Always annotate + commit** after analysis passes so findings persist in the repo.

### Regulatory research
```
# Find FDA approval documents for a drug
search "pembrolizumab" /fda/us
cat /fda/fda_XXXX/meta.json

# Compare regulatory filings across regions
search "semaglutide" -s fda
search "semaglutide" -s trials -T pmda

# Find clinical trials for a condition
search "breast cancer HER2" -s trials
cat /trials/tri_XXXX/meta.json
head -40 /trials/tri_XXXX/content.lines
```

### Corpus-level statistics
```
sql "SELECT pub_year, COUNT(*) FROM documents WHERE title ILIKE '%CRISPR%' GROUP BY pub_year ORDER BY pub_year"
```

## Sandbox Environment

Commands run in a sandboxed virtual shell (vsh).

**Allowed**: `cd`, `ls`, `cat`, `head`, `tail`, `grep`, `sed`, `awk`, `sort`, `cut`, `tr`, `jq`, `search`, `scan`, and more.
**Blocked**: `rm`, `curl`, `wget`, `ssh`, `sudo`, etc.
**Not supported**: Shell loops (`for`/`while`) and `xargs` Ã¢ÂÂ use pipes or multiple tool calls.

### Writable scratch: `/.gxl/`

Redirect output with `> /.gxl/file.txt` or `>> /.gxl/file.txt`. This maps to a `.gxl/` folder in the user's current working directory Ã¢ÂÂ files persist and are directly accessible on their machine.

```
grep -i "IC50" /papers/<id>/content.lines > /.gxl/ic50_hits.txt
awk -F, "NR==1 || \$3>100" /papers/<id>/supplements/data.csv > /.gxl/filtered.csv
ls /.gxl/
```

## Saving Files Locally

Any paper file can be saved to the local machine by redirecting `cat` with `>`. Binary assets (figures, images) stream as raw bytes; text files as text.

```
cat /papers/PMC10791696/meta.json > meta.json
cat /papers/PMC11576387/figures/fx1.jpg > fx1.jpg
cat /papers/PMC10791696/supplements/source_data.csv > data.csv
```

## Supplements (CSV / Excel)

Supplementary materials live under `supplements/` for many PMC papers. Process with `sed`/`awk`, write to `/.gxl/`, or save raw files locally with `cat > file`.

```
ls /papers/<id>/supplements/
head -5 /papers/<id>/supplements/source_data.csv
cat /papers/<id>/supplements/source_data.csv > source_data.csv
```

## Citation URL Format

Each reference must include a `citations.gxl.ai` link:

```
https://citations.gxl.ai/papers/<doc_id>#L<n1>,L<n2>
https://citations.gxl.ai/fda/<doc_id>#L<n1>,L<n2>
https://citations.gxl.ai/trials/<doc_id>#L<n1>,L<n2>```

- Use the path matching the document's VFS root (`/papers/`, `/fda/`, `/trials/`).
- `<doc_id>` = directory name under that root (e.g. `PMC10791696`, `bio_214f7ec77685`, `NDA213137`, `NCT03928938`).
- Line numbers from `L<n>` prefixes in `content.lines`.
- Single: `#L45` Ã¢ÂÂ range: `#L45-L52` Ã¢ÂÂ multiple: `#L45,L120,L210`.
- Nature style for journals. "bioRxiv/medRxiv (year)" for preprints.
- Get author names, title, DOI from `meta.json`.
- Number references in the order they first appear.

## Search Examples

```
search "CRISPR delivery nanoparticle"
search "protein design" -n 50
search -s pmc "mRNA vaccine"
search -s biorxiv "single cell"
search -s arxiv "transformer protein"
search -s abstracts "drug discovery"
search -s fda "pembrolizumab"
search -s trials -T pmda "semaglutide"
search -s trials "breast cancer HER2"
search -s trials "phase 3 NSCLC"search -e "genome-wide association study"
search "AlphaFold" --since 30d
search "cancer" --journal "Cell" --year 2024
search --all "protein folding"
```

Key options: `-n/--limit`, `-s/--source`, `-e/--exact`, `--since`, `--sort [relevance|date]`,
`--author`, `--journal`, `--year`, `--category`, `-m/--mode [any|all]`, `--ranking [hybrid|bm25|vector]`.

## Lookup Examples

```
lookup doi 10.1101/2024.01.15.575613
lookup pmc PMC7194329
lookup pmid 32943797
lookup arxiv 2403.03507
lookup author "James Zou" -n 10
lookup title "CRISPR base editing"
lookup journal "Nature Medicine"
```

Fields: doi, author, title, abstract, source, date, pmc, pmid, arxiv, journal,
publisher, type, keywords, category, license, year, volume, issue, issn.

## Region-Scoped Search Examples

```
search "pembrolizumab" /fda/us
search "cancer" /fda/jp
search "diabetes" /fda/eu
search "breast cancer" -s trials
search "pembrolizumab" -s fda
search "trastuzumab" -s trials -T pmda
search "nivolumab" -s trials -T epar
```

## SQL Details

```
sql "SELECT source, COUNT(*) FROM documents GROUP BY source"
sql "SELECT title, doi, source FROM documents WHERE authors ILIKE '%Doudna%' LIMIT 5"
```

Columns: `id`, `title`, `doi`, `authors`, `source`, `abstract_text`, `pub_date`,
`journal_title`, `article_type`, `pmid`, `keywords`, `categories`, `pub_year`, `created_at`.

Only `SELECT` on the `documents` table. 15s timeout, 200-row limit. Use `--source pmc|biorxiv` to filter.

## Map & Reduce Examples

```
search "protein design" -n 10
map --from s_14bebc10 "What methods were used for protein design?"
reduce --from m_ec2c9cc9 --strategy summarize "What are the main findings?"
reduce --from m_ec2c9cc9 --strategy table "Compare methods and results"
reduce --from m_ec2c9cc9 --strategy themes "What themes emerge?"
```

Reduce strategies: `summarize`, `table`, `themes`, `consensus`, `bullet_points`, `extract`.

## Paper Repository Examples

### Basic lifecycle
```
init my-review "Systematic review of XYZ"
checkout my-review
add PMC123 bio_456 --note "Key finding about X"
remove PMC789
commit -m "Initial curation"
repo my-review
log
```

### Annotations Ã¢ÂÂ record findings on specific papers
```
annotate PMC123 "IC50 data in Table 2" -L L412
annotate PMC123 "RCT, N=60, effect size -1.9 days (p=0.01)"
```

### Branching and comparison
```
branch sub-topic
checkout sub-topic
merge sub-topic
diff main..sub-topic
```

### Import and export
```
import refs.bib --init my-review
import PMC11271413 --min-cites 50
export bib -o refs.bib
export csv -o papers.csv
cite --graph
```

### Library management
```
library --matched
library --unmatched
```

## Ask-Image Examples

```
ls /papers/<id>/figures/
ask-image /papers/<id>/figures/<filename> "What does this figure show?"
ask-image /papers/<id>/figures/<filename> --fn describe
ask-image /papers/<id>/figures/<filename> --fn extract-data
```

## Tips

- Prefer `head -N`, section files, or `grep`/`scan` Ã¢ÂÂ avoid `cat` on full `content.lines`.
- Use `> file.txt` after any command to save output locally.
- Use `bash '...'` for pipes or redirection to `/.gxl/`.
- `map` runs an LLM reader per paper Ã¢ÂÂ limit inputs with `-n 5` on search.
- Run `paperclip <command> --help` for full usage on any command.
