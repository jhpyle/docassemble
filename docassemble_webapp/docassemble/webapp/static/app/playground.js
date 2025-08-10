// playground_page
var daCm;
var daAutoComp = [];
var exampleData;
var attrs_showing = Object();
var daExpireSession = null;
var vocab = [];
var attrs_showing = Object();

var $;

document.addEventListener("DOMContentLoaded", function () {
  if (typeof $ == "undefined") {
    $ = jQuery.noConflict();
  }
  $(document).ready(function () {
    switch (daPage) {
      case "questions":
        readyQuestionsPage();
        uploadListeners();
        readyVariables();
        break;
      case "files":
        readyFilesPage();
        readyVariables();
        break;
      case "package":
        readyPackagePage();
        uploadListeners();
        break;
    }
  });
});

Object.defineProperty(String.prototype, "daSprintf", {
  value: function () {
    var args = Array.from(arguments),
      i = 0;
    function defaultNumber(iValue) {
      return iValue != undefined && !isNaN(iValue) ? iValue : "0";
    }
    function defaultString(iValue) {
      return iValue == undefined ? "" : "" + iValue;
    }
    return this.replace(
      /%%|%([+\-])?([^1-9])?(\d+)?(\.\d+)?([deEfhHioQqs])/g,
      function (match, sign, filler, scale, precision, type) {
        var strOut, space, value;
        var asNumber = false;
        if (match == "%%") return "%";
        if (i >= args.length) return match;
        value = args[i];
        while (Array.isArray(value)) {
          args.splice(i, 1);
          for (var j = i; value.length > 0; j++)
            args.splice(j, 0, value.shift());
          value = args[i];
        }
        i++;
        if (filler == undefined) filler = " "; // default
        if (scale == undefined && !isNaN(filler)) {
          scale = filler;
          filler = " ";
        }
        if (sign == undefined) sign = "sqQ".indexOf(type) >= 0 ? "+" : "-"; // default
        if (scale == undefined) scale = 0; // default
        if (precision == undefined) precision = ".0"; // default
        scale = parseInt(scale);
        precision = parseInt(precision.substr(1));
        switch (type) {
          case "d":
          case "i":
            // decimal integer
            asNumber = true;
            strOut = parseInt(defaultNumber(value));
            if (precision > 0) strOut += "." + "0".repeat(precision);
            break;
          case "e":
          case "E":
            // float in exponential notation
            asNumber = true;
            strOut = parseFloat(defaultNumber(value));
            if (precision == 0) strOut = strOut.toExponential();
            else strOut = strOut.toExponential(precision);
            if (type == "E") strOut = strOut.replace("e", "E");
            break;
          case "f":
            // decimal float
            asNumber = true;
            strOut = parseFloat(defaultNumber(value));
            if (precision != 0) strOut = strOut.toFixed(precision);
            break;
          case "o":
          case "h":
          case "H":
            // Octal or Hexagesimal integer notation
            strOut =
              "\\" +
              (type == "o" ? "0" : type) +
              parseInt(defaultNumber(value)).toString(type == "o" ? 8 : 16);
            break;
          case "q":
            // single quoted string
            strOut = "'" + defaultString(value) + "'";
            break;
          case "Q":
            // double quoted string
            strOut = '"' + defaultString(value) + '"';
            break;
          default:
            // string
            strOut = defaultString(value);
            break;
        }
        if (typeof strOut != "string") strOut = "" + strOut;
        if ((space = strOut.length) < scale) {
          if (asNumber) {
            if (sign == "-") {
              if (strOut.indexOf("-") < 0)
                strOut = filler.repeat(scale - space) + strOut;
              else
                strOut =
                  "-" + filler.repeat(scale - space) + strOut.replace("-", "");
            } else {
              if (strOut.indexOf("-") < 0)
                strOut = "+" + filler.repeat(scale - space - 1) + strOut;
              else
                strOut =
                  "-" + filler.repeat(scale - space) + strOut.replace("-", "");
            }
          } else {
            if (sign == "-") strOut = filler.repeat(scale - space) + strOut;
            else strOut = strOut + filler.repeat(scale - space);
          }
        } else if (asNumber && sign == "+" && strOut.indexOf("-") < 0)
          strOut = "+" + strOut;
        return strOut;
      },
    );
  },
});

