from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.get_organizations_out import GetOrganizationsOut


T = TypeVar("T", bound="GetMultipleOrganizationsOut")


@attr.s(auto_attribs=True)
class GetMultipleOrganizationsOut:
    """
    Attributes:
        organizations (List['GetOrganizationsOut']):
    """

    organizations: List["GetOrganizationsOut"]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        organizations = []
        for organizations_item_data in self.organizations:
            organizations_item = organizations_item_data.to_dict()

            organizations.append(organizations_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organizations": organizations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_organizations_out import GetOrganizationsOut

        d = src_dict.copy()
        organizations = []
        _organizations = d.pop("organizations")
        for organizations_item_data in _organizations:
            organizations_item = GetOrganizationsOut.from_dict(organizations_item_data)

            organizations.append(organizations_item)

        get_multiple_organizations_out = cls(
            organizations=organizations,
        )

        get_multiple_organizations_out.additional_properties = d
        return get_multiple_organizations_out

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
