def apply_tree_layout(elements, canvas_width=1200, level_gap=200, sibling_gap=200, offset_step=15):
    """
    Assign positions for nodes in a tree-like layout.
    - Root node in the middle
    - Children placed level by level
    - Horizontal spacing between siblings
    - Small vertical offset alternation to reduce overlap
    """
    nodes = [el for el in elements if "source" not in el["data"]]
    edges = [el for el in elements if "source" in el["data"]]

    if not nodes:
        return elements

    root = nodes[0]["data"]["id"]

    # Build adjacency list
    children_map = {}
    for edge in edges:
        src = edge["data"]["source"]
        tgt = edge["data"]["target"]
        children_map.setdefault(src, []).append(tgt)

    # BFS for levels
    levels = {root: 0}
    queue = [root]
    while queue:
        parent = queue.pop(0)
        for child in children_map.get(parent, []):
            if child not in levels:
                levels[child] = levels[parent] + 1
                queue.append(child)

    # Assign positions per level
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

    # Write positions back to nodes
    for node in nodes:
        node_id = node["data"]["id"]
        if node_id in positions:
            node["position"] = positions[node_id]

    return nodes + edges
