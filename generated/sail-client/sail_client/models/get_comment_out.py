import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_object_info import BasicObjectInfo


T = TypeVar("T", bound="GetCommentOut")


@attr.s(auto_attribs=True)
class GetCommentOut:
    """
    Attributes:
        id (str):
        user (BasicObjectInfo):
        organization (BasicObjectInfo):
        comment (str):
        time (Union[Unset, datetime.datetime]):
    """

    id: str
    user: "BasicObjectInfo"
    organization: "BasicObjectInfo"
    comment: str
    time: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        user = self.user.to_dict()

        organization = self.organization.to_dict()

        comment = self.comment
        time: Union[Unset, str] = UNSET
        if not isinstance(self.time, Unset):
            time = self.time.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "user": user,
                "organization": organization,
                "comment": comment,
            }
        )
        if time is not UNSET:
            field_dict["time"] = time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.basic_object_info import BasicObjectInfo

        d = src_dict.copy()
        id = d.pop("id")

        user = BasicObjectInfo.from_dict(d.pop("user"))

        organization = BasicObjectInfo.from_dict(d.pop("organization"))

        comment = d.pop("comment")

        _time = d.pop("time", UNSET)
        time: Union[Unset, datetime.datetime]
        if isinstance(_time, Unset):
            time = UNSET
        else:
            time = isoparse(_time)

        get_comment_out = cls(
            id=id,
            user=user,
            organization=organization,
            comment=comment,
            time=time,
        )

        get_comment_out.additional_properties = d
        return get_comment_out

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
