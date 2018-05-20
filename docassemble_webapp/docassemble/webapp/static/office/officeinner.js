var parentOrigin = "http://localhost";
function receiveMessage(event)
{
  if (event.origin !== parentOrigin){
    console.log("Message received from improper origin.")
    return;
  }
  console.log("Received message " + event.data);
}
$( document ).ready(function() {
  window.addEventListener("message", receiveMessage, false);
  window.parent.postMessage('Hello world!', 'http://localhost');
});
