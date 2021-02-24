from flask import Response, abort
import requests
# from requests import Request, Session
import traceback

endpoint_service = "https://infogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc"
endpoint_wsdl = "https://infogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc?wsdl"
# endpoint_service = "https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc"
# endpoint_wsdl = "https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc?wsdl"

def proxy(request):

    try:
        print(f'Received a {request.method} request.')

        if request.method == 'GET':
            return "Invocation success", 200

        print("Original request headers:")
        print(request.headers)
        # Proxy the request
        print("Getting request data")
        xml = request.data
        print("Setting up headers")
        headers = {'content-type': 'application/soap+xml; charset=utf-8'}
        print(f"Forwarding SOAP request to {endpoint_service}")

#         print("XML Soap Request body:")
#         body = xml.decode('utf-8')
#         print(body)

        response = requests.post(endpoint_service, headers=headers, data=xml)
#         req = requests.Request('POST', endpoint_service, headers=headers, data=xml)
#
#         req_prep = req.prepare()
#         print("Prep request:")
#         print(req_prep)
#         s = requests.Session()
#         print("Session request:")
#         print(s)
#         response = s.send(req_prep)
#         print(response)
        #response = requests.get(endpoint_wsdl)

        # Debug
        print("Response headers:")
        print(response.headers)
#         for k,v in response.headers.iteritems():
#             print(f'{k}: {v}')
        print("Response content:")
        print(response.content)
        print("Response status code:")
        print(response.status_code)

        # Attempt to return
        return Response(response.content, mimetype=response.headers.get('content-type')), response.status_code
    except BaseException as error:
        print('An exception occurred: {}'.format(error))
