#!/usr/bin/env bash

# xmlsec requirements: https://pypi.org/project/xmlsec

sudo apt-get install libxml2-dev libxmlsec1-dev libxmlsec1-openssl libxml2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -mzeep tweaked_xml/wsdl.xml
