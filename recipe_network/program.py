# import the shared paths from config.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FINAL_DATA_DIR, LOGGING_DIR, LOG_LEVELS, GRAPH_OUTPUT_DIR
from utils.logging import Logger

from network_builder import RecipeNetwork
from graph_builder import GraphBuilder

def build_igraph_network():
    recipe_network = RecipeNetwork(FINAL_DATA_DIR, logger=Logger(LOGGING_DIR, "igraph_network.log", LOG_LEVELS))
    recipe_network.import_network_from_json("items.json", "buildings.json")
    recipe_network.plot_network()
    
def build_pyviz_network():
    graph_builder = GraphBuilder(FINAL_DATA_DIR, GRAPH_OUTPUT_DIR, "pyviz_graph", logger=Logger(LOGGING_DIR, "pyvis_graph_builder.log", LOG_LEVELS))
    graph_builder.import_network_from_json("items.json", "buildings.json")
    graph_builder.build_pyvis_graph()

if __name__ == "__main__":
    build_igraph_network()
    # build_pyviz_network()