if (typeof $ == "undefined") {
  var $ = jQuery.noConflict();
}
var daCtx,
  daColor = "#000";

var daTheWidth;
var daAspectRatio;
var daTheBorders;
var daWaiter;
var daWaitLimit;
var daIsEmpty;

function daInitializeSignature() {
  daAspectRatio = 0.4;
  daTheBorders = 30;
  daWaiter = 0;
  daWaitLimit = 2;
  daIsEmpty = 1;
  setTimeout(function () {
    if (!isCanvasSupported()) {
      daPost({ da_success: 0, da_ajax: 1 });
    }
    daNewCanvas();
    $(document).on("touchmove", function (event) {
      event.preventDefault();
    });
  }, 500);
  $(window).on("resize", function () {
    daResizeCanvas();
  });
  $(window).on("orientationchange", function () {
    daResizeCanvas();
  });

  // $(".dasigpalette").click(function(){
  //   $(".dasigpalette").css("border-color", "#777");
  //   $(".dasigpalette").css("border-style", "solid");
  //   $(this).css("border-color", "#fff");
  //   $(this).css("border-style", "dashed");
  //   daColor = $(this).css("background-color");
  //   daCtx.beginPath();
  //   daCtx.lineJoin="round";
  //   daCtx.strokeStyle = daColor;
  //   daCtx.fillStyle = daColor;
  // });
  $(".dasigclear").click(function (e) {
    e.preventDefault();
    daNewCanvas();
    return false;
  });
  $(".dasigsave").click(function (e) {
    e.preventDefault();
    if (daIsEmpty && document.getElementById("da_sig_required").value == "1") {
      $("#daerrormess").removeClass("dasignotshowing");
      setTimeout(function () {
        $("#daerrormess").addClass("dasignotshowing");
      }, 3000);
    } else {
      $(".dasigclear").attr("disabled", true);
      $(".dasigsave").attr("disabled", true);
      daSaveCanvas();
    }
    return false;
  });
}

// function to setup a new canvas for drawing

function daResizeCanvas() {
  //var cheight = $(window).height()-($("#sigheader").height() + $("#sigtoppart").height() + $("#sigbottompart").height());
  setTimeout(function () {
    daNewCanvas();
  }, 200);
  //console.log("I resized");
  return;
  // var cheight = $(window).width()*daAspectRatio;
  // if (cheight > $(window).height()-theTop){
  //   cheight = $(window).height()-theTop;
  // }
  // if (cheight > 350){
  //   cheight = 350;
  // }
  // var cwidth = $(window).width() - daTheBorders;

  // $("#sigcontent").height(cheight);
  // //$("#sigcontent").css('top', ($("#sigheader").height() + $("#sigtoppart").height()) + "px");
  // //$("#sigbottompart").css('top', (cheight) + "px");
  // $("#sigcanvas").width(cwidth);
  // $("#sigcanvas").height(cheight);
  // theTop = $("#sigcanvas").offset().top;
  // theLeft = $("#sigcanvas").offset().left;
  // daTheWidth = cwidth/100.0;
  // if (daTheWidth < 1){
  //   daTheWidth = 1;
  // }
  // return;
}

function daSaveCanvas() {
  var dataURL = document.getElementById("dasigcanvas").toDataURL();
  //console.log(dataURL)
  daSpinnerTimeout = setTimeout(daShowSpinner, 1000);
  daPost({ da_success: 1, da_the_image: dataURL, da_ajax: 1 });
}

