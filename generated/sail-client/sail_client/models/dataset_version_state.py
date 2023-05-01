from enum import Enum


class DatasetVersionState(str, Enum):
    ACTIVE = "ACTIVE"
    CREATING_DIRECTORY = "CREATING_DIRECTORY"
    ENCRYPTING = "ENCRYPTING"
    ERROR = "ERROR"
    INACTIVE = "INACTIVE"
    NOT_UPLOADED = "NOT_UPLOADED"

    def __str__(self) -> str:
        return str(self.value)
