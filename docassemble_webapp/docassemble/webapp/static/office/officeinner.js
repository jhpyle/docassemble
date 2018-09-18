var parwindow = window.parent;

function receiveMessage(event){
    if (event.origin !== parentOrigin){
        //console.log("Message received from improper origin " + event.origin);
        return;
    }
    //console.log("Received action " + event.data.action);
    if (event.data.action == 'fetchFiles'){
        fetchFiles();
    }
    else if (event.data.action == 'fetchVars'){
        //console.log("file is " + event.data.file)
        fetchVars(event.data.file);
    }
    else if (event.data.action == 'fetchVarsEtc'){
        //console.log("file is " + event.data.file)
        fetchVarsEtc(event.data.file);
    }
    else if (event.data.action == 'uploadFile'){
        uploadFile(event.data.yamlFile, event.data.fileName, event.data.content);
    }
}

function fetchFiles(){
    //console.log("Calling fetchFiles");
    $.ajax({
        type: "GET",
        url: "?fetchfiles=1",
        success: function(data){
            //console.log("Got response for fetchFiles");
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
    //console.log("Calling fetchVars");
    if (yamlFile == null){
        return;
    }
    $.ajax({
        type: "GET",
        url: "?pgvars=" + yamlFile,
        success: function(data){
            //console.log("Got response for fetchVars");
            if (data.success){
                parwindow.postMessage({"action": "vars", "vars": data.variables_json, "vocab": data.vocab_list}, parentOrigin);
            }
            else{
                parwindow.postMessage({"action": "fail", "tried": "vars"}, parentOrigin);
            }
        },
        error: function(xhr, status, error){
            console.log(xhr.responseText);
        },
        dataType: 'json'
    });
}

function fetchVarsEtc(yamlFile){
    //console.log("Calling fetchVarsEtc with " + yamlFile);
    if (yamlFile == null){
        yamlFile = '';
    }
    $.ajax({
        type: "GET",
        url: "?pgvars=" + yamlFile + '&html=1',
        success: function(data){
            //console.log("Got response for fetchVarsEtc");
            if (data.success){
                parwindow.postMessage({"action": "varsetc", "vars": data.variables_html, "vocab": data.vocab_list, "vocab_dict": data.vocab_dict}, parentOrigin);
            }
            else{
                parwindow.postMessage({"action": "fail", "tried": "varsetc"}, parentOrigin);
            }
        },
        error: function(xhr, status, error){
            console.log(xhr.responseText);
        },
        dataType: 'json'
    });
}

function uploadFile(yamlFile, fileName, content){
    //console.log("Calling uploadFile");
    if (yamlFile == null){
        yamlFile = ""
    }
    $.ajax({
        type: "POST",
        url: "?pgvars=" + yamlFile + '&html=1',
        data: $.param({'filename': fileName, 'content': content, 'csrf_token': $("input[name='csrf_token']").val()}),
        success: function(data){
            //console.log("Got response for uploadFile");
            if (data.success){
                parwindow.postMessage({"action": "varsetc", "vars": data.variables_html, "vocab": data.vocab_list, "vocab_dict": data.vocab_dict, "uploaded": true}, parentOrigin);
            }
            else{
                parwindow.postMessage({"action": "fail", "tried": "uploadFile"}, parentOrigin);
            }
        },
        error: function(xhr, status, error){
            console.log(xhr.responseText);
            parwindow.postMessage({"action": "fail", "tried": "uploadFile"}, parentOrigin);
        },
        dataType: 'json'
    });
}

$( document ).ready(function() {
    //console.log("In document ready in officeinner.js");
    window.addEventListener("message", receiveMessage, false);
    parwindow.postMessage({"action": "initialize"}, parentOrigin);
});
