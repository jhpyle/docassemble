'use strict';

console.log("Starting script");
var pythonVariableChar = /[A-Za-z0-9\_]/g;
var daServer = null;
var daFullServer = null;
var daYAML = null;
var daVocab = [];
var daVocabDict = Object();
var daUploadStatus = 'waiting';
var onDesktop = false;
var fileErrorTimeout = null;
var autocompleteInterval = null;
var lastCheckup = Date.now();
var autoCompleteEntries = [];
//var daVocabLower = [];
var attrs_showing = Object();

function flash(message, priority){
    if (priority == null){
        priority = 'info'
    }
    if (!$("#daflash").length){
        $("body").append('<div class="datopcenter dacol-centered col-sm-7 col-md-6 col-lg-5" id="daflash"></div>');
    }
    else{
        $("#daflash").empty();
    }
    var newMessage = $('<div class="alert alert-' + priority + ' daalert-interlocutory">' + message + '</div>');
    $("#daflash").append(newMessage);
    setTimeout(function(){
        if ($(newMessage).length > 0){
            $(newMessage).hide(300, function(){
                $(this).remove();
            });
        }
    }, 3000);
}

function fixServer(serverName) {
    var l = document.createElement("a");
    l.href = serverName;
    return l.origin;
}

function fixFullServer(serverName) {
    return serverName.replace(/\/$/, "");;
}

function fetchVarsEtc() {
    var action = Object();
    action.action = "fetchVarsEtc";
    action.file = daYAML;
    //console.log("fetchVarsEtc: getting " + daYAML);
    document.getElementById('server').contentWindow.postMessage(action, daServer);
}

function fetchFiles() {
    //console.log("Got to fetchFiles");
    var action = Object();
    action.action = "fetchFiles";
    document.getElementById('server').contentWindow.postMessage(action, daServer);
}

function receiveMessage(event) {
    //console.log("receiveMessage");
    //console.log("receiveMessage " + JSON.stringify(event.data));
    if (event.origin !== daServer) {
        //console.log("Message received from improper origin " + event.origin + ", which is not " + daServer);
        return;
    }
    //console.log("Received outer action " + event.data.action);
    if (event.data.action == 'initialize') {
        //console.log("Got to initialize");
        $("#variablesDiv").show();
        $("#iframeDiv").hide();
        daYAML = Cookies.get('daYAML');
        if (typeof daYAML == 'undefined') {
            daYAML = null;
        }
        if (daYAML == null) {
            fetchFiles();
        } else {
            fetchVarsEtc();
        }
        $("#daVariables").on('change', function () {
            if ($(this).val() != daYAML) {
                daYAML = $(this).val();
                Cookies.set('daYAML', daYAML, { expires: 999999 });
            }
            fetchVarsEtc();
        });
        if (!onDesktop) {
            $("#autocompletediv").show();
            $("#autocomplete").on('focus', function (event) {
                $(this).attr("size", 6);
            });
            $("#autocomplete").on('blur', function (event) {
                $(this).attr("size", 2);
            });
            $("#autocomplete").on('click', function (event) {
                event = event || window.event;
                event.preventDefault();
                if (event.stopPropagation) {
                    event.stopPropagation();
                } else {
                    event.cancelBubble = true;
                }
                if ("activeElement" in document) {
                    document.activeElement.blur();
                }
                $("#autocomplete option:selected").prop("selected", false);
                return false;
            });
            $("#autocomplete").on('change', function (event) {
                if ("activeElement" in document) {
                    document.activeElement.blur();
                }
                $("#autocomplete option:selected").prop("selected", false);
            });
            Office.context.document.addHandlerAsync(Office.EventType.DocumentSelectionChanged, SelectionChanged);
            //autocompleteInterval = setInterval(maybeUpdateAutocomplete, 3000);
        }
    } else if (event.data.action == 'files') {
        var pgYAML = $("#daVariables");
        pgYAML.empty();
        //var newOpt = $("<option></option>");
        //newOpt.val("");
        //newOpt.html("{{ word('-- Select a file --') }}");
        //newOpt.appendTo(pgYAML);
        var arr = Array();
        var n = event.data.files.length;
        //console.log("daYAML is " + daYAML + " and n is " + n);
        var need_to_fetch_vars;
        if (daYAML == null) {
            need_to_fetch_vars = true;
        } else {
            need_to_fetch_vars = false;
        }
        if (daYAML == null && n > 0) {
            //console.log("since null, set to first file");
            daYAML = event.data.files[0];
            Cookies.set('daYAML', daYAML, { expires: 999999 });
        }
        var found = false;
        for (var i = 0; i < n; i++) {
            //console.log("Considering " + event.data.files[i]);
            var newOpt = $("<option></option>");
            newOpt.val(event.data.files[i]);
            newOpt.html(event.data.files[i]);
            if (event.data.files[i] == daYAML) {
                newOpt.prop('selected', true);
                found = true;
            }
            newOpt.appendTo(pgYAML);
        }
        if (!found) {
            //console.log("file not found");
            if (n > 0) {
                //console.log("since not found, set to first file");
                daYAML = event.data.files[0];
                Cookies.set('daYAML', daYAML, { expires: 999999 });
                need_to_fetch_vars = true;
            } else if (daYAML != null) {
                daYAML = '';
                Cookies.set('daYAML', daYAML, { expires: 999999 });
            }
        }
        if (need_to_fetch_vars) {
            fetchVarsEtc();
        }
    } else if (event.data.action == 'varsetc') {
        //console.log("Got to varsetc.");
        if (event.data.uploaded && daUploadStatus != 'uploading'){
            console.log("Got varsetc message with uploaded when not uploading.  Ignoring.");
            return;
        }
        if (daYAML == null) {
            daYAML = '';
            Cookies.set('daYAML', daYAML, { expires: 999999 });
        } else {
            fetchFiles();
        }
        $("#daplaygroundtable").html(event.data.vars);
        daVocabDict = event.data.vocab_dict;
        daVocab = [];
        for (var name in daVocabDict){
            if (daVocabDict.hasOwnProperty(name)){
                daVocab.push(name);
            }
        }
        //daVocabLower = daVocab.map(x => x.toLowerCase());
        activateVariables();
        activatePopovers();
        $(".playground-variable").on("click", function (event) {
            event = event || window.event;
            //console.log("insert " + $(this).data("insert"));
            insertIntoWord($(this).data("insert"));
            event.preventDefault();
            if ("activeElement" in document) {
                document.activeElement.blur();
            }
            return false;
        });
        $("#uploadbutton").on('click', function(event){
            event.preventDefault();
            if (daUploadStatus != 'waiting'){
                $(this).blur();
                return false;
            }
            if (fileErrorTimeout != null){
                clearTimeout(fileErrorTimeout);
            }
            fileErrorTimeout = setTimeout(function () {
                $("#uploadbutton").show();
                $("#uploadbutton").blur();
                $("#uploadspinner").hide();
                flash(fileErrorMessage, 'danger');
            }, 10000);
            daUploadStatus = 'retrieving';
            uploadTemplateFile();
            $(this).hide();
            $("#uploadspinner").show();
            return false;            
        });
        if (event.data.uploaded){
            daUploadStatus = 'waiting';
            if (fileErrorTimeout != null){
                clearTimeout(fileErrorTimeout);
                fileErrorTimeout = null;
            }
            $("#uploadbutton").show();
            $("#uploadbutton").blur();
            $("#uploadspinner").hide();
            flash(fileSuccessMessage, "success");
        }
    }
}

