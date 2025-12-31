# Subagent Pipeline Architecture

> Technical reference for the chunked processing subagent system
> Version: 1.0.0

## Overview

The research-paper-summarizer uses a multi-agent pipeline for processing papers >12 pages. This document describes the architecture, coordination protocol, and error handling.

## Processing Mode Selection

```
Paper received
│
├─ Count pages
│
├─ pages ≤ 12?
│  └─ YES → Standard Mode (single-pass, legacy prompts)
│
└─ pages > 12?
   └─ YES → Chunked Mode (subagent pipeline)
```

## Chunked Mode Architecture

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────┐
│                    SETUP PHASE                               │
├─────────────────────────────────────────────────────────────┤
│  1. Section Detection                                        │
│     └─ Input: First 5-10 pages                              │
│     └─ Output: JSON mapping {section → page_range}          │
│                                                              │
│  2. Skeleton Creation                                        │
│     └─ Input: summary-skeleton.md + skeleton-config.md      │
│     └─ Output: {filename}_summary.md with PENDING markers   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   DISPATCH PHASE                             │
├─────────────────────────────────────────────────────────────┤
│  For each subagent in sequence:                             │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  overview   │ →  │   methods   │ →  │   results   │     │
│  │   agent     │    │    agent    │    │    agent    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │              │
│         ▼                  ▼                  ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  critique   │ →  │   context   │ →  │  synthesis  │     │
│  │   agent     │    │    agent    │    │    agent    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                              │
│  Each agent:                                                 │
│  1. Reads assigned PDF pages                                │
│  2. Reads current summary file                              │
│  3. Writes output to summary file                           │
│  4. Updates section marker: PENDING → COMPLETE              │
└─────────────────────────────────────────────────────────────┘
```

### Section Marker Protocol

The summary file uses HTML comment markers to track progress:

```html
<!-- SECTION: executive_summary PENDING -->
[placeholder text]
<!-- END SECTION: executive_summary -->
```

After subagent writes:

```html
<!-- SECTION: executive_summary COMPLETE -->
[actual content from subagent]
<!-- END SECTION: executive_summary -->
```

### Marker States

| State | Meaning |
|-------|---------|
| `PENDING` | Section not yet processed |
| `COMPLETE` | Section successfully written |
| `SKIPPED` | Section not applicable for article type |
| `FAILED` | Subagent failed after retry |

## Article-Type-Specific Sequences

### General Research
```
overview → methods → results → critique → context → synthesis
```

### Review Article
```
overview → evidence → landscape → critique → references → synthesis
```

### Cell & Molecular Biology
```
overview → models → mechanisms → results → critique → translational → synthesis
```

### Computational Biology
```
overview → data → methods → validation → critique → reproducibility → synthesis
```

## Subagent Inventory

### Shared Agents (All Article Types)

| Agent | Location | Purpose |
|-------|----------|---------|
| overview-agent | `subagents/overview-agent.md` | Executive summary, background, hypothesis |
| critique-agent | `subagents/critique-agent.md` | Critical analysis, limitations |
| synthesis-agent | `subagents/synthesis-agent.md` | Final synthesis (reads summary only) |

### Article-Type-Specific Agents

| Article Type | Directory | Agents |
|--------------|-----------|--------|
| General | `subagents/general/` | methods, results, context |
| Review | `subagents/review/` | evidence, landscape, references |
| Cell/Mol Bio | `subagents/cellmolbio/` | models, mechanisms, results, translational |
| Comp Bio | `subagents/compbio/` | data, methods, validation, reproducibility |

## Error Handling

### Retry Logic

```
Subagent fails
│
├─ Attempt 1 failed?
│  └─ Retry with same parameters
│
├─ Attempt 2 failed?
│  └─ Mark section as FAILED
│  └─ Log error details
│  └─ Continue to next agent
│
└─ Multiple failures?
   └─ Fall back to Standard Mode
   └─ Notify user of partial completion
```

### Recovery Workflow

User can resume incomplete summarization:

```
User: Continue summarizing this paper - some sections are still PENDING

Claude: [Reads summary file]
        Found 3 sections marked PENDING: critique, context, synthesis
        Resuming from critique agent...
```

## Performance Characteristics

| Paper Length | Mode | Approximate Time |
|--------------|------|------------------|
| ≤12 pages | Standard | 2-3 minutes |
| 13-24 pages | Chunked | 5-8 minutes |
| 25-40 pages | Chunked | 8-12 minutes |
| >40 pages | Chunked | 12-15 minutes |

Visual output generation adds ~1-2 minutes per format.
