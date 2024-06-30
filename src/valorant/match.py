from typing import List, TYPE_CHECKING, Union, Generator, Optional
import requests

if TYPE_CHECKING:
    from authorization import AuthorizationHandler


class Match:
    def __init__(self, matchID: str, QueueID: str, auth: "AuthorizationHandler", shard: str = "na", region: str = "na", gameStartTime: Optional[int] = None):
        self.matchID = matchID
        self.auth = auth

        self.pd_url = f"https://pd.{shard}.a.pvp.net"
        self.glz_url = f"https://glz-{shard}-1.{region}.a.pvp.net"

        self.shard = shard
        self.region = region

    def get_match_data(self):
        # https://pd.{shard}.a.pvp.net/match-details/v1/matches/{matchID}
        r = requests.get(f"{self.pd_url}/match-details/v1/matches/{self.matchID}", headers=self.auth.auth_headers)

        return r.json()
