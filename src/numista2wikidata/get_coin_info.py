#!/usr/bin/env python3
"""
Generates a Quickstaments command to create a particular coin type on Wikidata.
"""
import json
import webbrowser

import click
from wdcuration.wdcuration import render_qs_url

from dictionaries.all import DICTS
from numista2wikidata.helper import get_coin_statements, get_details, add_depict


@click.command(name="get")
@click.argument("coin_type_id")
def main(coin_type_id: str):
    """
    Generates a Quickstaments command to create a particular coin type on Wikidata.
    """
    get_coin_info(coin_type_id)


def get_coin_info(coin_type_id):
    string = get_coin_statements(coin_type_id)
    webbrowser.open_new_tab(render_qs_url(string))
    coin_details = get_details(coin_type_id)
    country_name = coin_details["issuer"]["name"]

    add_depict(country_name)

    with open("src/dictionaries/depict.json", "w+") as f:
        f.write(json.dumps(DICTS["depict"], indent=4, sort_keys=True))

    repeat = input("Rerun command? (y/n) ")
    if repeat == "y":
        get_coin_info(coin_type_id)
