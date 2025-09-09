import streamlit as st
from streamlit_cytoscapejs import st_cytoscapejs
from layout import apply_tree_layout
from topics import TOPICS
from query import get_relations

# --- Relation types with colors ---
RELATIONS = {
    "Subclass of (P279)": "P279",
    "Instance of (P31)": "P31",
    "Part of (P361)": "P361",
    "Has part (P527)": "P527"
}
RELATION_COLORS = {
    "P279": "#1f77b4",   # blue
    "P31": "#ff7f0e",    # orange
    "P361": "#2ca02c",   # green
    "P527": "#d62728"    # red
}

st.set_page_config(page_title="Ontology Graph Explorer", layout="wide")
st.title("📚 Ontology Graph Explorer (Wikidata)")

# --- UI selection ---
topic = st.selectbox("Choose a topic:", list(TOPICS.keys()))

selected_relations = []
for label, pid in RELATIONS.items():
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown(
            f"<div style='width:15px; height:15px; border-radius:50%; background:{RELATION_COLORS[pid]}'></div>",
            unsafe_allow_html=True
        )
    with col2:
        if st.checkbox(label, value=(pid == "P279")):
            selected_relations.append(pid)

if not selected_relations:
    st.warning("⚠️ Please select at least one relation type.")

# --- Session state init ---
if "elements" not in st.session_state:
    st.session_state["elements"] = []
if "root" not in st.session_state:
    st.session_state["root"] = None
if "expanded_relations" not in st.session_state:
    st.session_state["expanded_relations"] = set()
if "last_message" not in st.session_state:
    st.session_state["last_message"] = None
if "last_message_type" not in st.session_state:
    st.session_state["last_message_type"] = None
if "selected_node_id" not in st.session_state:
    st.session_state["selected_node_id"] = None

# --- Control buttons ---
col1, col2 = st.columns([0.5, 0.5])
with col1:
    if st.button("Start with root"):
        root_qid = TOPICS[topic]
        st.session_state["root"] = root_qid
        st.session_state["elements"] = [
            {"data": {"id": root_qid, "label": topic, "status": "new"}}
        ]
        st.session_state["expanded_relations"].clear()
        st.session_state["last_message"] = f"ℹ️ Root node {topic} ({root_qid}) initialized."
        st.session_state["last_message_type"] = "info"

with col2:
    if st.button("Run query on selected node"):
        node_id = st.session_state.get("selected_node_id")
        if node_id:
            new_elements, messages = [], []
            for pid in selected_relations:
                if (node_id, pid) in st.session_state["expanded_relations"]:
                    continue
                children, names = get_relations(node_id, pid, limit=10)
                for c in children:
                    if "source" in c["data"]:
                        c["data"]["relation"] = pid
                new_elements.extend(children)

                if names:
                    messages.append(f"{pid} → {len(names)} children: {', '.join(names)}")
                else:
                    messages.append(f"{pid} → no results")

                st.session_state["expanded_relations"].add((node_id, pid))

            if new_elements:
                st.session_state["elements"].extend(new_elements)
                for el in st.session_state["elements"]:
                    if el["data"].get("id") == node_id:
                        el["data"]["status"] = "expanded"

                st.session_state["last_message"] = (
                    f"✅ {node_id} expanded with relations:\n" +
                    "\n".join(f"- {m}" for m in messages)
                )
                st.session_state["last_message_type"] = "success"
                st.rerun()
            else:
                st.session_state["last_message"] = (
                    f"ℹ️ {node_id} already expanded for selected relations, or no results:\n" +
                    "\n".join(f"- {m}" for m in messages)
                )
                st.session_state["last_message_type"] = "info"
                st.rerun()

# --- Log panel ---
if st.session_state["last_message"]:
    if st.session_state["last_message_type"] == "success":
        st.success(st.session_state["last_message"])
    elif st.session_state["last_message_type"] == "error":
        st.error(st.session_state["last_message"])
    elif st.session_state["last_message_type"] == "info":
        st.info(st.session_state["last_message"])

# --- Graph display ---
if st.session_state["elements"]:
    elements_with_pos = apply_tree_layout(st.session_state["elements"])

    stylesheet = [
        {"selector": "core", "style": {"background-color": "#f5f5f5"}},  # lighter background
        {"selector": "node", "style": {"label": "data(label)", "color": "white"}},
        {"selector": 'node[status = "expanded"]', "style": {"background-color": "green"}},
        {"selector": 'node[status = "new"]', "style": {"background-color": "purple"}},
        {"selector": 'node[status = "empty"]', "style": {"background-color": "red"}},
        {"selector": 'node:selected', "style": {"background-color": "yellow", "border-width": 3, "border-color": "black"}},
    ]
    for pid, color in RELATION_COLORS.items():
        stylesheet.append({
            "selector": f'edge[relation = "{pid}"]',
            "style": {"line-color": color, "width": 2}
        })

    selected_node = st_cytoscapejs(
        elements=elements_with_pos,
        stylesheet=stylesheet,
        height="800px",
        width="1200px",
        key="cyto"
    )

    if selected_node:
        st.session_state["selected_node_id"] = selected_node.get("selected_node_id")
        if st.session_state["selected_node_id"]:
            st.info(f"👉 Selected node: {st.session_state['selected_node_id']}")
