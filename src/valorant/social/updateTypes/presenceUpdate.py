from typing import TYPE_CHECKING

import xml.etree.ElementTree as ET
import json
import base64
from ...user.user import User
from ...rank import Rank


if TYPE_CHECKING:
    from ...session import Session


class PresenceUpdate:
    def __init__(self, session: "Session", XML_data: ET.Element):
        self.from_user = User(session, XML_data.attrib['from'].split("@")[0])
        self.to_user = User(session, XML_data.attrib['to'].split("@")[0])

        self.from_self = self.from_user.puuid == self.to_user.puuid

        self.base64_data = XML_data.find('.//p')
        if self.base64_data is None:
            return
        self.base64_data = json.loads(base64.b64decode(self.base64_data.text).decode())

        self.is_idle = self.base64_data["isIdle"]

        self.from_user.rank = Rank(self.base64_data["competitiveTier"], None)
