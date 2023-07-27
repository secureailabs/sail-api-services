from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.data_model_series_schema import DataModelSeriesSchema


T = TypeVar("T", bound="DataModelSeries")


@attr.s(auto_attribs=True)
class DataModelSeries:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        series_schema (DataModelSeriesSchema):
    """

    id: str
    name: str
    description: str
    series_schema: "DataModelSeriesSchema"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        description = self.description
        series_schema = self.series_schema.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "series_schema": series_schema,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.data_model_series_schema import DataModelSeriesSchema

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        series_schema = DataModelSeriesSchema.from_dict(d.pop("series_schema"))

        data_model_series = cls(
            id=id,
            name=name,
            description=description,
            series_schema=series_schema,
        )

        data_model_series.additional_properties = d
        return data_model_series

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
