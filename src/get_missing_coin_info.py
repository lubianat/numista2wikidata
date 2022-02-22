from helper import *
from SPARQLWrapper import SPARQLWrapper, JSON
from login_info import *
import time
from helper import *

sparqlwd = SPARQLWrapper("https://query.wikidata.org/sparql")

query = """
SELECT DISTINCT
  ?item ?numista_id
WHERE 
{
  ?item wdt:P10205 ?numista_id . 
} 
"""

sparqlwd.setQuery(query)
sparqlwd.setReturnFormat(JSON)
data = sparqlwd.query().convert()

current_ids = []
for result in data["results"]["bindings"]:
    current_ids.append(result["numista_id"]["value"])

endpoint = "https://api.numista.com/api/v2"
user_id = "231967"
response = requests.get(
    endpoint + "/users/" + user_id + "/collected_coins",
    params={"lang": "en"},
    headers={"Numista-API-Key": api_key},
)
user_details = response.json()

collected_coins = user_details["collected_coins"]

coin_ids = []
for coin in collected_coins:
    coin_ids.append(str(coin["coin"]["id"]))

coin_ids = list(set(coin_ids))

coin_statements = []
for coin_id in coin_ids:
    if coin_id not in current_ids:
        print(f"https://en.numista.com/catalogue/pieces{coin_id}.html")
        coin_statements.append(get_coin_statements(coin_id))
        time.sleep(0.3)
with open("new_coins.qs", "w") as f:
    f.write("\n".join(coin_statements))
