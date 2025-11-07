# import the shared paths from config.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FINAL_DATA_DIR, LOGGING_DIR, LOG_FN

from network_builder import RecipeNetwork

def build_network():
    recipe_network = RecipeNetwork(FINAL_DATA_DIR, LOG_FN, LOGGING_DIR, "igraph_network.log")
    recipe_network.import_network_from_json("items.json", "buildings.json")
    recipe_network.plot_network()
    
if __name__ == "__main__":
    build_network()