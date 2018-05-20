var childOrigin = "https://demo.docassemble.org";
function receiveMessage(event)
{
  if (event.origin !== childOrigin){
    console.log("Message received from improper origin.")
    return;
  }
  console.log("Received message " + event.data);
}
$( document ).ready(function() {
  window.addEventListener("message", receiveMessage, false);
}
