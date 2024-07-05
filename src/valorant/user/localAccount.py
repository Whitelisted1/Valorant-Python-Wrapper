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
    def __init__(self, session: "Session", fetch_information: bool = True, **kwargs):
        super().__init__(session, None, **kwargs)

        self.country = None

        if fetch_information:
            self.fetch_local_account_information()

    def fetch_local_account_information(self) -> "LocalAccount":        
        content = self.session.fetch("https://auth.riotgames.com/userinfo")

        self.puuid = content["sub"]
        self.country = content["country"]
        self.game_name = content["acct"]["game_name"]
        self.game_tag = content["acct"]["tag_line"]

        return self

    def get_friends(self) -> Friends:
        data = self.session.fetch_local("chat/v4/friends")

        friends = Friends(self.session, [])
        for friend in data["friends"]:
            friends.users.append(Friend.from_json(self.session, friend))

        return friends

    def get_current_game_raw(self) -> Optional[dict]:
        content = self.session.fetch(f"{self.glz_url}/core-game/v1/players/{self.puuid}")

        if "httpStatus" in content and content["httpStatus"] == 404:
            return None

        matchID = content["MatchID"]
        return self.session.fetch(f"{self.glz_url}/core-game/v1/matches/{matchID}", use_cache=False)

    def get_current_game(self) -> Optional["Match"]:
        current_game = self.get_current_game_raw()

        if current_game is None:
            return None

        from ..match.match import Match
        return Match.from_json(self.session, current_game)

    def get_current_pregame_raw(self) -> Optional[dict]:
        content = self.session.fetch(f"{self.glz_url}/pregame/v1/players/{self.puuid}", use_cache=False)

        if "httpStatus" in content and content["httpStatus"] == 404:
            return None

        matchID = content["MatchID"]
        return self.session.fetch(f"{self.glz_url}/pregame/v1/matches/{matchID}", use_cache=False)

    def get_current_pregame(self) -> "Pregame":
        current_game = self.get_current_pregame_raw()

        if current_game is None:
            return None

        from ..match.pregame import Pregame
        return Pregame.from_json(self.session, current_game)
