from enum import Enum


class DataModelState(str, Enum):
    CHECKED_OUT = "CHECKED_OUT"
    DELETED = "DELETED"
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"

    def __str__(self) -> str:
        return str(self.value)
