/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

//import * as OfficeHelpers from '@microsoft/office-js-helpers';

var serverName = '';
var theVars;
var theVocab;
function receiveMessage(event)
{
  if (event.origin !== serverName){
    console.log("Message received from improper origin.")
    return;
  }
  console.log("Received action " + event.data.action);
  if (event.data.action == 'initialize'){
    $("#server").hide();
    $("#app-body").show();
    fetchFiles();
  }
  if (event.data.action == 'files'){
    var theSelection = $("#interviewName").val();
    $("#interviewName").empty();
    var firstOption = $("<option>");
    firstOption.text("Select an interview...");
    $("#interviewName").append(firstOption);
    var n = event.data.files.length;
    for (var i = 0; i < n; i++){
      var newOption = $("<option>");
      newOption.attr('value', event.data.files[i]);
      newOption.text(event.data.files[i]);
      if (event.data.files[i] == theSelection){
	newOption.prop('selected', true);
      }
      $("#interviewName").append(newOption);
    }
  }
  if (event.data.action == 'vars'){
    theVars = event.data.vars;
    theVocab = event.data.vocab;
    fetchFiles();
  }
}

function testServer(){
  $("#server")[0].contentWindow.postMessage({"action": "test"}, serverName);
}

function fetchFiles(){
  $("#server")[0].contentWindow.postMessage({"action": "fetchFiles"}, serverName);
}

function fetchVars(yamlFile){
  $("#server")[0].contentWindow.postMessage({"action": "fetchVars", "file": yamlFile}, serverName);
}

function validateUrl(value) {
  return /^https?:\/\/\S/i.test(value);
}

Office.initialize = (reason) => {
  $( document ).ready(function() {
    $('#sideload-msg').hide();
    try {
      var doc = document.getElementById('server').contentWindow.document;
      doc.open();
      doc.write('<html><head><title></title></head><body>Loading...</body></html>');
      doc.close();
    }
    catch(err) {
      console.log(err.message);
    }
    $("#app-body").hide();
    $("#serverSet").on('click', function(){
      if (!validateUrl($("#serverName").val())){
	$("#serverNameError").show();
	return false;
      }
      $("#serverNameError").hide();
      $("#serverNameDiv").hide();
      serverName = $("#serverName").val();
      Cookies.set('serverName', serverName, { expires: 999999 });
      $("#server").show();
      $("#server").attr('src', serverName + '/officeaddin');
      $("#server").attr('height', 1200);
      $("#server").height("1200px");
      return false;
    });
    window.addEventListener("message", receiveMessage, false);
    serverName = Cookies.get('serverName');
    if (serverName){
      $("#serverNameDiv").hide();
      $("#server").show();
      $("#server").attr('src', serverName + '/officeaddin');
      $("#server").attr('height', 1200);
      $("#server").height("1200px");
    }
    $('#ifPara').click(ifPara);
    $('#ifInline').click(ifInline);
    $('#listPara').click(listPara);
    $('#insertTemplate').click(insertTemplate);
    $('#commentPara').click(commentPara);
    $('#insertVariable').click(insertVariable);
    $("#interviewName").on('change', function(event){
      var newYaml = $("#interviewName").val();
      if (newYaml){
	console.log("YAML is now " + newYaml);
	fetchVars(newYaml);
      }
      else{
	console.log("YAML was blank");
      }
    });
  });
};

// Initialize FabricJS components
var DropdownHTMLElements = document.querySelectorAll('.ms-Dropdown');
for (var i = 0; i < DropdownHTMLElements.length; ++i) {
  var Dropdown = new fabric['Dropdown'](DropdownHTMLElements[i]);
}
var CheckBoxElements = document.querySelectorAll('.ms-CheckBox');
for (var i = 0; i < CheckBoxElements.length; i++) {
  new fabric['CheckBox'](CheckBoxElements[i]);
}
var TextFieldElements = document.querySelectorAll(".ms-TextField");
for (var i = 0; i < TextFieldElements.length; i++) {
  new fabric['TextField'](TextFieldElements[i]);
}
var ChoiceFieldGroupElements = document.querySelectorAll(".ms-ChoiceFieldGroup");
for (var i = 0; i < ChoiceFieldGroupElements.length; i++) {
  new fabric['ChoiceFieldGroup'](ChoiceFieldGroupElements[i]);
}
var CommandButtonElements = document.querySelectorAll(".ms-CommandButton");
for (var i = 0; i < CommandButtonElements.length; i++) {
  new fabric['CommandButton'](CommandButtonElements[i]);
}

////////////////////////////////////////////////////////////////
// Docassemble code actions
async function insertVariable() {
    return Word.run(async context => {
        const range = context.document.getSelection();

        var variableName = document.getElementById('inputVariableName').value;
        //checkboxVariableReplaceAll
        var variableReplaceAll = document.getElementById('checkboxVariableReplaceAll').checked;
        var variableFormat = document.getElementById('selectVariableFormat').value;


        if (variableFormat == "") {
            var textToInsert = variableName;
        } else {
            var textToInsert = variableFormat + '(' + variableName + ')';
        }

        range.load('text');

        if (! variableReplaceAll) {
            range.insertText('{{ ' + variableName + ' }}','Replace');
        } else {
            await context.sync();
            var textToReplace = range.text;

            // FIXME: We need to ignore Jinja statements and expressions -- search looks inside them now
            var results = context.document.body.search(textToReplace.trim(), {matchWholeWord: true}); // Word Online seems to select spaces next to a word you double-click on
            context.load(results);
            
            await context.sync();

            for (var i = 0; i < results.items.length; i++) {
                results.items[i].insertText('{{ ' + textToInsert + ' }}', "Replace");
            }
        }

        await context.sync();
    });
}

