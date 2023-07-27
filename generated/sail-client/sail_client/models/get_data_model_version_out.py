import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.data_model_version_state import DataModelVersionState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_model_dataframe import DataModelDataframe
    from ..models.data_model_version_basic_info import DataModelVersionBasicInfo


T = TypeVar("T", bound="GetDataModelVersionOut")


@attr.s(auto_attribs=True)
class GetDataModelVersionOut:
    """
    Attributes:
        name (str):
        description (str):
        data_model_id (str):
        id (str):
        organization_id (str):
        user_id (str):
        dataframes (List['DataModelDataframe']):
        state (DataModelVersionState): An enumeration.
        previous_version_id (Union[Unset, str]):
        creation_time (Union[Unset, datetime.datetime]):
        last_save_time (Union[Unset, datetime.datetime]):
        commit_time (Union[Unset, datetime.datetime]):
        commit_message (Union[Unset, str]):
        revision_history (Union[Unset, List['DataModelVersionBasicInfo']]):
    """

    name: str
    description: str
    data_model_id: str
    id: str
    organization_id: str
    user_id: str
    dataframes: List["DataModelDataframe"]
    state: DataModelVersionState
    previous_version_id: Union[Unset, str] = UNSET
    creation_time: Union[Unset, datetime.datetime] = UNSET
    last_save_time: Union[Unset, datetime.datetime] = UNSET
    commit_time: Union[Unset, datetime.datetime] = UNSET
    commit_message: Union[Unset, str] = UNSET
    revision_history: Union[Unset, List["DataModelVersionBasicInfo"]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        data_model_id = self.data_model_id
        id = self.id
        organization_id = self.organization_id
        user_id = self.user_id
        dataframes = []
        for dataframes_item_data in self.dataframes:
            dataframes_item = dataframes_item_data.to_dict()

            dataframes.append(dataframes_item)

        state = self.state.value

        previous_version_id = self.previous_version_id
        creation_time: Union[Unset, str] = UNSET
        if not isinstance(self.creation_time, Unset):
            creation_time = self.creation_time.isoformat()

        last_save_time: Union[Unset, str] = UNSET
        if not isinstance(self.last_save_time, Unset):
            last_save_time = self.last_save_time.isoformat()

        commit_time: Union[Unset, str] = UNSET
        if not isinstance(self.commit_time, Unset):
            commit_time = self.commit_time.isoformat()

        commit_message = self.commit_message
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
                "data_model_id": data_model_id,
                "id": id,
                "organization_id": organization_id,
                "user_id": user_id,
                "dataframes": dataframes,
                "state": state,
            }
        )
        if previous_version_id is not UNSET:
            field_dict["previous_version_id"] = previous_version_id
        if creation_time is not UNSET:
            field_dict["creation_time"] = creation_time
        if last_save_time is not UNSET:
            field_dict["last_save_time"] = last_save_time
        if commit_time is not UNSET:
            field_dict["commit_time"] = commit_time
        if commit_message is not UNSET:
            field_dict["commit_message"] = commit_message
        if revision_history is not UNSET:
            field_dict["revision_history"] = revision_history

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.data_model_dataframe import DataModelDataframe
        from ..models.data_model_version_basic_info import DataModelVersionBasicInfo

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        data_model_id = d.pop("data_model_id")

        id = d.pop("id")

        organization_id = d.pop("organization_id")

        user_id = d.pop("user_id")

        dataframes = []
        _dataframes = d.pop("dataframes")
        for dataframes_item_data in _dataframes:
            dataframes_item = DataModelDataframe.from_dict(dataframes_item_data)

            dataframes.append(dataframes_item)

        state = DataModelVersionState(d.pop("state"))

        previous_version_id = d.pop("previous_version_id", UNSET)

        _creation_time = d.pop("creation_time", UNSET)
        creation_time: Union[Unset, datetime.datetime]
        if isinstance(_creation_time, Unset):
            creation_time = UNSET
        else:
            creation_time = isoparse(_creation_time)

        _last_save_time = d.pop("last_save_time", UNSET)
        last_save_time: Union[Unset, datetime.datetime]
        if isinstance(_last_save_time, Unset):
            last_save_time = UNSET
        else:
            last_save_time = isoparse(_last_save_time)

        _commit_time = d.pop("commit_time", UNSET)
        commit_time: Union[Unset, datetime.datetime]
        if isinstance(_commit_time, Unset):
            commit_time = UNSET
        else:
            commit_time = isoparse(_commit_time)

        commit_message = d.pop("commit_message", UNSET)

        revision_history = []
        _revision_history = d.pop("revision_history", UNSET)
        for revision_history_item_data in _revision_history or []:
            revision_history_item = DataModelVersionBasicInfo.from_dict(revision_history_item_data)

            revision_history.append(revision_history_item)

        get_data_model_version_out = cls(
            name=name,
            description=description,
            data_model_id=data_model_id,
            id=id,
            organization_id=organization_id,
            user_id=user_id,
            dataframes=dataframes,
            state=state,
            previous_version_id=previous_version_id,
            creation_time=creation_time,
            last_save_time=last_save_time,
            commit_time=commit_time,
            commit_message=commit_message,
            revision_history=revision_history,
        )

        get_data_model_version_out.additional_properties = d
        return get_data_model_version_out

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
