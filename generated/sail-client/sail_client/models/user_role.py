from enum import Enum


class UserRole(str, Enum):
    DATA_MODEL_EDITOR = "DATA_MODEL_EDITOR"
    DATA_SUBMITTER = "DATA_SUBMITTER"
    ORGANIZATION_ADMIN = "ORGANIZATION_ADMIN"
    PAG_ADMIN = "PAG_ADMIN"
    PREMIUM_USER = "PREMIUM_USER"
    RESEARCHER = "RESEARCHER"
    SAIL_ADMIN = "SAIL_ADMIN"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
