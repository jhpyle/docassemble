$(document).on('daPageLoad', function(){
  $(".mysug").click(function(){
    $("input.form-control").val($(this).html());
  });
});
