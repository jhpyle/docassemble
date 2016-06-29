var ctx, color = "#000";	

var theTop;
var theLeft;
var theWidth;
var aspectRatio = 0.30;
var theBorders = 50;
var waiter = 0;
var waitlimit = 2;
var isEmpty = 1;

$(document).ready(function () {
  setTimeout(function(){
    if (!isCanvasSupported()){
      post({'success': 0});
    }
    newCanvas();
  }, 1000);
  
  $(".palette").click(function(){
    $(".palette").css("border-color", "#777");
    $(".palette").css("border-style", "solid");
    $(this).css("border-color", "#fff");
    $(this).css("border-style", "dashed");
    color = $(this).css("background-color");
    ctx.beginPath();
    ctx.lineJoin="round";
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
  });
  $("#new").click(function() {
    newCanvas();
  });
  $("#save").click(function() {
    if (isEmpty){
      $("#errormess").removeClass("notshowing");
      setTimeout(function(){ $("#errormess").addClass("notshowing"); }, 3000);
    }
    else{
      document.getElementById('save').disabled = true;
      saveCanvas();
    }
  });
  window.scrollTo(0,1);
});

// function to setup a new canvas for drawing

function resizeCanvas(){
  //var cheight = $(window).height()-($("#header").height() + $("#toppart").height() + $("#bottompart").height());
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
  
  // $("#content").height(cheight);
  // //$("#content").css('top', ($("#header").height() + $("#toppart").height()) + "px");
  // //$("#bottompart").css('top', (cheight) + "px");
  // $("#canvas").width(cwidth);
  // $("#canvas").height(cheight);
  // theTop = $("#canvas").offset().top;
  // theLeft = $("#canvas").offset().left;
  // theWidth = cwidth/100.0;
  // if (theWidth < 1){
  //   theWidth = 1;
  // }
  // return;
}


function saveCanvas(){
  var dataURL = document.getElementById("canvas").toDataURL();
  //console.log(dataURL)
  post({'_success': 1, '_the_image': dataURL});
}

function newCanvas(){
  var cwidth = $(window).width() - theBorders;
  if (cwidth > 800 ){
    cwidth = 800;
  }
  var cheight = cwidth*aspectRatio;
  var otherHeights = $("#toppart").outerHeight(true) + $("#bottompart").outerHeight(true);
  if (cheight > $(window).height()-otherHeights){
    cheight = $(window).height()-otherHeights;
  }
  if (cheight > 350){
    cheight = 350;
  }
  $("#content").height(cheight);
  var canvas = '<canvas id="canvas" width="'+(cwidth)+'px" height="'+(cheight)+'px"></canvas>';
  $("#content").html(canvas);
  theTop = $("#canvas").offset().top;
  theLeft = $("#canvas").offset().left;
  theWidth = cwidth/100.0;
  if (theWidth < 1){
    theWidth = 1;
  }
  
  // setup canvas
  ctx=document.getElementById("canvas").getContext("2d");
  ctx.strokeStyle = color;
  ctx.lineWidth = theWidth;	
  
  // setup to trigger drawing on mouse or touch
  $("#canvas").drawTouch();
  $("#canvas").drawPointer();
  $("#canvas").drawMouse();
  //$(document).on("touchend", function(event){event.preventDefault();});
  //$(document).on("touchcancel", function(event){event.preventDefault();});
  //$(document).on("touchstart", function(event){event.preventDefault();});
  $(document).on("touchmove", function(event){event.preventDefault();});	
  isEmpty = 1;
  //$("#save").prop("disabled", true);
}

// prototype to	start drawing on touch using canvas moveTo and lineTo
$.fn.drawTouch = function() {
  var start = function(e) {
    e = e.originalEvent;
    x = e.changedTouches[0].pageX-$("#canvas").offset().left;
    y = e.changedTouches[0].pageY-$("#canvas").offset().top;
    ctx.beginPath();
    ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
    ctx.fill();
    ctx.beginPath();
    ctx.lineJoin="round";
    ctx.moveTo(x,y);
    if (isEmpty){
      $("#save").prop("disabled", false);
      isEmpty = 0;
    }
  };
  var move = function(e) {
    e.preventDefault();
    if (waiter % waitlimit == 0){
      e = e.originalEvent;
      x = e.changedTouches[0].pageX-$("#canvas").offset().left;
      y = e.changedTouches[0].pageY-$("#canvas").offset().top;
      ctx.lineTo(x,y);
      ctx.stroke();
      if (isEmpty){
	//$("#save").prop("disabled", false);
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
    x = e.pageX-$("#canvas").offset().left;
    y = e.pageY-$("#canvas").offset().top;
    ctx.beginPath();
    ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
    ctx.fill();
    ctx.moveTo(x,y);
    if (isEmpty){
      //$("#save").prop("disabled", false);
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
    x = e.pageX-$("#canvas").offset().left;
    y = e.pageY-$("#canvas").offset().top;
    ctx.moveTo(x,y);
    if (isEmpty){
      //$("#save").prop("disabled", false);
      isEmpty = 0;
    }
    //ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
    //ctx.fill();
  };
  var move = function(e) {
    e.preventDefault();
    if (waiter % waitlimit == 0){
      e = e.originalEvent;
      x = e.pageX-$("#canvas").offset().left;
      y = e.pageY-$("#canvas").offset().top;
      ctx.lineTo(x,y);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(x,y);
      if (isEmpty){
	//$("#save").prop("disabled", false);
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
    x = e.pageX-$("#canvas").offset().left;
    y = e.pageY-$("#canvas").offset().top;
    ctx.beginPath();
    ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
    ctx.fill();
    ctx.beginPath();
    ctx.lineJoin="round";
    ctx.moveTo(x,y);
    if (isEmpty){
      //$("#save").prop("disabled", false);
      isEmpty = 0;
    }
  };
  var move = function(e) {
    if(clicked && waiter % waitlimit == 0){
      x = e.pageX-$("#canvas").offset().left;
      y = e.pageY-$("#canvas").offset().top;
      ctx.lineTo(x,y);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(x, y, 0.5*theWidth, 0, 2*Math.PI);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(x,y);
      if (isEmpty){
	//$("#save").prop("disabled", false);
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

function post(params) {
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
  $('#daform').submit();
  return;
}

function isCanvasSupported(){
  var elem = document.createElement('canvas');
  return !!(elem.getContext && elem.getContext('2d'));
}
