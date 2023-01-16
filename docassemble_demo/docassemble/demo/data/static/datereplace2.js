$(document).on("daPageLoad", function () {
  $('input[type="date"]').each(function () {
    $(this).attr("type", "text");
  });
});
