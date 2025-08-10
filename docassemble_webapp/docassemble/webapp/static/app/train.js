document.addEventListener("DOMContentLoaded", function () {
  $(document).ready(function () {
    $("#showimport").click(function (e) {
      $("#showimport").hide();
      $("#hideimport").show();
      $("#importcontrols").show("fast");
      e.preventDefault();
      return false;
    });
    $("#hideimport").click(function (e) {
      $("#showimport").show();
      $("#hideimport").hide();
      $("#importcontrols").hide("fast");
      e.preventDefault();
      return false;
    });
    $("input[type=radio][name=usepackage]").on("change", function (e) {
      if ($(this).val() == "no") {
        $("#uploadinput").show();
      } else {
        $("#uploadinput").hide();
      }
      e.preventDefault();
      return false;
    });
    $("button.prediction").click(function () {
      if (!$("#dependent" + $(this).data("id-number")).prop("disabled")) {
        $("#dependent" + $(this).data("id-number")).val(
          $(this).data("prediction"),
        );
      }
    });
    $("select.trainer").change(function () {
      var the_number = $(this).data("id-number");
      if (the_number == "newdependent") {
        $("#newdependent").val($(this).val());
      } else {
        $("#dependent" + the_number).val($(this).val());
      }
    });
    $("div.dadelete-observation input").change(function () {
      var the_number = $(this).data("id-number");
      if ($(this).is(":checked")) {
        $("#dependent" + the_number).prop("disabled", true);
        $("#selector" + the_number).prop("disabled", true);
      } else {
        $("#dependent" + the_number).prop("disabled", false);
        $("#selector" + the_number).prop("disabled", false);
      }
    });
  });
});
