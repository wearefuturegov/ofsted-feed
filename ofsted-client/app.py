import os
import json
import logging
import requests
from flask import Flask, request, abort, Response, current_app
from google.cloud import secretmanager

app = Flask(__name__)

# setup environmental variables
function_url = os.getenv('FUNCTION_URL')
port = int(os.environ.get('PORT', 8080))
app.logger.info(port)

# """Default route"""
# app.logger.debug('this is a DEBUG message')
# app.logger.info('this is an INFO message')
# app.logger.warning('this is a WARNING message')
# app.logger.error('this is an ERROR message')
# app.logger.critical('this is a CRITICAL message')

# This sets the logging level so its the same level in gunicorn and flask
# https://trstringer.com/logging-flask-gunicorn-the-manageable-way/
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/', methods=['GET'])
def get_json():
    if verify():
        app.logger.info("Requesting JSON file")
        response = get_feed('json')

        if response is None:
            return Response("No response received", status=500)

        app.logger.info("Response returned")

        json_data = response.text

        return Response(json_data, mimetype='application/json'), 200
    else:
        abort(401, 'Unauthorized: Invalid token')

def verify():
    access_token = get_secret("access_token")
    if access_token.strip():
        app.logger.info("Got an access token ok")
    else:
        app.logger.info("Got an empty access token")

    token = request.args.get('token')
    app.logger.info('Verifying token')
    if token == access_token:
        app.logger.info('Token verified successfully')
        return True
    else:
        app.logger.info('Token not verified')
        return False


def get_feed(format):
    response = call_proxy(format)

    if response.status_code != 200:
        app.logger.error(f"Error {response.status_code}: No response received")
        return None

    return response

def call_proxy(format):
    request_format = format or "json"
    app.logger.info('call_proxy(%s)', request_format)

    # Provide the token in the request to the receiving function
    headers = {'Authorization': f'bearer {jwt()}', 'Accept': 'application/xml'}
    app.logger.debug(headers)

    app.logger.info('Sending to: %s', function_url)
    response = requests.post(function_url, headers=headers, json={"format": format})

    return response


def jwt():
    """ See: https://cloud.google.com/functions/docs/securing/authenticating#functions-bearer-token-example-python """
    app.logger.info('jwt()')

    # Short-circuit for running locally
    local_token = os.getenv('FUNCTION_TOKEN')
    if local_token:
        app.logger.info(f"Local token: {local_token}")
        return local_token

    # Constants for setting up metadata server request
    # See https://cloud.google.com/compute/docs/instances/verifying-instance-identity#request_signature
    metadata_server_url = 'http://metadata/computeMetadata/v1/instance/service-accounts/default/identity?audience='
    token_full_url = metadata_server_url + function_url
    token_headers = {'Metadata-Flavor': 'Google'}

    # Fetch the token
    token_response = requests.get(token_full_url, headers=token_headers)
    jwt = token_response.text
    app.logger.info(f"jwt is: {jwt}")

    return jwt


def get_secret(name):

    if not name in current_app.config:

        # current_app.config[name] = name
        # return current_app.config[name]

        app.logger.info(f"Getting GCP secret for {name}")
        PROJECT_ID = os.environ.get("PROJECT_ID")
        app.logger.info(PROJECT_ID)
        secret_id = name
        version_id = 'latest'

        tmpname = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
        app.logger.info(tmpname)

        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": tmpname})
        app.logger.info(response)
        value = response.payload.data.decode("UTF-8")

        current_app.config[name] = value

    return current_app.config[name]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)
