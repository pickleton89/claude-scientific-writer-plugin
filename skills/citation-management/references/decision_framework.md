# Citation Management Decision Framework

Quick-reference decision matrices for citation style selection, metadata source routing, and database selection by field.

## Citation Style Selection by Venue

```
What is your target venue?
│
├─ Academic Journal
│  │
│  ├─ Biomedical (NEJM, JAMA, Lancet) → Vancouver/NLM style
│  │
│  ├─ Life Sciences (Nature, Science, Cell) → Nature/Science style
│  │
│  ├─ Social Sciences → APA 7th edition
│  │
│  ├─ Humanities → Chicago/MLA
│  │
│  └─ Engineering/CS (IEEE venues) → IEEE style
│
├─ Conference Paper
│  │
│  ├─ ACM venues → ACM Reference Format
│  │
│  ├─ IEEE venues → IEEE style
│  │
│  └─ Other CS → Check CFP for style guide
│
├─ Thesis/Dissertation
│  │
│  └─ Check institution requirements → Usually APA or Chicago
│
└─ Grant Proposal
   │
   ├─ NIH → Vancouver/NLM style
   │
   ├─ NSF → No strict requirement (APA common)
   │
   └─ Other → Check sponsor guidelines
```

## Identifier to Metadata Source Routing

| Identifier Type | Primary Source | Fallback Source | Coverage |
|-----------------|----------------|-----------------|----------|
| DOI | CrossRef API | DataCite API | ~99% of journal articles |
| PMID | PubMed E-utilities | CrossRef (via DOI) | Biomedical literature |
| PMCID | PubMed Central | PubMed E-utilities | Open access subset |
| arXiv ID | arXiv API | CrossRef (if published) | Preprints in physics/math/CS |
| ISBN | OpenLibrary/Google Books | WorldCat | Books |
| URL | Page scraping + DOI extraction | Manual entry | Varies |

## Database Selection by Field

| Research Domain | Primary Database | Secondary Database | Specialized Sources |
|-----------------|------------------|-------------------|---------------------|
| Biomedical | PubMed | Google Scholar | ClinicalTrials.gov, Cochrane |
| Life Sciences | PubMed | Web of Science | UniProt, GenBank citations |
| Computer Science | Google Scholar | ACM/IEEE DL | DBLP, arXiv |
| Physics/Math | arXiv | Google Scholar | ADS, MathSciNet |
| Social Sciences | Google Scholar | PsycINFO | ERIC, Sociological Abstracts |
| Chemistry | SciFinder | PubMed | ChemRxiv, Reaxys |
| Engineering | IEEE Xplore | Google Scholar | Compendex |

## Usage

Reference this document when:
- Selecting citation style for a new manuscript
- Choosing which API to query for metadata extraction
- Planning multi-database search strategy
