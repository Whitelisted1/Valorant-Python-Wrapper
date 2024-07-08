from typing import List, TYPE_CHECKING, Optional
import requests

from .user import User

if TYPE_CHECKING:
    from ..session import Session


class Users:
    def __init__(self, session: "Session", users: Optional[List[User]] = None, shard: str = "na"):
        """
        An object that contains multiple User objects

        Parameters:
        session (Session): The Session object
        users (List[User], optional, defaults to None): A list of the current users
        shard (str, defaults to "na"): The shard that the players are in
        """

        if users is None: self.users = []
        else: self.users = users

        self.session = session

        self.shard = shard
        self.pd_url = f"https://pd.{shard}.a.pvp.net"

    def get_names(self) -> List[str]:
        """
        Fetches the names of all the users in self.users

        Returns:
        List[str]: A list of strings representing the username and tagline of each player
        """

        content = self.session.fetch(f"{self.pd_url}/name-service/v2/players", method="PUT", json=[u.puuid for u in self.users])

        for user, data in zip(self.users, content):
            user.game_name = data["GameName"]
            user.game_tag = data["TagLine"]

        return [u.game_name + "#" + u.game_tag for u in self.users]

    def __iter__(self):
        return iter(self.users)
