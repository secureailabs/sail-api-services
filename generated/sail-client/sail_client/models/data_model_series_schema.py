from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.series_data_model_type import SeriesDataModelType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataModelSeriesSchema")


@attr.s(auto_attribs=True)
class DataModelSeriesSchema:
    """
    Attributes:
        type (SeriesDataModelType): An enumeration.
        list_value (Union[Unset, List[str]]):
        unit (Union[Unset, str]):
        min_ (Union[Unset, float]):
        max_ (Union[Unset, float]):
        resolution (Union[Unset, float]):
    """

    type: SeriesDataModelType
    list_value: Union[Unset, List[str]] = UNSET
    unit: Union[Unset, str] = UNSET
    min_: Union[Unset, float] = UNSET
    max_: Union[Unset, float] = UNSET
    resolution: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        list_value: Union[Unset, List[str]] = UNSET
        if not isinstance(self.list_value, Unset):
            list_value = self.list_value

        unit = self.unit
        min_ = self.min_
        max_ = self.max_
        resolution = self.resolution

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
            }
        )
        if list_value is not UNSET:
            field_dict["list_value"] = list_value
        if unit is not UNSET:
            field_dict["unit"] = unit
        if min_ is not UNSET:
            field_dict["min"] = min_
        if max_ is not UNSET:
            field_dict["max"] = max_
        if resolution is not UNSET:
            field_dict["resolution"] = resolution

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = SeriesDataModelType(d.pop("type"))

        list_value = cast(List[str], d.pop("list_value", UNSET))

        unit = d.pop("unit", UNSET)

        min_ = d.pop("min", UNSET)

        max_ = d.pop("max", UNSET)

        resolution = d.pop("resolution", UNSET)

        data_model_series_schema = cls(
            type=type,
            list_value=list_value,
            unit=unit,
            min_=min_,
            max_=max_,
            resolution=resolution,
        )

        data_model_series_schema.additional_properties = d
        return data_model_series_schema

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