function showIframe() {
    $("#server").attr('src', daFullServer + "/officeaddin?nm=1&project=" + currentProject);
    $("#iframeDiv").show();
}

function maybeUpdateAutocomplete() {
    if (Date.now() - lastCheckup > 1000) {
        //console.log("maybeUpdateAutocomplete: running");
        lastCheckup = Date.now();
        updateAutocomplete();
    } else {
        //console.log("maybeUpdateAutocomplete: skipped");
    }
}

function SelectionChanged(eventArgs) {
    maybeUpdateAutocomplete();
}

function arraysSame(a, b) {
    if (a.length !== b.length) {
        return false;
    }
    for (var i = a.length; i--;) {
        if (a[i] !== b[i]) {
            return false;
        }
    }
    return true;
}

Office.initialize = function (reason) {
    $(document).ready(function () {
        //console.log("Starting script during document ready");
        if (!Office.context.requirements.isSetSupported('WordApi', '1.3')) {
            onDesktop = true;
            //console.log("On desktop");
        } else {
            //console.log("On online");
        }
        window.addEventListener("message", receiveMessage, false);
        $("#serverConnect").on('click', function (event) {
            daFullServer = fixFullServer($("#daServer").val());
            daServer = fixServer($("#daServer").val());
            Cookies.set('daServer', daFullServer, { expires: 999999 });
            $("#daServerDiv").hide();
            $("#changeServerDiv").show();
            showIframe();
            event.preventDefault();
            return false;
        });
        $("#serverChange").on('click', function (event) {
            Cookies.remove('daServer');
            if (daServer){
                $("#daServer").val(daFullServer);
            }
            $("#daServerDiv").show();
            $("#iframeDiv").hide();
            $("#changeServerDiv").hide();
            $("#variablesDiv").hide();
            event.preventDefault();
            return false;
        });
        daFullServer = Cookies.get('daServer');
        if (!daFullServer) {
            if (defaultServer != null && defaultServer != "") {
                daFullServer = fixFullServer(defaultServer);
                daServer = fixServer(defaultServer);
                $("#changeServerDiv").show();
                showIframe();
            } else {
                $("#daServerDiv").show();
                $("#changeServerDiv").hide();
            }
        } else {
            daServer = fixServer(daFullServer);
            $("#changeServerDiv").show();
            showIframe();
        }
    });
};

