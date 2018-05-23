var parwindow = window.parent;

function receiveMessage(event){
  if (event.origin !== parentOrigin){
    console.log("Message received from improper origin " + event.origin);
    return;
  }
  console.log("Received action " + event.data.action);
  if (event.data.action == 'fetchFiles'){
    fetchFiles();
  }
  else if (event.data.action == 'fetchVars'){
    fetchVars(event.data.file);
  }
}

function fetchFiles(){
  $.ajax({
    type: "GET",
    url: "?fetchfiles=1",
    success: function(data){
      console.log("Got response for fetchFiles");
      if (data.success){
	parwindow.postMessage({"action": "files", "files": data.files}, parentOrigin);
      }
      else{
	parwindow.postMessage({"action": "fail", "tried": "files"}. parentOrigin);
      }
    },
    error: function(xhr, status, error){
      console.log(xhr.responseText);
    },
    dataType: 'json'
  });
}

function fetchVars(yamlFile){
  $.ajax({
    type: "GET",
    url: "?pgvars=" + yamlFile,
    success: function(data){
      console.log("Got response for fetchVars");
      if (data.success){
	parwindow.postMessage({"action": "vars", "vars": data.variables_json, "vocab": data.vocab_list}, parentOrigin);
      }
      else{
	parwindow.postMessage({"action": "fail", "tried": "vars"}. parentOrigin);
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
  parwindow.postMessage({"action": "initialize"}, parentOrigin);
});
