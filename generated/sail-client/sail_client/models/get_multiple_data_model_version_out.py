from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.get_data_model_version_out import GetDataModelVersionOut


T = TypeVar("T", bound="GetMultipleDataModelVersionOut")


@attr.s(auto_attribs=True)
class GetMultipleDataModelVersionOut:
    """
    Attributes:
        data_model_versions (List['GetDataModelVersionOut']):
    """

    data_model_versions: List["GetDataModelVersionOut"]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data_model_versions = []
        for data_model_versions_item_data in self.data_model_versions:
            data_model_versions_item = data_model_versions_item_data.to_dict()

            data_model_versions.append(data_model_versions_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_model_versions": data_model_versions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_data_model_version_out import GetDataModelVersionOut

        d = src_dict.copy()
        data_model_versions = []
        _data_model_versions = d.pop("data_model_versions")
        for data_model_versions_item_data in _data_model_versions:
            data_model_versions_item = GetDataModelVersionOut.from_dict(data_model_versions_item_data)

            data_model_versions.append(data_model_versions_item)

        get_multiple_data_model_version_out = cls(
            data_model_versions=data_model_versions,
        )

        get_multiple_data_model_version_out.additional_properties = d
        return get_multiple_data_model_version_out

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
