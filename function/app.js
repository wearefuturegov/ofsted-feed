
const soap = require('soap');
const xml2js = require('xml2js');

var url = 'https://ofsted-feed.herokuapp.com/wsdl?wsdl';

exports.feed = (req, res) => {

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