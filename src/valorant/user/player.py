from typing import List, TYPE_CHECKING, Union, Generator, Optional, Iterator
import requests

from .user import User
from .users import Users
from rank import Rank

if TYPE_CHECKING:
    from session import Session


class Players(Users):
    def __init__(self, session: "Session", *args, **kwargs):
        super().__init__(session, *args, **kwargs)

        self.users: List[Player]

    def __iter__(self) -> Iterator["Player"]:
        return super().__iter__()


class Player(User):
    def __init__(self, session: "Session", puuid: str, agent: str = None, team: str = None, **kwargs):
        super().__init__(session, puuid, **kwargs)

        self.agent = agent
        self.team = team
