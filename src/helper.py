import requests
import sys
import requests
from dictionaries import *
import traceback


def get_coin_statements(coin_type_id):
    api_key = "2GtYY2INUIgmEYynq7xAHTqRY01Us4dOXIf30mlA"
    client_id = "231967"
    endpoint = "https://api.numista.com/api/v2"
    ref = f'|S854|"https://en.numista.com/catalogue/type{str(coin_type_id)}.html"|S248|Q84602292'

    response = requests.get(
        endpoint + "/coins/" + coin_type_id,
        params={"lang": "en"},
        headers={"Numista-API-Key": api_key},
    )
    coin_details = response.json()

    # Extract fields of interest
    currency = currency_dict[coin_details["value"]["currency"]["full_name"]].replace(
        "Q", "U"
    )
    value = coin_details["value"]["numeric_value"]
    min_year = coin_details["min_year"]
    max_year = coin_details["max_year"]
    title_en = f"{coin_details['title']} coin ({min_year} - {max_year})"
    title_pt = f"moeda de {coin_details['title']} ({min_year} - {max_year})"

    try:
        material = composition_dict[coin_details["composition"]["text"]]
    except Exception:
        traceback.print_exc()
        text = coin_details["composition"]["text"]
        if "Bimetallic" in text:

            print(
                f"""
            CREATE
            LAST|Len|"{text}"
            LAST|Den|"Bimetallic material used for coins"
            LAST|P279|Q110983998{ref}"""
            )

            for key, value in composition_dict.items():
                if key.lower() in text.lower():
                    print(
                        f"""
            LAST|P527|{value}{ref}
            """
                    )

    country = issuer_dict[coin_details["issuer"]["name"]]
    country_name = coin_details["issuer"]["name"]
    diameter = coin_details["size"]
    weight = coin_details["weight"]

    # Generate quickstatements
    to_print = f"""
    CREATE
    LAST|Len|"{title_en}"
    LAST|Lpt|"{title_pt}"
    LAST|Den|"coin from {country_name}"
    LAST|Dpt|"tipo de moeda"
    LAST|P279|Q41207
    LAST|P17|{country}{ref}
    LAST|P580|+{min_year}-00-00T00:00:00Z/9{ref}
    LAST|P582|+{max_year}-00-00T00:00:00Z/9{ref}
    LAST|P186|{material}{ref}
    LAST|P2386|{diameter}U174789{ref}
    LAST|P2067|{weight}U41803{ref}
    LAST|P10205|"{str(coin_type_id)}"{ref}
    LAST|P3934|{value}{currency}{ref}
    """
    try:
        series = series_dict[coin_details["series"]]
        to_print = to_print + f"""LAST|P279|{series}{ref}\n"""
    except:
        pass

    try:
        thickness = coin_details["thickness"]
        to_print = to_print + f"""LAST|P2610|{thickness}U174789{ref}\n"""
    except:
        pass

    try:
        for engraver in coin_details["obverse"]["engravers"]:
            engraver_qid = engravers_dict[engraver]
            to_print = to_print + f"""LAST|P287|{engraver_qid}|P518|Q257418{ref}\n"""
    except KeyError as e:
        traceback.print_exc()

    try:
        for engraver in coin_details["reverse"]["engravers"]:
            engraver_qid = engravers_dict[engraver]
            to_print = to_print + f"""LAST|P287|{engraver_qid}|P518|Q1542661{ref}\n"""
    except KeyError as e:
        traceback.print_exc()

    if coin_details["type"] == "Standard circulation coin":
        to_print = to_print + f"""LAST|P279|Q110944598{ref}\n"""

    print(to_print)
    return to_print
