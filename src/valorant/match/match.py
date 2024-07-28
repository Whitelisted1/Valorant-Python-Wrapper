from typing import TYPE_CHECKING, Optional
import requests

from ..user.player import Players

if TYPE_CHECKING:
    from ..session import Session


class Match:
    def __init__(self, session: "Session", match_ID: str, map_ID: Optional[str] = None, mode_ID: Optional[str] = None, players: Optional["Players"] = None):
        self.session = session

        self.match_ID = match_ID
        self.map = map_ID
        self.mode = mode_ID

        if players is None: self.players = Players(session)
        else: self.players: Players = players

    def quit_match(self) -> None:
        """
        Quits the current match
        """

        if self.session.shard is None:
            self.session.get_region()

        self.session.fetch(f"{self.session.glz_url}/core-game/v1/players/{self.session.get_local_account().puuid}/disassociate/{self.match_ID}", method="POST")

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
