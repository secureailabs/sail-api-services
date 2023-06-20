import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.data_model_dataframe_state import DataModelDataframeState
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDataModelDataframeOut")


@attr.s(auto_attribs=True)
class GetDataModelDataframeOut:
    """
    Attributes:
        name (str):
        description (str):
        data_model_id (str):
        id (str):
        organization_id (str):
        state (DataModelDataframeState): An enumeration.
        creation_time (Union[Unset, datetime.datetime]):
    """

    name: str
    description: str
    data_model_id: str
    id: str
    organization_id: str
    state: DataModelDataframeState
    creation_time: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        data_model_id = self.data_model_id
        id = self.id
        organization_id = self.organization_id
        state = self.state.value

        creation_time: Union[Unset, str] = UNSET
        if not isinstance(self.creation_time, Unset):
            creation_time = self.creation_time.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "data_model_id": data_model_id,
                "id": id,
                "organization_id": organization_id,
                "state": state,
            }
        )
        if creation_time is not UNSET:
            field_dict["creation_time"] = creation_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        data_model_id = d.pop("data_model_id")

        id = d.pop("id")

        organization_id = d.pop("organization_id")

        state = DataModelDataframeState(d.pop("state"))

        _creation_time = d.pop("creation_time", UNSET)
        creation_time: Union[Unset, datetime.datetime]
        if isinstance(_creation_time, Unset):
            creation_time = UNSET
        else:
            creation_time = isoparse(_creation_time)

        get_data_model_dataframe_out = cls(
            name=name,
            description=description,
            data_model_id=data_model_id,
            id=id,
            organization_id=organization_id,
            state=state,
            creation_time=creation_time,
        )

        get_data_model_dataframe_out.additional_properties = d
        return get_data_model_dataframe_out

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