Object.defineProperty(window, "daSprintf", {
  value: function (str, ...rest) {
    if (typeof str == "string")
      return String.prototype.daSprintf.apply(str, rest);
    return "";
  },
});

function resetExpireSession() {
  if (daExpireSession != null) {
    window.clearTimeout(daExpireSession);
  }
  daExpireSession = setTimeout(function () {
    alert(daTranslations.sessionHasExpired);
  }, daSessionLifetimeSeconds);
}

function activateExample(id, scroll) {
  var info = exampleData[id];
  $("#da-example-source").html(info["html"]);
  $("#da-example-source-before").html(info["before_html"]);
  $("#da-example-source-after").html(info["after_html"]);
  $("#da-example-image-link").attr("href", info["interview"]);
  $("#da-example-image").attr("src", info["image"]);
  $("#da-example-image-dark").attr(
    "srcset",
    info["image"].replace("/examples/", "/examplesdark/"),
  );
  if (info["documentation"] != null) {
    $("#da-example-documentation-link").attr("href", info["documentation"]);
    $("#da-example-documentation-link").removeClass("da-example-hidden");
    //$("#da-example-documentation-link").slideUp();
  } else {
    $("#da-example-documentation-link").addClass("da-example-hidden");
    //$("#da-example-documentation-link").slideDown();
  }
  $(".da-example-list").addClass("da-example-hidden");
  $(".da-example-link").removeClass("da-example-active");
  $(".da-example-link").removeClass("active");
  $(".da-example-link").each(function () {
    if ($(this).data("example") == id) {
      $(this).addClass("da-example-active");
      $(this).addClass("active");
      $(this).parents(".da-example-list").removeClass("da-example-hidden");
      if (scroll) {
        setTimeout(function () {
          //console.log($(this).parents("li").last()[0].offsetTop);
          //console.log($(this).parents("li").last().parent()[0].offsetTop);
          $(".da-example-active")
            .parents("ul")
            .last()
            .scrollTop(
              $(".da-example-active").parents("li").last()[0].offsetTop,
            );
        }, 0);
      }
      //$(this).parents(".da-example-list").slideDown();
    }
  });
  $("#da-hide-full-example").addClass("dainvisible");
  if (info["has_context"]) {
    $("#da-show-full-example").removeClass("dainvisible");
  } else {
    $("#da-show-full-example").addClass("dainvisible");
  }
  $("#da-example-source-before").addClass("dainvisible");
  $("#da-example-source-after").addClass("dainvisible");
}

function saveCallback(data) {
  if (data.action && data.action == "reload") {
    location.reload(true);
  }
  if ($("#daflash").length) {
    $("#daflash").html(data.flash_message);
  } else {
    $("#damain").prepend(
      daSprintf(daNotificationContainer, data.flash_message),
    );
  }
  if (data.vocab_list != null) {
    vocab = data.vocab_list;
  }
  if (data.current_project != null) {
    currentProject = data.current_project;
  }
  history.replaceState(
    {},
    "",
    daUrlPlaygroundPage +
      encodeURI("?project=" + currentProject + "&file=" + currentFile),
  );
  $("#daVariables").val(data.active_file);
  $("#share-link").attr("href", data.active_interview_url);
  if (data.ac_list != null) {
    daAutoComp.length = 0;
    let n = data.ac_list.length;
    for (let i = 0; i < n; i++) {
      daAutoComp.push(data.ac_list[i]);
    }
  }
  if (data.variables_html != null) {
    $("#daplaygroundtable").html(data.variables_html);
    activateVariables();
    $("#form").trigger("reinitialize.areYouSure");
    var daPopoverTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="popover"]'),
    );
    var daPopoverList = daPopoverTriggerList.map(function (daPopoverTriggerEl) {
      return new bootstrap.Popover(daPopoverTriggerEl, {
        trigger: "click",
        html: true,
      });
    });
  }
  daConsoleMessages = data.console_messages;
  daShowConsoleMessages();
}

function daShowConsoleMessages() {
  for (i = 0; i < daConsoleMessages.length; ++i) {
    console.log(daConsoleMessages[i]);
  }
}

function disableButtonsUntilCallback() {
  $("button.dasubmitbutton").prop("disabled", true);
  $("a.dasubmitbutton").addClass("dadisabled");
}

function enableButtons() {
  $(".dasubmitbutton").prop("disabled", false);
  $("a.dasubmitbutton").removeClass("dadisabled");
}

