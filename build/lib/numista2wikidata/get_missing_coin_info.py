#!/usr/bin/env python3
import click
from SPARQLWrapper import JSON, SPARQLWrapper

from dictionaries.all import *
from numista2wikidata.get_coin_info import get_coin_info
from numista2wikidata.helper import *
from numista2wikidata.login_info import *


@click.command(name="random")
def main():
    sparqlwd = SPARQLWrapper(
        "https://query.wikidata.org/sparql",
        agent="numista2wikidata (https://github.com/lubianat/numista2wikidata)",
    )

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
        try:
            if coin["coin"]["category"] == "exonumia":
                continue
            coin_ids.append(str(coin["coin"]["id"]))

        except:
            print(coin)
            break

    coin_ids = list(set(coin_ids))

    coin_statements = []
    for coin_id in coin_ids:
        if coin_id not in current_ids:
            print("==================")
            print(f"numis get {str(coin_id)}")
            print("==================")

            get_coin_info(coin_id)
            break
    with open("new_coins.qs", "w") as f:
        f.write("\n".join(coin_statements))


if __name__ == "__main__":
    main()
