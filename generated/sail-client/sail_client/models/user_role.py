from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    DATA_SUBMITTER = "DATA_SUBMITTER"
    FEDERATION_OWNER = "FEDERATION_OWNER"
    RESEARCHER = "RESEARCHER"
    SAIL_ADMIN = "SAIL_ADMIN"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