function flash(message, priority) {
  if (priority == null) {
    priority = "info";
  }
  if (!$("#daflash").length) {
    $("body").append(daSprintf(daNotificationContainer, ""));
  }
  var newElement = $(daSprintf(daNotificationMessage, priority, message));
  $("#daflash").append(newElement);
  if (priority == "success") {
    setTimeout(function () {
      $(newElement).hide(300, function () {
        $(self).remove();
      });
    }, 3000);
  }
}

function uploadListeners() {
  $("#uploadlink").on("click", function (event) {
    $("#uploadlabel").click();
    event.preventDefault();
    return false;
  });
  $("#uploadlabel").on("click", function (event) {
    event.stopPropagation();
    event.preventDefault();
    $("#uploadfile").click();
    return false;
  });
  $("#uploadfile").on("click", function (event) {
    event.stopPropagation();
  });
  $("#uploadfile").on("change", function (event) {
    $("#fileform").submit();
  });
}

function readyQuestionsPage() {
  daCm = daNewEditor(
    $("#playground_content_container")[0],
    daContent,
    "yml",
    daKeymap,
    daWrapLines,
  );
  $("#daDelete").click(function (event) {
    if (
      originalFileName != $("#playground_name").val() ||
      $("#playground_name").val() == ""
    ) {
      $("#form button[name='submit']").click();
      event.preventDefault();
      return false;
    }
    if (!confirm(daTranslations.sureYouWantToDelete)) {
      event.preventDefault();
    }
  });
  $("#playground_content").val(daCm.state.doc.toString());
  $(daCm.dom).attr("tabindex", 70);
  $(daCm.dom).on("focus", function () {
    daCm.focus();
  });
  $(window).bind("beforeunload", function () {
    $("#playground_content").val(daCm.state.doc.toString());
    $("#form").trigger("checkform.areYouSure");
  });
  $("#form").areYouSure(daTranslations.unsavedChangesWarning);
  $("#form").bind("submit", function () {
    $("#playground_content").val(daCm.state.doc.toString());
    $("#form").trigger("reinitialize.areYouSure");
    return true;
  });
  $("#my-form").trigger("reinitialize.areYouSure");
  $("#daVariablesReport").on("shown.bs.modal", function () {
    daFetchVariableReport();
  });
  if (daEncodedExampleData) {
    exampleData = JSON.parse(atob(daEncodedExampleData[0]));
    activateExample(daEncodedExampleData[1], false);
    delete window.daEncodedExampleData;
  }
  variablesReady();
  resetExpireSession();
  $("#playground_name").on("change", function () {
    var newFileName = $(this).val();
    if (!isNew && newFileName == currentFile) {
      return;
    }
    for (var i = 0; i < existingFiles.length; i++) {
      if (
        newFileName == existingFiles[i] ||
        newFileName + ".yml" == existingFiles[i]
      ) {
        alert(daTranslations.fileExistWarning);
        return;
      }
    }
    return;
  });
  $("#share-link").click(function (event) {
    const shareLink = document.getElementById("share-link");
    const url = shareLink.getAttribute("href");
    const tempInput = document.createElement("input");
    tempInput.value = url;
    document.body.appendChild(tempInput);

    tempInput.select();
    tempInput.setSelectionRange(0, 99999);
    document.execCommand("copy");
    document.body.removeChild(tempInput);

    flash(daTranslations.linkCopiedClipboard, "success");
    event.preventDefault();
    return false;
  });
  $("#daRun").click(function (event) {
    if (
      originalFileName != $("#playground_name").val() ||
      $("#playground_name").val() == ""
    ) {
      $("#form button[name='submit']").click();
      event.preventDefault();
      return false;
    }
    $("#playground_content").val(daCm.state.doc.toString());
    disableButtonsUntilCallback();
    $.ajax({
      type: "POST",
      url: daUrlPlaygroundPageWithProject,
      data: $("#form").serialize() + "&run=Save+and+Run&ajax=1",
      success: function (data) {
        if (data.action && data.action == "reload") {
          location.reload(true);
        }
        enableButtons();
        resetExpireSession();
        saveCallback(data);
      },
      dataType: "json",
    });
    //event.preventDefault();
    return true;
  });
  var thisWindow = window;
  $("#daRunSyncGD").click(function (event) {
    $("#playground_content").val(daCm.state.doc.toString());
    $("#form").trigger("checkform.areYouSure");
    if (
      $("#form").hasClass("dirty") &&
      !confirm(daTranslations.unsavedChangesWarning)
    ) {
      event.preventDefault();
      return false;
    }
    if ($("#playground_name").val() == "") {
      $("#form button[name='submit']").click();
      event.preventDefault();
      return false;
    }
    setTimeout(function () {
      thisWindow.location.replace(daGoogleDriveSyncUrl);
    }, 100);
    return true;
  });
  $("#daRunSyncOD").click(function (event) {
    $("#playground_content").val(daCm.state.doc.toString());
    $("#form").trigger("checkform.areYouSure");
    if (
      $("#form").hasClass("dirty") &&
      !confirm(daTranslations.unsavedChangesWarning)
    ) {
      event.preventDefault();
      return false;
    }
    if ($("#playground_name").val() == "") {
      $("#form button[name='submit']").click();
      event.preventDefault();
      return false;
    }
    setTimeout(function () {
      thisWindow.location.replace(daOneDriveSyncUrl);
    }, 100);
    return true;
  });
  $("#form button[name='submit']").click(function (event) {
    $("#playground_content").val(daCm.state.doc.toString());
    if (
      validForm == false ||
      isNew == true ||
      originalFileName != $("#playground_name").val() ||
      $("#playground_name").val().trim() == ""
    ) {
      return true;
    }
    disableButtonsUntilCallback();
    $.ajax({
      type: "POST",
      url: daUrlPlaygroundPageWithProject,
      data: $("#form").serialize() + "&submit=Save&ajax=1",
      success: function (data) {
        if (data.action && data.action == "reload") {
          location.reload(true);
        }
        enableButtons();
        resetExpireSession();
        saveCallback(data);
        $("#daflash .alert-success").each(function () {
          var oThis = this;
          setTimeout(function () {
            $(oThis).hide(300, function () {
              $(self).remove();
            });
          }, 3000);
        });
      },
      dataType: "json",
    });
    event.preventDefault();
    return false;
  });

  $(".da-example-link").on("click", function () {
    var id = $(this).data("example");
    activateExample(id, false);
  });

  $(".da-example-copy").on("click", function (event) {
    if (daCm.state.selection.ranges.some((r) => !r.empty)) {
      daCm.dispatch(daCm.state.replaceSelection(""));
    }
    var id = $(".da-example-active").data("example");
    var curPos = daCm.state.selection.main.head;
    var notFound = 1;
    var curLine = daCm.state.doc.lineAt(curPos).number;
    let pos = 0;
    for (
      let lines = daCm.state.doc.iterLines((from = curLine));
      !lines.next().done && notFound;
      pos++
    ) {
      let { value } = lines;
      if (value.substring(0, 3) == "---" || value.substring(0, 3) == "...") {
        notFound = 0;
      }
    }
    let replacementText = "---\n" + exampleData[id]["source"] + "\n";
    var newPos;
    if (notFound) {
      newPos = daCm.state.doc.length;
      replacementText = "\n" + replacementText;
    } else {
      if (pos > 0) {
        pos--;
      }
      newPos = daCm.state.doc.line(curLine + pos).from;
    }
    daCm.dispatch({ selection: { anchor: newPos, head: newPos } });
    daCm.dispatch(daCm.state.replaceSelection(replacementText, "around"));
    daCm.focus();
    event.preventDefault();
    return false;
  });

  $(".da-example-heading").on("click", function () {
    var list = $(this).parent().children("ul").first();
    if (list != null) {
      if (!list.hasClass("da-example-hidden")) {
        return;
      }
      $(".da-example-list").addClass("da-example-hidden");
      //$(".da-example-list").slideUp();
      var new_link = $(this).parent().find("a.da-example-link").first();
      if (new_link.length) {
        var id = new_link.data("example");
        activateExample(id, true);
      }
    }
  });

  activatePopovers();

  $("#da-show-full-example").on("click", function () {
    var id = $(".da-example-active").data("example");
    var info = exampleData[id];
    $(this).addClass("dainvisible");
    $("#da-hide-full-example").removeClass("dainvisible");
    $("#da-example-source-before").removeClass("dainvisible");
    $("#da-example-source-after").removeClass("dainvisible");
  });

  $("#da-hide-full-example").on("click", function () {
    var id = $(".da-example-active").data("example");
    var info = exampleData[id];
    $(this).addClass("dainvisible");
    $("#da-show-full-example").removeClass("dainvisible");
    $("#da-example-source-before").addClass("dainvisible");
    $("#da-example-source-after").addClass("dainvisible");
  });
  if ($("#playground_name").val().length > 0) {
    daCm.focus();
    $("#form").trigger("reset");
  } else {
    $("#playground_name").focus();
  }
  $("#daflash .alert-success").each(function () {
    var oThis = this;
    setTimeout(function () {
      $(oThis).hide(300, function () {
        $(self).remove();
      });
    }, 3000);
  });

  activateVariables();
  updateRunLink();
  daShowConsoleMessages();
  if (currentFile != "") {
    history.replaceState(
      {},
      "",
      daUrlPlaygroundPage +
        encodeURI("?project=" + currentProject + "&file=" + currentFile),
    );
  }
}

