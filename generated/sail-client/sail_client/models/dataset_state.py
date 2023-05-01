from enum import Enum


class DatasetState(str, Enum):
    ACTIVE = "ACTIVE"
    CREATING_STORAGE = "CREATING_STORAGE"
    ERROR = "ERROR"
    INACTIVE = "INACTIVE"

    def __str__(self) -> str:
        return str(self.value)
