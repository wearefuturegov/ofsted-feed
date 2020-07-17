
from flask import Flask, Response, abort, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash

import requests
from zeep import Client, xsd
from zeep.wsse.username import UsernameToken
from zeep.wsse.signature import Signature
from zeep.wsse.signature import BinarySignature
from zeep.wsse import utils
from zeep.wsa import WsAddressingPlugin
from xml.dom import minidom
# import xml.etree.ElementTree as ET
from lxml import etree
from datetime import datetime, timedelta
from google.cloud import secretmanager
import os
import tempfile
import base64

app = Flask(__name__)

function_url = os.getenv('FUNCTION_URL')

@app.route('/')
def call():
    
    # Get the access token secret
    access_token = get_secret("access_token")
    if access_token.strip():
        print("Got an access token ok")
    else:
        print("Got an empty access token")

    # Check the access token value
    token = request.args.get('token')
    if not token or token != access_token:
        print("Token not matched")
        abort(401)
    else:
        print("Requesting feed")
        return get_feed()


def get_feed():

    user_name_token = username_password()
    signature = binary_signature_timestamp()

    client = Client('tweaked_xml/wsdl.xml', wsse=[user_name_token, signature], plugins=[WsAddressingPlugin()])
    # client.set_ns_prefix('', 'http://information.gateway.ofsted.gov.uk/ispp')
    # client.set_ns_prefix('s', 'http://www.w3.org/2003/05/soap-envelope')
    client.set_ns_prefix('a', 'http://www.w3.org/2005/08/addressing')
    client.set_ns_prefix('u', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd')
    parameters = {
        'LocalAuthorityCode': 825
      }
    
    # Add a "ReplyTo/Address"
    header = xsd.Element(
        '{http://www.w3.org/2005/08/addressing}ReplyTo',
        xsd.ComplexType([
            xsd.Element(
                '{http://www.w3.org/2005/08/addressing}Address',
                xsd.String()),
        ])
    )
    header_value = header(Address='http://www.w3.org/2005/08/addressing/anonymous')
    
    # Request document
    envelope = client.create_message(client.service, 'GetLocalAuthorityChildcareRegister', localAuthorityRequest=parameters, _soapheaders=[header_value])
    
    # Update a few tricky values

    header = envelope.find('{http://www.w3.org/2003/05/soap-envelope}Header')
    security = header.find('{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security')
    signature = security.find('{http://www.w3.org/2000/09/xmldsig#}Signature')
    signature_value = signature.find('{http://www.w3.org/2000/09/xmldsig#}SignatureValue')
    binary_security_token = security.find('{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}BinarySecurityToken')

    # Reformat base-64 values without line-wrapping 
    # # (possible the server isn't reading them correctly otherwise)
    nowrapping(signature_value)
    nowrapping(binary_security_token)

    # Sprinkle in some 'mustUnderstand' just in case
    mustunderstanders = [
            '{http://www.w3.org/2005/08/addressing}Action', 
            '{http://www.w3.org/2005/08/addressing}To', 
            '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security'
            ]
    for child in header:
        if child.tag in mustunderstanders:
            print(f"Adding mustUnderstand to {child.tag}")
            child.attrib['{http://www.w3.org/2003/05/soap-envelope}mustUnderstand']="1"
    
    # Pop in a couple of missing ids
    for child in header:
        if child.tag == '{http://www.w3.org/2005/08/addressing}To':
            child.attrib['{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id'] = "_1"
    for child in security:
        if child.tag == '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}UsernameToken':
            child.attrib['{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id'] = "_2"
    
    # Delete duplicated elements
    duplicates = ['{http://www.w3.org/2005/08/addressing}Action', '{http://www.w3.org/2005/08/addressing}To', '{http://www.w3.org/2005/08/addressing}MessageID']
    deduped = {}
    insert_index = 0
    for child in header:
        if child.tag in duplicates:
            deduped[child.tag] = child
            header.remove(child)
        if child.tag == '{http://www.w3.org/2005/08/addressing}ReplyTo':
            insert_index = header.index(child)

    # Re-insert the de-duped elements
    for child in deduped.values():
        insert_index = insert_index + 1
        header.insert(insert_index, child)

    for child in header:
        print(f' - {child.tag[child.tag.rindex("}")+1:]}  {child.tag}  -->  {child.attrib}')
        if child.tag=='{http://www.w3.org/2005/08/addressing}ReplyTo':
            print(header.index(child))
    
    # xmlstr =  minidom.parseString(ET.tostring(node)).toprettyxml(indent="   ")
    xmlstr = str(etree.tostring(envelope, encoding='unicode', pretty_print=True))
    print(type(xmlstr))

    # xmlstr=tweak(xmlstr)

    ##print(xmlstr)
    if os.path.isdir('/output'):
        with open('/output/actual1.xml', 'w+') as f:
            f.write(xmlstr)
            print("Saved generated XML message.")
    if os.path.isdir('../secrets/compare'):
        with open('../secrets/compare/actual1.xml', 'w+') as f:
            f.write(xmlstr)
            print("Saved generated XML message.")

    # response = call_proxy(envelope)

    # if response.status_code != 200:
    #     print(f"{response.status_code}: {response.text}")

    #return minidom.parseString(response.text)
    #ET.tostring(feed, encoding='unicode').toprettyxml(indent="   ")

    #return Response(f"{response.status_code} -- {response.text}"), 200
    # return Response(response.text, mimetype='text/xml'), response.status_code
    return Response(str(etree.tostring(envelope, encoding='unicode', pretty_print=True)), mimetype='text/xml'), 200


# def tweak(xmlstr):
#     result = xmlstr
#     # result = renamespace('soap-env', 's', result)
#     # result = renamespace('ns0', 's', result)
#     # result = renamespace('wsa', 'a', result)
#     # result = renamespace('ns1', 'a', result)
#     # result = renamespace('wsse', 'o', result)
#     # result = renamespace('wsu', 'u', result)
#     # result = renamespace('ns4', 'u', result)
#     # result = result.replace('<a:Action>', '<a:Action s:mustUnderstand="1">')
#     # result = result.replace('<a:To>', '<a:To s:mustUnderstand="1" u:Id="_1">')
#     # result = result.replace('<o:Password Type="', '<o:Password o:Type="')
#     return result

# def renamespace(current, updated, xmlstr):
#     result = xmlstr
#     result = result.replace(f'xmlns:{current}', f'xmlns:{updated}')
#     result = result.replace(f'{current}:', f'{updated}:')
#     return result

def nowrapping(element):
    """ Updates the text of the given element so that there are no line-breaks in the base-64 text value. """
    element_text = element.text
    data = base64.b64decode(element_text)
    b64 = base64.b64encode(data)
    element.text = b64


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
    password = get_secret('password')
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

    if not name in current_app.config:

        print(f"Getting GCP secret for {name}")
        PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
        secrets = secretmanager.SecretManagerServiceClient()
        current_app.config[name] = secrets.access_secret_version(f"projects/{PROJECT_NUMBER}/secrets/{name}/versions/latest").payload.data.decode("utf-8")

    return current_app.config[name]


def call_proxy(xml):

    # Provide the token in the request to the receiving function
    headers = {'Authorization': f'bearer {jwt()}'}
    body = etree.tostring(xml, encoding='utf-8', xml_declaration=True)
    # body = ET.tostring(xml, encoding='unicode')
    response = requests.post(function_url, headers=headers, data=body)
    return response


def jwt(): 
    """ See: https://cloud.google.com/functions/docs/securing/authenticating#functions-bearer-token-example-python """

    # Short-circuit for running locally
    local_token = os.getenv('FUNCTION_TOKEN')
    if local_token:
        print(f"Local token: {local_token}")
        return local_token

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