// variables_js()

function activatePopovers() {
  var daPopoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]'),
  );
  var daPopoverList = daPopoverTriggerList.map(function (daPopoverTriggerEl) {
    return new bootstrap.Popover(daPopoverTriggerEl, {
      trigger: "click",
      html: true,
    });
  });
}

function activateVariables() {
  $(".daparenthetical").on("click", function (event) {
    var reference = $(this).data("ref");
    var target = $('[data-name="' + reference + '"]').first();
    if (target.length > 0) {
      $("#daplaygroundcard").animate(
        {
          scrollTop: target.parent().parent().position().top,
        },
        1000,
      );
    }
    event.preventDefault();
  });

  $(".dashowmethods").on("click", function (event) {
    var target_id = $(this).data("showhide");
    $("#" + target_id).slideToggle();
  });

  $(".dashowattributes").each(function () {
    var basename = $(this).data("name");
    if (attrs_showing.hasOwnProperty(basename)) {
      if (attrs_showing[basename]) {
        $('tr[data-parent="' + basename + '"]').show();
      }
    } else {
      attrs_showing[basename] = false;
    }
  });

  $(".dashowattributes").on("click", function (event) {
    var basename = $(this).data("name");
    attrs_showing[basename] = !attrs_showing[basename];
    $('tr[data-parent="' + basename + '"]').each(function () {
      $(this).toggle();
    });
  });
  $(".playground-variable").on("click", function (event) {
    daCm.dispatch(
      daCm.state.replaceSelection($(this).data("insert"), "around"),
    );
    daCm.focus();
  });
  $(".dasearchicon").on("click", function (event) {
    var query = $(this).data("name");
    if (query == null || query.length == 0) {
      daCm.dispatch({
        selection: { anchor: daCm.state.selection.main.head },
      });
      return;
    }
    daStartNewSearch(daCm, query);
    event.preventDefault();
    return false;
  });
}

