from typing import TYPE_CHECKING

from .match import Match

if TYPE_CHECKING:
    from ..session import Session


class Pregame(Match):
    def quit_match(self) -> None:
        """
        Quits the current pregame
        """

        if self.session.shard is None:
            self.session.get_region()

        self.session.fetch(f"{self.session.glz_url}/pregame/v1/matches/{self.match_ID}/quit", method="POST")

    @staticmethod
    def from_json(session: "Session", data: dict) -> "Pregame":
        from ..user.player import Player, Players

        players = Players(session)
        team = data["AllyTeam"]["TeamID"]
        for player in data["AllyTeam"]["Players"]:
            agent = player["CharacterID"] if player["CharacterID"] != "" else None

            p = Player(
                session,
                player["Subject"],
                agent=agent,
                team=team,
                account_level=player["PlayerIdentity"]["AccountLevel"],
                hide_account_level=player["PlayerIdentity"]["HideAccountLevel"],
                incognito=player["PlayerIdentity"]["Incognito"]
            )

            if p.hide_account_level:
                p.account_level = None

            players.users.append(p)

        players.get_names()

        return Pregame(session, data["ID"], map_ID=data["MapID"], mode_ID=data["Mode"], players=players)
