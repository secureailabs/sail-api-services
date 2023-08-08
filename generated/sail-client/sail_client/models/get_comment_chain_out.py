from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_comment_out import GetCommentOut


T = TypeVar("T", bound="GetCommentChainOut")


@attr.s(auto_attribs=True)
class GetCommentChainOut:
    """
    Attributes:
        data_model_id (str):
        id (Union[Unset, str]):
        comments (Union[Unset, List['GetCommentOut']]):
    """

    data_model_id: str
    id: Union[Unset, str] = UNSET
    comments: Union[Unset, List["GetCommentOut"]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data_model_id = self.data_model_id
        id = self.id
        comments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.comments, Unset):
            comments = []
            for comments_item_data in self.comments:
                comments_item = comments_item_data.to_dict()

                comments.append(comments_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_model_id": data_model_id,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if comments is not UNSET:
            field_dict["comments"] = comments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_comment_out import GetCommentOut

        d = src_dict.copy()
        data_model_id = d.pop("data_model_id")

        id = d.pop("id", UNSET)

        comments = []
        _comments = d.pop("comments", UNSET)
        for comments_item_data in _comments or []:
            comments_item = GetCommentOut.from_dict(comments_item_data)

            comments.append(comments_item)

        get_comment_chain_out = cls(
            data_model_id=data_model_id,
            id=id,
            comments=comments,
        )

        get_comment_chain_out.additional_properties = d
        return get_comment_chain_out

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
