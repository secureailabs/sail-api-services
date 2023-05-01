from enum import Enum


class DataFederationProvisionState(str, Enum):
    CREATED = "CREATED"
    CREATING = "CREATING"
    CREATION_FAILED = "CREATION_FAILED"
    DELETED = "DELETED"
    DELETING = "DELETING"
    DELETION_FAILED = "DELETION_FAILED"

    def __str__(self) -> str:
        return str(self.value)
