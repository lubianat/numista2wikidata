"""
Helper functions to parse the numista API and connect to Wikidata.
"""
from asyncore import write
import json
import traceback

import requests
from wdcuration import add_key, render_qs_url
from wikidata2df import wikidata2df

from dictionaries.all import DICTS
import click
from pathlib import Path

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()
DICTS_FOLDER = HERE.parent.joinpath("dictionaries").resolve()


def get_coin_statements(coin_type_id, details=False):
    """
    Retrieves formatted Quickstatements V2 commands given a Numista coin type ID.
    Args:
      coin_type_id (str): The numeric ID for the coin type on Numista.
      details (bool)
    """
    global DICTS

    coin_details = get_details(coin_type_id)
    click.echo(coin_details if details else None)

    # Extract fields of interest
    ref = f'|S854|"https://en.numista.com/catalogue/type{str(coin_type_id)}.html"|S248|Q84602292'

    currency_name = coin_details["value"]["currency"]["full_name"]

    currency = get_currency_id(currency_name)

    value = coin_details["value"]["numeric_value"]
    min_year = coin_details["min_year"]
    max_year = coin_details["max_year"]

    if min_year == max_year:
        date_range = min_year
    else:
        date_range = f"{min_year} - {max_year}"

    coin_title = coin_details["title"].replace("&quot;", '"')
    title_en = f"{coin_title} coin ({date_range})"
    title_pt = f"moeda de {coin_title} ({date_range})"

    metal_name = coin_details["composition"]["text"]

    material = get_material_id(ref, metal_name)

    country_name = coin_details["issuer"]["name"]

    if country_name not in DICTS["issuer"]:
        DICTS["issuer"] = add_key(DICTS["issuer"], country_name)
        write_dict("issuer")

    country = DICTS["issuer"][coin_details["issuer"]["name"]]
    diameter = coin_details["size"]
    weight = coin_details["weight"]

    if coin_details["shape"] not in DICTS["shapes"]:
        DICTS["shapes"] = add_key(DICTS["shapes"], coin_details["shape"])
        write_dict("shapes")
    shape = DICTS["shapes"][coin_details["shape"]]

    try:
        mints = []
        for mint in coin_details["mints"]:

            try:
                mints.append(DICTS["mint"][mint["name"]])
            except Exception:
                traceback.print_exc()
                DICTS["mint"] = add_key(DICTS["mint"], mint["name"])
                write_dict("mint")
                break
    except Exception:
        traceback.print_exc()

    # Generate quickstatements
    to_print = f"""
    CREATE
    LAST|Len|"{title_en}"
    LAST|Den|"coin from {country_name}"
    LAST|P31|Q113813711
    LAST|P279|Q41207
    LAST|P17|{country}{ref}
    LAST|P580|+{min_year}-00-00T00:00:00Z/9{ref}
    LAST|P582|+{max_year}-00-00T00:00:00Z/9{ref}
    LAST|P186|{material}{ref}
    LAST|P2386|{diameter}U174789{ref}
    LAST|P2067|{weight}U41803{ref}
    LAST|P1419|{shape}{ref}
    LAST|P10205|"{str(coin_type_id)}"{ref}
    LAST|P3934|{value}{currency}{ref}
    """
    for mint in mints:
        to_print = to_print + f"""LAST|P176|{mint}{ref}\n"""

    if "series" in coin_details:
        if coin_details["series"] in DICTS["series"]:
            series = DICTS["series"][coin_details["series"]]
            to_print = to_print + f"""LAST|P179|{series}{ref}\n"""
        else:
            DICTS["series"] = add_key(DICTS["series"], coin_details["series"])

            write_dict("series")
    try:
        thickness = coin_details["thickness"]
        to_print = to_print + f"""LAST|P2610|{thickness}U174789{ref}\n"""
    except:
        pass

    if "engravers" in coin_details["obverse"]:
        for engraver in coin_details["obverse"]["engravers"]:
            to_print = update_engraver(to_print, ref, engraver, side="obverse")

    if "engravers" in coin_details["reverse"]:
        for engraver in coin_details["reverse"]["engravers"]:
            to_print = update_engraver(to_print, ref, engraver, side="reverse")

    if "lettering_scripts" in coin_details["obverse"]:
        for script in coin_details["obverse"]["lettering_scripts"]:
            to_print = update_scripts(to_print, ref, script["name"], side="obverse")

    if "lettering_scripts" in coin_details["reverse"]:
        for script in coin_details["reverse"]["lettering_scripts"]:
            to_print = update_scripts(to_print, ref, script["name"], side="reverse")

    print(f"Issuer:{country_name} ")
    if country_name in DICTS["depict"]:
        DICTS["depict"]["global"].update(DICTS["depict"][country_name])

    for key, value in DICTS["depict"]["global"].items():

        if key.lower() in coin_details["obverse"]["description"].lower():
            to_print = to_print + (f"""LAST|P180|{value}|P518|Q257418{ref}\n""")
        if key.lower() in coin_details["reverse"]["description"].lower():
            to_print = to_print + f"""LAST|P180|{value}|P518|Q1542661{ref}\n"""

    # Parse possible languages

    for key, value in DICTS["language"].items():

        if key.lower() in coin_details["obverse"]["description"].lower():
            to_print = to_print + (f"""LAST|P407|{value}|P518|Q257418{ref}\n""")

        if key.lower() in coin_details["reverse"]["description"].lower():
            to_print = to_print + f"""LAST|P407|{value}|P518|Q1542661{ref}\n"""

    if coin_details["type"] == "Standard circulation coin":
        to_print = to_print + f"""LAST|P279|Q110944598{ref}\n"""
    elif coin_details["type"] == "Circulating commemorative coin":
        to_print = to_print + f"""LAST|P279|Q110997090{ref}\n"""

    return to_print


