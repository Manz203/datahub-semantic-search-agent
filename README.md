# DataHub Semantic Search Agent

A semantic search agent for [DataHub](https://datahub.com)'s metadata catalog. Instead of relying on exact keyword matches, it uses sentence embeddings to understand the *meaning* of a natural language query and rank catalog entities (datasets, tables, columns) by relevance — surfacing the right data even when the query doesn't share exact wording with the dataset's name or description.

## How it works

1. **Fetch** — Pulls all dataset entities from a running DataHub instance via its GraphQL API (name, description, platform).
2. **Embed** — Encodes each entity's name + description using a `sentence-transformers` model (`all-MiniLM-L6-v2`).
3. **Search** — Encodes the user's natural language query the same way, then ranks catalog entities by cosine similarity between the query embedding and each entity embedding.

Example: a query like `"warehouse inventory levels"` correctly surfaces the `inventories` dataset (whose description mentions *"Tracks product inventory levels across warehouses"*) above datasets that only share the literal word "warehouse" — because the match is on meaning, not just keyword overlap.

## Tech stack

- **Python 3.11**
- **DataHub Core** (self-hosted via Docker, GraphQL API)
- **sentence-transformers** (`all-MiniLM-L6-v2`) for embeddings
- **numpy** for cosine similarity ranking
- **requests** for the DataHub API client

## Setup

### 1. Start DataHub locally

```bash
pip install acryl-datahub
datahub init          # host: http://localhost:8080, token: leave blank
datahub docker quickstart
```

Wait for all containers to report healthy (`docker ps` — gms, kafka, mysql, opensearch, frontend, actions should all show `Up`/`healthy`).

### 2. Load sample data

```bash
datahub datapack load showcase-ecommerce
```

This populates the catalog with a realistic e-commerce dataset (orders, customers, products, warehouses, etc.) so there's something meaningful to search.

### 3. Install project dependencies

```bash
pip install requests sentence-transformers numpy
```

### 4. Run the search agent

```bash
python search_agent.py
```

This fetches all datasets from your local DataHub instance, builds the embedding index, and drops you into an interactive prompt:

```
Search> customer shipping information
Search> product returns and refunds
Search> warehouse inventory levels
```

Type `quit` to exit.

## Files

- `search_agent.py` — main semantic search engine (fetch → embed → search loop)
- `test_connection.py` — minimal sanity-check script to confirm the DataHub GraphQL API is reachable before running the full agent

## Notes

- The script talks to DataHub's GMS backend directly on port `8080` rather than the frontend proxy on `9002`, since GMS doesn't require authentication in a local quickstart setup.
- Embeddings are computed with `all-MiniLM-L6-v2`, a lightweight (~90MB) model well-suited for short catalog descriptions; it downloads automatically on first run.
