var ctx, color = "#000";	

//var theTop;
//var theLeft;
var theWidth;
var aspectRatio;
var theBorders;
var waiter;
var waitlimit;
var isEmpty;

function daInitializeSignature(){
  aspectRatio = 0.4;
  theBorders = 24;
  waiter = 0;
  waitlimit = 2;
  isEmpty = 1;
  setTimeout(function(){
    if (!isCanvasSupported()){
      da_post({'success': 0});
    }
    newCanvas();
    $(document).on("touchmove", function(event){event.preventDefault();});
  }, 1000);
  $(window).resize(function(){resizeCanvas()});
  
  $(".sigpalette").click(function(){
    $(".sigpalette").css("border-color", "#777");
    $(".sigpalette").css("border-style", "solid");
    $(this).css("border-color", "#fff");
    $(this).css("border-style", "dashed");
    color = $(this).css("background-color");
    ctx.beginPath();
    ctx.lineJoin="round";
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
  });
  $(".sigclear").click(function() {
    newCanvas();
  });
  $(".sigsave").click(function() {
    if (isEmpty){
      $("#errormess").removeClass("signotshowing");
      setTimeout(function(){ $("#errormess").addClass("signotshowing"); }, 3000);
    }
    else{
      $(".sigclear").attr('disabled', true);
      $(".sigsave").attr('disabled', true);
      saveCanvas();
    }
  });
}

// function to setup a new canvas for drawing

function resizeCanvas(){
  //var cheight = $(window).height()-($("#sigheader").height() + $("#sigtoppart").height() + $("#sigbottompart").height());
  newCanvas();
  //console.log("I resized");
  return;
  // var cheight = $(window).width()*aspectRatio;
  // if (cheight > $(window).height()-theTop){
  //   cheight = $(window).height()-theTop;
  // }
  // if (cheight > 350){
  //   cheight = 350;
  // }
  // var cwidth = $(window).width() - theBorders;
  
  // $("#sigcontent").height(cheight);
  // //$("#sigcontent").css('top', ($("#sigheader").height() + $("#sigtoppart").height()) + "px");
  // //$("#sigbottompart").css('top', (cheight) + "px");
  // $("#sigcanvas").width(cwidth);
  // $("#sigcanvas").height(cheight);
  // theTop = $("#sigcanvas").offset().top;
  // theLeft = $("#sigcanvas").offset().left;
  // theWidth = cwidth/100.0;
  // if (theWidth < 1){
  //   theWidth = 1;
  // }
  // return;
}

function saveCanvas(){
  var dataURL = document.getElementById("sigcanvas").toDataURL();
  //console.log(dataURL)
  daSpinnerTimeout = setTimeout(showSpinner, 1000);
  da_post({'_success': 1, '_the_image': dataURL});
}

function newCanvas(){
  //console.log("running newCanvas");
  var cwidth = $(window).width() - theBorders;
  if (cwidth > 744 ){
    cwidth = 744;
  }
  var cheight = cwidth*aspectRatio;
  var otherHeights = $("#sigtoppart").outerHeight(true) + $("#sigbottompart").outerHeight(true);
  if (cheight > $(window).height()-otherHeights){
    cheight = $(window).height()-otherHeights;
  }
  if (cheight > 372){
    cheight = 372;
  }
  $("#sigcontent").height(cheight);
  var canvas = '<canvas id="sigcanvas" width="'+(cwidth)+'px" height="'+(cheight)+'px"></canvas>';
  $("#sigcontent").html(canvas);
  //theTop = $("#sigcanvas").offset().top;
  //theLeft = $("#sigcanvas").offset().left;
  theWidth = cwidth/100.0;
  if (theWidth < 1){
    theWidth = 1;
  }
  
  // setup canvas
  // ctx=document.getElementById("sigcanvas").getContext("2d");
  $("#sigcanvas").each(function(){
    ctx = $(this)[0].getContext("2d");
    ctx.strokeStyle = color;
    ctx.lineWidth = theWidth;
  });
  
  // setup to trigger drawing on mouse or touch
  $("#sigcanvas").drawTouch();
  $("#sigcanvas").drawPointer();
  $("#sigcanvas").drawMouse();
  //$(document).on("touchend", function(event){event.preventDefault();});
  //$(document).on("touchcancel", function(event){event.preventDefault();});
  //$(document).on("touchstart", function(event){event.preventDefault();});
  //$("meta[name=viewport]").attr('content', "width=device-width, minimum-scale=1.0, maximum-scale=1.0, initial-scale=1.0, user-scalable=0");
  isEmpty = 1;
  setTimeout(function () {
    window.scrollTo(0, 1);
  }, 10);
}

