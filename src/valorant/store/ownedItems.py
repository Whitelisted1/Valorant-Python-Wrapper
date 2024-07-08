from typing import List


class OwnedItems:
    def __init__(self, item_type_ID: str, owned_item_IDs: List[str]):
        """
        An object that contains the owned items for a given item type ID

        Parameters:
        item_type_ID (str): The item type ID for the items in owned_item_IDs
        owned_item_IDs (List[str]): A list of uuids, represented as strings, that the user owns
        """

        self.item_type_ID = item_type_ID
        self.owned_item_IDs = owned_item_IDs

    @staticmethod
    def from_json(data: dict) -> "OwnedItems":
        return OwnedItems(
            data["ItemTypeID"],
            [item["ItemID"] for item in data["Entitlements"]]
        )
