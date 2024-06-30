from typing import List, TYPE_CHECKING
import requests


if TYPE_CHECKING:
    from session import Session


class StoreManager:
    def __init__(self, session: "Session"):
        self.session = session

    def get_storefront(self) -> dict:
        if self.session.shard is None:
            self.session.get_region()

        r = requests.get(f"https://pd.{self.session.shard}.a.pvp.net/store/v2/storefront/{self.session.get_local_account().puuid}", headers=self.session.auth.auth_headers)

        return r.json()

    def get_all_item_prices(self):
        if self.session.shard is None:
            self.session.get_region()

        r = requests.get(f"https://pd.{self.session.shard}.a.pvp.net/store/v1/offers/", headers=self.session.auth.auth_headers)

        return r.json()

    def get_wallet(self):
        if self.session.shard is None:
            self.session.get_region()

        r = requests.get(f"https://pd.{self.session.shard}.a.pvp.net/store/v1/wallet/{self.session.get_local_account().puuid}", headers=self.session.auth.auth_headers)

        return r.json()
