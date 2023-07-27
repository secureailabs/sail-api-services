from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.data_model_dataframe import DataModelDataframe


T = TypeVar("T", bound="SaveDataModelVersionIn")


@attr.s(auto_attribs=True)
class SaveDataModelVersionIn:
    """
    Attributes:
        dataframes (List['DataModelDataframe']):
    """

    dataframes: List["DataModelDataframe"]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataframes = []
        for dataframes_item_data in self.dataframes:
            dataframes_item = dataframes_item_data.to_dict()

            dataframes.append(dataframes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataframes": dataframes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.data_model_dataframe import DataModelDataframe

        d = src_dict.copy()
        dataframes = []
        _dataframes = d.pop("dataframes")
        for dataframes_item_data in _dataframes:
            dataframes_item = DataModelDataframe.from_dict(dataframes_item_data)

            dataframes.append(dataframes_item)

        save_data_model_version_in = cls(
            dataframes=dataframes,
        )

        save_data_model_version_in.additional_properties = d
        return save_data_model_version_in

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
