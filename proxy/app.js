
const soap = require('soap');
const xml2js = require('xml2js');
const axios = require('axios');
const fs = require('fs')
const {SecretManagerServiceClient} = require('@google-cloud/secret-manager');

var url = process.env.WSDL;
var client;



exports.feed = async (req, res) => {

  if (!req.query.token || req.query.token != process.env.TOKEN) {
    res.send(401, 'please provide a ?token= parameter value.')
  }

  query();

}


async function usernamePasswordSecurity() {

    var options = {
      mustUnderstand: true
    }

    var username = await getSecret("username", "../credentials/cert/username.txt")
    var password = await getSecret("password", "../credentials/cert/password.txt")

    return new soap.WSSecurity(username, password, options)
}


async function digitalSignatureSecurity() {
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

  var privateKey = await getSecret("private_key", "../credentials/cert/privkey.pem");
  var publicKey = await getSecret("public_key", "../credentials/cert/pubkey.pem");
  var keypassword = '';

  return new soap.WSSecurityCert(privateKey, publicKey, keypassword, options);
}


async function injectSecondSecurityHeaders(client, wsSecurity) {

    var usernamePassword=wsSecurity.toXML()
    console.log(usernamePassword)
    var parser = new xml2js.Parser();
    secondSecunityHeaders = parser.parseString(usernamePassword);
}


function addeExtraHeaders(client) {

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
}


async function query() {

  // Create client
  soap.createClient(url, async function (err, client) {
    if (err) {
      throw err;
    }

    wsSecurityCert = digitalSignatureSecurity()
    client.setSecurity(wsSecurityCert);

    // Add extra security headers for username/password:
    wsSecurity = await usernamePasswordSecurity()
    console.log(wsSecurity)
    console.log(wsSecurity.toXML())
    injectSecondSecurityHeaders(client, wsSecurity)
    //client.setSecurity(wsSecurity);

    //console.log(client.describe())

    client.on('request', function (xml, eid) {
      console.log(`request`)
      // console.log(`Exchange ID: ${eid}`)
      console.log(`XML Body: ${xml}`);
      console.log(`-`);
    });

    // client.on('message', function (xml, eid) {
    //   console.log(`message`)
    //   console.log(`Exchange ID: ${eid}`)
    //   console.log(`XML Body: ${xml}`);
    //   console.log(`-`);
    // });

    /* 
    * Parameters of the service call, as specified
    * in the WSDL file
    */
    var args = {
      localAuthorityRequest: {
        LocalAuthorityCode: 825
      }
    };

    // var args = fs.readFileSync("soap/OfstedChildcareRegisterLocalAuthorityExtract-v1-3-example.xml")
    // call the service
    console.log(client)
    client.GetLocalAuthorityChildcareRegister(args, function (err, res, rawResponse, soapHeader, rawRequest) {
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


async function getSecret(name, localpath) {

  // Local run
  if (fs.existsSync(localpath)) {
    return fs.readFileSync(localpath)
  }

  // Secrets manager
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
    throw e;
  }

}


// Local run
query()