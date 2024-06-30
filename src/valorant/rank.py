from typing import List


class Rank:
    ranks_list: List[str] = []

    def __init__(self, rank_index: int, rank_rating: int):
        self.rank_index = rank_index
        self.rank_rating = rank_rating

    def to_string(self) -> str:
        """
        Converts the Rank object into a string

        Returns:
        str: The string representation of the Rank class
        """

        return f"{self.ranks_list[self.rank_index]} {self.rank_rating} RR"

    def __str__(self):
        return self.to_string()


rank_names = [
    {"name": "Unranked", "displayNumbers": False, "count": 3},
    {"name": "Iron", "displayNumbers": True, "count": 3},
    {"name": "Bronze", "displayNumbers": True, "count": 3},
    {"name": "Silver", "displayNumbers": True, "count": 3},
    {"name": "Gold", "displayNumbers": True, "count": 3},
    {"name": "Platinum", "displayNumbers": True, "count": 3},
    {"name": "Diamond", "displayNumbers": True, "count": 3},
    {"name": "Ascendant", "displayNumbers": True, "count": 3},
    {"name": "Immortal", "displayNumbers": True, "count": 3},
    {"name": "Radiant", "displayNumbers": False, "count": 1}
]

for r in rank_names:
    for i in range(r["count"]):
        Rank.ranks_list.append(r['name'] + (f" {i+1}" if r["displayNumbers"] else ""))


if __name__ == "__main__":
    print(Rank.ranks_list)
