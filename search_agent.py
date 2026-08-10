"""
DataHub Semantic Search Agent — core search engine.

Pulls every dataset from a local DataHub catalog via GraphQL, embeds each
one's name + description using a sentence-transformer model, and lets you
run natural language queries against the catalog using cosine similarity.

Usage:
    source ~/datahub-env/bin/activate
    pip install sentence-transformers numpy requests
    python search_agent.py
"""

import json
import requests
import numpy as np
from sentence_transformers import SentenceTransformer

GMS_GRAPHQL_URL = "http://localhost:8080/api/graphql"

QUERY = """
query listDatasets($start: Int!, $count: Int!) {
  search(input: {type: DATASET, query: "*", start: $start, count: $count}) {
    total
    searchResults {
      entity {
        urn
        ... on Dataset {
          name
          properties {
            name
            description
          }
          platform {
            name
          }
        }
      }
    }
  }
}
"""


def fetch_all_datasets(page_size: int = 50):
    """Pull every dataset entity from DataHub, paging through results."""
    all_entities = []
    start = 0

    while True:
        payload = {"query": QUERY, "variables": {"start": start, "count": page_size}}
        resp = requests.post(GMS_GRAPHQL_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if "errors" in data:
            print("GraphQL errors:", json.dumps(data["errors"], indent=2))
            break

        search_data = data["data"]["search"]
        total = search_data["total"]
        results = search_data["searchResults"]

        for r in results:
            entity = r["entity"]
            name = entity.get("properties", {}).get("name") or entity.get("name")
            description = entity.get("properties", {}).get("description") or ""
            platform = (entity.get("platform") or {}).get("name", "unknown")
            all_entities.append(
                {
                    "urn": entity["urn"],
                    "name": name,
                    "description": description,
                    "platform": platform,
                }
            )

        start += page_size
        if start >= total:
            break

    return all_entities


def build_search_text(entity: dict) -> str:
    """Combine name + description into one string for embedding."""
    # Truncate very long descriptions (some are full markdown docs) so the
    # embedding focuses on the most relevant summary content up front.
    desc = entity["description"][:500]
    return f"{entity['name']}. Platform: {entity['platform']}. {desc}"


class SemanticSearchIndex:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"Loading embedding model '{model_name}'...")
        self.model = SentenceTransformer(model_name)
        self.entities = []
        self.embeddings = None

    def build(self, entities: list):
        self.entities = entities
        texts = [build_search_text(e) for e in entities]
        print(f"Embedding {len(texts)} entities...")
        self.embeddings = self.model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        )
        print("Index built.\n")

    def search(self, query: str, top_k: int = 5):
        query_vec = self.model.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True
        )[0]
        # Since embeddings are normalized, dot product == cosine similarity
        scores = self.embeddings @ query_vec
        top_indices = np.argsort(-scores)[:top_k]

        results = []
        for idx in top_indices:
            results.append(
                {
                    "score": float(scores[idx]),
                    "entity": self.entities[idx],
                }
            )
        return results


def print_results(results):
    for i, r in enumerate(results, start=1):
        e = r["entity"]
        print(f"{i}. [{r['score']:.3f}] ({e['platform']}) {e['name']}")
        desc_preview = e["description"][:150].replace("\n", " ")
        if desc_preview:
            print(f"   {desc_preview}...")
        print(f"   {e['urn']}\n")


def main():
    print("Fetching datasets from DataHub...")
    entities = fetch_all_datasets()
    print(f"Fetched {len(entities)} datasets.\n")

    index = SemanticSearchIndex()
    index.build(entities)

    print("=" * 60)
    print("DataHub Semantic Search — type a query, or 'quit' to exit")
    print("=" * 60)

    while True:
        query = input("\nSearch> ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        results = index.search(query, top_k=5)
        print()
        print_results(results)


if __name__ == "__main__":
    main()