async function ifPara() {
    return Word.run(async context => {
            const range = context.document.getSelection();
            var ifExpression = document.getElementById('inputIfExpression').value;

            // Read the range text
            range.load('text');
            var textBefore = '{%p if ' + ifExpression + ' %}';

            range.insertParagraph(textBefore,'Before');
            range.insertParagraph('{%p endif %}','After');

            await context.sync();
            console.log(`The selected text was ${range.text}.`);
        });
}

async function ifInline() {
    return Word.run(async context => {
            const range = context.document.getSelection();
            var ifExpression = document.getElementById('inputIfExpression').value;
            var textBefore = '{% if ' + ifExpression + ' %}';

            // Read the range text
            range.load('text');

            range.insertText(textBefore,'Before');
            range.insertText('{% endif %}','After');

            await context.sync();
            console.log(`The selected text was ${range.text}.`);
        });
}

async function listPara() {
    return Word.run(async context => {
            const range = context.document.getSelection();
            var listVariableName = document.getElementById('inputListVariableName').value;
            var onlyTrue = document.getElementById('checkboxOnlyTrue').checked;
            if (onlyTrue) {
                var textBefore = '{%p for item in ' + listVariableName + '.true_values() %}'; 
            } else {
                var textBefore = '{%p for item in ' + listVariableName + '%}'; 
            }
            // Read the range text
            range.load('text');
            range.insertText('{{ item }}','Replace');
            range.insertParagraph(textBefore,'Before');
            range.insertParagraph('{%p endfor %}','After');

            await context.sync();
            console.log(`The selected text was ${range.text}.`);
        });
}

async function commentPara() {
    return Word.run(async context => {
        const range = context.document.getSelection();
            
        // Read the range text
        range.load('text');
        await context.sync(); // Guess this has a performance penalty?
        
        // Regexp with 3 groups: {# , text between comments, #}. We match both whitespace and non-whitespace, including newlines
        var re = new RegExp('({#)([\\s\\S]*)(#})');
        var matches = re.exec(range.text);

        if (matches) { // index 1 is the uncommented string
            // This is not correct as it removes formatting from the text
            // This sample looks like it shows how to do it correctly: https://github.com/OfficeDev/Word-Add-in-JS-SpecKit/blob/master/scripts/boilerplate.js in addBoilerplateParagraph
            // we should use var paragraphs = context.document.getSelection().paragraphs; and then loop through paragraph collection
            range.insertText(matches[2],'Replace'); 
            console.log('Removed comments.')
        } else {
            range.insertParagraph('{#','Before');
            range.insertParagraph('#}','After');
            console.log('Added comments.')
            // we should extend the selection to include the newly added text
        }
        await context.sync();
    });
}

async function insertTemplate() {
    return Word.run(async context => {
        const range = context.document.getSelection();
        var templateName = document.getElementById('inputTemplateName').value;
 
        var templateOptions = document.getElementById('inputTemplateOptions').value;
        if (templateOptions == "") {
            var textBefore = '{{p include_docx_template("' + templateName + '") }}'; 
        } else {
            var textBefore = '{{p include_docx_template("' + templateName + '", ' + templateOptions + ') }}'; 
        }

        // Read the range text
        range.load('text');
        
        range.insertText(textBefore,'Replace');
        
        await context.sync();
        console.log(`The selected text was ${range.text}.`);
    });
}

/////////////////////////////////////////////////////////////////////
// Helper functions

// File handling
function getDocumentAsCompressed() {
    Office.context.document.getFileAsync(Office.FileType.Compressed, {  }, 
        function (result) {
            if (result.status == "succeeded") {
            // If the getFileAsync call succeeded, then
            // result.value will return a valid File Object.
            var myFile = result.value;
            var sliceCount = myFile.sliceCount;
            var slicesReceived = 0, gotAllSlices = true, docdataSlices = [];
            app.showNotification("File size:" + myFile.size + " #Slices: " + sliceCount);

            // Get the file slices.
            getSliceAsync(myFile, 0, sliceCount, gotAllSlices, docdataSlices, slicesReceived);
            }
            else {
            app.showNotification("Error:", result.error.message);
            }
    });
}

function getSliceAsync(file, nextSlice, sliceCount, gotAllSlices, docdataSlices, slicesReceived) {
    file.getSliceAsync(nextSlice, function (sliceResult) {
        if (sliceResult.status == "succeeded") {
            if (!gotAllSlices) { // Failed to get all slices, no need to continue.
                return;
            }

            // Got one slice, store it in a temporary array.
            // (Or you can do something else, such as
            // send it to a third-party server.)
            docdataSlices[sliceResult.value.index] = sliceResult.value.data;
            if (++slicesReceived == sliceCount) {
               // All slices have been received.
               file.closeAsync();
               onGotAllSlices(docdataSlices);
            }
            else {
                getSliceAsync(file, ++nextSlice, sliceCount, gotAllSlices, docdataSlices, slicesReceived);
            }
        }
            else {
                gotAllSlices = false;
                file.closeAsync();
                app.showNotification("getSliceAsync Error:", sliceResult.error.message);
            }
    });
}

function onGotAllSlices(docdataSlices) {
    var docdata = [];
    for (var i = 0; i < docdataSlices.length; i++) {
        docdata = docdata.concat(docdataSlices[i]);
    }

    var fileContent = new String();
    for (var j = 0; j < docdata.length; j++) {
        fileContent += String.fromCharCode(docdata[j]);
    }

    // Now all the file content is stored in 'fileContent' variable,
    // you can do something with it, such as print, fax...
}
