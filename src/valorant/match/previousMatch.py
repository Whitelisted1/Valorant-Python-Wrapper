from typing import TYPE_CHECKING, Optional

from .match import Match
from ..user.player import Players

if TYPE_CHECKING:
    from ..session import Session


class PreviousMatch(Match):
    def __init__(self, session: "Session", match_ID: str, mode_ID: str, game_start_time: int, map_ID: Optional[str] = None, players: Optional["Players"] = None, shard: str = "na", region: str = "na"):
        super().__init__(session, match_ID, map_ID=map_ID, mode_ID=mode_ID, players=players, shard=shard, region=region)

        self.game_start_time = game_start_time

    def get_match_data_raw(self) -> dict:
        """
        Fetches match data for this object

        Returns:
        dict: The JSON data which represents this Match's data
        """

        return self.session.fetch(f"{self.pd_url}/match-details/v1/matches/{self.match_ID}")
