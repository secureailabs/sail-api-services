from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.data_model_state import DataModelState
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDataModelIn")


@attr.s(auto_attribs=True)
class UpdateDataModelIn:
    """
    Attributes:
        state (Union[Unset, DataModelState]): An enumeration.
        name (Union[Unset, str]): The name of the data model
        description (Union[Unset, str]): The description of the data model
        current_version_id (Union[Unset, str]): The current version id of the data model
        current_editor_id (Union[Unset, str]):
        current_editor_organization_id (Union[Unset, str]):
    """

    state: Union[Unset, DataModelState] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    current_version_id: Union[Unset, str] = UNSET
    current_editor_id: Union[Unset, str] = UNSET
    current_editor_organization_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        name = self.name
        description = self.description
        current_version_id = self.current_version_id
        current_editor_id = self.current_editor_id
        current_editor_organization_id = self.current_editor_organization_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if state is not UNSET:
            field_dict["state"] = state
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if current_version_id is not UNSET:
            field_dict["current_version_id"] = current_version_id
        if current_editor_id is not UNSET:
            field_dict["current_editor_id"] = current_editor_id
        if current_editor_organization_id is not UNSET:
            field_dict["current_editor_organization_id"] = current_editor_organization_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _state = d.pop("state", UNSET)
        state: Union[Unset, DataModelState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = DataModelState(_state)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        current_version_id = d.pop("current_version_id", UNSET)

        current_editor_id = d.pop("current_editor_id", UNSET)

        current_editor_organization_id = d.pop("current_editor_organization_id", UNSET)

        update_data_model_in = cls(
            state=state,
            name=name,
            description=description,
            current_version_id=current_version_id,
            current_editor_id=current_editor_id,
            current_editor_organization_id=current_editor_organization_id,
        )

        update_data_model_in.additional_properties = d
        return update_data_model_in

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
