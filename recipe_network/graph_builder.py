from pyvis.network import Network
import networkx as nx
import time

class GraphBuilder:
    def __init__(self,  log_dir: str, log_name: str = "graph_builder", graph_name: str = "recipe_network") -> None:
        self.log_dir = log_dir
        self.log_name = log_name
        self.graph_name = graph_name
        self.nx_graph = nx.DiGraph()
        self.pyvis_graph = Network(directed=True)

    def _logger(self, message: str, reset: bool = False) -> None:
        now = time.asctime()
        write_mode = "a"
        if reset:
            write_mode = "w"

        with open(f"{self.log_dir}/{self.log_name}.log", write_mode) as log_file:
            log_file.write(f"{now}: {message}\n")

    def _add_edge(self, from_node: str, to_node: str, **attributes) -> None:
        self.nx_graph.add_edge(from_node, to_node, **attributes)

    def _save_graph(self, output_dir: str) -> None:
        output_path = output_dir / f"{self.graph_name}.html"
        self.pyvis_graph.show(str(output_path))
        
    def build_pyvis_graph(self) -> None:
        self.pyvis_graph.from_nx(self.nx_graph)
