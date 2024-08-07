# Python Valorant Wrapper
A Valorant wrapper written in Python, built to be used on a local machine

<a href="https://pypi.org/project/valorant-wrapper/"><img src="https://img.shields.io/pypi/v/valorant-wrapper?color=4c1"></a>
<a href="https://pypi.org/project/valorant-wrapper/"><img title="Weekly download count" alt="Weekly download count" src="https://img.shields.io/pypi/dw/valorant-wrapper?color=4c1"></a>
<a href="https://pypi.org/project/valorant-wrapper/"><img title="Total download count" alt="Total download count" src="https://static.pepy.tech/badge/valorant-wrapper"></a>
<a href="https://trello.com/b/kEz9g2VK/valorant-wrapper"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ftrello.com%2Fb%2FkEz9g2VK%2Fvalorant-wrapper.json&query=%24.cards.length&suffix=%20cards&logo=Trello&logoColor=white&label=Trello"></a>
<a href="https://playvalorant.com/en-us/news/game-updates/"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fvalorant-api.com%2Fv1%2Fversion&query=%24.data.riotClientVersion&logo=Valorant&logoColor=white&label=Valorant%20Version"></a>
<a href="https://github.com/Whitelisted1/Valorant-Python-Wrapper/stargazers"><img src="https://img.shields.io/github/stars/whitelisted1/Valorant-Python-Wrapper"></a>

## Installation
```bash
pip install valorant-wrapper
```

## Usage
Documentation is coming soon, but here is a quickstart guide for those getting started:
```python
from valorant import Session

# Before beginning, make sure that the Riot Client is open
# This will not work otherwise

session = Session() # get session
local_account = session.get_local_account() # get the local account
rank = local_account.get_rank() # get our local account's rank

# print the name of the local account and its rank
print("[Rank]", local_account.get_name(), rank.to_string())

# get the local account's friends, then print all their names
friends = local_account.get_friends()
print("[Friends]", friends.get_names())

# get the active match (does not include pregame), and print all player names
current_game = local_account.get_current_game()

# check to see if the player is in a game
if current_game is None: print("[Game] Not in a game")
else: print("[Game]", current_game.players.get_names())

# get the current party and print the raw information (not yet complete)
party = local_account.get_party()

# check to see if the player is in a party
if party is None: print("[Party] Not in a party")
else: print("[Party]", party.get_information_raw())

# get the storefront and print the first item's cost
storefront = session.store.get_storefront()
print("[Store]", storefront.daily_shop[0].cost)
```

## Resources used
* https://github.com/techchrism/valorant-api-docs
* https://github.com/zayKenyon/VALORANT-rank-yoinker as a reference

## Legal
This project is not affiliated with Riot Games or any of its employees and therefore does not reflect the views of said parties.

Riot Games does not endorse or sponsor this project. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.