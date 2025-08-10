if (daGlobalEval == undefined) {
  var daGlobalEval = eval;
  if (!String.prototype.daSprintf) {
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
                      "-" +
                      filler.repeat(scale - space) +
                      strOut.replace("-", "");
                } else {
                  if (strOut.indexOf("-") < 0)
                    strOut = "+" + filler.repeat(scale - space - 1) + strOut;
                  else
                    strOut =
                      "-" +
                      filler.repeat(scale - space) +
                      strOut.replace("-", "");
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
  }
  function flash(message, priority) {
    if (priority == null) {
      priority = "info";
    }
    if (!$("#daflash").length) {
      $("body").append(daNotificationContainer);
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
  var da_flash = flash;
  function daShowNotifications() {
    var n = daMessageLog.length;
    for (var i = 0; i < n; i++) {
      var message = daMessageLog[i];
      if (message.priority == "console") {
        console.log(message.message);
      } else if (message.priority == "javascript") {
        daGlobalEval(message.message);
      } else if (
        message.priority == "success" ||
        message.priority == "warning" ||
        message.priority == "danger" ||
        message.priority == "secondary" ||
        message.priority == "tertiary" ||
        message.priority == "info" ||
        message.priority == "dark" ||
        message.priority == "light" ||
        message.priority == "primary"
      ) {
        da_flash(message.message, message.priority);
      } else {
        da_flash(message.message, "info");
      }
    }
  }
}
document.addEventListener("DOMContentLoaded", function () {
  $(document).ready(function () {
    $("#da-retry").on("click", function (e) {
      location.reload();
      e.preventDefault();
      return false;
    });
    daShowNotifications();
    $(document).trigger("daPageError");
  });
});
