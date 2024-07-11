from typing import Optional
import requests
import os
import re

from .authorization import AuthorizationManager
from .cacheManager import CacheManager
from .user.localAccount import LocalAccount
from .chat.conversationsManager import ConversationsManager
from .store.storeManager import StoreManager
from .social.socialManager import SocialManager

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Session:
    def __init__(self):
        """
        Session Manager for Valorant
        """

        self.auth = AuthorizationManager(self)
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
        """
        Fetches the given path at the local url using the given method

        Parameters:
        path (str): The path to the data that will be requested
        method (str, defaults to "GET"): The method the request will be sent with
        use_cache (bool, defaults to True): Determines if this request will use the CacheManager
        set_cache_time_seconds (int, optional, defaults to None): The amount of time a request's response will be stored in the cache for

        Returns:
        dict: The JSON response from the given path
        """

        # get the lockfile contents if they do not exist
        if self.auth.lockfile_contents is None:
            self.auth.get_lockfile_contents()

        # grab the item from the cache if it exists
        if use_cache:
            response = self.cache.get_from_cache(f"{method}_local/{path}-{args}-{kwargs}")

            if response is not None:
                return response

        # get the actual data
        r = requests.request(method, f"{self.auth.lockfile_contents['protocol']}://127.0.0.1:{self.auth.lockfile_contents['port']}/{path}", headers=self.auth.local_auth_headers, verify=False, *args, **kwargs)
        data = r.json()

        if "errorCode" in data and data["errorCode"] == "BAD_CLAIMS":
            self.auth.lockfile_contents = None
            self.auth.get_auth_headers(force_renew=True)
            return self.fetch_local(path, method, use_cache, set_cache_time_seconds, *args, **kwargs)

        # add the data to the cache
        self.cache.add_to_cache(f"{method}_local/{path}-{args}-{kwargs}", data, set_cache_time_seconds)

        # return the JSON data
        return data

    def fetch(self, url: str, method: str = "GET", use_cache: bool = True, set_cache_time_seconds: Optional[int] = None, *args, **kwargs) -> Optional[dict]:
        """
        Fetches the given url using the given method

        Parameters:
        url (str): The url to the data that will be requested
        method (str, defaults to "GET"): The method the request will be sent with
        use_cache (bool, defaults to True): Determines if this request will use the CacheManager
        set_cache_time_seconds (int, optional, defaults to None): The amount of time a request's response will be stored in the cache for

        Returns:
        dict: The JSON response from the url
        """

        # grab the item from the cache if it exists
        if use_cache:
            response = self.cache.get_from_cache(f"{method}_{url}-{args}-{kwargs}")

            if response is not None:
                return response

        # send the request
        r = requests.request(method, url, headers=self.auth.get_auth_headers(), *args, **kwargs)
        data = r.json()

        if method.upper() == "POST":
            return

        if "errorCode" in data and data["errorCode"] == "BAD_CLAIMS":
            self.auth.lockfile_contents = None
            self.auth.get_auth_headers(force_renew=True)
            return self.fetch(url, method, use_cache, set_cache_time_seconds, *args, **kwargs)

        # add the request's response to the cache
        self.cache.add_to_cache(f"{method}_{url}-{args}-{kwargs}", data, set_cache_time_seconds)

        # return the request's JSON data
        return data

    def get_game_version(self) -> str:
        """
        Fetches the game version from the valorant logging file

        Returns:
        str: The current game version
        """

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

    def get_current_season(self, include_acts: bool = True, include_episodes: bool = True):
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

    def get_region(self) -> tuple:
        """
        Fetches the current region using the Valorant logging file. Sets the self.shard and self.region variables.

        Returns:
        tuple: Returns the shard and region in a tuple
        """

        # return the current region if we already have it
        if not (self.shard is None or self.region is None):
            return (self.shard, self.region)

        # opens the Valorant logging file and gets the contents
        f = open(self.valorant_logging_file, "r")
        content = f.read()
        f.close()

        # gets the region using regex
        output = re.search("https://glz-(.+?)-1.(.+?).a.pvp.net", content)

        # Raise an error if we are unable to find the region in the logging file
        if output is None:
            raise RuntimeError("Unable to find region data in Valorant's log file. This can be solved by running Valorant and allowing for the client to log the region data.")

        output = output.groups()

        # get the shard and region
        self.shard = output[0]
        self.region = output[1]

        # return the shard and region
        return output

    def get_local_account(self) -> LocalAccount:
        """
        Gets the local account

        Returns:
        LocalAccount: The LocalAccount object
        """

        # return the self.local_account variable if it is already defined
        if self.local_account is not None:
            return self.local_account

        # make the local account variable from the class and return it
        self.local_account = LocalAccount(self)
        return self.local_account

    def get_seasons_acts_events_raw(self) -> dict:
        """
        Fetches all the seasons, acts, and events and returns it as JSON data

        Returns:
        dict: The JSON output
        """

        # get the current region if we do not have the shard
        if self.shard is None:
            self.get_region()

        # get all seasons, acts, and events and return them as JSON
        return self.fetch(f"https://shared.{self.shard}.a.pvp.net/content-service/v3/content")

    def get_help_raw(self) -> dict:
        """
        Gets help which shows a lot of data relating to events, functions and types

        Returns:
        dict: The JSON output from the request
        """

        return self.fetch_local("help")
