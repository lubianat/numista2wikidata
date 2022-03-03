import json

with open("src/dictionaries/currency.json") as f:
    currency_dict = json.loads(f.read())
