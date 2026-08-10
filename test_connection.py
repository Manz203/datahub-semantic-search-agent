"""
Quick sanity check: connect to a local DataHub instance and pull back
a handful of dataset entities via the GraphQL API.

Run this from WSL Ubuntu, inside your `datahub-env` virtualenv, from your
project folder (NOT from /mnt/c/... — stay in your Linux home directory).

    source ~/datahub-env/bin/activate
    pip install requests
    python test_connection.py
"""

import json
import requests

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


def fetch_datasets(start: int = 0, count: int = 10):
    payload = {
        "query": QUERY,
        "variables": {"start": start, "count": count},
    }
    resp = requests.post(GMS_GRAPHQL_URL, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        print("GraphQL returned errors:")
        print(json.dumps(data["errors"], indent=2))
        return []

    results = data["data"]["search"]["searchResults"]
    total = data["data"]["search"]["total"]
    print(f"Total datasets in catalog: {total}\n")

    entities = []
    for r in results:
        entity = r["entity"]
        name = entity.get("properties", {}).get("name") or entity.get("name")
        description = entity.get("properties", {}).get("description") or "(no description)"
        platform = (entity.get("platform") or {}).get("name", "unknown")
        urn = entity["urn"]
        entities.append(
            {
                "urn": urn,
                "name": name,
                "description": description,
                "platform": platform,
            }
        )
        print(f"- [{platform}] {name}")
        print(f"    {description}")
        print(f"    {urn}\n")

    return entities


if __name__ == "__main__":
    fetch_datasets()
