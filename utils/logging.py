import enum
import time

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

def logger(level: LogLevel, log_dir: str, log_name: str, message: str, reset: bool = False) -> None:
    if not level.value & log_level:
            return
    
    now = time.asctime()
    write_mode = "a"
    if reset:
        write_mode = "w"

    with open(f"{log_dir}/{log_name}", write_mode) as log_file:
        log_file.write(f"{now}: [{level.name}] - {message}\n")