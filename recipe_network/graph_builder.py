from pyvis.network import Network
import networkx as nx
import json

class GraphBuilder:
    def __init__(self, data_dir, log_fn, log_path: str, log_name: str, output_dir: str, graph_name: str) -> None:
        self.log_fn = log_fn
        self.log_path = log_path
        self.log_name = log_name
        self.data_dir = data_dir
        self.graph_name = graph_name
        self.output_dir = output_dir
        self.nx_graph = nx.DiGraph()
        self.pyvis_graph = Network(directed=True)

    def _logger(self, level, message: str, reset: bool = False) -> None:
        self.log_fn(level, self.log_path, self.log_name, message, reset=reset)

    def _add_edge(self, from_node: str, to_node: str, **attributes) -> None:
        self.nx_graph.add_edge(from_node, to_node, **attributes)

    def _save_graph(self, output_dir: str) -> None:
        from pathlib import Path
        output_path = Path(output_dir) / f"{self.graph_name}.html"
        
        self._logger(self.log_levels.DEBUG, f"Pyvis graph has {len(self.pyvis_graph.nodes)} nodes")
        self._logger(self.log_levels.DEBUG, f"Output path: {output_path}")
        
        if self.pyvis_graph is None:
            self._logger(self.log_levels.ERROR, "Cannot save: pyvis_graph is None")
            raise ValueError("pyvis_graph is None")
        
        try:
            self.pyvis_graph.show(str(output_path))
        except Exception as e:
            self._logger(self.log_levels.ERROR, f"Failed to save pyvis graph with show(): {e}")
            self._logger(self.log_levels.ERROR, f"Pyvis graph type: {type(self.pyvis_graph)}")
            
            try:
                self._logger(self.log_levels.INFO, f"Attempting manual HTML generation")
                html_content = self.pyvis_graph.generate_html()
                with open(str(output_path), 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self._logger(self.log_levels.INFO, f"Successfully saved via manual HTML generation")
            except Exception as e2:
                self._logger(self.log_levels.ERROR, f"Manual HTML generation also failed: {e2}")
                raise
        
    def _build_graph_data(self) -> None:
        network_data = []
        for data in self.file_data:
            self._logger(self.log_levels.TRACE, f"Processing data chunk with {len(data)} entries")
            network_data.extend(data)
            
        self._logger(self.log_levels.INFO, f"Converting json data into networkx network")

        # build the networkx graph from the parsed json data
        # each product is a source node,
        # each ingredient is a destination node
        # ingredient quantities are edge weights
        # final graph is directed from product =[weights]=> ingredients
        for data in network_data:
            name = data.get("product")
            
            # add the source node to graph
            self.nx_graph.add_node(name, label=name)
            self._logger(self.log_levels.TRACE, f"Added node: {name} to graph")

            # get all destination nodes and add edges
            dependencies = data.get("ingredients")
            self._logger(self.log_levels.TRACE, f"Processing dependencies for product: {name}")
            for ingredient, quantity in dependencies.items():
                self._logger(self.log_levels.TRACE, f"Processing ingredient: {ingredient} with quantity: {quantity}")
                
                # add destination node if it doesn't exist
                self.nx_graph.add_node(ingredient)
                self._logger(self.log_levels.TRACE, f"Added node: {ingredient} to graph")

                # add weighted edge from product to ingredient
                self.nx_graph.add_edge(name, ingredient, quantity=quantity)
                self._logger(self.log_levels.TRACE, f"Adding edge from {name} to {ingredient} with quantity {quantity}")
        
        self._logger(self.log_levels.INFO, f"Finished building networkx graph")
        self._logger(self.log_levels.INFO, "=" * 100)
    
    def set_log_levels(self, levels):
        self.log_levels = levels
        
    def import_network_from_json(self, *filenames: str) -> None:
        # read json for recipes generated from data_manipulation module
        # converts json into graph structure using igraph module
        # this graph can then be saved into a .gml file to skip the json parsing step later
        self._logger(self.log_levels.INFO, "=" * 100, reset=True)        
        
        self.file_data = []
        for filename in filenames:
            self._logger(self.log_levels.INFO, f"Starting to parse json from file: {filename}")
            try:
                with open(f"{self.data_dir}/{filename}", "r") as network_file:
                    self.file_data.append(json.load(network_file))
                    assert self.file_data[-1] is not None
            except Exception as e:
                self._logger(self.log_levels.ERROR, f"Failed to parse json from file: {filename}. Error: {e}")
                return
            self._logger(self.log_levels.INFO, f"Finished parsing json from file: {filename}")    
    
    def build_pyvis_graph(self) -> None:
        # build the networkx graph data from the imported json
        self._build_graph_data()
        
        self._logger(self.log_levels.INFO, f"NetworkX graph has {self.nx_graph.number_of_nodes()} nodes and {self.nx_graph.number_of_edges()} edges")
        self._logger(self.log_levels.INFO, f"Building pyvis graph from networkx graph")
        if self.nx_graph.number_of_nodes() == 0:
            self._logger(self.log_levels.ERROR, "NetworkX graph is empty - cannot build pyvis graph")
            return
            
        # Reinitialize pyvis graph to ensure clean state
        self._logger(self.log_levels.INFO, f"Reinitializing pyvis graph")
        self.pyvis_graph = Network(directed=True, height="600px", width="100%")
        
        try:
            self.pyvis_graph.from_nx(self.nx_graph)
            self._logger(self.log_levels.INFO, f"Pyvis graph built successfully with {len(self.pyvis_graph.nodes)} nodes")
            
            # Verify pyvis graph is properly initialized
            if self.pyvis_graph is None or not hasattr(self.pyvis_graph, 'nodes') or len(self.pyvis_graph.nodes) == 0:
                self._logger(self.log_levels.ERROR, "Pyvis graph is None or empty after from_nx conversion")
                return
                
        except Exception as e:
            self._logger(self.log_levels.ERROR, f"Failed to build pyvis graph from networkx: {e}")
            return
        
        # save the pyvis graph to an HTML file
        self._logger(self.log_levels.INFO, f"Saving pyvis graph to HTML file")
        self._save_graph(self.output_dir)
        self._logger(self.log_levels.INFO, f"Pyvis graph saved successfully to {self.output_dir / 'graph.html'}")
