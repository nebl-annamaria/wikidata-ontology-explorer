import streamlit as st
import requests
from streamlit_cytoscapejs import st_cytoscapejs


# --- Wikidata query ---
def get_children(qid, limit=10):
    query = f"""
    SELECT ?child ?childLabel (COUNT(?grandchild) AS ?childCount) WHERE {{
      ?child wdt:P279 wd:{qid}.
      OPTIONAL {{ ?grandchild wdt:P279 ?child. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    GROUP BY ?child ?childLabel
    ORDER BY DESC(?childCount)
    LIMIT {limit}
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        "Accept": "application/json",
        "User-Agent": "OntologyGraphDemo/0.1 (mailto:te@emailed.hu)"
    }

    response = requests.get(url, params={"query": query, "format": "json"}, headers=headers, timeout=20)

    try:
        data = response.json()
    except Exception:
        return [], []

    results = []
    names = []
    for item in data.get("results", {}).get("bindings", []):
        child_qid = item["child"]["value"].split("/")[-1]
        child_label = item["childLabel"]["value"]
        child_count = int(item["childCount"]["value"])
        names.append(f"{child_label} ({child_count})")
        # Node
        results.append({"data": {"id": child_qid,
                                 "label": f"{child_label} ({child_count})",
                                 "status": "new",
                                 "child_count": child_count}})
        # Edge
        results.append({"data": {"source": qid, "target": child_qid}})
    return results, names


# --- Tree layout ---
def apply_tree_layout(elements, canvas_width=1200, level_gap=200, sibling_gap=200, offset_step=15):
    nodes = [el for el in elements if "source" not in el["data"]]
    edges = [el for el in elements if "source" in el["data"]]

    if not nodes:
        return elements

    # Root in the middle
    root = nodes[0]["data"]["id"]

    # Building adjacency list
    children_map = {}
    for edge in edges:
        src = edge["data"]["source"]
        tgt = edge["data"]["target"]
        children_map.setdefault(src, []).append(tgt)

    # BFS for the levels
    levels = {root: 0}
    queue = [root]
    while queue:
        parent = queue.pop(0)
        for child in children_map.get(parent, []):
            if child not in levels:
                levels[child] = levels[parent] + 1
                queue.append(child)

    # Positioning by levels
    positions = {}
    max_level = max(levels.values())
    for lvl in range(max_level + 1):
        same_level = [n for n, l in levels.items() if l == lvl]
        for i, node_id in enumerate(same_level):
            offset = ((-1) ** i) * offset_step
            positions[node_id] = {
                "x": canvas_width // 2 + i * sibling_gap - (len(same_level) - 1) * sibling_gap / 2,
                "y": 100 + lvl * level_gap + offset,
            }

    # Writing positions
    for node in nodes:
        node_id = node["data"]["id"]
        if node_id in positions:
            node["position"] = positions[node_id]

    return nodes + edges


# --- Basic topics ---
TOPICS = {
    "Mathematics": "Q395",
    "Physics": "Q413",
    "Biology": "Q420",
    "Computer Science": "Q21198",
    "History": "Q309",
    "Chemistry": "Q2329"
}


# --- Streamlit UI ---
st.set_page_config(page_title="Ontology Graph Explorer", layout="wide")
st.title("📚 Ontology graph explorer (Wikidata)")

topic = st.selectbox("Choose a topic:", list(TOPICS.keys()))

if "elements" not in st.session_state:
    st.session_state["elements"] = []
if "root" not in st.session_state:
    st.session_state["root"] = None
if "expanded" not in st.session_state:
    st.session_state["expanded"] = set()
if "last_message" not in st.session_state:
    st.session_state["last_message"] = None
if "last_message_type" not in st.session_state:
    st.session_state["last_message_type"] = None

if st.button("Start generating ontology"):
    root_qid = TOPICS[topic]
    children, names = get_children(root_qid, limit=10)
    st.session_state["root"] = root_qid
    st.session_state["elements"] = [
        {"data": {"id": root_qid, "label": f"{topic} ({len(names)})", "status": "expanded"}}
    ] + children
    st.session_state["expanded"] = {root_qid}
    if names:
        st.session_state["last_message"] = f"✅ {topic} ({root_qid}) bővítve, {len(names)} gyerek: {', '.join(names)}"
        st.session_state["last_message_type"] = "success"
    else:
        st.session_state["last_message"] = f"❌ No subclass under {topic} ({root_qid}) ."
        st.session_state["last_message_type"] = "error"

# --- Log panel ---
if st.session_state["last_message"]:
    if st.session_state["last_message_type"] == "success":
        st.success(st.session_state["last_message"])
    elif st.session_state["last_message_type"] == "error":
        st.error(st.session_state["last_message"])

# --- Graph display ---
if st.session_state["elements"]:
    elements_with_pos = apply_tree_layout(st.session_state["elements"])

    stylesheet = [
        {"selector": "node", "style": {"label": "data(label)", "color": "white"}},
        {"selector": "edge", "style": {"line-color": "#AAAAAA"}},
        {"selector": 'node[status = "expanded"]', "style": {"background-color": "green"}},
        {"selector": 'node[status = "new"]', "style": {"background-color": "purple"}},
        {"selector": 'node[status = "empty"]', "style": {"background-color": "red"}},
    ]

    selected_node = st_cytoscapejs(
        elements=elements_with_pos,
        stylesheet=stylesheet,
        height="800px",
        width="1200px",
        key="cyto"
    )

    if selected_node:
        node_id = selected_node.get("selected_node_id")
        if node_id and node_id not in st.session_state["expanded"]:
            new_elements, names = get_children(node_id, limit=10)
            if new_elements:
                st.session_state["elements"].extend(new_elements)
                st.session_state["expanded"].add(node_id)
                for el in st.session_state["elements"]:
                    if el["data"].get("id") == node_id:
                        el["data"]["status"] = "expanded"
                st.session_state["last_message"] = f"✅ {node_id} expanded, {len(names)} child: {', '.join(names)}"
                st.session_state["last_message_type"] = "success"
                st.rerun()
            else:
                for el in st.session_state["elements"]:
                    if el["data"].get("id") == node_id:
                        el["data"]["status"] = "empty"
                st.session_state["last_message"] = f"❌ No subclass under {node_id}."
                st.session_state["last_message_type"] = "error"
                st.rerun()
