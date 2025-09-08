# 📚 Ontology Graph Explorer (Wikidata)

This demo project is an **interactive Streamlit web application** for exploring **Wikidata ontologies** as graphs.  
You can choose a scientific topic (e.g., Mathematics, Physics, Biology), and the app will query its subclass hierarchy using the **Wikidata SPARQL endpoint**.  
The result is an interactive graph where you can expand nodes by clicking on them.

---

## ✨ Features

- Query **Wikidata SPARQL** endpoint
- Visualize ontology hierarchies as graphs
- Node coloring by status:
  - 🟩 **expanded** – already expanded node
  - 🟪 **new** – newly loaded node
  - 🟥 **empty** – no subclasses available
- Interactive clickable graph powered by `cytoscape.js`
- Dynamic **tree layout** positioning
- Clean, simple **Streamlit UI**

### Main screen with topic selection

![Screenshot 1](screenshots/screenshot2.png)

### Expanded ontology graph

![Screenshot 2](screenshots/screenshot1.png)

---

## 📦 Installation

1. **Create a virtual environment**

   ```bash
   python3 -m venv .venv
   ```

2. **Activate it**

   ```bash
   source .venv/bin/activate
   ```

   _(On Windows: `.\.venv\Scripts\activate`)_

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Run the app

```bash
streamlit run wikipedia-sparql.py
```

Then open your browser at:
👉 [http://localhost:8501](http://localhost:8501)

---

## 📂 Project structure

```
.
├── wikipedia-sparql.py      # Main Streamlit app
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

---

## ⚙️ Requirements

- **Python 3.8+**
- [Streamlit](https://streamlit.io/)
- [streamlit-cytoscapejs](https://github.com/streamlit/streamlit-cytoscapejs)
- [Requests](https://docs.python-requests.org/)

---

## 🖼 Example usage

1. Select a topic from the dropdown (e.g., _Mathematics_).
2. Click **Start generating ontology**.
3. The initial graph appears.
4. Click on nodes to expand them further.

---

## 🛠 Development tips

- To add more topics, extend the `TOPICS` dictionary in `wikipedia-sparql.py`.
- To experiment with different layouts, modify the `apply_tree_layout` function.
- For larger graphs, increase the `limit` parameter in `get_children`.

---

## 📜 License

MIT License – free to use, modify, and distribute.

---
