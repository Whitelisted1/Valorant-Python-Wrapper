from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session import Session


class Message:
    def __init__(self, session: "Session", type: str, puuid: str, message_ID: str, content: str, is_read: bool, timestamp: int):
        self.session = session

        self.type = type
        self.puuid = puuid if puuid != "" else None
        self.message_ID = message_ID
        self.content = content
        self.is_read = is_read
        self.timestamp = timestamp

    @staticmethod
    def from_json(session: "Session", data: dict) -> "Message":
        return Message(session, data["type"], data["puuid"], data["mid"], data["body"], data["read"], int(data["time"]))