// prototype to	start drawing on touch using canvas moveTo and lineTo
$.fn.drawTouch = function() {
  var start = function(e) {
    e = e.originalEvent;
    x = e.changedTouches[0].pageX-$("#sigcanvas").offset().left;
    y = e.changedTouches[0].pageY-$("#sigcanvas").offset().top;
    ctx.beginPath();
    ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
    ctx.fill();
    ctx.beginPath();
    ctx.lineJoin="round";
    ctx.moveTo(x,y);
    if (isEmpty){
      $(".sigsave").prop("disabled", false);
      isEmpty = 0;
    }
  };
  var move = function(e) {
    e.preventDefault();
    if (waiter % waitlimit == 0){
      e = e.originalEvent;
      x = e.changedTouches[0].pageX-$("#sigcanvas").offset().left;
      y = e.changedTouches[0].pageY-$("#sigcanvas").offset().top;
      ctx.lineTo(x,y);
      ctx.stroke();
      if (isEmpty){
	isEmpty = 0;
      }
    }
    waiter++;
    //ctx.fillRect(x-0.5*theWidth,y-0.5*theWidth,theWidth,theWidth);
    //ctx.beginPath();
    //ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
    //ctx.fill();
  };
  var moveline = function(e) {
    waiter = 0;
    move(e);
  }
  var dot = function(e) {
    e.preventDefault();
    e = e.originalEvent;
    ctx.lineJoin="round";
    x = e.pageX-$("#sigcanvas").offset().left;
    y = e.pageY-$("#sigcanvas").offset().top;
    ctx.beginPath();
    ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
    ctx.fill();
    ctx.moveTo(x,y);
    if (isEmpty){
      isEmpty = 0;
    }
    //ctx.fillRect(x-0.5*theWidth,y-0.5*theWidth,theWidth,theWidth);
    //console.log("Got click");
  };
  $(this).on("click", dot);
  $(this).on("touchend", moveline);
  $(this).on("touchcancel", moveline);
  $(this).on("touchstart", start);
  $(this).on("touchmove", move);	
}; 
    
// prototype to	start drawing on pointer(microsoft ie) using canvas moveTo and lineTo
$.fn.drawPointer = function() {
  var start = function(e) {
    e = e.originalEvent;
    ctx.beginPath();
    ctx.lineJoin="round";
    x = e.pageX-$("#sigcanvas").offset().left;
    y = e.pageY-$("#sigcanvas").offset().top;
    ctx.moveTo(x,y);
    if (isEmpty){
      isEmpty = 0;
    }
    //ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
    //ctx.fill();
  };
  var move = function(e) {
    e.preventDefault();
    if (waiter % waitlimit == 0){
      e = e.originalEvent;
      x = e.pageX-$("#sigcanvas").offset().left;
      y = e.pageY-$("#sigcanvas").offset().top;
      ctx.lineTo(x,y);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(x,y);
      if (isEmpty){
	isEmpty = 0;
      }
    }
    //waiter++;
  };
  var moveline = function(e) {
    waiter = 0;
    move(e);
  };
  $(this).on("MSPointerDown", start);
  $(this).on("MSPointerMove", move);
  $(this).on("MSPointerUp", moveline);
};        

