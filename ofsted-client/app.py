
from flask import Flask, render_template, make_response, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.wsse.signature import Signature
from zeep.wsse.signature import BinarySignature
from zeep.wsse import utils
from xml.dom import minidom
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from google.cloud import secretmanager
import os
import tempfile

app = Flask(__name__)

function = os.getenv('FUNCTION')

@app.route('/')
def get_feed():

    user_name_token = username_password()
    signature = binary_signature_timestamp()

    client = Client('tweaked_xml/wsdl.xml', wsse=[user_name_token, signature])
    parameters = {
        'LocalAuthorityCode': 825
      }
    
    # Request document
    node = client.create_message(client.service, 'GetLocalAuthorityChildcareRegister', localAuthorityRequest=parameters)
    xmlstr = minidom.parseString(ET.tostring(node)).toprettyxml(indent="   ")
    print(xmlstr)

    # Response document
    result = client.service.GetLocalAuthorityChildcareRegister(localAuthorityRequest=parameters)
    xml = minidom.parseString(ET.tostring(result)).toprettyxml(indent="   ")
    print(xml)

    return xml


class BinarySignatureTimestamp(BinarySignature):
    def apply(self, envelope, headers):
        security = utils.get_security_header(envelope)

        created = datetime.utcnow()
        expired = created + timedelta(minutes=5)

        timestamp = utils.WSU('Timestamp')
        timestamp.append(utils.WSU('Created', created.replace(microsecond=0).isoformat()+'Z'))
        timestamp.append(utils.WSU('Expires', expired.replace(microsecond=0).isoformat()+'Z'))

        security.append(timestamp)

        super().apply(envelope, headers)
        return envelope, headers


def username_password():

    username = get_secret('username', '../secrets/cert/username.txt')
    password = get_secret('username', '../secrets/cert/password.txt')
    return UsernameToken(username, password)


def binary_signature_timestamp():

    private = get_secret('private_key', '../secrets/cert/privkey.pem')
    public = get_secret('public_key', '../secrets/cert/cert.pem')

    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as priv:
            priv.write(private)
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as pub:
            pub.write(public)

        # https://github.com/mvantellingen/python-zeep/issues/996
        return BinarySignatureTimestamp(priv.name, pub.name)
        # return Signature("../secrets/cert/privkey.pem", "../secrets/cert/cert.pem")

    finally:
        os.remove(priv.name)
        os.remove(pub.name)


def get_secret(name, local_file):

    if local_file and os.path.isfile(local_file):
        with open(local_file, 'r') as secret:
            return secret.read()

    PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
    secrets = secretmanager.SecretManagerServiceClient()
    return secrets.access_secret_version(f"projects/{PROJECT_NUMBER}/secrets/{name}/versions/latest").payload.data.decode("utf-8")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
