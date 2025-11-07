import time
import enum
import json

import igraph
import matplotlib.pyplot as plt

class LogLevel(enum.Enum):
    TRACE = 1
    DEBUG = 2
    INFO = 4
    WARNING = 8
    ERROR = 16

    @staticmethod
    def bitmask(*modes):
        mask = 0
        for mode in modes:
            mask |= mode.value
        return mask

log_level = LogLevel.bitmask(
    LogLevel.TRACE, LogLevel.DEBUG, LogLevel.INFO
)

class RecipeNetwork:
    def __init__(self, data_dir: str, log_path: str = "logs/", log_name: str = "networks.log") -> None:
        self.data_dir = data_dir
        self.log_path = log_path
        self.log_name = log_name
        self.network = igraph.Graph(directed=True)

    def _logger(self, level: LogLevel, message: str, reset: bool = False) -> None:
        if not level.value & log_level:
            return
        
        now = time.asctime()
        write_mode = "a"
        if reset:
            write_mode = "w"

        with open(f"{self.log_path}/{self.log_name}", write_mode) as log_file:
            log_file.write(f"{now}: [{level.name}] - {message}\n")
    
    def import_network_from_json(self, *filenames: str) -> None:
        # read json for recipes generated from data_manipulation module
        # converts json into graph structure using igraph module
        # this graph can then be saved into a .gml file to skip the json parsing step later

        file_data = []
        for filename in filenames:
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

            dependencies = data.get("ingredients")
            for ingredient, quantity in dependencies.items():
                try: self.network.vs.find(name=ingredient)
                except: self.network.add_vertex(ingredient, label=ingredient)


                edges.append((name, ingredient))
                edge_attributes["quantity"].append(quantity)
        self.network.add_edges(edges, edge_attributes)

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