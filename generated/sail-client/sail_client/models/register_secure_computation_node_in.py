from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.secure_computation_node_size import SecureComputationNodeSize

T = TypeVar("T", bound="RegisterSecureComputationNodeIn")


@attr.s(auto_attribs=True)
class RegisterSecureComputationNodeIn:
    """
    Attributes:
        data_federation_id (str):
        size (SecureComputationNodeSize): An enumeration.
    """

    data_federation_id: str
    size: SecureComputationNodeSize
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data_federation_id = self.data_federation_id
        size = self.size.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_federation_id": data_federation_id,
                "size": size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_federation_id = d.pop("data_federation_id")

        size = SecureComputationNodeSize(d.pop("size"))

        register_secure_computation_node_in = cls(
            data_federation_id=data_federation_id,
            size=size,
        )

        register_secure_computation_node_in.additional_properties = d
        return register_secure_computation_node_in

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
