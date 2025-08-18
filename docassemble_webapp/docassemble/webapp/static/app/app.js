var $;

document.addEventListener("DOMContentLoaded", function () {
  if (typeof $ == "undefined") {
    $ = jQuery.noConflict();
  }
  if (daJsEmbed) {
    daTargetDiv = "#" + daJsEmbed;
  } else {
    daTargetDiv = "#dabody";
  }
  daPreloadImage(daImageToPreLoad);
  if (daAutoColorScheme) {
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
  $(document).ready(daReadyFunction);
  if (!daObserverMode) {
    $(window).ready(daUpdateHeight);
    $(window).resize(daUpdateHeight);
  }
  daConfigureJqueryFuncs();
  for (var i = 0; i < daInitialExtraScripts.length; i++) {
    daEvalExtraScript(daInitialExtraScripts[i]);
  }
  for (var i = 0; i < daCustomItems.length; i++) {
    try {
      daGlobalEval(daCustomItems[i].js);
    } catch {
      console.log(
        "Error with JavaScript code of CustomDataType " +
          daCustomItems[i].datatype,
      );
    }
  }
});

var daColor = "#000";
var daWindowWidth;
var daTheWidth;
var daAspectRatio;
var daTheBorders;
var daSignaturePad;

function daInitializeSignature(penColor, defaultImage) {
  daColor = penColor;
  daAspectRatio = 0.4;
  daTheBorders = 30;
  daNewCanvas(defaultImage);

  $(window).on("resize", function () {
    daResizeCanvas();
  });
  $(window).on("orientationchange", function () {
    daResizeCanvas();
  });
  $(".dasigclear").click(function (e) {
    e.preventDefault();
    daNewCanvas();
    return false;
  });
  $(".dasigsave").click(function (e) {
    e.preventDefault();
    if (
      daSignaturePad.isEmpty() &&
      document.getElementById("da_sig_required").value == "1"
    ) {
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
  if ($(window).width() != daWindowWidth) {
    daWindowWidth = $(window).width();
    setTimeout(function () {
      daNewCanvas();
    }, 200);
  }
  return;
}

function daSaveCanvas() {
  var dataURL = daSignaturePad.toDataURL();
  //console.log(dataURL)
  daSpinnerTimeout = setTimeout(daShowSpinner, 1000);
  daPost({ da_success: 1, da_the_image: dataURL, da_ajax: 1 });
}

function daNewCanvas(defaultImage = null) {
  //console.log("running daNewCanvas");
  daWindowWidth = $(window).width();
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
  daTheWidth = (daThicknessScalingFactor * cwidth) / 100.0;
  if (daTheWidth < 1) {
    daTheWidth = 1;
  }
  daSignaturePad = new SignaturePad(document.querySelector("#dasigcanvas"));
  if (defaultImage != null) {
    daSignaturePad.fromDataURL(defaultImage, {
      ratio: 1,
      width: cwidth,
      height: cheight,
      xOffset: 0,
      yOffset: 0,
    });
  }
  daSignaturePad.minWidth = 0.5 * daThicknessScalingFactor;
  daSignaturePad.maxWidth = 2.5 * daThicknessScalingFactor;
  daSignaturePad.penColor = daColor;
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

function daWaitForGoogle(waitForPlaces) {
  return new Promise((resolve) => {
    let attempts = 0;
    const maxAttempts = 50;
    const interval = setInterval(() => {
      var found = false;
      try {
        if (google.maps === undefined) {
          throw new Error("google maps not defined");
        }
        if (waitForPlaces) {
          if (google.maps.places === undefined) {
            throw new Error("places not defined");
          }
        }
        found = true;
      } catch (e) {}
      if (found || attempts >= maxAttempts) {
        clearInterval(interval);
        resolve(found);
      }
      attempts++;
    }, 100);
  });
}

function daInitAutocomplete(info) {
  daAutocomplete = Object();
  for (var i = 0; i < info.length; ++i) {
    daAutocomplete[info[i][0]] = {
      id: info[i][0],
      opts: info[i][1],
      suggestions: {},
    };
  }
}

async function daInitAutocompleteOld(info) {
  await daWaitForGoogle(true);
  for (var i = 0; i < info.length; ++i) {
    var id = info[i][0];
    var opts = info[i][1];
    daAutocomplete[id] = new google.maps.places.Autocomplete(
      document.getElementById(id),
      opts,
    );
    google.maps.event.addListener(
      daAutocomplete[id],
      "place_changed",
      daFillInAddressFor(id),
    );
  }
}

function daFillInAddressFor(id) {
  return function () {
    daFillInAddressOld(id);
  };
}

async function daInitMap(daMapInfo) {
  var googleLoaded = await daWaitForGoogle(false);
  if (!googleLoaded) {
    console.log("Could not load Google Maps library");
    return;
  }
  await google.maps.importLibrary("core");
  var timePeriod = 0;
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
      var new_marker = await daAddMarker(
        maps[i],
        the_map.markers[j],
        show_marker,
      );
      bounds.extend(
        new google.maps.LatLng(
          new_marker.position.lat,
          new_marker.position.lng,
        ),
      );
    }
    if (marker_length > 1) {
      maps[i].map.fitBounds(bounds);
    }
  }
}

function daAddMap(map_num, center_lat, center_lon) {
  var map = new google.maps.Map(document.getElementById("map" + map_num), {
    zoom: 11,
    center: new google.maps.LatLng(center_lat, center_lon),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapId: "map" + map_num + "element",
  });
  var infowindow = new google.maps.InfoWindow();
  return { map: map, infowindow: infowindow };
}

async function daAddMarker(map, marker_info, show_marker) {
  const { AdvancedMarkerElement, PinElement } =
    await google.maps.importLibrary("marker");
  var marker;
  var content;
  if (marker_info.icon) {
    content = new PinElement(marker_info.icon);
  } else {
    content = new PinElement();
  }
  marker = new AdvancedMarkerElement({
    position: {
      lat: marker_info.latitude,
      lng: marker_info.longitude,
    },
    map: map.map,
    content: content.element,
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
      })(marker, marker_info.info),
    );
  }
  if (show_marker) {
    map.infowindow.setContent(marker_info.info);
    map.infowindow.open(map.map, marker);
  }
  return marker;
}

function daFillInAddress(origId, place) {
  var id;
  if (daVarLookupRev[origId]) {
    id = daVarLookupRev[origId];
  } else {
    id = origId;
  }
  var baseVarname = atob(id).replace(/.[a-zA-Z0-9_]+$/, "");
  baseVarname = baseVarname.replace(/[\[\]]/g, ".");
  var re = new RegExp("^" + baseVarname + ".(.*)");
  var componentTrans = {
    administrative_area_level_1: ["state", "shortText"],
    administrative_area_level_2: ["county", "longText"],
  };
  var alternatives = [
    [
      "city",
      [
        "locality",
        "sublocality_level_1",
        "neighborhood",
        "administrative_area_level_3",
        "colloquial_area",
      ],
    ],
    [
      "sublocality",
      [
        "sublocality_level_1",
        "sublocality_level_2",
        "sublocality_level_3",
        "sublocality_level_4",
        "sublocality_level_5",
      ],
    ],
  ];
  var fieldsToClear = [
    "address",
    "administrative_area_level_1",
    "administrative_area_level_2",
    "administrative_area_level_3",
    "administrative_area_level_4",
    "administrative_area_level_5",
    "administrative_area_level_6",
    "administrative_area_level_7",
    "adr_format_address",
    "airport",
    "bus_station",
    "business_status",
    "city",
    "colloquial_area",
    "compound_code",
    "country",
    "county",
    "directions_uri",
    "display_name",
    "display_name_language_code",
    "establishment",
    "floor",
    "formatted_address",
    "global_code",
    "has_wheelchair_accessible_entrance",
    "has_wheelchair_accessible_parking",
    "has_wheelchair_accessible_restroom",
    "has_wheelchair_accessible_seating",
    "id",
    "international_phone_number",
    "intersection",
    "landmark",
    "latitude",
    "locality",
    "location",
    "longitude",
    "national_phone_number",
    "natural_feature",
    "neighborhood",
    "park",
    "parking",
    "photos_uri",
    "place_uri ",
    "plus_code",
    "point_of_interest",
    "political",
    "post_box",
    "postal_code",
    "postal_town",
    "premise",
    "price_level",
    "primary_type",
    "primary_type_display_name",
    "primary_type_display_name_language_code",
    "rating",
    "reviews_uri",
    "room",
    "route",
    "state",
    "street_number",
    "sublocality",
    "subpremise",
    "train_station",
    "transit_station",
    "types",
    "utc_offset_minutes",
    "write_a_review_uri",
    "zip",
  ];
  var idForPart = {};
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
          idForPart[m[1]] = $(this).attr("id");
        }
      } catch (e) {}
    }
  });
  for (var component in fieldsToClear) {
    if (
      typeof idForPart[component] != "undefined" &&
      document.getElementById(idForPart[component]) != null
    ) {
      document.getElementById(idForPart[component]).value = "";
    }
  }
  var savedValues = {};
  var toChange = [];
  for (var i = 0; i < place.addressComponents.length; i++) {
    var addressType = place.addressComponents[i].types[0];
    if (addressType == "street_number" || addressType == "country") {
      savedValues[addressType] = place.addressComponents[i]["shortText"];
    } else {
      savedValues[addressType] = place.addressComponents[i]["longText"];
    }
    if (
      componentTrans[addressType] &&
      idForPart[componentTrans[addressType][0]] &&
      typeof idForPart[componentTrans[addressType][0]] != "undefined" &&
      document.getElementById(idForPart[componentTrans[addressType][0]]) != null
    ) {
      var val = place.addressComponents[i][componentTrans[addressType][1]];
      if (typeof val != "undefined") {
        document.getElementById(
          idForPart[componentTrans[addressType][0]],
        ).value = val;
        toChange.push("#" + idForPart[componentTrans[addressType][0]]);
      }
    }
    if (
      idForPart[addressType] &&
      typeof idForPart[addressType] != "undefined" &&
      document.getElementById(idForPart[addressType]) != null
    ) {
      var val = savedValues[addressType];
      if (typeof val != "undefined") {
        document.getElementById(idForPart[addressType]).value = val;
        toChange.push("#" + idForPart[addressType]);
      }
    }
  }
  if (
    typeof idForPart["address"] != "undefined" &&
    document.getElementById(idForPart["address"]) != null
  ) {
    var the_address = "";
    if (typeof savedValues["street_number"] != "undefined") {
      the_address += savedValues["street_number"] + " ";
    }
    if (typeof savedValues["route"] != "undefined") {
      the_address += savedValues["route"];
    }
    document.getElementById(idForPart["address"]).value = the_address;
    toChange.push("#" + idForPart["address"]);
  }
  if (
    typeof idForPart["zip"] != "undefined" &&
    document.getElementById(idForPart["zip"]) != null &&
    typeof savedValues["postal_code"] != "undefined" &&
    savedValues["postal_code"] != ""
  ) {
    var theZipCode = savedValues["postal_code"];
    if (
      typeof savedValues["postal_code_suffix"] != "undefined" &&
      savedValues["postal_code_suffix"] != ""
    ) {
      theZipCode += "-" + savedValues["postal_code_suffix"];
    }
    document.getElementById(idForPart["zip"]).value = theZipCode;
    toChange.push("#" + idForPart["zip"]);
  }
  if (place.location) {
    if (
      typeof idForPart["latitude"] != "undefined" &&
      document.getElementById(idForPart["latitude"]) != null
    ) {
      document.getElementById(idForPart["latitude"]).value =
        place.location.lat();
      toChange.push("#" + idForPart["latitude"]);
    }
    if (
      typeof idForPart["longitude"] != "undefined" &&
      document.getElementById(idForPart["longitude"]) != null
    ) {
      document.getElementById(idForPart["longitude"]).value =
        place.location.lng();
      toChange.push("#" + idForPart["longitude"]);
    }
  }
  for (var i = 0; i < alternatives.length; i++) {
    const [fieldName, altList] = alternatives[i];
    if (
      typeof idForPart[fieldName] != "undefined" &&
      document.getElementById(idForPart[fieldName]) != null &&
      document.getElementById(idForPart[fieldName]).value == ""
    ) {
    }
    for (var j = 0; j < altList.length; j++) {
      if (typeof savedValues[altList[j]] != "undefined") {
        document.getElementById(idForPart[fieldName]).value =
          savedValues[altList[j]];
        toChange.push("#" + idForPart[fieldName]);
        break;
      }
    }
  }
  var fieldsToGet = daAutocomplete[origId].opts.fields || [];
  for (var i = 0; i < fieldsToGet.length; i++) {
    var pythonVar = fieldsToGet[i];
    if (pythonVar == "address_components" || pythonVar == "location") {
      continue;
    }
    var jsVar = underscoreToCamel(pythonVar);
    if (
      place[jsVar] != null &&
      typeof place[jsVar] === "object" &&
      !Array.isArray(place[jsVar])
    ) {
      var transformedObject = JSON.parse(JSON.stringify(place[jsVar]));
      Object.entries(transformedObject).forEach(([jsSubVar, value]) => {
        var pythonSubVar = camelToUnderscore(jsSubVar);
        if (
          value != null &&
          typeof idForPart[pythonSubVar] != "undefined" &&
          document.getElementById(idForPart[pythonSubVar]) != null
        ) {
          document.getElementById(idForPart[pythonSubVar]).value =
            jsonIfObject(value);
          toChange.push("#" + idForPart[pythonSubVar]);
        }
      });
    } else if (
      place[jsVar] &&
      typeof idForPart[pythonVar] != "undefined" &&
      document.getElementById(idForPart[pythonVar]) != null
    ) {
      document.getElementById(idForPart[pythonVar]).value = jsonIfObject(
        place[jsVar],
      );
      toChange.push("#" + idForPart[pythonVar]);
    }
  }
  for (var i = 0; i < toChange.length; i++) {
    $(toChange[i]).trigger("change");
  }
}

