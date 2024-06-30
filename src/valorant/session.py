from typing import Optional
import requests
import os
import re

from authorization import AuthorizationHandler
from cacheManager import CacheManager
from user.localAccount import LocalAccount
from chat.conversationsManager import ConversationsManager
from store.storeManager import StoreManager
from social.socialManager import SocialManager

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Session:
    def __init__(self):
        self.auth = AuthorizationHandler(self)
        self.store = StoreManager(self)
        self.conversations = ConversationsManager(self)
        self.social = SocialManager(self)
        self.cache = CacheManager(self)

        self.shard = None
        self.region = None
        self.local_account = None

        self.valorant_logging_file = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')

        self.auth.get_auth_headers()

    def fetch_local(self, path: str, method: str = "GET", use_cache: bool = True, set_cache_time_seconds: Optional[int] = None, *args, **kwargs) -> dict:
        if self.auth.lockfile_contents is None:
            self.auth.get_lockfile_contents()

        if use_cache:
            response = self.cache.get_from_cache(f"{method}_local/{path}")

            if response is not None:
                return response

        r = requests.request(method, f"{self.auth.lockfile_contents['protocol']}://127.0.0.1:{self.auth.lockfile_contents['port']}/{path}", headers=self.auth.local_auth_headers, verify=False, *args, **kwargs)

        self.cache.add_to_cache(f"{method}_local/{path}", r.json(), set_cache_time_seconds)

        return r.json()

    def fetch(self, url: str, method: str = "GET", use_cache: bool = True, set_cache_time_seconds: Optional[int] = None, *args, **kwargs) -> dict:
        if self.auth.auth_headers is None:
            self.auth.get_auth_headers()

        if use_cache:
            response = self.cache.get_from_cache(f"{method}_{url}")

            if response is not None:
                return response

        r = requests.request(method, url, headers=self.auth.auth_headers, *args, **kwargs)

        self.cache.add_to_cache(f"{method}_{url}", r.json(), set_cache_time_seconds)

        return r.json()

    def get_game_version(self) -> str:
        f = open(self.valorant_logging_file, "r", encoding="utf-8")

        # following code is a modified form of code in the
        # https://github.com/molenzwiebel/Deceive repo
        while True:
            line = f.readline()
            if 'CI server version:' in line:
                version_without_shipping = line.split('CI server version: ')[1].strip()
                version = version_without_shipping.split("-")
                version.insert(2, "shipping")
                version = "-".join(version)

                f.close()

                return version

    def get_current_season(self, include_acts=True, include_episodes=True):
        if not (include_acts or include_episodes):
            raise RuntimeError("Both include_acts and include_episodes are false. One must be true.")

        data = self.get_seasons_acts_events_raw()

        season_data = data["Seasons"]

        for season in season_data:
            if not season["IsActive"]:
                continue

            if season["Type"] == "act" and include_acts is False:
                continue

            if season["Type"] == "episode" and include_episodes is False:
                continue

            # potentially turn into another class in the future
            return season["ID"]

    def get_region(self):
        if not (self.shard is None or self.region is None):
            return (self.shard, self.region)

        f = open(self.valorant_logging_file, "r")
        content = f.read()
        output = re.search("https://glz-(.+?)-1.(.+?).a.pvp.net", content)

        if output is None:
            raise RuntimeError("Unable to find region data in Valorant's log file. This can be solved by running Valorant and allowing for the client to log the region data.")

        output = output.groups()

        self.shard = output[0]
        self.region = output[1]

        return output

    def get_local_account(self) -> LocalAccount:
        if self.auth.auth_headers is None:
            self.auth.get_auth_headers()

        if self.local_account is not None:
            return self.local_account

        self.local_account = LocalAccount(self)
        return self.local_account

    def get_seasons_acts_events_raw(self):
        if self.shard is None:
            self.get_region()

        return self.fetch(f"https://shared.{self.shard}.a.pvp.net/content-service/v3/content")

    def get_help(self):
        return self.fetch_local("help")
