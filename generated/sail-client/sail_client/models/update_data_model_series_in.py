from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.data_model_series_state import DataModelSeriesState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.series_data_model_schema import SeriesDataModelSchema


T = TypeVar("T", bound="UpdateDataModelSeriesIn")


@attr.s(auto_attribs=True)
class UpdateDataModelSeriesIn:
    """
    Attributes:
        series_schema (Union[Unset, SeriesDataModelSchema]):
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        state (Union[Unset, DataModelSeriesState]): An enumeration.
    """

    series_schema: Union[Unset, "SeriesDataModelSchema"] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    state: Union[Unset, DataModelSeriesState] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        series_schema: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.series_schema, Unset):
            series_schema = self.series_schema.to_dict()

        name = self.name
        description = self.description
        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if series_schema is not UNSET:
            field_dict["series_schema"] = series_schema
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.series_data_model_schema import SeriesDataModelSchema

        d = src_dict.copy()
        _series_schema = d.pop("series_schema", UNSET)
        series_schema: Union[Unset, SeriesDataModelSchema]
        if isinstance(_series_schema, Unset):
            series_schema = UNSET
        else:
            series_schema = SeriesDataModelSchema.from_dict(_series_schema)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        _state = d.pop("state", UNSET)
        state: Union[Unset, DataModelSeriesState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = DataModelSeriesState(_state)

        update_data_model_series_in = cls(
            series_schema=series_schema,
            name=name,
            description=description,
            state=state,
        )

        update_data_model_series_in.additional_properties = d
        return update_data_model_series_in

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
