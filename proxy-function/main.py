from flask import Response, abort
import requests
# from requests import Request, Session
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
        xml = request.data.encode('utf-8')
        print("Setting up headers")
        headers = {'content-type': 'application/soap+xml; charset=utf-8'}
        print(f"Forwarding SOAP request to {endpoint_service}")

#         s = Session()
#         req = Request('POST', endpoint_service, headers=headers, data=xml)
#         prepared = req.prepare()
#
#         def pretty_print_POST(req):
#             """
#             At this point it is completely built and ready
#             to be fired; it is "prepared".
#
#             However pay attention at the formatting used in
#             this function because it is programmed to be pretty
#             printed and may differ from the actual request.
#             """
#             print('{}\n{}\r\n{}\r\n\r\n{}'.format(
#                 '-----------START-----------',
#                 req.method + ' ' + req.url,
#                 '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
#                 req.body,
#             ))
#
#         pretty_print_POST(prepared)
#         response = s.send(prepared, timeout=540)
        print("XML Soap Request body:")
        print(xml)
        response = requests.post(endpoint_service, headers=headers, data=xml)
        req = requests.Request('POST', endpoint_service, headers=headers, data=xml)

        req_prep = req.prepare()
        print("Prep request:")
        print(req_prep)
        s = requests.Session()
        print("Session request:")
        print(s)
        http_response = s.send(req_prep)
        print(http_response)
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
