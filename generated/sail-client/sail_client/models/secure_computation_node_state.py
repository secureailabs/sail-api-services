from enum import Enum


class SecureComputationNodeState(str, Enum):
    CREATING = "CREATING"
    DELETED = "DELETED"
    DELETE_FAILED = "DELETE_FAILED"
    DELETING = "DELETING"
    FAILED = "FAILED"
    INITIALIZING = "INITIALIZING"
    IN_USE = "IN_USE"
    READY = "READY"
    REQUESTED = "REQUESTED"
    WAITING_FOR_DATA = "WAITING_FOR_DATA"

    def __str__(self) -> str:
        return str(self.value)