function daNewCanvas() {
  //console.log("running daNewCanvas");
  var cwidth = $(window).width() - daTheBorders;
  var contentwidth = $("#dasigpage").outerWidth(true);
  if (cwidth > contentwidth) {
    cwidth = contentwidth;
  }
  var cheight = cwidth * daAspectRatio;
  var otherHeights =
    $("#dasigheader").outerHeight(true) +
    $("#dasigtoppart").outerHeight(true) +
    $("#dasigmidpart").outerHeight(true) +
    $("#dasigbottompart").outerHeight(true);
  //console.log("height is " + $(window).height());
  //console.log("otherHeights are " + otherHeights);
  if (cheight > $(window).height() - otherHeights) {
    cheight = $(window).height() - otherHeights;
  }
  if (cheight > 275) {
    cheight = 275;
  }
  $("#dasigcontent").height(cheight);
  var canvas =
    '<canvas id="dasigcanvas" width="' +
    cwidth +
    'px" height="' +
    cheight +
    'px"></canvas>';
  $("#dasigcontent").html(canvas);
  //theTop = $("#sigcanvas").offset().top;
  //theLeft = $("#sigcanvas").offset().left;
  daTheWidth = cwidth / 100.0;
  if (daTheWidth < 1) {
    daTheWidth = 1;
  }

  // setup canvas
  // daCtx=document.getElementById("sigcanvas").getContext("2d");
  $("#dasigcanvas").each(function () {
    daCtx = $(this)[0].getContext("2d");
    daCtx.strokeStyle = daColor;
    daCtx.lineWidth = daTheWidth;
  });

  // setup to trigger drawing on mouse or touch
  $("#dasigcanvas").drawTouch();
  $("#dasigcanvas").drawPointer();
  $("#dasigcanvas").drawMouse();
  //$(document).on("touchend", function(event){event.preventDefault();});
  //$(document).on("touchcancel", function(event){event.preventDefault();});
  //$(document).on("touchstart", function(event){event.preventDefault();});
  //$("meta[name=viewport]").attr('content', "width=device-width, minimum-scale=1.0, maximum-scale=1.0, initial-scale=1.0, user-scalable=0");
  daIsEmpty = 1;
  setTimeout(function () {
    if (daJsEmbed) {
      $(daTargetDiv)[0].scrollTo(0, 1);
      if (daSteps > 1) {
        $(daTargetDiv)[0].scrollIntoView();
      }
    } else {
      window.scrollTo(0, 1);
    }
  }, 10);
}

// prototype to	start drawing on touch using canvas moveTo and lineTo
$.fn.drawTouch = function () {
  var start = function (e) {
    e = e.originalEvent;
    x = e.changedTouches[0].pageX - $("#dasigcanvas").offset().left;
    y = e.changedTouches[0].pageY - $("#dasigcanvas").offset().top;
    daCtx.beginPath();
    daCtx.arc(x, y, 0.5 * daTheWidth, 0, 2 * Math.PI);
    daCtx.fill();
    daCtx.beginPath();
    daCtx.lineJoin = "round";
    daCtx.moveTo(x, y);
    if (daIsEmpty) {
      $(".dasigsave").prop("disabled", false);
      daIsEmpty = 0;
    }
  };
  var move = function (e) {
    e.preventDefault();
    if (daWaiter % daWaitLimit == 0) {
      e = e.originalEvent;
      x = e.changedTouches[0].pageX - $("#dasigcanvas").offset().left;
      y = e.changedTouches[0].pageY - $("#dasigcanvas").offset().top;
      daCtx.lineTo(x, y);
      daCtx.stroke();
      if (daIsEmpty) {
        daIsEmpty = 0;
      }
    }
    daWaiter++;
    //daCtx.fillRect(x-0.5*daTheWidth,y-0.5*daTheWidth,daTheWidth,daTheWidth);
    //daCtx.beginPath();
    //daCtx.arc(x, y, 0.5*daTheWidth, 0, 2*Math.PI);
    //daCtx.fill();
  };
  var moveline = function (e) {
    daWaiter = 0;
    move(e);
  };
  var dot = function (e) {
    e.preventDefault();
    e = e.originalEvent;
    daCtx.lineJoin = "round";
    x = e.pageX - $("#dasigcanvas").offset().left;
    y = e.pageY - $("#dasigcanvas").offset().top;
    daCtx.beginPath();
    daCtx.arc(x, y, 0.5 * daTheWidth, 0, 2 * Math.PI);
    daCtx.fill();
    daCtx.moveTo(x, y);
    if (daIsEmpty) {
      daIsEmpty = 0;
    }
    //daCtx.fillRect(x-0.5*daTheWidth,y-0.5*daTheWidth,daTheWidth,daTheWidth);
    //console.log("Got click");
  };
  $(this).on("click", dot);
  $(this).on("touchend", moveline);
  $(this).on("touchcancel", moveline);
  $(this).on("touchstart", start);
  $(this).on("touchmove", move);
};

