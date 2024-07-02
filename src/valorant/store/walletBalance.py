class WalletBalance:
    def __init__(self, valorant_points: int, kingdom_credits: int, radianite_points: int, free_agents: int):
        self.valorant_points = valorant_points
        self.kingdom_credits = kingdom_credits
        self.radianite_points = radianite_points
        self.free_agents = free_agents

    @staticmethod
    def from_json(data: dict):
        return WalletBalance(
            data["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"],
            data["Balances"]["85ca954a-41f2-ce94-9b45-8ca3dd39a00d"],
            data["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"],
            data["Balances"]["f08d4ae3-939c-4576-ab26-09ce1f23bb37"]
        )
