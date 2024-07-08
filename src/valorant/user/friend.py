from typing import List, TYPE_CHECKING, Union, Generator, Optional, Iterator
import requests

from .user import User
from .users import Users
from ..rank import Rank

if TYPE_CHECKING:
    from ..session import Session


class Friends(Users):
    def __init__(self, session: "Session", *args, **kwargs):
        """
        Represents a group of friends. Extends the Users class

        Parameters:
        session (Session): The Session object
        *args: additional arguments passed to the Users class init function
        **kwargs: additional keyword arguments passed to the Users class init function
        """

        super().__init__(session, *args, **kwargs)

        self.users: List[Friend]

    def __iter__(self) -> Iterator["Friend"]:
        return super().__iter__()


class Friend(User):
    def __init__(self, session: "Session", puuid: str, friend_note: Optional[str] = None, *args, **kwargs):
        """
        An object that represents an individual Friend

        Parameters:
        session (Session): The Session object
        puuid (str): The uuid of the friend
        friend_note (str, optional, defaults to None): The friend note of the friend
        *args: additional arguments passed to the User init function
        **kwargs: additional keyword arguments passed to the User init function
        """

        super().__init__(session, puuid, *args, **kwargs)

        self.friend_note = friend_note

    @staticmethod
    def from_json(session: "Session", data: dict):
        return Friend(session, data["puuid"], game_name=data["game_name"], game_tag=data["game_tag"], friend_note=data["note"])
