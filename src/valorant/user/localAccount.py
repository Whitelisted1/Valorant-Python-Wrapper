from typing import List, TYPE_CHECKING, Union, Generator, Optional
import requests

from .user import User
from .friend import Friend, Friends
from .users import Users
from ..rank import Rank

if TYPE_CHECKING:
    from ..session import Session
    from ..match.match import Match
    from ..match.pregame import Pregame


class LocalAccount(User):
    def __init__(self, session: "Session", fetch_information: bool = True, *args, **kwargs):
        """
        Represents the local account that is being run in the Valorant session

        Parameters:
        session (Session): The Session object
        fetch_information (bool, defaults to True): If True, automatically fetches user information (puuid, username, etc)
        *args: additional arguments passed to the User class init function
        **kwargs: additional keyword arguments passed to the User class init function
        """

        super().__init__(session, None, *args, **kwargs)

        self.country: Optional[str] = None

        if fetch_information:
            self.fetch_local_account_information()

    def fetch_local_account_information(self) -> None:
        """
        Fetches information relating to the local account from riot's servers
        """

        content = self.session.fetch("https://auth.riotgames.com/userinfo")

        self.puuid = content["sub"]
        self.country = content["country"]
        self.game_name = content["acct"]["game_name"]
        self.game_tag = content["acct"]["tag_line"]

    def get_friends(self) -> Friends:
        """
        Fetches all the friends for the local account

        Returns:
        Friends: An object that contains all the friends of the local user
        """

        data = self.session.fetch_local("chat/v4/friends", use_cache=False)

        friends = Friends(self.session, [])
        for friend in data["friends"]:
            friends.users.append(Friend.from_json(self.session, friend))

        return friends

    def get_current_game_raw(self) -> Optional[dict]:
        """
        Fetches the raw current game for the local user

        Returns:
        Optional[dict]: A dictionary or None object that contains data relating to the current game
        """

        content = self.session.fetch(f"{self.glz_url}/core-game/v1/players/{self.puuid}", use_cache=False)

        if "httpStatus" in content and content["httpStatus"] == 404:
            return None

        matchID = content["MatchID"]
        return self.session.fetch(f"{self.glz_url}/core-game/v1/matches/{matchID}", use_cache=False)

    def get_current_game(self) -> Optional["Match"]:
        """
        Fetches the current game for the local user

        Returns:
        Optional[Match]: A Match or None object that contains data relating to the current game
        """

        current_game = self.get_current_game_raw()

        if current_game is None:
            return None

        from ..match.match import Match
        return Match.from_json(self.session, current_game)

    def get_current_pregame_raw(self) -> Optional[dict]:
        """
        Fetches the raw current pregame for the local user

        Returns:
        Optional[dict]: A dictionary or None object that contains data relating to the current pregame
        """

        content = self.session.fetch(f"{self.glz_url}/pregame/v1/players/{self.puuid}", use_cache=False)

        if "httpStatus" in content and content["httpStatus"] == 404:
            return None

        matchID = content["MatchID"]
        return self.session.fetch(f"{self.glz_url}/pregame/v1/matches/{matchID}", use_cache=False)

    def get_current_pregame(self) -> "Pregame":
        """
        Fetches the current pregame for the local user

        Returns:
        Optional[Pregame]: A Pregame or None object that contains data relating to the current pregame
        """

        current_game = self.get_current_pregame_raw()

        if current_game is None:
            return None

        from ..match.pregame import Pregame
        return Pregame.from_json(self.session, current_game)

    def get_penalties(self) -> Optional[dict]:
        """
        Fetches the local user's matchmaking penalties. These are in an unknown format

        Returns:
        Optional[dict]: The matchmaking penalties
        """

        return self.session.fetch(f"{self.pd_url}/restrictions/v3/penalties", use_cache=False)["Penalties"]
