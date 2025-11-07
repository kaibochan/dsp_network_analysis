from recipe_network.recipe_network import RecipeNetwork

def main():
    recipe_network = RecipeNetwork("recipes_json/")
    recipe_network.import_network_from_json("items.json", "buildings.json")

    recipe_network.plot_network()

if __name__ == "__main__":
    main()