function daFillInAddressOld(origId) {
  var id;
  if (daVarLookupRev[origId]) {
    id = daVarLookupRev[origId];
  } else {
    id = origId;
  }
  var base_varname = atob(id).replace(/.[a-zA-Z0-9_]+$/, "");
  base_varname = base_varname.replace(/[\[\]]/g, ".");
  var re = new RegExp("^" + base_varname + ".(.*)");
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
  place = daAutocomplete[origId].getPlace();
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
          id_for_part[componentTrans[addressType]],
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
    typeof id_for_part["sublocality"] != "undefined" &&
    document.getElementById(id_for_part["sublocality"]) != null
  ) {
    if (
      document.getElementById(id_for_part["sublocality"]).value == "" &&
      typeof savedValues["sublocality_level_1"] != "undefined"
    ) {
      document.getElementById(id_for_part["sublocality"]).value =
        savedValues["sublocality_level_1"];
    }
    if (
      document.getElementById(id_for_part["sublocality"]).value == "" &&
      typeof savedValues["sublocality_level_2"] != "undefined"
    ) {
      document.getElementById(id_for_part["sublocality"]).value =
        savedValues["sublocality_level_2"];
    }
    if (
      document.getElementById(id_for_part["sublocality"]).value == "" &&
      typeof savedValues["sublocality_level_3"] != "undefined"
    ) {
      document.getElementById(id_for_part["sublocality"]).value =
        savedValues["sublocality_level_3"];
    }
    if (
      document.getElementById(id_for_part["sublocality"]).value == "" &&
      typeof savedValues["sublocality_level_4"] != "undefined"
    ) {
      document.getElementById(id_for_part["sublocality"]).value =
        savedValues["sublocality_level_4"];
    }
    if (
      document.getElementById(id_for_part["sublocality"]).value == "" &&
      typeof savedValues["sublocality_level_5"] != "undefined"
    ) {
      document.getElementById(id_for_part["sublocality"]).value =
        savedValues["sublocality_level_5"];
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
      document.getElementById(id_for_part["latitude"]).value =
        place.geometry.location.lat();
    }
    if (
      typeof id_for_part["longitude"] != "undefined" &&
      document.getElementById(id_for_part["longitude"]) != null
    ) {
      document.getElementById(id_for_part["longitude"]).value =
        place.geometry.location.lng();
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
var daRequestPending = false;
var isAndroid = /android/i.test(navigator.userAgent.toLowerCase());
var daWhichButton = null;
var daSocket = null;
var daChatHistory = [];
var daCheckinCode = null;
var daCheckingIn = 0;
var daShowingHelp = 0;
var daIframeEmbed;
if (window.location !== window.parent.location) {
  daIframeEmbed = true;
} else {
  daIframeEmbed = false;
}
var daChatPartnersAvailable = 0;
var daPhoneAvailable = false;
var daInitialized = false;
var daNotYetScrolled = true;
var daInformedChanged = false;
var daShowingSpinner = false;
var daSpinnerTimeout = null;
var daSubmitter = null;
var daGAConfigured = false;
var daShowIfInProcess = false;
var daFieldsToSkip = [
  "_checkboxes",
  "_empties",
  "_ml_info",
  "_back_one",
  "_files",
  "_files_inline",
  "_question_name",
  "_the_image",
  "_save_as",
  "_success",
  "_datatypes",
  "_event",
  "_visible",
  "_tracker",
  "_track_location",
  "_varnames",
  "_next_action",
  "_next_action_to_set",
  "ajax",
  "json",
  "informed",
  "csrf_token",
  "_action",
  "_order_changes",
  "_collect",
  "_list_collect_list",
  "_null_question",
];
var daVarLookup = Object();
var daVarLookupRev = Object();
var daVarLookupMulti = Object();
var daVarLookupRevMulti = Object();
var daVarLookupSelect = Object();
var daVarLookupCheckbox = Object();
var daVarLookupOption = Object();
var daTargetDiv;
var daComboBoxes = Object();
var daGlobalEval = eval;
var daFetchAcceptIncoming = false;
var daFetchAjaxTimeout = null;
var daFetchAjaxTimeoutRunning = null;
var daFetchAjaxTimeoutFetchAfter = null;
var daAddressAcceptIncoming = false;
var daAddressAjaxTimeout = null;
var daAddressAjaxTimeoutRunning = null;
var daAddressAjaxTimeoutCallAfter = null;
var daShowHideHappened = false;
var daCheckinInterval = null;
var daReloader = null;
var daDisable = null;
var daAutoColorScheme = true;
var daCurrentColorScheme;
var daUrlChangeColorScheme;
var daDesiredColorScheme;
var daAutoColorScheme = true;
var daThicknessScalingFactor;
var daJsEmbed;
var daAllowGoingBack;
var daSteps;
var daIsUser;
var daUserId;
var daChatStatus;
var daChatAvailable;
var daChatMode;
var daSendChanges;
var daBeingControlled;
var daInformed;
var daUsingGA;
var daUsingSegment;
var daDoAction;
var daQuestionID;
var daCsrf;
var daComboboxButtonLabel;
var daInterviewUrl;
var daLocationBar;
var daPostURL;
var daYamlFilename;
var daNotificationContainer;
var daNotificationMessage;
var daMessageLog;
var daImageToPreLoad;
var daGetVariablesUrl;
var daLiveHelpMessage;
var daLiveHelpMessagePhone;
var daNewChatMessage;
var daLiveHelpAvailableMessage;
var daScreenBeingControlled;
var daScreenNoLongerBeingControlled;
var daPathRoot;
var daCheckinSeconds;
var daChatRoles;
var daChatPartnerRoles;
var daAllButtonClasses;
var daButtonStyle;
var daShouldForceFullScreen;
var daPageSep;
var daAreYouSure;
var daOtherUser;
var daOtherUsers;
var daOperator;
var daOperators;
var daCheckinUrl;
var daCheckoutUrl;
var daCurrencyDecimalPlaces;
var daShouldDebugReadabilityHelp;
var daShouldDebugReadabilityQuestion;
var daEmailAddressRequired;
var daNeedCompleteEmail;
var daDefaultPopoverTrigger;
var daToggleWord;
var daCheckinUrlWithInterview;
var daReloadAfterSeconds;
var daCustomItems;
var daTrackingEnabled;

function dagoogleapicallback() {}
function daForceFullScreen(data) {
  if (data.steps > 1 && window != top) {
    top.location.href = location.href;
  }
}
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
function daGoToAnchor(target) {
  if (daJsEmbed) {
    scrollTarget = $(target).first().position().top - 60;
  } else {
    scrollTarget = $(target).first().offset().top - 60;
  }
  if (scrollTarget != null) {
    if (daJsEmbed) {
      $(daTargetDiv).animate(
        {
          scrollTop: scrollTarget,
        },
        500,
      );
    } else {
      $("html, body").animate(
        {
          scrollTop: scrollTarget,
        },
        500,
      );
    }
  }
}
function atou(b64) {
  return decodeURIComponent(escape(atob(b64)));
}
function utoa(data) {
  return btoa(unescape(encodeURIComponent(data)));
}
function dabtoa(str) {
  return window.utoa(str).replace(/[\n=]/g, "");
}
function daatob(str) {
  return atou(str);
}
function hideTablist() {
  var anyTabs =
    $("#daChatAvailable").is(":visible") ||
    $("daPhoneAvailable").is(":visible") ||
    $("#dahelptoggle").is(":visible");
  if (anyTabs) {
    $("#nav-bar-tab-list").removeClass("dainvisible");
    $("#daquestionlabel").parent().removeClass("dainvisible");
  } else {
    $("#nav-bar-tab-list").addClass("dainvisible");
    $("#daquestionlabel").parent().addClass("dainvisible");
  }
}
function getFields() {
  var allFields = [];
  for (var rawFieldName in daVarLookup) {
    if (daVarLookup.hasOwnProperty(rawFieldName)) {
      var fieldName = atou(rawFieldName);
      if (allFields.indexOf(fieldName) == -1) {
        allFields.push(fieldName);
      }
    }
  }
  return allFields;
}
var daGetFields = getFields;
function daAppendIfExists(fieldName, theArray) {
  var elem = $("[name='" + fieldName + "']");
  if (elem.length > 0) {
    for (var i = 0; i < theArray.length; ++i) {
      if (theArray[i] == elem[0]) {
        return;
      }
    }
    theArray.push(elem[0]);
  }
}
function getField(fieldName, notInDiv) {
  if (daVarLookupCheckbox[fieldName]) {
    var n = daVarLookupCheckbox[fieldName].length;
    for (var i = 0; i < n; ++i) {
      var elem = daVarLookupCheckbox[fieldName][i].checkboxes[0].elem;
      if (!$(elem).prop("disabled")) {
        var showifParents = $(elem).parents(".dajsshowif,.dashowif");
        if (
          showifParents.length == 0 ||
          $(showifParents[0]).data("isVisible") == "1"
        ) {
          if (notInDiv && $.contains(notInDiv, elem)) {
            continue;
          }
          return daVarLookupCheckbox[fieldName][i].elem;
        }
      }
    }
  }
  if (daVarLookupSelect[fieldName]) {
    var n = daVarLookupSelect[fieldName].length;
    for (var i = 0; i < n; ++i) {
      var elem = daVarLookupSelect[fieldName][i].select;
      if (!$(elem).prop("disabled")) {
        var showifParents = $(elem).parents(".dajsshowif,.dashowif");
        if (
          showifParents.length == 0 ||
          $(showifParents[0]).data("isVisible") == "1"
        ) {
          if (notInDiv && $.contains(notInDiv, elem)) {
            continue;
          }
          return elem;
        }
      }
    }
  }
  var fieldNameEscaped = dabtoa(fieldName);
  var possibleElements = [];
  daAppendIfExists(fieldNameEscaped, possibleElements);
  if (daVarLookupMulti.hasOwnProperty(fieldNameEscaped)) {
    for (var i = 0; i < daVarLookupMulti[fieldNameEscaped].length; ++i) {
      daAppendIfExists(daVarLookupMulti[fieldNameEscaped][i], possibleElements);
    }
  }
  var returnVal = null;
  for (var i = 0; i < possibleElements.length; ++i) {
    if (
      !$(possibleElements[i]).prop("disabled") ||
      $(possibleElements[i]).parents(".file-input.is-locked").length > 0
    ) {
      var showifParents = $(possibleElements[i]).parents(
        ".dajsshowif,.dashowif",
      );
      if (
        showifParents.length == 0 ||
        $(showifParents[0]).data("isVisible") == "1"
      ) {
        if (notInDiv && $.contains(notInDiv, possibleElements[i])) {
          continue;
        }
        returnVal = possibleElements[i];
      }
    }
  }
  if (
    $(returnVal).hasClass("da-to-labelauty") &&
    $(returnVal).parents("div.da-field-group").length > 0
  ) {
    var fieldSet = $(returnVal).parents("div.da-field-group")[0];
    if (
      !$(fieldSet).hasClass("da-field-checkbox") &&
      !$(fieldSet).hasClass("da-field-checkboxes")
    ) {
      return fieldSet;
    }
  }
  return returnVal;
}
var daGetField = getField;
function setChoices(fieldName, choices) {
  var elem = daGetField(fieldName);
  if (elem == null) {
    console.log("setChoices: reference to non-existent field " + fieldName);
    return;
  }
  var isCombobox =
    $(elem).attr("type") == "hidden" &&
    $(elem).parents(".combobox-container").length > 0;
  if (isCombobox) {
    var comboInput = $(elem)
      .parents(".combobox-container")
      .first()
      .find("input.combobox")
      .first();
    var comboObject = daComboBoxes[$(comboInput).attr("id")];
    var oldComboVal = comboObject.$target.val();
    elem = comboObject.$source;
  }
  if ($(elem).prop("tagName") != "SELECT") {
    console.log("setField: field " + fieldName + " is not a dropdown field");
    return;
  }
  var oldVal = $(elem).val();
  $(elem)
    .find("option[value!='']")
    .each(function () {
      $(this).remove();
    });
  var n = choices.length;
  for (var i = 0; i < n; i++) {
    var opt = $("<option>");
    opt.val(choices[i][0]);
    opt.text(choices[i][1]);
    if (oldVal == choices[i][0]) {
      opt.attr("selected", "selected");
    }
    $(elem).append(opt);
  }
  if (isCombobox) {
    comboObject.refresh();
    comboObject.clearTarget();
    if (oldComboVal != "") {
      daSetField(fieldName, oldComboVal);
    }
  }
}
var daSetChoices = setChoices;
function setField(fieldName, theValue) {
  var elem = daGetField(fieldName);
  if (elem == null) {
    console.log("setField: reference to non-existent field " + fieldName);
    return;
  }
  if (
    $(elem).prop("tagName") == "DIV" &&
    $(elem).hasClass("da-field-group") &&
    $(elem).hasClass("da-field-radio")
  ) {
    elem = $(elem).find("input")[0];
  }
  if ($(elem).attr("type") == "checkbox") {
    if (theValue) {
      if ($(elem).prop("checked") != true) {
        $(elem).click();
      }
    } else {
      if ($(elem).prop("checked") != false) {
        $(elem).click();
      }
    }
  } else if ($(elem).attr("type") == "radio") {
    var fieldNameEscaped = $(elem)
      .attr("name")
      .replace(/(:|\.|\[|\]|,|=)/g, "\\$1");
    var wasSet = false;
    if (theValue === true) {
      theValue = "True";
    }
    if (theValue === false) {
      theValue = "False";
    }
    $("input[name='" + fieldNameEscaped + "']").each(function () {
      if ($(this).val() == theValue) {
        if ($(this).prop("checked") != true) {
          $(this).prop("checked", true);
          $(this).trigger("change");
        }
        wasSet = true;
        return false;
      }
    });
    if (!wasSet) {
      console.log(
        "setField: could not set radio button " + fieldName + " to " + theValue,
      );
    }
  } else if ($(elem).attr("type") == "hidden") {
    if ($(elem).val() != theValue) {
      if ($(elem).parents(".combobox-container").length > 0) {
        var comboInput = $(elem)
          .parents(".combobox-container")
          .first()
          .find("input.combobox")
          .first();
        daComboBoxes[$(comboInput).attr("id")].manualSelect(theValue);
      } else {
        $(elem).val(theValue);
        $(elem).trigger("change");
      }
    }
  } else if (
    $(elem).prop("tagName") == "DIV" &&
    $(elem).hasClass("da-field-group") &&
    $(elem).hasClass("da-field-checkboxes")
  ) {
    if (!Array.isArray(theValue)) {
      throw new Error("setField: value must be an array");
    }
    var n = theValue.length;
    $(elem)
      .find("input")
      .each(function () {
        if ($(this).hasClass("danota-checkbox")) {
          $(this).prop("checked", n == 0);
          $(this).trigger("change");
          return;
        }
        if ($(this).hasClass("daaota-checkbox")) {
          $(this).prop("checked", false);
          $(this).trigger("change");
          return;
        }
        if ($(this).attr("name").substr(0, 7) === "_ignore") {
          return;
        }
        var theVal = atou($(this).data("cbvalue"));
        if ($(elem).hasClass("daobject")) {
          theVal = atou(theVal);
        }
        var oldVal = $(this).prop("checked") == true;
        var newVal = false;
        for (var i = 0; i < n; ++i) {
          if (theValue[i] == theVal) {
            newVal = true;
          }
        }
        if (oldVal != newVal) {
          $(this).click();
        }
      });
  } else if (
    $(elem).prop("tagName") == "SELECT" &&
    $(elem).hasClass("damultiselect")
  ) {
    if (daVarLookupSelect[fieldName]) {
      var n = daVarLookupSelect[fieldName].length;
      for (var i = 0; i < n; ++i) {
        if (daVarLookupSelect[fieldName][i].select === elem) {
          var oldValue =
            $(daVarLookupSelect[fieldName][i].option).prop("selected") == true;
          if (oldValue != theValue) {
            $(daVarLookupSelect[fieldName][i].option).prop(
              "selected",
              theValue,
            );
            $(elem).trigger("change");
          }
        }
      }
    } else {
      if (!Array.isArray(theValue)) {
        throw new Error("setField: value must be an array");
      }
      var n = theValue.length;
      var changed = false;
      $(elem)
        .find("option")
        .each(function () {
          var thisVal = daVarLookupOption[$(this).val()];
          var oldVal = $(this).prop("selected") == true;
          var newVal = false;
          for (var i = 0; i < n; ++i) {
            if (thisVal == theValue[i]) {
              newVal = true;
            }
          }
          if (newVal !== oldVal) {
            changed = true;
            $(this).prop("selected", newVal);
          }
        });
      if (changed) {
        $(elem).trigger("change");
      }
    }
  } else {
    if ($(elem).val() != theValue) {
      $(elem).val(theValue);
      $(elem).trigger("change");
    }
  }
}
var daSetField = setField;
function val(fieldName) {
  var elem = daGetField(fieldName);
  if (elem == null) {
    return null;
  }
  if (
    $(elem).prop("tagName") == "DIV" &&
    $(elem).hasClass("da-field-group") &&
    $(elem).hasClass("da-field-radio")
  ) {
    elem = $(elem).find("input")[0];
  }
  if ($(elem).attr("type") == "checkbox") {
    if ($(elem).prop("checked")) {
      theVal = true;
    } else {
      theVal = false;
    }
  } else if ($(elem).attr("type") == "radio") {
    var fieldNameEscaped = $(elem)
      .attr("name")
      .replace(/(:|\.|\[|\]|,|=)/g, "\\$1");
    theVal = $("input[name='" + fieldNameEscaped + "']:checked").val();
    if (typeof theVal == "undefined") {
      theVal = null;
    } else {
      if ($(elem).hasClass("daobject")) {
        theVal = atou(theVal);
      } else if (theVal == "True") {
        theVal = true;
      } else if (theVal == "False") {
        theVal = false;
      }
    }
  } else if (
    $(elem).prop("tagName") == "DIV" &&
    $(elem).hasClass("da-field-group") &&
    $(elem).hasClass("da-field-checkboxes")
  ) {
    var cbSelected = [];
    $(elem)
      .find("input")
      .each(function () {
        if ($(this).attr("name").substr(0, 7) === "_ignore") {
          return;
        }
        var theVal = atou($(this).data("cbvalue"));
        if ($(elem).hasClass("daobject")) {
          theVal = atou(theVal);
        }
        if ($(this).prop("checked")) {
          cbSelected.push(theVal);
        }
      });
    return cbSelected;
  } else if (
    $(elem).prop("tagName") == "SELECT" &&
    $(elem).hasClass("damultiselect")
  ) {
    if (daVarLookupSelect[fieldName]) {
      var n = daVarLookupSelect[fieldName].length;
      for (var i = 0; i < n; ++i) {
        if (daVarLookupSelect[fieldName][i].select === elem) {
          return $(daVarLookupSelect[fieldName][i].option).prop("selected");
        }
      }
    } else {
      var selectedVals = [];
      $(elem)
        .find("option")
        .each(function () {
          if ($(this).prop("selected")) {
            if (daVarLookupOption[$(this).val()]) {
              selectedVals.push(daVarLookupOption[$(this).val()]);
            }
          }
        });
      return selectedVals;
    }
  } else if (
    $(elem).prop("tagName") == "SELECT" &&
    $(elem).hasClass("daobject")
  ) {
    theVal = atou($(elem).val());
  } else {
    theVal = $(elem).val();
  }
  return theVal;
}
var da_val = val;
function daFormAsJSON(elem) {
  var isInitial = false;
  var formData = $("#daform").serializeArray();
  var data = Object();
  if (elem == "initial") {
    elem = null;
    data["_initial"] = true;
  } else {
    data["_initial"] = false;
  }
  if (elem !== null && $(elem).hasClass("combobox")) {
    elem = $(elem).parent().find('input[type="hidden"]');
  }
  data["_changed"] = null;
  var n = formData.length;
  for (var i = 0; i < n; ++i) {
    var key = formData[i]["name"];
    var val = formData[i]["value"];
    if ($.inArray(key, daFieldsToSkip) != -1 || key.indexOf("_ignore") == 0) {
      continue;
    }
    var isChangedElem = false;
    if (elem !== null && key == $(elem).attr("name")) {
      isChangedElem = true;
    }
    if (typeof daVarLookupRev[key] != "undefined") {
      data[atou(daVarLookupRev[key])] = val;
      if (isChangedElem) {
        data["_changed"] = atou(daVarLookupRev[key]);
      }
    } else {
      data[atou(key)] = val;
      if (isChangedElem) {
        data["_changed"] = atou(key);
      }
    }
  }
  return JSON.stringify(data);
}
function daPreloadImage(url) {
  var img = new Image();
  img.src = url;
}
function daShowHelpTab() {
  $("#dahelptoggle").tab("show");
}
function addCsrfHeader(xhr, settings) {
  if (daJsEmbed && !/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
    xhr.setRequestHeader("X-CSRFToken", daCsrf);
  }
}
function flash(message, priority, clear) {
  if (priority == null) {
    priority = "info";
  }
  if (!$("#daflash").length) {
    $(daTargetDiv).append(daSprintf(daNotificationContainer, ""));
  }
  if (clear) {
    $("#daflash").empty();
  }
  if (message != null) {
    var newElement = $(daSprintf(daNotificationMessage, priority, message));
    $("#daflash").append(newElement);
    if (priority == "success") {
      setTimeout(function () {
        newElement.hide(300, function () {
          $(this).remove();
        });
      }, 3000);
    }
  }
}
var da_flash = flash;
function url_action(action, args) {
  if (args == null) {
    args = {};
  }
  data = { action: action, arguments: args };
  var url;
  if (daJsEmbed) {
    url =
      daPostURL + "&action=" + encodeURIComponent(utoa(JSON_stringify(data)));
  } else {
    if (daLocationBar.indexOf("?") !== -1) {
      url =
        daLocationBar +
        "&action=" +
        encodeURIComponent(utoa(JSON_stringify(data)));
    } else {
      url =
        daLocationBar +
        "?action=" +
        encodeURIComponent(utoa(JSON_stringify(data)));
    }
  }
  return url;
}
var da_url_action = url_action;
function action_call(action, args, callback, forgetPrior = false) {
  if (args == null) {
    args = {};
  }
  if (forgetPrior) {
    args = { _action: action, _arguments: args };
    action = "_da_priority_action";
  }
  if (callback == null) {
    callback = function () {};
  }
  var data = { action: action, arguments: args };
  var url;
  if (daJsEmbed) {
    url =
      daPostURL + "&action=" + encodeURIComponent(utoa(JSON_stringify(data)));
  } else {
    url =
      daInterviewUrl +
      "&action=" +
      encodeURIComponent(utoa(JSON_stringify(data)));
  }
  return $.ajax({
    type: "GET",
    url: url,
    success: callback,
    beforeSend: addCsrfHeader,
    xhrFields: {
      withCredentials: true,
    },
    error: function (xhr, status, error) {
      setTimeout(function () {
        daProcessAjaxError(xhr, status, error);
      }, 0);
    },
  });
}
var da_action_call = action_call;
var url_action_call = action_call;
function action_perform(action, args, forgetPrior = false) {
  if (args == null) {
    args = {};
  }
  if (forgetPrior) {
    args = { _action: action, _arguments: args };
    action = "_da_priority_action";
  }
  var data = { action: action, arguments: args };
  daSpinnerTimeout = setTimeout(daShowSpinner, 1000);
  daRequestPending = true;
  return $.ajax({
    type: "POST",
    url: daInterviewUrl,
    beforeSend: addCsrfHeader,
    xhrFields: {
      withCredentials: true,
    },
    data: $.param({
      _action: utoa(JSON_stringify(data)),
      csrf_token: daCsrf,
      ajax: 1,
    }),
    success: function (data) {
      setTimeout(function () {
        daProcessAjax(data, $("#daform"), 1);
      }, 0);
    },
    error: function (xhr, status, error) {
      setTimeout(function () {
        daProcessAjaxError(xhr, status, error);
      }, 0);
    },
    dataType: "json",
  });
}
var da_action_perform = action_perform;
var url_action_perform = action_perform;
function action_perform_with_next(
  action,
  args,
  next_data,
  forgetPrior = false,
) {
  //console.log("action_perform_with_next: " + action + " | " + next_data)
  if (args == null) {
    args = {};
  }
  if (forgetPrior) {
    args = { _action: action, _arguments: args };
    action = "_da_priority_action";
  }
  var data = { action: action, arguments: args };
  daSpinnerTimeout = setTimeout(daShowSpinner, 1000);
  daRequestPending = true;
  return $.ajax({
    type: "POST",
    url: daInterviewUrl,
    beforeSend: addCsrfHeader,
    xhrFields: {
      withCredentials: true,
    },
    data: $.param({
      _action: utoa(JSON_stringify(data)),
      _next_action_to_set: utoa(JSON_stringify(next_data)),
      csrf_token: daCsrf,
      ajax: 1,
    }),
    success: function (data) {
      setTimeout(function () {
        daProcessAjax(data, $("#daform"), 1);
      }, 0);
    },
    error: function (xhr, status, error) {
      setTimeout(function () {
        daProcessAjaxError(xhr, status, error);
      }, 0);
    },
    dataType: "json",
  });
}
var da_action_perform_with_next = action_perform_with_next;
var url_action_perform_with_next = action_perform_with_next;
function get_interview_variables(callback) {
  if (callback == null) {
    callback = function () {};
  }
  return $.ajax({
    type: "GET",
    url: daGetVariablesUrl,
    success: callback,
    beforeSend: addCsrfHeader,
    xhrFields: {
      withCredentials: true,
    },
    error: function (xhr, status, error) {
      setTimeout(function () {
        daProcessAjaxError(xhr, status, error);
      }, 0);
    },
  });
}
var da_get_interview_variables = get_interview_variables;
function daInformAbout(subject, chatMessage) {
  if (subject in daInformed || (subject != "chatmessage" && !daIsUser)) {
    return;
  }
  if (daShowingHelp && subject != "chatmessage") {
    daInformed[subject] = 1;
    daInformedChanged = true;
    return;
  }
  if (daShowingHelp && subject == "chatmessage") {
    return;
  }
  var target;
  var message;
  var waitPeriod = 3000;
  if (subject == "chat") {
    target = "#daChatAvailable a";
    message = daLiveHelpMessage;
  } else if (subject == "chatmessage") {
    target = "#daChatAvailable a";
    message = chatMessage;
  } else if (subject == "phone") {
    target = "#daPhoneAvailable a";
    message = daLiveHelpMessagePhone;
  } else {
    return;
  }
  if (subject != "chatmessage") {
    daInformed[subject] = 1;
    daInformedChanged = true;
  }
  if (subject == "chatmessage") {
    $(target).popover({
      content: message,
      placement: "bottom",
      trigger: "manual",
      container: "body",
      title: daNewChatMessage,
    });
  } else {
    $(target).popover({
      content: message,
      placement: "bottom",
      trigger: "manual",
      container: "body",
      title: daLiveHelpAvailableMessage,
    });
  }
  $(target).popover("show");
  setTimeout(function () {
    $(target).popover("dispose");
    $(target).removeAttr("title");
  }, waitPeriod);
}
// function daCloseSocket(){
//   if (typeof daSocket !== 'undefined' && daSocket.connected){
//     //daSocket.emit('terminate');
//     //io.unwatch();
//   }
// }
function daPublishMessage(data) {
  var newDiv = document.createElement("li");
  $(newDiv).addClass("list-group-item");
  if (data.is_self) {
    $(newDiv).addClass("list-group-item-primary dalistright");
  } else {
    $(newDiv).addClass("list-group-item-secondary dalistleft");
  }
  //var newSpan = document.createElement('span');
  //$(newSpan).html(data.message);
  //$(newSpan).appendTo($(newDiv));
  //var newName = document.createElement('span');
  //$(newName).html(userNameString(data));
  //$(newName).appendTo($(newDiv));
  $(newDiv).html(data.message);
  $("#daCorrespondence").append(newDiv);
}
function daScrollChat() {
  var chatScroller = $("#daCorrespondence");
  if (chatScroller.length) {
    var height = chatScroller[0].scrollHeight;
    //console.log("Slow scrolling to " + height);
    if (height == 0) {
      daNotYetScrolled = true;
      return;
    }
    chatScroller.animate({ scrollTop: height }, 800);
  } else {
    console.log("daScrollChat: error");
  }
}
function daScrollChatFast() {
  var chatScroller = $("#daCorrespondence");
  if (chatScroller.length) {
    var height = chatScroller[0].scrollHeight;
    if (height == 0) {
      daNotYetScrolled = true;
      return;
    }
    //console.log("Scrolling to " + height + " where there are " + chatScroller[0].childElementCount + " children");
    chatScroller.scrollTop(height);
  } else {
    console.log("daScrollChatFast: error");
  }
}
function daSender() {
  //console.log("daSender");
  if ($("#daMessage").val().length) {
    daSocket.emit("chatmessage", {
      data: $("#daMessage").val(),
      i: daYamlFilename,
    });
    $("#daMessage").val("");
    $("#daMessage").focus();
  }
  return false;
}
function daShowControl(mode) {
  //console.log("You are now being controlled");
  if ($("body").hasClass("dacontrolled")) {
    return;
  }
  $('input[type="submit"], button[type="submit"]').prop("disabled", true);
  $("body").addClass("dacontrolled");
  var newDiv = document.createElement("div");
  $(newDiv).addClass(
    "datop-alert col-xs-10 col-sm-7 col-md-6 col-lg-5 dacol-centered",
  );
  $(newDiv).html(daScreenBeingControlled);
  $(newDiv).attr("id", "dacontrolAlert");
  $(newDiv).css("display", "none");
  $(newDiv).appendTo($(daTargetDiv));
  if (mode == "animated") {
    $(newDiv).slideDown();
  } else {
    $(newDiv).show();
  }
}
function daHideControl() {
  //console.log("You are no longer being controlled");
  if (!$("body").hasClass("dacontrolled")) {
    return;
  }
  $('input[type="submit"], button[type="submit"]').prop("disabled", false);
  $("body").removeClass("dacontrolled");
  $("#dacontrolAlert").html(daScreenNoLongerBeingControlled);
  setTimeout(function () {
    $("#dacontrolAlert").slideUp(300, function () {
      $("#dacontrolAlert").remove();
    });
  }, 2000);
}
function daInitializeSocket() {
  if (daSocket != null) {
    if (daSocket.connected) {
      //console.log("Calling connectagain");
      if (daChatStatus == "ready") {
        daSocket.emit("connectagain", { i: daYamlFilename });
      }
      if (daBeingControlled) {
        daShowControl("animated");
        daSocket.emit("start_being_controlled", { i: daYamlFilename });
      }
    } else {
      //console.log('daInitializeSocket: daSocket.connect()');
      daSocket.connect();
    }
    return;
  }
  if (location.protocol === "http:" || document.location.protocol === "http:") {
    daSocket = io.connect("http://" + document.domain + "/wsinterview", {
      path: daPathRoot + "ws/socket.io",
      query: "i=" + daYamlFilename,
    });
  }
  if (
    location.protocol === "https:" ||
    document.location.protocol === "https:"
  ) {
    daSocket = io.connect("https://" + document.domain + "/wsinterview", {
      path: daPathRoot + "ws/socket.io",
      query: "i=" + daYamlFilename,
    });
  }
  //console.log("daInitializeSocket: socket is " + daSocket);
  if (daSocket != null) {
    daSocket.on("connect", function () {
      if (daSocket == null) {
        console.log("Error: socket is null");
        return;
      }
      //console.log("Connected socket with sid " + daSocket.id);
      if (daChatStatus == "ready") {
        daChatStatus = "on";
        daDisplayChat();
        daPushChanges();
        //daTurnOnChat();
        //console.log("Emitting chat_log from on connect");
        daSocket.emit("chat_log", { i: daYamlFilename });
      }
      if (daBeingControlled) {
        daShowControl("animated");
        daSocket.emit("start_being_controlled", { i: daYamlFilename });
      }
    });
    daSocket.on("chat_log", function (arg) {
      //console.log("Got chat_log");
      $("#daCorrespondence").html("");
      daChatHistory = [];
      var messages = arg.data;
      for (var i = 0; i < messages.length; ++i) {
        daChatHistory.push(messages[i]);
        daPublishMessage(messages[i]);
      }
      daScrollChatFast();
    });
    daSocket.on("chatready", function (data) {
      //var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
      //console.log('chatready');
    });
    daSocket.on("terminate", function () {
      //console.log("interview: terminating socket");
      daSocket.disconnect();
    });
    daSocket.on("controllerstart", function () {
      daBeingControlled = true;
      daShowControl("animated");
    });
    daSocket.on("controllerexit", function () {
      daBeingControlled = false;
      //console.log("Hiding control 2");
      daHideControl();
      if (daChatStatus != "on") {
        if (daSocket != null && daSocket.connected) {
          //console.log('Terminating interview socket because control over');
          daSocket.emit("terminate");
        }
      }
    });
    daSocket.on("disconnect", function () {
      //console.log("Manual disconnect");
      //daSocket.emit('manual_disconnect', {i: daYamlFilename});
      //console.log("Disconnected socket");
      //daSocket = null;
    });
    daSocket.on("reconnected", function () {
      //console.log("Reconnected");
      daChatStatus = "on";
      daDisplayChat();
      daPushChanges();
      daTurnOnChat();
      //console.log("Emitting chat_log from reconnected");
      daSocket.emit("chat_log", { i: daYamlFilename });
    });
    daSocket.on("mymessage", function (arg) {
      //console.log("Received " + arg.data);
      $("#daPushResult").html(arg.data);
    });
    daSocket.on("departure", function (arg) {
      //console.log("Departure " + arg.numpartners);
      if (arg.numpartners == 0) {
        daCloseChat();
      }
    });
    daSocket.on("chatmessage", function (arg) {
      //console.log("Received chat message " + arg.data);
      daChatHistory.push(arg.data);
      daPublishMessage(arg.data);
      daScrollChat();
      daInformAbout("chatmessage", arg.data.message);
    });
    daSocket.on("newpage", function (incoming) {
      //console.log("newpage received");
      var data = incoming.obj;
      daProcessAjax(data, $("#daform"), 1);
    });
    daSocket.on("controllerchanges", function (data) {
      //console.log("controllerchanges: " + data.parameters);
      var valArray = Object();
      var values = JSON.parse(data.parameters);
      for (var i = 0; i < values.length; i++) {
        valArray[values[i].name] = values[i].value;
      }
      //console.log("valArray is " + JSON.stringify(valArray));
      $("#daform").each(function () {
        $(this)
          .find(":input")
          .each(function () {
            var type = $(this).attr("type");
            var id = $(this).attr("id");
            var name = $(this).attr("name");
            if (type == "checkbox") {
              if (name in valArray) {
                if (valArray[name] == "True") {
                  if ($(this).prop("checked") != true) {
                    $(this).prop("checked", true);
                    $(this).trigger("change");
                  }
                } else {
                  if ($(this).prop("checked") != false) {
                    $(this).prop("checked", false);
                    $(this).trigger("change");
                  }
                }
              } else {
                if ($(this).prop("checked") != false) {
                  $(this).prop("checked", false);
                  $(this).trigger("change");
                }
              }
            } else if (type == "radio") {
              if (name in valArray) {
                if (valArray[name] == $(this).val()) {
                  if ($(this).prop("checked") != true) {
                    $(this).prop("checked", true);
                    $(this).trigger("change");
                  }
                } else {
                  if ($(this).prop("checked") != false) {
                    $(this).prop("checked", false);
                    $(this).trigger("change");
                  }
                }
              }
            } else if ($(this).data().hasOwnProperty("sliderMax")) {
              $(this).slider("setValue", parseInt(valArray[name]));
            } else {
              if (name in valArray) {
                $(this).val(valArray[name]);
              }
            }
          });
      });
      if (data.clicked) {
        //console.log("Need to click " + data.clicked);
        $(data.clicked).prop("disabled", false);
        $(data.clicked).addClass("da-click-selected");
        if (
          $(data.clicked).prop("tagName") == "A" &&
          typeof $(data.clicked).attr("href") != "undefined" &&
          ($(data.clicked).attr("href").indexOf("javascript") == 0 ||
            $(data.clicked).attr("href").indexOf("#") == 0)
        ) {
          setTimeout(function () {
            $(data.clicked).removeClass("da-click-selected");
          }, 2200);
        }
        setTimeout(function () {
          //console.log("Clicking it now");
          $(data.clicked).click();
          //console.log("Clicked it.");
        }, 200);
      }
    });
  }
}
function daUnfakeHtmlResponse(text) {
  text = text.substr(text.indexOf("ABCDABOUNDARYSTARTABC") + 21);
  text = text.substr(0, text.indexOf("ABCDABOUNDARYENDABC")).replace(/\s/g, "");
  text = atou(text);
  return text;
}
function daInjectTrim(handler) {
  return function (element, event) {
    if (
      element.tagName === "TEXTAREA" ||
      (element.tagName === "INPUT" &&
        element.type !== "password" &&
        element.type !== "date" &&
        element.type !== "datetime" &&
        element.type !== "file")
    ) {
      setTimeout(function () {
        element.value = $.trim(element.value);
      }, 10);
    }
    return handler.call(this, element, event);
  };
}
function daInvalidHandler(form, validator) {
  var errors = validator.numberOfInvalids();
  var scrollTarget = null;
  if (
    errors &&
    $(validator.errorList[0].element).parents(".da-form-group").length > 0
  ) {
    if (daJsEmbed) {
      scrollTarget =
        $(validator.errorList[0].element)
          .parents(".da-form-group")
          .first()
          .position().top - 60;
    } else {
      scrollTarget =
        $(validator.errorList[0].element)
          .parents(".da-form-group")
          .first()
          .offset().top - 60;
    }
  }
  if (scrollTarget != null) {
    if (daJsEmbed) {
      $(daTargetDiv).animate(
        {
          scrollTop: scrollTarget,
        },
        1000,
      );
    } else {
      $("html, body").animate(
        {
          scrollTop: scrollTarget,
        },
        1000,
      );
    }
  }
}
var daValidator;
var daValidationRules = {};
function daValidationHandler(form) {
  if (daObserverMode) {
    return;
  }
  //form.submit();
  //console.log("daValidationHandler");
  var visibleElements = [];
  var seen = Object();
  $(form)
    .find("input, select, textarea")
    .filter(":not(:disabled)")
    .each(function () {
      //console.log("Considering an element");
      if (
        $(this).attr("name") &&
        $(this).attr("type") != "hidden" &&
        (($(this).hasClass("da-active-invisible") &&
          $(this).parent().is(":visible")) ||
          $(this).is(":visible"))
      ) {
        var theName = $(this).attr("name");
        //console.log("Including an element " + theName);
        if (!seen.hasOwnProperty(theName)) {
          visibleElements.push(theName);
          seen[theName] = 1;
        }
      }
    });
  $(form)
    .find("input[name='_visible']")
    .val(utoa(JSON_stringify(visibleElements)));
  $(form).each(function () {
    $(this).find(":input").off("change", daOnChange);
  });
  $("meta[name=viewport]").attr(
    "content",
    "width=device-width, minimum-scale=1.0, maximum-scale=1.0, initial-scale=1.0",
  );
  if (daCheckinInterval != null) {
    clearInterval(daCheckinInterval);
  }
  daDisable = setTimeout(function () {
    $(form).find('input[type="submit"]').prop("disabled", true);
    $(form).find('button[type="submit"]').prop("disabled", true);
  }, 1);
  if (daWhichButton != null) {
    $(".da-field-buttons .btn-da").each(function () {
      if (this != daWhichButton) {
        $(this).removeClass(daAllButtonClasses);
        $(this).addClass(daButtonStyle + "light");
      }
    });
    if ($(daWhichButton).hasClass(daButtonStyle + "success")) {
      $(daWhichButton).removeClass(daButtonStyle + "success");
      $(daWhichButton).addClass(daButtonStyle + "primary");
    } else {
      $(daWhichButton).removeClass(
        daButtonStyle +
          "primary " +
          daButtonStyle +
          "info " +
          daButtonStyle +
          "warning " +
          daButtonStyle +
          "danger " +
          daButtonStyle +
          "success " +
          daButtonStyle +
          "light",
      );
      $(daWhichButton).addClass(daButtonStyle + "secondary");
    }
  }
  var tableOrder = {};
  var tableOrderChanges = {};
  $("a.datableup").each(function () {
    var tableName = $(this).data("tablename");
    if (!tableOrder.hasOwnProperty(tableName)) {
      tableOrder[tableName] = [];
    }
    tableOrder[tableName].push(parseInt($(this).data("tableitem")));
  });
  var tableChanged = false;
  for (var tableName in tableOrder) {
    if (tableOrder.hasOwnProperty(tableName)) {
      var n = tableOrder[tableName].length;
      for (var i = 0; i < n; ++i) {
        if (i != tableOrder[tableName][i]) {
          tableChanged = true;
          if (!tableOrderChanges.hasOwnProperty(tableName)) {
            tableOrderChanges[tableName] = [];
          }
          tableOrderChanges[tableName].push([tableOrder[tableName][i], i]);
        }
      }
    }
  }
  if (tableChanged) {
    $("<input>")
      .attr({
        type: "hidden",
        name: "_order_changes",
        value: JSON.stringify(tableOrderChanges),
      })
      .appendTo($(form));
  }
  var collectToDelete = [];
  $(".dacollectunremove:visible").each(function () {
    collectToDelete.push(
      parseInt($(this).parent().parent().data("collectnum")),
    );
  });
  var lastOk = parseInt(
    $(".dacollectremove:visible, .dacollectremoveexisting:visible")
      .last()
      .parent()
      .parent()
      .data("collectnum"),
  );
  $(".dacollectremove, .dacollectremoveexisting").each(function () {
    if (parseInt($(this).parent().parent().data("collectnum")) > lastOk) {
      collectToDelete.push(
        parseInt($(this).parent().parent().data("collectnum")),
      );
    }
  });
  if (collectToDelete.length > 0) {
    $("<input>")
      .attr({
        type: "hidden",
        name: "_collect_delete",
        value: JSON.stringify(collectToDelete),
      })
      .appendTo($(form));
  }
  $("select.damultiselect:not(:disabled)").each(function () {
    var showifParents = $(this).parents(".dajsshowif,.dashowif");
    if (
      showifParents.length == 0 ||
      $(showifParents[0]).data("isVisible") == "1"
    ) {
      $(this)
        .find("option")
        .each(function () {
          $("<input>")
            .attr({
              type: "hidden",
              name: $(this).val(),
              value: $(this).prop("selected") ? "True" : "False",
            })
            .appendTo($(form));
        });
    }
    $(this).prop("disabled", true);
  });
  daWhichButton = null;
  if (
    daSubmitter != null &&
    daSubmitter.name &&
    $('input[name="' + daSubmitter.name + '"]').length == 0
  ) {
    $("<input>")
      .attr({
        type: "hidden",
        name: daSubmitter.name,
        value: daSubmitter.value,
      })
      .appendTo($(form));
  }
  if (daInformedChanged) {
    $("<input>")
      .attr({
        type: "hidden",
        name: "informed",
        value: Object.keys(daInformed).join(","),
      })
      .appendTo($(form));
  }
  $("<input>")
    .attr({
      type: "hidden",
      name: "ajax",
      value: "1",
    })
    .appendTo($(form));
  daSpinnerTimeout = setTimeout(daShowSpinner, 1000);
  var do_iframe_upload = false;
  inline_succeeded = false;
  if ($('input[name="_files"]').length) {
    var filesToRead = 0;
    var filesRead = 0;
    var newFileList = Array();
    var nullFileList = Array();
    var fileArray = { keys: Array(), values: Object() };
    var file_list = JSON.parse(atou($('input[name="_files"]').val()));
    var inline_file_list = Array();
    var namesWithImages = Object();
    for (var i = 0; i < file_list.length; i++) {
      var the_file_input = $(
        "#" + file_list[i].replace(/(:|\.|\[|\]|,|=|\/|\")/g, "\\$1"),
      )[0];
      var the_max_size = $(the_file_input).data("maximagesize");
      var the_image_type = $(the_file_input).data("imagetype");
      var hasImages = false;
      if (
        typeof the_max_size != "undefined" ||
        typeof the_image_type != "undefined"
      ) {
        for (var j = 0; j < the_file_input.files.length; j++) {
          var the_file = the_file_input.files[j];
          if (the_file.type.match(/image.*/)) {
            hasImages = true;
          }
        }
      }
      if (hasImages || (daJsEmbed && the_file_input.files.length > 0)) {
        for (var j = 0; j < the_file_input.files.length; j++) {
          var the_file = the_file_input.files[j];
          filesToRead++;
        }
        inline_file_list.push(file_list[i]);
      } else if (the_file_input.files.length > 0) {
        newFileList.push(file_list[i]);
      } else {
        nullFileList.push(file_list[i]);
      }
      namesWithImages[file_list[i]] = hasImages;
    }
    if (inline_file_list.length > 0) {
      var originalFileList = atou($('input[name="_files"]').val());
      if (newFileList.length == 0 && nullFileList.length == 0) {
        $('input[name="_files"]').remove();
      } else {
        $('input[name="_files"]').val(
          utoa(JSON_stringify(newFileList.concat(nullFileList))),
        );
      }
      for (var i = 0; i < inline_file_list.length; i++) {
        fileArray.keys.push(inline_file_list[i]);
        fileArray.values[inline_file_list[i]] = Array();
        var fileInfoList = fileArray.values[inline_file_list[i]];
        var file_input = $(
          "#" + inline_file_list[i].replace(/(:|\.|\[|\]|,|=|\/|\")/g, "\\$1"),
        )[0];
        var max_size;
        var image_type;
        var image_mime_type;
        var this_has_images = false;
        if (namesWithImages[inline_file_list[i]]) {
          this_has_images = true;
          max_size = parseInt($(file_input).data("maximagesize"));
          image_type = $(file_input).data("imagetype");
          image_mime_type = null;
          if (image_type) {
            if (image_type == "png") {
              image_mime_type = "image/png";
            } else if (image_type == "bmp") {
              image_mime_type = "image/bmp";
            } else {
              image_mime_type = "image/jpeg";
              image_type = "jpg";
            }
          }
        }
        for (var j = 0; j < file_input.files.length; j++) {
          var a_file = file_input.files[j];
          var tempFunc = function (the_file, max_size, has_images) {
            var reader = new FileReader();
            var thisFileInfo = {
              name: the_file.name,
              size: the_file.size,
              type: the_file.type,
            };
            fileInfoList.push(thisFileInfo);
            reader.onload = function (readerEvent) {
              if (
                has_images &&
                the_file.type.match(/image.*/) &&
                !(the_file.type.indexOf("image/svg") == 0)
              ) {
                var convertedName = the_file.name;
                var convertedType = the_file.type;
                if (image_type) {
                  var pos = the_file.name.lastIndexOf(".");
                  convertedName =
                    the_file.name.substr(
                      0,
                      pos < 0 ? the_file.name.length : pos,
                    ) +
                    "." +
                    image_type;
                  convertedType = image_mime_type;
                  thisFileInfo.name = convertedName;
                  thisFileInfo.type = convertedType;
                }
                var image = new Image();
                image.onload = function (imageEvent) {
                  var canvas = document.createElement("canvas"),
                    width = image.width,
                    height = image.height;
                  if (width > height) {
                    if (width > max_size) {
                      height *= max_size / width;
                      width = max_size;
                    }
                  } else {
                    if (height > max_size) {
                      width *= max_size / height;
                      height = max_size;
                    }
                  }
                  canvas.width = width;
                  canvas.height = height;
                  canvas.getContext("2d").drawImage(image, 0, 0, width, height);
                  thisFileInfo["content"] = canvas.toDataURL(convertedType);
                  filesRead++;
                  if (filesRead >= filesToRead) {
                    daResumeUploadSubmission(
                      form,
                      fileArray,
                      inline_file_list,
                      newFileList,
                    );
                  }
                };
                image.src = reader.result;
              } else {
                thisFileInfo["content"] = reader.result;
                filesRead++;
                if (filesRead >= filesToRead) {
                  daResumeUploadSubmission(
                    form,
                    fileArray,
                    inline_file_list,
                    newFileList,
                  );
                }
              }
            };
            reader.readAsDataURL(the_file);
          };
          tempFunc(a_file, max_size, this_has_images);
          inline_succeeded = true;
        }
      }
    }
    if (newFileList.length == 0) {
      //$('input[name="_files"]').remove();
    } else {
      do_iframe_upload = true;
    }
  }
  if (inline_succeeded) {
    return false;
  }
  if (do_iframe_upload) {
    $("#dauploadiframe").remove();
    var iframe = $(
      '<iframe name="dauploadiframe" id="dauploadiframe" style="display: none"></iframe>',
    );
    $(daTargetDiv).append(iframe);
    $(form).attr("target", "dauploadiframe");
    iframe.bind("load", function () {
      setTimeout(function () {
        try {
          daProcessAjax(
            $.parseJSON(
              daUnfakeHtmlResponse($("#dauploadiframe").contents().text()),
            ),
            form,
            1,
          );
        } catch (e) {
          try {
            daProcessAjax(
              $.parseJSON($("#dauploadiframe").contents().text()),
              form,
              1,
            );
          } catch (f) {
            daShowErrorScreen(
              document.getElementById("dauploadiframe").contentWindow.document
                .body.innerHTML,
              f,
            );
          }
        }
      }, 0);
    });
    form.submit();
  } else {
    daRequestPending = true;
    $.ajax({
      type: "POST",
      url: daInterviewUrl,
      data: $(form).serialize(),
      beforeSend: addCsrfHeader,
      xhrFields: {
        withCredentials: true,
      },
      success: function (data) {
        setTimeout(function () {
          daProcessAjax(data, form, 1);
        }, 0);
      },
      error: function (xhr, status, error) {
        setTimeout(function () {
          daProcessAjaxError(xhr, status, error);
        }, 0);
      },
    });
  }
  return false;
}
function daSetupValidation(rules, messages) {
  daValidationRules = rules;
  daValidationRules.submitHandler = daValidationHandler;
  daValidationRules.invalidHandler = daInvalidHandler;
  daValidationRules.onfocusout = daInjectTrim($.validator.defaults.onfocusout);
  if ($("#daform").length > 0) {
    daValidator = $("#daform").validate(daValidationRules);
    if (Object.keys(messages).length > 0) {
      daValidator.showErrors(messages);
    }
  }
}
function daRecordLocation() {
  if (document.getElementById("da_track_location") == null) {
    return;
  }
  if (navigator.geolocation) {
    document.getElementById("da_track_location").value = JSON.stringify({
      error: "getCurrentPosition was still running",
    });
    navigator.geolocation.getCurrentPosition(daSetPosition, daShowError, {
      timeout: 1000,
      maximumAge: 3600000,
    });
  } else {
    document.getElementById("da_track_location").value = JSON.stringify({
      error: "navigator.geolocation not available in browser",
    });
  }
}
function daSignatureSubmit(event) {
  $(this).find("input[name='ajax']").val(1);
  daRequestPending = true;
  $.ajax({
    type: "POST",
    url: daInterviewUrl,
    data: $(this).serialize(),
    beforeSend: addCsrfHeader,
    xhrFields: {
      withCredentials: true,
    },
    success: function (data) {
      setTimeout(function () {
        daProcessAjax(data, $(this), 1);
      }, 0);
    },
    error: function (xhr, status, error) {
      setTimeout(function () {
        daProcessAjaxError(xhr, status, error);
      }, 0);
    },
  });
  event.preventDefault();
  event.stopPropagation();
  return false;
}
function JSON_stringify(s) {
  var json = JSON.stringify(s);
  return json.replace(/[\u007f-\uffff]/g, function (c) {
    return "\\u" + ("0000" + c.charCodeAt(0).toString(16)).slice(-4);
  });
}
function daResumeUploadSubmission(
  form,
  fileArray,
  inline_file_list,
  newFileList,
) {
  $("<input>")
    .attr({
      type: "hidden",
      name: "_files_inline",
      value: utoa(JSON_stringify(fileArray)),
    })
    .appendTo($(form));
  for (var i = 0; i < inline_file_list.length; ++i) {
    document.getElementById(inline_file_list[i]).disabled = true;
  }
  if (newFileList.length > 0) {
    $("#dauploadiframe").remove();
    var iframe = $(
      '<iframe name="dauploadiframe" id="dauploadiframe" style="display: none"></iframe>',
    );
    $(daTargetDiv).append(iframe);
    $(form).attr("target", "dauploadiframe");
    iframe.bind("load", function () {
      setTimeout(function () {
        daProcessAjax(
          $.parseJSON($("#dauploadiframe").contents().text()),
          form,
          1,
        );
      }, 0);
    });
    form.submit();
  } else {
    daRequestPending = true;
    $.ajax({
      type: "POST",
      url: daInterviewUrl,
      data: $(form).serialize(),
      beforeSend: addCsrfHeader,
      xhrFields: {
        withCredentials: true,
      },
      success: function (data) {
        setTimeout(function () {
          daProcessAjax(data, form, 1);
        }, 0);
      },
      error: function (xhr, status, error) {
        setTimeout(function () {
          daProcessAjaxError(xhr, status, error);
        }, 0);
      },
    });
  }
}
function daOnChange() {
  if (daObserverMode) {
    return;
  }
  if (daCheckinSeconds == 0 || daShowIfInProcess) {
    return true;
  }
  if (daCheckinInterval != null) {
    clearInterval(daCheckinInterval);
  }
  var oThis = this;
  daCheckin(oThis);
  daCheckinInterval = setInterval(daCheckin, daCheckinSeconds);
  return true;
}
function daPushChanges() {
  //console.log("daPushChanges");
  if (daObserverMode) {
    if (daObserverChangesInterval != null) {
      clearInterval(daObserverChangesInterval);
    }
    if (!daSendChanges || !daConnected) {
      return;
    }
    daObserverChangesInterval = setInterval(daPushChanges, daCheckinSeconds);
    daSocket.emit("observerChanges", {
      uid: daUid,
      i: daYamlFilename,
      userid: daUserObserved,
      parameters: JSON.stringify($("#daform").serializeArray()),
    });
    return;
  }
  if (daCheckinSeconds == 0 || daShowIfInProcess) {
    return true;
  }
  if (daCheckinInterval != null) {
    clearInterval(daCheckinInterval);
  }
  daCheckin(null);
  daCheckinInterval = setInterval(daCheckin, daCheckinSeconds);
  return true;
}
function daProcessAjaxError(xhr, status, error) {
  daRequestPending = false;
  if (
    xhr.responseType == undefined ||
    xhr.responseType == "" ||
    xhr.responseType == "text"
  ) {
    var theHtml = xhr.responseText;
    if (theHtml == undefined) {
      $(daTargetDiv).html("error");
    } else {
      var newDiv = document.createElement("div");
      $(newDiv).html(theHtml);
      var daDivs = $(newDiv).children("div");
      if (daDivs.length > 0) {
        $(daTargetDiv).empty();
        for (var i = 0; i < daDivs.length; i++) {
          $(daTargetDiv).append(daDivs[i]);
        }
        var otherScripts = $(newDiv).children("script");
        if (otherScripts.length > 0) {
          for (var i = 0; i < otherScripts.length; i++) {
            var theHtml = $(otherScripts[i]).html();
            if (theHtml.startsWith("Object.assign")) {
              eval(theHtml);
            }
          }
        }
        if (daErrorScript) {
          var errorScriptDiv = document.createElement("div");
          $(errorScriptDiv).html(daErrorScript);
          var daScripts = $(errorScriptDiv).find("script");
          if (daScripts.length > 0) {
            for (var i = 0; i < daScripts.length; i++) {
              var theHtml = $(daScripts[i]).html();
              if (theHtml) {
                eval(theHtml);
              } else {
                var scriptElement = document.createElement("script");
                scriptElement.src = $(daScripts[i]).attr("src");
                document.body.appendChild(scriptElement);
              }
            }
          }
          delete errorScriptDiv;
        }
        $("#da-retry").on("click", function (e) {
          location.reload();
          e.preventDefault();
          return false;
        });
        daShowNotifications();
        $(document).trigger("daPageError");
      } else {
        $(daTargetDiv).html(theHtml);
      }
      delete newDiv;
    }
    if (daJsEmbed) {
      $(daTargetDiv)[0].scrollTo(0, 1);
    } else {
      window.scrollTo(0, 1);
    }
  } else {
    console.log("daProcessAjaxError: response was not text");
  }
}
function daAddScriptToHead(src) {
  var head = document.getElementsByTagName("head")[0];
  var script = document.createElement("script");
  script.src = src;
  script.async = true;
  script.defer = true;
  head.appendChild(script);
}
$(document).on("keydown", function (e) {
  if (e.which == 13) {
    if (daShowingHelp == 0) {
      var tag = $(document.activeElement).prop("tagName");
      if (
        tag != "INPUT" &&
        tag != "TEXTAREA" &&
        tag != "A" &&
        tag != "LABEL" &&
        tag != "BUTTON"
      ) {
        e.preventDefault();
        e.stopPropagation();
        if (
          $("#daform .da-field-buttons button").not(".danonsubmit").length == 1
        ) {
          $("#daform .da-field-buttons button").not(".danonsubmit").click();
        }
        return false;
      }
    }
    if ($(document.activeElement).hasClass("btn-file")) {
      e.preventDefault();
      e.stopPropagation();
      $(document.activeElement).find("input").click();
      return false;
    }
  }
});
function daShowErrorScreen(data, error) {
  console.log("daShowErrorScreen: " + error);
  if ("activeElement" in document) {
    document.activeElement.blur();
  }
  $(daTargetDiv).html(data);
}
function daEvalExtraScript(info) {
  switch (info.type) {
    case "custom":
      daGlobalEval(info.script);
      break;
    case "listeners":
      daAddListenersFor(info.element);
      break;
    case "enable_tracking":
      daTrackingEnabled = true;
      break;
    case "autocomplete":
      daInitAutocomplete(info.info);
      break;
    case "autocomplete_old":
      daInitAutocompleteOld(info.info);
      break;
    case "map":
      daInitMap(info.maps);
      break;
    case "validation":
      daSetupValidation(info.rules, info.messages);
      break;
    case "slider":
      $("#" + info.id).slider({ tooltip: "always", enabled: info.enabled });
      break;
    case "signature":
      daInitializeSignature(info.color, info.default);
      break;
  }
}
function daProcessAjax(data, form, doScroll, actionURL) {
  daRequestPending = false;
  daInformedChanged = false;
  if (daDisable != null) {
    clearTimeout(daDisable);
  }
  daCsrf = data.csrf_token;
  if (data.question_data) {
    daQuestionData = data.question_data;
  }
  if (data.action == "body") {
    if (daShouldForceFullScreen) {
      daForceFullScreen(data);
    }
    if ("activeElement" in document) {
      document.activeElement.blur();
    }
    $(daTargetDiv).html("");
    if (daJsEmbed) {
      $(daTargetDiv)[0].scrollTo(0, 1);
    } else {
      window.scrollTo(0, 1);
    }
    $(daTargetDiv).html(data.body);
    $(daTargetDiv).parent().removeClass();
    $(daTargetDiv).parent().addClass(data.bodyclass);
    $("meta[name=viewport]").attr(
      "content",
      "width=device-width, initial-scale=1",
    );
    daDoAction = data.do_action;
    //daNextAction = data.next_action;
    daChatAvailable = data.livehelp.availability;
    daChatMode = data.livehelp.mode;
    daChatRoles = data.livehelp.roles;
    daChatPartnerRoles = data.livehelp.partner_roles;
    daSteps = data.steps;
    //console.log("daProcessAjax: pushing " + daSteps);
    if (!daJsEmbed && !daIframeEmbed) {
      if (history.state != null && daSteps > history.state.steps) {
        history.pushState(
          { steps: daSteps },
          data.browser_title + " - page " + daSteps,
          daLocationBar + daPageSep + daSteps,
        );
      } else {
        history.replaceState(
          { steps: daSteps },
          "",
          daLocationBar + daPageSep + daSteps,
        );
      }
    }
    daAllowGoingBack = data.allow_going_back;
    daQuestionID = data.id_dict;
    daMessageLog = data.message_log;
    daInitialize(doScroll);
    //var tempDiv = document.createElement("div");
    //tempDiv.innerHTML = data.extra_scripts;
    //var scripts = tempDiv.getElementsByTagName("script");
    //for (var i = 0; i < scripts.length; i++) {
    for (var i = 0; i < data.extra_scripts.length; i++) {
      //console.log("Found one script");
      //if (script[i].src != "") {
      //console.log("Added script to head");
      //daAddScriptToHead(scripts[i].src);
      //} else {
      //daGlobalEval(scripts[i].innerHTML);
      //}
      daEvalExtraScript(data.extra_scripts[i]);
    }
    $(".da-group-has-error").each(function () {
      if ($(this).is(":visible")) {
        if (daJsEmbed) {
          var scrollToTarget = $(this).position().top - 60;
          setTimeout(function () {
            $(daTargetDiv).animate({ scrollTop: scrollToTarget }, 1000);
          }, 100);
        } else {
          var scrollToTarget = $(this).offset().top - 60;
          setTimeout(function () {
            $(daTargetDiv)
              .parent()
              .parent()
              .animate({ scrollTop: scrollToTarget }, 1000);
          }, 100);
        }
        return false;
      }
    });
    for (var i = 0; i < data.extra_css.length; i++) {
      $("head").append(data.extra_css[i]);
    }
    document.title = data.browser_title;
    if ($("html").attr("lang") != data.lang) {
      $("html").attr("lang", data.lang);
    }
    if (daTrackingEnabled) {
      daRecordLocation();
    }
    $(document).trigger("daPageLoad");
    if (daReloader != null) {
      clearTimeout(daReloader);
    }
    if (data.reload_after != null && data.reload_after > 0) {
      //daReloader = setTimeout(function(){location.reload();}, data.reload_after);
      daReloader = setTimeout(function () {
        daRefreshSubmit();
      }, data.reload_after);
    }
    daUpdateHeight();
  } else if (data.action == "redirect") {
    if (daSpinnerTimeout != null) {
      clearTimeout(daSpinnerTimeout);
      daSpinnerTimeout = null;
    }
    if (daShowingSpinner) {
      daHideSpinner();
    }
    window.location = data.url;
  } else if (data.action == "refresh") {
    daRefreshSubmit();
  } else if (data.action == "reload") {
    location.reload(true);
  } else if (data.action == "resubmit") {
    if (form == null) {
      window.location = actionURL;
    }
    $("input[name='ajax']").remove();
    if (
      daSubmitter != null &&
      daSubmitter.name &&
      $('input[name="' + daSubmitter.name + '"]').length == 0
    ) {
      var input = $("<input>")
        .attr("type", "hidden")
        .attr("name", daSubmitter.name)
        .val(daSubmitter.value);
      $(form).append($(input));
    }
    form.submit();
  }
}
function daEmbeddedJs(e) {
  //console.log("using embedded js");
  var data = decodeURIComponent($(this).data("js"));
  daGlobalEval(data);
  e.preventDefault();
  return false;
}
function daEmbeddedAction(e) {
  if (daRequestPending) {
    e.preventDefault();
    $(this).blur();
    return false;
  }
  if ($(this).hasClass("daremovebutton")) {
    if (confirm(daAreYouSure)) {
      return true;
    }
    e.preventDefault();
    $(this).blur();
    return false;
  }
  var actionData = decodeURIComponent($(this).data("embaction"));
  var theURL = $(this).attr("href");
  daRequestPending = true;
  $.ajax({
    type: "POST",
    url: daInterviewUrl,
    data: $.param({ _action: actionData, csrf_token: daCsrf, ajax: 1 }),
    beforeSend: addCsrfHeader,
    xhrFields: {
      withCredentials: true,
    },
    success: function (data) {
      setTimeout(function () {
        daProcessAjax(data, null, 1, theURL);
      }, 0);
    },
    error: function (xhr, status, error) {
      setTimeout(function () {
        daProcessAjaxError(xhr, status, error);
      }, 0);
    },
    dataType: "json",
  });
  daSpinnerTimeout = setTimeout(daShowSpinner, 1000);
  e.preventDefault();
  return false;
}
function daReviewAction(e) {
  if (daRequestPending) {
    e.preventDefault();
    $(this).blur();
    return false;
  }
  //action_perform_with_next($(this).data('action'), null, daNextAction);
  var info = $.parseJSON(atou($(this).data("action")));
  da_action_perform(info["action"], info["arguments"]);
  e.preventDefault();
  return false;
}
function daRingChat() {
  daChatStatus = "ringing";
  daPushChanges();
}
function daTurnOnChat() {
  //console.log("Publishing from daTurnOnChat");
  $("#daChatOnButton").addClass("dainvisible");
  $("#daChatBox").removeClass("dainvisible");
  $("#daCorrespondence").html("");
  for (var i = 0; i < daChatHistory.length; i++) {
    daPublishMessage(daChatHistory[i]);
  }
  daScrollChatFast();
  $("#daMessage").prop("disabled", false);
  if (daShowingHelp) {
    $("#daMessage").focus();
  }
}
function daCloseChat() {
  //console.log('daCloseChat');
  daChatStatus = "hangup";
  daPushChanges();
  if (daSocket != null && daSocket.connected) {
    daSocket.disconnect();
  }
}
// function daTurnOffChat(){
//   $("#daChatOnButton").removeClass("dainvisible");
//   $("#daChatBox").addClass("dainvisible");
//   //daCloseSocket();
//   $("#daMessage").prop('disabled', true);
//   $("#daSend").unbind();
//   //daStartCheckingIn();
// }
function daDisplayChat() {
  if (daChatStatus == "off" || daChatStatus == "observeonly") {
    $("#daChatBox").addClass("dainvisible");
    $("#daChatAvailable").addClass("dainvisible");
    $("#daChatOnButton").addClass("dainvisible");
  } else {
    if (daChatStatus == "waiting") {
      if (daChatPartnersAvailable > 0) {
        $("#daChatBox").removeClass("dainvisible");
      }
    } else {
      $("#daChatBox").removeClass("dainvisible");
    }
  }
  if (daChatStatus == "waiting") {
    //console.log("I see waiting")
    if (daChatHistory.length > 0) {
      $("#daChatAvailable a i").removeClass("da-chat-active");
      $("#daChatAvailable a i").addClass("da-chat-inactive");
      $("#daChatAvailable").removeClass("dainvisible");
    } else {
      $("#daChatAvailable a i").removeClass("da-chat-active");
      $("#daChatAvailable a i").removeClass("da-chat-inactive");
      $("#daChatAvailable").addClass("dainvisible");
    }
    $("#daChatOnButton").addClass("dainvisible");
    $("#daChatOffButton").addClass("dainvisible");
    $("#daMessage").prop("disabled", true);
    $("#daSend").prop("disabled", true);
  }
  if (daChatStatus == "standby" || daChatStatus == "ready") {
    //console.log("I see standby")
    $("#daChatAvailable").removeClass("dainvisible");
    $("#daChatAvailable a i").removeClass("da-chat-inactive");
    $("#daChatAvailable a i").addClass("da-chat-active");
    $("#daChatOnButton").removeClass("dainvisible");
    $("#daChatOffButton").addClass("dainvisible");
    $("#daMessage").prop("disabled", true);
    $("#daSend").prop("disabled", true);
    daInformAbout("chat");
  }
  if (daChatStatus == "on") {
    $("#daChatAvailable").removeClass("dainvisible");
    $("#daChatAvailable a i").removeClass("da-chat-inactive");
    $("#daChatAvailable a i").addClass("da-chat-active");
    $("#daChatOnButton").addClass("dainvisible");
    $("#daChatOffButton").removeClass("dainvisible");
    $("#daMessage").prop("disabled", false);
    if (daShowingHelp) {
      $("#daMessage").focus();
    }
    $("#daSend").prop("disabled", false);
    daInformAbout("chat");
  }
  hideTablist();
}
function daChatLogCallback(data) {
  if (data.action && data.action == "reload") {
    location.reload(true);
  }
  //console.log("daChatLogCallback: success is " + data.success);
  if (data.success) {
    $("#daCorrespondence").html("");
    daChatHistory = [];
    var messages = data.messages;
    for (var i = 0; i < messages.length; ++i) {
      daChatHistory.push(messages[i]);
      daPublishMessage(messages[i]);
    }
    daDisplayChat();
    daScrollChatFast();
  }
}
function daRefreshSubmit() {
  daRequestPending = true;
  $.ajax({
    type: "POST",
    url: daInterviewUrl,
    data: "csrf_token=" + daCsrf + "&ajax=1",
    beforeSend: addCsrfHeader,
    xhrFields: {
      withCredentials: true,
    },
    success: function (data) {
      setTimeout(function () {
        daProcessAjax(data, $("#daform"), 0);
      }, 0);
    },
    error: function (xhr, status, error) {
      setTimeout(function () {
        daProcessAjaxError(xhr, status, error);
      }, 0);
    },
  });
}
function daResetCheckinCode() {
  daCheckinCode = Math.random();
}
function daCheckinCallback(data) {
  if (data.action && data.action == "reload") {
    location.reload(true);
  }
  daCheckingIn = 0;
  //console.log("daCheckinCallback: success is " + data.success);
  if (data.checkin_code != daCheckinCode) {
    console.log("Ignoring checkincallback because code is wrong");
    return;
  }
  if (data.success) {
    if (data.commands.length > 0) {
      for (var i = 0; i < data.commands.length; ++i) {
        var command = data.commands[i];
        if (command.extra == "flash") {
          if (!$("#daflash").length) {
            $(daTargetDiv).append(daSprintf(daNotificationContainer, ""));
          }
          $("#daflash").append(
            daSprintf(daNotificationMessage, "info", command.value),
          );
          //console.log("command is " + command.value);
        } else if (command.extra == "refresh") {
          daRefreshSubmit();
        } else if (command.extra == "javascript") {
          //console.log("I should eval" + command.value);
          daGlobalEval(command.value);
        } else if (command.extra == "fields") {
          for (var key in command.value) {
            if (command.value.hasOwnProperty(key)) {
              if (
                typeof command.value[key] === "object" &&
                command.value[key] !== null
              ) {
                if (command.value[key].hasOwnProperty("choices")) {
                  daSetChoices(key, command.value[key]["choices"]);
                }
                if (command.value[key].hasOwnProperty("value")) {
                  daSetField(key, command.value[key]["value"]);
                }
              } else {
                daSetField(key, command.value[key]);
              }
            }
          }
        } else if (command.extra == "backgroundresponse") {
          var assignments = Array();
          if (
            command.value.hasOwnProperty("target") &&
            command.value.hasOwnProperty("content")
          ) {
            assignments.push({
              target: command.value.target,
              content: command.value.content,
            });
          }
          if (Array.isArray(command.value)) {
            for (i = 0; i < command.value.length; ++i) {
              var possible_assignment = command.value[i];
              if (
                possible_assignment.hasOwnProperty("target") &&
                possible_assignment.hasOwnProperty("content")
              ) {
                assignments.push({
                  target: possible_assignment.target,
                  content: possible_assignment.content,
                });
              }
            }
          }
          for (i = 0; i < assignments.length; ++i) {
            var assignment = assignments[i];
            $(".datarget" + assignment.target.replace(/[^A-Za-z0-9\_]/g)).prop(
              "innerHTML",
              assignment.content,
            );
          }
          //console.log("Triggering daCheckIn");
          $(document).trigger("daCheckIn", [command.action, command.value]);
        }
      }
      // setTimeout(function(){
      //   $("#daflash .daalert-interlocutory").hide(300, function(){
      //     $(self).remove();
      //   });
      // }, 5000);
    }
    oldDaChatStatus = daChatStatus;
    //console.log("daCheckinCallback: from " + daChatStatus + " to " + data.chat_status);
    if (data.phone == null) {
      $("#daPhoneMessage").addClass("dainvisible");
      $("#daPhoneMessage p").html("");
      $("#daPhoneAvailable").addClass("dainvisible");
      daPhoneAvailable = false;
    } else {
      $("#daPhoneMessage").removeClass("dainvisible");
      $("#daPhoneMessage p").html(data.phone);
      $("#daPhoneAvailable").removeClass("dainvisible");
      daPhoneAvailable = true;
      daInformAbout("phone");
    }
    var statusChanged;
    if (daChatStatus == data.chat_status) {
      statusChanged = false;
    } else {
      statusChanged = true;
    }
    if (statusChanged) {
      daChatStatus = data.chat_status;
      daDisplayChat();
      if (daChatStatus == "ready") {
        // console.log("calling initialize socket because ready");
        daInitializeSocket();
      }
    }
    daChatPartnersAvailable = 0;
    if (daChatMode == "peer" || daChatMode == "peerhelp") {
      daChatPartnersAvailable += data.num_peers;
      if (data.num_peers == 1) {
        $("#dapeerMessage").html(
          '<span class="badge bg-info">' +
            data.num_peers +
            " " +
            daOtherUser +
            "</span>",
        );
      } else {
        $("#dapeerMessage").html(
          '<span class="badge bg-info">' +
            data.num_peers +
            " " +
            daOtherUsers +
            "</span>",
        );
      }
      $("#dapeerMessage").removeClass("dainvisible");
    } else {
      $("#dapeerMessage").addClass("dainvisible");
    }
    if (daChatMode == "peerhelp" || daChatMode == "help") {
      if (data.help_available == 1) {
        $("#dapeerHelpMessage").html(
          '<span class="badge bg-primary">' +
            data.help_available +
            " " +
            daOperator +
            "</span>",
        );
      } else {
        $("#dapeerHelpMessage").html(
          '<span class="badge bg-primary">' +
            data.help_available +
            " " +
            daOperators +
            "</span>",
        );
      }
      $("#dapeerHelpMessage").removeClass("dainvisible");
    } else {
      $("#dapeerHelpMessage").addClass("dainvisible");
    }
    if (daBeingControlled) {
      if (!data.observerControl) {
        daBeingControlled = false;
        //console.log("Hiding control 1");
        daHideControl();
        if (daChatStatus != "on") {
          if (daSocket != null && daSocket.connected) {
            //console.log('Terminating interview socket because control is over');
            daSocket.emit("terminate");
          }
        }
      }
    } else {
      if (data.observerControl) {
        daBeingControlled = true;
        daInitializeSocket();
      }
    }
  }
  hideTablist();
}
function daCheckoutCallback(data) {}
function daInitialCheckin() {
  daCheckin("initial");
}
function daCheckin(elem) {
  //console.log("daCheckin");
  var elem = typeof elem === "undefined" ? null : elem;
  daCheckingIn += 1;
  //if (daCheckingIn > 1 && !(daCheckingIn % 3)){
  if (elem === null && daCheckingIn > 1) {
    //console.log("daCheckin: request already pending, not re-sending");
    return;
  }
  var datastring;
  if (daChatStatus != "off" && $("#daform").length > 0 && !daBeingControlled) {
    if (daDoAction != null) {
      datastring = $.param({
        action: "checkin",
        chatstatus: daChatStatus,
        chatmode: daChatMode,
        csrf_token: daCsrf,
        checkinCode: daCheckinCode,
        parameters: daFormAsJSON(elem),
        raw_parameters: JSON.stringify($("#daform").serializeArray()),
        do_action: daDoAction,
        ajax: "1",
      });
    } else {
      datastring = $.param({
        action: "checkin",
        chatstatus: daChatStatus,
        chatmode: daChatMode,
        csrf_token: daCsrf,
        checkinCode: daCheckinCode,
        parameters: daFormAsJSON(elem),
        raw_parameters: JSON.stringify($("#daform").serializeArray()),
        ajax: "1",
      });
    }
  } else {
    if (daDoAction != null) {
      datastring = $.param({
        action: "checkin",
        chatstatus: daChatStatus,
        chatmode: daChatMode,
        csrf_token: daCsrf,
        checkinCode: daCheckinCode,
        do_action: daDoAction,
        parameters: daFormAsJSON(elem),
        ajax: "1",
      });
    } else {
      datastring = $.param({
        action: "checkin",
        chatstatus: daChatStatus,
        chatmode: daChatMode,
        csrf_token: daCsrf,
        checkinCode: daCheckinCode,
        ajax: "1",
      });
    }
  }
  //console.log("Doing checkin with " + daChatStatus);
  $.ajax({
    type: "POST",
    url: daCheckinUrl,
    beforeSend: addCsrfHeader,
    xhrFields: {
      withCredentials: true,
    },
    data: datastring,
    success: daCheckinCallback,
    dataType: "json",
  });
  return true;
}
function daCheckout() {
  $.ajax({
    type: "POST",
    url: daCheckoutUrl,
    beforeSend: addCsrfHeader,
    xhrFields: {
      withCredentials: true,
    },
    data: "csrf_token=" + daCsrf + "&ajax=1&action=checkout",
    success: daCheckoutCallback,
    dataType: "json",
  });
  return true;
}
function daStopCheckingIn() {
  daCheckout();
  if (daCheckinInterval != null) {
    clearInterval(daCheckinInterval);
  }
}
function daShowSpinner() {
  if ($("#daquestion").length > 0) {
    $(
      '<div id="daSpinner" class="da-spinner-container da-top-for-navbar"><div class="container"><div class="row"><div class="col text-center"><span class="da-spinner"><i class="fa-solid fa-spinner fa-spin"></i></span></div></div></div></div>',
    ).appendTo(daTargetDiv);
  } else {
    var newSpan = document.createElement("span");
    var newI = document.createElement("i");
    $(newI).addClass("fa-solid fa-spinner fa-spin");
    $(newI).appendTo(newSpan);
    $(newSpan).attr("id", "daSpinner");
    $(newSpan).addClass("da-sig-spinner da-top-for-navbar");
    $(newSpan).appendTo("#dasigtoppart");
  }
  daShowingSpinner = true;
}
function daHideSpinner() {
  $("#daSpinner").remove();
  daShowingSpinner = false;
  daSpinnerTimeout = null;
}
function daObserverSubmitter(event) {
  if (!daSendChanges || !daConnected) {
    event.preventDefault();
    return false;
  }
  var theAction = null;
  if ($(this).hasClass("da-review-action")) {
    theAction = $(this).data("action");
  }
  var embeddedJs = $(this).data("js");
  var embeddedAction = $(this).data("embaction");
  var linkNum = $(this).data("linknum");
  var theId = $(this).attr("id");
  if (theId == "dapagetitle") {
    theId = "daquestionlabel";
  }
  var theName = $(this).attr("name");
  var theValue = $(this).val();
  var skey;
  if (linkNum) {
    skey = 'a[data-linknum="' + linkNum + '"]';
  } else if (embeddedAction) {
    skey =
      'a[data-embaction="' +
      embeddedAction.replace(/(:|\.|\[|\]|,|=|\/|\")/g, "\\$1") +
      '"]';
  } else if (theAction) {
    skey =
      'a[data-action="' +
      theAction.replace(/(:|\.|\[|\]|,|=|\/|\")/g, "\\$1") +
      '"]';
  } else if (theId) {
    skey = "#" + theId.replace(/(:|\.|\[|\]|,|=|\/|\")/g, "\\$1");
  } else if (theName) {
    skey =
      "#" +
      $(this).parents("form").attr("id") +
      " " +
      $(this).prop("tagName").toLowerCase() +
      '[name="' +
      theName.replace(/(:|\.|\[|\]|,|=|\/)/g, "\\$1") +
      '"]';
    if (typeof theValue !== "undefined") {
      skey += '[value="' + theValue + '"]';
    }
  } else {
    skey =
      "#" +
      $(this).parents("form").attr("id") +
      " " +
      $(this).prop("tagName").toLowerCase() +
      '[type="submit"]';
  }
  //console.log("Need to click on " + skey);
  if (
    daObserverChangesInterval != null &&
    embeddedJs == null &&
    theId != "dabackToQuestion" &&
    theId != "dahelptoggle" &&
    theId != "daquestionlabel"
  ) {
    clearInterval(daObserverChangesInterval);
  }
  daSocket.emit("observerChanges", {
    uid: daUid,
    i: daYamlFilename,
    userid: daUserObserved,
    clicked: skey,
    parameters: JSON.stringify($("#daform").serializeArray()),
  });
  if (embeddedJs != null) {
    //console.log("Running the embedded js");
    daGlobalEval(decodeURIComponent(embeddedJs));
  }
  if (
    theId != "dabackToQuestion" &&
    theId != "dahelptoggle" &&
    theId != "daquestionlabel"
  ) {
    event.preventDefault();
    return false;
  }
}
function daAdjustInputWidth(e) {
  var contents = $(this).val();
  var leftBracket = new RegExp("<", "g");
  var rightBracket = new RegExp(">", "g");
  contents = contents
    .replace(/&/g, "&amp;")
    .replace(leftBracket, "&lt;")
    .replace(rightBracket, "&gt;")
    .replace(/ /g, "&nbsp;");
  $('<span class="dainput-embedded" id="dawidth">')
    .html(contents)
    .appendTo("#daquestion");
  $("#dawidth").css("min-width", $(this).css("min-width"));
  $("#dawidth").css("background-color", $(daTargetDiv).css("background-color"));
  $("#dawidth").css("color", $(daTargetDiv).css("background-color"));
  $(this).width($("#dawidth").width() + 16);
  setTimeout(function () {
    $("#dawidth").remove();
  }, 0);
}
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
function daIgnoreAllButTab(event) {
  event = event || window.event;
  var code = event.keyCode;
  if (code != 9) {
    if (code == 13) {
      $(event.target)
        .parents(".file-caption-main")
        .find("input.dafile")
        .click();
    }
    event.preventDefault();
    return false;
  }
}
function daDisableIfNotHidden(query, value) {
  $(query).each(function () {
    var showIfParent = $(this).parents(".dashowif, .dajsshowif");
    if (
      !(
        showIfParent.length &&
        ($(showIfParent[0]).data("isVisible") == "0" ||
          !$(showIfParent[0]).is(":visible"))
      )
    ) {
      if (
        $(this).prop("tagName") == "INPUT" &&
        $(this).hasClass("combobox") &&
        daComboBoxes[$(this).attr("id")]
      ) {
        if (value) {
          daComboBoxes[$(this).attr("id")].disable();
        } else {
          daComboBoxes[$(this).attr("id")].enable();
        }
      } else if ($(this).hasClass("dafile")) {
        if (value) {
          $(this).data("fileinput").disable();
        } else {
          $(this).data("fileinput").enable();
        }
      } else if ($(this).hasClass("daslider")) {
        if (value) {
          $(this).slider("disable");
        } else {
          $(this).slider("enable");
        }
      } else {
        $(this).prop("disabled", value);
      }
      if (value) {
        $(this).parents(".da-form-group").addClass("dagreyedout");
      } else {
        $(this).parents(".da-form-group").removeClass("dagreyedout");
      }
    }
  });
}
function daShowIfCompare(theVal, showIfVal) {
  if (typeof theVal == "string" && theVal.match(/^-?\d+\.\d+$/)) {
    theVal = parseFloat(theVal);
  } else if (typeof theVal == "string" && theVal.match(/^-?\d+$/)) {
    theVal = parseInt(theVal);
  }
  if (typeof showIfVal == "string" && showIfVal.match(/^-?\d+\.\d+$/)) {
    showIfVal = parseFloat(showIfVal);
  } else if (typeof showIfVal == "string" && showIfVal.match(/^-?\d+$/)) {
    showIfVal = parseInt(showIfVal);
  }
  if (typeof theVal == "string" || typeof showIfVal == "string") {
    if (
      String(showIfVal) == "None" &&
      (String(theVal) == "" || theVal === null)
    ) {
      return true;
    }
    return String(theVal) == String(showIfVal);
  }
  return theVal == showIfVal;
}
function rationalizeListCollect() {
  var finalNum = $(".dacollectextraheader").last().data("collectnum");
  var num = $(".dacollectextraheader:visible").last().data("collectnum");
  if (parseInt(num) < parseInt(finalNum)) {
    if (
      $('div.dacollectextraheader[data-collectnum="' + num + '"]')
        .find(".dacollectadd")
        .hasClass("dainvisible")
    ) {
      $('div.dacollectextraheader[data-collectnum="' + (num + 1) + '"]').show(
        "fast",
      );
    }
  }
  var n = parseInt(finalNum);
  var firstNum = parseInt(
    $(".dacollectextraheader").first().data("collectnum"),
  );
  while (n-- > firstNum) {
    if (
      $('div.dacollectextraheader[data-collectnum="' + (n + 1) + '"]:visible')
        .length > 0
    ) {
      if (
        !$('div.dacollectextraheader[data-collectnum="' + (n + 1) + '"]')
          .find(".dacollectadd")
          .hasClass("dainvisible") &&
        $('div.dacollectextraheader[data-collectnum="' + n + '"]')
          .find(".dacollectremove")
          .hasClass("dainvisible")
      ) {
        $('div.dacollectextraheader[data-collectnum="' + (n + 1) + '"]').hide();
      }
    }
  }
  var n = parseInt(finalNum);
  var seenAddAnother = false;
  while (n-- > firstNum) {
    if (
      $('div.dacollectextraheader[data-collectnum="' + (n + 1) + '"]:visible')
        .length > 0
    ) {
      if (
        !$('div.dacollectextraheader[data-collectnum="' + (n + 1) + '"]')
          .find(".dacollectadd")
          .hasClass("dainvisible")
      ) {
        seenAddAnother = true;
      }
      var current = $('div.dacollectextraheader[data-collectnum="' + n + '"]');
      if (
        seenAddAnother &&
        !$(current).find(".dacollectadd").hasClass("dainvisible")
      ) {
        $(current).find(".dacollectadd").addClass("dainvisible");
        $(current).find(".dacollectunremove").removeClass("dainvisible");
      }
    }
  }
}
function daFetchAjax(elem, cb, doShow) {
  var wordStart = $(elem).val();
  if (wordStart.length < parseInt(cb.$source.data("trig"))) {
    if (cb.shown) {
      cb.hide();
    }
    return;
  }
  if (daFetchAjaxTimeout != null && daFetchAjaxTimeoutRunning) {
    daFetchAjaxTimeoutFetchAfter = true;
    return;
  }
  if (doShow) {
    daFetchAjaxTimeout = setTimeout(function () {
      daFetchAjaxTimeoutRunning = false;
      if (daFetchAjaxTimeoutFetchAfter) {
        daFetchAjax(elem, cb, doShow);
        daFetchAjaxTimeoutFetchAfter = false;
      }
    }, 2000);
    daFetchAjaxTimeoutRunning = true;
    daFetchAjaxTimeoutFetchAfter = false;
  }
  da_action_call(
    cb.$source.data("action"),
    { wordstart: wordStart },
    function (data) {
      wordStart = $(elem).val();
      if (typeof data == "object") {
        var upperWordStart = wordStart.toUpperCase();
        cb.$source.empty();
        var emptyItem = $("<option>");
        emptyItem.val("");
        emptyItem.text("");
        cb.$source.append(emptyItem);
        var notYetSelected = true;
        var selectedValue = null;
        if (Array.isArray(data)) {
          for (var i = 0; i < data.length; ++i) {
            if (Array.isArray(data[i])) {
              if (data[i].length >= 2) {
                var item = $("<option>");
                if (
                  notYetSelected &&
                  ((doShow && data[i][1].toString() == wordStart) ||
                    data[i][0].toString() == wordStart)
                ) {
                  item.prop("selected", true);
                  notYetSelected = false;
                  selectedValue = data[i][1];
                }
                item.text(data[i][1]);
                item.val(data[i][0]);
                cb.$source.append(item);
              } else if (data[i].length == 1) {
                var item = $("<option>");
                if (
                  notYetSelected &&
                  ((doShow && data[i][0].toString() == wordStart) ||
                    data[i][0].toString() == wordStart)
                ) {
                  item.prop("selected", true);
                  notYetSelected = false;
                  selectedValue = data[i][0];
                }
                item.text(data[i][0]);
                item.val(data[i][0]);
                cb.$source.append(item);
              }
            } else if (typeof data[i] == "object") {
              for (var key in data[i]) {
                if (data[i].hasOwnProperty(key)) {
                  var item = $("<option>");
                  if (
                    notYetSelected &&
                    ((doShow && key.toString() == wordStart) ||
                      key.toString() == wordStart)
                  ) {
                    item.prop("selected", true);
                    notYetSelected = false;
                    selectedValue = data[i][key];
                  }
                  item.text(data[i][key]);
                  item.val(key);
                  cb.$source.append(item);
                }
              }
            } else {
              var item = $("<option>");
              if (
                notYetSelected &&
                ((doShow &&
                  data[i].toString().toUpperCase() == upperWordStart) ||
                  data[i].toString() == wordStart)
              ) {
                item.prop("selected", true);
                notYetSelected = false;
                selectedValue = data[i];
              }
              item.text(data[i]);
              item.val(data[i]);
              cb.$source.append(item);
            }
          }
        } else if (typeof data == "object") {
          var keyList = Array();
          for (var key in data) {
            if (data.hasOwnProperty(key)) {
              keyList.push(key);
            }
          }
          keyList = keyList.sort();
          for (var i = 0; i < keyList.length; ++i) {
            var item = $("<option>");
            if (
              notYetSelected &&
              ((doShow &&
                keyList[i].toString().toUpperCase() == upperWordStart) ||
                keyList[i].toString() == wordStart)
            ) {
              item.prop("selected", true);
              notYetSelected = false;
              selectedValue = data[keyList[i]];
            }
            item.text(data[keyList[i]]);
            item.val(keyList[i]);
            cb.$source.append(item);
          }
        }
        if (doShow) {
          cb.refresh();
          cb.clearTarget();
          cb.$target.val(cb.$element.val());
          cb.lookup();
        } else {
          if (!notYetSelected) {
            cb.$element.val(selectedValue);
          }
        }
      }
    },
  );
}

function jsonIfObject(value) {
  if (typeof value === "object" || typeof value === "boolean") {
    return JSON.stringify(value);
  }
  return value;
}

function underscoreToCamel(str) {
  return str
    .split("_")
    .map((word, index) => {
      if (index === 0) return word;
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join("")
    .replace(/Uri$/, "URI");
}

function camelToUnderscore(camelStr) {
  return camelStr
    .replace(/URI$/, "Uri")
    .replace(/([A-Z])/g, "_$1")
    .toLowerCase()
    .replace(/^_/, "");
}

function daInitialize(doScroll) {
  if (!daObserverMode) {
    daResetCheckinCode();
  }
  daComboBoxes = Object();
  daVarLookupSelect = Object();
  daVarLookupCheckbox = Object();
  if (daSpinnerTimeout != null) {
    clearTimeout(daSpinnerTimeout);
    daSpinnerTimeout = null;
  }
  if (daShowingSpinner) {
    daHideSpinner();
  }
  if (daObserverMode) {
    $(
      'button[type="submit"], input[type="submit"], a.da-review-action, #dabackToQuestion, #daquestionlabel, #dapagetitle, #dahelptoggle, a[data-linknum], a[data-embaction], #dabackbutton',
    ).click(daObserverSubmitter);
  }
  daNotYetScrolled = true;
  // $(".dahelptrigger").click(function(e) {
  //   e.preventDefault();
  //   $(this).tab('show');
  // });
  $("input.dafile").fileinput({
    theme: "fas",
    language: document.documentElement.lang,
    allowedPreviewTypes: ["image"],
  });
  $(".datableup,.databledown").click(function (e) {
    e.preventDefault();
    $(this).blur();
    var row = $(this).parents("tr").first();
    if ($(this).is(".datableup")) {
      var prev = row.prev();
      if (prev.length == 0) {
        return false;
      }
      row.addClass("datablehighlighted");
      setTimeout(function () {
        row.insertBefore(prev);
      }, 200);
    } else {
      var next = row.next();
      if (next.length == 0) {
        return false;
      }
      row.addClass("datablehighlighted");
      setTimeout(function () {
        row.insertAfter(row.next());
      }, 200);
    }
    setTimeout(function () {
      row.removeClass("datablehighlighted");
    }, 1000);
    return false;
  });
  $(".dacollectextra").find("input, textarea, select").prop("disabled", true);
  $(".dacollectextra")
    .find("input.combobox")
    .each(function () {
      if (daComboBoxes[$(this).attr("id")]) {
        daComboBoxes[$(this).attr("id")].disable();
      } else {
        $(this).prop("disabled", true);
      }
    });
  $(".dacollectextra")
    .find("input.daslider")
    .each(function () {
      $(this).slider("disable");
    });
  $(".dacollectextra")
    .find("input.dafile")
    .each(function () {
      $(this).data("fileinput").disable();
    });
  $("#da-extra-collect").on("click", function () {
    $("<input>")
      .attr({
        type: "hidden",
        name: "_collect",
        value: $(this).val(),
      })
      .appendTo($("#daform"));
    $("#daform").submit();
    event.preventDefault();
    return false;
  });
  $(".dacollectadd").on("click", function (e) {
    e.preventDefault();
    if ($("#daform").valid()) {
      var num = $(this).parent().parent().data("collectnum");
      $('[data-collectnum="' + num + '"]').show("fast");
      $('[data-collectnum="' + num + '"]')
        .find("input, textarea, select")
        .each(function () {
          var showifParents = $(this).parents(".dajsshowif,.dashowif");
          if (showifParents.length == 0 || $(showifParents[0]).is(":visible")) {
            $(this).prop("disabled", false);
          }
        });
      $('[data-collectnum="' + num + '"]')
        .find("input.combobox")
        .each(function () {
          var showifParents = $(this).parents(".dajsshowif,.dashowif");
          if (showifParents.length == 0 || $(showifParents[0]).is(":visible")) {
            if (daComboBoxes[$(this).attr("id")]) {
              daComboBoxes[$(this).attr("id")].enable();
            } else {
              $(this).prop("disabled", false);
            }
          }
        });
      $('[data-collectnum="' + num + '"]')
        .find("input.daslider")
        .each(function () {
          var showifParents = $(this).parents(".dajsshowif,.dashowif");
          if (showifParents.length == 0 || $(showifParents[0]).is(":visible")) {
            $(this).slider("enable");
          }
        });
      $('[data-collectnum="' + num + '"]')
        .find("input.dafile")
        .each(function () {
          var showifParents = $(this).parents(".dajsshowif,.dashowif");
          if (showifParents.length == 0 || $(showifParents[0]).is(":visible")) {
            $(this).data("fileinput").enable();
          }
        });
      $(this)
        .parent()
        .find("button.dacollectremove")
        .removeClass("dainvisible");
      $(this).parent().find("span.dacollectnum").removeClass("dainvisible");
      $(this).addClass("dainvisible");
      $(".da-first-delete").removeClass("dainvisible");
      rationalizeListCollect();
      var elem = $('[data-collectnum="' + num + '"]')
        .find("input, textarea, select")
        .first();
      if ($(elem).visible()) {
        $(elem).focus();
      }
    }
    return false;
  });
  $("#dasigform").on("submit", daSignatureSubmit);
  $(".dacollectremove").on("click", function (e) {
    e.preventDefault();
    var num = $(this).parent().parent().data("collectnum");
    $(
      '[data-collectnum="' +
        num +
        '"]:not(.dacollectextraheader, .dacollectheader, .dacollectfirstheader)',
    ).hide("fast");
    $('[data-collectnum="' + num + '"]')
      .find("input, textarea, select")
      .prop("disabled", true);
    $('[data-collectnum="' + num + '"]')
      .find("input.combobox")
      .each(function () {
        if (daComboBoxes[$(this).attr("id")]) {
          daComboBoxes[$(this).attr("id")].disable();
        } else {
          $(this).prop("disabled", true);
        }
      });
    $('[data-collectnum="' + num + '"]')
      .find("input.daslider")
      .each(function () {
        $(this).slider("disable");
      });
    $('[data-collectnum="' + num + '"]')
      .find("input.dafile")
      .each(function () {
        $(this).data("fileinput").disable();
      });
    $(this).parent().find("button.dacollectadd").removeClass("dainvisible");
    $(this).parent().find("span.dacollectnum").addClass("dainvisible");
    $(this).addClass("dainvisible");
    rationalizeListCollect();
    return false;
  });
  $(".dacollectremoveexisting").on("click", function (e) {
    e.preventDefault();
    var num = $(this).parent().parent().data("collectnum");
    $(
      '[data-collectnum="' +
        num +
        '"]:not(.dacollectextraheader, .dacollectheader, .dacollectfirstheader)',
    ).hide("fast");
    $('[data-collectnum="' + num + '"]')
      .find("input, textarea, select")
      .prop("disabled", true);
    $('[data-collectnum="' + num + '"]')
      .find("input.combobox")
      .each(function () {
        if (daComboBoxes[$(this).attr("id")]) {
          daComboBoxes[$(this).attr("id")].disable();
        } else {
          $(this).prop("disabled", true);
        }
      });
    $('[data-collectnum="' + num + '"]')
      .find("input.daslider")
      .each(function () {
        $(this).slider("disable");
      });
    $('[data-collectnum="' + num + '"]')
      .find("input.dafile")
      .each(function () {
        $(this).data("fileinput").disable();
      });
    $(this)
      .parent()
      .find("button.dacollectunremove")
      .removeClass("dainvisible");
    $(this).parent().find("span.dacollectremoved").removeClass("dainvisible");
    $(this).addClass("dainvisible");
    rationalizeListCollect();
    return false;
  });
  $(".dacollectunremove").on("click", function (e) {
    e.preventDefault();
    var num = $(this).parent().parent().data("collectnum");
    $('[data-collectnum="' + num + '"]').show("fast");
    $('[data-collectnum="' + num + '"]')
      .find("input, textarea, select")
      .prop("disabled", false);
    $('[data-collectnum="' + num + '"]')
      .find("input.combobox")
      .each(function () {
        if (daComboBoxes[$(this).attr("id")]) {
          daComboBoxes[$(this).attr("id")].enable();
        } else {
          $(this).prop("disabled", false);
        }
      });
    $('[data-collectnum="' + num + '"]')
      .find("input.daslider")
      .each(function () {
        $(this).slider("enable");
      });
    $('[data-collectnum="' + num + '"]')
      .find("input.dafile")
      .each(function () {
        $(this).data("fileinput").enable();
      });
    $(this)
      .parent()
      .find("button.dacollectremoveexisting")
      .removeClass("dainvisible");
    $(this).parent().find("button.dacollectremove").removeClass("dainvisible");
    $(this).parent().find("span.dacollectnum").removeClass("dainvisible");
    $(this).parent().find("span.dacollectremoved").addClass("dainvisible");
    $(this).addClass("dainvisible");
    rationalizeListCollect();
    return false;
  });
  //$('#daquestionlabel').click(function(e) {
  //  e.preventDefault();
  //  $(this).tab('show');
  //});
  //$('#dapagetitle').click(function(e) {
  //  if ($(this).prop('href') == '#'){
  //    e.preventDefault();
  //    //$('#daquestionlabel').tab('show');
  //  }
  //});
  $("select.damultiselect").each(function () {
    var isObject = $(this).hasClass("daobject");
    var varname = atou($(this).data("varname"));
    var theSelect = this;
    $(this)
      .find("option")
      .each(function () {
        var theVal = atou($(this).data("valname"));
        if (isObject) {
          theVal = atou(theVal);
        }
        var key = varname + '["' + theVal + '"]';
        if (!daVarLookupSelect[key]) {
          daVarLookupSelect[key] = [];
        }
        daVarLookupSelect[key].push({
          select: theSelect,
          option: this,
          value: theVal,
        });
        key = varname + "['" + theVal + "']";
        if (!daVarLookupSelect[key]) {
          daVarLookupSelect[key] = [];
        }
        daVarLookupSelect[key].push({
          select: theSelect,
          option: this,
          value: theVal,
        });
      });
  });
  $("div.da-field-group.da-field-checkboxes").each(function () {
    var isObject = $(this).hasClass("daobject");
    var varname = atou($(this).data("varname"));
    var cbList = [];
    if (!daVarLookupCheckbox[varname]) {
      daVarLookupCheckbox[varname] = [];
    }
    $(this)
      .find("input")
      .each(function () {
        if ($(this).attr("name").substr(0, 7) === "_ignore") {
          return;
        }
        var theVal = atou($(this).data("cbvalue"));
        var theType = $(this).data("cbtype");
        var key;
        if (theType == "R") {
          key = varname + "[" + theVal + "]";
        } else {
          key = varname + '["' + theVal + '"]';
        }
        cbList.push({
          variable: key,
          value: theVal,
          type: theType,
          elem: this,
        });
      });
    daVarLookupCheckbox[varname].push({
      elem: this,
      checkboxes: cbList,
      isObject: isObject,
    });
    $(this)
      .find("input.danota-checkbox")
      .each(function () {
        if (!daVarLookupCheckbox[varname + "[nota]"]) {
          daVarLookupCheckbox[varname + "[nota]"] = [];
        }
        daVarLookupCheckbox[varname + "[nota]"].push({
          elem: this,
          checkboxes: [{ variable: varname + "[nota]", type: "X", elem: this }],
          isObject: isObject,
        });
      });
    $(this)
      .find("input.daaota-checkbox")
      .each(function () {
        if (!daVarLookupCheckbox[varname + "[aota]"]) {
          daVarLookupCheckbox[varname + "[aota]"] = [];
        }
        daVarLookupCheckbox[varname + "[aota]"].push({
          elem: this,
          checkboxes: [{ variable: varname + "[aota]", type: "X", elem: this }],
          isObject: isObject,
        });
      });
  });
  $(".dacurrency").each(function () {
    var theVal = $(this).val().toString();
    if (theVal.indexOf(".") >= 0) {
      theVal = theVal.replace(",", "");
      var num = parseFloat(theVal);
      var cleanNum = num.toFixed(daCurrencyDecimalPlaces).toString();
      if (cleanNum != "NaN") {
        $(this).val(cleanNum);
      }
    }
  });
  $(".dacurrency").on("change", function () {
    var theVal = $(this).val().toString();
    if (theVal.indexOf(".") >= 0) {
      theVal = theVal.replaceAll(/[\$,\(\)]/g, "");
      var num = parseFloat(theVal);
      var cleanNum = num.toFixed(daCurrencyDecimalPlaces).toString();
      if (cleanNum != "NaN") {
        $(this).val(cleanNum);
      } else {
        $(this).val(theVal);
      }
    } else {
      $(this).val(theVal.replaceAll(/[^0-9\.\-]/g, ""));
    }
  });
  $(".danumeric").on("change", function () {
    var theVal = $(this).val().toString();
    $(this).val(theVal.replaceAll(/[\$,\(\)]/g, ""));
  });
  // iOS will truncate text in `select` options. Adding an empty optgroup fixes that
  if (navigator.userAgent.match(/(iPad|iPhone|iPod touch);/i)) {
    var selects = document.querySelectorAll("select");
    for (var i = 0; i < selects.length; i++) {
      selects[i].appendChild(document.createElement("optgroup"));
    }
  }
  $(".da-to-labelauty").labelauty({
    class: "labelauty da-active-invisible dafullwidth",
  });
  $(".da-to-labelauty-icon").labelauty({ label: false });
  $("input[type=radio].da-to-labelauty:checked").trigger("change");
  $("input[type=radio].da-to-labelauty-icon:checked").trigger("change");
  $("button").on("click", function () {
    daWhichButton = this;
    return true;
  });
  $("#dasource").on("shown.bs.collapse", function (e) {
    if (daJsEmbed) {
      var scrollTarget = $("#dasource").first().position().top - 60;
      $(daTargetDiv).animate(
        {
          scrollTop: scrollTarget,
        },
        1000,
      );
    } else {
      var scrollTarget = $("#dasource").first().offset().top - 60;
      $("html, body").animate(
        {
          scrollTop: scrollTarget,
        },
        1000,
      );
    }
  });
  $('button[data-bs-target="#dahelp"]').on("shown.bs.tab", function (e) {
    daShowingHelp = 1;
    if (daNotYetScrolled) {
      daScrollChatFast();
      daNotYetScrolled = false;
    }
    if (daShouldDebugReadabilityHelp) {
      $("#dareadability-help").show();
      $("#dareadability-question").hide();
    }
  });
  $('button[data-bs-target="#daquestion"]').on("shown.bs.tab", function (e) {
    daShowingHelp = 0;
    if (daShouldDebugReadabilityQuestion) {
      $("#dareadability-help").hide();
      $("#dareadability-question").show();
    }
  });
  $("input.daaota-checkbox").click(function () {
    var anyChanged = false;
    var firstEncountered = null;
    $(this)
      .parents("div.da-field-group")
      .find("input.danon-nota-checkbox")
      .each(function () {
        if (firstEncountered === null) {
          firstEncountered = this;
        }
        var existing_val = $(this).prop("checked");
        $(this).prop("checked", true);
        if (existing_val != true) {
          $(this).trigger("change");
          anyChanged = true;
        }
      });
    if (firstEncountered !== null && anyChanged === false) {
      $(firstEncountered).trigger("change");
    }
    $(this)
      .parents("div.da-field-group")
      .find("input.danota-checkbox")
      .each(function () {
        var existing_val = $(this).prop("checked");
        $(this).prop("checked", false);
        if (existing_val != false) {
          $(this).trigger("change");
        }
      });
  });
  $("input.danota-checkbox").click(function () {
    var anyChanged = false;
    var firstEncountered = null;
    $(this)
      .parents("div.da-field-group")
      .find("input.danon-nota-checkbox")
      .each(function () {
        if (firstEncountered === null) {
          firstEncountered = this;
        }
        var existing_val = $(this).prop("checked");
        $(this).prop("checked", false);
        if (existing_val != false) {
          $(this).trigger("change");
          anyChanged = true;
        }
      });
    if (firstEncountered !== null && anyChanged === false) {
      $(firstEncountered).trigger("change");
    }
    $(this)
      .parents("div.da-field-group")
      .find("input.daaota-checkbox")
      .each(function () {
        var existing_val = $(this).prop("checked");
        $(this).prop("checked", false);
        if (existing_val != false) {
          $(this).trigger("change");
        }
      });
  });
  $("input.danon-nota-checkbox").click(function () {
    $(this)
      .parents("div.da-field-group")
      .find("input.danota-checkbox")
      .each(function () {
        var existing_val = $(this).prop("checked");
        $(this).prop("checked", false);
        if (existing_val != false) {
          $(this).trigger("change");
        }
      });
    if (!$(this).prop("checked")) {
      $(this)
        .parents("div.da-field-group")
        .find("input.daaota-checkbox")
        .each(function () {
          var existing_val = $(this).prop("checked");
          $(this).prop("checked", false);
          if (existing_val != false) {
            $(this).trigger("change");
          }
        });
    }
  });
  $("select.combobox").combobox({
    buttonLabel: daComboboxButtonLabel,
    inputBox: daInputBox,
  });
  $("select.da-ajax-combobox").combobox({
    clearIfNoMatch: true,
    buttonLabel: daComboboxButtonLabel,
    functionalButton: false,
    inputBox: daInputBox,
  });
  $("input.da-address-combobox").combobox({
    clearIfNoMatch: false,
    showButton: false,
    inputBox: daInputBox,
    matcher: function (item) {
      return true;
    },
    lookupWhileTyping: false,
  });
  $("input.da-ajax-combobox").each(function () {
    var cb = daComboBoxes[$(this).attr("id")];
    daFetchAjax(this, cb, false);
    $(this).on("keyup", function (e) {
      switch (e.keyCode) {
        case 40:
        case 39: // right arrow
        case 38: // up arrow
        case 37: // left arrow
        case 36: // home
        case 35: // end
        case 16: // shift
        case 17: // ctrl
        case 9: // tab
        case 13: // enter
        case 27: // escape
        case 18: // alt
          return;
      }
      daFetchAjax(this, cb, true);
      daFetchAcceptIncoming = true;
      e.preventDefault();
      return false;
    });
  });
  $.each(daComboBoxes, async function (thisId, cb) {
    if (!this.$element.hasClass("da-address-combobox")) {
      return;
    }
    if (cb.$target.val()) {
      cb.$element.val(cb.$target.val());
    }
    await daWaitForGoogle(false);
    const { Place, AutocompleteSessionToken, AutocompleteSuggestion } =
      await google.maps.importLibrary("places");
    const token = new AutocompleteSessionToken();
    var elem = cb.$element;
    var priorQuery = "";
    var priorResults = [];
    let request = {
      language: "en-US",
      region: "us",
      sessionToken: token,
    };
    cb.$target.on("change", async (e) => {
      if (!daAutocomplete[thisId].suggestions[cb.$target.val()]) {
        return;
      }
      var theVal = cb.$target.val();
      cb.$container.removeClass("combobox-selected");
      cb.selected = false;
      let place =
        daAutocomplete[thisId].suggestions[theVal].placePrediction.toPlace();
      await place.fetchFields({
        fields: (
          daAutocomplete[thisId].opts.fields || ["addressComponents"]
        ).map(underscoreToCamel),
      });
      // console.log(place);
      daFillInAddress(thisId, place);
    });
    elem.on("keyup", async (e) => {
      switch (e.keyCode) {
        case 40:
        case 39: // right arrow
        case 38: // up arrow
        case 37: // left arrow
        case 36: // home
        case 35: // end
        case 16: // shift
        case 17: // ctrl
        case 9: // tab
        case 13: // enter
        case 27: // escape
        case 18: // alt
          return;
      }
      request.input = elem.val();
      request.includedPrimaryTypes = daAutocomplete[thisId].opts.types || [
        "street_address",
      ];
      if (request.input.length > 2 && request.input != priorQuery) {
        priorQuery = request.input;
        const { suggestions } =
          await AutocompleteSuggestion.fetchAutocompleteSuggestions(request);
        var results = [];
        var sugMap = {};
        for (let suggestion of suggestions) {
          const placePrediction = suggestion.placePrediction;
          const addressText = placePrediction.text.toString();
          results.push(addressText);
          sugMap[addressText] = suggestion;
        }
        if (
          !(
            results.length === priorResults.length &&
            results.every((value, index) => value === priorResults[index])
          )
        ) {
          daAutocomplete[thisId].suggestions = sugMap;
          cb.options.items = results.length;
          cb.map = results.reduce((obj, key) => ({ ...obj, [key]: key }), {});
          cb.revMap = cb.map;
          priorResults = results;
        }
        cb.process(results);
      }
      e.preventDefault();
      return false;
    });
  });
  $("#daemailform").validate({
    submitHandler: daValidationHandler,
    rules: {
      _attachment_email_address: { minlength: 1, required: true, email: true },
    },
    messages: {
      _attachment_email_address: {
        required: daEmailAddressRequired,
        email: daNeedCompleteEmail,
      },
    },
    errorClass: "da-has-error invalid-feedback",
  });
  $("a[data-embaction]").click(daEmbeddedAction);
  $("a[data-js]").click(daEmbeddedJs);
  $("a.da-review-action").click(daReviewAction);
  $("input.dainput-embedded").on("keyup", daAdjustInputWidth);
  $("input.dainput-embedded").each(daAdjustInputWidth);
  var daPopoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]'),
  );
  var daPopoverTrigger = daDefaultPopoverTrigger;
  var daPopoverList = daPopoverTriggerList.map(function (daPopoverTriggerEl) {
    return new bootstrap.Popover(daPopoverTriggerEl, {
      trigger: daPopoverTrigger,
      html: true,
    });
  });
  if (daPopoverTrigger == "focus") {
    $(
      'label a[data-bs-toggle="popover"], legend a[data-bs-toggle="popover"]',
    ).on("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      $(this).focus();
      return false;
    });
  }
  if (!daObserverMode) {
    if (daPhoneAvailable) {
      $("#daPhoneAvailable").removeClass("dainvisible");
    }
    $(".daquestionbackbutton").on("click", function (event) {
      event.preventDefault();
      $("#dabackbutton").submit();
      return false;
    });
    $("#dabackbutton").on("submit", function (event) {
      if (daShowingHelp) {
        event.preventDefault();
        $("#daquestionlabel").tab("show");
        return false;
      }
      $("#dabackbutton").addClass("dabackiconpressed");
      var informed = "";
      if (daInformedChanged) {
        informed = "&informed=" + Object.keys(daInformed).join(",");
      }
      var url;
      if (daJsEmbed) {
        url = daPostURL;
      } else {
        url = $("#dabackbutton").attr("action");
      }
      daRequestPending = true;
      $.ajax({
        type: "POST",
        url: url,
        beforeSend: addCsrfHeader,
        xhrFields: {
          withCredentials: true,
        },
        data: $("#dabackbutton").serialize() + "&ajax=1" + informed,
        success: function (data) {
          setTimeout(function () {
            daProcessAjax(data, document.getElementById("backbutton"), 1);
          }, 0);
        },
        error: function (xhr, status, error) {
          setTimeout(function () {
            daProcessAjaxError(xhr, status, error);
          }, 0);
        },
      });
      daSpinnerTimeout = setTimeout(daShowSpinner, 1000);
      event.preventDefault();
    });
    $("#daChatOnButton").click(daRingChat);
    $("#daChatOffButton").click(daCloseChat);
    $("#daMessage").bind("keypress keydown keyup", function (e) {
      var theCode = e.which || e.keyCode;
      if (theCode == 13) {
        daSender();
        e.preventDefault();
      }
    });
    $('#daform button[type="submit"]').click(function () {
      daSubmitter = this;
      document.activeElement.blur();
      return true;
    });
    $('#daform input[type="submit"]').click(function () {
      daSubmitter = this;
      document.activeElement.blur();
      return true;
    });
    $('#daemailform button[type="submit"]').click(function () {
      daSubmitter = this;
      return true;
    });
    $('#dadownloadform button[type="submit"]').click(function () {
      daSubmitter = this;
      return true;
    });
    $(".danavlinks a.daclickable").click(function (e) {
      if (daRequestPending) {
        e.preventDefault();
        $(this).blur();
        return false;
      }
      var the_key = $(this).data("key");
      da_action_perform("_da_priority_action", { _action: the_key });
      e.preventDefault();
      return false;
    });
    $(".danav-vertical .danavnested").each(function () {
      var box = this;
      var prev = $(this).prev();
      if (prev && !prev.hasClass("active")) {
        var toggler;
        if ($(box).hasClass("danotshowing")) {
          toggler = $(
            '<a href="#" class="toggler" role="button" aria-pressed="false">',
          );
          $('<i class="fa-solid fa-caret-right">').appendTo(toggler);
          $(
            '<span class="visually-hidden">' + daToggleWord + "</span>",
          ).appendTo(toggler);
        } else {
          toggler = $(
            '<a href="#" class="toggler" role="button" aria-pressed="true">',
          );
          $('<i class="fa-solid fa-caret-down">').appendTo(toggler);
          $(
            '<span class="visually-hidden">' + daToggleWord + "</span>",
          ).appendTo(toggler);
        }
        toggler.appendTo(prev);
        toggler.on("click", function (e) {
          var oThis = this;
          $(this)
            .find("svg")
            .each(function () {
              if ($(this).attr("data-icon") == "caret-down") {
                $(this).removeClass("fa-caret-down");
                $(this).addClass("fa-caret-right");
                $(this).attr("data-icon", "caret-right");
                $(box).hide();
                $(oThis).attr("aria-pressed", "false");
                $(box).toggleClass("danotshowing");
              } else if ($(this).attr("data-icon") == "caret-right") {
                $(this).removeClass("fa-caret-right");
                $(this).addClass("fa-caret-down");
                $(this).attr("data-icon", "caret-down");
                $(box).show();
                $(oThis).attr("aria-pressed", "true");
                $(box).toggleClass("danotshowing");
              }
            });
          e.stopPropagation();
          e.preventDefault();
          return false;
        });
      }
    });
    $("body").focus();
    if (!daJsEmbed && !isAndroid) {
      setTimeout(function () {
        var firstInput = $("#daform .da-field-container")
          .not(".da-field-container-note")
          .first()
          .find("input, textarea, select")
          .filter(":visible")
          .first();
        if (firstInput.length > 0 && $(firstInput).visible()) {
          $(firstInput).focus();
          var inputType = $(firstInput).attr("type");
          if (
            $(firstInput).prop("tagName") != "SELECT" &&
            inputType != "checkbox" &&
            inputType != "radio" &&
            inputType != "hidden" &&
            inputType != "submit" &&
            inputType != "file" &&
            inputType != "range" &&
            inputType != "number" &&
            inputType != "date" &&
            inputType != "time"
          ) {
            var strLength = $(firstInput).val().length * 2;
            if (strLength > 0) {
              try {
                $(firstInput)[0].setSelectionRange(strLength, strLength);
              } catch (err) {
                console.log(err.message);
              }
            }
          }
        } else {
          var firstButton = $("#danavbar-collapse .nav-link")
            .filter(":visible")
            .first();
          if (firstButton.length > 0 && $(firstButton).visible()) {
            setTimeout(function () {
              $(firstButton).focus();
              $(firstButton).blur();
            }, 0);
          }
        }
      }, 15);
    }
  }
  $("input.dauncheckspecificothers").on("change", function () {
    if ($(this).is(":checked")) {
      var theIds = $.parseJSON(atou($(this).data("unchecklist")));
      var n = theIds.length;
      for (var i = 0; i < n; ++i) {
        var elem = document.getElementById(theIds[i]);
        $(elem).prop("checked", false);
        $(elem).trigger("change");
      }
    }
  });
  $("input.dauncheckspecificothers").each(function () {
    var theIds = $.parseJSON(atou($(this).data("unchecklist")));
    var n = theIds.length;
    var oThis = this;
    for (var i = 0; i < n; ++i) {
      var elem = document.getElementById(theIds[i]);
      $(elem).on("change", function () {
        if ($(this).is(":checked")) {
          $(oThis).prop("checked", false);
          $(oThis).trigger("change");
        }
      });
    }
  });
  $("input.dauncheckothers").on("change", function () {
    if ($(this).is(":checked")) {
      $("input.dauncheckable,input.dacheckothers").each(function () {
        if ($(this).is(":checked")) {
          $(this).prop("checked", false);
          $(this).trigger("change");
        }
      });
    }
  });
  $("input.dacheckspecificothers").on("change", function () {
    if ($(this).is(":checked")) {
      var theIds = $.parseJSON(atou($(this).data("checklist")));
      var n = theIds.length;
      for (var i = 0; i < n; ++i) {
        var elem = document.getElementById(theIds[i]);
        $(elem).prop("checked", true);
        $(elem).trigger("change");
      }
    }
  });
  $("input.dacheckspecificothers").each(function () {
    var theIds = $.parseJSON(atou($(this).data("checklist")));
    var n = theIds.length;
    var oThis = this;
    for (var i = 0; i < n; ++i) {
      var elem = document.getElementById(theIds[i]);
      $(elem).on("change", function () {
        if (!$(this).is(":checked")) {
          $(oThis).prop("checked", false);
          $(oThis).trigger("change");
        }
      });
    }
  });
  $("input.dacheckothers").on("change", function () {
    if ($(this).is(":checked")) {
      $("input.dauncheckable").each(function () {
        if (!$(this).is(":checked")) {
          $(this).prop("checked", true);
          $(this).trigger("change");
        }
      });
      $("input.dauncheckothers").each(function () {
        if (!$(this).is(":checked")) {
          $(this).prop("checked", false);
          $(this).trigger("change");
        }
      });
    }
  });
  $("input.dauncheckable").on("change", function () {
    if ($(this).is(":checked")) {
      $("input.dauncheckothers").each(function () {
        if ($(this).is(":checked")) {
          $(this).prop("checked", false);
          $(this).trigger("change");
        }
      });
    } else {
      $("input.dacheckothers").each(function () {
        if ($(this).is(":checked")) {
          $(this).prop("checked", false);
          $(this).trigger("change");
        }
      });
    }
  });
  var navMain = $("#danavbar-collapse");
  navMain.on("click", "a", null, function () {
    if (!$(this).hasClass("dropdown-toggle")) {
      navMain.collapse("hide");
    }
  });
  $("button[data-bs-target='#dahelp']").on("shown.bs.tab", function () {
    if (daJsEmbed) {
      $(daTargetDiv)[0].scrollTo(0, 1);
    } else {
      window.scrollTo(0, 1);
    }
    $("#dahelptoggle").removeClass("daactivetext");
    $("#dahelptoggle").blur();
  });
  $("#dasourcetoggle").on("click", function () {
    $(this).parent().toggleClass("active");
    $(this).blur();
  });
  $("#dabackToQuestion").click(function (event) {
    $("#daquestionlabel").tab("show");
  });
  daVarLookup = Object();
  daVarLookupRev = Object();
  daVarLookupMulti = Object();
  daVarLookupRevMulti = Object();
  daVarLookupOption = Object();
  if ($("input[name='_varnames']").length) {
    the_hash = $.parseJSON(atou($("input[name='_varnames']").val()));
    for (var key in the_hash) {
      if (the_hash.hasOwnProperty(key)) {
        daVarLookup[the_hash[key]] = key;
        daVarLookupRev[key] = the_hash[key];
        if (!daVarLookupMulti.hasOwnProperty(the_hash[key])) {
          daVarLookupMulti[the_hash[key]] = [];
        }
        daVarLookupMulti[the_hash[key]].push(key);
        if (!daVarLookupRevMulti.hasOwnProperty(key)) {
          daVarLookupRevMulti[key] = [];
        }
        daVarLookupRevMulti[key].push(the_hash[key]);
      }
    }
  }
  if ($("input[name='_checkboxes']").length) {
    var patt = new RegExp(/\[B['"][^\]]*['"]\]$/);
    var pattObj = new RegExp(/\[O['"][^\]]*['"]\]$/);
    var pattRaw = new RegExp(/\[R['"][^\]]*['"]\]$/);
    the_hash = $.parseJSON(atou($("input[name='_checkboxes']").val()));
    for (var key in the_hash) {
      if (the_hash.hasOwnProperty(key)) {
        var checkboxName = atou(key);
        var baseName = checkboxName;
        if (patt.test(baseName)) {
          bracketPart = checkboxName.replace(
            /^.*(\[B?['"][^\]]*['"]\])$/,
            "$1",
          );
          checkboxName = checkboxName.replace(
            /^.*\[B?['"]([^\]]*)['"]\]$/,
            "$1",
          );
          baseName = baseName.replace(/^(.*)\[.*/, "$1");
          var transBaseName = baseName;
          if (
            $("[name='" + key + "']").length == 0 &&
            typeof daVarLookup[utoa(transBaseName).replace(/[\n=]/g, "")] !=
              "undefined"
          ) {
            transBaseName = atou(
              daVarLookup[utoa(transBaseName).replace(/[\n=]/g, "")],
            );
          }
          var convertedName;
          try {
            convertedName = atou(checkboxName);
          } catch (e) {
            continue;
          }
          var daNameOne = utoa(transBaseName + bracketPart).replace(
            /[\n=]/g,
            "",
          );
          var daNameTwo = utoa(baseName + "['" + convertedName + "']").replace(
            /[\n=]/g,
            "",
          );
          var daNameThree = utoa(
            baseName + '["' + convertedName + '"]',
          ).replace(/[\n=]/g, "");
          var daNameBase = utoa(baseName).replace(/[\n=]/g, "");
          daVarLookupRev[daNameOne] = daNameTwo;
          daVarLookup[daNameTwo] = daNameOne;
          daVarLookup[daNameThree] = daNameOne;
          daVarLookupOption[key] = convertedName;
          if (!daVarLookupRevMulti.hasOwnProperty(daNameOne)) {
            daVarLookupRevMulti[daNameOne] = [];
          }
          daVarLookupRevMulti[daNameOne].push(daNameTwo);
          if (!daVarLookupMulti.hasOwnProperty(daNameTwo)) {
            daVarLookupMulti[daNameTwo] = [];
          }
          daVarLookupMulti[daNameTwo].push(daNameOne);
          if (!daVarLookupMulti.hasOwnProperty(daNameThree)) {
            daVarLookupMulti[daNameThree] = [];
          }
          daVarLookupMulti[daNameThree].push(daNameOne);
          if (!daVarLookupMulti.hasOwnProperty(daNameBase)) {
            daVarLookupMulti[daNameBase] = [];
          }
          daVarLookupMulti[daNameBase].push(daNameOne);
        } else if (pattObj.test(baseName)) {
          bracketPart = checkboxName.replace(
            /^.*(\[O?['"][^\]]*['"]\])$/,
            "$1",
          );
          checkboxName = checkboxName.replace(
            /^.*\[O?['"]([^\]]*)['"]\]$/,
            "$1",
          );
          baseName = baseName.replace(/^(.*)\[.*/, "$1");
          var transBaseName = baseName;
          if (
            $("[name='" + key + "']").length == 0 &&
            typeof daVarLookup[utoa(transBaseName).replace(/[\n=]/g, "")] !=
              "undefined"
          ) {
            transBaseName = atou(
              daVarLookup[utoa(transBaseName).replace(/[\n=]/g, "")],
            );
          }
          var convertedName;
          try {
            convertedName = atou(atou(checkboxName));
          } catch (e) {
            continue;
          }
          var daNameOne = utoa(transBaseName + bracketPart).replace(
            /[\n=]/g,
            "",
          );
          var daNameTwo = utoa(baseName + "['" + convertedName + "']").replace(
            /[\n=]/g,
            "",
          );
          var daNameThree = utoa(
            baseName + '["' + convertedName + '"]',
          ).replace(/[\n=]/g, "");
          var daNameBase = utoa(baseName).replace(/[\n=]/g, "");
          daVarLookupRev[daNameOne] = daNameTwo;
          daVarLookup[daNameTwo] = daNameOne;
          daVarLookup[daNameThree] = daNameOne;
          daVarLookupOption[key] = convertedName;
          if (!daVarLookupRevMulti.hasOwnProperty(daNameOne)) {
            daVarLookupRevMulti[daNameOne] = [];
          }
          daVarLookupRevMulti[daNameOne].push(daNameTwo);
          if (!daVarLookupMulti.hasOwnProperty(daNameTwo)) {
            daVarLookupMulti[daNameTwo] = [];
          }
          daVarLookupMulti[daNameTwo].push(daNameOne);
          if (!daVarLookupMulti.hasOwnProperty(daNameThree)) {
            daVarLookupMulti[daNameThree] = [];
          }
          daVarLookupMulti[daNameThree].push(daNameOne);
          if (!daVarLookupMulti.hasOwnProperty(daNameBase)) {
            daVarLookupMulti[daNameBase] = [];
          }
          daVarLookupMulti[daNameBase].push(daNameOne);
        } else if (pattRaw.test(baseName)) {
          bracketPart = checkboxName.replace(
            /^.*(\[R?['"][^\]]*['"]\])$/,
            "$1",
          );
          checkboxName = checkboxName.replace(
            /^.*\[R?['"]([^\]]*)['"]\]$/,
            "$1",
          );
          baseName = baseName.replace(/^(.*)\[.*/, "$1");
          var transBaseName = baseName;
          if (
            $("[name='" + key + "']").length == 0 &&
            typeof daVarLookup[utoa(transBaseName).replace(/[\n=]/g, "")] !=
              "undefined"
          ) {
            transBaseName = atou(
              daVarLookup[utoa(transBaseName).replace(/[\n=]/g, "")],
            );
          }
          var convertedName;
          try {
            convertedName = atou(checkboxName);
          } catch (e) {
            continue;
          }
          var daNameOne = utoa(transBaseName + bracketPart).replace(
            /[\n=]/g,
            "",
          );
          var daNameTwo = utoa(baseName + "[" + convertedName + "]").replace(
            /[\n=]/g,
            "",
          );
          var daNameBase = utoa(baseName).replace(/[\n=]/g, "");
          daVarLookupRev[daNameOne] = daNameTwo;
          daVarLookup[daNameTwo] = daNameOne;
          daVarLookupOption[key] = convertedName;
          if (!daVarLookupRevMulti.hasOwnProperty(daNameOne)) {
            daVarLookupRevMulti[daNameOne] = [];
          }
          daVarLookupRevMulti[daNameOne].push(daNameTwo);
          if (!daVarLookupMulti.hasOwnProperty(daNameTwo)) {
            daVarLookupMulti[daNameTwo] = [];
          }
          daVarLookupMulti[daNameTwo].push(daNameOne);
          if (!daVarLookupMulti.hasOwnProperty(daNameBase)) {
            daVarLookupMulti[daNameBase] = [];
          }
          daVarLookupMulti[daNameBase].push(daNameOne);
        }
      }
    }
  }
  daShowIfInProcess = true;
  var daTriggerQueries = [];
  var daInputsSeen = {};
  function daOnlyUnique(value, index, self) {
    return self.indexOf(value) === index;
  }
  $(".dajsshowif").each(function () {
    var showIfDiv = this;
    var jsInfo = JSON.parse(atou($(this).data("jsshowif")));
    var showIfSign = jsInfo["sign"];
    var showIfMode = jsInfo["mode"];
    var jsExpression = jsInfo["expression"];
    jsInfo["vars"].forEach(function (infoItem, i) {
      var showIfVars = [];
      var initShowIfVar = utoa(infoItem).replace(/[\n=]/g, "");
      var initShowIfVarEscaped = initShowIfVar.replace(
        /(:|\.|\[|\]|,|=)/g,
        "\\$1",
      );
      var elem = $("[name='" + initShowIfVarEscaped + "']");
      if (elem.length > 0) {
        showIfVars.push(initShowIfVar);
      }
      if (daVarLookupMulti.hasOwnProperty(initShowIfVar)) {
        for (var j = 0; j < daVarLookupMulti[initShowIfVar].length; j++) {
          var altShowIfVar = daVarLookupMulti[initShowIfVar][j];
          var altShowIfVarEscaped = altShowIfVar.replace(
            /(:|\.|\[|\]|,|=)/g,
            "\\$1",
          );
          var altElem = $("[name='" + altShowIfVarEscaped + "']");
          if (altElem.length > 0 && !$.contains(this, altElem[0])) {
            showIfVars.push(altShowIfVar);
          }
        }
      }
      if (showIfVars.length == 0) {
        console.log("ERROR: reference to non-existent field " + infoItem);
      }
      showIfVars.forEach(function (showIfVar) {
        var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/g, "\\$1");
        var varToUse = infoItem;
        var showHideDiv = function (speed) {
          var elem = daGetField(varToUse);
          if (
            elem != null &&
            !$(elem)
              .parents(".da-form-group")
              .first()
              .is($(this).parents(".da-form-group").first())
          ) {
            return;
          }
          var resultt = eval(jsExpression);
          if (resultt) {
            if (showIfSign) {
              if ($(showIfDiv).data("isVisible") != "1") {
                daShowHideHappened = true;
              }
              if (showIfMode == 0) {
                $(showIfDiv).show(speed);
              }
              $(showIfDiv).data("isVisible", "1");
              $(showIfDiv)
                .find("input, textarea, select")
                .prop("disabled", false);
              $(showIfDiv)
                .find("input.combobox")
                .each(function () {
                  if (daComboBoxes[$(this).attr("id")]) {
                    daComboBoxes[$(this).attr("id")].enable();
                  } else {
                    $(this).prop("disabled", false);
                  }
                });
              $(showIfDiv)
                .find("input.daslider")
                .each(function () {
                  $(this).slider("enable");
                });
              $(showIfDiv)
                .find("input.dafile")
                .each(function () {
                  $(this).data("fileinput").enable();
                });
            } else {
              if ($(showIfDiv).data("isVisible") != "0") {
                daShowHideHappened = true;
              }
              if (showIfMode == 0) {
                $(showIfDiv).hide(speed);
              }
              $(showIfDiv).data("isVisible", "0");
              $(showIfDiv)
                .find("input, textarea, select")
                .prop("disabled", true);
              $(showIfDiv)
                .find("input.combobox")
                .each(function () {
                  if (daComboBoxes[$(this).attr("id")]) {
                    daComboBoxes[$(this).attr("id")].disable();
                  } else {
                    $(this).prop("disabled", false);
                  }
                });
              $(showIfDiv)
                .find("input.daslider")
                .each(function () {
                  $(this).slider("disable");
                });
              $(showIfDiv)
                .find("input.dafile")
                .each(function () {
                  $(this).data("fileinput").disable();
                });
            }
          } else {
            if (showIfSign) {
              if ($(showIfDiv).data("isVisible") != "0") {
                daShowHideHappened = true;
              }
              if (showIfMode == 0) {
                $(showIfDiv).hide(speed);
              }
              $(showIfDiv).data("isVisible", "0");
              $(showIfDiv)
                .find("input, textarea, select")
                .prop("disabled", true);
              $(showIfDiv)
                .find("input.combobox")
                .each(function () {
                  if (daComboBoxes[$(this).attr("id")]) {
                    daComboBoxes[$(this).attr("id")].disable();
                  } else {
                    $(this).prop("disabled", true);
                  }
                });
              $(showIfDiv)
                .find("input.daslider")
                .each(function () {
                  $(this).slider("disable");
                });
              $(showIfDiv)
                .find("input.dafile")
                .each(function () {
                  $(this).data("fileinput").disable();
                });
            } else {
              if ($(showIfDiv).data("isVisible") != "1") {
                daShowHideHappened = true;
              }
              if (showIfMode == 0) {
                $(showIfDiv).show(speed);
              }
              $(showIfDiv).data("isVisible", "1");
              $(showIfDiv)
                .find("input, textarea, select")
                .prop("disabled", false);
              $(showIfDiv)
                .find("input.combobox")
                .each(function () {
                  if (daComboBoxes[$(this).attr("id")]) {
                    daComboBoxes[$(this).attr("id")].enable();
                  } else {
                    $(this).prop("disabled", false);
                  }
                });
              $(showIfDiv)
                .find("input.daslider")
                .each(function () {
                  $(this).slider("enable");
                });
              $(showIfDiv)
                .find("input.dafile")
                .each(function () {
                  $(this).data("fileinput").enable();
                });
            }
          }
          var leader = false;
          if (!daShowIfInProcess) {
            daShowIfInProcess = true;
            daInputsSeen = {};
            leader = true;
          }
          $(showIfDiv)
            .find(":input")
            .not("[type='file']")
            .each(function () {
              if (!daInputsSeen.hasOwnProperty($(this).attr("id"))) {
                $(this).trigger("change");
              }
              daInputsSeen[$(this).attr("id")] = true;
            });
          if (leader) {
            daShowIfInProcess = false;
          }
        };
        var showHideDivImmediate = function () {
          showHideDiv.apply(this, [null]);
        };
        var showHideDivFast = function () {
          showHideDiv.apply(this, ["fast"]);
        };
        daTriggerQueries.push("#" + showIfVarEscaped);
        daTriggerQueries.push(
          "input[type='radio'][name='" + showIfVarEscaped + "']",
        );
        daTriggerQueries.push(
          "input[type='checkbox'][name='" + showIfVarEscaped + "']",
        );
        $("#" + showIfVarEscaped).change(showHideDivFast);
        $("input[type='radio'][name='" + showIfVarEscaped + "']").change(
          showHideDivFast,
        );
        $("input[type='checkbox'][name='" + showIfVarEscaped + "']").change(
          showHideDivFast,
        );
        $("input.dafile[name='" + showIfVarEscaped + "']").on(
          "filecleared",
          showHideDivFast,
        );
        $("#" + showIfVarEscaped).on("daManualTrigger", showHideDivImmediate);
        $("input[type='radio'][name='" + showIfVarEscaped + "']").on(
          "daManualTrigger",
          showHideDivImmediate,
        );
        $("input[type='checkbox'][name='" + showIfVarEscaped + "']").on(
          "daManualTrigger",
          showHideDivImmediate,
        );
      });
    });
  });
  $(".dashowif").each(function () {
    var showIfVars = [];
    var showIfSign = $(this).data("showif-sign");
    var showIfMode = parseInt($(this).data("showif-mode"));
    var initShowIfVar = $(this).data("showif-var");
    var varName = atou(initShowIfVar);
    var elem = [];
    if (varName.endsWith("[nota]") || varName.endsWith("[aota]")) {
      var signifier = varName.endsWith("[nota]") ? "nota" : "aota";
      var cbVarName = varName.replace(/\[[na]ota\]$/, "");
      $("div.da-field-group.da-field-checkboxes").each(function () {
        var thisVarName = atou($(this).data("varname"));
        if (thisVarName == cbVarName) {
          elem = $(this).find("input.da" + signifier + "-checkbox");
          initShowIfVar = $(elem).attr("name");
        }
      });
    } else {
      var initShowIfVarEscaped = initShowIfVar.replace(
        /(:|\.|\[|\]|,|=)/g,
        "\\$1",
      );
      elem = $("[name='" + initShowIfVarEscaped + "']");
    }
    if (elem.length > 0) {
      showIfVars.push(initShowIfVar);
    }
    if (daVarLookupMulti.hasOwnProperty(initShowIfVar)) {
      var n = daVarLookupMulti[initShowIfVar].length;
      for (var i = 0; i < n; i++) {
        var altShowIfVar = daVarLookupMulti[initShowIfVar][i];
        var altShowIfVarEscaped = altShowIfVar.replace(
          /(:|\.|\[|\]|,|=)/g,
          "\\$1",
        );
        var altElem = $("[name='" + altShowIfVarEscaped + "']");
        if (altElem.length > 0 && !$.contains(this, altElem[0])) {
          showIfVars.push(altShowIfVar);
        }
      }
    }
    var showIfVal = $(this).data("showif-val");
    var saveAs = $(this).data("saveas");
    var showIfDiv = this;
    showIfVars.forEach(function (showIfVar) {
      var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/g, "\\$1");
      var showHideDiv = function (speed) {
        var elem = daGetField(varName, showIfDiv);
        if (
          elem != null &&
          !$(elem)
            .parents(".da-form-group")
            .first()
            .is($(this).parents(".da-form-group").first())
        ) {
          return;
        }
        var theVal;
        var showifParents = $(this).parents(".dashowif");
        if (
          showifParents.length !== 0 &&
          !($(showifParents[0]).data("isVisible") == "1")
        ) {
          theVal = "";
          //console.log("Setting theVal to blank.");
        } else if ($(this).attr("type") == "checkbox") {
          theVal = $("input[name='" + showIfVarEscaped + "']:checked").val();
          if (typeof theVal == "undefined") {
            //console.log('manually setting checkbox value to False');
            theVal = "False";
          }
        } else if ($(this).attr("type") == "radio") {
          theVal = $("input[name='" + showIfVarEscaped + "']:checked").val();
          if (typeof theVal == "undefined") {
            theVal = "";
          } else if (
            theVal != "" &&
            $("input[name='" + showIfVarEscaped + "']:checked").hasClass(
              "daobject",
            )
          ) {
            try {
              theVal = atou(theVal);
            } catch (e) {}
          }
        } else {
          theVal = $(this).val();
          if (theVal != "" && $(this).hasClass("daobject")) {
            try {
              theVal = atou(theVal);
            } catch (e) {}
          }
        }
        // console.log("There was a trigger on " + $(this).attr('id') + ". This handler was installed based on varName " + varName + ", showIfVar " + atou(showIfVar) + ". This handler was installed for the benefit of the .dashowif div encompassing the field for " + atou(saveAs) + ". The comparison value is " + String(showIfVal) + " and the current value of the element on the screen is " + String(theVal) + ".");
        if (daShowIfCompare(theVal, showIfVal)) {
          if (showIfSign) {
            if ($(showIfDiv).data("isVisible") != "1") {
              daShowHideHappened = true;
            }
            if (showIfMode == 0) {
              $(showIfDiv).show(speed);
            }
            $(showIfDiv).data("isVisible", "1");
            var firstChild = $(showIfDiv).children()[0];
            if (
              !$(firstChild).hasClass("dacollectextra") ||
              $(firstChild).is(":visible")
            ) {
              $(showIfDiv)
                .find("input, textarea, select")
                .prop("disabled", false);
              $(showIfDiv)
                .find("input.combobox")
                .each(function () {
                  if (daComboBoxes[$(this).attr("id")]) {
                    daComboBoxes[$(this).attr("id")].enable();
                  } else {
                    $(this).prop("disabled", false);
                  }
                });
              $(showIfDiv)
                .find("input.daslider")
                .each(function () {
                  $(this).slider("enable");
                });
              $(showIfDiv)
                .find("input.dafile")
                .each(function () {
                  $(this).data("fileinput").enable();
                });
            }
          } else {
            if ($(showIfDiv).data("isVisible") != "0") {
              daShowHideHappened = true;
            }
            if (showIfMode == 0) {
              $(showIfDiv).hide(speed);
            }
            $(showIfDiv).data("isVisible", "0");
            $(showIfDiv).find("input, textarea, select").prop("disabled", true);
            $(showIfDiv)
              .find("input.combobox")
              .each(function () {
                if (daComboBoxes[$(this).attr("id")]) {
                  daComboBoxes[$(this).attr("id")].disable();
                } else {
                  $(this).prop("disabled", true);
                }
              });
            $(showIfDiv)
              .find("input.daslider")
              .each(function () {
                $(this).slider("disable");
              });
            $(showIfDiv)
              .find("input.dafile")
              .each(function () {
                $(this).data("fileinput").disable();
              });
          }
        } else {
          if (showIfSign) {
            if ($(showIfDiv).data("isVisible") != "0") {
              daShowHideHappened = true;
            }
            if (showIfMode == 0) {
              $(showIfDiv).hide(speed);
            }
            $(showIfDiv).data("isVisible", "0");
            $(showIfDiv).find("input, textarea, select").prop("disabled", true);
            $(showIfDiv)
              .find("input.combobox")
              .each(function () {
                if (daComboBoxes[$(this).attr("id")]) {
                  daComboBoxes[$(this).attr("id")].disable();
                } else {
                  $(this).prop("disabled", true);
                }
              });
            $(showIfDiv)
              .find("input.daslider")
              .each(function () {
                $(this).slider("disable");
              });
            $(showIfDiv)
              .find("input.dafile")
              .each(function () {
                $(this).data("fileinput").disable();
              });
          } else {
            if ($(showIfDiv).data("isVisible") != "1") {
              daShowHideHappened = true;
            }
            if (showIfMode == 0) {
              $(showIfDiv).show(speed);
            }
            $(showIfDiv).data("isVisible", "1");
            var firstChild = $(showIfDiv).children()[0];
            if (
              !$(firstChild).hasClass("dacollectextra") ||
              $(firstChild).is(":visible")
            ) {
              $(showIfDiv)
                .find("input, textarea, select")
                .prop("disabled", false);
              $(showIfDiv)
                .find("input.combobox")
                .each(function () {
                  if (daComboBoxes[$(this).attr("id")]) {
                    daComboBoxes[$(this).attr("id")].enable();
                  } else {
                    $(this).prop("disabled", false);
                  }
                });
              $(showIfDiv)
                .find("input.daslider")
                .each(function () {
                  $(this).slider("enable");
                });
              $(showIfDiv)
                .find("input.dafile")
                .each(function () {
                  $(this).data("fileinput").enable();
                });
            }
          }
        }
        var leader = false;
        if (!daShowIfInProcess) {
          daShowIfInProcess = true;
          daInputsSeen = {};
          leader = true;
        }
        $(showIfDiv)
          .find(":input")
          .not("[type='file']")
          .each(function () {
            if (!daInputsSeen.hasOwnProperty($(this).attr("id"))) {
              $(this).trigger("change");
            }
            daInputsSeen[$(this).attr("id")] = true;
          });
        if (leader) {
          daShowIfInProcess = false;
        }
      };
      var showHideDivImmediate = function () {
        showHideDiv.apply(this, [null]);
      };
      var showHideDivFast = function () {
        showHideDiv.apply(this, ["fast"]);
      };
      daTriggerQueries.push("#" + showIfVarEscaped);
      daTriggerQueries.push(
        "input[type='radio'][name='" + showIfVarEscaped + "']",
      );
      daTriggerQueries.push(
        "input[type='checkbox'][name='" + showIfVarEscaped + "']",
      );
      $("#" + showIfVarEscaped).change(showHideDivFast);
      $("#" + showIfVarEscaped).on("daManualTrigger", showHideDivImmediate);
      $("input[type='radio'][name='" + showIfVarEscaped + "']").change(
        showHideDivFast,
      );
      $("input[type='radio'][name='" + showIfVarEscaped + "']").on(
        "daManualTrigger",
        showHideDivImmediate,
      );
      $("input[type='checkbox'][name='" + showIfVarEscaped + "']").change(
        showHideDivFast,
      );
      $("input[type='checkbox'][name='" + showIfVarEscaped + "']").on(
        "daManualTrigger",
        showHideDivImmediate,
      );
      $("input.dafile[name='" + showIfVarEscaped + "']").on(
        "filecleared",
        showHideDivFast,
      );
    });
  });
  function daTriggerAllShowHides() {
    var daUniqueTriggerQueries = daTriggerQueries.filter(daOnlyUnique);
    var daFirstTime = true;
    var daTries = 0;
    while ((daFirstTime || daShowHideHappened) && ++daTries < 100) {
      daShowHideHappened = false;
      daFirstTime = false;
      var n = daUniqueTriggerQueries.length;
      for (var i = 0; i < n; ++i) {
        $(daUniqueTriggerQueries[i]).trigger("daManualTrigger");
      }
    }
    if (daTries >= 100) {
      console.log("Too many contradictory 'show if' conditions");
    }
  }
  if (daTriggerQueries.length > 0) {
    daTriggerAllShowHides();
  }
  $(".danavlink").last().addClass("thelast");
  $(".danavlink").each(function () {
    if ($(this).hasClass("btn") && !$(this).hasClass("danotavailableyet")) {
      var the_a = $(this);
      var the_delay = 1000 + 250 * parseInt($(this).data("index"));
      setTimeout(function () {
        $(the_a).removeClass(daButtonStyle + "secondary");
        if ($(the_a).hasClass("active")) {
          $(the_a).addClass(daButtonStyle + "success");
        } else {
          $(the_a).addClass(daButtonStyle + "warning");
        }
      }, the_delay);
    }
  });
  daShowIfInProcess = false;
  if (!daObserverMode) {
    $("#daSend").click(daSender);
    if (daChatAvailable == "unavailable") {
      daChatStatus = "off";
    }
    if (daChatAvailable == "observeonly") {
      daChatStatus = "observeonly";
    }
    if (
      (daChatStatus == "off" || daChatStatus == "observeonly") &&
      daChatAvailable == "available"
    ) {
      daChatStatus = "waiting";
    }
    daDisplayChat();
    if (daBeingControlled) {
      daShowControl("fast");
    }
    if (daChatStatus == "ready" || daBeingControlled) {
      daInitializeSocket();
    }
    if (daInitialized == false && daCheckinSeconds > 0) {
      // why was this set to always retrieve the chat log?
      setTimeout(function () {
        //console.log("daInitialize call to chat_log in checkin");
        $.ajax({
          type: "POST",
          url: daCheckinUrlWithInterview,
          beforeSend: addCsrfHeader,
          xhrFields: {
            withCredentials: true,
          },
          data: $.param({ action: "chat_log", ajax: "1", csrf_token: daCsrf }),
          success: daChatLogCallback,
          dataType: "json",
        });
      }, 200);
    }
    if (daInitialized == true) {
      //console.log("Publishing from memory");
      $("#daCorrespondence").html("");
      for (var i = 0; i < daChatHistory.length; i++) {
        daPublishMessage(daChatHistory[i]);
      }
    }
    if (daChatStatus != "off") {
      daSendChanges = true;
    } else {
      if (daDoAction == null) {
        daSendChanges = false;
      } else {
        daSendChanges = true;
      }
    }
  }
  if (daSendChanges || daObserverMode) {
    $("#daform").each(function () {
      $(this).find(":input").change(daOnChange);
    });
  }
  daInitialized = true;
  daShowingHelp = 0;
  daSubmitter = null;
  $("#daflash .alert-success").each(function () {
    var oThis = this;
    setTimeout(function () {
      $(oThis).hide(300, function () {
        $(self).remove();
      });
    }, 3000);
  });
  if (doScroll && !daObserverMode) {
    setTimeout(function () {
      if (daJsEmbed) {
        $(daTargetDiv)[0].scrollTo(0, 1);
        if (daSteps > 1) {
          $(daTargetDiv)[0].scrollIntoView();
        }
      } else {
        window.scrollTo(0, 1);
      }
    }, 20);
  }
  if (daShowingSpinner) {
    daHideSpinner();
  }
  if (!daObserverMode) {
    if (daCheckinInterval != null) {
      clearInterval(daCheckinInterval);
    }
    if (daCheckinSeconds > 0) {
      setTimeout(daInitialCheckin, 100);
      daCheckinInterval = setInterval(daCheckin, daCheckinSeconds);
    }
    daShowNotifications();
    if (daUsingGA) {
      daPageview();
    }
    if (daUsingSegment) {
      daSegmentEvent();
    }
    hideTablist();
  }
}
function daUpdateHeight() {
  $(".dagooglemap").each(function () {
    var size = $(this).width();
    $(this).css("height", size);
  });
}
function daConfigureJqueryFuncs() {
  $.validator.setDefaults({
    ignore: ".danovalidation",
    highlight: function (element) {
      $(element).closest(".da-form-group").addClass("da-group-has-error");
      $(element).addClass("is-invalid");
    },
    unhighlight: function (element) {
      $(element).closest(".da-form-group").removeClass("da-group-has-error");
      $(element).removeClass("is-invalid");
    },
    errorElement: "span",
    errorClass: "da-has-error invalid-feedback",
    errorPlacement: function (error, element) {
      $(error).addClass("invalid-feedback");
      var elementName = $(element).attr("name");
      var idOfErrorSpan = $(element).attr("id") + "-error";
      $("#" + idOfErrorSpan).remove();
      $(error).attr("id", idOfErrorSpan);
      $(element).attr("aria-invalid", "true");
      $(element).attr("aria-errormessage", idOfErrorSpan);
      var lastInGroup = $.map(
        daValidationRules["groups"],
        function (thefields, thename) {
          var fieldsArr;
          if (thefields.indexOf(elementName) >= 0) {
            fieldsArr = thefields.split(" ");
            return fieldsArr[fieldsArr.length - 1];
          } else {
            return null;
          }
        },
      )[0];
      if (element.hasClass("dainput-embedded")) {
        error.insertAfter(element);
      } else if (element.hasClass("dafile-embedded")) {
        error.insertAfter(element);
      } else if (element.hasClass("daradio-embedded")) {
        element.parent().append(error);
      } else if (element.hasClass("dacheckbox-embedded")) {
        element.parent().append(error);
      } else if (element.hasClass("dauncheckable") && lastInGroup) {
        $("input[name='" + lastInGroup + "']")
          .parent()
          .append(error);
      } else if (element.parent().hasClass("combobox-container")) {
        element.parent().append(error);
      } else if (element.hasClass("dafile")) {
        var fileContainer = $(element).parents(".file-input").first();
        if (fileContainer.length > 0) {
          $(fileContainer).append(error);
        } else {
          error.insertAfter(element.parent());
        }
      } else if (element.parent(".input-group").length) {
        error.insertAfter(element.parent());
      } else if (element.hasClass("da-active-invisible")) {
        var choice_with_help = $(element).parents(".dachoicewithhelp").first();
        if (choice_with_help.length > 0) {
          $(choice_with_help).parent().append(error);
        } else {
          element.parent().append(error);
        }
      } else if (element.hasClass("danon-nota-checkbox")) {
        element.parents("div.da-field-group").append(error);
      } else {
        error.insertAfter(element);
      }
    },
  });
  $.validator.addMethod("datetime", function (a, b) {
    return true;
  });
  $.validator.addMethod("ajaxrequired", function (value, element, params) {
    var realElement = $("#" + $(element).attr("name") + "combobox");
    var realValue = $(realElement).val();
    if (!$(realElement).parent().is(":visible")) {
      return true;
    }
    if (realValue == null || realValue.replace(/\s/g, "") == "") {
      return false;
    }
    return true;
  });
  $.validator.addMethod("checkone", function (value, element, params) {
    var number_needed = params[0];
    var css_query = params[1];
    if ($(css_query).length >= number_needed) {
      return true;
    } else {
      return false;
    }
  });
  $.validator.addMethod("checkatleast", function (value, element, params) {
    if ($(element).attr("name") != "_ignore" + params[0]) {
      return true;
    }
    if ($(".dafield" + params[0] + ":checked").length >= params[1]) {
      return true;
    } else {
      return false;
    }
  });
  $.validator.addMethod("checkatmost", function (value, element, params) {
    if ($(element).attr("name") != "_ignore" + params[0]) {
      return true;
    }
    if ($(".dafield" + params[0] + ":checked").length > params[1]) {
      return false;
    } else {
      return true;
    }
  });
  $.validator.addMethod("checkexactly", function (value, element, params) {
    if ($(element).attr("name") != "_ignore" + params[0]) {
      return true;
    }
    if ($(".dafield" + params[0] + ":checked").length != params[1]) {
      return false;
    } else {
      return true;
    }
  });
  $.validator.addMethod("selectexactly", function (value, element, params) {
    if ($(element).find("option:selected").length == params[0]) {
      return true;
    } else {
      return false;
    }
  });
  $.validator.addMethod("mindate", function (value, element, params) {
    if (value == null || value == "") {
      return true;
    }
    try {
      var date = new Date(value);
      var comparator = new Date(params);
      if (date >= comparator) {
        return true;
      }
    } catch (e) {}
    return false;
  });
  $.validator.addMethod("maxdate", function (value, element, params) {
    if (value == null || value == "") {
      return true;
    }
    try {
      var date = new Date(value);
      var comparator = new Date(params);
      if (date <= comparator) {
        return true;
      }
    } catch (e) {}
    return false;
  });
  $.validator.addMethod("minmaxdate", function (value, element, params) {
    if (value == null || value == "") {
      return true;
    }
    try {
      var date = new Date(value);
      var before_comparator = new Date(params[0]);
      var after_comparator = new Date(params[1]);
      if (date >= before_comparator && date <= after_comparator) {
        return true;
      }
    } catch (e) {}
    return false;
  });
  $.validator.addMethod("mintime", function (value, element, params) {
    if (value == null || value == "") {
      return true;
    }
    try {
      var time = new Date("1970-01-01T" + value + "Z");
      var comparator = new Date("1970-01-01T" + params + "Z");
      if (time >= comparator) {
        return true;
      }
    } catch (e) {}
    return false;
  });
  $.validator.addMethod("maxtime", function (value, element, params) {
    if (value == null || value == "") {
      return true;
    }
    try {
      var time = new Date("1970-01-01T" + value + "Z");
      var comparator = new Date("1970-01-01T" + params + "Z");
      if (time <= comparator) {
        return true;
      }
    } catch (e) {}
    return false;
  });
  $.validator.addMethod("minmaxtime", function (value, element, params) {
    if (value == null || value == "") {
      return true;
    }
    try {
      var time = new Date("1970-01-01T" + value + "Z");
      var before_comparator = new Date("1970-01-01T" + params[0] + "Z");
      var after_comparator = new Date("1970-01-01T" + params[1] + "Z");
      if (time >= before_comparator && time <= after_comparator) {
        return true;
      }
    } catch (e) {}
    return false;
  });
  $.validator.addMethod("mindatetime", function (value, element, params) {
    if (value == null || value == "") {
      return true;
    }
    try {
      var datetime = new Date(value + "Z");
      var comparator = new Date(params + "Z");
      if (datetime >= comparator) {
        return true;
      }
    } catch (e) {}
    return false;
  });
  $.validator.addMethod("maxdatetime", function (value, element, params) {
    if (value == null || value == "") {
      return true;
    }
    try {
      var datetime = new Date(value + "Z");
      var comparator = new Date(params + "Z");
      if (datetime <= comparator) {
        return true;
      }
    } catch (e) {}
    return false;
  });
  $.validator.addMethod("minmaxdatetime", function (value, element, params) {
    if (value == null || value == "") {
      return true;
    }
    try {
      var datetime = new Date(value + "Z");
      var before_comparator = new Date(params[0] + "Z");
      var after_comparator = new Date(params[1] + "Z");
      if (datetime >= before_comparator && datetime <= after_comparator) {
        return true;
      }
    } catch (e) {}
    return false;
  });
  $.validator.addMethod("maxuploadsize", function (value, element, param) {
    try {
      var limit = parseInt(param) - 2000;
      if (limit <= 0) {
        return true;
      }
      var maxImageSize;
      if ($(element).data("maximagesize")) {
        maxImageSize =
          parseInt($(element).data("maximagesize")) *
          parseInt($(element).data("maximagesize")) *
          2;
      } else {
        maxImageSize = 0;
      }
      if ($(element).attr("type") === "file") {
        if (element.files && element.files.length) {
          var totalSize = 0;
          for (i = 0; i < element.files.length; i++) {
            if (
              maxImageSize > 0 &&
              element.files[i].size > 0.2 * maxImageSize &&
              element.files[i].type.match(/image.*/) &&
              !(element.files[i].type.indexOf("image/svg") == 0)
            ) {
              totalSize += maxImageSize;
            } else {
              totalSize += element.files[i].size;
            }
          }
          if (totalSize > limit) {
            return false;
          }
        }
        return true;
      }
    } catch (e) {}
    return false;
  });
}
var dataLayer = (window.dataLayer = window.dataLayer || []);
function gtag() {
  dataLayer.push(arguments);
}
function daPageview() {
  var idToUse = daQuestionID["id"];
  if (daQuestionID["ga"] != undefined && daQuestionID["ga"] != null) {
    idToUse = daQuestionID["ga"];
  }
  if (idToUse != null) {
    idToUse = idToUse.replace(/[^A-Za-z0-9]+/g, "_");
    if (!daGAConfigured) {
      var opts = { send_page_view: false };
      if (daSecureCookies) {
        opts["cookie_flags"] = "SameSite=None;Secure";
      }
      for (var i = 0; i < daGaIds.length; i++) {
        gtag("config", daGaIds[i], opts);
        daGAConfigured = true;
      }
    }
    gtag(
      "set",
      "page_path",
      daInterviewPackage + "/" + daInterviewFilename + "/" + idToUse,
    );
    gtag("event", "page_view", {
      page_path: daInterviewPackage + "/" + daInterviewFilename + "/" + idToUse,
    });
  }
}
function daStopPushChanges() {
  if (daObserverChangesInterval != null) {
    clearInterval(daObserverChangesInterval);
  }
}
function daResetPushChanges() {
  if (daObserverChangesInterval != null) {
    clearInterval(daObserverChangesInterval);
  }
  daObserverChangesInterval = setInterval(daPushChanges, 6000);
}
function daReadyFunction() {
  daInitialize(1);
  //console.log("ready: replaceState " + daSteps);
  if (!daJsEmbed && !daIframeEmbed) {
    history.replaceState(
      { steps: daSteps },
      "",
      daLocationBar + daPageSep + daSteps,
    );
  }
  var daReloadAfter = daReloadAfterSeconds;
  if (daReloadAfter > 0) {
    daReloader = setTimeout(function () {
      daRefreshSubmit();
    }, daReloadAfter);
  }
  if (daUsingGA && !daObserverMode) {
    gtag("js", new Date());
  }
  window.onpopstate = function (event) {
    if (
      event.state != null &&
      event.state.steps < daSteps &&
      daAllowGoingBack
    ) {
      $("#dabackbutton").submit();
    }
  };
  $(window).bind("unload", function () {
    if (!daObserverMode) {
      daStopCheckingIn();
    }
    if (daSocket != null && daSocket.connected) {
      //console.log('Terminating interview socket because window unloaded');
      daSocket.emit("terminate");
    }
  });
  var daDefaultAllowList = bootstrap.Tooltip.Default.allowList;
  daDefaultAllowList["*"].push("style");
  daDefaultAllowList["a"].push("style");
  daDefaultAllowList["img"].push("style");
  if (daJsEmbed) {
    $.ajax({
      type: "POST",
      url: daPostURL,
      beforeSend: addCsrfHeader,
      xhrFields: {
        withCredentials: true,
      },
      data: "csrf_token=" + daCsrf + "&ajax=1",
      success: function (data) {
        setTimeout(function () {
          daProcessAjax(data, $("#daform"), 0);
        }, 0);
      },
      error: function (xhr, status, error) {
        setTimeout(function () {
          daProcessAjaxError(xhr, status, error);
        }, 0);
      },
    });
  }
  if (daObserverMode) {
    if (
      location.protocol === "http:" ||
      document.location.protocol === "http:"
    ) {
      daSocket = io.connect("http://" + document.domain + "/observer", {
        path: daRootUrl + "/ws/socket.io",
        query: "i=" + daYamlFilename,
      });
    }
    if (
      location.protocol === "https:" ||
      document.location.protocol === "https:"
    ) {
      daSocket = io.connect("https://" + document.domain + "/observer", {
        path: daRootUrl + "/ws/socket.io",
        query: "i=" + daYamlFilename,
      });
    }
    if (typeof daSocket !== "undefined") {
      daSocket.on("connect", function () {
        //console.log("Connected!");
        daSocket.emit("observe", {
          uid: daUid,
          i: daYamlFilename,
          userid: daUserObserved,
        });
        daConnected = true;
      });
      daSocket.on("terminate", function () {
        //console.log("Terminating socket");
        daSocket.disconnect();
      });
      daSocket.on("disconnect", function () {
        //console.log("Disconnected socket");
        //daSocket = null;
      });
      daSocket.on("stopcontrolling", function (data) {
        window.parent.daStopControlling(data.key);
      });
      daSocket.on("start_being_controlled", function (data) {
        //console.log("Got start_being_controlled");
        daConfirmed = true;
        daPushChanges();
        window.parent.daGotConfirmation(data.key);
      });
      daSocket.on("abortcontrolling", function (data) {
        //console.log("Got abortcontrolling");
        //daSendChanges = false;
        //daConfirmed = false;
        //daStopPushChanges();
        window.parent.daAbortControlling(data.key);
      });
      daSocket.on("noconnection", function (data) {
        //console.log("warning: no connection");
        if (daNoConnectionCount++ > 2) {
          //console.log("error: no connection");
          window.parent.daStopControlling(data.key);
        }
      });
      daSocket.on("newpage", function (incoming) {
        //console.log("Got newpage")
        var data = incoming.obj;
        $(daTargetDiv).html(data.body);
        $(daTargetDiv).parent().removeClass();
        $(daTargetDiv).parent().addClass(data.bodyclass);
        daInitialize(1);
        for (var i = 0; i < data.extra_scripts.length; i++) {
          daEvalExtraScript(data.extra_scripts[i]);
        }
        for (var i = 0; i < data.extra_css.length; i++) {
          $("head").append(data.extra_css[i]);
        }
        document.title = data.browser_title;
        if ($("html").attr("lang") != data.lang) {
          $("html").attr("lang", data.lang);
        }
        daPushChanges();
      });
      daSocket.on("pushchanges", function (data) {
        //console.log("Got pushchanges: " + JSON.stringify(data));
        var valArray = Object();
        var values = data.parameters;
        for (var i = 0; i < values.length; i++) {
          valArray[values[i].name] = values[i].value;
        }
        $("#daform").each(function () {
          $(this)
            .find(":input")
            .each(function () {
              var type = $(this).attr("type");
              var id = $(this).attr("id");
              var name = $(this).attr("name");
              if (type == "checkbox") {
                if (name in valArray) {
                  if (valArray[name] == "True") {
                    if ($(this).prop("checked") != true) {
                      $(this).prop("checked", true);
                      $(this).trigger("change");
                    }
                  } else {
                    if ($(this).prop("checked") != false) {
                      $(this).prop("checked", false);
                      $(this).trigger("change");
                    }
                  }
                } else {
                  if ($(this).prop("checked") != false) {
                    $(this).prop("checked", false);
                    $(this).trigger("change");
                  }
                }
              } else if (type == "radio") {
                if (name in valArray) {
                  if (valArray[name] == $(this).val()) {
                    if ($(this).prop("checked") != true) {
                      $(this).prop("checked", true);
                      $(this).trigger("change");
                    }
                  } else {
                    if ($(this).prop("checked") != false) {
                      $(this).prop("checked", false);
                      $(this).trigger("change");
                    }
                  }
                }
              } else if ($(this).data().hasOwnProperty("sliderMax")) {
                $(this).slider("setValue", parseInt(valArray[name]));
              } else {
                if (name in valArray) {
                  $(this).val(valArray[name]);
                }
              }
            });
        });
      });
    }
    daObserverChangesInterval = setInterval(daPushChanges, daCheckinSeconds);
  }
  $(document).trigger("daPageLoad");
}

function daSetPosition(position) {
  document.getElementById("da_track_location").value = JSON.stringify({
    latitude: position.coords.latitude,
    longitude: position.coords.longitude,
  });
}

function daAddListenersFor(elementId) {
  $('[name="' + elementId + '"]').change(function () {
    if ($(this).attr("type") == "checkbox" || $(this).attr("type") == "radio") {
      theVal = $('[name="' + elementId + '"]:checked').val();
    } else {
      theVal = $(this).val();
    }
    var n = 0;
    if ($(this).data("disableothers")) {
      var id_list = JSON.parse(
        decodeURIComponent(escape(atob($(this).data("disableothers")))),
      );
      n = id_list.length;
    }
    if (n) {
      for (var i = 0; i < n; ++i) {
        var theElementId = id_list[i].replace(/(:|\.|\[|\]|,|=)/g, "\\$1");
        if (theVal == null || theVal == "") {
          daDisableIfNotHidden(
            "#daform [name='" + theElementId + "']:not([type=hidden])",
            false,
          );
          daDisableIfNotHidden(
            "#daform [id='" + theElementId + "']:not([type=hidden])",
            false,
          );
        } else {
          daDisableIfNotHidden(
            "#daform [name='" + theElementId + "']:not([type=hidden])",
            true,
          );
          daDisableIfNotHidden(
            "#daform [id='" + theElementId + "']:not([type=hidden])",
            true,
          );
        }
      }
    } else {
      if (theVal == null || theVal == "") {
        daDisableIfNotHidden(
          "#daform input:not([name='" +
            elementId +
            "']):not([id^='" +
            elementId +
            "']):not([type=hidden])",
          false,
        );
        daDisableIfNotHidden(
          "#daform select:not([name='" +
            elementId +
            "']):not([id^='" +
            elementId +
            "']):not([type=hidden])",
          false,
        );
        daDisableIfNotHidden(
          "#daform textarea:not([name='" + elementId + "']):not([type=hidden])",
          false,
        );
      } else {
        daDisableIfNotHidden(
          "#daform input:not([name='" +
            elementId +
            "']):not([id^='" +
            elementId +
            "']):not([type=hidden])",
          true,
        );
        daDisableIfNotHidden(
          "#daform select:not([name='" +
            elementId +
            "']):not([id^='" +
            elementId +
            "']):not([type=hidden])",
          true,
        );
        daDisableIfNotHidden(
          "#daform textarea:not([name='" + elementId + "']):not([type=hidden])",
          true,
        );
      }
    }
  });
  $("[data-disableothers]").trigger("change");
}

function daShowError(error) {
  switch (error.code) {
    case error.PERMISSION_DENIED:
      document.getElementById("da_track_location").value = JSON.stringify({
        error: "User denied the request for Geolocation",
      });
      console.log("User denied the request for Geolocation.");
      break;
    case error.POSITION_UNAVAILABLE:
      document.getElementById("da_track_location").value = JSON.stringify({
        error: "Location information is unavailable",
      });
      console.log("Location information is unavailable.");
      break;
    case error.TIMEOUT:
      document.getElementById("da_track_location").value = JSON.stringify({
        error: "The request to get user location timed out",
      });
      console.log("The request to get user location timed out.");
      break;
    case error.UNKNOWN_ERROR:
      document.getElementById("da_track_location").value = JSON.stringify({
        error: "An unknown error occurred",
      });
      console.log("An unknown error occurred.");
      break;
  }
}
