from typing import List, TYPE_CHECKING

import os
import requests
import base64
import json

from . import utilities

if TYPE_CHECKING:
    from .session import Session


class AuthorizationManager:
    def __init__(self, session: "Session"):
        """
        Manages getting authentication information from local endpoints and from the lockfile

        Parameters:
        session (Session): The Session object
        """

        self.session = session

        self.lockfile_path = os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')
        self.lockfile_contents = None

        self.local_auth_headers = None
        self.auth_headers = None

        self.parsed_pas_token = None
        self.pas_token = None

    def get_lockfile_contents(self) -> dict:
        """
        Gets the current lockfile contents

        Returns:
        dict: The lockfile contents as a dictionary
        """

        f = open(self.lockfile_path, "r")
        content = f.read().split(":")
        f.close()

        self.lockfile_contents = dict(zip(['name', 'PID', 'port', 'password', 'protocol'], content))

        self.local_auth_headers = {
            'Authorization': 'Basic ' + base64.b64encode(('riot:' + self.lockfile_contents['password']).encode()).decode()
        }

        return self.lockfile_contents

    def get_auth_headers(self, force_renew: bool = False) -> dict:
        """
        Fetches the current authentication headers

        Parameters:
        force_renew (bool, defaults to False): If True it forces the renewal of new authentication headers

        Returns:
        dict: The headers as a dictionary
        """

        if self.auth_headers is not None and not force_renew:
            return self.auth_headers

        if self.lockfile_contents is None:
            self.get_lockfile_contents()

        data = self.session.fetch_local("entitlements/v1/token", use_cache=False)

        self.auth_headers = {
            'Authorization': f"Bearer {data['accessToken']}",
            'X-Riot-Entitlements-JWT': data['token'],
            'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjog"
                                        "IldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5"
                                        "MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
            'X-Riot-ClientVersion': self.session.get_game_version(),
            "User-Agent": "ShooterGame/13 Windows/10.0.19043.1.256.64bit"
        }

        return self.auth_headers

    def get_pas_token(self, force_renew: bool = False) -> dict:
        """
        Fetches the PAS JWT

        Parameters:
        force_renew (bool, defaults to False): If True it forces the renewal of new authentication headers

        Returns:
        dict: The parsed PAS token containing the header, payload and signature
        """

        if self.pas_token is not None and not force_renew:
            return self.parsed_pas_token

        r = requests.get("https://riot-geo.pas.si.riotgames.com/pas/v1/service/chat", headers=self.get_auth_headers())

        JWT_TOKEN = r.content.decode().split(".")

        HEADER = json.loads(utilities.base64_url_decode(JWT_TOKEN[0]).decode("utf-8"))
        PAYLOAD = json.loads(utilities.base64_url_decode(JWT_TOKEN[1]).decode("utf-8"))
        SIGNATURE = JWT_TOKEN[2]

        self.parsed_pas_token = {"header": HEADER, "payload": PAYLOAD, "signature": SIGNATURE, "expires": PAYLOAD['exp']}
        self.pas_token = r.content.decode()

        return self.parsed_pas_token