// prototype to	start drawing on pointer(microsoft ie) using canvas moveTo and lineTo
$.fn.drawPointer = function () {
  var start = function (e) {
    e = e.originalEvent;
    daCtx.beginPath();
    daCtx.lineJoin = "round";
    x = e.pageX - $("#dasigcanvas").offset().left;
    y = e.pageY - $("#dasigcanvas").offset().top;
    daCtx.moveTo(x, y);
    if (daIsEmpty) {
      daIsEmpty = 0;
    }
    //daCtx.arc(x, y, 0.5*daTheWidth, 0, 2*Math.PI);
    //daCtx.fill();
  };
  var move = function (e) {
    e.preventDefault();
    if (daWaiter % daWaitLimit == 0) {
      e = e.originalEvent;
      x = e.pageX - $("#dasigcanvas").offset().left;
      y = e.pageY - $("#dasigcanvas").offset().top;
      daCtx.lineTo(x, y);
      daCtx.stroke();
      daCtx.beginPath();
      daCtx.arc(x, y, 0.5 * daTheWidth, 0, 2 * Math.PI);
      daCtx.fill();
      daCtx.beginPath();
      daCtx.moveTo(x, y);
      if (daIsEmpty) {
        daIsEmpty = 0;
      }
    }
    //daWaiter++;
  };
  var moveline = function (e) {
    daWaiter = 0;
    move(e);
  };
  $(this).on("MSPointerDown", start);
  $(this).on("MSPointerMove", move);
  $(this).on("MSPointerUp", moveline);
};

// prototype to	start drawing on mouse using canvas moveTo and lineTo
$.fn.drawMouse = function () {
  var clicked = 0;
  var start = function (e) {
    clicked = 1;
    x = e.pageX - $("#dasigcanvas").offset().left;
    y = e.pageY - $("#dasigcanvas").offset().top;
    daCtx.beginPath();
    daCtx.arc(x, y, 0.5 * daTheWidth, 0, 2 * Math.PI);
    daCtx.fill();
    daCtx.beginPath();
    daCtx.lineJoin = "round";
    daCtx.moveTo(x, y);
    if (daIsEmpty) {
      daIsEmpty = 0;
    }
  };
  var move = function (e) {
    if (clicked && daWaiter % daWaitLimit == 0) {
      x = e.pageX - $("#dasigcanvas").offset().left;
      y = e.pageY - $("#dasigcanvas").offset().top;
      daCtx.lineTo(x, y);
      daCtx.stroke();
      daCtx.beginPath();
      daCtx.arc(x, y, 0.5 * daTheWidth, 0, 2 * Math.PI);
      daCtx.fill();
      daCtx.beginPath();
      daCtx.moveTo(x, y);
      if (daIsEmpty) {
        daIsEmpty = 0;
      }
    }
    //daWaiter++;
  };
  var stop = function (e) {
    daWaiter = 0;
    move(e);
    clicked = 0;
    return true;
  };
  $(this).on("mousedown", start);
  $(this).on("mousemove", move);
  $(window).on("mouseup", stop);
};

function daPost(params) {
  for (var key in params) {
    if (params.hasOwnProperty(key)) {
      var hiddenField = document.getElementById(key);
      if (hiddenField != null) {
        hiddenField.setAttribute("value", params[key]);
      } else {
        console.log("Key does not exist: " + key);
        return;
      }
    }
  }
  $("#dasigform").submit();
  return;
}

function isCanvasSupported() {
  var elem = document.createElement("canvas");
  return !!(elem.getContext && elem.getContext("2d"));
}

var daAutocomplete = Object();

