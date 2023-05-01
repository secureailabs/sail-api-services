from enum import Enum


class DataModelState(str, Enum):
    DELETED = "DELETED"
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"

    def __str__(self) -> str:
        return str(self.value)
