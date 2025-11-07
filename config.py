from pathlib import Path
from utils.logging import LogLevel

PROJECT_ROOT = Path(__file__).parent

# data directories
DATA_DIR = PROJECT_ROOT / "data/" 
PROCESSED_DATA_DIR = DATA_DIR / "processed/" 
FINAL_DATA_DIR = DATA_DIR / "final/"

# logging configuration
LOG_LEVELS = LogLevel
LOGGING_DIR = PROJECT_ROOT / "logs/"

# graphing configuration
GRAPH_OUTPUT_DIR = PROJECT_ROOT / "graphs/"