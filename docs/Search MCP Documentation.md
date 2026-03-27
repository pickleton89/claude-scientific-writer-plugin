# Scite MCP Server

## Overview

Scite MCP connects AI assistants (Claude, ChatGPT, Copilot, Gemini CLI) to a database of 1.6 billion Smart Citations across 281 million scientific articles. All content delivered in compliance with publisher agreements.
The biggest problem with AI in research is that it isn't grounded in the literature. Scite MCP fixes that. It connects your AI assistant to over 250 million scientific articles, book chapters, preprints, and datasets, and gives it something most research MCPs don't: citation context.

That context comes from Smart Citations. Scite classifies every citation as supporting, disputing, or mentioning. So when your assistant searches for papers, it can prioritize work that's been supported by later research, flag findings that have been challenged, and help you make better decisions about what to trust and cite.

Most literature MCPs just search. Scite gives AI a quality signal on top of search. That's the difference between "here are papers that match your query" and "here are papers that match your query, and here's how the field has treated them."

Scite MCP also supports full-text search, DOI resolution, metadata verification, and access pathways through institutional link resolvers. If you only set up one research MCP, start here.

## Core Capabilities

- **Full-text literature search:** Queries Scite's full-text index (~50M articles via publisher partnerships + open access), returning relevant research articles — not just abstracts or metadata.
- **Smart Citation classification:** Each citation is classified as supporting, contrasting, or mentioning. This provides an evidence landscape around any claim, not just a reference list.
- **Contextual citation snippets:** Returns ~3-sentence excerpts from citing papers, classified by type and location in the article, enabling synthesis of actual argumentative context.
- **Citation metrics and tallies:** Per-paper metadata including total citations and breakdown by supporting/contrasting/mentioning, indicating reliability and reception.
- **DOI-based article lookup:** Retrieve verified article metadata by DOI — real papers with confirmed metadata, eliminating hallucinated citations.

## Differentiators

- Searches inside full text, not just titles and abstracts.
- Provides directional citation signals (supported vs. contradicted findings).
- Includes built-in access resolution so users can read retrieved papers.
- Grounds LLM responses in peer-reviewed papers with DOIs rather than web pages, blogs, or training data.

## Integration Features

- **Institutional access bridging:** Connects LLMs to library/enterprise holdings (LibKey, GetFTR, Article Galaxy, OpenURL). Enables summary → DOI → full text in one flow, with collection-gap detection.
- **Interactive follow-up:** Users can request deeper evidence exploration (e.g., "show supporting citations," "list all references") and the MCP re-queries Scite for detailed contexts.
- **Structured output generation:** Once Scite supplies citation and study data, LLM tools can generate evidence tables, feedback-loop graphs, diagrams, and HTML/PDF reports linked to specific studies.
- **Composable with other MCPs:** Works alongside Zotero, PubMed, and custom tools in MCP-aware clients for end-to-end workflows (search → filter by citation pattern → push DOIs to reference manager → generate outputs).
- **Admin analytics:** Institutions and publishers can view aggregate AI-read metrics — articles accessed via LLM, which LLMs are used, subscription gap detection — supporting future COUNTER-style AI-read reporting.

---

# Consensus MCP

## Overview

Consensus MCP connects AI assistants (Claude, ChatGPT, Copilot) to 220M+ peer-reviewed papers and preprints across 250,000+ journals. Sources include PubMed, OpenAlex, Semantic Scholar, arXiv, and bioRxiv. Retracted articles are flagged and removed via Retraction Watch integration. Index is continuously updated.

## Core Capabilities

- **Full-text-informed search:** Publisher partnerships (Wiley, APA, Sage, Taylor & Francis, ACS, AAAS) grant full-text access used during ranking — results reflect content relevance, not just keyword matches.
- **Hybrid ranking model:** Combines keyword + semantic search using proprietary models trained on 100M+ researcher queries across all disciplines. Retrieval accuracy is tuned per research domain.
- **Structured search strategies:** Supports boolean terms and PICO-based queries. Can run multiple searches in parallel for multi-step research plans.
- **Structured response per paper:** Each search returns the query, total papers found, and per-paper objects containing: title, authors, full abstract, journal name, publication details, year, citation count, and direct link on Consensus.
- **Pre-built research skills:** One-click workflows for grant searching, literature reviews, and curriculum development.
- **Formatted output generation:** Produces reading lists, literature reviews, and grant briefs directly.

