if (typeof $ == "undefined") {
  var $ = jQuery.noConflict();
}
var daCtx,
  daColor = "#000";

var daTheWidth;
var daAspectRatio;
var daTheBorders;
var daSigPad;
var daPrevCanvasWidth;

function daInitializeSignature() {
  daAspectRatio = 0.4;
  daTheBorders = 30;
  setTimeout(function () {
    if (!isCanvasSupported()) {
      daPost({ da_success: 0, da_ajax: 1 });
    }
    daNewCanvas();
    daPrevCanvasWidth = $("#dasigcanvas").width();
    $(document).on("touchmove", function (event) {
      if (window.matchMedia("(max-width: 575px)").matches) {
        event.preventDefault();
      }
    });

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
      daClearCanvas();
      return false;
    });
    $(".dasigsave").click(function (e) {
      e.preventDefault();
      if (daCanvasIsEmpty() && document.getElementById("da_sig_required").value == "1") {
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
  }, 500);
}

function daClearCanvas() {
  daSigPad.clear();
}

function daCanvasIsEmpty() {
  return daSigPad.isEmpty();
}

// function to setup a new canvas for drawing
function daResizeCanvas(){
  setTimeout(function () {
    var lines = daSigPad.toData();
    daNewCanvas();
    var currWidth = $('#dasigcanvas').width();
    // Restore old content
    var scale = currWidth/daPrevCanvasWidth;
    daPrevCanvasWidth = currWidth;
    daScaleSignaturePad(lines, scale);
    daSigPad.fromData(lines);
  }, 200);
  //console.log("I resized");
  return;
}

function daScaleSignaturePad (lines, scale) {
  lines.forEach(line => {
    line.points.forEach(point => {
      point.x *= scale;
      point.y *= scale;
    });
  });
};

function daSaveCanvas() {
  var dataURL = daSigPad.toDataURL("image/png");
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
  if (cheight > 275 || cheight < 30) {
    cheight = 275;
  }
  $("#dasigcontent").height(cheight);
  var canvas =
    '<canvas class="form-control" id="dasigcanvas" width="' +
    cwidth +
    'px" height="' +
    cheight +
    'px"></canvas>';
  $("#dasigcontent").html(canvas);
  //theTop = $("#sigcanvas").offset().top;
  //theLeft = $("#sigcanvas").offset().left;
  daTheWidth = (daThicknessScalingFactor * cwidth) / 100.0;
  if (daTheWidth < 1) {
    daTheWidth = 1;
  }

  // setup canvas
  daSigPad = new SignaturePad($("#dasigcanvas")[0], {
    dotSize: daTheWidth/1.75,
    maxWidth: daTheWidth,
    penColor: daColor
  });

  //$(document).on("touchend", function(event){event.preventDefault();});
  //$(document).on("touchcancel", function(event){event.preventDefault();});
  //$(document).on("touchstart", function(event){event.preventDefault();});
  //$("meta[name=viewport]").attr('content', "width=device-width, minimum-scale=1.0, maximum-scale=1.0, initial-scale=1.0, user-scalable=0");

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

function daInitAutocomplete(info) {
  var timePeriod = 0;
  try {
    google;
  } catch (e) {
    timePeriod = 1000;
  }
  setTimeout(function () {
    for (var i = 0; i < info.length; ++i) {
      var id = info[i][0];
      var opts = info[i][1];
      daAutocomplete[id] = new google.maps.places.Autocomplete(
        document.getElementById(id),
        opts
      );
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
  var base_varname = atob(id).replace(/.[a-zA-Z0-9_]+$/, "");
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
  var toChange = [];
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
        toChange.push("#" + id_for_part[componentTrans[addressType]]);
      }
      if (componentTrans[addressType] != addressType) {
        val = place.address_components[i]["long_name"];
        if (
          typeof val != "undefined" &&
          typeof id_for_part[addressType] != "undefined" &&
          document.getElementById(id_for_part[addressType]) != null
        ) {
          document.getElementById(id_for_part[addressType]).value = val;
          toChange.push("#" + id_for_part[addressType]);
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
        toChange.push("#" + id_for_part[addressType]);
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
    toChange.push("#" + id_for_part["address"]);
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
  if (
    place.adr_address &&
    typeof id_for_part["adr_address"] != "undefined" &&
    document.getElementById(id_for_part["adr_address"]) != null
  ) {
    document.getElementById(id_for_part["adr_address"]).value =
      place.adr_address;
  }
  if (
    place.business_status &&
    typeof id_for_part["business_status"] != "undefined" &&
    document.getElementById(id_for_part["business_status"]) != null
  ) {
    document.getElementById(id_for_part["business_status"]).value =
      place.business_status;
  }
  if (
    place.formatted_address &&
    typeof id_for_part["formatted_address"] != "undefined" &&
    document.getElementById(id_for_part["formatted_address"]) != null
  ) {
    document.getElementById(id_for_part["formatted_address"]).value =
      place.formatted_address;
  }
  if (
    place.formatted_phone_number &&
    typeof id_for_part["formatted_phone_number"] != "undefined" &&
    document.getElementById(id_for_part["formatted_phone_number"]) != null
  ) {
    document.getElementById(id_for_part["formatted_phone_number"]).value =
      place.formatted_phone_number;
  }
  if (place.geometry && place.geometry.location) {
    if (
      typeof id_for_part["latitude"] != "undefined" &&
      document.getElementById(id_for_part["latitude"]) != null
    ) {
      document.getElementById(
        id_for_part["latitude"]
      ).value = place.geometry.location.lat();
    }
    if (
      typeof id_for_part["longitude"] != "undefined" &&
      document.getElementById(id_for_part["longitude"]) != null
    ) {
      document.getElementById(
        id_for_part["longitude"]
      ).value = place.geometry.location.lng();
    }
  }
  if (
    place.icon &&
    typeof id_for_part["icon"] != "undefined" &&
    document.getElementById(id_for_part["icon"]) != null
  ) {
    document.getElementById(id_for_part["icon"]).value = place.icon;
  }
  if (
    place.international_phone_number &&
    typeof id_for_part["international_phone_number"] != "undefined" &&
    document.getElementById(id_for_part["international_phone_number"]) != null
  ) {
    document.getElementById(id_for_part["international_phone_number"]).value =
      place.international_phone_number;
  }
  if (
    place.name &&
    typeof id_for_part["name"] != "undefined" &&
    document.getElementById(id_for_part["name"]) != null
  ) {
    document.getElementById(id_for_part["name"]).value = place.name;
  }
  if (
    place.place_id &&
    typeof id_for_part["place_id"] != "undefined" &&
    document.getElementById(id_for_part["place_id"]) != null
  ) {
    document.getElementById(id_for_part["place_id"]).value = place.place_id;
  }
  if (
    place.price_level &&
    typeof id_for_part["price_level"] != "undefined" &&
    document.getElementById(id_for_part["price_level"]) != null
  ) {
    document.getElementById(id_for_part["price_level"]).value =
      place.price_level;
  }
  if (
    place.rating &&
    typeof id_for_part["rating"] != "undefined" &&
    document.getElementById(id_for_part["rating"]) != null
  ) {
    document.getElementById(id_for_part["rating"]).value = place.rating;
  }
  if (
    place.url &&
    typeof id_for_part["url"] != "undefined" &&
    document.getElementById(id_for_part["url"]) != null
  ) {
    document.getElementById(id_for_part["url"]).value = place.url;
  }
  if (
    place.utc_offset_minutes &&
    typeof id_for_part["utc_offset_minutes"] != "undefined" &&
    document.getElementById(id_for_part["utc_offset_minutes"]) != null
  ) {
    document.getElementById(id_for_part["utc_offset_minutes"]).value =
      place.utc_offset_minutes;
  }
  if (
    place.vicinity &&
    typeof id_for_part["vicinity"] != "undefined" &&
    document.getElementById(id_for_part["vicinity"]) != null
  ) {
    document.getElementById(id_for_part["vicinity"]).value = place.vicinity;
  }
  if (
    place.website &&
    typeof id_for_part["website"] != "undefined" &&
    document.getElementById(id_for_part["website"]) != null
  ) {
    document.getElementById(id_for_part["website"]).value = place.website;
  }
  for (var i = 0; i < toChange.length; i++) {
    $(toChange[i]).trigger("change");
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

function dagoogleapicallback() {}
