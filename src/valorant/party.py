from typing import TYPE_CHECKING, Optional

from .user.users import Users

if TYPE_CHECKING:
    from .session import Session


class Party:
    def __init__(self, session: "Session", party_ID: str, users: Optional[Users] = None):
        self.session = session

        self.party_ID = party_ID

        self.users = users
        if self.users is None:
            self.users = Users(session)

    def get_information_raw(self) -> dict:
        return self.session.fetch(f"{self.session.glz_url}/parties/v1/parties/{self.party_ID}")

    def get_information(self):
        return self.get_information_raw()

    def generate_party_code(self):
        return self.session.fetch(f"{self.session.glz_url}/parties/v1/parties/{self.party_ID}/invitecode", method="POST", use_cache=False)["InviteCode"]

    def disable_party_code(self):
        return self.session.fetch(f"{self.session.glz_url}/parties/v1/parties/{self.party_ID}/invitecode", method="DELETE")

    def get_custom_game_settings_raw(self):
        return self.session.fetch(f"{self.session.glz_url}/parties/v1/parties/customgameconfigs", use_cache=False)
