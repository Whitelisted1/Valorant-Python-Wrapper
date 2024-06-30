from typing import TYPE_CHECKING

from .match import Match

if TYPE_CHECKING:
    from session import Session


class Pregame(Match):
    @staticmethod
    def from_json(session: "Session", data: dict) -> "Pregame":
        from user.player import Player, Players

        players = Players(session)
        team = data["AllyTeam"]["TeamID"]
        for player in data["AllyTeam"]["Players"]:
            agent = player["CharacterID"] if player["CharacterID"] != "" else None

            players.users.append(Player(
                session,
                player["Subject"],
                agent=agent,
                team=team,
                account_level=player["PlayerIdentity"]["AccountLevel"],
                hide_account_level=player["PlayerIdentity"]["HideAccountLevel"],
                incognito=player["PlayerIdentity"]["Incognito"]
            ))

        return Pregame(session, data["ID"], mapID=data["MapID"], modeID=data["Mode"], players=players)
