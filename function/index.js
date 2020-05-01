
var soap = require('soap');
var url = 'http://localhost:8000/wsdl?wsdl';

exports.feed = (req, res) => {
  res.send(`Hello ${escapeHtml(req.query.name || req.body.name || 'World')}!`);
};

// Create client
soap.createClient(url, function (err, client) {
  if (err){
    throw err;
  }
  /* 
  * Parameters of the service call: they need to be called as specified
  * in the WSDL file
  */
  var args = {
    loginName: "Acouncil",
    lACode: "AAA"
  };
  // call the service
  client.GetChildcareExtractForLA(args, function (err, res) {
    if (err)
      throw err;
      // print the service returned result
    console.log(res); 
    // GetChildcareExtractForLAResult: 1,
    // xMLExtract: "testing"
  });
});