# from zeep import Client
# from zeep.wsse.username import UsernameToken
# from zeep.wsse.signature import Signature
# from zeep.wsse.signature import BinarySignature
# from zeep.wsse import utils
# from xml.dom import minidom
# import xml.etree.ElementTree as ET
# from datetime import datetime, timedelta
# from google.cloud import secretmanager
# import os
# import tempfile
from flask import Response, abort
import requests

endpoint_service = "https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc"
endpoint_wsdl = "https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc?wsdl"

def proxy(request):

    print(f'Received a {request.method} request.')

    # Only temporarily disabling --allow-unauthenticated, so keep it simple.
    token = request.args.get('token')
    if not token or token != 'test':
        print("nah...")
        abort(401)
    else:
        print("Let's go!")

    # Proxy the request
    xml = request.data
    headers = {'content-type': 'application/soap+xml'}
    response = requests.post(endpoint_service, headers=headers, data=xml)
    #response = requests.get(endpoint_wsdl)

    # Debug
    print("Headers:")
    for k,v in response.headers.iteritems():
        print(f'{k}: {v}')
    print(response.content)
    print(response.status_code)

    # Attempt to return
    return Response(response.content, mimetype=response.headers.get('content-type')), response.status_code