function updateRunLink() {
  if (currentProject == "default") {
    $("#daRunButton").attr(
      "href",
      interviewBaseUrl.replace(":.yml", ":" + $("#daVariables").val()),
    );
    $("a.da-example-share").attr(
      "href",
      shareBaseUrl.replace(":.yml", ":" + $("#daVariables").val()),
    );
  } else {
    $("#daRunButton").attr(
      "href",
      interviewBaseUrl.replace(
        ":.yml",
        currentProject + ":" + $("#daVariables").val(),
      ),
    );
    $("a.da-example-share").attr(
      "href",
      shareBaseUrl.replace(
        ":.yml",
        currentProject + ":" + $("#daVariables").val(),
      ),
    );
  }
}

function fetchVars(changed) {
  $("#playground_content").val(daCm.state.doc.toString());
  updateRunLink();
  $.ajax({
    type: "POST",
    url: daUrlPlaygroundVariables + "?project=" + currentProject,
    data:
      "csrf_token=" +
      $("#form input[name='csrf_token']").val() +
      "&variablefile=" +
      $("#daVariables").val() +
      "&ajax=1&changed=" +
      (changed ? 1 : 0),
    success: function (data) {
      if (data.action && data.action == "reload") {
        location.reload(true);
      }
      if (data.vocab_list != null) {
        vocab = data.vocab_list;
      }
      if (data.current_project != null) {
        currentProject = data.current_project;
      }
      if (data.ac_list != null) {
        daAutoComp.length = 0;
        let n = data.ac_list.length;
        for (let i = 0; i < n; i++) {
          daAutoComp.push(data.ac_list[i]);
        }
      }
      if (data.variables_html != null) {
        $("#daplaygroundtable").html(data.variables_html);
        var daPopoverTriggerList = [].slice.call(
          document.querySelectorAll('[data-bs-toggle="popover"]'),
        );
        var daPopoverList = daPopoverTriggerList.map(
          function (daPopoverTriggerEl) {
            return new bootstrap.Popover(daPopoverTriggerEl, {
              trigger: "focus",
              html: true,
            });
          },
        );
        activateVariables();
      }
    },
    dataType: "json",
  });
  $("#daVariables").blur();
}

