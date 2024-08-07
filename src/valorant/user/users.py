from typing import List, TYPE_CHECKING, Optional
import requests

from .user import User

if TYPE_CHECKING:
    from ..session import Session


class IncognitoFilter:
    def __init__(self, visible_users: List[User], incognito_users: List[User]):
        self.visible_users = visible_users
        self.incognito_users = incognito_users


class Users:
    def __init__(self, session: "Session", users: Optional[List[User]] = None):
        """
        An object that contains multiple User objects

        Parameters:
        session (Session): The Session object
        users (List[User], optional, defaults to None): A list of the current users
        """

        if users is None: self.users = []
        else: self.users = users

        self.session = session

    def filter_for_incognito(self) -> IncognitoFilter:
        """
        Returns an IncognitoFilter, which separates the visible from the incognito users

        Returns:
        IncognitoFilter: The object containing the visible/incognito users
        """

        filtered = IncognitoFilter([], [])

        for user in self.users:
            if user.incognito:
                filtered.incognito_users.append(user)
                continue

            filtered.visible_users.append(user)

        return filtered

    def get_names(self) -> List[str]:
        """
        Fetches the names of all the users in self.users

        Returns:
        List[str]: A list of strings representing the username and tagline of each player. Does not include incognito players
        """


        filtered = self.filter_for_incognito()
        content = self.session.fetch(f"{self.session.pd_url}/name-service/v2/players", method="PUT", json=[u.puuid for u in filtered.visible_users])

        for user, data in zip(filtered.visible_users, content):
            user.game_name = data["GameName"]
            user.game_tag = data["TagLine"]

        return [u.game_name + "#" + u.game_tag for u in filtered.visible_users]

    def __iter__(self):
        return iter(self.users)
