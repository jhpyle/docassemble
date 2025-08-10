var daWhichButton = null;

document.addEventListener("DOMContentLoaded", () => {
  if (daAutoColorScheme) {
    var daDesiredColorScheme;
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      daDesiredColorScheme = 1;
    } else {
      daDesiredColorScheme = 0;
    }
    if (daCurrentColorScheme != daDesiredColorScheme) {
      document.documentElement.setAttribute(
        "data-bs-theme",
        daDesiredColorScheme ? "dark" : "light",
      );
      $.ajax({
        type: "PATCH",
        url: daUrlChangeColorScheme,
        xhrFields: {
          withCredentials: true,
        },
        data: "scheme=" + daDesiredColorScheme,
        success: function (data) {
          daCurrentColorScheme = data.scheme;
        },
        error: function (xhr, status, error) {
          console.log("Unable to change desired color scheme.");
        },
        dataType: "json",
      });
    }
  }
  $(document).ready(function () {
    if (daRequestPath == "/utilities") {
      $("#pdfdocxfile").on("change", function () {
        var fileName = $(this).val();
        fileName = fileName.replace(/.*\\/, "");
        fileName = fileName.replace(/.*\//, "");
        $(this).next(".custom-file-label").html(fileName);
      });
    }
    if (
      ["/user/sign-in", "/user/register", "/user/forgot-password"].includes(
        daRequestPath,
      )
    ) {
      $(".da-form-group input").first().focus();
    } else if (daRequestPath != "/playgroundfiles") {
      $(".form")
        .find("input[type=text],textarea,select")
        .filter(":visible:first")
        .focus();
    }
    setTimeout(function () {
      window.scrollTo(0, 1);
    }, 10);
    setTimeout(function () {
      $("#flash .alert-success").hide(300, function () {
        $(self).remove();
      });
    }, 3000);
    $(".btn-da").click(function () {
      daWhichButton = this;
    });
    $(".form").on("submit", function () {
      $(this)
        .find(".btn-da")
        .each(function () {
          var the_button = this;
          var disable_button = $(the_button).data("disable-button");
          if (typeof disable_button != "undefined" && !disable_button) {
            return;
          }
          setTimeout(function () {
            $(the_button).prop("disabled", true);
          }, 1);
          if (this != daWhichButton) {
            $(this).removeClass(
              daButtonStyle +
                "primary " +
                daButtonStyle +
                "info " +
                daButtonStyle +
                "warning " +
                daButtonStyle +
                "error " +
                daButtonStyle +
                "success",
            );
            $(this).addClass(daButtonStyle + "secondary");
          } else {
            $(daWhichButton).removeClass(
              daButtonStyle +
                "primary " +
                daButtonStyle +
                "info " +
                daButtonStyle +
                "warning " +
                daButtonStyle +
                "error " +
                daButtonStyle +
                "secondary",
            );
            $(daWhichButton).addClass(daButtonStyle + "success");
          }
        });
    });
    if (daRequestPath == "/interviews") {
      $(".dadeletebutton").on("click", function (event) {
        console.log("Doing click");
        var yamlFilename = $("<input>")
          .attr("type", "hidden")
          .attr("name", "i")
          .val($(this).data("i"));
        $("#daform").append($(yamlFilename));
        var session = $("<input>")
          .attr("type", "hidden")
          .attr("name", "session")
          .val($(this).data("session"));
        $("#daform").append($(session));
        return true;
      });
      $("#delete_all").on("click", function (event) {
        if (confirm(daAreYouSureDelete)) {
          return true;
        }
        event.preventDefault();
        return false;
      });
    }
  });
});
