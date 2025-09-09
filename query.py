import requests


def get_relations(qid, prop="P279", limit=10):
    """
    Query Wikidata for related entities by a given property (e.g., P279 = subclass of).
    """
    query = f"""
    SELECT ?child ?childLabel (COUNT(?grandchild) AS ?childCount) WHERE {{
      ?child wdt:{prop} wd:{qid}.
      OPTIONAL {{ ?grandchild wdt:{prop} ?child. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    GROUP BY ?child ?childLabel
    ORDER BY DESC(?childCount)
    LIMIT {limit}
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        "Accept": "application/json",
        "User-Agent": "OntologyGraphDemo/0.1 (mailto:your@email)"
    }

    response = requests.get(url, params={"query": query, "format": "json"}, headers=headers, timeout=20)

    try:
        data = response.json()
    except Exception:
        return [], []

    results, names = [], []
    for item in data.get("results", {}).get("bindings", []):
        child_qid = item["child"]["value"].split("/")[-1]
        child_label = item["childLabel"]["value"]
        child_count = int(item["childCount"]["value"])
        names.append(f"{child_label} ({child_count})")
        results.append({"data": {"id": child_qid,
                                 "label": f"{child_label} ({child_count})",
                                 "status": "new",
                                 "child_count": child_count}})
        results.append({"data": {"source": qid, "target": child_qid}})
    return results, names
