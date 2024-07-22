from typing import TYPE_CHECKING, List

from .conversation import Conversation

if TYPE_CHECKING:
    from ..session import Session


class Conversations:
    def __init__(self, session: "Session", conversations: List[Conversation] = None):
        self.session = session

        if conversations is None:
            self.conversations: List[Conversation] = []
        else:
            self.conversations: List[Conversation] = conversations

    def __iter__(self):
        return iter(self.conversations)

    @staticmethod
    def from_json(session: "Session", data: dict) -> "Conversations":
        return Conversations(session, [Conversation.from_json(session, c) for c in data])