function daInitAutocomplete(ids) {
  var timePeriod = 0;
  try {
    google;
  } catch (e) {
    timePeriod = 1000;
  }
  setTimeout(function () {
    for (var i = 0; i < ids.length; ++i) {
      var id = ids[i];
      daAutocomplete[
        id
      ] = new google.maps.places.Autocomplete(document.getElementById(id), {
        types: ["address"],
      });
      daAutocomplete[id].setFields(["address_components"]);
      google.maps.event.addListener(
        daAutocomplete[id],
        "place_changed",
        daFillInAddressFor(id)
      );
    }
  }, timePeriod);
}

function daFillInAddressFor(id) {
  return function () {
    daFillInAddress(id);
  };
}

function daInitMap(daMapInfo) {
  var timePeriod = 0;
  try {
    google;
  } catch (e) {
    timePeriod = 1000;
  }
  setTimeout(function () {
    maps = [];
    var map_info_length = daMapInfo.length;
    for (var i = 0; i < map_info_length; i++) {
      the_map = daMapInfo[i];
      var bounds = new google.maps.LatLngBounds();
      maps[i] = daAddMap(i, the_map.center.latitude, the_map.center.longitude);
      marker_length = the_map.markers.length;
      if (marker_length == 1) {
        show_marker = true;
      } else {
        show_marker = false;
      }
      for (var j = 0; j < marker_length; j++) {
        var new_marker = daAddMarker(maps[i], the_map.markers[j], show_marker);
        bounds.extend(new_marker.getPosition());
      }
      if (marker_length > 1) {
        maps[i].map.fitBounds(bounds);
      }
    }
  }, timePeriod);
}

function daAddMap(map_num, center_lat, center_lon) {
  var map = new google.maps.Map(document.getElementById("map" + map_num), {
    zoom: 11,
    center: new google.maps.LatLng(center_lat, center_lon),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
  });
  var infowindow = new google.maps.InfoWindow();
  return { map: map, infowindow: infowindow };
}
function daAddMarker(map, marker_info, show_marker) {
  var marker;
  if (marker_info.icon) {
    if (marker_info.icon.path) {
      marker_info.icon.path = google.maps.SymbolPath[marker_info.icon.path];
    }
  } else {
    marker_info.icon = null;
  }
  marker = new google.maps.Marker({
    position: new google.maps.LatLng(
      marker_info.latitude,
      marker_info.longitude
    ),
    map: map.map,
    icon: marker_info.icon,
  });
  if (marker_info.info) {
    google.maps.event.addListener(
      marker,
      "click",
      (function (marker, info) {
        return function () {
          map.infowindow.setContent(info);
          map.infowindow.open(map.map, marker);
        };
      })(marker, marker_info.info)
    );
  }
  if (show_marker) {
    map.infowindow.setContent(marker_info.info);
    map.infowindow.open(map.map, marker);
  }
  return marker;
}

