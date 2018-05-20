function receiveMessage(event)
{
  if (event.origin !== parentOrigin){
    console.log("Message received from improper origin " + event.origin);
    return;
  }
  console.log("Received action " + event.data.action);
}

$( document ).ready(function() {
  window.addEventListener("message", receiveMessage, false);
  window.parent.postMessage({"action": "initialize"}, parentOrigin);
});
