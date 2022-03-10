import json

with open("src/dictionaries/engraver.json") as f:
    engravers_dict = json.loads(f.read())


with open("src/dictionaries/currency.json") as f:
    currency_dict = json.loads(f.read())

with open("src/dictionaries/shapes.json") as f:
    shape_dict = json.loads(f.read())

with open("src/dictionaries/composition.json") as f:
    composition_dict = json.loads(f.read())

with open("src/dictionaries/manufacturing.json") as f:
    manufacturing_dict = json.loads(f.read())


with open("src/dictionaries/mint.json") as f:
    mint_dict = json.loads(f.read())
