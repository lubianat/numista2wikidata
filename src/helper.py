from textwrap import indent
import requests
import sys
import requests
from dictionaries.all import *
import traceback
import json
import clipboard


def add_key(dictionary, string):
    clipboard.copy(string)
    qid = input(f"What is the qid for: {string} ?")
    dictionary[string] = qid
    return dictionary


def get_coin_statements(coin_type_id):
    global dicts

    coin_details = get_details(coin_type_id)

    # Extract fields of interest
    ref = f'|S854|"https://en.numista.com/catalogue/type{str(coin_type_id)}.html"|S248|Q84602292'

    currency_name = coin_details["value"]["currency"]["full_name"]

    try:
        currency = dicts["currency"][currency_name].replace("Q", "U")
    except KeyError:
        traceback.print_exc()
        dicts["currency"] = add_key(dicts["currency"], currency_name)

        with open("src/dictionaries/currency.json", "w+") as f:
            f.write(
                json.dumps(
                    dicts["currency"], indent=4, ensure_ascii=False, sort_keys=True
                )
            )

    value = coin_details["value"]["numeric_value"]
    min_year = coin_details["min_year"]
    max_year = coin_details["max_year"]
    title_en = f"{coin_details['title']} coin ({min_year} - {max_year})"
    title_pt = f"moeda de {coin_details['title']} ({min_year} - {max_year})"

    try:
        material = dicts["composition"][coin_details["composition"]["text"]]
    except Exception:
        traceback.print_exc()
        text = coin_details["composition"]["text"]
        print(
            f"""
            CREATE
            LAST|Len|"{text}"
            LAST|Den|"metallic material used for coins"  """
        )
        for key, value in dicts["composition"].items():
            if key.lower() in text.lower():
                print(
                    f"""
            LAST|P527|{value}{ref}"""
                )
        if "Bimetallic" in text:
            print(f"""LAST|P279|Q110983998{ref}""")
        else:
            print(f"""LAST|P279|Q214609{ref}""")

        dicts["composition"] = add_key(dicts["composition"], text)

        with open("src/dictionaries/composition.json", "w+") as f:
            f.write(
                json.dumps(
                    dicts["composition"], indent=4, ensure_ascii=False, sort_keys=True
                )
            )

    country = dicts["issuer"][coin_details["issuer"]["name"]]
    country_name = coin_details["issuer"]["name"]
    diameter = coin_details["size"]
    weight = coin_details["weight"]
    shape = dicts["shapes"][coin_details["shape"]]

    try:
        mints = []
        for mint in coin_details["mints"]:

            try:
                mints.append(dicts["mint"][mint["name"]])
            except Exception:
                traceback.print_exc()
                dicts["composition"] = add_key(dicts["mint"], mint["name"])
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
    LAST|P1419|{shape}{ref}
    LAST|P10205|"{str(coin_type_id)}"{ref}
    LAST|P3934|{value}{currency}{ref}
    """
    for mint in mints:
        to_print = to_print + f"""LAST|P176|{mint}{ref}\n"""
    try:
        series = dicts["series"][coin_details["series"]]
        to_print = to_print + f"""LAST|P279|{series}{ref}\n"""
    except:
        pass

    try:
        thickness = coin_details["thickness"]
        to_print = to_print + f"""LAST|P2610|{thickness}U174789{ref}\n"""
    except:
        pass

    try:
        engraver = ""
        for engraver in coin_details["obverse"]["engravers"]:
            engraver_qid = dicts["engraver"][engraver]
            to_print = to_print + f"""LAST|P287|{engraver_qid}|P518|Q257418{ref}\n"""
    except KeyError as e:
        traceback.print_exc()

        if engraver != "":
            qs = f"""
            CREATE
            LAST|Len|"{engraver}"
            LAST|Den|"engraver"
            LAST|P31|Q5
            LAST|P106|Q329439{ref}  """
            print(qs)
            dicts["engraver"] = add_key(dicts["engraver"], engraver)

            with open("src/dictionaries/engraver.json", "w+") as f:
                f.write(
                    json.dumps(
                        dicts["engraver"], indent=4, ensure_ascii=False, sort_keys=True
                    )
                )

    try:
        engraver = ""
        for engraver in coin_details["reverse"]["engravers"]:
            engraver_qid = dicts["engraver"][engraver]
            to_print = to_print + f"""LAST|P287|{engraver_qid}|P518|Q1542661{ref}\n"""
    except KeyError as e:
        traceback.print_exc()

        if engraver != "":
            engraver = ""
            qs = f"""
                CREATE
                LAST|Len|"{engraver}"
                LAST|Den|"engraver"
                LAST|P31|Q5
                LAST|P106|Q329439{ref}  """
            print(qs)
            dicts["engraver"] = add_key(dicts["engraver"], engraver)

            with open("src/dictionaries/engraver.json", "w+") as f:
                f.write(
                    json.dumps(
                        dicts["engraver"], indent=4, ensure_ascii=False, sort_keys=True
                    )
                )

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
    print(to_print)
    return to_print


def get_details(coin_type_id):
    api_key = "2GtYY2INUIgmEYynq7xAHTqRY01Us4dOXIf30mlA"
    client_id = "231967"
    endpoint = "https://api.numista.com/api/v2"

    response = requests.get(
        endpoint + "/coins/" + coin_type_id,
        params={"lang": "en"},
        headers={"Numista-API-Key": api_key},
    )
    coin_details = response.json()
    return coin_details
