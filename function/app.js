
const soap = require('soap');
const xml2js = require('xml2js');
const axios = require('axios');

var url = 'https://ofsted-feed.herokuapp.com/wsdl?wsdl';


exports.feed = (req, res) => {

  if (!req.query.token || req.query.token != process.env.TOKEN) {
    res.send(401, 'please provide a ?token= parameter value.')
  }

  // Ping the stub to see if our egress IP is the static IP we expect:
  axios.get('https://ofsted-feed.herokuapp.com')
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });

  // Create client
  soap.createClient(url, function (err, client) {
    if (err){
      throw err;
    }
    
    var args = {
      loginName: "Acouncil",
      lACode: "AAA"
    };

    // call the service
    client.GetChildcareExtractForLA(args, function (err, response) {
      if (err)
        throw err;

      var parser = new xml2js.Parser();
      parser.parseString(response, function (err, result) {
        if (err)
          throw err;

        res.json(result);
      });
      
    });

  });

};