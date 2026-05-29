import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import networkx as nx
except ImportError:
    nx = None

try:
    from pyvis.network import Network
except ImportError:
    Network = None


class KnowledgeGraph:
    """Simple knowledge graph representation using nodes and triples."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.triples: List[Dict[str, str]] = []

    def add_entity(self, entity_id: str, label: str | None = None, type: str | None = None, **attributes: Any) -> str:
        if entity_id not in self.nodes:
            self.nodes[entity_id] = {"id": entity_id, "label": label or entity_id}

        node = self.nodes[entity_id]
        if label:
            node["label"] = label
        if type:
            node["type"] = type
        node.update(attributes)
        return entity_id

    def add_relation(self, subject: str, predicate: str, object_: str) -> None:
        self.add_entity(subject)
        self.add_entity(object_)
        self.triples.append({"subject": subject, "predicate": predicate, "object": object_})

    def to_dict(self) -> Dict[str, Any]:
        return {"nodes": list(self.nodes.values()), "triples": self.triples}

    def display(self) -> None:
        print("Knowledge Graph Nodes:")
        for node in self.nodes.values():
            print(f"  - {node}")
        print("\nKnowledge Graph Triples:")
        for triple in self.triples:
            print(f"  - {triple['subject']} --{triple['predicate']}--> {triple['object']}")

    def save_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2, ensure_ascii=False)

    def to_networkx(self) -> Optional[Any]:
        """Convert KnowledgeGraph to NetworkX directed graph."""
        if nx is None:
            print("NetworkX not installed. Install with: pip install networkx")
            return None

        G = nx.DiGraph()

        # Add nodes with attributes
        for node_id, node_data in self.nodes.items():
            G.add_node(node_id, **node_data)

        # Add edges with labels
        for triple in self.triples:
            G.add_edge(
                triple["subject"],
                triple["object"],
                label=triple["predicate"],
            )

        return G

    def render_html(self, output_path: str = "graph_visualization.html") -> None:
        """Render the knowledge graph as an interactive HTML visualization."""
        if Network is None:
            print("Pyvis not installed. Install with: pip install pyvis")
            return

        G = self.to_networkx()
        if G is None:
            return

        net = Network(directed=True, height="750px", width="100%")
        net.from_nx(G)

        # Style the network
        net.toggle_physics(True)
        net.show_buttons(filter_=["physics"])

        net.write_html(output_path)
        print(f"Rendered interactive graph to {output_path}")



def build_sample_knowledge_graph() -> KnowledgeGraph:
    kg = KnowledgeGraph()

    kg.add_entity("Python", label="Python", type="ProgrammingLanguage")
    kg.add_entity("JavaScript", label="JavaScript", type="ProgrammingLanguage")
    kg.add_entity("TypeScript", label="TypeScript", type="ProgrammingLanguage")
    kg.add_entity("GitHub", label="GitHub", type="Platform")
    kg.add_entity("OpenAI", label="OpenAI", type="Organization")

    kg.add_relation("Python", "isUsedFor", "Data Science")
    kg.add_relation("JavaScript", "isUsedFor", "Web Development")
    kg.add_relation("TypeScript", "extends", "JavaScript")
    kg.add_relation("GitHub", "hosts", "Open Source Projects")
    kg.add_relation("OpenAI", "develops", "AI Models")
    kg.add_relation("Python", "integratesWith", "GitHub")

    return kg


def build_knowledge_graph_from_csv(csv_path: str) -> KnowledgeGraph:
    kg = KnowledgeGraph()
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subject = row.get("Source", "").strip()
            predicate = row.get("Relationship", "").strip()
            object_ = row.get("Target", "").strip()
            if subject and predicate and object_:
                kg.add_relation(subject, predicate, object_)
    return kg


def main() -> None:
    csv_file = Path("cybersecurity_relationships.csv")
    if csv_file.exists():
        kg = build_knowledge_graph_from_csv(str(csv_file))
        print(f"Loaded knowledge graph from {csv_file}")
    else:
        kg = build_sample_knowledge_graph()
        print("CSV file not found, built a sample knowledge graph instead.")

    kg.display()
    kg.save_json("knowledge_graph.json")
    print("Saved knowledge graph to knowledge_graph.json")

    kg.render_html("graph_visualization.html")


if __name__ == "__main__":
    main()