function insertIntoWord(theText) {
    return Word.run(function (context) {
        var range = context.document.getSelection();
        range.insertText(theText, 'Replace');
        range.select();
        return context.sync();
    }).catch(function (error) {
        console.log('Error: ' + JSON.stringify(error));
        if (error instanceof OfficeExtension.Error) {
            console.log('Debug info: ' + JSON.stringify(error.debugInfo));
        }
    });
}

function autoCompleteWord(wordToInsert) {
    return Word.run(function (context) {
        var range = context.document.getSelection();
        var paragraphs = range.paragraphs;
        context.load(paragraphs, 'text');
        return context.sync().then(function () {
            var thePara = paragraphs.getFirstOrNullObject();
            if (thePara == null) {
                //console.log("paragraph is null");
            } else {
                var prevPart = range.getRange('End').expandTo(thePara.getRange('Start'));
                context.load(prevPart, 'text');
                return context.sync().then(function () {
                    var theText = prevPart.text;
                    var i = theText.length;
                    var wordStart = null;
                    var wordEnd = null;
                    while (--i > 0) {
                        if (wordEnd == null) {
                            if (theText[i].match(pythonVariableChar)) {
                                wordEnd = i + 1;
                            }
                        } else if (wordStart == null) {
                            if (!theText[i].match(pythonVariableChar)) {
                                wordStart = i + 1;
                                break;
                            }
                        }
                    }
                    var textToInsert;
                    if (wordStart != null && wordEnd != null && wordStart != wordEnd && wordEnd == theText.length) {
                        var theWord = theText.slice(wordStart, wordEnd);
                        //console.log("autoCompleteWord: word is " + theWord);
                        if (wordToInsert.startsWith(theWord)) {
                            textToInsert = wordToInsert.slice(theWord.length);
                        } else {
                            textToInsert = wordToInsert;
                        }
                    } else {
                        textToInsert = wordToInsert;
                    }
                    range.insertText(textToInsert, 'Replace');
                    range.select('End');
                    return context.sync();
                });
            }
        });
    }).catch(function (error) {
        console.log('Error: ' + JSON.stringify(error));
        if (error instanceof OfficeExtension.Error) {
            console.log('Debug info: ' + JSON.stringify(error.debugInfo));
        }
    });
}

function updateAutocomplete() {
    return Word.run(function (context) {
        //console.log("updateAutocomplete: starting");
        var range = context.document.getSelection();
        var paragraphs = range.paragraphs;
        paragraphs.load('text');
        return context.sync().then(function () {
            //console.log("updateAutocomplete: second part");
            var thePara = paragraphs.getFirstOrNullObject();
            if (thePara == null) {
                //console.log("paragraph is null");
            } else {
                //console.log("updateAutocomplete: calling expandto");
                var prevPart = range.getRange('End').expandTo(thePara.getRange('Start'));
                //console.log("updateAutocomplete: calling load");
                prevPart.load('text');
                //console.log("updateAutocomplete: called load");
                return context.sync().then(function () {
                    //console.log("updateAutocomplete: third part");
                    var theText = prevPart.text;
                    var i = theText.length;
                    var inJinja = false;
                    while (--i > 0) {
                        if (theText[i] == '}' && (theText[i - 1] == '}' || theText[i - 1] == '%')) {
                            break;
                        }
                        if ((theText[i] == '%' || theText[i] == '{') && theText[i - 1] == '{') {
                            inJinja = true;
                            break;
                        }
                    }
                    if (inJinja) {
                        i = theText.length;
                        var wordStart = null;
                        var wordEnd = null;
                        while (--i > 0) {
                            if (wordEnd == null) {
                                if (theText[i].match(pythonVariableChar)) {
                                    wordEnd = i + 1;
                                }
                            } else if (wordStart == null) {
                                if (!theText[i].match(pythonVariableChar)) {
                                    wordStart = i + 1;
                                    break;
                                }
                            }
                        }
                        if (wordStart != null && wordEnd != null && wordStart != wordEnd && wordEnd == theText.length) {
                            var theWord = theText.slice(wordStart, wordEnd);
                            //console.log("Checking word " + theWord);
                            var newAutoCompleteEntries = [];
                            var n = daVocab.length;
                            for (var i = 0; i < n; i++) {
                                if (daVocab[i].startsWith(theWord) && daVocab[i].length > 1) {
                                    newAutoCompleteEntries.push(daVocab[i]);
                                }
                            }
                            if (!arraysSame(autoCompleteEntries, newAutoCompleteEntries)) {
                                autoCompleteEntries = newAutoCompleteEntries;
                                var autoComplete = $("#autocomplete");
                                autoComplete.empty();
                                var n = autoCompleteEntries.length;
                                for (var i = 0; i < n; ++i) {
                                    var newOpt = $("<option></option>");
                                    newOpt.val(autoCompleteEntries[i]);
                                    newOpt.html(daVocabDict[autoCompleteEntries[i]]);
                                    newOpt.appendTo(autoComplete);
                                }
                                $("#autocomplete option").on('click', function (event) {
                                    event = event || window.event;
                                    event.preventDefault();
                                    if (event.stopPropagation) {
                                        event.stopPropagation();
                                    } else {
                                        event.cancelBubble = true;
                                    }
                                    //console.log("insert " + $(this).val());
                                    autoCompleteWord(daVocabDict[$(this).val()]);
                                    setTimeout(function() {
                                        $("#autocomplete option:selected").prop("selected", false);
                                        if ("activeElement" in document) {
                                            document.activeElement.blur();
                                        }
                                    }, 0);
                                    return false;
                                });
                            } else {
                                //console.log("No need to update.");
                            }
                        } else {
                            //console.log("No word detected.");
                            if (autoCompleteEntries.length > 0) {
                                $("#autocomplete").empty();
                                autoCompleteEntries = [];
                            }
                        }
                    } else {
                        if (autoCompleteEntries.length > 0) {
                            $("#autocomplete").empty();
                            autoCompleteEntries = [];
                        }
                    }
                });
            }
        });
    }).catch(function (error) {
        console.log('Error: ' + JSON.stringify(error));
        if (error instanceof OfficeExtension.Error) {
            console.log('Debug info: ' + JSON.stringify(error.debugInfo));
        }
    });
}