## Differentiators

- Largest peer-reviewed research index outside Google Scholar.
- Full-text access during search (not just abstracts/metadata) via publisher partnerships.
- Ranking models trained on real researcher behavior, not generic semantic similarity.
- Retraction Watch integration for quality control.

## Workflow Example: Grant Discovery

A demonstrated multi-tool workflow: Consensus MCP performs multiple literature searches, then NIH RePORTER queries find similar funded projects, and results are assembled into a grant-application recommendation document. Illustrates how Consensus MCP composes with other tools for complex, multi-step research workflows.

## When to Use Web App vs. MCP

- **Web app:** Single, straightforward queries — offers filters, tables, and visualizations for quick paper discovery.
- **MCP:** Complex, personalized workflows — grant searching, literature review processes, curriculum/reading list generation — where AI planning, parallel searches, and bulk synthesis of hundreds of papers are needed.

## Example Prompts

- "Search for research on the effects of climate change on biodiversity."
- "Find recent studies (since 2020) on machine learning in healthcare diagnosis."
- "Search for high-quality human studies on cognitive behavioral therapy for anxiety with at least 100 participants."
- "What does research say about the effectiveness of remote work on productivity?"


# Consensus MCP Documenation
# Getting Started with the Consensus MCP

The Consensus MCP server enables AI assistants like ChatGPT, Claude, and other MCP-compatible clients to search over 200 million peer-reviewed academic research papers directly from the conversation.

## Getting Started

Consensus MCP lets AI assistants search 200+ million peer-reviewed research papers. Connect your preferred client below — you'll be searching in under 2 minutes.

> **Server URL:** `https://mcp.consensus.app/mcp`
>
> The `/mcp` path is required. Using `https://mcp.consensus.app` alone will not work.

***

## Connect Your Client

### Claude Desktop

1. Go to **Settings → Connectors**
2. Click **Browse Connectors**
3. Search for **Consensus**
4. Click **Connect** — OAuth sign-in will open automatically

### ChatGPT

1. Click **Apps** from the left sidebar
2. Search for **Consensus**
3. Click **Connect** and sign in with your Consensus account

Search results display in an interactive widget showing top papers with citations and direct links.

### Claude Code

```bash
claude mcp add --transport http consensus https://mcp.consensus.app/mcp
```

OAuth will open in your browser automatically on first use. You can also trigger it manually with the `/mcp` command inside Claude Code.

### Codex

```bash
codex mcp add consensus --url https://mcp.consensus.app/mcp
codex mcp login consensus
```

### Cursor

Add via **Settings → Tools & MCP → New MCP Server**, or edit your config directly:

```json
{
  "mcpServers": {
    "consensus": {
      "url": "https://mcp.consensus.app/mcp"
    }
  }
}
```

### VS Code (GitHub Copilot)

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "consensus": {
      "url": "https://mcp.consensus.app/mcp"
    }
  }
}
```

### Windsurf

Add via **Settings → Cascade → MCP Servers**, or edit your config directly:

```json
{
  "mcpServers": {
    "consensus": {
      "serverUrl": "https://mcp.consensus.app/mcp"
    }
  }
}
```

### Other MCP Clients

Any MCP compatible client can connect using the server URL `https://mcp.consensus.app/mcp` with HTTP transport. If your client supports OAuth, authentication will be handled automatically.

***

## Verify Your Connection

Try asking your AI assistant:

> What does the research say about the effects of exercise on depression?

You should see results citing specific papers with titles, journals, years, citation counts, and direct links.

***

## Plans and Access

Your results depend on your **Consensus plan**, not your AI subscription (Claude Pro, ChatGPT Plus, etc. have no effect on Consensus results).

No account is needed to get started, connect directly and try it out.

| Plan       | Papers per Search | Monthly Searches | Extra Features            |
| ---------- | ----------------- | ---------------- | ------------------------- |
| No Account | 3                 | Unlimited        | —                         |
| Free       | 10                | 30               | Full abstracts            |
| Pro        | 20                | 1,000            | Study type, key takeaways |

