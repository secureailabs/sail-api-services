from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"
    DATASET_ADMIN = "DATASET_ADMIN"
    DIGITAL_CONTRACT_ADMIN = "DIGITAL_CONTRACT_ADMIN"
    ORGANIZATION_ADMIN = "ORGANIZATION_ADMIN"
    SAIL_ADMIN = "SAIL_ADMIN"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