function getDocumentAsCompressed(successCallback) {
    Office.context.document.getFileAsync(Office.FileType.Compressed, { sliceSize: 65536 /*64 KB*/ }, 
                                         function (result) {
                                             if (result.status == "succeeded") {
                                                 var myFile = result.value;
                                                 var sliceCount = myFile.sliceCount;
                                                 var slicesReceived = 0, gotAllSlices = true, docdataSlices = [];
                                                 getSliceAsync(myFile, 0, sliceCount, gotAllSlices, docdataSlices, slicesReceived, successCallback);
                                             }
                                         });
}

function getSliceAsync(file, nextSlice, sliceCount, gotAllSlices, docdataSlices, slicesReceived, successCallback) {
    file.getSliceAsync(nextSlice, function (sliceResult) {
        if (sliceResult.status == "succeeded") {
            if (!gotAllSlices) {
                return;
            }
            docdataSlices[sliceResult.value.index] = sliceResult.value.data;
            if (++slicesReceived == sliceCount) {
                file.closeAsync();
                successCallback(docdataSlices);
            }
            else {
                getSliceAsync(file, ++nextSlice, sliceCount, gotAllSlices, docdataSlices, slicesReceived, successCallback);
            }
        }
        else {
            gotAllSlices = false;
            file.closeAsync();
        }
    });
}

function uploadTemplateFile() {
    return Word.run(function (context) {
        Office.context.document.getFilePropertiesAsync(function (asyncResult) {
            var fileName = asyncResult.value.url;
            //console.log("the raw fileName is " + fileName);
            fileName = fileName.replace(/.*[\/\\]/, '');
            fileName = fileName.replace(/\.docx\.docx/, '.docx');
            //console.log("the fileName is " + fileName);
            var action = Object();
            action.action = "uploadFile";
            action.yamlFile = daYAML;
            action.fileName = fileName;
            getDocumentAsCompressed(function(docdataSlices) {
                var docdata = [];
                for (var i = 0; i < docdataSlices.length; i++) {
                    docdata = docdata.concat(docdataSlices[i]);
                }

                var fileContent = new String();
                for (var j = 0; j < docdata.length; j++) {
                    fileContent += String.fromCharCode(docdata[j]);
                }
                action.content = 'data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,' + btoa(fileContent);
                if (daUploadStatus == 'retrieving'){
                    document.getElementById('server').contentWindow.postMessage(action, daServer);
                    daUploadStatus = 'uploading';
                }
            });
        });
        return context.sync();
    }).catch(function (error) {
        console.log('Error: ' + JSON.stringify(error));
        if (error instanceof OfficeExtension.Error) {
            console.log('Debug info: ' + JSON.stringify(error.debugInfo));
        }
    });
}
