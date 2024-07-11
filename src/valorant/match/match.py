from typing import TYPE_CHECKING
import requests

if TYPE_CHECKING:
    from ..session import Session
    from ..user.player import Players


class Match:
    def __init__(self, session: "Session", match_ID: str, map_ID: str = None, mode_ID: str = None, players: "Players" = None, shard: str = "na", region: str = "na",):
        self.session = session

        self.match_ID = match_ID
        self.map = map_ID
        self.mode = mode_ID

        self.pd_url = f"https://pd.{shard}.a.pvp.net"
        self.glz_url = f"https://glz-{shard}-1.{region}.a.pvp.net"

        self.shard = shard
        self.region = region

        if players is None: self.players = Players(session)
        else: self.players: Players = players

    def get_match_data_raw(self) -> dict:
        """
        Fetches match data for this object

        Returns:
        dict: The JSON data which represents this Match's data
        """

        return self.session.fetch(f"{self.pd_url}/match-details/v1/matches/{self.match_ID}")

    def quit_match(self) -> None:
        """
        Quits the current match
        """

        if self.session.shard is None:
            self.session.get_region()

        self.session.fetch(f"https://glz-{self.session.region}-1.{self.session.shard}.a.pvp.net/core-game/v1/players/{self.session.get_local_account().puuid}/disassociate/{self.match_ID}", method="POST")

    @staticmethod
    def from_json(session: "Session", data: dict) -> "Match":
        from ..user.player import Player, Players

        players = Players(session)
        for player in data["Players"]:
            players.users.append(Player(
                session,
                player["Subject"],
                agent=player["CharacterID"],
                team=player["TeamID"],
                account_level=player["PlayerIdentity"]["AccountLevel"],
                hide_account_level=player["PlayerIdentity"]["HideAccountLevel"],
                incognito=player["PlayerIdentity"]["Incognito"]
            ))

        players.get_names()

        return Match(session, data["MatchID"], map_ID=data["MapID"], mode_ID=data["ModeID"], players=players)
