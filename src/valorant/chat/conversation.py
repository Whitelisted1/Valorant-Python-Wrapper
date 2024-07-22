from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session import Session


class Conversation:
    def __init__(self, session: "Session", conversation_ID: str, is_direct_message: bool = False, is_global: bool = False, is_muted: bool = False):
        self.session = session

        self.conversation_ID = conversation_ID
        self.is_direct_message = is_direct_message
        self.is_global = is_global
        self.is_muted = is_muted

    def send_message(self, content):
        pass

    def get_history_raw(self):
        return self.session.fetch_local(f"chat/v6/messages?cid={self.conversation_ID}", use_cache=False)

    @staticmethod
    def from_json(session: "Session", data: dict) -> "Conversation":
        return Conversation(session, data["cid"], is_direct_message=data["direct_messages"], is_global=data["global_readership"], is_muted=data["muted"])
