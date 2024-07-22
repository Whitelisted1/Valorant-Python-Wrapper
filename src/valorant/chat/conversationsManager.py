from typing import List, TYPE_CHECKING, Union, Generator, Optional
import requests

from .conversations import Conversations

if TYPE_CHECKING:
    from ..session import Session


class ConversationsManager:
    def __init__(self, session: "Session"):
        self.session = session

    def get_conversations(self):
        return Conversations.from_json(self.session, self.session.fetch_local("chat/v6/conversations")["conversations"])
