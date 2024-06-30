from typing import List, TYPE_CHECKING, Union, Generator, Optional, Iterator
import requests

from .user import User
from .users import Users
from ..rank import Rank

if TYPE_CHECKING:
    from ..session import Session


class Friends(Users):
    def __init__(self, session: "Session", *args, **kwargs):
        super().__init__(session, *args, **kwargs)

        self.users: List[Friend]

    def __iter__(self) -> Iterator["Friend"]:
        return super().__iter__()


class Friend(User):
    def __init__(self, session: "Session", puuid: str, friend_note: str = None, **kwargs):
        super().__init__(session, puuid, **kwargs)

        self.friend_note = friend_note

    @staticmethod
    def from_json(session: "Session", data: dict):
        return Friend(session, data["puuid"], game_name=data["game_name"], game_tag=data["game_tag"], friend_note=data["note"])
