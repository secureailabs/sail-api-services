from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegisterDataModelVersionIn")


@attr.s(auto_attribs=True)
class RegisterDataModelVersionIn:
    """
    Attributes:
        name (str):
        description (str):
        data_model_id (str):
        previous_version_id (Union[Unset, str]):
    """

    name: str
    description: str
    data_model_id: str
    previous_version_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        data_model_id = self.data_model_id
        previous_version_id = self.previous_version_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "data_model_id": data_model_id,
            }
        )
        if previous_version_id is not UNSET:
            field_dict["previous_version_id"] = previous_version_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        data_model_id = d.pop("data_model_id")

        previous_version_id = d.pop("previous_version_id", UNSET)

        register_data_model_version_in = cls(
            name=name,
            description=description,
            data_model_id=data_model_id,
            previous_version_id=previous_version_id,
        )

        register_data_model_version_in.additional_properties = d
        return register_data_model_version_in

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
