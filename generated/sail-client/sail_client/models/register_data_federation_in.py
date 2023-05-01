from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.data_federation_data_format import DataFederationDataFormat
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegisterDataFederationIn")


@attr.s(auto_attribs=True)
class RegisterDataFederationIn:
    """
    Attributes:
        name (str):
        description (str):
        data_format (DataFederationDataFormat): An enumeration.
        data_model_id (Union[Unset, str]):
    """

    name: str
    description: str
    data_format: DataFederationDataFormat
    data_model_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        data_format = self.data_format.value

        data_model_id = self.data_model_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "data_format": data_format,
            }
        )
        if data_model_id is not UNSET:
            field_dict["data_model_id"] = data_model_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        data_format = DataFederationDataFormat(d.pop("data_format"))

        data_model_id = d.pop("data_model_id", UNSET)

        register_data_federation_in = cls(
            name=name,
            description=description,
            data_format=data_format,
            data_model_id=data_model_id,
        )

        register_data_federation_in.additional_properties = d
        return register_data_federation_in

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
