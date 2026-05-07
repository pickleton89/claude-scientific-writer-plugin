# arXiv Subject Categories (Biomedical-Adjacent)

Quick reference for arXiv subject taxonomy used when phrasing queries against
the arXiv-indexed slice of the Paperclip corpus. Paperclip's keyword search
does not natively filter by `cat:`, but category-aware phrasing (including the
category code as a literal term) tightens recall and helps screening.

For native category-filtered searches (outside the deep-research pipeline),
use arXiv's web/API directly with the `cat:` syntax shown below.

## Biology-relevant categories (q-bio.*)

| Code | Name | Typical content |
|------|------|----------------|
| `q-bio.BM` | Biomolecules | Protein/nucleic-acid structure, folding, binding, dynamics |
| `q-bio.CB` | Cell Behavior | Single-cell dynamics, cell signaling, motility, division |
| `q-bio.GN` | Genomics | Sequencing, variant calling, genome assembly, GWAS |
| `q-bio.MN` | Molecular Networks | Pathways, regulatory/metabolic networks, network inference |
| `q-bio.NC` | Neurons & Cognition | Computational neuroscience, neural coding, behavior |
| `q-bio.QM` | Quantitative Methods | Statistical and computational biology methodology |

## Computational adjuncts

| Code | Name | When biomedical work touches it |
|------|------|--------------------------------|
| `cs.AI` | Artificial Intelligence | AI for drug discovery, clinical decision support |
| `cs.LG` | Machine Learning | ML methods for biomedical data; deep learning architectures |
| `stat.ML` | Statistics — Machine Learning | Probabilistic ML, Bayesian methods, statistical learning theory |

## Native arXiv query syntax

```
cat:q-bio.QM AND title:"single cell"
cat:q-bio.GN AND abs:"variant calling"
(cat:cs.LG OR cat:stat.ML) AND abs:"protein structure"
```

Field prefixes: `cat:` (category), `title:`, `abs:` (abstract), `au:` (author),
`all:` (all fields). Combine with `AND`, `OR`, `ANDNOT`. Use parentheses for
grouping.

## Use within the deep-research pipeline

- **Paperclip channel** (`agents/bibliography.md` §Step 3 Paperclip channel):
  arXiv hits surface inside the unified Paperclip result set. Include the
  category code as a keyword in the Paperclip query when targeting a specific
  computational subfield (e.g., `paperclip search "q-bio.QM single cell RNA
  velocity" -n 30`).
- **Screening**: when a Paperclip hit returns an arXiv DOI, record the
  category in the Annotated Bibliography under `Source: arXiv (q-bio.QM)`
  to make the methodological lineage discoverable for the verification agent.
- **Out-of-scope categories** (physics, math, economics) usually indicate
  off-target hits; flag for triage exclusion unless the RQ explicitly bridges
  domains.

## Attribution

Category list and `cat:` syntax adapted from the legacy
`references/_legacy/database_strategies.md` (lines 25-30) and from
[arXiv help — search syntax](https://info.arxiv.org/help/api/user-manual.html#query_details).
