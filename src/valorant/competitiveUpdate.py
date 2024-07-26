from typing import TYPE_CHECKING

from .rank import Rank


class CompetitiveUpdate:
    def __init__(self, game_start_time: int, before_rank: "Rank", after_rank: "Rank", rr_change: int, performance_bonus: int, afk_penalty: int, match_ID: str, map_ID: str, season_ID: str):
        self.game_start_time = game_start_time

        self.before_rank = before_rank
        self.after_rank = after_rank
        self.rr_change = rr_change

        self.performance_bonus = performance_bonus
        self.afk_penalty = afk_penalty

        self.match_ID = match_ID
        self.map_ID = map_ID
        self.season_ID = season_ID

    @staticmethod
    def from_json(data: dict) -> "CompetitiveUpdate":
            # from .rank import Rank
        return CompetitiveUpdate(
            data["MatchStartTime"],
            Rank(data["TierBeforeUpdate"], data["RankedRatingBeforeUpdate"]),
            Rank(data["TierAfterUpdate"], data["RankedRatingAfterUpdate"]),
            data["RankedRatingEarned"],
            data["RankedRatingPerformanceBonus"],
            data["AFKPenalty"],
            data["MatchID"],
            data["MapID"],
            data["SeasonID"]
        )
