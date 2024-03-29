#!/usr/bin/env python3
"""
Generates a Quickstaments command to create a particular coin type on Wikidata.
"""
import json
import webbrowser
from tabnanny import verbose

import click
from wdcuration.wdcuration import render_qs_url

from dictionaries.all import DICTS
from numista2wikidata.helper import add_depict, check_depicts, get_coin_statements, get_details


@click.command(name="get")
@click.argument("coin_type_id")
@click.option("--details", "-d", is_flag=True, help="Print more output.")
def main(coin_type_id: str, details: bool):
    """
    Generates a Quickstaments command to create a particular coin type on Wikidata.
    """
    get_coin_info(coin_type_id, details)


def get_coin_info(coin_type_id, details=False):
    print(f"https://en.numista.com/catalogue/pieces{coin_type_id}.html")

    coin_details = get_details(coin_type_id)
    if coin_details["category"] == "exonumia":
        print("Exonumia, quitting")
        quit()
    country_name = coin_details["issuer"]["name"]
    print(country_name)
    print("===== Depicts =====")
    check_depicts(country_name, coin_details)
    add_depict(country_name)

    string = get_coin_statements(coin_type_id, details)

    webbrowser.open_new_tab(render_qs_url(string))
