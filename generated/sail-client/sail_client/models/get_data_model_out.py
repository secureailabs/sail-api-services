import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.data_model_state import DataModelState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_object_info import BasicObjectInfo
    from ..models.data_model_version_basic_info import DataModelVersionBasicInfo


T = TypeVar("T", bound="GetDataModelOut")


@attr.s(auto_attribs=True)
class GetDataModelOut:
    """
    Attributes:
        name (str):
        description (str):
        id (str):
        maintainer_organization (BasicObjectInfo):
        state (DataModelState): An enumeration.
        tags (Union[Unset, List[str]]):
        creation_time (Union[Unset, datetime.datetime]):
        current_version_id (Union[Unset, str]):
        revision_history (Union[Unset, List['DataModelVersionBasicInfo']]):
    """

    name: str
    description: str
    id: str
    maintainer_organization: "BasicObjectInfo"
    state: DataModelState
    tags: Union[Unset, List[str]] = UNSET
    creation_time: Union[Unset, datetime.datetime] = UNSET
    current_version_id: Union[Unset, str] = UNSET
    revision_history: Union[Unset, List["DataModelVersionBasicInfo"]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        id = self.id
        maintainer_organization = self.maintainer_organization.to_dict()

        state = self.state.value

        tags: Union[Unset, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        creation_time: Union[Unset, str] = UNSET
        if not isinstance(self.creation_time, Unset):
            creation_time = self.creation_time.isoformat()

        current_version_id = self.current_version_id
        revision_history: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.revision_history, Unset):
            revision_history = []
            for revision_history_item_data in self.revision_history:
                revision_history_item = revision_history_item_data.to_dict()

                revision_history.append(revision_history_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "id": id,
                "maintainer_organization": maintainer_organization,
                "state": state,
            }
        )
        if tags is not UNSET:
            field_dict["tags"] = tags
        if creation_time is not UNSET:
            field_dict["creation_time"] = creation_time
        if current_version_id is not UNSET:
            field_dict["current_version_id"] = current_version_id
        if revision_history is not UNSET:
            field_dict["revision_history"] = revision_history

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.basic_object_info import BasicObjectInfo
        from ..models.data_model_version_basic_info import DataModelVersionBasicInfo

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        id = d.pop("id")

        maintainer_organization = BasicObjectInfo.from_dict(d.pop("maintainer_organization"))

        state = DataModelState(d.pop("state"))

        tags = cast(List[str], d.pop("tags", UNSET))

        _creation_time = d.pop("creation_time", UNSET)
        creation_time: Union[Unset, datetime.datetime]
        if isinstance(_creation_time, Unset):
            creation_time = UNSET
        else:
            creation_time = isoparse(_creation_time)

        current_version_id = d.pop("current_version_id", UNSET)

        revision_history = []
        _revision_history = d.pop("revision_history", UNSET)
        for revision_history_item_data in _revision_history or []:
            revision_history_item = DataModelVersionBasicInfo.from_dict(revision_history_item_data)

            revision_history.append(revision_history_item)

        get_data_model_out = cls(
            name=name,
            description=description,
            id=id,
            maintainer_organization=maintainer_organization,
            state=state,
            tags=tags,
            creation_time=creation_time,
            current_version_id=current_version_id,
            revision_history=revision_history,
        )

        get_data_model_out.additional_properties = d
        return get_data_model_out

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
