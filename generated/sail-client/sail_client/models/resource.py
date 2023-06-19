from enum import Enum


class Resource(str, Enum):
    DATASET = "DATASET"
    DATA_FEDERATION = "DATA_FEDERATION"
    DATA_MODEL = "DATA_MODEL"
    SECURE_COMPUTATION_NODE = "SECURE_COMPUTATION_NODE"
    USER_ACTIVITY = "USER_ACTIVITY"

    def __str__(self) -> str:
        return str(self.value)
