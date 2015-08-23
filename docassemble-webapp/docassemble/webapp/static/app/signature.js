var ctx, color = "#000";	

var theTop;
var theLeft;
var theWidth;
var aspectRatio = 0.30;
var theBorders = 50;

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
  });
  $("#new").click(function() {
    newCanvas();
  });
  $("#save").click(function() {
    saveCanvas();
  });
  window.scrollTo(0,1);
});

// function to setup a new canvas for drawing

function resizeCanvas(){
  //var cheight = $(window).height()-($("#header").height() + $("#toppart").height() + $("#bottompart").height());
  newCanvas();
  //console.log("I resized");
  return;
  var cheight = $(window).width()*aspectRatio;
  if (cheight > $(window).height()-theTop){
    cheight = $(window).height()-theTop;
  }
  if (cheight > 350){
    cheight = 350;
  }
  var cwidth = $(window).width() - theBorders;
  
  $("#content").height(cheight);
  //$("#content").css('top', ($("#header").height() + $("#toppart").height()) + "px");
  //$("#bottompart").css('top', (cheight) + "px");
  $("#canvas").width(cwidth);
  $("#canvas").height(cheight);
  theTop = $("#canvas").offset().top;
  theLeft = $("#canvas").offset().left;
  theWidth = cwidth/100.0;
  if (theWidth < 1){
    theWidth = 1;
  }
  return;
}


function saveCanvas(){
  var dataURL = document.getElementById("canvas").toDataURL();
  //console.log(dataURL)
  post({'success': 1, 'theImage': dataURL});
}

function newCanvas(){
  //define and resize canvas
  //var cheight = $(window).height()-($("#header").height() + $("#toppart").height() + $("#bottompart").height());
  var cheight = $(window).width()*aspectRatio;
  if (cheight > $(window).height()-theTop){
    cheight = $(window).height()-theTop;
  }
  if (cheight > 350){
    cheight = 350;
  }
  var cwidth = $(window).width() - theBorders;
  $("#content").height(cheight);
  //$("#bottompart").css('top', (cheight) + "px");
  //$("#content").css('top', ($("#header").height() + $("#toppart").height()) + "px");
  //$("#content").css('bottom', ($("#bottompart").height()) + "px");
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
}

// prototype to	start drawing on touch using canvas moveTo and lineTo
$.fn.drawTouch = function() {
  var start = function(e) {
    e = e.originalEvent;
    ctx.beginPath();
    ctx.lineJoin="round";
    x = e.changedTouches[0].pageX-theLeft;
    y = e.changedTouches[0].pageY-theTop;
    ctx.moveTo(x,y);
  };
  var move = function(e) {
    e.preventDefault();
    e = e.originalEvent;
    x = e.changedTouches[0].pageX-theLeft;
    y = e.changedTouches[0].pageY-theTop;
    ctx.lineTo(x,y);
    ctx.stroke();
    ctx.fillRect(x-0.5*theWidth,y-0.5*theWidth,theWidth,theWidth);
  };
  var dot = function(e) {
    e.preventDefault();
    e = e.originalEvent;
    ctx.beginPath();
    ctx.lineJoin="round";
    x = e.pageX-theLeft;
    y = e.pageY-theTop;
    ctx.fillRect(x-0.5*theWidth,y-0.5*theWidth,theWidth,theWidth);
    //console.log("Got click");
  };
  $(this).on("click", dot);
  $(this).on("touchend", move);
  $(this).on("touchcancel", move);
  $(this).on("touchstart", start);
  $(this).on("touchmove", move);	
}; 
    
// prototype to	start drawing on pointer(microsoft ie) using canvas moveTo and lineTo
$.fn.drawPointer = function() {
  var start = function(e) {
    e = e.originalEvent;
    ctx.beginPath();
    ctx.lineJoin="round";
    x = e.pageX-theLeft;
    y = e.pageY-theTop;
    ctx.moveTo(x,y);
  };
  var move = function(e) {
    e.preventDefault();
    e = e.originalEvent;
    x = e.pageX-theLeft;
    y = e.pageY-theTop;
    ctx.lineTo(x,y);
    ctx.stroke();
  };
  $(this).on("MSPointerDown", start);
  $(this).on("MSPointerMove", move);
  $(this).on("MSPointerUp", move);
};        

// prototype to	start drawing on mouse using canvas moveTo and lineTo
$.fn.drawMouse = function() {
  var clicked = 0;
  var start = function(e) {
    clicked = 1;
    ctx.beginPath();
    ctx.lineJoin="round";
    x = e.pageX-theLeft;
    y = e.pageY-theTop;
    ctx.moveTo(x,y);
  };
  var move = function(e) {
    if(clicked){
      x = e.pageX-theLeft;
      y = e.pageY-theTop;
      ctx.lineTo(x,y);
      ctx.stroke();
    }
  };
  var stop = function(e) {
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
  $('#imageSubmit').submit();
  return;
}

function isCanvasSupported(){
  var elem = document.createElement('canvas');
  return !!(elem.getContext && elem.getContext('2d'));
}