def get_currency_id(currency_name):
    if currency_name in DICTS["currency"]:
        currency = DICTS["currency"][currency_name].replace("Q", "U")
    else:
        DICTS["currency"] = add_key(DICTS["currency"], currency_name)

        write_dict("currency")
        currency = get_currency_id(currency_name)

    return currency


def get_material_id(ref, metal_name):
    if metal_name in DICTS["composition"]:
        material_id = DICTS["composition"][metal_name]
        return material_id

    else:
        metal_qs = f"""
            CREATE
            LAST|Len|"{metal_name}"
            LAST|Den|"metallic material used for coins"  """
        for key, value in DICTS["composition"].items():
            if key.lower() in metal_name.lower():
                metal_qs = (
                    metal_qs
                    + f"""
            LAST|P527|{value}{ref}"""
                )
        if "Bimetallic" in metal_name:
            metal_qs = (
                metal_qs
                + f"""
            LAST|P279|Q110983998{ref}"""
            )
        else:
            metal_qs = (
                metal_qs
                + f"""
            LAST|P279|Q214609{ref}"""
            )
        print(render_qs_url(metal_qs))
        DICTS["composition"] = add_key(DICTS["composition"], metal_name)

        write_dict("composition")
        material_id = get_material_id(ref, metal_name)
        return material_id


def update_scripts(to_print, ref, script, side):
    if side == "obverse":
        side_id = "Q257418"
    elif side == "reverse":
        side_id = "Q1542661"
    if script in DICTS["scripts"]:
        script_qid = DICTS["scripts"][script]
        side_id = "Q257418"
        to_print = to_print + f"""LAST|P9302|{script_qid}|P518|{side_id}{ref}\n"""
    else:
        DICTS["scripts"] = add_key(DICTS["scripts"], script)

        write_dict("scripts")
        to_print = update_scripts(to_print, ref, script, side=side)

    return to_print


def update_engraver(to_print, ref, engraver, side="obverse"):

    if side == "obverse":
        side_id = "Q257418"
    elif side == "reverse":
        side_id = "Q1542661"
    if engraver in DICTS["engraver"]:
        engraver_qid = DICTS["engraver"][engraver]
        to_print = to_print + f"""LAST|P287|{engraver_qid}|P518|{side_id}{ref}\n"""
    else:
        qs = f"""
                CREATE
                LAST|Len|"{engraver}"
                LAST|Den|"engraver"
                LAST|P31|Q5
                LAST|P106|Q329439{ref}  """
        print(render_qs_url(qs))
        DICTS["engraver"] = add_key(DICTS["engraver"], engraver)

        write_dict("engraver")
        to_print = update_engraver(to_print, ref, engraver, side="obverse")

    return to_print


def get_details(coin_type_id):
    """
    Gets details from the Numista API.
    Args:
      coin_type_id (str): The numeric ID for the coin type on Numista.
    """
    api_key = "2GtYY2INUIgmEYynq7xAHTqRY01Us4dOXIf30mlA"
    endpoint = "https://api.numista.com/api/v2"

    response = requests.get(
        endpoint + "/coins/" + coin_type_id,
        params={"lang": "en"},
        headers={"Numista-API-Key": api_key},
    )
    response.encoding = "UTF-8"
    coin_details = response.json()
    return coin_details


def add_depict(country_name):
    """
    Adds depicts statements to the Quickstatements.
    """
    global DICTS
    add_depict_bool = input("Add depicts? 1 = global, 2 = national, other = no :")

    if add_depict_bool == "1":
        string_to_add = input("String to add:")
        DICTS["depict"]["global"] = add_key(DICTS["depict"]["global"], string_to_add)
        add_depict(country_name)
    elif add_depict_bool == "2":
        string_to_add = input("String to add:")

        if country_name not in DICTS["depict"]:
            DICTS["depict"][country_name] = {}
        DICTS["depict"][country_name] = add_key(DICTS["depict"][country_name], string_to_add)
        add_depict(country_name)

    else:
        write_dict("depict")

        return 0


def check_depicts(country_name, coin_details):
    if country_name in DICTS["depict"]:
        DICTS["depict"]["global"].update(DICTS["depict"][country_name])

    # Parse possible depicts
    print("=== Obverse ===")
    print(coin_details["obverse"]["description"])
    print("=== Reverse ===")
    print(coin_details["reverse"]["description"])

    depicted_qids = []
    for key, value in DICTS["depict"]["global"].items():

        if key.lower() in coin_details["obverse"]["description"].lower():
            depicted_qids.append(value)
        if key.lower() in coin_details["reverse"]["description"].lower():
            depicted_qids.append(value)

    depicted_qids_with_prefix = [f"wd:{a}" for a in depicted_qids]
    query = (
        "    SELECT ?x ?x_label WHERE {"
        "VALUES ?x {"
        f'{" ".join(depicted_qids_with_prefix)}'
        "} . "
        "?x rdfs:label ?x_label . "
        'FILTER (LANG (?x_label) = "en")'
        "}"
    )
    df = wikidata2df(query)
    print(df.drop_duplicates())


def write_dict(name):
    dict_as_string = json.dumps(DICTS[name], indent=4, ensure_ascii=False, sort_keys=True)
    DICTS_FOLDER.joinpath(f"{name}.json").write_text(dict_as_string, encoding="UTF-8")
