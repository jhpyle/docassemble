function seek_answer(){
  //console.log("Calling");
  url_action_call('predict', {inputstring: $("textarea").val()}, function(data){
    $("#fromserver").html(data.suggestions);
    //console.log("Got " + data.suggestions);
  });
}
$(document).on('daPageLoad', function(){
  $("textarea").change(seek_answer);
  $("textarea").keyup(function(event){
    if ( event.which == 32 || event.which == 13 ){
      seek_answer();
    }
  });
});
