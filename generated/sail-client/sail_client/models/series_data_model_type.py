from enum import Enum


class SeriesDataModelType(str, Enum):
    SERIESDATAMODELCATEGORICAL = "SeriesDataModelCategorical"
    SERIESDATAMODELDATE = "SeriesDataModelDate"
    SERIESDATAMODELDATETIME = "SeriesDataModelDateTime"
    SERIESDATAMODELINTERVAL = "SeriesDataModelInterval"
    SERIESDATAMODELUNIQUE = "SeriesDataModelUnique"

    def __str__(self) -> str:
        return str(self.value)