// prototype to	start drawing on mouse using canvas moveTo and lineTo
$.fn.drawMouse = function() {
  var clicked = 0;
  var start = function(e) {
    clicked = 1;
    x = e.pageX-$("#sigcanvas").offset().left;
    y = e.pageY-$("#sigcanvas").offset().top;
    ctx.beginPath();
    ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
    ctx.fill();
    ctx.beginPath();
    ctx.lineJoin="round";
    ctx.moveTo(x,y);
    if (isEmpty){
      isEmpty = 0;
    }
  };
  var move = function(e) {
    if(clicked && waiter % waitlimit == 0){
      x = e.pageX-$("#sigcanvas").offset().left;
      y = e.pageY-$("#sigcanvas").offset().top;
      ctx.lineTo(x,y);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(x,y);
      if (isEmpty){
	isEmpty = 0;
      }
    }
    //waiter++;
  };
  var stop = function(e) {
    waiter = 0;
    move(e);
    clicked = 0;
  };
  $(this).on("mousedown", start);
  $(this).on("mousemove", move);
  $(window).on("mouseup", stop);
};

function da_post(params) {
  for(var key in params) {
    if(params.hasOwnProperty(key)) {
      var hiddenField = document.getElementById(key);
      if (hiddenField != null){
	hiddenField.setAttribute("value", params[key]);
      }
      else{
	console.log("Key does not exist: " + key);
	return;
      }
    }
  }
  $('#dasigform').submit();
  return;
}

function isCanvasSupported(){
  var elem = document.createElement('canvas');
  return !!(elem.getContext && elem.getContext('2d'));
}
  
var placeSearch, autocomplete, base_id;

function initAutocomplete(id) {
  base_id = id;
  autocomplete = new google.maps.places.Autocomplete(
      (document.getElementById(base_id)),
      {types: ['geocode']});
  autocomplete.addListener('place_changed', fillInAddress);
}

function fillInAddress() {
  var base_varname = atob(base_id).replace(/.address$/, '');
  var re = new RegExp('^' + base_varname + '\\.(.*)');
  var componentForm = {
    locality: 'long_name',
    administrative_area_level_2: 'long_name',
    administrative_area_level_1: 'short_name',
    country: 'long_name',
    postal_code: 'short_name'
  };
  var componentTrans = {
    locality: 'city',
    administrative_area_level_2: 'county',
    administrative_area_level_1: 'state',
    country: 'country',
    postal_code: 'zip'
  };

  var fields_to_fill = ['address', 'city', 'county', 'state', 'zip'];
  var id_for_part = {};
  $("input, select").each(function(){
    try {
      var field_name = atob($(this).attr('id'));
      var m = re.exec(field_name);
      if (m.length > 0){
        id_for_part[m[1]] = $(this).attr('id');
      }
    } catch (e){
    }
  });
  var place = autocomplete.getPlace();

  document.getElementById(id_for_part['address']).value = '';

  for (var component in fields_to_fill) {
    if (id_for_part[component] != undefined){
      document.getElementById(id_for_part[component]).value = '';
    }
  }
  
  var street_number;
  var route;

  for (var i = 0; i < place.address_components.length; i++) {
    var addressType = place.address_components[i].types[0];
    console.log(addressType);                  
    if (addressType == 'street_number'){
      street_number = place.address_components[i]['short_name'];
    }                
    if (addressType == 'route'){
      route = place.address_components[i]['long_name'];
    }                
    if (componentForm[addressType] && id_for_part[componentTrans[addressType]]) {
      var val = place.address_components[i][componentForm[addressType]];
      document.getElementById(id_for_part[componentTrans[addressType]]).value = val;
    }
  }
  document.getElementById(id_for_part['address']).value = street_number + " " + route;
}

function geolocate() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var geolocation = {
	lat: position.coords.latitude,
	lng: position.coords.longitude
      };
      var circle = new google.maps.Circle({
	center: geolocation,
	radius: position.coords.accuracy
      });
      autocomplete.setBounds(circle.getBounds());
    });
  }
}
