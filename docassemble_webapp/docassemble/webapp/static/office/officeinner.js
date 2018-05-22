var yamlFile = '';

function receiveMessage(event){
  if (event.origin !== parentOrigin){
    console.log("Message received from improper origin " + event.origin);
    return;
  }
  console.log("Received action " + event.data.action);
}

function fetchFiles(event){
  $.ajax({
    type: "GET",
    url: "?fetchfiles=1",
    success: function(data){
      if (data.success){
	window.parent.postMessage({"action": "files", "files": data.files}, parentOrigin);
      }
      else{
	window.parent.postMessage({"action": "fail", "tried": "files"}. parentOrigin);
      }
    },
    error: function(xhr, status, error){
      console.log(xhr.responseText);
    },
    dataType: 'json'
  });
}

function fetchVars(event){
  $.ajax({
    type: "GET",
    url: "?pgvars=" + yamlFile,
    success: function(data){
      if (data.success){
	window.parent.postMessage({"action": "vars", "vars": data.variables_json, "vocab": data.vocab_list}, parentOrigin);
      }
      else{
	window.parent.postMessage({"action": "fail", "tried": "vars"}. parentOrigin);
      }
    },
    error: function(xhr, status, error){
      console.log(xhr.responseText);
    },
    dataType: 'json'
  });
}

$( document ).ready(function() {
  window.addEventListener("message", receiveMessage, false);
  window.parent.postMessage({"action": "initialize"}, parentOrigin);
});
