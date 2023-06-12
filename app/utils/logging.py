import logging
from enum import Enum

logger = logging.getLogger("apiservice")
handler = logging.FileHandler("audit.log")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)


class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Resource(Enum):
    DATASET = "DATASET"
    DATA_MODEL = "DATA_MODEL"
    SECURE_COMPUTATION_NODE = "SECURE_COMPUTATION_NODE"
    DATA_FEDERATION = "DATA_FEDERATION"
    USER_ACTIVITY = "USER_ACTIVITY"


def add_log_message(
    level: LogLevel,
    operation_resource: Resource,
    message: str,
):
    message = f"[{operation_resource.value}] {message}"
    if level == LogLevel.INFO:
        logger.info(message)
    elif level == LogLevel.WARNING:
        logger.warning(message)
    elif level == LogLevel.ERROR:
        logger.error(message)
    else:
        raise ValueError("Invalid log level")
    pass
