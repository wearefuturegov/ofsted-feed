// Retrieves the Ofsted WSDL file from the development environment.

const axios = require('axios');
const format = require('xml-formatter');
const fs = require('fs');
const tmp = require('tmp');
const {Storage} = require('@google-cloud/storage');

const urlWsdl = 'https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc?wsdl';
const urlXsd0 = 'https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc?xsd=xsd0';
const urlXsd1 = 'https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc?xsd=xsd1';

const bucketName = "ofsted-feed-soap"
const storage = new Storage();
const bucket = storage.bucket(bucketName);


exports.wsdl = async (req, res) => {

  if (!req.query.token || req.query.token != process.env.TOKEN) {
    res.send(401, 'please provide a ?token= parameter value.')
  }

  response = await axios.get(urlXsd0);
  xml = response.data
  save("xsd0.xml", xml)

  response = await axios.get(urlXsd1);
  xml = response.data
  save("xsd1.xml", xml)

  response = await axios.get(urlWsdl);
  xml = response.data
  save("wsdl.xml", xml)

  console.log(`The wsdl, xsd0 and xsd1 files have been saved to bucket ${bucketName}/development/`)

  // Return the wsdl
  res
    .set("Content-Type", "text/xml; charset=utf8")
    .status(200)
    .send(format(xml));
}


async function save(name, xml) {
  formatted = format(xml);
  file = tmp.fileSync();
  fs.writeFileSync(file.name, formatted)
  await storage.bucket(bucketName).upload(file.name, {destination: `development/${name}`})
  console.log(`XML saved to: ${bucketName}/${name}`);
}
