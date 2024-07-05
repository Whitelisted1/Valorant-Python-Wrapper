from typing import List, TYPE_CHECKING, Union, Generator, Optional
import requests

from ..rank import Rank

if TYPE_CHECKING:
    from ..session import Session
    from ..match.match import Match
    from ..match.pregame import Pregame


class User:
    def __init__(self, session: "Session", puuid: str, game_name=None, game_tag=None, incognito: bool = False, rank: Rank = None, peak_rank: Rank = None, account_level: int = 0, hide_account_level: bool = False, shard="na", region="na"):
        self.puuid: str = puuid
        self.session: "Session" = session

        self.pd_url: str = f"https://pd.{shard}.a.pvp.net"
        self.glz_url: str = f"https://glz-{shard}-1.{region}.a.pvp.net"

        self.shard: Optional[str] = shard
        self.region: Optional[str] = region

        self.game_name: Optional[str] = game_name
        self.game_tag: Optional[str] = game_tag
        self.incognito: bool = incognito

        self.rank: Optional[Rank] = rank
        self.peak_rank: Optional[Rank] = peak_rank

        self.account_level: int = account_level
        self.hide_account_level: bool = hide_account_level

    def get_name(self) -> str:
        if not (self.game_name is None or self.game_tag is None):
            return self.game_name + "#" + self.game_tag

        content = self.session.fetch(f"{self.pd_url}/name-service/v2/players", method="PUT", json=[self.puuid])[0]

        self.game_name = content["GameName"]
        self.game_tag = content["TagLine"]

        return self.game_name + "#" + self.game_tag

    def get_rank(self) -> Rank:
        if self.rank is not None:
            return self.rank

        data = self.get_ranked_data()
        rank = Rank(data["LatestCompetitiveUpdate"]["TierAfterUpdate"], data["LatestCompetitiveUpdate"]["RankedRatingAfterUpdate"])
        previous_ranked_seasons: dict = data["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]

        if rank.rank_index != 0 or previous_ranked_seasons is None:
            self.rank = rank
            return rank

        season_data: list = self.session.get_seasons_acts_events_raw()["Seasons"]
        season_data.reverse()

        for season in season_data:
            if season["ID"] not in previous_ranked_seasons:
                continue

            rank = Rank(previous_ranked_seasons[season["ID"]]["Rank"], previous_ranked_seasons[season["ID"]]["RankedRating"])
            self.rank = rank
            return rank

        self.rank = rank
        return rank

    def get_peak_rank(self) -> Rank:
        if self.peak_rank is not None:
            return self.peak_rank

        data: dict = self.get_ranked_data()["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]
        rank = Rank(0, 0)

        if data is None:
            self.peak_rank = rank
            return rank

        peak_rank = 0
        peak_rating = 0
        for season in data.values():
            if season["Rank"] > peak_rank:
                peak_rank = season["Rank"]
                peak_rating = season["RankedRating"]

            elif season["Rank"] == peak_rank and season["RankedRating"] > peak_rating:
                peak_rating = season["RankedRating"]

        rank = Rank(peak_rank, peak_rating)
        self.peak_rank = rank
        return rank

    def get_ranked_data_raw(self) -> dict:
        return self.session.fetch(f"{self.pd_url}/mmr/v1/players/{self.puuid}")

    # TEMP
    def get_ranked_data(self):
        return self.get_ranked_data_raw()

    def get_match_history_raw(self, start: int = 0, end: int = 20) -> dict:
        return self.session.fetch(f"{self.pd_url}/match-history/v1/history/{self.puuid}?startIndex={start}&endIndex={end}&queue=competitive")

    # TEMP
    def get_match_history(self, start: int = 0, end: int = 20) -> List["Match"]:
        return self.get_match_history_raw(start, end)

        # from match.match import Match
        matches = []
        for m in r.json()["History"]:
            matches.append(Match(self.session, m["MatchID"], m["QueueID"], self.session.auth, gameStartTime=m["GameStartTime"]))
            # matches.append(Match.from_json(self.session, m))

        return matches
