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

var wait_amount = 100;

if (interview == 'signature.yml' || interview == 'metadata.yml' || interview == 'help.yml'){
    casper.options.viewportSize = {width: 650, height: 1136};
    if (interview == 'signature.yml'){
	wait_amount = 2000;
    }
}
else{
    casper.options.viewportSize = {width: 1005, height: 650};
}

var url = "http://localhost?i=docassemble.base:data/questions/examples/" + interview

casper.start();

casper.thenOpen(url, function() {
    this.wait(wait_amount, function(){
	this.capture(casper.cli.get(1));
    });
});

casper.run();

