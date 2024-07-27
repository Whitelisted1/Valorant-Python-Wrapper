from typing import TYPE_CHECKING, List, Optional

from .message import Message
from ..user.user import User

if TYPE_CHECKING:
    from ..session import Session


class Conversation:
    def __init__(self, session: "Session", conversation_ID: str, is_direct_message: bool = False, is_global: bool = False, is_muted: bool = False):
        self.session = session

        self.conversation_ID = conversation_ID
        self.is_direct_message = is_direct_message
        self.is_global = is_global
        self.is_muted = is_muted

    def send_message(self, content: str, type: str = "chat"):
        return self.session.fetch_local("chat/v6/messages", method="POST", use_cache=False, json={"cid": self.conversation_ID, "message": content, "type": type})

    def get_history_raw(self) -> dict:
        return self.session.fetch_local(f"chat/v6/messages?cid={self.conversation_ID}", use_cache=False)

    def get_history(self) -> List[Message]:
        history_raw = self.get_history_raw()["messages"]
        history: List[Message] = []

        for message in history_raw:
            history.append(Message.from_json(self.session, message))

        return history

    def get_participants_raw(self) -> dict:
        return self.session.fetch_local(f"chat/v5/participants?cid={self.conversation_ID}", use_cache=False)

    def get_participants(self, include_self: bool = True) -> List[User]:
        participants_raw = self.get_participants_raw()["participants"]
        participants: List[User] = []

        local_puuid = self.session.get_local_account().puuid

        for participant in participants_raw:
            if local_puuid == participant["puuid"] and not include_self:
                continue

            participants.append(User(self.session, participant["puuid"], game_name=participant["game_name"], game_tag=participant["game_tag"], region=participant["region"]))

        return participants

    @staticmethod
    def from_json(session: "Session", data: dict) -> "Conversation":
        return Conversation(session, data["cid"], is_direct_message=data["direct_messages"], is_global=data["global_readership"], is_muted=data["muted"])
