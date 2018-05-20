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
function validateUrl(value) {
  return /^(?:(?:(?:https?):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:[/?#]\S*)?$/i.test(value);
}

$( document ).ready(function() {
  $("#serverSet").on('click', function(){
    if (!validateUrl($("#serverName").val())){
      $("#serverNameError").show();
      return false;
    }
    $("#serverNameError").hide();
    console.log("Hiding serverNameDiv because serverSet");
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
    console.log("Hiding serverNameDiv");
    $("#serverNameDiv").hide();
    $("#server").attr('src', serverName + '/officeaddin');
    $("#server").show();
  }
});
