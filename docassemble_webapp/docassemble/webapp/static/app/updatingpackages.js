var daCheckinInterval = null;
var resultsAreIn = false;
var pollDelay = 0;
var pollFail = 0;
var pollPending = false;
function daRestartCallback(data) {
  //console.log("Restart result: " + data.success);
}
function daRestart() {
  $.ajax({
    type: "POST",
    url: daRestartAjax,
    data: "csrf_token=" + daCsrf + "&action=restart",
    success: daRestartCallback,
    dataType: "json",
  });
  return true;
}
function daBadCallback(data) {
  pollPending = false;
  pollFail += 1;
}
function daUpdateCallback(data) {
  pollPending = false;
  if (data.success) {
    if (data.status == "finished") {
      resultsAreIn = true;
      if (data.ok) {
        $("#notification").html(daNoError);
        $("#notification").removeClass("alert-info");
        $("#notification").removeClass("alert-danger");
        $("#notification").addClass("alert-success");
      } else {
        $("#notification").html(daErrorWithLog);
        $("#notification").removeClass("alert-info");
        $("#notification").removeClass("alert-success");
        $("#notification").addClass("alert-danger");
      }
      $("#resultsContainer").show();
      $("#resultsArea").html(data.summary);
      if (daCheckinInterval != null) {
        clearInterval(daCheckinInterval);
      }
      //daRestart();
    } else if (data.status == "failed" && !resultsAreIn) {
      resultsAreIn = true;
      $("#notification").html(daUpdateError);
      $("#notification").removeClass("alert-info");
      $("#notification").removeClass("alert-success");
      $("#notification").addClass("alert-danger");
      $("#resultsContainer").show();
      if (data.error_message) {
        $("#resultsArea").html(data.error_message);
      } else if (data.summary) {
        $("#resultsArea").html(data.summary);
      }
      if (daCheckinInterval != null) {
        clearInterval(daCheckinInterval);
      }
    }
  } else if (!resultsAreIn) {
    $("#notification").html(daGeneralError);
    $("#notification").removeClass("alert-info");
    $("#notification").removeClass("alert-success");
    $("#notification").addClass("alert-danger");
    if (daCheckinInterval != null) {
      clearInterval(daCheckinInterval);
    }
  }
}
function daUpdate() {
  if (pollDelay > 50 || pollFail > 16) {
    $("#notification").html(daServerDidNotRespond);
    $("#notification").removeClass("alert-info");
    $("#notification").removeClass("alert-success");
    $("#notification").addClass("alert-danger");
    if (daCheckinInterval != null) {
      clearInterval(daCheckinInterval);
    }
    return;
  }
  if (pollPending) {
    pollDelay += 1;
    return;
  }
  if (resultsAreIn) {
    return;
  }
  pollDelay = 0;
  pollPending = true;
  $.ajax({
    type: "POST",
    url: daUrlUpdatePackageAjax,
    data: "csrf_token=" + daCsrf,
    success: daUpdateCallback,
    error: daBadCallback,
    timeout: 2000,
    dataType: "json",
  });
  return true;
}
document.addEventListener("DOMContentLoaded", function () {
  $(document).ready(function () {
    daCheckinInterval = setInterval(daUpdate, 6000);
  });
});