Create a free account at [consensus.app/sign-up](https://consensus.app/sign-up/) or upgrade at [consensus.app/pricing](https://consensus.app/pricing/).

### Enterprise and API Key Access

For enterprise access with unlimited rate limits, include your API key as a Bearer token:

```
Authorization: Bearer YOUR_API_KEY
```

Contact Consensus for enterprise API access at [consensus.app/home/api](https://consensus.app/home/api/).

***

## Search Tool

### Parameters

| Parameter         | Type         | Required | Description                                                                                                                                                                                           |
| ----------------- | ------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `query`           | string       | Yes      | The research question or topic to search for. Use specific academic terminology for best results.                                                                                                     |
| `year_min`        | integer      | No       | Exclude papers published before this year.                                                                                                                                                            |
| `year_max`        | integer      | No       | Exclude papers published after this year.                                                                                                                                                             |
| `study_types`     | string array | No       | Filter by study design. Values: `rct`, `meta-analysis`, `systematic review`, `literature review`, `case report`, `non-rct experimental`, `non-rct observational study`, `non-rct in vitro`, `animal`. |
| `sjr_max`         | integer      | No       | Filter by journal quality (SCImago Journal Rank quartile). 1 is Q1 (highest), 2 is Q2, 3 is Q3, 4 is Q4.                                                                                              |
| `human`           | boolean      | No       | Set to `true` to include only studies involving human subjects.                                                                                                                                       |
| `sample_size_min` | integer      | No       | Exclude studies with sample sizes smaller than this number.                                                                                                                                           |

### Response

Each search returns:

* **papers** — Array of paper objects with: `title`, `authors`, `abstract`, `journal`, `year`, `citation_count`, and `url` (direct link to the paper on Consensus)
* **total\_results** — Total number of papers found
* **query** — The original search query

Pro plans and above also include `study_type` and `takeaway` for each paper. Enterprise includes `doi`.

### Example Prompts

* "What does the research say about the effectiveness of remote work on productivity?"
* "Find RCTs and meta-analyses since 2020 on cognitive behavioral therapy for anxiety"
* "Search for high quality human studies on gut microbiome and mental health with at least 100 participants"
* "Recent research on large language model hallucination from top tier journals"

***

## Troubleshooting

### OAuth login is only supported for streamable HTTP servers (Codex)

You added the server with `-- --transport http` instead of `--url`. Remove and re-add:

```bash
codex mcp remove consensus
codex mcp add consensus --url https://mcp.consensus.app/mcp
codex mcp login consensus
```

### Authentication successful but server reconnection failed (Claude Code)

Fully quit and restart Claude Code — do not just use the reconnect option. Your credentials are saved and will work after restart.

### Tools stop working after a few hours (401 errors)

Your OAuth token has expired. Re-authenticate:

* **Claude Code:** Type `/mcp`, select Consensus, choose **Clear authentication**, re-authenticate, then restart Claude Code
* **Codex:** Run `codex mcp logout consensus` then `codex mcp login consensus`
* **Cursor:** Disconnect and reconnect the server in Settings then Tools and MCP
* **Claude Desktop:** Disconnect and reconnect the connector in Settings then Connectors

### Server shows failed or no tools appear

1. Verify the URL includes `/mcp` at the end
2. Remove and re-add the server using the commands above
3. Restart your client completely

### Consensus search has not been loaded yet (Claude Code)

This is normal. Claude loads tool definitions on demand when many tools are present. Retry the query and it will work on the second attempt.

### No results found

Try broadening your search query or removing filters. Use specific academic terminology rather than casual language.

### Rate limit exceeded (429 error)

Wait a few moments before searching again. If using automated workflows, implement backoff logic between requests.

***

## Security

* **Endpoint:** Only connect to the official URL: `https://mcp.consensus.app/mcp`
* **API keys:** Store securely using environment variables. Never share keys in prompts or public conversations. Rotate if compromised.
* **Data handling:** Search queries are sent to the Consensus API over HTTPS/TLS. Results contain publicly available academic paper metadata. No personal data is stored from MCP requests.

***

## Supported Platforms

| Platform          | Auth         | Status    |
| ----------------- | ------------ | --------- |
| Claude Desktop    | OAuth        | Supported |
| ChatGPT           | OAuth        | Supported |
| Claude Code       | OAuth        | Supported |
| Codex             | OAuth        | Supported |
| Cursor            | OAuth        | Supported |
| VS Code (Copilot) | Config       | Supported |
| Windsurf          | Config       | Supported |
| Other MCP Clients | Bearer token | Supported |

***

## Additional Resources

* [Consensus Website](https://consensus.app)
* [Consensus API Documentation](https://docs.consensus.app)
* [Model Context Protocol Specification](https://modelcontextprotocol.io/)