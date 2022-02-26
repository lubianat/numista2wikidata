#!/usr/bin/env python3
from helper import *
from login_info import *


# Send API request to Numista


with open("coin_info.qs", "w+") as f:
    f.write("")


endpoint = "https://api.numista.com/api/v2"
user_id = "231967"
response = requests.get(
    endpoint + "/coins",
    params={"q": "2021", "issuer": "ukraine", "ct": "coin"},
    headers={"Numista-API-Key": api_key},
)

print(response.json())

id_list = []
for coin in response.json()["coins"]:
    id_list.append(coin["id"])

with open("coin_info.qs", "a") as f:

    for coin_id in id_list:
        f.write(get_coin_statements(str(coin_id)))
