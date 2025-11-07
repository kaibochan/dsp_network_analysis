import time
import enum
import json
import igraph

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
    def __init__(self, recipe_json_path: str = "recipes/", log_path: str = "logs/", log_name: str = "networks.log") -> None:
        self.recipe_json_path = recipe_json_path
        self.log_path = log_path
        self.log_name = log_name
        self.network = None

    def _logger(self, level: LogLevel, message: str, reset: bool = False) -> None:
        if not level.value & log_level:
            return
        
        now = time.asctime()
        write_mode = "a"
        if reset:
            write_mode = "w"
        
        with open(f"{self.log_path}{self.log_name}", write_mode) as log_file:
            log_file.write(f"{now}: [{level.name}] - {message}\n")
    
    def import_network_from_json(self, filename: str) -> None:
        network_data = None

        try:
            with open(f"{self.recipe_json_path}{filename}", "r") as network_file:
                network_data = json.load(network_file)
                assert network_data is not None
        except Exception as e:
            self._logger(LogLevel.ERROR, f"Failed to parse json from file: {filename}. Error: {e}")
            return
        self._logger(LogLevel.INFO, f"Finished parsing json from file: {filename}")

        for data in network_data:
            data: dict
            name = data.get("product")
            dependencies = data.get("ingredients")
            self._logger(LogLevel.TRACE, f"Found {name} in network_data")

            
