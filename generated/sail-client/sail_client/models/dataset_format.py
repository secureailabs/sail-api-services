from enum import Enum


class DatasetFormat(str, Enum):
    CSV = "CSV"
    FHIR = "FHIR"

    def __str__(self) -> str:
        return str(self.value)
