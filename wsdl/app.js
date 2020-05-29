// Retrieves the Ofsted WSDL file from the development environment.

const axios = require('axios');

var url = 'https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc?wsdl';

exports.wsdl = async (req, res) => {

  if (!req.query.token || req.query.token != process.env.TOKEN) {
    res.send(401, 'please provide a ?token= parameter value.')
  }

  try {
    const response = await axios.get(url);
    console.log(response);
    xml = response.data

    res
      .set("Content-Type", "text/xml; charset=utf8")
      .status(200)
      .send(xml);

  } catch (error) {
    console.error(error);
  }

}