function variablesReady() {
  $("#daVariables").change(function (event) {
    fetchVars(true);
  });
}

function daFetchVariableReportCallback(data) {
  var modal = $("#daVariablesReport .modal-body");
  if (modal.length == 0) {
    console.log("No modal body on page");
    return;
  }
  if (!data.success) {
    $(modal).html("<p>" + daTranslations.failedToLoad + "</p>");
    return;
  }
  var yaml_file = data.yaml_file;
  modal.empty();
  var accordion = $("<div>");
  accordion.addClass("accordion");
  accordion.attr("id", "varsreport");
  var n = data.items.length;
  for (var i = 0; i < n; ++i) {
    var item = data.items[i];
    if (item.questions.length) {
      var accordionItem = $("<div>");
      accordionItem.addClass("accordion-item");
      var accordionItemHeader = $("<h2>");
      accordionItemHeader.addClass("accordion-header");
      accordionItemHeader.attr("id", "accordionItemheader" + i);
      accordionItemHeader.html(
        '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse' +
          i +
          '" aria-expanded="false" aria-controls="collapse' +
          i +
          '">' +
          item.name +
          "</button>",
      );
      accordionItem.append(accordionItemHeader);
      var collapse = $("<div>");
      collapse.attr("id", "collapse" + i);
      collapse.attr("aria-labelledby", "accordionItemheader" + i);
      collapse.data("bs-parent", "#varsreport");
      collapse.addClass("accordion-collapse");
      collapse.addClass("collapse");
      var accordionItemBody = $("<div>");
      accordionItemBody.addClass("accordion-body");
      var m = item.questions.length;
      for (var j = 0; j < m; j++) {
        var h5 = $("<h5>");
        h5.html(
          item.questions[j].usage.map((x) => daTranslations[x]).join(","),
        );
        var pre = $("<pre>");
        pre.html(item.questions[j].source_code);
        accordionItemBody.append(h5);
        accordionItemBody.append(pre);
        if (item.questions[j].yaml_file != yaml_file) {
          var p = $("<p>");
          p.html(daTranslations.from + " " + item.questions[j].yaml_file);
          accordionItemBody.append(p);
        }
      }
      collapse.append(accordionItemBody);
      accordionItem.append(collapse);
      accordion.append(accordionItem);
    }
  }
  modal.append(accordion);
}

function daFetchVariableReport(theFile = currentFile) {
  url = daVariablesReportUrl + "&file=" + theFile;
  $("#daVariablesReport .modal-body").html(
    "<p>" + daTranslations.loading + "</p>",
  );
  $.ajax({
    type: "GET",
    url: url,
    success: daFetchVariableReportCallback,
    xhrFields: {
      withCredentials: true,
    },
    error: function (xhr, status, error) {
      $("#daVariablesReport .modal-body").html(
        "<p>" + daTranslations.failedToLoad + "</p>",
      );
    },
  });
}

function readyVariables() {
  $(document).on("keydown", function (e) {
    if (e.which == 13) {
      var tag = $(document.activeElement).prop("tagName");
      if (tag == "INPUT") {
        e.preventDefault();
        e.stopPropagation();
        daCm.focus();
        return false;
      }
    }
  });
}

// files page

function saveCallbackFiles(data) {
  if (!data.success) {
    var n = data.errors.length;
    for (var i = 0; i < n; ++i) {
      $('input[name="' + data.errors[i].fieldName + '"]')
        .parents(".input-group")
        .addClass("da-group-has-error")
        .after(
          '<div class="da-has-error invalid-feedback">' +
            data.errors[i].err +
            "</div>",
        );
    }
    return;
  }
  $(".da-has-error").remove();
  $(".da-group-has-error").removeClass("da-group-has-error");
  fetchVars(true);
  if ($("#daflash").length) {
    $("#daflash").html(data.flash_message);
  } else {
    $("#damain").prepend(
      daSprintf(daNotificationContainer, data.flash_message),
    );
  }
}

