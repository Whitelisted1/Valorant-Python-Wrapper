from typing import List, TYPE_CHECKING
import requests


if TYPE_CHECKING:
    from ..session import Session


class StoreManager:
    def __init__(self, session: "Session"):
        self.session = session

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
