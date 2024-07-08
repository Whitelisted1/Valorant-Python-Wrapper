from typing import List, TYPE_CHECKING, Union, Generator, Optional, Iterator
import requests

from .user import User
from .users import Users
from ..rank import Rank

if TYPE_CHECKING:
    from ..session import Session


class Players(Users):
    def __init__(self, session: "Session", *args, **kwargs):
        """
        Represents a group of in game players. Extends the Users class

        Parameters:
        session (Session): The Session object
        *args: additional arguments passed to the Users class init function
        **kwargs: additional keyword arguments passed to the Users class init function
        """

        super().__init__(session, *args, **kwargs)

        self.users: List[Player]

    def __iter__(self) -> Iterator["Player"]:
        return super().__iter__()


class Player(User):
    def __init__(self, session: "Session", puuid: str, agent: Optional[str] = None, team: Optional[str] = None, *args, **kwargs):
        """
        An object that represents an individual, in-game, Player

        Parameters:
        session (Session): The Session object
        puuid (str): The uuid of the player
        agent (str, optional, defaults to None): The agent that the player is playing as
        team (str, optional, defaults to None): The team that the player is playing on
        *args: additional arguments passed to the User init function
        **kwargs: additional keyword arguments passed to the User init function
        """

        super().__init__(session, puuid, *args, **kwargs)

        self.agent = agent
        self.team = team