function scrollBottom() {
  $("html, body").animate(
    {
      scrollTop: $("#editnav").offset().top - 53,
    },
    "slow",
  );
}

function readyFilesPage() {
  resetExpireSession();
  $("#file_name").on("change", function () {
    var newFileName = $(this).val();
    if (!isNew && newFileName == currentFile) {
      return;
    }
    for (var i = 0; i < existingFiles.length; i++) {
      if (newFileName == existingFiles[i]) {
        alert(daTranslations.fileExistWarning);
        return;
      }
    }
    return;
  });
  $("#dauploadbutton").click(function (event) {
    if ($("#uploadfile").val() == "") {
      event.preventDefault();
      return false;
    }
  });
  daCm = daNewEditor(
    $("#playground_content_container")[0],
    daContent,
    daMode,
    daKeymap,
    daWrapLines,
  );
  $(daCm.dom).attr("tabindex", 580);
  $(daCm.dom).on("focus", function () {
    daCm.focus();
  });
  if (daScroll) {
    if ($("#file_name").val().length > 0) {
      daCm.focus();
    } else {
      $("#file_name").focus();
    }
    scrollBottom();
  }
  $("#file_content").val(daCm.state.doc.toString());
  $(window).bind("beforeunload", function () {
    $("#file_content").val(daCm.state.doc.toString());
    $("#formtwo").trigger("checkform.areYouSure");
  });
  $("#daDelete").click(function (event) {
    if (!confirm(daTranslations.sureYouWantToDeleteFile)) {
      event.preventDefault();
    }
  });
  $("#formtwo").areYouSure({ message: daTranslations.unsavedChangesWarning });
  $("#formtwo").bind("submit", function (e) {
    $("#file_content").val(daCm.state.doc.toString());
    $("#formtwo").trigger("reinitialize.areYouSure");
    if (daSection != "modules" && !isNew) {
      var extraVariable = "";
      if ($("#daVariables").length) {
        extraVariable =
          "&active_file=" + encodeURIComponent($("#daVariables").val());
      }
      $.ajax({
        type: "POST",
        url: daUrlPlaygroundFiles,
        data: $("#formtwo").serialize() + extraVariable + "&submit=Save&ajax=1",
        success: function (data) {
          if (data.action && data.action == "reload") {
            location.reload(true);
          }
          resetExpireSession();
          saveCallbackFiles(data);
          $("#daflash .alert-success").each(function () {
            var oThis = this;
            setTimeout(function () {
              $(oThis).hide(300, function () {
                $(self).remove();
              });
            }, 3000);
          });
        },
        dataType: "json",
      });
      e.preventDefault();
      return false;
    }
    return true;
  });
  variablesReady();
  fetchVars(false);
  $("#uploadfile").on("change", function () {
    var fileName = $(this).val();
    fileName = fileName.replace(/.*\\/, "");
    fileName = fileName.replace(/.*\//, "");
    $(this).next(".custom-file-label").html(fileName);
  });
  $("#daVariablesReport").on("shown.bs.modal", function () {
    daFetchVariableReport($("#daVariables").val());
  });
}

// packages page

function scrollBottomPackagePage() {
  $("html, body").animate({ scrollTop: $(document).height() }, "slow");
}

function readyPackagePage() {
  if (daScroll) {
    scrollBottomPackagePage();
  }
  resetExpireSession();
  $("#file_name").on("change", function () {
    var newFileName = $(this).val();
    if (!isNew && newFileName == currentFile) {
      return;
    }
    for (var i = 0; i < existingFiles.length; i++) {
      if (newFileName == existingFiles[i]) {
        alert(daTranslations.packageExistsWarning);
        return;
      }
    }
    return;
  });
  $("#daDelete").click(function (event) {
    if (!confirm(daTranslations.sureDeletePackage)) {
      event.preventDefault();
    }
  });
  daCm = daNewEditor(
    $("#playground_content_container")[0],
    daContent,
    "yml",
    daKeymap,
    daWrapLines,
  );
  $(daCm.dom).attr("tabindex", 70);
  $(daCm.dom).on("focus", function () {
    daCm.focus();
  });
  $("#readme").val(daCm.state.doc.toString());
  $(daCm.dom).attr("id", "readme_content");
  $(window).bind("beforeunload", function () {
    $("#readme").val(daCm.state.doc.toString());
    $("#form").trigger("checkform.areYouSure");
  });
  $("#form").areYouSure(daTranslations.unsavedChangesWarning);
  $("#form").bind("submit", function () {
    $("#readme").val(daCm.state.doc.toString());
    $("#form").trigger("reinitialize.areYouSure");
    return true;
  });
  // extra_command goes here
  $("#daCancelPyPI").click(function (event) {
    var daWhichButton = this;
    $("#pypi_message_div").hide();
    $(".btn-da").each(function () {
      if (
        this != daWhichButton &&
        $(this).attr("id") != "daCancelGitHub" &&
        $(this).is(":hidden")
      ) {
        $(this).show();
      }
    });
    $("#daPyPI").html(daTranslations.pypi);
    $(this).hide();
    event.preventDefault();
    return false;
  });
  $("#daCancelGitHub").click(function (event) {
    var daWhichButton = this;
    $("#commit_message_div").hide();
    $(".btn-da").each(function () {
      if (
        this != daWhichButton &&
        $(this).attr("id") != "daCancelPyPI" &&
        $(this).is(":hidden")
      ) {
        $(this).show();
      }
    });
    $("#daGitHub").html(daTranslations.github);
    $(this).hide();
    event.preventDefault();
    return false;
  });
  if ($("#github_branch option").length == 0) {
    $("#github_branch_div").hide();
  }
  $("#github_branch").on("change", function (event) {
    if ($(this).val() == "<new>") {
      $("#new_branch_div").show();
    } else {
      $("#new_branch_div").hide();
    }
  });
  $("#daPyPI").click(function (event) {
    if (
      existingPypiVersion != null &&
      existingPypiVersion == $("#version").val()
    ) {
      alert(daTranslations.needToIncrement);
      $("html, body").animate({
        scrollTop: $("#version").offset().top - 90,
        scrollLeft: 0,
      });
      $("#version").focus();
      var tmpStr = $("#version").val();
      $("#version").val("");
      $("#version").val(tmpStr);
      event.preventDefault();
      return false;
    }
    var daWhichButton = this;
    if ($("#pypi_message_div").is(":hidden")) {
      $("#pypi_message_div").show();
      $(".btn-da").each(function () {
        if (this != daWhichButton && $(this).is(":visible")) {
          $(this).hide();
        }
      });
      $(this).html(daTranslations.publish);
      $("#daCancelPyPI").show();
      window.scrollTo(0, document.body.scrollHeight);
      event.preventDefault();
      return false;
    }
  });
  $("#daGitHub").click(function (event) {
    var daWhichButton = this;
    if (
      $("#commit_message").val().length == 0 ||
      $("#commit_message_div").is(":hidden")
    ) {
      if ($("#commit_message_div").is(":visible")) {
        $("#commit_message").addClass("is-invalid");
      } else {
        $("#commit_message_div").show();
        $(".btn-da").each(function () {
          if (this != daWhichButton && $(this).is(":visible")) {
            $(this).hide();
          }
        });
        $(this).html(daTranslations.commit);
        $("#daCancelGitHub").show();
      }
      $("#commit_message").focus();
      window.scrollTo(0, document.body.scrollHeight);
      event.preventDefault();
      return false;
    }
    if (
      $("#pypi_also").prop("checked") &&
      existingPypiVersion != null &&
      existingPypiVersion == $("#version").val()
    ) {
      alert(daTranslations.needToIncrement);
      $("html, body").animate({
        scrollTop: $("#version").offset().top - 90,
        scrollLeft: 0,
      });
      $("#version").focus();
      var tmpStr = $("#version").val();
      $("#version").val("");
      $("#version").val(tmpStr);
      event.preventDefault();
      return false;
    }
  });
  $(document).on("keydown", function (e) {
    if (e.which == 13) {
      var tag = $(document.activeElement).prop("tagName");
      if (
        tag != "TEXTAREA" &&
        tag != "A" &&
        tag != "LABEL" &&
        tag != "BUTTON"
      ) {
        e.preventDefault();
        e.stopPropagation();
      }
    }
  });
}
