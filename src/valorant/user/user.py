from typing import List, TYPE_CHECKING, Union, Generator, Optional
import requests

from ..rank import Rank

if TYPE_CHECKING:
    from ..session import Session
    from ..match.match import Match
    from ..match.previousMatch import PreviousMatch


class User:
    def __init__(self, session: "Session", puuid: str, game_name: Optional[str] = None, game_tag: Optional[str] = None, incognito: bool = False, rank: Optional[Rank] = None, peak_rank: Optional[Rank] = None, account_level: int = 0, hide_account_level: bool = False, shard: str = "na", region: str = "na"):
        """
        An object that represents an individual User

        session (Session): The Session object
        puuid (str): The uuid of the user
        game_name (str, optional, defaults to None): The game name of the user
        game_tag (str, optional, defaults to None): The game tag of the user
        incognito (bool, defaults to False): Represents if the current user is in incognito mode
        rank (Rank, optional, defaults to None): The rank of the user
        peak_rank (Rank, optional, defaults to None): The peak rank of the user
        account_level (int, defaults to 0): The account level of the user
        hide_account_level (bool, defaults to False): Represents if we should hide the account level of the user
        shard (str, defaults to "na"): The shard of the user
        region (str, defaults to "na"): The region of the user
        """

        self.puuid: str = puuid
        self.session: "Session" = session

        self.pd_url: str = f"https://pd.{shard}.a.pvp.net"
        self.glz_url: str = f"https://glz-{shard}-1.{region}.a.pvp.net"

        self.shard: str = shard
        self.region: str = region

        self.game_name: Optional[str] = game_name
        self.game_tag: Optional[str] = game_tag
        self.incognito: bool = incognito

        self.rank: Optional[Rank] = rank
        self.peak_rank: Optional[Rank] = peak_rank

        self.account_level: int = account_level
        self.hide_account_level: bool = hide_account_level

    def get_name(self) -> str:
        """
        Fetches the name of the user

        Returns:
        str: The display name of the player
        """

        if not (self.game_name is None or self.game_tag is None):
            return self.game_name + "#" + self.game_tag

        content = self.session.fetch(f"{self.pd_url}/name-service/v2/players", method="PUT", json=[self.puuid])[0]

        self.game_name = content["GameName"]
        self.game_tag = content["TagLine"]

        return self.game_name + "#" + self.game_tag

    def get_rank(self) -> Rank:
        """
        Fetches the current rank of the user

        Returns:
        Rank: An object representing the rank of the user
        """

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
        """
        Fetches the peak rank of the user

        Returns:
        Rank: An object representing the peak rank of the user
        """

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
        """
        Fetches the raw ranked data for the user

        Returns:
        dict: A dictionary object containing the ranked data of the user
        """

        return self.session.fetch(f"{self.pd_url}/mmr/v1/players/{self.puuid}")

    # TEMP
    def get_ranked_data(self):
        return self.get_ranked_data_raw()

    def get_match_history_raw(self, start: int = 0, end: int = 20, queue_ID: Optional[str] = None) -> dict:
        """
        Fetches the raw match history for the user given start and end indices and the queue type

        Parameters:
        start (int, defaults to 0): The starting index of the match history
        end (int, defaults to 20): The ending index of the match history
        queue_ID (str, optional): The queue ID to get the history for (ex. "competitive")

        Returns:
        dict: A dictionary object containing the match history of the user
        """

        queue_url_parameter = f"&queue={queue_ID}" if queue_ID is not None else ""

        return self.session.fetch(f"{self.pd_url}/match-history/v1/history/{self.puuid}?startIndex={start}&endIndex={end}{queue_url_parameter}")

    def get_match_history(self, start: int = 0, end: int = 20, queue_ID: Optional[str] = None) -> List["PreviousMatch"]:
        """
        Fetches the match history for the user given start and end indices and the queue type

        Parameters:
        start (int, defaults to 0): The starting index of the match history
        end (int, defaults to 20): The ending index of the match history
        queue_ID (str, optional): The queue ID to get the history for (ex. "competitive")

        Returns:
        List["PreviousMatch"]: A list of the previous matches
        """

        matches_raw = self.get_match_history_raw(start, end, queue_ID=queue_ID)

        from ..match.previousMatch import PreviousMatch
        matches = []
        for m in matches_raw["History"]:
            matches.append(PreviousMatch(self.session, m["MatchID"], m["QueueID"], game_start_time=m["GameStartTime"]))

        return matches
