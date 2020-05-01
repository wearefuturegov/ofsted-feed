const express = require('express')
const bodyParser = require('body-parser')
const soap = require('node-soap')
const fs = require('fs')

require("dotenv").config()

const stub = require("./stub")

function splitter_function(args) {
    console.log('splitter_function');
    var splitter = args.splitter;
    var splitted_msg = args.message.split(splitter);
    var result = [];
    for(var i=0; i<splitted_msg.length; i++){
      result.push(splitted_msg[i]);
    }
    return {
        result: result
        }
}

var serviceObject = {
    MessageSplitterService: {
          MessageSplitterServiceSoapPort: {
              MessageSplitter: splitter_function
          },
          MessageSplitterServiceSoap12Port: {
              MessageSplitter: splitter_function
          }
      }
  };
  
  // load the WSDL file
  var xml = fs.readFileSync('soap/WebExtractServices.wsdl', 'utf8');
  // create express app
  var app = express();
  
  // root handler
  app.get('/', async (req, res) => {
    if(req.query.api_key === process.env.API_KEY){
      res.send(await stub())
    } else {
      res.status(401)
      res.send("Unauthorised")
    }
  })
  
  var port = process.env.PORT || 8000;
  // Launch the server and listen on *port*
  app.listen(port, function () {
    console.log('Listening on port ' + port);
    var wsdl_path = "/wsdl";
    // create SOAP server that listens on *path*
    // soap.listen(app, wsdl_path, serviceObject, xml);
    console.log("Check http://localhost:" + port + wsdl_path +"?wsdl to see if the service is working");
  });