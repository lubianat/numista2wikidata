# numista2wikidata

Code to connect the numista database to Wikidata.

Issuers and Engravers dictionary uses proprietary reconciliation by Xavier (numista) and thus are _not_ openly licensed. 

All other content is available in CC0. 

## Usage 

Add your Numista API Key as `api_key=API_KEY_VALUE` in `src/login_info.py`. You can find it at https://en.numista.com/api/doc/index.php . 

Make sure you don't version control that file. 

Instal package in edit mode: 

` pip install -e .`

Get the coin number on numista, e.g. "336633" and run:

` numis get 336633`