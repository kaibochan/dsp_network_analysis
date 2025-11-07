import json
from pathlib import Path

from utils.logging import Logger, LogLevel

class FuckassDSPDataTransformer:
    def __init__(self, raw_data_path: Path, transformed_data_path: Path, logger: Logger) -> None:
        self.raw_data_path = raw_data_path
        self.transformed_data_path = transformed_data_path
        self.df = None
        self.transformed_data = []
        self._logger = logger
        # self.log_path = log_path
        # self.log_fn = log_fn
        # self.log_name = log_name
        
    # def set_log_levels(self, levels):
    #     self.log_levels = levels

    # def _logger(self, level, message: str, reset: bool = False) -> None:
    #     self.log_fn(level, self.log_path, self.log_name, message, reset=reset)

    def _parse_line(self, line: str):
        # read in a line from the raw dsp data file and generate a usable dictionary
        # output dictionary format:
        # {
        #   "product": "item_name",
        #   "ingredients": {
        #       "ingredient_name_1": weight_1,
        #       "ingredient_name_2": weight_2,
        #       ...
        #   },
        self._logger(LogLevel.DEBUG, f"Parsing line: {line}")

        tokens = line.split(',"')
        key = tokens[0]
        weighted_valuemap = tokens[1].replace('"', '').split(',') # remove quotes and tokenize based on commas
        self._logger(LogLevel.TRACE, f"weighted_valuemap: {weighted_valuemap}")

        # split the #- ingredient weight pairs into something usable
        # example [1- Plasma Capsule, 2- Iron Ingot] -> {'Plasma Capsule': 1, 'Iron Ingot': 2}
        ingredients = {}        
        for ingredient in weighted_valuemap:
            ingredient_weight, ingredient_name = ingredient.split('- ')
            ingredient_weight = int(ingredient_weight)

            self._logger(LogLevel.TRACE, f"Ingredient parsed - Name: {ingredient_name}, Weight: {ingredient_weight}")

            ingredients[ingredient_name] = ingredient_weight

        self.transformed_data.append({
            "product": key,
            # "quantity", "item_quantity" # for future use
            "ingredients": ingredients
        })

    def parse_file(self, filename: str) -> None:
        self._logger(LogLevel.INFO, "=" * 100, reset=True)
        self._logger(LogLevel.INFO, f"Starting to parse file: {filename}")

        try:
            with open(self.raw_data_path / filename, "r") as raw_file:
                for line in raw_file:
                    self._parse_line(line.strip())
        except Exception as e:
            self._logger(LogLevel.ERROR, f"Failed to parse file: {filename}. Error: {e}")
            return

        self._logger(LogLevel.INFO, f"Finished parsing file: {filename}")
        
    def save_transformed_data(self, output_filename: str) -> None:
        try:
            with open(self.transformed_data_path / output_filename, "w") as output_file:
                json.dump(self.transformed_data, output_file, indent=4)
        except Exception as e:
            self._logger(LogLevel.ERROR, f"Failed to save transformed data to: {output_filename}. Error: {e}")
            return

        self._logger(LogLevel.INFO, f"Saved transformed data to: {output_filename}")
        self._logger(LogLevel.INFO, f"{output_filename} saved successfully.")
        self._logger(LogLevel.INFO,"=" * 100)