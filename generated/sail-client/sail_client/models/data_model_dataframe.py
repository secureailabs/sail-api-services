from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.data_model_series import DataModelSeries


T = TypeVar("T", bound="DataModelDataframe")


@attr.s(auto_attribs=True)
class DataModelDataframe:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        series (List['DataModelSeries']):
    """

    id: str
    name: str
    description: str
    series: List["DataModelSeries"]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        description = self.description
        series = []
        for series_item_data in self.series:
            series_item = series_item_data.to_dict()

            series.append(series_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "series": series,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.data_model_series import DataModelSeries

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        series = []
        _series = d.pop("series")
        for series_item_data in _series:
            series_item = DataModelSeries.from_dict(series_item_data)

            series.append(series_item)

        data_model_dataframe = cls(
            id=id,
            name=name,
            description=description,
            series=series,
        )

        data_model_dataframe.additional_properties = d
        return data_model_dataframe

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
