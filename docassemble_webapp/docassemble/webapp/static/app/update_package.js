var default_branch;
function get_branches() {
  var elem = $("#gitbranch");
  elem.empty();
  var opt = $("<option></option>");
  opt.attr("value", "").text("Not applicable");
  elem.append(opt);
  var github_url = $("#giturl").val();
  if (!github_url) {
    return;
  }
  $.get(daGetGitBranches, { url: github_url }, "json").done(function (data) {
    //console.log(data);
    if (data.success) {
      var n = data.result.length;
      if (n > 0) {
        var default_to_use = default_branch;
        var to_try = [default_branch, daGithubBranch, "master", "main"];
        outer: for (var j = 0; j < 4; j++) {
          for (var i = 0; i < n; i++) {
            if (data.result[i].name == to_try[j]) {
              default_to_use = to_try[j];
              break outer;
            }
          }
        }
        elem.empty();
        for (var i = 0; i < n; i++) {
          opt = $("<option></option>");
          opt.attr("value", data.result[i].name).text(data.result[i].name);
          if (data.result[i].name == default_to_use) {
            opt.prop("selected", true);
          }
          $(elem).append(opt);
        }
      }
    }
  });
}
document.addEventListener("DOMContentLoaded", function () {
  $(document).ready(function () {
    default_branch = daDefaultBranch;
    get_branches();
    $("#giturl").on("change", get_branches);
    $("#zipfile").on("change", function () {
      var fileName = $(this).val();
      fileName = fileName.replace(/.*\\/, "");
      fileName = fileName.replace(/.*\//, "");
      $(this).next(".custom-file-label").html(fileName);
    });
  });
});
