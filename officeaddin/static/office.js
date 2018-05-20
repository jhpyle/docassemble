var serverName = '';
function receiveMessage(event)
{
  if (event.origin !== serverName){
    console.log("Message received from improper origin.")
    return;
  }
  console.log("Received action " + event.data.action);
  if (event.data.action == 'initialize'){
    $("#server").hide();
  }
}

function testServer(){
  $("#server")[0].contentWindow.postMessage({"action": "test"}, serverName);
}

function validateUrl(value) {
  return /^https?:\/\/\S/i.test(value);
}

$( document ).ready(function() {
  var doc = document.getElementById('server').contentWindow.document;
  doc.open();
  doc.write('<html><head><title></title></head><body>Loading...</body></html>');
  doc.close();
  $("#serverSet").on('click', function(){
    if (!validateUrl($("#serverName").val())){
      $("#serverNameError").show();
      return false;
    }
    $("#serverNameError").hide();
    $("#serverNameDiv").hide();
    serverName = $("#serverName").val();
    Cookies.set('serverName', serverName, { expires: 999999 });
    $("#server").attr('src', serverName + '/officeaddin');
    $("#server").show();
    return false;
  });
  window.addEventListener("message", receiveMessage, false);
  serverName = Cookies.get('serverName');
  if (serverName){
    $("#serverNameDiv").hide();
    $("#server").attr('src', serverName + '/officeaddin');
    $("#server").show();
  }
});
