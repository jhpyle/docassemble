var casper = require('casper').create(
// {
//   verbose: true,
//   logLevel: "debug",
//   pageSettings: {
//     webSecurityEnabled: false
//   }
// }
);

var interview = casper.cli.get(0);

var wait_amount = 500;

if (interview == 'signature.yml'){
  wait_amount = 2000;
  casper.options.viewportSize = {width: 640, height: 1136};
}
else{
  casper.options.viewportSize = {width: 1136, height: 640};
}

var url = "http://localhost?i=docassemble.base:data/questions/examples/" + interview

casper.start();

casper.thenOpen(url, function() {
  this.wait(wait_amount, function(){
    this.capture(casper.cli.get(1));
  });
});

casper.run();
//496x520+86+78
