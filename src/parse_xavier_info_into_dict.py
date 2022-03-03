import pandas as pd
import json
from dictionaries.engraver import *
from dictionaries.issuer import *

artists_xavier = pd.read_csv("data/catalogue_artists.csv", header=None)

for i, row in artists_xavier.iterrows():
    name = row[0]
    qid = row[1]

    engravers_dict[name] = qid

with open("src/dictionaries/engraver.json", "w+") as f:
    f.write(json.dumps(engravers_dict, indent=4, ensure_ascii=False))


issuers_xavier = pd.read_csv("data/catalogue_countries.csv", header=None)

for i, row in issuers_xavier.iterrows():
    name = row[0]
    qid = row[1]

    if qid == qid:  # Skip NaNs
        issuer_dict[name] = qid

with open("src/dictionaries/issuer.json", "w+") as f:
    f.write(json.dumps(issuer_dict, indent=4, ensure_ascii=False))
