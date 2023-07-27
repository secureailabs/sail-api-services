import datetime
from typing import Any, Dict, List, Type, TypeVar

import attr
from dateutil.parser import isoparse

T = TypeVar("T", bound="DataModelVersionBasicInfo")


@attr.s(auto_attribs=True)
class DataModelVersionBasicInfo:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        commit_message (str):
        merge_time (datetime.datetime):
    """

    id: str
    name: str
    description: str
    commit_message: str
    merge_time: datetime.datetime
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        description = self.description
        commit_message = self.commit_message
        merge_time = self.merge_time.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "commit_message": commit_message,
                "merge_time": merge_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        commit_message = d.pop("commit_message")

        merge_time = isoparse(d.pop("merge_time"))

        data_model_version_basic_info = cls(
            id=id,
            name=name,
            description=description,
            commit_message=commit_message,
            merge_time=merge_time,
        )

        data_model_version_basic_info.additional_properties = d
        return data_model_version_basic_info

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
