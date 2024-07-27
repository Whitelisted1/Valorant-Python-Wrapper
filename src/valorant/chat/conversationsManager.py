from typing import List, TYPE_CHECKING, Union, Generator, Optional
import requests

from .conversations import Conversations

if TYPE_CHECKING:
    from ..session import Session


class ConversationsManager:
    def __init__(self, session: "Session"):
        self.session = session

    def get_direct_conversations_raw(self) -> dict:
        return self.session.fetch_local("chat/v6/conversations", use_cache=False)

    def get_direct_conversations(self) -> Conversations:
        return Conversations.from_json(self.session, self.get_direct_conversations_raw()["conversations"])

    def get_game_conversations_raw(self) -> dict:
        return self.session.fetch_local("chat/v6/conversations/ares-coregame", use_cache=False)

    def get_game_conversations(self) -> Conversations:
        return Conversations.from_json(self.session, self.get_game_conversations_raw()["conversations"])
