from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.data_model_dataframe_state import DataModelDataframeState
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDataModelDataframeIn")


@attr.s(auto_attribs=True)
class UpdateDataModelDataframeIn:
    """
    Attributes:
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        state (Union[Unset, DataModelDataframeState]): An enumeration.
    """

    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    state: Union[Unset, DataModelDataframeState] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        _state = d.pop("state", UNSET)
        state: Union[Unset, DataModelDataframeState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = DataModelDataframeState(_state)

        update_data_model_dataframe_in = cls(
            name=name,
            description=description,
            state=state,
        )

        update_data_model_dataframe_in.additional_properties = d
        return update_data_model_dataframe_in

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
