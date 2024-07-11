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
        """
        An object that represents a presence update

        Parameters:
        session (Session): The Session object
        XML_data (ET.Element): The XML data from the XMPP server
        """

        self.raw = XML_data

        self.from_user = User(session, XML_data.attrib['from'].split("@")[0])
        self.to_user = User(session, XML_data.attrib['to'].split("@")[0])
        self.is_self = self.from_user.puuid == self.to_user.puuid

        self.presence_data = XML_data.find('.//p')

        self.is_unavailable = "type" in XML_data.attrib and XML_data.attrib["type"] == "unavailable"
        self.invalid = self.presence_data is None

        if self.is_unavailable or self.invalid:
            return

        self.presence_data = json.loads(base64.b64decode(self.presence_data.text).decode())

        self.from_user.rank = Rank(self.presence_data["competitiveTier"], None)
        self.from_user.account_level = self.presence_data["accountLevel"]

        self.is_idle = self.presence_data["isIdle"]

        self.queueID = self.presence_data["queueId"]
        self.currentState = self.presence_data["sessionLoopState"]

        self.partySize = self.presence_data["partySize"]
        self.maxPartySize = self.presence_data["maxPartySize"]

        self.allyTeamScore = self.presence_data["partyOwnerMatchScoreAllyTeam"]
        self.enemyTeamScore = self.presence_data["partyOwnerMatchScoreEnemyTeam"]

        self.team = self.presence_data["partyOwnerMatchCurrentTeam"]
        self.map = self.presence_data["matchMap"]

        self.partyID = self.presence_data["partyId"]

        if self.currentState == "INGAME" and self.team == "":
            self.invalid = True
            return
