from typing import TYPE_CHECKING, List, Optional

from .conversation import Conversation

if TYPE_CHECKING:
    from ..session import Session


class Conversations:
    def __init__(self, session: "Session", conversations: Optional[List[Conversation]] = None):
        self.session = session

        self.conversations: List[Conversation] = conversations
        if self.conversations is None:
            self.conversations: List[Conversation] = []

    def __iter__(self):
        return iter(self.conversations)

    @staticmethod
    def from_json(session: "Session", data: dict) -> "Conversations":
        return Conversations(session, conversations=[Conversation.from_json(session, c) for c in data])
