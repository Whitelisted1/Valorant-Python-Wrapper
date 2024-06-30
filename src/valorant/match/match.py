from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from session import Session
    from user.player import Players


class Match:
    def __init__(self, session: "Session", matchID: str, mapID: str = None, modeID: str = None, players: "Players" = None):
        self.matchID = matchID
        self.map = mapID
        self.mode = modeID

        if players is None: self.players = Players(session)
        else: self.players: Players = players

    @staticmethod
    def from_json(session: "Session", data: dict) -> "Match":
        from user.player import Player, Players

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

        return Match(session, data["MatchID"], mapID=data["MapID"], modeID=data["ModeID"], players=players)
