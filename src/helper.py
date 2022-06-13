from textwrap import indent
import requests
import sys
import requests
from dictionaries.all import *
import traceback
import json
import clipboard
from wdcuration import add_key, render_qs_url


def get_coin_statements(coin_type_id):
    """
    Retrieves formatted Quickstatements V2 commands given a Numista coin type ID.
    Args:
      coin_type_id (str): The numeric ID for the coin type on Numista.
    """
    global dicts

    coin_details = get_details(coin_type_id)

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

    if country_name not in dicts["issuer"]:
        dicts["issuer"] = add_key(dicts["issuer"], country_name)
        with open("src/dictionaries/issuer.json", "w+") as f:
                    f.write(
                        json.dumps(
                            dicts["issuer"], indent=4, ensure_ascii=False, sort_keys=True
                        )
                    )


    country = dicts["issuer"][coin_details["issuer"]["name"]]
    diameter = coin_details["size"]
    weight = coin_details["weight"]

    if coin_details["shape"] not in dicts["shapes"]:
        dicts["shapes"] = add_key(dicts["shapes"], coin_details["shape"] )
        with open("src/dictionaries/shapes.json", "w+") as f:
                    f.write(
                        json.dumps(
                            dicts["shapes"], indent=4, ensure_ascii=False, sort_keys=True
                        )
                    )
    shape = dicts["shapes"][coin_details["shape"]]

    try:
        mints = []
        for mint in coin_details["mints"]:

            try:
                mints.append(dicts["mint"][mint["name"]])
            except Exception:
                traceback.print_exc()
                dicts["mint"] = add_key(dicts["mint"], mint["name"])
                with open("src/dictionaries/mint.json", "w+") as f:
                    f.write(
                        json.dumps(
                            dicts["mint"], indent=4, ensure_ascii=False, sort_keys=True
                        )
                    )
                break
    except Exception:
        traceback.print_exc()

    # Generate quickstatements
    to_print = f"""
    CREATE
    LAST|Len|"{title_en}"
    LAST|Den|"coin from {country_name}"
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
        if coin_details["series"] in dicts["series"]:
            series = dicts["series"][coin_details["series"]]
            to_print = to_print + f"""LAST|P179|{series}{ref}\n"""
        else:
            dicts["series"] = add_key(dicts["series"], coin_details["series"])

            with open("src/dictionaries/series.json", "w+") as f:
                f.write(
                    json.dumps(
                        dicts["series"], indent=4, ensure_ascii=False, sort_keys=True
                    )
                )

    try:
        thickness = coin_details["thickness"]
        to_print = to_print + f"""LAST|P2610|{thickness}U174789{ref}\n"""
    except:
        pass

    if "engravers" in coin_details["obverse"]:
        for engraver in coin_details["obverse"]["engravers"]:
            to_print = update_engraver(to_print, ref, engraver, side="obverse")

    if "engravers" in coin_details["reverse"]:
        for engraver in coin_details["obverse"]["engravers"]:
            to_print = update_engraver(to_print, ref, engraver, side="reverse")

    # Parse possible depicts
    print("=== Obverse ===")
    print(coin_details["obverse"]["description"])
    print("=== Reverse ===")
    print(coin_details["reverse"]["description"])

    country_dict_name = f"depict_{country_name.lower()}"

    print(f"Issuer:{country_name} ")
    if country_name in dicts["depict"]:
        dicts["depict"]["global"].update(dicts["depict"][country_name])

    for key, value in dicts["depict"]["global"].items():

        if key.lower() in coin_details["obverse"]["description"].lower():
            to_print = to_print + (f"""LAST|P180|{value}|P518|Q257418{ref}\n""")

        if key.lower() in coin_details["reverse"]["description"].lower():
            to_print = to_print + f"""LAST|P180|{value}|P518|Q1542661{ref}\n"""

    # Parse possible languages

    for key, value in dicts["language"].items():

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
    if currency_name in dicts["currency"]:
        currency = dicts["currency"][currency_name].replace("Q", "U")
    else:
        dicts["currency"] = add_key(dicts["currency"], currency_name)

        with open("src/dictionaries/currency.json", "w+") as f:
            f.write(
                json.dumps(
                    dicts["currency"], indent=4, ensure_ascii=False, sort_keys=True
                )
            )

        currency = get_currency_id(currency_name)

    return currency


def get_material_id(ref, metal_name):
    if metal_name in dicts["composition"]:
        material_id = dicts["composition"][metal_name]
        return material_id

    else:
        metal_qs = f"""
            CREATE
            LAST|Len|"{metal_name}"
            LAST|Den|"metallic material used for coins"  """
        for key, value in dicts["composition"].items():
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
        dicts["composition"] = add_key(dicts["composition"], metal_name)

        with open("src/dictionaries/composition.json", "w+") as f:
            f.write(
                json.dumps(
                    dicts["composition"], indent=4, ensure_ascii=False, sort_keys=True
                )
            )
        material_id = get_material_id(ref, metal_name)
        return material_id


def update_engraver(to_print, ref, engraver, side="obverse"):

    if side == "obverse":
        side_id = "Q257418"
    elif side == "reverse":
        side_id = "Q1542661"
    if engraver in dicts["engraver"]:
        engraver_qid = dicts["engraver"][engraver]
        side_id = "Q257418"
        to_print = to_print + f"""LAST|P287|{engraver_qid}|P518|{side_id}{ref}\n"""
    else:
        qs = f"""
                CREATE
                LAST|Len|"{engraver}"
                LAST|Den|"engraver"
                LAST|P31|Q5
                LAST|P106|Q329439{ref}  """
        print(render_qs_url(qs))
        dicts["engraver"] = add_key(dicts["engraver"], engraver)

        with open("src/dictionaries/engraver.json", "w+") as f:
            f.write(
                json.dumps(
                    dicts["engraver"], indent=4, ensure_ascii=False, sort_keys=True
                )
            )
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
