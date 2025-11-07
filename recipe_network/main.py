from network_factory import RecipeNetwork

def main():
    recipe_network = RecipeNetwork("recipes_json/")
    recipe_network.import_network_from_json("items.json")

if __name__ == "__main__":
    main()