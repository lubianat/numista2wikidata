import json
from dictionaries.depict import *
from dictionaries.all import *


with open("src/dictionaries/depict.json") as f:

    dictionary = json.loads(f.read())
    print(dictionary)

for issuer in dicts["issuer"]:
    country_dict_name = f"depict_{issuer.lower()}"
    dict_available = country_dict_name in globals()
    if dict_available:
        if issuer not in dictionary:
            dictionary[issuer] = {}
        dictionary[issuer].update(globals()[country_dict_name])


with open("src/dictionaries/depict.json", "w") as f:

    f.write(json.dumps(dictionary, indent=4, sort_keys=True))
