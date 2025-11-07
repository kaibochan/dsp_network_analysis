import pandas as pd
import json
import time
import enum

class LogLevel(enum.Enum):
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

log_level = LogLevel.DEBUG

class FuckassDSPDataTransformer:
    def __init__(self, raw_data_path: str, transformed_data_path: str, log_path: str = "logs/", log_name: str = "transformation.log") -> None:
        self.raw_data_path = raw_data_path
        self.transformed_data_path = transformed_data_path
        self.df = None
        self.transformed_data = []
        self.log_path = log_path
        self.log_name = log_name

    def _logger(self, message: str, reset: bool = False) -> None:        
        now = time.asctime()
        if reset:
            with open(f"{self.log_path}/{self.log_name}", "w") as log_file:
                log_file.write(f"{now}: {message}\n")
        else:
            with open(f"{self.log_path}/{self.log_name}", "a") as log_file:
                log_file.write(f"{now}: {message}\n")
                
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
        if log_level == LogLevel.DEBUG or log_level == LogLevel.TRACE:
            self._logger(f"[DEBUG] - Parsing line: {line}")

        tokens = line.split(',"')
        key = tokens[0]
        weighted_valuemap = tokens[1].replace('"', '').split(',') # remove quotes and tokenize based on commas
        if log_level == LogLevel.TRACE:
            self._logger(f"[TRACE] - weighted_valuemap: {weighted_valuemap}")
        
        # split the #- ingredient weight pairs into something usable
        # example [1- Plasma Capsule, 2- Iron Ingot] -> {'Plasma Capsule': 1, 'Iron Ingot': 2}
        ingredients = {}        
        for ingredient in weighted_valuemap:
            ingredient_weight, ingredient_name = ingredient.split('- ')
            ingredient_weight = int(ingredient_weight)
            
            if log_level == LogLevel.TRACE:
                self._logger(f"[TRACE] - Ingredient parsed - Name: {ingredient_name}, Weight: {ingredient_weight}")

            ingredients[ingredient_name] = ingredient_weight

        self.transformed_data.append({
            "product": key,
            # "quantity", "item_quantity" # for future use
            "ingredients": ingredients
        })

    def parse_file(self, filename: str) -> None:
        self._logger("=" * 100, reset=True)
        self._logger(f"[INFO] - Starting to parse file: {filename}")
        
        try:
            with open(f"{self.raw_data_path}/{filename}", "r") as raw_file:
                for line in raw_file:
                    self._parse_line(line.strip())
        except Exception as e:
            self._logger(f"[ERROR] - Failed to parse file: {filename}. Error: {e}")
            return

        self._logger(f"[INFO] - Finished parsing file: {filename}")
        
    def save_transformed_data(self, output_filename: str) -> None:
        try:
            with open(f"{self.transformed_data_path}/{output_filename}", "w") as output_file:
                json.dump(self.transformed_data, output_file, indent=4)
        except Exception as e:
            self._logger(f"[ERROR] - Failed to save transformed data to: {output_filename}. Error: {e}")
            return

        self._logger(f"[INFO] - Saved transformed data to: {output_filename}")
        self._logger(f"[INFO] - {output_filename} saved successfully.")
        self._logger("=" * 100)