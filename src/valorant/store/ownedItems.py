class OwnedItems:
    def __init__(self, item_type_ID: str, owned_item_ids: str):
        self.item_type_ID = item_type_ID
        self.owned_item_IDs = owned_item_ids

    @staticmethod
    def from_json(data: dict) -> "OwnedItems":
        return OwnedItems(
            data["ItemTypeID"],
            [item["ItemID"] for item in data["Entitlements"]]
        )
