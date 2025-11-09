import json
from pathlib import Path

from pyvis.network import Network
import networkx as nx

from utils.logging import Logger, LogLevel

class GraphBuilder:
    def __init__(self, data_dir: Path, output_path: Path, graph_name: str, logger: Logger) -> None:
        self._logger = logger
        self.data_dir = data_dir
        self.graph_name = graph_name
        self.output_path = output_path
        self.nx_graph = nx.DiGraph()
        self.pyvis_graph = Network(directed=True)

    def _add_edge(self, from_node: str, to_node: str, **attributes) -> None:
        self.nx_graph.add_edge(from_node, to_node, **attributes)

    def _save_graph(self, graph: Network, output_path: Path) -> None:
        from pathlib import Path
        #output_path = Path(output_dir) / f"{self.graph_name}.html"

        self._logger(LogLevel.DEBUG, f"Pyvis graph has {len(graph.nodes)} nodes")
        self._logger(LogLevel.DEBUG, f"Output path: {output_path}")

        if graph is None:
            self._logger(LogLevel.ERROR, "Cannot save: pyvis_graph is None")
            raise ValueError("pyvis_graph is None")
        
        try:
            graph.show(str(output_path), notebook=False)
        except Exception as e:
            self._logger(LogLevel.ERROR, f"Failed to save pyvis graph with show(): {e}")
            self._logger(LogLevel.ERROR, f"Pyvis graph type: {type(graph)}")

            try:
                self._logger(LogLevel.INFO, f"Attempting manual HTML generation")
                html_content = graph.generate_html()
                with open(str(output_path), 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self._logger(LogLevel.INFO, f"Successfully saved via manual HTML generation")
            except Exception as e2:
                self._logger(LogLevel.ERROR, f"Manual HTML generation also failed: {e2}")
                raise
        
    def _build_graph_data(self) -> None:
        network_data = []
        self.products = set()
        self.ingredients = dict()
        self.dependencies = dict()
        for data in self.file_data:
            self._logger(LogLevel.TRACE, f"Processing data chunk with {len(data)} entries")
            network_data.extend(data)
            
        self._logger(LogLevel.INFO, f"Converting json data into networkx network")

        # build the networkx graph from the parsed json data
        # each product is a source node,
        # each ingredient is a destination node
        # ingredient quantities are edge weights
        # final graph is directed from product =[weights]=> ingredients
        for data in network_data:
            name = data.get("product")
            
            # add the source node to graph
            self.nx_graph.add_node(name, label=name)
            self.products.add(name)
            self._logger(LogLevel.TRACE, f"Added node: {name} to graph")

            # get all destination nodes and add edges
            dependencies = data.get("ingredients")
            self._logger(LogLevel.TRACE, f"Processing dependencies for product: {name}")
            for ingredient, quantity in dependencies.items():
                self._logger(LogLevel.TRACE, f"Processing ingredient: {ingredient} with quantity: {quantity}")
                
                # add destination node if it doesn't exist
                self.nx_graph.add_node(ingredient)
                self.ingredients[ingredient] = self.ingredients.get(ingredient, 0) + 1
                self._logger(LogLevel.TRACE, f"Added node: {ingredient} to graph")

                # add weighted edge from product to ingredient
                self.nx_graph.add_edge(name, ingredient, quantity=quantity)
                self._logger(LogLevel.TRACE, f"Adding edge from {name} to {ingredient} with quantity {quantity}")
            
            self.dependencies[name] = list(dependencies.keys())
        
        self._logger(LogLevel.INFO, f"Finished building networkx graph")
        self._logger(LogLevel.INFO, "=" * 100)
    
    def find_products_with_common_ingredients(self):
        # create a dictionary that maps number of common ingredients to list of products and the ingredients
        # idea is to look through products and dependencies and find which products have 1, 2, 3,... common ingredients
        
        dependencies = self.dependencies
        common_ingredients_map = dict()
        for product, ingredients in dependencies.items():
            for next_product, next_ingredients in dependencies.items():
                if product == next_product:
                    continue
                
                # grab common ingredients between the sets based on the intersection
                common_ingredients = set(ingredients).intersection(set(next_ingredients))
                common_count = len(common_ingredients)
                
                if common_count == 0:
                    continue
                
                # add the products and their common ingredients to the map
                common_ingredients_map[common_count] = common_ingredients_map.get(common_count, [])
                
                # check for existing links, such as A-B and B-A
                reverse_exists = False
                for entry in common_ingredients_map[common_count]:
                    if (entry[0] == next_product and entry[1] == product):
                        reverse_exists = True
                        break
                
                if reverse_exists:
                    continue
                common_ingredients_map[common_count].append((product, next_product, common_ingredients))     

        return common_ingredients_map

    def print_items_summary(self) -> None:
        self._logger(LogLevel.INFO, f"Total unique products: {len(self.products)}")
        self._logger(LogLevel.INFO, f"Total unique ingredients: {len(self.ingredients)}")

        # print all products and ingredients with counts
        # self._logger(LogLevel.DEBUG, "Products:")
        # for product in sorted(self.products):
        #     self._logger(LogLevel.DEBUG, f" - {product}")
        self._logger(LogLevel.DEBUG, "Ingredients:")
        for ingredient, count in sorted(self.ingredients.items()):
            self._logger(LogLevel.DEBUG, f" - {ingredient}: used in {count} products")
            
        self._logger(LogLevel.INFO, "=" * 100)
            
        # print products with increasing number of common dependencies
        common_ingredient_map = self.find_products_with_common_ingredients()
        for common_count in sorted(common_ingredient_map.keys()):
            self._logger(LogLevel.INFO, f"Products with {common_count} common ingredients:")
            for product1, product2, common_ingredients in common_ingredient_map[common_count]:
                self._logger(LogLevel.INFO, f" - {product1} and {product2}: common ingredients: {', '.join(common_ingredients)}")
            self._logger(LogLevel.INFO, "=" * 100)

    def import_network_from_json(self, *filenames: str) -> None:
        # read json for recipes generated from data_manipulation module
        # converts json into graph structure using igraph module
        # this graph can then be saved into a .gml file to skip the json parsing step later
        self._logger(LogLevel.INFO, "=" * 100, reset=True)        
        
        self.file_data = []
        for filename in filenames:
            self._logger(LogLevel.INFO, f"Starting to parse json from file: {filename}")
            try:
                with open(f"{self.data_dir}/{filename}", "r") as network_file:
                    self.file_data.append(json.load(network_file))
                    assert self.file_data[-1] is not None
            except Exception as e:
                self._logger(LogLevel.ERROR, f"Failed to parse json from file: {filename}. Error: {e}")
                return
            self._logger(LogLevel.INFO, f"Finished parsing json from file: {filename}")
        
        # build the networkx graph data from the imported json
        self._build_graph_data()
    
    def partition_into_clusters(self) -> None:
        # use the Clauset-Newman-Moore greedy modularity maximization method to
        # partition the graph into modular communities

        self.communities = nx.community.greedy_modularity_communities(self.nx_graph, weight='quantity', resolution=2.0)
        for i, community in enumerate(self.communities):
            for node in community:
                self.nx_graph.nodes[node]['group'] = i

    def partition_into_common_ingredient_clusters(self) -> None:
        # partition the graph into clusters based on common ingredients between products

        common_ingredient_map = self.find_products_with_common_ingredients()
        # assign community groups based on common ingredient counts
        for i, common_count in enumerate(sorted(common_ingredient_map.keys(), reverse=True)):
            graph = nx.Graph()
            for product1, product2, common_ingredients in common_ingredient_map[common_count]:
                self.nx_graph.nodes[product1]['group'] = i
                self.nx_graph.nodes[product2]['group'] = i
                graph.add_edge(product1, product2, weight=len(common_ingredients))
            pyviz_graph = Network(directed=False, height="1000px", width="100%")
            pyviz_graph.from_nx(graph)
            output_path = self.output_path / f"{self.graph_name}_common_ingredients_{common_count}.html"
            self._save_graph(pyviz_graph, output_path)

    def build_pyviz_graph(self) -> None:       
        self._logger(LogLevel.INFO, f"NetworkX graph has {self.nx_graph.number_of_nodes()} nodes and {self.nx_graph.number_of_edges()} edges")
        self._logger(LogLevel.INFO, f"Building pyviz graph from networkx graph")
        if self.nx_graph.number_of_nodes() == 0:
            self._logger(LogLevel.ERROR, "NetworkX graph is empty - cannot build pyvis graph")
            return
            
        # Reinitialize pyvis graph to ensure clean state
        self._logger(LogLevel.INFO, f"Reinitializing pyvis graph")
        self.pyvis_graph = Network(directed=True, height="1000px", width="100%")
        
        try:
            self.pyvis_graph.from_nx(self.nx_graph)
            self._logger(LogLevel.INFO, f"Pyvis graph built successfully with {len(self.pyvis_graph.nodes)} nodes")
            
            # Verify pyvis graph is properly initialized
            if self.pyvis_graph is None or not hasattr(self.pyvis_graph, 'nodes') or len(self.pyvis_graph.nodes) == 0:
                self._logger(LogLevel.ERROR, "Pyvis graph is None or empty after from_nx conversion")
                return
                
        except Exception as e:
            self._logger(LogLevel.ERROR, f"Failed to build pyvis graph from networkx: {e}")
            return
        
        # save the pyvis graph to an HTML file
        self._logger(LogLevel.INFO, f"Saving pyvis graph to HTML file")
        output_path = self.output_path / f"{self.graph_name}.html"
        self._save_graph(self.pyvis_graph, output_path)
        self._logger(LogLevel.INFO, f"Pyvis graph saved successfully to {output_path}")
