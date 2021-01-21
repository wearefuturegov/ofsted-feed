from flask import Response, abort
import requests
import traceback

endpoint_service = "https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc"
endpoint_wsdl = "https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc?wsdl"

def proxy(request):

    try:
        print(f'Received a {request.method} request.')

        if request.method == 'GET':
            return "Invocation success", 200

        # Proxy the request
        print("Getting request data")
        xml = request.data
        print("Setting up headers")
        headers = {'content-type': 'application/soap+xml'}
        print(f"Forwarding SOAP request to {endpoint_service}")
        response = requests.post(endpoint_service, headers=headers, data=xml)
        #response = requests.get(endpoint_wsdl)

        # Debug
        print("Response headers:")
        for k,v in response.headers.iteritems():
            print(f'{k}: {v}')
        print("Response content:")
        print(response.content)
        print("Response status code:")
        print(response.status_code)

        # Attempt to return
        return Response(response.content, mimetype=response.headers.get('content-type')), response.status_code
    except:
        traceback.print_exc()
