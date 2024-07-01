from typing import TYPE_CHECKING
import requests

if TYPE_CHECKING:
    from ..session import Session
    from ..user.player import Players


class Match:
    def __init__(self, session: "Session", matchID: str, mapID: str = None, modeID: str = None, players: "Players" = None, shard: str = "na", region: str = "na",):
        self.session = session

        self.matchID = matchID
        self.map = mapID
        self.mode = modeID

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

        return self.session.fetch(f"{self.pd_url}/match-details/v1/matches/{self.matchID}")

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

        return Match(session, data["MatchID"], mapID=data["MapID"], modeID=data["ModeID"], players=players)
