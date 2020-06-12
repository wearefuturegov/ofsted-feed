
const soap = require('soap');
const xml2js = require('xml2js');
const axios = require('axios');
const {SecretManagerServiceClient} = require('@google-cloud/secret-manager');

var url = 'https://ofsted-feed.herokuapp.com/wsdl?wsdl';
// var url = 'http://localhost:8000/wsdl?wsdl';
var client;

async function getSecret(name) {
  ref = `projects/${process.env.PROJECT_NUMBER}/secrets/${name}/versions/latest`
  console.log(`Requesting secret ${ref}`)
  if (!client) client = new SecretManagerServiceClient();
  try {
    const [version] = await client.accessSecretVersion({
      name: ref,
    });
    return version.payload.data.toString('utf8');
  } catch (e) {
    console.error(`error: could not retrieve secret: ${e}`);
    return
  }
}

exports.feed = async (req, res) => {

  if (!req.query.token || req.query.token != process.env.TOKEN) {
    res.send(401, 'please provide a ?token= parameter value.')
  }

  // Create client

// Create client
soap.createClient(url, async function (err, client) {
  if (err) {
    throw err;
  }

  var options = {
    mustUnderstand: true
  }
  var wsSecurity = new soap.WSSecurity('username', 'password', options)
  console.log(wsSecurity.toXML())
  //client.setSecurity(wsSecurity);
  var usernamePassword=wsSecurity.toXML()
  // var parser = new xml2js.Parser();
  // parser.parseString(usernamePassword, function (err, result) {
  //     console.log(result);
  // });
  client.addSoapHeader(usernamePassword)

  var privateKey = await getSecret("private_key");
  var publicKey = await getSecret("public_key");
  var password = '';
  var options = {
    hasTimeStamp: true,
    signatureTransformations: ['http://www.w3.org/2001/10/xml-exc-c14n#'],
    signerOptions: {
        prefix: 'ds',
        attrs: { Id: 'Signature' },
        existingPrefixes: {
            wsse: 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
        }
    }
  };
  var wsSecurityCert = new soap.WSSecurityCert(privateKey, publicKey, password, options);
  // console.log(wsSecurityCert.toXML())
  // var cert=wsSecurity.toXML()
  // parser.parseString(cert, function (err, result) {
  //     console.log(result);
  // });
  client.setSecurity(wsSecurityCert);

  // Add extra security headers for username/password:
  var options = {
    mustUnderstand: true
  }
  var wsSecurity = new soap.WSSecurity('username', 'password', options)
  console.log(wsSecurity.toXML())
  //client.setSecurity(wsSecurity);
  var usernamePassword=wsSecurity.toXML()
  var parser = new xml2js.Parser();
  // parser.parseString(usernamePassword, function (err, result) {
  //     console.log(result);
  // });
  extra_secunity_headers = await parser.parseString(usernamePassword);


  //console.log(client.describe())

  // client.on('request', function (xml, eid) {
  //   console.log(`request`)
  //   console.log(`Exchange ID: ${eid}`)
  //   console.log(`XML Body: ${xml}`);
  //   console.log(`-`);
  // });

  // client.on('message', function (xml, eid) {
  //   console.log(`message`)
  //   console.log(`Exchange ID: ${eid}`)
  //   console.log(`XML Body: ${xml}`);
  //   console.log(`-`);
  // });

  // Add extra headers

  var action = {
    Action: {
      $: {mustUnderstand:1},
      _: "http://information.gateway.ofsted.gov.uk/ispp/ISPPGatewayServices/GetLocalAuthorityChildcareRegister"
    },
    ReplyTo: {
      Address: "http://www.w3.org/2005/08/addressing/anonymous"
    }
  }
  client.addSoapHeader({
    Action: "http://information.gateway.ofsted.gov.uk/ispp/ISPPGatewayServices/GetLocalAuthorityChildcareRegister",
    ReplyTo: {
      Address: "http://www.w3.org/2005/08/addressing/anonymous"
    }
  });
  var builder = new xml2js.Builder();
  var xml = builder.buildObject(action);
  console.log(xml)

  /* 
  * Parameters of the service call, as specified
  * in the WSDL file
  */
  var args = {
    localAuthorityRequest: {
      LocalAuthorityCode: 111
    }
  };

  // var args = fs.readFileSync("soap/OfstedChildcareRegisterLocalAuthorityExtract-v1-3-example.xml")
  // call the service
  client.GetChildcareExtractForLA(args, function (err, res, rawResponse, soapHeader, rawRequest) {
    if (err) {
      console.log(err)
      throw err;
      // print the service returned result
    } else {
      console.log(rawRequest)
      console.log(`Request succeeded`); 
    }
  });
});

}
