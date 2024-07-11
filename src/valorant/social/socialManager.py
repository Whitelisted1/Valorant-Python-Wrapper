from typing import Callable, List, TYPE_CHECKING, Any, Optional, Generator, AsyncGenerator
import threading
import socket
import ssl
import time
import xml.etree.ElementTree as ET
import asyncio

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
        """
        Helps to manage the XML data that that comes from the presence/social XMPP connection

        Parameters:
        session (Session): The Session object
        """

        self.session: "Session" = session

        self.listeners: List[Listener] = []
        self.is_listening: bool = False

        self.listening_thread: Optional[threading.Thread] = None
        self.listening_thread_flag = threading.Event()
        self.exit_flag = asyncio.Event()

        self.ping_task: Optional[asyncio.Task] = None
        self.get_messages_task: Optional[asyncio.Task] = None

        self.xml_parser: XMLParser = XMLParser()

        self.tls_socket: ssl.SSLSocket = None

        self.tag_to_class = {
            "presence": PresenceUpdate
        }

    async def send_message(self, content: str) -> None:
        """
        Send a message with self.tls_socket

        Parameters:
        content (str): The content of the message
        """

        if not self.is_listening or self.tls_socket is None:
            raise RuntimeError("Unable to send message. self.is_listening is False or self.tls_socket is None.")

        await asyncio.to_thread(self.tls_socket.sendall, content.encode())

    async def receive_message(self) -> str:
        """
        Receives a message with self.tls_socket
        """

        if not self.is_listening or self.tls_socket is None:
            raise RuntimeError("Unable to receive message. self.is_listening is False or self.tls_socket is None.")

        response: str = ""

        while True:
            chunk = (await asyncio.to_thread(self.tls_socket.recv, 1024)).decode("utf-8")
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

        region_affinity = self.session.auth.get_pas_token()["payload"]["affinity"]

        riot_client_config = self.session.fetch(f"https://clientconfig.rpg.riotgames.com/api/v1/config/player?os=windows&region={region_affinity}&app=Riot%20Client")

        server = riot_client_config["chat.affinities"][region_affinity]
        port = riot_client_config["chat.port"]
        xmppRegion = riot_client_config["chat.affinity_domains"][region_affinity]

        return ServerDetails(server, port, xmppRegion)

    async def send_ping(self):
        """
        Sends a ping to the server every 20 seconds
        """

        while True:
            try:
                await asyncio.sleep(20)
                await self.send_message(" ")
            except asyncio.CancelledError:
                break

    async def receive_messages(self):
        """
        Begins the process of receiving messages from the server
        """

        async def gen():
            while True:
                try:
                    yield await self.receive_message()
                except asyncio.CancelledError:
                    break

        await self.xml_parser.parse_stream(gen(), self.send_event)

    async def send_auth_messages(self, server_details: ServerDetails, PAS_token: str, RSO_token: str, entitlement: str):
        """
        Sends authentication messages via the XMPP connection

        Parameters:
        server_details (ServerDetails): The server details
        PAS_token (str): The PAS token to do authentication with
        RSO_token (str): The RSO token to do authentication with
        entitlement (str): The entitlement token to do authentication with
        """

        auth_messages = [
            {"content": f'<?xml version="1.0" encoding="UTF-8"?><stream:stream to="{server_details.xmppRegion}.pvp.net" xml:lang="en" version="1.0" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams">"', "receiveAfter": 2},
            {"content": f'<auth mechanism="X-Riot-RSO-PAS" xmlns="urn:ietf:params:xml:ns:xmpp-sasl"><rso_token>{RSO_token}</rso_token><pas_token>{PAS_token}</pas_token></auth>', "receiveAfter": 1},
            {"content": f'<?xml version="1.0"?><stream:stream to="{server_details.xmppRegion}.pvp.net" version="1.0" xmlns:stream="http://etherx.jabber.org/streams">', "receiveAfter": 2},
            {"content": '<iq id="_xmpp_bind1" type="set"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"></bind></iq>', "receiveAfter": 1},
            {"content": '<iq id="_xmpp_session1" type="set"><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></iq>', "receiveAfter": 1},
            {"content": f'<iq id="xmpp_entitlements_0" type="set"><entitlements xmlns="urn:riotgames:entitlements"><token xmlns="">{entitlement}</token></entitlements></iq>', "receiveAfter": 1},
        ]

        for message in auth_messages:
            await self.send_message(message["content"])

            for _ in range(message["receiveAfter"]):
                await self.receive_message()

    async def _start_listening(self):
        """
        Internal method to connect to the XMPP server
        """

        self.exit_flag.clear()

        # Create a regular socket and wrap it with TLS
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tls_socket = ssl.wrap_socket(raw_socket)

        # get server details
        server_details = self.get_server_details()

        # get various tokens and entitlement details
        self.session.auth.get_pas_token()
        PAS_token = self.session.auth.pas_token
        RSO_token = self.session.auth.get_auth_headers()['Authorization'][len("Bearer "):]
        entitlement = self.session.auth.get_auth_headers()["X-Riot-Entitlements-JWT"]

        # actually connect to the server
        self.tls_socket.connect((server_details.server, server_details.port))

        # send auth messages
        await self.send_auth_messages(server_details, PAS_token, RSO_token, entitlement)

        # get presence updates and request a list of friends
        await self.send_message("<presence/>")
        await self.send_message('<iq type="get" id="2"><query xmlns="jabber:iq:riotgames:roster" last_state="true" /></iq>')

        # init the pinging task and receive_messages task
        self.ping_task = asyncio.create_task(self.send_ping())
        self.get_messages_task = asyncio.create_task(self.receive_messages())

        # allow for the main thread to continue
        self.listening_thread_flag.set()

        # wait until the exit flag is set
        await self.exit_flag.wait()

    def start_listening(self):
        """
        Connect to the presence and social XMPP server and begin calling callbacks from self.add_callback
        """

        if self.is_listening:
            return

        self.is_listening = True
        self.listening_thread_flag.clear()

        def run_listening_thread():
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._start_listening())
            loop.close()

        # start the listening thread
        self.listening_thread = threading.Thread(target=run_listening_thread, daemon=True)
        self.listening_thread.start()

        # wait for the listening thread to allow us to continue
        self.listening_thread_flag.wait()

    def stop_listening(self):
        """
        Disconnect from the XMPP server and stop calling callbacks
        """

        if not self.is_listening:
            return

        self.is_listening = False
        self.exit_flag.set()

        self.get_messages_task.cancel()
        self.ping_task.cancel()
        self.tls_socket.close()
        self.listening_thread.join()

        self.get_messages_task = None
        self.ping_task = None
        self.listening_thread = None
        self.tls_socket = None

    def convert_tag_to_class(self, tag_name: str):
        return self.tag_to_class[tag_name] if tag_name in self.tag_to_class else None

    def send_event(self, event_data: str):
        """
        Sends an event to the callbacks added from self.add_callback

        Parameters:
        event_data (str): The data that will be sent to the callbacks
        """

        for xml in event_data:
            data = ET.fromstring(xml)

            tag = data.tag.split('}')[1] if '}' in data.tag else data.tag
            tag_class = self.convert_tag_to_class(tag)

            if tag_class is not None:
                data = tag_class(self.session, data)

                if data.invalid:
                    continue

            for listener in self.listeners:
                if listener.message_type is not None and tag.lower() != listener.message_type.lower():
                    continue

                listener.callback(data)

    def add_callback(self, callback: Callable[[ET.Element], Any], message_type: Optional[str] = None):
        """
        Add a callback to be called when an XMPP message is received

        Parameters:
        callback (Callable[[ET.Element], Any]): The callback to be called
        message_type (str, optional): The tag that the XML data from the XMPP server has to be in order for this callback to be called (see self.tag_to_class). If None, the callback will be called for every received message
        """

        self.listeners.append(Listener(callback, message_type))

    def remove_callback(self, callback: Callable[[ET.Element], Any]):
        """
        Removes the given callback as a listener

        Parameters:
        callback (Callable[[ET.Element], Any]): The callback to remove from self.listeners
        """

        for listener in self.listeners:
            if listener.callback is callback:
                self.listeners.remove(listener)
                return

        raise ValueError("Callback not in listeners")
