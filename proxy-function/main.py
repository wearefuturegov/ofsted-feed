# import functions_framework
from flask import Response
from google.cloud import secretmanager
import requests
import json
import os
# import xmltodict

# dev
# endpoint_service = os.environ.get(
#     'ENDPOINT_SERVICE', 'https://fidy.dev.api.ofsted.gov.uk/fidy')

# prod
endpoint_service = os.environ.get(
    'ENDPOINT_SERVICE', 'https://fidy.api.ofsted.gov.uk/fidy')

# @functions_framework.http


def ofsted_feed_proxy(request):

    try:
        print(f'Received a {request.method} request for Ofsted feed data')

        if request.method == 'GET':
            return "Invocation success", 200

        # only supporting json atm
        format = 'json'
        headers = get_headers(format)
        endpoint = get_endpoint(endpoint_service, format)

        print(f"Forwarding the request onto {endpoint}")
        response = requests.get(endpoint, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return Response(response.content, mimetype=response.headers.get('content-type')), response.status_code

        print("Response content-type:")
        print(response.headers.get('content-type'))

        print("Response headers:")
        print(response.headers)

        # print("Response text:")
        # print(response.text)

        try:
            json_data = json.loads(response.text)
            json_data = json.dumps(json_data)
            # print(json.dumps(json_data, indent=4))
        except json.JSONDecodeError:
            print("Error: couldn't load json")
            return "Error occurred", 500

        return Response(json_data, mimetype=f"application/json; charset=utf-8"), response.status_code
    except BaseException as error:
        print('An exception occurred: {}'.format(error))


def get_endpoint(endpoint_service, format):
    endpoint = endpoint_service
    if format == 'json':
        endpoint = endpoint_service + '/' + format
    return endpoint


def get_format(body):
    print("Determinining request format...")
    format = body["format"]
    if format not in ['json', 'xml']:
        format = 'json'
    print('Requested format will be: ' + format)
    return format


def get_headers(format):
    print("Setting up headers")

    ofsted_api_key = get_secret('ofsted_api_key')
    ofsted_service_key = get_secret('ofsted_service_key')
    ofsted_local_authority_code = get_secret('ofsted_local_authority_code')

    # print(f"api_key: {ofsted_api_key}")
    # print(f"service_key: {ofsted_service_key}")
    # print(f"Using LACode: {ofsted_local_authority_code}")

    headers = {
        'content-type': f"application/{format}; charset=utf-8",
        'APIKEY': ofsted_api_key,
        'service-key': ofsted_service_key,
        'LACode': ofsted_local_authority_code
    }

    print("headers:")
    print(headers)
    return headers


def get_secret(name):

    print(f"Getting GCP secret for {name}")
    PROJECT_ID = os.environ.get("PROJECT_ID")
    print(f"Project ID is {PROJECT_ID}")
    secret_id = name
    version_id = 'latest'

    tmpname = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    print(tmpname)

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": tmpname})
    print(response)
    value = response.payload.data.decode("UTF-8")
    print(value)

    return value
