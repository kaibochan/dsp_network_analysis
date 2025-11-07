from data_manipulator import FuckassDSPDataTransformer

# data from https://docs.google.com/spreadsheets/d/1UdwWUkZhCOrNBidocL2-Oueyl-dfo1P-/edit?gid=665114638#gid=665114638

def main():
    # transform item data
    item_transformer = FuckassDSPDataTransformer("transformed/", "final/", "logs/", "items.log")
    item_transformer.parse_file("items.csv")
    item_transformer.save_transformed_data("items.json")
    
    # transform building data
    building_transformer = FuckassDSPDataTransformer("transformed/", "final/", "logs/", "buildings.log")
    building_transformer.parse_file("buildings.csv")
    building_transformer.save_transformed_data("buildings.json")

if __name__ == "__main__":
    main()