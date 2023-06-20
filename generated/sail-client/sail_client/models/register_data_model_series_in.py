from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.series_data_model_schema import SeriesDataModelSchema


T = TypeVar("T", bound="RegisterDataModelSeriesIn")


@attr.s(auto_attribs=True)
class RegisterDataModelSeriesIn:
    """
    Attributes:
        name (str):
        description (str):
        series_schema (SeriesDataModelSchema):
        data_model_dataframe_id (str):
    """

    name: str
    description: str
    series_schema: "SeriesDataModelSchema"
    data_model_dataframe_id: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        series_schema = self.series_schema.to_dict()

        data_model_dataframe_id = self.data_model_dataframe_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "series_schema": series_schema,
                "data_model_dataframe_id": data_model_dataframe_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.series_data_model_schema import SeriesDataModelSchema

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        series_schema = SeriesDataModelSchema.from_dict(d.pop("series_schema"))

        data_model_dataframe_id = d.pop("data_model_dataframe_id")

        register_data_model_series_in = cls(
            name=name,
            description=description,
            series_schema=series_schema,
            data_model_dataframe_id=data_model_dataframe_id,
        )

        register_data_model_series_in.additional_properties = d
        return register_data_model_series_in

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
