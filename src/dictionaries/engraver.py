import json

with open("src/dictionaries/engraver.json") as f:
    engravers_dict = json.loads(f.read())
