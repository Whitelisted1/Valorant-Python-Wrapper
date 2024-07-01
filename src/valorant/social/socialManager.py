from typing import Callable, List, TYPE_CHECKING, Any, Optional, Generator
import threading
import socket
import ssl
import xml.etree.ElementTree as ET

from .xmlParser import XMLParser

from .updateTypes.presenceUpdate import PresenceUpdate

if TYPE_CHECKING:
    from ..session import Session


class Listener:
    def __init__(self, callback: Callable[[ET.Element], Any], message_type: Optional[str] = None):
        self.callback = callback
        self.message_type = message_type


class ServerDetails:
    def __init__(self, server: str, port: int, xmppRegion: str):
        self.server: str = server
        self.port: int = port
        self.xmppRegion: str = xmppRegion


class SocialManager:
    def __init__(self, session: "Session"):
        self.session: "Session" = session

        self.listeners: List[Listener] = []
        self.is_listening: bool = False
        self.listening_thread: Optional[threading.Thread] = None
        self.xml_parser: XMLParser = XMLParser()

        self.tls_socket: ssl.SSLSocket = None

        self.tag_to_class = {
            "presence": PresenceUpdate
        }

    def send_message(self, content: str) -> None:
        """
        Send a message with self.tls_socket

        Parameters:
        content (str): The content of the message
        """

        if not self.is_listening or self.tls_socket is None:
            raise RuntimeError("Unable to send message. self.is_listening is False or self.tls_socket is None.")

        self.tls_socket.sendall(content.encode())

    def receive_message(self) -> str:
        """
        Receives a message with self.tls_socket
        """

        if not self.is_listening or self.tls_socket is None:
            raise RuntimeError("Unable to receive message. self.is_listening is False or self.tls_socket is None.")

        response: str = ""

        while True:
            chunk = self.tls_socket.recv(1024).decode("utf-8")
            response += chunk

            if len(chunk) < 1024:
                break

        return response

    def get_server_details(self) -> ServerDetails:
        """
        Fetches the config for the Riot Client

        Returns:
        ServerDetails: An object which includes the server, port and region
        """

        region_affinity = self.session.auth.get_pas_data()["payload"]["affinity"]

        riot_client_config = self.session.fetch(f"https://clientconfig.rpg.riotgames.com/api/v1/config/player?os=windows&region={region_affinity}&app=Riot%20Client")

        server = riot_client_config["chat.affinities"][region_affinity]
        port = riot_client_config["chat.port"]
        xmppRegion = riot_client_config["chat.affinity_domains"][region_affinity]

        return ServerDetails(server, port, xmppRegion)

    def send_auth_messages(self, server_details: ServerDetails, PAS_token: str, RSO_token: str, entitlement: str):
        auth_messages = [
            {"content": f'<?xml version="1.0" encoding="UTF-8"?><stream:stream to="{server_details.xmppRegion}.pvp.net" xml:lang="en" version="1.0" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams">"', "receiveAfter": 2},
            {"content": f'<auth mechanism="X-Riot-RSO-PAS" xmlns="urn:ietf:params:xml:ns:xmpp-sasl"><rso_token>{RSO_token}</rso_token><pas_token>{PAS_token}</pas_token></auth>', "receiveAfter": 1},
            {"content": f'<?xml version="1.0"?><stream:stream to="{server_details.xmppRegion}.pvp.net" version="1.0" xmlns:stream="http://etherx.jabber.org/streams">', "receiveAfter": 2},
            {"content": '<iq id="_xmpp_bind1" type="set"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"></bind></iq>', "receiveAfter": 1},
            {"content": '<iq id="_xmpp_session1" type="set"><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></iq>', "receiveAfter": 1},
            {"content": f'<iq id="xmpp_entitlements_0" type="set"><entitlements xmlns="urn:riotgames:entitlements"><token xmlns="">{entitlement}</token></entitlements></iq>', "receiveAfter": 1},
        ]

        for message in auth_messages:
            self.send_message(message["content"])

            for _ in range(message["receiveAfter"]):
                self.receive_message()

    def receive_messages_generator(self) -> Generator[str, None, None]:
        while True:
            yield self.receive_message()

    def _start_listening(self):
        # Create a regular socket and wrap it with TLS
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tls_socket = ssl.wrap_socket(raw_socket)

        # get server details
        server_details = self.get_server_details()

        # get various tokens and entitlement details
        self.session.auth.get_pas_data()
        PAS_token = self.session.auth.pas_token
        RSO_token = self.session.auth.auth_headers['Authorization'][len("Bearer "):]
        entitlement = self.session.auth.auth_headers["X-Riot-Entitlements-JWT"]

        self.tls_socket.connect((server_details.server, server_details.port))

        self.send_auth_messages(server_details, PAS_token, RSO_token, entitlement)

        self.send_message("<presence/>")
        self.send_message('<iq type="get" id="2"><query xmlns="jabber:iq:riotgames:roster" last_state="true" /></iq>')

        self.xml_parser.parse_stream(self.receive_messages_generator(), self.send_event)

    def start_listening(self):
        if self.is_listening:
            return

        self.is_listening = True

        self.listening_thread = threading.Thread(target=self._start_listening, daemon=True)
        self.listening_thread.start()

    def stop_listening(self):
        if not self.is_listening:
            return

        self.is_listening = False

        # ...

    def convert_tag_to_class(self, tag_name: str):
        return self.tag_to_class[tag_name] if tag_name in self.tag_to_class else None

    def send_event(self, output: str):
        for xml in output:
            data = ET.fromstring(xml)

            tag = data.tag.split('}')[1] if '}' in data.tag else data.tag
            tag_class = self.convert_tag_to_class(tag)

            if tag_class is not None:
                data = tag_class(self.session, data)

                if data.invalid:
                    continue

            for listener in self.listeners:
                # if tag_class is None and listener.message_type is not None:
                #     continue

                if listener.message_type is not None and tag.lower() != listener.message_type.lower():
                    continue

                listener.callback(data)

    def add_callback(self, callback: Callable[[ET.Element], Any], message_type: Optional[str] = None):
        self.listeners.append(Listener(callback, message_type))

    # Throw a custom error in the future
    def remove_callback(self, callback):
        for listener in self.listeners:
            if listener.callback is callback:
                self.listeners.remove(listener)
                break
