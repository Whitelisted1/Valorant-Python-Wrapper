from typing import List, TYPE_CHECKING, Optional
import requests

from .walletBalance import WalletBalance
from .ownedItems import OwnedItems
from .storeFront import StoreFront

if TYPE_CHECKING:
    from ..session import Session


class StoreManager:
    def __init__(self, session: "Session"):
        self.session = session

    def get_storefront_raw(self) -> dict:
        if self.session.shard is None:
            self.session.get_region()

        return self.session.fetch(f"https://pd.{self.session.shard}.a.pvp.net/store/v2/storefront/{self.session.get_local_account().puuid}")

    def get_storefront(self) -> StoreFront:
        return StoreFront.from_json(self.session, self.get_storefront_raw())

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

    def get_owned_items_raw(self, item_ID: str) -> dict:
        if self.session.shard is None:
            self.session.get_region()

        return self.session.fetch(f"https://pd.{self.session.shard}.a.pvp.net/store/v1/entitlements/{self.session.get_local_account().puuid}/{item_ID}")

    def get_owned_items(self, item_name: str) -> OwnedItems:
        return OwnedItems.from_json(self.get_owned_items_raw(item_name))
