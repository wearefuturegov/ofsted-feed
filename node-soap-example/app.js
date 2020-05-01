/*jslint node: true */
"use strict";


var soap = require('soap');
var express = require('express');
var fs = require('fs');

// the function called by the service
function extract_function(args) {
    console.log('extract_function');
    console.log(args)
    var lACode = args.lACode;
    var loginName = args.loginName;
    console.log(`Login ${loginName} from LA ${lACode}`);
    //... example data ...
    return {
      GetChildcareExtractForLAResult: 1,
      xMLExtract: "testing"
    }
}

// the service
var serviceObject = {
  WebExtractServices: {
    WebExtractServicesSoap: {
          GetChildcareExtractForLA: extract_function
        },
        WebExtractServicesSoap12: {
          GetChildcareExtractForLA: extract_function
        }
    }
};

// load the WSDL file
var xml = fs.readFileSync('WebExtractServices.wsdl', 'utf8');
// create express app
var app = express();

// root handler
app.get('/', function (req, res) {
  res.send('Node Soap Example!<br /><a href="https://github.com/macogala/node-soap-example#readme">Git README</a>');
})

// Launch the server and listen
var port = 8000;
app.listen(port, function () {
  console.log('Listening on port ' + port);
  var wsdl_path = "/wsdl";
  soap.listen(app, wsdl_path, serviceObject, xml);
  console.log("Check http://localhost:" + port + wsdl_path +"?wsdl to see if the service is working");
});