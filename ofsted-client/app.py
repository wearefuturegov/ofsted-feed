
from flask import Flask, Response, abort, request
from werkzeug.security import generate_password_hash, check_password_hash

import requests
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

function_url = os.getenv('FUNCTION_URL')

@app.route('/')
def call():

    print("Anything?")
    
    access_token = get_secret("access_token")
    if access_token.strip():
        print("Got an access token ok")
    else:
        print("Got an empty access token")

    # Check the access token
    token = request.args.get('token')
    if not token or token != access_token:
        print("nah...")
        abort(401)
    else:
        print("Let's go!")
        return get_feed()


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

    response = call_proxy(node)

    if response.status_code != 200:
        print(f"{response.status_code}: {response.text}")

    #return minidom.parseString(response.text)
    #ET.tostring(feed, encoding='unicode').toprettyxml(indent="   ")

    return Response(response.text), 200
    #return Response(response.text, mimetype='text/xml'), response.status_code


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

    username = get_secret('username')
    password = get_secret('username')
    return UsernameToken(username, password)


def binary_signature_timestamp():

    private = get_secret('private_key')
    public = get_secret('certificate')

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


def get_secret(name):

    print(f"Getting GCP secret for {name}")
    PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
    secrets = secretmanager.SecretManagerServiceClient()
    return secrets.access_secret_version(f"projects/{PROJECT_NUMBER}/secrets/{name}/versions/latest").payload.data.decode("utf-8")


def call_proxy(xml):

    # Provide the token in the request to the receiving function
    headers = {'Authorization': f'bearer {jwt()}'}
    body = ET.tostring(xml, encoding='unicode')
    response = requests.post(function_url, headers=headers, data=body)
    return response


def jwt(): 
    """ See: https://cloud.google.com/functions/docs/securing/authenticating#functions-bearer-token-example-python """

    # Constants for setting up metadata server request
    # See https://cloud.google.com/compute/docs/instances/verifying-instance-identity#request_signature
    metadata_server_url = 'http://metadata/computeMetadata/v1/instance/service-accounts/default/identity?audience='
    token_full_url = metadata_server_url + function_url
    token_headers = {'Metadata-Flavor': 'Google'}

    # Fetch the token
    token_response = requests.get(token_full_url, headers=token_headers)
    jwt = token_response.text
    print(f"jwt is: {jwt}")

    return jwt


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
