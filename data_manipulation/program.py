# import the shared paths from config.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROCESSED_DATA_DIR, FINAL_DATA_DIR, LOGGING_DIR, LOG_LEVELS
from utils.logging import Logger

from data_manipulator import FuckassDSPDataTransformer

# data from https://docs.google.com/spreadsheets/d/1UdwWUkZhCOrNBidocL2-Oueyl-dfo1P-/edit?gid=665114638#gid=665114638

def data_transformation():
    # transform item data
    item_transformer = FuckassDSPDataTransformer(PROCESSED_DATA_DIR, FINAL_DATA_DIR, logger=Logger(LOGGING_DIR, "items.log", LOG_LEVELS))
    item_transformer.parse_file("items.csv")
    item_transformer.save_transformed_data("items.json")
    
    # transform building data
    building_transformer = FuckassDSPDataTransformer(PROCESSED_DATA_DIR, FINAL_DATA_DIR, logger=Logger(LOGGING_DIR, "buildings.log", LOG_LEVELS))
    building_transformer.parse_file("buildings.csv")
    building_transformer.save_transformed_data("buildings.json")
    
if __name__ == "__main__":
    data_transformation()