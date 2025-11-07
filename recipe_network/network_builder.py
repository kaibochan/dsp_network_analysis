import json
from pathlib import Path

import igraph
import matplotlib.pyplot as plt

from utils.logging import Logger, LogLevel

class RecipeNetwork:
    def __init__(self, data_dir: str|Path, logger: Logger) -> None:
        self.data_dir = data_dir
        self._logger = logger
        self.network = igraph.Graph(directed=True)
    
    def import_network_from_json(self, *filenames: str) -> None:
        # read json for recipes generated from data_manipulation module
        # converts json into graph structure using igraph module
        # this graph can then be saved into a .gml file to skip the json parsing step later
        self._logger(LogLevel.INFO, "=" * 100, reset=True)        
        
        file_data = []
        for filename in filenames:
            self._logger(LogLevel.INFO, f"Starting to parse json from file: {filename}")
            try:
                with open(f"{self.data_dir}/{filename}", "r") as network_file:
                    file_data.append(json.load(network_file))
                    assert file_data[-1] is not None
            except Exception as e:
                self._logger(LogLevel.ERROR, f"Failed to parse json from file: {filename}. Error: {e}")
                return
            self._logger(LogLevel.INFO, f"Finished parsing json from file: {filename}")
        
        network_data = []
        for data in file_data:
            network_data.extend(data)
            
        self._logger(LogLevel.INFO, f"Converting json data into igraph network")

        edges = []
        edge_attributes = {
            "quantity" : []
        }

        for data in network_data:
            name = data.get("product")
            self.network.add_vertex(name, label=name)
            self._logger(LogLevel.TRACE, f"Product added: {name}")

            dependencies = data.get("ingredients")
            for ingredient, quantity in dependencies.items():
                try:
                    self.network.vs.find(name=ingredient)
                    self._logger(LogLevel.TRACE, f"Ingredient already in network: {ingredient}")
                except:
                    self.network.add_vertex(ingredient, label=ingredient)
                    self._logger(LogLevel.TRACE, f"Ingredient implicitly added: {ingredient}")

                edges.append((name, ingredient))
                edge_attributes["quantity"].append(quantity)
        self.network.add_edges(edges, edge_attributes)
        
        self._logger(LogLevel.INFO, "=" * 100)

    def plot_network(self):
        fig = plt.figure(0)
        fig.add_subplot()
        igraph.plot(
            self.network, 
            target=fig.axes[0],
            vertex_size=10,
            vertex_label_size=7,
            vertex_label_dist=-1.5,
            edge_width=1,
            edge_arrow_width=5,
            edge_arrow_size=5,
            layout=self.network.layout("fruchterman_reingold")
        )

        plt.tight_layout()
        plt.show()