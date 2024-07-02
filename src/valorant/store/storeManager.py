from typing import List, TYPE_CHECKING, Optional
import requests

from .walletBalance import WalletBalance

if TYPE_CHECKING:
    from ..session import Session


class StoreManager:
    def __init__(self, session: "Session"):
        self.session = session

        # from table on https://valapidocs.techchrism.me/endpoint/owned-items
        self.item_name_to_ID = {
            "agents": "01bb38e1-da47-4e6a-9b3d-945fe4655707",
            "contracts": "f85cb6f7-33e5-4dc8-b609-ec7212301948",
            "sprays": "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475",
            "gun buddies": "dd3bf334-87f3-40bd-b043-682a57a8dc3a",
            "cards": "3f296c07-64c3-494c-923b-fe692a4fa1bd",
            "skins": "e7c63390-eda7-46e0-bb7a-a6abdacd2433",
            "skin variants": "3ad1b2b2-acdb-4524-852f-954a76ddae0a",
            "titles": "de7caa6b-adf7-4588-bbd1-143831e786c6"
        }

    def get_item_type_by_name(self, item_name: str) -> Optional[str]:
        return self.item_name_to_ID[item_name] if item_name in self.item_name_to_ID else None

    def get_storefront_raw(self) -> dict:
        if self.session.shard is None:
            self.session.get_region()

        return self.session.fetch(f"https://pd.{self.session.shard}.a.pvp.net/store/v2/storefront/{self.session.get_local_account().puuid}")

    def get_all_item_prices_raw(self) -> dict:
        if self.session.shard is None:
            self.session.get_region()

        return self.session.fetch(f"https://pd.{self.session.shard}.a.pvp.net/store/v1/offers/")

    def get_wallet_raw(self) -> dict:
        if self.session.shard is None:
            self.session.get_region()

        return self.session.fetch(f"https://pd.{self.session.shard}.a.pvp.net/store/v1/wallet/{self.session.get_local_account().puuid}")

    def get_wallet(self) -> WalletBalance:
        return WalletBalance.from_json(self.get_wallet_raw())

    def get_owned_items_raw(self, item_name: str) -> dict:
        if self.session.shard is None:
            self.session.get_region()

        item_type_ID = self.get_item_type_by_name(item_name.lower())

        if item_type_ID is None:
            raise RuntimeError(f"'{item_name.lower()}' is not a valid owned item name!\nSee: {self.item_name_to_ID}")

        return self.session.fetch(f"https://pd.{self.session.shard}.a.pvp.net/store/v1/entitlements/{self.session.get_local_account().puuid}/{item_type_ID}")