function daFillInAddress(origId) {
  var id;
  if (daVarLookupRev[origId]) {
    id = daVarLookupRev[origId];
  } else {
    id = origId;
  }
  var base_varname = atob(id).replace(/.address$/, "");
  base_varname = base_varname.replace(/[\[\]]/g, ".");
  var re = new RegExp("^" + base_varname + "\\.(.*)");
  var componentForm = {
    locality: "long_name",
    sublocality: "long_name",
    administrative_area_level_3: "long_name",
    administrative_area_level_2: "long_name",
    administrative_area_level_1: "short_name",
    country: "short_name",
    postal_code: "short_name",
  };
  var componentTrans = {
    locality: "city",
    administrative_area_level_2: "county",
    administrative_area_level_1: "state",
    country: "country",
    postal_code: "zip",
  };

  var fields_to_fill = [
    "address",
    "city",
    "county",
    "state",
    "zip",
    "neighborhood",
    "sublocality",
    "administrative_area_level_3",
    "postal_code",
  ];
  var id_for_part = {};
  $("input, select").each(function () {
    var the_id = $(this).attr("id");
    if (typeof the_id !== typeof undefined && the_id !== false) {
      try {
        var field_name = atob($(this).attr("id"));
        if (field_name.indexOf("_field_") == 0) {
          field_name = atob(daVarLookupRev[$(this).attr("id")]);
        }
        var m = re.exec(field_name);
        if (m.length > 0) {
          id_for_part[m[1]] = $(this).attr("id");
        }
      } catch (e) {}
    }
  });
  var place = daAutocomplete[origId].getPlace();
  if (
    typeof id_for_part["address"] != "undefined" &&
    document.getElementById(id_for_part["address"]) != null
  ) {
    document.getElementById(id_for_part["address"]).value = "";
  }

  for (var component in fields_to_fill) {
    if (
      typeof id_for_part[component] != "undefined" &&
      document.getElementById(id_for_part[component]) != null
    ) {
      document.getElementById(id_for_part[component]).value = "";
    }
  }

  var street_number;
  var route;
  var savedValues = {};

  for (var i = 0; i < place.address_components.length; i++) {
    var addressType = place.address_components[i].types[0];
    savedValues[addressType] = place.address_components[i]["long_name"];
    if (addressType == "street_number") {
      street_number = place.address_components[i]["short_name"];
    }
    if (addressType == "route") {
      route = place.address_components[i]["long_name"];
    }
    if (
      componentForm[addressType] &&
      id_for_part[componentTrans[addressType]] &&
      typeof id_for_part[componentTrans[addressType]] != "undefined" &&
      document.getElementById(id_for_part[componentTrans[addressType]]) != null
    ) {
      var val = place.address_components[i][componentForm[addressType]];
      if (typeof val != "undefined") {
        document.getElementById(
          id_for_part[componentTrans[addressType]]
        ).value = val;
      }
      if (componentTrans[addressType] != addressType) {
        val = place.address_components[i]["long_name"];
        if (
          typeof val != "undefined" &&
          typeof id_for_part[addressType] != "undefined" &&
          document.getElementById(id_for_part[addressType]) != null
        ) {
          document.getElementById(id_for_part[addressType]).value = val;
        }
      }
    } else if (
      id_for_part[addressType] &&
      typeof id_for_part[addressType] != "undefined" &&
      document.getElementById(id_for_part[addressType]) != null
    ) {
      var val = place.address_components[i]["long_name"];
      if (typeof val != "undefined") {
        document.getElementById(id_for_part[addressType]).value = val;
      }
    }
  }
  if (
    typeof id_for_part["address"] != "undefined" &&
    document.getElementById(id_for_part["address"]) != null
  ) {
    var the_address = "";
    if (typeof street_number != "undefined") {
      the_address += street_number + " ";
    }
    if (typeof route != "undefined") {
      the_address += route;
    }
    document.getElementById(id_for_part["address"]).value = the_address;
  }
  if (
    typeof id_for_part["city"] != "undefined" &&
    document.getElementById(id_for_part["city"]) != null
  ) {
    if (
      document.getElementById(id_for_part["city"]).value == "" &&
      typeof savedValues["sublocality_level_1"] != "undefined"
    ) {
      document.getElementById(id_for_part["city"]).value =
        savedValues["sublocality_level_1"];
    }
    if (
      document.getElementById(id_for_part["city"]).value == "" &&
      typeof savedValues["neighborhood"] != "undefined"
    ) {
      document.getElementById(id_for_part["city"]).value =
        savedValues["neighborhood"];
    }
    if (
      document.getElementById(id_for_part["city"]).value == "" &&
      typeof savedValues["administrative_area_level_3"] != "undefined"
    ) {
      document.getElementById(id_for_part["city"]).value =
        savedValues["administrative_area_level_3"];
    }
  }
}

function daGeolocate() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
      var geolocation = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      };
      var circle = new google.maps.Circle({
        center: geolocation,
        radius: position.coords.accuracy,
      });
      for (var id in daAutocomplete) {
        if (daAutocomplete.hasOwnProperty(id)) {
          daAutocomplete[id].setBounds(circle.getBounds());
        }
      }
    });
  }
}
